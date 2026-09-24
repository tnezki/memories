#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import shutil
import tempfile
import uuid
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from portfolio_runtime import (
    COURSE_CONFIG,
    archive_and_install_results,
    archive_and_install_state,
    build_results,
    github_root_from_runtime,
    install_results_to_local_folders,
    load_learning_map,
    portfolio_root,
    read_csv,
    read_json,
    safe_zip_tree,
    sha256_file,
    state_path,
    unit_root,
    utc_now,
    validate_state_zip,
    write_csv,
    write_json,
)
from apply_grading_result import (
    determine_report_number,
    rebuild_intervention_groups,
    update_mg_state,
)

REGISTRY_FIELDS = ["student_key","student_id","student_name","display_name","period","active","identifier_quality"]
ICAN_FIELDS = ["student_key","student_id","student_name","period","mastery_goal_id","i_can_id","i_can_text","status_code","status_label","student_action_code","student_action_label","source_opportunity_count","independent_convincing_count","latest_source_label","latest_source_date","latest_strength","review_flag"]
MG_FIELDS = ["student_key","student_id","student_name","period","mg_code","mastery_goal_title","assessed","secure_i_can_count","i_can_count","required_secure_count","demonstrated","grade_code","grade_label","transfer","transfer_reason"]
UNIT_FIELDS = ["student_key","student_id","student_name","period","unit","mastery_goals_demonstrated","mastery_goals_total","report_number","report_date"]
LEDGER_FIELDS = ["event_id","student_key","student_id","student_name","period","source_sha256","source_hash","source_date","source_type","source_label","source_legacy_alias","page_ref","page_task_id","task_id","question_lineage","mastery_goal_id","i_can_id","i_can_exact_text","evidence_role","opportunity_id","independent_opportunity","strength","note","concise_note","review_flag"]
INTERVENTION_FIELDS = ["student_key","student_name","period","mastery_goal_id","i_can_id","i_can_text","student_action_code","student_action_label","intervention_group"]
CLASS_SUMMARY_FIELDS = ["mastery_goal_id","i_can_id","i_can_exact_text","no_evidence_count","developing_count","mastered_count","transfer_count"]
REVIEW_FIELDS = ["student_key","student_name","period","i_can_id","issue","details","run_id"]
RUN_HISTORY_FIELDS = ["run_id","run_date","source_label","source_date","source_sha256","roster_count","submission_count","no_submission_count","review_flag_count","result"]


def display_name(name: str) -> str:
    name = (name or "").strip()
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
        return (first + " " + last).strip()
    return name


def period_from_file(path: Path, meta_class: str) -> str:
    low = path.name.lower()
    m = re.search(r"\b(\d{1,2})(st|nd|rd|th)\b", low)
    if m:
        return f"{m.group(1)}{m.group(2)} Hour"
    m = re.search(r"\bperiod[_ -]?(\d{1,2})\b", low)
    if m:
        return f"Period {m.group(1)}"
    return meta_class.strip() or path.stem


def parse_powerschool(path: Path) -> tuple[str, list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header_idx = None
    meta_class = ""
    for i, row in enumerate(rows):
        if row and row[0].strip() == "Class:" and len(row) > 1:
            meta_class = row[1].strip()
        if len(row) >= 2 and row[0].strip() == "Student Num" and row[1].strip() == "Student Name":
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"PowerSchool roster header was not found in {path.name}")
    period = period_from_file(path, meta_class)
    students: list[dict[str, str]] = []
    for row in rows[header_idx + 1:]:
        if not row or not any(x.strip() for x in row):
            continue
        sid = row[0].strip() if len(row) > 0 else ""
        name = row[1].strip() if len(row) > 1 else ""
        if not sid or not name:
            continue
        students.append({
            "student_key": sid,
            "student_id": sid,
            "student_name": name,
            "display_name": display_name(name),
            "period": period,
            "active": "yes",
            "identifier_quality": "PowerSchool student number",
        })
    if not students:
        raise ValueError(f"No students were found in {path.name}")
    return period, students


