4B · BUILD PHYSICS NOTES

Purpose: turn the approved 4A Notes Map into complete student + teacher Physics Notes.
Normal automatic inputs:
- current Curriculum Philosophy
- current Physics Framework
- current complete/materialized Unit Bank
- <course>/notes/unitN_notes_map/
- Tools/Physics_Notes_Image_Toolkit/

The 4A map owns story/image/processing-anchor placement. The Unit Bank owns WTC and EX/YTI content. The image toolkit owns source-image inventory/provenance. The Framework owns Physics Notes behavior and deployed layout contracts.

CONTENT-STABLE BANK IDENTITY (v1.1)
4B must recompute the same content-stable Bank fingerprint used by 4A with the bundled Tools/stable_bank_fingerprint.py. Harmless rezipping must not invalidate the Notes Map. Legacy raw-ZIP sha256 fingerprints fail closed and require one fresh 4A run.


v1.3 NOTES OPENING + VOCAB SORT + CSS + PROVENANCE
- Student opening uses KWL-style **What I already know** + **What I wonder**. Do not use an "Expected relationship" box.
- Optional **What I figured out** belongs near the end of the section.
- Finished build provenance is stored under `_notes_provenance/unitN/` so multiple Units can coexist cleanly in the course Notes repository.


v1.3 RESTORES THE ACTIVE VOCABULARY SORT
- Vocabulary Preview remains terms-only, but is immediately followed by the established 3-column prior-knowledge sort.
- Exact headers: Know for sure · Recognize · Don't know yet.
- Exact directions: Sort the vocabulary. Write each vocabulary word in the column that best matches what you know right now. You may move a word later.
- Current universal CSS snapshots are bundled under `references/css/base.css` and `references/css/notes.css` for exact layout/class QA. Production Notes still LINK the course-root CSS rather than packaging duplicate CSS.
