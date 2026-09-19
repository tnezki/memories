# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.4-pilot
REVISION: 2026-09-18.5

This tool builds original printable math practice from teacher-selected question structures. It must not reproduce copyrighted worksheet questions, wording, names, numbers, diagrams, or answer choices from reference sources.

## 1. Authority and core purpose — HARD

For question authoring, follow this authority order inside the request ZIP:

1. `response_contract/QUESTION_STRUCTURE_CORE.md`
2. `response_contract/MATH_WORKSHEET_GENERATOR_BANK.json`
3. `response_contract/PARALLEL_FAMILY_RULES.md`
4. this worksheet-builder contract
5. `request.json` teacher selections and family snapshots

Teacher selections control scope and exact counts. The Question Structure Core controls universal evidence/response/representation behavior. The generator bank controls family behavior.

- Build the worksheet described in `request.json` automatically; no separate teacher prompt is required.
- Write ORIGINAL problems that instantiate the selected architectures.
- Lower Elementary, Grade 4, Grade 5, and Grade 7 ratios are first-class pilot catalogs.
- A worksheet may intentionally mix selected skills from multiple grade/course catalogs.
- Treat grade/course filters and topic cards as teacher-facing browsing tools. The semantic `question_family_id` remains the generator identity.

## 2. Reference-use rule — HARD

Teacher-supplied sample worksheets and topic inventories are structural references only.

- Infer the I Can / evidence job, representation, response mode, pacing, and legitimate parameter ranges.
- Do not quote, trace, redraw, closely paraphrase, or numerically clone source problems.
- Do not reuse recognizable source names, exact answer choices, exact diagrams, or source-specific layout.
- A family describes the evidence job and architecture; it is not a stored source problem.

## 3. Exact teacher-selected blueprint — HARD

The worksheet has no independent target question-count control. `question_count_per_version` is derived from the teacher's exact family selections.

Each checked catalog family defaults to `requested_count = 1`. The teacher may increase or decrease that family's quantity before creating the request ZIP.

For every selected family:
- generate exactly `requested_count` items per version;
- preserve the selected family identity and evidence job;
- do not auto-balance, substitute another family, or reallocate counts based on a generic practice mode;
- do not silently change a selected family's number domain or representation simply to create variety.

A custom family, when enabled, also has an exact requested count. The total questions per version equals the sum of all selected family counts plus the custom count.

## 4. Multi-grade / multi-topic selection — HARD

A request may contain families from more than one grade/course and more than one topic.

- Preserve each selected family's own course/topic metadata.
- Do not raise or lower a family's mathematical demand to make all selected items look like one grade level.
- The worksheet title may be generic even when the blueprint spans grades.
- The optional learning-target field is advisory; it does not override explicit selected families.
- Grade/course browse filters are not themselves question selections. Hidden/unfiltered selected families remain part of the blueprint until explicitly removed.

## 5. Difficulty profile — HARD

The broad difficulty profile guides parameter choices inside each selected family; it does not authorize replacing the family.

- Intro-heavy = favor friendly values, stronger cues, and the easier valid parameter range.
- Balanced = use a reasonable spread of intro/standard and occasional mastery where the family supports it.
- Mastery-heavy = favor transfer, less cuing, dependency, or harder valid parameters where the family supports them.

Do not make mastery merely larger numbers. Respect each family's own allowed difficulty and number-domain constraints from the generator bank.

## 6. Parallel forms — HARD

When `version_count > 1`, generate legitimate parallel forms.

Across A/B/C/D for a matched question slot, preserve:
- the same learning target / I Can;
- the same evidence job and student action;
- the same family architecture;
- the same response mode and representation role;
- the same requested family count and slot sequence;
- approximately the same difficulty and computational load.

Vary original parameters such as values, names, surface contexts, exact visual values/orientation, and answer-choice order when appropriate. Do not change the underlying task just to make a form look different.

The current UI supports 1, 2, 3, or 4 forms. Family definitions are not intrinsically limited to four.

## 7. Student layout, print geometry, and type — HARD

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

## 8. Per-version / per-problem layout controls — HARD

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

## 9. Graphs and quantitative visuals — HARD

Follow `DISTRICT_RESPONSE_BUILD_STANDARD.md` and `DISTRICT_GRAPH_RENDERING_STANDARD.md`. Use the packaged authoritative Cartesian graph tool for supported coordinate graphs. Full-size Cartesian print weights remain:
- grid 0.6 pt `#aaaaaa`
- axes/arrows 1.8 pt `#222222`
- relation 2.0 pt
- major ticks 1.2 pt
- relation exit arrows 1.5 pt when used

For deterministic non-Cartesian visuals—base-ten blocks, fraction area models, pattern-block-style models, clocks, rulers, strip/tape diagrams, tables, open number lines, hundred charts, dot/line plots, simple geometry—clean SVG/HTML is appropriate when mathematically exact and answer-neutral.

## 10. Answer key — HARD

When requested, create `teacher/answer_key.html` matching exact student versions and order. Answers must include the reasoning required by explanation items and accurate visual answers. No separate answer-key PDF is required.

## 11. CLICK_ME — HARD

`CLICK_ME.html` contains only:
1. **Open adjustable worksheet** -> `worksheet/worksheet.html`
2. **Open answer key** -> `teacher/answer_key.html` when requested

Do not expose PDFs, QA, request JSON, CSS, contracts, or graph assets to the teacher dashboard. QA still exists internally.

## 12. Response package — HARD

Return one response ZIP containing `CLICK_ME.html`, locked assets, `worksheet/worksheet.html`, optional `teacher/answer_key.html`, `data/request.json`, and `data/qa.json`. No worksheet PDF is required; adjustable HTML + browser Print is canonical.

## 13. QA — HARD

Record at minimum:
- derived requested question count vs actual question count per version;
- every selected family ID and exact requested/actual count;
- selected course/topic metadata preserved;
- no unselected family substituted into the worksheet;
- family architecture preserved across parallel forms;
- difficulty distribution consistent across versions and valid for each family;
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

Overall PASS is not allowed if the actual question count differs from the derived selected blueprint, a selected family's count is wrong, an unselected family is substituted, a required visual is inaccurate/missing, parallel forms drift to different evidence jobs, a layout control changes the wrong problem, requested two-column print collapses, inline math is visibly oversized, or the answer key disagrees.
