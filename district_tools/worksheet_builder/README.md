# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable math question families.

## Current pilot coverage
- Lower Elementary Math
- Grade 4 Math
- Grade 5 Math
- Grade 7 Math — Ratios & Proportional Relationships
- other listed courses may use generic/custom families until their catalogs are added

## Workflow
1. Check one or more grade/course filters.
2. Choose 1-4 parallel versions, a broad difficulty profile, two-column vs one-column pages, and whether to include the answer key.
3. Browse topic cards or search across the selected grade levels.
4. Use the magnifying-glass **Preview** control beneath a skill's quantity counter to open a complete representative student problem. Visual families include their representative graph, table, model, or figure in the preview.
5. Check exact question structures. Every checked structure starts at **1 question**; use the `− / +` controls to change its quantity.
6. The worksheet question count is derived automatically from the selected blueprint. There is no separate question-count, practice-mode, builder-layout-slider, request-summary, or teacher-notes section.
7. Review the **Selected questions** tray, then click **Create Worksheet Request ZIP**; the ZIP downloads immediately.
8. Upload that request ZIP to ChatGPT. It runs automatically and returns one response ZIP.
9. Unzip the response and open `CLICK_ME.html`.

The finished `CLICK_ME.html` exposes only the adjustable worksheet and optional answer key. Internal QA stays hidden.

The finished adjustable worksheet keeps per-version/per-problem controls. Workspace can be collapsed to **0%** or expanded through **1200%**, allowing a selected problem to grow to approximately a full printable page when needed. Graph/diagram sizing remains independently adjustable.

## Canonical question design
The request packages the current `_question_structure/QUESTION_STRUCTURE_CORE.md`, `_question_structure/catalogs/math_worksheet_generator_bank.json`, and `_question_structure/guides/parallel_family_rules.md`. Teacher-supplied reference worksheets are used only to infer original generator structures; source questions are never copied into the bank.

The selected-family list is the authoritative worksheet blueprint. For parallel forms, every version preserves each selected family's I Can/evidence architecture and requested quantity while varying legitimate parameters.
