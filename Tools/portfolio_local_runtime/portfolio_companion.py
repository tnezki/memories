#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import mimetypes
import re
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
    build_results,
    extract_state,
    github_root_from_runtime,
    install_results_to_local_folders,
    load_learning_map,
    portfolio_root,
    read_csv,
    roster_rows,
    sha256_file,
    validate_state_zip,
)
from prepare_portfolio_emails import load_contacts, prepare as prepare_email
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


def teacher_dashboard_url(course: str) -> str:
    if course not in COURSE_CONFIG:
        raise ValueError(f"Unsupported course: {course}")
    repo_folder = COURSE_CONFIG[course]["repo_folder"]
    return f"https://tnezki.github.io/{repo_folder}/teacher_dashboard______zptdf.html"


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


def ensure_current_html_reports(course: str, unit: int, force: bool = False) -> bool:
    """Rebuild canonical local HTML reports from the installed state.

    With force=False, rebuild only when canonical HTML is missing. With force=True,
    regenerate student HTML, teacher HTML, and PowerSchool exports without changing
    evidence, grades, state identity, or state version.
    """
    u = unit_dir(course, unit)
    individual = u / "03 Student Packets" / "individual"
    teacher_html = u / "04 Class & Intervention Summaries" / "teacher_summary.html"
    if not force and individual.is_dir() and any(individual.glob("*.html")) and teacher_html.is_file():
        return False

    state = u / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    manifest = validate_state_zip(state, course, unit)
    with tempfile.TemporaryDirectory(prefix="portfolio_companion_report_refresh_") as td:
        td = Path(td)
        state_work = td / "state_work"
        extract_state(state, state_work)
        state_dir = state_work / "state"
        run_manifest = {}
        run_path = state_dir / "run_manifest.json"
        if run_path.is_file():
            try:
                run_manifest = json.loads(run_path.read_text(encoding="utf-8"))
            except Exception:
                run_manifest = {}
        try:
            report_number = int(run_manifest.get("report_number") or 1)
        except Exception:
            report_number = 1
        report_date = str(
            run_manifest.get("report_date")
            or str(manifest.get("generated_at") or "")[:10]
            or ""
        )
        latest_label = str(run_manifest.get("source_label") or "Current Portfolio State")
        latest_date = str(run_manifest.get("source_date") or report_date)
        results_dir = td / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        build_results(
            github_root=github_root_from_runtime(),
            runtime_dir=Path(__file__).resolve().parent,
            state_dir=state_dir,
            state_manifest=manifest,
            input_state_sha=sha256_file(state),
            course=course,
            unit=unit,
            report_number=report_number,
            report_date=report_date,
            latest_label=latest_label,
            latest_date=latest_date,
            class_insights=None,
            out_dir=results_dir,
        )
        install_results_to_local_folders(results_dir, u)
    return True



