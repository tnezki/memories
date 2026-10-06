#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
SOURCE="$GITHUB_ROOT/_algebra_teacher_tools/algebra_1_tools"
DEST="$MEMORIES_ROOT/_tool_mirrors/Algebra_1_Tools"
if [ ! -d "$SOURCE" ]; then echo "ERROR: Algebra 1 Tools folder not found: $SOURCE"; exit 1; fi
rm -rf "$DEST"; mkdir -p "$DEST"
SAFE_PATHS=("index.html" "README.txt" "COURSE_TOOL_CONTRACT.txt" "Open Algebra 1 Tools.command" "app" "assets" "shared" "assessments" "library/index.html" "library/items.json" "Algebra 1 Tools.app")
for rel in "${SAFE_PATHS[@]}"; do
  src="$SOURCE/$rel"; [ -e "$src" ] || continue
  mkdir -p "$DEST/$(dirname "$rel")"
  if [ -d "$src" ]; then
    rsync -a --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' --exclude='.runtime/' --exclude='settings.json' --exclude='*.log' "$src/" "$DEST/$rel/"
  else
    cp "$src" "$DEST/$rel"
  fi
done
python3 - "$DEST" <<'PY'
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]); items=[]
for p in sorted(root.rglob('*')):
    if p.is_file() and p.name!='MIRROR_MANIFEST.json':
        b=p.read_bytes(); items.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(root/'MIRROR_MANIFEST.json').write_text(json.dumps({'schema_version':1,'source':'_algebra_teacher_tools/algebra_1_tools','destination':'memories/_tool_mirrors/Algebra_1_Tools','file_count':len(items),'files':items},indent=2)+'\n')
PY
echo
echo "Algebra 1 Tools mirror refreshed: $DEST"
echo "Next: GitHub Sync -> Commit + Push when ready."
if [ "${1:-}" != "--no-prompt" ]; then read -r -p "Press Return to close..." _; fi
