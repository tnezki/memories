#!/usr/bin/env python3
"""One-time, date-scoped Algebra Week 07 Planner link repair.

Changes only the Warm Up student slot for Oct 12-16, 2026 through the
Planner's own /api/publish endpoint; does not rewrite Planner files or Git.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DATES = [f"2026-10-{day:02d}" for day in range(12, 17)]
OLD_URL = "https://tnezki.github.io/algebra/warmups/unit_2_warmups/unit_2_warmups.html"
NEW_BASE = "https://tnezki.github.io/algebra/warmups/week7/warm_up_week_07.html"
PLANNER_BASE = os.environ.get("ALGEBRA_PLANNER_API", "http://127.0.0.1:8767").rstrip("/")
TIMEOUT = 7


def git_root() -> Path:
    candidates = [os.environ.get("GITHUB_ROOT", ""), str(Path.home() / "GitHub"), str(Path.home() / "Documents" / "GitHub")]
    for item in candidates:
        if not item:
            continue
        p = Path(item).expanduser().resolve()
        if (p / "_algebra_teacher_tools").is_dir() and (p / "algebra").is_dir() and (p / "memories").is_dir():
            return p
    raise RuntimeError("GitHub workspace not found; no changes made.")


def api(path: str, body: dict | None = None) -> dict:
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(PLANNER_BASE + path, data=payload,
                  headers={"Accept":"application/json", "Content-Type":"application/json", "Cache-Control":"no-store"},
                  method="POST" if body is not None else "GET")
    with urlopen(req, timeout=TIMEOUT) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Planner response was not an object.")
    return data


def bootstrap(root: Path) -> dict:
    try:
        return api("/api/bootstrap")
    except (OSError, HTTPError, URLError, ValueError):
        launch = root / "_algebra_teacher_tools" / "runtime" / "Start Teacher Tools Runtime.command"
        if not launch.is_file() or not PLANNER_BASE.startswith("http://127.0.0.1:"):
            raise RuntimeError("Algebra Planner is not available on port 8767. Open Algebra Planner from Local Tools and try again.")
        print("Algebra Planner not running; starting existing Teacher Tools runtime...")
        log = root / "_curriculum_transfers" / "_logs" / "planner_week07_runtime.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("ab") as stream:
            subprocess.Popen(["/bin/bash", str(launch)], stdout=stream, stderr=stream, start_new_session=True)
        for attempt in range(20):
            time.sleep(.5)
            try:
                return api("/api/bootstrap")
            except (OSError, HTTPError, URLError, ValueError):
                pass
        raise RuntimeError("Algebra Planner did not start. Open it from Local Tools and try again.")


def repair_state(state: dict) -> tuple[dict, int]:
    if not isinstance(state, dict) or not str(state.get("schema", "")).startswith("algebra-planner-state/"):
        raise RuntimeError("Unexpected Algebra Planner state schema. Nothing changed.")
    days = state.get("days")
    if not isinstance(days, list):
        raise RuntimeError("Planner state has no valid days array. Nothing changed.")
    matches = {date: [d for d in days if isinstance(d, dict) and d.get("date") == date] for date in DATES}
    if any(len(matches[d]) != 1 for d in DATES):
        raise RuntimeError("Expected exactly one Planner day for each date Oct 12-16. Nothing changed.")
    fixed = copy.deepcopy(state)
    by_date = {d["date"]: d for d in fixed["days"] if isinstance(d, dict) and d.get("date") in DATES}
    changes = 0
    for index, date in enumerate(DATES, 1):
        day = by_date[date]
        if day.get("control", "Regular Day") != "Regular Day" or not str(day.get("section", "")).startswith(("2.1", "2.2")):
            raise RuntimeError(f"{date} is no longer a regular Unit 2 lesson day. No changes made.")
        slots = day.get("student_slots")
        if not isinstance(slots, list) or len(slots) != 5:
            raise RuntimeError(f"{date} has an unexpected student slot structure. No changes made.")
        custom_slots = day.get("custom_slots")
        if not isinstance(custom_slots, list):
            custom_slots = []
            day["custom_slots"] = custom_slots
        while len(custom_slots) < len(slots):
            custom_slots.append({"label":"", "url":""})
        warmup_indices = [i for i, name in enumerate(slots)
                          if name == "Warm Up" or (name == "Custom Item" and isinstance(custom_slots[i], dict)
                          and str(custom_slots[i].get("label", "")).strip() == "Warm Up")]
        if len(warmup_indices) != 1:
            raise RuntimeError(f"{date} must contain exactly one Warm Up slot (found {len(warmup_indices)}). No changes made.")
        slot = warmup_indices[0]
        existing = custom_slots[slot] if isinstance(custom_slots[slot], dict) else {}
        target = NEW_BASE + f"#day{index}"
        previous = str(existing.get("url", "")).strip()
        if slots[slot] == "Custom Item" and previous not in ("", OLD_URL, target, NEW_BASE):
            raise RuntimeError(f"{date} has an unexpected custom Warm Up link; preserving teacher edit. Nothing changed.")
        if slots[slot] != "Custom Item" or existing.get("url") != target or existing.get("label") != "Warm Up":
            slots[slot] = "Custom Item"
            custom_slots[slot] = {"label": "Warm Up", "url": target}
            changes += 1
        print(f"  {date} -> Week 07 Day {index}")
    return fixed, changes


def extract_current_week(html: str) -> str:
    match = re.search(r"(?<!\d)10/12(?!\d)", html)
    if not match:
        raise RuntimeError("Could not find Oct 12 in agenda.")
    start = html.rfind("<tbody", 0, match.start())
    end = html.find("</tbody>", match.end())
    if start < 0 or end < 0:
        raise RuntimeError("Could not isolate Oct 12 agenda week.")
    return html[start:end+8]


def verify_outputs(root: Path) -> None:
    for rel in ("algebra/agenda/index.html", "teacher_shared/algebra/index.html"):
        page = root / rel
        if not page.is_file():
            raise RuntimeError(f"Planner did not write {rel}.")
        week = extract_current_week(page.read_text(encoding="utf-8"))
        for day in range(1, 6):
            target = NEW_BASE + f"#day{day}"
            if week.count(target) != 1:
                raise RuntimeError(f"{rel}: expected exactly one Week 07 Day {day} URL, found {week.count(target)}.")
        if OLD_URL in week:
            raise RuntimeError(f"{rel}: old Unit 2 warm-up URL still present.")
        print(f"VERIFIED: {rel} — five day-specific Week 07 links.")


def main() -> int:
    print("ALGEBRA WEEK 07 PLANNER REPAIR")
    print("October 12-16, 2026 | Warm Up links only")
    print("=" * 48)
    root = git_root()
    package = root / "algebra" / "warmups" / "week7" / "warm_up_week_07.html"
    if not package.is_file():
        raise RuntimeError("Week 07 warm-up file is not installed. Run its curriculum transfer first. Nothing changed.")
    for day in range(1,6):
        if f'id="day{day}"' not in package.read_text(encoding="utf-8"):
            raise RuntimeError(f"Week 07 warm-up page missing Day {day} anchor. Nothing changed.")
    base = bootstrap(root)
    if base.get("ok") is False or not isinstance(base.get("state"), dict):
        raise RuntimeError("Planner did not return a valid saved state. Nothing changed.")
    updated, changes = repair_state(base["state"])
    if not changes:
        print("Planner schedule already contains the Week 07 links.")
        try:
            verify_outputs(root)
        except RuntimeError as exc:
            print("Published output needs refresh:", exc)
            changes = 1
        else:
            print("SUCCESS: No changes needed.")
            return 0
    snapshot = root / "_curriculum_transfers" / "_backups" / f"planner_week07_{datetime.now():%Y%m%d_%H%M%S}"
    snapshot.mkdir(parents=True, exist_ok=False)
    (snapshot / "state_before.json").write_text(json.dumps(base["state"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for rel in ("algebra/agenda/index.html", "teacher_shared/algebra/index.html"):
        src = root / rel
        if src.is_file():
            dest = snapshot / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    print(f"Backup: {snapshot}")
    print("Updating Planner through its own publish API...")
    result = api("/api/publish", {"state": updated})
    if result.get("ok") is not True:
        raise RuntimeError("Planner publish rejected repair: " + str(result.get("error") or result.get("message") or "unknown error"))
    verify_outputs(root)
    print("\nSUCCESS SUCCESS SUCCESS")
    print("PLANNER WEEK 07 REPAIR COMPLETE")
    print("Now choose Commit + Push All Repos in Local Tools / Planner Sync to publish to GitHub.")
    print("SUCCESS SUCCESS SUCCESS")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("\nFAILURE FAILURE FAILURE")
        print("PLANNER WEEK 07 REPAIR STOPPED")
        print(str(exc))
        print("No Git actions were performed. Any local backups remain in _curriculum_transfers/_backups.")
        print("FAILURE FAILURE FAILURE")
        sys.exit(1)
