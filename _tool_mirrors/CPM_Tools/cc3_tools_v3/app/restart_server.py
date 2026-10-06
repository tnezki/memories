#!/usr/bin/env python3
from pathlib import Path
import json, os, signal, subprocess, sys, time, webbrowser
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.runtime'/'server.json'
LOG=ROOT/'.runtime'/'server.log'
SERVER=ROOT/'app'/'server.py'

def proc_cmd(pid):
    try:
        return subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=2).stdout.strip()
    except Exception: return ''

def stop_old():
    if not STATE.exists(): return
    try: s=json.loads(STATE.read_text()); pid=int(s.get('pid',0))
    except Exception: pid=0
    if pid>1:
        cmd=proc_cmd(pid)
        if 'cc3_tools_v3' in cmd and 'server.py' in cmd:
            try: os.kill(pid,signal.SIGTERM)
            except ProcessLookupError: pass
            for _ in range(20):
                time.sleep(.1)
                try: os.kill(pid,0)
                except ProcessLookupError: break
            else:
                try: os.kill(pid,signal.SIGKILL)
                except ProcessLookupError: pass
    try: STATE.unlink()
    except FileNotFoundError: pass

def start():
    stop_old(); STATE.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open('a') as log:
        subprocess.Popen([sys.executable,str(SERVER),'--state-file',str(STATE)],cwd=str(ROOT),stdout=log,stderr=log,start_new_session=True)
    for _ in range(80):
        time.sleep(.1)
        if STATE.exists():
            try:
                s=json.loads(STATE.read_text()); port=int(s['port'])
                webbrowser.open(f'http://127.0.0.1:{port}/reader/index.html')
                return 0
            except Exception: pass
    return 1
if __name__=='__main__': raise SystemExit(start())
