BANK-V2 STEP 3A — BUILD BANK INSTRUCTIONAL CORE
===============================================

This folder replaces the old Stage 3A "Bank Seeds" workflow.

3A now authors only exact canonical instructional content from the accepted Bank-v2 map:
- WTC
- Example / You Try It
- CYU
- Warm-Ups

It consumes `banks/unitN_bank_map/` directly. Step 2.6/audited-map output is not required.

Canonical Bank storage is section-sized under `banks/unitN/` with a small BANK_MANIFEST.json and ITEM_INDEX.json.
No giant Bank JSON, no staged checkpoint ZIP source, and no audit-status workflow fields.

Next phase: 3B Practice Families.
