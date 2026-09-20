# Grading & Evidence Control Panel - Pilot

This district-wide pilot packages student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and optional Grade / subject.
2. Make the required **Grade / score handling** choice immediately after Grade / subject.
3. Add teacher name if desired.
4. Upload student evidence (required), then an optional roster and rubric/scoring guide.
5. Add only teacher exceptions/context when needed.
6. Click **Build Request ZIP**.
7. Upload the ZIP to ChatGPT. The package is the complete task contract.
8. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

The control panel does not ask the teacher to type an assignment/evidence-set name. The response detects a concise title from the evidence in this order: visible title on submitted work; rubric/scoring-guide title; meaningful filenames; content/skill inference; **Student Evidence Review** only as the last resort.

## Required grade/score choice

Grade / score handling is intentionally required. The teacher must choose one authoritative mode before the request ZIP can be built:

- **No separate grade / score**
- **Use the supplied rubric / scoring guide**
- **Recommend a grade / score from the evidence**

The evidence rating remains independent from the optional grade/score.

## Automatic grading behavior

The following are built-in defaults rather than teacher-facing buttons:

- list Areas of Strength and Areas for Improvement;
- highlight and credit reasoning;
- treat all evidence as formative;
- allow multiple valid methods/solution paths;
- ignore grammar/spelling/writing mechanics unless specifically requested;
- de-emphasize minor arithmetic/notation slips unless specifically requested;
- credit partial understanding;
- missing is not incorrect;
- keep feedback concise;
- extend students showing Convincing evidence;
- flag unclear scans or uncertainty instead of guessing.

The optional exceptions/context area is for unusual cases only. Its quick buttons are:

- Ignore a question
- Count grammar & writing mechanics
- Count minor arithmetic / notation errors
- Require shown work / reasoning
- Feedback only / don't grade
- Treat as extension / bonus

**Ignore a question** means do not use it as evidence. **Feedback only / don't grade** means review/comment on it but do not let it affect the grade/score recommendation.

## Evidence rating behavior

Every student report uses the fixed evidence labels **Convincing / Limited / Incorrect / Not Observed**. Blank, missing, omitted, or unreadable evidence is **Not Observed**, not automatically Incorrect.

## CLICK_ME dashboard

The response dashboard organization is intentionally simple and should remain stable.

Top quick actions:

1. **Print All Student Reports**
2. **Print All Individual Practice**
3. **View Scanned Student Work**

Main sections:

### Individual Student Reports & Practice
Each student card includes **Open Report** and **Individual Practice**. There is no duplicate individual-practice section later on the page.

### Class Data
Class patterns, strengths, needs, groupings, and evidence limitations.

### Common Course Practice
Three instructional products:

- **Common Worksheet / Review + Extension**
- **Stations**
- **Question / Solution Set**

A separate **Review All Questions** teacher-QA link shows every generated follow-up question in a compact no-workspace view.

## Common Worksheet / Review + Extension

The printable student artifact is **Student Worksheet**. The HTML teaching view with answers and discourse/teacher moves is labeled **Teacher Guide**, not merely HTML. The student worksheet visibly labels **Review** and **Extension / Transfer** so the two purposes are obvious on the page.

## Question / Solution Set

Only **Set 1** is generated. The Set 1 landing page is the **Activity Options** page itself, modeled directly on `algebra/activities/u1_1_act1/u1_1_act1.html`. Do not insert a separate card-menu page before it.

The Activity Options page contains:

- **Projection / Whiteboard Options** — Whiteboard Indy, Whiteboard Partners, Rally Coach, Speed Dating Math, Showdown, Think / Trade / Agree, Round Table, Mathematical Hot Seat, and Rally Coach II. Each routine links to its directions section on the same page and uses the same Set 1 Questions & Solutions deck.
- **Printable Handouts** — Stations, **Find Someone Who**, and **Cut-Apart Question Cards**.
- **Teacher / Print Utilities** — Print Presentation, Review All Questions, and Teacher Guide.

