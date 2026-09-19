# Grading & Evidence Control Panel - Pilot

This district-wide pilot packages student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name. Grade/subject and teacher name are optional.
2. Upload student evidence (required).
3. Upload a class roster (optional, strongly recommended for combined handwritten class scans).
4. Upload a rubric/scoring guide (optional).
5. Choose whether to also return a separate grade/score: none, use the supplied rubric/scoring guide, or recommend a grade from the evidence.
6. Add teacher notes (optional).
7. Click **Build Request ZIP**.
8. Upload the ZIP to ChatGPT. The package is the complete task contract.
9. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

The control panel no longer asks the teacher to type an assignment/evidence-set name. The response build detects a concise title from the evidence in this order: visible title on submitted work; rubric/scoring-guide title; meaningful filenames; content/skill inference. **Student Evidence Review** is the last-resort fallback only.

## Evidence rating behavior

Every student report still uses the fixed evidence labels **Convincing / Limited / Incorrect / Not Observed**. The builder no longer spends screen space explaining those labels; the response package carries the definitions and can show the legend in teacher outputs where useful.

## Optional grade/score

The teacher selects one authoritative mode:

- **No separate grade / score** (default)
- **Use the supplied rubric / scoring guide**
- **Recommend a grade from the evidence**

The evidence rating remains independent from the optional grade/score.

## CLICK_ME dashboard

Top quick actions:

1. **Print All Student Reports**
2. **Print All Individual Practice**
3. **View Scanned Student Work**

Main sections:

### Individual Student Reports & Practice
Each student card includes both **Open Report** and **Individual Practice**. There is no duplicate individual-practice section later on the page.

### Class Data
Class patterns, strengths, needs, groupings, and evidence limitations.

### Common Course Practice
Three instructional products:

- **Common Worksheet / Review + Extension**
- **Stations**
- **Question / Solution Set**

A separate **Review All Questions** teacher-QA link shows every generated follow-up question in a compact no-workspace view, grouped by source. Each item can reveal its answer, a brief teacher move, and a brief student discourse move.

## Question / Solution Set

Only one class-level set is generated. It reuses the strongest approved class-level questions rather than manufacturing a separate bank.

Required views:

- one-question-at-a-time presentation mode with Back/Next;
- compact Review All view;
- printable student set;
- matching solutions;
- optional classroom-structure layouts using the same questions.

The current classroom-structure menu is intentionally small: **Standard, Find Someone Who, Quiz-Quiz-Trade, RallyCoach / PairCoach, Showdown, Fan-N-Pick**. These are layout/direction templates, not new question-generation jobs. Detailed requirements live in `COMMON_PRACTICE_GUIDE.md`, which is packaged into every request.

## Duplex-safe student printing

Combined student reports and combined individual-practice PDFs are duplex-safe: each student's segment ends on an even physical page count so the next student begins on a new sheet front. `data/qa.json` records before/after counts.

## Stations

Stations remain four review stations plus two extension stations with a separate answer key and the existing locked station style.

## Math, graphs, and visuals

MathJax, graph, diagram, and visual requirements remain hard QA requirements. Required visuals must exist and be mathematically accurate; they may not be replaced by prose placeholders.

## Privacy / data handling

The control panel reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The builder uses a small built-in ZIP writer (STORE/no compression), loads locked CSS files into each request ZIP, and includes embedded fallbacks for local/offline operation.
