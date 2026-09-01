#!/usr/bin/env python3
from pathlib import Path
import subprocess

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"
WORKFLOW = REPO / ".github" / "workflows" / "update-agenda.yml"

def run(*args):
    print("$ " + " ".join(args))
    subprocess.check_call(list(args), cwd=str(REPO))

def main():
    run("git", "pull", "--ff-only", "origin", "main")

    text = BUILDER.read_text(encoding="utf-8")

    old = "    value = vc.value if vc.value is not None else lc.value\n    link = None\n"
    new = (
        "    # Use only the evaluated/displayed value for cell text.\n"
        "    # If a formula evaluates to blank, keep it blank instead of showing the formula.\n"
        "    value = vc.value\n"
        "    link = None\n"
    )

    if old not in text:
        raise SystemExit("Could not find the expected cell-value code to patch.")

    text = text.replace(old, new, 1)
    BUILDER.write_text(text, encoding="utf-8")
    print("Fixed blank-formula rendering in build_agenda.py")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    workflow = workflow.replace('cron: "*/15 * * * *"', 'cron: "*/5 * * * *"')
    WORKFLOW.write_text(workflow, encoding="utf-8")
    print("Changed GitHub schedule to every 5 minutes.")

    run("/usr/local/bin/python3", str(BUILDER))

    run(
        "git", "add",
        "agenda/build_agenda.py",
        "agenda/index.html",
        ".github/workflows/update-agenda.yml",
    )

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO)
    )

    if result.returncode == 0:
        print("No changes to commit.")
        return

    run("git", "commit", "-m", "Fix blank agenda formulas and update every 5 minutes")
    run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("Blank formula cells will stay blank.")
    print("GitHub Actions will check every 5 minutes.")

if __name__ == "__main__":
    main()
