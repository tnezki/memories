LOCAL TOOLS
===========

Use Local Tools.app as the daily local front door.

FIRST PAGE
----------
Student Data
- Portfolio
- reports
- email workflow

Planner
- Algebra 1 local Planner
- Physics local Planner
- AP Calculus AB local Planner
- Open All

Sync
- Pull All Repos
- Commit + Push All Repos

Sync includes the canonical `memories` system repo plus algebra, physics, apcalc, and teacher_shared.

Co-Teacher Agendas
- Algebra 1 hosted agenda
- Physics hosted agenda
- AP Calculus AB hosted agenda
- Teacher Shared home

HOSTED VS LOCAL
---------------
Local Planner pages are editing tools.

The co-teacher agendas live in the teacher_shared repository and are hosted from:
  https://tnezki.github.io/teacher_shared/

Local routes under /shared/... are preview/troubleshooting only.

CURRICULUM TRANSFER
-------------------
Curriculum Transfer remains a separate Dock app.

Manual fallback:
  Start Local Tools.command

Local page:
  http://127.0.0.1:8770/


OWNER-PAGE CO-TEACHER LINKS
---------------------------
Planner owner-page Co-Teacher Agenda buttons open the hosted teacher_shared pages,
not localhost preview routes. Local Tools automatically repairs an older local
Planner source on startup when needed.

Manual repair fallback:
  Fix Planner Co-Teacher Links.command
