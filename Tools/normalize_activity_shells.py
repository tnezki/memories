#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, Tag


HUB_PAGE_IDS = [
    "activity-options",
    "teacher-student-moves",
    "dir-whiteboard-indy",
    "dir-whiteboard-partners",
    "dir-rally-coach",
    "dir-speed-dating-math",
    "dir-showdown",
    "dir-think-trade-agree",
    "dir-round-table",
    "dir-mathematical-hot-seat",
    "dir-rally-coach-ii",
    "dir-desmos-activity",
    "dir-stations",
    "dir-find-someone-who",
    "dir-tarsia-puzzle-activity",
]

GENERIC_ROUTINE_PHRASES = (
    "use one of the two linked question sets",
    "students solve and explain",
    "partners compare evidence and revise if needed",
)

# Each tuple is a group. At least one term from every group must appear on that page.
STRUCTURE_TOKENS = {
    "dir-whiteboard-indy": [
        ("individual", "independent"),
        ("notes", "resources"),
        ("large", "readable", "clearly"),
        ("mistake", "correct", "revise"),
    ],
    "dir-whiteboard-partners": [
        ("partner",),
        ("alternate", "switch"),
        ("both",),
        ("disagree", "mistake", "check"),
    ],
    "dir-rally-coach": [
        ("coach",),
        ("question", "hint"),
        ("switch", "alternate"),
        ("solver", "partner a", "partner b"),
    ],
    "dir-speed-dating-math": [
        ("rotate", "rotation"),
        ("partner",),
        ("own work", "each student", "each person"),
        ("strategy", "reasoning", "evidence"),
    ],
    "dir-showdown": [
        ("reveal",),
        ("private", "independent", "silently"),
        ("compare",),
        ("revise", "explain", "defend"),
    ],
    "dir-think-trade-agree": [
        ("think", "independent", "alone"),
        ("trade",),
        ("clarifying", "question"),
        ("agree", "disagree", "conclusion"),
    ],
    "dir-round-table": [
        ("pass",),
        ("each", "every"),
        ("group",),
        ("step", "contribution", "add"),
    ],
    "dir-mathematical-hot-seat": [
        ("explain", "description"),
        ("question",),
        ("teammate", "group"),
        ("rotate", "switch", "next student"),
    ],
    "dir-rally-coach-ii": [
        ("coach",),
        ("solver",),
        ("switch", "alternate"),
        ("check", "evidence", "verify"),
    ],
    "dir-desmos-activity": [
        ("desmos",),
        ("teacher", "code", "link"),
    ],
    "dir-stations": [
        ("station",),
        ("rotate", "rotation", "move"),
        ("record", "work", "strategy"),
    ],
    "dir-find-someone-who": [
        ("signature", "sign"),
        ("partner",),
        ("different", "new partner", "someone new"),
        ("explain", "check", "reasoning"),
    ],
    "dir-tarsia-puzzle-activity": [
        ("tarsia", "puzzle"),
        ("match",),
        ("justify", "explain"),
        ("check", "revise"),
    ],
}


def norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def label_text(row: Tag) -> str:
    label = row.find(class_="dir-label")
    return norm_text(label.get_text(" ", strip=True)) if label else ""


def find_row(page: Tag, wanted: str) -> Tag | None:
    wanted = norm_text(wanted)
    for row in page.find_all(class_="dir-row"):
        if label_text(row) == wanted:
            return row
    return None


def list_after_exact_label(container: Tag, wanted: str) -> Tag | None:
    wanted = norm_text(wanted)
    for tag in container.find_all(["b", "strong", "p", "span"]):
        if norm_text(tag.get_text(" ", strip=True)) == wanted:
            ul = tag.find_next("ul")
            if ul is not None and container in ul.parents:
                return ul
    return None


def direct_pages(wrap: Tag) -> list[Tag]:
    pages = []
    for child in wrap.find_all("section", recursive=False):
        if "page" in (child.get("class") or []):
            pages.append(child)
    return pages


def ensure_stylesheet(soup: BeautifulSoup, href: str, before: Tag | None = None) -> None:
    links = soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    for link in links:
        if link.get("href") == href:
            return
    tag = soup.new_tag("link", rel="stylesheet", href=href)
    if before is not None:
        before.insert_before(tag)
    elif soup.head:
        soup.head.append(tag)


