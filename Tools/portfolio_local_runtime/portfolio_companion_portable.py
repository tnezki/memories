#!/usr/bin/env python3
# Current portable local Portfolio front door.
from __future__ import annotations

import html
import json
import re
import subprocess
import threading
import urllib.parse
from typing import Any

import portfolio_companion_sender as base

DEFERRED_REPORT_TOKENS = {
    "{{PROGRESS_MODEL_CLASS_OVERVIEW_HTML}}",
    "{{PROGRESS_MODEL_PRIORITY_DAY_HTML}}",
    "{{PROGRESS_MODEL_PULL_IN_HTML}}",
}

def _deferred_replace_tokens(doc: str, tokens: dict[str, Any]) -> str:
    for key, value in tokens.items():
        doc = doc.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", doc)))
    bad = [token for token in unresolved if token not in DEFERRED_REPORT_TOKENS]
    if bad:
        raise ValueError("Unresolved canonical report tokens: " + ", ".join(bad))
    return doc

def _safe_build_results(*args: Any, **kwargs: Any):
    runtime = base.runtime_module
    original_replace = runtime.replace_tokens
    runtime.replace_tokens = _deferred_replace_tokens
    try:
        return base.progress._patched_build_results(*args, **kwargs)
    finally:
        runtime.replace_tokens = original_replace

def _install_safe_builder() -> None:
    base.runtime_module.build_results = _safe_build_results
    base.core.build_results = _safe_build_results

_original_reload = base._reload_progress_overlay

def _reload_progress_overlay_safe() -> None:
    _original_reload()
    _install_safe_builder()

base._reload_progress_overlay = _reload_progress_overlay_safe
_install_safe_builder()

def _q(value: str) -> str:
    return urllib.parse.quote(value)

def _course_card(course: str) -> str:
    q = _q(course)
    dash = base.core.teacher_dashboard_url(course)
    return f'''
    <div class="card">
      <h2>{html.escape(course)}</h2>
      <p class="muted">Choose the local Portfolio job you want to do.</p>
      <div class="row">
        <a class="buttonlink" href="/control?course={q}&unit=1&tab=evidence">New Evidence</a>
        <a class="buttonlink" href="/control?course={q}&unit=1&tab=observations">Teacher Observations</a>
        <a class="buttonlink secondary" href="/reports?course={q}&unit=1">View / Print Reports</a>
        <a class="buttonlink secondary" href="/email?course={q}&unit=1">Prepare Email Reports</a>
        <a class="buttonlink secondary" href="{html.escape(dash)}" target="_blank">Teacher Dashboard</a>
      </div>
    </div>'''

