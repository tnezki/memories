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
from collections import Counter, defaultdict
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



def _legacy_next_pattern() -> re.Pattern[str]:
    return re.compile(
        r'<div\b[^>]*class=(?:"[^"]*\bican-next\b[^"]*"|\'[^\']*\bican-next\b[^\']*\')[^>]*>.*?</div>',
        re.I | re.S,
    )


def _recent_four_events(state_dir: Path) -> dict[str, list[dict[str, str]]]:
    ledger = state_dir / "evidence_ledger.csv"
    if not ledger.is_file():
        return {}
    _fields, rows = runtime.read_csv(ledger)
    by_student: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        strength = _clean(row.get("strength")).upper()
        if strength not in _ALLOWED_EVIDENCE:
            continue
        sk = _clean(row.get("student_key"))
        iid = _clean(row.get("i_can_id"))
        if sk and iid:
            by_student[sk].append(row)
    return {sk: list(reversed(events[-4:])) for sk, events in by_student.items()}


def _recent_rows_html(events: list[dict[str, str]], text_by_ican: dict[str, str]) -> str:
    if not events:
        return '<tr><td>—</td><td>No assessed evidence yet</td><td>—</td><td>No assessed evidence is currently recorded for this student.</td></tr>'
    rows: list[str] = []
    for event in events[:4]:
        iid = _clean(event.get("i_can_id"))
        target = _clean(event.get("i_can_exact_text")) or text_by_ican.get(iid, "")
        evidence = _clean(event.get("strength")).title()
        note = _clean(event.get("note") or event.get("concise_note"))
        rows.append(
            f'<tr><td><b>{html.escape(iid)}</b></td><td>{html.escape(target)}</td>'
            f'<td>{html.escape(evidence)}</td><td>{html.escape(note)}</td></tr>'
        )
    return "".join(rows)


def _replace_recent_tbody(doc: str, rows_html: str) -> str:
    pattern = re.compile(
        r'(<section\b[^>]*class=["\'][^"\']*\brecent\b[^"\']*["\'][^>]*>.*?<tbody>)(.*?)(</tbody>)',
        re.I | re.S,
    )
    return pattern.sub(lambda m: m.group(1) + rows_html + m.group(3), doc, count=1)


def _postprocess_student_markup(out_dir: Path, state_dir: Path | None = None) -> None:
    student_root = out_dir / "student_reports"
    if not student_root.is_dir():
        return

    next_pattern = _legacy_next_pattern()
    recent_by_student = _recent_four_events(state_dir) if state_dir is not None else {}
    text_by_ican: dict[str, str] = {}
    if state_dir is not None and (state_dir / "i_can_status_current.csv").is_file():
        _fields, current = runtime.read_csv(state_dir / "i_can_status_current.csv")
        for row in current:
            iid = _clean(row.get("i_can_id"))
            if iid:
                text_by_ican[iid] = _clean(row.get("i_can_text") or row.get("i_can_exact_text"))

    individual = student_root / "individual"
    if individual.is_dir():
        for path in sorted(individual.glob("*.html")):
            doc = path.read_text(encoding="utf-8")
            doc = next_pattern.sub("", doc)
            sk = path.stem
            doc = _replace_recent_tbody(doc, _recent_rows_html(recent_by_student.get(sk, []), text_by_ican))
            if next_pattern.search(doc) or "<b>Next:</b>" in doc:
                raise ValueError(f"Portfolio cleanup failed: retired per-I-Can Next line remains in {path.name}")
            path.write_text(doc, encoding="utf-8")

    # Rebuild the combined class packet from the cleaned individual reports so it
    # cannot retain stale Next markup or a different Recent Evidence table.
    combined = student_root / "class_student_packet.html"
    manifest_path = out_dir / "results_manifest.json"
    if combined.is_file() and manifest_path.is_file():
        manifest = runtime.read_json(manifest_path)
        articles: list[str] = []
        for row in manifest.get("students", []):
            rel = _clean(row.get("report"))
            report = out_dir / rel if rel else None
            if report is None or not report.is_file():
                continue
            doc = report.read_text(encoding="utf-8")
            m = re.search(r'(<article class="student-report">.*?</article>)', doc, re.S)
            if m:
                articles.append(m.group(1))
        if articles:
            doc = combined.read_text(encoding="utf-8")
            doc = re.sub(r'(?s)(<body[^>]*>).*?(</body>)', lambda m: m.group(1) + "\n" + "\n".join(articles) + "\n" + m.group(2), doc, count=1)
            if next_pattern.search(doc) or "<b>Next:</b>" in doc:
                raise ValueError("Portfolio cleanup failed: retired per-I-Can Next line remains in combined report")
            combined.write_text(doc, encoding="utf-8")


