#!/usr/bin/env python3
"""Private, persistent student / guardian email directory for Portfolio.

The file is in sibling _portfolio_data, never in the source repo or transfers.
Student IDs, not names, control automatic matching to current Portfolio rosters.
"""
from __future__ import annotations

import csv
import io
import os
import re
import tempfile
from pathlib import Path

from portfolio_runtime import github_root_from_runtime, portfolio_root, read_csv, roster_rows

FIELDS = ["student_id", "student_name", "student_email", "guardian_names", "guardian_emails", "active"]
FILENAME = "student_family_contacts_current.csv"
EMAIL_RE = re.compile(r"^[^\s@,;|<>]+@[^\s@,;|<>]+\.[^\s@,;|<>]+$")
ALIASES = {
    "student_id": {"student id", "studentid", "student number", "student num", "student_number", "student_id", "id"},
    "student_name": {"student name", "student_name", "student", "student full name", "name", "student fullname"},
    "student_email": {"student email", "student_email", "student e mail", "student school email", "school email"},
    "guardian_names": {"guardian names", "guardian_names", "parent names", "parent_names", "parent name", "guardian name"},
    "guardian_emails": {"guardian emails", "guardian_emails", "guardian email", "parent emails", "parent email", "parent email address", "parent guardian email", "parent/guardian email", "family email", "parent/guardian emails"},
    "active": {"active", "status"},
}
EXTRA_GUARDIAN_HEADERS = {"parent email 1", "parent email 2", "guardian email 1", "guardian email 2", "mother email", "father email", "guardian 1 email", "guardian 2 email", "parent 1 email", "parent 2 email", "contact 1 email", "contact 2 email", "parent/guardian email 1", "parent/guardian email 2", "parent email address 1", "parent email address 2"}


def contacts_path(root: Path | None = None) -> Path:
    root = root or portfolio_root(github_root_from_runtime())
    return root / "00 Contact Directory" / FILENAME


def clean(value: object) -> str:
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split()).strip()


