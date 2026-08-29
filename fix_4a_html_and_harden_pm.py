#!/usr/bin/env python3
"""
fix_4a_html_and_harden_pm.py

Run from the ROOT of the memories repo:

    python3 fix_4a_html_and_harden_pm.py

What it changes
---------------
1. ../physics/notes/unit1_notes_map/unit1_notes_map.html
   - replaces unresolved {esc(...)} Processing placeholders using the canonical
     processing_anchor values in unit1_notes_map.json
   - verifies every story beat is repaired
   - verifies no unresolved template token remains

2. pms_build/notes_map/PM.txt
   - bumps 4A PM v1.6 -> v1.7
   - adds a hard rendered-HTML sanity check before PASS
   - changes final A-I check to A-J

3. audit_curriculum_architecture_v2.py, if present
   - updates expected 4A PM version to v1.7
   - adds an unresolved-template check for canonical 4A HTML

It does NOT alter the Notes Map JSON, handoff, report, Bank, Framework,
Philosophy, toolkit, or any curriculum content.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


EXPECTED_HTML_BLOB = "0f164d41b1d4b418312885ec79491c61afa486b5"
EXPECTED_PM_BLOB = "3fd614dbb74d5d9be9c753d51c7c30d7ae72575b"

TOKEN = '{esc(b["processing_anchor"]["type"])}'


def git_blob_sha1(data: bytes) -> str:
    hdr = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(hdr + data).hexdigest()


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError(message)


def patch_html(memories_root: Path) -> tuple[Path, int]:
    physics_root = memories_root.parent / "physics"
    map_dir = physics_root / "notes" / "unit1_notes_map"
    html_path = map_dir / "unit1_notes_map.html"
    json_path = map_dir / "unit1_notes_map.json"

    require(html_path.exists(), f"Missing: {html_path}")
    require(json_path.exists(), f"Missing: {json_path}")

    html_bytes = html_path.read_bytes()
    current_blob = git_blob_sha1(html_bytes)
    require(
        current_blob == EXPECTED_HTML_BLOB,
        "Refusing to patch unexpected HTML revision.\n"
        f"Expected git blob: {EXPECTED_HTML_BLOB}\n"
        f"Actual git blob:   {current_blob}"
    )

    data = json.loads(json_path.read_text(encoding="utf-8"))

    beat_types = {}
    for section in data.get("sections", []):
        for beat in section.get("story_beats", []):
            beat_id = beat.get("beat_id")
            anchor = beat.get("processing_anchor") or {}
            anchor_type = anchor.get("type")
            require(beat_id, "Story beat missing beat_id")
            require(anchor_type, f"{beat_id} missing processing_anchor.type")
            beat_types[beat_id] = anchor_type

    require(len(beat_types) == 25, f"Expected 25 story beats; found {len(beat_types)}")

    label_for = {
        "example_yti_pair": "Example → You Try It",
        "stop_and_discuss": "Stop & Discuss",
    }

    html = html_bytes.decode("utf-8")
    require(TOKEN in html, "Expected unresolved Processing template token was not found.")

    pattern = re.compile(
        r'(<article class="card beat">(?:(?!</article>).)*?'
        r'<code>(?P<beat>U1-S\d-B\d+)</code>'
        r'(?:(?!</article>).)*?'
        r'<p><strong>Processing:</strong> )'
        + re.escape(TOKEN) +
        r'(</p></article>)',
        re.DOTALL
    )

    seen = []

    def repl(match: re.Match) -> str:
        beat_id = match.group("beat")
        require(beat_id in beat_types, f"HTML beat not found in JSON: {beat_id}")
        anchor_type = beat_types[beat_id]
        label = label_for.get(anchor_type, anchor_type.replace("_", " ").title())
        seen.append(beat_id)
        return match.group(1) + label + match.group(3)

    repaired, count = pattern.subn(repl, html)

    require(count == len(beat_types),
            f"Expected to repair {len(beat_types)} Processing labels; repaired {count}")
    require(len(set(seen)) == len(beat_types),
            "Duplicate/missing beat IDs during HTML repair")
    require(TOKEN not in repaired, "Unresolved Processing template token remains")
    require("{esc(" not in repaired, "Unresolved {esc(...)} template code remains")
    require("{{" not in repaired, "Possible unresolved {{...}} template token remains")
    require("<%=" not in repaired and "<%" not in repaired,
            "Possible unresolved <%...%> template token remains")

    html_path.write_text(repaired, encoding="utf-8")

    final = html_path.read_text(encoding="utf-8")
    require("{esc(" not in final, "Post-write unresolved template code remains")
    require(final.count("<strong>Processing:</strong>") == 25,
            "Post-write Processing label count is not 25")

    return html_path, count


def patch_pm(memories_root: Path) -> Path:
    pm_path = memories_root / "pms_build" / "notes_map" / "PM.txt"
    require(pm_path.exists(), f"Missing: {pm_path}")

    pm_bytes = pm_path.read_bytes()
    current_blob = git_blob_sha1(pm_bytes)
    require(
        current_blob == EXPECTED_PM_BLOB,
        "Refusing to patch unexpected 4A PM revision.\n"
        f"Expected git blob: {EXPECTED_PM_BLOB}\n"
        f"Actual git blob:   {current_blob}"
    )

    text = pm_bytes.decode("utf-8")

    require("4A · BUILD PHYSICS NOTES MAP PM v1.6" in text,
            "Expected v1.6 PM title not found.")
    text = text.replace(
        "4A · BUILD PHYSICS NOTES MAP PM v1.6",
        "4A · BUILD PHYSICS NOTES MAP PM v1.7",
        1
    )

    old_block = """I. OUTPUT FILENAMES ARRAY
