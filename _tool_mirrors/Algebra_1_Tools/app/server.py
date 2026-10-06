#!/usr/bin/env python3
from __future__ import annotations

import json, os, re, socket, subprocess, time, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote

APP_ROOT = Path(__file__).resolve().parents[1]
HOST = '127.0.0.1'
RUNTIME_DIR = APP_ROOT / '.runtime'
SETTINGS_PATH = APP_ROOT / 'library' / 'settings.json'
LOCAL_ITEMS_PATH = APP_ROOT / 'library' / 'items.json'

CATEGORIES = [
    ('lessons','Lessons',['notes']),
    ('assessments','Assessments',['quick_checks','assessments_zxrtjp']),
    ('practice','Practice',['practice_sets','warmups']),
    ('activities','Activities',['activities','investigations']),
    ('performance','Performance Tasks & Projects',['performance_tasks','projects']),
    ('reviews','Reviews',['reviews']),
    ('imported','Imported',[]),
]

def detect_github_root() -> Path | None:
    env = os.environ.get('GITHUB_ROOT','').strip()
    candidates=[]
    if env:
        candidates.append(Path(env).expanduser())
    try:
        candidates.extend([APP_ROOT.parents[1], APP_ROOT.parents[2]])
    except IndexError:
        pass
    candidates.extend([Path.home()/'GitHub', Path.home()/'Documents'/'GitHub'])
    seen=set()
    for p in candidates:
        try: p=p.resolve()
        except Exception: continue
        if str(p) in seen: continue
        seen.add(str(p))
        if (p/'algebra').is_dir() and (p/'memories').is_dir():
            return p
    return None

GITHUB_ROOT = detect_github_root()
ALGEBRA_REPO = (GITHUB_ROOT/'algebra') if GITHUB_ROOT else None
MEMORIES_REPO = (GITHUB_ROOT/'memories') if GITHUB_ROOT else None

def port_ready(port:int)->bool:
    try:
        with socket.create_connection((HOST,port),timeout=.35): return True
    except OSError: return False

