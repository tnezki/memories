#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from portfolio_runtime import (
    SCHEMA_RESULT,
    archive_and_install_results,
    archive_and_install_state,
    build_results,
    ensure_fields,
    extract_state,
    github_root_from_runtime,
    install_results_to_local_folders,
    mg_grade,
    mg_id,
    portfolio_root,
    read_csv,
    read_json,
    roster_rows,
    safe_zip_tree,
    sha256_file,
    state_path,
    status_from_history,
    timestamp,
    utc_now,
    validate_state_zip,
    write_csv,
    write_json,
)

STRENGTHS = {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE", "NOT_OBSERVED"}


def osa_choose_file(prompt: str) -> Path | None:
    script = f'''try\nset f to choose file with prompt "{prompt.replace('"','\\"')}"\nreturn POSIX path of f\non error number -128\nreturn ""\nend try'''
    proc = subprocess.run(["/usr/bin/osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    p = proc.stdout.strip() if proc.returncode == 0 else ""
    return Path(p) if p else None


def find_result() -> Path | None:
    downloads = Path.home() / "Downloads"
    candidates = []
    for pat in ["Portfolio_Grading_Result*.json", "portfolio_grading_result*.json"]:
        candidates.extend(downloads.glob(pat))
    candidates = [p for p in candidates if p.is_file()]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for p in candidates:
        try:
            data = read_json(p)
            if data.get("schema") == SCHEMA_RESULT:
                return p
        except Exception:
            pass
    return osa_choose_file("Choose Portfolio_Grading_Result.json")


def flatten_judgments(result: dict) -> list[dict]:
    if isinstance(result.get("judgments"), list):
        return [dict(x) for x in result["judgments"] if isinstance(x, dict)]
    out = []
    for student in result.get("students", []):
        if not isinstance(student, dict):
            continue
        base = {
            "student_key": student.get("student_key"),
            "student_name": student.get("student_name"),
            "period": student.get("period"),
        }
        for ev in student.get("evidence", []):
            if isinstance(ev, dict):
                row = dict(base)
                row.update(ev)
                out.append(row)
    return out


def bool_text(value: bool, style: str) -> str:
    return "True" if style == "title" and value else "False" if style == "title" else "yes" if value else "no"


def append_ledger(state_dir: Path, result: dict, roster_by: dict[str, dict[str, str]], current_icans: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], int]:
    path = state_dir / "evidence_ledger.csv"
    fields, rows = read_csv(path)
    ican_lookup = {(r.get("student_key", ""), r.get("i_can_id", "")): r for r in current_icans}
    source = result["source"]
    source_files = source.get("evidence_files", [])
    one_hash = source_files[0].get("sha256") if len(source_files) == 1 else ""
    one_name = source_files[0].get("name") if len(source_files) == 1 else ""
    run_id = result.get("run_id") or f"LOCAL-{timestamp()}"
    existing = set()
    for r in rows:
        existing.add((r.get("student_key", ""), r.get("i_can_id", ""), r.get("opportunity_id", ""), r.get("source_sha256") or r.get("source_hash") or ""))

    indep_style = "title" if any(str(r.get("independent_opportunity", "")).strip() in {"True", "False"} for r in rows[:20]) else "yes"
    added = 0
    for idx, j in enumerate(flatten_judgments(result), 1):
        sk = str(j.get("student_key") or "").strip()
        iid = str(j.get("i_can_id") or "").strip()
        strength = str(j.get("strength") or "").strip().upper()
        if strength not in STRENGTHS:
            raise ValueError(f"Unknown evidence strength for {sk} {iid}: {strength}")
        if strength == "NOT_OBSERVED":
            continue
        if sk not in roster_by:
            raise ValueError(f"Result references unknown student_key: {sk}")
        current = ican_lookup.get((sk, iid))
        if not current:
            raise ValueError(f"Result references unknown I Can for student {sk}: {iid}")
        mid = j.get("mastery_goal_id") or current.get("mastery_goal_id") or current.get("mg_code") or ""
        file_sha = str(j.get("source_file_sha256") or one_hash or "").strip()
        file_name = str(j.get("source_file_name") or one_name or "").strip()
        opp = str(j.get("opportunity_id") or "").strip()
        if not opp:
            prefix = (file_sha or result.get("run_id") or "local")[:12]
            opp = f"{prefix}-{sk}-{iid}"
        key = (sk, iid, opp, file_sha)
        if key in existing:
            continue
        indep = bool(j.get("independent_opportunity", True))
        event_id = str(j.get("event_id") or f"{run_id}-{sk}-{iid}-{idx:02d}")
        student = roster_by[sk]
        note = str(j.get("note") or j.get("concise_note") or "").strip()
        text = current.get("i_can_text") or current.get("i_can_exact_text") or ""
        row = {k: "" for k in fields}
        mapping = {
            "event_id": event_id,
            "student_key": sk,
            "student_id": student.get("student_id", ""),
            "student_name": student.get("display_name") or student.get("student_name", ""),
            "period": student.get("period", ""),
            "source_sha256": file_sha,
            "source_hash": file_sha,
            "source_date": source.get("date", ""),
            "source_type": source.get("type", "teacher_supplied_evidence"),
            "source_label": source.get("label", "New Evidence"),
            "source_legacy_alias": file_name,
            "page_ref": j.get("page_ref", ""),
            "page_task_id": j.get("page_ref") or j.get("task_id", ""),
            "task_id": j.get("task_id", ""),
            "question_lineage": j.get("question_lineage", ""),
            "mastery_goal_id": mid,
            "i_can_id": iid,
            "i_can_exact_text": text,
            "evidence_role": j.get("evidence_role", "source-level I Can judgment"),
            "opportunity_id": opp,
            "independent_opportunity": bool_text(indep, indep_style),
            "strength": strength,
            "note": note,
            "concise_note": note,
            "review_flag": j.get("review_flag", ""),
        }
        for k, v in mapping.items():
            if k in row:
                row[k] = "" if v is None else str(v)
        rows.append(row)
        existing.add(key)
        added += 1
    write_csv(path, fields, rows)
    return fields, rows, added


def update_ican_state(state_dir: Path, ledger_rows: list[dict[str, str]], result: dict) -> tuple[list[str], list[dict[str, str]]]:
    path = state_dir / "i_can_status_current.csv"
    fields, rows = read_csv(path)
    fields = ensure_fields(fields, "source_opportunity_count", "independent_convincing_count", "review_flag")
    by_pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for e in ledger_rows:
        by_pair_events[(e.get("student_key", ""), e.get("i_can_id", ""))].append(e)
    transfer_pairs = {(str(j.get("student_key") or ""), str(j.get("i_can_id") or "")) for j in flatten_judgments(result) if j.get("transfer") is True}
    source_label = result["source"].get("label", "")
    source_date = result["source"].get("date", "")
    # newest result strength for each affected pair
    newest_strength = {}
    newest_review = {}
    for j in flatten_judgments(result):
        strength = str(j.get("strength") or "").upper()
        if strength == "NOT_OBSERVED":
            continue
        pair = (str(j.get("student_key") or ""), str(j.get("i_can_id") or ""))
        newest_strength[pair] = strength
        if j.get("review_flag"):
            newest_review[pair] = str(j.get("review_flag"))
    for r in rows:
        pair = (r.get("student_key", ""), r.get("i_can_id", ""))
        events = by_pair_events.get(pair, [])
        status, label, action, action_label, opp_count, conv_count = status_from_history(r.get("status_code", ""), events, pair in transfer_pairs)
        r["status_code"] = status
        r["status_label"] = label
        r["student_action_code"] = action
        r["student_action_label"] = action_label
        r["source_opportunity_count"] = str(opp_count)
        r["independent_convincing_count"] = str(conv_count)
        if pair in newest_strength:
            if "latest_source_label" in fields: r["latest_source_label"] = source_label
            if "latest_source" in fields: r["latest_source"] = source_label
            if "latest_source_date" in fields: r["latest_source_date"] = source_date
            if "latest_strength" in fields: r["latest_strength"] = newest_strength[pair]
        if pair in newest_review:
            r["review_flag"] = newest_review[pair]
    write_csv(path, fields, rows)
    return fields, rows


def update_mg_state(state_dir: Path, ican_rows_data: list[dict[str, str]], roster_by: dict[str, dict[str, str]]) -> tuple[list[str], list[dict[str, str]], dict[str, dict[str, dict]]]:
    path = state_dir / "mastery_goal_status_current.csv"
    fields, rows = read_csv(path)
    fields = ensure_fields(fields, "assessed", "secure_i_can_count", "i_can_count", "required_secure_count", "demonstrated", "grade_code", "grade_label", "transfer", "transfer_reason")
    by_student_mg: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in ican_rows_data:
        by_student_mg[(r.get("student_key", ""), r.get("mastery_goal_id") or r.get("mg_code") or "")].append(r)
    existing = {(r.get("student_key", ""), r.get("mastery_goal_id") or r.get("mg_code") or ""): r for r in rows}
    grades: dict[str, dict[str, dict]] = defaultdict(dict)
    for (sk, mid), rr in sorted(by_student_mg.items()):
        if not mid:
            continue
        info = mg_grade(rr)
        grades[sk][mid] = info
        row = existing.get((sk, mid))
        if row is None:
            student = roster_by.get(sk, {})
            row = {k: "" for k in fields}
            row["student_key"] = sk
            if "student_id" in fields: row["student_id"] = student.get("student_id", "")
            row["student_name"] = student.get("student_name", "")
            row["period"] = student.get("period", "")
            if "mastery_goal_id" in fields: row["mastery_goal_id"] = mid
            if "mg_code" in fields: row["mg_code"] = mid
            rows.append(row)
            existing[(sk, mid)] = row
        row["assessed"] = "true" if info["assessed"] else "false"
        row["secure_i_can_count"] = str(info["secure"])
        row["i_can_count"] = str(info["count"])
        row["required_secure_count"] = str(info["threshold"])
        row["demonstrated"] = "true" if info["demonstrated"] else "false"
        row["grade_code"] = info["grade"]
        row["grade_label"] = info["label"]
        row["transfer"] = "true" if info["transfer"] else "false"
    write_csv(path, fields, rows)
    return fields, rows, grades


def update_unit_state(state_dir: Path, grades: dict[str, dict[str, dict]], roster_by: dict[str, dict[str, str]], result: dict, report_number: int, report_date: str) -> None:
    path = state_dir / "unit_status_current.csv"
    fields, rows = read_csv(path)
    fields = ensure_fields(fields, "report_number", "report_date")
    for r in rows:
        sk = r.get("student_key", "")
        g = grades.get(sk, {})
        demonstrated = sum(1 for x in g.values() if x.get("demonstrated"))
        if "mastery_goals_demonstrated" in fields: r["mastery_goals_demonstrated"] = str(demonstrated)
        if "mastery_goals_total" in fields: r["mastery_goals_total"] = str(len(g))
        if "mastery_goal_count" in fields: r["mastery_goal_count"] = str(len(g))
        if "unit_status_code" in fields: r["unit_status_code"] = "I" if demonstrated < len(g) else "A"
        if "unit_status_label" in fields: r["unit_status_label"] = "In Progress" if demonstrated < len(g) else "Mastery"
        r["report_number"] = str(report_number)
        r["report_date"] = report_date
    write_csv(path, fields, rows)


def rebuild_class_summary(state_dir: Path, ican_rows_data: list[dict[str, str]], ledger_rows: list[dict[str, str]], result: dict, active_keys: set[str]) -> None:
    path = state_dir / "class_i_can_summary.csv"
    fields, old = read_csv(path)
    if "scope" in fields:
        # Algebra-style: latest evidence strength counts by scope/period.
        latest = [e for e in ledger_rows if e.get("source_label") == result["source"].get("label", "") and e.get("source_date") == result["source"].get("date", "")]
        text = {}
        period_by_key = {}
        for r in ican_rows_data:
            text[r.get("i_can_id", "")] = r.get("i_can_text") or r.get("i_can_exact_text") or ""
            period_by_key[r.get("student_key", "")] = r.get("period", "")
        iids = sorted({r.get("i_can_id", "") for r in latest if r.get("i_can_id")})
        scopes = [("Combined", "")] + [(p, p) for p in sorted({period_by_key[k] for k in active_keys if period_by_key.get(k)})]
        rows = []
        for scope, period in scopes:
            keys = {k for k in active_keys if not period or period_by_key.get(k) == period}
            for iid in iids:
                events = [e for e in latest if e.get("i_can_id") == iid and e.get("student_key") in keys]
                c = Counter(e.get("strength", "") for e in events)
                submitted_keys = {e.get("student_key") for e in events}
                total = len(keys)
                row = {k: "" for k in fields}
                row.update({
                    "scope": scope,
                    "period": period,
                    "i_can_id": iid,
                    "i_can_text": text.get(iid, ""),
                    "convincing": str(c["CONVINCING"]),
                    "partial": str(c["PARTIAL"]),
                    "limited": str(c["LIMITED"]),
                    "unusable": str(c["UNUSABLE"]),
                    "no_submission": str(total - len(submitted_keys)),
                    "total": str(total),
                    "convincing_pct": f'{round(100*c["CONVINCING"]/total):d}%' if total else "0%",
                    "source_label": result["source"].get("label", ""),
                    "source_date": result["source"].get("date", ""),
                })
                rows.append(row)
        write_csv(path, fields, rows)
    else:
        # Physics-style: longitudinal status counts.
        text = {}
        grouped = defaultdict(list)
        for r in ican_rows_data:
            if r.get("student_key") not in active_keys:
                continue
            iid = r.get("i_can_id", "")
            grouped[(r.get("mastery_goal_id") or r.get("mg_code") or "", iid)].append(r)
            text[iid] = r.get("i_can_text") or r.get("i_can_exact_text") or ""
        rows = []
        for (mid, iid), rr in sorted(grouped.items()):
            c = Counter(r.get("status_code") for r in rr)
            row = {k: "" for k in fields}
            row.update({
                "mastery_goal_id": mid,
                "i_can_id": iid,
                "i_can_exact_text": text.get(iid, ""),
                "no_evidence_count": str(c["NO_EVIDENCE"]),
                "developing_count": str(c["DEVELOPING"]),
                "mastered_count": str(c["MASTERED"]),
                "transfer_count": str(c["TRANSFER"]),
            })
            rows.append(row)
        write_csv(path, fields, rows)


def rebuild_intervention_groups(state_dir: Path, ican_rows_data: list[dict[str, str]], active_keys: set[str]) -> None:
    path = state_dir / "intervention_groups.csv"
    fields, _old = read_csv(path)
    if "category" in fields and "students" in fields:
        grouped = defaultdict(list)
        for r in ican_rows_data:
            if r.get("student_key") not in active_keys:
                continue
            action = r.get("student_action_label", "")
            category = {
                "Practice + check soon": "Practice + check soon",
                "Needs another independent check": "Ready for another independent demonstration",
                "Needs first check": "No evidence / absent",
                "Secure": "Secure",
                "Extension": "Extension",
            }.get(action, action)
            grouped[(r.get("mastery_goal_id") or r.get("mg_code") or "", r.get("i_can_id", ""), r.get("i_can_text") or r.get("i_can_exact_text") or "", category)].append(r.get("student_name", ""))
        rows = []
        for (mid, iid, text, cat), names in sorted(grouped.items()):
            row = {k: "" for k in fields}
            row.update({"mastery_goal_id": mid, "i_can_id": iid, "i_can_exact_text": text, "category": cat, "student_count": str(len(names)), "students": " | ".join(names)})
            rows.append(row)
        write_csv(path, fields, rows)
    else:
        rows = []
        for r in ican_rows_data:
            if r.get("student_key") not in active_keys:
                continue
            row = {k: "" for k in fields}
            for k in fields:
                if k in r: row[k] = r[k]
            action = r.get("student_action_label", "")
            row["intervention_group"] = {
                "Practice + check soon": "Practice + check soon",
                "Needs another independent check": "Ready for another independent demonstration",
                "Needs first check": "No evidence / absent",
                "Secure": "Secure",
                "Extension": "Extension",
            }.get(action, action)
            rows.append(row)
        write_csv(path, fields, rows)


def append_review_queue(state_dir: Path, result: dict) -> None:
    path = state_dir / "review_queue.csv"
    if not path.is_file():
        return
    fields, rows = read_csv(path)
    unresolved = result.get("unresolved", [])
    for idx, item in enumerate(unresolved, 1):
        row = {k: "" for k in fields}
        if "review_id" in fields:
            row["review_id"] = f'{result.get("run_id","LOCAL")}-REVIEW-{idx:02d}'
            row["source_hash"] = item.get("source_file_sha256", "")
            row["source_label"] = result["source"].get("label", "")
            row["source_date"] = result["source"].get("date", "")
            row["page_reference"] = item.get("page_ref", "")
            row["issue_code"] = item.get("issue_code", "REVIEW")
            row["details"] = item.get("details", "")
            row["resolution_status"] = "OPEN"
        else:
            row["student_key"] = item.get("student_key", "")
            row["student_name"] = item.get("student_name", "")
            row["period"] = item.get("period", "")
            row["source_label"] = result["source"].get("label", "")
            row["page_ref"] = item.get("page_ref", "")
            row["reason"] = item.get("details", "")
            row["status"] = "OPEN"
        rows.append(row)
    write_csv(path, fields, rows)


def append_run_history(state_dir: Path, result: dict, active_count: int, event_count: int, report_number: int) -> None:
    path = state_dir / "run_history.csv"
    fields, rows = read_csv(path)
    row = {k: "" for k in fields}
    source_files = result["source"].get("evidence_files", [])
    source_hash = source_files[0].get("sha256", "") if len(source_files) == 1 else "MULTI_SOURCE"
    mapping = {
        "run_id": result.get("run_id", ""),
        "run_date": result.get("graded_at", utc_now())[:10],
        "course": result.get("course", ""),
        "unit": str(result.get("unit", "")),
        "source_label": result["source"].get("label", ""),
        "source_date": result["source"].get("date", ""),
        "source_sha256": source_hash,
        "source_hash": source_hash,
        "roster_count": str(active_count),
        "roster_students": str(active_count),
        "submission_count": str(len({j.get("student_key") for j in flatten_judgments(result) if str(j.get("strength","")).upper() != "NOT_OBSERVED"})),
        "identified_submissions": str(len({j.get("student_key") for j in flatten_judgments(result) if str(j.get("strength","")).upper() != "NOT_OBSERVED"})),
        "no_submission_count": str(len(result.get("no_submission_student_keys", []))),
        "unresolved_packets": str(len(result.get("unresolved", []))),
        "review_flag_count": str(len(result.get("unresolved", [])) + sum(bool(j.get("review_flag")) for j in flatten_judgments(result))),
        "evidence_events": str(event_count),
        "report_number": str(report_number),
        "result": "PASS_LOCAL_RUNTIME",
        "status": "PASS_LOCAL_RUNTIME",
    }
    for k, v in mapping.items():
        if k in row: row[k] = v
    rows.append(row)
    write_csv(path, fields, rows)


def update_run_manifest(state_dir: Path, result: dict, active_count: int, event_count: int, report_number: int, report_date: str) -> None:
    path = state_dir / "run_manifest.json"
    old = read_json(path) if path.is_file() else {}
    old.update({
        "schema": old.get("schema", "portfolio-run-manifest/1.3-local"),
        "run_id": result.get("run_id"),
        "course": result.get("course"),
        "unit": result.get("unit"),
        "report_number": report_number,
        "report_date": report_date,
        "source_label": result["source"].get("label", ""),
        "source_date": result["source"].get("date", ""),
        "roster_count": active_count,
        "submission_count": len({j.get("student_key") for j in flatten_judgments(result) if str(j.get("strength","")).upper() != "NOT_OBSERVED"}),
        "no_submission_count": len(result.get("no_submission_student_keys", [])),
        "delivery": "local_state_html_reports",
        "refresh_reason": "Local ChatGPT grading-result JSON applied by deterministic Portfolio runtime.",
        "local_runtime": {
            "schema": "portfolio-local-runtime/1.0",
            "graded_result_schema": result.get("schema"),
            "graded_at": result.get("graded_at"),
            "evidence_events_added": event_count,
            "google_drive_used": False,
        },
    })
    write_json(path, old)


def determine_report_number(state_dir: Path) -> int:
    nums = []
    p = state_dir / "unit_status_current.csv"
    if p.is_file():
        _f, rows = read_csv(p)
        for r in rows:
            try: nums.append(int(r.get("report_number", "")))
            except Exception: pass
    rm = state_dir / "run_manifest.json"
    if rm.is_file():
        try: nums.append(int(read_json(rm).get("report_number", 0)))
        except Exception: pass
    return max(nums or [0]) + 1


def build_new_state_manifest(work_root: Path, old_manifest: dict, current_sha: str, result: dict) -> dict:
    state_dir = work_root / "state"
    files = []
    for p in sorted(state_dir.rglob("*")):
        if p.is_file():
            files.append({"path": p.relative_to(work_root).as_posix(), "sha256": sha256_file(p)})
    return {
        "schema": "portfolio-portable-state/1",
        "status": "CURRENT",
        "course": result["course"],
        "unit": int(result["unit"]),
        "state_version": int(old_manifest.get("state_version", 0)) + 1,
        "state_id": f'{result["course"].replace(" ","-").upper()}-U{result["unit"]}-V{int(old_manifest.get("state_version",0))+1}-{uuid.uuid4().hex[:8]}',
        "generated_at": utc_now(),
        "parent_state_sha256": current_sha,
        "run_id": result.get("run_id"),
        "source_mode": "local_grading_result",
        "files": files,
    }


def main() -> int:
    result_path = find_result()
    if not result_path:
        print("No Portfolio_Grading_Result.json selected. Nothing changed.")
        return 0
    result = read_json(result_path)
    if result.get("schema") != SCHEMA_RESULT:
        raise ValueError(f"Wrong grading-result schema: {result.get('schema')}")
    if result.get("status") not in {"READY", "PASS"}:
        raise ValueError(f"Grading result is not READY/PASS: {result.get('status')}")
    course = result.get("course")
    unit = int(result.get("unit", 0))
    if not course or unit < 1:
        raise ValueError("Grading result is missing course/unit")
    github_root = github_root_from_runtime()
    root = portfolio_root(github_root)
    current = state_path(root, course, unit)
    old_manifest = validate_state_zip(current, course, unit)
    current_sha = sha256_file(current)
    parent = result.get("parent_state", {})
    if parent.get("sha256") != current_sha:
        raise ValueError("REFUSED: grading result was created from a different local state SHA-256. Sync _portfolio_data or rebuild the grading request before applying.")
    if int(parent.get("state_version", -1)) != int(old_manifest.get("state_version", -2)) or parent.get("state_id") != old_manifest.get("state_id"):
        raise ValueError("REFUSED: grading result state version/id does not match the installed current state.")

    run_id = result.get("run_id") or f"LOCAL-{timestamp()}"
    result["run_id"] = run_id
    result.setdefault("graded_at", utc_now())
    target = current.parent.parent  # unit N root
    report_number = determine_report_number_from_zip(current)
    report_date = result.get("report_date") or result.get("source", {}).get("date") or datetime.now().date().isoformat()

    print("Portfolio local grading-result processor")
    print(f"Target: {course} Unit {unit}")
    print(f"Current state: v{old_manifest.get('state_version')}")
    print(f"Result: {result_path.name}")
    print()

    with tempfile.TemporaryDirectory(prefix="portfolio_apply_") as td:
        td = Path(td)
        state_work = td / "state_work"
        extract_state(current, state_work)
        state_dir = state_work / "state"
        _rf, roster, roster_by = roster_rows(state_dir)
        active = [r for r in roster if r["active"] == "yes"]
        active_keys = {r["student_key"] for r in active}
        ican_fields, current_icans = read_csv(state_dir / "i_can_status_current.csv")
        _lf, ledger_rows, added = append_ledger(state_dir, result, roster_by, current_icans)
        _if, updated_icans = update_ican_state(state_dir, ledger_rows, result)
        _mf, _mgrows, grades = update_mg_state(state_dir, updated_icans, roster_by)
        report_number = determine_report_number(state_dir)
        update_unit_state(state_dir, grades, roster_by, result, report_number, report_date)
        rebuild_class_summary(state_dir, updated_icans, ledger_rows, result, active_keys)
        rebuild_intervention_groups(state_dir, updated_icans, active_keys)
        append_review_queue(state_dir, result)
        append_run_history(state_dir, result, len(active), added, report_number)
        update_run_manifest(state_dir, result, len(active), added, report_number, report_date)

        new_manifest = build_new_state_manifest(state_work, old_manifest, current_sha, result)
        write_json(state_work / "STATE_MANIFEST.json", new_manifest)
        new_state_zip = td / "Portfolio_State_UPDATED.zip"
        safe_zip_tree(state_work, new_state_zip)
        validate_state_zip(new_state_zip, course, unit)

        results_dir = td / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        results_manifest = build_results(
            github_root=github_root,
            runtime_dir=Path(__file__).resolve().parent,
            state_dir=state_dir,
            state_manifest=new_manifest,
            input_state_sha=sha256_file(new_state_zip),
            course=course,
            unit=unit,
            report_number=report_number,
            report_date=report_date,
            latest_label=result["source"].get("label", "New Evidence"),
            latest_date=result["source"].get("date", ""),
            class_insights=result.get("class_insights"),
            out_dir=results_dir,
        )
        results_zip = td / "Portfolio_Results.zip"
        safe_zip_tree(results_dir, results_zip)

        # Commit only after all state/report/validator work passed.
        archive_and_install_state(new_state_zip, current, new_manifest["state_version"])
        archive_and_install_results(results_zip, target)
        install_results_to_local_folders(results_dir, target)

    applied_dir = target / "02 Portfolio Data" / "Applied Grading Results"
    applied_dir.mkdir(parents=True, exist_ok=True)
    archived_result = applied_dir / f"{timestamp()}_{result_path.name}"
    shutil.copy2(result_path, archived_result)
    print(f"Applied {added} new source-level evidence judgment(s).")
    print(f"Installed {course} Unit {unit} state v{new_manifest['state_version']}.")
    print("Refreshed 03 Student Packets, 04 Class & Intervention Summaries, and 05 PowerSchool Exports.")
    print("Updated Latest Portfolio Results.zip.")
    print("Google Drive was not used.")
    print()
    print(f"Current state: {current}")
    return 0


def determine_report_number_from_zip(_path: Path) -> int:
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("\nFAILED. Nothing should be considered applied unless the success lines were printed.\n")
        print(str(exc))
        raise
