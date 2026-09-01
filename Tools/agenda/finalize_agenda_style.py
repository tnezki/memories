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
    run("git", "pull", "--ff-only", "origin", "main")

    text = BUILDER.read_text(encoding="utf-8")

    # ------------------------------------------------------------
    # 1. Current week header: weekday + date in ONE navy cell.
    #    Previous/lower weeks remain date-only.
    # ------------------------------------------------------------
    old = """    if current:
        weekday_row = "".join(
            f"<th><div class='dow'>{d}</div></th>" for d in DAY_NAMES
        )
        date_row = "".join(
            f"<th><div class='date'>{html.escape(x)}</div></th>" for x in dates
        )
        header = (
            f'<tr class="week-head">{weekday_row}</tr>'
            f'<tr class="current-date-row">{date_row}</tr>'
        )
        cls = "current-week"
"""
    new = """    if current:
        cells = "".join(
            f"<th><div class='dow'>{d}</div><div class='date'>{html.escape(x)}</div></th>"
            for d, x in zip(DAY_NAMES, dates)
        )
        header = f'<tr class="week-head">{cells}</tr>'
        cls = "current-week"
"""
    text = replace_once(text, old, new, "combined current weekday/date header")

    # ------------------------------------------------------------
    # 2. Final palette: one consistent navy + brighter gold.
    # ------------------------------------------------------------
    old = """  --navy:#173f6d;
  --navy-dark:#0f2f52;
  --gold:#d9b84f;
  --ink:#1f2937;
  --muted:#64748b;
  --lesson:#fff4c7;
  --link:#173f6d;
"""
    new = """  --navy:#173f6d;
  --navy-dark:#173f6d;
  --gold:#e0bd4f;
  --gold-light:#fff0b8;
  --gold-pale:#fff8df;
  --ink:#1f2937;
  --muted:#64748b;
  --lesson:#fff0b8;
  --link:#173f6d;
"""
    text = replace_once(text, old, new, "final color palette")

    # ------------------------------------------------------------
    # 3. Brighten resource strip to match selected Sample 2.
    # ------------------------------------------------------------
    old = """  border:1px solid #c8b675;
  border-top:0;
  padding:12px 14px 13px;
  display:flex;
  flex-wrap:wrap;
  justify-content:center;
  gap:8px;
  background:#f8f3df;
"""
    new = """  border:1px solid var(--gold);
  border-top:0;
  padding:12px 14px 13px;
  display:flex;
  flex-wrap:wrap;
  justify-content:center;
  gap:8px;
  background:#fff9e9;
"""
    text = replace_once(text, old, new, "resource strip")

    old = """  border:1px solid #c9ad52;
"""
    new = """  border:1px solid var(--gold);
"""
    text = replace_once(text, old, new, "resource pill border")

    old = """  background:var(--lesson);
  border-color:var(--navy);
"""
    new = """  background:var(--gold-light);
  border-color:var(--navy);
"""
    text = replace_once(text, old, new, "resource hover")

    # ------------------------------------------------------------
    # 4. Replace current-week CSS with the final iPad-friendly style.
    # ------------------------------------------------------------
    old = """.current-week .week-head th {{
  background:var(--navy-dark);
  color:#fff;
}}
.current-week .current-date-row th {{
  background:var(--gold);
  color:#10243d;
  padding:7px 6px;
  font-weight:850;
}}
.current-week .current-date-row .date {{ font-size:.95rem; }}
.current-week tr:nth-child(even) td {{ background:#fffaf0; }}
"""
    new = """.current-week .week-head th {{
  background:var(--navy);
  color:#fff;
  text-align:left;
  padding:9px 10px 10px;
}}
.current-week .dow {{
  font-size:1.02rem;
  font-weight:850;
  line-height:1.1;
}}
.current-week .date {{
  margin-top:4px;
  font-size:1.22rem;
  font-weight:900;
  text-align:left;
}}
.current-week td {{
  padding:0;
  height:48px;
  min-height:48px;
  background:#fff;
}}
.current-week .cal-link {{
  display:flex;
  align-items:center;
  justify-content:center;
  width:100%;
  min-height:48px;
  padding:10px 8px;
  font-size:1.08rem;
  font-weight:750;
  line-height:1.25;
}}
.current-week .cal-link.lesson {{
  background:#fff;
  border:0;
  color:var(--navy);
  font-size:1.12rem;
  font-weight:900;
  text-decoration:underline;
}}
.current-week .cal-link.holiday {{
  font-size:1.08rem;
  font-weight:900;
}}
.current-week tr:nth-child(odd):not(.week-head) td {{
  background:var(--gold-light);
}}
"""
    text = replace_once(text, old, new, "current week final CSS")

    # ------------------------------------------------------------
    # 5. Gold divider uses the final gold.
    # ------------------------------------------------------------
    old = """  background:#d9b84f !important;
"""
    new = """  background:var(--gold) !important;
"""
    text = replace_once(text, old, new, "previous weeks divider gold")

    # ------------------------------------------------------------
    # 6. Lower calendar current-week highlight: same school-color
    #    language, but date-only as requested.
    # ------------------------------------------------------------
    old = """.calendar-current-week .week-head th {{
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
"""
    new = """.calendar-current-week .week-head th {{
  background:var(--navy);
  color:#fff;
  border-top:5px solid var(--gold);
  padding:8px 9px;
  font-weight:850;
  text-align:left;
}}
.calendar-current-week .week-head th .date {{
  color:#fff;
  font-size:1rem;
  font-weight:900;
  text-align:left;
}}
.calendar-current-week tr td {{
  background:#fff !important;
  border-color:#cfd4da;
}}
.calendar-current-week tr:nth-child(odd):not(.week-head) td {{
  background:var(--gold-light) !important;
}}
.calendar-current-week .cal-link.lesson {{
  background:#fff;
  border:0;
  color:var(--navy);
  font-weight:900;
  text-decoration:underline;
}}
.calendar-current-week .cal-link.holiday {{
  background:#f6edcf;
  color:#475569;
}}
"""
    text = replace_once(text, old, new, "lower current-week final CSS")

    # ------------------------------------------------------------
    # 7. All lower/history dates left aligned.
    # ------------------------------------------------------------
    old = """.previous-week .week-head th {{
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
}}
"""
    new = """.previous-week .week-head th {{
  background:#3f4650;
  color:#fff;
  border-top:5px solid #20242a;
  text-align:left;
  padding-left:9px;
}}
"""
    text = replace_once(text, old, new, "left aligned previous dates")

    BUILDER.write_text(text, encoding="utf-8")
    print("Applied final agenda styling to build_agenda.py.")

    # Build locally before committing.
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")

    checks = {
        "combined weekday/date": "<div class='dow'>Monday</div><div class='date'>" in page,
        "iPad 48px target": "min-height:48px" in page,
        "single navy": "--navy-dark:#173f6d" in page,
        "bright gold bands": "--gold-light:#fff0b8" in page,
        "previous weeks": "Previous Weeks" in page,
        "lower current highlight": "calendar-current-week" in page,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Verification failed: " + ", ".join(failed) + ". Nothing committed.")

    print("Local build verified:")
    for name in checks:
        print("  OK - " + name)

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
        "Finalize student agenda styling",
    )
    run("git", "push", "origin", "main")

    print()
    print("FINAL UPDATE COMPLETE")
    print("- Sample 2 color direction applied")
    print("- one consistent navy")
    print("- current weekday + date combined")
    print("- all dates left aligned")
    print("- larger/bolder current-week text")
    print("- 48px iPad-friendly current-week tap targets")
    print("- previous weeks remain gray/black/white")
    print("- 5-minute GitHub workflow unchanged")


if __name__ == "__main__":
    main()
