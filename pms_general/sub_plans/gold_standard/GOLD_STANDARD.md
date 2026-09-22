SUB PLAN PRINT CENTER — GOLD STANDARD v1.2
==========================================

STATUS
------
Teacher-approved reference for Sub Plans output structure, student-handout CSS, print controls, page-break preview, content-routing quality, graph/MathJax behavior, and package navigation.

REFERENCE RUN
-------------
This folder is an approved mockup/test case. Its DATE, SECTIONS, QUESTIONS, ANSWERS, SCHEDULE, STEM CHALLENGE, and SEATING PLACEHOLDERS are examples only. Never copy them into a new run unless independently current and supported.

LOCKED / REUSE
--------------
Copy these into future Sub Plan packages byte-for-byte unless the teacher explicitly reopens the shell:
- assets/sub_handout_madlib.css
- assets/worksheet_styles.css
- assets/runtime.js
- assets/mathjax/tex-svg-full.js

Preserve these structural behaviors:
- index.html has four main actions: substitute bundle, Physics, Algebra 1, AP Calculus;
- print_bundle.html order is hour-by-hour -> General Procedures & Extensions -> seating charts -> STEM challenge/access -> answer keys;
- each academic handout is its own HTML page;
- screen preview shows real white Letter pages;
- live repagination makes page breaks visible before printing;
- student questions use the clean navy/white rounded-card language;
- every student problem has the three support checkboxes;
- answers/evidence mappings appear only in the substitute bundle at the end;
- MathJax is local SVG output using canonical delimiters;
- Cartesian graphs use the registered graph_tool/current district graph standard;
- Physics U1.3 resultant grids follow the current U1.3 Investigation visual format.

SLIDER CONTRACT — HARD
----------------------
The controls do NOT use multiplicative global x individual scaling.

- All workspaces directly sets every problem workspace to the chosen value.
- Problem selector chooses one problem.
- Workspace changes ONLY the selected problem.
- Graph / diagram changes ONLY the selected problem's graph/diagram.
- The selected Graph / diagram slider begins at 0%; keep the configured upper bound from the page/template (gold-standard sample = 160%).
- When Problem = All, the selected Workspace and Graph/diagram controls are disabled.
- Choosing Q5 loads Q5's stored workspace and visual values into the controls.
- Reset returns every problem's workspace and visual values to 100%.
- Resizing one problem may change page flow, but it must not change another problem's stored workspace or visual size.

STUDENT PAGE RULE — HARD
------------------------
Class-period sizing is internal build/QA information only. Do NOT show a Work-time target, class-length calculation, authoring formula, source ID, Question Structure ID, or QA metadata on a student worksheet.

CONTENT-ROUTING FLOOR
---------------------
Every academic handout must map and include:
1. recent/already-covered mastery or I-can evidence worth revisiting;
2. current section evidence;
3. challenge/extension work.

Use the current Philosophy -> Question Structure -> Framework -> PM -> current sources/tool hierarchy. Do not collapse a sub-day handout into a few easy current questions merely because they are quick to generate.

PHYSICS 1.3 REFERENCE SHAPE
---------------------------
The approved sample's shape is a floor for quality, not stale content to copy:
- only 2-3 quick same/opposite/net-force items;
- exactly 3 two-vector NON-PARALLEL resultant grid problems;
- exactly 2 three-vector investigation-style resultant problems;
- enough additional aligned prior/current/challenge work to fill the scheduled class period;
- typical total about 10-12 meaningful problems or more when tasks are brief; actual task demand controls.

Students draw resultants on the same grid and report magnitude plus direction as an angle from +x or a valid compass form.

CLASS-PERIOD SIZING
-------------------
Do not subtract fixed minutes by course. Size Physics, Algebra 1, and AP Calculus for the FULL resolved scheduled class period. Include enough meaningful core work plus challenge/extension that faster students still have productive work available.

Estimate actual student work time item-by-item. A 10-second one-step item is not a multi-minute task. The item-level time map belongs in QA/source-map data, not on the student page.

MATH / GRAPH QA
---------------
- local MathJax SVG only; canonical \( ... \) / \[ ... \] delimiters;
- run the registered MathJax finalizer/audit and visually inspect after typeset;
- zero visible raw/malformed math;
- every Cartesian graph records Tools/MANIFEST.json -> tools.graph_tool provenance and passes the District Graph Rendering Standard;
- Physics vector grids are non-Cartesian instructional diagrams and use the current U1.3 investigation language.

QA
--
A package is not PASS when class-period sizing, evidence mix, slider isolation, MathJax, graph provenance, or student-visibility rules fail.
