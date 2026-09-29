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
import tempfile
import zipfile
from pathlib import Path

VERSION = "portfolio-template-fidelity/1.3"
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


def classes_of_elements(doc: str, required_class: str) -> list[str]:
    out: list[str] = []
    pattern = r"<(?:section|article)\b[^>]*\bclass=[\"']([^\"']+)[\"'][^>]*>"
    for m in re.finditer(pattern, doc, re.I):
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
        errors.append(f'{label}: missing <style id="canonical-portfolio-css"> block')
        return
    actual = sha256_bytes(canonical.encode("utf-8"))
    if actual != css_sha:
        errors.append(f"{label}: embedded canonical CSS hash {actual} != source {css_sha}")
    for attrs, body in blocks:
        if re.search(r"\bid=[\"']canonical-portfolio-css[\"']", attrs, re.I):
            continue
        compact = re.sub(r"\s+", "", body)
        if compact and (not compact.startswith("@page{") or len(compact) > 240):
            errors.append(f"{label}: noncanonical extra visual <style> block detected")


def validate_report_meta(doc: str, expected_template_sha: str, css_sha: str, label: str, errors: list[str]) -> None:
    template_sha = meta_value(doc, "portfolio-template-sha256")
    embedded_css_sha = meta_value(doc, "portfolio-css-sha256")
    if template_sha != expected_template_sha:
        errors.append(f"{label}: portfolio-template-sha256 missing/mismatch")
    if embedded_css_sha != css_sha:
        errors.append(f"{label}: portfolio-css-sha256 missing/mismatch")


def validate_no_unresolved_tokens(doc: str, label: str, errors: list[str]) -> None:
    if re.search(r"\{\{[A-Z0-9_]+\}\}", doc):
        errors.append(f"{label}: unresolved canonical template token remains")


def validate_individual(path: Path, student_sha: str, css_sha: str, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, student_sha, css_sha, label, errors)
    validate_no_unresolved_tokens(doc, label, errors)
    reports = classes_of_elements(doc, "student-report")
    if len(reports) != 1:
        errors.append(f"{label}: expected exactly 1 student-report article, found {len(reports)}")
    required = [
        "Current Progress Report",
        "Essential Standard:",
        "Your current picture",
        "Status guide",
        "Unit Evidence Picture",
        "Recent evidence",
        "Four most recent pieces of assessed evidence",
        "Your Practice",
    ]
    for text in required:
        if text not in doc:
            errors.append(f"{label}: missing canonical fixed section text: {text}")
    if "Mastery Goal snapshot" in doc:
        errors.append(f"{label}: retired Mastery Goal snapshot panel detected")
    if re.search(r'class=["\'][^"\']*\bican-next\b', doc) or "<b>Next:</b>" in doc:
        errors.append(f"{label}: retired visible per-I-Can Next line detected")
    if "student-page" in doc or "student-front" in doc or "student-back" in doc:
        errors.append(f"{label}: legacy fixed-page student shell detected")


def validate_class_packet(path: Path, student_sha: str, css_sha: str, student_count: int, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, student_sha, css_sha, label, errors)
    validate_no_unresolved_tokens(doc, label, errors)
    reports = classes_of_elements(doc, "student-report")
    if len(reports) != student_count:
        errors.append(f"{label}: expected {student_count} student-report articles, found {len(reports)}")


def validate_teacher(path: Path, teacher_sha: str, css_sha: str, errors: list[str]) -> None:
    doc = read_text(path)
    label = path.as_posix()
    validate_styles(doc, css_sha, label, errors)
    validate_report_meta(doc, teacher_sha, css_sha, label, errors)
    validate_no_unresolved_tokens(doc, label, errors)
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
    sections = classes_of_elements(doc, "teacher-page")
    rendered = [c for c in sections if "omit-page" not in c.split()]
    if len(rendered) not in (3, 4):
        errors.append(f"{label}: expected 3 or 4 rendered teacher pages, found {len(rendered)}")
    for phrase in ["Detailed Evidence Appendix", "Brief guided practice", "I-grade intervention need"]:
        if phrase in doc:
            errors.append(f"{label}: forbidden recurring teacher-report section/label present: {phrase}")




