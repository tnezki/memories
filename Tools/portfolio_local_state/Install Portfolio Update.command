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

repair_misfiled_state_results() {
  local repaired=0
  while IFS= read -r -d '' archive; do
    if /usr/bin/python3 - "$archive" <<'PYCODE' >/dev/null 2>&1
import json,sys,zipfile
p=sys.argv[1]
try:
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist())
        if 'STATE_MANIFEST.json' not in names:
            raise SystemExit(1)
        m=json.loads(z.read('STATE_MANIFEST.json'))
        if m.get('schema')!='portfolio-portable-state/1':
            raise SystemExit(1)
        if 'results_manifest.json' in names:
            raise SystemExit(1)
except Exception:
    raise SystemExit(1)
PYCODE
    then
      echo "Repairing invalid Results Archive entry: $archive"
      rm -f "$archive"
      repaired=$((repaired + 1))
    fi
  done < <(find "$ROOT" -type f -path '*/02 Portfolio Data/Results Archives/*.zip' -print0 2>/dev/null || true)
  if [ "$repaired" -gt 0 ]; then
    echo "Removed $repaired portable-state ZIP(s) that had been mistakenly archived as results."
    echo
  fi
}

read_state_meta() {
  /usr/bin/python3 - "$1" <<'PYCODE'
import json,sys,zipfile
p=sys.argv[1]
try:
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('STATE_MANIFEST.json'))
except Exception as e:
    raise SystemExit('Invalid state ZIP: '+str(e))
if m.get('schema')!='portfolio-portable-state/1' or m.get('status')!='CURRENT':
    raise SystemExit('Invalid portable-state manifest schema/status')
course=str(m.get('course','')).strip(); unit=m.get('unit'); ver=m.get('state_version'); sid=str(m.get('state_id','')).strip()
if course not in {'Algebra 1','Physics','AP Calculus AB','STEM I'}:
    raise SystemExit('Unsupported course: '+course)
try:
    unit=int(unit); ver=int(ver)
except Exception:
    raise SystemExit('Invalid unit/state_version')
if unit < 1 or ver < 1 or not sid:
    raise SystemExit('Invalid unit/state_version/state_id')
print(f'{course}\t{unit}\t{ver}\t{sid}')
PYCODE
}

read_results_meta() {
  /usr/bin/python3 - "$1" <<'PYCODE'
import json,sys,zipfile
p=sys.argv[1]
try:
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist())
        if 'STATE_MANIFEST.json' in names:
            raise SystemExit('REFUSED: selected results ZIP is a portable state ZIP, not Portfolio_Results.zip.')
        if 'results_manifest.json' not in names:
            raise SystemExit('REFUSED: selected results ZIP has no results_manifest.json.')
        m=json.loads(z.read('results_manifest.json'))
except zipfile.BadZipFile:
    raise SystemExit('REFUSED: selected results file is not a valid ZIP.')
except json.JSONDecodeError:
    raise SystemExit('REFUSED: results_manifest.json is not valid JSON.')
course=str(m.get('course','')).strip()
try:
    unit=int(m.get('unit'))
except Exception:
    raise SystemExit('REFUSED: results manifest has invalid unit.')
if course not in {'Algebra 1','Physics','AP Calculus AB','STEM I'} or unit < 1:
    raise SystemExit('REFUSED: results manifest has unsupported course/unit.')
print(f'{course}\t{unit}')
PYCODE
}

repair_misfiled_state_results

echo "Portfolio local update installer"
echo "You may install an updated state, results only, or both."
echo

STATE_ZIP="$(choose_file 'Choose Portfolio_State_UPDATED.zip, or Cancel for a results-only install')"
STATE_COURSE=""
STATE_UNIT=""
VERSION=""
STATE_ID=""
if [ -n "$STATE_ZIP" ]; then
  META="$(read_state_meta "$STATE_ZIP")"
  IFS=$'\t' read -r STATE_COURSE STATE_UNIT VERSION STATE_ID <<< "$META"
fi

RESULTS_ZIP="$(choose_file 'Choose Portfolio_Results.zip, or Cancel if there are no results to install')"
RESULTS_COURSE=""
RESULTS_UNIT=""
if [ -n "$RESULTS_ZIP" ]; then
  RMETA="$(read_results_meta "$RESULTS_ZIP")"
  IFS=$'\t' read -r RESULTS_COURSE RESULTS_UNIT <<< "$RMETA"
