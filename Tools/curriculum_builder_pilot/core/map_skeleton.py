from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .authorities import ProjectContext, resolve_common
from .fs import read_json


def _unit_entry(index: Dict[str, Any], unit: int) -> Dict[str, Any]:
    for entry in index.get("units", []) if isinstance(index.get("units"), list) else []:
        if isinstance(entry, dict) and entry.get("unit") == unit:
            return entry
    raise ValueError(f"Unit {unit} not found in assessment plan index")


def build_mechanical_map_skeleton(ctx: ProjectContext, staging_root: Path) -> Dict[str, Any]:
    common = resolve_common(ctx)
    resource_root = common["resource_root"]
    profile = read_json(resource_root / "profiles/bank_course_profile.json")
    index = read_json(resource_root / "assessment_plans/indexes/assessment_plan_index.json")
    unit = _unit_entry(index, ctx.unit)
    sections: List[Dict[str, Any]] = [s for s in unit.get("sections", []) if isinstance(s, dict)]
    if not sections:
        raise ValueError("No sections found for requested Unit")

    p1 = profile["bank_inventory"]["practice_1"]
    p1_stage = p1["stage_counts"]
    wtc = profile["bank_inventory"]["wtc"]
    forms = profile["bank_inventory"]["summative"]["forms"]
    mastery_ids = []
    for section in sections:
        gid = section.get("mastery_goal_id")
        if gid and gid not in mastery_ids:
            mastery_ids.append(gid)
    items_per_form = max(1, len(mastery_ids) * 2)

    slots: List[Dict[str, Any]] = []
    for section in sections:
        sec = str(section["section_id"])
        for q in range(1, 5):
            slots.append({"design_slot_id": f"U{ctx.unit}-S{sec}-EXIT-Q{q}", "destination": "Exit", "section": sec, "locked": True})
        for stage in ("Intro", "Review", "Mastery"):
            for n in range(1, int(p1_stage[stage]) + 1):
                slots.append({
                    "design_slot_id": f"U{ctx.unit}-S{sec}-P1-{stage.upper()}-{n:02d}",
                    "destination": "Practice 1", "section": sec, "stage": stage, "locked": True,
                })
        for label in ("A", "B", "C", "D"):
            slots.append({"design_slot_id": f"U{ctx.unit}-S{sec}-WTC-{label}", "destination": "WTC", "section": sec, "part": f"Part {label}", "locked": True})

    for form in forms:
        for q in range(1, items_per_form + 1):
            slots.append({"design_slot_id": f"U{ctx.unit}-SUM-{form}-Q{q:02d}", "destination": "Summative", "form": form, "locked": True})

    seed_candidates = (profile.get("approved_seed_candidates") or {}).get(str(ctx.unit), [])
    seeds = [
        {"seed_id": x.get("seed_id"), "title": x.get("title"), "locked": True}
        for x in seed_candidates if isinstance(x, dict)
    ]

    counts: Dict[str, int] = {}
    for slot in slots:
        counts[slot["destination"]] = counts.get(slot["destination"], 0) + 1

    unresolved = {
        "purpose": "Only semantic fields that require authoring/judgment. Mechanical slot identity/counts are locked.",
        "fields": [
            "stage/goal/I Can routing where not directly determined by the exact authority row",
            "evidence_job", "student_action", "question_structure_id", "response_mode",
            "representation_mode/need/routes", "difficulty_intent", "variation_axes",
            "WTC shared stimulus design and real dependency decisions",
            "Summative secure family/parallel semantic design",
        ],
    }

    skeleton = {
        "schema": "curriculum-builder-bank-map-skeleton/0.2",
        "course": ctx.course,
        "unit": ctx.unit,
        "unit_title": unit.get("title"),
        "status": "MECHANICAL_SKELETON_READY",
        "locked_contract": {
            "sections": [str(s["section_id"]) for s in sections],
            "practice_questions_per_section": p1["count_per_section"],
            "practice_stage_counts": p1_stage,
            "exit_questions_per_section": 4,
            "wtc_parts_per_section": wtc["part_count"],
            "summative_forms": forms,
            "current_mastery_goal_ids": mastery_ids,
            "summative_items_per_form": items_per_form,
            "approved_seed_count": len(seeds),
        },
        "slot_count": len(slots),
        "destination_counts": counts,
        "slots": slots,
        "seeds": seeds,
        "unresolved_semantic_work": unresolved,
        "ai_boundary": "AI may fill unresolved semantic fields but may not add/drop/rename locked slots or alter locked counts unless a current authority defect is explicitly returned to the teacher.",
    }

    run_dir = staging_root / "skeletons" / f"algebra_1_u{ctx.unit}_bank_map"
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "MAP_BUILD_SKELETON.json"
    path.write_text(json.dumps(skeleton, indent=2) + "\n", encoding="utf-8")
    return {"skeleton": skeleton, "path": str(path)}
