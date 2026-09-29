#!/bin/bash
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SERVER="$TOOL_DIR/local_tools_server.py"
PID_FILE="/tmp/local_tools_${USER}.pid"
LOG_FILE="/tmp/local_tools_${USER}.log"
URL="http://127.0.0.1:8770/"

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      kill -0 "$OLD_PID" 2>/dev/null || break
      sleep 0.1
    done
  fi
  rm -f "$PID_FILE"
fi

/usr/bin/nohup /usr/bin/python3 "$SERVER" >"$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

READY=0
for _ in $(seq 1 40); do
  if /usr/bin/curl -fsS --max-time 1 "http://127.0.0.1:8770/health" 2>/dev/null | grep -q "LOCAL_TOOLS_OK"; then
    READY=1
    break
  fi
  sleep 0.25
done

if [[ "$READY" -ne 1 ]]; then
  /usr/bin/osascript -e 'display alert "Local Tools" message "The Local Tools server did not start. Check /tmp/local_tools_'$USER'.log." as critical'
  exit 1
fi

/usr/bin/open "$URL"
exit 0
