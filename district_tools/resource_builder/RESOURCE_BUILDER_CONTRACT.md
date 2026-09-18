# District Resource Builder Contract

STATUS: REQUIRED
VERSION: district-resource-builder/0.1-pilot

This contract is executable. It turns one structured teacher request into one finished classroom resource package. It replaces the old workflow of copying and editing long prompt templates by hand.

This tool also packages `DISTRICT_RESPONSE_BUILD_STANDARD.md`. Follow both contracts. The shared district standard governs MathJax, graph accuracy, diagrams/visuals, locked CSS, PDF QA, relative links, package integrity, conflict precedence, and the completed QA record. This contract adds the content and output rules specific to the Resource Builder.

## 1. Core purpose - HARD

- Build the resource type selected in `request.json`.
- Treat the selected resource profile and structured controls as authoritative.
- Produce a finished, classroom-ready artifact rather than a prompt, outline placeholder, or list of suggestions unless the selected profile itself is an outline/planning resource.
- Use the teacher's 1-4 I Can statements / learning targets as the primary academic anchor.
- Use attached source files only for content they actually support. Do not invent quotations, data, standards, examples, task details, or student information that are not present.
- Keep teacher-facing implementation complexity out of the final resource package.

## 2. Authority and conflict rules - HARD

Apply the shared district authority order. In this tool, the following structured choices are especially authoritative:

1. selected resource profile;
2. resolved output files;
3. teacher grade level / subject / unit / target(s);
4. resource-specific controls;
5. selected design priorities;
6. time / length / access constraints.

Free-form teacher notes may refine these choices but may not silently change the selected resource type, required outputs, locked CSS, or required QA. If notes conflict with a structured choice, follow the structured choice and record the conflict in `data/qa.json`.

## 3. Common instructional rules - HARD

Across every profile:

- Align every major component to at least one submitted learning target.
- Make the resource age/grade appropriate using the supplied context.
- A target reading/access level may simplify wording, chunking, vocabulary support, and directions, but it may not reduce the intended academic target or reasoning demand.
- Accuracy is always required even if the teacher does not select it as a design priority.
- Do not create filler merely to reach a requested page, slide, station, or question count.
- If the requested amount of content cannot fit legibly in the requested length, preserve readability and record the adjustment rather than shrinking text into an unusable artifact.
- When multiple student versions are created, keep the core learning target coherent across versions.
- Teacher answer keys, evidence guides, notes, and speaker notes must match the exact final student-facing artifact after any layout edits.

## 4. Design priorities

The request may include priorities such as real-world application, inclusion/accessibility, growth-oriented language, engagement, student choice/agency, reasoning, scaffolds, and extension/challenge.

- Use selected priorities where they naturally support the target and profile.
- Do not force a superficial real-world context into every item.
- Do not use growth-mindset language as decoration; keep it concise and authentic.
- Student choice should preserve common evidence expectations.
- Scaffolds should reduce access barriers without automatically reducing the academic goal.
- Extension should emphasize transfer, synthesis, investigation, design, or deeper reasoning rather than extra repetition.

## 5. Source files

Source files may include assignments, textbook excerpts, vocabulary, standards, readings, rubrics, examples, data, images, or other teacher materials.

- Ground the resource in source content when the teacher clearly supplied it for that purpose.
- Preserve source terminology and framing when relevant.
- Do not silently correct or replace source content with outside material unless the teacher explicitly requested research or verification.
- Do not copy long copyrighted passages into a new student resource when a short excerpt, reference, summary, or teacher-provided file is sufficient.
- If a task depends on an attached reading, image, table, graph, or other source, ensure students can access that source in the returned package or clearly identify the included source file.

## 6. Locked response styling - HARD

The request includes exact snapshots and hashes for:

- `response_contract/dashboard_styles.css`
- `response_contract/resource_styles.css`

Copy them byte-for-byte to:

- `assets/dashboard_styles.css`
- `assets/resource_styles.css`

Use `dashboard_styles.css` for `CLICK_ME.html` and teacher-facing guide/reference pages unless a profile requires a native artifact format such as PPTX or CSV.

Use `resource_styles.css` for print-ready HTML/PDF student resources, rubrics, lesson outlines, stations, unit outlines, answer keys, and other compatible documents.

