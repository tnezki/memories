(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const evidenceInput = $("evidenceFiles");
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
    setStatus(`Ready to package ${count} evidence file${count === 1 ? "" : "s"}.`, "good");
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
    rubricInput.value = "";
    notesInput.value = "";
    $("evidenceList").innerHTML = "";
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
      const rubricManifest = [];
      const entries = [];

      for (const file of [...evidenceInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "evidence");
        const path = `evidence/${packagedName}`;
        evidenceManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      for (const file of [...rubricInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "rubric");
        const path = `rubric/${packagedName}`;
        rubricManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      const request = {
        schema: "district-grading-request/0.2-pilot",
        created_at: createdAt,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: {
          name: assignmentName
        },
        scoring_policy: rubricManifest.length
          ? "Use the provided rubric/scoring guide when it clearly applies. Show evidence for scores and flag uncertainty."
          : "Do not invent a numeric grade. Provide evidence-based feedback and mastery/next-step indicators only.",
        teacher_notes_present: Boolean(teacherNotes),
        evidence_files: evidenceManifest,
        rubric_files: rubricManifest,
        requested_outputs: {
          student_reports: true,
          combined_student_reports_pdf: true,
          class_analysis: true,
          recommended_groupings: true,
          common_print_packet: "One class-wide review/extension packet based on the most important common patterns",
          individualized_print_packets: "Student-specific review/extension practice based on each student's evidence"
        }
      };

      const requestInstructions = buildInstructions(request, teacherNotes);
      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No teacher notes were provided.") }
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

  function fileManifest(file, packagedPath) {
    return {
      original_name: file.name,
      packaged_path: packagedPath,
      mime_type: file.type || null,
      size_bytes: file.size
    };
  }

  function buildInstructions(request, teacherNotes) {
    const rubricLine = request.rubric_files.length
      ? "A rubric/scoring guide is included. Use it only where it clearly applies to the submitted evidence."
      : "No rubric/scoring guide is included. Do NOT invent a numeric grade or point scale.";

    return `# District Grading & Evidence Request - Pilot\n\n` +
`## Your task\n` +
`Analyze the student evidence in this ZIP and return exactly ONE response ZIP. Begin from this packaged request; no additional teacher prompt is required to define the task. The teacher should only need to unzip the response and open \`CLICK_ME.html\`. Do not return a collection of loose files as the primary deliverable.\n\n` +
`Class / group: ${request.teacher.class_or_group}\n` +
`Assignment / evidence set: ${request.assignment.name}\n` +
`Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when the evidence makes it reasonably clear."}\n` +
`${rubricLine}\n\n` +
`Teacher notes:\n${teacherNotes || "No additional notes provided."}\n\n` +
`## Evidence rules\n` +
`- Judge student work from the supplied evidence, rubric (if present), and teacher notes.\n` +
`- Do not research students or use outside personal information.\n` +
`- Do not rely on prior chats, memories, or prior student records unless they are included in this request ZIP.\n` +
`- Do not use public web research to decide whether student work is correct. General subject-matter knowledge may be used to interpret the evidence and create practice.\n` +
`- Do not silently guess when a student identity, response, rubric match, or piece of handwriting is unclear. Flag uncertainty.\n` +
`- If some files cannot be read, process the readable evidence and clearly list the unreadable/ambiguous files.\n` +
`- If one file contains work from multiple students, separate students only when names/labels are reasonably clear. Otherwise use neutral labels such as Student 01 and flag the mapping issue.\n\n` +
`## Scoring / feedback policy\n` +
`- ${request.scoring_policy}\n` +
`- Evidence comments should distinguish demonstrated strengths from next steps.\n` +
`- Do not rank students against one another.\n` +
`- Make student-facing language age-appropriate when the grade level can be determined.\n` +
`- Treat any AI-produced score or classification as a teacher-review recommendation, not an irreversible final grade.\n\n` +
`## Required response ZIP structure\n\n` +
`\`\`\`text\n` +
`CLICK_ME.html\n` +
`assets/\n` +
`  styles.css\n` +
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
`    <one print-friendly HTML practice packet per identified student>\n` +
`  individualized_packets.pdf\n` +
`data/\n` +
`  analysis.json\n` +
`  request.json\n` +
`\`\`\`\n\n` +
`All HTML links must be relative and work when the ZIP is unzipped and opened locally with no web server. Use static HTML/CSS with no external CDN dependencies. PDFs must be generated as finished printable files, not placeholders.\n\n` +
`## CLICK_ME.html\n` +
`Create a simple teacher dashboard with three obvious areas:\n` +
`1. **Individual Student Reports** - clear links/cards for every identified student, plus an obvious **Print All Student Reports** link/button to \`print/all_student_reports.pdf\`.\n` +
`2. **Class Data** - a link to the class overview and a short summary of the biggest patterns.\n` +
`3. **Print Options** - simple print choices for class-wide and individualized follow-up:\n` +
`   - **Common Class Review + Extension** - one general packet based on the most important shared mistakes/unfinished understandings, with 1-2 extension opportunities when evidence supports them.\n` +
`   - **Individualized Practice** - student-specific practice packets matched to each student's evidence, with extension instead of remediation when appropriate.\n\n` +
`The teacher should not need to open the data folder. Make the print links prominent and understandable without technical knowledge.\n\n` +
`## Individual student reports\n` +
`Keep the individual report format concise, printable, and grounded in that student's evidence. Include:\n` +
`- student name/label and assignment;\n` +
`- what the student demonstrated successfully;\n` +
`- the most important misconception(s), gap(s), or revision need(s);\n` +
`- specific evidence references when feasible (question/task/criterion);\n` +
`- rubric criterion results/scores only when a provided rubric supports them;\n` +
`- 1-3 concrete next steps;\n` +
`- an uncertainty note when the evidence is incomplete or ambiguous.\n\n` +
`Do not include other students' names or performance in an individual student's report.\n\n` +
`Also create \`print/all_student_reports.html\` and \`print/all_student_reports.pdf\` containing every student's report in roster/identified order, with a clear page break between students. Preserve the same report content rather than creating a shortened second version.\n\n` +
`## Class analysis\n` +
`Create \`class/class_overview.html\` for the teacher. Include:\n` +
`- number of student evidence sets successfully analyzed;\n` +
`- strengths demonstrated by much of the class;\n` +
`- the most instructionally important common mistakes/misconceptions;\n` +
`- counts (and percentages when the denominator is reliable) for major patterns;\n` +
`- students who appear to share each instructional need;\n` +
`- students who appear ready for extension;\n` +
`- any evidence-quality or identification problems that limit conclusions.\n\n` +
`Groupings are instructional recommendations, not permanent labels.\n\n` +
`## Print option 1 - Common Class Review + Extension\n` +
`Create one general/common packet driven by actual class patterns, not a generic worksheet. It should:\n` +
`- target the 1-3 most instructionally useful common mistakes or unfinished understandings;\n` +
`- include concise reteach/support directions or examples when useful;\n` +
`- include practice that directly addresses those patterns;\n` +
`- include 1-2 clearly labeled extension opportunities when class evidence supports them;\n` +
`- avoid student names;\n` +
`- be usable as a whole-class handout, small-group task, or station-style activity at the teacher's discretion;\n` +
`- be age-appropriate and, for early elementary, favor concise teacher-led/hands-on directions over text-heavy worksheets.\n\n` +
`Provide both \`print/common_review_extension_packet.html\` and \`print/common_review_extension_packet.pdf\`.\n\n` +
`## Print option 2 - Individualized Practice\n` +
`Create one student-specific practice packet for every identified student. Each packet should:\n` +
`- use the student's name/label clearly at the top;\n` +
`- target that student's most important next step(s) from the submitted evidence;\n` +
`- avoid unnecessary practice on skills already demonstrated securely;\n` +
`- provide extension/transfer work instead of remediation when the student is ready;\n` +
`- contain enough context to be usable without showing the original analysis report;\n` +
`- never mention or compare the student to classmates.\n\n` +
`Save the individual HTML packets in \`print/individualized/\`. Also create \`print/individualized_packets.pdf\` containing all individualized packets with a clear page break between students so the teacher can print the full class set at once and distribute pages by student.\n\n` +
`## data/analysis.json\n` +
`Store the structured analysis that supports the HTML pages and print materials. Include student identifiers/labels, evidence-file mapping, rubric results when applicable, strengths, needs, class pattern counts, grouping recommendations, common-packet targets, individualized-practice targets, and uncertainty flags. Copy this request's \`request.json\` into \`data/request.json\`.\n\n` +
`## Final delivery\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open \`CLICK_ME.html\`.\n`;
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
