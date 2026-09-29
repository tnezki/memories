#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import threading
import urllib.parse

import portfolio_companion as core
import portfolio_companion_notes as notes
import portfolio_companion_observation_status as base
from portfolio_sender_package import build_sender_package

_original_write_notes = notes.write_notes


def _write_notes_build_package_then_clear_students(course: str, unit: int, weekly_note: str, student_notes: dict[str, str], selected_keys: list[str]) -> None:
    _original_write_notes(course, unit, weekly_note, student_notes, selected_keys)
    build_sender_package(course, unit)
    # Student-specific notes are current-send-only. The package now owns the exact
    # reviewed wording, so clear local student notes while preserving the weekly note.
    _original_write_notes(course, unit, weekly_note, {}, [])


notes.write_notes = _write_notes_build_package_then_clear_students


class Handler(base.Handler):
    server_version = "PortfolioLocalCompanion/2.0-local-sender-package"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/runtime-version":
            self.send_json({"status": "PASS", "version": "2.0-local-sender-package"})
            return
        super().do_GET()


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
    print("Runtime: local-sender-package-2.0")
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
