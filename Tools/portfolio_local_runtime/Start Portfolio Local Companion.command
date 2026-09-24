#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PORTFOLIO_ROOT="$GITHUB_ROOT/_portfolio_data"
LOG_DIR="$PORTFOLIO_ROOT/_logs"
PLIST="$HOME/Library/LaunchAgents/com.tnezki.portfolio-local-companion.plist"
LABEL="com.tnezki.portfolio-local-companion"
SERVER="$SCRIPT_DIR/portfolio_companion.py"
UID_NOW="$(id -u)"
mkdir -p "$LOG_DIR"

# v3.1: do not run the companion as a LaunchAgent. macOS privacy controls can
# block background launchd/Python processes from reading ~/Documents/GitHub.
# Running from Terminal inherits the teacher's interactive Documents access.
/bin/launchctl bootout "gui/$UID_NOW/$LABEL" >/dev/null 2>&1 || true
/usr/bin/pkill -f "$SERVER" >/dev/null 2>&1 || true
rm -f "$PLIST"

if [ ! -f "$SERVER" ]; then
  echo "Portfolio Local Companion could not be found:"
  echo "$SERVER"
  exit 1
fi

# Verify the interactive Python process can read the runtime file before
# starting the server. This gives a useful message if macOS privacy is blocking it.
if ! /usr/bin/python3 - "$SERVER" <<'PYCODE' >/dev/null 2>&1
import pathlib,sys
p=pathlib.Path(sys.argv[1])
p.read_bytes()
PYCODE
then
  echo
  echo "Portfolio Local Companion could not read its runtime files."
  echo "macOS is blocking Terminal/Python from the Documents folder."
  echo
  echo "Open System Settings > Privacy & Security > Files and Folders,"
  echo "allow Terminal access to Documents Folder, then run this command again."
  echo
  read -r -p "Press Return to close..." _
  exit 1
fi

echo
echo "Portfolio Local Companion"
echo
echo "Starting at http://127.0.0.1:8765/"
echo "Keep this Terminal window open while using Portfolio."
echo "You may minimize it. Press Control-C here when you are finished."
echo

# Run in the interactive Terminal session so macOS allows access to the
# teacher's private _portfolio_data and GitHub folders under Documents.
exec /usr/bin/python3 "$SERVER"
