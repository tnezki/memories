#!/usr/bin/env python3
"""CC2 extraction contract regression tests. Pure stdlib, offline synthetic fixtures."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import cc2_extract as mod


def page(contents):
    return ('<!doctype html><!-- saved from url=(0043)https://ebooks.cpm.org/test -->'
            '<html><body><div id="contents">' + contents + '</div></body></html>')


def question(pid, text):
    return (f'<div class="contentContainerReference problem" id="{pid}" container-id="source-abc">'
            f'<div class="contentContainerReference-title">{pid}.</div>'
            f'<div class="contentContainerReference-body"><p>{text}</p></div></div>')


class CC2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "cc2"
        self.root.mkdir()
        self.out = Path(self.tmp.name) / "private_cards"
        self.out.mkdir()
        self.qa = {"errors": [], "warnings": []}

    def tearDown(self):
        self.tmp.cleanup()

    def source(self, folder, name, content):
        dst = self.root / folder / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        return dst

    def extract(self, path):
        return mod.extract_page(path, self.root, self.out, set(), {}, self.qa)

    def test_declared_inventory_94_lessons_and_unpublished_checkpoint_four(self):
        self.assertEqual(sum(len(x.split()) for x in mod.LESSONS.values()), 94)
        self.assertEqual(len(mod.EXPECTED_CHECKPOINTS), 9)
        self.assertNotIn("4", mod.EXPECTED_CHECKPOINTS)
        self.assertEqual(mod.source_role(Path("ch05/CPM eBooks - CC Course 2 Lesson 5.4.html")), ("reflection", "5.4"))
        self.assertEqual(mod.source_role(Path("ch01/CPM eBooks - CC Course 2 Teacher Notes 1.closure.html")), ("teacher_closure", "1"))
        self.assertEqual(mod.source_role(Path("pip/1.html")), ("pip", "1"))
        self.assertEqual(mod.source_role(Path("checkpoints/7a.html")), ("checkpoint", "7a"))
        self.assertTrue(mod.PROBLEM_ID_RE.fullmatch("CL 1-142"))
        self.assertTrue(mod.PROBLEM_ID_RE.fullmatch("5-ML"))

    def test_teacher_solution_pairing_with_shared_cl_identifier(self):
        p = self.source("ch01", "CPM eBooks - CC Course 2 Lesson 1.closure.html", page(
            '<h2>Reflection</h2>' + question("CL 1-142", "Find the value.") +
            '<h2>Answers and Support for Closure Problems</h2>' + question("CL 1-142", "Solution: 12") +
            '<p>Support text only in teacher solution section.</p>'))
        cards = self.extract(p)
        q = next(x for x in cards if x["card_type"] == "problem")
        a = next(x for x in cards if x["card_type"] == "solution")
        self.assertEqual(q["visibility"], "student_candidate")
        self.assertEqual(a["visibility"], "teacher_only")
        self.assertTrue(all(c["visibility"] == "teacher_only" for c in cards if "Answers and Support" in c["text"]))
        self.assertEqual(q["paired_teacher_key_card_id"], a["card_id"])
        self.assertEqual(a["paired_student_card_id"], q["card_id"])
        self.assertEqual(q["source_problem_id"], "CL 1-142")
        self.assertNotEqual(q["card_id"], a["card_id"])
        self.assertFalse(any(x.get("warning") == "unusual_problem_id" for x in self.qa["warnings"]))

    def test_pip_original_identifier_and_checkpoint_source_reference(self):
        pip_page = self.source("pip", "1.html", page('<ul><li>PI-01. LONG DISTANCE</li><li>How far?</li></ul>'))
        pips = self.extract(pip_page)
        self.assertEqual(pips[0]["source_problem_id"], "PI-01")
        check_page = self.source("checkpoints", "7a.html", page('<div>Checkpoint 7A Problem 7-50 Simplifying Expressions</div>'))
        cards = self.extract(check_page)
        self.assertEqual(cards[0]["referenced_textbook_problem_id"], "7-50")

    def test_teacher_notes_and_student_cannot_mix(self):
        p = self.source("ch02", "CPM eBooks - CC Course 2 Teacher Notes 2.opening.html", page('<p>Teacher strategy</p>'))
        c = self.extract(p)
        self.assertTrue(c)
        self.assertTrue(all(x["visibility"] == "teacher_only" for x in c))

    def test_checkpoint_answers_kept_teacher_only_and_practice_split(self):
        p = self.source("checkpoints", "7a.html", page(
            '<div>Checkpoint 7A</div><p>Answers to problem 7-50: 42</p>'
            '<p>Here is how to simplify.</p><p>Example 1:</p><p>Model a solution.</p>'
            '<p>Here are some more to try.</p><ol><li>2+2</li><li>3+4</li></ol>'
            '<p>Answers:</p><div><ol><li>4</li><li>7</li></ol></div>'))
        cards = self.extract(p)
        keys = [x for x in cards if x["visibility"] == "teacher_only"]
        exercises = [x for x in cards if x["suggested_instructional_role"] == "checkpoint_practice"]
        self.assertEqual(len(keys), 2)
        self.assertEqual(len(exercises), 2)
        self.assertTrue(all(x["visibility"] == "student_candidate" for x in exercises))
        self.assertEqual([x["source_list_item_number"] for x in exercises], [1, 2])
        self.assertTrue(all(x["source_problem_id"] is None for x in exercises))
        self.assertTrue(all(x["card_type"] == "problem" for x in exercises))
        self.assertTrue(any(x["visibility"] == "student_candidate" and "how to simplify" in x["text"] for x in cards))

    def test_tex_media_and_original_source_metadata_retained(self):
        folder = "CPM eBooks - CC Course 2 Lesson 1.1.1_files"
        assets = self.root / "ch01" / folder
        assets.mkdir(parents=True)
        (assets / "sample.png").write_bytes(b"\x89PNG\r\n\x1a\nprivateexample")
        p = self.source("ch01", "CPM eBooks - CC Course 2 Lesson 1.1.1.html", page(
            question("1-1", '<c3po-media><script type="math/tex">\\frac{1}{2}</script></c3po-media>'
                     + f'<img src="./{folder}/sample.png">')))
        cards = self.extract(p)
        c = next(x for x in cards if x["card_type"] == "problem")
        self.assertIn(r"\frac{1}{2}", c["math_tex"])
        self.assertEqual(c["media"][0]["status"], "copied")
        self.assertEqual(c["media"][0]["sha256"], mod.sha256((assets / "sample.png").read_bytes()))
        self.assertTrue((self.out / c["media"][0]["output_relative"]).is_file())
        self.assertIn("assets/ch01/", c["html"])
        self.assertEqual(c["source_container_id"], "source-abc")
        self.assertEqual(len(c["source_sha256"]), 64)

    def test_missing_asset_warning_and_source_containment(self):
        p = self.source("ch01", "CPM eBooks - CC Course 2 Lesson 1.1.1.html", page(
            question("1-2", '<img src="./bad_files/missing.png"> <img src="../../secret.jpg">')))
        cards = self.extract(p)
        c = next(x for x in cards if x["card_type"] == "problem")
        self.assertEqual([m["status"] for m in c["media"]], ["missing_local_file", "unsafe_outside_source"])
        self.assertIn("missing_media", c["offline_warnings"])
        self.assertIn("unsafe_media_path", c["offline_warnings"])

    def create_all_inventory(self):
        for chapter, lids in mod.LESSONS.items():
            ch = f"ch{chapter:02d}"
            for lid in lids.split():
                self.source(ch, f"CPM eBooks - CC Course 2 Lesson {lid}.html", page(question(f"{chapter}-1", "Question")))
            for typ in ("opening", "closure"):
                self.source(ch, f"CPM eBooks - CC Course 2 Lesson {chapter}.{typ}.html", page("<p>Start or close.</p>"))
                self.source(ch, f"CPM eBooks - CC Course 2 Teacher Notes {chapter}.{typ}.html", page("<p>Private teaching.</p>"))
            (self.root / ch / f"CC2 Ch {chapter} RPs.pdf").write_bytes(b"%PDF-fixture")
            pg = self.root / "parent_guide"
            pg.mkdir(exist_ok=True)
            (pg / f"CC2_PG_Ch{chapter}.pdf").write_bytes(b"%PDF-fixture")
        self.source("ch05", "CPM eBooks - CC Course 2 Lesson 5.4.html", page("<p>Reflection.</p>"))
        for n in range(1, 15):
            self.source("pip", f"{n}.html", page("<p>PI question.</p>"))
        self.source("pip", "PIP.html", page("<p>PIP intro.</p>"))
        for checkpoint in mod.EXPECTED_CHECKPOINTS:
            self.source("checkpoints", checkpoint + ".html", page("<p>Checkpoint.</p>"))
        self.source("checkpoints", "CPM eBooks - CC Course 2 Checkpoints.html", page("<p>Checkpoints intro.</p>"))
        self.source("standards", "standards.html", page("<p>Standards.</p>"))
        (self.root / "standards" / "CC2_standards_alignment.pdf").write_bytes(b"%PDF-fixture")
        self.source("", "CPM eBooks - CC Course 2 Table of Contents.html", page("<p>TOC.</p>"))
        self.source("", "CPM eBooks - CC Course 2 Overview.html", page("<p>Overview.</p>"))
        for p in mod.pages(self.root):
            p.with_name(p.stem + "_files").mkdir(exist_ok=True)

    def test_full_synthetic_inventory_and_end_to_end(self):
        self.create_all_inventory()
        inv = mod.inventory(self.root)
        self.assertEqual(inv["errors"], [])
        self.assertEqual(inv["missing_pip"], [])
        self.assertEqual(inv["missing_checkpoints"], [])
        self.assertEqual(inv["missing_parent_guides"], [])
        with contextlib.redirect_stdout(io.StringIO()):
            rc = mod.run(["--source", str(self.root), "--output", str(self.out / "cards")])
        self.assertEqual(rc, 0)
        report = json.loads((self.out / "cards" / "qa_report.json").read_text())
        self.assertEqual(report["summary"]["numbered_lessons_found"], 94)
        self.assertEqual(report["inventory"]["errors"], [])
        self.assertEqual(report["summary"]["missing_media"], 0)
        self.assertGreater(report["summary"]["cards"], 155)
        self.assertTrue((self.out / "cards" / "PRIVATE_CONTENT_NOTICE.txt").is_file())
        self.assertTrue((self.out / "cards" / "cards.jsonl").is_file())
        # Generated output is guarded. A second run without --replace-output must refuse.
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                mod.run(["--source", str(self.root), "--output", str(self.out / "cards")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
