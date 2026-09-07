#!/usr/bin/env python3
import subprocess, sys, tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "fix_mathjax_output.py"


def run(html):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.html"
        p.write_bytes(html)
        r = subprocess.run([sys.executable, str(TOOL), str(p)], capture_output=True, text=True)
        return r, p.read_text(encoding="utf-8")


def test_current_notes_delimiters_preserved():
    src = b'''<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]],processEscapes:true}};</script>\n<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n<p>\\(x+1=2\\)</p><p>\\[y=3x\\]</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r"\(x+1=2\)" in out
    assert r"\[y=3x\]" in out
    assert "$x+1=2$" not in out


def test_control_character_frac_repaired():
    src = b'''<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]],processEscapes:true}};</script>\n<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n<p>\\(\x0crac{1}{2}\\)</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r"\frac{1}{2}" in out


def test_legacy_dollar_math_stays_dollar():
    src = b'''<script>window.MathJax={tex:{inlineMath:[["$","$"]],displayMath:[["$$","$$"]],processEscapes:true}};</script>\n<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n<p>$x+1=2$</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "$x+1=2$" in out


def test_current_notes_currency_is_not_treated_as_math():
    src = b'''<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]],processEscapes:true}};</script>\n<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n<p>The fee is $5 and the total is $12.</p><p>\\(x+1=2\\)</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "$5" in out and "$12" in out
    assert r"\(x+1=2\)" in out
