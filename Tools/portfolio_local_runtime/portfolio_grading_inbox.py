#!/usr/bin/env python3
"""Apply the newest Portfolio grading handoff from its dedicated private inbox.

Only result packages (or legacy result JSON) belong in this inbox.  The local
runtime remains responsible for state updates, reports, and evidence archival.
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import apply_grading_result_package as grader


INBOX_RELATIVE = Path("Portfolio Grading") / "Incoming"
APPLIED_RELATIVE = Path("Portfolio Grading") / "Applied"
REQUIRED_PACKAGE_FILES = {grader.RESULT_FILENAME, grader.MANIFEST_FILENAME}


def is_grading_package(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            return REQUIRED_PACKAGE_FILES.issubset({
                info.filename.replace("\\", "/")
                for info in zf.infolist()
                if not info.is_dir()
            })
    except (OSError, zipfile.BadZipFile):
        return False


def pending_results(inbox: Path) -> list[Path]:
    candidates = [
        p for p in inbox.iterdir()
        if p.is_file() and (
            (p.suffix.lower() == ".zip" and is_grading_package(p))
            or (p.suffix.lower() == ".json" and p.name.lower().startswith("portfolio_grading_result"))
        )
    ]
    return sorted(candidates, key=lambda p: (p.stat().st_mtime, p.name), reverse=True)


def unique_applied_path(folder: Path, filename: str) -> Path:
    target = folder / filename
    index = 2
    while target.exists():
        source = Path(filename)
        target = folder / f"{source.stem}_{index}{source.suffix}"
        index += 1
    return target


def main() -> int:
    downloads = Path.home() / "Downloads"
    inbox = downloads / INBOX_RELATIVE
    applied_dir = downloads / APPLIED_RELATIVE
    inbox.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 2:
        print("Usage: Apply Portfolio Grading Result.command [optional-result-file-path]")
        return 2
    if len(sys.argv) == 2:
        path = Path(sys.argv[1]).expanduser()
        if not path.is_file():
            print(f"Grading file not found: {path}")
            return 2
        if path.suffix.lower() == ".zip" and not is_grading_package(path):
            print(f"The selected ZIP is not a Portfolio grading result package: {path}")
            return 2
    else:
        results = pending_results(inbox)
        if not results:
            print("No Portfolio grading results are waiting in:")
            print(f"  {inbox}")
            print("Save the graded ZIP there (any descriptive filename is accepted).")
            print("Old files in the regular Downloads folder are not automatically selected.")
            return 0
        path = results[0]
        if len(results) > 1:
            print(f"Found {len(results)} pending results; selecting newest: {path.name}")
            print("Run the installer again for the next result.")

    print("Portfolio grading handoff found:")
    print(f"  {path}")
    print()

    # Apply first. The existing grader verifies the exact state and archive
    # integrity before the handoff is moved out of the incoming directory.
    if path.suffix.lower() == ".zip":
        grader.apply_package(path)
    else:
        grader.apply_legacy_json(path, downloads)

    # Only automatically move packages belonging to this dedicated inbox.
    # The existing local archive under _portfolio_data is also preserved.
    if path.parent.resolve() == inbox.resolve():
        applied_dir.mkdir(parents=True, exist_ok=True)
        destination = unique_applied_path(applied_dir, path.name)
        shutil.move(str(path), str(destination))
        print()
        print("Processed inbox handoff moved to:")
        print(f"  {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
