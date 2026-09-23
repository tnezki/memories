#!/usr/bin/env python3
"""Fail-closed Portfolio report template-fidelity validator.

Validates that report-producing Portfolio output was instantiated from the
registered canonical templates/CSS instead of being re-authored per course/run.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import sys
from pathlib import Path

VERSION = "portfolio-template-fidelity/1.0"
STUDENT_TEMPLATE = "student_packet_template.html"
TEACHER_TEMPLATE = "teacher_summary_template.html"
CSS_FILE = "portfolio.css"
CONTRACT_FILE = "PORTFOLIO_TEMPLATE_CONTRACT.json"
VALIDATOR_REPO_PATH = "Tools/templates/portfolio/verify_portfolio_output.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def classes_of_sections(doc: str, required_class: str) -> list[str]:
    out: list[str] = []
    for m in re.finditer(r"<section\b[^>]*\bclass=[\"']([^\"']+)[\"'][^>]*>", doc, re.I):
        classes = m.group(1).split()
        if required_class in classes:
            out.append(m.group(1))
    return out


def meta_value(doc: str, name: str) -> str | None:
    patterns = [
        rf"<meta\b[^>]*\bname=[\"']{re.escape(name)}[\"'][^>]*\bcontent=[\"']([^\"']+)[\"'][^>]*>",
        rf"<meta\b[^>]*\bcontent=[\"']([^\"']+)[\"'][^>]*\bname=[\"']{re.escape(name)}[\"'][^>]*>",
    ]
    for pattern in patterns:
        m = re.search(pattern, doc, re.I)
        if m:
            return html_lib.unescape(m.group(1)).strip()
    return None


def style_blocks(doc: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for m in re.finditer(r"<style\b([^>]*)>(.*?)</style>", doc, re.I | re.S):
        blocks.append((m.group(1), m.group(2)))
    return blocks


def canonical_css_block(doc: str) -> str | None:
    for attrs, body in style_blocks(doc):
        if re.search(r"\bid=[\"']canonical-portfolio-css[\"']", attrs, re.I):
            return body
    return None


def validate_styles(doc: str, css_sha: str, label: str, errors: list[str]) -> None:
    blocks = style_blocks(doc)
    canonical = canonical_css_block(doc)
    if canonical is None:
        errors.append(f"{label}: missing <style id=\"canonical-portfolio-css\"> block")
        return
    actual = sha256_bytes(canonical.encode("utf-8"))
    if actual != css_sha:
        errors.append(f"{label}: embedded canonical CSS hash {actual} != source {css_sha}")
    for attrs, body in blocks:
        if re.search(r"\bid=[\"']canonical-portfolio-css[\"']", attrs, re.I):
            continue
        compact = re.sub(r"\s+", "", body)
        if not compact.startswith("@page{") or len(compact) > 240:
            errors.append(f"{label}: noncanonical extra visual <style> block detected")


def validate_report_meta(doc: str, expected_template_sha: str, css_sha: str, label: str, errors: list[str]) -> None:
    template_sha = meta_value(doc, "portfolio-template-sha256")
    embedded_css_sha = meta_value(doc, "portfolio-css-sha256")
    if template_sha != expected_template_sha:
        errors.append(f"{label}: portfolio-template-sha256 missing/mismatch")
    if embedded_css_sha != css_sha:
        errors.append(f"{label}: portfolio-css-sha256 missing/mismatch")


def validate_individual(path: Path, student_sha: str, css_sha: str, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, student_sha, css_sha, label, errors)
    sections = classes_of_sections(doc, "student-page")
    if len(sections) != 2:
        errors.append(f"{label}: expected exactly 2 student-page sections, found {len(sections)}")
    if sum("student-front" in c.split() for c in sections) != 1:
        errors.append(f"{label}: expected one student-front page")
    if sum("student-back" in c.split() for c in sections) != 1:
        errors.append(f"{label}: expected one student-back page")
    for required in ["Current Progress Report", "Your current picture", "Unit Evidence Picture", "Recent evidence", "Your Practice"]:
        if required not in doc:
            errors.append(f"{label}: missing canonical fixed section text: {required}")


def validate_class_packet(path: Path, student_sha: str, css_sha: str, student_count: int, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, student_sha, css_sha, label, errors)
    pages = classes_of_sections(doc, "student-page")
    expected = 2 * student_count
    if len(pages) != expected:
        errors.append(f"{label}: expected {expected} student-page sections for {student_count} students, found {len(pages)}")


def validate_teacher(path: Path, teacher_sha: str, css_sha: str, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, teacher_sha, css_sha, label, errors)
    required = ["Class Overview", "Priority Day Groups", "Pull In Students"]
    positions = []
    for heading in required:
        pos = doc.find(heading)
        if pos < 0:
            errors.append(f"{label}: missing canonical teacher heading: {heading}")
        positions.append(pos)
    if all(p >= 0 for p in positions) and positions != sorted(positions):
        errors.append(f"{label}: canonical teacher page order changed")
    whole = doc.find("Whole Class")
    if whole >= 0 and positions[0] >= 0 and positions[1] >= 0 and not (positions[0] < whole < positions[1]):
        errors.append(f"{label}: Whole Class appears outside canonical location")
    sections = classes_of_sections(doc, "teacher-page")
    rendered = [c for c in sections if "omit-page" not in c.split()]
    if len(rendered) not in (3, 4):
        errors.append(f"{label}: expected 3 or 4 rendered teacher pages, found {len(rendered)}")
    forbidden = ["Detailed Evidence Appendix", "Brief guided practice"]
    for phrase in forbidden:
        if phrase in doc:
            errors.append(f"{label}: forbidden recurring teacher-report section/label present: {phrase}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="Unpacked Portfolio results directory")
    ap.add_argument("--templates", required=True, help="Directory containing canonical Portfolio template files")
    ap.add_argument("--write-json", help="Optional QA JSON output path")
    args = ap.parse_args()

    results = Path(args.results).resolve()
    templates = Path(args.templates).resolve()
    errors: list[str] = []

    required_sources = {
        "student_template": templates / STUDENT_TEMPLATE,
        "teacher_template": templates / TEACHER_TEMPLATE,
        "css": templates / CSS_FILE,
        "contract": templates / CONTRACT_FILE,
    }
    for label, path in required_sources.items():
        if not path.is_file():
            errors.append(f"canonical source missing: {label} -> {path}")

    if errors:
        hashes = {}
    else:
        hashes = {label: sha256_file(path) for label, path in required_sources.items()}

    manifest_path = results / "results_manifest.json"
    manifest: dict = {}
    if not manifest_path.is_file():
        errors.append("results_manifest.json missing")
    else:
        try:
            manifest = json.loads(read_text(manifest_path))
        except Exception as exc:
            errors.append(f"results_manifest.json invalid JSON: {exc}")

    if hashes and manifest:
        prov = manifest.get("template_provenance")
        if not isinstance(prov, dict):
            errors.append("results_manifest.json: template_provenance object missing")
        else:
            expected = {
                "student_template_sha256": hashes["student_template"],
                "teacher_template_sha256": hashes["teacher_template"],
                "css_sha256": hashes["css"],
                "contract_sha256": hashes["contract"],
                "validator": VALIDATOR_REPO_PATH,
                "template_fidelity_status": "PASS",
            }
            for key, val in expected.items():
                if prov.get(key) != val:
                    errors.append(f"results_manifest.json: template_provenance.{key} missing/mismatch")
            if not str(prov.get("system_commit", "")).strip():
                errors.append("results_manifest.json: template_provenance.system_commit missing")

        students = manifest.get("students")
        if not isinstance(students, list) or not students:
            errors.append("results_manifest.json: students list missing/empty")
            students = []

        for row in students:
            rel = row.get("report") if isinstance(row, dict) else None
            if not rel:
                errors.append("results_manifest.json: student report path missing")
                continue
            report = results / rel
            if not report.is_file():
                errors.append(f"student report missing: {rel}")
                continue
            validate_individual(report, hashes["student_template"], hashes["css"], errors)

        combined_rel = manifest.get("combined_student_report", "student_reports/class_student_packet.html")
        combined = results / combined_rel
        if not combined.is_file():
            errors.append(f"combined student packet missing: {combined_rel}")
        else:
            validate_class_packet(combined, hashes["student_template"], hashes["css"], len(students), errors)

        teacher_rel = manifest.get("teacher_report", "teacher_report/teacher_summary.html")
        teacher = results / teacher_rel
        if not teacher.is_file():
            errors.append(f"teacher report missing: {teacher_rel}")
        else:
            validate_teacher(teacher, hashes["teacher_template"], hashes["css"], errors)

    result = {
        "schema": VERSION,
        "status": "PASS" if not errors else "FAIL",
        "failure_code": None if not errors else "PORTFOLIO_TEMPLATE_DRIFT",
        "source_sha256": hashes,
        "errors": errors,
    }
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.write_json:
        Path(args.write_json).write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
