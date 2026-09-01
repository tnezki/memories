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

    old = '''import html
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
'''
    new = '''import html
import re
import tempfile
import time
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
'''
    text = replace_once(text, old, new, "HTML link-parser imports")

    old = '''SPREADSHEET_ID = "1Qga2eTz0Nfgu8wIw5L-ZGC2xRtb4fOUoUXN-TyxuASE"
SHEET_NAME = "Student Calendar"
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
'''
    new = '''SPREADSHEET_ID = "1Qga2eTz0Nfgu8wIw5L-ZGC2xRtb4fOUoUXN-TyxuASE"
SHEET_ID = "2143927343"
SHEET_NAME = "Student Calendar"
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"

LINK_HTML_URLS = [
    (
        "native htmlview",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/htmlview"
        f"?gid={SHEET_ID}&single=true",
    ),
    (
        "published html",
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSBynd64DDPSLoZRT3E4rdLBfGASMzjAU4pD6mCYX6fRl66XqRUIkaae5kZpzghJ1LmkLD86LpMIKVM/"
        f"pubhtml?gid={SHEET_ID}&single=true",
    ),
]
'''
    text = replace_once(text, old, new, "Google HTML link sources")

    marker = "\ndef cell_info(ws_values, ws_links, row, col):\n"
    parser_code = r'''

def normalize_google_link(href):
    if not href:
        return None

    href = href.strip()
    if href.startswith("/url?"):
        href = "https://www.google.com" + href

    parsed = urlparse(href)
    if parsed.netloc.endswith("google.com") and parsed.path == "/url":
        target = parse_qs(parsed.query).get("q", [None])[0]
        if target:
            return target

    if href.startswith(("http://", "https://")):
        return href

    return None


class SheetTableParser(HTMLParser):
    # Parse Google rendered sheet tables and retain links by cell coordinate.

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.table_depth = 0
        self.row = -1
        self.next_col = 0
        self.active_cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "table":
            if self.table is None:
                self.table = {
                    "class": attrs.get("class", ""),
                    "grid": {},
                    "max_row": -1,
                    "max_col": -1,
                }
                self.table_depth = 1
            else:
                self.table_depth += 1
            return

        if self.table is None or self.table_depth != 1:
            return

        if tag == "tr":
            self.row += 1
            self.next_col = 0
            self.table["max_row"] = max(self.table["max_row"], self.row)
            return

        if tag in ("td", "th") and self.row >= 0:
            grid = self.table["grid"]

            while (self.row, self.next_col) in grid:
                self.next_col += 1

            try:
                rowspan = max(1, int(attrs.get("rowspan", "1")))
            except ValueError:
                rowspan = 1

            try:
                colspan = max(1, int(attrs.get("colspan", "1")))
            except ValueError:
                colspan = 1

            cell = {"text": [], "href": None}

            for rr in range(self.row, self.row + rowspan):
                for cc in range(self.next_col, self.next_col + colspan):
                    grid[(rr, cc)] = cell
                    self.table["max_row"] = max(self.table["max_row"], rr)
                    self.table["max_col"] = max(self.table["max_col"], cc)

            self.active_cell = cell
            self.next_col += colspan
            return

        if tag == "a" and self.active_cell is not None:
            href = normalize_google_link(attrs.get("href"))
            if href and not self.active_cell["href"]:
                self.active_cell["href"] = href

    def handle_data(self, data):
        if self.active_cell is not None:
            self.active_cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.active_cell = None
            return

        if tag == "table" and self.table is not None:
            self.table_depth -= 1
            if self.table_depth == 0:
                self.tables.append(self.table)
                self.table = None
                self.row = -1
                self.next_col = 0
                self.active_cell = None

    def best_sheet_table(self):
        candidates = []

        for table in self.tables:
            grid = table["grid"]
            rows = table["max_row"] + 1
            cols = table["max_col"] + 1

            if rows < 10 or cols < 5:
                continue

            first_rows_text = []
            for rr in range(min(rows, 5)):
                for cc in range(min(cols, 8)):
                    cell = grid.get((rr, cc))
                    if cell:
                        first_rows_text.append(
                            " ".join("".join(cell["text"]).split())
                        )

            joined = " ".join(first_rows_text)
            weekday_score = sum(
                1
                for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
                if day in joined
            )

            unique_cells = {id(v): v for v in grid.values()}.values()
            link_count = sum(1 for cell in unique_cells if cell.get("href"))
            waffle_bonus = (
                1000 if "waffle" in table.get("class", "").split() else 0
            )
            score = (
                waffle_bonus
                + weekday_score * 500
                + link_count * 5
                + min(rows * cols, 500)
            )

            candidates.append((score, table, link_count))

        if not candidates:
            return None, 0

        candidates.sort(key=lambda item: item[0], reverse=True)
        _, table, link_count = candidates[0]
        return table, link_count


class LinkGrid:
    def __init__(self, table):
        self.grid = table["grid"]

    def link_at(self, row, col):
        cell = self.grid.get((row - 1, col - 1))
        return cell.get("href") if cell else None


def download_link_grid():
    # Fetch the rendered Student Calendar and capture its real hyperlinks.

    errors = []

    for source_name, base_url in LINK_HTML_URLS:
        for attempt in range(1, 4):
            separator = "&" if "?" in base_url else "?"
            url = f"{base_url}{separator}_agenda_cache={int(time.time())}"

            try:
                response = requests.get(
                    url,
                    timeout=45,
                    headers={
                        "User-Agent": "Mozilla/5.0 AgendaBuilder/2.0",
                        "Cache-Control": "no-cache",
                    },
                )
                response.raise_for_status()

                parser = SheetTableParser()
                parser.feed(response.text)
                table, link_count = parser.best_sheet_table()

                if table is not None and link_count >= 5:
                    print(
                        f"Link source OK: {source_name} "
                        f"({link_count} linked cells found)"
                    )
                    return LinkGrid(table)

                errors.append(
                    f"{source_name} attempt {attempt}: "
                    f"sheet table/link count not usable ({link_count} links)"
                )

            except Exception as exc:
                errors.append(f"{source_name} attempt {attempt}: {exc}")

            if attempt < 3:
                time.sleep(attempt * 2)

    raise RuntimeError(
        "Could not read calendar hyperlinks from Google. "
        "The existing GitHub agenda was left untouched.\n"
        + "\n".join(errors[-6:])
    )


def cell_info(ws_values, ws_links, row, col, link_grid=None):
'''
    if marker not in text:
        raise SystemExit("Could not find cell_info(). Nothing committed.")
    text = text.replace(marker, parser_code, 1)

    old = '''    formula = lc.value
    if not link and isinstance(formula, str) and formula.startswith("="):
        m = re.search(r'HYPERLINK\\(\\s*"([^"]+)"', formula, re.I)
        if m:
            link = m.group(1)

    return safe_text(value), link
'''
    new = '''    formula = lc.value
    if not link and isinstance(formula, str) and formula.startswith("="):
        m = re.search(r'HYPERLINK\\(\\s*"([^"]+)"', formula, re.I)
        if m:
            link = m.group(1)

    # Google XLSX export drops many formula-driven hyperlinks.
    # Recover those from the rendered Student Calendar.
    if not link and link_grid is not None:
        link = link_grid.link_at(row, col)

    return safe_text(value), link
'''
    text = replace_once(text, old, new, "cell hyperlink fallback")

    old = '''def gather_items(ws_values, ws_links, start_row, end_row, col):
    items = []
    for row in range(start_row, end_row + 1):
        label, url = cell_info(ws_values, ws_links, row, col)
'''
    new = '''def gather_items(ws_values, ws_links, start_row, end_row, col, link_grid=None):
    items = []
    for row in range(start_row, end_row + 1):
        label, url = cell_info(
            ws_values, ws_links, row, col, link_grid=link_grid
        )
'''
    text = replace_once(text, old, new, "gather_items link grid")

    old = '''def read_calendar():
    xlsx = download_workbook()
    try:
'''
    new = '''def read_calendar():
    # Fetch links before building. If Google temporarily refuses the rendered
    # sheet, the build fails safely and the existing GitHub page stays live.
    link_grid = download_link_grid()
    xlsx = download_workbook()
    try:
'''
    text = replace_once(text, old, new, "read_calendar link fetch")

    old = '''        current_dates = [cell_info(wsv, wsl, 2, c)[0] for c in range(1, 6)]
        current_items = [gather_items(wsv, wsl, 3, 9, c) for c in range(1, 6)]
'''
    new = '''        current_dates = [
            cell_info(wsv, wsl, 2, c, link_grid=link_grid)[0]
            for c in range(1, 6)
        ]
        current_items = [
            gather_items(wsv, wsl, 3, 9, c, link_grid=link_grid)
            for c in range(1, 6)
        ]
'''
    text = replace_once(text, old, new, "current-week link grid")

    old = '''            dates = [cell_info(wsv, wsl, date_row, c)[0] for c in range(1, 6)]
'''
    new = '''            dates = [
                cell_info(wsv, wsl, date_row, c, link_grid=link_grid)[0]
                for c in range(1, 6)
            ]
'''
    text = replace_once(text, old, new, "archive dates link grid")

    old = '''            items = [gather_items(wsv, wsl, date_row + 1, end_row, c) for c in range(1, 6)]
'''
    new = '''            items = [
                gather_items(
                    wsv,
                    wsl,
                    date_row + 1,
                    end_row,
                    c,
                    link_grid=link_grid,
                )
                for c in range(1, 6)
            ]
'''
    text = replace_once(text, old, new, "archive items link grid")

    old = '''a.cal-link:hover,
a.cal-link:focus-visible {{
  background:#fff4c7;
  text-decoration:underline;
}}
'''
    new = '''a.cal-link:hover,
a.cal-link:focus-visible {{
  background:#fff4c7;
  text-decoration:none;
}}
'''
    text = replace_once(text, old, new, "hover underline")

    # Remove the explicit lesson-title underlines from current-week styles.
    text = text.replace("  text-decoration:underline;\n", "  text-decoration:none;\n")

    BUILDER.write_text(text, encoding="utf-8")
    print("Patched build_agenda.py to recover Google calendar links.")

    # Test locally before committing.
    run(sys.executable, str(BUILDER))

    page = INDEX.read_text(encoding="utf-8")
    calendar_link_count = page.count('<a class="cal-link')

    if calendar_link_count < 10:
        raise SystemExit(
            f"Only {calendar_link_count} calendar links were generated. "
            "Nothing committed."
        )

    if "text-decoration:underline" in page:
        raise SystemExit("Underline CSS is still present. Nothing committed.")

    known_markers = [
        "0_1_1_welcome.html",
        "unit_1_warmups",
    ]
    if not any(marker in page for marker in known_markers):
        raise SystemExit(
            "Calendar links were generated, but known Algebra links were not found. "
            "Nothing committed."
        )

    print(f"Verified {calendar_link_count} clickable calendar cells.")
    print("Verified underlines removed.")

    run("git", "add", "agenda/build_agenda.py", "agenda/index.html")

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(REPO),
    ).returncode != 0

    if not changed:
        print("No changes to commit.")
        return

    run("git", "commit", "-m", "Restore clickable agenda links")
    run("git", "push", "origin", "main")

    print()
    print("DONE")
    print("- calendar links restored")
    print("- underlines removed")
    print("- current styling preserved")
    print("- 5-minute workflow unchanged")
    print("- students still load only the static GitHub agenda")


if __name__ == "__main__":
    main()
