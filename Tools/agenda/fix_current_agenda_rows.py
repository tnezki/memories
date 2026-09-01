#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"
INDEX = REPO / "agenda" / "index.html"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(REPO))


def main():
    # Start from exactly what is currently on GitHub.
    run("git", "fetch", "origin", "main")
    run(
        "git", "restore",
        "--source=origin/main",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )

    text = BUILDER.read_text(encoding="utf-8")

    old = '''        current_date_values = [
            wsv.cell(row=2, column=col).value
            for col in range(1, 6)
        ]
        current_dates = [
            safe_text(value)
            for value in current_date_values
        ]

        current_items = [
            gather_items(
                wsv,
                wsl,
                3,
                9,
                col,
                day_date=current_date_values[col - 1],
                date_to_pacing_key=date_to_pacing_key,
                pacing_links=pacing_links,
            )
            for col in range(1, 6)
        ]
'''

    new = '''        # Find the actual current-calendar header instead of assuming
        # it is at the top of the sheet. Resource rows may appear above it.
        weekday_row = None
        for row in range(1, min(wsv.max_row, 50) + 1):
            labels = [
                safe_text(wsv.cell(row=row, column=col).value)
                for col in range(1, 6)
            ]
            if labels == DAY_NAMES:
                weekday_row = row
                break

        if weekday_row is None:
            raise RuntimeError(
                "Could not find Monday-Friday header in Student Calendar."
            )

        current_date_row = weekday_row + 1
        current_item_start = current_date_row + 1
        current_item_end = current_item_start + 6

        print(
            f"Current calendar located at rows "
            f"{weekday_row}-{current_item_end}"
        )

        current_date_values = [
            wsv.cell(row=current_date_row, column=col).value
            for col in range(1, 6)
        ]
        current_dates = [
            safe_text(value)
            for value in current_date_values
        ]

        current_items = [
            gather_items(
                wsv,
                wsl,
                current_item_start,
                current_item_end,
                col,
                day_date=current_date_values[col - 1],
                date_to_pacing_key=date_to_pacing_key,
                pacing_links=pacing_links,
            )
            for col in range(1, 6)
        ]
'''

    if old not in text:
        raise SystemExit(
            "Expected current-week code was not found. Nothing changed."
        )

    text = text.replace(old, new, 1)

    old_archive = '''        for row in range(11, min(wsv.max_row, 500) + 1):
'''
    new_archive = '''        for row in range(
            current_item_end + 1,
            min(wsv.max_row, 500) + 1,
        ):
'''

    if old_archive not in text:
        raise SystemExit(
            "Expected archive scan code was not found. Nothing changed."
        )

    text = text.replace(old_archive, new_archive, 1)

    BUILDER.write_text(text, encoding="utf-8")
    print("Fixed current-week row detection.", flush=True)

    # Build and verify before commit.
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")

    current_start = page.find('class="week-block current-week"')
    previous_start = page.find('class="previous-weeks-divider"')

    if current_start == -1 or previous_start == -1:
        raise SystemExit("Could not verify current-week HTML. Nothing committed.")

    current_html = page[current_start:previous_start]

    required = [
        "9/28",
        "9/29",
        "9/30",
        "10/1",
        "10/2",
        "1.5: Eqns as Models",
        "Unit 1 Sum Assess",
        "2.1: Rate of Change",
        "Warm Up",
        "Demo",
        "Notes",
        "Investigation",
        "Activity",
        "Practice Set",
    ]

    missing = [item for item in required if item not in current_html]
    if missing:
        raise SystemExit(
            "Current week is still missing: "
            + ", ".join(missing)
            + ". Nothing committed."
        )

    wrong = ["Overview", "Agenda", "Web Site", "Textbook", "Virtual Tools"]
    leaked = [item for item in wrong if item in current_html]
    if leaked:
        raise SystemExit(
            "Resource labels still leaked into current week: "
            + ", ".join(leaked)
            + ". Nothing committed."
        )

    link_count = page.count('<a class="cal-link')
    if link_count < 600:
        raise SystemExit(
            f"Link verification failed: only {link_count} calendar links. "
            "Nothing committed."
        )

    print("Verified correct current week.", flush=True)
    print(f"Verified {link_count} clickable calendar cells.", flush=True)

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")
    run("git", "commit", "-m", "Fix current agenda row detection")
    run("git", "push", "origin", "main")

    print("", flush=True)
    print("DONE", flush=True)
    print("- current week restored", flush=True)
    print("- resource rows excluded from calendar", flush=True)
    print("- clickable links preserved", flush=True)
    print("- previous weeks preserved", flush=True)


if __name__ == "__main__":
    main()
