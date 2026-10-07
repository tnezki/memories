#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import html
import json
import mimetypes
import random
import re
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

import checkpoint_engine as core
import print_layout_assets

OUTPUT_SCHEMA_VERSION = 24


def _clean(v: Any) -> str:
    return str(v or "").strip()


def _safe_token(v: str, fallback: str = "item") -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", _clean(v)).strip("_")
    return s or fallback


def _sha(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def output_dir(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_output" / plan_id


def output_zip_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_output" / f"{plan_id}_SUMMATIVE.zip"


def assembly_manifest_path(github_root: Path, plan_id: str) -> Path:
    return output_dir(github_root, plan_id) / "assembly_manifest.json"


def load_assembly(github_root: Path, plan_id: str) -> dict[str, Any] | None:
    path = assembly_manifest_path(github_root, plan_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    state = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_state" / plan_id
    plan_path = state / "plan.json"
    response_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_families" / plan_id / "summative_families.json"
    review_path = state / "family_review.json"
    if data.get("plan_sha256") != _sha(plan_path):
        return None
    if data.get("family_response_sha256") != _sha(response_path):
        return None
    if data.get("family_review_sha256") != _sha(review_path):
        return None
    if int(data.get("output_schema_version", 0) or 0) != OUTPUT_SCHEMA_VERSION:
        return None
    return data


def _mathjax_head() -> str:
    # JS needs TWO literal backslashes in its source so the resulting delimiter
    # strings still contain one backslash at runtime. A normal Python string
    # collapsed this one level too early and left raw \(...\) visible.
    return r'''<script>window.MathJax={tex:{inlineMath:[["\\(","\\)"],["$","$"]],displayMath:[["\\[","\\]"],["$$","$$"]],processEscapes:true},options:{skipHtmlTags:["script","noscript","style","textarea","pre","code"]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'''

def _embedded_generators() -> str:
    app_dir = Path(__file__).resolve().parent
    out = []
    for name in ("assessment_builder_generation.js", "assessment_builder_generation_34.js"):
        p = app_dir / name
        if p.is_file():
            out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)


def _family_exemplar(family: dict[str, Any], key: str = "exemplar") -> dict[str, Any]:
    ex = family.get(key)
    return dict(ex) if isinstance(ex, dict) else {}


def _embed_summative_assets(github_root: Path, plan_id: str, markup: str, unit: int) -> str:
    """Embed temporary Summative assets first, then canonical Bank assets.

    New temporary graph families store graph-tool output under
    summative_families/<plan_id>/figures/. Legacy Bank-relative assets still
    resolve through the existing Bank embedder.
    """
    if not markup or "src=" not in markup:
        return markup
    family_root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_families" / plan_id
    pattern = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.I)

    def repl(match: re.Match[str]) -> str:
        src = match.group(2).strip()
        if not src or src.startswith(("data:", "http://", "https://")):
            return match.group(0)
        rel = src.lstrip("./")
        asset = family_root / rel
        try:
            asset.resolve().relative_to(family_root.resolve())
        except ValueError:
            return match.group(0)
        if not asset.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
        data = base64.b64encode(asset.read_bytes()).decode("ascii")
        return f"{match.group(1)}data:{mime};base64,{data}{match.group(3)}"

    converted = pattern.sub(repl, markup)
    return core._embed_bank_assets(github_root, converted, unit)


def _parse_choices(markup: str, answer: str) -> tuple[str, list[str], int]:
    m = re.search(r'(<ol\b[^>]*class=["\'][^"\']*\bchoices\b[^"\']*["\'][^>]*>)(.*?)(</ol>)', markup or "", re.I | re.S)
    if not m:
        raise ValueError("MC family exemplar is missing <ol class=\"choices\">.")
    choices = re.findall(r'<li\b[^>]*>(.*?)</li>', m.group(2), re.I | re.S)
    if len(choices) != 4:
        raise ValueError("MC family exemplar must contain exactly four choices.")
    am = re.match(r'^\s*([A-D])\s*[.):-]', answer or "", re.I)
    if not am:
        raise ValueError("MC family answer must begin with A-D.")
    correct = ord(am.group(1).upper()) - 65
    prompt = (markup[:m.start()] + markup[m.end():]).strip()
    return prompt, choices, correct


def _mc_versions(plan: dict[str, Any], families: list[dict[str, Any]], github_root: Path) -> list[dict[str, Any]]:
    if not families:
        raise ValueError("No accepted MC families are available.")
    if len(families) > 16:
        raise ValueError("A Summative MC set may contain at most 16 questions. Narrow the selected I Can scope.")

    def prepare(family: dict[str, Any], ex: dict[str, Any]) -> dict[str, Any]:
        prompt, choices, correct = _parse_choices(_clean(ex.get("student_html")), _clean(ex.get("answer")))
        targets = [core.normalize_ican(x) for x in (family.get("target_i_can_ids") or [])]
        iid = next((x for x in targets if x), "")
        unit = core.ican_sort_key(iid)[0] if iid else int(plan.get("storage_unit", 1) or 1)
        prompt = _embed_summative_assets(github_root, _clean(plan.get("plan_id")), prompt, unit)
        choices = [_embed_summative_assets(github_root, _clean(plan.get("plan_id")), c, unit) for c in choices]
        return {
            "family_id": _clean(family.get("family_id")),
            "family_name": _clean(family.get("family_name")),
            "i_can_id": iid,
            "prompt": prompt,
            "choices": choices,
            "correct": correct,
            "solution": _clean(ex.get("solution")),
        }

    base: list[dict[str, Any]] = []
    makeup_a: list[dict[str, Any]] = []
    makeup_b: list[dict[str, Any]] = []
    for family in families:
        base.append(prepare(family, _family_exemplar(family)))
        makeups = family.get("makeup_exemplars")
        if not isinstance(makeups, list) or len(makeups) < 2:
            raise ValueError(f"{_clean(family.get('family_id'))} is missing its two parallel number-swap makeup exemplars for Forms 5 and 6.")
        if not isinstance(makeups[0], dict) or not isinstance(makeups[1], dict):
            raise ValueError(f"{_clean(family.get('family_id'))} has invalid makeup exemplars.")
        makeup_a.append(prepare(family, makeups[0]))
        makeup_b.append(prepare(family, makeups[1]))

    versions = []
    base_seed = _clean(plan.get("plan_id"))
    for version in range(1, 7):
        # Forms 1-4 are the exact same test-day question instances, with only
        # question order and choice order scrambled. Forms 5-6 use the two
        # accepted parallel number-swap instances, then scramble those.
        prepared = base if version <= 4 else (makeup_a if version == 5 else makeup_b)
        rng = random.Random(hashlib.sha256(f"{base_seed}|MC|V{version}".encode()).hexdigest())
        order = list(range(len(prepared)))
        rng.shuffle(order)
        questions = []
        for qno, idx in enumerate(order, 1):
            src = prepared[idx]
            choice_order = list(range(4))
            rng.shuffle(choice_order)
            choices = [src["choices"][i] for i in choice_order]
            correct_index = choice_order.index(src["correct"])
            questions.append({
                "number": qno,
                "family_id": src["family_id"],
                "family_name": src["family_name"],
                "i_can_id": src["i_can_id"],
                "prompt": src["prompt"],
                "choices": choices,
                "answer_letter": "ABCD"[correct_index],
                "answer_text": re.sub(r"<[^>]+>", "", choices[correct_index]).strip(),
                "solution": src["solution"],
                "version_role": "test_day" if version <= 4 else "makeup_parallel",
            })
        versions.append({"version": version, "role": "test_day" if version <= 4 else "makeup_parallel", "questions": questions})
    return versions

def _title(plan: dict[str, Any]) -> str:
    custom = _clean(plan.get("custom_name"))
    item = _clean(plan.get("item_label"))
    if custom:
        return f"{item} {custom}".strip()
    if item.lower().startswith("summative"):
        return item
    return f"Summative {item}".strip()


def _shared_question_layout_css() -> str:
    # Canonical question/figure/workspace sizing is owned by print_layout_controller.css.
    return ""


def _mc_css() -> str:
    return r'''
@page{size:letter;margin:0}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#eef1f5;color:#111}.mc-stage{padding:16px;margin-left:310px}.mc-page{width:8.5in;height:11in;min-height:11in;margin:16px auto;background:#fff;padding:.42in .48in;overflow:hidden;position:relative;display:flex;flex-direction:column;break-after:page;page-break-after:always;box-shadow:0 2px 8px rgba(0,0,0,.16)}.exam-header{border-bottom:4px solid #00003d;padding-bottom:10px;margin-bottom:12px}.exam-header.continued{padding-bottom:7px;margin-bottom:9px}.exam-header.continued .directions{display:none}.title-row{display:flex;justify-content:space-between;align-items:flex-end;gap:16px}.title{font-size:19.5pt;font-weight:900;color:#00003d}.form-pill{border:2px solid #00003d;border-radius:999px;padding:4px 12px;font-weight:900;color:#00003d}.role{font-size:7.5pt;font-weight:900;letter-spacing:.06em;color:#667085;text-transform:uppercase;margin-top:2px;text-align:right}.directions{font-size:9.5pt;margin:8px 0 0}.mc-grid{display:block!important;columns:auto!important;column-count:1!important;flex:1 1 auto;min-height:0;overflow:hidden}.mc-flow{display:block!important;width:100%!important;min-width:0;height:100%!important;overflow:hidden;columns:auto!important;column-count:1!important}.mc-page.blank-back{display:block}.mc-question{display:block!important;width:100%!important;max-width:100%!important;float:none!important;clear:both!important;break-inside:avoid;border:1px solid #d7dce2;border-top:3px solid #00003d;border-radius:7px;padding:8px 10px;margin:0 0 10px;font-size:9.7pt;line-height:1.25;background:#fff}.mc-question .num{font-weight:900;color:#00003d;margin-right:4px}.mc-question p{display:inline;margin:0}.mc-question ol{margin:5px 0 0 22px;padding-left:15px}.mc-question li{margin:2px 0}.mc-page-number{position:absolute;right:.24in;bottom:.16in;font-size:7pt;color:#8a94a3;font-weight:700}.mc-controls{position:fixed;left:0;top:0;bottom:0;width:310px;background:#fff;border-right:1px solid #cdd6e2;padding:15px 12px;overflow:auto;z-index:20}.mc-controls h1{font-size:1.05rem;margin:0 0 6px;color:#173f73}.mc-controls h2{font-size:.82rem;margin:0 0 7px;color:#173f73}.mc-controls p{font-size:.73rem;line-height:1.35;color:#5d6a7d}.mc-controls label{display:block;font-size:.7rem;font-weight:800;color:#4e5d70;margin:11px 0 4px}.mc-controls select,.mc-controls button{width:100%;padding:7px 8px;border:1px solid #b9c5d6;border-radius:8px;background:#fff;font:inherit}.mc-controls button{font-weight:800;color:#173f73;cursor:pointer}.mc-controls .primary{background:#173f73;color:#fff;border-color:#173f73;margin-top:8px}.control-section{border-top:1px solid #e1e6ed;margin-top:12px;padding-top:11px}.qcontrol{border-top:1px solid #e1e6ed;padding:8px 0}.qcontrol-head{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:4px}.qcontrol-head strong{display:block;font-size:.68rem;margin:0;line-height:1.25}.qcontrol-order{display:flex;gap:4px;flex:0 0 auto}.qcontrol-order button{width:30px!important;height:30px;padding:0!important;border-radius:7px!important;font-size:16px!important;line-height:1!important}.fit{font-size:.66rem;line-height:1.35;border-radius:7px;padding:6px 7px;margin-top:6px;background:#eef6ee;color:#2c6941}.fit.bad{background:#fff4df;color:#815d10;border:1px solid #edcf86}.approval-note{font-size:.65rem;line-height:1.35;color:#5d6a7d;margin-top:6px}.screen-hidden{display:none!important}@media print{.mc-controls{display:none!important}.mc-stage{margin-left:0;padding:0}.mc-page{margin:0;box-shadow:none}.screen-hidden{display:block!important}}
''' + _shared_question_layout_css()


def mc_booklet_document(plan: dict[str, Any], versions: list[dict[str, Any]], layout: dict[str, Any] | None = None, approval_enabled: bool = True) -> str:
    title = _title(plan)
    plan_id = _clean(plan.get("plan_id"))
    initial = {"whole": {"workspace": 11, "figure": 100}, "entities": {}, "questions": {}}
    if isinstance(layout, dict):
        if isinstance(layout.get("whole"), dict):
            initial["whole"].update(layout["whole"])
        elif isinstance(layout.get("packet"), dict):
            initial["whole"].update(layout["packet"])
        entities = layout.get("entities") or layout.get("versions") or {}
        if isinstance(entities, dict):
            initial["entities"].update(entities)
        if isinstance(layout.get("questions"), dict):
            initial["questions"].update(layout["questions"])

    pages: list[str] = []
    qmeta: dict[str, list[dict[str, Any]]] = {}
    for v in versions:
        version = int(v["version"])
        qs = []
        metas = []
        for q in v["questions"]:
            lis = ''.join(f'<li>{c}</li>' for c in q['choices'])
            has_figure = bool(re.search(r'<(?:img|svg|canvas)\b|class=["\'][^"\']*(?:graph|visual|figure)', q['prompt'] + ''.join(q['choices']), re.I))
            qs.append(
                f'<article class="mc-question plc-question" data-qno="{q["number"]}" data-family-id="{html.escape(q["family_id"], quote=True)}">'
                f'<div class="plc-question-content"><span class="num">{q["number"]}.</span>{q["prompt"]}<ol type="A">{lis}</ol></div>'
                f'<div class="plc-figure"></div><div class="plc-workspace"></div></article>'
            )
            metas.append({"number": q["number"], "family_id": q["family_id"], "family_name": q["family_name"], "has_figure": has_figure})
        qmeta[str(version)] = metas
        role = "Test Day · scrambled common questions" if version <= 4 else "Makeup · parallel number-swap questions"
        pages.append(
            f'<section class="mc-page" data-version="{version}" data-page="1"><header class="exam-header"><div class="title-row">'
            f'<div class="title">{html.escape(title)}</div><div><div class="form-pill">FORM {version}</div><div class="role">{html.escape(role)}</div></div>'
            f'</div><div class="directions">Use the separate personalized answer sheet. Do not write on this booklet.</div></header>'
            f'<main class="mc-grid"><div class="mc-flow">{"".join(qs)}</div></main>'
            f'<div class="mc-page-number">Form {version} · Page 1</div></section>'
        )

    approve_html = (
        '<div class="control-section"><h2>Approve for Future Use</h2>'
        '<p class="approval-note">Approval saves these six forms plus the current spacing/figure layout as the reusable MC set.</p>'
        '<button id="mcApprove" class="primary">Approve MC Set for Future Use</button><div id="mcApproveStatus" class="fit" hidden></div></div>'
        if approval_enabled else
        '<div class="control-section"><h2>Approved MC Set</h2><p class="approval-note">These controls start from the approved saved layout. Temporary print adjustments do not change the approved set.</p></div>'
    )
    options = ''.join(f'<option value="{i}">Form {i}{" · Test Day" if i <= 4 else " · Makeup"}</option>' for i in range(1, 7))
    controls = (
        '<aside class="mc-controls"><h1>MC Booklet Controls</h1>'
        '<p>Forms 1–4 are Test Day scrambles of the same questions. Forms 5–6 are scrambled parallel number-swap makeups.</p>'
        '<label>Version</label><select id="mcVersionSelect"><option value="">Show All Versions</option>' + options + '</select>'
        '<button id="mcShowAll">Show All Versions</button><button id="mcPrintAll" class="primary">Print All 6 Forms</button>'
        '<div id="mcFit" class="fit"></div>'
        '<div class="control-section"><h2>Preview</h2><div id="mcViewControls"></div></div>'
        '<div class="control-section"><div id="mcLayoutControls"></div></div>'
        '<div id="mcQuestionControls" class="control-section"><h2>Individual Questions</h2><div id="mcQuestionList"><p class="approval-note">Choose a form above to adjust individual MC questions.</p></div></div>'
        + approve_html + '</aside>'
    )

    approval_js = ""
    if approval_enabled:
        approval_js = r'''
async function approve(){
  checkFit();
  const box=document.getElementById('mcApproveStatus');
  if(box){box.hidden=false;box.className='fit';box.textContent='Opening Save dialog for the approved MC-set transfer…'}
  try{
    const r=await fetch('/api/summative/approve-mc-set',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:PLAN,layout:{...plc.exportState(),fit_ok:true}})}),d=await r.json().catch(()=>({}));
    if(!r.ok||!d.ok)throw new Error(d.error||`Approval failed (${r.status})`);
    if(d.cancelled){if(box){box.className='fit bad';box.textContent='Approval transfer was not saved.'}return}
    if(box){box.className='fit';box.textContent=`Saved ${d.name}.`}
  }catch(e){if(box){box.className='fit bad';box.textContent=e.message}}
}
document.getElementById('mcApprove').onclick=approve;
'''
    script = r'''<script>(function(){
const PLAN=__PLAN__,initial=__INITIAL__,meta=__META__,sel=document.getElementById('mcVersionSelect'),fit=document.getElementById('mcFit'),list=document.getElementById('mcQuestionList'),stage=document.querySelector('.mc-stage');
let plc,reflowQueued=false,reflowing=false;
function pageNodes(){return [...document.querySelectorAll('.mc-page')]}
function status(msg){fit.className='fit';fit.textContent=msg}
function checkFit(){const counts=new Map();for(let i=1;i<=6;i++)counts.set(String(i),pageNodes().filter(p=>p.dataset.version===String(i)).length);if(sel.value){const n=counts.get(String(sel.value))||0,blank=pageNodes().some(p=>p.dataset.version===String(sel.value)&&p.dataset.blankBack==='1');status(`Form ${sel.value} uses ${n} printed pages${blank?' (blank back added for duplex).':'.'}`)}else{const total=[...counts.values()].reduce((a,b)=>a+b,0),bad=[...counts.entries()].filter(([,n])=>n%2!==0);status(bad.length?`Duplex page check failed for Form ${bad.map(([v])=>v).join(', ')}.`:`All 6 forms use ${total} printed pages total; every form uses an even page count.`)}return counts}
function applyVisibility(){const v=sel.value;pageNodes().forEach(p=>p.classList.toggle('screen-hidden',Boolean(v)&&p.dataset.version!==String(v)))}
function makePage(version,ctx,pageNo){const page=document.createElement('section');page.className='mc-page';page.dataset.version=String(version);page.dataset.page=String(pageNo);const header=ctx.header.cloneNode(true);if(pageNo>1){header.classList.add('continued');const role=header.querySelector('.role');if(role)role.textContent=`FORM ${version} · continued`}page.appendChild(header);const grid=document.createElement('main');grid.className='mc-grid';const flow=document.createElement('div');flow.className='mc-flow';grid.appendChild(flow);page.appendChild(grid);const footer=document.createElement('div');footer.className='mc-page-number';footer.textContent=`Form ${version} · Page ${pageNo}`;page.appendChild(footer);return page}
function makeBlankBack(version,_ctx,pageNo){const page=document.createElement('section');page.className='mc-page blank-back';page.dataset.version=String(version);page.dataset.page=String(pageNo);page.dataset.blankBack='1';return page}
function paginateAll(){if(reflowing||!stage||!plc)return;reflowing=true;try{plc.reflowDynamicAll({ensureEven:true});for(let i=1;i<=6;i++)relabelMc(String(i),plc.orderedIds(String(i)));applyVisibility();plc.refreshView();checkFit()}finally{reflowing=false}}
function queueReflow(){if(reflowQueued)return;reflowQueued=true;requestAnimationFrame(()=>{reflowQueued=false;paginateAll()})}
function relabelMc(v,ids){const pages=pageNodes().filter(p=>p.dataset.version===String(v)&&p.dataset.blankBack!=='1');(ids||[]).forEach((id,pos)=>{for(const page of pages){const q=[...page.querySelectorAll('.mc-question[data-qno]')].find(el=>String(el.dataset.qno||'')===String(id));if(!q)continue;const num=q.querySelector('.num');if(num)num.textContent=(pos+1)+'.';break}})}
function renderQuestions(){const v=sel.value;if(!v){list.innerHTML='<p class="approval-note">Choose a form above to adjust individual MC questions.</p>';return}const byId=new Map((meta[v]||[]).map(q=>[String(q.number),q])),ids=plc?plc.orderedIds(v):(meta[v]||[]).map(q=>String(q.number)),ordered=ids.map(id=>byId.get(String(id))).filter(Boolean);list.innerHTML=ordered.map((q,pos)=>`<div class="qcontrol" data-q="${q.number}"><div class="qcontrol-head"><strong>Question ${pos+1} · ${q.family_name}</strong><div class="qcontrol-order"><button type="button" data-up aria-label="Move question up" title="Move question up" ${pos===0?'disabled':''}>↑</button><button type="button" data-down aria-label="Move question down" title="Move question down" ${pos===ordered.length-1?'disabled':''}>↓</button></div></div><div data-q-layout></div></div>`).join('');list.querySelectorAll('.qcontrol').forEach(box=>{const n=box.dataset.q;const keys=plc.questionHasFigure(v,n)?['workspace','figure']:['workspace'],mount=box.querySelector('[data-q-layout]');plc.mountQuestionControls(mount,v,n,keys,{reorder:false});mount.querySelector('.plc-reset')?.remove();box.querySelector('[data-up]').onclick=()=>plc.moveQuestion(v,n,-1);box.querySelector('[data-down]').onclick=()=>plc.moveQuestion(v,n,1)});relabelMc(v,ids)}
function show(v){applyVisibility();plc.setSelectedEntity();renderQuestions();plc.refreshView();setTimeout(checkFit,20)}
plc=new window.PrintLayoutController({
 fields:[{key:'workspace',label:'Workspace',min:0,max:1200,step:1,default:11,unit:'px'},{key:'figure',label:'Figure size',min:0,max:300,step:1,default:100,unit:'%'}],
 storageKey:'shared-print-layout-summative-mc-v3:'+PLAN,initialState:initial,initialStateAuthoritative:__AUTHORITATIVE__,entitySelect:sel,mainMount:'#mcLayoutControls',viewMount:'#mcViewControls',stage:'.mc-stage',pageSelector:'.mc-page',pageBodySelector:'.mc-flow',entityAttr:'version',questionSelector:'.mc-question[data-qno]',questionAttr:'qno',pagesPerEntity:2,sidebarWidth:310,hiddenClass:'screen-hidden',figureBasePx:320,figureSelector:'.plc-figure:not(:empty)',scopeOwnsDescendants:true,wholeLayoutTitle:'Whole Booklet Layout',entityLayoutTitle:'Selected Form Layout',wholeResetLabel:'Reset Booklet Layout',entityResetLabel:'Use Whole Booklet Layout',pageLabel:p=>`Form ${p.dataset.version} · Page ${p.dataset.page||'?'}`,captureContext:(v,page)=>({header:page.querySelector('.exam-header').cloneNode(true)}),makePage:makePage,makeBlankPage:makeBlankBack,onChange:(_s,ctx)=>{if(ctx?.commit&&ctx?.level!=='question')renderQuestions()},onCommit:()=>queueReflow(),onReorder:(v,ids)=>{const qs=new Map(pageNodes().filter(p=>p.dataset.version===String(v)).flatMap(p=>[...p.querySelectorAll('.mc-question[data-qno]')]).map(q=>[String(q.dataset.qno),q]));const first=pageNodes().find(p=>p.dataset.version===String(v)&&p.dataset.blankBack!=='1');if(first){const flow=first.querySelector('.mc-flow');ids.forEach(id=>{const q=qs.get(String(id));if(q)flow.appendChild(q)});relabelMc(v,ids);queueReflow()}renderQuestions()}
});
sel.onchange=()=>show(sel.value);document.getElementById('mcShowAll').onclick=()=>{sel.value='';show('')};document.getElementById('mcPrintAll').onclick=()=>{sel.value='';show('');paginateAll();setTimeout(()=>window.print(),120)};
__APPROVAL__
show('');queueReflow();window.addEventListener('load',()=>setTimeout(()=>{const done=()=>{queueReflow();setTimeout(checkFit,40)};if(window.MathJax?.typesetPromise)window.MathJax.typesetPromise().then(done).catch(done);else done()},180));
})();</script>'''
    script = script.replace('__PLAN__', json.dumps(plan_id)).replace('__INITIAL__', json.dumps(initial, separators=(',', ':'))).replace('__META__', json.dumps(qmeta, separators=(',', ':'))).replace('__AUTHORITATIVE__', 'true' if not approval_enabled else 'false').replace('__APPROVAL__', approval_js)
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} - MC Forms 1-6</title><style>{_mc_css()}</style>{print_layout_assets.inline_assets()}{_mathjax_head()}</head><body>{controls}<main class="mc-stage">{"".join(pages)}</main>{script}</body></html>'


