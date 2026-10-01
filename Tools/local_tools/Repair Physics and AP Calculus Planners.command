#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
/usr/bin/python3 "$SCRIPT_DIR/repair_physics_apcalc_planners_20260930.py"
echo
echo "Press Return to close."
read
