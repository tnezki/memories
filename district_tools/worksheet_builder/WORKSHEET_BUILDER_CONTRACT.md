# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.6-pilot
REVISION: 2026-09-19.2

This tool builds original printable math practice from teacher-selected canonical question families. It must not reproduce copyrighted worksheet questions, wording, names, numbers, diagrams, answer choices, or source-specific layouts from reference sources.

## 1. Authority and core purpose — HARD

For question authoring, follow this authority order inside the request ZIP:

1. `response_contract/QUESTION_STRUCTURE_CORE.md`
2. `response_contract/MATH_WORKSHEET_GENERATOR_BANK.json`
3. `response_contract/PARALLEL_FAMILY_RULES.md`
4. this worksheet-builder contract
5. `request.json` teacher selections and family snapshots

The packaged `MATH_WORKSHEET_GENERATOR_BANK.json` is a generated compatibility aggregate of the current canonical math-family registry and course-family maps. Its `family_contracts` are executable contracts, not suggestion text.

Teacher selections control scope and exact counts. Question Structure Core controls universal evidence/response/representation behavior. The selected family contract controls the exact student action, response mode, representation role, parameter validity, answer rule, and legitimate parallel variation.

- Build the worksheet described in `request.json` automatically; no separate teacher prompt is required.
- Write ORIGINAL problems that instantiate the selected family contracts.
- Lower Elementary, Grade 4, Grade 5, Grade 6, Grade 7, and Grade 8 are first-class active catalogs.
- A worksheet may intentionally mix selected skills from multiple grade/course catalogs.
- Treat grade/course filters and topic cards as teacher-facing browsing tools. The semantic `question_family_id` remains the generator identity.
- Algebra 1, Geometry, Algebra 2, Precalculus, and Calculus remain future course maps until their teacher reference sets are incorporated; do not fabricate comprehensive catalogs for them from generic labels alone.

## 2. Reference-use rule — HARD

Teacher-supplied sample worksheets, topic inventories, and external worksheet catalogs are structural references only.

They may inform:
- target skill / I Can scope;
- evidence job and student action;
- representation role;
- response mode;
- useful mathematical property/options;
- parameter ranges and clean-answer constraints;
- pacing and relative difficulty.

They may NOT be used to:
- quote, trace, redraw, closely paraphrase, or numerically clone source problems;
- reuse recognizable source names, exact answer choices, exact diagrams, or source-specific layout;
- store source questions as a hidden bank.

A canonical family is a generator contract for an evidence architecture, not a stored source problem.

## 3. Canonical family lock — HARD

Before authoring any selected item, resolve its exact `question_family_id` in `family_contracts`.

The final student item MUST agree with that contract on:
- `evidence_job`;
- `student_action`;
- allowed `response_modes`;
- `representation_modes` and actual render route;
- generator prompt architecture;
- parameter/validity constraints;
- answer rule;
- parallel invariants and allowed variation;
- family quality gates.

The family label, category, summary, or teacher-facing catalog row is not enough to generate a question. Do not free-write a vaguely related problem and attach the selected family ID afterward.

If a requested family cannot be instantiated validly, fail closed for that item rather than silently substituting another family.

## 4. Direct / concise wording — HARD

`direct_concise` is the default worksheet wording profile.

- State the mathematical action plainly.
- Keep only givens needed to solve or interpret the task.
- Do not add names, stories, repeated directions, or decorative context merely to make a procedural item sound authentic.
- Context is appropriate when the context is mathematically functional: it determines a model, unit, interpretation, rate, percent, measurement, data relationship, or other evidence requirement.
- Do not strip necessary context from genuine modeling/application families.

A shorter prompt is preferred when it collects the same evidence more clearly.

## 5. Exact teacher-selected blueprint — HARD

The worksheet has no independent target question-count control. `question_count_per_version` is derived from the teacher's exact family selections.

Each checked catalog family defaults to `requested_count = 1`. The teacher may increase or decrease that family's quantity before creating the request ZIP.