def mc_key_document(plan: dict[str, Any], versions: list[dict[str, Any]]) -> str:
    title=_title(plan)
    plan_id=_clean(plan.get('plan_id'))
    blocks=[]
    for v in versions:
        rows=''.join(f'<tr data-q="{q["number"]}"><td class="key-number">{q["number"]}</td><td>{html.escape(q["answer_letter"])}</td><td>{html.escape(q["i_can_id"])}</td><td>{html.escape(q["family_name"])}</td></tr>' for q in v['questions'])
        blocks.append(f'<section class="key" data-version="{v["version"]}"><h2>Form {v["version"]}</h2><table><thead><tr><th>#</th><th>Answer</th><th>I Can</th><th>Family</th></tr></thead><tbody>{rows}</tbody></table></section>')
    css='body{font-family:Arial;margin:24px;color:#182230}h1,h2{color:#173f73}.key{break-after:page;margin-bottom:24px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:6px 8px;text-align:left}th{background:#eef2f7}'
    storage_key=json.dumps('shared-print-layout-summative-mc-v3:'+plan_id)
    script=f'''<script>(function(){{try{{const state=JSON.parse(localStorage.getItem({storage_key})||'null')||{{}},orders=state.order||{{}};document.querySelectorAll('.key[data-version]').forEach(sec=>{{const v=String(sec.dataset.version||''),body=sec.querySelector('tbody'),rows=[...body.querySelectorAll('tr[data-q]')],map=new Map(rows.map(r=>[String(r.dataset.q),r])),saved=Array.isArray(orders[v])?orders[v].map(String):[],ids=saved.filter(id=>map.has(id));rows.forEach(r=>{{const id=String(r.dataset.q);if(!ids.includes(id))ids.push(id)}});ids.forEach((id,pos)=>{{const row=map.get(id);if(!row)return;const n=row.querySelector('.key-number');if(n)n.textContent=String(pos+1);body.appendChild(row)}})}})}}catch(_e){{}}}})();</script>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)} - MC Key</title><style>{css}</style></head><body><h1>{html.escape(title)} · MC Answer Key</h1>{"".join(blocks)}{script}</body></html>'


def _frq_source_questions(github_root: Path, plan: dict[str, Any], families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    banks=core.load_all_banks(github_root)
    by_id={_clean(f.get('family_id')):f for f in banks.get('families',[])}
    ext_by_iid={}
    for f in families:
        if _clean(f.get('slot_kind'))=='extension_mc':
            targets=[core.normalize_ican(x) for x in (f.get('target_i_can_ids') or [])]
            if targets and targets[0]: ext_by_iid[targets[0]]=f
    forms=[]
    for s in plan.get('students',[]):
        qs=[]
        for slot in sorted(s.get('reassessment_slots') or [], key=lambda x:int(x.get('slot',999) or 999)):
            fid=_clean(slot.get('source_family_id'))
            family=by_id.get(fid)
            if not family: raise ValueError(f"Approved source family {fid} is no longer available for {_clean(s.get('student_display'))}.")
            ex=_family_exemplar(family)
            iid=core.normalize_ican(slot.get('i_can_id'))
            unit=core.ican_sort_key(iid)[0]
            markup=_embed_summative_assets(github_root,_clean(plan.get('plan_id')), _clean(ex.get('student_html')),unit)
            qs.append({'kind':'reassessment','label':f'FRQ {len(qs)+1}','i_can_id':iid,'family_id':fid,'family_name':_clean(family.get('family_name')),'student_html':markup,'exemplar':{**ex,'student_html':markup}})
        ext_count=int(s.get('extension_count',0) or 0)
        secure=list(s.get('secure_i_cans') or [])
        assigned_ext=[]
        for iid in secure:
            f=ext_by_iid.get(iid)
            if f and len(assigned_ext)<ext_count: assigned_ext.append((iid,f))
        if len(assigned_ext)<ext_count:
            raise ValueError(f"{_clean(s.get('student_display'))} needs {ext_count} extension FRQ slot(s), but the accepted extension families do not include enough FRQ extension targets.")
        for ext_index,(iid,family) in enumerate(assigned_ext,1):
            ex=_family_exemplar(family,'frq_exemplar')
            if not _clean(ex.get('student_html')):
                raise ValueError(f"Extension family {_clean(family.get('family_id'))} needs frq_exemplar before personalized Summative assembly.")
            unit=core.ican_sort_key(iid)[0]
            markup=_embed_summative_assets(github_root,_clean(plan.get('plan_id')), _clean(ex.get('student_html')),unit)
            qs.append({'kind':'extension','label':f'Extension {ext_index}','i_can_id':iid,'family_id':_clean(family.get('family_id')),'family_name':_clean(family.get('family_name')),'student_html':markup,'exemplar':{**ex,'student_html':markup}})
        target=int(plan.get('target_questions_per_student',4) or 4)
        if len(qs)!=target: raise ValueError(f"{_clean(s.get('student_display'))} assembled with {len(qs)} FRQs; expected {target}.")
        forms.append({'student_key':_clean(s.get('student_key')),'student_display':_clean(s.get('student_display')),'questions':qs})
    return forms


def _answer_css() -> str:
    return r'''