def _teacher_breakdown_data(state_dir: Path, out_dir: Path) -> dict[str, Any]:
    """Build current teacher-facing breakdown and routing from local Portfolio state."""
    _fields, current_rows = recalculate_state_dir(Path(state_dir))
    registry_path = Path(state_dir) / "student_registry.csv"
    _rf, registry = runtime.read_csv(registry_path) if registry_path.is_file() else ([], [])
    active = [r for r in registry if _clean(r.get("active")).lower() in {"yes", "true", "1", "y"}]
    if not active:
        keys = sorted({_clean(r.get("student_key")) for r in current_rows if _clean(r.get("student_key"))})
        active = [{"student_key": k, "display_name": k, "student_name": k, "period": ""} for k in keys]
    active_by = {_clean(r.get("student_key")): r for r in active}
    active_keys = set(active_by)
    rows = [r for r in current_rows if _clean(r.get("student_key")) in active_keys]

    def mg_sort(mid: str):
        m = re.search(r"(?:MG)?0*(\d+)$", _clean(mid), re.I)
        return (int(m.group(1)) if m else 9999, _clean(mid))

    def ican_sort(iid: str):
        m = re.search(r"IC0*(\d+)$", _clean(iid), re.I)
        return (int(m.group(1)) if m else 9999, _clean(iid))

    mg_titles: dict[str, str] = {}
    mg_state = Path(state_dir) / "mastery_goal_status_current.csv"
    if mg_state.is_file():
        _mf, mrows = runtime.read_csv(mg_state)
        for row in mrows:
            mid = runtime.mg_id(row)
            title = _clean(row.get("mastery_goal_title"))
            if mid and title and mid not in mg_titles:
                mg_titles[mid] = title

    text_by_ican: dict[str, str] = {}
    mg_by_ican: dict[str, str] = {}
    for row in rows:
        iid = _clean(row.get("i_can_id"))
        mid = runtime.mg_id(row)
        if iid:
            text_by_ican.setdefault(iid, _clean(row.get("i_can_text") or row.get("i_can_exact_text")))
            if mid:
                mg_by_ican[iid] = mid

    by_student_mg: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_student_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_ican: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        sk = _clean(row.get("student_key"))
        mid = runtime.mg_id(row)
        iid = _clean(row.get("i_can_id"))
        if sk:
            by_student_rows[sk].append(row)
        if sk and mid:
            by_student_mg[(sk, mid)].append(row)
        if iid:
            by_ican[iid].append(row)

    mg_order = sorted({mid for (_sk, mid) in by_student_mg}, key=mg_sort)
    grades: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for (sk, mid), rr in by_student_mg.items():
        grades[sk][mid] = mg_grade(rr)

    practice_by_student: dict[str, list[dict[str, str]]] = {}
    fb_goal_count: dict[str, int] = {}
    f_goal_count: dict[str, int] = {}
    for sk in active_keys:
        practice = [r for r in by_student_rows.get(sk, []) if _clean(r.get("student_action_code")) == "PRACTICE_AND_CHECK"]
        practice_by_student[sk] = practice
        infos = list(grades.get(sk, {}).values())
        fb_goal_count[sk] = sum(1 for x in infos if _clean(x.get("report_display")) in {"Falling Behind", "F"})
        f_goal_count[sk] = sum(1 for x in infos if _clean(x.get("report_display")) == "F")

    def student_name(sk: str) -> str:
        row = active_by.get(sk, {})
        return _clean(row.get("display_name") or row.get("student_name")) or sk

    def student_period(sk: str) -> str:
        return _clean(active_by.get(sk, {}).get("period"))

    gap_count = {sk: len(practice_by_student.get(sk, [])) for sk in active_keys}
    pull_keys = sorted([sk for sk, n in gap_count.items() if 1 <= n <= 2], key=lambda sk: (student_period(sk), student_name(sk), sk))

    priority: list[dict[str, Any]] = []
    for sk in active_keys:
        practice = practice_by_student.get(sk, [])
        if not practice or fb_goal_count.get(sk, 0) < 1:
            continue
        sev = Counter(_clean(r.get("latest_strength")).upper() for r in practice)
        priority.append({
            "student_key": sk,
            "practice": practice,
            "fb": fb_goal_count.get(sk, 0),
            "f": f_goal_count.get(sk, 0),
            "severity": (sev.get("UNUSABLE", 0), sev.get("LIMITED", 0), sev.get("PARTIAL", 0)),
        })
    priority.sort(key=lambda x: (-x["f"], -x["fb"], -len(x["practice"]), -x["severity"][0], -x["severity"][1], -x["severity"][2], x["student_key"]))
    g1, g2, wait = priority[:15], priority[15:30], priority[30:]

    practice_counts = Counter(_clean(r.get("i_can_id")) for rr in practice_by_student.values() for r in rr if _clean(r.get("i_can_id")))
    whole_ic, whole_count = practice_counts.most_common(1)[0] if practice_counts else ("", 0)
    whole_active = bool(whole_ic and whole_count >= max(5, round(len(active) * 0.6)))

    one_gap = sum(1 for n in gap_count.values() if n == 1)
    two_gap = sum(1 for n in gap_count.values() if n == 2)
    three_plus = sum(1 for n in gap_count.values() if n >= 3)
    fb_growth = sum(1 for sk in active_keys if any(_clean(x.get("report_display")) == "Falling Behind" for x in grades.get(sk, {}).values()))
    f_students = sum(1 for sk in active_keys if f_goal_count.get(sk, 0) > 0)
    no_concern = sum(1 for sk in active_keys if gap_count.get(sk, 0) == 0 and fb_goal_count.get(sk, 0) == 0)
    practice_total = sum(gap_count.values())

    manifest_path = out_dir / "results_manifest.json"
    manifest = runtime.read_json(manifest_path) if manifest_path.is_file() else {}
    course = _clean(manifest.get("course"))
    unit = manifest.get("unit", "")
    latest = manifest.get("latest_evidence") if isinstance(manifest.get("latest_evidence"), dict) else {}
    latest_label = _clean(latest.get("label")) or "Current state"
    latest_date = _clean(latest.get("date"))

    mg_cards: list[str] = []
    for mid in mg_order:
        dist = Counter()
        for sk in active_keys:
            info = grades.get(sk, {}).get(mid)
            display = _clean(info.get("report_display")) if info else "Not Yet Assessed"
            if display == "—" or not display:
                display = "Building"
            dist[display] += 1
        actionable = sum(1 for r in rows if runtime.mg_id(r) == mid and _clean(r.get("student_action_code")) == "PRACTICE_AND_CHECK")
        title = mg_titles.get(mid, "")
        short = mid.replace(f"U{unit}-", "") if unit != "" else mid
        heading = html.escape(short) + (f" · {html.escape(title)}" if title else "")
        mg_cards.append(
            '<div class="teacher-mg-card">'
            f'<div class="teacher-mg-title">{heading}</div>'
            '<div class="teacher-grade-line">'
            f'<span><b>A+</b> {dist.get("A+",0)}</span><span><b>A</b> {dist.get("A",0)}</span><span><b>B</b> {dist.get("B",0)}</span><span><b>C</b> {dist.get("C",0)}</span>'
            '</div>'
            '<div class="teacher-grade-line">'
            f'<span><b>Falling Behind</b> {dist.get("Falling Behind",0)}</span><span><b>F</b> {dist.get("F",0)}</span><span><b>Building/NYA</b> {dist.get("Building",0)+dist.get("Not Yet Assessed",0)}</span>'
            '</div>'
            f'<div class="teacher-actionable"><b>{actionable}</b> Practice + check I Can placement(s)</div>'
            '</div>'
        )

    ican_rows_html: list[str] = []
    ranked_iids = sorted(
        by_ican,
        key=lambda iid: (
            -sum(_canonical_status(r.get("status_code")) in {"STARTED", "DEVELOPING"} for r in by_ican[iid]),
            mg_sort(mg_by_ican.get(iid, "")),
            ican_sort(iid),
        ),
    )[:6]
    for iid in ranked_iids:
        counts = Counter(_canonical_status(r.get("status_code")) for r in by_ican[iid])
        practice_n = counts.get("STARTED", 0) + counts.get("DEVELOPING", 0)
        mastered_plus = counts.get("MASTERED", 0) + counts.get("EXTENDED", 0)
        ican_rows_html.append(
            '<tr>'
            f'<td><b>{html.escape(iid)}</b><div class="teacher-ican-text">{html.escape(text_by_ican.get(iid,""))}</div></td>'
            f'<td>{counts.get("NOT_YET_ASSESSED",0)}</td><td>{counts.get("STARTED",0)}</td><td>{counts.get("DEVELOPING",0)}</td><td>{counts.get("PROGRESSING",0)}</td><td>{mastered_plus}</td><td><b>{practice_n}</b></td>'
            '</tr>'
        )
    if not ican_rows_html:
        ican_rows_html.append('<tr><td colspan="7">No current I Can status rows are available.</td></tr>')

    latest_lines: list[str] = []
    ledger_path = Path(state_dir) / "evidence_ledger.csv"
    if ledger_path.is_file():
        _lf, ledger = runtime.read_csv(ledger_path)
        latest_by_ic: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in ledger:
            if _clean(row.get("source_label")) == latest_label and (not latest_date or _clean(row.get("source_date")) == latest_date):
                iid = _clean(row.get("i_can_id"))
                if iid:
                    latest_by_ic[iid].append(row)
        for iid in sorted(latest_by_ic, key=lambda x: (-len(latest_by_ic[x]), x))[:3]:
            c = Counter(_clean(x.get("strength")).upper() for x in latest_by_ic[iid])
            latest_lines.append(
                f'<li><b>{html.escape(iid)} · {html.escape(text_by_ican.get(iid,""))}</b> — {c.get("CONVINCING",0)} convincing, {c.get("PARTIAL",0)} partial, {c.get("LIMITED",0)} limited, {c.get("UNUSABLE",0)} unusable across {len(latest_by_ic[iid])} source-level judgment(s).</li>'
            )
    latest_html = '<ul>' + ''.join(latest_lines) + '</ul>' if latest_lines else '<p>No source-level evidence judgments were added in the latest run.</p>'

    whole_text = (
        f'{html.escape(whole_ic)} · {whole_count} students need Practice + check soon.'
        if whole_active else 'No broad shared target is currently supported.'
    )
    whole_detail = (
        f'Whole Class is active for {html.escape(whole_ic)} ({whole_count} students).'
        if whole_active else 'No single Practice + check target currently reaches the Whole Class threshold.'
    )

    overview_html = f'''
  <div class="report-head">
    <div><div class="eyebrow">{html.escape(course)} - Unit {html.escape(str(unit))} Portfolio</div><h1>Class Overview</h1></div>
    <div class="meta"><b>Latest evidence:</b> {html.escape(latest_label)}<br>{html.escape(latest_date)}<br><b>Active students:</b> {len(active)}</div>
  </div>

  <div class="grid4">
    <div class="stat"><strong>{len(active)}</strong><span>Active students</span></div>
    <div class="stat"><strong>{len(priority)}</strong><span>Priority Day eligible now</span></div>
    <div class="stat"><strong>{len(pull_keys)}</strong><span>Pull In students with 1-2 actionable gaps</span></div>
    <div class="stat"><strong>{f_students}</strong><span>Students currently meeting an F condition</span></div>
  </div>

  <div class="section teacher-mg-breakdown">
    <h2>Mastery Goal breakdown</h2>
    <div class="teacher-mg-grid">{''.join(mg_cards)}</div>
  </div>

  <div class="grid2 teacher-breakdown-grid">
    <div class="section">
      <h2>Top actionable I Cans</h2>
      <table class="teacher-ican-table"><thead><tr><th>I Can</th><th>NYA</th><th>Started</th><th>Developing</th><th>Progressing</th><th>Mastered+</th><th>Practice</th></tr></thead><tbody>{''.join(ican_rows_html)}</tbody></table>
    </div>
    <div class="section">
      <h2>Intervention breakdown</h2>
      <div class="teacher-route-grid">
        <div><b>{no_concern}</b><span>No current concern</span></div>
        <div><b>{fb_growth}</b><span>Falling Behind but showing growth</span></div>
        <div><b>{f_students}</b><span>F condition</span></div>
        <div><b>{one_gap}</b><span>1 actionable I Can</span></div>
        <div><b>{two_gap}</b><span>2 actionable I Cans</span></div>
        <div><b>{three_plus}</b><span>3+ actionable I Cans</span></div>
      </div>
      <p class="teacher-route-note"><b>{practice_total}</b> total Practice + check placements. {whole_detail}</p>
    </div>
  </div>

  <div class="grid3 teacher-lane-grid">
    <div class="lane"><div class="num">{'1 target' if whole_active else '0'}</div><div class="label">Whole Class</div><p>{whole_text}</p></div>
    <div class="lane"><div class="num">{len(priority)}</div><div class="label">Priority Day eligible</div><p>Falling Behind/F plus at least one Practice + check target. The first 30 fill the two weekly groups.</p></div>
    <div class="lane"><div class="num">{len(pull_keys)}</div><div class="label">Pull In Students</div><p>Exactly 1-2 actionable Practice + check gaps. This lane does not require a Falling Behind/F goal.</p></div>
  </div>

  <div class="section soft latest-picture">
    <h2>Latest evidence picture — {html.escape(latest_label)}</h2>
    {latest_html}
  </div>
'''

    def target_chips(group: list[dict[str, Any]]) -> str:
        c = Counter(_clean(r.get("i_can_id")) for x in group for r in x["practice"] if _clean(r.get("i_can_id")))
        return ''.join(f'<span class="chip{" hot" if i==0 else ""}">{html.escape(iid)} × {n}</span>' for i, (iid, n) in enumerate(c.most_common(7)))

    def student_rows(group: list[dict[str, Any]]) -> str:
        return ''.join(
            f'<div class="student-row"><b>{html.escape(student_name(x["student_key"]))}</b><div class="codes">{html.escape(", ".join(_clean(r.get("i_can_id")) for r in x["practice"] if _clean(r.get("i_can_id"))))}</div></div>'
            for x in group
        )

    def group_summary(group: list[dict[str, Any]]) -> str:
        c = Counter(_clean(r.get("i_can_id")) for x in group for r in x["practice"] if _clean(r.get("i_can_id")))
        tops = c.most_common(3)
        if not tops:
            return "No eligible students are currently assigned to this group."
        desc = ", ".join(f"{iid} ({n})" for iid, n in tops)
        return f"The dominant overlapping Practice + check targets are {desc}. Use one common model-practice-check routine, then give a short alternate strip to students with outlier targets."

    timeline = '<b>0-4 min</b><span>Model one clean example and name the decision point.</span><b>4-10 min</b><span>Guided practice on the dominant shared target.</span><b>10-16 min</b><span>Independent parallel item; short alternate strip for outlier targets.</span><b>16-20 min</b><span>Quick feedback and route each student to practice or another independent demonstration.</span>'

    def group_card(group: list[dict[str, Any]], number: int, cls: str) -> str:
        if not group:
            return f'<div class="group-card {cls}"><div class="group-title"><div><div class="eyebrow">Priority</div><div class="rank">Group {number}</div></div><div class="count"><b>0 students</b></div></div><p>No eligible students currently fill this group.</p></div>'
        start_rank = 1 if number == 1 else 16
        end_rank = start_rank + len(group) - 1
        return f'<div class="group-card {cls}"><div class="group-title"><div><div class="eyebrow">{"First priority" if number==1 else "Second priority"}</div><div class="rank">Group {number}</div></div><div class="count"><b>{len(group)} students</b><br>Ranks {start_rank}-{end_rank}</div></div><div class="mix">{target_chips(group)}</div><div class="student-list">{student_rows(group)}</div><div class="crew-plan"><h3>Best use of the 20-minute Crewtime</h3><p>{html.escape(group_summary(group))}</p><div class="timeline">{timeline}</div></div></div>'

    priority_html = f'''
  <div class="report-head">
    <div><div class="eyebrow">{html.escape(course)} - Unit {html.escape(str(unit))} Portfolio</div><h1>Priority Day Groups</h1></div>
    <div class="meta"><b>Eligible now:</b> {len(priority)}<br><b>Rule:</b> Falling Behind/F + Practice + check<br><b>Capacity:</b> 2 groups · 15 students each</div>
  </div>
  <div class="priority-note">Ranked by current F condition first, then total Falling Behind/F goals, actionable-gap count, evidence severity, and stable student key.</div>
  <div class="grid2 priority-grid">{group_card(g1,1,'first')}{group_card(g2,2,'second')}</div>
  {'' if not wait else f'<div class="priority-waitlist">{len(wait)} additional eligible student(s) remain after Group 2 capacity.</div>'}
'''

    pull_cards: list[str] = []
    pull_mix = Counter()
    for sk in pull_keys:
        needs = []
        for r in practice_by_student.get(sk, []):
            iid = _clean(r.get("i_can_id"))
            if not iid:
                continue
            pull_mix[iid] += 1
            needs.append(f'<div class="need"><b>{html.escape(iid)}</b> · {html.escape(text_by_ican.get(iid,""))}</div>')
        pull_cards.append(f'<div class="pull-card"><div class="name">{html.escape(student_name(sk))}</div><div class="period">{html.escape(student_period(sk))}</div>{"".join(needs)}</div>')
    if not pull_cards:
        pull_cards.append('<div class="pull-empty">No students currently have exactly 1-2 Practice + check gaps.</div>')
    pull_html = f'''
  <div class="report-head">
    <div><div class="eyebrow">{html.escape(course)} - Unit {html.escape(str(unit))} Portfolio</div><h1>Pull In Students</h1></div>
    <div class="meta"><b>Lane:</b> exactly 1-2 Practice + check gaps<br><b>Latest evidence:</b> {html.escape(latest_label)} - {html.escape(latest_date)}</div>
  </div>
  <div class="pull-banner"><div class="big">ALL {len(pull_keys)} STUDENTS: PRACTICE + CHECK SOON</div><div class="sub">This lane is based on actionable gap count.<br>Falling Behind/F is not required.</div></div>
  <div class="pull-grid {'cols4' if len(pull_keys)>9 else ''}">{''.join(pull_cards)}</div>
  <div class="footer-note"><span>Students who only need another independent demonstration are intentionally kept out of this lane.</span><span>{html.escape(' · '.join(f'{k} × {v}' for k,v in pull_mix.most_common()))}</span></div>
'''

    return {"overview_html": overview_html, "priority_html": priority_html, "pull_html": pull_html}