def latest_evidence(state_dir: Path) -> tuple[str, str]:
    p = state_dir / "evidence_ledger.csv"
    if not p.is_file():
        return "Current Portfolio", datetime.now().date().isoformat()
    _f, rows = read_csv(p)
    candidates = []
    for r in rows:
        d = (r.get("source_date") or "").strip()
        label = (r.get("source_label") or "").strip()
        if d and label:
            candidates.append((d, label))
    if not candidates:
        return "Current Portfolio", datetime.now().date().isoformat()
    d, label = sorted(candidates)[-1]
    return label, d


def ensure_empty(path: Path, fields: list[str]) -> None:
    if not path.exists():
        write_csv(path, fields, [])


def learning_flat(learning: dict) -> tuple[list[dict], list[dict]]:
    mgs = learning.get("mastery_goals", [])
    icans = []
    for mg in mgs:
        for ic in mg.get("i_cans", []):
            icans.append({"mg_id": mg.get("id", ""), "mg_title": mg.get("title", ""), "i_can_id": ic.get("id", ""), "i_can_text": ic.get("statement", "")})
    return mgs, icans


def initialize_state(github_root: Path, course: str, unit: int, roster_files: list[Path], note: str, work_root: Path) -> tuple[dict, Path]:
    learning = load_learning_map(github_root, course, unit, None)
    state_dir = work_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    all_students: dict[str, dict[str, str]] = {}
    periods = []
    for rf in roster_files:
        period, students = parse_powerschool(rf)
        periods.append((period, rf))
        for s in students:
            if s["student_key"] in all_students:
                raise ValueError(f"Student {s['student_key']} appears more than once in the uploaded roster files.")
            all_students[s["student_key"]] = s
    write_csv(state_dir / "student_registry.csv", REGISTRY_FIELDS, list(all_students.values()))
    ensure_empty(state_dir / "evidence_ledger.csv", LEDGER_FIELDS)
    mgs, icatalog = learning_flat(learning)
    ican_rows = []
    mg_rows = []
    unit_rows = []
    report_date = datetime.now().date().isoformat()
    for s in all_students.values():
        for ic in icatalog:
            ican_rows.append({
                "student_key": s["student_key"], "student_id": s["student_id"], "student_name": s["display_name"], "period": s["period"],
                "mastery_goal_id": ic["mg_id"], "i_can_id": ic["i_can_id"], "i_can_text": ic["i_can_text"],
                "status_code": "NO_EVIDENCE", "status_label": "No Evidence", "student_action_code": "NEEDS_FIRST_CHECK", "student_action_label": "Needs first check",
                "source_opportunity_count": "0", "independent_convincing_count": "0", "latest_source_label": "", "latest_source_date": "", "latest_strength": "", "review_flag": "",
            })
        for mg in mgs:
            n = len(mg.get("i_cans", [])); threshold = (n + 1) // 2
            mg_rows.append({
                "student_key": s["student_key"], "student_id": s["student_id"], "student_name": s["student_name"], "period": s["period"],
                "mg_code": mg.get("id", ""), "mastery_goal_title": mg.get("title", ""), "assessed": "false", "secure_i_can_count": "0", "i_can_count": str(n),
                "required_secure_count": str(threshold), "demonstrated": "false", "grade_code": "", "grade_label": "Not assessed", "transfer": "false", "transfer_reason": "",
            })
        unit_rows.append({
            "student_key": s["student_key"], "student_id": s["student_id"], "student_name": s["student_name"], "period": s["period"], "unit": str(unit),
            "mastery_goals_demonstrated": "0", "mastery_goals_total": str(len(mgs)), "report_number": "1", "report_date": report_date,
        })
    write_csv(state_dir / "i_can_status_current.csv", ICAN_FIELDS, ican_rows)
    write_csv(state_dir / "mastery_goal_status_current.csv", MG_FIELDS, mg_rows)
    write_csv(state_dir / "unit_status_current.csv", UNIT_FIELDS, unit_rows)
    write_csv(state_dir / "class_i_can_summary.csv", CLASS_SUMMARY_FIELDS, [])
    write_csv(state_dir / "intervention_groups.csv", INTERVENTION_FIELDS, [])
    write_csv(state_dir / "review_queue.csv", REVIEW_FIELDS, [])
    run_id = f"{re.sub(r'[^A-Za-z0-9]+','',course).upper()}-U{unit}-LOCAL-INIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    write_csv(state_dir / "run_history.csv", RUN_HISTORY_FIELDS, [{
        "run_id": run_id, "run_date": report_date, "source_label": "Local roster initialization", "source_date": report_date, "source_sha256": "",
        "roster_count": str(len(all_students)), "submission_count": "0", "no_submission_count": "0", "review_flag_count": "0", "result": "PASS_LOCAL_INITIALIZATION",
    }])
    write_json(state_dir / "run_manifest.json", {
        "schema": "portfolio-run-manifest/1.2", "run_id": run_id, "course": course, "unit": unit, "report_number": 1, "report_date": report_date,
        "source_label": "Local roster initialization", "source_date": report_date, "roster_count": len(all_students), "submission_count": 0,
        "delivery": "portfolio_local_runtime", "teacher_note": note, "qa": {"evidence_state_changed": False, "grades_changed": False, "google_drive_used": False},
    })
    for period, rf in periods:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", period).strip("_") or "Class"
        shutil.copy2(rf, state_dir / f"PowerSchool_Template_{safe}_RAW.csv")
    files = []
    for p in sorted(state_dir.rglob("*")):
        if p.is_file():
            files.append({"path": p.relative_to(work_root).as_posix(), "sha256": sha256_file(p), "size_bytes": p.stat().st_size})
    manifest = {
        "schema": "portfolio-portable-state/1", "status": "CURRENT", "course": course, "unit": unit, "state_version": 1,
        "state_id": f"{course.replace(' ','-').upper()}-U{unit}-V1-{uuid.uuid4().hex[:8]}", "generated_at": utc_now(), "parent_state_sha256": None,
        "run_id": run_id, "source_mode": "local_roster_initialization", "files": files,
    }
    write_json(work_root / "STATE_MANIFEST.json", manifest)
    return manifest, state_dir


