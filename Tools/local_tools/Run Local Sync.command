#!/bin/bash
set -u

ACTION="${1:-}"
if [[ "$ACTION" != "pull" && "$ACTION" != "push" ]]; then
  echo "Usage: $0 pull|push"
  exit 2
fi

detect_root() {
  if [[ -n "${GITHUB_ROOT:-}" && -d "$GITHUB_ROOT" ]]; then
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
REPOS=("memories" "algebra" "physics" "apcalc" "teacher_shared")
FAILURES=0
STAMP="$(date '+%Y-%m-%d %H:%M')"
COMMIT_MESSAGE="Local Tools sync ${STAMP}"

fail_banner() {
  echo
  echo "FAILURE FAILURE FAILURE"
  echo "LOCAL TOOLS SYNC FAILURE"
  echo "FAILURE FAILURE FAILURE"
  echo
}

success_banner() {
  echo
  echo "SUCCESS SUCCESS SUCCESS"
  if [[ "$ACTION" == "pull" ]]; then
    echo "LOCAL TOOLS PULL SUCCESS"
  else
    echo "LOCAL TOOLS COMMIT + PUSH SUCCESS"
  fi
  echo "SUCCESS SUCCESS SUCCESS"
  echo
}

normalize_tnezki_origin_to_ssh() {
  local repo="$1"
  local remote="$2"
  case "$remote" in
    https://github.com/tnezki/*.git)
      local suffix="${remote#https://github.com/tnezki/}"
      local ssh="git@github.com:tnezki/${suffix}"
      if git -C "$repo" remote set-url origin "$ssh"; then
        echo "Normalized origin to SSH: $ssh"
        printf '%s\n' "$ssh"
        return 0
      fi
      ;;
    https://github.com/tnezki/*)
      local suffix="${remote#https://github.com/tnezki/}"
      local ssh="git@github.com:tnezki/${suffix}.git"
      if git -C "$repo" remote set-url origin "$ssh"; then
        echo "Normalized origin to SSH: $ssh"
        printf '%s\n' "$ssh"
        return 0
      fi
      ;;
  esac
  printf '%s\n' "$remote"
  return 0
}

if [[ -z "$ROOT" ]]; then
  echo "Could not locate the GitHub workspace root."
  fail_banner
  read -r -p "Press Return to close..."
  exit 1
fi

echo
echo "Local Tools - Curriculum Sync"
echo "============================="
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
    echo "FAILED: not a Git repository: $repo"
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  gitdir="$(git -C "$repo" rev-parse --git-dir 2>/dev/null || true)"
  if [[ -n "$gitdir" ]]; then
    case "$gitdir" in
      /*) abs_gitdir="$gitdir" ;;
      *) abs_gitdir="$repo/$gitdir" ;;
    esac
    if [[ -d "$abs_gitdir/rebase-merge" || -d "$abs_gitdir/rebase-apply" || -f "$abs_gitdir/MERGE_HEAD" ]]; then
      echo "FAILED: merge/rebase already in progress. Resolve it manually first."
      FAILURES=$((FAILURES + 1))
      echo
      continue
    fi
  fi

  branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  remote="$(git -C "$repo" remote get-url origin 2>/dev/null || true)"
  echo "Branch: ${branch:-unknown}"
  echo "Origin: ${remote:-missing}"

  if [[ -n "$remote" ]]; then
    normalized="$(normalize_tnezki_origin_to_ssh "$repo" "$remote")"
    remote="$(printf '%s\n' "$normalized" | tail -n 1)"
  fi

  if [[ "$ACTION" == "pull" ]]; then
    if [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]]; then
      echo "BLOCKED: local changes are present. Pull All will not stash or modify them."
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

  if ! git -C "$repo" add -A; then
    echo "FAILED: could not stage $name"
    FAILURES=$((FAILURES + 1))
    echo
    continue
  fi

  if ! git -C "$repo" diff --cached --quiet; then
    if git -C "$repo" commit -m "$COMMIT_MESSAGE"; then
      echo "COMMITTED: $name"
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
  success_banner
  EXIT_CODE=0
else
  echo "$FAILURES repository issue(s) require attention."
  fail_banner
  EXIT_CODE=1
fi

read -r -p "Press Return to close..."
exit "$EXIT_CODE"
