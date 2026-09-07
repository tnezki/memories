from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .authorities import ProjectContext, resolve_common
from .fs import read_json, sha256_file

EXPECTED_SOURCE_MAP_FILES = {
    "MAP_MANIFEST.json",
    "MAP_REPORT.txt",
    "bank_inventory_map.json",
    "exit_map.json",
    "practice1_map.json",
    "seed_map.json",
    "summative_map.json",
    "unit1_question_design_map.json",  # unit number is normalized below
    "wtc_map.json",
}

EXPECTED_SLICES = {
    "inventory": "bank_inventory_map.json",
    "question_design": None,  # unit-specific below
    "Exit": "exit_map.json",
    "Summative": "summative_map.json",
    "Practice 1": "practice1_map.json",
    "WTC": "wtc_map.json",
    "Seeds": "seed_map.json",
}

DIRECT_STRUCTURE = "FEATURE-IDENTIFY-FROM-REPRESENTATION-01"
INFERENCE_STRUCTURES = {"GRAPH-INFER-BEHAVIOR-01"}
DIRECT_TOKENS = (
    "read ", "read a ", "identify ", "identify the ", "name ", "extract ",
    "locate ", "record ", "coordinate", "axis", "axes", "scale", "intercept",
)
INFERENCE_TOKENS = (
    "infer", "trend", "behavior", "increase", "decrease", "predict", "justify",
    "explain why", "rate of change", "compare how", "growth", "qualitative",
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    record_id: str = ""
    path: str = ""
    suggested_change: str = ""


def _finding(severity: str, code: str, message: str, **kwargs: str) -> Finding:
    return Finding(severity=severity, code=code, message=message, **kwargs)


def _records(data: Any) -> List[Dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    recs = data.get("records")
    return [r for r in recs if isinstance(r, dict)] if isinstance(recs, list) else []


def _wtc_records(data: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(data, dict):
        return out
    for wtc in data.get("wtcs", []) if isinstance(data.get("wtcs"), list) else []:
        if not isinstance(wtc, dict):
            continue
        for rec in wtc.get("parts_plan", []) if isinstance(wtc.get("parts_plan"), list) else []:
            if isinstance(rec, dict):
                out.append(rec)
    return out


def _seed_records(data: Any) -> List[Dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    for key in ("records", "seeds", "seed_records"):
        value = data.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    return []


def _rid(rec: Dict[str, Any]) -> str:
    return str(rec.get("design_slot_id") or rec.get("record_id") or rec.get("seed_id") or "")


def _semantic_direct_read_findings(records: Iterable[Dict[str, Any]], rel_path: str) -> List[Finding]:
    findings: List[Finding] = []
    for rec in records:
        sid = str(rec.get("question_structure_id") or "")
        if sid not in INFERENCE_STRUCTURES:
            continue
        evidence = str(rec.get("evidence_job") or "").lower()
        action = str(rec.get("student_action") or "").lower()
        text = f"{evidence} {action}"
        direct = any(token in text for token in DIRECT_TOKENS)
        infer = any(token in text for token in INFERENCE_TOKENS)
        supplied = not any(
            bool(route.get("student_constructed"))
            for route in rec.get("representation_routes", [])
            if isinstance(route, dict)
        )
        if direct and not infer and supplied:
            findings.append(_finding(
                "REPAIR",
                "DIRECT_READ_STRUCTURE_MISMATCH",
                f"Direct representation read is mapped to inference structure {sid}.",
                record_id=_rid(rec),
                path=rel_path,
                suggested_change=f"Use current direct representation-reading structure, expected {DIRECT_STRUCTURE}, if semantic review confirms the task remains direct.",
            ))
    return findings


def _load_required(path: Path, findings: List[Finding], label: str) -> Any:
    if not path.is_file():
        findings.append(_finding("BLOCKER", "REQUIRED_FILE_MISSING", f"Missing required {label}.", path=str(path)))
        return None
    try:
        return read_json(path)
    except Exception as exc:
        findings.append(_finding("BLOCKER", "INVALID_JSON", f"Invalid JSON in {label}: {exc}", path=str(path)))
        return None


def audit_bank_map(ctx: ProjectContext, source_map_override: Path | None = None) -> Dict[str, Any]:
    source_map = source_map_override if source_map_override is not None else ctx.course_dir / f"banks/unit{ctx.unit}/source_map"
    findings: List[Finding] = []
    facts: Dict[str, Any] = {
        "source_map": str(source_map),
        "unit": ctx.unit,
        "mechanical_contract_locked": True,
        "ai_may_not_override_mechanical_facts": True,
    }

    if not source_map.is_dir():
        findings.append(_finding("BLOCKER", "SOURCE_MAP_MISSING", "Deployed Bank Map directory is missing.", path=str(source_map)))
        return _finish(facts, findings)

    expected_files = set(EXPECTED_SOURCE_MAP_FILES)
    expected_files.remove("unit1_question_design_map.json")
    design_name = f"unit{ctx.unit}_question_design_map.json"
    expected_files.add(design_name)
    actual_files = {p.name for p in source_map.iterdir() if p.is_file() and not p.name.startswith(".")}
    missing = sorted(expected_files - actual_files)
    unexpected = sorted(actual_files - expected_files)
    facts["expected_files"] = sorted(expected_files)
    facts["actual_files"] = sorted(actual_files)
    facts["missing_files"] = missing
    facts["unexpected_files"] = unexpected
    if missing:
        findings.append(_finding("BLOCKER", "CURRENT_SHAPE_MISSING_FILES", f"Missing current Bank Map files: {', '.join(missing)}", path=str(source_map)))
    if unexpected:
        findings.append(_finding("REPAIR", "CURRENT_SHAPE_UNEXPECTED_FILES", f"Unexpected active files in source_map: {', '.join(unexpected)}", path=str(source_map)))

    manifest_path = source_map / "MAP_MANIFEST.json"
    manifest = _load_required(manifest_path, findings, "MAP_MANIFEST.json")
    inventory = _load_required(source_map / "bank_inventory_map.json", findings, "bank_inventory_map.json")
    design = _load_required(source_map / design_name, findings, design_name)
    exit_map = _load_required(source_map / "exit_map.json", findings, "exit_map.json")
    summative_map = _load_required(source_map / "summative_map.json", findings, "summative_map.json")
    practice_map = _load_required(source_map / "practice1_map.json", findings, "practice1_map.json")
    wtc_map = _load_required(source_map / "wtc_map.json", findings, "wtc_map.json")
    seed_map = _load_required(source_map / "seed_map.json", findings, "seed_map.json")

    if isinstance(manifest, dict):
        facts["manifest_status"] = manifest.get("status")
        facts["map_fingerprint"] = manifest.get("map_fingerprint")
        if str(manifest.get("status", "")).upper() != "PASS":
            findings.append(_finding("BLOCKER", "MANIFEST_NOT_PASS", f"MAP_MANIFEST status is {manifest.get('status')!r}.", path=str(manifest_path)))

        expected_slices = dict(EXPECTED_SLICES)
        expected_slices["question_design"] = design_name
        actual_slices = manifest.get("slices") if isinstance(manifest.get("slices"), dict) else {}
        facts["expected_slices"] = expected_slices
        facts["actual_slices"] = actual_slices
        if actual_slices != expected_slices:
            findings.append(_finding("REPAIR", "SLICE_MANIFEST_MISMATCH", "MAP_MANIFEST slices do not match the current pilot Bank Map slice contract.", path=str(manifest_path)))

        declared = manifest.get("files") if isinstance(manifest.get("files"), list) else []
        hash_checks = []
        for entry in declared:
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path")
            expected_hash = entry.get("sha256")
            if not rel or not expected_hash:
                continue
            p = source_map / str(rel)
            actual_hash = sha256_file(p) if p.is_file() else None
            ok = actual_hash == expected_hash
            hash_checks.append({"path": rel, "ok": ok, "expected": expected_hash, "actual": actual_hash})
            if not ok:
                findings.append(_finding("BLOCKER", "DECLARED_HASH_MISMATCH", f"Declared SHA-256 mismatch for {rel}.", path=str(p)))
        facts["declared_hash_checks"] = hash_checks

    design_records = _records(design)
    facts["design_record_count"] = len(design_records)
    if isinstance(design, dict):
        declared_count = ((design.get("question_design") or {}).get("finished_task_slot_count")
                          if isinstance(design.get("question_design"), dict) else None)
        facts["design_declared_count"] = declared_count
        if declared_count != len(design_records):
            findings.append(_finding("BLOCKER", "DESIGN_COUNT_MISMATCH", f"Design declares {declared_count}; records[] contains {len(design_records)}.", path=str(source_map / design_name)))

    ids = [_rid(r) for r in design_records]
    dupes = sorted(k for k, v in Counter(ids).items() if k and v > 1)
    blanks = sum(1 for x in ids if not x)
    facts["duplicate_design_ids"] = dupes
    facts["blank_design_ids"] = blanks
    if dupes:
        findings.append(_finding("BLOCKER", "DUPLICATE_DESIGN_IDS", f"Duplicate design slot IDs: {', '.join(dupes[:10])}", path=str(source_map / design_name)))
    if blanks:
        findings.append(_finding("BLOCKER", "BLANK_DESIGN_IDS", f"{blanks} design records have no design_slot_id.", path=str(source_map / design_name)))

    dest_counts = Counter(str(r.get("destination") or "") for r in design_records)
    facts["destination_counts"] = dict(sorted(dest_counts.items()))

    if isinstance(inventory, dict):
        inv_total = inventory.get("finished_task_slot_total")
        inv_dest = {}
        for d in inventory.get("canonical_destinations", []) if isinstance(inventory.get("canonical_destinations"), list) else []:
            if isinstance(d, dict):
                inv_dest[str(d.get("destination"))] = d
        expected_by_inventory = {
            name: d.get("finished_task_slots")
            for name, d in inv_dest.items()
            if isinstance(d.get("finished_task_slots"), int) and int(d.get("finished_task_slots")) > 0
        }
        facts["inventory_finished_task_total"] = inv_total
        facts["inventory_destination_counts"] = expected_by_inventory
        if isinstance(inv_total, int) and inv_total != len(design_records):
            findings.append(_finding("BLOCKER", "INVENTORY_TOTAL_MISMATCH", f"Inventory total {inv_total} does not equal design record count {len(design_records)}.", path=str(source_map / "bank_inventory_map.json")))
        for destination, expected_count in expected_by_inventory.items():
            actual = dest_counts.get(destination, 0)
            if actual != expected_count:
                findings.append(_finding("BLOCKER", "DESTINATION_COUNT_MISMATCH", f"{destination}: inventory expects {expected_count}, design map contains {actual}.", path=str(source_map / design_name)))

    slice_sets = {
        "Exit": {_rid(r) for r in _records(exit_map)},
        "Summative": {_rid(r) for r in _records(summative_map)},
        "Practice 1": {_rid(r) for r in _records(practice_map)},
        "WTC": {_rid(r) for r in _wtc_records(wtc_map)},
    }
    for destination, slice_ids in slice_sets.items():
        design_ids = {_rid(r) for r in design_records if str(r.get("destination")) == destination}
        missing_ids = sorted(design_ids - slice_ids)
        extra_ids = sorted(slice_ids - design_ids)
        facts.setdefault("slice_id_checks", {})[destination] = {
            "design_count": len(design_ids), "slice_count": len(slice_ids),
            "missing": missing_ids, "extra": extra_ids,
        }
        if missing_ids or extra_ids:
            findings.append(_finding("BLOCKER", "SLICE_ID_MISMATCH", f"{destination} slice IDs do not match question-design IDs (missing={len(missing_ids)}, extra={len(extra_ids)})."))

    practice_records = _records(practice_map)
    practice_counts = defaultdict(Counter)
    for rec in practice_records:
        practice_counts[str(rec.get("section"))][str(rec.get("stage"))] += 1
    facts["practice_stage_counts"] = {s: dict(c) for s, c in sorted(practice_counts.items())}
    for section, counts in sorted(practice_counts.items()):
        for stage in ("Intro", "Review", "Mastery"):
            if counts.get(stage, 0) != 8:
                findings.append(_finding("BLOCKER", "PRACTICE_STAGE_BALANCE", f"Section {section} has {counts.get(stage, 0)} {stage} Practice records; expected 8."))
        if sum(counts.values()) != 24:
            findings.append(_finding("BLOCKER", "PRACTICE_SECTION_COUNT", f"Section {section} has {sum(counts.values())} Practice records; expected 24."))

    exit_counts = Counter(str(r.get("section")) for r in _records(exit_map))
    facts["exit_section_counts"] = dict(sorted(exit_counts.items()))
    for section, count in sorted(exit_counts.items()):
        if count != 4:
            findings.append(_finding("BLOCKER", "EXIT_SECTION_COUNT", f"Section {section} has {count} Exit records; expected 4."))

    wtc_counts = Counter(str(r.get("section")) for r in _wtc_records(wtc_map))
    facts["wtc_section_part_counts"] = dict(sorted(wtc_counts.items()))
    for section, count in sorted(wtc_counts.items()):
        if count != 4:
            findings.append(_finding("BLOCKER", "WTC_PART_COUNT", f"Section {section} has {count} WTC parts; expected 4."))

    profile = None
    try:
        common = resolve_common(ctx)
        profile = read_json(common["resource_root"] / "profiles/bank_course_profile.json")
    except Exception as exc:
        findings.append(_finding("BLOCKER", "PROFILE_UNREADABLE", f"Could not read current Bank profile: {exc}"))
    seed_records = _seed_records(seed_map)
    facts["seed_record_count"] = len(seed_records)
    if isinstance(profile, dict):
        approved = ((profile.get("approved_seed_candidates") or {}).get(str(ctx.unit), []))
        approved_ids = {str(x.get("seed_id")) for x in approved if isinstance(x, dict)} if isinstance(approved, list) else set()
        actual_seed_ids = {_rid(r) for r in seed_records}
        facts["approved_seed_ids"] = sorted(approved_ids)
        facts["actual_seed_ids"] = sorted(actual_seed_ids)
        if approved_ids and approved_ids != actual_seed_ids:
            findings.append(_finding("REPAIR", "SEED_SET_MISMATCH", f"Approved seed set differs from deployed seed set (expected={len(approved_ids)}, actual={len(actual_seed_ids)}).", path=str(source_map / "seed_map.json")))

    semantic_records: List[Dict[str, Any]] = []
    for recs in (_records(exit_map), _records(summative_map), practice_records, _wtc_records(wtc_map)):
        semantic_records.extend(recs)
    semantic_findings = _semantic_direct_read_findings(semantic_records, "destination slices")
    findings.extend(semantic_findings)
    facts["local_semantic_lint"] = {
        "direct_read_structure_mismatches": len(semantic_findings),
        "rule": "Only flags explicit inference structures on supplied representations when evidence/action language is direct-read and contains no inference-language signal.",
    }

    if isinstance(manifest, dict):
        qa = manifest.get("qa") if isinstance(manifest.get("qa"), dict) else {}
        sem = qa.get("semantic_conflicts") if isinstance(qa.get("semantic_conflicts"), dict) else {}
        declared_direct = sem.get("direct_read_inflation_conflicts")
        facts["manifest_declared_direct_read_conflicts"] = declared_direct
        if isinstance(declared_direct, int) and declared_direct != len(semantic_findings):
            findings.append(_finding(
                "REPAIR",
                "SEMANTIC_QA_COUNTER_STALE",
                f"MAP_MANIFEST reports direct_read_inflation_conflicts={declared_direct}, but local current-contract lint finds {len(semantic_findings)} candidate mismatch(es).",
                path=str(manifest_path),
            ))

    mechanical_codes = {
        "SOURCE_MAP_MISSING", "CURRENT_SHAPE_MISSING_FILES", "CURRENT_SHAPE_UNEXPECTED_FILES",
        "MANIFEST_NOT_PASS", "SLICE_MANIFEST_MISMATCH", "DECLARED_HASH_MISMATCH", "DESIGN_COUNT_MISMATCH",
        "DUPLICATE_DESIGN_IDS", "BLANK_DESIGN_IDS", "INVENTORY_TOTAL_MISMATCH", "DESTINATION_COUNT_MISMATCH",
        "SLICE_ID_MISMATCH", "PRACTICE_STAGE_BALANCE", "PRACTICE_SECTION_COUNT", "EXIT_SECTION_COUNT",
        "WTC_PART_COUNT", "REQUIRED_FILE_MISSING", "INVALID_JSON",
    }
    facts["mechanical_finding_count"] = sum(1 for f in findings if f.code in mechanical_codes)
    facts["semantic_candidate_count"] = sum(1 for f in findings if f.code in {"DIRECT_READ_STRUCTURE_MISMATCH", "SEMANTIC_QA_COUNTER_STALE"})
    return _finish(facts, findings)


def _finish(facts: Dict[str, Any], findings: List[Finding]) -> Dict[str, Any]:
    blockers = [f for f in findings if f.severity == "BLOCKER"]
    repairs = [f for f in findings if f.severity == "REPAIR"]
    status = "FAIL" if blockers else ("REPAIR_NEEDED" if repairs else "PASS")
    mechanical_ok = not any(f.severity == "BLOCKER" or f.code in {
        "CURRENT_SHAPE_UNEXPECTED_FILES", "SLICE_MANIFEST_MISMATCH"
    } for f in findings)
    return {
        "schema": "curriculum-builder-local-map-audit/0.2",
        "status": status,
        "mechanical_shape_status": "PASS" if mechanical_ok else "FAIL",
        "facts": facts,
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
        "locked_ai_instruction": (
            "Mechanical facts in this report are authoritative for the pilot run. AI may not claim missing/old filenames, "
            "count/hash/schema defects, or migration needs unless this local report records that defect. AI review is limited "
            "to listed semantic candidates and other explicitly unresolved semantic judgment."
        ),
    }


def save_audit_report(report: Dict[str, Any], run_dir: Path) -> Dict[str, str]:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "LOCAL_MAP_AUDIT.json"
    txt_path = run_dir / "LOCAL_MAP_AUDIT.txt"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "CURRICULUM BUILDER LOCAL MAP AUDIT v0.2",
        "=======================================",
        f"status: {report['status']}",
        f"mechanical_shape_status: {report['mechanical_shape_status']}",
        f"finding_count: {report['finding_count']}",
        "",
        "LOCKED MECHANICAL FACTS",
        "-----------------------",
        f"actual_files: {', '.join(report['facts'].get('actual_files', []))}",
        f"design_record_count: {report['facts'].get('design_record_count')}",
        f"destination_counts: {report['facts'].get('destination_counts')}",
        f"mechanical_finding_count: {report['facts'].get('mechanical_finding_count')}",
        f"semantic_candidate_count: {report['facts'].get('semantic_candidate_count')}",
        "",
        "FINDINGS",
        "--------",
    ]
    if not report["findings"]:
        lines.append("NONE")
    for f in report["findings"]:
        rid = f" [{f['record_id']}]" if f.get("record_id") else ""
        lines.append(f"{f['severity']} {f['code']}{rid}: {f['message']}")
        if f.get("suggested_change"):
            lines.append(f"  suggested: {f['suggested_change']}")
    lines.extend(["", "AI BOUNDARY", "-----------", report["locked_ai_instruction"]])
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "text": str(txt_path)}
