#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from apply_grading_result import apply_result_path
from portfolio_runtime import (
    SCHEMA_RESULT,
    extract_state,
    portfolio_root,
    github_root_from_runtime,
    read_csv,
    roster_rows,
    sha256_file,
    state_path,
    utc_now,
    validate_state_zip,
)

VALID_STRENGTHS = {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE"}


def apply_teacher_observation(
    course: str,
    unit: int,
    student_key: str,
    i_can_ids: list[str],
    strength: str = "CONVINCING",
    source_date: str = "",
    note: str = "",
    source_label: str = "Teacher Observation",
) -> dict:
    unit = int(unit)
    strength = str(strength or "CONVINCING").strip().upper()
    if strength not in VALID_STRENGTHS:
        raise ValueError(f"Unsupported observation strength: {strength}")
    clean_ids = []
    seen = set()
    for iid in i_can_ids:
        iid = str(iid or "").strip()
        if iid and iid not in seen:
            seen.add(iid)
            clean_ids.append(iid)
    if not clean_ids:
        raise ValueError("Select at least one I Can for the teacher observation.")
    source_date = source_date.strip() or datetime.now().date().isoformat()
    source_label = source_label.strip() or "Teacher Observation"

    root = portfolio_root(github_root_from_runtime())
    current = state_path(root, course, unit)
    manifest = validate_state_zip(current, course, unit)
    current_sha = sha256_file(current)

    with tempfile.TemporaryDirectory(prefix="portfolio_observation_state_") as td:
        td = Path(td)
        extract_state(current, td)
        state_dir = td / "state"
        _rf, roster, roster_by = roster_rows(state_dir)
        if student_key not in roster_by or roster_by[student_key].get("active") != "yes":
            raise ValueError("Choose an active student from the current local roster.")
        student = roster_by[student_key]
        _if, icans = read_csv(state_dir / "i_can_status_current.csv")
        by_id = {}
        for row in icans:
            if row.get("student_key") == student_key:
                iid = (row.get("i_can_id") or "").strip()
                if iid:
                    by_id[iid] = row
        missing = [iid for iid in clean_ids if iid not in by_id]
        if missing:
            raise ValueError("Unknown I Can for selected student: " + ", ".join(missing))

        session_id = uuid.uuid4().hex[:10]
        run_id = f"OBS-{course.replace(' ','').upper()}-U{unit}-{source_date.replace('-','')}-{session_id}"
        judgments = []
        for iid in clean_ids:
            row = by_id[iid]
            mid = (row.get("mastery_goal_id") or row.get("mg_code") or "").strip()
            judgments.append({
                "student_key": student_key,
                "student_name": student.get("display_name") or student.get("student_name") or "",
                "period": student.get("period", ""),
                "source_file_name": "",
                "source_file_sha256": "",
                "page_ref": "",
                "task_id": "teacher_observation",
                "question_lineage": "teacher_observation",
                "mastery_goal_id": mid,
                "i_can_id": iid,
                "strength": strength,
                "note": note.strip() or "Teacher observed the student demonstrate this I Can during class.",
                "opportunity_id": f"OBS-{source_date}-{session_id}-{student_key}-{iid}",
                "independent_opportunity": True,
                "review_flag": "",
                "transfer": False,
            })

        result = {
            "schema": SCHEMA_RESULT,
            "status": "READY",
            "course": course,
            "unit": unit,
            "run_id": run_id,
            "graded_at": utc_now(),
            "report_date": source_date,
            "parent_state": {
                "sha256": current_sha,
                "state_version": int(manifest.get("state_version", 0)),
                "state_id": manifest.get("state_id"),
            },
            "source": {
                "label": source_label,
                "date": source_date,
                "type": "Teacher Observation",
                "evidence_files": [],
            },
            "judgments": judgments,
            "no_submission_student_keys": [],
            "unresolved": [],
            "class_insights": {},
        }
        result_path = td / "Portfolio_Grading_Result_Teacher_Observation.json"
        result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        applied = apply_result_path(result_path, archive_input=True)
    applied["observation_student_key"] = student_key
    applied["observation_i_can_count"] = len(clean_ids)
    applied["observation_strength"] = strength
    return applied
