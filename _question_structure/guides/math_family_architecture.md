# Math Question Family Architecture

## Canonical ownership
A **family** is a reusable student-action/evidence architecture, not a stored question and not a grade-specific prompt. The canonical library is resolved through `catalogs/math_family_library_manifest.json`. That manifest composes globally unique family definitions and course maps without cloning shared families.

The Lower Elementary–Grade 8 base families remain in `catalogs/math_question_family_registry.json`; course-specific extensions may live in separate canonical files such as `catalogs/math_question_families_algebra1.json`. Course visibility is likewise modular: the LE–8 map is `catalogs/math_course_family_maps.json`, while Algebra 1 is `catalogs/math_course_family_map_algebra1.json`.

Derived worksheet catalogs/banks and district-tool mirrors are compatibility outputs, not independent authoring authorities.

## Family lock
Before authoring, resolve exactly one `family_id` through the library manifest. Preserve its evidence job, student action, response mode, representation role, validity constraints, answer rule, difficulty band, and parallel invariants. A family summary is not a prompt.

## What is stored
Store generator contracts: prompt architecture, parameter names, mathematical property controls, validity constraints, render route, answer rule, legal variation axes, difficulty policy, and QA gates. **Do not store source questions.**

## Course maps
A family may appear in multiple courses. Shared families are referenced by ID rather than copied. Course maps control teacher browsing labels/topic placement only. New high-school courses may add new family-supplement and course-map files registered in the library manifest.

## Wording
`direct_concise` is the default. Context is included only when it carries mathematical information, modeling, units, interpretation, or transfer. Decorative backstory and filler directions are prohibited.

## Parallel forms and refresh candidates
Parallel forms and in-worksheet refresh candidates instantiate the same family with different legal parameters. They must preserve evidence demand, response/representation role, and approximate difficulty.

## Source/reference policy
Teacher-supplied parallel forms and external free worksheet catalogs may be studied for topic scope, recurring task architecture, representations, configurable properties, and difficulty progression. Never store or reproduce source wording, names, values, answer choices, diagrams, or source-specific layouts.

## Algebra 1 extension
The Algebra 1 extension was built from the teacher-supplied parallel forms plus a coverage/property review of Kuta Software's free Algebra 1 catalog. The Delta-style materials contribute representation-rich families such as balance/flowchart/tape models, mapping diagrams, function graphs, nonlinear systems, form-selection quadratics, regression/residual reasoning, and algebra tiles. Kuta contributes coverage and parameterization patterns for equations, inequalities, linear functions, systems, polynomials/factoring, quadratics, radicals/rational expressions, right-triangle trigonometry, and statistics. Neither source is stored as a question bank.
