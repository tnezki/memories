# _question_structure v2.0 — READ FIRST

This package is the dedicated authority for question-design planning, reusable question-family architecture, representation alignment, and parallel variation. It travels with build PMs independently of large visual/source libraries.

It does not replace the current Curriculum Philosophy, Base PM, course Framework, Assessment Plan, or course-specific visual/graph tools. It answers a narrower question:

> Before writing a question, what evidence job, student action, family, response mode, representation, valid parameters, and variation are allowed for this exact target and destination?

## Authority / precedence
When bundled with a build PM, use this order for question authoring:
1. current explicit teacher instruction
2. current Curriculum Philosophy
3. current executable Base PM
4. current course Framework + exact Assessment Plan/I-can map
5. **this `_question_structure` package for question-design/family/variation behavior**
6. current visual/source toolkit for graphics, source examples, and enrichment

If older Question Structure + Visual Toolkit material conflicts with this package on authoring sequence, wording profiles, evidence-response alignment, family identity, parallel variation, or representation execution, this package wins.

## Core workflow
Do not start by generating question text.

**Map target → evidence job → student action → canonical family → response/representation → parameters → author → independently solve/verify → derive metadata.**

DOK/Bloom remain descriptive and are assigned only after the final task exists.

## Canonical math-family architecture
For reusable math questions, use these authorities in order:

1. `QUESTION_STRUCTURE_CORE.md`
2. `contracts/math_question_family_schema.json`
3. `catalogs/math_question_family_registry.json`
4. `catalogs/math_course_family_maps.json`
5. `guides/math_family_architecture.md`
6. `guides/parallel_family_rules.md`
7. `guides/wording_profiles.md`

The registry owns the family definition. Course maps own where a family appears for teacher browsing. Derived worksheet banks/catalogs may package those definitions for a tool, but they are not separate authoring authorities.

One family may appear in several grade/course maps. Do not clone the family merely to give it a different grade label.

## Direct / concise math wording
`direct_concise` is the default profile for routine math worksheets, Quick Checks, and ordinary practice unless context is mathematically functional.

Do not add names, stories, or repeated directions that do not affect the model, operation, interpretation, units, or evidence demand.

## Source-reference rule
Teacher-provided parallel forms and external worksheet catalogs may be studied for:
- skill scope;
- recurring task architecture;
- representations;
- parameter/property options;
- difficulty progression;
- response modes.

Do not store or reproduce their question wording, numbers, names, choices, diagrams, or layouts as family content. The reusable asset is the abstract generator contract.

## Legacy libraries
`library/Universal_Question_Structure_Library_v2.md`, `library/Question_Starter_Stem_Library_v1.md`, and the legacy structure indexes remain available as reference menus for unusual destinations and non-math work.

They are **not canonical math worksheet generators** and may not override a current math family contract. Wordy legacy stems should not be imported merely because they exist in the older library.

## Scope levels
This package supports planning at five nested levels:
- **artifact** — what kinds of evidence the whole artifact needs
- **section** — how evidence/representations/variety are distributed
- **I-can** — best-fit evidence modes for the exact target
- **family** — the reusable evidence/student-action/generator contract
- **item** — one instantiated question with exact parameters and final metadata

## Critical rule
Variety is not a quota. Do not force every target into every structure. Map what actually fits, then author to that map.

## Read order
1. `QUESTION_STRUCTURE_CORE.md`
2. `contracts/question_design_workflow.json`
3. `contracts/question_design_schema.json`
4. for math: `contracts/math_question_family_schema.json`
5. for math: `catalogs/math_question_family_registry.json`
6. for math: `catalogs/math_course_family_maps.json`
7. relevant guides
8. legacy universal structure library/catalog only as a menu after the target and evidence job are known
