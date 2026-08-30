#!/usr/bin/env python3
"""Mechanical Bank -> 4A -> 4B Notes handoff validator."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_SCHEMA = "physics-notes-map/2.0"
EXPECTED_REVISION = "bank-v2-textbook-chunks-v2"
CURRENT_ROUTE = "bank-notes-route/1.0"
LEGACY_ROUTE = "legacy-paths-notes/1.0"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def blob_sha(p):
    b = p.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()

def err(out, code, msg):
    out.append({"code": code, "message": msg})

def pair_routes(section):
    out = []
    for ch in section.get("ordered_flow", []):
        p = ch.get("primary_processing_after")
        if isinstance(p, dict) and p.get("type") == "ex_yti":
            out.append(p)
    out.extend([p for p in section.get("post_reading_ex_yti_queue", []) if isinstance(p, dict)])
    return out

def opening(section):
    return section.get("opening") or section.get("opening_contract") or {}

def route_item(p, kind):
    if kind == "example":
        return p.get("example_item_id") or p.get("example_id")
    return p.get("yti_item_id") or p.get("yti_id")

def validate(root: Path, unit: int, map_path: Path):
    errors = []
    base = root / f"banks/unit{unit}"
    mp = base / "BANK_MANIFEST.json"
    ip = base / "ITEM_INDEX.json"
    if not mp.exists(): err(errors, "BANK_MANIFEST_MISSING", str(mp)); return errors
    if not ip.exists(): err(errors, "ITEM_INDEX_MISSING", str(ip)); return errors
    if not map_path.exists(): err(errors, "MAP_MISSING", str(map_path)); return errors

    manifest, index, m = load(mp), load(ip), load(map_path)
    if manifest.get("status") != "COMPLETE" or manifest.get("ready_for_downstream") is not True:
        err(errors, "BANK_NOT_READY", "Bank must be COMPLETE and ready_for_downstream=true")

    route = ((manifest.get("paths") or {}).get("notes"))
    if not route:
        err(errors, "BANK_NOTES_ROUTE_MISSING", "BANK_MANIFEST.paths.notes missing")
        route = ""

    hs = ((manifest.get("downstream_contracts") or {}).get("notes_route") or {})
    declared = hs.get("schema")
    recorded = m.get("bank_notes_route_contract_schema")
    if declared:
        if declared != CURRENT_ROUTE:
            err(errors, "SYSTEM_CONTRACT_MISMATCH",
                f"Bank declares unsupported Notes route schema {declared!r}; supported={CURRENT_ROUTE!r}")
        if recorded != declared:
            err(errors, "ROUTE_SCHEMA_DRIFT", f"map={recorded!r}, Bank={declared!r}")
        if hs.get("route_field") != "paths.notes":
            err(errors, "ROUTE_FIELD_DRIFT", "Bank notes route_field must be 'paths.notes'")
        if hs.get("route_template") != route:
            err(errors, "ROUTE_TEMPLATE_HANDSHAKE_DRIFT", "handshake route_template != paths.notes")
    elif recorded != LEGACY_ROUTE:
        err(errors, "LEGACY_ROUTE_SCHEMA_REQUIRED",
            f"legacy finalized Bank requires map bank_notes_route_contract_schema={LEGACY_ROUTE!r}")

    if m.get("schema") != EXPECTED_SCHEMA:
        err(errors, "MAP_SCHEMA", f"schema must be {EXPECTED_SCHEMA}")
    if m.get("notes_flow_revision") != EXPECTED_REVISION:
        err(errors, "FLOW_REVISION",
            f"notes_flow_revision must be {EXPECTED_REVISION!r}; found {m.get('notes_flow_revision')!r}")
    if m.get("bank_manifest_path") != f"banks/unit{unit}/BANK_MANIFEST.json":
        err(errors, "BANK_MANIFEST_PATH", "wrong/missing bank_manifest_path")
    if m.get("bank_manifest_blob_sha") != blob_sha(mp):
        err(errors, "BANK_MANIFEST_BLOB", "bank_manifest_blob_sha does not match consumed Bank manifest")
    if m.get("bank_notes_route_template") != route:
        err(errors, "BANK_ROUTE_TEMPLATE", "bank_notes_route_template != BANK_MANIFEST.paths.notes")

    idx = {}
    for it in index.get("items", []):
        if str(it.get("destination", "")).upper() not in {"WTC", "EXAMPLE", "YTI"}:
            continue
        sid = str(it.get("section", ""))
        idx.setdefault(sid, {"paths": set(), "ids": set()})
        idx[sid]["paths"].add(str(it.get("path", "")))
        idx[sid]["ids"].add(str(it.get("item_id", "")))

    sections = m.get("sections", [])
    section_ids = [str(s.get("section_id", "")) for s in sections if isinstance(s, dict)]
    if set(section_ids) != set(idx) or len(section_ids) != len(set(section_ids)):
        err(errors, "SECTION_SET", f"map sections {sorted(section_ids)} != Bank Notes sections {sorted(idx)}")

    for s in sections:
        sid = str(s.get("section_id", ""))
        rel = route.replace("<section-id>", sid) if "<section-id>" in route else ""
        full_rel = f"banks/unit{unit}/{rel}" if rel else ""
        if s.get("bank_notes_path") != full_rel:
            err(errors, "SECTION_BANK_PATH", f"[{sid}] expected {full_rel!r}")
        f = root / full_rel if full_rel else None
        if not f or not f.exists():
            err(errors, "SECTION_BANK_FILE", f"[{sid}] missing {full_rel}")
            continue
        if s.get("bank_notes_blob_sha") != blob_sha(f):
            err(errors, "SECTION_BANK_BLOB", f"[{sid}] bank_notes_blob_sha mismatch")
        if idx.get(sid, {}).get("paths") != {rel}:
            err(errors, "ITEM_INDEX_ROUTE", f"[{sid}] ITEM_INDEX Notes routes do not equal {rel!r}")

        records = load(f).get("records", [])
        bank_wtc = [r.get("item_id") for r in records if str(r.get("destination","")).upper()=="WTC"]
        op = opening(s)
        wtc = op.get("wtc", {}) if isinstance(op, dict) else {}
        map_wtc = (wtc.get("item_id") or wtc.get("bank_id")) if isinstance(wtc, dict) else None
        if len(bank_wtc) != 1 or map_wtc != bank_wtc[0]:
            err(errors, "WTC_IDENTITY", f"[{sid}] mapped WTC {map_wtc!r} != Bank {bank_wtc!r}")

        pairs = {}
        for r in records:
            pid, role = r.get("pair_id"), str(r.get("pair_role","")).lower()
            if pid and role in {"example","yti"}:
                pairs.setdefault(pid, {})[role] = r.get("item_id")
        routes = pair_routes(s)
        seen = {}
        for p in routes:
            if p.get("pair_id"):
                seen.setdefault(p["pair_id"], []).append(p)
        if set(seen) != set(pairs):
            err(errors, "PAIR_SET", f"[{sid}] mapped pair set != Bank pair set")
        for pid, roles in pairs.items():
            rs = seen.get(pid, [])
            if len(rs) != 1:
                err(errors, "PAIR_ROUTE_COUNT", f"[{sid}] {pid} routed {len(rs)} times")
                continue
            p = rs[0]
            if route_item(p,"example") != roles.get("example") or route_item(p,"yti") != roles.get("yti"):
                err(errors, "PAIR_IDENTITY", f"[{sid}] {pid} example/YTI identity drift")
        nums = sorted(p.get("display_pair_number") for p in routes if isinstance(p.get("display_pair_number"), int))
        if nums != list(range(1, len(pairs)+1)):
            err(errors, "DISPLAY_PAIR_NUMBERS", f"[{sid}] expected 1..{len(pairs)}, found {nums}")

        if not s.get("what_i_figured_out_target"):
            err(errors, "WHAT_I_FIGURED_OUT", f"[{sid}] missing what_i_figured_out_target")
        if "generated_representation_needs" not in s:
            err(errors, "GENERATED_REPRESENTATION_NEEDS", f"[{sid}] missing generated_representation_needs")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_repo_root")
    ap.add_argument("--unit", type=int, required=True)
    ap.add_argument("--map", dest="map_path", required=True)
    ap.add_argument("--json-report")
    a = ap.parse_args()
    root = Path(a.course_repo_root).resolve()
    mp = Path(a.map_path).resolve()
    errors = validate(root, a.unit, mp)
    report = {
        "schema": "notes-4a-contract-qa/1.0",
        "status": "PASS" if not errors else "FAIL",
        "unit": a.unit,
        "scope": "mechanical Bank -> 4A -> 4B handoff only",
        "errors": errors,
    }
    if a.json_report:
        p = Path(a.json_report)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(f"Notes 4A deterministic contract: FAIL (unit {a.unit})")
        for e in errors:
            print(f"ERROR: {e['code']}: {e['message']}")
        print("Scope: mechanical handoff only; instructional/source-quality QA is separate.")
        raise SystemExit(1)
    print(f"Notes 4A deterministic contract: PASS (unit {a.unit})")
    print("Scope: mechanical handoff only; instructional/source-quality QA is separate.")

if __name__ == "__main__":
    main()
