# Deterministic Grading Response Data Contract

STATUS: HARD / REQUIRED
VERSION: district-grading-response-data/1.0
DATE: 2026-09-20

The model grades the evidence and writes **one canonical JSON data file**. It does **not** hand-author response HTML.

## Required workflow

1. Review/grade the evidence.
2. Create the small canonical follow-up content set once.
3. Independently verify every Set 1 answer once.
4. Write `response_data.json` matching this contract.
5. Run packaged `response_contract/response_builder.py`.
6. Add/merge grading-analysis QA/timings into `data/qa.json`, preserving `data/template_qa.json`.
7. Zip the rendered response.

Do not rewrite, restyle, or reconstruct builder-generated HTML.

## Root fields

- `assignment_title` string
- `class_name` string
- `grade_subject` string or null
- `student_packet_summary` string
- `scan_source` request-root relative path when one source PDF can be preserved directly
- `scan_output_name` output filename
- `set1_focus` concise focus line
- `students` array
- `class_summary` object
- `set1` array
- `stations` array of exactly 6 stations: 4 Review + 2 Extension

## students[]

Each object:

- `name`
- `slug` optional stable filename slug
- `evidence_pages`
- `rating`: exactly Convincing / Limited / Incorrect / Not Observed
- `recommended_score` string or null according to teacher grade/score mode
- `strengths` array of concise strings
- `improvements` array of concise strings
- `feedback` concise string
- `highest_leverage_need` concise string
- `practice_intro` optional string
- `practice_questions` array

Each practice question:

- `id`
- `label` concise skill label
- `prompt` MathJax-ready HTML/text
- `workspace` optional CSS length, default `1.05in`
- `visual` optional response-root-relative asset path such as `assets/graphs/q3.svg`
- `visual_alt` optional

## set1[]

Set 1 is the one shared canonical class question pool. Each object:

- `id` unique, e.g. `Q1`
- `section`: `Review` or `Extension / Transfer`
- `label` concise instructional label
- `prompt` MathJax-ready HTML/text
- `answer` MathJax-ready HTML/text
- `teacher_move`
- `discourse_move`
- `workspace` optional CSS length
- `visual` optional response-root-relative asset path
- `visual_alt` optional
- `verification` object with:
  - `passed`: must be `true`
  - `method`: concise independent check description

The deterministic renderer refuses to build Set 1 when `verification.passed` is absent or false.

## stations[]

Exactly 6 objects. Each:

- `type`: `Review` or `Extension`
- `number`
- `title`
- `questions`: 4-6 objects, each with `prompt`, `answer`, optional `visual`, optional `visual_alt`

Stations may draw from or parallel the same small canonical content decisions, but station prompts/answers are stored once here and rendered identically into student/key formats.

## class_summary

- `eyebrow` optional, e.g. `Precalc Class Data`
- `evidence_line`
- `evidence_analyzed`
- `strengths` array
- `needs` array
- `highest_leverage_target` optional
- `groupings` array of `{title, students, note}`
- `limitations`

## Hard rule

The model is the grader/content author. `response_builder.py` is the layout author. Do not swap those roles.
