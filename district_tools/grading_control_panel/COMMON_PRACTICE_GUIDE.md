# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-common-practice/1.1  
DATE: 2026-09-20

This guide is the controlling contract for Common Course Practice and Question / Solution Set layout. If older request wording conflicts with this file, this file controls.

## 1. One approved class-level question pool
Build one coherent class-level pool from the strongest common instructional needs plus justified extension targets. Reuse approved questions across Common Worksheet / Review + Extension, Stations when appropriate, Set 1, presentation, review pages, and participation structures.

Do not manufacture unrelated extra questions just because multiple delivery formats exist. When a question is reused, the mathematics, answer, graph/diagram, and difficulty remain identical.

## 2. Common Worksheet / Review + Extension
This product has two teacher-facing links:

- **Student Worksheet** — the printable student version.
- **Teacher Guide** — the HTML teaching view with answers/solutions, concise teacher moves, and concise student discourse moves.

Do not label the Teacher Guide merely “HTML.” If browser print already gives the intended worksheet print layout, do not add a second redundant Print button.

Keep the student worksheet header small and worksheet-like. Do not use a large hero/title block that consumes question space.

## 3. Set 1 is the mathematical set
Create exactly one class-level **Set 1**. Do not create Set 2 in this workflow.

Set 1 is not a delivery format. It is the approved mathematical question set. The same complete Set 1 is reused by:

- Presentation
- Print Presentation
- Review All Questions
- Student Set
- Teacher Guide
- Find Someone Who
- Cut-Apart Question Cards
- projection participation structures

There is no fixed Set 1 size such as 8 or 14. The number is determined by the evidence and instructional purpose.

**Completeness rule:** every Set 1 artifact must use the entire Set 1 unless the structure intentionally paginates/cards the complete set across multiple pages. Never silently show only the first 6 or 8 questions.

## 4. Set 1 menu
`print/question_set/index.html` should expose only the useful choices:

1. **Presentation**
2. **Print Presentation**
3. **Review All Questions**
4. **Student Set**
5. **Teacher Guide**
6. **Classroom Structures**

Do not expose separate “Print Student Set” or “Print Teacher Guide/Solutions” buttons when browser print is the same layout. Keep a dedicated print artifact only when the print format is genuinely different, as with Print Presentation.

## 5. Presentation — compact screen behavior
`presentation.html` is one question at a time.

Requirements:

- compact top bar;
- visible **Back / Next** controls;
- visible question counter;
- question and required visual fill the useful browser area;
- answer, Teacher Move, and Student Discourse Move may be teacher-only toggles;
- no print-page-sized empty vertical space;
- no long scrolling between questions;
- required graphs/figures remain large enough to read.

This follows the established Algebra activity principle: project the question efficiently and change the participation structure without creating a new question bank.

## 6. Print Presentation — required 2-up format
Create `print_presentation.html` and `print_presentation.pdf` from the exact Set 1 questions.

Print rules:

- letter-size portrait pages;
- **exactly two large question panels per physical page**, stacked vertically;
- scale each question and required graph/figure to fit its half-page cleanly;
- no answers;
- no teacher moves;
- no student discourse moves;
- no unnecessary student workspace;
- no giant header;
- all Set 1 questions included;
- when Set 1 has an odd number of questions, the unused final half-page may remain blank.

The browser view should visibly show the real printed page boundaries so the teacher can inspect pagination before printing.

## 7. Review All Questions — Set 1 QA
`print/question_set/review_all.html` is a compact zero-workspace teacher QA view of every Set 1 question.

Use a dense responsive grid/list. Each item includes:

- question number;
- compact prompt;
- required graph/figure/model;
- collapsible **Show Answer**;
- collapsible **Teacher Move**;
- collapsible **Student Discourse Move**.

The purpose is to judge question quality quickly, not to simulate a worksheet.

## 8. Student Set
`student_set.html` is the student worksheet version of Set 1.

Rules:

- small worksheet-style header;
- student name/date line when useful;
- all Set 1 questions;
- no projected participation directions;
- sensible question spacing/workspace;
- required figures/graphs remain readable;
- true page breaks that match print intent;
- avoid a giant title block.

If the browser-print version already produces the intended student handout, do not add a redundant print-only button. A generated PDF may still exist as a file for reliability without becoming a duplicate dashboard button.

## 9. Teacher Guide
`teacher_guide.html` follows the Student Set question order exactly and adds:

- concise answer/solution;
- brief Teacher Move when useful;
- brief Student Discourse Move when useful.

Keep it compact enough for practical teacher use. Do not turn every question into a page-long lesson plan.

## 10. Classroom Structures — reuse Set 1
The classroom structure system follows the existing Algebra activity architecture. The mathematics stays the same; only the participation routine changes.

### A. Projection structures
Projection structures do **not** get duplicate question artifacts. They provide concise projectable directions and use the same Set 1 Presentation.

Use these established routines and direction patterns:

#### Whiteboard Indy
- **Structure:** Individual independent practice
- **Setup:** Each student has a whiteboard and marker.
- **Directions:** Notes are welcome. Try something before asking for an answer. Write large and clearly. Use a partner for reasoning, not copying. Fix mistakes and discuss what changed.
- **Goal:** Individual accountability + low-stakes problem entry

