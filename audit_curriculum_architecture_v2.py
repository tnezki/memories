#!/usr/bin/env python3
"""
audit_curriculum_architecture_v2.py

Current Curriculum Build architecture audit for the Physics Notes pipeline.
Run from the root of the memories repository:

    python3 audit_curriculum_architecture_v2.py

This audit is read-only. It checks the current central-manifest architecture,
Physics textbook-spine Notes contracts, course-owned image/CSS dependencies,
and any local sibling Physics Notes Map artifacts it can see.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {
    ".txt", ".md", ".json", ".html", ".css", ".js", ".py", ".csv",
    ".yaml", ".yml", ".xml", ".ini", ".toml"
}
SKIP_DIRS = {".git", "__pycache__", ".idea", ".vscode", "node_modules", ".pytest_cache", ".mypy_cache"}

EXPECTED_TOOLKIT_ROOT = "resources/Physics_Notes_Image_Toolkit"
EXPECTED_TOOLKIT_CATALOG = "resources/Physics_Notes_Image_Toolkit/IMAGE_CATALOG.json"
EXPECTED_TEXTBOOK_REPO = "tnezki/textbooks"
EXPECTED_TEXTBOOK_ROOT = "physics"
EXPECTED_TEXTBOOK_SECTION_PATTERN = "physics/units/unitN/section_N_S.html"
EXPECTED_4A_MAP_SCHEMA = "physics-notes-map/1.0"
EXPECTED_4A_HANDOFF_SCHEMA = "physics-notes-map-handoff/1.1"

REQUIRED_MEMORIES_FILES = [
    Path("Curriculum_Philosophy.txt"),
    Path("SYSTEM_MANIFEST.json"),
    Path("SYSTEM_RUNTIME_CONTRACT.txt"),
    Path("frameworks/MANIFEST.json"),
    Path("frameworks/Physics/FRAMEWORK.txt"),
    Path("frameworks/Physics/MANIFEST.json"),
    Path("pms_build/MANIFEST.json"),
    Path("pms_build/notes_map/PM.txt"),
    Path("pms_build/notes/PM.txt"),
    Path("curriculum_control_panel.html"),
]

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


def iter_text_files(root: Path, self_path: Path):
    for p in root.rglob("*"):
        if not p.is_file() or p.resolve() == self_path.resolve():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in TEXT_SUFFIXES or p.name in {"README", "LICENSE", "Makefile"}:
            yield p


def check_required_files(root: Path, findings: list):
    for rp in REQUIRED_MEMORIES_FILES:
        if not (root / rp).exists():
            add(findings, "ERROR", rp, "required current architecture file is missing")


def check_repo_wide_forbidden(root: Path, self_path: Path, findings: list):
    for p in iter_text_files(root, self_path):
        text = read_text(p)
        if text is None:
            continue
        for needle, desc in FORBIDDEN_STRINGS.items():
            for line_no, line in enumerate(text.splitlines(), start=1):
                if needle in line:
                    add(findings, "ERROR", rel(root, p), f"{desc}: {needle!r}", line_no)


def load_json(root: Path, rp: Path, findings: list):
    p = root / rp
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        add(findings, "ERROR", rp, f"invalid JSON: {e}")
        return None


def check_framework_manifest(root: Path, findings: list):
    rp = Path("frameworks/Physics/MANIFEST.json")
    data = load_json(root, rp, findings)
    if not isinstance(data, dict):
        return

    resources = data.get("course_resources", {})
    toolkit = resources.get("physics_notes_image_toolkit")
    if not isinstance(toolkit, dict):
        add(findings, "ERROR", rp, "missing course_resources.physics_notes_image_toolkit")
    else:
        checks = {
            "repo_scope": "course",
            "root": EXPECTED_TOOLKIT_ROOT,
            "catalog": EXPECTED_TOOLKIT_CATALOG,
            "delivery": "reference_in_place",
        }
        for key, expected in checks.items():
            if toolkit.get(key) != expected:
                add(findings, "ERROR", rp, f"physics_notes_image_toolkit.{key} must be {expected!r}; got {toolkit.get(key)!r}")

    textbook = resources.get("physics_textbook")
    if not isinstance(textbook, dict):
        add(findings, "ERROR", rp, "missing course_resources.physics_textbook")
    else:
        checks = {
            "repo_scope": "external",
            "repo": EXPECTED_TEXTBOOK_REPO,
            "root": EXPECTED_TEXTBOOK_ROOT,
            "section_pattern": EXPECTED_TEXTBOOK_SECTION_PATTERN,
            "delivery": "reference_in_place",
            "role": "notes_instructional_spine",
        }
        for key, expected in checks.items():
            if textbook.get(key) != expected:
                add(findings, "ERROR", rp, f"physics_textbook.{key} must be {expected!r}; got {textbook.get(key)!r}")


def check_build_registry(root: Path, findings: list):
    rp = Path("pms_build/MANIFEST.json")
    data = load_json(root, rp, findings)
    if not isinstance(data, dict):
        return
    jobs = {j.get("job"): j for j in data.get("jobs", []) if isinstance(j, dict)}
    expected = {
        "notes_map_4a": "pms_build/notes_map/PM.txt",
        "notes_build_4b": "pms_build/notes/PM.txt",
    }
    for job, entrypoint in expected.items():
        row = jobs.get(job)
        if not row:
            add(findings, "ERROR", rp, f"central build registry is missing {job}")
        elif row.get("entrypoint") != entrypoint:
            add(findings, "ERROR", rp, f"{job}.entrypoint must be {entrypoint!r}; got {row.get('entrypoint')!r}")


def require_strings(root: Path, rp: Path, strings: list[str], findings: list):
    p = root / rp
    if not p.exists():
        return
    text = read_text(p) or ""
    low = text.lower()
    for s in strings:
        if s.lower() not in low:
            add(findings, "ERROR", rp, f"missing required contract text: {s!r}")


def check_pm_contracts(root: Path, findings: list):
    require_strings(root, Path("pms_build/notes_map/PM.txt"), [
        "4A · BUILD PHYSICS NOTES MAP PM v1.7",
        "TEXTBOOK-SPINE FAST PATH",
        "Read the current Curriculum Philosophy completely",
        "course_resources.physics_textbook",
        "course_resources.physics_notes_image_toolkit",
        "uN_notes_map.json",
        "uN_notes_map.html",
        "NOTES_MAP_REPORT.txt",
        "NOTES_MAP_HANDOFF.json",
        "physics-notes-map/1.0",
        "physics-notes-map-handoff/1.1",
        "source_bank_fingerprint_method",
        "source_bank_fingerprint",
        "30–40 minute",
    ], findings)

    rp4b = Path("pms_build/notes/PM.txt")
    require_strings(root, rp4b, [
        "4B · BUILD PHYSICS NOTES PM v1.4",
        "TEXTBOOK-SPINE FAST PATH",
        "Read the current Curriculum Philosophy completely",
        "course_resources.physics_textbook",
        "course_resources.physics_notes_image_toolkit",
        "css/base.css",
        "css/notes.css",
        "DO NOT copy the toolkit image",
        "30–40 minute",
    ], findings)
    p = root / rp4b
    if p.exists():
        text = read_text(p) or ""
        if "pms_build/notes/references/css/" in text:
            add(findings, "ERROR", rp4b, "4B still depends on deleted duplicate CSS snapshots; use pinned course css/base.css and css/notes.css")


def check_runtime_contract(root: Path, findings: list):
    rp = Path("SYSTEM_RUNTIME_CONTRACT.txt")
    p = root / rp
    if not p.exists():
        return
    text = read_text(p) or ""
    for s in ["PMs own procedure", "manifests own stable discovery", "Git history owns version history"]:
        if s.lower() not in text.lower():
            add(findings, "ERROR", rp, f"runtime contract missing architecture rule: {s!r}")


def check_control_panel(root: Path, findings: list):
    rp = Path("curriculum_control_panel.html")
    p = root / rp
    if not p.exists():
        return
    text = read_text(p) or ""
    if EXPECTED_TOOLKIT_ROOT in text or "physics_notes_image_toolkit" in text:
        add(findings, "ERROR", rp, "Control Panel should not own Physics toolkit location/dependency logic")
    if EXPECTED_TEXTBOOK_REPO in text or "physics_textbook" in text:
        add(findings, "ERROR", rp, "Control Panel should not own Physics textbook location/dependency logic")
    # Current UI path is display-only, but warn if it still advertises the legacy map path.
    if "notes/unit${unit}_notes_map/unit${unit}_notes_map.json" in text:
        add(findings, "WARN", rp, "4B source display still advertises legacy Notes Map path; PM resolves the current uN path so execution is not blocked")


def find_sibling(root: Path, names: tuple[str, ...]):
    for name in names:
        p = root.parent / name
        if p.is_dir():
            return p
    return None


def audit_map_folder(root: Path, physics: Path, folder: Path, n: int, new_style: bool, findings: list):
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

    if data.get("schema") != EXPECTED_4A_MAP_SCHEMA:
        add(findings, "ERROR", rel(root.parent, map_path), f"map schema must be {EXPECTED_4A_MAP_SCHEMA!r}; got {data.get('schema')!r}")
    for key in ("source_bank_fingerprint_method", "source_bank_fingerprint"):
        if not data.get(key):
            add(findings, "ERROR", rel(root.parent, map_path), f"missing top-level {key}")

    if html_path.exists():
        html = read_text(html_path) or ""
        for marker in ("{esc(", "{{", "<%"):
            if marker in html:
                add(findings, "ERROR", rel(root.parent, html_path), f"unresolved template/code token: {marker!r}")
    else:
        add(findings, "WARN", rel(root.parent, folder), f"missing derived readable map {html_name}")

    if handoff_path.exists():
        try:
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
        except Exception as e:
            add(findings, "WARN", rel(root.parent, handoff_path), f"derived handoff is malformed and should be regenerated: {e}")
        else:
            if handoff.get("schema") != EXPECTED_4A_HANDOFF_SCHEMA:
                add(findings, "WARN", rel(root.parent, handoff_path), f"handoff schema should be {EXPECTED_4A_HANDOFF_SCHEMA!r}")
            if handoff.get("source_bank_fingerprint") != data.get("source_bank_fingerprint"):
                add(findings, "WARN", rel(root.parent, handoff_path), "derived handoff fingerprint does not match map")
    else:
        add(findings, "WARN", rel(root.parent, folder), "derived NOTES_MAP_HANDOFF.json is missing; current 4B may regenerate it from a valid map")

    if new_style and not isinstance(data.get("textbook_source"), dict):
        add(findings, "WARN", rel(root.parent, map_path), "map predates textbook-spine 4A and has no textbook_source; rerun 4A before relying on textbook-spine 4B")


def check_sibling_physics(root: Path, findings: list):
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
            audit_map_folder(root, physics, folder, int(m.group(1)), True, findings)
            continue
        m = re.fullmatch(r"unit(\d+)_notes_map", folder.name)
        if m:
            audit_map_folder(root, physics, folder, int(m.group(1)), False, findings)


def check_sibling_textbooks(root: Path, findings: list):
    textbooks = find_sibling(root, ("textbooks", "Textbooks"))
    if textbooks is None:
        add(findings, "INFO", "../textbooks", "sibling textbooks repo not found; pinned GitHub textbook dependency will be checked at runtime")
        return
    for rp in [Path("physics/index.html"), Path("physics/units")]:
        if not (textbooks / rp).exists():
            add(findings, "ERROR", rel(root.parent, textbooks / rp), "required Physics textbook resource is missing")


def run_checks(root: Path, self_path: Path):
    findings = []
    check_required_files(root, findings)
    check_repo_wide_forbidden(root, self_path, findings)
    check_framework_manifest(root, findings)
    check_build_registry(root, findings)
    check_pm_contracts(root, findings)
    check_runtime_contract(root, findings)
    check_control_panel(root, findings)
    check_sibling_physics(root, findings)
    check_sibling_textbooks(root, findings)
    return findings


def print_report(findings: list):
    rank = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings = sorted(findings, key=lambda x: (rank.get(x[0], 9), x[1], x[2] or 0))
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    print("\nCURRICULUM ARCHITECTURE AUDIT v2 — TEXTBOOK-SPINE")
    print("=" * 80)
    for level, path, line_no, msg in findings:
        counts[level] = counts.get(level, 0) + 1
        where = f"{path}:{line_no}" if line_no else path
        print(f"[{level:5}] {where}")
        print(f"        {msg}")
    if not findings:
        print("PASS — no findings.")
    print("\nSUMMARY")
    print("-" * 80)
    print(f"Errors:   {counts['ERROR']}")
    print(f"Warnings: {counts['WARN']}")
    print(f"Info:     {counts['INFO']}")
    if counts["ERROR"]:
        print("\nRESULT: FAIL — active architecture/output problems remain.")
        return 1
    if counts["WARN"]:
        print("\nRESULT: PASS WITH WARNINGS — active contracts are usable; listed cleanup remains.")
        return 0
    print("\nRESULT: PASS — active architecture checks are clean.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="retained for compatibility; current audit is intentionally read-only")
    args = parser.parse_args()
    if args.fix:
        print("NOTE: --fix is retained for compatibility, but this revision performs no automatic mutations.")
    root = Path.cwd().resolve()
    if not (root / "SYSTEM_MANIFEST.json").exists():
        print("ERROR: Run this script from the root of the memories repository.")
        print(f"Current directory: {root}")
        return 2
    return print_report(run_checks(root, Path(__file__).resolve()))


if __name__ == "__main__":
    sys.exit(main())
