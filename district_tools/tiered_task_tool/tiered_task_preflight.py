#!/usr/bin/env python3
"""Deterministic preflight for District Tiered Task request packages."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

VERSION = "district-tiered-task-preflight/1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-root", default=".")
    ap.add_argument("--out", default="work/tiered_task_preflight.json")
    args = ap.parse_args()
    root = Path(args.request_root).resolve()
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    failures, checks = [], {}

    try:
        request = json.loads((root / "request.json").read_text(encoding="utf-8"))
        checks["request_json"] = {"status":"PASS"}
    except Exception as exc:
        request = {}
        failures.append("request_json")
        checks["request_json"] = {"status":"FAIL","error":str(exc)}

    required = [
        "response_contract/TIERED_TASK_GENERATION_CONTRACT.md",
        "response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md",
        "response_contract/TIERED_TASK_BUILD_EXECUTION.md",
        "response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md",
        "response_contract/task_card_styles.css",
        "response_contract/guide_styles.css",
        "response_contract/tiered_task_preflight.py",
        "response_contract/tiered_task_finalize.py",
        "response_contract/tiered_task_qa.py",
        "response_contract/graph_tool/MANIFEST.json",
    ]
    graph_ep = (request.get("graph_rendering") or {}).get("packaged_entrypoint")
    if graph_ep:
        required.append(graph_ep)
    missing = [p for p in required if not (root / p).exists()]
    checks["packaged_dependencies"] = {"status":"PASS" if not missing else "FAIL","missing":missing}
    if missing: failures.append("packaged_dependencies")

    teacher = request.get("teacher") or {}
    targets = request.get("i_can_statements") or []
    products = ((request.get("product_choices") or {}).get("allowed") or [])
    required_fields = {
        "task_name": bool((request.get("task") or {}).get("name")),
        "subject_course": bool(teacher.get("subject_course")),
        "grade_level": bool(teacher.get("grade_level")),
        "i_can_statements": bool(targets),
        "allowed_products": bool(products),
    }
    ok = all(required_fields.values())
    checks["required_instructional_fields"] = {"status":"PASS" if ok else "FAIL", **required_fields}
    if not ok: failures.append("required_instructional_fields")

    for key in ("task_card","guide"):
        meta = (request.get("locked_styles") or {}).get(key) or {}
        p = root / str(meta.get("request_path") or "")
        expected = meta.get("sha256")
        actual = sha256(p) if p.exists() else None
        same = bool(expected and actual == expected)
        checks[f"style_{key}"] = {"status":"PASS" if same else "FAIL","expected":expected,"actual":actual}
        if not same: failures.append(f"style_{key}")

    for key in ("preflight","finalize","qa"):
        meta = (request.get("deterministic_tools") or {}).get(key) or {}
        p = root / str(meta.get("path") or "")
        expected = meta.get("sha256")
        actual = sha256(p) if p.exists() else None
        same = bool(expected and actual == expected)
        checks[f"tool_{key}"] = {"status":"PASS" if same else "FAIL","expected":expected,"actual":actual}
        if not same: failures.append(f"tool_{key}")

    gm = request.get("graph_rendering") or {}
    gp = root / str(gm.get("packaged_entrypoint") or "")
    gexpected = gm.get("sha256")
    gactual = sha256(gp) if gp.exists() else None
    same = bool(gexpected and gactual == gexpected)
    checks["graph_tool"] = {"status":"PASS" if same else "FAIL","entrypoint":gm.get("entrypoint"),"expected":gexpected,"actual":gactual}
    if not same: failures.append("graph_tool")

    source_missing = [x.get("packaged_path") for x in request.get("source_files") or [] if not (root / str(x.get("packaged_path") or "")).exists()]
    checks["source_files"] = {"status":"PASS" if not source_missing else "FAIL","count":len(request.get("source_files") or []),"missing":source_missing}
    if source_missing: failures.append("source_files")

    result = {"version":VERSION,"status":"PASS" if not failures else "FAIL","checks":checks,"failures":failures}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not failures else 2

if __name__ == "__main__":
    raise SystemExit(main())
