# CPM Tools — Reusable Chapter Question-Bank Build Recipe

**Authority:** teacher-approved working recipe, 2026-11-15.  
**Scope:** Algebra 1 chapter banks first; reusable for other CPM courses after checking their exact course mapping.  
**Repository location:** `memories/_question_structure/recipes/ALG1_CHAPTER_BANK_BUILD_RECIPE.md`  
**Current pilot:** Algebra 1, Chapter 4 — Systems of Equations.

## Exact new-chat trigger and required behavior

> **Read bank memory and start Alg 1 Chapter 4.**

Treat minor capitalization/spelling changes as equivalent. **This is an instruction to do the work now, not to explain a proposed workflow or ask the teacher to restate it.**

1. Use connected Google Drive mirror to find the **current** `memories/CHECK_MEMORY.md`, then `_question_structure/README_FIRST.md`, this recipe, and any relevant existing chapter/category recipes. If Drive mirror is unavailable, use accessible verified repository files; say what could not be verified. Do not assume a historic transfer ZIP is installed.
2. Read `CPM_Tools/PROJECT_START_HERE.md`, `CPM_Tools/docs/SHARED_SYSTEM_CONTRACT.md`, the current `CPM_Tools/data/algebra1_assessment_plans.json`, the current bank files/manifest and teacher-review mechanics, and source lesson files and diagrams **before authoring new questions**. Confirm the current source checksum and actual installed representation. Never ask the teacher to upload files already accessible in the mirror.
3. Confirm Chapter 4 planning is **teacher-verified for the three learning goals and 13 supporting skills only** (2026-11-15). This **does not** approve new question families or release them to Assessment Builder. Use actual current plan data if a newer revision changes this.
4. **Execute Chapter 4 Pass 1 for all eight lesson columns in the same task.** Inspect source, identify real skills, build and solve representative questions, install new bank content safely, perform Pass 1 QA, and deliver **one** Curriculum Transfer — Local Only / GitHub Transfer ZIP. Do not stop at a plan or at a handoff unless current source is genuinely unavailable.
5. Report what is actually complete, source limitations, any below-target counts and why. Do not claim teacher approval, local installation, or Mac verification without evidence.

**After Pass 1:** When the teacher says **"continue"**, **"next pass"**, or **"pass 2"** in this workflow, use the installed/current bank and execute the next planned pass. Continue with Pass 3, Pass 4, Pass 5 in order on subsequent requests; do not restart Pass 1 or regenerate previously approved source. A specific teacher instruction overrides the default sequence. The assistant owns source lookup, development, independent QA, and packaging; the teacher reviews/installs and alone grants approval.

## Course scope — Chapter 4 pilot

- Course: CPM **Core Connections Algebra 1**, Chapter 4 **Systems of Equations**.
- Teacher-verified section goals: **4.1**, **4.2**, **4.3**. Use the actual text and skills from the current Assessment Plans JSON rather than retyping, reauthoring or enlarging them.
- Eight CPM lesson columns: `4.1.1`, `4.1.2`, `4.2.1`, `4.2.2`, `4.2.3`, `4.2.4`, `4.2.5`, `4.3.1`.
- A **column means a lesson's four bank categories**, *not* an entire chapter goal or each skill inside the assessment plan.
- The exact original CPM Review & Preview problems are already coded/extracted elsewhere. **Find and reuse them**; do not create substitute "CPM" problems or repeat an extract without checking source, diagrams and attribution. Locate existing canonical bank/source cards before rebuilding any R&P extraction.
- Build from verified lesson material, the 4.1–4.3 goal-to-skill mapping, existing question-family design contracts and the course-specific source diagrams. Do not import Algebra 2 or another chapter's topic simply to fill a cell.

## Overall sequence

| Pass | What changes | Deliberately excluded |
| --- | --- | --- |
| **1 — Foundation** | Representative Direct Skills, authentic original Review & Preview, MC and Extensions for all columns; correct answers/source alignment; bank shell | Difficulty levels and New Question pools |
| **2 — Direct difficulty** | Add genuinely distinct Levels 1, 2 and 3 to each valid Direct Skills family | Bulk numeric alternatives and New Question variations |
| **3 — Parallel variants** | Add quality-controlled New Question alternatives to appropriate families, within fixed Direct level; original R&P stays first | Invented quotas, unrelated replacements |
| **4 — Deep quality audit and repair** | Duplicates, independent math, skill fit, distractors, solutions, MathJax, diagram fidelity and answer leakage | New families solely to inflate counts |
| **5 — Classroom acceptance** | Browser/screen/print interaction and release-safety tests; targeted fixes; final teacher review package | Auto-approval or automatic assessment release |

### Pass 1 — Build the foundation (default start)

For **each** of the eight lesson columns, start with this four-group layout:

| Group | Target per lesson | First-pass requirement |
| --- | ---: | --- |
| **Direct Skills** | **3** | Three **different mathematical evidence jobs**, one correct question per family, linked to the verified section skill(s). No difficulty selector. |
| **CPM Review & Preview** | **All authentic existing source problems for the lesson** | Reuse exact source wording, numbered subparts, tables, images and diagrams already coded. One original question per existing problem/family; no new variants or level control. |
| **Multiple Choice** | **3** | Three distinct evidence jobs/questions (not three restatements of the same skill); each with four distinct choices and plausible misconception-based distractors. |
| **Extensions** | **3** | Three distinct, genuinely deeper *chapter-aligned* tasks (e.g., reverse reasoning, nonroutine comparison, modeling/strategy, or a linked representation), each with a verifiable answer/solution. Not simply "justify" or "explain" appended to routine practice. |

**Planning target: 24 Direct + 24 MC + 24 Extensions = 72 authored representative question families**, **plus** the original CPM Review & Preview families. This is **not a hard quota**: if only two authentic distinct skills exist in a lesson/category, create two strong families and report the gap instead of fabricating a third. Do not count the same concept as a new family just because the representation or directions have been paraphrased.

Pass 1 workflow:

1. Make a lesson-by-lesson **evidence matrix**: source CPM lesson, verified section LG and skill ID, three proposed Direct evidence jobs, three distinct MC evidence jobs, three Extension evidence jobs, and source R&P problem IDs. Check for overlap before writing.
2. For each family define stable ID, student action, representation mode, response mode, invariant evidence job, source/provenance and teacher-review status. Reuse compatible canonical question-family definitions rather than inventing a second shared registry; custom local family structures must be explicit.
3. Write one representative question per family, complete answer and a genuinely worked solution. Verify the math independently against the **displayed** prompt, including negative signs, units, constraints, tables, graph points, plotted scales and distractor truth values. No answer-revealing directions, alt text, image titles, SVG text or styles.
4. For Review & Preview, preserve original CPM question **exactly**, including subparts and source figures. Reuse its existing coded family/ID and assets where available. Do not reduce a six-part original to a one-part substitute. If a source problem cannot be recovered, mark the gap and keep that family out of teacher-reviewed/bank-ready counts. Never label fabricated material as an original.
5. Render MathJax and images. Use canonical `memories/Tools/graph_tool.py` or the existing registered course visual tool for graphs and diamond problems; verify tile counts, axes, labels, endpoints and all numeric parameters. No fake graphs or text in place of a required diagram.
6. Install only the required Chapter 4 bank additions and routing; preserve previous chapters, existing family IDs, teacher review records, original source and offline fallback data. Keep all new families `PENDING_TEACHER_REVIEW`, `assessment_eligible:false`, and excluded from automatic/student-facing summative generation until separate teacher approval.
7. Check bank load in browser and sample all four category formats, then return a single verified Local Only transfer. Include an **internal QA record in the transfer** if helpful, not multiple standalone download cards.

**Pass 1 exit gate:** all eight lesson columns accessible, category counts and any justified shortages reported, R&P source fidelity established, all authored answers/misconception choices mathematically checked, diagrams load, no bad TeX, no regressions to Ch 1–3, and teacher approval still pending. No New Question or difficulty controls should show before those pools exist.

### Pass 2 — Add difficulty to Direct Skills

- For each Direct family keep its original representative question as the Level 1 exemplar when suitable; author distinct Level 2 and Level 3 questions **within the same stable family**, with independently verified answers.
- **Level 1:** straightforward recognition/computation with minimal clutter. **Level 2:** meaningful intermediate structure (signed values, less cueing, non-obvious substitution, linked data). **Level 3:** structurally harder or transfer within the same evidence job (dependent steps, choosing information, reverse direction, non-obvious constraints). Do **not** use larger arbitrary numbers or extra decorative wording as the sole difference.
- Difficulty is for Direct Skills only unless the teacher later requests otherwise. Review & Preview has **no level selector**.
- Retain IDs, prior teacher-review notes and source original candidates; do not replace the whole bank or destroy evidence history.
- Exit: three real levels in each eligible Direct family, clear rationale, math and representation verified, no false cross-level duplicate prompts.

### Pass 3 — Add New Question variations

- Only now populate bounded question alternatives per family; **quality beats a target of 12**. A family with only 3–5 sound alternatives is better than a 12-question pool of answer-changing near duplicates.
- Direct Skills: keep the selected Level 1/2/3 **fixed** while New Question cycles **within** that level. Maintain meaningful level distinctions.
- R&P: the *original CPM source question is always version 1*. Subsequent versions preserve the **same task structure, subpart count, stimulus type and conceptual work**. Prefer valid synchronized number swaps for routine spiral practice; regenerate images/diagrams and recalculated answers whenever givens change. Keep source-only where safe alternatives cannot be made. R&P always has a single pool and no difficulty control.
- MC: preserve four distinct options, exactly one intended correct answer, plausible misconceptions and varied correct-answer position. Do not generate contradictory givens.
- Extensions: meaningful variation in reasoning/modeling/representation, not only a cosmetic "justify". No out-of-grade inclusion–exclusion or other unrelated advanced content to force quota.
- Verify buttons, displayed count (including nonconsecutive variation indices), complete cycle, matching answer/solution, keyboard use, and offline fallback payload. Keep new variants teacher-pending.

