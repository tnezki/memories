SUB PLAN PRINT CENTER — GOLD STANDARD v2
========================================

STATUS
------
Teacher-approved reference for Sub Plans output structure, student-handout CSS, print controls, page-break preview, content-routing quality, graph/MathJax behavior, and package navigation.

REFERENCE RUN
-------------
This folder is the approved 2026-09-22 mockup/test case. Its DATE, SECTIONS, QUESTIONS, ANSWERS, SCHEDULE, STEM CHALLENGE, and SEATING PLACEHOLDERS are examples only. Never copy them into a new run unless they are independently current and supported.

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
- workspace/visual sliders repaginate live so page breaks are visible before printing;
- student questions use the same clean navy/white rounded-card visual language;
- every student problem has the three support checkboxes;
- answers/evidence mappings are only in the substitute bundle at the end;
- MathJax is local SVG output using canonical delimiters;
- Cartesian graphs use the registered graph_tool/current district graph standard;
- Physics U1.3 resultant grids follow the current U1.3 Investigation visual format rather than a generic Cartesian-function graph style.

SLIDER BEHAVIOR — HARD
----------------------
The workspace controls are direct stored values, NOT nested multipliers.

- `All workspaces` directly sets every problem's workspace to the chosen percentage.
- `Problem` chooses one problem for local editing.
- `Workspace` changes ONLY the selected problem.
- When `Problem = All`, the individual `Workspace` slider is disabled and its output displays an em dash.
- Selecting Q1, Q2, etc. loads that problem's currently stored workspace percentage into the individual slider.
- Changing one problem may move later problems to different pages because the document repaginates, but it must NOT change any other problem's workspace height.
- Reset restores every problem workspace to 100%, returns the selector to All, and disables the individual workspace slider again.
- The current `Graph / diagram` slider remains a global visual-size control for this gold-standard version.

A future runtime must not restore the old behavior `effective workspace = global multiplier × selected multiplier`; that interaction was rejected because the individual control appeared to change all questions and made 100% ambiguous after a global adjustment.

CONTENT-ROUTING EXAMPLE
-----------------------
The included source map documents why the approved sample worked:
- Physics: validated Section 1.3 bank families plus teacher-directed non-parallel/resultant investigation work; only a few very short collinear problems; three 2-vector non-parallel grid tasks; two 3-vector investigation finishers.
- Algebra 1: classwide recent evidence priority (MG1 graph scale/intercepts) dominates the sheet; current Section 1.2 appears only as a short check at the end.
- AP Calculus: current Notes/Practice 2.3 Continuity + approved Calculus structures; no invented section-level I Can layer.

TIMING EXAMPLE
--------------
- Physics = scheduled class length minus about 10 minutes.
- AP Calculus AB = scheduled class length minus about 10 minutes.
- Algebra 1 = scheduled class length minus about 15 minutes.

Use actual task demand to estimate time. A 10-second one-step problem is not a multi-minute task.

QA
--
Future builds should match the shell/quality level of this folder while replacing every stale run-specific fact with current authority. See data/qa.json and data/source_map.json for the exemplar's traceability.
