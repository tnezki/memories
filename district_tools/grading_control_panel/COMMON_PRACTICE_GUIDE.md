# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-common-practice/1.3  
DATE: 2026-09-20

This guide controls Common Course Practice and Set 1 delivery. If older request wording conflicts with this file, this file controls. `RESPONSE_LAYOUT_LOCK.md` controls visual continuity.

## 1. One approved class-level question pool
Build one coherent class-level pool from the strongest common instructional needs plus justified extension targets. Reuse approved questions across Common Worksheet / Review + Extension, Stations when appropriate, Set 1, projection pages, review pages, and participation structures.

Do not manufacture unrelated extra questions just because multiple delivery formats exist. When a question is reused, the mathematics, answer, graph/diagram, and difficulty remain identical.

## 2. Common Worksheet / Review + Extension
Keep the current gold worksheet/teacher-guide layout. The student worksheet visibly separates:

- **Review** — observed common needs, unfinished understanding, or prerequisites.
- **Extension / Transfer** — application/transfer for students already showing Convincing evidence or a justified class-wide extension target.

Use clear labels on the worksheet. Keep the header compact. Teacher-facing HTML is named **Teacher Guide**, not merely HTML. Do not add redundant print buttons when browser print already gives the intended product.

## 3. Set 1 is the one mathematical set
Create exactly one class-level **Set 1**. Do not create Set 2.

Set 1 is reused by:

- Set 1 Questions & Solutions projection deck;
- Print Presentation;
- Review All Questions;
- Teacher Guide;
- Find Someone Who;
- Cut-Apart Question Cards;
- projection/whiteboard participation structures.

There is no fixed Set 1 size. Every Set 1 artifact uses the entire set unless it is intentionally paginating/cards the same complete set.

## 4. `print/question_set/index.html` = Activity Options page
The old six-card Set 1 menu is retired. `index.html` itself must closely mirror the structure and hierarchy of:

`algebra/activities/u1_1_act1/u1_1_act1.html`

Adaptations for this grading tool:

- one Set 1 only;
- no Set 2;
- no Tarsia;
- no Blooket;
- do not invent unrelated activity types;
- add **Cut-Apart Question Cards** under Printable Handouts;
- use the current gold response colors/typography from locked `styles.css` rather than introducing a new theme.

The Activity Options page contains the projectable direction sections in the same HTML page using internal anchors, just like the Algebra activity page. Do not create a second `structures/index.html` card menu or a separate `directions.html` maze.

### Projection / Whiteboard Options
List these routines as simple linked rows/list items. Each routine name links to its directions anchor and its **Set 1** link points to the same `presentation.html` Questions & Solutions deck:

- Whiteboard Indy
- Whiteboard Partners
- Rally Coach
- Speed Dating Math
- Showdown
- Think, Trade, Agree
- Round Table
- Mathematical Hot Seat
- Rally Coach II

No standalone **Presentation / Open Presentation** card belongs on the Activity Options page.

### Printable Handouts
List:

- **Stations** — link to the already-generated Stations product;
- **Find Someone Who** — link to `structures/find_someone_who.html`;
- **Cut-Apart Question Cards** — link to `structures/cut_apart_cards.html`.

The card deck remains visually unchanged from the current gold run.

### Teacher / Print Utilities
Keep direct utility links available without turning them into the old card menu:

- **Print Presentation** — two-up student-question printout;
- **Review All Questions** — compact teacher QA;
- **Teacher Guide** — answers/moves.

## 5. Set 1 Questions & Solutions projection deck
`presentation.html` is no longer the compact Back/Next shell from the previous run.

Build it like the Algebra `u1_1_set1_questions_solutions.html` pattern:

- one large **Question** page for Set 1 Problem 1;
- immediately followed by one large **Solution** page for Problem 1;
- repeat Question then Solution for every Set 1 problem;
- large projectable math/figures;
- question page has useful white space for board discussion;
- solution page repeats the prompt and gives the concise solution plus teacher/discourse move only when useful;
- use the locked `.activity-page`, `.prob-head`, `.prob-q`, `.projection-work`, and `.solution` classes;
- no Back/Next shell, no question counter bar, no giant empty browser page created only to imitate printing.

Every projection/whiteboard structure reuses this same deck.

## 6. Print Presentation - keep the current gold two-up format
Create `print_presentation.html` + PDF from the exact Set 1 questions.

- Letter portrait;
- exactly two large question panels per physical page;
- top-align each question within its half-page panel;
- no answers/moves/workspace;
- all Set 1 questions;
- final lower half may be blank when the set count is odd.

Do not redesign the current approved two-up panel styling.

## 7. Review All Questions - keep current gold layout
`review_all.html` remains the compact zero-workspace teacher QA view of all Set 1 questions with required visuals and collapsible Answer / Teacher Move / Student Discourse Move.

## 8. Find Someone Who = Student Set worksheet look + signatures
The separate generic Student Set is no longer a teacher-facing Activity Options choice. Use the **current gold Student Set visual layout** as the base for Find Someone Who.

`structures/find_someone_who.html` requirements:

- compact Set 1 worksheet header;
- current two-column `.student-set-grid` / `.student-question` look;
- all Set 1 questions in natural flow;
- each problem adds a compact **Partner signature** line;
- each problem keeps useful workspace;
- required graph/diagram remains readable;
- no cut-card boxes;
- no giant activity title block;
- browser print is the canonical handout.

