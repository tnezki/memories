# District Tools

District Tools is the home for cross-course teacher utilities that package a complete request for ChatGPT and ask for a self-contained response package.

## Organization pattern

The directory uses a small **tool capsule + registry** pattern:

- `index.html` is the district landing page.
- `tool_registry.json` owns landing-page metadata and categories. Future tools should normally require only a new tool folder plus one registry entry; the landing page should not need to be redesigned each time.
- Each tool lives in its own folder and owns its UI, request schema, build contract, locked response styling, README, and browser-side request ZIP builder.
- Tools should avoid depending on implementation files from another tool. This keeps one pilot from breaking another.
- Do not create a `_shared/` implementation layer until the same contract/code is genuinely repeated across several tools. When that happens, shared pieces can be promoted deliberately instead of coupling pilots too early.

## Scope

`district_tools/` is for tools intended to work across courses or departments. Course-specific tools should normally remain in the appropriate course repository, but they can reuse the same design pattern: simple teacher controls -> self-contained request ZIP -> one response ZIP -> `CLICK_ME.html`.

## Current tools

- Grading & Evidence Control Panel - pilot
- Tiered Task Tool - pilot

## Request-builder convention

A district request builder should:

1. Keep teacher-facing inputs simple.
2. Package teacher choices, optional source files, and the full response/build contract into the request ZIP.
3. Require no separate prompt after the request ZIP is uploaded.
4. Ask for one authoritative response ZIP with a clear `CLICK_ME.html` entry point.
5. Keep output styling/contracts versioned inside the owning tool folder.
6. Fail clearly when required teacher inputs are missing instead of silently inventing them.
