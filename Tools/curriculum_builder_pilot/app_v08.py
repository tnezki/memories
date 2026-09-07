from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
APP_HOME = Path.home() / "Documents" / "Curriculum Builder"
WORKSPACE_ROOT = APP_HOME / "Workspace"
AI_EXCHANGE_ROOT = APP_HOME / "AI Exchange"
RUNTIME_ROOT = APP_HOME / "Runtime" / "app_python"
DOWNLOADS = Path.home() / "Downloads"
TRANSFER_ROOT_DEFAULT = DOWNLOADS / "_github_transfers"
CONVENIENCE_LAUNCHER = Path.home() / "Applications" / "Curriculum Builder.command"


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
    runtime_python = RUNTIME_ROOT / "bin" / "python3"
    if not runtime_python.is_file():
        RUNTIME_ROOT.parent.mkdir(parents=True, exist_ok=True)
        print("Curriculum Builder: creating one-time local runtime in Documents/Curriculum Builder...")
        if subprocess.run([str(current), "-m", "venv", str(RUNTIME_ROOT)]).returncode != 0:
            raise RuntimeError("Could not create the Curriculum Builder Python runtime.")
    if not _graphics_ready(runtime_python):
        print("Curriculum Builder: installing matplotlib/numpy into its local runtime (one time)...")
        proc = subprocess.run([
            str(runtime_python), "-m", "pip", "install",
            "--disable-pip-version-check", "--only-binary=:all:",
            "numpy", "matplotlib",
        ])
        if proc.returncode != 0:
            raise RuntimeError("Could not install matplotlib/numpy into the Curriculum Builder runtime.")
    if not _graphics_ready(runtime_python):
        raise RuntimeError("Curriculum Builder runtime exists but cannot import matplotlib/numpy.")
    env = os.environ.copy()
    env["CURRICULUM_BUILDER_RUNTIME"] = "managed-v090"
    os.execve(str(runtime_python), [str(runtime_python), str(HERE / "app_v08.py")], env)


def _ensure_convenience_launcher() -> None:
    CONVENIENCE_LAUNCHER.parent.mkdir(parents=True, exist_ok=True)
    target = HERE / "Start Curriculum Builder.command"
    text = f'''#!/bin/bash\nset -e\nexec "{target}"\n'''
    if not CONVENIENCE_LAUNCHER.is_file() or CONVENIENCE_LAUNCHER.read_text(encoding="utf-8", errors="ignore") != text:
        CONVENIENCE_LAUNCHER.write_text(text, encoding="utf-8")
        CONVENIENCE_LAUNCHER.chmod(0o755)


def _prune_app_owned(days: int = 14) -> int:
    cutoff = time.time() - days * 86400
    removed = 0
    for parent in (WORKSPACE_ROOT / "full_pipeline", WORKSPACE_ROOT / "notes_pipeline", AI_EXCHANGE_ROOT / "Archive"):
        if not parent.is_dir():
            continue
        for path in list(parent.rglob("*")):
            if not path.is_dir() or path.name == "Current":
                continue
            try:
                if path.stat().st_mtime < cutoff and not any(p == AI_EXCHANGE_ROOT / "Current" for p in path.parents):
                    shutil.rmtree(path)
                    removed += 1
            except Exception:
                pass
    return removed


def _ensure_transfer_bridge(transfer_root: Path) -> dict:
    tools = transfer_root / "_tools"
    github_helper = tools / "apply_curriculum_transfers.py"
    source = HERE / "support" / "apply_builder_ai_results.py"
    dest = tools / "apply_builder_ai_results.py"
    command = transfer_root / "Apply Curriculum Transfers.command"
    if not source.is_file():
        return {"ready": False, "detail": f"Builder AI-result importer source is missing: {source}", "command": str(command)}
    if not github_helper.is_file():
        return {"ready": False, "detail": f"Existing GitHub transfer helper is missing: {github_helper}", "command": str(command)}
    tools.mkdir(parents=True, exist_ok=True)
    if not dest.is_file() or dest.read_bytes() != source.read_bytes():
        shutil.copy2(source, dest)

    script = '''#!/bin/bash
set -e
ROOT="$HOME/Downloads/_github_transfers"
echo "=== Curriculum Builder AI result packages ==="
/usr/bin/python3 "$ROOT/_tools/apply_builder_ai_results.py"
echo
echo "=== Curriculum GitHub transfers ==="
/usr/bin/python3 "$ROOT/_tools/apply_curriculum_transfers.py"
echo
echo "Transfer processing complete. Review GitHub Desktop for any repository changes."
echo "Press Return to close."
read
'''
    if not command.is_file() or command.read_text(encoding="utf-8", errors="ignore") != script:
        command.write_text(script, encoding="utf-8")
    command.chmod(0o755)

    proc = subprocess.run(
        ["/usr/bin/python3", str(dest), "--self-test"],
        text=True,
        capture_output=True,
        timeout=30,
    )
    ready = proc.returncode == 0 and "SELF_TEST: PASS" in proc.stdout
    detail = proc.stdout.strip() if ready else (proc.stderr.strip() or proc.stdout.strip() or "self-test failed")
    return {"ready": ready, "detail": detail, "command": str(command), "importer": str(dest)}


