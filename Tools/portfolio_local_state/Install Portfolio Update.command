#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ROOT="$GITHUB_ROOT/_portfolio_data"
mkdir -p "$ROOT"

choose_file() {
  local prompt="$1"
  /usr/bin/osascript <<OSA 2>/dev/null || true
try
  set f to choose file with prompt "$prompt"
  return POSIX path of f
on error number -128
  return ""
end try
OSA
}

STATE_ZIP="$(choose_file 'Choose Portfolio_State_UPDATED.zip')"
if [ -z "$STATE_ZIP" ]; then
  echo "No state ZIP selected. Nothing changed."
  exit 0
fi

META="$(/usr/bin/python3 - "$STATE_ZIP" <<'PYCODE'
import json,sys,zipfile
p=sys.argv[1]
with zipfile.ZipFile(p) as z:
    try: m=json.loads(z.read('STATE_MANIFEST.json'))
    except Exception as e: raise SystemExit('Invalid state ZIP: '+str(e))
if m.get('schema')!='portfolio-portable-state/1' or m.get('status')!='CURRENT':
    raise SystemExit('Invalid portable-state manifest schema/status')
course=str(m.get('course','')).strip(); unit=m.get('unit'); ver=m.get('state_version'); sid=str(m.get('state_id','')).strip()
if course not in {'Algebra 1','Physics','AP Calculus AB','STEM I'}: raise SystemExit('Unsupported course: '+course)
try: unit=int(unit); ver=int(ver)
except: raise SystemExit('Invalid unit/state_version')
if unit < 1 or ver < 1 or not sid: raise SystemExit('Invalid unit/state_version/state_id')
print(f'{course}\t{unit}\t{ver}\t{sid}')
PYCODE
)"
IFS=$'\t' read -r COURSE UNIT VERSION STATE_ID <<< "$META"
TARGET="$ROOT/$COURSE/unit $UNIT"
DATA="$TARGET/02 Portfolio Data"
STATE_ARCH="$DATA/State Archives"
RESULT_ARCH="$DATA/Results Archives"
mkdir -p "$TARGET/01 Evidence Inbox" "$STATE_ARCH" "$RESULT_ARCH" "$TARGET/03 Student Packets" "$TARGET/04 Class & Intervention Summaries" "$TARGET/05 PowerSchool Exports"
CURRENT="$DATA/Portfolio_State_CURRENT.zip"

if [ -f "$CURRENT" ]; then
  CURRENT_VERSION="$(/usr/bin/python3 - "$CURRENT" <<'PYCODE'
import json,sys,zipfile
try:
  with zipfile.ZipFile(sys.argv[1]) as z: print(int(json.loads(z.read('STATE_MANIFEST.json')).get('state_version',0)))
except: print(0)
PYCODE
)"
  if [ "$CURRENT_VERSION" -ge "$VERSION" ]; then
    echo "REFUSED: installed state version $CURRENT_VERSION is not older than incoming version $VERSION."
    echo "Nothing was changed."
    exit 1
  fi
fi

STAMP="$(date '+%Y-%m-%d_%H%M%S')"
if [ -f "$CURRENT" ]; then
  cp -p "$CURRENT" "$STATE_ARCH/${STAMP}_PREVIOUS_State.zip"
fi
cp -p "$STATE_ZIP" "$CURRENT"
cp -p "$STATE_ZIP" "$STATE_ARCH/${STAMP}_State_v${VERSION}.zip"
SRC_HASH="$(shasum -a 256 "$STATE_ZIP" | awk '{print $1}')"
DST_HASH="$(shasum -a 256 "$CURRENT" | awk '{print $1}')"
if [ "$SRC_HASH" != "$DST_HASH" ]; then
  echo "FAILED: state copy hash mismatch."
  exit 1
fi

echo "Installed $COURSE Unit $UNIT state v$VERSION"
echo "Current state: $CURRENT"

RESULTS_ZIP="$(choose_file 'Choose Portfolio_Results.zip, or Cancel to skip results installation')"
if [ -n "$RESULTS_ZIP" ]; then
  R_HASH="$(shasum -a 256 "$RESULTS_ZIP" | awk '{print $1}')"
  cp -p "$RESULTS_ZIP" "$RESULT_ARCH/${STAMP}_Portfolio_Results.zip"
  cp -p "$RESULTS_ZIP" "$RESULT_ARCH/Latest Portfolio Results.zip"
  L_HASH="$(shasum -a 256 "$RESULT_ARCH/Latest Portfolio Results.zip" | awk '{print $1}')"
  if [ "$R_HASH" != "$L_HASH" ]; then
    echo "FAILED: results copy hash mismatch."
    exit 1
  fi
  echo "Results archived and Latest Portfolio Results.zip updated."
fi

echo
echo "Done. Copy the whole _portfolio_data folder to USB at the end of the day."
echo
read -r -p "Press Return to close..." _
