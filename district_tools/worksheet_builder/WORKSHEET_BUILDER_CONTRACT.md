# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.8-pilot
REVISION: 2026-09-19.8

This tool builds original printable math practice from teacher-selected canonical question families. It must not reproduce source worksheet wording, numbers, names, diagrams, choices, or source-specific layouts.

## 1. Authority and core purpose — HARD
For question authoring inside a request ZIP, follow: `QUESTION_STRUCTURE_CORE.md`; packaged `MATH_WORKSHEET_GENERATOR_BANK.json`; `PARALLEL_FAMILY_RULES.md`; this contract; structured `request.json`. The packaged generator bank is a runtime compatibility aggregate composed from the canonical manifest and all registered course extensions. Family contracts are executable requirements, not suggestions.

Active teacher catalogs: Lower Elementary; Grades 4–8; Algebra 1; Geometry; Algebra 2; Precalculus; Calculus.

### GitHub Pages canonical-source loading — HARD
The canonical `_question_structure` directory is repository authority and may be excluded from GitHub Pages publication because its name begins with an underscore. Browser runtime code MUST load canonical family manifests/sources through a repository-safe route (raw GitHub content or the GitHub Contents API), not assume `../../_question_structure/...` is published as a Pages URL. Before showing the teacher catalog, verify every `active_courses` entry in the family manifest resolves. If canonical composition fails, fail closed with a visible error; never silently fall back to an older partial catalog.

## 2. Reference-use rule — HARD
Teacher sample worksheets, parallel forms, topic inventories, and external free worksheet catalogs may inform skill scope, recurring task architecture, representations, response modes, parameter/property controls, validity ranges, and difficulty progression. They may not be copied, traced, closely paraphrased, numerically cloned, or stored as a hidden question bank.

## 3. Canonical family lock — HARD
Resolve the exact selected `question_family_id` in packaged `family_contracts`. The final item MUST match evidence job, student action, response mode, representation role/render route, parameter validity, answer rule, **visual policy**, parallel invariants, and quality gates. Do not free-write a vaguely related item then attach the ID. Fail closed when a family cannot be instantiated validly.

## 4. Student visual / solution visual — HARD
Honor each family `visual_policy`.
- Student visuals contain only givens and answer-neutral representation.
- If construction is assessed, provide a blank/partial construction surface rather than the completed answer.
- Completed boundary lines, inequality shading, transformed images, tangent/secant lines, solution curves, Riemann rectangles, plotted responses, and similar answer objects belong only in `solution_view` unless explicitly supplied as givens.
- The answer key uses the exact same generated parameters and may add the completed overlay.
A visually correct-looking image that reveals the answer is a FAIL.

## 5. Direct / concise wording — HARD
`direct_concise` is the default. State the mathematical action plainly. Functional context stays when it carries modeling, units, interpretation, data, rate, percent, measurement, or transfer information; decorative story/filler does not.

## 6. Exact teacher-selected blueprint — HARD
Each checked family defaults to 1 question and has an exact requested count. Generate exactly that count per version. Do not auto-balance, substitute, or reallocate. Custom structures keep their exact count.

## 7. Multi-course selection — HARD
A request may mix courses/topics. Preserve each family's own scope and demand. Browse filters do not delete hidden selected families.

## 8. Builder previews — HARD
Every family row exposes Preview. A preview must be a complete original representative problem with the correct graph/table/diagram/model and response form, following student visual policy. Metadata prose is never a preview. If a curated specimen/renderer is missing, display **Preview pending quality review**.

## 9. Difficulty — HARD
Difficulty changes legal parameters/cuing inside the selected family, not the evidence family itself. Mastery is not merely bigger numbers.

## 10. Parallel forms and refresh candidates — HARD
Across versions preserve family ID, I Can/evidence job, student action, response/representation role, visual policy, slot sequence, and approximate difficulty. Vary only contract-authorized parameters.

For every Version + Problem slot, author and independently solve **3 original same-family candidates**. The finished worksheet places **↻ New Question** below Problem selection. Refresh changes only that slot, cycles candidates before repeating, preserves workspace/visual sizing, and never changes family/evidence/difficulty/visual role. Candidate pools are embedded locally.

**Same-family means a fresh legitimate instance of the selected family, not merely cosmetic editing of the current item.** When the family permits more than one legal morphology/representation/context pattern, the three-candidate pool SHOULD use meaningful variation across those legal axes while keeping the same evidence demand and approximate difficulty. Pure number swaps are acceptable only when numerical procedural fluency is the actual family evidence job.

