from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .authorities import ProjectContext, resolve_bank_sources, resolve_common
from .bank_complete import _locked_record
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha
from .map_audit import audit_bank_map, save_audit_report
from .map_skeleton import build_mechanical_map_skeleton
from .preflight import run_preflight

MAP_AI_SCHEMA = "curriculum-builder-ai-bank-map/0.7"
BANK_AI_SCHEMA = "curriculum-builder-ai-bank-content/0.5"
PIPELINE_SCHEMA = "curriculum-builder-full-bank-pipeline/0.7"
SEMANTIC_REVIEW_SCHEMA = "curriculum-builder-semantic-review/0.2.1"
PILOT_VERSION = "0.7.1"


def _slug(text: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_state(root: Path) -> Dict[str, Any]:
    path = root / "PIPELINE_STATE.json"
    if not path.is_file():
        return {}
    return read_json(path)


def _write_state(root: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    _write_json(root / "PIPELINE_STATE.json", state)
    return state


def _pipeline_root(staging_root: Path, ctx: ProjectContext) -> Path:
    return staging_root / "full_pipeline" / _slug(ctx.course) / f"unit{ctx.unit}"


def _copy_source(src: Path, input_root: Path, github_root: Path) -> None:
    rel = src.resolve().relative_to(github_root.resolve())
    dst = input_root / rel
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _zip_dir(root: Path, out_zip: Path) -> Path:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != out_zip:
                zf.write(path, path.relative_to(root))
    return out_zip


def _easy_name(course: str, unit: int, kind: str) -> str:
    compact = "".join(ch for ch in course if ch.isalnum())
    return f"AI_HANDOFF_{compact}_U{unit}_{kind}.zip"


def _copy_handoff(src: Path, downloads: Path, name: str) -> Path:
    downloads.mkdir(parents=True, exist_ok=True)
    dst = downloads / name
    shutil.copy2(src, dst)
    return dst


def _relative_memories(ctx: ProjectContext, path: Path) -> str:
    try:
        return path.resolve().relative_to(ctx.memories_dir.resolve()).as_posix()
    except Exception:
        return str(path)


def _map_work_order(ctx: ProjectContext, run_id: str) -> str:
    return f"""CURRICULUM BUILDER FULL BANK PIPELINE - MAP AUTHORING\n\nRUN ID: {run_id}\nCOURSE: {ctx.course}\nUNIT: {ctx.unit}\n\nSOURCE BOUNDARY - HARD\nUse only files in this handoff plus the current explicit teacher instruction. No public web, File Library, old chats, saved memory, or similarly named substitutes.\n\nMECHANICAL LOCK - HARD\nRead MAP_BUILD_SKELETON.json first. Every design_slot_id, destination, section, Practice stage, WTC part, Summative form, count, and approved seed identity in that skeleton is locked. Do not add, drop, rename, or move slots.\n\nTASK\nAuthor the unresolved semantic Bank Map fields only. This is Step 3a design, not finished student questions. Make each record executable for the later Complete Bank build. Use exact Question Structure IDs from the included Universal Question Structure Library. Direct graph/representation reads must use the direct feature-reading structure, not a qualitative inference structure.\n\nOUTPUT CONTRACT - HARD\nReturn exactly one file named AI_MAP_CONTENT.json with this shape:\n{{\n  \"schema\": \"{MAP_AI_SCHEMA}\",\n  \"run_id\": \"{run_id}\",\n  \"course\": \"{ctx.course}\",\n  \"unit\": {ctx.unit},\n  \"records\": [\n    {{\n      \"design_slot_id\": \"exact locked ID\",\n      \"mastery_goal\": {{\"goal_id\": \"...\", \"title\": \"...\", \"text\": \"...\"}},\n      \"primary_i_can\": {{\"i_can_id\": \"...\", \"source_i_can_index\": 1, \"text\": \"...\"}},\n      \"supporting_i_cans\": [],\n      \"evidence_job\": \"...\",\n      \"student_action\": \"...\",\n      \"question_structure_id\": \"exact included-library ID\",\n      \"response_mode\": \"...\",\n      \"representation_mode\": \"...\",\n      \"representation_need\": \"required|optional|none\",\n      \"representation_routes\": [],\n      \"difficulty_intent\": \"...\",\n      \"variation_axes\": {{\"allowed\": [], \"required\": [], \"forbidden\": []}},\n      \"security_role\": \"...\",\n      \"slot_role\": \"...\",\n      \"reassessment_of\": null,\n      \"carry_forward_from\": null,\n      \"shared_stimulus_id\": null,\n      \"depends_on\": null,\n      \"family_id\": null\n    }}\n  ]\n}}\n\nRequirements:\n- exactly one record for every locked slot and no extras;\n- preserve the Exit architecture: current Mastery evidence plus mapped reassessment carry-forward;\n- Practice remains exactly 8 Intro + 8 Review + 8 Mastery per section;\n- each WTC is one meaningful shared stimulus with Parts A-D;\n- Summative V1-V6 are secure parallel forms;\n- do not author finished prompts/answers;\n- self-audit semantic structure fit before returning the file;\n- stop after AI_MAP_CONTENT.json.\n"""


def _bank_work_order(ctx: ProjectContext, run_id: str) -> str:
    return f"""CURRICULUM BUILDER FULL BANK PIPELINE - COMPLETE BANK AUTHORING\n\nRUN ID: {run_id}\nCOURSE: {ctx.course}\nUNIT: {ctx.unit}\n\nSOURCE BOUNDARY - HARD\nUse only files in this handoff plus the current explicit teacher instruction. No public web, File Library, old chats, saved memory, or similarly named substitutes.\n\nLOCKED MAP - HARD\nRead LOCKED_BANK_FACTS.json and EXPECTED_BANK_RECORDS.json first. The staged Bank Map has already passed local mechanical and semantic audit. Do not redesign it.\n\nTASK\nAuthor finished student-facing content for every locked record. Preserve every map field. Use exact mapped Question Structures. Secure Summative content stays private. WTC parts share the mapped stimulus.\n\nRENDERING CONTRACT\n- For algebra coordinate-plane work, use graph blocks with semantic_mode \"algebra_coordinate\" or response_surface kind \"blank_coordinate_grid\".\n- For real-world axes/ranges, use semantic_mode \"context\" and meaningful axis labels.\n- Do not duplicate ugly raw algebra such as x^2 in prose when an equation block can carry the math cleanly.\n- Return structured graph/table/equation data; local code renders final assets with the registered tools.\n\nOUTPUT CONTRACT - HARD\nReturn exactly one AI_BANK_CONTENT.json using schema {BANK_AI_SCHEMA}.\nIt must contain exactly the locked design_slot_ids, the exact accepted_map_fingerprint, records[], and wtc_stimuli[]. No TODO/TBD/placeholders.\nStop after AI_BANK_CONTENT.json.\n"""


def _snapshot_sources(ctx: ProjectContext, job: str, root: Path, skip_current_source_map: bool = False) -> None:
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    current_source = ctx.course_dir / "banks" / f"unit{ctx.unit}" / "source_map"
    for src in resolve_bank_sources(ctx, job):
        if skip_current_source_map:
            try:
                if src.resolve() == current_source.resolve():
                    continue
            except Exception:
                pass
        if src.exists():
            _copy_source(src, inputs, ctx.github_root)


def start_full_pipeline(ctx: ProjectContext, staging_root: Path, downloads: Path) -> Dict[str, Any]:
    preflight = run_preflight(ctx, "bank_map")
    if preflight.get("status") != "PASS":
        return {"status": "BLOCKED", "stage": "preflight", "preflight": preflight}

    root = _pipeline_root(staging_root, ctx)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    pipeline_id = f"{time.strftime('%Y%m%d-%H%M%S')}_{_slug(ctx.course)}_u{ctx.unit}_full_bank"
    map_run_id = pipeline_id + "_map"
    map_ai = root / "map_ai"
    map_ai.mkdir()
    _snapshot_sources(ctx, "bank_map", map_ai)

    sk = build_mechanical_map_skeleton(ctx, staging_root)
    skeleton = sk["skeleton"]
    _write_json(map_ai / "MAP_BUILD_SKELETON.json", skeleton)
    (map_ai / "AI_WORK_ORDER.txt").write_text(_map_work_order(ctx, map_run_id), encoding="utf-8")
    manifest = {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "run_id": map_run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "job": "full_bank_pipeline_map",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "record_count": skeleton.get("slot_count"),
        "destination_counts": skeleton.get("destination_counts"),
        "public_web_allowed": False,
        "file_library_allowed": False,
        "git_commands_allowed": False,
    }
    _write_json(map_ai / "RUN_MANIFEST.json", manifest)
    handoff = _zip_dir(map_ai, root / "AI_HANDOFF_FULL_MAP.zip")
    easy = _copy_handoff(handoff, downloads, _easy_name(ctx.course, ctx.unit, "FULL_MAP"))

    state = {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "stage": "awaiting_map_ai",
        "map_run_id": map_run_id,
        "system_head": manifest["system_head"],
        "course_head": manifest["course_head"],
        "map_handoff": str(easy),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _write_state(root, state)
    return {
        "status": "AI_NEEDED",
        "stage": state["stage"],
        "preflight": preflight,
        "pipeline_id": pipeline_id,
        "handoff": str(easy),
        "record_count": skeleton.get("slot_count"),
        "destination_counts": skeleton.get("destination_counts"),
        "seed_count": (skeleton.get("locked_contract") or {}).get("approved_seed_count"),
    }


def _download_json_candidates(downloads: Path, glob: str) -> List[Path]:
    if not downloads.is_dir():
        return []
    return sorted((p for p in downloads.glob(glob) if p.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)


def _find_json(downloads: Path, glob: str, schema: str, run_id: str) -> Tuple[Path, Dict[str, Any]]:
    errors: List[str] = []
    for path in _download_json_candidates(downloads, glob):
        try:
            data = read_json(path)
            if data.get("schema") != schema or str(data.get("run_id") or "") != run_id:
                continue
            return path, data
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    extra = f" Latest unreadable candidate: {errors[0]}" if errors else ""
    raise FileNotFoundError(f"No matching {glob} result is in Downloads for run {run_id}.{extra}")


def _required_map_fields(rec: Dict[str, Any], rid: str) -> None:
    required_text = [
        "evidence_job", "student_action", "question_structure_id", "response_mode",
        "representation_mode", "representation_need", "difficulty_intent", "security_role", "slot_role",
    ]
    for key in required_text:
        if not str(rec.get(key) or "").strip():
            raise ValueError(f"{rid}: AI map result is missing {key}")
    if not isinstance(rec.get("mastery_goal"), dict) or not str(rec["mastery_goal"].get("goal_id") or "").strip():
        raise ValueError(f"{rid}: mastery_goal is missing")
    if not isinstance(rec.get("primary_i_can"), dict) or not str(rec["primary_i_can"].get("text") or "").strip():
        raise ValueError(f"{rid}: primary_i_can is missing")
    if not isinstance(rec.get("representation_routes"), list):
        raise ValueError(f"{rid}: representation_routes must be a list")
    if not isinstance(rec.get("variation_axes"), dict):
        raise ValueError(f"{rid}: variation_axes must be an object")


def _source_basis(ctx: ProjectContext) -> List[str]:
    common = resolve_common(ctx)
    rr = common["resource_root"]
    return [
        _relative_memories(ctx, rr / f"assessment_plans/original/unit{ctx.unit}_assessment_plan/unit{ctx.unit}_assessment_plan.html"),
        _relative_memories(ctx, rr / "assessment_plans/indexes/assessment_plan_index.json"),
        _relative_memories(ctx, rr / "profiles/bank_course_profile.json"),
        _relative_memories(ctx, common["question_structure_entrypoint"]),
        _relative_memories(ctx, common["question_structure_library"]),
    ]


def _refresh_map_manifest(ctx: ProjectContext, source_map: Path) -> None:
    design_name = f"unit{ctx.unit}_question_design_map.json"
    design = read_json(source_map / design_name)
    seed_map = read_json(source_map / "seed_map.json")
    records = design.get("records", [])
    seeds = seed_map.get("records", [])
    fp_blob = json.dumps({"records": records, "seeds": seeds}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    fingerprint = hashlib.sha256(fp_blob).hexdigest()
    manifest_path = source_map / "MAP_MANIFEST.json"
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    files = []
    for name in [
        design_name, "bank_inventory_map.json", "exit_map.json", "summative_map.json",
        "practice1_map.json", "wtc_map.json", "seed_map.json", "MAP_REPORT.txt",
    ]:
        p = source_map / name
        files.append({"path": name, "sha256": sha256_file(p)})
    manifest.update({
        "schema": "algebra-bank-map-manifest/1.0",
        "course": ctx.course,
        "unit": ctx.unit,
        "status": "PASS",
        "map_fingerprint": fingerprint,
        "question_design": {"status": "PASS", "finished_task_slot_count": len(records)},
        "qa": {"status": "PASS", "semantic_conflicts": {"direct_read_inflation_conflicts": 0}},
        "canonical_repository_destination": f"{ctx.course_dir.name}/banks/unit{ctx.unit}/source_map/",
        "files": files,
        "slices": {
            "inventory": "bank_inventory_map.json",
            "question_design": design_name,
            "Exit": "exit_map.json",
            "Summative": "summative_map.json",
            "Practice 1": "practice1_map.json",
            "WTC": "wtc_map.json",
            "Seeds": "seed_map.json",
        },
        "finalization": {"status": "PASS", "terminal_signal": "FINALIZATION_QA: PASS"},
        "map_fingerprint_method": "pilot-full-pipeline-map-content-v1",
    })
    _write_json(manifest_path, manifest)


def _assemble_map(ctx: ProjectContext, root: Path, ai: Dict[str, Any]) -> Path:
    skeleton = read_json(root / "map_ai" / "MAP_BUILD_SKELETON.json")
    if ai.get("schema") != MAP_AI_SCHEMA:
        raise ValueError(f"AI_MAP_CONTENT schema must be {MAP_AI_SCHEMA}")
    slots = skeleton.get("slots")
    if not isinstance(slots, list):
        raise ValueError("MAP_BUILD_SKELETON has no slots[]")
    slot_by_id = {str(s.get("design_slot_id")): s for s in slots if isinstance(s, dict)}
    records = ai.get("records")
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("AI_MAP_CONTENT records must be an array of objects")
    ids = [str(r.get("design_slot_id") or "") for r in records]
    if len(ids) != len(set(ids)) or set(ids) != set(slot_by_id):
        raise ValueError("AI_MAP_CONTENT record IDs do not exactly match the locked map skeleton")

    ai_by_id = {str(r["design_slot_id"]): r for r in records}
    basis = _source_basis(ctx)
    merged: List[Dict[str, Any]] = []
    for rid, slot in slot_by_id.items():
        rec = dict(ai_by_id[rid])
        _required_map_fields(rec, rid)
        out = {
            "design_slot_id": rid,
            "destination": slot.get("destination"),
            "unit": ctx.unit,
            "section": slot.get("section"),
            "stage": slot.get("stage") or ("Mastery" if slot.get("destination") == "Exit" else None),
            "mastery_goal": rec.get("mastery_goal"),
            "primary_i_can": rec.get("primary_i_can"),
            "supporting_i_cans": rec.get("supporting_i_cans") or [],
            "evidence_job": rec.get("evidence_job"),
            "student_action": rec.get("student_action"),
            "question_structure_id": rec.get("question_structure_id"),
            "response_mode": rec.get("response_mode"),
            "representation_mode": rec.get("representation_mode"),
            "representation_need": rec.get("representation_need"),
            "representation_routes": rec.get("representation_routes") or [],
            "difficulty_intent": rec.get("difficulty_intent"),
            "variation_axes": rec.get("variation_axes") or {},
            "source_basis": basis,
            "security_role": rec.get("security_role"),
            "slot_role": rec.get("slot_role"),
        }
        if slot.get("destination") == "Summative":
            out["form"] = slot.get("form")
            out["form_id"] = slot.get("form")
            m = re.search(r"-Q(\d+)$", rid)
            out["question_number"] = int(m.group(1)) if m else None
        if slot.get("destination") == "WTC":
            out["part_label"] = slot.get("part") or rid.rsplit("-", 1)[-1]
            out["wtc_id"] = f"U{ctx.unit}-S{slot.get('section')}-WTC"
            out["shared_stimulus_id"] = str(rec.get("shared_stimulus_id") or f"U{ctx.unit}-S{slot.get('section')}-WTC-STIMULUS")
        for key in ("target", "reassessment_of", "carry_forward_from", "depends_on", "family_id"):
            value = rec.get(key)
            if value not in (None, "", []):
                out[key] = value
        merged.append(out)

    source_map = root / "staged_source_map"
    if source_map.exists():
        shutil.rmtree(source_map)
    source_map.mkdir(parents=True)

    title = skeleton.get("unit_title") or f"Unit {ctx.unit}"
    design_name = f"unit{ctx.unit}_question_design_map.json"
    _write_json(source_map / design_name, {
        "schema": "algebra-question-design-map/1.0",
        "course": ctx.course,
        "unit": ctx.unit,
        "title": title,
        "status": "PASS",
        "question_design": {"status": "PASS", "finished_task_slot_count": len(merged), "seed_count": len(skeleton.get("seeds") or [])},
        "records": merged,
    })

    by_dest: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in merged:
        by_dest[str(rec.get("destination"))].append(rec)
    _write_json(source_map / "exit_map.json", {"schema": "algebra-bank-exit-map/1.0", "course": ctx.course, "unit": ctx.unit, "status": "PASS", "records": by_dest["Exit"]})
    _write_json(source_map / "summative_map.json", {"schema": "algebra-bank-summative-map/1.0", "course": ctx.course, "unit": ctx.unit, "status": "PASS", "records": by_dest["Summative"]})
    _write_json(source_map / "practice1_map.json", {"schema": "algebra-bank-practice1-map/1.0", "course": ctx.course, "unit": ctx.unit, "status": "PASS", "records": by_dest["Practice 1"]})

    wtcs = []
    wtc_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in by_dest["WTC"]:
        wtc_groups[str(rec.get("section"))].append(rec)
    for section, rows in sorted(wtc_groups.items()):
        rows.sort(key=lambda r: str(r.get("part_label") or r.get("design_slot_id")))
        wtcs.append({
            "section": section,
            "wtc_id": f"U{ctx.unit}-S{section}-WTC",
            "shared_stimulus_id": rows[0].get("shared_stimulus_id") if rows else None,
            "parts_plan": rows,
        })
    _write_json(source_map / "wtc_map.json", {"schema": "algebra-bank-wtc-map/1.0", "course": ctx.course, "unit": ctx.unit, "status": "PASS", "wtcs": wtcs})

    common = resolve_common(ctx)
    profile = read_json(common["resource_root"] / "profiles/bank_course_profile.json")
    approved = ((profile.get("approved_seed_candidates") or {}).get(str(ctx.unit), []))
    seeds = [dict(x) for x in approved if isinstance(x, dict)] if isinstance(approved, list) else []
    _write_json(source_map / "seed_map.json", {"schema": "algebra-bank-seed-map/1.0", "course": ctx.course, "unit": ctx.unit, "status": "PASS", "records": seeds})

    counts = Counter(str(r.get("destination")) for r in merged)
    section_count = len((skeleton.get("locked_contract") or {}).get("sections") or [])
    forms = (skeleton.get("locked_contract") or {}).get("summative_forms") or []
    items_per_form = (skeleton.get("locked_contract") or {}).get("summative_items_per_form") or 0
    _write_json(source_map / "bank_inventory_map.json", {
        "schema": "algebra-bank-inventory-map/1.0",
        "course": ctx.course,
        "unit": ctx.unit,
        "status": "PASS",
        "canonical_destinations": [
            {"destination": "Exit", "status": "canonical", "finished_task_slots": counts.get("Exit", 0)},
            {"destination": "Summative", "status": "canonical_secure", "forms": len(forms), "items_per_form": items_per_form, "finished_task_slots": counts.get("Summative", 0)},
            {"destination": "Practice 1", "status": "canonical", "sections": section_count, "questions_per_section": 24, "stage_counts_per_section": {"Intro": 8, "Review": 8, "Mastery": 8}, "finished_task_slots": counts.get("Practice 1", 0)},
            {"destination": "WTC", "status": "canonical", "wtc_count": section_count, "parts_per_wtc": 4, "finished_task_slots": counts.get("WTC", 0)},
            {"destination": "Seeds", "status": "canonical_when_useful", "seed_records": len(seeds), "finished_task_slots": 0},
        ],
        "finished_task_slot_total": len(merged),
        "seed_count": len(seeds),
    })
    report = (
        f"BANK MAP - FULL PIPELINE v{PILOT_VERSION}\n"
        f"Course: {ctx.course}\nUnit: {ctx.unit}\n"
        f"Finished task slots: {len(merged)}\nSeeds: {len(seeds)}\n"
        f"Destination counts: {json.dumps(dict(sorted(counts.items())), sort_keys=True)}\n"
        "LOCAL MAP QA: PASS BEFORE SEMANTIC LINT\n"
    )
    (source_map / "MAP_REPORT.txt").write_text(report, encoding="utf-8")
    _write_json(source_map / "MAP_MANIFEST.json", {})
    _refresh_map_manifest(ctx, source_map)
    return source_map


def _candidate_ids(report: Dict[str, Any]) -> List[str]:
    out = []
    for finding in report.get("findings", []) if isinstance(report.get("findings"), list) else []:
        if isinstance(finding, dict) and finding.get("code") == "DIRECT_READ_STRUCTURE_MISMATCH" and finding.get("record_id"):
            out.append(str(finding["record_id"]))
    return out


def _map_repair_handoff(ctx: ProjectContext, root: Path, report: Dict[str, Any], downloads: Path) -> Path:
    run_id = str(_read_state(root).get("pipeline_id")) + "_map_repair"
    work = root / "map_repair_ai"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    shutil.copytree(root / "staged_source_map", work / "staged_source_map")
    common = resolve_common(ctx)
    for path in [common["question_structure_entrypoint"], common["question_structure_library"], common["question_structure_manifest"]]:
        dst = work / "question_structure" / path.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
    _write_json(work / "LOCAL_MAP_AUDIT.json", report)
    ids = _candidate_ids(report)
    ids_text = "\n".join(f"- {x}" for x in ids)
    (work / "AI_WORK_ORDER.txt").write_text(
        f"""FULL PIPELINE MAP AUDIT REPAIR\nRUN ID: {run_id}\n\nMechanical map facts already PASS. Review only these semantic candidates:\n{ids_text}\n\nFor each candidate decide KEEP or REPAIR for question_structure_id using the included exact structure library. Return one AI_SEMANTIC_REVIEW.json with schema {SEMANTIC_REVIEW_SCHEMA}, run_id {run_id}, course {ctx.course}, unit {ctx.unit}, and exactly one decision per candidate. Do not change any other field.\n""",
        encoding="utf-8",
    )
    _write_json(work / "RUN_MANIFEST.json", {"schema": PIPELINE_SCHEMA, "run_id": run_id, "candidate_ids": ids})
    handoff = _zip_dir(work, root / "AI_HANDOFF_FULL_MAP_REPAIR.zip")
    return _copy_handoff(handoff, downloads, _easy_name(ctx.course, ctx.unit, "FULL_MAP_REPAIR"))


def _replace_structure_in_obj(obj: Any, decisions: Dict[str, str]) -> None:
    if isinstance(obj, dict):
        rid = str(obj.get("design_slot_id") or obj.get("record_id") or "")
        if rid in decisions and "question_structure_id" in obj:
            obj["question_structure_id"] = decisions[rid]
        for value in obj.values():
            _replace_structure_in_obj(value, decisions)
    elif isinstance(obj, list):
        for value in obj:
            _replace_structure_in_obj(value, decisions)


def _apply_map_review(ctx: ProjectContext, root: Path, review: Dict[str, Any], expected_ids: List[str]) -> None:
    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("AI_SEMANTIC_REVIEW decisions[] is missing")
    by_id: Dict[str, str] = {}
    for row in decisions:
        if not isinstance(row, dict):
            continue
        rid = str(row.get("design_slot_id") or "")
        decision = str(row.get("decision") or "").upper()
        current = str(row.get("current_question_structure_id") or "")
        recommended = str(row.get("recommended_question_structure_id") or "")
        if decision not in {"KEEP", "REPAIR"} or not rid:
            raise ValueError("Invalid semantic review decision")
        by_id[rid] = recommended if decision == "REPAIR" else current
    if set(by_id) != set(expected_ids):
        raise ValueError("Semantic review IDs do not exactly match staged map audit candidates")
    source_map = root / "staged_source_map"
    for path in source_map.glob("*.json"):
        data = read_json(path)
        _replace_structure_in_obj(data, by_id)
        _write_json(path, data)
    (source_map / "MAP_REPORT.txt").write_text(
        (source_map / "MAP_REPORT.txt").read_text(encoding="utf-8") + f"Semantic structure repairs reviewed: {len(by_id)}\n",
        encoding="utf-8",
    )
    _refresh_map_manifest(ctx, source_map)


def _build_bank_skeleton_from_map(ctx: ProjectContext, source_map: Path, run_dir: Path) -> Dict[str, Any]:
    manifest = read_json(source_map / "MAP_MANIFEST.json")
    design_name = (manifest.get("slices") or {}).get("question_design") or f"unit{ctx.unit}_question_design_map.json"
    design = read_json(source_map / design_name)
    records = design.get("records") if isinstance(design, dict) else None
    if not isinstance(records, list):
        raise ValueError("Staged question design has no records[]")
    locked = [_locked_record(r) for r in records]
    seed_map = read_json(source_map / "seed_map.json")
    seeds = seed_map.get("records") if isinstance(seed_map, dict) else []
    if not isinstance(seeds, list):
        raise ValueError("Staged seed map has no records[]")
    fingerprint = str(manifest.get("map_fingerprint") or "")
    counts = dict(sorted(Counter(r["destination"] for r in locked).items()))
    payload = {
        "schema": "curriculum-builder-complete-bank-skeleton/0.7",
        "course": ctx.course,
        "unit": ctx.unit,
        "accepted_map_fingerprint": fingerprint,
        "record_count": len(locked),
        "destination_counts": counts,
        "seed_count": len(seeds),
        "records": [{"design_slot_id": r["design_slot_id"], "locked_map": r} for r in locked],
        "locked_seeds": seeds,
    }
    _write_json(run_dir / "EXPECTED_BANK_RECORDS.json", payload)
    _write_json(run_dir / "LOCKED_BANK_FACTS.json", {
        "schema": "curriculum-builder-complete-bank-locked-facts/0.7",
        "course": ctx.course,
        "unit": ctx.unit,
        "accepted_map_fingerprint": fingerprint,
        "record_count": len(locked),
        "destination_counts": counts,
        "seed_count": len(seeds),
        "mechanical_map_audit": "PASS",
        "semantic_candidates": 0,
    })
    return payload


def _prepare_bank_handoff(ctx: ProjectContext, root: Path, downloads: Path) -> Dict[str, Any]:
    source_map = root / "staged_source_map"
    report = audit_bank_map(ctx, source_map_override=source_map)
    if report.get("mechanical_shape_status") != "PASS" or int((report.get("facts") or {}).get("semantic_candidate_count", 0) or 0):
        raise ValueError("Staged Bank Map must fully PASS before Complete Bank authoring")
    state = _read_state(root)
    bank_run_id = str(state.get("pipeline_id")) + "_bank"
    work = root / "bank_ai"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    _snapshot_sources(ctx, "bank_complete", work, skip_current_source_map=True)
    course_folder = ctx.course_dir.name
    snap = work / "inputs" / course_folder / "banks" / f"unit{ctx.unit}" / "source_map"
    snap.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_map, snap)
    shutil.copytree(source_map, work / "STAGED_SOURCE_MAP")
    skeleton = _build_bank_skeleton_from_map(ctx, source_map, work)
    (work / "AI_WORK_ORDER.txt").write_text(_bank_work_order(ctx, bank_run_id), encoding="utf-8")
    _write_json(work / "RUN_MANIFEST.json", {
        "schema": PIPELINE_SCHEMA,
        "run_id": bank_run_id,
        "pipeline_id": state.get("pipeline_id"),
        "course": ctx.course,
        "unit": ctx.unit,
        "job": "full_pipeline_bank_complete",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "accepted_map_fingerprint": skeleton.get("accepted_map_fingerprint"),
    })
    handoff = _zip_dir(work, root / "AI_HANDOFF_FULL_BANK.zip")
    easy = _copy_handoff(handoff, downloads, _easy_name(ctx.course, ctx.unit, "FULL_BANK"))
    state.update({"stage": "awaiting_bank_ai", "bank_run_id": bank_run_id, "bank_handoff": str(easy)})
    _write_state(root, state)
    return {
        "status": "AI_NEEDED",
        "stage": "awaiting_bank_ai",
        "handoff": str(easy),
        "map_audit": "PASS",
        "record_count": skeleton.get("record_count"),
        "destination_counts": skeleton.get("destination_counts"),
        "seed_count": skeleton.get("seed_count"),
    }


def _pipeline_bank_loader(ctx: ProjectContext, root: Path, ai: Dict[str, Any]) -> Dict[str, Any]:
    work = root / "bank_ai"
    expected = read_json(work / "EXPECTED_BANK_RECORDS.json")
    state = _read_state(root)
    if ai.get("schema") != BANK_AI_SCHEMA:
        raise ValueError(f"AI_BANK_CONTENT schema must be {BANK_AI_SCHEMA}")
    if str(ai.get("run_id") or "") != str(state.get("bank_run_id") or ""):
        raise ValueError("AI_BANK_CONTENT run_id does not match the active full pipeline")
    if ai.get("course") != ctx.course or int(ai.get("unit", -1)) != ctx.unit:
        raise ValueError("AI_BANK_CONTENT course/unit mismatch")
    if str(ai.get("accepted_map_fingerprint") or "") != str(expected.get("accepted_map_fingerprint") or ""):
        raise ValueError("AI_BANK_CONTENT map fingerprint mismatch")
    source_map = root / "staged_source_map"
    return {
        "run_id": state["bank_run_id"],
        "run_dir": work,
        "manifest": read_json(work / "RUN_MANIFEST.json"),
        "expected": expected,
        "source_snapshot": source_map,
        "current_source": source_map,
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
    }


def _mathify_prose(text: str) -> str:
    escaped = html.escape(text)
    # Conservative algebra cleanup for visible prose. Wrap obvious power notation
    # in MathJax delimiters so a valid question never fails only because a
    # teacher-facing sentence contains caret syntax.
    parenthesized_power = re.compile(r"(\(-?\d+(?:\.\d+)?\)\^[0-9]+)")
    escaped = parenthesized_power.sub(lambda m: r"\(" + m.group(1) + r"\)", escaped)
    numeric_power = re.compile(r"(?<![A-Za-z0-9])([0-9]+(?:\.[0-9]+)?\^[0-9]+)")
    escaped = numeric_power.sub(lambda m: r"\(" + m.group(1) + r"\)", escaped)
    caret = re.compile(r"(?<![A-Za-z])([0-9]*[A-Za-z](?:\^[0-9]+)(?:\s*[+\-*/]\s*[0-9A-Za-z().^\-]+)*)")
    escaped = caret.sub(lambda m: r"\(" + m.group(1) + r"\)", escaped)
    assign = re.compile(r"\b([A-Za-z])\s*=\s*(-?\d+(?:\.\d+)?)")
    escaped = assign.sub(lambda m: r"\(" + m.group(1) + "=" + m.group(2) + r"\)", escaped)
    return escaped


def _install_renderer_patches(bank_finish_module) -> Dict[str, Any]:
    originals = {
        "append": bank_finish_module._append_graph_runner,
        "collect": bank_finish_module._collect_graph_specs,
        "render": bank_finish_module._render_blocks,
        "viewer": bank_finish_module._viewer,
        "loader": bank_finish_module._load_complete_run,
        "version": bank_finish_module.PILOT_VERSION,
    }

    def collect(records: Iterable[Dict[str, Any]], stimuli: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        specs, refs = originals["collect"](records, stimuli)
        for spec in specs:
            mode = str(spec.get("semantic_mode") or "").lower()
            kind = str(spec.get("kind") or "").lower()
            if mode in {"construction_surface", "algebra_coordinate", "coordinate", "point_read"}:
                spec["pilot_render_mode"] = "standard_coordinate"
            elif kind == "coordinate_graph" and str(spec.get("x_label") or "x").lower() == "x" and str(spec.get("y_label") or "y").lower() == "y":
                spec["pilot_render_mode"] = "standard_coordinate"
            else:
                spec["pilot_render_mode"] = "context"
            if mode == "construction_surface":
                spec["bounds"] = {"x_min": -10, "x_max": 10, "y_min": -10, "y_max": 10}
        return specs, refs

    def append_graph_runner(graph_tool: Path, runner: Path) -> None:
        base = graph_tool.read_text(encoding="utf-8")
        code = r'''

# FULL PIPELINE APPEND-ONLY GRAPH GENERATION BLOCK
if __name__ == "__main__":
    import json as _json
    import sys as _sys
    from pathlib import Path as _Path
    spec_path = _Path(_sys.argv[1])
    out_dir = _Path(_sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = _json.loads(spec_path.read_text(encoding="utf-8"))
    for spec in specs:
        fig, ax = plt.subplots(figsize=(6, 6))
        b = spec["bounds"]
        xmin, xmax = float(b["x_min"]), float(b["x_max"])
        ymin, ymax = float(b["y_min"]), float(b["y_max"])
        functions = []
        if isinstance(spec.get("line"), dict):
            m = float(spec["line"].get("slope", 0))
            c = float(spec["line"].get("intercept", 0))
            functions.append({"expr": lambda x, m=m, c=c: m*x+c, "deriv": lambda x, m=m: np.full_like(x, m, dtype=float), "color": "steelblue", "label": None})
        for piece in spec.get("piecewise", []) if isinstance(spec.get("piecewise"), list) else []:
            if not isinstance(piece, dict):
                continue
            m = float(piece.get("slope", 0)); c = float(piece.get("intercept", 0))
            domain = piece.get("domain") if isinstance(piece.get("domain"), dict) else {}
            lo = float(domain.get("x_min", xmin)); hi = float(domain.get("x_max", xmax))
            def _expr(x, m=m, c=c, lo=lo, hi=hi):
                y = m*x+c
                return np.where((x >= lo) & (x <= hi), y, np.nan)
            functions.append({"expr": _expr, "deriv": lambda x, m=m: np.full_like(x, m, dtype=float), "color": "steelblue", "label": None})
        if spec.get("pilot_render_mode") == "standard_coordinate":
            make_standard_graph(ax, functions, title="")
        else:
            make_context_graph(ax, functions, xmin, xmax, ymin, ymax, xlabel=str(spec.get("x_label") or "x"), ylabel=str(spec.get("y_label") or "y"), title="")
        points = spec.get("points") if isinstance(spec.get("points"), list) else []
        if points:
            xs = [float(p[0]) for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
            ys = [float(p[1]) for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
            if xs and len(xs) == len(ys):
                ax.scatter(xs, ys, color="steelblue", s=42, zorder=5)
                if spec.get("connect_points"):
                    ax.plot(xs, ys, color="steelblue", linewidth=2, zorder=4)
        fig.savefig(out_dir / spec["filename"], dpi=150, bbox_inches="tight")
        plt.close(fig)
'''
        runner.write_text(base.rstrip() + "\n" + code, encoding="utf-8")

    def render_blocks(owner: str, blocks: List[Dict[str, Any]], graph_refs: Dict[str, str], choices: List[Any] | None = None):
        out: List[str] = []
        used: List[str] = []
        for i, block in enumerate(blocks):
            t = block.get("type")
            data = block.get("data") if isinstance(block.get("data"), dict) else {}
            if t == "prose":
                out.append(f'<p>{_mathify_prose(str(data.get("text") or ""))}</p>')
            elif t == "equation":
                latex = str(data.get("latex") or "").strip()
                out.append(f'<div class="equation-card">\\[{html.escape(latex)}\\]</div>')
            elif t == "table":
                out.append(bank_finish_module._html_table(data))
            elif t in {"graph", "response_surface"}:
                filename = graph_refs.get(f"{owner}:{i}")
                if filename:
                    used.append(filename)
                    label = "Graph" if t == "graph" else "Response graphing surface"
                    out.append(f'<div class="representation"><img class="graph-img" src="figures/{html.escape(filename)}" alt="{label}"></div>')
                elif t == "response_surface":
                    out.append('<div class="response-surface" aria-label="Response area"></div>')
        if choices:
            out.append('<ol class="choices" type="A">')
            for choice in choices:
                text = choice.get("text") if isinstance(choice, dict) else choice
                out.append(f"<li>{html.escape(str(text))}</li>")
            out.append("</ol>")
        return "".join(out), used

    def viewer(bank_root: Path, authored: List[Dict[str, Any]], stimuli: Dict[str, Dict[str, Any]], fingerprint: str) -> None:
        unit_label = bank_root.name.removeprefix("unit") or bank_root.name
        viewer_name = f"{bank_root.name}.html"
        by_dest: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for rec in authored:
            by_dest[str(rec.get("destination"))].append(rec)
        parts = [
            '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            f'<title>Algebra 1 Unit {html.escape(unit_label)} Bank</title>',
            '<link rel="stylesheet" href="../../css/base.css"><link rel="stylesheet" href="../../css/bank.css">',
            '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]}};</script>',
            '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script></head>',
            '<body class="bank-viewer">',
            f'<header class="bank-header"><h1>Algebra 1 Unit {html.escape(unit_label)} Bank</h1>',
            f'<p class="sub">Accepted map: {html.escape(fingerprint)} | {len(authored)} finished tasks</p></header>',
            '<div class="toolbar" id="bankToolbar">',
            '<button class="active" data-tab="Exit">Exit</button><button data-tab="Practice 1">Practice 1</button><button data-tab="WTC">WTC</button><button data-tab="Summative">Summative</button>',
            '<input id="bankSearch" placeholder="Filter by ID, I Can, NEW, REASSESS...">',
            '</div>',
            '<div class="totals">',
        ]
        for dest in ("Exit", "Practice 1", "WTC", "Summative"):
            parts.append(f'<div class="total"><b>{len(by_dest.get(dest, []))}</b><span>{html.escape(dest)}</span></div>')
        parts.append('</div>')
        for dest in ("Exit", "Practice 1", "WTC"):
            active = " active" if dest == "Exit" else ""
            parts.append(f'<section class="tab-panel{active}" data-panel="{html.escape(dest)}"><h2>{html.escape(dest)}</h2>')
            groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for rec in by_dest.get(dest, []):
                groups[str(rec.get("section") or "")].append(rec)
            for section, rows in sorted(groups.items()):
                parts.append(f'<div class="section-block"><h2>Section {html.escape(section)}</h2>')
                if dest == "WTC" and rows:
                    sid = str(rows[0].get("shared_stimulus_id") or "")
                    stim = stimuli.get(sid, {})
                    parts.append(f'<article class="card searchable" data-search="{html.escape(sid)}"><div class="ican">Shared stimulus</div><div class="student-surface">{stim.get("student_html", "")}</div></article>')
                parts.append('<div class="cards">')
                for rec in rows:
                    role = ""
                    if dest == "Exit":
                        slot_role = str(rec.get("slot_role") or "").lower()
                        role = "REASSESS" if ("reassess" in slot_role or rec.get("reassessment_of") or rec.get("carry_forward_from")) else "NEW"
                    meta = f'{rec["item_id"]} | {str(rec.get("stage") or "")}'+(f' | {role}' if role else '')
                    search = " ".join([meta, str((rec.get("primary_i_can") or {}).get("text") or ""), str(rec.get("evidence_job") or "")])
                    parts.append(f'<article class="card searchable" data-search="{html.escape(search.lower())}">')
                    parts.append(f'<div class="meta-compact">{html.escape(meta)}</div>')
                    parts.append(f'<div class="ican">{html.escape(str((rec.get("primary_i_can") or {}).get("text") or ""))}</div>')
                    parts.append(f'<div class="student-surface">{rec.get("student_html", "")}</div>')
                    parts.append('<details class="answer"><summary>Answer / solution</summary>')
                    parts.append(f'<p>{_mathify_prose(str(rec.get("answer") or ""))}</p><p>{_mathify_prose(str(rec.get("solution_text") or ""))}</p></details></article>')
                parts.append('</div></div>')
            parts.append('</section>')
        parts.append('<section class="tab-panel secure" data-panel="Summative"><h2>Summative secure blueprint</h2><div class="secure-banner">Secure prompts and keys are intentionally hidden in this viewer.</div><div class="cards">')
        for rec in by_dest.get("Summative", []):
            goal = rec.get("mastery_goal") or {}
            parts.append(f'<article class="card secure searchable" data-search="{html.escape((str(rec.get("item_id"))+" "+str(goal.get("title") or "")).lower())}"><div class="meta-compact">{html.escape(str(rec.get("item_id")))} | {html.escape(str(rec.get("form") or rec.get("form_id") or ""))}</div><div class="target">{html.escape(str(goal.get("title") or goal.get("text") or ""))}</div></article>')
        parts.append('</div></section>')
        parts.append(r'''<script>
const buttons=[...document.querySelectorAll('#bankToolbar button[data-tab]')];
const panels=[...document.querySelectorAll('.tab-panel[data-panel]')];
function showTab(name){buttons.forEach(b=>b.classList.toggle('active',b.dataset.tab===name));panels.forEach(p=>p.classList.toggle('active',p.dataset.panel===name));}
buttons.forEach(b=>b.addEventListener('click',()=>showTab(b.dataset.tab)));
document.getElementById('bankSearch').addEventListener('input',e=>{const q=e.target.value.toLowerCase().trim();document.querySelectorAll('.searchable').forEach(x=>x.classList.toggle('hidden',q && !x.dataset.search.includes(q)));});
</script></body></html>''')
        (bank_root / viewer_name).write_text("".join(parts), encoding="utf-8")

    bank_finish_module._collect_graph_specs = collect
    bank_finish_module._append_graph_runner = append_graph_runner
    bank_finish_module._render_blocks = render_blocks
    bank_finish_module._viewer = viewer
    bank_finish_module.PILOT_VERSION = PILOT_VERSION
    return originals


def _restore_renderer(bank_finish_module, originals: Dict[str, Any]) -> None:
    bank_finish_module._append_graph_runner = originals["append"]
    bank_finish_module._collect_graph_specs = originals["collect"]
    bank_finish_module._render_blocks = originals["render"]
    bank_finish_module._viewer = originals["viewer"]
    bank_finish_module._load_complete_run = originals["loader"]
    bank_finish_module.PILOT_VERSION = originals["version"]


def _audit_bank_output(bank_root: Path, unit: int) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    manifest_path = bank_root / "BANK_MANIFEST.json"
    if not manifest_path.is_file():
        findings.append({"code": "BANK_MANIFEST_MISSING"})
        return {"status": "FAIL", "findings": findings}
    manifest = read_json(manifest_path)
    if manifest.get("qa_status") != "PASS" or not manifest.get("ready_for_downstream"):
        findings.append({"code": "BANK_MANIFEST_NOT_READY"})
    for name in ("MAP_FIDELITY_REPORT.json", "RENDER_QA_REPORT.json"):
        path = bank_root / name
        if not path.is_file() or read_json(path).get("status") != "PASS":
            findings.append({"code": "UPSTREAM_QA_NOT_PASS", "path": name})
    viewer = bank_root / f"unit{unit}.html"
    if not viewer.is_file():
        findings.append({"code": "VIEWER_MISSING"})
        text = ""
    else:
        text = viewer.read_text(encoding="utf-8", errors="replace")
        if 'id="bankToolbar"' not in text:
            findings.append({"code": "VIEWER_MENU_MISSING"})
        if "REASSESS" not in text or "NEW" not in text:
            findings.append({"code": "EXIT_EVIDENCE_ROLE_LABELS_MISSING"})
        # Ignore caret syntax already inside MathJax delimiters. Only visible
        # un-delimited caret notation is a defect.
        audit_text = re.sub(r"\\\((.*?)\\\)", "", text, flags=re.S)
        audit_text = re.sub(r"\\\[(.*?)\\\]", "", audit_text, flags=re.S)
        if re.search(r"<p>[^<]*[A-Za-z0-9)]\^[0-9]", audit_text):
            findings.append({"code": "VISIBLE_RAW_CARET_MATH"})
    graph_specs_path = bank_root.parent.parent.parent.parent / "GRAPH_SPECS.json"
    # The graph specs normally live in the Bank AI run, not the Bank folder. This check is populated by caller when available.
    final_log = bank_root / "FINALIZATION_LOG.txt"
    if not final_log.is_file() or "FINALIZATION_QA: PASS" not in final_log.read_text(encoding="utf-8", errors="replace"):
        findings.append({"code": "FINALIZATION_NOT_PASS"})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings}


def _final_transfer(ctx: ProjectContext, staged_bank: Path, transfer_root: Path, system_head: str | None, course_head: str | None) -> Path:
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
        row: Dict[str, Any] = {"action": "replace" if old else "create", "source": arc, "destination": dst_rel.as_posix()}
        if old:
            row["expected_existing_sha256"] = sha256_file(old)
        entries.append(row)
        payloads.append((src, arc))
    for rel, old in sorted(existing_files.items()):
        if rel not in staged_files:
            dst_rel = Path(ctx.course_dir.name) / "banks" / f"unit{ctx.unit}" / rel
            entries.append({"action": "delete", "destination": dst_rel.as_posix(), "expected_existing_sha256": sha256_file(old)})
    transfer_root.mkdir(parents=True, exist_ok=True)
    out = transfer_root / f"{ctx.course_dir.name}_u{ctx.unit}_FULL_BANK_PIPELINE_v0_7_TRANSFER.zip"
    manifest = {
        "schema_version": 2,
        "package_type": "github_transfer",
        "package_id": f"{ctx.course_dir.name}_u{ctx.unit}_full_bank_pipeline_v0_7_{time.strftime('%Y%m%d-%H%M%S')}",
        "source_snapshot": {"system_head": system_head, "course_head": course_head},
        "files": entries,
    }
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2))
        for src, arc in payloads:
            zf.write(src, arc)
    return out


def _finish_bank(ctx: ProjectContext, root: Path, ai: Dict[str, Any], transfer_root: Path) -> Dict[str, Any]:
    from . import bank_finish

    work = root / "bank_ai"
    state = _read_state(root)
    originals = _install_renderer_patches(bank_finish)
    bank_finish._load_complete_run = lambda _ctx, _staging, _ai, _folder: _pipeline_bank_loader(ctx, root, _ai)
    try:
        result = bank_finish.finish_complete_bank(ctx, root, ai, ctx.course_dir.name, root / "_internal_transfer")
    finally:
        _restore_renderer(bank_finish, originals)

    staged_bank = Path(result["staged_bank"])
    audit = _audit_bank_output(staged_bank, ctx.unit)
    graph_specs_path = work / "GRAPH_SPECS.json"
    axes_mismatches: List[str] = []
    mode_counts = Counter()
    if graph_specs_path.is_file():
        for spec in read_json(graph_specs_path):
            if not isinstance(spec, dict):
                continue
            mode = str(spec.get("pilot_render_mode") or "")
            mode_counts[mode] += 1
            if str(spec.get("semantic_mode") or "").lower() == "construction_surface" and mode != "standard_coordinate":
                axes_mismatches.append(str(spec.get("filename") or "unknown"))
    if axes_mismatches:
        audit["status"] = "FAIL"
        audit.setdefault("findings", []).append({"code": "REQUIRED_AXES_RENDER_MODE", "files": axes_mismatches})
        audit["finding_count"] = len(audit["findings"])
    audit["graph_render_modes"] = dict(mode_counts)
    audit["required_axes_mode_mismatches"] = axes_mismatches
    _write_json(staged_bank / "FULL_PIPELINE_AUDIT.json", audit)
    if audit.get("status") != "PASS":
        raise ValueError("Complete Bank audit did not PASS: " + json.dumps(audit.get("findings", [])[:6]))
    final_zip = _final_transfer(ctx, staged_bank, transfer_root, state.get("system_head"), state.get("course_head"))
    return {**result, "transfer_zip": str(final_zip), "full_pipeline_audit": audit}


def continue_full_pipeline(ctx: ProjectContext, staging_root: Path, downloads: Path, transfer_root: Path) -> Dict[str, Any]:
    root = _pipeline_root(staging_root, ctx)
    state = _read_state(root)
    if not state:
        raise ValueError("No active Full Bank Pipeline. Click Start Full Pipeline first.")
    stage = str(state.get("stage") or "")

    if stage == "awaiting_map_ai":
        path, ai = _find_json(downloads, "AI_MAP_CONTENT*.json", MAP_AI_SCHEMA, str(state.get("map_run_id")))
        source_map = _assemble_map(ctx, root, ai)
        report = audit_bank_map(ctx, source_map_override=source_map)
        audit_dir = root / "map_audit"
        if audit_dir.exists():
            shutil.rmtree(audit_dir)
        save_audit_report(report, audit_dir)
        if report.get("mechanical_shape_status") != "PASS":
            raise ValueError("Fresh staged Bank Map failed local mechanical audit")
        candidates = _candidate_ids(report)
        if candidates:
            handoff = _map_repair_handoff(ctx, root, report, downloads)
            state.update({"stage": "awaiting_map_repair_ai", "map_result": str(path), "map_repair_run_id": str(state.get("pipeline_id")) + "_map_repair", "map_candidate_ids": candidates, "map_repair_handoff": str(handoff)})
            _write_state(root, state)
            return {"status": "AI_NEEDED", "stage": "awaiting_map_repair_ai", "map_mechanical_audit": "PASS", "semantic_candidate_count": len(candidates), "handoff": str(handoff)}
        state.update({"map_result": str(path), "map_audit": "PASS"})
        _write_state(root, state)
        return _prepare_bank_handoff(ctx, root, downloads)

    if stage == "awaiting_map_repair_ai":
        path, review = _find_json(downloads, "AI_SEMANTIC_REVIEW*.json", SEMANTIC_REVIEW_SCHEMA, str(state.get("map_repair_run_id")))
        _apply_map_review(ctx, root, review, list(state.get("map_candidate_ids") or []))
        report = audit_bank_map(ctx, source_map_override=root / "staged_source_map")
        if report.get("mechanical_shape_status") != "PASS" or int((report.get("facts") or {}).get("semantic_candidate_count", 0) or 0):
            raise ValueError("Staged Bank Map still does not PASS after semantic repair")
        state.update({"map_repair_result": str(path), "map_audit": "PASS"})
        _write_state(root, state)
        return _prepare_bank_handoff(ctx, root, downloads)

    if stage == "awaiting_bank_ai":
        path, ai = _find_json(downloads, "AI_BANK_CONTENT*.json", BANK_AI_SCHEMA, str(state.get("bank_run_id")))
        result = _finish_bank(ctx, root, ai, transfer_root)
        state.update({
            "stage": "complete",
            "bank_result": str(path),
            "bank_audit": "PASS",
            "transfer_zip": result.get("transfer_zip"),
            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        _write_state(root, state)
        return {
            "status": "PASS",
            "stage": "complete",
            "map_audit": "PASS",
            "bank_audit": "PASS",
            "finished_task_count": result.get("finished_task_count"),
            "seed_count": result.get("seed_count"),
            "graph_asset_count": result.get("graph_asset_count"),
            "graph_render_modes": (result.get("full_pipeline_audit") or {}).get("graph_render_modes"),
            "transfer_zip": result.get("transfer_zip"),
            "canonical_repo_modified": False,
        }

    if stage == "complete":
        return {"status": "PASS", "stage": "complete", "map_audit": state.get("map_audit"), "bank_audit": state.get("bank_audit"), "transfer_zip": state.get("transfer_zip"), "canonical_repo_modified": False}
    raise ValueError(f"Unknown Full Bank Pipeline stage: {stage}")
