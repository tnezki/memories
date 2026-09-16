# Grading & Evidence Control Panel - Pilot

This is a district-wide pilot tool for packaging student evidence into a self-contained grading/evidence request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and assignment/evidence-set name.
2. Upload student evidence (required).
3. Upload a class roster (optional, but strongly recommended for combined handwritten class scans). The roster is packaged under `roster/` and is used only to resolve names, identify unmatched/missing evidence, and preserve class order.
4. Upload a rubric/scoring guide (optional).
5. Choose the **Grade / score output** for the run.
6. Add teacher notes (optional). Clickable note hints cover reasoning, formative emphasis, ignored questions, paired work, multiple methods, explanation/vocabulary, writing mechanics, partial understanding, missing evidence, concise feedback, extension, and unclear scans.
7. Click **Build Request ZIP**.
8. Upload the generated ZIP to ChatGPT. The packaged request is the complete task contract, so no special run phrase is required.
9. ChatGPT is instructed to return one response ZIP. The teacher unzips it and opens `CLICK_ME.html`.

## Built-in response contract

The control panel owns the grading-response build contract directly in `app.js`; no separate PM selection is required. Each request ZIP includes:

- `REQUEST_READ_ME_FIRST.md` - the complete response/build instructions;
- `request.json` - teacher choices, source file manifest, and expected outputs;
- `response_contract/styles.css` - the locked response stylesheet;
- `response_contract/STYLE_VERSION.txt` - the stylesheet contract version;
- `response_contract/MATH_VISUAL_QA.md` - hard MathJax, graphing, visual-creation, and QA requirements;
- `response_contract/MATH_VISUAL_QA_VERSION.txt` - the math/visual contract version;
- submitted evidence, roster (if any), rubric (if any), and teacher notes.

The response contract requires ChatGPT to copy the provided response stylesheet exactly to `assets/styles.css` so dashboards, student reports, class analysis, and printable packets have a consistent visual system across runs.

The same built-in contract now makes visual correctness a hard requirement:

- mathematical notation must be typeset with MathJax and visually checked in HTML and PDF;
- any required graph must exist as a real mathematically accurate SVG/PNG asset rather than being described in prose; a dedicated grapher is preferred when available, otherwise another approved accurate graph-generation capability may be used;
- any referenced image/diagram/figure must actually be created and embedded;
- `data/qa.json` records MathJax rendering checks, grade-output compliance, graph-generation method/assets, visual assets, link checks, PDF checks, and failures. A response cannot claim PASS with raw TeX, a missing graph, or a missing referenced visual.

## Pilot scoring behavior

The teacher now selects one authoritative grade-output mode for each request. Free-form notes may add details, but they cannot override the selected mode. If a note conflicts, the response follows the selected mode, records the conflict, and continues instead of stalling.

- **Mastery level** (default): report exactly one of `Secure`, `Developing`, or `Needs Revision`; no numeric/letter conversion.
- **Feedback only**: return feedback and next steps with no grade or mastery label.
- **Use supplied rubric / scoring guide**: requires an uploaded rubric; use only the scoring/scale the rubric actually defines.
- **Recommend a grade from the evidence**: use a supplied rubric/scale when available. Without one, objective item-by-item work may receive an evidence-based percent/points-correct recommendation when equal weighting is reasonable; subjective/open-ended work falls back to a mastery level rather than inventing a numeric/letter scale.

For combined scans, the request also includes an identity-pass rule: use `roster/` when provided; if a handwritten name remains unreadable after one reasonable pass, assign a stable neutral label such as `Student 01`, preserve the page mapping, flag uncertainty, and continue the run.

## Requested response package

The generated request instructs ChatGPT to return a mostly self-contained ZIP containing (MathJax may be the sole external runtime dependency for HTML math when a local/serialized render is not available; PDFs remain fully rendered/offline):

- `CLICK_ME.html` - teacher dashboard;
- `assets/styles.css` - exact copy of the locked request stylesheet;
- `assets/graphs/` - actual graph assets with their generation method recorded in QA when graphs are needed;
- `assets/visuals/` - actual created diagrams/images/figures when visuals are needed;
- `scanned_work/` - one teacher-friendly combined PDF of the submitted student work with a descriptive class/assignment filename;
- `students/` - one print-friendly report per identified student;
- `class/class_overview.html` - class strengths, common mistakes, pattern counts, groupings, extension readiness, and limitations;
- `print/all_student_reports.pdf` - all individual student reports combined with page breaks;
- `print/all_student_reports.html` - browser-printable equivalent;
- `print/common_review_extension_packet.pdf` and `.html` - one general class follow-up packet based on common needs;
- `print/individualized/` - one student-specific practice packet per identified student;
- `print/individualized_packets.pdf` - the entire individualized class set combined with page breaks;
- `data/analysis.json` - structured analysis behind the reports and print materials;
- `data/qa.json` - required MathJax/graph/visual/link/PDF QA record;
- `data/request.json` - copy of the original request metadata.

## CLICK_ME dashboard rule

The top of `CLICK_ME.html` has exactly three quick actions:

1. **Print All Student Reports (PDF)**
2. **Print All Individualized Practice (PDF)**
3. **View Scanned Student Work (PDF)**

Those three combined actions are not repeated lower on the page. Lower sections contain the individual student report links, class data, the common review/extension packet, and individual student practice links only.

## Privacy / data handling

The control panel reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The pilot uses a small built-in ZIP writer (STORE/no compression) so the page has no third-party JavaScript dependency. `response_styles.css` is the repository copy of the locked response stylesheet; the builder loads it into each request ZIP and has the same CSS embedded as a fallback for local/offline use.
