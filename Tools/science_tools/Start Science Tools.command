#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
TARGET="$ROOT/SCIENCE_Tools/Start Science Tools.command"
if [[ ! -f "$TARGET" ]]; then
  printf 'New Science Tools has not been installed. Run the latest Curriculum Transfer.\n'
  exit 1
fi
exec /bin/bash "$TARGET"
