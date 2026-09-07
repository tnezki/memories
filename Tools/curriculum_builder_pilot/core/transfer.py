from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path
from typing import Iterable, List

from .fs import sha256_file


def create_transfer_zip(github_root: Path, changed_files: Iterable[Path], out_zip: Path, package_id: str) -> Path:
    """Package local changed files for the existing transfer helper. No repo writes occur here."""
    files: List[dict] = []
    payloads: List[tuple[Path, str]] = []
    for src in changed_files:
        src = src.resolve()
        rel = src.relative_to(github_root.resolve())
        payload_rel = Path("payload") / rel
        destination = str(rel)
        entry = {"action": "create", "source": str(payload_rel), "destination": destination}
        # This function intentionally does not guess REPLACE vs CREATE against some other snapshot.
        # A future validated-output stage will supply explicit action/hash metadata.
        files.append(entry)
        payloads.append((src, str(payload_rel)))

    manifest = {
        "schema_version": 2,
        "package_type": "github_transfer",
        "package_id": package_id,
        "files": files,
    }
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TRANSFER_MANIFEST.json", json.dumps(manifest, indent=2))
        for src, arc in payloads:
            zf.write(src, arc)
    return out_zip
