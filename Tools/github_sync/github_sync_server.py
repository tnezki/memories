#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import socket
import subprocess
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8771
TOOL_DIR = Path(__file__).resolve().parent
REPOS = ["memories", "algebra", "physics", "apcalc", "teacher_shared"]


def detect_root() -> Path | None:
    env = os.environ.get("GITHUB_ROOT", "").strip()
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend([Path.home() / "GitHub", Path.home() / "Documents" / "GitHub"])
    for p in candidates:
        if p.is_dir() and (p / "memories").exists():
            return p.resolve()
    return None


ROOT = detect_root()


def run_text(args: list[str], cwd: Path | None = None) -> str:
    try:
        cp = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=4, check=False)
        return cp.stdout.strip()
    except Exception:
        return ""


def repo_status(name: str) -> dict[str, str | bool]:
    if ROOT is None:
        return {"name": name, "exists": False, "branch": "", "state": "Workspace missing", "detail": ""}
    repo = ROOT / name
    if not (repo / ".git").exists():
        return {"name": name, "exists": False, "branch": "", "state": "Missing", "detail": str(repo)}

    branch = run_text(["/usr/bin/git", "rev-parse", "--abbrev-ref", "HEAD"], repo) or "?"
    short = run_text(["/usr/bin/git", "status", "--porcelain"], repo)
    dirty = bool(short)

    ahead = behind = 0
    counts = run_text(["/usr/bin/git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"], repo)
    if counts:
        try:
            a, b = counts.split()[:2]
            ahead, behind = int(a), int(b)
        except Exception:
            pass

    if dirty:
        state = "Changes"
    elif ahead and behind:
        state = f"Ahead {ahead} · Behind {behind}"
    elif ahead:
        state = f"Ahead {ahead}"
    elif behind:
        state = f"Behind {behind}"
    else:
        state = "Clean"

    return {
        "name": name,
        "exists": True,
        "branch": branch,
        "state": state,
        "detail": "Local changes present" if dirty else "No local changes",
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
    }


def open_terminal_action(action: str) -> str:
    runner = TOOL_DIR / "Run GitHub Sync.command"
    if not runner.exists():
        return "GitHub Sync runner is missing."
    quoted_runner = str(runner).replace("'", "'\\''")
    quoted_action = action.replace("'", "'\\''")
    cmd = f"'{quoted_runner}' '{quoted_action}'"
    script = f'''
tell application "Terminal"
  activate
  do script {cmd!r}
end tell
'''
    subprocess.run(["/usr/bin/osascript", "-e", script], check=False)
    labels = {
        "pull": "Pull All Repos",
        "commit": "Commit All Repos",
        "push": "Push All Repos",
        "commit-push": "Commit + Push All Repos",
    }
    return f"Opened Terminal for {labels.get(action, action)}."


