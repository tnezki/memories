#!/usr/bin/env python3
from __future__ import annotations

import portfolio_progress_model as progress

progress.install_runtime()

import apply_grading_result_package

progress.install_loaded_modules()


if __name__ == "__main__":
    raise SystemExit(apply_grading_result_package.main())
