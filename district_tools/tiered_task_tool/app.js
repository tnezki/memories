(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const REQUEST_SCHEMA = "district-tiered-task-request/0.4-pilot";
  const TOOL_VERSION = "district-tiered-task-tool/0.4-pilot";
  const CONTRACT_VERSION = "district-tiered-task-generation/0.4-pilot";
  const SHARED_STANDARD_VERSION = "district-response-build-standard/1.1";
  const EXECUTION_VERSION = "district-tiered-task-build-execution/1.1";
  const PREFLIGHT_VERSION = "district-tiered-task-preflight/1.1";
  const FINALIZE_VERSION = "district-tiered-task-finalize/1.0";
  const QA_VERSION = "district-tiered-task-mechanical-qa/1.0";
  const GRAPH_RENDERING_STANDARD_VERSION = "district-graph-rendering-standard/1.2";
  const LAYOUT_LOCK_VERSION = "district-tiered-task-layout-lock/1.0";
  const TASK_CARD_STYLE_VERSION = "district-tiered-task-card-style/0.2-pilot";
  const GUIDE_STYLE_VERSION = "district-tiered-task-guide-style/0.2-pilot";
  const REQUIRED_DELIVERY_LINE = "Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.";

  const sourceInput = $("sourceFiles");
  const buildButton = $("buildZip");
  const status = $("buildStatus");
  const productInputs = [...document.querySelectorAll('#productChoices input[type="checkbox"]')];

  sourceInput.addEventListener("change", () => { renderFiles(sourceInput.files, $("sourceList")); refreshStatus(); });
  ["taskName","subjectCourse","gradeLevel","icanStatements","customProduct","readingLevel","timeAvailable","teacherNotes","teacherName"].forEach((id) => {
    $(id).addEventListener("input", refreshStatus);
  });
  productInputs.forEach((input) => input.addEventListener("change", refreshStatus));
  buildButton.addEventListener("click", buildRequestZip);
  $("clearForm").addEventListener("click", clearForm);
  refreshStatus();

  function getICans() {
    const seen = new Set();
    return String($("icanStatements").value || "")
      .split(/\r?\n/)
      .map((line) => line.trim().replace(/^(?:[-*•▪◦‣]+|\d+[.)])\s*/, "").trim())
      .filter(Boolean)
      .filter((target) => {
        const key = target.toLowerCase();
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
  }

  function getProducts() {
    const products = productInputs.filter((input) => input.checked).map((input) => input.value);
    const custom = $("customProduct").value.trim();
    if (custom) products.push(custom);
    return [...new Set(products)];
  }

  function refreshStatus() {
    const missing = [];
    if (!$("taskName").value.trim()) missing.push("task name");
    if (!$("subjectCourse").value.trim()) missing.push("subject/course");
    if (!$("gradeLevel").value.trim()) missing.push("grade level");
    if (!getICans().length) missing.push("at least one I Can statement");
    if (!getProducts().length) missing.push("at least one allowed product");
    if (missing.length) {
      setStatus(`Add ${missing.join(", ")}.`, "warn");
      return false;
    }
    setStatus(`Ready: 1 task card, ${getICans().length} I Can statement${getICans().length === 1 ? "" : "s"}, ${getProducts().length} allowed product type${getProducts().length === 1 ? "" : "s"}${sourceInput.files.length ? `, and ${sourceInput.files.length} supporting file${sourceInput.files.length === 1 ? "" : "s"}` : ""}.`, "good");
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
        sourceManifest.push({original_name:file.name, packaged_path:path, mime_type:file.type || null, size_bytes:file.size});
        entries.push({name:path, data:new Uint8Array(await file.arrayBuffer())});
      }

      const [contractText, sharedText, executionText, layoutLockText, taskCss, guideCss, preflightPy, finalizePy, qaPy, graphStandard, manifestText] = await Promise.all([
        loadText("TIERED_TASK_GENERATION_CONTRACT.md?v=20260920d"),
        loadText("DISTRICT_RESPONSE_BUILD_STANDARD.md?v=20260920d"),
        loadText("TIERED_TASK_BUILD_EXECUTION.md?v=20260920d"),
        loadText("TIERED_TASK_LAYOUT_LOCK.md?v=20260920d"),
        loadText("task_card_styles.css?v=20260920d"),
        loadText("guide_styles.css?v=20260920d"),
        loadText("tiered_task_preflight.py?v=20260920d"),
        loadText("tiered_task_finalize.py?v=20260920d"),
        loadText("tiered_task_qa.py?v=20260920d"),
        loadText("DISTRICT_GRAPH_RENDERING_STANDARD.md?v=20260920d"),
        loadText("../../Tools/MANIFEST.json?v=20260920d")
      ]);
      let graphManifest;
      try { graphManifest = JSON.parse(manifestText); } catch { throw new Error("Tools/MANIFEST.json is not valid JSON."); }
      const graphEntrypoint = graphManifest?.tools?.graph_tool;
      if (!graphEntrypoint) throw new Error("Tools/MANIFEST.json does not declare tools.graph_tool.");
      const graphTool = await loadText(`../../${graphEntrypoint}?v=20260920d`);

      const [layoutLockHash, taskHash, guideHash, preflightHash, finalizeHash, qaHash, graphHash] = await Promise.all([
        sha256Hex(layoutLockText), sha256Hex(taskCss), sha256Hex(guideCss), sha256Hex(preflightPy), sha256Hex(finalizePy), sha256Hex(qaPy), sha256Hex(graphTool)
      ]);

      const request = {
        schema: REQUEST_SCHEMA,
        tool_version: TOOL_VERSION,
        created_at: new Date().toISOString(),
        contracts: {
          tiered_task: CONTRACT_VERSION,
          shared_standard: SHARED_STANDARD_VERSION,
          execution: EXECUTION_VERSION,
          graph_rendering: GRAPH_RENDERING_STANDARD_VERSION,
          layout_lock: LAYOUT_LOCK_VERSION
        },
        teacher: {
          name: valueOrNull("teacherName"),
          subject_course: $("subjectCourse").value.trim(),
          grade_level: $("gradeLevel").value.trim()
        },
        task: {
          name: $("taskName").value.trim(),
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
        teacher_notes: valueOrNull("teacherNotes"),
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
        locked_styles: {
          task_card:{version:TASK_CARD_STYLE_VERSION, request_path:"response_contract/task_card_styles.css", response_path:"assets/task_card_styles.css", sha256:taskHash},
          guide:{version:GUIDE_STYLE_VERSION, request_path:"response_contract/guide_styles.css", response_path:"assets/guide_styles.css", sha256:guideHash}
        },
        layout_lock: {version:LAYOUT_LOCK_VERSION, path:"response_contract/TIERED_TASK_LAYOUT_LOCK.md", sha256:layoutLockHash},
        deterministic_tools: {
          preflight:{version:PREFLIGHT_VERSION, path:"response_contract/tiered_task_preflight.py", sha256:preflightHash},
          finalize:{version:FINALIZE_VERSION, path:"response_contract/tiered_task_finalize.py", sha256:finalizeHash},
          qa:{version:QA_VERSION, path:"response_contract/tiered_task_qa.py", sha256:qaHash}
        },
        graph_rendering: {
          standard_version: GRAPH_RENDERING_STANDARD_VERSION,
          manifest: "response_contract/graph_tool/MANIFEST.json",
          entrypoint: graphEntrypoint,
          packaged_entrypoint: `response_contract/graph_tool/${graphEntrypoint.split("/").pop()}`,
          sha256: graphHash
        },
        baseline_requirements: {
          accuracy:true,
          accessibility:true,
          grade_appropriate:true,
          one_integrated_card:true,
          broad_product_choice_is_default:true
        },
        delivery: { required_final_line: REQUIRED_DELIVERY_LINE }
      };

      entries.unshift(
        {name:"REQUEST_READ_ME_FIRST.md", data:enc.encode(buildInstructions(request))},
        {name:"request.json", data:enc.encode(JSON.stringify(request,null,2))},
        {name:"response_contract/TIERED_TASK_GENERATION_CONTRACT.md", data:enc.encode(contractText)},
        {name:"response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md", data:enc.encode(sharedText)},
        {name:"response_contract/TIERED_TASK_BUILD_EXECUTION.md", data:enc.encode(executionText)},
        {name:"response_contract/TIERED_TASK_LAYOUT_LOCK.md", data:enc.encode(layoutLockText)},
        {name:"response_contract/task_card_styles.css", data:enc.encode(taskCss)},
        {name:"response_contract/guide_styles.css", data:enc.encode(guideCss)},
        {name:"response_contract/tiered_task_preflight.py", data:enc.encode(preflightPy)},
        {name:"response_contract/tiered_task_finalize.py", data:enc.encode(finalizePy)},
        {name:"response_contract/tiered_task_qa.py", data:enc.encode(qaPy)},
        {name:"response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md", data:enc.encode(graphStandard)},
        {name:"response_contract/graph_tool/MANIFEST.json", data:enc.encode(manifestText)},
        {name:`response_contract/graph_tool/${graphEntrypoint.split("/").pop()}`, data:enc.encode(graphTool)},
        {name:"response_contract/CONTRACT_VERSION.txt", data:enc.encode(CONTRACT_VERSION+"\n")},
        {name:"response_contract/SHARED_STANDARD_VERSION.txt", data:enc.encode(SHARED_STANDARD_VERSION+"\n")},
        {name:"response_contract/EXECUTION_VERSION.txt", data:enc.encode(EXECUTION_VERSION+"\n")},
        {name:"response_contract/LAYOUT_LOCK_SHA256.txt", data:enc.encode(layoutLockHash+"\n")},
        {name:"response_contract/TASK_CARD_STYLE_SHA256.txt", data:enc.encode(taskHash+"\n")},
        {name:"response_contract/GUIDE_STYLE_SHA256.txt", data:enc.encode(guideHash+"\n")}
      );

      const blob = makeZip(entries);
      const filename = `tiered_task_request_${slug(request.task.name)}_${dateStamp()}.zip`;
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
    const targets = request.i_can_statements.map((t,i) => `${i+1}. ${t}`).join("\n");
    const sources = request.source_files.length ? `${request.source_files.length} supporting source file(s) are included under sources/. Treat all listed files as available supporting sources.` : "No supporting source files were attached.";
    return `# District Tiered Task Request - Deterministic Pilot\n\n## Run automatically\nBuild the complete Tiered Task response from this request ZIP and return exactly ONE response ZIP. No additional teacher prompt is required.\n\nTask: ${request.task.name}\nSubject/course: ${request.teacher.subject_course}\nGrade level: ${request.teacher.grade_level}\nIntended use: ${request.task.intended_use}\nTime available: ${request.task.time_available || "Not specified"}\nReading/access level: ${request.task.target_reading_access_level || "Not specified"}\nWork mode: ${request.task.work_mode}\nResearch policy: ${request.task.research_policy}\nAllowed products: ${request.product_choices.allowed.join(", ")}\n${sources}\n\n## Learning targets\n${targets}\n\n## Grade-level interpretation - HARD\nUse the explicit grade level together with the I Can statements to set appropriate rigor, representations, number choices, vocabulary, reading load, expected reasoning, and scaffolding. Do not infer rigor from the wording of an I Can statement alone.\n\n## Teacher directions / constraints\n${request.teacher_notes || "No additional teacher directions were provided."}\n\n## Required execution order\n1. Run \`python response_contract/tiered_task_preflight.py --request-root . --out work/tiered_task_preflight.json\`. If it fails, stop and report the packaging error; do not search GitHub/web for missing core dependencies.\n2. Read the request and relevant supporting source files once. ChatGPT owns instructional judgment, DOK design, and the small amount of new content.\n3. Create one integrated DOK 1-4 card and one matching Teacher Guide. Use the packaged graph tool for supported Cartesian graph work and the graph standard for all graph output.\n4. Create the required HTML/PDF outputs using the locked CSS. Do not invent a new visual system.\n5. Run \`python response_contract/tiered_task_finalize.py --request-root . --response RESPONSE\` to copy locked assets/request metadata and generate CLICK_ME.html.\n6. Run \`python response_contract/tiered_task_qa.py --request-root . --response RESPONSE --out RESPONSE/data/mechanical_qa.json\`. Fix only reported failures; do not restart unrelated content work.\n7. Complete bounded content/visual QA and write RESPONSE/data/qa.json. Mechanical checks are not repeated manually.\n8. Zip RESPONSE and return that one response ZIP.\n\n## Required contracts\nFollow response_contract/TIERED_TASK_GENERATION_CONTRACT.md, response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md, response_contract/TIERED_TASK_BUILD_EXECUTION.md, response_contract/TIERED_TASK_LAYOUT_LOCK.md, and response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md.\n\nReturn only the completed response ZIP. The final user-facing line must be exactly:\n\n${request.delivery.required_final_line}\n`;
  }

  function clearForm() {
    ["taskName","teacherName","subjectCourse","gradeLevel","readingLevel","timeAvailable","icanStatements","customProduct","teacherNotes"].forEach((id) => { $(id).value = ""; });
    $("useCase").value = "extension_after_mastery";
    $("workMode").value = "teacher_choice";
    $("researchPolicy").value = "teacher_choice";
    productInputs.forEach((input, index) => { input.checked = index < 8; });
    sourceInput.value = "";
    $("sourceList").innerHTML = "";
    $("advancedOptions").open = false;
    refreshStatus();
  }

  function renderFiles(files,target){target.innerHTML="";[...files].forEach((file)=>{const li=document.createElement("li");li.textContent=`${file.name} (${formatBytes(file.size)})`;target.appendChild(li);});}
  function formatBytes(bytes){if(bytes<1024)return `${bytes} B`;if(bytes<1024*1024)return `${(bytes/1024).toFixed(1)} KB`;return `${(bytes/(1024*1024)).toFixed(1)} MB`;}
  function setStatus(message,kind){status.textContent=message;status.className=`status ${kind}`;}
  function valueOrNull(id){const v=$(id).value.trim();return v||null;}
  async function loadText(path){const response=await fetch(path,{cache:"no-store"});if(!response.ok)throw new Error(`Could not load required packaged dependency ${path} (HTTP ${response.status})`);return await response.text();}
  async function sha256Hex(value){const digest=await crypto.subtle.digest("SHA-256",enc.encode(String(value)));return [...new Uint8Array(digest)].map((b)=>b.toString(16).padStart(2,"0")).join("");}
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
