COURSE TOOL SHARED UI
=====================
Canonical maintenance source for teacher-facing controls reused by course tools.

Portable course applications MUST bundle the shared files they need; they must not depend on the memories repository at runtime.

Current canonical files:
- COURSE_TOOL_INTERFACE_CONTRACT.txt
- course-tool.css
- course-tool.js

When a shared interaction changes, update this canonical source first, then propagate the same behavior into each course bundle and refresh that course's safe mirror.
