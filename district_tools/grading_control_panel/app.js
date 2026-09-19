(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.3";
  const STATION_STYLE_VERSION = "district-grading-station-style/1.0";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.4";
  const COMMON_PRACTICE_VERSION = "district-grading-common-practice/1.0";
  const REQUEST_SCHEMA = "district-grading-request/0.8-pilot";

  const RESPONSE_CSS_FALLBACK = String.raw`:root{--ink:#172033;--muted:#5d687b;--line:#d5dde8;--soft:#f4f7fa;--panel:#fff;--hero:#eef3f8;--accent:#365f82;--accent-dark:#284b68;--success:#176b46;--warn:#8a5a00;--shadow:0 8px 24px rgba(20,34,50,.06)}*{box-sizing:border-box}html{background:#fff;color:var(--ink)}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:var(--ink);font-size:16px;line-height:1.5}a{color:var(--accent-dark)}.wrap{max-width:1180px;margin:0 auto;padding:20px}.hero{background:var(--hero);border:1px solid var(--line);border-radius:24px;padding:32px 36px;margin:10px 0 24px}.hero h1{margin:0;font-size:42px}.quick-actions,.inline-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:11px 18px;border-radius:12px;border:1px solid #9fb4c8;background:#fff;color:var(--accent);font-weight:800;text-decoration:none}.btn.primary{background:var(--accent);color:#fff}.section{margin:22px 0;background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px}.grid,.student-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}.card{border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff}.card-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}.question-review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:10px}.question-review-card{border:1px solid var(--line);border-radius:12px;padding:12px}.question-source{font-size:11px;text-transform:uppercase;font-weight:800;color:var(--muted)}.question-review-card details{margin-top:7px;border-top:1px solid #e3e7ed;padding-top:6px}.question-review-card summary{cursor:pointer;font-weight:800}.teacher-move,.discourse-move,.answer-box{font-size:12px;background:var(--soft);border-radius:8px;padding:8px;margin-top:6px}.presentation-shell{min-height:100vh;display:grid;grid-template-rows:auto 1fr auto}.presentation-head{padding:14px 20px;border-bottom:1px solid var(--line)}.presentation-question{display:flex;align-items:center;justify-content:center;padding:26px;min-height:calc(100vh - 150px)}.presentation-card{width:min(1050px,96vw);font-size:clamp(22px,2.5vw,38px)}.presentation-nav{position:sticky;bottom:0;background:#fff;border-top:1px solid var(--line);padding:12px 18px;display:flex;justify-content:space-between;gap:10px}.report-page,.practice-page,.packet-page{max-width:8in;margin:0 auto}.feedback-box,.practice-block{border:1px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}.duplex-blank-page{display:none}.math-display{margin:12px 0}.visual-block img,.graph-frame img{display:block;max-width:100%;height:auto;margin:0 auto}@media print{@page{size:letter;margin:.55in}.quick-actions,.no-print,.screen-only,.presentation-nav{display:none!important}.duplex-blank-page{display:block;height:9.9in;min-height:9.9in;break-after:page;page-break-after:always}.card,.practice-block,.feedback-box,.question-review-card{break-inside:avoid}}`;

  const STATION_CSS_FALLBACK = String.raw`@page{size:letter landscape;margin:0}:root{--navy:#00003d;--page-w:11in;--page-h:8.5in}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#111;background:#e8e8e8}.page{width:var(--page-w);height:var(--page-h);margin:0 auto .25in;background:#fff;padding:.32in .42in .24in;display:flex;flex-direction:column;overflow:hidden;page-break-after:always}.header{background:var(--navy);color:#fff;font-size:21pt;font-weight:800;padding:.11in .20in;margin-bottom:.12in}.station-grid{display:grid;grid-template-columns:1fr 1fr;gap:.10in .13in}.station-problem{border:1.2px solid #222;border-radius:5px;padding:.08in;font-size:10.2pt;break-inside:avoid}.figure img,.figure svg{display:block;max-width:100%;max-height:1.9in;height:auto;margin:0 auto}.page-footer{margin-top:auto;font-size:7.5pt}.station-index{width:11in;min-height:8.5in;margin:0 auto;background:#fff;padding:.45in}@media print{body{background:#fff}.page{margin:0}.station-index{display:none}}`;

  const COMMON_PRACTICE_FALLBACK = String.raw`# Common Course Practice & Question Review Guide

Use one approved class-level question pool across the Common Worksheet / Review + Extension, Stations when appropriate, Question / Solution Set, presentation mode, Review All Questions, and cooperative layouts. Create one Question / Solution Set only. Required question-set views: presentation, compact review-all, printable student set, and solutions. Review All Questions must show all common and individual follow-up questions with zero student workspace and collapsible Answer, Teacher Move, and Student Discourse Move. Cooperative templates reuse the same questions: Standard, Find Someone Who, Quiz-Quiz-Trade, RallyCoach / PairCoach, Showdown, and Fan-N-Pick. Write original concise directions; do not copy proprietary published wording.`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, Visual, and Station QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.4

## Math rendering - HARD
- Use valid TeX and MathJax whenever mathematical notation is appropriate.
- Preferred delimiters are \\( ... \\) inline and \\[ ... \\] display.
- Generate PDFs only after MathJax has finished typesetting.
- Raw TeX, missing symbols, or clipped math is a failure.

## Graphs - HARD
- If text asks for, refers to, or depends on a graph, create the actual mathematically accurate graph.
- When the district registered graph tool is packaged/available, use it for supported Cartesian graphs, including blank student construction grids.
- Save graph assets under assets/graphs/ and embed them where used.
- Never substitute prose, ASCII art, CSS sketches, or a browser-drawn coordinate grid for a required supported graph.

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
    if (!className || !count) {
      setStatus("Add a class/group name and at least one evidence file.", "warn");
      return false;
    }
    if (gradeOutputInput.value === "rubric" && !rubricInput.files.length) {
      setStatus("Optional grade/score is set to rubric scoring, but no rubric/scoring guide is attached.", "bad");
      return false;
    }
    const rosterNote = rosterInput.files.length
      ? ` Roster included (${rosterInput.files.length} file${rosterInput.files.length === 1 ? "" : "s"}).`
      : " If this is one combined handwritten class scan, adding a roster is strongly recommended.";
    setStatus(`Ready to package ${count} evidence file${count === 1 ? "" : "s"}. The assignment title will be detected from the evidence.${rosterNote}`, "good");
    return true;
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
    gradeOutputInput.value = "none";
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
        grade_output: {
          mode: gradeMode,
          policy: gradePolicy(gradeMode, rubricManifest.length > 0)
        },
        teacher_notes_present: Boolean(teacherNotes),
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
            common_review_extension: true,
            stations: {
              review_stations: 4,
              extension_stations: 2,
              questions_per_station_min: 4,
              questions_per_station_max: 6,
              separate_answer_key: true,
              locked_style: STATION_STYLE_VERSION
            },
            question_solution_set: {
              count: 1,
              reuse_class_level_question_pool: true,
              presentation_mode: true,
              compact_review_all_mode: true,
              printable_student_set: true,
              matching_solutions: true,
              classroom_structures: [
                "Standard",
                "Find Someone Who",
                "Quiz-Quiz-Trade",
                "RallyCoach / PairCoach",
                "Showdown",
                "Fan-N-Pick"
              ]
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
          ]
        }
      };

      const [responseCss, stationCss, commonPracticeGuide] = await Promise.all([
        loadTextFile("response_styles.css", RESPONSE_CSS_FALLBACK),
        loadTextFile("station_styles.css", STATION_CSS_FALLBACK),
        loadTextFile("COMMON_PRACTICE_GUIDE.md", COMMON_PRACTICE_FALLBACK)
      ]);
      const requestInstructions = buildInstructions(request, teacherNotes);

      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No teacher notes were provided.") },
        { name: "response_contract/styles.css", data: enc.encode(responseCss) },
        { name: "response_contract/STYLE_VERSION.txt", data: enc.encode(RESPONSE_STYLE_VERSION + "\n") },
        { name: "response_contract/stations.css", data: enc.encode(stationCss) },
        { name: "response_contract/STATION_STYLE_VERSION.txt", data: enc.encode(STATION_STYLE_VERSION + "\n") },
        { name: "response_contract/MATH_VISUAL_QA.md", data: enc.encode(MATH_VISUAL_QA_CONTRACT) },
        { name: "response_contract/MATH_VISUAL_QA_VERSION.txt", data: enc.encode(MATH_VISUAL_QA_VERSION + "\n") },
        { name: "response_contract/COMMON_PRACTICE_GUIDE.md", data: enc.encode(commonPracticeGuide) },
        { name: "response_contract/COMMON_PRACTICE_VERSION.txt", data: enc.encode(COMMON_PRACTICE_VERSION + "\n") }
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
`Analyze the student evidence in this ZIP and return exactly ONE response ZIP. This packaged request is the complete build contract; no additional teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.\n\n` +
`Class / group: ${request.teacher.class_or_group}\n` +
`Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when reasonably clear from the evidence."}\n` +
`${rubricLine}\n${rosterLine}\n\n` +
`Teacher notes:\n${teacherNotes || "No additional notes provided."}\n\n` +
`## Detect the assignment / evidence title - REQUIRED\n` +
`The teacher intentionally did NOT type an assignment name. Determine a concise, useful title from the submitted evidence. Use this priority order:\n` +
`1. A visible title printed on the scanned/uploaded assignment or evidence.\n` +
`2. The title of the supplied rubric/scoring guide when it clearly names the evidence task.\n` +
`3. Meaningful evidence filenames.\n` +
`4. A concise title you create from the actual skill/content demonstrated by the evidence (examples: "Solving Right Triangles", "Newton's Laws CER", "Fraction Multiplication Models").\n` +
`5. Use **Student Evidence Review** only as a last resort when the evidence does not support a more informative title.\n` +
`Do not guess an unrelated unit or standard. Save the chosen title and its basis in data/analysis.json and use it consistently in reports, practice, PDFs, and CLICK_ME.\n\n` +
`## Evidence rating - REQUIRED\n` +
`Every student report must include exactly one evidence rating: Convincing, Limited, Incorrect, or Not Observed.\n` +
`- Convincing: the submitted evidence clearly and sufficiently demonstrates the target.\n` +
`- Limited: meaningful correct evidence is present, but incomplete, inconsistent, or insufficient.\n` +
`- Incorrect: the student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.\n` +
`- Not Observed: there is not enough usable evidence to judge the target. Blank, omitted, missing, or unreadable work belongs here rather than being automatically called Incorrect.\n` +
`The rating legend may appear in teacher outputs where useful; it does not need to appear on every student page.\n\n` +
`## Optional grade / score - AUTHORITATIVE\n` +
`Selected mode: ${gradeMode}\n${request.grade_output.policy}\n` +
`The selected mode outranks free-form teacher notes if they conflict. Record any conflict in data/qa.json and continue.\n\n` +
`## Feedback policy\n` +
`- Give specific positive feedback grounded in what the student actually demonstrated.\n` +
`- Clearly identify what is incorrect, incomplete, or needs revision and what the student should fix.\n` +
`- Keep feedback concise and prioritize the highest-leverage next steps.\n` +
`- For Convincing evidence, favor extension, transfer, or application over unnecessary repetition.\n` +
`- Flag uncertainty instead of guessing handwriting, identity, or missing evidence.\n\n` +
`## Evidence and identity rules\n` +
`- Judge work only from submitted evidence, rubric if present, roster for identity/order only, and teacher notes.\n` +
`- Do not research students or use prior personal/student records.\n` +
`- If a roster student has no identifiable work, use Not Observed/no evidence rather than Incorrect.\n\n` +
`## Locked styling and shared contracts\n` +
`Copy response_contract/styles.css exactly to assets/styles.css. Copy response_contract/stations.css exactly to assets/stations.css. Follow response_contract/MATH_VISUAL_QA.md and response_contract/COMMON_PRACTICE_GUIDE.md as executable contracts.\n\n` +
`## Required response ZIP structure\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n  styles.css\n  stations.css\n  graphs/\n  visuals/\n` +
`scanned_work/\n  ${scannedPath.split('/').pop()}\n` +
`students/\n  <one report HTML per identified student>\n` +
`class/\n  class_overview.html\n  review_all_questions.html\n` +
`print/\n` +
`  all_student_reports.html\n  all_student_reports.pdf\n` +
`  common_review_extension_packet.html\n  common_review_extension_packet.pdf\n` +
`  individualized/\n    <one HTML practice packet per student>\n` +
`  individual_practice_packets.pdf\n` +
`  stations/\n    index.html\n    stations.html\n    stations.pdf\n    answer_key.html\n    answer_key.pdf\n` +
`  question_set/\n    index.html\n    presentation.html\n    review_all.html\n    student_set.html\n    student_set.pdf\n    solutions.html\n    solutions.pdf\n    structures/\n      index.html\n      find_someone_who.html\n      quiz_quiz_trade.html\n      rallycoach.html\n      showdown.html\n      fan_n_pick.html\n` +
`data/\n  analysis.json\n  qa.json\n  request.json\n` +
`~~~\n\n` +
`All navigation, CSS, graph assets, and visual assets must use local relative links. PDFs must be finished printable files, not placeholders.\n\n` +
`## Scanned student work archive\n` +
`Create ${scannedPath}. Preserve submitted student work exactly; combine readable scan/image pages into one teacher-friendly PDF when needed. Do not rewrite or clean up student answers.\n\n` +
`## CLICK_ME.html layout - HARD\n` +
`1. Hero/header with class, detected evidence title, and grade/subject.\n` +
`2. ONE top quick-action row with exactly: **Print All Student Reports**, **Print All Individual Practice**, **View Scanned Student Work**.\n` +
`3. **Individual Student Reports & Practice**. Each student card has exactly two direct links: **Open Report** and **Individual Practice**. Do not create a duplicate Individual Student Practice section lower on the dashboard.\n` +
`4. **Class Data**.\n` +
`5. **Common Course Practice** with three primary cards: **Common Worksheet / Review + Extension**, **Stations**, **Question / Solution Set**.\n` +
`6. In the Common Course Practice heading/intro, add a visible teacher-only **Review All Questions** link to class/review_all_questions.html.\n` +
`Do not use the heading "Print Options" and do not repeat the three top quick actions lower on the page.\n\n` +
`## Individual student reports and practice\n` +
`Each report includes student name/label; detected evidence title; Evidence Rating; optional grade/score only according to selected mode; specific positive feedback; the most important incorrect/incomplete/revision need; evidence references when feasible; 1-3 clear next steps; and uncertainty when needed.\n` +
`Create one individual practice packet per identified student. Target highest-leverage next steps; for Convincing students use extension/transfer rather than remediation.\n` +
`Create print/all_student_reports.html + PDF and print/individual_practice_packets.pdf in roster/identified order.\n\n` +
`## Duplex pairing for student documents - HARD\n` +
`For both combined reports and combined individual practice, each student's segment must occupy an even number of physical pages. If final content count is odd, append exactly one intentionally blank page before the next student. Verify the actual PDF sequence after creation and record before/after page counts in data/qa.json.\n\n` +
`## Class analysis\n` +
`Include evidence sets analyzed, major strengths, top actionable errors/unfinished understandings, reliable pattern counts/percentages, suggested instructional groupings, Convincing students ready for extension, and evidence/identity limitations.\n\n` +
`## Common Course Practice\n` +
`Build one coherent class-level question pool from actual common needs plus justified extension targets. Reuse these approved questions across the following delivery formats rather than generating separate unrelated banks.\n\n` +
`### Common Worksheet / Review + Extension\n` +
`Create one compact class-wide worksheet based on actual common needs, with concise support, targeted practice, and extension when justified. Provide HTML and PDF. It may also serve as the source layout for Find Someone Who.\n\n` +
`### Stations\n` +
`Create six stations under print/stations/: four review stations and two extension stations. Each has 4-6 questions. If fewer than four distinct misconceptions exist, use consolidation/prerequisite/transfer tied to observed needs rather than inventing a misconception. Use assets/stations.css exactly and create a complete separate answer key.\n\n` +
`### Question / Solution Set - ONE SET ONLY\n` +
`Create exactly one class-level question/solution set. Reuse strong questions from the class-level pool/stations/common worksheet whenever appropriate; do not make a third independent bank merely to fill the set.\n` +
`Required views:\n` +
`- print/question_set/presentation.html: one-question-at-a-time teacher presentation that fills the usable browser viewport, with Back, Next, question counter, Show Answer, Teacher Move, and Student Discourse Move. Avoid full print-page blank vertical space and long scrolling between questions.\n` +
`- print/question_set/review_all.html: compact zero-workspace scan of the one set.\n` +
`- student_set.html/PDF and solutions.html/PDF.\n` +
`- structures/index.html exposes Standard, Find Someone Who, Quiz-Quiz-Trade, RallyCoach / PairCoach, Showdown, and Fan-N-Pick. These layouts reuse the SAME approved questions; they do not trigger new question generation. Follow COMMON_PRACTICE_GUIDE.md for original concise directions and templates.\n\n` +
`## Review All Questions - REQUIRED TEACHER QA VIEW\n` +
`Create class/review_all_questions.html and link it from CLICK_ME. This is a compact no-workspace review of ALL generated follow-up questions, grouped by Common Worksheet, Stations, Question/Solution Set, and Individual Practice by student.\n` +
`Each question card must include:\n` +
`- compact prompt plus required graph/figure/model;\n` +
`- tiny teacher-only source/purpose label;\n` +
`- collapsible **Show Answer**;\n` +
`- collapsible **Teacher Move**;\n` +
`- collapsible **Student Discourse Move**.\n` +
`Keep moves short and useful. The page exists so a teacher can quickly judge question quality before printing. Reused questions may be labeled as reused rather than repeated unnecessarily in common sections.\n\n` +
`## Math, graph, and visual rendering - HARD\n` +
`Follow response_contract/MATH_VISUAL_QA.md. Math must be rendered with MathJax and visually checked. Any required graph must be mathematically accurate and actually embedded. Any referenced image/diagram/figure must exist. Apply the same requirement to stations, common practice, question sets, Review All Questions, and individual practice.\n\n` +
`## data/analysis.json\n` +
`Include detected evidence title plus title basis; student identifiers; evidence mapping; evidence ratings; optional grade results; roster matching; strengths; needs; class patterns; groupings; common-practice targets; individual-practice targets; station targets; question-set pool/source mapping; and uncertainty flags. Copy request.json into data/request.json.\n\n` +
`## Final QA before delivery\n` +
`- assets/styles.css and assets/stations.css match the packaged contracts.\n` +
`- A concise evidence title was detected using the required priority; Student Evidence Review is used only when necessary.\n` +
`- CLICK_ME top row has exactly the three required quick actions.\n` +
`- Individual Student Reports & Practice has both links on each student card and there is no duplicate individual-practice section.\n` +
`- Common Course Practice contains the three required primary choices plus Review All Questions.\n` +
`- Review All Questions contains every generated follow-up question, zero workspace, and Answer/Teacher Move/Student Discourse Move controls.\n` +
`- Exactly one Question / Solution Set exists; its presentation view advances question-by-question without page-sized blank screen gaps.\n` +
`- Cooperative structure layouts reuse the approved question pool rather than inventing new questions.\n` +
`- Exactly four review stations and two extension stations exist; answer key covers every station item.\n` +
`- MathJax, graphs, and visuals are rendered and checked.\n` +
`- Combined student reports and individual-practice PDFs are duplex-safe and verified.\n` +
`- Scanned-work PDF, report PDF, individual-practice PDF, common worksheet PDF, station PDF/key, and question-set PDF/solutions all exist and open.\n` +
`- All relative links resolve after unzip.\n` +
`- data/qa.json reports PASS with no unresolved failures.\n\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.\n`;
  }

  function gradePolicy(mode, rubricPresent) {
    if (mode === "rubric") return "Return the evidence rating and the score/grade defined by the supplied rubric or scoring guide. Do not invent a different scale.";
    if (mode === "recommend") {
      return rubricPresent
        ? "Return the evidence rating and a teacher-review grade recommendation. Use the supplied rubric/scale when it applies; otherwise explain the evidence basis briefly."
        : "Return the evidence rating and a clear teacher-review grade recommendation from the submitted evidence. For objective item-based work, points/percent correct may be used. For open-ended work, use evidence-based professional judgment and label the result as a recommendation, not a final grade.";
    }
    return "Return the evidence rating only. Do not add a separate numeric, percentage, point, or letter grade.";
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
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function makeZip(entries) {
    const localParts = [], centralParts = [];
    let offset = 0, count = 0;
    for (const entry of entries) {
      const nameBytes = enc.encode(entry.name.replace(/\\/g, "/"));
      const data = entry.data instanceof Uint8Array ? entry.data : new Uint8Array(entry.data);
      const crc = crc32(data); const { time, date } = dosTimeDate(new Date());
      const local = new Uint8Array(30 + nameBytes.length); const lv = new DataView(local.buffer);
      lv.setUint32(0, 0x04034b50, true); lv.setUint16(4, 20, true); lv.setUint16(6, 0x0800, true); lv.setUint16(8, 0, true); lv.setUint16(10, time, true); lv.setUint16(12, date, true); lv.setUint32(14, crc, true); lv.setUint32(18, data.length, true); lv.setUint32(22, data.length, true); lv.setUint16(26, nameBytes.length, true); lv.setUint16(28, 0, true); local.set(nameBytes, 30); localParts.push(local, data);
      const central = new Uint8Array(46 + nameBytes.length); const cv = new DataView(central.buffer);
      cv.setUint32(0, 0x02014b50, true); cv.setUint16(4, 20, true); cv.setUint16(6, 20, true); cv.setUint16(8, 0x0800, true); cv.setUint16(10, 0, true); cv.setUint16(12, time, true); cv.setUint16(14, date, true); cv.setUint32(16, crc, true); cv.setUint32(20, data.length, true); cv.setUint32(24, data.length, true); cv.setUint16(28, nameBytes.length, true); cv.setUint16(30, 0, true); cv.setUint16(32, 0, true); cv.setUint16(34, 0, true); cv.setUint16(36, 0, true); cv.setUint32(38, 0, true); cv.setUint32(42, offset, true); central.set(nameBytes, 46); centralParts.push(central);
      offset += local.length + data.length; count += 1;
    }
    const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
    const end = new Uint8Array(22); const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true); ev.setUint16(4, 0, true); ev.setUint16(6, 0, true); ev.setUint16(8, count, true); ev.setUint16(10, count, true); ev.setUint32(12, centralSize, true); ev.setUint32(16, offset, true); ev.setUint16(20, 0, true);
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
