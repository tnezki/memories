# PATCH Z · Metadata Reconcile — v1.1

## Purpose
Reconcile final metadata from stable audited questions after content patches are complete.

# Shared operating contract

## Course restriction
This v1.1 patch PM is Physics-targeted. If the request course is not Physics, fail closed unless the user explicitly asks to adapt the PM for another course.

## Current-Bank rule — HARD
The request MUST contain the **most current complete/materialized Unit Bank**, after every previously approved REPO_PATCH has been applied to the deployed Bank. Never use a Bank copied from an earlier chat, an earlier request, or a sparse patch as the source Bank.

If the packaged input is not a complete/materialized current Unit Bank, fail closed. A REPO_PATCH is an overlay/delivery artifact, never the next Bank source by itself.

> **Tool packaging note:** The current Physics Framework already bundles the canonical `~graph_tool_v12.py`. A second loose copy under `memories/Tools/` is optional, not a required authority. The large visual toolkit is optional support and must never block a Patch request when absent.

## Authority order
Read and obey, in this order when supplied:
1. current Curriculum Philosophy;
2. this patch PM (scope/repair verb);
3. current course Framework (course-specific behavior and hard rules);
4. current Build Bank PM (canonical Bank schema/rendering/handoff contract);
5. current `_question_structure.zip` (question-design/variation authority);
6. current materialized Unit Bank being patched;
7. optional visual/tool support explicitly packaged by the request.

If authorities conflict, the more specific current authority controls within its owning layer. Fail closed rather than inventing a rule.

## Scope lock
- Work only inside the Unit/scope selected by the request.
- Never change a canonical `bank_id`, section, destination/form routing, exact primary `i_can_id`, supporting I-can IDs, Learning Target, Mastery Goal, evidence-point/security routing, canonical count, or item order unless THIS PM explicitly authorizes that field.
- `KEEP` items are read-only in every content patch PM.
- `NEEDS AUDIT` items are read-only in content patch PMs; the Audit + Route patch owns classification.
- Preserve all non-target canonical questions unchanged.
- Do not use synonym swaps, noun swaps, number swaps, sentence-order swaps, or choice-order swaps as a substitute for a new evidence opportunity.

## Audit-status lifecycle
Allowed canonical values are exactly `NEEDS AUDIT`, `KEEP`, `CLEAN`, `REBUILD`.
- Fresh build: `NEEDS AUDIT` with no failure reason yet.
- Audit + Route patch: classifies NEEDS AUDIT as KEEP/CLEAN/REBUILD and writes why + issue codes + owning route.
- Any patch that materially changes student prompt, choices, answer/key, evidence job, stimulus, figure/representation, or solution MUST reset that changed item to `NEEDS AUDIT` and clear its prior `audit_primary_issue`, `audit_issue_codes`, `audit_why`, and `audit_patch_route` because those reasons describe the old bytes.
- A patch never certifies its own changed work as KEEP.
- Pure metadata reconciliation may preserve status when student evidence did not change.

## Canonical-first editing
Edit canonical item object(s) first. Then keep all derived teacher views/maps synchronized from those same objects. At minimum inspect/update canonical Bank JSON and every teacher view that displays changed items (`unitN.html`, `unitN_review.html`, `unitN_resources.html`) plus any mapping/export/design artifact whose stored content actually changed.

Do not hand-edit one HTML view while leaving canonical JSON or another view stale.

## Question-design discipline
When authoring/re-authoring a question:
1. resolve exact I-can and evidence job;
2. inspect existing `question_design` and Unit question-design map;
3. choose/repair the evidence opportunity before prose;
4. use `_question_structure.zip` for structure, wording profile, multi-step, vocabulary, parallel variation, and representation choices;
5. use Physics Framework for Physics-specific quantitative/diagram/graph/context rules;
6. write the actual question;
7. independently solve/verify the final instantiated question, representation, answer/key, and solution;
8. derive DOK/Bloom/family metadata from the finished task rather than from a slot quota.

## Quality guardrails
- Natural high-school Physics language; no Mad-Lib location/object collisions.
- No internal authoring labels/scaffold leakage in student prompts.
- Context must earn its place.
- If a task asks students to interpret/critique/compare a representation, provide the actual representation.
- A representation must be answer-neutral where required and match the prompt/key exactly.
- Secure destinations require semantically independent evidence, not cosmetic variation.
- Selected-response distractors must arise from the exact item's plausible misconception/error paths.

## Audit reason + routing contract
Every audited item carries enough information to answer **why** it has its status and which narrow patch owns the problem.

Canonical audit fields:
- `audit_status`: exact value `NEEDS AUDIT`, `KEEP`, `CLEAN`, or `REBUILD`.
- `audit_primary_issue`: one stable issue code or empty/null when not applicable.
- `audit_issue_codes`: array of all material issue codes found in the current audited version.
- `audit_why`: short teacher-readable reason tied to the actual item.
- `audit_patch_route`: exact workflow key of the recommended owning patch, or empty/null for KEEP/NEEDS AUDIT.

Stable route families:
- `patch_bank_mapping_integrity`
- `patch_bank_clean`
- `patch_bank_wtc_frq`
- `patch_bank_ex_yti`
- `patch_bank_practice_families`
- `patch_bank_exit_tickets`
- `patch_bank_summative_secure`
- `patch_bank_summative_distractors`
- `patch_bank_representations`
- `patch_bank_core_questions`
- `patch_bank_math_notation`
- `patch_bank_cross_resource_freshness`
- `patch_bank_metadata`

