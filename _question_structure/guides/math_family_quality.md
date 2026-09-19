# Math Family Prompt & Preview Quality — HARD

Status: CURRENT  
Updated: 2026-09-19

## 1. Metadata is not student wording
`evidence_job`, `student_action`, summaries, categories, quality labels, and representation labels are planning metadata. They MUST NOT be paraphrased into generic student prompts. Student wording must instantiate the family with concrete mathematics.

## 2. Complete-question gate
Before an item may render: all placeholders are resolved; enough information is supplied; required representations are present and semantically correct; the problem is independently solved; the answer agrees with the prompt/visual. Fail closed if any check fails.

## 3. Visual semantics gate
A visually attractive but semantically wrong figure is a failure. Systems show the actual relations; mapping families show mappings; regression families show data/model or residuals; algebra-tile families show correct signed/degree tiles; nonvisual algebra does not receive decorative graphs.

## 4. Curated preview specimens
Canonical preview sources are registered by `catalogs/math_family_library_manifest.json` and currently include the Grade 8/base set, LE–7 supplement, and Algebra 1 supplement. Algebra 1-specific families have curated original morphology previews; shared base families reuse their already-reviewed preview by `family_id`.

Preview specimens demonstrate architecture only. They are original and are not source questions. Generated worksheet items use new legal parameters and may not simply clone preview wording/values.

## 5. Coverage gate
An active course is quality-complete only when every mapped family resolves to a canonical contract and a curated preview, and every required visual has an implemented deterministic renderer. If not, the teacher UI must show **Preview pending quality review** rather than inventing a fallback.

## 6. Concision
Prefer direct mathematical language. Do not append filler such as “Use the representation shown and complete the requested response.”

## 7. Refresh quality
Each generated worksheet slot must have three solved candidates from the exact same family. Refresh may change legal values/context/visual parameters only; it may not drift to a neighboring skill. The matching answer key must follow the active candidate state.
