#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_REQUEST = "portfolio-grading-request/1.0"
SCHEMA_RESULT = "portfolio-grading-result/1.0"
SCHEMA_STATE = "portfolio-portable-state/1"
SCHEMA_RESULTS = "portfolio-results/2.4-local"

GRADE_LABELS = {
    "I": "In Progress",
    "C": "Meeting",
    "B": "Advancing",
    "A": "Mastery",
    "A+": "Mastery + Transfer",
}

COURSE_CONFIG = {
    "Algebra 1": {
        "repo_folder": "algebra",
        "course_repo": "tnezki/algebra",
        "policy_path": "frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework/contracts/portfolio_quick_check_policy.json",
        "units": {
            1: {
                "title": "Foundations of Functions and Algebra",
                "essential_standard": "Use graphs, slope, rules, expressions, and equations as basic tools for Algebra 1.",
                "practice_url": "https://tnezki.github.io/algebra/practice_builder___p7r4x/student_practice_builder.html?unit=1",
                "qr_asset": "algebra_1_unit1.png",
                "learning_map": None,
            }
        },
    },
    "Physics": {
        "repo_folder": "physics",
        "course_repo": "tnezki/physics",
        "policy_path": "frameworks/Physics/PORTFOLIO_POLICY.json",
        "units": {
            1: {
                "title": "Forces, Motion, and Equilibrium",
                "essential_standard": "Students will use evidence and models to explain how forces affect motion. They will identify forces acting on an object, represent forces with vectors and force diagrams, determine net force and equilibrium, apply Newton’s First Law, and connect the resulting force model to whether motion stays the same or changes.",
                "practice_url": "https://tnezki.github.io/physics/practice_builder___p7r4x/student_practice_builder.html?unit=1",
                "qr_asset": "physics_unit1.png",
                "learning_map": "frameworks/2_Framework_Physics/Conceptual_Physics_Framework/curriculum/unit1_learning_map.json",
            }
        },
    },
    "AP Calculus AB": {
        "repo_folder": "apcalc",
        "course_repo": "tnezki/apcalc",
        "policy_path": "frameworks/AP_Calculus_AB/PORTFOLIO_POLICY.json",
        "units": {
            1: {
                "title": "Limits and Continuity",
                "essential_standard": "Limits describe local and end behavior through graphical, numerical, and algebraic representations, and continuity connects those limits to function values and theorem-based conclusions.",
                "practice_url": None,
                "qr_asset": "ap_calculus_ab_unit1.png",
                "learning_map": "frameworks/2_Framework_CALC/AP_Calculus_AB_Framework_v2/curriculum/unit1_portfolio_learning_map.json",
            }
        },
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), [dict(row) for row in r]


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if row.get(k) is None else row.get(k, "") for k in fields})


def ensure_fields(fields: list[str], *needed: str) -> list[str]:
    out = list(fields)
    for name in needed:
        if name not in out:
            out.append(name)
    return out


def github_root_from_runtime() -> Path:
    # .../GitHub/memories/Tools/portfolio_local_runtime/portfolio_runtime.py
    return Path(__file__).resolve().parents[3]


def portfolio_root(github_root: Path | None = None) -> Path:
    root = github_root or github_root_from_runtime()
    return root / "_portfolio_data"


def memories_root(github_root: Path | None = None) -> Path:
    root = github_root or github_root_from_runtime()
    return root / "memories"


def local_git_head(repo_dir: Path) -> str:
    git = repo_dir / ".git"
    if not git.exists():
        return "LOCAL_UNPINNED"
    if git.is_file():
        m = re.search(r"gitdir:\s*(.+)", git.read_text(encoding="utf-8", errors="ignore"))
        if not m:
            return "LOCAL_UNPINNED"
        git = (repo_dir / m.group(1).strip()).resolve()
    head = git / "HEAD"
    if not head.is_file():
        return "LOCAL_UNPINNED"
    value = head.read_text(encoding="utf-8", errors="ignore").strip()
    if re.fullmatch(r"[0-9a-fA-F]{40}", value):
        return value.lower()
    if value.startswith("ref:"):
        ref = value.split(":", 1)[1].strip()
        ref_file = git / ref
        if ref_file.is_file():
            v = ref_file.read_text(encoding="utf-8", errors="ignore").strip()
            if re.fullmatch(r"[0-9a-fA-F]{40}", v):
                return v.lower()
        packed = git / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                sha, _, name = line.partition(" ")
                if name.strip() == ref and re.fullmatch(r"[0-9a-fA-F]{40}", sha):
                    return sha.lower()
    return "LOCAL_UNPINNED"


def state_path(root: Path, course: str, unit: int) -> Path:
    return root / course / f"unit {unit}" / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"


def unit_root(root: Path, course: str, unit: int) -> Path:
    return root / course / f"unit {unit}"


def scan_states(root: Path) -> list[tuple[str, int, Path]]:
    out: list[tuple[str, int, Path]] = []
    if not root.exists():
        return out
    for course_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name != "00 Contact Directory"):
        for unit_dir in sorted(course_dir.glob("unit *")):
            m = re.fullmatch(r"unit\s+(\d+)", unit_dir.name)
            if not m:
                continue
            p = unit_dir / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
            if p.is_file():
                out.append((course_dir.name, int(m.group(1)), p))
    return out


