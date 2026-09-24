#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import subprocess
import tempfile
import threading
import urllib.parse
from pathlib import Path

import portfolio_companion as base
from portfolio_runtime import (
    build_results,
    extract_state,
    github_root_from_runtime,
    install_results_to_local_folders,
    sha256_file,
    validate_state_zip,
)


class Handler(base.Handler):
    """Portfolio companion with an explicit report-only refresh action."""

    server_version = "PortfolioLocalCompanion/1.4"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/refresh-reports":
            q = urllib.parse.parse_qs(parsed.query)
            try:
                course = (q.get("course") or [""])[0]
                unit = int((q.get("unit") or ["1"])[0])
                refresh_current_reports(course, unit)
                self.send_html(self.reports_page(course, unit, refreshed=True))
            except Exception as exc:
                self.send_html(self.error_page(str(exc)), status=400)
            return
        super().do_GET()

    def reports_page(self, course: str, unit: int, refreshed: bool = False) -> str:
        doc = super().reports_page(course, unit)
        title = f"{course} Unit {unit} Reports"
        needle = f"<h1>{html.escape(title)}</h1>"
        q_course = urllib.parse.quote(course)
        refresh_url = f"/refresh-reports?course={q_course}&unit={unit}"
        controls = (
            '<div class="row report-refresh-row">'
            f'<a class="buttonlink" href="{refresh_url}">Refresh Reports from Current State</a>'
            '<span class="muted">Report-only rebuild. Evidence, grades, and state version do not change.</span>'
            '</div>'
        )
        notice = (
            '<div class="notice good"><b>Reports refreshed.</b> Student HTML, teacher HTML, and PowerSchool exports '
            'were rebuilt from the current authoritative local Portfolio state. No evidence, grades, or state version changed.</div>'
            if refreshed else ""
        )
        if needle in doc:
            doc = doc.replace(needle, needle + controls + notice, 1)
        return doc


def refresh_current_reports(course: str, unit: int) -> dict:
    """Force a transactional report-only rebuild from the current installed state."""
    u = base.unit_dir(course, unit)
    state = u / "02 Portfolio Data" / "Portfolio_State_CURRENT.zip"
    manifest = validate_state_zip(state, course, unit)

    with tempfile.TemporaryDirectory(prefix="portfolio_companion_forced_report_refresh_") as td:
        td = Path(td)
        state_work = td / "state_work"
        extract_state(state, state_work)
        state_dir = state_work / "state"

        run_manifest = {}
        run_path = state_dir / "run_manifest.json"
        if run_path.is_file():
            try:
                run_manifest = json.loads(run_path.read_text(encoding="utf-8"))
            except Exception:
                run_manifest = {}

        try:
            report_number = int(run_manifest.get("report_number") or 1)
        except Exception:
            report_number = 1
        report_date = str(
            run_manifest.get("report_date")
            or str(manifest.get("generated_at") or "")[:10]
            or ""
        )
        latest_label = str(run_manifest.get("source_label") or "Current Portfolio State")
        latest_date = str(run_manifest.get("source_date") or report_date)

        results_dir = td / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        results_manifest = build_results(
            github_root=github_root_from_runtime(),
            runtime_dir=Path(base.__file__).resolve().parent,
            state_dir=state_dir,
            state_manifest=manifest,
            input_state_sha=sha256_file(state),
            course=course,
            unit=unit,
            report_number=report_number,
            report_date=report_date,
            latest_label=latest_label,
            latest_date=latest_date,
            class_insights=None,
            out_dir=results_dir,
        )
        install_results_to_local_folders(results_dir, u)

    return {
        "status": "PASS",
        "course": course,
        "unit": unit,
        "state_version": int(manifest.get("state_version", 0)),
        "state_id": manifest.get("state_id"),
        "results_status": results_manifest.get("status"),
        "message": "Reports refreshed from current local state. Evidence, grades, and state version were unchanged.",
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=base.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    server = base.ThreadingHTTPServer((base.HOST, args.port), Handler)
    url = f"http://{base.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print(f"Local URL: {url}")
    print("Teacher observations and grading runs refresh reports automatically.")
    print("View Reports also includes a manual report-only refresh button.")
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
