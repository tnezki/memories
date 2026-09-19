# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable canonical math question families.

## Current catalog coverage
Lower Elementary Math; Grades 4–8; Algebra 1; Geometry; Algebra 2; Precalculus; Calculus.

## Canonical family architecture
The builder resolves `../../_question_structure/catalogs/math_family_library_manifest.json` at runtime. It composes every registered family source, course map, and preview source, so new course extensions no longer require a separate hand-maintained district-tool catalog or course-specific JavaScript mirror.

This expansion adds 130 new high-school family contracts across Geometry, shared Algebra 2/Precalculus structures, and Calculus, while reusing existing base/Algebra 1 families when the student action/evidence architecture is genuinely the same.

## Source use
Teacher-supplied parallel forms establish recurring task architecture, representation roles, difficulty patterns, and family boundaries. Official Kuta free course catalogs are used only as a coverage/property cross-check. Source questions, wording, values, and diagrams are not stored or copied.

## Student visual vs. solution visual
Construction families explicitly separate student givens from completed answers. Blank axes/figures belong in the student view when the student is asked to construct; completed lines, shading, transformations, tangent/secant overlays, and solution curves belong in the answer key.

## Quality rule
A family name/summary is metadata, not student wording. Every generated item must be a concrete, independently solved instance of its exact canonical family. Curated previews show complete representative problems. If a family ever lacks a reviewed specimen, Preview fails closed.

## Worksheet display standards
Finished adjustable worksheets use true US Letter page view, same screen/print breaks, per-problem workspace/visual sizing, three same-family refresh candidates, matching answer-key state, and fraction-bar division by default for symbolic algebra.

## Workflow
1. Choose one or more course filters.
2. Choose versions, difficulty, one/two columns, and optional answer key.
3. Browse/search family cards and inspect previews.
4. Select exact families and quantities.
5. Create the request ZIP; upload it to ChatGPT; open returned `CLICK_ME.html`.
6. In the adjustable worksheet, resize exact problems or use **↻ New Question** to cycle same-family alternatives before printing.
