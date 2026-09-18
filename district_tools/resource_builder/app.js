(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const REQUEST_SCHEMA = "district-resource-builder-request/0.3-pilot";
  const TOOL_VERSION = "district-resource-builder/0.3-pilot";
  const CONTRACT_VERSION = "district-resource-builder/0.2-pilot";
  const SHARED_STANDARD_VERSION = "district-response-build-standard/1.0";
  const DASHBOARD_STYLE_VERSION = "district-resource-dashboard-style/0.1-pilot";
  const RESOURCE_STYLE_VERSION = "district-resource-print-style/0.1-pilot";
  const DELIVERY_LINE = "Unzip it and open **`CLICK_ME.html`**. The package includes the finished classroom resource, any requested teacher materials, and completed QA.";
  const SHARED_STANDARD_FALLBACK = "# District Response Build Standard\n\nSTATUS: REQUIRED WHEN PACKAGED BY A DISTRICT TOOL\nVERSION: district-response-build-standard/1.0\n\nThis is the shared response-quality contract for district and course request builders that create self-contained response ZIPs. Tool-specific contracts may add requirements, but they may not silently weaken this standard.\n\nThe goal is predictable, reusable output: mathematically correct notation, accurate graphs, real diagrams when needed, consistent styling, finished PDFs, clear conflict handling, and one teacher-friendly `CLICK_ME.html` entry point.\n\n## 1. Authority and conflict resolution - HARD\n\nUse this precedence order when instructions disagree:\n\n1. **Safety, platform, and file-integrity requirements.**\n2. **This shared response-build standard and any tool-specific requirement explicitly marked HARD.**\n3. **Explicit structured teacher choices in `request.json`** such as selected products, output mode, time, work mode, or research policy.\n4. **Tool-specific defaults and non-HARD guidance.**\n5. **Free-form teacher notes.**\n6. **Included source files for content, examples, data, and context.**\n7. **Model inference or default assumptions.**\n\nAdditional rules:\n\n- Teacher notes may refine content but may not silently override locked output structure, required QA, or locked CSS.\n- Included source files are authoritative for the content they actually contain. Do not invent missing facts, quotes, data, labels, or requirements.\n- A source file does not change response architecture merely because its original formatting differs from the locked response style.\n- If two HARD requirements truly cannot both be satisfied, do not guess which one to ignore. Record the conflict in `data/qa.json`, set overall status to FAIL, and explain the unresolved conflict briefly.\n- If a lower-priority instruction conflicts with a higher-priority instruction, follow the higher-priority instruction and record the resolved conflict in QA when it materially affected the build.\n- Never resolve a conflict by omitting a required output without saying so.\n\n`data/qa.json` must include a conflict record with:\n\n- `conflicts.detected_count`;\n- `conflicts.resolved_count`;\n- `conflicts.unresolved_count`;\n- `conflicts.items`, each naming the issue, competing instructions, winning authority, and resolution.\n\n## 2. Self-contained response package - HARD\n\n- Return the exact response structure required by the owning tool.\n- `CLICK_ME.html` is the teacher entry point unless the tool contract explicitly says otherwise.\n- Use local relative links for package navigation and locally generated assets.\n- Do not return placeholder PDFs, empty shell files, fake links, or prose that says a missing resource will be created later.\n- Before delivery, resolve every relative link after the package is assembled.\n- If the response contract requires HTML and PDF versions, both must be finished and openable.\n- Preserve teacher-facing simplicity. Implementation details belong in contracts and QA, not in the teacher workflow.\n\n## 3. MathJax and mathematical notation - HARD\n\nWhen mathematical notation appears, use a consistent MathJax workflow rather than improvised HTML styling.\n\n### Authoring\n\n- Use valid TeX with `\\\\( ... \\\\)` for inline math and `\\\\[ ... \\\\]` for display math unless the owning tool explicitly defines another MathJax delimiter convention.\n- Use MathJax for expressions, equations, inequalities, vectors, exponents, radicals, fractions, subscripts, Greek letters, matrices, and other mathematical notation that benefits from typesetting.\n- Use semantic math notation rather than approximating math with `<i>`, superscript text, Unicode lookalikes, or manually positioned characters.\n- Put units in mathematically appropriate upright text when they are inside an expression, for example `\\\\(4\\\\,\\\\mathrm{m/s^2}\\\\)`.\n- Avoid raw `$...$` delimiters unless the MathJax configuration in the finished page explicitly enables and verifies them.\n\n### Rendering\n\n- MathJax must finish typesetting before PDF generation.\n- Prefer MathJax SVG output or another MathJax output mode that is stable in print.\n- Final HTML must not show raw TeX if a viewer opens the package normally.\n- A final package should not depend on a remote-only math renderer when a local or pre-rendered MathJax result can reasonably be produced. If an external runtime is unavoidable, record that dependency in QA and ensure the finished PDF is already fully rendered.\n- Do not rasterize ordinary equations merely to avoid MathJax.\n\n### QA\n\nFor every page containing math, visually inspect both HTML and the finished PDF. `data/qa.json` must record at least:\n\n- `mathjax.pages_with_math`;\n- `mathjax.rendered_and_checked`;\n- `mathjax.raw_tex_visible_count`;\n- `mathjax.pdf_generated_after_typeset`;\n- `mathjax.external_runtime_dependency`.\n\nPASS is not allowed if raw TeX is visible, symbols are missing, formulas are clipped, or the PDF was generated before MathJax finished.\n\n## 4. Graphs and grapher use - HARD\n\nIf a task, answer, explanation, or source requires a mathematical graph, create or supply the actual accurate graph.\n\n- Prefer the platform's dedicated graphing/grapher capability when available.\n- If a dedicated grapher is not available, use a deterministic math/plotting method that computes the graph from the actual function/data.\n- Do **not** use a generative image model to fabricate a quantitatively accurate mathematical graph.\n- Do not substitute prose, ASCII art, a decorative sketch, or a blank box for a required graph.\n- Save generated graph assets under the owning tool's graph asset folder, normally `assets/graphs/`.\n- Prefer SVG when practical for crisp printing; PNG is acceptable when appropriate.\n- Include readable axes, scale, tick marks, labels, units, plotted points/curves, and legends when the task requires them.\n- Verify that the plotted relationship, coordinates, intercepts, asymptotes, domain/range cues, and scale are mathematically correct for the task.\n- If students are supposed to create the graph themselves, do not reveal the completed answer graph. Supply only the prompt, data, axes/grid, or other neutral scaffold the task actually requires.\n\n`data/qa.json` must include:\n\n- `graphs.required_count`;\n- `graphs.created_or_supplied_count`;\n- `graphs.dedicated_grapher_available`;\n- `graphs.dedicated_grapher_used_when_available`;\n- `graphs.assets`, including each path, generation method, and accuracy-check result.\n\nPASS is not allowed if a required graph is missing or mathematically inaccurate.\n\n## 5. Diagrams, figures, and instructional visuals - HARD\n\nUse real visuals when the task depends on spatial, structural, or representational information.\n\nExamples include force setups, circuits, geometric figures, maps, experimental apparatus, labeled biological structures, tables/data displays, coordinate grids, vector layouts, timelines, and process diagrams.\n\n- If the task refers to a diagram, figure, image, setup, model, map, table, or other visual, that visual must actually exist in the response or in an explicitly included source file.\n- Prefer clean vector/SVG instructional diagrams for simple line art, geometry, force setups, circuits, arrows, and labeled models.\n- Use generated raster imagery only when a realistic image is genuinely useful; decorative imagery is not a substitute for an instructional diagram.\n- If a visual would materially reduce ambiguity or reading load, include it even when the prompt could technically be written without one.\n- If **creating the diagram is the assessed skill**, do not give away the completed answer. Provide only a neutral setup sketch, blank grid, unlabeled structure, or other scaffold when useful.\n- In physics, a scenario sketch and a force diagram are not automatically the same thing. If students are being assessed on constructing the force diagram, a neutral object/setup sketch may be supplied without pre-drawing the answer vectors.\n- Save generated non-graph visuals under the owning tool's visual asset folder, normally `assets/visuals/`.\n- Every referenced visual must have a resolvable path and appear at readable print size.\n\n`data/qa.json` must include:\n\n- `visuals.required_count`;\n- `visuals.created_or_supplied_count`;\n- `visuals.assets`, with path, purpose, generation method, and visual-check result.\n\nPASS is not allowed if a prompt refers to a visual that is absent, unreadable, misleading, or answer-revealing when the student is supposed to construct it.\n\n## 6. Locked CSS and visual consistency - HARD\n\nEach tool owns an exact response stylesheet snapshot. The shared district standard defines the behavior; the owning tool's packaged CSS defines the final appearance.\n\n- Copy each locked CSS file from the request package **byte-for-byte** to the required response asset path.\n- Do not restyle the response because another source file uses different fonts, colors, spacing, or page layout.\n- Do not silently add inline CSS that defeats the locked stylesheet.\n- If the content does not fit, improve wording, chunking, or layout **within the existing CSS contract first**. Do not solve overflow by shrinking text to an unreadable size.\n- If the owning tool requires one page, one landscape page, duplex-safe pages, or another print rule, satisfy that rule and verify the actual rendered PDF.\n- Extra pages that are not explicitly assigned another style should inherit the owning tool's teacher/dashboard style rather than inventing a third visual system.\n- Keep common district response conventions when they exist: white background, dark readable text, restrained blue/navy accent, clear sections/cards, prominent action buttons, high-contrast print, and uncluttered teacher navigation.\n- Tool-specific student artifacts may use a specialized locked layout when that improves classroom use.\n\nThe request should provide a style version and, when practical, a SHA-256 hash for each locked CSS file. `data/qa.json` must record expected and actual hashes and whether they match.\n\nPASS is not allowed when locked CSS does not match the request snapshot or when the final PDF is clipped/unreadable despite a hash match.\n\n## 7. PDF generation and visual QA - HARD\n\nA file existing is not enough. Finished PDFs must be rendered and visually inspected.\n\n- Generate PDFs only after fonts, MathJax, graphs, diagrams, and linked assets are ready.\n- Verify page size/orientation, margins, page breaks, clipping, overlap, unreadably small text, missing images, broken math, and accidental blank pages.\n- Verify that print-specific rules such as one-page cards, landscape stations, or duplex padding are true in the **actual PDF**, not merely intended by CSS.\n- Open every required PDF after generation.\n- When the environment supports page rendering/screenshots, inspect the rendered pages rather than relying only on text extraction.\n\n`data/qa.json` must include:\n\n- `pdfs.rendered_and_visually_checked`;\n- `pdfs.openable`;\n- per-file page size/orientation and page count when the tool contract depends on them;\n- `pdfs.failures` for clipping, missing assets, or layout problems.\n\n## 8. Content integrity and teacher review - HARD\n\n- Do not invent source facts, quotations, student evidence, measurements, citations, or teacher decisions.\n- When a teacher has explicitly chosen an option in the request UI, treat that structured selection as authoritative over conflicting free-form notes.\n- Flag uncertainty instead of pretending it is resolved.\n- Answer keys/evidence guides must match the exact student tasks in the final student artifact.\n- If a task changes during layout editing, update the guide/answer key too and rerun QA.\n- Do not rank students, classes, teachers, or political choices unless the owning tool explicitly calls for a permitted non-political ranking.\n\n## 9. QA record - HARD\n\nEvery response package covered by this standard must create `data/qa.json` or the owning tool's equivalent QA path.\n\nAt minimum record:\n\n- shared-standard version;\n- tool-specific contract version;\n- overall PASS/FAIL;\n- conflict resolution summary;\n- MathJax status;\n- graph status;\n- visual/diagram status;\n- locked CSS expected/actual hashes;\n- relative-link resolution;\n- required-file existence;\n- PDF open/visual checks;\n- tool-specific checks;\n- `failures` array.\n\n`overall_status: PASS` is not allowed while `failures` contains an unresolved item.\n\n## 10. Delivery - HARD\n\nReturn one authoritative response ZIP when the owning tool requests one. Keep the user-facing delivery note short and useful. Do not present internal component files as competing required deliverables unless the teacher explicitly asked for them separately.\n";

  let profiles = [];
  let currentProfile = null;
  const sourceInput = $("sourceFiles");
  const status = $("buildStatus");
  const buildButton = $("buildZip");

  init();

  async function init() {
    renderTargetInputs();
    bindCommonEvents();
    try {
      const response = await fetch("resource_profiles.json?v=0.3-pilot", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      profiles = data.profiles || [];
      if (!profiles.length) throw new Error("No resource profiles found.");
      renderProfileSelect();
      selectProfile(profiles[0].id);
      refreshStatus();
    } catch (error) {
      console.error(error);
      setStatus("Could not load resource profiles. Refresh this page from the District Tools website.", "bad");
      buildButton.disabled = true;
    }
  }

  function renderTargetInputs() {
    $("targetInputs").innerHTML = [1,2,3,4].map((n) => `<div class="target-row"><div class="target-num">${n}</div><input id="target${n}" type="text" placeholder="${n === 1 ? "I can..." : "Optional additional target"}"></div>`).join("");
  }

  function bindCommonEvents() {
    ["resourceName","teacherName","subjectCourse","gradeLevel","unitTopic","timeLength","readingLevel","context","standards","teacherNotes"].forEach((id) => $(id).addEventListener("input", refreshStatus));
    [1,2,3,4].forEach((n) => document.addEventListener("input", (e) => { if (e.target && e.target.id === `target${n}`) refreshStatus(); }));
    document.querySelectorAll('#priorityChoices input[type="checkbox"]').forEach((el) => el.addEventListener("change", refreshStatus));
    sourceInput.addEventListener("change", () => { renderFiles(sourceInput.files, $("sourceList")); refreshStatus(); });
    $("clearForm").addEventListener("click", clearForm);
    buildButton.addEventListener("click", buildRequestZip);
  }

  function renderProfileSelect() {
    $("resourceType").innerHTML = profiles.map((p) => `<option value="${escAttr(p.id)}">${escHtml(p.label)}</option>`).join("");
    $("resourceType").addEventListener("change", () => selectProfile($("resourceType").value));
  }

  function selectProfile(id) {
    currentProfile = profiles.find((p) => p.id === id) || profiles[0];
    $("resourceType").value = currentProfile.id;
    $("profileSummary").innerHTML = `<h3>${escHtml(currentProfile.label)}</h3><div class="small">${escHtml(currentProfile.summary || "")}</div>`;
    renderProfileControls(currentProfile);
    refreshStatus();
  }

  function renderProfileControls(profile) {
    const mount = $("profileControls");
    mount.innerHTML = "";
    (profile.controls || []).forEach((control) => {
      const wrap = document.createElement("div");
      wrap.className = `profile-control ${control.type === "checkbox" ? "checkbox" : ""}`;
      const id = `profile_${control.id}`;
      if (control.type === "checkbox") {
        wrap.innerHTML = `<input id="${id}" type="checkbox" ${control.default ? "checked" : ""}><label for="${id}">${escHtml(control.label)}</label>`;
      } else if (control.type === "select") {
        wrap.innerHTML = `<div><label for="${id}">${escHtml(control.label)}</label><select id="${id}">${(control.options || []).map(([value,label]) => `<option value="${escAttr(value)}" ${String(value) === String(control.default) ? "selected" : ""}>${escHtml(label)}</option>`).join("")}</select></div>`;
      } else if (control.type === "number") {
        wrap.innerHTML = `<div><label for="${id}">${escHtml(control.label)}</label><input id="${id}" type="number" value="${escAttr(control.default ?? "")}" ${control.min != null ? `min="${control.min}"` : ""} ${control.max != null ? `max="${control.max}"` : ""}></div>`;
      } else {
        wrap.innerHTML = `<div><label for="${id}">${escHtml(control.label)}</label><input id="${id}" type="text" value="${escAttr(control.default || "")}" placeholder="${escAttr(control.placeholder || "")}"></div>`;
      }
      mount.appendChild(wrap);
      const input = $(id);
      input.addEventListener(control.type === "checkbox" || control.type === "select" ? "change" : "input", refreshStatus);
    });
  }

  function getTargets() {
    return [1,2,3,4].map((n) => $(`target${n}`).value.trim()).filter(Boolean);
  }

  function getPriorities() {
    return [...document.querySelectorAll('#priorityChoices input[type="checkbox"]:checked')].map((el) => el.value);
  }

  function getProfileOptions() {
    const out = {};
    (currentProfile?.controls || []).forEach((control) => {
      const el = $(`profile_${control.id}`);
      if (!el) return;
      out[control.id] = control.type === "checkbox" ? el.checked : control.type === "number" ? Number(el.value) : el.value.trim();
    });
    return out;
  }

  function resolveOutputs(profileId, options) {
    const common = [];
    if (profileId === "worksheet_practice") return {primary:["resource/worksheet.html","resource/worksheet.pdf"],teacher:options.answer_key ? ["teacher/answer_key.html","teacher/answer_key.pdf"] : [],required_files:[]};
    if (profileId === "differentiated_worksheet") {
      const count = Number(options.version_count || 2);
      const primary = [];
      ["a","b","c"].slice(0,count).forEach((v) => primary.push(`resource/version_${v}.html`,`resource/version_${v}.pdf`));
      const teacher = ["teacher/differentiation_notes.html","teacher/differentiation_notes.pdf"];
      if (options.answer_key) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary,teacher,required_files:[]};
    }
    if (profileId === "extension_activity") return {primary:["resource/extension_activity.html","resource/extension_activity.pdf"],teacher:options.teacher_guide ? ["teacher/teacher_guide.html","teacher/teacher_guide.pdf"] : [],required_files:[]};
    if (profileId === "formative_assessment") {
      const teacher = [];
      if (options.answer_key || options.misconception_notes) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary:["resource/formative_assessment.html","resource/formative_assessment.pdf"],teacher,required_files:[]};
    }
    if (profileId === "rubric") return {primary:["resource/rubric.html","resource/rubric.pdf"],teacher:[],required_files:[]};
    if (profileId === "lesson_outline") return {primary:["resource/lesson_outline.html","resource/lesson_outline.pdf"],teacher:[],required_files:[]};
    if (profileId === "presentation") {
      const primary = ["resource/presentation.pptx","resource/presentation.pdf"];
      if (options.student_handout) primary.push("resource/student_handout.html","resource/student_handout.pdf");
      const teacher = options.speaker_notes ? ["teacher/speaker_notes.html","teacher/speaker_notes.pdf"] : [];
      return {primary,teacher,required_files:[]};
    }
    if (profileId === "stations") {
      const teacher = ["teacher/station_guide.html","teacher/station_guide.pdf"];
      if (options.answer_key) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary:["resource/stations.html","resource/stations.pdf"],teacher,required_files:[]};
    }
    if (profileId === "unit_outline") return {primary:["resource/unit_outline.html","resource/unit_outline.pdf"],teacher:[],required_files:[]};
    if (profileId === "blooket_review") return {primary:["resource/blooket_import.csv"],teacher:["teacher/answer_key.html","teacher/answer_key.pdf"],required_files:[]};
    if (profileId === "custom_resource") {
      const fmt = options.output_format || "best_fit";
      let primary = ["resource/custom_resource.html","resource/custom_resource.pdf"];
      if (fmt === "docx") primary = ["resource/custom_resource.docx"];
      if (fmt === "pptx") primary = ["resource/custom_resource.pptx"];
      if (fmt === "csv") primary = ["resource/custom_resource.csv"];
      if (fmt === "best_fit") primary = ["resource/custom_resource.*"];
      const teacher = options.teacher_support ? ["teacher/teacher_guide.html","teacher/teacher_guide.pdf"] : [];
      return {primary,teacher,required_files:[]};
    }
    return {primary:common,teacher:[],required_files:[]};
  }

  function refreshStatus() {
    if (!currentProfile) return false;
    const missing = [];
    if (!$("resourceName").value.trim()) missing.push("resource name");
    if (!$("subjectCourse").value.trim()) missing.push("subject/course");
    if (!getTargets().length) missing.push("at least one learning target");
    if (missing.length) { setStatus(`Add ${missing.join(", ")}.`, "warn"); return false; }
    setStatus(`Ready to build a ${currentProfile.label} request with ${getTargets().length} target${getTargets().length === 1 ? "" : "s"}${sourceInput.files.length ? ` and ${sourceInput.files.length} source file${sourceInput.files.length === 1 ? "" : "s"}` : ""}.`, "good");
    return true;
  }

  async function buildRequestZip() {
    if (!refreshStatus()) return;
    buildButton.disabled = true;
    setStatus("Packaging request...", "warn");
    try {
      const entries = [];
      const sourceManifest = [];
      const used = new Set();
      for (const file of [...sourceInput.files]) {
        const name = uniqueName(safeFileName(file.name), used);
        const path = `sources/${name}`;
        sourceManifest.push({original_name:file.name,packaged_path:path,mime_type:file.type || null,size_bytes:file.size});
        entries.push({name:path,data:new Uint8Array(await file.arrayBuffer())});
      }

      const profileOptions = getProfileOptions();
      const outputs = resolveOutputs(currentProfile.id, profileOptions);
      outputs.required_files = ["CLICK_ME.html","assets/dashboard_styles.css","assets/resource_styles.css","data/request.json","data/qa.json",...outputs.primary,...outputs.teacher];

      const [contractText, sharedText, dashboardCss, resourceCss] = await Promise.all([
        loadText("RESOURCE_BUILDER_CONTRACT.md?v=0.3-pilot"),
        loadText("DISTRICT_RESPONSE_BUILD_STANDARD.md?v=0.3-pilot", SHARED_STANDARD_FALLBACK),
        loadText("dashboard_styles.css?v=0.3-pilot"),
        loadText("resource_styles.css?v=0.3-pilot")
      ]);
      const [dashboardHash, resourceHash] = await Promise.all([sha256Hex(dashboardCss), sha256Hex(resourceCss)]);

      const request = {
        schema: REQUEST_SCHEMA,
        tool_version: TOOL_VERSION,
        created_at: new Date().toISOString(),
        contracts: {resource_builder:CONTRACT_VERSION,shared_standard:SHARED_STANDARD_VERSION},
        resource: {name:$("resourceName").value.trim(),profile_id:currentProfile.id,profile_label:currentProfile.label,unit_topic:valueOrNull("unitTopic")},
        teacher: {name:valueOrNull("teacherName"),subject_course:$("subjectCourse").value.trim(),grade_level:valueOrNull("gradeLevel")},
        learning_targets: getTargets(),
        context: valueOrNull("context"),
        standards_framework: valueOrNull("standards"),
        time_length_constraint: valueOrNull("timeLength"),
        target_reading_access_level: valueOrNull("readingLevel"),
        design_priorities: getPriorities(),
        profile_options: profileOptions,
        profile_snapshot: currentProfile,
        teacher_notes: valueOrNull("teacherNotes"),
        source_files: sourceManifest,
        resolved_outputs: outputs,
        locked_styles: {
          dashboard:{version:DASHBOARD_STYLE_VERSION,request_path:"response_contract/dashboard_styles.css",response_path:"assets/dashboard_styles.css",sha256:dashboardHash},
          resource:{version:RESOURCE_STYLE_VERSION,request_path:"response_contract/resource_styles.css",response_path:"assets/resource_styles.css",sha256:resourceHash}
        },
        authority_note: "Structured resource/profile choices outrank conflicting free-form notes. Follow the packaged shared district conflict standard.",
        delivery: {required_final_line:DELIVERY_LINE}
      };

      entries.unshift(
        {name:"REQUEST_READ_ME_FIRST.md",data:enc.encode(buildInstructions(request))},
        {name:"request.json",data:enc.encode(JSON.stringify(request,null,2))},
        {name:"response_contract/RESOURCE_BUILDER_CONTRACT.md",data:enc.encode(contractText)},
        {name:"response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md",data:enc.encode(sharedText)},
        {name:"response_contract/SELECTED_PROFILE.json",data:enc.encode(JSON.stringify(currentProfile,null,2))},
        {name:"response_contract/dashboard_styles.css",data:enc.encode(dashboardCss)},
        {name:"response_contract/resource_styles.css",data:enc.encode(resourceCss)},
        {name:"response_contract/CONTRACT_VERSION.txt",data:enc.encode(CONTRACT_VERSION + "\n")},
        {name:"response_contract/SHARED_STANDARD_VERSION.txt",data:enc.encode(SHARED_STANDARD_VERSION + "\n")},
        {name:"response_contract/DASHBOARD_STYLE_SHA256.txt",data:enc.encode(dashboardHash + "\n")},
        {name:"response_contract/RESOURCE_STYLE_SHA256.txt",data:enc.encode(resourceHash + "\n")}
      );

      const blob = makeZip(entries);
      const filename = `resource_builder_request_${slug(request.resource.name)}_${dateStamp()}.zip`;
      downloadBlob(blob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function buildInstructions(request) {
    const targets = request.learning_targets.map((t,i) => `${i+1}. ${t}`).join("\n");
    const priorities = request.design_priorities.length ? request.design_priorities.join(", ") : "No extra priorities selected beyond accuracy and the profile contract.";
    const sources = request.source_files.length ? `${request.source_files.length} source file(s) are included under sources/.` : "No source files were attached.";
    return `# District Resource Builder Request - Pilot\n\n## Run automatically\nBuild the complete classroom resource from this request ZIP and return exactly ONE response ZIP. No additional teacher prompt is required.\n\nResource: ${request.resource.name}\nType: ${request.resource.profile_label}\nSubject/course: ${request.teacher.subject_course}\nGrade level: ${request.teacher.grade_level || "Not specified"}\nUnit/topic: ${request.resource.unit_topic || "Not specified"}\nTime/length: ${request.time_length_constraint || "Not specified"}\nReading/access level: ${request.target_reading_access_level || "Not specified"}\nStandards/framework: ${request.standards_framework || "Not specified"}\nDesign priorities: ${priorities}\n${sources}\n\n## Learning targets\n${targets}\n\n## Context\n${request.context || "No additional context provided."}\n\n## Structured profile options\n\n\`\`\`json\n${JSON.stringify(request.profile_options,null,2)}\n\`\`\`\n\n## Teacher notes\n${request.teacher_notes || "No additional teacher notes provided."}\n\n## Required contracts\nFollow BOTH response_contract/RESOURCE_BUILDER_CONTRACT.md and response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md. The selected profile snapshot is response_contract/SELECTED_PROFILE.json. Structured selections in request.json are authoritative over conflicting free-form notes.\n\n## Required output files\n${request.resolved_outputs.required_files.map((p) => `- ${p}`).join("\n")}\n\nFor custom_resource with a wildcard primary output, resolve the wildcard to the practical file extension required by the selected/best-fit format and record the choice in data/qa.json.\n\nCopy the two locked CSS files byte-for-byte to the response assets and verify their SHA-256 hashes in QA. Use MathJax, accurate grapher output, and real diagrams/visuals whenever the contracts require them. Open and visually inspect all required PDFs/native artifacts before delivery.\n\nReturn only the completed response ZIP. The final user-facing line must be exactly:\n\n${request.delivery.required_final_line}\n`;
  }

  function clearForm() {
    ["resourceName","teacherName","subjectCourse","gradeLevel","unitTopic","timeLength","readingLevel","context","standards","teacherNotes"].forEach((id) => $(id).value = "");
    [1,2,3,4].forEach((n) => $(`target${n}`).value = "");
    sourceInput.value = ""; $("sourceList").innerHTML = "";
    document.querySelectorAll('#priorityChoices input[type="checkbox"]').forEach((el) => { el.checked = ["real_world_application","inclusion_accessibility","engagement"].includes(el.value); });
    selectProfile(profiles[0].id);
    refreshStatus();
  }

  function renderFiles(files,target){target.innerHTML="";[...files].forEach((file)=>{const li=document.createElement("li");li.textContent=`${file.name} (${formatBytes(file.size)})`;target.appendChild(li);});}
  function formatBytes(bytes){if(bytes<1024)return `${bytes} B`;if(bytes<1024*1024)return `${(bytes/1024).toFixed(1)} KB`;return `${(bytes/(1024*1024)).toFixed(1)} MB`;}
  function setStatus(message,kind){status.textContent=message;status.className=`status ${kind}`;}
  function valueOrNull(id){const v=$(id).value.trim();return v||null;}
  async function loadText(path,fallback=null){
    try{
      const response=await fetch(path,{cache:"no-store"});
      if(!response.ok)throw new Error(`Could not load ${path} (HTTP ${response.status})`);
      return await response.text();
    }catch(error){
      if(fallback!==null){console.warn(`Using embedded fallback for ${path}.`,error);return fallback;}
      throw error;
    }
  }
  async function sha256Hex(value){const digest=await crypto.subtle.digest("SHA-256",enc.encode(String(value)));return [...new Uint8Array(digest)].map((b)=>b.toString(16).padStart(2,"0")).join("");}
  function escHtml(value){return String(value??"").replace(/[&<>"']/g,(ch)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));}
  function escAttr(value){return escHtml(value);}
  function safeFileName(name){const cleaned=String(name||"file").replace(/[\\/:*?"<>|\u0000-\u001f]/g,"_").replace(/^\.+/,"").trim();return cleaned||"file";}
  function uniqueName(name,used){let candidate=name,n=2;while(used.has(candidate.toLowerCase())){const dot=name.lastIndexOf(".");candidate=dot>0?`${name.slice(0,dot)}_${n}${name.slice(dot)}`:`${name}_${n}`;n++;}used.add(candidate.toLowerCase());return candidate;}
  function slug(value){return String(value||"request").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"").slice(0,48)||"request";}
  function dateStamp(){const d=new Date();return `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,"0")}${String(d.getDate()).padStart(2,"0")}`;}
  function downloadBlob(blob,filename){const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}

  function makeZip(entries) {
    const localParts=[],centralParts=[];let offset=0,count=0;
    for(const entry of entries){const nameBytes=enc.encode(entry.name.replace(/\\/g,"/"));const data=entry.data instanceof Uint8Array?entry.data:new Uint8Array(entry.data);const crc=crc32(data);const {time,date}=dosTimeDate(new Date());
      const local=new Uint8Array(30+nameBytes.length),lv=new DataView(local.buffer);lv.setUint32(0,0x04034b50,true);lv.setUint16(4,20,true);lv.setUint16(6,0x0800,true);lv.setUint16(8,0,true);lv.setUint16(10,time,true);lv.setUint16(12,date,true);lv.setUint32(14,crc,true);lv.setUint32(18,data.length,true);lv.setUint32(22,data.length,true);lv.setUint16(26,nameBytes.length,true);lv.setUint16(28,0,true);local.set(nameBytes,30);localParts.push(local,data);
      const central=new Uint8Array(46+nameBytes.length),cv=new DataView(central.buffer);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(8,0x0800,true);cv.setUint16(10,0,true);cv.setUint16(12,time,true);cv.setUint16(14,date,true);cv.setUint32(16,crc,true);cv.setUint32(20,data.length,true);cv.setUint32(24,data.length,true);cv.setUint16(28,nameBytes.length,true);cv.setUint16(30,0,true);cv.setUint16(32,0,true);cv.setUint16(34,0,true);cv.setUint16(36,0,true);cv.setUint32(38,0,true);cv.setUint32(42,offset,true);central.set(nameBytes,46);centralParts.push(central);offset+=local.length+data.length;count++;}
    const centralSize=centralParts.reduce((s,p)=>s+p.length,0),end=new Uint8Array(22),ev=new DataView(end.buffer);ev.setUint32(0,0x06054b50,true);ev.setUint16(4,0,true);ev.setUint16(6,0,true);ev.setUint16(8,count,true);ev.setUint16(10,count,true);ev.setUint32(12,centralSize,true);ev.setUint32(16,offset,true);ev.setUint16(20,0,true);return new Blob([...localParts,...centralParts,end],{type:"application/zip"});
  }
  function dosTimeDate(d){const year=Math.max(1980,d.getFullYear());return {time:(d.getHours()<<11)|(d.getMinutes()<<5)|Math.floor(d.getSeconds()/2),date:((year-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate()};}
  const crcTable=(()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);t[n]=c>>>0;}return t;})();
  function crc32(bytes){let crc=0xffffffff;for(const b of bytes)crc=crcTable[(crc^b)&0xff]^(crc>>>8);return (crc^0xffffffff)>>>0;}
})();
