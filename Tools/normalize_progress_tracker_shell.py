#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup

CHECK_GLYPHS = "□☐☑✓✔"


def clean_leading_check(text: str) -> str:
    return re.sub(
        rf"^[\s{re.escape(CHECK_GLYPHS)}]+",
        "",
        text or "",
    ).strip()


def normalize(path: Path) -> None:
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")

    # Normalize each authoritative I-can row to the locked shell:
    #   .check + .ican-text
    for row in soup.select(".ican-list .ican"):
        text = clean_leading_check(row.get_text(" ", strip=True))
        row.clear()

        check = soup.new_tag(
            "span",
            attrs={"class": "check", "aria-hidden": "true"},
        )
        txt = soup.new_tag("span", attrs={"class": "ican-text"})
        txt.string = text

        row.append(check)
        row.append(txt)

    # Status choices are repeated once PER Mastery Goal.
    # Only strip accidental checkbox glyphs; do not merge or reduce rows.
    for choice in soup.select(".goal-card .status-row .status-choice"):
        text = clean_leading_check(choice.get_text(" ", strip=True))
        choice.clear()
        choice.string = text

    path.write_text(str(soup), encoding="utf-8")


def audit(path: Path) -> list[str]:
    errors: list[str] = []
    soup = BeautifulSoup(
        path.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )

    # I-can shell audit.
    for i, row in enumerate(soup.select(".ican-list .ican"), 1):
        children = row.find_all(recursive=False)
        check = row.select_one(":scope > .check")
        text = row.select_one(":scope > .ican-text")

        if len(children) != 2 or not check or not text:
            errors.append(
                f"I-can row {i} must have exactly .check + .ican-text"
            )
            continue

        if check.get_text(strip=True):
            errors.append(f"I-can row {i} .check must be empty")

        if not re.match(
            r"^I\s+can\b",
            text.get_text(" ", strip=True),
            re.I,
        ):
            errors.append(
                f"I-can row {i} text must begin with 'I can'"
            )

    # Global status key: exactly four labels once at the top of the tracker.
    status_key = soup.select_one(".status-key")
    if not status_key:
        errors.append("Missing .status-key")
    else:
        key_choices = status_key.select(":scope > .status-choice")
        if len(key_choices) != 4:
            errors.append(
                "Expected 4 status choices in .status-key, "
                f"found {len(key_choices)}"
            )

    # Per-Mastery-Goal status audit.
    # The old normalizer incorrectly required FOUR choices in the ENTIRE file.
    # Current Progress PM requires FOUR choices inside EVERY goal card.
    goal_cards = soup.select(".goal-card")
    if not goal_cards:
        errors.append("No .goal-card elements found")

    for i, goal in enumerate(goal_cards, 1):
        goal_id = (
            goal.get("data-mastery-goal")
            or (goal.select_one(".goal-id").get_text(" ", strip=True)
                if goal.select_one(".goal-id")
                else f"goal {i}")
        )

        status_rows = goal.select(":scope .status-row")
        if len(status_rows) != 1:
            errors.append(
                f"{goal_id}: expected exactly 1 .status-row, "
                f"found {len(status_rows)}"
            )
            continue

        choices = status_rows[0].select(":scope > .status-choice")
        if len(choices) != 4:
            errors.append(
                f"{goal_id}: expected 4 status choices, "
                f"found {len(choices)}"
            )

        for c in choices:
            if re.search(r"[□☐☑✓✔]", c.get_text()):
                errors.append(
                    f"{goal_id}: status choice contains checkbox glyph "
                    "even though CSS supplies it"
                )

    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    args = ap.parse_args()

    root = Path(args.root)
    files = list(root.rglob("unit_*_progress.html"))

    if not files:
        raise SystemExit("No Progress Tracker HTML found.")

    all_errors: list[str] = []

    for path in files:
        normalize(path)
        all_errors += [
            f"{path}: {error}"
            for error in audit(path)
        ]

    if all_errors:
        print("\n".join("ERROR: " + error for error in all_errors))
        raise SystemExit(1)

    print("Progress Tracker shell normalizer: PASS")


if __name__ == "__main__":
    main()
