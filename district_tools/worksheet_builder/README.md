# Math Worksheet Builder — Family-Contract Pilot

District teacher tool for building self-contained worksheet requests from reusable canonical math question families.

## Current active coverage
- Lower Elementary Math
- Grade 4 Math
- Grade 5 Math
- Grade 6 Math
- Grade 7 Math
- Grade 8 Math

Algebra 1, Geometry, Algebra 2, Precalculus, and Calculus are intentionally held as future course maps until their teacher reference sets are incorporated. Do not infer that the current middle-school catalog is a complete secondary-math catalog.

## Workflow
1. Check one or more grade/course filters.
2. Choose 1-4 parallel versions, a broad difficulty profile, two-column vs one-column pages, and whether to include the answer key.
3. Browse topic cards or search across the selected grade levels.
4. Use the magnifying-glass **Preview** control to inspect a representative complete problem for a family.
5. Check exact question families. Every checked family starts at **1 question**; use the `− / +` controls to change its quantity.
6. Use **+ Add another custom question structure** for teacher-defined structures that are not yet in the canonical library.
7. Review the **Selected questions** tray, then click **Create Worksheet Request ZIP**; the ZIP downloads immediately.
8. Upload that request ZIP to ChatGPT. It runs automatically and returns one response ZIP.
9. Unzip the response and open `CLICK_ME.html`.

The finished `CLICK_ME.html` exposes only the adjustable worksheet and optional answer key. Internal QA stays hidden.

The finished adjustable worksheet keeps per-version/per-problem controls. Workspace can be collapsed to **0%** or expanded through **1200%**. Graph/diagram sizing remains independently adjustable.

## Canonical math-family architecture
The active system separates three jobs:

1. `_question_structure/catalogs/math_question_family_registry.json` — one canonical definition per reusable mathematical task family.
2. `_question_structure/catalogs/math_course_family_maps.json` — maps those families into grade/course and topic browsing locations without duplicating the family definition.
3. `_question_structure/catalogs/math_worksheet_generator_bank.json` and this tool's `question_structure_catalog.json` — generated compatibility/browse files, not independent authorities.

Each canonical family locks the evidence job, student action, allowed response/representation modes, concise prompt architecture, validity rules, answer rule, render route, parallel invariants/variation, and QA gates.

`direct_concise` is the default worksheet wording profile. Functional context remains when it changes the mathematics or the interpretation; decorative context does not.

Teacher-supplied and external worksheet references are used only to infer useful task structures, representations, parameter properties, and coverage. Source questions are never stored or copied into the family registry.

Run `python Tools/build_math_question_catalogs.py` from the `memories` repo root after changing the canonical registry or course maps. The script validates references and regenerates the derived worksheet catalogs.
