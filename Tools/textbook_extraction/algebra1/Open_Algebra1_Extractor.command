#!/bin/bash
# Extract Algebra 1 CPM textbook cards locally. Never publish proprietary assets.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
printf '\nCore Connections Algebra 1 — Canonical Card Extraction\n======================================================\n\n'
SOURCE="${1:-}"
if [ -z "$SOURCE" ] && command -v osascript >/dev/null 2>&1; then
  SOURCE="$(osascript -e 'POSIX path of (choose folder with prompt "Select your local cc_algebra textbook folder (containing ch01 through ch11 and appendix_a)")' 2>/dev/null || true)"
fi
if [ -z "$SOURCE" ]; then
  printf 'Path to your local cc_algebra source folder (drag folder here, then press Return): '
  IFS= read -r SOURCE
fi
SOURCE="${SOURCE%\"}"; SOURCE="${SOURCE#\"}"
SOURCE="${SOURCE%\'}"; SOURCE="${SOURCE#\'}"
if [ -z "$SOURCE" ] || [ ! -d "$SOURCE" ]; then
  printf '\nNo valid source folder selected. Nothing changed.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf '\nPython 3 was not found. Nothing changed.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
python3 "$HERE/algebra1_extract.py" --source "$SOURCE" --replace-output
STATUS=$?
if [ "$STATUS" -eq 0 ]; then
  printf '\nSOURCE INVENTORY AND EXTRACTION CHECKS: PASS\n'
else
  printf '\nEXTRACTION OR SOURCE INVENTORY REQUIRES REVIEW (exit %s)\n' "$STATUS"
fi
REPORT="$HOME/Documents/CPM_Private_Extracted/algebra1_canonical_cards_v1/QA_REPORT.md"
if [ -f "$REPORT" ] && command -v open >/dev/null 2>&1; then
  open -a TextEdit "$REPORT" >/dev/null 2>&1 || true
fi
printf '\nReport: %s\n' "$REPORT"
printf 'Press Return to close: '; IFS= read -r _
exit "$STATUS"
