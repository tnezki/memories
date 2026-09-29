#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_EXEC="$SCRIPT_DIR/Planner Pages.app/Contents/MacOS/Planner Pages.command"
exec "$APP_EXEC"
