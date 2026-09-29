#!/bin/zsh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORIES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GITHUB_ROOT="$(cd "$MEMORIES_ROOT/.." && pwd)"
TRANSFER_ROOT="${CURRICULUM_TRANSFER_ROOT:-$GITHUB_ROOT/_curriculum_transfers}"
PYTHON_BIN="/usr/bin/python3"
LOCK_DIR="$TRANSFER_ROOT/.run_lock"
ROOTS_SEED="$SCRIPT_DIR/approved_roots.json"

mkdir -p "$TRANSFER_ROOT/downloads" "$TRANSFER_ROOT/_processed" "$TRANSFER_ROOT/_failed" "$TRANSFER_ROOT/_backups" "$TRANSFER_ROOT/_logs" "$TRANSFER_ROOT/_transactions"

if [[ ! -f "$ROOTS_SEED" ]]; then
  clear
  printf '%s\n' 'Curriculum Transfer - Local Only'
  printf '%s\n' '================================'
  printf '\nFAILURE: Approved roots seed is missing: %s\n' "$ROOTS_SEED"
  printf 'Press Return to close...'
  read -r
  exit 1
fi
/bin/cp -f "$ROOTS_SEED" "$TRANSFER_ROOT/approved_roots.json"

clear
printf '%s\n' 'Curriculum Transfer - Local Only'
printf '%s\n' '================================'
printf '\nWorkspace root: %s\n' "$GITHUB_ROOT"
printf 'Incoming transfer ZIPs: %s\n' "$TRANSFER_ROOT/downloads"
printf 'Local-only mode: apply + verify; no Git commit or push\n'

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '\nFAILURE: Another Curriculum Transfer run appears to be active.\n'
  printf 'Press Return to close...'
  read -r
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

transfer_status=0
"$PYTHON_BIN" "$SCRIPT_DIR/apply_curriculum_transfers.py" \
  --transfer-root "$TRANSFER_ROOT" \
  --github-root "$GITHUB_ROOT" \
  --local-only || transfer_status=$?

printf '\n'
if [[ "$transfer_status" -eq 0 ]]; then
  printf 'LOCAL-ONLY TRANSFER SUCCESS\n'
  printf 'No Git actions were run.\n'
  final_status=0
else
  printf 'LOCAL-ONLY TRANSFER FAILURE\n'
  final_status=1
fi

printf '\nPress Return to close...'
read -r
exit "$final_status"
