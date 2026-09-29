#!/bin/bash
set -u

ACTION="${1:-}"
if [[ "$ACTION" != "pull" && "$ACTION" != "push" ]]; then
  echo "Usage: $0 pull|push"
  exit 2
fi

detect_root() {
  if [[ -n "${GITHUB_ROOT:-}" && -d "${GITHUB_ROOT}" ]]; then
    printf '%s\n' "$GITHUB_ROOT"
    return 0
  fi
  if [[ -d "$HOME/GitHub" ]]; then
    printf '%s\n' "$HOME/GitHub"
    return 0
  fi
  if [[ -d "$HOME/Documents/GitHub" ]]; then
    printf '%s\n' "$HOME/Documents/GitHub"
    return 0
  fi
  return 1
}

ROOT="$(detect_root || true)"
if [[ -z "$ROOT" ]]; then
  echo
  echo "FAILURE FAILURE FAILURE"
  echo "PLANNER SYNC FAILURE"
  echo "Could not locate the GitHub workspace root."
  echo "FAILURE FAILURE FAILURE"
  echo
  read -r -p "Press Return to close..."
  exit 1
fi

REPOS=("algebra" "physics" "apcalc" "teacher_shared")
FAILURES=0
CHANGED=0
STAMP="$(date '+%Y-%m-%d %H:%M')"
COMMIT_MESSAGE="Planner sync ${STAMP}"

in_progress() {
  local repo="$1"
  local gitdir
  gitdir="$(git -C "$repo" rev-parse --git-dir 2>/dev/null)" || return 1
  [[ -d "$repo/$gitdir/rebase-merge" || -d "$repo/$gitdir/rebase-apply" || -f "$repo/$gitdir/MERGE_HEAD" ]]
}

is_dirty() {
  local repo="$1"
  [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]]
}

echo
echo "Planner Sync"
echo "============"
echo
echo "Workspace root: $ROOT"
if [[ "$ACTION" == "pull" ]]; then
  echo "Action: PULL ALL REPOS"
else
  echo "Action: COMMIT + PUSH ALL REPOS"
  echo "Commit message: $COMMIT_MESSAGE"
fi
echo
echo "Repositories: ${REPOS[*]}"
echo

for name in "${REPOS[@]}"; do
  repo="$ROOT/$name"
  echo "=== $name ==="

  if [[ ! -d "$repo/.git" ]]; then
    echo "FAILED: $name is not an available Git repository at $repo"
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  if in_progress "$repo"; then
    echo "FAILED: merge/rebase already in progress. Resolve it manually first."
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  remote="$(git -C "$repo" remote get-url origin 2>/dev/null || true)"
  echo "Branch: ${branch:-unknown}"
  echo "Origin: ${remote:-missing}"

  if [[ "$ACTION" == "pull" ]]; then
    if is_dirty "$repo"; then
      echo "BLOCKED: local changes are present. Pull All will not stash or alter them."
      git -C "$repo" status --short
      FAILURES=$((FAILURES + 1))
      echo
      continue
    fi

    if git -C "$repo" pull --ff-only; then
      echo "PULLED: $name"
    else
      echo "FAILED: pull --ff-only failed for $name"
      FAILURES=$((FAILURES + 1))
    fi
    echo
    continue
  fi

  # Explicit Commit + Push workflow.
  if ! git -C "$repo" add -A; then
    echo "FAILED: could not stage $name"
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  if ! git -C "$repo" diff --cached --quiet; then
    if git -C "$repo" commit -m "$COMMIT_MESSAGE"; then
      echo "COMMITTED: $name"
      CHANGED=$((CHANGED + 1))
    else
      echo "FAILED: commit failed for $name"
      FAILURES=$((FAILURES + 1))
      echo
      continue
    fi
  else
    echo "NO LOCAL CHANGES: $name"
  fi

  if ! git -C "$repo" pull --rebase; then
    echo "FAILED: pull --rebase failed for $name"
    git -C "$repo" rebase --abort >/dev/null 2>&1 || true
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  if git -C "$repo" push; then
    echo "PUSHED: $name"
  else
    echo "FAILED: push failed for $name"
    FAILURES=$((FAILURES + 1))
  fi
  echo
done

if [[ "$FAILURES" -eq 0 ]]; then
  echo "SUCCESS SUCCESS SUCCESS"
  if [[ "$ACTION" == "pull" ]]; then
    echo "PLANNER PULL SUCCESS"
  else
    echo "PLANNER COMMIT + PUSH SUCCESS"
  fi
  echo "SUCCESS SUCCESS SUCCESS"
  EXIT_CODE=0
else
  echo "FAILURE FAILURE FAILURE"
  echo "PLANNER SYNC FAILURE - $FAILURES REPOSITORY ISSUE(S)"
  echo "FAILURE FAILURE FAILURE"
  EXIT_CODE=1
fi

echo
read -r -p "Press Return to close..."
exit "$EXIT_CODE"
