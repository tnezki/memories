# Tiered Task Generation Contract

STATUS: REQUIRED
VERSION: district-tiered-task-generation/0.2-pilot

This contract is executable. It defines how one teacher request becomes one integrated student Tiered Task Card plus one Teacher Guide / Evidence Guide.

This tool also packages `DISTRICT_RESPONSE_BUILD_STANDARD.md`. Follow both contracts. The shared district standard governs MathJax, graph accuracy, diagrams/visuals, locked CSS, PDF QA, links, package integrity, and conflict precedence. This Tiered Task contract adds the content and layout requirements specific to the DOK card.

If a true HARD-to-HARD conflict remains after applying the shared conflict rules, record it in `data/qa.json`, set overall status to FAIL, and do not silently drop either requirement.

## Purpose

Create a ready-to-use extension/enrichment task that increases **cognitive complexity** from DOK 1 through DOK 4 while staying anchored to the teacher's 1-4 I Can statements. This is not an "easy / medium / hard / hardest" worksheet and it is not four separate task cards.

## One-card rule - HARD

- Create exactly ONE integrated student task card.
- The card contains exactly four labeled task areas: DOK 1, DOK 2, DOK 3, DOK 4.
- All four tasks belong to the same task card and draw from the submitted I Can statements as a coherent target set.
- Do not generate one card per I Can statement.
- The finished student card must remain one readable letter-landscape PDF page.

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
- If the task is revised to solve a layout issue, update the Teacher Guide so it still repeats the exact final student task.

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

- Follow teacher-provided time, work mode, research/internet policy, and special directions where they do not conflict with HARD contracts.
- Structured choices in `request.json` outrank conflicting free-form notes.
- Use included source files when they provide task context, required readings, data, images, assignments, or other constraints.
- Do not invent quotations, data, source details, or teacher requirements that are not present.
- If a task calls for a source/graph/image/diagram, make the necessary resource available to the student in the response package or clearly rely on an included source file. Never refer students to a missing resource.
- Record any material instruction conflict according to the shared district standard.

## MathJax, graphs, diagrams, and visuals - HARD

Follow `response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md` exactly.

For this tool specifically:

- Any mathematical expression in the final student card or Teacher Guide should use valid MathJax/TeX rather than improvised italic HTML when true mathematical notation is present. For example, render Newton's Second Law as `\\(F=ma\\)` rather than `<i>F</i> = <i>ma</i>`.
- The PDF must be generated only after MathJax typesetting completes.
- If a DOK task requires interpreting a graph, include the actual accurate graph unless creating that graph is itself the student task.
- Prefer a dedicated grapher for mathematical graphs. If unavailable, use a deterministic accurate plotting method, not generative imagery.
- If a DOK task depends on a physical setup, spatial relationship, geometry, circuit, force setup, or other diagram-worthy scenario, include a clean instructional diagram when it materially reduces ambiguity.
- Do not give away an assessed diagram. For example, if students are being assessed on drawing a free-body diagram, a neutral cart/object/setup sketch may be included, but do not pre-draw the answer force vectors.
- Save mathematical graphs under `assets/graphs/` and other generated instructional visuals under `assets/visuals/`.
- The Teacher Guide must show/describe the same graph/diagram references used by the exact student task and must not answer a different version of the prompt.

## Student Task Card requirements

Create `student/task_card.html` and `student/task_card.pdf`.

The task card must fit on ONE letter landscape page using the locked `assets/task_card_styles.css` without clipping or unreadably shrinking text.

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
8. Any graph/diagram/visual the task genuinely needs, embedded at readable size without revealing an answer the student is supposed to create.

Do not place teacher answers, scoring commentary, DOK rationales, QA details, or hidden implementation notes on the student card.

### One-page fit policy

- Keep the locked CSS unchanged.
- If content overflows, first tighten wording, remove redundancy, use shorter student directions, and simplify the task presentation without reducing the academic demand.
- Do not silently shrink fonts or margins below the locked style.
- Do not delete a required graph/diagram merely to make the page fit.
- If the requested combination of required content truly cannot fit legibly on one landscape page, record the limitation and FAIL rather than returning a clipped or unreadable card.

## Teacher Guide / Evidence Guide requirements

Create `teacher/teacher_guide.html` and `teacher/teacher_guide.pdf` using `assets/guide_styles.css`.

Include:

- request overview and intended use;
- submitted I Can statements;
- a DOK 1-4 table or sections with the **exact final student task**, I Can mapping, why the task is that DOK level, and what convincing evidence would look like;
- exemplar reasoning/solutions or evidence notes when appropriate to the subject/task;
- likely misconceptions or weak evidence to watch for when useful;
- product-neutral evidence expectations;
- reading/access adjustments made, when a target reading level was supplied;
- pacing/facilitation notes, including an honest time note for DOK 4;
- graph/diagram/visual notes when a visual is used or intentionally withheld because construction is assessed;
- source/resource notes;
- any limitation, uncertainty, or resolved conflict that should be reviewed by the teacher.

