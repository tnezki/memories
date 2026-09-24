#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from portfolio_runtime import (
    COURSE_CONFIG,
    SCHEMA_REQUEST,
    github_root_from_runtime,
    load_learning_map,
    local_git_head,
    portfolio_root,
    read_csv,
    read_json,
    roster_rows,
    scan_states,
    sha256_file,
    state_path,
    validate_state_zip,
    utc_now,
    write_json,
)


def osa(script: str) -> str:
    proc = subprocess.run(["/usr/bin/osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def choose_target(options: list[tuple[str, int, Path]]) -> tuple[str, int, Path] | None:
    labels = [f"{c} · Unit {u}" for c, u, _ in options]
    escaped = ",".join('"' + x.replace('"', '\\"') + '"' for x in labels)
    script = f'''set choices to {{{escaped}}}\ntry\nset picked to choose from list choices with prompt "Choose the Portfolio course and Unit for this grading request" with title "Portfolio Local Grader"\nif picked is false then return ""\nreturn item 1 of picked\non error number -128\nreturn ""\nend try'''
    picked = osa(script)
    if not picked:
        return None
    idx = labels.index(picked)
    return options[idx]


def choose_files(prompt: str, multiple: bool = True) -> list[Path]:
    multi = " with multiple selections allowed" if multiple else ""
    script = f'''try\nset fs to choose file with prompt "{prompt.replace('"','\\"')}"{multi}\nif class of fs is list then\nset out to ""\nrepeat with f in fs\nset out to out & POSIX path of f & linefeed\nend repeat\nreturn out\nelse\nreturn POSIX path of fs\nend if\non error number -128\nreturn ""\nend try'''
    out = osa(script)
    return [Path(x) for x in out.splitlines() if x.strip()]


def ask_text(prompt: str, default: str = "") -> str:
    script = f'''try\ndisplay dialog "{prompt.replace('"','\\"')}" default answer "{default.replace('"','\\"')}" with title "Portfolio Local Grader"\nreturn text returned of result\non error number -128\nreturn ""\nend try'''
    return osa(script)


def ask_yes_no(prompt: str) -> bool:
    script = f'''try\ndisplay dialog "{prompt.replace('"','\\"')}" with title "Portfolio Local Grader" buttons {{"No","Yes"}} default button "No"\nreturn button returned of result\non error number -128\nreturn "No"\nend try'''
    return osa(script) == "Yes"


def main() -> int:
    github_root = github_root_from_runtime()
    root = portfolio_root(github_root)
    states = scan_states(root)
    if not states:
        print("No local Portfolio_State_CURRENT.zip files were found under _portfolio_data.")
        return 1
    target = choose_target(states)
    if not target:
        print("Canceled. No grading request was created.")
        return 0
    course, unit, current_state = target
    manifest = validate_state_zip(current_state, course, unit)

    evidence_files = choose_files("Choose the NEW student evidence file(s) for this grading run")
    if not evidence_files:
        print("Canceled. No evidence was selected.")
        return 0
    support_files: list[Path] = []
    if ask_yes_no("Do you need to attach an answer key, source map, rubric, or other teacher supporting file?"):
        support_files = choose_files("Choose supporting file(s). These are references, not student evidence.")

    label = ask_text("Evidence label", "New Evidence") or "New Evidence"
    date = ask_text("Evidence date (YYYY-MM-DD)", "")

    with tempfile.TemporaryDirectory(prefix="portfolio_grading_request_") as td:
        work = Path(td)
        with zipfile.ZipFile(current_state) as z:
            z.extractall(work / "current_state")
        state_dir = work / "current_state" / "state"
        _, roster, _ = roster_rows(state_dir)
        _, icans = read_csv(state_dir / "i_can_status_current.csv")
        prior_summary = []
        for r in icans:
            prior_summary.append({
                "student_key": r.get("student_key", ""),
                "student_name": r.get("student_name", ""),
                "period": r.get("period", ""),
                "mastery_goal_id": r.get("mastery_goal_id") or r.get("mg_code") or "",
                "i_can_id": r.get("i_can_id", ""),
                "i_can_text": r.get("i_can_text") or r.get("i_can_exact_text") or "",
                "status_code": r.get("status_code", ""),
                "student_action_code": r.get("student_action_code", ""),
                "independent_convincing_count": r.get("independent_convincing_count", ""),
                "latest_strength": r.get("latest_strength", ""),
                "latest_source": r.get("latest_source_label") or r.get("latest_source") or "",
                "latest_source_date": r.get("latest_source_date", ""),
                "review_flag": r.get("review_flag", ""),
            })
        learning = load_learning_map(github_root, course, unit, state_dir)
        cfg = COURSE_CONFIG[course]
        course_repo_dir = github_root / cfg["repo_folder"]
        memories = github_root / "memories"
        attached_authorities = {
            "grading_pm": memories / "pms_build" / "portfolio_grading_local.txt",
            "base_portfolio_pm": memories / "pms_build" / "portfolio.txt",
            "course_policy": memories / cfg["policy_path"],
            "result_schema": Path(__file__).resolve().parent / "PORTFOLIO_GRADING_RESULT_SCHEMA.json",
        }
        for label_name, authority_path in attached_authorities.items():
            if not authority_path.is_file():
                raise ValueError(f"Required local grading authority is missing: {label_name} -> {authority_path}")
        request = {
            "schema": SCHEMA_REQUEST,
            "created_at": utc_now(),
            "course": course,
            "unit": unit,
            "pm_entrypoint": "pms_build/portfolio_grading_local.txt",
            "system_repo": "tnezki/memories",
            "system_commit": local_git_head(github_root / "memories"),
            "course_repo": cfg["course_repo"],
            "course_commit": local_git_head(course_repo_dir),
            "course_policy": cfg["policy_path"],
            "attached_authorities": {k: f"authority/{v.name}" for k, v in attached_authorities.items()},
            "parent_state": {
                "sha256": sha256_file(current_state),
                "state_version": manifest.get("state_version"),
                "state_id": manifest.get("state_id"),
            },
            "source": {
                "label": label,
                "date": date,
                "type": "teacher_supplied_evidence",
                "evidence_files": [{"name": p.name, "sha256": sha256_file(p)} for p in evidence_files],
                "supporting_files": [{"name": p.name, "sha256": sha256_file(p)} for p in support_files],
            },
            "output": {
                "filename": "Portfolio_Grading_Result.json",
                "schema": "portfolio-grading-result/1.0",
                "state_or_reports_from_chatgpt": False,
            },
            "rules": {
                "chatgpt_role": "grade_and_structure_source_level_evidence_only",
                "local_python_role": "state_update_status_grades_reports_powerschool_email_prep",
                "google_drive_allowed": False,
                "do_not_build_reports": True,
                "do_not_build_portable_state": True,
            },
        }
        context = {
            "schema": "portfolio-grading-context/1.0",
            "course": course,
            "unit": unit,
            "active_roster": [
                {"student_key": r["student_key"], "student_id": r["student_id"], "student_name": r["display_name"], "period": r["period"]}
                for r in roster if r["active"] == "yes"
            ],
            "learning_map": learning,
            "prior_i_can_state": prior_summary,
            "privacy": "Private student context for this grading request only. Never write to GitHub.",
        }

        downloads = Path.home() / "Downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        out = downloads / f"portfolio_grading_request_{course.lower().replace(' ','_')}_u{unit}_{utc_now()[:10].replace('-','')}.zip"
        # avoid overwriting another request from the same day
        n = 2
        while out.exists():
            out = downloads / f"portfolio_grading_request_{course.lower().replace(' ','_')}_u{unit}_{utc_now()[:10].replace('-','')}_{n}.zip"
            n += 1
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("REQUEST.json", json.dumps(request, indent=2, ensure_ascii=False) + "\n")
            z.writestr("grading_context.json", json.dumps(context, indent=2, ensure_ascii=False) + "\n")
            for label_name, authority_path in attached_authorities.items():
                z.write(authority_path, f"authority/{authority_path.name}")
            for p in evidence_files:
                z.write(p, f"evidence/{p.name}")
            for p in support_files:
                z.write(p, f"supporting/{p.name}")
        print(f"Portfolio grading request created:\n{out}\n")
        print("Upload that ZIP to ChatGPT. The expected response is one Portfolio_Grading_Result.json file.")
        subprocess.run(["/usr/bin/open", "-R", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
