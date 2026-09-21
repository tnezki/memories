(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const REQUEST_SCHEMA = "district-resource-builder-request/0.5-pilot";
  const TOOL_VERSION = "district-resource-builder/0.5-pilot";
  const CONTRACT_VERSION = "district-resource-builder/0.4-pilot";
  const SHARED_STANDARD_VERSION = "district-response-build-standard/1.1";
  const EXECUTION_VERSION = "district-resource-build-execution/1.0";
  const PREFLIGHT_VERSION = "district-resource-preflight/1.0";
  const FINALIZE_VERSION = "district-resource-finalize/1.0";
  const QA_VERSION = "district-resource-mechanical-qa/1.0";
  const GRAPH_RENDERING_STANDARD_VERSION = "district-graph-rendering-standard/1.2";
  const DASHBOARD_STYLE_VERSION = "district-resource-dashboard-style/0.1-pilot";
  const RESOURCE_STYLE_VERSION = "district-resource-print-style/0.1-pilot";
  const DELIVERY_LINE = "Unzip it and open **`CLICK_ME.html`**. The package includes the finished classroom resource, any requested teacher materials, and completed QA.";

  let profiles = [];
  let currentProfile = null;
  const sourceInput = $("sourceFiles");
  const status = $("buildStatus");
  const buildButton = $("buildZip");

  init();

  async function init() {
    bindCommonEvents();
    try {
      const response = await fetch("resource_profiles.json?v=20260920d", { cache: "no-store" });
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

  function bindCommonEvents() {
    ["resourceName","teacherName","subjectCourse","gradeLevel","learningTargets","timeLength","readingLevel","context","standards","teacherNotes"].forEach((id) => $(id).addEventListener("input", refreshStatus));
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

  function parseLearningTargets(value) {
    const seen = new Set();
    return String(value || "")
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

  function getTargets() {
    return parseLearningTargets($("learningTargets").value);
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
    if (profileId === "worksheet_practice") return {primary:["resource/worksheet.html","resource/worksheet.pdf"],teacher:options.answer_key ? ["teacher/answer_key.html","teacher/answer_key.pdf"] : [],required_files:[]};
    if (profileId === "differentiated_worksheet") {
      const count = Number(options.version_count || 2); const primary=[];
      ["a","b","c"].slice(0,count).forEach((v) => primary.push(`resource/version_${v}.html`,`resource/version_${v}.pdf`));
      const teacher=["teacher/differentiation_notes.html","teacher/differentiation_notes.pdf"];
      if (options.answer_key) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary,teacher,required_files:[]};
    }
    if (profileId === "extension_activity") return {primary:["resource/extension_activity.html","resource/extension_activity.pdf"],teacher:options.teacher_guide ? ["teacher/teacher_guide.html","teacher/teacher_guide.pdf"] : [],required_files:[]};
    if (profileId === "formative_assessment") {
      const teacher=[]; if (options.answer_key || options.misconception_notes) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary:["resource/formative_assessment.html","resource/formative_assessment.pdf"],teacher,required_files:[]};
    }
    if (profileId === "rubric") return {primary:["resource/rubric.html","resource/rubric.pdf"],teacher:[],required_files:[]};
    if (profileId === "lesson_outline") return {primary:["resource/lesson_outline.html","resource/lesson_outline.pdf"],teacher:[],required_files:[]};
    if (profileId === "presentation") {
      const primary=["resource/presentation.pptx","resource/presentation.pdf"];
      if (options.student_handout) primary.push("resource/student_handout.html","resource/student_handout.pdf");
      const teacher=options.speaker_notes ? ["teacher/speaker_notes.html","teacher/speaker_notes.pdf"] : [];
      return {primary,teacher,required_files:[]};
    }
    if (profileId === "stations") {
      const teacher=["teacher/station_guide.html","teacher/station_guide.pdf"];
      if (options.answer_key) teacher.push("teacher/answer_key.html","teacher/answer_key.pdf");
      return {primary:["resource/stations.html","resource/stations.pdf"],teacher,required_files:[]};
    }
    if (profileId === "unit_outline") return {primary:["resource/unit_outline.html","resource/unit_outline.pdf"],teacher:[],required_files:[]};
    if (profileId === "blooket_review") return {primary:["resource/blooket_import.csv"],teacher:["teacher/answer_key.html","teacher/answer_key.pdf"],required_files:[]};
    if (profileId === "custom_resource") {
      const fmt=options.output_format || "best_fit"; let primary=["resource/custom_resource.html","resource/custom_resource.pdf"];
      if (fmt === "docx") primary=["resource/custom_resource.docx"];
      if (fmt === "pptx") primary=["resource/custom_resource.pptx"];
      if (fmt === "csv") primary=["resource/custom_resource.csv"];
      if (fmt === "best_fit") primary=["resource/custom_resource.*"];
      const teacher=options.teacher_support ? ["teacher/teacher_guide.html","teacher/teacher_guide.pdf"] : [];
      return {primary,teacher,required_files:[]};
    }
    return {primary:[],teacher:[],required_files:[]};
  }

  function refreshStatus() {
    if (!currentProfile) return false;
    const missing=[];
    if (!$("resourceName").value.trim()) missing.push("resource name");
    if (!$("subjectCourse").value.trim()) missing.push("subject/course");
    if (!$("gradeLevel").value.trim()) missing.push("grade level");
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
      const entries=[]; const sourceManifest=[]; const used=new Set();
      for (const file of [...sourceInput.files]) {
        const name=uniqueName(safeFileName(file.name),used); const path=`sources/${name}`;
        sourceManifest.push({original_name:file.name,packaged_path:path,mime_type:file.type || null,size_bytes:file.size});
        entries.push({name:path,data:new Uint8Array(await file.arrayBuffer())});
      }

      const profileOptions=getProfileOptions();
      const outputs=resolveOutputs(currentProfile.id,profileOptions);
      outputs.required_files=["CLICK_ME.html","assets/dashboard_styles.css","assets/resource_styles.css","data/request.json","data/qa.json",...outputs.primary,...outputs.teacher];

      const [contractText,sharedText,executionText,dashboardCss,resourceCss,preflightPy,finalizePy,qaPy,graphStandard,manifestText] = await Promise.all([
        loadText("RESOURCE_BUILDER_CONTRACT.md?v=20260920d"),
        loadText("DISTRICT_RESPONSE_BUILD_STANDARD.md?v=20260920d"),
        loadText("RESOURCE_BUILD_EXECUTION.md?v=20260920d"),
        loadText("dashboard_styles.css?v=20260920d"),
        loadText("resource_styles.css?v=20260920d"),
        loadText("resource_preflight.py?v=20260920d"),
        loadText("resource_finalize.py?v=20260920d"),
        loadText("resource_qa.py?v=20260920d"),
        loadText("DISTRICT_GRAPH_RENDERING_STANDARD.md?v=20260920d"),
        loadText("../../Tools/MANIFEST.json?v=20260920d")
      ]);
      let graphManifest; try { graphManifest=JSON.parse(manifestText); } catch { throw new Error("Tools/MANIFEST.json is not valid JSON."); }
      const graphEntrypoint=graphManifest?.tools?.graph_tool;
      if (!graphEntrypoint) throw new Error("Tools/MANIFEST.json does not declare tools.graph_tool.");
      const graphTool=await loadText(`../../${graphEntrypoint}?v=20260920d`);

      const [dashboardHash,resourceHash,preflightHash,finalizeHash,qaHash,graphHash] = await Promise.all([
        sha256Hex(dashboardCss),sha256Hex(resourceCss),sha256Hex(preflightPy),sha256Hex(finalizePy),sha256Hex(qaPy),sha256Hex(graphTool)
      ]);

      const request={
        schema:REQUEST_SCHEMA,
        tool_version:TOOL_VERSION,
        created_at:new Date().toISOString(),
        contracts:{resource_builder:CONTRACT_VERSION,shared_standard:SHARED_STANDARD_VERSION,execution:EXECUTION_VERSION,graph_rendering:GRAPH_RENDERING_STANDARD_VERSION},
        resource:{name:$("resourceName").value.trim(),profile_id:currentProfile.id,profile_label:currentProfile.label},
        teacher:{name:valueOrNull("teacherName"),subject_course:$("subjectCourse").value.trim(),grade_level:$("gradeLevel").value.trim()},
        learning_targets:getTargets(),
        context:valueOrNull("context"),
        standards_framework:valueOrNull("standards"),
        time_length_constraint:valueOrNull("timeLength"),
        target_reading_access_level:valueOrNull("readingLevel"),
        design_priorities:getPriorities(),
        profile_options:profileOptions,
        profile_snapshot:currentProfile,
        teacher_notes:valueOrNull("teacherNotes"),
        source_files:sourceManifest,
        resolved_outputs:outputs,
        locked_styles:{
          dashboard:{version:DASHBOARD_STYLE_VERSION,request_path:"response_contract/dashboard_styles.css",response_path:"assets/dashboard_styles.css",sha256:dashboardHash},
          resource:{version:RESOURCE_STYLE_VERSION,request_path:"response_contract/resource_styles.css",response_path:"assets/resource_styles.css",sha256:resourceHash}
        },
        deterministic_tools:{
          preflight:{version:PREFLIGHT_VERSION,path:"response_contract/resource_preflight.py",sha256:preflightHash},
          finalize:{version:FINALIZE_VERSION,path:"response_contract/resource_finalize.py",sha256:finalizeHash},
          qa:{version:QA_VERSION,path:"response_contract/resource_qa.py",sha256:qaHash}
        },
        graph_rendering:{standard_version:GRAPH_RENDERING_STANDARD_VERSION,manifest:"response_contract/graph_tool/MANIFEST.json",entrypoint:graphEntrypoint,packaged_entrypoint:`response_contract/graph_tool/${graphEntrypoint.split("/").pop()}`,sha256:graphHash},
        baseline_requirements:{accuracy:true,clarity:true,accessibility:true,grade_appropriate:true,design_priorities_are_optional_emphasis:true},
        authority_note:"Structured resource/profile choices, grade level, and learning targets outrank conflicting free-form notes. Advanced design priorities are optional emphasis only.",
        delivery:{required_final_line:DELIVERY_LINE}
      };

      entries.unshift(
        {name:"REQUEST_READ_ME_FIRST.md",data:enc.encode(buildInstructions(request))},
        {name:"request.json",data:enc.encode(JSON.stringify(request,null,2))},
        {name:"response_contract/RESOURCE_BUILDER_CONTRACT.md",data:enc.encode(contractText)},
        {name:"response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md",data:enc.encode(sharedText)},
        {name:"response_contract/RESOURCE_BUILD_EXECUTION.md",data:enc.encode(executionText)},
        {name:"response_contract/SELECTED_PROFILE.json",data:enc.encode(JSON.stringify(currentProfile,null,2))},
        {name:"response_contract/dashboard_styles.css",data:enc.encode(dashboardCss)},
        {name:"response_contract/resource_styles.css",data:enc.encode(resourceCss)},
        {name:"response_contract/resource_preflight.py",data:enc.encode(preflightPy)},
        {name:"response_contract/resource_finalize.py",data:enc.encode(finalizePy)},
        {name:"response_contract/resource_qa.py",data:enc.encode(qaPy)},
        {name:"response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md",data:enc.encode(graphStandard)},
        {name:"response_contract/graph_tool/MANIFEST.json",data:enc.encode(manifestText)},
        {name:`response_contract/graph_tool/${graphEntrypoint.split("/").pop()}`,data:enc.encode(graphTool)},
        {name:"response_contract/CONTRACT_VERSION.txt",data:enc.encode(CONTRACT_VERSION+"\n")},
        {name:"response_contract/SHARED_STANDARD_VERSION.txt",data:enc.encode(SHARED_STANDARD_VERSION+"\n")},
        {name:"response_contract/EXECUTION_VERSION.txt",data:enc.encode(EXECUTION_VERSION+"\n")},
        {name:"response_contract/DASHBOARD_STYLE_SHA256.txt",data:enc.encode(dashboardHash+"\n")},
        {name:"response_contract/RESOURCE_STYLE_SHA256.txt",data:enc.encode(resourceHash+"\n")}
      );

      const blob=makeZip(entries);
      const filename=`resource_builder_request_${slug(request.resource.name)}_${dateStamp()}.zip`;
      downloadBlob(blob,filename);
      setStatus(`Request ready: ${filename}`,"good");
    } catch (error) {
      console.error(error); setStatus(`Could not build the ZIP: ${error.message || error}`,"bad");
    } finally { buildButton.disabled=false; }
  }

  function buildInstructions(request) {
    const targets=request.learning_targets.map((t,i)=>`${i+1}. ${t}`).join("\n");
    const priorities=request.design_priorities.length ? request.design_priorities.join(", ") : "None selected. Use the baseline contract without extra emphasis.";
    const sources=request.source_files.length ? `${request.source_files.length} source file(s) are included under sources/. Treat all listed files as available supporting sources.` : "No source files were attached.";
    return `# District Resource Builder Request - Deterministic Pilot\n\n## Run automatically\nBuild the complete classroom resource from this request ZIP and return exactly ONE response ZIP. No additional teacher prompt is required.\n\nResource: ${request.resource.name}\nType: ${request.resource.profile_label}\nSubject/course: ${request.teacher.subject_course}\nGrade level: ${request.teacher.grade_level}\nTime/length: ${request.time_length_constraint || "Not specified"}\nReading/access level: ${request.target_reading_access_level || "Not specified"}\nStandards/framework: ${request.standards_framework || "Not specified"}\nOptional design emphasis: ${priorities}\n${sources}\n\n## Learning targets\n${targets}\n\n## Grade-level interpretation - HARD\nUse the explicit grade level together with the learning target(s) to determine appropriate rigor, representations, number choices, vocabulary, directions, reading load, expected reasoning, and scaffolding. Do not infer rigor from the I Can wording alone.\n\n## Context\n${request.context || "No additional context provided."}\n\n## Structured profile options\n\n\`\`\`json\n${JSON.stringify(request.profile_options,null,2)}\n\`\`\`\n\n## Teacher notes\n${request.teacher_notes || "No additional teacher notes provided."}\n\n## Required execution order\n1. Run \`python response_contract/resource_preflight.py --request-root . --out work/resource_preflight.json\`. If it fails, stop and report the packaging error; do not search GitHub/web for missing core dependencies.\n2. Read the teacher request and supporting source files. ChatGPT owns instructional judgment and the small amount of new content.\n3. Create required graphs with the packaged canonical graph tool and follow response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md. Reuse graph assets rather than redrawing the same graph.\n4. Build the profile outputs from the locked CSS and profile contract. Do not invent a new visual system.\n5. Run \`python response_contract/resource_finalize.py --request-root . --response RESPONSE\` to copy locked assets, copy request metadata, and generate the deterministic CLICK_ME.html dashboard.\n6. Run \`python response_contract/resource_qa.py --request-root . --response RESPONSE --out RESPONSE/data/mechanical_qa.json\`. Fix only reported failures; do not rerun unrelated work.\n7. Complete bounded content/visual QA and write RESPONSE/data/qa.json. Mechanical checks are not repeated manually.\n8. Zip RESPONSE and return that one response ZIP.\n\n## Required contracts\nFollow response_contract/RESOURCE_BUILDER_CONTRACT.md, response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md, response_contract/RESOURCE_BUILD_EXECUTION.md, the selected profile snapshot, and the district graph rendering standard. Structured selections in request.json are authoritative over conflicting free-form notes.\n\n## Required output files\n${request.resolved_outputs.required_files.map((p)=>`- ${p}`).join("\n")}\n\nFor custom_resource with a wildcard primary output, resolve the wildcard to the practical file extension required by the selected/best-fit format and record the choice in data/qa.json.\n\nReturn only the completed response ZIP. The final user-facing line must be exactly:\n\n${request.delivery.required_final_line}\n`;
  }

  function clearForm() {
    ["resourceName","teacherName","subjectCourse","gradeLevel","learningTargets","timeLength","readingLevel","context","standards","teacherNotes"].forEach((id)=>$(id).value="");
    sourceInput.value=""; $("sourceList").innerHTML="";
    document.querySelectorAll('#priorityChoices input[type="checkbox"]').forEach((el)=>{el.checked=false;});
    $("advancedOptions").open=false;
    selectProfile(profiles[0].id); refreshStatus();
  }

  function renderFiles(files,target){target.innerHTML="";[...files].forEach((file)=>{const li=document.createElement("li");li.textContent=`${file.name} (${formatBytes(file.size)})`;target.appendChild(li);});}
  function formatBytes(bytes){if(bytes<1024)return `${bytes} B`;if(bytes<1024*1024)return `${(bytes/1024).toFixed(1)} KB`;return `${(bytes/(1024*1024)).toFixed(1)} MB`;}
  function setStatus(message,kind){status.textContent=message;status.className=`status ${kind}`;}
  function valueOrNull(id){const v=$(id).value.trim();return v||null;}
  async function loadText(path){const response=await fetch(path,{cache:"no-store"});if(!response.ok)throw new Error(`Could not load required packaged dependency ${path} (HTTP ${response.status})`);return await response.text();}
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
