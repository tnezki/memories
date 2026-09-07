from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent


def _graphics_ready(python_exe: Path) -> bool:
    try:
        proc = subprocess.run(
            [str(python_exe), "-c", "import numpy, matplotlib; import matplotlib.pyplot as plt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _bootstrap_python_runtime() -> None:
    current = Path(sys.executable)
    if _graphics_ready(current):
        return

    # The stock macOS /usr/bin/python3 used by the legacy launcher often lacks
    # matplotlib. Create one app-owned runtime, then restart THIS app in it.
    # This keeps the app and every graph subprocess on the same interpreter.
    runtime_root = Path.home() / "Downloads" / "_curriculum_builder_pilot" / "_runtime" / "app_python"
    runtime_python = runtime_root / "bin" / "python3"
    if not runtime_python.is_file():
        runtime_root.parent.mkdir(parents=True, exist_ok=True)
        print("Curriculum Builder: creating one-time local graphics runtime...")
        proc = subprocess.run([str(current), "-m", "venv", str(runtime_root)])
        if proc.returncode != 0:
            raise RuntimeError("Could not create the Curriculum Builder Python runtime.")

    if not _graphics_ready(runtime_python):
        print("Curriculum Builder: installing matplotlib/numpy into the local runtime (one time)...")
        proc = subprocess.run([
            str(runtime_python), "-m", "pip", "install",
            "--disable-pip-version-check", "--only-binary=:all:",
            "numpy", "matplotlib",
        ])
        if proc.returncode != 0:
            raise RuntimeError(
                "Could not install matplotlib/numpy into the Curriculum Builder runtime. "
                "This is a runtime dependency setup failure, not a curriculum-source failure."
            )

    if not _graphics_ready(runtime_python):
        raise RuntimeError("Curriculum Builder graphics runtime exists but still cannot import matplotlib/numpy.")

    env = os.environ.copy()
    env["CURRICULUM_BUILDER_RUNTIME"] = "managed"
    print(f"Curriculum Builder: restarting with managed runtime: {runtime_python}")
    os.execve(str(runtime_python), [str(runtime_python), str(HERE / "app.py")], env)


_bootstrap_python_runtime()

from core.authorities import make_context
from core.git_snapshot import read_head_sha
from core.jobs import JOBS
from core.map_audit import audit_bank_map, save_audit_report
from core.map_skeleton import build_mechanical_map_skeleton
from core.map_repair import apply_semantic_review_to_staging, validate_semantic_review
from core.bank_finish import finish_complete_bank, validate_ai_bank_content
from core.preflight import run_preflight
from core.work_order import create_work_order

STATIC = HERE / "static"
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
GITHUB_ROOT = Path(os.environ.get("CURRICULUM_GITHUB_ROOT", CONFIG["github_root"])).expanduser()
STAGING_ROOT = Path(os.environ.get("CURRICULUM_BUILDER_STAGING", CONFIG["staging_root"])).expanduser()
HOST = CONFIG.get("host", "127.0.0.1")
PORT = int(os.environ.get("CURRICULUM_BUILDER_PORT", CONFIG.get("port", 8765)))
DOWNLOADS = Path.home() / "Downloads"
TRANSFER_ROOT = Path(os.environ.get("CURRICULUM_TRANSFER_ROOT", str(DOWNLOADS / "_github_transfers"))).expanduser()


def json_bytes(obj) -> bytes:
    return json.dumps(obj, indent=2).encode("utf-8")


def course_config(name: str):
    course = CONFIG.get("courses", {}).get(name)
    if not course:
        raise ValueError(f"Unsupported pilot course: {name}")
    return course


def _audit_run_dir(course: str, unit: int) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = course.lower().replace(" ", "_")
    return STAGING_ROOT / "runs" / f"{stamp}_{slug}_u{unit}_local_map_audit"


def _easy_handoff_name(course: str, unit: int) -> str:
    slug = "".join(ch for ch in course if ch.isalnum())
    return f"AI_HANDOFF_{slug}_U{unit}_BANK_MAP.zip"


def _copy_handoff_to_downloads(handoff_path: str, course: str, unit: int) -> Path:
    src = Path(handoff_path)
    if not src.is_file():
        raise FileNotFoundError(f"AI handoff ZIP was not created: {src}")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    dst = DOWNLOADS / _easy_handoff_name(course, unit)
    shutil.copy2(src, dst)
    return dst




def _easy_complete_handoff_name(course: str, unit: int) -> str:
    slug = "".join(ch for ch in course if ch.isalnum())
    return f"AI_HANDOFF_{slug}_U{unit}_COMPLETE_BANK.zip"


def _copy_complete_handoff_to_downloads(handoff_path: str, course: str, unit: int) -> Path:
    src = Path(handoff_path)
    if not src.is_file():
        raise FileNotFoundError(f"Complete Bank AI handoff ZIP was not created: {src}")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    dst = DOWNLOADS / _easy_complete_handoff_name(course, unit)
    shutil.copy2(src, dst)
    return dst




def _find_bank_content_candidates() -> list[Path]:
    if not DOWNLOADS.is_dir():
        return []
    paths = [p for p in DOWNLOADS.glob("AI_BANK_CONTENT*.json") if p.is_file()]
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def _find_matching_bank_content(ctx, course_folder: str) -> tuple[Path, dict]:
    errors: list[str] = []
    for path in _find_bank_content_candidates():
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
            validate_ai_bank_content(ctx, STAGING_ROOT, content, course_folder)
            return path, content
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    suffix = ""
    if errors:
        suffix = " Latest rejected candidate: " + errors[0]
    raise FileNotFoundError(
        "No matching AI_BANK_CONTENT*.json was found in Downloads for this Complete Bank run. "
        "Download AI_BANK_CONTENT.json into Downloads, then click Finish Complete Bank." + suffix
    )


def _find_review_candidates() -> list[Path]:
    if not DOWNLOADS.is_dir():
        return []
    paths = [p for p in DOWNLOADS.glob("AI_SEMANTIC_REVIEW*.json") if p.is_file()]
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def _find_matching_review(ctx, course_folder: str, expected_run_id: str | None) -> tuple[Path, dict]:
    errors: list[str] = []
    for path in _find_review_candidates():
        try:
            review = json.loads(path.read_text(encoding="utf-8"))
            if expected_run_id and str(review.get("run_id") or "") != expected_run_id:
                continue
            validate_semantic_review(ctx, STAGING_ROOT, review, course_folder)
            return path, review
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    suffix = ""
    if errors:
        suffix = " Latest rejected candidate: " + errors[0]
    raise FileNotFoundError(
        "No matching AI_SEMANTIC_REVIEW*.json was found in Downloads for this audit run. "
        "Download the AI result, leave it in Downloads, then click Finish Audit again." + suffix
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "CurriculumBuilderPilot/0.6.0"

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
                "downloads": str(DOWNLOADS),
                "python_executable": sys.executable,
                "graphics_runtime_ready": _graphics_ready(Path(sys.executable)),
                "memories_exists": memories.is_dir(),
                "algebra_exists": algebra.is_dir(),
                "memories_head": read_head_sha(memories),
                "algebra_head": read_head_sha(algebra),
                "courses": CONFIG.get("courses", {}),
                "jobs": JOBS,
                "network_policy": "LOCAL ONLY — no public web / no File Library",
                "git_policy": "NO GIT COMMANDS / NO GITHUB WRITES",
                "pilot_capabilities": [
                    "one-click local Bank Map audit flow",
                    "mechanical facts locked before AI",
                    "AI handoff copied to Downloads with an easy filename",
                    "automatic AI semantic-result discovery in Downloads",
                    "validated staged repair + local re-audit",
                    "fail-closed github_transfer/2 package generation",
                    "Complete Bank: local 208-record lock + AI content-only handoff",
                    "Complete Bank: automatic AI_BANK_CONTENT discovery + local render/QA/finalization/transfer",
                ],
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

            if self.path == "/api/run-complete-bank-flow":
                if job != "bank_complete":
                    raise ValueError("Prepare Complete Bank is only available for Build Complete Bank in v0.5")
                preflight = run_preflight(ctx, job)
                if preflight["status"] != "PASS":
                    self._send_json({"status": "BLOCKED", "stage": "preflight", "preflight": preflight}, 409)
                    return
                work = create_work_order(ctx, job, STAGING_ROOT)
                skeleton = work.get("complete_bank_skeleton") or {}
                easy_handoff = _copy_complete_handoff_to_downloads(work["handoff_zip"], course, unit)
                self._send_json({
                    "status": "AI_NEEDED",
                    "stage": "awaiting_ai_content",
                    "preflight": preflight,
                    "work_order": work,
                    "easy_handoff": str(easy_handoff),
                    "record_count": skeleton.get("record_count"),
                    "destination_counts": skeleton.get("destination_counts"),
                    "seed_count": skeleton.get("seed_count"),
                    "accepted_map_fingerprint": skeleton.get("accepted_map_fingerprint"),
                })
                return


            if self.path == "/api/finish-complete-bank-flow":
                if job != "bank_complete":
                    raise ValueError("Finish Complete Bank is only available for Build Complete Bank")
                content_path, content = _find_matching_bank_content(ctx, cfg["repo_folder"])
                result = finish_complete_bank(
                    ctx, STAGING_ROOT, content, cfg["repo_folder"], TRANSFER_ROOT
                )
                self._send_json({
                    "status": "PASS",
                    "content_path": str(content_path),
                    "result": result,
                })
                return

            if self.path == "/api/run-audit-flow":
                if job != "audit_rebuild_bank_map":
                    raise ValueError("Simple Run Audit is only available for Audit + Rebuild Bank Map in v0.4")
                preflight = run_preflight(ctx, job)
                if preflight["status"] != "PASS":
                    self._send_json({"status": "BLOCKED", "stage": "preflight", "preflight": preflight}, 409)
                    return
                report = audit_bank_map(ctx)
                audit_run_dir = _audit_run_dir(course, unit)
                report_paths = save_audit_report(report, audit_run_dir)
                if report.get("mechanical_shape_status") != "PASS":
                    self._send_json({
                        "status": "BLOCKED",
                        "stage": "local_audit",
                        "preflight": preflight,
                        "report": report,
                        "report_paths": report_paths,
                    }, 409)
                    return
                semantic_count = int(report.get("facts", {}).get("semantic_candidate_count", 0) or 0)
                if semantic_count == 0:
                    self._send_json({
                        "status": "PASS_NO_AI",
                        "stage": "complete",
                        "preflight": preflight,
                        "report": report,
                        "report_paths": report_paths,
                    })
                    return
                work = create_work_order(ctx, job, STAGING_ROOT)
                easy_handoff = _copy_handoff_to_downloads(work["handoff_zip"], course, unit)
                self._send_json({
                    "status": "AI_NEEDED",
                    "stage": "awaiting_ai",
                    "preflight": preflight,
                    "report": report,
                    "report_paths": report_paths,
                    "work_order": work,
                    "easy_handoff": str(easy_handoff),
                    "semantic_candidate_count": semantic_count,
                })
                return

            if self.path == "/api/finish-audit-flow":
                if job != "audit_rebuild_bank_map":
                    raise ValueError("Finish Audit is only available for Audit + Rebuild Bank Map in v0.4")
                expected_run_id = str(payload.get("run_id") or "").strip() or None
                review_path, review = _find_matching_review(ctx, cfg["repo_folder"], expected_run_id)
                result = apply_semantic_review_to_staging(
                    ctx, STAGING_ROOT, review, cfg["repo_folder"], TRANSFER_ROOT
                )
                self._send_json({
                    "status": "PASS",
                    "review_path": str(review_path),
                    "result": result,
                })
                return

            # Advanced/manual endpoints retained for troubleshooting and later pipeline work.
            if self.path == "/api/preflight":
                self._send_json(run_preflight(ctx, job))
                return
            if self.path == "/api/build-map-skeleton":
                preflight = run_preflight(ctx, "bank_map")
                if preflight["status"] != "PASS":
                    self._send_json({"error": "Bank Map preflight failed", "preflight": preflight}, 409)
                    return
                result = build_mechanical_map_skeleton(ctx, STAGING_ROOT)
                self._send_json({"status": "PASS", "result": result})
                return
            if self.path == "/api/map-audit":
                preflight = run_preflight(ctx, "audit_rebuild_bank_map")
                if preflight["status"] != "PASS":
                    self._send_json({"error": "Audit preflight failed", "preflight": preflight}, 409)
                    return
                report = audit_bank_map(ctx)
                run_dir = _audit_run_dir(course, unit)
                paths = save_audit_report(report, run_dir)
                self._send_json({"status": "PASS", "report": report, "paths": paths, "run_dir": str(run_dir)})
                return
            if self.path == "/api/create-work-order":
                preflight = run_preflight(ctx, job)
                if preflight["status"] != "PASS":
                    self._send_json({"error": "Preflight failed", "preflight": preflight}, 409)
                    return
                result = create_work_order(ctx, job, STAGING_ROOT)
                self._send_json({"status": "PASS", "result": result})
                return
            if self.path == "/api/import-semantic-review":
                if job != "audit_rebuild_bank_map":
                    raise ValueError("AI semantic review import is only available for Audit + Rebuild Bank Map")
                review = payload.get("review")
                if not isinstance(review, dict):
                    raise ValueError("Request must include parsed AI_SEMANTIC_REVIEW.json as review")
                result = apply_semantic_review_to_staging(
                    ctx, STAGING_ROOT, review, cfg["repo_folder"], TRANSFER_ROOT
                )
                self._send_json({"status": "PASS", "result": result})
                return
            self._send_json({"error": "Unknown API endpoint"}, 404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 400)


def main():
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    version = (HERE / "VERSION").read_text(encoding="utf-8").strip()
    print(f"Curriculum Builder Pilot v{version}")
    print(f"Project root: {GITHUB_ROOT}")
    print(f"Runtime staging: {STAGING_ROOT}")
    print(f"Downloads: {DOWNLOADS}")
    print("Network policy: local project repos only")
    print("Git actions: NONE")
    print("Bank Map: simple Run Audit -> AI only if needed -> Finish Audit from Downloads")
    print("Complete Bank: Prepare -> AI content -> Finish Complete Bank from Downloads")
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
