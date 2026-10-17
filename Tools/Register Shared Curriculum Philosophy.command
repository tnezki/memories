#!/bin/zsh
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
clear
printf '%s\n' 'Register Shared Curriculum Philosophy'
printf '%s\n' '===================================='
/usr/bin/python3 "$SCRIPT_DIR/apply_shared_curriculum_manifest_update.py"
return_code=$?
printf '\n'
if [[ "$return_code" -eq 0 ]]; then
  printf '%s\n' 'SUCCESS SUCCESS SUCCESS'
  printf '%s\n' 'MANIFEST UPDATE COMPLETE'
else
  printf '%s\n' 'FAILURE FAILURE FAILURE'
  printf '%s\n' 'MANIFEST UPDATE FAILED'
fi
printf '\nPress Return to close...'
read -r
exit "$return_code"