Teacher-defined custom structures also receive a three-candidate pool at response-build time and use the same **↻ New Question** control. The finished offline worksheet does not invent a brand-new AI-authored custom problem after the response package has been built. A truly new custom problem beyond its embedded candidate pool requires a new request/build (or a future explicitly connected AI service); do not expose a dead or misleading AI button in the offline worksheet.

When an answer key is requested, **Open matching answer key** carries the active candidate-state map so the key matches refreshed questions.

## 11. Student layout, true page view, and type — HARD
Use locked `worksheet_styles.css` byte-for-byte. US Letter portrait. Honor one/two columns in screen and print. Adjustable screen shows real `.worksheet-page` US Letter fragments with the exact page boundaries browser Print will use.

### Screen/print page geometry — HARD
- Physical page box is exactly **8.5 in × 11 in**.
- Browser `@page` margin is **0**.
- The `.worksheet-page` itself supplies the actual classroom print margin with **0.55 in internal padding**.
- Therefore the usable content box is 7.4 in × 9.9 in on both screen and print.
- Do not apply both browser page margins and page padding; double margins are a FAIL.

### Deterministic repagination — HARD
New worksheet responses MUST paginate from the measured rendered content rather than assigning a fixed number of questions per page.

- Keep one canonical ordered list of problem nodes/data for each version outside the rendered page fragments.
- Whenever MathJax finishes, the version changes, a refresh candidate changes, a workspace changes, graph/diagram scale changes, reset is used, or any problem height changes, **discard the old page/column assignment and repaginate that version from scratch**.
- Measure the actual rendered height of the prompt, math, model/graph/diagram, response area, and current workspace after the change.
- In two-column mode, use explicit `.page-columns` with two `.page-column` containers. Greedily place each whole problem into the current column while it fits; then advance to column 2; then create the next page. Do not rely on CSS `column-count` as the authoritative pagination algorithm for new responses.
- In one-column mode, greedily fill the single column/page in the same way.
- Never split a problem between columns/pages unless the owning family explicitly permits a multi-page response area.
- A problem that cannot fit in the remaining space moves to the next column/page. A problem too tall for an empty column may be given a dedicated one-column/full-page treatment rather than clipped.
- **Workspace 0% means zero workspace height.** It must not retain the old measured height, a hidden `min-height`, or a reserved blank block.
- Changing all workspaces in a version to 0% must usually compact the version substantially; old page assignments may not be preserved merely because the version previously occupied more pages.
- Avoidable large blank regions are a pagination failure. If a later whole problem would fit in the unused space of the current column/page at its current measured size, it must be placed there before opening a new page.

The screen page count and the actual browser Print page count MUST agree. Never clip a problem to preserve page count.

Symbolic division uses a stacked MathJax fraction by default. Unicode `÷` or slash is allowed only when that notation is itself intentional to the family or part of a conventional unit such as m/s.

## 12. Version-wide and per-problem layout controls — HARD
Finished `worksheet/worksheet.html` has a screen-only left rail in this order: Version; **All workspaces in this version**; Problem; ↻ New Question + status; Workspace; Graph/diagram; Reset; optional Open matching answer key; Print.

### Version-wide workspace control
- Provide an **All workspaces in this version** slider with a practical range of **0–300%**, default 100%.
- Moving it writes that workspace percentage to every problem slot in the currently selected version only and immediately repaginates that version.
- Its primary use case is rapid compaction: setting it to **0%** collapses all question workspaces in that version without altering prompts, visuals, candidate selections, or any other version.
- It must never change another version.
- After a version-wide change, the teacher may still override any individual problem with the per-problem Workspace control.
- If individual problem workspaces in the selected version no longer share one value, the control may display a **Mixed** status; moving the slider again intentionally re-unifies them.
- Version-wide changes must preserve each problem's graph/diagram scale.

### Per-problem controls
The selected Problem keeps Workspace **0–1200%** and Graph/diagram **70–160%**. Per-problem settings are stored per exact version/problem and persist across candidate changes. A moving slider with no rendered change is a FAIL.

## 13. Graphs, models, geometry marks, and visuals — HARD
Follow packaged district response/graph standards and the authoritative graph tool for supported Cartesian graphs. Full-size print weights: grid 0.6 pt #aaaaaa; axes/arrows 1.8 pt #222222; relation 2.0 pt; major ticks 1.2 pt; relation exit arrows 1.5 pt. Deterministic SVG/HTML is appropriate for exact non-Cartesian models. Never reveal answer visuals when construction is assessed.

### Fraction multiplication area models — HARD
For family `FRAC_MULT_AREA_MODEL`, the picture must represent the actual factors directly and remain easy to read.

