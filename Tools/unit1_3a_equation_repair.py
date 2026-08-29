#!/usr/bin/env python3
"""One-off repair for the seven Unit 1 Stage 3A equation-render contract defects.

Run from the Physics repository root, or pass the repository root as the first argument.
This script is intentionally narrow: it edits only student_html for seven exact item IDs.
It fails closed if the expected files/items are missing or if a target already contains
MathJax, so it cannot silently broaden the repair scope.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TARGETS = {
    "U1-S3-CYU-03": r"\(F_{\text{net}} = F_1 + F_2\)",
    "U1-S3-CYU-04": r"\(F_{\text{net}} = F_{\text{right}} - F_{\text{left}}\)",
    "U1-S3-WU1-Q4": r"\(F_{\text{net}} = F_{\text{right}} - F_{\text{left}}\)",
    "U1-S3-WU2-Q1": r"\(F_{\text{net}} = F_1 + F_2\)",
    "U1-S3-WU2-Q4": r"\(F_{\text{net}} = F_{\text{right}} - F_{\text{left}}\)",
    "U1-S3-WU3-Q3": r"\(F_{\text{net}} = F_1 + F_2\)",
    "U1-S3-WU3-Q4": r"\(F_{\text{net}} = F_{\text{left}} - F_{\text{right}}\)",
}

FILES = (
    Path("banks/unit1/cyu/section_1.3.json"),
    Path("banks/unit1/warmups/section_1.3.json"),
)


def has_mathjax(html: str) -> bool:
    return any(token in html for token in (r"\(", r"\[", "$$", "<math"))


def insert_equation(html: str, equation: str) -> str:
    marker = "</p>"
    pos = html.find(marker)
    if pos < 0:
        raise ValueError("student_html has no opening paragraph to attach equation after")
    end = pos + len(marker)
    return html[:end] + f"<p>{equation}</p>" + html[end:]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser().resolve()
    remaining = set(TARGETS)
    changed_files: list[Path] = []
    changed_ids: list[str] = []

    for rel in FILES:
        path = root / rel
        if not path.is_file():
            print(f"ERROR: required file not found: {path}", file=sys.stderr)
            return 1

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR: cannot parse {path}: {exc}", file=sys.stderr)
            return 1

        records = data.get("records")
        if not isinstance(records, list):
            print(f"ERROR: {path} has no records list", file=sys.stderr)
            return 1

        file_changed = False
        for record in records:
            item_id = record.get("item_id")
            if item_id not in TARGETS:
                continue

            html = record.get("student_html")
            if not isinstance(html, str) or not html.strip():
                print(f"ERROR: {item_id} has missing/empty student_html", file=sys.stderr)
                return 1
            if record.get("representation_mode") != "equation_relationship":
                print(
                    f"ERROR: {item_id} no longer has representation_mode=equation_relationship; "
                    "refusing to broaden repair",
                    file=sys.stderr,
                )
                return 1
            if has_mathjax(html):
                print(
                    f"ERROR: {item_id} already contains a rendered equation; "
                    "refusing to make a second change",
                    file=sys.stderr,
                )
                return 1

            record["student_html"] = insert_equation(html, TARGETS[item_id])
            remaining.remove(item_id)
            changed_ids.append(item_id)
            file_changed = True

        if file_changed:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            changed_files.append(rel)

    if remaining:
        print(
            "ERROR: target item(s) not found: " + ", ".join(sorted(remaining)),
            file=sys.stderr,
        )
        return 1

    print("Unit 1 Stage 3A equation-render repair: DONE")
    print(f"Changed {len(changed_ids)} exact records:")
    for item_id in changed_ids:
        print(f"  {item_id}")
    print("Changed files:")
    for rel in changed_files:
        print(f"  {rel}")
    print("No other records or fields were intentionally changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
