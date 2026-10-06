CC3 Tools V3 - Full-course student source library

Build a Document now uses the student-facing raw extraction for Chapters 1-10 through chapter-packed card files.

Installed content:
- 1,476 selectable cards across Chapters 1-10
- lesson titles and Learning Focus cards
- Launch / Explore / Methods & Meanings / Closure / Review & Preview content
- student problems with original CPM problem numbers
- instructional links preserved
- referenced local student-content images copied into the portable textbook asset library
- Chapter 1-10 Resource Pages PDFs

Known source-capture gaps are recorded in:
  library/textbooks/cc3e3/source_status.json
  library/textbooks/cc3e3/FULL_COURSE_CARD_BUILD_REPORT.json

Those gaps do not block the rest of the course. Lessons with incomplete captures remain visible in the picker with a Source gap notice; only content actually present in the supplied capture is included.

Architecture note:
- cards/index.json is lightweight metadata for searching/filtering/saved-set scope.
- cards/chapter_XX/cards.json holds the full card content for each chapter.
- the picker loads one chapter pack at a time; the assembler loads only packs needed by the current document.
