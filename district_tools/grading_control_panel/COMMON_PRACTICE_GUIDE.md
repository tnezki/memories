# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-common-practice/1.6  
DATE: 2026-09-20

This guide controls Common Course Practice and Set 1 delivery. If older request wording conflicts with this file, this file controls. `RESPONSE_LAYOUT_LOCK.md` controls visual continuity. `response_builder.py` is now the only layout author.


## 0. Deterministic rendering - HARD
The grading model does not hand-author HTML. It grades evidence, writes one canonical `response_data.json`, verifies the small shared question set once, then runs packaged `response_contract/response_builder.py`. The builder owns all stable HTML shells, page-preview controls, pagination, Activity directions, Stations markup, and shared-question reuse. Do not alter builder-generated HTML after rendering.

## 1. One approved class-level question pool - HARD
Build one coherent class-level question pool from the strongest common instructional needs plus justified extension/transfer targets. Author, solve, and validate each question exactly once. Reuse the same approved question object across every delivery format.

When a question is reused, its prompt, answer, graph/diagram asset, difficulty, teacher move, and student discourse move remain identical. Delivery templates may change presentation only. Do not re-author, re-solve, or independently re-grade the same Set 1 question for each view.

## 2. Common Worksheet / Review + Extension - GOLD
Keep the current approved two-column Common Worksheet layout.

The student worksheet visibly separates:

- **Review** - observed common needs, unfinished understanding, or prerequisites.
- **Extension / Transfer** - application/transfer for students already showing Convincing evidence or a justified class-wide extension target.

Required behavior:

- compact header with Name / Date;
- natural two-column question flow;
- no forced wasteful question-per-page breaks;
- browser-print HTML is canonical; do not generate a duplicate PDF;
- use real Letter-size screen page previews whose boundaries match browser Print;
- add the Worksheet Builder-style screen-only left control rail in this order: **All workspaces**, **Problem**, **Workspace**, **Graph / diagram** when applicable, **Reset**, **Print**;
- changing workspace or graph size repaginates immediately and visibly;
- controls disappear in print.

The same `student_worksheet.html` is also the student handout used for **Find Someone Who**. Do not create a second Find Someone Who worksheet with a different title or layout.

## 3. Teacher Guide - one teacher review authority
`print/common_review_extension/teacher_guide.html` is the single teacher-facing review for the shared Common Worksheet / Set 1 questions.

Keep the current approved two-column Teacher Guide layout:

- question number + Review or Extension / Transfer purpose;
- exact prompt;
- concise **Answer**;
- concise **Teacher move**;
- concise **Student discourse move**.

Do not generate duplicate compact Review All pages or a second Set 1 teacher guide containing the same information. Links that formerly opened those duplicates should point to this Teacher Guide.

## 4. Set 1 is the one mathematical set
Create exactly one class-level **Set 1**. Do not create Set 2.

Set 1 is the same question pool used by:

- Common Worksheet;
- Teacher Guide;
- Set 1 classroom presentation;
- Print Presentation;
- Find Someone Who, via the Common Worksheet;
- Cut-Apart Question Cards;
- classroom participation structures.

There is no fixed Set 1 size. Every Set 1 delivery uses the full approved set unless a station intentionally selects a separate station-specific subset.

## 5. `print/question_set/index.html` = Activity Options page
The Set 1 landing page itself is the Activity Options page, closely following the structure and hierarchy of:

`algebra/activities/u1_1_act1/u1_1_act1.html`

Use the locked district response colors/typography. Do not insert a six-card menu before it and do not create a second structures index/directions maze.

At the **top of the page**, before the participation structures, show:

### Teacher / Print Utilities

- **Print Presentation** -> `print_presentation.html`
- **Teacher Guide** -> `../common_review_extension/teacher_guide.html`

Also show the concise **Set 1 focus** line in this top utility area.

Do not include a Review All Questions utility; the approved Teacher Guide replaces it.

## 6. Classroom Participation Structures
Rename the old **Projection / Whiteboard Options** section to **Classroom Participation Structures** so the tool works beyond math classes.

Organize the choices into these two subgroups.

### Shared Prompt / Partner Structures
Each structure links to its directions section on the same page. Its Set 1/material link points to `presentation.html` unless noted otherwise.

- Whiteboard Indy
- Whiteboard Partners
- Rally Coach
- **Speed Dating**
- Showdown
- Think, Trade, Agree
- Round Table
- **Hot Seat**
- Rally Coach II

