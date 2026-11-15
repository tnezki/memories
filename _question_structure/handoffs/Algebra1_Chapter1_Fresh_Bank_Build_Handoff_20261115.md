# Algebra 1 — Chapter 1 Fresh Question-Bank Build
## Detailed handoff, source map, production recipe, and quality gates

**Prepared:** November 15, 2026  
**Project:** Portfolio → Curriculum Build → CPM Tools → Algebra 1 Question Bank  
**Next chat:** Build **Chapter 1** from the authoritative learning goals and supporting skills, not by patching or lightly editing the old Chapter 1 bank.  
**Scope:** Question-bank design and teacher-review interface. **Do not** change Assessment Builder generation permissions, student Portfolio evidence, grades, rosters, email delivery, or other course applications.  
**Delivery:** When repository files are created/modified, **one GitHub Transfer ZIP, Local Only**, with the same ZIP link at the beginning and end of the response. No GitHub writing, commits, pushes, pulls, or automatic synchronization.

---

## 0. The next-chat instruction — read and execute

> Read this handoff **in full**, then inspect the *current* Google Drive mirror of CPM_Tools and the installed Question Structures resources. Chapter 1 is a **fresh bank design**: use the approved Chapter 1 learning goals, nine supporting skills, and actual CPM lesson sequence as the authority. Do not take the existing Chapter 1 families, shuffle them, give them a new label, or preserve their arbitrary family counts. Preserve the old bank for provenance/history and do not discard teacher feedback, but build a genuinely new set of skill-aligned families and exemplars. Consult the canonical 390-family Question Structures system and the five November 15 resource-research passes **before authoring**, using the accepted Chapter 3 format and Chapter 2 production lessons as references. Begin with a coherent **first pass of all four categories** — Direct Skills, original CPM Review & Preview, Summative MC, Extensions — with correct representative questions and answers, but **do not yet force three difficulty levels or large variation pools**. Show only functioning controls. Conduct focused subsequent passes, one or two kinds of improvement per pass, with teacher spot-check opportunities between transfers. Never deliver unfinished or mathematically unverified questions as if they passed QA. The amount of content is governed by necessary evidence, not a target count. Use the canonical Graph Tool; copy original CPM Review & Preview questions *exactly* and separately label teacher-generated number-swapped versions in metadata. Keep Chapter 2 and Chapter 3 unchanged, with explicit byte preservation checks.

### Non-negotiable principles

1. **Start over in Chapter 1 design, not a patch job.** Existing `CH01.json` is archival/reference material and a source of stable historical provenance, **not a family blueprint or quota**. A new canonical Chapter 1 bank can be built in a working staging file, then introduced through a verified transfer after QA.
2. **Authority sequence:** **Learning Goal → Supporting Skill → Evidence Job → Student Action → Canonical Structure → Response/Representation → Actual Question → Independently Checked Answer.** Lesson placement follows CPM sequence.
3. **Exactly four displayed categories:** Direct Skills; Review & Preview; Summative MC; Extensions. No separate Reasoning, Diagnosis, or Explanation categories. Reasoning or interpretation is a legitimate **mathematical action within a category** when the skill genuinely calls for it.
4. **No numerical quotas.** Neither three families per lesson nor 20 tasks per skill nor 24 versions per level is a goal. Use **enough distinct evidence** to assess the actual skills; not more, not less. A lesson may have a different number of families than another lesson.
5. **Questions must be mathematically substantive.** Do not manufacture “new skills” by merely adding *justify*, *explain*, *find an error*, or a longer story to the same exercise. A meaningful reversal, representation translation, or comparison may warrant a distinct family; a word change does not.
6. **A visible question is not proof of readiness.** Every authored exemplar and every generated version needs its own verified mathematical answer. Visual QA, MathJax, distractors, and independent re-solving are additional gates.
7. **Never compromise the user’s prior accepted work.** Chapter 2 and Chapter 3 data, stable teacher-review namespaces, and working interfaces stay intact. Reuse existing shared components without wholesale redesign.
8. **Teacher review is an approval gate.** New families/candidates are draft and not eligible for automated assessments, scoring, or Portfolio until separately reviewed and integrated through an approved workflow.

---

## 1. Verified Chapter 1 learning goals, skills and lesson progression

The following were read from the **Chapter 1 embedded bank snapshot** in the November 15 shared `CPM_Tools/banks/section.html` (Pass 13). **Before authoring, compare with the authoritative `data/algebra1_assessment_plans.json`, schema version 5, and actual CPM chapter lessons.** If that current canonical plan differs, the canonical plan wins; document the difference rather than guessing.

### Section 1.1: Growing patterns and introductory quadratics

**Goal `ALG1-S1.1`:** “I can recognize and represent growing patterns and explain how graphs show different kinds of change.”

| Skill | Exact supporting-skill text | Natural evidence to investigate (illustrative, not mandatory families) |
|---|---|---|
| `ALG1-S1.1-SK01` | Identify and extend visual and numerical patterns. | Extend visual tile patterns; describe additive vs other growth; predict a stage; determine a missing stage; match different depictions. |
| `ALG1-S1.1-SK02` | Organize pattern information in tables and graphs. | Complete/build tables; plot coordinates; read/construct stage-vs-total graphs; match tile figures with tables or graphs. |
| `ALG1-S1.1-SK03` | Recognize when a pattern is not linear. | Examine successive differences; contrast tables/graphs/figures; select the nonconstant-change pattern; distinguish linear from curved growth. |
| `ALG1-S1.1-SK04` | Describe features of an introductory quadratic graph. | Read shape, location, change in direction, symmetry/basic features using source-appropriate graphs; compare to a linear graph. Do not introduce advanced quadratic techniques ahead of lessons. |

**Lessons in the current bank snapshot:**

- **1.1.1 — Solving Puzzles in Teams:** earliest tasks must respect the actual introductory lesson; do not drop in later-function or quadratic algebra merely because the section ultimately contains it.
- **1.1.2 — Investigating the Growth of Patterns:** genuine tile figures, tables, graphs and stage rules as the textbook introduces them.
- **1.1.3 — Investigating the Graphs of Quadratic Functions:** introductory graphical properties and comparisons grounded in the actual lesson, not later factoring, transformations or vertex-form material unless the source explicitly teaches it.

### Section 1.2: Functions, graphs, rules, domain and range

