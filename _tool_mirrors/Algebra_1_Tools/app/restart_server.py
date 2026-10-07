#!/usr/bin/env python3
from pathlib import Path
import json, os, signal, subprocess, sys, time, webbrowser
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.runtime'/'server.json'; LOG=ROOT/'.runtime'/'server.log'; SERVER=ROOT/'app'/'server.py'


def proc_cmd(pid):
    try: return subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=2).stdout.strip()
    except Exception: return ''


def repair_checkpoint_request_path():
    """One-time migration repair for the native Algebra Assessment Builder.

    The Checkpoint server already calls checkpoint_engine.request_path(), but the
    copied legacy engine never defined that helper. Add the deterministic helper
    beside the existing ZIP creator so direct CC3-style request downloads work.
    """
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
    updated=raw.replace(marker,helper+marker,1)
    tmp=engine.with_name(engine.name+'.tmp')
    tmp.write_text(updated,encoding='utf-8')
    os.replace(tmp,engine)
    # Keep the safe diagnostic mirror truthful after this one-time local repair.
    memories=None
    for candidate in (ROOT.parents[1]/'memories', Path.home()/'GitHub'/'memories', Path.home()/'Documents'/'GitHub'/'memories'):
        if candidate.is_dir(): memories=candidate; break
    if memories:
        refresh=memories/'Tools'/'tool_mirrors'/'Refresh Algebra 1 Tools Mirror.command'
        if refresh.is_file():
            try: subprocess.run(['/bin/bash',str(refresh),'--no-prompt'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=45,check=False)
            except Exception: pass
    return True


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
    # The Assessment Builder is a child server with its own random localhost port.
    # It must be stopped too, otherwise Algebra 1 Tools reuses stale builder code.
    assessment_state=ROOT/'.runtime'/'assessment_builder.json'
    stop_state_process(assessment_state,'assessment_builder')
    stop_state_process(STATE,'algebra_1_tools')


def start():
    stop_old()
    repair_checkpoint_request_path()
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
