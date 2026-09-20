#!/usr/bin/env python3
"""Fast deterministic mechanical QA for District Grading & Evidence responses.

This owns repeatable file/link/hash/policy checks so the model does not rewrite ad-hoc QA scripts.
It intentionally does not replace content judgment or visual inspection of true outliers.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

VERSION = "district-grading-mechanical-qa/1.1"

REQUIRED = [
    "CLICK_ME.html",
    "class/class_overview.html",
    "print/all_student_reports.html",
    "print/all_individual_practice.html",
    "print/common_review_extension/student_worksheet.html",
    "print/common_review_extension/teacher_guide.html",
    "print/stations/index.html",
    "print/stations/stations.html",
    "print/stations/answer_key.html",
    "print/question_set/index.html",
    "print/question_set/presentation.html",
    "print/question_set/print_presentation.html",
    "print/question_set/structures/cut_apart_cards.html",
    "data/response_data.json",
    "data/template_qa.json",
]
FORBIDDEN_DUPLICATES = [
    "class/review_all_questions.html",
    "print/question_set/review_all.html",
    "print/question_set/teacher_guide.html",
    "print/question_set/structures/find_someone_who.html",
]
ACTIVITY_NAMES = [
    "Whiteboard Indy", "Whiteboard Partners", "Rally Coach", "Speed Dating", "Showdown",
    "Think, Trade, Agree", "Round Table", "Hot Seat", "Rally Coach II",
    "Quiz-Quiz-Trade", "Fan-N-Pick", "Mix-Pair-Share with Cards", "Inside-Outside Circle with Cards",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.styles=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == "style": self.styles += 1
        for key in ("href","src"):
            if key in d and d[key]: self.refs.append(d[key])


def local_target(html_path: Path, ref: str, root: Path) -> Path | None:
    ref = ref.strip()
    if not ref or ref.startswith(("#","mailto:","tel:","javascript:","data:")):
        return None
    u=urlparse(ref)
    if u.scheme in ("http","https"): return None
    clean=u.path
    if not clean: return None
    return (html_path.parent / clean).resolve()


def add(checks, name, ok, **extra):
    checks[name] = {"status":"PASS" if ok else "FAIL", **extra}
    return ok


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--response", required=True)
    ap.add_argument("--request-root", required=True)
    ap.add_argument("--out", default="")
    args=ap.parse_args()
    response=Path(args.response).resolve(); req=Path(args.request_root).resolve()
    out=Path(args.out).resolve() if args.out else response/"data"/"mechanical_qa.json"
    checks={}; failures=[]

    missing=[p for p in REQUIRED if not (response/p).exists()]
    if not add(checks,"required_files",not missing,missing=missing): failures.append("required_files")

    template_qa=response/"data/template_qa.json"
    tq={}
    try: tq=json.loads(template_qa.read_text(encoding="utf-8"))
    except Exception as e: tq={"error":str(e)}
    if not add(checks,"template_qa",tq.get("status")=="PASS",builder_version=tq.get("builder_version"),detail=tq): failures.append("template_qa")

    expected_file=req/"response_contract/STYLE_SHA256.txt"
    style=response/"assets/styles.css"
    expected=expected_file.read_text(encoding="utf-8").strip() if expected_file.exists() else None
    actual=sha256(style) if style.exists() else None
    if not add(checks,"locked_style_sha",bool(expected and actual==expected),expected=expected,actual=actual): failures.append("locked_style_sha")

    station_expected=req/"response_contract/stations.css"
    station_actual=response/"assets/stations.css"
    exp_station=sha256(station_expected) if station_expected.exists() else None
    act_station=sha256(station_actual) if station_actual.exists() else None
    if not add(checks,"locked_station_css_sha",bool(exp_station and act_station==exp_station),expected=exp_station,actual=act_station): failures.append("locked_station_css_sha")

    broken=[]; local_style=[]
    html_files=sorted(response.rglob("*.html"))
    response_resolved=response.resolve()
    for h in html_files:
        parser=RefParser()
        try: parser.feed(h.read_text(encoding="utf-8",errors="replace"))
        except Exception as e:
            broken.append({"file":str(h.relative_to(response)),"ref":"<parse>","error":str(e)}); continue
        if parser.styles: local_style.append(str(h.relative_to(response)))
        for ref in parser.refs:
            target=local_target(h,ref,response)
            if target is None: continue
            try: target.relative_to(response_resolved)
            except ValueError:
                broken.append({"file":str(h.relative_to(response)),"ref":ref,"reason":"escapes response root"}); continue
            if not target.exists(): broken.append({"file":str(h.relative_to(response)),"ref":ref})
    if not add(checks,"local_links",not broken,broken=broken): failures.append("local_links")
    if not add(checks,"no_page_local_style_blocks",not local_style,files=local_style): failures.append("no_page_local_style_blocks")

    pdfs=[str(p.relative_to(response)) for p in response.rglob("*.pdf")]
    forbidden=[p for p in pdfs if not p.startswith("scanned_work/")]
    if not add(checks,"generated_pdf_policy",not forbidden,pdfs=pdfs,forbidden=forbidden): failures.append("generated_pdf_policy")

    duplicates=[p for p in FORBIDDEN_DUPLICATES if (response/p).exists()]
    if not add(checks,"no_duplicate_review_authority",not duplicates,files=duplicates): failures.append("no_duplicate_review_authority")

    adjustable=[
      "print/all_individual_practice.html",
      "print/common_review_extension/student_worksheet.html",
      "print/question_set/presentation.html",
      "print/question_set/print_presentation.html",
    ]
    missing_runtime=[]
    for rel in adjustable:
        p=response/rel
        if not p.exists(): continue
        s=p.read_text(encoding="utf-8",errors="replace")
        if "runtime.css" not in s or "runtime.js" not in s: missing_runtime.append(rel)
    if not add(checks,"runtime_assets_on_adjustable_pages",not missing_runtime,missing=missing_runtime): failures.append("runtime_assets_on_adjustable_pages")

    act=response/"print/question_set/index.html"
    txt=act.read_text(encoding="utf-8",errors="replace") if act.exists() else ""
    missing_names=[n for n in ACTIVITY_NAMES if n not in txt]
    prohibited=[n for n in ("Speed Dating Math","Mathematical Hot Seat","Tarsia","Blooket") if n in txt]
    if not add(checks,"activity_options",not missing_names and not prohibited,missing_names=missing_names,prohibited=prohibited): failures.append("activity_options")

    # Ensure Find Someone Who is a link to the Common Worksheet, not a separate handout.
    f_ok=("../common_review_extension/student_worksheet.html" in txt or "common_review_extension/student_worksheet.html" in txt)
    if not add(checks,"find_someone_who_reuse",f_ok): failures.append("find_someone_who_reuse")

    # Locked station markup is literal-template output, not a regenerated layout.
    station_shells={
        "print/stations/index.html":["station-index","station-list","station-card","Open Student Stations","Open Answer Key"],
        "print/stations/stations.html":["class=\"page\"","station-grid","station-problem","copy-note","page-footer"],
        "print/stations/answer_key.html":["class=\"page\"","solution-list","solution-item","page-footer"],
    }
    station_missing={}
    for rel,tokens in station_shells.items():
        p=response/rel; body=p.read_text(encoding="utf-8",errors="replace") if p.exists() else ""
        miss=[t for t in tokens if t not in body]
        if miss: station_missing[rel]=miss
    if not add(checks,"locked_station_shell",not station_missing,missing=station_missing): failures.append("locked_station_shell")

    pp=response/"print/question_set/print_presentation.html"
    ppt=pp.read_text(encoding="utf-8",errors="replace") if pp.exists() else ""
    pp_tokens=["runtime.css","runtime.js","runtime-set-page","runtime-set-question","runtime-set-teacher","Answer:","Teacher move:","Student discourse move:","All question spacing","Question spacing / workspace"]
    pp_missing=[t for t in pp_tokens if t not in ppt]
    if not add(checks,"print_presentation_locked_layout",not pp_missing,missing=pp_missing): failures.append("print_presentation_locked_layout")

    # Canonical response-data sanity.
    rd={}
    try: rd=json.loads((response/"data/response_data.json").read_text(encoding="utf-8"))
    except Exception as e: rd={"_error":str(e)}
    set1=rd.get("set1") or rd.get("set_1") or rd.get("question_set") or []
    if isinstance(set1,dict): set1=set1.get("questions") or []
    if not isinstance(set1,list): set1=[]
    unverified=[]
    for i,q in enumerate(set1,1):
        if not isinstance(q,dict) or not ((q.get("verification") or {}).get("passed") is True): unverified.append(i)
    if not add(checks,"set1_verification_flags",bool(set1) and not unverified,set1_count=len(set1),unverified=unverified): failures.append("set1_verification_flags")

    result={"version":VERSION,"status":"PASS" if not failures else "FAIL","checks":checks,"failures":failures,
            "note":"Mechanical QA only. Visual inspection is limited to generated graphs/diagrams and actual overflow/content outliers."}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"status":result["status"],"version":VERSION,"failures":failures,"out":str(out)}))
    return 0 if not failures else 2

if __name__ == "__main__":
    raise SystemExit(main())
