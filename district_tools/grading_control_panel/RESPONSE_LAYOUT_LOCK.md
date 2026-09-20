# Grading Response Gold Layout Lock

STATUS: HARD / REQUIRED  
VERSION: district-grading-response-layout-lock/1.0  
DATE: 2026-09-20  
LOCKED CSS SHA-256: `59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df`

## Purpose
The 2026-09-20 Precalculus Circuit Training grading response is the visual baseline for this tool. Future grading runs must preserve that response system instead of inventing a new layout on each run.

`response_contract/styles.css` is the canonical response stylesheet. The response must copy it byte-for-byte to `assets/styles.css`; `data/qa.json` must record the SHA-256 above and PASS only when it matches.

## Stable surfaces - DO NOT REDESIGN
Keep the current gold layout/markup hierarchy for all of these unless a later teacher-approved contract explicitly changes one:

- `CLICK_ME.html`
- individual student reports
- class overview
- individual practice packets
- combined report/practice print documents
- Common Worksheet / Review + Extension
- Common Worksheet Teacher Guide
- Stations and station answer key
- Review All Questions pages
- Set 1 Teacher Guide
- Print Presentation two-up pages
- Cut-Apart Question Cards

Do not change hero sizes, card shapes, button treatment, typography hierarchy, spacing system, report boxes, dashboard organization, station styling, or card-deck styling simply because another layout seems cleaner.

## Approved Set 1 exceptions in this revision
Only these Set 1 surfaces intentionally differ from the previous run:

1. `print/question_set/index.html` becomes the Algebra-style **Activity Options** page modeled on `algebra/activities/u1_1_act1/u1_1_act1.html`, adapted to one Set 1.
2. `presentation.html` becomes the Algebra-style **Set 1 Questions & Solutions** projection deck (question page followed by solution page), not the prior Back/Next presentation shell.
3. **Find Someone Who** adopts the current Student Set worksheet look: compact two-column problem flow, with a partner signature line and workspace added to each problem.
4. Find Someone Who gets the Worksheet Builder-style screen-only left control rail for workspace and graph/diagram size.
5. Cartesian construction graphs use the current canonical district graph tool and the worksheet/Quick-Check coordinate visual rules in the District Graph Rendering Standard.

Everything else remains visually frozen.

## HTML/CSS discipline
- Do not add page-local `<style>` blocks that restyle shared gold classes.
- Do not invent alternate dashboard/card/page systems.
- Use the class structures named by `COMMON_PRACTICE_GUIDE.md` and this lock.
- Content may change from one evidence set to another; the shell/layout does not.
- If content is longer, solve it with natural pagination/content fitting, not a new design language.
- Graph/workspace controls may set CSS custom properties or inline values needed for sizing; they may not restyle the page.

## QA
Before delivery, verify:

- `assets/styles.css` exactly matches packaged `response_contract/styles.css` and SHA-256 `59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df`;
- every stable surface above still uses the gold class hierarchy;
- only the five approved exceptions changed layout;
- Cut-Apart Cards remain visually unchanged from the gold run;
- no unapproved page-local CSS overrides the gold stylesheet.
