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

## Response package

The requested response contains:

- `CLICK_ME.html`;
- a one-page landscape student Tiered Task Card in HTML/PDF;
- a Teacher Guide / Evidence Guide in HTML/PDF;
- locked response CSS;
- graph/visual assets when required;
- `data/request.json` and `data/qa.json`.

## District-tools organization

This tool follows the district **tool capsule** pattern: it owns its own UI, request schema, response contract, CSS, and README. `../tool_registry.json` controls how it appears on the district landing page. That keeps future pilots easy to add without forcing existing tools to share implementation code prematurely.

## Privacy

The page packages selected files locally in the browser. It does not upload them by itself. Teachers remain responsible for following district policy for any student or protected data they later upload to an AI service.
