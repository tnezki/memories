# WTC Architecture and Audit + Rebuild — Local QA Report

Status: Requested system edits implemented; the original finalizer defect is now **RESOLVED / PASS** after the follow-up below. All changes remain uncommitted. No remote, branch, commit, pull, or push operations were performed.

## Scope and behavior

- Algebra Framework and Bank profile now require one meaningful shared setup, then exactly Part A, Part B, Part C, Part D. All parts share the situation; independent parts are allowed. Per-part evidence/action/structure authentication replaces forced dependency chains.
- Philosophy owns the durable shared-stimulus principle. Question Structure core, WTC library entry, indexes, and destination guidance were reconciled. Changed package hashes/byte counts were refreshed.
- Bank Map and Complete Bank PMs inherit course architecture and preserve stage ownership. Generic Audit + Rebuild now supports both stages, their specific audits, accepted-map compatibility, registered QA, finalization, and local delivery overrides.
- Control Panel exposes Bank Map and Complete Bank; the legacy unit_bank target remains compatible.
- Canonical Algebra Notes CSS places setup before parts, displays parts in one column, and removes part borders. Notes profile prohibits divider lines and routes canonical content defects upstream.
- Legacy registered WTC mechanical validation accepts named Part labels, compares count/order against the accepted map, and retains duplicate/coverage/shared-stimulus checks. It does not certify mathematical coherence.
- Existing Unit 1 Bank, map, questions, assets, and Notes HTML were not rebuilt. This job changes system architecture and workflow; those artifacts require a separate stage-specific audit/rebuild.

## QA results

- **PASS:** 21 regression tests, including three new WTC tests covering independent four-part acceptance, missing/extra parts, and incorrect/duplicate labels. Existing Bank 3a/3b, Notes 4a, MathJax, and finalizer regression cases passed.
- Pytest was unavailable in both Python runtimes. Tests were executed directly using unittest and the existing standalone test functions; no dependencies were installed.
- **PASS:** Control Panel JavaScript syntax, unique maintenance targets, and current build-registry route resolution.
- **PASS:** WTC CSS checks for setup-first flow, single-column parts, and no part borders. No browser render of existing Notes was performed.
- **PASS:** Changed JSON parses; modified Question Structure files match manifest byte counts/SHA-256 values; referenced CSS/template/build-PM paths exist.
- **PASS:** Local diff whitespace checks in both repositories. Asset files were unchanged.
- **PASS:** Targeted current-authority scan found no remaining “3–5 parts,” required real carry-forward, or mandatory-chain WTC rule in the reviewed PMs/profiles/core/library/indexes/validator. Legitimate chain requirements remain conditional on actual dependency. Historical course artifacts were not rewritten.
- **FAIL:** Universal finalization on a temporary copy of the complete changed-file tree returned `FINALIZATION_QA: FAIL`. `fix_mathjax_output` reported an odd unescaped dollar-delimiter count in `pms_build/bank_complete.txt` and attempted 131 repairs across that source PM and `curriculum_control_panel.html`. The tool applies math-block rewriting to literal source/code content. No staged finalizer rewrites were copied into the working files; temporary staging was removed.

## Original unresolved issue (finalizer resolved by follow-up below)

At the original run, the universal finalizer needed source/code-aware handling before this mixed authority/Control Panel source tree can receive finalization PASS. Its repair logic was not changed in this architecture job. The legacy Bank-v2 validator entrypoints also target older artifact schemas; the generic PM now requires verifying applicability rather than forcing current Banks into retired inventory contracts. Regression results do not certify a rebuilt Unit 1 Bank.

## Exact files changed

