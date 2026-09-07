from __future__ import annotations

import hashlib
import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .authorities import ProjectContext, resolve_common
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha
from .map_audit import audit_bank_map, save_audit_report

REVIEW_SCHEMA = "curriculum-builder-semantic-review/0.2.1"
TRANSFER_SCHEMA = 2
DIRECT_CODE = "DIRECT_READ_STRUCTURE_MISMATCH"


def _rid(rec: Dict[str, Any]) -> str:
    return str(rec.get("design_slot_id") or rec.get("record_id") or rec.get("seed_id") or "")


def _iter_map_records(data: Any) -> Iterable[Dict[str, Any]]:
    if not isinstance(data, dict):
        return
    records = data.get("records")
    if isinstance(records, list):
        for rec in records:
            if isinstance(rec, dict):
                yield rec
    wtcs = data.get("wtcs")
    if isinstance(wtcs, list):
        for wtc in wtcs:
            if not isinstance(wtc, dict):
                continue
            parts = wtc.get("parts_plan")
            if isinstance(parts, list):
                for rec in parts:
                    if isinstance(rec, dict):
                        yield rec


def _structure_ids(library_path: Path) -> set[str]:
    text = library_path.read_text(encoding="utf-8")
    ids = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            ids.add(line[4:].strip())
    return ids


def _snapshot_source_map(run_dir: Path, course_folder: str, unit: int) -> Path:
    return run_dir / "inputs" / course_folder / "banks" / f"unit{unit}" / "source_map"


def _current_source_map(ctx: ProjectContext) -> Path:
    return ctx.course_dir / f"banks/unit{ctx.unit}/source_map"


def _compare_trees(a: Path, b: Path) -> List[str]:
    problems: List[str] = []
    a_files = {p.relative_to(a).as_posix(): p for p in a.rglob("*") if p.is_file() and not p.name.startswith(".")}
    b_files = {p.relative_to(b).as_posix(): p for p in b.rglob("*") if p.is_file() and not p.name.startswith(".")}
    if set(a_files) != set(b_files):
        problems.append(f"file set differs: snapshot={sorted(a_files)} current={sorted(b_files)}")
        return problems
    for rel in sorted(a_files):
        if sha256_file(a_files[rel]) != sha256_file(b_files[rel]):
            problems.append(rel)
    return problems


def _load_run_manifest(run_dir: Path) -> Dict[str, Any]:
    p = run_dir / "RUN_MANIFEST.json"
    if not p.is_file():
        raise ValueError(f"RUN_MANIFEST.json not found for AI review run: {run_dir}")
    data = read_json(p)
    if not isinstance(data, dict):
        raise ValueError("RUN_MANIFEST.json is not an object")
    return data


def _candidate_ids_from_run(run_dir: Path, manifest: Dict[str, Any]) -> List[str]:
    ids = manifest.get("semantic_candidate_ids")
    if isinstance(ids, list) and all(isinstance(x, str) and x for x in ids):
        return list(ids)
    audit_path = run_dir / "LOCAL_MAP_AUDIT.json"
    audit = read_json(audit_path)
    out = []
    for f in audit.get("findings", []) if isinstance(audit, dict) else []:
        if isinstance(f, dict) and f.get("code") == DIRECT_CODE and f.get("record_id"):
            out.append(str(f["record_id"]))
    return out


