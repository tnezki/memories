#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from portfolio_runtime import (
    extract_state,
    github_root_from_runtime,
    portfolio_root,
    read_csv,
    roster_rows,
    scan_states,
    validate_state_zip,
    write_csv,
)

FILE_NAME = "student_support_contacts_current.csv"
FIELDS = ["student_id", "student_name", "staff_name", "staff_email", "role", "support_class", "active"]
EMAIL_RE = re.compile(r"^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+$")
EMAIL_FIND_RE = re.compile(r"[^\s,;|<>]+@[^\s,;|<>]+\.[^\s,;|<>]+")

HEADER_ALIASES = {
    "student_id": {"student_id", "student id", "studentid", "student_num", "student num", "student number", "student_number", "id"},
    "student_name": {"student_name", "student name", "student", "student fullname", "student full name"},
    "staff_name": {"staff_name", "staff name", "staff", "teacher", "teacher_name", "teacher name", "case_manager", "case manager", "support_teacher", "support teacher"},
    "staff_email": {"staff_email", "staff email", "teacher_email", "teacher email", "email", "support_email", "support email"},
    "role": {"role", "staff_role", "staff role", "support_role", "support role"},
    "support_class": {"support_class", "support class", "class", "caseload", "support period", "support_period"},
    "active": {"active", "status", "enabled"},
}


def contacts_path() -> Path:
    root = portfolio_root(github_root_from_runtime())
    path = root / "00 Contact Directory" / FILE_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _clean(value: object) -> str:
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split()).strip()


def _norm_name(value: str) -> str:
    value = _clean(value).lower()
    if "," in value:
        last, first = [x.strip() for x in value.split(",", 1)]
        value = f"{first} {last}".strip()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _truth(value: str, default: bool = True) -> bool:
    v = _clean(value).lower()
    if not v:
        return default
    if v in {"yes", "true", "1", "active", "y"}:
        return True
    if v in {"no", "false", "0", "inactive", "n"}:
        return False
    raise ValueError(f"Unrecognized active value: {value}")


def _display_active(value: str) -> str:
    return "yes" if _truth(value, True) else "no"


def _roster_index() -> tuple[dict[str, str], dict[str, set[str]]]:
    root = portfolio_root(github_root_from_runtime())
    id_to_name: dict[str, str] = {}
    name_to_ids: dict[str, set[str]] = defaultdict(set)
    for course, unit, state in scan_states(root):
        try:
            validate_state_zip(state, course, unit)
            with tempfile.TemporaryDirectory(prefix="portfolio_contact_roster_") as td:
                dest = Path(td)
                extract_state(state, dest)
                state_dir = dest / "state"
                _fields, roster, _by = roster_rows(state_dir)
            for student in roster:
                sid = _clean(student.get("student_id") or student.get("student_key"))
                name = _clean(student.get("display_name") or student.get("student_name"))
                if not sid:
                    continue
                if name and sid not in id_to_name:
                    id_to_name[sid] = name
                if name:
                    name_to_ids[_norm_name(name)].add(sid)
                    raw = _clean(student.get("student_name"))
                    if raw:
                        name_to_ids[_norm_name(raw)].add(sid)
        except Exception:
            continue
    return id_to_name, name_to_ids


def _resolve_student(student_id: str, student_name: str, id_to_name: dict[str, str], name_to_ids: dict[str, set[str]]) -> tuple[str, str]:
    sid = _clean(student_id)
    name = _clean(student_name)
    if sid:
        return sid, name or id_to_name.get(sid, "")
    if not name:
        raise ValueError("Each support row needs a student ID or student name.")
    ids = sorted(name_to_ids.get(_norm_name(name), set()))
    if not ids:
        raise ValueError(f"Could not match student name to the local Portfolio roster: {name}")
    if len(ids) > 1:
        raise ValueError(f"Student name matches more than one local student; use student_id: {name}")
    sid = ids[0]
    return sid, id_to_name.get(sid, name)


