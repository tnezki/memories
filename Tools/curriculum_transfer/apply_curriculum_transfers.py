#!/usr/bin/env python3
"""Apply Curriculum Transfer packages safely to approved local roots.

Default behavior is transactional publishing for Git-backed destinations:
validate -> verify clean/synced repos -> apply -> verify -> commit exact transfer
paths -> push. Use --local-only to preserve the older apply-without-Git behavior.

The tool supports curriculum_transfer/3 and legacy github_transfer/2 packages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
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


class PushError(TransferError):
    def __init__(self, message: str, pending_repos: List[str]):
        super().__init__(message)
        self.pending_repos = pending_repos


@dataclass
class PlannedAction:
    action: str
    source: Optional[str]
    destination: Path
    destination_rel: str
    expected_sha256: Optional[str]
    original_mode: Optional[int]


@dataclass
class RepoPlan:
    root: Path
    paths: List[str]
    before_sha: str
    branch: str
    upstream: str
    commit_sha: Optional[str] = None
    pushed: bool = False


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


def verify_applied(zf: zipfile.ZipFile, planned: List[PlannedAction]) -> None:
    for item in planned:
        if item.action == "delete":
            if item.destination.exists():
                raise TransferError(f"Post-apply verification failed; file still exists: {item.destination_rel}")
            continue
        if not item.destination.is_file():
            raise TransferError(f"Post-apply verification failed; file missing: {item.destination_rel}")
        expected = hashlib.sha256(zf.read(item.source or "")).hexdigest()
        actual = sha256_file(item.destination)
        if actual != expected:
            raise TransferError(
                f"Post-apply SHA-256 mismatch for {item.destination_rel}: expected {expected}, found {actual}"
            )


def run_git(repo: Path, args: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise TransferError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return proc


def existing_ancestor(path: Path, stop: Path) -> Path:
    cursor = path if path.is_dir() else path.parent
    while not cursor.exists() and cursor != stop:
        cursor = cursor.parent
    return cursor


def discover_repo(path: Path, github_root: Path) -> Optional[Path]:
    anchor = existing_ancestor(path, github_root)
    proc = subprocess.run(
        ["git", "-C", str(anchor), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    repo = Path(proc.stdout.strip()).resolve()
    ensure_within(repo, github_root, "Git repository")
    return repo


def repo_relative(repo: Path, destination: Path) -> str:
    return destination.resolve(strict=False).relative_to(repo.resolve()).as_posix()


def build_repo_plans(planned: List[PlannedAction], github_root: Path) -> Tuple[List[RepoPlan], List[str]]:
    grouped: Dict[Path, Set[str]] = {}
    local_only: List[str] = []
    for item in planned:
        repo = discover_repo(item.destination, github_root)
        if repo is None:
            local_only.append(item.destination_rel)
            continue
        grouped.setdefault(repo, set()).add(repo_relative(repo, item.destination))

    plans: List[RepoPlan] = []
    for repo in sorted(grouped, key=lambda p: str(p).lower()):
        before_sha = run_git(repo, ["rev-parse", "HEAD"]).stdout.strip()
        branch = run_git(repo, ["symbolic-ref", "--short", "HEAD"]).stdout.strip()
        upstream_proc = run_git(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], check=False)
        if upstream_proc.returncode != 0 or not upstream_proc.stdout.strip():
            raise TransferError(f"Git preflight failed for {repo.name}: current branch has no upstream")
        upstream = upstream_proc.stdout.strip()
        plans.append(
            RepoPlan(
                root=repo,
                paths=sorted(grouped[repo]),
                before_sha=before_sha,
                branch=branch,
                upstream=upstream,
            )
        )
    return plans, local_only


def preflight_git(repo_plans: List[RepoPlan]) -> None:
    for plan in repo_plans:
        unstaged = set(run_git(plan.root, ["diff", "--name-only"]).stdout.splitlines())
        staged = set(run_git(plan.root, ["diff", "--cached", "--name-only"]).stdout.splitlines())
        untracked = set(
            run_git(plan.root, ["ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
        )
        changed = {p for p in (unstaged | staged | untracked) if p}
        unexpected = sorted(changed - set(plan.paths))
        if unexpected:
            preview = ", ".join(unexpected[:8])
            if len(unexpected) > 8:
                preview += f", ... (+{len(unexpected) - 8} more)"
            raise TransferError(
                f"Git preflight failed for {plan.root.name}: unrelated local changes are present: {preview}. "
                "Commit, stash, or discard them before applying this transfer, or use the Local Only launcher."
            )

        name = run_git(plan.root, ["config", "--get", "user.name"], check=False).stdout.strip()
        email = run_git(plan.root, ["config", "--get", "user.email"], check=False).stdout.strip()
        if not name or not email:
            raise TransferError(f"Git preflight failed for {plan.root.name}: git user.name/user.email are not configured")

        counts = run_git(plan.root, ["rev-list", "--left-right", "--count", f"HEAD...{plan.upstream}"]).stdout.strip().split()
        if len(counts) != 2:
            raise TransferError(f"Git preflight failed for {plan.root.name}: could not compare HEAD to {plan.upstream}")
        ahead, behind = int(counts[0]), int(counts[1])
        if ahead or behind:
            raise TransferError(
                f"Git preflight failed for {plan.root.name}: local branch and {plan.upstream} are not synchronized "
                f"(ahead {ahead}, behind {behind}). Sync first, then apply the transfer."
            )

        dry = run_git(plan.root, ["push", "--dry-run"], check=False)
        if dry.returncode != 0:
            detail = (dry.stderr or dry.stdout).strip()
            raise TransferError(f"Git preflight failed for {plan.root.name}: push check failed: {detail}")


def commit_transfer(repo_plans: List[RepoPlan], package_id: str) -> List[str]:
    messages: List[str] = []
    for plan in repo_plans:
        run_git(plan.root, ["add", "-A", "--", *plan.paths])

        staged_all = run_git(plan.root, ["diff", "--cached", "--name-only"]).stdout.splitlines()
        unexpected = sorted(set(staged_all) - set(plan.paths))
        if unexpected:
            raise TransferError(
                f"Refusing to commit unexpected staged paths in {plan.root.name}: {', '.join(unexpected)}"
            )

        staged = [p for p in staged_all if p in plan.paths]
        if not staged:
            messages.append(f"NO GIT CHANGE: {plan.root.name} (payload already matched repository content)")
            continue

        message = f"Curriculum transfer: {package_id}"
        run_git(plan.root, ["commit", "-m", message, "--", *plan.paths])
        plan.commit_sha = run_git(plan.root, ["rev-parse", "HEAD"]).stdout.strip()
        messages.append(f"COMMITTED: {plan.root.name} {plan.commit_sha[:12]}")
    return messages


def push_transfer(repo_plans: List[RepoPlan]) -> List[str]:
    messages: List[str] = []
    failures: List[str] = []
    for plan in repo_plans:
        if not plan.commit_sha:
            continue
        proc = run_git(plan.root, ["push"], check=False)
        if proc.returncode == 0:
            plan.pushed = True
            messages.append(f"PUSHED: {plan.root.name}/{plan.branch}")
        else:
            detail = (proc.stderr or proc.stdout).strip()
            failures.append(f"{plan.root.name}: {detail}")
    if failures:
        pending = [p.root.name for p in repo_plans if p.commit_sha and not p.pushed]
        raise PushError("One or more Git pushes failed: " + " | ".join(failures), pending)
    return messages


def rollback_unpublished(
    planned: List[PlannedAction],
    repo_plans: List[RepoPlan],
    backup_root: Path,
    github_root: Path,
) -> None:
    repo_by_path: Dict[Path, RepoPlan] = {}
    for plan in repo_plans:
        for item in planned:
            try:
                item.destination.resolve(strict=False).relative_to(plan.root.resolve())
                repo_by_path[item.destination] = plan
            except ValueError:
                pass

    errors: List[str] = []
    for plan in repo_plans:
        try:
            run_git(plan.root, ["reset", "--hard", plan.before_sha])
            created = [repo_relative(plan.root, i.destination) for i in planned if i.action == "create" and repo_by_path.get(i.destination) == plan]
            if created:
                run_git(plan.root, ["clean", "-fd", "--", *created])
        except Exception as exc:
            errors.append(f"reset {plan.root}: {exc}")

    for item in reversed(planned):
        if item.destination in repo_by_path:
            continue
        try:
            if item.action == "create":
                item.destination.unlink(missing_ok=True)
                remove_empty_parents(item.destination.parent, github_root)
            else:
                bpath = backup_path(backup_root, item.destination_rel)
                item.destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bpath, item.destination)
        except Exception as exc:
            errors.append(f"restore {item.destination_rel}: {exc}")

    if errors:
        raise TransferError("Automatic rollback had errors: " + "; ".join(errors))


def log_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_transaction(
    transfer_root: Path,
    package_id: str,
    package_name: str,
    backup_root: Path,
    repo_plans: List[RepoPlan],
    local_only_paths: List[str],
    status: str,
    note: Optional[str] = None,
) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in package_id)[:120]
    record = {
        "schema_version": 1,
        "package_id": package_id,
        "package_name": package_name,
        "status": status,
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backup_root": str(backup_root),
        "local_only_paths": local_only_paths,
        "repositories": [
            {
                "repo": str(p.root),
                "branch": p.branch,
                "upstream": p.upstream,
                "before_sha": p.before_sha,
                "commit_sha": p.commit_sha,
                "pushed": p.pushed,
                "paths": p.paths,
            }
            for p in repo_plans
        ],
    }
    if note:
        record["note"] = note
    out = transfer_root / "_transactions" / f"{stamp}_{safe_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return out


def process_package(
    package: Path,
    transfer_root: Path,
    github_root: Path,
    approved_roots: Dict[str, Path],
    local_only_mode: bool,
) -> Tuple[str, str]:
    lines: List[str] = [f"Package: {package}", f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    backup_root: Optional[Path] = None
    repo_plans: List[RepoPlan] = []
    local_only_paths: List[str] = []
    package_id = package.stem
    planned: List[PlannedAction] = []

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

            if not local_only_mode:
                repo_plans, local_only_paths = build_repo_plans(planned, github_root)
                preflight_git(repo_plans)
                for plan in repo_plans:
                    lines.append(f"Git preflight OK: {plan.root.name} ({plan.branch} -> {plan.upstream})")
                for path in local_only_paths:
                    lines.append(f"Local-only destination: {path}")

            messages, backup_root = apply_package(package, zf, package_id, planned, transfer_root, github_root)
            lines.extend(messages)
            lines.append(f"Backup root: {backup_root}")
            verify_applied(zf, planned)
            lines.append("Post-apply verification: PASS")

            if local_only_mode:
                lines.append("Git mode: LOCAL ONLY. No Git actions were run.")
            else:
                commit_messages = commit_transfer(repo_plans, package_id)
                lines.extend(commit_messages)
                push_messages = push_transfer(repo_plans)
                lines.extend(push_messages)
                if repo_plans:
                    lines.append("Git publish: SUCCESS")
                else:
                    lines.append("Git publish: not applicable; no Git-backed destinations were changed.")

        dest = unique_destination(transfer_root / "_processed", package.name)
        shutil.move(str(package), str(dest))
        lines.append(f"Moved package to: {dest}")
        lines.append(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if backup_root is not None:
            tx = write_transaction(
                transfer_root,
                package_id,
                package.name,
                backup_root,
                repo_plans,
                local_only_paths,
                "local_only" if local_only_mode else "published",
            )
            lines.append(f"Transaction record: {tx}")
        log_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{package.stem}.log"
        log_text(transfer_root / "_logs" / log_name, "\n".join(lines) + "\n")
        return "success", "\n".join(lines[3:])

    except PushError as exc:
        lines.append(f"ERROR: {exc}")
        lines.append("Files were applied and committed locally, but one or more pushes did not finish.")
        lines.append("Do not re-apply this transfer. Retry the pending push from GitHub Desktop or the repository command line.")
        if backup_root is not None:
            tx = write_transaction(
                transfer_root,
                package_id,
                package.name,
                backup_root,
                repo_plans,
                local_only_paths,
                "push_failed",
                note=str(exc),
            )
            lines.append(f"Transaction record: {tx}")
        try:
            dest = unique_destination(transfer_root / "_processed", package.name)
            shutil.move(str(package), str(dest))
            lines.append(f"Moved package to: {dest}")
        except Exception as move_exc:
            lines.append(f"Could not move package after push failure: {move_exc}")
        log_name = f"{time.strftime('%Y%m%d-%H%M%S')}_{package.stem}_PUSH_FAILED.log"
        log_text(transfer_root / "_logs" / log_name, "\n".join(lines) + "\n")
        return "failure", "\n".join(lines[2:])

    except Exception as exc:
        lines.append(f"ERROR: {exc}")
        # If files were already applied but nothing was pushed, restore the exact pre-transfer state.
        if backup_root is not None and not any(p.pushed for p in repo_plans):
            try:
                if local_only_mode:
                    # Local-only mode already has apply-time rollback; post-apply failures are verification-only.
                    for item in reversed(planned):
                        if item.action == "create":
                            item.destination.unlink(missing_ok=True)
                        else:
                            bpath = backup_path(backup_root, item.destination_rel)
                            item.destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(bpath, item.destination)
                else:
                    rollback_unpublished(planned, repo_plans, backup_root, github_root)
                lines.append("Automatic rollback: SUCCESS")
            except Exception as rollback_exc:
                lines.append(f"Automatic rollback: FAILED: {rollback_exc}")
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
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Apply transfers without Git commit/push. Intended for deliberate local testing or offline work.",
    )
    args = parser.parse_args()

    transfer_root = args.transfer_root.expanduser().resolve()
    github_root = args.github_root.expanduser().resolve()

    for name in ("downloads", "_processed", "_failed", "_backups", "_logs", "_transactions"):
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
            status, detail = process_package(
                package, transfer_root, github_root, approved_roots, args.local_only
            )
            recognized += 1
            failed += int(status == "failure")
            print(f"\nFAILED: {package.name}\n{detail}")
            continue

        recognized += 1
        status, detail = process_package(
            package, transfer_root, github_root, approved_roots, args.local_only
        )
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
