# Algebra 1 canonical card extraction (Core Connections Algebra)

This is a **local, private, source-preserving** card extractor based on the same CC1 card contract. It creates reusable copies of textbook notes/exposition and numbered problems, while linking explicit Closure solutions as teacher-only cards. **It does not change the Lesson Builder or create assessment plans.**

## Run after applying the single Curriculum Transfer ZIP

1. Have a completely synced **local copy** of the private Google Drive folder `cpm_textbooks/cc_algebra`. The selected folder must itself contain `ch01` through `ch11`, `appendix_a`, `checkpoints`, `parent_guides`, `standards`, and `contents.html`. If the folder is Drive-only in a browser, download/unzip it before running.
2. In Finder, open `memories/Tools/textbook_extraction/algebra1/Open_Algebra1_Extractor.command`, and select the **cc_algebra** folder. Do not select a chapter folder.
3. The extractor writes to `~/Documents/CPM_Private_Extracted/algebra1_canonical_cards_v1/` outside the repository. Inspect `QA_REPORT.md` (automatically opened on macOS).
4. If you rerun it, the command replaces only its prior **generated output**, guarded by `ALGEBRA1_GENERATED_OUTPUT.marker`. Original textbook captures are never edited. Do not edit generated cards in place; save future teacher edits separately.

## Verified source inventory contract

Core Connections Algebra has **112 numbered lessons** across Chapters 1–11 and Appendix A (chapter number 12), including extension activity **2.4.1**. The saved source names are irregular in Chapters 1 and 2: `1-1-1.html`, `intro.html`, `closure.html`, `intr0.html` (zero), and `extraactivity.html`. These are mapped to original canonical lesson IDs, without renaming the saved captures. All 15 checkpoints, 12 Parent Guides, and all opening, closure, resource-PDF, and Teacher Notes **opening** pages are checked. Separate Teacher Notes closure files are not in the supplied Algebra inventory and are not assumed.

## Output format

- `cards.jsonl`: rich canonical card records preserving textbook source text, fragment HTML, saved CPM URL, source file SHA-256, chapter/lesson, original problem number, math TeX, external eTool links, image dependencies, and suggested instructional role.
- `card_index.json`: compact selectable card index for a future unified Lesson Builder.
- `cards/chXX/*.json`: one card per JSON file (Appendix A is represented as chapter 12).
- `assets/`: copies of images directly referenced in extracted cards, using source-relative paths.
- `qa_report.json` and `QA_REPORT.md`: audit of inventory, card counts, missing media, and classification warnings.
- `PRIVATE_CONTENT_NOTICE.txt`: keep copied licensed content private.

## Questions and keys

- Student questions retain `card_type=problem`, `visibility=student_candidate`.
- In Closure pages, source blocks beginning `Solution` or `More Solution` are preserved as separate `teacher_only` solution cards and linked to the matching question where unambiguous.
- Teacher Notes openings are `teacher_only`. The future builder must enforce that boundary; it must **never** mix solution cards into student output by default.
- Cards for mathematical explanations, examples, reflection, and checkpoint material have machine-suggested labels and need teacher review before final classroom use.

## Limits and privacy

The extractor tests for local reference integrity, not visual fidelity of every graph and equation. MathJax TeX is retained; a future renderer must display it correctly. External CPM eTools are recorded as links, not copied for offline use. Do not upload generated cards, source textbook HTML, or textbook images to public GitHub. The transfer ZIP contains only the reusable source-to-card code, test suite, and instructions, **not copyrighted textbook content**.

## Command-line use

`python3 algebra1_extract.py --source "/path/to/cc_algebra" --output "/private/destination"`

`--replace-output` may remove an old generated output **only** if the output folder contains `ALGEBRA1_GENERATED_OUTPUT.marker`.

Tests: `python3 -m unittest -v test_algebra1_extract.py`. A full synthetic inventory dry run was also checked before packaging.

## Version 1.1 classification corrections

The actual Algebra 1 audit exposed three source conventions: Appendix A uses canonical `A-1` through `A-97` problem numbers; its Closure uses `CL A-98` and subsequent problem IDs; and one legitimate question, 9-47, is titled "Solutions to a Linear Inequality." Version 1.1 accepts those source IDs, keeps 9-47 as a student question, and pairs Closure blocks beginning "More Solution" with their corresponding problem as teacher-only answer cards. Rerun the launcher to refresh the generated private library.
