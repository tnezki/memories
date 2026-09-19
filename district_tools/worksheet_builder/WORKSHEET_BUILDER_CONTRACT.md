# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.6-pilot
REVISION: 2026-09-19.4

This tool builds original printable math practice from teacher-selected canonical question families. It must not reproduce source worksheet wording, numbers, names, diagrams, choices, or source-specific layouts.

## 1. Authority and core purpose — HARD
For question authoring inside a request ZIP, follow: `QUESTION_STRUCTURE_CORE.md`; packaged `MATH_WORKSHEET_GENERATOR_BANK.json`; `PARALLEL_FAMILY_RULES.md`; this contract; structured `request.json`. The packaged generator bank is a compatibility aggregate composed from the canonical math-family library and may include course extensions such as Algebra 1. Its family contracts are executable requirements, not suggestions.

Active teacher catalogs: Lower Elementary, Grades 4–8, and Algebra 1. Geometry, Algebra 2, Precalculus, and Calculus remain future until their reference sets pass the family/preview quality gate.

## 2. Reference-use rule — HARD
Teacher sample worksheets, parallel forms, topic inventories, and external free worksheet catalogs may inform skill scope, recurring task architecture, representations, response modes, parameter/property controls, validity ranges, and difficulty progression. They may not be copied, traced, closely paraphrased, numerically cloned, or stored as a hidden question bank.

## 3. Canonical family lock — HARD
Resolve the exact selected `question_family_id` in the packaged `family_contracts`. The final item MUST match that contract's evidence job, student action, response mode, representation role/render route, parameter validity, answer rule, parallel invariants, and quality gates. Do not free-write a vaguely related item then attach the ID. If the family cannot be instantiated validly, fail closed.

## 4. Direct / concise wording — HARD
`direct_concise` is the default. State the mathematical action plainly. Functional context stays when it carries modeling, units, interpretation, data, rate, percent, measurement, or transfer information; decorative story/filler does not.

## 5. Exact teacher-selected blueprint — HARD
Each checked family defaults to 1 question and has an exact requested count. Generate exactly that count per version. Do not auto-balance, substitute, or reallocate. Custom structures keep their exact count and remain teacher-defined unless they genuinely resolve to an existing canonical family.

## 6. Multi-course selection — HARD
A request may mix grades/courses/topics. Preserve each family's own scope and demand. Browse filters do not delete hidden selected families.

## 7. Builder previews — HARD
Every family row exposes Preview. A preview must be a complete original representative problem with the correct graph/table/diagram/model and response form. Metadata prose is never a preview. If a curated specimen/renderer is missing, display **Preview pending quality review** rather than inventing a fallback.

## 8. Difficulty — HARD
Difficulty changes legal parameters/cuing inside the selected family, not the evidence family itself. Mastery is not merely bigger numbers.

## 9. Parallel forms and refresh candidates — HARD
Across versions preserve family ID, I Can/evidence job, student action, response/representation role, slot sequence, and approximate difficulty. Vary only contract-authorized parameters.

For every generated Version + Problem slot, author and independently solve **3 original same-family candidates**: the initial item plus two alternates. In the finished adjustable worksheet, place **↻ New Question** directly below the Problem selector with `Question n of 3` status. Refresh changes only the selected slot, cycles through its three candidates before repeating, preserves that slot's workspace/visual sizing, and never changes family/evidence/difficulty role. Candidate pools are embedded locally so refresh works offline.

When an answer key is requested, provide **Open matching answer key** from the worksheet controls. It carries the active candidate-state map so the key matches refreshed questions. Opening the answer key from `CLICK_ME.html` without state shows the initial candidate set.

## 10. Student layout, true page view, and type — HARD
Use locked `worksheet_styles.css` byte-for-byte. US Letter portrait; `@page` margin 0.55 in; honor one/two-column selection in screen and print. Keep directions short and MathJax at surrounding-text size.

### True page view
The adjustable worksheet screen MUST show actual US Letter page boundaries rather than one continuous white canvas.

