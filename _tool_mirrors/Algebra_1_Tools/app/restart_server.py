#!/usr/bin/env python3
from pathlib import Path
import json, os, signal, subprocess, sys, time, webbrowser
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.runtime'/'server.json'; LOG=ROOT/'.runtime'/'server.log'; SERVER=ROOT/'app'/'server.py'


def proc_cmd(pid):
    try: return subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=2).stdout.strip()
    except Exception: return ''


def _write_atomic(path, text):
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(text,encoding='utf-8')
    os.replace(tmp,path)


def repair_checkpoint_request_path():
    engine=ROOT/'assessments'/'assessment_builder'/'checkpoint_engine.py'
    if not engine.is_file(): return False
    try: raw=engine.read_text(encoding='utf-8')
    except Exception: return False
    if 'def request_path(github_root: Path, plan_id: str) -> Path:' in raw: return False
    marker='def create_extension_request_zip(github_root: Path, plan: dict[str, Any]) -> Path | None:\n'
    if marker not in raw: return False
    helper=(
        'def request_path(github_root: Path, plan_id: str) -> Path:\n'
        '    """Return the deterministic path for a Checkpoint AI-family request ZIP."""\n'
        '    root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_requests"\n'
        '    return root / f"{plan_id}_AI_FAMILY_REQUEST.zip"\n\n\n'
    )
    _write_atomic(engine,raw.replace(marker,helper+marker,1))
    return True


def install_ai_result_import():
    changed=False
    builder=ROOT/'assessments'/'assessment_builder'
    server=builder/'server.py'
    index=builder/'index.html'
    checkpoint=builder/'checkpoint_engine.py'
    summative=builder/'summative_engine.py'
    ui=builder/'assessment_builder.js'

    if server.is_file():
        raw=server.read_text(encoding='utf-8')
        if 'import result_import\n' not in raw:
            marker='import summative_output\n'
            if marker in raw:
                raw=raw.replace(marker,marker+'import result_import\n',1)
                changed=True

        if '/api/checkpoint/import-result' not in raw:
            marker="    def do_POST(self) -> None:\n        path = self.path.split(\"?\", 1)[0]\n"
            replacement="""    def do_POST(self) -> None:
        parsed_post = urlparse(self.path)
        path = parsed_post.path
        if path in {"/api/checkpoint/import-result", "/api/summative/import-result"}:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BODY:
                    raise ValueError("Result file is empty or too large.")
                plan_id = (parse_qs(parsed_post.query).get("plan_id") or [""])[0]
                if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                    raise ValueError("Invalid plan_id.")
                filename = self.headers.get("X-Result-Filename", "")
                try:
                    from urllib.parse import unquote
                    filename = unquote(filename)
                except Exception:
                    pass
                body = self.rfile.read(length)
                if path == "/api/checkpoint/import-result":
                    result = result_import.import_checkpoint_result(self.server.github_root, plan_id, body, filename)  # type: ignore[attr-defined]
                else:
                    result = result_import.import_summative_result(self.server.github_root, plan_id, body, filename)  # type: ignore[attr-defined]
                self.json_response(200, {"ok": True, **result})
            except ValueError as exc:
                self.json_response(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self.json_response(500, {"ok": False, "error": str(exc)})
            return
"""
            if marker in raw:
                raw=raw.replace(marker,replacement,1)
                changed=True
        _write_atomic(server,raw)

    if index.is_file():
        raw=index.read_text(encoding='utf-8')
        if 'result_import.js' not in raw:
            marker='  <script src="course_shell.js?v=1"></script>\n'
            if marker in raw:
                raw=raw.replace(marker,marker+'  <script src="result_import.js?v=1"></script>\n',1)
                _write_atomic(index,raw)
                changed=True

    if checkpoint.is_file():
        raw=checkpoint.read_text(encoding='utf-8')
        replacements={
            'The returned Curriculum Transfer should install temporary families for this plan.':
                'Return one AI Result ZIP containing extension_families.json at the ZIP root. Do not return a Curriculum Transfer or GitHub Transfer.',
            'Return a Curriculum Transfer that installs one complete extension_families.json under _algebra_teacher_tools/assessment_builder/checkpoint_extensions/<plan_id>/.':
                'Return one AI Result ZIP containing one complete extension_families.json at the ZIP root. Do not return a Curriculum Transfer or GitHub Transfer. The teacher imports this ZIP with Load Returned Families in Algebra 1 Tools.',
            'Return a Curriculum Transfer that replaces _algebra_teacher_tools/assessment_builder/checkpoint_extensions/<plan_id>/extension_families.json.':
                'Return one AI Result ZIP containing the complete replacement extension_families.json at the ZIP root. The teacher imports it with Load Returned Families; do not return a Curriculum Transfer.'
        }
        new=raw
        for old,val in replacements.items(): new=new.replace(old,val)
        if new!=raw:
            _write_atomic(checkpoint,new); changed=True

    if summative.is_file():
        raw=summative.read_text(encoding='utf-8')
        replacements={
            'Return a Curriculum Transfer that installs one complete summative_families.json under _algebra_teacher_tools/assessment_builder/summative_families/<plan_id>/.':
                'Return one AI Result ZIP containing one complete summative_families.json at the ZIP root plus any required figures/ assets. Do not return a Curriculum Transfer or GitHub Transfer. The teacher imports this ZIP with Load Returned Families in Algebra 1 Tools.',
            'Return one COMPLETE summative_families.json containing accepted families plus replacements.':
                'Return one AI Result ZIP containing one COMPLETE summative_families.json with accepted families plus replacements, plus any required figures/ assets. The teacher imports it with Load Returned Families.',
            'Return one COMPLETE summative_families.json for this same plan_id containing every existing family unchanged except for the added makeup_exemplars arrays, plus any required figures/ assets in the same plan folder.':
                'Return one AI Result ZIP containing one COMPLETE summative_families.json for this same plan_id, with every existing family unchanged except for the added makeup_exemplars arrays, plus any required figures/ assets.'
        }
        new=raw
        for old,val in replacements.items(): new=new.replace(old,val)
        old='Graph-bearing results must return graph-tool-generated figures/ assets with the family JSON; do not inline coordinate SVG.\\n'
        add=old+'Return one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\\n'
        new=new.replace(old,add)
        if new!=raw:
            _write_atomic(summative,new); changed=True

    if ui.is_file():
        raw=ui.read_text(encoding='utf-8')
        replacements={
            'apply the returned transfer, then click Load Returned Families.':
                'return to Algebra 1 Tools, click Load Returned Families, and choose the AI Result ZIP.',
            'Still waiting for the returned temporary-family transfer. Apply it, then click Load Returned Families.':
                'Choose the returned AI Result ZIP with Load Returned Families.',
            'Still waiting for the returned Summative-family transfer. Apply it, then click Load Returned Families.':
                'Choose the returned AI Result ZIP with Load Returned Families.',
            'Save the Makeup Parallel Request, apply the returned transfer, then Load Returned Families.':
                'Save the Makeup Parallel Request, upload it to Curriculum Build, then import the returned AI Result ZIP with Load Returned Families.'
        }
        new=raw
        for old,val in replacements.items(): new=new.replace(old,val)
        if new!=raw:
            _write_atomic(ui,new); changed=True

    return changed


