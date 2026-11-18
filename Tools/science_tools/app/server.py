#!/usr/bin/env python3
"""Science Tools foundation: read-only local curriculum index; no student-data access.

This deliberately does not import, copy, or replace Physics Tools / CPM Tools modules.
Shared presentation assets are bundled from memories/Tools/course_tool_shared.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8784
HEALTH = b"SCIENCE_TOOLS_OK_V1"
MAX_INDEXED_FILES = 3000
ASSET_TYPES = {".html", ".htm", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf"}
INDEX_TYPES = {".html", ".htm", ".pdf", ".md", ".json"}
ALLOWED_PUBLIC = "lessons"


def workspace_root() -> Path | None:
    """Find the teacher's existing workspace without creating or scanning private data."""
    configured = os.environ.get("MAPS_WORKSPACE_ROOT", "").strip()
    candidates = ([Path(configured).expanduser()] if configured else []) + list(APP_ROOT.parents)
    for base in candidates:
        if (base / "memories").is_dir() and (base / "physics").is_dir():
            return base.resolve()
    return None


def load_courses() -> list[dict]:
    data = json.loads((APP_ROOT / "config" / "course_registry.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("courses"), list):
        raise ValueError("Unsupported course registry")
    return data["courses"]


def physics_public_folder(root: Path | None) -> Path | None:
    folder = root / "physics" / ALLOWED_PUBLIC if root is not None else None
    return folder if folder is not None and folder.is_dir() else None


@lru_cache(maxsize=4)
def index_resources(folder_name: str) -> tuple[dict, ...]:
    root = Path(folder_name)
    result: list[dict] = []
    if not root.is_dir():
        return ()
    # Public, teacher-authored interactive assets only. Never scan private assessment
    # directories, Drive sync, portfolio state, rosters or local tool data.
    for current, dirs, filenames in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not (Path(current) / d).is_symlink())
        for filename in sorted(filenames):
            if len(result) >= MAX_INDEXED_FILES:
                break
            path = Path(current) / filename
            if path.is_symlink() or path.suffix.lower() not in INDEX_TYPES:
                continue
            rel = path.relative_to(root).as_posix()
            result.append({
                "name": path.stem.replace("_", " ").replace("-", " "),
                "file": filename,
                "relative_path": rel,
                "type": path.suffix.lower().lstrip("."),
                "folder": (path.relative_to(root).parent.as_posix() if path.relative_to(root).parent != Path(".") else "Root"),
                "previewable": path.suffix.lower() in {".html", ".htm", ".pdf"},
            })
        if len(result) >= MAX_INDEXED_FILES:
            break
    return tuple(sorted(result, key=lambda r: r["relative_path"].lower()))


def local_summary(root: Path | None) -> dict:
    lessons = physics_public_folder(root)
    items = index_resources(str(lessons)) if lessons else ()
    local_science = root / "SCIENCE_Tools" if root else None
    science_library = root / "SCIENCE_Tools_Library" if root else None
    existing_physics = root / "_physics_teacher_tools" / "app" / "server.py" if root else None
    return {
        "health": "ok",
        "version": "foundation-1",
        "workspace_found": root is not None,
        "workspace_label": str(root) if root else "Not located",
        "physics_repository_found": bool(root and (root / "physics").is_dir()),
        "physics_public_lessons_found": bool(lessons),
        "public_resource_count": len(items),
        "science_tools_folder_found": bool(local_science and local_science.is_dir()),
        "science_library_folder_found": bool(science_library and science_library.is_dir()),
        "existing_physics_tools_found": bool(existing_physics and existing_physics.is_file()),
        "student_data_connection": "not_configured",
        "courses": load_courses(),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ScienceToolsFoundation/1"

    def log_message(self, format: str, *args: object) -> None:
        return  # No student identifiers or query strings written to runtime logs.

    def respond(self, content: bytes, content_type: str, code: int = HTTPStatus.OK, *, csp: bool = False) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if csp:
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def json_response(self, obj: object, code: int = HTTPStatus.OK) -> None:
        self.respond((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"), "application/json; charset=utf-8", code)

    def local_asset(self, path: Path, csp: bool = True) -> None:
        if not path.is_file() or path.is_symlink():
            self.json_response({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.respond(path.read_bytes(), mime + ("; charset=utf-8" if mime.startswith("text/") or mime == "application/javascript" else ""), csp=csp)

    def serve_public(self, relative_url: str) -> None:
        root = workspace_root()
        folder = physics_public_folder(root)
        if folder is None:
            self.json_response({"error": "Public Physics lessons folder missing"}, HTTPStatus.NOT_FOUND)
            return
        decoded = unquote(relative_url)
        # URL encoding cannot override the allowlist or traverse the workspace.
        if not decoded or decoded.startswith("/") or "\\" in decoded:
            self.json_response({"error": "Invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        rel = Path(decoded)
        if any(part in (".", "..", "") for part in rel.parts) or rel.suffix.lower() not in ASSET_TYPES:
            self.json_response({"error": "Invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        dest = (folder / rel).resolve()
        if not dest.is_relative_to(folder.resolve()):
            self.json_response({"error": "Invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        self.local_asset(dest, csp=False)

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/health":
            self.respond(HEALTH, "text/plain; charset=utf-8")
            return
        if path == "/api/status":
            self.json_response(local_summary(workspace_root()))
            return
        if path == "/api/resources":
            args = parse_qs(parsed.query)
            course = args.get("course", ["physics"])[0]
            if course != "physics":
                self.json_response({"course": course, "items": [], "total": 0, "message": "Course is not configured."})
                return
            folder = physics_public_folder(workspace_root())
            if args.get("refresh", [""])[0] == "1":
                index_resources.cache_clear()
            rows = list(index_resources(str(folder))) if folder else []
            needle = args.get("q", [""])[0].strip().lower()[:120]
            if needle:
                rows = [r for r in rows if needle in (r["name"] + " " + r["relative_path"]).lower()]
            try:
                limit = max(1, min(3000, int(args.get("limit", ["100"])[0])))
            except ValueError:
                limit = 100
            self.json_response({"course": course, "items": rows[:limit], "total": len(rows), "truncated": len(rows) > limit})
            return
        if path in {"/", "/index.html"}:
            self.local_asset(APP_ROOT / "app" / "index.html")
            return
        known_assets = {
            "/app.css": APP_ROOT / "app" / "app.css",
            "/app.js": APP_ROOT / "app" / "app.js",
            "/assets/course-tool.css": APP_ROOT / "assets" / "course-tool.css",
            "/assets/course-tool.js": APP_ROOT / "assets" / "course-tool.js",
        }
        if path in known_assets:
            self.local_asset(known_assets[path])
            return
        if path.startswith("/public/lessons/"):
            self.serve_public(path[len("/public/lessons/"):])
            return
        self.json_response({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        self.json_response({"error": "Foundation shell is read-only"}, HTTPStatus.METHOD_NOT_ALLOWED)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start local Science Tools foundation")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default=DEFAULT_HOST)
    args = parser.parse_args()
    if args.host != DEFAULT_HOST:
        parser.error("Science Tools must bind to loopback (127.0.0.1) only")
    if not 1024 <= args.port <= 65535:
        parser.error("Port must be between 1024 and 65535")
    print(f"Science Tools Foundation: http://{args.host}:{args.port}", flush=True)
    print("Read-only curriculum index; no student information loaded.", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
