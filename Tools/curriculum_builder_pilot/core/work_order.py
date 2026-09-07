from __future__ import annotations

import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Dict, List

from .authorities import ProjectContext, resolve_bank_sources
from .fs import sha256_file
from .git_snapshot import read_head_sha
from .map_audit import audit_bank_map, save_audit_report
from .bank_complete import build_complete_bank_skeleton


JOB_LABELS = {
    "bank_map": "Build Bank Map",
    "audit_rebuild_bank_map": "Audit + Rebuild Bank Map",
    "bank_complete": "Build Complete Bank",
}


def _slug(text: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def _copy_source(src: Path, input_root: Path, github_root: Path) -> Dict[str, object]:
    rel = src.resolve().relative_to(github_root.resolve())
    dst = input_root / rel
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        count = sum(1 for p in dst.rglob("*") if p.is_file())
        return {"source": str(src), "snapshot": str(dst), "kind": "directory", "file_count": count}
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"source": str(src), "snapshot": str(dst), "kind": "file", "sha256": sha256_file(dst)}


def _audit_candidate_ids(local_audit: Dict[str, object] | None) -> List[str]:
    if not isinstance(local_audit, dict):
        return []
    out: List[str] = []
    for finding in local_audit.get("findings", []) if isinstance(local_audit.get("findings"), list) else []:
        if not isinstance(finding, dict):
            continue
        rid = str(finding.get("record_id") or "").strip()
        code = str(finding.get("code") or "")
        if rid and code == "DIRECT_READ_STRUCTURE_MISMATCH":
            out.append(rid)
    return out


def _work_order_text(
    ctx: ProjectContext,
    job: str,
    system_sha: str | None,
    course_sha: str | None,
    run_id: str,
    local_audit: Dict[str, object] | None = None,
) -> str:
    common = f"""CURRICULUM BUILDER PILOT — AI WORK ORDER

RUN ID: {run_id}
COURSE: {ctx.course}
UNIT: {ctx.unit}
JOB: {JOB_LABELS[job]}
LOCAL SYSTEM SNAPSHOT: {system_sha or 'unknown'}
LOCAL COURSE SNAPSHOT: {course_sha or 'unknown'}

SOURCE BOUNDARY — HARD
Use only the files in this AI handoff package plus the current explicit teacher instruction accompanying the handoff. Do not use public web search/fetch, File Library, prior chats, saved memory, old packages, or similarly named substitutes.

QUESTION STRUCTURE AUTHORITY — HARD
The handoff includes the current version manifest, Question Structure Core, and the exact current Universal Question Structure Library resolved from that manifest. Use exact structure definitions/IDs from those included files. Do not invent or guess a structure ID.

GOOD-ENOUGH / STOP RULE — HARD
Do the declared job correctly, align to the accepted authorities, satisfy required QA, and STOP. Do not reopen passed upstream work, polish above the good-enough floor, or search for additional sources for reassurance.

"""
    if job == "bank_map":
        return common + """TASK
Execute only the unresolved semantic authoring/judgment work permitted by the local Bank Map skeleton. Mechanical slot IDs/counts/routing are locked by the local app and may not be changed. Do not author finished Bank questions. Return the semantic result in the exact response format requested by the handoff; do not redesign the mechanical inventory.
"""
    if job == "audit_rebuild_bank_map":
        candidate_ids = _audit_candidate_ids(local_audit)
        ids_text = "\n".join(f"- {rid}" for rid in candidate_ids) or "- NONE"
        return common + f"""LOCAL AUDIT BOUNDARY — HARD
Read LOCAL_MAP_AUDIT.json before reviewing any map record.
The local app has already determined mechanical facts. Those facts outrank AI speculation.
Do NOT claim missing/old filenames, count/hash/schema/fingerprint defects, migration needs, or other mechanical defects unless LOCAL_MAP_AUDIT.json explicitly records them.
Do NOT broaden the audit beyond the semantic candidates listed below.

SEMANTIC CANDIDATE IDS ({len(candidate_ids)})
{ids_text}

TASK
For each candidate ID above, inspect the included deployed map record plus the exact current Question Structure definitions. Decide only whether the current question_structure_id should be KEPT or REPAIRED for semantic fit.
Preserve every non-candidate record.
Do not edit map files in this AI step.

OUTPUT CONTRACT — HARD
Return exactly one file named AI_SEMANTIC_REVIEW.json with this shape:
{{
  "schema": "curriculum-builder-semantic-review/0.2.1",
  "run_id": "{run_id}",
  "course": "{ctx.course}",
  "unit": {ctx.unit},
  "decisions": [
    {{
      "design_slot_id": "candidate ID",
      "decision": "KEEP or REPAIR",
      "current_question_structure_id": "exact current ID",
      "recommended_question_structure_id": "exact included-library ID; same as current when KEEP",
      "reason": "brief evidence-job/student-action/structure-fit reason"
    }}
  ]
}}

Requirements:
- exactly one decision for every candidate ID and no other IDs;
- recommended IDs must exist in the included Universal Question Structure Library;
- do not change evidence_job, student_action, response_mode, representation_mode, IDs, routing, counts, hashes, or files in this AI step;
- if semantic evidence is insufficient, KEEP and explain why rather than inventing a repair;
- stop after producing AI_SEMANTIC_REVIEW.json.
"""
    return common + f"""COMPLETE BANK LOCAL BOUNDARY — HARD
Read LOCKED_BANK_FACTS.json and EXPECTED_BANK_RECORDS.json first.
The local app has already accepted the audited Bank Map, verified its declared hashes, locked every finished-task design_slot_id, locked destination counts/routing, and preserved the approved Seeds.
Do NOT redesign Step 3a, add/drop/rename records, change targets/I Cans/evidence jobs/student actions/Question Structures/response modes/representation routes/security roles, or reopen map audit.

TASK
Author the student-facing content for every record in EXPECTED_BANK_RECORDS.json. Use only the allowed AI output fields. Preserve the exact locked design. Use the included current Question Structure definitions to make each authored task materially execute its mapped structure. Keep secure Summative content independent and do not reuse secure prompts in Practice. WTC parts must share the mapped stimulus and preserve only mapped dependencies.

REPRESENTATION RULE
Do not hand-build final graph assets. For mapped registered-tool graphs, return structured representation_data containing the mathematical data/equation/points, labels, semantic mode, and bounds needed by the local renderer. For tables, return semantic table data. For student-constructed representations, request an answer-neutral response surface. Local code will render/validate final assets later.

OUTPUT CONTRACT — HARD
Return exactly one file named AI_BANK_CONTENT.json with this top-level shape:
{{
  "schema": "curriculum-builder-ai-bank-content/0.5",
  "run_id": "{run_id}",
  "course": "{ctx.course}",
  "unit": {ctx.unit},
  "accepted_map_fingerprint": "COPY EXACTLY FROM LOCKED_BANK_FACTS.json",
  "records": [
    {{
      "design_slot_id": "exact locked ID",
      "prompt_text": "finished student-facing prompt",
      "prompt_blocks": [{{"type": "prose|equation|table|graph|response_surface", "data": {{}}}}],
      "answer_text": "finished answer/key",
      "solution_text": "finished reasoning/solution",
      "choices": [],
      "representation_data": {{}},
      "instantiation_summary": "brief values/context/variation used"
    }}
  ],
  "wtc_stimuli": [
    {{
      "shared_stimulus_id": "exact mapped ID",
      "student_text": "one meaningful shared setup for its four mapped parts",
      "content_blocks": []
    }}
  ]
}}

Requirements:
- exactly one record for every locked design_slot_id and no extras;
- 208 records for the current Unit 1 pilot when LOCKED_BANK_FACTS.json says 208;
- do not author/alter the six locked seed records; they travel locally from source_map;
- selected_response records must include visible, distinct choices and one answer;
- no TODO/TBD/placeholders;
- no internal authoring labels in student prose;
- preserve secure content in this private AI result only;
- stop after producing AI_BANK_CONTENT.json. Do not package a canonical Bank or transfer ZIP in the AI step.
"""


