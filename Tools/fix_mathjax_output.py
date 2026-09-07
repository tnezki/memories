#!/usr/bin/env python3
"""Mechanical MathJax repair + audit for curriculum outputs.

Stable canonical replacement for the old _fix_mathjax_v11.py.

Key rule: preserve the file's existing math delimiter contract. Current Notes use
\\(...\\) and \\[...\\]. Legacy files that already use $...$ / $$...$$ are also
supported, but this tool never converts one delimiter family into another.

Usage:
    python3 Tools/fix_mathjax_output.py <file-or-folder>

Exit codes:
    0 = repair/audit PASS
    2 = one or more audit warnings remain
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TARGET = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
SUPPORTED = {".html", ".txt", ".csv", ".json"}

BYTE_FIXES = [
    (b"\x0crac{", b"\\frac{"),
    (b"\x0corall", b"\\forall"),
    (b"\x08egin{", b"\\begin{"),
    (b"\x09heta", b"\\theta"),
    (b"\x09ext{", b"\\text{"),
    (b"\x09imes", b"\\times"),
    (b"\x0dight", b"\\right"),
    (b"\x0dangle", b"\\rangle"),
    (b"\x07lpha", b"\\alpha"),
    (b"\x07ngle", b"\\angle"),
    (b"\x0bec{", b"\\vec{"),
    (b"\x0bee", b"\\vee"),
    (b"\x0bdots", b"\\vdots"),
    (b"\\rac{", b"\\frac{"),
    (b"\\ight", b"\\right"),
]

KNOWN_TEX_COMMANDS = (
    "frac", "dfrac", "tfrac", "sqrt", "left", "right", "text", "theta",
    "alpha", "beta", "gamma", "delta", "lambda", "mu", "pi", "sigma",
    "times", "cdot", "div", "to", "rightarrow", "leftarrow",
    "leftrightarrow", "infty", "pm", "mp", "le", "ge", "lt", "gt", "ne",
    "neq", "approx", "sim", "equiv", "forall", "exists", "angle", "rangle",
    "langle", "vec", "overline", "underline", "hat", "bar", "sin", "cos",
    "tan", "log", "ln", "exp", "min", "max", "lim", "sum", "prod",
    "begin", "end", "qquad", "quad"
)
DOUBLED_KNOWN_TEX_RE = re.compile(
    r"\\\\(?=(?:" + "|".join(map(re.escape, KNOWN_TEX_COMMANDS)) + r")\b)"
)
MERGED_RELATION_RE = re.compile(
    r"\\(?P<rel>lt|gt|le|ge|ne)(?P<var>[a-pr-zA-PR-Z])"
    r"(?=(?:\^|_|[+\-*/=<>),.;:\]}]|\\|$|\s))"
)
BARE_RAC_RE = re.compile(r"(?<![A-Za-z\\])rac\{")
LEFT_GLYPH_TAIL_RE = re.compile(r"(?:≤|&le;|&#8804;)\s*ft(?=\s*[({\[])")
RIGHT_GLYPH_TAIL_RE = re.compile(r"(?:≥|&ge;|&#8805;)\s*ight(?=\s*[)}\]])")
MULTIROW_ENV_RE = re.compile(
    r"\\begin\{(?:cases|aligned|alignedat|array|matrix|pmatrix|bmatrix|vmatrix|Vmatrix|gathered)\}"
)
CORRUPTED_SYSTEM_ROW_RE = re.compile(
    r"(?<!\\)\\(?P<var>[A-Za-z])(?=\s*(?:[-+*/=]|\\(?:le|ge|lt|gt|ne|neq)\b))"
)

# Four delimiter families. Order matters: display before inline, current before legacy.
MATH_BLOCK_RE = re.compile(
    r"(?P<bracket>\\\[(?P<bracket_body>.*?)\\\])"
    r"|(?P<paren>\\\((?P<paren_body>.*?)\\\))"
    r"|(?P<dollar_display>(?<!\\)\$\$(?P<dollar_display_body>.*?)(?<!\\)\$\$)"
    r"|(?P<dollar_inline>(?<!\\)\$(?!\$)(?P<dollar_inline_body>.*?)(?<!\\)\$(?!\$))",
    re.DOTALL,
)

PROTECTED_HTML_RE = re.compile(
    r"(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>)", re.I | re.S
)


def split_math(match):
    if match.group("bracket") is not None:
        return r"\[", match.group("bracket_body"), r"\]"
    if match.group("paren") is not None:
        return r"\(", match.group("paren_body"), r"\)"
    if match.group("dollar_display") is not None:
        return "$$", match.group("dollar_display_body"), "$$"
    return "$", match.group("dollar_inline_body"), "$"


def repair_math_content(content: str):
    hits = 0

    if MULTIROW_ENV_RE.search(content):
        def row_repl(m):
            nonlocal hits
            hits += 1
            return r"\\ " + m.group("var")
        content = CORRUPTED_SYSTEM_ROW_RE.sub(row_repl, content)

    for pat, repl in [
        (LEFT_GLYPH_TAIL_RE, r"\\left"),
        (RIGHT_GLYPH_TAIL_RE, r"\\right"),
    ]:
        n = len(pat.findall(content))
        if n:
            content = pat.sub(repl, content)
            hits += n

    # High-confidence control-character command tails that survived decoding.
    tail_fixes = [
        (re.compile("\theta"), r"\\theta"),
        (re.compile("\text\\{"), r"\\text{"),
        (re.compile("\times"), r"\\times"),
        (re.compile(r"\to(?=[0-9A-Za-z({\[+\-])"), r"\\to "),
        (re.compile(r"\r?\nightarrow"), r"\\rightarrow"),
        (re.compile(r"\r?\nangle"), r"\\rangle"),
    ]
    for pat, repl in tail_fixes:
        n = len(pat.findall(content))
        if n:
            content = pat.sub(repl, content)
            hits += n

    n = len(DOUBLED_KNOWN_TEX_RE.findall(content))
    if n:
        content = DOUBLED_KNOWN_TEX_RE.sub(lambda _: "\\", content)
        hits += n

    n = len(BARE_RAC_RE.findall(content))
    if n:
        content = BARE_RAC_RE.sub(r"\\frac{", content)
        hits += n

    def rel_repl(m):
        nonlocal hits
        hits += 1
        return "\\" + m.group("rel") + " " + m.group("var")
    content = MERGED_RELATION_RE.sub(rel_repl, content)

    # HTML-safe relations inside math.
    for src, dst in [
        ("&lt;", r"\lt "), ("&#60;", r"\lt "),
        ("&gt;", r"\gt "), ("&#62;", r"\gt "),
    ]:
        n = content.count(src)
        if n:
            content = content.replace(src, dst)
            hits += n
    n = content.count("<")
    if n:
        content = content.replace("<", r"\lt ")
        hits += n
    n = content.count(">")
    if n:
        content = content.replace(">", r"\gt ")
        hits += n

    return content, hits


def repair_math_blocks(text: str, allow_dollar: bool = True):
    total = 0
    def repl(match):
        nonlocal total
        open_delim, body, close_delim = split_math(match)
        if open_delim.startswith("$") and not allow_dollar:
            return match.group(0)
        body, n = repair_math_content(body)
        total += n
        return open_delim + body + close_delim
    return MATH_BLOCK_RE.sub(repl, text), total


def content_without_script_style(text: str) -> str:
    return re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", text, flags=re.I | re.S)


def delimiter_usage(text: str):
    visible = content_without_script_style(text)
    return {
        "paren": bool(re.search(r"\\\(.*?\\\)", visible, re.S)),
        "bracket": bool(re.search(r"\\\[.*?\\\]", visible, re.S)),
        "dollar_inline": bool(re.search(r"(?<!\\)\$(?!\$).*?(?<!\\)\$(?!\$)", visible, re.S)),
        "dollar_display": bool(re.search(r"(?<!\\)\$\$.*?(?<!\\)\$\$", visible, re.S)),
    }


def config_support(text: str):
    # Accept compact or expanded JavaScript formatting.
    return {
        "paren": bool(re.search(r"inlineMath\s*:\s*\[[^\]]*\\\\\([^\]]*\\\\\)", text, re.S)),
        "bracket": bool(re.search(r"displayMath\s*:\s*\[[^\]]*\\\\\[[^\]]*\\\\\]", text, re.S)),
        "dollar_inline": bool(re.search(r"inlineMath\s*:\s*\[[^\]]*['\"]\$['\"]", text, re.S)),
        "dollar_display": bool(re.search(r"displayMath\s*:\s*\[[^\]]*['\"]\$\$['\"]", text, re.S)),
    }


def repair_compact_current_config(text: str):
    """Repair only obviously malformed current Notes config; preserve delimiter family."""
    if "window.MathJax" not in text:
        return text, 0
    usage = delimiter_usage(text)
    support = config_support(text)
    # Current Notes contract: if paren/bracket math exists and config is missing it,
    # normalize the tex object to include those delimiters. Do not add dollar delimiters.
    if (usage["paren"] and not support["paren"]) or (usage["bracket"] and not support["bracket"]):
        pat = re.compile(r"window\.MathJax\s*=\s*\{\s*tex\s*:\s*\{.*?\}\s*\}\s*;?", re.S)
        if pat.search(text):
            repl = 'window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]],processEscapes:true}};'
            return pat.sub(repl, text, count=1), 1
    return text, 0


def audit(path: Path, text: str):
    issues = []
    visible = content_without_script_style(text)

    # Current delimiter balance.
    if visible.count(r"\(") != visible.count(r"\)"):
        issues.append("unbalanced \\( ... \\) delimiters")
    if visible.count(r"\[") != visible.count(r"\]"):
        issues.append("unbalanced \\[ ... \\] delimiters")

    usage = delimiter_usage(text)
    support = config_support(text) if path.suffix.lower() == ".html" else {"dollar_inline": True, "dollar_display": True}

    # Only treat dollar signs as math delimiters when the HTML config actually
    # enables dollar math. Current Notes intentionally do not, so $5 is prose.
    if path.suffix.lower() != ".html" or support.get("dollar_inline") or support.get("dollar_display"):
        dollars = len(re.findall(r"(?<!\\)\$", visible))
        if dollars % 2:
            issues.append("odd unescaped $ delimiter count")

    if path.suffix.lower() == ".html" and "window.MathJax" in text:
        for key, label in [
            ("paren", r"\\(...\\)"),
            ("bracket", r"\\[...\\]"),
            ("dollar_inline", "$...$"),
            ("dollar_display", "$$...$$"),
        ]:
            if key.startswith("dollar_") and not support[key]:
                continue
            if usage[key] and not support[key]:
                issues.append(f"MathJax config does not enable used delimiter {label}")

    # Broken command tails that should never leave final output.
    for desc, pat in [
        ("dropped frac command", re.compile(r"(?<![A-Za-z\\])rac\{")),
        ("corrupted left command", LEFT_GLYPH_TAIL_RE),
        ("corrupted right command", RIGHT_GLYPH_TAIL_RE),
    ]:
        if pat.search(visible):
            issues.append(desc)

    # Control chars other than newline/tab/carriage return.
    bad_controls = [ord(ch) for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]
    if bad_controls:
        issues.append("unexpected control character remains")

    if "mathjax" in text.lower() and ("cdnjs" in text or "unpkg" in text):
        issues.append("noncanonical MathJax CDN")
    config_pos = text.find("window.MathJax")
    cdn_pos = text.find("cdn.jsdelivr.net")
    if config_pos != -1 and cdn_pos != -1 and config_pos > cdn_pos:
        issues.append("MathJax config appears after CDN script")

    return issues


def process(path: Path):
    raw = path.read_bytes()
    changed = False
    repair_count = 0
    for bad, good in BYTE_FIXES:
        n = raw.count(bad)
        if n:
            raw = raw.replace(bad, good)
            changed = True
            repair_count += n

    text = raw.decode("utf-8", errors="replace")

    # JSON: only byte/control-tail repair; do not reinterpret escaped TeX delimiters.
    if path.suffix.lower() != ".json":
        allow_dollar = True
        if path.suffix.lower() == ".html" and "window.MathJax" in text:
            support = config_support(text)
            allow_dollar = support["dollar_inline"] or support["dollar_display"]
        new_text, n = repair_math_blocks(text, allow_dollar=allow_dollar)
        if n:
            text = new_text
            changed = True
            repair_count += n

        if path.suffix.lower() == ".html":
            new_text, n = repair_compact_current_config(text)
            if n:
                text = new_text
                changed = True
                repair_count += n

    if changed:
        path.write_text(text, encoding="utf-8")

    return changed, repair_count, audit(path, text)


def main():
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
    warning_files = 0
    total_repairs = 0
    for path in files:
        changed, repairs, issues = process(path)
        total_repairs += repairs
        if changed:
            changed_files += 1
            print(f"FIXED {path}")
        if issues:
            warning_files += 1
            print(f"FAIL  {path}")
            for issue in issues:
                print(f"  - {issue}")

    print(f"MathJax finalizer: {len(files)} file(s), {changed_files} changed, {total_repairs} repair(s), {warning_files} warning file(s).")
    return 2 if warning_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