def refresh_mirror():
    memories=None
    for candidate in (ROOT.parents[1]/'memories', Path.home()/'GitHub'/'memories', Path.home()/'Documents'/'GitHub'/'memories'):
        if candidate.is_dir(): memories=candidate; break
    if not memories: return
    refresh=memories/'Tools'/'tool_mirrors'/'Refresh Algebra 1 Tools Mirror.command'
    if refresh.is_file():
        try: subprocess.run(['/bin/bash',str(refresh),'--no-prompt'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=45,check=False)
        except Exception: pass


def stop_state_process(state_path, required_text):
    if not state_path.exists(): return
    try: pid=int(json.loads(state_path.read_text()).get('pid',0))
    except Exception: pid=0
    if pid>1:
        cmd=proc_cmd(pid)
        if required_text in cmd and 'server.py' in cmd:
            try: os.kill(pid,signal.SIGTERM)
            except ProcessLookupError: pass
            for _ in range(20):
                if not proc_cmd(pid): break
                time.sleep(.1)
    try: state_path.unlink()
    except FileNotFoundError: pass


def stop_old():
    assessment_state=ROOT/'.runtime'/'assessment_builder.json'
    stop_state_process(assessment_state,'assessment_builder')
    stop_state_process(STATE,'algebra_1_tools')


def start():
    stop_old()
    changed=repair_checkpoint_request_path()
    changed=install_ai_result_import() or changed
    if changed: refresh_mirror()
    STATE.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open('a') as log:
        subprocess.Popen([sys.executable,str(SERVER)],cwd=str(ROOT),stdout=log,stderr=log,start_new_session=True)
    for _ in range(100):
        time.sleep(.1)
        if STATE.exists():
            try:
                port=int(json.loads(STATE.read_text())['port'])
                webbrowser.open(f'http://127.0.0.1:{port}/')
                return 0
            except Exception: pass
    return 1
if __name__=='__main__': raise SystemExit(start())
