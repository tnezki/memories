# Grading & Evidence Control Panel - Pilot

This district-wide pilot packages student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and optional Grade / subject.
2. Make the required **Grade / score handling** choice immediately after Grade / subject.
3. Add teacher name if desired.
4. Upload student evidence (required), then optional roster/rubric files.
5. Add only teacher exceptions/context when needed.
6. Click **Build Request ZIP**.
7. Upload that ZIP to ChatGPT. The ZIP is the complete build contract.
8. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

The assignment title is detected from the evidence rather than typed by the teacher.

## Grade / score handling

The teacher must choose one authoritative mode:

- No separate grade / score
- Use the supplied rubric / scoring guide
- Recommend a grade / score from the evidence

Every student report still uses **Convincing / Limited / Incorrect / Not Observed**.

## Deterministic response build

The grading model now does only the variable work: read/grade evidence, create the small canonical follow-up set, and write `response_data.json`. Packaged `response_builder.py` renders all approved pages. This prevents Class Data, Stations, Activities, worksheets, and print behavior from drifting between runs and keeps fast-model runs useful.

The Common Worksheet and Individual Practice previews use one shared deterministic runtime: real Letter sheets, natural question flow, live workspace repagination, actual problem selection, and print output matching the preview.

The request also packages `evidence_review.py` and `response_qa.py`. The first owns repeatable PDF/image rendering and contact-sheet preparation; the second owns repeatable file/link/hash/policy QA. Grading runs should not write new mechanical scripts or fetch these utilities from GitHub/web.

## Gold response layout

The tested 2026-09-20 Precalculus Circuit Training response is the visual baseline. Stable dashboard/report/class/worksheet/teacher-guide/station/card surfaces are locked. The current locked response CSS SHA-256 is:

`2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad`

Future runs change content, not the approved visual system, unless the contract explicitly names an approved change.

### Locked dashboard surfaces

- top dashboard hierarchy and buttons;
- **Individual Student Reports & Practice** card grid;
- **Class Data** page;
- Common Course Practice cards;
- individual report/practice styles.

## HTML-first printing

Generated classroom/teacher print products use HTML + browser Print as the canonical workflow. Do not create duplicate PDFs for products that already print correctly from HTML.

Top quick actions:

1. **Print All Student Reports** -> combined printable HTML
2. **Print All Individual Practice** -> combined printable HTML
3. **View Scanned Student Work** -> preserved source scan/PDF

Combined report/practice HTML remains duplex-safe by inserting a truly blank physical page only when a student's rendered segment has an odd page count.

Stations expose HTML Student Stations + HTML Answer Key only. Common Worksheet, Print Presentation, Teacher Guide, and Cut-Apart Cards are also HTML-first.

## Adjustable page previews

The Common Worksheet, combined Individual Practice, and Set 1 classroom presentation use Worksheet Builder-style screen controls and true Letter-size page previews. Screen page boundaries are the same boundaries used by browser Print.

Common Worksheet / practice controls include:

- All workspaces
- Problem
- Workspace
- Graph / diagram when applicable
- Reset
- Print

Set 1 classroom presentation uses the same control language with question spacing/workspace rather than a student worksheet workspace.

## Common Worksheet / Review + Extension

The current two-column worksheet is gold. It visibly labels **Review** and **Extension / Transfer** and now gains adjustable spacing controls plus real Letter-size preview pages.

**Find Someone Who uses this exact same student worksheet file.** It does not generate a separately titled/restyled handout.

## Teacher Guide

`print/common_review_extension/teacher_guide.html` is the single teacher review authority for the shared Common Worksheet / Set 1 questions. It keeps the approved two-column layout with:

- question;
- answer;
- teacher move;
- student discourse move.

Duplicate global/Set 1 Review All pages are removed rather than regenerating the same information in weaker layouts.

## Question / Solution Set

Only **Set 1** is generated.

`print/question_set/index.html` is the Activity Options page itself. At the top it shows **Teacher / Print Utilities** and the Set 1 focus, then **Classroom Participation Structures**.

### Shared Prompt / Partner Structures

- Whiteboard Indy
- Whiteboard Partners
- Rally Coach
- Speed Dating
- Showdown
- Think, Trade, Agree
- Round Table
- Hot Seat
- Rally Coach II

### Card-Based Structures

All use the same Cut-Apart Question Cards deck:

- Quiz-Quiz-Trade
- Fan-N-Pick
- Mix-Pair-Share with Cards
- Inside-Outside Circle with Cards

Every structure gets its own Algebra-style directions section on the Activity Options page. No Set 2, Tarsia, or Blooket.

### Printable Handouts

- Stations
- Find Someone Who -> same Common Worksheet HTML
- Cut-Apart Question Cards

### Teacher / Print Utilities

- Print Presentation
- Teacher Guide

## Set 1 classroom presentation

`presentation.html` uses one Letter page per problem:

- top half: question, top-aligned;
- bottom half: Answer + Teacher move + Student discourse move, top-aligned.

It uses the same rounded-panel visual language as the approved Print Presentation and adds screen-only spacing/graph controls with true page previews.

`print_presentation.html` now uses the same locked one-problem Letter template as the classroom Set 1 view: question in the top half; Answer + Teacher move + Student discourse move in the bottom half; live spacing/graph controls; preview equals Print.

## Stations

Stations remain four review stations plus two extension stations with a separate answer key. Their approved HTML structure and station CSS are literal mad-lib templates: the renderer only drops in station titles, questions, answers, visuals, and counts. The redundant station PDFs stay removed.

## Graphs

Every request ZIP packages the current District Graph Rendering Standard and exactly one self-contained graph runtime resolved from `Tools/MANIFEST.json`. Supported Cartesian graphs, including blank construction grids, must use that runtime. Reused Set 1 questions reuse the exact same graph asset across views.

## Faster QA execution

The response build now follows a locked-template fast path:

- packaged `evidence_review.py` handles page rendering/contact sheets once;
- packaged `response_qa.py` handles repeatable mechanical QA once;

- full student-evidence review remains required;
- canonical questions/answers/moves/visuals are generated and validated once;
- locked templates are populated like mad-lib shells rather than redesigned or revalidated from scratch;
- programmatic checks run before visual rendering;
- visual QA is bounded to graphs/diagrams and actual overflow/content outliers;
- slider QA uses one default, one mid, and one max smoke test instead of an exhaustive matrix;
- local corrections rerender only the changed artifact and direct dependents;
- generated duplicate PDFs are not created;
- `data/qa.json` records build-phase timings so slow runs can be diagnosed.

## Privacy / data handling

The control panel reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.
