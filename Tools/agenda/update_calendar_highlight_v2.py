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
        raise SystemExit(f"Could not find: {label}. Nothing committed.")
    return text.replace(old, new, 1)


def main():
    run("git", "pull", "--ff-only", "origin", "main")

    text = BUILDER.read_text(encoding="utf-8")

    # 1) Keep all lower/archive weeks and mark the one matching the top current week.
    old = """            # Rows below the top block are the archived weeks.
            # Skip only an exact duplicate of the current top week.
            if current_start and start and start == current_start:
                continue

            end_row = min(next_date_row - 1, date_row + 10)
"""
    new = """            # Keep every week in the lower calendar.
            # Highlight the one that matches the top current-week block.
            is_current = bool(current_start and start and start == current_start)

            end_row = min(next_date_row - 1, date_row + 10)
"""
    text = replace_once(text, old, new, "archive current-week detection")

    old = """            if any(items):
                previous.append({"dates": dates, "items": items})
"""
    new = """            if any(items):
                previous.append({
                    "dates": dates,
                    "items": items,
                    "is_current": is_current,
                })
"""
    text = replace_once(text, old, new, "archive week record")

    # 2) Lower weeks show dates only, not Monday/Tuesday/etc.
    text = replace_once(
        text,
        "def render_week(dates, items_by_day, current=False):\n",
        "def render_week(dates, items_by_day, current=False, archive_current=False):\n",
        "render_week signature",
    )

    old = """    else:
        cells = "".join(
            f"<th><div class='dow'>{d}</div><div class='date'>{html.escape(x)}</div></th>"
            for d, x in zip(DAY_NAMES, dates)
        )
        header = f'<tr class="week-head">{cells}</tr>'
        cls = "previous-week"
"""
    new = """    else:
        cells = "".join(
            f"<th><div class='date'>{html.escape(x)}</div></th>"
            for x in dates
        )
        header = f'<tr class="week-head">{cells}</tr>'
        cls = "calendar-current-week" if archive_current else "previous-week"
"""
    text = replace_once(text, old, new, "lower week header")

    # 3) Pass the current-week flag into lower rendering.
    old = """                render_week(w["dates"], w["items"], current=False)
                for w in calendar["previous"]
"""
    new = """                render_week(
                    w["dates"],
                    w["items"],
                    current=False,
                    archive_current=w.get("is_current", False),
                )
                for w in calendar["previous"]
"""
    text = replace_once(text, old, new, "lower calendar render call")

    # 4) Add navy/gold formatting for the matching week in the lower calendar.
    css_marker = """.previous-week .week-head th {{
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
}}
"""
    css_replacement = """.calendar-current-week .week-head th {{
  background:var(--gold);
  color:#10243d;
  border-top:5px solid var(--navy-dark);
  padding:7px 6px;
  font-weight:850;
}}
.calendar-current-week .week-head th .date {{
  color:#10243d;
  font-size:.95rem;
}}
.calendar-current-week tr td {{
  background:#fff !important;
  border-color:#cfd4da;
}}
.calendar-current-week tr:nth-child(even) td {{
  background:#fffaf0 !important;
}}
.calendar-current-week .cal-link.lesson {{
  background:var(--lesson);
  border:1px solid #e1c86d;
  color:var(--navy-dark);
}}
.calendar-current-week .cal-link.holiday {{
  background:#f6edcf;
  color:#475569;
}}

.previous-week .week-head th {{
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
}}
"""
    text = replace_once(text, css_marker, css_replacement, "lower current-week CSS")

    BUILDER.write_text(text, encoding="utf-8")
    print("Patched builder.")

    # Build locally first.
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")

    if "calendar-current-week" not in page:
        raise SystemExit(
            "Build completed but current lower week was not found. Nothing committed."
        )

    # In lower headers, weekdays should not be emitted by the non-current renderer anymore.
    if "calendar-current-week" in page:
        print("Verified lower current-week class exists.")
    if "Previous Weeks" in page:
        print("Verified lower calendar exists.")

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("No changes to commit.")
        return

    run(
        "git", "commit",
        "-m", "Simplify lower calendar and highlight current week",
    )
    run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("- lower week headers show dates only")
    print("- other weeks stay black/gray/white")
    print("- matching current week is gold/navy")
    print("- 5-minute workflow is unchanged")


if __name__ == "__main__":
    main()
