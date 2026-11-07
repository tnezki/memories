# CPM Tools — shared Lesson Builder handoff: browser quota regression (2026-11-07)

Status: development regression-tested; awaiting teacher-Mac acceptance.

## Teacher-reported failure
CC1 Lesson 7.1.3: 14 cards checked in the picker, but Assembly shows "No cards selected". Browser reports `QuotaExceededError` while writing `cpm_cc1_library_documents_v90`.

## Current shared architecture repair
- Algebra 1 `builder/assets/picker.js` and `assembly.js` are the canonical actual files for **all seven** courses. No native-course copies.
- The picker caches editable documents **in memory**, writes the changed document to `/api/algebra/lesson-documents`, and navigates only after the server confirms the write. If a server write fails, stay in the picker and show the error.
- Assembly reads the server-backed documents into memory; edits use in-memory state and server persistence. Neither screen rewrites a huge saved-document dictionary into localStorage.
- The older browser source-card and document caches are safely removed after server hydration; official canonical cards and private server copies are not touched.
- Combined lesson selection, Student/Teacher rendering, MathJax, tables, and existing bank/lesson adapters remain unchanged.

## QA
- Static regression and Node syntax checks passed.
- Chromium in-page tests passed with **all localStorage writes forced to throw**: 14-card standalone picker -> server-backed record -> 14-card Assembly; 14-card combined lesson -> Assembly; failed POST -> remain in picker with error. No JS page errors.
- This environment blocks direct localhost navigation, so a real teacher-Mac browser + PDF flow remains the acceptance test. No claim of Mac verification.

## Acceptance
Apply single Local Only transfer, restart app, hard-refresh. CC1 Chapter 7 Lesson 7.1.3: choose 14 cards, build; ensure Assembly shows 14 (not "No cards selected"). Then return/add cards and verify combined lessons. **Do not restore disposable test drafts.** Portfolio/student data is out of scope.
