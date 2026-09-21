# District Resource Builder - Pilot

A district-wide request builder that turns a small set of teacher inputs into one self-contained request ZIP for a finished classroom resource.

## Teacher flow

1. Select the resource type.
2. Enter resource name, subject/course, **grade level**, and the I Can statements / learning targets in one multiline field.
3. Set the visible resource-specific options.
4. Optionally attach **multiple supporting source files**.
5. Open **Advanced options** only when you need extra constraints, context, standards, reading/access targets, design emphasis, or special directions.
6. Click **Build Request ZIP**.
7. Upload that ZIP to ChatGPT. No separate build prompt is required.
8. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

## I Can statement entry

Use one multiline field for I Can statements / learning targets. **Recommend 1-4, but do not enforce a maximum.** Teachers may paste a bulleted list or enter one target per line; the browser removes common bullet/number prefixes and stores each nonblank target separately in `request.json`. More than four targets are valid when they form one coherent instructional set.

## Why grade level stays visible

Grade level is required because the same learning target can imply very different work at different grades. The build contract requires grade level to influence rigor, representations, number choices, vocabulary, reading load, explanation expectations, and scaffolding.

## Advanced options

Advanced options are optional refinements, not baseline quality switches. Accuracy, clarity, accessibility, and grade appropriateness are always required.

The former Design Approach defaults are no longer pre-checked. Selecting a box now means **emphasize this beyond the baseline**.

Advanced contains:

- time / length constraint;
- target reading / access level;
- prior-learning context;
- standards / framework;
- learning-emphasis priorities;
- design-approach priorities;
- special directions / what to avoid.

`Unit / topic` has been removed from the teacher form. Resource name + subject/course + grade level + learning targets provide the primary context; additional placement/context can be supplied under Advanced when it actually matters.

## Multiple source files

The source picker supports multiple files. Every selected file is packaged under `sources/` and listed in `request.json`. The response contract tells the build to treat all listed files as available supporting sources rather than assuming a single source.

## Deterministic build architecture

The model should spend its effort on instructional judgment and new content. Repeatable mechanics are packaged in the request:

- `resource_preflight.py` verifies contracts, hashes, sources, locked styles, and graph dependencies before content work begins.
- `resource_finalize.py` copies locked CSS/request metadata and creates the standard `CLICK_ME.html` dashboard.
- `resource_qa.py` performs repeatable file/link/hash/PDF/graph-provenance QA.
- the canonical graph runtime is resolved from `Tools/MANIFEST.json` and packaged into the request.
- `DISTRICT_GRAPH_RENDERING_STANDARD.md` controls graph geometry/style/provenance.
- `RESOURCE_BUILD_EXECUTION.md` prevents recreation of mechanical scripts and repeated QA work.

Missing packaged core dependencies fail closed. A response run should not search GitHub/the web for the renderer, graph tool, CSS, contracts, or QA utilities.

## Locked response styles

The request carries exact snapshots of:

- `dashboard_styles.css`
- `resource_styles.css`

Their SHA-256 hashes are recorded in `request.json`. The deterministic finalizer copies them byte-for-byte into the finished response.

## Resource profiles

Current profiles:

1. Worksheet / Practice
2. Differentiated Worksheet
3. Extension Activity
4. Formative Assessment
5. Rubric
6. Lesson Plan / Lesson Outline
7. Presentation / Lesson Slides
8. Stations
9. Curriculum / Unit Outline
10. Blooket Review
11. Other / Custom Resource

`resource_profiles.json` owns the profile catalog and resource-specific controls so individual profiles can evolve without crowding the teacher-facing form.
