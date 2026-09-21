# Tiered Task Generation Contract

STATUS: REQUIRED
VERSION: district-tiered-task-generation/0.3-pilot
DATE: 2026-09-20

This contract defines how one teacher request becomes one integrated student Tiered Task Card plus one Teacher Guide / Evidence Guide. It works with `DISTRICT_RESPONSE_BUILD_STANDARD.md`, `TIERED_TASK_BUILD_EXECUTION.md`, and `DISTRICT_GRAPH_RENDERING_STANDARD.md`.

## 1. Purpose - HARD

Create a ready-to-use extension/enrichment task that increases **cognitive complexity** from DOK 1 through DOK 4 while staying anchored to the teacher's 1-4 I Can statements. This is not an easy/medium/hard/hardest worksheet and it is not four separate task cards.

## 2. Grade level is instructional data - HARD

Grade level is required. Use it together with subject/course and the I Can statements to set:

- appropriate content rigor and abstraction;
- number/data choices and computational complexity where relevant;
- representation type;
- vocabulary and reading load;
- expected reasoning/explanation length;
- independence and scaffolding;
- what counts as authentic application, transfer, and extended thinking.

Do not infer rigor from the wording of an I Can statement alone. The same target wording may require very different work in Grade 2, Grade 8, or high school.

## 3. One-card rule - HARD

- Create exactly ONE integrated student task card.
- The card contains exactly four labeled task areas: DOK 1, DOK 2, DOK 3, DOK 4.
- All four tasks belong to the same card and draw from the submitted I Can statements as a coherent target set.
- Do not generate one card per I Can statement.
- The finished student card must remain one readable letter-landscape PDF page.

## 4. DOK meaning - HARD

Depth of Knowledge is the cognitive processing required, not difficulty, length, or verb matching.

### DOK 1 - Recall and Reproduction
Direct retrieval, identification, description, representation, routine calculation, or reproduction of foundational knowledge needed for the target.

### DOK 2 - Skills and Concepts
Application of concepts/procedures with some decision making: compare/classify, interpret information, organize relationships, choose a method, explain how/why, or apply learning in a familiar but not purely routine context.

### DOK 3 - Strategic Thinking
Non-routine reasoning, justification, critique, defense, revision, evidence-based conclusion, or selection among plausible approaches. The path is not completely specified.

### DOK 4 - Extended Thinking
Genuine extended reasoning through investigation, synthesis across ideas/sources/data, design, modeling, transfer, iterative revision, or development/defense of a substantial solution. DOK 4 must not be DOK 3 plus more questions.

If the teacher's time is too short for authentic DOK 4, preserve authentic extended thinking and make the time expectation transparent in the Teacher Guide rather than falsely relabeling a short routine task.

## 5. Alignment to learning targets - HARD

- Every DOK task maps to at least one submitted I Can statement.
- Across the card, all submitted I Can statements are meaningfully represented unless they are contradictory or too unrelated to combine.
- Do not invent unrelated standards/content just to make DOK 3/4 sound sophisticated.
- The Teacher Guide shows the I Can mapping for each DOK task.
- If a student task changes during layout correction, the Teacher Guide must be updated to repeat the exact final task.

## 6. Reading/access level - HARD when supplied

A target reading/access level may change wording, sentence length, vocabulary support, chunking, and directions. It may NOT reduce the academic target, required reasoning, DOK level, or evidence standard.

## 7. Product choice - HARD

The teacher's selected product types are authoritative.

- Broad choice is the default when the teacher leaves the Advanced product list unchanged.
- Show only selected/entered product types on the student card.
- Do not silently add an unselected product.
- If multiple products are allowed, students may choose among them.
- If only one is allowed, present it as the required product.
- The intellectual evidence stays constant across product formats.
- Product formats are not DOK levels.

## 8. Teacher constraints and source files

- Zero, one, or many source files may be included. Treat all listed files in `request.json` as available supporting sources.
- Read relevant sources once; do not repeatedly rediscover them.
- Follow time, work mode, research policy, and teacher directions when they do not conflict with HARD contracts.
- Do not invent quotations, source facts, data, measurements, or teacher requirements.
- If a task calls for a source/graph/image/diagram, make that resource available in the response or clearly rely on an included source file. Never refer students to a missing resource.

