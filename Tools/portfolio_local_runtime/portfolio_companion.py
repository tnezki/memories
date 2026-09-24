#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import mimetypes
import subprocess
import tempfile
import threading
import urllib.parse
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build_grading_request import build_request
from portfolio_runtime import (
    COURSE_CONFIG,
    extract_state,
    github_root_from_runtime,
    load_learning_map,
    portfolio_root,
    roster_rows,
    validate_state_zip,
)
from prepare_portfolio_emails import prepare as prepare_email
from teacher_observations import apply_teacher_observation
from update_roster import update_roster

HOST = "127.0.0.1"
PORT = 8765


def local_root() -> Path:
    return portfolio_root(github_root_from_runtime())


def unit_dir(course: str, unit: int) -> Path:
    if course not in COURSE_CONFIG:
        raise ValueError(f"Unsupported course: {course}")
    return local_root() / course / f"unit {int(unit)}"


def state_status(course: str, unit: int) -> dict:
    u = unit_dir(course, unit)
    state = u / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    out = {
        "course": course,
        "unit": int(unit),
        "state_ready": False,
        "state_version": None,
        "state_id": None,
        "reports_ready": any((u / "03 Student Packets").glob("*")) if (u / "03 Student Packets").is_dir() else False,
        "email_ready": (u / "06 Email Delivery" / "Current").is_dir(),
    }
    if state.is_file():
        m = validate_state_zip(state, course, int(unit))
        out.update({"state_ready": True, "state_version": int(m.get("state_version", 0)), "state_id": m.get("state_id")})
    return out


def observation_data(course: str, unit: int) -> dict:
    u = unit_dir(course, unit)
    state = u / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    validate_state_zip(state, course, unit)
    with tempfile.TemporaryDirectory(prefix="portfolio_companion_context_") as td:
        td = Path(td)
        extract_state(state, td)
        state_dir = td / "state"
        _rf, roster, _by = roster_rows(state_dir)
        active = [r for r in roster if r["active"] == "yes"]
        learning = load_learning_map(github_root_from_runtime(), course, unit, state_dir)
    periods = []
    for r in active:
        p = r.get("period", "").strip()
        if p and p not in periods:
            periods.append(p)
    students = [
        {"student_key": r["student_key"], "student_name": r["display_name"], "period": r["period"]}
        for r in active
    ]
    icans = []
    for mg in learning.get("mastery_goals", []):
        for item in mg.get("i_cans", []):
            icans.append({
                "mastery_goal_id": mg.get("id", ""),
                "mastery_goal_title": mg.get("title", ""),
                "i_can_id": item.get("id", ""),
                "statement": item.get("statement", ""),
            })
    return {"status": "PASS", "course": course, "unit": unit, "periods": periods, "students": students, "i_cans": icans}


def parse_form(handler: BaseHTTPRequestHandler) -> tuple[dict[str, list[str]], dict[str, list[tuple[str, bytes]]]]:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    body = handler.rfile.read(length)
    ctype = handler.headers.get("Content-Type", "")
    fields: dict[str, list[str]] = {}
    files: dict[str, list[tuple[str, bytes]]] = {}
    if ctype.startswith("multipart/form-data"):
        raw = (f"Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n").encode("utf-8") + body
        msg = BytesParser(policy=default).parsebytes(raw)
        for part in msg.iter_parts():
            cd = part.get("Content-Disposition", "")
            if "form-data" not in cd:
                continue
            name = part.get_param("name", header="content-disposition") or ""
            filename = part.get_filename()
            payload = part.get_payload(decode=True) or b""
            if filename:
                files.setdefault(name, []).append((Path(filename).name, payload))
            else:
                charset = part.get_content_charset() or "utf-8"
                fields.setdefault(name, []).append(payload.decode(charset, errors="replace"))
    elif ctype.startswith("application/x-www-form-urlencoded"):
        parsed = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
        fields = {k: [str(x) for x in v] for k, v in parsed.items()}
    elif body:
        try:
            obj = json.loads(body)
            for k, v in obj.items():
                if isinstance(v, list):
                    fields[k] = [str(x) for x in v]
                else:
                    fields[k] = [str(v)]
        except Exception:
            pass
    return fields, files


