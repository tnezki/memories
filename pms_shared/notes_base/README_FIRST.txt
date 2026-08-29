BASE NOTES PM STARTER v4.8 — READ FIRST
=======================================

Purpose
-------
This starter is the universal Notes layer. It is intentionally course-neutral.

Normal fresh-chat Notes build inputs
------------------------------------
1. This Base Notes PM Starter ZIP (includes Base Notes PM + current Curriculum Philosophy)
2. The current self-contained Course Framework ZIP
3. The finalized current Unit Bank ZIP

Do NOT upload a separate Curriculum Philosophy when it is already bundled here.

Pilot prompt
------------
Carefully read PM and Run.

Architecture
------------
Curriculum Philosophy -> Base Notes PM -> Course Framework -> finalized Unit Bank -> complete Unit Notes

Authority split
---------------
- Curriculum Philosophy: universal teaching/learning beliefs.
- Base Notes PM: universal Notes construction, canonical-Bank consumption, student/teacher mechanics, QA, and packaging.
- Course Framework: course-specific Notes philosophy/behavior, exact learning architecture, reading/tone, representations, visual/layout contract, sources, deployment paths, and graph/figure capabilities.
- Finalized Unit Bank: canonical WTC / Example / You Try It content and approved Bank figures/answers.

Current v4.8 Notes mechanics
----------------------------
- Every substantial reading is followed immediately by a content-specific Stop and Discuss.
- Main S&D: normally 2–3 questions mixing direct/text-dependent sense-making with conceptual inference.
- Later S&D within the same I-can: normally one focused conceptual checkpoint when useful.
- Useful Math/Model Notes abundance is allowed; teacher can skip.
- First meaningful introduction of a previewed vocabulary/notation term may be bolded; do not bold every recurrence.
- Visible Example/YTI numbering follows rendered teaching order while canonical Bank identity stays in metadata.
- Canonical graph/table content must receive the current Framework presentation classes; bare figures/tables are a layout defect when approved classes exist.
- Descriptive captions/titles beneath student-facing representations are omitted; mathematically necessary labels remain inside the representation.
- Exact typography/graph/table/workspace values come from the CURRENT Framework visual contract; stale older numeric defaults must not survive a version update.
- Three-column vocabulary sort markup now has an exact CSS contract: `vocab-sort-table` on the table, `vocab-sort-space` on the blank body row, and directions inside `vocab-sort-task` / `vocab-sort-directions`.
- Three-row skim / "Let's Get Started" markup now has an exact CSS contract: `skim-section-directions` on the directions paragraph and `skim-section-table` on the table so the prompt column stays narrow and the writing column stays generous.

CSS / layout
------------
Production HTML keeps exactly base.css then notes.css. The Base PM provides the universal class floor; the current Course Framework may approve course-specific wrapper/layout classes in its Notes visual contract. Do not add a third production stylesheet merely to carry a pilot patch.

Fresh-chat rule
---------------
Read every file in this starter plus the current Framework and Bank. Do not blend remembered older Notes PMs or course-family branches into the build.

Pre-ZIP final-byte gate
-----------------------
Run the current Framework `tools/MathJax/final-byte fixer declared by the current Framework manifest` on the complete staging Notes output before creating the final ZIP; then QA the repaired bytes.

Existing Notes repair helper
----------------------------
Use `Tools/fix_notes_layout_contract.py` to repair legacy vocabulary-sort and skim-table markup without changing CSS.

GENERIC RUN
Use exactly: `Carefully read PM and Run.`
The current PM package determines the operation; do not paste an older resource-specific prompt.