def normalize_html(path: Path) -> None:
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(
        r"^\s*(?:```html\s*|html\s*)(?=(?:<!doctype\s+html\b|<html\b))",
        "",
        raw,
        count=1,
        flags=re.I,
    )
    name = path.name.lower()

    # Direction hubs are audit-only. Never rewrite their curricular language here.
    if "stations" not in name and "find_someone_who" not in name:
        path.write_text(raw, encoding="utf-8")
        return

    # Preserve the established shell normalizations for Stations / FSW.
    soup = BeautifulSoup(raw, "html.parser")
    if "stations" in name and soup.body:
        wrap = soup.body.find("div", class_="wrap", recursive=False)
        if wrap is None:
            wrap = soup.new_tag("div", attrs={"class": "wrap"})
            for child in list(soup.body.contents):
                if getattr(child, "name", None) is not None or str(child).strip():
                    wrap.append(child.extract())
            soup.body.append(wrap)

    links = soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    for link in list(links):
        if link.get("href") in {
            "../../css/activity_stations.css",
            "../../css/activity_find_someone_who.css",
        }:
            link.decompose()

    first_style = soup.find("link", rel=lambda v: v and "stylesheet" in v)
    ensure_stylesheet(soup, "../../css/base.css", before=first_style)

    if "stations" in name:
        ensure_stylesheet(soup, "../../css/activities/activity_stations.css")
        for fig in soup.find_all("figure"):
            if fig.find("img"):
                classes = [c for c in (fig.get("class") or []) if c != "graph-block"]
                if "figure" not in classes:
                    classes.append("figure")
                fig["class"] = classes

    if "find_someone_who" in name:
        ensure_stylesheet(soup, "../../css/activities/activity_find_someone_who.css")

    out = str(soup)
    if not re.match(r"(?is)^\s*<!doctype\s+html\b", out):
        out = "<!doctype html>" + out
    path.write_text(out, encoding="utf-8")


def shell_error(path: Path, message: str) -> str:
    return f"{path}: ACTIVITY_SHELL_DEFECT: {message}"


def directions_error(path: Path, message: str) -> str:
    return f"{path}: ACTIVITY_DIRECTIONS_DEFECT: {message}"


def audit_moves_page(path: Path, page: Tag) -> list[str]:
    errors: list[str] = []
    text = norm_text(page.get_text(" ", strip=True))

    if "i-can moves" not in text and "i can moves" not in text:
        errors.append(directions_error(path, "Page 2 missing a visible I-Can Moves region"))
    if "participation-structure moves" not in text and "participation structure moves" not in text:
        errors.append(
            directions_error(path, "Page 2 missing a visible Participation-Structure Moves region")
        )

    ican_strongs: list[Tag] = []
    for tag in page.find_all(["strong", "b"]):
        t = norm_text(tag.get_text(" ", strip=True))
        if re.search(r"\bi\s*can\b", t) and "moves" not in t:
            ican_strongs.append(tag)

    if not ican_strongs:
        errors.append(directions_error(path, "Page 2 has no distinct I-can move blocks"))

    seen_ican: set[str] = set()
    checked_blocks = 0
    for strong in ican_strongs:
        itext = norm_text(strong.get_text(" ", strip=True))
        if itext in seen_ican:
            continue
        seen_ican.add(itext)
        container = strong.find_parent("div")
        if container is None:
            continue
        teacher = list_after_exact_label(container, "Teacher Moves")
        student = list_after_exact_label(container, "Student Moves")
        if teacher is None or len(teacher.find_all("li", recursive=False)) < 2:
            errors.append(
                directions_error(path, f"I-can block lacks at least 2 Teacher Moves: {strong.get_text(' ', strip=True)[:90]}")
            )
        if student is None or len(student.find_all("li", recursive=False)) < 2:
            errors.append(
                directions_error(path, f"I-can block lacks at least 2 Student Moves: {strong.get_text(' ', strip=True)[:90]}")
            )
        checked_blocks += 1

    # Enough separate move groups to prevent one generic Teacher/Student list from standing in
    # for the entire section. Four participation groups is the minimum executable floor; richer
    # grouping remains encouraged by the PM.
    teacher_labels = 0
    student_labels = 0
    for tag in page.find_all(["b", "strong"]):
        t = norm_text(tag.get_text(" ", strip=True))
        if t == "teacher moves":
            teacher_labels += 1
        elif t == "student moves":
            student_labels += 1

    minimum_groups = max(1, checked_blocks) + 4
    if teacher_labels < minimum_groups or student_labels < minimum_groups:
        errors.append(
            directions_error(
                path,
                "Page 2 is too generic: expected separate Teacher/Student move blocks for "
                f"each I-can plus at least 4 participation groups; found {teacher_labels}/{student_labels}",
            )
        )

    participation_markers = (
        "whiteboard",
        "rally coach",
        "showdown",
        "hot seat",
        "stations",
        "find someone who",
    )
    missing = [m for m in participation_markers if m not in text]
    if missing:
        errors.append(
            directions_error(path, "Page 2 participation guide missing major structures: " + ", ".join(missing))
        )

    return errors


