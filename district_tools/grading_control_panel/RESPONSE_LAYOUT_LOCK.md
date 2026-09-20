# Grading Response Gold Layout Lock

STATUS: HARD / REQUIRED  
VERSION: district-grading-response-layout-lock/1.3  
DATE: 2026-09-20  
LOCKED CSS SHA-256: `2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad`

## Purpose
The tested 2026-09-20 Precalculus Circuit Training grading response is the visual baseline for this tool. Future runs preserve that response system instead of inventing a new layout on each run.

`response_contract/styles.css` remains the canonical visual stylesheet. Stable HTML is now generated only by packaged `response_builder.py`; the model may not reconstruct these pages. `runtime.css` and `runtime.js` own only page-preview/pagination/control behavior.

## Stable surfaces - DO NOT REDESIGN
Keep the current gold layout/markup hierarchy for these unless a later teacher-approved contract explicitly changes one:

- `CLICK_ME.html` overall dashboard hierarchy and button treatment;
- **Individual Student Reports & Practice** dashboard section;
- individual student report pages;
- **Class Data** / class overview page;
- individual practice question styling;
- Common Worksheet visual language;
- Common Worksheet Teacher Guide;
- Stations landing page, student stations, and station answer key;
- Print Presentation one-problem Letter-page shell;
- Cut-Apart Question Cards.

Do not change hero sizes, card shapes, typography hierarchy, border/radius system, dashboard student-card grid, class-summary cards, report boxes, station styling, or cut-card styling because another design seems cleaner.

## Approved functional/layout changes in this revision
These changes are intentional and are now part of the gold system:

1. Top quick actions **Print All Student Reports** and **Print All Individual Practice** open combined printable HTML rather than generated PDFs. **View Scanned Student Work** remains the preserved scan/PDF.
2. Generated classroom/teacher print products are HTML-first. Duplicate generated PDFs are removed unless explicitly requested.
3. Common Worksheet keeps its current visual design but gains Worksheet Builder-style left controls plus true Letter-size screen page previews and deterministic repagination.
4. Find Someone Who links to the exact Common Worksheet HTML; it does not own a separately titled/restyled worksheet.
5. `print/common_review_extension/teacher_guide.html` is the one approved teacher review layout for the shared Common Worksheet / Set 1 questions. Duplicate Review All pages and duplicate Set 1 teacher guides are removed.
6. The Activity Options page begins with **Teacher / Print Utilities** and the Set 1 focus line, then **Classroom Participation Structures** with Shared Prompt / Partner and Card-Based subgroups.
7. **Speed Dating Math** is renamed **Speed Dating** and **Mathematical Hot Seat** is renamed **Hot Seat**.
8. Card-based structures are Quiz-Quiz-Trade, Fan-N-Pick, Mix-Pair-Share with Cards, and Inside-Outside Circle with Cards. They all reuse the one locked Cut-Apart Question Cards deck.
9. Set 1 classroom presentation uses the approved rounded-panel visual language with one Letter page per problem: question in the top half, Answer + Teacher move + Student discourse move in the bottom half. It gains left layout controls and real page previews.
10. Print Presentation uses the same locked one-problem Letter template as the classroom Set 1 view: question top half; Answer + Teacher move + Student discourse move bottom half; live spacing/graph controls; true page preview.
11. Combined Individual Practice gains true Letter page previews, spacing/workspace controls, graph/diagram controls, and deterministic repagination. Combined Student Reports gains true page previews and browser Print without a duplicate PDF.
12. Stations keep their current look but expose HTML Student Stations + HTML Answer Key only.
13. Supported Cartesian graphs use the current canonical district graph tool and District Graph Rendering Standard; no page-local CSS may restyle graph strokes away from the standard.

## HTML/CSS discipline
- Existing baseline CSS remains unchanged except for appended/targeted classes needed for the approved controls/page-preview/set-half layout above.
- Do not add page-local `<style>` blocks that restyle shared gold classes.
- Do not invent alternate dashboard/card/page systems.
- Content may change from run to run; the shell/layout does not.
- Longer content is handled with natural deterministic pagination, not a new design language.
- Workspace/spacing/graph controls may set CSS custom properties or inline values needed for sizing; they may not restyle the page.
- Cut-Apart Cards remain visually unchanged.

## Locked page-preview behavior
Adjustable HTML uses explicit 8.5 x 11 in page containers on screen and print. Screen shows white pages against the gray preview background with visible boundaries. Browser Print uses those same page containers. Controls are screen-only and disappear in print.

## QA
Before delivery verify:

- `assets/styles.css` exactly matches packaged `response_contract/styles.css` and SHA-256 `2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad`;
- every stable surface still uses the gold class hierarchy;
- only the approved changes above alter structure;
- duplicate Review All pages are absent;
- generated duplicate classroom PDFs are absent;
- Find Someone Who resolves to the Common Worksheet;
- Cut-Apart Cards are unchanged visually;
- no unapproved page-local CSS overrides the gold stylesheet.


## Literal-template enforcement - HARD
The prior CSS-only lock was insufficient because a run could change HTML while keeping the stylesheet. That path is retired. The deterministic renderer is now the literal shell authority for CLICK_ME, Class Data, student reports, individual practice, Common Worksheet, Teacher Guide, Stations, Activity Options/directions, Set 1 presentation, Print Presentation, cut cards, and combined print documents. Generated HTML must not be manually edited after rendering.

Class Data uses the approved `Precalc Class Data`/Evidence Analyzed/Major Strengths/Top Actionable Patterns/Suggested Instructional Groupings hierarchy. Stations uses the long-standing approved station markup and exact locked station CSS as a literal mad-lib shell. Only data fields are injected; structure/classes/CSS are not regenerated. Activity directions are fixed per structure.
