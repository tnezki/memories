# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.2-pilot
REVISION: 2026-09-18.3

This tool builds original printable math practice from teacher-selected question structures. It combines clean parameterized fluency practice with conceptual, visual, application, and multi-representation practice. It must not reproduce copyrighted worksheet questions, wording, names, numbers, diagrams, or answer choices from reference sources.

## 1. Core purpose - HARD

- Build the worksheet described in `request.json` automatically; no separate teacher prompt is required.
- Use the selected course, topic, question count, practice mode, difficulty mix, number-domain settings, selected family snapshots, and custom-family description as the primary authority.
- Write ORIGINAL problems that instantiate the selected architectures. Preserve structure, representation, and difficulty while changing surface context and values.
- The pilot catalog is seeded for Grade 7 Ratios & Proportional Relationships but the schema is intentionally expandable from Grade 6 through Calculus.

## 2. Reference-use rule - HARD

The packaged `QUESTION_STRUCTURE_CATALOG.json` contains descriptive abstractions derived from broad worksheet conventions and teacher-supplied examples.

- Use those abstractions as structural guidance only.
- Do not quote, trace, redraw, paraphrase closely, or numerically clone source problems.
- Do not use recognizable source names, recipe names, labels, word-bank orderings, or exact diagram arrangements.
- A family describes the evidence job and representation; it is not a source question to copy.

## 3. Question mix - HARD

Honor the requested total question count.

Practice modes:
- `fluency`: emphasize short direct items and repeated parameterized practice.
- `conceptual`: emphasize visuals, multiple representations, explanation, and application.
- `mixed`: deliberately combine fluency, conceptual/visual, representation/scaffold, and application/reasoning families.
- `custom_mix`: use the teacher-entered per-family counts exactly when the sum equals the requested total; if not, fail closed and record the mismatch.

Difficulty bands:
- Intro = straightforward entry examples with friendly values and one main decision.
- Standard = normal grade-level variation, mixed representations, and less cuing.
- Mastery = transfer, multi-step reasoning, fractional/decimal values when allowed, or representation changes without changing the target skill.

Do not make mastery merely larger numbers.

## 4. Number-domain controls - HARD

Respect the teacher-selected domains: whole numbers, integers/negatives, fractions, decimals. Use only domains appropriate to the chosen course/topic and selected family. Avoid ugly arithmetic unless it is instructionally intentional. Answers should simplify cleanly when simplification is part of the skill.

## 5. Student layout, print geometry, and type - HARD

Use `assets/worksheet_styles.css` byte-for-byte as the base stylesheet.

- US Letter portrait.
- Preserve the locked `@page` margin of 0.55 in.
- Honor `request.json -> layout.two_column` in both SCREEN and PRINT. A two-column worksheet must remain two columns when the Print button/browser print dialog opens.
- A visual-heavy item may span both columns only when one-column placement would make the visual unreadable; record any span exception in QA.
- Keep directions short.
- Give each problem enough white space to work without turning the sheet into oversized cards.
- Do not use decorative shaded problem cards.
- Use MathJax for mathematical notation, but do not wrap ordinary prose numerals in MathJax when plain text is sufficient.
- Inline MathJax MUST remain at the same visual font size as surrounding prose.
- Do not add per-question inline font-size overrides. The locked worksheet stylesheet owns student typography.

### Print-column regression rule

Responsive screen rules must be scoped with `@media screen`. A narrow-screen one-column fallback must never override the requested print column count. Before PASS, open print preview from the worksheet's Print button and verify the requested column count on the printed pages.

## 6. Per-version / per-problem layout controls - HARD

The finished `worksheet/worksheet.html` MUST include screen-only layout controls in the left rail on desktop. These controls edit ONE exact problem at a time.

Required controls:

1. **Version** dropdown: A-D, limited to the versions that exist.
2. **Problem** dropdown: 1 through the requested problem count.
3. **Workspace scale** slider + exact percent input, range 60%-180%.
4. **Graph/diagram scale** slider + exact percent input, range 70%-160%.
5. **Reset selected problem** button.
6. **Print** button.

The controls must make the selected target obvious, for example `Version A · Problem 7`.

### Required DOM identity

Every version and problem must be addressable without depending on visible text:

- each version root has `class="worksheet"` and `data-version="A"` (or B/C/D);
- each problem has `class="problem"` and `data-problem="1"` through the final problem number.

The worksheet may also include internal stable IDs, but the two data attributes above are required.

### Workspace behavior

Every problem must contain a usable response/workspace surface unless the problem's required response structure already supplies the writing/drawing surface. A plain direct-response item should not omit its workspace merely because the default height is small.

The selected problem owns its own final workspace dimension. The locked CSS uses:

- global default: `--workspace-height: .62in`;
- problem override: `--problem-workspace-height`.

The worksheet JavaScript must calculate:

`workspaceHeightIn = 0.62 * workspacePercent / 100`

and set `--problem-workspace-height` on the selected `.problem` element only.

Changing Version A / Problem 3 must not change Version A / Problem 4 or Version B / Problem 3.

### Graph/diagram behavior

The selected problem owns its own final graph/diagram width. The locked CSS uses:

- global default: `--graph-width: 3in`;
- problem override: `--problem-graph-width`.

The worksheet JavaScript must calculate:

