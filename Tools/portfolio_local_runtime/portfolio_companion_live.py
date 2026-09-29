#!/usr/bin/env python3
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
    runtime_module = base.runtime_module
    original_replace = runtime_module.replace_tokens
    runtime_module.replace_tokens = _deferred_replace_tokens
    try:
        return base.progress._patched_build_results(*args, **kwargs)
    finally:
        runtime_module.replace_tokens = original_replace

def _install_safe_builder() -> None:
    base.runtime_module.build_results = _safe_build_results
    base.core.build_results = _safe_build_results

_original_reload = base._reload_progress_overlay

def _reload_progress_overlay_safe() -> None:
    _original_reload()
    _install_safe_builder()

base._reload_progress_overlay = _reload_progress_overlay_safe
_install_safe_builder()

def q(value: str) -> str:
    return urllib.parse.quote(value)

def nav_button(label: str, href: str, secondary: bool = False, target: str = "") -> str:
    cls = "buttonlink secondary" if secondary else "buttonlink"
    t = f' target="{target}"' if target else ""
    return f'<a class="{cls}" href="{html.escape(href)}"{t}>{html.escape(label)}</a>'

def course_card(course: str) -> str:
    qc = q(course)
    return (
        '<div class="card">'
        f'<h2>{html.escape(course)}</h2>'
        '<p class="muted">Choose what you want to do with this local Portfolio.</p>'
        '<div class="row">'
        f'{nav_button("New Evidence", f"/new-evidence?course={qc}&unit=1")}'
        f'{nav_button("Teacher Observations", f"/teacher-observations?course={qc}&unit=1")}'
        f'{nav_button("View / Print Reports", f"/reports?course={qc}&unit=1", True)}'
        f'{nav_button("Prepare Email Reports", f"/email?course={qc}&unit=1", True)}'
        f'{nav_button("Open Email Sender", "/open-email-sender", True, "_blank")}'
        '</div></div>'
    )

