#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import hashlib
import html
import json
import mimetypes
import re
import shutil
import time
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

import print_layout_assets

ICAN_RE = re.compile(r"U(\d+)-MG(\d{2})-IC(\d{2})", re.I)
STUDENT_KEYS = (
    "student_name", "student", "name", "display_name", "student_display_name",
    "student_id", "sis_id", "id", "local_id", "student_key",
)
ROSTER_STUDENT_KEYS = (
    "student_name", "student", "display_name", "student_display_name",
    "student_id", "sis_id", "local_id", "student_key",
)
STATUS_KEYS = (
    "status", "mastery_status", "evidence_status", "current_status", "assessment_status",
    "portfolio_status", "decision", "rating", "level", "label", "status_label",
    "display_status", "level_label", "progress_status", "status_code",
    "recheck_status", "needs_recheck", "needs_reassessment", "needs_evidence", "needs_more_evidence",
)
BAR_KEYS = (
    "mastery_bars", "bar_count", "bars", "filled_bars", "filled_bar_count",
    "mastery_level", "progress_level", "score", "level", "rating",
)
COUNT_KEYS = (
    "observation_count", "observations", "evidence_count", "count", "num_observations",
    "assessment_count", "pieces_of_evidence", "source_opportunity_count",
)

NEED_TERMS = {
    "needs recheck": 100,
    "needs_recheck": 100,
    "re-check": 100,
    "recheck": 100,
    "retry": 95,
    "not secure": 95,
    "not_secure": 95,
    "reassess": 100,
    "reassessment": 100,
    "needs reassessment": 100,
    "needs_reassessment": 100,
    "not yet": 95,
    "not_yet": 95,
    "needs evidence": 90,
    "needs_evidence": 90,
    "needs more evidence": 90,
    "needs_more_evidence": 90,
    "insufficient": 85,
    "developing": 75,
    "emerging": 75,
    "partial": 65,
    "in progress": 60,
    "in_progress": 60,
}
CHECKPOINT_OUTPUT_SCHEMA_VERSION = 22

SECURE_TERMS = {
    "mastered", "mastery", "secure", "proficient", "complete", "completed",
    "full", "meets", "met", "advanced", "exceeds",
}


@dataclass
class EvidenceRecord:
    student: str
    i_can_id: str
    status: str
    mastery_bars: int | None
    observation_count: int | None
    source: str
    source_mtime: float
    priority: int


@dataclass
class BankFamily:
    family_id: str
    teacher_question_id: str
    i_can_id: str
    family_label: str
    family_name: str
    approval_status: str
    product_eligibility: list[str]
    exemplar: dict[str, Any]
    authoring_reference: dict[str, Any]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value).strip()
    return ""


def normalize_ican(value: Any, unit: int | None = None) -> str | None:
    text = normalize_text(value)
    m = ICAN_RE.search(text)
    if not m:
        return None
    found_unit = int(m.group(1))
    if unit is not None and found_unit != int(unit):
        return None
    return f"U{found_unit}-MG{m.group(2)}-IC{m.group(3)}"


def ican_sort_key(value: str) -> tuple[int, int, int, str]:
    m = ICAN_RE.search(str(value))
    if not m:
        return (999, 999, 999, str(value))
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), str(value))


def parse_count(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float) and value.is_integer():
        return max(0, int(value))
    text = normalize_text(value)
    if text.isdigit():
        return int(text)
    return None


