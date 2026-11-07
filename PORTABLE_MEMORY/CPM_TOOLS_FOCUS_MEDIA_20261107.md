# CPM Tools — shared builder and focus status, 2026-11-07

**Repair first; temporary teacher-built lessons and test PDFs are disposable.** Never modify Portfolio, rosters, student grades, canonical textbook banks, or approved Unit Plans without separately scoped instruction.

## Authority
- One Algebra 1-based Lesson Builder and one shared rendering/runtime engine for seven courses; course content and saved teacher data are isolated by course.
- All interaction changes (card editing, picker, Assembly, MathJax, sizing, Library, exports) must be made once in the shared source and run regression tests across all seven routes.

## Current pending transfer: Shared readable HTML tables + Learning Focus
- File: `CPM_Tools_Seven_Course_Tables_Learning_Focus_20261107_GITHUB_TRANSFER.zip`.
- Repaired issue: CC1 problem 7-14 has a genuine HTML table whose lettering was reduced to roughly one third of size by the global figure setting. Shared engine now keeps HTML tables at 11pt by default; deliberate per-table teacher adjustments remain possible.
- Native CC2 picker sidebar sometimes appears scrolled down on entry; shared runtime resets the sidebar at first load/pageshow. Treat actual Mac verification as pending.
- Focus overlay uses the **approved CC1 and CC2 chapter/unit plans** to author 47 missing CC1 targets and 91 CC2 targets (Chapters 1-9). These are lesson-level teacher adaptations, not verbatim approved Plan quotations or assessment-mastery declarations. Existing completed focuses are preserved. All overlay handling is in shared `app/unified_lesson_engine.py` plus `data/shared_lesson_focus.json`; no canonical source card changes.
- Outstanding: check current Focus coverage for CC3, Geometry, Algebra 2, Precalculus, and Algebra 1 before asserting seven-course content completeness. The engine is shared, but these curriculum materials were not rewritten in this patch.

## Regression
- Browser: actual CC1 7-14 HTML table rendered at approximately 160px width and 11pt after auto size vs 53px wide at old 32% zoom.
- Browser: CC2 picker sidebar restored to top on first load.
- Source-card integration: full CC1 Chapter 7 source pack plus support overlay; checked Focus 7.1.2 and 7-14 unchanged. Mock CC2 Chapter 2 cards insert Focus once after title, with no duplicate on second pass.
- Static: Python compile + Node JS syntax + unique IDs + manifest hash actions passed.
- Teacher Mac acceptance **pending**: confirm CC1 7-14 table in Assembly/PDF; filter CC1 Chapter 3 and CC2 Chapter 2 by Focus; CC2 picker top alignment; check that saved/printed pages remain valid.

Do not declare installed or Mac-verified until the user confirms local transfer application and retest.
