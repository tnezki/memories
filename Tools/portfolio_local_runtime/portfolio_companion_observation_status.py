#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import threading
import urllib.parse
from collections import defaultdict
from pathlib import Path

import portfolio_companion as core
import portfolio_companion_notes as notes
import portfolio_report_history as report_history
import portfolio_email_message as email_message
import portfolio_support_contacts as support_contacts
import portfolio_grading_package as grading_package

report_history.install_patch()
email_message.install_patch()
core.build_request = grading_package.build_request


STATUS_LABELS = {
    "TRANSFER": "Transfer",
    "MASTERED": "Secure",
    "DEVELOPING": "Developing",
    "NO_EVIDENCE": "No evidence",
}


def _is_teacher_observation(row: dict[str, str]) -> bool:
    task = (row.get("task_id") or "").strip().lower()
    lineage = (row.get("question_lineage") or "").strip().lower()
    label = (row.get("source_label") or row.get("latest_source_label") or "").strip().lower()
    source_type = (row.get("source_type") or "").strip().lower()
    return (
        "teacher_observation" in task
        or "teacher_observation" in lineage
        or "teacher observation" in label
        or "teacher observation" in source_type
        or "teacher walk-around checklist" in label
        or "teacher walk around checklist" in label
        or "teacher walk-around checklist" in source_type
        or "teacher walk around checklist" in source_type
    )


def _observation_status_map(course: str, unit: int) -> dict[str, dict[str, dict[str, object]]]:
    state = core.unit_dir(course, unit) / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    core.validate_state_zip(state, course, unit)

    with tempfile.TemporaryDirectory(prefix="portfolio_observation_status_") as td:
        root = Path(td)
        core.extract_state(state, root)
        state_dir = root / "state"
        _fields, current_rows = core.read_csv(state_dir / "i_can_status_current.csv")
        evidence_path = state_dir / "evidence_ledger.csv"
        evidence_rows = core.read_csv(evidence_path)[1] if evidence_path.is_file() else []

    evidence_opportunities: dict[tuple[str, str], set[str]] = defaultdict(set)
    observation_opportunities: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in evidence_rows:
        student_key = (row.get("student_key") or "").strip()
        i_can_id = (row.get("i_can_id") or "").strip()
        strength = (row.get("strength") or "").strip().upper()
        if not student_key or not i_can_id or strength not in {"CONVINCING", "PARTIAL", "LIMITED", "UNUSABLE"}:
            continue
        opportunity_id = (row.get("opportunity_id") or "").strip()
        if not opportunity_id:
            opportunity_id = (row.get("event_id") or "").strip()
        if not opportunity_id:
            opportunity_id = "|".join(
                [
                    (row.get("source_date") or "").strip(),
                    (row.get("source_label") or "Portfolio Evidence").strip(),
                    strength,
                    (row.get("note") or row.get("concise_note") or "").strip(),
                ]
            )
        pair = (student_key, i_can_id)
        evidence_opportunities[pair].add(opportunity_id)
        if _is_teacher_observation(row):
            observation_opportunities[pair].add(opportunity_id)

    out: dict[str, dict[str, dict[str, object]]] = {}
    for row in current_rows:
        student_key = (row.get("student_key") or "").strip()
        i_can_id = (row.get("i_can_id") or "").strip()
        if not student_key or not i_can_id:
            continue
        code = (row.get("status_code") or "NO_EVIDENCE").strip().upper() or "NO_EVIDENCE"
        label = STATUS_LABELS.get(code)
        if not label:
            label = (row.get("status_label") or code.replace("_", " ").title()).strip()
        pair = (student_key, i_can_id)
        try:
            stored_evidence_count = int((row.get("source_opportunity_count") or "0").strip() or 0)
        except ValueError:
            stored_evidence_count = 0
        evidence_count = max(stored_evidence_count, len(evidence_opportunities.get(pair, set())))
        out.setdefault(student_key, {})[i_can_id] = {
            "status_code": code,
            "status_label": label,
            "next_action": (row.get("student_action_label") or "").strip(),
            "evidence_count": evidence_count,
            "observation_count": len(observation_opportunities.get(pair, set())),
        }
    return out


class Handler(notes.Handler):
    """Portfolio UI with email notes, evidence history, and observation counts."""

    server_version = "PortfolioLocalCompanion/1.9-grading-package"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/runtime-version":
            self.send_json({"status": "PASS", "version": "1.9-grading-package"})
            return
        if parsed.path == "/api/support-contacts":
            try:
                q = urllib.parse.parse_qs(parsed.query)
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                # Validate that the selected Portfolio state exists before showing contacts.
                core.observation_data(course, unit)
                self.send_json(support_contacts.api_payload())
            except Exception as exc:
                self.send_json({"status": "FAIL", "message": str(exc)}, status=400)
            return
        if parsed.path != "/api/observation-data":
            super().do_GET()
            return
        try:
            q = urllib.parse.parse_qs(parsed.query)
            course = (q.get("course") or [""])[0]
            unit = int((q.get("unit") or ["1"])[0])
            data = core.observation_data(course, unit)
            data["student_i_can_status"] = _observation_status_map(course, unit)
            self.send_json(data)
        except Exception as exc:
            self.send_json({"status": "FAIL", "message": str(exc)}, status=400)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/support-contacts":
            super().do_POST()
            return
        try:
            fields, files = core.parse_form(self)
            course = core.one(fields, "course")
            unit = int(core.one(fields, "unit", "1"))
            core.observation_data(course, unit)
            pasted = core.one(fields, "pasted_text", "")
            replace = core.one(fields, "replace", "").strip().lower() in {"1", "true", "yes", "on"}
            result = support_contacts.update_from_sources(files.get("support_file", []), pasted, replace=replace)
            result.update({
                "status": "PASS",
                "message": (
                    f"Saved {result.get('imported_count', 0)} support assignment(s). "
                    f"Contact directory now has {result.get('active_count', 0)} active row(s). "
                    "Email Reports will use the updated support recipients on reload."
                ),
            })
            self.send_json(result)
        except Exception as exc:
            self.send_json({"status": "FAIL", "message": str(exc)}, status=400)



def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=core.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    server = core.ThreadingHTTPServer((core.HOST, args.port), Handler)
    url = f"http://{core.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
    print("Runtime: evidence-history-1.9 + grading package + support contacts")
    print("The helper is local to this Mac and does not expose Portfolio data to the network.")
    print("Press Control-C to stop this foreground instance.\n")
    if not args.no_open:
        threading.Timer(
            0.5,
            lambda: subprocess.run(
                ["/usr/bin/open", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
        ).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPortfolio Local Companion stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
