#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import lru_cache
import argparse, ast, hashlib, importlib.util, io, json, math, os, re, time, uuid, zipfile
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
USER_ASSET_DIR = ROOT / 'library' / 'user_assets'
GENERATED_VISUAL_DIR = ROOT / 'library' / 'generated_visuals'
SAVED_SET_DIR = ROOT / 'library' / 'saved_sets'
ASSESSMENT_REQUEST_DIR = ROOT / 'library' / 'assessment_requests'
ASSESSMENT_RESULT_DIR = ROOT / 'library' / 'assessment_results'
CREATION_SOURCE_DIR = ROOT / 'library' / 'creation_sources'
CREATION_REQUEST_DIR = ROOT / 'library' / 'creation_requests'
CREATION_RESULT_DIR = ROOT / 'library' / 'creation_results'
MAX_CREATION_SOURCE_BYTES = 40 * 1024 * 1024
MAX_CREATION_REQUEST_BYTES = 8 * 1024 * 1024
MAX_CREATION_RESULT_BYTES = 24 * 1024 * 1024
ALLOWED_CREATION_SOURCE_EXTENSIONS = {'.pdf','.doc','.docx','.ppt','.pptx','.txt','.md','.html','.htm','.png','.jpg','.jpeg','.webp'}
MAX_SUMMATIVE_REQUEST_BYTES = 8 * 1024 * 1024
MAX_SUMMATIVE_RESULT_BYTES = 20 * 1024 * 1024
MAX_SAVED_SET_BYTES = 20 * 1024 * 1024
MAX_CUSTOM_IMAGE_BYTES = 15 * 1024 * 1024
ALLOWED_CUSTOM_IMAGE_TYPES = {
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/gif': '.gif',
    'image/webp': '.webp',
}



def _safe_slug(value, fallback='item'):
    cleaned = re.sub(r'[^A-Za-z0-9]+', '_', str(value or '').strip()).strip('_').lower()
    return cleaned or fallback



