# v6.7 — Practice-to-Summative renderer/profile correction

- Kept universal/shared CSS unchanged; fixed downstream HTML/profile selection instead of creating Physics CSS forks.
- Physics Practice 1/2/3/Extra now use `ws-50`; CYU remains its canonical 3x2 + separate workspace page.
- Made Tarsia (18 pairs/section) and Blooket (20 questions/section) required Physics downstream outputs. Dedicated Bank exports are copied when present; otherwise the Framework explicitly permits traceable nonsecure derived game exports without mutating the Bank.
- Locked Activities to the teacher-approved universal 15-page hub and canonical Questions/Solutions, Stations, and Find Someone Who shells; companion naming standardized to set1/set2.
- Locked Exit printing to the universal `.print-active` packet JavaScript used by Algebra; shared `exit.css` remains unchanged.
- Locked Progress Tracker to exactly two physical print pages using the canonical compact mad-lib shell and all exact supporting I-cans.
- Locked Physics Summative answer sheet to 16 materialized bubble rows; unresolved renderer expressions fail closed. Review and Warm-Ups are unchanged.

# v6.6 — Plan-First Question Design

- Added dedicated question-design-map contract and required `unitN_question_design_map.json`.
- Added Physics-specific formula/quantitative priority, reverse solve directions, dependency-based multi-step design, I-can-specific Practice variety, and Exit variety rules.
- Exit Tickets are formative-secure by destination for semantic QA.
- Semantic question families may not be manufactured from form/version/question numbers.
- Inline SVG now requires answer-neutrality QA metadata.
- Updated finalizer/package checks accordingly.

# v6.5 — WTC becomes cross-Unit FRQ-decomposition practice

- Reframed every Physics WTC as one true connected multi-part FRQ, normally 3-5 labeled parts around a shared stimulus.
- WTC now explicitly practices unpacking/navigation skills: givens/unknowns, representations, part dependencies, relationship/strategy selection, prediction, planning, justification, and interpretation.
- WTC content may come from any Physics Unit and is explicitly excluded from current-Unit I-can coverage floors.
- WTC retains an exact course I-can ID/text as content provenance; that ID may be cross-Unit.
- Added WTC-specific canonical fields and finalizer checks for FRQ form/shared stimulus/part count/focus/coverage role.
- Added the unfamiliar-content safeguard: use future content only when the student work remains accessible as breakdown/representation/planning practice.
- External FRQ workbooks/released questions are structural exemplars only; do not copy source wording/data/figures.
- No CSS change required.

# v6.4 — Bank audit status + Unit resource sequence view

- Added canonical per-item `audit_status`; every fresh Bank item starts `NEEDS AUDIT`.
- Added teacher dispositions `KEEP`, `CLEAN`, and `REBUILD` with colored status badges and exact I-can text on every Bank card.
- Added `unitN_resources.html`, a stacked Unit-wide WTC / EX-YTI / Warm-Up / Exit Ticket / Summative sequence view.
- Preserved `unitN_review.html` for side-by-side I-can/question-family comparison rather than overloading the new sequential view.
- Added Physics path/schema/finalizer support for the new internal view and audit metadata.
- Extended canonical `bank.css` only where needed for utility links, audit badges, and stacked resource sequences.

# v6.4 — Final Bank-test hardening before Physics-specific PM work

- Added semantic-clone rules beyond literal duplicates; number/object/unit swaps alone are not meaningful variation.
- Added physical/linguistic plausibility and irrelevant-given guardrails.
- Added representation-fidelity rule: representation-explicit I-cans require actual student-facing representation evidence.
- Clarified that answer-neutral figures must remain present when the evidence job needs them; “do not show the answer” must never become “avoid images.”
- Resolved Bank handoff conflict: `figures` is the canonical structured field; item-level `dok`, `evidence_point_id`, `security_level`, `tables`, and `supporting_i_can_ids` are now literal required fields.
- Added detection for one fixed Practice weighting signature reused across multiple sections.
- Added source-provenance quality rule against one boilerplate `source_basis` on the entire Bank.
- Hardened `~finalize_bank.py` to enforce/flag the above and to catch high-confidence contradictory Physics wording.

# Physics Framework Reconciliation — v6.4

## v6.4 — I-can-first Bank correction
- Makes exact Assessment Plan I-can statements the atomic Bank planning/evidence/routing address.
- Adds `curriculum/i_can_index.json` with stable IDs for all 120 exact course I-cans.
- Adds `contracts/i_can_first_bank_contract.json` with destination coverage floors and evidence-plan requirements.
- Requires `unit{U}_i_can_map.csv` as a first-class downstream handoff.
- Reconciles Physics Notes inventory to 4 Example/YTI pairs = 8 items per section.
- Finalizer now hard-checks per-I-can Notes, Practice, CYU, Warm-Up, Exit A/B/C, and per-form Summative coverage.
- Unequal I-can counts remain allowed when evidence complexity warrants them; zero coverage and unexplained overconcentration are not.

## Kept
- Original eight Physics Assessment Plans unchanged as curricular evidence authority.
- Existing section reference packets, section enrichment, source-page matches, formula archetypes, approved course figures, source-reference figures, graph/finalizer/MathJax tools, future-resource hooks, and Physics Summative rendering contract.

## Added / strengthened
- Algebra-style course-profile/compatibility architecture adapted to Physics rather than copied mechanically.
- `curriculum/section_index.json` and `curriculum/mastery_evidence_map.json`.
- Full extracted Hewitt/Conceptual Physics source library and indexes, including 361 captured images.
- Hewitt question-family profile and section-level source/visual routing.
- Physics Notes contract emphasizing longer conceptual reading, image-led storytelling, and more Stop & Discuss opportunities.
- Teacher dashboard snapshot/inventory/path QA.
- Stable naming + changed-files-only repo delivery contract.

## Deliberately not copied from Algebra
- No Algebra `spiral_stage_map.json`: Physics Assessment Plans use Mastery Goals + recurring disciplinary practices rather than Algebra's Current Learning/Retrieval/Mastery stage architecture. Physics receives `mastery_evidence_map.json` instead.
- No Algebra graph/equation/table/context quota system. Physics uses phenomenon/model/diagram/graph/data/equation/context representations according to the exact learning job.
- No Algebra-only Diamond Problem behavior or constructed-response-only Summative rule.

## Known dashboard cleanup findings
- Comments still mention the Algebra repo/folder.
- Printables and Welcomes top links still point to Algebra URLs.
These are recorded for later dashboard repair and are not treated as Framework path authority.
