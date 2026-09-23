#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GITHUB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ROOT="$GITHUB_ROOT/_portfolio_data"
mkdir -p "$ROOT/00 Contact Directory"
for course in "Algebra 1" "Physics" "AP Calculus AB" "STEM I"; do
  mkdir -p "$ROOT/$course"
done
if [ ! -f "$ROOT/PORTFOLIO_LOCAL_ROOT.json" ]; then
cat > "$ROOT/PORTFOLIO_LOCAL_ROOT.json" <<'JSON'
{
  "schema": "portfolio-local-root/1",
  "status": "CURRENT",
  "root_name": "_portfolio_data",
  "transport": "manual_usb_copy",
  "private_student_data": true,
  "never_git": true
}
JSON
fi
printf '\nPortfolio local root is ready:\n%s\n\n' "$ROOT"
printf 'Course folders are ready. Unit folders are created automatically by the installer as needed.\n'
printf 'Do not initialize _portfolio_data as a Git repository.\n\n'
read -r -p "Press Return to close..." _
