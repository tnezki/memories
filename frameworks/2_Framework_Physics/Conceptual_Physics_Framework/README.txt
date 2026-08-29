CONCEPTUAL PHYSICS FRAMEWORK — v6.8
========================================

Stable saved artifact: Framework_Physics.zip
Internal version: v6.8 (diagnostic metadata only)

This revision keeps the I-can-first Physics architecture and hardens two recurring failure modes exposed by Unit 1 testing: cloned question inventory and answer-revealing student figures. The exact I-can remains the atomic planning/evidence/routing address.

Major additions:
- absolute student-figure rule: NEVER SHOW THE ANSWER IN THE STUDENT IMAGE; reusable/source figures require prompt-specific visual inspection and Bank figure metadata
- exact canonical prompt duplication prohibited by default; secure/Summative exact duplicates forbidden; repeated families must vary meaningful evidence features
- I-can-first is not an equal-allocation quota: do not default to 8/8/8 just because a Practice set has 24 items and 3 I-cans
- exact-I-can atomic index (`curriculum/i_can_index.json`) + hard I-can-first Bank architecture/coverage contract
- Physics finalizer reconciled to 8 Notes items/section and direct per-I-can destination/Summative coverage QA
- complete Physics course profiles for Bank, Notes, Practice, Activities, Demos/Investigations, Performance Tasks/Quick Checks, and Recurring/Assessment resources
- Base-PM compatibility contracts for each resource family
- normalized curriculum/section/mastery-evidence indexes
- teacher-dashboard snapshot + live path inventory/QA
- full teacher-supplied extracted Conceptual Physics library: 100 source/review folders, 361 captured images, manifests, HTML, and extraction notes
- section-to-Hewitt visual/source routing
- Hewitt question-family profile (Reading Check; Think and Do; Plug and Chug; Think and Solve; Think and Rank; Think and Explain; Think and Discuss)
- explicit Physics Notes visual-story contract: images often drive the narrative; more reading and content-specific Stop & Discuss than Algebra
- stable/unversioned canonical artifact naming; versions live in metadata, not authority-by-filename logic

Current authority boundary: Curriculum Philosophy -> `_question_structure.zip` -> Physics Framework (exact Unit Assessment Plan within it) -> task PM -> tools/CSS. Framework source/visual libraries are Physics-specific enrichment.

V6.3 FINAL BANK-TEST HARDENING
------------------------------
This revision is intentionally narrow. It adds semantic-clone, physical-plausibility, representation-fidelity, literal machine-handoff, item-level provenance, and cross-section I-can-allocation checks. The next successful Unit 1 test is intended to mark the transition from Framework tuning to Physics-specific PM upgrades.



V6.6 PLAN-FIRST QUESTION DESIGN
--------------------------------
- Adds a required `unitN_question_design_map.json` before final question prose is authored.
- Integrates the dedicated `_question_structure.zip` as the question-design/variation authority; the older combined Toolkit remains for visual/source enrichment and nonconflicting legacy structures.
- Physics EX/YTI now explicitly prioritizes strong contextual quantitative/formula pairs when the I-can naturally requires mathematical application.
- Practice variety is mapped by I-can fit (formula/direct/inverse, dependent multi-step, vocabulary/matching, graph/data, diagram/FBD/vector/model, misconception, short response, transfer) with no universal percentages.
- Multi-step is defined by dependency; one natural final question is preferred when the intermediate result is only a bridge.
- Exit Tickets require planned variety within the four questions and across A/B/C and are formative-secure by destination.
- `question_family_id` must be semantic; version/question-number tokens cannot manufacture unique families.
- Inline SVG representations now carry the same answer-neutrality QA metadata as file-backed figures.
- Finalizer requires question-design-map/item linkage and applies destination-based Exit security.

V6.5 WTC FRQ-DECOMPOSITION ROUTINE
----------------------------------
- Every WTC is a true connected multi-part FRQ, normally 3-5 labeled parts around one shared stimulus.
- WTC practices how students break down long questions; it is not a current-section preview/coverage requirement.
- WTC content may come from any Physics Unit. The exact source content I-can is still displayed for provenance, but WTC is excluded from current-Unit I-can coverage.
- Cross-Unit or future-content WTCs must remain accessible as unpacking/representation/relationship-selection/planning practice when the procedure has not been taught.
- External/released/workbook FRQs are morphology references only; Bank WTCs are newly authored.
- No bank.css change was required; existing bank-item/multipart HTML supports the new WTC form.

V6.4 BANK AUDIT/RESOURCE-VIEW ADDITION
--------------------------------------
- Adds canonical audit_status with fresh-build NEEDS AUDIT state and KEEP/CLEAN/REBUILD dispositions.
- Adds `unitN_resources.html` as a stacked Unit-wide WTC / EX-YTI / Warm-Up / Exit Ticket / Summative teacher view.
- Preserves `unitN_review.html` as the separate I-can/question-family side-by-side comparison view.
- Extends shared bank.css with compact colored audit badges and resource-view support.
- Finalizer now validates the third teacher view and audit-status schema/display.


V6.7 PRACTICE-TO-SUMMATIVE RENDERING LOCK
-----------------------------------------
- Shared/universal CSS remains unchanged.
- Practice 1/2/3/Extra: ws-50; CYU unchanged.
- Physics Tarsia/Blooket are required; derive traceable nonsecure game exports only when dedicated Bank exports are absent.
- Activities use exact universal 15-page hub and canonical companion shells with set1/set2 filenames.
- Exit uses universal `.print-active` print JavaScript; no Physics-only print target mechanism.
- Progress Tracker is exactly two physical print pages using canonical compact shell.
- Physics Summative must materialize 16 bubble rows; Review/Warm-Ups unchanged.

V6.8 AUTHORITY RECONCILIATION
-------------------------------
- Preserves exact Assessment Plans, WTC FRQ decomposition, contextual quantitative EX/YTI priority, real Physics representations, and source-grounded Notes behavior.
- Universal question/evidence structures resolve to `_question_structure.zip`; procedure/package mechanics resolve to task PMs; renderer mechanics resolve to tools/CSS.
- Naked variable-assignment plug-and-chug prompts are explicitly rejected in favor of concrete physical situations.
