# District Response Build Standard

STATUS: REQUIRED WHEN PACKAGED BY A DISTRICT TOOL
VERSION: district-response-build-standard/1.0

This is the shared response-quality contract for district and course request builders that create self-contained response ZIPs. Tool-specific contracts may add requirements, but they may not silently weaken this standard.

The goal is predictable, reusable output: mathematically correct notation, accurate graphs, real diagrams when needed, consistent styling, finished PDFs, clear conflict handling, and one teacher-friendly `CLICK_ME.html` entry point.

## 1. Authority and conflict resolution - HARD

Use this precedence order when instructions disagree:

1. **Safety, platform, and file-integrity requirements.**
2. **This shared response-build standard and any tool-specific requirement explicitly marked HARD.**
3. **Explicit structured teacher choices in `request.json`** such as selected products, output mode, time, work mode, or research policy.
4. **Tool-specific defaults and non-HARD guidance.**
5. **Free-form teacher notes.**
6. **Included source files for content, examples, data, and context.**
7. **Model inference or default assumptions.**

Additional rules:

- Teacher notes may refine content but may not silently override locked output structure, required QA, or locked CSS.
- Included source files are authoritative for the content they actually contain. Do not invent missing facts, quotes, data, labels, or requirements.
- A source file does not change response architecture merely because its original formatting differs from the locked response style.
- If two HARD requirements truly cannot both be satisfied, do not guess which one to ignore. Record the conflict in `data/qa.json`, set overall status to FAIL, and explain the unresolved conflict briefly.
- If a lower-priority instruction conflicts with a higher-priority instruction, follow the higher-priority instruction and record the resolved conflict in QA when it materially affected the build.
- Never resolve a conflict by omitting a required output without saying so.

`data/qa.json` must include a conflict record with:

- `conflicts.detected_count`;
- `conflicts.resolved_count`;
- `conflicts.unresolved_count`;
- `conflicts.items`, each naming the issue, competing instructions, winning authority, and resolution.

## 2. Self-contained response package - HARD

- Return the exact response structure required by the owning tool.
- `CLICK_ME.html` is the teacher entry point unless the tool contract explicitly says otherwise.
- Use local relative links for package navigation and locally generated assets.
- Do not return placeholder PDFs, empty shell files, fake links, or prose that says a missing resource will be created later.
- Before delivery, resolve every relative link after the package is assembled.
- If the response contract requires HTML and PDF versions, both must be finished and openable.
- Preserve teacher-facing simplicity. Implementation details belong in contracts and QA, not in the teacher workflow.

## 3. MathJax and mathematical notation - HARD

When mathematical notation appears, use a consistent MathJax workflow rather than improvised HTML styling.

### Authoring

- Use valid TeX with `\\( ... \\)` for inline math and `\\[ ... \\]` for display math unless the owning tool explicitly defines another MathJax delimiter convention.
- Use MathJax for expressions, equations, inequalities, vectors, exponents, radicals, fractions, subscripts, Greek letters, matrices, and other mathematical notation that benefits from typesetting.
- Use semantic math notation rather than approximating math with `<i>`, superscript text, Unicode lookalikes, or manually positioned characters.
- Put units in mathematically appropriate upright text when they are inside an expression, for example `\\(4\\,\\mathrm{m/s^2}\\)`.
- Avoid raw `$...$` delimiters unless the MathJax configuration in the finished page explicitly enables and verifies them.

### Rendering

- MathJax must finish typesetting before PDF generation.
- Prefer MathJax SVG output or another MathJax output mode that is stable in print.
- Final HTML must not show raw TeX if a viewer opens the package normally.
- A final package should not depend on a remote-only math renderer when a local or pre-rendered MathJax result can reasonably be produced. If an external runtime is unavoidable, record that dependency in QA and ensure the finished PDF is already fully rendered.
- Do not rasterize ordinary equations merely to avoid MathJax.

### QA

For every page containing math, visually inspect both HTML and the finished PDF. `data/qa.json` must record at least:

- `mathjax.pages_with_math`;
- `mathjax.rendered_and_checked`;
- `mathjax.raw_tex_visible_count`;
- `mathjax.pdf_generated_after_typeset`;
- `mathjax.external_runtime_dependency`.

PASS is not allowed if raw TeX is visible, symbols are missing, formulas are clipped, or the PDF was generated before MathJax finished.

## 4. Graphs and grapher use - HARD

If a task, answer, explanation, or source requires a mathematical graph, create or supply the actual accurate graph.

- Prefer the platform's dedicated graphing/grapher capability when available.
- If a dedicated grapher is not available, use a deterministic math/plotting method that computes the graph from the actual function/data.
- Do **not** use a generative image model to fabricate a quantitatively accurate mathematical graph.
- Do not substitute prose, ASCII art, a decorative sketch, or a blank box for a required graph.
- Save generated graph assets under the owning tool's graph asset folder, normally `assets/graphs/`.
- Prefer SVG when practical for crisp printing; PNG is acceptable when appropriate.
- Include readable axes, scale, tick marks, labels, units, plotted points/curves, and legends when the task requires them.
- Verify that the plotted relationship, coordinates, intercepts, asymptotes, domain/range cues, and scale are mathematically correct for the task.
- If students are supposed to create the graph themselves, do not reveal the completed answer graph. Supply only the prompt, data, axes/grid, or other neutral scaffold the task actually requires.

`data/qa.json` must include:

