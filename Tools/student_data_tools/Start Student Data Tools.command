#!/bin/zsh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PORTFOLIO_RUNNER="$MEMORIES_ROOT/Tools/portfolio_local_runtime/Start Portfolio Local Companion.command"

# Unique Terminal title lets the Dock app close only its stale runtime window.
printf '\033]0;Student Data Tools Runtime\007'
printf '\nStudent Data Tools\n'
printf '==================\n\n'
printf 'Starting private Portfolio runtime...\n'

if [[ ! -f "$PORTFOLIO_RUNNER" ]]; then
  printf '\nFAILURE FAILURE FAILURE\n'
  printf 'STUDENT DATA TOOLS FAILURE\n'
  printf 'Portfolio runtime launcher is missing:\n%s\n' "$PORTFOLIO_RUNNER"
  printf 'FAILURE FAILURE FAILURE\n\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi

# Student Data Tools owns the browser landing page. Keep the local companion
# running, but do not also open its raw 127.0.0.1 homepage on app launch.
export PORTFOLIO_NO_OPEN=1
exec "$PORTFOLIO_RUNNER"
