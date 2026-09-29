#!/bin/zsh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
CONFIG_DIR="$GITHUB_ROOT/_portfolio_data/_student_data_tools"
URL_FILE="$CONFIG_DIR/email_sender_url.txt"
mkdir -p "$CONFIG_DIR"

clear
printf 'Student Data Tools - Email Sender URL\n'
printf '=====================================\n\n'
printf 'Paste the deployed Portfolio Email Delivery web-app URL, then press Return.\n'
printf 'Press Return on a blank line to cancel.\n\n'
printf 'URL: '
IFS= read -r VALUE
VALUE="${VALUE//$'\r'/}"
VALUE="${VALUE//$'\n'/}"

if [[ -z "$VALUE" ]]; then
  printf '\nCanceled. Nothing changed.\n'
  printf 'Press Return to close...'
  read -r
  exit 0
fi

if [[ "$VALUE" != https://script.google.com/* && "$VALUE" != https://script.googleusercontent.com/* ]]; then
  printf '\nFAILURE FAILURE FAILURE\n'
  printf 'STUDENT DATA TOOLS FAILURE\n'
  printf 'That does not look like a Google Apps Script web-app URL. Nothing changed.\n'
  printf 'FAILURE FAILURE FAILURE\n\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi

printf '%s\n' "$VALUE" > "$URL_FILE"
printf '\nSUCCESS SUCCESS SUCCESS\n'
printf 'EMAIL SENDER URL SAVED\n'
printf 'SUCCESS SUCCESS SUCCESS\n\n'
printf 'Reopen Student Data Tools to use the saved sender.\n'
printf 'Press Return to close...'
read -r