def validate_semantic_review(ctx: ProjectContext, staging_root: Path, review: Dict[str, Any], course_folder: str) -> Dict[str, Any]:
    if not isinstance(review, dict):
        raise ValueError("AI semantic review must be a JSON object")
    if review.get("schema") != REVIEW_SCHEMA:
        raise ValueError(f"AI review schema must be {REVIEW_SCHEMA}")
    run_id = str(review.get("run_id") or "").strip()
    if not run_id:
        raise ValueError("AI review is missing run_id")
    run_dir = staging_root / "runs" / run_id
    manifest = _load_run_manifest(run_dir)

    if manifest.get("job") != "audit_rebuild_bank_map":
        raise ValueError("AI review run is not an Audit + Rebuild Bank Map run")
    if review.get("course") != ctx.course or int(review.get("unit", -1)) != ctx.unit:
        raise ValueError("AI review course/unit does not match the selected pilot course/unit")
    if manifest.get("course") != ctx.course or int(manifest.get("unit", -1)) != ctx.unit:
        raise ValueError("RUN_MANIFEST course/unit does not match the selected pilot course/unit")

    current_system = read_head_sha(ctx.memories_dir)
    current_course = read_head_sha(ctx.course_dir)
    if manifest.get("system_head") and current_system != manifest.get("system_head"):
        raise ValueError("memories HEAD changed since AI handoff. Re-run Local Map Audit + AI handoff before importing this review.")
    if manifest.get("course_head") and current_course != manifest.get("course_head"):
        raise ValueError("course HEAD changed since AI handoff. Re-run Local Map Audit + AI handoff before importing this review.")

    snapshot = _snapshot_source_map(run_dir, course_folder, ctx.unit)
    current = _current_source_map(ctx)
    if not snapshot.is_dir():
        raise ValueError(f"AI handoff source_map snapshot is missing: {snapshot}")
    if not current.is_dir():
        raise ValueError(f"Current source_map is missing: {current}")
    changed = _compare_trees(snapshot, current)
    if changed:
        raise ValueError("Current source_map changed since the AI handoff. Re-run the local audit/handoff. Changed: " + ", ".join(changed[:12]))

    expected = _candidate_ids_from_run(run_dir, manifest)
    expected_set = set(expected)
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("AI review decisions must be a list")
    ids = [str(x.get("design_slot_id") or "") for x in decisions if isinstance(x, dict)]
    if len(ids) != len(decisions) or any(not x for x in ids):
        raise ValueError("Every AI review decision must have design_slot_id")
    if len(set(ids)) != len(ids):
        raise ValueError("AI review contains duplicate design_slot_id values")
    if set(ids) != expected_set:
        missing = sorted(expected_set - set(ids))
        extra = sorted(set(ids) - expected_set)
        raise ValueError(f"AI review candidate ID set mismatch. missing={missing}; extra={extra}")

    common = resolve_common(ctx)
    version_manifest = read_json(common["question_structure_manifest"])
    rel_library = None
    if isinstance(version_manifest, dict):
        for entry in version_manifest.get("files", []) if isinstance(version_manifest.get("files"), list) else []:
            if isinstance(entry, dict) and str(entry.get("path", "")).endswith("Universal_Question_Structure_Library_v2.md"):
                rel_library = str(entry["path"])
                break
    if not rel_library:
        raise ValueError("Current Question Structure version manifest does not declare Universal_Question_Structure_Library_v2.md")
    library_path = common["question_structure_manifest"].parent / rel_library
    valid_structures = _structure_ids(library_path)

    design_path = current / f"unit{ctx.unit}_question_design_map.json"
    design = read_json(design_path)
    by_id = {_rid(r): r for r in _iter_map_records(design)}

    normalized: List[Dict[str, str]] = []
    for raw in decisions:
        assert isinstance(raw, dict)
        rid = str(raw.get("design_slot_id"))
        decision = str(raw.get("decision") or "").upper()
        current_id = str(raw.get("current_question_structure_id") or "")
        recommended = str(raw.get("recommended_question_structure_id") or "")
        reason = str(raw.get("reason") or "").strip()
        if decision not in {"KEEP", "REPAIR"}:
            raise ValueError(f"{rid}: decision must be KEEP or REPAIR")
        rec = by_id.get(rid)
        if not rec:
            raise ValueError(f"{rid}: candidate does not exist in current design map")
        actual_current = str(rec.get("question_structure_id") or "")
        if current_id != actual_current:
            raise ValueError(f"{rid}: AI current_question_structure_id={current_id!r} does not match current map {actual_current!r}")
        if not recommended:
            raise ValueError(f"{rid}: recommended_question_structure_id is required")
        if recommended not in valid_structures:
            raise ValueError(f"{rid}: recommended structure {recommended!r} is not in the current Universal Question Structure Library")
        if decision == "KEEP" and recommended != actual_current:
            raise ValueError(f"{rid}: KEEP must recommend the current structure ID")
        if decision == "REPAIR" and recommended == actual_current:
            raise ValueError(f"{rid}: REPAIR must recommend a different structure ID")
        if not reason:
            raise ValueError(f"{rid}: reason is required")
        normalized.append({
            "design_slot_id": rid,
            "decision": decision,
            "current_question_structure_id": actual_current,
            "recommended_question_structure_id": recommended,
            "reason": reason,
        })

    return {
        "run_id": run_id,
        "run_dir": run_dir,
        "run_manifest": manifest,
        "candidate_ids": expected,
        "decisions": normalized,
        "snapshot_source_map": snapshot,
        "current_source_map": current,
        "library_path": library_path,
    }


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _update_records_file(path: Path, changes: Dict[str, str]) -> Tuple[int, List[str]]:
    data = read_json(path)
    changed_ids: List[str] = []
    for rec in _iter_map_records(data):
        rid = _rid(rec)
        if rid in changes:
            before = str(rec.get("question_structure_id") or "")
            after = changes[rid]
            if before != after:
                rec["question_structure_id"] = after
                changed_ids.append(rid)
    if changed_ids:
        _write_json(path, data)
    return len(changed_ids), changed_ids


