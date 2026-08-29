Algebra 1 Framework v6.41 - Course-Specific Bank + Notes + Practice + Activities + Demos/Investigations + Performance Tasks/Quick Checks + Recurring/Assessment Partners + Curated Reference Brain
====================================================================================================

CURRENT ARCHITECTURE
  Curriculum Philosophy = universal principles
  `_question_structure.zip` = universal question/evidence structures
  THIS Framework = Algebra-specific behavior + exact Unit Assessment Plans
  current task PM = execution procedure
  Tools/CSS/templates = implementation/rendering mechanics

Assessment Plans inside `assessment_plans/original/` are preserved unchanged. Keep Unit Source Alignment (Current Learning Source / Retrieval Source / Mastery Source) distinct from Section Spiral Planning (Intro / Review / Mastery). Section Review is retrieval practice; student-facing Unit Review is current-Unit mastery preparation aligned to Progress Tracker + Summative evidence.

ALGEBRA BANK PROFILE
- Exact Assessment Plan I-cans + Current Learning/Retrieval/Mastery are the instructional spine.
- Canonical instructional/Summative items are constructed/open response; Blooket is the selected-response exception.
- Current resolved section inventory remains 139 canonical items, including 24 in each of the four Practice forms.
- Algebra Practice intentionally allows 3-5 closely related questions in one high-value family when useful.
- Exact duplicates/repeated procedural families are not deterministic defects and do not trigger anti-clone rewriting.
- Graph • Equation • Table • Context are the Algebra representation system; use the applicable forms substantively.
- Natural values/graph-friendly ranges are course-specific requirements in profiles/bank_course_profile.json.

MAP-FIRST REPETITION DISCIPLINE
- For multi-item / multi-section authoring, map the full requested scope before final student materials.
- Use the map to distinguish purposeful repetition from template-driven cloning.
- Repetition with a real Algebra learning/evidence purpose stays; there are no anti-repetition quotas.
- Revise suspicious template clusters at the PLAN stage, not with a late cosmetic diversification pass.


ALGEBRA NOTES PROFILE
- Execution inputs and packaging are resolved by the current Notes PM; this Framework supplies Algebra-specific Notes behavior and exact Unit authority.
- Exact Assessment Plan Learning Targets/I-cans are the instructional spine.
- After WTC, main content is organized into visible I-can instructional clusters.
- Canonical Bank WTC/Examples/YTIs are reused unchanged; current Algebra Banks normally contain six pairs per section, but trust the real Bank.
- Reading, representations, Math Notes, discussion, Examples/YTIs all serve the actual I-can rather than a generic textbook sequence.
- Substantial Algebra reading uses the Conceptual Physics tone benchmark and is usually 3–4 developed paragraphs; bold target vocabulary at first meaningful use.
- Every substantial reading is followed immediately by a 2–3 question Stop and Discuss; later same-I-can checkpoints are normally one focused question.
- Useful Math Notes abundance is encouraged; CPM-informed reference blocks should show actual mathematics and use Graph/Equation/Table/Context together when the I-can supports it.
- Algebra Notes are primarily current-learning instruction; retrieval/mastery support may appear when it serves the current I-can.
- Notability-first; current default workspace is 2.0in and graph max is 2.52in; task/reading wrappers avoid bad page splits when they fit.
- Approved typography baseline: 9pt normal prose/list/table text; 13pt Example/YTI + I-can headings; 18pt major Learning/Vocabulary/Summary/Mistakes headings; 20pt What's to Come / Let's Get Started headings.
- Teacher copy adds red/bold support only inside existing workspaces, including direct answers + conceptual inference support for Stop and Discuss.
- Notes end at Summary + Common Mistakes + blank miscellaneous workspace; no Summary workspace and no embedded Exit Ticket / Notes Exit Check.
- Approved Unit 1 pilot structure/layout is stored in contracts/notes_visual_contract.json and reference_library/notes_layout/. Production HTML still links exactly base.css then notes.css.

