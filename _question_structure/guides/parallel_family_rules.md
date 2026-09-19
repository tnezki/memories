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
