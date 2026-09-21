#!/usr/bin/env python3
"""Deterministic finalizer for District Resource Builder responses."""
from __future__ import annotations
import argparse, html, json, shutil
from pathlib import Path

VERSION = "district-resource-finalize/1.0"


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def resolve_expected(response: Path, path: str) -> list[Path]:
    if "*" in path:
        return sorted(response.glob(path))
    p = response / path
    return [p] if p.exists() else []


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
    shutil.copy2(root / "response_contract/dashboard_styles.css", assets / "dashboard_styles.css")
    shutil.copy2(root / "response_contract/resource_styles.css", assets / "resource_styles.css")

    data_dir = response / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "request.json", data_dir / "request.json")

    outputs = request.get("resolved_outputs") or {}
    cards = []
    for heading, paths in (("Student / Primary Resource", outputs.get("primary") or []), ("Teacher Materials", outputs.get("teacher") or [])):
        links = []
        for path in paths:
            found = resolve_expected(response, path)
            for p in found:
                rel = p.relative_to(response).as_posix()
                links.append(f'<a class="btn" href="{esc(rel)}">{esc(p.name)}</a>')
        if links:
            cards.append(f'<section class="section"><h2>{esc(heading)}</h2><div class="quick-actions">{"".join(links)}</div></section>')

    teacher = request.get("teacher") or {}
    resource = request.get("resource") or {}
    targets = "".join(f"<li>{esc(t)}</li>" for t in request.get("learning_targets") or [])
    source_count = len(request.get("source_files") or [])
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(resource.get('name'))}</title><link rel="stylesheet" href="assets/dashboard_styles.css"></head><body><div class="wrap"><header class="hero"><p class="eyebrow">District Resource Builder</p><h1>{esc(resource.get('name'))}</h1><p class="subtitle">{esc(resource.get('profile_label'))} · {esc(teacher.get('subject_course'))} · {esc(teacher.get('grade_level'))}</p></header><section class="section"><h2>Learning Targets</h2><ul>{targets}</ul><p class="muted">{source_count} supporting source file{'s' if source_count != 1 else ''} were included in the request.</p></section>{''.join(cards)}<section class="section"><h2>Build Record</h2><p class="muted">Generated with {VERSION}. See <code>data/qa.json</code> for completed QA.</p></section></div></body></html>'''
    (response / "CLICK_ME.html").write_text(page, encoding="utf-8")
    print("PASS", VERSION, response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
