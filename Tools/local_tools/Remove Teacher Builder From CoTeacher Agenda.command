#!/bin/bash
set -euo pipefail

printf '\nCo-Teacher Agenda Cleanup\n=========================\n\n'

python3 - <<'PY'
from pathlib import Path
from datetime import datetime
import re
import shutil

home = Path.home()
candidates = [home / "GitHub", home / "Documents" / "GitHub"]
root = next((p for p in candidates if (p / "teacher_shared").is_dir() and (p / "_algebra_teacher_tools").is_dir()), None)
if root is None:
    raise SystemExit("ERROR: Could not locate the GitHub workspace containing teacher_shared and _algebra_teacher_tools.")

generated = root / "teacher_shared" / "algebra" / "index.html"
if not generated.is_file():
    raise SystemExit(f"ERROR: Co-teacher agenda not found: {generated}")

skip_dirs = {".git", "__pycache__", "backups", "_backups", "migration_backups", "logs", "_logs", "node_modules", ".venv", "venv"}
allowed_exts = {".py", ".js", ".html", ".htm", ".txt"}

# Deliberately narrow: only the exact Teacher Practice Builder anchor.
anchor_re = re.compile(
    r'<a\b[^>]*href=["\'][^"\']*teacher_practice_builder\.html[^"\']*["\'][^>]*>\s*Teacher Practice Builder\s*</a>',
    re.IGNORECASE,
)

def remove_anchor(text: str):
    return anchor_re.subn("", text)

# Find only source files that clearly own the Shared Teacher Resources header.
source_candidates = []
tool_root = root / "_algebra_teacher_tools"
for path in tool_root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in allowed_exts:
        continue
    if any(part in skip_dirs for part in path.parts):
        continue
    try:
        if path.stat().st_size > 2_000_000:
            continue
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    if "Shared Teacher Resources" in raw and "teacher_practice_builder.html" in raw:
        source_candidates.append(path)

if len(source_candidates) > 4:
    raise SystemExit(
        "ERROR: Found more co-teacher agenda source candidates than expected. Nothing changed.\n" +
        "\n".join(str(p) for p in source_candidates)
    )

targets = [generated] + source_candidates
changes = []
prepared = []
for path in targets:
    raw = path.read_text(encoding="utf-8")
    updated, count = remove_anchor(raw)
    if count:
        prepared.append((path, raw, updated, count))

if not any(path == generated for path, *_ in prepared):
    raise SystemExit("ERROR: Teacher Practice Builder was not found in the current co-teacher agenda. Nothing changed.")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_root = root / "_curriculum_transfers" / "backups" / f"coteacher_agenda_teacher_builder_{stamp}"

for path, raw, updated, count in prepared:
    rel = path.resolve().relative_to(root.resolve())
    backup = backup_root / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")
    changes.append((rel.as_posix(), count))

print("SUCCESS: Removed Teacher Practice Builder from the shared co-teacher agenda.")
for rel, count in changes:
    print(f"  UPDATED: {rel} ({count} link removal{'s' if count != 1 else ''})")
print(f"Backups: {backup_root}")
print("No other buttons or agenda content were changed.")
PY

status=$?
if [ "$status" -eq 0 ]; then
  printf '\nDone. Refresh the co-teacher agenda locally. After review, use your normal Commit + Push All Repos when ready.\n\n'
fi

printf 'Press Return to close...'
read -r _