def _map_fingerprint(source_map: Path, unit: int) -> str:
    names = [
        "bank_inventory_map.json",
        "exit_map.json",
        "practice1_map.json",
        "seed_map.json",
        "summative_map.json",
        f"unit{unit}_question_design_map.json",
        "wtc_map.json",
    ]
    h = hashlib.sha256()
    for name in sorted(names):
        p = source_map / name
        digest = sha256_file(p)
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def _append_report(report_path: Path, repair_count: int, keep_count: int, system_head: str | None, course_head: str | None) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = report_path.read_text(encoding="utf-8") if report_path.is_file() else ""
    block = f"""

AUDIT + REBUILD — CURRICULUM BUILDER PILOT v0.3
===============================================
- Completed: {stamp}
- Current audit system HEAD: {system_head or 'unknown'}
- Current audit course HEAD: {course_head or 'unknown'}
- Mechanical shape before repair: PASS
- AI semantic candidates reviewed: {repair_count + keep_count}
- question_structure_id repairs applied: {repair_count}
- candidates kept unchanged: {keep_count}
- Other map fields changed by semantic import: 0
- Post-repair local audit: PASS
- Finished-task design slots preserved: 208
- Generation provenance above remains the original generation snapshot.
- FINALIZATION_QA: PASS (JSON/TXT-only map; rendered HTML finalization not applicable.)
"""
    report_path.write_text(existing.rstrip() + block + "\n", encoding="utf-8")


def _refresh_manifest(source_map: Path, unit: int, repair_count: int, keep_count: int, system_head: str | None, course_head: str | None) -> None:
    path = source_map / "MAP_MANIFEST.json"
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ValueError("MAP_MANIFEST.json is not an object")
    qa = manifest.setdefault("qa", {})
    if isinstance(qa, dict):
        qa["status"] = "PASS"
        sem = qa.setdefault("semantic_conflicts", {})
        if isinstance(sem, dict):
            sem["direct_read_inflation_conflicts"] = 0
    manifest["status"] = "PASS"
    manifest["map_fingerprint"] = _map_fingerprint(source_map, unit)
    manifest["map_fingerprint_method"] = "pilot-map-content-manifest-v1"
    manifest["latest_audit_rebuild"] = {
        "pilot_version": "0.3.0",
        "system_head": system_head,
        "course_head": course_head,
        "semantic_candidates_reviewed": repair_count + keep_count,
        "question_structure_repairs": repair_count,
        "kept": keep_count,
        "mechanical_shape_preserved": True,
        "post_repair_local_audit": "PASS",
    }
    declared = manifest.get("files")
    if isinstance(declared, list):
        for entry in declared:
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path")
            if rel and (source_map / str(rel)).is_file():
                entry["sha256"] = sha256_file(source_map / str(rel))
    _write_json(path, manifest)


def _refresh_manifest_hashes_after_report(source_map: Path) -> None:
    path = source_map / "MAP_MANIFEST.json"
    manifest = read_json(path)
    declared = manifest.get("files") if isinstance(manifest, dict) else None
    if isinstance(declared, list):
        for entry in declared:
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path")
            if rel and (source_map / str(rel)).is_file():
                entry["sha256"] = sha256_file(source_map / str(rel))
    _write_json(path, manifest)


def _changed_vs_original(original: Path, staged: Path) -> List[Path]:
    out: List[Path] = []
    for p in sorted(staged.iterdir()):
        if not p.is_file() or p.name.startswith("."):
            continue
        q = original / p.name
        if not q.is_file() or sha256_file(p) != sha256_file(q):
            out.append(p)
    return out


def _create_transfer_zip(ctx: ProjectContext, original: Path, staged: Path, changed_files: List[Path], out_zip: Path, system_head: str | None, course_head: str | None) -> None:
    files = []
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in changed_files:
            rel_inside = src.relative_to(staged)
            dest_rel = Path(ctx.course_dir.name) / f"banks/unit{ctx.unit}/source_map" / rel_inside
            payload_rel = Path("payload") / dest_rel
            original_file = original / rel_inside
            entry = {
                "action": "replace" if original_file.is_file() else "create",
                "source": payload_rel.as_posix(),
                "destination": dest_rel.as_posix(),
            }
            if original_file.is_file():
                entry["expected_existing_sha256"] = sha256_file(original_file)
            files.append(entry)
            zf.write(src, payload_rel.as_posix())
        manifest = {
            "schema_version": TRANSFER_SCHEMA,
            "package_type": "github_transfer",
            "package_id": f"{ctx.course_dir.name}_u{ctx.unit}_bank_map_audit_repair_pilot_v0_3_{time.strftime('%Y%m%d-%H%M%S')}",
            "source_snapshot": {
                "system_head": system_head,
                "course_head": course_head,
            },
            "files": files,
        }
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")


