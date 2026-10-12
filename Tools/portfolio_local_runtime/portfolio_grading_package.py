#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import tempfile
import zipfile
from pathlib import Path

import build_grading_request as legacy

PACKAGE_SCHEMA = "portfolio-grading-result-package/1.0"
PACKAGE_FILENAME = "Portfolio_Grading_Result_Package.zip"  # Legacy fallback
RESULT_FILENAME = "Portfolio_Grading_Result.json"
RESULT_INBOX = "~/Downloads/Portfolio Grading/Incoming"

_original_build_request = legacy.build_request


def _safe_label(value: str, default: str, max_length: int = 35) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "")).strip("_")
    return value[:max_length].rstrip("_") or default


def _result_filename(request: dict) -> str:
    course = re.sub(r"[^A-Za-z0-9]", "", str(request.get("course") or "")) or "Course"
    unit = int(request.get("unit") or 0)
    source = request.get("source") or {}
    label = _safe_label(source.get("label"), "Evidence")
    # Date of request creation makes the expected filename deterministic.
    created_day = str(request.get("created_at") or "")[:10]
    date = re.sub(r"[^0-9]", "", created_day)
    if len(date) != 8:
        date = "Undated"
    return f"{course}_U{unit}_{label}_Graded_{date}.zip"


def _rewrite_request_contract(path: Path) -> Path:
    path = Path(path)
    with tempfile.TemporaryDirectory(prefix="portfolio_request_contract_") as td:
        tmp = Path(td) / path.name
        with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                name = info.filename.replace("\\", "/")
                data = zin.read(info.filename)
                if name == "REQUEST.json":
                    request = json.loads(data.decode("utf-8"))
                    request["output"] = {
                        "filename": _result_filename(request),
                        "schema": PACKAGE_SCHEMA,
                        "result_json": RESULT_FILENAME,
                        "include_original_evidence": True,
                        "include_next_step_reminder": True,
                        "state_or_reports_from_chatgpt": False,
                        "save_result_to": RESULT_INBOX,
                    }
                    rules = dict(request.get("rules") or {})
                    rules.update({
                        "chatgpt_role": "grade_and_structure_source_level_evidence_only",
                        "local_python_role": "state_update_status_grades_reports_powerschool_email_prep_and_evidence_archival",
                        "google_drive_allowed": False,
                        "do_not_build_reports": True,
                        "do_not_build_portable_state": True,
                        "return_private_grading_package": True,
                        "copy_original_evidence_byte_for_byte": True,
                    })
                    request["rules"] = rules
                    data = (json.dumps(request, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
                zout.writestr(info, data)
        tmp.replace(path)
    return path


def build_request(*args, **kwargs) -> Path:
    return _rewrite_request_contract(_original_build_request(*args, **kwargs))


def main() -> int:
    legacy.build_request = build_request
    return legacy.main()


if __name__ == "__main__":
    raise SystemExit(main())
