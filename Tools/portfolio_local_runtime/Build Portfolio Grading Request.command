#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
/usr/bin/python3 "$SCRIPT_DIR/build_grading_request.py"
printf '\n'
read -r -p "Press Return to close..." _
