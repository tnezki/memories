# Algebra 1 Warm-Up Bank — Three Quality Passes (November 21, 2026)

## Current state

This package updates the **source-lesson question bank** only. It does not change the lesson assembler, existing lesson artifacts, Q1/Q2 fluency bank, teacher flags, Portfolio priority selection, or question history publication logic.

- **102 source lessons**, each with **two spiral families** (204 total).
- Each spiral has **four extension options**: application, conceptual/error, connection/representation, and deeper reasoning. Total **816 extension families** and **6,528 extension variants** (eight per family).
- **1,632** source spiral versions; **8,160** total Q3/Q4 and Q5/Q6 source versions.
- Q5 extends exactly the chosen Q3 source instance; Q6 extends the chosen Q4 source instance. The future prebuilt lesson will select Q3/Q5 from the previous completed lesson and Q4/Q6 from another earlier lesson by balanced random review, later overridable through Portfolio-informed teacher adjustment.

## Pass 1 — Mathematics and instructional quality

All 8,160 source and extension versions were screened for missing text, malformed math, and source linkage. The number-only arithmetic audit evaluated **4,322** unambiguous relationships. It found no unexplained mismatches; **48** deliberately false equations occur in questions about contradictions/no solutions, and **21** are numeric evaluator artifacts within rounding tolerance. This is a scope-limited audit, not a proof that every word-problem answer has been independently solved.

Updated **728 numbered extension versions** across **98 families**, plus **30** original source prompt presentation fixes. Repaired mistaken skill alignments for quadratic generic rectangles, polynomial multiplication, exponential decay, two-variable inequalities, and experimental/statistical reasoning. Avoided needless large exponential arithmetic and unreasonable measurement rounding. Existing IDs and original source family memberships remain intact. Revised content requires explicit teacher review.

## Pass 2 — Duplicates and variety

Exact repeated student prompts: **0** across the 6,528 extension variants. After normalization of numbers, **430** distinct starter structures remain among 816 extension families. **98** same-lesson, same-role A/B pairs share very similar question templates; these are inventoried in the near-duplicate catalog for teacher judgment, **not misrepresented as all fixed**. Cross-lesson recurrence of a concept can be intentional spiral learning.

## Pass 3 — MathJax and browser

Compiled **23,325** mathematical spans representing **17,243** unique TeX expressions with the real MathJax engine: **0 parser errors**. A real headless-browser review of the existing bank app passed: two source families/four extension choices each, number swaps, page switching, teacher flags, notes, export, and SVG math display. This does **not** mean every printed lesson, graphic, or all 8,160 browser states was visually checked.

## Review gate and restrictions

- Existing review-history key, question IDs, course lesson IDs, and parent links remain unchanged. All edited extensions remain unapproved drafts.
- Do not replace the revised bank with its baseline; incoming transfer's `expected_existing_sha256` protects against overwriting a divergent local file.
- Only the Bank JSON is replaced; the matching installed review application is retained.
- Following teacher review, the **assembler** still needs Q3/Q5 previous-completed-lesson assignment and balanced prior-lesson Q4/Q6 defaults, with future Portfolio overrides. This is a separate job.
- The exact changes and remaining near-duplicate candidates are included as separate research records within this same transfer.

## Source verification

Baseline installed checksum: `488ce2495f73a61e3ef12385ea3371c1a0d359cccfa999ddd917576028124b11`  
Revised question-bank checksum: `e596eb13940244d7b18010990cb6c379dcc9f7396faa084248447622b5a665da`