def finalize_current_progress_model(results: Path, templates: Path, manifest: dict, errors: list[str]) -> None:
    """Finish reports with the current on-disk progress model before validation.

    Report refreshes can outlive a Curriculum Transfer that replaces the shared
    progress-model module/template. The localhost process may therefore still
    hold the previous imported module in memory. The validator runs in a fresh
    Python process, so it is the safe finalization boundary: if current progress
    tokens remain, load the current module from disk, apply its deterministic
    student/teacher postprocessors against a temporary copy of the authoritative
    current state, then validate the final bytes.
    """
    teacher_rel = manifest.get("teacher_report", "teacher_report/teacher_summary.html") if isinstance(manifest, dict) else "teacher_report/teacher_summary.html"
    teacher = results / str(teacher_rel)
    if not teacher.is_file():
        return
    doc = read_text(teacher)
    if "{{PROGRESS_MODEL_" not in doc and 'class="ican-next"' not in doc and "<b>Next:</b>" not in doc:
        return

    course = str(manifest.get("course") or "").strip()
    try:
        unit = int(manifest.get("unit"))
    except Exception:
        errors.append("progress-model finalizer: results_manifest course/unit missing or invalid")
        return
    if not course:
        errors.append("progress-model finalizer: results_manifest course missing")
        return

    # templates = <GitHub>/memories/Tools/templates/portfolio
    try:
        github_root = templates.parents[3]
    except IndexError:
        errors.append(f"progress-model finalizer: could not resolve GitHub root from {templates}")
        return
    runtime_dir = github_root / "memories" / "Tools" / "portfolio_local_runtime"
    model_path = runtime_dir / "portfolio_progress_model.py"
    state_zip = github_root / "_portfolio_data" / course / f"unit {unit}" / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    if not model_path.is_file():
        errors.append(f"progress-model finalizer: current model missing: {model_path}")
        return
    if not state_zip.is_file():
        errors.append(f"progress-model finalizer: current state missing: {state_zip}")
        return

    try:
        if str(runtime_dir) not in sys.path:
            sys.path.insert(0, str(runtime_dir))
        # This validator is a fresh process. Importing by normal module name means
        # the installed on-disk module is authoritative for this validation run.
        import portfolio_progress_model as progress  # type: ignore

        with tempfile.TemporaryDirectory(prefix="portfolio_validator_progress_") as td:
            work = Path(td)
            with zipfile.ZipFile(state_zip) as z:
                z.extractall(work)
            state_dir = work / "state"
            if not state_dir.is_dir():
                errors.append("progress-model finalizer: state/ directory missing after extracting current state")
                return
            # Use the same deterministic postprocessors as a fresh runtime.
            if hasattr(progress, "_postprocess_student_markup"):
                progress._postprocess_student_markup(results)
            if not hasattr(progress, "_postprocess_teacher_copy"):
                errors.append("progress-model finalizer: current model lacks teacher postprocessor")
                return
            progress._postprocess_teacher_copy(results, state_dir)
    except Exception as exc:
        errors.append(f"progress-model finalizer failed: {exc}")


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

    hashes = {} if errors else {label: sha256_file(path) for label, path in required_sources.items()}

    manifest_path = results / "results_manifest.json"
    manifest: dict = {}
    if not manifest_path.is_file():
        errors.append("results_manifest.json missing")
    else:
        try:
            manifest = json.loads(read_text(manifest_path))
        except Exception as exc:
            errors.append(f"results_manifest.json invalid JSON: {exc}")

    if manifest:
        finalize_current_progress_model(results, templates, manifest, errors)

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
