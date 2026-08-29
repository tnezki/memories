#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("qa_bank_3a_contract", HERE.parent / "qa_bank_3a_contract.py")
qa = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = qa
assert SPEC.loader is not None
SPEC.loader.exec_module(qa)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_route():
    return {"route_type": "direct_render", "representation": "direct_text", "html_contract": "direct"}


def map_record(iid: str, destination: str, response: str = "constructed_response", rep: str = "direct_text", **extra):
    rec = {
        "record_id": iid,
        "record_mode": "exact_content",
        "destination": destination,
        "scope": "1.1",
        "primary_i_can_id": "U1-S1-IC1",
        "primary_i_can": "I can test the validator.",
        "supporting_i_can_ids": [],
        "evidence_job": "Demonstrate the mapped action.",
        "student_action": "Demonstrate the mapped action.",
        "question_structure_id": "TEST-01",
        "response_mode": response,
        "representation_mode": rep,
        "representation_need": "none" if rep == "direct_text" else "required",
        "slot_id": iid,
        "design_slot_id": iid,
        "security_level": "nonsecure_instructional",
        "representation_route": base_route(),
        "render_contract": base_route(),
    }
    rec.update(extra)
    return rec


def authored_from_map(m, text="Do the task."):
    rec = {
        "item_id": m["record_id"],
        "bank_id": m["record_id"],
        "record_mode": m["record_mode"],
        "destination": m["destination"],
        "section": "1.1",
        "scope": "1.1",
        "primary_i_can_id": m["primary_i_can_id"],
        "primary_i_can": m["primary_i_can"],
        "supporting_i_can_ids": m["supporting_i_can_ids"],
        "evidence_job": m["evidence_job"],
        "student_action": m["student_action"],
        "question_structure_id": m["question_structure_id"],
        "response_mode": m["response_mode"],
        "representation_mode": m["representation_mode"],
        "security_level": m["security_level"],
        "student_text": text,
        "student_html": f"<p>{text}</p>",
        "choices": [],
        "correct_choice": "",
        "answer": "A valid answer.",
        "solution_text": "A valid solution.",
        "solution_html": "<p>A valid solution.</p>",
        "tables": [],
        "figures": [],
        "figure_refs": [],
        "representation_refs": [],
        "source_map_record_id": m["record_id"],
        "question_design": {
            "design_slot_id": m["design_slot_id"],
            "question_structure_id": m["question_structure_id"],
            "response_mode": m["response_mode"],
            "representation_mode": m["representation_mode"],
            "representation_route": copy.deepcopy(m["representation_route"]),
            "render_contract": copy.deepcopy(m["render_contract"]),
        },
    }
    return rec


