#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$HERE/../../.." && pwd)"
SRC="$WORKSPACE/SCIENCE_Tools"
DST="$WORKSPACE/maps_memories/_tool_mirrors/SCIENCE_Tools"
if [[ ! -d "$SRC" || ! -d "$WORKSPACE/maps_memories" ]]; then
  echo "Science Tools mirror skipped: local Science Tools or maps_memories checkout is unavailable."
  exit 0
fi
/usr/bin/python3 - "$SRC" "$DST" <<'PYTHON'
from pathlib import Path
import sys,hashlib,json,shutil
source=Path(sys.argv[1]).resolve()
target=Path(sys.argv[2]).resolve()
assert target.as_posix().endswith('/maps_memories/_tool_mirrors/SCIENCE_Tools')
allow=(
 'README.md','Start Science Tools.command',
 'app/index.html','app/app.js','app/server.py',
 'assets/science-ui.css','assets/science-mark.svg','assets/science-icon-preview.png',
 'config/courses.json','tests/test_science_tools.py',
 'Science Tools.app/Contents/Info.plist',
 'Science Tools.app/Contents/MacOS/Science Tools.command',
 'Science Tools.app/Contents/Resources/ScienceTools.icns',
)
items=[]
for rel in allow:
    path=(source/rel).resolve()
    if not path.is_file() or not path.is_relative_to(source):
        raise SystemExit('Missing or unsafe Science Tools source: '+rel)
    data=path.read_bytes()
    # Fixed audited allowlist intentionally excludes logs, student data, exports and credentials.
    dest=target/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    items.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest={
 'schema_version':1,
 'source':'SCIENCE_Tools',
 'destination':'maps_memories/_tool_mirrors/SCIENCE_Tools',
 'content_policy':'public-code-and-assets-only; no student or staff records',
 'file_count':len(items),
 'files':items,
}
(target/'MIRROR_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Science Tools diagnostic mirror refreshed:',len(items),'safe application files.')
PYTHON
