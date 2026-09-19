# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.7-pilot
REVISION: 2026-09-19.6

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

When an answer key is requested, **Open matching answer key** carries the active candidate-state map so the key matches refreshed questions.

## 11. Student layout, true page view, and type — HARD
Use locked `worksheet_styles.css` byte-for-byte. US Letter portrait; `@page` margin 0.55 in; honor one/two columns in screen and print. Adjustable screen shows real `.worksheet-page` US Letter fragments with the exact page boundaries browser Print will use. Repaginate after MathJax, refresh, workspace/visual changes, reset, and any content-height change. Never clip a problem to preserve page count.

Symbolic division uses a stacked MathJax fraction by default. Unicode `÷` or slash is allowed only when that notation is itself intentional to the family or part of a conventional unit such as m/s.

## 12. Per-problem layout controls — HARD
Finished `worksheet/worksheet.html` has a screen-only left rail: Version; Problem; ↻ New Question + status; Workspace 0–1200%; Graph/diagram 70–160%; Reset; optional Open matching answer key; Print. Settings are stored per exact version/problem and persist across candidate changes.

## 13. Graphs and visuals — HARD
Follow packaged district response/graph standards and the authoritative graph tool for supported Cartesian graphs. Full-size print weights: grid 0.6 pt #aaaaaa; axes/arrows 1.8 pt #222222; relation 2.0 pt; major ticks 1.2 pt; relation exit arrows 1.5 pt. Deterministic SVG/HTML is appropriate for exact non-Cartesian models. Never reveal answer visuals when construction is assessed.

## 14. Answer key — HARD
When requested, `teacher/answer_key.html` matches every version, slot, and candidate. Explanation items include required reasoning. Construction answers show the completed solution view.

## 15. CLICK_ME — HARD
Expose only **Open adjustable worksheet** and **Open answer key** when requested. Do not expose QA/contracts/PDF buttons.

## 16. Response package — HARD
Return one response ZIP containing `CLICK_ME.html`, locked assets, adjustable worksheet HTML, optional answer key HTML, `data/request.json`, and `data/qa.json`. Adjustable HTML + browser Print is canonical.

## 17. QA — HARD
Verify exact counts; family conformity; originality; direct wording; parallel equivalence; 3 candidates per slot; candidate correctness; refresh isolation/cycle/persistence; matching key state; page/print agreement; workspace 0/100/500/1200%; graph scaling; MathJax; graph weights; deterministic visual accuracy; fraction-bar notation; and student/solution visual separation.

Overall PASS is forbidden if any item drifts from its family, required visual is wrong/missing, a student construction view reveals the answer, refresh swaps family/difficulty/visual role, answers disagree, sizing controls fail, page view and print disagree, content clips, symbolic division uses unjustified `÷`/slash, or the answer key mismatches.
