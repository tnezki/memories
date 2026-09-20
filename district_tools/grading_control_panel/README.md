# Grading & Evidence Control Panel - Pilot

This district-wide pilot packages student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name. Grade/subject and teacher name are optional.
2. Upload student evidence (required).
3. Upload a class roster (optional, strongly recommended for combined handwritten class scans).
4. Upload a rubric/scoring guide (optional).
5. Make the required **Grade / score handling** choice: no separate grade/score, use the supplied rubric/scoring guide, or recommend a grade/score from the evidence.
6. Add only teacher exceptions/context when needed.
7. Click **Build Request ZIP**.
8. Upload the ZIP to ChatGPT. The package is the complete task contract.
9. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

The control panel does not ask the teacher to type an assignment/evidence-set name. The response detects a concise title from the evidence in this order: visible title on submitted work; rubric/scoring-guide title; meaningful filenames; content/skill inference; **Student Evidence Review** only as the last resort.

## Required grade/score choice

Step 4 is intentionally required. The teacher must choose one authoritative mode before the request ZIP can be built:

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

Only **Set 1** is generated. Set 1 is the mathematical question set and is reused across delivery formats.

Required choices:

- **Presentation** — one question at a time with compact browser use.
- **Print Presentation** — exactly two large Set 1 questions per letter page, scaled to fit, **top-aligned** in each half-page, no answers/moves.
- **Review All Questions** — compact zero-workspace QA view.
- **Student Set** — normal worksheet layout, small header, all Set 1 questions, and natural page flow rather than fixed question-page forcing that leaves large blank areas.
- **Teacher Guide** — matching answers plus concise teacher/discourse moves.
- **Classroom Structures** — existing Algebra-style participation routines using the same Set 1.

The Classroom Structures page closely follows the existing Algebra `u1_2_act1` **Activity Options** architecture, adapted to **one Set 1 only**. Projection / Whiteboard routines reuse the Set 1 Presentation. Printable Handouts list the already-generated **Stations**, **Find Someone Who**, and the added **Cut-Apart Question Cards**. Do not include Tarsia or Blooket.

**Find Someone Who is not a card layout.** It uses the established Algebra-style vertically stacked problem blocks with Partner signature, Work / reasoning, and workspace. The separate Cut-Apart Question Cards deck supports Quiz-Quiz-Trade, Fan-N-Pick, and other appropriate card routines.

Every Set 1 artifact must include the complete Set 1 across enough pages/cards. No structure may silently stop at six or eight questions.

Redundant Print buttons are omitted when browser print already produces the intended layout.

## Duplex-safe student printing

Combined student reports and combined individual-practice PDFs are duplex-safe: each student's segment ends on an even physical page count so the next student begins on a new sheet front. `data/qa.json` records before/after counts.

## Stations

Stations remain four review stations plus two extension stations with a separate answer key and the existing locked station style. This upgrade does not redesign them.

## Math, graphs, and visuals

MathJax, graph, diagram, and visual requirements remain hard QA requirements. Required visuals must exist and be mathematically accurate; they may not be replaced by prose placeholders. Each request ZIP now packages the current **District Graph Rendering Standard** plus the graph entrypoint resolved from `Tools/MANIFEST.json` and its required graph-tool dependencies. Supported Cartesian graphs must be created with that packaged registered graph tool, including blank student construction grids; a hand-built SVG/CSS/canvas graph that merely resembles the style is a QA failure. Graph provenance is recorded in `data/qa.json`.

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
