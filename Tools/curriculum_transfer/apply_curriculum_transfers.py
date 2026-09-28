#!/usr/bin/env python3
"""Apply Curriculum Transfer packages safely to approved local roots.

This tool never runs Git commands. It supports the current
curriculum_transfer/3 schema and can still validate legacy github_transfer/2
packages when they are deliberately placed in the Curriculum Transfer inbox.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import time
import traceback
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

MANIFEST_NAME = "TRANSFER_MANIFEST.json"
CURRENT_SCHEMA_VERSION = 3
CURRENT_PACKAGE_TYPE = "curriculum_transfer"
LEGACY_SCHEMA_VERSION = 2
LEGACY_PACKAGE_TYPE = "github_transfer"


class TransferError(RuntimeError):
    pass


@dataclass
class PlannedAction:
    action: str
    source: Optional[str]
    destination: Path
    destination_rel: str
    expected_sha256: Optional[str]
    original_mode: Optional[int]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel(value: str, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value.strip():
        raise TransferError(f"{label} must be a non-empty relative path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        raise TransferError(f"Unsafe {label}: {value}")
    return p


def ensure_within(path: Path, root: Path, label: str) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise TransferError(f"{label} escapes allowed root: {path}") from exc


def normalize_hash(value: Any, required: bool, label: str) -> Optional[str]:
    if value is None or value == "":
        if required:
            raise TransferError(f"{label} requires expected_existing_sha256")
        return None
    if not isinstance(value, str):
        raise TransferError(f"{label} expected_existing_sha256 must be a string")
    value = value.lower().strip()
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise TransferError(f"{label} expected_existing_sha256 is not a SHA-256 hex digest")
    return value


def load_roots(config_path: Path, github_root: Path) -> Dict[str, Path]:
    if not config_path.is_file():
        raise TransferError(f"Approved roots file not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("roots"), dict):
        raise TransferError("approved_roots.json has an unsupported schema")
    roots: Dict[str, Path] = {}
    for alias, record in data["roots"].items():
        if not isinstance(alias, str) or not alias.strip() or not isinstance(record, dict):
            raise TransferError("Invalid approved root entry")
        rel = safe_rel(record.get("path", ""), f"approved root {alias}")
        dest = github_root.joinpath(*rel.parts)
        ensure_within(dest, github_root, f"approved root {alias}")
        roots[alias] = dest
    return roots


def read_manifest(zf: zipfile.ZipFile) -> Optional[Dict[str, Any]]:
    names = zf.namelist()
    if MANIFEST_NAME not in names:
        return None
    if names.count(MANIFEST_NAME) != 1:
        raise TransferError("TRANSFER_MANIFEST.json appears more than once")
    try:
        raw = zf.read(MANIFEST_NAME)
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise TransferError(f"Could not read {MANIFEST_NAME}: {exc}") from exc


def unique_destination(folder: Path, name: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    candidate = folder / name
    if not candidate.exists():
        return candidate
    stamp = time.strftime("%Y%m%d-%H%M%S")
    stem = Path(name).stem
    suffix = Path(name).suffix
    i = 1
    while True:
        candidate = folder / f"{stem}_{stamp}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def collect_zip_files(inboxes: Iterable[Path]) -> List[Path]:
    found: List[Path] = []
    seen: Set[str] = set()
    for inbox in inboxes:
        if not inbox.is_dir():
            continue
        for path in sorted(inbox.glob("*.zip"), key=lambda p: p.name.lower()):
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                found.append(path)
    return found


def plan_package(
    package: Path,
    zf: zipfile.ZipFile,
    manifest: Dict[str, Any],
    github_root: Path,
    approved_roots: Dict[str, Path],
) -> Tuple[str, List[PlannedAction]]:
    schema_version = manifest.get("schema_version")
    package_type = manifest.get("package_type")
    package_id = manifest.get("package_id")
    entries = manifest.get("files")

    if not isinstance(package_id, str) or not package_id.strip():
        raise TransferError("package_id must be a non-empty string")
    if not isinstance(entries, list) or not entries:
        raise TransferError("files must be a non-empty array")

    current = package_type == CURRENT_PACKAGE_TYPE and schema_version == CURRENT_SCHEMA_VERSION
    legacy = package_type == LEGACY_PACKAGE_TYPE and schema_version == LEGACY_SCHEMA_VERSION
    if not (current or legacy):
        raise TransferError(
            f"Unsupported transfer schema: package_type={package_type!r}, schema_version={schema_version!r}"
        )

    zip_names = set(zf.namelist())
    planned: List[PlannedAction] = []
    destinations: Set[str] = set()

    for index, entry in enumerate(entries, start=1):
        label = f"files[{index}]"
        if not isinstance(entry, dict):
            raise TransferError(f"{label} must be an object")
        action = str(entry.get("action", "")).lower().strip()
        if action not in {"create", "replace", "delete"}:
            raise TransferError(f"{label} has invalid action: {action!r}")

        source: Optional[str] = None
        if current:
            root_alias = entry.get("root")
            if root_alias not in approved_roots:
                raise TransferError(f"{label} uses unapproved root: {root_alias!r}")
            rel = safe_rel(entry.get("path", ""), f"{label}.path")
            destination = approved_roots[root_alias].joinpath(*rel.parts)
            ensure_within(destination, approved_roots[root_alias], label)
            destination_rel = destination.resolve().relative_to(github_root.resolve()).as_posix()
            if action != "delete":
                source = entry.get("source")
                expected_source = f"payload/{root_alias}/{rel.as_posix()}"
                if source != expected_source:
                    raise TransferError(
                        f"{label}.source must exactly match {expected_source!r} for curriculum_transfer/3"
                    )
            expected_hash = normalize_hash(
                entry.get("expected_existing_sha256"),
                required=action in {"replace", "delete"},
                label=label,
            )
        else:
            dest_rel = safe_rel(entry.get("destination", ""), f"{label}.destination")
            destination = github_root.joinpath(*dest_rel.parts)
            ensure_within(destination, github_root, label)
            destination_rel = dest_rel.as_posix()
            if action != "delete":
                source = entry.get("source")
                safe_rel(source or "", f"{label}.source")
            expected_hash = normalize_hash(
                entry.get("expected_existing_sha256"),
                required=action == "delete",
                label=label,
            )

        if destination_rel in destinations:
            raise TransferError(f"Duplicate destination in package: {destination_rel}")
        destinations.add(destination_rel)

        if source is not None:
            if source not in zip_names:
                raise TransferError(f"Missing payload member: {source}")
            info = zf.getinfo(source)
            if info.is_dir():
                raise TransferError(f"Payload source is a directory, expected file: {source}")

        original_mode: Optional[int] = None
        if action == "create":
            if destination.exists():
                raise TransferError(f"CREATE requires destination to be absent: {destination_rel}")
        else:
            if not destination.is_file():
                raise TransferError(f"{action.upper()} requires an existing file: {destination_rel}")
            original_mode = stat.S_IMODE(destination.stat().st_mode)
            if expected_hash:
                actual = sha256_file(destination)
                if actual != expected_hash:
                    raise TransferError(
                        f"SHA-256 mismatch for {destination_rel}: expected {expected_hash}, found {actual}"
                    )

        planned.append(
            PlannedAction(
                action=action,
                source=source,
                destination=destination,
                destination_rel=destination_rel,
                expected_sha256=expected_hash,
                original_mode=original_mode,
            )
        )

    return package_id, planned


def write_payload_atomic(zf: zipfile.ZipFile, source: str, dest: Path, mode: Optional[int]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = zf.read(source)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.name}.", suffix=".curriculum-transfer.tmp", dir=str(dest.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        tmp = Path(tmp_name)
        if mode is not None:
            os.chmod(tmp, mode)
        else:
            os.chmod(tmp, 0o644)
        if dest.name.endswith(".command"):
            os.chmod(tmp, stat.S_IMODE(tmp.stat().st_mode) | 0o111)
        os.replace(tmp, dest)
    finally:
        try:
            Path(tmp_name).unlink(missing_ok=True)
        except Exception:
            pass


def backup_path(backup_root: Path, destination_rel: str) -> Path:
    rel = PurePosixPath(destination_rel)
    return backup_root.joinpath(*rel.parts)


def remove_empty_parents(path: Path, stop: Path) -> None:
    current = path
    while current != stop and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def apply_package(
    package: Path,
    zf: zipfile.ZipFile,
    package_id: str,
    planned: List[PlannedAction],
    transfer_root: Path,
    github_root: Path,
) -> Tuple[List[str], Path]:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in package_id)[:120]
    backup_root = transfer_root / "_backups" / f"{stamp}_{safe_id}"
    created_files: List[Path] = []
    created_dirs: List[Path] = []
    backed_up: Dict[Path, Path] = {}
    messages: List[str] = []

    try:
        for item in planned:
            if item.action in {"replace", "delete"}:
                bpath = backup_path(backup_root, item.destination_rel)
                bpath.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item.destination, bpath)
                backed_up[item.destination] = bpath

        for item in planned:
            before_parents: List[Path] = []
            parent = item.destination.parent
            cursor = parent
            while cursor != github_root and not cursor.exists():
                before_parents.append(cursor)
                cursor = cursor.parent

            if item.action == "create":
                write_payload_atomic(zf, item.source or "", item.destination, mode=None)
                created_files.append(item.destination)
                created_dirs.extend(before_parents)
                messages.append(f"CREATED: {item.destination_rel}")
            elif item.action == "replace":
                write_payload_atomic(zf, item.source or "", item.destination, mode=item.original_mode)
                if item.destination.name.endswith(".command"):
                    os.chmod(item.destination, stat.S_IMODE(item.destination.stat().st_mode) | 0o111)
                messages.append(f"REPLACED: {item.destination_rel}")
            elif item.action == "delete":
                item.destination.unlink()
                messages.append(f"DELETED: {item.destination_rel}")

        return messages, backup_root
    except Exception:
        rollback_errors: List[str] = []
        for dest, bpath in reversed(list(backed_up.items())):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bpath, dest)
            except Exception as exc:
                rollback_errors.append(f"restore {dest}: {exc}")
        for path in reversed(created_files):
            try:
                path.unlink(missing_ok=True)
            except Exception as exc:
                rollback_errors.append(f"remove {path}: {exc}")
        for directory in sorted(set(created_dirs), key=lambda p: len(p.parts), reverse=True):
            try:
                remove_empty_parents(directory, github_root)
            except Exception as exc:
                rollback_errors.append(f"remove dir {directory}: {exc}")
        if rollback_errors:
            raise TransferError("Apply failed and rollback had errors: " + "; ".join(rollback_errors))
        raise


def log_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def process_package(
    package: Path,
    transfer_root: Path,
    github_root: Path,
    approved_roots: Dict[str, Path],
) -> Tuple[str, str]:
    lines: List[str] = [f"Package: {package}", f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    try:
        with zipfile.ZipFile(package, "r") as zf:
            bad = zf.testzip()
            if bad:
                raise TransferError(f"ZIP integrity failure at member: {bad}")
            manifest = read_manifest(zf)
            if manifest is None:
                return "ignored", "No TRANSFER_MANIFEST.json"
            package_id, planned = plan_package(package, zf, manifest, github_root, approved_roots)
            lines.append(f"Package id: {package_id}")
            lines.append(f"Validated actions: {len(planned)}")
            messages, backup_root = apply_package(package, zf, package_id, planned, transfer_root, github_root)
            lines.extend(messages)
            lines.append(f"Backup root: {backup_root}")
            lines.append("No Git actions were run.")

        dest = unique_destination(transfer_root / "_processed", package.name)
        shutil.move(str(package), str(dest))
        lines.append(f"Moved package to: {dest}")
        lines.append(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        log_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{package.stem}.log"
        log_text(transfer_root / "_logs" / log_name, "\n".join(lines) + "\n")
        return "success", "\n".join(messages)
    except Exception as exc:
        lines.append(f"ERROR: {exc}")
        lines.append("No Git actions were run.")
        lines.append(traceback.format_exc())
        try:
            dest = unique_destination(transfer_root / "_failed", package.name)
            shutil.move(str(package), str(dest))
            lines.append(f"Moved package to: {dest}")
        except Exception as move_exc:
            lines.append(f"Could not move failed package: {move_exc}")
        log_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{package.stem}_FAILED.log"
        log_text(transfer_root / "_logs" / log_name, "\n".join(lines) + "\n")
        return "failure", str(exc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-root", type=Path, required=True)
    parser.add_argument("--github-root", type=Path, required=True)
    args = parser.parse_args()

    transfer_root = args.transfer_root.expanduser().resolve()
    github_root = args.github_root.expanduser().resolve()

    for name in ("downloads", "_processed", "_failed", "_backups", "_logs"):
        (transfer_root / name).mkdir(parents=True, exist_ok=True)

    approved_roots = load_roots(transfer_root / "approved_roots.json", github_root)
    packages = collect_zip_files([transfer_root / "downloads"])
    recognized = 0
    succeeded = 0
    failed = 0

    if not packages:
        print("No ZIP packages found.")
        return 0

    for package in packages:
        try:
            with zipfile.ZipFile(package, "r") as zf:
                if MANIFEST_NAME not in zf.namelist():
                    continue
        except zipfile.BadZipFile:
            # A broken ZIP in the transfer inbox is actionable and should fail visibly.
            status, detail = process_package(package, transfer_root, github_root, approved_roots)
            recognized += 1
            failed += int(status == "failure")
            print(f"\nFAILED: {package.name}\n{detail}")
            continue

        recognized += 1
        status, detail = process_package(package, transfer_root, github_root, approved_roots)
        if status == "success":
            succeeded += 1
            print(f"\nAPPLIED: {package.name}")
            if detail:
                print(detail)
        elif status == "failure":
            failed += 1
            print(f"\nFAILED: {package.name}\n{detail}")

    if recognized == 0:
        print("No Curriculum Transfer packages found.")
        return 0

    print(f"\nFinished: {succeeded} applied, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
