#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

PORTS = (8767, 8768, 8769)

HOSTED = {
    "algebra": "https://tnezki.github.io/teacher_shared/algebra/",
    "physics": "https://tnezki.github.io/teacher_shared/physics/",
    "calc": "https://tnezki.github.io/teacher_shared/calc/",
}

LOCAL_TARGETS = {
    "algebra": {
        "http://127.0.0.1:8767/shared/algebra/index.html",
        "http://127.0.0.1:8767/shared/algebra/",
        "/shared/algebra/index.html",
        "/shared/algebra/",
        "shared/algebra/index.html",
        "shared/algebra/",
    },
    "physics": {
        "http://127.0.0.1:8768/shared/physics/index.html",
        "http://127.0.0.1:8768/shared/physics/",
        "/shared/physics/index.html",
        "/shared/physics/",
        "shared/physics/index.html",
        "shared/physics/",
    },
    "calc": {
        "http://127.0.0.1:8769/shared/calc/index.html",
        "http://127.0.0.1:8769/shared/calc/",
        "/shared/calc/index.html",
        "/shared/calc/",
        "shared/calc/index.html",
        "shared/calc/",
        "http://127.0.0.1:8769/shared/apcalc/index.html",
        "http://127.0.0.1:8769/shared/apcalc/",
        "/shared/apcalc/index.html",
        "/shared/apcalc/",
        "shared/apcalc/index.html",
        "shared/apcalc/",
    },
}

SKIP_DIRS = {
    ".git", "__pycache__", "logs", "_logs", "backups", "_backups",
    "migration_backups", "node_modules", ".venv", "venv",
}

ANCHOR_RE = re.compile(
    r'(<a\b[^>]*?\bhref\s*=\s*)(["\'])([^"\']*)(\2)([^>]*>.*?</a>)',
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def detect_root() -> Path:
    env = os.environ.get("GITHUB_ROOT", "").strip()
    candidates = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend([Path.home() / "GitHub", Path.home() / "Documents" / "GitHub"])
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "memories").exists():
            return candidate.resolve()
    raise RuntimeError("Could not locate the GitHub workspace root.")


def candidate_files(root: Path):
    for tool_root in (
        root / "_algebra_teacher_tools",
        root / "_physics_teacher_tools",
        root / "_apcalc_teacher_tools",
    ):
        if not tool_root.is_dir():
            continue
        for path in tool_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            yield path


def _anchor_text(fragment: str) -> str:
    return " ".join(TAG_RE.sub(" ", fragment).split()).lower()


def patch_hosted_links(raw: str) -> tuple[str, int]:
    changes = 0

    def sub(match: re.Match) -> str:
        nonlocal changes
        text = _anchor_text(match.group(5))
        if not any(label in text for label in ("co-teacher agenda", "coteacher agenda", "co teacher agenda")):
            return match.group(0)

        href = match.group(3).strip()
        for course, targets in LOCAL_TARGETS.items():
            if href in targets:
                changes += 1
                return match.group(1) + match.group(2) + HOSTED[course] + match.group(4) + match.group(5)
        return match.group(0)

    return ANCHOR_RE.sub(sub, raw), changes


def backup_and_write(root: Path, path: Path, updated: str, backup_root: Path) -> None:
    rel = path.resolve().relative_to(root.resolve())
    backup = backup_root / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")


def listener_pids(port: int) -> list[int]:
    result = subprocess.run(
        ["/usr/sbin/lsof", "-tiTCP:%d" % port, "-sTCP:LISTEN"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    out = []
    for token in result.stdout.split():
        try:
            out.append(int(token))
        except ValueError:
            pass
    return out


def stop_planners() -> None:
    pids = sorted(set(pid for port in PORTS for pid in listener_pids(port)))
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + 3
    while time.time() < deadline:
        alive = []
        for pid in pids:
            try:
                os.kill(pid, 0)
                alive.append(pid)
            except ProcessLookupError:
                pass
        if not alive:
            break
        time.sleep(0.1)


def start_planners(root: Path) -> bool:
    runtime = root / "_algebra_teacher_tools" / "runtime" / "Start Teacher Tools Runtime.command"
    if not runtime.exists():
        print(f"Planner runtime launcher not found: {runtime}")
        return False
    log_dir = root / "_algebra_teacher_tools" / "runtime" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / "planner_owner_link_restart.log"
    with log.open("ab") as handle:
        subprocess.Popen(
            ["/bin/bash", str(runtime)],
            stdout=handle,
            stderr=handle,
            start_new_session=True,
        )
    deadline = time.time() + 30
    while time.time() < deadline:
        if all(listener_pids(p) for p in PORTS):
            return True
        time.sleep(0.5)
    return all(listener_pids(p) for p in PORTS)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely update only Co-Teacher Agenda href targets. This script never edits Planner UI/layout."
    )
    parser.add_argument("--restart-if-changed", action="store_true")
    args = parser.parse_args()

    root = detect_root()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = root / "_curriculum_transfers" / "backups" / f"planner_coteacher_links_{stamp}"

    staged: list[tuple[Path, str, int]] = []
    for path in candidate_files(root):
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated, count = patch_hosted_links(raw)
        if count and updated != raw:
            staged.append((path, updated, count))

    if not staged:
        print("Planner hosted Co-Teacher Agenda links already current. No files changed.")
        return 0

    total = 0
    for path, updated, count in staged:
        backup_and_write(root, path, updated, backup_root)
        total += count
        print(f"UPDATED: {path}")

    print(f"Updated {len(staged)} file(s); {total} Co-Teacher Agenda link change(s).")
    print(f"Backups: {backup_root}")

    if args.restart_if_changed:
        print("Restarting Planner services on ports 8767-8769...")
        stop_planners()
        if not start_planners(root):
            print("WARNING: Planner runtime did not fully return. Check the runtime log.")
            return 2
        print("Planner runtime restarted successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