def audit_direction_page(path: Path, page: Tag) -> tuple[list[str], str, str]:
    errors: list[str] = []
    pid = page.get("id") or "<missing-id>"
    page_text = norm_text(page.get_text(" ", strip=True))

    for wanted in ("Structure", "Setup", "Directions"):
        if find_row(page, wanted) is None:
            errors.append(directions_error(path, f"{pid}: missing visible {wanted} row"))

    goal = page.find(class_="dir-goal")
    if goal is None or not norm_text(goal.get_text(" ", strip=True)):
        errors.append(directions_error(path, f"{pid}: missing visible Goal"))

    directions = find_row(page, "Directions")
    direction_signature = ""
    if directions is not None:
        ol = directions.find("ol")
        if ol is None:
            errors.append(directions_error(path, f"{pid}: Directions must be an ordered list"))
        else:
            items = [norm_text(li.get_text(" ", strip=True)) for li in ol.find_all("li", recursive=False)]
            if len(items) < 3:
                errors.append(directions_error(path, f"{pid}: Directions need at least 3 actionable steps"))
            direction_signature = " | ".join(items)
            joined = " ".join(items)
            if all(phrase in joined for phrase in GENERIC_ROUTINE_PHRASES):
                errors.append(directions_error(path, f"{pid}: prohibited generic 3-step routine"))

    good = page.find(class_="looks-good")
    bad = page.find(class_="looks-bad")
    if good is None or bad is None:
        errors.append(directions_error(path, f"{pid}: missing Looks Like Success / Doesn't Look Like regions"))
        looks_signature = ""
    else:
        good_items = [norm_text(li.get_text(" ", strip=True)) for li in good.find_all("li")]
        bad_items = [norm_text(li.get_text(" ", strip=True)) for li in bad.find_all("li")]
        if len(good_items) < 3:
            errors.append(directions_error(path, f"{pid}: Looks Like Success needs at least 3 specific bullets"))
        if len(bad_items) < 3:
            errors.append(directions_error(path, f"{pid}: Doesn't Look Like needs at least 3 specific bullets"))
        looks_signature = "GOOD:" + " | ".join(good_items) + " BAD:" + " | ".join(bad_items)

    # Activity-specific mechanics. This is intentionally behavior-focused, not Physics-content-focused.
    for alternatives in STRUCTURE_TOKENS.get(pid, []):
        if not any(term in page_text for term in alternatives):
            errors.append(
                directions_error(
                    path,
                    f"{pid}: missing defining participation mechanic ({' / '.join(alternatives)})",
                )
            )

    return errors, direction_signature, looks_signature


def audit_hub(path: Path, soup: BeautifulSoup) -> list[str]:
    errors: list[str] = []

    hrefs = [
        x.get("href", "")
        for x in soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    ]
    expected_hrefs = ["../../css/base.css", "../../css/activities.css"]
    if hrefs != expected_hrefs:
        errors.append(
            shell_error(path, f"hub stylesheets must be exactly {expected_hrefs}, found {hrefs}")
        )

    if soup.body is None:
        return errors + [shell_error(path, "missing body")]

    wrap = soup.body.find("div", class_="wrap", recursive=False)
    if wrap is None:
        return errors + [shell_error(path, "body missing direct .wrap")]

    pages = direct_pages(wrap)
    if len(pages) != 15:
        errors.append(shell_error(path, f"hub requires exactly 15 direct .page sections, found {len(pages)}"))

    ids = [p.get("id") for p in pages]
    if ids != HUB_PAGE_IDS:
        errors.append(shell_error(path, f"hub page IDs/order mismatch: {ids}"))

    page_by_id = {p.get("id"): p for p in pages if p.get("id")}
    moves = page_by_id.get("teacher-student-moves")
    if moves is None:
        errors.append(shell_error(path, "missing teacher-student-moves page"))
    else:
        errors.extend(audit_moves_page(path, moves))

    direction_signatures: dict[str, str] = {}
    looks_signatures: dict[str, str] = {}
    for pid in HUB_PAGE_IDS[2:]:
        page = page_by_id.get(pid)
        if page is None:
            continue
        for required_hook in ("dir-header", "dir-body", "dir-text"):
            if page.find(class_=required_hook) is None:
                errors.append(shell_error(path, f"{pid}: missing .{required_hook}"))
        page_errors, dsig, lsig = audit_direction_page(path, page)
        errors.extend(page_errors)
        if dsig:
            if dsig in direction_signatures:
                errors.append(
                    directions_error(
                        path,
                        f"{pid}: Directions are identical to {direction_signatures[dsig]}",
                    )
                )
            else:
                direction_signatures[dsig] = pid
        if lsig:
            if lsig in looks_signatures:
                errors.append(
                    directions_error(
                        path,
                        f"{pid}: Looks Like / Doesn't Look Like blocks are identical to {looks_signatures[lsig]}",
                    )
                )
            else:
                looks_signatures[lsig] = pid

    return errors