_bootstrap_python_runtime()
APP_HOME.mkdir(parents=True, exist_ok=True)
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
AI_EXCHANGE_ROOT.mkdir(parents=True, exist_ok=True)
_ensure_convenience_launcher()
_prune_app_owned(14)

from core.authorities import make_context
from core.full_pipeline_v081 import continue_full_pipeline, start_full_pipeline
from core.notes_pipeline_v09 import continue_notes_pipeline, start_notes_pipeline
from core.git_snapshot import read_head_sha

STATIC = HERE / "static"
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
GITHUB_ROOT = Path(os.environ.get("CURRICULUM_GITHUB_ROOT", CONFIG["github_root"])).expanduser()
STAGING_ROOT = Path(os.environ.get("CURRICULUM_BUILDER_STAGING", str(WORKSPACE_ROOT))).expanduser()
TRANSFER_ROOT = Path(os.environ.get("CURRICULUM_TRANSFER_ROOT", str(TRANSFER_ROOT_DEFAULT))).expanduser()
HOST = CONFIG.get("host", "127.0.0.1")
PORT = int(os.environ.get("CURRICULUM_BUILDER_PORT", CONFIG.get("port", 8765)))
TRANSFER_BRIDGE = _ensure_transfer_bridge(TRANSFER_ROOT)

JOBS = [
    {
        "key": "full_bank_pipeline",
        "label": "Full Bank - Map -> Audit -> Bank -> Audit",
        "purpose": "Fresh staged Bank Map and Complete Bank with one AI handoff, local audits, and one final GitHub transfer ZIP.",
    },
    {
        "key": "notes_build",
        "label": "Build Notes",
        "purpose": "Build student + teacher Algebra Notes from the complete current Bank, exact Assessment Plan, canonical Notes template, and one AI content handoff.",
    },
]


def _json_bytes(obj) -> bytes:
    return json.dumps(obj, indent=2).encode("utf-8")


def _course_config(name: str):
    course = CONFIG.get("courses", {}).get(name)
    if not course:
        raise ValueError(f"Unsupported pilot course: {name}")
    return course


def _archive_legacy_downloads() -> dict:
    archive = APP_HOME / "Legacy Archive" / time.strftime("%Y%m%d-%H%M%S")
    archive.mkdir(parents=True, exist_ok=True)
    moved = []
    patterns = [
        "AI_HANDOFF_*.zip",
        "AI_MAP_CONTENT*.json",
        "AI_BANK_CONTENT*.json",
        "AI_SEMANTIC_REVIEW*.json",
        "AI_FULL_BANK_RESULT*.json",
        "AI_NOTES_RESULT*.json",
    ]
    for pattern in patterns:
        for path in DOWNLOADS.glob(pattern):
            if not path.is_file():
                continue
            dst = archive / path.name
            if dst.exists():
                dst = archive / f"{path.stem}_{int(time.time())}{path.suffix}"
            shutil.move(str(path), str(dst))
            moved.append(path.name)
    old_root = DOWNLOADS / "_curriculum_builder_pilot"
    if old_root.exists():
        dst = archive / "_curriculum_builder_pilot"
        shutil.move(str(old_root), str(dst))
        moved.append("_curriculum_builder_pilot/")
    if not moved:
        try:
            archive.rmdir()
        except Exception:
            pass
    return {"moved": moved, "archive": str(archive) if moved else None}


