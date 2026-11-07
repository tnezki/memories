# Portable Memory — Project and Authority Index

Status: **conservative index**, updated 2026-11-07. It tells the assistant *where to read*, not which old project files to execute.

| Requested project | Start with | Verification / limits |
| --- | --- | --- |
| CPM Tools (seven courses) | `memories/Tools/CPM_TOOLS_PORTABLE_MEMORY_POINTER.md` → `CPM_Tools/PROJECT_START_HERE.md` → `CPM_Tools/docs/SHARED_SYSTEM_CONTRACT.md` | Architecture established; verify latest code, transfer transactions and Mac tests. |
| Curriculum Build/control panel | `memories/SYSTEM_MANIFEST.json` → its declared philosophy/framework/PM/runtime and transfer contracts | Existing manifest remains authoritative. No newly invented master PM. |
| Textbook Extraction | `memories/Tools/textbook_extraction/` and course extraction sources declared for the particular task | Current workflow/version **not audited** in this index; inspect before changes. Canonical cards are separate from teacher-created recipes. |
| Physics | `physics/` and any currently declared teacher tool mirror; resolve exact tools/contracts from the current system manifest | **Not audited** for present workflow; don't use old chat files as authority. |
| AP Calculus | `apcalc/` and its declared teacher tool mirror | **Not audited** for present workflow; inspect before changes. |
| STEM | `stem/` and relevant current course materials | **Not audited**; don't infer a shared Physics/AP Calc authority. |
| Portfolio / student data | `memories/SYSTEM_MANIFEST.json` → declared Portfolio and Student Data Tools contracts | PRIVATE: this index stores no records, names, grades, or contact data. Operational status not verified here. |

## CPM Tools fixed decisions (do not fork implementations)

One shared Lesson Builder/Assembler UI, math service, styling, saving and printing system for Algebra 1, CC1, CC2, CC3, Geometry, Algebra 2 and Precalculus, with separate course banks/cards, unit plans/ladders, rosters, Portfolio data and private teacher work. Shared Assessment, Library, Rosters, Portfolio and planning interfaces remain a **target**, not an already completed migration. Consult the current implementation contract for accurate scope.

Keep the mirror as **read-only diagnostic access**; the owner-local install is authoritative for accepted behavior. Curriculum Build changes use one schema-3 Local Only transfer ZIP. Never run Git actions automatically.

No other project entry in this index is an approval to change, delete, consolidate, or reclassify its current files.
