#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
SOURCE="$GITHUB_ROOT/_algebra_teacher_tools/assessment_builder/Algebra Assessment Builder.app"
DEST="$MEMORIES_ROOT/_tool_mirrors/Algebra_Legacy_Assessment_Builder"

if [ ! -d "$SOURCE" ]; then
  echo "Algebra legacy Assessment Builder is not installed; mirror refresh skipped."
  exit 0
fi

rm -rf "$DEST"
mkdir -p "$DEST/app_source" "$DEST/launcher"

APP_SOURCE="$SOURCE/Contents/Resources/app"
if [ -d "$APP_SOURCE" ]; then
  while IFS= read -r -d '' src; do
    rel="${src#$APP_SOURCE/}"
    case "$rel" in
      .runtime/*|*/.runtime/*|__pycache__/*|*/__pycache__/*|requests/*|*/requests/*|results/*|*/results/*|outputs/*|*/outputs/*|generated/*|*/generated/*|library/*|*/library/*|saved/*|*/saved/*|runs/*|*/runs/*|checkpoint_extensions/*|*/checkpoint_extensions/*|imports/*|*/imports/*|exports/*|*/exports/*|uploads/*|*/uploads/*|temp/*|*/temp/*|tmp/*|*/tmp/*|data/*|*/data/*) continue ;;
    esac
    case "$src" in
      *.py|*.html|*.htm|*.css|*.js|*.md|*.txt)
        mkdir -p "$DEST/app_source/$(dirname "$rel")"
        cp "$src" "$DEST/app_source/$rel"
        ;;
    esac
  done < <(find "$APP_SOURCE" -type f -print0)
fi

[ -f "$SOURCE/Contents/Info.plist" ] && cp "$SOURCE/Contents/Info.plist" "$DEST/launcher/Info.plist"
if [ -d "$SOURCE/Contents/MacOS" ]; then
  find "$SOURCE/Contents/MacOS" -maxdepth 1 -type f -print0 | while IFS= read -r -d '' src; do
    case "$src" in
      *.command|*.sh|*.py) cp "$src" "$DEST/launcher/$(basename "$src")" ;;
    esac
  done
fi

cat > "$DEST/README.md" <<'README'
# Algebra Legacy Assessment Builder Mirror

Temporary code-only diagnostic mirror of the working Algebra Assessment Builder during migration into Algebra 1 Tools.

Included: application source files and launcher source needed to inspect behavior.
Excluded: runtime state, requests/results, generated outputs, saved items, imports/exports, student data, logs, caches, and other teacher-local data.

The live `_algebra_teacher_tools/assessment_builder/` folder remains authoritative until migration is complete.
README

python3 - "$DEST" <<'PY'
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]); items=[]
for p in sorted(root.rglob('*')):
    if p.is_file() and p.name!='MIRROR_MANIFEST.json':
        b=p.read_bytes()
        items.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(root/'MIRROR_MANIFEST.json').write_text(json.dumps({
    'schema_version':1,
    'source':'_algebra_teacher_tools/assessment_builder/Algebra Assessment Builder.app',
    'destination':'memories/_tool_mirrors/Algebra_Legacy_Assessment_Builder',
    'file_count':len(items),
    'files':items,
},indent=2)+'\n')
PY

echo
echo "Algebra legacy Assessment Builder mirror refreshed: $DEST"
if [ "${1:-}" != "--no-prompt" ]; then
  read -r -p "Press Return to close..." _
fi
