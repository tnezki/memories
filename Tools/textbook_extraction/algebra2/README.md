# Core Connections Algebra 2 — Private Canonical Card Extractor

This is the course-specific, offline textbook-to-card extractor for CPM *Core Connections, Algebra 2*. It follows the same architecture as the CC1, CC2, Algebra 1, and Geometry extraction tools. The installer contains **code, documentation, and synthetic tests only** — never copyrighted CPM cards, images, or PDFs. It does not change the existing teacher course applications, lesson builders, or assessment plans.

## Install / run on Mac

1. Place the delivered `curriculum_transfer/3` ZIP in `~/GitHub/_curriculum_transfers/downloads/`, then run the existing **Apply Curriculum Transfers.command**.
2. Let Google Drive finish syncing the entire Algebra 2 capture to your local disk. The selected root must contain **`ch01` through `ch12`, `appendixa`, `appendixb`, `appendixc`, `checkpoints`, `parent_guides`, `standards`**, and Overview and Table of Contents HTML pages, with adjacent `_files` folders for every HTML.
3. Double-click `~/GitHub/memories/Tools/textbook_extraction/algebra2/Open_Algebra2_Extractor.command`, and choose the local Algebra 2 capture **root folder** (not an individual chapter).
4. Review the terminal result and the opened `QA_REPORT.md`.

**Output:** `~/Documents/CPM_Private_Extracted/algebra2_canonical_cards_v1/`

The source capture is never changed. The destination is regenerated only when its own `ALGEBRA2_GENERATED_OUTPUT.marker` is present and `--replace-output` is specified. **Keep generated content private; never commit the output directory to a public GitHub repository or publish cards/images on a shared site.** Teacher changes and assembly recipes belong in a separate store and must not be kept only inside generated output.

## Source baseline / inventory

From the October 11, 2026 complete Drive audit:

- **123 numbered lessons**: 102 across Chapters 1–12 and 21 in Appendices A, B, C (the saved appendices use filenames `Lesson 13...`, `Lesson 14...`, `Lesson 15...`).
- **15 student openings, 15 student closures, 15 teacher opening notes, and 15 teacher closure notes**, including the three appendices.
- **15 Resource Pages PDFs**: `CCA2 Ch 1 RPs.pdf` through `CCA2 Ch 12 RPs.pdf`, plus `CCA2 Ch A/B/C RPs.pdf`.
- **18 checkpoint pages:** 2a, 2b, 3a, 3b, 4a, 4b, 5a, 5b, 6a, 6b, 7a, 7b, 8a, 8b, 9a, 9b, 10, 11, plus the index.
- **15 Parent Guide PDFs** plus `PG_intro_generic.pdf`. The captured filenames can contain duplicate-download suffixes such as `(1)`, `(2)`, or `_1`.
- **7 standards HTML pages, 7 standards PDFs**, plus root Overview and Table of Contents HTML pages. The saved `misc` folder is empty and is not a missing-file error.
- **211 HTML pages** and **38 reference PDFs** in this audited baseline, when no optional pages have been added. Extra approved pages should be reviewed before broadening the ingestion registry.
- The **Chapter 8 student Closure HTML and matching `_files` folder are confirmed present**, resolving the last identified omission.
- Student Hunt, Teacher Hunt, Credits, Student Note, Glossary, and Index are **optional supplementary sources not captured**, and do not block the core inventory.

## Card extraction and QA

Each card preserves its original source-problem label, source order and source file, source HTML, original saved URL where available, media references, TeX expressions, file checksums, and teacher/student visibility. `teacher_approved: false` marks provisional machine suggestions, **not approved assessments**. Teacher Notes and identifiable Closure solutions are always `teacher_only`. Checkpoint original answers and answer sections are also teacher-only; practice list items are individual cards, including diagram-only ones.

For Closure key pairing, the extractor handles source inconsistencies **without rewriting source IDs**. Chapter 7 question `7-167` pairs with solution `CL 7-167` solely through a normalized lookup identity; Appendix C question `CLC-62` pairs with solution `CL C-62` the same way. Both original card labels are unchanged. The fifteen original Closure source files have been sampled; **146 student/solution pairs** were found with **zero unmatched/ambiguous key notices** in this real-source sample audit. Thirteen final self-reflections were explicitly detected; two Closure pages have all listed problems matched with answers and need no invented reflection item.

The deliverable produces `cards.jsonl`, `cards/` JSON files, `card_index.json`, `assets/` containing locally referenced images, `resource_index.json` (index only — PDFs stay at source), `qa_report.json`, `QA_REPORT.md`, and the privacy notice. `QA_REPORT.md` includes extraction totals, missing source items and image references, and content-boundary review warnings. A PASS means the captured files and media references exist and no structural error was detected; it is **not** proof of eTool interactivity, printing fidelity, or semantic correctness of every card boundary.

## CLI / tests

```bash
python3 algebra2_extract.py --source "/path/to/local/Algebra2" --replace-output
python3 algebra2_extract.py --source "/path/to/local/Algebra2" --output "/path/to/private/algebra2_cards" --replace-output
python3 -m unittest -v test_algebra2_extract.py
```

No third-party Python dependencies or network connection are required after local sync. Share the private `QA_REPORT.md` or terminal report back for a post-extraction QA review while Precalculus capture continues. Do not distribute the original textbook pages, cards, media, or PDFs.