There is **no standalone Presentation card**, no separate Classroom Structures menu page, no Set 2, no Tarsia, and no Blooket. The projection deck follows the Algebra questions/solutions pattern: a large question page followed by its large solution page, repeated through the complete Set 1. Print Presentation remains the separate top-aligned two-up student-facing print format.

**Find Someone Who is not a card layout.** It uses the uploaded gold response's **Student Set** look as its visual base: compact two-column worksheet flow, with a partner signature line and adjustable workspace added to each problem. A screen-only left control rail follows the Worksheet Builder pattern for all-workspace size, selected problem, per-problem workspace, graph/diagram size, Reset, and Print.

The separate **Cut-Apart Question Cards** deck keeps the uploaded gold-run card layout unchanged and supports Quiz-Quiz-Trade, Fan-N-Pick, and other appropriate card routines.

Every Set 1 artifact must include the complete Set 1 across enough pages/cards. No structure may silently stop at six or eight questions. Redundant Print buttons are omitted when browser print already produces the intended layout.

## Duplex-safe student printing

Combined student reports and combined individual-practice PDFs are duplex-safe: each student's segment ends on an even physical page count so the next student begins on a new sheet front. `data/qa.json` records before/after counts.

## Stations

Stations remain four review stations plus two extension stations with a separate answer key and the existing locked station style. This upgrade does not redesign them.

## Math, graphs, and visuals

MathJax, graph, diagram, and visual requirements remain hard QA requirements. Required visuals must exist and be mathematically accurate; they may not be replaced by prose placeholders. Each request ZIP packages the current **District Graph Rendering Standard** plus exactly one self-contained graph runtime resolved from `Tools/MANIFEST.json`. The current canonical runtime is `Tools/graph_tool.py`; versioned v12/v13/v14 files are no longer packaged as an active dependency chain. Supported Cartesian graphs must be created with the packaged registered graph tool, including blank student construction grids; a hand-built SVG/CSS/canvas graph that merely resembles the style is a QA failure. Graph provenance is recorded in `data/qa.json`.

## Faster QA execution

The request also packages `RESPONSE_QA_EXECUTION.md`. It preserves full review of student evidence while reducing redundant output rerendering:

- run package/link/count/provenance checks before expensive visual rendering;
- visually inspect every graph/diagram page plus representative or outlier pages for stable templates;
- after a local correction, rerender only the changed artifact and direct dependent combined PDF/index;
- do not automatically rerender every already-stable report, practice page, station page, or Set 1 view;
- record exactly what was rendered and rerendered in `data/qa.json`.

This is intended to keep a normal six-student grading run from doubling in time simply because one artifact required a local correction.

## Privacy / data handling

The control panel reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The builder uses a small built-in ZIP writer (STORE/no compression), loads locked CSS files into each request ZIP, and includes embedded fallbacks for local/offline operation.


## Gold response layout lock (2026-09-20)

The uploaded Precalculus Circuit Training response is now the visual baseline. `response_styles.css` is frozen at SHA-256 `59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df` after adding only the approved Activity Options / Questions & Solutions / Find Someone Who controls. Future response runs must not invent a new layout for stable pages. `RESPONSE_LAYOUT_LOCK.md` is packaged into every request and is a HARD contract.

Set 1 now follows the Algebra `u1_1_act1` architecture directly: `question_set/index.html` is Activity Options with one Set 1, projection structures link to one Algebra-style Questions & Solutions deck, Printable Handouts are Stations / Find Someone Who / Cut-Apart Question Cards, and Teacher/Print Utilities expose Print Presentation / Review All / Teacher Guide. There is no standalone Presentation card, no Set 2, no Tarsia, and no Blooket.

Find Someone Who uses the approved Student Set worksheet look with partner signatures and Worksheet Builder-style left controls for workspace and graph sizing. Cut-Apart Cards remain visually unchanged.