- Each printed sheet is represented by one `.worksheet.worksheet-page` element with a 1:1 screen page frame.
- Put page elements inside a version container such as `.worksheet-version[data-version="A"]`; do not use one infinitely growing `.worksheet` element for a multi-page version.
- On desktop screen, every page frame is exactly 8.5 in × 11 in with the same 0.55 in content margins used for print, a visible neutral gap between pages, and no content drawn across the page edge.
- In print, each `.worksheet-page` is one page fragment and must end with an explicit page break except the final page of the selected version.
- Page boundaries shown on screen MUST be the same boundaries used by browser Print. A dashed line or decorative page-break marker that does not control print pagination does not satisfy this rule.
- Keep a problem intact within a column/page whenever possible. If an enlarged workspace or visual no longer fits, move the whole problem to the next column/page or give it its own page; never clip it to preserve the old page count.
- Repaginate the active version after initial MathJax/typesetting, after **↻ New Question**, after workspace or graph/diagram sizing changes, after reset, and after any other action that changes measured problem height.
- Hidden candidates and hidden versions may not affect pagination.
- The screen page count and printed page count for the selected version must agree.

### Division notation default
For symbolic math, ordinary division is rendered with a fraction bar by default.

- Prefer MathJax `\frac{numerator}{denominator}` (or the equivalent display form) when one algebraic/numeric expression is divided by another.
- Example: author `\frac{t^7\cdot t^3}{t^4}` rather than `t^7\cdot t^3 \div t^4`.
- Do not use the Unicode division sign `÷` or a slash `/` merely as a compact substitute for a fraction in symbolic algebra, exponent rules, rational expressions, equations, scientific notation, or similar families.
- `÷` remains allowed only when the family explicitly teaches/assesses the division symbol or an elementary-operation representation where that notation is mathematically intentional.
- Conventional unit/rate notation such as `m/s` may use a slash when the slash is part of the unit convention rather than the operation being assessed.
- Apply the same notation rule to worksheet prompts, refresh candidates, worked solutions, and answer keys.

## 11. Per-problem layout controls — HARD
Finished `worksheet/worksheet.html` has a screen-only left rail on desktop: Version; Problem; ↻ New Question + candidate status; Workspace 0–1200%; Graph/diagram 70–160%; Reset selected problem; optional Open matching answer key; Print. Workspace/visual settings are stored per exact version/problem and persist when candidate changes. A moving slider with no rendered change is FAIL.

The layout controls and repagination system are coupled: any control that changes the selected problem's height must immediately recompute page assignment before print. Changing one problem may change later page breaks in that version, but it may not change another problem's stored workspace/visual setting.

## 12. Graphs and visuals — HARD
Follow packaged district response/graph standards and the authoritative graph tool for supported Cartesian graphs. Full-size print weights: grid 0.6 pt #aaaaaa; axes/arrows 1.8 pt #222222; relation 2.0 pt; major ticks 1.2 pt; relation exit arrows 1.5 pt when used. Deterministic SVG/HTML is appropriate for non-Cartesian instructional models when mathematically exact. Do not reveal answer visuals when construction itself is assessed.

## 13. Answer key — HARD
When requested, `teacher/answer_key.html` must match every version, slot, and candidate. Explanation items include required reasoning. No separate PDF is required.

## 14. CLICK_ME — HARD
Expose only **Open adjustable worksheet** and **Open answer key** (when requested). Do not expose QA/contracts/PDF buttons.

## 15. Response package — HARD
Return one response ZIP containing `CLICK_ME.html`, locked assets, adjustable worksheet HTML, optional answer key HTML, `data/request.json`, and `data/qa.json`. Adjustable HTML + browser Print is canonical.

## 16. QA — HARD
Verify exact selected counts, family conformity, source originality, direct wording, parallel equivalence, 3 candidates per slot, candidate answer correctness, refresh isolation/cycle/persistence, matching answer-key state transfer, print columns/margins, workspace 0/100/500/1200%, graph scaling/isolation, MathJax, graph line weights, deterministic visual accuracy, answer-key alignment, and screen/print rendering.

Also verify:
- every visible page is a real `.worksheet-page` print fragment, not a decorative marker;
- page frames are 8.5 in × 11 in on desktop screen with the locked 0.55 in margins;
- screen and print page boundaries/page counts agree for each version;
- no problem, graph, diagram, or workspace crosses/clips at a page bottom;
- repagination succeeds after refresh, workspace changes, graph/diagram changes, and reset;
- hidden candidates do not create pages or blank space;
- symbolic division uses a fraction bar by default and no stray `÷`/slash substitution remains unless the exact family/notation exception permits it.

Overall PASS is forbidden if any item drifts from its family, a required visual is wrong/missing, refresh swaps family/difficulty, candidate answers disagree, sizing controls fail, print layout collapses, page-view boundaries disagree with printed boundaries, content clips at a page edge, symbolic division is rendered with an unjustified `÷`/slash instead of a fraction bar, or the answer key mismatches.
