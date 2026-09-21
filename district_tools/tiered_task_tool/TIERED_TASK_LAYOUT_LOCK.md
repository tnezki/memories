# Tiered Task Layout Lock

STATUS: HARD / GOLD LAYOUT
VERSION: district-tiered-task-layout-lock/1.0
DATE: 2026-09-20

The current Tiered Task student-card and Teacher Guide visual system is approved and must not drift between runs.

## Locked authorities

- `response_contract/task_card_styles.css` is the byte-exact student-card style authority.
- `response_contract/guide_styles.css` is the byte-exact Teacher Guide / dashboard style authority.
- The SHA-256 values in `request.json -> locked_styles` are authoritative for the request.
- A response may copy these files to their required response paths; it may not regenerate, restyle, or approximate them.

## Student card geometry - HARD

- One US Letter landscape page.
- Existing header, target strip, DOK 1-4 four-column structure, product bar, typography, spacing, borders, and print geometry remain as defined by the locked CSS.
- New content must be edited to fit the approved layout. Do not solve overflow by creating a different card design, changing page size/orientation, or shrinking text below the locked style.

## Teacher Guide / dashboard - HARD

- Preserve the current restrained district blue/navy styling, cards, typography hierarchy, spacing, and print behavior defined by `guide_styles.css`.
- Do not invent a third visual system or add page-local CSS that overrides the locked appearance.

## Allowed changes

Content changes are expected: task title, grade/course metadata, I Can statements, DOK tasks, product choices, answers/evidence guidance, graphs/diagrams, and teacher notes may change. Generated graph/visual assets may be resized within the existing layout rules.

## QA / fail-closed rule

- Preflight must verify this layout-lock file and both CSS dependencies are packaged.
- Locked CSS hashes must match before PASS.
- If the approved one-page student card cannot fit legibly after content tightening, fail/flag the content-layout conflict rather than redesigning the template.
