#!/usr/bin/env python3
"""
Read-only Curriculum Build architecture audit for the current Physics Notes pipeline.

Run from the root of the memories repository:
    python3 audit_curriculum_architecture_v2.py

The audit follows the central-registry / flat-PM architecture. It does not mutate files.
`--fix` is accepted only for backward CLI compatibility and still performs no writes.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED_TOOLKIT_ROOT = "resources/Physics_Notes_Image_Toolkit"
EXPECTED_TOOLKIT_CATALOG = "resources/Physics_Notes_Image_Toolkit/IMAGE_CATALOG.json"
EXPECTED_TEXTBOOK_REPO = "tnezki/textbooks"
EXPECTED_TEXTBOOK_ROOT = "physics"
EXPECTED_TEXTBOOK_SECTION_PATTERN = "physics/units/unitN/section_N_S.html"
EXPECTED_MAP_SCHEMA = "physics-notes-map/1.0"
EXPECTED_HANDOFF_SCHEMA = "physics-notes-map-handoff/1.1"
EXPECTED_FLOW_REVISION = "textbook-chunks-v2"

REQUIRED_MEMORIES_FILES = [
    Path("Curriculum_Philosophy.txt"),
    Path("SYSTEM_MANIFEST.json"),
    Path("SYSTEM_RUNTIME_CONTRACT.txt"),
    Path("frameworks/MANIFEST.json"),
    Path("frameworks/Physics/FRAMEWORK.txt"),
    Path("frameworks/Physics/MANIFEST.json"),
    Path("pms_build/MANIFEST.json"),
    Path("pms_build/notes_map.txt"),
    Path("pms_build/notes.txt"),
    Path("pms_build/activities.txt"),
    Path("curriculum_control_panel.html"),
]

TEXT_SUFFIXES = {".txt", ".md", ".json", ".html", ".css", ".js", ".py", ".csv", ".yaml", ".yml", ".xml", ".ini", ".toml"}
SKIP_DIRS = {".git", "__pycache__", ".idea", ".vscode", "node_modules", ".pytest_cache", ".mypy_cache"}
FORBIDDEN_STRINGS = {
    "Tools/Physics_Notes_Image_Toolkit": "retired memories-owned Physics image toolkit path",
    "tnezki/physics-image-toolkit": "retired separate Physics image toolkit repository",
}


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def add(findings, level, path, message, line=None):
    findings.append((level, str(path), line, message))


def load_json(root: Path, rp: Path, findings):
    p = root / rp
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        add(findings, "ERROR", rp, f"invalid JSON: {e}")
        return None


def iter_text_files(root: Path, self_path: Path):
    for p in root.rglob("*"):
        if not p.is_file() or p.resolve() == self_path.resolve():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in TEXT_SUFFIXES or p.name in {"README", "LICENSE", "Makefile"}:
            yield p


def check_required_files(root, findings):
    for rp in REQUIRED_MEMORIES_FILES:
        if not (root / rp).exists():
            add(findings, "ERROR", rp, "required current architecture file is missing")


def check_forbidden(root, self_path, findings):
    for p in iter_text_files(root, self_path):
        text = read_text(p)
        if text is None:
            continue
        for needle, desc in FORBIDDEN_STRINGS.items():
            for n, line in enumerate(text.splitlines(), 1):
                if needle in line:
                    add(findings, "ERROR", rel(root, p), f"{desc}: {needle!r}", n)


def check_framework_manifest(root, findings):
    rp = Path("frameworks/Physics/MANIFEST.json")
    data = load_json(root, rp, findings)
    if not isinstance(data, dict):
        return
    resources = data.get("course_resources", {})

    toolkit = resources.get("physics_notes_image_toolkit")
    if not isinstance(toolkit, dict):
        add(findings, "ERROR", rp, "missing course_resources.physics_notes_image_toolkit")
    else:
        for key, expected in {
            "repo_scope": "course",
            "root": EXPECTED_TOOLKIT_ROOT,
            "catalog": EXPECTED_TOOLKIT_CATALOG,
            "delivery": "reference_in_place",
        }.items():
            if toolkit.get(key) != expected:
                add(findings, "ERROR", rp, f"physics_notes_image_toolkit.{key} must be {expected!r}; got {toolkit.get(key)!r}")

    textbook = resources.get("physics_textbook")
    if not isinstance(textbook, dict):
        add(findings, "ERROR", rp, "missing course_resources.physics_textbook")
    else:
        for key, expected in {
            "repo_scope": "external",
            "repo": EXPECTED_TEXTBOOK_REPO,
            "root": EXPECTED_TEXTBOOK_ROOT,
            "section_pattern": EXPECTED_TEXTBOOK_SECTION_PATTERN,
            "delivery": "reference_in_place",
            "role": "notes_instructional_spine",
        }.items():
            if textbook.get(key) != expected:
                add(findings, "ERROR", rp, f"physics_textbook.{key} must be {expected!r}; got {textbook.get(key)!r}")


def check_build_registry(root, findings):
    rp = Path("pms_build/MANIFEST.json")
    data = load_json(root, rp, findings)
    if not isinstance(data, dict):
        return
    jobs = {j.get("job"): j for j in data.get("jobs", []) if isinstance(j, dict)}
    expected = {
        "notes_map_4a": "pms_build/notes_map.txt",
        "notes_build_4b": "pms_build/notes.txt",
        "activities": "pms_build/activities.txt",
    }
    for job, entrypoint in expected.items():
        row = jobs.get(job)
        if not row:
            add(findings, "ERROR", rp, f"central build registry is missing {job}")
            continue
        if row.get("entrypoint") != entrypoint:
            add(findings, "ERROR", rp, f"{job}.entrypoint must be {entrypoint!r}; got {row.get('entrypoint')!r}")
        if row.get("path") != entrypoint:
            add(findings, "ERROR", rp, f"{job}.path must be the flat file {entrypoint!r}; got {row.get('path')!r}")


def require_strings(root, rp, strings, findings):
    p = root / rp
    if not p.exists():
        return
    low = (read_text(p) or "").lower()
    for s in strings:
        if s.lower() not in low:
            add(findings, "ERROR", rp, f"missing required contract text: {s!r}")


def check_pm_contracts(root, findings):
    require_strings(root, Path("pms_build/notes_map.txt"), [
        "4A · BUILD PHYSICS NOTES MAP PM v1.8",
        "TEXTBOOK-CHUNK / NOTABILITY FLOW",
        "course_resources.physics_textbook",
        "course_resources.physics_notes_image_toolkit",
        "textbook-chunks-v2",
        "ONE processing event",
        "2–4 questions",
        "Vocabulary Preview",
        "What I Figured Out",
        "uN_notes_map.json",
        "physics-notes-map/1.0",
        "physics-notes-map-handoff/1.1",
        "30–40 minute",
    ], findings)

    require_strings(root, Path("pms_build/notes.txt"), [
        "4B · BUILD PHYSICS NOTES PM v1.5",
        "TEXTBOOK-CHUNK / NOTABILITY FLOW",
        "textbook-chunks-v2",
        "Notability",
        "ONE thing you notice",
        "ONE thing you wonder",
        "What I Figured Out",
        "answers in RED",
        "Teacher Moves",
        "Student Discourse Moves",
        "css/base.css",
        "css/notes.css",
        "30–40 minute",
    ], findings)

    text = read_text(root / "pms_build/notes.txt") or ""
    if "pms_build/notes/references/css/" in text:
        add(findings, "ERROR", "pms_build/notes.txt", "4B still depends on retired PM-local CSS snapshots")


def check_runtime_contract(root, findings):
    rp = Path("SYSTEM_RUNTIME_CONTRACT.txt")
    text = read_text(root / rp) or ""
    for s in ["PMs own procedure", "manifests own stable discovery", "Git history owns version history"]:
        if s.lower() not in text.lower():
            add(findings, "ERROR", rp, f"runtime contract missing architecture rule: {s!r}")


def check_control_panel(root, findings):
    rp = Path("curriculum_control_panel.html")
    text = read_text(root / rp) or ""
    # Fallbacks are non-authoritative because normal discovery uses pms_build/MANIFEST.json.
    stale = [
        "pms_build/notes_map/PM.txt",
        "pms_build/notes/PM.txt",
        "pms_build/activities/PM.txt",
    ]
    if any(x in text for x in stale):
        add(findings, "WARN", rp, "hard-coded BUILD_FALLBACK still contains pre-flatten PM paths; normal manifest discovery is correct, but clean this once the PM flatten migration is complete")
    if "notes/unit${unit}_notes_map/unit${unit}_notes_map.json" in text:
        add(findings, "WARN", rp, "4B source display still advertises the legacy Notes Map path; current PM resolves uN_notes_map")
    if EXPECTED_TOOLKIT_ROOT in text or "physics_notes_image_toolkit" in text:
        add(findings, "ERROR", rp, "Control Panel should not own Physics toolkit location/dependency logic")
    if EXPECTED_TEXTBOOK_REPO in text or "physics_textbook" in text:
        add(findings, "ERROR", rp, "Control Panel should not own Physics textbook location/dependency logic")


def find_sibling(root, names):
    for name in names:
        p = root.parent / name
        if p.is_dir():
            return p
    return None


def audit_map_folder(root, folder, n, new_style, findings):
    map_name = f"u{n}_notes_map.json" if new_style else f"unit{n}_notes_map.json"
    html_name = f"u{n}_notes_map.html" if new_style else f"unit{n}_notes_map.html"
    map_path = folder / map_name
    html_path = folder / html_name
    handoff_path = folder / "NOTES_MAP_HANDOFF.json"

    if not map_path.exists():
        add(findings, "ERROR", rel(root.parent, folder), f"missing map JSON {map_name}")
        return
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except Exception as e:
        add(findings, "ERROR", rel(root.parent, map_path), f"invalid JSON: {e}")
        return

    if data.get("schema") != EXPECTED_MAP_SCHEMA:
        add(findings, "ERROR", rel(root.parent, map_path), f"map schema must be {EXPECTED_MAP_SCHEMA!r}; got {data.get('schema')!r}")
    if data.get("notes_flow_revision") != EXPECTED_FLOW_REVISION:
        add(findings, "WARN", rel(root.parent, map_path), "map is from the pre-critique flow; rerun 4A before using current 4B")
    for key in ("source_bank_fingerprint_method", "source_bank_fingerprint"):
        if not data.get(key):
            add(findings, "ERROR", rel(root.parent, map_path), f"missing top-level {key}")

    if not html_path.exists():
        add(findings, "WARN", rel(root.parent, folder), f"missing derived readable map {html_name}")
    else:
        html = read_text(html_path) or ""
        for marker in ("{esc(", "{{", "<%"):
            if marker in html:
                add(findings, "ERROR", rel(root.parent, html_path), f"unresolved template/code token: {marker!r}")

    if handoff_path.exists():
        try:
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
        except Exception as e:
            add(findings, "WARN", rel(root.parent, handoff_path), f"derived handoff malformed; regenerate: {e}")
        else:
            if handoff.get("schema") != EXPECTED_HANDOFF_SCHEMA:
                add(findings, "WARN", rel(root.parent, handoff_path), f"handoff schema should be {EXPECTED_HANDOFF_SCHEMA!r}")
            if handoff.get("source_bank_fingerprint") != data.get("source_bank_fingerprint"):
                add(findings, "WARN", rel(root.parent, handoff_path), "derived handoff fingerprint does not match map")
            if data.get("notes_flow_revision") == EXPECTED_FLOW_REVISION and handoff.get("notes_flow_revision") != EXPECTED_FLOW_REVISION:
                add(findings, "WARN", rel(root.parent, handoff_path), "derived handoff flow revision does not match map")
    else:
        add(findings, "WARN", rel(root.parent, folder), "derived NOTES_MAP_HANDOFF.json missing; current 4B may regenerate it")


def check_sibling_physics(root, findings):
    physics = find_sibling(root, ("physics", "Physics"))
    if physics is None:
        add(findings, "INFO", "../physics", "sibling Physics repo not found; skipped local course-resource/output audit")
        return
    for rp in [Path(EXPECTED_TOOLKIT_ROOT), Path(EXPECTED_TOOLKIT_CATALOG), Path("css/base.css"), Path("css/notes.css")]:
        if not (physics / rp).exists():
            add(findings, "ERROR", rel(root.parent, physics / rp), "required Physics course dependency is missing")
    notes = physics / "notes"
    if not notes.is_dir():
        return
    for folder in sorted(notes.iterdir()):
        if not folder.is_dir():
            continue
        m = re.fullmatch(r"u(\d+)_notes_map", folder.name)
        if m:
            audit_map_folder(root, folder, int(m.group(1)), True, findings)
            continue
        m = re.fullmatch(r"unit(\d+)_notes_map", folder.name)
        if m:
            audit_map_folder(root, folder, int(m.group(1)), False, findings)


def check_sibling_textbooks(root, findings):
    textbooks = find_sibling(root, ("textbooks", "Textbooks"))
    if textbooks is None:
        add(findings, "INFO", "../textbooks", "sibling textbooks repo not found; runtime will verify the pinned GitHub textbook dependency")
        return
    for rp in [Path("physics/index.html"), Path("physics/units")]:
        if not (textbooks / rp).exists():
            add(findings, "ERROR", rel(root.parent, textbooks / rp), "required Physics textbook resource is missing")


def run_checks(root: Path, self_path: Path):
    findings = []
    check_required_files(root, findings)
    check_forbidden(root, self_path, findings)
    check_framework_manifest(root, findings)
    check_build_registry(root, findings)
    check_pm_contracts(root, findings)
    check_runtime_contract(root, findings)
    check_control_panel(root, findings)
    check_sibling_physics(root, findings)
    check_sibling_textbooks(root, findings)
    return findings


def print_report(findings):
    rank = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings = sorted(findings, key=lambda x: (rank.get(x[0], 9), x[1], x[2] or 0))
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    print("\nCURRICULUM ARCHITECTURE AUDIT v2 — FLAT PHYSICS NOTES PMs")
    print("=" * 80)
    for level, path, line_no, msg in findings:
        counts[level] = counts.get(level, 0) + 1
        loc = f"{path}:{line_no}" if line_no else path
        print(f"[{level}] {loc} — {msg}")
    if not findings:
        print("PASS — no findings")
    print("=" * 80)
    print(f"ERROR={counts['ERROR']} WARN={counts['WARN']} INFO={counts['INFO']}")
    return counts["ERROR"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="memories repository root")
    parser.add_argument("--fix", action="store_true", help="accepted for compatibility; audit remains read-only")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if args.fix:
        print("NOTE: --fix is compatibility-only; this audit performs no mutations.")
    errors = print_report(run_checks(root, Path(__file__).resolve()))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
