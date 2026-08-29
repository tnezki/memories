# 16 — Build Unit Plan PM

## Purpose
Build one course Unit Plan DOCX from the current course Framework while preserving the embedded Gold Standard document **exactly as the layout authority**.

This PM exists because the Unit 1 Algebra plan was manually refined until its structure, density, voice, links, and pacing behavior were approved as the gold standard. Future Unit Plans should reproduce that standard natively rather than re-designing the document.

## Required authorities and inputs
Read these in this order before editing:

1. `REQUEST.txt` and `REQUEST_MANIFEST.json` — selected course/unit and any explicit run instruction.
2. Current Curriculum Philosophy — curriculum-wide behavior and assessment/portfolio philosophy.
3. Current course Framework — authoritative unit name, sections, learning targets, I-cans, mastery/spiral expectations, vocabulary/concepts, and pacing intent.
4. `inputs/teacher_dashboard.html` — current deployed course resource paths/labels. This is the link authority for course/unit/section resources.
5. `templates/Unit Plan Template Gold Standard.docx` — **layout, typography, table geometry, stable wording, pacing architecture, and visual authority**.

If the Framework cannot resolve the selected unit, the template is missing, or the current Teacher Dashboard is required but missing, **fail closed**. Do not substitute an older copy from another chat or memory.

## Final output
Return exactly one completed DOCX for the selected unit, named:

`Unit_<NN>_<Unit_Name>_Unit_Plan.docx`

Example: `Unit_02_Linear_Functions_and_Modeling_Unit_Plan.docx`

Do not return render PNGs/PDFs unless explicitly requested. They are QA artifacts only.

---

# A. GOLD STANDARD IS FORMAT-AUTHORITATIVE

Start from the embedded Gold Standard DOCX. **Do not recreate it from scratch.** Make only surgical text and hyperlink replacements inside the existing document.

Do **not** change unless the user explicitly asks:

- page size, orientation, margins, section breaks, or page count architecture;
- school logo/header placement;
- fonts, font sizes, bold/italics behavior, colors, fills, borders, or line weights;
- table count, row/column geometry, widths, cell margins, merged cells, or vertical alignment;
- paragraph spacing, indentation, bullets/numbering, or heading placement;
- resource-table layout;
- pacing-guide table layout, day cells, gold/navy styling, or footer guidance box.

The goal is **same document, different unit content** — not a redesigned unit plan.

When replacing text, preserve the formatting of the existing paragraph/run whenever possible. If a replacement must span runs, preserve the paragraph/cell formatting and recreate only the minimum runs needed.

---

# B. SOURCE HIERARCHY

Use this authority order for content conflicts:

1. explicit request packaged with this run;
2. current Curriculum Philosophy;
3. current course Framework;
4. current Teacher Dashboard / deployed link map;
5. embedded Gold Standard template.

The template owns **form and stable language**. The Framework owns **what this unit teaches**. The Dashboard owns **where resources link**.

Do not silently import wording or mappings from old Unit Plans.

---

# C. PAGE 1–2 CONTENT CONTRACT

## 1. Main title
Use:

`<Course>: Unit <N>: <Framework Unit Name>`

Preserve the existing mixed bold/non-bold title styling exactly.

## 2. Essential Standards Taught
Keep the three-part Gold Standard voice and labels:

**Introduced — Unit N Current Learning:**  
A substantive 1–3 sentence synthesis of what students are learning now across the unit. Cover the actual section arc; do not reduce this to a list of nouns.

**Reviewed — Unit N Retrieval:**  
Name the prerequisite or previously learned ideas students must retrieve and use in this unit. Use Framework spiral/retrieval information where available.

**Mastery — Unit N Spiral Mastery:**  
State the earlier skills/ideas students are expected to apply accurately and increasingly independently during this unit.

Depth standard: this cell should communicate the intellectual work of the unit to a teacher who has not opened the Framework yet.

## 3. Essential Standards Mastered
Use the label:

**Mastered — Unit N:**

Write a concise but substantial mastery statement describing what students should independently do by the end of the unit. Include reasoning/interpretation/context/verification when the Framework supports them; do not make mastery sound like isolated procedure completion.

## 4. Dates of Unit
Use only the human-readable marking-period label, e.g.:

`1st Marking Period`

Do not include template notes such as “units 1–2 marking period 1...” in the final document.

Derive the marking period from the current Framework/course pacing when available. For the current 8-unit Algebra sequence, use Units 1–2 = 1st, 3–4 = 2nd, 5–6 = 3rd, 7–8 = 4th unless the current Framework says otherwise.

## 5. Instructional Days
Preserve the Gold Standard phrasing/voice unless the Framework explicitly establishes a different unit length.

For the canonical five-section unit structure, use:

`15 Days – 5+ Days for Assessing/Reteaching/Distractions`

If the number of sections differs, preserve the pacing architecture rather than forcing false dates: normally budget three core days per section plus the assessment/reteach/interruption buffer. Do not change the table design.

## 6. Vocabulary
This must have real depth.

