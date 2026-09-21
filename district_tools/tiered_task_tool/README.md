# Tiered Task Tool - Pilot

A district-wide request builder for one integrated DOK 1-4 Tiered Task Card plus a Teacher Guide / Evidence Guide.

## Teacher flow

1. Enter the assignment/task name, subject/course, **grade level**, and at least one I Can statement.
2. Optionally attach **multiple supporting resources**.
3. Open **Advanced options** only when you need to change reading/access level, time, intended use, allowed product types, work mode, research policy, or teacher constraints.
4. Click **Build Request ZIP**.
5. Upload that ZIP to ChatGPT. No separate PM/prompt is required.
6. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

`Unit / topic` is no longer a teacher field. Task name + subject/course + grade level + I Can statements provide the primary context.

## Grade level stays visible

Grade level is required because identical target wording can imply very different rigor. The contract requires grade level to influence representations, number/data choices, vocabulary, reading load, explanation expectations, independence, scaffolding, and what counts as authentic DOK 3/4 work.

## Advanced options

The normal path uses broad student product choice. Advanced options contain:

- target reading/access level;
- time available;
- intended use;
- allowed product types and a custom product;
- work mode;
- research/internet policy;
- teacher directions/constraints.

Unchecked/changed product options are treated as explicit teacher restrictions. The evidence standard remains constant across product formats.

## Supporting resources

The file picker supports multiple files. Every selected file is packaged under `sources/` and listed in `request.json`.

## DOK design

The tool creates exactly one card with DOK 1, 2, 3, and 4. DOK is cognitive complexity, not difficulty or verb matching. DOK 4 requires genuine extended thinking rather than simply more work.

## Deterministic build architecture

ChatGPT should focus on instructional judgment and new content. Repeatable mechanics are packaged in the request:

- `tiered_task_preflight.py` verifies dependencies, required teacher data, hashes, sources, and graph runtime before content work;
- `tiered_task_finalize.py` copies locked CSS/request metadata and builds the standard `CLICK_ME.html` dashboard;
- `tiered_task_qa.py` performs repeatable file/link/hash/PDF checks;
- `TIERED_TASK_BUILD_EXECUTION.md` defines the fast-path execution order;
- the current canonical graph runtime is resolved through `Tools/MANIFEST.json` and packaged with the request;
- a local snapshot of `DISTRICT_GRAPH_RENDERING_STANDARD.md` prevents GitHub Pages `_shared` path failures.

Missing packaged core dependencies fail closed. A response run must not search GitHub/the web for the graph tool, locked CSS, contracts, or deterministic utilities.

## Locked response layout

The existing Physics Newton's Laws pilot remains the visual baseline:

- one readable letter-landscape student card;
- locked `task_card_styles.css`;
- locked `guide_styles.css` for dashboard/Teacher Guide;
- HTML + PDF student card;
- HTML + PDF Teacher Guide / Evidence Guide;
- completed QA record.

## Required delivery line

The completed response ends with:

> Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.
