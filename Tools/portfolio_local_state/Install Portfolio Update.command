#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ROOT="$GITHUB_ROOT/_portfolio_data"
mkdir -p "$ROOT"

choose_mode() {
  /usr/bin/osascript <<'OSA' 2>/dev/null || true
try
  set choices to {"Updated state only", "Results only", "State + results"}
  set picked to choose from list choices with prompt "What are you installing?" with title "Portfolio Local Update"
  if picked is false then return ""
  return item 1 of picked
on error number -128
  return ""
end try
OSA
}

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

read_state_meta() {
  /usr/bin/python3 - "$1" <<'PY'
import json,sys,zipfile
p=sys.argv[1]
try:
    with zipfile.ZipFile(p) as z:m=json.loads(z.read('STATE_MANIFEST.json'))
except Exception as e: raise SystemExit('Invalid state ZIP: '+str(e))
if m.get('schema')!='portfolio-portable-state/1' or m.get('status')!='CURRENT': raise SystemExit('Invalid portable-state manifest schema/status')
course=str(m.get('course','')).strip(); unit=int(m.get('unit',0)); ver=int(m.get('state_version',0)); sid=str(m.get('state_id','')).strip()
if course not in {'Algebra 1','Physics','AP Calculus AB','STEM I'} or unit<1 or ver<1 or not sid: raise SystemExit('Invalid course/unit/state metadata')
print(f'{course}\t{unit}\t{ver}\t{sid}')
PY
}

read_results_meta() {
  /usr/bin/python3 - "$1" <<'PY'
import json,sys,zipfile
p=sys.argv[1]
try:
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist())
        if 'STATE_MANIFEST.json' in names: raise SystemExit('REFUSED: selected results ZIP is a portable state ZIP.')
        if 'results_manifest.json' not in names: raise SystemExit('REFUSED: selected results ZIP has no results_manifest.json.')
        m=json.loads(z.read('results_manifest.json'))
except zipfile.BadZipFile: raise SystemExit('REFUSED: selected results file is not a valid ZIP.')
course=str(m.get('course','')).strip(); unit=int(m.get('unit',0))
if course not in {'Algebra 1','Physics','AP Calculus AB','STEM I'} or unit<1: raise SystemExit('REFUSED: results manifest has unsupported course/unit.')
print(f'{course}\t{unit}')
PY
}

unpack_results() {
  /usr/bin/python3 - "$1" "$2" <<'PY'
import shutil,sys,tempfile,zipfile
from pathlib import Path
zip_path=Path(sys.argv[1]); unit_root=Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='portfolio_results_install_') as td:
    td=Path(td)
    with zipfile.ZipFile(zip_path) as z:z.extractall(td/'results')
    mappings=[
      (td/'results'/'student_reports', unit_root/'03 Student Packets'),
      (td/'results'/'teacher_report', unit_root/'04 Class & Intervention Summaries'),
      (td/'results'/'powerschool', unit_root/'05 PowerSchool Exports'),
    ]
    staged=[]; backups=[]
    try:
      for src,dst in mappings:
        new=dst.with_name(dst.name+'.new')
        if new.exists(): shutil.rmtree(new)
        new.mkdir(parents=True,exist_ok=True)
        if src.is_dir():
          for p in src.rglob('*'):
            if p.is_file():
              q=new/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        staged.append((new,dst))
      for new,dst in staged:
        old=dst.with_name(dst.name+'.previous')
        if old.exists(): shutil.rmtree(old)
        if dst.exists(): dst.rename(old);backups.append((old,dst))
        new.rename(dst)
      for old,_ in backups:
        if old.exists(): shutil.rmtree(old)
    except Exception:
      for new,dst in staged:
        if new.exists(): shutil.rmtree(new,ignore_errors=True)
      for old,dst in reversed(backups):
        if dst.exists(): shutil.rmtree(dst,ignore_errors=True)
        if old.exists(): old.rename(dst)
      raise
PY
}

printf '\nPortfolio local update installer\n\n'
MODE="$(choose_mode)"
if [ -z "$MODE" ]; then
  echo "Canceled. Nothing changed."
  exit 0
fi

