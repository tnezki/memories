(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.5";
  const STATION_STYLE_VERSION = "district-grading-station-style/1.0";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.5";
  const COMMON_PRACTICE_VERSION = "district-grading-common-practice/1.2";
  const RESPONSE_QA_VERSION = "district-grading-response-qa-execution/1.0";
  const GRAPH_RENDERING_STANDARD_VERSION = "district-graph-rendering-standard/1.0";
  const REQUEST_SCHEMA = "district-grading-request/1.0-pilot";

  const RESPONSE_CSS_FALLBACK = String.raw`:root{--ink:#172033;--muted:#5d687b;--line:#d5dde8;--soft:#f4f7fa;--panel:#fff;--hero:#eef3f8;--accent:#365f82;--accent-dark:#284b68;--success:#176b46;--warn:#8a5a00;--shadow:0 8px 24px rgba(20,34,50,.06)}*{box-sizing:border-box}html{background:#fff;color:var(--ink)}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:var(--ink);font-size:16px;line-height:1.5}a{color:var(--accent-dark)}.wrap{max-width:1180px;margin:0 auto;padding:20px}.hero{background:var(--hero);border:1px solid var(--line);border-radius:20px;padding:24px 28px;margin:10px 0 20px}.hero h1{margin:0;font-size:36px}.quick-actions,.inline-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 15px;border-radius:10px;border:1px solid #9fb4c8;background:#fff;color:var(--accent);font-weight:800;text-decoration:none}.btn.primary{background:var(--accent);color:#fff}.section{margin:18px 0;background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px}.grid,.student-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.card{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fff}.card-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.question-review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:9px}.question-review-card{border:1px solid var(--line);border-radius:10px;padding:10px}.question-source{font-size:11px;text-transform:uppercase;font-weight:800;color:var(--muted)}.question-review-card details{margin-top:6px;border-top:1px solid #e3e7ed;padding-top:5px}.question-review-card summary{cursor:pointer;font-weight:800}.teacher-move,.discourse-move,.answer-box{font-size:12px;background:var(--soft);border-radius:7px;padding:7px;margin-top:5px}.presentation-shell{height:100vh;display:grid;grid-template-rows:auto minmax(0,1fr) auto;overflow:hidden}.presentation-head{padding:9px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:center}.presentation-question{display:flex;align-items:center;justify-content:center;padding:14px 22px;min-height:0;overflow:auto}.presentation-card{width:min(1100px,96vw);font-size:clamp(22px,2.4vw,38px)}.presentation-nav{background:#fff;border-top:1px solid var(--line);padding:9px 14px;display:flex;justify-content:space-between;gap:8px}.report-page,.practice-page,.packet-page{max-width:8in;margin:0 auto}.feedback-box,.practice-block{border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0}.duplex-blank-page{display:none}.math-display{margin:10px 0}.visual-block img,.graph-frame img{display:block;max-width:100%;height:auto;margin:0 auto}.set-head,.activity-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;border-bottom:1.5px solid var(--line);padding:0 0 8px;margin:0 0 12px}.set-head h1,.activity-head h1{font-size:23px;margin:0}.set-head p,.activity-head p{margin:2px 0 0;font-size:12px;color:var(--muted)}.student-set-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 14px}.student-question{border-top:1px solid #dce2e9;padding:9px 2px;break-inside:auto;page-break-inside:auto}.teacher-guide-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:10px}.teacher-question{border:1px solid var(--line);border-radius:10px;padding:11px;break-inside:avoid}.print-presentation-page{width:8in;min-height:10in;margin:0 auto 18px;padding:0;background:#fff;display:grid;grid-template-rows:1fr 1fr;gap:.16in;break-after:page}.print-slide{border:1.5px solid #9ca8b5;border-radius:10px;padding:.18in .22in;display:flex;flex-direction:column;justify-content:flex-start;overflow:hidden;break-inside:avoid}.print-slide .slide-number{font-size:11px;font-weight:800;color:var(--muted);margin-bottom:4px}.print-slide .slide-question{font-size:clamp(18px,2.1vw,28px);line-height:1.25}.print-slide img,.print-slide svg{max-height:3.25in;max-width:100%;object-fit:contain}.structure-menu{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.structure-card{border:1px solid var(--line);border-radius:10px;padding:11px}.structure-card h3{margin:0 0 3px;font-size:16px}.structure-card p{margin:3px 0;color:var(--muted);font-size:12px}.structure-directions{max-width:900px;margin:0 auto}.structure-directions .direction-row{display:grid;grid-template-columns:135px 1fr;gap:12px;padding:8px 0;border-top:1px solid #e1e5ea}.cut-card-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.cut-card{border:1.4px dashed #777;border-radius:7px;padding:10px;min-height:150px;break-inside:avoid}.find-someone-sheet{display:block}.find-someone-box{border:1.4px solid #222;border-left:8px solid var(--accent-dark);border-radius:0;padding:10px 12px;margin:0 0 12px;break-inside:avoid}.find-someone-box .signature-line{font-size:12px;font-weight:800;margin:8px 0 6px;padding-bottom:5px;border-bottom:1px solid #bbb}.find-someone-box .workspace{min-height:1.15in;border:1px dashed #999;margin-top:4px}.partner-line{margin-top:10px;border-bottom:1px solid #555;height:20px}.worksheet-section-label{font-size:13px;font-weight:900;text-transform:uppercase;letter-spacing:.055em;padding:7px 10px;margin:14px 0 8px;border-left:5px solid var(--accent-dark);background:#f1f5f8}.worksheet-section-label.extension{border-left-color:#667085;background:#f6f6f7}.screen-page{max-width:8.5in;min-height:11in;margin:14px auto;background:#fff;border:1px solid #cfd7e2;box-shadow:0 3px 18px rgba(20,34,50,.08);padding:.45in}.page-break{break-before:page;page-break-before:always}@media(max-width:700px){.student-set-grid,.cut-card-grid{grid-template-columns:1fr}.screen-page{min-height:0;margin:0;border:0;box-shadow:none;padding:14px}.structure-directions .direction-row{grid-template-columns:1fr;gap:2px}}@media print{@page{size:letter;margin:.48in}@page presentation2up{size:letter portrait;margin:.25in}body{font-size:11pt;background:#fff}.quick-actions,.no-print,.screen-only,.presentation-nav{display:none!important}.duplex-blank-page{display:block;height:9.9in;min-height:9.9in;break-after:page;page-break-after:always}.card,.practice-block,.feedback-box,.question-review-card,.teacher-question,.cut-card,.find-someone-box{break-inside:avoid}.screen-page{max-width:none;min-height:0;margin:0;border:0;box-shadow:none;padding:0}.print-presentation-page{page:presentation2up;width:auto;height:10.5in;min-height:10.5in;margin:0;gap:.14in}.print-slide{height:5.18in}.student-set-grid{gap:7px 12px}.presentation-shell{display:block;height:auto;overflow:visible}.presentation-question{display:block;padding:0}.presentation-card{font-size:12pt;width:auto}}`;

  const STATION_CSS_FALLBACK = String.raw`@page{size:letter landscape;margin:0}:root{--navy:#00003d;--page-w:11in;--page-h:8.5in}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#111;background:#e8e8e8}.page{width:var(--page-w);height:var(--page-h);margin:0 auto .25in;background:#fff;padding:.32in .42in .24in;display:flex;flex-direction:column;overflow:hidden;page-break-after:always}.header{background:var(--navy);color:#fff;font-size:21pt;font-weight:800;padding:.11in .20in;margin-bottom:.12in}.station-grid{display:grid;grid-template-columns:1fr 1fr;gap:.10in .13in}.station-problem{border:1.2px solid #222;border-radius:5px;padding:.08in;font-size:10.2pt;break-inside:avoid}.figure img,.figure svg{display:block;max-width:100%;max-height:1.9in;height:auto;margin:0 auto}.page-footer{margin-top:auto;font-size:7.5pt}.station-index{width:11in;min-height:8.5in;margin:0 auto;background:#fff;padding:.45in}@media print{body{background:#fff}.page{margin:0}.station-index{display:none}}`;

  const COMMON_PRACTICE_FALLBACK = String.raw`# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS
VERSION: district-grading-common-practice/1.2
DATE: 2026-09-20

Use one approved class-level Set 1 question pool. Do not create Set 2. Common Worksheet must visibly label Review and Extension / Transfer. Print Presentation uses exactly two large top-aligned question panels per page. Student Set flows naturally and must not waste pages by forcing whole question/workspace blocks onto new pages. Classroom Structures should closely mirror the established Algebra u1_2 Activity Options architecture with one Set 1 only: Projection / Whiteboard Options plus Printable Handouts. Printable handouts are the existing Stations link, Find Someone Who, and the added Cut-Apart Question Cards. Do not include Tarsia or Blooket. Find Someone Who uses vertically stacked problem blocks with partner signature and work/reasoning space; it is not a cut-card grid. Cut-Apart Question Cards remain a separate reusable card deck for Quiz-Quiz-Trade, Fan-N-Pick, and similar card routines.`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, Visual, and Station QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.5

## Math rendering - HARD
- Use valid TeX and MathJax whenever mathematical notation is appropriate.
- Preferred delimiters are \\( ... \\) inline and \\[ ... \\] display.
- Generate PDFs only after MathJax has finished typesetting.
- Raw TeX, missing symbols, or clipped math is a failure.
- Prefer fraction-bar notation for symbolic division when that is the natural mathematical form.

## Graphs - HARD
- If text asks for, refers to, or depends on a graph, create the actual mathematically accurate graph.
- The request ZIP packages the current registered graph tool and District Graph Rendering Standard. For every supported Cartesian graph, including blank student construction grids, use that packaged tool directly.
- A graph that only resembles the district style but was drawn by hand-built SVG/CSS/canvas is a failure.
- Save graph assets under assets/graphs/ and embed the same asset anywhere the question is reused.
- Record renderer entrypoint + asset path for every Cartesian graph in data/qa.json.
- Never substitute prose, ASCII art, CSS sketches, browser-drawn axes, or another plotting style for a graph supported by the packaged registered graph tool.

## Images and diagrams - HARD
- If text refers to a diagram, figure, image, model, setup, or other visual, create and embed the actual visual.
- Save generated non-graph visuals under assets/visuals/.

## Evidence rating - HARD
Every student report uses exactly one of these labels: Convincing, Limited, Incorrect, Not Observed.
- Convincing: evidence clearly and sufficiently demonstrates the target.
- Limited: meaningful correct evidence is present, but incomplete, inconsistent, or insufficient.
- Incorrect: the student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.
- Not Observed: there is not enough usable evidence to judge the target, including blank, omitted, missing, or unreadable work. Not Observed is not Incorrect.

## Duplex student-document pairing - HARD
- Applies to combined student reports and combined individual-practice documents.
- Every student's segment must occupy an EVEN number of physical pages.
- If a student's final content page count is odd, append exactly one intentionally blank page before the next student.
- Verify actual PDF page order after creation and record before/after counts in data/qa.json.

## Required QA record
Create data/qa.json including evidence-rating checks, MathJax checks, graph/visual checks, duplex before/after page counts, links, PDF validation, question-review coverage, and failures. PASS is forbidden with unresolved failures.`;

  const RESPONSE_QA_FALLBACK = String.raw`# Grading Response QA Execution Guide

VERSION: district-grading-response-qa-execution/1.0

Run programmatic checks first, then targeted visual QA. Preserve full evidence review. Visually render every graph/diagram page and representative pages for each stable template. After a local correction, rerender only the changed artifact and direct dependents, not the entire already-stable package. Record QA coverage in data/qa.json.`;

  const GRAPH_STANDARD_FALLBACK = String.raw`# District Graph Rendering Standard

VERSION: district-graph-rendering-standard/1.0

Use the registered graph tool for every supported Cartesian graph, including blank construction grids. Do not replace it with hand-built SVG/CSS/canvas. Preserve approved print weights and record graph-tool provenance in data/qa.json.`;

  const evidenceInput = $("evidenceFiles");
  const rosterInput = $("rosterFiles");
  const rubricInput = $("rubricFiles");
  const gradeOutputInput = $("gradeOutput");
  const notesInput = $("teacherNotes");
  const buildButton = $("buildZip");
  const status = $("buildStatus");

  document.querySelectorAll(".chip[data-note]").forEach((button) => {
    button.addEventListener("click", () => {
      const note = button.dataset.note || "";
      const current = notesInput.value.trim();
      notesInput.value = current ? `${current}\n${note}` : note;
      notesInput.focus();
    });
  });

  evidenceInput.addEventListener("change", () => { renderFiles(evidenceInput.files, $("evidenceList")); refreshStatus(); });
  rosterInput.addEventListener("change", () => renderFiles(rosterInput.files, $("rosterList")));
  rubricInput.addEventListener("change", () => { renderFiles(rubricInput.files, $("rubricList")); refreshStatus(); });
  gradeOutputInput.addEventListener("change", refreshStatus);
  $("className").addEventListener("input", refreshStatus);
  $("clearForm").addEventListener("click", clearForm);
  buildButton.addEventListener("click", buildRequestZip);

  function renderFiles(files, target) {
    target.innerHTML = "";
    [...files].forEach((file) => {
      const li = document.createElement("li");
      li.textContent = `${file.name} (${formatBytes(file.size)})`;
      target.appendChild(li);
    });
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function refreshStatus() {
    const className = $("className").value.trim();
    const count = evidenceInput.files.length;
    const gradeMode = gradeOutputInput.value;
    if (!className || !count || !gradeMode) {
      const missing = [];
      if (!className) missing.push("a class/group name");
      if (!count) missing.push("at least one evidence file");
      if (!gradeMode) missing.push("a Step 4 grade/score handling choice");
      setStatus(`Add ${joinList(missing)}.`, "warn");
      return false;
    }
    if (gradeMode === "rubric" && !rubricInput.files.length) {
      setStatus("Grade/score handling is set to use the rubric, but no rubric/scoring guide is attached.", "bad");
      return false;
    }
    const rosterNote = rosterInput.files.length
      ? ` Roster included (${rosterInput.files.length} file${rosterInput.files.length === 1 ? "" : "s"}).`
      : " If this is one combined handwritten class scan, adding a roster is strongly recommended.";
    setStatus(`Ready to package ${count} evidence file${count === 1 ? "" : "s"}. The assignment title will be detected from the evidence.${rosterNote}`, "good");
    return true;
  }

  function joinList(items) {
    if (items.length <= 1) return items[0] || "the required information";
    if (items.length === 2) return `${items[0]} and ${items[1]}`;
    return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = `status ${kind}`;
  }

  function clearForm() {
    $("className").value = "";
    $("gradeSubject").value = "";
    $("teacherName").value = "";
    evidenceInput.value = "";
    rosterInput.value = "";
    rubricInput.value = "";
    gradeOutputInput.value = "";
    notesInput.value = "";
    $("evidenceList").innerHTML = "";
    $("rosterList").innerHTML = "";
    $("rubricList").innerHTML = "";
    refreshStatus();
  }

  async function buildRequestZip() {
    if (!refreshStatus()) return;
    buildButton.disabled = true;
    setStatus("Packaging request...", "warn");

    try {
      const className = $("className").value.trim();
      const gradeSubject = $("gradeSubject").value.trim();
      const teacherName = $("teacherName").value.trim();
      const teacherNotes = notesInput.value.trim();
      const gradeMode = gradeOutputInput.value;
      const createdAt = new Date().toISOString();

      const usedPaths = new Set();
      const evidenceManifest = [];
      const rosterManifest = [];
      const rubricManifest = [];
      const entries = [];

      for (const file of [...evidenceInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "evidence");
        const path = `evidence/${packagedName}`;
        evidenceManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }
      for (const file of [...rosterInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "roster");
        const path = `roster/${packagedName}`;
        rosterManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }
      for (const file of [...rubricInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "rubric");
        const path = `rubric/${packagedName}`;
        rubricManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      const scannedWorkFilename = `${friendlyFilePart(className)}_Scanned_Student_Work.pdf`;
      const request = {
        schema: REQUEST_SCHEMA,
        created_at: createdAt,
        response_style_version: RESPONSE_STYLE_VERSION,
        station_style_version: STATION_STYLE_VERSION,
        math_visual_qa_version: MATH_VISUAL_QA_VERSION,
        common_practice_version: COMMON_PRACTICE_VERSION,
        response_qa_execution_version: RESPONSE_QA_VERSION,
        graph_rendering_standard_version: GRAPH_RENDERING_STANDARD_VERSION,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: {
          name: null,
          detection_mode: "derive_from_uploaded_evidence",
          fallback: "Student Evidence Review",
          detection_priority: [
            "visible title on submitted student work",
            "rubric/scoring-guide title",
            "meaningful evidence filenames",
            "concise title inferred from the actual skill/content in the evidence",
            "Student Evidence Review only when no more informative title can be supported"
          ]
        },
        evidence_rating: {
          schema: "convincing-limited-incorrect-not-observed/1.0",
          required_on_each_student_report: true,
          labels: ["Convincing", "Limited", "Incorrect", "Not Observed"]
        },
        grading_defaults: {
          areas_of_strength_and_improvement: true,
          credit_reasoning_and_partial_understanding: true,
          formative_evidence_emphasis: true,
          allow_multiple_valid_methods: true,
          ignore_writing_mechanics_unless_requested: true,
          de_emphasize_minor_arithmetic_notation_unless_requested: true,
          missing_is_not_incorrect: true,
          concise_feedback: true,
          extend_convincing_students: true,
          flag_unclear_scans_instead_of_guessing: true
        },
        grade_output: {
          mode: gradeMode,
          required_teacher_selection: true,
          policy: gradePolicy(gradeMode, rubricManifest.length > 0)
        },
        teacher_exceptions_present: Boolean(teacherNotes),
        evidence_files: evidenceManifest,
        roster_files: rosterManifest,
        rubric_files: rubricManifest,
        requested_outputs: {
          student_reports: true,
          combined_student_reports_pdf: true,
          individual_practice: true,
          combined_individual_practice_pdf: true,
          class_analysis: true,
          recommended_groupings: true,
          scanned_student_work_pdf: `scanned_work/${scannedWorkFilename}`,
          common_course_practice: {
            common_review_extension: {
              enabled: true,
              printable_student_worksheet: true,
              teacher_guide_html: true,
              teacher_guide_includes_answers_and_moves: true,
              visible_student_sections: ["Review", "Extension / Transfer"]
            },
            stations: {
              review_stations: 4,
              extension_stations: 2,
              questions_per_station_min: 4,
              questions_per_station_max: 6,
              separate_answer_key: true,
              locked_style: STATION_STYLE_VERSION
            },
            question_solution_set: {
              set_name: "Set 1",
              count: 1,
              create_set_2: false,
              complete_set_reuse_required: true,
              reuse_class_level_question_pool: true,
              presentation: true,
              print_presentation_two_up: true,
              compact_review_all: true,
              student_set: true,
              teacher_guide: true,
              redundant_print_buttons_forbidden: true,
              classroom_structures: {
                projection: [
                  "Whiteboard Indy",
                  "Whiteboard Partners",
                  "RallyCoach",
                  "Speed Dating Math",
                  "Showdown",
                  "Think, Trade, Agree",
                  "Round Table",
                  "Mathematical Hot Seat",
                  "Rally Coach II"
                ],
                printable: [
                  "Find Someone Who",
                  "Cut-Apart Question Cards"
                ],
                card_artifact_supports: ["Quiz-Quiz-Trade", "Fan-N-Pick"],
                activity_options_reference: "algebra/activities/u1_2_act1/u1_2_act1.html",
                activity_options_one_set_only: true,
                printable_options: ["Stations", "Find Someone Who", "Cut-Apart Question Cards"],
                prohibited_optional_links: ["Tarsia", "Blooket"]
              }
            }
          },
          review_all_questions: {
            enabled: true,
            include_common_review: true,
            include_stations: true,
            include_question_solution_set: true,
            include_individual_practice: true,
            zero_workspace: true,
            show_answer: true,
            teacher_move: true,
            student_discourse_move: true
          },
          duplex_pairing: {
            combined_student_reports: true,
            combined_individual_practice: true,
            rule: "Each student's segment must occupy an even number of physical pages. After final rendering, add one intentionally blank page only when that student's page count is odd so the next student starts on a sheet front."
          }
        },
        click_me: {
          quick_actions: [
            "Print All Student Reports",
            "Print All Individual Practice",
            "View Scanned Student Work"
          ],
          sections: [
            "Individual Student Reports & Practice",
            "Class Data",
            "Common Course Practice"
          ],
          common_course_practice_cards: [
            "Common Worksheet / Review + Extension",
            "Stations",
            "Question / Solution Set"
          ]
        }
      };

      const [responseCss, stationCss, commonPracticeGuide, responseQaGuide, graphRenderingStandard, graphBundle] = await Promise.all([
        loadTextFile("response_styles.css", RESPONSE_CSS_FALLBACK),
        loadTextFile("station_styles.css", STATION_CSS_FALLBACK),
        loadTextFile("COMMON_PRACTICE_GUIDE.md", COMMON_PRACTICE_FALLBACK),
        loadTextFile("RESPONSE_QA_EXECUTION.md", RESPONSE_QA_FALLBACK),
        loadTextFile("../_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md", GRAPH_STANDARD_FALLBACK),
        loadGraphToolBundle()
      ]);
      request.graph_rendering = {
        standard_version: GRAPH_RENDERING_STANDARD_VERSION,
        source_manifest: "response_contract/graph_tool/MANIFEST.json",
        entrypoint: graphBundle.entrypoint,
        packaged_entrypoint: `response_contract/graph_tool/${graphBundle.entrypoint.split("/").pop()}`,
        packaged_files: Object.keys(graphBundle.files).map((path) => `response_contract/graph_tool/${path.split("/").pop()}`),
        provenance_required_in_qa: true
      };
      const requestInstructions = buildInstructions(request, teacherNotes);
      const graphEntries = Object.entries(graphBundle.files).map(([path, content]) => ({
        name: `response_contract/graph_tool/${path.split("/").pop()}`,
        data: enc.encode(content)
      }));

      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_exceptions_context.txt", data: enc.encode(teacherNotes || "No teacher exceptions or additional context were provided.") },
        { name: "response_contract/styles.css", data: enc.encode(responseCss) },
        { name: "response_contract/STYLE_VERSION.txt", data: enc.encode(RESPONSE_STYLE_VERSION + "\n") },
        { name: "response_contract/stations.css", data: enc.encode(stationCss) },
        { name: "response_contract/STATION_STYLE_VERSION.txt", data: enc.encode(STATION_STYLE_VERSION + "\n") },
        { name: "response_contract/MATH_VISUAL_QA.md", data: enc.encode(MATH_VISUAL_QA_CONTRACT) },
        { name: "response_contract/MATH_VISUAL_QA_VERSION.txt", data: enc.encode(MATH_VISUAL_QA_VERSION + "\n") },
        { name: "response_contract/COMMON_PRACTICE_GUIDE.md", data: enc.encode(commonPracticeGuide) },
        { name: "response_contract/COMMON_PRACTICE_VERSION.txt", data: enc.encode(COMMON_PRACTICE_VERSION + "\n") },
        { name: "response_contract/RESPONSE_QA_EXECUTION.md", data: enc.encode(responseQaGuide) },
        { name: "response_contract/RESPONSE_QA_VERSION.txt", data: enc.encode(RESPONSE_QA_VERSION + "\n") },
        { name: "response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md", data: enc.encode(graphRenderingStandard) },
        { name: "response_contract/GRAPH_RENDERING_STANDARD_VERSION.txt", data: enc.encode(GRAPH_RENDERING_STANDARD_VERSION + "\n") },
        { name: "response_contract/graph_tool/MANIFEST.json", data: enc.encode(graphBundle.manifestText) },
        ...graphEntries
      );

      const zipBlob = makeZip(entries);
      const filename = `grading_request_${slug(className)}_${dateStamp()}.zip`;
      downloadBlob(zipBlob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function buildInstructions(request, teacherNotes) {
    const rosterLine = request.roster_files.length
      ? "A roster is included under roster/. Use it only to resolve student identity, identify missing/unmatched evidence, and preserve roster order."
      : "No roster is included. Make one reasonable identity pass; if a handwritten name remains unreadable, assign a stable label such as Student 01, preserve the evidence/page mapping, flag the uncertainty, and continue rather than stalling the run.";
    const rubricLine = request.rubric_files.length
      ? "A rubric/scoring guide is included under rubric/. Use it where it clearly applies."
      : "No rubric/scoring guide is included.";
    const scannedPath = request.requested_outputs.scanned_student_work_pdf;
    const gradeMode = request.grade_output.mode;

    return `# District Grading & Evidence Request - Pilot\n\n` +
`## Task\n` +
`Analyze the student evidence in this ZIP and return exactly ONE response ZIP. This package is the complete build contract; no separate teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.\n\n` +
`Class / group: ${request.teacher.class_or_group}\n` +
`Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when reasonably clear from the evidence."}\n` +
`${rubricLine}\n${rosterLine}\n\n` +
`Teacher exceptions / context:\n${teacherNotes || "No exceptions or additional context provided."}\n\n` +
`## Detect the assignment / evidence title - REQUIRED\n` +
`The teacher intentionally did NOT type an assignment name. Determine a concise, useful title from the submitted evidence in this order: visible title on student work; rubric/scoring-guide title; meaningful filenames; concise title inferred from the actual skill/content; Student Evidence Review only as a last resort. Save the title and its basis in data/analysis.json and use it consistently.\n\n` +
`## Evidence rating - REQUIRED\n` +
`Every student report must use exactly one evidence rating: Convincing, Limited, Incorrect, or Not Observed. Convincing = clear/sufficient evidence. Limited = meaningful correct evidence but incomplete/inconsistent/insufficient. Incorrect = attempted evidence demonstrates a substantive incorrect idea/method/conclusion. Not Observed = insufficient usable evidence, including blank, omitted, missing, or unreadable work. Missing is not Incorrect.\n\n` +
`## Grade / score handling - REQUIRED AND AUTHORITATIVE\n` +
`Selected mode: ${gradeMode}\n${request.grade_output.policy}\n` +
`This teacher selection outranks free-form notes if they conflict. Record any conflict in data/qa.json and continue.\n\n` +
`## Default grading behavior - AUTOMATIC\n` +
`These are system defaults, not optional teacher requests: list Areas of Strength and Areas for Improvement; highlight and credit reasoning; treat all evidence as formative; allow multiple valid methods/solution paths; focus on mathematical/scientific reasoning rather than writing mechanics unless the teacher explicitly opts in; de-emphasize minor arithmetic/notation slips unless the teacher explicitly says to count them; credit partial understanding; do not equate missing with incorrect; keep feedback concise; give Convincing students extension/transfer; and flag unclear scans/uncertainty instead of guessing. Teacher exceptions/context may override only the specific item named.\n\n` +
`Exception semantics: "Ignore a question" means do not use that question as evidence. "Feedback only / don't grade" means review and comment on the question but do not let it affect the grade/score recommendation.\n\n` +
`## Evidence and identity rules\n` +
`Judge only from submitted evidence, rubric if present, roster for identity/order only, and teacher exceptions/context. Do not research students or use prior personal/student records. If a roster student has no identifiable work, use Not Observed/no evidence rather than Incorrect.\n\n` +
`## Locked styling and shared contracts\n` +
`Copy response_contract/styles.css exactly to assets/styles.css and response_contract/stations.css exactly to assets/stations.css. Follow response_contract/MATH_VISUAL_QA.md, response_contract/COMMON_PRACTICE_GUIDE.md, response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md, and response_contract/RESPONSE_QA_EXECUTION.md as executable HARD contracts. If older wording elsewhere in this request conflicts with COMMON_PRACTICE_GUIDE.md about Common Course Practice or Question / Solution Set layout, COMMON_PRACTICE_GUIDE.md controls.\n\n` +
`## Required response ZIP structure\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n  styles.css\n  stations.css\n  graphs/\n  visuals/\n` +
`scanned_work/\n  ${scannedPath.split('/').pop()}\n` +
`students/\n  <one report HTML per identified student>\n` +
`class/\n  class_overview.html\n  review_all_questions.html\n` +
`print/\n` +
`  all_student_reports.html\n  all_student_reports.pdf\n` +
`  common_review_extension/\n    student_worksheet.html\n    student_worksheet.pdf\n    teacher_guide.html\n` +
`  individualized/\n    <one HTML practice packet per student>\n` +
`  individual_practice_packets.pdf\n` +
`  stations/\n    index.html\n    stations.html\n    stations.pdf\n    answer_key.html\n    answer_key.pdf\n` +
`  question_set/\n    index.html\n    presentation.html\n    print_presentation.html\n    print_presentation.pdf\n    review_all.html\n    student_set.html\n    student_set.pdf\n    teacher_guide.html\n    structures/\n      index.html\n      directions.html\n      find_someone_who.html\n      cut_apart_cards.html\n` +
`data/\n  analysis.json\n  qa.json\n  request.json\n` +
`~~~\n\n` +
`All navigation, CSS, graph assets, and visual assets must use local relative links. PDFs must be finished printable files, not placeholders.\n\n` +
`## Scanned student work archive\n` +
`Create ${scannedPath}. Preserve submitted work exactly; combine readable scan/image pages into one teacher-friendly PDF when needed. Do not rewrite or clean up student answers.\n\n` +
`## CLICK_ME.html layout - LOCKED\n` +
`Keep the current simple dashboard hierarchy. 1) Hero/header with class, detected evidence title, grade/subject. 2) One quick-action row with exactly Print All Student Reports, Print All Individual Practice, View Scanned Student Work. 3) Individual Student Reports & Practice; each student card has Open Report and Individual Practice. 4) Class Data. 5) Common Course Practice with exactly three primary cards: Common Worksheet / Review + Extension, Stations, Question / Solution Set. Add a teacher-only Review All Questions link near the Common Course Practice heading. Do not create duplicate individual-practice or quick-action sections.\n\n` +
`## Individual reports and practice\n` +
`Each report includes student name/label; detected evidence title; Evidence Rating; optional grade/score only according to selected mode; specific strengths; highest-leverage improvement; evidence references when feasible; 1-3 next steps; and uncertainty when needed. Create one individual practice packet per student. For Convincing students favor extension/transfer. Create combined duplex-safe reports and practice PDFs in roster/identified order.\n\n` +
`## Duplex pairing - HARD\n` +
`For combined reports and combined individual practice, every student's segment must occupy an even number of physical pages. If final content count is odd, append exactly one intentionally blank page before the next student. Verify actual PDF page order and record before/after counts in data/qa.json.\n\n` +
`## Class analysis\n` +
`Include evidence sets analyzed, major strengths, top actionable errors/unfinished understandings, reliable pattern counts/percentages, suggested instructional groupings, Convincing students ready for extension, and evidence/identity limitations.\n\n` +
`## Common Worksheet / Review + Extension\n` +
`Create one compact class-wide student worksheet based on actual common needs, with targeted review and justified extension. On the student worksheet itself, visibly label the two sections **Review** and **Extension / Transfer** so students and teachers can tell which questions serve which purpose. The student-facing printable artifact is Student Worksheet. The HTML page that includes answers, teacher moves, and discourse moves is Teacher Guide. Do not call the teacher-facing HTML merely "HTML" and do not expose redundant Print buttons when browser print already produces the same intended layout.\n\n` +
`## Stations\n` +
`Create exactly four review stations plus two extension stations, 4-6 questions per station, with a complete separate answer key. Preserve the existing locked stations style. Do not redesign stations in this pass.\n\n` +
`## Question / Solution Set - SET 1 ONLY\n` +
`Set 1 is the mathematical question set; delivery formats reuse it. Create no Set 2. The set length is determined by the evidence and instructional purpose; no fixed number such as 8 or 14 is implied. Every Set 1 delivery artifact must include the entire Set 1 unless it intentionally paginates/cards the complete set across multiple sheets.\n` +
`Required Set 1 menu: Presentation; Print Presentation; Review All Questions; Student Set; Teacher Guide; Classroom Structures. Do not show separate Print Student Set or Print Teacher Guide buttons when browser print already produces the intended print layout.\n\n` +
`### Presentation\n` +
`Use one question at a time. Keep the top header compact and let the question/visual fill the useful browser area. Provide Back / Next and a visible question counter. Teacher-only answer/move toggles may be present. Do not emulate a full printed page on screen and do not force long blank scrolling.\n\n` +
`### Print Presentation - REQUIRED\n` +
`Create a dedicated print_presentation.html + PDF containing the exact Set 1 questions, exactly TWO large question panels per letter page, stacked and scaled to fit each half-page. TOP-ALIGN the question content within each half-page panel; do not vertically center it. Include all required graphs/figures. No answers, teacher moves, discourse moves, or large unused workspace. If Set 1 has an odd count, the final lower half may be blank. The screen view should visually show the real printed page boundaries.\n\n` +
`### Review All Questions\n` +
`Compact zero-workspace teacher QA view showing every Set 1 question with required visuals. Each item can reveal Answer, Teacher Move, and Student Discourse Move. Keep vertical waste low so the teacher can scan quality quickly.\n\n` +
`### Student Set\n` +
`Normal worksheet-style layout with a small header, all Set 1 questions, no projected classroom directions, sensible question spacing/workspace, and natural print pagination. Do not preassign question counts to pages or force an entire question + workspace block onto a new page when that wastes large blank areas. Keep prompt/required figure together when practical, but let workspace flow/split as needed. Do not use a giant activity title block.\n\n` +
`### Teacher Guide\n` +
`Match the Student Set questions and order. Include concise answers/solutions plus brief teacher and discourse moves where useful. A browser-print layout is sufficient unless a materially different dedicated print artifact is required.\n\n` +
`### Classroom Structures\n` +
`Make structures/index.html closely mirror the established Algebra u1_2_act1 Activity Options page, adapted to ONE Set 1 only. Use grouped **Projection / Whiteboard Options** and **Printable Handouts**. Projection structures (Whiteboard Indy, Whiteboard Partners, RallyCoach, Speed Dating Math, Showdown, Think-Trade-Agree, Round Table, Mathematical Hot Seat, Rally Coach II) link to the same Set 1 Presentation; do not generate duplicate question pages. Printable Handouts list: existing Stations, Find Someone Who, and the added Cut-Apart Question Cards. Do NOT include Tarsia or Blooket. Find Someone Who must look like the dedicated Algebra Find Someone Who handout: vertically stacked bordered problem blocks with Partner signature, Work / reasoning, and useful workspace; it is not a card grid. Cut-Apart Question Cards are a separate complete Set 1 deck and may be reused for Quiz-Quiz-Trade and Fan-N-Pick. Keep structure headers compact.\n\n` +
`## Review All Questions - teacher QA across all products\n` +
`Create class/review_all_questions.html and link it from CLICK_ME. Show ALL generated follow-up questions from Common Worksheet, Stations, Set 1, and Individual Practice by student. Use zero workspace, compact cards/rows, required visuals, tiny source/purpose labels, and collapsible Answer / Teacher Move / Student Discourse Move. Reused common questions may be labeled as reused instead of visually duplicated.\n\n` +
`## Math, graph, and visual rendering - HARD\n` +
`Follow response_contract/MATH_VISUAL_QA.md and response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md. The request packages the current registered graph tool under response_contract/graph_tool/. For every supported Cartesian graph, including blank student grids, execute that packaged entrypoint directly. Do not substitute hand-built SVG/CSS/canvas or another plotting style just because it looks similar. Record renderer entrypoint + graph asset path for every Cartesian graph in data/qa.json. Apply these rules to every common/individual artifact.\n\n` +
`## data/analysis.json\n` +
`Include detected evidence title plus basis; student identifiers; evidence mapping; evidence ratings; optional grade results; roster matching; strengths; needs; class patterns; groupings; common-practice targets; individual-practice targets; station targets; Set 1 question/source mapping; and uncertainty flags. Copy request.json into data/request.json.\n\n` +
`## QA execution order - REQUIRED\n` +
`Follow response_contract/RESPONSE_QA_EXECUTION.md. Preserve full evidence review, but do programmatic package checks before expensive visual rendering. Visually render every graph/diagram page plus representative/outlier pages for each stable template. After a local fix, rerender only the changed artifact and direct dependents; do not automatically rerender the entire already-stable package. Record visual-QA coverage in data/qa.json.\n\n` +
`## Final QA before delivery\n` +
`- Required locked CSS/contracts are used.\n` +
`- Detected title follows the required priority.\n` +
`- CLICK_ME retains the locked three-part hierarchy and quick actions.\n` +
`- Common Worksheet exposes Student Worksheet + Teacher Guide.\n` +
`- Stations remain four review + two extension with complete key.\n` +
`- Exactly one Question / Solution Set exists and every Set 1 artifact includes the full set.\n` +
`- Common Worksheet visibly labels Review and Extension / Transfer.\n` +
`- Print Presentation is present, exactly two questions per printed page, and top-aligned within each half-page.\n` +
`- Student Set uses natural flow without wasteful fixed page breaks.\n` +
`- Activity Options uses one Set 1, includes Cards, links to Stations/Find Someone Who, and omits Tarsia/Blooket.\n` +
`- Find Someone Who uses its dedicated signature/workspace worksheet layout, not cut cards.\n` +
`- Student Set and structure pages use compact headers.\n` +
`- No redundant Print buttons are shown when browser print is equivalent.\n` +
`- Review All pages are compact, zero-workspace, and complete.\n` +
`- MathJax, graphs, and visuals are rendered and checked.\n` +
`- Combined student PDFs are duplex-safe and verified.\n` +
`- All relative links resolve after unzip and data/qa.json reports PASS with no unresolved failures.\n\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.\n`;
  }

  function gradePolicy(mode, rubricPresent) {
    if (mode === "rubric") return "Return the evidence rating and the score/grade defined by the supplied rubric or scoring guide. Do not invent a different scale.";
    if (mode === "recommend") {
      return rubricPresent
        ? "Return the evidence rating and a teacher-review grade/score recommendation. Use the supplied rubric/scale when it applies; otherwise explain the evidence basis briefly."
        : "Return the evidence rating and a clear teacher-review grade/score recommendation from the submitted evidence. For objective item-based work, points/percent correct may be used. For open-ended work, use evidence-based professional judgment and label the result as a recommendation, not a final grade.";
    }
    return "Return the evidence rating only. Do not add a separate numeric, percentage, point, or letter grade.";
  }

  async function loadGraphToolBundle() {
    const manifestText = await loadCanonicalRepoText("Tools/MANIFEST.json");
    if (!manifestText) throw new Error("Could not load the canonical Tools/MANIFEST.json graph registry.");
    let manifest;
    try { manifest = JSON.parse(manifestText); } catch (error) { throw new Error("Canonical Tools/MANIFEST.json is not valid JSON."); }
    const entrypoint = manifest?.tools?.graph_tool;
    const base = manifest?.tools?.graph_tool_base;
    if (!entrypoint) throw new Error("Tools/MANIFEST.json does not declare tools.graph_tool.");

    const queue = [entrypoint];
    if (base) queue.push(base);
    const files = {};
    const seen = new Set();
    while (queue.length) {
      const path = queue.shift();
      if (!path || seen.has(path)) continue;
      seen.add(path);
      const content = await loadCanonicalRepoText(path);
      if (!content) throw new Error(`Could not load canonical graph dependency: ${path}`);
      files[path] = content;
      for (const match of content.matchAll(/~graph_tool_v\d+\.py/g)) {
        const dep = `Tools/${match[0]}`;
        if (!seen.has(dep)) queue.push(dep);
      }
    }
    return { manifestText, entrypoint, files };
  }

  async function loadCanonicalRepoText(repoPath) {
    const cleanPath = String(repoPath || "").replace(/^\/+/, "");
    if (!cleanPath) return "";

    // First try the GitHub Pages copy. This is fastest for ordinary files, but
    // Pages/Jekyll may omit source filenames such as ~graph_tool_v14.py.
    const pagesRelative = `../../${cleanPath}`;
    const pagesText = await loadTextFile(pagesRelative, "");
    if (pagesText) return pagesText;

    // Fall back to GitHub raw content so canonical files excluded by Pages are
    // still resolved from the repository named by Tools/MANIFEST.json.
    const encodedPath = cleanPath.split("/").map(encodeURIComponent).join("/");
    const rawUrl = `https://raw.githubusercontent.com/tnezki/memories/main/${encodedPath}`;
    try {
      const response = await fetch(rawUrl, { cache: "no-store" });
      if (response.ok) return await response.text();
    } catch (error) {
      console.warn(`Raw GitHub fetch failed for ${cleanPath}.`, error);
    }

    // Final browser-safe fallback: GitHub Contents API. Keep this read-only.
    const apiUrl = `https://api.github.com/repos/tnezki/memories/contents/${encodedPath}?ref=main`;
    try {
      const response = await fetch(apiUrl, {
        cache: "no-store",
        headers: { Accept: "application/vnd.github+json" }
      });
      if (response.ok) {
        const payload = await response.json();
        if (payload && payload.encoding === "base64" && payload.content) {
          const binary = atob(String(payload.content).replace(/\s/g, ""));
          const bytes = Uint8Array.from(binary, (ch) => ch.charCodeAt(0));
          return new TextDecoder().decode(bytes);
        }
      }
    } catch (error) {
      console.warn(`GitHub Contents API fetch failed for ${cleanPath}.`, error);
    }
    return "";
  }

  async function loadTextFile(filename, fallback) {
    try {
      const url = new URL(filename, window.location.href);
      const response = await fetch(url, { cache: "no-store" });
      if (response.ok) return await response.text();
    } catch (error) {
      console.warn(`Using embedded fallback for ${filename}.`, error);
    }
    return fallback;
  }

  function fileManifest(file, packagedPath) {
    return { original_name: file.name, packaged_path: packagedPath, mime_type: file.type || null, size_bytes: file.size };
  }

  function friendlyFilePart(value) {
    const cleaned = String(value || "Work").normalize("NFKD").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 54);
    return cleaned || "Work";
  }

  function slug(value) {
    return String(value || "request").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 48) || "request";
  }

  function safeFileName(name) {
    const cleaned = String(name || "file").replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_").replace(/^\.+/, "").trim();
    return cleaned || "file";
  }

  function uniqueName(name, usedPaths, folderKey) {
    let candidate = name;
    let n = 2;
    const keyFor = (value) => `${folderKey}/${value}`.toLowerCase();
    while (usedPaths.has(keyFor(candidate))) {
      const dot = name.lastIndexOf(".");
      candidate = dot > 0 ? `${name.slice(0, dot)}_${n}${name.slice(dot)}` : `${name}_${n}`;
      n += 1;
    }
    usedPaths.add(keyFor(candidate));
    return candidate;
  }

  function dateStamp() {
    const d = new Date();
    return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`;
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function makeZip(entries) {
    const localParts = [];
    const centralParts = [];
    let offset = 0;
    let count = 0;
    for (const entry of entries) {
      const nameBytes = enc.encode(entry.name.replace(/\\/g, "/"));
      const data = entry.data instanceof Uint8Array ? entry.data : new Uint8Array(entry.data);
      const crc = crc32(data);
      const { time, date } = dosTimeDate(new Date());
      const local = new Uint8Array(30 + nameBytes.length);
      const lv = new DataView(local.buffer);
      lv.setUint32(0, 0x04034b50, true);
      lv.setUint16(4, 20, true);
      lv.setUint16(6, 0x0800, true);
      lv.setUint16(8, 0, true);
      lv.setUint16(10, time, true);
      lv.setUint16(12, date, true);
      lv.setUint32(14, crc, true);
      lv.setUint32(18, data.length, true);
      lv.setUint32(22, data.length, true);
      lv.setUint16(26, nameBytes.length, true);
      lv.setUint16(28, 0, true);
      local.set(nameBytes, 30);
      localParts.push(local, data);

      const central = new Uint8Array(46 + nameBytes.length);
      const cv = new DataView(central.buffer);
      cv.setUint32(0, 0x02014b50, true);
      cv.setUint16(4, 20, true);
      cv.setUint16(6, 20, true);
      cv.setUint16(8, 0x0800, true);
      cv.setUint16(10, 0, true);
      cv.setUint16(12, time, true);
      cv.setUint16(14, date, true);
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, nameBytes.length, true);
      cv.setUint16(30, 0, true);
      cv.setUint16(32, 0, true);
      cv.setUint16(34, 0, true);
      cv.setUint16(36, 0, true);
      cv.setUint32(38, 0, true);
      cv.setUint32(42, offset, true);
      central.set(nameBytes, 46);
      centralParts.push(central);
      offset += local.length + data.length;
      count += 1;
    }
    const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
    const end = new Uint8Array(22);
    const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(4, 0, true);
    ev.setUint16(6, 0, true);
    ev.setUint16(8, count, true);
    ev.setUint16(10, count, true);
    ev.setUint32(12, centralSize, true);
    ev.setUint32(16, offset, true);
    ev.setUint16(20, 0, true);
    return new Blob([...localParts, ...centralParts, end], { type: "application/zip" });
  }

  function dosTimeDate(d) {
    const year = Math.max(1980, d.getFullYear());
    const time = (d.getHours() << 11) | (d.getMinutes() << 5) | Math.floor(d.getSeconds() / 2);
    const date = ((year - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
    return { time, date };
  }

  const crcTable = (() => {
    const table = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      table[n] = c >>> 0;
    }
    return table;
  })();

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const b of bytes) crc = crcTable[(crc ^ b) & 0xff] ^ (crc >>> 8);
    return (crc ^ 0xffffffff) >>> 0;
  }

  refreshStatus();
})();
