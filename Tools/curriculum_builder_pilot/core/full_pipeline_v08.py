from __future__ import annotations

import json
import shutil
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .authorities import ProjectContext
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha
from .map_audit import audit_bank_map, save_audit_report
from .map_skeleton import build_mechanical_map_skeleton
from .preflight import run_preflight
from . import full_pipeline as legacy

FULL_AI_SCHEMA = "curriculum-builder-ai-full-bank/0.8"
PIPELINE_SCHEMA = "curriculum-builder-full-bank-pipeline/0.8"
PILOT_VERSION = "0.8.0"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _slug(text: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def _pipeline_root(staging_root: Path, ctx: ProjectContext) -> Path:
    return staging_root / "full_pipeline" / _slug(ctx.course) / f"unit{ctx.unit}"


def _exchange_current(ai_exchange: Path, ctx: ProjectContext) -> Path:
    return ai_exchange / "Current" / _slug(ctx.course) / f"unit{ctx.unit}"


def _archive_exchange(ai_exchange: Path, pipeline_id: str) -> Path:
    return ai_exchange / "Archive" / pipeline_id


def _zip_dir(root: Path, out_zip: Path) -> Path:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != out_zip:
                zf.write(path, path.relative_to(root))
    return out_zip


def _combined_work_order(ctx: ProjectContext, run_id: str) -> str:
    return f"""CURRICULUM BUILDER v0.8 - ONE-HANDOFF FULL BANK PIPELINE

RUN ID: {run_id}
COURSE: {ctx.course}
UNIT: {ctx.unit}

SOURCE BOUNDARY - HARD
Use only files in this handoff plus the teacher's current explicit instruction. No public web, File Library, old chats, saved memory, old packages, or similarly named substitutes.

GOOD-ENOUGH / STOP RULE - HARD
Build the declared Map and Bank correctly, align to the included current authorities, satisfy the response contract, self-audit, and STOP. Do not reopen settled architecture or add optional polish.

MECHANICAL LOCK - HARD
Read MAP_BUILD_SKELETON.json first. Every design_slot_id, destination, section, Practice stage, WTC part, Summative form, count, and approved seed identity is locked. Do not add, drop, rename, or move slots.

ONE AI JOB
In ONE result:
1. Complete the semantic Bank Map fields for every locked slot.
2. Author the finished Bank content for those SAME slots using the semantic design you just supplied.

The local app will validate and audit map_records FIRST. It will only accept bank_records if that Map passes. Local code computes the accepted map fingerprint after validation, renders graphs/tables/math, audits the Bank, finalizes, and creates the GitHub transfer.

MAP RULES
- Preserve Exit architecture: current-section Mastery evidence plus mapped reassessment carry-forward.
- Practice 1: exactly 8 Intro + 8 Review + 8 Mastery per section.
- WTC: one meaningful shared stimulus with Parts A-D; dependency only when mathematically necessary.
- Summative V1-V6: secure parallel forms.
- Use exact Question Structure IDs from the included library.
- Direct representation reads stay direct; do not inflate them into inference structures.

BANK AUTHORING RULES
- Make every finished task materially execute its map evidence job/student action/Question Structure.
- Secure Summative prompts/keys remain private in this AI result.
- Do not reuse secure prompts in Practice.
- No TODO/TBD/placeholders.
- No internal authoring labels in student prose.
- For algebra coordinate-plane graphs use semantic_mode "algebra_coordinate". For a student blank graphing surface use response_surface kind "blank_coordinate_grid".
- Use semantic_mode "context" only for real-world/modeling axes with meaningful axis labels.
- Return structured graph/table/equation data. Do not hand-build graph SVG/PNG.
- Avoid raw caret math in prose when an equation block or MathJax-ready expression should carry the math.

OUTPUT CONTRACT - HARD
Return exactly ONE file named AI_FULL_BANK_RESULT.json:
{{
  "schema": "{FULL_AI_SCHEMA}",
  "run_id": "{run_id}",
  "course": "{ctx.course}",
  "unit": {ctx.unit},
  "map_records": [
    {{
      "design_slot_id": "exact locked ID",
      "mastery_goal": {{"goal_id": "...", "title": "...", "text": "..."}},
      "primary_i_can": {{"i_can_id": "...", "source_i_can_index": 1, "text": "..."}},
      "supporting_i_cans": [],
      "evidence_job": "...",
      "student_action": "...",
      "question_structure_id": "exact included-library ID",
      "response_mode": "...",
      "representation_mode": "...",
      "representation_need": "required|optional|none",
      "representation_routes": [],
      "difficulty_intent": "...",
      "variation_axes": {{"allowed": [], "required": [], "forbidden": []}},
      "security_role": "...",
      "slot_role": "...",
      "reassessment_of": null,
      "carry_forward_from": null,
      "shared_stimulus_id": null,
      "depends_on": null,
      "family_id": null
    }}
  ],
  "bank_records": [
    {{
      "design_slot_id": "exact locked ID",
      "prompt_text": "finished student-facing prompt",
      "prompt_blocks": [{{"type": "prose|equation|table|graph|response_surface", "data": {{}}}}],
      "answer_text": "finished answer/key",
      "solution_text": "finished reasoning/solution",
      "choices": [],
      "representation_data": {{}},
      "instantiation_summary": "brief values/context/variation used"
    }}
  ],
  "wtc_stimuli": [
    {{
      "shared_stimulus_id": "exact mapped shared stimulus ID",
      "student_text": "one shared setup for its Parts A-D",
      "content_blocks": []
    }}
  ]
}}

RESPONSE REQUIREMENTS
- map_records: exactly one record for every locked design_slot_id, no extras.
- bank_records: exactly one record for every locked design_slot_id, no extras.
- The bank record for an ID must implement that same ID's map record.
- wtc_stimuli: exactly one per mapped WTC shared_stimulus_id.
- selected_response records require visible distinct choices and one correct answer.
- self-audit both map and finished Bank before returning the single JSON file.
- stop after AI_FULL_BANK_RESULT.json.
"""


def _copy_combined_sources(ctx: ProjectContext, work: Path) -> None:
    # Bank Map authorities plus Complete Bank PM. Current deployed source_map is
    # deliberately excluded because v0.8 is testing a fresh staged map.
    legacy._snapshot_sources(ctx, "bank_map", work)
    legacy._snapshot_sources(ctx, "bank_complete", work, skip_current_source_map=True)


def start_full_pipeline(
    ctx: ProjectContext,
    staging_root: Path,
    ai_exchange: Path,
) -> Dict[str, Any]:
    preflight = run_preflight(ctx, "bank_map")
    if preflight.get("status") != "PASS":
        return {"status": "BLOCKED", "stage": "preflight", "preflight": preflight}

    root = _pipeline_root(staging_root, ctx)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    exchange = _exchange_current(ai_exchange, ctx)
    if exchange.exists():
        shutil.rmtree(exchange)
    exchange.mkdir(parents=True)

    pipeline_id = f"{time.strftime('%Y%m%d-%H%M%S')}_{_slug(ctx.course)}_u{ctx.unit}_full_bank_v08"
    run_id = pipeline_id + "_ai"

    # Keep the legacy map assembly helper's expected folder shape.
    map_ai = root / "map_ai"
    map_ai.mkdir()
    sk = build_mechanical_map_skeleton(ctx, staging_root)
    skeleton = sk["skeleton"]
    _write_json(map_ai / "MAP_BUILD_SKELETON.json", skeleton)

    work = root / "full_ai"
    work.mkdir()
    _copy_combined_sources(ctx, work)
    _write_json(work / "MAP_BUILD_SKELETON.json", skeleton)
    (work / "AI_WORK_ORDER.txt").write_text(_combined_work_order(ctx, run_id), encoding="utf-8")
    manifest = {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "job": "full_bank_pipeline_one_handoff",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "record_count": skeleton.get("slot_count"),
        "destination_counts": skeleton.get("destination_counts"),
        "seed_count": (skeleton.get("locked_contract") or {}).get("approved_seed_count"),
        "public_web_allowed": False,
        "file_library_allowed": False,
        "git_commands_allowed": False,
        "expected_result": "AI_FULL_BANK_RESULT.json",
    }
    _write_json(work / "RUN_MANIFEST.json", manifest)

    handoff_name = f"AI_HANDOFF_{''.join(ch for ch in ctx.course if ch.isalnum())}_U{ctx.unit}_FULL_BANK_ONE_HANDOFF.zip"
    handoff = _zip_dir(work, exchange / handoff_name)
    state = {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "stage": "awaiting_full_ai",
        "system_head": manifest["system_head"],
        "course_head": manifest["course_head"],
        "handoff": str(handoff),
        "exchange": str(exchange),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _write_json(root / "PIPELINE_STATE.json", state)
    return {
        "status": "AI_NEEDED",
        "stage": "awaiting_full_ai",
        "preflight": preflight,
        "pipeline_id": pipeline_id,
        "handoff": str(handoff),
        "exchange": str(exchange),
        "expected_result": "AI_FULL_BANK_RESULT.json",
        "record_count": skeleton.get("slot_count"),
        "destination_counts": skeleton.get("destination_counts"),
        "seed_count": manifest["seed_count"],
        "manual_ai_round_trips": 1,
    }


def _read_state(root: Path) -> Dict[str, Any]:
    path = root / "PIPELINE_STATE.json"
    return read_json(path) if path.is_file() else {}


def _write_state(root: Path, state: Dict[str, Any]) -> None:
    _write_json(root / "PIPELINE_STATE.json", state)


def _candidate_result_paths(ai_exchange: Path, ctx: ProjectContext, downloads: Path) -> List[Path]:
    paths: List[Path] = []
    current = _exchange_current(ai_exchange, ctx)
    if current.is_dir():
        paths.extend(p for p in current.glob("AI_FULL_BANK_RESULT*.json") if p.is_file())
    if downloads.is_dir():
        paths.extend(p for p in downloads.glob("AI_FULL_BANK_RESULT*.json") if p.is_file())
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def _find_and_import_result(
    ai_exchange: Path,
    ctx: ProjectContext,
    downloads: Path,
    expected_run_id: str,
) -> Tuple[Path, Dict[str, Any]]:
    errors: List[str] = []
    current = _exchange_current(ai_exchange, ctx)
    current.mkdir(parents=True, exist_ok=True)
    for path in _candidate_result_paths(ai_exchange, ctx, downloads):
        try:
            data = read_json(path)
            if data.get("schema") != FULL_AI_SCHEMA:
                continue
            if str(data.get("run_id") or "") != expected_run_id:
                continue
            if data.get("course") != ctx.course or int(data.get("unit", -1)) != ctx.unit:
                continue
            imported = current / "AI_FULL_BANK_RESULT.json"
            if path.resolve() != imported.resolve():
                if imported.exists():
                    imported.unlink()
                shutil.move(str(path), str(imported))
                path = imported
            return path, data
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    extra = f" Latest unreadable candidate: {errors[0]}" if errors else ""
    raise FileNotFoundError(
        f"AI result not found yet. Download AI_FULL_BANK_RESULT.json, then click Continue. Run: {expected_run_id}.{extra}"
    )


def _validate_combined_ids(ctx: ProjectContext, root: Path, ai: Dict[str, Any]) -> None:
    skeleton = read_json(root / "map_ai" / "MAP_BUILD_SKELETON.json")
    expected = {str(x.get("design_slot_id")) for x in skeleton.get("slots", []) if isinstance(x, dict)}
    for key in ("map_records", "bank_records"):
        rows = ai.get(key)
        if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
            raise ValueError(f"AI_FULL_BANK_RESULT {key} must be an array of objects")
        ids = [str(x.get("design_slot_id") or "") for x in rows]
        if not all(ids) or len(ids) != len(set(ids)) or set(ids) != expected:
            raise ValueError(f"AI_FULL_BANK_RESULT {key} IDs do not exactly match the locked {len(expected)} slots")


def _normalize_bank_graph_modes(bank_records: List[Dict[str, Any]]) -> None:
    # Rendering policy is local. AI supplies semantic data; local code decides
    # which registered graph-tool mode executes it.
    for rec in bank_records:
        blocks = rec.get("prompt_blocks")
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict):
                continue
            data = block.get("data") if isinstance(block.get("data"), dict) else None
            if data is None:
                continue
            if block.get("type") == "response_surface" and data.get("kind") == "blank_coordinate_grid":
                data["semantic_mode"] = "construction_surface"
                data.setdefault("x_min", -10)
                data.setdefault("x_max", 10)
                data.setdefault("y_min", -10)
                data.setdefault("y_max", 10)
                continue
            if block.get("type") != "graph":
                continue
            x_label = str(data.get("x_label") or "x").strip().lower()
            y_label = str(data.get("y_label") or "y").strip().lower()
            explicit = str(data.get("semantic_mode") or "").strip().lower()
            if explicit == "context" and (x_label != "x" or y_label != "y"):
                data["semantic_mode"] = "context"
            else:
                data["semantic_mode"] = "algebra_coordinate"
                data.setdefault("kind", "coordinate_graph")


def _prepare_internal_bank(ctx: ProjectContext, root: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    work = root / "bank_ai"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    skeleton = legacy._build_bank_skeleton_from_map(ctx, root / "staged_source_map", work)
    bank_run_id = str(state.get("pipeline_id")) + "_bank_internal"
    _write_json(work / "RUN_MANIFEST.json", {
        "schema": PIPELINE_SCHEMA,
        "run_id": bank_run_id,
        "pipeline_id": state.get("pipeline_id"),
        "course": ctx.course,
        "unit": ctx.unit,
        "job": "full_pipeline_bank_complete_internal",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "accepted_map_fingerprint": skeleton.get("accepted_map_fingerprint"),
    })
    state["bank_run_id"] = bank_run_id
    _write_state(root, state)
    return skeleton


def _final_transfer_v08(
    ctx: ProjectContext,
    staged_bank: Path,
    transfer_root: Path,
    system_head: str | None,
    course_head: str | None,
) -> Path:
    canonical = ctx.course_dir / "banks" / f"unit{ctx.unit}"
    staged_files = {p.relative_to(staged_bank).as_posix(): p for p in staged_bank.rglob("*") if p.is_file()}
    existing_files = {p.relative_to(canonical).as_posix(): p for p in canonical.rglob("*") if p.is_file()} if canonical.is_dir() else {}
    entries: List[Dict[str, Any]] = []
    payloads: List[Tuple[Path, str]] = []
    for rel, src in sorted(staged_files.items()):
        dst_rel = Path(ctx.course_dir.name) / "banks" / f"unit{ctx.unit}" / rel
        old = existing_files.get(rel)
        if old and sha256_file(old) == sha256_file(src):
            continue
        arc = (Path("payload") / dst_rel).as_posix()
        row: Dict[str, Any] = {
            "action": "replace" if old else "create",
            "source": arc,
            "destination": dst_rel.as_posix(),
        }
        if old:
            row["expected_existing_sha256"] = sha256_file(old)
        entries.append(row)
        payloads.append((src, arc))
    for rel, old in sorted(existing_files.items()):
        if rel not in staged_files:
            dst_rel = Path(ctx.course_dir.name) / "banks" / f"unit{ctx.unit}" / rel
            entries.append({
                "action": "delete",
                "destination": dst_rel.as_posix(),
                "expected_existing_sha256": sha256_file(old),
            })
    if not entries:
        raise ValueError("Full pipeline produced no repository changes to transfer")
    transfer_root.mkdir(parents=True, exist_ok=True)
    out = transfer_root / f"{ctx.course_dir.name}_u{ctx.unit}_FULL_BANK_PIPELINE_v0_8_TRANSFER.zip"
    manifest = {
        "schema_version": 2,
        "package_type": "github_transfer",
        "package_id": f"{ctx.course_dir.name}_u{ctx.unit}_full_bank_pipeline_v0_8_{time.strftime('%Y%m%d-%H%M%S')}",
        "source_snapshot": {"system_head": system_head, "course_head": course_head},
        "files": entries,
    }
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2))
        for src, arc in payloads:
            zf.write(src, arc)
    return out


