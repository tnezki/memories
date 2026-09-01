#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import re

REPO = Path("/Users/troynezki/Documents/GitHub/algebra")
BUILDER = REPO / "agenda" / "build_agenda.py"
INDEX = REPO / "agenda" / "index.html"
WORKFLOW = REPO / ".github" / "workflows" / "update-agenda.yml"
GOOD_COMMIT = "2a1f9283004d4c8d463a660bd7639d4307c98c09"


def run(*args):
    cmd = [str(x) for x in args]
    print("$ " + " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(REPO))


def pause_and_restore():
    run("git", "pull", "--ff-only", "origin", "main")

    run(
        "git", "restore",
        f"--source={GOOD_COMMIT}",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )

    workflow = WORKFLOW.read_text(encoding="utf-8")
    scheduled = 'on:\n  workflow_dispatch:\n  schedule:\n    - cron: "*/5 * * * *"\n'
    paused = 'on:\n  workflow_dispatch:\n'

    if scheduled in workflow:
        workflow = workflow.replace(scheduled, paused, 1)
        WORKFLOW.write_text(workflow, encoding="utf-8")

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

    if changed:
        run("git", "commit", "-m", "Freeze stable agenda for clean rebuild")
        run("git", "push", "origin", "main")

    print("Stable backup restored and automatic rebuilds paused.", flush=True)


def install_new_reader():
    text = BUILDER.read_text(encoding="utf-8")

    start = text.index("\ndef cell_info(ws_values, ws_links, row, col):\n")
    end = text.index("\ndef download_workbook():\n", start)

    helper_block = r'''

def direct_cell_link(cell):
    if cell.hyperlink and cell.hyperlink.target:
        return cell.hyperlink.target

    formula = cell.value
    if isinstance(formula, str) and formula.startswith("="):
        match = re.search(r'HYPERLINK\(\s*"([^"]+)"', formula, re.I)
        if match:
            return match.group(1)

    return None


def normalized_key(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def normalized_label(value):
    return re.sub(r"\s+", " ", safe_text(value)).strip().casefold()


def build_date_to_pacing_key(teacher_values):
    mapping = {}

    for row in range(1, min(teacher_values.max_row, 600) + 1):
        date_values = [
            teacher_values.cell(row=row, column=col).value
            for col in range(4, 9)
        ]

        if sum(1 for value in date_values if looks_like_date(value)) < 4:
            continue

        for day_index, date_value in enumerate(date_values):
            key_date = date_key(date_value)
            if not key_date:
                continue

            key_col = 9 + day_index
            pacing_key = None

            for source_row in range(
                row + 1,
                min(row + 12, teacher_values.max_row + 1),
            ):
                candidate = normalized_key(
                    teacher_values.cell(
                        row=source_row,
                        column=key_col,
                    ).value
                )
                if candidate not in (None, ""):
                    pacing_key = candidate
                    break

            if pacing_key not in (None, ""):
                mapping[key_date] = pacing_key

    return mapping


def build_pacing_link_lookup(pacing_values, pacing_formulas):
    lookup = {}
    direct_link_count = 0

    for row in range(1, min(pacing_values.max_row, 500) + 1):
        pacing_key = normalized_key(
            pacing_values.cell(row=row, column=1).value
        )
        if pacing_key in (None, ""):
            continue

        row_links = lookup.setdefault(pacing_key, {})

        for col in range(2, min(pacing_values.max_column, 26) + 1):
            label = safe_text(
                pacing_values.cell(row=row, column=col).value
            )
            if not label:
                continue

            link = (
                direct_cell_link(
                    pacing_formulas.cell(row=row, column=col)
                )
                or direct_cell_link(
                    pacing_values.cell(row=row, column=col)
                )
            )

            if link:
                direct_link_count += 1
                row_links.setdefault(normalized_label(label), link)

    return lookup, direct_link_count


def cell_info(
    ws_values,
    ws_links,
    row,
    col,
    day_date=None,
    date_to_pacing_key=None,
    pacing_links=None,
):
    vc = ws_values.cell(row=row, column=col)
    lc = ws_links.cell(row=row, column=col)

    label = safe_text(vc.value)
    link = direct_cell_link(vc) or direct_cell_link(lc)

    if (
        not link
        and label
        and day_date is not None
        and date_to_pacing_key is not None
        and pacing_links is not None
    ):
        key_date = date_key(day_date)
        pacing_key = (
            date_to_pacing_key.get(key_date)
            if key_date is not None
            else None
        )

        if pacing_key is not None:
            link = pacing_links.get(pacing_key, {}).get(
                normalized_label(label)
            )

    return label, link


def gather_items(
    ws_values,
    ws_links,
    start_row,
    end_row,
    col,
    day_date=None,
    date_to_pacing_key=None,
    pacing_links=None,
):
    items = []

    for row in range(start_row, end_row + 1):
        label, url = cell_info(
            ws_values,
            ws_links,
            row,
            col,
            day_date=day_date,
            date_to_pacing_key=date_to_pacing_key,
            pacing_links=pacing_links,
        )
        if label:
            items.append((label, url))

    return items

'''

    text = text[:start] + helper_block + text[end:]

    start = text.index("\ndef read_calendar():\n")
    end = text.index("\ndef render_link(label, url, kind=\"\"):\n", start)

    read_block = r'''

def read_calendar():
    xlsx = download_workbook()

    try:
        wb_values = load_workbook(xlsx, data_only=True, read_only=False)
        wb_links = load_workbook(xlsx, data_only=False, read_only=False)

        required = (SHEET_NAME, "Teacher Calendar", "Pacing")
        for sheet_name in required:
            if sheet_name not in wb_values.sheetnames:
                raise RuntimeError(f"Missing sheet: {sheet_name}")

        wsv = wb_values[SHEET_NAME]
        wsl = wb_links[SHEET_NAME]
        teacher_values = wb_values["Teacher Calendar"]
        pacing_values = wb_values["Pacing"]
        pacing_formulas = wb_links["Pacing"]

        weekday_row = None
        for row in range(1, min(wsv.max_row, 60) + 1):
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

        marker_row = None
        for row in range(current_date_row + 1, min(wsv.max_row, 100) + 1):
            label = safe_text(wsv.cell(row=row, column=1).value)
            if label.lower().startswith("previous weeks"):
                marker_row = row
                break

        if marker_row is None:
            raise RuntimeError(
                "Could not find the Previous Weeks marker in Student Calendar."
            )

        current_item_start = current_date_row + 1
        current_item_end = marker_row - 1

        current_date_values = [
            wsv.cell(row=current_date_row, column=col).value
            for col in range(1, 6)
        ]

        if sum(1 for value in current_date_values if looks_like_date(value)) < 4:
            raise RuntimeError(
                "Current date row does not contain a normal Monday-Friday week."
            )

        date_to_pacing_key = build_date_to_pacing_key(teacher_values)
        pacing_links, direct_link_count = build_pacing_link_lookup(
            pacing_values,
            pacing_formulas,
        )

        print(
            f"Student Calendar layout: weekdays row {weekday_row}, "
            f"dates row {current_date_row}, "
            f"activities rows {current_item_start}-{current_item_end}, "
            f"previous weeks start after row {marker_row}"
        )
        print(
            "Current dates: "
            + ", ".join(safe_text(value) for value in current_date_values)
        )
        print(f"Pacing direct hyperlinks available: {direct_link_count}")

        if direct_link_count < 100:
            raise RuntimeError("Too few Pacing hyperlinks were found.")

        current_dates = [safe_text(value) for value in current_date_values]

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

        current_start = next(
            (
                date_key(value)
                for value in current_date_values
                if date_key(value)
            ),
            None,
        )

        archive_date_rows = []
        for row in range(marker_row + 1, min(wsv.max_row, 500) + 1):
            values = [
                wsv.cell(row=row, column=col).value
                for col in range(1, 6)
            ]
            if sum(1 for value in values if looks_like_date(value)) >= 4:
                archive_date_rows.append(row)

        previous = []

        for i, date_row in enumerate(archive_date_rows):
            next_date_row = (
                archive_date_rows[i + 1]
                if i + 1 < len(archive_date_rows)
                else min(date_row + 12, wsv.max_row + 1)
            )

            archive_date_values = [
                wsv.cell(row=date_row, column=col).value
                for col in range(1, 6)
            ]
            dates = [safe_text(value) for value in archive_date_values]

            start_date = next(
                (
                    date_key(value)
                    for value in archive_date_values
                    if date_key(value)
                ),
                None,
            )

            is_current = bool(
                current_start
                and start_date
                and start_date == current_start
            )

            end_row = next_date_row - 1

            items = [
                gather_items(
                    wsv,
                    wsl,
                    date_row + 1,
                    end_row,
                    col,
                    day_date=archive_date_values[col - 1],
                    date_to_pacing_key=date_to_pacing_key,
                    pacing_links=pacing_links,
                )
                for col in range(1, 6)
            ]

            if any(items):
                previous.append(
                    {
                        "dates": dates,
                        "items": items,
                        "is_current": is_current,
                    }
                )

        return {
            "current": {
                "dates": current_dates,
                "items": current_items,
            },
            "previous": previous,
        }

    finally:
        try:
            xlsx.unlink()
        except OSError:
            pass

'''

    text = text[:start] + read_block + text[end:]
    text = text.replace("text-decoration:underline;", "text-decoration:none;")
    BUILDER.write_text(text, encoding="utf-8")


def verify_build():
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")
    current_start = page.find('class="week-block current-week"')
    previous_start = page.find('class="previous-weeks-divider"')

    if current_start == -1 or previous_start == -1:
        raise SystemExit("Could not verify generated calendar structure.")

    current_html = page[current_start:previous_start]

    for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
        if day not in current_html:
            raise SystemExit(f"Current week is missing {day}.")

    date_hits = re.findall(r"\b\d{1,2}/\d{1,2}\b", current_html)
    if len(set(date_hits)) < 4:
        raise SystemExit(
            "Current week did not generate a normal set of dates."
        )

    link_count = page.count('<a class="cal-link')
    if link_count < 100:
        raise SystemExit(
            f"Only {link_count} clickable calendar cells were generated."
        )

    if "text-decoration:underline" in page:
        raise SystemExit("Underline CSS still remains.")

    print(f"Verified {link_count} clickable calendar cells.", flush=True)
    print("Verified current week without assuming a specific date.", flush=True)
    print("Verified previous weeks and no-underlines style.", flush=True)


def resume_and_push():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    paused = 'on:\n  workflow_dispatch:\n'
    scheduled = 'on:\n  workflow_dispatch:\n  schedule:\n    - cron: "*/5 * * * *"\n'

    if scheduled not in workflow:
        if paused not in workflow:
            raise SystemExit(
                "Could not recognize workflow trigger block; leaving it paused."
            )
        workflow = workflow.replace(paused, scheduled, 1)
        WORKFLOW.write_text(workflow, encoding="utf-8")

    run(
        "git", "add",
        "agenda/build_agenda.py",
        "agenda/index.html",
        ".github/workflows/update-agenda.yml",
    )
    run("git", "commit", "-m", "Rebuild agenda for new Student Calendar layout")
    run("git", "push", "origin", "main")

    print("", flush=True)
    print("DONE", flush=True)
    print("- new Student Calendar layout detected automatically", flush=True)
    print("- current week no longer depends on fixed row numbers", flush=True)
    print("- calendar links restored from Pacing", flush=True)
    print("- previous weeks preserved", flush=True)
    print("- 5-minute backup updater resumed", flush=True)


def main():
    pause_and_restore()
    install_new_reader()
    verify_build()
    resume_and_push()


if __name__ == "__main__":
    main()
