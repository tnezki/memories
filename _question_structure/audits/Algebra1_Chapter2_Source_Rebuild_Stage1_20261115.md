# Algebra 1 — Chapter 2 source-grounded content rebuild, stage 1

**Date:** November 15, 2026  
**State:** Teacher review draft, not approved for automatic assessment generation.

## Purpose and treatment of legacy content

This changes the installed Chapter 2 bank, not merely an audit. Preserve the 117 original family records and their identifiers. Hide 27 synthetic families previously mislabeled as textbook Review & Preview, 27 automatically generated unverified multiple-choice families, nine unverified extension families, and seven redundant/invalid direct or reasoning families. Historical family records remain in the canonical JSON with `pilot_hidden=true`; teacher review key namespaces remain intact. Chapter 1 and Chapter 3 embedded data are unchanged byte-for-byte.

The teacher-approved **Chapter 3** content is not revised. The shared `bank.js` change separates Chapter 2's *Reasoning & Representation* category from its *Direct Skills* instead of mixing error-diagnosis tasks into direct practice. Chapter 3 retains its existing layout, categories, and feedback key.

## New visible bank

| Measure | Value |
|---|---:|
| Stored family records | 132 |
| Visible question families | 62 |
| Visible direct-skill families | 24 |
| Visible reasoning families | 23 |
| Visible original CPM Review & Preview families | 15 |
| Visible candidate questions | 563 |
| Repeated visible student-question HTML | 0 |

There is no fixed family or variation quota. The visible generated review pools are reduced and remain drafts. This is **stage 1**, not full independent mathematical validation of all retained variants.

## Authenticated source material

Actual CPM *lesson eBook captures*, not the separate `CCA Ch 2 RPs.pdf` **Resource Pages**, supplied source problem numbers and mathematical content. Answers were derived separately, not claimed to be publisher answer keys.

| Lesson | Source problems retained | Saved Google Drive source ID |
|---|---|---|
| 2.1.3 | 2-31, 2-33, 2-34 | 1HD6f9rv2lBnvgIVqT_O3qNYW1NazHudv |
| 2.1.4 | 2-41, 2-42, 2-43, 2-44 | 1YhWjODUMsRIoyyv4rB6zMYS6QBrB-Ctb |
| 2.2.2 | 2-62, 2-63, 2-64 | 1bAQNrooXOyeo_z5L21d8f5bzGU5nSjkf |
| 2.2.3 | 2-70, 2-71 | 1_7ruXfKbTQm-LkcC2eT0WJ-k09Z3DgGT |
| 2.3.2 | 2-91, 2-93, 2-94 | 1aDdYIgG845V5SzPxbVjmlOG1WIl1ghuB |

All source-backed original problems have one reviewed-source candidate, no artificial Level 2/3 variations, explicit provenance fields, and a blocked assessment status. Their display text has been lightly normalized for readable HTML/MathJax while retaining original number, mathematical givens and requested evidence. Detailed image-dependent exercises were deliberately not imported until illustrations can be reconstructed faithfully.

Original CPM R&P has **not yet been sourced** for Lessons 2.1.1, 2.1.2, 2.2.1, and 2.3.1. The category appears empty for those lessons rather than substituting invented tasks.

## Focused family rewrites

- Q066 (`2.1.2`): uses point pairs where reversing rise/run produces a demonstrably incorrect reciprocal slope; keeps the critique in Reasoning only.
- Q064 (`2.1.2`): asks for slope and sign, rather than claiming that uncontextualized coordinates possess physical units.
- Q078 (`2.1.4`): interprets a physically plausible positive hourly cost or decreasing balance; no negative hourly *charge*.
- Q097 (`2.2.2`): now genuinely converts a rate's time unit, rather than duplicating simple unit-rate calculation; primary skill remapped to SK02.
- Q100 (`2.2.3`): supplies an actual table for a table-to-equation task, rather than a verbal formula.
- Q101 (`2.2.3`): includes an explicit prediction to check, rather than merely asking to evaluate a given equation.

## QA and limitations

- Source preconditions: Chapter 2 canonical SHA256 `42f6beb389cc3517d1d354d3bea69511a1ba9a2a3b1a86d4b5fe9ffa62ae3970`; bank page SHA256 `25d6a0a8e722f32805d33da51c4454961efdc5e00795bc5094c7d899348c49b5`; bank JS SHA256 `26a09e7982052c21fb69178be3d08009756bd2dce6e58bd713ba86da951eb09a`. All were freshly read from the installed Google Drive mirror following the last pass.
- Canonical and embedded Chapter 2 JSON match semantically; all prior family IDs remain unique/present; source numbers occur in actual eBook HTML; reviewed-source original math spot-checks pass.
- 563 visible candidates contain **zero exact duplicate question HTML presentations**. New Q066 slopes independently checked for reciprocal mistakes; new Q100 tabular values independently checked to satisfy derived line equations; 15 original source references checked.
- `bank.js` passes `node --check`. The changed page keeps Chapter 1 and Chapter 3 embedded JSON bytes exactly unchanged and leaves Chapter 3 feedback-storage key untouched.
- **Full headless-browser smoke test timed out in this environment**, both before and during rebuild. Installed visual review, MathJax/graph checks, and manual source fidelity remain teacher-review gates. No automatic test/assessment/Portfolio eligibility granted.
- Candidate pools retained from earlier generated drafts have not all received complete independent semantic/math QA; future passes should review them before approval. The 27 generated MC and nine unverified extensions remain hidden until separate review.

## Next work after teacher inspects stage 1

1. Ground and restore actual R&P originals for the four lessons still missing saved eBook captures, with any required figures from the canonical Graph Tool.
2. Audit and improve all remaining active Direct/Reasoning families lesson by lesson, checking difficulty distinctions, calculations, source alignment and answer neutrality.
3. Rebuild worthwhile optional Extensions and one-correct-answer MC for summative use only after independent validation.
4. Confirm teacher review controls and Chapter 2 notes in the installed UI before progressing to Chapter 1.