For every selected family:
- generate exactly `requested_count` visible problem slots per version;
- preserve the selected family identity and evidence job;
- do not auto-balance, substitute another family, or reallocate counts based on a generic practice mode;
- do not silently change number domain, response mode, or representation simply to create variety.

Repeatable teacher custom structures also have exact counts. A custom structure remains teacher-defined unless it genuinely resolves to an existing canonical family; do not manufacture a canonical family ID for it.

The visible question count per version equals the sum of all selected catalog-family counts plus all custom-entry counts. Hidden refresh alternates defined in Section 12 do NOT increase the visible question count.

## 6. Multi-grade / multi-topic selection — HARD

A request may contain families from more than one grade/course and more than one topic.

- Preserve each selected family's own course/topic metadata.
- Do not raise or lower a family's mathematical demand to make all selected items look like one grade level.
- The worksheet title may be generic even when the blueprint spans grades.
- Grade/course browse filters are not themselves question selections. Hidden/unfiltered selected families remain part of the blueprint until explicitly removed.

## 7. Builder UI and previews — HARD

The teacher-facing builder is intentionally compact.

- Section 1: worksheet setup and grade/course filters.
- Section 2: versions, broad difficulty, **Two-column student pages**, and **Include answer key**.
- Section 3: browse/search question structures, exact per-family quantities, and repeatable custom structure entries.
- Section 4: exact selected-question tray plus Reset and **Create Worksheet Request ZIP**.
- Do not reintroduce separate builder sections for student-layout sliders, request summary, or teacher notes.
- The request ZIP downloads directly from the Create button; no second download button is required.

Every catalog skill row must expose a magnifying-glass Preview control. The preview is a teacher-facing structural sample only and must:
- show a complete representative student problem, not merely a stem description;
- render the representative graph, table, diagram, model, algorithm, or figure whenever the family uses one;
- include representative answer choices or response space appropriate to the family's response mode;
- preserve the family contract's actual evidence/representation architecture;
- use original preview values/context and never reproduce source questions;
- remain clearly labeled representative so the teacher knows the generated worksheet will use new parameters.

## 8. Difficulty profile — HARD

The broad difficulty profile guides parameter choices inside each selected family; it does not authorize replacing the family.

- Intro-heavy = favor friendly values, stronger cues, and the easier valid parameter range.
- Balanced = use a reasonable spread of intro/standard and occasional mastery where the family supports it.
- Mastery-heavy = favor transfer, less cuing, dependency, or harder valid parameters where the family supports them.

Do not make mastery merely larger numbers. Respect the family contract's validity and difficulty constraints.

## 9. Parallel forms — HARD

When `version_count > 1`, generate legitimate parallel forms.

Across A/B/C/D for a matched question slot, preserve:
- the same canonical family ID;
- the same learning target / I Can;
- the same evidence job and student action;
- the same response mode and representation role;
- the same requested family count and slot sequence;
- approximately the same difficulty and computational load.

Vary only contract-authorized parameters such as values, functional surface contexts, exact visual values/orientation, and answer-choice order when appropriate. Do not change the underlying task just to make a form look different.

The current UI supports 1, 2, 3, or 4 forms. Family definitions are not intrinsically limited to four.

## 10. Student layout, print geometry, and type — HARD

Use `assets/worksheet_styles.css` byte-for-byte as the base stylesheet.

- US Letter portrait.
- Preserve the locked `@page` margin of 0.55 in.
- Honor `layout.two_column` in SCREEN and PRINT.
- A visual-heavy item may span both columns only when needed for readability; record the exception in QA.
- Keep directions short.
- Give each problem enough workspace without oversized cards by default.
- Use MathJax for mathematical notation, but ordinary prose numerals may remain plain text.
- Inline MathJax stays at surrounding-text size.
- Responsive one-column screen rules must be inside `@media screen` and may not collapse two-column print.

## 11. Per-version / per-problem layout controls — HARD

The finished `worksheet/worksheet.html` must include screen-only controls in a left rail on desktop:

1. Version dropdown limited to generated versions.
2. Problem dropdown 1..N.
3. **Refresh / New Question** control for the selected problem, using a refresh-arrow icon (`↻` or equivalent) and an accessible label.
4. Small screen-only variant status, for example `Question 1 of 3`.
5. Workspace slider + exact percent input, **0%-1200%**.
6. Graph/diagram slider + exact percent input, 70%-160%.
7. Reset selected problem layout.
8. **Open matching answer key** when an answer key exists.
9. Print.

Place the Refresh / New Question control directly below the Problem selector so the teacher can change the selected question while watching the worksheet.

Each worksheet root uses `class="worksheet" data-version="A"` etc. Each problem uses `class="problem" data-problem="1"` etc.

Workspace and graph dimensions are stored per exact version/problem slot. Changing A3 must not alter A4 or B3. Persist layout values in localStorage when practical. Disable graph controls when the selected problem has no visual.

The workspace default remains `--workspace-height: .62in`. The selected problem's workspace height is calculated as:

`workspaceHeightIn = 0.62 * workspacePercent / 100`

and written to `--problem-workspace-height` on that selected problem only.

- `0%` must collapse workspace completely; do not impose a positive CSS `min-height`.
- The upper range must be high enough for one selected problem to expand to approximately a full printable page when desired. The locked range is 0%-1200%.
- Large workspace values may naturally push the selected problem to its own page/column; do not clip the workspace to preserve compact pagination.
- Refreshing a question must preserve that slot's current workspace and graph/diagram scale settings.
- Reset selected problem resets layout sizing only; it does not silently change the active question variant.

A slider that moves while the rendered problem does not change is a FAIL.

## 12. Refreshable question variants — HARD

The finished adjustable worksheet must allow the teacher to refresh the currently selected problem and see a new legitimate instance from the SAME family.

### Candidate pool
For every canonical family slot in every generated worksheet version:
- pre-generate exactly **3 complete candidate instances**: the initial visible instance plus 2 refresh alternates;
- candidate 1 is the default visible question;
- candidates 2 and 3 remain hidden until selected by the refresh control;
- hidden candidates do not count as additional worksheet questions;
- the response package remains fully self-contained and must not call an online generator when Refresh is clicked.

For custom teacher-defined structures, create the same 3-candidate pool only when the custom description provides enough information to create legitimate parallels. Otherwise disable Refresh for that custom slot and show a brief screen-only message such as `Refresh unavailable for this custom question`.

### Same-family lock
All candidates for one slot MUST preserve:
- the same `question_family_id`;
- the same evidence job and student action;
- the same response mode;
- the same representation role and render semantics;
- the same approximate difficulty / computational load;
- the same family-specific validity constraints and answer rule.

Only contract-authorized variation is allowed: values, coordinates, data, model counts, legal orientation, functional context, or answer-choice order as appropriate. Refresh must never substitute a different family merely because it is nearby in the same topic.

The three candidates must be meaningfully distinct. Exact prompt/value duplicates are a FAIL.

### Refresh behavior
- Refresh affects only the currently selected Version + Problem slot.
- Cycle through the 3 candidates without repeating until all have been shown; after candidate 3, the next refresh may cycle to candidate 1.
- The displayed variant status updates immediately.
- MathJax, graph/diagram rendering, workspace, and answer-neutrality must remain correct after every swap.
- Only the active candidate may appear in screen flow and print flow; hidden candidates must not create blank space, extra pages, duplicate numbering, or print output.
- Preserve the active candidate map in a compact URL fragment or equivalent deterministic self-contained state so a browser reload can restore the chosen question variants without relying solely on `file://` localStorage behavior.

### Matching answer key state
When `answer_key = true`:
- `teacher/answer_key.html` must contain the answers for all pre-generated candidates;
- the worksheet left rail must expose **Open matching answer key**;
- that control passes the current compact candidate-state map in the answer-key URL fragment/query;
- the answer key reads that state and displays/prints the exact active candidate answer for every worksheet slot;
- opening the answer key directly from `CLICK_ME.html` with no candidate state defaults to candidate 1 for every slot;
- the matching answer key must remain complete for explanation/visual-response items.

