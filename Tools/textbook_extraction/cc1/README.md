# CC1 canonical extraction — local, private

This extraction engine is **separate from the CPM Tools dashboard** so it cannot break your existing Algebra, CC3, assessment, or portfolio builders. It can be integrated after its extracted cards have been reviewed.

## One-time use

1. Use a **local copy** of your private Google Drive `cpm_textbooks/cc1` folder, containing `ch01` through `ch09`, `pip`, `checkpoints`, and `parent_guides`. If it exists only in Drive's browser, download the whole `cc1` folder and unzip it first. Wait for the local files/assets to finish syncing before running.
2. In Finder, open the installed `Open_CC1_Extractor.command`. Choose the **cc1 folder itself**, not a chapter folder.
3. The extractor creates: `~/Documents/CPM_Private_Extracted/cc1_canonical_cards_v1/`. The original Drive captures are never changed.
4. Read `QA_REPORT.md` (opens in TextEdit). Check media, MathJax, links, and the lesson cards before using them with students.

**No GitHub material upload:** Generated card JSON and copied images are placed **outside the GitHub checkout** by default. They contain copyrighted textbook content and must remain local/private. The Curriculum Transfer ZIP contains only the extraction program and tests, not textbook content.

## Output

- `cards.jsonl`: complete JSONL records, with rich HTML, source text, source problems, and media dependencies.
- `card_index.json`: smaller lookup list for a future shared Lesson Builder.
- `cards/<chapter>/*.json`: one reviewable JSON file per extracted card.
- `assets/`: copies of image/media files referenced by saved HTML cards.
- `qa_report.json`, `QA_REPORT.md`: extraction coverage, capture gaps, missing local assets, and review warnings.
- `PRIVATE_CONTENT_NOTICE.txt`: copyright/privacy reminder.

For each card: stable ID, chapter/lesson, source HTML path, saved original CPM URL, SHA-256 of original page, source problem ID and container ID where available, suggested type, and teacher-review status. Original captured files are not changed.

### What is validated, and what is not

Validated by the engine: source page presence (83 lessons), openings/closures, 14 PIPs, 12 checkpoints, 9 Parent Guides, `_files` sibling folders, readable source DOM, numbered problem container extraction, local referenced image existence, image copy, mathematical TeX source retention, external activity link inventory, and duplicate card IDs.

**Not automatically proven:** pixel-perfect offline rendering of MathJax/SVG equations, diagrams or multimedia activities; fidelity of interactive eTools, which may need the internet. Math TeX is preserved as a source representation, not as a guaranteed complete offline typesetting engine. The machine-assigned roles are suggestions and require teacher approval. Do not call this a final, classroom-ready card bank until visual QA and teacher review are complete.

### Command-line options

```sh
python3 cc1_extract.py --source "/path/to/cc1" --replace-output
python3 cc1_extract.py --source "/path/to/cc1" --output "/private/output/cc1_cards" --replace-output
python3 -m unittest test_cc1_extract.py -v
```

`--replace-output` may delete **only** a previously generated output directory containing the program's marker file. It will refuse to delete unknown folders or any source directory. If you change card records manually, save them in a separate teacher-edits library before rerunning extraction, because generated output is deliberately disposable.

## Intentional future step

Build a source-card review panel inside Unified CPM Tools. The approved review decisions, instructional roles, custom examples, and lesson assembly recipes must live in a **separate teacher-authored store**, never overwrite original source cards.
