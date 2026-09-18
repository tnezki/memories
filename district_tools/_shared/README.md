# District Tools Shared Contracts

This folder contains cross-tool **contracts and standards**, not shared runtime application code.

The district tools started as independent pilots. After the Grading & Evidence and Tiered Task tools repeated the same lessons around MathJax, graph accuracy, real diagrams, locked CSS, PDF QA, self-contained ZIPs, and conflict handling, those behaviors became stable enough to promote into a shared standard.

## Current shared authority

- `DISTRICT_RESPONSE_BUILD_STANDARD.md` - common response-build rules for MathJax, grapher use, diagrams/visuals, locked CSS, conflict precedence, package integrity, PDF checks, and QA.

## Adoption pattern

A tool that uses the shared standard should:

1. Keep its own UI, request schema, tool-specific contract, CSS, and browser-side ZIP builder inside its tool folder.
2. Package a snapshot of the shared standard into each request ZIP under `response_contract/`.
3. Record the shared-standard version in `request.json` and `data/qa.json`.
4. Let tool-specific HARD requirements add to the shared standard, but not silently weaken it.
5. Keep its exact CSS snapshot local to the tool. Do not create a shared runtime CSS dependency that could change multiple classroom tools unexpectedly.

This gives district/course tools consistent quality without coupling their working interfaces or print layouts.
