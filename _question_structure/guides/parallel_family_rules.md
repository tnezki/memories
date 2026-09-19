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
A refreshable worksheet alternate is a teacher-selectable replacement for one worksheet slot after the initial exact blueprint has been generated. Its purpose is **another question with the same instructional intent**.

For the District Math Worksheet Builder, resolve refresh behavior through `catalogs/math_refresh_groups.json`:
- Candidate 1 keeps the slot's original blueprint family.
- If Candidate 1 belongs to a curated refresh group, Candidates 2–3 come only from the family IDs and morphologies authorized by that group.
- If Candidate 1 belongs to no refresh group, Candidates 2–3 remain in the exact same family.
- Do **not** use all families selected elsewhere on the worksheet as the refresh pool.
- A refresh group may explicitly authorize a close neighbor family even if that family was not separately selected for the initial worksheet. This is a semantic permission for refresh, not a change to the initial blueprint.

For every refresh candidate, keep invariant at the instructional-intent level:
- the broad student action (factor stays factor; solve stays solve; graph stays graph; compare stays compare);
- appropriate grade/course scope;
- approximate overall difficulty/computational load;
- originality and answer correctness;
- family-contract validity for whichever group-authorized family is used;
- answer-neutral student visual policy.

A refresh alternate FAIL occurs when:
- it leaves the seed family's curated refresh group;
- it changes the broad student action or evidence intent;
- it is materially easier/harder than the slot it replaces without teacher intent;
- it violates its own family contract;
- its required representation is missing/wrong or answer-revealing;
- it duplicates another candidate's effective prompt/parameters without a good procedural-fluency reason.

A canonical visible slot uses a three-candidate pool by default: initial blueprint candidate + two refresh alternates. The teacher may cycle those candidates before printing. Hidden candidates do not count toward the initial visible question total.

### Quadratic factoring example
For seed family `POLY_FACTOR_QUAD`, the curated `quadratic_factoring` group intentionally supports variation such as:
- a standard monic factorable trinomial;
- a factorable trinomial with leading coefficient `a ≠ 1` and integer factors;
- a special quadratic factorization through `POLY_FACTOR_SPECIAL`, such as difference of squares or a perfect-square trinomial.

It explicitly does **not** authorize balancing/linear-equation items, exponent-rule items, solving a quadratic equation, expanding special products, or graphing a quadratic. Those change the requested student action.

Teacher-defined custom structures use the teacher's custom description as their invariant refresh neighborhood and receive three build-time candidates.

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
