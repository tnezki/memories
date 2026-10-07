ALGEBRA 1 TOOLS - PHASE 3 ASSESSMENT MIGRATION
================================================

Active now:
- Algebra 1 Tools home shell
- Algebra 1 Planner launcher
- newest GitHub Sync launcher
- organized Library view of existing Algebra resources
- local-only vs Local + GitHub delivery preference
- optional Reporting / Portfolio launcher
- Algebra 1 app icon bundled in the macOS app
- Assessment Builder migrates into Algebra 1 Tools on first launch

ASSESSMENT BUILDER MIGRATION
----------------------------
The first time Assessment Builder is opened after this phase, Algebra 1 Tools copies the last working Assessment Builder source into its own assessments/assessment_builder folder, applies the shared CC3-style course-tool shell, and launches that bundled copy.

After the copy is complete, Algebra 1 Tools launches its own bundled Assessment Builder rather than opening the separate legacy Assessment Builder app.

The proven Practice, Quick Check, Checkpoint, Summative, question-generation, and shared print/layout code is preserved during this move.

TRANSITION BRIDGE
-----------------
Checkpoint/Summative state and existing owner-only save destinations still point to the current Algebra owner-data locations so existing work is not broken. Moving that state into the portable Algebra 1 Tools Library is a later migration gate.

Portable teacher copies will ultimately carry the bundled Assessment Builder and will not require the legacy app.

The live local Algebra 1 Tools folder is the runtime source of truth. Its safe diagnostic mirror belongs in memories/_tool_mirrors/Algebra_1_Tools.

PHASE 4 CLEANUP
---------------
- Planner launches directly to /planner/ instead of the legacy Teacher Tools dashboard.
- Algebra 1 Tools uses a versioned bundled icon so macOS can refresh the Dock icon cleanly.
- Legacy Teacher Tools remains on disk only as a migration source/fallback; it is no longer a destination from Algebra 1 Tools.
