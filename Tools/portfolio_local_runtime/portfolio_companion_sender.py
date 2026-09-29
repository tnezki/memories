#!/usr/bin/env python3
from __future__ import annotations

import importlib
import subprocess
import threading
import urllib.parse
from pathlib import Path

import portfolio_progress_model as progress
import portfolio_runtime as runtime_module

# Install the shared progress model before the companion/report modules import
# runtime functions by value.
progress.install_runtime()

import portfolio_companion as core
import portfolio_companion_notes as notes
import portfolio_companion_observation_status as base
import portfolio_sender_package as sender_package

progress.install_loaded_modules()

_original_write_notes = notes.write_notes
_original_prepare_email = core.prepare_email


def _prepare_email_without_early_folder_open(course: str, unit: int, open_folder: bool = True, selected_student_keys: list[str] | None = None):
    # The final package builder owns the reveal action so Finder highlights the
    # exact ZIP rather than merely opening the containing folder too early.
    return _original_prepare_email(course, unit, open_folder=False, selected_student_keys=selected_student_keys)


core.prepare_email = _prepare_email_without_early_folder_open


def _configured_sender_url() -> str:
    path = core.local_root() / "_student_data_tools" / "email_sender_url.txt"
    if not path.is_file():
        return ""
    url = path.read_text(encoding="utf-8").strip()
    return url if url.startswith(("https://", "http://")) else ""


def _reveal_package_and_open_sender(package_path: str) -> None:
    package = Path(package_path)
    if package.is_file():
        subprocess.run(
            ["/usr/bin/open", "-R", str(package)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    sender_url = _configured_sender_url()
    if sender_url:
        subprocess.run(
            ["/usr/bin/open", sender_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _write_notes_build_package_then_clear_students(course: str, unit: int, weekly_note: str, student_notes: dict[str, str], selected_keys: list[str]) -> None:
    _original_write_notes(course, unit, weekly_note, student_notes, selected_keys)
    result = sender_package.build_sender_package(course, unit)
    # Student-specific notes are current-send-only. The package now owns the exact
    # reviewed wording, so clear local student notes while preserving the weekly note.
    _original_write_notes(course, unit, weekly_note, {}, [])
    _reveal_package_and_open_sender(str(result.get("package") or ""))


notes.write_notes = _write_notes_build_package_then_clear_students




def _reload_progress_overlay() -> None:
    """Reload deterministic Portfolio report/grading overlays from disk.

    Curriculum Transfer can replace the shared progress model while this local
    server is already running. Rebuild the canonical runtime module first so the
    freshly reloaded overlay wraps canonical functions rather than wrapping the
    previous overlay again, then repoint the companion's imported build_results
    alias. This removes the need for a manual Student Data Tools restart after a
    progress-model/template-only update.
    """
    global progress
    importlib.reload(runtime_module)
    progress = importlib.reload(progress)
    progress.install_runtime()
    progress.install_loaded_modules()
    core.build_results = runtime_module.build_results


class Handler(base.Handler):
    server_version = "PortfolioLocalCompanion/2.3-hot-reload"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/runtime-version":
            self.send_json({"status": "PASS", "version": "2.3-hot-reload"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in {
            "/api/refresh-reports",
            "/api/prepare-email",
            "/api/add-observation",
            "/api/update-roster",
        }:
            _reload_progress_overlay()
        super().do_POST()


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
    print("Runtime: progress-model-2.3 hot reload + local sender package")
    print("Prepared email data comes only from local _portfolio_data.")
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
