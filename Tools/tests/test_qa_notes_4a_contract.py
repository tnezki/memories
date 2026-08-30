import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

def blob_sha(p):
    b=p.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def fixture(tmp):
    root=tmp/"course"
    (root/"banks/unit1/notes").mkdir(parents=True)
    recs=[
      {"item_id":"W","destination":"WTC"},
      {"item_id":"E","destination":"EXAMPLE","pair_id":"P","pair_role":"example"},
      {"item_id":"Y","destination":"YTI","pair_id":"P","pair_role":"yti"},
    ]
    nf=root/"banks/unit1/notes/section_1.1.json"
    nf.write_text(json.dumps({"records":recs},indent=2))
    mf=root/"banks/unit1/BANK_MANIFEST.json"
    mf.write_text(json.dumps({"status":"COMPLETE","ready_for_downstream":True,
                              "paths":{"notes":"notes/section_<section-id>.json"}},indent=2))
    idx=[{"item_id":r["item_id"],"destination":r["destination"],"section":"1.1","path":"notes/section_1.1.json"} for r in recs]
    (root/"banks/unit1/ITEM_INDEX.json").write_text(json.dumps({"items":idx},indent=2))
    m={
      "schema":"physics-notes-map/2.0",
      "notes_flow_revision":"bank-v2-textbook-chunks-v2",
      "bank_manifest_path":"banks/unit1/BANK_MANIFEST.json",
      "bank_manifest_blob_sha":blob_sha(mf),
      "bank_notes_route_contract_schema":"legacy-paths-notes/1.0",
      "bank_notes_route_template":"notes/section_<section-id>.json",
      "sections":[{
        "section_id":"1.1","bank_notes_path":"banks/unit1/notes/section_1.1.json",
        "bank_notes_blob_sha":blob_sha(nf),
        "opening":{"wtc":{"item_id":"W"}},
        "ordered_flow":[{"flow_id":"f","primary_processing_after":{"type":"ex_yti","pair_id":"P",
          "example_id":"E","yti_id":"Y","display_pair_number":1}}],
        "post_reading_ex_yti_queue":[],
        "what_i_figured_out_target":"x","generated_representation_needs":[]
      }]
    }
    mp=tmp/"map.json"; mp.write_text(json.dumps(m,indent=2))
    return root,mp,m

def run(tool,root,mp):
    return subprocess.run([sys.executable,str(tool),str(root),"--unit","1","--map",str(mp)],
                          capture_output=True,text=True)

def test_pass():
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); root,mp,m=fixture(t)
        tool=Path(__file__).parents[1]/"qa_notes_4a_contract.py"
        r=run(tool,root,mp); assert r.returncode==0, r.stdout+r.stderr

def test_wrong_revision_fails():
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); root,mp,m=fixture(t)
        m.pop("notes_flow_revision"); m["flow_revision"]="bank-v2-textbook-chunks-v2"
        mp.write_text(json.dumps(m,indent=2))
        tool=Path(__file__).parents[1]/"qa_notes_4a_contract.py"
        r=run(tool,root,mp); assert r.returncode==1 and "FLOW_REVISION" in r.stdout
