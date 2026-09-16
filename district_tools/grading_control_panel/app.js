(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.0";
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
`;

  const evidenceInput = $("evidenceFiles");
  const rosterInput = $("rosterFiles");
  const rubricInput = $("rubricFiles");
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
  rubricInput.addEventListener("change", () => renderFiles(rubricInput.files, $("rubricList")));
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
    const rosterNote = rosterInput.files.length ? ` Roster included (${rosterInput.files.length} file${rosterInput.files.length === 1 ? "" : "s"}).` : "";
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
        schema: "district-grading-request/0.3-pilot",
        response_style_version: RESPONSE_STYLE_VERSION,
        created_at: createdAt,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: { name: assignmentName },
        scoring_policy: rubricManifest.length
          ? "Use the provided rubric/scoring guide when it clearly applies. Show evidence for scores and flag uncertainty."
          : "Do not invent a numeric grade. Provide evidence-based feedback and mastery/next-step indicators only.",
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
        click_me_no_duplicate_quick_actions: true
      };

      const responseCss = await loadResponseCss();
      const requestInstructions = buildInstructions(request, teacherNotes);
      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No teacher notes were provided.") },
        { name: "response_contract/styles.css", data: enc.encode(responseCss) },
        { name: "response_contract/STYLE_VERSION.txt", data: enc.encode(RESPONSE_STYLE_VERSION + "\n") }
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
      ? "A rubric/scoring guide is included. Use it only where it clearly applies to the submitted evidence."
      : "No rubric/scoring guide is included. Do NOT invent a numeric grade or point scale.";
    const rosterLine = request.roster_files.length
      ? "A roster is included. Use it only to resolve student names, identify missing/unmatched evidence, and preserve roster order. Do not infer achievement from the roster."
      : "No roster is included. Resolve names only from the submitted evidence and filenames; flag uncertainty rather than guessing.";
    const scannedPath = request.requested_outputs.scanned_student_work_pdf;

    return `# District Grading & Evidence Request - Pilot

## Task
Analyze the student evidence in this ZIP and return exactly ONE response ZIP. This packaged request is the complete build contract; no additional teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.

Class / group: ${request.teacher.class_or_group}
Assignment / evidence set: ${request.assignment.name}
Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when the evidence makes it reasonably clear."}
${rubricLine}
${rosterLine}

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

## Scoring and feedback policy
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
- Combined printable documents: page-break between students.

## Required response ZIP structure
~~~text
CLICK_ME.html
assets/
  styles.css
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
  request.json
~~~

All links must be relative and work when the ZIP is unzipped and opened locally with no web server. PDFs must be finished printable files, not placeholders.

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
Keep the current concise report format: student name/label and assignment; demonstrated strengths; the most important misconception/gap/revision need; specific evidence references when feasible; rubric criterion results only when supported; 1-3 concrete next steps; and an uncertainty note when needed. Do not include other students' names or performance.

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
