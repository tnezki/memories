#!/bin/bash
# Geometry source-to-card extraction. Original saved CPM captures are never modified.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
printf '\nCore Connections Geometry — Private Canonical Card Extraction\n=============================================================\n\n'
SOURCE="${1:-}"
if [ -z "$SOURCE" ] && command -v osascript >/dev/null 2>&1; then
  SOURCE="$(osascript -e 'POSIX path of (choose folder with prompt "Select local Geometry textbook folder (containing ch01 through ch12)")' 2>/dev/null || true)"
fi
if [ -z "$SOURCE" ]; then
  printf 'Path to local Geometry source folder (drag the folder here and press Return): '
  IFS= read -r SOURCE
fi
SOURCE="${SOURCE%\"}"; SOURCE="${SOURCE#\"}"
SOURCE="${SOURCE%\'}"; SOURCE="${SOURCE#\'}"
if [ -z "$SOURCE" ] || [ ! -d "$SOURCE" ]; then
  printf '\nNo usable Geometry source folder selected. No files changed.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf '\nPython 3 is required but not installed. No files changed.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
python3 "$HERE/geometry_extract.py" --source "$SOURCE" --replace-output
STATUS=$?
REPORT="$HOME/Documents/CPM_Private_Extracted/geometry_canonical_cards_v1/QA_REPORT.md"
if [ "$STATUS" -eq 0 ]; then
  printf '\nEXTRACTION AND INVENTORY CHECKS: PASS\n'
else
  printf '\nEXTRACTION OR INVENTORY REQUIRES REVIEW (exit %s)\n' "$STATUS"
fi
if [ -f "$REPORT" ] && command -v open >/dev/null 2>&1; then
  open -a TextEdit "$REPORT" >/dev/null 2>&1 || true
fi
printf '\nPrivate report: %s\n' "$REPORT"
printf 'Press Return to close: '; IFS= read -r _
exit "$STATUS"