Create a scan-friendly vertical list of the important vocabulary/representations/structures students actually need across the whole unit. Prefer the Framework’s language. Include prerequisite/retrieval vocabulary only when it is genuinely active in the unit.

Use compact paired/grouped forms where the Gold Standard voice benefits from them, e.g. `input / output`, `term / coefficient / factor`, but do not compress unrelated concepts merely to save space.

Avoid a five-word “summary vocabulary” list. The Gold Standard target is roughly the depth of Unit 1: enough terminology to represent all five sections and the important spiral reasoning.

## 7. Essential Questions
Write approximately 8–10 high-value questions spanning the whole unit.

Questions should emphasize the unit’s reasoning, representations, structure, modeling, interpretation, verification, comparison, constraints, or evidence — not merely “How do I solve...?”

Use the Framework as the source. Questions should sound like a coherent teacher-facing inquiry arc. Include at least one question that connects current learning to important retrieval/spiral knowledge when appropriate.

Keep the Gold Standard bullet formatting.

## 8. Common Formative Assessments
Preserve the Gold Standard portfolio language and voice. The core contract is:

- CFAs are collected into the student portfolio/body of evidence.
- Evidence may include Exit Tickets, Quick Checks, Performance Tasks, and other appropriate artifacts.
- The body of evidence drives next-step intervention decisions.

Do not turn this cell into a long catalog of every possible assessment product. Do not replace the portfolio philosophy with a list of DOK tasks unless the current Philosophy explicitly changes the system.

## 9. Common Summative Assessment
Use the unit-specific linked title:

`Unit N Summative Assessment`

Follow it with the Gold Standard curriculum/portfolio language, including that the summative is a driving force in curriculum changes and that selected performance tasks/labs/quizzes/other evidence can complete the portfolio picture.

The linked summative text must point to the current unit summative from the Dashboard/deployed path.

## 10. Unit N Learning Ladder
Change the left label to `Unit N Learning Ladder`.

Create an **8-rung numbered ladder**, condensed from the current Framework’s unit I-cans / mastery progression.

Gold Standard ordering is top-down from highest transfer/creation/critique toward foundational recognition/fluency:

1. design/model/synthesize in context;
2. construct/revise representations or strategies;
3. critique reasoning/solution pathways;
4. assess reasonableness/interpretation/evidence;
5. apply the core unit methods accurately;
6. construct/use representations and connected procedures;
7. compute/evaluate/use foundational operations correctly;
8. identify/classify/read the foundational notation, objects, or structures.

These are structural roles, not canned wording. Every rung must be rewritten to match the selected unit. Preserve first-person `I can...` voice.

Do not paste all Framework I-cans. Condense them into a coherent progression.

## 11. Completed Data Protocols
Leave blank, exactly as the Gold Standard does.

---

# D. RESOURCES CONTRACT

Preserve every Gold Standard resource category, label order, punctuation, line break, and table layout.

### Course Wide Resources
Preserve the canonical labels:
Teacher Dashboard · Student Dashboard · Agenda · Year at a Glance · Activity Structures · Rubrics

For Algebra 1, the embedded Gold Standard links remain the default course-wide links unless the current Dashboard/request provides a newer authority. For other courses, use the current course Dashboard/Framework to replace course-specific destinations; do not knowingly point a Physics or Calculus plan to Algebra-only pages.

### Unit Resources
Update Unit-specific destinations for the selected unit:
Progress Tracker · Review · Assessment Plan · Question Banks · Summative Assessments · Teacher Reflection

### Section Resources
Use Section 1 of the selected unit as the representative section resource links, matching the Gold Standard:
3 Warm Ups · Demo · Notes · Investigation · 2 Activities · Practice · Extra Practice · Check Your Understanding · Tarsia Puzzle · Blooket · 3 Welcome Screens

### Teacher Guides w/Discourse Moves
Notes · Investigations · Demo · Performance Task

### Section Assessments
3 Exit Tickets (4 versions each) · Review · Quick Checks (6 versions) · Performance Tasks · Summative Assessments

Prefer exact hrefs found in the selected unit entry of `teacher_dashboard.html`. Resolve relative hrefs against `PUBLISHED_BASE_URL` from the request manifest. Keep already-absolute hrefs unchanged.

---

# E. PACING GUIDE CONTRACT

## Title
Use:

`Unit N: <Framework Unit Name> – Pacing Guide`

Preserve the existing navy title band and table layout.

## Section pacing
Use the Framework section order. Canonical Gold Standard pacing is three instructional days per section:

**Day A (launch/direct instruction)**
- Welcome
- Warm Up
- Progress Tracker **only on the first day of the unit**
- Notes
- Practice Set

**Day B (investigate/apply)**
- Welcome
- Warm Up
- Investigation
- Activity 1

**Day C (apply/check)**
- Welcome
- Warm Up
- Activity 2
- C.Y.U.
- CFA possible

Then repeat for the next Framework section.

Keep the section heading style as the template uses it (`Section N.S`) unless the current request explicitly asks for abbreviated section names.

