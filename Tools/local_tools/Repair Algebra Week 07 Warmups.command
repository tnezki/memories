#!/bin/bash
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo
/usr/bin/python3 "$SCRIPT_DIR/repair_algebra_week07_warmups.py"
RESULT=$?
echo
read -r -p "Press Return to close..."
exit "$RESULT"