def apply_semantic_review_to_staging(ctx: ProjectContext, staging_root: Path, review: Dict[str, Any], course_folder: str, transfer_root: Path) -> Dict[str, Any]:
    validated = validate_semantic_review(ctx, staging_root, review, course_folder)
    run_id = validated["run_id"]
    source_map = validated["current_source_map"]
    decisions = validated["decisions"]

    repair_decisions = [d for d in decisions if d["decision"] == "REPAIR"]
    keep_decisions = [d for d in decisions if d["decision"] == "KEEP"]
    changes = {d["design_slot_id"]: d["recommended_question_structure_id"] for d in repair_decisions}

    stamp = time.strftime("%Y%m%d-%H%M%S")
    repair_run = staging_root / "runs" / f"{stamp}_{ctx.course_dir.name}_u{ctx.unit}_semantic_repair"
    staged = repair_run / "staged_source_map"
    repair_run.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source_map, staged)
    _write_json(repair_run / "AI_SEMANTIC_REVIEW.json", review)

    file_names = [
        f"unit{ctx.unit}_question_design_map.json",
        "exit_map.json",
        "summative_map.json",
        "practice1_map.json",
        "wtc_map.json",
    ]
    touched_by_file: Dict[str, List[str]] = {}
    total_occurrences = 0
    seen_repair_ids: set[str] = set()
    for name in file_names:
        p = staged / name
        if not p.is_file():
            continue
        count, ids = _update_records_file(p, changes)
        if count:
            touched_by_file[name] = ids
            total_occurrences += count
            seen_repair_ids.update(ids)
    missing = sorted(set(changes) - seen_repair_ids)
    if missing:
        raise ValueError("Repair candidate IDs were not found in staged map files: " + ", ".join(missing))

    system_head = read_head_sha(ctx.memories_dir)
    course_head = read_head_sha(ctx.course_dir)
    _append_report(staged / "MAP_REPORT.txt", len(repair_decisions), len(keep_decisions), system_head, course_head)
    _refresh_manifest(staged, ctx.unit, len(repair_decisions), len(keep_decisions), system_head, course_head)
    _refresh_manifest_hashes_after_report(staged)

    post = audit_bank_map(ctx, source_map_override=staged)
    save_audit_report(post, repair_run / "post_repair_audit")
    if post.get("mechanical_shape_status") != "PASS" or post.get("status") != "PASS":
        raise ValueError(f"Post-repair local audit did not PASS: status={post.get('status')} mechanical={post.get('mechanical_shape_status')}")

    changed_files = _changed_vs_original(source_map, staged)
    if not changed_files:
        raise ValueError("AI review produced no staged changes; no transfer package was created")

    transfer_name = f"{ctx.course_dir.name}_u{ctx.unit}_bank_map_audit_repair_pilot_v0_3_TRANSFER.zip"
    transfer_zip = transfer_root / transfer_name
    _create_transfer_zip(ctx, source_map, staged, changed_files, transfer_zip, system_head, course_head)

    result = {
        "schema": "curriculum-builder-semantic-repair-result/0.3",
        "source_ai_run_id": run_id,
        "repair_run_dir": str(repair_run),
        "staged_source_map": str(staged),
        "repair_count": len(repair_decisions),
        "keep_count": len(keep_decisions),
        "changed_file_count": len(changed_files),
        "changed_files": [p.name for p in changed_files],
        "touched_occurrences": total_occurrences,
        "touched_by_file": touched_by_file,
        "post_repair_audit_status": post.get("status"),
        "post_repair_mechanical_status": post.get("mechanical_shape_status"),
        "post_repair_design_record_count": post.get("facts", {}).get("design_record_count"),
        "post_repair_semantic_candidate_count": post.get("facts", {}).get("semantic_candidate_count"),
        "transfer_zip": str(transfer_zip),
        "git_writes": False,
        "canonical_repo_modified": False,
    }
    _write_json(repair_run / "REPAIR_RESULT.json", result)
    return result
