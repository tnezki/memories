# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable math question families.

## Current pilot coverage
- Lower Elementary Math
- Grade 4 Math
- Grade 5 Math
- Grade 7 Math — Ratios & Proportional Relationships
- other listed courses may use a custom topic + generic families until their catalogs are added

## Workflow
1. Choose course and topic.
2. Search/select question structures.
3. Choose question count, practice profile, number domains, and 1-4 parallel versions.
4. Set initial workspace and graph/diagram scale.
5. Click **Create Worksheet Request ZIP**; the ZIP downloads immediately.
6. Upload that request ZIP to ChatGPT. It runs automatically and returns one response ZIP.
7. Unzip the response and open `CLICK_ME.html`.

The finished `CLICK_ME.html` exposes only the adjustable worksheet and optional answer key. Internal QA stays hidden.

## Canonical question design
The request packages the current `_question_structure/QUESTION_STRUCTURE_CORE.md`, `_question_structure/catalogs/math_worksheet_generator_bank.json`, and `_question_structure/guides/parallel_family_rules.md`. Teacher-supplied reference worksheets are used only to infer original generator structures; source questions are never copied into the bank.