def validate_state_zip(path: Path, expected_course: str | None = None, expected_unit: int | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"State ZIP not found: {path}")
    with zipfile.ZipFile(path) as z:
        try:
            manifest = json.loads(z.read("STATE_MANIFEST.json"))
        except Exception as exc:
            raise ValueError(f"Invalid state ZIP manifest: {exc}") from exc
        if manifest.get("schema") != SCHEMA_STATE or manifest.get("status") != "CURRENT":
            raise ValueError("State ZIP is not a current portfolio-portable-state/1 package")
        if expected_course and manifest.get("course") != expected_course:
            raise ValueError(f"State course mismatch: {manifest.get('course')} != {expected_course}")
        if expected_unit is not None and int(manifest.get("unit", 0)) != int(expected_unit):
            raise ValueError(f"State unit mismatch: {manifest.get('unit')} != {expected_unit}")
        names = set(z.namelist())
        for entry in manifest.get("files", []):
            rel = entry.get("path")
            if not rel or rel not in names:
                raise ValueError(f"State manifest file missing: {rel}")
            if sha256_bytes(z.read(rel)) != entry.get("sha256"):
                raise ValueError(f"State internal hash mismatch: {rel}")
    return manifest


def extract_state(path: Path, dest: Path) -> dict[str, Any]:
    manifest = validate_state_zip(path)
    with zipfile.ZipFile(path) as z:
        z.extractall(dest)
    return manifest


def safe_zip_tree(root: Path, out_zip: Path) -> None:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(root).as_posix())


def normalize_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def roster_rows(state_dir: Path) -> tuple[list[str], list[dict[str, str]], dict[str, dict[str, str]]]:
    fields, rows = read_csv(state_dir / "student_registry.csv")
    out: list[dict[str, str]] = []
    by_key: dict[str, dict[str, str]] = {}
    for r in rows:
        active = r.get("active", "yes")
        is_active = str(active).strip().lower() not in {"no", "false", "0", "inactive"}
        name = (r.get("display_name") or r.get("student_name") or "").strip()
        if "," in name and not r.get("display_name"):
            last, first = [x.strip() for x in name.split(",", 1)]
            display = f"{first} {last}".strip()
        else:
            display = name
        sid = (r.get("student_id") or r.get("student_num") or r.get("student_key") or "").strip()
        n = {
            "student_key": (r.get("student_key") or sid).strip(),
            "student_id": sid,
            "student_name": name,
            "display_name": display,
            "period": (r.get("period") or r.get("class_name") or "").strip(),
            "active": "yes" if is_active else "no",
            "raw": r,
        }
        out.append(n)
        by_key[n["student_key"]] = n
    return fields, out, by_key


def ican_rows(state_dir: Path) -> tuple[list[str], list[dict[str, str]]]:
    return read_csv(state_dir / "i_can_status_current.csv")


def ican_text(row: dict[str, str]) -> str:
    return (row.get("i_can_text") or row.get("i_can_exact_text") or row.get("statement") or "").strip()


def mg_id(row: dict[str, str]) -> str:
    return (row.get("mastery_goal_id") or row.get("mg_code") or row.get("mastery_goal") or "").strip()


def latest_source_label(row: dict[str, str]) -> str:
    return (row.get("latest_source_label") or row.get("latest_source") or "").strip()


def load_learning_map(github_root: Path, course: str, unit: int, state_dir: Path | None = None) -> dict[str, Any]:
    cfg = COURSE_CONFIG.get(course, {}).get("units", {}).get(unit, {})
    path = cfg.get("learning_map")
    if path:
        p = github_root / "memories" / path
        if p.is_file():
            data = read_json(p)
            return data
    # Fallback: build a map from current state without inventing learning statements.
    if state_dir is None:
        raise ValueError(f"No learning map configured for {course} Unit {unit}")
    _, rows = ican_rows(state_dir)
    mg_titles: dict[str, str] = {}
    mg_file = state_dir / "mastery_goal_status_current.csv"
    if mg_file.is_file():
        _, mgrows = read_csv(mg_file)
        for r in mgrows:
            mid = mg_id(r)
            title = (r.get("mastery_goal_title") or "").strip()
            if mid and title:
                mg_titles[mid] = title
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for r in rows:
        mid = mg_id(r)
        iid = (r.get("i_can_id") or "").strip()
        if not mid or not iid or (mid, iid) in seen:
            continue
        seen.add((mid, iid))
        grouped[mid].append({"id": iid, "statement": ican_text(r)})
    return {
        "course": course,
        "unit": unit,
        "unit_title": cfg.get("title", f"Unit {unit}"),
        "essential_standard": cfg.get("essential_standard", ""),
        "mastery_goals": [
            {
                "id": mid,
                "title": mg_titles.get(mid, mid),
                "description": "",
                "i_cans": sorted(items, key=lambda x: x["id"]),
            }
            for mid, items in sorted(grouped.items())
        ],
    }