## Welcome links
Every instructional day other than the Summative day receives a `Welcome` line.

For each section S and within-section day D = 1, 2, 3, link Welcome to:

`<PUBLISHED_BASE_URL>misc/welcomes/slides/<unit>_<section-index>_<D>_welcome.html`

Example for Algebra Unit 1 Section 1.1 Day 1:
`https://tnezki.github.io/algebra/misc/welcomes/slides/1_1_1_welcome.html`

## Resource links in pacing cells
Every blue/linked resource line in the Gold Standard must remain linked in the new plan.

Use current Dashboard paths where available. Canonical roles:

- Warm Up → unit Warm Ups page
- Progress Tracker → unit progress page
- Notes → section Notes
- Practice Set → section Practice Set 1
- Investigation → section Investigation
- Activity 1 / Activity 2 → section Activities page (both may intentionally point to the same page)
- C.Y.U. → section CYU
- CFA possible → section Quick Check
- Summative Assessment → unit Summative

Do not leave placeholder hyperlinks from Unit 1 when building another unit.

## Assessment/flex days
Preserve the Gold Standard Day 16–20 row behavior. For the canonical 5-section structure, Day 16 contains linked `Summative Assessment`; remaining flex-day cells remain visually as the template shows.

Preserve the four Gold Standard pacing notes at the bottom unless the current Philosophy explicitly changes them:

- Formative Assessments on the third day of a section are possible, not mandatory every time; extra days provide room for other activities, reteaching, and performance tasks.
- Summatives cover DOK 1–3; DOK 4 is assessed through performance work/extended DOK 4 evidence.
- No dedicated pre/post summative review day; comprehensive assessment review/reassessment happens through the established system.
- Students should use the Progress Tracker even without a dedicated review day.

---

# F. LINK RESOLUTION RULES

1. Parse `teacher_dashboard.html` and find the selected Unit object.
2. Use its `meta` links for Unit Resources.
3. Use the matching section’s `studentResources` and `teacherResources` links for Section Resources and pacing.
4. Resolve relative URLs with `PUBLISHED_BASE_URL`; leave absolute URLs unchanged.
5. Generate individual Welcome links from the canonical welcome-slide pattern above.
6. Preserve stable shared Google-resource links from the template only when they are still intentionally shared for the selected course.
7. Never fabricate an opaque filename. If the Teacher Dashboard identifies an obscured dashboard filename, use that exact file.
8. If a required link cannot be resolved with confidence, fail closed and report the unresolved label rather than silently leaving a wrong-unit link.

---

# G. DOCX EDITING METHOD

Use the DOCX skill and follow its render-inspect-iterate requirement.

Preferred approach:

1. Copy the embedded Gold Standard DOCX to a working output file.
2. Inspect `word/document.xml` and hyperlink relationships.
3. Make targeted text replacements in existing cells/paragraphs; preserve cell/table XML and paragraph formatting.
4. Update hyperlink relationship targets surgically; do not rebuild the tables.
5. Only add/remove runs when necessary for changed text length or bold label boundaries.
6. Keep the existing header/logo relationship and images untouched.
7. Render the completed DOCX to PNGs.
8. Inspect every page at 100%.
9. Iterate until there is no clipping, overflow, moved logo, altered table geometry, broken hyperlink styling, unexpected page break, or visual drift.

### Visual QA gate
A final file is not acceptable merely because the text is correct. It must visually match the Gold Standard’s structure.

Compare against the embedded template and verify:

- same page architecture;
- same tables and boundaries;
- title/header alignment unchanged;
- no row/column drift;
- no text clipping;
- no accidental font substitutions;
- no blank extra pages;
- pacing cells remain balanced and readable;
- all expected hyperlinks exist and point to the selected unit/course.

---

# H. FINAL SELF-CHECK

Before delivery confirm all of the following:

- [ ] Correct course, unit number, and Framework unit name.
- [ ] Gold Standard layout preserved; no redesign.
- [ ] Standards Taught has Introduced / Reviewed / Mastery depth.
- [ ] Standards Mastered states independent end-of-unit mastery.
- [ ] Marking Period is clean human-readable text only.
- [ ] Vocabulary has whole-unit depth.
- [ ] Essential Questions have whole-unit reasoning depth.
- [ ] Portfolio-based formative language preserved.
- [ ] Common Summative is Unit-specific and linked.
- [ ] 8-rung Unit N Learning Ladder is Framework-derived.
- [ ] Completed Data Protocols remains blank.
- [ ] Resources retain Gold Standard labels/layout and selected-unit links.
- [ ] Pacing title includes Unit N.
- [ ] Welcome appears on all instructional section days and each Welcome link uses the correct 1/2/3 slide.
- [ ] Every pacing resource line expected to be linked is linked.
- [ ] No Unit 1 URLs remain accidentally in another unit’s unit-specific resources.
- [ ] Summative day is linked; flex days remain in Gold Standard form.
- [ ] Final DOCX rendered and every page visually inspected.

If any check fails, fix it before returning the file.
