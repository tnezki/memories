# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable canonical math question families.

## Current catalog coverage
Lower Elementary Math; Grades 4–8; Algebra 1; Geometry; Algebra 2; Precalculus; Calculus.

## Canonical family architecture
The builder resolves the canonical `_question_structure/catalogs/math_family_library_manifest.json` at runtime and composes every registered family source, course map, and preview source. Because GitHub Pages can omit underscore-prefixed repository folders, the browser loader uses raw GitHub content with the GitHub Contents API as a fallback instead of assuming `_question_structure` is published as a Pages path. If the full active-course manifest cannot be resolved, the tool fails closed with a visible error rather than silently showing an older partial catalog.

The high-school expansion adds reusable family contracts across Geometry, shared Algebra 2/Precalculus structures, and Calculus, while reusing existing base/Algebra 1 families when the student action/evidence architecture is genuinely the same.

## Source use
Teacher-supplied parallel forms establish recurring task architecture, representation roles, difficulty patterns, and family boundaries. Official Kuta free course catalogs are used only as a coverage/property cross-check. Source questions, wording, values, and diagrams are not stored or copied.

## Student visual vs. solution visual
Construction families explicitly separate student givens from completed answers. Blank axes/figures belong in the student view when the student is asked to construct; completed lines, shading, transformations, tangent/secant overlays, and solution curves belong in the answer key.

## Quality rule
A family name/summary is metadata, not student wording. Every generated item must be a concrete, independently solved instance of its exact canonical family. Curated previews show complete representative problems. If a family ever lacks a reviewed specimen, Preview fails closed.

## Worksheet display standards
Finished adjustable worksheets use true US Letter page view, the same 8.5 × 11 screen/print page boxes, 0.55 in internal print margins, a **version-wide workspace slider (0–300%)**, per-problem workspace/visual sizing, three selected-family-pool refresh candidates, matching answer-key state, and fraction-bar division by default for symbolic algebra.

Pagination is content-driven, not question-count-driven. Any workspace/visual/refresh/MathJax change causes the active version to be repaginated from scratch using the actual rendered problem heights. At 0% workspace, no old workspace height or old page assignment may remain reserved. New two-column responses use explicit page-column containers so screen page breaks and browser Print page breaks stay aligned.

## Model rendering standards
- Fraction multiplication area models use the actual factor denominators as the grid dimensions. For example, `2/3 × 3/5` is a **3-column × 5-row** model, not a dense micro-grid.
- Count-money models use recognizable cartoon bills and coins: bill proportions/borders/denomination cues and coin rims/relative sizes/denomination cues. Plain pill-shaped `$1`/`$5` placeholders are not considered finished money models.
- Geometry figures use conventional notation: perpendicular tick strokes for congruent segments, arrowhead/chevron marks for parallel segments, and square right-angle markers.

## Workflow
1. Choose one or more course filters.
2. Choose versions, difficulty, one/two columns, and optional answer key.
3. Browse/search family cards and inspect previews.
4. Select exact families and quantities.
5. Create the request ZIP; upload it to ChatGPT; open returned `CLICK_ME.html`.
6. In the adjustable worksheet, use **All workspaces in this version** to collapse or expand every workspace in the active version, resize exact problems individually as needed, or use **↻ New Question** to replace the selected slot with another pre-generated question drawn from the worksheet's selected family pool.

## Refresh and custom behavior
The exact selected family counts control the **initial worksheet**. **↻ New Question** is a teacher edit after generation: it changes only the selected slot and cycles through embedded candidates drawn from the worksheet's **selected family pool**. It may switch that slot to another family the teacher selected, but it may never introduce an unselected family. When multiple families were selected, the refresh pool should include cross-family variety when comparable difficulty permits.

Teacher-defined custom structures may participate in the selected pool and receive pre-generated candidates. A truly new AI-authored custom question after the response ZIP has already been built would require another AI/build call, so the offline worksheet does not pretend to generate one.
