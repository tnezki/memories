#!/bin/zsh
set -u

BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "$BIN_DIR/../.." && pwd)"
TOOL_DIR="$(cd "$APP_DIR/.." && pwd)"
RUNNER="$TOOL_DIR/Apply Curriculum Transfers.command"

if [[ ! -f "$RUNNER" ]]; then
  /usr/bin/osascript -e 'display alert "Curriculum Transfer" message "The Curriculum Transfer runner is missing." as critical'
  exit 1
fi

/usr/bin/osascript - "$RUNNER" <<'APPLESCRIPT'
on run argv
  set runnerPath to item 1 of argv
  tell application "Terminal"
    activate
    do script quoted form of runnerPath
  end tell
end run
APPLESCRIPT
