# Algebra 1 Chapter 3 — Teacher-approved objective audit

**Date:** 2026-11-15  
**Source checked:** Installed CPM Tools mirror `banks/data/CH03.json` (SHA-256 `a91058df8939c9...`) and matching `banks/section.html`. CPM ebook Lesson 3.3.2 was reopened and read before changing question scope.  
**Instructional status:** Chapter 3 approved by teacher for current use; no wholesale rewrite. Draft assessment generation gates deliberately unchanged.

## Confirmed and repaired

The three Lesson 3.3.2 literal-formula families repeated the **identical prompts in all three difficulty bands**, despite presenting 6/5/5 variants at each level. There were 32 exact repeats across those three families.

- `ALG1-AP2-3-3-2-S01` — familiar formulas: preserve all six existing Level 1 items; replace six Level 2 and six Level 3 items.
- `ALG1-AP2-3-3-2-S02` — geometry formulas: preserve all five Level 1 items; replace five Level 2 and five Level 3 items.
- `ALG1-AP2-3-3-2-S03` — applied formulas: preserve four of five Level 1 items; fix one no-op item that asked students to solve for an already-isolated `F`; replace five Level 2 and five Level 3 items.

The resulting 32 replacement variants are distinct within their families and have independently checked solutions (symbolic algebra plus substitution tests). Level 2 requires more rearrangement and Level 3 frequently requires collecting multiple occurrences of the target variable. Positive-radius root assumptions are made explicit in applicable geometry questions. The 3.3.2 source emphasizes rewriting multivariable equations; the revised task types stay within that scope.

## Verified unaffected

- Exactly 171 Chapter 3 family records; 115 visible families.
- 3,511 visible candidate questions in the **source**, compared with the stale previous quality metadata showing 3,522. Candidate count was corrected in the updated bank; 32 variants were replaced, not added.
- Chapter 1 and Chapter 2 embedded JSON blocks in `banks/section.html` are byte-for-byte identical to the current installed source.
- Existing teacher Good / Needs Work / Bad controls and saved review namespace are untouched.
- The active candidate indices remain continuous in every level and no candidate has been promoted to automatic assessment eligibility.
- Browser smoke tests passed for the three revised families at Levels 1/2/3 and for review controls; no JavaScript runtime errors.

## Deliberately not changed

The remaining Chapter 3 bank has 36 **exact source-HTML duplicate presentations** across 14 other visible families. In several families the duplicates are across levels, not simply within a single level. Their correct-answer fields agree. Because the teacher has accepted Chapter 3, and the duplicate records have existing candidate identifiers, these are recorded for a later controlled cleanup rather than silently changing 14 more families and their identifiers.

Thirty-eight original CPM Review & Preview candidate answer fields still say `Original CPM answer key required`. They were not guessed from the textbook. Their automatic assessment status remains blocked. Student-facing original questions were not changed by this pass.

The original quality-review metadata still includes other historical teacher-review notes; these are retained as provenance rather than deleted.

## Chapter 2 next-pass baseline

The current Chapter 2 mirror `banks/data/CH02.json` contains 117 visible families and 4,212 draft variants (12 per level × 3 levels for each family). A source-HTML duplicate scan identified 102 exact repeated variant presentations across 32 families. These are *candidates* for a more careful lesson-alignment and generator audit, not automatically math errors. Chapter 2 remains `BLOCKED_UNTIL_TEACHER_REVIEW` and was **not modified** by this transfer.

**Next implementation priority:** A Chapter 2 family-by-family audit using the canonical question structures, verified CPM source material, and the fourth/fifth research-pass variation and diagnostic rules. Avoid a mechanical 36-variation quota and preserve source Review & Preview questions separately.

## QA method

Parsed source/updated JSON, verified family and candidate IDs, prompt/answer presence and MathJax delimiter balance, compared all non-target Chapter 3 family objects, checked chapter 1/2 embedded bytes, matched embedded chapter-3 SHA-256 against the JSON payload, independently solved and substituted the 33 new/edited formulas, checked continuous difficulty-candidate indices, and ran a Playwright browser smoke test of all three repaired families. This audit is not a claim that every preexisting answer and CPM original diagram has been independently proof-checked.