def build_fixture(root: Path) -> None:
    map_dir = root / "banks" / "unit1_bank_map"
    unit_dir = root / "banks" / "unit1"

    wtc = map_record(
        "U1-S1-WTC-01", "WTC", rep="supplied_diagram",
        representation_route={
            "route_type": "canonical_asset",
            "repository": "tnezki/physics",
            "pinned_commit": "abc",
            "canonical_path": "resources/test_asset.png",
            "asset_id": "TEST-ASSET",
        },
        render_contract={"render": "canonical_image_asset", "path": "resources/test_asset.png"},
        parts_plan=[
            {"part": "a", "move": "interpret"},
            {"part": "b", "move": "use_result", "depends_on": "a"},
            {"part": "c", "move": "communicate", "depends_on": "b"},
        ],
    )
    ex = map_record("U1-S1-NOTES-EXAMPLE-P1", "EXAMPLE")
    yti = map_record("U1-S1-NOTES-YTI-P1", "YTI")
    cyu = map_record("U1-S1-CYU-01", "CYU", response="selected_response", choice_count=4)
    warm = map_record(
        "U1-S1-WU1-Q1", "WARM_UP", rep="student_constructed_fbd",
        representation_route={"route_type": "student_constructed", "surface_type": "force_diagram"},
        render_contract={"route_type": "student_constructed", "surface_type": "force_diagram"},
    )
    table = map_record(
        "U1-S1-CYU-02", "CYU", response="selected_response", rep="semantic_data_table", choice_count=4,
        representation_route={"route_type": "semantic_html_table", "html_contract": '<table class="values">'},
        render_contract={"route_type": "semantic_html_table", "html_contract": '<table class="values">'},
    )

    write_json(map_dir / "notes_map.json", {"wtc_records": [wtc], "records": [ex, yti]})
    write_json(map_dir / "cyu_map.json", {"records": [cyu, table]})
    write_json(map_dir / "warmup_map.json", {"records": [warm]})
    write_json(map_dir / "unit1_question_design_map.json", {"schema": "test"})
    write_json(map_dir / "practice_map.json", {"records": []})
    write_json(map_dir / "exit_map.json", {"records": []})
    write_json(map_dir / "summative_map.json", {"records": []})
    (map_dir / "MAP_REPORT.txt").write_text("PASS\n", encoding="utf-8")

    map_files = [
        "unit1_question_design_map.json", "notes_map.json", "practice_map.json", "cyu_map.json",
        "warmup_map.json", "exit_map.json", "summative_map.json", "MAP_REPORT.txt",
    ]
    map_manifest = {
        "schema": "bank-map-manifest/1.0",
        "course": "Physics",
        "unit": 1,
        "status": "PASS",
        "files": [{"path": name, "sha256": sha(map_dir / name)} for name in map_files],
        "map_fingerprint": "fixture-map",
    }
    write_json(map_dir / "MAP_MANIFEST.json", map_manifest)

    asset = root / "resources" / "test_asset.png"
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_bytes(b"fixture")

    aw = authored_from_map(wtc, "Use the shared figure.\n(a) Read it.\n(b) Use part (a).\n(c) State the result.")
    aw["student_html"] = '<p>Use the shared figure.</p><img class="bank-figure" src="../../resources/test_asset.png"><p>(a) Read it.</p><p>(b) Use part (a).</p><p>(c) State the result.</p>'
    aw["figures"] = [{"asset_id": "TEST-ASSET", "file": "resources/test_asset.png"}]
    aw["figure_refs"] = ["resources/test_asset.png"]
    aw["representation_refs"] = [{"type": "canonical_asset", "asset_id": "TEST-ASSET", "path": "resources/test_asset.png"}]
    aw.update({
        "coverage_role": "wtc_frq_practice",
        "coverage_counts_toward_unit_i_can_floor": False,
        "wtc_frq": True,
        "wtc_shared_stimulus": True,
        "wtc_part_count": 3,
        # Intentionally false semantic metadata. Mechanical pass must not judge it.
        "wtc_frq_focus": ["justify a model plan"],
    })

    ae = authored_from_map(ex)
    ae.update({"pair_id": "U1-S1-PAIR-1", "pair_role": "example"})
    ay = authored_from_map(yti)
    ay.update({"pair_id": "U1-S1-PAIR-1", "pair_role": "yti"})

    ac = authored_from_map(cyu, "Choose the correct answer.")
    ac["choices"] = [{"id": x, "text": t} for x, t in zip("ABCD", ["One", "Two", "Three", "Four"])]
    ac["correct_choice"] = "B"
    ac["answer"] = "Two"
    ac["student_html"] = '<p>Choose the correct answer.</p><ol class="choices"><li>One</li><li>Two</li><li>Three</li><li>Four</li></ol>'

    at = authored_from_map(table, "Use the table.")
    at["choices"] = [{"id": x, "text": t} for x, t in zip("ABCD", ["A1", "B1", "C1", "D1"])]
    at["correct_choice"] = "A"
    at["answer"] = "A1"
    at["student_html"] = '<p>Use the table.</p><table class="values"><thead><tr><th>Time (s)</th><th>Distance (m)</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table><ol class="choices"><li>A1</li><li>B1</li><li>C1</li><li>D1</li></ol>'
    at["tables"] = [{"table_id": "t1", "headers": ["Time (s)", "Distance (m)"], "rows": [[1, 2]]}]
    at["representation_refs"] = [{"type": "semantic_html_table", "table_id": "t1"}]

    au = authored_from_map(warm, "Draw the force diagram.")
    au["student_html"] = '<p>Draw the force diagram.</p><div class="response-surface force-diagram-surface"></div>'
    au["representation_refs"] = [{"type": "student_constructed_blank_surface", "surface_type": "force_diagram"}]

    notes_records = [aw, ae, ay]
    cyu_records = [ac, at]
    warm_records = [au]
    write_json(unit_dir / "notes" / "section_1.1.json", {"records": notes_records})
    write_json(unit_dir / "cyu" / "section_1.1.json", {"records": cyu_records})
    write_json(unit_dir / "warmups" / "section_1.1.json", {"records": warm_records})

    index = []
    for path, records in [
        ("notes/section_1.1.json", notes_records),
        ("cyu/section_1.1.json", cyu_records),
        ("warmups/section_1.1.json", warm_records),
    ]:
        for i, rec in enumerate(records):
            index.append({"item_id": rec["item_id"], "path": path, "record_index": i})
    write_json(unit_dir / "ITEM_INDEX.json", {"items": index})
    write_json(unit_dir / "BANK_MANIFEST.json", {
        "schema": "bank-v2-manifest/1.0",
        "course": "Physics",
        "unit": 1,
        "completed": ["3A_instructional_core"],
        "accepted_bank_map": {
            "map_fingerprint": "fixture-map",
            "question_design_map_sha256": sha(map_dir / "unit1_question_design_map.json"),
        },
        "record_counts": {
            "stage_3a_total": 6,
            "wtc": 1,
            "notes_example": 1,
            "notes_yti": 1,
            "cyu": 2,
            "warmups": 1,
        },
    })


