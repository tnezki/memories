#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import checkpoint_engine
import summative_engine
import summative_output

MAX_FILES = 250
MAX_UNCOMPRESSED = 60 * 1024 * 1024
ALLOWED_ASSET_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}


def _safe_member(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"Unsafe ZIP member path: {name}")
    return p


def _load_result_bytes(data: bytes, expected_name: str, family_key: str) -> tuple[dict[str, Any], list[tuple[PurePosixPath, bytes]]]:
    if not data:
        raise ValueError("The selected result file is empty.")

    if not zipfile.is_zipfile(io.BytesIO(data)):
        try:
            payload = json.loads(data.decode("utf-8"))
        except Exception as exc:
            raise ValueError("Choose an AI Result ZIP or JSON file.") from exc
        if not isinstance(payload, dict) or family_key not in payload:
            raise ValueError(f"Result JSON must contain {family_key}.")
        return payload, []

    assets: list[tuple[PurePosixPath, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
        infos = [x for x in zf.infolist() if not x.is_dir()]
        if len(infos) > MAX_FILES:
            raise ValueError(f"Result ZIP contains too many files ({len(infos)} > {MAX_FILES}).")
        total = sum(max(0, int(x.file_size)) for x in infos)
        if total > MAX_UNCOMPRESSED:
            raise ValueError("Result ZIP is too large after extraction.")

        safe_infos = [(_safe_member(info.filename), info) for info in infos]
        candidates = [(p, i) for p, i in safe_infos if p.name == expected_name]
        payload = None
        payload_path = None

        scan = candidates or [(p, i) for p, i in safe_infos if p.suffix.lower() == ".json"]
        for p, info in scan:
            try:
                obj = json.loads(zf.read(info).decode("utf-8"))
            except Exception:
                continue
            if isinstance(obj, dict) and family_key in obj:
                payload = obj
                payload_path = p
                break

        if payload is None or payload_path is None:
            raise ValueError(f"Result ZIP must contain {expected_name}.")

        prefix = payload_path.parent
        for p, info in safe_infos:
            if p == payload_path:
                continue
            try:
                rel = p.relative_to(prefix)
            except ValueError:
                rel = p
            if len(rel.parts) >= 2 and rel.parts[0] == "figures" and rel.suffix.lower() in ALLOWED_ASSET_EXTENSIONS:
                assets.append((rel, zf.read(info)))

        return payload, assets


def _atomic_install_dir(target_dir: Path, writer) -> None:
    parent = target_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if target_dir.exists():
        backup = parent / (target_dir.name + ".previous_import")
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        target_dir.rename(backup)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        writer(target_dir)
        if backup and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
    except Exception:
        shutil.rmtree(target_dir, ignore_errors=True)
        if backup and backup.exists():
            backup.rename(target_dir)
        raise


def import_checkpoint_result(github_root: Path, plan_id: str, data: bytes, filename: str = "") -> dict[str, Any]:
    plan_path = github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state" / plan_id / "plan.json"
    if not plan_path.is_file():
        raise ValueError("Checkpoint plan was not found on this Mac.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    payload, _assets = _load_result_bytes(data, "extension_families.json", "extension_families")
    if str(payload.get("plan_id") or "") != plan_id:
        raise ValueError("The selected result belongs to a different Checkpoint plan.")

    validation = checkpoint_engine.validate_extension_response(plan, payload)
    if not validation.get("complete"):
        errors = list(validation.get("errors") or [])
        raise ValueError("Checkpoint result failed validation: " + " ".join(errors[:4]))

    target = checkpoint_engine.extension_response_path(github_root, plan_id)

    def write_result(folder: Path) -> None:
        (folder / "extension_families.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    _atomic_install_dir(target.parent, write_result)
    checkpoint_engine.family_review_path(github_root, plan_id).unlink(missing_ok=True)
    checkpoint_engine.clear_checkpoint_assembly(github_root, plan_id)

    status = checkpoint_engine.checkpoint_status(github_root, plan_id)
    return {
        **status,
        "imported": True,
        "imported_filename": filename,
        "message": f"Imported {len(validation.get('families') or [])} Checkpoint families.",
    }


def import_summative_result(github_root: Path, plan_id: str, data: bytes, filename: str = "") -> dict[str, Any]:
    plan_path = summative_engine.state_dir(github_root, plan_id) / "plan.json"
    if not plan_path.is_file():
        raise ValueError("Summative plan was not found on this Mac.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    payload, assets = _load_result_bytes(data, "summative_families.json", "summative_families")
    if str(payload.get("plan_id") or "") != plan_id:
        raise ValueError("The selected result belongs to a different Summative plan.")

    target = summative_engine.response_path(github_root, plan_id).parent

    def write_result(folder: Path) -> None:
        (folder / "summative_families.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        for rel, content in assets:
            dest = folder / Path(*rel.parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)

        validation = summative_engine.validate_response(plan, payload, github_root)
        if not validation.get("complete"):
            errors = list(validation.get("errors") or [])
            raise ValueError("Summative result failed validation: " + " ".join(errors[:4]))

    _atomic_install_dir(target, write_result)

    summative_engine.review_path(github_root, plan_id).unlink(missing_ok=True)
    out = summative_output.output_dir(github_root, plan_id)
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    summative_output.output_zip_path(github_root, plan_id).unlink(missing_ok=True)

    status = summative_engine.summative_status(github_root, plan_id)
    count = len((status.get("response_validation") or {}).get("families") or [])
    return {
        **status,
        "imported": True,
        "imported_filename": filename,
        "message": f"Imported {count} Summative families.",
    }