def norm_header(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[_\-]+", " ", clean(value).lower())).strip()


def split_emails(value: str) -> list[str]:
    result = []
    for part in re.split(r"[|;,\s]+", clean(value)):
        part = part.strip().lower()
        if not part:
            continue
        if not EMAIL_RE.fullmatch(part):
            raise ValueError(f"Invalid email address: {part}")
        if part not in result:
            result.append(part)
    return result


def normalize(row: dict, *, require_recipient: bool = True) -> dict[str, str]:
    sid = clean(row.get("student_id"))
    name = clean(row.get("student_name"))
    if not sid:
        raise ValueError("Student ID is required to match contacts safely with Portfolio reports.")
    student_emails = split_emails(row.get("student_email") or "")
    if len(student_emails) > 1:
        raise ValueError(f"Student {sid}: enter one student email address.")
    guardian = split_emails(row.get("guardian_emails") or "")
    if require_recipient and not (student_emails or guardian):
        raise ValueError(f"Student {sid}: enter a student or parent/guardian email address.")
    active = clean(row.get("active") or "yes").lower()
    if active in {"no", "false", "0", "inactive"}:
        active = "no"
    elif active in {"yes", "true", "1", "active"}:
        active = "yes"
    else:
        raise ValueError(f"Student {sid}: active must be yes or no.")
    return {
        "student_id": sid,
        "student_name": name,
        "student_email": student_emails[0] if student_emails else "",
        "guardian_names": clean(row.get("guardian_names")),
        "guardian_emails": "|".join(guardian),
        "active": active,
    }


def read_current(root: Path | None = None) -> list[dict[str, str]]:
    path = contacts_path(root)
    if not path.is_file():
        return []
    fields, records = read_csv(path)
    if not {"student_id", "guardian_emails", "student_email"}.issubset(fields):
        raise ValueError("The saved family directory has an incompatible header; no updates were made.")
    out = []
    ids = set()
    for record in records:
        norm = normalize(record, require_recipient=False)
        sid = norm["student_id"]
        if sid in ids:
            raise ValueError(f"Duplicate student ID in saved family directory: {sid}")
        ids.add(sid)
        out.append(norm)
    return out


def save_current(rows: list[dict[str, str]], root: Path | None = None) -> None:
    path = contacts_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    # An atomic same-folder replacement avoids half-written addresses if interrupted.
    fd, temp = tempfile.mkstemp(prefix=".family_contacts_", suffix=".csv", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            for row in sorted(rows, key=lambda r: (r["student_name"].lower(), r["student_id"])):
                writer.writerow({key: row.get(key, "") for key in FIELDS})
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _roster_names() -> dict[str, set[str]]:
    # Only needed on import of rows without IDs, never on routine report views.
    from portfolio_support_contacts import _roster_index
    _id_to_name, name_to_ids = _roster_index()
    return name_to_ids


def _match_name(name: str, index: dict[str, set[str]]) -> str:
    from portfolio_support_contacts import _norm_name
    ids = sorted(index.get(_norm_name(name), set()))
    if len(ids) != 1:
        raise ValueError(f"Cannot uniquely match student {name!r} to an existing Portfolio roster. Include student_id.")
    return ids[0]


def _parse_table(filename: str, data: bytes) -> list[dict[str, str]]:
    if Path(filename).suffix.lower() not in {".csv", ".tsv", ".txt"}:
        raise ValueError("Use a CSV or tab-separated text contact file.")
    if len(data) > 3 * 1024 * 1024:
        raise ValueError("Contact file exceeds the 3 MB upload limit.")
    try:
        source = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Export contacts as UTF-8 CSV or TSV.") from None
    if not source.strip():
        raise ValueError("The contact file is empty.")
    delimiter = "\t" if filename.lower().endswith(".tsv") or ("\t" in source.splitlines()[0] and "," not in source.splitlines()[0]) else ","
    reader = csv.DictReader(io.StringIO(source), delimiter=delimiter)
    if not reader.fieldnames:
        raise ValueError("The contact file needs a column header row.")
    mapped = {}
    extra = []
    for field in reader.fieldnames:
        if field is None:
            continue
        nh = norm_header(field)
        if nh in EXTRA_GUARDIAN_HEADERS:
            extra.append(field)
            continue
        for canonical, aliases in ALIASES.items():
            if nh in {norm_header(x) for x in aliases}:
                if canonical == "guardian_emails" and canonical in mapped:
                    extra.append(field)
                elif canonical not in mapped:
                    mapped[canonical] = field
                break
    if not mapped.get("student_id") and not mapped.get("student_name"):
        raise ValueError("Missing Student ID or Student Name column.")
    if not mapped.get("student_email") and not mapped.get("guardian_emails") and not extra:
        raise ValueError("Missing student or guardian/parent email column.")
    rows = []
    for row in reader:
        if not any(clean(v) for v in row.values() if isinstance(v, str)):
            continue
        d = {canonical: clean(row.get(field)) for canonical, field in mapped.items()}
        guardians = [d.get("guardian_emails", "")] + [clean(row.get(field)) for field in extra]
        d["guardian_emails"] = "|".join(x for x in guardians if x)
        rows.append(d)
    if not rows:
        raise ValueError("The file contains no contact rows.")
    if len(rows) > 10000:
        raise ValueError("Too many contact rows in one import.")
    return rows


def _upsert(existing: list[dict[str, str]], new: list[dict[str, str]], *, replace_contact: bool) -> list[dict[str, str]]:
    by_id = {row["student_id"]: dict(row) for row in existing}
    for row in new:
        sid = row["student_id"]
        prior = by_id.get(sid)
        if not prior:
            by_id[sid] = dict(row)
            continue
        if replace_contact:
            # Manual editing explicitly replaces emails; blank student email is allowed.
            by_id[sid] = {**prior, **row, "student_name": row["student_name"] or prior["student_name"]}
        else:
            # Bulk import is additive: never erase contacts omitted by a new export.
            guardians = split_emails(prior["guardian_emails"] + "|" + row["guardian_emails"])
            by_id[sid] = {
                **prior,
                "student_name": row["student_name"] or prior["student_name"],
                "student_email": row["student_email"] or prior["student_email"],
                "guardian_names": row["guardian_names"] or prior["guardian_names"],
                "guardian_emails": "|".join(guardians),
                "active": row["active"],
            }
    return list(by_id.values())


def import_files(files: list[tuple[str, bytes]], root: Path | None = None) -> dict:
    if not files:
        raise ValueError("Choose at least one CSV/TSV contact file.")
    before = read_current(root)
    raw = []
    for filename, data in files:
        raw.extend(_parse_table(filename, data))
    name_index = None
    clean_rows = []
    for row in raw:
        if not clean(row.get("student_id")):
            if name_index is None:
                name_index = _roster_names()
            row["student_id"] = _match_name(row.get("student_name", ""), name_index)
        clean_rows.append(normalize(row))
    # The entire import must validate before any private data is replaced.
    after = _upsert(before, clean_rows, replace_contact=False)
    save_current(after, root)
    return {"status": "PASS", "imported_rows": len(clean_rows), "stored_count": len(after), "message": f"Imported {len(clean_rows)} row(s) into the saved local contact directory."}


def save_manual(form: dict[str, str], root: Path | None = None) -> dict:
    row = normalize(form)
    before = read_current(root)
    after = _upsert(before, [row], replace_contact=True)
    save_current(after, root)
    return {"status": "PASS", "stored_count": len(after), "message": f"Saved contacts for {row['student_name'] or row['student_id']}."}


def api_payload(root: Path | None = None) -> dict:
    rows = read_current(root)
    return {"status": "PASS", "rows": rows, "stored_count": len(rows), "directory": "_portfolio_data/00 Contact Directory/" + FILENAME}


def merge_recipients(state_dir: Path, root: Path, state_recipients: dict[str, dict]) -> dict[str, dict]:
    """Saved contacts override per-unit recipient rows by verified roster ID only."""
    saved = {r["student_id"]: r for r in read_current(root)}
    merged = {sk: dict(record) for sk, record in state_recipients.items()}
    if not saved:
        return merged
    _fields, roster, _by = roster_rows(state_dir)
    for student in roster:
        sid = student["student_id"]
        sk = student["student_key"]
        rec = saved.get(sid)
        if not rec or not sk:
            continue
        target = merged.setdefault(sk, {})
        # Saved nonempty addresses win. A blank student email in a family-only
        # import does not erase a school email already held in the unit state.
        # Deactivation, however, must suppress stale student/family recipients.
        for key in ("student_email", "guardian_emails"):
            if rec["active"] == "no":
                target[key] = ""
            elif rec.get(key):
                target[key] = rec[key]
    return merged