def create_work_order(ctx: ProjectContext, job: str, staging_root: Path) -> Dict[str, object]:
    local_audit: Dict[str, object] | None = None
    if job == "audit_rebuild_bank_map":
        local_audit = audit_bank_map(ctx)
        if local_audit.get("mechanical_shape_status") != "PASS":
            raise ValueError("Local mechanical Bank Map audit must PASS before AI semantic handoff.")
        if not _audit_candidate_ids(local_audit):
            raise ValueError("Local Bank Map audit found no unresolved direct-read semantic candidates; no AI handoff is needed.")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_id = f"{stamp}_{_slug(ctx.course)}_u{ctx.unit}_{job}"
    run_dir = staging_root / "runs" / run_id
    input_root = run_dir / "inputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    input_root.mkdir(parents=True)

    sources = resolve_bank_sources(ctx, job)
    copied: List[Dict[str, object]] = []
    for src in sources:
        if not src.exists():
            raise FileNotFoundError(f"Required source missing: {src}")
        copied.append(_copy_source(src, input_root, ctx.github_root))

    if local_audit is not None:
        save_audit_report(local_audit, run_dir)

    complete_bank_skeleton = None
    if job == "bank_complete":
        complete_bank_skeleton = build_complete_bank_skeleton(ctx, run_dir)

    system_sha = read_head_sha(ctx.memories_dir)
    course_sha = read_head_sha(ctx.course_dir)
    work_order = _work_order_text(ctx, job, system_sha, course_sha, run_id, local_audit)
    (run_dir / "AI_WORK_ORDER.txt").write_text(work_order, encoding="utf-8")

    manifest = {
        "schema": "curriculum-builder-pilot-run/0.5",
        "run_id": run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "job": job,
        "system_head": system_sha,
        "course_head": course_sha,
        "source_policy": "LOCAL_PROJECT_REPOS_ONLY",
        "public_web_allowed": False,
        "file_library_allowed": False,
        "git_commands_allowed": False,
        "inputs": copied,
        "ai_boundary": ("complete_bank_content_only_v0_5" if job == "bank_complete" else "locked_local_facts_plus_semantic_candidates_v0_2_1"),
        "local_audit_included": local_audit is not None,
        "semantic_candidate_ids": _audit_candidate_ids(local_audit),
        "complete_bank_skeleton": complete_bank_skeleton,
    }
    (run_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    handoff = run_dir / "AI_HANDOFF.zip"
    with zipfile.ZipFile(handoff, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in run_dir.rglob("*"):
            if not path.is_file() or path == handoff:
                continue
            zf.write(path, path.relative_to(run_dir))

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "handoff_zip": str(handoff),
        "input_count": len(copied),
        "system_head": system_sha,
        "course_head": course_sha,
        "local_audit_included": local_audit is not None,
        "semantic_candidate_count": len(_audit_candidate_ids(local_audit)),
        "complete_bank_skeleton": complete_bank_skeleton,
    }
