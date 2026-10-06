#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
SOURCE="$GITHUB_ROOT/CPM_Tools/cc3_tools_v3"
DEST="$MEMORIES_ROOT/_tool_mirrors/CPM_Tools/cc3_tools_v3"

if [ ! -d "$SOURCE" ]; then
  echo "ERROR: CPM Tools V3 folder not found: $SOURCE"
  exit 1
fi

mkdir -p "$DEST"
SAFE_PATHS=(
  "index.html" "README.txt" "QA_REPORT.json" "Open CC3 Tools V3.command"
  "app" "builder" "creation" "assessments" "assessment-plans" "visuals" "banks"
  "saved/index.html" "reader/index.html" "reader/assets"
)

rm -rf "$DEST"
mkdir -p "$DEST"
for rel in "${SAFE_PATHS[@]}"; do
  src="$SOURCE/$rel"
  [ -e "$src" ] || continue
  mkdir -p "$DEST/$(dirname "$rel")"
  if [ -d "$src" ]; then
    rsync -a \
      --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' \
      --exclude='.runtime/' --exclude='library/' --exclude='imports/' --exclude='exports/' \
      "$src/" "$DEST/$rel/"
  else
    cp "$src" "$DEST/$rel"
  fi
done

cat > "$(dirname "$DEST")/README.md" <<'README'
# CPM Tools Source Mirror

Code-only reference mirror of local `CPM_Tools/cc3_tools_v3`. Runtime/library/student or teacher-generated data is intentionally excluded.
README

python3 - "$(dirname "$DEST")" <<'PY'
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1])
items=[]
for p in sorted(root.rglob('*')):
    if p.is_file() and p.name!='MIRROR_MANIFEST.json':
        b=p.read_bytes(); items.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(root/'MIRROR_MANIFEST.json').write_text(json.dumps({'schema_version':1,'source':'CPM_Tools/cc3_tools_v3','destination':'memories/_tool_mirrors/CPM_Tools','file_count':len(items),'files':items},indent=2)+'\n')
PY

echo
printf '%s\n' "CPM Tools mirror refreshed:" "  $MEMORIES_ROOT/_tool_mirrors/CPM_Tools" "" "Next: GitHub Sync -> Commit + Push."
if [ "${1:-}" != "--no-prompt" ]; then
  read -r -p "Press Return to close..." _
fi
