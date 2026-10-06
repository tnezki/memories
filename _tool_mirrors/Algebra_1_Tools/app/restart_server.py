#!/usr/bin/env python3
from pathlib import Path
import json, os, signal, subprocess, sys, time, webbrowser
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.runtime'/'server.json'; LOG=ROOT/'.runtime'/'server.log'; SERVER=ROOT/'app'/'server.py'

def proc_cmd(pid):
    try: return subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=2).stdout.strip()
    except Exception: return ''

def stop_old():
    if not STATE.exists(): return
    try: pid=int(json.loads(STATE.read_text()).get('pid',0))
    except Exception: pid=0
    if pid>1 and 'algebra_1_tools' in proc_cmd(pid) and 'server.py' in proc_cmd(pid):
        try: os.kill(pid,signal.SIGTERM)
        except ProcessLookupError: pass
        time.sleep(.3)
    try: STATE.unlink()
    except FileNotFoundError: pass

def start():
    stop_old(); STATE.parent.mkdir(parents=True,exist_ok=True)
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