**Goal `ALG1-S1.2`:** “I can identify and interpret functions using rules, graphs, tables, domain, and range.”

| Skill | Exact supporting-skill text | Natural evidence to investigate (illustrative, not mandatory families) |
|---|---|---|
| `ALG1-S1.2-SK01` | Describe important features of a graph. | Read intervals of increase/decrease; local shape; intercepts, extrema or end behavior when lesson-appropriate; compare graph features. |
| `ALG1-S1.2-SK02` | Connect inputs and outputs through function rules. | Evaluate from a machine/rule/table/graph; reverse known outputs to inputs when valid; complete a table; distinguish function-notation input and output. |
| `ALG1-S1.2-SK03` | Determine whether a relation is a function and explain why. | Ordered pairs, tables, mappings, graphs; repeated-input reasoning; vertical line test when taught; classify and identify the evidence. |
| `ALG1-S1.2-SK04` | Identify domain and range in different representations. | Finite ordered-pair/table sets; graph endpoints including open/closed; restrictions from a supplied situation; map from input/output sets. |
| `ALG1-S1.2-SK05` | Recognize the behavior of different function families. | Compare linear, quadratic, absolute-value and cube-root behavior only to the extent established in the source lessons. |

**Lessons in the current bank snapshot:**

- **1.2.1 — Describing a Graph**
- **1.2.2 — Cube Root and Absolute Value Functions**
- **1.2.3 — Function Machines**
- **1.2.4 — Functions**
- **1.2.5 — Domain and Range**

**Lesson progression is a gate.** A later problem may revisit an earlier skill with a new representation or additional reasoning; the first lesson that introduces a skill should not inherit material from the end of the section. Verify the detailed CPM lesson learning focus, “I can” statements, worked examples, and teacher plans before assigning families.

**Required artifact before authoring:** a simple, machine-readable **goal × skill × lesson × evidence-job × representation matrix**. It should record lesson prerequisites, teacher-facing reason for inclusion, canonical structure IDs, and proposed response type. Reject rows with “question slot needed” as their only rationale.

---

## 2. Exact sources to inspect first, in priority order

### A. Current installed application and course content — use Google Drive mirror

CPM_Tools is a **local** application mirrored to Google Drive; do **not** assume it lives in the GitHub repository. Search connected Drive before requesting uploads. The following IDs were verified in the earlier Chapter 2 process; **revalidate metadata, path and hash on entry to the new chat**:

| Installed path / resource | Mirror ID or location | Purpose |
|---|---|---|
| `CPM_Tools/banks/data/CH01.json` | Search the bank data folder; do not infer file ID | Existing Chapter 1 archival starting point, not target design |
| `CPM_Tools/banks/data/CH02.json` | `1LBUWUek5s9A9HEFVn61elcBO2KleYzjC` | Preserve/compare; Chapter 2 after Pass 13 |
| `CPM_Tools/banks/data/CH03.json` | `1I6GsLJlnhZwbYQNjK-gn2LqVVjlsWnR2` | Chapter 3 accepted interface and evidence reference |
| `CPM_Tools/banks/section.html` | `11XsoNoxbUG-GlWvQsoEQxyFJdzQyGQf6` | Shared page with **three embedded bank snapshots**; must keep CH02/CH03 untouched |
| `CPM_Tools/banks/bank.js` | `1_E-4sFNtK4aMpq2eFiIWsEu_yKgjfYIn` | Teacher bank categories, difficulty, New Question, solution and review controls |
| `CPM_Tools/banks/bank.css` | Bank folder search | Shared presentation and print behavior |
| `data/algebra1_assessment_plans.json` | Search current mirror | Authoritative learning goals/skills, schema version 5 |
| Original Algebra 1 Chapter 1 CPM eBook lessons and figure assets | Search curriculum/textbook archives and lesson HTML/figures in Drive | Exact Review & Preview and actual lesson scope |
| Bank data folder | `1tDKOYiaVUZjtXaVcd6OkLJz0SK8yhh1D` | Locate current chapter JSON |
| Bank main folder | `1lNCzEQctnGgR3Wx36bJlq21RZ0Z1caCW` | Locate JS, HTML, CSS and assets |
| Bank assets folder | `1xVUn8wcoNtIOKroQ7L8qgXTA3MgUVkwe` | Resolve/reference diagrams and images |

**Search lesson HTML under short names too** (e.g., `1-1-1.html`, saved eBook names, and accompanying `_files` directories). Chapter 2 mistakes occurred because only one naming pattern was searched. Check resource media, not merely text.

### B. Canonical question-structure system — read actual files

In the user's `memories/_question_structure/` (mirrored to Drive, and readable in the GitHub `tnezki/memories` repo where applicable):

- `QUESTION_STRUCTURE_CORE.md` — **the required design sequence**, evidence/response/representation compatibility, concise wording, true dependent multistep structure, legitimate variations, forbidden shortcuts, and destination-specific task design. Its checked header is **Question Structure Core v1.4**.
- `catalogs/math_question_family_registry.json` — 165 foundational/middle-course families.
- `catalogs/math_question_families_algebra1.json` — **95 Algebra 1 canonical families**.
- `catalogs/math_question_families_geometry.json` — 25 families.
- `catalogs/math_question_families_advanced.json` — 62 families.
- `catalogs/math_question_families_calculus.json` — 43 families.
- The full library contains **390 math-family contracts** (165+95+25+62+43) across courses. For Algebra 1, inspect Algebra 1 contracts **and** foundational ones for early prerequisite content.
- Related manifests, schema, course mappings, wording profiles, mathematical parameter/parallel-variant rules, quality standards and representations rules in this same tree.