### Card-Based Structures
These use the single shared `structures/cut_apart_cards.html` deck. Do not create new card sets.

- **Quiz-Quiz-Trade**
- **Fan-N-Pick**
- **Mix-Pair-Share with Cards**
- **Inside-Outside Circle with Cards**

For every structure, include a corresponding directions section below using the same approved Algebra activity hierarchy:

- compact eyebrow/title/subtitle;
- **Structure**;
- **Setup**;
- concise ordered **Directions**;
- **Goal**;
- a clear Set 1 / Cards material link;
- right-side **Looks Like Success / Doesn't Look Like** boxes.

These sections are locked templates populated with the current assignment title/focus; they are not newly designed each run.

### Established directions

**Whiteboard Indy** - individual independent practice; each student has a board/marker; notes welcome; try first; write large/clearly; partners support reasoning rather than copying; revise mistakes. Goal: individual accountability + low-stakes entry.

**Whiteboard Partners** - fast partner practice; one board/marker per pair; both engaged; alternate writer; explain before erasing; resolve disagreements with evidence. Goal: engagement + quick feedback.

**Rally Coach** - partner explanation + alternating roles; one explains while one records; coach with questions not answers; switch each problem; both verify. Goal: verbal reasoning + procedural accuracy.

**Speed Dating** - independent attempt -> timed partner comparison -> rotation; share a strategy and carry one useful idea forward. Goal: repeated explanation + strategy comparison.

**Showdown** - individual think -> simultaneous reveal -> team check. Goal: individual accountability + team feedback.

**Think, Trade, Agree** - individual think -> trade explanations -> clarifying question -> justified agreement/disagreement. Goal: evidence-based comparison.

**Round Table** - team rotation of written reasoning; read prior work before adding; team checks the complete response. Goal: visible collaborative reasoning.

**Hot Seat** - describe -> reason -> reveal; use precise subject-specific language without simply giving the final response. Goal: academic language + listening.

**Rally Coach II** - solve -> coach -> restate -> switch. Goal: metacognition + partner coaching.

**Quiz-Quiz-Trade** - each student receives one card; pair; Partner A quizzes Partner B; A coaches/checks; switch roles; trade cards; find a new partner. Goal: repeated retrieval + peer explanation.

**Fan-N-Pick** - teams of four rotate roles: Fan, Pick, Answer, Coach/Check; rotate roles after each card. Goal: equal participation + structured peer feedback.

**Mix-Pair-Share with Cards** - students mix; pair on signal; use one partner's card as the prompt; each responds/explains; trade or retain cards as directed; mix again. Goal: rapid partner variety + retrieval.

**Inside-Outside Circle with Cards** - paired inner/outer circles respond to a card; partners explain/check; one circle rotates on signal; repeat with the new partner/card. Goal: repeated explanation + broad peer interaction.

## 7. Printable Handouts
List exactly:

- **Stations** - link to the existing Stations product;
- **Find Someone Who** - link directly to `../common_review_extension/student_worksheet.html`;
- **Cut-Apart Question Cards** - link to `structures/cut_apart_cards.html`.

Find Someone Who does not own a separate worksheet file. Its participation directions live on the Activity Options page; the student uses the same Common Worksheet.

## 8. Set 1 classroom presentation - gold half-page question/answer layout
`print/question_set/presentation.html` uses the current approved Print Presentation visual language, but with **one Set 1 problem per Letter page**:

- top half = the question, top-aligned;
- bottom half = **Answer**, **Teacher move**, and **Student discourse move**, top-aligned;
- use the locked rounded-panel presentation treatment and typography;
- no Back/Next shell;
- no alternating separate Question and Solution pages;
- all Set 1 problems, one physical page per problem.

Add a Worksheet Builder-style screen-only left rail:

1. **All question spacing** - applies to the current Set 1 pages without changing mathematics;
2. **Problem** selector;
3. **Question spacing / workspace** for the selected problem;
4. **Graph / diagram** size when applicable;
5. **Reset**;
6. **Print**.

Show true Letter-size page boundaries on screen. Slider changes must update the preview immediately. Graph controls resize geometry only; stroke weights remain canonical. The answer/moves region starts in the lower half and must not drift into the question half.

## 9. Print Presentation - one problem per Letter page
`print_presentation.html` uses the same locked presentation template as the classroom Set 1 view:

