# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.3-pilot
REVISION: 2026-09-18.4

This tool builds original printable math practice from teacher-selected question structures. It combines clean parameterized fluency practice with conceptual, visual, application, and multi-representation practice. It must not reproduce copyrighted worksheet questions, wording, names, numbers, diagrams, or answer choices from reference sources.

## 1. Authority and core purpose — HARD

For question authoring, follow this authority order inside the request ZIP:

1. `response_contract/QUESTION_STRUCTURE_CORE.md`
2. `response_contract/MATH_WORKSHEET_GENERATOR_BANK.json`
3. `response_contract/PARALLEL_FAMILY_RULES.md`
4. this worksheet-builder contract
5. `request.json` teacher selections and family snapshots

Teacher selections control scope. The Question Structure Core controls universal evidence/response/representation behavior. The generator bank controls course/topic family behavior.

- Build the worksheet described in `request.json` automatically; no separate teacher prompt is required.
- Write ORIGINAL problems that instantiate the selected architectures.
- Lower Elementary, Grade 4, and Grade 5 are now first-class pilot catalogs; Grade 7 ratios remains supported. Other courses may use the generic families + custom topic until expanded.
- Treat course/topic browsing as a teacher-facing filter. The semantic `question_family_id` remains the generator identity.

## 2. Reference-use rule — HARD

Teacher-supplied sample worksheets and topic inventories are structural references only.

- Infer the I Can / evidence job, representation, response mode, pacing, and legitimate parameter ranges.
- Do not quote, trace, redraw, closely paraphrase, or numerically clone source problems.
- Do not reuse recognizable source names, exact answer choices, exact diagrams, or source-specific layout.
- A family describes the evidence job and architecture; it is not a stored source problem.

## 3. Parallel forms — HARD

When `version_count > 1`, generate legitimate parallel forms.

Across A/B/C/D for a matched question slot, preserve:
- the same learning target / I Can;
- the same evidence job and student action;
- the same family architecture;
- the same response mode and representation role;
- approximately the same difficulty and computational load.

Vary original parameters such as values, names, surface contexts, exact visual values/orientation, and answer-choice order when appropriate. Do not change the underlying task just to make a form look different.

The current UI supports 1, 2, 3, or 4 forms. Family definitions are not intrinsically limited to four.

## 4. Question mix — HARD

Honor the requested total question count.

- `fluency`: emphasize short direct items and repeated parameterized practice.
- `conceptual`: emphasize visuals, multiple representations, explanation, and application.
- `mixed`: deliberately combine fluency, conceptual/visual, representation/scaffold, and application/reasoning families.
- `custom_mix`: use teacher-entered per-family counts exactly; fail closed if the sum does not equal the requested total.

Difficulty bands:
- Intro = friendly entry values with one main decision.
- Standard = normal grade-level variation and less cuing.
- Mastery = transfer, multi-step dependency, or representation changes that preserve the same target.

Do not make mastery merely larger numbers.

## 5. Number domains — HARD
Respect the teacher-selected domains and the selected family. Avoid ugly arithmetic unless instructionally intentional. Answers should simplify cleanly when simplification is part of the target.

## 6. Student layout, print geometry, and type — HARD
Use `assets/worksheet_styles.css` byte-for-byte as the base stylesheet.

- US Letter portrait.
- Preserve the locked `@page` margin of 0.55 in.
- Honor `layout.two_column` in SCREEN and PRINT.
- A visual-heavy item may span both columns only when needed for readability; record the exception in QA.
- Keep directions short.
- Give each problem enough workspace without oversized cards.
- Use MathJax for mathematical notation, but ordinary prose numerals may remain plain text.
- Inline MathJax stays at surrounding-text size.
- Responsive one-column screen rules must be inside `@media screen` and may not collapse two-column print.

## 7. Per-version / per-problem layout controls — HARD
The finished `worksheet/worksheet.html` must include screen-only controls in a left rail on desktop:

1. Version dropdown limited to generated versions.
2. Problem dropdown 1..N.
3. Workspace slider + exact percent input, 60%-180%.
4. Graph/diagram slider + exact percent input, 70%-160%.
5. Reset selected problem.
6. Print.

Each worksheet root uses `class="worksheet" data-version="A"` etc. Each problem uses `class="problem" data-problem="1"` etc.

Workspace and graph dimensions are stored per exact version/problem. Changing A3 must not alter A4 or B3. Persist values in localStorage when practical. Disable graph controls when the selected problem has no visual.

A slider that moves while the rendered problem does not change is a FAIL.

## 8. Graphs and quantitative visuals — HARD
Follow `DISTRICT_RESPONSE_BUILD_STANDARD.md` and `DISTRICT_GRAPH_RENDERING_STANDARD.md`. Use the packaged authoritative Cartesian graph tool for supported coordinate graphs. Full-size Cartesian print weights remain:
- grid 0.6 pt `#aaaaaa`
- axes/arrows 1.8 pt `#222222`
- relation 2.0 pt
- major ticks 1.2 pt
- relation exit arrows 1.5 pt when used

For deterministic non-Cartesian visuals—base-ten blocks, fraction area models, pattern-block-style models, clocks, rulers, strip/tape diagrams, tables, open number lines, hundred charts, dot/line plots, simple geometry—clean SVG/HTML is appropriate when mathematically exact and answer-neutral.

## 9. Answer key — HARD
When requested, create `teacher/answer_key.html` matching exact student versions and order. Answers must include the reasoning required by explanation items and accurate visual answers. No separate answer-key PDF is required.

## 10. CLICK_ME — HARD
`CLICK_ME.html` contains only:
1. **Open adjustable worksheet** -> `worksheet/worksheet.html`
2. **Open answer key** -> `teacher/answer_key.html` when requested

Do not expose PDFs, QA, request JSON, CSS, contracts, or graph assets to the teacher dashboard. QA still exists internally.

## 11. Response package — HARD
Return one response ZIP containing `CLICK_ME.html`, locked assets, `worksheet/worksheet.html`, optional `teacher/answer_key.html`, `data/request.json`, and `data/qa.json`. No worksheet PDF is required; adjustable HTML + browser Print is canonical.

## 12. QA — HARD
Record at minimum:
- question count per version;
- selected family IDs and counts;
- family architecture preserved across parallel forms;
- difficulty distribution consistent across versions;
- original source-copying check;
- requested column count preserved in print;
- 0.55 in print margin preserved;
- per-version/per-problem DOM identity;
- functional selected-problem workspace and graph tests;
- cross-problem and cross-version isolation;
- MathJax size normalization;
- graph-tool and line-weight compliance;
- deterministic visual accuracy;
- answer-key alignment;
- CLICK_ME exposes only classroom-use actions;
- screen and print visual checks.

Overall PASS is not allowed if a required visual is inaccurate/missing, parallel forms drift to different evidence jobs, a layout control changes the wrong problem, requested two-column print collapses, inline math is visibly oversized, or the answer key disagrees.
