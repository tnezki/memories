# Tiered Task Build Execution Contract

STATUS: HARD
VERSION: district-tiered-task-build-execution/1.1
DATE: 2026-09-20

## Division of labor

ChatGPT owns only the variable instructional work:

1. understand the grade level, subject/course, I Can statements, sources, and teacher refinements;
2. design the DOK 1-4 progression;
3. author the small amount of new student/teacher content;
4. check content accuracy and DOK/alignment quality.

Packaged deterministic tools own repeatable mechanics: request preflight, dependency/hash checks, layout-lock verification, locked CSS copying, dashboard generation, required-file/link checks, PDF signatures/page-count checks, and graph dependency verification.

## Required run order

1. Run `tiered_task_preflight.py` once.
2. Read the request and relevant sources once.
3. Author one integrated DOK 1-4 card and one matching Teacher Guide.
4. Generate each distinct graph/diagram once; reuse assets.
5. Produce the required HTML/PDF files with the locked CSS.
6. Run `tiered_task_finalize.py` once.
7. Run `tiered_task_qa.py` once.
8. Correct only reported failures/outliers and rerun only affected steps.
9. Write final `data/qa.json`, zip the response, and return it.

## No recreation/search rule

Do not write new scripts for jobs already owned by the packaged utilities. Do not fetch the contracts, layout lock, locked CSS, graph tool, graph standard, or QA utilities from GitHub/the web during the response run. Missing packaged dependencies are a request-package defect and must fail closed.

## Grade-level rule

Grade level is primary instructional data. Use it with the I Can statements to set rigor, representation, numbers/data, vocabulary, reading load, expected reasoning, independence, and scaffolding. Do not infer rigor from target wording alone.

## QA fast path

Mechanical checks are authoritative for file existence, hashes, links, and package rules. Visual QA is bounded to the content-bearing task/guide pages, math/graphs/diagrams, final PDFs, and actual overflow/outliers. A local correction does not justify restarting unrelated work.
