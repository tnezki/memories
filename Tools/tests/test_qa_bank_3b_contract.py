#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "qa_bank_3b_contract.py"


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def fixture(root: Path):
    bank = root / "banks/unit1"
    mroot = root / "banks/unit1_bank_map"
    asset = root / "resources/img.png"
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_bytes(b"x")

    common = {
        "record_mode": "family_seed",
        "destination": "PRACTICE",
        "family_type": "conceptual_application",
        "primary_i_can_id": "U1-S1-IC1",
        "primary_i_can": "I can test.",
        "supporting_i_can_ids": [],
        "evidence_job": "Do the thing.",
        "intended_reasoning": "Do the thing.",
        "difficulty_intent": "moderate",
        "security_level": "nonsecure_family",
        "selection_tags": ["U1-S1-IC1", "conceptual_application", "practice"],
        "locked_elements": ["primary_i_can_id"],
        "allowed_variations": ["context_evidence"],
        "required_variations": ["change evidence"],
        "forbidden_variations": ["noun/name swap as the only meaningful change"],
        "representation_variation_rule": "keep behavior",
        "scope": "1.1",
    }
    m1 = dict(common, record_id="U1-S1-PRACTICE-F01", family_id="U1-S1-PRACTICE-F01",
              question_structure_id="SELECT-01", response_mode="selected_response",
              representation_mode="direct_text", representation_need="none", choice_count=4,
              design_slot_id="U1-S1-PRACTICE-F01",
              representation_route={"route_type":"direct_render","representation":"direct_text"})
    m2 = dict(common, record_id="U1-S1-PRACTICE-F02", family_id="U1-S1-PRACTICE-F02",
              question_structure_id="REP-01", response_mode="constructed_response",
              representation_mode="supplied_diagram", representation_need="required",
              design_slot_id="U1-S1-PRACTICE-F02",
              representation_route={"route_type":"canonical_asset","canonical_path":"resources/img.png","asset_id":"X"})
    write_json(mroot / "practice_map.json", {"family_records":[m1,m2]})
    write_json(mroot / "MAP_MANIFEST.json", {"counts":{"practice_families":2},"map_fingerprint":"abc"})

    def authored(m, seed):
        a = {k:v for k,v in m.items() if k not in {"record_id","scope","choice_count","representation_route"}}
        a["section"] = "1.1"
        a["source_map_record_id"] = m["record_id"]
        a["source_basis"] = ["fixture"]
        a["question_design"] = {"design_slot_id":m["design_slot_id"]}
        a["canonical_seed"] = seed
        return a

    s1 = {
        "student_text":"Choose.",
        "student_html":"<p>Choose.</p><ol class=\"choices\"><li>One</li><li>Two</li><li>Three</li><li>Four</li></ol>",
        "choices":[{"id":"A","text":"One"},{"id":"B","text":"Two"},{"id":"C","text":"Three"},{"id":"D","text":"Four"}],
        "correct_choice":"A","answer":"One","solution_text":"Because.","solution_html":"<p>Because.</p>","figure_refs":[]
    }
    s2 = {
        "student_text":"Use diagram.",
        "student_html":"<p>Use diagram.</p><img src=\"../../resources/img.png\">",
        "answer":"Answer","solution_text":"Solution","solution_html":"<p>Solution</p>",
        "figure_refs":["resources/img.png"]
    }
    fams = [authored(m1,s1), authored(m2,s2)]
    write_json(bank / "practice/section_1.1.json", {"families":fams})
    write_json(bank / "BANK_MANIFEST.json", {
        "status":"BUILDING","ready_for_downstream":False,
        "completed":["3A_instructional_core","3B_practice_families"],
        "pending":["3C_assessment_families"],"next_phase":"3C_assessment_families",
        "accepted_bank_map":{"map_fingerprint":"abc"}
    })
    items = [
        {"item_id":"U1-S1-PRACTICE-F01","path":"practice/section_1.1.json","record_index":0,"record_mode":"family_seed"},
        {"item_id":"U1-S1-PRACTICE-F02","path":"practice/section_1.1.json","record_index":1,"record_mode":"family_seed"},
    ]
    write_json(bank / "ITEM_INDEX.json", {"record_count":2,"items":items})
    return bank


def run(root: Path):
    p = subprocess.run(["python3", str(TOOL), str(root), "--unit", "1"], text=True, capture_output=True)
    return p.returncode, p.stdout + p.stderr


def test_pass():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); fixture(root)
        rc,out = run(root)
        assert rc == 0, out
        assert "PASS" in out


def test_missing_family_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); bank = fixture(root)
        p = bank / "practice/section_1.1.json"
        d = json.loads(p.read_text()); d["families"] = d["families"][:1]; write_json(p,d)
        rc,out = run(root)
        assert rc == 1 and "FAMILY_MISSING" in out


def test_selected_response_missing_choices_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); bank = fixture(root)
        p = bank / "practice/section_1.1.json"
        d = json.loads(p.read_text()); d["families"][0]["canonical_seed"]["choices"] = []; write_json(p,d)
        rc,out = run(root)
        assert rc == 1 and "SR_CHOICES_MISSING" in out


def test_variation_drift_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); bank = fixture(root)
        p = bank / "practice/section_1.1.json"
        d = json.loads(p.read_text()); d["families"][0]["forbidden_variations"] = []; write_json(p,d)
        rc,out = run(root)
        assert rc == 1 and "MAP_FIELD_DRIFT" in out


def test_asset_not_rendered_fails():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); bank = fixture(root)
        p = bank / "practice/section_1.1.json"
        d = json.loads(p.read_text()); d["families"][1]["canonical_seed"]["student_html"] = "<p>Use diagram.</p>"; write_json(p,d)
        rc,out = run(root)
        assert rc == 1 and "ASSET_NOT_RENDERED" in out


if __name__ == "__main__":
    tests=[test_pass,test_missing_family_fails,test_selected_response_missing_choices_fails,test_variation_drift_fails,test_asset_not_rendered_fails]
    for t in tests:
        t(); print("PASS", t.__name__)
