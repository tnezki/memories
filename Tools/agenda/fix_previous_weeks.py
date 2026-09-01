#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO))


def main():
    run("git", "pull", "--ff-only", "origin", "main")

    text = BUILDER.read_text(encoding="utf-8")

    old = "            if current_start and start and start >= current_start:\n                continue\n"
    new = (
        "            # Rows below the top block are the archived weeks.\n"
        "            # Skip only an exact duplicate of the current top week.\n"
        "            if current_start and start and start == current_start:\n"
        "                continue\n"
    )

    if old not in text:
        raise SystemExit("Expected previous-week filter was not found. No files changed.")

    BUILDER.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Fixed previous-week filtering.")

    run(sys.executable, str(BUILDER))

    page = (REPO / "agenda" / "index.html").read_text(encoding="utf-8")
    if "Previous Weeks" not in page:
        raise SystemExit("Build completed, but Previous Weeks still did not render.")

    print("Previous Weeks rendered successfully.")

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if changed:
        run("git", "commit", "-m", "Restore previous weeks on agenda")
        run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("- current week stays navy/gold")
    print("- archived weeks render below it")
    print("- archived weeks keep the existing black/gray/white styling")


if __name__ == "__main__":
    main()
