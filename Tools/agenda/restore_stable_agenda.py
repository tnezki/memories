#!/usr/bin/env python3
from pathlib import Path
import subprocess

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
GOOD_COMMIT = "2a1f9283004d4c8d463a660bd7639d4307c98c09"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(REPO))


def main():
    run("git", "fetch", "origin", "main")

    # Throw away only the local failed agenda edits.
    run(
        "git", "restore",
        "--source=origin/main",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )

    # Restore the two agenda files from the last visually correct version.
    run(
        "git", "restore",
        f"--source={GOOD_COMMIT}",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("Agenda is already at the good version.", flush=True)
        return

    run("git", "commit", "-m", "Restore stable agenda display")
    run("git", "push", "origin", "main")

    print("", flush=True)
    print("DONE", flush=True)
    print("The live agenda is back to the last version that looked correct.", flush=True)
    print("Do not run any other agenda fix scripts yet.", flush=True)


if __name__ == "__main__":
    main()
