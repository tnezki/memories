#!/usr/bin/env python3
"""
~surgical_course_sync.py

Safely replace one Unit Bank and a pre-validated overlay of Bank-driven
unit artifacts inside an existing course-site ZIP.

The script does NOT generate curriculum content. The governing PM generates and
validates an overlay first. This tool enforces the "touch nothing else" boundary.

Example:
  python3 ~surgical_course_sync.py \
      --course algebra.zip \
      --bank unit3_bank_UPGRADED.zip \
      --overlay /tmp/unit3_overlay \
      --out /tmp/output/algebra.zip \
      --report /tmp/course_sync_report.txt
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath


JUNK_PARTS = {"__MACOSX"}
JUNK_NAMES = {".DS_Store"}
BANK_DATA_RE = re.compile(r"(?:^|/)(unit(?P<unit>\d+)_bank_data\.json)$", re.I)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm_zip_name(name: str) -> str:
    return str(PurePosixPath(name.replace("\\", "/")))


def is_junk_bank_path(name: str) -> bool:
    p = PurePosixPath(norm_zip_name(name))
    return any(part in JUNK_PARTS for part in p.parts) or p.name in JUNK_NAMES or p.name.startswith("._")


def detect_course_root(zf: zipfile.ZipFile) -> str:
    candidates = set()
    names = [norm_zip_name(n) for n in zf.namelist()]
    for n in names:
        if "/banks/" in n:
            prefix = n.split("/banks/", 1)[0]
            if prefix:
                candidates.add(prefix)
        elif n.endswith("/banks"):
            candidates.add(n.rsplit("/banks", 1)[0])
    if len(candidates) != 1:
        raise RuntimeError(f"Could not uniquely detect course root. Candidates: {sorted(candidates)}")
    return next(iter(candidates)).rstrip("/")


def detect_bank_unit_and_base(zf: zipfile.ZipFile) -> tuple[int, str, str]:
    hits = []
    for raw in zf.namelist():
        name = norm_zip_name(raw)
        if is_junk_bank_path(name) or name.endswith("/"):
            continue
        m = BANK_DATA_RE.search(name)
        if m:
            unit = int(m.group("unit"))
            parent = str(PurePosixPath(name).parent)
            if parent == ".":
                parent = ""
            hits.append((unit, parent, name))
    if len(hits) != 1:
        raise RuntimeError(f"Expected exactly one unit bank_data JSON in Bank ZIP; found {hits}")
    return hits[0]


def read_json_from_zip(zf: zipfile.ZipFile, name: str) -> dict:
    return json.loads(zf.read(name).decode("utf-8"))


def bank_items_signature(data: dict) -> dict[str, tuple[str, str]]:
    out = {}
    for item in data.get("items", []):
        bid = item.get("bank_id")
        if not bid:
            raise RuntimeError("Bank item missing bank_id")
        if bid in out:
            raise RuntimeError(f"Duplicate bank_id in Bank: {bid}")
        out[bid] = (str(item.get("section", "")), str(item.get("destination", "")))
    return out


def bank_content_digest(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(payload)


def allowed_overlay_prefixes(unit: int) -> list[re.Pattern]:
    u = str(unit)
    return [
        re.compile(rf"^notes/u{u}_[^/]+_notes(?:/|$)"),
        re.compile(rf"^practice_sets/practice_sets_{u}_[^/]+(?:/|$)"),
        re.compile(rf"^activities/u{u}_[^/]+_act1(?:/|$)"),
        re.compile(rf"^warmups/unit_{u}_warmups(?:/|$)"),
        re.compile(rf"^exit/exit{u}(?:/|$)"),
        re.compile(rf"^reviews/review{u}(?:/|$)"),
        re.compile(rf"^assessments_zxrtjp/unit{u}_summative(?:/|$)"),
    ]


def classify_replace_root(rel: str, unit: int) -> str:
    p = PurePosixPath(rel)
    parts = p.parts
    if not parts:
        raise RuntimeError("Empty overlay path")
    u = str(unit)

    if parts[0] == "notes" and len(parts) >= 2 and re.fullmatch(rf"u{u}_[^/]+_notes", parts[1]):
        return "/".join(parts[:2])
    if parts[0] == "practice_sets" and len(parts) >= 2 and re.fullmatch(rf"practice_sets_{u}_[^/]+", parts[1]):
        return "/".join(parts[:2])
    if parts[0] == "activities" and len(parts) >= 2 and re.fullmatch(rf"u{u}_[^/]+_act1", parts[1]):
        return "/".join(parts[:2])
    if parts[0] == "warmups" and len(parts) >= 2 and parts[1] == f"unit_{u}_warmups":
        return "/".join(parts[:2])
    if parts[0] == "exit" and len(parts) >= 2 and parts[1] == f"exit{u}":
        return "/".join(parts[:2])
    if parts[0] == "reviews" and len(parts) >= 2 and parts[1] == f"review{u}":
        return "/".join(parts[:2])
    if parts[0] == "assessments_zxrtjp" and len(parts) >= 2 and parts[1] == f"unit{u}_summative":
        return "/".join(parts[:2])
    raise RuntimeError(f"Overlay path is outside allowed Unit {unit} Bank-driven roots: {rel}")


def collect_overlay(overlay: Path, unit: int) -> tuple[dict[str, bytes], set[str]]:
    if not overlay.is_dir():
        raise RuntimeError(f"Overlay directory does not exist: {overlay}")
    files: dict[str, bytes] = {}
    roots: set[str] = set()
    for path in sorted(overlay.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(overlay).as_posix()
        # Hard reject macOS/temp junk in generated overlay.
        if any(part == "__MACOSX" for part in PurePosixPath(rel).parts) or PurePosixPath(rel).name in {".DS_Store"} or PurePosixPath(rel).name.startswith("._"):
            continue
        root = classify_replace_root(rel, unit)
        roots.add(root)
        files[rel] = path.read_bytes()
    if not files:
        raise RuntimeError("Overlay contains no files")
    return files, roots


def collect_new_bank_files(zf: zipfile.ZipFile, base: str, unit: int) -> dict[str, bytes]:
    prefix = (base.rstrip("/") + "/") if base else ""
    files = {}
    for raw in zf.namelist():
        name = norm_zip_name(raw)
        if name.endswith("/") or is_junk_bank_path(name):
            continue
        if prefix and not name.startswith(prefix):
            continue
        rel = name[len(prefix):] if prefix else name
        if not rel or rel.startswith("../"):
            continue
        files[rel] = zf.read(raw)

    required = {
        f"unit{unit}_bank_data.json",
        f"unit{unit}_downstream_manifest.json",
    }
    missing = sorted(required - set(files))
    if missing:
        raise RuntimeError(f"New Bank missing required files: {missing}")
    return files


def entry_is_under(name: str, prefix: str) -> bool:
    name = norm_zip_name(name).rstrip("/")
    prefix = norm_zip_name(prefix).rstrip("/")
    return name == prefix or name.startswith(prefix + "/")


def clone_info(info: zipfile.ZipInfo) -> zipfile.ZipInfo:
    new = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
    new.comment = info.comment
    new.extra = info.extra
    new.create_system = info.create_system
    new.create_version = info.create_version
    new.extract_version = info.extract_version
    new.flag_bits = info.flag_bits
    new.volume = info.volume
    new.internal_attr = info.internal_attr
    new.external_attr = info.external_attr
    new.compress_type = info.compress_type
    return new


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", required=True, type=Path)
    ap.add_argument("--bank", required=True, type=Path)
    ap.add_argument("--overlay", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--report", required=False, type=Path)
    args = ap.parse_args()

    report = []
    def log(msg: str) -> None:
        report.append(msg)
        print(msg)

    if args.course.resolve() == args.out.resolve():
        raise RuntimeError("Output ZIP must be a different working path from input course ZIP")

    with zipfile.ZipFile(args.course, "r") as course_zf, zipfile.ZipFile(args.bank, "r") as bank_zf:
        course_root = detect_course_root(course_zf)
        unit, bank_base, bank_data_name = detect_bank_unit_and_base(bank_zf)

        new_bank_data = read_json_from_zip(bank_zf, bank_data_name)
        if str(new_bank_data.get("unit", "")).strip() not in {str(unit), f"Unit {unit}", f"unit{unit}", f"unit {unit}"}:
            # Many Banks store unit as a title/dict; filename remains primary detector.
            log(f"NOTICE: Bank JSON unit field is {new_bank_data.get('unit')!r}; filename resolves Unit {unit}.")

        new_sig = bank_items_signature(new_bank_data)
        new_digest = bank_content_digest(new_bank_data)

        old_bank_json = f"{course_root}/banks/unit{unit}/unit{unit}_bank_data.json"
        old_exists = old_bank_json in course_zf.namelist()

        if old_exists:
            old_bank_data = read_json_from_zip(course_zf, old_bank_json)
            old_sig = bank_items_signature(old_bank_data)
            if set(old_sig) != set(new_sig):
                added = sorted(set(new_sig) - set(old_sig))
                removed = sorted(set(old_sig) - set(new_sig))
                raise RuntimeError(
                    "STRUCTURAL BANK CHANGE: Bank ID set differs. "
                    f"Added={len(added)} Removed={len(removed)}. Surgical sync refused."
                )
            moved = [bid for bid in old_sig if old_sig[bid] != new_sig[bid]]
            if moved:
                raise RuntimeError(
                    "STRUCTURAL BANK CHANGE: section/destination changed for Bank IDs "
                    f"(first 10): {moved[:10]}. Surgical sync refused."
                )
            old_digest = bank_content_digest(old_bank_data)
            content_changed = old_digest != new_digest
        else:
            content_changed = True
            old_digest = None

        overlay_files, overlay_roots = collect_overlay(args.overlay, unit)
        bank_files = collect_new_bank_files(bank_zf, bank_base, unit)

        original_files = {}
        for info in course_zf.infolist():
            if info.is_dir():
                continue
            name = norm_zip_name(info.filename)
            original_files[name] = course_zf.read(info.filename)

        def subtree_bytes(prefix):
            prefix = norm_zip_name(prefix).rstrip("/")
            result = {}
            for name, data in original_files.items():
                if entry_is_under(name, prefix):
                    rel = name[len(prefix):].lstrip("/")
                    if rel:
                        result[rel] = data
            return result

        bank_replace_root = f"{course_root}/banks/unit{unit}"
        existing_bank_files = subtree_bytes(bank_replace_root)
        bank_folder_changed = existing_bank_files != bank_files

        changed_overlay_roots = set()
        for root in sorted(overlay_roots):
            staged = {
                rel[len(root):].lstrip("/"): data
                for rel, data in overlay_files.items()
                if entry_is_under(rel, root)
            }
            existing = subtree_bytes(f"{course_root}/{root}")
            if staged != existing:
                changed_overlay_roots.add(root)

        replace_prefixes = set()
        if bank_folder_changed:
            replace_prefixes.add(bank_replace_root)
        for root in changed_overlay_roots:
            replace_prefixes.add(f"{course_root}/{root}")

        log(f"COURSE_ROOT={course_root}")
        log(f"UNIT={unit}")
        log(f"OLD_BANK_PRESENT={'YES' if old_exists else 'NO'}")
        log(f"BANK_FOLDER_CHANGED={'YES' if bank_folder_changed else 'NO'}")
        log(f"CHANGED_CHILD_FOLDERS={len(changed_overlay_roots)}")
        log("REPLACE_ROOTS:")
        for p in sorted(replace_prefixes):
            log(f"  {p}")

        args.out.parent.mkdir(parents=True, exist_ok=True)

        if not replace_prefixes:
            args.out.write_bytes(args.course.read_bytes())
            log("NO_CHANGE=YES")
            log("OUTPUT_ZIP_BYTE_IDENTICAL=YES")
            log("ZIP_INTEGRITY=PASS")
            log("TOUCH_CONTRACT=PASS")
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
            return 0

        with zipfile.ZipFile(args.out, "w") as out_zf:
            # Copy untouched archive entries with original metadata and bytes.
            for info in course_zf.infolist():
                name = norm_zip_name(info.filename)
                if any(entry_is_under(name, p) for p in replace_prefixes):
                    continue
                data = b"" if info.is_dir() else course_zf.read(info.filename)
                out_zf.writestr(clone_info(info), data)

            # New Bank only when the full Bank folder actually differs.
            if bank_folder_changed:
                for rel, data in sorted(bank_files.items()):
                    arc = f"{bank_replace_root}/{rel}"
                    out_zf.writestr(arc, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

            # Validated overlay only for child folders whose full file set/bytes differ.
            for rel, data in sorted(overlay_files.items()):
                root = classify_replace_root(rel, unit)
                if root not in changed_overlay_roots:
                    continue
                arc = f"{course_root}/{rel}"
                out_zf.writestr(arc, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

        # Integrity and untouched-byte verification.
        with zipfile.ZipFile(args.out, "r") as out_zf:
            bad = out_zf.testzip()
            if bad:
                raise RuntimeError(f"Output ZIP integrity failed at {bad}")

            out_names = set(norm_zip_name(n) for n in out_zf.namelist() if not n.endswith("/"))
            untouched_checked = 0
            for name, old_bytes in original_files.items():
                if any(entry_is_under(name, p) for p in replace_prefixes):
                    continue
                if name not in out_names:
                    raise RuntimeError(f"Protected file missing from output: {name}")
                new_bytes = out_zf.read(name)
                if old_bytes != new_bytes:
                    raise RuntimeError(f"Protected file byte mismatch: {name}")
                untouched_checked += 1

            # Reject unexpected new files outside replacement roots.
            original_names = set(original_files)
            for name in out_names - original_names:
                if not any(entry_is_under(name, p) for p in replace_prefixes):
                    raise RuntimeError(f"Unexpected new file outside replacement roots: {name}")

        log(f"PROTECTED_FILES_BYTE_IDENTICAL={untouched_checked}")
        log("ZIP_INTEGRITY=PASS")
        log("TOUCH_CONTRACT=PASS")

        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text("\n".join(report) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