- [memories/Curriculum_Philosophy.txt](/Users/troynezki/Documents/GitHub/memories/Curriculum_Philosophy.txt)
- [memories/Tools/qa_bank_3a_contract.py](/Users/troynezki/Documents/GitHub/memories/Tools/qa_bank_3a_contract.py)
- [memories/Tools/tests/test_qa_bank_3a_contract.py](/Users/troynezki/Documents/GitHub/memories/Tools/tests/test_qa_bank_3a_contract.py)
- [memories/_question_structure/QUESTION_STRUCTURE_CORE.md](/Users/troynezki/Documents/GitHub/memories/_question_structure/QUESTION_STRUCTURE_CORE.md)
- [memories/_question_structure/catalogs/destination_design_patterns.json](/Users/troynezki/Documents/GitHub/memories/_question_structure/catalogs/destination_design_patterns.json)
- [memories/_question_structure/catalogs/legacy_question_structure_index.csv](/Users/troynezki/Documents/GitHub/memories/_question_structure/catalogs/legacy_question_structure_index.csv)
- [memories/_question_structure/catalogs/legacy_question_structure_index.json](/Users/troynezki/Documents/GitHub/memories/_question_structure/catalogs/legacy_question_structure_index.json)
- [memories/_question_structure/guides/destination_patterns.md](/Users/troynezki/Documents/GitHub/memories/_question_structure/guides/destination_patterns.md)
- [memories/_question_structure/library/Universal_Question_Structure_Library_v2.md](/Users/troynezki/Documents/GitHub/memories/_question_structure/library/Universal_Question_Structure_Library_v2.md)
- [memories/_question_structure/version_manifest.json](/Users/troynezki/Documents/GitHub/memories/_question_structure/version_manifest.json)
- [memories/curriculum_control_panel.html](/Users/troynezki/Documents/GitHub/memories/curriculum_control_panel.html)
- [memories/frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework/profiles/bank_course_profile.json](/Users/troynezki/Documents/GitHub/memories/frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework/profiles/bank_course_profile.json)
- [memories/frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework/profiles/notes_course_profile.json](/Users/troynezki/Documents/GitHub/memories/frameworks/2_Framework_Algebra_1/Algebra1_Spiral_Framework/profiles/notes_course_profile.json)
- [memories/frameworks/Algebra_1/FRAMEWORK.txt](/Users/troynezki/Documents/GitHub/memories/frameworks/Algebra_1/FRAMEWORK.txt)
- [memories/pms_build/bank_complete.txt](/Users/troynezki/Documents/GitHub/memories/pms_build/bank_complete.txt)
- [memories/pms_build/bank_map.txt](/Users/troynezki/Documents/GitHub/memories/pms_build/bank_map.txt)
- [memories/pms_maintenance/generic_audit_rebuild.txt](/Users/troynezki/Documents/GitHub/memories/pms_maintenance/generic_audit_rebuild.txt)
- [algebra/css/notes_alg.css](/Users/troynezki/Documents/GitHub/algebra/css/notes_alg.css)
- [memories/WTC_SYSTEM_TEST_REPORT.md](/Users/troynezki/Documents/GitHub/memories/WTC_SYSTEM_TEST_REPORT.md)

## Finalizer repair follow-up — PASS

The registered MathJax fixer now supports rendered HTML only. It skips non-HTML source/authority/serialized files, protects embedded scripts/styles/comments/code/attributes, preserves current TeX delimiters, and enables legacy dollar math only through a real MathJax configuration. Real math corruption, unbalanced delimiters, and malformed current configurations remain checked. Source line endings are preserved even when adjacent rendered math is repaired.

- **PASS:** Full `Tools/tests/` suite: 36 tests, including 15 new regression tests. Executed through unittest and the standalone test functions because pytest is unavailable; no dependencies were installed.
- **PASS:** Previous failed finalization QA rerun against 23 staged files inside memories, including both original failure inputs (`pms_build/bank_complete.txt` and `curriculum_control_panel.html`). `FINALIZATION_QA: PASS`; zero repairs, zero warnings, and every staged file byte-for-byte unchanged.
- **PASS:** Both original failure inputs also passed individual finalization checks without changes.
- Algebra was not accessed or changed in this follow-up. Its CSS is outside the new MathJax repair scope; this rerun covers the previous task's memories files within the authorized workspace.
- The original failure above is retained as history. The finalizer defect is resolved; the separate legacy Bank-schema limitation remains as previously reported.
- All changes remain uncommitted. No Git remote, commit, pull, push, branch, or PR operations occurred.

Exact files changed in this follow-up (all under `/Users/troynezki/Documents/GitHub/memories`):

- `Tools/fix_mathjax_output.py`
- `Tools/finalize_output.py`
- `Tools/FINALIZE_OUTPUT_CONTRACT.txt`
- `Tools/tests/test_fix_mathjax_output.py`
- `Tools/tests/test_finalize_output.py`
- `WTC_SYSTEM_TEST_REPORT.md`
