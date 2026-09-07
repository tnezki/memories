#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List

PACKAGE_SCHEMA = "curriculum-builder-ai-result-package/1"
PACKAGE_TYPE = "curriculum_builder_ai_result"
MANIFEST_NAME = "BUILDER_RESULT_MANIFEST.json"


def _safe_zip_member(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts


def _course_slug(course: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in course).split())


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_manifest(zf: zipfile.ZipFile) -> Dict[str, Any] | None:
    names = set(zf.namelist())
    if MANIFEST_NAME not in names:
        return None
    raw = zf.read(MANIFEST_NAME)
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Builder result manifest must be a JSON object")
    return data


def _validate_manifest(manifest: Dict[str, Any]) -> None:
    if manifest.get("schema") != PACKAGE_SCHEMA:
        raise ValueError(f"Unsupported builder-result schema: {manifest.get('schema')!r}")
    if manifest.get("package_type") != PACKAGE_TYPE:
        raise ValueError(f"Unsupported builder-result package_type: {manifest.get('package_type')!r}")
    for key in ("run_id", "course", "result_payload"):
        if not str(manifest.get(key) or "").strip():
            raise ValueError(f"Builder result manifest is missing {key}")
    try:
        unit = int(manifest.get("unit"))
    except Exception as exc:
        raise ValueError("Builder result manifest has invalid unit") from exc
    if unit < 1:
        raise ValueError("Builder result manifest unit must be positive")
    payload = str(manifest.get("result_payload"))
    if not _safe_zip_member(payload):
        raise ValueError("Builder result payload path is unsafe")
    result_name = str(manifest.get("result_filename") or Path(payload).name)
    if Path(result_name).name != result_name or not result_name.endswith(".json"):
        raise ValueError("Builder result filename must be a simple .json filename")


def _validate_result_json(manifest: Dict[str, Any], raw: bytes) -> Dict[str, Any]:
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Builder AI result must be a JSON object")
    if str(data.get("run_id") or "") != str(manifest.get("run_id") or ""):
        raise ValueError("Builder AI result run_id does not match its package manifest")
    if str(data.get("course") or "") != str(manifest.get("course") or ""):
        raise ValueError("Builder AI result course does not match its package manifest")
    if int(data.get("unit", -1)) != int(manifest.get("unit")):
        raise ValueError("Builder AI result unit does not match its package manifest")
    expected_schema = str(manifest.get("result_schema") or "")
    if expected_schema and str(data.get("schema") or "") != expected_schema:
        raise ValueError("Builder AI result schema does not match its package manifest")
    expected_sha = str(manifest.get("result_sha256") or "").strip().lower()
    if expected_sha and _sha256_bytes(raw) != expected_sha:
        raise ValueError("Builder AI result SHA-256 does not match its package manifest")
    return data


def _candidate_dirs(home: Path) -> List[Path]:
    downloads = home / "Downloads"
    return [downloads / "_github_transfers", downloads]


def _candidate_zips(home: Path) -> List[Path]:
    found: Dict[Path, float] = {}
    for folder in _candidate_dirs(home):
        if not folder.is_dir():
            continue
        for path in folder.glob("*.zip"):
            if not path.is_file():
                continue
            try:
                found[path.resolve()] = path.stat().st_mtime
            except Exception:
                continue
    return [p for p, _ in sorted(found.items(), key=lambda kv: kv[1], reverse=True)]


def _archive_package(home: Path, package: Path, run_id: str) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    archive_dir = home / "Documents" / "Curriculum Builder" / "AI Exchange" / "Archive" / "Imported Packages" / stamp
    archive_dir.mkdir(parents=True, exist_ok=True)
    dst = archive_dir / package.name
    if dst.exists():
        dst = archive_dir / f"{package.stem}_{run_id[-12:]}{package.suffix}"
    shutil.move(str(package), str(dst))
    return dst


