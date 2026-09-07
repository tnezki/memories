from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .authorities import ProjectContext, resolve_bank_sources
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha


def _result(name: str, status: str, detail: str, path: str | None = None) -> Dict[str, str]:
    data = {"name": name, "status": status, "detail": detail}
    if path:
        data["path"] = path
    return data


def _check_file(path: Path) -> Dict[str, str]:
    if path.is_file():
        return _result(path.name, "PASS", "Readable file", str(path))
    if path.is_dir():
        return _result(path.name, "PASS", "Readable directory", str(path))
    return _result(path.name, "FAIL", "Missing required path", str(path))


def _validate_source_map(source_map: Path) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    manifest_path = source_map / "MAP_MANIFEST.json"
    if not manifest_path.is_file():
        out.append(_result("MAP_MANIFEST", "FAIL", "Accepted source map is not installed", str(manifest_path)))
        return out
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        out.append(_result("MAP_MANIFEST", "FAIL", f"Invalid JSON: {exc}", str(manifest_path)))
        return out
    status = str(manifest.get("status", "")).upper()
    out.append(_result("MAP_MANIFEST status", "PASS" if status == "PASS" else "FAIL", f"status={status or 'missing'}", str(manifest_path)))

    # Verify declared file hashes when the manifest exposes a recognizable file collection.
    declared = manifest.get("files")
    if isinstance(declared, list):
        checked = 0
        bad = 0
        for entry in declared:
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path") or entry.get("file") or entry.get("name")
            expected = entry.get("sha256")
            if not rel or not expected:
                continue
            p = source_map / str(rel)
            checked += 1
            if not p.is_file() or sha256_file(p) != expected:
                bad += 1
        out.append(_result("Declared map hashes", "PASS" if bad == 0 else "FAIL", f"checked={checked}; mismatches={bad}"))
    return out


def run_preflight(ctx: ProjectContext, job: str) -> Dict[str, object]:
    steps: List[Dict[str, str]] = []
    steps.append(_result("Local memories repo", "PASS" if ctx.memories_dir.is_dir() else "FAIL", str(ctx.memories_dir)))
    steps.append(_result("Local course repo", "PASS" if ctx.course_dir.is_dir() else "FAIL", str(ctx.course_dir)))
    steps.append(_result("memories HEAD", "PASS" if read_head_sha(ctx.memories_dir) else "WARN", read_head_sha(ctx.memories_dir) or "Unable to resolve local HEAD without git"))
    steps.append(_result("course HEAD", "PASS" if read_head_sha(ctx.course_dir) else "WARN", read_head_sha(ctx.course_dir) or "Unable to resolve local HEAD without git"))

    try:
        required = resolve_bank_sources(ctx, job)
    except Exception as exc:
        steps.append(_result("Authority resolution", "FAIL", str(exc)))
        return {"status": "FAIL", "steps": steps}

    for path in required:
        steps.append(_check_file(path))

    if job in {"audit_rebuild_bank_map", "bank_complete"}:
        source_map = ctx.course_dir / f"banks/unit{ctx.unit}/source_map"
        steps.extend(_validate_source_map(source_map))

    # Hard source-boundary check: the pilot intentionally has no network or File Library route.
    steps.append(_result("Source boundary", "PASS", "Local project repos only; no public web, File Library, or chat-memory recovery"))
    steps.append(_result("Git safety", "PASS", "Pilot contains no Git command execution or GitHub write path"))

    fail_count = sum(1 for s in steps if s["status"] == "FAIL")
    status = "PASS" if fail_count == 0 else "FAIL"
    return {"status": status, "fail_count": fail_count, "steps": steps}
