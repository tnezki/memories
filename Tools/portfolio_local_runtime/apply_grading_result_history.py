#!/usr/bin/env python3
from __future__ import annotations

import portfolio_report_history as report_history

report_history.install_patch()

import apply_grading_result


if __name__ == "__main__":
    raise SystemExit(apply_grading_result.main())
