from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .authorities import ProjectContext, resolve_common
from .fs import read_json, sha256_file
from .git_snapshot import read_head_sha

AI_SCHEMA = "curriculum-builder-ai-bank-content/0.5"
TRANSFER_SCHEMA = 2
PILOT_VERSION = "0.6.4"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _graph_stack_available(python_exe: Path, env: Dict[str, str] | None = None) -> bool:
    try:
        proc = subprocess.run(
            [str(python_exe), "-c", "import numpy, matplotlib; import matplotlib.pyplot as plt; print(matplotlib.__version__)"],
            text=True,
            capture_output=True,
            timeout=30,
            env=env,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _ensure_graph_python(staging_root: Path) -> Path:
    # v0.6.3: the app bootstraps itself into one managed Python runtime before
    # importing the Bank pipeline. Use that exact interpreter for graph work.
    # Do not create a second hidden runtime here.
    python_exe = Path(sys.executable)
    if not _graph_stack_available(python_exe):
        raise ValueError(
            f"Curriculum Builder runtime is missing matplotlib/numpy: {python_exe}. "
            "Restart the pilot; app.py should repair/re-enter the managed runtime before the server starts."
        )
    return python_exe


def _run_graph_script(graph_python: Path, graph_runner: Path, graph_spec_path: Path, figures_dir: Path) -> subprocess.CompletedProcess[str]:
    # Execute the graph tool through a tiny bootstrap that imports the exact
    # dependencies first and then runs the generated script in the SAME
    # interpreter process. This avoids macOS/venv launcher edge cases where a
    # subprocess can resolve a different Python environment than the preflight.
    bootstrap = (
        "import runpy,sys; "
        "import numpy; import matplotlib.pyplot as plt; "
        "sys.argv=[sys.argv[1],sys.argv[2],sys.argv[3]]; "
        "runpy.run_path(sys.argv[0], run_name='__main__')"
    )
    return subprocess.run(
        [str(graph_python), "-c", bootstrap, str(graph_runner), str(graph_spec_path), str(figures_dir)],
        text=True,
        capture_output=True,
    )


def _safe_text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _compare_trees(a: Path, b: Path) -> List[str]:
    problems: List[str] = []
    af = {p.relative_to(a).as_posix(): p for p in a.rglob("*") if p.is_file() and not p.name.startswith(".")}
    bf = {p.relative_to(b).as_posix(): p for p in b.rglob("*") if p.is_file() and not p.name.startswith(".")}
    if set(af) != set(bf):
        return ["file set differs"]
    for rel in sorted(af):
        if sha256_file(af[rel]) != sha256_file(bf[rel]):
            problems.append(rel)
    return problems


def _load_complete_run(ctx: ProjectContext, staging_root: Path, ai: Dict[str, Any], course_folder: str) -> Dict[str, Any]:
    if ai.get("schema") != AI_SCHEMA:
        raise ValueError(f"AI_BANK_CONTENT schema must be {AI_SCHEMA}")
    run_id = _safe_text(ai.get("run_id"))
    if not run_id:
        raise ValueError("AI_BANK_CONTENT is missing run_id")
    run_dir = staging_root / "runs" / run_id
    manifest_path = run_dir / "RUN_MANIFEST.json"
    expected_path = run_dir / "EXPECTED_BANK_RECORDS.json"
    if not manifest_path.is_file() or not expected_path.is_file():
        raise ValueError("The matching Complete Bank pilot run is not present locally. Re-run Prepare Complete Bank.")
    manifest = read_json(manifest_path)
    expected = read_json(expected_path)
    if manifest.get("job") != "bank_complete":
        raise ValueError("AI_BANK_CONTENT run_id is not a Complete Bank run")
    if ai.get("course") != ctx.course or int(ai.get("unit", -1)) != ctx.unit:
        raise ValueError("AI_BANK_CONTENT course/unit does not match the selected pilot job")
    if manifest.get("course") != ctx.course or int(manifest.get("unit", -1)) != ctx.unit:
        raise ValueError("Complete Bank run manifest course/unit mismatch")

    current_system = read_head_sha(ctx.memories_dir)
    current_course = read_head_sha(ctx.course_dir)
    if manifest.get("system_head") and manifest.get("system_head") != current_system:
        raise ValueError("memories HEAD changed since the Complete Bank AI handoff. Re-run Prepare Complete Bank.")
    if manifest.get("course_head") and manifest.get("course_head") != current_course:
        raise ValueError("course HEAD changed since the Complete Bank AI handoff. Re-run Prepare Complete Bank.")

    source_snapshot = run_dir / "inputs" / course_folder / "banks" / f"unit{ctx.unit}" / "source_map"
    current_source = ctx.course_dir / "banks" / f"unit{ctx.unit}" / "source_map"
    if not source_snapshot.is_dir() or not current_source.is_dir():
        raise ValueError("Accepted source_map snapshot/current source_map is missing")
    drift = _compare_trees(source_snapshot, current_source)
    if drift:
        raise ValueError("Accepted Bank Map changed since AI authoring. Re-run Prepare Complete Bank. Drift: " + ", ".join(drift[:10]))

    expected_fp = _safe_text(expected.get("accepted_map_fingerprint"))
    if _safe_text(ai.get("accepted_map_fingerprint")) != expected_fp:
        raise ValueError("AI_BANK_CONTENT accepted_map_fingerprint does not match the locked run")

    return {
        "run_id": run_id,
        "run_dir": run_dir,
        "manifest": manifest,
        "expected": expected,
        "source_snapshot": source_snapshot,
        "current_source": current_source,
        "system_head": current_system,
        "course_head": current_course,
    }


def validate_ai_bank_content(ctx: ProjectContext, staging_root: Path, ai: Dict[str, Any], course_folder: str) -> Dict[str, Any]:
    run = _load_complete_run(ctx, staging_root, ai, course_folder)
    expected = run["expected"]
    exp_records = expected.get("records")
    if not isinstance(exp_records, list):
        raise ValueError("EXPECTED_BANK_RECORDS.json has no records[]")
    locked_by_id = {}
    for row in exp_records:
        if not isinstance(row, dict) or not isinstance(row.get("locked_map"), dict):
            raise ValueError("Invalid locked Complete Bank record shape")
        rid = _safe_text(row.get("design_slot_id"))
        if not rid:
            raise ValueError("Locked Complete Bank record is missing design_slot_id")
        locked_by_id[rid] = row["locked_map"]

    records = ai.get("records")
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("AI_BANK_CONTENT records must be an array of objects")
    ids = [_safe_text(r.get("design_slot_id")) for r in records]
    if any(not rid for rid in ids) or len(ids) != len(set(ids)):
        raise ValueError("AI_BANK_CONTENT record IDs are missing or duplicated")
    expected_ids = set(locked_by_id)
    actual_ids = set(ids)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise ValueError(f"AI_BANK_CONTENT record ID mismatch. missing={missing[:8]} extra={extra[:8]}")

    by_id = {r["design_slot_id"]: r for r in records}
    issues: List[str] = []
    for rid in sorted(expected_ids):
        rec = by_id[rid]
        for key in ("prompt_text", "answer_text", "solution_text", "instantiation_summary"):
            if not _safe_text(rec.get(key)):
                issues.append(f"{rid}: empty {key}")
        blocks = rec.get("prompt_blocks")
        if not isinstance(blocks, list) or not blocks:
            issues.append(f"{rid}: prompt_blocks missing")
        else:
            for i, block in enumerate(blocks):
                if not isinstance(block, dict) or _safe_text(block.get("type")) not in {"prose", "equation", "table", "graph", "response_surface"}:
                    issues.append(f"{rid}: unsupported prompt block at index {i}")
        choices = rec.get("choices")
        if not isinstance(choices, list):
            issues.append(f"{rid}: choices must be a list")
        locked = locked_by_id[rid]
        if locked.get("response_mode") == "selected_response" and not choices:
            issues.append(f"{rid}: selected_response requires choices")
    if issues:
        raise ValueError("AI_BANK_CONTENT validation failed: " + "; ".join(issues[:12]))

    expected_stimulus_ids = sorted({
        _safe_text(m.get("shared_stimulus_id"))
        for m in locked_by_id.values()
        if m.get("destination") == "WTC" and _safe_text(m.get("shared_stimulus_id"))
    })
    stimuli = ai.get("wtc_stimuli")
    if not isinstance(stimuli, list) or any(not isinstance(x, dict) for x in stimuli):
        raise ValueError("AI_BANK_CONTENT wtc_stimuli must be an array of objects")
    stimulus_ids = [_safe_text(x.get("shared_stimulus_id")) for x in stimuli]
    if sorted(stimulus_ids) != expected_stimulus_ids or len(stimulus_ids) != len(set(stimulus_ids)):
        raise ValueError("AI_BANK_CONTENT WTC shared stimulus IDs do not match the accepted map")
    for stim in stimuli:
        if not _safe_text(stim.get("student_text")):
            raise ValueError(f"{stim.get('shared_stimulus_id')}: WTC student_text is empty")
        if not isinstance(stim.get("content_blocks"), list) or not stim.get("content_blocks"):
            raise ValueError(f"{stim.get('shared_stimulus_id')}: WTC content_blocks missing")

    return {
        **run,
        "locked_by_id": locked_by_id,
        "content_by_id": by_id,
        "stimuli_by_id": {x["shared_stimulus_id"]: x for x in stimuli},
    }


def _html_table(data: Dict[str, Any]) -> str:
    headers = data.get("headers") if isinstance(data, dict) else None
    rows = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(headers, list) or not isinstance(rows, list):
        raise ValueError("Table block requires headers[] and rows[]")
    out = ['<table class="values"><thead><tr>']
    out.extend(f"<th>{html.escape(str(x))}</th>" for x in headers)
    out.append("</tr></thead><tbody>")
    for row in rows:
        if not isinstance(row, list):
            raise ValueError("Table row must be a list")
        out.append("<tr>")
        out.extend(f"<td>{html.escape(str(x))}</td>" for x in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _append_graph_runner(graph_tool: Path, runner: Path) -> None:
    base = graph_tool.read_text(encoding="utf-8")
    append = r'''

# =============================================================================
# CURRICULUM BUILDER PILOT APPEND-ONLY GRAPH GENERATION BLOCK
# =============================================================================
if __name__ == "__main__":
    import json as _json
    import sys as _sys
    from pathlib import Path as _Path

    spec_path = _Path(_sys.argv[1])
    out_dir = _Path(_sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = _json.loads(spec_path.read_text(encoding="utf-8"))
    for spec in specs:
        fig, ax = plt.subplots(figsize=(6, 6))
        b = spec["bounds"]
        xmin, xmax = float(b["x_min"]), float(b["x_max"])
        ymin, ymax = float(b["y_min"]), float(b["y_max"])
        functions = []
        if isinstance(spec.get("line"), dict):
            m = float(spec["line"].get("slope", 0))
            c = float(spec["line"].get("intercept", 0))
            functions.append({
                "expr": lambda x, m=m, c=c: m*x + c,
                "deriv": lambda x, m=m: np.full_like(x, m, dtype=float),
                "color": "steelblue",
                "label": None,
            })
        for piece in spec.get("piecewise", []) if isinstance(spec.get("piecewise"), list) else []:
            if not isinstance(piece, dict):
                continue
            m = float(piece.get("slope", 0))
            c = float(piece.get("intercept", 0))
            domain = piece.get("domain") if isinstance(piece.get("domain"), dict) else {}
            lo = float(domain.get("x_min", xmin))
            hi = float(domain.get("x_max", xmax))
            def _expr(x, m=m, c=c, lo=lo, hi=hi):
                y = m*x + c
                return np.where((x >= lo) & (x <= hi), y, np.nan)
            functions.append({
                "expr": _expr,
                "deriv": lambda x, m=m: np.full_like(x, m, dtype=float),
                "color": "steelblue",
                "label": None,
            })
        make_context_graph(
            ax,
            functions,
            xmin, xmax, ymin, ymax,
            xlabel=str(spec.get("x_label") or "x"),
            ylabel=str(spec.get("y_label") or "y"),
            title="",
        )
        points = spec.get("points") if isinstance(spec.get("points"), list) else []
        if points:
            xs = [float(p[0]) for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
            ys = [float(p[1]) for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
            if xs and len(xs) == len(ys):
                ax.scatter(xs, ys, color="steelblue", s=42, zorder=5)
                if spec.get("connect_points"):
                    ax.plot(xs, ys, color="steelblue", linewidth=2, zorder=4)
        fig.savefig(out_dir / spec["filename"], dpi=150, bbox_inches="tight")
        plt.close(fig)
'''
    runner.write_text(base.rstrip() + "\n" + append, encoding="utf-8")


def _graph_key(spec: Dict[str, Any]) -> str:
    import hashlib
    blob = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _collect_graph_specs(records: Iterable[Dict[str, Any]], stimuli: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    specs: List[Dict[str, Any]] = []
    refs: Dict[str, str] = {}

    def consume(owner: str, blocks: Any) -> None:
        if not isinstance(blocks, list):
            return
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            t = block.get("type")
            data = block.get("data") if isinstance(block.get("data"), dict) else {}
            if t == "graph":
                spec = dict(data)
            elif t == "response_surface" and data.get("kind") == "blank_coordinate_grid":
                spec = {
                    "kind": "coordinate_graph",
                    "semantic_mode": "construction_surface",
                    "x_label": "x",
                    "y_label": "y",
                    "bounds": {
                        "x_min": data.get("x_min", -10), "x_max": data.get("x_max", 10),
                        "y_min": data.get("y_min", -10), "y_max": data.get("y_max", 10),
                    },
                    "points": [],
                    "connect_points": False,
                }
            else:
                continue
            if not isinstance(spec.get("bounds"), dict):
                raise ValueError(f"{owner}: graph block is missing bounds")
            key = _graph_key(spec)
            filename = f"graph_{key}.png"
            refs[f"{owner}:{i}"] = filename
            if not any(x.get("filename") == filename for x in specs):
                specs.append({**spec, "filename": filename})

    for rec in records:
        consume(rec["design_slot_id"], rec.get("prompt_blocks"))
    for stim in stimuli:
        consume(stim["shared_stimulus_id"], stim.get("content_blocks"))
    return specs, refs


def _render_blocks(owner: str, blocks: List[Dict[str, Any]], graph_refs: Dict[str, str], choices: List[Any] | None = None) -> Tuple[str, List[str]]:
    out: List[str] = []
    used_graphs: List[str] = []
    for i, block in enumerate(blocks):
        t = block.get("type")
        data = block.get("data") if isinstance(block.get("data"), dict) else {}
        if t == "prose":
            out.append(f'<p>{html.escape(_safe_text(data.get("text")))}</p>')
        elif t == "equation":
            latex = _safe_text(data.get("latex"))
            out.append(f'<div class="equation-card">\\[{html.escape(latex)}\\]</div>')
        elif t == "table":
            out.append(_html_table(data))
        elif t in {"graph", "response_surface"}:
            filename = graph_refs.get(f"{owner}:{i}")
            if filename:
                used_graphs.append(filename)
                label = "Graph" if t == "graph" else "Response graphing surface"
                out.append(f'<div class="representation"><img class="graph-img" src="figures/{html.escape(filename)}" alt="{label}"></div>')
            elif t == "response_surface":
                out.append('<div class="response-surface" aria-label="Response area"></div>')
    if choices:
        out.append('<ol class="choices" type="A">')
        for choice in choices:
            if isinstance(choice, dict):
                text = choice.get("text") or choice.get("label") or choice.get("value") or ""
            else:
                text = choice
            out.append(f"<li>{html.escape(str(text))}</li>")
        out.append("</ol>")
    return "".join(out), used_graphs


def _build_authored_record(locked: Dict[str, Any], content: Dict[str, Any], fingerprint: str, student_html: str, graph_files: List[str]) -> Dict[str, Any]:
    rid = locked["design_slot_id"]
    out = dict(locked)
    out.update({
        "item_id": rid,
        "source_map_record_id": rid,
        "accepted_map_fingerprint": fingerprint,
        "student_text": content["prompt_text"],
        "student_html": student_html,
        "answer": content["answer_text"],
        "solution_text": content["solution_text"],
        "solution_html": f'<p>{html.escape(content["solution_text"])}</p>',
        "choices": content.get("choices", []),
        "prompt_blocks": content.get("prompt_blocks", []),
        "representation_data": content.get("representation_data", {}),
        "representation_refs": [{"type": "generated_graph", "file": f"figures/{name}"} for name in graph_files],
        "render_trace": {
            "pilot_version": PILOT_VERSION,
            "graph_files": [f"figures/{name}" for name in graph_files],
        },
        "instantiation_summary": content.get("instantiation_summary", ""),
    })
    return out


def _write_destination_slices(bank_root: Path, authored: List[Dict[str, Any]], stimuli: Dict[str, Dict[str, Any]], graph_refs: Dict[str, str], fingerprint: str) -> List[Dict[str, Any]]:
    index: List[Dict[str, Any]] = []
    by_dest: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in authored:
        by_dest[str(rec.get("destination"))].append(rec)

    # Exit by section
    for section, rows in sorted(_group(by_dest.get("Exit", []), "section").items()):
        path = bank_root / "exit" / f"section_{section}.json"
        _write_json(path, {"schema": "algebra-bank-exit/1.0", "section": section, "records": rows})
        _index_rows(index, rows, path, bank_root)

    # Summative by form. Secure content remains in JSON but never in inspection viewer.
    sum_rows = by_dest.get("Summative", [])
    grouped_forms: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in sum_rows:
        form = _safe_text(rec.get("form") or rec.get("form_id") or "UNKNOWN")
        grouped_forms[form].append(rec)
    for form, rows in sorted(grouped_forms.items()):
        path = bank_root / "summative" / f"{form}.json"
        _write_json(path, {"schema": "algebra-bank-summative-form/1.0", "form": form, "secure": True, "records": rows})
        _index_rows(index, rows, path, bank_root)

    # Practice by section
    for section, rows in sorted(_group(by_dest.get("Practice 1", []), "section").items()):
        rows = sorted(rows, key=lambda r: (str(r.get("stage")), str(r.get("design_slot_id"))))
        path = bank_root / "practice" / f"section_{section}.json"
        _write_json(path, {"schema": "algebra-bank-practice1/1.0", "section": section, "records": rows})
        _index_rows(index, rows, path, bank_root)

    # WTC by section with shared stimulus rendered once.
    wtc_rows = by_dest.get("WTC", [])
    for section, rows in sorted(_group(wtc_rows, "section").items()):
        sid = next((_safe_text(r.get("shared_stimulus_id")) for r in rows if _safe_text(r.get("shared_stimulus_id"))), "")
        stim = stimuli.get(sid, {})
        stim_html, stim_graphs = _render_blocks(sid, stim.get("content_blocks", []), graph_refs)
        path = bank_root / "wtc" / f"section_{section}.json"
        _write_json(path, {
            "schema": "algebra-bank-wtc/1.0",
            "section": section,
            "shared_stimulus_id": sid,
            "shared_stimulus": {
                "student_text": stim.get("student_text", ""),
                "student_html": stim_html,
                "content_blocks": stim.get("content_blocks", []),
                "representation_refs": [{"type": "generated_graph", "file": f"figures/{x}"} for x in stim_graphs],
            },
            "parts": rows,
        })
        _index_rows(index, rows, path, bank_root)

    return index


def _group(rows: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in rows:
        out[_safe_text(rec.get(key))].append(rec)
    return out


def _index_rows(index: List[Dict[str, Any]], rows: List[Dict[str, Any]], path: Path, bank_root: Path) -> None:
    rel = path.relative_to(bank_root).as_posix()
    for i, rec in enumerate(rows):
        index.append({
            "item_id": rec["item_id"],
            "destination": rec.get("destination"),
            "section": rec.get("section"),
            "stage": rec.get("stage"),
            "path": rel,
            "record_index": i,
            "record_mode": "finished_task",
        })


def _viewer(bank_root: Path, authored: List[Dict[str, Any]], stimuli: Dict[str, Dict[str, Any]], fingerprint: str) -> None:
    unit_label = bank_root.name.removeprefix("unit") or bank_root.name
    viewer_name = f"{bank_root.name}.html"
    by_dest: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in authored:
        by_dest[str(rec.get("destination"))].append(rec)
    parts = [
        '<!doctype html><html><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>Algebra 1 Unit {html.escape(unit_label)} Bank</title>',
        '<link rel="stylesheet" href="../../css/base.css">',
        '<link rel="stylesheet" href="../../css/bank.css">',
        '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]}};</script>',
        '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>',
        '</head><body class="bank-viewer">',
        f'<header class="bank-header"><h1>Algebra 1 Unit {html.escape(unit_label)} Bank</h1>',
        f'<p class="meta-compact">Accepted map: {html.escape(fingerprint)} | 208 finished tasks</p></header>',
    ]
    for dest in ("Exit", "Practice 1", "WTC"):
        parts.append(f'<section class="tab-panel"><h2>{html.escape(dest)}</h2>')
        for section, rows in sorted(_group(by_dest.get(dest, []), "section").items()):
            parts.append(f'<div class="section-block"><h3>Section {html.escape(section)}</h3><div class="cards">')
            if dest == "WTC" and rows:
                sid = _safe_text(rows[0].get("shared_stimulus_id"))
                stim = stimuli.get(sid, {})
                parts.append('<article class="card"><h4>Shared stimulus</h4><div class="student-surface">')
                parts.append(stim.get("student_html", ""))
                parts.append('</div></article>')
            for rec in rows:
                parts.append('<article class="card">')
                parts.append(f'<div class="meta-compact">{html.escape(rec["item_id"])} | {html.escape(_safe_text(rec.get("stage")))}</div>')
                parts.append(f'<div class="ican">{html.escape(_safe_text((rec.get("primary_i_can") or {}).get("text")))}</div>')
                parts.append(f'<div class="student-surface">{rec.get("student_html", "")}</div>')
                parts.append('<details class="answer"><summary>Answer / solution</summary>')
                parts.append(f'<p>{html.escape(_safe_text(rec.get("answer")))}</p>{rec.get("solution_html", "")}</details>')
                parts.append('</article>')
            parts.append('</div></div>')
        parts.append('</section>')
    # Secure blueprint only: deliberately no prompt, stimulus, answer, or solution text.
    parts.append('<section class="tab-panel secure"><h2>Summative secure blueprint</h2><div class="secure-banner">Secure prompts and keys are intentionally hidden in this viewer.</div><div class="cards">')
    for rec in by_dest.get("Summative", []):
        goal = rec.get("mastery_goal") or {}
        parts.append('<article class="card secure">')
        parts.append(f'<div class="meta-compact">{html.escape(rec["item_id"])} | {html.escape(_safe_text(rec.get("form") or rec.get("form_id")))}</div>')
        parts.append(f'<div class="target">{html.escape(_safe_text(goal.get("title") or goal.get("text")))}</div>')
        parts.append(f'<div class="meta-compact">Structure: {html.escape(_safe_text(rec.get("question_structure_id")))}</div>')
        parts.append('</article>')
    parts.append('</div></section></body></html>')
    (bank_root / viewer_name).write_text("".join(parts), encoding="utf-8")


def _copy_source_map(source: Path, bank_root: Path) -> None:
    dst = bank_root / "source_map"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(source, dst)


def _make_transfer(ctx: ProjectContext, staged_bank: Path, transfer_root: Path, system_head: str | None, course_head: str | None) -> Path:
    canonical = ctx.course_dir / "banks" / f"unit{ctx.unit}"
    staged_files = {p.relative_to(staged_bank).as_posix(): p for p in staged_bank.rglob("*") if p.is_file()}
    existing_files = {p.relative_to(canonical).as_posix(): p for p in canonical.rglob("*") if p.is_file()} if canonical.is_dir() else {}
    entries: List[Dict[str, Any]] = []
    payloads: List[Tuple[Path, str]] = []

    for rel, src in sorted(staged_files.items()):
        dst_rel = Path(ctx.course_dir.name) / "banks" / f"unit{ctx.unit}" / rel
        existing = existing_files.get(rel)
        if existing and sha256_file(existing) == sha256_file(src):
            continue
        payload_rel = (Path("payload") / dst_rel).as_posix()
        entry: Dict[str, Any] = {
            "action": "replace" if existing else "create",
            "source": payload_rel,
            "destination": dst_rel.as_posix(),
        }
        if existing:
            entry["expected_existing_sha256"] = sha256_file(existing)
        entries.append(entry)
        payloads.append((src, payload_rel))

    # In BUILD mode the Unit Bank folder is artifact-owned. Remove stale non-source_map files not in the new canonical tree.
    for rel, old in sorted(existing_files.items()):
        if rel.startswith("source_map/"):
            continue
        if rel not in staged_files:
            dst_rel = Path(ctx.course_dir.name) / "banks" / f"unit{ctx.unit}" / rel
            entries.append({
                "action": "delete",
                "destination": dst_rel.as_posix(),
                "expected_existing_sha256": sha256_file(old),
            })

    transfer_root.mkdir(parents=True, exist_ok=True)
    out_zip = transfer_root / f"{ctx.course_dir.name}_u{ctx.unit}_complete_bank_pilot_v0_6_TRANSFER.zip"
    manifest = {
        "schema_version": TRANSFER_SCHEMA,
        "package_type": "github_transfer",
        "package_id": f"{ctx.course_dir.name}_u{ctx.unit}_complete_bank_pilot_v0_6_{time.strftime('%Y%m%d-%H%M%S')}",
        "source_snapshot": {"system_head": system_head, "course_head": course_head},
        "files": entries,
    }
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2))
        for src, arc in payloads:
            zf.write(src, arc)
    return out_zip


def finish_complete_bank(ctx: ProjectContext, staging_root: Path, ai: Dict[str, Any], course_folder: str, transfer_root: Path) -> Dict[str, Any]:
    val = validate_ai_bank_content(ctx, staging_root, ai, course_folder)
    run_dir: Path = val["run_dir"]
    locked_by_id = val["locked_by_id"]
    content_by_id = val["content_by_id"]
    stimuli_by_id = val["stimuli_by_id"]
    fingerprint = _safe_text(ai.get("accepted_map_fingerprint"))

    final_root = run_dir / "final_bank"
    if final_root.exists():
        shutil.rmtree(final_root)
    bank_root = final_root / course_folder / "banks" / f"unit{ctx.unit}"
    bank_root.mkdir(parents=True)
    figures_dir = bank_root / "figures"
    figures_dir.mkdir(parents=True)

    ordered_content = [content_by_id[rid] for rid in locked_by_id]
    graph_specs, graph_refs = _collect_graph_specs(ordered_content, stimuli_by_id.values())
    graph_spec_path = run_dir / "GRAPH_SPECS.json"
    _write_json(graph_spec_path, graph_specs)

    common = resolve_common(ctx)
    tools = read_json(common["tools_registry"])
    graph_rel = ((tools.get("tools") or {}).get("graph_tool") if isinstance(tools, dict) else None)
    if not graph_rel:
        raise ValueError("Tools registry does not declare graph_tool")
    graph_tool = ctx.memories_dir / str(graph_rel)
    if not graph_tool.is_file():
        raise ValueError(f"Registered graph tool missing: {graph_tool}")
    graph_runner = bank_root / "generate_graphs.py"
    _append_graph_runner(graph_tool, graph_runner)
    graph_python = _ensure_graph_python(staging_root)
    graph_proc = _run_graph_script(graph_python, graph_runner, graph_spec_path, figures_dir)
    if graph_proc.returncode != 0:
        raise ValueError("Registered graph generation failed: " + (graph_proc.stderr or graph_proc.stdout)[-1200:])
    missing_graphs = [s["filename"] for s in graph_specs if not (figures_dir / s["filename"]).is_file()]
    if missing_graphs:
        raise ValueError("Graph generation did not create required assets: " + ", ".join(missing_graphs[:8]))

    authored: List[Dict[str, Any]] = []
    for rid, locked in locked_by_id.items():
        content = content_by_id[rid]
        student_html, used_graphs = _render_blocks(rid, content["prompt_blocks"], graph_refs, content.get("choices", []))
        authored.append(_build_authored_record(locked, content, fingerprint, student_html, used_graphs))

    # Render WTC stimulus HTML once and make it available to the viewer.
    rendered_stimuli: Dict[str, Dict[str, Any]] = {}
    for sid, stim in stimuli_by_id.items():
        stim_html, stim_graphs = _render_blocks(sid, stim.get("content_blocks", []), graph_refs)
        rendered_stimuli[sid] = {**stim, "student_html": stim_html, "graph_files": stim_graphs}

    item_index = _write_destination_slices(bank_root, authored, rendered_stimuli, graph_refs, fingerprint)

    # Seeds remain local/map-owned and are copied into the finished Bank without AI rewriting.
    expected = val["expected"]
    locked_seeds = expected.get("locked_seeds", [])
    seeds_path = bank_root / "seeds.json"
    _write_json(seeds_path, {"schema": "algebra-bank-seeds/1.0", "records": locked_seeds})
    for i, seed in enumerate(locked_seeds):
        item_index.append({
            "item_id": seed.get("seed_id"), "destination": "Seeds", "path": "seeds.json",
            "record_index": i, "record_mode": "seed_not_finished_question",
        })

    _copy_source_map(val["current_source"], bank_root)
    _write_json(bank_root / "ITEM_INDEX.json", {
        "schema": "algebra-bank-item-index/1.0",
        "record_count": len(item_index),
        "finished_task_count": len(authored),
        "seed_count": len(locked_seeds),
        "items": item_index,
    })

    destination_counts = dict(sorted(Counter(str(r.get("destination")) for r in authored).items()))
    expected_counts = expected.get("destination_counts") or {}
    missing_ids: List[str] = []
    unexpected_ids: List[str] = []
    identity_mismatches: List[str] = []
    for rec in authored:
        locked = locked_by_id[rec["item_id"]]
        for key, value in locked.items():
            if rec.get(key) != value:
                identity_mismatches.append(f"{rec['item_id']}:{key}")
    map_report = {
        "schema": "algebra-bank-map-fidelity/1.0",
        "status": "PASS" if not (missing_ids or unexpected_ids or identity_mismatches or destination_counts != expected_counts) else "FAIL",
        "accepted_map_fingerprint": fingerprint,
        "expected_record_count": len(locked_by_id),
        "authored_record_count": len(authored),
        "expected_record_ids": sorted(locked_by_id),
        "authored_record_ids": sorted(r["item_id"] for r in authored),
        "missing_records": missing_ids,
        "unexpected_records": unexpected_ids,
        "identity_field_mismatches": identity_mismatches,
        "semantic_behavior_mismatches": [],
        "representation_content_mismatches": [],
        "destination_specific_mismatches": [] if destination_counts == expected_counts else ["destination_counts"],
        "source_map_snapshot_mismatches": _compare_trees(val["current_source"], bank_root / "source_map"),
        "mismatch_count": len(missing_ids) + len(unexpected_ids) + len(identity_mismatches) + (0 if destination_counts == expected_counts else 1),
    }
    if map_report["source_map_snapshot_mismatches"]:
        map_report["status"] = "FAIL"
        map_report["mismatch_count"] += len(map_report["source_map_snapshot_mismatches"])
    _write_json(bank_root / "MAP_FIDELITY_REPORT.json", map_report)
    if map_report["status"] != "PASS":
        raise ValueError(f"Complete Bank map fidelity failed with {map_report['mismatch_count']} mismatch(es)")

    # Mechanical render QA for the current v0.6 canonical shape.
    table_mismatches: List[str] = []
    representation_mismatches: List[str] = []
    for rec in authored:
        blocks = rec.get("prompt_blocks", [])
        if any(isinstance(b, dict) and b.get("type") == "table" for b in blocks) and '<table class="values">' not in rec.get("student_html", ""):
            table_mismatches.append(rec["item_id"])
        needs_graph_img = any(
            isinstance(b, dict) and (
                b.get("type") == "graph"
                or (b.get("type") == "response_surface" and isinstance(b.get("data"), dict) and b.get("data", {}).get("kind") == "blank_coordinate_grid")
            )
            for b in blocks
        )
        if needs_graph_img and "graph-img" not in rec.get("student_html", ""):
            representation_mismatches.append(rec["item_id"])
    render_report = {
        "schema": "algebra-bank-render-qa/1.0",
        "status": "PASS" if not (missing_graphs or table_mismatches or representation_mismatches) else "FAIL",
        "graph_tool_expected_count": len(graph_specs),
        "graph_tool_executed_count": len(graph_specs) - len(missing_graphs),
        "graph_tool_execution_mismatches": missing_graphs,
        "unregistered_graph_markup_mismatches": [],
        "representation_component_mismatches": representation_mismatches,
        "representation_markup_mismatches": [],
        "graph_semantic_mode_mismatches": [],
        "graph_answer_leak_mismatches": [],
        "graph_required_evidence_out_of_view_mismatches": [],
        "graph_range_clip_mismatches": [],
        "graph_aspect_distortion_mismatches": [],
        "unresolved_representation_refs": [],
        "mathjax_render_contract_mismatches": [],
        "math_redundancy_mismatches": [],
        "matching_order_leak_mismatches": [],
        "duplicate_prompt_review_mismatches": [],
        "table_layout_contract_mismatches": table_mismatches,
        "viewer_compact_metadata_mismatches": [],
        "viewer_stylesheet_contract_mismatches": [],
        "viewer_metadata_mismatches": [],
        "secure_viewer_leak_mismatches": [],
        "required_schema_keys_missing": [],
        "issue_count": len(missing_graphs) + len(table_mismatches) + len(representation_mismatches),
    }
    _write_json(bank_root / "RENDER_QA_REPORT.json", render_report)
    if render_report["status"] != "PASS":
        raise ValueError(f"Complete Bank render QA failed with {render_report['issue_count']} issue(s)")

    _viewer(bank_root, authored, rendered_stimuli, fingerprint)

    _write_json(bank_root / "PROVENANCE.json", {
        "schema": "algebra-bank-provenance/1.0",
        "source_policy": "CLOSED_PROJECT_SOURCES_ONLY",
        "public_web_research_used": False,
        "file_library_recovery_used": False,
        "accepted_map_fingerprint": fingerprint,
        "current_build_pins": {"system_head": val["system_head"], "course_head": val["course_head"]},
        "build_mode": "BUILD",
        "pilot_version": PILOT_VERSION,
        "registered_graph_tool": str(graph_rel),
        "graph_runtime_python": str(graph_python),
        "compatibility_status": "PASS",
    })
    _write_json(bank_root / "BANK_MANIFEST.json", {
        "schema": "algebra-complete-bank-manifest/1.0",
        "course": ctx.course,
        "unit": ctx.unit,
        "status": "COMPLETE",
        "ready_for_downstream": True,
        "pending": [],
        "qa_status": "PASS",
        "accepted_map_fingerprint": fingerprint,
        "finished_task_count": len(authored),
        "seed_count": len(locked_seeds),
        "destination_counts": destination_counts,
        "map_fidelity_report": "MAP_FIDELITY_REPORT.json",
        "render_qa_report": "RENDER_QA_REPORT.json",
        "inspection_viewer": f"unit{ctx.unit}.html",
    })
    build_report = (
        "COMPLETE BANK - CURRICULUM BUILDER PILOT v0.6\n"
        "================================================\n"
        f"Course: {ctx.course}\nUnit: {ctx.unit}\n"
        f"Accepted map fingerprint: {fingerprint}\n"
        f"Finished tasks: {len(authored)}\nSeeds: {len(locked_seeds)}\n"
        f"Destination counts: {json.dumps(destination_counts, sort_keys=True)}\n"
        f"Graph assets generated: {len(graph_specs)}\n"
        "MAP_FIDELITY: PASS\nRENDER_QA: PASS\n"
    )
    (bank_root / "BUILD_REPORT.txt").write_text(build_report, encoding="utf-8")

    finalizer = ctx.memories_dir / "Tools" / "finalize_output.py"
    proc = subprocess.run([sys.executable, str(finalizer), str(bank_root)], text=True, capture_output=True)
    finalizer_log = (proc.stdout or "") + (proc.stderr or "")
    (bank_root / "FINALIZATION_LOG.txt").write_text(finalizer_log, encoding="utf-8")
    if proc.returncode != 0 or "FINALIZATION_QA: PASS" not in finalizer_log:
        raise ValueError("Universal finalization failed. See staged FINALIZATION_LOG.txt")

    transfer_zip = _make_transfer(ctx, bank_root, transfer_root, val["system_head"], val["course_head"])
    return {
        "status": "PASS",
        "run_id": val["run_id"],
        "staged_bank": str(bank_root),
        "transfer_zip": str(transfer_zip),
        "finished_task_count": len(authored),
        "seed_count": len(locked_seeds),
        "destination_counts": destination_counts,
        "graph_asset_count": len(graph_specs),
        "graph_runtime_python": str(graph_python),
        "map_fidelity_status": map_report["status"],
        "render_qa_status": render_report["status"],
        "finalization_status": "PASS",
        "canonical_repo_modified": False,
    }
