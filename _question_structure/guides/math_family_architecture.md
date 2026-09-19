# Math Question Family Architecture

## Canonical ownership
A **family** is a reusable student-action/evidence architecture, not a stored question and not a grade-specific prompt. The canonical library is resolved through `catalogs/math_family_library_manifest.json`. The manifest composes globally unique family definitions, course maps, and curated preview sources without cloning shared families.

The library is modular by mathematical need, not by arbitrary course duplication. Lower Elementary–Grade 8 shared/base families remain in `math_question_family_registry.json`; Algebra 1, Geometry, shared Algebra 2/Precalculus, and Calculus extensions live in registered supplement files. Course maps decide where each family appears to teachers.

Derived worksheet catalogs/banks and district-tool mirrors are compatibility outputs, not independent authoring authorities.

## Family lock
Before authoring, resolve exactly one `family_id` through the library manifest. Preserve its evidence job, student action, response mode, representation role, validity constraints, answer rule, difficulty band, visual policy, and parallel invariants. A family summary is not a prompt.

## What is stored
Store generator contracts: prompt architecture, parameter names, mathematical property controls, validity constraints, render route, answer rule, legal variation axes, difficulty policy, visual policy, and QA gates. **Do not store source questions.**

## Course maps
A family may appear in multiple courses. Shared families are referenced by ID rather than copied. Course maps control teacher browsing labels/topic placement only. The active library now spans Lower Elementary Math through Calculus.

## Student visual vs. solution visual — HARD
Every graph/diagram/construction family must distinguish the information the student is given from the completed solution.

- `student_view` contains only givens, answer-neutral markings, blank axes/construction surface, or the representation being interpreted.
- `solution_view` may add the completed graph, image, shading, tangent/secant, transformed figure, solution curve, labels, or other answer evidence.
- When construction itself is assessed, a completed construction may **never** appear in the student preview or student worksheet.
- The answer key must use the same generated parameters and may overlay the completed construction.

This rule prevents errors such as giving a student the boundary line/shading for an inequality they were asked to graph.

## Wording
`direct_concise` is the default. Context is included only when it carries mathematical information, modeling, units, interpretation, or transfer. Decorative backstory and filler directions are prohibited.

## Parallel forms and refresh candidates
Parallel forms and in-worksheet refresh candidates instantiate the same family with different legal parameters. They preserve evidence demand, response/representation role, visual policy, and approximate difficulty.

## Source/reference policy
Teacher-supplied parallel forms and external free worksheet catalogs may be studied for topic scope, recurring task architecture, representations, configurable properties, and difficulty progression. Never store or reproduce source wording, names, values, answer choices, diagrams, or source-specific layouts.

## High-school expansion
Geometry, Algebra 2, Precalculus, and Calculus extensions were built from the teacher-supplied parallel forms/topic inventories and cross-checked against official Kuta free course catalogs for coverage/property options. Delta-style references contribute representation-rich tasks; Kuta informs coverage and configurable-generator breadth. Neither is stored as a question bank.