- exactly one Set 1 problem per Letter page;
- question and any visual in the **top half**;
- **Answer + Teacher move + Student discourse move** in the **bottom half**;
- both halves top-aligned;
- screen-only left controls: **All question spacing**, **Problem**, **Question spacing / workspace**, **Graph / diagram**, **Reset**, **Print**;
- real Letter page boundaries on screen;
- slider changes update the preview immediately;
- browser Print uses the same page fragments shown on screen.

This is a locked template populated from the already-validated Set 1 objects. Do not create a separate two-up question-only version.

## 10. Cut-Apart Question Cards - LOCKED
The current card artifact is approved and remains visually unchanged except for the actual Set 1 content/required visual.

- one task per card;
- dashed cut lines;
- complete Set 1 across enough pages/cards;
- no answer on the question side;
- shared by the four card-based structures above.

## 11. Stations - GOLD / HTML ONLY
Keep the exact approved Stations landing page, student-station pages, station cards, and answer-key markup. These are literal mad-lib templates: only titles, station labels, prompts, answers, visuals, and counts may be injected. Do not regenerate station HTML structure or CSS.

- exactly four review stations plus two extension stations;
- 4-6 questions each;
- separate answer key;
- `Open Student Stations` and `Open Answer Key` HTML links only;
- do not generate Student PDF or Answer Key PDF duplicates.

## 12. Combined student printing - HTML first
Top dashboard quick actions use printable HTML:

- **Print All Student Reports** -> combined printable HTML;
- **Print All Individual Practice** -> combined printable HTML;
- **View Scanned Student Work** -> preserved submitted scan/PDF.

Do not generate duplicate combined report/practice PDFs.

Combined printable HTML remains duplex-safe: each student's segment occupies an even number of physical browser-print pages. Insert one truly blank page only when a student's rendered segment is odd so the next student begins on a sheet front.

### Combined Individual Practice controls
Use true Letter-size page previews plus the left rail: **All workspaces**, **Problem**, **Workspace**, **Graph / diagram** when applicable, **Reset**, **Print**. Changing controls repaginates immediately.

### Combined Student Reports
Show true Letter-size page previews and a screen-only Print control. Question-workspace sliders are not required when the report itself contains no adjustable question workspace.

## 13. Adjustable HTML page geometry - HARD
For adjustable student/practice/set HTML:

- screen preview shows real 8.5 x 11 in page fragments on the gray background;
- browser Print uses the same page fragments and boundaries;
- use explicit page containers and deterministic repagination after MathJax, workspace changes, graph/diagram changes, or content changes;
- avoid stale page assignments and avoidable large blank regions;
- never clip content merely to preserve an old page count;
- screen page count and browser Print page count must agree.

## 14. Math, graphs, and visuals
All products inherit the packaged Math / Graph / Visual QA contract and District Graph Rendering Standard.

- supported Cartesian graphs, including blank grids, use the packaged canonical graph tool;
- reuse the exact same graph asset anywhere a question is reused;
- prefer SVG assets for adjustable HTML;
- graph size controls scale geometry, not stroke weights;
- record graph tool entrypoint + asset path in `data/qa.json`;
- student construction visuals remain answer-neutral.

## 15. Gold layout lock
Follow `response_contract/RESPONSE_LAYOUT_LOCK.md` as a HARD contract. Copy `styles.css` byte-for-byte. The current tested response remains the visual baseline everywhere except for the explicitly approved changes in that lock.

## 16. QA requirements
Before delivery verify:

- one Set 1 only / no Set 2;
- shared question objects are solved/validated once and reused, not regenerated per view;
- Common Worksheet visibly labels Review and Extension / Transfer;
- Common Worksheet has left controls and real Letter page previews;
- Find Someone Who links to that exact Common Worksheet file;
- Teacher Guide is the one teacher review authority; no duplicate Review All pages;
- Activity Options begins with Teacher / Print Utilities and Set 1 focus;
- Classroom Participation Structures contains both Shared Prompt / Partner and Card-Based subgroups;
- Speed Dating and Hot Seat use those exact names;
- all four card structures have full directions sections and use the one Cut-Apart deck;
- Set 1 presentation has question top half + answer/moves bottom half, with left controls and true page preview;
- Print Presentation uses one Letter page per problem with question top half and answer/moves bottom half, with live controls and page preview;
- Cut-Apart Cards match the current gold layout;
- Stations expose HTML only, no generated station PDFs;
- combined reports/practice quick actions open HTML, not generated PDFs;
- no Tarsia or Blooket;
- graph style/provenance pass the canonical standard;
- locked CSS hash matches;
- links resolve and `data/qa.json` has no unresolved failure.
