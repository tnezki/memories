#!/usr/bin/env python3
"""Deterministic mechanical contract validator for Bank-v2 Stage 3B.

This validator checks only mechanically decidable Practice-family contracts.
It intentionally does NOT judge physics correctness, instructional quality,
semantic evidence alignment, difficulty quality, novelty, wording, or aesthetics.
Those belong in separate review passes.

Exit codes:
  0 PASS
  1 FAIL (contract errors found)
  2 usage/input error
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TOOL_VERSION = "1.0.0"
REPORT_SCHEMA = "bank-3b-contract-qa/1.0"


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    family_id: str = ""
    path: str = ""


def norm_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = html_lib.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def add(findings: list[Finding], code: str, message: str, *, family_id: str = "", path: str = "") -> None:
    findings.append(Finding(code=code, message=message, family_id=family_id, path=path))


def has_class(html: str, tag: str, class_name: str) -> bool:
    pat = re.compile(
        rf"<{tag}\b[^>]*\bclass\s*=\s*(['\"])\s*[^'\"]*\b{re.escape(class_name)}\b[^'\"]*\1",
        re.IGNORECASE,
    )
    return bool(pat.search(html or ""))


def visible_html_text(html: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", html or "", flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    return norm_text(text)


def authored_family_list(data: Any, path: Path) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError(f"expected object in authored practice slice: {path}")
    for key in ("family_records", "families", "records"):
        value = data.get(key)
        if isinstance(value, list):
            bad = [i for i, x in enumerate(value) if not isinstance(x, dict)]
            if bad:
                raise ValueError(f"non-object {key} entries in {path} at indexes {bad}")
            return value
    raise ValueError(f"expected family_records[], families[], or records[] in authored practice slice: {path}")


def route_for(map_rec: dict[str, Any]) -> dict[str, Any]:
    route = map_rec.get("representation_route")
    if isinstance(route, dict):
        return route
    render = map_rec.get("render_contract")
    if isinstance(render, dict):
        return render
    return {}


def compare_field(map_rec: dict[str, Any], authored: dict[str, Any], field: str, findings: list[Finding], rel_path: str) -> None:
    fid = str(authored.get("family_id") or authored.get("record_id") or "")
    if map_rec.get(field) != authored.get(field):
        add(
            findings,
            "MAP_FIELD_DRIFT",
            f"{field} differs from accepted Practice map: expected {map_rec.get(field)!r}; got {authored.get(field)!r}",
            family_id=fid,
            path=rel_path,
        )


def check_seed_nonempty(seed: dict[str, Any], findings: list[Finding], fid: str, rel_path: str) -> None:
    for key in ("student_text", "student_html", "answer", "solution_text", "solution_html"):
        value = seed.get(key)
        if not isinstance(value, str) or not value.strip():
            add(findings, "SEED_CONTENT_EMPTY", f"canonical_seed.{key} is empty", family_id=fid, path=rel_path)
        elif value.strip().lower() in {"todo", "tbd", "placeholder", "lorem ipsum"}:
            add(findings, "SEED_PLACEHOLDER", f"canonical_seed.{key} is a placeholder", family_id=fid, path=rel_path)


def check_selected_response(map_rec: dict[str, Any], seed: dict[str, Any], findings: list[Finding], fid: str, rel_path: str) -> None:
    if map_rec.get("response_mode") != "selected_response":
        return
    choices = seed.get("choices")
    if not isinstance(choices, list) or not choices:
        add(findings, "SR_CHOICES_MISSING", "selected-response canonical seed has no stored choices", family_id=fid, path=rel_path)
        return

    expected_count = map_rec.get("choice_count")
    if isinstance(expected_count, int) and len(choices) != expected_count:
        add(findings, "SR_CHOICE_COUNT", f"expected {expected_count} choices; found {len(choices)}", family_id=fid, path=rel_path)

    ids: list[str] = []
    texts: list[str] = []
    for i, choice in enumerate(choices):
        if not isinstance(choice, dict):
            add(findings, "SR_CHOICE_SHAPE", f"choice index {i} is not an object", family_id=fid, path=rel_path)
            continue
        cid = norm_text(choice.get("id"))
        ctext = norm_text(choice.get("text"))
        ids.append(cid)
        texts.append(ctext)
        if not cid or not ctext:
            add(findings, "SR_CHOICE_EMPTY", f"choice index {i} has empty id/text", family_id=fid, path=rel_path)

    for dup in sorted(k for k, v in Counter(ids).items() if k and v > 1):
        add(findings, "SR_DUPLICATE_ID", f"duplicate choice id {dup!r}", family_id=fid, path=rel_path)
    normed = [x.casefold() for x in texts if x]
    for dup in sorted(k for k, v in Counter(normed).items() if v > 1):
        add(findings, "SR_DUPLICATE_TEXT", f"duplicate choice text {dup!r}", family_id=fid, path=rel_path)

    correct = norm_text(seed.get("correct_choice"))
    if not correct:
        add(findings, "SR_KEY_MISSING", "selected-response canonical seed has no correct_choice", family_id=fid, path=rel_path)
    elif correct not in ids:
        add(findings, "SR_KEY_INVALID", f"correct_choice {correct!r} is not a stored choice id", family_id=fid, path=rel_path)

    student_html = str(seed.get("student_html") or "")
    if not has_class(student_html, "ol", "choices") and not has_class(student_html, "ul", "choices"):
        add(findings, "SR_CHOICES_NOT_RENDERED", "student_html has no choice list with class choices", family_id=fid, path=rel_path)
    rendered = visible_html_text(student_html).casefold()
    for text in texts:
        if text and text.casefold() not in rendered:
            add(findings, "SR_CHOICE_NOT_VISIBLE", f"stored choice not visible in student_html: {text!r}", family_id=fid, path=rel_path)


def check_representation(course_root: Path, map_rec: dict[str, Any], seed: dict[str, Any], findings: list[Finding], fid: str, rel_path: str) -> None:
    mode = str(map_rec.get("representation_mode") or "")
    route = route_for(map_rec)
    route_type = str(route.get("route_type") or "")
    student_html = str(seed.get("student_html") or "")

    if mode == "semantic_data_table" or route_type == "semantic_html_table":
        if not re.search(r"<table\b", student_html, flags=re.I):
            add(findings, "TABLE_HTML_MISSING", "table seed has no <table> in student_html", family_id=fid, path=rel_path)
        if not has_class(student_html, "table", "values"):
            add(findings, "TABLE_VALUES_CLASS_MISSING", "table seed does not use class values", family_id=fid, path=rel_path)

    if route_type == "canonical_asset":
        canonical = norm_text(route.get("canonical_path"))
        if not canonical:
            add(findings, "ASSET_PATH_MISSING", "canonical_asset route has no canonical_path", family_id=fid, path=rel_path)
        else:
            if not (course_root / canonical).is_file():
                add(findings, "ASSET_FILE_MISSING", f"canonical asset does not exist: {canonical}", family_id=fid, path=rel_path)
            refs = seed.get("figure_refs")
            if not isinstance(refs, list) or canonical not in refs:
                add(findings, "ASSET_REF_MISSING", f"canonical_seed.figure_refs does not contain {canonical}", family_id=fid, path=rel_path)
            if canonical not in student_html and Path(canonical).name not in student_html:
                add(findings, "ASSET_NOT_RENDERED", f"student_html does not reference canonical asset {canonical}", family_id=fid, path=rel_path)

    if route_type == "student_constructed" or mode.startswith("student_constructed"):
        if not has_class(student_html, "div", "response-surface"):
            add(findings, "CONSTRUCTED_SURFACE_MISSING", "student-constructed seed has no response-surface div", family_id=fid, path=rel_path)

    if mode == "equation_relationship" and not any(token in student_html for token in ("\\(", "\\[", "$$")):
        add(findings, "EQUATION_NOT_RENDERED", "equation_relationship seed has no MathJax delimiter in student_html", family_id=fid, path=rel_path)

    if route_type == "registered_tool":
        tool_key = norm_text(route.get("tool_key") or route.get("tool"))
        if not tool_key:
            add(findings, "REGISTERED_TOOL_KEY_MISSING", "registered_tool route has no tool_key", family_id=fid, path=rel_path)
        refs = seed.get("representation_refs")
        if not isinstance(refs, list) or not refs:
            add(findings, "REGISTERED_TOOL_OUTPUT_REF_MISSING", "registered_tool seed has no representation_refs", family_id=fid, path=rel_path)

    rep_need = str(map_rec.get("representation_need") or "")
    if rep_need.startswith("required") and mode not in {"", "direct_text"}:
        visible = (
            re.search(r"<(?:img|svg|table)\b", student_html, flags=re.I)
            or "response-surface" in student_html
            or any(token in student_html for token in ("\\(", "\\[", "$$"))
        )
        if not visible:
            add(findings, "REQUIRED_REPRESENTATION_NOT_VISIBLE", f"required representation_mode {mode!r} has no visible render marker", family_id=fid, path=rel_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="expanded course repository root")
    ap.add_argument("--unit", type=int, required=True)
    ap.add_argument("--json-report")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    bank_root = root / "banks" / f"unit{args.unit}"
    map_root = root / "banks" / f"unit{args.unit}_bank_map"
    findings: list[Finding] = []

    try:
        practice_map = load_json(map_root / "practice_map.json")
        map_manifest = load_json(map_root / "MAP_MANIFEST.json")
        manifest = load_json(bank_root / "BANK_MANIFEST.json")
        item_index = load_json(bank_root / "ITEM_INDEX.json")
    except ValueError as exc:
        print(f"INPUT ERROR: {exc}")
        return 2

    map_records = practice_map.get("family_records") if isinstance(practice_map, dict) else None
    if not isinstance(map_records, list) or any(not isinstance(x, dict) for x in map_records):
        print("INPUT ERROR: practice_map.json must contain family_records[] objects")
        return 2

    map_by_id: dict[str, dict[str, Any]] = {}
    for rec in map_records:
        fid = str(rec.get("family_id") or rec.get("record_id") or "")
        if not fid:
            add(findings, "MAP_FAMILY_ID_MISSING", "Practice map record has no family_id/record_id")
            continue
        if fid in map_by_id:
            add(findings, "MAP_DUPLICATE_FAMILY", "Practice map contains duplicate family ID", family_id=fid)
        map_by_id[fid] = rec

    authored_by_id: dict[str, tuple[dict[str, Any], str, int]] = {}
    practice_dir = bank_root / "practice"
    if not practice_dir.is_dir():
        add(findings, "PRACTICE_DIR_MISSING", f"missing practice directory: {practice_dir.relative_to(root)}")
    else:
        for path in sorted(practice_dir.glob("section_*.json")):
            rel = str(path.relative_to(bank_root))
            try:
                families = authored_family_list(load_json(path), path)
            except ValueError as exc:
                add(findings, "PRACTICE_SLICE_INVALID", str(exc), path=rel)
                continue
            for idx, fam in enumerate(families):
                fid = str(fam.get("family_id") or fam.get("record_id") or "")
                if not fid:
                    add(findings, "AUTHORED_FAMILY_ID_MISSING", "authored Practice family has no family_id", path=rel)
                    continue
                if fid in authored_by_id:
                    add(findings, "AUTHORED_DUPLICATE_FAMILY", "Practice family authored more than once", family_id=fid, path=rel)
                else:
                    authored_by_id[fid] = (fam, rel, idx)

    expected_ids = set(map_by_id)
    actual_ids = set(authored_by_id)
    for fid in sorted(expected_ids - actual_ids):
        add(findings, "FAMILY_MISSING", "mapped Practice family was not authored", family_id=fid)
    for fid in sorted(actual_ids - expected_ids):
        add(findings, "UNMAPPED_FAMILY", "authored Practice family is not in accepted Practice map", family_id=fid, path=authored_by_id[fid][1])

    exact_fields = (
        "family_id",
        "record_mode",
        "destination",
        "family_type",
        "primary_i_can_id",
        "primary_i_can",
        "supporting_i_can_ids",
        "evidence_job",
        "intended_reasoning",
        "question_structure_id",
        "response_mode",
        "representation_mode",
        "representation_need",
        "difficulty_intent",
        "security_level",
        "selection_tags",
        "locked_elements",
        "allowed_variations",
        "required_variations",
        "forbidden_variations",
        "representation_variation_rule",
    )

    for fid in sorted(expected_ids & actual_ids):
        map_rec = map_by_id[fid]
        fam, rel, _ = authored_by_id[fid]
        # tolerate record_id-only map legacy while family_id is canonical authored field
        if fam.get("family_id") != fid:
            add(findings, "FAMILY_ID_DRIFT", f"family_id must be {fid}", family_id=fid, path=rel)
        for field in exact_fields:
            if field == "family_id" and field not in map_rec:
                continue
            compare_field(map_rec, fam, field, findings, rel)

        if fam.get("source_map_record_id") != (map_rec.get("record_id") or fid):
            add(findings, "SOURCE_MAP_ID_MISMATCH", "source_map_record_id does not match accepted map record", family_id=fid, path=rel)
        if not isinstance(fam.get("source_basis"), list) or not fam.get("source_basis"):
            add(findings, "SOURCE_BASIS_MISSING", "Practice family has no source_basis", family_id=fid, path=rel)

        qd = fam.get("question_design")
        if not isinstance(qd, dict):
            add(findings, "QUESTION_DESIGN_MISSING", "Practice family has no question_design object", family_id=fid, path=rel)
        elif qd.get("design_slot_id") != map_rec.get("design_slot_id"):
            add(findings, "DESIGN_SLOT_DRIFT", f"question_design.design_slot_id must be {map_rec.get('design_slot_id')!r}", family_id=fid, path=rel)

        seed = fam.get("canonical_seed")
        if not isinstance(seed, dict):
            add(findings, "CANONICAL_SEED_MISSING", "Practice family has no canonical_seed object", family_id=fid, path=rel)
            continue
        check_seed_nonempty(seed, findings, fid, rel)
        check_selected_response(map_rec, seed, findings, fid, rel)
        check_representation(root, map_rec, seed, findings, fid, rel)

    # Section counts and family-type mix must match the accepted map exactly.
    map_section_counts = Counter(str(r.get("scope") or r.get("section") or "") for r in map_records)
    authored_section_counts = Counter(str(v[0].get("section") or v[0].get("scope") or "") for v in authored_by_id.values())
    if map_section_counts != authored_section_counts:
        add(findings, "SECTION_COUNT_MISMATCH", f"Practice section counts differ from map: expected {dict(map_section_counts)}; got {dict(authored_section_counts)}")

    map_mix: dict[str, Counter[str]] = defaultdict(Counter)
    actual_mix: dict[str, Counter[str]] = defaultdict(Counter)
    for rec in map_records:
        map_mix[str(rec.get("scope") or rec.get("section") or "")][str(rec.get("family_type") or "")] += 1
    for fam, _, _ in authored_by_id.values():
        actual_mix[str(fam.get("section") or fam.get("scope") or "")][str(fam.get("family_type") or "")] += 1
    if {k: dict(v) for k, v in map_mix.items()} != {k: dict(v) for k, v in actual_mix.items()}:
        add(findings, "FAMILY_MIX_MISMATCH", f"Practice family-type mix differs from map: expected { {k: dict(v) for k,v in map_mix.items()} }; got { {k: dict(v) for k,v in actual_mix.items()} }")

    map_count = ((map_manifest.get("counts") or {}).get("practice_families") if isinstance(map_manifest, dict) else None)
    if isinstance(map_count, int) and map_count != len(map_records):
        add(findings, "MAP_MANIFEST_COUNT_MISMATCH", f"MAP_MANIFEST practice_families={map_count}, practice_map has {len(map_records)}")

    # ITEM_INDEX: every authored family exactly once, with correct path/index/mode.
    items = item_index.get("items") if isinstance(item_index, dict) else None
    if not isinstance(items, list):
        add(findings, "ITEM_INDEX_INVALID", "ITEM_INDEX.json has no items[]")
        items = []
    index_family_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in items:
        if isinstance(entry, dict):
            iid = str(entry.get("item_id") or entry.get("family_id") or "")
            if iid in expected_ids:
                index_family_entries[iid].append(entry)
    for fid in sorted(expected_ids):
        entries = index_family_entries.get(fid, [])
        if len(entries) != 1:
            add(findings, "ITEM_INDEX_FAMILY_COUNT", f"ITEM_INDEX must contain family exactly once; found {len(entries)}", family_id=fid)
            continue
        fam, rel, idx = authored_by_id.get(fid, ({}, "", -1))
        ent = entries[0]
        if ent.get("path") != rel:
            add(findings, "ITEM_INDEX_PATH_MISMATCH", f"ITEM_INDEX path expected {rel!r}; got {ent.get('path')!r}", family_id=fid)
        if ent.get("record_index") != idx:
            add(findings, "ITEM_INDEX_RECORD_INDEX_MISMATCH", f"ITEM_INDEX record_index expected {idx}; got {ent.get('record_index')!r}", family_id=fid)
        if ent.get("record_mode") != "family_seed":
            add(findings, "ITEM_INDEX_MODE_MISMATCH", "ITEM_INDEX record_mode must be family_seed", family_id=fid)
    if isinstance(item_index.get("record_count"), int) and item_index.get("record_count") != len(items):
        add(findings, "ITEM_INDEX_TOTAL_MISMATCH", f"ITEM_INDEX record_count={item_index.get('record_count')} but items has {len(items)} entries")

    # BANK_MANIFEST state after 3B.
    if manifest.get("status") != "BUILDING":
        add(findings, "MANIFEST_STATUS", "BANK_MANIFEST status must remain BUILDING after 3B")
    if manifest.get("ready_for_downstream") is not False:
        add(findings, "MANIFEST_READY_FLAG", "BANK_MANIFEST ready_for_downstream must remain false after 3B")
    completed = manifest.get("completed")
    if not isinstance(completed, list) or "3A_instructional_core" not in completed or "3B_practice_families" not in completed:
        add(findings, "MANIFEST_COMPLETED", "BANK_MANIFEST completed must include 3A_instructional_core and 3B_practice_families")
    pending = manifest.get("pending")
    if not isinstance(pending, list) or "3C_assessment_families" not in pending or "3B_practice_families" in pending:
        add(findings, "MANIFEST_PENDING", "BANK_MANIFEST pending must contain 3C and no longer contain 3B")
    if manifest.get("next_phase") != "3C_assessment_families":
        add(findings, "MANIFEST_NEXT_PHASE", "BANK_MANIFEST next_phase must be 3C_assessment_families")

    accepted = manifest.get("accepted_bank_map") if isinstance(manifest, dict) else None
    map_fp = map_manifest.get("map_fingerprint") if isinstance(map_manifest, dict) else None
    if isinstance(accepted, dict) and map_fp and accepted.get("map_fingerprint") != map_fp:
        add(findings, "MAP_FINGERPRINT_DRIFT", "BANK_MANIFEST accepted map fingerprint differs from MAP_MANIFEST")

    report = {
        "schema": REPORT_SCHEMA,
        "tool_version": TOOL_VERSION,
        "unit": args.unit,
        "scope": "mechanical Practice-family contracts only; semantic/content QA is separate",
        "status": "PASS" if not findings else "FAIL",
        "expected_families": len(map_records),
        "authored_families": len(authored_by_id),
        "findings": [asdict(x) for x in findings],
    }

    if args.json_report:
        out = Path(args.json_report)
        if not out.is_absolute():
            out = Path.cwd() / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if findings:
        print(f"Bank 3B deterministic contract: FAIL (unit {args.unit}; {len(authored_by_id)}/{len(map_records)} Practice families)")
        for f in findings:
            where = f" [{f.family_id}]" if f.family_id else ""
            path = f" ({f.path})" if f.path else ""
            print(f"ERROR: {f.code}{where}{path}: {f.message}")
        print("Scope: mechanical Practice-family contracts only; semantic/content QA is a separate pass.")
        return 1

    print(f"Bank 3B deterministic contract: PASS (unit {args.unit}; {len(authored_by_id)}/{len(map_records)} Practice families)")
    print("Scope: mechanical Practice-family contracts only; semantic/content QA is a separate pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
