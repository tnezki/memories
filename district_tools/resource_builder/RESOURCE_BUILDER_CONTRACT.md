# District Resource Builder Contract

STATUS: REQUIRED
VERSION: district-resource-builder/0.4-pilot
DATE: 2026-09-20

This contract turns one structured teacher request into one finished classroom resource package. It is intentionally teacher-simple and implementation-heavy: the teacher supplies instructional intent; the request ZIP carries the engineering rules and repeatable tools.

## 1. Core purpose - HARD

- Build the resource profile selected in `request.json`.
- Use the teacher's learning target(s), explicit grade level, subject/course, and profile-specific options as the primary instructional authority.
- Produce a finished classroom-ready artifact, not a prompt or placeholder.
- Return exactly one response ZIP with `CLICK_ME.html` as the teacher entry point.
- Do not ask the teacher to restate information already present in the request.

## 1A. Learning-target entry - HARD

The teacher interface uses one multiline I Can / learning-target field. Recommend **1-4 targets**, but do not impose a maximum. Each nonblank line is a separate target after removing ordinary bullet/number prefixes. More than four targets are valid when they belong to one coherent instructional set; do not discard or merge them merely to reach four.

## 2. Grade level is instructional data - HARD

Grade level is required because identical target wording can imply very different rigor across grades.

Use grade level together with the learning target(s) to set:

- number choices and computational complexity;
- representation type and abstraction level;
- expected reasoning and explanation length;
- vocabulary and direction complexity;
- reading load;
- amount and type of scaffolding;
- independence expected from students;
- what counts as appropriate application or transfer.

Do not infer grade-level rigor from the wording of an I Can statement alone.

## 3. Baseline quality vs. optional Advanced emphasis

Accuracy, clarity, age/grade appropriateness, accessibility, readable directions, and alignment are baseline requirements even when no Advanced checkbox is selected.

`design_priorities` contains only optional emphases selected under Advanced Options. An unchecked box does not mean "avoid this" and does not weaken baseline quality.

Examples:

- `real_world_application` means emphasize authentic application where natural; never force a fake context.
- `inclusion_accessibility` means add extra access attention beyond the baseline, not that baseline accessibility was optional.
- `engagement` means prioritize active/interesting participation without adding decorative gimmicks.
- `scaffolds` means intentionally add supports without lowering the target.
- `extension_challenge` means deepen transfer/synthesis, not merely add more repetition.

## 4. Authority and conflicts - HARD

Use this order when instructions conflict:

1. safety/platform/file-integrity requirements;
2. packaged HARD contracts;
3. resource profile and resolved outputs;
4. grade level + subject/course + learning targets;
5. profile-specific controls;
6. optional Advanced fields and selected design priorities;
7. free-form teacher notes;
8. source files for the content they actually contain;
9. model inference.

Record material conflicts in `data/qa.json`. Do not silently discard a higher authority.

## 5. Supporting source files - HARD

The teacher may attach zero, one, or many source files. Treat every `request.source_files[]` entry as an available supporting source.

- Read all files that materially affect the requested resource.
- Preserve source terminology, framing, data, and examples when relevant.
- Do not invent missing quotations, measurements, standards, or source facts.
- Do not assume the first file is the only source.
- Do not search the web merely because a packaged/source dependency is missing. Missing core package files are a packaging failure.
- External research is allowed only when the teacher explicitly requests it or the selected profile clearly requires current outside information; distinguish it from source-provided content.

## 6. Common instructional rules - HARD

- Align every major component to at least one submitted learning target.
- Avoid filler used only to hit a page/question count.
- Preserve readability instead of shrinking text to force a requested length.
- When multiple student versions are created, keep the essential target coherent.
- Answer keys/teacher guides must match the final student artifact exactly.
- When the assessed skill is creating a graph/diagram, do not reveal the answer in the student scaffold.
- Use concise labels separately from the actual prompt when both appear; do not run a skill/type label directly into the problem sentence.

## 7. MathJax - HARD

Use valid MathJax/TeX for mathematical notation. Do not fake math with Unicode lookalikes or improvised HTML. Verify rendered symbols, fractions, radicals, exponents, vectors, inequalities, and units. Final print/native output must not expose raw TeX.

## 8. Graphs - HARD

Follow `response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md`.

For supported Cartesian graphs and blank student grids:

- execute the packaged canonical graph tool directly;
- use `request.graph_rendering.packaged_entrypoint`;
- generate each distinct graph once and reuse the asset;
- prefer SVG where practical;
- do not use a generative image model for quantitatively accurate graphs;
- record renderer entrypoint and graph asset paths in `data/graph_provenance.json` when graphs are created.

## 9. Diagrams and instructional visuals

Use real diagrams when the task depends on spatial/structural information. Prefer clean SVG/line art for geometry, force setups, circuits, labeled structures, arrows, tables, timelines, and process diagrams. Decorative images do not replace instructional visuals.

## 10. Locked styling - HARD

The response must use the packaged locked styles:

- `response_contract/dashboard_styles.css` -> `assets/dashboard_styles.css`
- `response_contract/resource_styles.css` -> `assets/resource_styles.css`

Do not invent a separate visual system or page-local CSS. The deterministic finalizer copies these exact files. Profile-specific structure may vary, but it uses the locked visual language.

## 11. Repeatable mechanics - HARD

Mechanical work belongs to the packaged utilities:

- `resource_preflight.py` verifies request integrity, sources, contracts, hashes, and graph dependencies.
- `resource_finalize.py` copies locked assets/request metadata and creates the standard `CLICK_ME.html` dashboard.
- `resource_qa.py` checks required outputs, local links, locked-style hashes, file integrity, PDF signatures, and graph provenance.

Do not rewrite equivalent ad-hoc Python/shell scripts during a normal run. Do not manually repeat checks already reported by these tools.

## 12. Output and QA

Create every file in `request.resolved_outputs.required_files`, resolving the Custom Resource wildcard to a real file when needed.

`data/qa.json` must record:

- overall PASS/FAIL;
- contract/tool versions;
- conflicts;
- content accuracy checks;
- MathJax status when math appears;
- graph/visual status;
- mechanical QA result/path;
- PDF/native visual checks where required;
- unresolved failures.

PASS is forbidden with an unresolved required-output, accuracy, graph, visual, or package-integrity failure.
