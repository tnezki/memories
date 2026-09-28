#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import portfolio_report_history as report_history

report_history.install_patch()

import apply_grading_result
from portfolio_runtime import github_root_from_runtime, portfolio_root

PACKAGE_SCHEMA = "portfolio-grading-result-package/1.0"
RESULT_SCHEMA = "portfolio-grading-result/1.0"
RESULT_FILENAME = "Portfolio_Grading_Result.json"
MANIFEST_FILENAME = "PACKAGE_MANIFEST.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_component(value: str, fallback: str = "evidence") -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return s[:70] or fallback


def validate_zip_members(zf: zipfile.ZipFile) -> None:
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError(f"Unsafe path inside grading package: {info.filename}")


def find_latest_input(downloads: Path | None = None) -> Path | None:
    downloads = downloads or (Path.home() / "Downloads")
    candidates: list[Path] = []
    for pat in [
        "Portfolio_Grading_Result_Package*.zip",
        "portfolio_grading_result_package*.zip",
        "Portfolio_Grading_Result*.json",
        "portfolio_grading_result*.json",
    ]:
        candidates.extend(p for p in downloads.glob(pat) if p.is_file())
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _unique_dir(parent: Path, stem: str) -> Path:
    out = parent / stem
    n = 2
    while out.exists():
        out = parent / f"{stem}_{n}"
        n += 1
    return out


def _source_signature(obj: dict) -> tuple:
    source = obj.get("source", {}) or {}
    files = tuple(sorted(
        (Path(str(x.get("name") or "")).name, str(x.get("sha256") or "").lower())
        for x in (source.get("evidence_files", []) or [])
    ))
    parent = obj.get("parent_state", {}) or {}
    return (
        str(obj.get("course", "")),
        int(obj.get("unit", 0) or 0),
        str(parent.get("sha256", "")).lower(),
        int(parent.get("state_version", -1) or -1),
        str(parent.get("state_id", "")),
        str(source.get("label", "")),
        str(source.get("date", "")),
        files,
    )


def _verify_evidence_files(result: dict, evidence_root: Path) -> list[Path]:
    expected = result.get("source", {}).get("evidence_files", []) or []
    evidence_paths: list[Path] = []
    for row in expected:
        name = Path(str(row.get("name") or "")).name
        expected_sha = str(row.get("sha256") or "").lower()
        if not name or len(expected_sha) != 64:
            raise ValueError("Result JSON contains an invalid evidence filename/hash.")
        p = evidence_root / name
        if not p.is_file():
            raise ValueError(f"Original evidence file is missing: {name}")
        actual = sha256_file(p)
        if actual != expected_sha:
            raise ValueError(f"Original evidence hash mismatch for {name}.")
        evidence_paths.append(p)
    return evidence_paths


def _package_data(package_path: Path, extract_root: Path) -> tuple[dict, dict, list[Path]]:
    with zipfile.ZipFile(package_path, "r") as zf:
        validate_zip_members(zf)
        names = {x.filename.replace("\\", "/") for x in zf.infolist() if not x.is_dir()}
        if RESULT_FILENAME not in names:
            raise ValueError(f"Grading package is missing {RESULT_FILENAME}.")
        if MANIFEST_FILENAME not in names:
            raise ValueError(f"Grading package is missing {MANIFEST_FILENAME}.")
        zf.extractall(extract_root)

    result_path = extract_root / RESULT_FILENAME
    manifest_path = extract_root / MANIFEST_FILENAME
    result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if result.get("schema") != RESULT_SCHEMA:
        raise ValueError(f"Wrong grading-result schema: {result.get('schema')}")
    if manifest.get("schema") != PACKAGE_SCHEMA:
        raise ValueError(f"Wrong grading-package schema: {manifest.get('schema')}")
    for key in ["course", "unit", "run_id"]:
        if str(manifest.get(key, "")) != str(result.get(key, "")):
            raise ValueError(f"Grading package {key} does not match the result JSON.")
    if manifest.get("result_file") != RESULT_FILENAME:
        raise ValueError("Grading package manifest points to the wrong result file.")

    evidence_paths = _verify_evidence_files(result, extract_root / "evidence")
    manifest_by_name = {
        Path(str(row.get("name") or row.get("path") or "")).name: row
        for row in (manifest.get("evidence_files", []) or [])
        if Path(str(row.get("name") or row.get("path") or "")).name
    }
    for p in evidence_paths:
        row = manifest_by_name.get(p.name)
        if not row or str(row.get("sha256") or "").lower() != sha256_file(p):
            raise ValueError(f"Package manifest does not verify original evidence file: {p.name}")
        if str(row.get("path") or "") != f"evidence/{p.name}":
            raise ValueError(f"Package manifest has the wrong evidence path for {p.name}")

    return result, manifest, evidence_paths


