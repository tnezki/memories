(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.1";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.1";
  const RESPONSE_CSS_FALLBACK = String.raw`:root{
  --ink:#172033;
  --muted:#5d687b;
  --line:#d5dde8;
  --soft:#f4f7fa;
  --panel:#ffffff;
  --hero:#eef3f8;
  --accent:#365f82;
  --accent-dark:#284b68;
  --success:#176b46;
  --warn:#8a5a00;
  --shadow:0 8px 24px rgba(20,34,50,.06);
}
*{box-sizing:border-box}
html{background:#fff;color:var(--ink)}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:var(--ink);font-size:16px;line-height:1.5}
a{color:var(--accent-dark)}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
.hero{background:var(--hero);border:1px solid var(--line);border-radius:24px;padding:32px 36px;margin:10px 0 24px}
.eyebrow{margin:0 0 2px;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:var(--muted);font-size:15px}
.hero h1{margin:0;font-size:42px;line-height:1.08;letter-spacing:-.02em}
.subtitle{margin:10px 0 0;font-size:20px;color:var(--ink)}
.quick-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:12px 20px;border-radius:12px;border:1px solid #9fb4c8;background:#fff;color:var(--accent);font-weight:800;text-decoration:none;font-size:17px}
.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn:hover{filter:brightness(.98)}
.section{margin:22px 0;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:var(--shadow)}
.section h2{margin:0 0 6px;font-size:25px;line-height:1.2}
.section-intro{margin:0 0 18px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff}
.card h3{margin:0 0 5px;font-size:18px}.card p{margin:5px 0;color:var(--muted)}
.card a{font-weight:800;text-decoration:none}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:14px 0}
.stat{border:1px solid var(--line);background:var(--soft);border-radius:14px;padding:14px}.stat strong{display:block;font-size:28px;line-height:1.05}.stat span{color:var(--muted);font-size:13px}
.notice{border-left:4px solid var(--accent);background:var(--soft);border-radius:10px;padding:12px 14px;margin:14px 0}
.notice.warn{border-left-color:var(--warn)}
.notice.good{border-left-color:var(--success)}
.report-page,.practice-page,.packet-page{max-width:8in;margin:0 auto;padding:.1in 0;color:#111}
.report-head{border-bottom:2px solid #cfd7e2;padding-bottom:12px;margin-bottom:18px}
.report-head .eyebrow{font-size:12px}.report-head h1{font-size:30px;margin:0}.report-meta{color:#555;margin-top:4px}
.report-section{margin:18px 0}.report-section h2{font-size:19px;margin:0 0 7px}.report-section p,.report-section li{font-size:15px}
ul.clean{margin:7px 0 0;padding-left:21px}ul.clean li{margin:5px 0}
.feedback-box{border:1px solid #d8dee7;border-radius:12px;padding:13px 15px;margin:12px 0;background:#fafbfc}
.practice-block{border:1px solid #cfd7e2;border-radius:12px;padding:14px;margin:14px 0;break-inside:avoid}.practice-block h2,.practice-block h3{margin-top:0}
.name-line{display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #bfc8d3;padding-bottom:8px;margin-bottom:14px;font-weight:700}
.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}th,td{border:1px solid #d6dde6;padding:8px 9px;text-align:left;vertical-align:top}th{background:#f3f6f9}
.small{font-size:13px;color:var(--muted)}
.page-break{break-before:page;page-break-before:always}
.no-print{display:block}
@media(max-width:700px){.wrap{padding:12px}.hero{padding:24px 20px;border-radius:18px}.hero h1{font-size:32px}.subtitle{font-size:17px}.btn{width:100%}.section{padding:17px}}
@media print{
  @page{size:letter;margin:.55in}
  body{font-size:11pt;background:#fff}
  .wrap{max-width:none;padding:0}
  .hero,.section{box-shadow:none}
  .no-print,.quick-actions,.screen-only{display:none!important}
  .report-page,.practice-page,.packet-page{max-width:none;padding:0}
  a{color:#000;text-decoration:none}
  .page-break{break-before:page;page-break-before:always}
  .practice-block,.feedback-box,.card,.stat{break-inside:avoid}
}

/* Math, graph, and created-visual support (style contract 1.1) */
.math-inline{white-space:nowrap}
.math-display{margin:12px 0;overflow-x:auto;overflow-y:hidden;padding:4px 0}
.visual-block{margin:16px 0;break-inside:avoid;page-break-inside:avoid}
.visual-block img,.graph-frame img,.graph-image,.instructional-visual{display:block;max-width:100%;height:auto;margin:0 auto}
.graph-frame{margin:16px auto;padding:10px;border:1px solid #d6dde6;border-radius:12px;background:#fff;break-inside:avoid;page-break-inside:avoid}
.figure-caption{margin:6px auto 0;max-width:92%;font-size:12px;line-height:1.35;color:#5d687b;text-align:center}
mjx-container[jax="SVG"]{max-width:100%;overflow-x:auto;overflow-y:hidden}
@media print{
  .math-display,.visual-block,.graph-frame,mjx-container{break-inside:avoid;page-break-inside:avoid}
  .figure-caption{color:#333}
}
`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, and Visual QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.1

This contract is executable. It applies to every student report, class page, common packet, individualized packet, combined HTML/PDF, and any other generated instructional content in the response ZIP.

## 1. Math rendering - HARD
- When mathematical notation is used, author it as valid TeX and render it with MathJax. Do not leave raw TeX, dollar-delimited source, Unicode approximations, or plain-text substitutes where formatted mathematics is appropriate.
- Preferred delimiters are \\( ... \\) for inline mathematics and \\[ ... \\] for display mathematics.
- Every HTML page containing mathematical notation must load or contain working MathJax output. MathJax 3 TeX-to-SVG is preferred because it creates stable printable output.
- If MathJax is loaded at runtime, the MathJax script is the sole allowed external runtime dependency. Package navigation, CSS, graph images, diagrams, and other assets must remain relative/local.
- Generate PDFs only after MathJax has finished typesetting. The PDF is not allowed to contain raw TeX delimiters or unrendered expressions.
- Inspect the rendered HTML and PDF, not just the source code. If raw delimiters, missing symbols, clipped equations, or failed typesetting are visible, repair and re-check before delivery.
- If MathJax cannot be rendered and verified, do not silently substitute plain text. Treat that as MATHJAX_RENDER_QA_FAILED and repair before final delivery.

Recommended runtime configuration when a local serialized MathJax result is not available:
  window.MathJax = {
    tex: {
      inlineMath: [['\\\\(', '\\\\)']],
      displayMath: [['\\\\[', '\\\\]']]
    },
    svg: { fontCache: 'global' }
  };
  MathJax runtime: https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js

## 2. Graphs - HARD
- If the response says, implies, or asks the student to use a graph, create the actual graph. Never write a placeholder such as "the graph shows...", "see graph", "graph here", or describe a graph that is not present.
- Generate the graph with the best available approved graph-generation capability. If a dedicated graphing/grapher tool is exposed, prefer and use it. If not, use another mathematically accurate plotting capability that can create a verifiable SVG or PNG. The required outcome is a correct graph asset, not a dependency on one tool name.
- Save the resulting graph as a real SVG or PNG asset under assets/graphs/ and embed it in every HTML/PDF location that refers to it.
- Preserve the mathematical content: correct equation/data, useful window, labeled axes when instructionally appropriate, legible tick marks, and visible key features needed by the task.
- Do not invent coordinates that were not supplied or legitimately derived for the task. For student evidence, preserve the submitted data/equation and clearly distinguish any teacher-created follow-up graph from student work.
- If no available capability can create a graph required only by newly generated follow-up content, revise that generated task so it no longer depends on the missing graph while preserving the instructional target. Never ship prose that refers to a missing graph. If a graph is essential and cannot be created, record GRAPH_ASSET_CREATION_FAILED and do not claim PASS.

## 3. Images and diagrams - HARD
- If instructions, feedback, or practice refer to an image, diagram, figure, model, geometry drawing, lab setup, visual pattern, or other visual, create and embed the actual visual.
- Never write "the image shows...", "see image", "diagram below", or similar language unless the referenced visual file exists and is visible in that exact output.
- Use an appropriate visual creation method: image generation for illustrative/photo-like content, or a clean SVG/diagram for schematic instructional visuals. The visual must be saved under assets/visuals/ and embedded in the related HTML/PDF.
- Do not use a text box or alt text as a substitute for a missing visual.
- Do not alter the scanned student-work archive when creating teacher-generated follow-up visuals.

## 4. Visual asset rules
- Every generated graph or visual must have a descriptive filename, a local relative path, meaningful alt text in HTML, and a short caption only when the caption helps instruction.
- Generated visuals must remain legible in print. Avoid tiny labels, cropped axes, low-resolution raster images, and page-break placement that separates a prompt from the visual it requires.
- Keep graphs and diagrams with the question/explanation they support whenever possible.

## 5. Required QA record
Create data/qa.json. It must record at minimum:
- overall_status: PASS only when all required checks below pass;
- mathjax.pages_with_math;
- mathjax.rendered_and_checked;
- mathjax.raw_tex_visible_count;
- grade_output.selected_mode;
- grade_output.followed;
- grade_output.teacher_note_conflicts as an array;
- graphs.required_count;
- graphs.created_count;
- graphs.dedicated_grapher_available;
- graphs.dedicated_grapher_used_when_available;
- graphs.assets with page, asset path, and generation_method;
- visuals.required_count;
- visuals.created_count;
- visuals.assets with page and asset path;
- links.all_relative_links_resolve;
- pdfs.rendered_and_visually_checked;
- failures as an array (empty for PASS).

Final delivery cannot report PASS when raw TeX is visible, a required graph asset is missing or mathematically incorrect, a referenced visual is missing, an image/graph link is broken, or a PDF contains an unrendered/clipped required visual.
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
      setStatus("Grade output is set to rubric scoring, but no rubric/scoring guide is attached.", "bad");
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
    gradeOutputInput.value = "mastery";
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
      const gradeOutput = resolveGradeOutput(gradeOutputInput.value, rubricInput.files.length > 0);
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
        schema: "district-grading-request/0.5-pilot",
        math_visual_qa_version: MATH_VISUAL_QA_VERSION,
        response_style_version: RESPONSE_STYLE_VERSION,
        created_at: createdAt,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: { name: assignmentName },
        grade_output: gradeOutput,
        scoring_policy: gradeOutput.policy,
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
          individualized_print_packets: "Student-specific review/extension practice based on each student's evidence"
        },
        click_me_quick_actions: [
          "Print All Student Reports (PDF)",
          "Print All Individualized Practice (PDF)",
          "View Scanned Student Work (PDF)"
        ],
        click_me_no_duplicate_quick_actions: true,
        rendering_contract: {
          mathjax_required_when_math_present: true,
          actual_graph_asset_required_when_graph_needed: true,
          preferred_graph_generation: "Use a dedicated grapher when available; otherwise use the best accurate graph-generation capability available.",
          create_all_referenced_visuals: true,
          qa_record_required: "data/qa.json"
        }
      };

      const responseCss = await loadResponseCss();
      const requestInstructions = buildInstructions(request, teacherNotes);
      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No teacher notes were provided.") },
        { name: "response_contract/styles.css", data: enc.encode(responseCss) },
        { name: "response_contract/STYLE_VERSION.txt", data: enc.encode(RESPONSE_STYLE_VERSION + "\n") },
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

  async function loadResponseCss() {
    try {
      const url = new URL("response_styles.css", window.location.href);
      const response = await fetch(url, { cache: "no-store" });
      if (response.ok) return await response.text();
    } catch (error) {
      console.warn("Using embedded response CSS fallback.", error);
    }
    return RESPONSE_CSS_FALLBACK;
  }


  function resolveGradeOutput(mode, hasRubric) {
    switch (mode) {
      case "none":
        return {
          mode: "none",
          label: "Feedback only",
          policy: "Return feedback and next steps only. Do not return a numeric grade, letter grade, point score, or mastery label. A provided rubric may organize feedback but must not be converted into a reported score unless the teacher changes this mode."
        };
      case "rubric":
        return {
          mode: "rubric",
          label: "Use supplied rubric / scoring guide",
          policy: "Use the supplied rubric/scoring guide as the grading authority. Report criterion scores and an overall score/grade only when the supplied rubric or scale defines how to do so. Do not invent missing weights, cut scores, or letter-grade conversions."
        };
      case "recommend":
        return {
          mode: "recommend",
          label: "Recommend a grade from the evidence",
          policy: hasRubric
            ? "Return an evidence-based grade recommendation using the supplied rubric/scoring guide when it applies. State the basis and flag uncertainty."
            : "Return an evidence-based grade recommendation. For clearly objective item-by-item work, a percentage/points-correct recommendation may be calculated from observable correctness when equal weighting is reasonable; state that assumption. Apply any explicit grading scale supplied in teacher notes. For subjective/open-ended work without a defensible scale, return the mastery level Secure / Developing / Needs Revision instead of inventing a numeric or letter grade, and flag the limitation."
        };
      case "mastery":
      default:
        return {
          mode: "mastery",
          label: "Mastery level",
          policy: "Return exactly one overall mastery level for each student: Secure, Developing, or Needs Revision, supported by the submitted evidence. Do not convert that mastery level into a numeric or letter grade unless the teacher selects a different grade-output mode."
        };
    }
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
    const rubricLine = request.rubric_files.length
      ? "A rubric/scoring guide is included under rubric/ and listed in request.json. Use it according to the selected grade-output mode."
      : "No rubric/scoring guide is included.";
    const rosterLine = request.roster_files.length
      ? "A roster is included under roster/ and listed in request.json under roster_files. Use it only to resolve student names, identify missing/unmatched evidence, and preserve roster order. Do not infer achievement from the roster."
      : "No roster is included. Resolve names only from the submitted evidence and filenames; after one reasonable identity pass, use stable neutral labels for unreadable names rather than stalling or guessing.";
    const scannedPath = request.requested_outputs.scanned_student_work_pdf;

    return `# District Grading & Evidence Request - Pilot

## Task
Analyze the student evidence in this ZIP and return exactly ONE response ZIP. This packaged request is the complete build contract; no additional teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.

Class / group: ${request.teacher.class_or_group}
Assignment / evidence set: ${request.assignment.name}
Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when the evidence makes it reasonably clear."}
${rubricLine}
${rosterLine}
Selected grade / score output: ${request.grade_output.label}
Authoritative grading policy: ${request.grade_output.policy}

Teacher notes:
${teacherNotes || "No additional notes provided."}

## Evidence rules
- Judge student work from the supplied evidence, rubric (if present), roster (identity/order only), and teacher notes.
- Do not research students or use outside personal information.
- Do not rely on prior chats, memories, or prior student records unless they are included in this request ZIP.
- Do not use public web research to decide whether student work is correct. General subject-matter knowledge may be used to interpret evidence and create follow-up practice.
- Do not silently guess when a student identity, response, rubric match, or piece of handwriting is unclear. Flag uncertainty.
- If some files cannot be read, process the readable evidence and clearly list the unreadable or ambiguous files.
- If a roster student has no identifiable submitted work, mark that as no evidence submitted rather than as incorrect work.
- If evidence names a student not found on the roster, keep the evidence and flag the mismatch rather than discarding it.
- IDENTITY PASS: For combined scans, do one reasonable pass to match pages to students. Use roster/ when supplied. If a handwritten name remains unreadable, assign a stable neutral label such as Student 01, preserve the page/evidence mapping, flag the uncertainty, and continue the analysis. Do not let uncertain names stall the entire run.

## Scoring and feedback policy
- The selected grade-output mode in request.json is authoritative. Teacher notes may add grading details (for example, a scale) but may not override the selected mode. If a note conflicts with the selected mode, follow the selected mode, record the conflict in data/qa.json, and continue rather than stalling.
- ${request.scoring_policy}
- Distinguish demonstrated strengths from next steps.
- Do not rank students against one another.
- Make student-facing language age-appropriate when the grade level can be determined.
- Treat any AI-produced score or classification as a teacher-review recommendation, not an irreversible final grade.

## Locked response styling
The request includes response_contract/styles.css. Copy those exact bytes to assets/styles.css in the response ZIP and use that stylesheet for ALL response HTML pages. Do not substitute a new visual theme. Avoid page-specific inline CSS except when strictly necessary for content generated from evidence. The goal is repeatable output across grading runs.

Use the stylesheet classes as intended:
- CLICK_ME.html: wrap, hero, eyebrow, subtitle, quick-actions, btn, section, grid, card, summary-grid, stat, notice.
- Student reports: report-page, report-head, report-meta, report-section, feedback-box, clean.
- Practice/packets: practice-page or packet-page, name-line, practice-block.
- Math/visual content: math-inline, math-display, visual-block, graph-frame, figure-caption.
- Combined printable documents: page-break between students.

## Math, graph, and visual rendering - HARD
The request includes response_contract/MATH_VISUAL_QA.md. Follow it as an executable contract, not a suggestion.

- MATH: If mathematical notation appears, author valid TeX and render it with MathJax. Inspect the rendered page and rendered PDF. Raw TeX/delimiters visible to the teacher or student are a QA failure.
- GRAPHS: If any report, explanation, question, or packet needs a graph, generate an actual mathematically accurate graph with the best available approved graph-generation capability. Prefer a dedicated grapher when it is exposed; otherwise use another accurate plotting capability. Include the real SVG/PNG asset. Do not merely say what a graph would show, and never ship a prose placeholder, ASCII art, or CSS sketch in place of a required graph.
- IMAGES/DIAGRAMS: If text refers to an image, diagram, figure, model, or other visual, create the actual visual and embed it. Never refer to a visual that does not exist in the output.
- Store generated graphs under assets/graphs/ and other created visuals under assets/visuals/. Embed the same real assets in HTML and the corresponding PDFs.
- Create data/qa.json and record MathJax, grade-output, graph-generation, visual, link, and PDF checks required by the included QA contract.
- If a dedicated grapher is unavailable, use another accurate graph-generation capability. If no capability can create a graph needed only for newly generated follow-up practice, revise that generated task so it does not depend on a missing graph. Never substitute prose that refers to a graph that is not present. MathJax rendering failures must still be repaired before delivery.

## Required response ZIP structure
~~~text
CLICK_ME.html
assets/
  styles.css
  graphs/
    <actual graph SVG/PNG assets when graphs are used>
  visuals/
    <actual created visual assets when visuals are used>
scanned_work/
  ${scannedPath.split('/').pop()}
students/
  <one print-friendly HTML report per identified student>
class/
  class_overview.html
print/
  all_student_reports.html
  all_student_reports.pdf
  common_review_extension_packet.html
  common_review_extension_packet.pdf
  individualized/
    <one print-friendly HTML practice packet per identified student>
  individualized_packets.pdf
data/
  analysis.json
  qa.json
  request.json
~~~

All package navigation, CSS, graph assets, and visual assets must use relative local links and work when the ZIP is unzipped. PDFs must be finished printable files, not placeholders. MathJax is the sole allowed external runtime dependency when a local/serialized MathJax result is not available; PDFs must already contain fully rendered mathematics and remain usable offline.

## Scanned student work archive
Create ${scannedPath} as the teacher-friendly archive of the submitted student work.
- If the submitted evidence is already one combined scan PDF, preserve the page content and simply give it the required teacher-friendly filename.
- If the submitted evidence is multiple scanned PDFs/images, combine the readable pages into one PDF in a sensible evidence/roster order while preserving the original work.
- Do not redraw, rewrite, clean up, or alter student answers.
- If a submitted file cannot reasonably be represented in the combined PDF, keep the readable work in the PDF and record the limitation in class/class_overview.html and data/analysis.json.

## CLICK_ME.html layout - fixed
Keep the dashboard compact. Use this order:

1. Hero/header with class, assignment, and grade/subject.
2. ONE top quick-action row with exactly these three prominent buttons:
   - Print All Student Reports (PDF) -> print/all_student_reports.pdf
   - Print All Individualized Practice (PDF) -> print/individualized_packets.pdf
   - View Scanned Student Work (PDF) -> ${scannedPath}
3. Individual Student Reports section with one link/card per student.
4. Class Data section with a concise pattern summary and link to class/class_overview.html.
5. Print Options section containing ONLY items that are not duplicates of the three top quick actions:
   - Common Class Review + Extension -> common packet PDF/HTML.
   - Individual Student Practice -> one clearly labeled link/card per student's individualized HTML packet.

Do NOT repeat Print All Student Reports, Print All Individualized Practice, or View Scanned Student Work again lower on CLICK_ME.html. The teacher should never have to click a second-looking button just to discover it is the same file.

## Individual student reports
Keep the current concise report format: student name/label and assignment; the grade/score/mastery result required by request.grade_output; demonstrated strengths; the most important misconception/gap/revision need; specific evidence references when feasible; rubric criterion results only when supported; 1-3 concrete next steps; and an uncertainty note when needed. Do not include other students' names or performance.

Create print/all_student_reports.html and print/all_student_reports.pdf containing every student's full report in roster order when a roster is available, otherwise identified order. Put a clear page break between students. Do not create a shortened second version.

## Class analysis
Create class/class_overview.html for the teacher. Include the number of evidence sets analyzed, class strengths, the most instructionally important common mistakes, reliable counts/percentages for major patterns, suggested instructional groupings, students ready for extension, and evidence/identity limitations. Groupings are instructional recommendations, not permanent labels.

## Print option - Common Class Review + Extension
Create one general packet driven by actual class patterns, not a generic worksheet. Target the 1-3 most useful common mistakes or unfinished understandings, include concise support/examples when useful, include practice that directly addresses the patterns, and include 1-2 extension opportunities when evidence supports them. Avoid student names. Make it usable as whole-class work, small-group work, or stations at teacher discretion. Provide both HTML and PDF.

## Print option - Individualized Practice
Create one student-specific practice packet for every identified student. Target that student's highest-leverage next step(s), avoid unnecessary practice on already-secure skills, and use extension/transfer instead of remediation when appropriate. Never compare the student to classmates. Save individual HTML packets in print/individualized/ and create print/individualized_packets.pdf containing the entire class set with a page break between students.

## data/analysis.json
Store the structured analysis behind the reports and print materials. Include student identifiers/labels, evidence-file mapping, roster matching status when applicable, rubric results when applicable, strengths, needs, class pattern counts, grouping recommendations, common-packet targets, individualized-practice targets, and uncertainty flags. Copy request.json into data/request.json.

## Final QA before delivery
- assets/styles.css exactly matches response_contract/styles.css from this request.
- CLICK_ME.html has exactly one top quick-action row and no duplicate quick-action links lower on the page.
- The scanned-work PDF exists at ${scannedPath} and the top dashboard link opens it.
- Combined student-report PDF contains all identified students in roster/identified order with page breaks.
- Combined individualized-practice PDF contains all identified students with page breaks.
- Every page containing math has been rendered with MathJax and visually checked; no raw TeX/delimiters are visible in HTML or PDF.
- Every graph that is referenced or instructionally required exists as a mathematically accurate SVG/PNG asset created with the best available approved graph-generation capability, embedded, and visually checked; data/qa.json records the generation method and whether a dedicated grapher was available/used.
- Every referenced image/diagram/figure exists as a real embedded asset; there are no missing-visual placeholders.
- Generated graphs/visuals are legible in the related PDFs and are not clipped or separated from the prompt they support.
- data/qa.json records the selected grade-output mode, whether it was followed, any teacher-note conflict, and reports PASS with no unresolved math, graph, visual, link, or PDF failures.
- All relative HTML links resolve after unzip.
- Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.
`;
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

  // Minimal ZIP writer using the STORE method (no compression). This keeps the
  // pilot self-contained with no CDN or third-party JavaScript dependency.
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
      lv.setUint16(6, 0x0800, true); // UTF-8 names
      lv.setUint16(8, 0, true);      // STORE
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
