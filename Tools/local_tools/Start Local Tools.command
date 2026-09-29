#!/bin/bash
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec /usr/bin/open "$SCRIPT_DIR/Local Tools.app"