def _control_shell(course: str, unit: int, active_tab: str) -> str:
    if course not in base.core.COURSE_CONFIG:
        raise ValueError(f"Unsupported course: {course}")
    if active_tab not in {"evidence", "observations", "roster"}:
        active_tab = "evidence"

    course_json = json.dumps(course)
    unit_json = json.dumps(str(unit))
    tab_json = json.dumps(active_tab)
    units = "".join(
        f'<option value="{n}"{" selected" if n == unit else ""}>Unit {n}</option>'
        for n in range(1, 9)
    )

    body = f'''
<div class="control-head">
  <div>
    <h1>{html.escape(course)} Portfolio</h1>
    <p>Private local work. Current state is found automatically under <code>_portfolio_data</code>.</p>
  </div>
  <div class="row">
    <a class="buttonlink secondary" href="/">Student Data Home</a>
    <a class="buttonlink secondary" href="/reports?course={_q(course)}&unit={unit}">View Reports</a>
    <a class="buttonlink secondary" href="/email?course={_q(course)}&unit={unit}">Prepare Email Reports</a>
  </div>
</div>

<div class="card compact">
  <div class="toolbar">
    <label><b>Unit</b>
      <select id="unitSelect">{units}</select>
    </label>
    <span id="stateStatus" class="notice muted">Checking current local state...</span>
  </div>
</div>

<div class="tabs">
  <button class="tab" data-tab="evidence">New Evidence</button>
  <button class="tab" data-tab="observations">Teacher Observations</button>
  <button class="tab" data-tab="roster">Update Roster</button>
</div>

<section id="evidencePanel" class="panel card">
  <h2>Grade new evidence</h2>
  <p>Add only the new student evidence. The local runtime adds the current roster, learning map, prior I Can context, and state identity automatically.</p>
  <label class="field">New student evidence</label>
  <input id="evidenceFiles" type="file" multiple>
  <div class="grid2">
    <label class="field">Evidence label <span class="muted">optional</span><input id="evidenceLabel" type="text" placeholder="Example: Quick Check 1.2"></label>
    <label class="field">Evidence date <span class="muted">optional</span><input id="evidenceDate" type="date"></label>
  </div>
  <label class="field">Teacher note <span class="muted">optional</span><textarea id="evidenceNote" placeholder="Only add a note when this evidence needs a special instruction."></textarea></label>
  <div class="row"><button id="buildEvidence">Build Grading Request</button></div>
  <div id="evidenceStatus" class="notice muted">Choose the new evidence files.</div>
</section>

<section id="observationsPanel" class="panel card">
  <h2>Teacher observations</h2>
  <p>Direct observations are longitudinal evidence. A classroom observation does not advance the formal class assessment-opportunity clock.</p>

  <div class="subcard">
    <h3>Record an observation now</h3>
    <div class="grid3">
      <label class="field">Hour / period<select id="obsPeriod"></select></label>
      <label class="field">Student<select id="obsStudent"></select></label>
      <label class="field">Date<input id="obsDate" type="date"></label>
    </div>
    <div class="grid2">
      <label class="field">Evidence strength
        <select id="obsStrength">
          <option value="CONVINCING" selected>Convincing - observed them do it</option>
          <option value="PARTIAL">Partial</option>
          <option value="LIMITED">Limited</option>
          <option value="UNUSABLE">Unusable attempt</option>
        </select>
      </label>
      <label class="field">Optional note<input id="obsNote" type="text" placeholder="Example: explained without prompting"></label>
    </div>
    <div class="field"><b>I Can statements observed</b></div>
    <div class="row"><button class="secondary" type="button" onclick="setChecks('obsIcanList',true)">Select All</button><button class="secondary" type="button" onclick="setChecks('obsIcanList',false)">Clear</button></div>
    <div id="obsIcanList" class="ican-list"><span class="muted">Loading I Cans...</span></div>
    <div class="row"><button id="recordObservation">Record Observation Locally</button></div>
    <div id="obsStatus" class="notice muted">Choose a student and at least one I Can.</div>
  </div>

  <div class="subcard">
    <h3>Printable walk-around checklist</h3>
    <div class="grid2">
      <label class="field">Hour / period<select id="checkPeriod"></select></label>
      <div class="field"><b>Checklist targets</b><div class="muted">Choose up to 8 I Cans.</div></div>
    </div>
    <div class="row"><button class="secondary" type="button" onclick="setChecks('checkIcanList',true)">Select All</button><button class="secondary" type="button" onclick="setChecks('checkIcanList',false)">Clear</button></div>
    <div id="checkIcanList" class="ican-list"><span class="muted">Loading I Cans...</span></div>
    <div class="row"><button id="openChecklist">Open Printable Checklist</button></div>
    <div id="checkStatus" class="notice muted">Choose the hour and I Can columns.</div>
  </div>

  <div class="subcard">
    <h3>Upload a completed checklist</h3>
    <p class="muted">A scan/photo/PDF becomes a small observation grading request for ChatGPT.</p>
    <input id="checkUpload" type="file" multiple>
    <div class="grid2">
      <label class="field">Observation date<input id="checkDate" type="date"></label>
      <label class="field">Optional note<input id="checkNote" type="text"></label>
    </div>
    <div class="row"><button id="buildObservationRequest">Build Observation Request</button></div>
    <div id="uploadObsStatus" class="notice muted">Choose the completed checklist file(s).</div>
  </div>
</section>

<section id="rosterPanel" class="panel card">
  <h2>Update roster</h2>
  <p>Upload the current PowerSchool roster/template CSV file(s). Existing student history is preserved; missing students become inactive.</p>
  <input id="rosterFiles" type="file" multiple accept=".csv,text/csv">
  <label class="field">Optional note<textarea id="rosterNote"></textarea></label>
  <div class="row"><button id="updateRoster">Update Roster Locally</button></div>
  <div id="rosterStatus" class="notice muted">Choose the current roster CSV file(s).</div>
</section>
'''

    script = f'''<script>
const COURSE={course_json};
let UNIT={unit_json};
const INITIAL_TAB={tab_json};
let obsData=null;
function fdBase(){{const f=new FormData();f.append('course',COURSE);f.append('unit',UNIT);return f}}
function setNotice(id,msg,kind='muted'){{const x=document.getElementById(id);x.className='notice '+kind;x.textContent=msg}}
function today(){{return new Date().toISOString().slice(0,10)}}
document.getElementById('obsDate').value=today();
document.getElementById('checkDate').value=today();
function setTab(tab){{document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));for(const t of ['evidence','observations','roster'])document.getElementById(t+'Panel').classList.toggle('active',t===tab)}}
setTab(INITIAL_TAB);
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));
document.getElementById('unitSelect').onchange=()=>{{const p=new URLSearchParams(location.search);p.set('course',COURSE);p.set('unit',document.getElementById('unitSelect').value);p.set('tab',document.querySelector('.tab.active')?.dataset.tab||'evidence');location.search=p.toString()}};
async function post(path,form,statusId){{setNotice(statusId,'Working locally...');const r=await fetch(path,{{method:'POST',body:form}});const d=await r.json();if(!r.ok||d.status!=='PASS'){{setNotice(statusId,d.message||'Local action failed.','bad');throw new Error(d.message||'Local action failed')}}setNotice(statusId,d.message||'Completed.','good');return d}}
async function checkState(){{try{{const r=await fetch(`/api/status?course=${{encodeURIComponent(COURSE)}}&unit=${{UNIT}}`,{{cache:'no-store'}});const d=await r.json();if(!r.ok||d.status!=='PASS')throw new Error('State check failed');setNotice('stateStatus',d.state_ready?`Local state ready - v${{d.state_version}}`:'Local companion ready - no state yet',d.state_ready?'good':'warn');if(d.state_ready)await loadObservations()}}catch(e){{setNotice('stateStatus','Local state could not be loaded.','bad')}}}}
function renderIcanList(id){{const box=document.getElementById(id);box.innerHTML='';const groups=new Map();for(const x of (obsData?.i_cans||[])){{const key=x.mastery_goal_id+' · '+x.mastery_goal_title;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(x)}}for(const [title,items] of groups){{const g=document.createElement('div');g.className='mg-group';g.innerHTML=`<div class="mg-title">${{title}}</div>`;for(const x of items){{const l=document.createElement('label');l.className='ican-check';l.innerHTML=`<input type="checkbox" value="${{x.i_can_id}}"> <b>${{x.i_can_id}}</b> · ${{x.statement}}`;g.appendChild(l)}}box.appendChild(g)}}}}
function selected(id){{return [...document.querySelectorAll(`#${{id}} input[type=checkbox]:checked`)].map(x=>x.value)}}
function setChecks(id,value){{document.querySelectorAll(`#${{id}} input[type=checkbox]`).forEach(x=>x.checked=value)}}window.setChecks=setChecks;
function fillStudents(){{const p=document.getElementById('obsPeriod').value;document.getElementById('obsStudent').innerHTML=(obsData?.students||[]).filter(s=>s.period===p).map(s=>`<option value="${{s.student_key}}">${{s.student_name}}</option>`).join('')}}
async function loadObservations(){{const r=await fetch(`/api/observation-data?course=${{encodeURIComponent(COURSE)}}&unit=${{UNIT}}`,{{cache:'no-store'}});const d=await r.json();if(!r.ok||d.status!=='PASS')throw new Error(d.message||'Could not load observations');obsData=d;const opts=d.periods.map(p=>`<option value="${{p}}">${{p}}</option>`).join('');document.getElementById('obsPeriod').innerHTML=opts;document.getElementById('checkPeriod').innerHTML=opts;fillStudents();renderIcanList('obsIcanList');renderIcanList('checkIcanList')}}
document.getElementById('obsPeriod').onchange=fillStudents;
document.getElementById('buildEvidence').onclick=async()=>{{const files=document.getElementById('evidenceFiles').files;if(!files.length){{setNotice('evidenceStatus','Choose at least one new evidence file.','bad');return}}const f=fdBase();f.append('label',document.getElementById('evidenceLabel').value.trim()||'New Evidence');f.append('date',document.getElementById('evidenceDate').value);f.append('note',document.getElementById('evidenceNote').value.trim());for(const file of files)f.append('evidence',file,file.name);await post('/api/build-grading-request',f,'evidenceStatus')}};
document.getElementById('recordObservation').onclick=async()=>{{const ids=selected('obsIcanList');if(!ids.length){{setNotice('obsStatus','Select at least one I Can.','bad');return}}const f=fdBase();f.append('student_key',document.getElementById('obsStudent').value);f.append('strength',document.getElementById('obsStrength').value);f.append('date',document.getElementById('obsDate').value);f.append('note',document.getElementById('obsNote').value.trim());ids.forEach(x=>f.append('i_can_id',x));await post('/api/add-observation',f,'obsStatus');setChecks('obsIcanList',false);await checkState()}};
document.getElementById('openChecklist').onclick=()=>{{const ids=selected('checkIcanList');if(!ids.length){{setNotice('checkStatus','Select at least one I Can.','bad');return}}if(ids.length>8){{setNotice('checkStatus','Choose at most 8 I Cans.','bad');return}}const p=new URLSearchParams({{course:COURSE,unit:UNIT,period:document.getElementById('checkPeriod').value}});ids.forEach(x=>p.append('i_can',x));window.open('/checklist?'+p.toString(),'_blank');setNotice('checkStatus','Printable checklist opened.','good')}};
document.getElementById('buildObservationRequest').onclick=async()=>{{const files=document.getElementById('checkUpload').files;if(!files.length){{setNotice('uploadObsStatus','Choose the completed checklist file(s).','bad');return}}const f=fdBase();f.append('date',document.getElementById('checkDate').value);f.append('note',document.getElementById('checkNote').value.trim());for(const file of files)f.append('evidence',file,file.name);await post('/api/build-observation-request',f,'uploadObsStatus')}};
document.getElementById('updateRoster').onclick=async()=>{{const files=document.getElementById('rosterFiles').files;if(!files.length){{setNotice('rosterStatus','Choose the roster CSV file(s).','bad');return}}const f=fdBase();f.append('note',document.getElementById('rosterNote').value.trim());for(const file of files)f.append('roster',file,file.name);await post('/api/update-roster',f,'rosterStatus');await checkState()}};
checkState();
</script>'''

    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(course)} Portfolio</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;background:#eef2f6;color:#182230;margin:0}}main{{max-width:1080px;margin:26px auto;padding:0 18px}}h1,h2,h3{{color:#173f73}}h1{{margin:0}}.control-head{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;margin-bottom:14px}}.control-head p{{margin:6px 0;color:#667085}}.card{{background:#fff;border:1px solid #d5dce5;border-radius:14px;padding:18px;margin:14px 0}}.compact{{padding:12px 18px}}.subcard{{border:1px solid #d9e1ea;border-radius:12px;padding:14px;margin-top:13px;background:#fbfcfe}}.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}.toolbar{{display:flex;gap:12px;align-items:center;flex-wrap:wrap}}.tabs{{display:flex;gap:8px;flex-wrap:wrap}}.tab,button,.buttonlink{{background:#245b87;color:#fff;border:1px solid #245b87;border-radius:9px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block}}.tab{{background:#fff;color:#173f73;border-color:#aebdcb}}.tab.active{{background:#173f73;color:#fff}}button.secondary,.buttonlink.secondary{{background:#fff;color:#173f73;border-color:#aebdcb}}.panel{{display:none}}.panel.active{{display:block}}.field{{display:block;margin:11px 0 5px;font-size:13px;font-weight:700}}input,select,textarea{{font:inherit;padding:9px;border:1px solid #bec9d5;border-radius:8px;background:#fff;max-width:100%}}input[type=file],textarea{{width:100%}}textarea{{min-height:78px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}.notice{{padding:9px 11px;border-radius:8px;margin-top:10px;border:1px solid #d9e0e8}}.muted{{color:#667085}}.notice.good{{background:#eefbf4;border-color:#b8e4ca;color:#125f3e}}.notice.bad{{background:#fff1f0;border-color:#f4c1bd;color:#912018}}.notice.warn{{background:#fff8e8;border-color:#efdaa6;color:#7c4900}}.ican-list{{max-height:300px;overflow:auto;border:1px solid #d9e1ea;border-radius:10px;background:#fff;padding:8px 10px}}.mg-group{{padding:7px 0;border-bottom:1px solid #edf0f4}}.mg-title{{font-weight:900;color:#173f73;margin-bottom:5px}}.ican-check{{display:block;font-size:12px;line-height:1.35;margin:5px 0}}code{{background:#f3f5f7;border-radius:5px;padding:2px 5px}}@media(max-width:760px){{.grid2,.grid3{{grid-template-columns:1fr}}}}
