#!/usr/bin/env python3
"""
audit_curriculum_architecture.py — v2

Run from the root of the memories repo:

    python3 audit_curriculum_architecture.py

To perform the SAFE cleanup:

    python3 audit_curriculum_architecture.py --fix

Safe --fix actions:
- removes obsolete physics_notes_image_toolkit keys from the 4A/4B UI profiles
- deletes redundant 4A/4B helper instruction files that are not runtime authorities

It NEVER rewrites PM.txt, Frameworks, Philosophy, curriculum, Banks, or Physics outputs.
Physics outputs are audited read-only.

Architecture:
- Framework manifest owns resource discovery/location
- PM.txt owns execution procedure
- Control Panel profile owns UI metadata only
- Git history owns version history
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

SKIP_DIRS = {
    ".git", "__pycache__", ".idea", ".vscode", "node_modules",
    ".pytest_cache", ".mypy_cache"
}

# Actual stale references. The audit script itself is excluded from scanning.
FORBIDDEN_STRINGS = {
    "Tools/Physics_Notes_Image_Toolkit": "old memories-owned Physics image toolkit path",
    "tnezki/physics-image-toolkit": "retired separate Physics image toolkit repository",
    '"physics_notes_image_toolkit": true': "duplicate Control Panel profile ownership flag",
}

REQUIRED_MEMORIES_FILES = [
    Path("Curriculum_Philosophy.txt"),
    Path("SYSTEM_MANIFEST.json"),
    Path("SYSTEM_RUNTIME_CONTRACT.txt"),
    Path("frameworks/Physics/FRAMEWORK.txt"),
    Path("frameworks/Physics/MANIFEST.json"),
    Path("pms_build/notes_map/PM.txt"),
    Path("pms_build/notes_map/MANIFEST.json"),
    Path("pms_build/notes_map/CONTROL_PANEL_PROFILE.json"),
    Path("pms_build/notes/PM.txt"),
    Path("pms_build/notes/MANIFEST.json"),
    Path("pms_build/notes/CONTROL_PANEL_PROFILE.json"),
    Path("curriculum_control_panel.html"),
]

REDUNDANT_HELPERS = [
    Path("pms_build/notes_map/README_FIRST.txt"),
    Path("pms_build/notes_map/RUN_PROMPT.txt"),
    Path("pms_build/notes_map/SOURCE_CONTRACT_AUDIT.txt"),
    Path("pms_build/notes/README_FIRST.txt"),
    Path("pms_build/notes/RUN_PROMPT.txt"),
    Path("pms_build/notes/SOURCE_CONTRACT_AUDIT.txt"),
]

EXPECTED_TOOLKIT_ROOT = "resources/Physics_Notes_Image_Toolkit"
EXPECTED_TOOLKIT_CATALOG = "resources/Physics_Notes_Image_Toolkit/IMAGE_CATALOG.json"

EXPECTED_4A_FILES_TEMPLATE = {
    "unit{n}_notes_map.json",
    "unit{n}_notes_map.html",
    "NOTES_MAP_REPORT.txt",
    "NOTES_MAP_HANDOFF.json",
}

EXPECTED_4A_MAP_SCHEMA = "physics-notes-map/1.0"
EXPECTED_4A_HANDOFF_SCHEMA = "physics-notes-map-handoff/1.1"


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {
        "README", "LICENSE", "Makefile"
    }


def iter_text_files(root: Path, self_path: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.resolve() == self_path.resolve():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if is_text_candidate(p):
            yield p


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


def check_framework_manifest(root: Path, findings: list):
    p = root / "frameworks/Physics/MANIFEST.json"
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        add(findings, "ERROR", rel(root, p), f"invalid JSON: {e}")
        return

    resource = data.get("course_resources", {}).get("physics_notes_image_toolkit")
    if not isinstance(resource, dict):
        add(findings, "ERROR", rel(root, p),
            "missing course_resources.physics_notes_image_toolkit")
        return

    checks = {
        "repo_scope": "course",
        "root": EXPECTED_TOOLKIT_ROOT,
        "catalog": EXPECTED_TOOLKIT_CATALOG,
        "delivery": "reference_in_place",
    }
    for key, expected in checks.items():
        if resource.get(key) != expected:
            add(findings, "ERROR", rel(root, p),
                f"physics_notes_image_toolkit.{key} must be {expected!r}; got {resource.get(key)!r}")


def check_tools_manifest(root: Path, findings: list):
    p = root / "Tools/MANIFEST.json"
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        add(findings, "ERROR", rel(root, p), f"invalid JSON: {e}")
        return
    tools = data.get("tools", {})
    if "physics_notes_image_toolkit" in tools:
        add(findings, "ERROR", rel(root, p),
            "Physics Notes Image Toolkit must not be registered as a System Tool")


def check_pm_contracts(root: Path, findings: list):
    p4a = root / "pms_build/notes_map/PM.txt"
    if p4a.exists():
        t = read_text(p4a) or ""
        required = [
            "4A · BUILD PHYSICS NOTES MAP PM v1.6",
            "Read the current Curriculum Philosophy completely",
            "course_resources.physics_notes_image_toolkit",
            "unitN_notes_map.json",
            "unitN_notes_map.html",
            "NOTES_MAP_REPORT.txt",
            "NOTES_MAP_HANDOFF.json",
            "physics-notes-map/1.0",
            "physics-notes-map-handoff/1.1",
            "source_bank_fingerprint_method",
            "source_bank_fingerprint",
        ]
        for s in required:
            if s.lower() not in t.lower():
                add(findings, "ERROR", rel(root, p4a),
                    f"4A PM missing required positive contract text: {s!r}")

        # We intentionally DO NOT flag legacy names when they occur in
        # explicit "do not"/"forbidden" clauses. Those are safeguards.

    p4b = root / "pms_build/notes/PM.txt"
    if p4b.exists():
        t = read_text(p4b) or ""
        required = [
            "4B · BUILD PHYSICS NOTES PM v1.4",
            "Read the current Curriculum Philosophy completely",
            "course_resources.physics_notes_image_toolkit",
            "resources/Physics_Notes_Image_Toolkit",
            "DO NOT copy the toolkit image",
            "reference",
        ]
        for s in required:
            if s.lower() not in t.lower():
                add(findings, "ERROR", rel(root, p4b),
                    f"4B PM missing required positive architecture text: {s!r}")


def check_profiles(root: Path, findings: list):
    for rp in [
        Path("pms_build/notes_map/CONTROL_PANEL_PROFILE.json"),
        Path("pms_build/notes/CONTROL_PANEL_PROFILE.json"),
    ]:
        p = root / rp
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            add(findings, "ERROR", rp, f"invalid JSON: {e}")
            continue

        if "physics_notes_image_toolkit" in data:
            add(findings, "ERROR", rp,
                "UI profile duplicates Framework-manifest resource ownership")

        # Profiles should remain UI metadata only.
        forbidden_profile_keys = {
            "toolkit_path", "toolkit_catalog", "image_toolkit_repo",
            "image_toolkit_commit", "resource_path"
        }
        for key in forbidden_profile_keys:
            if key in data:
                add(findings, "ERROR", rp,
                    f"UI profile contains resource-location metadata: {key}")


def check_helper_surfaces(root: Path, findings: list):
    for rp in REDUNDANT_HELPERS:
        if (root / rp).exists():
            add(findings, "WARN", rp,
                "redundant helper instruction surface exists; PM.txt should be the sole execution procedure")


def check_runtime_contract(root: Path, findings: list):
    p = root / "SYSTEM_RUNTIME_CONTRACT.txt"
    if not p.exists():
        return
    t = read_text(p) or ""
    required = [
        "PMs own procedure",
        "manifests own stable discovery",
        "Git history owns version history",
    ]
    for s in required:
        if s.lower() not in t.lower():
            add(findings, "ERROR", rel(root, p),
                f"runtime contract missing architecture rule: {s!r}")


def check_control_panel(root: Path, findings: list):
    p = root / "curriculum_control_panel.html"
    if not p.exists():
        return
    t = read_text(p) or ""

    # The Control Panel can identify PM paths and course repos, but it should
    # not carry the Physics toolkit's canonical path or old repo.
    if EXPECTED_TOOLKIT_ROOT in t:
        add(findings, "ERROR", rel(root, p),
            "Control Panel hardcodes Physics toolkit path; Framework manifest should own it")

    if "physics-image-toolkit" in t:
        add(findings, "ERROR", rel(root, p),
            "Control Panel references retired separate toolkit repository")

    if "physics_notes_image_toolkit" in t:
        add(findings, "ERROR", rel(root, p),
            "Control Panel contains toolkit-specific dependency logic")

    # Request execution must resolve through manifests.
    required = [
        "SYSTEM_MANIFEST.json first",
        "selected PM determines",
    ]
    for s in required:
        if s.lower() not in t.lower():
            add(findings, "WARN", rel(root, p),
                f"Control Panel request text does not visibly contain expected rule: {s!r}")


def find_sibling_physics(root: Path):
    candidates = [
        root.parent / "physics",
        root.parent / "Physics",
    ]
    for p in candidates:
        if p.is_dir():
            return p
    return None


def check_sibling_physics(root: Path, findings: list):
    physics = find_sibling_physics(root)
    if physics is None:
        add(findings, "INFO", "../physics",
            "sibling Physics repo not found; skipped local course-resource/output audit")
        return

    toolkit = physics / EXPECTED_TOOLKIT_ROOT
    catalog = physics / EXPECTED_TOOLKIT_CATALOG
    if not toolkit.exists():
        add(findings, "ERROR", rel(root.parent, toolkit), "Physics toolkit root is missing")
    if not catalog.exists():
        add(findings, "ERROR", rel(root.parent, catalog), "Physics toolkit catalog is missing")

    # Audit any canonical 4A folders already present.
    notes_root = physics / "notes"
    if not notes_root.exists():
        return

    pat = re.compile(r"unit(\d+)_notes_map$")
    for folder in sorted(notes_root.iterdir()):
        if not folder.is_dir():
            continue
        m = pat.fullmatch(folder.name)
        if not m:
            continue
        n = int(m.group(1))
        expected = {x.format(n=n) for x in EXPECTED_4A_FILES_TEMPLATE}
        actual = {p.name for p in folder.iterdir() if p.is_file()}

        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            msg = "4A folder violates exact file contract"
            if missing:
                msg += f"; missing={missing}"
            if extra:
                msg += f"; extra={extra}"
            add(findings, "ERROR", rel(root.parent, folder), msg)
            continue

        map_path = folder / f"unit{n}_notes_map.json"
        handoff_path = folder / "NOTES_MAP_HANDOFF.json"

        try:
            map_data = json.loads(map_path.read_text(encoding="utf-8"))
        except Exception as e:
            add(findings, "ERROR", rel(root.parent, map_path), f"invalid JSON: {e}")
            continue

        try:
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
        except Exception as e:
            add(findings, "ERROR", rel(root.parent, handoff_path), f"invalid JSON: {e}")
            continue

        if map_data.get("schema") != EXPECTED_4A_MAP_SCHEMA:
            add(findings, "ERROR", rel(root.parent, map_path),
                f"map schema must be {EXPECTED_4A_MAP_SCHEMA!r}; got {map_data.get('schema')!r}")

        if handoff.get("schema") != EXPECTED_4A_HANDOFF_SCHEMA:
            add(findings, "ERROR", rel(root.parent, handoff_path),
                f"handoff schema must be {EXPECTED_4A_HANDOFF_SCHEMA!r}; got {handoff.get('schema')!r}")

        if handoff.get("status") != "PASS" or handoff.get("qa_status") != "PASS":
            add(findings, "ERROR", rel(root.parent, handoff_path),
                "handoff status and qa_status must both be PASS")

        for key in ("source_bank_fingerprint_method", "source_bank_fingerprint"):
            if not map_data.get(key):
                add(findings, "ERROR", rel(root.parent, map_path),
                    f"missing top-level {key}")
            if handoff.get(key) != map_data.get(key):
                add(findings, "ERROR", rel(root.parent, handoff_path),
                    f"{key} does not exactly match map")

        # Current canonical U1 Bank has 20 EX/YTI pairs. Check when U1 exists.
        if n == 1 and handoff.get("ex_yti_pairs_placed") != 20:
            add(findings, "ERROR", rel(root.parent, handoff_path),
                f"Unit 1 handoff must report 20 EX/YTI pairs; got {handoff.get('ex_yti_pairs_placed')!r}")


def apply_safe_fixes(root: Path):
    changed = []

    # Remove obsolete resource-ownership key from UI profiles.
    for rp in [
        Path("pms_build/notes_map/CONTROL_PANEL_PROFILE.json"),
        Path("pms_build/notes/CONTROL_PANEL_PROFILE.json"),
    ]:
        p = root / rp
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "physics_notes_image_toolkit" in data:
            del data["physics_notes_image_toolkit"]
            p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            changed.append(f"updated {rp}")

    # Retire duplicate procedure surfaces. Git keeps history.
    for rp in REDUNDANT_HELPERS:
        p = root / rp
        if p.exists():
            p.unlink()
            changed.append(f"deleted {rp}")

    return changed


def run_checks(root: Path, self_path: Path):
    findings = []
    check_required_files(root, findings)
    check_repo_wide_forbidden(root, self_path, findings)
    check_framework_manifest(root, findings)
    check_tools_manifest(root, findings)
    check_pm_contracts(root, findings)
    check_profiles(root, findings)
    check_helper_surfaces(root, findings)
    check_runtime_contract(root, findings)
    check_control_panel(root, findings)
    check_sibling_physics(root, findings)
    return findings


def print_report(findings: list, changed: list[str]):
    rank = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings = sorted(findings, key=lambda x: (rank.get(x[0], 9), x[1], x[2] or 0))

    print("\nCURRICULUM ARCHITECTURE AUDIT v2")
    print("=" * 80)

    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for level, path, line_no, msg in findings:
        counts[level] = counts.get(level, 0) + 1
        where = f"{path}:{line_no}" if line_no else path
        print(f"[{level:5}] {where}")
        print(f"        {msg}")

    if not findings:
        print("PASS — no findings.")

    print("\nSUMMARY")
    print("-" * 80)
    print(f"Errors:   {counts.get('ERROR', 0)}")
    print(f"Warnings: {counts.get('WARN', 0)}")
    print(f"Info:     {counts.get('INFO', 0)}")

    if changed:
        print("\nSAFE FIXES APPLIED")
        print("-" * 80)
        for item in changed:
            print(f"- {item}")

    print()
    if counts.get("ERROR", 0):
        print("RESULT: FAIL — active architecture/output problems remain.")
        return 1
    if counts.get("WARN", 0):
        print("RESULT: PASS WITH WARNINGS — active contracts are usable, cleanup remains.")
        return 0
    print("RESULT: PASS — active architecture checks are clean.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true",
                        help="apply only the safe cleanup actions documented above")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    self_path = Path(__file__).resolve()

    if not (root / "SYSTEM_MANIFEST.json").exists():
        print("ERROR: Run this script from the root of the memories repository.")
        print(f"Current directory: {root}")
        return 2

    changed = []
    if args.fix:
        changed = apply_safe_fixes(root)

    findings = run_checks(root, self_path)
    return print_report(findings, changed)


if __name__ == "__main__":
    sys.exit(main())
