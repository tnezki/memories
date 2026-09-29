#!/bin/zsh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUNTIME="$MEMORIES_ROOT/Tools/portfolio_local_runtime/portfolio_companion_live.py"
PORT=8765

printf '\033]0;Student Data Tools Runtime\007'
printf '\nStudent Data Tools\n'
printf '==================\n\n'
printf 'Starting authoritative private Portfolio runtime...\n'

if [[ ! -f "$RUNTIME" ]]; then
  printf '\nFAILURE FAILURE FAILURE\n'
  printf 'STUDENT DATA TOOLS FAILURE\n'
  printf 'Authoritative Portfolio runtime is missing:\n%s\n' "$RUNTIME"
  printf 'FAILURE FAILURE FAILURE\n\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi

PIDS="$(/usr/sbin/lsof -tiTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "$PIDS" ]]; then
  printf 'Stopping stale Portfolio listener on port %s...\n' "$PORT"
  /bin/kill $PIDS >/dev/null 2>&1 || true
  for _ in {1..20}; do
    if ! /usr/sbin/lsof -tiTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1; then
      break
    fi
    /bin/sleep 0.1
  done
  PIDS="$(/usr/sbin/lsof -tiTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$PIDS" ]]; then
    /bin/kill -9 $PIDS >/dev/null 2>&1 || true
  fi
fi

export PORTFOLIO_NO_OPEN=1
exec /usr/bin/python3 "$RUNTIME" --no-open
