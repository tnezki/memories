#!/usr/bin/env python3
"""Shared deterministic Portfolio progress/grade overlay.

This module intentionally leaves source-level evidence judgment to ChatGPT and
recomputes longitudinal I Can progress, Mastery Goal report status, PowerSchool
score, and report progress bars from the local evidence ledger.
"""
from __future__ import annotations

import copy
import html
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import portfolio_runtime as runtime

_ALLOWED_EVIDENCE = {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE"}
_PROGRESS_RANK = {
    "NOT_YET_ASSESSED": 0,
    "STARTED": 1,
    "DEVELOPING": 2,
    "PROGRESSING": 3,
    "MASTERED": 4,
    "EXTENDED": 5,
    # migration compatibility
    "NO_EVIDENCE": 0,
    "TRANSFER": 5,
}
_LABEL = {
    "NOT_YET_ASSESSED": "Not Yet Assessed",
    "STARTED": "Started",
    "DEVELOPING": "Developing",
    "PROGRESSING": "Progressing",
    "MASTERED": "Mastered",
    "EXTENDED": "Extended",
}
_ACTION = {
    "NOT_YET_ASSESSED": ("NEEDS_FIRST_CHECK", "Needs first check"),
    "STARTED": ("PRACTICE_AND_CHECK", "Practice + check soon"),
    "DEVELOPING": ("PRACTICE_AND_CHECK", "Practice + check soon"),
    "PROGRESSING": ("NEEDS_ANOTHER_DEMONSTRATION", "Needs another independent check"),
    "MASTERED": ("SECURE", "Secure"),
    "EXTENDED": ("EXTENSION", "Extension"),
}

_ORIGINAL_BUILD_RESULTS = runtime.build_results
_ORIGINAL_BUILD_POWERSCHOOL = runtime.build_powerschool_exports
_INSTALLED = False


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    return _clean(value).lower() in {"1", "true", "yes", "y", "on"}


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(_clean(value) or default)
    except (TypeError, ValueError):
        return default


def _is_teacher_observation(row: dict[str, str]) -> bool:
    hay = " | ".join(
        _clean(row.get(k)).lower()
        for k in ("task_id", "question_lineage", "source_label", "source_type")
    )
    return (
        "teacher_observation" in hay
        or "teacher observation" in hay
        or "teacher walk-around checklist" in hay
        or "teacher walk around checklist" in hay
    )


def _source_signature(row: dict[str, str]) -> str:
    # Class opportunity identity follows the instructional event first, not an
    # individual scan/file hash. That keeps separate period scans of the same
    # dated Quick Check as one class opportunity while allowing the same prompt
    # to be used again on a later date as a new opportunity.
    date = _clean(row.get("source_date"))
    label = _clean(row.get("source_label"))
    source_type = _clean(row.get("source_type"))
    if date or label or source_type:
        return "event:" + "|".join([date, label, source_type])
    source_hash = _clean(row.get("source_sha256") or row.get("source_hash")).lower()
    return "hash:" + source_hash if source_hash else ""


def _event_opportunity(row: dict[str, str]) -> str:
    return _clean(row.get("opportunity_id") or row.get("event_id"))


def _independent_ops(events: Iterable[dict[str, str]], strength: str) -> set[str]:
    out: set[str] = set()
    strength = strength.upper()
    for row in events:
        if _clean(row.get("strength")).upper() != strength:
            continue
        if not _bool(row.get("independent_opportunity")):
            continue
        oid = _event_opportunity(row)
        if oid:
            out.add(oid)
    return out


def _all_ops(events: Iterable[dict[str, str]]) -> set[str]:
    return {_event_opportunity(row) for row in events if _event_opportunity(row)}


def _canonical_status(code: str) -> str:
    raw = _clean(code).upper()
    if raw == "NO_EVIDENCE":
        return "NOT_YET_ASSESSED"
    if raw == "TRANSFER":
        return "EXTENDED"
    return raw if raw in _LABEL else "NOT_YET_ASSESSED"


def class_opportunity_context(
    ican_rows: list[dict[str, str]], ledger_rows: list[dict[str, str]]
) -> tuple[dict[str, int], dict[str, int]]:
    """Return class opportunity counts by I Can and Mastery Goal.

    Count distinct formal/common sources across the class. Teacher observations
    contribute student evidence but do not advance the class-opportunity clock.
    """
    mg_by_ican: dict[str, str] = {}
    for row in ican_rows:
        iid = _clean(row.get("i_can_id"))
        mid = runtime.mg_id(row)
        if iid and mid:
            mg_by_ican[iid] = mid

    by_ican: dict[str, set[str]] = defaultdict(set)
    by_mg: dict[str, set[str]] = defaultdict(set)
    for row in ledger_rows:
        if _is_teacher_observation(row):
            continue
        iid = _clean(row.get("i_can_id"))
        if not iid:
            continue
        sig = _source_signature(row)
        if not sig:
            continue
        by_ican[iid].add(sig)
        mid = _clean(row.get("mastery_goal_id")) or mg_by_ican.get(iid, "")
        if mid:
            by_mg[mid].add(sig)
    return ({k: len(v) for k, v in by_ican.items()}, {k: len(v) for k, v in by_mg.items()})


def status_from_history(
    current_status: str,
    events: list[dict[str, str]],
    explicit_transfer: bool = False,
    class_opportunity_count: int = 0,
) -> tuple[str, str, str, str, int, int]:
    """Compatibility signature used by legacy runtime callers.

    The extra class_opportunity_count is optional; the patched state updater
    passes it so an absent student can move from Not Yet Assessed to Started.
    """
    current = _canonical_status(current_status)
    conv = _independent_ops(events, "CONVINCING")
    partial = _independent_ops(events, "PARTIAL")
    ops = _all_ops(events)
    attempted = any(_clean(e.get("strength")).upper() in _ALLOWED_EVIDENCE for e in events)

    # Existing established mastery/transfer remains durable unless the teacher
    # explicitly resolves a contradiction through a later workflow.
    established_mastery = current in {"MASTERED", "EXTENDED"} or len(conv) >= 2
    extension = explicit_transfer or current == "EXTENDED"

    if established_mastery and extension:
        status = "EXTENDED"
    elif established_mastery:
        status = "MASTERED"
    elif len(conv) >= 1 or len(partial) >= 3:
        status = "PROGRESSING"
    elif len(partial) >= 1:
        status = "DEVELOPING"
    elif attempted or int(class_opportunity_count or 0) >= 1:
        status = "STARTED"
    else:
        status = "NOT_YET_ASSESSED"

    action, action_label = _ACTION[status]
    return status, _LABEL[status], action, action_label, len(ops), len(conv)


def _recalculate_rows(
    state_dir: Path,
    ledger_rows: list[dict[str, str]] | None = None,
    explicit_transfer_pairs: set[tuple[str, str]] | None = None,
    latest_result: dict | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    path = state_dir / "i_can_status_current.csv"
    fields, rows = runtime.read_csv(path)
    fields = runtime.ensure_fields(
        fields,
        "source_opportunity_count",
        "independent_convincing_count",
        "independent_partial_count",
        "class_opportunity_count",
        "mg_class_opportunity_count",
        "review_flag",
    )
    if ledger_rows is None:
        ledger_path = state_dir / "evidence_ledger.csv"
        ledger_rows = runtime.read_csv(ledger_path)[1] if ledger_path.is_file() else []

    by_pair: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in ledger_rows:
        by_pair[(_clean(event.get("student_key")), _clean(event.get("i_can_id")))].append(event)

    ican_class, mg_class = class_opportunity_context(rows, ledger_rows)
    explicit_transfer_pairs = explicit_transfer_pairs or set()

    newest_strength: dict[tuple[str, str], str] = {}
    newest_review: dict[tuple[str, str], str] = {}
    source_label = ""
    source_date = ""
    if latest_result:
        source = latest_result.get("source", {}) or {}
        source_label = _clean(source.get("label"))
        source_date = _clean(source.get("date"))
        flatten = getattr(sys.modules.get("apply_grading_result"), "flatten_judgments", None)
        judgments = flatten(latest_result) if callable(flatten) else list(latest_result.get("judgments", []) or [])
        for judgment in judgments:
            strength = _clean(judgment.get("strength")).upper()
            if strength == "NOT_OBSERVED":
                continue
            pair = (_clean(judgment.get("student_key")), _clean(judgment.get("i_can_id")))
            newest_strength[pair] = strength
            if judgment.get("review_flag"):
                newest_review[pair] = _clean(judgment.get("review_flag"))
            if judgment.get("transfer") is True:
                explicit_transfer_pairs.add(pair)

    for row in rows:
        sk = _clean(row.get("student_key"))
        iid = _clean(row.get("i_can_id"))
        mid = runtime.mg_id(row)
        pair = (sk, iid)
        events = by_pair.get(pair, [])
        class_count = ican_class.get(iid, 0)
        extension = pair in explicit_transfer_pairs or _canonical_status(row.get("status_code", "")) == "EXTENDED"
        status, label, action, action_label, opp_count, conv_count = status_from_history(
            row.get("status_code", ""), events, extension, class_count
        )
        partial_count = len(_independent_ops(events, "PARTIAL"))
        row["status_code"] = status
        row["status_label"] = label
        row["student_action_code"] = action
        row["student_action_label"] = action_label
        row["source_opportunity_count"] = str(opp_count)
        row["independent_convincing_count"] = str(conv_count)
        row["independent_partial_count"] = str(partial_count)
        row["class_opportunity_count"] = str(class_count)
        row["mg_class_opportunity_count"] = str(mg_class.get(mid, 0))
        if pair in newest_strength:
            if "latest_source_label" in fields:
                row["latest_source_label"] = source_label
            if "latest_source" in fields:
                row["latest_source"] = source_label
            if "latest_source_date" in fields:
                row["latest_source_date"] = source_date
            if "latest_strength" in fields:
                row["latest_strength"] = newest_strength[pair]
        if pair in newest_review:
            row["review_flag"] = newest_review[pair]

    runtime.write_csv(path, fields, rows)
    return fields, rows


def recalculate_state_dir(state_dir: Path) -> tuple[list[str], list[dict[str, str]]]:
    return _recalculate_rows(Path(state_dir))


def mg_grade(ican_group: list[dict[str, str]]) -> dict[str, Any]:
    n = len(ican_group)
    if n <= 0:
        return {
            "assessed": False,
            "secure": 0,
            "count": 0,
            "threshold": 0,
            "demonstrated": False,
            "grade": "",
            "label": "Not Yet Assessed",
            "transfer": False,
            "report_display": "Not Yet Assessed",
            "powerschool_grade": "",
            "routing_code": "NOT_YET_ASSESSED",
            "class_opportunities": 0,
            "progressing": 0,
            "mastered": 0,
            "extended": 0,
        }

    statuses = [_canonical_status(r.get("status_code", "")) for r in ican_group]
    progressing = sum(_PROGRESS_RANK.get(s, 0) >= _PROGRESS_RANK["PROGRESSING"] for s in statuses)
    mastered = sum(_PROGRESS_RANK.get(s, 0) >= _PROGRESS_RANK["MASTERED"] for s in statuses)
    extended = sum(s == "EXTENDED" for s in statuses)
    developing_or_better = sum(_PROGRESS_RANK.get(s, 0) >= _PROGRESS_RANK["DEVELOPING"] for s in statuses)
    class_opportunities = max((_int(r.get("mg_class_opportunity_count")) for r in ican_group), default=0)
    student_evidence = any(_int(r.get("source_opportunity_count")) > 0 for r in ican_group)

    c_required = max(1, math.ceil(0.75 * n))
    b_mastered_required = max(1, math.ceil(0.50 * n))

    grade = ""
    ps_grade = ""
    report = "—"
    routing = "BUILDING_EVIDENCE"
    demonstrated = False

    if mastered == n and extended >= 1:
        grade = ps_grade = "A+"
        report = "A+"
        routing = "MEETING"
        demonstrated = True
    elif mastered == n:
        grade = ps_grade = "A"
        report = "A"
        routing = "MEETING"
        demonstrated = True
    elif progressing >= c_required and mastered >= b_mastered_required:
        grade = ps_grade = "B"
        report = "B"
        routing = "MEETING"
        demonstrated = True
    elif progressing >= c_required:
        grade = ps_grade = "C"
        report = "C"
        routing = "MEETING"
        demonstrated = True
    elif class_opportunities >= 2:
        # Internal I is retained only as a private routing compatibility code.
        # It is never written to PowerSchool or shown in a family report.
        grade = "I"
        if developing_or_better >= 1:
            report = "Falling Behind"
            ps_grade = ""
            routing = "FALLING_BEHIND"
        else:
            report = "F"
            ps_grade = "F"
            routing = "FALLING_BEHIND"
    elif class_opportunities == 0 and not student_evidence and developing_or_better == 0:
        report = "Not Yet Assessed"
        routing = "NOT_YET_ASSESSED"
    else:
        report = "—"
        routing = "BUILDING_EVIDENCE"

    assessed = report != "Not Yet Assessed"
    return {
        "assessed": assessed,
        "secure": mastered,
        "count": n,
        "threshold": c_required,
        "demonstrated": demonstrated,
        "grade": grade,
        "label": report,
        "transfer": extended > 0,
        "report_display": report,
        "powerschool_grade": ps_grade,
        "routing_code": routing,
        "class_opportunities": class_opportunities,
        "progressing": progressing,
        "mastered": mastered,
        "extended": extended,
        "meaningful_growth": developing_or_better >= 1,
        "c_required": c_required,
        "b_mastered_required": b_mastered_required,
    }


def display_grade(info: dict[str, Any]) -> str:
    if _clean(info.get("report_display")):
        return _clean(info.get("report_display"))
    grade = _clean(info.get("grade"))
    if grade == "I":
        return "Falling Behind"
    if not info.get("assessed"):
        return "Not Yet Assessed"
    return grade or "—"


def status_icon(code: str) -> str:
    status = _canonical_status(code)
    segments = _PROGRESS_RANK.get(status, 0)
    boxes = "".join('<span class="fill"></span>' if i < segments else "<span></span>" for i in range(5))
    label = html.escape(_LABEL.get(status, "Not Yet Assessed"))
    return f'<span class="ican-progress"><span class="progress-bar">{boxes}</span><span class="progress-label">{label}</span></span>'


def _patched_build_powerschool_exports(*args: Any, **kwargs: Any):
    if "grades" in kwargs:
        grades = copy.deepcopy(kwargs["grades"])
        kwargs = dict(kwargs)
        kwargs["grades"] = grades
    elif len(args) >= 6:
        args = list(args)
        grades = copy.deepcopy(args[5])
        args[5] = grades
        args = tuple(args)
    else:
        return _ORIGINAL_BUILD_POWERSCHOOL(*args, **kwargs)

    for by_mg in grades.values():
        for info in by_mg.values():
            ps = _clean(info.get("powerschool_grade"))
            info["grade"] = ps
    return _ORIGINAL_BUILD_POWERSCHOOL(*args, **kwargs)


def _state_dir_from_call(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Path | None:
    value = kwargs.get("state_dir")
    if value is None and len(args) >= 3:
        value = args[2]
    return Path(value) if value is not None else None



def _postprocess_student_markup(out_dir: Path) -> None:
    student_root = out_dir / "student_reports"
    if not student_root.is_dir():
        return
    pattern = re.compile(r'<div class="ican-next">.*?</div>', re.S)
    for path in student_root.rglob("*.html"):
        doc = path.read_text(encoding="utf-8")
        doc = pattern.sub("", doc)
        path.write_text(doc, encoding="utf-8")

def _postprocess_teacher_copy(out_dir: Path) -> None:
    path = out_dir / "teacher_report" / "teacher_summary.html"
    if not path.is_file():
        return
    doc = path.read_text(encoding="utf-8")
    replacements = {
        "Current Mastery Goal grades of I": "Mastery Goals Falling Behind",
        "at least one current assessed Mastery Goal grade I": "at least one current Falling Behind/F Mastery Goal",
        "current assessed MG grades I": "current Falling Behind/F Mastery Goals",
        "assessed MG grades I": "Falling Behind/F Mastery Goals",
        "Ranked by I-grade count": "Ranked by Falling Behind/F goal count",
        "I-grade count": "Falling Behind/F goal count",
        "I-grade intervention need": "Falling Behind intervention need",
    }
    for old, new in replacements.items():
        doc = doc.replace(old, new)
    path.write_text(doc, encoding="utf-8")


def _patched_build_results(*args: Any, **kwargs: Any):
    state_dir = _state_dir_from_call(tuple(args), kwargs)
    if state_dir is not None and (state_dir / "i_can_status_current.csv").is_file():
        fields, rows = recalculate_state_dir(state_dir)
        # The legacy report builder recognizes TRANSFER as an established strength.
        # Use that legacy code only in this temporary render copy; status_icon() and
        # mg_grade() translate it back to the current family-facing Extended state.
        changed = False
        for row in rows:
            if _clean(row.get("status_code")).upper() == "EXTENDED":
                row["status_code"] = "TRANSFER"
                row["status_label"] = "Extended"
                changed = True
        if changed:
            runtime.write_csv(state_dir / "i_can_status_current.csv", fields, rows)
    manifest = _ORIGINAL_BUILD_RESULTS(*args, **kwargs)
    out = kwargs.get("out_dir")
    if out is None and len(args) >= 13:
        out = args[12]
    if out is not None:
        out_path = Path(out)
        _postprocess_student_markup(out_path)
        _postprocess_teacher_copy(out_path)
    return manifest


def _patched_update_ican_state(state_dir: Path, ledger_rows: list[dict[str, str]], result: dict):
    return _recalculate_rows(Path(state_dir), ledger_rows=ledger_rows, latest_result=result)


def _patched_update_mg_state(state_dir: Path, ican_rows_data: list[dict[str, str]], roster_by: dict[str, dict[str, str]]):
    # Always recalculate from the ledger so roster-only runs also migrate legacy
    # statuses and receive current class-opportunity counts.
    _fields, fresh = recalculate_state_dir(Path(state_dir))
    path = Path(state_dir) / "mastery_goal_status_current.csv"
    fields, rows = runtime.read_csv(path)
    fields = runtime.ensure_fields(
        fields,
        "assessed",
        "secure_i_can_count",
        "i_can_count",
        "required_secure_count",
        "demonstrated",
        "grade_code",
        "grade_label",
        "transfer",
        "transfer_reason",
        "class_opportunity_count",
        "progressing_i_can_count",
        "mastered_i_can_count",
        "report_display",
        "powerschool_score",
        "routing_code",
    )
    by_student_mg: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in fresh:
        by_student_mg[(_clean(row.get("student_key")), runtime.mg_id(row))].append(row)
    existing = {(_clean(r.get("student_key")), runtime.mg_id(r)): r for r in rows}
    grades: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

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
            if "student_id" in fields:
                row["student_id"] = student.get("student_id", "")
            row["student_name"] = student.get("student_name", student.get("display_name", ""))
            row["period"] = student.get("period", "")
            if "mastery_goal_id" in fields:
                row["mastery_goal_id"] = mid
            if "mg_code" in fields:
                row["mg_code"] = mid
            rows.append(row)
            existing[(sk, mid)] = row
        row["assessed"] = "true" if info["assessed"] else "false"
        row["secure_i_can_count"] = str(info["mastered"])
        row["i_can_count"] = str(info["count"])
        row["required_secure_count"] = str(info["c_required"])
        row["demonstrated"] = "true" if info["demonstrated"] else "false"
        # Never persist/export a visible I grade.
        row["grade_code"] = info["powerschool_grade"]
        row["grade_label"] = info["report_display"]
        row["transfer"] = "true" if info["transfer"] else "false"
        row["class_opportunity_count"] = str(info["class_opportunities"])
        row["progressing_i_can_count"] = str(info["progressing"])
        row["mastered_i_can_count"] = str(info["mastered"])
        row["report_display"] = info["report_display"]
        row["powerschool_score"] = info["powerschool_grade"]
        row["routing_code"] = info["routing_code"]
    runtime.write_csv(path, fields, rows)
    return fields, rows, grades


def _patched_update_unit_state(state_dir: Path, grades: dict[str, dict[str, dict]], roster_by: dict[str, dict[str, str]], result: dict, report_number: int, report_date: str) -> None:
    path = Path(state_dir) / "unit_status_current.csv"
    fields, rows = runtime.read_csv(path)
    fields = runtime.ensure_fields(fields, "report_number", "report_date")
    for row in rows:
        sk = _clean(row.get("student_key"))
        g = grades.get(sk, {})
        demonstrated = sum(1 for x in g.values() if x.get("demonstrated"))
        if "mastery_goals_demonstrated" in fields:
            row["mastery_goals_demonstrated"] = str(demonstrated)
        if "mastery_goals_total" in fields:
            row["mastery_goals_total"] = str(len(g))
        if "mastery_goal_count" in fields:
            row["mastery_goal_count"] = str(len(g))
        # No overall Unit letter grade is part of the current Portfolio model.
        if "unit_status_code" in fields:
            row["unit_status_code"] = ""
        if "unit_status_label" in fields:
            row["unit_status_label"] = "Progress"
        row["report_number"] = str(report_number)
        row["report_date"] = report_date
    runtime.write_csv(path, fields, rows)


def sender_mg_grades(state_dir: Path) -> dict[str, list[dict[str, str]]]:
    """Sender-safe MG display built from the current shared progress model."""
    recalculate_state_dir(Path(state_dir))
    _fields, ican_rows = runtime.read_csv(Path(state_dir) / "i_can_status_current.csv")
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ican_rows:
        grouped[(_clean(row.get("student_key")), runtime.mg_id(row))].append(row)

    by_student: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for (sk, mid), rr in grouped.items():
        if sk and mid:
            by_student[sk].append((mid, mg_grade(rr)))

    out: dict[str, list[dict[str, str]]] = {}
    for sk, items in by_student.items():
        def sort_key(item: tuple[str, dict[str, Any]]):
            m = re.search(r"(\d+)$", item[0])
            return int(m.group(1)) if m else 9999
        rows_out: list[dict[str, str]] = []
        for mid, info in sorted(items, key=sort_key):
            rows_out.append({
                "code": mid,
                "title": "",
                "display": info["report_display"],
                "grade_code": info["powerschool_grade"],
                "grade_label": info["report_display"],
                "assessed": "TRUE" if info["assessed"] else "FALSE",
            })
        out[sk] = rows_out
    return out


def install_runtime() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    runtime.status_from_history = status_from_history
    runtime.mg_grade = mg_grade
    runtime.display_grade = display_grade
    runtime.status_icon = status_icon
    runtime.build_powerschool_exports = _patched_build_powerschool_exports
    runtime.build_results = _patched_build_results
    _INSTALLED = True


def install_loaded_modules() -> None:
    """Patch aliases in modules that imported runtime functions by value."""
    agr = sys.modules.get("apply_grading_result")
    if agr is not None:
        agr.status_from_history = status_from_history
        agr.mg_grade = mg_grade
        agr.update_ican_state = _patched_update_ican_state
        agr.update_mg_state = _patched_update_mg_state
        agr.update_unit_state = _patched_update_unit_state
    roster = sys.modules.get("update_roster")
    if roster is not None:
        roster.update_mg_state = _patched_update_mg_state
    sender = sys.modules.get("portfolio_sender_package")
    if sender is not None:
        sender._load_mg_grades = sender_mg_grades


install_runtime()