def _extra_graph_audit(root: Path) -> Dict[str, Any]:
    specs_path = root / "bank_ai" / "GRAPH_SPECS.json"
    bad: List[str] = []
    counts = Counter()
    if specs_path.is_file():
        for spec in read_json(specs_path):
            if not isinstance(spec, dict):
                continue
            semantic = str(spec.get("semantic_mode") or "").lower()
            render = str(spec.get("pilot_render_mode") or "")
            kind = str(spec.get("kind") or "").lower()
            x_label = str(spec.get("x_label") or "x").lower()
            y_label = str(spec.get("y_label") or "y").lower()
            counts[render] += 1
            algebra = semantic in {"construction_surface", "algebra_coordinate", "coordinate", "point_read"}
            algebra = algebra or (kind == "coordinate_graph" and x_label == "x" and y_label == "y")
            if algebra and render != "standard_coordinate":
                bad.append(str(spec.get("filename") or "unknown"))
    return {
        "status": "PASS" if not bad else "FAIL",
        "graph_render_modes": dict(counts),
        "standard_coordinate_mode_mismatches": bad,
    }


def _archive_completed_exchange(ai_exchange: Path, ctx: ProjectContext, pipeline_id: str) -> None:
    current = _exchange_current(ai_exchange, ctx)
    if not current.exists():
        return
    archive = _archive_exchange(ai_exchange, pipeline_id)
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        shutil.rmtree(archive)
    shutil.move(str(current), str(archive))


