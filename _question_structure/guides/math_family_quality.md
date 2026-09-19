# Math Family Prompt & Preview Quality — HARD

Status: CURRENT  
Updated: 2026-09-19

## 1. Metadata is not student wording
`evidence_job`, `student_action`, summaries, categories, quality labels, and representation labels are planning metadata. They MUST NOT be paraphrased into generic student prompts. Student wording must instantiate the family with concrete mathematics.

## 2. Complete-question gate
Before an item may render: all placeholders are resolved; enough information is supplied; required representations are present and semantically correct; the problem is independently solved; the answer agrees with the prompt/visual. Fail closed if any check fails.

## 3. Visual semantics gate
A visually attractive but semantically wrong figure is a failure. Systems show the actual relations; mapping families show mappings; regression families show data/model or residuals; algebra tiles show correct signed/degree tiles; nonvisual algebra does not receive decorative graphs.

### Conventional geometry marking — HARD
When a geometry figure communicates segment or angle relationships, use standard mathematical notation:
- congruent segments use short perpendicular tick strokes; the same tick count means the same congruence class;
- parallel segments use small arrowhead/chevron marks; the same arrow count means the same parallel class;
- right angles use a square corner marker;
- never substitute asterisks, stars, X/snowflake symbols, Unicode approximations, or ambiguous overlapping marks;
- use drawn vector strokes that remain legible at print size;
- omit redundant markings unless they are part of the evidence or givens.

## 4. Student / solution visual separation — HARD
The student representation must be answer-neutral. For a construction family, the student gets givens plus a blank construction surface; the answer key gets the completed construction. Never reveal a requested boundary line, inequality shading, transformed image, tangent line, secant line, solution curve, Riemann rectangles, plotted image, or similar answer object in the student view unless it is explicitly part of the given information.

Canonical new high-school family contracts carry `visual_policy.student_view`, `visual_policy.solution_view`, and `visual_policy.construction_assessed`. Generated instances must honor those fields.

## 5. Curated preview specimens
Canonical preview sources are registered by `catalogs/math_family_library_manifest.json`. Every active newly added high-school family has an original curated specimen. A final registered repair source may intentionally override earlier preview specimens when testing exposes a student/solution visual defect; the override must remain answer-neutral and is canonical through the manifest. Preview specimens demonstrate architecture only; generated worksheet items use new legal parameters and may not clone preview wording/values.

## 6. Coverage gate
An active course is quality-complete only when every mapped family resolves to a canonical contract and a curated preview, and every required representation has an implemented deterministic renderer or explicit inline specimen. Otherwise show **Preview pending quality review** rather than inventing a fallback.

## 7. Concision
Prefer direct mathematical language. Do not append filler such as “Use the representation shown and complete the requested response.”

## 8. Refresh quality
Each generated worksheet slot has three solved candidates from the exact same family. Refresh may change legal values/context/visual parameters and family-authorized morphology/representation variants only; it may not drift to a neighboring skill. When richer legal variation exists, the pool should not be three trivial number swaps. Pure number variation is appropriate when procedural fluency is the intended evidence. The matching answer key follows the active candidate state.

Teacher-defined custom slots are also authored as three solved candidates at build time. The offline response package does not manufacture additional AI-authored custom questions after build time.
