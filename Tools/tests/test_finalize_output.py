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
