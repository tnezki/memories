# Math Worksheet Builder Contract

STATUS: PILOT
VERSION: district-math-worksheet-builder/0.1-pilot

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

## 5. Student layout - HARD

Use `assets/worksheet_styles.css` byte-for-byte as the base stylesheet.

- US Letter portrait.
- Two student columns by default, matching the teacher preference for dense-but-readable math practice.
- A visual-heavy item may span both columns only when one-column placement would make the visual unreadable; record any span exception in QA.
- Keep directions short.
- Give each problem enough white space to work without turning the sheet into oversized cards.
- Do not use decorative shaded problem cards.
- Use MathJax for mathematical notation.

## 6. Adjustable workspace and graph/diagram scale - HARD

The finished `worksheet/worksheet.html` MUST include screen-only layout controls that operate on CSS variables and affect print:

- Workspace scale slider + exact percent input. Recommended range 60%-180%.
- Graph/diagram scale slider + exact percent input. Recommended range 70%-160%.
- Reset button.
- Print button.
- The two controls are independent: changing graph size must not silently change workspace height and vice versa.
- Persist the teacher's selected values in browser `localStorage` for that worksheet when practical.
- Show a small live page/overflow warning when the browser can detect obvious overflow; never silently clip content.
- The request's `layout.workspace_scale_percent` and `layout.graph_scale_percent` are the initial values.

## 7. Graphs and quantitative visuals - HARD

Follow the packaged shared district response standard. When Cartesian graphs are required, use the packaged authoritative graph tools when they cleanly support the representation.

Full-size Cartesian print weights are locked for this tool:
- grid: 0.6 pt, `#aaaaaa`
- axes and axis arrows: 1.8 pt, `#222222`
- plotted relation: 2.0 pt
- major ticks: 1.2 pt

Do not apply ad hoc CSS thickness overrides that change those weights. Scale the completed graph through layout geometry only.

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
- initial workspace and graph scale values;
- controls present and print-hidden;
- graph line-weight compliance;
- answer-key alignment;
- no source-text copying detected in the authored problems;
- all required PDFs visually checked.

Overall PASS is not allowed if the question count is wrong, a required visual is missing, a graph is inaccurate, the answer key disagrees, or print layout clips.
