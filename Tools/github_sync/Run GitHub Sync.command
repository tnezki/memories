#!/bin/bash
set -u

ACTION="${1:-}"
case "$ACTION" in
  pull|commit|push|commit-push) ;;
  *)
    echo "Usage: $0 pull|commit|push|commit-push"
    exit 2
    ;;
esac

detect_root() {
  if [[ -n "${GITHUB_ROOT:-}" && -d "$GITHUB_ROOT" ]]; then
    printf '%s\n' "$GITHUB_ROOT"; return 0
  fi
  if [[ -d "$HOME/GitHub" ]]; then
    printf '%s\n' "$HOME/GitHub"; return 0
  fi
  if [[ -d "$HOME/Documents/GitHub" ]]; then
    printf '%s\n' "$HOME/Documents/GitHub"; return 0
  fi
  return 1
}

ROOT="$(detect_root || true)"
REPOS=("memories" "algebra" "physics" "apcalc" "teacher_shared")
FAILURES=0
STAMP="$(date '+%Y-%m-%d %H:%M')"
COMMIT_MESSAGE="GitHub Sync ${STAMP}"

banner_fail() {
  echo
  echo "FAILURE FAILURE FAILURE"
  echo "GITHUB SYNC FAILURE"
  echo "FAILURE FAILURE FAILURE"
  echo
}

banner_success() {
  echo
  echo "SUCCESS SUCCESS SUCCESS"
  echo "GITHUB SYNC SUCCESS"
  echo "SUCCESS SUCCESS SUCCESS"
  echo
}

if [[ -z "$ROOT" ]]; then
  echo "Could not locate the GitHub workspace root."
  banner_fail
  read -r -p "Press Return to close..."
  exit 1
fi

# Network/auth preflight BEFORE a workflow that may create commits.
if [[ "$ACTION" == "pull" || "$ACTION" == "push" || "$ACTION" == "commit-push" ]]; then
  if ! git -C "$ROOT/memories" ls-remote origin HEAD >/dev/null 2>&1; then
    echo "GitHub authentication/network preflight failed."
    echo "No repositories were changed."
    echo
    echo "Try: ssh -T git@github.com"
    banner_fail
    read -r -p "Press Return to close..."
    exit 1
  fi
fi

echo
echo "GitHub Sync"
echo "==========="
echo
echo "Workspace root: $ROOT"
echo "Action: $ACTION"
[[ "$ACTION" == "commit" || "$ACTION" == "commit-push" ]] && echo "Commit message: $COMMIT_MESSAGE"
echo "Repositories: ${REPOS[*]}"
echo

for name in "${REPOS[@]}"; do
  repo="$ROOT/$name"
  echo "=== $name ==="

  if [[ ! -d "$repo/.git" ]]; then
    echo "FAILED: not a Git repository: $repo"
    FAILURES=$((FAILURES + 1)); echo; continue
  fi

  gitdir="$(git -C "$repo" rev-parse --git-dir 2>/dev/null || true)"
  if [[ -n "$gitdir" ]]; then
    case "$gitdir" in /*) abs_gitdir="$gitdir" ;; *) abs_gitdir="$repo/$gitdir" ;; esac
    if [[ -d "$abs_gitdir/rebase-merge" || -d "$abs_gitdir/rebase-apply" || -f "$abs_gitdir/MERGE_HEAD" ]]; then
      echo "FAILED: merge/rebase already in progress."
      FAILURES=$((FAILURES + 1)); echo; continue
    fi
  fi

  branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  remote="$(git -C "$repo" remote get-url origin 2>/dev/null || true)"
  echo "Branch: ${branch:-unknown}"
  echo "Origin: ${remote:-missing}"

  if [[ "$ACTION" == "pull" ]]; then
    if [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]]; then
      echo "BLOCKED: local changes are present. Commit or discard them first."
      git -C "$repo" status --short
      FAILURES=$((FAILURES + 1)); echo; continue
    fi
    if git -C "$repo" pull --ff-only; then echo "PULLED: $name"; else echo "FAILED: pull failed for $name"; FAILURES=$((FAILURES + 1)); fi
    echo; continue
  fi

  if [[ "$ACTION" == "commit" || "$ACTION" == "commit-push" ]]; then
    if ! git -C "$repo" add -A; then
      echo "FAILED: could not stage $name"
      FAILURES=$((FAILURES + 1)); echo; continue
    fi
    if ! git -C "$repo" diff --cached --quiet; then
      if git -C "$repo" commit -m "$COMMIT_MESSAGE"; then echo "COMMITTED: $name"; else echo "FAILED: commit failed for $name"; FAILURES=$((FAILURES + 1)); echo; continue; fi
    else
      echo "NO LOCAL CHANGES: $name"
    fi
    if [[ "$ACTION" == "commit" ]]; then echo; continue; fi
  fi

  if [[ "$ACTION" == "push" ]]; then
    if [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]]; then
      echo "BLOCKED: uncommitted local changes are present. Use Commit first."
      git -C "$repo" status --short
      FAILURES=$((FAILURES + 1)); echo; continue
    fi
    if git -C "$repo" push; then echo "PUSHED: $name"; else echo "FAILED: push failed for $name"; FAILURES=$((FAILURES + 1)); fi
    echo; continue
  fi

  if [[ "$ACTION" == "commit-push" ]]; then
    if ! git -C "$repo" pull --rebase; then
      echo "FAILED: pull --rebase failed for $name"
      git -C "$repo" rebase --abort >/dev/null 2>&1 || true
      FAILURES=$((FAILURES + 1)); echo; continue
    fi
    if git -C "$repo" push; then echo "PUSHED: $name"; else echo "FAILED: push failed for $name"; FAILURES=$((FAILURES + 1)); fi
    echo; continue
  fi

done

if [[ "$FAILURES" -eq 0 ]]; then
  banner_success
  EXIT_CODE=0
else
  echo "$FAILURES repository issue(s) require attention."
  banner_fail
  EXIT_CODE=1
fi

read -r -p "Press Return to close..."
exit "$EXIT_CODE"
