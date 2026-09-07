from __future__ import annotations

import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List

from .authorities import ProjectContext, resolve_bank_sources
from .fs import sha256_file
from .git_snapshot import read_head_sha


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


def _work_order_text(ctx: ProjectContext, job: str, system_sha: str | None, course_sha: str | None) -> str:
    common = f"""CURRICULUM BUILDER PILOT — AI WORK ORDER

COURSE: {ctx.course}
UNIT: {ctx.unit}
JOB: {JOB_LABELS[job]}
LOCAL SYSTEM SNAPSHOT: {system_sha or 'unknown'}
LOCAL COURSE SNAPSHOT: {course_sha or 'unknown'}

SOURCE BOUNDARY — HARD
Use only the files in this AI handoff package plus the current explicit teacher instruction accompanying the handoff. Do not use public web search/fetch, File Library, prior chats, saved memory, old packages, or similarly named substitutes.

GOOD-ENOUGH / STOP RULE — HARD
Do the declared job correctly, align to the accepted authorities, satisfy required QA, and STOP. Do not reopen passed upstream work, polish above the good-enough floor, or search for additional sources for reassurance.

"""
    if job == "bank_map":
        return common + """TASK
Execute Step 3a from the included current Bank Map PM and authorities. Produce the canonical Bank Map design only. Do not author finished Bank questions. Follow the PM's declared build order. Preserve the current Algebra inventory and exact Unit Assessment Plan/operational-map routing. Return only the canonical Step 3a output tree plus concise QA/provenance required by the PM.
"""
    if job == "audit_rebuild_bank_map":
        return common + """TASK
Audit the INCLUDED deployed source_map against the included current Bank Map PM and Audit + Rebuild PM. Begin with actual current shape. Preserve correct map/design bytes. Repair only concrete current-contract defects. Different historical generation pins alone are not defects. If only audit provenance changes, keep generation provenance intact and record the current audit separately. Return the smallest correct changed-file set plus required QA/provenance.
"""
    return common + """TASK
Execute Step 3b from the INCLUDED accepted PASS source_map and current Complete Bank PM. Treat the accepted audited Bank Map as finished design authority. Do not redo Step 3a. Build the expected record table, author every mapped Bank record, generate required representations through declared tools/routes, run batch QA, build viewer/index/reports, run finalization, package the complete canonical Bank, and STOP when the good-enough/current-PM floor passes.
"""


def create_work_order(ctx: ProjectContext, job: str, staging_root: Path) -> Dict[str, object]:
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

    system_sha = read_head_sha(ctx.memories_dir)
    course_sha = read_head_sha(ctx.course_dir)
    work_order = _work_order_text(ctx, job, system_sha, course_sha)
    (run_dir / "AI_WORK_ORDER.txt").write_text(work_order, encoding="utf-8")

    manifest = {
        "schema": "curriculum-builder-pilot-run/0.1",
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
        "ai_boundary": "manual_handoff_v0_1",
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
    }
