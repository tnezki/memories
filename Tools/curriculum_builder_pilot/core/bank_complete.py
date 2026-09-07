from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict

from .authorities import ProjectContext
from .fs import read_json, sha256_file
from .map_audit import audit_bank_map


SCHEMA = "curriculum-builder-complete-bank-skeleton/0.5"
AI_CONTENT_SCHEMA = "curriculum-builder-ai-bank-content/0.5"


def _required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Missing required Complete Bank map field: {label}")
    return text


def _load_manifest(source_map: Path) -> dict:
    manifest = read_json(source_map / "MAP_MANIFEST.json")
    if str(manifest.get("status", "")).upper() != "PASS":
        raise ValueError("Accepted Bank Map must have MAP_MANIFEST.status=PASS")
    return manifest


def _slice_path(source_map: Path, manifest: dict, key: str, fallback: str) -> Path:
    slices = manifest.get("slices") if isinstance(manifest, dict) else None
    if isinstance(slices, dict):
        rel = slices.get(key)
        if isinstance(rel, str) and rel.strip():
            return source_map / rel
    return source_map / fallback


def _verify_manifest_hashes(source_map: Path, manifest: dict) -> None:
    declared = manifest.get("files")
    if not isinstance(declared, list):
        raise ValueError("MAP_MANIFEST.files[] is required for Complete Bank entry gate")
    checked = 0
    for entry in declared:
        if not isinstance(entry, dict):
            continue
        rel = entry.get("path")
        expected = entry.get("sha256")
        if not rel or not expected:
            continue
        checked += 1
        path = source_map / str(rel)
        if not path.is_file():
            raise ValueError(f"Accepted Bank Map declared file is missing: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"Accepted Bank Map hash mismatch: {rel}")
    if checked == 0:
        raise ValueError("Accepted Bank Map manifest exposed no verifiable SHA-256 entries")


def _locked_record(rec: dict) -> dict:
    rid = _required_text(rec.get("design_slot_id"), "design_slot_id")
    destination = _required_text(rec.get("destination"), f"{rid}.destination")
    required = {
        "design_slot_id": rid,
        "destination": destination,
        "unit": rec.get("unit"),
        "section": rec.get("section"),
        "stage": rec.get("stage"),
        "target": rec.get("target"),
        "mastery_goal": rec.get("mastery_goal"),
        "primary_i_can": rec.get("primary_i_can"),
        "supporting_i_cans": rec.get("supporting_i_cans", []),
        "evidence_job": rec.get("evidence_job"),
        "student_action": rec.get("student_action"),
        "question_structure_id": rec.get("question_structure_id"),
        "response_mode": rec.get("response_mode"),
        "representation_mode": rec.get("representation_mode"),
        "representation_need": rec.get("representation_need"),
        "representation_routes": rec.get("representation_routes", []),
        "difficulty_intent": rec.get("difficulty_intent"),
        "variation_axes": rec.get("variation_axes", {}),
        "security_role": rec.get("security_role"),
        "slot_role": rec.get("slot_role"),
    }
    # Preserve destination-specific identity needed downstream without asking AI to recreate it.
    for key in (
        "form", "form_id", "question_number", "reassessment_of", "carry_forward_from",
        "shared_stimulus_id", "depends_on", "part_label", "wtc_id", "family_id",
    ):
        if key in rec:
            required[key] = rec.get(key)
    return required


def build_complete_bank_skeleton(ctx: ProjectContext, run_dir: Path) -> Dict[str, object]:
    """Build the local, immutable Complete Bank authoring skeleton from the accepted map.

    This does not author student questions. It locks record identity/counts/routing so
    the AI handoff can contain only semantic/content authoring work.
    """
    local_audit = audit_bank_map(ctx)
    if local_audit.get("mechanical_shape_status") != "PASS":
        raise ValueError("Complete Bank blocked: local Bank Map mechanical audit is not PASS")
    semantic_count = int(local_audit.get("facts", {}).get("semantic_candidate_count", 0) or 0)
    if semantic_count:
        raise ValueError(
            f"Complete Bank blocked: accepted Bank Map still has {semantic_count} unresolved semantic candidate(s)"
        )

    source_map = ctx.course_dir / f"banks/unit{ctx.unit}/source_map"
    manifest = _load_manifest(source_map)
    _verify_manifest_hashes(source_map, manifest)
    fingerprint = _required_text(manifest.get("map_fingerprint"), "MAP_MANIFEST.map_fingerprint")

    question_design_path = _slice_path(
        source_map, manifest, "question_design", f"unit{ctx.unit}_question_design_map.json"
    )
    question_design = read_json(question_design_path)
    records = question_design.get("records") if isinstance(question_design, dict) else None
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError(f"Question design map must contain records[] objects: {question_design_path}")

    locked = [_locked_record(r) for r in records]
    ids = [r["design_slot_id"] for r in locked]
    if len(ids) != len(set(ids)):
        dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
        raise ValueError(f"Duplicate Complete Bank design_slot_id values: {dupes[:10]}")

    expected_count = ((question_design.get("question_design") or {}).get("finished_task_slot_count")
                      if isinstance(question_design, dict) else None)
    if isinstance(expected_count, int) and expected_count != len(locked):
        raise ValueError(f"Question design count mismatch: expected {expected_count}; found {len(locked)}")

    inventory_path = _slice_path(source_map, manifest, "inventory", "bank_inventory_map.json")
    inventory = read_json(inventory_path)
    inventory_total = inventory.get("finished_task_slot_total") if isinstance(inventory, dict) else None
    if isinstance(inventory_total, int) and inventory_total != len(locked):
        raise ValueError(f"Bank inventory count mismatch: expected {inventory_total}; found {len(locked)}")

    seed_path = _slice_path(source_map, manifest, "Seeds", "seed_map.json")
    seed_map = read_json(seed_path)
    seeds = seed_map.get("records") if isinstance(seed_map, dict) else None
    if not isinstance(seeds, list) or any(not isinstance(s, dict) for s in seeds):
        raise ValueError(f"Seed map must contain records[] objects: {seed_path}")

    destination_counts = dict(sorted(Counter(r["destination"] for r in locked).items()))
    payload = {
        "schema": SCHEMA,
        "course": ctx.course,
        "unit": ctx.unit,
        "accepted_map_fingerprint": fingerprint,
        "record_count": len(locked),
        "destination_counts": destination_counts,
        "seed_count": len(seeds),
        "immutable_rule": (
            "All locked_map fields and record IDs are local mechanical facts. AI may author only the allowed output fields."
        ),
        "allowed_ai_fields": [
            "design_slot_id",
            "prompt_text",
            "prompt_blocks",
            "answer_text",
            "solution_text",
            "choices",
            "representation_data",
            "instantiation_summary",
        ],
        "records": [
            {
                "design_slot_id": rec["design_slot_id"],
                "locked_map": rec,
                "ai_output_schema": {
                    "design_slot_id": rec["design_slot_id"],
                    "prompt_text": "required",
                    "prompt_blocks": "required list of typed content blocks",
                    "answer_text": "required",
                    "solution_text": "required",
                    "choices": "required only for selected_response; otherwise []",
                    "representation_data": "structured data needed to render mapped representation; {} when none",
                    "instantiation_summary": "brief statement of values/context/variation actually used",
                },
            }
            for rec in locked
        ],
        "locked_seeds": seeds,
        "ai_result_contract": {
            "filename": "AI_BANK_CONTENT.json",
            "schema": AI_CONTENT_SCHEMA,
            "required_top_level": [
                "schema", "run_id", "course", "unit", "accepted_map_fingerprint", "records", "wtc_stimuli"
            ],
            "record_count": len(locked),
            "record_ids_exact": ids,
        },
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "EXPECTED_BANK_RECORDS.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    facts = {
        "schema": "curriculum-builder-complete-bank-locked-facts/0.5",
        "course": ctx.course,
        "unit": ctx.unit,
        "accepted_map_fingerprint": fingerprint,
        "record_count": len(locked),
        "destination_counts": destination_counts,
        "seed_count": len(seeds),
        "mechanical_map_audit": "PASS",
        "semantic_candidates": 0,
        "canonical_repo_modified": False,
    }
    facts_path = run_dir / "LOCKED_BANK_FACTS.json"
    facts_path.write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")

    return {
        "path": str(out),
        "facts_path": str(facts_path),
        "record_count": len(locked),
        "destination_counts": destination_counts,
        "seed_count": len(seeds),
        "accepted_map_fingerprint": fingerprint,
    }
