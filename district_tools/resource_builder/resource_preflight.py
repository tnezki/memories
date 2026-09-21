#!/usr/bin/env python3
"""Deterministic preflight for District Resource Builder request packages."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

VERSION = "district-resource-preflight/1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-root", default=".")
    ap.add_argument("--out", default="work/resource_preflight.json")
    args = ap.parse_args()
    root = Path(args.request_root).resolve()
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    failures = []
    checks = {}

    req_path = root / "request.json"
    try:
        request = json.loads(req_path.read_text(encoding="utf-8"))
        checks["request_json"] = {"status": "PASS"}
    except Exception as exc:
        request = {}
        failures.append("request_json")
        checks["request_json"] = {"status": "FAIL", "error": str(exc)}

    required = [
        "response_contract/RESOURCE_BUILDER_CONTRACT.md",
        "response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md",
        "response_contract/RESOURCE_BUILD_EXECUTION.md",
        "response_contract/SELECTED_PROFILE.json",
        "response_contract/dashboard_styles.css",
        "response_contract/resource_styles.css",
        "response_contract/resource_preflight.py",
        "response_contract/resource_finalize.py",
        "response_contract/resource_qa.py",
        "response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md",
        "response_contract/graph_tool/MANIFEST.json",
    ]
    graph_ep = (request.get("graph_rendering") or {}).get("packaged_entrypoint")
    if graph_ep:
        required.append(graph_ep)
    missing = [p for p in required if not (root / p).exists()]
    checks["packaged_dependencies"] = {"status": "PASS" if not missing else "FAIL", "missing": missing}
    if missing:
        failures.append("packaged_dependencies")

    for key in ("dashboard", "resource"):
        meta = (request.get("locked_styles") or {}).get(key) or {}
        p = root / str(meta.get("request_path") or "")
        expected = meta.get("sha256")
        actual = sha256(p) if p.exists() else None
        ok = bool(expected and actual == expected)
        checks[f"style_{key}"] = {"status": "PASS" if ok else "FAIL", "expected": expected, "actual": actual}
        if not ok:
            failures.append(f"style_{key}")

    for key in ("preflight", "finalize", "qa"):
        meta = (request.get("deterministic_tools") or {}).get(key) or {}
        p = root / str(meta.get("path") or "")
        expected = meta.get("sha256")
        actual = sha256(p) if p.exists() else None
        ok = bool(expected and actual == expected)
        checks[f"tool_{key}"] = {"status": "PASS" if ok else "FAIL", "expected": expected, "actual": actual}
        if not ok:
            failures.append(f"tool_{key}")

    gm = request.get("graph_rendering") or {}
    gp = root / str(gm.get("packaged_entrypoint") or "")
    expected = gm.get("sha256")
    actual = sha256(gp) if gp.exists() else None
    ok = bool(expected and actual == expected)
    checks["graph_tool"] = {"status": "PASS" if ok else "FAIL", "expected": expected, "actual": actual, "path": str(gm.get("packaged_entrypoint") or "")}
    if not ok:
        failures.append("graph_tool")

    source_rows = []
    for item in request.get("source_files") or []:
        rel = item.get("packaged_path")
        p = root / str(rel or "")
        exists = p.exists()
        size = p.stat().st_size if exists else None
        expected_size = item.get("size_bytes")
        size_ok = exists and (expected_size is None or size == expected_size)
        source_rows.append({"path": rel, "exists": exists, "size_bytes": size, "expected_size_bytes": expected_size, "status": "PASS" if size_ok else "FAIL"})
        if not size_ok:
            failures.append(f"source:{rel}")
    checks["sources"] = {"status": "PASS" if all(r["status"] == "PASS" for r in source_rows) else "FAIL", "count": len(source_rows), "items": source_rows}

    grade = ((request.get("teacher") or {}).get("grade_level") or "").strip()
    targets = request.get("learning_targets") or []
    grade_ok = bool(grade)
    target_ok = bool(targets)
    checks["instructional_inputs"] = {"status": "PASS" if grade_ok and target_ok else "FAIL", "grade_level": grade, "target_count": len(targets)}
    if not grade_ok or not target_ok:
        failures.append("instructional_inputs")

    payload = {"version": VERSION, "overall_status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(payload["overall_status"], VERSION, out)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
