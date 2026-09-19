# Parallel Family Rules

A `question_family_id` names a semantic evidence family, not a file slot, version, grade, or question number.

## Canonical math family rule
For math worksheet generation, resolve the family in `catalogs/math_question_family_registry.json`. The family contract is HARD: evidence job, student action, response mode, representation role, validity constraints, answer rule, and difficulty band must all match the final item.

## Instructional parallels
Numeric-only variants are legitimate when procedural fluency is the explicit evidence job. Conceptual/modeling families require stronger variation while preserving the same evidence demand.

## Parallel worksheet forms
When teacher-supplied Version A/B/C/etc. worksheets intentionally mirror one another, use the invariant architecture to infer one generator family. Do not store the forms as separate question banks.

Keep invariant:
- target/evidence job;
- student action;
- family architecture;
- response and representation role;
- approximate difficulty and computational load.

May vary when valid:
- clean numerical parameters;
- names or functional surface contexts;
- answer-choice order and misconception distractors;
- model counts, dimensions, coordinates, or orientation when evidence-equivalent.

A parallel FAIL occurs when a new version changes operation, reasoning demand, representation requirement, recognition-vs-construction demand, or difficulty band.

## Refreshable worksheet alternates
A refreshable worksheet alternate is another legitimate parallel instance of the SAME family occupying the SAME worksheet slot. It is not a new family, new topic, or extra visible question.

For a refresh pool, keep invariant:
- `question_family_id`;
- learning target / I Can and evidence job;
- student action;
- response mode;
- representation role and visual semantics;
- approximate difficulty and computational load;
- validity constraints and answer rule.

Refresh candidates may vary only along the family's legal variation axes. Values, coordinates, data, model counts, functional surface context, legal orientation, answer-choice order, and family-authorized morphology/representation variants may change when the family permits them.

A refresh pool should feel like **three legitimate new questions from the same family**, not one question mechanically re-skinned three times. When more than one legal morphology or representation path exists, use meaningful variation across the pool while holding evidence and difficulty invariant. Pure number swaps are sufficient only for families whose explicit evidence job is numerical/procedural fluency.

A refresh alternate FAIL occurs when:
- it changes to another family;
- it changes the operation or reasoning demand;
- it changes recognition to construction or vice versa;
- it drops/adds a required representation;
- its visual is semantically different from the family requirement;
- its difficulty meaningfully drifts;
- it duplicates another candidate's effective prompt/parameters.

For the District Math Worksheet Builder, a canonical visible slot uses a three-candidate pool by default: initial candidate + two refresh alternates. The teacher may cycle those candidates before printing. Hidden candidates do not count toward the teacher-selected visible question total. Teacher-defined custom slots follow the same three-candidate rule, using the teacher's custom description as the invariant authoring constraint.

The finished worksheet is offline/self-contained. It may cycle only the embedded candidate pool; authoring an additional AI-generated custom candidate after build time requires a new build or an explicitly connected future AI service.

When the worksheet has an answer key, the active refresh-candidate state must be transferable to the key so the displayed/printed key matches the exact refreshed worksheet.

## Secure parallels
For secure assessment items, version/order/noun/number swaps alone are not sufficient. Use a new evidence stimulus while preserving the target and appropriate family.

## Family planning record
Every family must record:
- invariants;
- legal variation axes;
- validity constraints;
- answer rule;
- render route;
- QA gates.