Must list exactly:
- unitN_notes_map.json
- unitN_notes_map.html
- NOTES_MAP_REPORT.txt
- NOTES_MAP_HANDOFF.json

If ANY item A-I fails:
- DO NOT emit PASS
- repair the artifact
- rerun this complete final output contract check
- only then package/return it
"""

    new_block = """I. OUTPUT FILENAMES ARRAY
Must list exactly:
- unitN_notes_map.json
- unitN_notes_map.html
- NOTES_MAP_REPORT.txt
- NOTES_MAP_HANDOFF.json

J. RENDERED HTML SANITY — HARD
Open/read the final unitN_notes_map.html AS RENDERED OUTPUT, not as a source template.
The final HTML MUST NOT contain unresolved template/code placeholders, including:
- {esc(...)}
- {{...}}
- <%...%>
- literal builder-variable expressions such as b["processing_anchor"] or equivalent
Every visible Processing label and other dynamic field must contain the resolved human-readable value.
Search the final HTML text for unresolved template delimiters/tokens before PASS.
If any unresolved template/code token is present, QA FAILS even when the JSON and handoff are otherwise correct.

If ANY item A-J fails:
- DO NOT emit PASS
- repair the artifact
- rerun this complete final output contract check
- only then package/return it
"""

    require(old_block in text, "Expected final-check block not found in PM.")
    text = text.replace(old_block, new_block, 1)

    marker = """======================================================================
V1.6 COURSE-OWNED IMAGE RESOURCE FIX
======================================================================
"""

    v17 = """======================================================================
V1.7 RENDERED HTML SANITY FIX
======================================================================

v1.7 preserves the v1.6 course-owned image-resource architecture and all prior
4A→4B contracts. It adds a hard rendered-output sanity check: the final
unitN_notes_map.html may not contain unresolved template/code placeholders or
builder-variable expressions. JSON/handoff correctness does not excuse a broken
teacher-readable HTML artifact.

"""

    require(marker in text, "Expected V1.6 history marker not found.")
    text = text.replace(marker, v17 + marker, 1)

    pm_path.write_text(text, encoding="utf-8")

    final = pm_path.read_text(encoding="utf-8")
    require("4A · BUILD PHYSICS NOTES MAP PM v1.7" in final,
            "PM version bump failed")
    require("J. RENDERED HTML SANITY — HARD" in final,
            "Rendered HTML sanity check was not added")
    require("If ANY item A-J fails:" in final,
            "Final A-J fail-closed rule missing")

    return pm_path


def patch_audit_if_present(memories_root: Path) -> Path | None:
    audit_path = memories_root / "audit_curriculum_architecture_v2.py"
    if not audit_path.exists():
        return None

    text = audit_path.read_text(encoding="utf-8")

    text = text.replace(
        '"4A · BUILD PHYSICS NOTES MAP PM v1.6",',
        '"4A · BUILD PHYSICS NOTES MAP PM v1.7",'
    )

    if "unresolved template/code token in 4A HTML" not in text:
        needle = """        map_path = folder / f"unit{n}_notes_map.json"
        handoff_path = folder / "NOTES_MAP_HANDOFF.json"
"""
        addition = """        map_path = folder / f"unit{n}_notes_map.json"
        handoff_path = folder / "NOTES_MAP_HANDOFF.json"
        html_path = folder / f"unit{n}_notes_map.html"

        html_text = read_text(html_path) or ""
        unresolved_markers = ["{esc(", "{{", "<%"]
        for marker in unresolved_markers:
            if marker in html_text:
                add(findings, "ERROR", rel(root.parent, html_path),
                    f"unresolved template/code token in 4A HTML: {marker!r}")
"""

        if needle in text:
            text = text.replace(needle, addition, 1)

    audit_path.write_text(text, encoding="utf-8")
    return audit_path


def main() -> int:
    root = Path.cwd().resolve()

    require((root / "SYSTEM_MANIFEST.json").exists(),
            "Run this script from the ROOT of the memories repository.")
    require((root.parent / "physics").is_dir(),
            "Expected sibling physics repository next to memories.")

    changed = []

    html_path, count = patch_html(root)
    changed.append(html_path)

    pm_path = patch_pm(root)
    changed.append(pm_path)

    audit_path = patch_audit_if_present(root)
    if audit_path:
        changed.append(audit_path)

    print("\nFIX COMPLETE")
    print("=" * 72)
    print(f"HTML Processing labels repaired: {count}")
    print("4A PM bumped: v1.6 -> v1.7")
    print("Rendered-HTML unresolved-template QA: ADDED")
    print("\nChanged files:")
    for p in changed:
        try:
            print(f"- {p.relative_to(root.parent)}")
        except ValueError:
            print(f"- {p}")

    print("\nNO 4A RERUN REQUIRED.")
    print("Sync memories and physics, then verify before 4B.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        raise SystemExit(1)
