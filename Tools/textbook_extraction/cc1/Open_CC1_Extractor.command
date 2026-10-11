#!/bin/bash
# Offline CC1 source extraction; preserves all original captures.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
printf '\nCC1 Canonical Card Extraction\n=============================\n\n'
SOURCE="${1:-}"
if [ -z "$SOURCE" ] && command -v osascript >/dev/null 2>&1; then
  SOURCE="$(osascript -e 'POSIX path of (choose folder with prompt "Select your local CC1 textbook capture folder (containing ch01 through ch09)")' 2>/dev/null || true)"
fi
if [ -z "$SOURCE" ]; then
  printf 'Path to your local CC1 source folder (drag it here, then Return): '
  IFS= read -r SOURCE
fi
SOURCE="${SOURCE%\"}"; SOURCE="${SOURCE#\"}"
SOURCE="${SOURCE%\'}"; SOURCE="${SOURCE#\'}"
if [ -z "$SOURCE" ] || [ ! -d "$SOURCE" ]; then
  printf '\nNo usable source directory selected. No changes made.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf '\nPython 3 not found. No changes made.\n'
  printf 'Press Return to close: '; IFS= read -r _
  exit 1
fi
python3 "$HERE/cc1_extract.py" --source "$SOURCE" --replace-output
STATUS=$?
if [ "$STATUS" -eq 0 ]; then
 printf '\nSOURCE INVENTORY AND EXTRACTION CHECKS: PASS\n'
else
 printf '\nSOURCE INVENTORY OR EXTRACTION CHECKS NEED REVIEW (exit %s)\n' "$STATUS"
fi
REPORT="$HOME/Documents/CPM_Private_Extracted/cc1_canonical_cards_v1/QA_REPORT.md"
if [ -f "$REPORT" ] && command -v open >/dev/null 2>&1; then
 open -a TextEdit "$REPORT" >/dev/null 2>&1 || true
fi
printf '\nReport: %s\n' "$REPORT"
printf '\nPress Return to close: '; IFS= read -r _
exit "$STATUS"
