#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$SCRIPT_DIR/../Resources/app"
GITHUB_ROOT="$HOME/GitHub"
PORT="8782"
URL="http://127.0.0.1:${PORT}/"
CACHE_DIR="$HOME/Library/Caches/org.tnezki.algebra-assessment-builder.owner"
LOG_DIR="$HOME/Library/Logs"
PID_FILE="$CACHE_DIR/server.pid"
LOG_FILE="$LOG_DIR/Algebra Assessment Builder.log"

mkdir -p "$CACHE_DIR" "$LOG_DIR"

# Always restart our own previous server so the Dock app uses the current installed version.
if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      kill -0 "$OLD_PID" 2>/dev/null || break
      sleep 0.1
    done
  fi
  rm -f "$PID_FILE"
fi

# Refuse to take over the port if another program owns it.
if /usr/bin/curl -fsS --max-time 1 "$URL" >/dev/null 2>&1; then
  /usr/bin/osascript -e 'display alert "Algebra Assessment Builder" message "Port 8782 is already in use by another local service. Close that service and open the Assessment Builder again." as critical'
  exit 1
fi

nohup /usr/bin/python3 "$APP_ROOT/server.py" --port "$PORT" --app-root "$APP_ROOT" --github-root "$GITHUB_ROOT" >"$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

for _ in {1..50}; do
  if /usr/bin/curl -fsS --max-time 1 "http://127.0.0.1:${PORT}/api/ping" >/dev/null 2>&1; then
    /usr/bin/open "$URL"
    exit 0
  fi
  sleep 0.1
done

/usr/bin/osascript -e 'display alert "Algebra Assessment Builder" message "The local Assessment Builder did not start. Check ~/Library/Logs/Algebra Assessment Builder.log." as critical'
exit 1
