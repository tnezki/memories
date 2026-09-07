from __future__ import annotations

from pathlib import Path
from typing import Optional


def _read_packed_ref(git_dir: Path, ref_name: str) -> Optional[str]:
    packed = git_dir / "packed-refs"
    if not packed.exists():
        return None
    for raw in packed.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("^"):
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1] == ref_name:
            return parts[0]
    return None


def read_head_sha(repo_dir: Path) -> Optional[str]:
    """Read the local repository HEAD without invoking git."""
    git_dir = repo_dir / ".git"
    if git_dir.is_file():
        text = git_dir.read_text(encoding="utf-8", errors="replace").strip()
        if text.startswith("gitdir:"):
            raw = text.split(":", 1)[1].strip()
            git_dir = (repo_dir / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
    head = git_dir / "HEAD"
    if not head.exists():
        return None
    value = head.read_text(encoding="utf-8", errors="replace").strip()
    if value.startswith("ref:"):
        ref_name = value.split(":", 1)[1].strip()
        ref_path = git_dir / ref_name
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8", errors="replace").strip()
        return _read_packed_ref(git_dir, ref_name)
    return value or None
