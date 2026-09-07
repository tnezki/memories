from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .fs import read_json


@dataclass(frozen=True)
class ProjectContext:
    github_root: Path
    memories_dir: Path
    course_dir: Path
    course: str
    unit: int


ALG_RESOURCE_ROOT = Path("frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework")


def make_context(github_root: Path, course_folder: str, course: str, unit: int) -> ProjectContext:
    return ProjectContext(
        github_root=github_root,
        memories_dir=github_root / "memories",
        course_dir=github_root / course_folder,
        course=course,
        unit=unit,
    )


def _resolve_universal_structure_library(question_root: Path, manifest_path: Path) -> Path:
    """Resolve the exact current Universal Question Structure Library from its manifest.

    The pilot must not guess a versioned filename. The version manifest is the
    authority for which library file belongs to the current package.
    """
    manifest = read_json(manifest_path)
    candidates: List[str] = []
    for entry in manifest.get("files", []) if isinstance(manifest, dict) else []:
        if not isinstance(entry, dict):
            continue
        rel = str(entry.get("path") or "")
        name = Path(rel).name
        if rel.startswith("library/") and name.startswith("Universal_Question_Structure_Library") and name.endswith(".md"):
            candidates.append(rel)
    if len(candidates) != 1:
        raise ValueError(
            "Question Structure manifest must declare exactly one Universal Question Structure Library; "
            f"found {len(candidates)}: {candidates}"
        )
    return question_root / candidates[0]


def resolve_common(ctx: ProjectContext) -> Dict[str, Path]:
    memories = ctx.memories_dir
    system_manifest_path = memories / "SYSTEM_MANIFEST.json"
    system = read_json(system_manifest_path)
    framework_registry_path = memories / system["frameworks"]
    framework_registry = read_json(framework_registry_path)
    course_entry = framework_registry["courses"][ctx.course]
    framework_manifest_path = memories / course_entry["manifest"]
    framework_manifest = read_json(framework_manifest_path)
    resource_root = memories / framework_manifest["resource_root"]

    build_registry_path = memories / system["build_pms"]
    maintenance_registry_path = memories / system["maintenance_pms"]
    tools_registry_path = memories / system["tools"]

    question_root = memories / system["question_structure"]["path"]
    question_manifest_path = question_root / system["question_structure"]["manifest"]
    question_library_path = _resolve_universal_structure_library(question_root, question_manifest_path)

    return {
        "system_manifest": system_manifest_path,
        "runtime_contract": memories / system["runtime_contract"],
        "local_transfer_contract": memories / system["local_transfer_contract"],
        "philosophy": memories / system["philosophy"],
        "question_structure_manifest": question_manifest_path,
        "question_structure_entrypoint": question_root / system["question_structure"]["entrypoint"],
        "question_structure_library": question_library_path,
        "framework_registry": framework_registry_path,
        "framework_manifest": framework_manifest_path,
        "framework": memories / course_entry["entrypoint"],
        "resource_root": resource_root,
        "build_registry": build_registry_path,
        "maintenance_registry": maintenance_registry_path,
        "tools_registry": tools_registry_path,
        "finalization_contract": memories / system["finalization_contract"],
    }


def resolve_bank_sources(ctx: ProjectContext, job: str) -> List[Path]:
    common = resolve_common(ctx)
    resource_root = common["resource_root"]
    unit = ctx.unit
    exact_plan = resource_root / f"assessment_plans/original/unit{unit}_assessment_plan/unit{unit}_assessment_plan.html"
    profile = resource_root / "profiles/bank_course_profile.json"
    exit_map = resource_root / "curriculum/exit_evidence_map.json"
    warmup_map = resource_root / "curriculum/warmup_progression_map.json"
    assessment_index = resource_root / "assessment_plans/indexes/assessment_plan_index.json"

    base = [
        common["system_manifest"],
        common["runtime_contract"],
        common["local_transfer_contract"],
        common["philosophy"],
        common["question_structure_manifest"],
        common["question_structure_entrypoint"],
        common["question_structure_library"],
        common["framework_registry"],
        common["framework_manifest"],
        common["framework"],
        common["build_registry"],
        common["maintenance_registry"],
        common["tools_registry"],
        common["finalization_contract"],
        profile,
        exit_map,
        warmup_map,
        assessment_index,
        exact_plan,
    ]

    if job == "bank_map":
        base.append(ctx.memories_dir / "pms_build/bank_map.txt")
    elif job == "audit_rebuild_bank_map":
        base.extend([
            ctx.memories_dir / "pms_maintenance/generic_audit_rebuild.txt",
            ctx.memories_dir / "pms_build/bank_map.txt",
            ctx.course_dir / f"banks/unit{unit}/source_map",
        ])
    elif job == "bank_complete":
        base.extend([
            ctx.memories_dir / "pms_build/bank_complete.txt",
            ctx.course_dir / f"banks/unit{unit}/source_map",
        ])
    else:
        raise ValueError(f"Unsupported pilot job: {job}")
    return base
