# MAPS Science Tools — Foundation build 1

**Status:** Functional local shell / read-only public Physics catalog. Not a full Lesson Builder, Assessment Builder, Portfolio, or student-data integration.

## What is installed

The first transfer places this portable, self-contained shell under:

`~/GitHub/memories/Tools/science_tools/`

This location uses the already approved `memories` transfer root. The same transfer adds `science_tools -> SCIENCE_Tools` and `maps_memories -> maps_memories` to the Curriculum Transfer *approved-roots seed*, so future transfers can install directly to the existing owner-local `~/GitHub/SCIENCE_Tools/` folder. **Do not manually duplicate this shell into SCIENCE_Tools yet.** We are staging the shared foundation safely before hooking up a teacher-owned runtime.

Launch it with `Start Science Tools.command`. Python 3 and a browser are required. It binds to `http://127.0.0.1:8784/`, does not use a cloud service, does not read personal data and does not write application state to disk.

## Read-only acceptance features

- Dashboard and navigation for Courses, Curriculum Library, Lesson Builder, Assessments, Portfolio, Distribution, Settings.
- Course registry with Physics as the only configured course.
- Existing 107-instructional-day Physics plan shown as a **planning target**, not an imported curriculum map.
- Local index/search/preview of original, public `physics/lessons` assets only.
- Reads the presence of existing `_physics_teacher_tools/` without altering it.
- Both `SCIENCE_Tools` and `SCIENCE_Tools_Library` owner-local directories are recognized as pending destinations.
- Explicitly marks student directory and private Portfolio integration as not configured.
- Bundles canonical `memories/Tools/course_tool_shared` CSS and JS, so it does not rely on external assets to render.

## Source and role audit (2026-11-17)

| Existing source | Verified state | Reuse decision |
| --- | --- | --- |
| `SCIENCE_Tools/` | Empty teacher-local directory in synced mirror | Future owner-local runtime; do not invent prior content. |
| `SCIENCE_Tools_Library/` | Empty teacher-local directory in synced mirror | Future saved teacher library. |
| `_physics_teacher_tools/` | Existing Physics app/server, planner, lesson/practice/warm-up controls | Keep operating unchanged; integrate by interface later. |
| `CPM_Tools/app/` | Live multi-course lesson engine and Portfolio/assessment modules | Reuse shared patterns/engines after API audit; do not copy full backend. |
| `memories/Tools/course_tool_shared` | Shared UI CSS/JS and interface contract | Bundled exactly into this build. |
| `physics/lessons/` | Existing public Physics lesson resources | Indexed **read-only** and locally previewable. |
| `__MAPS_Student_Data` (district Drive) | Planned authoritative district student-data source | **Not connected.** No contact, roster, IEP/504 or NWEA import. |

## Architecture boundaries

- **MAPS Student Data:** District-managed authoritative contacts, PowerSchool roster exports, authorized Student Services supports and NWEA data, with school-approved permissions. No private data moves into GitHub or GitHub Transfer.
- **MAPS Memories:** Intended district-wide documentation authority. Its repository is present; this transfer authorizes the root for **future reviewed transfers** but does not write to it.
- **Physics repository:** Public original interactives and course source; existing published links should not be rewritten.
- **Teacher-local Science Tools:** Future runtime for teacher saves, Library and Portfolio connections. It will access district data only after validated import contracts and permission review.

## Next implementation stage

1. Install shell into approved owner-local `SCIENCE_Tools/` and confirm the teacher's Mac entrypoint.
2. Connect the approved Physics 107-day map (including reading, thinking sheet, simulation, video lab), preserving the source order.
3. Define a narrow adapter to the **existing** Physics lesson and CPM shared Builder systems. Require working save/reopen and print before calling it an integration.
4. Add assessment and Portfolio adapters only after authoritative source/ownership verification.
5. Publish district-wide architecture records to `maps_memories` in a later reviewed transfer; never include student-specific data.

Do not treat planned integrations as functioning merely because they appear in navigation.
