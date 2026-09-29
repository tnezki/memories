PLANNER SYNC / PLANNER PAGES
=============================

Planner Sync.app
----------------
Use this Dock app for the same two Planner repository actions:
- Pull All Repos
- Commit + Push All Repos

The Terminal stays visible so repository-by-repository status is easy to inspect.
A completed run ends with a repeated SUCCESS or FAILURE banner.

Planner Pages.app
-----------------
Use this Dock app when you simply want to get back to:
- Algebra 1 Planner
- Physics Planner
- AP Calculus AB Planner
- or all three

If the Planner runtime is not already running, the app starts the existing Teacher Tools Runtime in the background and waits for ports 8767-8769.

Repository scope
----------------
Planner Sync intentionally operates only on:
  algebra
  physics
  apcalc
  teacher_shared

It does not commit/push memories or other curriculum repositories.

Manual fallback
---------------
Run:
  Tools/planner_sync/Run Planner Sync.command pull
or:
  Tools/planner_sync/Run Planner Sync.command push