@page{size:letter;margin:0}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#eef1f5;color:#111}.answer-stage{padding:16px;margin-left:310px}.sum-page{width:8.5in;height:11in;min-height:11in;margin:16px auto;background:#fff;padding:.42in .48in;overflow:hidden;display:flex;flex-direction:column;break-after:page;page-break-after:always;box-shadow:0 2px 8px rgba(0,0,0,.16)}.exam-header{border-bottom:4px solid #00003d;padding-bottom:9px;margin-bottom:9px}.title-row{display:flex;justify-content:space-between;align-items:flex-end;gap:16px}.exam-title{font-size:19pt;font-weight:900;color:#00003d}.sheet-pill{border:2px solid #00003d;border-radius:999px;padding:4px 10px;font-size:9.5pt;font-weight:900;color:#00003d}.student-row{display:grid;grid-template-columns:1.6fr .7fr;gap:16px;margin-top:9px;font-size:10pt;font-weight:700}.student-row .name{border-bottom:1px solid #444;padding-bottom:2px}.meta-row{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:7px;font-size:8.6pt}.form-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:800}.version-box{display:flex;gap:5px;align-items:center}.version-bubble,.choice-bubble{display:inline-grid;place-items:center;border:1.5px solid #111;border-radius:50%;width:.19in;height:.19in;font-size:7pt;line-height:1}.mc-answer-wrap{border:1px solid #c9d1db;border-radius:8px;padding:7px 9px;margin:8px 0 9px}.mc-answer-head{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:5px;color:#00003d;font-size:8.8pt;font-weight:900}.bubble-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px 10px}.bubble-block{border-left:1px solid #e1e5ea;padding-left:7px}.bubble-block:first-child{border-left:0}.answer-row{display:grid;grid-template-columns:18px repeat(4,1fr);align-items:center;gap:3px;height:.25in;font-size:7.8pt}.answer-row .qno{font-weight:900}.answer-row.unused{opacity:.28}.bubble-choice{display:flex;align-items:center;gap:2px}.frq{border:1px solid #d7dce2;border-top:3px solid #00003d;border-radius:7px;padding:8px 10px;margin:7px 0;break-inside:avoid;overflow:hidden}.frq-head{display:flex;align-items:center;gap:7px;margin-bottom:4px}.frq-label{display:inline-block;background:#00003d;color:#fff;border-radius:999px;padding:3px 8px;font-size:8.2pt;font-weight:900}.frq-label.extension{background:#9b6b00}.frq-meta{font-size:7.4pt;color:#667085;font-weight:700}.frq-prompt{font-size:10.3pt;line-height:1.28}.frq-prompt p{margin:4px 0}.continuation{display:flex;justify-content:space-between;border-bottom:2px solid #00003d;padding-bottom:6px;margin-bottom:8px;color:#00003d;font-size:9pt;font-weight:900}.sum-page>.plc-page-body{flex:1 1 auto;min-height:0;overflow:hidden}.sum-controls{position:fixed;left:0;top:0;bottom:0;width:310px;background:#fff;border-right:1px solid #cdd6e2;padding:15px 12px;overflow:auto;z-index:30}.sum-controls h1{font-size:1.05rem;margin:0 0 5px;color:#173f73}.sum-controls h2{font-size:.82rem;margin:0 0 7px;color:#173f73}.sum-controls p{font-size:.73rem;line-height:1.35;color:#5d6a7d}.sum-controls label{display:block;font-size:.7rem;font-weight:800;color:#4e5d70;margin:11px 0 4px}.sum-controls select,.sum-controls button{width:100%;font:inherit;border:1px solid #b9c5d6;border-radius:8px;background:#fff;padding:7px 8px}.sum-controls button{font-weight:800;color:#173f73;cursor:pointer}.sum-controls .primary{background:#173f73;color:#fff;border-color:#173f73;margin-top:8px}.control-section{border-top:1px solid #e1e6ed;margin-top:12px;padding-top:11px}.slot{border-top:1px solid #e1e6ed;padding:9px 0}.slot-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:4px}.slot-head strong{display:block;font-size:.7rem;margin:0}.slot-order{display:flex;gap:4px;flex:0 0 auto}.slot-order button{width:30px!important;height:28px!important;padding:0!important;margin:0!important;border:1px solid #c3ced9!important;border-radius:6px!important;background:#fff!important;color:#173f73!important;font-size:.95rem!important;font-weight:900!important;line-height:1!important}.slot-order button:disabled{opacity:.38!important;cursor:not-allowed!important}.slot small{display:block;font-size:.62rem;color:#6b7788;margin:3px 0}.slot button{padding:5px 7px;font-size:.66rem;margin-top:4px}.fit{font-size:.66rem;line-height:1.35;border-radius:7px;padding:6px 7px;margin-top:6px;background:#eef6ee;color:#2c6941}.fit.bad{background:#fff4df;color:#815d10;border:1px solid #edcf86}.sum-page.overfull{outline:3px solid #d69b27;outline-offset:-3px}.screen-hidden{display:none!important}@media print{.sum-controls{display:none!important}.answer-stage{margin-left:0;padding:0}.sum-page{margin:0;box-shadow:none}.screen-hidden{display:block!important}}
''' + _shared_question_layout_css()

def _bubble_grid(mc_count: int) -> str:
    blocks=[]
    for b in range(4):
        rows=[]
        for offset in range(4):
            n=b*4+offset+1
            unused=n>mc_count
            choices=''.join(f'<span class="bubble-choice"><span class="choice-bubble"></span>{letter}</span>' for letter in 'ABCD')
            rows.append(f'<div class="answer-row{" unused" if unused else ""}"><span class="qno">{n}</span>{choices}</div>')
        blocks.append(f'<div class="bubble-block">{"".join(rows)}</div>')
    return ''.join(blocks)


def _frq_html(q: dict[str, Any], idx: int) -> str:
    cls='frq-label extension' if q.get('kind')=='extension' else 'frq-label'
    return f'<section class="frq plc-question" data-slot-index="{idx}"><div class="frq-head"><span class="{cls}">{html.escape(_clean(q.get("label")) or f"FRQ {idx}")}</span><span class="frq-meta">{html.escape(_clean(q.get("i_can_id")))}</span></div><div class="frq-prompt plc-question-content">{q.get("student_html") or ""}</div><div class="plc-figure"></div><div class="frq-workspace plc-workspace"></div></section>'


def _control_data(github_root: Path, plan: dict[str, Any], forms: list[dict[str, Any]], families: list[dict[str, Any]]) -> dict[str, Any]:
    banks=core.load_all_banks(github_root)
    by_ican={}
    for f in banks.get('families',[]): by_ican.setdefault(_clean(f.get('i_can_id')),[]).append(f)
    for iid in by_ican: by_ican[iid].sort(key=lambda f:(_clean(f.get('family_label')),_clean(f.get('family_id'))))
    ext_options=[]
    for f in families:
        if _clean(f.get('slot_kind'))=='extension_mc' and _clean((_family_exemplar(f,'frq_exemplar')).get('student_html')):
            ext_options.append({'family_id':_clean(f.get('family_id')),'family_name':_clean(f.get('family_name')),'kind':'extension','target_i_can_ids':[core.normalize_ican(x) for x in (f.get('target_i_can_ids') or []) if core.normalize_ican(x)],'exemplar':_family_exemplar(f,'frq_exemplar')})
    students=[]
    for form in forms:
        slots=[]
        for idx,q in enumerate(form.get('questions',[]),1):
            if q.get('kind')=='extension': opts=[x for x in ext_options if _clean(q.get('i_can_id')) in x.get('target_i_can_ids',[])]
            else:
                opts=[]
                for f in by_ican.get(_clean(q.get('i_can_id')),[]):
                    opts.append({'family_id':_clean(f.get('family_id')),'family_label':_clean(f.get('family_label')),'teacher_question_id':_clean(f.get('teacher_question_id')),'family_name':_clean(f.get('family_name')),'kind':'reassessment','target_i_can_ids':[_clean(f.get('i_can_id'))],'exemplar':_family_exemplar(f)})
            slots.append({'slot_index':idx,'kind':q.get('kind'),'label':q.get('label'),'i_can_id':q.get('i_can_id'),'selected_family_id':q.get('family_id'),'selected_family_name':q.get('family_name'),'has_figure':bool(re.search(r'<(?:img|svg|canvas)\b|class=["\'][^"\']*(?:graph|visual|figure)',_clean(q.get('student_html')),re.I)),'options':opts})
        students.append({'student_key':form.get('student_key'),'student_display':form.get('student_display'),'slots':slots})
    return {'plan_id':plan.get('plan_id'),'students':students}


def answer_sheets_document(github_root: Path, plan: dict[str, Any], forms: list[dict[str, Any]], families: list[dict[str, Any]], mc_count: int) -> str:
    title=_title(plan)
    pages=[]
    plan_code=_safe_token(_clean(plan.get('item_label')) or 'SUM','SUM')[:12]
    for form in forms:
        sk=_clean(form.get('student_key')); name=_clean(form.get('student_display')); qs=form.get('questions',[])
        form_id=f"{plan_code}-{sk}"[:28]
        vrow=''.join(f'<span class="bubble-choice"><span class="version-bubble"></span>{i}</span>' for i in range(1,7))
        first=''.join(_frq_html(q,i+1) for i,q in enumerate(qs[:2]))
        second=''.join(_frq_html(q,i+3) for i,q in enumerate(qs[2:]))
        p1=f'<section class="sum-page" data-student-key="{html.escape(sk,quote=True)}" data-page="1"><header class="exam-header"><div class="title-row"><div class="exam-title">{html.escape(title)}</div><div class="sheet-pill">ANSWER + FRQ</div></div><div class="student-row"><div>Name: <span class="name">{html.escape(name)}</span></div><div>Date: __________________</div></div><div class="meta-row"><span class="form-id">Form ID: {html.escape(form_id)}</span><span class="version-box"><strong>MC Form</strong>{vrow}</span></div></header><main class="plc-page-body"><section class="mc-answer-wrap"><div class="mc-answer-head"><span>Multiple Choice Answers · Questions 1-{mc_count}</span><span>Fill one bubble per question.</span></div><div class="bubble-grid">{_bubble_grid(mc_count)}</div></section>{first}</main></section>'
        p2=f'<section class="sum-page" data-student-key="{html.escape(sk,quote=True)}" data-page="2"><div class="continuation"><span>{html.escape(title)} · continued</span><span>{html.escape(name)} · {html.escape(form_id)}</span></div><main class="plc-page-body">{second}</main></section>'
        pages.extend([p1,p2])
    controls='<aside class="sum-controls"><h1>Summative Controls</h1><p>Preview and adjust one student at a time. Print All always prints each personalized answer/FRQ sheet in two-page order for duplex printing.</p><label>Student</label><select id="sumStudentSelect"><option value="">All students</option>'+''.join(f'<option value="{html.escape(_clean(f.get("student_key")),quote=True)}">{html.escape(_clean(f.get("student_display")))}</option>' for f in forms)+'</select><button id="sumShowAll">Show All Students</button><button id="sumPrintAll" class="primary">Print All · Double-Sided</button><div id="sumStudentFit" class="fit"></div><section class="control-section"><h2>Preview</h2><div id="sumViewControls"></div></section><section class="control-section"><div id="sumLayoutControls"></div></section><div id="sumControlSlots"></div><div id="sumControlStatus" class="fit"></div></aside>'
    data=json.dumps(_control_data(github_root,plan,forms,families),ensure_ascii=False).replace('</','<\\/')
    script=f'''<script>window.SUMMATIVE_CONTROL_DATA={data};</script><script>{_embedded_generators()}</script><script>(function(){{
const data=window.SUMMATIVE_CONTROL_DATA||{{students:[]}},sel=document.getElementById('sumStudentSelect'),slots=document.getElementById('sumControlSlots'),status=document.getElementById('sumControlStatus'),fit=document.getElementById('sumStudentFit');
const byKey=new Map((data.students||[]).map(s=>[s.student_key,s]));let plc,overflow=new Map();
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const PAGE_BOTTOM_RESERVE=28;let settleToken=0;
function measureEntity(k){{const all=plc.measureOverflow(3);return all.get(String(k))||[]}}
function checkFit(){{const all=plc.measureOverflow(3);overflow=all;const k=sel.value;if(k){{const o=all.get(String(k))||[],name=byKey.get(k)?.student_display||k;fit.textContent=o.length?name+' would exceed 2 pages — page '+o.join(', ')+' is overfull.':name+' fits in 2 pages.';fit.className='fit'+(o.length?' bad':'')}}else{{const names=[...all.keys()].map(x=>byKey.get(x)?.student_display||x);fit.textContent=names.length?names.length+' students exceed 2 pages: '+names.slice(0,7).join(', ')+(names.length>7?' …':''):'All students fit in 2 pages.';fit.className='fit'+(names.length?' bad':'')}}return all}}
function relabelFrqs(k,ids){{const pages=[...document.querySelectorAll('.sum-page')].filter(p=>String(p.dataset.studentKey||'')===String(k));(ids||[]).forEach((id,pos)=>{{for(const page of pages){{const q=[...page.querySelectorAll('.frq[data-slot-index]')].find(el=>String(el.dataset.slotIndex||'')===String(id));if(!q)continue;const label=q.querySelector('.frq-label');if(label)label.textContent='FRQ '+(pos+1);break}}}})}}
function reflowStudent(k,ids){{plc.reflowFixedEntity(k,ids);relabelFrqs(k,ids)}}
function reflowNow(){{const k=sel.value;if(k)reflowStudent(k,plc.orderedIds(k));else(data.students||[]).forEach(s=>reflowStudent(s.student_key,plc.orderedIds(s.student_key)));checkFit()}}
function settleLayout(){{const token=++settleToken;fit.textContent='Checking layout…';fit.className='fit';const run=()=>{{if(token!==settleToken)return;reflowNow();plc?.refreshView?.()}};requestAnimationFrame(()=>requestAnimationFrame(run));setTimeout(run,120);setTimeout(run,360)}}
function renderSlots(){{const k=sel.value;if(!k){{slots.innerHTML='';return}}const s=byKey.get(k),ids=plc?plc.orderedIds(k):(s.slots||[]).map(x=>String(x.slot_index)),ordered=ids.map(i=>s.slots.find(x=>String(x.slot_index)===String(i))).filter(Boolean);slots.innerHTML='<section class="control-section"><h2>Individual FRQ Controls</h2></section>'+ordered.map((x,pos)=>{{const opts=(x.options||[]).map(o=>{{const prefix=o.kind==='reassessment'?[o.family_label?'Family '+o.family_label:'',o.teacher_question_id||''].filter(Boolean).join(' · '):'';const label=prefix?prefix+' · '+o.family_name:o.family_name;return '<option value="'+esc(o.family_id)+'" '+(o.family_id===x.selected_family_id?'selected':'')+'>'+esc(label)+'</option>'}}).join('');return '<div class="slot" data-slot="'+x.slot_index+'"><div class="slot-head"><strong>FRQ '+(pos+1)+' · '+esc(x.i_can_id)+'</strong><div class="slot-order"><button type="button" data-up aria-label="Move FRQ up" title="Move FRQ up" '+(pos===0?'disabled':'')+'>↑</button><button type="button" data-down aria-label="Move FRQ down" title="Move FRQ down" '+(pos===ordered.length-1?'disabled':'')+'>↓</button></div></div><select data-family>'+opts+'</select><small>'+esc(x.kind==='extension'?'Extension family':'Current Bank reassessment family')+'</small><div data-q-layout></div><button data-new>New instance</button></div>'}}).join('');bindSlots();relabelFrqs(k,ids)}}
function bindSlots(){{const k=sel.value,s=byKey.get(k);slots.querySelectorAll('[data-slot]').forEach(box=>{{const idx=Number(box.dataset.slot),slot=s.slots.find(x=>Number(x.slot_index)===idx),fam=box.querySelector('[data-family]'),mount=box.querySelector('[data-q-layout]');plc.mountQuestionControls(mount,k,idx,plc.questionHasFigure(k,idx)?['workspace','figure']:['workspace'],{{reorder:false}});mount.querySelector('.plc-reset')?.remove();box.querySelector('[data-up]').onclick=()=>plc.moveQuestion(k,idx,-1);box.querySelector('[data-down]').onclick=()=>plc.moveQuestion(k,idx,1);fam.onchange=async()=>{{const opt=(slot.options||[]).find(o=>o.family_id===fam.value);if(!opt)return;await saveQuestion(k,idx,opt,opt.exemplar)}};box.querySelector('[data-new]').onclick=async()=>{{const opt=(slot.options||[]).find(o=>o.family_id===fam.value);if(!opt)return;if(!window.AssessmentGeneration?.supports?.(opt.family_id)){{status.textContent='This family does not have an executable instance generator yet.';status.className='fit bad';return}}const inst=window.AssessmentGeneration.generate({{family_id:opt.family_id}});if(!inst)return;await saveQuestion(k,idx,opt,inst)}}}})}}
async function saveQuestion(k,idx,opt,inst){{status.textContent='Saving question change…';status.className='fit';try{{const r=await fetch('/api/summative/manual-adjust',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_id:data.plan_id,student_key:k,slot_index:idx,family_id:opt.family_id,instance:inst}})}}),d=await r.json();if(!r.ok||!d.ok)throw new Error(d.error||'Save failed');location.reload()}}catch(e){{status.textContent='Could not save: '+e.message;status.className='fit bad'}}}}
function showStudent(k){{document.querySelectorAll('.sum-page').forEach(p=>p.classList.toggle('screen-hidden',Boolean(k)&&p.dataset.studentKey!==k));if(k)reflowStudent(k,plc.orderedIds(k));plc.setSelectedEntity();renderSlots();settleLayout()}}
plc=new window.PrintLayoutController({{
 fields:[{{key:'workspace',label:'Workspace',min:0,max:1200,step:1,default:50,unit:'px'}},{{key:'figure',label:'Figure size',min:0,max:300,step:1,default:100,unit:'%'}}],
 storageKey:'shared-print-layout-summative-frq-v7:'+String(data.plan_id||'default'),initialState:{{whole:{{workspace:50,figure:100}},entities:{{}},questions:{{}},order:{{}}}},entitySelect:sel,mainMount:'#sumLayoutControls',viewMount:'#sumViewControls',stage:'.answer-stage',pageSelector:'.sum-page',pageBodySelector:'.plc-page-body',entityAttr:'studentKey',questionSelector:'.frq[data-slot-index]',questionAttr:'slotIndex',pagesPerEntity:2,sidebarWidth:310,hiddenClass:'screen-hidden',figureBasePx:320,scopeOwnsDescendants:true,figureSelector:'.plc-figure:not(:empty)',bottomReservePx:28,wholeLayoutTitle:'Whole Packet Layout',entityLayoutTitle:'Selected Student Layout',wholeResetLabel:'Reset Packet Layout',entityResetLabel:'Use Whole Packet Layout',pageLabel:p=>p.dataset.page||'?',onChange:(_state,ctx)=>{{if(ctx?.commit&&ctx?.level!=='question')renderSlots()}},onCommit:()=>settleLayout(),onReorder:(k,ids)=>{{reflowStudent(k,ids);renderSlots();settleLayout()}},onAfterApply:()=>{{}}
}});
sel.onchange=()=>showStudent(sel.value);document.getElementById('sumShowAll').onclick=()=>{{sel.value='';showStudent('')}};document.getElementById('sumPrintAll').onclick=()=>{{const prior=sel.value;sel.value='';showStudent('');setTimeout(()=>{{if(overflow.size&&!confirm(overflow.size+' student(s) exceed two pages. Print anyway?')){{sel.value=prior;showStudent(prior);return}}window.print()}},650)}};
document.querySelectorAll('.answer-stage img').forEach(img=>{{if(!img.complete)img.addEventListener('load',settleLayout,{{once:true}})}});
if(document.fonts?.ready)document.fonts.ready.then(settleLayout);
if(window.MathJax?.startup?.promise)window.MathJax.startup.promise.then(settleLayout).catch(()=>{{}});
const first=(data.students||[])[0];if(first){{sel.value=first.student_key;plc.setSelectedEntity();plc.apply(false,{{commit:false,source:'answer-init'}});showStudent(first.student_key)}}else showStudent('');
}})();</script>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} - Answer and FRQ Sheets</title><style>{_answer_css()}</style>{print_layout_assets.inline_assets()}{_mathjax_head()}</head><body>{controls}<main class="answer-stage">{"".join(pages)}</main>{script}</body></html>'

