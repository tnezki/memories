# Math Family Prompt & Preview Quality — HARD

Status: CURRENT  
Updated: 2026-09-19

## 1. Metadata is not student wording
`evidence_job`, `student_action`, summaries, categories, quality labels, and representation labels are planning metadata. They MUST NOT be paraphrased into generic student prompts. Student wording must instantiate the family with concrete mathematics.

## 2. Complete-question gate
Before an item may render: all placeholders are resolved; enough information is supplied; required representations are present and semantically correct; the problem is independently solved; the answer agrees with the prompt/visual. Fail closed if any check fails.

## 3. Visual semantics gate
A visually attractive but semantically wrong figure is a failure. Systems show the actual relations; mapping families show mappings; regression families show data/model or residuals; algebra tiles show correct signed/degree tiles; nonvisual algebra does not receive decorative graphs.

### Fraction multiplication area-model standard — HARD
For `FRAC_MULT_AREA_MODEL`, represent `a/b × c/d` with exactly `b` equal strips in one direction and `d` equal strips in the other (or the transposed orientation), for exactly `b × d` cells. Shade `a` strips for one factor and `c` strips for the other, with a distinct overlap. Do not subdivide those cells again or create a dense micro-grid. A `2/3 × 3/5` example is a 3-by-5 model. Use print-safe contrast and choose legal values that keep cells readable.

### Money-model standard — HARD
For `MONEY_TOTAL`, render recognizable original/cartoon currency rather than denomination text inside generic pills. Bills use bill-like proportions, inner framing, corner denomination numerals, and a simple center seal/portrait cue. Coins use circular rims, readable denomination cues, and differentiated relative diameters; when using US denominations, use the real size ordering (quarter largest; nickel; penny; dime smallest). Visual recognition must work in grayscale printing and must not depend on color.

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
Each generated worksheet slot has three solved candidates. Candidate 1 is the exact initial blueprint family. Candidates 2–3 follow the seed family's curated refresh neighborhood in `catalogs/math_refresh_groups.json`; if no group exists, they remain in the exact same family.

Refresh is about **same instructional intent**, not random worksheet variety. Never use the entire worksheet's selected-family list as the alternate pool. A group-authorized neighbor family is permitted only when the group explicitly preserves the same broad student action and evidence intent.

For `POLY_FACTOR_QUAD`, useful refresh variety includes monic trinomials, non-monic `a ≠ 1` trinomials, GCF-then-factor cases when appropriate, and a group-authorized special quadratic factorization. Balancing equations, exponent rules, solving equations, expanding products, and graphing are not valid refreshes for a factoring prompt.

The original exact family counts govern initial generation. Every candidate must independently satisfy its own canonical family contract and answer-neutral visual policy. The matching answer key follows the active candidate state.

Teacher-defined custom structures use the teacher description as their refresh neighborhood and are authored as solved candidates at build time. The offline response package does not manufacture additional AI-authored custom questions after build time.

## 9. Page-use quality for generated worksheet responses — HARD
Workspace is an adjustable response area, not a hidden page reservation. When workspace size, visual size, candidate content, MathJax height, or version changes, the owning worksheet renderer must repaginate from the actual rendered heights. At 0% workspace, there is no residual minimum workspace height. Avoidable large blank regions or extra pages caused by stale previous measurements are a FAIL.