**Examples confirmed in the actual 95-family Algebra 1 registry** (use exact IDs when the evidence fits, not because the ID's name resembles the topic): `FUNC_EVALUATE_TABLE`, `FUNC_EVALUATE_GRAPH`, `FUNC_EVALUATE_FORMULA`, `FUNC_MAPPING_CLASSIFY`, `FUNC_ORDERED_PAIRS_CLASSIFY`, `FUNC_GRAPH_CLASSIFY`, `FUNC_DOMAIN_RANGE_SET_TABLE`, `FUNC_DOMAIN_RANGE_GRAPH`, `FUNC_CONTEXT_MODEL`, `FUNC_COMPARE_VALUES`, `FUNC_GRAPH_EQUATION_INTERSECTIONS`, `SLOPE_FROM_TWO_POINTS`, `LINE_WRITE_TWO_POINTS`, `LINE_GRAPH_SLOPE_INTERCEPT`. For Chapter 1 find and inspect additional pattern/coordinate/area/graph contracts instead of reusing slope families by habit.

**Hard meaning of a canonical family:** an executable design contract identifying the specific **evidence job**, **student action**, **response mode**, **representation role**, **invariant mathematics**, **legal variation axes**, and forbidden shortcuts. Do not assign a matching-looking `question_structure_id` after writing unrelated prose. If a task changes the evidence action, choose a different contract or document a justified extension.

### C. November 15 source-idea / variation / diagnostic research

These catalogs/guides were researched and installed earlier; inspect actual data records and confidence/source tags. They are **ideation resources**, **not compulsory question slots** and **not approved bank questions**.

| Research source | Verified scale | What to extract |
|---|---:|---|
| `catalogs/cpm_reference_question_ideas_20261115.json`, `guides/CPM_REFERENCE_CATALOG_README.md` | 42 initial ideas across seven courses | Source types and real mathematical task shapes |
| `catalogs/cpm_question_structure_deep_research_20261115.json`, `guides/CPM_QUESTION_SOURCE_DEEP_RESEARCH_README.md` | 111 additional ideas; 153 total | Evidence tasks, representation translations, reverse unknowns and source confidence |
| `catalogs/cpm_question_variation_quality_pass4_20261115.json` and its guide | 28 variation recipes, 16 QA checks | Legal variation axes, same-difficulty equivalence, misconception/answer traps |
| `catalogs/cpm_diagnostic_evidence_pass5_20261115.json` and its guide | 28 diagnostic profiles; 56 paired prompts; 14 gates | Short contrasting probes, possible misconceptions; never automatic labels about a student |
| `memories/_question_structure/qa/check_student_question_hygiene.py` | Reusable student-prompt hygiene checker | Caption leakage, student-facing internals, malformed directions; update rule set only for validated problems |

**Research source archives:** Google Drive `~Curriculum → All Classes Resources → Resources`, Kuta worksheets, Exeter mathematics materials, Carnegie Algebra 2, CPM CC1/CC2/CC3, Common Core samples, saved DeltaMath example PDFs and DeltaMath topic inventories. These are structure/variation references; **do not claim publisher questions are copied verbatim except true CPM Review & Preview from verified original lesson pages**. DeltaMath topic-inventory titles are *not* actual problem specimens. Preserve confidence tags: visually inspected vs extracted text vs folder inventory.

### D. Existing bank references — use correctly

- **Chapter 3:** teacher-accepted overall design/visual standard for Direct Skills, levels, New Question, source fidelity and teacher review. Do not rewrite Chapter 3.
- **Chapter 2:** the procedural history and repair lessons, including multiple passes on Direct Skills, exact CPM Review & Preview, graph/tile images, diamond tool, MC/Extension variation, MathJax and answer-key/distractor balance. **Do not assume all Chapter 2 questions are pedagogically perfect** because automated checks passed.
- **Old Chapter 1:** preserve as historical reference and provenance; do not inherit its simplistic 3/3/3-per-I-can allocation. The embedded Chapter 1 snapshot in the Pass 13 page had **96 stored family records** in `TEACHER_REVIEW_DRAFT` state. Historical approvals in old AP1/AP2 data may apply to specific original exemplars, **never automatically to newly generated families or versions**.

---

## 3. The permanent bank-design recipe

### 3.1 Make the evidence matrix before any prompt

For each authoritative **supporting skill**, brainstorm multiple real mathematical evidence opportunities using natural representations (tile figures, tables, graphs, ordered pairs, equations, mapping diagrams, contexts, comparisons, missing inputs/outputs, inverse actions, and true construction tasks). The aim is **broad candidate exploration**, not choosing a quota of 20. Choose only what is appropriate for the skill and its lesson sequence.

Record at minimum:

`learning_goal_id | skill_id | lesson_id | prerequisite | evidence_job | student_action | canonical_family_id | response_mode | representation_mode | graph/diagram tool | difficulty_axes | legal_variation_axes | expected_answer_method | source_basis | teacher_rationale`

**Then deduplicate by *mathematical action***, not by family name or numeric values. For example, three prompts that all say “find the next number” with larger integers are probably **one** family with numerical versions. A graph-to-table match, a missing-input reversal, and the construction of a function rule are different kinds of evidence. Do not force a graph onto an arithmetic-only task, nor force a long explanation onto a direct calculation.

A real Lesson 1.1.2 pattern evidence brainstorm could include: count tiles in authentic figures, complete a table, map stages to coordinates, distinguish constant from changing differences, extend to an unseen figure, write a stage rule where introduced, or compare two representations. These become separate families **only if** they actually demand different student evidence.

### 3.2 Separate family, exemplar and candidate

- **Learning goal:** broad intended understanding, owned by Assessment Plan.
- **Supporting skill:** specific assessable outcome, owned by Assessment Plan.
- **Evidence job:** what correctness proves (e.g., identifies same input with different outputs).
- **Canonical family contract:** permissible student action + response/representation + mathematical invariant.
- **Question family:** the distinct local reusable task tied to a lesson/skill, with a stable `family_id`.
- **Exemplar:** the first complete, correct, representative version; **not** a template lacking an answer.
- **Candidate/variation:** a fully instantiated question with a distinct ID, `student_html`, independently checked `answer` and `worked_steps`/`solution`, graphical assets if needed, and review status.
- **Difficulty:** meaningful mathematical workload or structure. It is **not** a separate skill, category, mastery grade, or arbitrary number-size increase.

Typical family metadata to retain/author (adapt to the installed schema, do not invent a parallel unrecognized app schema): `family_id`, `teacher_question_id`, `category`, `cpm_lesson`, `learning_goal_id`, `primary_skill_ids`, `question_structure_id`, `evidence_job`, `student_action`, `representation_mode`, `response_mode`, `template_contract`, `source_basis`, `difficulty_contract` where applicable, `exemplar`, `candidates`, `approval_status`, `generation_eligibility`, `pilot_hidden`, `family_revision`, historical provenance. Candidate metadata: `variant_id`, `difficulty` if applicable, `variation_index`, `student_html`, `answer`, `worked_steps`, `solution`, `skill_ids`, `variant_status`, `assessment_eligible`, `source`.

**Never render technical metadata to students** if it doesn't help solve the problem. Keep original-source numbers in teacher controls/heading, not as noisy instructions inside each variation. Do not have alt text, captions, tables or graph labels disclose the answer accidentally.

### 3.3 Four categories, exactly

| Category | Evidence role | Difficulty controls? | New Question behavior? | Source rule |
|---|---|---|---|---|
| **Direct Skills** (`direct`) | Many **distinct** skill-aligned actions across appropriate representations; routine, interpretation, matching, construction as needed | **Yes, Levels 1–3**, introduced in a later dedicated pass | Cycling **within the selected difficulty only** after candidate pool exists | Teacher-authored, grounded in canonical contracts and real CPM progression |
| **Review & Preview** (`spiral`) | True CPM spiral/practice source, not forced to assess only the current lesson's newest target | **No levels** | Swaps only between the original plus validated same-task alternatives; hide if only original | **Original CPM task copied exactly**, images included; generated versions clearly distinguished in metadata |
| **Summative MC** (`multiple_choice`) | Test-only selected-response evidence of learning goals/skills, with plausible distinct distractors | **No levels** | Cycle validated parallel versions; initially hide if one version | Teacher-authored, four distinct options, **exactly one defensible correct answer**, no answer-location pattern |
| **Extensions** (`extension`) | Optional deeper mathematical transfer, multi-representation/missing givens/novel application only when genuine | **No levels** | Cycle real variations; initially hide if one version | Optional, no “required for an A”, no artificial wordy complexity |

**Family count policy:** for Summative MC and Extensions, the teacher's Chapter 2 implementation used **three per lesson as a compact starting point**, and discussed **about 3–5 maximum**. These are **practical preferences, not a strict formula**, and do not supersede the new rule: use the smallest adequate set for useful skill evidence. The number of Direct Skills families per lesson is especially not fixed. Review & Preview availability depends on the *actual original CPM source*, not an invented count.

---

## 4. Recommended staged-pass workflow — confirmed for Chapter 1

**YES: the best first content pass is to build the four categories with meaningful base questions first, and postpone difficulty/large variation pools until later targeted passes.** This prevents generating thousands of variations from bad family designs. However, **answer and solution correctness cannot be postponed**. Every exemplar must be fully solved and verified before it enters the first transfer.

### Pass 0 — Source verification and independent design (no production questions yet)

1. Verify the current installed Drive mirror, file hashes, lesson sources, source diagrams, assessment plan and transfer history. Inspect the old Chapter 1 bank **only for archival provenance/IDs/teacher review**.
2. Read authoritative Chapter 1 goals, exact supporting skills and all eight real CPM lessons in sequence. Resolve actual introductory content vs later prerequisites; read real Review & Preview source blocks and original figures.
3. Consult the canonical Algebra 1/foundational families and research catalogs. Build the 9-skill evidence matrix and a proposed family inventory across the four categories. Remove identical student actions, fix coverage gaps, and write an explicit lesson rationale. Do not write a fixed desired question count.
4. Record exact original-source problem IDs and images, source confidence and whether an answer key exists. Track uncertain originals as `ANSWER_KEY_PENDING`/review only rather than inventing keys.
5. Draft a compact internal design QA report: skill coverage, too-early material, family overlap, representation mix, source provenance. This stage can be combined with Pass 1 execution in one chat **as long as it is actually performed first**.

### Pass 1 — Core questions **for all four categories** (one complete representative question/family)

Build the right *types* of questions across the entire chapter **before multiplying versions**:

- **Direct Skills:** correct short exemplar for each distinct chosen mathematical family. Use genuine graph/table/tile/mapping representations when demanded. No fake three-level buttons until those levels exist.
- **Review & Preview:** faithfully transcribe each selected original CPM problem from the actual lesson source, exact wording/numbers/parts, exact original diagrams/images (or a clearly documented faithful reconstruction if the original cannot be used). Set source and validation status honestly. Do **not** change or “improve” original wording while claiming verbatim copying.
- **Summative MC:** small, skill-aligned set of strong base MC prompts with four plausible choices, only one correct, original solved key and distractor rationale. Test-only category, teacher-review drafts.
- **Extensions:** a small set of truly deeper/transfer-based base questions; solve each independently, check that it actually extends the skill and lesson, not just longer prose.

**One working representative candidate is enough for the initial family**. No meaningless `1 / 1` “New Question” control, no empty or deceptive Levels 2/3. If needed, the UI should render candidate count honestly and omit buttons not yet implemented. Keep familiar four-category layout and Good / Needs Work / Bad + notes.

**Pass 1 release gate:** every visible question has correct mathematical givens and a teacher-only answer/solution or an explicitly blocked unresolved original key; all required images load; lesson and skills match; the transfer installs cleanly; Chapter 2/3 preserved. No “we'll check the math later.” Teacher may spot-check this pass *before* expanding variations.

### Pass 2 — Direct Skills **difficulty** design and proof of progression

**This pass applies to `direct` only.** For each approved-in-design family, create **Level 1, Level 2, Level 3 exemplars** grounded in the same supporting skill and evidence job, but with meaningful increasing mathematical demands:

- **Level 1 — accessible entry:** clear/equally spaced/table or basic graph, short calculations and uncomplicated values where appropriate; the student still performs the target skill.
- **Level 2 — substantial application:** negative numbers, non-unit increments, different representation, reverse known/unknown relationship, realistic constraints, more decisions or interpretive work **only when appropriate to that family**.
- **Level 3 — genuine transfer/complexity:** rational/non-integer relationships, less direct givens, multi-representation evidence, a genuine dependent step, or a more complex but still lesson-appropriate case. Do not simply enlarge coefficients, add irrelevant words, or introduce out-of-sequence content.

**Difficulty is mathematical and family-specific**, not a universal integer recipe. For a classification task, higher levels might require distinguishing subtle representation cases rather than larger numbers. For a graph-reading family, difficulty may depend on point selection, scaling, graph window and missing values. For a function family, it may depend on reversed mapping, finite domain restrictions or comparison of representations, **not automatically on calculus-style algebra**.

**Critical rules:**

1. Preserve the **same evidence target** across all three levels; if Level 3 becomes a different skill, create a new family or reject it.
2. Ensure Levels 1–3 are **not the same displayed mathematical question** with new labels. Cross-level duplicate checks are mandatory.
3. If a particular family cannot naturally support three meaningful levels, **do not fake them**. Revisit family boundaries/level design or mark the family for teacher decision; do not populate empty placeholders.
4. During this pass a family may have **only one representative candidate per verified level**. A New Question control should be absent or disabled until a real pool exists.
5. Re-solve/check answers **for each level**; verify source diagrams and answer neutrality before transfer.

### Pass 3 — Direct Skills parallel variation pools (while retaining Levels 1–3)

For each family and level, develop **enough mathematically independent same-level versions to make New Question useful**. Quality governs size; do not clone a universal 12/18/24-per-level count. The past Chapter 2 bank used 12–24 per level depending on structure, but that was a workload choice, not evidence of quality.

Legal variation axes include different: values/signs, input-output sets, known/unknown placement, graph windows/scales, representation instances, function examples, selected points, rates/contexts (when context changes evidence), dependency paths where relevant, true/false and yes/no cases, answer locations and misleading-but-valid distractors.

**Same-level New Question invariant:** `difficulty_selected` must **not** change when a question refreshes. All candidates preserve the family evidence job and comparable mathematical demand. Identity: `family_id + level + variation_index`; a new question needs genuinely different math, not just a renamed item. Recompute all answers, figures and worked steps from the new parameters. Check answer-class balance (positive/negative/zero/undefined, true/false, etc. where applicable) and detect near-duplicates.

### Pass 4 — Review & Preview number-swaps and visual completion

Start from locked originals installed in Pass 1, **not** reconstructed imaginary textbook questions. Add generated versions where mathematically legitimate, with original **always version 1**, unchanged; new versions use the same mathematical structure and problem intent but their own source status, answers and diagram assets.

- No difficulty levels, ever, in Chapter 1 Review & Preview.
- A swappable arithmetic, equation, diamond, table or pattern question may support many variants; each new version has recalculated answer and image/diagram if appropriate.
- A complex graph/geometry/source-dependent question may stay original-only until a faithful replacement diagram and complete verified answer is possible.
- Make **real tile figures** for tile/figure-pattern questions, not long verbal descriptions of what figures supposedly look like.
- For original CPM images: copy exact bytes where possible; use correct relative paths or verified embedded images. Do not consider the image complete merely because a file was packaged; **test browser loading at the actual route**.
- For image-based number swaps: regenerate the corresponding graphical facts and check every count, point, intercept and scale. Do not change the givens while leaving the original diagram.
- For diamond problems, use `Tools/graph_tool.py` **`make_diamond(top, left, right, bottom, filename=...)`**, preserve blank cells and the mathematical top/product and bottom/sum relationship. Do not render a rough CSS diamond or a prose replacement.

### Pass 5 — MC and Extension parallel variations (still no levels)

Keep the number of families tied to evidence sufficiency. Create real parallel variants for all reusable MC and extension families; New Question appears **only if 2+ verified candidates** exist. Preserve teacher-reviewed originals where applicable.

- **MC**: four unique, correctly typeset answers; exactly **one** correct mathematical/interpretive choice. Distractors should expose plausible mathematical misunderstandings, not random values. Recompute alternatives and rationale. Shuffle answer positions *independently per family* and check global A/B/C/D balance **and** local answer-run patterns (Chapter 2's first version accidentally reused the same six-letter sequence in every family).
- **Extensions**: genuine new mathematical relationships/multiple-representation comparisons, novel constraints, reverse reasoning or model transfer; not just standard problems with bigger numbers and “explain.” Must have complete worked solutions. Do not label an extension necessary to earn an A.
- **No difficulty controls** for MC/Extensions.
- Keep test eligibility blocked until approved and validated through Assessment Builder, irrespective of successful technical QA.

### Passes 6+ — **Focused** quality improvement cycles; do not cram everything into one pass

Do **one or two prioritized audits per pass**, fix actual findings, and package a small, reliable transfer. Teacher spot-check after a useful improvement; then choose the next audit from evidence. Recommended audit menu and repeat triggers:

| Independent pass | Check | Repair & recheck |
|---|---|---|
| **Skills / lesson alignment** | Every family and candidate evidences its assigned skill; first-use lesson is appropriate; no family is present only to fill columns | Rework bad questions and **re-run coverage matrix** after archiving |
| **Bad question / answer-neutrality** | Ambiguous directions, invalid givens, accidental answer cues, unnecessary narrative, hidden solution revealed by diagram/caption/alt | Rewrite the question, then **re-solve and re-render** |
| **Redundancy / variety** | Same mathematical action repeated across neighboring lessons/families; exact and near-duplicate math across levels/versions | Collapse duplicates or replace with different authentic evidence; re-run skill coverage |
| **Direct Skills difficulty** | L1/L2/L3 genuinely progress; same-level variants have comparable load | Repair levels and recheck all their variants |
| **MathJax / typography** | Broken TeX, unbalanced `\\(`/`\\)` / `\\[`/`\\]`, `1x`, signs, fractions, cube roots, function notation, tables, overflow | Fix formatting; render actual MathJax in browser and read it |
| **Graph/visual** | Canonical graph style, scales/coordinates/points/diagrams, true tile figures, grayscale and print legibility, all image links | Regenerate via canonical tool; independent numerical check and visual inspection |
| **Solution/key/distractor** | Every answer recomputed independently from displayed givens; MC exactly one correct; all steps valid, units/conditions correct | Correct questions/keys/options and **re-run MC validation** |
| **Student UX / controls** | Four categories; proper visibility; New Question works and loops; direct levels stable; no levels elsewhere; Good/Needs Work/Bad and notes work; print | Browser smoke + teacher review persistence checks; do not reset namespaces |
| **Final release gate** | Actual installed source hashes, assets, chapter isolation, JS/JSON syntax, transfer manifest, safe paths | Package/rebase after any new installed changes; do not bypass hash guard |

A useful cadence is **Pass 1 → teacher spot-check → one focused pass → another focused pass → teacher spot-check → more passes only if needed**. The workflow should improve the actual bank, not produce repeated planning-only transfers.

---

## 5. When and how answers/solutions are verified

**Answer to the explicit question: _We check answers from the first pass, and again in a dedicated independent QA pass._** Correctness is a continuous requirement, not a late optional stage.

### Mandatory checks whenever a question is authored or modified

1. **Write or generate the actual fully specified student prompt and all required data/graphics.** A placeholder template is not a finished question.
2. **Solve from the displayed student givens**, not merely by replaying the generator's answer formula. For equation problems: substitute the candidate solution, check equality/restrictions. For functions: independently evaluate or reverse the rule as asked. For pattern/graph tasks: recompute counts, slopes, intercepts, coordinates, endpoints and scales against the visible figure.
3. **Verify the answer field and each worked step**, including sign, units, correct algebra, valid domain assumptions, labels and rounding rules. Do not silently change the student question to make a wrong stored answer appear correct.
4. For **MC**, calculate the truth of **every** option using an independent checker; confirm exactly one correct answer in the printed order and that the stored key maps to it. Assess distractor plausibility and answer-letter distribution.
5. For **multiple answers or open-ended extensions**, identify an answer set or grading criteria and acceptable equivalent forms; a single exemplar is not always the only correct solution.
6. For **original CPM Review & Preview**, *source transcription fidelity and answer certainty are separate checks*. The original may lack an accessible verified key; retain source exactly, mark key unresolved and block test/Portfolio use rather than inventing a plausible answer. Any number swap needs a verified new key.
7. Check that no answer/solution is leaked in `student_html`, SVG paths/labels, figure captions, alt text, titles or sample table cells where the student was supposed to construct them.
8. Render MathJax/diagrams and spot-inspect visually; structural existence is not proof of a correct picture.

### Why an additional dedicated independent answer pass is still necessary

A generation script often uses the **same mistaken assumptions** to author its prompt and answer. Verifying with that same code is not genuinely independent. A later checker should parse final prompts/data and recompute independently (symbolic algebra or a separately written evaluator, geometric invariants, option recomputation, consistency cases) and flag unusual situations for human review.

Run this pass **after** creating base questions, **after** generating variants and **again after any repair** to equations/figures/answer choices. The final QA report must distinguish `generated math checked`, `independently re-solved`, `MathJax parsed`, `sample browser rendered`, `all images resolved`, `teacher approved`, and `installed-Mac smoke tested`. Never roll all into a vague “QA passed.”

**Question-specific blockers** should be visible: missing source, unknown correct answer, ambiguous prompt, more than one MC answer, inaccurate diagram, lesson out-of-scope, answer exposed to student, or incomplete mathematical validation. Block questionable families; don't hide them without documenting the coverage consequence.

---

## 6. Graph Tool, diagrams and mathematical rendering contract

### Canonical tooling

- Read `memories/Tools/MANIFEST.json` and **`memories/Tools/graph_tool.py`** from the available current source. An earlier inspection verified the tool provides:
  - `make_window_graph(ax, functions, xmin, xmax, ymin, ymax, title='', xlabel='', ylabel='')`: canonical Cartesian window; passing an **empty `functions` list** creates a truly blank, answer-neutral construction grid.
  - `make_standard_graph(ax, functions, title='')`, `make_context_graph(ax, functions, xmin, xmax, ymin, ymax, xlabel='x', ylabel='y', title='')`: standard and contextual graph styles.
  - `make_diamond(top, left, right, bottom, filename='diamond.png')`: canonical CPM diamond figure; `None`/empty cells remain blank.
  - `make_rectangle_model(...)`, `make_number_line(...)`, `make_number_line_blank(...)`, `make_piecewise_graph(...)`, plus other registered chart/model functions.
  - `save_graph(fig, filename)` writes a real image to the tool's configured `OUTPUT_DIR`; **verify the produced image file and its final packaged location**.
- For Cartesian graph questions, **use the tool**, rather than hand-drawing unregistered HTML/CSS/SVG axes. Preserve the classroom worksheet/graph style: correct labels, scale, grid density, points, line shape, arrowheads when appropriate and readable print sizing.
- Legitimate supplied-graph tasks must show the required graph information; legitimate *graph-this-equation* tasks must provide a **blank** graph, not the solution line or vertex.
- For tile/figure sequences, use real **unit-square pattern diagrams**, with an actual coherent geometry across stages, label Figure 1/2/3, count tiles independently and match the stated growth. A numerical list described as “a diagram” is not an acceptable substitute.
- For mappings, function machines, area models, number lines and geometric diagrams, use the appropriate canonical/shared representation. Where no specialized tool exists, deterministic accurate SVG or semantic HTML may be appropriate **without bypassing the Cartesian Graph Tool requirement**.
- Embed images self-contained **or** include all referenced assets in the transfer with resolvable application-relative URLs. Verify image loading at the real bank page URL, not only that the ZIP contains a PNG.

### Graph/diagram QA requirements (every affected pass)

1. **Mathematical validity:** plotted points satisfy the equation; line slope and intercept are exact; axes match coordinates; endpoints/open circles are correct; tile stage counts match rules; blank construction surfaces contain no solution.
2. **Visual validity:** legible labels, compact enough for narrow lesson columns, print-safe black/white contrast, no clipping, overprinting or misleading arrowheads; MathJax renders alongside graph.
3. **Student answer neutrality:** no answer in alt text, captions, SVG labels, colored helper line, already-filled generic-rectangle cell or selected graph unless the job is interpretation of a supplied object.
4. **Swappable consistency:** every new version regenerates data, answer, diagram and worked solution in sync.
5. **Source fidelity:** never call reconstructed teacher-generated figures “exact original CPM” if they are not; if recreating an unavailable source image, preserve its mathematics and document reconstruction honestly.

### MathJax standards

Use the installed MathJax configuration (`\(...\)` inline and `\[...\]` display, as represented in source strings). Check commands supported by the installed renderer, especially `\\frac`, signs, radicals, exponents, function notation, interval notation, inequalities and coordinate pairs. A JSON backslash escaping failure can silently alter a mathematical string; parse rendered markup in an actual browser and inspect sample difficulty/variation changes. Existing Python/math validation utilities do **not** replace visual browser checks.

---

## 7. Variation and difficulty decision table — remember what the teacher actually chose

| Design choice | Correct Chapter 1 policy |
|---|---|
| Question family count | Whatever distinctly assesses the real supporting skills; **no preset quota** |
| First substantive pass | Four complete categories with **one verified question per family**, before multiplying variants |
| Direct Skills levels | **Yes**, separate later pass; three genuinely different mathematical levels where the family supports them |
| Direct Skills New Question | Later pass, **within selected level only** |
| Review & Preview levels | **No** |
| Review & Preview original | Original CPM **exact** as version 1; original figures/images faithfully preserved |
| Review & Preview variations | Number-swap same mathematical task where valid; separate generated status; diagram and answer regenerated |
| Summative MC levels | **No**, summative tests only; four unique options/one correct |
| Extensions levels | **No**, optional and genuinely deeper, not a letter-grade requirement |
| MC and Extensions New Question | Later pass, only with at least two actually different, checked versions |
| Graphs/diamonds/tiles | Actual mathematical visuals; Graph Tool for Cartesian/diamond, coherent tile diagrams |
| Solution correctness | **Every initial question**; independently revisit on dedicated QA pass and after edits |
| Approval | Teacher review first; fresh generated variants remain assessment-blocked |
| Transfer style | **One guarded Local Only GitHub Transfer ZIP** per useful pass; no GitHub writes |

---

## 8. UI, approval, source and record-integrity requirements

- Preserve **four category panels** and original CPM lesson-column navigation. The current `bank.js`/`section.html` serve shared chapter views; avoid creating a Chapter 1-only different UI unless a verified needed change is proven safe for Chapters 2/3.
- Direct Skills show 1/2/3 controls **only after** the distinct level prompts actually exist. Other categories never show levels. New Question appears only when more than one verified candidate is available. Candidate counters reflect actual pool size.
- Preserve **Good / Needs Work / Bad** teacher review controls and freeform notes. Never reset existing Chapter 2/3 localStorage namespaces or private review records. Prefer family-ID stability where content truly continues; do not silently assign old teacher approval to a wholly redesigned task sharing an old ID.
- Answers/worked solutions are shown in the teacher section (`Answer + worked solution`) and stored in separate candidate fields, not copied into student-facing diagrams.
- Distinguish `source_basis.source_type` for actual CPM original, adapted/numerically swappable CPM-like version, and teacher-authored new material. Retain original exact HTML in a locked `source_original_html`/archive field where supported. `question_structure_id` describes an actual action, not the textbook publisher or lesson number.
- Keep teacher-draft and `assessment_eligible=false` statuses until explicit teacher approval plus downstream Builder verification; do not update Portfolio or student data.
- When restructuring Chapter 1, retain archived historical records/provenance and existing review references if possible, but the **visible** new bank should be a fresh skill-driven set. If a true family must be replaced, use clear `superseded_by`/revision metadata rather than destructive silent deletion.

---

## 9. GitHub Transfer ZIP contract and release preflight

All repository-file edits are packaged as one **GitHub Transfer ZIP** with `TRANSFER_MANIFEST.json` using the user's **current `github_transfer` contract**. Existing recent transfers used schema 3 and this shape:

```json
{
  "schema_version": 3,
  "package_type": "curriculum_transfer",
  "package_id": "unique-lowercase-id",
  "files": [
    {
      "action": "replace",
      "root": "cpm_tools",
      "path": "banks/data/CH01.json",
      "source": "payload/cpm_tools/banks/data/CH01.json",
      "expected_existing_sha256": "ACTUAL_SHA256_OF_CURRENT_INSTALLED_FILE"
    },
    {
      "action": "replace",
      "root": "cpm_tools",
      "path": "banks/section.html",
      "source": "payload/cpm_tools/banks/section.html",
      "expected_existing_sha256": "ACTUAL_SHA256_OF_CURRENT_INSTALLED_FILE"
    }
  ]
}
```

Verify the **current** transfer contract before packaging; do not assume example contents are exhaustive. Root `cpm_tools` means `GitHub/CPM_Tools` in the installed Local Only tool; `memories` means `GitHub/memories`. Do not guess or create ZIP entries that could escape those allowed roots.

### Preflight checklist for each transfer

1. Read current Drive mirror file bytes, installed transfer logs and timestamps; compute **real current SHA-256** for every `replace` target. New transfers must rebase if another transfer was installed after the working snapshot. **Do not ask the user to bypass a hash mismatch.**
2. Validate JSON schema, unique `family_id`/`variant_id`, real lesson and skill references, active/hidden category counts, all required answers, no duplicate candidate IDs and no accidental new assessment eligibility.
3. Where `section.html` embeds Chapter 1/2/3 JSON: update only Chapter 1's payload. Verify external `CH01.json` and embedded Chapter 1 data match, and embedded **Chapter 2 and Chapter 3 are byte-identical** before vs after. Preserve unrelated CSS/JS and teacher-review code.
4. Check complete image/asset references and MathJax in **actual browser** including narrow column and teacher/print views. Browser samples do not certify every question; report coverage honestly.
5. Run question hygiene, semantic math, per-family candidate and source-original fidelity checks; record checks actually run and unresolved findings. Keep teacher review controls live.
6. Verify ZIP integrity, manifest source paths, allowed roots, action policies, current precondition hashes and simulated/local installer compatibility. Do not rewrite or remove existing user files not included in the target scope.
7. Transfer output should be the **single authoritative ZIP**; link it at the **top and bottom** of final response. Explain changes and QA between links, compactly. No individual repository component cards or alternative required downloads.
8. User's install: download ZIP into `GitHub/_curriculum_transfers/downloads/` **unopened**, run `memories/Tools/curriculum_transfer/Apply Curriculum Transfers - Local Only.command`, inspect log. No Git commits/push. User may later sync manually via GitHub Desktop.

**Chapter 2 cautionary event:** a Pass 6 ZIP failed its SHA-256 guard because Pass 5 was already installed; the correct fix was rebasing manifest/replacement against current Pass 5. The guard worked as designed.

---

## 10. Known Chapter 2 mistakes to prevent in Chapter 1

| Observed failure in the Chapter 2 cycle | Preventive Chapter 1 acceptance test |
|---|---|
| One visible slope family remained in Lesson 2.1.2 despite several legitimate evidence forms | Show actual **visible family + evidence-job coverage per lesson/skill** before generating many variants. Don't hide legitimate coverage just to reduce repetition. |
| Repeated task called a new skill by appending “explain/justify/diagnose” | Audit actual **student mathematical action**, not wording. |
| Thousands of numeric swaps gave false sense of family diversity | Establish distinct evidence families first; then add legitimate same-family variations. |
| Artificial quotas for categories and difficulty | Use skill/lesson-driven content; add direct L1–L3 only when genuine; leave others level-free. |
| Review & Preview lessons blank or copied source figures broken | Find actual textbook originals, **resolve every image in the installed bank**, preserve verbatim source wording. |
| Tile-growth question described a diagram instead of showing one | Visual representation is mandatory where the task says to read/copy/interpret a figure; use real coherent tiles. |
| MC answer-letter patterns identical across unrelated families | Test **family-local and global** answer-position patterns, distractors and key mapping. |
| Review & Preview and MC “New Question” displayed at `1/1` | Hide nonworking controls until real candidate pools exist. |
| Solutions generated from the same mistaken rule as question | Independent re-solve from final student prompt; separate answer-verification audit after changes. |
| Packaging checked included images, but some were broken in application | Browser asset-path checks, actual image decoding and rendered visual inspection. |
| ZIP transfer failed after a prior pass had been installed | Verify actual latest source bytes before building manifest; rebase; use source-hash guard. |
| “QA passed” meant syntax only | Publish a per-gate QA summary specifying mathematical, MathJax, browser, visual, install and teacher-review status independently. |

---

## 11. Current reference status as verified on November 15 (not a future hash promise)

The latest **Pass 13** Chapter 2 transfer, `Algebra1_Chapter2_MC_Extensions_Quality_MathJax_Redundancy_Pass13_20261115_GITHUB_TRANSFER.zip`, was installed: the Google Drive mirror showed `CH02.json` and `section.html` sizes matching Pass 13's payload after the timestamp update. On entry to the next chat, recompute current hashes rather than assuming the installation stays fixed.

**Chapter 2 visible counts in the Pass 13 payload** (reference examples, **not Chapter 1 quotas**):

| Category | Visible families | Variants | Notes |
|---|---:|---:|---|
| Direct Skills | 76 | 3,648 | Three levels; broad representations |
| Original CPM Review & Preview | 50 | 391 | Originals + verified same-task swaps; no levels |
| Summative MC | 27 | 189 | 7 versions/family; no levels; test only |
| Extensions | 27 | 189 | 7 versions/family; no levels |

Pass 13's recorded QA included: 189/189 MC answer-choice verification, 505 distinct MathJax expression parses, 54/54 New Question browser interaction checks, one redundant 2.3.2 task replaced, and answer-letter positions A=47, B=47, C=47, D=48. These are **specific technical checks**, not blanket teacher approval of Chapter 2 or proof that all mathematical diagrams across every category are perfect.

**Chapter 1 prior baseline:** the Pass 13 shared page contained an old `CH01` snapshot with **96 records**, 2 section goals, 9 supporting skills and 8 lessons. This old bank's counts and categories are not to be copied. Preserve its history, but **design a new bank from the goals**.

---

## 12. How to report each pass without frustrating the teacher

For each transfer, provide a concise change summary with:

- **What changed** by category, which lesson/skill evidence improved, and what was deliberately left unchanged.
- **What counts actually mean:** number of families (different mathematical actions) vs number of candidates (parallel problems), not a boast of inflated volume.
- **What was verified:** exact check scope/results; explicitly separate independently recomputed answers, MathJax parse, browser sample, all image loading, teacher approval and actual Mac installation.
- **What still needs a later pass** (e.g., Direct Skills levels not yet generated, number swaps pending, missing verified CPM key), without claiming those controls or content already exist.
- **What to spot-check next**: 2–4 specific families or lessons, not a demand for the teacher to review everything at once.
- **One install instruction**: Apply Curriculum Transfers — Local Only; never tell the user to reinstall previous passes unless a specific cumulative transfer was built and tested.

Do not begin each message with an apology, a fresh strategy that contradicts the last agreement, or a rehash of the same Chapter 2 failure. Execute the committed recipe, report measurable QA and deliver one ZIP.

---

## 13. Definition of a successful Chapter 1 first-pass transfer

Before handing the teacher the **first** Chapter 1 transfer, all of these must be true:

- [ ] Current mirror and authority files actually inspected; installed hashes recorded.
- [ ] Exact Chapter 1 goals, nine skills and eight lessons checked against Assessment Plan and CPM sources.
- [ ] Evidence matrix exists and **every essential skill** has appropriate planned visible coverage; no quota-driven fillers.
- [ ] Four categories all present where appropriate; each visible family has a **real mathematical task**.
- [ ] Every new question is **solved and mathematically checked**; MC has four distinct options and exactly one correct answer; any original-only CPM key uncertainty is explicit and blocked.
- [ ] Original CPM Review & Preview source text is verbatim, diagrams faithful and visibly loaded; no invented source claims.
- [ ] Graph Tool and tile/figure diagrams used as appropriate; graph construction surfaces do not leak solutions.
- [ ] No fake difficulty controls or fake New Question buttons before those pools exist.
- [ ] Teacher review controls and notes still work; all new candidates blocked from assessment generation.
- [ ] CH02 and CH03 remain unchanged, including their embedded snapshots; no student/Portfolio changes.
- [ ] JSON + JS + MathJax + image + targeted browser + transfer precondition checks passed (with honest scope).
- [ ] One downloadable Local Only **GitHub Transfer ZIP** delivered, with top and bottom link.

**Subsequent passes:** add *real* Direct Skills difficulty progression, then genuine parallel variants; Review & Preview swaps/visuals; MC and Extensions variants; and focused one- or two-topic quality passes with independent answer audits repeated after changes. The teacher spot-checks after useful increments, not after endless near-identical patches.

---

## 14. Short suggested opening message for the next chat

> We are rebuilding Algebra 1 **Chapter 1** from scratch at the question-design level. Read and use `Algebra1_Chapter1_Fresh_Bank_Build_Handoff_20261115.md` as the working contract. Start with the actual Section 1.1 and 1.2 learning goals, nine supporting skills, eight CPM lessons, and canonical Question Structures sources. Build an evidence matrix first. Then deliver a **four-category first pass** of accurate representative questions, exact original CPM Review & Preview with working figures, and teacher-review-ready Summative MC and Extensions. **Do not use the existing Chapter 1 bank as a template, do not force counts, and do not yet generate difficulty/variation pools.** Check every question's math and answer immediately, then add levels/versions and targeted independent QA in subsequent passes. Preserve CH02/CH03 and return only a verified GitHub Transfer ZIP. No unnecessary questions or status-only handoff.

---

**Final rule:** **First decide what mathematical evidence students must demonstrate; then decide which question structures best reveal it; only then write and vary questions.** Question counts, version counts, and even family boundaries follow that decision — never the other way around.
