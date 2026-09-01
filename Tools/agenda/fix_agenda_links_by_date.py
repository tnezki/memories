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
    # Always start from the known-good GitHub version.
    run("git", "fetch", "origin", "main")
    run(
        "git", "restore",
        "--source=origin/main",
        "--",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )
    print("Restored known-good agenda files from GitHub.", flush=True)

    text = BUILDER.read_text(encoding="utf-8")

    # ------------------------------------------------------------
    # Replace the hyperlink helper section.
    # ------------------------------------------------------------
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

    # Teacher Calendar historical/current week blocks use dates in D:H.
    # The corresponding Pacing day number is repeated in I:M on the
    # content rows directly below each date row.
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

            # The key is normally in row+1, and is repeated down the block.
            # Search a few rows so holidays/blank first rows do not matter.
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

    # Keep evaluated blank formulas blank instead of displaying the formula.
    value = vc.value
    label = safe_text(value)

    link = direct_cell_link(vc) or direct_cell_link(lc)

    # Google XLSX export drops hyperlinks inherited through formulas on
    # Student Calendar. Restore them by date/day-number + exact displayed label.
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

    # ------------------------------------------------------------
    # Replace only read_calendar(). Rendering/design stays untouched.
    # ------------------------------------------------------------
    start = text.index("\ndef read_calendar():\n")
    end = text.index("\ndef render_link(label, url, kind=\"\"):\n", start)

    read_calendar_block = r'''

def read_calendar():
    xlsx = download_workbook()

    try:
        wb_values = load_workbook(
            xlsx,
            data_only=True,
            read_only=False,
        )
        wb_links = load_workbook(
            xlsx,
            data_only=False,
            read_only=False,
        )

        required = (SHEET_NAME, "Teacher Calendar", "Pacing")
        for sheet_name in required:
            if sheet_name not in wb_values.sheetnames:
                raise RuntimeError(f"Missing sheet: {sheet_name}")

        wsv = wb_values[SHEET_NAME]
        wsl = wb_links[SHEET_NAME]

        teacher_values = wb_values["Teacher Calendar"]
        pacing_values = wb_values["Pacing"]
        pacing_formulas = wb_links["Pacing"]

        date_to_pacing_key = build_date_to_pacing_key(
            teacher_values
        )
        pacing_links, direct_link_count = build_pacing_link_lookup(
            pacing_values,
            pacing_formulas,
        )

        print(
            f"Teacher dates mapped to Pacing days: "
            f"{len(date_to_pacing_key)}"
        )
        print(
            f"Pacing direct hyperlinks available: "
            f"{direct_link_count}"
        )

        if len(date_to_pacing_key) < 20:
            raise RuntimeError(
                "Too few Teacher Calendar dates mapped to Pacing."
            )

        if direct_link_count < 100:
            raise RuntimeError(
                "Too few direct Pacing hyperlinks were found."
            )

        current_date_values = [
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

        current_start = next(
            (
                date_key(value)
                for value in current_date_values
                if date_key(value)
            ),
            None,
        )

        archive_date_rows = []

        for row in range(11, min(wsv.max_row, 500) + 1):
            values = [
                wsv.cell(row=row, column=col).value
                for col in range(1, 6)
            ]

            if sum(
                1 for value in values if looks_like_date(value)
            ) >= 4:
                archive_date_rows.append(row)

        previous = []

        for i, date_row in enumerate(archive_date_rows):
            next_date_row = (
                archive_date_rows[i + 1]
                if i + 1 < len(archive_date_rows)
                else min(date_row + 11, wsv.max_row + 1)
            )

            archive_date_values = [
                wsv.cell(row=date_row, column=col).value
                for col in range(1, 6)
            ]
            dates = [
                safe_text(value)
                for value in archive_date_values
            ]

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

            end_row = min(
                next_date_row - 1,
                date_row + 10,
            )

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

    text = text[:start] + read_calendar_block + text[end:]

    # Remove visual underlines. Links remain full-cell clickable targets.
    text = text.replace(
        "text-decoration:underline;",
        "text-decoration:none;",
    )

    BUILDER.write_text(text, encoding="utf-8")
    print(
        "Installed date/Pacing hyperlink resolver.",
        flush=True,
    )

    # ------------------------------------------------------------
    # Build and verify BEFORE committing.
    # ------------------------------------------------------------
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")
    link_count = page.count('<a class="cal-link')

    expected_current_links = [
        "1_5_2_welcome.html",
        "1_5_3_welcome.html",
        "1_sum_welcome.html",
        "2_1_1_welcome.html",
        "2_1_2_welcome.html",
        "u1_5_demo",
        "u2_1_demo",
        "u1_5_notes",
        "u2_1_notes",
        "practice_set_1_5",
        "practice_set_2_1",
    ]

    expected_old_links = [
        "0_1_1_welcome.html",
        "1_1_1_welcome.html",
        "1_4_1_welcome.html",
    ]

    missing = [
        marker
        for marker in expected_current_links + expected_old_links
        if marker not in page
    ]

    print(
        f"Clickable calendar cells generated: {link_count}",
        flush=True,
    )

    if link_count < 100:
        raise SystemExit(
            f"Expected at least 100 clickable calendar cells; "
            f"got {link_count}. Nothing committed."
        )

    if missing:
        raise SystemExit(
            "Known calendar links are still missing: "
            + ", ".join(missing)
            + ". Nothing committed."
        )

    if "text-decoration:underline" in page:
        raise SystemExit(
            "Underline CSS still remains. Nothing committed."
        )

    print("Verified current-week links.", flush=True)
    print("Verified previous-week links.", flush=True)
    print("Verified underlines removed.", flush=True)

    run(
        "git",
        "add",
        "agenda/build_agenda.py",
        "agenda/index.html",
    )

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("No changes to commit.", flush=True)
        return

    run(
        "git",
        "commit",
        "-m",
        "Restore clickable agenda links",
    )
    run("git", "push", "origin", "main")

    print("", flush=True)
    print("DONE", flush=True)
    print("- calendar links restored", flush=True)
    print("- underlines removed", flush=True)
    print("- final styling preserved", flush=True)
    print("- 5-minute automation unchanged", flush=True)


if __name__ == "__main__":
    main()
