Base Performance Tasks + Quick Checks PM v1.6
==============================================

Purpose: universal map-first mechanics for later evidence resources.

Normal fresh-chat inputs:
1. 9_Base_Performance_Tasks_Quick_Checks_PM.zip
2. current course Framework ZIP

Normal Algebra prompt:
  Carefully read PM and Run.

Map-first repetition rule:
- map the full requested scope before final authoring;
- keep purposeful repetition;
- revise template-driven cloning in the PLAN;
- use no anti-repetition quotas and no late cosmetic diversification pass.

CSS deployment rule:
- bundled reference CSS is not automatically copied into output;
- obey the Framework deployment path;
- if CSS lives in course-root css/, section HTML links to that shared dependency and the two-resource-root ZIP does not duplicate it.


The Framework owns course-specific scope, I-can/evidence expression, actions/materials, DOK role, representation system, tool behavior, exact deployed paths, and package roots.

Current hard QA additions:
- visible TeX-style math must be inside MathJax delimiters; loading MathJax alone does not count;
- if the Framework requires parallel Quick Check forms, map the common evidence blueprint first and then build the exact version count with planned value/context variation + question-order permutations;
- Performance Task renderer must honor the mapped action; stable CSS does not mean a fixed page/card shell;
- when CSS is a shared course-root dependency, any CSS copied inside the returned resource roots is a packaging failure.


v1.4 LOCKED REFINEMENTS
-----------------------
- When a course Framework requests multiple Quick Check forms in one file, build ONE HTML per section containing all complete forms; do not emit separate _v2/_v3/etc. HTML files.
- Each form is print-separated and independently identifiable while sharing one section HTML/dashboard path.
- Use the exact approved MathJax boilerplate from the PM. Display delimiters belong under `displayMath`, not `inlineMath`; invented MathJax configs fail QA.

MathJax v1.4 reconciliation:
- MathJax uses the established course-wide dollar-delimiter contract: $...$ inline and $$...$$ display.
- This matches the course finalizer and ~fix_mathjax repair workflow; do not create a PT/QC-only delimiter convention.


v1.6 FINAL-BYTE GATE
--------------------
Before packaging, run current Framework `tools/~fix_mathjax_v10.py` on both staging resource roots (or their common staging parent), then rerun QA and ZIP only the repaired bytes.

GENERIC RUN
Use exactly: `Carefully read PM and Run.`
The current PM package determines the operation; do not paste an older resource-specific prompt.
