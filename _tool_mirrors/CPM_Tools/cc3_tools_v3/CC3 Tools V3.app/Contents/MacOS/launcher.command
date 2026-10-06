#!/bin/bash
set -u

APP_NAME="CC3 Tools V3"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RUNTIME="$ROOT/.runtime"
LOG="$RUNTIME/app_launcher.log"
mkdir -p "$RUNTIME"

{
  echo ""
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') $APP_NAME launcher ==="
  echo "ROOT=$ROOT"
  echo "PATH=$PATH"
} >> "$LOG"

PYTHON=""
if [ -x /usr/bin/python3 ] && /usr/bin/python3 --version >/dev/null 2>&1; then
  PYTHON="/usr/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
fi

if [ -z "$PYTHON" ]; then
  /usr/bin/osascript -e 'display dialog "CC3 Tools V3 needs Python 3. Open \"Open CC3 Tools V3.command\" once and allow macOS to install the required developer tools, then try the app again." with title "CC3 Tools V3" buttons {"OK"} default button "OK" with icon stop'
  echo "ERROR: python3 not available" >> "$LOG"
  exit 1
fi

echo "PYTHON=$PYTHON" >> "$LOG"
"$PYTHON" "$ROOT/app/restart_server.py" >> "$LOG" 2>&1
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  /usr/bin/osascript -e 'display dialog "CC3 Tools V3 could not start. Try \"Open CC3 Tools V3.command\" in the cc3_tools_v3 folder. A launcher log was written to .runtime/app_launcher.log." with title "CC3 Tools V3" buttons {"OK"} default button "OK" with icon stop'
  echo "ERROR: restart_server.py exited $STATUS" >> "$LOG"
fi

exit "$STATUS"
