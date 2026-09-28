#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

import build_grading_request as legacy

PACKAGE_SCHEMA = "portfolio-grading-result-package/1.0"
PACKAGE_FILENAME = "Portfolio_Grading_Result_Package.zip"
RESULT_FILENAME = "Portfolio_Grading_Result.json"

_original_build_request = legacy.build_request


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
                        "filename": PACKAGE_FILENAME,
                        "schema": PACKAGE_SCHEMA,
                        "result_json": RESULT_FILENAME,
                        "include_original_evidence": True,
                        "include_next_step_reminder": True,
                        "state_or_reports_from_chatgpt": False,
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
    # The legacy interactive CLI calls its module-level build_request. Point it
    # at this wrapper so fallback command-line use gets the same package contract
    # as the browser control panel.
    legacy.build_request = build_request
    return legacy.main()


if __name__ == "__main__":
    raise SystemExit(main())
