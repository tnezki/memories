# Algebra 1 Chapter 3 - Student prompt clarity and answer-leakage audit

Date: 2026-11-15  
Source: Chapter 3 bank from `Algebra1_Chapter3_Formula_Audit_and_Chapter2_Baseline_20261115_GITHUB_TRANSFER.zip`  
Scope: 115 visible Chapter 3 families / 3,511 active review variants; 56 other hidden/pilot families retained without modification.

## Findings and corrections

**Teacher observation:** `ALG1-CH03-3-2-4-S04` showed the meaningless figcaption "A partitioned rectangle" above a fully presented multiplication model. The actual question already asked students to write the area as a sum and product. The caption served no evidence purpose.

Student-facing corrections, counting **candidate** changes only (not archived sources, exemplar, or metadata copies):

| Correction | Candidate occurrences | Reason |
| --- | ---: | --- |
| Remove "A partitioned rectangle" | 38 | Redundant diagram description; givens and problem unaffected. |
| Remove "Each section is a rectangle. Find the combined area." | 48 | Repeats the mathematical direction already in the prompt. |
| Remove "Cell areas; side labels omitted" | 72 | Internal authoring commentary; labels are visibly absent. |
| Remove "Original CPM 3-xx" prefix from student text | 52 | Source/provenance belongs to teacher metadata, not student question. |
| Remove "Equivalent area model reconstructed from textbook tile layout." | 1 | Internal reconstruction note, not mathematics. |
| Rewrite filled-in partial-product rectangle directions | 24 | The figure already contains all partial products, so "Label each partial product" incorrectly asks for a completed response. New question: "Find the total area by adding the cell areas." |
| Repair "Which expression equals for nonzero x?" | 36 | Incomplete MC stem. It now asks which expression is equivalent for nonzero x. |

**Total distinct active variants changed: 270**, across **56 active families**. Some variants had more than one issue. Teacher-facing exemplar and generator-template wording were reconciled too.

## Student answer-neutrality review

The structural scan traversed all 3,511 visible student HTML variants and found:
- 487 embedded tables, 76 inline SVG figures, 17 images.
- 41 graph-construction variants with an SVG graph; **none showed thick pre-plotted solution relations** under the rule used. Given graphs for read-a-line tasks are permitted because the graph is the evidence stimulus.
- No student markup class/label explicitly marked as a solution or answer key.
- No direct textual inclusion of the complete stored constructed-response answer according to a conservative equality heuristic (a zero-hit heuristic is *not* proof of no leakage).
- Graph labels and diamond-image alternative descriptions inspected for the distinction between givens and requested missing values. The original CPM 3-99 includes a worked example involving a different equation; the example is intentional source material and was retained.
- One genuine duplicate instruction/response mismatch in 24 filled-in rectangle variants was corrected as above.

**Limitations:** Automatic checks cannot guarantee that a figure visually communicates precisely the intended values or that later multipart prose never hints at an earlier result. No figures, images, equations, or answer keys were regenerated. These checks are **static and sampled visual-semantic checks**, not a complete independent visual inspection of every rendered page. Do not mistake a zero-finding result for teacher approval of each candidate.

## Regression protections

Added the portable standard-library QA script: `_question_structure/qa/check_student_question_hygiene.py`. Example use:

```shell
python3 memories/_question_structure/qa/check_student_question_hygiene.py CPM_Tools/banks/data/CH03.json
```

It checks missing MathJax delimiter pairs, student source badges, known redundant captions, answer/solution markers in student HTML, and possible pre-plotted answers in graph-construction tasks. It is meant as an early **failure gate**, not an automatic authoring or grading system. Current result: **0 flagged conditions across 3,511 visible candidates**.

## Preservation checks

- 171 stored families unchanged in number; 115 visible; 3,511 visible candidates unchanged in number.
- Student question/variant IDs, level assignments, answers, worked steps, solutions, assessment eligibility, and review metadata unchanged.
- Original CPM wording retained in `source_original_html` and archival `prior_exemplar` wherever previously present. Source family names retain CPM problem identity for teachers.
- Every pre-existing HTML table, SVG, image, and partitioned-area diagram in the candidate fields byte-equivalent after parsing; none redrawn or algebraically altered.
- The shared bank page preserves Chapter 1 and Chapter 2 JSON script blocks **byte-for-byte**; only the Chapter 3 embedded JSON and Chapter 3 version tag were updated.
- No `bank.js` changes; current teacher review controls and local rating namespace preserved. No Portfolio data touched.
- All generated chapter questions remain blocked from automatic assessment use pending existing teacher-review and quality gates.

Status: **Quality and structure checks passed on the patched data.** Intended as teacher-review quality improvement, not a substitute for final assessment validation.
