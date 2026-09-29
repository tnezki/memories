#!/bin/zsh
set -u

BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "$BIN_DIR/../.." && pwd)"
TOOL_DIR="$(cd "$APP_DIR/.." && pwd)"
MEMORIES_ROOT="$(cd "$TOOL_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
RUNNER="$TOOL_DIR/Start Student Data Tools.command"
CONFIG_DIR="$GITHUB_ROOT/_portfolio_data/_student_data_tools"
URL_FILE="$CONFIG_DIR/email_sender_url.txt"
DASHBOARD="$CONFIG_DIR/index.html"
PORTFOLIO_URL="http://127.0.0.1:8765/"
HEALTH_URL="http://127.0.0.1:8765/api/runtime-version"

mkdir -p "$CONFIG_DIR"

if [[ ! -f "$RUNNER" ]]; then
  /usr/bin/osascript -e 'display alert "Student Data Tools" message "The Student Data Tools runtime launcher is missing." as critical'
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

portfolio_ready=0
for _ in {1..40}; do
  if /usr/bin/curl -fsS --max-time 1 "$HEALTH_URL" 2>/dev/null | /usr/bin/grep -q '"status"[[:space:]]*:[[:space:]]*"PASS"'; then
    portfolio_ready=1
    break
  fi
  /bin/sleep 0.25
done

if [[ "$portfolio_ready" -ne 1 ]]; then
  /usr/bin/osascript -e 'display alert "Student Data Tools" message "Portfolio runtime did not pass its health check. Leave the Terminal window open and review the error shown there." as critical'
  exit 1
fi

email_url=""
if [[ -f "$URL_FILE" ]]; then
  email_url="$(/usr/bin/head -n 1 "$URL_FILE" | /usr/bin/tr -d '\r\n')"
fi

if [[ -z "$email_url" ]]; then
  email_url=$(/usr/bin/osascript <<'APPLESCRIPT'
try
  set d to display dialog "Paste the deployed Portfolio Email Delivery web-app URL. You can choose Not Now and set it later." default answer "" buttons {"Not Now", "Save"} default button "Save" with title "Student Data Tools"
  if button returned of d is "Save" then
    return text returned of d
  end if
on error number -128
end try
return ""
APPLESCRIPT
)
  email_url="${email_url//$'\r'/}"
  email_url="${email_url//$'\n'/}"
  if [[ -n "$email_url" ]]; then
    if [[ "$email_url" == https://script.google.com/* || "$email_url" == https://script.googleusercontent.com/* ]]; then
      printf '%s\n' "$email_url" > "$URL_FILE"
    else
      /usr/bin/osascript -e 'display alert "Student Data Tools" message "The pasted value was not recognized as a Google Apps Script web-app URL. Portfolio will still open; the email sender was not saved." as warning'
      email_url=""
    fi
  fi
fi

email_state="NOT CONFIGURED"
email_detail="Use Set Email Sender URL.command when you are ready."
email_button=""
if [[ -n "$email_url" ]]; then
  code=$(/usr/bin/curl -L --max-time 8 --silent --output /dev/null --write-out '%{http_code}' "$email_url" 2>/dev/null || true)
  if [[ "$code" == 2?? || "$code" == 3?? ]]; then
    email_state="REACHABLE"
    email_detail="Open the sender, load the current local Portfolio_Email_Sender_Package.zip, then run its teacher-account, quota, attachment, and recipient preflight checks."
  else
    email_state="UNREACHABLE"
    email_detail="The saved sender URL did not respond successfully. Portfolio is still available."
  fi
  email_button="<a class=\"button\" href=\"$email_url\" target=\"_blank\" rel=\"noopener\">Open Portfolio Email Sender</a>"
fi

cat > "$DASHBOARD" <<EOF2
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Data Tools</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:#f3f5f8;color:#17202a;margin:0}.wrap{max-width:820px;margin:42px auto;padding:0 20px}h1{margin:0 0 8px;color:#173f73}.lead{color:#667085;margin:0 0 24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:720px){.grid{grid-template-columns:1fr}}.card{background:#fff;border:1px solid #d9e0e8;border-radius:16px;padding:20px;box-shadow:0 5px 20px rgba(20,40,70,.06)}h2{margin-top:0}.status{font-weight:800;margin:10px 0}.ok{color:#147a3e}.warn{color:#a15a00}.button{display:inline-block;margin-top:12px;padding:11px 14px;border-radius:9px;background:#245b87;color:white;text-decoration:none;font-weight:800}.note{margin-top:18px;background:#fff;border:1px solid #d9e0e8;border-radius:12px;padding:14px;color:#59636f;font-size:14px}code{background:#f1f3f6;padding:2px 5px;border-radius:5px}
</style></head><body><div class="wrap">
<h1>Student Data Tools</h1><p class="lead">Private local Portfolio work and teacher-authorized report delivery.</p>
<div class="grid">
<div class="card"><h2>Portfolio</h2><div class="status ok">READY</div><p>The local Portfolio runtime passed its health check on <code>127.0.0.1:8765</code>.</p><a class="button" href="$PORTFOLIO_URL">Open Portfolio Tools</a></div>
<div class="card"><h2>Email Sender</h2><div class="status $([[ "$email_state" == "REACHABLE" ]] && printf ok || printf warn)">$email_state</div><p>$email_detail</p>$email_button</div>
</div>
<div class="note"><b>Privacy:</b> this landing page contains no student data. Email is never sent automatically. The sender's own preflight and explicit LIVE SEND confirmation remain required.</div>
</div></body></html>
EOF2

/usr/bin/open "$DASHBOARD"
/usr/bin/osascript -e 'display notification "Portfolio runtime is ready." with title "Student Data Tools"' >/dev/null 2>&1 || true

# The runtime must remain in Terminal for macOS Documents-folder access. Minimize
# the newly opened Terminal window after successful health check when possible.
/bin/sleep 0.5
/usr/bin/osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
tell application "Terminal"
  if (count of windows) > 0 then set miniaturized of front window to true
end tell
APPLESCRIPT

exit 0