def _canonicalize(row: dict[str, str], id_to_name: dict[str, str], name_to_ids: dict[str, set[str]]) -> dict[str, str]:
    sid, student_name = _resolve_student(row.get("student_id", ""), row.get("student_name", ""), id_to_name, name_to_ids)
    staff_name = _clean(row.get("staff_name"))
    email = _clean(row.get("staff_email")).lower()
    active = _display_active(row.get("active", "yes"))
    if not email or not EMAIL_RE.fullmatch(email):
        raise ValueError(f"Support row for {student_name or sid} has a missing/invalid staff email.")
    if active == "yes" and not staff_name:
        raise ValueError(f"Active support row for {student_name or sid} needs staff_name so the email sender can identify the recipient.")
    return {
        "student_id": sid,
        "student_name": student_name,
        "staff_name": staff_name,
        "staff_email": email,
        "role": _clean(row.get("role")) or "Support staff",
        "support_class": _clean(row.get("support_class")),
        "active": active,
    }


def _normalized_header(value: str) -> str:
    return re.sub(r"\s+", " ", _clean(value).lower().replace("-", " ")).strip()


def _header_map(header: list[str]) -> dict[int, str]:
    out: dict[int, str] = {}
    for i, raw in enumerate(header):
        key = _normalized_header(raw)
        for canonical, aliases in HEADER_ALIASES.items():
            if key in aliases:
                out[i] = canonical
                break
    return out


def _parse_tabular(text: str) -> list[dict[str, str]] | None:
    sample = text[:4096]
    dialect = None
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t|;")
    except Exception:
        pass
    if dialect is None:
        return None
    rows = list(csv.reader(io.StringIO(text), dialect))
    rows = [[_clean(x) for x in row] for row in rows if any(_clean(x) for x in row)]
    if not rows:
        return []
    hmap = _header_map(rows[0])
    if "staff_email" not in hmap.values() or not ({"student_id", "student_name"} & set(hmap.values())):
        return None
    out: list[dict[str, str]] = []
    for source in rows[1:]:
        row = {k: "" for k in FIELDS}
        for i, canonical in hmap.items():
            if i < len(source):
                row[canonical] = source[i]
        if any(_clean(v) for v in row.values()):
            out.append(row)
    return out


def _split_loose(line: str) -> list[str]:
    line = line.strip().lstrip("-*• ").strip()
    if "\t" in line:
        return [_clean(x) for x in line.split("\t") if _clean(x)]
    if "|" in line:
        return [_clean(x) for x in line.split("|") if _clean(x)]
    if " - " in line:
        return [_clean(x) for x in line.split(" - ") if _clean(x)]
    if "," in line:
        return [_clean(x) for x in next(csv.reader([line])) if _clean(x)]
    return [_clean(line)] if _clean(line) else []


def _try_student_token(tokens: Iterable[str], id_to_name: dict[str, str], name_to_ids: dict[str, set[str]]) -> tuple[str, str, int] | None:
    values = list(tokens)
    for i, token in enumerate(values):
        t = _clean(token)
        if t in id_to_name:
            return t, id_to_name.get(t, ""), i
    for i, token in enumerate(values):
        ids = sorted(name_to_ids.get(_norm_name(token), set()))
        if len(ids) == 1:
            sid = ids[0]
            return sid, id_to_name.get(sid, _clean(token)), i
    return None


