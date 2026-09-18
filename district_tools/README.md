# District Tools

District Tools is the home for cross-course teacher utilities that package a complete request for ChatGPT and ask for a self-contained response package.

## Organization pattern

The directory uses a **tool capsule + registry + shared contract** pattern:

- `index.html` is the district landing page.
- `tool_registry.json` owns landing-page metadata and categories. Future tools should normally require only a new tool folder plus one registry entry; the landing page should not need to be redesigned each time.
- Each tool lives in its own folder and owns its UI, request schema, tool-specific build contract, locked response CSS, README, and browser-side request ZIP builder.
- `_shared/` contains cross-tool response standards only. It does **not** contain shared runtime JavaScript or CSS that could break several working tools at once.
- Tools package the shared standard into their request ZIP when they adopt it, so the build remains self-contained after download.
- Tool-specific CSS remains versioned and locked inside the owning tool. Shared standards define common quality expectations without forcing every classroom artifact into the same layout.

## Why the shared contract exists

The first district tools independently exposed the same recurring build lessons:

- Math notation needs a real MathJax render-and-check workflow.
- Mathematical graphs need an accurate grapher/plotting path rather than prose or decorative sketches.
- Referenced diagrams and instructional visuals must actually exist.
- Finished PDFs need visual QA, not merely file creation.
- Locked CSS keeps response packages visually consistent from run to run.
- Structured teacher choices need a clear precedence order so free-form notes do not create hidden contradictions.
- Every request should be self-contained and every response should have one obvious `CLICK_ME.html` entry point.

Those stable behaviors are now captured in `_shared/DISTRICT_RESPONSE_BUILD_STANDARD.md` for new/adopting tools.

## Scope

`district_tools/` is for tools intended to work across courses or departments. Course-specific tools should normally remain in the appropriate course repository, but they can reuse the same architecture: simple teacher controls -> self-contained request ZIP -> one response ZIP -> `CLICK_ME.html`.

## Current tools

- Grading & Evidence Control Panel - pilot. It already carries its own mature Math/visual/QA contract; migrate it to the shared standard deliberately during a future grading-tool revision rather than destabilizing a working pilot.
- Tiered Task Tool - pilot. It packages the shared response-build standard plus its Tiered Task-specific contract and locked CSS.

## Request-builder convention

A district request builder should:

1. Keep teacher-facing inputs simple.
2. Package teacher choices, optional source files, the applicable shared standard, and the full tool-specific response/build contract into the request ZIP.
3. Require no separate prompt after the request ZIP is uploaded.
4. Ask for one authoritative response ZIP with a clear `CLICK_ME.html` entry point.
5. Keep output styling/contracts versioned inside the owning tool folder and copy locked CSS exactly into the response.
6. Fail clearly when required teacher inputs are missing instead of silently inventing them.
7. Record conflicts, rendering checks, link checks, CSS hashes, and PDF QA in the response's QA record.