### Pass 4 — Deep audit (and fix what it finds)

Review **all** families and all variants, not only newly added ones. Use independent calculation where practical; sampled visual verification does not substitute for full structural/math checks.

- **Skill and difficulty:** no artificial explain/justify skill families; no exact or near-duplicate evidence jobs; real coverage of verified LG skills; L1/L2/L3 order credible.
- **Mathematics:** independently check displayed formulas against numeric keys, worked steps, answer constraints, systems solutions and graph/table values; handle zero coefficients, negatives, repeated roots, invalid assumptions and no/infinitely many solutions where appropriate. Check reverse wording such as "adds -3" or "adds 3 from input"; remove literal placeholder tokens (`{j}`), `1x`/`0x` artifacts and malformed `x²x` expressions.
- **Variation:** detect exact prompt duplicates within and across levels/families, parameter constants that never vary, repeated answers masquerading as fresh reasoning, equivalent repeated situations, and reductions in original multi-part structure. Do not fix skill duplication with superficial number swapping.
- **MC:** four truly different answer choices, one justified correct choice, no contradictory story conditions, distractors grounded in real student mistakes and no answer-position bias.
- **Visual and TeX:** render every distinct MathJax expression, check broken syntax/Unicode signs, SVG validation, embedded raster decoding, image aspect and mapping labels/tile coordinates, clipping and no hidden solution in alt text or visually exposed markup. Graph coordinates/scale and textual key must agree.
- **Safety/integration:** unchanged original CPM Review & Preview source and metadata, unchanged Chapter 1–3 and private review state; assessment blocks still active; no hidden old bank in standalone/offline fallback.

If unresolved material errors remain, disclose them explicitly and keep affected families blocked. A neat JSON structure alone is not proof of mathematical correctness.

### Pass 5 — Classroom readiness and exit

- Open the real installed-style browser view at desktop and narrow lesson-column widths. Test category switching, R&P source question, multi-part layout, graphs/MathJax, answer reveal, Next/New Question, difficulty persistence, original/variant cycling and printing/PDF/duplex where supported.
- Test source-bank JSON and embedded/offline fallback, no regressions in neighboring chapters, and teacher-review controls. Inspect print page breaks, font sizing, image loading and student-answer leakage.
- Recheck all current variant IDs and family IDs stable; no mandatory 12-count; ensure every family remains teacher-pending until explicit per-family/bank approval.
- Report final checks and known limitations accurately (including whether this was only browser automation vs the teacher's actual Mac install). **Do not silently mark a bank approved** based solely on automated QA.

## Fixed cross-pass boundaries

1. **Teacher controls approvals.** Verified Chapter 4 learning goals do not imply approved Chapter 4 bank families, variants, assessment eligibility or Portfolio updates. Chapter 1–3 curriculum approval is not the same as bank approval.
2. **Original CPM content is source-preserved.** Never rewrite exact originals, guess original diagrams, or call new teacher-authored content CPM source. Respect image/figure copyrights and the existing local/extracted assets.
3. **Existing work is additive and stable.** Never wipe private teacher reviews, IDs, prior chapters, saved work, or local Portfolio. No automatic GitHub writes, commits, pushes, pulls or sync. Read GitHub and Google Drive mirror as needed.
4. **Delivery is one authoritative ZIP only.** Use current `memories/Tools/CURRICULUM_TRANSFER_CONTRACT.txt` (schema 3) with `TRANSFER_MANIFEST.json` and approved `payload/<root>/...` paths, content hashes and narrow replacements/creates. The teacher applies **Curriculum Transfer — Local Only**, handles GitHub Desktop manually, and checks the Mac app. For Curriculum Build requests never expose separate repository files as second deliverables. Put the ZIP link at both top and bottom of the response.
5. **Use the latest source, not stale history.** Verify current paths/sha and transfer logs before a patch. If the already-installed bank differs from a previous ZIP, rebase content rather than overwrite it. Do not ask to reupload accessible mirror files.
6. **Stop when done.** Five passes are a planned sequence, not justification for endless cosmetic edits. Address defects with targeted patches; keep the final bank locked for teacher review.

## Quick readiness checklist for new chat

- [ ] Read actual memory entrypoints and **this recipe**.
- [ ] Resolve source CPM Tools install and exact current assessment plan/approved Ch 4 goals.
- [ ] List all eight lesson columns and original CPM Review & Preview source problems.
- [ ] Make per-lesson 3/3/3 evidence matrix, flag real shortfalls.
- [ ] Complete requested pass with independently checked answers and real visuals.
- [ ] Preserve previous chapters, stable IDs and teacher approval gates.
- [ ] Validate source hashes, browser interaction where appropriate, manifest and ZIP.
- [ ] Return **one** GitHub/Curriculum Transfer ZIP, top and bottom, and state what to do next.