def audit_station_or_fsw(path: Path, soup: BeautifulSoup) -> list[str]:
    errors: list[str] = []
    name = path.name.lower()
    hrefs = [
        x.get("href", "")
        for x in soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    ]
    if "../../css/base.css" not in hrefs:
        errors.append(shell_error(path, "missing ../../css/base.css"))

    if "stations" in name:
        if "../../css/activities/activity_stations.css" not in hrefs:
            errors.append(shell_error(path, "wrong Stations stylesheet path"))
        if "../../css/activity_stations.css" in hrefs:
            errors.append(shell_error(path, "obsolete Stations stylesheet path remains"))
        wrap = soup.body.find("div", class_="wrap", recursive=False) if soup.body else None
        if wrap is None:
            errors.append(shell_error(path, "Stations body missing direct .wrap"))
        else:
            pages = wrap.find_all("section", class_="page", recursive=False)
            qpages = [x for x in pages if "station-question-page" in (x.get("class") or [])]
            first_answer = next(
                (i for i, x in enumerate(pages) if "station-answer-page" in (x.get("class") or [])),
                len(pages),
            )
            prompt_region = pages[:first_answer]
            if len(prompt_region) != 2 * len(qpages):
                errors.append(shell_error(path, "prompt region must be station/blank pairs"))
            for i in range(0, len(prompt_region), 2):
                q = prompt_region[i]
                if "station-question-page" not in (q.get("class") or []):
                    errors.append(shell_error(path, f"prompt pair {i // 2 + 1} does not start with station question page"))
                    continue
                grid = q.find(class_="station-grid")
                probs = grid.find_all(class_="station-problem", recursive=False) if grid else []
                if len(probs) != 4:
                    errors.append(shell_error(path, "station prompt page must contain exactly 4 problems"))
                if q.select('.workspace, .work-space, .answer-space, textarea, input[type="text"]'):
                    errors.append(shell_error(path, "station prompt cards must not contain student workspace"))
                if i + 1 >= len(prompt_region) or "station-blank-page" not in (prompt_region[i + 1].get("class") or []):
                    errors.append(shell_error(path, "each station prompt page must be followed by one blank duplex page"))
                elif prompt_region[i + 1].get_text(" ", strip=True):
                    errors.append(shell_error(path, "station blank duplex page must contain no visible text"))
            sol_region = pages[first_answer:]
            if len(sol_region) != 2 * len(qpages):
                errors.append(shell_error(path, "solution region must contain exactly two pages per station"))
        for fig in soup.find_all("figure"):
            if fig.find("img") and "figure" not in (fig.get("class") or []):
                errors.append(shell_error(path, "Stations image figure missing .figure"))

    if "find_someone_who" in name:
        if "../../css/activities/activity_find_someone_who.css" not in hrefs:
            errors.append(shell_error(path, "wrong Find Someone Who stylesheet path"))
        if "../../css/activity_find_someone_who.css" in hrefs:
            errors.append(shell_error(path, "obsolete Find Someone Who stylesheet path remains"))

    return errors


def is_hub(path: Path) -> bool:
    return bool(re.fullmatch(r"u?\d+_\d+_act1\.html", path.name.lower()))


def audit(root: Path) -> list[str]:
    errors: list[str] = []
    hub_count = 0

    for path in root.rglob("*.html"):
        raw = path.read_text(encoding="utf-8", errors="replace")
        if not re.match(r"(?is)^\s*(?:<!doctype\s+html\b|<html\b)", raw):
            errors.append(shell_error(path, "visible token before HTML document"))
        soup = BeautifulSoup(raw, "html.parser")
        name = path.name.lower()

        if is_hub(path):
            hub_count += 1
            errors.extend(audit_hub(path, soup))
        elif "stations" in name or "find_someone_who" in name:
            errors.extend(audit_station_or_fsw(path, soup))

    if hub_count == 0:
        errors.append(f"{root}: ACTIVITY_SHELL_DEFECT: no Activity hub u*_act1.html found")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Staged Activities directory or a parent containing Activities HTML")
    args = ap.parse_args()
    root = Path(args.root)

    if not root.exists():
        raise SystemExit(f"Activity root does not exist: {root}")

    for path in root.rglob("*.html"):
        normalize_html(path)

    errors = audit(root)
    if errors:
        print("\n".join("ERROR: " + error for error in errors))
        raise SystemExit(1)

    print("Activity shell + directions validator: PASS")


if __name__ == "__main__":
    main()