def frq_key_document(plan: dict[str, Any], forms: list[dict[str, Any]]) -> str:
    title=_title(plan); cards=[]
    for f in forms:
        qs=[]
        for q in f.get('questions',[]):
            ex=q.get('exemplar') if isinstance(q.get('exemplar'),dict) else {}
            qs.append(f'<section class="q"><h3>{html.escape(_clean(q.get("label")))} · {html.escape(_clean(q.get("i_can_id")))}</h3><p><strong>Family:</strong> {html.escape(_clean(q.get("family_name")))}</p><p><strong>Answer:</strong> {html.escape(_clean(ex.get("answer"))) or "—"}</p><p><strong>Solution:</strong> {html.escape(_clean(ex.get("solution")))}</p><p><strong>Scoring:</strong> {html.escape(_clean(ex.get("scoring_guidance")))}</p></section>')
        cards.append(f'<article class="student"><h2>{html.escape(_clean(f.get("student_display")))}</h2>{"".join(qs)}</article>')
    css='body{font-family:Arial;margin:24px;color:#182230}h1,h2,h3{color:#173f73}.student{break-after:page}.q{border-top:2px solid #173f73;padding:8px 0}.q p{margin:4px 0}'
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)} - FRQ Key</title><style>{css}</style></head><body><h1>{html.escape(title)} · Personalized FRQ Key</h1>{"".join(cards)}</body></html>'


