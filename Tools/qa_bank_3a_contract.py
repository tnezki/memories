#!/usr/bin/env python3
"""Deterministic contract validator for Bank-v2 Stage 3A.

Checks only mechanically decidable contracts. It intentionally does NOT judge
physics quality, instructional quality, WTC difficulty, or whether a prompt
semantically fulfills a claimed reasoning move. Those belong in separate passes.

Exit codes:
  0 PASS
  1 FAIL (contract errors found)
  2 usage/input error
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

TOOL_VERSION = "1.0.0"
REPORT_SCHEMA = "bank-3a-contract-qa/1.0"


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    item_id: str = ""
    path: str = ""


def norm_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = html_lib.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def iter_dicts(node: Any) -> Iterable[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from iter_dicts(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_dicts(value)


def collect_map_records(data: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for obj in iter_dicts(data):
        if obj.get("record_mode") == "exact_content" and obj.get("record_id"):
            out.append(obj)
    return out


def get_records_from_slice(data: Any, path: Path) -> list[dict[str, Any]]:
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list):
        raise ValueError(f"expected top-level records[] in authored slice: {path}")
    bad = [i for i, r in enumerate(records) if not isinstance(r, dict)]
    if bad:
        raise ValueError(f"non-object records in {path} at indexes {bad}")
    return records


def add(findings: list[Finding], code: str, message: str, *, item_id: str = "", path: str = "") -> None:
    findings.append(Finding(code=code, message=message, item_id=item_id, path=path))


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


def check_nonempty_content(rec: dict[str, Any], findings: list[Finding], rel_path: str) -> None:
    iid = str(rec.get("item_id", ""))
    for key in ("student_text", "student_html", "answer", "solution_text", "solution_html"):
        value = rec.get(key)
        if not isinstance(value, str) or not value.strip():
            add(findings, "CONTENT_EMPTY", f"required field {key} is empty", item_id=iid, path=rel_path)
        elif value.strip().lower() in {"todo", "tbd", "placeholder", "lorem ipsum"}:
            add(findings, "CONTENT_PLACEHOLDER", f"required field {key} is a placeholder", item_id=iid, path=rel_path)


def check_selected_response(map_rec: dict[str, Any], rec: dict[str, Any], findings: list[Finding], rel_path: str) -> None:
    iid = str(rec.get("item_id", ""))
    if rec.get("response_mode") != "selected_response":
        return
    choices = rec.get("choices")
    if not isinstance(choices, list) or not choices:
        add(findings, "SR_CHOICES_MISSING", "selected_response item has no stored choices", item_id=iid, path=rel_path)
        return

    expected_count = map_rec.get("choice_count")
    if isinstance(expected_count, int) and len(choices) != expected_count:
        add(findings, "SR_CHOICE_COUNT", f"expected {expected_count} choices from map; found {len(choices)}", item_id=iid, path=rel_path)

    ids: list[str] = []
    texts: list[str] = []
    for i, choice in enumerate(choices):
        if not isinstance(choice, dict):
            add(findings, "SR_CHOICE_SHAPE", f"choice index {i} is not an object", item_id=iid, path=rel_path)
            continue
        cid = norm_text(choice.get("id"))
        ctext = norm_text(choice.get("text"))
        if not cid or not ctext:
            add(findings, "SR_CHOICE_EMPTY", f"choice index {i} has empty id/text", item_id=iid, path=rel_path)
        ids.append(cid)
        texts.append(ctext)

    for duplicate in sorted(k for k, v in Counter(ids).items() if k and v > 1):
        add(findings, "SR_DUPLICATE_ID", f"duplicate choice id {duplicate!r}", item_id=iid, path=rel_path)
    normed_texts = [t.casefold() for t in texts if t]
    for duplicate in sorted(k for k, v in Counter(normed_texts).items() if k and v > 1):
        add(findings, "SR_DUPLICATE_TEXT", f"duplicate choice text {duplicate!r}", item_id=iid, path=rel_path)

    correct = norm_text(rec.get("correct_choice"))
    if not correct:
        add(findings, "SR_KEY_MISSING", "selected_response item has no correct_choice", item_id=iid, path=rel_path)
    elif correct not in ids:
        add(findings, "SR_KEY_INVALID", f"correct_choice {correct!r} is not a stored choice id", item_id=iid, path=rel_path)

    student_html = str(rec.get("student_html") or "")
    if not has_class(student_html, "ol", "choices") and not has_class(student_html, "ul", "choices"):
        add(findings, "SR_CHOICES_NOT_RENDERED", "student_html has no list with class choices", item_id=iid, path=rel_path)
    rendered = visible_html_text(student_html).casefold()
    for choice_text in texts:
        if choice_text and choice_text.casefold() not in rendered:
            add(findings, "SR_CHOICE_NOT_VISIBLE", f"stored choice not visible in student_html: {choice_text!r}", item_id=iid, path=rel_path)

    if correct in ids:
        keyed_text = texts[ids.index(correct)] if ids.index(correct) < len(texts) else ""
        answer = norm_text(rec.get("answer"))
        if keyed_text and answer and keyed_text.casefold() not in answer.casefold() and answer.casefold() != correct.casefold():
            add(findings, "SR_ANSWER_KEY_MISMATCH", f"answer {answer!r} does not include keyed choice {correct}: {keyed_text!r}", item_id=iid, path=rel_path)


def table_required(map_rec: dict[str, Any], rec: dict[str, Any]) -> bool:
    mode = str(rec.get("representation_mode") or map_rec.get("representation_mode") or "")
    route = map_rec.get("representation_route") or map_rec.get("render_contract") or {}
    route_type = route.get("route_type") if isinstance(route, dict) else ""
    return mode == "semantic_data_table" or route_type == "semantic_html_table" or bool(rec.get("tables"))


def check_table(map_rec: dict[str, Any], rec: dict[str, Any], findings: list[Finding], rel_path: str) -> None:
    if not table_required(map_rec, rec):
        return
    iid = str(rec.get("item_id", ""))
    student_html = str(rec.get("student_html") or "")
    if not re.search(r"<table\b", student_html, flags=re.I):
        add(findings, "TABLE_HTML_MISSING", "table representation has no <table> in student_html", item_id=iid, path=rel_path)
    if not has_class(student_html, "table", "values"):
        add(findings, "TABLE_VALUES_CLASS_MISSING", "table representation does not use class values", item_id=iid, path=rel_path)
    tables = rec.get("tables")
    if not isinstance(tables, list) or not tables:
        add(findings, "TABLE_PAYLOAD_MISSING", "table representation has no tables payload", item_id=iid, path=rel_path)
        return
    rendered = visible_html_text(student_html).casefold()
    for ti, table in enumerate(tables):
        if not isinstance(table, dict):
            add(findings, "TABLE_PAYLOAD_SHAPE", f"table payload {ti} is not an object", item_id=iid, path=rel_path)
            continue
        headers = table.get("headers")
        rows = table.get("rows")
        if not isinstance(headers, list) or not headers or any(not norm_text(h) for h in headers):
            add(findings, "TABLE_HEADERS_INVALID", f"table payload {ti} has missing/empty headers", item_id=iid, path=rel_path)
        else:
            for header in headers:
                ht = norm_text(header)
                if ht and ht.casefold() not in rendered:
                    add(findings, "TABLE_HEADER_NOT_VISIBLE", f"header not visible in student_html: {ht!r}", item_id=iid, path=rel_path)
        if not isinstance(rows, list) or not rows:
            add(findings, "TABLE_ROWS_INVALID", f"table payload {ti} has no rows", item_id=iid, path=rel_path)


def route_for(map_rec: dict[str, Any]) -> dict[str, Any]:
    route = map_rec.get("representation_route")
    if isinstance(route, dict):
        return route
    render = map_rec.get("render_contract")
    if isinstance(render, dict) and render.get("route_type"):
        return render
    return {}


def check_representation(course_root: Path, map_rec: dict[str, Any], rec: dict[str, Any], findings: list[Finding], rel_path: str) -> None:
    iid = str(rec.get("item_id", ""))
    mode = str(rec.get("representation_mode") or "")
    student_html = str(rec.get("student_html") or "")
    route = route_for(map_rec)
    route_type = str(route.get("route_type") or "")

    if route_type == "canonical_asset":
        canonical = norm_text(route.get("canonical_path"))
        asset_id = norm_text(route.get("asset_id"))
        if not canonical:
            add(findings, "ASSET_PATH_MISSING", "canonical_asset route has no canonical_path", item_id=iid, path=rel_path)
        else:
            if not (course_root / canonical).is_file():
                add(findings, "ASSET_FILE_MISSING", f"canonical asset does not exist: {canonical}", item_id=iid, path=rel_path)
            refs = rec.get("figure_refs")
            if not isinstance(refs, list) or canonical not in refs:
                add(findings, "ASSET_REF_MISSING", f"figure_refs does not contain canonical asset {canonical}", item_id=iid, path=rel_path)
            if Path(canonical).name not in student_html and canonical not in student_html:
                add(findings, "ASSET_NOT_RENDERED", f"student_html does not reference canonical asset {canonical}", item_id=iid, path=rel_path)
        figures = rec.get("figures")
        if not isinstance(figures, list) or not figures:
            add(findings, "ASSET_PAYLOAD_MISSING", "canonical asset item has no figures payload", item_id=iid, path=rel_path)
        else:
            matches = [f for f in figures if isinstance(f, dict) and (not canonical or f.get("file") == canonical)]
            if not matches:
                add(findings, "ASSET_PAYLOAD_PATH_MISMATCH", "figures payload does not match canonical path", item_id=iid, path=rel_path)
            elif asset_id and not any(norm_text(f.get("asset_id")) == asset_id for f in matches):
                add(findings, "ASSET_ID_MISMATCH", f"figures payload does not preserve asset_id {asset_id}", item_id=iid, path=rel_path)

    if route_type == "student_constructed" or mode.startswith("student_constructed"):
        if not has_class(student_html, "div", "response-surface"):
            add(findings, "CONSTRUCTED_SURFACE_MISSING", "student-constructed representation has no response-surface div", item_id=iid, path=rel_path)
        refs = rec.get("representation_refs")
        if not isinstance(refs, list) or not any(isinstance(r, dict) and str(r.get("type", "")).startswith("student_constructed") for r in refs):
            add(findings, "CONSTRUCTED_REF_MISSING", "student-constructed representation has no student_constructed representation_ref", item_id=iid, path=rel_path)

    if route_type == "registered_tool":
        tool_key = norm_text(route.get("tool_key") or route.get("tool"))
        if not tool_key:
            add(findings, "REGISTERED_TOOL_KEY_MISSING", "registered_tool route has no tool_key", item_id=iid, path=rel_path)
        refs = rec.get("representation_refs")
        if not isinstance(refs, list) or not refs:
            add(findings, "REGISTERED_TOOL_OUTPUT_REF_MISSING", "registered_tool item has no representation_refs", item_id=iid, path=rel_path)

    if mode == "equation_relationship" and not any(token in student_html for token in ("\\(", "\\[", "$$")):
        add(findings, "EQUATION_NOT_RENDERED", "equation_relationship item has no MathJax delimiter in student_html", item_id=iid, path=rel_path)

    rep_need = str(map_rec.get("representation_need") or "")
    if rep_need == "required" and mode not in {"", "direct_text"}:
        visible_marker = (
            re.search(r"<(?:img|svg|table)\b", student_html, flags=re.I)
            or "response-surface" in student_html
            or any(token in student_html for token in ("\\(", "\\[", "$$"))
        )
        if not visible_marker:
            add(findings, "REQUIRED_REPRESENTATION_NOT_VISIBLE", f"required representation_mode {mode!r} has no visible render marker", item_id=iid, path=rel_path)


def check_wtc(map_rec: dict[str, Any], rec: dict[str, Any], findings: list[Finding], rel_path: str) -> None:
    if str(rec.get("destination")) != "WTC":
        return
    iid = str(rec.get("item_id", ""))
    text = str(rec.get("student_text") or "")
    parts = re.findall(r"(?m)^\s*\(([a-e])\)\s+", text)
    if not (3 <= len(parts) <= 5):
        add(findings, "WTC_PART_COUNT", f"WTC must have 3-5 labeled parts; found {len(parts)}", item_id=iid, path=rel_path)
    if len(parts) != len(set(parts)):
        add(findings, "WTC_DUPLICATE_PART_LABEL", f"WTC has duplicate part labels: {parts}", item_id=iid, path=rel_path)
    declared = rec.get("wtc_part_count")
    if isinstance(declared, int) and declared != len(parts):
        add(findings, "WTC_DECLARED_COUNT_MISMATCH", f"wtc_part_count={declared}, actual labeled parts={len(parts)}", item_id=iid, path=rel_path)
    plan = map_rec.get("parts_plan") or map_rec.get("decomposition_move_plan")
    if isinstance(plan, list) and len(plan) != len(parts):
        add(findings, "WTC_MAP_PART_COUNT_MISMATCH", f"map plans {len(plan)} parts; authored prompt has {len(parts)}", item_id=iid, path=rel_path)
    if rec.get("coverage_role") != "wtc_frq_practice":
        add(findings, "WTC_COVERAGE_ROLE", "coverage_role must be wtc_frq_practice", item_id=iid, path=rel_path)
    if rec.get("coverage_counts_toward_unit_i_can_floor") is not False:
        add(findings, "WTC_COVERAGE_FLOOR", "WTC must not count toward current Unit I-can floor", item_id=iid, path=rel_path)
    if rec.get("wtc_frq") is not True:
        add(findings, "WTC_FRQ_FLAG", "wtc_frq must be true", item_id=iid, path=rel_path)
    if rec.get("wtc_shared_stimulus") is not True:
        add(findings, "WTC_SHARED_STIMULUS_FLAG", "wtc_shared_stimulus must be true", item_id=iid, path=rel_path)
    # Deliberately no semantic validation of the claimed WTC moves here.


def check_pairing(records: list[tuple[dict[str, Any], str]], findings: list[Finding]) -> None:
    pairs: dict[str, list[tuple[dict[str, Any], str]]] = defaultdict(list)
    for rec, path in records:
        if rec.get("destination") in {"EXAMPLE", "YTI"}:
            pid = norm_text(rec.get("pair_id"))
            if not pid:
                add(findings, "PAIR_ID_MISSING", "Example/YTI item has no pair_id", item_id=str(rec.get("item_id", "")), path=path)
                continue
            pairs[pid].append((rec, path))
    for pid in sorted(pairs):
        members = pairs[pid]
        roles = [norm_text(r.get("pair_role")).lower() for r, _ in members]
        if len(members) != 2 or Counter(roles) != Counter({"example": 1, "yti": 1}):
            add(findings, "PAIR_INCOMPLETE", f"pair {pid} must contain exactly one example and one yti; found roles={roles}")
        if len(members) == 2:
            a, b = members[0][0], members[1][0]
            for key in ("section", "primary_i_can_id", "evidence_job"):
                if a.get(key) != b.get(key):
                    add(findings, "PAIR_CONTRACT_MISMATCH", f"pair {pid} differs on {key}: {a.get(key)!r} vs {b.get(key)!r}")


def check_index(course_root: Path, unit_dir: Path, expected_ids: set[str], slice_records: dict[str, list[dict[str, Any]]], findings: list[Finding]) -> None:
    path = unit_dir / "ITEM_INDEX.json"
    rel_index = str(path.relative_to(course_root))
    if not path.is_file():
        add(findings, "INDEX_MISSING", "ITEM_INDEX.json is missing", path=rel_index)
        return
    try:
        data = load_json(path)
    except ValueError as exc:
        add(findings, "INDEX_INVALID", str(exc), path=rel_index)
        return
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        add(findings, "INDEX_ITEMS_MISSING", "ITEM_INDEX.json has no items[]", path=rel_index)
        return

    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in items:
        if isinstance(entry, dict) and entry.get("item_id") in expected_ids:
            by_id[str(entry.get("item_id"))].append(entry)
    for iid in sorted(expected_ids):
        entries = by_id.get(iid, [])
        if len(entries) != 1:
            add(findings, "INDEX_ENTRY_COUNT", f"expected exactly one index entry; found {len(entries)}", item_id=iid, path=rel_index)
            continue
        entry = entries[0]
        rel = norm_text(entry.get("path"))
        idx = entry.get("record_index")
        if rel not in slice_records:
            add(findings, "INDEX_PATH_INVALID", f"index path does not resolve to a loaded 3A slice: {rel!r}", item_id=iid, path=rel_index)
            continue
        if not isinstance(idx, int) or idx < 0 or idx >= len(slice_records[rel]):
            add(findings, "INDEX_RECORD_INDEX_INVALID", f"record_index {idx!r} invalid for {rel}", item_id=iid, path=rel_index)
            continue
        target = slice_records[rel][idx]
        if target.get("item_id") != iid:
            add(findings, "INDEX_TARGET_MISMATCH", f"index points to {target.get('item_id')!r} at {rel}[{idx}]", item_id=iid, path=rel_index)


def check_manifests(course_root: Path, map_dir: Path, unit_dir: Path, expected_counts: dict[str, int], findings: list[Finding]) -> None:
    map_manifest_path = map_dir / "MAP_MANIFEST.json"
    bank_manifest_path = unit_dir / "BANK_MANIFEST.json"
    try:
        mm = load_json(map_manifest_path)
    except ValueError as exc:
        add(findings, "MAP_MANIFEST_INVALID", str(exc), path=str(map_manifest_path.relative_to(course_root)))
        return
    try:
        bm = load_json(bank_manifest_path)
    except ValueError as exc:
        add(findings, "BANK_MANIFEST_INVALID", str(exc), path=str(bank_manifest_path.relative_to(course_root)))
        return

    if mm.get("status") != "PASS":
        add(findings, "MAP_STATUS_NOT_PASS", f"MAP_MANIFEST status is {mm.get('status')!r}", path=str(map_manifest_path.relative_to(course_root)))

    for declared_info in mm.get("files", []):
        if not isinstance(declared_info, dict) or not declared_info.get("path") or not declared_info.get("sha256"):
            continue
        declared = map_dir / str(declared_info["path"])
        if not declared.is_file():
            add(findings, "MAP_DECLARED_FILE_MISSING", f"declared map file missing: {declared_info['path']}", path=str(map_manifest_path.relative_to(course_root)))
            continue
        actual = sha256_file(declared)
        if actual != declared_info["sha256"]:
            add(findings, "MAP_FILE_HASH_MISMATCH", f"sha256 mismatch for {declared_info['path']}: manifest={declared_info['sha256']} actual={actual}", path=str(map_manifest_path.relative_to(course_root)))

    accepted = bm.get("accepted_bank_map") or {}
    if isinstance(accepted, dict):
        if accepted.get("map_fingerprint") != mm.get("map_fingerprint"):
            add(findings, "BANK_MAP_FINGERPRINT_MISMATCH", "BANK_MANIFEST accepted map fingerprint does not match MAP_MANIFEST", path=str(bank_manifest_path.relative_to(course_root)))
        qmap = map_dir / f"unit{mm.get('unit')}_question_design_map.json"
        if qmap.is_file() and accepted.get("question_design_map_sha256"):
            actual = sha256_file(qmap)
            if accepted.get("question_design_map_sha256") != actual:
                add(findings, "BANK_QMAP_HASH_MISMATCH", f"BANK_MANIFEST question_design_map_sha256 does not match actual file ({actual})", path=str(bank_manifest_path.relative_to(course_root)))

    completed = bm.get("completed")
    if not isinstance(completed, list) or "3A_instructional_core" not in completed:
        add(findings, "BANK_3A_NOT_COMPLETED", "BANK_MANIFEST.completed does not include 3A_instructional_core", path=str(bank_manifest_path.relative_to(course_root)))

    rc = bm.get("record_counts") or {}
    count_fields = {
        "stage_3a_total": expected_counts["total"],
        "wtc": expected_counts["wtc"],
        "notes_example": expected_counts["example"],
        "notes_yti": expected_counts["yti"],
        "cyu": expected_counts["cyu"],
        "warmups": expected_counts["warmup"],
    }
    if isinstance(rc, dict):
        for key, expected in count_fields.items():
            if key in rc and rc.get(key) != expected:
                add(findings, "BANK_COUNT_MISMATCH", f"BANK_MANIFEST record_counts.{key}={rc.get(key)!r}; expected {expected}", path=str(bank_manifest_path.relative_to(course_root)))


def compare_map_to_authored(course_root: Path, map_records: list[dict[str, Any]], authored: list[tuple[dict[str, Any], str]], findings: list[Finding]) -> None:
    map_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in map_records:
        map_by_id[str(rec.get("record_id"))].append(rec)
    authored_by_id: dict[str, list[tuple[dict[str, Any], str]]] = defaultdict(list)
    for rec, path in authored:
        authored_by_id[str(rec.get("item_id"))].append((rec, path))

    map_ids = set(map_by_id)
    authored_ids = set(authored_by_id)
    for iid in sorted(map_ids - authored_ids):
        add(findings, "AUTHORED_RECORD_MISSING", "mapped exact_content record was not authored", item_id=iid)
    for iid in sorted(authored_ids - map_ids):
        add(findings, "UNMAPPED_AUTHORED_RECORD", "authored 3A record has no exact_content map record", item_id=iid)

    for iid in sorted(map_ids & authored_ids):
        if len(map_by_id[iid]) != 1:
            add(findings, "MAP_DUPLICATE_ID", f"map contains {len(map_by_id[iid])} records with this ID", item_id=iid)
            continue
        if len(authored_by_id[iid]) != 1:
            add(findings, "AUTHORED_DUPLICATE_ID", f"authored Bank contains {len(authored_by_id[iid])} records with this ID", item_id=iid)
            continue
        m = map_by_id[iid][0]
        rec, rel_path = authored_by_id[iid][0]

        if rec.get("source_map_record_id") != iid:
            add(findings, "SOURCE_MAP_ID_MISMATCH", f"source_map_record_id={rec.get('source_map_record_id')!r}; expected {iid!r}", item_id=iid, path=rel_path)
        if rec.get("bank_id") not in {None, iid}:
            add(findings, "BANK_ID_MISMATCH", f"bank_id={rec.get('bank_id')!r}; expected {iid!r}", item_id=iid, path=rel_path)

        for key in (
            "record_mode", "destination", "primary_i_can_id", "primary_i_can",
            "supporting_i_can_ids", "evidence_job", "student_action",
            "question_structure_id", "response_mode", "representation_mode", "security_level",
        ):
            if key in m and rec.get(key) != m.get(key):
                add(findings, "MAP_FIELD_DRIFT", f"{key} drifted from map: map={m.get(key)!r}, authored={rec.get(key)!r}", item_id=iid, path=rel_path)

        expected_slot = m.get("design_slot_id") or m.get("slot_id") or iid
        qd = rec.get("question_design")
        if not isinstance(qd, dict):
            add(findings, "QUESTION_DESIGN_MISSING", "authored item has no question_design object", item_id=iid, path=rel_path)
        else:
            if qd.get("design_slot_id") != expected_slot:
                add(findings, "DESIGN_SLOT_MISMATCH", f"question_design.design_slot_id={qd.get('design_slot_id')!r}; expected {expected_slot!r}", item_id=iid, path=rel_path)
            for key in ("question_structure_id", "response_mode", "representation_mode"):
                expected = m.get(key)
                if expected is not None and qd.get(key) != expected:
                    add(findings, "QUESTION_DESIGN_DRIFT", f"question_design.{key}={qd.get(key)!r}; expected {expected!r}", item_id=iid, path=rel_path)
            if "representation_route" in m and qd.get("representation_route") != m.get("representation_route"):
                add(findings, "REPRESENTATION_ROUTE_DRIFT", "question_design.representation_route differs from accepted map", item_id=iid, path=rel_path)
            if "render_contract" in m and qd.get("render_contract") != m.get("render_contract"):
                add(findings, "RENDER_CONTRACT_DRIFT", "question_design.render_contract differs from accepted map", item_id=iid, path=rel_path)

        check_nonempty_content(rec, findings, rel_path)
        check_selected_response(m, rec, findings, rel_path)
        check_table(m, rec, findings, rel_path)
        check_representation(course_root, m, rec, findings, rel_path)
        check_wtc(m, rec, findings, rel_path)


def run(course_root: Path, unit: int) -> dict[str, Any]:
    findings: list[Finding] = []
    course_root = course_root.resolve()
    map_dir = course_root / "banks" / f"unit{unit}_bank_map"
    unit_dir = course_root / "banks" / f"unit{unit}"

    if not course_root.is_dir():
        raise ValueError(f"course root is not a directory: {course_root}")
    if not map_dir.is_dir():
        raise ValueError(f"Bank Map directory is missing: {map_dir}")
    if not unit_dir.is_dir():
        raise ValueError(f"Bank directory is missing: {unit_dir}")

    map_records: list[dict[str, Any]] = []
    for name in ("notes_map.json", "cyu_map.json", "warmup_map.json"):
        map_records.extend(collect_map_records(load_json(map_dir / name)))

    bank_slice_paths: list[Path] = []
    for subdir in ("notes", "cyu", "warmups"):
        directory = unit_dir / subdir
        if not directory.is_dir():
            rel = str(directory.relative_to(course_root))
            add(findings, "BANK_SLICE_DIR_MISSING", f"required 3A directory is missing: {rel}", path=rel)
            continue
        bank_slice_paths.extend(sorted(directory.glob("section_*.json")))

    authored: list[tuple[dict[str, Any], str]] = []
    slice_records: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(bank_slice_paths):
        records = get_records_from_slice(load_json(path), path)
        rel_from_unit = str(path.relative_to(unit_dir)).replace("\\", "/")
        slice_records[rel_from_unit] = records
        authored.extend((rec, rel_from_unit) for rec in records)

    compare_map_to_authored(course_root, map_records, authored, findings)
    check_pairing(authored, findings)
    expected_ids = {str(rec.get("record_id")) for rec in map_records if rec.get("record_id")}
    check_index(course_root, unit_dir, expected_ids, slice_records, findings)

    counts = {
        "total": len(map_records),
        "wtc": sum(1 for rec in map_records if rec.get("destination") == "WTC"),
        "example": sum(1 for rec in map_records if rec.get("destination") == "EXAMPLE"),
        "yti": sum(1 for rec in map_records if rec.get("destination") == "YTI"),
        "cyu": sum(1 for rec in map_records if rec.get("destination") == "CYU"),
        "warmup": sum(1 for rec in map_records if rec.get("destination") == "WARM_UP"),
    }
    check_manifests(course_root, map_dir, unit_dir, counts, findings)

    findings = sorted(findings, key=lambda f: (f.code, f.item_id, f.path, f.message))
    return {
        "schema": REPORT_SCHEMA,
        "tool": "qa_bank_3a_contract",
        "tool_version": TOOL_VERSION,
        "status": "FAIL" if findings else "PASS",
        "course_root": str(course_root),
        "unit": unit,
        "checked": {
            "mapped_exact_content_records": len(map_records),
            "authored_3a_records": len(authored),
            "wtc": counts["wtc"],
            "example": counts["example"],
            "yti": counts["yti"],
            "cyu": counts["cyu"],
            "warmup": counts["warmup"],
        },
        "scope_note": (
            "Mechanical contract pass only. This result does not certify physics correctness, "
            "semantic evidence alignment, WTC reasoning-move truth, difficulty, or instructional quality."
        ),
        "findings": [asdict(f) for f in findings],
    }


def print_human(report: dict[str, Any]) -> None:
    checked = report["checked"]
    print(
        f"Bank 3A deterministic contract: {report['status']} "
        f"(unit {report['unit']}; {checked['authored_3a_records']}/{checked['mapped_exact_content_records']} authored records)"
    )
    for finding in report["findings"]:
        prefix = finding["code"]
        if finding.get("item_id"):
            prefix += f" [{finding['item_id']}]"
        if finding.get("path"):
            prefix += f" ({finding['path']})"
        print(f"ERROR: {prefix}: {finding['message']}")
    print("Scope: mechanical contracts only; semantic/content QA is a separate pass.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate mechanically decidable Bank-v2 Stage 3A contracts.")
    parser.add_argument("course_root", help="Path to the course repository root.")
    parser.add_argument("--unit", type=int, required=True, help="Unit number to validate.")
    parser.add_argument("--json-report", help="Optional output path for a deterministic JSON report.")
    args = parser.parse_args(argv)

    try:
        report = run(Path(args.course_root), args.unit)
    except ValueError as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2

    print_human(report)
    if args.json_report:
        out = Path(args.json_report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
