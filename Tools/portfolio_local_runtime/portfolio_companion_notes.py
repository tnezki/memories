#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import subprocess
import threading
import urllib.parse
from pathlib import Path

import portfolio_companion as core
import portfolio_companion_final as final


NOTE_FILE = "email_message_notes.csv"
NOTE_TEXT_FILE = "email_message_notes.txt"
MAX_NOTE_LENGTH = 1000


def _clean_note(value: str) -> str:
    value = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    return value[:MAX_NOTE_LENGTH]


def _notes_path(course: str, unit: int) -> Path:
    return core.unit_dir(course, unit) / "06 Email Delivery" / "Current" / NOTE_FILE


def load_notes(course: str, unit: int) -> tuple[str, dict[str, str]]:
    path = _notes_path(course, unit)
    if not path.is_file():
        return "", {}
    weekly = ""
    students: dict[str, str] = {}
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if not weekly:
                    weekly = str(row.get("whole_class_note") or "").strip()
                key = str(row.get("student_key") or "").strip()
                if key:
                    students[key] = str(row.get("student_note") or "").strip()
    except Exception:
        return "", {}
    return weekly, students


def write_notes(course: str, unit: int, weekly_note: str, student_notes: dict[str, str], selected_keys: list[str]) -> None:
    current = core.unit_dir(course, unit) / "06 Email Delivery" / "Current"
    current.mkdir(parents=True, exist_ok=True)
    selected = {str(x).strip() for x in selected_keys if str(x).strip()}
    whole = _clean_note(weekly_note)
    notes = {str(k).strip(): _clean_note(v) for k, v in student_notes.items() if str(k).strip()}

    review = core.email_review_data(course, unit)
    rows = []
    for student in review["rows"]:
        key = student["student_key"]
        note = notes.get(key, "")
        rows.append({
            "student_key": key,
            "student_name": student["student_name"],
            "period": student["period"],
            "selected_for_package": "TRUE" if key in selected else "FALSE",
            "whole_class_note": whole,
            "student_note": note,
        })

    with (current / NOTE_FILE).open("w", newline="", encoding="utf-8") as f:
        fields = ["student_key", "student_name", "period", "selected_for_package", "whole_class_note", "student_note"]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    lines = [
        f"Portfolio email notes - {course} Unit {unit}",
        "",
        "Whole-class note:",
        whole or "(none)",
        "",
        "Student-specific notes for selected reports:",
    ]
    selected_rows = [r for r in rows if r["selected_for_package"] == "TRUE"]
    for row in selected_rows:
        lines.append(f"- {row['student_name']}: {row['student_note'] or '(none)'}")
    (current / NOTE_TEXT_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")


def email_page_shell(body: str) -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Report Email Delivery</title><style>
body{{font-family:Arial,sans-serif;background:#f3f5f8;color:#17202a;margin:0}}main{{max-width:1280px;margin:20px auto;padding:0 16px}}.card{{background:#fff;border:1px solid #d9e0e8;border-radius:14px;padding:16px;margin-bottom:14px}}h1{{margin:0 0 4px;color:#173f73}}h2{{color:#173f73}}.muted{{color:#667085;font-size:12px}}.version{{display:inline-block;margin-left:8px;padding:2px 7px;border-radius:999px;background:#e9f1fb;color:#244d78;font-size:11px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr 1fr}}}}select,.staticfield,textarea,input[type=text]{{width:100%;padding:9px;border:1px solid #bcc8d5;border-radius:8px;font:inherit;background:#fff}}textarea{{min-height:72px;resize:vertical}}input.note{{min-width:230px}}button,.buttonlink{{padding:10px 13px;border-radius:8px;border:1px solid #aab8c7;background:#fff;font-weight:700;cursor:pointer;text-decoration:none;color:#244d78;display:inline-block}}button.primary{{background:#245b87;color:#fff;border-color:#245b87}}button:disabled{{opacity:.42;cursor:not-allowed}}.status{{padding:11px;border-radius:8px;background:#f6f8fb;border:1px solid #d9e0e8;margin-top:10px;display:flex;gap:9px;align-items:center}}.ok{{background:#eefaf3;border-color:#b7dfc7}}.bad{{background:#fff1f0;border-color:#efbbb6}}.dirty{{background:#fff8e8;border-color:#e5c56d}}.spinner{{width:16px;height:16px;border:3px solid #c9d8e7;border-top-color:#245b87;border-radius:50%;animation:spin .85s linear infinite;flex:0 0 auto}}@keyframes spin{{to{{transform:rotate(360deg)}}}}.tablewrap{{overflow:auto}}table{{width:100%;min-width:1320px;border-collapse:collapse;font-size:12px}}th,td{{border-bottom:1px solid #e4e9ef;padding:8px;vertical-align:top;text-align:left}}th{{background:#f8fafc;position:sticky;top:0}}.pill{{display:inline-block;padding:2px 6px;border-radius:999px;background:#eef2f6;margin:1px 2px 1px 0;font-size:11px}}.err{{color:#a42418}}.actions{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}.right{{margin-left:auto}}.sendcol{{width:58px;text-align:center}}.student{{min-width:150px}}.notecol{{min-width:260px}}.mgcol{{width:58px;text-align:center;white-space:nowrap}}.mggrade{{display:inline-block;min-width:24px;padding:3px 6px;border-radius:999px;background:#eef2f6;font-weight:700;text-align:center}}.reviewbar{{position:sticky;bottom:0;z-index:5;box-shadow:0 -6px 18px rgba(23,32,42,.08)}}.live-warning{{border:1px solid #b7c9dc;background:#eef5fb;color:#244d78;padding:10px 12px;border-radius:8px;font-weight:700;margin-top:10px}}code{{background:#f3f5f7;border-radius:5px;padding:2px 5px}}
</style></head><body>{body}</body></html>'''


class Handler(final.Handler):
    """Final Portfolio UI with only the email note fields restored."""

    server_version = "PortfolioLocalCompanion/1.6-email-notes"

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/prepare-email":
            super().do_POST()
            return
        try:
            fields, _files = core.parse_form(self)
            course = core.one(fields, "course")
            unit = int(core.one(fields, "unit", "1"))
            core.ensure_current_html_reports(course, unit)
            selected = [x for x in fields.get("student_key", []) if x]
            weekly_note = core.one(fields, "weekly_note", "")
            raw_notes = core.one(fields, "student_notes_json", "{}")
            try:
                student_notes = json.loads(raw_notes) if raw_notes else {}
            except Exception as exc:
                raise ValueError("Could not read the student-specific email notes.") from exc
            if not isinstance(student_notes, dict):
                raise ValueError("Student-specific email notes were not in the expected format.")
            result = core.prepare_email(course, unit, open_folder=True, selected_student_keys=selected)
            write_notes(course, unit, weekly_note, student_notes, selected)
            result["message"] = f"Prepared {result.get('prepared_pdfs', 0)} selected student PDF(s) with the current class/student notes. No email was sent."
            self.send_json(result)
        except Exception as exc:
            self.send_json({"status": "FAIL", "message": str(exc)}, status=400)

    def email_page(self, course: str, unit: int) -> str:
        data = core.email_review_data(course, unit)
        u = core.unit_dir(course, unit)
        dashboard = core.teacher_dashboard_url(course)
        current = u / "06 Email Delivery" / "Current"
        package_ready = current.is_dir() and any(current.iterdir())
        saved_weekly, saved_student_notes = load_notes(course, unit)
        period_options = ['<option value="__ALL__">All periods</option>'] + [f'<option value="{html.escape(p)}">{html.escape(p)}</option>' for p in data["periods"]]
        headers = ''.join(f'<th class="mgcol">{html.escape(mid.replace("U{}-".format(unit), ""))}</th>' for mid in data["mg_ids"])
        rows = []
        for r in data["rows"]:
            mg_cells = ''.join(
                f'<td class="mgcol" title="{html.escape((m.get("code") or "") + (" - " + m.get("label", "") if m.get("label") else ""))}"><span class="mggrade">{html.escape(m.get("display", "—"))}</span></td>'
                for m in r["mg_grades"]
            )
            guardians = ''.join(f'<span class="pill">{html.escape(x.strip())}</span>' for x in __import__("re").split(r'[|;,]', r["guardian_emails"]) if x.strip()) or '<span class="muted">none</span>'
            support = ''.join(f'<span class="pill">{html.escape(x)}</span>' for x in r["support_staff_emails"]) or '<span class="muted">none</span>'
            student_email = html.escape(r["student_email"]) if r["student_email"] else '<span class="muted">none</span>'
            issue_html = ''.join(f'<div class="err">{html.escape(x)}</div>' for x in r["issues"])
            saved_note = saved_student_notes.get(r["student_key"], "")
            rows.append(
                f'<tr data-period="{html.escape(r["period"])}"><td class="sendcol"><input type="checkbox" name="student_key" value="{html.escape(r["student_key"])}" checked></td>'
                f'<td class="student"><b>{html.escape(r["student_name"])}</b></td>'
                f'<td class="notecol"><input class="note" type="text" data-note="{html.escape(r["student_key"])}" placeholder="Optional note" value="{html.escape(saved_note, quote=True)}"></td>'
                f'<td>{html.escape(r["period"])}</td>{mg_cells}'
                f'<td>{student_email}</td><td>{guardians}</td><td>{support}</td><td>{html.escape(r["status"])}{issue_html}</td></tr>'
            )
        current_text = 'A prepared package is available in the local email folder.' if package_ready else 'No email package has been prepared yet.'
        body = f'''<main>
<div class="card"><div class="actions"><div><h1>Portfolio Report Email Delivery <span class="version">local</span></h1><div class="muted">Choose who you want, add optional class/student notes, prepare only those PDFs, and review the local package. Nothing is sent from this page.</div></div><a class="buttonlink right" href="{html.escape(dashboard)}" target="_blank">Back to {html.escape(course)} Teacher Dashboard</a></div></div>
<div class="card"><div class="grid"><div><b>Course</b><div class="staticfield">{html.escape(course)}</div></div><div><b>Unit</b><div class="staticfield">Unit {unit}</div></div><div><b>Period</b><select id="period">{''.join(period_options)}</select></div><div><b>Reports</b><button id="refresh" class="primary">Refresh Reports &amp; Reload Class</button></div></div><div id="status" class="status ok">Current HTML reports loaded from local state. Review the class below.</div></div>
<div class="card"><b>This week's note</b><div class="muted">Optional note that applies to every selected student in this prepared email batch.</div><textarea id="weekly" placeholder="Optional whole-class note">{html.escape(saved_weekly)}</textarea></div>
<div class="card"><div class="tablewrap"><table><thead><tr><th class="sendcol">Prepare</th><th class="student">Student</th><th class="notecol">Custom note</th><th>Period</th>{headers}<th>Student email</th><th>Guardians</th><th>Support staff</th><th>Status</th></tr></thead><tbody id="rows">{''.join(rows)}</tbody></table></div></div>
<div class="card reviewbar"><div id="summary" class="status"></div><div class="actions" style="margin-top:12px"><button type="button" id="selectAll">Select All</button><button type="button" id="deselectAll">Deselect All</button><button type="button" id="selectVisible">Select Visible</button><button type="button" id="deselectVisible">Deselect Visible</button><span class="right"></span><button id="prepare" class="primary">Prepare Selected PDFs</button></div><div class="live-warning"><b>LOCAL PREPARATION ONLY:</b> this creates PDFs, the email manifest, and the class/student note file in <code>06 Email Delivery/Current</code>. No email is sent.</div></div>
<div class="card"><h2>Current email package</h2><p>{html.escape(current_text)} <a href="/open-folder?course={urllib.parse.quote(course)}&unit={unit}&kind=email" target="_blank">Reveal email folder in Finder</a>.</p></div>
</main>'''
        script = f'''<script>
const period=document.getElementById('period'),rows=[...document.querySelectorAll('#rows tr')],summary=document.getElementById('summary'),status=document.getElementById('status'),weekly=document.getElementById('weekly');
const noteStoreKey={json.dumps('portfolioEmailNotes::' + course + '::' + str(unit))};
function visibleRows(){{return rows.filter(r=>r.style.display!=='none')}}
function collectNotes(){{const out={{}};rows.forEach(r=>{{const x=r.querySelector('input[data-note]');if(x&&x.value.trim())out[x.dataset.note]=x.value.trim()}});return out}}
function saveDraft(){{try{{localStorage.setItem(noteStoreKey,JSON.stringify({{weekly:weekly.value,students:collectNotes()}}))}}catch(e){{}}}}
function restoreDraft(){{try{{const raw=localStorage.getItem(noteStoreKey);if(!raw)return;const d=JSON.parse(raw);if(d.weekly!==undefined)weekly.value=d.weekly||'';if(d.students)rows.forEach(r=>{{const x=r.querySelector('input[data-note]');if(x&&Object.prototype.hasOwnProperty.call(d.students,x.dataset.note))x.value=d.students[x.dataset.note]||''}})}}catch(e){{}}}}
function applyFilter(){{const p=period.value;rows.forEach(r=>r.style.display=(p==='__ALL__'||r.dataset.period===p)?'':'none');updateSummary()}}
function setAll(v,visibleOnly=false){{(visibleOnly?visibleRows():rows).forEach(r=>{{const x=r.querySelector('input[name="student_key"]');if(x)x.checked=v}});updateSummary()}}
function updateSummary(){{const checked=rows.filter(r=>r.querySelector('input[name="student_key"]')?.checked).length;const vis=visibleRows().length;summary.className='status '+(checked?'ok':'dirty');summary.textContent=`${{checked}} student report(s) selected · ${{vis}} row(s) visible`;document.getElementById('prepare').disabled=checked===0}}
period.addEventListener('change',applyFilter);weekly.addEventListener('input',saveDraft);rows.forEach(r=>{{r.querySelector('input[name="student_key"]')?.addEventListener('change',updateSummary);r.querySelector('input[data-note]')?.addEventListener('input',saveDraft)}});
document.getElementById('selectAll').onclick=()=>setAll(true,false);document.getElementById('deselectAll').onclick=()=>setAll(false,false);document.getElementById('selectVisible').onclick=()=>setAll(true,true);document.getElementById('deselectVisible').onclick=()=>setAll(false,true);
document.getElementById('refresh').onclick=async()=>{{saveDraft();const b=document.getElementById('refresh');b.disabled=true;status.className='status';status.innerHTML='<span class="spinner"></span><span>Rebuilding reports from current state...</span>';const fd=new FormData();fd.append('course',{json.dumps(course)});fd.append('unit',{json.dumps(str(unit))});try{{const rr=await fetch('/api/refresh-reports',{{method:'POST',body:fd}});const d=await rr.json();if(!rr.ok||d.status!=='PASS')throw new Error(d.message||'Refresh failed');status.className='status ok';status.textContent=d.message;setTimeout(()=>location.reload(),650)}}catch(e){{status.className='status bad';status.textContent=e.message;b.disabled=false}}}};
document.getElementById('prepare').onclick=async()=>{{saveDraft();const chosen=rows.map(r=>r.querySelector('input[name="student_key"]')).filter(x=>x&&x.checked);if(!chosen.length)return;const b=document.getElementById('prepare');b.disabled=true;status.className='status';status.innerHTML='<span class="spinner"></span><span>Preparing selected PDFs and saving notes locally...</span>';const fd=new FormData();fd.append('course',{json.dumps(course)});fd.append('unit',{json.dumps(str(unit))});fd.append('weekly_note',weekly.value.trim());fd.append('student_notes_json',JSON.stringify(collectNotes()));chosen.forEach(x=>fd.append('student_key',x.value));try{{const rr=await fetch('/api/prepare-email',{{method:'POST',body:fd}});const d=await rr.json();if(!rr.ok||d.status!=='PASS')throw new Error(d.message||'Email preparation failed');status.className='status ok';status.textContent=d.message+' Ready rows: '+d.ready_rows+'. No email was sent.';setTimeout(()=>location.reload(),900)}}catch(e){{status.className='status bad';status.textContent=e.message;b.disabled=false;updateSummary()}}}};
restoreDraft();applyFilter();updateSummary();
</script>'''
        return email_page_shell(body + script)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=core.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    server = core.ThreadingHTTPServer((core.HOST, args.port), Handler)
    url = f"http://{core.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
    print("Runtime: email-notes-1.6")
    print("The helper is local to this Mac and does not expose Portfolio data to the network.")
    print("Press Control-C to stop this foreground instance.\n")
    if not args.no_open:
        threading.Timer(0.5, lambda: subprocess.run(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPortfolio Local Companion stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
