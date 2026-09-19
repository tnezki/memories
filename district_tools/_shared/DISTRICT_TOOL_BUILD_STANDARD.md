# District Tool Build Standard

STATUS: REQUIRED FOR NEW OR REBUILT DISTRICT REQUEST TOOLS
VERSION: district-tool-build-standard/1.0
DATE: 2026-09-18

This standard owns the common teacher workflow for cross-course district request builders. Tool-specific contracts may add controls and outputs, but they should not make the basic workflow more complicated without a clear instructional reason.

## 1. Teacher workflow - HARD

The default district-tool workflow is:

1. Teacher opens the district tool.
2. Teacher makes simple structured choices and optionally attaches sources.
3. Teacher clicks ONE primary action such as `Create Request ZIP`.
4. That click packages the request and immediately starts the browser download. Do not require a second `Download Request ZIP` click.
5. Teacher uploads the request ZIP to ChatGPT.
6. The packaged request runs automatically; no separate PM prompt or copied instruction is required.
7. ChatGPT returns exactly ONE response ZIP.
8. Teacher unzips the response and opens `CLICK_ME.html`.

A district tool should not require the teacher to understand implementation contracts, manifests, QA schemas, graph-tool dependencies, CSS hashes, or package internals in order to use it.

## 2. Self-contained request package - HARD

Each request ZIP must carry enough authority to run without a second prompt. Include, as applicable:

- `REQUEST_READ_ME_FIRST.md` with automatic-run instructions;
- `request.json` with structured teacher choices;
- the tool-specific response/build contract;
- the current shared district response standard;
- the current shared graph-rendering standard when mathematical graphs can be required;
- locked response CSS snapshots and expected hashes;
- required deterministic tools/dependencies, or exact packaged copies when the tool contract calls for them;
- selected profile/catalog snapshots;
- teacher notes and attached sources.

Structured controls in `request.json` outrank conflicting free-form notes.

## 3. One-click request download - HARD

The primary build button must directly create and download the request ZIP in the same user action.

Allowed implementation:

- create Blob;
- create a temporary `<a download>`;
- click it programmatically;
- revoke the Blob URL after a short delay;
- show a short status such as `Request package created. Download started.`

Do not expose an unnecessary intermediate ready state requiring another teacher click.

## 4. Response package - HARD

The request must ask for one authoritative response ZIP with `CLICK_ME.html` as the teacher entry point unless the tool has an explicitly approved exception.

The response may contain internal contracts, QA records, request copies, generated assets, and supporting files, but `CLICK_ME.html` should surface only the things the teacher actually needs to open, print, or use.

### Teacher-facing simplicity rule

- Do not expose `data/qa.json`, `request.json`, CSS files, contracts, manifests, or implementation assets as normal dashboard actions.
- Do not create duplicate HTML/PDF buttons for the same logical resource when the HTML is the adjustable/printable source. Prefer one clear action such as `Open adjustable worksheet`.
- A direct PDF action is appropriate when PDF is itself the distinct teacher workflow, such as a combined duplex print packet.
- Keep teacher guides/answer keys as one obvious action each rather than separate HTML/PDF choices unless the tool has a real reason for both.

QA remains required even when it is hidden from the normal teacher workflow.

## 5. Locked presentation and print behavior - HARD

- Each tool owns versioned locked response CSS.
- Teacher-facing controls may be simple; implementation complexity belongs in contracts.
- If a finished HTML resource has live print/layout controls, those controls must actually change the rendered artifact and must disappear from print.
- Responsive screen rules must not accidentally override print geometry.
- Verify the actual browser print mode, not only the screen preview.

## 6. Math / graph capable tools - HARD

If the tool may generate mathematical graphs, use `_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md` and package the required graph authority into the request.

Do not let each district tool reinvent graph styling, axis behavior, line weights, or a replacement graph renderer.

## 7. GitHub Pages publishing rule - HARD

GitHub Pages/Jekyll may not publish underscore-prefixed folders such as `district_tools/_shared/`.

A browser tool may not assume those paths are directly fetchable from the published site. Use one of these approaches:

- package a local published bridge/copy;
- fetch the canonical repository text through the GitHub Contents API;
- or another deterministic path that has been tested on the deployed site.

When changing browser JavaScript or CSS, use a cache-busting query/version so the deployed tool does not silently run a stale asset.

## 8. Functional QA for the request builder - HARD

Before declaring a district-tool change ready, verify the actual interaction, not merely the code path:

- required controls enable/disable correctly;
- one click starts the request ZIP download;
- request ZIP contains every declared contract/style/tool dependency;
- paths resolve after unzip;
- any live sliders/selectors change the intended target and no unintended target;
- print preview preserves the requested layout;
- tool still works from the deployed GitHub Pages path.

## 9. Ownership boundary

This standard is implementation/workflow architecture. It does not belong in a course Framework and does not change course learning targets, evidence architecture, or instructional progression.
