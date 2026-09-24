#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
/usr/bin/python3 "$SCRIPT_DIR/apply_grading_result.py"
printf '\n'
read -r -p "Press Return to close..." _