def _postprocess_teacher_copy(out_dir: Path, state_dir: Path | None) -> None:
    path = out_dir / "teacher_report" / "teacher_summary.html"
    if not path.is_file():
        return
    doc = path.read_text(encoding="utf-8")
    replacements = {
        "Current Mastery Goal grades of I": "Mastery Goals needing intervention",
        "at least one current assessed Mastery Goal grade I": "at least one current Falling Behind/F Mastery Goal",
        "current assessed MG grades I": "current Falling Behind/F Mastery Goals",
        "assessed MG grades I": "Falling Behind/F Mastery Goals",
        "Ranked by I-grade count": "Ranked by Falling Behind/F goal count",
        "I-grade count": "Falling Behind/F goal count",
        "I-grade intervention need": "Falling Behind/F intervention need",
    }
    for old, new in replacements.items():
        doc = doc.replace(old, new)

    if state_dir is not None:
        data = _teacher_breakdown_data(Path(state_dir), out_dir)
        if "{{PROGRESS_MODEL_CLASS_OVERVIEW_HTML}}" in doc:
            doc = doc.replace("{{PROGRESS_MODEL_CLASS_OVERVIEW_HTML}}", data["overview_html"])
        else:
            doc = re.sub(r'(?s)(<section class="teacher-page">).*?(</section>)', lambda m: m.group(1) + data["overview_html"] + m.group(2), doc, count=1)
        if "{{PROGRESS_MODEL_PRIORITY_DAY_HTML}}" in doc:
            doc = doc.replace("{{PROGRESS_MODEL_PRIORITY_DAY_HTML}}", data["priority_html"])
        else:
            doc = re.sub(r'(?s)(<section class="teacher-page priority-page">).*?(</section>)', lambda m: m.group(1) + data["priority_html"] + m.group(2), doc, count=1)
        if "{{PROGRESS_MODEL_PULL_IN_HTML}}" in doc:
            doc = doc.replace("{{PROGRESS_MODEL_PULL_IN_HTML}}", data["pull_html"])
        else:
            doc = re.sub(r'(?s)(<section class="teacher-page pull-page">).*?(</section>)', lambda m: m.group(1) + data["pull_html"] + m.group(2), doc, count=1)

    path.write_text(doc, encoding="utf-8")

