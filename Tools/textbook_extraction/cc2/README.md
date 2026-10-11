# CC2 canonical cards — private local extraction

This folder extends the installed **CC1 / Algebra 1 textbook extraction architecture** with Core Connections, Course 2 (CC2). It does **not** change the Lesson Builder, CPM Tools, or assessment planning.

## Installation and run

1. Apply the single GitHub/Curriculum Transfer ZIP using the installed `Apply Curriculum Transfers.command` launcher. It creates four files in `memories/Tools/textbook_extraction/cc2/` and leaves existing course extractors untouched.
2. Make sure your privately captured **entire CC2** Google Drive folder is **really available on the Mac** as local files, including `ch01` through `ch09`, `pip`, `checkpoints`, `parent_guide`, `standards`, sibling `_files` folders and their images. Browser-only Drive shortcuts are not sufficient.
3. Double-click `memories/Tools/textbook_extraction/cc2/Open_CC2_Extractor.command`, then select **the CC2 root folder**. Do not select a single chapter or the Google Drive webpage.
4. The program creates or refreshes `~/Documents/CPM_Private_Extracted/cc2_canonical_cards_v1/`. On completion, its `QA_REPORT.md` opens in TextEdit. Inspect source coverage, unusual card IDs, teacher solutions, and media warnings.

**Important:** The transfer installs the extractor. The actual full CC2 library is generated **on your Mac** after the local CC2 folder is selected; the ZIP deliberately contains **no proprietary textbook content**.

## Source contract (verified October 11, 2026)

- All **94** lessons across Chapters 1–9.
- Student chapter openings, closures, and teacher opening/closure notes: **9 of each**.
- Chapter resource PDFs: **9**; Parent Guides: **9**.
- Puzzle Investigator Problems **PI 1–14** and PIP index.
- **Nine** checkpoints: `1`, `2`, `3`, `5`, `6`, `7a`, `7b`, `8`, `9`. There is **no expected Checkpoint 4**.
- Standalone Chapter **5.4 Mid-Course Reflection**, standards sources, overview, TOC, and matching `_files` asset folders.

The Google Drive source inventory was reviewed; **this does not claim a complete locally generated CC2 library already exists**. The local run performs the real file integrity scan.

## Canonical output

- `cards.jsonl` — every card as JSON, including original page URL/SHA, source HTML, preserved TeX, image references and copied media, source problem IDs, teacher/student visibility, and closure question-key pairs.
- `card_index.json` — small searchable card selection index with stable card IDs.
- `cards/<chapter>/*.json` — individual reviewable card files.
- `assets/` — copied image/media assets, stored under relative paths derived from their original source files.
- `qa_report.json` and `QA_REPORT.md` — lesson/resource inventory, counts, asset failures and review warnings.
- `PRIVATE_CONTENT_NOTICE.txt` — privacy reminder.

**Student / teacher boundaries:** Student questions and separately saved Chapter Closure answers sharing IDs like `CL 1-142` remain separate cards. Answer/support blocks in closures and checkpoints are `teacher_only`. Teacher Notes are also `teacher_only`. This field must be enforced by future card consumers; manual teacher review is still required. In a checkpoint, list-based practice items are split into individual student problems, using **generated local sequence numbers**, not invented CPM problem IDs.

MathJax source TeX is preserved; the program cannot guarantee every MathJax graphic or external eTool works offline or has correct pixel rendering. It never downloads eTools. Local image presence does not prove every diagram displays perfectly. Retained cards and figures must not be committed to public GitHub.

## Command line and diagnostics

```sh
python3 cc2_extract.py --source "/path/to/cc2" --replace-output
python3 cc2_extract.py --source "/path/to/cc2" --output "/private/output/cc2_cards" --replace-output
python3 -m unittest -v test_cc2_extract.py
```

`--replace-output` operates only on a previously generated folder containing `CC2_GENERATED_OUTPUT.marker`. The original source directory is read-only. Choose a different output location if you made manual changes to generated cards; future teacher choices belong in a separate store rather than editing canonical source cards.

## CC2 1.1 source-boundary correction (October 11, 2026)

- Recognizes either `PIP.html` or the original saved filename `CPM eBooks - CC Course 2 PIP.html` as the PIP index. It is not a missing page.
- Separates Closure solution containers that are nested in HTML lists and pairs them with their student questions. The real source uses this layout in Chapter 4 (eight solutions) and Chapter 7 (one solution).
- Keeps the final Closure self-rating problem in each chapter as a student card (`closure_self_assessment`) with its original problem number, without falsely demanding an answer key.
- This is a generator update, not a source-content or Lesson Builder change. **Run the extractor launcher again** after applying the transfer; its marker-protected private output will be regenerated. Preserve teacher edits separately before running.
- Remaining long exposition blocks are source-fidelity review notices, not inventory errors. Review them before student use.
