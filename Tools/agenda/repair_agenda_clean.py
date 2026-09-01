#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"
WORKFLOW = REPO / ".github" / "workflows" / "update-agenda.yml"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO))


def main():
    if not REPO.exists():
        raise SystemExit(f"Repo not found: {REPO}")

    run("git", "fetch", "origin", "main")

    run(
        "git", "restore",
        "--source=origin/main",
        "--",
        "agenda/build_agenda.py",
        ".github/workflows/update-agenda.yml",
    )
    print("Restored original automation files from GitHub.")

    text = BUILDER.read_text(encoding="utf-8")

    old_value = "    value = vc.value if vc.value is not None else lc.value\n"
    new_value = (
        "    # Keep evaluated blank formulas blank instead of displaying the formula.\n"
        "    value = vc.value\n"
    )
    if old_value not in text:
        raise SystemExit("Expected cell-value line was not found after restore.")
    text = text.replace(old_value, new_value, 1)

    old_safe = 'def safe_text(value):\n    if value is None:\n        return ""\n'
    new_safe = (
        'def safe_text(value):\n'
        '    if value is None or value.__class__.__name__ == "ArrayFormula":\n'
        '        return ""\n'
    )
    if old_safe not in text:
        raise SystemExit("Expected safe_text function was not found after restore.")
    text = text.replace(old_safe, new_safe, 1)

    BUILDER.write_text(text, encoding="utf-8")
    print("Fixed blank formula rendering.")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    if 'cron: "*/15 * * * *"' in workflow:
        workflow = workflow.replace(
            'cron: "*/15 * * * *"',
            'cron: "*/5 * * * *"',
            1,
        )
    WORKFLOW.write_text(workflow, encoding="utf-8")
    print("Set automatic check to every 5 minutes.")

    run(sys.executable, str(BUILDER))

    page = (REPO / "agenda" / "index.html").read_text(encoding="utf-8")
    bad_markers = [
        "='Teacher Calendar'",
        "ArrayFormula object",
        "openpyxl.worksheet.formula",
    ]
    found = [x for x in bad_markers if x in page]
    if found:
        raise SystemExit(
            "Build finished, but bad formula text is still present: "
            + ", ".join(found)
        )

    print("Local build looks clean.")

    run(
        "git", "add",
        "agenda/build_agenda.py",
        "agenda/index.html",
        ".github/workflows/update-agenda.yml",
    )

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("No changes to commit.")
        return

    run(
        "git", "commit",
        "-m", "Fix blank agenda cells and update every 5 minutes",
    )
    run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("- blank formula cells stay blank")
    print("- array-formula placeholders stay blank")
    print("- automatic GitHub check is every 5 minutes")
    print("- corrected agenda was rebuilt and pushed")


if __name__ == "__main__":
    main()
