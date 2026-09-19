# Math Family Prompt & Preview Quality — HARD

Status: CURRENT  
Updated: 2026-09-18

This guide closes a failure mode exposed by the District Math Worksheet Builder: family metadata and generic visuals were being rendered as though they were complete student questions.

## 1. Metadata is not student wording
The following fields are planning metadata and MUST NOT be turned directly into student prompt prose:
- `evidence_job`
- `student_action`
- `summary`
- `category`
- `quality_status`
- representation labels

A prompt such as **“Interpret zero/negative exponents as multiplicative inverses. Use the representation shown and complete the requested response.”** is invalid because it paraphrases metadata instead of instantiating a mathematical task.

Student-facing wording must instantiate the family generator with concrete mathematical values, expressions, data, context, and/or figures.

## 2. Complete-question gate
Before an item may render, verify all of the following:
1. Every placeholder in the family prompt pattern is resolved.
2. The student has enough information to produce the requested response.
3. Any required representation is actually present.
4. The representation is the correct semantic kind for that family.
5. The item has been independently solved.
6. The stored answer agrees with the prompt and representation.

If any check fails, fail the item closed. Do not substitute generic prose or a generic visual.

## 3. Visual semantics gate
A visually accurate but semantically wrong figure is a failure.

Examples:
- `SYSTEM_GRAPH_SOLUTION` must show two graphed relations whose intersection is the system solution. A triangle on a coordinate grid is invalid.
- `TRANSFORM_SEQUENCE` must show both the source and image figures (or an equally complete transformation stimulus). Showing only one triangle is invalid.
- `SLOPE_FROM_GRAPH` must show the intended line with a readable scale. A generic coordinate grid is invalid.
- `EXP_ZERO_NEGATIVE` normally requires an expression, not a decorative coordinate graph.
- Lower-elementary visual families must show the actual base-ten, fraction, number-line, clock, ruler, money, array, or grouped-object model named by the family.

## 4. Curated preview specimens
Curated preview specimens are stored by canonical `family_id` in:
- `catalogs/math_family_preview_specimens.json` — Grade 8 / initial quality-repair set
- `catalogs/math_family_preview_specimens_le7.json` — Lower Elementary through Grade 7 supplement

Together these cover all **165 currently active Lower Elementary through Grade 8 canonical math families**.

Preview specimens:
- are original questions;
- are not source questions;
- demonstrate what a complete instance of the family looks like;
- include the correct representation semantics;
- include a hidden answer key for QA;
- are not copied verbatim into generated student worksheets.

Teacher-facing preview UIs MUST merge the canonical specimen sets by `family_id`. If a future family does not yet have a curated specimen, show **Preview pending quality review** rather than inventing a fallback question.

## 5. Generated-item relationship to preview
The generated problem may change values, coordinates, data, orientation, context, or legal response details, but it must preserve the family morphology demonstrated by the curated preview and the canonical family generator contract.

Preview similarity is structural, not textual. Do not clone the preview wording/numbers merely to pass QA.

## 6. Concision
For routine math practice, prefer direct mathematical language. Do not append filler such as:
- “Use the representation shown and complete the requested response.”
- “Show what you know about the concept.”
- “Use your reasoning to determine the answer.”

Use such directions only when they name an actual required action that is not already clear from the problem.

## 7. Coverage gate for active courses
For every active course map:
- every mapped `family_id` must resolve to a curated preview specimen;
- every specimen must have a concrete prompt and solved `answer_key`;
- any required visual must resolve to an implemented family-appropriate renderer;
- preview coverage must be checked before a course is marked ready for classroom use.

Algebra 1, Geometry, Algebra 2, Precalculus, and Calculus may be added to the course maps while their reference sets are being built, but no new family should be treated as quality-complete until this gate passes.
