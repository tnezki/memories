# Algebra 1 Chapter 2 - Targeted Bank Repair Pass 1 (November 15, 2026)

## Verified source state

- Latest connected Drive mirror: `CPM_Tools/banks/data/CH02.json`, SHA-256 `27b3e64bc115f02e867956447002aec2920a5fa4b0191902d12cad492aa79727`.
- Shared embedded bank page: `CPM_Tools/banks/section.html`, SHA-256 `823efec419534c8bea67c1e7f26f5122d5db2b5d044c27cab9f69771c6a6bb5b`.
- Current Chapter 3 bank: SHA-256 `0e4702b565ddc909f7d378240cdd0249cada9427c70d20709eabb13504de75c8`, matching the teacher-accepted latest patch. Chapter 3 is not modified.

## Exact change scope

Only four Chapter 2 families were modified, with all 36 existing L1-L3 candidate IDs in each one preserved. **144 total candidates repaired**:

1. `ALG1-AP1-2-1-1-R01`: replaced all-yes equation/table checks with balanced matches and single incorrect entries; corrected family metadata from three-representation/graph claims to the actual table/equation evidence.
2. `ALG1-AP1-2-1-1-R02`: replaced multi-task find slope/write rule with one demonstrable constant-rate goal across three intervals. Level 1 has unit x steps; Level 2 uses unequal x intervals; Level 3 uses rational rates.
3. `ALG1-AP1-2-1-1-R03`: replaced all-not-linear single tables with two genuinely contrasting patterns (one linear, one non-linear), alternating which is correct; Level 3 uses unequal x intervals and rational rates.
4. `ALG1-AP1-2-1-3-R03`: replaced given answer slopes with two ordered-pair data sets requiring calculations, balanced which slope is greater, including signed and fractional rates.

All changed questions have independently computed answer fields and worked steps. Candidate statuses remain `PENDING_TEACHER_REVIEW`; assessment eligibility remains `false`. No question family, stable variant ID, source provenance, or historical `prior_exemplar` was deleted.

## QA completed

- Independent mathematical parser/checks passed for all 144 candidate questions (not merely trusting generated key text).
- All 117 family IDs and 4,212 candidate IDs preserved, 113 family records untouched.
- Source and embedded Chapter 2 JSON are structurally identical; Chapter 1 and Chapter 3 embedded JSON script blocks byte-identical to the verified installed source.
- JS static syntax (`node --check`) and review wiring check passed. `bank.js` remains unchanged. Chapter 2 and Chapter 3 feedback use distinct localStorage keys; no existing feedback is reset.
- Exact duplicate HTML presentation count using strict string equality decreased from 235 redundant entries to 221 (14 removed). Remaining duplications are future-pass work, including semantic duplicates not detected by exact matching.
- All ZIP replacement entries have verified SHA-256 preconditions against the connected mirror and safe local-only paths.

**QA limitation:** Headless Chromium rendering of the entire 10 MB shared bank page timed out. The first-pass transfer is validated for structural/math correctness, not certified as a completed visual-browser smoke test. Check Chapter 2 teacher preview and review buttons in the installed app after applying the transfer.

## Deliberately deferred

- Remaining 113 Chapter 2 families: pedagogical and mathematical audit.
- Full scan for answer-neutral figures, missing CPM Review & Preview original fidelity, unverified answer keys and mixed-level near duplicates.
- Full visual inspection of all three levels and live teacher review/export interaction.
- Family count and variation quota simplification. Twelve candidate positions per level are retained in this first targeted patch to avoid incompatible navigation changes.
- All Chapter 3, Chapter 1, Portfolio student records, Assessment Builder/scan/mail system and personal teacher review records are untouched.
