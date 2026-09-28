#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import portfolio_runtime as runtime

_ALLOWED_STRENGTHS = {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE"}
_ORIGINAL_BUILD_RESULTS = runtime.build_results
_PATCH_INSTALLED = False


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _clip(value: Any, limit: int = 180) -> str:
    text = " ".join(_clean(value).split())
    if len(text) <= limit:
        return text
    cut = text[: max(1, limit - 1)].rstrip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" .,;:") + "…"


def _evidence_signature(row: dict[str, str]) -> tuple[str, ...]:
    event = _clean(row.get("event_id"))
    if event:
        return ("event", event)
    return (
        "fallback",
        _clean(row.get("student_key")),
        _clean(row.get("i_can_id")),
        _clean(row.get("opportunity_id")),
        _clean(row.get("source_label")),
        _clean(row.get("source_date")),
        _clean(row.get("strength")).upper(),
        _clean(row.get("note") or row.get("concise_note")),
    )


def recent_evidence_by_student(state_dir: Path, limit: int = 4) -> dict[str, list[dict[str, str]]]:
    path = state_dir / "evidence_ledger.csv"
    if not path.is_file():
        return {}
    _fields, rows = runtime.read_csv(path)
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: dict[str, set[tuple[str, ...]]] = defaultdict(set)

    # The Portfolio ledger is append-only. Reading it backward therefore gives
    # the true most-recent evidence order, including repeated checks on the same I Can.
    # Family reports intentionally cap this history at four rows to preserve the locked two-page layout.
    for row in reversed(rows):
        sk = _clean(row.get("student_key"))
        iid = _clean(row.get("i_can_id"))
        strength = _clean(row.get("strength")).upper()
        if not sk or not iid or strength not in _ALLOWED_STRENGTHS:
            continue
        sig = _evidence_signature(row)
        if sig in seen[sk]:
            continue
        seen[sk].add(sig)
        if len(out[sk]) < limit:
            out[sk].append(row)
    return dict(out)


def _evidence_row_html(row: dict[str, str]) -> str:
    iid = _clean(row.get("i_can_id"))
    target = _clean(row.get("i_can_exact_text") or row.get("i_can_text") or row.get("statement"))
    strength = _clean(row.get("strength")).replace("_", " ").title()
    source = _clean(row.get("source_label")) or "Portfolio evidence"
    date = _clean(row.get("source_date"))
    note = _clip(row.get("note") or row.get("concise_note") or "", 180)
    if not note:
        note = "This evidence was used in the current Portfolio picture."
    source_line = source + (f" · {date}" if date else "")
    return (
        "<tr>"
        f"<td><b>{html.escape(iid)}</b></td>"
        f"<td>{html.escape(target)}</td>"
        f"<td><b>{html.escape(strength)}</b><br><span>{html.escape(source_line)}</span></td>"
        f"<td>{html.escape(note)}</td>"
        "</tr>"
    )


def _replace_recent_tbody(doc: str, rows_html: str) -> str:
    pattern = re.compile(
        r'(<section class="recent">.*?<tbody>)(.*?)(</tbody>.*?</section>)',
        re.S,
    )
    updated, count = pattern.subn(lambda m: m.group(1) + rows_html + m.group(3), doc, count=1)
    if count != 1:
        raise ValueError("Could not locate the canonical Recent evidence table in a student report.")
    return updated


def _postprocess_student_reports(out_dir: Path, manifest: dict[str, Any], state_dir: Path) -> None:
    recent = recent_evidence_by_student(state_dir, limit=4)
    articles: list[str] = []

    for student in manifest.get("students", []):
        sk = _clean(student.get("student_key"))
        rel = _clean(student.get("report"))
        if not sk or not rel:
            continue
        path = out_dir / rel
        if not path.is_file():
            raise ValueError(f"Student report missing during evidence-history refresh: {rel}")
        rows = recent.get(sk, [])
        if rows:
            rows_html = "".join(_evidence_row_html(row) for row in rows)
        else:
            rows_html = (
                "<tr><td>—</td><td>No assessed evidence is stored yet.</td>"
                "<td>No evidence</td><td>The Portfolio does not yet have a usable evidence record for this student.</td></tr>"
            )
        doc = _replace_recent_tbody(path.read_text(encoding="utf-8"), rows_html)
        path.write_text(doc, encoding="utf-8")
        m = re.search(r'(<article class="student-report">.*?</article>)', doc, re.S)
        if not m:
            raise ValueError(f"Could not isolate student-report article after evidence-history refresh: {sk}")
        articles.append(m.group(1))

    combined_rel = _clean(manifest.get("combined_student_report")) or "student_reports/class_student_packet.html"
    combined = out_dir / combined_rel
    if combined.is_file():
        original = combined.read_text(encoding="utf-8")
        head, sep, rest = original.partition("<body>")
        if not sep or "</body>" not in rest:
            raise ValueError("Could not rebuild combined student packet after evidence-history refresh.")
        tail = rest.split("</body>", 1)[1]
        combined.write_text(head + "<body>\n" + "\n".join(articles) + "\n</body>" + tail, encoding="utf-8")


def _rerun_template_qa(github_root: Path, out_dir: Path) -> None:
    templates = github_root / "memories" / "Tools" / "templates" / "portfolio"
    validator = templates / "verify_portfolio_output.py"
    if not validator.is_file():
        raise ValueError(f"Canonical Portfolio validator missing: {validator}")
    qa_json = out_dir / "qa" / "template_validation.json"
    proc = subprocess.run(
        ["/usr/bin/python3", str(validator), "--results", str(out_dir), "--templates", str(templates), "--write-json", str(qa_json)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if proc.returncode != 0:
        raise ValueError("Portfolio template validator failed after evidence-history refresh:\n" + proc.stdout)


def build_results_with_history(
    github_root: Path,
    runtime_dir: Path,
    state_dir: Path,
    state_manifest: dict[str, Any],
    input_state_sha: str,
    course: str,
    unit: int,
    report_number: int,
    report_date: str,
    latest_label: str,
    latest_date: str,
    class_insights: dict[str, Any] | None,
    out_dir: Path,
) -> dict[str, Any]:
    manifest = _ORIGINAL_BUILD_RESULTS(
        github_root=github_root,
        runtime_dir=runtime_dir,
        state_dir=state_dir,
        state_manifest=state_manifest,
        input_state_sha=input_state_sha,
        course=course,
        unit=unit,
        report_number=report_number,
        report_date=report_date,
        latest_label=latest_label,
        latest_date=latest_date,
        class_insights=class_insights,
        out_dir=out_dir,
    )
    _postprocess_student_reports(Path(out_dir), manifest, Path(state_dir))
    _rerun_template_qa(Path(github_root), Path(out_dir))
    return runtime.read_json(Path(out_dir) / "results_manifest.json")

def install_patch() -> None:
    global _PATCH_INSTALLED
    if _PATCH_INSTALLED:
        return

    # Modules import build_results by value, so patch each runtime entry point that
    # can rebuild Portfolio reports. This keeps one report behavior whether reports
    # are refreshed, a grading result is applied, a roster is updated, or an
    # observation is recorded.
    import apply_grading_result
    import portfolio_companion
    import update_roster

    portfolio_companion.build_results = build_results_with_history
    apply_grading_result.build_results = build_results_with_history
    update_roster.build_results = build_results_with_history
    runtime.build_results = build_results_with_history
    _PATCH_INSTALLED = True
