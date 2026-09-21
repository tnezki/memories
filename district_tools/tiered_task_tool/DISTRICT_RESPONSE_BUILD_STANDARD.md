# District Response Build Standard

STATUS: REQUIRED WHEN PACKAGED BY A DISTRICT TOOL
VERSION: district-response-build-standard/1.1
DATE: 2026-09-20

This is the common base contract for district request builders. Tool-specific contracts may add requirements but may not silently weaken these rules.

## 1. Authority and fail-closed behavior - HARD

Use: safety/platform/file integrity -> HARD packaged contracts -> structured teacher choices -> tool defaults -> teacher notes -> source files -> inference.

If a packaged core dependency named by the request is missing or hash-invalid, fail closed as a packaging error. Do not search GitHub/the web for a replacement and do not recreate a supposedly locked tool from memory.

## 2. Teacher-simple architecture

The teacher interface should expose instructional choices, not implementation details. Technical behavior belongs in contracts and packaged utilities.

If an operation can be performed the same way across many requests, prefer a deterministic packaged tool over asking the model to recreate it.

## 3. Finished response package - HARD

- Return one authoritative response ZIP.
- `CLICK_ME.html` is the entry point unless the owning tool explicitly says otherwise.
- Use local relative links.
- No placeholder files, fake links, empty shells, or promises to create an artifact later.
- Required answer keys/guides must match final student-facing work.

## 4. Math and MathJax - HARD

- Use semantic TeX/MathJax for real mathematical notation.
- Configure delimiters consistently.
- Do not expose raw TeX in the finished resource.
- Do not rasterize ordinary equations merely to avoid MathJax.
- Perform visual math QA only on pages that contain math and on actual outliers; do not re-audit stable locked shells unnecessarily.

## 5. Graphs - HARD

When a graph is required, use the owning tool's packaged canonical graph renderer when available. A required mathematical graph may not be replaced by prose, ASCII art, an image-generation model, or a decorative sketch.

Generate a distinct graph once, reuse it, and record provenance. Student construction tasks receive answer-neutral scaffolds.

## 6. Diagrams and visuals - HARD

If the task depends on a figure, map, apparatus, circuit, geometric diagram, data display, coordinate grid, vector layout, timeline, or other visual, the visual must actually exist. Prefer deterministic SVG/line-art methods for instructional diagrams.

## 7. Locked styling - HARD

Packaged locked CSS is authority. Copy/verify it instead of restyling each run. Do not insert page-local CSS unless the owning contract explicitly permits it.

## 8. Mechanical QA fast path - HARD

Run deterministic file/hash/link/package checks before visual QA. Trust successful locked hashes. Visually inspect only content-bearing pages, generated graphs/diagrams, PDFs/native outputs, and genuine overflow/layout outliers.

After a local correction, rerun only the affected deterministic build/QA steps; do not restart unrelated content work.

## 9. PDF/native output

When the selected profile explicitly requires PDF/PPTX/DOCX/CSV or another native artifact, produce the finished file and verify it opens. For PDFs, verify page count/geometry and inspect representative/content-risk pages for clipping or missing assets.

## 10. QA record - HARD

Every response includes `data/qa.json` with overall PASS/FAIL, versions, conflicts, required-file status, locked-style hashes, math/graph/visual status, native/PDF status where applicable, mechanical QA status, and an unresolved-failures list.
