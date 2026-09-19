# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable math question families.

## Current catalog coverage
- Lower Elementary Math
- Grade 4 Math
- Grade 5 Math
- Grade 6 Math
- Grade 7 Math
- Grade 8 Math
- Algebra 1 through Calculus are the next planned course maps as their reference sets are incorporated.

## Family quality rule
The family name/summary/evidence job is planning metadata, not student wording. A generated item must be a concrete, solvable problem instantiated from the canonical family generator contract.

The builder enriches its teacher-facing catalog at runtime from `_question_structure/catalogs/math_question_family_registry.json`. This means selected-family records placed into the request ZIP carry the canonical generator contract and hard quality gates rather than only a short topic summary.

Teacher previews use `family_preview_specimens.json`, a published mirror of `_question_structure/catalogs/math_family_preview_specimens.json`.

- A curated preview shows one complete, solved representative morphology specimen.
- A required graph/diagram/table must be the correct semantic visual for that family.
- A system-of-equations family shows two graphed relations, not a generic coordinate-grid figure.
- A transformation family shows the source and image figures when the task requires mapping between them.
- A nonvisual algebra family does not receive a decorative graph.
- If a family has not received a curated specimen yet, Preview displays **Preview pending quality review** rather than inventing a generic prompt or visual.

Preview specimens demonstrate architecture only; generated worksheets use new legal values/context and must not copy the specimen verbatim.

## Workflow
1. Check one or more grade/course filters.
2. Choose 1–4 parallel versions, a difficulty profile, one/two-column pages, and optional answer key.
3. Browse or search family cards.
4. Use the magnifying-glass Preview control to inspect a curated complete example when available.
5. Check exact families; each begins at 1 question and has its own − / + quantity control.
6. Review the Selected Questions tray.
7. Click **Create Worksheet Request ZIP**. The ZIP downloads immediately.
8. Upload that request ZIP to ChatGPT; it runs automatically and returns one response ZIP.
9. Open `CLICK_ME.html`.

## Finished worksheet controls
The adjustable worksheet keeps controls for the exact Version + Problem slot:
- Version and Problem selectors;
- **↻ New Question** directly below the Problem selector;
- a small `Question 1 of 3` status;
- 0%–1200% workspace sizing;
- graph/diagram sizing;
- reset selected-problem layout;
- matching answer key when requested;
- print.

Each canonical problem slot contains three original, solved candidates from the same family: the initial question plus two alternates. Refresh cycles only that selected slot and preserves its workspace/visual sizing. It never swaps to another family.

The active candidate map is carried in self-contained page state so reloads can restore it. When an answer key is requested, **Open matching answer key** transfers that same state so the key always matches any questions the teacher refreshed before printing.

The finished worksheet uses the registered graph tool/print standards where applicable.
