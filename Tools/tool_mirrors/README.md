# Local Tool Mirrors

Tool mirrors make local-only teacher apps inspectable from GitHub without moving private runtime data to GitHub.

Current mirrors:
- Algebra 1 Tools: local `_algebra_teacher_tools/algebra_1_tools` -> `memories/_tool_mirrors/Algebra_1_Tools/`
- Algebra legacy Assessment Builder migration source: code-only mirror from `_algebra_teacher_tools/assessment_builder/Algebra Assessment Builder.app` -> `memories/_tool_mirrors/Algebra_Legacy_Assessment_Builder/`
- AP Calculus: local `_apcalc_teacher_tools` -> `apcalc/_teacher_tools_mirror/`
- CPM Tools V3: local `CPM_Tools/cc3_tools_v3` -> `memories/_tool_mirrors/CPM_Tools/`

The Algebra legacy Assessment Builder mirror is temporary migration infrastructure. It exists so the working builder can be inspected and absorbed into Algebra 1 Tools without guessing. It should be retired after feature parity is reached.

Privacy rule: mirror source code, templates, configuration schemas, and fake fixtures only. Never mirror real student names, grades, email addresses, accommodations, evidence, uploaded student work, or credentials.

When a tool needs student-shaped data for development, use fictional fixtures that match the real schema.
