#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import checkpoint_engine
import summative_engine
import summative_output
import result_import

MAX_BODY = 30 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(value: str, fallback: str = "item") -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "").strip()).strip("_").lower()
    return value or fallback


def safe_filename(value: str, fallback: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip()).strip("._")
    return stem or fallback


def _applescript_string(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\"')


def save_request_copy_with_dialog(source: Path, github_root: Path, prompt: str) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(f"Request ZIP was not found: {source}")
    request_dir = github_root / "_curriculum_transfers" / "requests"
    request_dir.mkdir(parents=True, exist_ok=True)
    default_folder = _applescript_string(str(request_dir) + "/")
    default_name = _applescript_string(source.name)
    safe_prompt = _applescript_string(prompt)
    script = (
        'try\n'
        f'set defaultFolder to POSIX file "{default_folder}" as alias\n'
        f'set chosenFile to choose file name with prompt "{safe_prompt}" default name "{default_name}" default location defaultFolder\n'
        'return POSIX path of chosenFile\n'
        'on error number -128\n'
        'return ""\n'
        'end try'
    )
    proc = subprocess.run(["/usr/bin/osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"Could not open the macOS Save dialog: {detail}")
    chosen = proc.stdout.strip()
    if not chosen:
        return {"ok": True, "cancelled": True}
    destination = Path(chosen).expanduser()
    if destination.suffix.lower() != ".zip":
        destination = destination.with_name(destination.name + ".zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {"ok": True, "cancelled": False, "path": str(destination), "name": destination.name}


def save_transfer_copy_with_dialog(source: Path, github_root: Path, prompt: str) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(f"Transfer ZIP was not found: {source}")
    transfer_dir = github_root / "_curriculum_transfers" / "downloads"
    transfer_dir.mkdir(parents=True, exist_ok=True)
    default_folder = _applescript_string(str(transfer_dir) + "/")
    default_name = _applescript_string(source.name)
    safe_prompt = _applescript_string(prompt)
    script = (
        'try\n'
        f'set defaultFolder to POSIX file "{default_folder}" as alias\n'
        f'set chosenFile to choose file name with prompt "{safe_prompt}" default name "{default_name}" default location defaultFolder\n'
        'return POSIX path of chosenFile\n'
        'on error number -128\n'
        'return ""\n'
        'end try'
    )
    proc = subprocess.run(["/usr/bin/osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"Could not open the macOS Save dialog: {detail}")
    chosen = proc.stdout.strip()
    if not chosen:
        return {"ok": True, "cancelled": True}
    destination = Path(chosen).expanduser()
    if destination.suffix.lower() != ".zip":
        destination = destination.with_name(destination.name + ".zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {"ok": True, "cancelled": False, "path": str(destination), "name": destination.name}


def current_marker(product_dir: str, item_slug: str) -> str:
    return f"assessment-builder:{product_dir}:{item_slug}"


def update_library_index(raw: str, product: str, item_label: str, custom_name: str, item_slug: str, versions: list[dict[str, Any]], combined_file: str | None = None) -> str:
    if product == "Practice":
        section_id = "practices"
        product_dir = "practices"
    elif product == "Quick Check":
        section_id = "quick-checks"
        product_dir = "quick_checks"
    else:
        raise ValueError(f"Teacher Library saving is not enabled for {product} yet.")

    marker = current_marker(product_dir, item_slug)
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    raw = re.sub(re.escape(start) + r".*?" + re.escape(end), "", raw, flags=re.S)

    display = item_label.strip() or "Untitled"
    if custom_name.strip():
        display += " " + custom_name.strip()
    elif product not in display:
        display += " " + product

    pieces = []
    for v in versions:
        n = int(v["version"])
        student = html.escape(v["student_file"], quote=True)
        key = html.escape(v["key_file"], quote=True)
        rel_base = f"builder/{product_dir}/{item_slug}/"
        pieces.append(
            f'<strong>V{n}</strong> '
            f'<a href="{rel_base}{student}" target="_blank" rel="noopener">Student</a> · '
            f'<a href="{rel_base}{key}" target="_blank" rel="noopener">Key</a>'
        )
    if combined_file:
        combined = html.escape(combined_file, quote=True)
        rel_base = f"builder/{product_dir}/{item_slug}/"
        pieces.insert(0, f'<strong>All Versions</strong> <a href="{rel_base}{combined}" target="_blank" rel="noopener">Print All</a>')
    block = f'{start}<li class="builder-item"><strong>{html.escape(display)}</strong> — ' + " &nbsp; | &nbsp; ".join(pieces) + f"</li>{end}"

    section_re = re.compile(rf'(<section\s+id="{re.escape(section_id)}"[^>]*>)(.*?)(</section>)', re.S)
    m = section_re.search(raw)
    if not m:
        raise ValueError(f"Teacher Library section #{section_id} was not found.")
    head, body, tail = m.group(1), m.group(2), m.group(3)

    if section_id == "practices":
        body = re.sub(r'<p\s+class="placeholder">Builder-created Unit 1 practices will appear here\.[^<]*</p>', '', body, flags=re.S)

    ul = re.search(r"<ul>(.*?)</ul>", body, flags=re.S)
    if ul:
        new_ul = "<ul>" + ul.group(1).rstrip() + block + "</ul>"
        body = body[:ul.start()] + new_ul + body[ul.end():]
    else:
        body = body.rstrip() + f"<ul>{block}</ul>"
    return raw[:m.start()] + head + body + tail + raw[m.end():]


def write_files(base: Path, versions: list[dict[str, Any]], manifest: dict[str, Any], combined: dict[str, str] | None = None) -> None:
    base.mkdir(parents=True, exist_ok=True)
    for v in versions:
        (base / v["student_file"]).write_text(v["student_html"], encoding="utf-8")
        (base / v["key_file"]).write_text(v["key_html"], encoding="utf-8")
    if combined:
        (base / combined["file"]).write_text(combined["html"], encoding="utf-8")
    (base / "build_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def load_transfer_engine(github_root: Path):
    path = github_root / "memories" / "Tools" / "curriculum_transfer" / "apply_curriculum_transfers.py"
    if not path.is_file():
        raise RuntimeError(f"Curriculum Transfer engine not found: {path}")
    spec = importlib.util.spec_from_file_location("curriculum_transfer_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Curriculum Transfer engine.")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def make_transfer(github_root: Path, product: str, item_slug: str, versions: list[dict[str, Any]], build_manifest: dict[str, Any], combined: dict[str, str] | None = None) -> tuple[Path, str]:
    teacher_root = github_root / "teacher_shared"
    index_path = teacher_root / "algebra" / "library" / "unit1" / "index.html"
    if not index_path.is_file():
        raise RuntimeError(f"Teacher Library index not found: {index_path}")

    product_dir = "practices" if product == "Practice" else "quick_checks"
    rel_dir = Path("algebra/library/unit1/builder") / product_dir / item_slug
    new_index = update_library_index(
        index_path.read_text(encoding="utf-8"),
        product,
        str(build_manifest.get("item_label", "")),
        str(build_manifest.get("custom_name", "")),
        item_slug,
        versions,
        combined["file"] if combined else None,
    )

    stamp = time.strftime("%Y%m%d_%H%M%S")
    package_id = f"assessment_builder_save_{product_dir}_{item_slug}_{stamp}"
    transfer_root = github_root / "_curriculum_transfers"
    downloads = transfer_root / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    zip_path = downloads / f"{package_id}_GITHUB_TRANSFER.zip"

    with tempfile.TemporaryDirectory(prefix="assessment-builder-transfer-") as td:
        stage = Path(td)
        files: list[dict[str, Any]] = []

        def add_payload(rel: Path, content: str, *, expected_path: Path | None = None):
            payload_rel = Path("payload/teacher_shared") / rel
            out = stage / payload_rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
            target = teacher_root / rel
            entry: dict[str, Any] = {
                "action": "replace" if target.is_file() else "create",
                "root": "teacher_shared",
                "path": rel.as_posix(),
                "source": payload_rel.as_posix(),
            }
            if target.is_file():
                entry["expected_existing_sha256"] = sha256_file(target)
            files.append(entry)

        for v in versions:
            add_payload(rel_dir / v["student_file"], v["student_html"])
            add_payload(rel_dir / v["key_file"], v["key_html"])
        if combined:
            add_payload(rel_dir / combined["file"], combined["html"])
        add_payload(rel_dir / "build_manifest.json", json.dumps(build_manifest, indent=2) + "\n")
        add_payload(Path("algebra/library/unit1/index.html"), new_index)

        manifest = {
            "package_type": "curriculum_transfer",
            "schema_version": 3,
            "package_id": package_id,
            "files": files,
        }
        (stage / "TRANSFER_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(stage.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(stage).as_posix())

    return zip_path, package_id


def apply_one_transfer(github_root: Path, package_path: Path) -> str:
    engine = load_transfer_engine(github_root)
    transfer_root = github_root / "_curriculum_transfers"
    roots = engine.load_roots(transfer_root / "approved_roots.json", github_root)
    status, detail = engine.process_package(package_path, transfer_root, github_root, roots, False)
    if status != "success":
        raise RuntimeError(detail or "Curriculum Transfer failed.")
    return detail


class BuilderHandler(SimpleHTTPRequestHandler):
    server_version = "AlgebraAssessmentBuilder/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def json_response(self, status: int, payload: dict[str, Any]) -> None:
        data = (json.dumps(payload) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if path == "/api/ping":
            self.json_response(200, {"ok": True, "app": "Algebra Assessment Builder", "mode": "owner"})
            return
        if path == "/api/checkpoint/eligibility":
            self.json_response(200, {"ok": True, **checkpoint_engine.eligibility_catalog(self.server.github_root)})  # type: ignore[attr-defined]
            return
        if path == "/api/summative/eligibility":
            self.json_response(200, {"ok": True, **summative_engine.eligibility_catalog(self.server.github_root)})  # type: ignore[attr-defined]
            return
        if path == "/api/summative/latest":
            self.json_response(200, {"ok": True, **self.server.latest_summative()})  # type: ignore[attr-defined]
            return
        if path == "/api/summative/status":
            plan_id = (query.get("plan_id") or [""])[0]
            if not plan_id:
                self.json_response(400, {"ok": False, "error": "plan_id is required."})
                return
            self.json_response(200, {"ok": True, **summative_engine.summative_status(self.server.github_root, plan_id)})  # type: ignore[attr-defined]
            return
        if path in {"/api/summative/reveal-request", "/api/summative/save-replacement-request"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            replacement = path.endswith("save-replacement-request")
            req = summative_engine.replacement_request_path(self.server.github_root, plan_id) if replacement else summative_engine.request_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            if not req.is_file():
                self.json_response(404, {"ok": False, "error": "Summative replacement request ZIP was not found." if replacement else "Summative AI request ZIP was not found."})
                return
            try:
                result = save_request_copy_with_dialog(req, self.server.github_root, "Save Summative replacement request" if replacement else "Save Summative AI request")  # type: ignore[attr-defined]
            except Exception as exc:
                self.json_response(500, {"ok": False, "error": str(exc)})
                return
            self.json_response(200, result)
            return
        if path in {"/api/summative/request.zip", "/api/summative/replacement-request.zip"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            if path.endswith("replacement-request.zip"):
                req = summative_engine.replacement_request_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                missing_message = "Summative replacement request ZIP was not found."
            else:
                req = summative_engine.request_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                missing_message = "Summative AI request ZIP was not found."
            if not req.is_file():
                self.json_response(404, {"ok": False, "error": missing_message})
                return
            data = req.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{req.name}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/summative/reveal-output":
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            assembly = summative_engine.load_summative_assembly(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            if not assembly:
                self.json_response(404, {"ok": False, "error": "Summative output has not been assembled yet."})
                return
            folder = summative_engine.summative_output_dir(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            proc = subprocess.run(["/usr/bin/open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            if proc.returncode != 0:
                self.json_response(500, {"ok": False, "error": f"Could not open Finder for {folder}."})
                return
            self.json_response(200, {"ok": True, "path": str(folder)})
            return
        if path in {"/api/summative/mc-booklet.html", "/api/summative/answer-sheets.html", "/api/summative/mc-key.html", "/api/summative/frq-key.html", "/api/summative/output.zip"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            assembly = summative_engine.load_summative_assembly(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            if not assembly:
                self.json_response(404, {"ok": False, "error": "Summative output has not been assembled yet."})
                return
            if path == "/api/summative/output.zip":
                file_path = summative_engine.summative_output_zip_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                content_type = "application/zip"
                disposition = f'attachment; filename="{file_path.name}"'
            else:
                out = summative_engine.summative_output_dir(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                name = {
                    "/api/summative/mc-booklet.html": "mc_booklet.html",
                    "/api/summative/answer-sheets.html": "answer_sheets.html",
                    "/api/summative/mc-key.html": "mc_key.html",
                    "/api/summative/frq-key.html": "frq_key.html",
                }[path]
                file_path = out / name
                # Editable Summative preview surfaces are rendered live from the
                # stored assembly data on every open. This prevents old generated
                # HTML from surviving controller/template upgrades. The stored
                # question instances remain authoritative; only presentation is rebuilt.
                if path in {"/api/summative/mc-booklet.html", "/api/summative/answer-sheets.html"}:
                    try:
                        plan_path = self.server.github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_state" / plan_id / "plan.json"  # type: ignore[attr-defined]
                        data_path = out / "assembly_data.json"
                        if plan_path.is_file() and data_path.is_file():
                            plan = json.loads(plan_path.read_text(encoding="utf-8"))
                            assembly_data = json.loads(data_path.read_text(encoding="utf-8"))
                            versions = assembly_data.get("mc_versions") or []
                            if path == "/api/summative/mc-booklet.html":
                                fresh_html = summative_output.mc_booklet_document(plan, versions)
                            else:
                                forms = assembly_data.get("student_forms") or []
                                status = summative_engine.summative_status(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                                validation = status.get("response_validation") if isinstance(status, dict) else None
                                families = validation.get("families") if isinstance(validation, dict) else []
                                families = families if isinstance(families, list) else []
                                mc_count = 0
                                if versions and isinstance(versions[0], dict):
                                    mc_count = len(versions[0].get("questions") or [])
                                if not mc_count:
                                    mc_count = len(families)
                                fresh_html = summative_output.answer_sheets_document(
                                    self.server.github_root, plan, forms, families, mc_count  # type: ignore[attr-defined]
                                )
                            file_path.write_text(fresh_html, encoding="utf-8")
                    except Exception as exc:
                        label = "MC booklet" if path == "/api/summative/mc-booklet.html" else "Answer/FRQ sheet"
                        self.json_response(500, {"ok": False, "error": f"Could not refresh {label} preview: {exc}"})
                        return
                content_type = "text/html; charset=utf-8"
                disposition = None
            if not file_path.is_file():
                self.json_response(404, {"ok": False, "error": "Summative output file was not found."})
                return
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            if disposition:
                self.send_header("Content-Disposition", disposition)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/checkpoint/latest":
            self.json_response(200, {"ok": True, **self.server.latest_checkpoint()})  # type: ignore[attr-defined]
            return
        if path == "/api/checkpoint/status":
            plan_id = (query.get("plan_id") or [""])[0]
            if not plan_id:
                self.json_response(400, {"ok": False, "error": "plan_id is required."})
                return
            self.json_response(200, {"ok": True, **checkpoint_engine.checkpoint_status(self.server.github_root, plan_id)})  # type: ignore[attr-defined]
            return
        if path == "/api/checkpoint/library.html":
            doc = checkpoint_engine.checkpoint_library_document(self.server.github_root)  # type: ignore[attr-defined]
            data = doc.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if path in {"/api/checkpoint/reveal-request", "/api/checkpoint/save-replacement-request"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            replacement = path.endswith("save-replacement-request")
            req = checkpoint_engine.replacement_request_path(self.server.github_root, plan_id) if replacement else self.server.checkpoint_request_path(plan_id)  # type: ignore[attr-defined]
            if not req.is_file():
                self.json_response(404, {"ok": False, "error": "Family replacement request ZIP was not found." if replacement else "AI family request ZIP was not found."})
                return
            try:
                result = save_request_copy_with_dialog(req, self.server.github_root, "Save Checkpoint replacement request" if replacement else "Save Checkpoint AI request")  # type: ignore[attr-defined]
            except Exception as exc:
                self.json_response(500, {"ok": False, "error": str(exc)})
                return
            self.json_response(200, result)
            return
        if path == "/api/checkpoint/reveal-output":
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            assembly = checkpoint_engine.load_checkpoint_assembly(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            if not assembly:
                self.json_response(404, {"ok": False, "error": "Checkpoint output has not been assembled yet."})
                return
            folder = checkpoint_engine.checkpoint_output_dir(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            proc = subprocess.run(["/usr/bin/open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            if proc.returncode != 0:
                self.json_response(500, {"ok": False, "error": f"Could not open Finder for {folder}."})
                return
            self.json_response(200, {"ok": True, "path": str(folder)})
            return
        if path in {"/api/checkpoint/student.html", "/api/checkpoint/class-packet.html", "/api/checkpoint/teacher-key.html", "/api/checkpoint/output.zip"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            assembly = checkpoint_engine.load_checkpoint_assembly(self.server.github_root, plan_id)  # type: ignore[attr-defined]
            if not assembly:
                self.json_response(404, {"ok": False, "error": "Checkpoint output has not been assembled yet."})
                return
            if path == "/api/checkpoint/output.zip":
                file_path = checkpoint_engine.checkpoint_output_zip_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                content_type = "application/zip"
                disposition = f'attachment; filename="{file_path.name}"'
            else:
                out = checkpoint_engine.checkpoint_output_dir(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                if path == "/api/checkpoint/class-packet.html":
                    rel = assembly.get("class_packet_file", "class_packet.html")
                elif path == "/api/checkpoint/teacher-key.html":
                    rel = assembly.get("teacher_key_file", "teacher_key.html")
                else:
                    student_key = (query.get("student_key") or [""])[0]
                    match = next((x for x in assembly.get("student_forms", []) if x.get("student_key") == student_key), None)
                    if not match:
                        self.json_response(404, {"ok": False, "error": "Student form was not found."})
                        return
                    rel = match.get("file", "")
                file_path = out / str(rel)
                try:
                    file_path.resolve().relative_to(out.resolve())
                except ValueError:
                    self.json_response(400, {"ok": False, "error": "Invalid checkpoint output path."})
                    return
                content_type = "text/html; charset=utf-8"
                disposition = None
            if not file_path.is_file():
                self.json_response(404, {"ok": False, "error": "Checkpoint output file was not found."})
                return
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            if disposition:
                self.send_header("Content-Disposition", disposition)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if path in {"/api/checkpoint/request.zip", "/api/checkpoint/replacement-request.zip"}:
            plan_id = (query.get("plan_id") or [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                self.json_response(400, {"ok": False, "error": "Invalid plan_id."})
                return
            if path.endswith("replacement-request.zip"):
                req = checkpoint_engine.replacement_request_path(self.server.github_root, plan_id)  # type: ignore[attr-defined]
                missing_message = "Family replacement request ZIP was not found."
            else:
                req = self.server.checkpoint_request_path(plan_id)  # type: ignore[attr-defined]
                missing_message = "AI family request ZIP was not found."
            if not req.is_file():
                self.json_response(404, {"ok": False, "error": missing_message})
                return
            data = req.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{req.name}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed_post = urlparse(self.path)
        path = parsed_post.path
        if path in {"/api/checkpoint/import-result", "/api/summative/import-result"}:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BODY:
                    raise ValueError("Result file is empty or too large.")
                plan_id = (parse_qs(parsed_post.query).get("plan_id") or [""])[0]
                if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id or ""):
                    raise ValueError("Invalid plan_id.")
                filename = self.headers.get("X-Result-Filename", "")
                try:
                    from urllib.parse import unquote
                    filename = unquote(filename)
                except Exception:
                    pass
                body = self.rfile.read(length)
                if path == "/api/checkpoint/import-result":
                    result = result_import.import_checkpoint_result(self.server.github_root, plan_id, body, filename)  # type: ignore[attr-defined]
                else:
                    result = result_import.import_summative_result(self.server.github_root, plan_id, body, filename)  # type: ignore[attr-defined]
                self.json_response(200, {"ok": True, **result})
            except ValueError as exc:
                self.json_response(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self.json_response(500, {"ok": False, "error": str(exc)})
            return
        if path not in {"/api/save", "/api/checkpoint/analyze", "/api/checkpoint/family-review", "/api/checkpoint/assemble", "/api/checkpoint/manual-adjust", "/api/checkpoint/approve", "/api/checkpoint/unapprove", "/api/summative/analyze", "/api/summative/family-review", "/api/summative/assemble", "/api/summative/manual-adjust", "/api/summative/approve-mc-set"}:
            self.json_response(404, {"ok": False, "error": "Unknown endpoint."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("Request is empty or too large.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if path == "/api/save":
                result = self.server.save_build(payload)  # type: ignore[attr-defined]
            elif path == "/api/checkpoint/analyze":
                result = self.server.analyze_checkpoint(payload)  # type: ignore[attr-defined]
            elif path == "/api/checkpoint/family-review":
                result = self.server.review_checkpoint_family(payload)  # type: ignore[attr-defined]
            elif path == "/api/checkpoint/manual-adjust":
                result = self.server.manual_adjust_checkpoint(payload)  # type: ignore[attr-defined]
            elif path == "/api/checkpoint/approve":
                result = self.server.approve_checkpoint(payload)  # type: ignore[attr-defined]
            elif path == "/api/checkpoint/unapprove":
                result = self.server.unapprove_checkpoint(payload)  # type: ignore[attr-defined]
            elif path == "/api/summative/analyze":
                result = self.server.analyze_summative(payload)  # type: ignore[attr-defined]
            elif path == "/api/summative/family-review":
                result = self.server.review_summative_family(payload)  # type: ignore[attr-defined]
            elif path == "/api/summative/assemble":
                result = self.server.assemble_summative(payload)  # type: ignore[attr-defined]
            elif path == "/api/summative/manual-adjust":
                result = self.server.manual_adjust_summative(payload)  # type: ignore[attr-defined]
            elif path == "/api/summative/approve-mc-set":
                result = self.server.approve_summative_mc_set(payload)  # type: ignore[attr-defined]
            else:
                result = self.server.assemble_checkpoint(payload)  # type: ignore[attr-defined]
            self.json_response(200, {"ok": True, **result})
        except Exception as exc:
            self.json_response(500, {"ok": False, "error": str(exc)})


class BuilderServer(ThreadingHTTPServer):
    def __init__(self, address, handler, github_root: Path, auto_apply: bool):
        super().__init__(address, handler)
        self.github_root = github_root
        self.auto_apply = auto_apply

    def checkpoint_state_root(self) -> Path:
        return self.github_root / "_algebra_teacher_tools" / "assessment_builder" / "checkpoint_state"

    def checkpoint_request_path(self, plan_id: str) -> Path:
        return checkpoint_engine.request_path(self.github_root, plan_id)

    def latest_checkpoint(self) -> dict[str, Any]:
        root = self.checkpoint_state_root()
        if not root.is_dir():
            return {"found": False}
        plans = sorted(root.glob("*/plan.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not plans:
            return {"found": False}
        try:
            plan = json.loads(plans[0].read_text(encoding="utf-8"))
        except Exception:
            return {"found": False}
        return checkpoint_engine.checkpoint_status(self.github_root, str(plan.get("plan_id", "")))

    def latest_summative(self) -> dict[str, Any]:
        root = self.github_root / "_algebra_teacher_tools" / "assessment_builder" / "summative_state"
        if not root.is_dir():
            return {"found": False}
        plans = sorted(root.glob("*/plan.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not plans:
            return {"found": False}
        try:
            plan = json.loads(plans[0].read_text(encoding="utf-8"))
        except Exception:
            return {"found": False}
        return summative_engine.summative_status(self.github_root, str(plan.get("plan_id", "")))

    def analyze_summative(self, payload: dict[str, Any]) -> dict[str, Any]:
        unit = int(payload.get("unit", 1))
        item_label = str(payload.get("item_label", "Summative")).strip() or "Summative"
        custom_name = str(payload.get("custom_name", "")).strip()
        eligible = payload.get("eligible_i_cans") or []
        if not isinstance(eligible, list):
            raise ValueError("eligible_i_cans must be a list.")
        plan = summative_engine.build_summative_plan(
            self.github_root,
            item_label=item_label,
            custom_name=custom_name,
            target_questions=4,
            unit=unit,
            eligible_i_cans=[str(x) for x in eligible],
        )
        state_path = summative_engine.write_summative_state(self.github_root, plan)
        request_path = summative_engine.create_request_zip(self.github_root, plan)
        status = summative_engine.summative_status(self.github_root, plan["plan_id"])
        return {**status, "plan": plan, "state_path": str(state_path), "request_ready": True, "request_name": request_path.name, "request_url": f"/api/summative/request.zip?plan_id={plan['plan_id']}"}

    def review_summative_family(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        family_id = str(payload.get("family_id", "")).strip()
        decision = str(payload.get("decision", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        if not family_id:
            raise ValueError("family_id is required.")
        return summative_engine.save_family_review_decision(self.github_root, plan_id, family_id, decision)

    def assemble_summative(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        assembly = summative_engine.assemble_summative(self.github_root, plan_id)
        status = summative_engine.summative_status(self.github_root, plan_id)
        return {**status, "assembly": assembly}

    def manual_adjust_summative(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        student_key = str(payload.get("student_key", "")).strip()
        family_id = str(payload.get("family_id", "")).strip()
        slot_index = int(payload.get("slot_index", 0) or 0)
        instance = payload.get("instance") if isinstance(payload.get("instance"), dict) else {}
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        if not student_key or not family_id or slot_index < 1:
            raise ValueError("student_key, family_id, and slot_index are required.")
        assembly = summative_engine.manual_adjust_summative(self.github_root, plan_id, student_key, slot_index, family_id, instance)
        return {"assembly": assembly}

    def approve_summative_mc_set(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        transfer = summative_engine.create_mc_library_transfer(self.github_root, plan_id)
        result = save_transfer_copy_with_dialog(transfer, self.github_root, "Save approved Summative MC-set transfer")
        if result.get("cancelled"):
            return {"saved": False, **result}
        return {"saved": True, **result}

    def analyze_checkpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        unit = int(payload.get("unit", 1))
        target = int(payload.get("target_questions", 6))
        item_label = str(payload.get("item_label", "Checkpoint")).strip() or "Checkpoint"
        custom_name = str(payload.get("custom_name", "")).strip()
        eligible = payload.get("eligible_i_cans") or []
        if not isinstance(eligible, list):
            raise ValueError("eligible_i_cans must be a list.")
        plan = checkpoint_engine.build_checkpoint_plan(
            self.github_root,
            item_label=item_label,
            custom_name=custom_name,
            target_questions=target,
            unit=unit,
            eligible_i_cans=[str(x) for x in eligible],
        )
        state_path = checkpoint_engine.write_checkpoint_state(self.github_root, plan)
        request_path = checkpoint_engine.create_extension_request_zip(self.github_root, plan)
        status = checkpoint_engine.checkpoint_status(self.github_root, plan["plan_id"])
        return {
            **status,
            "plan": plan,
            "state_path": str(state_path),
            "request_ready": bool(request_path),
            "request_name": request_path.name if request_path else None,
            "request_url": f"/api/checkpoint/request.zip?plan_id={plan['plan_id']}" if request_path else None,
            "replacement_request_url": f"/api/checkpoint/replacement-request.zip?plan_id={plan['plan_id']}" if status.get("replacement_request_ready") else None,
        }

    def review_checkpoint_family(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        family_id = str(payload.get("family_id", "")).strip()
        decision = str(payload.get("decision", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        if not family_id:
            raise ValueError("family_id is required.")
        status = checkpoint_engine.save_family_review_decision(self.github_root, plan_id, family_id, decision)
        return {
            **status,
            "request_url": f"/api/checkpoint/request.zip?plan_id={plan_id}",
            "replacement_request_url": f"/api/checkpoint/replacement-request.zip?plan_id={plan_id}" if status.get("replacement_request_ready") else None,
        }

    def assemble_checkpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        fresh_instances = payload.get("fresh_instances") or []
        if not isinstance(fresh_instances, list):
            raise ValueError("fresh_instances must be a list.")
        checkpoint_engine.assemble_checkpoint(self.github_root, plan_id, fresh_instances)
        status = checkpoint_engine.checkpoint_status(self.github_root, plan_id)
        return {
            **status,
            "request_url": f"/api/checkpoint/request.zip?plan_id={plan_id}",
            "replacement_request_url": f"/api/checkpoint/replacement-request.zip?plan_id={plan_id}" if status.get("replacement_request_ready") else None,
        }

    def manual_adjust_checkpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        student_key = str(payload.get("student_key", "")).strip()
        family_id = str(payload.get("family_id", "")).strip()
        try:
            slot_index = int(payload.get("slot_index", 0))
        except (TypeError, ValueError):
            slot_index = 0
        instance = payload.get("instance") if isinstance(payload.get("instance"), dict) else {}
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        if not student_key or not family_id or slot_index < 1:
            raise ValueError("student_key, slot_index, and family_id are required.")
        checkpoint_engine.manual_adjust_checkpoint(self.github_root, plan_id, student_key, slot_index, family_id, instance)
        status = checkpoint_engine.checkpoint_status(self.github_root, plan_id)
        return {**status}

    def approve_checkpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        approval = checkpoint_engine.approve_checkpoint(
            self.github_root,
            plan_id,
            bool(payload.get("fit_confirmed")),
            payload.get("layout_state") if isinstance(payload.get("layout_state"), dict) else {},
        )
        return {"approved": True, "approval": approval}

    def unapprove_checkpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan_id = str(payload.get("plan_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", plan_id):
            raise ValueError("Invalid plan_id.")
        checkpoint_engine.revoke_checkpoint_approval(self.github_root, plan_id)
        return {"approved": False}

    def save_build(self, payload: dict[str, Any]) -> dict[str, Any]:
        if int(payload.get("schema_version", 0)) != 1:
            raise ValueError("Unsupported save schema.")
        product = str(payload.get("product", ""))
        if product not in {"Practice", "Quick Check"}:
            raise ValueError(f"Owner saving for {product or 'this product'} is not enabled yet.")
        if int(payload.get("unit", 0)) != 1:
            raise ValueError("This first owner release currently supports Unit 1 only.")
        versions_in = payload.get("versions")
        if not isinstance(versions_in, list) or not versions_in:
            raise ValueError("No built versions were supplied.")

        item_label = str(payload.get("item_label", "")).strip() or "Untitled"
        custom_name = str(payload.get("custom_name", "")).strip()
        item_slug = slugify(item_label + ("_" + custom_name if custom_name else ""), "untitled")
        save_target = str(payload.get("save_target", "both"))
        if save_target not in {"both", "library", "local"}:
            raise ValueError("Invalid save destination.")

        versions: list[dict[str, Any]] = []
        seen = set()
        for record in versions_in:
            if not isinstance(record, dict):
                raise ValueError("Invalid version record.")
            n = int(record.get("version", 0))
            if n < 1 or n in seen:
                raise ValueError("Version numbers must be unique positive integers.")
            seen.add(n)
            base = safe_filename(record.get("base_filename", ""), f"Algebra_1_U1_{item_slug}_{slugify(product)}_V{n}")
            student_html = str(record.get("student_html", ""))
            key_html = str(record.get("key_html", ""))
            if "<html" not in student_html.lower() or "<html" not in key_html.lower():
                raise ValueError(f"Version {n} is missing its student or key HTML.")
            versions.append({
                "version": n,
                "student_file": base + ".html",
                "key_file": base + "_KEY.html",
                "student_html": student_html,
                "key_html": key_html,
                "question_count": len(record.get("questions") or []),
            })
        versions.sort(key=lambda x: x["version"])

        combined = None
        combined_html = str(payload.get("combined_student_html", ""))
        combined_base = safe_filename(payload.get("combined_base_filename", ""), f"Algebra_1_U1_{item_slug}_{slugify(product)}_ALL_VERSIONS")
        if combined_html:
            if "<html" not in combined_html.lower():
                raise ValueError("Combined all-versions HTML is invalid.")
            combined = {"file": combined_base + ".html", "html": combined_html}

        manifest = {
            "schema_version": 1,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "course": "Algebra 1",
            "unit": 1,
            "product": product,
            "item_label": item_label,
            "custom_name": custom_name,
            "display_title": str(payload.get("display_title", "")).strip(),
            "bank_revision": payload.get("bank_revision"),
            "versions": [
                {"version": v["version"], "student_file": v["student_file"], "key_file": v["key_file"], "question_count": v["question_count"]}
                for v in versions
            ],
            "all_versions_file": combined["file"] if combined else None,
        }

        result: dict[str, Any] = {}
        if save_target in {"both", "local"}:
            product_dir = "practices" if product == "Practice" else "quick_checks"
            local_dir = self.github_root / "_algebra_teacher_tools" / "assessment_builder" / "output" / "unit1" / product_dir / item_slug
            write_files(local_dir, versions, manifest, combined)
            result["local_path"] = str(local_dir)

        if save_target in {"both", "library"}:
            zip_path, package_id = make_transfer(self.github_root, product, item_slug, versions, manifest, combined)
            if self.auto_apply:
                detail = apply_one_transfer(self.github_root, zip_path)
                result["transfer_status"] = detail
            else:
                result["transfer_path"] = str(zip_path)
            result["package_id"] = package_id
            result["library_url"] = "https://tnezki.github.io/teacher_shared/algebra/library/unit1/index.html"

        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8782)
    parser.add_argument("--app-root", type=Path, required=True)
    parser.add_argument("--github-root", type=Path, required=True)
    parser.add_argument("--no-apply", action="store_true")
    args = parser.parse_args()

    app_root = args.app_root.expanduser().resolve()
    github_root = args.github_root.expanduser().resolve()
    if not (app_root / "index.html").is_file():
        raise SystemExit(f"Builder index missing: {app_root / 'index.html'}")
    if not github_root.is_dir():
        raise SystemExit(f"GitHub root missing: {github_root}")

    handler = partial(BuilderHandler, directory=str(app_root))
    server = BuilderServer(("127.0.0.1", args.port), handler, github_root, not args.no_apply)
    print(f"Algebra Assessment Builder owner server: http://127.0.0.1:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