def update_existing_state(github_root: Path, current: Path, course: str, unit: int, roster_files: list[Path], note: str, work_root: Path) -> tuple[dict, Path, str, int, str]:
    old_manifest = validate_state_zip(current, course, unit)
    old_sha = sha256_file(current)
    with zipfile.ZipFile(current) as z:
        z.extractall(work_root)
    state_dir = work_root / "state"
    learning = load_learning_map(github_root, course, unit, state_dir)
    mgs, icatalog = learning_flat(learning)
    incoming: dict[str, dict[str, str]] = {}
    periods = []
    for rf in roster_files:
        period, students = parse_powerschool(rf)
        periods.append((period, rf))
        for s in students:
            if s["student_key"] in incoming:
                raise ValueError(f"Student {s['student_key']} appears more than once in the uploaded roster files.")
            incoming[s["student_key"]] = s
    reg_fields, registry = read_csv(state_dir / "student_registry.csv")
    for f in REGISTRY_FIELDS:
        if f not in reg_fields: reg_fields.append(f)
    by_key = {r.get("student_key", ""): r for r in registry}
    for r in registry:
        r["active"] = "no"
    for sk, s in incoming.items():
        r = by_key.get(sk)
        if r is None:
            r = {k: "" for k in reg_fields}; registry.append(r); by_key[sk] = r
        for k, v in s.items():
            if k in r: r[k] = v
        r["active"] = "yes"
    write_csv(state_dir / "student_registry.csv", reg_fields, registry)

    ic_fields, ic_rows = read_csv(state_dir / "i_can_status_current.csv")
    for f in ICAN_FIELDS:
        if f not in ic_fields: ic_fields.append(f)
    existing_pairs = {(r.get("student_key", ""), r.get("i_can_id", "")) for r in ic_rows}
    for r in ic_rows:
        s = by_key.get(r.get("student_key", ""))
        if s:
            r["student_id"] = s.get("student_id", r.get("student_id", "")); r["student_name"] = s.get("display_name", r.get("student_name", "")); r["period"] = s.get("period", r.get("period", ""))
    for sk, s in incoming.items():
        for ic in icatalog:
            if (sk, ic["i_can_id"]) in existing_pairs: continue
            row = {k: "" for k in ic_fields}
            row.update({"student_key":sk,"student_id":s["student_id"],"student_name":s["display_name"],"period":s["period"],"mastery_goal_id":ic["mg_id"],"i_can_id":ic["i_can_id"],"i_can_text":ic["i_can_text"],"status_code":"NO_EVIDENCE","status_label":"No Evidence","student_action_code":"NEEDS_FIRST_CHECK","student_action_label":"Needs first check","source_opportunity_count":"0","independent_convincing_count":"0"})
            ic_rows.append(row)
    write_csv(state_dir / "i_can_status_current.csv", ic_fields, ic_rows)

    mg_fields, mg_rows = read_csv(state_dir / "mastery_goal_status_current.csv")
    for f in MG_FIELDS:
        if f not in mg_fields: mg_fields.append(f)
    existing_mg = {(r.get("student_key", ""), r.get("mg_code") or r.get("mastery_goal_id") or "") for r in mg_rows}
    mg_by_id = {m.get("id",""):m for m in mgs}
    for r in mg_rows:
        s = by_key.get(r.get("student_key", "")); mid = r.get("mg_code") or r.get("mastery_goal_id") or ""
        if s:
            r["student_id"] = s.get("student_id",r.get("student_id","")); r["student_name"] = s.get("student_name",r.get("student_name","")); r["period"] = s.get("period",r.get("period",""))
        if mid in mg_by_id and "mastery_goal_title" in r: r["mastery_goal_title"] = mg_by_id[mid].get("title", r.get("mastery_goal_title",""))
    for sk, s in incoming.items():
        for mg in mgs:
            mid = mg.get("id","")
            if (sk, mid) in existing_mg: continue
            n = len(mg.get("i_cans", [])); threshold=(n+1)//2
            row={k:"" for k in mg_fields}; row.update({"student_key":sk,"student_id":s["student_id"],"student_name":s["student_name"],"period":s["period"],"mg_code":mid,"mastery_goal_title":mg.get("title",""),"assessed":"false","secure_i_can_count":"0","i_can_count":str(n),"required_secure_count":str(threshold),"demonstrated":"false","grade_code":"","grade_label":"Not assessed","transfer":"false"}); mg_rows.append(row)
    write_csv(state_dir / "mastery_goal_status_current.csv", mg_fields, mg_rows)

    report_number = determine_report_number(state_dir)
    report_date = datetime.now().date().isoformat()
    unit_fields, unit_rows = read_csv(state_dir / "unit_status_current.csv")
    for f in UNIT_FIELDS:
        if f not in unit_fields: unit_fields.append(f)
    by_unit = {r.get("student_key",""):r for r in unit_rows}
    for sk, s in incoming.items():
        if sk not in by_unit:
            row={k:"" for k in unit_fields}; row.update({"student_key":sk,"student_id":s["student_id"],"student_name":s["student_name"],"period":s["period"],"unit":str(unit),"mastery_goals_demonstrated":"0","mastery_goals_total":str(len(mgs)),"report_number":str(report_number),"report_date":report_date}); unit_rows.append(row); by_unit[sk]=row
    for r in unit_rows:
        s=by_key.get(r.get("student_key",""))
        if s:
            r["student_id"]=s.get("student_id",r.get("student_id","")); r["student_name"]=s.get("student_name",r.get("student_name","")); r["period"]=s.get("period",r.get("period","")); r["report_number"]=str(report_number); r["report_date"]=report_date
    write_csv(state_dir / "unit_status_current.csv", unit_fields, unit_rows)

    _, roster_now = read_csv(state_dir / "student_registry.csv")
    roster_by = {r.get("student_key",""):r for r in roster_now}
    _, _, grades = update_mg_state(state_dir, ic_rows, roster_by)
    # Update Unit demonstrated counts after MG recalculation.
    _, unit_rows = read_csv(state_dir / "unit_status_current.csv")
    for r in unit_rows:
        g=grades.get(r.get("student_key",""),{}); r["mastery_goals_demonstrated"]=str(sum(1 for x in g.values() if x.get("demonstrated"))); r["mastery_goals_total"]=str(len(g)); r["report_number"]=str(report_number); r["report_date"]=report_date
    write_csv(state_dir / "unit_status_current.csv", unit_fields, unit_rows)
    active_keys={r.get("student_key","") for r in roster_now if str(r.get("active","")).lower()=="yes"}
    rebuild_intervention_groups(state_dir, ic_rows, active_keys)
    # Physics/Calc style class summary is longitudinal status and should reflect the new active roster.
    cs_path=state_dir / "class_i_can_summary.csv"
    if cs_path.is_file():
        cs_fields,_=read_csv(cs_path)
        if "scope" not in cs_fields:
            grouped=defaultdict(list); text={}
            for r in ic_rows:
                if r.get("student_key") not in active_keys: continue
                mid=r.get("mastery_goal_id") or r.get("mg_code") or ""; iid=r.get("i_can_id","")
                grouped[(mid,iid)].append(r); text[iid]=r.get("i_can_text") or r.get("i_can_exact_text") or ""
            rows=[]
            for (mid,iid),rr in sorted(grouped.items()):
                counts=defaultdict(int)
                for x in rr: counts[x.get("status_code","")]+=1
                row={k:"" for k in cs_fields}; row.update({"mastery_goal_id":mid,"i_can_id":iid,"i_can_exact_text":text.get(iid,""),"no_evidence_count":str(counts["NO_EVIDENCE"]),"developing_count":str(counts["DEVELOPING"]),"mastered_count":str(counts["MASTERED"]),"transfer_count":str(counts["TRANSFER"])}); rows.append(row)
            write_csv(cs_path,cs_fields,rows)

    for period, rf in periods:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", period).strip("_") or "Class"
        shutil.copy2(rf, state_dir / f"PowerSchool_Template_{safe}_RAW.csv")

    run_id=f"{re.sub(r'[^A-Za-z0-9]+','',course).upper()}-U{unit}-ROSTER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    rh=state_dir / "run_history.csv"
    if rh.is_file():
        rh_fields,rh_rows=read_csv(rh)
    else:
        rh_fields,rh_rows=list(RUN_HISTORY_FIELDS),[]
    for f in RUN_HISTORY_FIELDS:
        if f not in rh_fields: rh_fields.append(f)
    row={k:"" for k in rh_fields}; row.update({"run_id":run_id,"run_date":report_date,"source_label":"Roster maintenance","source_date":report_date,"roster_count":str(len(incoming)),"submission_count":"0","no_submission_count":"0","review_flag_count":"0","result":"PASS_LOCAL_ROSTER_UPDATE"}); rh_rows.append(row); write_csv(rh,rh_fields,rh_rows)
    rm=state_dir / "run_manifest.json"; data=read_json(rm) if rm.is_file() else {}; data.update({"schema":data.get("schema","portfolio-run-manifest/1.2"),"run_id":run_id,"course":course,"unit":unit,"report_number":report_number,"report_date":report_date,"source_label":"Roster maintenance","source_date":report_date,"roster_count":len(incoming),"submission_count":0,"delivery":"portfolio_local_runtime","teacher_note":note,"qa":{"evidence_state_changed":False,"grades_changed":False,"google_drive_used":False}}); write_json(rm,data)

    files=[]
    for p in sorted(state_dir.rglob("*")):
        if p.is_file(): files.append({"path":p.relative_to(work_root).as_posix(),"sha256":sha256_file(p),"size_bytes":p.stat().st_size})
    new_version=int(old_manifest.get("state_version",0))+1
    new_manifest={"schema":"portfolio-portable-state/1","status":"CURRENT","course":course,"unit":unit,"state_version":new_version,"state_id":f"{course.replace(' ','-').upper()}-U{unit}-V{new_version}-{uuid.uuid4().hex[:8]}","generated_at":utc_now(),"parent_state_sha256":old_sha,"run_id":run_id,"source_mode":"local_roster_update","files":files}
    write_json(work_root / "STATE_MANIFEST.json",new_manifest)
    return new_manifest,state_dir,old_sha,report_number,report_date