class Handler(BaseHTTPRequestHandler):
    server_version = "CurriculumBuilder/0.9.0"

    def log_message(self, fmt, *args):
        sys.stdout.write("[builder] " + fmt % args + "\n")

    def _send_json(self, obj, status=200):
        body = _json_bytes(obj)
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
                "workspace_root": str(STAGING_ROOT),
                "ai_exchange_root": str(AI_EXCHANGE_ROOT),
                "transfer_root": str(TRANSFER_ROOT),
                "downloads": str(DOWNLOADS),
                "launcher": str(CONVENIENCE_LAUNCHER),
                "python_executable": sys.executable,
                "graphics_runtime_ready": _graphics_ready(Path(sys.executable)),
                "transfer_bridge_ready": bool(TRANSFER_BRIDGE.get("ready")),
                "transfer_bridge_detail": TRANSFER_BRIDGE.get("detail"),
                "transfer_command": TRANSFER_BRIDGE.get("command"),
                "memories_exists": memories.is_dir(),
                "algebra_exists": algebra.is_dir(),
                "memories_head": read_head_sha(memories),
                "algebra_head": read_head_sha(algebra),
                "courses": CONFIG.get("courses", {}),
                "jobs": JOBS,
                "network_policy": "LOCAL PROJECT SOURCES ONLY",
                "git_policy": "NO GIT COMMANDS / NO GITHUB WRITES",
                "ai_round_trips_normal": 1,
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
            cfg = _course_config(course)
            if unit < 1 or unit > int(cfg["units"]):
                raise ValueError(f"Unit out of range: {unit}")
            ctx = make_context(GITHUB_ROOT, cfg["repo_folder"], course, unit)

            if self.path == "/api/start-full-bank-pipeline":
                result = start_full_pipeline(ctx, STAGING_ROOT, AI_EXCHANGE_ROOT)
                self._send_json(result, 200 if result.get("status") != "BLOCKED" else 409)
                return
            if self.path == "/api/continue-full-bank-pipeline":
                result = continue_full_pipeline(ctx, STAGING_ROOT, AI_EXCHANGE_ROOT, DOWNLOADS, TRANSFER_ROOT)
                self._send_json(result)
                return
            if self.path == "/api/start-notes-pipeline":
                result = start_notes_pipeline(ctx, STAGING_ROOT, AI_EXCHANGE_ROOT)
                self._send_json(result, 200 if result.get("status") != "BLOCKED" else 409)
                return
            if self.path == "/api/continue-notes-pipeline":
                result = continue_notes_pipeline(ctx, STAGING_ROOT, AI_EXCHANGE_ROOT, TRANSFER_ROOT)
                self._send_json(result)
                return
            if self.path == "/api/reveal-ai-exchange":
                folder = AI_EXCHANGE_ROOT / "Current" / "algebra_1" / f"unit{unit}"
                folder.mkdir(parents=True, exist_ok=True)
                if sys.platform == "darwin":
                    subprocess.run(["open", str(folder)], check=False)
                self._send_json({"status": "PASS", "folder": str(folder)})
                return
            if self.path == "/api/reveal-transfer-inbox":
                TRANSFER_ROOT.mkdir(parents=True, exist_ok=True)
                if sys.platform == "darwin":
                    subprocess.run(["open", str(TRANSFER_ROOT)], check=False)
                self._send_json({"status": "PASS", "folder": str(TRANSFER_ROOT)})
                return
            if self.path == "/api/archive-legacy-downloads":
                self._send_json({"status": "PASS", **_archive_legacy_downloads()})
                return
            self._send_json({"error": "Unknown API endpoint"}, 404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 400)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    version = (HERE / "VERSION").read_text(encoding="utf-8").strip()
    print(f"Curriculum Builder v{version}")
    print(f"GitHub root: {GITHUB_ROOT}")
    print(f"Workspace: {STAGING_ROOT}")
    print(f"AI Exchange: {AI_EXCHANGE_ROOT}")
    print(f"Transfer inbox: {TRANSFER_ROOT}")
    print(f"Transfer bridge: {'READY' if TRANSFER_BRIDGE.get('ready') else 'NOT READY'}")
    print(f"Convenience launcher: {CONVENIENCE_LAUNCHER}")
    print("Bank: one AI handoff ZIP -> one AI result ZIP -> Apply Curriculum Transfers -> Continue -> final transfer")
    print("Notes: one AI handoff ZIP -> one Notes AI result ZIP -> Apply Curriculum Transfers -> Continue -> final Notes transfer")
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
