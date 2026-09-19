# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS
VERSION: district-grading-common-practice/1.0
DATE: 2026-09-19

## 1. Reuse one approved class-level question pool
Build one coherent class-level question pool from the strongest common instructional needs and appropriate extension targets found in the evidence. Reuse that pool across Common Worksheet / Review + Extension, Stations when appropriate, Question / Solution Set, presentation mode, Review All Questions, and cooperative-structure layouts. Do not manufacture unrelated extra questions merely because multiple layouts exist.

The same question may appear in more than one teacher-selected delivery format. The mathematics, answer, graph/diagram, and difficulty must remain identical when reused.

## 2. Question / Solution Set
Create one set only. The set is a teacher-facing delivery option, not another assessment bank.

Required views:
- `index.html`: simple teacher menu.
- `presentation.html`: screen-filling one-question-at-a-time view with Back, Next, question counter, Show Answer, Teacher Move, and Student Discourse Move. Do not use print-page-sized blank vertical space on screen.
- `review_all.html`: compact no-workspace view of all questions. Use a dense responsive grid/list so the teacher can scan quality quickly. Each question has collapsible Show Answer, Teacher Move, and Student Discourse Move.
- `student_set.html` + PDF: compact printable student question set.
- `solutions.html` + PDF: matching solutions.

Teacher Move and Student Discourse Move must be short and useful. Prefer prompts such as “What evidence supports that?”, “Where could an error enter?”, “Compare two methods,” or “What changes and what stays the same?” Tailor them to the question when possible; do not add paragraphs of pedagogy.

## 3. Review All Questions — teacher QA
Create `class/review_all_questions.html` and link it from CLICK_ME under Common Course Practice.

This page shows ALL generated follow-up questions, grouped by source:
- Common Worksheet / Review + Extension;
- Stations;
- Question / Solution Set;
- Individual Practice, grouped by student.

Rules:
- zero student workspace;
- compact cards/rows with minimal vertical waste;
- keep required graphs/figures readable but compact;
- include tiny teacher-only purpose/source text (for example “Common need: factoring quadratics” or “Extension: transfer”);
- each item has collapsible Answer, Teacher Move, and Student Discourse Move;
- repeated/reused questions may be marked “reused from …” rather than duplicated unnecessarily in the common sections;
- this is a review screen, not a student handout and not a PDF requirement unless specifically requested.

## 4. Cooperative classroom structures
Use the SAME approved class-level question pool. These are layout/direction templates, not new question-generation jobs. Write original concise directions; do not copy proprietary published wording.

### Standard
Ordinary individual/pair practice layout.

### Find Someone Who
Use a grid of question boxes. Each box contains one problem/task and a small line for the partner/student name. Directions should have students find classmates, discuss/solve one item together, record the partner, then move to another person. Do not require every teacher to use every box.

### Quiz-Quiz-Trade
Create cut-apart question cards from the approved pool. Keep each card concise and visually readable. Provide the matching answer/coaching information in the teacher solution view rather than exposing it on the student-facing question side.

### RallyCoach / PairCoach
Arrange questions in alternating Partner A / Partner B turns. One student solves/explains while the partner checks, prompts, and coaches; then roles switch. Keep the directions to a few lines.

### Showdown
Use one question at a time for teams. Students solve independently, reveal/compare at the teacher/team cue, discuss differences, and agree on a corrected solution. The presentation view may be used directly; no unique question generation is needed.

### Fan-N-Pick
Create cut-apart cards from the approved pool and provide a short role rotation cue (select/read, answer, check/coach, rotate). Keep teacher solutions separate.

## 5. Do not overbuild
A response may expose the six choices above from a small “Classroom structure” menu, but it should not create a maze of redundant dashboard cards. Keep the main CLICK_ME hierarchy simple:
1. Individual Student Reports & Practice
2. Class Data
3. Common Course Practice

The cooperative choices belong inside the Question / Solution Set or Common Worksheet workflow.
