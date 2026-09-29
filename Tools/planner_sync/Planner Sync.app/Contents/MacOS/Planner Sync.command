#!/bin/bash
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RUNNER="$TOOL_DIR/Run Planner Sync.command"

CHOICE=$(/usr/bin/osascript <<'APPLESCRIPT'
set choices to {"Pull All Repos", "Commit + Push All Repos"}
set picked to choose from list choices with title "Planner Sync" with prompt "Choose the Planner repository action:" default items {"Pull All Repos"} OK button name "Run" cancel button name "Cancel"
if picked is false then return ""
return item 1 of picked
APPLESCRIPT
)

if [[ -z "$CHOICE" ]]; then
  exit 0
fi

if [[ "$CHOICE" == "Pull All Repos" ]]; then
  ACTION="pull"
else
  ACTION="push"
  CONFIRM=$(/usr/bin/osascript <<'APPLESCRIPT'
display dialog "This will stage all current changes in algebra, physics, apcalc, and teacher_shared, create timestamped commits when needed, pull/rebase, and push. No force-push is used." with title "Commit + Push All Repos" buttons {"Cancel", "Continue"} default button "Continue" cancel button "Cancel"
return "continue"
APPLESCRIPT
) || exit 0
fi

CMD="$(printf '%q %q' "$RUNNER" "$ACTION")"
/usr/bin/osascript - "$CMD" <<'APPLESCRIPT'
on run argv
  tell application "Terminal"
    activate
    do script item 1 of argv
  end tell
end run
APPLESCRIPT
