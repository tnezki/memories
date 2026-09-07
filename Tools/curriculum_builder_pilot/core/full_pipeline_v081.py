from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any, Dict

from .authorities import ProjectContext
from . import full_pipeline_v08 as base

FULL_AI_SCHEMA = base.FULL_AI_SCHEMA
PIPELINE_SCHEMA = base.PIPELINE_SCHEMA
PILOT_VERSION = "0.8.1"
PACKAGE_SCHEMA = "curriculum-builder-ai-result-package/1"
PACKAGE_TYPE = "curriculum_builder_ai_result"


def _course_code(course: str) -> str:
    if course.strip().lower() == "algebra 1":
        return "ALG1"
    compact = "".join(ch for ch in course.upper() if ch.isalnum())
    return compact[:12] or "COURSE"


def _course_slug(course: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in course).split())


def ai_result_package_name(ctx: ProjectContext) -> str:
    return f"{_course_code(ctx.course)}_U{ctx.unit}_BANK_AI_RESULT.zip"


def final_transfer_name(ctx: ProjectContext) -> str:
    return f"{_course_code(ctx.course)}_U{ctx.unit}_BANK_TRANSFER.zip"


def _transport_contract(ctx: ProjectContext, run_id: str) -> Dict[str, Any]:
    return {
        "schema": PACKAGE_SCHEMA,
        "package_type": PACKAGE_TYPE,
        "expected_zip_name": ai_result_package_name(ctx),
        "manifest_name": "BUILDER_RESULT_MANIFEST.json",
        "run_id": run_id,
        "course": ctx.course,
        "course_slug": _course_slug(ctx.course),
        "unit": ctx.unit,
        "result_schema": FULL_AI_SCHEMA,
        "result_filename": "AI_FULL_BANK_RESULT.json",
        "result_payload": "payload/AI_FULL_BANK_RESULT.json",
        "manifest_required_fields": [
            "schema",
            "package_type",
            "run_id",
            "course",
            "course_slug",
            "unit",
            "result_schema",
            "result_filename",
            "result_payload",
            "result_sha256",
        ],
        "install_scope": "Curriculum Builder AI Exchange only; never GitHub",
    }


def _transport_instructions(ctx: ProjectContext, run_id: str) -> str:
    contract = _transport_contract(ctx, run_id)
    return f"""

TRANSPORT OUTPUT CONTRACT - HARD
Do NOT return a loose JSON file. Return exactly ONE ZIP named:
  {contract['expected_zip_name']}

ZIP root must be exactly:
  BUILDER_RESULT_MANIFEST.json
  payload/AI_FULL_BANK_RESULT.json

AI_FULL_BANK_RESULT.json must satisfy the full content contract above.
BUILDER_RESULT_MANIFEST.json must be:
{{
  "schema": "{PACKAGE_SCHEMA}",
  "package_type": "{PACKAGE_TYPE}",
  "run_id": "{run_id}",
  "course": "{ctx.course}",
  "course_slug": "{_course_slug(ctx.course)}",
  "unit": {ctx.unit},
  "result_schema": "{FULL_AI_SCHEMA}",
  "result_filename": "AI_FULL_BANK_RESULT.json",
  "result_payload": "payload/AI_FULL_BANK_RESULT.json",
  "result_sha256": "SHA-256 of the exact payload/AI_FULL_BANK_RESULT.json bytes"
}}

The teacher will run Apply Curriculum Transfers.command. That command imports this package into Curriculum Builder's local AI Exchange. It MUST NOT write this intermediate AI result to a GitHub repository.
Stop after returning the one ZIP.
"""


def _rewrite_handoff_zip(handoff: Path, ctx: ProjectContext, run_id: str) -> None:
    temp = handoff.with_suffix(".tmp.zip")
    contract = _transport_contract(ctx, run_id)
    with zipfile.ZipFile(handoff, "r") as src, zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            if info.filename in {"AI_WORK_ORDER.txt", "AI_RESULT_PACKAGE_CONTRACT.json"}:
                continue
            dst.writestr(info, src.read(info.filename))
        original = src.read("AI_WORK_ORDER.txt").decode("utf-8")
        dst.writestr("AI_WORK_ORDER.txt", original.rstrip() + _transport_instructions(ctx, run_id) + "\n")
        dst.writestr("AI_RESULT_PACKAGE_CONTRACT.json", json.dumps(contract, indent=2) + "\n")
    temp.replace(handoff)


def start_full_pipeline(ctx: ProjectContext, staging_root: Path, ai_exchange: Path) -> Dict[str, Any]:
    result = base.start_full_pipeline(ctx, staging_root, ai_exchange)
    if result.get("stage") == "awaiting_full_ai" and result.get("handoff"):
        handoff = Path(str(result["handoff"]))
        run_id = str(result.get("pipeline_id") or "") + "_ai"
        # Prefer the run ID stored by v0.8 when available in the handoff manifest.
        try:
            with zipfile.ZipFile(handoff, "r") as zf:
                manifest = json.loads(zf.read("RUN_MANIFEST.json").decode("utf-8"))
                run_id = str(manifest.get("run_id") or run_id)
        except Exception:
            pass
        _rewrite_handoff_zip(handoff, ctx, run_id)
        result["expected_result"] = ai_result_package_name(ctx)
        result["expected_result_package"] = ai_result_package_name(ctx)
        result["result_transport"] = "Apply Curriculum Transfers.command"
    return result


def _rename_final_transfer(ctx: ProjectContext, staging_root: Path, result: Dict[str, Any]) -> Dict[str, Any]:
    path_text = str(result.get("transfer_zip") or "").strip()
    if not path_text:
        return result
    old = Path(path_text)
    new = old.with_name(final_transfer_name(ctx))
    if old != new and old.is_file():
        if new.exists():
            new.unlink()
        old.replace(new)
        result["transfer_zip"] = str(new)
        try:
            root = base._pipeline_root(staging_root, ctx)
            state_path = root / "PIPELINE_STATE.json"
            if state_path.is_file():
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state["transfer_zip"] = str(new)
                state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass
    return result


def continue_full_pipeline(
    ctx: ProjectContext,
    staging_root: Path,
    ai_exchange: Path,
    downloads: Path,
    transfer_root: Path,
) -> Dict[str, Any]:
    try:
        result = base.continue_full_pipeline(ctx, staging_root, ai_exchange, downloads, transfer_root)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"AI result has not been imported yet. Download {ai_result_package_name(ctx)}, "
            "run Apply Curriculum Transfers.command, then click Continue."
        ) from exc
    if result.get("stage") == "complete":
        result = _rename_final_transfer(ctx, staging_root, result)
    return result