class _DeferredValidatorSubprocess:
    """Let the legacy renderer finish, then validate the final cleaned output."""

    def __init__(self, real: Any):
        self._real = real

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)

    def run(self, cmd: Any, *args: Any, **kwargs: Any):
        try:
            parts = [str(x) for x in cmd]
        except TypeError:
            parts = [str(cmd)]
        if any(Path(x).name == "verify_portfolio_output.py" for x in parts):
            return self._real.CompletedProcess(cmd, 0, stdout="Deferred until final Portfolio cleanup.\n")
        return self._real.run(cmd, *args, **kwargs)


def _run_final_validator(out_dir: Path) -> None:
    templates = Path(runtime.__file__).resolve().parent.parent / "templates" / "portfolio"
    validator = templates / "verify_portfolio_output.py"
    qa_json = out_dir / "qa" / "template_validation.json"
    cmd = [
        "/usr/bin/python3",
        str(validator),
        "--results",
        str(out_dir),
        "--templates",
        str(templates),
        "--write-json",
        str(qa_json),
    ]
    proc = runtime.subprocess.run(cmd, stdout=runtime.subprocess.PIPE, stderr=runtime.subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise ValueError("Canonical Portfolio template validator failed after final cleanup:\n" + proc.stdout)


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

    # The legacy builder runs template QA before this overlay can remove its
    # retired per-I-Can Next markup. Defer only that validator invocation, then
    # run the canonical validator on the actual final report bytes below.
    real_subprocess = runtime.subprocess
    runtime.subprocess = _DeferredValidatorSubprocess(real_subprocess)
    try:
        manifest = _ORIGINAL_BUILD_RESULTS(*args, **kwargs)
    finally:
        runtime.subprocess = real_subprocess

    out = kwargs.get("out_dir")
    if out is None and len(args) >= 13:
        out = args[12]
    if out is not None:
        out_path = Path(out)
        _postprocess_student_markup(out_path, state_dir)
        _postprocess_teacher_copy(out_path, state_dir)
        _run_final_validator(out_path)
        manifest_path = out_path / "results_manifest.json"
        if manifest_path.is_file():
            manifest = runtime.read_json(manifest_path)
            manifest.setdefault("qa", {})["template_fidelity_status"] = "PASS"
            manifest["qa"]["identity_status"] = "PASS"
            manifest["status"] = "PASS"
            runtime.write_json(manifest_path, manifest)
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