def parse_mastery_bars(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        n = int(value)
        if float(value) == n and 0 <= n <= 5:
            return n
    text = normalize_text(value).lower()
    if not text:
        return None
    m = re.fullmatch(r"([0-5])(?:\s*(?:/\s*5|bars?))?", text)
    if m:
        return int(m.group(1))
    label_map = (
        ("extended", 5),
        ("mastered", 4),
        ("mastery", 4),
        ("progressing", 3),
        ("developing", 2),
        ("started", 1),
        ("not yet assessed", 0),
        ("not_yet_assessed", 0),
        ("no_evidence", 0),
        ("transfer", 5),
    )
    for term, bars in label_map:
        if term in text:
            return bars
    return None


def dict_value_ci(obj: dict[str, Any], keys: Iterable[str]) -> Any:
    lower = {str(k).lower(): v for k, v in obj.items()}
    for key in keys:
        if key.lower() in lower:
            return lower[key.lower()]
    return None


def student_from_dict(obj: dict[str, Any], inherited: str | None = None) -> str | None:
    value = dict_value_ci(obj, STUDENT_KEYS)
    text = normalize_text(value)
    if text and len(text) <= 160:
        return text
    return inherited


def roster_student_from_dict(obj: dict[str, Any]) -> str | None:
    value = dict_value_ci(obj, ROSTER_STUDENT_KEYS)
    text = normalize_text(value)
    if text and len(text) <= 160:
        return text
    return None


def status_from_dict(obj: dict[str, Any]) -> str:
    lower = {str(k).lower(): v for k, v in obj.items()}
    # Portfolio tools may store the current evidence decision as a boolean flag
    # instead of a free-text status. Treat an explicit true/yes/1 need flag as a need.
    for key, label in (
        ("needs_recheck", "needs recheck"),
        ("needs_reassessment", "needs reassessment"),
        ("needs_evidence", "needs evidence"),
        ("needs_more_evidence", "needs more evidence"),
        ("recheck", "recheck"),
    ):
        if key not in lower:
            continue
        value = lower[key]
        if value is True or normalize_text(value).lower() in {"true", "yes", "y", "1", "needed", "need"}:
            return label
    value = dict_value_ci(obj, STATUS_KEYS)
    return normalize_text(value)


def bars_from_dict(obj: dict[str, Any]) -> int | None:
    return parse_mastery_bars(dict_value_ci(obj, BAR_KEYS))


def count_from_dict(obj: dict[str, Any]) -> int | None:
    return parse_count(dict_value_ci(obj, COUNT_KEYS))


def priority_from(status: str, count: int | None) -> int:
    low = status.lower().strip()
    for term, score in NEED_TERMS.items():
        if term in low:
            return score * 100 - min(count or 0, 20)
    if any(term in low for term in SECURE_TERMS):
        return 0
    if count is not None:
        if count <= 0:
            return 7000
        if count == 1:
            return 6000
        return 0
    return 0


def extract_records_from_json(data: Any, source: Path, unit: int | None = None) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    mtime = source.stat().st_mtime if source.exists() else 0.0

    def emit(student: str | None, ican: str | None, obj: dict[str, Any], status_override: Any = None, count_override: Any = None, bars_override: Any = None) -> None:
        if not student or not ican:
            return
        status = normalize_text(status_override) if status_override is not None else status_from_dict(obj)
        bars = parse_mastery_bars(bars_override) if bars_override is not None else bars_from_dict(obj)
        if bars is None:
            bars = parse_mastery_bars(status)
        count = parse_count(count_override) if count_override is not None else count_from_dict(obj)
        records.append(EvidenceRecord(student, ican, status, bars, count, str(source), mtime, priority_from(status, count)))

    def walk(node: Any, inherited_student: str | None = None) -> None:
        if isinstance(node, dict):
            student = student_from_dict(node, inherited_student)
            direct_ican = None
            # A mapping such as {"U1-MG01-IC01": 4} is handled below by the
            # key-I-Can branch. Do not also emit a blank duplicate record for
            # the first key. Direct-record emission is only for rows/objects
            # where the I Can appears as a field VALUE (for example
            # {"i_can_id": "U1-MG01-IC01", "status": "Mastered"}).
            for k, v in node.items():
                if normalize_ican(k, unit):
                    continue
                direct_ican = normalize_ican(v, unit)
                if direct_ican:
                    break
            if direct_ican:
                emit(student, direct_ican, node)

            for k, v in node.items():
                key_ican = normalize_ican(k, unit)
                if not key_ican:
                    continue
                if isinstance(v, dict):
                    emit(student_from_dict(v, student), key_ican, v)
                else:
                    primitive_bars = parse_mastery_bars(v)
                    emit(student, key_ican, node, status_override=v, bars_override=primitive_bars)

            for v in node.values():
                walk(v, student)
        elif isinstance(node, list):
            for item in node:
                walk(item, inherited_student)

    walk(data)
    return records


def extract_records_from_csv(path: Path, unit: int | None = None) -> list[EvidenceRecord]:
    out: list[EvidenceRecord] = []
    mtime = path.stat().st_mtime
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                student = student_from_dict(row)
                ican = None
                for k, v in row.items():
                    ican = normalize_ican(k, unit) or normalize_ican(v, unit)
                    if ican:
                        break
                if not student or not ican:
                    continue
                status = status_from_dict(row)
                bars = bars_from_dict(row)
                if bars is None:
                    bars = parse_mastery_bars(status)
                count = count_from_dict(row)
                out.append(EvidenceRecord(student, ican, status, bars, count, str(path), mtime, priority_from(status, count)))
    except (OSError, csv.Error, UnicodeDecodeError):
        pass
    return out


def extract_roster_students_from_json(data: Any) -> set[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            s = roster_student_from_dict(node)
            if s:
                found.add(s)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    return found


def extract_roster_students_from_csv(path: Path) -> set[str]:
    found: set[str] = set()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                s = roster_student_from_dict(row)
                if s:
                    found.add(s)
    except (OSError, csv.Error, UnicodeDecodeError):
        pass
    return found


def candidate_portfolio_roots(github_root: Path) -> list[Path]:
    home = Path.home()
    candidates = [
        github_root / "_portfolio_data",
        home / "GitHub" / "_portfolio_data",
        home / "Documents" / "GitHub" / "_portfolio_data",
        github_root / "____Portfolio_Data",
        home / "GitHub" / "____Portfolio_Data",
        home / "Documents" / "GitHub" / "____Portfolio_Data",
    ]
    seen: set[str] = set()
    result: list[Path] = []
    for p in candidates:
        key = str(p.expanduser().resolve(strict=False))
        if key in seen:
            continue
        seen.add(key)
        if p.is_dir():
            result.append(p)
    return result


def _machine_files(roots: list[Path]) -> list[Path]:
    all_files: list[Path] = []
    algebra_files: list[Path] = []
    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".json", ".csv"}:
                continue
            if any(part.startswith(".") for part in p.parts):
                continue
            try:
                if p.stat().st_size > 8_000_000:
                    continue
            except OSError:
                continue
            all_files.append(p)
            low = str(p).lower()
            if "algebra" in low or "alg1" in low or "alg_1" in low:
                algebra_files.append(p)
    return sorted(set(algebra_files or all_files), key=lambda p: str(p).lower())


def _zip_csv_rows(zf: zipfile.ZipFile, basename: str) -> list[dict[str, str]]:
    """Read a CSV from a Portfolio state ZIP by basename.

    Current Portfolio state ZIPs store their live state under ``state/``. The
    basename lookup also keeps this compatible with an older flat archive.
    """
    target = next((name for name in zf.namelist() if Path(name).name == basename), None)
    if not target:
        return []
    try:
        text = zf.read(target).decode("utf-8-sig")
        return [dict(row) for row in csv.DictReader(text.splitlines())]
    except (KeyError, UnicodeDecodeError, csv.Error):
        return []


def _portfolio_state_scan(github_root: Path, unit: int | None = None) -> dict[str, Any] | None:
    """Read the same current I Can state used by Portfolio progress reports.

    Checkpoint should consume the deterministic Portfolio output, not try to
    reinterpret raw grading-result files. Each unit's Portfolio_State_CURRENT
    archive contains ``student_registry.csv`` and ``i_can_status_current.csv``.
    """
    roots = candidate_portfolio_roots(github_root)
    state_zips: list[Path] = []
    for root in roots:
        course_root = root / "Algebra 1"
        if not course_root.is_dir():
            continue
        for path in course_root.glob("unit */02 Portfolio Data/Portfolio_State_CURRENT.zip"):
            m = re.fullmatch(r"unit\s+(\d+)", path.parents[1].name, re.I)
            if unit is not None and (not m or int(m.group(1)) != int(unit)):
                continue
            state_zips.append(path)

    if not state_zips:
        return None

    records: list[EvidenceRecord] = []
    students: set[str] = set()
    scanned: list[str] = []

    for path in sorted(set(state_zips), key=lambda p: str(p).lower()):
        scanned.append(str(path))
        try:
            with zipfile.ZipFile(path) as zf:
                try:
                    manifest = json.loads(zf.read("STATE_MANIFEST.json").decode("utf-8"))
                except Exception:
                    manifest = {}
                if manifest and manifest.get("course") not in {None, "", "Algebra 1"}:
                    continue
                if manifest and manifest.get("status") not in {None, "", "CURRENT"}:
                    continue

                roster_rows = _zip_csv_rows(zf, "student_registry.csv")
                status_rows = _zip_csv_rows(zf, "i_can_status_current.csv")
        except (OSError, zipfile.BadZipFile):
            continue

        roster_by_key: dict[str, dict[str, str]] = {}
        active_keys: set[str] = set()
        for row in roster_rows:
            key = normalize_text(row.get("student_key") or row.get("student_id") or row.get("student_num"))
            if not key:
                continue
            active = normalize_text(row.get("active") or "yes").lower() not in {"no", "false", "0", "inactive"}
            if not active:
                continue
            name = normalize_text(row.get("display_name") or row.get("student_name") or row.get("name"))
            if not name:
                name = key
            roster_by_key[key] = row
            active_keys.add(key)
            students.add(name)

        mtime = path.stat().st_mtime if path.exists() else 0.0
        for row in status_rows:
            key = normalize_text(row.get("student_key") or row.get("student_id") or row.get("student_num"))
            if active_keys and key not in active_keys:
                continue
            ican = normalize_ican(row.get("i_can_id"), unit)
            if not key or not ican:
                continue
            roster = roster_by_key.get(key, {})
            student = normalize_text(
                roster.get("display_name") or roster.get("student_name") or
                row.get("display_name") or row.get("student_name") or key
            )
            students.add(student)
            status = normalize_text(row.get("status_label") or row.get("status_code"))
            status_code = normalize_text(row.get("status_code"))
            bars = parse_mastery_bars(status_code) or parse_mastery_bars(status)
            # Preserve zero explicitly; ``or`` above is only unsafe for zero.
            if parse_mastery_bars(status_code) == 0 or (not status_code and parse_mastery_bars(status) == 0):
                bars = 0
            count = parse_count(row.get("source_opportunity_count"))
            records.append(EvidenceRecord(
                student=student,
                i_can_id=ican,
                status=status or status_code,
                mastery_bars=bars,
                observation_count=count,
                source=f"{path}::state/i_can_status_current.csv",
                source_mtime=mtime,
                priority=priority_from(status or status_code, count),
            ))

    if not records and not students:
        return None

    # There is exactly one current row per student/I Can in the authoritative
    # state. If multiple unit archives somehow contribute the same pair, keep
    # the newest installed state archive.
    latest: dict[tuple[str, str], EvidenceRecord] = {}
    for record in records:
        key = (record.student, record.i_can_id)
        old = latest.get(key)
        if old is None or record.source_mtime >= old.source_mtime:
            latest[key] = record

    return {
        "portfolio_roots": [str(p) for p in roots],
        "files_scanned": scanned,
        "records": [asdict(r) for r in latest.values()],
        "students": sorted(students, key=lambda s: s.lower()),
        "source_mode": "Portfolio_State_CURRENT",
    }


def scan_portfolio(github_root: Path, unit: int | None = None) -> dict[str, Any]:
    # Prefer Portfolio's deterministic current state. This is the same source
    # that drives the visible progress bars and status labels in reports.
    current_state = _portfolio_state_scan(github_root, unit)
    if current_state is not None:
        return current_state

    # Fallback for a machine that has not yet produced a current state ZIP.
    roots = candidate_portfolio_roots(github_root)
    files = _machine_files(roots)
    records: list[EvidenceRecord] = []
    students: set[str] = set()
    scanned: list[str] = []

    for path in files:
        scanned.append(str(path))
        low = str(path).lower()
        roster_likely = any(token in low for token in ("roster", "student", "class", "registry", "portfolio", "status", "observation"))
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            recs = extract_records_from_json(data, path, unit)
            records.extend(recs)
            students.update(r.student for r in recs)
            if roster_likely:
                students.update(extract_roster_students_from_json(data))
        else:
            recs = extract_records_from_csv(path, unit)
            records.extend(recs)
            students.update(r.student for r in recs)
            if roster_likely:
                students.update(extract_roster_students_from_csv(path))

    latest: dict[tuple[str, str], EvidenceRecord] = {}

    def record_quality(r: EvidenceRecord) -> tuple[int, int, int]:
        # On the same source/time, prefer a record that actually carries the
        # Portfolio level/status over a structural duplicate with blank fields.
        return (
            1 if r.mastery_bars is not None else 0,
            1 if normalize_text(r.status) else 0,
            1 if r.observation_count is not None else 0,
        )

    for r in records:
        key = (r.student, r.i_can_id)
        old = latest.get(key)
        if old is None or (r.source_mtime, record_quality(r), r.priority) > (old.source_mtime, record_quality(old), old.priority):
            latest[key] = r

    students.update(r.student for r in latest.values())
    return {
        "portfolio_roots": [str(p) for p in roots],
        "files_scanned": scanned,
        "records": [asdict(r) for r in latest.values()],
        "students": sorted(students, key=lambda s: s.lower()),
    }


def load_bank_unit(github_root: Path, unit: int) -> dict[str, Any] | None:
    bank_root = github_root / "algebra" / "banks" / f"unit{unit}"
    resolution_path = bank_root / "BANK_RESOLUTION.json"
    qmap_path = bank_root / "QUESTION_ID_MAP.json"
    if not resolution_path.is_file() or not qmap_path.is_file():
        return None
    try:
        resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
        qmap = json.loads(qmap_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    revision_map: dict[str, dict[str, Any]] = {}
    overlay = resolution.get("family_revision_overlay")
    if overlay and (bank_root / overlay).is_file():
        revs = json.loads((bank_root / overlay).read_text(encoding="utf-8"))
        revision_map = {r["family_id"]: r for r in revs.get("revisions", []) if r.get("family_id")}

    families: list[BankFamily] = []
    catalog: dict[str, dict[str, Any]] = {}
    mg_catalog: dict[str, dict[str, Any]] = {}

    for mgid, base_rel in (resolution.get("base_mastery_goal_files") or {}).items():
        base_path = bank_root / base_rel
        if not base_path.is_file():
            continue
        base = json.loads(base_path.read_text(encoding="utf-8"))
        mg_info = base.get("mastery_goal") or {}
        mg_catalog[mgid] = {
            "mg_id": mgid,
            "title": normalize_text(mg_info.get("title") or mg_info.get("exact_text")),
            "exact_text": normalize_text(mg_info.get("exact_text")),
        }
        ext_rel = (resolution.get("extension_mastery_goal_files") or {}).get(mgid)
        ext = json.loads((bank_root / ext_rel).read_text(encoding="utf-8")) if ext_rel and (bank_root / ext_rel).is_file() else {"i_cans": []}
        ext_by = {ic.get("i_can_id"): ic.get("families", []) for ic in ext.get("i_cans", [])}
        for ic in base.get("i_cans", []):
            ican = normalize_ican(ic.get("i_can_id"), unit)
            if not ican:
                continue
            catalog[ican] = {
                "i_can_id": ican,
                "exact_text": normalize_text(ic.get("exact_text")),
                "mg_id": mgid,
                "unit": unit,
            }
            for raw in [*(ic.get("families") or []), *(ext_by.get(ic.get("i_can_id")) or [])]:
                f = dict(raw)
                rev = revision_map.get(f.get("family_id", ""))
                if rev:
                    override = rev.get("override") or {}
                    f.update(override)
                    f["template_contract"] = {**(raw.get("template_contract") or {}), **(override.get("template_contract") or {})}
                    f["exemplar"] = {**(raw.get("exemplar") or {}), **(override.get("exemplar") or {})}
                fid = f.get("family_id", "")
                status = f.get("approval_status") or (qmap.get("items") or {}).get(fid, {}).get("status") or ""
                if f.get("superseded_by"):
                    continue
                if status not in {"APPROVED", "DRAFT_REVIEW"}:
                    continue
                authoring_reference = {
                    key: f.get(key)
                    for key in (
                        "family_id", "family_label", "family_name", "family_purpose",
                        "evidence_job", "student_action", "question_structure_id",
                        "response_mode", "representation_mode", "representation_need",
                        "representation_routes", "difficulty_intent", "invariant",
                        "variation_axes", "forbidden_variations", "allowed_destinations",
                        "best_use", "avoid_uses", "fresh_instance_rule", "exemplar",
                    )
                    if f.get(key) not in (None, "", [], {})
                }
                families.append(BankFamily(
                    family_id=fid,
                    teacher_question_id=(qmap.get("items") or {}).get(fid, {}).get("teacher_question_id", ""),
                    i_can_id=ican,
                    family_label=str(f.get("family_label", "")),
                    family_name=str(f.get("family_name", "")),
                    approval_status=status,
                    product_eligibility=list(f.get("product_eligibility") or f.get("allowed_destinations") or []),
                    exemplar=dict(f.get("exemplar") or {}),
                    authoring_reference=authoring_reference,
                ))

    return {
        "unit": unit,
        "bank_root": str(bank_root),
        "families": [asdict(f) for f in families],
        "catalog": catalog,
        "mg_catalog": mg_catalog,
    }


def load_all_banks(github_root: Path) -> dict[str, Any]:
    bank_base = github_root / "algebra" / "banks"
    units: list[int] = []
    if bank_base.is_dir():
        for p in bank_base.iterdir():
            if not p.is_dir():
                continue
            m = re.fullmatch(r"unit(\d+)", p.name, re.I)
            if m and (p / "BANK_RESOLUTION.json").is_file():
                units.append(int(m.group(1)))
    families: list[dict[str, Any]] = []
    catalog: dict[str, dict[str, Any]] = {}
    mg_catalog: dict[str, dict[str, Any]] = {}
    loaded_units: list[int] = []
    for unit in sorted(set(units)):
        data = load_bank_unit(github_root, unit)
        if not data:
            continue
        loaded_units.append(unit)
        families.extend(data["families"])
        catalog.update(data["catalog"])
        mg_catalog.update(data["mg_catalog"])
    return {"units": loaded_units, "families": families, "catalog": catalog, "mg_catalog": mg_catalog}


def eligibility_catalog(github_root: Path) -> dict[str, Any]:
    scan = scan_portfolio(github_root, None)
    banks = load_all_banks(github_root)
    catalog: dict[str, dict[str, Any]] = {k: dict(v) for k, v in banks["catalog"].items()}
    family_counts: dict[str, int] = {}
    for f in banks["families"]:
        family_counts[f["i_can_id"]] = family_counts.get(f["i_can_id"], 0) + 1

    evidence_counts: dict[str, int] = {}
    for r in scan["records"]:
        ican = normalize_ican(r.get("i_can_id"))
        if not ican:
            continue
        evidence_counts[ican] = evidence_counts.get(ican, 0) + 1
        if ican not in catalog:
            m = ICAN_RE.search(ican)
            if not m:
                continue
            catalog[ican] = {
                "i_can_id": ican,
                "exact_text": "",
                "mg_id": f"U{int(m.group(1))}-MG{m.group(2)}",
                "unit": int(m.group(1)),
            }

    grouped: dict[int, dict[str, list[dict[str, Any]]]] = {}
    for ican in sorted(catalog, key=ican_sort_key):
        info = catalog[ican]
        unit = int(info.get("unit") or ican_sort_key(ican)[0])
        mgid = str(info.get("mg_id") or f"U{unit}-MG{ican_sort_key(ican)[1]:02d}")
        grouped.setdefault(unit, {}).setdefault(mgid, []).append({
            "i_can_id": ican,
            "exact_text": str(info.get("exact_text") or ""),
            "evidence_student_count": evidence_counts.get(ican, 0),
            "bank_family_count": family_counts.get(ican, 0),
        })

    units_out: list[dict[str, Any]] = []
    for unit in sorted(grouped):
        mgs: list[dict[str, Any]] = []
        for mgid in sorted(grouped[unit], key=lambda x: (ican_sort_key(x + "-IC00")[1], x)):
            mg_info = banks["mg_catalog"].get(mgid) or {}
            mgs.append({
                "mg_id": mgid,
                "title": str(mg_info.get("title") or mg_info.get("exact_text") or ""),
                "i_cans": grouped[unit][mgid],
            })
        units_out.append({"unit": unit, "mastery_goals": mgs})

    return {
        "schema_version": 2,
        "portfolio_roots": scan["portfolio_roots"],
        "files_scanned": scan["files_scanned"],
        "student_count": len(scan["students"]),
        "evidence_record_count": len(scan["records"]),
        "bank_units": banks["units"],
        "units": units_out,
    }


def stable_choice(items: list[dict[str, Any]], seed: str) -> dict[str, Any] | None:
    if not items:
        return None
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(items)
    return items[idx]


def anonymize(student: str, salt: str) -> str:
    digest = hashlib.sha256((salt + "|" + student).encode("utf-8")).hexdigest()[:10]
    return f"S-{digest}"


def build_checkpoint_plan(
    github_root: Path,
    item_label: str,
    custom_name: str,
    target_questions: int = 6,
    unit: int = 1,
    eligible_i_cans: list[str] | None = None,
) -> dict[str, Any]:
    target_questions = max(1, min(int(target_questions), 6))
    eligible = sorted({x for x in (normalize_ican(v) for v in (eligible_i_cans or [])) if x}, key=ican_sort_key)
    if not eligible:
        raise ValueError("Select at least one eligible Mastery Goal or I Can before analyzing Portfolio evidence.")

    scan = scan_portfolio(github_root, None)
    banks = load_all_banks(github_root)
    families = banks["families"]
    by_ican: dict[str, list[dict[str, Any]]] = {}
    for f in families:
        by_ican.setdefault(f["i_can_id"], []).append(f)

    catalog = {k: dict(v) for k, v in banks["catalog"].items()}
    for ican in eligible:
        if ican not in catalog:
            m = ICAN_RE.search(ican)
            if m:
                catalog[ican] = {"i_can_id": ican, "exact_text": "", "mg_id": f"U{int(m.group(1))}-MG{m.group(2)}", "unit": int(m.group(1))}

    by_student: dict[str, list[dict[str, Any]]] = {s: [] for s in scan["students"]}
    for r in scan["records"]:
        by_student.setdefault(r["student"], []).append(r)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    base_label = re.sub(r"[^A-Za-z0-9]+", "_", item_label or "checkpoint").strip("_") or "checkpoint"
    plan_id = f"checkpoint_{base_label}_{stamp}"
    salt = hashlib.sha256((plan_id + str(time.time_ns())).encode("utf-8")).hexdigest()[:16]
    students: list[dict[str, Any]] = []
    extension_total = 0
    missing_family_total = 0
    reassessment_total = 0
    eligible_set = set(eligible)

    def mastered_for_checkpoint(record: dict[str, Any] | None) -> bool:
        if not record:
            return False
        # The Portfolio's five-box display is a mastery LEVEL, not a count of
        # observations. Four filled boxes means Mastered; five means Extended.
        # Never use observation_count as a substitute for the bar level.
        bars = parse_mastery_bars(record.get("mastery_bars"))
        if bars is None:
            bars = parse_mastery_bars(record.get("status"))
        if bars is not None:
            return bars >= 4
        low = normalize_text(record.get("status")).lower()
        return any(term in low for term in SECURE_TERMS)

    for student in sorted(by_student, key=lambda s: s.lower()):
        recs = by_student[student]
        current_by_ican = {r.get("i_can_id"): r for r in recs if r.get("i_can_id")}
        needs: list[dict[str, Any]] = []
        for ican in eligible:
            record = current_by_ican.get(ican)
            # Checkpoint rule: selected I Cans are rechecked unless the current
            # Portfolio picture shows Mastered (4+ bars/evidence). A selected
            # I Can with no current record is treated as Not Yet Assessed.
            if mastered_for_checkpoint(record):
                continue
            if record is None:
                record = {
                    "student": student,
                    "i_can_id": ican,
                    "status": "Not Yet Assessed",
                    "mastery_bars": 0,
                    "observation_count": 0,
                    "priority": 10000,
                    "source": "",
                    "source_mtime": 0.0,
                }
            needs.append(record)
        # If more than six selected I Cans need evidence, give the least-secure
        # current I Cans first; ties stay in stable I Can order.
        needs.sort(key=lambda r: (
            parse_mastery_bars(r.get("mastery_bars")) if parse_mastery_bars(r.get("mastery_bars")) is not None else 0,
            ican_sort_key(r.get("i_can_id", "")),
        ))
        chosen_needs = needs[:target_questions]
        reassessment_total += len(chosen_needs)
        assigned: list[dict[str, Any]] = []
        missing_family: list[dict[str, Any]] = []

        for slot, r in enumerate(chosen_needs, start=1):
            ican = r["i_can_id"]
            candidates = by_ican.get(ican, [])
            checkpoint_pref = [f for f in candidates if "Checkpoint" in f.get("product_eligibility", [])]
            pool = checkpoint_pref or candidates
            fam = stable_choice(pool, f"{student}|{plan_id}|{ican}|{slot}")
            info = catalog.get(ican) or {}
            record = {
                "slot": slot,
                "kind": "reassessment",
                "i_can_id": ican,
                "i_can_text": str(info.get("exact_text") or ""),
                "status": r.get("status", ""),
                "mastery_bars": r.get("mastery_bars"),
                "observation_count": r.get("observation_count"),
                "family": fam,
            }
            if fam:
                assigned.append(record)
            else:
                record["kind"] = "reassessment_family_needed"
                missing_family.append(record)

        extension_count = max(0, target_questions - len(chosen_needs))
        extension_total += extension_count
        missing_family_total += len(missing_family)
        student_key = anonymize(student, salt)
        other_current = sorted({r["i_can_id"] for r in recs if r["i_can_id"] not in {x["i_can_id"] for x in chosen_needs}}, key=ican_sort_key)
        students.append({
            "student_key": student_key,
            "student_display": student,
            "reassessment_need_count": len(chosen_needs),
            "reassessment_slots": assigned,
            "reassessment_family_requests": missing_family,
            "extension_count": extension_count,
            "other_current_i_cans": other_current,
        })

    eligible_mgs = sorted({re.sub(r"-IC\d{2}$", "", x) for x in eligible}, key=lambda x: ican_sort_key(x + "-IC00"))
    eligible_units = sorted({ican_sort_key(x)[0] for x in eligible})
    request_slots = extension_total + missing_family_total

    # Temporary families are authored as reusable FAMILY TEMPLATES, not one
    # family per student slot. A six-question checkpoint therefore needs at
    # most six shared extension families. Missing reassessment families are
    # also deduplicated by exact I Can and can serve every student needing that
    # same target.
    extension_family_count = min(6, max((int(s.get("extension_count", 0)) for s in students), default=0))
    extension_family_requests: list[dict[str, Any]] = []
    for index in range(1, extension_family_count + 1):
        extension_family_requests.append({
            "slot_kind": "extension",
            "extension_index": index,
            "assigned_student_keys": [s["student_key"] for s in students if int(s.get("extension_count", 0)) >= index],
        })

    missing_by_ican: dict[str, dict[str, Any]] = {}
    for student in students:
        for need in student.get("reassessment_family_requests", []):
            iid = str(need.get("i_can_id") or "")
            if not iid:
                continue
            entry = missing_by_ican.setdefault(iid, {
                "slot_kind": "reassessment_family_needed",
                "i_can_id": iid,
                "i_can_text": str(need.get("i_can_text") or (catalog.get(iid) or {}).get("exact_text") or ""),
                "assigned_student_keys": [],
            })
            if student["student_key"] not in entry["assigned_student_keys"]:
                entry["assigned_student_keys"].append(student["student_key"])
    missing_family_requests = [missing_by_ican[iid] for iid in sorted(missing_by_ican, key=ican_sort_key)]

    scope_catalog = []
    bank_family_examples: list[dict[str, Any]] = []
    for iid in eligible:
        info = catalog.get(iid) or {}
        current_families = sorted(by_ican.get(iid, []), key=lambda f: (str(f.get("family_label", "")), str(f.get("family_id", ""))))
        scope_catalog.append({
            "i_can_id": iid,
            "i_can_text": str(info.get("exact_text") or ""),
            "mastery_goal_id": str(info.get("mg_id") or re.sub(r"-IC\d{2}$", "", iid)),
            "unit": int(info.get("unit") or ican_sort_key(iid)[0]),
            "current_bank_family_count": len(current_families),
        })
        for family in current_families[:2]:
            ref = dict(family.get("authoring_reference") or {})
            if ref:
                bank_family_examples.append({
                    "i_can_id": iid,
                    "teacher_question_id": family.get("teacher_question_id", ""),
                    "approval_status": family.get("approval_status", ""),
                    **ref,
                })

    requested_family_count = extension_family_count + len(missing_family_requests)

    plan = {
        "schema_version": 3,
        "plan_id": plan_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "course": "Algebra 1",
        "storage_unit": unit,
        "item_label": item_label,
        "custom_name": custom_name,
        "target_questions_per_student": target_questions,
        "eligible_i_cans": eligible,
        "eligible_mastery_goals": eligible_mgs,
        "eligible_units": eligible_units,
        "portfolio_roots": scan["portfolio_roots"],
        "files_scanned": scan["files_scanned"],
        "evidence_record_count": len(scan["records"]),
        "student_count": len(students),
        "reassessment_slot_count": reassessment_total,
        "missing_reassessment_family_slot_count": missing_family_total,
        "extension_slot_count": extension_total,
        "temporary_family_request_slot_count": request_slots,
        "extension_family_request_count": extension_family_count,
        "missing_reassessment_family_request_count": len(missing_family_requests),
        "temporary_family_request_count": requested_family_count,
        "extension_family_requests": extension_family_requests,
        "missing_reassessment_family_requests": missing_family_requests,
        "scope_catalog": scope_catalog,
        "bank_family_examples": bank_family_examples,
        "students": students,
    }
    return plan


def request_payload(plan: dict[str, Any]) -> dict[str, Any]:
    students = []
    for s in plan.get("students", []):
        students.append({
            "student_key": s["student_key"],
            "assigned_reassessment_i_cans": [x["i_can_id"] for x in s.get("reassessment_slots", [])],
            "missing_reassessment_family_i_cans": [x["i_can_id"] for x in s.get("reassessment_family_requests", [])],
            "extension_count": s.get("extension_count", 0),
        })
    return {
        "schema_version": 3,
        "request_type": "algebra_checkpoint_temporary_families",
        "plan_id": plan.get("plan_id"),
        "course": plan.get("course"),
        "item_label": plan.get("item_label"),
        "custom_name": plan.get("custom_name"),
        "target_questions_per_student": plan.get("target_questions_per_student"),
        "eligible_i_cans": plan.get("eligible_i_cans", []),
        "eligible_mastery_goals": plan.get("eligible_mastery_goals", []),
        "scope_catalog": plan.get("scope_catalog", []),
        "bank_family_examples": plan.get("bank_family_examples", []),
        "open_student_slot_count": plan.get("temporary_family_request_slot_count", 0),
        "requested_family_count": plan.get("temporary_family_request_count", 0),
        "requested_extension_family_count": plan.get("extension_family_request_count", 0),
        "extension_family_requests": plan.get("extension_family_requests", []),
        "reassessment_family_requests": plan.get("missing_reassessment_family_requests", []),
        "students": students,
        "instructions": [
            "The teacher explicitly selected the eligible I Can scope. Do not author reassessment targets outside that scope.",
            "Author reusable temporary FAMILIES, not one family per student slot.",
            "Create exactly requested_extension_family_count shared extension families (0-6 total). Extension family 1 serves every student listed for extension_index 1, and so on.",
            "For each reassessment_family_request, create one temporary family targeted to that exact I Can; the same family may serve every assigned student_key listed for that request.",
            "Extension families should extend/transfer the selected learning, not merely repeat a direct bank question with cosmetic number changes.",
            "Use the supplied bank_family_examples as the style/structure reference. Preserve the bank's evidence-first family architecture and concise student-facing wording.",
            "Temporary families remain local to this checkpoint and must not be added to the permanent Algebra bank unless the teacher later promotes them deliberately.",
            "Return one AI Result ZIP containing one complete extension_families.json at the ZIP root. Do not return a Curriculum Transfer or GitHub Transfer. The teacher imports this ZIP with Load Returned Families in Algebra 1 Tools.",
            "The teacher will review every returned family in the Builder and mark Accept or Replace before checkpoint assembly.",
        ],
        "expected_response": {
            "schema_version": 3,
            "plan_id": plan.get("plan_id"),
            "extension_families": [
                {
                    "extension_family_id": "TMP-...",
                    "slot_kind": "extension or reassessment_family_needed",
                    "extension_index": "1-6 for extension; omit for reassessment",
                    "assigned_student_keys": ["S-..."],
                    "target_i_can_ids": ["U1-MG01-IC01"],
                    "family_name": "...",
                    "family_purpose": "...",
                    "evidence_job": "...",
                    "student_action": "...",
                    "question_structure_id": "...",
                    "response_mode": "...",
                    "representation_mode": "...",
                    "difficulty_intent": "...",
                    "invariant": "...",
                    "variation_axes": ["..."],
                    "forbidden_variations": ["..."],
                    "fresh_instance_rule": "...",
                    "exemplar": {
                        "student_html": "...",
                        "answer": "...",
                        "solution": "...",
                        "scoring_guidance": "..."
                    },
                }
            ],
        },
    }


def write_checkpoint_state(github_root: Path, plan: dict[str, Any]) -> Path:
    root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan["plan_id"]
    root.mkdir(parents=True, exist_ok=True)
    out = root / "plan.json"
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return out


def request_path(github_root: Path, plan_id: str) -> Path:
    """Return the deterministic path for a Checkpoint AI-family request ZIP."""
    root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_requests"
    return root / f"{plan_id}_AI_FAMILY_REQUEST.zip"


def create_extension_request_zip(github_root: Path, plan: dict[str, Any]) -> Path | None:
    if int(plan.get("temporary_family_request_count", plan.get("temporary_family_request_slot_count", 0))) <= 0:
        return None
    req_root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_requests"
    req_root.mkdir(parents=True, exist_ok=True)
    path = req_root / f"{plan['plan_id']}_AI_FAMILY_REQUEST.zip"
    payload = request_payload(plan)
    readme = (
        "Algebra Assessment Builder - Checkpoint AI Family Request\n"
        "===============================================================\n\n"
        "Upload this ZIP to the Curriculum Build chat.\n"
        "The request is anonymized: student names remain only in the local plan on this Mac.\n"
        "The teacher-selected eligible I Can scope is locked into this request.\n"
        "Return one AI Result ZIP containing extension_families.json at the ZIP root. Do not return a Curriculum Transfer or GitHub Transfer.\n"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("CHECKPOINT_EXTENSION_REQUEST.json", json.dumps(payload, indent=2) + "\n")
        zf.writestr("README.txt", readme)
    return path


def extension_response_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_extensions" / plan_id / "extension_families.json"


def family_review_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "family_review.json"


def replacement_request_path(github_root: Path, plan_id: str) -> Path:
    root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_requests"
    return root / f"{plan_id}_FAMILY_REPLACEMENT_REQUEST.zip"


def _temporary_family_id(family: dict[str, Any]) -> str:
    return normalize_text(family.get("extension_family_id") or family.get("family_id"))


def validate_extension_response(plan: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(response, dict):
        return {"complete": False, "errors": ["Returned family response is not a JSON object."], "warnings": [], "families": []}
    if normalize_text(response.get("plan_id")) != normalize_text(plan.get("plan_id")):
        errors.append("Returned family response plan_id does not match this Checkpoint plan.")
    families = response.get("extension_families")
    if not isinstance(families, list):
        errors.append("Returned family response must contain extension_families as a list.")
        families = []

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(families, 1):
        if not isinstance(raw, dict):
            errors.append(f"Family #{index} is not a JSON object.")
            continue
        family = dict(raw)
        fid = _temporary_family_id(family)
        if not fid:
            errors.append(f"Family #{index} is missing extension_family_id.")
            continue
        if fid in seen:
            errors.append(f"Duplicate temporary family id: {fid}")
            continue
        seen.add(fid)
        family["extension_family_id"] = fid
        kind = normalize_text(family.get("slot_kind"))
        if kind not in {"extension", "reassessment_family_needed"}:
            errors.append(f"{fid} has invalid slot_kind: {kind or '(blank)'}")
        targets = []
        for value in family.get("target_i_can_ids") or []:
            iid = normalize_ican(value)
            if iid and iid not in targets:
                targets.append(iid)
        family["target_i_can_ids"] = targets
        family["assigned_student_keys"] = [normalize_text(x) for x in (family.get("assigned_student_keys") or []) if normalize_text(x)]
        family["family_name"] = normalize_text(family.get("family_name"))
        family["student_action"] = normalize_text(family.get("student_action"))
        exemplar = family.get("exemplar") if isinstance(family.get("exemplar"), dict) else {}
        family["exemplar"] = exemplar
        if not family["family_name"]:
            errors.append(f"{fid} is missing family_name.")
        if not family["student_action"]:
            warnings.append(f"{fid} is missing student_action.")
        if not normalize_text(exemplar.get("student_html")):
            errors.append(f"{fid} is missing exemplar.student_html.")
        normalized.append(family)

    requested_ext = int(plan.get("extension_family_request_count", 0))
    ext_families = [f for f in normalized if normalize_text(f.get("slot_kind")) == "extension"]
    if len(ext_families) != requested_ext:
        errors.append(f"Expected {requested_ext} extension families but received {len(ext_families)}.")
    if requested_ext:
        ext_indexes = []
        for family in ext_families:
            try:
                ext_indexes.append(int(family.get("extension_index")))
            except (TypeError, ValueError):
                errors.append(f"{family['extension_family_id']} is missing a valid extension_index.")
        if sorted(ext_indexes) != list(range(1, requested_ext + 1)):
            errors.append("Extension family indexes must be exactly 1 through the requested extension family count.")

    requested_reassess = {str(x.get("i_can_id") or "") for x in plan.get("missing_reassessment_family_requests", []) if x.get("i_can_id")}
    returned_reassess: set[str] = set()
    for family in normalized:
        if normalize_text(family.get("slot_kind")) != "reassessment_family_needed":
            continue
        if len(family.get("target_i_can_ids") or []) != 1:
            errors.append(f"{family['extension_family_id']} must target exactly one reassessment I Can.")
        else:
            returned_reassess.add(family["target_i_can_ids"][0])
    missing = sorted(requested_reassess - returned_reassess, key=ican_sort_key)
    extra = sorted(returned_reassess - requested_reassess, key=ican_sort_key)
    if missing:
        errors.append("Missing temporary reassessment family for: " + ", ".join(missing))
    if extra:
        warnings.append("Returned reassessment family was not requested for: " + ", ".join(extra))

    return {
        "complete": not errors,
        "errors": errors,
        "warnings": warnings,
        "families": normalized,
        "requested_family_count": int(plan.get("temporary_family_request_count", 0)),
        "returned_family_count": len(normalized),
    }


def load_family_review(github_root: Path, plan_id: str) -> dict[str, Any]:
    path = family_review_path(github_root, plan_id)
    if not path.is_file():
        return {"schema_version": 1, "plan_id": plan_id, "decisions": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "plan_id": plan_id, "decisions": {}}
    if not isinstance(data, dict):
        data = {}
    decisions = data.get("decisions") if isinstance(data.get("decisions"), dict) else {}
    return {"schema_version": 1, "plan_id": plan_id, "updated_at": data.get("updated_at", ""), "decisions": decisions}


def create_replacement_request_zip(github_root: Path, plan: dict[str, Any], response: dict[str, Any], review: dict[str, Any]) -> Path | None:
    decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
    replace_ids = sorted(fid for fid, decision in decisions.items() if decision == "REPLACE")
    path = replacement_request_path(github_root, str(plan.get("plan_id", "")))
    if not replace_ids:
        if path.is_file():
            path.unlink()
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    accepted_ids = sorted(fid for fid, decision in decisions.items() if decision == "ACCEPT")
    payload = {
        "schema_version": 1,
        "request_type": "algebra_checkpoint_temporary_family_replacements",
        "plan_id": plan.get("plan_id"),
        "replace_family_ids": replace_ids,
        "accepted_family_ids": accepted_ids,
        "original_authoring_request": request_payload(plan),
        "current_response": response,
        "instructions": [
            "Replace only the families listed in replace_family_ids.",
            "Preserve every accepted family exactly as supplied in current_response.",
            "Return one COMPLETE extension_families.json for this plan, containing the preserved accepted families plus the replacements.",
            "Keep the same extension_family_id, slot_kind, extension_index, target_i_can_ids, and assigned_student_keys for each replaced family unless the request itself requires a correction.",
            "Return one AI Result ZIP containing the complete replacement extension_families.json at the ZIP root. The teacher imports it with Load Returned Families; do not return a Curriculum Transfer.",
        ],
    }
    readme = (
        "Algebra Assessment Builder - Temporary Family Replacement Request\n"
        "=============================================================\n\n"
        "Upload this ZIP to the Curriculum Build chat.\n"
        "Only families marked Replace should be rewritten. Accepted families must remain unchanged.\n"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("CHECKPOINT_FAMILY_REPLACEMENT_REQUEST.json", json.dumps(payload, indent=2) + "\n")
        zf.writestr("README.txt", readme)
    return path



def checkpoint_output_dir(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_output" / plan_id


def checkpoint_output_zip_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_output" / f"{plan_id}_CHECKPOINT.zip"


def assembly_manifest_path(github_root: Path, plan_id: str) -> Path:
    return checkpoint_output_dir(github_root, plan_id) / "assembly_manifest.json"


def _sha256_path(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checkpoint_approval_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "approval.json"


def revoke_checkpoint_approval(github_root: Path, plan_id: str) -> None:
    checkpoint_approval_path(github_root, plan_id).unlink(missing_ok=True)


def load_checkpoint_approval(github_root: Path, plan_id: str) -> dict[str, Any] | None:
    path = checkpoint_approval_path(github_root, plan_id)
    if not path.is_file():
        return None
    try:
        approval = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    assembly = load_checkpoint_assembly(github_root, plan_id)
    if not assembly:
        return None
    if approval.get("assembly_manifest_sha256") != _sha256_path(assembly_manifest_path(github_root, plan_id)):
        return None
    if approval.get("output_zip_sha256") != _sha256_path(checkpoint_output_zip_path(github_root, plan_id)):
        return None
    return approval


def approve_checkpoint(github_root: Path, plan_id: str, fit_confirmed: bool, layout_state: Any = None) -> dict[str, Any]:
    if not fit_confirmed:
        raise ValueError("Approval is blocked until every student fits the fixed two-page form.")
    assembly = load_checkpoint_assembly(github_root, plan_id)
    if not assembly:
        raise ValueError("Assemble the Checkpoint before approving it.")
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not state_path.is_file():
        raise ValueError("Checkpoint plan was not found.")
    plan = json.loads(state_path.read_text(encoding="utf-8"))
    approval = {
        "schema_version": 1,
        "plan_id": plan_id,
        "approved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "approved_epoch": time.time(),
        "title": normalize_text(plan.get("custom_name")) or f"Checkpoint {normalize_text(plan.get('item_label')) or ''}".strip(),
        "student_count": int(assembly.get("student_count", 0) or 0),
        "pages_per_student": int(assembly.get("pages_per_student", 2) or 2),
        "assembly_manifest_sha256": _sha256_path(assembly_manifest_path(github_root, plan_id)),
        "output_zip_sha256": _sha256_path(checkpoint_output_zip_path(github_root, plan_id)),
        "layout_state": layout_state if isinstance(layout_state, dict) else {},
    }
    path = checkpoint_approval_path(github_root, plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(approval, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return approval


def _safe_file_token(value: str, fallback: str = "student") -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", normalize_text(value)).strip("_")
    return token or fallback


def _family_exemplar(family: dict[str, Any]) -> dict[str, Any]:
    ex = family.get("exemplar")
    return dict(ex) if isinstance(ex, dict) else {}


def _embed_bank_assets(github_root: Path, markup: str, unit: int) -> str:
    if not markup or "src=" not in markup:
        return markup
    bank_root = github_root / "algebra" / "banks" / f"unit{unit}"
    pattern = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.I)

    def repl(match: re.Match[str]) -> str:
        src = match.group(2).strip()
        if not src or src.startswith(("data:", "http://", "https://")):
            return match.group(0)
        rel = src.lstrip("./")
        asset = bank_root / rel
        try:
            asset.resolve().relative_to(bank_root.resolve())
        except ValueError:
            return match.group(0)
        if not asset.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
        data = base64.b64encode(asset.read_bytes()).decode("ascii")
        return f"{match.group(1)}data:{mime};base64,{data}{match.group(3)}"

    return pattern.sub(repl, markup)


def _checkpoint_css() -> str:
    return """
@page{size:letter;margin:0}
*{box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;color:#182230;margin:0;background:#eef1f5}
.checkpoint-stage{padding:16px}
.checkpoint-form{width:8.5in;height:11in;min-height:11in;margin:16px auto;background:#fff;padding:.38in .48in;box-shadow:0 1px 4px rgba(0,0,0,.16);break-after:page;page-break-after:always;overflow:hidden;display:flex;flex-direction:column}.checkpoint-form>.plc-page-body{flex:1 1 auto;min-height:0;overflow:hidden}
.form-head{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:end;border-bottom:2px solid #182230;padding-bottom:9px;margin-bottom:12px}
.form-head h1{font-size:1.18rem;margin:0 0 4px}.form-head .course{font-size:.78rem;font-weight:800;color:#566474;text-transform:uppercase;letter-spacing:.03em}.student-line{font-size:.85rem;font-weight:800}.date-line{font-size:.75rem;color:#566474;margin-top:4px}
.question{break-inside:avoid;border-bottom:1px solid #dfe4ea;padding:9px 0 13px;margin-bottom:3px}.question:last-child{border-bottom:0}.question-label{font-size:.74rem;font-weight:900;color:#173f73;text-transform:uppercase;letter-spacing:.04em;margin-bottom:7px}.question-label.extension{display:inline-block;padding:4px 7px;border-radius:999px;background:#fff3c4;color:#6f5612;border:1px solid #e2c96d}.question-body{font-size:.94rem;line-height:1.38}.question-body p{margin:.42em 0}.question-body img,.question-body svg,.question-body canvas{display:block!important;width:min(100%,var(--plc-figure-width,320px))!important;max-width:100%!important;max-height:none!important;height:auto!important;margin:8px auto!important}.packet-workspace{height:var(--plc-workspace-height,0px)!important;min-height:0!important;background:#fff}.question-body table{border-collapse:collapse;margin:8px 0}.question-body th,.question-body td{border:1px solid #556170;padding:5px 9px;text-align:center}.response-surface{min-height:.38in;margin-top:7px}.choices{list-style-type:upper-alpha;margin-top:6px;margin-bottom:6px}
.key-form{width:8.5in;min-height:11in;margin:16px auto;background:#fff;padding:.42in .52in;box-shadow:0 1px 4px rgba(0,0,0,.16);break-after:page;page-break-after:always}.key-form:last-child{break-after:auto;page-break-after:auto}.key-question{break-inside:avoid;border-bottom:1px solid #dfe4ea;padding:10px 0 13px}.key-meta{font-size:.68rem;color:#667085;margin:4px 0 8px}.key-answer{font-size:.86rem;line-height:1.4}.key-answer p{margin:5px 0}
.checkpoint-controls{position:fixed;left:0;top:0;bottom:0;width:310px;background:#fff;border-right:1px solid #cfd7e3;padding:18px 16px;overflow:auto;z-index:20;box-shadow:2px 0 8px rgba(0,0,0,.08)}
.checkpoint-controls h1{font-size:1.05rem;margin:0 0 5px}.checkpoint-controls h2{font-size:.82rem;margin:0 0 8px;color:#173f73}.checkpoint-controls .control-note{font-size:.76rem;line-height:1.35;color:#5d6a7d;margin:0 0 14px}.checkpoint-controls label{display:block;font-size:.72rem;font-weight:800;color:#4e5d70;margin:12px 0 5px}.checkpoint-controls select,.checkpoint-controls button{width:100%;font:inherit;border:1px solid #b9c5d6;border-radius:8px;background:#fff;padding:8px 9px}.checkpoint-controls button{font-weight:800;color:#163f73;cursor:pointer}.checkpoint-controls button.primary-control{background:#173f73;color:#fff;border-color:#173f73;margin-top:10px}.checkpoint-control-slots{margin-top:12px}.checkpoint-control-slot{border-top:1px solid #e1e6ed;padding:11px 0}.checkpoint-control-slot:first-child{border-top:0}.checkpoint-control-slot strong{display:block;font-size:.75rem;margin-bottom:5px}.checkpoint-control-slot small{display:block;color:#6b7788;font-size:.66rem;margin:4px 0}.checkpoint-control-slot .regen{margin-top:5px;padding:6px 8px;font-size:.72rem}.checkpoint-mini-layout{border:1px solid #e1e6ed;border-radius:8px;background:#f8fafc;padding:7px 8px;margin:7px 0}.checkpoint-mini-layout .mini-row{margin:5px 0}.checkpoint-mini-layout .mini-head{display:flex;justify-content:space-between;gap:6px;font-size:.64rem;font-weight:800;color:#59677a}.checkpoint-mini-layout input[type=range]{width:100%;margin:3px 0 0}.checkpoint-mini-layout button{padding:5px 7px;font-size:.64rem;margin-top:5px}.checkpoint-control-status{font-size:.7rem;line-height:1.35;margin-top:10px;min-height:1.2em;color:#5d6a7d}.checkpoint-control-status.error{color:#9d2a20}.checkpoint-control-section{border-top:1px solid #e1e6ed;margin-top:14px;padding-top:13px}.checkpoint-layout-row{margin:9px 0}.checkpoint-layout-row .layout-head{display:flex;justify-content:space-between;gap:8px;align-items:center;font-size:.7rem;font-weight:800;color:#4e5d70}.checkpoint-layout-row input[type=range]{width:100%;margin-top:5px}.checkpoint-layout-status{font-size:.66rem;line-height:1.3;color:#6b7788;min-height:1.1em}.checkpoint-static-select{border:1px solid #c6d0dd;border-radius:8px;padding:8px 9px;background:#f6f8fb;color:#526174;font-size:.78rem}.checkpoint-finish-card{border:1px solid #d6deea;border-radius:9px;padding:9px;margin-top:8px;background:#f8fafc}.checkpoint-finish-card span{display:block;text-transform:uppercase;letter-spacing:.04em;font-size:.61rem;font-weight:900;color:#6b7788}.checkpoint-finish-card strong{display:block;font-size:.73rem;line-height:1.35;color:#173f73;margin-top:3px}.checkpoint-controls a.control-link{display:block;text-align:center;text-decoration:none;width:100%;font:inherit;border:1px solid #b9c5d6;border-radius:8px;background:#fff;padding:8px 9px;font-weight:800;color:#163f73;margin-top:7px}.checkpoint-form.overfull{outline:3px solid #d69b27;outline-offset:-3px}.checkpoint-student-fit,.checkpoint-finish-readiness,.checkpoint-approval-status{font-size:.67rem;line-height:1.35;border-radius:7px;padding:7px 8px;margin-top:7px;background:#eef6ee;color:#2c6941}.checkpoint-controls button:disabled{opacity:.48;cursor:not-allowed}.checkpoint-student-fit.bad,.checkpoint-finish-readiness.bad{background:#fff4df;color:#815d10;border:1px solid #edcf86}.checkpoint-finish-readiness.good{border:1px solid #bad8c4}.checkpoint-form.screen-hidden.measure-layout{display:block!important;position:absolute!important;visibility:hidden!important;left:-10000px!important;top:0!important;pointer-events:none!important}.packet-with-controls .checkpoint-stage{margin-left:310px}.screen-hidden{display:none!important}
@media print{body{background:#fff}.checkpoint-controls{display:none!important}.packet-with-controls .checkpoint-stage,.checkpoint-stage{margin:0;padding:0}.checkpoint-form,.key-form{display:block!important;margin:0;box-shadow:none}.screen-hidden{display:block!important}}
"""


def _mathjax_head() -> str:
    # The JavaScript source must contain escaped backslashes so MathJax receives
    # the literal TeX delimiters \( ... \) and \[ ... \].
    return r'<script>window.MathJax={tex:{inlineMath:[["\\(","\\)"],["$","$"]],displayMath:[["\\[","\\]"]],processEscapes:true},startup:{typeset:true}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'


def _question_html(q: dict[str, Any], slot_index: int) -> str:
    label_class = "question-label extension" if q.get("kind") == "extension" else "question-label"
    return (
        f'<section class="question plc-question" data-slot-index="{int(slot_index)}" data-family-id="{html.escape(normalize_text(q.get("family_id")), quote=True)}">'
        f'<div class="{label_class}">{html.escape(str(q.get("label") or "Question"))}</div>'
        f'<div class="question-body plc-question-content">{q.get("student_html") or ""}</div><div class="plc-figure"></div><div class="packet-workspace plc-workspace" aria-hidden="true"></div></section>'
    )


def _student_pages_html(title: str, student: str, student_key: str, questions: list[dict[str, Any]]) -> str:
    # Every student receives exactly two physical pages so the complete class
    # packet can be printed duplex without student forms bleeding together.
    indexed = list(enumerate(questions, start=1))
    split = (len(indexed) + 1) // 2
    groups = [indexed[:split], indexed[split:]]
    pages: list[str] = []
    for page_no, group in enumerate(groups, start=1):
        continued = " · continued" if page_no == 2 else ""
        parts = "".join(_question_html(q, slot_index) for slot_index, q in group)
        if not parts:
            parts = '<div style="height:8.2in"></div>'
        pages.append(
            f'<article class="checkpoint-form" data-student-key="{html.escape(student_key, quote=True)}" data-student-name="{html.escape(student, quote=True)}" data-page="{page_no}">'
            f'<header class="form-head"><div><div class="course">Algebra 1 · Checkpoint{continued}</div><h1>{html.escape(title)}</h1></div>'
            f'<div><div class="student-line">{html.escape(student)}</div><div class="date-line">Date: __________</div></div></header><main class="plc-page-body">{parts}</main></article>'
        )
    return "".join(pages)


def _student_document(title: str, student: str, student_key: str, questions: list[dict[str, Any]]) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{html.escape(title)} - {html.escape(student)}</title><style>{_checkpoint_css()}</style>{_mathjax_head()}</head><body>'
        f'<main class="checkpoint-stage">{_student_pages_html(title, student, student_key, questions)}</main></body></html>'
    )


def _teacher_key_document(title: str, student_forms: list[dict[str, Any]]) -> str:
    forms = []
    for form in student_forms:
        parts = []
        for q in form.get("questions", []):
            meta = " · ".join(x for x in [normalize_text(q.get("i_can_id")), normalize_text(q.get("family_name"))] if x)
            ex = q.get("exemplar") if isinstance(q.get("exemplar"), dict) else {}
            answer = html.escape(normalize_text(ex.get("answer"))) or "—"
            solution = html.escape(normalize_text(ex.get("solution")))
            scoring = html.escape(normalize_text(ex.get("scoring_guidance")))
            details = [f'<p><strong>Answer:</strong> {answer}</p>']
            if solution:
                details.append(f'<p><strong>Solution:</strong> {solution}</p>')
            if scoring:
                details.append(f'<p><strong>Scoring:</strong> {scoring}</p>')
            label_class = "question-label extension" if q.get("kind") == "extension" else "question-label"
            parts.append(
                f'<section class="key-question"><div class="{label_class}">{html.escape(str(q.get("label") or "Question"))}</div>'
                f'<div class="key-meta">{html.escape(meta)}</div><div class="key-answer">{"".join(details)}</div></section>'
            )
        forms.append(
            f'<article class="key-form"><header class="form-head"><div><div class="course">Teacher Key · Algebra 1 Checkpoint</div><h1>{html.escape(title)}</h1></div>'
            f'<div class="student-line">{html.escape(str(form.get("student_display") or ""))}</div></header>{"".join(parts)}</article>'
        )
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + f'<title>{html.escape(title)} - Teacher Key</title><style>{_checkpoint_css()}</style>{_mathjax_head()}</head><body><main class="checkpoint-stage">' + "".join(forms) + '</main></body></html>'


def _assembly_data_path(github_root: Path, plan_id: str) -> Path:
    return checkpoint_output_dir(github_root, plan_id) / "assembly_data.json"


def _load_temp_families_for_assembly(github_root: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    request_count = int(plan.get("temporary_family_request_count", plan.get("temporary_family_request_slot_count", 0)) or 0)
    if not request_count:
        return []
    ext_path = extension_response_path(github_root, str(plan.get("plan_id") or ""))
    if not ext_path.is_file():
        raise ValueError("Returned temporary families have not been installed yet.")
    response = json.loads(ext_path.read_text(encoding="utf-8"))
    validation = validate_extension_response(plan, response)
    if not validation.get("complete"):
        raise ValueError("Returned temporary families must pass validation before assembly.")
    review = load_family_review(github_root, str(plan.get("plan_id") or ""))
    decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
    temp_families = [dict(f) for f in validation.get("families", [])]
    unaccepted = [_temporary_family_id(f) for f in temp_families if decisions.get(_temporary_family_id(f)) != "ACCEPT"]
    if unaccepted:
        raise ValueError("Accept every returned temporary family before assembly.")
    return temp_families


def _family_option(family: dict[str, Any], kind: str) -> dict[str, Any]:
    fid = normalize_text(family.get("family_id") or family.get("extension_family_id"))
    targets = family.get("target_i_can_ids") or ([family.get("i_can_id")] if family.get("i_can_id") else [])
    return {
        "family_id": fid,
        "family_name": normalize_text(family.get("family_name")) or fid,
        "kind": kind,
        "target_i_can_ids": [normalize_text(x) for x in targets if normalize_text(x)],
        "exemplar": _family_exemplar(family),
    }


def _control_data(github_root: Path, plan: dict[str, Any], student_forms: list[dict[str, Any]], temp_families: list[dict[str, Any]]) -> dict[str, Any]:
    banks = load_all_banks(github_root)
    by_ican: dict[str, list[dict[str, Any]]] = {}
    for family in banks.get("families", []):
        by_ican.setdefault(normalize_text(family.get("i_can_id")), []).append(family)
    for iid in by_ican:
        by_ican[iid].sort(key=lambda f: (normalize_text(f.get("family_label")), normalize_text(f.get("family_id"))))
    extension_options = [_family_option(f, "extension") for f in temp_families if normalize_text(f.get("slot_kind")) == "extension"]
    out_students = []
    for form in student_forms:
        slots = []
        for idx, q in enumerate(form.get("questions", []), start=1):
            if q.get("kind") == "extension":
                options = extension_options
            else:
                options = [_family_option(f, "reassessment") for f in by_ican.get(normalize_text(q.get("i_can_id")), [])]
            slots.append({
                "slot_index": idx,
                "kind": q.get("kind"),
                "label": q.get("label"),
                "i_can_id": q.get("i_can_id"),
                "selected_family_id": q.get("family_id"),
                "selected_family_name": q.get("family_name"),
                "has_figure": bool(re.search(r"<(?:img|svg)\b", normalize_text(q.get("student_html")), re.I)),
                "options": options,
            })
        out_students.append({
            "student_key": form.get("student_key"),
            "student_display": form.get("student_display"),
            "slots": slots,
        })
    approval = load_checkpoint_approval(github_root, normalize_text(plan.get("plan_id")))
    return {"plan_id": plan.get("plan_id"), "students": out_students, "approved": bool(approval), "approval": approval}


def _embedded_generator_scripts() -> str:
    app_dir = Path(__file__).resolve().parent
    chunks = []
    for name in ("assessment_builder_generation.js", "assessment_builder_generation_34.js"):
        path = app_dir / name
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _class_controls_script(control_data: dict[str, Any]) -> str:
    data = json.dumps(control_data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<script>window.CHECKPOINT_CONTROL_DATA={data};</script>
<script>
(function(){{
  const data=window.CHECKPOINT_CONTROL_DATA||{{students:[]}};
  const studentSelect=document.getElementById('checkpointStudentSelect');
  const slotsHost=document.getElementById('checkpointControlSlots');
  const status=document.getElementById('checkpointControlStatus');
  const studentFit=document.getElementById('checkpointStudentFit');
  const finishReadiness=document.getElementById('checkpointFinishReadiness');
  const approveBtn=document.getElementById('checkpointApproveBtn');
  const approvalStatus=document.getElementById('checkpointApprovalStatus');
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
  const byKey=new Map((data.students||[]).map(s=>[s.student_key,s]));
  let overflowByStudent=new Map();
  function setStatus(msg,err=false){{status.textContent=msg||'';status.className='checkpoint-control-status'+(err?' error':'')}}
  function studentName(key){{return byKey.get(key)?.student_display||key||'Student'}}
  function supports(fid){{return Boolean(window.AssessmentGeneration?.supports?.(fid))}}
  function makeInstance(option){{if(!option)return null;if(option.kind==='reassessment'&&supports(option.family_id)){{for(let i=0;i<8;i++){{const inst=window.AssessmentGeneration.generate({{family_id:option.family_id}});if(inst&&inst.student_html)return inst}}}}return option.exemplar||null}}
  async function updateSlot(studentKey,slotIndex,familyId){{const student=byKey.get(studentKey),slot=student?.slots?.find(x=>Number(x.slot_index)===Number(slotIndex)),option=slot?.options?.find(x=>x.family_id===familyId);if(!option)return;const instance=makeInstance(option);if(!instance?.student_html){{setStatus('This family could not create a usable question instance.',true);return}}setStatus('Updating '+student.student_display+'…');try{{const r=await fetch('/api/checkpoint/manual-adjust',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_id:data.plan_id,student_key:studentKey,slot_index:Number(slotIndex),family_id:familyId,instance}})}}),resp=await r.json().catch(()=>({{}}));if(!r.ok||!resp.ok)throw new Error(resp.error||('Update failed ('+r.status+')'));location.reload()}}catch(e){{setStatus(e.message||String(e),true)}}}}
  async function revokeApproval(message='Changes made — approve again when the Checkpoint is ready.'){{if(!data.approved)return;data.approved=false;if(approvalStatus){{approvalStatus.textContent=message;approvalStatus.className='checkpoint-approval-status'}}if(approveBtn){{approveBtn.disabled=false;approveBtn.textContent='Approve Checkpoint'}}try{{await fetch('/api/checkpoint/unapprove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_id:data.plan_id}})}})}}catch(_e){{}}}}
  const approvedLayout=data.approved&&data.approval&&data.approval.layout_state&&typeof data.approval.layout_state==='object'?data.approval.layout_state:{{}};
  let plc;
  function updateStudentOptions(over){{[...studentSelect.options].forEach(opt=>{{if(!opt.value){{opt.textContent='All students';return}}opt.textContent=(over.has(opt.value)?'⚠ ':'')+studentName(opt.value)}})}}
  function checkOverflow(){{if(!plc)return new Map();const over=plc.measureOverflow(3);overflowByStudent=over;updateStudentOptions(over);const selected=studentSelect.value;if(selected){{const pagesOver=over.get(selected)||[],name=studentName(selected),msg=pagesOver.length?`${{name}} would exceed 2 pages — page${{pagesOver.length===1?'':'s'}} ${{pagesOver.join(', ')}} ${{pagesOver.length===1?'is':'are'}} overfull.`:`${{name}} fits in 2 pages.`;if(studentFit){{studentFit.textContent=msg;studentFit.className='checkpoint-student-fit'+(pagesOver.length?' bad':'')}}}}else{{const names=[...over.keys()].filter(Boolean).map(studentName),msg=names.length?`${{names.length}} student${{names.length===1?'':'s'}} would exceed 2 pages: ${{names.slice(0,8).join(', ')}}${{names.length>8?` (+${{names.length-8}} more)`:''}}.`:'All students fit in 2 pages.';if(studentFit){{studentFit.textContent=msg;studentFit.className='checkpoint-student-fit'+(names.length?' bad':'')}}}}if(finishReadiness){{const count=over.size;finishReadiness.textContent=count?`Layout needs attention — ${{count}} student${{count===1?'':'s'}} exceed the fixed two-page form.`:`Ready to finish — all ${{(data.students||[]).length}} students fit the two-page form.`;finishReadiness.className='checkpoint-finish-readiness '+(count?'bad':'good')}}if(approveBtn){{approveBtn.disabled=over.size>0||Boolean(data.approved);approveBtn.textContent=data.approved?'Approved Checkpoint':'Approve Checkpoint'}}return over}}
  function renderSlots(key){{if(!key){{slotsHost.innerHTML='<p class="control-note">Choose a student to adjust individual questions. Printing always includes every student.</p>';return}}const s=byKey.get(key);if(!s){{slotsHost.innerHTML='';return}}slotsHost.innerHTML=(s.slots||[]).map(slot=>{{const opts=(slot.options||[]).map(o=>`<option value="${{esc(o.family_id)}}" ${{o.family_id===slot.selected_family_id?'selected':''}}>${{esc(o.family_name||o.family_id)}}</option>`).join(''),regen=slot.kind==='reassessment'&&supports(slot.selected_family_id);return `<div class="checkpoint-control-slot"><strong>${{esc(slot.label)}}${{slot.i_can_id?' · '+esc(slot.i_can_id):''}}</strong><select data-slot="${{slot.slot_index}}">${{opts}}</select><small>${{slot.kind==='extension'?'Extension':'Reassessment'}} family</small><div class="checkpoint-mini-layout" data-q-layout-slot="${{slot.slot_index}}"></div><button class="regen" data-regen="${{slot.slot_index}}" ${{regen?'':'disabled'}}>New instance</button></div>`}}).join('');slotsHost.querySelectorAll('select[data-slot]').forEach(sel=>sel.onchange=()=>updateSlot(key,sel.dataset.slot,sel.value));slotsHost.querySelectorAll('button[data-regen]').forEach(btn=>btn.onclick=()=>{{const slot=s.slots.find(x=>Number(x.slot_index)===Number(btn.dataset.regen));if(slot)updateSlot(key,slot.slot_index,slot.selected_family_id)}});slotsHost.querySelectorAll('[data-q-layout-slot]').forEach(box=>{{const slot=Number(box.dataset.qLayoutSlot),meta=s.slots.find(x=>Number(x.slot_index)===slot);plc.mountQuestionControls(box,key,slot,plc.questionHasFigure(key,slot)?['workspace','figure']:['workspace'],{{resetLabel:'Use Student Layout'}})}})}}
  function reflowStudent(key,ids){{plc.reflowFixedEntity(key,ids);requestAnimationFrame(checkOverflow)}}
  function reflowCurrent(){{const key=studentSelect.value;if(key)reflowStudent(key,plc.orderedIds(key));else(data.students||[]).forEach(s=>reflowStudent(s.student_key,plc.orderedIds(s.student_key)))}}
  function showStudent(key){{document.querySelectorAll('.checkpoint-form[data-student-key]').forEach(p=>p.classList.toggle('screen-hidden',!!key&&p.dataset.studentKey!==key));plc.setSelectedEntity();if(key)reflowStudent(key,plc.orderedIds(key));renderSlots(key);setTimeout(checkOverflow,0)}}
  async function approveCheckpoint(){{const over=checkOverflow();if(over.size){{setStatus('Approval is blocked until every student fits the fixed two-page form.',true);return}}if(approveBtn)approveBtn.disabled=true;setStatus('Approving Checkpoint…');try{{const r=await fetch('/api/checkpoint/approve',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_id:data.plan_id,fit_confirmed:true,layout_state:plc.exportState()}})}}),resp=await r.json().catch(()=>({{}}));if(!r.ok||!resp.ok)throw new Error(resp.error||('Approval failed ('+r.status+')'));data.approved=true;data.approval=resp.approval||null;if(approveBtn)approveBtn.textContent='Approved Checkpoint';if(approvalStatus){{approvalStatus.textContent='Approved — this Checkpoint is now listed in the local Checkpoint Library.';approvalStatus.className='checkpoint-approval-status'}}setStatus('Checkpoint approved.')}}catch(e){{if(approveBtn)approveBtn.disabled=false;setStatus(e.message||String(e),true)}}}}
  plc=new window.PrintLayoutController({{
    fields:[
      {{key:'workspace',label:'Workspace',min:0,max:1200,step:1,default:0,unit:'px'}},
      {{key:'figure',label:'Figure size',min:0,max:300,step:1,default:100,unit:'%'}}
    ],
    storageKey:'shared-print-layout-checkpoint-v3:'+String(data.plan_id||'default'),initialState:approvedLayout,initialStateAuthoritative:Boolean(data.approved),
    entitySelect:studentSelect,mainMount:'#checkpointLayoutControls',viewMount:'#checkpointViewControls',stage:'.checkpoint-stage',
    pageSelector:'.checkpoint-form',pageBodySelector:'.plc-page-body',entityAttr:'studentKey',questionSelector:'.question[data-slot-index]',questionAttr:'slotIndex',pagesPerEntity:2,sidebarWidth:310,hiddenClass:'screen-hidden',figureBasePx:320,
    wholeLayoutTitle:'Whole Packet Layout',entityLayoutTitle:'Selected Student Layout',wholeResetLabel:'Reset Packet Layout',entityResetLabel:'Use Whole Packet Layout',
    pageLabel:p=>Number(p.dataset.page||0)||'?',bottomReservePx:28,scopeOwnsDescendants:true,figureSelector:'.plc-figure:not(:empty)',
    onChange:(_state,ctx)=>{{if(ctx?.commit)revokeApproval();if(ctx?.commit&&ctx?.level!=='question')renderSlots(studentSelect.value);}},onCommit:()=>{{reflowCurrent();requestAnimationFrame(checkOverflow)}},onReorder:(key,ids)=>{{reflowStudent(key,ids);renderSlots(key)}},onAfterApply:(_state,ctx)=>{{if(ctx?.commit)requestAnimationFrame(checkOverflow)}}
  }});
  studentSelect.onchange=()=>showStudent(studentSelect.value);document.getElementById('checkpointShowAllBtn').onclick=()=>{{studentSelect.value='';showStudent('')}};document.getElementById('checkpointPrintBtn').onclick=()=>{{const over=checkOverflow();if(over.size){{const names=[...over.keys()].filter(Boolean).map(studentName),msg=`${{names.length}} student${{names.length===1?'':'s'}} exceed the fixed two-page layout. Printing now may clip content. Print anyway?`;if(!window.confirm(msg))return}}window.print()}};
  if(approveBtn)approveBtn.onclick=approveCheckpoint;if(approvalStatus&&data.approved){{approvalStatus.textContent='Approved — this Checkpoint is listed in the local Checkpoint Library.';approvalStatus.className='checkpoint-approval-status'}}
  const reveal=document.getElementById('checkpointRevealOutputBtn');if(reveal)reveal.onclick=async()=>{{setStatus('Opening output folder…');try{{const r=await fetch('/api/checkpoint/reveal-output?plan_id='+encodeURIComponent(data.plan_id),{{cache:'no-store'}}),resp=await r.json().catch(()=>({{}}));if(!r.ok||!resp.ok)throw new Error(resp.error||'Could not open output folder.');setStatus('Output folder opened in Finder.')}}catch(e){{setStatus(e.message||String(e),true)}}}};
  const first=(data.students||[])[0];if(first){{studentSelect.value=first.student_key;showStudent(first.student_key)}}else showStudent('');window.addEventListener('load',()=>{{setTimeout(checkOverflow,250);setTimeout(checkOverflow,1400)}});
}})();
</script>'''

def _class_packet_document(github_root: Path, title: str, plan: dict[str, Any], student_forms: list[dict[str, Any]], temp_families: list[dict[str, Any]]) -> str:
    pages = "".join(_student_pages_html(title, normalize_text(f.get("student_display")), normalize_text(f.get("student_key")), list(f.get("questions") or [])) for f in student_forms)
    control_data = _control_data(github_root, plan, student_forms, temp_families)
    options = ''.join(f'<option value="{html.escape(normalize_text(s.get("student_key")), quote=True)}">{html.escape(normalize_text(s.get("student_display")))}</option>' for s in control_data.get("students", []))
    plan_id = html.escape(normalize_text(plan.get("plan_id")), quote=True)
    controls = (
        '<aside class="checkpoint-controls"><h1>Checkpoint Controls</h1><p class="control-note">Preview or adjust one student at a time. Print All always prints every student in two-page order for duplex printing.</p>'
        '<label for="checkpointStudentSelect">Student</label><select id="checkpointStudentSelect"><option value="">All students</option>' + options + '</select>'
        '<div id="checkpointStudentFit" class="checkpoint-student-fit"></div>'
        '<button id="checkpointShowAllBtn">Show All Students</button><button id="checkpointPrintBtn" class="primary-control">Print All · Double-Sided</button>'
        '<section class="checkpoint-control-section"><h2>Preview</h2><div id="checkpointViewControls"></div></section>'
        '<section class="checkpoint-control-section"><div id="checkpointLayoutControls"></div></section>'
        '<div id="checkpointControlSlots" class="checkpoint-control-slots"></div><div id="checkpointControlStatus" class="checkpoint-control-status"></div>'
        '<section class="checkpoint-control-section"><h2>Finish Checkpoint</h2><div id="checkpointFinishReadiness" class="checkpoint-finish-readiness"></div><button id="checkpointApproveBtn" class="primary-control">Approve Checkpoint</button><div id="checkpointApprovalStatus" class="checkpoint-approval-status"></div><label>When finished</label><div class="checkpoint-static-select">Local copy only</div>'
        '<div class="checkpoint-finish-card"><span>Finish destination</span><strong>Only approved Checkpoints appear in the local Checkpoint Library. Student evidence remains private on this Mac.</strong></div>'
        f'<a class="control-link" href="/api/checkpoint/teacher-key.html?plan_id={plan_id}" target="_blank" rel="noopener">Open Teacher Key</a>'
        f'<a class="control-link" href="/api/checkpoint/output.zip?plan_id={plan_id}" download>Download Checkpoint ZIP</a>'
        '<button id="checkpointRevealOutputBtn">Open Output Folder</button></section></aside>'
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{html.escape(title)} - Class Packet</title><style>{_checkpoint_css()}</style>{print_layout_assets.inline_assets()}{_mathjax_head()}</head><body class="packet-with-controls">{controls}'
        f'<main class="checkpoint-stage">{pages}</main><script>{_embedded_generator_scripts()}</script>{_class_controls_script(control_data)}</body></html>'
    )

def checkpoint_library_document(github_root: Path) -> str:
    state_root = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state"
    records: list[tuple[float, dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    if state_root.is_dir():
        for path in state_root.glob("*/plan.json"):
            try:
                plan = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            plan_id = normalize_text(plan.get("plan_id") or path.parent.name)
            assembly = load_checkpoint_assembly(github_root, plan_id)
            approval = load_checkpoint_approval(github_root, plan_id)
            if not assembly or not approval:
                continue
            approved_epoch = float(approval.get("approved_epoch", path.stat().st_mtime) or path.stat().st_mtime)
            records.append((approved_epoch, plan, assembly, approval))
    records.sort(key=lambda x: x[0], reverse=True)
    cards: list[str] = []
    for approved_epoch, plan, assembly, approval in records:
        plan_id = normalize_text(plan.get("plan_id"))
        label = normalize_text(plan.get("custom_name")) or f"Checkpoint {normalize_text(plan.get('item_label')) or ''}".strip()
        stamp = time.strftime("%b %d, %Y · %I:%M %p", time.localtime(approved_epoch)).replace(" 0", " ")
        scope = list(plan.get("eligible_i_cans") or [])
        scope_text = f"{len(scope)} selected I Can" + ("s" if len(scope) != 1 else "")
        links = (
            f'<a href="/api/checkpoint/class-packet.html?plan_id={html.escape(plan_id, quote=True)}">Open / Edit Packet</a>'
            f'<a href="/api/checkpoint/teacher-key.html?plan_id={html.escape(plan_id, quote=True)}">Teacher Key</a>'
            f'<a href="/api/checkpoint/output.zip?plan_id={html.escape(plan_id, quote=True)}">Download ZIP</a>'
        )
        status = f"Approved · {int(assembly.get('student_count', 0) or 0)} students · 2 pages each"
        cards.append('<article class="checkpoint-card">' f'<div><h2>{html.escape(label)}</h2><p>Approved {html.escape(stamp)} · {html.escape(scope_text)}</p><p class="status">{html.escape(status)}</p></div>' f'<div class="links">{links}</div></article>')
    if not cards:
        cards.append('<div class="empty">No approved local Checkpoints yet. Working drafts stay in Assessment Builder until you approve them.</div>')
    css = """*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f4f6f8;color:#173f6d}.wrap{max-width:1040px;margin:30px auto;padding:0 18px}header{background:#173f6d;color:#fff;padding:18px 22px;border-radius:14px;margin-bottom:16px}header h1{margin:0;font-size:2rem}header p{margin:7px 0 0;color:#e7eef8}.links a{text-decoration:none;color:#173f6d;background:#fff;border:1px solid #d4b34e;border-radius:999px;padding:8px 12px;font-weight:800}.checkpoint-card{background:#fff;border:1px solid #d9dee5;border-radius:14px;padding:18px;margin:12px 0;display:flex;justify-content:space-between;gap:18px;align-items:center}.checkpoint-card h2{margin:0 0 5px}.checkpoint-card p{margin:4px 0;color:#667085}.checkpoint-card .status{color:#173f6d;font-weight:700}.links{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.empty{background:#fff;border:1px solid #d9dee5;border-radius:14px;padding:20px;color:#667085}@media(max-width:720px){.checkpoint-card{display:block}.links{justify-content:flex-start;margin-top:14px}}"""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' f'<title>Algebra Checkpoint Library</title><style>{css}</style></head><body><div class="wrap">' '<header><h1>Algebra Checkpoint Library</h1><p>Only teacher-approved Checkpoints are listed here. Working drafts remain in Assessment Builder.</p></header>' + ''.join(cards) + '</div></body></html>')


def clear_checkpoint_assembly(github_root: Path, plan_id: str) -> None:
    revoke_checkpoint_approval(github_root, plan_id)
    out = checkpoint_output_dir(github_root, plan_id)
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    checkpoint_output_zip_path(github_root, plan_id).unlink(missing_ok=True)


def load_checkpoint_assembly(github_root: Path, plan_id: str) -> dict[str, Any] | None:
    path = assembly_manifest_path(github_root, plan_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    ext_path = extension_response_path(github_root, plan_id)
    review_path = family_review_path(github_root, plan_id)
    if data.get("plan_sha256") != _sha256_path(state_path):
        return None
    if data.get("extension_response_sha256", "") != _sha256_path(ext_path):
        return None
    if data.get("family_review_sha256", "") != _sha256_path(review_path):
        return None
    if int(data.get("output_schema_version", 0) or 0) != CHECKPOINT_OUTPUT_SCHEMA_VERSION:
        return None
    return data


def _safe_instance(raw: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    src = raw if isinstance(raw, dict) else fallback
    if not isinstance(src, dict) or not normalize_text(src.get("student_html")):
        src = fallback
    if not isinstance(src, dict) or not normalize_text(src.get("student_html")):
        raise ValueError("Question instance is missing student_html.")
    return {
        "student_html": normalize_text(src.get("student_html")),
        "answer": normalize_text(src.get("answer")),
        "solution": normalize_text(src.get("solution")),
        "scoring_guidance": normalize_text(src.get("scoring_guidance")),
        "generation_note": normalize_text(src.get("generation_note")),
    }


def _write_checkpoint_outputs(github_root: Path, plan: dict[str, Any], student_forms: list[dict[str, Any]], temp_families: list[dict[str, Any]]) -> dict[str, Any]:
    plan_id = normalize_text(plan.get("plan_id"))
    revoke_checkpoint_approval(github_root, plan_id)
    title = normalize_text(plan.get("custom_name")) or f"Checkpoint {normalize_text(plan.get('item_label')) or ''}".strip()
    out = checkpoint_output_dir(github_root, plan_id)
    (out / "students").mkdir(parents=True, exist_ok=True)
    manifest_forms: list[dict[str, Any]] = []
    total_reassess = 0
    total_extensions = 0
    for form in student_forms:
        display = normalize_text(form.get("student_display"))
        sk = normalize_text(form.get("student_key"))
        questions = list(form.get("questions") or [])
        student_doc = _student_document(title, display, sk, questions)
        filename = f"{_safe_file_token(display)}_{_safe_file_token(plan_id, 'checkpoint')}.html"
        rel = f"students/{filename}"
        (out / rel).write_text(student_doc, encoding="utf-8")
        slots = [{"kind": q.get("kind"), "label": q.get("label"), "family_name": q.get("family_name"), "family_id": q.get("family_id"), "i_can_id": q.get("i_can_id")} for q in questions]
        total_reassess += sum(1 for q in questions if q.get("kind") == "reassessment")
        total_extensions += sum(1 for q in questions if q.get("kind") == "extension")
        manifest_forms.append({"student_key": sk, "student_display": display, "file": rel, "question_count": len(questions), "page_count": 2, "slots": slots})

    (out / "class_packet.html").write_text(_class_packet_document(github_root, title, plan, student_forms, temp_families), encoding="utf-8")
    (out / "teacher_key.html").write_text(_teacher_key_document(title, student_forms), encoding="utf-8")
    (out / "assembly_data.json").write_text(json.dumps({"schema_version": 2, "plan_id": plan_id, "student_forms": student_forms}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    ext_path = extension_response_path(github_root, plan_id)
    review_path = family_review_path(github_root, plan_id)
    target = int(plan.get("target_questions_per_student", 6) or 6)
    manifest = {
        "schema_version": 2,
        "output_schema_version": CHECKPOINT_OUTPUT_SCHEMA_VERSION,
        "plan_id": plan_id,
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "student_count": len(manifest_forms),
        "target_questions_per_student": target,
        "pages_per_student": 2,
        "question_count_total": sum(x["question_count"] for x in manifest_forms),
        "reassessment_question_count": total_reassess,
        "extension_question_count": total_extensions,
        "student_forms": manifest_forms,
        "class_packet_file": "class_packet.html",
        "teacher_key_file": "teacher_key.html",
        "plan_sha256": _sha256_path(state_path),
        "extension_response_sha256": _sha256_path(ext_path),
        "family_review_sha256": _sha256_path(review_path),
    }
    zip_path = checkpoint_output_zip_path(github_root, plan_id)
    manifest["output_zip_name"] = zip_path.name
    manifest["output_folder"] = str(out)
    (out / "assembly_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(out.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(out).as_posix())
    return manifest


def assemble_checkpoint(github_root: Path, plan_id: str, instance_overrides: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not state_path.is_file():
        raise ValueError("Checkpoint plan was not found.")
    plan = json.loads(state_path.read_text(encoding="utf-8"))
    temp_families = _load_temp_families_for_assembly(github_root, plan)
    ext_by_index: dict[int, dict[str, Any]] = {}
    reassess_by_ican: dict[str, dict[str, Any]] = {}
    for family in temp_families:
        if normalize_text(family.get("slot_kind")) == "extension":
            try:
                ext_by_index[int(family.get("extension_index"))] = family
            except (TypeError, ValueError):
                pass
        elif normalize_text(family.get("slot_kind")) == "reassessment_family_needed":
            targets = family.get("target_i_can_ids") or []
            if targets:
                reassess_by_ican[normalize_text(targets[0])] = family

    override_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in instance_overrides or []:
        if not isinstance(item, dict):
            continue
        key = (normalize_text(item.get("student_key")), normalize_text(item.get("family_id")), normalize_text(item.get("i_can_id")))
        if all(key):
            override_map[key] = item.get("instance") if isinstance(item.get("instance"), dict) else {}

    target = int(plan.get("target_questions_per_student", 6) or 6)
    clear_checkpoint_assembly(github_root, plan_id)
    student_forms: list[dict[str, Any]] = []
    for student in plan.get("students", []):
        display = normalize_text(student.get("student_display") or student.get("student_key"))
        sk = normalize_text(student.get("student_key"))
        questions: list[dict[str, Any]] = []
        reassessment_records = list(student.get("reassessment_slots") or []) + list(student.get("reassessment_family_requests") or [])
        reassessment_records.sort(key=lambda r: int(r.get("slot", 999) or 999))
        for index, record in enumerate(reassessment_records, start=1):
            family = record.get("family") if isinstance(record.get("family"), dict) else None
            if family is None:
                family = reassess_by_ican.get(normalize_text(record.get("i_can_id")))
            if not family:
                raise ValueError(f"No usable family is available for {display} {record.get('i_can_id', '')}.")
            iid = normalize_text(record.get("i_can_id") or (family.get("target_i_can_ids") or [""])[0])
            fid = normalize_text(family.get("family_id") or family.get("extension_family_id"))
            exemplar = _family_exemplar(family)
            fresh = override_map.get((sk, fid, iid), {})
            instance = _safe_instance(fresh, exemplar)
            unit = ican_sort_key(iid)[0]
            student_html = _embed_bank_assets(github_root, instance.get("student_html", ""), unit)
            instance["student_html"] = student_html
            questions.append({
                "kind": "reassessment",
                "label": f"Question {index}",
                "i_can_id": iid,
                "family_id": fid,
                "family_name": normalize_text(family.get("family_name")),
                "student_html": student_html,
                "exemplar": instance,
            })

        ext_count = int(student.get("extension_count", 0) or 0)
        for ext_index in range(1, ext_count + 1):
            family = ext_by_index.get(ext_index)
            if not family:
                raise ValueError(f"Extension {ext_index} is missing for {display}.")
            exemplar = _family_exemplar(family)
            targets = family.get("target_i_can_ids") or []
            iid = normalize_text(targets[0] if targets else "")
            fid = _temporary_family_id(family)
            instance = _safe_instance({}, exemplar)
            unit = ican_sort_key(iid)[0] if iid else int(plan.get("storage_unit", 1) or 1)
            student_html = _embed_bank_assets(github_root, instance.get("student_html", ""), unit)
            instance["student_html"] = student_html
            questions.append({
                "kind": "extension",
                "label": f"Extension {ext_index}",
                "i_can_id": iid,
                "family_id": fid,
                "family_name": normalize_text(family.get("family_name")),
                "student_html": student_html,
                "exemplar": instance,
            })
        if len(questions) != target:
            raise ValueError(f"{display} assembled with {len(questions)} questions; expected {target}.")
        student_forms.append({"student_key": sk, "student_display": display, "questions": questions})
    return _write_checkpoint_outputs(github_root, plan, student_forms, temp_families)


def manual_adjust_checkpoint(github_root: Path, plan_id: str, student_key: str, slot_index: int, family_id: str, instance: dict[str, Any]) -> dict[str, Any]:
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not state_path.is_file():
        raise ValueError("Checkpoint plan was not found.")
    plan = json.loads(state_path.read_text(encoding="utf-8"))
    data_path = _assembly_data_path(github_root, plan_id)
    if not data_path.is_file():
        raise ValueError("Assemble the Checkpoint before making manual adjustments.")
    assembly_data = json.loads(data_path.read_text(encoding="utf-8"))
    forms = assembly_data.get("student_forms") if isinstance(assembly_data.get("student_forms"), list) else []
    form = next((f for f in forms if normalize_text(f.get("student_key")) == student_key), None)
    if not form:
        raise ValueError("Student form was not found.")
    questions = form.get("questions") if isinstance(form.get("questions"), list) else []
    if slot_index < 1 or slot_index > len(questions):
        raise ValueError("Invalid question slot.")
    current = questions[slot_index - 1]
    temp_families = _load_temp_families_for_assembly(github_root, plan)
    family: dict[str, Any] | None = None
    if current.get("kind") == "extension":
        family = next((f for f in temp_families if normalize_text(f.get("slot_kind")) == "extension" and _temporary_family_id(f) == family_id), None)
    else:
        iid = normalize_text(current.get("i_can_id"))
        family = next((f for f in load_all_banks(github_root).get("families", []) if normalize_text(f.get("family_id")) == family_id and normalize_text(f.get("i_can_id")) == iid), None)
    if not family:
        raise ValueError("That family is not an allowed option for this slot.")
    exemplar = _family_exemplar(family)
    fresh = _safe_instance(instance, exemplar)
    iid = normalize_text(current.get("i_can_id"))
    if current.get("kind") == "extension":
        targets = family.get("target_i_can_ids") or []
        iid = normalize_text(targets[0] if targets else iid)
    unit = ican_sort_key(iid)[0] if iid else int(plan.get("storage_unit", 1) or 1)
    student_html = _embed_bank_assets(github_root, fresh.get("student_html", ""), unit)
    fresh["student_html"] = student_html
    current.update({
        "i_can_id": iid,
        "family_id": normalize_text(family.get("family_id") or family.get("extension_family_id")),
        "family_name": normalize_text(family.get("family_name")),
        "student_html": student_html,
        "exemplar": fresh,
    })
    return _write_checkpoint_outputs(github_root, plan, forms, temp_families)

def save_family_review_decision(github_root: Path, plan_id: str, family_id: str, decision: str) -> dict[str, Any]:
    decision = normalize_text(decision).upper()
    if decision not in {"ACCEPT", "REPLACE"}:
        raise ValueError("Family decision must be ACCEPT or REPLACE.")
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not state_path.is_file():
        raise ValueError("Checkpoint plan was not found.")
    plan = json.loads(state_path.read_text(encoding="utf-8"))
    ext_path = extension_response_path(github_root, plan_id)
    if not ext_path.is_file():
        raise ValueError("Returned temporary families were not found yet.")
    response = json.loads(ext_path.read_text(encoding="utf-8"))
    validation = validate_extension_response(plan, response)
    valid_ids = {_temporary_family_id(f) for f in validation.get("families", [])}
    review = load_family_review(github_root, plan_id)
    decisions = dict(review.get("decisions") or {})
    if family_id == "*":
        if decision != "ACCEPT":
            raise ValueError("Bulk family review only supports ACCEPT.")
        for fid in valid_ids:
            decisions[fid] = "ACCEPT"
    else:
        if family_id not in valid_ids:
            raise ValueError(f"Unknown temporary family id: {family_id}")
        decisions[family_id] = decision
    review = {
        "schema_version": 1,
        "plan_id": plan_id,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "decisions": decisions,
    }
    path = family_review_path(github_root, plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    clear_checkpoint_assembly(github_root, plan_id)
    create_replacement_request_zip(github_root, plan, response, review)
    return checkpoint_status(github_root, plan_id)


def checkpoint_status(github_root: Path, plan_id: str) -> dict[str, Any]:
    state_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not state_path.is_file():
        return {"found": False, "plan_id": plan_id}
    plan = json.loads(state_path.read_text(encoding="utf-8"))
    ext_path = extension_response_path(github_root, plan_id)
    result: dict[str, Any] = {"found": True, "plan": plan, "extensions_ready": False}
    if ext_path.is_file():
        try:
            ext = json.loads(ext_path.read_text(encoding="utf-8"))
            validation = validate_extension_response(plan, ext)
            review = load_family_review(github_root, plan_id)
            decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
            reviewed_families = []
            for family in validation.get("families", []):
                item = dict(family)
                item["review_decision"] = decisions.get(_temporary_family_id(family), "PENDING")
                reviewed_families.append(item)
            accepted = sum(1 for f in reviewed_families if f.get("review_decision") == "ACCEPT")
            replace = sum(1 for f in reviewed_families if f.get("review_decision") == "REPLACE")
            pending = sum(1 for f in reviewed_families if f.get("review_decision") == "PENDING")
            replacement = create_replacement_request_zip(github_root, plan, ext, review) if replace else None
            result.update({
                "extensions_ready": True,
                "extension_response": {**ext, "extension_families": reviewed_families},
                "extension_path": str(ext_path),
                "response_validation": validation,
                "family_review": {
                    **review,
                    "accepted_count": accepted,
                    "replace_count": replace,
                    "pending_count": pending,
                    "all_accepted": bool(validation.get("complete")) and bool(reviewed_families) and pending == 0 and replace == 0,
                },
                "replacement_request_ready": bool(replacement),
            })
        except Exception as exc:
            result["extension_error"] = str(exc)
    assembly = load_checkpoint_assembly(github_root, plan_id)
    if assembly:
        result["assembly_ready"] = True
        result["assembly"] = assembly
        approval = load_checkpoint_approval(github_root, plan_id)
        result["approved"] = bool(approval)
        if approval:
            result["approval"] = approval
    else:
        result["assembly_ready"] = False
        result["approved"] = False
    return result

