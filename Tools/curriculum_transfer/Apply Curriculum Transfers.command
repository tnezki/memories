#!/bin/zsh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
TRANSFER_ROOT="${CURRICULUM_TRANSFER_ROOT:-$GITHUB_ROOT/_curriculum_transfers}"
PYTHON_BIN="/usr/bin/python3"
LOCK_DIR="$TRANSFER_ROOT/.run_lock"
ROOTS_SEED="$SCRIPT_DIR/approved_roots.json"

mkdir -p "$TRANSFER_ROOT/downloads" "$TRANSFER_ROOT/requests" "$TRANSFER_ROOT/_processed" "$TRANSFER_ROOT/_failed" "$TRANSFER_ROOT/_backups" "$TRANSFER_ROOT/_logs"

# The canonical approved-root list lives with this tool in memories. Keep the
# local runtime copy current every time the launcher starts.
if [[ ! -f "$ROOTS_SEED" ]]; then
  clear
  printf '%s\n' 'Curriculum Transfer'
  printf '%s\n' '=================='
  printf '\nFAILURE FAILURE FAILURE\n'
  printf 'CURRICULUM TRANSFER FAILURE\n'
  printf 'Approved roots seed is missing: %s\n' "$ROOTS_SEED"
  printf 'FAILURE FAILURE FAILURE\n\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi
/bin/cp -f "$ROOTS_SEED" "$TRANSFER_ROOT/approved_roots.json"

clear
printf '%s\n' 'Curriculum Transfer'
printf '%s\n' '=================='
printf '\nWorkspace root: %s\n' "$GITHUB_ROOT"
printf 'Incoming transfer ZIPs: %s\n' "$TRANSFER_ROOT/downloads"
printf 'AI request ZIPs: %s\n' "$TRANSFER_ROOT/requests"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '\nFAILURE FAILURE FAILURE\n'
  printf 'CURRICULUM TRANSFER FAILURE\n'
  printf 'Another Curriculum Transfer run appears to be active.\n'
  printf 'FAILURE FAILURE FAILURE\n\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

# Returned Curriculum Transfers are intentionally processed only from the
# dedicated inbox. This keeps the teacher's manual Save step visible and
# prevents unrelated ZIPs in ~/Downloads from being silently imported.

transfer_status=0

printf '\n=== Curriculum Transfers ===\n'
"$PYTHON_BIN" "$SCRIPT_DIR/apply_curriculum_transfers.py" \
  --transfer-root "$TRANSFER_ROOT" \
  --github-root "$GITHUB_ROOT" || transfer_status=$?

printf '\n'
if [[ "$transfer_status" -eq 0 ]]; then
  printf 'SUCCESS SUCCESS SUCCESS\n'
  printf 'CURRICULUM TRANSFER SUCCESS\n'
  printf 'SUCCESS SUCCESS SUCCESS\n'
  final_status=0
else
  printf 'FAILURE FAILURE FAILURE\n'
  printf 'CURRICULUM TRANSFER FAILURE\n'
  printf 'FAILURE FAILURE FAILURE\n'
  final_status=1
fi

printf '\nSee transfer result above for Git publish status.\n'
printf 'Press Return to close...'
read -r
exit "$final_status"
