BUILD ASSESSMENT PLAN — PILOT WORKING PM v0.1
===============================================
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
Create or revise the exact Unit Assessment Plan that the course Framework will preserve and consume.

PROCEDURE
1. Read the teacher-provided/current course source material and any existing current Assessment Plan.
2. Preserve existing course/unit terminology exactly unless the teacher explicitly changes it. Never normalize one course's stage vocabulary to another course.
3. Define the unit/section learning targets, exact I-can statements, vocabulary/notation, representations, misconceptions, application/modeling opportunities, learning-stage/source alignment, mastery goals, evidence opportunity plan, progress-tracking language, and summative plan appropriate to the course.
4. When revising an existing Assessment Plan, make the smallest necessary change and preserve unrelated plan language.
5. Do not copy universal question-structure catalogs into the Assessment Plan. Evidence descriptions may name needed evidence types, but structure taxonomy remains in `_question_structure.zip` and course preferences remain in the Framework.
6. Validate internal consistency: every named I-can/mastery goal/source is defined; section/unit terminology is used consistently; no invented aliases are introduced.

ALGEBRA SAFETY RULE
If working on the current Algebra architecture, preserve BOTH vocabularies where the plan uses them:
- Unit Source Alignment: Current Learning Source / Retrieval Source / Mastery Source
- Section Spiral Planning: Intro / Review / Mastery
These are distinct vocabularies, not aliases.

OUTPUT
Return the exact Assessment Plan file(s) plus a short BUILD_REPORT. If the job is a revision, preserve the plan's established format and filename unless the teacher explicitly requests a redesign.