def open_url(url:str)->None:
    try: subprocess.Popen(['/usr/bin/open',url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except Exception: webbrowser.open(url)

def run_background(command:list[str], log:Path|None=None)->None:
    out=subprocess.DEVNULL; handle=None
    if log:
        log.parent.mkdir(parents=True,exist_ok=True)
        handle=log.open('ab',buffering=0); out=handle
    try:
        subprocess.Popen(command,stdout=out,stderr=out,start_new_session=True)
    finally:
        if handle: handle.close()

def load_settings()->dict:
    default_mode='local_and_github' if GITHUB_ROOT else 'local_only'
    data={'delivery_mode':default_mode}
    if SETTINGS_PATH.is_file():
        try:
            saved=json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
            if saved.get('delivery_mode') in {'local_only','local_and_github'}:
                data['delivery_mode']=saved['delivery_mode']
        except Exception: pass
    return data

def save_settings(payload:dict)->dict:
    mode=str(payload.get('delivery_mode') or '')
    if mode not in {'local_only','local_and_github'}:
        raise ValueError('Unknown delivery mode.')
    if mode=='local_and_github' and not GITHUB_ROOT:
        raise ValueError('GitHub publishing is not configured on this computer.')
    SETTINGS_PATH.parent.mkdir(parents=True,exist_ok=True)
    data={'delivery_mode':mode,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%S')}
    SETTINGS_PATH.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    return data

def infer_pages_base()->str:
    if not ALGEBRA_REPO: return ''
    try:
        remote=subprocess.run(['git','-C',str(ALGEBRA_REPO),'config','--get','remote.origin.url'],capture_output=True,text=True,timeout=2).stdout.strip()
    except Exception:
        return ''
    m=re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$',remote)
    if not m: return ''
    user,repo=m.group(1),m.group(2)
    return f'https://{user}.github.io/{repo}/'

def tool_status()->dict:
    root=str(GITHUB_ROOT) if GITHUB_ROOT else ''
    return {
        'github_workspace': bool(GITHUB_ROOT),
        'github_root': root,
        'planner_available': bool(GITHUB_ROOT and (GITHUB_ROOT/'_algebra_teacher_tools/runtime/Start Teacher Tools Runtime.command').is_file()),
        'planner_running': port_ready(8767),
        'github_sync_available': bool(MEMORIES_REPO and (MEMORIES_REPO/'Tools/github_sync/Start GitHub Sync.command').is_file()),
        'reporting_available': bool(MEMORIES_REPO and (MEMORIES_REPO/'Tools/portfolio_local_runtime/Start Portfolio Local Companion.command').is_file()),
        'reporting_running': port_ready(8765),
        'pages_base': infer_pages_base(),
        'delivery_mode': load_settings()['delivery_mode'],
    }

def launch_tool(name:str)->str:
    if name=='planner':
        if port_ready(8767):
            open_url('http://127.0.0.1:8767/'); return 'Opened Algebra 1 Planner.'
        if not GITHUB_ROOT: raise RuntimeError('Planner owner setup is not installed on this computer.')
        cmd=GITHUB_ROOT/'_algebra_teacher_tools/runtime/Start Teacher Tools Runtime.command'
        if not cmd.is_file(): raise RuntimeError('Planner runtime launcher was not found.')
        run_background(['/bin/bash',str(cmd)],RUNTIME_DIR/'planner_launcher.log')
        deadline=time.time()+25
        while time.time()<deadline:
            if port_ready(8767):
                open_url('http://127.0.0.1:8767/'); return 'Opened Algebra 1 Planner.'
            time.sleep(.4)
        raise RuntimeError('Planner did not become reachable. Check .runtime/planner_launcher.log.')
    if name=='github-sync':
        if not MEMORIES_REPO: raise RuntimeError('GitHub workspace is not configured on this computer.')
        cmd=MEMORIES_REPO/'Tools/github_sync/Start GitHub Sync.command'
        if not cmd.is_file(): raise RuntimeError('GitHub Sync launcher was not found.')
        run_background(['/bin/bash',str(cmd)],RUNTIME_DIR/'github_sync_launcher.log')
        return 'Opened GitHub Sync.'
    if name=='reporting':
        if port_ready(8765):
            open_url('http://127.0.0.1:8765/'); return 'Opened Reporting / Portfolio.'
        if not MEMORIES_REPO: raise RuntimeError('Reporting owner setup is not installed on this computer.')
        cmd=MEMORIES_REPO/'Tools/portfolio_local_runtime/Start Portfolio Local Companion.command'
        if not cmd.is_file(): raise RuntimeError('Reporting launcher was not found.')
        # Use Terminal because this runtime intentionally remains interactive for Documents-folder access.
        subprocess.run(['/usr/bin/open',str(cmd)],check=False)
        return 'Opened Reporting launcher in Terminal.'
    raise RuntimeError('Unknown tool.')

def pretty_title(stem:str)->str:
    s=stem.replace('_',' ').replace('-',' ')
    s=re.sub(r'\b(u|unit)\s*(\d+)\b',lambda m:f'Unit {m.group(2)}',s,flags=re.I)
    return ' '.join(w.upper() if w.lower() in {'mc','frq'} else w.capitalize() for w in s.split())

def unit_from_path(path:str)->str:
    m=re.search(r'(?:^|/)(?:u|unit)[_-]?(\d+)',path,re.I)
    if not m: m=re.search(r'\b(\d+)[_.-](\d+)\b',path)
    return m.group(1) if m else ''

def category_for_rel(rel:str)->str:
    top=rel.split('/',1)[0]
    for key,_label,folders in CATEGORIES:
        if top in folders: return key
    return 'other'

def repo_library_items()->list[dict]:
    if not ALGEBRA_REPO: return []
    folders=set(sum((x[2] for x in CATEGORIES),[]))
    items=[]
    for folder in sorted(folders):
        base=ALGEBRA_REPO/folder
        if not base.is_dir(): continue
        for p in base.rglob('*.html'):
            try: rel=p.relative_to(ALGEBRA_REPO).as_posix()
            except Exception: continue
            name=p.name.lower()
            if name in {'index.html','library.html'}: continue
            if name.endswith('_teacher_guide.html'): kind='teacher guide'
            else: kind='student page'
            items.append({
                'id':'repo:'+rel,
                'title':pretty_title(p.stem),
                'category':category_for_rel(rel),
                'unit':unit_from_path(rel),
                'source':'github',
                'kind':kind,
                'relative_path':rel,
                'local_path':str(p),
                'hosted_url': infer_pages_base()+rel if infer_pages_base() else '',
            })
    items.sort(key=lambda x:(x['category'], int(x['unit']) if x['unit'].isdigit() else 99, x['title']))
    return items[:2500]

def local_library_items()->list[dict]:
    if not LOCAL_ITEMS_PATH.is_file(): return []
    try: raw=json.loads(LOCAL_ITEMS_PATH.read_text(encoding='utf-8'))
    except Exception: return []
    arr=raw if isinstance(raw,list) else raw.get('items',[]) if isinstance(raw,dict) else []
    out=[]
    for i,x in enumerate(arr):
        if not isinstance(x,dict): continue
        out.append({
            'id':str(x.get('id') or f'local:{i}'),
            'title':str(x.get('title') or 'Untitled'),
            'category':str(x.get('category') or 'imported'),
            'unit':str(x.get('unit') or ''),
            'source':'local',
            'kind':str(x.get('kind') or 'local item'),
            'relative_path':'',
            'local_path':str(x.get('path') or ''),
            'hosted_url':str(x.get('hosted_url') or ''),
        })
    return out

def library_payload()->dict:
    items=local_library_items()+repo_library_items()
    return {'items':items,'categories':[{'key':k,'label':l} for k,l,_ in CATEGORIES]+[{'key':'other','label':'Other'}], 'status':tool_status()}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(APP_ROOT),**kwargs)
    def log_message(self,fmt,*args):
        RUNTIME_DIR.mkdir(parents=True,exist_ok=True)
        with (RUNTIME_DIR/'server.log').open('a',encoding='utf-8') as f:
            f.write((fmt%args)+'\n')
    def send_json(self,obj,status=200):
        data=json.dumps(obj).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def read_json(self):
        n=int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n).decode('utf-8') or '{}')
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=='/api/status': return self.send_json(tool_status())
        if parsed.path=='/api/library': return self.send_json(library_payload())
        if parsed.path=='/api/open-local':
            q=parse_qs(parsed.query); raw=unquote((q.get('path') or [''])[0])
            if not raw: return self.send_json({'error':'Missing path.'},400)
            p=Path(raw)
            try:
                allowed=[APP_ROOT.resolve()]
                if GITHUB_ROOT: allowed.append(GITHUB_ROOT.resolve())
                rp=p.resolve()
                if not any(str(rp).startswith(str(a)) for a in allowed): raise ValueError
            except Exception:
                return self.send_json({'error':'Path is outside the approved workspace.'},400)
            if not p.exists(): return self.send_json({'error':'File not found.'},404)
            subprocess.run(['/usr/bin/open',str(p)],check=False)
            return self.send_json({'ok':True})
        return super().do_GET()
    def do_POST(self):
        parsed=urlparse(self.path)
        try:
            if parsed.path.startswith('/api/open-tool/'):
                name=parsed.path.rsplit('/',1)[-1]
                return self.send_json({'ok':True,'message':launch_tool(name)})
            if parsed.path=='/api/settings':
                return self.send_json({'ok':True,'settings':save_settings(self.read_json())})
            self.send_json({'error':'Not found.'},404)
        except Exception as exc:
            self.send_json({'error':str(exc)},400)

def main():
    RUNTIME_DIR.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer((HOST,0),Handler)
    port=server.server_address[1]
    (RUNTIME_DIR/'server.json').write_text(json.dumps({'pid':os.getpid(),'port':port,'root':str(APP_ROOT)},indent=2)+'\n')
    print(f'Algebra 1 Tools running at http://{HOST}:{port}/',flush=True)
    server.serve_forever()

if __name__=='__main__': main()