For `a/b × c/d`:
- partition the rectangle into exactly **b equal columns** and **d equal rows** (or the transposed orientation);
- the complete model therefore has exactly **b × d cells**;
- shade `a` of the `b` strips in one direction and `c` of the `d` strips in the other direction;
- make the overlap visually distinct and answer-neutral enough for the student to interpret;
- **do not subdivide the cells again** and do not convert a 3-by-5 model into a dense 15-by-10/20-style grid;
- use an outer border that is clearly stronger than the interior grid and keep the interior grid visually light;
- use fill/pattern contrast that still works in grayscale printing; do not depend on color alone;
- keep each cell large enough to read at the selected print size. If legal generated denominators would create an unreadably dense model, choose different legal values rather than shrinking into micro-cells.

Example architecture: `2/3 × 3/5` is represented by a **3-column × 5-row** rectangle, not by dozens of narrow subdivisions.

### Money models — HARD
For family `MONEY_TOTAL`, money should look recognizably like money while remaining original/cartoon instructional art. Plain pills/rectangles containing only `$5` or `$1` are not sufficient.

- **Bills:** draw a bill-like rectangle with realistic bill proportions (roughly 2.2–2.5:1), rounded or clipped corners, an inner border/frame, denomination numerals in corners, a central seal/portrait-style icon or oval, and the denomination clearly readable. It may be cartoonish and does not need to imitate legal tender artwork.
- **Coins:** draw circular coins with a rim, denomination, and a simple face/emblem cue. Different denominations should have recognizably different relative diameters; use actual US size ordering when practical (quarter largest; nickel next; penny next; dime smallest). Include a small readable denomination cue such as `25¢`/quarter, `10¢`/dime, `5¢`/nickel, or `1¢`/penny so recognition does not depend on color.
- All money visuals must remain legible in grayscale classroom printing.
- Keep bills/coins large enough to identify without zooming and avoid excessive whitespace around a small cluster.

### Standard geometry notation
Geometry diagrams must use conventional drawn marks rather than decorative/text glyphs:
- **Congruent segments:** one, two, or three short perpendicular tick strokes centered on the segment. Segments in the same congruence class use the same tick count; different classes use different counts.
- **Parallel segments:** one or two small arrowhead/chevron marks drawn along the segment. Segments in the same parallel class use the same arrow count.
- **Right angles:** use a small square corner marker.
- Do **not** use asterisks, stars, X/snowflake-like symbols, Unicode lookalikes, or overlapping marks that are hard to identify.
- Marks must be vector/drawn strokes that remain recognizable on screen and in print and scale with the diagram.
- Avoid redundant markings unless they carry evidence needed by the question.

## 14. Answer key — HARD
When requested, `teacher/answer_key.html` matches every version, slot, and candidate. Explanation items include required reasoning. Construction answers show the completed solution view.

## 15. CLICK_ME — HARD
Expose only **Open adjustable worksheet** and **Open answer key** when requested. Do not expose QA/contracts/PDF buttons.

## 16. Response package — HARD
Return one response ZIP containing `CLICK_ME.html`, locked assets, adjustable worksheet HTML, optional answer key HTML, `data/request.json`, and `data/qa.json`. Adjustable HTML + browser Print is canonical.

## 17. QA — HARD
Verify exact counts; family conformity; originality; direct wording; parallel equivalence; 3 candidates per slot; candidate correctness; same-family refresh variety; refresh isolation/cycle/persistence; matching key state; screen/print page geometry; deterministic repagination after every layout/content mutation; version-wide workspace 0/100/300%; per-problem workspace 0/100/500/1200%; no stale page assignments at 0%; no avoidable large blank regions; graph scaling; MathJax; graph weights; fraction-area model denominator geometry; recognizable money-model rendering; conventional geometry marks; deterministic visual accuracy; fraction-bar notation; and student/solution visual separation.

Required pagination spot check: after setting **All workspaces in this version = 0%**, capture the active version's screen page count and browser Print page count and confirm they agree. Confirm that compact remaining questions repack upward/leftward and that the version does not preserve pages solely from its previous workspace heights.

Overall PASS is forbidden if any item drifts from its family, required visual is wrong/missing/unreadable, a student construction view reveals the answer, refresh swaps family/difficulty/visual role, answers disagree, sizing controls fail, page view and print disagree, content clips, stale pagination leaves avoidable extra pages, a fraction multiplication model uses incorrect/dense subdivisions, money is represented by unrecognizable placeholder shapes, symbolic division uses unjustified `÷`/slash, geometry marks are ambiguous, or the answer key mismatches.