Representative issue codes include:
- mapping: `mapping_wrong_i_can`, `mapping_cross_view_mismatch`, `mapping_coverage_conflict`;
- clean: `wording_grammar`, `scaffold_leakage`, `minor_context_naturalness`;
- WTC: `wtc_not_frq`, `wtc_missing_shared_stimulus`, `wtc_not_decomposition`;
- EX/YTI: `ex_yti_weak_transfer`, `ex_yti_formula_opportunity_missed`;
- Practice: `practice_semantic_clone`, `practice_quota_variety`, `practice_structure_mismatch`;
- Exit: `exit_semantic_exposure`, `exit_form_variety`;
- Summative secure: `summative_semantic_exposure`, `summative_form_clone`, `summative_response_mode_mismatch`;
- distractors: `distractor_generic_reuse`, `distractor_implausible`;
- representation: `representation_missing`, `representation_mismatch`, `representation_rejected`, `representation_answer_bearing`, `representation_metadata_mismatch`;
- core: `physics_incorrect`, `answer_key_incorrect`, `context_incoherent`, `evidence_missing`, `question_structure_mismatch`;
- math/notation: `math_notation`, `unit_notation`;
- freshness: `cross_resource_clone`;
- metadata: `family_metadata_mismatch`, `dok_bloom_mismatch`, `design_map_mismatch`, `security_metadata_mismatch`.

If an item has multiple problems, route it to the **smallest owning patch that can repair the substantive evidence safely**. Destination-specific patches win over generic representation/core patches when they already own the item (for example, a WTC with a missing shared representation routes to WTC FRQ, not generic Representation). Mapping integrity is the exception: if mapping itself is unreliable, route to Mapping Integrity first.

## Bank-level routing summary
Maintain/recompute a root-level `audit_summary` in the canonical Bank data whenever audit fields or statuses change. It must include at minimum:
- `status_counts`;
- `issue_counts`;
- `route_counts`;
- `recommended_next_patch` with `workflow_key`, `label`, `target_count`, and a concise `why`;
- `metadata_reconcile_required` boolean;
- `final_audit_required` boolean.

### Recommendation algorithm
The teacher does NOT memorize a sequence.
1. If any unresolved item is routed to `patch_bank_mapping_integrity`, recommend Mapping Integrity first, regardless of count.
2. Otherwise, among unresolved `REBUILD` items, aggregate by `audit_patch_route` and recommend the route with the largest affected-item count. Use hard security/representation/content severity only as a tie-breaker; do not invent a fixed destination sequence.
3. When no REBUILD items remain, recommend `patch_bank_clean` if CLEAN items remain.
4. When no classified CLEAN/REBUILD items remain but one or more items are `NEEDS AUDIT`, recommend `patch_bank_audit_route`.
5. When all evidence-bearing items are KEEP and `metadata_reconcile_required == true`, recommend `patch_bank_metadata`.
6. After metadata reconciliation, recommend `patch_bank_audit_route` for final verification when `final_audit_required == true`.
7. When no unresolved issue, no NEEDS AUDIT, no metadata reconciliation, and no final verification remain, report `BANK PATCH CYCLE COMPLETE`.

Every PM's chat response MUST end with a clearly visible block:
`NEXT PATCH: <exact label or BANK PATCH CYCLE COMPLETE>`
`WHY: <current-Bank reason and affected count>`
`CURRENT BANK RULE: Apply this returned REPO_PATCH to the deployed Bank before creating the next request.`
Do not merely say "re-audit later" or assume the teacher remembers a sequence.

## QA and delivery
Run the current Bank finalizer after edits. Also perform semantic/Physics QA that the finalizer cannot guarantee.
Pre-existing out-of-scope defects may be reported but are NOT permission to broaden scope.

Final delivery is always a **PATCH**, not a replacement Bank:
- If multiple repository files changed, return ONE `REPO_PATCH` ZIP containing only new/changed files in repository-relative structure.
- If exactly one repository file changed, return that file.
- Do not package unchanged repository files merely to make the ZIP look complete.
- In chat, state target count, changed count, skipped/read-only count, fail-closed items, finalizer result, and then the exact NEXT PATCH block required above.

# PM-SPECIFIC CONTRACT

## Entry condition
Run only when current routing summary recommends PATCH Z or the request explicitly targets audited metadata defects. Do not use this to repair student content.

Re-derive semantic family ID, DOK/Bloom, task architecture, response mode, variation, representation metadata, security metadata, and design-map linkage from the finished evidence. Never manufacture family uniqueness with version/question numbers. Equivalent tasks should not receive contradictory DOK merely because of slots.

Do not change student prompt/choices/answer/solution/figure or exact I-can/evidence routing. If honest metadata cannot be reconciled without changing evidence, fail closed and route to content patch.

On successful reconciliation set `metadata_reconcile_required=false` and `final_audit_required=true`; preserve status where evidence did not change; recompute summary. NEXT PATCH should therefore normally be PATCH 00 · Audit + Route for final verification.

# Completion standard
A successful run patches only its owned current-Bank defects, never rewrites KEEP items, resets material changes to NEEDS AUDIT, keeps all derived Bank views synchronized, recomputes routing, runs the current finalizer, and tells the teacher exactly which patch to run next.
