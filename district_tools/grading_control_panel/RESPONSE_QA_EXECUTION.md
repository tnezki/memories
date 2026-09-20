# Grading Response QA Execution Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-response-qa-execution/1.1  
DATE: 2026-09-20

## Purpose
Keep response QA rigorous without turning every six-student grading run into a full-package rerender loop. This guide changes QA execution order, not quality requirements.

## 1. Evidence review is not reduced
Student evidence still receives the visual/semantic inspection needed to grade it accurately. Scanned handwriting, diagrams, and ambiguous pages must be inspected as needed. Do not use this guide to skip evidence review.

## 2. Build once before visual QA
Generate the complete response package in one coherent pass whenever possible. Do not repeatedly render intermediate drafts of unchanged artifacts.

## 3. Programmatic checks first
Before expensive visual rendering, run inexpensive checks across the full package:

- required files and folders exist;
- local links resolve;
- request/analysis/QA JSON parses;
- locked CSS bytes/version/SHA-256 match the packaged contract and `RESPONSE_LAYOUT_LOCK.md`;
- MathJax source has no obvious raw/unclosed delimiters;
- Set 1 counts and reuse mappings match across all views;
- Activity Options structure matches the one-set Algebra u1_1 architecture;
- Find Someone Who left-rail controls exist and the generic old Set 1 card menu is absent;
- Review vs Extension labels exist where required;
- graph provenance records name the packaged registered graph tool;
- expected graph assets exist;
- duplex page-count logic is internally consistent;
- PDF files open and report plausible page counts;
- Print Presentation count implies exactly two Set 1 questions per page;
- Student Set does not contain deliberate fixed-question page breaks unless content truly requires them.

Fix programmatic failures before broad visual QA.

## 4. Gold-shell check before rendering
Confirm unchanged gold surfaces still use the locked class hierarchy. Do not redesign or rerender a stable page just to explore a different layout. Only the approved exceptions in `RESPONSE_LAYOUT_LOCK.md` may change structure.

## 5. Targeted visual QA
Visually render the pages that are most likely to reveal layout/math problems:

- every page containing a mathematical graph or nontrivial diagram;
- first page and one later representative page of each distinct output template;
- Print Presentation first page plus any page containing an oversized figure;
- Student Set pages around actual page breaks;
- Find Someone Who first page plus any graph-heavy page;
- Cut-Apart Cards first page plus any card with a large figure;
- Station/student/practice/report pages that are layout outliers by content length or page count;
- any page flagged by programmatic checks.

Locked CSS/templates that already pass do not require every near-duplicate student page to be rerendered just because the student's text differs.

## 6. Correction loop — only changed artifacts
If QA finds a defect, regenerate and rerender:

1. the artifact that changed;
2. any combined PDF or index directly dependent on it;
3. any page specifically affected by the same systemic rule.

Do **not** rerender unrelated stable artifacts or the entire package after a local fix.

## 7. Graph QA remains strict
Graph pages are never skipped merely because the layout template is trusted. Every supported Cartesian graph must record the packaged registered graph tool as renderer. Visually inspect graph-heavy pages for readability and mathematical accuracy.

## 8. Duplex QA
Verify duplex pairing programmatically for every student segment. Visually inspect representative transition points and any segment whose page count changed after a correction. Do not rerender every unchanged report/practice page only to reconfirm the same blank-back template.

## 9. QA record
`data/qa.json` should record:

- programmatic checks run;
- pages/artifacts visually rendered;
- graph provenance checks;
- changed artifacts rerendered after fixes;
- dependent combined PDFs rerendered;
- explicit note that unchanged stable artifacts were not redundantly rerendered.

PASS still requires no unresolved failures.
