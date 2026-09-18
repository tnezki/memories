# Tiered Task Generation Contract

STATUS: REQUIRED
VERSION: district-tiered-task-generation/0.1-pilot

This contract is executable. It defines how one teacher request becomes one integrated student Tiered Task Card plus one Teacher Guide / Evidence Guide.

## Purpose

Create a ready-to-use extension/enrichment task that increases **cognitive complexity** from DOK 1 through DOK 4 while staying anchored to the teacher's 1-4 I Can statements. This is not an "easy / medium / hard / hardest" worksheet and it is not four separate task cards.

## One-card rule - HARD

- Create exactly ONE integrated student task card.
- The card contains exactly four labeled task areas: DOK 1, DOK 2, DOK 3, DOK 4.
- All four tasks belong to the same task card and draw from the submitted I Can statements as a coherent target set.
- Do not generate one card per I Can statement.

## DOK meaning - HARD

Depth of Knowledge is the cognitive processing required, not how difficult, lengthy, or obscure a task feels. Do not assign DOK from verbs alone.

### DOK 1 - Recall and Reproduction
Use direct retrieval, identification, description, representation, routine calculation, or reproduction of foundational knowledge needed for the target.

### DOK 2 - Skills and Concepts
Require application of concepts or procedures with some decision making: compare/classify, interpret information, organize or represent relationships, choose a method, explain how/why, or apply learning in a familiar but not purely routine context.

### DOK 3 - Strategic Thinking
Require non-routine reasoning, justification, critique, defense, revision, evidence-based conclusion, or selection among plausible approaches. The path should not be completely specified for the student.

### DOK 4 - Extended Thinking
Require genuine extended reasoning: investigation, synthesis across ideas/sources/data, design, modeling, transfer to a new situation, iterative revision, or development/defense of a substantial solution. DOK 4 must not be "DOK 3 plus more questions."

If the teacher's listed time is too short for authentic DOK 4, keep an authentic extended task and make the time expectation transparent in the Teacher Guide. The student card may frame it as an extended pathway/project continuation. Never falsely label a short routine task DOK 4 just to fit the period.

## Alignment to learning targets - HARD

- Every DOK task must trace to at least one submitted I Can statement.
- Across the card, all submitted I Can statements should be meaningfully represented unless they are contradictory or too unrelated to combine. If that happens, preserve one card, prioritize the common conceptual thread, and flag the limitation in the Teacher Guide rather than inventing alignment.
- Do not introduce an unrelated standard or content target merely to make a higher DOK task sound sophisticated.
- The Teacher Guide must show the I Can mapping for each DOK task.

## Reading/access level - HARD

When a target reading level is supplied, adjust student-facing wording, sentence length, vocabulary support, chunking, and directions to approximately that access level.

The reading level may NOT reduce:
- the academic content target;
- the required reasoning;
- the DOK level;
- the evidence standard.

Prefer plain language and short directions. Define or support unavoidable domain-specific vocabulary rather than replacing important content vocabulary with inaccurate simplifications.

## Product choice - HARD

The teacher's selected product types are authoritative.

- Show only the selected/entered product types on the student task card.
- Do not silently add an unselected product type.
- If multiple products are allowed, students may choose among them.
- If only one product is allowed, present it as the required product rather than pretending there is a choice.
- The same intellectual evidence must be required regardless of product medium. A video, poster, discussion, model, written response, etc. cannot become academically easier merely because the format changes.
- Product choices are ways to demonstrate learning, not separate DOK levels.

## Teacher constraints and source files

- Follow teacher-provided time, work mode, research/internet policy, and special directions where they do not conflict with this contract.
- Use included source files when they provide task context, required readings, data, images, assignments, or other constraints.
- Do not invent quotations, data, source details, or teacher requirements that are not present.
- If a task calls for a source/graph/image/diagram, make the necessary resource available to the student in the response package or clearly rely on an included source file. Never refer students to a missing resource.

## Student Task Card requirements

Create `student/task_card.html` and `student/task_card.pdf`.

The task card should fit on ONE letter landscape page using the locked `assets/task_card_styles.css` without clipping or unreadably shrinking text.

Required content:
1. Assignment/task title.
2. Subject/course and unit/topic.
3. Compact I Can statement strip.
4. Concise directions that explain the DOK 1 -> 4 progression and when students move forward.
5. Four task areas labeled:
   - DOK 1 - Recall and Reproduction
   - DOK 2 - Skills and Concepts
   - DOK 3 - Strategic Thinking
   - DOK 4 - Extended Thinking
