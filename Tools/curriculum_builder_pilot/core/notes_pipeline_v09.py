from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
from difflib import SequenceMatcher
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Tuple

from .authorities import ProjectContext, resolve_common
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha

NOTES_AI_SCHEMA = "curriculum-builder-ai-notes/0.9"
PIPELINE_SCHEMA = "curriculum-builder-notes-pipeline/0.9"
PACKAGE_SCHEMA = "curriculum-builder-ai-result-package/1"
PACKAGE_TYPE = "curriculum_builder_ai_result"
PILOT_VERSION = "0.9.0"


def _slug(text: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def _course_code(course: str) -> str:
    if course.strip().lower() == "algebra 1":
        return "ALG1"
    compact = "".join(ch for ch in course.upper() if ch.isalnum())
    return compact[:12] or "COURSE"


def ai_result_package_name(ctx: ProjectContext) -> str:
    return f"{_course_code(ctx.course)}_U{ctx.unit}_NOTES_AI_RESULT.zip"


def final_transfer_name(ctx: ProjectContext) -> str:
    return f"{_course_code(ctx.course)}_U{ctx.unit}_NOTES_TRANSFER.zip"


def _pipeline_root(staging_root: Path, ctx: ProjectContext) -> Path:
    return staging_root / "notes_pipeline" / _slug(ctx.course) / f"unit{ctx.unit}"


def _exchange_current(ai_exchange: Path, ctx: ProjectContext) -> Path:
    return ai_exchange / "Current" / _slug(ctx.course) / f"unit{ctx.unit}"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _strip_tags(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_li_list(block: str, heading: str) -> List[str]:
    pat = re.compile(
        rf"<h3[^>]*>\s*{re.escape(heading)}\s*</h3>\s*<ul[^>]*>(.*?)</ul>",
        re.I | re.S,
    )
    m = pat.search(block)
    if not m:
        return []
    return [_strip_tags(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", m.group(1), flags=re.I | re.S)]


def _parse_assessment_plan(path: Path, unit: int) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
    h1_text = _strip_tags(h1.group(1)) if h1 else f"Algebra 1 — Unit {unit}"
    unit_title = h1_text.split(":", 1)[1].strip() if ":" in h1_text else h1_text

    sections: List[Dict[str, Any]] = []
    pattern = re.compile(
        r'<section\s+class=["\']outline-card["\'][^>]*>\s*'
        r'<div\s+class=["\']outline-card-title["\'][^>]*>\s*Section\s+([^:<]+)\s*:\s*(.*?)</div>'
        r'(.*?)</section>',
        re.I | re.S,
    )
    for m in pattern.finditer(text):
        sid = _strip_tags(m.group(1))
        title = _strip_tags(m.group(2))
        body = m.group(3)
        lt = re.search(r"<p[^>]*>\s*<strong[^>]*>\s*Learning Target:\s*</strong>\s*(.*?)</p>", body, flags=re.I | re.S)
        learning_target = _strip_tags(lt.group(1)) if lt else ""
        i_cans = _extract_li_list(body, "I Can Statements")
        vocab = _extract_li_list(body, "Key Vocabulary / Notation")
        representations = _extract_li_list(body, "Key Representations")
        misconceptions = _extract_li_list(body, "Common Misconceptions / Failure Points")
        if learning_target and i_cans:
            sections.append({
                "section_id": sid,
                "section_title": title,
                "learning_target": learning_target,
                "i_can_texts": i_cans,
                "vocabulary": vocab,
                "key_representations": representations,
                "assessment_plan_misconceptions": misconceptions,
            })
    if not sections:
        raise ValueError("Could not resolve any Notes sections from the exact Unit Assessment Plan")
    return {"unit_title": unit_title, "sections": sections}


def _notes_sources(ctx: ProjectContext) -> Dict[str, Path]:
    common = resolve_common(ctx)
    rr = common["resource_root"]
    bank = ctx.course_dir / "banks" / f"unit{ctx.unit}"
    return {
        "philosophy": common["philosophy"],
        "runtime_contract": common["runtime_contract"],
        "framework": common["framework"],
        "question_structure_entrypoint": common["question_structure_entrypoint"],
        "question_structure_library": common["question_structure_library"],
        "assessment_plan": rr / f"assessment_plans/original/unit{ctx.unit}_assessment_plan/unit{ctx.unit}_assessment_plan.html",
        "notes_profile": rr / "profiles/notes_course_profile.json",
        "template": ctx.memories_dir / "Tools/templates/algebra/notes/notes_alg_section_template.html",
        "base_css": ctx.course_dir / "css/base.css",
        "notes_css": ctx.course_dir / "css/notes_alg.css",
        "bank_manifest": bank / "BANK_MANIFEST.json",
        "wtc_dir": bank / "wtc",
        "exit_dir": bank / "exit",
        "notes_pm": ctx.memories_dir / "pms_build/notes.txt",
        "tools_registry": common["tools_registry"],
        "finalization_contract": common["finalization_contract"],
    }




def _source_fingerprint(ctx: ProjectContext) -> str:
    src = _notes_sources(ctx)
    rows: List[Tuple[str, str]] = []
    for key in (
        "philosophy", "runtime_contract", "framework", "question_structure_entrypoint", "question_structure_library",
        "assessment_plan", "notes_profile", "template", "base_css", "notes_css", "bank_manifest", "notes_pm",
        "tools_registry", "finalization_contract",
    ):
        path = src[key]
        if path.is_file():
            rows.append((key, sha256_file(path)))
    for key in ("wtc_dir", "exit_dir"):
        path = src[key]
        if path.is_dir():
            for f in sorted(x for x in path.rglob("*") if x.is_file()):
                rows.append((f"{key}/{f.relative_to(path).as_posix()}", sha256_file(f)))
    blob = json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def _read_wtc(ctx: ProjectContext, section_id: str) -> Dict[str, Any]:
    path = ctx.course_dir / "banks" / f"unit{ctx.unit}" / "wtc" / f"section_{section_id}.json"
    return read_json(path)


def _read_exit(ctx: ProjectContext, section_id: str) -> Dict[str, Any]:
    path = ctx.course_dir / "banks" / f"unit{ctx.unit}" / "exit" / f"section_{section_id}.json"
    return read_json(path)


def _normalize_text(text: str) -> str:
    text = _strip_tags(text).lower()
    text = re.sub(r"\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _collect_item_texts(data: Any) -> List[str]:
    out: List[str] = []
    if isinstance(data, dict):
        if str(data.get("student_text") or "").strip():
            out.append(str(data["student_text"]))
        for key, value in data.items():
            if key not in {"answer", "solution_text", "solution_html"}:
                out.extend(_collect_item_texts(value))
    elif isinstance(data, list):
        for value in data:
            out.extend(_collect_item_texts(value))
    return out


def _canonical_i_can_ids(section: Dict[str, Any], wtc: Dict[str, Any], unit: int) -> List[Dict[str, Any]]:
    by_text: Dict[str, str] = {}
    for part in wtc.get("parts", []) if isinstance(wtc, dict) else []:
        if not isinstance(part, dict):
            continue
        ic = part.get("primary_i_can") if isinstance(part.get("primary_i_can"), dict) else {}
        text = str(ic.get("text") or "").strip()
        iid = str(ic.get("i_can_id") or "").strip()
        if text and iid:
            by_text[_normalize_text(text)] = iid
    out = []
    for index, text in enumerate(section["i_can_texts"], start=1):
        iid = by_text.get(_normalize_text(text)) or f"U{unit}-S{section['section_id']}-NOTES-IC{index:02d}"
        out.append({"i_can_id": iid, "source_i_can_index": index, "text": text})
    return out


def _build_facts(ctx: ProjectContext, plan: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    all_exit_texts: List[Dict[str, Any]] = []
    for source_sec in plan["sections"]:
        exit_data = _read_exit(ctx, source_sec["section_id"])
        for rec in exit_data.get("records", []) if isinstance(exit_data, dict) else []:
            if isinstance(rec, dict) and str(rec.get("student_text") or "").strip():
                all_exit_texts.append({
                    "section_id": source_sec["section_id"],
                    "item_id": rec.get("item_id"),
                    "student_text": rec.get("student_text"),
                })

    sections = []
    for sec in plan["sections"]:
        sid = sec["section_id"]
        wtc = _read_wtc(ctx, sid)
        parts = [p for p in wtc.get("parts", []) if isinstance(p, dict)]
        parts.sort(key=lambda p: str(p.get("part_label") or p.get("item_id") or ""))
        sections.append({
            **sec,
            "i_cans": _canonical_i_can_ids(sec, wtc, ctx.unit),
            "wtc": {
                "wtc_id": parts[0].get("wtc_id") if parts else f"U{ctx.unit}-S{sid}-WTC",
                "shared_stimulus_id": wtc.get("shared_stimulus_id"),
                "part_ids": [p.get("item_id") for p in parts],
            },
            "exit_items_for_duplicate_avoidance": all_exit_texts,
        })
    return {
        "schema": "curriculum-builder-notes-facts/0.9",
        "course": ctx.course,
        "unit": ctx.unit,
        "unit_title": plan["unit_title"],
        "accepted_map_fingerprint": manifest.get("accepted_map_fingerprint"),
        "sections": sections,
    }


def run_notes_preflight(ctx: ProjectContext) -> Dict[str, Any]:
    src = _notes_sources(ctx)
    steps: List[Dict[str, Any]] = []
    fatal = False
    for name in (
        "philosophy", "runtime_contract", "framework", "question_structure_entrypoint", "question_structure_library",
        "assessment_plan", "notes_profile", "template", "base_css", "notes_css", "bank_manifest", "wtc_dir", "exit_dir", "notes_pm",
    ):
        path = src[name]
        ok = path.is_dir() if name.endswith("_dir") else path.is_file()
        steps.append({"name": name, "status": "PASS" if ok else "FAIL", "path": str(path), "detail": "found" if ok else "missing"})
        fatal = fatal or not ok
    if fatal:
        return {"status": "BLOCKED", "steps": steps, "reason": "FAIL_BLOCKING_DEPENDENCY"}

    manifest = read_json(src["bank_manifest"])
    bank_ok = manifest.get("status") == "COMPLETE" and manifest.get("ready_for_downstream") is True and bool(manifest.get("accepted_map_fingerprint"))
    steps.append({
        "name": "Complete Bank downstream readiness",
        "status": "PASS" if bank_ok else "FAIL",
        "path": str(src["bank_manifest"]),
        "detail": f"status={manifest.get('status')} ready={manifest.get('ready_for_downstream')} fingerprint={'yes' if manifest.get('accepted_map_fingerprint') else 'no'}",
    })
    if not bank_ok:
        return {"status": "BLOCKED", "steps": steps, "reason": "FAIL_BLOCKING_DEPENDENCY"}

    try:
        plan = _parse_assessment_plan(src["assessment_plan"], ctx.unit)
    except Exception as exc:
        steps.append({"name": "Assessment Plan section parse", "status": "FAIL", "detail": str(exc), "path": str(src["assessment_plan"])})
        return {"status": "BLOCKED", "steps": steps, "reason": "FAIL_BLOCKING_DEPENDENCY"}
    missing = []
    for sec in plan["sections"]:
        sid = sec["section_id"]
        for kind, folder in (("WTC", src["wtc_dir"]), ("Exit", src["exit_dir"])):
            p = folder / f"section_{sid}.json"
            if not p.is_file():
                missing.append(f"{kind} {sid}: {p}")
    steps.append({"name": "Per-section canonical WTC + Exit", "status": "PASS" if not missing else "FAIL", "detail": f"{len(plan['sections'])} section(s)" if not missing else "; ".join(missing[:6])})
    return {"status": "PASS" if not missing else "BLOCKED", "steps": steps, "section_count": len(plan["sections"]), "reason": None if not missing else "FAIL_BLOCKING_DEPENDENCY"}


def _copy_source(src: Path, root: Path, github_root: Path) -> None:
    try:
        rel = src.resolve().relative_to(github_root.resolve())
    except Exception:
        rel = Path(src.name)
    dst = root / "inputs" / rel
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _zip_dir(root: Path, out_zip: Path) -> Path:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != out_zip:
                zf.write(path, path.relative_to(root))
    return out_zip


def _work_order(ctx: ProjectContext, run_id: str) -> str:
    return f"""CURRICULUM BUILDER v0.9 - ALGEBRA NOTES AUTHORING\n\nRUN ID: {run_id}\nCOURSE: {ctx.course}\nUNIT: {ctx.unit}\n\nSOURCE BOUNDARY - HARD\nUse only files in this handoff plus the teacher's current explicit instruction. No public web, File Library, old chats, saved memory, old Notes, alternate assessment plans, or similarly named substitutes.\n\nGOOD-ENOUGH / STOP RULE - HARD\nBuild the declared Notes content correctly, align to the included current authorities, satisfy this response contract, self-audit, and STOP. Do not redesign upstream curriculum or add optional polish.\n\nLOCAL APP OWNS THESE FACTS - DO NOT REAUTHOR THEM\n- exact section IDs/titles\n- exact Learning Targets\n- exact I Can wording/order\n- exact canonical Bank WTC\n- canonical Notes template/CSS\n- final section paths and filenames\n- graph rendering with the registered graph tool\n\nYOUR JOB\nRead NOTES_BUILD_FACTS.json and author the noncanonical instructional content for every section and every exact I Can. The local app will insert the canonical WTC itself, assemble student + teacher copies from the canonical template, render graphs, run focused Exit duplicate checks, finalize, and package the GitHub transfer.\n\nCONTENT RULES\n- Robust reading: normally 2-4 concise substantive paragraphs per I Can.\n- Math Notes must contain actual mathematics, not styled labels.\n- If four views are intentionally shown, they are exactly Equation/Rule + Table + Graph + Context/Situation. Ordered pairs are not a fifth view and cannot replace Graph.\n- Named representations must be literal. Use block type table for a table, graph for a graph, mapping for a mapping, ordered_pairs only when ordered pairs are the intended representation, and context for a situation.\n- Default one Example/YTI pair per exact I Can. Student prompts are unsolved. Teacher answer/reasoning/support go only in the teacher fields.\n- Example/YTI must be fresh and not duplicate or near-parallel the included Exit items.\n- Stop and Discuss: 2-3 concise prompts, not a second practice set.\n- Vocabulary Reference uses the exact vocabulary terms in NOTES_BUILD_FACTS; supply concise meanings only.\n- Common Mistakes: 2-4 high-value mistakes.\n- Do not author or alter the canonical WTC.\n\nSUPPORTED CONTENT BLOCKS\nEach math_notes_blocks / example.prompt_blocks / yti.prompt_blocks is an array of blocks. Supported types:\n- prose: {{\"type\":\"prose\",\"data\":{{\"text\":\"...\"}}}}\n- equation: {{\"type\":\"equation\",\"data\":{{\"latex\":\"...\"}}}}\n- table: {{\"type\":\"table\",\"data\":{{\"headers\":[...],\"rows\":[[...],...]}}}}\n- graph: structured graph spec; use semantic_mode algebra_coordinate for ordinary Algebra coordinate planes and context only for real-world axes. Functions may use families linear, quadratic, absolute_value, exponential, or constant with numeric parameters.\n- mapping: {{\"type\":\"mapping\",\"data\":{{\"inputs\":[...],\"outputs\":[...],\"pairs\":[[input,output],...]}}}}\n- ordered_pairs: {{\"type\":\"ordered_pairs\",\"data\":{{\"pairs\":[[x,y],...]}}}}\n- context: {{\"type\":\"context\",\"data\":{{\"text\":\"...\"}}}}\n\nOUTPUT CONTENT CONTRACT - HARD\nReturn one JSON payload with:\n{{\n  \"schema\": \"{NOTES_AI_SCHEMA}\",\n  \"run_id\": \"{run_id}\",\n  \"course\": \"{ctx.course}\",\n  \"unit\": {ctx.unit},\n  \"sections\": [\n    {{\n      \"section_id\": \"exact section ID\",\n      \"section_tagline\": \"short useful tagline\",\n      \"why_it_matters\": \"purpose without fake career relevance\",\n      \"intro_heading\": \"short heading\",\n      \"intro_paragraphs\": [\"...\"],\n      \"intro_close\": \"...\",\n      \"vocab_reference\": [{{\"term\":\"exact term\",\"meaning\":\"...\"}}],\n      \"i_can_content\": [\n        {{\n          \"i_can_id\": \"exact ID from NOTES_BUILD_FACTS\",\n          \"i_can_text\": \"exact wording from NOTES_BUILD_FACTS\",\n          \"robust_reading_paragraphs\": [\"...\"],\n          \"math_notes_title\": \"...\",\n          \"math_notes_blocks\": [],\n          \"math_notes_takeaway\": \"...\",\n          \"example\": {{\"title\":\"...\",\"prompt_blocks\":[],\"answer\":\"...\",\"reasoning\":\"...\",\"teacher_move\":\"...\",\"misconception\":\"...\"}},\n          \"yti\": {{\"title\":\"...\",\"prompt_blocks\":[],\"answer\":\"...\",\"reasoning\":\"...\",\"teacher_move\":\"...\",\"misconception\":\"...\"}},\n          \"stop_discuss_prompts\": [\"...\"],\n          \"stop_discuss_teacher_notes\": [\"...\"]\n        }}\n      ],\n      \"summary_bullets\": [\"...\"],\n      \"understand_now_prompt\": \"2-4 sentence reflection prompt\",\n      \"common_mistakes\": [{{\"mistake\":\"...\",\"remember\":\"...\"}}]\n    }}\n  ]\n}}\n\nTRANSPORT OUTPUT CONTRACT - HARD\nDo NOT return a loose JSON file. Return exactly ONE ZIP named:\n  {ai_result_package_name(ctx)}\n\nZIP root must be exactly:\n  BUILDER_RESULT_MANIFEST.json\n  payload/AI_NOTES_RESULT.json\n\nBUILDER_RESULT_MANIFEST.json must use schema {PACKAGE_SCHEMA}, package_type {PACKAGE_TYPE}, this exact run_id/course/unit, result_schema {NOTES_AI_SCHEMA}, result_filename AI_NOTES_RESULT.json, result_payload payload/AI_NOTES_RESULT.json, and result_sha256 equal to SHA-256 of the exact payload bytes.\n\nSELF-AUDIT BEFORE RETURN\n- exact section set\n- exact I Can set/order per section\n- exact vocabulary term set per section\n- one Example/YTI per I Can\n- 2-3 Stop and Discuss prompts per I Can\n- no Exit task duplication\n- no raw placeholder/TODO/TBD\n- no canonical WTC rewriting\n- named representations use the matching block type\n\nStop after returning the one ZIP.\n"""


def start_notes_pipeline(ctx: ProjectContext, staging_root: Path, ai_exchange: Path) -> Dict[str, Any]:
    preflight = run_notes_preflight(ctx)
    if preflight.get("status") != "PASS":
        return {"status": "BLOCKED", "stage": "preflight", "preflight": preflight}

    src = _notes_sources(ctx)
    manifest = read_json(src["bank_manifest"])
    plan = _parse_assessment_plan(src["assessment_plan"], ctx.unit)
    facts = _build_facts(ctx, plan, manifest)

    root = _pipeline_root(staging_root, ctx)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    exchange = _exchange_current(ai_exchange, ctx)
    exchange.mkdir(parents=True, exist_ok=True)
    for stale in exchange.glob("AI_NOTES_RESULT*.json"):
        try:
            stale.unlink()
        except Exception:
            pass

    pipeline_id = f"{time.strftime('%Y%m%d-%H%M%S')}_{_slug(ctx.course)}_u{ctx.unit}_notes_v09"
    run_id = pipeline_id + "_ai"
    work = root / "ai_handoff"
    work.mkdir()

    for key in (
        "philosophy", "runtime_contract", "framework", "question_structure_entrypoint", "question_structure_library",
        "assessment_plan", "notes_profile", "template", "base_css", "notes_css", "bank_manifest", "wtc_dir", "exit_dir", "notes_pm",
        "tools_registry", "finalization_contract",
    ):
        _copy_source(src[key], work, ctx.github_root)
    _write_json(work / "NOTES_BUILD_FACTS.json", facts)
    (work / "AI_WORK_ORDER.txt").write_text(_work_order(ctx, run_id), encoding="utf-8")
    _write_json(work / "RUN_MANIFEST.json", {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "job": "notes_build",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "accepted_map_fingerprint": manifest.get("accepted_map_fingerprint"),
        "section_count": len(facts["sections"]),
        "public_web_allowed": False,
        "file_library_allowed": False,
        "git_commands_allowed": False,
        "expected_result_package": ai_result_package_name(ctx),
        "source_fingerprint": _source_fingerprint(ctx),
    })
    handoff_name = f"AI_HANDOFF_{_course_code(ctx.course)}_U{ctx.unit}_NOTES.zip"
    handoff = _zip_dir(work, exchange / handoff_name)
    _write_json(root / "PIPELINE_STATE.json", {
        "schema": PIPELINE_SCHEMA,
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "course": ctx.course,
        "unit": ctx.unit,
        "stage": "awaiting_notes_ai",
        "system_head": read_head_sha(ctx.memories_dir),
        "course_head": read_head_sha(ctx.course_dir),
        "accepted_map_fingerprint": manifest.get("accepted_map_fingerprint"),
        "handoff": str(handoff),
        "source_fingerprint": _source_fingerprint(ctx),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    return {
        "status": "AI_NEEDED",
        "stage": "awaiting_notes_ai",
        "preflight": preflight,
        "handoff": str(handoff),
        "expected_result_package": ai_result_package_name(ctx),
        "section_count": len(facts["sections"]),
        "i_can_count": sum(len(s["i_cans"]) for s in facts["sections"]),
    }


def _load_active(ctx: ProjectContext, staging_root: Path) -> Tuple[Path, Dict[str, Any], Dict[str, Any]]:
    root = _pipeline_root(staging_root, ctx)
    state_path = root / "PIPELINE_STATE.json"
    facts_path = root / "ai_handoff" / "NOTES_BUILD_FACTS.json"
    if not state_path.is_file() or not facts_path.is_file():
        raise ValueError("No active Notes pipeline. Click Start Notes first.")
    return root, read_json(state_path), read_json(facts_path)


def _find_result(ai_exchange: Path, ctx: ProjectContext, run_id: str) -> Tuple[Path, Dict[str, Any]]:
    current = _exchange_current(ai_exchange, ctx)
    candidates = sorted(current.glob("AI_NOTES_RESULT*.json"), key=lambda p: p.stat().st_mtime, reverse=True) if current.is_dir() else []
    for path in candidates:
        try:
            data = read_json(path)
            if data.get("schema") == NOTES_AI_SCHEMA and str(data.get("run_id") or "") == run_id and data.get("course") == ctx.course and int(data.get("unit", -1)) == ctx.unit:
                return path, data
        except Exception:
            continue
    raise FileNotFoundError(
        f"Notes AI result has not been imported yet. Put {ai_result_package_name(ctx)} in _github_transfers, run Apply Curriculum Transfers.command, then click Continue Notes."
    )


def _validate_result(facts: Dict[str, Any], ai: Dict[str, Any]) -> None:
    rows = ai.get("sections")
    if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
        raise ValueError("AI_NOTES_RESULT sections must be an array of objects")
    expected = {s["section_id"]: s for s in facts["sections"]}
    actual_ids = [str(x.get("section_id") or "") for x in rows]
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != set(expected):
        raise ValueError("AI_NOTES_RESULT section IDs do not exactly match the Unit Assessment Plan")
    by_id = {str(x["section_id"]): x for x in rows}
    errors: List[str] = []
    forbidden = re.compile(r"\b(?:TODO|TBD|PLACEHOLDER)\b|\{\{[^}]+\}\}", re.I)
    for sid, fact in expected.items():
        sec = by_id[sid]
        for key in ("section_tagline", "why_it_matters", "intro_heading", "intro_close", "understand_now_prompt"):
            if not str(sec.get(key) or "").strip():
                errors.append(f"{sid}: missing {key}")
        if not isinstance(sec.get("intro_paragraphs"), list) or not sec["intro_paragraphs"]:
            errors.append(f"{sid}: intro_paragraphs missing")
        vocab = sec.get("vocab_reference")
        terms = [str(x.get("term") or "") for x in vocab] if isinstance(vocab, list) and all(isinstance(x, dict) for x in vocab) else []
        if terms != fact.get("vocabulary", []):
            errors.append(f"{sid}: vocab_reference term order/set must exactly match NOTES_BUILD_FACTS")
        ics = sec.get("i_can_content")
        if not isinstance(ics, list) or any(not isinstance(x, dict) for x in ics):
            errors.append(f"{sid}: i_can_content missing")
            continue
        exp_ics = fact["i_cans"]
        if [str(x.get("i_can_id") or "") for x in ics] != [x["i_can_id"] for x in exp_ics]:
            errors.append(f"{sid}: I Can IDs/order do not match")
        for i, exp in enumerate(exp_ics):
            if i >= len(ics):
                continue
            row = ics[i]
            if str(row.get("i_can_text") or "") != exp["text"]:
                errors.append(f"{sid}: I Can {i+1} wording drift")
            reading = row.get("robust_reading_paragraphs")
            if not isinstance(reading, list) or not (2 <= len(reading) <= 4):
                errors.append(f"{sid}: I Can {i+1} reading must contain 2-4 paragraphs")
            if not isinstance(row.get("math_notes_blocks"), list) or not row["math_notes_blocks"]:
                errors.append(f"{sid}: I Can {i+1} Math Notes blocks missing")
            else:
                math_kinds = {str(b.get("type") or "") for b in row["math_notes_blocks"] if isinstance(b, dict)}
                if not (math_kinds & {"equation", "table", "graph", "mapping", "ordered_pairs"}):
                    errors.append(f"{sid}: I Can {i+1} Math Notes must show actual mathematics/representation")
            for task_key in ("example", "yti"):
                task = row.get(task_key)
                if not isinstance(task, dict) or not isinstance(task.get("prompt_blocks"), list) or not task["prompt_blocks"]:
                    errors.append(f"{sid}: I Can {i+1} {task_key} missing")
                else:
                    for need in ("title", "answer", "reasoning", "teacher_move", "misconception"):
                        if not str(task.get(need) or "").strip():
                            errors.append(f"{sid}: I Can {i+1} {task_key} missing {need}")
            stop = row.get("stop_discuss_prompts")
            if not isinstance(stop, list) or not (2 <= len(stop) <= 3):
                errors.append(f"{sid}: I Can {i+1} Stop and Discuss must have 2-3 prompts")
        summary = sec.get("summary_bullets")
        if not isinstance(summary, list) or not summary:
            errors.append(f"{sid}: summary_bullets missing")
        mistakes = sec.get("common_mistakes")
        if not isinstance(mistakes, list) or not (2 <= len(mistakes) <= 4):
            errors.append(f"{sid}: common_mistakes must have 2-4 rows")
        if forbidden.search(json.dumps(sec, ensure_ascii=False)):
            errors.append(f"{sid}: placeholder/TODO/TBD remains")
    if errors:
        raise ValueError("AI_NOTES_RESULT validation failed: " + "; ".join(errors[:16]))


def _graph_tool(ctx: ProjectContext) -> Path:
    common = resolve_common(ctx)
    tools = read_json(common["tools_registry"])
    rel = ((tools.get("tools") or {}).get("graph_tool"))
    if not rel:
        raise ValueError("Registered graph_tool missing from Tools/MANIFEST.json")
    path = ctx.memories_dir / rel
    if not path.is_file():
        raise ValueError(f"Registered graph tool missing: {path}")
    return path


def _collect_graphs(ai: Dict[str, Any]) -> List[Dict[str, Any]]:
    specs: Dict[str, Dict[str, Any]] = {}

    def consume(blocks: Any) -> None:
        if not isinstance(blocks, list):
            return
        for block in blocks:
            if not isinstance(block, dict) or block.get("type") != "graph" or not isinstance(block.get("data"), dict):
                continue
            data = block["data"]
            clean = {k: v for k, v in data.items() if not str(k).startswith("_")}
            key = hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
            filename = f"notes_graph_{key}.png"
            data["_rendered_file"] = filename
            specs[filename] = {**clean, "filename": filename}

    for sec in ai.get("sections", []):
        for ic in sec.get("i_can_content", []):
            consume(ic.get("math_notes_blocks"))
            for task_key in ("example", "yti"):
                task = ic.get(task_key) if isinstance(ic.get(task_key), dict) else {}
                consume(task.get("prompt_blocks"))
    return list(specs.values())


def _append_graph_runner(graph_tool: Path, runner: Path) -> None:
    base = graph_tool.read_text(encoding="utf-8")
    code = r'''

# CURRICULUM BUILDER NOTES v0.9 APPEND-ONLY GRAPH GENERATION BLOCK
if __name__ == "__main__":
    import json as _json
    import sys as _sys
    from pathlib import Path as _Path
    spec_path = _Path(_sys.argv[1]); out_dir = _Path(_sys.argv[2]); out_dir.mkdir(parents=True, exist_ok=True)
    specs = _json.loads(spec_path.read_text(encoding="utf-8"))
    def _function(spec):
        family = str(spec.get("family") or "linear").lower(); p = spec.get("parameters") or {}
        if family == "linear":
            m=float(p.get("m",1)); b=float(p.get("b",0)); return (lambda x,m=m,b=b:m*x+b),(lambda x,m=m:np.full_like(x,m,dtype=float))
        if family == "quadratic":
            a=float(p.get("a",1)); h=float(p.get("h",0)); k=float(p.get("k",0)); return (lambda x,a=a,h=h,k=k:a*(x-h)**2+k),(lambda x,a=a,h=h:2*a*(x-h))
        if family == "absolute_value":
            a=float(p.get("a",1)); h=float(p.get("h",0)); k=float(p.get("k",0)); return (lambda x,a=a,h=h,k=k:a*np.abs(x-h)+k),(lambda x,a=a,h=h:a*np.sign(x-h))
        if family == "exponential":
            a=float(p.get("a",1)); basev=float(p.get("base",2)); h=float(p.get("h",0)); k=float(p.get("k",0)); return (lambda x,a=a,basev=basev,h=h,k=k:a*(basev**(x-h))+k),(lambda x,a=a,basev=basev,h=h:a*np.log(basev)*(basev**(x-h)))
        if family == "constant":
            c=float(p.get("c",0)); return (lambda x,c=c:np.full_like(x,c,dtype=float)),(lambda x:np.zeros_like(x,dtype=float))
        raise ValueError("Unsupported Notes graph family: "+family)
    for spec in specs:
        fig, ax = plt.subplots(figsize=(6,6))
        functions=[]
        for fn in spec.get("functions",[]) if isinstance(spec.get("functions"),list) else []:
            if not isinstance(fn,dict): continue
            expr,deriv=_function(fn)
            functions.append({"expr":expr,"deriv":deriv,"color":str(fn.get("color") or "steelblue"),"label":fn.get("label")})
        if isinstance(spec.get("line"),dict):
            m=float(spec["line"].get("slope",0)); b=float(spec["line"].get("intercept",0))
            functions.append({"expr":lambda x,m=m,b=b:m*x+b,"deriv":lambda x,m=m:np.full_like(x,m,dtype=float),"color":"steelblue","label":None})
        mode=str(spec.get("semantic_mode") or "algebra_coordinate").lower()
        if mode == "context":
            bounds=spec.get("bounds") or {}; xmin=float(bounds.get("x_min",0)); xmax=float(bounds.get("x_max",10)); ymin=float(bounds.get("y_min",0)); ymax=float(bounds.get("y_max",10))
            make_context_graph(ax,functions,xmin,xmax,ymin,ymax,xlabel=str(spec.get("x_label") or "x"),ylabel=str(spec.get("y_label") or "y"),title="")
        else:
            make_standard_graph(ax,functions,title="")
        pts=spec.get("points") if isinstance(spec.get("points"),list) else []
        if pts:
            xs=[float(p[0]) for p in pts if isinstance(p,(list,tuple)) and len(p)>=2]; ys=[float(p[1]) for p in pts if isinstance(p,(list,tuple)) and len(p)>=2]
            if xs and len(xs)==len(ys):
                ax.scatter(xs,ys,color="steelblue",s=42,zorder=5)
                if spec.get("connect_points"): ax.plot(xs,ys,color="steelblue",linewidth=2,zorder=4)
        fig.savefig(out_dir/spec["filename"],dpi=150,bbox_inches="tight"); plt.close(fig)
'''
    runner.write_text(base.rstrip() + "\n" + code, encoding="utf-8")


def _render_graphs(ctx: ProjectContext, root: Path, specs: List[Dict[str, Any]]) -> Path:
    figures = root / "generated_figures"
    figures.mkdir(parents=True, exist_ok=True)
    if not specs:
        return figures
    graph_tool = _graph_tool(ctx)
    runner = root / "generate_notes_graphs.py"
    spec_path = root / "NOTES_GRAPH_SPECS.json"
    _append_graph_runner(graph_tool, runner)
    _write_json(spec_path, specs)
    proc = subprocess.run([sys.executable, str(runner), str(spec_path), str(figures)], text=True, capture_output=True)
    if proc.returncode != 0:
        raise ValueError("Registered graph tool failed for Notes: " + (proc.stderr.strip() or proc.stdout.strip())[:1000])
    missing = [s["filename"] for s in specs if not (figures / s["filename"]).is_file()]
    if missing:
        raise ValueError("NOTES_REQUIRED_GRAPH_MISSING: " + ", ".join(missing[:8]))
    return figures


def _html_table(data: Dict[str, Any]) -> str:
    headers = data.get("headers")
    rows = data.get("rows")
    if not isinstance(headers, list) or not isinstance(rows, list):
        raise ValueError("Table block requires headers[] and rows[]")
    out = ['<table class="values"><thead><tr>']
    out.extend(f"<th>{html.escape(str(x))}</th>" for x in headers)
    out.append("</tr></thead><tbody>")
    for row in rows:
        if not isinstance(row, list):
            raise ValueError("Table row must be a list")
        out.append("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _render_mapping(data: Dict[str, Any]) -> str:
    pairs = data.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("Mapping block requires pairs[]")
    out = ['<div class="mapping-diagram" role="group" aria-label="Mapping diagram"><table class="values mapping-table"><thead><tr><th>Input</th><th></th><th>Output</th></tr></thead><tbody>']
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) < 2:
            raise ValueError("Mapping pair must contain input and output")
        out.append(f"<tr><td>{html.escape(str(pair[0]))}</td><td aria-hidden=\"true\">→</td><td>{html.escape(str(pair[1]))}</td></tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _render_blocks(blocks: List[Dict[str, Any]]) -> str:
    out: List[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        kind = str(block.get("type") or "")
        data = block.get("data") if isinstance(block.get("data"), dict) else {}
        if kind == "prose":
            out.append(f"<p>{html.escape(str(data.get('text') or ''))}</p>")
        elif kind == "equation":
            out.append(f'<div class="equation-card">\\[{html.escape(str(data.get("latex") or ""))}\\]</div>')
        elif kind == "table":
            out.append(_html_table(data))
        elif kind == "graph":
            filename = str(data.get("_rendered_file") or "")
            if not filename:
                raise ValueError("Graph block was not rendered")
            out.append(f'<div class="representation"><img class="graph-img" src="figures/{html.escape(filename)}" alt="Graph"></div>')
        elif kind == "mapping":
            out.append(_render_mapping(data))
        elif kind == "ordered_pairs":
            pairs = data.get("pairs") if isinstance(data.get("pairs"), list) else []
            notation = ",\\;".join(f"({html.escape(str(p[0]))},{html.escape(str(p[1]))})" for p in pairs if isinstance(p, (list, tuple)) and len(p) >= 2)
            out.append(f'<div class="equation-card">\\[{notation}\\]</div>')
        elif kind == "context":
            out.append(f'<div class="context-card"><p>{html.escape(str(data.get("text") or ""))}</p></div>')
        else:
            raise ValueError(f"Unsupported Notes content block: {kind}")
    return "".join(out)


def _copy_wtc_assets(ctx: ProjectContext, wtc: Dict[str, Any], section_dir: Path) -> None:
    bank_root = ctx.course_dir / "banks" / f"unit{ctx.unit}"
    names = set()
    blob = json.dumps(wtc, ensure_ascii=False)
    for match in re.finditer(r"figures/([A-Za-z0-9_.-]+)", blob):
        names.add(match.group(1))
    if not names:
        return
    figures = section_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = bank_root / "figures" / name
        if not src.is_file():
            raise ValueError(f"Canonical WTC figure missing: {src}")
        shutil.copy2(src, figures / name)


def _wtc_html(ctx: ProjectContext, sid: str, teacher: bool, issue_warning: str | None = None) -> Tuple[str, str]:
    wtc = _read_wtc(ctx, sid)
    shared = wtc.get("shared_stimulus") if isinstance(wtc.get("shared_stimulus"), dict) else {}
    parts = [p for p in wtc.get("parts", []) if isinstance(p, dict)]
    parts.sort(key=lambda p: str(p.get("part_label") or p.get("item_id") or ""))
    wtc_id = str(parts[0].get("wtc_id") if parts else f"U{ctx.unit}-S{sid}-WTC")
    out: List[str] = []
    if teacher and issue_warning:
        out.append(f'<div class="teacher-support"><strong>Teacher warning:</strong> {html.escape(issue_warning)}</div>')
    out.append(f'<div class="wtc-shared" data-shared-stimulus-id="{html.escape(str(wtc.get("shared_stimulus_id") or ""))}">{shared.get("student_html") or html.escape(str(shared.get("student_text") or ""))}</div>')
    for part in parts:
        label = str(part.get("part_label") or "Part")
        out.append(f'<section class="wtc-part" data-item-id="{html.escape(str(part.get("item_id") or ""))}"><h3>{html.escape(label)}</h3>{part.get("student_html") or f"<p>{html.escape(str(part.get("student_text") or ""))}</p>"}<div class="workspace"></div>')
        if teacher:
            out.append('<div class="teacher-support">')
            if str(part.get("answer") or "").strip():
                out.append(f'<p><strong>Answer:</strong> {html.escape(str(part.get("answer")))}</p>')
            if str(part.get("solution_text") or "").strip():
                out.append(f'<p><strong>Reasoning:</strong> {html.escape(str(part.get("solution_text")))}</p>')
            out.append('</div>')
        out.append('</section>')
    return wtc_id, "".join(out)


def _task_teacher_support(task: Dict[str, Any]) -> str:
    return (
        '<div class="teacher-support">'
        f'<p><strong>Answer:</strong> {html.escape(str(task.get("answer") or ""))}</p>'
        f'<p><strong>Reasoning:</strong> {html.escape(str(task.get("reasoning") or ""))}</p>'
        f'<p><strong>Teacher move:</strong> {html.escape(str(task.get("teacher_move") or ""))}</p>'
        f'<p><strong>Listen for:</strong> {html.escape(str(task.get("misconception") or ""))}</p>'
        '</div>'
    )


def _split_template(template: str) -> Tuple[str, str, str]:
    start_marker = "<!-- Repeat this I CAN BLOCK once per exact I Can in Framework order. -->"
    end_marker = "<!-- END REPEATED I CAN BLOCK -->"
    a = template.find(start_marker)
    b = template.find(end_marker)
    if a < 0 or b < 0 or b <= a:
        raise ValueError("Canonical Notes template repeat markers are missing")
    block_start = a + len(start_marker)
    return template[:a], template[block_start:b], template[b + len(end_marker):]


def _replace_tokens(text: str, values: Dict[str, str]) -> str:
    out = text
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def _task_text(task: Dict[str, Any]) -> str:
    parts: List[str] = []
    for block in task.get("prompt_blocks", []) if isinstance(task.get("prompt_blocks"), list) else []:
        if not isinstance(block, dict):
            continue
        data = block.get("data") if isinstance(block.get("data"), dict) else {}
        kind = block.get("type")
        if kind in {"prose", "context"}:
            parts.append(str(data.get("text") or ""))
        elif kind == "equation":
            parts.append(str(data.get("latex") or ""))
        elif kind == "table":
            parts.append(json.dumps(data, sort_keys=True))
        elif kind in {"graph", "mapping", "ordered_pairs"}:
            parts.append(json.dumps({k: v for k, v in data.items() if not str(k).startswith("_")}, sort_keys=True))
    return " ".join(parts)


def _representation_fidelity(task: Dict[str, Any], label: str, issues: List[Dict[str, Any]]) -> None:
    blocks = task.get("prompt_blocks") if isinstance(task.get("prompt_blocks"), list) else []
    kinds = {str(b.get("type") or "") for b in blocks if isinstance(b, dict)}
    prompt = _normalize_text(_task_text(task))
    checks = {"table": "table", "graph": "graph", "mapping": "mapping"}
    for word, kind in checks.items():
        if re.search(rf"\b{word}\b", prompt) and kind not in kinds:
            issues.append({"issue_code": "NOTES_REQUIRED_REPRESENTATION_MISSING", "severity": "BLOCKING", "owner": "NOTES_LOCAL_TASK_REPAIR", "description": f"{label} names {word} but has no {kind} block", "build_action_taken": "Stopped local assembly", "recommended_followup": "Repair the generated Notes task"})


def _focused_exit_check(ctx: ProjectContext, fact: Dict[str, Any], sec_ai: Dict[str, Any], issues: List[Dict[str, Any]]) -> None:
    exits = [str(x.get("student_text") or "") for x in fact.get("exit_items_for_duplicate_avoidance", []) if isinstance(x, dict)]
    for i, ic in enumerate(sec_ai.get("i_can_content", []), start=1):
        for task_key in ("example", "yti"):
            task = ic.get(task_key) if isinstance(ic.get(task_key), dict) else {}
            candidate = _normalize_text(_task_text(task))
            if not candidate:
                continue
            _representation_fidelity(task, f"{fact['section_id']} I Can {i} {task_key}", issues)
            for exit_text in exits:
                target = _normalize_text(exit_text)
                if not target:
                    continue
                ratio = SequenceMatcher(None, candidate, target).ratio()
                if candidate == target or (len(candidate) >= 35 and len(target) >= 35 and ratio >= 0.94):
                    issues.append({
                        "issue_code": "NOTES_LOCAL_TASK_EXIT_DUPLICATE",
                        "section_id": fact["section_id"],
                        "severity": "BLOCKING",
                        "owner": "NOTES_LOCAL_TASK_REPAIR",
                        "description": f"Generated {task_key} is too close to a canonical Exit item (similarity {ratio:.2f})",
                        "build_action_taken": "Stopped before final transfer",
                        "recommended_followup": "Regenerate this one local Notes task with fresh values/representation/context",
                    })
                    break


def _wtc_exit_conflict(ctx: ProjectContext, sid: str) -> bool:
    wtc = _read_wtc(ctx, sid)
    exit_data = _read_exit(ctx, sid)
    wtc_texts = [str(p.get("student_text") or "") for p in wtc.get("parts", []) if isinstance(p, dict)]
    exit_texts = [str(p.get("student_text") or "") for p in exit_data.get("records", []) if isinstance(p, dict)]
    for a in wtc_texts:
        na = _normalize_text(a)
        if not na:
            continue
        for b in exit_texts:
            nb = _normalize_text(b)
            if na == nb or (len(na) >= 35 and len(nb) >= 35 and SequenceMatcher(None, na, nb).ratio() >= 0.96):
                return True
    return False


def _assemble_section(
    ctx: ProjectContext,
    fact: Dict[str, Any],
    sec_ai: Dict[str, Any],
    template: str,
    output_root: Path,
    generated_figures: Path,
    issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    sid = fact["section_id"]
    section_slug = sid.replace(".", "_")
    section_dir = output_root / f"u{ctx.unit}_{section_slug.split('_',1)[1]}_notes" if section_slug.startswith(f"{ctx.unit}_") else output_root / f"u{ctx.unit}_{section_slug}_notes"
    # Canonical pattern uses u1_1_notes for section 1.1.
    section_tail = sid.split(".", 1)[1] if "." in sid else sid
    section_dir = output_root / f"u{ctx.unit}_{section_tail}_notes"
    section_dir.mkdir(parents=True, exist_ok=True)
    _copy_wtc_assets(ctx, _read_wtc(ctx, sid), section_dir)
    if generated_figures.is_dir():
        figures = section_dir / "figures"
        figures.mkdir(parents=True, exist_ok=True)
        for p in generated_figures.glob("*.png"):
            shutil.copy2(p, figures / p.name)

    prefix, ic_template, suffix = _split_template(template)
    vocab_terms = fact.get("vocabulary", [])
    vocab_ref = {str(x.get("term") or ""): str(x.get("meaning") or "") for x in sec_ai.get("vocab_reference", []) if isinstance(x, dict)}
    conflict = _wtc_exit_conflict(ctx, sid)
    warning = "Canonical WTC is unusually close to an Exit item. Keep WTC as written; route upstream repair to BANK/WTC REPAIR." if conflict else None
    if conflict:
        issues.append({
            "issue_code": "WTC_EXIT_CONFLICT", "section_id": sid, "severity": "WARNING", "owner": "BANK_WTC_REPAIR",
            "description": warning, "build_action_taken": "Preserved canonical WTC and added teacher-copy warning", "recommended_followup": "Repair upstream Bank/WTC after this Notes build",
        })

    for teacher in (False, True):
        wtc_id, wtc_content = _wtc_html(ctx, sid, teacher=teacher, issue_warning=warning)
        globals_map = {
            "COURSE": html.escape(ctx.course),
            "SECTION_ID": html.escape(sid),
            "SECTION_TITLE": html.escape(fact["section_title"]),
            "COPY_LABEL": "Teacher Copy" if teacher else "Student Copy",
            "COPY_CLASS": "teacher-copy" if teacher else "student-copy",
            "UNIT_LABEL": f"Unit {ctx.unit}",
            "UNIT_TITLE": html.escape(str(fact.get("unit_title") or "")),
            "SECTION_TAGLINE": html.escape(str(sec_ai.get("section_tagline") or "")),
            "LEARNING_TARGET": html.escape(fact["learning_target"]),
            "I_CAN_LIST_ITEMS": "".join(f"<li>{html.escape(ic['text'])}</li>" for ic in fact["i_cans"]),
            "WHY_IT_MATTERS": html.escape(str(sec_ai.get("why_it_matters") or "")),
            "INTRO_HEADING": html.escape(str(sec_ai.get("intro_heading") or "")),
            "INTRO_PARAGRAPHS": "".join(f"<p>{html.escape(str(p))}</p>" for p in sec_ai.get("intro_paragraphs", [])),
            "INTRO_CLOSE": html.escape(str(sec_ai.get("intro_close") or "")),
            "VOCAB_LIST": html.escape(" · ".join(vocab_terms)),
            "WTC_ID": html.escape(wtc_id),
            "WTC_CONTENT": wtc_content,
            "WTC_TEACHER_SUPPORT": "",
        }
        page = _replace_tokens(prefix, globals_map)
        ic_chunks: List[str] = []
        by_iid = {str(x.get("i_can_id") or ""): x for x in sec_ai.get("i_can_content", []) if isinstance(x, dict)}
        for n, ic_fact in enumerate(fact["i_cans"], start=1):
            ic_ai = by_iid[ic_fact["i_can_id"]]
            ex = ic_ai["example"]; yti = ic_ai["yti"]
            ic_values = {
                "I_CAN_ID": html.escape(ic_fact["i_can_id"]),
                "I_CAN_NUMBER": str(n),
                "I_CAN_TEXT": html.escape(ic_fact["text"]),
                "ROBUST_READING_PARAGRAPHS": "".join(f"<p>{html.escape(str(p))}</p>" for p in ic_ai.get("robust_reading_paragraphs", [])),
                "MATH_NOTES_TITLE": html.escape(str(ic_ai.get("math_notes_title") or "")),
                "SUBSTANTIVE_MATH_NOTES_VISUAL": _render_blocks(ic_ai.get("math_notes_blocks", [])),
                "MATH_NOTES_TAKEAWAY": f'<p class="takeaway">{html.escape(str(ic_ai.get("math_notes_takeaway") or ""))}</p>',
                "EXAMPLE_ID": f"U{ctx.unit}-S{sid}-NOTES-IC{n:02d}-EX",
                "EXAMPLE_TITLE": html.escape(str(ex.get("title") or "")),
                "EXAMPLE_PROMPT_AND_REPRESENTATION": _render_blocks(ex.get("prompt_blocks", [])),
                "EXAMPLE_TEACHER_SUPPORT": _task_teacher_support(ex) if teacher else "",
                "YTI_ID": f"U{ctx.unit}-S{sid}-NOTES-IC{n:02d}-YTI",
                "YTI_TITLE": html.escape(str(yti.get("title") or "")),
                "YTI_PROMPT_AND_REPRESENTATION": _render_blocks(yti.get("prompt_blocks", [])),
                "YTI_TEACHER_SUPPORT": _task_teacher_support(yti) if teacher else "",
                "STOP_DISCUSS_LIST_ITEMS": "".join(f"<li>{html.escape(str(p))}</li>" for p in ic_ai.get("stop_discuss_prompts", [])),
                "STOP_DISCUSS_TEACHER_SUPPORT": ('<div class="teacher-support"><p><strong>Teacher notes:</strong> ' + html.escape(" ".join(str(x) for x in ic_ai.get("stop_discuss_teacher_notes", []))) + '</p></div>') if teacher and ic_ai.get("stop_discuss_teacher_notes") else "",
            }
            ic_chunks.append(_replace_tokens(ic_template, ic_values))
        page += "".join(ic_chunks)
        suffix_values = {
            "VOCAB_REFERENCE_ROWS": "".join(f"<tr><td>{html.escape(term)}</td><td>{html.escape(vocab_ref.get(term,''))}</td></tr>" for term in vocab_terms),
            "SUMMARY_LIST_ITEMS": "".join(f"<li>{html.escape(str(x))}</li>" for x in sec_ai.get("summary_bullets", [])),
            "UNDERSTAND_NOW_PROMPT": html.escape(str(sec_ai.get("understand_now_prompt") or "")),
            "COMMON_MISTAKE_ROWS": "".join(f"<tr><td>{html.escape(str(x.get('mistake') or ''))}</td><td>{html.escape(str(x.get('remember') or ''))}</td></tr>" for x in sec_ai.get("common_mistakes", []) if isinstance(x, dict)),
        }
        page += _replace_tokens(suffix, suffix_values)
        name = f"u{ctx.unit}_{section_tail}_notes_teacher.html" if teacher else f"u{ctx.unit}_{section_tail}_notes.html"
        (section_dir / name).write_text(page, encoding="utf-8")
    return {"section_id": sid, "folder": section_dir.name, "wtc_id": wtc_id, "conflict_warning": conflict}


def _finalize(ctx: ProjectContext, notes_root: Path, log_path: Path) -> None:
    # Fresh Notes already use the canonical current template/CSS. The legacy
    # Notes layout-repair helper is intentionally NOT run here because it may
    # inject page-level teacher CSS, which the current Notes PM forbids.
    common = resolve_common(ctx)
    tools = read_json(common["tools_registry"])
    finalizer = ctx.memories_dir / ((tools.get("tools") or {}).get("finalize_output") or "Tools/finalize_output.py")
    if not finalizer.is_file():
        raise ValueError(f"Required finalization tool missing: {finalizer}")
    proc = subprocess.run([sys.executable, str(finalizer), str(notes_root)], text=True, capture_output=True)
    text = f"$ {sys.executable} {finalizer} {notes_root}\n{proc.stdout}\n{proc.stderr}\n"
    log_path.write_text(text, encoding="utf-8")
    if proc.returncode != 0 or "FINALIZATION_QA: PASS" not in text:
        raise ValueError("Notes finalization did not PASS")


def _mechanical_qa(ctx: ProjectContext, output_root: Path, facts: Dict[str, Any], ai: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    by_sid = {str(x.get("section_id") or ""): x for x in ai.get("sections", [])}
    for fact in facts["sections"]:
        sid = fact["section_id"]
        tail = sid.split(".", 1)[1] if "." in sid else sid
        folder = output_root / f"u{ctx.unit}_{tail}_notes"
        student = folder / f"u{ctx.unit}_{tail}_notes.html"
        teacher = folder / f"u{ctx.unit}_{tail}_notes_teacher.html"
        for path in (student, teacher):
            if not path.is_file():
                findings.append({"code": "NOTES_FILE_MISSING", "path": str(path)})
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "{{" in text or "}}" in text:
                findings.append({"code": "TEMPLATE_PLACEHOLDER_REMAINS", "path": str(path)})
            if '<link rel="stylesheet" href="../../css/base.css">' not in text or '<link rel="stylesheet" href="../../css/notes_alg.css">' not in text:
                findings.append({"code": "NOTES_CSS_CONTRACT", "path": str(path)})
            if "body class=\"notes-alg" not in text or 'main class="container notes-page"' not in text:
                findings.append({"code": "NOTES_SHELL_CONTRACT", "path": str(path)})
            if re.search(r"<style\b|\sstyle=", text, flags=re.I):
                findings.append({"code": "NOTES_PAGE_LEVEL_STYLE_FORBIDDEN", "path": str(path)})
            if fact["learning_target"] not in html.unescape(text):
                findings.append({"code": "LEARNING_TARGET_DRIFT", "section": sid, "path": str(path)})
            for ic in fact["i_cans"]:
                if html.escape(ic["text"]) not in text:
                    findings.append({"code": "I_CAN_DRIFT", "section": sid, "i_can_id": ic["i_can_id"]})
            wtc = _read_wtc(ctx, sid)
            parts = [p for p in wtc.get("parts", []) if isinstance(p, dict)]
            for part in parts:
                if str(part.get("item_id") or "") not in text:
                    findings.append({"code": "WTC_ID_MISSING", "section": sid, "item_id": part.get("item_id")})
            if path == student:
                for part in parts:
                    answer = str(part.get("answer") or "").strip()
                    if answer and len(answer) >= 12 and html.escape(answer) in text:
                        findings.append({"code": "STUDENT_WTC_ANSWER_LEAK", "section": sid, "item_id": part.get("item_id")})
        sec_ai = by_sid[sid]
        _focused_exit_check(ctx, fact, sec_ai, issues)
        # Four-view enforcement for Math Notes.
        for i, ic in enumerate(sec_ai.get("i_can_content", []), start=1):
            blocks = ic.get("math_notes_blocks") if isinstance(ic.get("math_notes_blocks"), list) else []
            kinds = {str(b.get("type") or "") for b in blocks if isinstance(b, dict)}
            rep_kinds = kinds & {"equation", "table", "graph", "context", "ordered_pairs"}
            if len(rep_kinds) >= 4:
                required = {"equation", "table", "graph", "context"}
                if not required.issubset(kinds):
                    issues.append({"issue_code": "NOTES_FOUR_VIEW_CONTRACT", "section_id": sid, "severity": "BLOCKING", "owner": "NOTES_LOCAL_TASK_REPAIR", "description": f"I Can {i} shows four+ representation types but does not include Equation/Rule + Table + Graph + Context/Situation", "build_action_taken": "Stopped before transfer", "recommended_followup": "Repair Math Notes representation set"})
    blocking = [x for x in issues if x.get("severity") == "BLOCKING"]
    status = "PASS" if not findings and not blocking else "FAIL"
    return {"schema": "curriculum-builder-notes-local-qa/0.9", "status": status, "finding_count": len(findings), "findings": findings, "blocking_issue_count": len(blocking)}


def _make_transfer(ctx: ProjectContext, staged_root: Path, transfer_root: Path, system_head: str | None, course_head: str | None) -> Path:
    entries: List[Dict[str, Any]] = []
    payloads: List[Tuple[Path, str]] = []
    # Notes section folders
    targets: List[Tuple[Path, Path]] = []
    for src in sorted(staged_root.glob(f"u{ctx.unit}_*_notes")):
        if src.is_dir():
            targets.append((src, ctx.course_dir / "notes" / src.name))
    prov = staged_root / "_notes_provenance" / f"unit{ctx.unit}"
    if prov.is_dir():
        targets.append((prov, ctx.course_dir / "_notes_provenance" / f"unit{ctx.unit}"))

    for src_root, dst_root in targets:
        staged_files = {p.relative_to(src_root).as_posix(): p for p in src_root.rglob("*") if p.is_file()}
        existing_files = {p.relative_to(dst_root).as_posix(): p for p in dst_root.rglob("*") if p.is_file()} if dst_root.is_dir() else {}
        for rel, src in sorted(staged_files.items()):
            dest = dst_root / rel
            dest_rel = dest.resolve().relative_to(ctx.github_root.resolve()).as_posix()
            old = existing_files.get(rel)
            if old and sha256_file(old) == sha256_file(src):
                continue
            arc = (Path("payload") / dest_rel).as_posix()
            row: Dict[str, Any] = {"action": "replace" if old else "create", "source": arc, "destination": dest_rel}
            if old:
                row["expected_existing_sha256"] = sha256_file(old)
            entries.append(row); payloads.append((src, arc))
        for rel, old in sorted(existing_files.items()):
            if rel not in staged_files:
                dest_rel = (dst_root / rel).resolve().relative_to(ctx.github_root.resolve()).as_posix()
                entries.append({"action": "delete", "destination": dest_rel, "expected_existing_sha256": sha256_file(old)})
    if not entries:
        raise ValueError("Notes build produced no repository changes")
    transfer_root.mkdir(parents=True, exist_ok=True)
    out = transfer_root / final_transfer_name(ctx)
    manifest = {
        "schema_version": 2,
        "package_type": "github_transfer",
        "package_id": f"{_slug(ctx.course)}_u{ctx.unit}_notes_v09_{time.strftime('%Y%m%d-%H%M%S')}",
        "source_snapshot": {"system_head": system_head, "course_head": course_head},
        "files": entries,
    }
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
        for src, arc in payloads:
            zf.write(src, arc)
    return out


def continue_notes_pipeline(ctx: ProjectContext, staging_root: Path, ai_exchange: Path, transfer_root: Path) -> Dict[str, Any]:
    root, state, facts = _load_active(ctx, staging_root)
    if state.get("stage") == "complete":
        return {"status": "PASS", "stage": "complete", "transfer_zip": state.get("transfer_zip"), "final_status": state.get("final_status")}
    if state.get("stage") != "awaiting_notes_ai":
        raise ValueError(f"Unknown Notes pipeline stage: {state.get('stage')}")
    if state.get("system_head") != read_head_sha(ctx.memories_dir) or state.get("course_head") != read_head_sha(ctx.course_dir):
        raise ValueError("Repository HEAD changed since the Notes AI handoff. Start Notes again so the handoff pins the current authorities.")
    if state.get("source_fingerprint") and state.get("source_fingerprint") != _source_fingerprint(ctx):
        raise ValueError("A Notes source file changed since the AI handoff. Start Notes again so the AI result is tied to the exact current authorities.")

    result_path, ai = _find_result(ai_exchange, ctx, str(state.get("run_id") or ""))
    _validate_result(facts, ai)
    specs = _collect_graphs(ai)
    figures = _render_graphs(ctx, root, specs)

    staged = root / "staged_notes"
    if staged.exists():
        shutil.rmtree(staged)
    staged.mkdir(parents=True)
    template = _notes_sources(ctx)["template"].read_text(encoding="utf-8")
    issues: List[Dict[str, Any]] = []
    by_sid = {str(x.get("section_id") or ""): x for x in ai["sections"]}
    section_reports = []
    for fact in facts["sections"]:
        fact = {**fact, "unit_title": facts.get("unit_title")}
        section_reports.append(_assemble_section(ctx, fact, by_sid[fact["section_id"]], template, staged, figures, issues))

    qa = _mechanical_qa(ctx, staged, facts, ai, issues)
    _write_json(staged / "NOTES_LOCAL_QA.json", qa)
    if qa.get("status") != "PASS":
        raise ValueError("Notes local QA did not PASS: " + json.dumps((qa.get("findings") or [])[:6] + [x for x in issues if x.get("severity") == "BLOCKING"][:4]))

    final_log = staged / "FINALIZATION_LOG.txt"
    _finalize(ctx, staged, final_log)

    prov = staged / "_notes_provenance" / f"unit{ctx.unit}"
    prov.mkdir(parents=True, exist_ok=True)
    canonical_wtc_ids = [r["wtc_id"] for r in section_reports]
    generated_task_ids = []
    for fact in facts["sections"]:
        sid = fact["section_id"]
        for n, _ in enumerate(fact["i_cans"], start=1):
            generated_task_ids += [f"U{ctx.unit}-S{sid}-NOTES-IC{n:02d}-EX", f"U{ctx.unit}-S{sid}-NOTES-IC{n:02d}-YTI"]
    final_status = "PASS_WITH_WARNINGS" if any(x.get("severity") == "WARNING" for x in issues) else "PASS"
    _write_json(prov / "NOTES_BUILD_HANDOFF.json", {
        "schema": "algebra-notes-build-handoff/1.0",
        "course": ctx.course,
        "unit": ctx.unit,
        "system_head": state.get("system_head"),
        "course_head": state.get("course_head"),
        "bank_path": f"banks/unit{ctx.unit}",
        "bank_status": "COMPLETE",
        "accepted_map_fingerprint": facts.get("accepted_map_fingerprint"),
        "canonical_wtc_ids": canonical_wtc_ids,
        "generated_notes_task_ids": generated_task_ids,
        "sections": [{"section_id": s["section_id"], "i_can_ids": [ic["i_can_id"] for ic in s["i_cans"]]} for s in facts["sections"]],
        "focused_exit_duplicate_check": "PASS",
        "graph_tool": str(_graph_tool(ctx).resolve().relative_to(ctx.memories_dir.resolve())),
        "issues": issues,
        "final_status": final_status,
    })
    (prov / "NOTES_BUILD_REPORT.txt").write_text(
        f"ALGEBRA 1 UNIT {ctx.unit} NOTES BUILD\nFINAL STATUS: {final_status}\nSections: {len(facts['sections'])}\nI Cans: {sum(len(s['i_cans']) for s in facts['sections'])}\nGenerated Example/YTI tasks: {len(generated_task_ids)}\nGraph assets: {len(specs)}\nIssues: {len(issues)}\nFINALIZATION_QA: PASS\n",
        encoding="utf-8",
    )
    _write_json(prov / "IMAGE_USE_MANIFEST.json", {
        "schema": "notes-image-use-manifest/1.0",
        "generated_graph_count": len(specs),
        "graph_files": [s["filename"] for s in specs],
        "canonical_wtc_images": "copied from current complete Bank where referenced",
    })

    transfer = _make_transfer(ctx, staged, transfer_root, state.get("system_head"), state.get("course_head"))
    state.update({"stage": "complete", "result_path": str(result_path), "transfer_zip": str(transfer), "final_status": final_status, "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    _write_json(root / "PIPELINE_STATE.json", state)
    return {
        "status": "PASS",
        "stage": "complete",
        "final_status": final_status,
        "section_count": len(facts["sections"]),
        "i_can_count": sum(len(s["i_cans"]) for s in facts["sections"]),
        "generated_task_count": len(generated_task_ids),
        "graph_asset_count": len(specs),
        "warning_count": sum(1 for x in issues if x.get("severity") == "WARNING"),
        "transfer_zip": str(transfer),
        "canonical_repo_modified": False,
    }