def continue_full_pipeline(
    ctx: ProjectContext,
    staging_root: Path,
    ai_exchange: Path,
    downloads: Path,
    transfer_root: Path,
) -> Dict[str, Any]:
    root = _pipeline_root(staging_root, ctx)
    state = _read_state(root)
    if not state:
        raise ValueError("No active v0.8 Full Bank Pipeline. Click Start Fresh Full Pipeline first.")
    if state.get("stage") == "complete":
        return {
            "status": "PASS",
            "stage": "complete",
            "map_audit": state.get("map_audit"),
            "bank_audit": state.get("bank_audit"),
            "transfer_zip": state.get("transfer_zip"),
            "canonical_repo_modified": False,
        }
    if state.get("stage") != "awaiting_full_ai":
        raise ValueError(f"Unknown v0.8 pipeline stage: {state.get('stage')}")

    result_path, combined = _find_and_import_result(
        ai_exchange, ctx, downloads, str(state.get("run_id") or "")
    )
    _validate_combined_ids(ctx, root, combined)

    # 1) Assemble and audit the fresh map from the combined result.
    map_ai = {
        "schema": legacy.MAP_AI_SCHEMA,
        "records": combined["map_records"],
    }
    source_map = legacy._assemble_map(ctx, root, map_ai)
    map_report = audit_bank_map(ctx, source_map_override=source_map)
    audit_dir = root / "map_audit"
    if audit_dir.exists():
        shutil.rmtree(audit_dir)
    save_audit_report(map_report, audit_dir)
    if map_report.get("mechanical_shape_status") != "PASS":
        raise ValueError("Fresh staged Bank Map failed local mechanical audit")
    candidates = legacy._candidate_ids(map_report)
    if candidates:
        raise ValueError(
            f"Fresh staged Map still has {len(candidates)} semantic candidate(s). "
            "The one-handoff result must self-repair these before the Bank is accepted: " + ", ".join(candidates[:8])
        )

    # 2) Locally lock the accepted map and validate/render the Bank content that
    # arrived in the SAME AI result.
    state["map_audit"] = "PASS"
    skeleton = _prepare_internal_bank(ctx, root, state)
    bank_records = [dict(x) for x in combined["bank_records"]]
    _normalize_bank_graph_modes(bank_records)
    bank_ai = {
        "schema": legacy.BANK_AI_SCHEMA,
        "run_id": state["bank_run_id"],
        "course": ctx.course,
        "unit": ctx.unit,
        "accepted_map_fingerprint": skeleton["accepted_map_fingerprint"],
        "records": bank_records,
        "wtc_stimuli": combined.get("wtc_stimuli", []),
    }

    internal_transfer = root / "_internal_transfer"
    if internal_transfer.exists():
        shutil.rmtree(internal_transfer)
    old_legacy_version = legacy.PILOT_VERSION
    legacy.PILOT_VERSION = PILOT_VERSION
    try:
        build = legacy._finish_bank(ctx, root, bank_ai, internal_transfer)
    finally:
        legacy.PILOT_VERSION = old_legacy_version
    staged_bank = Path(build["staged_bank"])
    graph_audit = _extra_graph_audit(root)
    _write_json(staged_bank / "V08_GRAPH_MODE_AUDIT.json", graph_audit)
    if graph_audit["status"] != "PASS":
        raise ValueError(
            "Registered graph-tool routing audit failed for standard algebra coordinate planes: "
            + ", ".join(graph_audit["standard_coordinate_mode_mismatches"][:8])
        )

    final_zip = _final_transfer_v08(
        ctx,
        staged_bank,
        transfer_root,
        state.get("system_head"),
        state.get("course_head"),
    )
    state.update({
        "stage": "complete",
        "ai_result": str(result_path),
        "map_audit": "PASS",
        "bank_audit": "PASS",
        "transfer_zip": str(final_zip),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    _write_state(root, state)
    _archive_completed_exchange(ai_exchange, ctx, str(state.get("pipeline_id")))
    return {
        "status": "PASS",
        "stage": "complete",
        "map_audit": "PASS",
        "bank_audit": "PASS",
        "finished_task_count": build.get("finished_task_count"),
        "seed_count": build.get("seed_count"),
        "graph_asset_count": build.get("graph_asset_count"),
        "graph_render_modes": graph_audit.get("graph_render_modes"),
        "transfer_zip": str(final_zip),
        "ai_round_trips": 1,
        "canonical_repo_modified": False,
    }