STATE_ZIP=""; RESULTS_ZIP=""; STATE_COURSE=""; STATE_UNIT=""; VERSION=""; STATE_ID=""; RESULTS_COURSE=""; RESULTS_UNIT=""
if [ "$MODE" = "Updated state only" ] || [ "$MODE" = "State + results" ]; then
  STATE_ZIP="$(choose_file 'Choose Portfolio_State_UPDATED.zip')"
  if [ -z "$STATE_ZIP" ]; then echo "Canceled before state selection. Nothing changed."; exit 0; fi
  META="$(read_state_meta "$STATE_ZIP")"; IFS=$'\t' read -r STATE_COURSE STATE_UNIT VERSION STATE_ID <<< "$META"
fi
if [ "$MODE" = "Results only" ] || [ "$MODE" = "State + results" ]; then
  RESULTS_ZIP="$(choose_file 'Choose Portfolio_Results.zip')"
  if [ -z "$RESULTS_ZIP" ]; then echo "Canceled before results selection. Nothing changed."; exit 0; fi
  RMETA="$(read_results_meta "$RESULTS_ZIP")"; IFS=$'\t' read -r RESULTS_COURSE RESULTS_UNIT <<< "$RMETA"
fi
if [ -n "$STATE_ZIP" ] && [ -n "$RESULTS_ZIP" ]; then
  if [ "$STATE_COURSE" != "$RESULTS_COURSE" ] || [ "$STATE_UNIT" != "$RESULTS_UNIT" ]; then
    echo "REFUSED: state and results target different course/Unit."; exit 1
  fi
fi
if [ -n "$STATE_ZIP" ]; then COURSE="$STATE_COURSE"; UNIT="$STATE_UNIT"; else COURSE="$RESULTS_COURSE"; UNIT="$RESULTS_UNIT"; fi
TARGET="$ROOT/$COURSE/unit $UNIT"; DATA="$TARGET/02 Portfolio Data"; STATE_ARCH="$DATA/State Archives"; RESULT_ARCH="$DATA/Results Archives"
mkdir -p "$TARGET/01 Evidence Inbox" "$STATE_ARCH" "$RESULT_ARCH" "$TARGET/03 Student Packets" "$TARGET/04 Class & Intervention Summaries" "$TARGET/05 PowerSchool Exports" "$TARGET/06 Email Delivery"
CURRENT="$DATA/Portfolio_State_CURRENT.zip"; STAMP="$(date '+%Y-%m-%d_%H%M%S')"

if [ -n "$STATE_ZIP" ]; then
  if [ -f "$CURRENT" ]; then
    CURRENT_VERSION="$(/usr/bin/python3 - "$CURRENT" <<'PY'
import json,sys,zipfile
try:
 with zipfile.ZipFile(sys.argv[1]) as z: print(int(json.loads(z.read('STATE_MANIFEST.json')).get('state_version',0)))
except Exception: print(0)
PY
)"
    if [ "$CURRENT_VERSION" -ge "$VERSION" ]; then echo "REFUSED: installed state v$CURRENT_VERSION is not older than incoming v$VERSION."; exit 1; fi
    cp -p "$CURRENT" "$STATE_ARCH/${STAMP}_PREVIOUS_State.zip"
  fi
  cp -p "$STATE_ZIP" "$CURRENT"; cp -p "$STATE_ZIP" "$STATE_ARCH/${STAMP}_State_v${VERSION}.zip"
  [ "$(shasum -a 256 "$STATE_ZIP" | awk '{print $1}')" = "$(shasum -a 256 "$CURRENT" | awk '{print $1}')" ] || { echo "FAILED: state hash mismatch."; exit 1; }
  echo "Installed $COURSE Unit $UNIT state v$VERSION"
fi

if [ -n "$RESULTS_ZIP" ]; then
  [ -f "$CURRENT" ] || { echo "REFUSED: results installation requires existing Portfolio_State_CURRENT.zip."; exit 1; }
  cp -p "$RESULTS_ZIP" "$RESULT_ARCH/${STAMP}_Portfolio_Results.zip"; cp -p "$RESULTS_ZIP" "$RESULT_ARCH/Latest Portfolio Results.zip"
  [ "$(shasum -a 256 "$RESULTS_ZIP" | awk '{print $1}')" = "$(shasum -a 256 "$RESULT_ARCH/Latest Portfolio Results.zip" | awk '{print $1}')" ] || { echo "FAILED: results hash mismatch."; exit 1; }
  unpack_results "$RESULTS_ZIP" "$TARGET"
  echo "Installed latest results for $COURSE Unit $UNIT and refreshed folders 03-05."
fi

echo
echo "Done. Copy the whole _portfolio_data folder to USB at the end of the day."
echo
read -r -p "Press Return to close..." _