This state-transfer mechanism is required so refreshing one problem can never make the printed answer key silently disagree with the worksheet.

## 13. Graphs and quantitative visuals — HARD

Follow `DISTRICT_RESPONSE_BUILD_STANDARD.md` and `DISTRICT_GRAPH_RENDERING_STANDARD.md`. Use the packaged authoritative Cartesian graph tool for supported coordinate graphs. Full-size Cartesian print weights remain:
- grid 0.6 pt `#aaaaaa`
- axes/arrows 1.8 pt `#222222`
- relation 2.0 pt
- major ticks 1.2 pt
- relation exit arrows 1.5 pt when used

For deterministic non-Cartesian visuals—base-ten blocks, fraction area models, clocks, rulers, strip/tape diagrams, balance models, tables, open number lines, dot/line plots, simple geometry—clean SVG/HTML is appropriate when mathematically exact and answer-neutral.

## 14. Answer key — HARD

When requested, create `teacher/answer_key.html` matching exact student versions, order, and active refresh candidates. Answers must include the reasoning required by explanation items and accurate visual answers. No separate answer-key PDF is required.

## 15. CLICK_ME — HARD

`CLICK_ME.html` contains only:
1. **Open adjustable worksheet** -> `worksheet/worksheet.html`
2. **Open answer key** -> `teacher/answer_key.html` when requested

Do not expose PDFs, QA, request JSON, CSS, contracts, or graph assets to the teacher dashboard. QA still exists internally.

## 16. Response package — HARD

Return one response ZIP containing `CLICK_ME.html`, locked assets, `worksheet/worksheet.html`, optional `teacher/answer_key.html`, `data/request.json`, and `data/qa.json`. No worksheet PDF is required; adjustable HTML + browser Print is canonical.

The alternate candidate pool may be embedded in `worksheet/worksheet.html` and `teacher/answer_key.html` or stored in a local relative data/asset file. It must remain inside the response ZIP and work offline.

## 17. QA — HARD

Record at minimum:
- derived requested visible question count vs actual visible question count per version;
- every selected canonical family ID and exact requested/actual visible count;
- family-contract conformity for every visible item and every refresh candidate: evidence job, student action, response mode, representation, validity constraints, and answer rule;
- exactly 3 candidates for each refreshable canonical slot;
- refresh-candidate uniqueness check;
- selected course/topic metadata preserved;
- no unselected family substituted into the worksheet or refresh pool;
- family architecture preserved across parallel forms and refresh candidates;
- direct/concise wording check and decorative-prose check;
- difficulty distribution consistent across versions and refresh candidates and valid for each family;
- original source-copying check;
- requested column count preserved in print;
- 0.55 in print margin preserved;
- per-version/per-problem DOM identity;
- workspace tests at 0%, 100%, at least 500%, and the full-page-capable upper range;
- functional selected-problem graph test;
- cross-problem and cross-version layout isolation;
- refresh isolation: refreshing A3 changes A3 only;
- refresh preserves the selected slot's workspace and graph/diagram sizing;
- refresh cycles through candidates and updates variant status;
- hidden candidates do not appear in print or affect pagination;
- candidate-state URL fragment/query restores after reload;
- matching-answer-key state reproduces the exact active candidate for every slot;
- large workspace does not clip and may move the problem to a new page/column;
- MathJax size normalization;
- graph-tool and line-weight compliance;
- deterministic visual accuracy;
- answer-key alignment;
- CLICK_ME exposes only classroom-use actions;
- screen and print visual checks.

Overall PASS is not allowed if the actual visible question count differs from the selected blueprint, a selected family's count is wrong, a final item or refresh candidate drifts from its family contract, an unselected family is substituted, a required visual is inaccurate/missing, parallel forms or refresh candidates drift to different evidence jobs, decorative prose obscures a simple task, a layout control changes the wrong problem, Refresh changes the wrong slot, Refresh loses the slot's sizing, workspace cannot collapse to 0%, large workspace clips, hidden alternates print, requested two-column print collapses, inline math is visibly oversized, or the matching answer key disagrees with the active refreshed worksheet.
