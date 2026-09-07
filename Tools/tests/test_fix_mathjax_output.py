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


def test_plain_html_currency_and_templates_unchanged():
    src = br'''<p>A fee is $5, $12 &lt; $20; ${amount} is source notation.</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.encode() == src


def test_source_spans_and_attributes_unchanged_with_real_math_repair():
    protected = br'''<script>const t = `${amount} < $5`; const r = /\(\rac{.*}\)/; const end = /$/;</script>
<style>.x::after { content: "$5 < $10 \\(\\rac{1}{2}\\)"; }</style>
<!-- \(\rac{1}{2}\) $ -->
<pre>\(\rac{1}{2}\) ${amount} $</pre><code>\[\rac{1}{2}\] $</code>
<textarea>\(\rac{1}{2}\) $</textarea>
<div data-source="\(\rac{1}{2}\) $" onclick="alert(`${x} < $5`)">Text</div>'''
    src = protected + b'<p>\\(\x0crac{1}{2}\\)</p>'
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.startswith(protected.decode())
    assert out.endswith(r'<p>\(\frac{1}{2}\)</p>')


def test_unbalanced_real_html_math_still_fails():
    for src in (br'<p>\(x+1</p>', br'<p>\[x+1</p>'):
        r, out = run(src)
        assert r.returncode == 2, r.stdout + r.stderr
        assert 'unbalanced' in r.stdout
        assert out.encode() == src


def test_unrepairable_corruption_still_fails():
    r, out = run(b'<p>\\(x\x01+1\\)</p>')
    assert r.returncode == 2
    assert 'unexpected control character' in r.stdout


def test_display_only_config_does_not_enable_single_dollar_repair():
    src = br'''<script>window.MathJax={tex:{displayMath:[["$$","$$"]]}};</script>
<p>The fees are $5 &lt; $10.</p><p>$$\rac{1}{2}$$</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert '<p>The fees are $5 &lt; $10.</p>' in out
    assert r'$$\frac{1}{2}$$' in out


def test_legacy_configured_math_corruption_repaired():
    src = br'''<script>window.MathJax={tex:{inlineMath:[["$","$"]]}};</script><p>$\rac{1}{2}$</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r'$\frac{1}{2}$' in out


def test_currency_cannot_hide_real_current_math_corruption():
    src = b'<p>At $5, use \\(\x0crac{1}{2}\\) to compare with $10.</p>'
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r'\frac{1}{2}' in out
    assert '$5' in out and '$10' in out


def test_display_only_config_ignores_lone_currency():
    src = br'''<script>window.MathJax={tex:{displayMath:[["$$","$$"]]}};</script><p>Price $5.</p><p>$$x=1$$</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.encode() == src


def test_unbalanced_legacy_math_still_fails():
    for setting, body in ((b'inlineMath:[["$","$"]]', b'$x+1'),
                          (b'displayMath:[["$$","$$"]]', b'$$x+1')):
        r, out = run(b'<script>window.MathJax={tex:{' + setting + b'}};</script><p>' + body + b'</p>')
        assert r.returncode == 2, r.stdout + r.stderr
        assert 'delimiter count' in r.stdout


def test_config_like_source_cannot_enable_dollar_math():
    src = br'''<script>const example = 'window.MathJax={tex:{inlineMath:[["$","$"]]}}';</script>
<pre>window.MathJax={tex:{inlineMath:[["$","$"]]}};</pre>
<p>The fee is $5 &lt; $12.</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.encode() == src


def test_crlf_source_bytes_preserved_during_real_html_repair():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "notes.html"
        protected = b'<script>\r\nconst price = "$5";\r\n</script>\r\n'
        path.write_bytes(protected + b'<p>\\(\x0crac{1}{2}\\)</p>\r\n')
        result = subprocess.run([sys.executable, str(TOOL), str(path)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert path.read_bytes() == protected + br'<p>\(\frac{1}{2}\)</p>' + b'\r\n'


def test_config_example_is_not_rewritten_when_page_has_real_math():
    src = br'''<script>const example = 'window.MathJax={tex:{inlineMath:[["$","$"]]}}';</script><p>\(x=1\)</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.encode() == src


def test_real_malformed_current_config_is_repaired():
    src = br'''<script>window.MathJax={tex:{inlineMath:[]}};</script><p>\(\rac{1}{2}\)</p>'''
    r, out = run(src)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r'inlineMath:[["\\(","\\)"]]' in out
    assert r'\(\frac{1}{2}\)' in out