def _html_escape(value):
    return (str(value or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;'))


def _creation_kind(value):
    kind = str(value or '').strip().lower().replace('-', '_').replace(' ', '_')
    if kind not in {'performance_task', 'project'}:
        raise ValueError('Creation type must be Performance Task or Project.')
    return kind


def _creation_kind_label(kind):
    return 'Performance Task' if _creation_kind(kind) == 'performance_task' else 'Project'


def _creation_request_id(value):
    request_id = str(value or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{8,96}', request_id):
        raise ValueError('Invalid creation request id.')
    return request_id


def _creation_request_json_path(request_id):
    return CREATION_REQUEST_DIR / f'{_creation_request_id(request_id)}.json'


def _creation_request_zip_path(request_id):
    return CREATION_REQUEST_DIR / f'{_creation_request_id(request_id)}.zip'


def _read_creation_request(request_id):
    path = _creation_request_json_path(request_id)
    if not path.is_file():
        raise FileNotFoundError('Creation request was not found.')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 'cc3_creation_request/1':
        raise ValueError('Saved creation request is invalid.')
    return data


def _clean_external_url(value):
    raw = str(value or '').strip()
    if not raw:
        return ''
    parsed = urlparse(raw)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise ValueError('Source URL must begin with http:// or https://.')
    return raw[:2000]


def _creation_source_record(value):
    if not isinstance(value, dict):
        raise ValueError('Invalid source file record.')
    stored = Path(str(value.get('stored_name') or '')).name
    if not stored or stored != str(value.get('stored_name') or ''):
        raise ValueError('Invalid source filename.')
    path = CREATION_SOURCE_DIR / stored
    if not path.is_file():
        raise FileNotFoundError(f'Source file was not found: {stored}')
    return {
        'name': str(value.get('name') or stored)[:240],
        'stored_name': stored,
        'url': f'/library/creation_sources/{stored}',
        'size': path.stat().st_size,
    }


def save_creation_source(data, filename):
    original = Path(str(filename or 'source')).name
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_CREATION_SOURCE_EXTENSIONS:
        allowed = ', '.join(sorted(ALLOWED_CREATION_SOURCE_EXTENSIONS))
        raise ValueError(f'Unsupported source file. Use one of: {allowed}')
    if not data:
        raise ValueError('The uploaded source file was empty.')
    digest = hashlib.sha256(data).hexdigest()[:16]
    stem = _safe_slug(Path(original).stem, 'source')[:70]
    stored = f'{stem}_{digest}{ext}'
    CREATION_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = CREATION_SOURCE_DIR / stored
    if not path.exists():
        path.write_bytes(data)
    return {'name': original, 'stored_name': stored, 'url': f'/library/creation_sources/{stored}', 'size': len(data)}


def _creation_contract(kind):
    label = _creation_kind_label(kind)
    if kind == 'performance_task':
        rules = [
            'Build one coherent, authentic application task rather than a worksheet of unrelated questions.',
            'Make the task multi-step and require students to make decisions, explain reasoning, or justify conclusions.',
            'Create a clear student product or performance and state exactly what students must submit or present.',
            'Every selected I Can must produce visible student evidence somewhere in the task; do not merely mention standards.',
            'Use mathematical representations that fit the selected I Cans (graphs, tables, models, equations, diagrams, written reasoning).',
            'Keep directions student-friendly, concise, and realistic for the requested time window.',
            'Include success criteria and a usable rubric tied directly to the selected I Cans.',
            'Include teacher guidance with evidence look-fors, likely approaches, and implementation notes.',
            'Avoid filler, trivia, decorative context that does not affect the mathematics, and hidden prerequisite skills outside the selected targets.',
        ]
    else:
        rules = [
            'Build a coherent longer-form student project with a meaningful final product, not a packet of unrelated exercises.',
            'Organize the work into clear milestones or checkpoints that fit the requested duration.',
            'Every selected I Can must produce visible student evidence in the process or final product.',
            'State the final product, required components, materials/technology assumptions, and student-facing success criteria.',
            'Allow collaboration when appropriate but preserve individual mathematical accountability.',
            'Use mathematical representations that fit the selected I Cans and require explanation or reasoning, not just decoration.',
            'Include a usable rubric tied directly to the selected I Cans and project requirements.',
            'Include teacher guidance with pacing, checkpoints, evidence look-fors, and implementation notes.',
            'Keep the scope realistic for a normal classroom and avoid unnecessary supplies or outside accounts.',
        ]
    return {'label': label, 'rules': rules}


def _creation_result_template(request):
    return {
        'schema': 'cc3_creation_result/1',
        'request_id': request.get('request_id'),
        'title': request.get('title') or _creation_kind_label(request.get('kind')),
        'student_sections': [
            {'heading': 'Student Task', 'html': '<p>Student-facing directions and task content...</p>', 'kind': 'text', 'workspace_inches': 0},
            {'heading': 'Student Work', 'html': '<p>Prompt or work requirement...</p>', 'kind': 'problem', 'workspace_inches': 1.5},
        ],
        'rubric_html': '<table><thead><tr><th>Criteria</th><th>Meets</th><th>Developing</th><th>Beginning</th></tr></thead><tbody><tr><td>...</td><td>...</td><td>...</td><td>...</td></tr></tbody></table>',
        'teacher_guide_html': '<h2>Teacher Guide</h2><p>Implementation notes, evidence look-fors, and likely approaches...</p>',
    }


def _creation_request_readme(request):
    contract = request.get('authoring_contract') or {}
    rules = '\n'.join(f'{i+1}. {rule}' for i, rule in enumerate(contract.get('rules') or []))
    targets = '\n'.join(f"- {item.get('id')}: {item.get('text')}" for item in request.get('selected_i_cans') or [])
    source_lines = []
    for src in request.get('source_files') or []:
        source_lines.append(f"- Attached file: sources/{src.get('stored_name')}")
    if request.get('source_url'):
        source_lines.append(f"- Source URL: {request.get('source_url')}")
    source_text = '\n'.join(source_lines) if source_lines else '- No source material supplied.'
    return f'''CC3 {_creation_kind_label(request.get('kind')).upper()} AUTHORING REQUEST

This package was created by CC3 Tools V3.
Request ID: {request.get('request_id')}
Type: {_creation_kind_label(request.get('kind'))}
Title: {request.get('title')}
Chapter: {request.get('chapter') or 'Unassigned'}
Requested duration: {request.get('duration') or 'Teacher did not specify'}
Requested student product: {request.get('product_type') or 'Choose an appropriate product'}

SELECTED I CANS
{targets}

SOURCE MATERIAL
{source_text}

AUTHORING CONTRACT
{rules}

TEACHER NOTES
{request.get('teacher_notes') or 'None supplied.'}

OUTPUT CONTRACT
Return a ZIP named CC3_Creation_Result.zip containing CC3_Creation_Result.json.
- schema must be cc3_creation_result/1
- request_id must exactly match this request
- student_sections must contain the complete student-facing task/project as editable HTML sections
- section kind must be text, problem, or heading
- workspace_inches may be 0-5 and should be used only when blank student work space is useful
- rubric_html is required and must align to the selected I Cans
- teacher_guide_html is required and should include implementation notes and evidence look-fors
- use self-contained HTML/SVG or local CC3 asset paths; do not depend on external image URLs

Do NOT return a GitHub/Curriculum Transfer. The teacher will upload the result ZIP directly back into CC3 Tools V3, which will add the editable result to the Library.
'''


def create_creation_request(payload):
    if not isinstance(payload, dict):
        raise ValueError('Invalid creation request.')
    kind = _creation_kind(payload.get('kind'))
    mode = str(payload.get('mode') or '').strip().lower()
    if mode not in {'i_cans', 'combine'}:
        raise ValueError('Request mode must be I Cans or Combine.')
    title = str(payload.get('title') or '').strip()[:160]
    if not title:
        raise ValueError('Give the item a title.')
    selected = payload.get('selected_i_cans') or []
    if not isinstance(selected, list) or not selected:
        raise ValueError('Select at least one I Can.')
    clean_targets = []
    seen = set()
    for item in selected:
        if not isinstance(item, dict):
            continue
        target_id = str(item.get('id') or '').strip()[:100]
        text = str(item.get('text') or '').strip()[:500]
        if not target_id or not text or target_id in seen:
            continue
        seen.add(target_id)
        clean_targets.append({'id': target_id, 'text': text, 'scope': str(item.get('scope') or '')[:160]})
    if not clean_targets:
        raise ValueError('Select at least one valid I Can.')
    chapter = int(payload.get('chapter') or 0)
    if chapter < 1 or chapter > 99:
        raise ValueError('Choose a chapter.')
    sources = payload.get('source_files') or []
    clean_sources = [_creation_source_record(x) for x in sources] if isinstance(sources, list) else []
    source_url = _clean_external_url(payload.get('source_url'))
    if mode == 'combine' and not clean_sources and not source_url:
        raise ValueError('Combine mode needs an uploaded source file or source URL.')
    stamp = time.strftime('%Y%m%d_%H%M%S')
    request_id = f'cc3_create_{chapter}_{stamp}_{uuid.uuid4().hex[:6]}'
    contract = _creation_contract(kind)
    request = {
        'schema': 'cc3_creation_request/1',
        'request_id': request_id,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'course': 'Core Connections Course 3',
        'content_package': 'cc3e3',
        'kind': kind,
        'mode': mode,
        'title': title,
        'chapter': chapter,
        'scope_id': str(payload.get('scope_id') or '').strip()[:120],
        'scope_title': str(payload.get('scope_title') or '').strip()[:240],
        'selected_i_cans': clean_targets,
        'duration': str(payload.get('duration') or '').strip()[:120],
        'product_type': str(payload.get('product_type') or '').strip()[:160],
        'teacher_notes': str(payload.get('teacher_notes') or '').strip()[:4000],
        'source_url': source_url,
        'source_files': clean_sources,
        'authoring_contract': contract,
    }
    CREATION_REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _creation_request_json_path(request_id)
    zip_path = _creation_request_zip_path(request_id)
    json_path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('README_FIRST.txt', _creation_request_readme(request))
        zf.writestr('CC3_Creation_Request.json', json.dumps(request, indent=2, ensure_ascii=False) + '\n')
        zf.writestr('CC3_Creation_Result_TEMPLATE.json', json.dumps(_creation_result_template(request), indent=2, ensure_ascii=False) + '\n')
        for src in clean_sources:
            zf.write(CREATION_SOURCE_DIR / src['stored_name'], arcname=f"sources/{src['stored_name']}")
    return {
        'request_id': request_id,
        'name': f"{_safe_slug(title, kind)}_{stamp}_REQUEST.zip",
        'download_url': f'/api/creation-request/{request_id}.zip',
        'saved_path': str(zip_path.relative_to(ROOT)),
    }


def _parse_creation_result_bytes(data, filename):
    name = str(filename or '').lower()
    if name.endswith('.json'):
        return json.loads(data.decode('utf-8'))
    try:
        with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
            candidates = [n for n in zf.namelist() if Path(n).name == 'CC3_Creation_Result.json']
            if not candidates:
                raise ValueError('Result ZIP must contain CC3_Creation_Result.json.')
            return json.loads(zf.read(candidates[0]).decode('utf-8'))
    except zipfile.BadZipFile:
        raise ValueError('Upload a CC3 Creation result ZIP or JSON file.')


def _normalize_creation_result(result, request):
    if not isinstance(result, dict) or result.get('schema') != 'cc3_creation_result/1':
        raise ValueError('Result schema must be cc3_creation_result/1.')
    if str(result.get('request_id') or '') != request.get('request_id'):
        raise ValueError('Result request_id does not match this request.')
    title = str(result.get('title') or request.get('title') or '').strip()[:160]
    if not title:
        raise ValueError('Result needs a title.')
    sections = result.get('student_sections')
    if not isinstance(sections, list) or not sections or len(sections) > 40:
        raise ValueError('Result must contain 1-40 student_sections.')
    clean_sections = []
    for idx, item in enumerate(sections, start=1):
        if not isinstance(item, dict):
            raise ValueError(f'Student section {idx} is invalid.')
        heading = str(item.get('heading') or f'Section {idx}').strip()[:160]
        html = str(item.get('html') or '').strip()
        if not html:
            raise ValueError(f'Student section {idx} is empty.')
        kind = str(item.get('kind') or 'text').strip().lower()
        if kind not in {'text','problem','heading'}:
            raise ValueError(f'Student section {idx} kind must be text, problem, or heading.')
        try: workspace = float(item.get('workspace_inches') or 0)
        except Exception: workspace = 0
        workspace = max(0, min(5, workspace))
        clean_sections.append({'heading': heading, 'html': html, 'kind': kind, 'workspace_inches': workspace})
    rubric = str(result.get('rubric_html') or '').strip()
    teacher_guide = str(result.get('teacher_guide_html') or '').strip()
    if not rubric:
        raise ValueError('Result must include rubric_html.')
    if not teacher_guide:
        raise ValueError('Result must include teacher_guide_html.')
    return {'title': title, 'student_sections': clean_sections, 'rubric_html': rubric, 'teacher_guide_html': teacher_guide}


def _creation_recipe(request, normalized):
    kind = request.get('kind')
    title = normalized['title']
    chapter = int(request.get('chapter') or 0) or ''
    scope_id = str(request.get('scope_id') or '').strip()
    section_scope = scope_id if re.fullmatch(r'\d+\.\d+(?:\.\d+)?', scope_id) else ''
    order, custom, options = [], {}, {}
    def add_card(card_type, label, html, workspace=0):
        idx = len(order) + 1
        cid = f"custom-{kind}-{_safe_slug(title,'item')[:28]}-{idx:02d}-{uuid.uuid4().hex[:5]}"
        editor_type = 'problem' if card_type == 'custom_problem' else ('heading' if card_type == 'custom_heading' else 'text')
        card = {
            'schema_version': 1, 'card_id': cid, 'textbook_id': 'teacher', 'chapter': chapter or 1,
            'lesson': section_scope or _creation_kind_label(kind), 'section': _creation_kind_label(kind),
            'card_type': card_type, 'editor_type': editor_type, 'html': html,
        }
        if card_type == 'custom_problem': card['problem_label'] = label
        else: card['label'] = label
        custom[cid] = card
        order.append(cid)
        options[cid] = {'workspace': workspace, 'figures': {}, 'visuals': []}
        return cid
    for item in normalized['student_sections']:
        if item['kind'] == 'heading':
            add_card('custom_heading', item['heading'], item['html'], 0)
        elif item['kind'] == 'problem':
            add_card('custom_problem', item['heading'], item['html'], item['workspace_inches'])
        else:
            add_card('custom_text', item['heading'], item['html'], item['workspace_inches'])
    rubric_heading = add_card('custom_heading', 'Success Criteria / Rubric', '<h2>Success Criteria / Rubric</h2>', 0)
    add_card('custom_text', 'Rubric', normalized['rubric_html'], 0)
    return {
        'schema': 'teacher_tools_document/1', 'core_version': 'teacher-tools-core/0.2-cc3-pilot',
        'content_package': 'cc3e3', 'document_kind': kind, 'title': title, 'order': order,
        'breaks': [rubric_heading],
        'settings': {'spacing':'normal','margin':'normal','figure':'normal','workspace':'medium','title':title,'showTitle':True},
        'card_options': options, 'custom_cards': custom, 'source_overrides': {}, 'section_headings': {},
        'library_scope': {'chapter': str(chapter) if chapter else '', 'section': section_scope},
        'creation_origin': {
            'request_id': request.get('request_id'), 'kind': kind, 'mode': request.get('mode'),
            'selected_i_cans': request.get('selected_i_cans') or [], 'source_url': request.get('source_url') or '',
            'source_files': request.get('source_files') or [],
        },
    }


def _teacher_guide_recipe(request, normalized):
    kind = request.get('kind')
    title = f"{normalized['title']} — Teacher Guide"
    cid = f"custom-{kind}-teacher-guide-{uuid.uuid4().hex[:8]}"
    chapter = int(request.get('chapter') or 0) or 1
    targets = ''.join(f"<li><strong>{_html_escape(x.get('id'))}</strong> — {_html_escape(x.get('text'))}</li>" for x in request.get('selected_i_cans') or [])
    html = f"<h2>Selected I Cans</h2><ul>{targets}</ul>{normalized['teacher_guide_html']}"
    return {
        'schema':'teacher_tools_document/1','core_version':'teacher-tools-core/0.2-cc3-pilot','content_package':'cc3e3',
        'document_kind':f'{kind}_teacher_guide','title':title,'order':[cid],'breaks':[],
        'settings':{'spacing':'normal','margin':'normal','figure':'normal','workspace':'medium','title':title,'showTitle':True},
        'card_options':{cid:{'workspace':0,'figures':{},'visuals':[]}},
        'custom_cards':{cid:{'schema_version':1,'card_id':cid,'textbook_id':'teacher','chapter':chapter,'lesson':'Teacher Guide','section':_creation_kind_label(kind),'card_type':'custom_text','editor_type':'text','label':'Teacher Guide','html':html}},
        'source_overrides':{},'section_headings':{},'library_scope':{'chapter':str(chapter),'section':''},
        'creation_origin':{'request_id':request.get('request_id'),'kind':kind,'teacher_guide':True},
    }


def save_creation_result_upload(request_id, data, filename):
    request = _read_creation_request(request_id)
    parsed = _parse_creation_result_bytes(data, filename)
    normalized = _normalize_creation_result(parsed, request)
    CREATION_RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result_path = CREATION_RESULT_DIR / f'{request_id}.json'
    result_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    student = write_saved_set({'name': normalized['title'], 'recipe': _creation_recipe(request, normalized)})
    guide_title = f"{normalized['title']} — Teacher Guide"
    guide = write_saved_set({'name': guide_title, 'recipe': _teacher_guide_recipe(request, normalized)})
    return {
        'request_id': request_id, 'student_saved_set_id': student['id'], 'teacher_guide_saved_set_id': guide['id'],
        'student_open_url': f"/builder/assemble.html?set={student['id']}",
        'teacher_guide_open_url': f"/builder/assemble.html?set={guide['id']}",
        'library_url': '/saved/index.html',
    }


def save_existing_creation(payload):
    if not isinstance(payload, dict):
        raise ValueError('Invalid existing-item request.')
    kind = _creation_kind(payload.get('kind'))
    title = str(payload.get('title') or '').strip()[:160]
    if not title:
        raise ValueError('Give the item a title.')
    chapter = int(payload.get('chapter') or 0)
    if chapter < 1 or chapter > 99:
        raise ValueError('Choose a chapter.')
    sources = payload.get('source_files') or []
    clean_sources = [_creation_source_record(x) for x in sources] if isinstance(sources, list) else []
    source_url = _clean_external_url(payload.get('source_url'))
    if not clean_sources and not source_url:
        raise ValueError('Upload a source file or add a source URL.')
    links = []
    for src in clean_sources:
        links.append(f'<li><a href="{_html_escape(src["url"])}" target="_blank" rel="noopener">{_html_escape(src["name"])}</a></li>')
    if source_url:
        links.append(f'<li><a href="{_html_escape(source_url)}" target="_blank" rel="noopener">{_html_escape(source_url)}</a></li>')
    notes = str(payload.get('teacher_notes') or '').strip()[:4000]
    cid = f"custom-existing-{kind}-{uuid.uuid4().hex[:8]}"
    html = f'<h2>Original item</h2><ul>{"".join(links)}</ul>' + (f'<h3>Teacher notes</h3><p>{_html_escape(notes)}</p>' if notes else '')
    recipe = {
        'schema':'teacher_tools_document/1','core_version':'teacher-tools-core/0.2-cc3-pilot','content_package':'cc3e3','document_kind':kind,
        'title':title,'order':[cid],'breaks':[],'settings':{'spacing':'normal','margin':'normal','figure':'normal','workspace':'medium','title':title,'showTitle':True},
        'card_options':{cid:{'workspace':0,'figures':{},'visuals':[]}},
        'custom_cards':{cid:{'schema_version':1,'card_id':cid,'textbook_id':'teacher','chapter':chapter,'lesson':_creation_kind_label(kind),'section':_creation_kind_label(kind),'card_type':'custom_text','editor_type':'text','label':'Original item','html':html}},
        'source_overrides':{},'section_headings':{},'library_scope':{'chapter':str(chapter),'section':''},
        'creation_origin':{'kind':kind,'mode':'existing','source_url':source_url,'source_files':clean_sources},
    }
    record = write_saved_set({'name':title,'recipe':recipe})
    return {'saved_set_id':record['id'],'open_url':f"/builder/assemble.html?set={record['id']}",'library_url':'/saved/index.html'}


def _summative_request_id(value):
    request_id = str(value or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{8,96}', request_id):
        raise ValueError('Invalid Summative request id.')
    return request_id


def _summative_request_json_path(request_id):
    return ASSESSMENT_REQUEST_DIR / f'{_summative_request_id(request_id)}.json'


def _summative_request_zip_path(request_id):
    return ASSESSMENT_REQUEST_DIR / f'{_summative_request_id(request_id)}.zip'


def _read_summative_request(request_id):
    path = _summative_request_json_path(request_id)
    if not path.is_file():
        raise FileNotFoundError('Summative request was not found.')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 'cc3_summative_request/1':
        raise ValueError('Saved Summative request is invalid.')
    return data


def _summative_result_template(request):
    mc_count = int(request.get('mc_count') or 0)
    frq_count = int(request.get('frq_count') or 0)
    versions = int(request.get('version_count') or 1)
    questions = []
    for i in range(mc_count):
        questions.append({
            'slot': i + 1,
            'kind': 'mc',
            'i_can_id': '<choose from mc_i_cans>',
            'family_id': '<approved family id>',
            'family_name': '<family name>',
            'question_structure_id': '<question structure id>',
            'response_mode': 'selected_response',
            'representation_mode': '<text/table/graph/model/etc>',
            'student_html': '<p>Question stem...</p><ol class="choices" type="A"><li>...</li><li>...</li><li>...</li><li>...</li></ol>',
            'answer': 'A',
            'solution': 'Short teacher solution.'
        })
    for i in range(frq_count):
        questions.append({
            'slot': mc_count + i + 1,
            'kind': 'frq',
            'i_can_id': '<choose from frq_i_cans>',
            'family_id': '<approved family id>',
            'family_name': '<family name>',
            'question_structure_id': '<question structure id>',
            'response_mode': 'constructed_response',
            'representation_mode': '<text/table/graph/model/etc>',
            'student_html': '<p>Free-response question...</p>',
            'answer': '<answer>',
            'solution': 'Short teacher solution.'
        })
    return {
        'schema': 'cc3_summative_result/1',
        'request_id': request.get('request_id'),
        'assessment_title': request.get('document_title') or request.get('assessment_type') or 'Summative',
        'versions': [
            {'label': chr(65 + v), 'questions': json.loads(json.dumps(questions))}
            for v in range(versions)
        ]
    }


def _summative_request_readme(request):
    mc = int(request.get('mc_count') or 0)
    frq = int(request.get('frq_count') or 0)
    versions = int(request.get('version_count') or 1)
    return f'''CC3 SUMMATIVE AUTHORING REQUEST

This package was created by CC3 Tools V3.
Request ID: {request.get('request_id')}
Assessment: {request.get('assessment_type')}
Chapter: {request.get('chapter')}
Requested per version: {mc} multiple-choice + {frq} free-response
Versions requested: {versions}

AUTHORING RULES
1. Treat CC3_Summative_Request.json as authoritative. Use only the MC I Cans for MC slots and only the FRQ I Cans for FRQ slots.
2. Use the supplied bank family records as the source of truth. Preserve each chosen family's evidence job, invariant structure, representation requirements, and forbidden variations.
3. Keep routine wording direct and concise. If the evidence job requires a graph, table, Diamond, tiles, or another representation, the student question must actually contain that representation.
4. MC items must have exactly four visible choices, exactly one correct answer, and plausible distractors tied to likely student errors. Avoid all/none-of-the-above.
5. FRQ items must be constructed response, not disguised multiple choice. Provide enough workspace-worthy mathematical work for the selected I Can.
6. Prefer existing approved family_id values from the request. If an exact selected-response family does not exist, you may author a temporary family that still targets the selected I Can; use a family_id beginning CC3-AI- and include family_snapshot in that question.
7. Across versions, keep the same I Can coverage and family architecture while changing parameters/context so versions are genuinely parallel. Do not merely reorder identical questions.
8. Do not use external image URLs. Existing bank asset paths and local /api/assessment-visual?... routes are allowed in student_html.

OUTPUT CONTRACT
Return a ZIP named CC3_Summative_Result.zip containing CC3_Summative_Result.json. The JSON must follow CC3_Summative_Result_TEMPLATE.json exactly.
- schema must be cc3_summative_result/1
- request_id must exactly match this request
- return exactly {versions} version(s)
- each version must contain exactly {mc} mc question(s) and {frq} frq question(s)
- every question needs i_can_id, family_id, student_html, answer, and solution
- MC response_mode must be selected_response
- FRQ response_mode must not be selected_response

Do NOT return a GitHub/Curriculum Transfer. The teacher will upload the result ZIP directly back into CC3 Tools V3.
'''


def create_summative_request(payload):
    if not isinstance(payload, dict):
        raise ValueError('Invalid Summative request.')
    mc_count = int(payload.get('mc_count') or 0)
    frq_count = int(payload.get('frq_count') or 0)
    version_count = int(payload.get('version_count') or 1)
    if mc_count < 0 or mc_count > 40 or frq_count < 0 or frq_count > 40:
        raise ValueError('MC and FRQ counts must each be between 0 and 40.')
    if mc_count + frq_count < 1 or mc_count + frq_count > 60:
        raise ValueError('Choose between 1 and 60 total Summative questions.')
    if version_count < 1 or version_count > 4:
        raise ValueError('Summative requests support 1-4 versions.')
    mc_i_cans = payload.get('mc_i_cans') or []
    frq_i_cans = payload.get('frq_i_cans') or []
    if not isinstance(mc_i_cans, list) or not isinstance(frq_i_cans, list):
        raise ValueError('MC and FRQ I Can selections must be lists.')
    if mc_count and not mc_i_cans:
        raise ValueError('Select at least one MC I Can.')
    if frq_count and not frq_i_cans:
        raise ValueError('Select at least one FRQ I Can.')
    chapter = int(payload.get('chapter') or 0)
    if chapter < 1 or chapter > 99:
        raise ValueError('A valid chapter is required.')
    stamp = time.strftime('%Y%m%d_%H%M%S')
    request_id = f'cc3_sum_{chapter}_{stamp}_{uuid.uuid4().hex[:6]}'
    assessment_type = str(payload.get('assessment_type') or 'Mixed Test').strip()[:80] or 'Mixed Test'
    scope_id = str(payload.get('scope_id') or '').strip()[:120]
    document_title = str(payload.get('document_title') or '').strip()[:160]
    request = {
        'schema': 'cc3_summative_request/1',
        'request_id': request_id,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'course': 'Core Connections Course 3',
        'content_package': 'cc3e3',
        'assessment_type': assessment_type,
        'document_title': document_title,
        'chapter': chapter,
        'bank_view': str(payload.get('bank_view') or 'mg')[:32],
        'scope_id': scope_id,
        'scope_title': str(payload.get('scope_title') or '').strip()[:240],
        'mc_count': mc_count,
        'frq_count': frq_count,
        'version_count': version_count,
        'include_answer_key': bool(payload.get('include_answer_key', True)),
        'mc_i_cans': mc_i_cans,
        'frq_i_cans': frq_i_cans,
        'mc_source_families': payload.get('mc_source_families') if isinstance(payload.get('mc_source_families'), list) else [],
        'frq_source_families': payload.get('frq_source_families') if isinstance(payload.get('frq_source_families'), list) else [],
        'authoring_contract': payload.get('authoring_contract') if isinstance(payload.get('authoring_contract'), dict) else {},
    }
    ASSESSMENT_REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _summative_request_json_path(request_id)
    zip_path = _summative_request_zip_path(request_id)
    json_path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    template = _summative_result_template(request)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('README_FIRST.txt', _summative_request_readme(request))
        zf.writestr('CC3_Summative_Request.json', json.dumps(request, indent=2, ensure_ascii=False) + '\n')
        zf.writestr('CC3_Summative_Result_TEMPLATE.json', json.dumps(template, indent=2, ensure_ascii=False) + '\n')
    return {
        'request_id': request_id,
        'name': f'{_safe_slug(document_title or assessment_type, "cc3_summative")}_{stamp}_REQUEST.zip',
        'stored_name': zip_path.name,
        'download_url': f'/api/summative-request/{request_id}.zip',
        'relative_path': str(zip_path.relative_to(ROOT)),
        'request': request,
    }


def _safe_result_html(value):
    text = str(value or '').strip()
    if not text:
        raise ValueError('Question student_html cannot be blank.')
    if len(text) > 50000:
        raise ValueError('Question student_html is too large.')
    lowered = text.lower()
    blocked = ('<script', 'javascript:', ' onload=', ' onclick=', ' onerror=', 'http://', 'https://')
    if any(token in lowered for token in blocked):
        raise ValueError('Question HTML contains an unsupported script, event handler, or external URL.')
    return text


def _parse_summative_result_bytes(data, filename):
    if not data:
        raise ValueError('Returned Summative result was empty.')
    name = str(filename or '').lower()
    if name.endswith('.zip') or data[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
            infos = [info for info in zf.infolist() if not info.is_dir()]
            if sum(info.file_size for info in infos) > MAX_SUMMATIVE_RESULT_BYTES:
                raise ValueError('Returned result ZIP expands beyond the allowed size.')
            exact = [info for info in infos if Path(info.filename).name == 'CC3_Summative_Result.json']
            jsons = [info for info in infos if info.filename.lower().endswith('.json')]
            target = exact[0] if exact else (jsons[0] if len(jsons) == 1 else None)
            if target is None:
                raise ValueError('Result ZIP must contain CC3_Summative_Result.json.')
            raw = zf.read(target)
    else:
        raw = data
    try:
        result = json.loads(raw.decode('utf-8'))
    except Exception as exc:
        raise ValueError(f'Could not read Summative result JSON: {exc}')
    if not isinstance(result, dict):
        raise ValueError('Summative result JSON must be an object.')
    return result


def validate_summative_result(result, request):
    if result.get('schema') != 'cc3_summative_result/1':
        raise ValueError('Unsupported Summative result schema.')
    if str(result.get('request_id') or '') != str(request.get('request_id') or ''):
        raise ValueError('Returned result request_id does not match this request.')
    versions = result.get('versions')
    expected_versions = int(request.get('version_count') or 1)
    if not isinstance(versions, list) or len(versions) != expected_versions:
        raise ValueError(f'Returned result must contain exactly {expected_versions} version(s).')
    mc_allowed = {str(x.get('id') or '') for x in request.get('mc_i_cans') or [] if isinstance(x, dict)}
    frq_allowed = {str(x.get('id') or '') for x in request.get('frq_i_cans') or [] if isinstance(x, dict)}
    expected_mc = int(request.get('mc_count') or 0)
    expected_frq = int(request.get('frq_count') or 0)
    normalized_versions = []
    for vi, version in enumerate(versions):
        if not isinstance(version, dict):
            raise ValueError(f'Version {vi + 1} is invalid.')
        questions = version.get('questions')
        if not isinstance(questions, list):
            raise ValueError(f'Version {vi + 1} is missing questions.')
        mc = [q for q in questions if isinstance(q, dict) and str(q.get('kind') or '').lower() == 'mc']
        frq = [q for q in questions if isinstance(q, dict) and str(q.get('kind') or '').lower() == 'frq']
        if len(mc) != expected_mc or len(frq) != expected_frq or len(questions) != expected_mc + expected_frq:
            raise ValueError(f'Version {vi + 1} must contain exactly {expected_mc} MC and {expected_frq} FRQ questions.')
        normalized_questions = []
        for qi, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError(f'Version {vi + 1}, question {qi + 1} is invalid.')
            kind = str(question.get('kind') or '').lower()
            if kind not in ('mc', 'frq'):
                raise ValueError(f'Version {vi + 1}, question {qi + 1} must be mc or frq.')
            i_can_id = str(question.get('i_can_id') or '').strip()
            allowed = mc_allowed if kind == 'mc' else frq_allowed
            if i_can_id not in allowed:
                raise ValueError(f'Version {vi + 1}, question {qi + 1} uses I Can {i_can_id or "(blank)"}, which was not selected for {kind.upper()}.')
            family_id = str(question.get('family_id') or '').strip()
            if not family_id:
                raise ValueError(f'Version {vi + 1}, question {qi + 1} is missing family_id.')
            response_mode = str(question.get('response_mode') or ('selected_response' if kind == 'mc' else 'constructed_response')).strip()
            if kind == 'mc' and response_mode != 'selected_response':
                raise ValueError(f'Version {vi + 1}, question {qi + 1} is MC but response_mode is not selected_response.')
            if kind == 'frq' and response_mode == 'selected_response':
                raise ValueError(f'Version {vi + 1}, question {qi + 1} is FRQ but response_mode is selected_response.')
            student_html = _safe_result_html(question.get('student_html'))
            answer = str(question.get('answer') or '').strip()
            if not answer:
                raise ValueError(f'Version {vi + 1}, question {qi + 1} is missing an answer.')
            if kind == 'mc':
                choice_count = len(re.findall(r'<li\b', student_html, flags=re.IGNORECASE))
                if choice_count != 4:
                    raise ValueError(f'Version {vi + 1}, question {qi + 1} must contain exactly four MC choices.')
                if answer.upper() not in {'A', 'B', 'C', 'D'}:
                    raise ValueError(f'Version {vi + 1}, question {qi + 1} MC answer must be A, B, C, or D.')
            normalized_questions.append({
                'slot': int(question.get('slot') or qi + 1),
                'kind': kind,
                'i_can_id': i_can_id,
                'family_id': family_id,
                'family_name': str(question.get('family_name') or family_id).strip()[:200],
                'teacher_question_id': str(question.get('teacher_question_id') or '').strip()[:80],
                'question_structure_id': str(question.get('question_structure_id') or '').strip()[:120],
                'response_mode': response_mode,
                'representation_mode': str(question.get('representation_mode') or 'text').strip()[:120],
                'student_html': student_html,
                'answer': answer[:10000],
                'solution': str(question.get('solution') or '').strip()[:20000],
                'family_snapshot': question.get('family_snapshot') if isinstance(question.get('family_snapshot'), dict) else None,
            })
        normalized_versions.append({'label': chr(65 + vi), 'questions': normalized_questions})
    return {
        'schema': 'cc3_summative_result/1',
        'request_id': request.get('request_id'),
        'assessment_title': str(result.get('assessment_title') or request.get('document_title') or request.get('assessment_type') or 'Summative').strip()[:160],
        'versions': normalized_versions,
    }


def save_summative_result_upload(request_id, data, filename):
    request = _read_summative_request(request_id)
    parsed = _parse_summative_result_bytes(data, filename)
    normalized = validate_summative_result(parsed, request)
    ASSESSMENT_RESULT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(str(filename or 'CC3_Summative_Result.json')).name
    safe_name = re.sub(r'[^A-Za-z0-9_.-]+', '_', safe_name).strip('._') or 'CC3_Summative_Result.json'
    raw_path = ASSESSMENT_RESULT_DIR / f'{request_id}_{safe_name}'
    raw_path.write_bytes(data)
    normalized_path = ASSESSMENT_RESULT_DIR / f'{request_id}_normalized.json'
    normalized_path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return {
        'result': normalized,
        'relative_path': str(raw_path.relative_to(ROOT)),
        'normalized_relative_path': str(normalized_path.relative_to(ROOT)),
        'summary': {
            'version_count': len(normalized['versions']),
            'mc_count': int(request.get('mc_count') or 0),
            'frq_count': int(request.get('frq_count') or 0),
        }
    }



TEXTBOOK_CARD_INDEX = ROOT / 'library' / 'textbooks' / 'cc3e3' / 'cards' / 'index.json'

@lru_cache(maxsize=1)
def card_scope_index():
    mapping = {}
    fallback_chapter = None
    try:
        data = json.loads(TEXTBOOK_CARD_INDEX.read_text(encoding='utf-8'))
        fallback_chapter = data.get('chapter')
        for card in data.get('cards') or []:
            card_id = str(card.get('card_id') or '')
            lesson = str(card.get('lesson') or '')
            match = re.fullmatch(r'(\d+)\.(\d+)(?:\.(\d+))?', lesson)
            if not card_id or not match:
                continue
            chapter = match.group(1) or str(fallback_chapter or '')
            section = f'{match.group(1)}.{match.group(2)}'
            mapping[card_id] = {
                'chapter': chapter,
                'section': section,
                'lesson': lesson,
            }
    except Exception:
        pass
    return mapping


def content_scope_catalog():
    catalog = {}
    for meta in card_scope_index().values():
        chapter = str(meta.get('chapter') or '')
        section = str(meta.get('section') or '')
        if not chapter:
            continue
        catalog.setdefault(chapter, set())
        if section:
            catalog[chapter].add(section)
    def natural(value):
        return [int(part) if part.isdigit() else part for part in str(value).split('.')]
    return [
        {'chapter': chapter, 'sections': sorted(sections, key=natural)}
        for chapter, sections in sorted(catalog.items(), key=lambda item: natural(item[0]))
    ]


def recipe_scope(recipe):
    explicit = recipe.get('library_scope') if isinstance(recipe, dict) else None
    if isinstance(explicit, dict):
        chapter = str(explicit.get('chapter') or '').strip() or None
        section = str(explicit.get('section') or '').strip() or None
        if chapter and section:
            return {'chapter': chapter, 'section': section, 'chapters': [chapter], 'sections': [section], 'lessons': [], 'scope_label': f'Chapter {chapter} · Section {section}'}
        if chapter:
            return {'chapter': chapter, 'section': None, 'chapters': [chapter], 'sections': [], 'lessons': [], 'scope_label': f'Chapter {chapter} · Whole chapter'}
        if recipe.get('document_kind') == 'printable':
            return {'chapter': None, 'section': None, 'chapters': [], 'sections': [], 'lessons': [], 'scope_label': 'Reusable printable'}

    taxonomy = card_scope_index()
    chapters = set()
    sections = set()
    lessons = set()
    for card_id in recipe.get('order') or []:
        meta = taxonomy.get(str(card_id))
        if not meta:
            continue
        chapters.add(meta['chapter'])
        sections.add(meta['section'])
        lessons.add(meta['lesson'])
    chapters = sorted(chapters, key=lambda x: [int(p) if p.isdigit() else p for p in str(x).split('.')])
    sections = sorted(sections, key=lambda x: [int(p) if p.isdigit() else p for p in str(x).split('.')])
    lessons = sorted(lessons, key=lambda x: [int(p) if p.isdigit() else p for p in str(x).split('.')])
    chapter = chapters[0] if len(chapters) == 1 else None
    section = sections[0] if len(sections) == 1 else None
    if chapter and section:
        label = f'Chapter {chapter} · Section {section}'
    elif chapter and sections:
        label = f'Chapter {chapter} · Multiple sections'
    elif len(chapters) > 1:
        label = 'Multiple chapters'
    else:
        label = 'General / unassigned'
    return {
        'chapter': chapter,
        'section': section,
        'chapters': chapters,
        'sections': sections,
        'lessons': lessons,
        'scope_label': label,
    }


def saved_set_path(saved_id):
    value = str(saved_id or '').strip().lower()
    if not re.fullmatch(r'[a-f0-9]{12}', value):
        raise ValueError('Invalid saved set id.')
    return SAVED_SET_DIR / f'{value}.json'


def read_saved_set(saved_id):
    path = saved_set_path(saved_id)
    if not path.is_file():
        raise FileNotFoundError('Saved set not found.')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('recipe'), dict):
        raise ValueError('Saved set file is invalid.')
    return data


def normalized_assessment_bundle(value):
    if value is None:
        return None
    if not isinstance(value, dict) or value.get('schema') != 'teacher_tools_assessment_versions/1':
        raise ValueError('Unsupported assessment bundle.')
    recipes = value.get('recipes')
    if not isinstance(recipes, list) or not recipes:
        raise ValueError('Assessment bundle must contain at least one version.')
    if len(recipes) > 12:
        raise ValueError('Assessment bundle has too many versions.')
    for recipe in recipes:
        if not isinstance(recipe, dict) or recipe.get('schema') != 'teacher_tools_document/1':
            raise ValueError('Assessment bundle contains an unsupported document recipe.')
    bundle = json.loads(json.dumps(value))
    bundle['version_count'] = max(1, min(int(bundle.get('version_count') or len(recipes)), len(recipes)))
    bundle['active_index'] = max(0, min(int(bundle.get('active_index') or 0), bundle['version_count'] - 1))
    return bundle


def assessment_saved_scope(bundle, recipe):
    origin = bundle.get('origin') if isinstance(bundle, dict) else {}
    if not isinstance(origin, dict):
        origin = {}
    chapter = str(origin.get('chapter') or '').strip() or None
    bank_view = str(origin.get('bank_view') or '').strip()
    scope_id = str(origin.get('scope_id') or '').strip()
    section = scope_id if bank_view == 'section' and re.fullmatch(r'\d+\.\d+(?:\.\d+)?', scope_id) else None
    if chapter and section:
        label = f'Chapter {chapter} · Section {section}'
        return {'chapter': chapter, 'section': section, 'chapters': [chapter], 'sections': [section], 'lessons': [], 'scope_label': label}
    if chapter:
        detail = scope_id if scope_id else str(origin.get('scope_title') or '').strip()
        label = f'Chapter {chapter}' + (f' · {detail}' if detail else '')
        return {'chapter': chapter, 'section': None, 'chapters': [chapter], 'sections': [], 'lessons': [], 'scope_label': label}
    return recipe_scope(recipe)


def write_saved_set(payload):
    name = str(payload.get('name') or '').strip()
    recipe = payload.get('recipe')
    assessment_bundle = normalized_assessment_bundle(payload.get('assessment_bundle'))
    if not name or len(name) > 120:
        raise ValueError('Saved set name must be 1-120 characters.')
    if not isinstance(recipe, dict) or recipe.get('schema') != 'teacher_tools_document/1':
        raise ValueError('Unsupported document recipe.')
    if assessment_bundle:
        active = assessment_bundle['active_index']
        recipe = assessment_bundle['recipes'][active]
    SAVED_SET_DIR.mkdir(parents=True, exist_ok=True)
    saved_id = str(payload.get('id') or '').strip().lower()
    existing = None
    if saved_id:
        existing = read_saved_set(saved_id)
    else:
        saved_id = uuid.uuid4().hex[:12]
    now = time.time()
    record = {
        'schema': 'teacher_tools_saved_set/1',
        'id': saved_id,
        'name': name,
        'created_at': (existing or {}).get('created_at', now),
        'updated_at': now,
        'recipe': recipe,
    }
    if assessment_bundle:
        record['assessment_bundle'] = assessment_bundle
    path = saved_set_path(saved_id)
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(tmp, path)
    return record


def list_saved_sets():
    SAVED_SET_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for path in SAVED_SET_DIR.glob('*.json'):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            recipe = data.get('recipe') if isinstance(data, dict) else None
            if not isinstance(recipe, dict):
                continue
            assessment_bundle = data.get('assessment_bundle') if isinstance(data.get('assessment_bundle'), dict) else None
            is_assessment = bool(assessment_bundle and assessment_bundle.get('schema') == 'teacher_tools_assessment_versions/1')
            scope = assessment_saved_scope(assessment_bundle, recipe) if is_assessment else recipe_scope(recipe)
            origin = assessment_bundle.get('origin') if is_assessment and isinstance(assessment_bundle.get('origin'), dict) else {}
            items.append({
                'id': data.get('id') or path.stem,
                'name': data.get('name') or 'Untitled',
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'card_count': len(recipe.get('order') or []),
                'document_kind': 'assessment' if is_assessment else str(recipe.get('document_kind') or 'assembly'),
                'assessment_type': str(origin.get('assessment_type') or '') if is_assessment else None,
                'version_count': int(assessment_bundle.get('version_count') or len(assessment_bundle.get('recipes') or [])) if is_assessment else None,
                'printable_type': ((recipe.get('printable') or {}).get('type') if isinstance(recipe.get('printable'), dict) else None),
                'document_title': (recipe.get('settings') or {}).get('title') or recipe.get('title') or '',
                **scope,
            })
        except Exception:
            continue
    items.sort(key=lambda x: x.get('updated_at') or 0, reverse=True)
    return items

def image_bytes_match(data, content_type):
    if content_type == 'image/png':
        return data.startswith(b'\x89PNG\r\n\x1a\n')
    if content_type == 'image/jpeg':
        return data.startswith(b'\xff\xd8\xff')
    if content_type == 'image/gif':
        return data.startswith((b'GIF87a', b'GIF89a'))
    if content_type == 'image/webp':
        return len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP'
    return False



def find_github_root():
    override = os.environ.get('CC3_GITHUB_ROOT')
    candidates = [Path(override).expanduser().resolve()] if override else []
    candidates += [ROOT, *ROOT.parents]
    for candidate in candidates:
        if (candidate / 'memories' / 'Tools' / 'MANIFEST.json').is_file():
            return candidate
    raise RuntimeError('Could not locate GitHub root containing memories/Tools/MANIFEST.json')


def resolve_graph_tool_path():
    github_root = find_github_root()
    memories = github_root / 'memories'
    registry = json.loads((memories / 'Tools' / 'MANIFEST.json').read_text(encoding='utf-8'))
    rel = registry.get('tools', {}).get('graph_tool')
    if not rel:
        raise RuntimeError('Tools/MANIFEST.json does not define tools.graph_tool')
    path = memories / rel
    if not path.is_file():
        raise RuntimeError(f'Registered graph tool not found: {path}')
    return path


@lru_cache(maxsize=1)
def load_graph_tool():
    graph_path = resolve_graph_tool_path()
    spec = importlib.util.spec_from_file_location('cc3_canonical_graph_tool', graph_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    module.OUTPUT_DIR = str(GENERATED_VISUAL_DIR)
    return module


def svg_response_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0.04, facecolor='white')
    return buf.getvalue()


def save_svg(fig, filename):
    GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_VISUAL_DIR / filename
    path.write_bytes(svg_response_bytes(fig))
    return path


def safe_number(value, default, low=-1000, high=1000):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return default
    return min(high, max(low, n))


def safe_int(value, default, low=0, high=100):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return min(high, max(low, n))


def visual_cache_name(kind, params, ext):
    raw = json.dumps({'renderer_rev': 2, 'kind': kind, 'params': params}, sort_keys=True, separators=(',', ':')).encode('utf-8')
    digest = hashlib.sha256(raw).hexdigest()[:16]
    clean = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in kind)[:30]
    return f'{clean}_{digest}.{ext}'


def _svg_escape(value):
    return (str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;').replace("'", '&#39;'))


def _write_svg(kind, clean_params, svg_text):
    filename = visual_cache_name(kind, clean_params, 'svg')
    path = GENERATED_VISUAL_DIR / filename
    if not path.exists():
        GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(svg_text, encoding='utf-8')
    return path


def _nice_step(span, target=10):
    span = abs(float(span))
    if span <= 0:
        return 1.0
    raw = span / max(1, target)
    power = 10 ** int(math.floor(math.log10(raw)))
    fraction = raw / power
    if fraction <= 1:
        nice = 1
    elif fraction <= 2:
        nice = 2
    elif fraction <= 5:
        nice = 5
    else:
        nice = 10
    return nice * power


def _tick_values(lo, hi, step):
    if step <= 0:
        return []
    first = math.ceil(lo / step) * step
    values = []
    value = first
    guard = 0
    while value <= hi + step * 1e-8 and guard < 250:
        if abs(value) < step * 1e-8:
            value = 0.0
        values.append(value)
        value += step
        guard += 1
    return values


def _fmt_tick(value):
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return ('%.3f' % value).rstrip('0').rstrip('.')




def _normalize_graph_expression(text):
    text = str(text or '').strip().replace('−','-').replace('×','*').replace('÷','/')
    text = text.replace('^','**').replace('π','pi')
    # Simple absolute-value notation such as |x| or |x-2|.
    if text.count('|') == 2:
        a,b = text.split('|',2)[1:]
        if b == '':
            text = text.split('|',1)[0] + 'abs(' + a + ')'
    if '=' in text:
        lhs,rhs=text.split('=',1)
        lhs=lhs.strip().lower()
        if lhs == 'y' or lhs.startswith('f(') or lhs.startswith('g(') or lhs.startswith('h('):
            text=rhs.strip()
    # Common calculator-style implicit multiplication.
    text=re.sub(r'(?<=\d)(?=x\b)', '*', text)
    text=re.sub(r'(?<=\d)(?=\()', '*', text)
    text=re.sub(r'(?<=x)(?=\()', '*', text)
    text=re.sub(r'(?<=\))(?=x\b|\d|\()', '*', text)
    return text

_ALLOWED_GRAPH_FUNCS = {
    'abs': abs, 'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
    'tan': math.tan, 'exp': math.exp, 'log': math.log10, 'ln': math.log,
    'floor': math.floor, 'ceil': math.ceil,
}
_ALLOWED_GRAPH_NAMES = {'x', 'pi', 'e'} | set(_ALLOWED_GRAPH_FUNCS)
_ALLOWED_GRAPH_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name, ast.Load,
    ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd,
)


def _compile_graph_expression(text):
    normalized=_normalize_graph_expression(text)
    if not normalized:
        raise ValueError('Enter an expression to graph.')
    tree=ast.parse(normalized, mode='eval')
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_GRAPH_NODES):
            raise ValueError('Use ordinary calculator-style expressions in x.')
        if isinstance(node, ast.Name) and node.id not in _ALLOWED_GRAPH_NAMES:
            raise ValueError(f'Unsupported symbol: {node.id}')
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_GRAPH_FUNCS:
                raise ValueError('Unsupported graph function.')
            if node.keywords:
                raise ValueError('Keyword arguments are not supported in graph expressions.')
    code=compile(tree,'<teacher-tools-graph>','eval')
    def fn(x):
        env={'x':x,'pi':math.pi,'e':math.e,**_ALLOWED_GRAPH_FUNCS}
        try:
            y=eval(code, {'__builtins__':{}}, env)
            y=float(y)
            return y if math.isfinite(y) else None
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
    return normalized, fn


def _graph_expression_series(expressions, xmin, xmax):
    if isinstance(expressions, str):
        expressions=[line.strip() for line in expressions.splitlines() if line.strip()]
    elif not isinstance(expressions, list):
        expressions=[]
    expressions=[str(x).strip() for x in expressions if str(x).strip()][:6]
    if not expressions:
        expressions=['y = x']
    palette=['#1f5a85','#9a4b3b','#3b6f4f','#70528e','#8a651e','#4a6475']
    series=[]
    clean=[]
    for idx, raw in enumerate(expressions):
        text=raw.replace('−','-').strip()
        # A simple vertical line x = constant is useful in a Desmos-like teacher grapher.
        if '=' in text and text.split('=',1)[0].strip().lower() == 'x':
            rhs=text.split('=',1)[1].strip()
            normalized, const_fn=_compile_graph_expression(rhs)
            value=const_fn(0.0)
            if value is None:
                raise ValueError(f'Could not graph: {raw}')
            series.append({'vertical_x':value,'color':palette[idx % len(palette)]})
            clean.append(f'x = {rhs}')
            continue
        normalized, fn=_compile_graph_expression(text)
        points=[]
        samples=1201
        for i in range(samples):
            x=xmin+(xmax-xmin)*i/(samples-1)
            points.append((x,fn(x)))
        series.append({'points':points,'color':palette[idx % len(palette)]})
        clean.append(raw)
    return clean, series


def _svg_coordinate_plane(xmin, xmax, ymin, ymax, plotted=None, xlabel="", ylabel="", options=None):
    """Portable Teacher Tools Cartesian renderer used only when the registered
    graph tool cannot run on the local Python stack.

    Uses the Teacher Tools classroom defaults chosen for this pilot: bounded grid,
    strong axes through zero, labels beside axes, labels every 5 on the standard
    window, and arrows on both axis ends. Teacher-selected advanced settings are
    preserved in the saved visual recipe and applied deterministically here.
    """
    options = dict(options or {})
    width = height = 560
    left = right = 54
    top = bottom = 42
    plot_w = width - left - right
    plot_h = height - top - bottom
    xspan = xmax - xmin
    yspan = ymax - ymin

    def positive_step(value, default):
        try:
            value = abs(float(value))
        except (TypeError, ValueError):
            return default
        return value if value > 1e-9 else default

    x_minor = positive_step(options.get('x_minor'), 1.0 if xspan <= 24 else _nice_step(xspan, 18))
    y_minor = positive_step(options.get('y_minor'), 1.0 if yspan <= 24 else _nice_step(yspan, 18))
    major_every = max(1, safe_int(options.get('major_every'), 5, 1, 50))
    x_label_step = positive_step(options.get('x_label_step'), max(x_minor, 5.0 if xspan <= 24 else x_minor * 5))
    y_label_step = positive_step(options.get('y_label_step'), max(y_minor, 5.0 if yspan <= 24 else y_minor * 5))
    show_minor = bool(options.get('show_minor', True))
    show_major = bool(options.get('show_major', True))
    show_numbers = bool(options.get('show_numbers', True))
    axis_arrows = str(options.get('axis_arrows') or 'both')
    if axis_arrows not in ('none', 'positive', 'both'):
        axis_arrows = 'both'

    def sx(x): return left + (x - xmin) / xspan * plot_w
    def sy(y): return top + (ymax - y) / yspan * plot_h

    minor_grid = []
    major_grid = []
    x_values = _tick_values(xmin, xmax, x_minor)
    y_values = _tick_values(ymin, ymax, y_minor)

    def is_major(value, minor):
        interval = minor * major_every
        if interval <= 0:
            return False
        q = value / interval
        return abs(q - round(q)) < 1e-7

    if show_minor or show_major:
        for x in x_values:
            px = sx(x)
            if show_major and is_major(x, x_minor):
                major_grid.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{height-bottom}" class="majorgrid"/>')
            elif show_minor:
                minor_grid.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{height-bottom}" class="minorgrid"/>')
        for y in y_values:
            py = sy(y)
            if show_major and is_major(y, y_minor):
                major_grid.append(f'<line x1="{left}" y1="{py:.2f}" x2="{width-right}" y2="{py:.2f}" class="majorgrid"/>')
            elif show_minor:
                minor_grid.append(f'<line x1="{left}" y1="{py:.2f}" x2="{width-right}" y2="{py:.2f}" class="minorgrid"/>')

    x_axis_y = sy(0) if ymin <= 0 <= ymax else height-bottom
    y_axis_x = sx(0) if xmin <= 0 <= xmax else left
    labels = []
    if show_numbers:
        for x in _tick_values(xmin, xmax, x_label_step):
            if abs(x) < 1e-9:
                continue
            px = sx(x)
            label_y = min(height-bottom+22, max(top+15, x_axis_y+20))
            labels.append(f'<text x="{px:.2f}" y="{label_y:.2f}" text-anchor="middle" class="tick">{_fmt_tick(x)}</text>')
        for y in _tick_values(ymin, ymax, y_label_step):
            if abs(y) < 1e-9:
                continue
            py = sy(y)
            tx = y_axis_x - 9 if y_axis_x > left + 28 else y_axis_x + 9
            anchor = 'end' if y_axis_x > left + 28 else 'start'
            labels.append(f'<text x="{tx:.2f}" y="{py+4:.2f}" text-anchor="{anchor}" class="tick">{_fmt_tick(y)}</text>')

    axes = []
    def markers(axis, positive_at_end=True):
        if axis_arrows == 'none':
            return ''
        if axis_arrows == 'both':
            return ' marker-start="url(#axisArrow)" marker-end="url(#axisArrow)"'
        return ' marker-end="url(#axisArrow)"' if positive_at_end else ' marker-start="url(#axisArrow)"'

    if ymin <= 0 <= ymax:
        py = sy(0)
        axes.append(f'<line x1="{left}" y1="{py:.2f}" x2="{width-right}" y2="{py:.2f}" class="axis"{markers("x")}/>')
    if xmin <= 0 <= xmax:
        px = sx(0)
        # SVG y decreases upward; the positive y end is the first endpoint.
        if axis_arrows == 'both':
            marker=' marker-start="url(#axisArrow)" marker-end="url(#axisArrow)"'
        elif axis_arrows == 'positive':
            marker=' marker-start="url(#axisArrow)"'
        else:
            marker=''
        axes.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{height-bottom}" class="axis"{marker}/>')

    plotted_markup = ''
    if plotted:
        if isinstance(plotted, list) and plotted and isinstance(plotted[0], dict):
            plotted_series=plotted
        else:
            plotted_series=[{'points': plotted, 'color':'#222222'}]
        parts=[]

        def arrow_head(tip, inner, color, length=11.0, half_width=5.0):
            tx, ty = tip; ix, iy = inner
            dx, dy = tx-ix, ty-iy
            mag = math.hypot(dx, dy)
            if mag < 1e-7:
                return ''
            ux, uy = dx/mag, dy/mag
            bx, by = tx-ux*length, ty-uy*length
            px, py = -uy*half_width, ux*half_width
            return (f'<polygon points="{tx:.2f},{ty:.2f} {bx+px:.2f},{by+py:.2f} '
                    f'{bx-px:.2f},{by-py:.2f}" fill="{color}" class="relation-arrow"/>')

        def y_crossing(p1, p2, boundary):
            x1, y1 = p1; x2, y2 = p2
            if y2 == y1:
                return (x1, boundary)
            t = (boundary-y1)/(y2-y1)
            t = max(0.0, min(1.0, t))
            return (x1+t*(x2-x1), boundary)

        for idx, series in enumerate(plotted_series):
            color=_svg_escape(str(series.get('color') or '#222222'))
            if 'vertical_x' in series:
                try:
                    vx=float(series['vertical_x'])
                except (TypeError,ValueError):
                    continue
                if xmin <= vx <= xmax:
                    px=sx(vx)
                    parts.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{height-bottom}" class="relation" style="stroke:{color}"/>')
                    parts.append(arrow_head((px,top),(px,top+18),color))
                    parts.append(arrow_head((px,height-bottom),(px,height-bottom-18),color))
                continue

            raw = series.get('points') or []
            segments=[]
            current=[]
            current_start_arrow=False
            prev=None
            prev_inside=False

            for point in raw:
                x, y = point
                valid = (y is not None and isinstance(y,(int,float)) and math.isfinite(y))
                if not valid:
                    if len(current)>1:
                        segments.append((current,current_start_arrow,False))
                    current=[]; current_start_arrow=False; prev=None; prev_inside=False
                    continue

                inside = ymin <= y <= ymax
                if prev is None:
                    if inside:
                        current=[(sx(x),sy(y))]
                        current_start_arrow=abs(x-xmin) < 1e-9
                    prev=(x,y); prev_inside=inside
                    continue

                px0, py0 = prev
                # Do not bridge discontinuities that leap across the full visible range.
                giant_jump = abs(y-py0) > yspan*2.5

                if prev_inside and inside:
                    current.append((sx(x),sy(y)))
                elif prev_inside and not inside:
                    boundary = ymax if y > ymax else ymin
                    cross = y_crossing(prev,(x,y),boundary)
                    current.append((sx(cross[0]),sy(cross[1])))
                    if len(current)>1:
                        segments.append((current,current_start_arrow,True))
                    current=[]; current_start_arrow=False
                elif not prev_inside and inside:
                    boundary = ymax if py0 > ymax else ymin
                    cross = y_crossing(prev,(x,y),boundary)
                    current=[(sx(cross[0]),sy(cross[1])),(sx(x),sy(y))]
                    current_start_arrow=True
                elif not giant_jump and ((py0 < ymin and y > ymax) or (py0 > ymax and y < ymin)):
                    # A continuous steep segment can pass through the entire window.
                    first_boundary = ymin if py0 < ymin else ymax
                    second_boundary = ymax if py0 < ymin else ymin
                    c1=y_crossing(prev,(x,y),first_boundary)
                    c2=y_crossing(prev,(x,y),second_boundary)
                    segments.append(([(sx(c1[0]),sy(c1[1])),(sx(c2[0]),sy(c2[1]))],True,True))

                prev=(x,y); prev_inside=inside

            if len(current)>1:
                end_arrow = abs(raw[-1][0]-xmax) < 1e-9 and prev_inside
                segments.append((current,current_start_arrow,end_arrow))

            for seg,start_arrow,end_arrow in segments:
                pts=' '.join(f'{px:.2f},{py:.2f}' for px,py in seg)
                parts.append(f'<polyline points="{pts}" class="relation" style="stroke:{color}" clip-path="url(#plotClip)"/>')
                if start_arrow and len(seg)>1:
                    parts.append(arrow_head(seg[0],seg[min(4,len(seg)-1)],color))
                if end_arrow and len(seg)>1:
                    parts.append(arrow_head(seg[-1],seg[max(0,len(seg)-5)],color))
        plotted_markup=''.join(parts)

    axis_labels = []
    if xlabel:
        axis_labels.append(f'<text x="{width-right+18}" y="{max(top+18,min(height-bottom-7,x_axis_y-8)):.2f}" class="axislabel">{_svg_escape(xlabel)}</text>')
    if ylabel:
        axis_labels.append(f'<text x="{min(width-right-22,max(left+8,y_axis_x+10)):.2f}" y="{top-18}" class="axislabel">{_svg_escape(ylabel)}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Coordinate plane" overflow="visible">
<defs><clipPath id="plotClip"><rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}"/></clipPath><marker id="axisArrow" markerWidth="6" markerHeight="6" refX="4.8" refY="3" orient="auto-start-reverse" markerUnits="strokeWidth"><path d="M0,0 L6,3 L0,6 z" fill="#222222"/></marker></defs>
<style>.minorgrid{{stroke:#aaaaaa;stroke-width:.8}}.majorgrid{{stroke:#888888;stroke-width:1.05}}.axis{{stroke:#222222;stroke-width:2.4;stroke-linecap:round}}.relation{{fill:none;stroke:#222222;stroke-width:2.67;stroke-linecap:round;stroke-linejoin:round}}.tick{{font:14px Arial,sans-serif;fill:#252b33}}.axislabel{{font:700 15px Arial,sans-serif;fill:#222222}}</style>
<rect width="100%" height="100%" fill="white"/>
<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#aaaaaa" stroke-width=".8"/>
{"".join(minor_grid)}{"".join(major_grid)}{"".join(axes)}{plotted_markup}{"".join(labels)}{"".join(axis_labels)}</svg>"""

def _fallback_visual(kind, params):
    if kind == 'blank_graph':
        xmin = safe_number(params.get('xmin'), -10); xmax = safe_number(params.get('xmax'), 10)
        ymin = safe_number(params.get('ymin'), -10); ymax = safe_number(params.get('ymax'), 10)
        if xmax <= xmin: xmin, xmax = -10, 10
        if ymax <= ymin: ymin, ymax = -10, 10
        xlabel = str(params.get('xlabel') or '')[:20]
        ylabel = str(params.get('ylabel') or '')[:20]
        options = {
            'x_minor': safe_number(params.get('x_minor'), 1, 0.05, 1000),
            'y_minor': safe_number(params.get('y_minor'), 1, 0.05, 1000),
            'major_every': safe_int(params.get('major_every'), 5, 1, 50),
            'x_label_step': safe_number(params.get('x_label_step'), 5, 0.05, 1000),
            'y_label_step': safe_number(params.get('y_label_step'), 5, 0.05, 1000),
            'show_minor': bool(params.get('show_minor', True)),
            'show_major': bool(params.get('show_major', True)),
            'show_numbers': bool(params.get('show_numbers', True)),
            'axis_arrows': str(params.get('axis_arrows') or 'both')[:12],
        }
        clean = {'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'xlabel': xlabel, 'ylabel': ylabel, **options}
        return _write_svg(kind, clean, _svg_coordinate_plane(xmin,xmax,ymin,ymax,xlabel=xlabel,ylabel=ylabel,options=options)), 'Blank coordinate plane'

    if kind == 'graph_paper':
        cols = safe_int(params.get('cols'), 20, 2, 80); rows = safe_int(params.get('rows'), 20, 2, 80)
        major_every = safe_int(params.get('major_every'), 5, 1, 40)
        show_minor=bool(params.get('show_minor',True)); show_major=bool(params.get('show_major',True)); show_border=bool(params.get('show_border',True))
        clean={'cols':cols,'rows':rows,'major_every':major_every,'show_minor':show_minor,'show_major':show_major,'show_border':show_border}
        width=720; height=720; m=30; pw=width-2*m; ph=height-2*m
        lines=[]
        for i in range(cols+1):
            x=m+pw*i/cols; major=(i%major_every==0)
            if major and show_major: lines.append(f'<line x1="{x:.2f}" y1="{m}" x2="{x:.2f}" y2="{height-m}" stroke="#888" stroke-width="1.05"/>')
            elif show_minor: lines.append(f'<line x1="{x:.2f}" y1="{m}" x2="{x:.2f}" y2="{height-m}" stroke="#aaa" stroke-width=".8"/>')
        for j in range(rows+1):
            y=m+ph*j/rows; major=(j%major_every==0)
            if major and show_major: lines.append(f'<line x1="{m}" y1="{y:.2f}" x2="{width-m}" y2="{y:.2f}" stroke="#888" stroke-width="1.05"/>')
            elif show_minor: lines.append(f'<line x1="{m}" y1="{y:.2f}" x2="{width-m}" y2="{y:.2f}" stroke="#aaa" stroke-width=".8"/>')
        border=f'<rect x="{m}" y="{m}" width="{pw}" height="{ph}" fill="none" stroke="#777" stroke-width="1.0"/>' if show_border else ''
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(lines)}{border}</svg>'
        return _write_svg(kind,clean,svg),'Graph paper'

    if kind == 'number_line':
        xmin = safe_number(params.get('xmin'), -10); xmax = safe_number(params.get('xmax'), 10)
        if xmax <= xmin: xmin, xmax = -10, 10
        span=xmax-xmin
        tick_step=safe_number(params.get('tick_step'), _nice_step(span,12), .01, 1e6)
        label_step=safe_number(params.get('label_step'), tick_step, .01, 1e6)
        show_ticks=bool(params.get('show_ticks',True)); show_labels=bool(params.get('show_labels',True))
        arrows=str(params.get('arrows') or 'both'); arrows=arrows if arrows in ('none','positive','both') else 'both'
        axis_label=str(params.get('axis_label') or '')[:30]
        clean={'xmin':xmin,'xmax':xmax,'tick_step':tick_step,'label_step':label_step,'show_ticks':show_ticks,'show_labels':show_labels,'arrows':arrows,'axis_label':axis_label}
        width=760; height=170; left=50; right=50; y=80
        def sx(x): return left+(x-xmin)/span*(width-left-right)
        parts=[f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#222" stroke-width="2.4"/>']
        if arrows in ('both','positive'): parts.append(f'<path d="M {width-right} {y} l -12 -7 l 0 14 z" fill="#222"/>')
        if arrows=='both': parts.append(f'<path d="M {left} {y} l 12 -7 l 0 14 z" fill="#222"/>')
        if show_ticks:
            for x in _tick_values(xmin,xmax,tick_step):
                px=sx(x); parts.append(f'<line x1="{px:.2f}" y1="{y-9}" x2="{px:.2f}" y2="{y+9}" stroke="#222" stroke-width="1.4"/>')
        if show_labels:
            for x in _tick_values(xmin,xmax,label_step):
                px=sx(x); parts.append(f'<text x="{px:.2f}" y="{y+32}" text-anchor="middle" font-family="Arial" font-size="14">{_fmt_tick(x)}</text>')
        if axis_label: parts.append(f'<text x="{width-right+8}" y="{y-15}" text-anchor="start" font-family="Arial" font-size="14" font-weight="700">{_svg_escape(axis_label)}</text>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(parts)}</svg>'
        return _write_svg(kind,clean,svg),'Blank number line'

    if kind in ('function_graph','parent_function'):
        xmin=safe_number(params.get('xmin'),-10); xmax=safe_number(params.get('xmax'),10); ymin=safe_number(params.get('ymin'),-10); ymax=safe_number(params.get('ymax'),10)
        if xmax<=xmin: xmin,xmax=-10,10
        if ymax<=ymin: ymin,ymax=-10,10
        if kind=='parent_function' and not params.get('expressions'):
            fn=str(params.get('function') or 'linear')
            parent={'linear':'y = x','quadratic':'y = x^2','absolute':'y = abs(x)','cubic':'y = x^3','sqrt':'y = sqrt(x)','reciprocal':'y = 1/x'}
            expressions=[parent.get(fn,'y = x')]
        else:
            expressions=params.get('expressions') or ['y = x']
        clean_exprs, series=_graph_expression_series(expressions,xmin,xmax)
        options = {
            'x_minor': safe_number(params.get('x_minor'), 1, 0.05, 1000),
            'y_minor': safe_number(params.get('y_minor'), 1, 0.05, 1000),
            'major_every': safe_int(params.get('major_every'), 5, 1, 50),
            'x_label_step': safe_number(params.get('x_label_step'), 5, 0.05, 1000),
            'y_label_step': safe_number(params.get('y_label_step'), 5, 0.05, 1000),
            'show_minor': bool(params.get('show_minor', True)),
            'show_major': bool(params.get('show_major', True)),
            'show_numbers': bool(params.get('show_numbers', True)),
            'axis_arrows': str(params.get('axis_arrows') or 'both')[:12],
        }
        xlabel=str(params.get('xlabel') or '')[:20]; ylabel=str(params.get('ylabel') or '')[:20]
        clean={'expressions':clean_exprs,'xmin':xmin,'xmax':xmax,'ymin':ymin,'ymax':ymax,'xlabel':xlabel,'ylabel':ylabel,**options}
        return _write_svg('function_graph',clean,_svg_coordinate_plane(xmin,xmax,ymin,ymax,series,xlabel,ylabel,options)), 'Function graph'

    if kind == 'diamond':
        clean={k:str(params.get(k) or '')[:24] for k in ('top','left','right','bottom')}
        show_diagonals=bool(params.get('show_diagonals',True)); font_size=safe_int(params.get('font_size'),28,16,44)
        clean.update({'show_diagonals':show_diagonals,'font_size':font_size})
        width=420; height=420; cx=210; cy=210; r=145
        cells={'top':(cx,145),'left':(140,cy+8),'right':(280,cy+8),'bottom':(cx,292)}
        texts=''.join(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial" font-size="{font_size}" font-weight="600">{_svg_escape(clean[k])}</text>' for k,(x,y) in cells.items() if clean[k])
        diagonals=(f'<line x1="{cx-r/2}" y1="{cy-r/2}" x2="{cx+r/2}" y2="{cy+r/2}" stroke="#222" stroke-width="2"/><line x1="{cx+r/2}" y1="{cy-r/2}" x2="{cx-r/2}" y2="{cy+r/2}" stroke="#222" stroke-width="2"/>') if show_diagonals else ''
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><polygon points="{cx},{cy-r} {cx+r},{cy} {cx},{cy+r} {cx-r},{cy}" fill="none" stroke="#222" stroke-width="3"/>{diagonals}{texts}</svg>'
        return _write_svg(kind,clean,svg),'Diamond problem'

    if kind == 'fraction_bar':
        parts=safe_int(params.get('parts'),4,1,20); shaded=safe_int(params.get('shaded'),0,0,parts); show_labels=bool(params.get('show_labels',False)); outline_weight=safe_number(params.get('outline_weight'),1.5,.5,4); clean={'parts':parts,'shaded':shaded,'show_labels':show_labels,'outline_weight':outline_weight}
        width=760; height=180; x=40; y=50; w=680; h=80; cell=w/parts; pieces=[]
        for i in range(parts):
            fill='#d9e8f5' if i<shaded else 'white'; pieces.append(f'<rect x="{x+i*cell:.2f}" y="{y}" width="{cell:.2f}" height="{h}" fill="{fill}" stroke="#222" stroke-width="{outline_weight}"/>');
            if show_labels: pieces.append(f'<text x="{x+(i+.5)*cell:.2f}" y="{y+h/2+5:.2f}" text-anchor="middle" font-family="Arial" font-size="13">1/{parts}</text>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(pieces)}</svg>'
        return _write_svg(kind,clean,svg),'Fraction bar'

    if kind == 'hundred_grid':
        shaded=safe_int(params.get('shaded'),0,0,100); order=str(params.get('shading_order') or 'row'); major_every=safe_int(params.get('major_every'),5,1,10); show_major=bool(params.get('show_major',True)); clean={'shaded':shaded,'shading_order':order,'major_every':major_every,'show_major':show_major}; width=620; height=620; m=35; cell=(width-2*m)/10; pieces=[]
        for r in range(10):
            for c in range(10):
                i=(c*10+r) if order=='column' else (r*10+c); fill='#d9e8f5' if i<shaded else 'white'; sw=1.5 if show_major and (r%major_every==0 or c%major_every==0) else .8; pieces.append(f'<rect x="{m+c*cell:.2f}" y="{m+r*cell:.2f}" width="{cell:.2f}" height="{cell:.2f}" fill="{fill}" stroke="#555" stroke-width="{sw}"/>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(pieces)}</svg>'
        return _write_svg(kind,clean,svg),'Hundred grid'

    if kind == 'area_model':
        rows=[str(x)[:18] for x in (params.get('rows') or ['x','1'])][:6] or ['x','1']; cols=[str(x)[:18] for x in (params.get('cols') or ['x','1'])][:6] or ['x','1']; show_labels=bool(params.get('show_labels',True)); label_size=safe_int(params.get('label_size'),24,12,40); clean={'rows':rows,'cols':cols,'show_labels':show_labels,'label_size':label_size}
        width=720; height=520; left=120; top=95; right=35; bottom=35; gw=width-left-right; gh=height-top-bottom; cw=gw/len(cols); rh=gh/len(rows); pieces=[]
        if show_labels:
            for c,label in enumerate(cols): pieces.append(f'<text x="{left+(c+.5)*cw:.2f}" y="62" text-anchor="middle" font-family="Arial" font-size="{label_size}">{_svg_escape(label)}</text>')
            for r,label in enumerate(rows): pieces.append(f'<text x="70" y="{top+(r+.5)*rh+8:.2f}" text-anchor="middle" font-family="Arial" font-size="{label_size}">{_svg_escape(label)}</text>')
        for r in range(len(rows)):
            for c in range(len(cols)): pieces.append(f'<rect x="{left+c*cw:.2f}" y="{top+r*rh:.2f}" width="{cw:.2f}" height="{rh:.2f}" fill="white" stroke="#222" stroke-width="1.7"/>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(pieces)}</svg>'
        return _write_svg(kind,clean,svg),'Area model'

    if kind == 'input_output_table':
        orientation=str(params.get('orientation') or 'vertical')
        count=safe_int(params.get('count'),6,2,16)
        input_label=str(params.get('input_label') or 'Input')[:24]
        output_label=str(params.get('output_label') or 'Output')[:24]
        show_header=bool(params.get('show_header',True))
        line_weight=safe_number(params.get('line_weight'),1.2,.5,4)
        clean={'orientation':orientation,'count':count,'input_label':input_label,'output_label':output_label,'show_header':show_header,'line_weight':line_weight}
        pieces=[]
        if orientation=='horizontal':
            width=760; height=260; left=30; top=45; cols=count+1; cw=(width-60)/cols; rh=80
            labels=[input_label if show_header else '']+['' for _ in range(count)]
            labels2=[output_label if show_header else '']+['' for _ in range(count)]
            for r,row in enumerate((labels,labels2)):
                for c,val in enumerate(row):
                    fill='#f2f5f7' if c==0 and show_header else 'white'
                    pieces.append(f'<rect x="{left+c*cw:.2f}" y="{top+r*rh:.2f}" width="{cw:.2f}" height="{rh}" fill="{fill}" stroke="#222" stroke-width="{line_weight}"/>')
                    if val: pieces.append(f'<text x="{left+(c+.5)*cw:.2f}" y="{top+r*rh+49:.2f}" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600">{_svg_escape(val)}</text>')
        else:
            width=500; height=max(360,100+count*55); left=60; top=35; cw=190; header_rows=1 if show_header else 0; rh=(height-70)/(count+header_rows)
            row_offset=0
            if show_header:
                pieces.append(f'<rect x="{left}" y="{top}" width="{cw}" height="{rh:.2f}" fill="#f2f5f7" stroke="#222" stroke-width="{line_weight}"/><rect x="{left+cw}" y="{top}" width="{cw}" height="{rh:.2f}" fill="#f2f5f7" stroke="#222" stroke-width="{line_weight}"/>')
                pieces.append(f'<text x="{left+cw/2}" y="{top+rh*.62:.2f}" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600">{_svg_escape(input_label)}</text><text x="{left+cw+cw/2}" y="{top+rh*.62:.2f}" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600">{_svg_escape(output_label)}</text>')
                row_offset=1
            for r in range(count):
                y=top+(r+row_offset)*rh
                pieces.append(f'<rect x="{left}" y="{y:.2f}" width="{cw}" height="{rh:.2f}" fill="white" stroke="#222" stroke-width="{line_weight}"/><rect x="{left+cw}" y="{y:.2f}" width="{cw}" height="{rh:.2f}" fill="white" stroke="#222" stroke-width="{line_weight}"/>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(pieces)}</svg>'
        return _write_svg(kind,clean,svg),'Input-output table'

    if kind == 'unit_circle':
        mode=str(params.get('mode') or 'blank'); show_axes=bool(params.get('show_axes',True)); show_rays=bool(params.get('show_rays',False)); show_points=bool(params.get('show_points',True)); show_axis_labels=bool(params.get('show_axis_labels',False)); clean={'mode':mode,'show_axes':show_axes,'show_rays':show_rays,'show_points':show_points,'show_axis_labels':show_axis_labels}; width=height=600; cx=cy=300; r=220; pieces=[f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#222" stroke-width="2.5"/>']
        if show_axes:
            pieces += [f'<line x1="55" y1="{cy}" x2="545" y2="{cy}" stroke="#222" stroke-width="1.8"/>',f'<line x1="{cx}" y1="55" x2="{cx}" y2="545" stroke="#222" stroke-width="1.8"/>']
            if show_axis_labels: pieces += [f'<text x="552" y="{cy-8}" font-family="Arial" font-size="15" font-weight="700">x</text>', f'<text x="{cx+8}" y="48" font-family="Arial" font-size="15" font-weight="700">y</text>']
        if mode in ('angles','degrees_radians'):
            labels_rad={0:'0',30:'π/6',45:'π/4',60:'π/3',90:'π/2',120:'2π/3',135:'3π/4',150:'5π/6',180:'π',210:'7π/6',225:'5π/4',240:'4π/3',270:'3π/2',300:'5π/3',315:'7π/4',330:'11π/6'}
            angles=list(labels_rad)
            for deg in angles:
                a=math.radians(deg); x=cx+r*math.cos(a); y=cy-r*math.sin(a);
                if show_rays: pieces.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="#aaa" stroke-width=".8"/>')
                if show_points: pieces.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="#222"/>')
                tx=cx+(r+30)*math.cos(a); ty=cy-(r+30)*math.sin(a)+5
                label=f'{deg}°' if mode=='angles' else labels_rad[deg]
                pieces.append(f'<text x="{tx:.2f}" y="{ty:.2f}" text-anchor="middle" font-family="Arial" font-size="14">{label}</text>')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{"".join(pieces)}</svg>'
        return _write_svg(kind,clean,svg),'Unit circle'

    raise ValueError('Unsupported visual type')


def _canonical_visual(kind, params):
    module = load_graph_tool()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)

    if kind == 'blank_graph':
        advanced_keys=('x_minor','y_minor','major_every','x_label_step','y_label_step','show_minor','show_major','show_numbers','axis_arrows')
        if any(k in params for k in advanced_keys):
            raise ValueError('portable SVG renderer')
        xmin = safe_number(params.get('xmin'), -10); xmax = safe_number(params.get('xmax'), 10)
        ymin = safe_number(params.get('ymin'), -10); ymax = safe_number(params.get('ymax'), 10)
        if xmax <= xmin: xmin, xmax = -10, 10
        if ymax <= ymin: ymin, ymax = -10, 10
        xlabel = str(params.get('xlabel') or '')[:20]; ylabel = str(params.get('ylabel') or '')[:20]
        clean_params = {'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'xlabel': xlabel, 'ylabel': ylabel}
        filename = visual_cache_name(kind, clean_params, 'svg'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists():
            fig, ax = plt.subplots(figsize=(4.1, 4.1)); module.make_window_graph(ax, [], xmin, xmax, ymin, ymax, title='', xlabel=xlabel, ylabel=ylabel); fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03); save_svg(fig, filename); plt.close(fig)
        return path, 'Blank coordinate plane'

    if kind == 'number_line':
        if any(k in params for k in ('tick_step','label_step','show_ticks','show_labels','arrows','axis_label')):
            raise ValueError('portable SVG renderer')
        xmin = safe_number(params.get('xmin'), -10); xmax = safe_number(params.get('xmax'), 10)
        if xmax <= xmin: xmin, xmax = -10, 10
        clean_params = {'xmin': xmin, 'xmax': xmax}; filename = visual_cache_name(kind, clean_params, 'svg'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists():
            fig, ax = plt.subplots(figsize=(6.4, 1.45)); module.make_number_line_blank(ax, xmin=xmin, xmax=xmax); save_svg(fig, filename); plt.close(fig)
        return path, 'Blank number line'

    if kind == 'parent_function':
        fn_name = str(params.get('function') or 'linear')
        mappings = {
            'linear': (lambda x: x, lambda x: np.ones_like(x), 'Linear parent function'),
            'quadratic': (lambda x: x**2, lambda x: 2*x, 'Quadratic parent function'),
            'absolute': (lambda x: np.abs(x), lambda x: np.where(x < 0, -1.0, 1.0), 'Absolute value parent function'),
            'cubic': (lambda x: x**3, lambda x: 3*x**2, 'Cubic parent function'),
            'sqrt': (lambda x: np.where(x >= 0, np.sqrt(x), np.nan), lambda x: np.where(x > 0, 1/(2*np.sqrt(x)), np.nan), 'Square root parent function'),
            'reciprocal': (lambda x: np.where(np.abs(x)>1e-8, 1/x, np.nan), lambda x: np.where(np.abs(x)>1e-8, -1/(x**2), np.nan), 'Reciprocal parent function'),
        }
        expr, deriv, label = mappings.get(fn_name, mappings['linear'])
        xmin=safe_number(params.get('xmin'),-10); xmax=safe_number(params.get('xmax'),10); ymin=safe_number(params.get('ymin'),-10); ymax=safe_number(params.get('ymax'),10)
        if xmax<=xmin: xmin,xmax=-10,10
        if ymax<=ymin: ymin,ymax=-10,10
        clean_params = {'function': fn_name, 'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax}; filename = visual_cache_name(kind, clean_params, 'svg'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists():
            fig, ax = plt.subplots(figsize=(4.1, 4.1)); module.make_window_graph(ax, [{'expr':expr,'deriv':deriv,'color':'steelblue','label':None}], xmin, xmax, ymin, ymax, title='', xlabel='', ylabel=''); fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03); save_svg(fig, filename); plt.close(fig)
        return path, label

    if kind == 'diamond':
        if any(k in params for k in ('show_diagonals','font_size')):
            raise ValueError('portable SVG renderer')
        clean_params = {k: str(params.get(k) or '')[:24] for k in ('top','left','right','bottom')}; filename = visual_cache_name(kind, clean_params, 'png'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists(): module.make_diamond(clean_params['top'], clean_params['left'], clean_params['right'], clean_params['bottom'], filename=filename)
        return path, 'Diamond problem'

    if kind == 'fraction_bar':
        if any(k in params for k in ('show_labels','outline_weight')):
            raise ValueError('portable SVG renderer')
        parts = safe_int(params.get('parts'), 4, 1, 20); shaded = safe_int(params.get('shaded'), 0, 0, parts); clean_params = {'parts':parts,'shaded':shaded}; filename = visual_cache_name(kind, clean_params, 'png'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists(): module.make_fraction_bar(parts, shaded, filename=filename)
        return path, 'Fraction bar'

    if kind == 'hundred_grid':
        if any(k in params for k in ('shading_order','major_every','show_major')):
            raise ValueError('portable SVG renderer')
        shaded = safe_int(params.get('shaded'), 0, 0, 100); clean_params = {'shaded':shaded}; filename = visual_cache_name(kind, clean_params, 'png'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists(): module.make_hundred_grid(shaded, filename=filename)
        return path, 'Hundred grid'

    if kind == 'area_model':
        if any(k in params for k in ('show_labels','label_size')):
            raise ValueError('portable SVG renderer')
        rows = [str(x)[:18] for x in (params.get('rows') or ['x','1'])][:4] or ['x','1']; cols = [str(x)[:18] for x in (params.get('cols') or ['x','1'])][:4] or ['x','1']; cells = [['' for _ in cols] for _ in rows]; clean_params = {'rows':rows,'cols':cols}; filename = visual_cache_name(kind, clean_params, 'png'); path = GENERATED_VISUAL_DIR / filename
        if not path.exists(): module.make_rectangle_model(rows, cols, cells, filename=filename)
        return path, 'Area model'

    if kind == 'unit_circle' and hasattr(module, 'make_unit_circle_blank'):
        if any(k in params for k in ('show_axes','show_rays','show_points','show_axis_labels')):
            raise ValueError('portable SVG renderer')
        mode=str(params.get('mode') or 'blank'); clean_params={'mode':mode}; filename=visual_cache_name(kind,clean_params,'png'); path=GENERATED_VISUAL_DIR/filename
        if not path.exists():
            if mode=='blank' or not hasattr(module,'make_unit_circle_angles'): module.make_unit_circle_blank(filename=filename)
            else: module.make_unit_circle_angles(filename=filename)
        return path,'Unit circle'

    raise ValueError('Use portable SVG renderer for this visual type')


def generate_visual(kind, params):
    # Prefer the registered canonical graph tool; use a deterministic SVG fallback when its plotting stack is unavailable.
    force_fallback = os.environ.get('CC3_FORCE_SVG_FALLBACK') == '1'
    if not force_fallback:
        try:
            return _canonical_visual(kind, params)
        except (ModuleNotFoundError, ImportError):
            pass
        except ValueError as exc:
            if 'portable SVG renderer' not in str(exc):
                raise
        except RuntimeError:
            pass
    return _fallback_visual(kind, params)

@lru_cache(maxsize=1)
def blank_coordinate_plane_svg():
    path, _ = generate_visual('blank_graph', {'xmin':-10,'xmax':10,'ymin':-10,'ymax':10})
    if path.suffix.lower() == '.svg':
        return path.read_bytes()
    return _fallback_visual('blank_graph', {'xmin':-10,'xmax':10,'ymin':-10,'ymax':10})[0].read_bytes()


def _assessment_visual_path_canonical(query):
    """Generate a deterministic same-family assessment visual through the canonical graph tool."""
    kind = str((query.get('kind') or [''])[0]).strip().lower()
    if not kind:
        raise ValueError('Missing assessment visual kind.')
    module = load_graph_tool()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    def q(name, default=''):
        return (query.get(name) or [default])[0]
    def qnum(name, default, low=-1000, high=1000):
        return safe_number(q(name, default), default, low, high)
    def qcsv(name):
        raw = str(q(name, '') or '')
        vals=[]
        for part in raw.split(','):
            part=part.strip()
            if not part:
                continue
            vals.append(safe_number(part, 0))
        return vals

    GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    clean = {'kind': kind, **{k: (v[0] if isinstance(v, list) and v else '') for k,v in sorted(query.items())}}
    ext = 'png' if kind in ('tiles','diamond') else 'svg'
    filename = visual_cache_name('assessment_' + kind, clean, ext)
    path = GENERATED_VISUAL_DIR / filename
    if path.exists():
        return path

    if kind == 'tiles':
        expression = {}
        for key in ('x2','neg_x2','x','neg_x','one','neg_one'):
            n = safe_int(q(key, 0), 0, 0, 20)
            if n:
                expression[key] = n
        if not expression:
            expression = {'x': 1}
        module.make_algebra_tiles(expression, filename=filename)
        return path

    if kind == 'diamond':
        module.make_diamond(str(q('top','')), str(q('left','')), str(q('right','')), str(q('bottom','')), filename=filename)
        return path

    xmin=qnum('xmin',-10); xmax=qnum('xmax',10); ymin=qnum('ymin',-10); ymax=qnum('ymax',10)
    if xmax <= xmin: xmin, xmax = -10, 10
    if ymax <= ymin: ymin, ymax = -10, 10
    xlabel=str(q('xlabel',''))[:40]; ylabel=str(q('ylabel',''))[:40]

    if kind == 'blank':
        fig, ax = plt.subplots(figsize=(4.3,4.3))
        module.make_window_graph(ax, [], xmin, xmax, ymin, ymax, title='', xlabel=xlabel, ylabel=ylabel)
        fig.subplots_adjust(left=.05,right=.97,top=.97,bottom=.05)
        save_svg(fig, filename); plt.close(fig); return path

    if kind == 'point':
        x=qnum('x',2,xmin,xmax); y=qnum('y',3,ymin,ymax); label=str(q('label',''))[:8]
        fig, ax = plt.subplots(figsize=(4.6,4.1))
        if str(q('context','0')) == '1':
            module.make_context_graph(ax, [], xmin, xmax, ymin, ymax, xlabel=xlabel or 'x', ylabel=ylabel or 'y', title='')
        else:
            module.make_window_graph(ax, [], xmin, xmax, ymin, ymax, title='', xlabel=xlabel, ylabel=ylabel)
        ax.scatter([x],[y],s=45,color='steelblue',zorder=6)
        if label:
            ax.text(x, y, '  '+label, fontsize=11, fontweight='bold', fontfamily='Arial', va='bottom', ha='left', zorder=7)
        fig.subplots_adjust(left=.10,right=.95,top=.95,bottom=.12)
        save_svg(fig, filename); plt.close(fig); return path

    if kind == 'line':
        m=qnum('m',2,-20,20); b=qnum('b',0,-100,100)
        fn=lambda x: m*np.asarray(x)+b
        deriv=lambda x: np.asarray(x)*0+m
        functions=[{'expr':fn,'deriv':deriv,'color':'steelblue','label':None}]
        fig, ax = plt.subplots(figsize=(4.6,4.1))
        if str(q('context','0')) == '1':
            module.make_context_graph(ax, functions, xmin, xmax, ymin, ymax, xlabel=xlabel or 'x', ylabel=ylabel or 'y', title='')
        else:
            module.make_window_graph(ax, functions, xmin, xmax, ymin, ymax, title='', xlabel=xlabel, ylabel=ylabel)
        fig.subplots_adjust(left=.10,right=.95,top=.95,bottom=.12)
        save_svg(fig, filename); plt.close(fig); return path

    if kind == 'piecewise':
        a=qnum('a',3,xmin,xmax); b=qnum('b',6,xmin,xmax); level=qnum('y',60,ymin,ymax)
        if b <= a: b = min(xmax-1, a+2)
        start_y=max(ymin, level*0.25)
        end_y=min(ymax, level + max(10,(ymax-ymin)*0.22))
        fig, ax = plt.subplots(figsize=(4.6,4.1))
        module.make_context_graph(ax, [], xmin, xmax, ymin, ymax, xlabel=xlabel or 'x', ylabel=ylabel or 'y', title='')
        xs=[xmin,a,b,xmax]; ys=[start_y,level,level,end_y]
        ax.plot(xs,ys,color='steelblue',linewidth=getattr(module,'CURVE_WIDTH',2.0),zorder=4)
        ax.scatter(xs,ys,s=18,color='steelblue',zorder=5)
        fig.subplots_adjust(left=.10,right=.95,top=.95,bottom=.12)
        save_svg(fig, filename); plt.close(fig); return path

    if kind == 'scatter':
        xs=qcsv('x'); ys=qcsv('y')
        if not xs or len(xs) != len(ys):
            xs=[1,2,3,4,5,6]; ys=[2,4,7,8,11,12]
        fig, ax = plt.subplots(figsize=(4.6,4.1))
        module.make_scatter_plot(ax, xs, ys, xmin, xmax, ymin, ymax, xlabel=xlabel or 'x', ylabel=ylabel or 'y', title='')
        fig.subplots_adjust(left=.12,right=.95,top=.95,bottom=.13)
        save_svg(fig, filename); plt.close(fig); return path

    raise ValueError('Unsupported assessment visual kind.')


def _assessment_visual_query_value(query, name, default=''):
    return (query.get(name) or [default])[0]


def _assessment_visual_portable(query):
    """Portable SVG assessment renderer.

    Assessment variants must work on teacher machines even when the optional
    matplotlib/numpy stack used by the registered graph tool is unavailable.
    This renderer intentionally reuses the app's existing deterministic SVG
    coordinate-plane authority and only supplies the generated relation/model
    geometry needed by same-family assessment variants.
    """
    kind = str(_assessment_visual_query_value(query, 'kind', '')).strip().lower()
    if not kind:
        raise ValueError('Missing assessment visual kind.')

    def q(name, default=''):
        return _assessment_visual_query_value(query, name, default)

    def qnum(name, default, low=-1000, high=1000):
        return safe_number(q(name, default), default, low, high)

    def qint(name, default=0, low=0, high=100):
        return safe_int(q(name, default), default, low, high)

    def qcsv(name):
        values=[]
        for part in str(q(name, '') or '').split(','):
            part=part.strip()
            if not part:
                continue
            values.append(safe_number(part, 0))
        return values

    xmin=qnum('xmin',-10); xmax=qnum('xmax',10)
    ymin=qnum('ymin',-10); ymax=qnum('ymax',10)
    if xmax <= xmin:
        xmin, xmax = -10, 10
    if ymax <= ymin:
        ymin, ymax = -10, 10
    xlabel=str(q('xlabel',''))[:40]
    ylabel=str(q('ylabel',''))[:40]
    context=str(q('context','0')) == '1'
    plane_options={
        'axis_arrows': 'positive' if context else 'both',
        'show_minor': True,
        'show_major': True,
        'show_numbers': True,
    }

    clean={'kind':kind, **{k:(v[0] if isinstance(v,list) and v else '') for k,v in sorted(query.items())}}
    filename=visual_cache_name('assessment_portable_'+kind, clean, 'svg')
    path=GENERATED_VISUAL_DIR / filename
    if path.exists():
        return path

    def write(svg_text):
        GENERATED_VISUAL_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(svg_text, encoding='utf-8')
        return path

    # Coordinate mapping must match _svg_coordinate_plane().
    width=height=560; left=right=54; top=bottom=42
    plot_w=width-left-right; plot_h=height-top-bottom
    xspan=xmax-xmin; yspan=ymax-ymin
    def sx(x): return left + (float(x)-xmin)/xspan*plot_w
    def sy(y): return top + (ymax-float(y))/yspan*plot_h
    def overlay(svg, markup):
        return svg.replace('</svg>', markup + '</svg>')

    def plane(plotted):
        # Keep assessment axis labels inside the SVG viewBox. The generic
        # portable renderer intentionally allows labels to overflow, which is
        # useful in its editor preview but can be clipped by an <img> element.
        svg=_svg_coordinate_plane(xmin,xmax,ymin,ymax,plotted,'','',plane_options)
        labels=[]
        if xlabel:
            labels.append(f'<text x="{width-right-4}" y="{height-10}" text-anchor="end" font-family="Arial" font-size="15" font-weight="700" fill="#222222">{_svg_escape(xlabel)}</text>')
        if ylabel:
            labels.append(f'<text x="{left+6}" y="24" text-anchor="start" font-family="Arial" font-size="15" font-weight="700" fill="#222222">{_svg_escape(ylabel)}</text>')
        return overlay(svg,''.join(labels))

    if kind == 'blank':
        return write(plane([]))

    if kind == 'line':
        m=qnum('m',2,-20,20); b=qnum('b',0,-100,100)
        samples=181
        points=[]
        for i in range(samples):
            x=xmin+(xmax-xmin)*i/(samples-1)
            points.append((x,m*x+b))
        svg=plane([{'points':points,'color':'#4682b4'}])
        return write(svg)

    if kind == 'point':
        x=qnum('x',2,xmin,xmax); y=qnum('y',3,ymin,ymax); label=str(q('label',''))[:12]
        svg=plane([])
        markup=f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="6" fill="#4682b4"/>'
        if label:
            markup += f'<text x="{sx(x)+10:.2f}" y="{sy(y)-10:.2f}" font-family="Arial" font-size="15" font-weight="700">{_svg_escape(label)}</text>'
        return write(overlay(svg,markup))

    if kind == 'piecewise':
        a=qnum('a',3,xmin,xmax); b=qnum('b',6,xmin,xmax); level=qnum('y',60,ymin,ymax)
        if b <= a:
            b=min(xmax-1,a+2)
        start_y=max(ymin,level*0.25)
        end_y=min(ymax,level+max(10,(ymax-ymin)*0.22))
        points=[(xmin,start_y),(a,level),(b,level),(xmax,end_y)]
        svg=plane([{'points':points,'color':'#4682b4'}])
        circles=''.join(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="4" fill="#4682b4"/>' for x,y in points)
        return write(overlay(svg,circles))

    if kind == 'scatter':
        xs=qcsv('x'); ys=qcsv('y')
        if not xs or len(xs) != len(ys):
            xs=[1,2,3,4,5,6]; ys=[2,4,7,8,11,12]
        svg=plane([])
        circles=[]
        for x,y in zip(xs,ys):
            if xmin <= x <= xmax and ymin <= y <= ymax:
                circles.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="5" fill="#4682b4"/>')
        return write(overlay(svg,''.join(circles)))

    if kind == 'diamond':
        params={k:str(q(k,''))[:24] for k in ('top','left','right','bottom')}
        generated,_=_fallback_visual('diamond',params)
        return generated

    if kind == 'tiles':
        counts={
            'x2':qint('x2',0,0,20), 'neg_x2':qint('neg_x2',0,0,20),
            'x':qint('x',0,0,20), 'neg_x':qint('neg_x',0,0,20),
            'one':qint('one',0,0,40), 'neg_one':qint('neg_one',0,0,40),
        }
        if not any(counts.values()):
            counts['x']=1
        tile_specs={
            'x2':(80,80,'#5bacd6','x²'), 'neg_x2':(80,80,'#e05c5c','−x²'),
            'x':(34,92,'#5bacd6','x'), 'neg_x':(34,92,'#e05c5c','−x'),
            'one':(34,34,'#3a3ab0','1'), 'neg_one':(34,34,'#e05c5c','−1'),
        }
        tiles=[]
        for key in ('x2','neg_x2','x','neg_x','one','neg_one'):
            tiles.extend([key]*counts[key])
        canvas_w=620; gap=12; pad=24; max_x=canvas_w-pad
        xcur=pad; ycur=pad; row_h=0; shapes=[]
        for key in tiles:
            tw,th,color,label=tile_specs[key]
            if xcur+tw > max_x and xcur>pad:
                xcur=pad; ycur += row_h+gap; row_h=0
            shapes.append(f'<rect x="{xcur}" y="{ycur}" width="{tw}" height="{th}" rx="4" fill="{color}" stroke="white" stroke-width="2"/>')
            shapes.append(f'<text x="{xcur+tw/2:.1f}" y="{ycur+th/2+5:.1f}" text-anchor="middle" font-family="Arial" font-size="{18 if tw>=60 else 14}" font-weight="700" fill="white">{label}</text>')
            xcur += tw+gap; row_h=max(row_h,th)
        canvas_h=max(150,ycur+row_h+pad)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}"><rect width="100%" height="100%" fill="white"/>{"".join(shapes)}</svg>'
        return write(svg)

    raise ValueError('Unsupported assessment visual kind.')


def assessment_visual_path(query):
    """Render an assessment visual, preferring the canonical graph tool.

    The existing Teacher Tools visual system already permits a portable SVG
    fallback when the plotting stack is unavailable. Same-family assessment
    generation now follows that same rule instead of returning broken images.
    """
    if os.environ.get('CC3_FORCE_SVG_FALLBACK') != '1':
        try:
            return _assessment_visual_path_canonical(query)
        except Exception as exc:
            # A teacher machine may not have numpy/matplotlib available to the
            # launcher Python. Do not break the assessment; render the same
            # mathematical object with the deterministic local SVG fallback.
            print(f'Assessment visual canonical renderer unavailable; using portable SVG: {exc}')
    return _assessment_visual_portable(query)


def send_file_response(handler, path):
    data = path.read_bytes()
    suffix = path.suffix.lower()
    content_type = 'image/svg+xml; charset=utf-8' if suffix == '.svg' else 'image/png'
    handler.send_response(200)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(data)))
    handler.send_header('Cache-Control', 'no-store')
    handler.end_headers()
    handler.wfile.write(data)


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self, max_bytes):
        try:
            length = int(self.headers.get('Content-Length') or '0')
        except ValueError:
            length = 0
        if length <= 0 or length > max_bytes:
            raise ValueError('Invalid request size.')
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def read_bytes_body(self, max_bytes):
        try:
            length = int(self.headers.get('Content-Length') or '0')
        except ValueError:
            length = 0
        if length <= 0 or length > max_bytes:
            raise ValueError('Invalid request size.')
        data = self.rfile.read(length)
        if len(data) != length:
            raise ValueError('Upload was incomplete.')
        return data

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/creation-source':
            try:
                data = self.read_bytes_body(MAX_CREATION_SOURCE_BYTES)
                filename = unquote(self.headers.get('X-Filename') or 'source')
                saved = save_creation_source(data, filename)
                self.send_json(201, {'ok': True, **saved})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        if path == '/api/creation-existing':
            try:
                payload = self.read_json_body(MAX_CREATION_REQUEST_BYTES)
                saved = save_existing_creation(payload)
                self.send_json(201, {'ok': True, **saved})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        if path == '/api/creation-request/create':
            try:
                payload = self.read_json_body(MAX_CREATION_REQUEST_BYTES)
                created = create_creation_request(payload)
                self.send_json(201, {'ok': True, **created})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        creation_match = re.fullmatch(r'/api/creation-request/([A-Za-z0-9_.-]+)/result', path)
        if creation_match:
            try:
                request_id = _creation_request_id(creation_match.group(1))
                data = self.read_bytes_body(MAX_CREATION_RESULT_BYTES)
                filename = unquote(self.headers.get('X-Filename') or 'CC3_Creation_Result.zip')
                saved = save_creation_result_upload(request_id, data, filename)
                self.send_json(201, {'ok': True, **saved})
            except FileNotFoundError as exc:
                self.send_json(404, {'ok': False, 'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        if path == '/api/summative-request/create':
            try:
                payload = self.read_json_body(MAX_SUMMATIVE_REQUEST_BYTES)
                created = create_summative_request(payload)
                self.send_json(201, {'ok': True, **created})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        match = re.fullmatch(r'/api/summative-request/([A-Za-z0-9_.-]+)/result', path)
        if match:
            try:
                request_id = _summative_request_id(match.group(1))
                data = self.read_bytes_body(MAX_SUMMATIVE_RESULT_BYTES)
                filename = unquote(self.headers.get('X-Filename') or 'CC3_Summative_Result.zip')
                saved = save_summative_result_upload(request_id, data, filename)
                self.send_json(201, {'ok': True, **saved})
            except FileNotFoundError as exc:
                self.send_json(404, {'ok': False, 'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return

        if path == '/api/saved-sets':
            try:
                payload = self.read_json_body(MAX_SAVED_SET_BYTES)
                if not isinstance(payload, dict):
                    raise ValueError('Invalid saved set request.')
                record = write_saved_set(payload)
                self.send_json(200 if payload.get('id') else 201, {
                    'id': record['id'], 'name': record['name'],
                    'created_at': record['created_at'], 'updated_at': record['updated_at']
                })
            except FileNotFoundError as exc:
                self.send_json(404, {'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'error': str(exc)})
            return

        if path == '/api/visuals/generate':
            try:
                payload = self.read_json_body(128 * 1024)
                kind = str(payload.get('type') or '')
                params = payload.get('params') if isinstance(payload.get('params'), dict) else {}
                generated, label = generate_visual(kind, params)
                self.send_json(201, {
                    'url': '/library/generated_visuals/' + generated.name,
                    'label': label,
                    'filename': generated.name,
                    'type': kind,
                })
            except Exception as exc:
                self.send_json(400, {'error': str(exc)})
            return

        if path != '/api/uploads/custom-image':
            self.send_json(404, {'error': 'Unknown endpoint'})
            return

        content_type = (self.headers.get('Content-Type') or '').split(';', 1)[0].strip().lower()
        ext = ALLOWED_CUSTOM_IMAGE_TYPES.get(content_type)
        if not ext:
            self.send_json(415, {'error': 'Use a PNG, JPG, GIF, or WebP image.'})
            return
        try:
            length = int(self.headers.get('Content-Length') or '0')
        except ValueError:
            length = 0
        if length <= 0:
            self.send_json(400, {'error': 'The uploaded image was empty.'})
            return
        if length > MAX_CUSTOM_IMAGE_BYTES:
            self.send_json(413, {'error': 'Image must be 15 MB or smaller.'})
            return

        data = self.rfile.read(length)
        if len(data) != length or not image_bytes_match(data, content_type):
            self.send_json(400, {'error': 'The uploaded file does not match the selected image type.'})
            return

        original = unquote(self.headers.get('X-Filename') or 'teacher-image')
        digest = hashlib.sha256(data).hexdigest()[:16]
        safe_stem = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in Path(original).stem)[:48].strip('_') or 'teacher_image'
        filename = f'{safe_stem}_{digest}{ext}'
        USER_ASSET_DIR.mkdir(parents=True, exist_ok=True)
        destination = USER_ASSET_DIR / filename
        if not destination.exists():
            destination.write_bytes(data)
        self.send_json(201, {
            'url': f'/library/user_assets/{filename}',
            'filename': filename,
            'original_name': original,
        })

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        creation_match = re.fullmatch(r'/api/creation-request/([A-Za-z0-9_.-]+)\.zip', path)
        if creation_match:
            try:
                request_id = _creation_request_id(creation_match.group(1))
                target = _creation_request_zip_path(request_id)
                if not target.is_file():
                    raise FileNotFoundError('Creation request ZIP was not found.')
                data = target.read_bytes()
                request = _read_creation_request(request_id)
                title = _safe_slug(request.get('title') or request.get('kind'), 'cc3_creation')
                filename = f'{title}_{request_id}_REQUEST.zip'
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError as exc:
                self.send_json(404, {'ok': False, 'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return
        match = re.fullmatch(r'/api/summative-request/([A-Za-z0-9_.-]+)\.zip', path)
        if match:
            try:
                request_id = _summative_request_id(match.group(1))
                target = _summative_request_zip_path(request_id)
                if not target.is_file():
                    raise FileNotFoundError('Summative request ZIP was not found.')
                data = target.read_bytes()
                request = _read_summative_request(request_id)
                title = _safe_slug(request.get('document_title') or request.get('assessment_type'), 'cc3_summative')
                filename = f'{title}_{request_id}_REQUEST.zip'
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError as exc:
                self.send_json(404, {'ok': False, 'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'ok': False, 'error': str(exc)})
            return
        if path == '/api/assessment-visual':
            try:
                send_file_response(self, assessment_visual_path(parse_qs(parsed.query, keep_blank_values=True)))
            except Exception as exc:
                msg = f'Assessment visual error: {exc}'.encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type','text/plain; charset=utf-8')
                self.send_header('Content-Length',str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
            return
        if path == '/api/content-scope':
            self.send_json(200, {'chapters': content_scope_catalog()})
            return
        if path == '/api/saved-sets':
            self.send_json(200, {'items': list_saved_sets()})
            return
        if path.startswith('/api/saved-sets/'):
            saved_id = path.rsplit('/', 1)[-1]
            try:
                self.send_json(200, read_saved_set(saved_id))
            except FileNotFoundError as exc:
                self.send_json(404, {'error': str(exc)})
            except Exception as exc:
                self.send_json(400, {'error': str(exc)})
            return
        if path == '/api/graph/blank-coordinate-plane.svg':
            try:
                data = blank_coordinate_plane_svg()
                self.send_response(200)
                self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(data)
            except Exception as exc:
                msg = f'Canonical graph tool error: {exc}'.encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
            return
        super().do_GET()

    def do_DELETE(self):
        path = urlparse(self.path).path
        if not path.startswith('/api/saved-sets/'):
            self.send_json(404, {'error': 'Unknown endpoint'})
            return
        saved_id = path.rsplit('/', 1)[-1]
        try:
            target = saved_set_path(saved_id)
            if not target.is_file():
                raise FileNotFoundError('Saved set not found.')
            target.unlink()
            self.send_json(200, {'deleted': saved_id})
        except FileNotFoundError as exc:
            self.send_json(404, {'error': str(exc)})
        except Exception as exc:
            self.send_json(400, {'error': str(exc)})

    def end_headers(self):
        self.send_header('Cache-Control','no-store, no-cache, must-revalidate')
        self.send_header('Pragma','no-cache')
        self.send_header('Expires','0')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state-file',required=True); args=ap.parse_args()
    state=Path(args.state_file)
    handler=lambda *a,**kw: Handler(*a,directory=str(ROOT),**kw)
    httpd=ThreadingHTTPServer(('127.0.0.1',0),handler)
    port=httpd.server_address[1]
    state.parent.mkdir(parents=True,exist_ok=True)
    state.write_text(json.dumps({'pid':os.getpid(),'port':port,'root':str(ROOT),'started':time.time()}))
    try: httpd.serve_forever()
    finally:
        try:
            if state.exists() and json.loads(state.read_text()).get('pid')==os.getpid(): state.unlink()
        except Exception: pass


if __name__=='__main__': main()
