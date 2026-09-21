# District Resource Builder Execution Contract

STATUS: HARD
VERSION: district-resource-build-execution/1.0
DATE: 2026-09-20

## Division of labor

ChatGPT should spend its effort on:

1. understanding the teacher's target, grade level, sources, and profile;
2. making instructional/content decisions;
3. authoring the small amount of new classroom content;
4. checking content accuracy and instructional fit.

Packaged deterministic tools own repeated mechanics: request preflight, locked CSS copying, dashboard generation, file/link/hash checks, PDF signatures, and graph dependency verification.

## Required run order

1. Run `resource_preflight.py` once.
2. Read the relevant source files and author the resource content.
3. Use the packaged graph tool for supported Cartesian graph work.
4. Create the requested resource/teacher outputs.
5. Run `resource_finalize.py` once.
6. Run `resource_qa.py` once.
7. Correct only failures/outliers, rerunning only affected steps.
8. Write final `data/qa.json`, zip the response, return it.

## No recreation rule

Do not write new scripts for tasks already owned by the packaged utilities. Do not fetch the renderer, graph tool, CSS, contracts, profile registry, or QA utilities from GitHub/web during the response run. Missing packaged dependencies are a request-package defect.

## Source-file rule

Multiple source files are normal. Inventory them once from `request.json`; inspect the ones relevant to the resource. Do not repeatedly rediscover the same files.

## QA scope

Mechanical checks are authoritative for file existence, hashes, links, and package rules. Visual QA is bounded to generated math/graphs/diagrams, content-heavy pages, PDF/native output, and actual overflow/outlier pages.
