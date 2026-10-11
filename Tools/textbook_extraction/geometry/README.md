# Core Connections Geometry — canonical card extractor (PRIVATE / offline)

This course-specific extractor creates canonical, source-faithful cards from the **teacher's locally captured CPM Core Connections, Geometry eBook**. It follows the CC1 / CC2 / Algebra 1 extraction architecture, and **does not** modify the Lesson Builder, course apps, or assessment plans. The transfer itself contains **code, tests, and documentation only**; no textbook content is included or committed to GitHub.

## Install and run

1. Move the delivered GitHub/Curriculum Transfer ZIP to `~/GitHub/_curriculum_transfers/downloads/` and run the installed `Apply Curriculum Transfers.command`. It creates `~/GitHub/memories/Tools/textbook_extraction/geometry/` with four files.
2. Verify the complete Geometry textbook capture is **fully synced as real files to your Mac**. It needs a top-level folder with `ch01` through `ch12`, `checkpoints`, `standards`, `parent_guides`, `misc`, the overview and Table of Contents HTML, each saved HTML's sibling `_files` directory, and local images. An online-only Google Drive shortcut or a browser link is not enough.
3. Double-click `Open_Geometry_Extractor.command` inside the installed Geometry tool directory, select the **Geometry root** folder, and let the extraction finish. A terminal report appears and `QA_REPORT.md` opens in TextEdit.
4. The private cards are generated under `~/Documents/CPM_Private_Extracted/geometry_canonical_cards_v1/` unless you explicitly change the output CLI option. **Do not upload this folder to GitHub or public websites.**

When `EXTRACTION AND INVENTORY CHECKS: PASS` appears, the machine's expected-file inventory is satisfied and no fatal card validation error was found. `REVIEW` warnings can still point out unusual card boundaries or missing images. A PASS is **not** certification that all diagrams and eTools render offline.

## Source inventory baseline (Drive audit, October 11, 2026)

- **126** numbered lessons across **12 chapters**.
- **12 each** of student chapter openings, student chapter closures, teacher opening notes, and teacher closure notes.
- **12** Chapter Resource Pages PDFs (`CCG Ch 1 RPs.pdf` through `CCG Ch 12 RPs.pdf`).
- **13** checkpoints: `1`, `2`, `3`, `4`, `5a`, `5b`, `6`, `7`, `8`, `9a`, `9b`, `10`, `11`, plus the checkpoint index. The numbering gaps are intentional; do not invent a 12th checkpoint.
- **12** chapter Parent Guide PDFs, 2 Algebra Practice parent guides and parent intro; 4 standards PDFs, 5 miscellaneous reference/rubric PDFs.
- 4 standards HTML pages, root Overview and Table of Contents HTML, and matching `_files` folders for all captured HTML.

**194 HTML pages and 36 reference PDFs** are expected in the baseline full source capture. The optional Student Hunt, Teacher Hunt, Credits, Student Note, Glossary, and Index source pages can be captured later; they are **not** artificially marked as completed, and are not required for the core 126-lesson extraction. If any are added, review and extend the source-role/page registry before automatically importing them.

## Core extraction behavior

- Output includes `cards.jsonl`, `card_index.json`, `cards/<chapter>/*.json`, `assets/`, `resource_index.json`, `qa_report.json`, `QA_REPORT.md`, and a privacy notice.
- Preserves **source problem IDs, original saved URL, source file and SHA256, source order, source HTML, MathJax TeX, and copied local images/media**. External eTool links are retained as external references, not downloaded or falsely treated as working offline.
- Separates lesson problem cards from explanatory/source-note cards without paraphrasing the textbook. Source roles and pedagogical purposes are **machine suggestions**; `teacher_approved: false` indicates teacher review is still required.
- Teacher Notes are always `teacher_only`. Chapter Closure answer blocks are separated from student problems and matched by their original `CL n-nnn` identifiers when unambiguous; never publish those keys on student materials. The twelve final Closure self-rating/reflection questions intentionally have no answer keys.
- **Geometry Chapter 8** wraps student questions and answer blocks in one nested `<ul><li>`; this extractor explicitly unwraps it, preserving the original question-answer boundaries. All **12 actual captured Geometry Closure HTML pages** were inspected before shipping, with **115 correctly paired key cards and 12 student reflection cards**, no unmatched-key notices in that specific sample audit.
- Image-only practice problems from **Checkpoints 7 and 8** are individual problem cards (24 and 20 respectively on the actual sampled pages). Items receive generated **local list sequence numbers**, not fabricated CPM problem IDs. Checkpoint answers, including worked answers to the referenced original checkpoint problem, are marked `teacher_only`.
- PDF references are indexed with source-relative paths and SHA256 in `resource_index.json`. The original PDFs stay in the local source directory and are **not** copied into GitHub.

## CLI and privacy

```bash
python3 geometry_extract.py --source "/path/to/private/Geometry" --replace-output
python3 geometry_extract.py --source "/path/to/private/Geometry" --output "/path/to/private/geometry_cards" --replace-output
python3 -m unittest -v test_geometry_extract.py
```

The source capture is read-only. `--replace-output` only replaces the chosen folder when it contains the known `GEOMETRY_GENERATED_OUTPUT.marker`; no other folder will be deleted. Regeneration replaces generated cards, so keep any **teacher-approved revisions/assembly recipes in separate stores**. Do not distribute CPM cards, images, or resource PDFs publicly.

## Follow-up QA

After first full Mac run, inspect and send back `QA_REPORT.md` or the terminal output. We can refine any course-specific boundary or missing-media warnings without recapturing completed source pages. Future expansion should preserve stable card IDs where source identity is unchanged and must not silently relabel copyrighted source content.