fi

if [ -z "$STATE_ZIP" ] && [ -z "$RESULTS_ZIP" ]; then
  echo "No state or results ZIP selected. Nothing else changed."
  exit 0
fi

if [ -n "$STATE_ZIP" ] && [ -n "$RESULTS_ZIP" ]; then
  if [ "$STATE_COURSE" != "$RESULTS_COURSE" ] || [ "$STATE_UNIT" != "$RESULTS_UNIT" ]; then
    echo "REFUSED: state and results are for different course/unit targets."
    echo "State: $STATE_COURSE Unit $STATE_UNIT"
    echo "Results: $RESULTS_COURSE Unit $RESULTS_UNIT"
    exit 1
  fi
fi

if [ -n "$STATE_ZIP" ]; then
  COURSE="$STATE_COURSE"
  UNIT="$STATE_UNIT"
else
  COURSE="$RESULTS_COURSE"
  UNIT="$RESULTS_UNIT"
fi

TARGET="$ROOT/$COURSE/unit $UNIT"
DATA="$TARGET/02 Portfolio Data"
STATE_ARCH="$DATA/State Archives"
RESULT_ARCH="$DATA/Results Archives"
mkdir -p "$TARGET/01 Evidence Inbox" "$STATE_ARCH" "$RESULT_ARCH" "$TARGET/03 Student Packets" "$TARGET/04 Class & Intervention Summaries" "$TARGET/05 PowerSchool Exports"
CURRENT="$DATA/Portfolio_State_CURRENT.zip"
STAMP="$(date '+%Y-%m-%d_%H%M%S')"

if [ -n "$STATE_ZIP" ]; then
  if [ -f "$CURRENT" ]; then
    CURRENT_VERSION="$(/usr/bin/python3 - "$CURRENT" <<'PYCODE'
import json,sys,zipfile
try:
  with zipfile.ZipFile(sys.argv[1]) as z:
    print(int(json.loads(z.read('STATE_MANIFEST.json')).get('state_version',0)))
except Exception:
  print(0)
PYCODE
)"
    if [ "$CURRENT_VERSION" -ge "$VERSION" ]; then
      echo "REFUSED: installed state version $CURRENT_VERSION is not older than incoming version $VERSION."
      echo "Nothing was changed by this install."
      exit 1
    fi
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
fi

if [ -n "$RESULTS_ZIP" ]; then
  if [ ! -f "$CURRENT" ]; then
    echo "REFUSED: results-only installation requires an existing Portfolio_State_CURRENT.zip for $COURSE Unit $UNIT."
    exit 1
  fi
  /usr/bin/python3 - "$CURRENT" "$COURSE" "$UNIT" <<'PYCODE'
import json,sys,zipfile
p,expected_course,expected_unit=sys.argv[1],sys.argv[2],int(sys.argv[3])
try:
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('STATE_MANIFEST.json'))
except Exception as e:
    raise SystemExit('REFUSED: existing current state is invalid: '+str(e))
if m.get('schema')!='portfolio-portable-state/1' or m.get('status')!='CURRENT':
    raise SystemExit('REFUSED: existing current state has invalid schema/status.')
if str(m.get('course','')).strip()!=expected_course or int(m.get('unit'))!=expected_unit:
    raise SystemExit('REFUSED: existing current state course/unit does not match results target.')
PYCODE
  R_HASH="$(shasum -a 256 "$RESULTS_ZIP" | awk '{print $1}')"
  cp -p "$RESULTS_ZIP" "$RESULT_ARCH/${STAMP}_Portfolio_Results.zip"
  cp -p "$RESULTS_ZIP" "$RESULT_ARCH/Latest Portfolio Results.zip"
  L_HASH="$(shasum -a 256 "$RESULT_ARCH/Latest Portfolio Results.zip" | awk '{print $1}')"
  if [ "$R_HASH" != "$L_HASH" ]; then
    echo "FAILED: results copy hash mismatch."
    exit 1
  fi
  echo "Results archived and Latest Portfolio Results.zip updated for $COURSE Unit $UNIT."
elif [ -n "$STATE_ZIP" ]; then
  echo "No Portfolio results ZIP selected; results archive was not changed."
fi

echo
echo "Done. Copy the whole _portfolio_data folder to USB at the end of the day."
echo
read -r -p "Press Return to close..." _