def update_roster(course: str, unit: int, roster_files: list[Path], note: str = "") -> dict:
    if course not in COURSE_CONFIG:
        raise ValueError(f"Unsupported Portfolio course: {course}")
    roster_files=[Path(p) for p in roster_files]
    if not roster_files: raise ValueError("Select at least one current PowerSchool roster/template CSV.")
    for p in roster_files:
        if not p.is_file(): raise ValueError(f"Roster file not found: {p}")
    github_root=github_root_from_runtime(); root=portfolio_root(github_root); current=state_path(root,course,unit); uroot=unit_root(root,course,unit)
    uroot.mkdir(parents=True,exist_ok=True)
    (uroot / "02 Portfolio Data").mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="portfolio_roster_update_") as td:
        td=Path(td); state_work=td / "state_package"; state_work.mkdir()
        if current.is_file():
            manifest,state_dir,parent_sha,report_number,report_date=update_existing_state(github_root,current,course,unit,roster_files,note,state_work)
        else:
            manifest,state_dir=initialize_state(github_root,course,unit,roster_files,note,state_work)
            parent_sha=""; report_number=1; report_date=datetime.now().date().isoformat()
        new_zip=td / "Portfolio_State_UPDATED.zip"; safe_zip_tree(state_work,new_zip); new_sha=sha256_file(new_zip)
        latest_label,latest_date=latest_evidence(state_dir)
        results_dir=td / "results"; results_dir.mkdir()
        results_manifest=build_results(github_root,Path(__file__).resolve().parent,state_dir,manifest,new_sha,course,unit,report_number,report_date,latest_label,latest_date,None,results_dir)
        results_zip=td / "Portfolio_Results.zip"; safe_zip_tree(results_dir,results_zip)
        archive_and_install_state(new_zip,current,int(manifest["state_version"]))
        archive_and_install_results(results_zip,uroot)
        install_results_to_local_folders(results_dir,uroot)
        return {"status":"PASS","course":course,"unit":unit,"state_version":manifest["state_version"],"state_id":manifest["state_id"],"active_roster":len(parse_all_roster(roster_files)),"results_status":results_manifest.get("status"),"current_state":str(current),"latest_results":str(uroot / "02 Portfolio Data" / "Results Archives" / "Latest Portfolio Results.zip")}


def parse_all_roster(files: list[Path]) -> dict[str,dict[str,str]]:
    out={}
    for f in files:
        _period,students=parse_powerschool(f)
        for s in students: out[s["student_key"]]=s
    return out


def main() -> int:
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--course",required=True); ap.add_argument("--unit",type=int,required=True); ap.add_argument("--note",default=""); ap.add_argument("roster",nargs="+")
    args=ap.parse_args(); result=update_roster(args.course,args.unit,[Path(x) for x in args.roster],args.note); print(json.dumps(result,indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
