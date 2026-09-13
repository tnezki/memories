#!/usr/bin/env python3
"""Protect prose currency from MathJax dollar delimiters in rendered HTML.

This is a narrow preflight for pages that explicitly enable $...$ inline math.
It does not touch bracket/parenthesis math, scripts, styles, comments, code/pre,
textarea contents, tag attributes, or arbitrary serialized data. A schema-aware
adapter also protects rendered exemplar strings in family-bank JSON files.

High-confidence currency markers such as ``$2.75 each`` or ``costs $5.`` are
escaped to ``\\$`` so MathJax leaves them as literal currency. Suspicious numeric
dollar spans that cannot be classified safely are reported instead of guessed.

Usage:
    python3 Tools/fix_mathjax_currency_guard.py <file-or-folder>

Exit codes:
    0 = repair/audit PASS
    2 = one or more ambiguous currency/math collisions remain
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TARGET = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
SUPPORTED = {".html", ".json"}
BANK_RENDERED_KEYS = {"student_html", "answer", "solution", "scoring_guidance"}

PROTECTED_HTML_RE = re.compile(
    r"(<!--.*?-->|<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>"
    r"|<pre\b[^>]*>.*?</pre\s*>|<code\b[^>]*>.*?</code\s*>|<textarea\b[^>]*>.*?</textarea\s*>"
    r"|<![^>]*>|</?[A-Za-z][A-Za-z0-9:-]*(?:\s+(?:[^>\"']|\"[^\"]*\"|'[^']*')*)?\s*/?>)",
    re.I | re.S,
)

INLINE_DOLLAR_CONFIG_RE = re.compile(
    r"inlineMath\s*:.*?\[\s*['\"]\$['\"]\s*,\s*['\"]\$['\"]\s*\]",
    re.S,
)

DOLLAR_SPAN_RE = re.compile(
    r"(?<!\\)\$(?!\$)(?P<body>.*?)(?<!\\)\$(?!\$)",
    re.S,
)

AMOUNT_PREFIX_RE = re.compile(
    r"^\s*(?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)"
)

ISOLATED_CURRENCY_RE = re.compile(
    r"(?<!\\)\$(?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)"
)

MATH_SIGNAL_RE = re.compile(r"[=+*/^_{}\\]")
PROSE_WORD_RE = re.compile(r"\b[A-Za-z]{2,}\b")
RANGE_BRIDGES = {"-", "–", "—", ",", ";", "/", "to", "and", "or"}


def configuration_spans(text: str):
    for script in re.finditer(r"<script\b[^>]*>(.*?)</script\s*>", text, re.I | re.S):
        body = script.group(1)
        assignment = re.search(r"(?:^|[;\n])\s*window\.MathJax\s*=\s*\{", body)
        if assignment:
            yield body[assignment.start():]


def dollar_inline_enabled(text: str) -> bool:
    return any(INLINE_DOLLAR_CONFIG_RE.search(span) for span in configuration_spans(text))


def starts_with_digit(text: str) -> bool:
    return bool(re.match(r"\s*\d", text))


def currency_bridge(body: str) -> bool:
    """Return True only for a high-confidence currency-to-currency bridge."""
    amount = AMOUNT_PREFIX_RE.match(body)
    if not amount:
        return False
    bridge = body[amount.end():]
    stripped = bridge.strip().lower()
    if not stripped:
        return False
    if MATH_SIGNAL_RE.search(bridge):
        return False
    if stripped in RANGE_BRIDGES:
        return True
    if PROSE_WORD_RE.search(bridge):
        return True
    return False


def repair_collision_spans(text: str):
    """Escape the two dollar signs when they clearly represent two currencies."""
    hits = 0

    def repl(match):
        nonlocal hits
        after = text[match.end():]
        if starts_with_digit(after) and currency_bridge(match.group("body")):
            hits += 2
            return r"\$" + match.group("body") + r"\$"
        return match.group(0)

    return DOLLAR_SPAN_RE.sub(repl, text), hits


def looks_like_isolated_currency(text: str, match: re.Match) -> bool:
    """Classify an unpaired $number token conservatively from nearby prose."""
    end = match.end()
    if end >= len(text):
        return True
    tail = text[end:end + 100]
    if not tail:
        return True

    first = tail[0]
    if first in ".,;:!?)]":
        return True
    if first in "-–—" and re.match(r"[-–—]\s*\\?\$?\d", tail):
        return True
    if not first.isspace():
        return False

    stripped = tail.lstrip()
    if not stripped:
        return True
    if stripped[0] in "+*/=^_({[\\":
        return False

    word = re.match(r"([A-Za-z]+)", stripped)
    if word:
        token = word.group(1)
        # A single variable after a number is plausibly real math: $2 x + 1...
        if len(token) == 1:
            return False
        return True

    # Ordinary punctuation/closing prose after whitespace is currency-like.
    if stripped[0] in ".,;:!?)]":
        return True
    return False


def repair_outside_valid_math(text: str):
    """Protect valid $...$ spans, then repair isolated high-confidence currency."""
    out = []
    last = 0
    hits = 0
    for match in DOLLAR_SPAN_RE.finditer(text):
        outside = text[last:match.start()]
        outside, n = repair_isolated_currency(outside)
        hits += n
        out.append(outside)
        out.append(match.group(0))
        last = match.end()
    outside = text[last:]
    outside, n = repair_isolated_currency(outside)
    hits += n
    out.append(outside)
    return "".join(out), hits


def repair_isolated_currency(text: str):
    hits = 0

    def repl(match):
        nonlocal hits
        if looks_like_isolated_currency(text, match):
            hits += 1
            return r"\$" + match.group("amount")
        return match.group(0)

    return ISOLATED_CURRENCY_RE.sub(repl, text), hits


def repair_visible_chunk(text: str):
    text, a = repair_collision_spans(text)
    text, b = repair_outside_valid_math(text)
    return text, a + b


def ambiguous_numeric_collisions(text: str):
    issues = []
    for match in DOLLAR_SPAN_RE.finditer(text):
        body = match.group("body")
        if not AMOUNT_PREFIX_RE.match(body):
            continue
        after = text[match.end():]
        if starts_with_digit(after) and not currency_bridge(body):
            sample = ("$" + body + "$" + after[:18]).replace("\n", " ")
            issues.append(f"ambiguous numeric dollar span; review currency vs. math: {sample[:90]}")
    return issues


def process_html(path: Path):
    original = path.read_text(encoding="utf-8", errors="strict")
    if not dollar_inline_enabled(original):
        return False, 0, []

    chunks = PROTECTED_HTML_RE.split(original)
    repairs = 0
    issues = []
    for i in range(0, len(chunks), 2):
        chunks[i], n = repair_visible_chunk(chunks[i])
        repairs += n
        issues.extend(ambiguous_numeric_collisions(chunks[i]))

    text = "".join(chunks)
    changed = text != original
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, repairs, issues


def is_family_bank(data) -> bool:
    return isinstance(data, dict) and str(data.get("schema_version", "")).startswith("family-bank/")


def repair_bank_json_value(value, key=None, trail="root"):
    repairs = 0
    issues = []
    changed = False

    if isinstance(value, dict):
        out = {}
        for child_key, child_value in value.items():
            fixed, did_change, n, child_issues = repair_bank_json_value(
                child_value, child_key, f"{trail}.{child_key}"
            )
            out[child_key] = fixed
            changed = changed or did_change
            repairs += n
            issues.extend(child_issues)
        return out, changed, repairs, issues

    if isinstance(value, list):
        out = []
        for i, child_value in enumerate(value):
            fixed, did_change, n, child_issues = repair_bank_json_value(
                child_value, key, f"{trail}[{i}]"
            )
            out.append(fixed)
            changed = changed or did_change
            repairs += n
            issues.extend(child_issues)
        return out, changed, repairs, issues

    if isinstance(value, str) and key in BANK_RENDERED_KEYS and "$" in value:
        fixed, n = repair_visible_chunk(value)
        local_issues = [f"{trail}: {msg}" for msg in ambiguous_numeric_collisions(fixed)]
        return fixed, fixed != value, n, local_issues

    return value, False, 0, []


def process_json(path: Path):
    original = path.read_text(encoding="utf-8", errors="strict")
    try:
        data = json.loads(original)
    except json.JSONDecodeError:
        return False, 0, []
    if not is_family_bank(data):
        return False, 0, []

    fixed, changed, repairs, issues = repair_bank_json_value(data)
    if changed:
        path.write_text(json.dumps(fixed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed, repairs, issues


def process(path: Path):
    if path.suffix.lower() not in SUPPORTED:
        return False, 0, []
    if path.suffix.lower() == ".html":
        return process_html(path)
    if path.suffix.lower() == ".json":
        return process_json(path)
    return False, 0, []


def main():
    if not TARGET.exists():
        print(f"FAIL missing currency-guard target: {TARGET}")
        return 2
    if TARGET.is_file():
        files = [TARGET] if TARGET.suffix.lower() in SUPPORTED else []
    else:
        files = sorted(
            p for p in TARGET.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED
            and "__MACOSX" not in p.parts and not p.name.startswith("._")
        )

    if not files:
        print(f"No supported files found: {TARGET}")
        return 0

    changed_files = 0
    repair_total = 0
    warning_files = 0
    for path in files:
        changed, repairs, issues = process(path)
        repair_total += repairs
        if changed:
            changed_files += 1
            print(f"CURRENCY FIXED {path}")
        if issues:
            warning_files += 1
            print(f"FAIL  {path}")
            for issue in issues:
                print(f"  - {issue}")

    print(
        f"MathJax currency guard: {len(files)} file(s), {changed_files} changed, "
        f"{repair_total} escaped currency marker(s), {warning_files} warning file(s)."
    )
    return 2 if warning_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
