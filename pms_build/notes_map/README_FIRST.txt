4A BUILD NOTES MAP v1.6
======================

PURPOSE
Design the Physics Notes instructional story BEFORE prose is written.
Sequence the best Hewitt/source-textbook images, conceptual reading beats, the already-canonical Bank EX/YTI anchors, WTC placement, vocabulary development, and Stop & Discuss processing.

FIRST TASK
READ THE CURRENT CURRICULUM PHILOSOPHY COMPLETELY FROM THE PINNED SNAPSHOT, THEN FOLLOW THE DETERMINISTIC RETRIEVAL BLOCK IN THE PM.

RETRIEVAL PERFORMANCE RULE
- Read the Curriculum Philosophy directly from the exact pinned text file named by the request/control plane.
- Resolve Physics through `frameworks/MANIFEST.json`; read the stable `frameworks/Physics/FRAMEWORK.txt` front door and only the supporting files listed by `frameworks/Physics/MANIFEST.json` that 4A requires.
- Resolve the Physics Notes Image Toolkit from `frameworks/Physics/MANIFEST.json` as a COURSE resource; read `resources/Physics_Notes_Image_Toolkit/IMAGE_CATALOG.json` from the pinned Physics repo and inspect only selected images as needed.
- No web search, repository archaeology, or fallback to old/deployed copies when the canonical pinned path exists.
- Routine retrieval mechanics stay silent. If the prescribed route fails, fail closed with the exact repo + commit + path.

REQUIRED INPUTS
1. This PM package
2. Current Curriculum Philosophy
3. Current Physics Framework
4. Current complete/materialized Unit Bank
5. Physics course resource: `resources/Physics_Notes_Image_Toolkit/` (resolved by the Physics Framework manifest)

IMPORTANT AUTHORITY SPLIT
- The Unit Bank owns canonical WTC / Example / YTI wording, values, figures, and solutions.
- The Physics Notes Image Toolkit owns the image inventory and provenance.
- 4A owns Notes sequencing/planning only.
- 4B will own final Notes prose/rendering/package mechanics.
- _question_structure/ is NOT required for 4A; 4A does not author new Bank questions.

OUTPUT
unitN_notes_map/

CANONICAL STORAGE
Save/extract the expanded folder at `<course>/notes/unitN_notes_map/`. A ZIP may be returned only as the download/handoff container.

DO NOT deploy the Notes Map as Notes. It is a planning checkpoint for 4B.

HARD STOP & DISCUSS VALIDATION
Before PASS, every Stop & Discuss anchor must keep source_image_ids as verified PHYS-XXXXXXXXXXXX toolkit IDs and expected_reasoning_evidence_to_listen_for as teacher-facing reasoning text. Swapped/overloaded fields fail closed.

CONTENT-STABLE BANK IDENTITY (preserved from v1.2)
4A must fingerprint the Bank by authored content, never by raw unitN_bank.zip bytes. Use canonical `Tools/stable_bank_fingerprint.py`. Primary identity is STAGE_3E_HANDOFF.json canonical_authored_content_sha256; deterministic extracted-content manifest is the documented fallback.