def write_outputs(github_root: Path, plan: dict[str, Any], families: list[dict[str, Any]], forms: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    plan_id=_clean(plan.get('plan_id'));out=output_dir(github_root,plan_id)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    versions=_mc_versions(plan,families,github_root)
    forms=forms or _frq_source_questions(github_root,plan,families)
    (out/'mc_booklet.html').write_text(mc_booklet_document(plan,versions),encoding='utf-8')
    (out/'mc_key.html').write_text(mc_key_document(plan,versions),encoding='utf-8')
    (out/'answer_sheets.html').write_text(answer_sheets_document(github_root,plan,forms,families,len(families)),encoding='utf-8')
    (out/'frq_key.html').write_text(frq_key_document(plan,forms),encoding='utf-8')
    (out/'assembly_data.json').write_text(json.dumps({'schema_version':1,'plan_id':plan_id,'student_forms':forms,'mc_versions':versions},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    state=github_root/'_algebra_teacher_tools'/'assessment_builder'/'summative_state'/plan_id
    response=github_root/'_algebra_teacher_tools'/'assessment_builder'/'summative_families'/plan_id/'summative_families.json'
    review=state/'family_review.json'
    manifest={'schema_version':1,'output_schema_version':OUTPUT_SCHEMA_VERSION,'plan_id':plan_id,'built_at':time.strftime('%Y-%m-%d %H:%M:%S'),'title':_title(plan),'student_count':len(forms),'pages_per_student':2,'mc_question_count':len(families),'mc_version_count':6,'personalized_frq_count_per_student':int(plan.get('target_questions_per_student',4) or 4),'files':{'mc_booklet':'mc_booklet.html','mc_key':'mc_key.html','answer_sheets':'answer_sheets.html','frq_key':'frq_key.html'},'plan_sha256':_sha(state/'plan.json'),'family_response_sha256':_sha(response),'family_review_sha256':_sha(review)}
    zpath=output_zip_path(github_root,plan_id);manifest['output_zip_name']=zpath.name;manifest['output_folder']=str(out)
    (out/'assembly_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    zpath.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob('*')):
            if p.is_file(): zf.write(p,p.relative_to(out).as_posix())
    return manifest


def manual_adjust(github_root: Path, plan: dict[str, Any], families: list[dict[str, Any]], student_key: str, slot_index: int, family_id: str, instance: dict[str, Any]) -> dict[str, Any]:
    data_path=output_dir(github_root,_clean(plan.get('plan_id')))/'assembly_data.json'
    if not data_path.is_file(): raise ValueError('Assemble the Summative before making manual adjustments.')
    data=json.loads(data_path.read_text(encoding='utf-8'));forms=data.get('student_forms') or []
    form=next((f for f in forms if _clean(f.get('student_key'))==student_key),None)
    if not form: raise ValueError('Student form was not found.')
    qs=form.get('questions') or []
    if slot_index<1 or slot_index>len(qs): raise ValueError('Invalid FRQ slot.')
    current=qs[slot_index-1];iid=_clean(current.get('i_can_id'));kind=_clean(current.get('kind'))
    family=None;ex={}
    if kind=='extension':
        family=next((f for f in families if _clean(f.get('family_id'))==family_id and iid in [core.normalize_ican(x) for x in (f.get('target_i_can_ids') or [])]),None)
        if family: ex=_family_exemplar(family,'frq_exemplar')
    else:
        family=next((f for f in core.load_all_banks(github_root).get('families',[]) if _clean(f.get('family_id'))==family_id and _clean(f.get('i_can_id'))==iid),None)
        if family: ex=_family_exemplar(family)
    if not family: raise ValueError('That family is not allowed for this FRQ slot.')
    src=instance if isinstance(instance,dict) and _clean(instance.get('student_html')) else ex
    if not _clean(src.get('student_html')): raise ValueError('Question instance is missing student_html.')
    unit=core.ican_sort_key(iid)[0];markup=_embed_summative_assets(github_root,_clean(plan.get('plan_id')),_clean(src.get('student_html')),unit)
    current.update({'family_id':family_id,'family_name':_clean(family.get('family_name')),'student_html':markup,'exemplar':{**src,'student_html':markup}})
    return write_outputs(github_root,plan,families,forms)


def _update_library_index(raw: str, rel_dir: str, title: str, slug: str) -> str:
    marker=f'assessment-builder:summative-mc:{slug}';start=f'<!-- {marker}:START -->';end=f'<!-- {marker}:END -->'
    raw=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',raw,flags=re.S)
    block=(f'{start}<li class="builder-item"><strong>{html.escape(title)} · Reusable MC Set</strong> — '
           f'<a href="{rel_dir}/mc_booklet.html" target="_blank" rel="noopener">Forms 1–6</a> · '
           f'<a href="{rel_dir}/mc_key.html" target="_blank" rel="noopener">Key</a> · '
           f'<a href="{rel_dir}/mc_set.json" target="_blank" rel="noopener">Family Set</a></li>{end}')
    section=None
    for sid in ('summative-assessments','assessments'):
        m=re.search(rf'(<section\s+id="{sid}"[^>]*>)(.*?)(</section>)',raw,re.S)
        if m: section=(m,sid);break
    if not section: raise ValueError('Teacher Library Summative section was not found.')
    m,sid=section;head,body,tail=m.group(1),m.group(2),m.group(3)
    body=re.sub(r'<p\s+class="placeholder">.*?</p>','',body,flags=re.S)
    ul=re.search(r'<ul>(.*?)</ul>',body,re.S)
    if ul: body=body[:ul.start()]+'<ul>'+ul.group(1).rstrip()+block+'</ul>'+body[ul.end():]
    else: body=body.rstrip()+f'<ul>{block}</ul>'
    return raw[:m.start()]+head+body+tail+raw[m.end():]


def create_mc_library_transfer(github_root: Path, plan: dict[str, Any], families: list[dict[str, Any]], layout: dict[str, Any] | None = None) -> Path:
    assembly = load_assembly(github_root, _clean(plan.get('plan_id')))
    if not assembly:
        raise ValueError('Open the MC booklet before approving its reusable MC set.')
    layout = layout if isinstance(layout, dict) else {}
    if layout.get('fit_ok') is False:
        raise ValueError('Fix MC booklet page-fit warnings before approval.')
    out = output_dir(github_root, _clean(plan.get('plan_id')))
    teacher = github_root / 'teacher_shared'
    index = teacher / 'algebra' / 'library' / 'unit1' / 'index.html'
    if not index.is_file():
        raise ValueError(f'Teacher Library index not found: {index}')
    title = _title(plan)
    slug = _safe_token((_clean(plan.get('item_label')) + '_' + _clean(plan.get('custom_name'))).strip('_') or _clean(plan.get('plan_id')), 'summative').lower()
    rel_dir = Path('algebra/library/unit1/builder/summatives/mc_sets') / slug
    rel_link = f'builder/summatives/mc_sets/{slug}'
    new_index = _update_library_index(index.read_text(encoding='utf-8'), rel_link, title, slug)
    data = json.loads((out / 'assembly_data.json').read_text(encoding='utf-8'))
    versions = data.get('mc_versions', [])
    approved_booklet = mc_booklet_document(plan, versions, layout=layout, approval_enabled=False).encode()
    mc_set = {
        'schema_version': 2,
        'title': title,
        'unit': int(plan.get('storage_unit', 1) or 1),
        'source_plan_id': plan.get('plan_id'),
        'approved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'question_count': int(assembly.get('mc_question_count', 0) or 0),
        'version_count': 6,
        'version_policy': {
            'forms_1_4': 'test_day_same_question_instances_scrambled_order_and_choices',
            'forms_5_6': 'makeup_parallel_number_swap_instances_scrambled_order_and_choices',
        },
        'eligible_i_cans': plan.get('eligible_i_cans', []),
        'families': families,
        'versions': versions,
        'approved_layout': layout,
    }
    stamp = time.strftime('%Y%m%d_%H%M%S')
    package_id = f'assessment_builder_approve_summative_mc_{slug}_{stamp}'
    work = Path(tempfile.mkdtemp(prefix='summative-mc-transfer-'))
    try:
        files = []
        def add(rel: Path, content: bytes):
            payload = work / 'payload' / 'teacher_shared' / rel
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(content)
            target = teacher / rel
            entry = {'action': 'replace' if target.is_file() else 'create', 'root': 'teacher_shared', 'path': rel.as_posix(), 'source': ('payload/teacher_shared/' + rel.as_posix())}
            if target.is_file():
                entry['expected_existing_sha256'] = _sha(target)
            files.append(entry)
        add(rel_dir / 'mc_booklet.html', approved_booklet)
        add(rel_dir / 'mc_key.html', (out / 'mc_key.html').read_bytes())
        add(rel_dir / 'mc_set.json', (json.dumps(mc_set, indent=2, ensure_ascii=False) + '\n').encode())
        add(Path('algebra/library/unit1/index.html'), new_index.encode())
        manifest = {'package_type': 'curriculum_transfer', 'schema_version': 3, 'package_id': package_id, 'files': files}
        (work / 'TRANSFER_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        dest = output_dir(github_root, _clean(plan.get('plan_id'))) / f'{package_id}_GITHUB_TRANSFER.zip'
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
            for q in sorted(work.rglob('*')):
                if q.is_file():
                    zf.write(q, q.relative_to(work).as_posix())
        return dest
    finally:
        shutil.rmtree(work, ignore_errors=True)
