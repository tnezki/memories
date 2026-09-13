#!/usr/bin/env python3
"""Run the canonical curriculum finalizer on the folder containing this file.

Manual convenience helper.

Workflow:
1. Copy this file into the exact folder you want to clean.
2. Run/double-click the file using Python / your VS Code Python runner.
3. The helper searches upward for the project-root ``memories/Tools`` folder.
4. It runs the canonical ``finalize_output.py`` recursively on ONLY the folder
   containing this helper.
5. Review changed files in GitHub Desktop before committing.

This wrapper does not contain its own MathJax repair rules. It always delegates
to the current canonical finalizer, so improvements to the canonical MathJax and
currency tools automatically apply here too.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def find_finalizer(target: Path) -> Path | None:
    """Locate canonical memories/Tools/finalize_output.py without leaving project tree."""
    candidates: list[Path] = []

    # If this helper is sitting in memories/Tools, use the sibling directly.
    candidates.append(target / "finalize_output.py")

    # If copied anywhere inside a course repo, project root is normally an ancestor
    # containing a sibling memories/ folder.
    for base in (target, *target.parents):
        candidates.append(base / "memories" / "Tools" / "finalize_output.py")
        # Also support a target somewhere inside the memories repo itself.
        candidates.append(base / "Tools" / "finalize_output.py")

    seen: set[Path] = set()
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
        except OSError:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file():
            return candidate
    return None


def pause_if_interactive() -> None:
    """Keep a double-click terminal window open long enough to read the result."""
    try:
        if sys.stdin.isatty():
            input("\nPress Return to close...")
    except (EOFError, KeyboardInterrupt):
        pass


def main() -> int:
    target = Path(__file__).resolve().parent
    finalizer = find_finalizer(target)

    print("=" * 64)
    print("Curriculum MathJax Folder Cleaner")
    print("=" * 64)
    print(f"Target folder : {target}")

    if finalizer is None:
        print("\nFAIL: Could not locate memories/Tools/finalize_output.py")
        print("Place this helper somewhere inside your Curriculum GitHub project tree")
        print("(for example inside algebra/, physics/, calculus/, or memories/).")
        pause_if_interactive()
        return 2

    print(f"Finalizer    : {finalizer}")
    print("\nScanning only this folder and its subfolders...\n")

    env = os.environ.copy()
    proc = subprocess.run(
        [sys.executable, str(finalizer), str(target)],
        cwd=str(target),
        env=env,
    )

    print("\n" + "=" * 64)
    if proc.returncode == 0:
        print("PASS: Folder cleanup completed.")
        print("Review the changed files in GitHub Desktop before committing.")
    else:
        print("CHECK REQUIRED: The finalizer reported one or more warnings/failures.")
        print("Review the messages above. Ambiguous cases are intentionally not guessed.")
    print("=" * 64)

    pause_if_interactive()
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
