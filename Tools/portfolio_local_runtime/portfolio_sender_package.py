#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from portfolio_runtime import (
    github_root_from_runtime,
    portfolio_root,
    read_csv,
    roster_rows,
    sha256_file,
    validate_state_zip,
)

PACKAGE_NAME = "Portfolio_Email_Sender_Package.zip"
MANIFEST_NAME = "sender_manifest.json"
SCHEMA = "portfolio-email-sender-package/1.0"


def _split_emails(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for part in re.split(r"[|;,]", str(value or "")):
        email = part.strip()
        if not email:
            continue
        key = email.lower()
        if key not in seen:
            seen.add(key)
            out.append(email)
    return out


def _load_notes(current: Path) -> tuple[str, dict[str, str]]:
    path = current / "email_message_notes.csv"
    if not path.is_file():
        return "", {}
    weekly = ""
    students: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not weekly:
                weekly = str(row.get("whole_class_note") or "").strip()
            key = str(row.get("student_key") or "").strip()
            if key:
                students[key] = str(row.get("student_note") or "").strip()
    return weekly, students


def _load_support(root: Path) -> dict[str, list[dict[str, str]]]:
    path = root / "00 Contact Directory" / "student_support_contacts_current.csv"
    out: dict[str, list[dict[str, str]]] = {}
    if not path.is_file():
        return out
    _fields, rows = read_csv(path)
    for row in rows:
        active = str(row.get("active") or "yes").strip().lower()
        if active in {"no", "false", "0", "inactive"}:
            continue
        sid = str(row.get("student_id") or "").strip()
        if not sid:
            continue
        item = {
            "name": str(row.get("staff_name") or "").strip(),
            "email": str(row.get("staff_email") or "").strip(),
            "role": str(row.get("role") or "Support staff").strip() or "Support staff",
            "support_class": str(row.get("support_class") or "").strip(),
        }
        out.setdefault(sid, []).append(item)
    return out


def _load_mg_grades(state_dir: Path) -> dict[str, list[dict[str, str]]]:
    path = state_dir / "mastery_goal_status_current.csv"
    result: dict[str, list[dict[str, str]]] = {}
    if not path.is_file():
        return result
    _fields, rows = read_csv(path)
    temp: dict[str, dict[int, dict[str, str]]] = {}
    for row in rows:
        key = str(row.get("student_key") or "").strip()
        code = str(row.get("mastery_goal_id") or row.get("mg_code") or "").strip()
        m = re.search(r"(\d+)$", code)
        if not key or not m:
            continue
        idx = int(m.group(1))
        if idx < 1 or idx > 4:
            continue
        assessed = str(row.get("assessed") or "").strip().lower() in {"true", "yes", "1"}
        grade = str(row.get("grade_code") or "").strip()
        label = str(row.get("grade_label") or "").strip()
        temp.setdefault(key, {})[idx] = {
            "code": code or f"MG{idx}",
            "title": str(row.get("mastery_goal_title") or "").strip(),
            "display": (grade or "—") if assessed else "NA",
            "grade_code": grade,
            "grade_label": label,
            "assessed": "TRUE" if assessed else "FALSE",
        }
    for key, slots in temp.items():
        result[key] = [slots.get(i, {"code": f"MG{i}", "title": "", "display": "—", "grade_code": "", "grade_label": "", "assessed": "FALSE"}) for i in range(1, 5)]
    return result


def build_sender_package(course: str, unit: int) -> dict:
    github_root = github_root_from_runtime()
    root = portfolio_root(github_root)
    unit_dir = root / course / f"unit {unit}"
    current = unit_dir / "06 Email Delivery" / "Current"
    manifest_path = current / "email_delivery_manifest.csv"
    state_zip = unit_dir / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"

    if not manifest_path.is_file():
        raise ValueError("The local email delivery manifest is missing. Prepare selected PDFs first.")
    validate_state_zip(state_zip, course, unit)

    _fields, delivery_rows = read_csv(manifest_path)
    if not delivery_rows:
        raise ValueError("The local email delivery manifest has no rows.")

    weekly_note, student_notes = _load_notes(current)
    support_by_id = _load_support(root)

    with tempfile.TemporaryDirectory(prefix="portfolio_sender_package_") as td:
        td_path = Path(td)
        with zipfile.ZipFile(state_zip) as zf:
            zf.extractall(td_path)
        state_dir = td_path / "state"
        _rf, roster, _by = roster_rows(state_dir)
        roster_by_key = {r["student_key"]: r for r in roster}
        mg_by_key = _load_mg_grades(state_dir)

    package_rows = []
    package_files: list[tuple[Path, str]] = []
    seen_keys: set[str] = set()

    for row in delivery_rows:
        key = str(row.get("student_key") or "").strip()
        if not key:
            raise ValueError("A delivery row is missing student_key.")
        if key in seen_keys:
            raise ValueError(f"Duplicate student_key in local delivery manifest: {key}")
        seen_keys.add(key)

        student = roster_by_key.get(key, {})
        sid = str(student.get("student_id") or "").strip()
        pdf_rel = str(row.get("pdf_file") or "").strip()
        pdf_source = current / pdf_rel if pdf_rel else None
        expected_hash = str(row.get("pdf_sha256") or "").strip().lower()
        identity_verified = str(row.get("identity_verified") or "").strip().upper() == "TRUE"
        ready = str(row.get("ready_to_send") or "").strip().upper() == "TRUE"

        pdf_path = ""
        if ready:
            if not pdf_source or not pdf_source.is_file():
                raise ValueError(f"Prepared PDF is missing for {row.get('student_name') or key}.")
            actual_hash = sha256_file(pdf_source)
            if not expected_hash or actual_hash != expected_hash:
                raise ValueError(f"Prepared PDF hash mismatch for {row.get('student_name') or key}.")
            if not identity_verified:
                raise ValueError(f"Identity verification is missing for {row.get('student_name') or key}.")
            pdf_path = f"PDFs/{pdf_source.name}"
            package_files.append((pdf_source, pdf_path))

        support_details = support_by_id.get(sid, [])
        listed_support = {x.lower() for x in _split_emails(row.get("support_staff_emails") or "")}
        if listed_support:
            support_details = [x for x in support_details if x.get("email", "").lower() in listed_support]
            known = {x.get("email", "").lower() for x in support_details}
            for email in sorted(listed_support - known):
                support_details.append({"name": "", "email": email, "role": "Support staff", "support_class": ""})

        package_rows.append({
            "student_key": key,
            "student_id": sid,
            "student_name": str(row.get("student_name") or student.get("display_name") or "").strip(),
            "period": str(row.get("period") or student.get("period") or "").strip(),
            "student_email": str(row.get("student_email") or "").strip(),
            "guardian_emails": _split_emails(row.get("guardian_emails") or ""),
            "support_staff": support_details,
            "mg_grades": mg_by_key.get(key, [{"code": f"MG{i}", "title": "", "display": "—", "grade_code": "", "grade_label": "", "assessed": "FALSE"} for i in range(1, 5)]),
            "pdf_path": pdf_path,
            "pdf_sha256": expected_hash,
            "identity_verified": identity_verified,
            "ready_to_send": ready,
            "status": str(row.get("status") or "").strip(),
            "whole_class_note": weekly_note,
            "student_note": student_notes.get(key, ""),
        })

    sender_manifest = {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "local _portfolio_data",
        "course": course,
        "unit": unit,
        "rows": package_rows,
    }

    out_path = current / PACKAGE_NAME
    tmp_path = current / (PACKAGE_NAME + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME, json.dumps(sender_manifest, indent=2, ensure_ascii=False) + "\n")
        for source, arcname in package_files:
            zf.write(source, arcname)
    tmp_path.replace(out_path)

    return {
        "status": "PASS",
        "package": str(out_path),
        "course": course,
        "unit": unit,
        "rows": len(package_rows),
        "ready_rows": sum(1 for r in package_rows if r["ready_to_send"]),
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", required=True)
    ap.add_argument("--unit", type=int, required=True)
    args = ap.parse_args()
    print(json.dumps(build_sender_package(args.course, args.unit), indent=2))
