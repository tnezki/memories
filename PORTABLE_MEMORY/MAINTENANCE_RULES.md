# Portable Memory — No-Conflict Maintenance

1. **One source per decision.** This index points to the current manifest/contracts instead of copying their detailed requirements. Do not create a second curriculum philosophy, transfer schema, PM, app architecture spec, or assessment rubric here.
2. **Project-specific truth stays in the owning project.** CPM Tools architectural decisions belong in `CPM_Tools/PROJECT_START_HERE.md` and `CPM_Tools/docs/SHARED_SYSTEM_CONTRACT.md`. Link to them; never fork their full text into a second memory.
3. **Source hierarchy:** current explicit teacher instructions and project-specific current contracts; declared `memories/SYSTEM_MANIFEST.json` and referenced framework/PM/owner files; latest verified local source/transaction evidence for installed behavior; only then older notes for background. Resolve apparent contradictions rather than silently choosing the most convenient copy.
4. **Status discipline:** design agreed != source implemented != built transfer != locally applied != runtime tested. State exactly what has been observed, including known failures and the check that would confirm a fix.
5. **Safety:** do not place real student information, grades, addresses, private records, tokens, credentials, or installation logs containing them in repository memory. Prefer synthetic examples if a QA case needs data.
6. **Update protocol:** only amend a project entry when an actual architectural decision or an observed defect changes its scope. Read the existing entry first, modify only the correct authority, and verify linked paths. Do not update dozens of old PMs just because a chat ended.
7. **Historical files:** do not bulk delete, rename, or mark old Physics/AP Calc/Portfolio assets superseded until their owning authority and current usage are verified. An old timestamp alone does not make an artifact obsolete.
8. **Future chats:** if the Drive mirror is stale or disconnected, ask for a current verified source only when the task cannot proceed, and identify the gap explicitly. Never claim automatic live filesystem access.

## Existing authority locations

- `memories/SYSTEM_MANIFEST.json`
- `memories/SYSTEM_RUNTIME_CONTRACT.txt`
- `memories/Tools/CURRICULUM_TRANSFER_CONTRACT.txt`
- `memories/Tools/LOCKED_BUILDER_UI_CONTRACT.txt` (review against the current accepted CPM Tools implementation before applying historical UI details)
- `memories/README_CURRENT_SYSTEM_MAP.md`

This file is **a navigation/maintenance policy only**; it does not override the original contracts.

9. **Repair first; test drafts are disposable (teacher instruction 2026-11-07).** For CPM Tools, prioritize correcting the shared implementation over preserving experimental teacher-created assemblies. Such files may be discarded/rebuilt when necessary; do not require the teacher to repeat work solely to protect tests. This excludes Portfolio/student data, canonical source banks and approved curriculum or system contracts, which are still protected. Repairs must be regression-tested end-to-end, across representative native courses and Algebra 1, and keep Mac verification distinct from local tests.
