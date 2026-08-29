BUILD SUMMATIVE — PILOT WORKING PM v0.1
=========================================
STATUS: PILOT / WORKING — test and revise from real jobs.

CANONICAL AUTHORITY / GITHUB SNAPSHOT — HARD RULE
=================================================
GitHub is the canonical source of truth. At the start of each job:
1. Resolve the current commit of the canonical system repository once.
2. Pin that commit for the entire job; do not mix files from later commits.
3. Read `_Curriculum_Philosophy_PM.zip` FIRST from that pinned snapshot.
4. Read `_question_structure.zip` when the job authors, varies, audits, or repairs questions.
5. Read the current course Framework from the same pinned snapshot.
6. Read this PM from the same pinned snapshot.
7. Resolve any required Bank, Bank Map, CSS, tools, templates, or course-repository files from the declared canonical repository/commit for the job.
8. If a required canonical authority is missing, duplicated under conflicting names, or ambiguous, FAIL CLOSED. Do not substitute an older upload, stale chat copy, remembered version, or similarly named file.

Normal authority order by domain:
  Curriculum Philosophy -> Question Structure -> Course Framework -> PM -> Tool/CSS/template
The exact current Unit Assessment Plan embedded/identified by the Framework is authoritative for the course/unit terminology and learning/evidence architecture.
A direct teacher instruction for the current artifact may intentionally override the normal default locally. That does not automatically change the system-wide rule or upstream Bank.

PM BOUNDARY
===========
This PM owns procedure: what to fetch, validate, select, assemble, audit, and output. It does not restate a competing Philosophy, Framework, Question Structure catalog, or renderer/CSS specification.
Finished classroom artifacts may improve, rewrite, replace, add, or remove Bank-sourced wording when that makes the declared artifact better. Preserve lightweight provenance when practical. Local artifact edits do not automatically update the Bank.
Each job declares replacement/output scope. Do not alter unrelated artifacts outside that scope. Return the smallest coherent deployable result appropriate to the declared scope.


PURPOSE
Build secure Summative assessment form(s) from the exact Assessment Plan/Framework blueprint, using the Bank as structured source/provenance and `_question_structure.zip` for appropriate authoring/variation.

PROCEDURE
1. Resolve the course-specific form count, response profile, target distribution, security relationship between forms, scoring, shell/CSS, and answer-sheet requirements from the current Framework.
2. Preserve blueprint/mapping. Author or adapt finished questions as needed for assessment quality and secure independence; local artifact improvements do not automatically mutate the Bank.
3. Do not establish security by changing only nouns, numbers, sentence order, answer-choice order, or generic framing. Follow the current Framework's form-family architecture.
4. Build selected-response distractors from the exact misconception/error for that item. Do not reuse generic distractor bags across unrelated families.
5. Supply every required representation and verify that its evidence matches the prompt/key.
6. Render the approved Summative shell including the current course answer-sheet/bubble-page contract.
7. LAST CONTENT STEP BEFORE FINAL RENDER/PACKAGING: run the canonical `Tools/scramble_selected_response.py` on a staged copy when the Framework requires choice balancing. The canonical Bank need not be permanently mutated for display-order scrambling.
8. The scrambler must recognize current canonical SR signals even when `item_type` is absent: Summative routing + non-empty choices + `question_design.response_mode == selected_response` is sufficient. Under a strict mode, a no-op is a failure when Summative records with choices exist but zero SR records were recognized.
9. After scrambling, verify rendered choice order/key synchronization and required answer-position balance, then run semantic/security/print/final-byte QA.

OUTPUT
Return the declared Summative replacement scope, answer key/solutions/answer-sheet materials required by the Framework, and a compact QA report.
