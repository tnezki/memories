#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path


def _read(name: str) -> str:
    path = Path(__file__).resolve().parent / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def inline_assets() -> str:
    css = _read("print_layout_controller.css")
    js = _read("print_layout_controller.js").replace("</script", "<\\/script")
    return f"<style>{css}</style><script>{js}</script>"