This guide is for teacher review; it is not a student-facing rubric unless the request explicitly asks for one.

## Locked styling - HARD

The response package must use the exact CSS snapshots included in the request.

- Copy `response_contract/task_card_styles.css` byte-for-byte to `assets/task_card_styles.css`.
- Copy `response_contract/guide_styles.css` byte-for-byte to `assets/guide_styles.css`.
- Use the task-card CSS for the student card.
- Use the guide CSS for `CLICK_ME.html` and the Teacher Guide.
- Do not replace the styles with CSS from an attached source file.
- Do not add inline overrides that change the locked page geometry, fonts, colors, or layout rules.
- Math/graph/visual support classes are already part of the locked CSS snapshot; use them rather than inventing a conflicting visual system.
- The expected CSS SHA-256 hashes are stored in `request.json`. Compute the response copies' hashes and record exact-match results in `data/qa.json`.

## Response package - HARD

Return exactly ONE ZIP with this structure:

```text
CLICK_ME.html
assets/
  task_card_styles.css
  guide_styles.css
  graphs/             (when needed)
  visuals/            (when needed)
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

Keep those four resources as the primary actions. Also provide a small non-primary QA status/link to `data/qa.json` so the completed QA is easy to inspect without cluttering the main workflow.

Use local relative links only. The response must work after the ZIP is unzipped.

## QA - HARD

Create `data/qa.json` and verify at least:

### Contract and conflict checks

- `overall_status` is PASS or FAIL.
- shared response standard version matches the request.
- Tiered Task generation-contract version matches the request.
- `conflicts.detected_count`, `resolved_count`, `unresolved_count`, and `items` are present.
- PASS requires `conflicts.unresolved_count` = 0.

### Tiered Task checks

- `one_card.exactly_one_student_task_card` is true.
- `dok.exactly_four_levels` is true.
- `dok.levels_present` contains 1, 2, 3, 4.
- `dok.cognitive_complexity_not_verb_matching` is true.
- `dok.dok4_is_genuine_extended_thinking` is true.
- `alignment.each_task_maps_to_submitted_i_can` is true.
- `alignment.all_submitted_i_can_statements_meaningfully_represented` is true unless a documented limitation explains otherwise.
- `alignment.unrelated_targets_invented` is false.
- `alignment.teacher_guide_repeats_exact_student_tasks` is true.
- `reading_level.academic_demand_reduced` is false.
- `products.only_teacher_allowed_products_shown` is true.
- `products.evidence_standard_constant_across_products` is true.

### Student-card layout checks

- `student_card.letter_landscape_one_page` is true.
- `student_card.pdf_page_count` = 1.
- `student_card.clipped_or_unreadable_content` is false.
- `student_card.visually_checked` is true.

### MathJax checks

Follow the shared standard and record:

- pages containing math;
- rendered/checked status;
- raw TeX visible count = 0;
- PDF generated after MathJax typesetting;
- external-runtime dependency status.

### Graph checks

- `graphs.required_count` equals `graphs.created_or_supplied_count`.
- dedicated grapher availability/use is recorded.
- every graph asset includes generation method and accuracy-check result.

### Visual/diagram checks

- `visuals.required_count` equals `visuals.created_or_supplied_count`.
- every referenced diagram/visual exists and is readable.
- no provided scaffold reveals an answer that the student is supposed to construct.

### PDF and link checks

- `pdfs.rendered_and_visually_checked` is true.
- `pdfs.openable` is true.
- `links.all_relative_links_resolve` is true.
- `links.click_me_has_all_four_required_resource_links` is true.
- `links.click_me_links_qa_record` is true.

### Locked CSS checks

- `locked_css.task_card_expected_sha256` matches the value in `request.json`.
- `locked_css.task_card_actual_sha256` is computed from `assets/task_card_styles.css`.
- `locked_css.task_card_matches_request` is true.
- corresponding guide-style expected/actual hash fields exist and match.

### Failure rule

`failures` must be an array. `overall_status: PASS` is not allowed if `failures` contains an unresolved failure.

PASS is not allowed if the response has four separate cards, a falsely labeled DOK 4 task, lowered academic demand caused by reading-level simplification, unselected product choices, missing referenced resources, raw TeX, inaccurate/missing required graphs, missing required diagrams, answer-revealing visual scaffolds, broken links, clipped student-card content, placeholder PDFs, mismatched locked CSS, unresolved conflicts, or unresolved QA failures.

## Delivery - HARD

Return only the completed response ZIP as the authoritative artifact.

The user-facing response that returns the ZIP must end with this exact final line:

Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.
