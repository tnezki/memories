(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const TOOL_VERSION = "0.4.0-pilot";
  const REQUEST_SCHEMA = "district-math-worksheet-builder-request/0.4";
  const CONTRACT_VERSION = "district-math-worksheet-builder/0.5-pilot";
  const SHARED_STANDARD_VERSION = "district-response-build-standard/1.0";
  const DASHBOARD_STYLE_VERSION = "worksheet-builder-dashboard/0.1";
  const WORKSHEET_STYLE_VERSION = "worksheet-builder-student/0.3";
  const WORKSPACE_DEFAULT_PERCENT = 100;
  const WORKSPACE_RANGE_PERCENT = [0,1200];
  const GRAPH_DEFAULT_PERCENT = 100;
  const GRAPH_RANGE_PERCENT = [70,160];

  let catalog = null;
  const familyState = new Map();
  const familyMeta = new Map();

  function escHtml(value){return String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));}
  function escAttr(value){return escHtml(value);}
  function difficulty(){return document.querySelector('input[name="difficulty"]:checked')?.value || "balanced";}
  function gradeBadge(name){if(name==="Lower Elementary Math")return "LE";const m=name.match(/Grade\s+(\d+)/i);if(m)return m[1];return name.replace(/\s+Math$/i,"").slice(0,3);}

  async function init(){
    bindEvents();
    try{
      const r=await fetch("question_structure_catalog.json",{cache:"no-store"});
      if(!r.ok)throw new Error(`HTTP ${r.status}`);
      catalog=await r.json();
    }catch(error){
      console.error("Catalog fetch failed.",error);
      catalog={courses:[]};
    }
    indexCatalog();
    renderCourseFilters();
    renderFamilies();
    refresh();
  }

  function indexCatalog(){
    familyMeta.clear();
    for(const course of (catalog?.courses||[])){
      for(const topic of (course.topics||[])){
        for(const family of (topic.families||[])){
          const meta={...family,course:course.name,topic_id:topic.id,topic:topic.label};
          familyMeta.set(family.id,meta);
          if(!familyState.has(family.id))familyState.set(family.id,{enabled:false,count:1});
        }
      }
    }
  }

  function renderCourseFilters(){
    const mount=$("courseFilters"); mount.innerHTML="";
    const courses=catalog?.courses||[];
    courses.forEach(course=>{
      const label=document.createElement("label"); label.className="course-chip";
      const checked=course.name==="Grade 5 Math";
      label.innerHTML=`<input type="checkbox" value="${escAttr(course.name)}" ${checked?"checked":""}>${escHtml(course.name)}`;
      mount.appendChild(label);
    });
    mount.querySelectorAll('input[type="checkbox"]').forEach(el=>el.addEventListener("change",()=>{renderFamilies();refresh();}));
  }

  function browseCourses(){return [...$("courseFilters").querySelectorAll('input[type="checkbox"]:checked')].map(x=>x.value);}

  function bindEvents(){
    $("title").addEventListener("input",refresh);
    $("target").addEventListener("input",refresh);
    $("versions").addEventListener("change",refresh);
    document.querySelectorAll('input[name="difficulty"]').forEach(el=>el.addEventListener("change",refresh));
    $("twoColumn").addEventListener("change",refresh);
    $("answerKey").addEventListener("change",refresh);
    $("customEnabled").addEventListener("change",()=>{
      const on=$("customEnabled").checked;
      $("customDescription").disabled=!on;
      $("customCount").disabled=!on;
      $("customMinus").disabled=!on;
      $("customPlus").disabled=!on;
      refresh();
    });
    $("customDescription").addEventListener("input",refresh);
    $("customCount").addEventListener("input",()=>{clampCustom();refresh();});
    $("customMinus").addEventListener("click",()=>setCustomCount(Number($("customCount").value)-1));
    $("customPlus").addEventListener("click",()=>setCustomCount(Number($("customCount").value)+1));
    $("structureSearch").addEventListener("input",renderFamilies);
    $("selectVisible").addEventListener("click",()=>setVisible(true));
    $("clearVisible").addEventListener("click",()=>setVisible(false));
    $("resetBtn").addEventListener("click",reset);
    $("buildBtn").addEventListener("click",buildZip);
  }

  function clampCustom(){let n=Math.round(Number($("customCount").value)||1);n=Math.max(1,Math.min(10,n));$("customCount").value=String(n);}
  function setCustomCount(value){$("customCount").value=String(Math.max(1,Math.min(10,Math.round(value||1))));refresh();}

  function familyMatches(meta,q){
    if(!q)return true;
    const hay=[meta.course,meta.topic,meta.label,meta.summary,meta.category,...(meta.skill_tags||[]),...(meta.representations||[])].join(" ").toLowerCase();
    return hay.includes(q);
  }

  function visibleGroups(){
    const selectedBrowse=new Set(browseCourses());
    const q=$("structureSearch").value.trim().toLowerCase();
    const groups=[];
    for(const course of (catalog?.courses||[])){
      if(!selectedBrowse.has(course.name))continue;
      for(const topic of (course.topics||[])){
        const topicMatches=q && [course.name,topic.label].join(" ").toLowerCase().includes(q);
        const families=(topic.families||[]).map(f=>familyMeta.get(f.id)).filter(meta=>topicMatches||familyMatches(meta,q));
        if(families.length)groups.push({course:course.name,topic_id:topic.id,topic:topic.label,families});
      }
    }
    return groups;
  }

  function setVisible(enabled){
    for(const group of visibleGroups()){
      for(const meta of group.families){
        const st=familyState.get(meta.id)||{enabled:false,count:1};
        st.enabled=enabled;
        if(st.count<1)st.count=1;
        familyState.set(meta.id,st);
      }
    }
    renderFamilies(); refresh();
  }

  function renderFamilies(){
    const mount=$("familyMount"); mount.innerHTML="";
    const groups=visibleGroups();
    let shown=0;
    if(!browseCourses().length){mount.innerHTML='<div class="empty-state">Check at least one grade/course filter above.</div>';$("structureCount").textContent="0 shown";renderSelectedTray();return;}
    if(!groups.length){mount.innerHTML='<div class="empty-state">No topics or skills match the current filters/search.</div>';$("structureCount").textContent="0 shown";renderSelectedTray();return;}

    for(const group of groups){
      const card=document.createElement("section");card.className="topic-card";
      const head=document.createElement("div");head.className="topic-head";head.innerHTML=`<h3>${escHtml(group.topic)}</h3><span class="grade-badge" title="${escAttr(group.course)}">${escHtml(gradeBadge(group.course))}</span>`;card.appendChild(head);
      const list=document.createElement("div");list.className="skill-list";
      for(const meta of group.families){
        shown++;
        const st=familyState.get(meta.id)||{enabled:false,count:1};familyState.set(meta.id,st);
        const row=document.createElement("div");row.className="skill-row"+(st.enabled?" selected":"");row.dataset.familyId=meta.id;
        const tags=[];if(meta.category)tags.push(meta.category);(meta.representations||[]).slice(0,1).forEach(x=>tags.push(x));
        row.innerHTML=`<input type="checkbox" data-family-toggle="${escAttr(meta.id)}" ${st.enabled?"checked":""} aria-label="Select ${escAttr(meta.label)}"><div class="skill-main"><h4>${escHtml(meta.label)}</h4><div>${tags.map(t=>`<span class="tag">${escHtml(t)}</span>`).join("")}</div><p>${escHtml(meta.summary||"")}</p></div><div class="qty"><button class="qty-btn" data-minus="${escAttr(meta.id)}" type="button" ${st.enabled?"":"disabled"}>−</button><input class="qty-input" data-family-count="${escAttr(meta.id)}" type="number" min="1" max="10" value="${st.count}" ${st.enabled?"":"disabled"} aria-label="Quantity for ${escAttr(meta.label)}"><button class="qty-btn" data-plus="${escAttr(meta.id)}" type="button" ${st.enabled?"":"disabled"}>+</button></div>`;
        list.appendChild(row);
      }
      card.appendChild(list);mount.appendChild(card);
    }
    $("structureCount").textContent=`${shown} skill${shown===1?"":"s"} shown`;
    bindFamilyControls(mount);
    renderSelectedTray();
  }

  function bindFamilyControls(root){
    root.querySelectorAll("[data-family-toggle]").forEach(el=>el.addEventListener("change",e=>{
      const id=e.target.dataset.familyToggle,st=familyState.get(id)||{enabled:false,count:1};st.enabled=e.target.checked;if(st.count<1)st.count=1;familyState.set(id,st);renderFamilies();refresh();
    }));
    root.querySelectorAll("[data-family-count]").forEach(el=>el.addEventListener("input",e=>{
      const id=e.target.dataset.familyCount,st=familyState.get(id)||{enabled:true,count:1};let n=Math.round(Number(e.target.value)||1);n=Math.max(1,Math.min(10,n));st.count=n;st.enabled=true;familyState.set(id,st);e.target.value=String(n);renderSelectedTray();refresh();
    }));
    root.querySelectorAll("[data-minus]").forEach(el=>el.addEventListener("click",()=>adjustFamilyCount(el.dataset.minus,-1)));
    root.querySelectorAll("[data-plus]").forEach(el=>el.addEventListener("click",()=>adjustFamilyCount(el.dataset.plus,1)));
  }

  function adjustFamilyCount(id,delta){const st=familyState.get(id)||{enabled:true,count:1};st.enabled=true;st.count=Math.max(1,Math.min(10,(st.count||1)+delta));familyState.set(id,st);renderFamilies();refresh();}
  function removeFamily(id){const st=familyState.get(id);if(st){st.enabled=false;familyState.set(id,st);}renderFamilies();refresh();}

  function selectedFamilies(){return [...familyMeta.values()].filter(meta=>familyState.get(meta.id)?.enabled).map(meta=>({...meta,requested_count:familyState.get(meta.id)?.count||1}));}
  function derivedQuestionCount(){return selectedFamilies().reduce((sum,f)=>sum+(f.requested_count||1),0)+($("customEnabled").checked?(Number($("customCount").value)||1):0);}

  function renderSelectedTray(){
    const tray=$("selectedTray"); if(!tray)return;
    const selected=selectedFamilies();
    if(!selected.length && !$("customEnabled").checked){tray.innerHTML='<div class="empty-state">Select at least one skill above.</div>';$("selectedTotal").textContent="0 questions";return;}
    tray.innerHTML="";
    for(const meta of selected){
      const st=familyState.get(meta.id);
      const row=document.createElement("div");row.className="selected-item";
      row.innerHTML=`<div><strong>${escHtml(meta.label)}</strong><span class="selected-meta">${escHtml(meta.course)} · ${escHtml(meta.topic)}</span></div><div class="qty"><button class="qty-btn" data-tray-minus="${escAttr(meta.id)}" type="button">−</button><input class="qty-input" data-tray-count="${escAttr(meta.id)}" type="number" min="1" max="10" value="${st.count}" aria-label="Selected quantity for ${escAttr(meta.label)}"><button class="qty-btn" data-tray-plus="${escAttr(meta.id)}" type="button">+</button></div><button class="remove-btn" data-remove="${escAttr(meta.id)}" type="button" title="Remove ${escAttr(meta.label)}">×</button>`;
      tray.appendChild(row);
    }
    if($("customEnabled").checked){
      const row=document.createElement("div");row.className="selected-item";
      row.innerHTML=`<div><strong>Custom question structure</strong><span class="selected-meta">${escHtml(browseCourses().join(", ")||"Selected grade scope")}</span></div><div class="qty"><button class="qty-btn" data-custom-tray-minus type="button">−</button><input class="qty-input" data-custom-tray-count type="number" min="1" max="10" value="${escAttr($("customCount").value)}"><button class="qty-btn" data-custom-tray-plus type="button">+</button></div><button class="remove-btn" data-remove-custom type="button" title="Remove custom structure">×</button>`;
      tray.appendChild(row);
    }
    $("selectedTotal").textContent=`${derivedQuestionCount()} question${derivedQuestionCount()===1?"":"s"}`;
    tray.querySelectorAll("[data-tray-minus]").forEach(el=>el.addEventListener("click",()=>adjustFamilyCount(el.dataset.trayMinus,-1)));
    tray.querySelectorAll("[data-tray-plus]").forEach(el=>el.addEventListener("click",()=>adjustFamilyCount(el.dataset.trayPlus,1)));
    tray.querySelectorAll("[data-tray-count]").forEach(el=>el.addEventListener("input",e=>{const id=e.target.dataset.trayCount,st=familyState.get(id);if(!st)return;let n=Math.round(Number(e.target.value)||1);n=Math.max(1,Math.min(10,n));st.count=n;familyState.set(id,st);e.target.value=String(n);renderFamilies();refresh();}));
    tray.querySelectorAll("[data-remove]").forEach(el=>el.addEventListener("click",()=>removeFamily(el.dataset.remove)));
    tray.querySelector("[data-custom-tray-minus]")?.addEventListener("click",()=>setCustomCount(Number($("customCount").value)-1));
    tray.querySelector("[data-custom-tray-plus]")?.addEventListener("click",()=>setCustomCount(Number($("customCount").value)+1));
    tray.querySelector("[data-custom-tray-count]")?.addEventListener("input",e=>setCustomCount(Number(e.target.value)));
    tray.querySelector("[data-remove-custom]")?.addEventListener("click",()=>{$("customEnabled").checked=false;$("customDescription").disabled=true;$("customCount").disabled=true;$("customMinus").disabled=true;$("customPlus").disabled=true;renderSelectedTray();refresh();});
  }

  function selectedCourseScope(){
    const names=new Set(selectedFamilies().map(f=>f.course));
    if($("customEnabled").checked)browseCourses().forEach(x=>names.add(x));
    return [...names];
  }

  function validate(){
    const problems=[];
    if(!$("title").value.trim())problems.push("worksheet title");
    if(!selectedFamilies().length && !$("customEnabled").checked)problems.push("at least one question structure");
    if($("customEnabled").checked && !$("customDescription").value.trim())problems.push("custom structure description");
    if($("customEnabled").checked && !browseCourses().length && !selectedFamilies().length)problems.push("a grade/course filter for the custom structure");
    if(derivedQuestionCount()>60)problems.push("60 questions or fewer per version");
    return problems;
  }

  function refresh(){
    renderSelectedTray();
    const q=derivedQuestionCount();
    const errors=validate();$("buildBtn").disabled=errors.length>0;
    if(errors.length){$("status").className="status warn";$("status").textContent="Add/fix: "+errors.join("; ")+".";}
    else{$("status").className="status good";$("status").textContent=`Ready to package ${q} exact question${q===1?"":"s"} across ${$("versions").value} version${$("versions").value==="1"?"":"s"}.`;}
  }

  function reset(){
    $("courseFilters").querySelectorAll('input[type="checkbox"]').forEach(x=>x.checked=x.value==="Grade 5 Math");
    for(const st of familyState.values()){st.enabled=false;st.count=1;}
    $("title").value="Math Practice";$("target").value="";$("versions").value="3";document.querySelector('input[name="difficulty"][value="balanced"]').checked=true;
    $("twoColumn").checked=true;$("answerKey").checked=true;
    $("customEnabled").checked=false;$("customDescription").value="";$("customDescription").disabled=true;$("customCount").value="1";$("customCount").disabled=true;$("customMinus").disabled=true;$("customPlus").disabled=true;
    $("structureSearch").value="";renderFamilies();refresh();
  }

  function prepareDownload(blob,filename){const url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=filename;link.style.display="none";document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}
  async function loadText(path){const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw new Error(`Could not load ${path} (HTTP ${r.status})`);return await r.text();}
  async function loadGitHubRepoText(repo,path){const encodedPath=path.split("/").map(part=>encodeURIComponent(part)).join("/"),url=`https://api.github.com/repos/${repo}/contents/${encodedPath}`,r=await fetch(url,{cache:"no-store",headers:{Accept:"application/vnd.github+json"}});if(!r.ok)throw new Error(`Could not load GitHub source ${path} (HTTP ${r.status})`);const data=await r.json();if(data.type!=="file"||!data.content)throw new Error(`GitHub source ${path} was not returned as a file.`);const binary=atob(String(data.content).replace(/\s/g,"")),bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return new TextDecoder("utf-8").decode(bytes);}
  async function sha256Hex(value){const digest=await crypto.subtle.digest("SHA-256",enc.encode(String(value)));return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,"0")).join("");}

  async function buildZip(){
    const errors=validate();if(errors.length)return;
    $("buildBtn").disabled=true;$("status").className="status";$("status").textContent="Packaging self-contained worksheet request…";
    try{
      const selected=selectedFamilies();
      const [contract,shared,graphStandard,catalogText,dashboardCss,worksheetCss,questionCore,generatorBank,parallelRules,g12,g13,g14]=await Promise.all([
        loadText("WORKSHEET_BUILDER_CONTRACT.md"),loadText("../_shared/DISTRICT_RESPONSE_BUILD_STANDARD.md"),loadText("../_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md"),loadText("question_structure_catalog.json"),loadText("dashboard_styles.css"),loadText("worksheet_styles.css"),loadGitHubRepoText("tnezki/memories","_question_structure/QUESTION_STRUCTURE_CORE.md"),loadGitHubRepoText("tnezki/memories","_question_structure/catalogs/math_worksheet_generator_bank.json"),loadGitHubRepoText("tnezki/memories","_question_structure/guides/parallel_family_rules.md"),loadGitHubRepoText("tnezki/memories","Tools/~graph_tool_v12.py"),loadGitHubRepoText("tnezki/memories","Tools/~graph_tool_v13.py"),loadGitHubRepoText("tnezki/memories","Tools/~graph_tool_v14.py")
      ]);
      const [dashHash,workHash]=await Promise.all([sha256Hex(dashboardCss),sha256Hex(worksheetCss)]),versions=Number($("versions").value),count=derivedQuestionCount(),scope=selectedCourseScope();
      const request={
        schema:REQUEST_SCHEMA,tool_version:TOOL_VERSION,created_at:new Date().toISOString(),
        contracts:{worksheet_builder:CONTRACT_VERSION,shared_standard:SHARED_STANDARD_VERSION,graph_rendering_standard:"district-graph-rendering-standard/1.0",question_structure_core:"current GitHub authority",generator_bank:"math-worksheet-generator-bank/0.1"},
        worksheet:{title:$("title").value.trim(),grade_course_scope:scope,learning_target:$("target").value.trim()||null,question_count_per_version:count,selection_model:"explicit_family_counts",difficulty_profile:difficulty(),version_count:versions,version_labels:["A","B","C","D"].slice(0,versions),answer_key:$("answerKey").checked},
        question_structures:{catalog_schema:catalog?.schema||"catalog-unavailable",selected_families:selected,parallel_form_policy:catalog?.parallel_form_policy||null,custom_enabled:$("customEnabled").checked,custom_course_scope:$("customEnabled").checked?browseCourses():[],custom_description:$("customEnabled").checked?$("customDescription").value.trim():null,custom_requested_count:$("customEnabled").checked?(Number($("customCount").value)||1):0},
        layout:{page_size:"US Letter portrait",two_column:$("twoColumn").checked,workspace_scale_percent:WORKSPACE_DEFAULT_PERCENT,graph_scale_percent:GRAPH_DEFAULT_PERCENT,workspace_control_range_percent:WORKSPACE_RANGE_PERCENT,graph_control_range_percent:GRAPH_RANGE_PERCENT,independent_controls:true,full_page_workspace_capable:true},
        locked_styles:{dashboard:{version:DASHBOARD_STYLE_VERSION,request_path:"response_contract/dashboard_styles.css",response_path:"assets/dashboard_styles.css",sha256:dashHash},worksheet:{version:WORKSHEET_STYLE_VERSION,request_path:"response_contract/worksheet_styles.css",response_path:"assets/worksheet_styles.css",sha256:workHash}},
        graph_tools:{entrypoint:"response_contract/graph_tool/~graph_tool_v14.py",dependencies:["response_contract/graph_tool/~graph_tool_v13.py","response_contract/graph_tool/~graph_tool_v12.py"],cartesian_print_standard:{grid:{color:"#aaaaaa",linewidth_pt:0.6},axes_arrows:{color:"#222222",linewidth_pt:1.8},relation:{linewidth_pt:2.0},major_ticks:{linewidth_pt:1.2}}},
        resolved_outputs:{required_files:["CLICK_ME.html","assets/dashboard_styles.css","assets/worksheet_styles.css","worksheet/worksheet.html","data/request.json","data/qa.json",...($("answerKey").checked?["teacher/answer_key.html"]:[])]},
        authority_note:"The exact selected-family counts are the worksheet blueprint. Question Structure Core and the Math Worksheet Generator Bank control family behavior. All authored problems remain original."
      };
      const entries=[
        {name:"REQUEST_READ_ME_FIRST.md",data:enc.encode(buildInstructions(request))},{name:"request.json",data:enc.encode(JSON.stringify(request,null,2))},{name:"response_contract/WORKSHEET_BUILDER_CONTRACT.md",data:enc.encode(contract)},{name:"response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md",data:enc.encode(shared)},{name:"response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md",data:enc.encode(graphStandard)},{name:"response_contract/QUESTION_STRUCTURE_CORE.md",data:enc.encode(questionCore)},{name:"response_contract/MATH_WORKSHEET_GENERATOR_BANK.json",data:enc.encode(generatorBank)},{name:"response_contract/PARALLEL_FAMILY_RULES.md",data:enc.encode(parallelRules)},{name:"response_contract/QUESTION_STRUCTURE_CATALOG.json",data:enc.encode(catalogText)},{name:"response_contract/dashboard_styles.css",data:enc.encode(dashboardCss)},{name:"response_contract/worksheet_styles.css",data:enc.encode(worksheetCss)},{name:"response_contract/DASHBOARD_STYLE_SHA256.txt",data:enc.encode(dashHash+"\n")},{name:"response_contract/WORKSHEET_STYLE_SHA256.txt",data:enc.encode(workHash+"\n")},{name:"response_contract/graph_tool/~graph_tool_v12.py",data:enc.encode(g12)},{name:"response_contract/graph_tool/~graph_tool_v13.py",data:enc.encode(g13)},{name:"response_contract/graph_tool/~graph_tool_v14.py",data:enc.encode(g14)}
      ];
      const blob=makeZip(entries),scopeSlug=scope.length===1?scope[0]:"mixed_math",name=`math_worksheet_request_${slug(scopeSlug)}_${dateStamp()}.zip`;prepareDownload(blob,name);$("status").className="status good";$("status").textContent="Request package created. Download started.";
    }catch(error){console.error(error);$("status").className="status bad";$("status").textContent="Could not package request: "+(error.message||error);}
    finally{$("buildBtn").disabled=validate().length>0;}
  }

  function buildInstructions(req){
    const fam=req.question_structures.selected_families.map(f=>`- ${f.course} > ${f.topic} > ${f.id}: ${f.label} — ${f.requested_count} question${f.requested_count===1?"":"s"} per version — ${f.summary}`).join("\n");
    return `# Math Worksheet Builder Request — Pilot\n\n## Run automatically\nBuild the complete worksheet package from this ZIP. No additional teacher prompt is required. Return exactly ONE response ZIP.\n\n## Teacher request\n- Grade/course scope: ${req.worksheet.grade_course_scope.join(", ")}\n- Title: ${req.worksheet.title}\n- Learning target/focus: ${req.worksheet.learning_target||"Not specified"}\n- Questions per version: ${req.worksheet.question_count_per_version}\n- Selection model: exact selected family counts\n- Difficulty profile: ${req.worksheet.difficulty_profile}\n- Versions: ${req.worksheet.version_count} (${req.worksheet.version_labels.join(", ")})\n- Answer key: ${req.worksheet.answer_key?"Yes":"No"}\n- Student layout: ${req.layout.two_column?"two columns":"one column"}\n- Initial workspace scale: ${req.layout.workspace_scale_percent}%\n- Workspace adjustment range in the finished worksheet: ${req.layout.workspace_control_range_percent[0]}%–${req.layout.workspace_control_range_percent[1]}%\n- Initial graph/diagram scale: ${req.layout.graph_scale_percent}%\n\n## Exact selected question blueprint\n${fam||"No catalog families selected."}\n${req.question_structures.custom_enabled?`\n### Teacher custom structure\nScope: ${req.question_structures.custom_course_scope.join(", ")||"Use the worksheet scope"}\nCount per version: ${req.question_structures.custom_requested_count}\n${req.question_structures.custom_description}\n`:""}\n## Required authority\nFollow response_contract/QUESTION_STRUCTURE_CORE.md first for universal authoring behavior, then response_contract/MATH_WORKSHEET_GENERATOR_BANK.json and response_contract/PARALLEL_FAMILY_RULES.md for worksheet-family and parallel-form behavior, plus the worksheet and district response contracts. Use response_contract/QUESTION_STRUCTURE_CATALOG.json as the teacher-selection snapshot. All student questions, values, contexts, diagrams, and answer choices must be original.\n\nThe selected family counts are exact. Do not auto-balance, substitute, or reallocate categories. If a selected family requests 3, produce 3 legitimate instances of that family per version.\n\nFor parallel versions, preserve the same I Can/evidence family, family sequence, requested count, and difficulty slot-for-slot while varying legitimate original parameters and surface context.\n\nThe authoritative graph entrypoint is packaged at response_contract/graph_tool/~graph_tool_v14.py with v13 and v12 beside it. Use it for supported Cartesian graph needs and preserve the locked Cartesian print weights in request.json.\n\nCopy both locked CSS files byte-for-byte to the response assets and verify their hashes in QA. The student worksheet HTML must keep per-version/per-problem workspace and graph/diagram scaling controls available before print. Workspace must be adjustable from 0% through 1200% so a teacher can collapse it completely or expand one problem to approximately a full printable page.\n\n## Required files\n${req.resolved_outputs.required_files.map(p=>`- ${p}`).join("\n")}\n\nVisually inspect the adjustable worksheet and answer key in screen and print modes. Return only the completed response ZIP.`;
  }

  function slug(value){return String(value||"worksheet").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"").slice(0,44)||"worksheet";}
  function dateStamp(){const d=new Date();return `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,"0")}${String(d.getDate()).padStart(2,"0")}`;}
  function makeZip(entries){const localParts=[],centralParts=[];let offset=0,count=0;for(const entry of entries){const nameBytes=enc.encode(entry.name.replace(/\\/g,"/")),data=entry.data instanceof Uint8Array?entry.data:new Uint8Array(entry.data),crc=crc32(data),{time,date}=dosTimeDate(new Date());const local=new Uint8Array(30+nameBytes.length),lv=new DataView(local.buffer);lv.setUint32(0,0x04034b50,true);lv.setUint16(4,20,true);lv.setUint16(6,0x0800,true);lv.setUint16(8,0,true);lv.setUint16(10,time,true);lv.setUint16(12,date,true);lv.setUint32(14,crc,true);lv.setUint32(18,data.length,true);lv.setUint32(22,data.length,true);lv.setUint16(26,nameBytes.length,true);lv.setUint16(28,0,true);local.set(nameBytes,30);localParts.push(local,data);const central=new Uint8Array(46+nameBytes.length),cv=new DataView(central.buffer);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(8,0x0800,true);cv.setUint16(10,0,true);cv.setUint16(12,time,true);cv.setUint16(14,date,true);cv.setUint32(16,crc,true);cv.setUint32(20,data.length,true);cv.setUint32(24,data.length,true);cv.setUint16(28,nameBytes.length,true);cv.setUint16(30,0,true);cv.setUint16(32,0,true);cv.setUint16(34,0,true);cv.setUint16(36,0,true);cv.setUint32(38,0,true);cv.setUint32(42,offset,true);central.set(nameBytes,46);centralParts.push(central);offset+=local.length+data.length;count++;}const centralSize=centralParts.reduce((s,p)=>s+p.length,0),end=new Uint8Array(22),ev=new DataView(end.buffer);ev.setUint32(0,0x06054b50,true);ev.setUint16(4,0,true);ev.setUint16(6,0,true);ev.setUint16(8,count,true);ev.setUint16(10,count,true);ev.setUint32(12,centralSize,true);ev.setUint32(16,offset,true);ev.setUint16(20,0,true);return new Blob([...localParts,...centralParts,end],{type:"application/zip"});}
  function dosTimeDate(d){const year=Math.max(1980,d.getFullYear());return {time:(d.getHours()<<11)|(d.getMinutes()<<5)|Math.floor(d.getSeconds()/2),date:((year-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate()};}
  const crcTable=(()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);t[n]=c>>>0;}return t;})();
  function crc32(bytes){let crc=0xffffffff;for(const b of bytes)crc=crcTable[(crc^b)&0xff]^(crc>>>8);return (crc^0xffffffff)>>>0;}

  init();
})();