### Screen-only left controls - match Worksheet Builder
Add the Worksheet Builder-style left rail on wide screens. Use this order:

1. **All workspaces in this sheet** — 0-300%, default 100%;
2. **Problem** selector;
3. **Workspace** — 0-1200% for the selected problem;
4. **Graph / diagram** — 70-160% for the selected problem when a visual exists;
5. **Reset**;
6. **Print**.

There is no Version control and no New Question button because this is one fixed Set 1.

Controls are screen-only and disappear in print. Workspace and graph size are independent. Resizing changes geometry only; graph stroke weights never change. Preserve current problem order and mathematics.

If a generic `student_set.html` is retained internally for compatibility, do not expose it as a primary Activity Options link and do not give it a second competing visual design.

## 9. Teacher Guide - keep current gold layout
Keep the current compact Teacher Guide styling/order. It follows Set 1 and provides concise answer/solution plus brief teacher/discourse moves where useful.

## 10. Activity direction sections - mirror Algebra u1_1
The Activity Options HTML includes one direction section per routine using the Algebra hierarchy:

- compact eyebrow/title/subtitle;
- **Structure**;
- **Setup**;
- concise ordered **Directions**;
- **Goal**;
- one **Set 1** link;
- right-side **Looks Like Success / Doesn't Look Like** boxes.

Use these established routine meanings:

### Whiteboard Indy
Structure: Individual independent practice. Setup: each student has a whiteboard/marker. Directions: notes welcome; try something first; write large/clearly; use partners for reasoning not copying; revise mistakes. Goal: individual accountability + low-stakes entry.

### Whiteboard Partners
Structure: fast partner practice. Setup: one board/marker per pair. Directions: both engaged; alternate writer; explain before erasing; resolve disagreements with evidence. Goal: engagement + quick feedback.

### Rally Coach
Structure: partner explanation + alternating roles. Setup: shared workspace. Directions: A explains/B records; coach with questions not answers; switch each problem; both verify. Goal: verbal reasoning + procedural accuracy.

### Speed Dating Math
Structure: independent attempt -> timed partner comparison -> rotation. Goal: repeated explanation + strategy comparison.

### Showdown
Structure: individual think -> simultaneous reveal -> team check. Goal: individual accountability + team feedback.

### Think, Trade, Agree
Structure: individual think -> trade explanations -> clarifying question -> justified agreement/disagreement. Goal: evidence-based comparison.

### Round Table
Structure: team rotation of written reasoning. Goal: visible collaborative reasoning.

### Mathematical Hot Seat
Structure: describe -> reason -> reveal. Goal: mathematical language + listening.

### Rally Coach II
Structure: solve -> coach -> restate -> switch. Goal: metacognition + partner coaching.

Use the same concise success/non-example language pattern as the Algebra activity page. Do not invent new rule systems.

## 11. Cut-Apart Question Cards - LOCKED
The current card artifact is approved. Keep it visually and structurally unchanged except for the actual Set 1 content/required visual.

- one task per card;
- dashed cut lines;
- complete Set 1 across enough cards/pages;
- no answer on question side;
- supports Quiz-Quiz-Trade and Fan-N-Pick.

Do not use the cards for Find Someone Who.

## 12. Global Review All Questions - teacher QA
Keep the current gold `class/review_all_questions.html` layout. Show all generated follow-up questions from Common Worksheet, Stations, Set 1, and Individual Practice with zero workspace and collapsible teacher information.

## 13. Stations remain unchanged
Exactly four review stations plus two extension stations, 4-6 questions each, separate answer key, locked station CSS. Do not redesign.

## 14. Math, graphs, and visuals
All products inherit the packaged Math / Graph / Visual QA contract and District Graph Rendering Standard.

- supported Cartesian graphs, including blank grids, use the packaged canonical graph tool;
- use the same graph asset wherever a question is reused;
- prefer SVG for adjustable student handouts;
- graph size controls scale the asset geometry, not its stroke weights;
- record graph tool entrypoint + asset in `data/qa.json`;
- student construction visuals remain answer-neutral.

## 15. Gold layout lock
Follow `response_contract/RESPONSE_LAYOUT_LOCK.md` as a HARD contract. Copy `styles.css` byte-for-byte. Apart from the explicitly approved Set 1 changes in that lock, do not restyle the response package.

## 16. QA requirements
Before delivery verify:

- one Set 1 only / no Set 2;
- every Set 1 delivery uses the full set;
- Common Worksheet visibly labels Review and Extension / Transfer;
- `question_set/index.html` is the Algebra-style Activity Options page, not the old six-card menu;
- no standalone Presentation card;
- every projection routine's Set 1 link points to the same Questions & Solutions deck;
- projection deck alternates Question then Solution for every problem;
- Print Presentation remains exactly two top-aligned questions per physical page;
- Find Someone Who uses the current Student Set look, partner signatures, useful workspace, and the left control rail;
- controls work at all-workspace 0/100/300%, per-problem workspace 0/100/500/1200%, graph 70/100/160%;
- Cut-Apart Cards match the gold layout;
- no Tarsia or Blooket;
- no separate structures card menu/directions maze;
- graph style/provenance pass the canonical standard;
- locked CSS hash matches;
- links resolve and `data/qa.json` has no unresolved failure.
