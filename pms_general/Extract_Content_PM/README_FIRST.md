EXTRACT CONTENT — PILOT WORKING PM v0.2
=======================================
STATUS: PILOT / WORKING — test and revise from real jobs.

PURPOSE
Extract requested content faithfully from supplied files without silently rewriting, reconciling, or filling gaps.

AUTHORITY
- The user's current instruction and supplied files are the authority for this GENERAL extraction job.
- Do not load Curriculum Build authorities unless the user explicitly asks to compare/reconcile the extracted material against them.

PROCEDURE
1. Follow the requested extraction scope exactly: text, tables, questions, headings, metadata, figures, etc.
2. Preserve source terminology/order unless the user explicitly requests normalization or reorganization.
3. Distinguish unreadable/missing material from material genuinely absent; do not guess.
4. Use OCR only as a last resort when native/built-in reading cannot recover needed content.
5. When multiple supplied sources conflict, report the conflict unless the user supplied an authority rule.

OUTPUT
Return the extracted content in the requested usable format with source labels when useful.