def status_from_history(current_status: str, events: list[dict[str, str]], explicit_transfer: bool = False) -> tuple[str, str, str, str, int, int]:
    if explicit_transfer or current_status == "TRANSFER":
        return "TRANSFER", "Transfer", "EXTENSION", "Extension", len({e.get("opportunity_id", "") for e in events if e.get("opportunity_id")}), sum(1 for _ in _convincing_ops(events))
    conv = list(_convincing_ops(events))
    convincing_count = len(conv)
    opps = {e.get("opportunity_id", "") for e in events if e.get("opportunity_id")}
    if current_status == "MASTERED" or convincing_count >= 2:
        return "MASTERED", "Mastered", "SECURE", "Secure", len(opps), convincing_count
    if convincing_count == 1:
        return "DEVELOPING", "Developing", "NEEDS_ANOTHER_DEMONSTRATION", "Needs another independent check", len(opps), convincing_count
    usable_or_attempt = [e for e in events if e.get("strength") in {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE"}]
    if usable_or_attempt:
        return "DEVELOPING", "Developing", "PRACTICE_AND_CHECK", "Practice + check soon", len(opps), convincing_count
    return "NO_EVIDENCE", "No Evidence", "NEEDS_FIRST_CHECK", "Needs first check", len(opps), convincing_count


def _convincing_ops(events: list[dict[str, str]]) -> Iterable[str]:
    seen: set[str] = set()
    for e in events:
        if e.get("strength") != "CONVINCING":
            continue
        if not normalize_bool(e.get("independent_opportunity", "")):
            continue
        oid = (e.get("opportunity_id") or "").strip()
        if oid and oid not in seen:
            seen.add(oid)
            yield oid


def mg_grade(ican_group: list[dict[str, str]]) -> dict[str, Any]:
    n = len(ican_group)
    threshold = (n + 1) // 2
    secure = sum(1 for r in ican_group if r.get("status_code") in {"MASTERED", "TRANSFER"})
    assessed = any(r.get("status_code") != "NO_EVIDENCE" for r in ican_group)
    transfer = any(r.get("status_code") == "TRANSFER" for r in ican_group)
    if not assessed:
        return {"assessed": False, "secure": secure, "count": n, "threshold": threshold, "demonstrated": False, "grade": "", "label": "Not assessed", "transfer": transfer}
    if secure < threshold:
        grade = "I"
    elif secure == threshold:
        grade = "C"
    elif secure < n:
        grade = "B"
    elif transfer:
        grade = "A+"
    else:
        grade = "A"
    return {"assessed": True, "secure": secure, "count": n, "threshold": threshold, "demonstrated": secure >= threshold, "grade": grade, "label": GRADE_LABELS[grade], "transfer": transfer}


def display_grade(info: dict[str, Any]) -> str:
    if not info["assessed"]:
        return "Not assessed"
    if info["grade"] == "I":
        return "Grade I · In Progress"
    return f"Grade {info['grade']} · {info['label']}"


def html_escape(x: Any) -> str:
    return html.escape(str(x), quote=True)


def replace_tokens(doc: str, tokens: dict[str, Any]) -> str:
    for k, v in tokens.items():
        doc = doc.replace("{{" + k + "}}", str(v))
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", doc)))
    if unresolved:
        raise ValueError("Unresolved canonical report tokens: " + ", ".join(unresolved))
    return doc


def self_contain(doc: str, css: str, meta_html: str) -> str:
    doc = doc.replace('<link rel="stylesheet" href="portfolio.css">', f'<style id="canonical-portfolio-css">{css}</style>')
    marker = '<meta name="viewport" content="width=device-width,initial-scale=1">'
    doc = doc.replace(marker, marker + "\n" + meta_html, 1)
    return doc


def status_icon(code: str) -> str:
    if code == "TRANSFER":
        return '<span class="status-star">★</span>'
    cls = "status-dot"
    if code == "DEVELOPING":
        cls += " developing"
    elif code == "MASTERED":
        cls += " mastered"
    return f'<span class="{cls}"></span>'


def qr_html(runtime_dir: Path, course: str, unit: int, url: str | None) -> str:
    if not url:
        return ""
    cfg = COURSE_CONFIG.get(course, {}).get("units", {}).get(unit, {})
    asset = cfg.get("qr_asset")
    if not asset:
        return ""
    p = runtime_dir / "qr" / asset
    if not p.is_file():
        return ""
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f'<a href="{html_escape(url)}"><img alt="QR code for Unit {unit} Practice Builder" src="data:image/png;base64,{data}"></a><div class="qrlabel">Practice Builder · Unit {unit}</div>'


def result_source_events(evidence_rows: list[dict[str, str]], label: str, date: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in evidence_rows:
        if (r.get("source_label") or "") == label and (r.get("source_date") or "") == date:
            out[r.get("student_key", "")].append(r)
    return out


def grade_by_student(ican_rows_data: list[dict[str, str]]) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, list[dict[str, str]]]]:
    by_student: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in ican_rows_data:
        by_student[r.get("student_key", "")].append(r)
    grades: dict[str, dict[str, dict[str, Any]]] = {}
    for sk, rows in by_student.items():
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for r in rows:
            grouped[mg_id(r)].append(r)
        grades[sk] = {mid: mg_grade(rr) for mid, rr in grouped.items() if mid}
    return grades, by_student


def build_results(
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
    memories = github_root / "memories"
    templates = memories / "Tools" / "templates" / "portfolio"
    student_template_path = templates / "student_packet_template.html"
    teacher_template_path = templates / "teacher_summary_template.html"
    css_path = templates / "portfolio.css"
    contract_path = templates / "PORTFOLIO_TEMPLATE_CONTRACT.json"
    validator_path = templates / "verify_portfolio_output.py"
    for p in [student_template_path, teacher_template_path, css_path, contract_path, validator_path]:
        if not p.is_file():
            raise ValueError(f"Canonical Portfolio source missing: {p}")
    student_template = student_template_path.read_text(encoding="utf-8")
    teacher_template = teacher_template_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    student_sha = sha256_file(student_template_path)
    teacher_sha = sha256_file(teacher_template_path)
    css_sha = sha256_file(css_path)
    contract_sha = sha256_file(contract_path)
    system_commit = local_git_head(memories)

    learning = load_learning_map(github_root, course, unit, state_dir)
    unit_title = learning.get("unit_title") or COURSE_CONFIG.get(course, {}).get("units", {}).get(unit, {}).get("title", f"Unit {unit}")
    essential = learning.get("essential_standard") or COURSE_CONFIG.get(course, {}).get("units", {}).get(unit, {}).get("essential_standard", "")
    mg_catalog = {m["id"]: m for m in learning.get("mastery_goals", [])}
    mg_order = [m["id"] for m in learning.get("mastery_goals", [])]

    _, roster, roster_by = roster_rows(state_dir)
    active = [r for r in roster if r["active"] == "yes"]
    active_keys = {r["student_key"] for r in active}
    _, icans = ican_rows(state_dir)
    _, evidence = read_csv(state_dir / "evidence_ledger.csv")
    grades, by_student = grade_by_student(icans)
    latest_events = result_source_events(evidence, latest_label, latest_date)
    text_by_ican: dict[str, str] = {}
    for r in icans:
        iid = r.get("i_can_id", "")
        if iid and iid not in text_by_ican:
            text_by_ican[iid] = ican_text(r)

    meta_student = (
        f'<meta name="portfolio-template-sha256" content="{student_sha}">\n'
        f'<meta name="portfolio-css-sha256" content="{css_sha}">\n'
        f'<meta name="portfolio-system-commit" content="{html_escape(system_commit)}">'
    )
    meta_teacher = (
        f'<meta name="portfolio-template-sha256" content="{teacher_sha}">\n'
        f'<meta name="portfolio-css-sha256" content="{css_sha}">\n'
        f'<meta name="portfolio-system-commit" content="{html_escape(system_commit)}">'
    )
    practice_url = COURSE_CONFIG.get(course, {}).get("units", {}).get(unit, {}).get("practice_url")
    qr = qr_html(runtime_dir, course, unit, practice_url)

    def card(sk: str, mid: str) -> str:
        rows = sorted([r for r in by_student.get(sk, []) if mg_id(r) == mid], key=lambda r: r.get("i_can_id", ""))
        info = grades.get(sk, {}).get(mid, mg_grade(rows))
        cat = mg_catalog.get(mid, {"title": mid, "description": ""})
        parts = [f'<div class="mg-card"><div class="mg-head"><h2>{html_escape(mid)} · {html_escape(cat.get("title", mid))}</h2><p>{html_escape(cat.get("description", ""))}</p></div>']
        for r in rows:
            parts.append(
                '<div class="ican">' + status_icon(r.get("status_code", "NO_EVIDENCE")) +
                f'<div><div class="ican-text"><b>{html_escape(r.get("i_can_id", ""))}</b> · {html_escape(ican_text(r))}</div>' +
                f'<div class="ican-next"><b>Next:</b> {html_escape(r.get("student_action_label", ""))}</div></div></div>'
            )
        parts.append(
            f'<div class="mg-foot"><span>{info["secure"]} of {info["count"]} I Cans secure · {info["threshold"]} needed to demonstrate</span><strong>{html_escape(display_grade(info))}</strong></div></div>'
        )
        return "".join(parts)

    individual_manifest: list[dict[str, Any]] = []
    articles: list[str] = []
    student_out = out_dir / "student_reports" / "individual"
    student_out.mkdir(parents=True, exist_ok=True)
    for s in active:
        sk = s["student_key"]
        student_grades = grades.get(sk, {})
        demonstrated = sum(1 for x in student_grades.values() if x.get("demonstrated"))
        chips = []
        for mid in mg_order:
            info = student_grades.get(mid, {"secure": 0, "count": len(mg_catalog.get(mid, {}).get("i_cans", [])), "assessed": False, "grade": "", "label": "Not assessed"})
            chips.append(f'<div class="mg-chip"><b>{html_escape(mid.replace(f"U{unit}-", ""))} · {html_escape(display_grade(info))}</b><span>{info.get("secure",0)}/{info.get("count",0)} secure</span></div>')
        cards = [card(sk, mid) for mid in mg_order]
        recent_rows: list[str] = []
        evs = sorted(latest_events.get(sk, []), key=lambda r: (r.get("i_can_id", ""), r.get("event_id", "")))
        if evs:
            for e in evs:
                note = e.get("note") or e.get("concise_note") or ""
                target = e.get("i_can_exact_text") or text_by_ican.get(e.get("i_can_id", ""), "")
                recent_rows.append(f'<tr><td><b>{html_escape(e.get("i_can_id", ""))}</b></td><td>{html_escape(target)}</td><td>{html_escape((e.get("strength") or "").title())}</td><td>{html_escape(note)}</td></tr>')
        else:
            recent_rows.append('<tr><td>—</td><td>No evidence added from this source</td><td>No submission</td><td>No usable submission was identified for this student in the latest source.</td></tr>')
        pr = [r for r in by_student.get(sk, []) if r.get("student_action_code") == "PRACTICE_AND_CHECK"]
        if pr:
            focus = "".join(f'<li><b>{html_escape(r.get("i_can_id", ""))}</b> · {html_escape(ican_text(r))}</li>' for r in pr)
        else:
            focus = '<li>No current Practice + check soon targets.</li>'
        link_html = f'<a class="practice-link" href="{html_escape(practice_url)}">Open Unit {unit} Practice Builder</a>' if practice_url else ""
        tokens = {
            "COURSE": course,
            "UNIT_NUMBER": unit,
            "UNIT_TITLE": unit_title,
            "STUDENT_NAME": s["display_name"],
            "PERIOD": s["period"],
            "REPORT_NUMBER": report_number,
            "REPORT_DATE": report_date,
            "ESSENTIAL_STANDARD": essential,
            "MG_DEMONSTRATED_COUNT": demonstrated,
            "MG_TOTAL": len(mg_order),
            "APPROVED_CURRENT_PICTURE_TEXT": "Mastery Goal grades are current evidence, not averages, and can improve with new evidence. An I means In Progress and is not permanent. Use the I Can rows below to see what needs a first check, practice + check soon, another independent check, secure, or extension.",
            "MG_CHIPS_HTML": "".join(chips),
            "ICAN_TOTAL": sum(len(mg_catalog.get(mid, {}).get("i_cans", [])) for mid in mg_order) or len({r.get("i_can_id") for r in icans}),
            "PAGE_1_MASTERY_GOAL_CARDS_HTML": "".join(cards),
            "PAGE_2_MASTERY_GOAL_CARDS_HTML": "",
            "LATEST_EVIDENCE_LABEL": latest_label,
            "LATEST_EVIDENCE_DATE": latest_date,
            "RECENT_EVIDENCE_ROWS_HTML": "".join(recent_rows),
            "PRACTICE_FOCUS_ICANS_HTML": focus,
            "PRACTICE_BUILDER_LINK_HTML": link_html,
            "PRACTICE_BUILDER_QR_HTML": qr,
        }
        doc = replace_tokens(self_contain(student_template, css, meta_student), tokens)
        rel = f"student_reports/individual/{sk}.html"
        (out_dir / rel).write_text(doc, encoding="utf-8")
        individual_manifest.append({"student_key": sk, "student_name": s["display_name"], "period": s["period"], "report": rel})
        m = re.search(r'(<article class="student-report">.*?</article>)', doc, re.S)
        if not m:
            raise ValueError(f"Could not isolate student-report article for {sk}")
        articles.append(m.group(1))

    style = f'<style id="canonical-portfolio-css">{css}</style>'
    combined = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n' + meta_student + f'\n<title>{html_escape(course)} Unit {unit} Portfolio - Class Student Reports</title>\n' + style + '\n</head><body>\n' + '\n'.join(articles) + '\n</body></html>\n'
    (out_dir / "student_reports").mkdir(parents=True, exist_ok=True)
    (out_dir / "student_reports" / "class_student_packet.html").write_text(combined, encoding="utf-8")

    # Teacher routing is deterministic; model-provided class_insights may improve explanatory wording.
    practice_counts = Counter(r.get("i_can_id") for r in icans if r.get("student_key") in active_keys and r.get("student_action_code") == "PRACTICE_AND_CHECK")
    if practice_counts:
        whole_ic, whole_count = practice_counts.most_common(1)[0]
    else:
        whole_ic, whole_count = (mg_order[0] + "-IC01" if mg_order else "", 0)
    whole_active = bool(whole_ic and whole_count >= max(5, round(len(active) * 0.6)))

    routing: list[dict[str, Any]] = []
    for s in active:
        rows = by_student.get(s["student_key"], [])
        igrades = sum(1 for x in grades.get(s["student_key"], {}).values() if x.get("grade") == "I")
        practice = [r for r in rows if r.get("student_action_code") == "PRACTICE_AND_CHECK"]
        sev = Counter((r.get("latest_strength") or "").upper() for r in practice)
        if igrades >= 1 and practice:
            routing.append({"student": s, "igrades": igrades, "practice": practice, "sev": (sev["UNUSABLE"], sev["LIMITED"], sev["PARTIAL"])})
    routing.sort(key=lambda x: (-x["igrades"], -len(x["practice"]), -x["sev"][0], -x["sev"][1], -x["sev"][2], x["student"]["student_key"]))
    g1, g2, wait = routing[:15], routing[15:30], routing[30:]
    pull = [x for x in routing if 1 <= len(x["practice"]) <= 2]

    all_grade_codes = [x.get("grade") for d in grades.values() for x in d.values() if x.get("grade")]
    grade_counts = Counter(all_grade_codes)
    practice_total = sum(1 for r in icans if r.get("student_key") in active_keys and r.get("student_action_code") == "PRACTICE_AND_CHECK")
    overview = "".join([
        f'<div class="stat"><strong>{len(active)}</strong><span>Active students</span></div>',
        f'<div class="stat"><strong>{grade_counts.get("I",0)}</strong><span>Current Mastery Goal grades of I</span></div>',
        f'<div class="stat"><strong>{practice_total}</strong><span>Practice + check soon I Can placements</span></div>',
        f'<div class="stat"><strong>{len(pull)}</strong><span>Pull In students with 1-2 actionable gaps</span></div>',
    ])

    secure_counts = Counter()
    for r in icans:
        if r.get("student_key") in active_keys and r.get("status_code") in {"MASTERED", "TRANSFER"}:
            secure_counts[r.get("i_can_id", "")] += 1
    strengths = secure_counts.most_common(3)
    strength_html = '<ul>' + ''.join(f'<li><b>{html_escape(iid)} · {html_escape(text_by_ican.get(iid,""))}</b> — {n} active student status record(s) are currently secure.</li>' for iid, n in strengths) + '</ul>'
    if not strengths:
        strength_html = '<p>No I Can is broadly secure yet; use current evidence to identify the first leverage point.</p>'

    insights = class_insights or {}
    highest_text = insights.get("highest_leverage_pattern")
    if highest_text:
        highest = f'<p>{html_escape(highest_text)}</p>'
    else:
        highest = f'<p><b>{html_escape(whole_ic)} · {html_escape(text_by_ican.get(whole_ic,""))}</b></p><p>{whole_count} of {len(active)} active students currently need Practice + check soon on this target.</p>' if whole_ic else '<p>No common Practice + check soon target is active.</p>'

    latest_by_ic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in evidence:
        if r.get("source_label") == latest_label and r.get("source_date") == latest_date:
            latest_by_ic[r.get("i_can_id", "")].append(r)
    latest_top = sorted(latest_by_ic, key=lambda iid: (-len(latest_by_ic[iid]), iid))[:3]
    latest_lines = []
    for iid in latest_top:
        c = Counter((x.get("strength") or "").upper() for x in latest_by_ic[iid])
        latest_lines.append(f'<li><b>{html_escape(iid)} · {html_escape(text_by_ican.get(iid,""))}</b> — {c.get("CONVINCING",0)} convincing, {c.get("PARTIAL",0)} partial, {c.get("LIMITED",0)} limited, {c.get("UNUSABLE",0)} unusable across {len(latest_by_ic[iid])} source-level judgment(s).</li>')
    latest_picture = '<ul>' + ''.join(latest_lines) + '</ul>' if latest_lines else '<p>No source-level evidence judgments were added in the latest run.</p>'

    whole_ins = insights.get("whole_class") or {}
    whole_pattern = whole_ins.get("evidence_pattern") or (f'{whole_count} active students currently share this Practice + check soon target.' if whole_ic else 'No broad shared target is currently supported.')
    whole_move = whole_ins.get("teacher_move") or 'Model one clean example, name the decision point explicitly, have students correct one near-miss, then collect a short independent check.'
    whole_why = whole_ins.get("why") or (f'{whole_count} of {len(active)} active students share this current actionable need.' if whole_active else 'The current actionable need is not broad enough to justify a Whole Class page.')
    whole_short = whole_ins.get("short_response") or 'Keep the response focused on the exact target and one independently produced check.'

    def target_chips(group: list[dict[str, Any]]) -> str:
        c = Counter(r.get("i_can_id", "") for x in group for r in x["practice"])
        return ''.join(f'<span class="chip{" hot" if i==0 else ""}">{html_escape(iid)} × {n}</span>' for i, (iid, n) in enumerate(c.most_common(7)))

    def student_rows(group: list[dict[str, Any]]) -> str:
        return ''.join(f'<div class="student-row"><b>{html_escape(x["student"]["display_name"])}</b><div class="codes">{html_escape(", ".join(r.get("i_can_id","") for r in x["practice"]))}</div></div>' for x in group)

    def group_summary(group: list[dict[str, Any]], number: int) -> str:
        c = Counter(r.get("i_can_id", "") for x in group for r in x["practice"])
        tops = c.most_common(3)
        if not tops:
            return "No eligible students are currently assigned to this group."
        desc = ", ".join(f'{iid} ({n})' for iid, n in tops)
        return f'The dominant overlapping Practice + check targets are {desc}. Use a common model-practice-check routine, then route any outlier target to a short alternate strip.'

    timeline = '<b>0-4 min</b><span>Model one clean example and name the decision point.</span><b>4-10 min</b><span>Guided practice on the dominant shared target.</span><b>10-16 min</b><span>Independent parallel item; short alternate strip for outlier targets.</span><b>16-20 min</b><span>Quick feedback and route each student to practice or another independent demonstration.</span>'

    def group2_card(group: list[dict[str, Any]]) -> str:
        if not group:
            return ""
        return f'''<div class="group-card second"><div class="group-title"><div><div class="eyebrow">Second priority</div><div class="rank">Group 2</div></div><div class="count"><b>{len(group)} students</b><br>Ranks 16-{15+len(group)}</div></div><div class="mix">{target_chips(group)}</div><div class="student-list">{student_rows(group)}</div><div class="crew-plan"><h3>Best use of the 20-minute Crewtime</h3><p>{html_escape(group_summary(group,2))}</p><div class="timeline">{timeline}</div></div></div>'''

    pull_cards: list[str] = []
    pull_mix = Counter()
    for x in pull:
        needs = []
        for r in x["practice"]:
            iid = r.get("i_can_id", "")
            pull_mix[iid] += 1
            needs.append(f'<div class="need"><b>{html_escape(iid)}</b> · {html_escape(ican_text(r))}</div>')
        pull_cards.append(f'<div class="pull-card"><div class="name">{html_escape(x["student"]["display_name"])}</div><div class="period">{html_escape(x["student"]["period"])}</div>{"".join(needs)}</div>')

    teacher_tokens = {
        "COURSE": course,
        "UNIT_NUMBER": unit,
        "LATEST_EVIDENCE_LABEL": latest_label,
        "LATEST_EVIDENCE_DATE": latest_date,
        "ACTIVE_STUDENT_COUNT": len(active),
        "OVERVIEW_STATS_HTML": overview,
        "MAJOR_STRENGTHS_HTML": strength_html,
        "HIGHEST_LEVERAGE_PATTERN_HTML": highest,
        "WHOLE_CLASS_LANE_COUNT": "1 target" if whole_active else "0",
        "WHOLE_CLASS_LANE_SUMMARY": f'{whole_ic} · {whole_count} students need Practice + check soon.' if whole_active else 'No broad shared target is currently supported.',
        "PULL_IN_COUNT": len(pull),
        "LATEST_EVIDENCE_PICTURE_TITLE": f'Latest evidence picture — {latest_label}',
        "LATEST_EVIDENCE_PICTURE_HTML": latest_picture,
        "WHOLE_CLASS_DISPLAY_CLASS": "" if whole_active else "omit-page",
        "WHOLE_CLASS_ICAN_ID": whole_ic or "—",
        "WHOLE_CLASS_ICAN_TEXT": text_by_ican.get(whole_ic, "No broad target active"),
        "WHOLE_CLASS_AFFECTED_COUNT": whole_count,
        "WHOLE_CLASS_SHORT_CODE": whole_ic or "target",
        "WHOLE_CLASS_EVIDENCE_PATTERN": html_escape(whole_pattern),
        "WHOLE_CLASS_TEACHER_MOVE": html_escape(whole_move),
        "WHOLE_CLASS_WHY": html_escape(whole_why),
        "WHOLE_CLASS_SHORT_RESPONSE": html_escape(whole_short),
        "PRIORITY_SORT_EXPLANATION_HTML": "Eligible students have at least one current assessed Mastery Goal grade I and at least one Practice + check soon target. Ranked by I-grade count, then actionable-gap count, evidence severity, then stable student key.",
        "PRIORITY_GROUP_1_COUNT": len(g1),
        "PRIORITY_GROUP_1_COUNT_SUMMARY_HTML": f'Ranks 1-{len(g1)}' if g1 else 'No eligible students',
        "PRIORITY_GROUP_1_TARGET_CHIPS_HTML": target_chips(g1),
        "PRIORITY_GROUP_1_STUDENTS_HTML": student_rows(g1),
        "PRIORITY_GROUP_1_SUMMARY": html_escape(group_summary(g1, 1)),
        "PRIORITY_GROUP_1_TIMELINE_HTML": timeline,
        "PRIORITY_GROUP_2_CARD_HTML": group2_card(g2),
        "PRIORITY_WAITLIST_HTML": '' if not wait else f'<div class="priority-waitlist">{len(wait)} additional eligible students remain after Group 2 capacity.</div>',
        "PULL_IN_GRID_CLASS": "cols4" if len(pull) > 9 else "",
        "PULL_IN_STUDENT_CARDS_HTML": ''.join(pull_cards),
        "PULL_IN_TARGET_MIX_HTML": ' · '.join(f'{k} × {v}' for k, v in pull_mix.most_common()),
    }
    teacher_doc = replace_tokens(self_contain(teacher_template, css, meta_teacher), teacher_tokens)
    (out_dir / "teacher_report").mkdir(parents=True, exist_ok=True)
    (out_dir / "teacher_report" / "teacher_summary.html").write_text(teacher_doc, encoding="utf-8")

    powerschool_files = build_powerschool_exports(state_dir, out_dir / "powerschool", course, unit, mg_order, grades, active)

    provenance = {
        "system_commit": system_commit,
        "student_template_path": "Tools/templates/portfolio/student_packet_template.html",
        "teacher_template_path": "Tools/templates/portfolio/teacher_summary_template.html",
        "css_path": "Tools/templates/portfolio/portfolio.css",
        "contract_path": "Tools/templates/portfolio/PORTFOLIO_TEMPLATE_CONTRACT.json",
        "validator": "Tools/templates/portfolio/verify_portfolio_output.py",
        "student_template_sha256": student_sha,
        "teacher_template_sha256": teacher_sha,
        "css_sha256": css_sha,
        "contract_sha256": contract_sha,
        "template_fidelity_status": "PASS",
    }
    manifest = {
        "schema": SCHEMA_RESULTS,
        "course": course,
        "unit": unit,
        "unit_title": unit_title,
        "report_number": report_number,
        "report_date": report_date,
        "generated_at": utc_now(),
        "source_mode": "local_grading_result",
        "delivery_mode": "responsive_html",
        "input_state_sha256": input_state_sha,
        "input_state_version": state_manifest.get("state_version"),
        "input_state_id": state_manifest.get("state_id"),
        "latest_evidence": {"label": latest_label, "date": latest_date},
        "students": individual_manifest,
        "combined_student_report": "student_reports/class_student_packet.html",
        "teacher_report": "teacher_report/teacher_summary.html",
        "powerschool_files": powerschool_files,
        "template_provenance": provenance,
        "qa": {"state_integrity": "PASS", "template_fidelity_status": "PENDING_VALIDATOR", "identity_status": "PENDING", "google_drive_used": False},
        "status": "QA_PENDING",
        "failure_code": None,
    }
    write_json(out_dir / "results_manifest.json", manifest)

    # identity QA
    idqa = {"schema": "portfolio-identity-qa/1.0", "status": "PASS", "students": []}
    for row in individual_manifest:
        doc = (out_dir / row["report"]).read_text(encoding="utf-8")
        ok = row["student_name"] in doc
        idqa["students"].append({**row, "visible_identity_match": ok})
        if not ok:
            idqa["status"] = "FAIL"
    write_json(out_dir / "qa" / "identity_checks.json", idqa)
    if idqa["status"] != "PASS":
        raise ValueError("Portfolio identity QA failed")

    qa_json = out_dir / "qa" / "template_validation.json"
    cmd = ["/usr/bin/python3", str(validator_path), "--results", str(out_dir), "--templates", str(templates), "--write-json", str(qa_json)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise ValueError("Canonical Portfolio template validator failed:\n" + proc.stdout)
    manifest = read_json(out_dir / "results_manifest.json")
    manifest["qa"]["template_fidelity_status"] = "PASS"
    manifest["qa"]["identity_status"] = "PASS"
    manifest["status"] = "PASS"
    write_json(out_dir / "results_manifest.json", manifest)
    return manifest


def build_powerschool_exports(state_dir: Path, out_dir: Path, course: str, unit: int, mg_order: list[str], grades: dict[str, dict[str, dict[str, Any]]], active: list[dict[str, str]]) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    templates: list[Path] = []
    for p in state_dir.glob("*.csv"):
        name = p.name.lower()
        if "powerschool_template" in name or name in {"physics_pst.csv", "powerschool_template.csv"}:
            templates.append(p)
    if not templates:
        # No template means no export rather than fabricating PowerSchool structure.
        return []
    files: list[str] = []
    by_period = defaultdict(list)
    for s in active:
        by_period[s["period"]].append(s)

    def template_period(path: Path) -> str | None:
        _, rows = _read_raw_csv(path)
        for row in rows[:8]:
            if row and row[0].strip() == "Class:" and len(row) > 1:
                raw = row[1].strip()
                # Match exact period/class name when possible.
                for period in by_period:
                    if period.lower() in raw.lower() or raw.lower() in period.lower():
                        return period
        if len(by_period) == 1:
            return next(iter(by_period))
        # Algebra templates include period in filename.
        low = path.name.lower()
        for period in by_period:
            if "3rd" in low and "3rd" in period.lower(): return period
            if "6th" in low and "6th" in period.lower(): return period
        return None

    for template in sorted(templates):
        period = template_period(template)
        if not period:
            continue
        _, raw_rows = _read_raw_csv(template)
        header_idx = next((i for i, row in enumerate(raw_rows) if row[:3] == ["Student Num", "Student Name", "Score"]), None)
        if header_idx is None:
            continue
        meta_rows = raw_rows[:header_idx]
        template_students = raw_rows[header_idx + 1:]
        key_by_id = {s["student_id"]: s["student_key"] for s in by_period[period]}
        for idx, mid in enumerate(mg_order, 1):
            rows_out: list[list[str]] = []
            for row in meta_rows:
                rr = list(row)
                if rr and rr[0] == "Assignment Name:":
                    rr = ["Assignment Name:", f"Unit {unit} Mastery Goal {idx}", ""]
                rows_out.append(rr)
            rows_out.append(["Student Num", "Student Name", "Score"])
            for row in template_students:
                if not row:
                    continue
                sid = row[0].strip() if len(row) > 0 else ""
                sk = key_by_id.get(sid)
                score = grades.get(sk, {}).get(mid, {}).get("grade", "") if sk else ""
                name = row[1] if len(row) > 1 else ""
                rows_out.append([sid, name, score])
            safe_period = re.sub(r"[^A-Za-z0-9]+", "_", period).strip("_") or "Class"
            filename = f"{safe_period}_MG{idx:02d}.csv"
            _write_raw_csv(out_dir / filename, rows_out)
            files.append(f"powerschool/{filename}")
    return files


def _read_raw_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [], list(csv.reader(f))


def _write_raw_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerows(rows)


def install_results_to_local_folders(results_dir: Path, target_unit_root: Path) -> None:
    mappings = [
        (results_dir / "student_reports", target_unit_root / "03 Student Packets"),
        (results_dir / "teacher_report", target_unit_root / "04 Class & Intervention Summaries"),
        (results_dir / "powerschool", target_unit_root / "05 PowerSchool Exports"),
    ]
    staging: list[tuple[Path, Path]] = []
    for src, dst in mappings:
        tmp = dst.with_name(dst.name + ".new")
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            for p in src.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(src)
                    (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, tmp / rel)
        staging.append((tmp, dst))
    backups: list[tuple[Path, Path]] = []
    try:
        for tmp, dst in staging:
            backup = dst.with_name(dst.name + ".previous")
            if backup.exists():
                shutil.rmtree(backup)
            if dst.exists():
                dst.rename(backup)
                backups.append((backup, dst))
            tmp.rename(dst)
        for backup, _ in backups:
            if backup.exists():
                shutil.rmtree(backup)
    except Exception:
        for tmp, dst in staging:
            if tmp.exists():
                shutil.rmtree(tmp, ignore_errors=True)
        for backup, dst in reversed(backups):
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            if backup.exists():
                backup.rename(dst)
        raise


def archive_and_install_state(new_zip: Path, current_zip: Path, version: int) -> None:
    data = current_zip.parent
    arch = data / "State Archives"
    arch.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    if current_zip.exists():
        shutil.copy2(current_zip, arch / f"{stamp}_PREVIOUS_State.zip")
    shutil.copy2(new_zip, current_zip)
    shutil.copy2(new_zip, arch / f"{stamp}_State_v{version}.zip")
    if sha256_file(new_zip) != sha256_file(current_zip):
        raise ValueError("Installed state hash mismatch")


def archive_and_install_results(results_zip: Path, unit_root_path: Path) -> None:
    arch = unit_root_path / "02 Portfolio Data" / "Results Archives"
    arch.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    shutil.copy2(results_zip, arch / f"{stamp}_Portfolio_Results.zip")
    shutil.copy2(results_zip, arch / "Latest Portfolio Results.zip")
    if sha256_file(results_zip) != sha256_file(arch / "Latest Portfolio Results.zip"):
        raise ValueError("Installed results hash mismatch")
