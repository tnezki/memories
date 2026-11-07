# Current CPM Tools work — checkpoint (2026-11-07)

A **dated checkpoint**, not the canonical architecture or proof of teacher-Mac installation. Read `CPM_Tools/PROJECT_START_HERE.md` for latest state and actual source files for what is installed.

## Last observed issues

- Duplicate native dark builder header: teacher screenshot indicated corrected. Not a fresh automated seven-course UI pass.
- Geometry Chapter 3 problem 3-5 and 3-6: raw `\(...\)` and `\frac` in picker screenshots; reproduced as **one missing dynamically loaded MathJax extension aborting the full grid**.
- Patch in this transfer: shared `app/unified_lesson_engine.py` maps MathJax 3.2.x extensions to `builder/assets/mathjax/input/tex/extensions/`; those JS extension scripts are bundled once offline for all seven courses (not copied per course). The single shared Assembly exporter also embeds optional extension code into self-contained saved HTML. An isolated browser test rendered `\boldsymbol`, `\enclose` and fractions without network requests; full student/teacher PDF generation must still be checked on the teacher Mac.
- Development browser verification: complete available Geometry Chapter 3 source pack plus 3.1.1 duplicates, **622 MathJax formulas rendered**, including 3-5 and 3-6. Mac retest, actual student/teacher downloaded HTML and PDF exports still required.
- CC1 Chapter 3 Learning Focus placeholder visible; earlier Chapter 8 correction did not fill Chapter 3. Fill curriculum content from approved chapter plans and ladders, not generated guesses.
- Library preview clipping and filing of multi-lesson sets remain unresolved.
- Shared Assessment/Portfolio/Roster/Plans/Ladders interface consolidation is **not complete** even though Lesson Builder uses the shared engine.

## Next human checks

1. After Local Only transfer and CPM Tools restart, open Geometry Chapter 3 (3.1.1) and verify problems 3-5 and 3-6 display typeset geometry/fractions. Also spot-check CC2 Chapter 3 math.
2. In a selected combined lesson, verify Assembly preview, Student/Teacher view, edit/reopen, and locally generated PDFs; separately confirm graph/table defaults and readability.
3. Complete learning focus placeholders as curriculum content work, then Library preview and chapter Multi-Lesson Sets filing.

No private student or grading data belongs in this index.

## 2026-11-07 follow-up — user-confirmed and diagnostic findings

- **MathJax:** Teacher reports Geometry picker MathJax is now fine. The 2026-11-07 offline MathJax transfer is confirmed in the Drive mirror; no further MathJax changes needed unless a new example fails.
- **Saved Geometry 3.1.1:** Verified in the mirror at `CPM_Tools_Library/geometry/Shared_Lesson_Builder/Single_Lessons/Lesson_3.1.1`, with `Editable/main.json`, Student HTML+PDF, Teacher HTML. This confirms successful save at approximately 2026-11-07 10:56 ET.
- **Library indexing bug:** Current native Library UI requests `/api/saved-sets` only. That older collection does not include shared-builder `Shared_Lesson_Builder` documents. The result is a missing Library entry even though the save succeeded. Do not repeat the incorrect claim that the lesson failed to save.
- **Repair proposed in this transfer:** native course Library reads a compact shared-document index from the ONE unified lesson engine and displays saved classroom HTML without duplicating documents into `saved_sets`. The source repair applies to CC1, CC2, CC3, Geometry, Algebra 2 and Precalculus; Algebra 1 continues with its existing Library path. Teacher Mac Library/reopen/export test is required; a packaged transfer is not proof of local application.
- **Teacher workflow priority:** disposable experimental created lessons need not be preserved. Fix root causes; no Portfolio/roster/grade/student data edits.

- Geometry Library chapter cap: server formerly passed 4 though Geometry has 12 course chapters. This transfer corrects that cap.

## 2026-11-07 Geometry Library startup regression — confirmed root cause and patch

- Following the initial shared-builder Library integration transfer, Geometry Library showed `127.0.0.1 didn't send any data` inside the iframe. The teacher-Mac `CPM_Tools/.runtime/server.log` captured `ValueError: A valid course ID is required for the native Library` from `course_library_layout.render_html(12)` called through `library_chapter_moves.enhance_library_html(raw,12)`.
- Root cause: the legacy implicit course-ID fallback recognized Geometry's original 4-chapter pilot but not its now-installed 12 chapters. The previous synthetic QA called `render_html(12,'geometry','Geometry')` and therefore missed the actual failing wrapper.
- Repair package `cpm-tools-geometry-library-startup-route-repair-20261107-v1` adds the 12-chapter fallback in the one shared `course_library_layout.py` and enhances the existing QA to invoke the real wrapper and check seven-course ID isolation. No changes to teacher work, canonical banks, Portfolio, server routing, or other course data.
- **Status:** source-level regression reproduced and fixed; teacher-Mac Library load and saved 3.1.1 preview still need a live check. Do not record success solely from transfer verification.

## 2026-11-07 Geometry Library not indexing shared lessons — actual URL rewrite root cause

- Teacher confirmed Geometry Library now loads old V3 saved sets but shows the warning `Shared lessons unavailable: Geometry file not found`. This is **not** a lost-document problem. The prior route smoke test missed the failing browser/API URL.
- Root cause: one shared Library HTML template generated a JavaScript URL by combining `/courses/` + course ID + the literal `/api/algebra/`. A legacy full-page rewrite then prefixed `/api/` again, causing a nonexistent `/courses/geometry/courses/geometry/api/algebra/lesson-library` route. The shared `Open in Assembler` link had the identical double-prefix bug with `/builder/`.
- Current repair: in **one** `app/course_library_layout.py`, define `nativeBase='/courses/'+COURSE_ID+'/'`, append tokenized relative API/editor paths. No per-course workaround, no migration, no teacher-data writes.
- New regression test applies the actual native V3 course rewrite, evaluates real client URL construction, and dispatches six native course URLs through the shared-engine GET handler against temporary saved HTML.
- **Teacher priority (repeat):** repairs are judged on the application workflow, not on recovering disposable test lessons. Do not spend response space praising a found save. Preserve Portfolio/roster/evidence separately, but prioritize system operation.
- **Status:** developed and regression-tested; Mac Library → Chapter 3 → preview → edit → export still needs teacher verification. Do not mark repaired solely because the transfer applies.
