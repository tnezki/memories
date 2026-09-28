#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import portfolio_companion as core

_ORIGINAL_PREPARE = core.prepare_email
_PATCHED = False


def approved_message(course: str) -> str:
    return (
        f"Attached is your current {course} progress report. It shows what is going well and what to work on next.\n\n"
        "An I means In Progress. It is not permanent. It reflects the evidence we have right now. "
        "As you practice and provide new or stronger evidence, the current Mastery Goal grade updates; "
        "earlier checks are not averaged in as permanent penalties.\n"
    )


def prepare_with_approved_message(course: str, unit: int, *args, **kwargs):
    result = _ORIGINAL_PREPARE(course, unit, *args, **kwargs)
    folder = Path(str(result.get("email_folder") or ""))
    if folder.is_dir():
        (folder / "email_message_template.txt").write_text(
            f"Subject: {course} Unit {unit} Portfolio Progress Report\n\n" + approved_message(course),
            encoding="utf-8",
        )
    return result


def install_patch() -> None:
    global _PATCHED
    if _PATCHED:
        return
    core.prepare_email = prepare_with_approved_message
    _PATCHED = True
