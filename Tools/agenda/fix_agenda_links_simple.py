#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"
INDEX = REPO / "agenda" / "index.html"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO))


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Could not find expected code for: {label}. Nothing committed.")
    return text.replace(old, new, 1)


def main():
    # Throw away the two failed local link experiments and start from GitHub.
    run("git", "fetch", "origin", "main")
    run(
        "git", "restore",
        "--source=origin/main",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )
    print("Restored known-good agenda files from GitHub.")

    text = BUILDER.read_text(encoding="utf-8")

    # Replace only the workbook-reading section. Styling/rendering stays intact.
    old_start = text.index("\ndef cell_info(ws_values, ws_links, row, col):\n")
    old_end = text.index("\ndef render_link(label, url, kind=\"\"):\n", old_start)

    new_reader = r