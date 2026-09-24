#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
import threading
import urllib.parse
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build_grading_request import build_request
from portfolio_runtime import COURSE_CONFIG, portfolio_root, github_root_from_runtime, validate_state_zip
from prepare_portfolio_emails import prepare as prepare_email
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
        "reports_ready": (u / "03 Student Packets").is_dir(),
        "email_ready": (u / "06 Email Delivery" / "Current").is_dir(),
    }
    if state.is_file():
        m = validate_state_zip(state, course, int(unit))
        out.update({"state_ready": True, "state_version": int(m.get("state_version", 0)), "state_id": m.get("state_id")})
    return out


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
                fields[k] = [str(v)]
        except Exception:
            pass
    return fields, files


def one(fields: dict[str, list[str]], key: str, default_value: str = "") -> str:
    vals = fields.get(key) or []
    return vals[0] if vals else default_value


class Handler(BaseHTTPRequestHandler):
    server_version = "PortfolioLocalCompanion/1.0"

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
                result = prepare_email(course, unit, open_folder=True)
                self.send_json(result)
                return
            self.send_json({"status": "FAIL", "message": "Unknown endpoint"}, status=404)
        except Exception as exc:
            self.send_json({"status": "FAIL", "message": str(exc)}, status=400)

    def home_page(self) -> str:
        cards = []
        for course in COURSE_CONFIG:
            cards.append(f'<div class="card"><h2>{html.escape(course)}</h2><p><a href="/reports?course={urllib.parse.quote(course)}&unit=1">View Unit 1 reports</a></p><p><a href="/email?course={urllib.parse.quote(course)}&unit=1">Email control panel</a></p></div>')
        return page("Portfolio Local Companion", '<p class="lead">Local bridge for reports, roster updates, grading-request creation, and email PDF preparation. Keep this Terminal window open while using the course Portfolio control panels.</p>' + ''.join(cards))

    def reports_page(self, course: str, unit: int) -> str:
        s = state_status(course, unit)
        u = unit_dir(course, unit)
        groups = [
            ("Student Reports", u / "03 Student Packets"),
            ("Class & Intervention Summaries", u / "04 Class & Intervention Summaries"),
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
                        items.append(f'<li><a href="/file?course={urllib.parse.quote(course)}&unit={unit}&path={urllib.parse.quote(rel)}" target="_blank">{html.escape(rel)}</a></li>')
            body.append('<ul>' + ''.join(items) + '</ul>' if items else '<p class="muted">No current files in this folder.</p>')
            body.append('</div>')
        return page(f"{course} Unit {unit} Reports", ''.join(body))

    def email_page(self, course: str, unit: int) -> str:
        u = unit_dir(course, unit)
        current = u / "06 Email Delivery" / "Current"
        files = []
        if current.is_dir():
            for p in sorted(current.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(u).as_posix()
                    files.append(f'<li><a href="/file?course={urllib.parse.quote(course)}&unit={unit}&path={urllib.parse.quote(rel)}" target="_blank">{html.escape(rel)}</a></li>')
        form = f'''<div class="card"><h2>Prepare current email PDFs</h2><p>This creates PDFs locally from the current HTML reports, verifies student identity, builds the delivery manifest, and sends nothing.</p><form method="post" action="/api/prepare-email"><input type="hidden" name="course" value="{html.escape(course)}"><input type="hidden" name="unit" value="{unit}"><button type="submit">Prepare Email PDFs</button></form></div>'''
        current_html = '<div class="card"><h2>Current email package</h2>' + ('<ul>'+''.join(files)+'</ul>' if files else '<p class="muted">No email package prepared yet.</p>') + '</div>'
        return page(f"{course} Unit {unit} Email", form + current_html)

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
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{font-family:Arial,Helvetica,sans-serif;background:#eef2f6;color:#182230;margin:0}}main{{max-width:1000px;margin:30px auto;padding:0 18px}}h1{{color:#173f73}}.lead{{font-size:16px;line-height:1.5}}.card{{background:#fff;border:1px solid #d5dce5;border-radius:14px;padding:18px;margin:14px 0}}a{{color:#173f73;font-weight:700}}button{{background:#245b87;color:#fff;border:0;border-radius:9px;padding:11px 15px;font-weight:800;cursor:pointer}}.muted{{color:#667085}}.error{{border-color:#efb8b3;background:#fff4f2}}li{{margin:6px 0}}</style></head><body><main><h1>{html.escape(title)}</h1>{body}</main></body></html>'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    url = f"http://{HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
    print("Keep this Terminal window open while using Portfolio control panels.")
    print("Press Control-C to stop.\n")
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