class ValidatorTests(unittest.TestCase):
    def fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        build_fixture(root)
        return td, root

    def test_clean_fixture_passes_and_semantic_wtc_claim_does_not_expand_mechanical_pass(self):
        td, root = self.fixture()
        self.addCleanup(td.cleanup)
        report = qa.run(root, 1)
        self.assertEqual(report["status"], "PASS", report["findings"])

    def test_missing_selected_response_choices_fails(self):
        td, root = self.fixture()
        self.addCleanup(td.cleanup)
        path = root / "banks/unit1/cyu/section_1.1.json"
        data = json.loads(path.read_text())
        data["records"][0]["choices"] = []
        write_json(path, data)
        report = qa.run(root, 1)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("SR_CHOICES_MISSING", codes)

    def test_map_field_drift_fails(self):
        td, root = self.fixture()
        self.addCleanup(td.cleanup)
        path = root / "banks/unit1/notes/section_1.1.json"
        data = json.loads(path.read_text())
        data["records"][1]["response_mode"] = "selected_response"
        write_json(path, data)
        report = qa.run(root, 1)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("MAP_FIELD_DRIFT", codes)

    def test_missing_asset_fails(self):
        td, root = self.fixture()
        self.addCleanup(td.cleanup)
        (root / "resources/test_asset.png").unlink()
        report = qa.run(root, 1)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("ASSET_FILE_MISSING", codes)

    def test_missing_constructed_surface_fails(self):
        td, root = self.fixture()
        self.addCleanup(td.cleanup)
        path = root / "banks/unit1/warmups/section_1.1.json"
        data = json.loads(path.read_text())
        data["records"][0]["student_html"] = "<p>Draw it.</p>"
        write_json(path, data)
        report = qa.run(root, 1)
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("CONSTRUCTED_SURFACE_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
