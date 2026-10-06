#!/bin/bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
LOG="$ROOT/.runtime/app_launcher.log"
mkdir -p "$ROOT/.runtime"
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') Algebra 1 Tools launcher ==="
  echo "ROOT=$ROOT"
  echo "PYTHON=/usr/bin/python3"
} >> "$LOG"
if [ ! -x /usr/bin/python3 ]; then
  /usr/bin/osascript -e 'display alert "Algebra 1 Tools" message "Python 3 is not available on this Mac. Open the fallback command once to install the required Apple component." as critical'
  exit 1
fi
/usr/bin/python3 "$ROOT/app/restart_server.py" >> "$LOG" 2>&1
STATUS=$?
if [ "$STATUS" -ne 0 ]; then
  /usr/bin/osascript -e 'display alert "Algebra 1 Tools" message "Algebra 1 Tools could not start. See .runtime/app_launcher.log inside the Algebra 1 Tools folder." as critical'
fi
exit "$STATUS"