def import_package(package: Path, home: Path, *, archive: bool = True) -> Dict[str, Any] | None:
    with zipfile.ZipFile(package, "r") as zf:
        manifest = _load_manifest(zf)
        if manifest is None:
            return None
        _validate_manifest(manifest)
        payload = str(manifest["result_payload"])
        if payload not in set(zf.namelist()):
            raise ValueError(f"Builder result payload missing from ZIP: {payload}")
        raw = zf.read(payload)
        result = _validate_result_json(manifest, raw)

    course = str(manifest["course"])
    unit = int(manifest["unit"])
    slug = str(manifest.get("course_slug") or _course_slug(course))
    if slug != _course_slug(course):
        raise ValueError("Builder result course_slug does not match course")
    result_name = str(manifest.get("result_filename") or Path(payload).name)

    current = home / "Documents" / "Curriculum Builder" / "AI Exchange" / "Current" / slug / f"unit{unit}"
    current.mkdir(parents=True, exist_ok=True)
    out = current / result_name
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_bytes(raw)
    tmp.replace(out)

    archived = None
    if archive:
        archived = _archive_package(home, package, str(manifest["run_id"]))

    return {
        "package": str(package),
        "installed": str(out),
        "archived": str(archived) if archived else None,
        "run_id": str(manifest["run_id"]),
        "course": course,
        "unit": unit,
        "result_schema": str(result.get("schema") or ""),
    }


def process_all(home: Path) -> Dict[str, Any]:
    imported: List[Dict[str, Any]] = []
    failures: List[str] = []
    for package in _candidate_zips(home):
        try:
            result = import_package(package, home)
            if result:
                imported.append(result)
        except zipfile.BadZipFile:
            continue
        except Exception as exc:
            failures.append(f"{package.name}: {exc}")
    return {"imported": imported, "failures": failures}


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="builder-result-selftest-") as td:
        home = Path(td)
        inbox = home / "Downloads" / "_github_transfers"
        inbox.mkdir(parents=True)
        result = {
            "schema": "curriculum-builder-ai-full-bank/0.8",
            "run_id": "SELFTEST-RUN",
            "course": "Algebra 1",
            "unit": 1,
            "map_records": [],
            "bank_records": [],
            "wtc_stimuli": [],
        }
        raw = (json.dumps(result, indent=2) + "\n").encode("utf-8")
        manifest = {
            "schema": PACKAGE_SCHEMA,
            "package_type": PACKAGE_TYPE,
            "run_id": "SELFTEST-RUN",
            "course": "Algebra 1",
            "course_slug": "algebra_1",
            "unit": 1,
            "result_schema": result["schema"],
            "result_filename": "AI_FULL_BANK_RESULT.json",
            "result_payload": "payload/AI_FULL_BANK_RESULT.json",
            "result_sha256": _sha256_bytes(raw),
        }
        package = inbox / "SELFTEST_AI_RESULT.zip"
        with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2) + "\n")
            zf.writestr("payload/AI_FULL_BANK_RESULT.json", raw)
        imported = import_package(package, home, archive=False)
        assert imported is not None
        installed = home / "Documents" / "Curriculum Builder" / "AI Exchange" / "Current" / "algebra_1" / "unit1" / "AI_FULL_BANK_RESULT.json"
        assert installed.is_file()
        assert json.loads(installed.read_text(encoding="utf-8"))["run_id"] == "SELFTEST-RUN"
    print("BUILDER_AI_RESULT_IMPORTER_SELF_TEST: PASS")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import Curriculum Builder AI-result ZIPs without writing to GitHub.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.self_test:
        self_test()
        return 0

    home = Path.home()
    report = process_all(home)
    imported = report["imported"]
    failures = report["failures"]
    if imported:
        for item in imported:
            print(f"BUILDER AI RESULT IMPORTED: {item['course']} Unit {item['unit']}")
            print(f"  -> {item['installed']}")
    else:
        print("No Curriculum Builder AI-result ZIPs found.")
    if failures:
        print("Builder AI-result import failures:")
        for failure in failures:
            print(f"  - {failure}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
