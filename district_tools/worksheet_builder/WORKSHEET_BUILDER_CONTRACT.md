# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.1-pilot
REVISION: 2026-09-18.2

This tool builds original printable math practice from teacher-selected question structures. It intentionally combines two useful design traditions: clean parameterized fluency practice and conceptually varied visual/multi-representation practice. It must not reproduce copyrighted worksheet questions, wording, names, numbers, diagrams, or answer choices from reference sources.

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
- Preserve the locked `@page` margin of 0.55 in. Do not replace it with zero-margin printing or compensate with tiny page padding.
- Two student columns by default, matching the teacher preference for dense-but-readable math practice.
- A visual-heavy item may span both columns only when one-column placement would make the visual unreadable; record any span exception in QA.
- Keep directions short.
- Give each problem enough white space to work without turning the sheet into oversized cards.
- Do not use decorative shaded problem cards.
- Use MathJax for mathematical notation, but do not wrap ordinary prose numerals in MathJax when plain text is sufficient.
- Inline MathJax MUST remain at the same visual font size as surrounding prose. Do not allow the MathJax default enlargement to make values, variables, fractions, or labels visibly larger than the sentence containing them.
- Do not add per-question inline font-size overrides. The locked worksheet stylesheet owns student typography.

## 6. Adjustable workspace and graph/diagram scale - HARD

The finished `worksheet/worksheet.html` MUST include screen-only layout controls with all of the following behavior:

- Workspace scale slider + exact percent input. Range 60%-180%.
- Graph/diagram scale slider + exact percent input. Range 70%-160%.
- Reset button.
- Print button.
- The two controls are independent: changing graph size must not silently change workspace height and vice versa.
- Persist the teacher's selected values in browser `localStorage` for that worksheet when practical.
- Show a small live page/overflow warning when the browser can detect obvious overflow; never silently clip content.
- The request's `layout.workspace_scale_percent` and `layout.graph_scale_percent` are the initial values.
- On desktop screens the controls belong in a fixed/sticky LEFT rail so the teacher can see the worksheet change while moving a slider. On narrower screens they may return to a top bar.

### Required implementation rule

Do NOT implement scaling as CSS multiplication such as:

`height: calc(var(--base-workspace) * var(--workspace-scale))`

or

`width: calc(var(--base-graph-width) * var(--graph-scale))`.

Those expressions are not a reliable cross-browser mechanism for multiplying CSS dimensions by a unitless custom property and can leave a slider that moves without changing the worksheet.

Instead, the locked CSS exposes final dimension variables:

- `--workspace-height` (default `.62in`)
- `--graph-width` (default `3in`)

The worksheet JavaScript MUST calculate and write the actual dimensions whenever either slider or numeric input changes. Use these baselines unless a later contract explicitly changes them:

- `workspaceHeightIn = 0.62 * workspacePercent / 100`
- `graphWidthIn = 3.00 * graphPercent / 100`

Then set, for example:

`document.documentElement.style.setProperty('--workspace-height', workspaceHeightIn.toFixed(3) + 'in')`

`document.documentElement.style.setProperty('--graph-width', graphWidthIn.toFixed(3) + 'in')`

Apply the values on initial load, on every `input` event, after Reset, and after restoring saved values. The visible worksheet must change immediately without reloading.

Before declaring QA PASS, exercise both controls at two non-default values (for example 80% and 140%) and verify that the rendered dimensions actually change while the other dimension remains unchanged.

## 7. Graphs and quantitative visuals - HARD

Follow the packaged shared district response standard.

For every Cartesian graph type supported by the packaged graph tool, the builder MUST use the packaged authoritative entrypoint:

`response_contract/graph_tool/~graph_tool_v14.py`

with v13 and v12 staged beside it. Do not replace a supported Cartesian graph with hand-drawn SVG, improvised HTML axes, or ad hoc plotting code merely because that is quicker. A custom deterministic SVG/HTML visual is appropriate only for a representation the graph tool does not own, such as ratio tables, double number lines, simple shape arrays, scale drawings, and exact geometric polygons.

Full-size Cartesian print weights are locked to the teacher-approved 2026-09-18 standard:
- grid: 0.6 pt, `#aaaaaa`
- axes and axis arrows: 1.8 pt, `#222222`
- plotted relation: 2.0 pt
- major ticks: 1.2 pt
- relation exit arrows: 1.5 pt when used

These are the approved printed darkness from the Quick Check repair. Do not apply ad hoc CSS thickness overrides that change graph-tool output. Resize the completed graph through layout geometry only. Compact multi-panel graph-tool types may retain their built-in proportional weights.

For deterministic non-Cartesian visuals such as ratio tables, double number lines, simple shape arrays, scale drawings, and geometric polygons, clean SVG/HTML is appropriate when mathematically exact. Do not use generative imagery for quantitative diagrams.

## 8. Versions - HARD

Create the number of versions requested: 1, 2, or 4.

- Keep the same selected family distribution and difficulty profile across versions.
- Change values, names/contexts, problem order, and answer-choice order when appropriate.
- Do not change the underlying evidence architecture merely to make versions look different.
- Label versions A-D clearly.

## 9. Answer key - HARD

When requested, create `teacher/answer_key.html` and `teacher/answer_key.pdf` matching the exact student versions and order. Answers must be concise but include required reasoning for explanation items. Visual answers must be mathematically accurate.

## 10. Response package - HARD

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
  worksheet.pdf
teacher/
  answer_key.html   (when requested)
  answer_key.pdf    (when requested)
data/
  request.json
  qa.json
```

`CLICK_ME.html` is the teacher entry point and links to the worksheet HTML/PDF, answer key when requested, and QA.

`worksheet.pdf` may contain all requested versions sequentially. Start each version on a new page. Do not mix versions within a page.

## 11. QA - HARD

In addition to the shared district QA requirements, record:
- requested vs actual question count per version;
- selected family IDs and actual counts;
- difficulty distribution;
- two-column layout used and any span exceptions;
- locked 0.55 in print margin preserved;
- initial workspace and graph scale values;
- controls present, located in the left rail on desktop, and print-hidden;
- workspace control functional test with before/after computed dimension;
- graph control functional test with before/after computed dimension;
- independence test showing workspace changes do not change graph width and graph changes do not change workspace height;
- MathJax inline-size normalization checked against surrounding prose;
- graph-tool entrypoint used for every supported Cartesian graph;
- graph line-weight compliance;
- answer-key alignment;
- no source-text copying detected in the authored problems;
- all required PDFs visually checked.

Overall PASS is not allowed if the question count is wrong, a required visual is missing, a graph is inaccurate, a supported Cartesian graph bypasses the packaged graph tool, either layout control is nonfunctional, inline math is visibly oversized, the answer key disagrees, print margins are smaller than the locked value, or print layout clips.
