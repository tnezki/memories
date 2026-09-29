#!/bin/bash
set -u

detect_root() {
  if [[ -n "${GITHUB_ROOT:-}" && -d "${GITHUB_ROOT}" ]]; then
    printf '%s\n' "$GITHUB_ROOT"; return 0
  fi
  if [[ -d "$HOME/GitHub" ]]; then
    printf '%s\n' "$HOME/GitHub"; return 0
  fi
  if [[ -d "$HOME/Documents/GitHub" ]]; then
    printf '%s\n' "$HOME/Documents/GitHub"; return 0
  fi
  return 1
}

ROOT="$(detect_root || true)"
if [[ -z "$ROOT" ]]; then
  /usr/bin/osascript -e 'display alert "Planner Pages" message "Could not locate the GitHub workspace root." as critical'
  exit 1
fi

CHOICE=$(/usr/bin/osascript <<'APPLESCRIPT'
set choices to {"Algebra 1", "Physics", "AP Calculus AB", "Open All Planner Pages"}
set picked to choose from list choices with title "Planner Pages" with prompt "Open which Planner?" default items {"Algebra 1"} OK button name "Open" cancel button name "Cancel"
if picked is false then return ""
return item 1 of picked
APPLESCRIPT
)
[[ -n "$CHOICE" ]] || exit 0

ready() {
  /usr/bin/curl -fsS --max-time 1 "http://127.0.0.1:$1/" >/dev/null 2>&1
}

need_runtime=0
case "$CHOICE" in
  "Algebra 1") ready 8767 || need_runtime=1 ;;
  "Physics") ready 8768 || need_runtime=1 ;;
  "AP Calculus AB") ready 8769 || need_runtime=1 ;;
  "Open All Planner Pages")
    ready 8767 || need_runtime=1
    ready 8768 || need_runtime=1
    ready 8769 || need_runtime=1
    ;;
esac

if [[ "$need_runtime" -eq 1 ]]; then
  RUNTIME="$ROOT/_algebra_teacher_tools/runtime/Start Teacher Tools Runtime.command"
  LOG_DIR="$ROOT/_algebra_teacher_tools/runtime/logs"
  LOG_FILE="$LOG_DIR/planner_pages_launcher.log"
  if [[ ! -f "$RUNTIME" ]]; then
    /usr/bin/osascript -e 'display alert "Planner Pages" message "Start Teacher Tools Runtime.command was not found." as critical'
    exit 1
  fi
  mkdir -p "$LOG_DIR"
  /usr/bin/nohup /bin/bash "$RUNTIME" >"$LOG_FILE" 2>&1 &
  disown || true

  for _ in $(seq 1 30); do
    all_ready=1
    case "$CHOICE" in
      "Algebra 1") ready 8767 || all_ready=0 ;;
      "Physics") ready 8768 || all_ready=0 ;;
      "AP Calculus AB") ready 8769 || all_ready=0 ;;
      "Open All Planner Pages")
        ready 8767 || all_ready=0
        ready 8768 || all_ready=0
        ready 8769 || all_ready=0
        ;;
    esac
    [[ "$all_ready" -eq 1 ]] && break
    sleep 1
  done
fi

case "$CHOICE" in
  "Algebra 1")
    /usr/bin/open "http://127.0.0.1:8767/"
    ;;
  "Physics")
    /usr/bin/open "http://127.0.0.1:8768/"
    ;;
  "AP Calculus AB")
    /usr/bin/open "http://127.0.0.1:8769/"
    ;;
  "Open All Planner Pages")
    /usr/bin/open "http://127.0.0.1:8767/"
    /usr/bin/open "http://127.0.0.1:8768/"
    /usr/bin/open "http://127.0.0.1:8769/"
    ;;
esac