def page_shell(title: str, body: str) -> str:
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;background:#eef2f6;color:#182230;margin:0}}
main{{max-width:1060px;margin:28px auto;padding:0 18px}}
h1,h2,h3{{color:#173f73}}h1{{margin:0 0 6px}}
.card{{background:#fff;border:1px solid #d5dce5;border-radius:14px;padding:18px;margin:14px 0}}
.row{{display:flex;gap:9px;flex-wrap:wrap;align-items:center}}
.buttonlink,button{{background:#245b87;color:#fff;border:1px solid #245b87;border-radius:9px;padding:10px 14px;font-weight:800;text-decoration:none;cursor:pointer}}
.secondary{{background:#fff!important;color:#173f73!important;border-color:#aebdcb!important}}
.muted{{color:#667085}}label{{display:block;font-weight:700;margin:10px 0 4px}}
input,select,textarea{{font:inherit;padding:9px;border:1px solid #bdc8d4;border-radius:8px;background:#fff;max-width:100%}}
input[type=file],textarea{{width:100%}}textarea{{min-height:72px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}
.notice{{padding:10px 12px;border:1px solid #d9e0e8;border-radius:8px;margin-top:10px}}
.good{{background:#eefaf3;border-color:#b7dfc7;color:#14633f}}
.bad{{background:#fff1f0;border-color:#efbbb6;color:#912018}}
.ican-list{{max-height:330px;overflow:auto;border:1px solid #d9e1ea;border-radius:10px;padding:8px;background:#fff}}
.mg{{border-bottom:1px solid #edf0f4;padding:7px 0}}
.mg-title{{font-weight:900;color:#173f73;margin-bottom:5px}}
.ican{{display:block;font-size:13px;line-height:1.35;margin:5px 0}}
@media(max-width:760px){{.grid2,.grid3{{grid-template-columns:1fr}}}}
</style></head><body><main>{body}</main></body></html>'''

def new_evidence_page(course: str, unit: int) -> str:
    units = "".join(f'<option value="{n}"{" selected" if n == unit else ""}>Unit {n}</option>' for n in range(1,9))
    body = f'''
<div class="row">{nav_button("Portfolio Home","/",True)}{nav_button("View Reports",f"/reports?course={q(course)}&unit={unit}",True)}</div>
<h1>{html.escape(course)} - New Evidence</h1>
<p class="muted">Add only the new student evidence. Current roster, learning map, prior evidence context, and state identity are added automatically.</p>
<div class="card">
<label>Unit</label><select id="unit">{units}</select>
<label>New student evidence</label><input id="files" type="file" multiple>
<div class="grid2">
<div><label>Evidence label</label><input id="label" type="text" placeholder="Example: Quick Check 1.2"></div>
<div><label>Evidence date</label><input id="date" type="date"></div>
</div>
<label>Teacher note <span class="muted">(optional)</span></label><textarea id="note"></textarea>
<div class="row"><button id="build">Build Grading Request</button></div>
<div id="status" class="notice muted">Choose the new evidence files.</div>
</div>
<script>
const COURSE={json.dumps(course)};
const statusEl=document.getElementById('status');
function setStatus(t,c='muted'){{statusEl.className='notice '+c;statusEl.textContent=t}}
document.getElementById('unit').onchange=()=>location.href='/new-evidence?course='+encodeURIComponent(COURSE)+'&unit='+document.getElementById('unit').value;
document.getElementById('build').onclick=async()=>{{
  const files=document.getElementById('files').files;
  if(!files.length){{setStatus('Choose at least one new evidence file.','bad');return}}
  const fd=new FormData();fd.append('course',COURSE);fd.append('unit',document.getElementById('unit').value);
  fd.append('label',document.getElementById('label').value.trim()||'New Evidence');
  fd.append('date',document.getElementById('date').value);fd.append('note',document.getElementById('note').value.trim());
  for(const f of files)fd.append('evidence',f,f.name);
  setStatus('Building grading request...');
  const r=await fetch('/api/build-grading-request',{{method:'POST',body:fd}});const d=await r.json();
  if(!r.ok||d.status!=='PASS'){{setStatus(d.message||'Could not build request.','bad');return}}
  setStatus(d.message||'Grading request created.','good');
}};
</script>'''
    return page_shell(f"{course} New Evidence", body)

def teacher_observations_page(course: str, unit: int) -> str:
    units = "".join(f'<option value="{n}"{" selected" if n == unit else ""}>Unit {n}</option>' for n in range(1,9))
    body = f'''
<div class="row">{nav_button("Portfolio Home","/",True)}{nav_button("View Reports",f"/reports?course={q(course)}&unit={unit}",True)}</div>
<h1>{html.escape(course)} - Teacher Observations</h1>
<p class="muted">Teacher observations are evidence, but they do not advance the formal class assessment-opportunity clock.</p>

<div class="card">
<label>Unit</label><select id="unit">{units}</select>
</div>

<div class="card">
<h2>Record an observation now</h2>
<div class="grid3">
<div><label>Hour / period</label><select id="period"></select></div>
<div><label>Student</label><select id="student"></select></div>
<div><label>Date</label><input id="obsDate" type="date"></div>
</div>
<div class="grid2">
<div><label>Evidence strength</label><select id="strength"><option value="CONVINCING">Convincing</option><option value="PARTIAL">Partial</option><option value="LIMITED">Limited</option><option value="UNUSABLE">Unusable attempt</option></select></div>
<div><label>Optional note</label><input id="obsNote" type="text" placeholder="Example: explained without prompting"></div>
</div>
<label>I Can statements observed</label>
<div class="row"><button class="secondary" type="button" onclick="setChecks('obsList',true)">Select All</button><button class="secondary" type="button" onclick="setChecks('obsList',false)">Clear</button></div>
<div id="obsList" class="ican-list"><span class="muted">Loading...</span></div>
<div class="row"><button id="saveObs">Record Observation Locally</button></div>
<div id="obsStatus" class="notice muted">Choose a student and at least one I Can.</div>
</div>

<div class="card">
<h2>Printable walk-around checklist</h2>
<label>Hour / period</label><select id="checkPeriod"></select>
<label>I Can columns <span class="muted">(up to 8)</span></label>
<div class="row"><button class="secondary" type="button" onclick="setChecks('checkList',true)">Select All</button><button class="secondary" type="button" onclick="setChecks('checkList',false)">Clear</button></div>
<div id="checkList" class="ican-list"><span class="muted">Loading...</span></div>
<div class="row"><button id="openChecklist">Open Printable Checklist</button></div>
<div id="checkStatus" class="notice muted">Choose the hour and I Can columns.</div>
</div>

<div class="card">
<h2>Upload a completed checklist</h2>
<input id="uploadFiles" type="file" multiple>
<div class="grid2">
<div><label>Observation date</label><input id="uploadDate" type="date"></div>
<div><label>Optional note</label><input id="uploadNote" type="text"></div>
</div>
<div class="row"><button id="buildObsRequest">Build Observation Request</button></div>
<div id="uploadStatus" class="notice muted">Choose the completed checklist file(s).</div>
</div>

<script>
const COURSE={json.dumps(course)};let data=null;
const UNIT=()=>document.getElementById('unit').value;
function status(id,t,c='muted'){{const e=document.getElementById(id);e.className='notice '+c;e.textContent=t}}
function today(){{return new Date().toISOString().slice(0,10)}}
document.getElementById('obsDate').value=today();document.getElementById('uploadDate').value=today();
document.getElementById('unit').onchange=()=>location.href='/teacher-observations?course='+encodeURIComponent(COURSE)+'&unit='+UNIT();
function selected(id){{return [...document.querySelectorAll('#'+id+' input:checked')].map(x=>x.value)}}
function setChecks(id,v){{document.querySelectorAll('#'+id+' input[type=checkbox]').forEach(x=>x.checked=v)}}window.setChecks=setChecks;
function render(id){{const box=document.getElementById(id);box.innerHTML='';const groups={{}};for(const x of data.i_cans||[]){{const k=x.mastery_goal_id+' · '+x.mastery_goal_title;(groups[k]??=[]).push(x)}}for(const [k,items] of Object.entries(groups)){{const g=document.createElement('div');g.className='mg';g.innerHTML='<div class="mg-title">'+k+'</div>';for(const x of items){{const l=document.createElement('label');l.className='ican';l.innerHTML='<input type="checkbox" value="'+x.i_can_id+'"> <b>'+x.i_can_id+'</b> · '+x.statement;g.appendChild(l)}}box.appendChild(g)}}}}
function fillStudents(){{const p=document.getElementById('period').value;document.getElementById('student').innerHTML=(data.students||[]).filter(s=>s.period===p).map(s=>'<option value="'+s.student_key+'">'+s.student_name+'</option>').join('')}}
async function load(){{const r=await fetch('/api/observation-data?course='+encodeURIComponent(COURSE)+'&unit='+UNIT(),{{cache:'no-store'}});data=await r.json();if(!r.ok||data.status!=='PASS'){{status('obsStatus',data.message||'Could not load observation data.','bad');return}}const opts=(data.periods||[]).map(p=>'<option value="'+p+'">'+p+'</option>').join('');document.getElementById('period').innerHTML=opts;document.getElementById('checkPeriod').innerHTML=opts;fillStudents();render('obsList');render('checkList')}}
document.getElementById('period').onchange=fillStudents;
document.getElementById('saveObs').onclick=async()=>{{const ids=selected('obsList');if(!ids.length){{status('obsStatus','Select at least one I Can.','bad');return}}const fd=new FormData();fd.append('course',COURSE);fd.append('unit',UNIT());fd.append('student_key',document.getElementById('student').value);fd.append('strength',document.getElementById('strength').value);fd.append('date',document.getElementById('obsDate').value);fd.append('note',document.getElementById('obsNote').value.trim());ids.forEach(x=>fd.append('i_can_id',x));status('obsStatus','Saving observation...');const r=await fetch('/api/add-observation',{{method:'POST',body:fd}});const d=await r.json();if(!r.ok||d.status!=='PASS'){{status('obsStatus',d.message||'Could not save observation.','bad');return}}status('obsStatus',d.message||'Observation saved.','good');setChecks('obsList',false)}};
document.getElementById('openChecklist').onclick=()=>{{const ids=selected('checkList');if(!ids.length){{status('checkStatus','Select at least one I Can.','bad');return}}if(ids.length>8){{status('checkStatus','Choose at most 8 I Cans.','bad');return}}const p=new URLSearchParams({{course:COURSE,unit:UNIT(),period:document.getElementById('checkPeriod').value}});ids.forEach(x=>p.append('i_can',x));window.open('/checklist?'+p.toString(),'_blank');status('checkStatus','Checklist opened.','good')}};
document.getElementById('buildObsRequest').onclick=async()=>{{const files=document.getElementById('uploadFiles').files;if(!files.length){{status('uploadStatus','Choose the completed checklist file(s).','bad');return}}const fd=new FormData();fd.append('course',COURSE);fd.append('unit',UNIT());fd.append('date',document.getElementById('uploadDate').value);fd.append('note',document.getElementById('uploadNote').value.trim());for(const f of files)fd.append('evidence',f,f.name);status('uploadStatus','Building observation request...');const r=await fetch('/api/build-observation-request',{{method:'POST',body:fd}});const d=await r.json();if(!r.ok||d.status!=='PASS'){{status('uploadStatus',d.message||'Could not build request.','bad');return}}status('uploadStatus',d.message||'Observation request created.','good')}};
load();
</script>'''
    return page_shell(f"{course} Teacher Observations", body)

class Handler(base.Handler):
    server_version = "PortfolioLocalCompanion/2.5-authoritative"

    def _retire_teacher_dashboard_nav(self, doc: str, course: str) -> str:
        dashboard = base.core.teacher_dashboard_url(course)
        escaped_dashboard = html.escape(dashboard)
        report_old = (
            f'<a class="buttonlink secondary" href="{escaped_dashboard}" target="_blank">'
            f'Back to {html.escape(course)} Teacher Dashboard</a>'
        )
        report_new = (
            '<a class="buttonlink secondary" href="/">Back to Portfolio Home</a>'
            '<a class="buttonlink secondary" href="/open-email-sender" target="_blank">Open Email Sender</a>'
        )
        doc = doc.replace(report_old, report_new)

        email_old = (
            f'<a class="buttonlink right" href="{escaped_dashboard}" target="_blank">'
            f'Back to {html.escape(course)} Teacher Dashboard</a>'
        )
        email_new = (
            '<span class="right"></span>'
            '<a class="buttonlink" href="/" style="margin-left:8px">Portfolio Home</a>'
            '<a class="buttonlink" href="/open-email-sender" target="_blank" style="margin-left:8px">Open Email Sender</a>'
        )
        return doc.replace(email_old, email_new)

    def reports_page(self, course: str, unit: int) -> str:
        return self._retire_teacher_dashboard_nav(super().reports_page(course, unit), course)

    def email_page(self, course: str, unit: int) -> str:
        return self._retire_teacher_dashboard_nav(super().email_page(course, unit), course)

    def home_page(self) -> str:
        cards = "".join(course_card(course) for course in base.core.COURSE_CONFIG)
        return base.core.page(
            "Portfolio Local Companion",
            '<p class="lead">Private local Portfolio work. New Evidence, Teacher Observations, reports, and email preparation all live here.</p>' + cards,
        )

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/api/runtime-version":
            self.send_json({"status": "PASS", "version": "2.5-authoritative"})
            return
        if parsed.path == "/open-email-sender":
            sender_url = base._configured_sender_url()
            if not sender_url:
                self.send_html(
                    page_shell(
                        "Portfolio Email Sender",
                        '<div class="card"><h1>Email Sender not configured</h1>'
                        '<p>Open Student Data Tools and set the deployed Google Apps Script web-app URL once.</p>'
                        '<div class="row"><a class="buttonlink secondary" href="/">Back to Portfolio Home</a></div></div>'
                    ),
                    status=400,
                )
                return
            self.send_response(302)
            self.send_header("Location", sender_url)
            self.end_headers()
            return
        if parsed.path == "/new-evidence":
            course = (query.get("course") or [""])[0]
            unit = int((query.get("unit") or ["1"])[0])
            self.send_html(new_evidence_page(course, unit))
            return
        if parsed.path == "/teacher-observations":
            course = (query.get("course") or [""])[0]
            unit = int((query.get("unit") or ["1"])[0])
            self.send_html(teacher_observations_page(course, unit))
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
    print("Runtime: 2.5 authoritative local controls + progress report bridge")
    print(f"Local URL: {url}")
    print(f"Workspace root: {base.core.github_root_from_runtime()}")
    print("Private Portfolio data remains under sibling _portfolio_data.")
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
