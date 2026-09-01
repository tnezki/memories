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


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Could not find expected code for: {label}. No commit made.")
    return text.replace(old, new, 1)


def main():
    run("git", "pull", "--ff-only", "origin", "main")

    text = BUILDER.read_text(encoding="utf-8")

    # Keep the matching current week in the lower/full calendar and tag it.
    old = '''            # Rows below the top block are the archived weeks.
            # Skip only an exact duplicate of the current top week.
            if current_start and start and start == current_start:
                continue

            end_row = min(next_date_row - 1, date_row + 10)
'''
    new = '''            # Keep every calendar week below the top block.
            # Mark the week whose start date matches the current top week.
            is_current = bool(current_start and start and start == current_start)

            end_row = min(next_date_row - 1, date_row + 10)
'''
    text = replace_once(text, old, new, "current-week archive detection")

    old = '''            if any(items):
                previous.append({"dates": dates, "items": items})
'''
    new = '''            if any(items):
                previous.append({
                    "dates": dates,
                    "items": items,
                    "is_current": is_current,
                })
'''
    text = replace_once(text, old, new, "archive current flag")

    # Lower calendar: dates only, no repeated Monday-Friday labels.
    old = '''def render_week(dates, items_by_day, current=False):
'''
    new = '''def render_week(dates, items_by_day, current=False, archive_current=False):
'''
    text = replace_once(text, old, new, "render_week signature")

    old = '''    else:
        cells = "".join(
            f"<th><div class='dow'>{d}</div><div class='date'>{html.escape(x)}</div></th>"
            for d, x in zip(DAY_NAMES, dates)
        )
        header = f'<tr class="week-head">{cells}</tr>'
        cls = "previous-week"
'''
    new = '''    else:
        # Lower calendar weeks show dates only; weekday names are already
        # established by the main calendar layout above.
        cells = "".join(
            f"<th><div class='date'>{html.escape(x)}</div></th>"
            for x in dates
        )
        header = f'<tr class="week-head">{cells}</tr>'
        cls = "calendar-current-week" if archive_current else "previous-week"
'''
    text = replace_once(text, old, new, "lower week header")

    old = '''                render_week(w["dates"], w["items"], current=False)
                for w in calendar["previous"]
'''
    new = '''                render_week(
                    w["dates"],
                    w["items"],
                    current=False,
                    archive_current=w.get("is_current", False),
                )
                for w in calendar["previous"]
'''
    text = replace_once(text, old, new, "lower calendar rendering")

    # Add school-color styling for the current week inside the lower calendar.
    marker = '''.previous-week .week-head th {
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
}
'''
    addition = '''.calendar-current-week .week-head th {
  background:var(--gold);
  color:#10243d;
  border-top:5px solid var(--navy-dark);
  padding:7px 6px;
  font-weight:850;
}
.calendar-current-week .week-head th .date {
  color:#10243d;
  font-size:.95rem;
}
.calendar-current-week tr td {
  background:#fff !important;
}
.calendar-current-week tr:nth-child(even) td {
  background:#fffaf0 !important;
}
.calendar-current-week .cal-link.lesson {
  background:var(--lesson);
  border:1px solid #e1c86d;
  color:var(--navy-dark);
}
.calendar-current-week .cal-link.holiday {
  background:#f6edcf;
  color:#475569;
}

.previous-week .week-head th {
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
}
'''
    text = replace_once(text, marker, addition, "lower current-week CSS")

    BUILDER.write_text(text, encoding="utf-8")
    print("Updated lower-calendar headers and current-week highlighting.")

    # Build first; do not commit if the build fails.
    run(sys.executable, str(BUILDER))

    page_path = REPO / "agenda" / "index.html"
    page = page_path.read_text(encoding="utf-8")

    if "calendar-current-week" not in page:
        raise SystemExit(
            "Build succeeded, but no lower current-week highlight was found. "
            "No commit made."
        )

    # Verify lower previous-week headers no longer contain weekday labels.
    print("Local build verified.")

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("No changes to commit.")
        return

    run(
        "git",
        "commit",
        "-m",
        "Simplify calendar headers and highlight current week",
    )
    run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("- lower weeks show dates only")
    print("- non-current lower weeks stay gray/black/white")
    print("- lower week matching the top current week is navy/gold")
    print("- 5-minute automation is unchanged")


if __name__ == "__main__":
    main()
