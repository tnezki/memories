#!/usr/bin/env python3
import subprocess, sys, tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "finalize_output.py"


def test_placeholder_blocks_pass():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.html"
        p.write_text("<html><body>{{LEARNING_TARGET}}</body></html>", encoding="utf-8")
        r = subprocess.run([sys.executable, str(TOOL), str(p)], capture_output=True, text=True)
        assert r.returncode == 2
        assert "unreplaced template placeholder" in r.stdout


def test_duplicate_id_blocks_pass():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.html"
        p.write_text('<html><body><div id="a"></div><div id="a"></div></body></html>', encoding="utf-8")
        r = subprocess.run([sys.executable, str(TOOL), str(p)], capture_output=True, text=True)
        assert r.returncode == 2
        assert "duplicate HTML id" in r.stdout


def test_source_files_unchanged_and_pass_for_both_tools():
    # Includes literal dollars, templates, regexes, currency and apparent TeX.
    source = br'''const t = `${value} < $5`; const regex = /\(\rac{.*}\)$/;
price = "$12"; pattern = r"\[\rac{1}{2}\]"; echo "$HOME ${value}"
'''
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        paths = [root / name for name in (
            'source.py', 'source.js', 'source.css', 'run.sh', 'run.command',
            'Makefile', 'run.ps1', 'source.ts', 'authority.txt', 'records.json',
            'index.csv', 'guide.md',
        )]
        for path in paths:
            path.write_bytes(source)
        for tool in (TOOL, TOOL.with_name('fix_mathjax_output.py')):
            for target in (root, *paths):
                result = subprocess.run([sys.executable, str(tool), str(target)], capture_output=True, text=True)
                assert result.returncode == 0, result.stdout + result.stderr
                assert all(path.read_bytes() == source for path in paths)


def test_control_panel_source_is_not_math_or_placeholder_output():
    src = br'''<html><script>
const template = `${amount} < $5`; const regex = /\(\rac{.*}\)$/;
const sample = '<p id="same">{{EXAMPLE}}</p><p id="same">$12</p>';
</script><style>.cost::after {content:"$5 < $10";}</style>
<body><p>The cost is $5.</p><pre>\(\rac{1}{2}\) ${value} $</pre></body></html>'''
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'panel.html'
        path.write_bytes(src)
        result = subprocess.run([sys.executable, str(TOOL), str(path)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'FINALIZATION_QA: PASS' in result.stdout
        assert path.read_bytes() == src