def _parse_loose_notes(text: str, id_to_name: dict[str, str], name_to_ids: dict[str, set[str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    current_staff: dict[str, str] | None = None
    unresolved: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = _split_loose(line)
        email_match = EMAIL_FIND_RE.search(line)
        email = email_match.group(0).rstrip(".,") if email_match else ""
        student = _try_student_token(parts, id_to_name, name_to_ids)

        if email:
            remaining = [p for p in parts if email not in p]
            if student:
                sid, student_name, idx = student
                student_token = parts[idx]
                remaining = [p for p in remaining if p != student_token]
                staff_name = remaining[0] if remaining else ""
                role = remaining[1] if len(remaining) > 1 else "Support staff"
                support_class = remaining[2] if len(remaining) > 2 else ""
                out.append({"student_id": sid, "student_name": student_name, "staff_name": staff_name, "staff_email": email, "role": role, "support_class": support_class, "active": "yes"})
            else:
                staff_parts = [p for p in remaining if not p.lower().startswith(("staff:", "teacher:"))]
                staff_name = staff_parts[0] if staff_parts else ""
                role = staff_parts[1] if len(staff_parts) > 1 else "Support staff"
                support_class = staff_parts[2] if len(staff_parts) > 2 else ""
                current_staff = {"staff_name": staff_name, "staff_email": email, "role": role, "support_class": support_class, "active": "yes"}
            continue

        if current_staff:
            # A line can list multiple students separated by semicolons after a label.
            student_text = re.sub(r"^(students?|caseload)\s*:\s*", "", line, flags=re.I)
            candidates = [x.strip() for x in student_text.split(";") if x.strip()]
            matched_any = False
            for candidate in candidates:
                st = _try_student_token([candidate], id_to_name, name_to_ids)
                if not st:
                    continue
                sid, student_name, _ = st
                out.append({"student_id": sid, "student_name": student_name, **current_staff})
                matched_any = True
            if matched_any:
                continue

        unresolved.append(line)

    if unresolved:
        sample = "; ".join(unresolved[:3])
        extra = "" if len(unresolved) <= 3 else f" (+{len(unresolved)-3} more)"
        raise ValueError("Could not understand these pasted line(s): " + sample + extra)
    return out


def parse_input(text: str) -> list[dict[str, str]]:
    clean = str(text or "").replace("\ufeff", "").strip()
    if not clean:
        return []
    id_to_name, name_to_ids = _roster_index()
    raw_rows = _parse_tabular(clean)
    if raw_rows is None:
        raw_rows = _parse_loose_notes(clean, id_to_name, name_to_ids)
    return [_canonicalize(row, id_to_name, name_to_ids) for row in raw_rows]


def read_current() -> list[dict[str, str]]:
    path = contacts_path()
    if not path.is_file():
        return []
    fields, rows = read_csv(path)
    id_to_name, name_to_ids = _roster_index()
    out: list[dict[str, str]] = []
    for row in rows:
        mapped = {k: _clean(row.get(k)) for k in FIELDS}
        try:
            out.append(_canonicalize(mapped, id_to_name, name_to_ids))
        except Exception:
            # Preserve visibility of malformed legacy rows without letting them be emailed.
            sid = _clean(row.get("student_id"))
            out.append({
                "student_id": sid,
                "student_name": _clean(row.get("student_name")) or id_to_name.get(sid, ""),
                "staff_name": _clean(row.get("staff_name")),
                "staff_email": _clean(row.get("staff_email")),
                "role": _clean(row.get("role")),
                "support_class": _clean(row.get("support_class")),
                "active": "no",
            })
    return out


def save_contacts(rows: list[dict[str, str]], replace: bool = False) -> dict[str, object]:
    path = contacts_path()
    existing = [] if replace else read_current()
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in existing:
        sid = _clean(row.get("student_id"))
        email = _clean(row.get("staff_email")).lower()
        if sid and email:
            by_key[(sid, email)] = {k: _clean(row.get(k)) for k in FIELDS}
    for row in rows:
        sid = _clean(row.get("student_id"))
        email = _clean(row.get("staff_email")).lower()
        by_key[(sid, email)] = {k: _clean(row.get(k)) for k in FIELDS}
    merged = sorted(by_key.values(), key=lambda r: (_norm_name(r.get("student_name", "")), r.get("student_id", ""), _norm_name(r.get("staff_name", "")), r.get("staff_email", "")))
    write_csv(path, FIELDS, merged)
    active = sum(1 for r in merged if _truth(r.get("active", "yes"), True))
    return {"rows": merged, "row_count": len(merged), "active_count": active, "path": str(path)}


def update_from_sources(file_parts: list[tuple[str, bytes]], pasted_text: str, replace: bool = False) -> dict[str, object]:
    combined: list[dict[str, str]] = []
    for name, data in file_parts:
        suffix = Path(name).suffix.lower()
        if suffix not in {".csv", ".txt", ".tsv"}:
            raise ValueError(f"Unsupported support-contact file type: {name}. Use CSV, TSV, or TXT.")
        text = data.decode("utf-8-sig", errors="replace")
        combined.extend(parse_input(text))
    if _clean(pasted_text):
        combined.extend(parse_input(pasted_text))
    if not combined:
        raise ValueError("Upload a support-contact file or paste at least one student-to-staff mapping.")
    # Last occurrence wins if the same student/staff pair appears twice in one update.
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for row in combined:
        dedup[(row["student_id"], row["staff_email"].lower())] = row
    result = save_contacts(list(dedup.values()), replace=replace)
    result["imported_count"] = len(dedup)
    result["replace_mode"] = bool(replace)
    return result


def api_payload() -> dict[str, object]:
    rows = read_current()
    return {
        "status": "PASS",
        "file": str(contacts_path()),
        "row_count": len(rows),
        "active_count": sum(1 for r in rows if _truth(r.get("active", "yes"), True)),
        "rows": rows,
        "fields": FIELDS,
    }
