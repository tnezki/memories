# District Tools

District Tools is the home for cross-course teacher utilities that package a complete request for ChatGPT and ask for a self-contained response package.

## Organization pattern

The directory uses a **tool capsule + registry + shared standards** pattern:

- `index.html` is the district landing page.
- `tool_registry.json` owns landing-page metadata and categories.
- Each tool lives in its own folder and owns its UI, request schema, tool-specific build contract, locked response CSS, README, and browser-side request ZIP builder.
- `_shared/` contains cross-tool standards. It does **not** contain shared runtime JavaScript or CSS that could break several working tools at once.
- Tool-specific CSS remains versioned and locked inside the owning tool.

## Shared standards for new/rebuilt tools

New or substantially rebuilt district request tools should resolve these authorities:

1. `_shared/DISTRICT_TOOL_BUILD_STANDARD.md` — teacher workflow and request-builder behavior.
2. `_shared/DISTRICT_RESPONSE_BUILD_STANDARD.md` — response quality, MathJax, visuals, locked CSS, PDF/print QA, conflict handling, and internal QA.
3. `_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md` — registered graph-tool routing and teacher-approved graph print weights when mathematical graphs are possible.

Tool-specific contracts may add requirements but should not silently weaken these shared behaviors.

Existing pilot tools may still have older dashboard/output details until their next targeted revision; the shared standards define the direction for new and rebuilt tools.

## Default teacher workflow

The normal district-tool flow is intentionally simple:

**simple teacher controls -> one click downloads the self-contained request ZIP -> upload the ZIP with no extra prompt -> one response ZIP -> open `CLICK_ME.html`**

`CLICK_ME.html` should show only teacher-use actions. Internal QA/request/contracts remain in the package but are not normal teacher dashboard buttons. Avoid duplicate HTML/PDF buttons for the same logical resource when the HTML is already the adjustable/printable source; direct PDFs remain appropriate when PDF is itself the distinct workflow, such as a combined print packet.

## Why the shared standards exist

The first district tools repeatedly exposed the same build lessons:

- Math notation needs a real MathJax render-and-check workflow.
- Mathematical graphs need the current registered grapher rather than improvised coordinate SVG.
- Full-size Cartesian graphs need consistent print darkness.
- Referenced diagrams and instructional visuals must actually exist.
- Locked CSS keeps response packages visually consistent from run to run.
- Live sliders/selectors must change the intended artifact, not merely move on screen.
- Screen-responsive rules must not accidentally break print geometry.
- Structured teacher choices need a clear precedence order.
- Request ZIPs should run automatically without a separate copied prompt.
- Every response should have one obvious `CLICK_ME.html` entry point.
- The dashboard should expose teacher actions, not implementation files.

## Scope

`district_tools/` is for tools intended to work across courses or departments. Course-specific tools should normally remain in the appropriate course repository, but they can reuse the same architecture.

These implementation/workflow rules do not belong in a course Framework. Frameworks own course learning/evidence architecture; PMs own executable curriculum procedures; district-tool shared standards own cross-tool request/response mechanics.

## Current tools

- Grading & Evidence Control Panel - pilot.
- Tiered Task Tool - pilot.
- District Resource Builder - pilot.
- Math Worksheet Builder - pilot. The initial catalog pilots Grade 7 Ratios & Proportional Relationships and is designed to expand from Grade 6 through Calculus.

## Request-builder convention

A district request builder should:

1. Keep teacher-facing inputs simple.
2. Use one primary build button that directly starts the request ZIP download.
3. Package teacher choices, optional sources, shared standards, the tool-specific response/build contract, locked CSS, and needed deterministic tools into the request ZIP.
4. Require no separate prompt after the request ZIP is uploaded.
5. Ask for one authoritative response ZIP with a clear `CLICK_ME.html` entry point.
6. Hide internal QA/contract files from the normal teacher dashboard while still producing and validating them.
7. Use the current registered graph tool and shared graph-rendering standard when mathematical graphs are possible.
8. Fail clearly when required teacher inputs are missing instead of silently inventing them.
9. Functionally test request download, live controls, print behavior, links, and packaging before release.

## Generic profile -> specialized tool

Use the Resource Builder for broadly useful, configurable classroom artifact types. When one profile develops enough specialized pedagogy, UI, output structure, or recurring teacher workflow, promote it into its own tool capsule rather than making the generic builder increasingly complex.