def _recover_evidence_from_request(result: dict, downloads: Path, extract_root: Path) -> tuple[Path | None, list[Path]]:
    wanted = _source_signature(result)
    candidates = sorted(
        [p for p in downloads.glob("portfolio_grading_request_*.zip") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for request_zip in candidates:
        try:
            with zipfile.ZipFile(request_zip, "r") as zf:
                validate_zip_members(zf)
                names = {x.filename.replace("\\", "/") for x in zf.infolist() if not x.is_dir()}
                if "REQUEST.json" not in names:
                    continue
                request = json.loads(zf.read("REQUEST.json").decode("utf-8"))
                if _source_signature(request) != wanted:
                    continue
                dest = extract_root / "recovered_request"
                dest.mkdir(parents=True, exist_ok=True)
                for row in result.get("source", {}).get("evidence_files", []) or []:
                    name = Path(str(row.get("name") or "")).name
                    member = f"evidence/{name}"
                    if member not in names:
                        raise ValueError(f"Matching grading request is missing evidence/{name}")
                    (dest / name).write_bytes(zf.read(member))
                evidence_paths = _verify_evidence_files(result, dest)
                return request_zip, evidence_paths
        except (zipfile.BadZipFile, json.JSONDecodeError, ValueError):
            continue
    return None, []


def _stage_evidence(result: dict, evidence_paths: list[Path]) -> tuple[Path, Path]:
    root = portfolio_root(github_root_from_runtime())
    unit_root = root / str(result["course"]) / f"unit {int(result['unit'])}"
    inbox = unit_root / "01 Evidence Inbox"
    applied_root = inbox / "Applied"
    applied_root.mkdir(parents=True, exist_ok=True)

    source = result.get("source", {}) or {}
    date = safe_component(source.get("date") or str(result.get("graded_at") or "")[:10] or "undated", "undated")
    label = safe_component(source.get("label") or "evidence", "evidence")
    run_id = safe_component(result.get("run_id") or "run", "run")
    final_dir = _unique_dir(applied_root, f"{date}_{label}_{run_id}")
    pending_dir = inbox / f".pending_{run_id}"
    if pending_dir.exists():
        shutil.rmtree(pending_dir)
    pending_dir.mkdir(parents=True, exist_ok=False)

    for src in evidence_paths:
        shutil.copy2(src, pending_dir / src.name)

    archive_manifest = {
        "schema": "portfolio-evidence-archive/1.0",
        "course": result.get("course"),
        "unit": result.get("unit"),
        "run_id": result.get("run_id"),
        "source_label": source.get("label", ""),
        "source_date": source.get("date", ""),
        "files": [{"name": p.name, "sha256": sha256_file(pending_dir / p.name)} for p in evidence_paths],
    }
    (pending_dir / "evidence_archive_manifest.json").write_text(json.dumps(archive_manifest, indent=2) + "\n", encoding="utf-8")
    return pending_dir, final_dir


def _finish_evidence_archive(pending_dir: Path, final_dir: Path) -> None:
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    pending_dir.replace(final_dir)


def _archive_package(package_path: Path, result: dict) -> Path:
    root = portfolio_root(github_root_from_runtime())
    unit_root = root / str(result["course"]) / f"unit {int(result['unit'])}"
    package_archive = unit_root / "02 Portfolio Data" / "Applied Grading Results" / "Packages"
    package_archive.mkdir(parents=True, exist_ok=True)
    out = package_archive / package_path.name
    if out.exists():
        stem, suffix = out.stem, out.suffix
        n = 2
        while out.exists():
            out = package_archive / f"{stem}_{n}{suffix}"
            n += 1
    shutil.copy2(package_path, out)
    return out


def apply_package(package_path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="portfolio_grading_package_") as td:
        extract_root = Path(td) / "package"
        extract_root.mkdir(parents=True)
        result, _manifest, evidence_paths = _package_data(package_path, extract_root)
        result_path = extract_root / RESULT_FILENAME
        pending_dir, final_dir = _stage_evidence(result, evidence_paths)
        try:
            applied = apply_grading_result.apply_result_path(result_path, archive_input=True)
            _finish_evidence_archive(pending_dir, final_dir)
            archived_pkg = _archive_package(package_path, result)
        except Exception:
            if pending_dir.exists():
                shutil.rmtree(pending_dir)
            raise

    print()
    unit_root = portfolio_root(github_root_from_runtime()) / str(result["course"]) / f"unit {int(result['unit'])}"
    print("Original evidence archived to:")
    print(f"  {final_dir}")
    print("Grading JSON archived under:")
    print(f"  {unit_root / '02 Portfolio Data' / 'Applied Grading Results'}")
    print("Grading package archived under:")
    print(f"  {archived_pkg}")
    return applied


def apply_legacy_json(result_path: Path, downloads: Path) -> dict:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("schema") != RESULT_SCHEMA:
        raise ValueError(f"Wrong grading-result schema: {result.get('schema')}")

    with tempfile.TemporaryDirectory(prefix="portfolio_legacy_result_") as td:
        request_zip, evidence_paths = _recover_evidence_from_request(result, downloads, Path(td))
        if evidence_paths:
            pending_dir, final_dir = _stage_evidence(result, evidence_paths)
        else:
            pending_dir = final_dir = None
        try:
            applied = apply_grading_result.apply_result_path(result_path, archive_input=True)
            if pending_dir is not None and final_dir is not None:
                _finish_evidence_archive(pending_dir, final_dir)
        except Exception:
            if pending_dir is not None and pending_dir.exists():
                shutil.rmtree(pending_dir)
            raise

    print()
    if final_dir is not None:
        print("Recovered the exact original evidence from the matching grading-request ZIP and archived it to:")
        print(f"  {final_dir}")
        print(f"Matched request: {request_zip.name}")
    else:
        print("Legacy JSON applied, but no matching grading-request ZIP was found in Downloads, so the original evidence could not be archived automatically.")
    print("Grading JSON archived under the Unit's 02 Portfolio Data/Applied Grading Results folder.")
    print("Future grading runs should return Portfolio_Grading_Result_Package.zip so evidence archival is automatic.")
    return applied


def main() -> int:
    downloads = Path.home() / "Downloads"
    path = find_latest_input(downloads)
    if not path:
        print("No Portfolio grading result package or legacy grading-result JSON was found in Downloads.")
        print("Expected one of:")
        print("  Portfolio_Grading_Result_Package.zip")
        print("  Portfolio_Grading_Result.json")
        return 0

    print("Portfolio grading handoff found:")
    print(f"  {path}")
    print()
    if path.suffix.lower() == ".zip":
        apply_package(path)
    else:
        apply_legacy_json(path, downloads)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
