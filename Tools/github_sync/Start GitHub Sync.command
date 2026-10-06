#!/bin/bash
set -e
BASE="$(cd "$(dirname "$0")" && pwd)"
SERVER="$BASE/github_sync_server.py"
LOG="$BASE/github_sync_server.log"
if ! /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:8771/health >/dev/null 2>&1; then
  PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$SERVER" >> "$LOG" 2>&1 &
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:8771/health >/dev/null 2>&1; then
      break
    fi
    /bin/sleep 0.25
  done
fi
/usr/bin/open http://127.0.0.1:8771/
