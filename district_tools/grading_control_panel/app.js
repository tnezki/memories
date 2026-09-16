(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.1";
  const STATION_STYLE_VERSION = "district-grading-station-style/1.0";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.2";
  const REQUEST_SCHEMA = "district-grading-request/0.6-pilot";

  const RESPONSE_CSS_FALLBACK = String.raw`:root{--ink:#172033;--muted:#5d687b;--line:#d5dde8;--soft:#f4f7fa;--panel:#fff;--hero:#eef3f8;--accent:#365f82;--accent-dark:#284b68;--success:#176b46;--warn:#8a5a00;--shadow:0 8px 24px rgba(20,34,50,.06)}*{box-sizing:border-box}html{background:#fff;color:var(--ink)}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:var(--ink);font-size:16px;line-height:1.5}a{color:var(--accent-dark)}.wrap{max-width:1180px;margin:0 auto;padding:20px}.hero{background:var(--hero);border:1px solid var(--line);border-radius:24px;padding:32px 36px;margin:10px 0 24px}.eyebrow{margin:0 0 2px;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:var(--muted);font-size:15px}.hero h1{margin:0;font-size:42px;line-height:1.08;letter-spacing:-.02em}.subtitle{margin:10px 0 0;font-size:20px}.quick-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:12px 20px;border-radius:12px;border:1px solid #9fb4c8;background:#fff;color:var(--accent);font-weight:800;text-decoration:none;font-size:17px}.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}.section{margin:22px 0;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:var(--shadow)}.section h2{margin:0 0 6px;font-size:25px}.section-intro{margin:0 0 18px;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff}.card h3{margin:0 0 5px;font-size:18px}.card p{margin:5px 0;color:var(--muted)}.card a{font-weight:800;text-decoration:none}.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:14px 0}.stat{border:1px solid var(--line);background:var(--soft);border-radius:14px;padding:14px}.stat strong{display:block;font-size:28px}.stat span{color:var(--muted);font-size:13px}.notice{border-left:4px solid var(--accent);background:var(--soft);border-radius:10px;padding:12px 14px;margin:14px 0}.notice.warn{border-left-color:var(--warn)}.notice.good{border-left-color:var(--success)}.report-page,.practice-page,.packet-page{max-width:8in;margin:0 auto;padding:.1in 0;color:#111}.report-head{border-bottom:2px solid #cfd7e2;padding-bottom:12px;margin-bottom:18px}.report-head .eyebrow{font-size:12px}.report-head h1{font-size:30px;margin:0}.report-meta{color:#555;margin-top:4px}.report-section{margin:18px 0}.report-section h2{font-size:19px;margin:0 0 7px}.report-section p,.report-section li{font-size:15px}ul.clean{margin:7px 0 0;padding-left:21px}ul.clean li{margin:5px 0}.feedback-box{border:1px solid #d8dee7;border-radius:12px;padding:13px 15px;margin:12px 0;background:#fafbfc}.practice-block{border:1px solid #cfd7e2;border-radius:12px;padding:14px;margin:14px 0;break-inside:avoid}.name-line{display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #bfc8d3;padding-bottom:8px;margin-bottom:14px;font-weight:700}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}th,td{border:1px solid #d6dde6;padding:8px 9px;text-align:left;vertical-align:top}th{background:#f3f6f9}.small{font-size:13px;color:var(--muted)}.page-break{break-before:page;page-break-before:always}.no-print{display:block}.math-inline{white-space:nowrap}.math-display{margin:12px 0;overflow-x:auto;overflow-y:hidden;padding:4px 0}.visual-block{margin:16px 0;break-inside:avoid;page-break-inside:avoid}.visual-block img,.graph-frame img,.graph-image,.instructional-visual{display:block;max-width:100%;height:auto;margin:0 auto}.graph-frame{margin:16px auto;padding:10px;border:1px solid #d6dde6;border-radius:12px;background:#fff;break-inside:avoid;page-break-inside:avoid}.figure-caption{margin:6px auto 0;max-width:92%;font-size:12px;line-height:1.35;color:#5d687b;text-align:center}mjx-container[jax="SVG"]{max-width:100%;overflow-x:auto;overflow-y:hidden}@media(max-width:700px){.wrap{padding:12px}.hero{padding:24px 20px;border-radius:18px}.hero h1{font-size:32px}.subtitle{font-size:17px}.btn{width:100%}.section{padding:17px}}@media print{@page{size:letter;margin:.55in}body{font-size:11pt;background:#fff}.wrap{max-width:none;padding:0}.hero,.section{box-shadow:none}.no-print,.quick-actions,.screen-only{display:none!important}.report-page,.practice-page,.packet-page{max-width:none;padding:0}a{color:#000;text-decoration:none}.page-break{break-before:page;page-break-before:always}.practice-block,.feedback-box,.card,.stat,.math-display,.visual-block,.graph-frame,mjx-container{break-inside:avoid;page-break-inside:avoid}}`;

  const STATION_CSS_FALLBACK = String.raw`@page{size:letter landscape;margin:0}:root{--navy:#00003d;--navy-mid:#004d99;--page-w:11in;--page-h:8.5in;--content-media-max-height:1.9in}*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#111;background:#e8e8e8;line-height:1.18;-webkit-print-color-adjust:exact;print-color-adjust:exact}.page{width:var(--page-w);height:var(--page-h);margin:0 auto .25in;background:#fff;padding:.32in .42in .24in;box-shadow:0 2px 12px rgba(0,0,0,.18);display:flex;flex-direction:column;overflow:hidden;page-break-after:always;break-after:page;position:relative}.header{background:var(--navy);color:#fff;font-size:21pt;font-weight:800;padding:.11in .20in;margin-bottom:.12in;border-radius:4px;line-height:1.05}.header.small{font-size:18pt}.copy-note{position:absolute;right:.42in;top:.39in;font-size:9.5pt;font-weight:800;color:#555;text-transform:uppercase;letter-spacing:.05em}.station-grid{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:.10in .13in;flex:0 0 auto;align-content:start}.station-problem{border:1.2px solid #222;border-radius:5px;padding:.08in;font-size:10.2pt;line-height:1.23;break-inside:avoid;overflow:visible;background:#fff;min-height:0}.station-problem h3{font-size:11.5pt;color:var(--navy);margin-bottom:.04in}.station-problem p{margin:0 0 .045in 0}.label{font-size:8.4pt;letter-spacing:.05em;text-transform:uppercase;color:#555;font-weight:800;margin-bottom:.035in}.figure{text-align:center;margin:.04in auto;width:100%}.figure img,.figure svg{display:block;max-width:100%;max-height:var(--content-media-max-height)!important;height:auto;object-fit:contain;margin:0 auto;border:0}.values{border-collapse:collapse;margin:.07in auto;font-size:9.3pt;width:auto}.values th,.values td{border:1px solid #555;padding:.035in .065in;text-align:center;vertical-align:middle}.values th{font-weight:800;background:#fff;color:#111}.solution-list{font-size:11.2pt;line-height:1.30;flex:1;overflow:hidden}.solution-item{border-bottom:1px solid #bbb;padding:.07in 0;break-inside:avoid}.solution-item h3{font-size:12.2pt;color:var(--navy);margin-bottom:.025in}.solution-item .question{font-size:10.5pt;color:#333;margin-bottom:.035in}.page-footer{padding-top:.08in;display:flex;justify-content:space-between;font-size:7.5pt;color:#111;margin-top:auto}.station-index{width:11in;min-height:8.5in;margin:0 auto;background:#fff;padding:.45in;font-family:Arial,Helvetica,sans-serif}.station-index h1{font-size:24pt;color:var(--navy);margin:0 0 .08in}.station-index p{margin:.06in 0;font-size:12pt}.station-index .buttons{display:flex;gap:.12in;flex-wrap:wrap;margin:.20in 0}.station-index a{display:inline-block;padding:.11in .18in;border:2px solid var(--navy);border-radius:6px;text-decoration:none;color:var(--navy);font-weight:800;background:#fff}.station-index a.primary{background:var(--navy);color:#fff}.station-list{display:grid;grid-template-columns:1fr 1fr;gap:.12in .18in;margin-top:.18in}.station-card{border:1px solid #888;border-radius:6px;padding:.12in}.station-card h2{font-size:14pt;color:var(--navy);margin:0 0 .04in}.station-card p{font-size:10.5pt;margin:0}mjx-container[jax="SVG"]{max-width:100%;overflow-x:auto;overflow-y:hidden}@media print{body{background:#fff}.page{margin:0;box-shadow:none}.page:last-child{page-break-after:auto;break-after:auto}.station-index{display:none}}`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, Visual, and Station QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.2

This contract is executable. It applies to all response HTML/PDF, including station pages and answer keys.

## Math rendering - HARD
- Use valid TeX and MathJax whenever mathematical notation is appropriate.
- Preferred delimiters are \\( ... \\) inline and \\[ ... \\] display.
- Generate PDFs only after MathJax has finished typesetting.
- Inspect rendered HTML and PDF. Raw TeX, missing symbols, or clipped math is a failure.

## Graphs - HARD
- If text asks for, refers to, or depends on a graph, create the actual mathematically accurate graph.
- Prefer a dedicated graphing/grapher capability when available. Otherwise use another approved accurate graph-generation capability.
- Save real SVG/PNG assets under assets/graphs/ and embed them where used.
- Never substitute prose, ASCII art, CSS sketches, or "the graph shows..." for a missing graph.

## Images and diagrams - HARD
- If text refers to a diagram, figure, image, model, setup, or other visual, create and embed the actual visual.
- Save generated non-graph visuals under assets/visuals/.
- Never refer to a visual that does not exist in that output.

## Evidence rating - HARD
Every student report uses the fixed evidence labels Convincing, Limited, Incorrect, or Not Observed.
- Convincing: the submitted evidence clearly and sufficiently demonstrates the target.
- Limited: there is meaningful correct evidence, but it is incomplete, inconsistent, or not yet sufficient.
- Incorrect: the student attempted the target and the submitted evidence demonstrates a substantive incorrect idea, method, or conclusion.
- Not Observed: there is not enough usable evidence to judge the target, including blank, omitted, missing, or unreadable work. Not Observed must never be treated as Incorrect.

## Required QA record
Create data/qa.json with at least:
- overall_status;
- evidence_rating.scheme and followed;
- grade_output.selected_mode, followed, and teacher_note_conflicts;
- mathjax.pages_with_math, rendered_and_checked, raw_tex_visible_count;
- graphs.required_count, created_count, dedicated_grapher_available, dedicated_grapher_used_when_available, assets with generation_method;
- visuals.required_count, created_count, assets;
- stations.review_count, extension_count, question_count_by_station, page_count_by_station, answer_key_complete, locked_css_matches;
- links.all_relative_links_resolve;
- pdfs.rendered_and_visually_checked;
- failures array.

PASS is not allowed with raw TeX, missing/incorrect required graphs, missing referenced visuals, broken links, incomplete station answers, incorrect evidence-label usage, or clipped/unrendered PDF content.
`;

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

  evidenceInput.addEventListener("change", () => renderFiles(evidenceInput.files, $("evidenceList")));
  rosterInput.addEventListener("change", () => renderFiles(rosterInput.files, $("rosterList")));
  rubricInput.addEventListener("change", () => {
    renderFiles(rubricInput.files, $("rubricList"));
    refreshStatus();
  });
  gradeOutputInput.addEventListener("change", refreshStatus);
  buildButton.addEventListener("click", buildRequestZip);
  $("clearForm").addEventListener("click", clearForm);

  [$("className"), $("assignmentName"), evidenceInput].forEach((el) => {
    el.addEventListener("input", refreshStatus);
    el.addEventListener("change", refreshStatus);
  });

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
    const assignmentName = $("assignmentName").value.trim();
    const count = evidenceInput.files.length;
    if (!className || !assignmentName || !count) {
      setStatus("Add the required fields and at least one evidence file.", "warn");
      return false;
    }
    if (gradeOutputInput.value === "rubric" && !rubricInput.files.length) {
      setStatus("Optional grade/score is set to rubric scoring, but no rubric/scoring guide is attached.", "bad");
      return false;
    }
    const rosterNote = rosterInput.files.length
      ? ` Roster included (${rosterInput.files.length} file${rosterInput.files.length === 1 ? "" : "s"}).`
      : " If this is one combined handwritten class scan, adding a roster is strongly recommended.";
    setStatus(`Ready to package ${count} evidence file${count === 1 ? "" : "s"}.${rosterNote}`, "good");
    return true;
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = `status ${kind}`;
  }

  function clearForm() {
    $("className").value = "";
    $("assignmentName").value = "";
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
      const assignmentName = $("assignmentName").value.trim();
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

      const scannedWorkFilename = `${friendlyFilePart(className)}_${friendlyFilePart(assignmentName)}_Scanned_Student_Work.pdf`;
      const request = {
        schema: REQUEST_SCHEMA,
        created_at: createdAt,
        response_style_version: RESPONSE_STYLE_VERSION,
        station_style_version: STATION_STYLE_VERSION,
        math_visual_qa_version: MATH_VISUAL_QA_VERSION,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: { name: assignmentName },
        evidence_rating: {
          scheme: "convincing-limited-incorrect-not-observed/1.0",
          required_on_each_student_report: true,
          labels: ["Convincing", "Limited", "Incorrect", "Not Observed"],
          definitions: {
            Convincing: "Evidence clearly and sufficiently demonstrates the target.",
            Limited: "Meaningful correct evidence is present, but it is incomplete, inconsistent, or insufficient.",
            Incorrect: "The student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.",
            "Not Observed": "There is not enough usable evidence to judge the target; blank, omitted, missing, or unreadable evidence is not automatically incorrect."
          }
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
          class_analysis: true,
          recommended_groupings: true,
          scanned_student_work_pdf: `scanned_work/${scannedWorkFilename}`,
          common_print_packet: "One class-wide review/extension packet based on the most important common patterns",
          individualized_print_packets: "Student-specific review/extension practice based on each student's evidence",
          stations: {
            review_stations: 4,
            extension_stations: 2,
            questions_per_station_min: 4,
            questions_per_station_max: 6,
            pages_per_station_preferred: 1,
            pages_per_station_max: 2,
            separate_answer_key: true,
            locked_style: STATION_STYLE_VERSION
          }
        },
        click_me_quick_actions: [
          "Print All Student Reports (PDF)",
          "Print All Individualized Practice (PDF)",
          "View Scanned Student Work (PDF)"
        ],
        click_me_no_duplicate_quick_actions: true,
        rendering_contract: {
          mathjax_required_when_math_present: true,
          create_all_required_graph_assets: true,
          create_all_referenced_visuals: true,
          qa_record_required: "data/qa.json"
        }
      };

      const [responseCss, stationCss] = await Promise.all([
        loadTextFile("response_styles.css", RESPONSE_CSS_FALLBACK),
        loadTextFile("station_styles.css", STATION_CSS_FALLBACK)
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
        { name: "response_contract/MATH_VISUAL_QA_VERSION.txt", data: enc.encode(MATH_VISUAL_QA_VERSION + "\n") }
      );

      const zipBlob = makeZip(entries);
      const filename = `grading_request_${slug(className)}_${slug(assignmentName)}_${dateStamp()}.zip`;
      downloadBlob(zipBlob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function gradePolicy(mode, rubricPresent) {
    if (mode === "rubric") {
      return "Return the evidence rating and the score/grade defined by the supplied rubric or scoring guide. Do not invent a different scale.";
    }
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
    return {
      original_name: file.name,
      packaged_path: packagedPath,
      mime_type: file.type || null,
      size_bytes: file.size
    };
  }

  function friendlyFilePart(value) {
    const cleaned = String(value || "Work")
      .normalize("NFKD")
      .replace(/[^A-Za-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 54);
    return cleaned || "Work";
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
`Assignment / evidence set: ${request.assignment.name}\n` +
`Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when reasonably clear from the evidence."}\n` +
`${rubricLine}\n${rosterLine}\n\n` +
`Teacher notes:\n${teacherNotes || "No additional notes provided."}\n\n` +
`## Evidence rating - REQUIRED\n` +
`Every student report must include an evidence rating using exactly one of these labels: Convincing, Limited, Incorrect, Not Observed.\n` +
`- Convincing: the submitted evidence clearly and sufficiently demonstrates the target.\n` +
`- Limited: meaningful correct evidence is present, but it is incomplete, inconsistent, or not yet sufficient.\n` +
`- Incorrect: the student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.\n` +
`- Not Observed: there is not enough usable evidence to judge the target. Blank, omitted, missing, or unreadable work belongs here rather than being automatically called Incorrect.\n` +
`Use the same labels at the criterion/target level when the evidence naturally separates that way.\n\n` +
`## Optional grade / score - AUTHORITATIVE\n` +
`Selected mode: ${gradeMode}\n` +
`${request.grade_output.policy}\n` +
`The selected mode outranks free-form teacher notes if they conflict. Notes may add grading details but may not silently change the selected mode. Record any conflict in data/qa.json and continue the run.\n\n` +
`## Feedback policy\n` +
`- Give specific positive feedback grounded in what the student actually demonstrated.\n` +
`- Clearly identify what is incorrect, incomplete, or needs revision and state what the student should fix.\n` +
`- Keep feedback concise and prioritize the highest-leverage next steps.\n` +
`- For Convincing evidence, favor extension, transfer, or application over unnecessary repetition.\n` +
`- Do not rank students against one another.\n` +
`- Flag uncertainty instead of guessing handwriting, identity, or missing evidence.\n\n` +
`## Evidence and identity rules\n` +
`- Judge work only from the submitted evidence, rubric if present, roster for identity/order only, and teacher notes.\n` +
`- Do not research students or use prior personal/student records.\n` +
`- If a roster student has no identifiable work, use Not Observed/no evidence rather than Incorrect.\n` +
`- If evidence names a student not on the roster, keep it and flag the mismatch.\n\n` +
`## Locked styling\n` +
`Copy response_contract/styles.css exactly to assets/styles.css and use it for the dashboard, reports, class analysis, common packet, and individualized practice.\n` +
`Copy response_contract/stations.css exactly to assets/stations.css and use it for ALL station and station-answer-key pages. Do not redesign the station pages. The station stylesheet intentionally matches the current Algebra station format: letter landscape, dark navy header, Classroom Copy/Answer Key label, 2x2 problem grid, Arial, compact tables, and landscape answer pages.\n\n` +
`## Math, graph, and visual rendering - HARD\n` +
`Follow response_contract/MATH_VISUAL_QA.md as an executable contract. Math must be rendered with MathJax and visually checked. Any required graph must actually be generated as a mathematically accurate SVG/PNG and embedded. Any referenced image/diagram/figure must actually exist and be embedded. Never describe a missing graph or visual in prose.\n\n` +
`## Required response ZIP structure\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n` +
`  styles.css\n` +
`  stations.css\n` +
`  graphs/\n` +
`  visuals/\n` +
`scanned_work/\n` +
`  ${scannedPath.split('/').pop()}\n` +
`students/\n` +
`  <one print-friendly HTML report per identified student>\n` +
`class/\n` +
`  class_overview.html\n` +
`print/\n` +
`  all_student_reports.html\n` +
`  all_student_reports.pdf\n` +
`  common_review_extension_packet.html\n` +
`  common_review_extension_packet.pdf\n` +
`  individualized/\n` +
`    <one HTML packet per student>\n` +
`  individualized_packets.pdf\n` +
`  stations/\n` +
`    index.html\n` +
`    stations.html\n` +
`    stations.pdf\n` +
`    answer_key.html\n` +
`    answer_key.pdf\n` +
`data/\n` +
`  analysis.json\n` +
`  qa.json\n` +
`  request.json\n` +
`~~~\n\n` +
`All package navigation, CSS, graph assets, and visual assets must use local relative links. PDFs must be finished printable files, not placeholders.\n\n` +
`## Scanned student work archive\n` +
`Create ${scannedPath}. Preserve submitted student work exactly; combine readable scan/image pages into one teacher-friendly PDF when needed. Do not rewrite or clean up student answers.\n\n` +
`## CLICK_ME.html layout - fixed\n` +
`1. Hero/header with class, assignment, and grade/subject.\n` +
`2. ONE top quick-action row with exactly: Print All Student Reports (PDF), Print All Individualized Practice (PDF), View Scanned Student Work (PDF).\n` +
`3. Individual Student Reports.\n` +
`4. Class Data.\n` +
`5. Print Options with three distinct choices that are NOT duplicates of the top buttons:\n` +
`   - Common Class Review + Extension.\n` +
`   - Stations -> print/stations/index.html.\n` +
`   - Individual Student Practice -> individual student packet links.\n` +
`Do not repeat the three top quick actions lower on the page.\n\n` +
`## Individual student reports\n` +
`Each report must include: student name/label; assignment; Evidence Rating; optional grade/score only according to the selected mode; specific positive feedback; the most important incorrect/incomplete/revision need; evidence references when feasible; 1-3 clear next steps; and uncertainty when needed. Do not include classmates' names/performance.\n` +
`Create print/all_student_reports.html and PDF with every full report in roster/identified order and page breaks between students.\n\n` +
`## Class analysis\n` +
`Include evidence sets analyzed, major strengths, top actionable errors/unfinished understandings, reliable pattern counts/percentages, suggested instructional groupings, Convincing students ready for extension, and evidence/identity limitations.\n\n` +
`## Common Class Review + Extension\n` +
`Create one general class packet based on actual common needs, with concise support, targeted practice, and extension when justified. Provide HTML and PDF.\n\n` +
`## Individualized Practice\n` +
`Create one student-specific packet per identified student. Target the highest-leverage next steps; for Convincing students use extension/transfer rather than remediation. Create the combined individualized PDF with page breaks.\n\n` +
`## Stations - REQUIRED PRINT OPTION\n` +
`Create six stations from the class evidence and place them under print/stations/.\n` +
`- Stations 1-4 are REVIEW stations targeting the four most instructionally useful things the class needs to fix. Each station should address one clear need and contain 4-6 questions. Prefer one landscape page per station; use at most two pages when 5-6 questions or required visuals genuinely need the space. Do not shrink content into unreadable layouts.\n` +
`- If the evidence supports fewer than four genuinely distinct misconceptions, do NOT invent a fake misconception. Use the remaining review station(s) for closely related prerequisite practice, mixed consolidation, or transfer tied to the observed needs, and label that purpose accurately.\n` +
`- Stations 5-6 are EXTENSION stations for students showing Convincing evidence. Use transfer, application, synthesis, or challenge; do not make them merely harder copies of remediation questions. Each has 4-6 questions and the same one-page-preferred/two-page-maximum rule.\n` +
`- Use assets/stations.css exactly. Follow the current station visual pattern: dark navy header, Station N plus Review/Extension title, Classroom Copy label, 2x2 question blocks on a landscape page, compact tables/visuals, and a small footer. If a station needs more than four questions, continue that same station on a second landscape page rather than squeezing six tiny boxes onto one page.\n` +
`- Create a separate answer key using the same landscape visual system with Answer Key labels and complete answers/explanations for every station question. Keep student station pages answer-free.\n` +
`- print/stations/index.html is a simple teacher landing page with two prominent actions: Print Stations (PDF) and Print Answer Key (PDF), followed by a concise list of the six station purposes.\n` +
`- Create stations.html/stations.pdf and answer_key.html/answer_key.pdf.\n` +
`- Apply the MathJax/graph/visual contract to stations too. If a station says use a graph, include the real graph.\n\n` +
`## data/analysis.json\n` +
`Include student identifiers, evidence mapping, evidence ratings, optional grade results, roster matching, strengths, needs, class patterns, groupings, common-packet targets, individualized targets, six station targets, and uncertainty flags. Copy request.json into data/request.json.\n\n` +
`## Final QA before delivery\n` +
`- assets/styles.css exactly matches response_contract/styles.css.\n` +
`- assets/stations.css exactly matches response_contract/stations.css.\n` +
`- Every student report uses Convincing/Limited/Incorrect/Not Observed correctly; blanks/missing/unreadable evidence are not mislabeled Incorrect.\n` +
`- Optional grade/score follows selected mode ${gradeMode}; conflicting free-form notes do not change it.\n` +
`- CLICK_ME has one top quick-action row and no duplicate quick actions lower down.\n` +
`- Stations appears under Print Options and links to print/stations/index.html.\n` +
`- Exactly four review stations and two extension stations exist; each has 4-6 questions and no station exceeds two landscape pages.\n` +
`- Station answer key covers every question.\n` +
`- MathJax, graphs, and visuals are rendered and checked in HTML/PDF.\n` +
`- Scanned-work PDF, combined reports PDF, individualized PDF, station PDF, and station answer-key PDF all exist and open.\n` +
`- data/qa.json reports PASS with no unresolved failures.\n` +
`- All relative links resolve after unzip.\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.\n`;
  }

  function slug(value) {
    return String(value || "request")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 48) || "request";
  }

  function safeFileName(name) {
    const cleaned = String(name || "file")
      .replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_")
      .replace(/^\.+/, "")
      .trim();
    return cleaned || "file";
  }

  function uniqueName(name, usedPaths, folderKey) {
    let candidate = name;
    let n = 2;
    const keyFor = (value) => `${folderKey}/${value}`.toLowerCase();
    while (usedPaths.has(keyFor(candidate))) {
      const dot = name.lastIndexOf(".");
      candidate = dot > 0
        ? `${name.slice(0, dot)}_${n}${name.slice(dot)}`
        : `${name}_${n}`;
      n += 1;
    }
    usedPaths.add(keyFor(candidate));
    return candidate;
  }

  function dateStamp() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}${m}${day}`;
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