ALGEBRA PRACTICE SETS PROFILE
- Execution inputs and packaging are resolved by the current Practice PM; this Framework supplies Algebra-specific Practice behavior and exact Unit authority.
- Practice Sets are downstream renderings of canonical Bank destinations, not a second question-authoring system.
- Per section, current Algebra Bank routes 24 Practice 1 + 24 Practice 2 + 24 Practice 3 + 24 Extra Practice + 6 CYU, plus 18-pair Tarsia and 20-question Blooket when used.
- Repeated families/numeric variants/exact duplicates are rendered faithfully; no anti-clone rewrite.
- Practice 2/3 appear under teacher dashboard resources for assignment choice but remain clean student Practice pages, not answer keys.
- Production HTML links exactly base.css then the UNIVERSAL practice_set.css; the Framework mirror is byte-identical to the Base Practice Starter copy.
- Visible page names are short: Algebra Practice U.S; Set 2/3 append ` :::: Set 2/3`; Extra and CYU use their approved short names.
- Titles are navy text with a horizontal rule, not a filled title box. Two-column data tables are compact/centered 50/50. Decorative graph captions are omitted.
- Initial workspace is ws-25 for every ordinary Practice question; teacher may manually bump any individual problem with existing ws-N utilities.
- CYU uses a 3x2 grid with no per-question workspace and one blank full-page workspace afterward.
- Practice copies finalized Bank figures and does not package graph tools or per-section graph generators.
- Tarsia/Blooket are copied from their canonical Bank exports; `_practice_3` is a filename convention, not derivation from Practice 3.
- See profiles/practice_course_profile.json and contracts/practice_visual_contract.json.

BANK HTML
- unitN.html = normal teaching-order teacher Bank.
- unitN_review.html = same canonical items regrouped by exact I-can, then question_family_id for side-by-side comparison.
- The review page is internal to the Bank folder and does not need a dashboard button/column.
- Persistent Keep/Replace/Multiples OK/Rework/Remap ratings are intentionally deferred to a later review/repair system.

BANK TOOLS
  GRAPH_TOOL_CAPABILITY_INVENTORY.md -> easy-to-find inventory of every supported graph/model type, including multiple Diamond blank-pattern variants.
  tools/~graph_tool_v12.py  -> copy intact into Bank as generate_graphs.py; append approved Unit generation calls.
  tools/~finalize_bank.py   -> copy intact into Bank as ~finalize_bank.py; validates both HTML views, applies MathJax
                               repairs, runs resolved Algebra inventory/response checks, and creates final ZIP.

A produced Bank contains exactly two Python tools. The teacher may inspect either HTML immediately, then run:
  python3 ~finalize_bank.py
from inside the extracted unitN/ folder.

Deployment/file paths: contracts/course_file_structure.json
Algebra Bank course profile: profiles/bank_course_profile.json
Canonical Bank style reference: reference_library/deployment/shared_css/bank.css
Canonical Algebra/Calculus-style Summative print style: reference_library/deployment/shared_css/summative_math.css
Canonical Practice Sets style: reference_library/deployment/shared_css/practice_set.css

v6.29 (2026-08-22): Added map-first Performance Tasks + Quick Checks evidence architecture, approved CSS mirrors, Algebra DOK 3/4 Performance Task action mapping, quiz-like print/scan Quick Checks, mirrored red-answer Performance Task teacher guides, and exact two-root all-course ZIP packaging.
v6.28 (2026-08-22): Demos/Investigations now use a hard plan-first gate. The builder maps every section's Investigation type + real student action + representation/graph decision before any HTML, packages the plan, and must render faithfully from it; graph-heavy Algebra plans get a pre-render graph-use sanity check.
v6.20 (2026-08-22): reconciliation-only cleanup; repaired one malformed Activities sentence/bullet and reconciled Stations / Find Someone Who live CSS paths to the existing course-root files. No curriculum behavior changed.
v6.19 (2026-08-22): Activities now use the full 24-question Practice Set 2/3 routes, 6 stations x 4, all-24 Find Someone Who, same-document directions links from activity names, prompt-before-representation projection DOM order, and compact projection tables. Stale 16-question/subset assumptions removed.
v6.16 (2026-08-21): added Base Practice PM compatibility, Algebra Practice course/visual profiles, canonical-Bank-only Practice rendering rules, deployed practice_set.css reference, exact dashboard folder/file contract, ws-25 default, and Tarsia/Blooket copy rules; Bank and Notes content behavior preserved.
v6.14 (2026-08-21): finalized the approved Unit 1 Notes format/content baseline, including reduced typography scale and 2.52in graph maximum; preserved reading/S&D/Math Notes/content rules and Bank behavior.




