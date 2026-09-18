# Tiered Task Tool - Pilot

A district-wide request builder for one integrated DOK 1-4 Tiered Task Card plus a Teacher Guide / Evidence Guide.

## Teacher flow

1. Enter the assignment/task name, subject/course, unit/topic, and at least one I Can statement.
2. Optionally add teacher name, grade level, target reading/access level, time available, work mode, research policy, teacher constraints, and source files.
3. Select the student product types that are allowed. The teacher can leave many choices available or narrow the list.
4. Click **Build Request ZIP**.
5. Upload that ZIP to ChatGPT. The ZIP contains the complete build contract; no separate PM/prompt is required.
6. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

## Research-informed design rules

The builder contract treats DOK as cognitive complexity rather than difficulty or verb matching.

- DOK 1: recall/reproduction.
- DOK 2: skills/concepts with application and decisions.
- DOK 3: strategic, non-routine reasoning with justification/evidence.
- DOK 4: genuine extended thinking through investigation, synthesis, design, modeling, transfer, or iterative development.

The tool creates exactly one card. Up to four I Can statements are treated as one coherent target set, not as four separate cards.

A target reading/access level changes wording and accessibility but may not lower the academic target, DOK, or evidence standard.

Product choices are controlled by teacher checkboxes. The intellectual evidence stays constant across product formats.

## Hardened response-build rules

Tiered Task requests package two executable contracts:

- `TIERED_TASK_GENERATION_CONTRACT.md` - the tool-specific DOK/task-card requirements;
- `DISTRICT_RESPONSE_BUILD_STANDARD.md` - the shared district rules for MathJax, accurate graphs, diagrams/visuals, locked CSS, conflict handling, PDFs, relative links, and QA.

The shared standard is copied into every request ZIP, so a later build does not depend on remembering another chat or retrieving a live repository file.

### MathJax

- Mathematical expressions use valid TeX/MathJax rather than improvised italic HTML.
- PDF generation happens only after MathJax finishes typesetting.
- Raw TeX, clipped equations, or missing symbols fail QA.

### Graphs

- A required mathematical graph is generated with a dedicated grapher when available, otherwise by a deterministic accurate plotting method.
- Mathematical graphs are not fabricated with a generative image model.
- Required axes, scale, labels, units, and relationships are checked.

### Diagrams and visuals

- If a prompt depends on a diagram/figure/setup, the real visual must be present.
- When drawing the diagram is itself the assessed skill, the response does not give away the completed answer; it may provide a neutral setup sketch/grid when useful.
- Generated graphs live under `assets/graphs/`; other instructional visuals live under `assets/visuals/`.

### Locked CSS

The current classroom layout was validated with the Physics Newton's Laws pilot and is intentionally preserved.

- The student card remains one readable letter-landscape page.
- The dashboard/teacher guide keep the existing restrained district blue/navy visual language.
- The request includes exact CSS snapshots, versions, and SHA-256 hashes.
- The response must copy those CSS files byte-for-byte and record the expected/actual hashes in QA.
- If content does not fit, the builder improves wording/layout within the contract instead of silently replacing the CSS or shrinking text until it is unreadable.

## Conflict policy

The request package now has an explicit authority order so later runs do not improvise when instructions disagree. HARD response/build rules come first, then structured teacher choices in `request.json`, then tool defaults, teacher notes, source files, and finally model inference. Resolved and unresolved conflicts are recorded in `data/qa.json`.

This is especially important for product selections, work/research modes, source requirements, one-page layout, math/visual rendering, and locked CSS.

## Response package

The requested response contains:

- `CLICK_ME.html`;
- a one-page landscape student Tiered Task Card in HTML/PDF;
- a Teacher Guide / Evidence Guide in HTML/PDF;
- locked response CSS;
- graph/visual assets when required;
- `data/request.json` and completed `data/qa.json`.

`CLICK_ME.html` keeps the four prominent student/teacher resource links and also exposes the completed QA record without turning QA into a competing primary action.

## Required delivery line

The user-facing response that returns the completed ZIP ends with exactly:

> Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.

## District-tools organization

This tool follows the district **tool capsule + shared contract** pattern. It owns its own UI, request schema, Tiered Task contract, locked CSS, and browser-side ZIP builder. Cross-tool quality rules live in `../_shared/`, but runtime JavaScript/CSS are not shared across tools. That keeps future tools consistent without allowing a change in one pilot to unexpectedly break another.

## Privacy

The page packages selected files locally in the browser. It does not upload them by itself. Teachers remain responsible for following district policy for any student or protected data they later upload to an AI service.
