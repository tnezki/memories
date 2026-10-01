#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import signal
import subprocess
from pathlib import Path

COURSES = {
    "physics": {
        "repo_names": {"physics", "_physics_teacher_tools"},
        "shared_path": "teacher_shared/physics/index.html",
        "shared_url": "https://tnezki.github.io/teacher_shared/physics/",
        "port": 8768,
    },
    "calc": {
        "repo_names": {"apcalc", "_apcalc_teacher_tools", "calc", "_calc_teacher_tools"},
        "shared_path": "teacher_shared/calc/index.html",
        "shared_url": "https://tnezki.github.io/teacher_shared/calc/",
        "port": 8769,
    },
}

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "backups", "_backups",
    "migration_backups", "logs", "_logs", "_processed", "_failed",
}

OWNER_MARKERS = ("Planner Editor", "Apply Changes + Update Agendas", "Current State")

GITHUB_BLOCK = '''  <div class="resource-label teacher">GitHub</div>
  <nav class="resources" aria-label="GitHub repository actions">
    <button id="gitPullBtn" type="button">Pull All Repos</button>
    <button id="gitPushBtn" type="button">Commit + Push All Repos</button>
    <button id="applyBtn" type="button" class="gold">Apply Changes + Update Agendas</button>
    <button id="undoBtn" type="button" class="secondary">Undo Changes</button>
    <button id="jumpBtn" type="button" class="secondary">Jump to Current Week</button>
  </nav>'''


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


def course_for_path(path: Path) -> str | None:
    lowered = {p.lower() for p in path.parts}
    for course, cfg in COURSES.items():
        if lowered.intersection({x.lower() for x in cfg["repo_names"]}):
            return course
    return None


def is_owner_planner(raw: str) -> bool:
    return all(marker in raw for marker in OWNER_MARKERS)


def remove_injected_fragments(raw: str) -> str:
    out = raw
    patterns = [
        r'<form\b[^>]*class=["\'][^"\']*\blocal-tools-top-sync\b[^"\']*["\'][^>]*>.*?</form>',
        r'<section\b[^>]*id=["\']local-tools-planner-controls["\'][^>]*>.*?</section>',
        r'<style\b[^>]*id=["\']local-tools-safe-planner-controls-style["\'][^>]*>.*?</style>\s*<script\b[^>]*id=["\']local-tools-safe-planner-controls["\'][^>]*>.*?</script>',
        r'<style\b[^>]*id=["\']local-tools-planner-five-controls-style["\'][^>]*>.*?</style>\s*<script\b[^>]*id=["\']local-tools-planner-five-controls["\'][^>]*>.*?</script>',
    ]
    for pattern in patterns:
        out = re.sub(pattern, "", out, flags=re.IGNORECASE | re.DOTALL)
    return out