</style></head><body><main>{body}{script}</main></body></html>'''

class Handler(base.Handler):
    server_version = "PortfolioLocalCompanion/2.4-portable"

    def home_page(self) -> str:
        cards = "".join(_course_card(course) for course in base.core.COURSE_CONFIG)
        intro = '<p class="lead">Private local Portfolio controls. New Evidence and Teacher Observations live here; student data remains under <code>_portfolio_data</code>.</p>'
        return base.core.page("Portfolio Local Companion", intro + cards)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/runtime-version":
            self.send_json({"status": "PASS", "version": "2.4-portable"})
            return
        if parsed.path == "/control":
            q = urllib.parse.parse_qs(parsed.query)
            course = (q.get("course") or [""])[0]
            unit = int((q.get("unit") or ["1"])[0])
            tab = (q.get("tab") or ["evidence"])[0]
            try:
                self.send_html(_control_shell(course, unit, tab))
            except Exception as exc:
                self.send_html(base.core.page("Portfolio Control - Error", f'<div class="card error"><p>{html.escape(str(exc))}</p></div>'), status=400)
            return
        super().do_GET()

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=base.core.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    server = base.core.ThreadingHTTPServer((base.core.HOST, args.port), Handler)
    url = f"http://{base.core.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
    print("Runtime: 2.4 portable local UI + progress-report token bridge")
    print(f"Workspace root: {base.core.github_root_from_runtime()}")
    print("Private Portfolio data remains under the sibling _portfolio_data folder.")
    print("Press Control-C to stop this foreground instance.\\n")
    if not args.no_open:
        threading.Timer(0.5, lambda: subprocess.run(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nPortfolio Local Companion stopped.")
    finally:
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