## 9. MathJax, graphs, diagrams, and visuals - HARD

Follow the packaged district standards.

- Use valid MathJax/TeX for mathematical notation.
- Generate required supported Cartesian graphs with the packaged canonical graph tool.
- Generate each distinct graph once and reuse it.
- Do not use generative imagery for quantitative graphs.
- Include real diagrams/figures when the task depends on spatial/structural information.
- Do not reveal an answer when constructing the graph/diagram is itself the assessed skill; provide only an answer-neutral scaffold.
- Store graphs under `assets/graphs/` and other generated instructional visuals under `assets/visuals/`.

## 10. Student Task Card requirements

Create `student/task_card.html` and `student/task_card.pdf`.

The card must fit on ONE readable letter-landscape page using the locked `assets/task_card_styles.css`.

Required content:

1. assignment/task title;
2. subject/course and grade level;
3. compact I Can statement strip;
4. concise directions explaining the DOK 1 -> 4 progression;
5. exactly four task areas labeled DOK 1-4 with their canonical DOK names;
6. allowed product type(s), exactly matching the teacher selection;
7. concise student-facing work/research constraints when relevant;
8. any graph/diagram/visual the task genuinely needs.

Do not place teacher answers, DOK rationales, QA details, or hidden implementation notes on the student card.

### One-page fit policy

Keep the locked CSS unchanged. If content overflows, tighten wording and remove redundancy without lowering academic demand. Do not solve overflow by shrinking the locked fonts/margins or deleting a required visual. If the required content truly cannot fit legibly, FAIL rather than returning a clipped card.

## 11. Teacher Guide / Evidence Guide requirements

Create `teacher/teacher_guide.html` and `teacher/teacher_guide.pdf` using `assets/guide_styles.css`.

Include:

- request overview/intended use and grade level;
- submitted I Can statements;
- DOK 1-4 sections with the **exact final student task**, I Can mapping, why the task is that DOK, and what convincing evidence looks like;
- exemplar reasoning/solutions/evidence notes where appropriate;
- likely misconceptions or weak evidence when useful;
- product-neutral evidence expectations;
- reading/access adjustments when supplied;
- pacing/facilitation notes including honest DOK 4 timing;
- graph/diagram/visual notes;
- source/resource notes;
- material limitations, uncertainties, or resolved conflicts.

## 12. Locked styling - HARD

The response uses the exact CSS snapshots included in the request:

- copy `response_contract/task_card_styles.css` byte-for-byte to `assets/task_card_styles.css`;
- copy `response_contract/guide_styles.css` byte-for-byte to `assets/guide_styles.css`;
- use task-card CSS for the student card;
- use guide CSS for `CLICK_ME.html` and the Teacher Guide;
- do not add page-local CSS that alters the locked geometry/visual system;
- record expected/actual SHA-256 hashes in QA.

## 13. Response package - HARD

Return exactly one ZIP with:

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
  mechanical_qa.json
```

`CLICK_ME.html` is the teacher entry point with prominent links to the student Task Card HTML/PDF and Teacher Guide HTML/PDF plus a small QA link.

## 14. QA - HARD

Create `data/qa.json`. PASS requires, at minimum:

- exactly one student task card;
- exactly four DOK levels, 1-4;
- DOK 4 is genuine extended thinking;
- every task maps to submitted I Can statements;
- no unrelated target is invented;
- Teacher Guide repeats the exact final student tasks;
- reading/access changes do not reduce academic demand;
- only teacher-allowed products appear;
- evidence standard remains constant across product formats;
- student card PDF is one letter-landscape page with no clipping/unreadable content;
- required math/graphs/visuals are present and correct;
- all required relative links resolve;
- locked CSS hashes match;
- required PDFs open;
- unresolved conflicts/failures are zero.

Use the packaged `tiered_task_qa.py` for mechanical file/link/hash/PDF checks rather than recreating those checks manually.

## 15. Delivery - HARD

Return only the completed response ZIP as the authoritative artifact. End the user-facing response with exactly:

Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.