#### Whiteboard Partners
- **Structure:** Fast partner practice
- **Setup:** One whiteboard and marker per pair.
- **Directions:** Both students stay engaged. Alternate who writes. Explain before erasing. Resolve disagreements with evidence.
- **Goal:** Engagement + quick feedback

#### RallyCoach
- **Structure:** Partner explanation + alternating roles
- **Setup:** Partners share a workspace; one explains while one records.
- **Directions:** Partner A explains and Partner B records. Coach with questions, not answers. Switch roles after each problem. Both partners verify the final response.
- **Goal:** Verbal reasoning + procedural accuracy

#### Speed Dating Math
- **Structure:** Paired practice -> timed rotation -> strategy sharing
- **Setup:** Each student keeps their own work while partners rotate.
- **Directions:** Solve independently first. Compare methods with the current partner. Rotate when directed. Carry one useful strategy to the next partner.
- **Goal:** Repeated explanation + strategy comparison

#### Showdown
- **Structure:** Individual think -> simultaneous reveal -> team check
- **Setup:** Teams need individual boards or papers.
- **Directions:** Everyone solves before anyone reveals. Reveal together on the signal. Compare differences in reasoning. Revise only after discussion.
- **Goal:** Individual accountability + team feedback

#### Think, Trade, Agree
- **Structure:** Individual think -> partner trade -> agreement
- **Setup:** Students need individual workspace.
- **Directions:** Think and solve first. Trade explanations with a partner. Ask one clarifying question. Agree on a justified response or record the disagreement.
- **Goal:** Evidence-based comparison

#### Round Table
- **Structure:** Team rotation of written reasoning
- **Setup:** One shared sheet or board per team.
- **Directions:** One student adds a step or representation. Pass the work. Read what is already there before adding. Team-check the complete solution.
- **Goal:** Visible collaborative reasoning

#### Mathematical Hot Seat
- **Structure:** Describe -> reason -> reveal
- **Setup:** One student faces away from the projected question while teammates describe permitted information.
- **Directions:** Use precise mathematical language. Do not simply say the final answer. Hot-seat student records the reasoning. Reveal and compare afterward.
- **Goal:** Mathematical language + listening

#### Rally Coach II
- **Structure:** Solve -> coach -> restate -> switch
- **Setup:** Partners each need a workspace.
- **Directions:** Solver works aloud. Coach asks questions only. Solver restates the completed reasoning. Switch roles for the next problem.
- **Goal:** Metacognition + partner coaching

### B. Printable structures
Only structures that genuinely need a transformed physical artifact receive one.

#### Find Someone Who
Use the complete Set 1 across as many pages as needed.

- grid of question boxes;
- each box has one Set 1 task and a partner/signature line;
- small activity-style header;
- directions: attempt a problem first, find a partner, compare reasoning, sign only when both can explain, use different partners across the page;
- do not truncate Set 1 to fit one page.

#### Cut-Apart Question Cards
Create one reusable complete Set 1 card deck.

- one Set 1 task per card;
- compact cut lines;
- readable mathematical figures;
- question side contains no answer;
- matching answer/coaching information lives in the Teacher Guide.

This one card artifact supports **Quiz-Quiz-Trade**, **Fan-N-Pick**, and other card-based routines. Do not create separate duplicate card decks for each routine.

## 11. Structure page design
Use a compact activity-style header, not a giant title block. A structure direction page should emphasize:

- structure;
- setup;
- concise directions;
- goal;
- direct link to Set 1 Presentation or the printable artifact.

Do not create a maze of nearly identical files.

## 12. Global Review All Questions — teacher QA
Create `class/review_all_questions.html` and link it from CLICK_ME under Common Course Practice.

This page shows **all generated follow-up questions**, grouped by source:

- Common Worksheet / Review + Extension;
- Stations;
- Set 1;
- Individual Practice by student.

Rules:

- zero student workspace;
- compact cards/rows;
- required graphs/figures remain readable but compact;
- tiny teacher-only source/purpose label;
- collapsible Answer, Teacher Move, Student Discourse Move;
- reused common questions may be marked as reused rather than visually duplicated.

## 13. Stations remain unchanged in this pass
Stations continue as four review stations plus two extension stations with 4-6 questions each, separate answer key, and the locked station CSS. Do not redesign the established station product during this upgrade.

## 14. Math, graphs, and visuals
All Common Course Practice products inherit the packaged Math / Graph / Visual QA contract.

Required visuals must exist and be mathematically accurate. Supported Cartesian graphs, including blank student construction grids, use the registered canonical graph tool. Student construction visuals must not reveal the completed answer.

## 15. QA requirements
Before delivery, verify:

- one Set 1 only;
- no Set 2;
- every Set 1 view uses the full Set 1;
- Print Presentation has exactly two questions per physical page;
- Student Set and structure headers are compact;
- Review All pages use zero workspace and show every expected question;
- Find Someone Who and Cut-Apart Cards include the complete Set 1 across enough pages/cards;
- redundant print buttons are absent when browser print is equivalent;
- all links resolve after unzip;
- MathJax and required graphs/figures render correctly;
- `data/qa.json` records these checks and may not report PASS with an unresolved failure.