def open_github_desktop() -> str:
    subprocess.run(["/usr/bin/open", "-a", "GitHub Desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return "Opened GitHub Desktop."


def page(message: str = "") -> str:
    statuses = [repo_status(name) for name in REPOS]
    rows = []
    for s in statuses:
        state = str(s.get("state", ""))
        cls = "clean"
        if state == "Changes":
            cls = "changes"
        elif state.startswith("Ahead"):
            cls = "ahead"
        elif state.startswith("Behind"):
            cls = "behind"
        elif state in {"Missing", "Workspace missing"}:
            cls = "missing"
        rows.append(
            f'<div class="repo"><div><strong>{html.escape(str(s["name"]))}</strong><span>{html.escape(str(s.get("branch", "")))}</span></div>'
            f'<b class="badge {cls}">{html.escape(state)}</b></div>'
        )
    msg = f'<div class="message">{html.escape(message)}</div>' if message else ""
    root_text = html.escape(str(ROOT)) if ROOT else "Workspace not found"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub Sync</title>
<style>
:root{{--navy:#173f73;--blue:#2563a7;--green:#157347;--gold:#d7a81e;--ink:#172033;--muted:#667085;--line:#d9e1ea;--bg:#eef3f8;--card:#fff;--red:#a33a3a}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);font-family:Arial,Helvetica,sans-serif;color:var(--ink)}}
.wrap{{max-width:980px;margin:0 auto;padding:34px 24px 46px}} header{{display:flex;align-items:center;gap:16px;margin-bottom:22px}}
.logo{{width:68px;height:68px;border-radius:18px;background:var(--navy);color:#fff;display:grid;place-items:center;font-size:38px;font-weight:900;box-shadow:0 10px 24px rgba(23,63,115,.2)}}
h1{{margin:0;color:var(--navy);font-size:42px;line-height:1}} .subtitle{{margin-top:6px;color:var(--muted);font-size:18px}}
.message{{background:#e9f1fb;border-left:5px solid var(--blue);border-radius:10px;padding:12px 14px;margin-bottom:18px;font-weight:800}}
.actions{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}
.action{{border:0;border-radius:18px;padding:22px 16px;color:white;text-align:left;cursor:pointer;min-height:150px;box-shadow:0 10px 24px rgba(24,39,75,.10)}}
.action .icon{{font-size:44px;line-height:1;display:block;margin-bottom:16px}} .action strong{{display:block;font-size:21px;margin-bottom:5px}} .action small{{font-size:13px;line-height:1.35;opacity:.92}}
.pull{{background:var(--blue)}} .commit{{background:#8a6b06}} .push{{background:var(--green)}} .combo{{background:var(--navy)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 8px 22px rgba(24,39,75,.06)}}
.panel h2{{margin:0 0 14px;color:var(--navy)}} .repo{{display:flex;justify-content:space-between;align-items:center;padding:11px 2px;border-bottom:1px solid #edf0f4}} .repo:last-child{{border-bottom:0}}
.repo strong{{display:block;font-size:16px}} .repo span{{color:var(--muted);font-size:12px;margin-left:8px}}
.badge{{font-size:12px;border-radius:999px;padding:6px 9px}} .clean{{background:#e8f5ed;color:var(--green)}} .changes{{background:#fff3d7;color:#7b5d00}} .ahead{{background:#e8f0ff;color:#3157a8}} .behind{{background:#fbe9e9;color:var(--red)}} .missing{{background:#eee;color:#666}}
.utilities{{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}} .utility{{border:1px solid var(--navy);background:#fff;color:var(--navy);font-weight:800;border-radius:10px;padding:10px 13px;cursor:pointer}}
.footer{{margin-top:15px;color:var(--muted);font-size:12px}}
@media(max-width:800px){{.actions{{grid-template-columns:1fr 1fr}}}} @media(max-width:500px){{.actions{{grid-template-columns:1fr}}h1{{font-size:34px}}}}
</style></head><body><div class="wrap">
<header><div class="logo">↕</div><div><h1>GitHub Sync</h1><div class="subtitle">Simple controls for your curriculum repositories.</div></div></header>
{msg}
<form method="post" class="actions">
<button class="action pull" name="action" value="pull"><span class="icon">↓</span><strong>Pull</strong><small>Bring down remote changes. Blocks if a repo has local edits.</small></button>
<button class="action commit" name="action" value="commit"><span class="icon">✓</span><strong>Commit</strong><small>Stage and commit local changes. No network action.</small></button>
<button class="action push" name="action" value="push"><span class="icon">↑</span><strong>Push</strong><small>Push existing local commits to GitHub. Does not auto-commit.</small></button>
<button class="action combo" name="action" value="commit-push"><span class="icon">⇅</span><strong>Commit + Push</strong><small>Safe one-click normal workflow with GitHub authentication checked first.</small></button>
</form>
<section class="panel"><h2>Repository Status</h2>{''.join(rows)}
<form method="post" class="utilities"><button class="utility" name="action" value="refresh">↻ Refresh Status</button><button class="utility" name="action" value="desktop">Open GitHub Desktop</button></form>
</section><div class="footer">Workspace: {root_text} · GitHub Sync: 127.0.0.1:{PORT}</div>
</div></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_html(self, body: str, code: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            data = b"GITHUB_SYNC_OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_html(page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace")
        action = parse_qs(body).get("action", [""])[0]
        if action in {"pull", "commit", "push", "commit-push"}:
            message = open_terminal_action(action)
        elif action == "desktop":
            message = open_github_desktop()
        else:
            message = "Status refreshed."
        self.send_html(page(message))


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