def one(fields: dict[str, list[str]], key: str, default_value: str = "") -> str:
    vals = fields.get(key) or []
    return vals[0] if vals else default_value


class Handler(BaseHTTPRequestHandler):
    server_version = "PortfolioLocalCompanion/1.2"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[Portfolio Companion] {self.address_string()} - {fmt % args}")

    def cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")

    def send_json(self, obj: dict, status: int = 200) -> None:
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(status)
        self.cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_html(self, text: str, status: int = 200) -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        q = urllib.parse.parse_qs(parsed.query)
        try:
            if path == "/api/status":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                self.send_json({"status": "PASS", **state_status(course, unit)})
                return
            if path == "/api/observation-data":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                self.send_json(observation_data(course, unit))
                return
            if path == "/reports":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                self.send_html(self.reports_page(course, unit))
                return
            if path == "/email":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                self.send_html(self.email_page(course, unit))
                return
            if path == "/checklist":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                period = (q.get("period") or [""])[0]
                ids = [x for x in q.get("i_can", []) if x]
                self.send_html(self.checklist_page(course, unit, period, ids))
                return
            if path == "/file":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                rel = (q.get("path") or [""])[0]
                self.serve_local_file(course, unit, rel)
                return
            self.send_html(self.home_page())
        except Exception as exc:
            self.send_html(self.error_page(str(exc)), status=400)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            fields, files = parse_form(self)
            if parsed.path == "/api/build-grading-request":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                label = one(fields, "label", "New Evidence")
                date = one(fields, "date", "")
                note = one(fields, "note", "")
                evidence_parts = files.get("evidence", [])
                if not evidence_parts:
                    raise ValueError("Choose at least one new evidence file.")
                with tempfile.TemporaryDirectory(prefix="portfolio_companion_upload_") as td:
                    td = Path(td)
                    evidence_paths = []
                    support_paths = []
                    for name, data in evidence_parts:
                        p = td / name; p.write_bytes(data); evidence_paths.append(p)
                    for name, data in files.get("support", []):
                        p = td / name; p.write_bytes(data); support_paths.append(p)
                    out = build_request(course, unit, evidence_paths, support_paths, label, date, note, reveal=True)
                self.send_json({"status": "PASS", "message": "Grading request created in Downloads.", "path": str(out)})
                return
            if parsed.path == "/api/build-observation-request":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                date = one(fields, "date", "")
                teacher_note = one(fields, "note", "")
                evidence_parts = files.get("evidence", [])
                if not evidence_parts:
                    raise ValueError("Upload at least one completed checklist scan/photo/PDF.")
                hard_note = (
                    "TEACHER WALK-AROUND CHECKLIST. A clearly checked student/I Can cell is teacher-observed evidence. "
                    "Blank cells mean NOT_OBSERVED, not incorrect. Preserve the printed student identity and exact I Can column. "
                    "Use CONVINCING for a clear checkmark unless the teacher wrote a different evidence-strength note. "
                    "Treat this checklist session as one independent opportunity per student/I Can."
                )
                if teacher_note.strip():
                    hard_note += " Teacher note: " + teacher_note.strip()
                with tempfile.TemporaryDirectory(prefix="portfolio_observation_upload_") as td:
                    td = Path(td)
                    evidence_paths = []
                    for name, data in evidence_parts:
                        p = td / name; p.write_bytes(data); evidence_paths.append(p)
                    out = build_request(course, unit, evidence_paths, [], "Teacher Walk-Around Checklist", date, hard_note, reveal=True)
                self.send_json({"status": "PASS", "message": "Observation grading request created in Downloads.", "path": str(out)})
                return
            if parsed.path == "/api/add-observation":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                student_key = one(fields, "student_key")
                ids = fields.get("i_can_id", [])
                strength = one(fields, "strength", "CONVINCING")
                date = one(fields, "date", "")
                note = one(fields, "note", "")
                result = apply_teacher_observation(course, unit, student_key, ids, strength, date, note)
                result["message"] = f"Recorded {result.get('observation_i_can_count', 0)} teacher observation(s) and refreshed local Portfolio state/reports."
                self.send_json(result)
                return
            if parsed.path == "/api/update-roster":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                note = one(fields, "note", "")
                roster_parts = files.get("roster", [])
                if not roster_parts:
                    raise ValueError("Choose the current PowerSchool roster/template CSV file(s).")
                with tempfile.TemporaryDirectory(prefix="portfolio_companion_roster_") as td:
                    td = Path(td)
                    paths = []
                    for name, data in roster_parts:
                        p = td / name; p.write_bytes(data); paths.append(p)
                    result = update_roster(course, unit, paths, note)
                self.send_json(result)
                return
            if parsed.path == "/api/prepare-email":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                selected = [x for x in fields.get("student_key", []) if x]
                result = prepare_email(course, unit, open_folder=True, selected_student_keys=selected)
                result["message"] = f"Prepared {result.get('prepared_pdfs', 0)} selected student PDF(s). No email was sent."
                self.send_json(result)
                return
            self.send_json({"status": "FAIL", "message": "Unknown endpoint"}, status=404)
        except Exception as exc:
            self.send_json({"status": "FAIL", "message": str(exc)}, status=400)

    def home_page(self) -> str:
        cards = []
        for course in COURSE_CONFIG:
            q = urllib.parse.quote(course)
            cards.append(f'<div class="card"><h2>{html.escape(course)}</h2><p><a href="/reports?course={q}&unit=1">View Unit 1 reports</a></p><p><a href="/email?course={q}&unit=1">Email control panel</a></p></div>')
        return page("Portfolio Local Companion", '<p class="lead">Local bridge for Portfolio reports, teacher observations, grading requests, roster maintenance, and selected-student email PDF preparation.</p>' + ''.join(cards))

    def reports_page(self, course: str, unit: int) -> str:
        s = state_status(course, unit)
        u = unit_dir(course, unit)
        groups = [
            ("Student Reports", u / "03 Student Packets"),
            ("Teacher Report", u / "04 Class & Intervention Summaries"),
            ("PowerSchool Exports", u / "05 PowerSchool Exports"),
        ]
        body = [f'<p class="lead"><b>{html.escape(course)} - Unit {unit}</b> &nbsp; State v{s.get("state_version") if s.get("state_ready") else "not initialized"}</p>']
        for title, folder in groups:
            body.append(f'<div class="card"><h2>{html.escape(title)}</h2>')
            items = []
            if folder.is_dir():
                for p in sorted(folder.rglob("*")):
                    if p.is_file():
                        rel = p.relative_to(u).as_posix()
                        items.append(f'<li><a href="/file?course={urllib.parse.quote(course)}&unit={unit}&path={urllib.parse.quote(rel)}" target="_blank">{html.escape(p.name)}</a><span class="path">{html.escape(rel)}</span></li>')
            body.append('<ul class="files">' + ''.join(items) + '</ul>' if items else '<p class="muted">No current files in this folder.</p>')
            body.append('</div>')
        return page(f"{course} Unit {unit} Reports", ''.join(body))

    def email_page(self, course: str, unit: int) -> str:
        data = observation_data(course, unit)
        u = unit_dir(course, unit)
        current = u / "06 Email Delivery" / "Current"
        current_files = []
        if current.is_dir():
            for p in sorted(current.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(u).as_posix()
                    current_files.append(f'<li><a href="/file?course={urllib.parse.quote(course)}&unit={unit}&path={urllib.parse.quote(rel)}" target="_blank">{html.escape(p.name)}</a></li>')
        by_period: dict[str, list[dict]] = {}
        for s in data["students"]:
            by_period.setdefault(s["period"], []).append(s)
        groups = []
        for period, students in by_period.items():
            checks = ''.join(
                f'<label class="student"><input type="checkbox" name="student_key" value="{html.escape(s["student_key"])}" checked> {html.escape(s["student_name"])}</label>'
                for s in students
            )
            groups.append(f'<div class="period"><h3>{html.escape(period)}</h3><div class="students">{checks}</div></div>')
        form = f'''<div class="card"><h2>Prepare selected reports for email</h2><p>Select only the students whose current reports you want prepared. PDFs are generated locally; nothing is sent.</p><div class="row"><button type="button" class="secondary" onclick="setAll(true)">Select All</button><button type="button" class="secondary" onclick="setAll(false)">Deselect All</button></div><form id="emailForm"><input type="hidden" name="course" value="{html.escape(course)}"><input type="hidden" name="unit" value="{unit}">{''.join(groups)}<button type="submit">Prepare Selected PDFs</button></form><div id="emailStatus" class="notice muted"></div></div>'''
        current_html = '<div class="card"><h2>Current email package</h2>' + ('<ul>'+''.join(current_files)+'</ul>' if current_files else '<p class="muted">No email package prepared yet.</p>') + '</div>'
        script = '''<script>function setAll(v){document.querySelectorAll('input[name="student_key"]').forEach(x=>x.checked=v)}document.getElementById('emailForm').addEventListener('submit',async(e)=>{e.preventDefault();const st=document.getElementById('emailStatus');st.textContent='Preparing selected PDFs locally...';const fd=new FormData(e.target);try{const r=await fetch('/api/prepare-email',{method:'POST',body:fd});const d=await r.json();if(!r.ok||d.status!=='PASS')throw new Error(d.message||'Email preparation failed');st.className='notice good';st.textContent=d.message+' Ready rows: '+d.ready_rows+'.';setTimeout(()=>location.reload(),900)}catch(err){st.className='notice bad';st.textContent=err.message}})</script>'''
        return page(f"{course} Unit {unit} Email Reports", form + current_html + script)

    def checklist_page(self, course: str, unit: int, period: str, ids: list[str]) -> str:
        if not period:
            raise ValueError("Choose a class hour/period for the checklist.")
        if not ids:
            raise ValueError("Select at least one I Can for the checklist.")
        if len(ids) > 8:
            raise ValueError("Choose at most 8 I Cans per walk-around checklist so the printed columns remain usable.")
        data = observation_data(course, unit)
        students = [s for s in data["students"] if s["period"] == period]
        if not students:
            raise ValueError(f"No active students were found for {period}.")
        lookup = {x["i_can_id"]: x for x in data["i_cans"]}
        missing = [x for x in ids if x not in lookup]
        if missing:
            raise ValueError("Unknown I Can: " + ", ".join(missing))
        heads = ''.join(f'<th><b>{html.escape(iid)}</b><span>{html.escape(lookup[iid]["statement"])}</span></th>' for iid in ids)
        check_cells = ''.join('<td class="check"></td>' for _ in ids)
        rows = ''.join(
            '<tr><td class="name">' + html.escape(s["student_name"]) + '</td>' + check_cells + '</tr>'
            for s in students
        )
        body = f'''<div class="check-head"><div><h1>{html.escape(course)} Unit {unit} Walk-Around Checklist</h1><p>{html.escape(period)}</p></div><div class="fields">Date: __________________ &nbsp;&nbsp; Activity/Source: ______________________________</div></div><p class="directions">Check a box only when you directly observe the student demonstrate that I Can. A blank box means not observed, not incorrect.</p><table class="checklist"><thead><tr><th class="name">Student</th>{heads}</tr></thead><tbody>{rows}</tbody></table><p class="footer">After class, you can enter observations directly in the Portfolio control panel or upload a scan/photo of this completed checklist to build an observation grading request.</p><script>window.addEventListener('load',()=>setTimeout(()=>window.print(),250))</script>'''
        return checklist_page_shell(body)

    def serve_local_file(self, course: str, unit: int, rel: str) -> None:
        u = unit_dir(course, unit).resolve()
        p = (u / rel).resolve()
        if u not in p.parents or not p.is_file():
            raise ValueError("Requested file is outside the Portfolio Unit folder or does not exist.")
        data = p.read_bytes()
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if ctype == "application/octet-stream" or p.suffix.lower() in {".csv", ".zip"}:
            self.send_header("Content-Disposition", f'inline; filename="{p.name}"')
        self.end_headers()
        self.wfile.write(data)

    def error_page(self, message: str) -> str:
        return page("Portfolio Local Companion - Error", f'<div class="card error"><h2>Could not complete that action</h2><p>{html.escape(message)}</p></div>')


def page(title: str, body: str) -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{font-family:Arial,Helvetica,sans-serif;background:#eef2f6;color:#182230;margin:0}}main{{max-width:1080px;margin:30px auto;padding:0 18px}}h1{{color:#173f73}}h2{{color:#173f73}}h3{{margin:12px 0 8px;color:#173f73}}.lead{{font-size:16px;line-height:1.5}}.card{{background:#fff;border:1px solid #d5dce5;border-radius:14px;padding:18px;margin:14px 0}}a{{color:#173f73;font-weight:700}}button{{background:#245b87;color:#fff;border:1px solid #245b87;border-radius:9px;padding:11px 15px;font-weight:800;cursor:pointer}}button.secondary{{background:#fff;color:#173f73;border-color:#aebdcb}}.row{{display:flex;gap:8px;margin:10px 0;flex-wrap:wrap}}.muted{{color:#667085}}.error,.notice.bad{{border-color:#efb8b3;background:#fff4f2;color:#8c2018}}.notice.good{{border-color:#b8e4ca;background:#eefbf4;color:#125f3e}}.notice{{padding:9px 11px;border-radius:8px;margin-top:10px}}li{{margin:7px 0}}.files .path{{display:block;color:#667085;font-size:11px;font-weight:400}}.period{{border-top:1px solid #e0e6ee;padding-top:4px;margin-top:10px}}.students{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px 12px;margin-bottom:12px}}.student{{font-size:13px}}@media(max-width:760px){{.students{{grid-template-columns:1fr 1fr}}}}</style></head><body><main><h1>{html.escape(title)}</h1>{body}</main></body></html>'''


def checklist_page_shell(body: str) -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Portfolio Walk-Around Checklist</title><style>@page{{size:Letter landscape;margin:.32in}}*{{box-sizing:border-box}}body{{font-family:Arial,Helvetica,sans-serif;margin:0;color:#17243a}}.check-head{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #173f73;padding-bottom:6px;margin-bottom:6px}}h1{{font-size:20px;margin:0;color:#173f73}}.check-head p{{margin:2px 0 0;font-weight:700}}.fields{{font-size:11px}}.directions{{font-size:10px;margin:5px 0 7px}}table{{border-collapse:collapse;width:100%;table-layout:fixed}}th,td{{border:1px solid #65758b}}th{{background:#eaf1fa;padding:4px;font-size:8.5px;vertical-align:bottom}}th span{{display:block;font-weight:400;line-height:1.14;margin-top:2px}}th.name,td.name{{width:1.8in;text-align:left}}td.name{{padding:4px 5px;font-size:10px;font-weight:700}}td.check{{height:.32in;background:#fff}}.footer{{font-size:8.5px;color:#5a687b;margin-top:6px}}@media print{{button{{display:none}}}}</style></head><body>{body}</body></html>'''


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    url = f"http://{HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
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
