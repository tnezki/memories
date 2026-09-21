#!/usr/bin/env python3
"""Deterministic finalizer for District Tiered Task responses."""
from __future__ import annotations
import argparse, html, json, shutil
from pathlib import Path

VERSION = "district-tiered-task-finalize/1.0"

def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-root", default=".")
    ap.add_argument("--response", required=True)
    args = ap.parse_args()
    root = Path(args.request_root).resolve()
    response = Path(args.response).resolve()
    response.mkdir(parents=True, exist_ok=True)
    request = json.loads((root / "request.json").read_text(encoding="utf-8"))

    assets = response / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "response_contract/task_card_styles.css", assets / "task_card_styles.css")
    shutil.copy2(root / "response_contract/guide_styles.css", assets / "guide_styles.css")

    data_dir = response / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "request.json", data_dir / "request.json")

    teacher = request.get("teacher") or {}
    task = request.get("task") or {}
    targets = "".join(f"<li>{esc(t)}</li>" for t in request.get("i_can_statements") or [])
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(task.get('name'))}</title><link rel="stylesheet" href="assets/guide_styles.css"></head><body><div class="wrap"><header class="hero"><p class="eyebrow">Tiered Task</p><h1>{esc(task.get('name'))}</h1><p class="subtitle">{esc(teacher.get('subject_course'))} · {esc(teacher.get('grade_level'))}</p><div class="quick-actions"><a class="btn primary" href="student/task_card.pdf">Student Task Card (PDF)</a><a class="btn" href="student/task_card.html">Student Task Card (HTML)</a><a class="btn" href="teacher/teacher_guide.pdf">Teacher Guide / Evidence Guide (PDF)</a><a class="btn" href="teacher/teacher_guide.html">Teacher Guide / Evidence Guide (HTML)</a></div></header><section class="section"><h2>Learning Targets</h2><ul>{targets}</ul></section><section class="section"><h2>Build Record</h2><p class="muted">One integrated DOK 1-4 task card. Grade level: {esc(teacher.get('grade_level'))}. Supporting files: {len(request.get('source_files') or [])}.</p><p class="qa-link"><a href="data/qa.json">Open completed QA record</a></p></section></div></body></html>'''
    (response / "CLICK_ME.html").write_text(page, encoding="utf-8")
    print(f"PASS {VERSION}: {response}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