ALGEBRA PERFORMANCE TASKS + QUICK CHECKS PROFILE
- Execution inputs and packaging are resolved by the current task PM; this Framework supplies course-specific behavior.
- Normal scope: all 40 active Algebra sections in one run. FIRST create/QA exact I-can evidence maps for both resource families before any HTML.
- Quick Checks are independent quiz-like deeper evidence, roughly 8-15 minutes, print/collect/scan, 1 page preferred and 2 pages maximum, with DOUBLED blank white workspace and unsplit question cards. Build exactly 6 parallel versions/section from one evidence blueprint, using permitted variation plus planned question-order scrambling; the unversioned file remains Version 1 for dashboard compatibility.
- Performance Tasks are Algebra's primary vehicle for DOK 4 and selected DOK 3 evidence. DOK 4 should be a major/dominant all-course role rather than a tiny minority, while still remaining honest to the I-cans; no numeric quota and no artificial DOK inflation.
- Performance Task actions deliberately include modeling/data collection plus movement/building, audit-repair-stress-test, create-trade-reconstruct-evaluate, decision/optimization, and other coherent performances that fit the I-cans. The renderer must make those verbs real and may not flatten all tasks into one page/card shell.
- Graph / Equation / Table / Context is a high-value recurring Algebra route, especially collect data -> table -> graph -> equation (by hand and/or Desmos) -> use/test/evaluate, but all four are not forced everywhere.
- Every Performance Task teacher guide mirrors the student document page-for-page; red answers/sample answers/evaluation guidance sit inside the same student workspaces.
- One returned ZIP has EXACTLY two top-level folders: performance_task___5134zrt/ and quick_check____htq5855/. Each root carries its plan artifacts + section folders. CSS is NOT packaged there; production HTML links shared course-root css/performance_task.css or css/quick_check.css.
- MathJax must wrap visible TeX-style math; raw x^2-style text is not accepted merely because the script tag exists.
- See profiles/performance_tasks_quick_checks_course_profile.json and the two visual contracts.

ALGEBRA DEMOS + INVESTIGATIONS PROFILE
- Execution inputs and packaging are resolved by the current task PM; this Framework supplies course-specific behavior.

- Build all 40 active sections in one run, but FIRST create + QA the complete section-by-section plan artifacts before any section HTML. Each Investigation gets an explicit type, action, artifact, representation/graph decision, materials, and experience sequence; then the renderer follows that plan.
- Demos remain projector-first 5-8 minute curiosity/bridge experiences using demo.css. Students copy/record earlier evidence when later slides need it; later slides normally use those notes rather than repeating prior evidence on-screen. Hook modes may include physical/manipulative reveals, graph/data reveals, class predictions, movement/human models, competing claims, quick data collection, contradictions, and four-view mysteries.
- Investigations are Framework/Assessment-Plan authored optional learning experiences, not Bank/Practice question wrappers. The builder assigns the Investigation type for all 40 sections in the plan before authoring tasks. There is no universal Task 1/Task 2 sequence or fixed middle choreography. Use section-fit actions such as four-view connection, data collection/modeling, movement, making/building, graph comparison, data analysis, critique, gallery/sort work, create-and-trade, and approved tools/simulations.
- Algebra uses Graph / Equation / Table / Context substantively. Section enrichment + future-resource hooks guide Investigation design. The graph-tool inventory is also an active ideation source; Demos/Investigations may generate new supported visuals because they are authoring resources.
- New Investigation student visual baseline uses clean hierarchy, minimal decorative boxes, purposeful workspace, compact tables, prompt-before-representation, and no descriptive captions.
- All Demo/Investigation teacher guides use teacher_guide.css.
- Final all-course ZIP is course-root drop-in: ~demos_investigations_build_plan.json + .html + css/ + demo/ + investigations/.

ALGEBRA ACTIVITIES PROFILE
- Execution inputs and packaging are resolved by the current task PM; this Framework supplies course-specific behavior.

