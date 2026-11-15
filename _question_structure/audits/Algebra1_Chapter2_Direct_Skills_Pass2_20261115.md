# Algebra 1 Chapter 2 — Direct Skills Pass 2

**Date:** November 15, 2026  
**State:** Draft for teacher review. Automatic assessment generation remains blocked.

## Scope

Input files taken from the verified Google Drive CPM_Tools mirror after Stage 1 installed. No GitHub write, Portfolio student-data change, or changes to Chapter 1 or 3. This source package replaces only Chapter 2 JSON and the matching Chapter 2 inline script in the shared bank page. No JavaScript or styles changed.

## Direct-skill clean-up

- Direct Skills visible families: **24 -> 22**. All original family IDs and historical exemplar records remain present, including hidden ones.
- **19 families rewritten** with **173 independently computed and rechecked fresh direct-skill variants** across all 3 levels.
- **2 redundant families archived**: Lesson 2.1.2 Q068 (rise alone duplicates finding both coordinate changes in Q075), and Lesson 2.1.4 Q083 (reading m alone duplicates reading both m and b in Q082). Prior content preserved in canonical records; teacher feedback namespace unchanged.
- Lesson 2.1.1 Q060/Q061/Q062 now give three different tasks: rate from table, complete table, equation from table. Q060 no longer duplicates coordinate-pair slope.
- Lesson 2.1.3 Q074/Q075/Q076 now ask slope from supplied deltas, compute deltas from points, or classify positive/negative/zero/undefined slope. Classifying every slope as zero was removed.
- Q082 combines reading m and b from slope-intercept form. Q088 handles signed position rates; Q089 handles displacement from signed rate and elapsed time. Q095 includes cheaper A, cheaper B, and equal prices at each difficulty level rather than always A. Q096 always gives labeled unit rates.
- Q102 no longer manufactures Level 2 difficulty by adding "explain both numbers". Q103 finds an initial value not explicitly printed in an equation, and Q104 evaluates a contextual position model.
- Q004/Q005/Q006 introduce increasing algebraic complexity without paradoxical easiest tasks at Level 3; point-slope notation avoids y-(-...) and x-(-...).
- Q011 calculates an equation from two points, including rational slopes at Level 3. Q013 instead checks whether points satisfy a given equation (distinct evidence).
- Existing reasoning families, verified original CPM R&P problems, and all archived MC/extension content are *unchanged*.

## Counts and protection

| Measure | Stage 1 | Pass 2 |
|---|---:|---:|
| Visible families | 62 | 60 |
| Visible direct skills | 24 | 22 |
| Visible variants | 563 | 484 |
| Original CPM R&P problems | 15 | 15 |
| Visible exact duplicate HTML | 0 | 0 |

All revised candidates remain blocked from assessment generation pending teacher approval. The four lessons without sourced original CPM Review & Preview pages (2.1.1, 2.1.2, 2.2.1, 2.3.1) remain unresolved rather than populated with invented sources.

## Validation

- Compared Drive mirror source SHA256 for `banks/data/CH02.json`: `e56ce8530c8d78442832d1ed89257748d4ab4811aa8cea6749f339849da367bb`.
- Compared Drive mirror source SHA256 for `banks/section.html`: `31f86b1221a3f7a464134101fa3442cdf9def2a7520cdc62fbb183b816d0c7c2`.
- Output bank SHA256: `91de81d07ebfe141116c608d3d5ee3ef91f8de519adb7f40a4749aa41398d5f5`.
- Output section SHA256: `173adcef64d09bce7701425f679858390a4340f32494573bfb70fa4f6a2cd1a2`.
- Strict schema, unique IDs, question HTML, MathJax delimiter balance, source provenance, category counts, correct answer keys and independent mathematical checks for **173** newly authored variants passed.
- Confirmed Chapter 1 and 3 inline JSON content *and all other page bytes outside Chapter 2 inline block* unchanged.
- `bank.js` is not distributed; existing teacher-review localStorage key and UI functionality are not rewritten.
- Browser smoke test could **not** execute: Chromium denied local and localhost navigation with `ERR_BLOCKED_BY_ADMINISTRATOR` even for a minimal static HTML page. This is a runtime limitation, not a successful visual test. Verify installed Chapter 2 lesson display and MathJax in the teacher app.

## Next recommended review

Review Direct Skills with the teacher (especially semantic difficulty progression and practical classroom suitability), then audit the 23 reasoning families. Continue resolving original CPM Review & Preview source gaps without inventing publisher questions.