`graphWidthIn = 3.00 * graphPercent / 100`

and set `--problem-graph-width` on the selected `.problem` element only.

If the selected problem has no graph or diagram, disable the graph controls and show a short neutral note such as `No graph/diagram in this problem.` Do not apply the graph change to some other problem.

### Initial values and persistence

- `request.json -> layout.workspace_scale_percent` and `layout.graph_scale_percent` are the INITIAL defaults for every problem.
- After first render, each version/problem may diverge independently.
- Persist per-version/per-problem values in `localStorage` when practical. Keys must include both version and problem number.
- On Version/Problem dropdown change, load that problem's current values into the controls without changing the page.
- Reset affects the selected problem only and returns it to the request defaults.
- Workspace and graph controls remain independent.

### Functional QA

Before PASS, test at least:

- Version A / Problem 1 workspace at 80%;
- a different problem workspace at 140%;
- one problem with a graph at two graph sizes;
- switch versions and prove the other version retains its own values;
- prove workspace changes do not change graph width and graph changes do not change workspace height.

A slider that moves while the rendered problem does not change is a FAIL.

## 7. Graphs and quantitative visuals - HARD

Follow BOTH:

- `response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md`
- `response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md`

For every Cartesian graph type supported by the packaged graph tool, use the packaged authoritative entrypoint:

`response_contract/graph_tool/~graph_tool_v14.py`

with v13 and v12 staged beside it. Do not replace a supported Cartesian graph with hand-drawn SVG, improvised HTML axes, or ad hoc plotting code merely because that is quicker.

Full-size Cartesian print weights are locked to the teacher-approved 2026-09-18 standard:
- grid: 0.6 pt, `#aaaaaa`
- axes and axis arrows: 1.8 pt, `#222222`
- plotted relation: 2.0 pt
- major ticks: 1.2 pt
- relation exit arrows: 1.5 pt when used

Resize the completed graph through layout geometry only. Compact multi-panel graph-tool types may retain their built-in proportional weights.

For deterministic non-Cartesian visuals such as ratio tables, double number lines, simple shape arrays, scale drawings, and geometric polygons, clean SVG/HTML is appropriate when mathematically exact. Do not use generative imagery for quantitative diagrams.

## 8. Versions - HARD

Create the number of versions requested: 1, 2, or 4.

- Keep the same selected family distribution and difficulty profile across versions.
- Change values, names/contexts, problem order, and answer-choice order when appropriate.
- Do not change the underlying evidence architecture merely to make versions look different.
- Label versions A-D clearly.

## 9. Answer key - HARD

When requested, create `teacher/answer_key.html` matching the exact student versions and order. Answers must be concise but include required reasoning for explanation items. Visual answers must be mathematically accurate. The answer key must have clean browser-print behavior; a separate answer-key PDF is not required.

## 10. Teacher dashboard / CLICK_ME - HARD

The dashboard exists to make the teacher workflow obvious, not to expose implementation files.

`CLICK_ME.html` must contain only the classroom-use actions below:

1. **Open adjustable worksheet** -> `worksheet/worksheet.html`
2. **Open answer key** -> `teacher/answer_key.html` when an answer key was requested

Do NOT show buttons/links for:
- worksheet PDF;
- answer-key PDF;
- `data/qa.json`;
- `data/request.json`;
- CSS/contracts/graph assets;
- duplicate HTML/PDF versions of the same resource.

QA still exists internally and must PASS. It is simply not part of the normal teacher-facing dashboard.

## 11. Response package - HARD

Return ONE response ZIP with:

```text
CLICK_ME.html
assets/
  dashboard_styles.css
  worksheet_styles.css
  graphs/        (when used)
  visuals/       (when used)
worksheet/
  worksheet.html
teacher/
  answer_key.html   (when requested)
data/
  request.json
  qa.json
```

No worksheet PDF or answer-key PDF is required. The adjustable HTML + browser Print button is the canonical printable worksheet source.

## 12. QA - HARD

In addition to shared district QA requirements, record:

- requested vs actual question count per version;
- selected family IDs and actual counts;
- difficulty distribution;
- requested column count preserved in screen and print preview;
- locked 0.55 in print margin preserved;
- every version root has the correct `data-version`;
- every problem has the correct `data-problem`;
- every plain direct-response problem has a usable workspace surface;
- Version and Problem dropdowns list the exact available targets;
- selected-problem workspace functional test;
- selected-problem graph functional test;
- cross-problem isolation test;
- cross-version isolation test;
- workspace/graph independence test;
- graph control disables cleanly when the selected problem has no visual;
- MathJax inline-size normalization checked against surrounding prose;
- graph-tool entrypoint used for every supported Cartesian graph;
- graph line-weight compliance;
- answer-key alignment;
- CLICK_ME exposes only the adjustable worksheet and optional answer key;
- no source-text copying detected in the authored problems;
- screen and print modes visually checked.

Overall PASS is not allowed if the question count is wrong, a required visual is missing, a graph is inaccurate, a supported Cartesian graph bypasses the packaged graph tool, a selected-problem control changes the wrong problem, a layout control is nonfunctional, inline math is visibly oversized, the answer key disagrees, print margins are smaller than the locked value, requested two-column print collapses to one column, or print layout clips.