- Build one Activity Options hub per section at activities/uU_S_act1/uU_S_act1.html.
- Use the full canonical Practice Set 2 / Practice Set 3 routes for the two Activity sets; do not casually rewrite or thin the mathematics.
- The hub exposes the approved participation structures; activity NAMES link to projectable directions in the same hub HTML.
- Set 1 uses all 24 Practice Set 2 items; Set 2 uses all 24 Practice Set 3 items. Projection and Find Someone Who use all 24; Stations use 6 stations x 4.
- Projection prompt comes before table/graph/figure; ordinary activity data tables stay compact/centered.
- Do not use Summatives or official Exit Tickets as ordinary Activity content. Do not append an Activity Check by default.
- Tarsia remains in Practice. Normal Activities builds copy Bank figures and do not package/invoke the graph tool.
- CSS: base.css + exactly one selected Activity stylesheet. activity_projector.css is legacy/reference only.
- Preserve teacher-live Activities on later upgrades unless explicitly replaced.


RECURRING + ASSESSMENT RESOURCE PARTNER
--------------------------------------
- Execution inputs and packaging are resolved by the current task PM; this Framework supplies course-specific behavior.
- Warm-Ups: Notability-first; canonical Bank content; current tested two-card page geometry.
- Exit Tickets: projector-only full-screen 2x2 tickets with section A/B/C index.
- Progress Tracker: exactly two printed pages; Mastery Goals + I-cans + portfolio evidence + current evidence status + next move; no ladder/DOK scoring.
- Review: screen study guide + linked review-practice handout; follow actual spiral/mastery target rather than relabeling it to the deployed unit slot.
- Summative: Algebra uses summative_math.css; Physics will use summative_physics.css in the Physics Framework. Active form IDs always come from current Framework/Bank, never a stale rendered HTML; current Algebra resolves to V1-V6 and stale V7/V8 controls are discarded.
- Exact deployed paths and filenames live in contracts/course_file_structure.json.

v6.23 (2026-08-22): added the Recurring + Assessment partner, exact CSS/path contracts, Review Practice path, and Algebra math-Summative stylesheet; removed the stale Physics Summative stylesheet reference from Algebra.


v6.23 (2026-08-22): Warm-Up HTML contract now explicitly forbids the large kicker/subtitle/name/date header and visible workspace boxes; preserves tested Notability card geometry.


v6.23 (2026-08-22): added Summative stale-template precedence guard; current Bank/Framework active form IDs now explicitly outrank old rendered HTML/version selectors.

v6.26 (2026-08-22): added the Demos + Investigations partner/profile and new Investigation student visual baseline; Banks are not required for normal Demos/Investigations builds.

v6.26 (2026-08-22): Demo evidence dependencies now use student-recorded notes instead of repeated carry-forward panels; Investigation teacher guides keep top Strong Synthesis and add an end synthesis replica/answer walkthrough; teacher-guide tables polished.


v6.27 (2026-08-22): strengthened Demos/Investigations variety planning; prototype mechanics no longer propagate by default; added course-specific student-action mode libraries and explicit graph-tool authoring/ideation use for Demos/Investigations.


SINGLE-HTML QUICK CHECK FORMS
-----------------------------
Each active section has ONE Quick Check HTML at the existing dashboard path. That one HTML contains all six parallel forms, print-separated and version-labeled. Do not create _v2 through _v6 HTML files.
MathJax on PT/QC pages uses the exact PM/Framework boilerplate; do not invent a replacement config.


v6.34 FINAL-BYTE RECONCILIATION
- Framework standalone MathJax maintenance tool is now ~fix_mathjax_v10.py.
- Bank finalizer embeds the v10 configuration-alignment repair and runs it before the FINAL ZIP.
- All HTML-producing Base PMs now require a Framework v10 staging repair before their deliverable ZIP.

## v6.36 generic-run reconciliation
Use `Carefully read PM and Run.` with the current executable Base PM. The Base PM determines the operation; this Framework supplies course-specific authority.

V6.41: Preserves Unit Source Alignment and Section Spiral Planning as separate Assessment Plan vocabularies. Section Review is retrieval practice; student-facing Unit Review is current-Unit mastery preparation. Universal question structures now resolve to `_question_structure.zip`; procedure and rendering mechanics stay with PMs/tools.
