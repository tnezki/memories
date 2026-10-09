#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import time
import zipfile
from itertools import combinations
from pathlib import Path
from typing import Any

import checkpoint_engine as core
import summative_output


def _mastered(record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    bars = core.parse_mastery_bars(record.get("mastery_bars"))
    if bars is None:
        bars = core.parse_mastery_bars(record.get("status"))
    if bars is not None:
        return bars >= 4
    low = core.normalize_text(record.get("status")).lower()
    return any(term in low for term in ("mastered", "extended", "mastery", "transfer", "secure"))


def eligibility_catalog(github_root: Path) -> dict[str, Any]:
    return core.eligibility_catalog(github_root)


def _family_is_summative_preferred(family: dict[str, Any]) -> bool:
    values = [str(x).strip().lower() for x in family.get("product_eligibility", [])]
    return any("summative" in x for x in values)


def _source_family_pool(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred = [f for f in candidates if _family_is_summative_preferred(f)]
    return preferred or candidates


def _choose_source_family(candidates: list[dict[str, Any]], seed: str) -> dict[str, Any] | None:
    return core.stable_choice(_source_family_pool(candidates), seed)


def _find_extension_targets(students: list[dict[str, Any]], eligible: list[str], limit: int = 4) -> list[str]:
    needing = [s for s in students if int(s.get("extension_count", 0) or 0) > 0]
    if not needing:
        return []
    candidates = [iid for iid in eligible if any(iid in set(s.get("secure_i_cans") or []) for s in needing)]
    # Small exact multicover search: find the smallest <=4 set of mastered I Cans
    # so every student receives as many distinct extension families as needed.
    for size in range(1, min(limit, len(candidates)) + 1):
        for combo in combinations(candidates, size):
            chosen = set(combo)
            if all(len(chosen.intersection(set(s.get("secure_i_cans") or []))) >= int(s.get("extension_count", 0) or 0) for s in needing):
                return list(combo)
    raise ValueError(
        "The selected I Can scope cannot cover every student's extension slots with four reusable extension families. "
        "Select a broader/common I Can scope, or reduce the personalized summative question count."
    )


def build_summative_plan(
    github_root: Path,
    item_label: str,
    custom_name: str,
    eligible_i_cans: list[str],
    target_questions: int = 4,
    unit: int = 1,
) -> dict[str, Any]:
    target_questions = max(1, min(int(target_questions), 4))
    eligible = sorted({x for x in (core.normalize_ican(v) for v in eligible_i_cans) if x}, key=core.ican_sort_key)
    if len(eligible) < target_questions:
        raise ValueError(f"Select at least {target_questions} I Can statements before analyzing Summative evidence.")

    scan = core.scan_portfolio(github_root, None)
    banks = core.load_all_banks(github_root)
    catalog = {k: dict(v) for k, v in banks.get("catalog", {}).items()}
    by_ican: dict[str, list[dict[str, Any]]] = {}
    for family in banks.get("families", []):
        iid = core.normalize_text(family.get("i_can_id"))
        if iid:
            by_ican.setdefault(iid, []).append(family)
    for iid in by_ican:
        by_ican[iid].sort(key=lambda f: (core.normalize_text(f.get("family_label")), core.normalize_text(f.get("family_id"))))
    for iid in eligible:
        if iid not in catalog:
            m = core.ICAN_RE.search(iid)
            if m:
                catalog[iid] = {
                    "i_can_id": iid,
                    "exact_text": "",
                    "mg_id": f"U{int(m.group(1))}-MG{m.group(2)}",
                    "unit": int(m.group(1)),
                }

    by_student: dict[str, list[dict[str, Any]]] = {s: [] for s in scan.get("students", [])}
    for record in scan.get("records", []):
        by_student.setdefault(record.get("student", ""), []).append(record)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    base_label = re.sub(r"[^A-Za-z0-9]+", "_", item_label or "summative").strip("_") or "summative"
    plan_id = f"summative_{base_label}_{stamp}"
    salt = hashlib.sha256((plan_id + str(time.time_ns())).encode("utf-8")).hexdigest()[:16]

    students: list[dict[str, Any]] = []
    reassessment_total = 0
    extension_total = 0
    source_by_ican: dict[str, dict[str, Any]] = {}

    for student in sorted(by_student, key=lambda s: s.lower()):
        recs = by_student[student]
        current = {r.get("i_can_id"): r for r in recs if r.get("i_can_id")}
        needs: list[dict[str, Any]] = []
        secure: list[str] = []
        for iid in eligible:
            record = current.get(iid)
            if _mastered(record):
                secure.append(iid)
                continue
            if record is None:
                record = {
                    "student": student,
                    "i_can_id": iid,
                    "status": "Not Yet Assessed",
                    "mastery_bars": 0,
                    "observation_count": 0,
                }
            needs.append(record)
        needs.sort(key=lambda r: (
            core.parse_mastery_bars(r.get("mastery_bars")) if core.parse_mastery_bars(r.get("mastery_bars")) is not None else 0,
            core.ican_sort_key(r.get("i_can_id", "")),
        ))
        chosen = needs[:target_questions]
        reassessment_total += len(chosen)
        extension_count = target_questions - len(chosen)
        extension_total += extension_count
        sk = core.anonymize(student, salt)
        slots = []
        for slot, record in enumerate(chosen, start=1):
            iid = record["i_can_id"]
            source = source_by_ican.get(iid)
            if source is None:
                source = _choose_source_family(by_ican.get(iid, []), f"summative|{plan_id}|{iid}")
                if source is None:
                    raise ValueError(f"No current approved/DRAFT_REVIEW bank family exists for {iid}; Summative MC conversion needs a source family first.")
                source_by_ican[iid] = source
            info = catalog.get(iid) or {}
            slots.append({
                "slot": slot,
                "kind": "reassessment_mc",
                "i_can_id": iid,
                "i_can_text": str(info.get("exact_text") or ""),
                "status": record.get("status", ""),
                "mastery_bars": record.get("mastery_bars"),
                "source_family_id": source.get("family_id", ""),
                "source_teacher_question_id": source.get("teacher_question_id", ""),
                "source_family_name": source.get("family_name", ""),
            })
        students.append({
            "student_key": sk,
            "student_display": student,
            "reassessment_need_count": len(chosen),
            "reassessment_slots": slots,
            "extension_count": extension_count,
            "secure_i_cans": sorted(secure, key=core.ican_sort_key),
        })

    extension_targets = _find_extension_targets(students, eligible, 4)
    extension_requests: list[dict[str, Any]] = []
    assigned_counts: dict[str, int] = {s["student_key"]: 0 for s in students}
    for iid in extension_targets:
        assigned = []
        for s in students:
            need = int(s.get("extension_count", 0) or 0)
            if need <= assigned_counts[s["student_key"]]:
                continue
            if iid in set(s.get("secure_i_cans") or []):
                assigned.append(s["student_key"])
                assigned_counts[s["student_key"]] += 1
        if assigned:
            info = catalog.get(iid) or {}
            extension_requests.append({
                "slot_kind": "extension_mc",
                "target_i_can_id": iid,
                "target_i_can_text": str(info.get("exact_text") or ""),
                "assigned_student_keys": assigned,
            })
    for s in students:
        need = int(s.get("extension_count", 0) or 0)
        if assigned_counts.get(s["student_key"], 0) != need:
            raise ValueError("Could not assign the reusable extension families fairly to every student in the selected scope.")

    conversion_requests: list[dict[str, Any]] = []
    for iid in sorted(source_by_ican, key=core.ican_sort_key):
        source = source_by_ican[iid]
        info = catalog.get(iid) or {}
        source_pool = _source_family_pool(by_ican.get(iid, []))
        conversion_requests.append({
            "slot_kind": "reassessment_mc",
            "i_can_id": iid,
            "i_can_text": str(info.get("exact_text") or ""),
            "source_family_id": source.get("family_id", ""),
            "source_teacher_question_id": source.get("teacher_question_id", ""),
            "source_family_name": source.get("family_name", ""),
            "source_family": dict(source.get("authoring_reference") or {}),
            "source_family_pool_count": len(source_pool),
            "source_family_pool_ids": [core.normalize_text(f.get("family_id")) for f in source_pool if core.normalize_text(f.get("family_id"))],
            "assigned_student_keys": [
                s["student_key"] for s in students
                if any(x.get("i_can_id") == iid for x in s.get("reassessment_slots", []))
            ],
        })

    total_mc_families = len(conversion_requests) + len(extension_requests)
    if total_mc_families > 16:
        raise ValueError(
            f"This Summative would require {total_mc_families} common MC families, but the standard answer sheet supports at most 16. "
            "Narrow the selected I Can scope and analyze again."
        )

    scope_catalog = []
    for iid in eligible:
        info = catalog.get(iid) or {}
        scope_catalog.append({
            "i_can_id": iid,
            "i_can_text": str(info.get("exact_text") or ""),
            "mastery_goal_id": str(info.get("mg_id") or re.sub(r"-IC\d{2}$", "", iid)),
            "unit": int(info.get("unit") or core.ican_sort_key(iid)[0]),
            "current_bank_family_count": len(by_ican.get(iid, [])),
        })

    return {
        "schema_version": 2,
        "representation_contract_version": 1,
        "plan_id": plan_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "course": "Algebra 1",
        "storage_unit": unit,
        "item_label": item_label,
        "custom_name": custom_name,
        "target_questions_per_student": target_questions,
        "eligible_i_cans": eligible,
        "eligible_mastery_goals": sorted({re.sub(r"-IC\d{2}$", "", x) for x in eligible}, key=lambda x: core.ican_sort_key(x + "-IC00")),
        "eligible_units": sorted({core.ican_sort_key(x)[0] for x in eligible}),
        "portfolio_roots": scan.get("portfolio_roots", []),
        "files_scanned": scan.get("files_scanned", []),
        "evidence_record_count": len(scan.get("records", [])),
        "student_count": len(students),
        "reassessment_slot_count": reassessment_total,
        "extension_slot_count": extension_total,
        "mc_conversion_request_count": len(conversion_requests),
        "extension_family_request_count": len(extension_requests),
        "temporary_family_request_count": len(conversion_requests) + len(extension_requests),
        "mc_conversion_requests": conversion_requests,
        "extension_family_requests": extension_requests,
        "scope_catalog": scope_catalog,
        "students": students,
    }


def request_payload(plan: dict[str, Any]) -> dict[str, Any]:
    students = []
    for s in plan.get("students", []):
        students.append({
            "student_key": s.get("student_key"),
            "reassessment_i_cans": [x.get("i_can_id") for x in s.get("reassessment_slots", [])],
            "extension_count": s.get("extension_count", 0),
            "secure_selected_i_cans": s.get("secure_i_cans", []),
        })
    return {
        "schema_version": 2,
        "representation_contract_version": int(plan.get("representation_contract_version", 0) or 0),
        "request_type": "algebra_summative_multiple_choice_families",
        "plan_id": plan.get("plan_id"),
        "course": plan.get("course"),
        "item_label": plan.get("item_label"),
        "custom_name": plan.get("custom_name"),
        "target_questions_per_student": plan.get("target_questions_per_student", 4),
        "eligible_i_cans": plan.get("eligible_i_cans", []),
        "scope_catalog": plan.get("scope_catalog", []),
        "mc_conversion_requests": plan.get("mc_conversion_requests", []),
        "extension_family_requests": plan.get("extension_family_requests", []),
        "students": students,
        "instructions": [
            "The teacher selected the exact eligible I Can scope. Do not assess outside that scope.",
            "For every mc_conversion_request, author ONE reusable temporary multiple-choice family for that exact I Can, using the supplied approved/current source family as the evidence architecture. The request also reports the full current Summative-eligible source-family pool for transparency; do not invent a new evidence family outside that approved pool.",
            "The multiple-choice conversion must preserve the source family's evidence job, representation demand, tool/render route, and mastery demand; downstream conversion does not reset representation authority.",
            "Use exactly four answer choices with one defensible correct answer and three misconception-based distractors.",
            "GRAPH HARD RULE: when a base or makeup exemplar requires a Cartesian/mathematical graph supported by the registered graph tool, use the packaged GRAPH_AUTHORITY/Tools/graph_tool.py. Do not hand-author coordinate SVG, CSS axes, canvas graphs, or improvised plotting styles.",
            "For every graph-bearing exemplar, generate a fresh graph asset under figures/, reference it with <img class=\"graph\" src=\"figures/...\">, and include exemplar.representation_data with asset plus generator='Tools/graph_tool.py'. Do not inline the SVG markup in student_html.",
            "If the required representation is not supported by the packaged registered tool or approved source route, fail the family rather than substituting a different representation.",
            "For EVERY returned MC family, also provide exactly two makeup_exemplars. Each makeup exemplar must be a parallel NUMBER-SWAP version of the accepted base exemplar: preserve the same context/representation/reasoning structure and only change legal numeric values or graph values needed to create a genuinely parallel item. Do not introduce a new context or a different question architecture.",
            "The first four printed forms will reuse the base exemplar with question/choice scrambling. Printed Forms 5 and 6 will use makeup_exemplars[0] and makeup_exemplars[1], respectively, with their own scrambling.",
            "For every extension_family_request, author ONE reusable multiple-choice extension/transfer family for the exact target I Can and only the assigned students listed there.",
            "Every extension MC family must also include frq_exemplar: an open-response extension version of the same evidence target for the personalized FRQ sheet. It must not contain multiple-choice options.",
            "Extensions must extend or transfer demonstrated learning; do not merely make the original direct item numerically harder.",
            "Returned families are temporary/local to this Summative. They do not enter the permanent bank unless the teacher later promotes them deliberately.",
            "Return one AI Result ZIP containing one complete summative_families.json at the ZIP root plus any required figures/ assets. Do not return a Curriculum Transfer or GitHub Transfer. The teacher imports this ZIP with Load Returned Families in Algebra 1 Tools.",
            "The Builder will require teacher Accept/Replace review before personalized Summative assembly.",
        ],
        "expected_response": {
            "schema_version": 1,
            "plan_id": plan.get("plan_id"),
            "summative_families": [
                {
                    "family_id": "TMP-SUM-...",
                    "slot_kind": "reassessment_mc or extension_mc",
                    "target_i_can_ids": ["U1-MG01-IC01"],
                    "source_family_id": "required for reassessment_mc",
                    "assigned_student_keys": ["S-..."],
                    "family_name": "...",
                    "family_purpose": "...",
                    "evidence_job": "...",
                    "student_action": "...",
                    "question_structure_id": "...",
                    "response_mode": "multiple choice",
                    "representation_mode": "...",
                    "difficulty_intent": "...",
                    "invariant": "...",
                    "variation_axes": ["..."],
                    "forbidden_variations": ["..."],
                    "fresh_instance_rule": "...",
                    "exemplar": {
                        "student_html": "<p>...</p><img class=\"graph\" src=\"figures/example.svg\"><ol class=\"choices\"><li>...</li><li>...</li><li>...</li><li>...</li></ol> when a graph is required; omit the img when no graph is required",
                        "answer": "B. ...",
                        "solution": "...",
                        "scoring_guidance": "1 point: ...",
                        "representation_data": [{"asset": "figures/example.svg", "generator": "Tools/graph_tool.py", "qa": "bounds/scale/points checked"}],
                    },
                    "makeup_exemplars": [
                        {"student_html": "<p>Parallel number-swap MC...</p><ol class=\"choices\"><li>...</li><li>...</li><li>...</li><li>...</li></ol>", "answer": "C. ...", "solution": "...", "scoring_guidance": "1 point: ..."},
                        {"student_html": "<p>Second parallel number-swap MC...</p><ol class=\"choices\"><li>...</li><li>...</li><li>...</li><li>...</li></ol>", "answer": "A. ...", "solution": "...", "scoring_guidance": "1 point: ..."}
                    ],
                    "frq_exemplar": {
                        "student_html": "Required for extension_mc only: open-response extension prompt with no answer choices.",
                        "answer": "...",
                        "solution": "...",
                        "scoring_guidance": "...",
                    },
                }
            ],
        },
    }


def state_dir(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_state" / plan_id


def write_summative_state(github_root: Path, plan: dict[str, Any]) -> Path:
    root = state_dir(github_root, plan["plan_id"])
    root.mkdir(parents=True, exist_ok=True)
    out = root / "plan.json"
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return out


def working_request_path(github_root: Path, plan_id: str) -> Path:
    return state_dir(github_root, plan_id) / f"{plan_id}_AI_MC_REQUEST.zip"


def request_path(github_root: Path, plan_id: str) -> Path:
    current = working_request_path(github_root, plan_id)
    legacy = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_requests" / f"{plan_id}_AI_MC_REQUEST.zip"
    return current if current.is_file() or not legacy.is_file() else legacy


def working_replacement_request_path(github_root: Path, plan_id: str) -> Path:
    return state_dir(github_root, plan_id) / f"{plan_id}_FAMILY_REPLACEMENT_REQUEST.zip"


def replacement_request_path(github_root: Path, plan_id: str) -> Path:
    current = working_replacement_request_path(github_root, plan_id)
    legacy = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_requests" / f"{plan_id}_FAMILY_REPLACEMENT_REQUEST.zip"
    return current if current.is_file() or not legacy.is_file() else legacy


def response_path(github_root: Path, plan_id: str) -> Path:
    return github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_families" / plan_id / "summative_families.json"


def review_path(github_root: Path, plan_id: str) -> Path:
    return state_dir(github_root, plan_id) / "family_review.json"




def _graph_authority_paths(github_root: Path) -> list[tuple[Path, str]]:
    manifest = github_root / "memories" / "Tools" / "MANIFEST.json"
    standard = github_root / "memories" / "district_tools" / "_shared" / "DISTRICT_GRAPH_RENDERING_STANDARD.md"
    if not manifest.is_file():
        raise ValueError("SUMMATIVE_GRAPH_AUTHORITY_MISSING: memories/Tools/MANIFEST.json")
    try:
        registry = json.loads(manifest.read_text(encoding="utf-8"))
        graph_rel = core.normalize_text(((registry.get("tools") or {}).get("graph_tool")))
    except Exception as exc:
        raise ValueError(f"SUMMATIVE_GRAPH_AUTHORITY_INVALID: {exc}") from exc
    if not graph_rel:
        raise ValueError("SUMMATIVE_GRAPH_AUTHORITY_MISSING: tools.graph_tool is undeclared")
    graph_tool = github_root / "memories" / graph_rel
    if not graph_tool.is_file():
        raise ValueError(f"SUMMATIVE_GRAPH_AUTHORITY_MISSING: memories/{graph_rel}")
    if not standard.is_file():
        raise ValueError("SUMMATIVE_GRAPH_AUTHORITY_MISSING: district graph rendering standard")
    return [
        (manifest, "GRAPH_AUTHORITY/Tools/MANIFEST.json"),
        (graph_tool, f"GRAPH_AUTHORITY/{graph_rel}"),
        (standard, "GRAPH_AUTHORITY/DISTRICT_GRAPH_RENDERING_STANDARD.md"),
    ]


def _write_graph_authority_bundle(zf: zipfile.ZipFile, github_root: Path) -> None:
    for src, arc in _graph_authority_paths(github_root):
        zf.write(src, arc)


def _strict_representation_contract(plan: dict[str, Any]) -> bool:
    return int(plan.get("representation_contract_version", 0) or 0) >= 1


def _graph_text(value: Any) -> bool:
    if isinstance(value, (list, tuple, dict)):
        value = json.dumps(value, sort_keys=True)
    return "graph" in core.normalize_text(value).lower()


def _family_requires_graph(req: dict[str, Any] | None, family: dict[str, Any]) -> bool:
    source = (req or {}).get("source_family") if isinstance((req or {}).get("source_family"), dict) else {}
    fields = [
        family.get("representation_mode"), family.get("representation_need"), family.get("representation_routes"),
        source.get("representation_mode"), source.get("representation_need"), source.get("representation_routes"),
    ]
    return any(_graph_text(v) for v in fields if v not in (None, "", [], {}))


def _graph_asset_refs(markup: str) -> list[str]:
    refs=[]
    for m in re.finditer(r'<img\b[^>]*?\bsrc=["\']([^"\']+)["\']', markup or "", re.I):
        src=m.group(1).strip()
        if src.startswith("figures/"):
            refs.append(src)
    return refs


def _validate_graph_exemplar(
    errors: list[str], fid: str, label: str, ex: dict[str, Any], *,
    github_root: Path | None, plan_id: str, required: bool,
) -> None:
    markup = core.normalize_text(ex.get("student_html"))
    if not markup or not required:
        return
    if re.search(r'<\s*(?:svg|canvas)\b', markup, re.I):
        errors.append(f"{fid} {label} uses an inline/improvised graph. Use the registered graph tool and a figures/ asset instead.")
    refs = _graph_asset_refs(markup)
    if not refs:
        errors.append(f"{fid} {label} requires a graph-tool figure referenced as <img src=\"figures/...\">.")
    rep = ex.get("representation_data") if isinstance(ex.get("representation_data"), list) else []
    declared = {core.normalize_text(x.get("asset")): core.normalize_text(x.get("generator")) for x in rep if isinstance(x, dict)}
    for ref in refs:
        gen = declared.get(ref, "")
        if gen != "Tools/graph_tool.py":
            errors.append(f"{fid} {label} must declare representation_data for {ref} with generator Tools/graph_tool.py.")
        if github_root is not None:
            asset = github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_families" / plan_id / ref
            if not asset.is_file():
                errors.append(f"{fid} {label} is missing installed graph asset: {ref}")


def create_request_zip(github_root: Path, plan: dict[str, Any]) -> Path:
    path = working_request_path(github_root, plan["plan_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    readme = (
        "Algebra Assessment Builder - Summative AI Multiple-Choice Request\n"
        "=================================================================\n\n"
        "Upload this ZIP to the Curriculum Build chat.\n"
        "Student names remain local; the request uses anonymous student keys.\n"
        "The teacher-selected I Can scope and Portfolio routing are locked into this request.\n"
        "AI should convert the requested approved bank families into temporary MC families and author only the requested extensions.\n"
        "If a requested family needs a mathematical graph, the required current graph authority is included under GRAPH_AUTHORITY/.\n"
        "Graph-bearing results must return graph-tool-generated figures/ assets with the family JSON; do not inline coordinate SVG.\nReturn one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\nReturn one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\nReturn one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\nReturn one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\nReturn one AI Result ZIP; do not return a Curriculum Transfer or GitHub Transfer. Import happens through Load Returned Families in Algebra 1 Tools.\n"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUMMATIVE_MC_REQUEST.json", json.dumps(request_payload(plan), indent=2) + "\n")
        zf.writestr("README.txt", readme)
        _write_graph_authority_bundle(zf, github_root)
    return path


def _family_id(family: dict[str, Any]) -> str:
    return core.normalize_text(family.get("family_id") or family.get("summative_family_id"))


def _choice_count(markup: str) -> int:
    m = re.search(r"<ol\b[^>]*class=[\"'][^\"']*\bchoices\b[^\"']*[\"'][^>]*>(.*?)</ol>", markup or "", re.I | re.S)
    return len(re.findall(r"<li\b", m.group(1), re.I)) if m else 0


def validate_response(plan: dict[str, Any], response: dict[str, Any], github_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(response, dict):
        return {"complete": False, "errors": ["Returned Summative response is not a JSON object."], "warnings": [], "families": []}
    if core.normalize_text(response.get("plan_id")) != core.normalize_text(plan.get("plan_id")):
        errors.append("Returned family response plan_id does not match this Summative plan.")
    raw_families = response.get("summative_families")
    if not isinstance(raw_families, list):
        errors.append("Returned response must contain summative_families as a list.")
        raw_families = []
    families: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, raw in enumerate(raw_families, 1):
        if not isinstance(raw, dict):
            errors.append(f"Family #{idx} is not a JSON object.")
            continue
        family = dict(raw)
        fid = _family_id(family)
        if not fid:
            errors.append(f"Family #{idx} is missing family_id.")
            continue
        if fid in seen:
            errors.append(f"Duplicate family_id: {fid}")
            continue
        seen.add(fid)
        family["family_id"] = fid
        kind = core.normalize_text(family.get("slot_kind"))
        if kind not in {"reassessment_mc", "extension_mc"}:
            errors.append(f"{fid} has invalid slot_kind: {kind or '(blank)'}")
        targets = [core.normalize_ican(x) for x in (family.get("target_i_can_ids") or [])]
        targets = [x for x in targets if x]
        family["target_i_can_ids"] = targets
        if len(targets) != 1:
            errors.append(f"{fid} must target exactly one I Can.")
        family["assigned_student_keys"] = [core.normalize_text(x) for x in (family.get("assigned_student_keys") or []) if core.normalize_text(x)]
        family["family_name"] = core.normalize_text(family.get("family_name"))
        exemplar = family.get("exemplar") if isinstance(family.get("exemplar"), dict) else {}
        family["exemplar"] = exemplar
        markup = core.normalize_text(exemplar.get("student_html"))
        if not family["family_name"]:
            errors.append(f"{fid} is missing family_name.")
        if not markup:
            errors.append(f"{fid} is missing exemplar.student_html.")
        elif _choice_count(markup) != 4:
            errors.append(f"{fid} must contain exactly four <ol class=\"choices\"> answer choices.")
        answer = core.normalize_text(exemplar.get("answer"))
        if not re.match(r"^[A-D]\s*[.):-]", answer, re.I):
            errors.append(f"{fid} exemplar.answer must begin with A-D.")
        families.append(family)

    requested_mc = {x.get("i_can_id"): x for x in plan.get("mc_conversion_requests", [])}
    returned_mc = {}
    requested_ext = {x.get("target_i_can_id"): x for x in plan.get("extension_family_requests", [])}
    returned_ext = {}
    for family in families:
        targets = family.get("target_i_can_ids") or []
        iid = targets[0] if len(targets) == 1 else ""
        if family.get("slot_kind") == "reassessment_mc":
            if iid in returned_mc:
                errors.append(f"More than one reassessment MC family was returned for {iid}.")
            returned_mc[iid] = family
            req = requested_mc.get(iid)
            if req and core.normalize_text(family.get("source_family_id")) != core.normalize_text(req.get("source_family_id")):
                errors.append(f"{family['family_id']} source_family_id must remain {req.get('source_family_id')}.")
        elif family.get("slot_kind") == "extension_mc":
            if iid in returned_ext:
                errors.append(f"More than one extension MC family was returned for {iid}.")
            returned_ext[iid] = family
            frq = family.get("frq_exemplar") if isinstance(family.get("frq_exemplar"), dict) else {}
            if requested_ext.get(iid) and not core.normalize_text(frq.get("student_html")):
                errors.append(f"{family['family_id']} must include frq_exemplar for its personalized extension slot.")
            elif core.normalize_text(frq.get("student_html")) and _choice_count(core.normalize_text(frq.get("student_html"))):
                errors.append(f"{family['family_id']} frq_exemplar must be open response, not multiple choice.")

    if _strict_representation_contract(plan):
        plan_id = core.normalize_text(plan.get("plan_id"))
        for family in families:
            targets = family.get("target_i_can_ids") or []
            iid = targets[0] if len(targets) == 1 else ""
            req = requested_mc.get(iid) if family.get("slot_kind") == "reassessment_mc" else requested_ext.get(iid)
            graph_required = _family_requires_graph(req, family)
            _validate_graph_exemplar(errors, family["family_id"], "base exemplar", family.get("exemplar") or {}, github_root=github_root, plan_id=plan_id, required=graph_required)
            makeups = family.get("makeup_exemplars") if isinstance(family.get("makeup_exemplars"), list) else []
            for n, ex in enumerate(makeups[:2], 1):
                if isinstance(ex, dict):
                    _validate_graph_exemplar(errors, family["family_id"], f"makeup exemplar {n}", ex, github_root=github_root, plan_id=plan_id, required=graph_required)
            if family.get("slot_kind") == "extension_mc":
                frq = family.get("frq_exemplar") if isinstance(family.get("frq_exemplar"), dict) else {}
                _validate_graph_exemplar(errors, family["family_id"], "FRQ exemplar", frq, github_root=github_root, plan_id=plan_id, required=graph_required and bool(core.normalize_text(frq.get("student_html"))))

    missing_mc = sorted(set(requested_mc) - set(returned_mc), key=core.ican_sort_key)
    extra_mc = sorted(set(returned_mc) - set(requested_mc), key=core.ican_sort_key)
    missing_ext = sorted(set(requested_ext) - set(returned_ext), key=core.ican_sort_key)
    extra_ext = sorted(set(returned_ext) - set(requested_ext), key=core.ican_sort_key)
    if missing_mc:
        errors.append("Missing reassessment MC family for: " + ", ".join(missing_mc))
    if extra_mc:
        warnings.append("Unrequested reassessment MC family returned for: " + ", ".join(extra_mc))
    if missing_ext:
        errors.append("Missing extension MC family for: " + ", ".join(missing_ext))
    if extra_ext:
        warnings.append("Unrequested extension MC family returned for: " + ", ".join(extra_ext))

    return {
        "complete": not errors,
        "errors": errors,
        "warnings": warnings,
        "families": families,
        "requested_family_count": int(plan.get("temporary_family_request_count", 0) or 0),
        "returned_family_count": len(families),
    }


def makeup_parallel_gaps(families: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    for family in families:
        fid = _family_id(family)
        vals = family.get("makeup_exemplars")
        valid = 0
        if isinstance(vals, list):
            for ex in vals[:2]:
                if not isinstance(ex, dict):
                    continue
                markup = core.normalize_text(ex.get("student_html"))
                answer = core.normalize_text(ex.get("answer"))
                if markup and _choice_count(markup) == 4 and re.match(r"^\s*[A-D]\s*[.):-]", answer, re.I):
                    valid += 1
        if valid < 2:
            gaps.append(fid)
    return gaps


def working_makeup_request_path(github_root: Path, plan_id: str) -> Path:
    return state_dir(github_root, plan_id) / f"{plan_id}_MAKEUP_PARALLEL_REQUEST.zip"


def create_makeup_request_zip(github_root: Path, plan_id: str) -> Path:
    plan, families = _accepted_families(github_root, plan_id)
    gaps = makeup_parallel_gaps(families)
    if not gaps:
        raise ValueError("All accepted MC families already include the two required makeup parallels.")
    requested = []
    for family in families:
        if _family_id(family) not in gaps:
            continue
        requested.append({
            "family_id": _family_id(family),
            "slot_kind": family.get("slot_kind"),
            "target_i_can_ids": family.get("target_i_can_ids", []),
            "source_family_id": family.get("source_family_id", ""),
            "family_name": family.get("family_name", ""),
            "invariant": family.get("invariant", ""),
            "variation_axes": family.get("variation_axes", []),
            "forbidden_variations": family.get("forbidden_variations", []),
            "fresh_instance_rule": family.get("fresh_instance_rule", ""),
            "base_exemplar": family.get("exemplar", {}),
        })
    payload = {
        "schema_version": 1,
        "request_type": "algebra_summative_makeup_parallel_exemplars",
        "plan_id": plan_id,
        "families_needing_makeup_parallels": requested,
        "instructions": [
            "Do not replace or rewrite the accepted base families.",
            "For each listed family, add exactly two makeup_exemplars to that same family.",
            "Each makeup exemplar must be a parallel NUMBER-SWAP version of the accepted base exemplar: same context, representation, evidence job, and reasoning structure; only legal numeric/graph values change.",
            "Each makeup exemplar must have exactly four choices, one defensible correct answer, misconception-based distractors, and answer/solution/scoring fields.",
            "If the accepted family requires a graph, use the packaged registered graph tool, generate a fresh figures/ asset, reference it with <img>, declare representation_data.generator as Tools/graph_tool.py, and never inline a coordinate SVG/canvas.",
            "Return one AI Result ZIP containing one COMPLETE summative_families.json for this same plan_id, with every existing family unchanged except for the added makeup_exemplars arrays, plus any required figures/ assets.",
        ],
    }
    path = working_makeup_request_path(github_root, plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUMMATIVE_MAKEUP_PARALLEL_REQUEST.json", json.dumps(payload, indent=2) + "\n")
        zf.writestr("README.txt", "Upload this ZIP to Curriculum Build. It only adds the two number-swap makeup exemplars required for Forms 5 and 6.\n")
        _write_graph_authority_bundle(zf, github_root)
    return path


def load_review(github_root: Path, plan_id: str) -> dict[str, Any]:
    path = review_path(github_root, plan_id)
    if not path.is_file():
        return {"schema_version": 1, "plan_id": plan_id, "decisions": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    decisions = data.get("decisions") if isinstance(data, dict) and isinstance(data.get("decisions"), dict) else {}
    return {"schema_version": 1, "plan_id": plan_id, "updated_at": data.get("updated_at", "") if isinstance(data, dict) else "", "decisions": decisions}


def create_replacement_request_zip(github_root: Path, plan: dict[str, Any], response: dict[str, Any], review: dict[str, Any]) -> Path | None:
    decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
    replace_ids = sorted(fid for fid, decision in decisions.items() if decision == "REPLACE")
    path = working_replacement_request_path(github_root, str(plan.get("plan_id", "")))
    if not replace_ids:
        if path.is_file():
            path.unlink()
        return None
    accepted_ids = sorted(fid for fid, decision in decisions.items() if decision == "ACCEPT")
    payload = {
        "schema_version": 1,
        "request_type": "algebra_summative_family_replacements",
        "plan_id": plan.get("plan_id"),
        "replace_family_ids": replace_ids,
        "accepted_family_ids": accepted_ids,
        "original_authoring_request": request_payload(plan),
        "current_response": response,
        "instructions": [
            "Replace only the families listed in replace_family_ids.",
            "Preserve every accepted family exactly as supplied in current_response.",
            "Return one AI Result ZIP containing one COMPLETE summative_families.json with accepted families plus replacements, plus any required figures/ assets. The teacher imports it with Load Returned Families.",
            "Every family must still pass the four-choice multiple-choice contract.",
            "For graph-bearing replacements, use the packaged registered graph tool and install fresh figures/ assets; never return inline coordinate SVG/CSS/canvas graphs.",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUMMATIVE_FAMILY_REPLACEMENT_REQUEST.json", json.dumps(payload, indent=2) + "\n")
        zf.writestr("README.txt", "Upload this ZIP to Curriculum Build to replace only the Summative families marked Replace.\n")
        _write_graph_authority_bundle(zf, github_root)
    return path


def save_family_review_decision(github_root: Path, plan_id: str, family_id: str, decision: str) -> dict[str, Any]:
    state = state_dir(github_root, plan_id)
    plan_path = state / "plan.json"
    if not plan_path.is_file():
        raise ValueError("Summative plan was not found.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rpath = response_path(github_root, plan_id)
    if not rpath.is_file():
        raise ValueError("Returned Summative families have not been installed yet.")
    response = json.loads(rpath.read_text(encoding="utf-8"))
    validation = validate_response(plan, response, github_root)
    if family_id != "*" and family_id not in {_family_id(f) for f in validation.get("families", [])}:
        raise ValueError("Returned family was not found.")
    if decision not in {"ACCEPT", "REPLACE"}:
        raise ValueError("decision must be ACCEPT or REPLACE.")
    review = load_review(github_root, plan_id)
    decisions = dict(review.get("decisions") or {})
    if family_id == "*":
        if decision != "ACCEPT":
            raise ValueError("Bulk review supports ACCEPT only.")
        for f in validation.get("families", []):
            decisions[_family_id(f)] = "ACCEPT"
    else:
        decisions[family_id] = decision
    review = {"schema_version": 1, "plan_id": plan_id, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "decisions": decisions}
    path = review_path(github_root, plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    create_replacement_request_zip(github_root, plan, response, review)
    return summative_status(github_root, plan_id)


def summative_status(github_root: Path, plan_id: str) -> dict[str, Any]:
    plan_path = state_dir(github_root, plan_id) / "plan.json"
    if not plan_path.is_file():
        return {"found": False}
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    req = request_path(github_root, plan_id)
    rpath = response_path(github_root, plan_id)
    response = None
    validation = None
    review = load_review(github_root, plan_id)
    if rpath.is_file():
        try:
            response = json.loads(rpath.read_text(encoding="utf-8"))
            validation = validate_response(plan, response, github_root)
        except Exception as exc:
            validation = {"complete": False, "errors": [str(exc)], "warnings": [], "families": []}
    decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
    returned_ids = [_family_id(f) for f in (validation or {}).get("families", [])]
    accepted = sum(1 for fid in returned_ids if decisions.get(fid) == "ACCEPT")
    replace = sum(1 for fid in returned_ids if decisions.get(fid) == "REPLACE")
    pending = max(0, len(returned_ids) - accepted - replace)
    replacement = replacement_request_path(github_root, plan_id)
    assembly = summative_output.load_assembly(github_root, plan_id)
    accepted_families = [dict(f) for f in (validation or {}).get("families", []) if decisions.get(_family_id(f)) == "ACCEPT"]
    makeup_gaps = makeup_parallel_gaps(accepted_families) if accepted_families else []
    if isinstance(validation, dict):
        validation["makeup_parallel_gap_count"] = len(makeup_gaps)
        validation["makeup_parallel_gap_family_ids"] = makeup_gaps
    return {
        "found": True,
        "plan": plan,
        "request_ready": req.is_file(),
        "request_name": req.name if req.is_file() else None,
        "request_url": f"/api/summative/request.zip?plan_id={plan_id}" if req.is_file() else None,
        "families_ready": rpath.is_file(),
        "family_response": response,
        "response_validation": validation,
        "family_review": {**review, "accepted_count": accepted, "replace_count": replace, "pending_count": pending},
        "replacement_request_ready": replacement.is_file(),
        "replacement_request_url": f"/api/summative/replacement-request.zip?plan_id={plan_id}" if replacement.is_file() else None,
        "assembly_ready": bool(validation and validation.get("complete") and returned_ids and accepted == len(returned_ids) and not replace and not pending),
        "makeup_parallel_gap_count": len(makeup_gaps),
        "makeup_parallel_gap_family_ids": makeup_gaps,
        "makeup_request_ready": working_makeup_request_path(github_root, plan_id).is_file(),
        "assembly": assembly,
    }


def _accepted_families(github_root: Path, plan_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan_path = state_dir(github_root, plan_id) / "plan.json"
    if not plan_path.is_file():
        raise ValueError("Summative plan was not found.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rpath = response_path(github_root, plan_id)
    if not rpath.is_file():
        raise ValueError("Returned Summative families have not been installed yet.")
    response = json.loads(rpath.read_text(encoding="utf-8"))
    validation = validate_response(plan, response, github_root)
    if not validation.get("complete"):
        raise ValueError("Returned Summative families must pass validation before assembly.")
    review = load_review(github_root, plan_id)
    decisions = review.get("decisions") if isinstance(review.get("decisions"), dict) else {}
    families = [dict(f) for f in validation.get("families", [])]
    unaccepted = [_family_id(f) for f in families if decisions.get(_family_id(f)) != "ACCEPT"]
    if unaccepted:
        raise ValueError("Accept every returned Summative family before assembly.")
    return plan, families


def assemble_summative(github_root: Path, plan_id: str) -> dict[str, Any]:
    plan, families = _accepted_families(github_root, plan_id)
    gaps = makeup_parallel_gaps(families)
    if gaps:
        raise ValueError("Makeup parallel number-swap exemplars are still needed for: " + ", ".join(gaps) + ". Save the Makeup Parallel Request, apply the returned transfer, then Load Returned Families.")
    return summative_output.write_outputs(github_root, plan, families)


def manual_adjust_summative(github_root: Path, plan_id: str, student_key: str, slot_index: int, family_id: str, instance: dict[str, Any]) -> dict[str, Any]:
    plan, families = _accepted_families(github_root, plan_id)
    return summative_output.manual_adjust(github_root, plan, families, student_key, slot_index, family_id, instance)


def load_summative_assembly(github_root: Path, plan_id: str) -> dict[str, Any] | None:
    return summative_output.load_assembly(github_root, plan_id)


def summative_output_dir(github_root: Path, plan_id: str) -> Path:
    return summative_output.output_dir(github_root, plan_id)


def summative_output_zip_path(github_root: Path, plan_id: str) -> Path:
    return summative_output.output_zip_path(github_root, plan_id)


def create_mc_library_transfer(github_root: Path, plan_id: str, layout: dict[str, Any] | None = None) -> Path:
    plan, families = _accepted_families(github_root, plan_id)
    gaps = makeup_parallel_gaps(families)
    if gaps:
        raise ValueError("Forms 5-6 makeup parallels are still missing for: " + ", ".join(gaps))
    return summative_output.create_mc_library_transfer(github_root, plan, families, layout or {})
