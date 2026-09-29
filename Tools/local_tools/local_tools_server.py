#!/usr/bin/env python3
from __future__ import annotations

import html
import os
from pathlib import Path
import socket
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8770
TOOL_DIR = Path(__file__).resolve().parent

SHARED_URLS = {
    "algebra": "https://tnezki.github.io/teacher_shared/algebra/",
    "physics": "https://tnezki.github.io/teacher_shared/physics/",
    "apcalc": "https://tnezki.github.io/teacher_shared/calc/",
    "home": "https://tnezki.github.io/teacher_shared/",
}

def detect_root() -> Path | None:
    env = os.environ.get("GITHUB_ROOT", "").strip()
    candidates = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend([Path.home() / "GitHub", Path.home() / "Documents" / "GitHub"])
    try:
        candidates.insert(0, TOOL_DIR.parents[2])
    except IndexError:
        pass
    for p in candidates:
        if p.is_dir() and (p / "memories").exists():
            return p.resolve()
    return None

ROOT = detect_root()

FIX_PLANNER_LINKS = TOOL_DIR / "fix_planner_coteacher_links.py"

def repair_planner_owner_links() -> None:
    if not FIX_PLANNER_LINKS.exists():
        return
    subprocess.run(
        ["/usr/bin/python3", str(FIX_PLANNER_LINKS), "--restart-if-changed"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def port_ready(port: int) -> bool:
    try:
        with socket.create_connection((HOST, port), timeout=0.35):
            return True
    except OSError:
        return False

def run_background(command: list[str], log_path: Path | None = None) -> None:
    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL
    handle = None
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(log_path, "ab", buffering=0)
        stdout = handle
        stderr = handle
    try:
        subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
    finally:
        if handle:
            handle.close()

def open_url(url: str) -> None:
    subprocess.Popen(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def open_terminal_command(command_path: Path, arg: str | None = None) -> None:
    parts = [str(command_path)]
    if arg:
        parts.append(arg)
    quoted = " ".join("'" + p.replace("'", "'\\''") + "'" for p in parts)
    script = f"""
tell application "Terminal"
  activate
  do script {quoted!r}
end tell
"""
    subprocess.run(["/usr/bin/osascript", "-e", script], check=False)

def ensure_planner_runtime() -> tuple[bool, str]:
    if ROOT is None:
        return False, "GitHub workspace root not found."
    runtime = ROOT / "_algebra_teacher_tools" / "runtime" / "Start Teacher Tools Runtime.command"
    if not runtime.exists():
        return False, f"Planner runtime launcher not found: {runtime}"
    log = ROOT / "_algebra_teacher_tools" / "runtime" / "logs" / "local_tools_planner_launcher.log"
    run_background(["/bin/bash", str(runtime)], log)
    return True, "Planner runtime start requested."

def wait_for_port(port: int, seconds: int = 25) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if port_ready(port):
            return True
        time.sleep(0.5)
    return False

def launch_student_data() -> str:
    if port_ready(8765):
        open_url("http://127.0.0.1:8765/")
        return "Opened Student Data Tools."
    if ROOT is None:
        return "GitHub workspace root not found."
    app = ROOT / "memories" / "Tools" / "student_data_tools" / "Student Data Tools.app"
    command = ROOT / "memories" / "Tools" / "student_data_tools" / "Start Student Data Tools.command"
    if app.exists():
        subprocess.Popen(["/usr/bin/open", str(app)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Starting Student Data Tools."
    if command.exists():
        run_background(["/bin/bash", str(command)])
        return "Starting Student Data Tools."
    return "Student Data Tools launcher was not found."

def launch_planner(port: int, label: str) -> str:
    repair_planner_owner_links()
    if not port_ready(port):
        ok, msg = ensure_planner_runtime()
        if not ok:
            return msg
        if not wait_for_port(port):
            return f"{label} Planner did not become reachable on port {port}. Check the Planner runtime log."
    open_url(f"http://127.0.0.1:{port}/")
    return f"Opened {label} Planner."

def launch_all_planners() -> str:
    repair_planner_owner_links()
    if any(not port_ready(p) for p in (8767, 8768, 8769)):
        ok, msg = ensure_planner_runtime()
        if not ok:
            return msg
        deadline = time.time() + 30
        while time.time() < deadline and any(not port_ready(p) for p in (8767, 8768, 8769)):
            time.sleep(0.5)
    for p in (8767, 8768, 8769):
        if port_ready(p):
            open_url(f"http://127.0.0.1:{p}/")
    missing = [str(p) for p in (8767, 8768, 8769) if not port_ready(p)]
    if missing:
        return "Opened reachable Planner pages. Still unavailable: " + ", ".join(missing)
    return "Opened all Planner pages."

def launch_shared(course: str) -> str:
    url = SHARED_URLS.get(course)
    if not url:
        return "Unknown hosted co-teacher agenda."
    open_url(url)
    labels = {
        "algebra": "Algebra 1",
        "physics": "Physics",
        "apcalc": "AP Calculus AB",
        "home": "Teacher Shared",
    }
    return f"Opened hosted {labels.get(course, course)} co-teacher agenda."

def launch_sync(action: str) -> str:
    runner = TOOL_DIR / "Run Local Sync.command"
    if not runner.exists():
        return "Local sync runner is missing."
    open_terminal_command(runner, action)
    return "Opened Terminal for " + ("Pull All Repos." if action == "pull" else "Commit + Push All Repos.")

def status_badge(ready: bool) -> str:
    cls = "ready" if ready else "stopped"
    word = "READY" if ready else "STOPPED"
    return f'<span class="badge {cls}">{word}</span>'

def page(message: str = "") -> str:
    root_text = str(ROOT) if ROOT else "Not found"
    msg = f'<div class="message">{html.escape(message)}</div>' if message else ""
    portfolio = status_badge(port_ready(8765))
    planner_a = status_badge(port_ready(8767))
    planner_p = status_badge(port_ready(8768))
    planner_c = status_badge(port_ready(8769))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local Tools</title>
<style>
:root{{--navy:#173f73;--blue:#245f91;--bg:#edf2f7;--card:#fff;--line:#d6e0eb;--ink:#182438;--muted:#607089;--green:#16834a;--amber:#9a6500;--gold:#d7aa36;--goldbg:#fff9e8}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);font-family:Arial,Helvetica,sans-serif;color:var(--ink)}}
.wrap{{max-width:1080px;margin:0 auto;padding:34px 28px 50px}}
header{{margin-bottom:24px}}
h1{{margin:0;color:var(--navy);font-size:46px;line-height:1}}
.subtitle{{margin:8px 0 0;color:var(--muted);font-size:20px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:24px;box-shadow:0 8px 24px rgba(23,63,115,.06)}}
.card h2{{margin:0 0 8px;color:var(--navy);font-size:30px}}
.card p{{color:var(--muted);line-height:1.45;margin:0 0 18px}}
.card.hosted{{border:2px solid var(--gold);background:var(--goldbg)}}
.actions{{display:flex;gap:10px;flex-wrap:wrap}}
button{{border:0;border-radius:10px;background:var(--blue);color:white;font-size:16px;font-weight:800;padding:12px 16px;cursor:pointer}}
button.secondary{{background:white;color:var(--navy);border:1.5px solid var(--navy)}}
button.hosted{{background:var(--navy)}}
.status-row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0 18px}}
.badge{{font-size:11px;font-weight:900;border-radius:999px;padding:5px 8px}}
.ready{{background:#eaf7ef;color:var(--green)}}
.stopped{{background:#fff5df;color:var(--amber)}}
.message{{background:#eaf1fa;border-left:5px solid var(--navy);padding:12px 14px;border-radius:10px;margin:0 0 18px;font-weight:700}}
.note{{font-size:12px;color:#6d5618;margin-top:12px}}
.footer{{margin-top:18px;color:var(--muted);font-size:12px}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}h1{{font-size:38px}}}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Local Tools</h1>
  <div class="subtitle">Student Data, local Planners, repository Sync, and hosted co-teacher agendas.</div>
</header>
{msg}
<div class="grid">
  <section class="card">
    <h2>Student Data</h2>
    <div class="status-row">Portfolio {portfolio}</div>
    <p>Open Portfolio reports, evidence tools, grading workflows, and the teacher-authorized email workflow.</p>
    <form method="post"><button name="action" value="student-data">Open Student Data Tools</button></form>
  </section>

  <section class="card">
    <h2>Planner</h2>
    <div class="status-row">Algebra {planner_a} Physics {planner_p} AP Calc {planner_c}</div>
    <p>These are your local editing Planners. If the Planner runtime is stopped, Local Tools starts it.</p>
    <form method="post" class="actions">
      <button name="action" value="planner-algebra">Algebra 1</button>
      <button name="action" value="planner-physics">Physics</button>
      <button name="action" value="planner-apcalc">AP Calculus</button>
      <button class="secondary" name="action" value="planner-all">Open All</button>
    </form>
  </section>

  <section class="card">
    <h2>Sync</h2>
    <p>Sync memories, algebra, physics, apcalc, and teacher_shared. Terminal stays visible so you can inspect every repository.</p>
    <form method="post" class="actions">
      <button class="secondary" name="action" value="sync-pull">Pull All Repos</button>
      <button name="action" value="sync-push" onclick="return confirm('Commit and push current changes in algebra, physics, apcalc, and teacher_shared?');">Commit + Push All Repos</button>
    </form>
  </section>

  <section class="card hosted">
    <h2>Co-Teacher Agendas</h2>
    <p>Hosted read-only agendas from the <b>teacher_shared</b> repository. These are the co-teacher links; the local <code>/shared/...</code> Planner routes are preview only.</p>
    <form method="post" class="actions">
      <button class="hosted" name="action" value="shared-algebra">Algebra 1</button>
      <button class="hosted" name="action" value="shared-physics">Physics</button>
      <button class="hosted" name="action" value="shared-apcalc">AP Calculus</button>
      <button class="secondary" name="action" value="shared-home">Teacher Shared Home</button>
    </form>
    <div class="note">Curriculum Transfer remains a separate Dock app.</div>
  </section>
</div>
<div class="footer">Workspace: {html.escape(root_text)} · Local Tools: 127.0.0.1:{PORT}</div>
</div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, body: str, code: int = 200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            data = b"LOCAL_TOOLS_OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self._send(page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace")
        action = parse_qs(body).get("action", [""])[0]
        if action == "student-data":
            message = launch_student_data()
        elif action == "planner-algebra":
            message = launch_planner(8767, "Algebra 1")
        elif action == "planner-physics":
            message = launch_planner(8768, "Physics")
        elif action == "planner-apcalc":
            message = launch_planner(8769, "AP Calculus AB")
        elif action == "planner-all":
            message = launch_all_planners()
        elif action == "shared-algebra":
            message = launch_shared("algebra")
        elif action == "shared-physics":
            message = launch_shared("physics")
        elif action == "shared-apcalc":
            message = launch_shared("apcalc")
        elif action == "shared-home":
            message = launch_shared("home")
        elif action == "sync-pull":
            message = launch_sync("pull")
        elif action == "sync-push":
            message = launch_sync("push")
        else:
            message = "Unknown Local Tools action."
        self._send(page(message))

if __name__ == "__main__":
    repair_planner_owner_links()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
