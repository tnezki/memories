(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const REQUEST_SCHEMA = "district-tiered-task-request/0.1-pilot";
  const TOOL_VERSION = "district-tiered-task-tool/0.1-pilot";
  const CONTRACT_VERSION = "district-tiered-task-generation/0.1-pilot";
  const TASK_CARD_STYLE_VERSION = "district-tiered-task-card-style/0.1-pilot";
  const GUIDE_STYLE_VERSION = "district-tiered-task-guide-style/0.1-pilot";

  const CONTRACT_FALLBACK = `# Tiered Task Generation Contract\n\nSTATUS: REQUIRED\nVERSION: ${CONTRACT_VERSION}\n\nCreate exactly one integrated student Tiered Task Card containing DOK 1, DOK 2, DOK 3, and DOK 4 tasks aligned to the submitted I Can statements. Treat DOK as cognitive complexity rather than difficulty or verb matching. DOK 4 must require genuine extended thinking through investigation, synthesis, design, modeling, transfer, or iterative development. A target reading level may simplify wording and access but may not reduce academic demand. Show only teacher-allowed product types and keep the same evidence standard across product media. Create a Teacher Guide / Evidence Guide that maps every task to the I Can statements, explains the DOK rationale, and describes convincing evidence. Return one ZIP with CLICK_ME.html, HTML/PDF student card, HTML/PDF teacher guide, locked CSS, request.json, and qa.json. Use real required graphs/visuals and rendered MathJax when needed. All relative links must resolve.\n`;

  const TASK_CSS_FALLBACK = `@page{size:letter landscape;margin:.28in}*{box-sizing:border-box}html,body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#15191f}.task-card-page{width:10.44in;height:7.94in;margin:0 auto;display:flex;flex-direction:column;overflow:hidden}.task-head{display:grid;grid-template-columns:1.7fr 1fr;gap:.18in;border-bottom:2px solid #222;padding-bottom:.09in;margin-bottom:.09in}.task-title{font-size:20pt;font-weight:800}.task-meta{text-align:right;font-size:9.5pt}.target-strip{border:1px solid #aeb7c3;background:#f2f5f8;padding:.08in .10in;margin-bottom:.08in}.target-list{display:flex;gap:.12in;flex-wrap:wrap;font-size:8.8pt}.directions{font-size:9.2pt;margin:0 0 .08in}.dok-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.08in;flex:1;min-height:0}.dok{border:1.2px solid #222;border-radius:5px;overflow:hidden}.dok-head{background:#234f73;color:#fff;padding:.07in .08in;font-weight:800;font-size:11pt}.dok-sub{background:#dfeaf3;padding:.045in .08in;font-size:8.2pt;font-weight:800}.dok-body{padding:.08in;font-size:9.5pt;line-height:1.24}.product-bar{border:1px solid #aeb7c3;margin-top:.08in;padding:.07in .09in;font-size:8.8pt}.footer{display:flex;justify-content:space-between;margin-top:.05in;font-size:7.5pt;color:#555}`;

  const GUIDE_CSS_FALLBACK = `@page{size:letter portrait;margin:.55in}*{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;color:#172033;line-height:1.5}.wrap{max-width:980px;margin:auto;padding:22px}.hero{background:#eef3f8;border:1px solid #d5dde8;border-radius:20px;padding:26px 30px}.quick-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.btn{display:inline-flex;padding:11px 16px;border-radius:10px;border:1px solid #9fb4c8;text-decoration:none;font-weight:800}.section{margin:18px 0;border:1px solid #d5dde8;border-radius:14px;padding:18px}.guide-page{max-width:7.4in;margin:auto}.dok-block{border:1px solid #d5dde8;border-radius:10px;padding:12px;margin:10px 0;break-inside:avoid}@media print{.quick-actions{display:none}}`;

  const sourceInput = $("sourceFiles");
  const buildButton = $("buildZip");
  const status = $("buildStatus");
  const productInputs = [...document.querySelectorAll('#productChoices input[type="checkbox"]')];

  sourceInput.addEventListener("change", () => {
    renderFiles(sourceInput.files, $("sourceList"));
    refreshStatus();
  });

  ["taskName", "subjectCourse", "unitTopic", "ican1", "ican2", "ican3", "ican4", "customProduct"].forEach((id) => {
    $(id).addEventListener("input", refreshStatus);
  });
  productInputs.forEach((input) => input.addEventListener("change", refreshStatus));
  buildButton.addEventListener("click", buildRequestZip);
  $("clearForm").addEventListener("click", clearForm);

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

  function getICans() {
    return [1, 2, 3, 4]
      .map((n) => $(`ican${n}`).value.trim())
      .filter(Boolean);
  }

  function getProducts() {
    const checked = productInputs.filter((input) => input.checked).map((input) => input.value);
    const custom = $("customProduct").value.trim();
    if (custom) checked.push(custom);
    return [...new Set(checked)];
  }

  function refreshStatus() {
    const taskName = $("taskName").value.trim();
    const subjectCourse = $("subjectCourse").value.trim();
    const unitTopic = $("unitTopic").value.trim();
    const iCans = getICans();
    const products = getProducts();

    if (!taskName || !subjectCourse || !unitTopic || !iCans.length || !products.length) {
      setStatus("Add the required fields, at least one I Can statement, and at least one product type.", "warn");
      return false;
    }

    setStatus(`Ready: 1 task card, ${iCans.length} I Can statement${iCans.length === 1 ? "" : "s"}, ${products.length} allowed product type${products.length === 1 ? "" : "s"}${sourceInput.files.length ? `, and ${sourceInput.files.length} supporting file${sourceInput.files.length === 1 ? "" : "s"}` : ""}.`, "good");
    return true;
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = `status ${kind}`;
  }

  function clearForm() {
    ["taskName", "subjectCourse", "unitTopic", "teacherName", "gradeLevel", "readingLevel", "timeAvailable", "ican1", "ican2", "ican3", "ican4", "customProduct", "teacherNotes"].forEach((id) => { $(id).value = ""; });
    $("useCase").value = "extension_after_mastery";
    $("workMode").value = "teacher_choice";
    $("researchPolicy").value = "teacher_choice";
    productInputs.forEach((input, index) => { input.checked = index < 8; });
    sourceInput.value = "";
    $("sourceList").innerHTML = "";
    refreshStatus();
  }

  async function buildRequestZip() {
    if (!refreshStatus()) return;

    buildButton.disabled = true;
    setStatus("Packaging request...", "warn");

    try {
      const sourceManifest = [];
      const entries = [];
      const used = new Set();

      for (const file of [...sourceInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), used);
        const path = `sources/${packagedName}`;
        sourceManifest.push({
          original_name: file.name,
          packaged_path: path,
          mime_type: file.type || null,
          size_bytes: file.size
        });
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      const teacherNotes = $("teacherNotes").value.trim();
      const request = {
        schema: REQUEST_SCHEMA,
        tool_version: TOOL_VERSION,
        created_at: new Date().toISOString(),
        generation_contract_version: CONTRACT_VERSION,
        task_card_style_version: TASK_CARD_STYLE_VERSION,
        guide_style_version: GUIDE_STYLE_VERSION,
        teacher: {
          name: valueOrNull("teacherName"),
          subject_course: $("subjectCourse").value.trim(),
          grade_level: valueOrNull("gradeLevel")
        },
        task: {
          name: $("taskName").value.trim(),
          unit_topic: $("unitTopic").value.trim(),
          intended_use: $("useCase").value,
          target_reading_access_level: valueOrNull("readingLevel"),
          time_available: valueOrNull("timeAvailable"),
          work_mode: $("workMode").value,
          research_policy: $("researchPolicy").value
        },
        i_can_statements: getICans(),
        product_choices: {
          allowed: getProducts(),
          rule: "Only these product types may appear on the student task card. The academic evidence standard must remain constant across product formats."
        },
        teacher_notes_present: Boolean(teacherNotes),
        source_files: sourceManifest,
        dok_progression: {
          DOK1: "Recall and Reproduction",
          DOK2: "Skills and Concepts",
          DOK3: "Strategic Thinking",
          DOK4: "Extended Thinking",
          rule: "DOK is cognitive complexity, not difficulty or verb matching. DOK 4 must be genuine extended thinking, not DOK 3 with more work."
        },
        requested_outputs: {
          integrated_task_cards: 1,
          student_task_card_html: "student/task_card.html",
          student_task_card_pdf: "student/task_card.pdf",
          teacher_guide_html: "teacher/teacher_guide.html",
          teacher_guide_pdf: "teacher/teacher_guide.pdf",
          click_me: "CLICK_ME.html",
          qa_record: "data/qa.json",
          request_copy: "data/request.json"
        },
        response_structure: {
          click_me_links: [
            "Student Task Card (PDF)",
            "Student Task Card (HTML)",
            "Teacher Guide / Evidence Guide (PDF)",
            "Teacher Guide / Evidence Guide (HTML)"
          ],
          student_card_page: "letter landscape, one page",
          all_links_relative: true
        }
      };

      const [contractText, taskCss, guideCss] = await Promise.all([
        loadTextFile("TIERED_TASK_GENERATION_CONTRACT.md", CONTRACT_FALLBACK),
        loadTextFile("task_card_styles.css", TASK_CSS_FALLBACK),
        loadTextFile("guide_styles.css", GUIDE_CSS_FALLBACK)
      ]);

      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(buildInstructions(request, teacherNotes)) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No additional teacher directions were provided.") },
        { name: "response_contract/TIERED_TASK_GENERATION_CONTRACT.md", data: enc.encode(contractText) },
        { name: "response_contract/task_card_styles.css", data: enc.encode(taskCss) },
        { name: "response_contract/guide_styles.css", data: enc.encode(guideCss) },
        { name: "response_contract/CONTRACT_VERSION.txt", data: enc.encode(CONTRACT_VERSION + "\n") },
        { name: "response_contract/TASK_CARD_STYLE_VERSION.txt", data: enc.encode(TASK_CARD_STYLE_VERSION + "\n") },
        { name: "response_contract/GUIDE_STYLE_VERSION.txt", data: enc.encode(GUIDE_STYLE_VERSION + "\n") }
      );

      const zipBlob = makeZip(entries);
      const filename = `tiered_task_request_${slug(request.task.name)}_${dateStamp()}.zip`;
      downloadBlob(zipBlob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function valueOrNull(id) {
    const value = $(id).value.trim();
    return value || null;
  }

  function buildInstructions(request, teacherNotes) {
    const sourceLine = request.source_files.length
      ? `${request.source_files.length} supporting source file(s) are included under sources/. Use them when they provide required task context or resources.`
      : "No supporting source files were attached. Build from the teacher inputs without inventing quotations, data, or missing resource details.";
    const readingLine = request.task.target_reading_access_level
      ? `Target reading/access level: ${request.task.target_reading_access_level}. Adjust wording/access only; do NOT reduce the academic target, DOK, or evidence standard.`
      : "No target reading/access level was specified; use clear grade-appropriate teacher/student language based on the supplied context.";

    return `# District Tiered Task Request - Pilot\n\n` +
`## Run this request automatically\n` +
`Build the complete Tiered Task response from this ZIP and return exactly ONE response ZIP. This request package contains the full instructions and contracts; no additional teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.\n\n` +
`Task: ${request.task.name}\n` +
`Subject/course: ${request.teacher.subject_course}\n` +
`Unit/topic: ${request.task.unit_topic}\n` +
`Grade level: ${request.teacher.grade_level || "Not specified"}\n` +
`Intended use: ${request.task.intended_use}\n` +
`${readingLine}\n` +
`Time available: ${request.task.time_available || "Not specified"}\n` +
`Work mode: ${request.task.work_mode}\n` +
`Research policy: ${request.task.research_policy}\n` +
`${sourceLine}\n\n` +
`## I Can statements\n` +
request.i_can_statements.map((text, i) => `${i + 1}. ${text}`).join("\n") + `\n\n` +
`## Allowed student product types - AUTHORITATIVE\n` +
request.product_choices.allowed.map((text) => `- ${text}`).join("\n") + `\n\n` +
`Show only these allowed product types on the student task card. If exactly one is allowed, present it as required rather than as a choice. Keep the same intellectual evidence standard across formats.\n\n` +
`## Teacher directions\n${teacherNotes || "No additional teacher directions were provided."}\n\n` +
`## Required build contract\n` +
`Follow response_contract/TIERED_TASK_GENERATION_CONTRACT.md as an executable contract. In particular:\n` +
`- Create exactly ONE integrated student task card, not one card per I Can statement.\n` +
`- Include exactly DOK 1, DOK 2, DOK 3, and DOK 4 tasks on that one card.\n` +
`- Treat DOK as cognitive complexity rather than difficulty or verb matching.\n` +
`- Make DOK 4 genuine extended thinking, not simply more/harder questions.\n` +
`- Keep reading/access adjustments from lowering academic demand.\n` +
`- Map every task to submitted I Can statement(s) in the Teacher Guide.\n` +
`- If a graph/image/diagram/table/source is required or referenced, include the real resource or use an attached one.\n` +
`- Use rendered MathJax for mathematical notation when needed.\n\n` +
`## Locked styling\n` +
`Copy response_contract/task_card_styles.css exactly to assets/task_card_styles.css and use it for the one-page landscape student card.\n` +
`Copy response_contract/guide_styles.css exactly to assets/guide_styles.css and use it for CLICK_ME.html and the Teacher Guide.\n\n` +
`## Required response ZIP\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n` +
`  task_card_styles.css\n` +
`  guide_styles.css\n` +
`  graphs/        (when needed)\n` +
`  visuals/       (when needed)\n` +
`student/\n` +
`  task_card.html\n` +
`  task_card.pdf\n` +
`teacher/\n` +
`  teacher_guide.html\n` +
`  teacher_guide.pdf\n` +
`data/\n` +
`  request.json\n` +
`  qa.json\n` +
`~~~\n\n` +
`CLICK_ME.html must prominently link to both student-card files and both teacher-guide files using local relative links. Copy this request.json to data/request.json.\n\n` +
`## Student Task Card\n` +
`Fit the complete student card on one readable letter-landscape page. Include task title, subject/course, unit/topic, compact I Can statements, concise directions, the four DOK tasks, allowed product type(s), and student-relevant constraints. Do not put teacher answers/DOK rationales on the student card.\n\n` +
`## Teacher Guide / Evidence Guide\n` +
`Include the exact four student tasks, I Can mapping, why each task is that DOK level, convincing evidence, exemplar reasoning/solutions when appropriate, useful misconceptions/weak evidence, product-neutral evidence expectations, reading/access adjustments, pacing/facilitation notes, resource notes, and any limitation/uncertainty needing teacher review.\n\n` +
`## QA before delivery\n` +
`Create data/qa.json and perform every check listed in the generation contract. PASS is not allowed with multiple task cards, missing DOK levels, a fake DOK 4 task, reduced academic demand from reading simplification, unselected product choices, missing referenced resources, raw TeX, clipped/unreadable card content, placeholder PDFs, broken relative links, mismatched locked CSS, or unresolved failures. Visually inspect the HTML/PDF outputs before delivery.\n\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.\n`;
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

  function safeFileName(name) {
    const cleaned = String(name || "file")
      .replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_")
      .replace(/^\.+/, "")
      .trim();
    return cleaned || "file";
  }

  function uniqueName(name, used) {
    let candidate = name;
    let n = 2;
    while (used.has(candidate.toLowerCase())) {
      const dot = name.lastIndexOf(".");
      candidate = dot > 0 ? `${name.slice(0, dot)}_${n}${name.slice(dot)}` : `${name}_${n}`;
      n += 1;
    }
    used.add(candidate.toLowerCase());
    return candidate;
  }

  function slug(value) {
    return String(value || "request")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 48) || "request";
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
