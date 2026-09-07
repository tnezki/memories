#!/usr/bin/env python3
"""Universal mechanical finalizer for curriculum outputs.

Runs the registered MathJax repair/audit, then performs generic final-byte HTML
checks that are safe for every artifact family. It never changes curriculum
meaning, questions, mappings, difficulty, or assessment evidence.

Usage:
    python3 Tools/finalize_output.py <file-or-folder>

Exit codes:
    0 = PASS
    2 = final-byte QA failure
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

TARGET = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
HERE = Path(__file__).resolve().parent
MATHJAX = HERE / "fix_mathjax_output.py"

PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_][A-Z0-9_ .:\-/]*\}\}")
ID_RE = re.compile(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", re.I)
PROTECTED_RE = re.compile(
    r"<!--.*?-->|<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>"
    r"|<pre\b[^>]*>.*?</pre\s*>|<code\b[^>]*>.*?</code\s*>|<textarea\b[^>]*>.*?</textarea\s*>",
    re.I | re.S,
)
VISIBLE_ESCAPED_WS_RE = re.compile(r"\\[nrt](?=\\|\s|<|$)")


def html_files(target: Path):
    if target.is_file():
        return [target] if target.suffix.lower() == ".html" else []
    return sorted(p for p in target.rglob("*.html") if "__MACOSX" not in p.parts)


def audit_html(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []

    visible = PROTECTED_RE.sub("", text)
    placeholders = PLACEHOLDER_RE.findall(visible)
    if placeholders:
        issues.append(f"unreplaced template placeholder(s): {', '.join(sorted(set(placeholders))[:6])}")

    ids = ID_RE.findall(visible)
    dupes = sorted({x for x in ids if ids.count(x) > 1})
    if dupes:
        issues.append(f"duplicate HTML id(s): {', '.join(dupes[:8])}")

    visible = PROTECTED_RE.sub("", text)
    if VISIBLE_ESCAPED_WS_RE.search(visible):
        issues.append(r"visible escaped whitespace token such as \n/\t/\r remains")

    bad_controls = [ord(ch) for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]
    if bad_controls:
        issues.append("unexpected control character remains")

    return issues


def main():
    if not TARGET.exists():
        print(f"FAIL missing finalization target: {TARGET}")
        return 2

    proc = subprocess.run([sys.executable, str(MATHJAX), str(TARGET)], text=True)
    failed = proc.returncode != 0

    for path in html_files(TARGET):
        issues = audit_html(path)
        if issues:
            failed = True
            print(f"FAIL  {path}")
            for issue in issues:
                print(f"  - {issue}")

    if failed:
        print("FINALIZATION_QA: FAIL")
        return 2

    print("FINALIZATION_QA: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
