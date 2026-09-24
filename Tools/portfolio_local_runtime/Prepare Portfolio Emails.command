#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
/usr/bin/python3 "$SCRIPT_DIR/prepare_portfolio_emails.py"
printf '\n'
read -r -p "Press Return to close..." _