Do not silently redesign a resource because an uploaded source uses another style. Native PPTX outputs should use a restrained district navy/blue/white visual language with strong contrast and readable sizing. CSV output is exempt from CSS but remains subject to structure and QA.

## 7. Response package - HARD

Return exactly ONE response ZIP.

Base structure:

```text
CLICK_ME.html
assets/
  dashboard_styles.css
  resource_styles.css
  graphs/       (when needed)
  visuals/      (when needed)
resource/
  <resolved profile outputs>
teacher/
  <resolved teacher outputs when applicable>
data/
  request.json
  qa.json
```

- Create every path listed in `request.json -> resolved_outputs.required_files`.
- Do not create fake links to optional outputs that were not requested.
- `CLICK_ME.html` must prominently link to every finished primary classroom resource, then teacher materials, then a small completed-QA link.
- Copy the packaged `request.json` to `data/request.json`.
- Use local relative links only.

## 8. Profile rules - HARD

The selected profile snapshot is packaged in `response_contract/SELECTED_PROFILE.json`. Follow its `rules` plus the requirements below.

### Worksheet / Practice

- Build a coherent practice progression tied to the targets.
- Match approximate question count and target length without sacrificing readability.
- Use answer space that matches the response type.
- When requested, provide a complete answer key that matches the final student version.

### Differentiated Worksheet

- Create exactly the requested number of versions.
- Use neutral student-facing labels by default: Version A, Version B, Version C.
- Preserve the same essential targets while varying scaffolding, access, or complexity according to the selected differentiation basis.
- Include teacher differentiation notes describing what changed and why.

### Extension Activity

- Extension must go beyond routine repetition through transfer, comparison, synthesis, design, investigation, modeling, critique, or application.
- If the teacher asks to use student work, only do so when the relevant work/context is actually supplied.
- Respect the target duration; if authentic work requires longer, state that clearly in the teacher guide.

### Formative Assessment

- Diagnose student thinking, not merely right/wrong performance.
- Use the selected response mix and diagnostic balance.
- When requested, include item-level answer/exemplar guidance and likely misconception/next-step notes.
- Distractors must be plausible and content-based, not silly throwaways.

### Rubric

- Criteria must be observable and aligned to the actual task/target.
- Descriptors must distinguish levels with concrete evidence rather than vague words alone.
- For single-point rubrics, use a clear proficiency target with space for evidence above/below expectations.
- Include student self-assessment space when selected.

### Lesson Plan / Lesson Outline

- Timing must add up realistically to the class period.
- Include teacher actions, student actions, and checks for understanding at a level appropriate to the requested detail.
- If a hook, closure, or materials list is selected, include it explicitly.
- Avoid lecture-heavy filler when students can actively process, discuss, practice, investigate, or apply.

### Presentation / Lesson Slides

- Create a finished 16:9 PPTX at `resource/presentation.pptx` and a PDF rendering at `resource/presentation.pdf`.
- Use readable slide design: concise text, strong contrast, meaningful whitespace, and no tiny body text.
- Include the requested number of embedded formative checks.
- When speaker notes are selected, include them in the PPTX and create the requested teacher notes files. Notes must correspond to the final slide sequence.
- When a student handout is selected, create the resolved handout files.
- Use real diagrams/graphs/visuals when instruction depends on them.

### Stations

- Create exactly the requested number of distinct stations.
- Keep each station purposefully different while aligned to the same target set.
- Respect materials restrictions.
- When one-page-per-station is selected, verify actual PDF page boundaries.
- Include answer key/teacher solutions when selected.

### Curriculum / Unit Outline

- Build a coherent progression across the requested number of weeks and meetings.
- Include pacing, lesson focus, evidence/assessment points, and major resources/experiences.
- Include the selected formative, summative, hands-on, and differentiation elements when appropriate.
- Do not overfill the calendar; leave realistic room for instruction, practice, feedback, and revision.

### Blooket Review

Create `resource/blooket_import.csv` using exactly this two-row header structure:

```csv
Blooket Import Template,,,,,,,
Question #,Question Text,Answer 1,Answer 2,Answer 3 (Optional),Answer 4 (Optional),Time Limit (sec) (Max: 300 seconds),Correct Answer(s) (Only include Answer #)
```

CSV rules:

- Question numbering starts at 1.
- Use the requested question count.
- Time Limit uses the structured teacher value for every question unless the profile is later revised to allow per-question timing.
- Correct Answer(s) uses numeric answer positions only (1-4).
- Keep CSV content plain text. Do not place Markdown, HTML, MathJax, commentary, or a teacher explanation inside the CSV.
- Escape commas and quotation marks correctly according to CSV rules.
- Do not add blank rows at the end.
- Provide a separate teacher answer reference in HTML/PDF with richer explanations when required by `resolved_outputs`.

### Other / Custom Resource

- Follow the teacher's custom description and selected audience.
- Use the selected preferred output format.
- If `best_fit` is selected, choose a practical classroom format, record the decision in QA, and still provide all `resolved_outputs` required by the request.
- Do not reinterpret the request as one of the named profiles unless doing so is necessary to create the requested resource; if you do, record that choice in QA.

## 9. MathJax, graphs, diagrams, visuals - HARD

Apply the packaged shared district standard throughout.

Additional Resource Builder rules:

- Math-rich HTML/PDF resources must use the shared MathJax workflow and be visually checked after typesetting.
- Mathematical graphs must come from a dedicated grapher when available, otherwise a deterministic accurate plotting method. Do not fabricate quantitative graphs with an image model.
- If a student prompt refers to a diagram, figure, map, circuit, force setup, geometric figure, table, coordinate grid, data display, timeline, or model, include the actual visual unless creating it is the assessed skill.
- When creating the visual is the assessed skill, provide only the neutral scaffold needed (blank grid, setup sketch, unlabeled structure, etc.) without giving away the answer.
- Save generated quantitative graphs under `assets/graphs/` and other instructional visuals under `assets/visuals/`.

## 10. PDF and native-artifact QA - HARD

- Open every required PDF and visually inspect it.
- Check actual page size/orientation, page counts where constrained, clipping, overlap, blank pages, missing visuals, missing fonts, broken math, unreadable text, and incorrect page breaks.
- Open native PPTX/DOCX/CSV files enough to verify that they are structurally valid and contain the intended content.
- For PPTX, verify slide count, aspect ratio, speaker notes when requested, and that no required visual is missing.
- For CSV, parse it as CSV and verify row count, column count, header rows, numbering, time limit values, and numeric correct-answer fields.

## 11. Required QA record - HARD

Create `data/qa.json` and include at least:

- `overall_status` = PASS or FAIL;
- `shared_standard_version`;
- `resource_builder_contract_version`;
- `selected_profile.id` and `selected_profile.label`;
- `targets.submitted_count` and alignment result;
- `conflicts` structure required by the shared standard;
- `mathjax` structure required by the shared standard;
- `graphs` structure required by the shared standard;
- `visuals` structure required by the shared standard;
- `locked_css.dashboard.expected_sha256`, `actual_sha256`, `matches`;
- `locked_css.resource.expected_sha256`, `actual_sha256`, `matches`;
- `required_files.expected`, `present`, `missing`;
- `links.all_relative_links_resolve`;
- `pdfs.rendered_and_visually_checked` and per-file checks;
- `native_files` checks for PPTX/DOCX/CSV when applicable;
- `profile_checks` for the selected profile's structured options;
- `failures` array.

PASS is not allowed with unresolved conflicts, missing required files, mismatched locked CSS, raw TeX, missing/inaccurate graphs, missing referenced visuals, broken links, placeholder artifacts, clipped/unreadable PDFs, malformed CSV, invalid native files, or profile-specific requirements that were not followed.

## 12. CLICK_ME dashboard - HARD

`CLICK_ME.html` is the only teacher entry point.

It should show:

1. resource name, subject/course, grade level, and unit/topic;
2. one prominent button/card for each primary resource output;
3. a separate Teacher Materials section only when teacher outputs exist;
4. a small completed-QA status/link;
5. no implementation-contract text unless a problem needs teacher review.

Keep the dashboard simple enough that another district teacher can unzip the response and immediately know what to open or print.

## 13. Delivery - HARD

Return only the single completed response ZIP as the authoritative artifact.

The final user-facing line must be exactly:

Unzip it and open **`CLICK_ME.html`**. The package includes the finished classroom resource, any requested teacher materials, and completed QA.
