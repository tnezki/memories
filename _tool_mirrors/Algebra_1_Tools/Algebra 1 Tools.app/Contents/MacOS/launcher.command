#!/bin/bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
LOG="$ROOT/.runtime/app_launcher.log"
mkdir -p "$ROOT/.runtime"

# One-time icon cache refresh for the course-app bundle identity introduced in v0.4.
ICON_STAMP="$ROOT/.runtime/icon_v4_refresh_done"
if [ ! -f "$ICON_STAMP" ]; then
  /usr/bin/touch "$ROOT/Algebra 1 Tools.app" 2>/dev/null || true
  /usr/bin/killall Dock >/dev/null 2>&1 || true
  /usr/bin/touch "$ICON_STAMP" 2>/dev/null || true
fi

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