- `graphs.required_count`;
- `graphs.created_or_supplied_count`;
- `graphs.dedicated_grapher_available`;
- `graphs.dedicated_grapher_used_when_available`;
- `graphs.assets`, including each path, generation method, and accuracy-check result.

PASS is not allowed if a required graph is missing or mathematically inaccurate.

## 5. Diagrams, figures, and instructional visuals - HARD

Use real visuals when the task depends on spatial, structural, or representational information.

Examples include force setups, circuits, geometric figures, maps, experimental apparatus, labeled biological structures, tables/data displays, coordinate grids, vector layouts, timelines, and process diagrams.

- If the task refers to a diagram, figure, image, setup, model, map, table, or other visual, that visual must actually exist in the response or in an explicitly included source file.
- Prefer clean vector/SVG instructional diagrams for simple line art, geometry, force setups, circuits, arrows, and labeled models.
- Use generated raster imagery only when a realistic image is genuinely useful; decorative imagery is not a substitute for an instructional diagram.
- If a visual would materially reduce ambiguity or reading load, include it even when the prompt could technically be written without one.
- If **creating the diagram is the assessed skill**, do not give away the completed answer. Provide only a neutral setup sketch, blank grid, unlabeled structure, or other scaffold when useful.
- In physics, a scenario sketch and a force diagram are not automatically the same thing. If students are being assessed on constructing the force diagram, a neutral object/setup sketch may be supplied without pre-drawing the answer vectors.
- Save generated non-graph visuals under the owning tool's visual asset folder, normally `assets/visuals/`.
- Every referenced visual must have a resolvable path and appear at readable print size.

`data/qa.json` must include:

- `visuals.required_count`;
- `visuals.created_or_supplied_count`;
- `visuals.assets`, with path, purpose, generation method, and visual-check result.

PASS is not allowed if a prompt refers to a visual that is absent, unreadable, misleading, or answer-revealing when the student is supposed to construct it.

## 6. Locked CSS and visual consistency - HARD

Each tool owns an exact response stylesheet snapshot. The shared district standard defines the behavior; the owning tool's packaged CSS defines the final appearance.

- Copy each locked CSS file from the request package **byte-for-byte** to the required response asset path.
- Do not restyle the response because another source file uses different fonts, colors, spacing, or page layout.
- Do not silently add inline CSS that defeats the locked stylesheet.
- If the content does not fit, improve wording, chunking, or layout **within the existing CSS contract first**. Do not solve overflow by shrinking text to an unreadable size.
- If the owning tool requires one page, one landscape page, duplex-safe pages, or another print rule, satisfy that rule and verify the actual rendered PDF.
- Extra pages that are not explicitly assigned another style should inherit the owning tool's teacher/dashboard style rather than inventing a third visual system.
- Keep common district response conventions when they exist: white background, dark readable text, restrained blue/navy accent, clear sections/cards, prominent action buttons, high-contrast print, and uncluttered teacher navigation.
- Tool-specific student artifacts may use a specialized locked layout when that improves classroom use.

The request should provide a style version and, when practical, a SHA-256 hash for each locked CSS file. `data/qa.json` must record expected and actual hashes and whether they match.

PASS is not allowed when locked CSS does not match the request snapshot or when the final PDF is clipped/unreadable despite a hash match.

## 7. PDF generation and visual QA - HARD

A file existing is not enough. Finished PDFs must be rendered and visually inspected.

- Generate PDFs only after fonts, MathJax, graphs, diagrams, and linked assets are ready.
- Verify page size/orientation, margins, page breaks, clipping, overlap, unreadably small text, missing images, broken math, and accidental blank pages.
- Verify that print-specific rules such as one-page cards, landscape stations, or duplex padding are true in the **actual PDF**, not merely intended by CSS.
- Open every required PDF after generation.
- When the environment supports page rendering/screenshots, inspect the rendered pages rather than relying only on text extraction.

`data/qa.json` must include:

- `pdfs.rendered_and_visually_checked`;
- `pdfs.openable`;
- per-file page size/orientation and page count when the tool contract depends on them;
- `pdfs.failures` for clipping, missing assets, or layout problems.

## 8. Content integrity and teacher review - HARD

- Do not invent source facts, quotations, student evidence, measurements, citations, or teacher decisions.
- When a teacher has explicitly chosen an option in the request UI, treat that structured selection as authoritative over conflicting free-form notes.
- Flag uncertainty instead of pretending it is resolved.
- Answer keys/evidence guides must match the exact student tasks in the final student artifact.
- If a task changes during layout editing, update the guide/answer key too and rerun QA.
- Do not rank students, classes, teachers, or political choices unless the owning tool explicitly calls for a permitted non-political ranking.

## 9. QA record - HARD

Every response package covered by this standard must create `data/qa.json` or the owning tool's equivalent QA path.

At minimum record:

- shared-standard version;
- tool-specific contract version;
- overall PASS/FAIL;
- conflict resolution summary;
- MathJax status;
- graph status;
- visual/diagram status;
- locked CSS expected/actual hashes;
- relative-link resolution;
- required-file existence;
- PDF open/visual checks;
- tool-specific checks;
- `failures` array.

`overall_status: PASS` is not allowed while `failures` contains an unresolved item.

## 10. Delivery - HARD

Return one authoritative response ZIP when the owning tool requests one. Keep the user-facing delivery note short and useful. Do not present internal component files as competing required deliverables unless the teacher explicitly asked for them separately.
