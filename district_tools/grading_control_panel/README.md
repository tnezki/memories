# Grading & Evidence Control Panel - Pilot

This is a district-wide pilot tool for packaging student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and assignment/evidence-set name.
2. Upload student evidence (required).
3. Upload a class roster (optional, but strongly recommended for combined handwritten class scans). The roster is packaged under `roster/` and is used only to resolve names, identify unmatched/missing evidence, and preserve class order.
4. Upload a rubric/scoring guide (optional).
5. Every report uses the evidence-rating language **Convincing / Limited / Incorrect / Not Observed**.
6. Choose whether to also return a separate grade/score: none, use the supplied rubric/scoring guide, or recommend a grade from the evidence.
7. Add teacher notes (optional). Clickable hints include a new **Positive + clear fixes** option that asks for specific positive feedback followed by a clear explanation of what is wrong/incomplete and what needs fixing.
8. Click **Build Request ZIP**.
9. Upload the ZIP to ChatGPT. The packaged request is the complete task contract.
10. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

## Evidence rating behavior

The evidence language is fixed across runs:

- **Convincing** - the submitted evidence clearly and sufficiently demonstrates the target.
- **Limited** - meaningful correct evidence is present, but it is incomplete, inconsistent, or insufficient.
- **Incorrect** - the student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.
- **Not Observed** - there is not enough usable evidence to judge the target. Blank, omitted, missing, or unreadable work is not automatically Incorrect.

The evidence rating is independent from the optional grade/score. This avoids the earlier conflict where a run could simultaneously request a grade and prohibit one.

## Optional grade/score

The teacher selects one authoritative mode:

- **No separate grade / score** (default) - reports show the evidence rating only.
- **Use the supplied rubric / scoring guide** - requires a rubric upload and follows the scale actually provided.
- **Recommend a grade from the evidence** - returns the evidence rating plus a teacher-review grade recommendation. Objective item-based work may use points/percent correct; open-ended work may use evidence-based professional judgment. The result is explicitly a recommendation, not a final grade.

Free-form notes may add grading directions but may not silently change the selected mode. Conflicts are recorded in `data/qa.json` and the run continues.

## Built-in response contract

The control panel owns the grading-response build contract directly in `app.js`. Each request ZIP includes:

- `REQUEST_READ_ME_FIRST.md` - complete response/build instructions;
- `request.json` - teacher choices and source manifests;
- `response_contract/styles.css` - locked general response stylesheet;
- `response_contract/stations.css` - locked station stylesheet based on the current Algebra station format;
- style-version files;
- `response_contract/MATH_VISUAL_QA.md` - hard MathJax, graph, visual, evidence-rating, station, and QA requirements;
- submitted evidence, roster, rubric, and teacher notes.

## Stations print option

`CLICK_ME.html` keeps the same three top quick actions, then includes **Stations** under Print Options.

The station set contains:

- **Stations 1-4: Review** - the four most useful things the class needs to fix. Each station has 4-6 questions, prefers one landscape page, and may use at most two pages when needed.
- **Stations 5-6: Extension** - transfer/application/challenge for students showing Convincing evidence. Each also has 4-6 questions.
- If fewer than four distinct misconceptions are genuinely present, remaining review stations become clearly labeled consolidation/prerequisite/transfer work tied to observed needs instead of inventing fake misconceptions.
- A separate complete answer key is required.

The locked station CSS follows the current Algebra station look: letter landscape, Arial, dark navy header, Classroom Copy/Answer Key label, 2x2 problem grid, compact tables/visuals, and landscape solution pages.

Expected station outputs:

- `print/stations/index.html` - teacher landing page;
- `print/stations/stations.html` and `stations.pdf`;
- `print/stations/answer_key.html` and `answer_key.pdf`;
- `assets/stations.css` - exact copy of the locked request stylesheet.

## Requested response package

The response ZIP includes:

- `CLICK_ME.html`;
- `assets/styles.css` and `assets/stations.css`;
- `assets/graphs/` and `assets/visuals/` when needed;
- `scanned_work/` with the combined teacher-friendly source-work PDF;
- `students/` with individual reports;
- `class/class_overview.html`;
- combined report and individualized-practice PDFs;
- common class review/extension packet;
- the six-station set and answer key;
- `data/analysis.json`, `data/qa.json`, and `data/request.json`.

## Math, graphs, and visuals

- Mathematical notation is rendered with MathJax and visually checked in HTML/PDF.
- If a graph is needed, an actual mathematically accurate graph asset is generated and embedded. The response cannot replace it with prose such as "the graph shows...".
- If a question refers to a diagram/image/figure, the actual visual must exist and be embedded.
- These rules apply to stations and answer keys too.

## CLICK_ME dashboard rule

The top contains exactly these three quick actions:

1. **Print All Student Reports (PDF)**
2. **Print All Individualized Practice (PDF)**
3. **View Scanned Student Work (PDF)**

They are not repeated lower on the page. Print Options then contains the distinct choices **Common Class Review + Extension**, **Stations**, and individual student practice links.

## Privacy / data handling

The control panel reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The pilot uses a small built-in ZIP writer (STORE/no compression) so the builder has no third-party JavaScript dependency. The builder loads the locked CSS files into each request ZIP and also contains embedded fallbacks for local/offline operation.
