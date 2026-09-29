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
RUNTIME_DIR="$MEMORIES_ROOT/Tools/portfolio_local_runtime"

mkdir -p "$CONFIG_DIR"

if [[ ! -f "$RUNNER" ]]; then
  /usr/bin/osascript -e 'display alert "Student Data Tools" message "The Student Data Tools runtime launcher is missing." as critical'
  exit 1
fi

# Stop stale Portfolio servers first so closing their old Terminal windows does
# not trigger a terminate-running-process confirmation. Do not touch unrelated
# Terminal processes/windows.
for runtime in \
  portfolio_companion.py \
  portfolio_companion_refresh.py \
  portfolio_companion_final.py \
  portfolio_companion_notes.py \
  portfolio_companion_observation_status.py \
  portfolio_companion_sender.py; do
  /usr/bin/pkill -f "$RUNTIME_DIR/$runtime" >/dev/null 2>&1 || true
done
/bin/sleep 0.25

# Close only stale Student Data Tools / Portfolio runtime Terminal windows.
/usr/bin/osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
set staleWindows to {}
tell application "Terminal"
  repeat with w in windows
    set stale to false
    try
      set windowName to (name of w as text)
      if windowName contains "Student Data Tools Runtime" then set stale to true
      if windowName contains "Start Student Data Tools.command" then set stale to true
      if windowName contains "Start Portfolio Local Companion.command" then set stale to true
    end try
    if stale is false then
      try
        set tabText to (contents of selected tab of w as text)
        if tabText contains "Portfolio Local Companion is running." then set stale to true
        if tabText contains "Starting private Portfolio runtime..." then set stale to true
      end try
    end if
    if stale then set end of staleWindows to w
  end repeat
  repeat with w in staleWindows
    try
      close w
    end try
  end repeat
end tell
APPLESCRIPT

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
  /usr/bin/osascript -e 'display alert "Student Data Tools" message "Portfolio runtime did not pass its health check. Leave the Student Data Tools Runtime Terminal window open and review the error shown there." as critical'
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
email_class="warn"
email_detail="Set the sender URL when you are ready."
email_button='<span class="button disabled">Sender not configured</span>'
if [[ -n "$email_url" ]]; then
  code=$(/usr/bin/curl -L --max-time 8 --silent --output /dev/null --write-out '%{http_code}' "$email_url" 2>/dev/null || true)
  if [[ "$code" == 2?? || "$code" == 3?? ]]; then
    email_state="REACHABLE"
    email_class="ok"
    email_detail="Sender page responded. Its own package/preflight checks remain authoritative."
  else
    email_state="UNREACHABLE"
    email_class="warn"
    email_detail="The saved sender URL did not respond successfully. Portfolio is still available."
  fi
  email_button="<a class=\"button\" href=\"$email_url\" target=\"_blank\" rel=\"noopener\">Open Portfolio Email Sender</a>"
fi

cat > "$DASHBOARD" <<EOF2
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Data Tools</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:#f3f5f8;color:#17202a;margin:0}.wrap{max-width:940px;margin:34px auto;padding:0 20px}h1{margin:0 0 7px;color:#173f73;font-size:38px}.lead{color:#667085;margin:0 0 18px}.health{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}.badge{background:#fff;border:1px solid #d9e0e8;border-radius:999px;padding:8px 11px;font-weight:800}.ok{color:#147a3e}.warn{color:#a15a00}.card{background:#fff;border:1px solid #d9e0e8;border-radius:16px;padding:20px;box-shadow:0 5px 20px rgba(20,40,70,.06)}h2{margin:0 0 8px;color:#173f73}.step{display:grid;grid-template-columns:44px 1fr;gap:14px;padding:15px 0;border-top:1px solid #e3e8ef}.step:first-of-type{border-top:0}.num{width:36px;height:36px;border-radius:50%;background:#173f73;color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;font-size:18px}.step h3{margin:0 0 4px;color:#173f73}.step p{margin:0 0 9px;line-height:1.42;color:#39475a}.button{display:inline-block;padding:10px 14px;border-radius:9px;background:#245b87;color:white;text-decoration:none;font-weight:800}.button.secondary{background:#fff;color:#173f73;border:1.5px solid #173f73}.button.disabled{background:#aab3bd;cursor:default}.small{font-size:12px;color:#667085;margin-top:7px!important}.note{margin-top:16px;background:#fff;border:1px solid #d9e0e8;border-radius:12px;padding:13px;color:#59636f;font-size:14px}code{background:#f1f3f6;padding:2px 5px;border-radius:5px}
</style></head><body><div class="wrap">
<h1>Student Data Tools</h1><p class="lead">Private local Portfolio work and teacher-authorized report delivery.</p>
<div class="health"><span class="badge ok">Portfolio READY</span><span class="badge $email_class">Email Sender $email_state</span></div>
<div class="card"><h2>What do you want to do?</h2>
<div class="step"><div class="num">1</div><div><h3>New Evidence</h3><p>Add or grade new evidence, enter teacher observations, or update a roster. This is the path that can change student progress.</p><a class="button" href="$PORTFOLIO_URL">Open Portfolio Tools</a></div></div>
<div class="step"><div class="num">2</div><div><h3>Just Print / View Reports</h3><p>Use the current saved Portfolio state. No new evidence is added and grades do not change.</p><a class="button secondary" href="$PORTFOLIO_URL">View / Print Current Reports</a></div></div>
<div class="step"><div class="num">3</div><div><h3>Prepare Email Reports</h3><p>Open Portfolio, choose the course/unit Email control panel, select students, review notes, and prepare the batch.</p><a class="button" href="$PORTFOLIO_URL">Prepare Email Reports</a><p class="small">When preparation succeeds, Finder highlights the exact <code>Portfolio_Email_Sender_Package.zip</code> and the configured sender page opens automatically.</p></div></div>
<div class="step"><div class="num">4</div><div><h3>Send Reports</h3><p>In the sender, choose the highlighted ZIP, Load Local Package, verify recipients/status, optionally Send Test to Me, then explicitly use LIVE SEND.</p>$email_button<p class="small">$email_detail</p></div></div>
</div>
<div class="note"><b>Privacy:</b> this landing page contains no student data. Email is never sent automatically. The sender's own preflight and explicit LIVE SEND confirmation remain required.</div>
</div></body></html>
EOF2

/usr/bin/open "$DASHBOARD"
/usr/bin/osascript -e 'display notification "Portfolio runtime is ready." with title "Student Data Tools"' >/dev/null 2>&1 || true

# The runtime must remain in Terminal for macOS Documents-folder access. Minimize
# the uniquely titled fresh runtime window after successful health check.
/bin/sleep 0.5
/usr/bin/osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
tell application "Terminal"
  repeat with w in windows
    set isRuntime to false
    try
      if (name of w as text) contains "Student Data Tools Runtime" then set isRuntime to true
      if (name of w as text) contains "Start Portfolio Local Companion.command" then set isRuntime to true
    end try
    if isRuntime is false then
      try
        set tabText to (contents of selected tab of w as text)
        if tabText contains "Portfolio Local Companion is running." then set isRuntime to true
        if tabText contains "Runtime: progress-model-" then set isRuntime to true
      end try
    end if
    if isRuntime then
      try
        set miniaturized of w to true
      end try
    end if
  end repeat
end tell
APPLESCRIPT

exit 0
