#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PORTFOLIO_ROOT="$GITHUB_ROOT/_portfolio_data"
LOG_DIR="$PORTFOLIO_ROOT/_logs"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST="$PLIST_DIR/com.tnezki.portfolio-local-companion.plist"
PYTHON="/usr/bin/python3"
SERVER="$SCRIPT_DIR/portfolio_companion.py"
LABEL="com.tnezki.portfolio-local-companion"
UID_NOW="$(id -u)"
mkdir -p "$LOG_DIR" "$PLIST_DIR"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$SERVER</string>
    <string>--no-open</string>
  </array>
  <key>WorkingDirectory</key><string>$SCRIPT_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG_DIR/portfolio_local_companion.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/portfolio_local_companion_error.log</string>
</dict>
</plist>
EOF

/bin/launchctl bootout "gui/$UID_NOW/$LABEL" >/dev/null 2>&1 || true
/usr/bin/pkill -f "$SERVER" >/dev/null 2>&1 || true
/bin/launchctl bootstrap "gui/$UID_NOW" "$PLIST"
/bin/launchctl kickstart -k "gui/$UID_NOW/$LABEL" >/dev/null 2>&1 || true

READY=0
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if /usr/bin/curl -fsS "http://127.0.0.1:8765/" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 0.35
done

echo
echo "Portfolio Local Companion"
if [ "$READY" -eq 1 ]; then
  echo "Ready at http://127.0.0.1:8765/"
  echo "It is now installed as a private login helper and will restart automatically on this Mac."
  /usr/bin/open "http://127.0.0.1:8765/"
else
  echo "The login helper was installed, but the local page did not answer yet."
  echo "Check: $LOG_DIR/portfolio_local_companion_error.log"
  exit 1
fi

echo
echo "You can close this Terminal window."
read -r -p "Press Return to close..." _
