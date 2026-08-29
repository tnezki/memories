# AP Calculus AB Framework v2.4

Machine-first, Framework-integrated course brain for the supplied 8-unit / 40-section AP Calculus AB course.

## What is embedded
- 8 original Unit Assessment Plans (unchanged source bytes)
- 40-section course map and pacing/classroom-flow signals
- CED-derived official AP topic titles, unit weightings, big ideas, mathematical practices, calculator/exam expectations
- compact AP Topics scoring-guide source catalog with 68 source documents, representative task excerpts, and scoring signals
- section reference packets combining Assessment Plan authority + CED + AP task models + calculus textbook page pointers
- question/task archetype menus, misconception/distractor seeds, Math Note ideas, reusable table structures, and future resource hooks
- 40 approved answer-neutral course figures generated with the authoritative graph tool
- graph/finalizer/MathJax/CSS references retained as implementation support; current task PM/tools own their use
- canonical course-file-structure and live-course-upgrade contracts

## Compact-source policy
Large raw AP Topic PDFs, textbooks, and CED are not duplicated into the ZIP. Their strongest authoring value is curated into machine-readable packets, representative AP task excerpts, scoring profiles, page pointers, source hashes, and visual pointers. This keeps the Framework portable while avoiding a thin metadata-only package.

## Current authority boundary
Curriculum Philosophy owns universal principles; `_question_structure.zip` owns universal question/evidence structures; this Framework owns AP Calculus-specific behavior + exact Unit Assessment Plans; current task PM owns procedure; tools/CSS own implementation mechanics. Framework source packets and task archetypes are Calculus-specific enrichment, not a competing universal structure catalog.

## v2.2 final-byte reconciliation
- Standalone MathJax maintenance tool updated to `tools/~fix_mathjax_v10.py`.
- Universal Bank finalizer embeds the v10 configuration-alignment repair and runs it before the FINAL ZIP.
- HTML-producing resource builds may run the Framework v10 tool on staging output before packaging.

## v2.4 authority reconciliation
Preserves all Unit Assessment Plans/AP mappings while moving procedure/package mechanics to task PMs and universal question structures to `_question_structure.zip`. Calculus-specific notation, graphs, calculator expectations, AP justification, FRQ morphology, and source intelligence remain Framework-owned.
