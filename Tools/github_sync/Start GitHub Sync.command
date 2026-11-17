#!/bin/bash
set -e
BASE="$(cd "$(dirname "$0")" && pwd)"
SERVER="$BASE/github_sync_server.py"
LOG="$BASE/github_sync_server.log"
URL="http://127.0.0.1:8771/health"
EXPECTED="GITHUB_SYNC_OK_V3"
health="$(/usr/bin/curl -fsS --max-time 1 "$URL" 2>/dev/null || true)"

if [[ -n "$health" && "$health" != "$EXPECTED" ]]; then
  # Port 8771 may still be served by an earlier GitHub Sync process. Only
  # signal it if the exact server script path is in that process's command.
  pid="$(/usr/sbin/lsof -n -P -tiTCP:8771 -sTCP:LISTEN 2>/dev/null | /usr/bin/head -n 1 || true)"
  if [[ -z "$pid" ]]; then
    echo "GitHub Sync server on port 8771 could not be identified; refusing to stop it." >&2
    exit 1
  fi
  cmd="$(/bin/ps -p "$pid" -o command= 2>/dev/null || true)"
  if [[ "$cmd" != *"$SERVER"* ]]; then
    echo "Port 8771 is in use by an unexpected process; no process was stopped." >&2
    exit 1
  fi
  /bin/kill "$pid"
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if ! /usr/bin/curl -fsS --max-time 1 "$URL" >/dev/null 2>&1; then break; fi
    /bin/sleep 0.25
  done
fi

if [[ "$(/usr/bin/curl -fsS --max-time 1 "$URL" 2>/dev/null || true)" != "$EXPECTED" ]]; then
  PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$SERVER" >> "$LOG" 2>&1 &
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if [[ "$(/usr/bin/curl -fsS --max-time 1 "$URL" 2>/dev/null || true)" == "$EXPECTED" ]]; then
      break
    fi
    /bin/sleep 0.25
  done
fi
if [[ "$(/usr/bin/curl -fsS --max-time 1 "$URL" 2>/dev/null || true)" != "$EXPECTED" ]]; then
  echo "GitHub Sync server did not start with the expected version." >&2
  exit 1
fi
/usr/bin/open http://127.0.0.1:8771/
