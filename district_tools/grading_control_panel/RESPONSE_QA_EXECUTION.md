# Grading Response QA Execution Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-response-qa-execution/1.3  
DATE: 2026-09-20

## Purpose
Keep grading/evidence QA rigorous while avoiding repeated work on locked templates and duplicate delivery formats. Student evidence still receives full review. The speed gains come from validating generated content once, trusting hash-locked shells, using HTML as the canonical print surface, and rerendering only what changes.

## 1. Record phase timings - REQUIRED
Record elapsed seconds in `data/qa.json` for at least:

- evidence review;
- grading/analysis;
- question/practice content generation;
- graph/visual generation;
- HTML/template assembly;
- programmatic QA;
- visual QA;
- correction/rerender work;
- total response build time.

These timings are diagnostic and must not change grading quality.

## 2. Evidence review is never reduced
Visually inspect scanned handwriting, diagrams, multi-page packets, and ambiguous evidence as needed to grade accurately. Do not use a speed shortcut to skip student evidence review or infer unreadable work.

## 3. Generate canonical content once
Build one canonical data object for each student report, each individual-practice question, each class-level Set 1 question, each answer, each teacher move, each discourse move, and each generated visual.

Solve/check a Set 1 question once. Reuse the validated object in Common Worksheet, Teacher Guide, Set 1 presentation, Print Presentation, Find Someone Who/Common Worksheet, and Cut-Apart Cards. Do not independently re-solve or revalidate identical mathematics simply because it appears in another delivery template.

## 4. Deterministic-renderer fast path - HARD
The packaged `response_builder.py` owns stable HTML. The run writes canonical `response_data.json`, runs the builder once, and preserves `data/template_qa.json`. PASS is forbidden if the builder fails. Do not hand-author, restyle, or visually re-audit stable shells. Visually inspect only generated graphs/diagrams and actual overflow/pagination outliers. A local content correction reruns only the deterministic builder, not the evidence review.

## 5. HTML is canonical for generated print products
Generated classroom/teacher products are HTML + browser Print unless the request explicitly requires a PDF.

Do **not** generate duplicate PDFs for:

- combined student reports;
- combined individual practice;
- Common Worksheet;
- Stations student pages;
- Stations answer key;
- Set 1 classroom presentation;
- Print Presentation;
- Teacher Guide;
- Cut-Apart Cards.

The submitted/scanned student-work archive may remain PDF because preserving the source evidence is a different function.

## 6. Programmatic checks first
Before expensive visual rendering, verify:

- required files/folders exist;
- local links resolve;
- request/analysis/QA JSON parses;
- locked CSS bytes/version/SHA match;
- MathJax loaders are present on math pages;
- canonical shared question IDs/counts match across reused views;
- duplicate Review All/Set 1 teacher-guide files are absent;
- Find Someone Who points to the same Common Worksheet HTML;
- Activity Options structure/names/material links match the contract;
- Set 1 classroom presentation has one problem per Letter page with question top half and answer/moves bottom half;
- Print Presentation has exactly two questions per Letter page;
- adjustable pages contain the required left-rail controls and explicit Letter page containers;
- duplex HTML page-count logic is internally consistent;
- graph provenance records the packaged registered graph tool;
- expected graph/visual assets exist;
- no prohibited generated classroom PDFs are present.

Fix programmatic failures before broad visual QA.

## 7. Targeted visual QA
Visually inspect:

- every page containing a mathematical graph or nontrivial diagram;
- first page and at least one later representative/outlier page of each distinct locked template;
- actual page-break transitions in Common Worksheet and combined Individual Practice;
- first and last Set 1 classroom-presentation pages plus graph-heavy pages;
- first and last Print Presentation pages plus graph-heavy pages;
- Cut-Apart Cards first page plus any card with a large figure;
- Stations first, representative middle, and final page;
- representative duplex student transitions for combined reports/practice;
- any page flagged by programmatic checks or overflow detection.

Do not rerender every stable report/practice page only because text differs.

## 8. Adjustable-page QA
For each adjustable HTML type, spot check the required controls at meaningful values.

For Common Worksheet and combined Individual Practice:

- All workspaces: 0%, 100%, 300%;
- selected-problem Workspace: 0%, 100%, 500%, 1200%;
- Graph/diagram when present: 70%, 100%, 160%.

For Set 1 classroom presentation:

- All question spacing: minimum/default/maximum;
- selected-problem Question spacing/workspace: minimum/default/maximum;
- Graph/diagram when present: 70%, 100%, 160%.

After each mutation, confirm screen pagination updates and browser Print uses the same physical page boundaries. A slider that moves but does not change layout is a failure.

## 9. Duplex HTML QA
For combined reports and combined Individual Practice, determine each student's rendered physical page count from the explicit page containers. If odd, add exactly one truly blank page before the next student. Verify representative student-to-student transitions and record content pages, blank backs, and physical pages in `data/qa.json`.

Do not generate a PDF merely to prove duplex pairing.

## 10. Graph QA remains strict
Every supported Cartesian graph is generated by the packaged registered graph tool. Graph pages are always visually checked for mathematical accuracy, labels, readability, and the canonical district style. Reused questions reuse the same graph asset.

## 11. Correction loop - changed artifacts only
If QA finds a defect, regenerate/rerender only:

1. the artifact that changed;
2. direct HTML/index dependents;
3. pages affected by the same systemic rule.

Do not automatically rerender the entire response after a local correction.

## 12. Required QA record
`data/qa.json` records:

- phase timings;
- programmatic checks;
- visual-QA coverage;
- graph provenance;
- adjustable-control checks;
- duplex HTML page counts;
- changed artifacts rerendered;
- explicit note that unchanged locked templates were not redundantly rerendered;
- failures.

PASS is forbidden with unresolved failures.


## Deterministic functional checks - REQUIRED
- `data/template_qa.json` exists and reports PASS.
- No generated page contains page-local `<style>` blocks.
- Common Worksheet and Individual Practice use `assets/runtime.js` and `assets/runtime.css`.
- A workspace slider changes workspace height while problems continue to flow inside true Letter pages.
- The Problem selector contains the actual problem IDs, not only an `All` placeholder.
- Class Data, Stations, dashboard cards, Teacher Guide, and cut cards come from the renderer and cannot drift between runs.
- Activity directions are structure-specific static builder content, not newly generated generic directions.
- Set 1 items cannot render unless `verification.passed=true`.
