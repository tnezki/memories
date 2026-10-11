# Precalculus Third Edition — Private Canonical Card Extraction

Offline Mac source-to-card extractor for CPM *Precalculus Third Edition* (PC3). The Curriculum Transfer ZIP installs code, this README, a `.command` launcher, and synthetic regression tests **only**. No textbook HTML, copyrighted cards, diagrams, source PDFs, or images are included.

## Install and use

1. Put the ZIP in `~/GitHub/_curriculum_transfers/downloads/` and run the existing **Apply Curriculum Transfers.command**.
2. Wait for private Google Drive sync to finish. The capture root must contain `ch01` through `ch13`, `checkpoints`, `standards`, `misc`, the top-level Overview and Table of Contents HTMLs, and an adjacent `_files` folder for every saved HTML. `parent_guides` may be empty.
3. Double-click `~/GitHub/memories/Tools/textbook_extraction/precalculus/Open_Precalculus_Extractor.command`. Select the synced **root** (not an individual chapter or checkpoint folder).
4. Review the terminal status and private `QA_REPORT.md` generated at `~/Documents/CPM_Private_Extracted/precalculus_canonical_cards_v1/`.

Run directly with Python 3 if preferred:

```bash
python3 precalculus_extract.py --source "/path/to/synced/Precalculus" --replace-output
python3 -m unittest -v test_precalculus_extract.py
```

The capture source is never modified. A rerun replaces only output bearing its own `PRECALCULUS_GENERATED_OUTPUT.marker` with explicit `--replace-output`. Teacher classifications and assembly recipes must be stored separately; do not edit generated cards as the only record of teacher changes.

## Audited PC3 source structure

- **13 chapters** (`ch01`–`ch13`) and **121 numbered lessons**, including distinct supplemental lesson **13.2.2A**, preserved under its actual ID.
- **13 student openings, 13 student closures, 13 teacher opening notes, and 13 teacher closure notes**.
- **17 checkpoint HTMLs**: 4a, 4b, 5, 6, 6b, 7a, 7b, 8a, 8b, 9a, 9b, 10, 11, 12a, 12b, 13a, 13b, plus the checkpoint overview/index. Checkpoint 12A and its `_files` folder were confirmed after initial audit.
- **13 chapter resource PDFs**, named `pc3_ch1_rps.pdf` through `pc3_ch13_rps.pdf`; **4 standards PDFs** and **2 misc PDFs** (`pc3_rps.pdf`, `PC Skill Builders.pdf`). These PDFs are indexed from their local source, not copied to output. The supplied edition has no required Parent Guides and no standards HTML pages.
- **193 core HTML pages** (121 lessons + 52 chapter opening/closure/teacher note pages + 17 checkpoint items + 1 checkpoint overview + 2 root HTML). **19 reference PDFs** in the initial audit. Extra approved sources may increase these totals.
- PC3 Hunts, separate full Checkpoint Materials PDF, Selected Answers, Glossary, and Index are supplementary, not blockers.

## Extraction guarantees and limitations

Each card keeps original source identifiers and text, source order, provenance, saved URL where present, source checksum, Math TeX, retained card-level HTML, teacher/student visibility suggestion, image/media assets from its private capture, and any external links. Original Closure solutions are teacher-only and paired with student questions where their source IDs match; the final self-reflection problems are left student-facing **without fabricated keys**. PC3 Chapters 1 and 2 use the wording *"Check your answers in/using the following table"*, handled as self-assessment. A space at the end of the Chapter 6 source ID `CL 6-143 ` is preserved and ignored only in validation/matching.

Checkpoint worked examples may be student-facing; answers to original checkpoint questions and answer sections are teacher-only, with image-based practice items split by their original list boundaries without fabricated problem labels. **Classification is machine-suggested, not teacher-approved.** Large exposition chunks are flagged for review rather than silently rewritten.

The extractor generates `cards.jsonl`, per-card `cards/` JSON, `card_index.json`, cloned referenced `assets/`, `resource_index.json`, `qa_report.json`, `QA_REPORT.md`, and privacy notice. Inventory PASS checks the required structure and local media existence; it does **not** certify all images render correctly, eTools work offline, or teacher-approved content boundaries.

**Privacy:** Keep these licensed CPM cards, HTML, images, and references private on your Mac; do not publish cards or original assets on public GitHub or hosted sites. Only code-only transfers are permitted in the project repository.