6. Allowed product type(s), exactly matching the teacher selection.
7. Any concise teacher-supplied constraint students need to know, such as individual/partner work or source restrictions.

Do not place teacher answers, scoring commentary, DOK rationales, or hidden implementation notes on the student card.

## Teacher Guide / Evidence Guide requirements

Create `teacher/teacher_guide.html` and `teacher/teacher_guide.pdf` using `assets/guide_styles.css`.

Include:
- request overview and intended use;
- submitted I Can statements;
- a DOK 1-4 table or sections with the exact student task, I Can mapping, why the task is that DOK level, and what convincing evidence would look like;
- exemplar reasoning/solutions or evidence notes when appropriate to the subject/task;
- likely misconceptions or weak evidence to watch for when useful;
- product-neutral evidence expectations;
- reading/access adjustments made, when a target reading level was supplied;
- pacing/facilitation notes, including an honest time note for DOK 4;
- source/resource notes;
- any limitation or uncertainty that should be reviewed by the teacher.

This guide is for teacher review; it is not a student-facing rubric unless the request explicitly asks for one.

## Math, graphs, and visuals - HARD

- Use valid MathJax/TeX for mathematical notation when needed and verify it rendered before PDF creation.
- If a task requires or refers to a graph, generate/embed the real accurate graph or use an included graph source. Do not replace a required graph with prose or ASCII art.
- If a task requires or refers to an image, diagram, table, data display, model, map, or figure, include/embed the actual resource or use an included source file. Do not refer to a missing visual.
- Place generated graph/image assets under `assets/graphs/` or `assets/visuals/`.

## Response package - HARD

Return exactly ONE ZIP with this structure:

```text
CLICK_ME.html
assets/
  task_card_styles.css
  guide_styles.css
  graphs/
  visuals/
student/
  task_card.html
  task_card.pdf
teacher/
  teacher_guide.html
  teacher_guide.pdf
data/
  request.json
  qa.json
```

Empty `graphs/` and `visuals/` folders may be omitted when no such assets are needed.

`CLICK_ME.html` is the teacher entry point. It must show the task title/subject/unit and prominent links to:
- Student Task Card (PDF)
- Student Task Card (HTML)
- Teacher Guide / Evidence Guide (PDF)
- Teacher Guide / Evidence Guide (HTML)

Use local relative links only. The response must work after the ZIP is unzipped.

Copy the request's `response_contract/task_card_styles.css` exactly to `assets/task_card_styles.css` and `response_contract/guide_styles.css` exactly to `assets/guide_styles.css`.

## QA - HARD

Create `data/qa.json` and verify at least:

- `overall_status` is PASS or FAIL.
- `one_card.exactly_one_student_task_card` is true.
- `dok.exactly_four_levels` is true.
- `dok.levels_present` contains 1, 2, 3, 4.
- `dok.cognitive_complexity_not_verb_matching` is true.
- `dok.dok4_is_genuine_extended_thinking` is true.
- `alignment.each_task_maps_to_submitted_i_can` is true.
- `alignment.unrelated_targets_invented` is false.
- `reading_level.academic_demand_reduced` is false.
- `products.only_teacher_allowed_products_shown` is true.
- `products.evidence_standard_constant_across_products` is true.
- `student_card.letter_landscape_one_page` is true.
- `student_card.clipped_or_unreadable_content` is false.
- `math.raw_tex_visible_count` is 0.
- `graphs.required_count` equals `graphs.created_or_supplied_count`.
- `visuals.required_count` equals `visuals.created_or_supplied_count`.
- `pdfs.open_and_visually_checked` is true.
- `links.all_relative_links_resolve` is true.
- `locked_css.task_card_matches_request` is true.
- `locked_css.guide_matches_request` is true.
- `failures` is an array.

PASS is not allowed if the response has four separate cards, a falsely labeled DOK 4 task, lowered academic demand caused by reading-level simplification, unselected product choices, missing referenced resources, raw TeX, broken links, clipped student-card content, placeholder PDFs, or unresolved QA failures.

## Delivery

Return only the completed response ZIP as the authoritative artifact. The teacher should only need to unzip it and open `CLICK_ME.html`.
