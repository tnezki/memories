# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.6-pilot
REVISION: 2026-09-19.3

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

## 10. Student layout and type — HARD
Use locked `worksheet_styles.css` byte-for-byte. US Letter portrait; `@page` margin 0.55 in; honor one/two-column selection in screen and print. Keep directions short and MathJax at surrounding-text size.

## 11. Per-problem layout controls — HARD
Finished `worksheet/worksheet.html` has a screen-only left rail on desktop: Version; Problem; ↻ New Question + candidate status; Workspace 0–1200%; Graph/diagram 70–160%; Reset selected problem; optional Open matching answer key; Print. Workspace/visual settings are stored per exact version/problem and persist when candidate changes. A moving slider with no rendered change is FAIL.

## 12. Graphs and visuals — HARD
Follow packaged district response/graph standards and the authoritative graph tool for supported Cartesian graphs. Full-size print weights: grid 0.6 pt #aaaaaa; axes/arrows 1.8 pt #222222; relation 2.0 pt; major ticks 1.2 pt; relation exit arrows 1.5 pt when used. Deterministic SVG/HTML is appropriate for non-Cartesian instructional models when mathematically exact. Do not reveal answer visuals when construction itself is assessed.

## 13. Answer key — HARD
When requested, `teacher/answer_key.html` must match every version, slot, and candidate. Explanation items include required reasoning. No separate PDF is required.

## 14. CLICK_ME — HARD
Expose only **Open adjustable worksheet** and **Open answer key** (when requested). Do not expose QA/contracts/PDF buttons.

## 15. Response package — HARD
Return one response ZIP containing `CLICK_ME.html`, locked assets, adjustable worksheet HTML, optional answer key HTML, `data/request.json`, and `data/qa.json`. Adjustable HTML + browser Print is canonical.

## 16. QA — HARD
Verify exact selected counts, family conformity, source originality, direct wording, parallel equivalence, 3 candidates per slot, candidate answer correctness, refresh isolation/cycle/persistence, matching answer-key state transfer, print columns/margins, workspace 0/100/500/1200%, graph scaling/isolation, MathJax, graph line weights, deterministic visual accuracy, answer-key alignment, and screen/print rendering. Overall PASS is forbidden if any item drifts from its family, a required visual is wrong/missing, refresh swaps family/difficulty, candidate answers disagree, sizing controls fail, print layout collapses, or the answer key mismatches.
