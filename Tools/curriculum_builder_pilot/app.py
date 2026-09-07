from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from core.authorities import make_context
from core.git_snapshot import read_head_sha
from core.jobs import JOBS
from core.preflight import run_preflight
from core.work_order import create_work_order

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
GITHUB_ROOT = Path(os.environ.get("CURRICULUM_GITHUB_ROOT", CONFIG["github_root"])).expanduser()
STAGING_ROOT = Path(os.environ.get("CURRICULUM_BUILDER_STAGING", CONFIG["staging_root"])).expanduser()
HOST = CONFIG.get("host", "127.0.0.1")
PORT = int(os.environ.get("CURRICULUM_BUILDER_PORT", CONFIG.get("port", 8765)))


def json_bytes(obj) -> bytes:
    return json.dumps(obj, indent=2).encode("utf-8")


def course_config(name: str):
    course = CONFIG.get("courses", {}).get(name)
    if not course:
        raise ValueError(f"Unsupported pilot course: {name}")
    return course


class Handler(BaseHTTPRequestHandler):
    server_version = "CurriculumBuilderPilot/0.1"

    def log_message(self, fmt, *args):
        sys.stdout.write("[pilot] " + fmt % args + "\n")

    def _send_json(self, obj, status=200):
        body = json_bytes(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            memories = GITHUB_ROOT / "memories"
            algebra = GITHUB_ROOT / "algebra"
            self._send_json({
                "version": (HERE / "VERSION").read_text(encoding="utf-8").strip(),
                "github_root": str(GITHUB_ROOT),
                "staging_root": str(STAGING_ROOT),
                "memories_exists": memories.is_dir(),
                "algebra_exists": algebra.is_dir(),
                "memories_head": read_head_sha(memories),
                "algebra_head": read_head_sha(algebra),
                "courses": CONFIG.get("courses", {}),
                "jobs": JOBS,
                "network_policy": "LOCAL ONLY — no public web / no File Library",
                "git_policy": "NO GIT COMMANDS / NO GITHUB WRITES",
            })
            return
        if parsed.path.startswith("/api/"):
            self._send_json({"error": "Unknown API endpoint"}, 404)
            return
        self._serve_static(parsed.path)

    def _serve_static(self, path: str):
        rel = "index.html" if path in {"", "/"} else path.lstrip("/")
        target = (STATIC / rel).resolve()
        try:
            target.relative_to(STATIC.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            target = STATIC / "index.html"
        data = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            payload = self._read_json_body()
            course = payload.get("course", "Algebra 1")
            unit = int(payload.get("unit", 1))
            job = payload.get("job", "bank_map")
            cfg = course_config(course)
            if unit < 1 or unit > int(cfg["units"]):
                raise ValueError(f"Unit out of range: {unit}")
            if job not in {j["key"] for j in JOBS}:
                raise ValueError(f"Unsupported pilot job: {job}")
            ctx = make_context(GITHUB_ROOT, cfg["repo_folder"], course, unit)

            if self.path == "/api/preflight":
                self._send_json(run_preflight(ctx, job))
                return
            if self.path == "/api/create-work-order":
                preflight = run_preflight(ctx, job)
                if preflight["status"] != "PASS":
                    self._send_json({"error": "Preflight failed", "preflight": preflight}, 409)
                    return
                result = create_work_order(ctx, job, STAGING_ROOT)
                self._send_json({"status": "PASS", "result": result})
                return
            self._send_json({"error": "Unknown API endpoint"}, 404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 400)


def main():
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print("Curriculum Builder Pilot v0.1")
    print(f"Project root: {GITHUB_ROOT}")
    print(f"Runtime staging: {STAGING_ROOT}")
    print("Network policy: local project repos only")
    print("Git actions: NONE")
    print(f"Open: {url}")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
