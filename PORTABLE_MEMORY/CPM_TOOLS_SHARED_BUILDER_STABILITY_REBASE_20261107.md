# CPM Tools shared Lesson Builder stability rebase - 2026-11-07

- Governing requirement: one canonical Builder and Assembler for all seven courses, with course-specific banks and isolated teacher data.
- Previous stability transfer failed safely because picker.js on the Mac was the newer multi-lesson version, not the older mirrored code used for packaging.
- This transfer rebases on that multi-lesson picker and assembler, retaining combined lesson selection and editing.
- Shared fixes: new sessions use Chapter 1 / first available instead of Chapter 3, remove decorative Review & Preview source artwork from presentation clones, natural-width 11-pt HTML tables, guarded bat measurements table reconstruction.
- Run read-only tools/verify_shared_builder_stability.py after installation, then confirm a table in actual student/teacher PDF.
- Do not change canonical banks, Portfolio, rosters, grades, student data, or teacher overrides. Disposable test lessons need not be recovered.
- Status: transfer created and development-tested; teacher Mac verification not yet complete.