def restore_github_block(raw: str) -> str:
    # Replace the native GitHub action nav and any immediately preceding GitHub label.
    nav_re = re.compile(
        r'(?:\s*<div\s+class=["\']resource-label\s+teacher["\']>\s*GitHub\s*</div>)?'
        r'\s*<nav\s+class=["\']resources["\']\s+aria-label=["\']GitHub repository actions["\'][^>]*>.*?</nav>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    if nav_re.search(raw):
        return nav_re.sub("\n" + GITHUB_BLOCK, raw, count=1)

    # Fallback: insert immediately after the Teacher resources nav.
    teacher_nav = re.compile(
        r'(<nav\s+class=["\']resources["\']\s+aria-label=["\']Teacher resources["\'][^>]*>.*?</nav>)',
        flags=re.IGNORECASE | re.DOTALL,
    )
    return teacher_nav.sub(r'\1\n' + GITHUB_BLOCK, raw, count=1)


def remove_editor_duplicate_controls(raw: str) -> str:
    # Only remove the legacy three-button controls block directly after the Planner Editor heading.
    pattern = re.compile(
        r'(<div\s+class=["\']section-title["\']>\s*Planner Editor[^<]*</div>)\s*'
        r'<div\s+class=["\']controls["\']>\s*'
        r'<button\b[^>]*id=["\']applyBtn["\'][^>]*>.*?</button>\s*'
        r'<button\b[^>]*id=["\']undoBtn["\'][^>]*>.*?</button>\s*'
        r'<button\b[^>]*id=["\']jumpBtn["\'][^>]*>.*?</button>\s*'
        r'</div>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub(r'\1\n', raw, count=1)


def fix_footer(raw: str, course: str) -> str:
    cfg = COURSES[course]
    desired = cfg["shared_path"]
    hosted = cfg["shared_url"]

    # Repair the known malformed footer text introduced by the bad migration.
    raw = re.sub(
        r'teacher_https://tnezki\.github\.io/teacher_shared/(?:physics|calc|apcalc)/',
        desired,
        raw,
        flags=re.IGNORECASE,
    )
    raw = re.sub(
        r'teacher_https://tnezki\.github\.io/teacher_shared/(?:physics|calc|apcalc)/index\.html',
        desired,
        raw,
        flags=re.IGNORECASE,
    )

    # Keep Co-Teacher Agenda hosted, not localhost/shared.
    raw = re.sub(
        r'(<a\b[^>]*href=["\'])(?:http://127\.0\.0\.1:\d+)?/?shared/(?:physics|calc|apcalc)(?:/index\.html|/)?(["\'][^>]*>\s*Co-Teacher Agenda\s*</a>)',
        r'\1' + hosted + r'\2',
        raw,
        flags=re.IGNORECASE,
    )
    return raw


def patch_file(path: Path, course: str) -> bool:
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    if not is_owner_planner(raw):
        return False

    out = remove_injected_fragments(raw)
    out = restore_github_block(out)
    out = remove_editor_duplicate_controls(out)
    out = fix_footer(out, course)

    # Structural checks: one of each native control and one GitHub label/nav.
    expected_ids = ["gitPullBtn", "gitPushBtn", "applyBtn", "undoBtn", "jumpBtn"]
    for ident in expected_ids:
        if len(re.findall(rf'id=["\']{re.escape(ident)}["\']', out, flags=re.IGNORECASE)) != 1:
            raise RuntimeError(f"Refusing to write {path}: expected exactly one #{ident} control after repair.")
    if len(re.findall(r'>\s*GitHub\s*</div>', out, flags=re.IGNORECASE)) != 1:
        raise RuntimeError(f"Refusing to write {path}: expected exactly one GitHub heading after repair.")
    if "teacher_https://" in out:
        raise RuntimeError(f"Refusing to write {path}: malformed teacher_https footer remains.")

    if out == raw:
        return False
    path.write_text(out, encoding="utf-8")
    return True


def iter_candidates(root: Path):
    for course, cfg in COURSES.items():
        for repo_name in cfg["repo_names"]:
            repo = root / repo_name
            if not repo.is_dir():
                continue
            for p in repo.rglob("*"):
                if not p.is_file() or p.suffix.lower() not in {".html", ".htm", ".py"}:
                    continue
                if any(part in SKIP_DIRS for part in p.parts):
                    continue
                yield course, p

    # Also inspect memories runtime sources, but only files that clearly identify a Physics/Calc planner.
    memories = root / "memories"
    if memories.is_dir():
        for p in memories.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".html", ".htm", ".py"}:
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            try:
                raw = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if not is_owner_planner(raw):
                continue
            low = raw.lower()
            if "8768" in low and ("physics" in low or "teacher_shared/physics" in low):
                yield "physics", p
            elif "8769" in low and ("apcalc" in low or "teacher_shared/calc" in low or "teacher_shared/apcalc" in low):
                yield "calc", p


def stop_port(port: int) -> None:
    try:
        proc = subprocess.run(
            ["/usr/sbin/lsof", "-ti", f"tcp:{port}"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return
    for token in proc.stdout.split():
        try:
            os.kill(int(token), signal.SIGTERM)
        except (ValueError, ProcessLookupError, PermissionError):
            pass


def main() -> int:
    root = detect_root()
    changed: list[Path] = []
    seen: set[Path] = set()

    for course, path in iter_candidates(root):
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if patch_file(path, course):
            changed.append(path)

    if not changed:
        print("No Physics or AP Calculus Planner source needed repair.")
        print("========== DONE ==========")
        return 0

    stop_port(COURSES["physics"]["port"])
    stop_port(COURSES["calc"]["port"])

    print("Repaired Physics/AP Calculus Planner owner pages:")
    for path in changed:
        try:
            print("  " + str(path.relative_to(root)))
        except ValueError:
            print("  " + str(path))
    print()
    print("Planner services on ports 8768/8769 were stopped so the repaired sources load cleanly next time they are opened.")
    print("========== DONE ==========")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
