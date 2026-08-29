#!/usr/bin/env python3
"""Compute the content-stable Physics Bank identity used by Notes 4A/4B.

Primary: STAGE_3E_HANDOFF.json canonical_authored_content_sha256.
Fallback: deterministic manifest of extracted file paths + file SHA-256 values.
Never hashes ZIP container bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
IGNORE_DIRS = {"__MACOSX", "__pycache__"}
IGNORE_NAMES = {".DS_Store"}

def ignored(rel: Path) -> bool:
    if any(part in IGNORE_DIRS for part in rel.parts): return True
    name = rel.name
    return name in IGNORE_NAMES or name.startswith("._") or name.endswith(".pyc")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def stage3e_identity(root: Path):
    candidates = [p for p in root.rglob("STAGE_3E_HANDOFF.json") if not ignored(p.relative_to(root))]
    valid = []
    for p in candidates:
        try: data = json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        value = data.get("canonical_authored_content_sha256")
        if isinstance(value, str):
            value = value.strip().lower()
            if HEX64.fullmatch(value): valid.append((p, value))
    hashes = sorted({v for _, v in valid})
    if len(hashes) == 1:
        return {"method":"stage3e-canonical-v1","fingerprint":f"stage3e-canonical:{hashes[0]}","source":str(valid[0][0].relative_to(root).as_posix())}
    if len(hashes) > 1: raise SystemExit("Conflicting canonical_authored_content_sha256 values found in STAGE_3E_HANDOFF.json files")
    return None

def manifest_identity(root: Path):
    rows=[]
    for p in root.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if ignored(rel): continue
        rows.append((rel.as_posix(),sha256_file(p)))
    rows.sort(key=lambda x:x[0])
    h=hashlib.sha256()
    for rel,digest in rows:
        h.update(rel.encode("utf-8")); h.update(b"\0"); h.update(digest.lower().encode("ascii")); h.update(b"\n")
    return {"method":"content-manifest-v1","fingerprint":f"content-manifest:{h.hexdigest()}","file_count":len(rows)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("bank_root",help="Extracted/materialized unitN Bank folder"); ap.add_argument("--require-stage3e",action="store_true")
    args=ap.parse_args(); root=Path(args.bank_root).resolve()
    if not root.is_dir(): raise SystemExit(f"Bank root is not a directory: {root}")
    result=stage3e_identity(root)
    if result is None:
        if args.require_stage3e: raise SystemExit("No valid Stage 3E canonical_authored_content_sha256 found")
        result=manifest_identity(root)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__ == "__main__": main()