def email_review_data(course: str, unit: int) -> dict:
    """Build the local, read-only review table used by the email-prep page."""
    ensure_current_html_reports(course, unit)
    u = unit_dir(course, unit)
    state = u / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    validate_state_zip(state, course, unit)
    with tempfile.TemporaryDirectory(prefix="portfolio_email_review_") as td:
        td = Path(td)
        extract_state(state, td)
        state_dir = td / "state"
        _rf, roster, _by = roster_rows(state_dir)
        active = [r for r in roster if r["active"] == "yes"]
        recipients, support = load_contacts(state_dir, local_root())
        mg_path = state_dir / "mastery_goal_status_current.csv"
        mg_rows = read_csv(mg_path)[1] if mg_path.is_file() else []

    mg_ids = []
    grades_by = {}
    for row in mg_rows:
        mid = (row.get("mastery_goal_id") or row.get("mg_code") or "").strip()
        sk = (row.get("student_key") or "").strip()
        if mid and mid not in mg_ids:
            mg_ids.append(mid)
        if sk and mid:
            code = (row.get("grade_code") or "").strip()
            label = (row.get("grade_label") or "").strip()
            grades_by.setdefault(sk, {})[mid] = {"code": code, "label": label, "display": code or "—"}
    mg_ids = sorted(mg_ids)[:4]

    rows = []
    reports_dir = u / "03 Student Packets" / "individual"
    for student in active:
        sk = student["student_key"]
        rec = recipients.get(sk, {})
        student_email = (rec.get("student_email") or "").strip()
        guardians = (rec.get("guardian_emails") or "").strip()
        support_emails = sorted(support.get(student["student_id"], set()))
        html_ready = (reports_dir / f"{sk}.html").is_file()
        has_recipient = bool(student_email or guardians or support_emails)
        issues = []
        if not html_ready:
            issues.append("HTML report missing")
        if not has_recipient:
            issues.append("No stored recipient")
        rows.append({
            "student_key": sk,
            "student_name": student["display_name"],
            "period": student["period"],
            "mg_grades": [grades_by.get(sk, {}).get(mid, {"display": "—", "code": "", "label": ""}) for mid in mg_ids],
            "student_email": student_email,
            "guardian_emails": guardians,
            "support_staff_emails": support_emails,
            "html_ready": html_ready,
            "has_recipient": has_recipient,
            "status": "READY" if html_ready and has_recipient else "CHECK",
            "issues": issues,
        })
    periods = []
    for row in rows:
        if row["period"] and row["period"] not in periods:
            periods.append(row["period"])
    return {"course": course, "unit": unit, "periods": periods, "mg_ids": mg_ids, "rows": rows}


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
    server_version = "PortfolioLocalCompanion/1.4"

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
            if path == "/open-folder":
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                kind = (q.get("kind") or [""])[0]
                self.open_local_folder(course, unit, kind)
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
            if parsed.path == "/api/refresh-reports":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                ensure_current_html_reports(course, unit, force=True)
                status = state_status(course, unit)
                self.send_json({
                    "status": "PASS",
                    "message": "Reports refreshed from current state. No evidence, grades, or state version changed.",
                    "state_version": status.get("state_version"),
                })
                return
            if parsed.path == "/api/prepare-email":
                course = one(fields, "course")
                unit = int(one(fields, "unit", "1"))
                ensure_current_html_reports(course, unit)
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
            dash = teacher_dashboard_url(course)
            cards.append(f'<div class="card"><h2>{html.escape(course)}</h2><p><a href="/reports?course={q}&unit=1">View Unit 1 reports</a></p><p><a href="/email?course={q}&unit=1">Email control panel</a></p><p><a href="{html.escape(dash)}" target="_blank">Open Teacher Dashboard</a></p></div>')
        return page("Portfolio Local Companion", '<p class="lead">Local bridge for Portfolio reports, teacher observations, grading requests, roster maintenance, and selected-student email PDF preparation.</p>' + ''.join(cards))

    def reports_page(self, course: str, unit: int) -> str:
        rebuilt = ensure_current_html_reports(course, unit)
        st = state_status(course, unit)
        u = unit_dir(course, unit)
        groups = [
            ("Student Reports", u / "03 Student Packets"),
            ("Teacher Report", u / "04 Class & Intervention Summaries"),
            ("PowerSchool Exports", u / "05 PowerSchool Exports"),
        ]
        dashboard = teacher_dashboard_url(course)
        body = [
            f'<div class="row"><a class="buttonlink secondary" href="{html.escape(dashboard)}" target="_blank">Back to {html.escape(course)} Teacher Dashboard</a>'
            f'<button id="refreshReports" type="button">Refresh Reports from Current State</button></div>',
            f'<p class="lead"><b>{html.escape(course)} - Unit {unit}</b> &nbsp; State v{st.get("state_version") if st.get("state_ready") else "not initialized"}</p>',
            '<div id="refreshStatus" class="notice muted">Refresh is report-only: it rebuilds student HTML, teacher HTML, and PowerSchool CSVs from the current state.</div>',
        ]
        if rebuilt:
            body.append('<div class="notice good">Current HTML reports were rebuilt from the installed local Portfolio state. No evidence, grades, or state version changed.</div>')
        for title, folder in groups:
            body.append(f'<div class="card"><h2>{html.escape(title)}</h2>')
            if title == "PowerSchool Exports":
                rel_folder = f'_portfolio_data/{course}/unit {unit}/05 PowerSchool Exports'
                reveal = f'/open-folder?course={urllib.parse.quote(course)}&unit={unit}&kind=powerschool'
                body.append(
                    f'<p><b>Already local.</b> When importing grades into PowerSchool, use the CSVs in <code>{html.escape(rel_folder)}</code>. '
                    f'<a href="{reveal}" target="_blank">Reveal PowerSchool folder in Finder</a>.</p>'
                )
            items = []
            if folder.is_dir():
                for p in sorted(folder.rglob("*")):
                    if p.is_file():
                        rel = p.relative_to(u).as_posix()
                        items.append(f'<li><a href="/file?course={urllib.parse.quote(course)}&unit={unit}&path={urllib.parse.quote(rel)}" target="_blank">{html.escape(p.name)}</a><span class="path">{html.escape(rel)}</span></li>')
            body.append('<ul class="files">' + ''.join(items) + '</ul>' if items else '<p class="muted">No current files in this folder.</p>')
            body.append('</div>')
        script = f'''<script>
        document.getElementById('refreshReports').addEventListener('click',async()=>{{
          const b=document.getElementById('refreshReports'),st=document.getElementById('refreshStatus');
          b.disabled=true;st.className='notice';st.textContent='Rebuilding current reports from state...';
          const fd=new FormData();fd.append('course',{json.dumps(course)});fd.append('unit',{json.dumps(str(unit))});
          try{{const r=await fetch('/api/refresh-reports',{{method:'POST',body:fd}});const d=await r.json();if(!r.ok||d.status!=='PASS')throw new Error(d.message||'Refresh failed');st.className='notice good';st.textContent=d.message;setTimeout(()=>location.reload(),700)}}
          catch(e){{st.className='notice bad';st.textContent=e.message;b.disabled=false}}
        }});
        </script>'''
        return page(f"{course} Unit {unit} Reports", ''.join(body) + script)

    def email_page(self, course: str, unit: int) -> str:
        data = email_review_data(course, unit)
        u = unit_dir(course, unit)
        dashboard = teacher_dashboard_url(course)
        current = u / "06 Email Delivery" / "Current"
        package_ready = current.is_dir() and any(current.iterdir())
        period_options = ['<option value="__ALL__">All periods</option>'] + [f'<option value="{html.escape(p)}">{html.escape(p)}</option>' for p in data["periods"]]
        headers = ''.join(f'<th class="mgcol">{html.escape(mid.replace("U{}-".format(unit), ""))}</th>' for mid in data["mg_ids"])
        rows = []
        for r in data["rows"]:
            mg_cells = ''.join(
                f'<td class="mgcol" title="{html.escape((m.get("code") or "") + (" - " + m.get("label", "") if m.get("label") else ""))}"><span class="mggrade">{html.escape(m.get("display", "—"))}</span></td>'
                for m in r["mg_grades"]
            )
            guardians = ''.join(f'<span class="pill">{html.escape(x.strip())}</span>' for x in re.split(r'[|;,]', r["guardian_emails"]) if x.strip()) or '<span class="muted">none</span>'
            support = ''.join(f'<span class="pill">{html.escape(x)}</span>' for x in r["support_staff_emails"]) or '<span class="muted">none</span>'
            student_email = html.escape(r["student_email"]) if r["student_email"] else '<span class="muted">none</span>'
            issue_html = ''.join(f'<div class="err">{html.escape(x)}</div>' for x in r["issues"])
            rows.append(
                f'<tr data-period="{html.escape(r["period"])}"><td class="sendcol"><input type="checkbox" name="student_key" value="{html.escape(r["student_key"])}" checked></td>'
                f'<td class="student"><b>{html.escape(r["student_name"])}</b></td><td>{html.escape(r["period"])}</td>{mg_cells}'
                f'<td>{student_email}</td><td>{guardians}</td><td>{support}</td><td>{html.escape(r["status"])}{issue_html}</td></tr>'
            )
        current_text = 'A prepared package is available in the local email folder.' if package_ready else 'No email package has been prepared yet.'
        body = f'''<main>
<div class="card"><div class="actions"><div><h1>Portfolio Report Email Delivery <span class="version">local</span></h1><div class="muted">Use the familiar review layout. Choose who you want, prepare only those PDFs, and review the local package. Nothing is sent from this page.</div></div><a class="buttonlink right" href="{html.escape(dashboard)}" target="_blank">Back to {html.escape(course)} Teacher Dashboard</a></div></div>
<div class="card"><div class="grid"><div><b>Course</b><div class="staticfield">{html.escape(course)}</div></div><div><b>Unit</b><div class="staticfield">Unit {unit}</div></div><div><b>Period</b><select id="period">{''.join(period_options)}</select></div><div><b>Reports</b><button id="refresh" class="primary">Refresh Reports &amp; Reload Class</button></div></div><div id="status" class="status ok">Current HTML reports loaded from local state. Review the class below.</div></div>
<div class="card"><div class="tablewrap"><table><thead><tr><th class="sendcol">Prepare</th><th class="student">Student</th><th>Period</th>{headers}<th>Student email</th><th>Guardians</th><th>Support staff</th><th>Status</th></tr></thead><tbody id="rows">{''.join(rows)}</tbody></table></div></div>
<div class="card reviewbar"><div id="summary" class="status"></div><div class="actions" style="margin-top:12px"><button type="button" id="selectAll">Select All</button><button type="button" id="deselectAll">Deselect All</button><button type="button" id="selectVisible">Select Visible</button><button type="button" id="deselectVisible">Deselect Visible</button><span class="right"></span><button id="prepare" class="primary">Prepare Selected PDFs</button></div><div class="live-warning"><b>LOCAL PREPARATION ONLY:</b> this creates PDFs and an email manifest in <code>06 Email Delivery/Current</code>. No email is sent.</div></div>
<div class="card"><h2>Current email package</h2><p>{html.escape(current_text)} <a href="/open-folder?course={urllib.parse.quote(course)}&unit={unit}&kind=email" target="_blank">Reveal email folder in Finder</a>.</p></div>
</main>'''
        script = f'''<script>
const period=document.getElementById('period'),rows=[...document.querySelectorAll('#rows tr')],summary=document.getElementById('summary'),status=document.getElementById('status');
function visibleRows(){{return rows.filter(r=>r.style.display!=='none')}}
function applyFilter(){{const p=period.value;rows.forEach(r=>r.style.display=(p==='__ALL__'||r.dataset.period===p)?'':'none');updateSummary()}}
function setAll(v,visibleOnly=false){{(visibleOnly?visibleRows():rows).forEach(r=>{{const x=r.querySelector('input[name="student_key"]');if(x)x.checked=v}});updateSummary()}}
function updateSummary(){{const checked=rows.filter(r=>r.querySelector('input[name="student_key"]')?.checked).length;const vis=visibleRows().length;summary.className='status '+(checked?'ok':'dirty');summary.textContent=`${{checked}} student report(s) selected · ${{vis}} row(s) visible`;document.getElementById('prepare').disabled=checked===0}}
period.addEventListener('change',applyFilter);rows.forEach(r=>r.querySelector('input[name="student_key"]')?.addEventListener('change',updateSummary));
document.getElementById('selectAll').onclick=()=>setAll(true,false);document.getElementById('deselectAll').onclick=()=>setAll(false,false);document.getElementById('selectVisible').onclick=()=>setAll(true,true);document.getElementById('deselectVisible').onclick=()=>setAll(false,true);
document.getElementById('refresh').onclick=async()=>{{const b=document.getElementById('refresh');b.disabled=true;status.className='status';status.innerHTML='<span class="spinner"></span><span>Rebuilding reports from current state...</span>';const fd=new FormData();fd.append('course',{json.dumps(course)});fd.append('unit',{json.dumps(str(unit))});try{{const rr=await fetch('/api/refresh-reports',{{method:'POST',body:fd}});const d=await rr.json();if(!rr.ok||d.status!=='PASS')throw new Error(d.message||'Refresh failed');status.className='status ok';status.textContent=d.message;setTimeout(()=>location.reload(),650)}}catch(e){{status.className='status bad';status.textContent=e.message;b.disabled=false}}}};
document.getElementById('prepare').onclick=async()=>{{const chosen=rows.map(r=>r.querySelector('input[name="student_key"]')).filter(x=>x&&x.checked);if(!chosen.length)return;const b=document.getElementById('prepare');b.disabled=true;status.className='status';status.innerHTML='<span class="spinner"></span><span>Preparing selected PDFs locally...</span>';const fd=new FormData();fd.append('course',{json.dumps(course)});fd.append('unit',{json.dumps(str(unit))});chosen.forEach(x=>fd.append('student_key',x.value));try{{const rr=await fetch('/api/prepare-email',{{method:'POST',body:fd}});const d=await rr.json();if(!rr.ok||d.status!=='PASS')throw new Error(d.message||'Email preparation failed');status.className='status ok';status.textContent=d.message+' Ready rows: '+d.ready_rows+'. No email was sent.';setTimeout(()=>location.reload(),900)}}catch(e){{status.className='status bad';status.textContent=e.message;b.disabled=false;updateSummary()}}}};
applyFilter();updateSummary();
</script>'''
        return email_page_shell(body + script)

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

    def open_local_folder(self, course: str, unit: int, kind: str) -> None:
        u = unit_dir(course, unit)
        folders = {
            "student": u / "03 Student Packets",
            "teacher": u / "04 Class & Intervention Summaries",
            "powerschool": u / "05 PowerSchool Exports",
            "email": u / "06 Email Delivery" / "Current",
        }
        folder = folders.get(kind)
        if folder is None:
            raise ValueError("Unknown local Portfolio folder request.")
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.run(["/usr/bin/open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        back = f'/reports?course={urllib.parse.quote(course)}&unit={unit}'
        self.send_html(page("Portfolio folder opened", f'<div class="card"><h2>Opened in Finder</h2><p>{html.escape(str(folder))}</p><p><a href="{back}">Return to reports</a></p></div>'))

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
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{font-family:Arial,Helvetica,sans-serif;background:#eef2f6;color:#182230;margin:0}}main{{max-width:1080px;margin:30px auto;padding:0 18px}}h1{{color:#173f73}}h2{{color:#173f73}}h3{{margin:12px 0 8px;color:#173f73}}.lead{{font-size:16px;line-height:1.5}}.card{{background:#fff;border:1px solid #d5dce5;border-radius:14px;padding:18px;margin:14px 0}}a{{color:#173f73;font-weight:700}}button,.buttonlink{{background:#245b87;color:#fff;border:1px solid #245b87;border-radius:9px;padding:11px 15px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block}}button.secondary,.buttonlink.secondary{{background:#fff;color:#173f73;border-color:#aebdcb}}.row{{display:flex;gap:8px;margin:10px 0;flex-wrap:wrap}}.muted{{color:#667085}}.error,.notice.bad{{border-color:#efb8b3;background:#fff4f2;color:#8c2018}}.notice.good{{border:1px solid #b8e4ca;background:#eefbf4;color:#125f3e}}.notice{{padding:9px 11px;border-radius:8px;margin-top:10px}}code{{background:#f3f5f7;border-radius:5px;padding:2px 5px}}li{{margin:7px 0}}.files .path{{display:block;color:#667085;font-size:11px;font-weight:400}}.period{{border-top:1px solid #e0e6ee;padding-top:4px;margin-top:10px}}.students{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px 12px;margin-bottom:12px}}.student{{font-size:13px}}@media(max-width:760px){{.students{{grid-template-columns:1fr 1fr}}}}</style></head><body><main><h1>{html.escape(title)}</h1>{body}</main></body></html>'''



def email_page_shell(body: str) -> str:
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Report Email Delivery</title><style>
body{{font-family:Arial,sans-serif;background:#f3f5f8;color:#17202a;margin:0}}main{{max-width:1280px;margin:20px auto;padding:0 16px}}.card{{background:#fff;border:1px solid #d9e0e8;border-radius:14px;padding:16px;margin-bottom:14px}}h1{{margin:0 0 4px;color:#173f73}}h2{{color:#173f73}}.muted{{color:#667085;font-size:12px}}.version{{display:inline-block;margin-left:8px;padding:2px 7px;border-radius:999px;background:#e9f1fb;color:#244d78;font-size:11px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr 1fr}}}}select,.staticfield{{width:100%;padding:9px;border:1px solid #bcc8d5;border-radius:8px;font:inherit;background:#fff}}button,.buttonlink{{padding:10px 13px;border-radius:8px;border:1px solid #aab8c7;background:#fff;font-weight:700;cursor:pointer;text-decoration:none;color:#244d78;display:inline-block}}button.primary{{background:#245b87;color:#fff;border-color:#245b87}}button:disabled{{opacity:.42;cursor:not-allowed}}.status{{padding:11px;border-radius:8px;background:#f6f8fb;border:1px solid #d9e0e8;margin-top:10px;display:flex;gap:9px;align-items:center}}.ok{{background:#eefaf3;border-color:#b7dfc7}}.bad{{background:#fff1f0;border-color:#efbbb6}}.dirty{{background:#fff8e8;border-color:#e5c56d}}.spinner{{width:16px;height:16px;border:3px solid #c9d8e7;border-top-color:#245b87;border-radius:50%;animation:spin .85s linear infinite;flex:0 0 auto}}@keyframes spin{{to{{transform:rotate(360deg)}}}}.tablewrap{{overflow:auto}}table{{width:100%;min-width:1080px;border-collapse:collapse;font-size:12px}}th,td{{border-bottom:1px solid #e4e9ef;padding:8px;vertical-align:top;text-align:left}}th{{background:#f8fafc;position:sticky;top:0}}.pill{{display:inline-block;padding:2px 6px;border-radius:999px;background:#eef2f6;margin:1px 2px 1px 0;font-size:11px}}.err{{color:#a42418}}.actions{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}.right{{margin-left:auto}}.sendcol{{width:58px;text-align:center}}.student{{min-width:150px}}.mgcol{{width:58px;text-align:center;white-space:nowrap}}.mggrade{{display:inline-block;min-width:24px;padding:3px 6px;border-radius:999px;background:#eef2f6;font-weight:700;text-align:center}}.reviewbar{{position:sticky;bottom:0;z-index:5;box-shadow:0 -6px 18px rgba(23,32,42,.08)}}.live-warning{{border:1px solid #b7c9dc;background:#eef5fb;color:#244d78;padding:10px 12px;border-radius:8px;font-weight:700;margin-top:10px}}code{{background:#f3f5f7;border-radius:5px;padding:2px 5px}}
</style></head><body>{body}</body></html>'''


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
