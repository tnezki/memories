const RAW_ROOT='https://raw.githubusercontent.com/tnezki/algebra/main/banks/unit1/';
const PAGE_ROOT='https://tnezki.github.io/algebra/banks/unit1/';
const CACHE_PREFIX='alg-assessment-builder-u1:';
const DRAFT_KEY='alg-assessment-builder-owner-draft-v1';
const state={
  product:'Practice',mgid:'U1-MG01',focus:'',selected:new Map(),goal:null,qmap:null,
  manifest:null,resolution:null,revisions:new Map(),usedCache:false,versionCount:1,activeVersion:1,
  allFigureSize:260,allWorkSize:0,practiceLayoutState:null,saveTarget:'both',draftLoaded:false,builtVersions:[],generationMessage:'',scrambleOrder:true,scrambleChoices:true,
  checkpointPlan:null,checkpointPlanId:'',checkpointExtensionsReady:false,checkpointBusy:false,checkpointEligibility:null,checkpointEligibleIcanIds:new Set(),checkpointScopeLoaded:false,checkpointAssembly:null,
  summativePlan:null,summativePlanId:'',summativeFamiliesReady:false,summativeBusy:false,summativeEligibility:null,summativeEligibleIcanIds:new Set(),summativeScopeLoaded:false,summativeAssembly:null,
  suppressLatestRestore:false
};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $=id=>document.getElementById(id);
function safeCacheGet(key){try{return localStorage.getItem(key)}catch(_){return null}}
function safeCacheSet(key,value){try{localStorage.setItem(key,value)}catch(_){}}
async function getJson(path){
  try{
    const r=await fetch(RAW_ROOT+path,{cache:'no-store'});
    if(!r.ok)throw new Error(`${path} (${r.status})`);
    const data=await r.json();
    safeCacheSet(CACHE_PREFIX+path,JSON.stringify(data));
    return data;
  }catch(err){
    const cached=safeCacheGet(CACHE_PREFIX+path);
    if(cached){state.usedCache=true;return JSON.parse(cached)}
    throw err;
  }
}
function rewriteRelativeResources(html){
  const t=document.createElement('template');t.innerHTML=html||'';
  t.content.querySelectorAll('[src]').forEach(el=>{const v=el.getAttribute('src');if(v&&!/^(https?:|data:|blob:|\/\/)/i.test(v))el.setAttribute('src',new URL(v,PAGE_ROOT).href)});
  t.content.querySelectorAll('a[href]').forEach(el=>{const v=el.getAttribute('href');if(v&&!/^(https?:|#|mailto:|\/\/)/i.test(v))el.setAttribute('href',new URL(v,PAGE_ROOT).href)});
  return t.innerHTML;
}
function mergeFamilyRevision(f,rev){if(!rev)return f;const o=rev.override||{};return {...f,...o,template_contract:{...(f.template_contract||{}),...(o.template_contract||{})},exemplar:{...(f.exemplar||{}),...(o.exemplar||{})}}}
function currentApprovalStatus(f){return f.approval_status||state.qmap?.items?.[f.family_id]?.status||''}
function familySelectable(f){const status=currentApprovalStatus(f);return (status==='APPROVED'||status==='DRAFT_REVIEW')&&!f.superseded_by}
function qidFor(fid){return state.qmap?.items?.[fid]?.teacher_question_id||''}
function familyHasFigure(x){
  const html=x?.f?.exemplar?.student_html||'';
  if(!html)return false;
  const t=document.createElement('template');t.innerHTML=html;
  return Boolean(t.content.querySelector('img,svg,canvas'));
}
function familyCard(f,ic){
  const ex=f.exemplar||{},qid=qidFor(f.family_id),selectable=familySelectable(f),checked=state.selected.has(f.family_id);
  return `<article class="family ${checked?'selected':''} ${selectable?'':'unavailable'}" id="${esc(f.family_id)}">
    <input class="family-select" type="checkbox" data-family="${esc(f.family_id)}" ${checked?'checked':''} ${selectable?'':'disabled'} title="${selectable?'Select this current bank family':'This family is unavailable for runtime use'}">
    <div class="family-head"><span class="qid">${esc(qid)}</span><span class="badge">Family ${esc(f.family_label)}</span><span class="family-name">${esc(f.family_name)}</span></div>
    <div class="ican-mini">${esc(ic.i_can_id)} · ${esc(ic.exact_text)}</div>
    <p class="purpose">${esc(f.family_purpose)}</p>
    <div class="meta">${esc(f.question_structure_id)} · ${esc(f.response_mode)} · ${esc(f.representation_mode)}</div>
    <div class="question"><h4>Exemplar</h4>${rewriteRelativeResources(ex.student_html||'<p>Exemplar unavailable.</p>')}</div>
    <details><summary>Answer + short solution</summary><p><strong>Answer:</strong> ${esc(ex.answer)}</p><p>${esc(ex.solution)}</p></details>
  </article>`;
}
async function loadCore(){
  const [manifest,resolution,qmap,revs]=await Promise.all([
    getJson('BANK_MANIFEST.json'),getJson('BANK_RESOLUTION.json'),getJson('QUESTION_ID_MAP.json'),getJson('FAMILY_REVISIONS.json')
  ]);
  state.manifest=manifest;state.resolution=resolution;state.qmap=qmap;state.revisions=new Map((revs.revisions||[]).map(r=>[r.family_id,r]));
  const status=$('bankStatus');
  if(state.usedCache){status.className='status-pill cached';status.textContent=`Using cached bank · revision ${manifest.content_revision??'?'}`}
  else{status.className='status-pill live';status.textContent=`Bank current · revision ${manifest.content_revision??'?'}`}
}
async function getResolvedGoal(mgid){
  const basePath=state.resolution.base_mastery_goal_files?.[mgid]||`mastery_goals/${mgid}.json`;
  const extPath=state.resolution.extension_mastery_goal_files?.[mgid];
  const base=await getJson(basePath);const ext=extPath?await getJson(extPath):null;
  const byIc=new Map((ext?.i_cans||[]).map(x=>[x.i_can_id,x.families||[]]));
  const icans=(base.i_cans||[]).map(ic=>({...ic,families:[...(ic.families||[]),...(byIc.get(ic.i_can_id)||[])].map(f=>mergeFamilyRevision(f,state.revisions.get(f.family_id)))}));
  return {...base,i_cans:icans};
}
async function loadGoal(mgid){
  try{
    $('familyRows').innerHTML='<div class="notice">Loading approved families…</div>';
    state.goal=await getResolvedGoal(mgid);state.mgid=mgid;renderGoal();
  }catch(err){$('familyRows').innerHTML=`<div class="error">Could not load the bank: ${esc(err.message)}</div>`;$('bankStatus').className='status-pill error';$('bankStatus').textContent='Bank unavailable'}
}
function setupGoalNav(){
  const mg=$('mgSelect'),ic=$('icanSelect');mg.innerHTML='';
  ['01','02','03','04'].forEach(x=>mg.add(new Option('MG'+x,'U1-MG'+x)));mg.value=state.mgid;
  ic.innerHTML='';ic.add(new Option('Show all I Cans',''));
  (state.goal?.i_cans||[]).forEach(x=>ic.add(new Option(`${x.i_can_id} · ${x.exact_text}`,x.i_can_id)));ic.value=state.focus||'';
}
function renderGoal(){
  const goal=state.goal,mg=goal.mastery_goal,icans=goal.i_cans||[];setupGoalNav();
  const visibleIcans=state.focus?icans.filter(ic=>ic.i_can_id===state.focus):icans;
  $('mgTitle').textContent=`${state.mgid} · ${mg.title}`;$('mgSubtitle').textContent=mg.exact_text;
  const allFamilies=icans.flatMap(x=>x.families||[]);
  const visibleFamilies=visibleIcans.flatMap(x=>x.families||[]);
  const selectable=visibleFamilies.filter(familySelectable).length;
  $('mgCount').textContent=state.focus
    ?`${visibleFamilies.length} families in ${state.focus} · ${selectable} selectable`
    :`${icans.length} I Cans · ${allFamilies.length} families · ${selectable} selectable`;
  const heads=$('icanHeads');
  heads.style.gridTemplateColumns=`repeat(${Math.max(1,visibleIcans.length)},minmax(0,1fr))`;
  heads.innerHTML=visibleIcans.map(ic=>`<div class="ican-head">${esc(ic.i_can_id)}<br>${esc(ic.exact_text)}</div>`).join('');
  const labels=[...new Set(visibleIcans.flatMap(ic=>(ic.families||[]).map(f=>f.family_label)))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
  const rows=$('familyRows');rows.innerHTML='';
  for(const label of labels){
    const cells=visibleIcans.map(ic=>{const f=(ic.families||[]).find(x=>x.family_label===label);return f?familyCard(f,ic):''}).filter(Boolean);
    if(!cells.length)continue;
    const l=document.createElement('div');l.className='row-label';l.textContent='Family '+label;rows.appendChild(l);
    const row=document.createElement('div');row.className='family-row';row.style.gridTemplateColumns=`repeat(${Math.max(1,cells.length)},minmax(0,1fr))`;row.innerHTML=cells.join('');rows.appendChild(row);
  }
  rows.querySelectorAll('.family-select').forEach(cb=>cb.addEventListener('change',()=>toggleFamily(cb.dataset.family,cb.checked)));
  typeset();
}
function findFamily(fid){for(const ic of state.goal?.i_cans||[]){const f=(ic.families||[]).find(x=>x.family_id===fid);if(f)return {f,ic}}return null}
function toggleFamily(fid,on){
  if(on){const hit=findFamily(fid);if(hit&&familySelectable(hit.f)){state.selected.set(fid,{...hit,f:hit.f,ic:hit.ic,figureSize:state.allFigureSize,workSize:state.allWorkSize,unit:1})}}
  else state.selected.delete(fid);
  invalidateBuiltVersions('Question selection changed. Build Versions again when ready.');updateSummary();renderGoal();saveDraft();
}
function sanitizeLabel(s){return String(s||'').trim().replace(/[^A-Za-z0-9]+/g,'_').replace(/^_+|_+$/g,'')||'Untitled'}
function productToken(){return state.product.replace(/\s+/g,'_')}
function itemToken(){return sanitizeLabel($('itemLabel').value)}
function customToken(){return sanitizeLabel($('customName').value)}
function customName(){return $('customName').value.trim()}
function displayTitle(){const item=$('itemLabel').value.trim()||'Untitled';return customName()?`${item} ${customName()}`:`${item} ${state.product}`}
function baseFilename(v=1){const c=customName()?`_${customToken()}`:'';if(isCheckpoint())return `Algebra_1_${itemToken()}${c}_Checkpoint_V${v}`;if(isSummative())return `Algebra_1_${itemToken()}${c}_Summative_V${v}`;return `Algebra_1_U1_${itemToken()}${c}_${productToken()}_V${v}`}
function storageName(){
  const item=displayTitle();
  const plural=state.product==='Practice'?'Practices':state.product==='Quick Check'?'Quick Checks':state.product==='Summative'?'Assessments':state.product+'s';
  const library=`Teacher Library → Unit 1 → ${plural} → ${item}`;
  if(state.saveTarget==='local')return 'Local copy only';
  if(state.saveTarget==='library')return library;
  return `${library} + local copy`;
}
function shortIcan(id){return String(id||'').replace(/^U\d+-/,'')}

function draftPayload(){
  return {
    schema_version:1,
    saved_at:new Date().toISOString(),
    bank_revision:state.manifest?.content_revision??null,
    product:state.product,
    item_label:$('itemLabel')?.value??'1.1',
    custom_name:$('customName')?.value??'',
    save_target:state.saveTarget,
    mgid:state.mgid,
    focus:state.focus,
    version_count:state.versionCount,
    active_version:state.activeVersion,
    all_figure_size:state.allFigureSize,
    all_work_size:state.allWorkSize,
    practice_layout_state:state.practiceLayoutState||null,
    scramble_order:state.scrambleOrder,
    scramble_choices:state.scrambleChoices,
    checkpoint_plan_id:state.checkpointPlanId||'',
    checkpoint_eligible_i_cans:[...state.checkpointEligibleIcanIds].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})),
    summative_plan_id:state.summativePlanId||'',
    suppress_latest_restore:!!state.suppressLatestRestore,
    summative_eligible_i_cans:[...state.summativeEligibleIcanIds].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})),
    selected:[...state.selected.values()].map(x=>({
      family_id:x.f.family_id,
      unit:x.unit||1,
      figureSize:x.figureSize,
      workSize:x.workSize,
      baseInstance:x.baseInstance||null,
      f:x.f,
      ic:x.ic
    }))
  };
}
function saveDraft(){
  if(!state.manifest)return;
  try{
    localStorage.setItem(DRAFT_KEY,JSON.stringify(draftPayload()));
    setDraftStatus('Draft auto-saved in this browser.','');
  }catch(_){setDraftStatus('Browser draft could not be saved.','warn')}
}
function setDraftStatus(message,kind=''){
  const el=$('draftStatus');if(!el)return;el.textContent=message;el.className=`draft-status ${kind}`.trim();
}
function normalizeDraft(d){
  if(!d||typeof d!=='object')throw new Error('This is not an Assessment Builder draft.');
  if(Number(d.schema_version)!==1)throw new Error(`Unsupported draft schema: ${d.schema_version??'missing'}`);
  if(!Array.isArray(d.selected))throw new Error('Draft is missing its selected-question list.');
  return d;
}
async function resolveDraftSelections(d){
  const groups=new Map();
  for(const x of d.selected||[]){
    const fid=String(x?.family_id||'');
    const m=fid.match(/^(U\d+-MG\d+)-/);
    if(!m)continue;
    if(!groups.has(m[1]))groups.set(m[1],[]);
    groups.get(m[1]).push(x);
  }
  const rebuilt=new Map();let skipped=0;
  for(const [mgid,entries] of groups){
    if(!mgid.startsWith('U1-')){skipped+=entries.length;continue;}
    let goal;try{goal=await getResolvedGoal(mgid)}catch(_){skipped+=entries.length;continue;}
    const lookup=new Map();
    for(const ic of goal.i_cans||[])for(const f of ic.families||[])lookup.set(f.family_id,{f,ic});
    for(const x of entries){
      const hit=lookup.get(x.family_id);
      if(!hit||!familySelectable(hit.f)){skipped+=1;continue;}
      rebuilt.set(x.family_id,{f:hit.f,ic:hit.ic,figureSize:Number(x.figureSize??state.allFigureSize),workSize:Number(x.workSize??0),unit:1,baseInstance:(d.bank_revision===state.manifest?.content_revision&&x.baseInstance)?x.baseInstance:null,candidateInstance:null});
    }
  }
  return {rebuilt,skipped};
}
async function hydrateDraft(raw,source='browser'){
  const d=normalizeDraft(raw);
  state.product=['Practice','Quick Check','Checkpoint','Summative'].includes(d.product)?d.product:'Practice';
  state.saveTarget=d.save_target||'both';
  state.mgid=(d.mgid&&String(d.mgid).startsWith('U1-'))?d.mgid:state.mgid;state.focus=d.focus||'';
  state.versionCount=clampVersionCount(d.version_count||1);state.activeVersion=Math.min(d.active_version||1,state.versionCount);
  state.allFigureSize=Number(d.all_figure_size||260);state.allWorkSize=Number(d.all_work_size||0);state.practiceLayoutState=(d.practice_layout_state&&typeof d.practice_layout_state==='object')?d.practice_layout_state:null;
  state.scrambleOrder=d.scramble_order!==false;state.scrambleChoices=d.scramble_choices!==false;state.checkpointPlanId=String(d.checkpoint_plan_id||'');state.suppressLatestRestore=d.suppress_latest_restore===true;state.checkpointEligibleIcanIds=new Set(Array.isArray(d.checkpoint_eligible_i_cans)?d.checkpoint_eligible_i_cans.map(String):[]);state.summativePlanId=String(d.summative_plan_id||'');state.summativeEligibleIcanIds=new Set(Array.isArray(d.summative_eligible_i_cans)?d.summative_eligible_i_cans.map(String):[]);
  const {rebuilt,skipped}=await resolveDraftSelections(d);state.selected=rebuilt;
  $('productType').value=state.product;$('itemLabel').value=d.item_label||'1.1';$('customName').value=d.custom_name||'';$('saveTarget').value=state.saveTarget;
  state.draftLoaded=true;
  const revChanged=d.bank_revision!=null&&state.manifest?.content_revision!=null&&d.bank_revision!==state.manifest.content_revision;
  let msg=`Loaded ${state.selected.size} current bank question${state.selected.size===1?'':'s'} from ${source} draft.`;
  if(revChanged)msg+=` Bank changed from revision ${d.bank_revision} to ${state.manifest.content_revision}; selections were re-resolved against the current bank.`;
  if(skipped)msg+=` ${skipped} unavailable selection${skipped===1?' was':'s were'} skipped.`;
  setDraftStatus(msg,skipped?'warn':'good');
}
async function restoreDraft(){
  let d=null;try{d=JSON.parse(localStorage.getItem(DRAFT_KEY)||'null')}catch(_){setDraftStatus('Browser draft could not be read.','warn')}
  if(!d)return;
  try{await hydrateDraft(d,'browser')}catch(err){setDraftStatus(`Browser draft was not restored: ${err.message}`,'warn')}
}
async function loadDraftFile(file){
  if(!file)return;
  try{
    const text=await file.text();const d=JSON.parse(text);await hydrateDraft(d,'uploaded');
    await loadGoal(state.mgid);updateSummary();
    saveDraft();
  }catch(err){setDraftStatus(`Could not load draft: ${err.message}`,'error')}
}
function downloadDraft(){
  const data=JSON.stringify(draftPayload(),null,2)+'\n';
  const blob=new Blob([data],{type:'application/json'});const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download=`${baseFilename(1)}_BUILD_DRAFT.json`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
function printablePageSnapshot(root=$('paperPages')){
  if(!root)return '';
  const holder=document.createElement('div');
  root.querySelectorAll('.paper-page').forEach(page=>{
    const clone=page.cloneNode(true);
    clone.classList.remove('plc-preview-hidden','screen-hidden');
    clone.style.removeProperty('zoom');
    clone.style.removeProperty('margin');
    holder.appendChild(clone);
  });
  return holder.innerHTML;
}
function combinedBaseFilename(){return baseFilename(1).replace(/_V1$/,'_ALL_VERSIONS')}
function downloadCurrentPreview(){
  const html=wrapStoredStudentDocument(printablePageSnapshot(),state.activeVersion);
  const blob=new Blob([html],{type:'text/html'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${baseFilename(state.activeVersion)}.html`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
async function allVersionPages(){
  if(!state.builtVersions.length)return '';
  const original=state.activeVersion;const chunks=[];
  try{
    for(let v=1;v<=state.builtVersions.length;v++)chunks.push(await captureVersionPages(v));
  }finally{
    state.activeVersion=original;
    await renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap());
    renderVersionTabs();
  }
  return chunks.join('');
}
function openPrintWindowShell(){
  const w=window.open('about:blank','_blank');
  if(!w)throw new Error('The browser blocked the print window. Allow pop-ups for 127.0.0.1 and try again.');
  w.document.open();w.document.write('<!doctype html><title>Preparing print…</title><p style="font-family:Arial;padding:24px">Preparing printable pages…</p>');w.document.close();return w;
}
function writePrintWindow(w,html){
  const marked=html.replace('</body>','<script>window.addEventListener("load",()=>setTimeout(()=>window.print(),500));<\/script></body>');
  w.document.open();w.document.write(marked);w.document.close();
}
async function printCurrentVersion(){
  if(!state.builtVersions.length){setSaveStatus('Build versions first.','warn');return}
  let w;try{w=openPrintWindowShell();const pages=await captureVersionPages(state.activeVersion);writePrintWindow(w,wrapStoredStudentDocument(pages,state.activeVersion))}catch(err){if(w&&!w.closed)w.close();setSaveStatus(`Could not open print view: ${err.message}`,'warn')}
}
async function printAllVersions(){
  if(!state.builtVersions.length){setSaveStatus('Build versions first.','warn');return}
  let w;const btn=$('printAllVersionsBtn');if(btn)btn.disabled=true;
  try{w=openPrintWindowShell();setSaveStatus(`Preparing all ${state.builtVersions.length} versions for one print job…`,'');const pages=await allVersionPages();const t=document.createElement('template');t.innerHTML=pages;const pageCount=t.content.querySelectorAll('.paper-page').length;writePrintWindow(w,wrapStoredStudentDocument(pages,'All Versions'));setSaveStatus(`Opened one ${pageCount}-page print file containing all ${state.builtVersions.length} versions.`,'good')}
  catch(err){if(w&&!w.closed)w.close();setSaveStatus(`Could not prepare all versions: ${err.message}`,'warn')}
  finally{if(btn)btn.disabled=!state.builtVersions.length}
}


function setSaveStatus(message,kind=''){
  const el=$('saveStatus');if(!el)return;el.textContent=message;el.className=`save-status ${kind}`.trim();
}
function versionQuestionRecords(versionIndex){
  const vals=[...state.selected.values()],byId=new Map(vals.map(x=>[x.f.family_id,x]));
  const built=state.builtVersions[versionIndex-1];
  if(!built)return [];
  const savedOrder=state.practiceLayoutState?.order?.[String(versionIndex)],order=Array.isArray(savedOrder)&&savedOrder.length?savedOrder:built.order;
  return order.map((fid,i)=>{
    const x=byId.get(fid),inst=built.instances.get(fid)||x?.baseInstance||exemplarInstance(x),layout=practiceLayoutValues(versionIndex,fid);
    return {
      number:i+1,
      family_id:fid,
      teacher_question_id:qidFor(fid),
      i_can_id:x?.ic?.i_can_id||'',
      family_name:x?.f?.family_name||'',
      student_html:rewriteRelativeResources(inst?.student_html||''),
      answer:inst?.answer||'',
      solution:inst?.solution||'',
      figure_size:practiceFigurePxFromPercent(layout.figure),
      figure_percent:Number(layout.figure||0),
      work_size:Number(layout.workspace||0)
    };
  });
}
function storedPageCss(){return `@page{size:letter;margin:0}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#182230;margin:0;background:#eef1f5}.paper-page{width:8.5in;height:11in;padding:.45in .55in;background:#fff;margin:18px auto;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.16);page-break-after:always;break-after:page}.paper-page:last-child{page-break-after:auto}.paper-head{display:flex;justify-content:space-between;gap:20px;border-bottom:2px solid #182230;padding-bottom:8px;margin-bottom:14px;min-height:.58in}.paper-head div{display:flex;flex-direction:column;gap:4px}.paper-head span{font-size:.8rem}.paper-body{height:9.35in;overflow:hidden}.workspace-question{border-bottom:1px solid #dde2e8;padding:10px 0 16px;margin:0 0 8px;break-inside:avoid}.workspace-question-head{font-size:.78rem;font-weight:800;color:#566474;margin-bottom:7px}.workspace-question>.plc-figure{width:min(100%,var(--plc-figure-width,260px));max-width:100%;margin:7px auto 3px}.workspace-question>.plc-figure img,.workspace-question>.plc-figure svg,.workspace-question>.plc-figure canvas{display:block;width:100%!important;max-width:100%!important;height:auto!important;margin:0 auto}.workspace-question>.plc-workspace{height:var(--plc-workspace-height,0px);background:#fff}.choices{list-style-type:upper-alpha}.response-surface{background:#fff}.page-break-label,.page-overflow-warning{display:none}.data-table,.workspace-question table{border-collapse:collapse;margin:12px 0}.data-table th,.data-table td,.workspace-question table th,.workspace-question table td{border:1px solid #556170;padding:7px 12px;text-align:center;min-width:54px}.data-table th,.workspace-question table th{font-weight:800;background:#f2f4f7}@media print{html,body{margin:0!important;padding:0!important;background:#fff!important}.paper-page{width:8.5in!important;height:11in!important;margin:0!important;padding:.45in .55in!important;box-shadow:none!important;border:0!important;zoom:1!important;transform:none!important;break-after:page!important;page-break-after:always!important}.paper-page:last-child{break-after:auto!important;page-break-after:auto!important}}`;}
function wrapStoredStudentDocument(pageHtml,versionIndex){
  const label=String(versionIndex)==='All Versions'?'All Versions':`Version ${versionIndex}`;
  const title=`Algebra 1 · ${displayTitle()} · ${label}`;
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><script>window.MathJax={tex:{inlineMath:[["\\(","\\)"],["$","$"]],displayMath:[["\\[","\\]"]],processEscapes:true}};<\/script><script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"><\/script><style>${storedPageCss()}</style></head><body>${pageHtml}</body></html>`;
}
function wrapStoredKeyDocument(records,versionIndex){
  const title=`Algebra 1 · ${displayTitle()} · Version ${versionIndex} Key`;
  const rows=records.map(q=>`<section class="key-item"><h2>${q.number}. <span>${esc(q.teacher_question_id)} · ${esc(q.i_can_id)}</span></h2><div class="key-question">${q.student_html}</div><p><strong>Answer:</strong> ${esc(q.answer)}</p>${q.solution?`<p><strong>Short solution:</strong> ${esc(q.solution)}</p>`:''}</section>`).join('');
  const css=`body{font-family:Arial,Helvetica,sans-serif;color:#182230;max-width:8in;margin:24px auto;padding:0 20px}header{border-bottom:2px solid #182230;margin-bottom:18px}h1{margin-bottom:4px}.key-item{border-bottom:1px solid #ccd3dc;padding:14px 0;break-inside:avoid}.key-item h2{font-size:1rem}.key-item h2 span{font-size:.8rem;color:#667085}.key-question{margin:8px 0}.key-question img,.key-question svg{max-width:320px;height:auto}.data-table,.key-question table{border-collapse:collapse;margin:10px 0}.data-table th,.data-table td,.key-question table th,.key-question table td{border:1px solid #556170;padding:6px 10px;text-align:center}.choices{list-style-type:upper-alpha}@media print{@page{size:letter;margin:.55in}body{margin:0;max-width:none}}`;
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><script>window.MathJax={tex:{inlineMath:[["\\(","\\)"],["$","$"]],displayMath:[["\\[","\\]"]],processEscapes:true}};<\/script><script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"><\/script><style>${css}</style></head><body><header><h1>${esc(title)}</h1><p>Teacher key · bank revision ${esc(state.manifest?.content_revision??'?')}</p></header>${rows}</body></html>`;
}
async function captureVersionPages(versionIndex){
  const original=state.activeVersion;state.activeVersion=versionIndex;
  await renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap());
  const html=printablePageSnapshot();
  state.activeVersion=original;
  await renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap());
  renderVersionTabs();
  return html;
}
async function saveFinishedBuild(){
  if(!state.builtVersions.length){setSaveStatus('Build the requested versions first.','warn');return;}
  const btn=$('saveBtn');btn.disabled=true;setSaveStatus('Preparing all versions and keys…','');
  try{
    const versions=[],allPages=[];
    for(let v=1;v<=state.builtVersions.length;v++){
      const records=versionQuestionRecords(v);
      const pages=await captureVersionPages(v);allPages.push(pages);
      versions.push({version:v,base_filename:baseFilename(v),student_html:wrapStoredStudentDocument(pages,v),key_html:wrapStoredKeyDocument(records,v),questions:records});
    }
    const combinedHtml=wrapStoredStudentDocument(allPages.join(''),'All Versions');
    const payload={schema_version:1,product:state.product,unit:1,item_label:$('itemLabel').value.trim(),custom_name:customName(),display_title:displayTitle(),save_target:state.saveTarget,bank_revision:state.manifest?.content_revision??null,versions,combined_student_html:combinedHtml,combined_base_filename:combinedBaseFilename()};
    setSaveStatus(state.saveTarget==='local'?'Saving local copies…':'Saving and publishing through Curriculum Transfer…','');
    const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await r.json().catch(()=>({}));
    if(!r.ok||!data.ok)throw new Error(data.error||`Save failed (${r.status})`);
    const parts=[];if(data.local_path)parts.push(`Local: ${data.local_path}`);if(data.library_url)parts.push(`Teacher Library: ${data.library_url}`);
    setSaveStatus(`Saved successfully. ${parts.join(' · ')}`,'good');
  }catch(err){setSaveStatus(`Save failed: ${err.message}`,'error')}
  finally{btn.disabled=!state.builtVersions.length}
}

function isCheckpoint(){return state.product==='Checkpoint'}
function setCheckpointStatus(message,kind=''){
  const el=$('checkpointStatus');if(!el)return;el.textContent=message;el.className=`checkpoint-status ${kind}`.trim();
}
function checkpointScopeIdsForUnit(unit){
  const out=[];for(const u of state.checkpointEligibility?.units||[])if(Number(u.unit)===Number(unit))for(const mg of u.mastery_goals||[])for(const ic of mg.i_cans||[])out.push(ic.i_can_id);return out;
}
function checkpointScopeIdsForMg(mgid){
  const out=[];for(const u of state.checkpointEligibility?.units||[])for(const mg of u.mastery_goals||[])if(mg.mg_id===mgid)for(const ic of mg.i_cans||[])out.push(ic.i_can_id);return out;
}
function checkpointAllScopeIds(){
  return (state.checkpointEligibility?.units||[]).flatMap(u=>(u.mastery_goals||[]).flatMap(mg=>(mg.i_cans||[]).map(ic=>ic.i_can_id)));
}
function setScopeGroup(ids,on){
  ids.forEach(id=>on?state.checkpointEligibleIcanIds.add(id):state.checkpointEligibleIcanIds.delete(id));renderCheckpointEligibility();saveDraft();
}
function selectAllCheckpointScope(){
  state.checkpointEligibleIcanIds=new Set(checkpointAllScopeIds());renderCheckpointEligibility();saveDraft();setCheckpointStatus('All available I Can statements are eligible. Uncheck anything you do not want considered for this checkpoint.','');
}
function clearCheckpointScope(){
  state.checkpointEligibleIcanIds.clear();renderCheckpointEligibility();saveDraft();setCheckpointStatus('Choose the I Can statements that are fair game for this checkpoint.','');
}
function updateCheckpointScopeSummary(){
  const el=$('checkpointScopeSummary');if(!el)return;
  const ids=[...state.checkpointEligibleIcanIds];
  const selectedMgs=new Set(),selectedUnits=new Set();
  for(const id of ids){
    const m=String(id).match(/^(U\d+-MG\d+)-IC\d+$/);if(!m)continue;
    selectedMgs.add(m[1]);const um=m[1].match(/^U(\d+)-/);if(um)selectedUnits.add(`U${Number(um[1])}`);
  }
  const students=Number(state.checkpointEligibility?.student_count||0),records=Number(state.checkpointEligibility?.evidence_record_count||0);
  el.innerHTML=`<strong>${ids.length} I Can${ids.length===1?'':'s'} selected</strong><span>${selectedMgs.size} MG${selectedMgs.size===1?'':'s'} · ${selectedUnits.size} unit${selectedUnits.size===1?'':'s'}</span><span>${students} Portfolio student${students===1?'':'s'} · ${records} evidence records</span>`;
  $('analyzeCheckpointBtn').disabled=state.checkpointBusy||ids.length===0;
}
function renderCheckpointEligibility(){
  const host=$('checkpointEligibility');if(!host)return;
  const data=state.checkpointEligibility;
  if(!data){host.innerHTML='<div class="checkpoint-empty">Loading eligible I Can statements…</div>';updateCheckpointScopeSummary();return}
  const units=data.units||[];
  if(!units.length){host.innerHTML='<div class="checkpoint-empty">No Algebra I Can statements were found in the current Portfolio/bank data.</div>';updateCheckpointScopeSummary();return}
  host.innerHTML=units.map(u=>{
    const groups=(u.mastery_goals||[]).map(mg=>{
      const items=(mg.i_cans||[]).map(ic=>{
        const checked=state.checkpointEligibleIcanIds.has(ic.i_can_id);
        const text=ic.exact_text?` · ${esc(ic.exact_text)}`:'';
        const meta=[];if(Number(ic.evidence_student_count||0))meta.push(`${Number(ic.evidence_student_count)} students in Portfolio`);if(Number(ic.bank_family_count||0))meta.push(`${Number(ic.bank_family_count)} bank families`);
        return `<label class="checkpoint-ican-pick"><input type="checkbox" data-scope-ican="${esc(ic.i_can_id)}" ${checked?'checked':''}><span><strong>${esc(ic.i_can_id)}</strong>${text}</span>${meta.length?`<small>${esc(meta.join(' · '))}</small>`:''}</label>`;
      }).join('');
      return `<section class="checkpoint-mg-group"><div class="checkpoint-mg-title"><strong>${esc(mg.mg_id)}</strong>${mg.title?` · ${esc(mg.title)}`:''}</div><div class="checkpoint-ican-picks">${items}</div></section>`;
    }).join('');
    return `<section class="checkpoint-unit"><div class="checkpoint-unit-title">Unit ${Number(u.unit)}</div>${groups}</section>`;
  }).join('');
  host.querySelectorAll('[data-scope-ican]').forEach(cb=>cb.onchange=()=>{
    const id=cb.dataset.scopeIcan;if(!id)return;
    if(cb.checked)state.checkpointEligibleIcanIds.add(id);else state.checkpointEligibleIcanIds.delete(id);
    updateCheckpointScopeSummary();saveDraft();
  });
  updateCheckpointScopeSummary();
}
async function loadCheckpointEligibility(force=false){
  if(state.checkpointScopeLoaded&&!force){renderCheckpointEligibility();return}
  const host=$('checkpointEligibility');if(host)host.innerHTML='<div class="checkpoint-empty">Reading Portfolio and available Algebra banks…</div>';
  try{
    const r=await fetch('/api/checkpoint/eligibility',{cache:'no-store'});const data=await r.json().catch(()=>({}));
    if(!r.ok||!data.ok)throw new Error(data.error||`Scope load failed (${r.status})`);
    state.checkpointEligibility=data;state.checkpointScopeLoaded=true;
    const available=new Set((data.units||[]).flatMap(u=>(u.mastery_goals||[]).flatMap(mg=>(mg.i_cans||[]).map(ic=>ic.i_can_id))));
    state.checkpointEligibleIcanIds=new Set([...state.checkpointEligibleIcanIds].filter(id=>available.has(id)));
    renderCheckpointEligibility();
    if(!state.checkpointEligibleIcanIds.size)setCheckpointStatus('Select the I Can statements that are eligible for this checkpoint. Portfolio status outside those I Cans will be ignored.','');
  }catch(err){
    state.checkpointScopeLoaded=false;if(host)host.innerHTML=`<div class="checkpoint-empty">Could not load eligible evidence scope: ${esc(err.message)}</div>`;setCheckpointStatus(`Could not load Checkpoint scope: ${err.message}`,'error');updateCheckpointScopeSummary();
  }
}
function checkpointStudentCard(s,target=6){
  const reassess=s.reassessment_slots||[],missing=s.reassessment_family_requests||[];
  const needs=[...reassess.map(x=>({code:x.i_can_id||'',missing:false})),...missing.map(x=>({code:x.i_can_id||'',missing:true}))];
  const extCount=Math.max(0,Number(s.extension_count||0));
  const slots=[];
  for(let i=1;i<=extCount;i++)slots.push({kind:'extension',label:`Extension ${i}`});
  needs.forEach((x,i)=>slots.push({kind:x.missing?'need missing':'need',label:x.code||`Need ${i+1}`}));
  while(slots.length<target)slots.push({kind:'open',label:'Open slot'});
  const shown=slots.slice(0,Math.max(target,slots.length));
  const rows=shown.map(x=>`<div class="checkpoint-spot-slot ${x.kind}">${esc(x.label)}</div>`).join('');
  return `<article class="checkpoint-student"><div class="checkpoint-student-head"><strong>${esc(s.student_display||s.student_key)}</strong></div><div class="checkpoint-spot-list">${rows}</div>${missing.length?`<div class="checkpoint-family-gap">${missing.length} reassessment need${missing.length===1?'':'s'} require${missing.length===1?'s':''} a temporary family.</div>`:''}</article>`;
}
function temporaryFamilyCard(f,valid=true){
  const fid=f.extension_family_id||f.family_id||'Temporary family';
  const decision=String(f.review_decision||'PENDING').toUpperCase();
  const kind=String(f.slot_kind||'');
  const extIndex=Number(f.extension_index||0);
  const kindLabel=kind==='extension'?`Extension ${extIndex||''}`.trim():`Reassessment · ${(f.target_i_can_ids||[]).join(', ')||'target'}`;
  const targets=(f.target_i_can_ids||[]).map(x=>`<span>${esc(x)}</span>`).join('');
  const assigned=(f.assigned_student_keys||[]).length;
  const ex=f.exemplar||{};
  const studentHtml=String(ex.student_html||'');
  const disabled=valid?'':'disabled';
  return `<article class="checkpoint-family-card decision-${esc(decision.toLowerCase())}" data-temp-family="${esc(fid)}">
    <div class="checkpoint-family-card-head"><div><span class="checkpoint-family-kind">${esc(kindLabel)}</span><h4>${esc(f.family_name||fid)}</h4></div><span class="checkpoint-family-decision">${esc(decision==='PENDING'?'Pending':decision==='ACCEPT'?'Accepted':'Replace')}</span></div>
    <div class="checkpoint-family-meta">${targets}<span>${assigned} student${assigned===1?'':'s'}</span></div>
    ${f.family_purpose?`<p class="checkpoint-family-purpose">${esc(f.family_purpose)}</p>`:''}
    ${f.student_action?`<div class="checkpoint-family-action"><strong>Student action:</strong> ${esc(f.student_action)}</div>`:''}
    <div class="checkpoint-family-preview">${studentHtml||'<em>No exemplar preview supplied.</em>'}</div>
    <details class="checkpoint-family-key"><summary>Answer / solution</summary>${ex.answer?`<p><strong>Answer:</strong> ${esc(ex.answer)}</p>`:''}${ex.solution?`<p><strong>Solution:</strong> ${esc(ex.solution)}</p>`:''}${ex.scoring_guidance?`<p><strong>Scoring:</strong> ${esc(ex.scoring_guidance)}</p>`:''}</details>
    <div class="checkpoint-family-buttons"><button class="secondary ${decision==='ACCEPT'?'active':''}" data-family-decision="ACCEPT" data-family-id="${esc(fid)}" ${disabled}>Accept</button><button class="secondary replace ${decision==='REPLACE'?'active':''}" data-family-decision="REPLACE" data-family-id="${esc(fid)}" ${disabled}>Replace</button></div>
  </article>`;
}
function renderCheckpointFamilyReview(response,review,validation,replacementUrl=null){
  const section=$('checkpointFamilyReview'),cards=$('checkpointFamilyCards'),summary=$('checkpointFamilyReviewSummary'),acceptAll=$('acceptAllTemporaryFamiliesBtn'),replacement=$('downloadReplacementRequestBtn');
  if(!section||!cards||!summary||!acceptAll||!replacement)return;
  if(!response||!Array.isArray(response.extension_families)){
    section.hidden=true;cards.innerHTML='';summary.innerHTML='';replacement.hidden=true;return;
  }
  section.hidden=false;
  const families=[...(response.extension_families||[])].sort((a,b)=>{const ak=String(a.slot_kind||'')==='extension'?0:1,bk=String(b.slot_kind||'')==='extension'?0:1;if(ak!==bk)return ak-bk;if(ak===0)return Number(a.extension_index||0)-Number(b.extension_index||0);return String((a.target_i_can_ids||[])[0]||'').localeCompare(String((b.target_i_can_ids||[])[0]||''),undefined,{numeric:true})});
  const complete=validation?.complete!==false;
  const accepted=Number(review?.accepted_count||0),replaceCount=Number(review?.replace_count||0),pending=Number(review?.pending_count??families.filter(f=>!f.review_decision||f.review_decision==='PENDING').length);
  const errors=validation?.errors||[],warnings=validation?.warnings||[];
  summary.innerHTML=`<strong>${families.length} returned famil${families.length===1?'y':'ies'}</strong><span>${accepted} accepted</span><span>${pending} pending</span><span>${replaceCount} replace</span>${errors.length?`<span class="bad">${errors.length} response error${errors.length===1?'':'s'}</span>`:''}${warnings.length?`<span>${warnings.length} warning${warnings.length===1?'':'s'}</span>`:''}`;
  cards.innerHTML=families.map(f=>temporaryFamilyCard(f,complete)).join('');
  cards.querySelectorAll('[data-family-decision]').forEach(btn=>btn.onclick=()=>reviewCheckpointFamily(btn.dataset.familyId,btn.dataset.familyDecision));
  acceptAll.disabled=!complete||!families.length||pending===0||replaceCount>0;
  replacement.hidden=replaceCount===0;
  replacement.href='#';replacement.removeAttribute('download');replacement.onclick=null;
  if(replaceCount){replacement.onclick=(event)=>{event.preventDefault();saveCheckpointReplacementRequest()}}
  if(errors.length){
    const text=errors.slice(0,3).join(' ');setCheckpointStatus(`Returned family file needs correction before approval. ${text}`,'error');
  }else if(review?.all_accepted){
    setCheckpointStatus('All temporary families are accepted. The evidence plan and family set are locked; student checkpoint assembly is the next phase.','good');
  }else if(replaceCount){
    setCheckpointStatus(`${replaceCount} temporary famil${replaceCount===1?'y is':'ies are'} marked Replace. Save the replacement request ZIP, upload it to Curriculum Build, apply the returned transfer, then click Load Returned Families.`,'warn');
  }else{
    setCheckpointStatus(`Returned temporary families are ready for review. Accept each family or mark it Replace before checkpoint assembly.`,'good');
  }
  typeset();
}
async function reviewCheckpointFamily(familyId,decision){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  setCheckpointStatus(decision==='ACCEPT'?'Saving family approval…':'Marking family for replacement…','');
  try{
    const r=await fetch('/api/checkpoint/family-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:planId,family_id:familyId,decision})});
    const data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Family review failed (${r.status})`);
    renderCheckpointPlan(data.plan,!!data.extensions_ready,data.request_url||null,data.extension_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);
  }catch(err){setCheckpointStatus(`Could not save temporary-family review: ${err.message}`,'error')}
}
async function acceptAllTemporaryFamilies(){
  await reviewCheckpointFamily('*','ACCEPT');
}
function assembledStudentCard(s,planId){
  const slots=(s.slots||[]).map(x=>`<div class="checkpoint-assembled-slot ${x.kind==='extension'?'extension':''}">${esc(x.label||x.family_name||'Question')}</div>`).join('');
  const href=`/api/checkpoint/student.html?plan_id=${encodeURIComponent(planId)}&student_key=${encodeURIComponent(s.student_key||'')}`;
  return `<article class="checkpoint-assembled-student"><div class="checkpoint-assembled-student-head"><strong>${esc(s.student_display||s.student_key)}</strong><a href="${href}" target="_blank" rel="noopener">Preview Form</a></div><div class="checkpoint-assembled-student-slots">${slots}</div></article>`;
}
function renderCheckpointAssembly(plan,familyReview,responseValidation,assembly=null){
  const section=$('checkpointAssembly'),assemble=$('assembleCheckpointBtn'),status=$('checkpointAssemblyStatus'),summary=$('checkpointAssemblySummary'),actions=$('checkpointOutputActions'),students=$('checkpointAssemblyStudents');
  if(!section||!assemble||!status||!summary||!actions||!students)return;
  const requestFamilies=Number(plan?.temporary_family_request_count??plan?.temporary_family_request_slot_count??0);
  const unlocked=!!plan && (requestFamilies===0 || (responseValidation?.complete!==false && familyReview?.all_accepted===true));
  section.hidden=!unlocked;
  if(!unlocked){state.checkpointAssembly=null;summary.hidden=true;actions.hidden=true;students.innerHTML='';return}
  state.checkpointAssembly=assembly||null;assemble.disabled=false;
  if(!assembly){
    assemble.textContent='Assemble Student Checkpoints';status.className='checkpoint-status';status.textContent='Family review is complete. Assemble the individualized student forms when ready.';summary.hidden=true;actions.hidden=true;students.innerHTML='';return;
  }
  assemble.textContent='Rebuild Student Checkpoints';status.className='checkpoint-status good';status.textContent='Student Checkpoints are assembled as two-page duplex forms. Open Class Packet for the left-side student controls and manual question adjustments.';
  const count=Number(assembly.student_count||0),questions=Number(assembly.question_count_total||0);
  summary.hidden=false;summary.innerHTML=`<strong>${count} student form${count===1?'':'s'}</strong><span>2 pages per student · duplex-ready</span><span>${questions} total question placements</span><span>${Number(assembly.extension_question_count||0)} labeled Extension</span><span>${Number(assembly.reassessment_question_count||0)} reassessment</span>`;
  const pid=encodeURIComponent(plan.plan_id);actions.hidden=false;$('openClassPacketBtn').href=`/api/checkpoint/class-packet.html?plan_id=${pid}`;$('openTeacherKeyBtn').href=`/api/checkpoint/teacher-key.html?plan_id=${pid}`;$('downloadCheckpointZipBtn').href=`/api/checkpoint/output.zip?plan_id=${pid}`;$('downloadCheckpointZipBtn').setAttribute('download','');
  students.innerHTML=(assembly.student_forms||[]).map(s=>assembledStudentCard(s,plan.plan_id)).join('');
}
function renderCheckpointPlan(plan,extensionsReady=false,requestUrl=null,extensionResponse=null,familyReview=null,responseValidation=null,replacementUrl=null,assembly=null){
  if(plan)state.suppressLatestRestore=false;
  state.checkpointPlan=plan||null;state.checkpointPlanId=plan?.plan_id||state.checkpointPlanId;state.checkpointExtensionsReady=!!extensionsReady;
  const sum=$('checkpointSummary'),students=$('checkpointStudents'),refresh=$('refreshCheckpointBtn'),saveRequest=$('saveExtensionRequestBtn');
  if(!plan){sum.hidden=true;students.innerHTML='';refresh.disabled=true;saveRequest.hidden=true;renderCheckpointFamilyReview(null,null,null,null);renderCheckpointAssembly(null,null,null,null);return}
  if(Number(plan.schema_version||1)>=2&&Array.isArray(plan.eligible_i_cans)){
    state.checkpointEligibleIcanIds=new Set(plan.eligible_i_cans);renderCheckpointEligibility();
  }
  const studentCount=Number(plan.student_count||0),ext=Number(plan.extension_slot_count||0),missingSlots=Number(plan.missing_reassessment_family_slot_count||0),openSlots=Number(plan.temporary_family_request_slot_count??(ext+missingSlots)),requestFamilies=Number(plan.temporary_family_request_count??openSlots),extFamilies=Number(plan.extension_family_request_count??ext),missingFamilies=Number(plan.missing_reassessment_family_request_count??missingSlots),records=Number(plan.evidence_record_count||0),scopeIcans=(plan.eligible_i_cans||[]).length,scopeMgs=new Set((plan.eligible_i_cans||[]).map(id=>String(id).replace(/-IC\d{2}$/,''))).size;
  sum.hidden=false;sum.innerHTML=`<strong>${studentCount} student${studentCount===1?'':'s'} in plan</strong><span>${scopeIcans} eligible I Can${scopeIcans===1?'':'s'} · ${scopeMgs} MG${scopeMgs===1?'':'s'}</span><span>${records} Portfolio current-status records</span><span>${Number(plan.reassessment_slot_count||0)} reassessment slot${Number(plan.reassessment_slot_count||0)===1?'':'s'}</span><span>${ext} extension slot${ext===1?'':'s'}</span>${missingSlots?`<span>${missingSlots} reassessment slot${missingSlots===1?'':'s'} need temporary family coverage</span>`:''}${requestFamilies?`<span>${requestFamilies} AI famil${requestFamilies===1?'y':'ies'} requested · ${extFamilies} extension + ${missingFamilies} reassessment</span>`:''}<span>Target: ${Number(plan.target_questions_per_student||6)} questions per student</span>`;
  students.innerHTML=(plan.students||[]).map(s=>checkpointStudentCard(s,Number(plan.target_questions_per_student||6))).join('');
  refresh.disabled=false;saveRequest.hidden=requestFamilies===0;
  renderCheckpointFamilyReview(extensionsReady?extensionResponse:null,familyReview,responseValidation,replacementUrl);
  renderCheckpointAssembly(plan,familyReview,responseValidation,assembly);
  if(!studentCount){
    setCheckpointStatus(`No students were recognized yet. ${plan.files_scanned?.length||0} current Portfolio state file(s) were scanned.`,'warn');
  }else if(requestFamilies===0){
    setCheckpointStatus('Checkpoint evidence plan is complete from current bank families. No temporary AI families are needed.','good');
  }else if(!extensionsReady){
    setCheckpointStatus(`Evidence plan created. ${openSlots} open student slot${openSlots===1?'':'s'} can be covered by ${requestFamilies} reusable temporary famil${requestFamilies===1?'y':'ies'}. Click Save AI Request, then upload that ZIP to Curriculum Build.`,'good');
  }
  saveDraft();
}

async function saveCheckpointRequest(){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  setCheckpointStatus('Opening Save dialog for the AI request…','');
  try{
    const r=await fetch(`/api/checkpoint/reveal-request?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'});const data=await r.json().catch(()=>({}));
    if(!r.ok||!data.ok)throw new Error(data.error||`Could not open Save dialog (${r.status})`);
    if(data.cancelled){setCheckpointStatus('AI request was not saved. Click Save AI Request when you are ready.','warn');return}
    setCheckpointStatus(`AI request saved as ${data.name||'request ZIP'} in the location you confirmed. Upload that ZIP to Curriculum Build.`,'good');
  }catch(err){setCheckpointStatus(`Could not save the AI request: ${err.message}`,'error')}
}
async function saveCheckpointReplacementRequest(){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  setCheckpointStatus('Opening Save dialog for the replacement request…','');
  try{const r=await fetch(`/api/checkpoint/save-replacement-request?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Could not open Save dialog (${r.status})`);if(data.cancelled){setCheckpointStatus('Replacement request was not saved.','warn');return}setCheckpointStatus(`Replacement request saved as ${data.name||'request ZIP'}. Upload that ZIP to Curriculum Build.`,'good')}catch(err){setCheckpointStatus(`Could not save the replacement request: ${err.message}`,'error')}
}
function freshCheckpointInstance(family){
  const fid=String(family?.family_id||'');
  if(!fid||!window.AssessmentGeneration?.supports?.(fid))return null;
  const exemplar=String(family?.exemplar?.student_html||'');
  let candidate=null;
  for(let i=0;i<8;i++){
    const next=window.AssessmentGeneration.generate(family);
    if(next?.student_html){candidate=next;if(String(next.student_html)!==exemplar)break}
  }
  return candidate;
}
function checkpointFreshInstances(plan){
  const out=[];
  for(const student of plan?.students||[]){
    for(const record of student.reassessment_slots||[]){
      const family=record?.family;if(!family?.family_id)continue;
      const instance=freshCheckpointInstance(family);
      if(!instance)continue;
      out.push({student_key:String(student.student_key||''),family_id:String(family.family_id||''),i_can_id:String(record.i_can_id||family.i_can_id||''),instance});
    }
  }
  return out;
}
async function assembleCheckpoint(){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  const btn=$('assembleCheckpointBtn');btn.disabled=true;$('checkpointAssemblyStatus').className='checkpoint-status';$('checkpointAssemblyStatus').textContent='Generating fresh approved-family instances and assembling two-page student forms…';
  try{
    const fresh_instances=checkpointFreshInstances(state.checkpointPlan);
    const r=await fetch('/api/checkpoint/assemble',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:planId,fresh_instances})});const data=await r.json().catch(()=>({}));
    if(!r.ok||!data.ok)throw new Error(data.error||`Assembly failed (${r.status})`);
    renderCheckpointPlan(data.plan,!!data.extensions_ready,data.request_url||null,data.extension_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);
  }catch(err){$('checkpointAssemblyStatus').className='checkpoint-status error';$('checkpointAssemblyStatus').textContent=`Could not assemble Checkpoint: ${err.message}`;btn.disabled=false}
}
async function openCheckpointOutputFolder(){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  try{const r=await fetch(`/api/checkpoint/reveal-output?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'});const data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Could not open output folder (${r.status})`)}catch(err){$('checkpointAssemblyStatus').className='checkpoint-status error';$('checkpointAssemblyStatus').textContent=`Could not open output folder: ${err.message}`}
}

async function analyzeCheckpoint(){
  if(state.checkpointBusy)return;
  const eligible=[...state.checkpointEligibleIcanIds].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
  if(!eligible.length){setCheckpointStatus('Select at least one eligible I Can statement first.','warn');return}
  state.checkpointBusy=true;
  const btn=$('analyzeCheckpointBtn');btn.disabled=true;setCheckpointStatus('Reading current Portfolio status only inside the I Can statements you selected…','');
  try{
    const payload={unit:Number($('unitSelect')?.value||1),item_label:$('itemLabel').value.trim(),custom_name:customName(),target_questions:Number($('checkpointQuestionCount').value||6),eligible_i_cans:eligible};
    const r=await fetch('/api/checkpoint/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Analysis failed (${r.status})`);
    renderCheckpointPlan(data.plan,!!data.extensions_ready,data.request_url||null,data.extension_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);
  }catch(err){setCheckpointStatus(`Checkpoint analysis failed: ${err.message}`,'error')}
  finally{state.checkpointBusy=false;updateCheckpointScopeSummary()}
}
async function refreshCheckpoint(){
  const planId=state.checkpointPlanId||state.checkpointPlan?.plan_id;if(!planId)return;
  setCheckpointStatus('Checking for returned temporary families…','');
  try{
    const r=await fetch(`/api/checkpoint/status?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'});const data=await r.json().catch(()=>({}));
    if(!r.ok||!data.ok)throw new Error(data.error||`Refresh failed (${r.status})`);
    if(!data.found)throw new Error('The local checkpoint plan was not found.');
    renderCheckpointPlan(data.plan,!!data.extensions_ready,data.request_url||null,data.extension_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);
    if(!data.extensions_ready&&Number(data.plan?.temporary_family_request_slot_count ?? data.plan?.extension_slot_count ?? 0)>0)setCheckpointStatus('Still waiting for the returned temporary-family transfer. Apply it, then click Load Returned Families.','warn');
  }catch(err){setCheckpointStatus(`Could not refresh Checkpoint: ${err.message}`,'error')}
}
async function restoreLatestCheckpoint(){
  if(state.suppressLatestRestore&&!state.checkpointPlanId)return;
  if(!isCheckpoint())return;
  try{
    const planId=state.checkpointPlanId;
    const url=planId?`/api/checkpoint/status?plan_id=${encodeURIComponent(planId)}`:'/api/checkpoint/latest';
    const r=await fetch(url,{cache:'no-store'});const data=await r.json().catch(()=>({}));
    if(r.ok&&data.ok&&data.found&&data.plan&&Number(data.plan.schema_version||1)>=2)renderCheckpointPlan(data.plan,!!data.extensions_ready,data.request_url||null,data.extension_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);
  }catch(_){ }
}
function isSummative(){return state.product==='Summative'}
function setSummativeStatus(message,kind=''){
  const el=$('summativeStatus');if(!el)return;el.textContent=message;el.className=`checkpoint-status ${kind}`.trim();
}
function summativeAllScopeIds(){return (state.summativeEligibility?.units||[]).flatMap(u=>(u.mastery_goals||[]).flatMap(mg=>(mg.i_cans||[]).map(ic=>ic.i_can_id)))}
function selectAllSummativeScope(){state.summativeEligibleIcanIds=new Set(summativeAllScopeIds());renderSummativeEligibility();saveDraft();setSummativeStatus('All available I Can statements are eligible. Uncheck anything you do not want considered for this Summative.','')}
function clearSummativeScope(){state.summativeEligibleIcanIds.clear();renderSummativeEligibility();saveDraft();setSummativeStatus('Choose at least four I Can statements that are fair game for this Summative.','')}
function updateSummativeScopeSummary(){
  const el=$('summativeScopeSummary');if(!el)return;
  const ids=[...state.summativeEligibleIcanIds],mgs=new Set(),units=new Set();
  ids.forEach(id=>{const m=String(id).match(/^(U\d+-MG\d+)-IC\d+$/);if(m){mgs.add(m[1]);const u=m[1].match(/^U(\d+)-/);if(u)units.add(`U${Number(u[1])}`)}});
  const students=Number(state.summativeEligibility?.student_count||0),records=Number(state.summativeEligibility?.evidence_record_count||0);
  el.innerHTML=`<strong>${ids.length} I Can${ids.length===1?'':'s'} selected</strong><span>${mgs.size} MG${mgs.size===1?'':'s'} · ${units.size} unit${units.size===1?'':'s'}</span><span>${students} Portfolio student${students===1?'':'s'} · ${records} current-status records</span>`;
  $('analyzeSummativeBtn').disabled=state.summativeBusy||ids.length<4;
}
function renderSummativeEligibility(){
  const host=$('summativeEligibility');if(!host)return;const data=state.summativeEligibility;
  if(!data){host.innerHTML='<div class="checkpoint-empty">Loading eligible I Can statements…</div>';updateSummativeScopeSummary();return}
  const units=data.units||[];if(!units.length){host.innerHTML='<div class="checkpoint-empty">No Algebra I Can statements were found in the current Portfolio/bank data.</div>';updateSummativeScopeSummary();return}
  host.innerHTML=units.map(u=>`<section class="checkpoint-unit"><div class="checkpoint-unit-title">Unit ${Number(u.unit)}</div>${(u.mastery_goals||[]).map(mg=>`<section class="checkpoint-mg-group"><div class="checkpoint-mg-title"><strong>${esc(mg.mg_id)}</strong>${mg.title?` · ${esc(mg.title)}`:''}</div><div class="checkpoint-ican-picks">${(mg.i_cans||[]).map(ic=>{const checked=state.summativeEligibleIcanIds.has(ic.i_can_id),text=ic.exact_text?` · ${esc(ic.exact_text)}`:'',meta=[];if(Number(ic.evidence_student_count||0))meta.push(`${Number(ic.evidence_student_count)} students in Portfolio`);if(Number(ic.bank_family_count||0))meta.push(`${Number(ic.bank_family_count)} bank families`);return `<label class="checkpoint-ican-pick"><input type="checkbox" data-summative-ican="${esc(ic.i_can_id)}" ${checked?'checked':''}><span><strong>${esc(ic.i_can_id)}</strong>${text}</span>${meta.length?`<small>${esc(meta.join(' · '))}</small>`:''}</label>`}).join('')}</div></section>`).join('')}</section>`).join('');
  host.querySelectorAll('[data-summative-ican]').forEach(cb=>cb.onchange=()=>{const id=cb.dataset.summativeIcan;if(!id)return;if(cb.checked)state.summativeEligibleIcanIds.add(id);else state.summativeEligibleIcanIds.delete(id);updateSummativeScopeSummary();saveDraft()});
  updateSummativeScopeSummary();
}
async function loadSummativeEligibility(force=false){
  if(state.summativeScopeLoaded&&!force){renderSummativeEligibility();return}
  const host=$('summativeEligibility');if(host)host.innerHTML='<div class="checkpoint-empty">Reading Portfolio and available Algebra banks…</div>';
  try{const r=await fetch('/api/summative/eligibility',{cache:'no-store'}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Scope load failed (${r.status})`);state.summativeEligibility=data;state.summativeScopeLoaded=true;const available=new Set((data.units||[]).flatMap(u=>(u.mastery_goals||[]).flatMap(mg=>(mg.i_cans||[]).map(ic=>ic.i_can_id))));state.summativeEligibleIcanIds=new Set([...state.summativeEligibleIcanIds].filter(id=>available.has(id)));renderSummativeEligibility();if(!state.summativeEligibleIcanIds.size)setSummativeStatus('Select at least four I Can statements. Portfolio will choose each student’s four least-secure targets inside that scope.','')}
  catch(err){state.summativeScopeLoaded=false;if(host)host.innerHTML=`<div class="checkpoint-empty">Could not load eligible evidence scope: ${esc(err.message)}</div>`;setSummativeStatus(`Could not load Summative scope: ${err.message}`,'error');updateSummativeScopeSummary()}
}
function summativeStudentCard(s,target=4){
  const needs=(s.reassessment_slots||[]).map(x=>x.i_can_id||'');const ext=Math.max(0,Number(s.extension_count||0));const slots=[];needs.forEach(code=>slots.push({kind:'need',label:code}));for(let i=1;i<=ext;i++)slots.push({kind:'extension',label:`Extension ${i}`});while(slots.length<target)slots.push({kind:'open',label:'Open slot'});return `<article class="checkpoint-student"><div class="checkpoint-student-head"><strong>${esc(s.student_display||s.student_key)}</strong></div><div class="checkpoint-spot-list">${slots.slice(0,target).map(x=>`<div class="checkpoint-spot-slot ${x.kind}">${esc(x.label)}</div>`).join('')}</div></article>`;
}
function summativeFamilyCard(f,decision='PENDING',valid=true){
  const fid=f.family_id||'Temporary family',kind=String(f.slot_kind||''),targets=(f.target_i_can_ids||[]),assigned=(f.assigned_student_keys||[]).length,ex=f.exemplar||{},disabled=valid?'':'disabled';
  const label=kind==='extension_mc'?'Extension MC':`Reassessment MC · ${targets.join(', ')||'target'}`;
  return `<article class="checkpoint-family-card decision-${esc(String(decision).toLowerCase())}" data-sum-family="${esc(fid)}"><div class="checkpoint-family-card-head"><div><span class="checkpoint-family-kind">${esc(label)}</span><h4>${esc(f.family_name||fid)}</h4></div><span class="checkpoint-family-decision">${esc(decision==='ACCEPT'?'Accepted':decision==='REPLACE'?'Replace':'Pending')}</span></div><div class="checkpoint-family-meta">${targets.map(x=>`<span>${esc(x)}</span>`).join('')}<span>${assigned} student${assigned===1?'':'s'}</span></div>${f.family_purpose?`<p class="checkpoint-family-purpose">${esc(f.family_purpose)}</p>`:''}<div class="checkpoint-family-preview">${String(ex.student_html||'<em>No exemplar preview supplied.</em>')}</div><details class="checkpoint-family-key"><summary>Answer / solution</summary>${ex.answer?`<p><strong>Answer:</strong> ${esc(ex.answer)}</p>`:''}${ex.solution?`<p><strong>Solution:</strong> ${esc(ex.solution)}</p>`:''}</details><div class="checkpoint-family-buttons"><button class="secondary ${decision==='ACCEPT'?'active':''}" data-sum-decision="ACCEPT" data-sum-id="${esc(fid)}" ${disabled}>Accept</button><button class="secondary replace ${decision==='REPLACE'?'active':''}" data-sum-decision="REPLACE" data-sum-id="${esc(fid)}" ${disabled}>Replace</button></div></article>`;
}
function renderSummativeFamilyReview(response,review,validation,replacementUrl=null){
  const section=$('summativeFamilyReview'),cards=$('summativeFamilyCards'),summary=$('summativeFamilyReviewSummary'),replacement=$('downloadSummativeReplacementBtn'),next=$('summativeNextPhase');
  if(!response){section.hidden=true;next.hidden=true;cards.innerHTML='';return}
  section.hidden=false;const families=validation?.families||response.summative_families||[],decisions=review?.decisions||{},valid=validation?.complete!==false;
  const accepted=families.filter(f=>decisions[f.family_id]==='ACCEPT').length,replaceCount=families.filter(f=>decisions[f.family_id]==='REPLACE').length,pending=Math.max(0,families.length-accepted-replaceCount);
  summary.innerHTML=`<strong>${families.length} returned families</strong><span>${accepted} accepted</span><span>${pending} pending</span><span>${replaceCount} replace</span>`;
  cards.innerHTML=families.map(f=>summativeFamilyCard(f,decisions[f.family_id]||'PENDING',valid)).join('');cards.querySelectorAll('[data-sum-decision]').forEach(btn=>btn.onclick=()=>reviewSummativeFamily(btn.dataset.sumId,btn.dataset.sumDecision));
  replacement.hidden=!replacementUrl;replacement.href='#';replacement.removeAttribute('download');replacement.onclick=null;if(replacementUrl)replacement.onclick=(event)=>{event.preventDefault();saveSummativeReplacementRequest()};next.hidden=!(valid&&families.length&&accepted===families.length&&!replaceCount&&!pending);typeset();
  if(validation&&!valid)setSummativeStatus(`Returned family file needs correction before approval. ${(validation.errors||[]).slice(0,3).join(' ')}`,'error');
  else if(!next.hidden){const gaps=Number(validation?.makeup_parallel_gap_count||0);setSummativeStatus(gaps?`All returned MC families are accepted. Save the short Makeup Parallel Request so Forms 5–6 can use true number-swap parallels.`:'All returned Summative families are accepted. Open any print/key page; it will assemble automatically on first use.','good')}
  else if(replaceCount)setSummativeStatus(`${replaceCount} famil${replaceCount===1?'y is':'ies are'} marked Replace. Save the replacement request, upload it to Curriculum Build, apply the returned transfer, then click Load Returned Families.`,'warn');
  else setSummativeStatus('Returned multiple-choice families are ready for review. Accept each family or mark it Replace.','good');
}
async function reviewSummativeFamily(familyId,decision){
  const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)return;setSummativeStatus(decision==='ACCEPT'?'Saving family approval…':'Marking family for replacement…','');
  try{const r=await fetch('/api/summative/family-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:planId,family_id:familyId,decision})}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Review failed (${r.status})`);renderSummativePlan(data.plan,!!data.families_ready,data.request_url||null,data.family_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null)}catch(err){setSummativeStatus(`Could not save Summative family review: ${err.message}`,'error')}
}
async function acceptAllSummativeFamilies(){await reviewSummativeFamily('*','ACCEPT')}
function renderSummativeAssembly(assembly){
  state.summativeAssembly=assembly||null;const section=$('summativeNextPhase'),status=$('summativeAssemblyStatus'),summary=$('summativeAssemblySummary'),actions=$('summativeOutputActions');
  if(!section)return;
  const ready=!section.hidden,gaps=Number(state.summativeMakeupGapCount||0);
  if(!ready){summary.hidden=true;actions.hidden=true;if(status)status.textContent='Accept all returned MC families to unlock printing.';return}
  if(gaps>0){summary.hidden=true;actions.hidden=true;if(status)status.textContent=`Waiting for the returned makeup-parallel transfer for ${gaps} famil${gaps===1?'y':'ies'}. Apply it, then click Load Returned Families.`;return}
  actions.hidden=false;
  if(!assembly){summary.hidden=true;if(status)status.textContent='Ready. Open any print/key page below; the first click will assemble the Summative automatically.';return}
  summary.hidden=false;summary.innerHTML=`<strong>${Number(assembly.mc_question_count||0)} common MC question${Number(assembly.mc_question_count||0)===1?'':'s'}</strong><span>Forms 1–4 · Test Day scrambles</span><span>Forms 5–6 · parallel makeups</span><span>${Number(assembly.student_count||0)} personalized answer/FRQ sheets</span><span>2 pages each</span><span>${Number(assembly.personalized_frq_count_per_student||4)} FRQs per student</span>`;
  if(status)status.textContent='Summative ready. Fine-tune MC spacing/figures on the MC Booklet page and personalized FRQs on the Answer + FRQ page.';
}
async function ensureSummativeAssembly(){
  if(state.summativeAssembly)return state.summativeAssembly;const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)throw new Error('No Summative plan is selected.');if(Number(state.summativeMakeupGapCount||0)>0)throw new Error('Forms 5–6 still need the Makeup Parallel Request.');setSummativeStatus('Building the six MC forms and personalized two-page answer/FRQ sheets…','');const r=await fetch('/api/summative/assemble',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan_id:planId})}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Assembly failed (${r.status})`);state.summativeAssembly=data.assembly||null;renderSummativeAssembly(state.summativeAssembly);setSummativeStatus('Summative assembled. Opened the page you selected.','good');return state.summativeAssembly;
}
async function openSummativeArtifact(kind){
  const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)return;const routes={mc:'/api/summative/mc-booklet.html',answer:'/api/summative/answer-sheets.html',mckey:'/api/summative/mc-key.html',frqkey:'/api/summative/frq-key.html'},url=routes[kind];if(!url)return;const tab=window.open('about:blank','_blank');try{await ensureSummativeAssembly();tab.location=`${url}?plan_id=${encodeURIComponent(planId)}`}catch(err){if(tab)tab.close();setSummativeStatus(`Could not open Summative page: ${err.message}`,'error')}
}
function renderSummativePlan(plan,familiesReady=false,requestUrl=null,familyResponse=null,familyReview=null,responseValidation=null,replacementUrl=null,assembly=null){
  if(plan)state.suppressLatestRestore=false;
  state.summativePlan=plan||null;state.summativePlanId=plan?.plan_id||state.summativePlanId;state.summativeFamiliesReady=!!familiesReady;state.summativeMakeupGapCount=Number(responseValidation?.makeup_parallel_gap_count||0);state.summativeMakeupGapFamilyIds=responseValidation?.makeup_parallel_gap_family_ids||[];
  const sum=$('summativeSummary'),students=$('summativeStudents'),refresh=$('refreshSummativeBtn'),save=$('saveSummativeRequestBtn');if(!plan){sum.hidden=true;students.innerHTML='';refresh.disabled=true;save.hidden=true;renderSummativeFamilyReview(null,null,null,null);renderSummativeAssembly(null);return}
  state.summativeEligibleIcanIds=new Set(plan.eligible_i_cans||[]);renderSummativeEligibility();
  const studentCount=Number(plan.student_count||0),re=Number(plan.reassessment_slot_count||0),ext=Number(plan.extension_slot_count||0),mc=Number(plan.mc_conversion_request_count||0),extFam=Number(plan.extension_family_request_count||0),records=Number(plan.evidence_record_count||0),scope=(plan.eligible_i_cans||[]).length;
  sum.hidden=false;sum.innerHTML=`<strong>${studentCount} student${studentCount===1?'':'s'} in plan</strong><span>${scope} eligible I Can${scope===1?'':'s'}</span><span>${records} Portfolio current-status records</span><span>${re} reassessment slot${re===1?'':'s'}</span><span>${ext} extension slot${ext===1?'':'s'}</span><span>${mc} MC conversion famil${mc===1?'y':'ies'} + ${extFam} extension famil${extFam===1?'y':'ies'}</span><span>Target: 4 questions per student</span>`;
  students.innerHTML=(plan.students||[]).map(s=>summativeStudentCard(s,4)).join('');refresh.disabled=false;save.hidden=false;renderSummativeFamilyReview(familiesReady?familyResponse:null,familyReview,responseValidation,replacementUrl);renderSummativeAssembly(assembly);
  if(!studentCount)setSummativeStatus(`No students were recognized yet. ${plan.files_scanned?.length||0} current Portfolio state file(s) were scanned.`,'warn');else if(!familiesReady)setSummativeStatus(`Summative evidence plan created. AI will convert ${mc} exact reassessment target${mc===1?'':'s'} to reusable multiple-choice families and author ${extFam} extension famil${extFam===1?'y':'ies'}. Click Save AI Request, then upload that ZIP to Curriculum Build.`,'good');saveDraft();
}
async function analyzeSummative(){
  if(state.summativeBusy)return;const eligible=[...state.summativeEligibleIcanIds].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));if(eligible.length<4){setSummativeStatus('Select at least four eligible I Can statements first.','warn');return}state.summativeBusy=true;updateSummativeScopeSummary();setSummativeStatus('Reading current Portfolio status and choosing each student’s four least-secure targets…','');
  try{const payload={unit:Number($('unitSelect')?.value||1),item_label:$('itemLabel').value.trim(),custom_name:customName(),eligible_i_cans:eligible},r=await fetch('/api/summative/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Analysis failed (${r.status})`);renderSummativePlan(data.plan,!!data.families_ready,data.request_url||null,data.family_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null)}catch(err){setSummativeStatus(`Summative analysis failed: ${err.message}`,'error')}finally{state.summativeBusy=false;updateSummativeScopeSummary()}
}
async function saveSummativeRequest(){const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)return;setSummativeStatus('Opening Save dialog for the AI request…','');try{const r=await fetch(`/api/summative/reveal-request?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Could not open Save dialog (${r.status})`);if(data.cancelled){setSummativeStatus('AI request was not saved. Click Save AI Request when you are ready.','warn');return}setSummativeStatus(`AI request saved as ${data.name||'request ZIP'} in the location you confirmed. Upload that ZIP to Curriculum Build.`,'good')}catch(err){setSummativeStatus(`Could not save the Summative request: ${err.message}`,'error')}}
async function saveSummativeReplacementRequest(){const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)return;setSummativeStatus('Opening Save dialog for the replacement request…','');try{const r=await fetch(`/api/summative/save-replacement-request?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Could not open Save dialog (${r.status})`);if(data.cancelled){setSummativeStatus('Replacement request was not saved.','warn');return}setSummativeStatus(`Replacement request saved as ${data.name||'request ZIP'}. Upload that ZIP to Curriculum Build.`,'good')}catch(err){setSummativeStatus(`Could not save the Summative replacement request: ${err.message}`,'error')}}
async function refreshSummative(){const planId=state.summativePlanId||state.summativePlan?.plan_id;if(!planId)return;setSummativeStatus('Checking for returned Summative families…','');try{const r=await fetch(`/api/summative/status?plan_id=${encodeURIComponent(planId)}`,{cache:'no-store'}),data=await r.json().catch(()=>({}));if(!r.ok||!data.ok)throw new Error(data.error||`Refresh failed (${r.status})`);if(!data.found)throw new Error('The local Summative plan was not found.');renderSummativePlan(data.plan,!!data.families_ready,data.request_url||null,data.family_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null);if(!data.families_ready)setSummativeStatus('Still waiting for the returned Summative-family transfer. Apply it, then click Load Returned Families.','warn')}catch(err){setSummativeStatus(`Could not refresh Summative: ${err.message}`,'error')}}
async function restoreLatestSummative(){if(!isSummative())return;if(state.suppressLatestRestore&&!state.summativePlanId)return;try{const planId=state.summativePlanId,url=planId?`/api/summative/status?plan_id=${encodeURIComponent(planId)}`:'/api/summative/latest',r=await fetch(url,{cache:'no-store'}),data=await r.json().catch(()=>({}));if(r.ok&&data.ok&&data.found&&data.plan)renderSummativePlan(data.plan,!!data.families_ready,data.request_url||null,data.family_response||null,data.family_review||null,data.response_validation||null,data.replacement_request_url||null,data.assembly||null)}catch(_){}}

function updateModeUI(){
  const checkpoint=isCheckpoint(),summative=isSummative(),special=checkpoint||summative;
  $('checkpointPanel').hidden=!checkpoint;$('summativePanel').hidden=!summative;$('bankGoal').hidden=special;
  $('nextBtn').hidden=special;$('mgSelect').disabled=special;$('icanSelect').disabled=special;
  const saveWrap=$('saveTargetWrap'),destinationCard=$('destinationCard');
  if(saveWrap)saveWrap.hidden=special;if(destinationCard)destinationCard.hidden=special;
  if(checkpoint){
    state.saveTarget='local';$('saveTarget').value='local';$('saveTarget').disabled=true;
    $('mgTitle').textContent='Owner Checkpoint · Evidence Autopilot';$('mgSubtitle').textContent='Choose eligible I Can statements across any units, then let the Portfolio determine each student’s reassessment needs inside that scope.';$('mgCount').textContent='Teacher-selected I Cans first · Portfolio need second · temporary families only for open slots';
    $('destinationPreview').textContent='Local/private Checkpoint build — student evidence is not published to GitHub';
    $('selectedCount').textContent='Checkpoint eligibility is selected below';$('icanSummary').innerHTML='<span>Select the exact I Can statements across any units you want included.</span>';
    loadCheckpointEligibility().then(()=>restoreLatestCheckpoint());
  }else if(summative){
    state.saveTarget='local';$('saveTarget').value='local';$('saveTarget').disabled=true;
    $('mgTitle').textContent='Owner Summative · Common MC + Personalized FRQ';$('mgSubtitle').textContent='Choose the eligible I Can scope. Portfolio status selects up to four least-secure I Cans per student for the personalized FRQ sheet while accepted AI conversions become the reusable common MC set.';$('mgCount').textContent='Teacher-selected scope · reusable 6-form MC set · 4 personalized FRQs per student';
    $('destinationPreview').textContent='Local/private Summative build — individualized student evidence is not published to GitHub';
    $('selectedCount').textContent='Summative eligibility is selected below';$('icanSummary').innerHTML='<span>Select at least four exact I Can statements across any units you want included.</span>';
    loadSummativeEligibility().then(()=>restoreLatestSummative());
  }else{
    $('saveTarget').disabled=false;renderGoal();updateSummary();
  }
}

function updateSummary(){
  if(isCheckpoint()){
    $('filenamePreview').textContent=`Algebra_1_${itemToken()}${customName()?`_${customToken()}`:''}_Checkpoint`;
    $('destinationPreview').textContent='Local/private Checkpoint build — student evidence is not published to GitHub';
    saveDraft();return;
  }
  if(isSummative()){
    $('filenamePreview').textContent=`Algebra_1_${itemToken()}${customName()?`_${customToken()}`:''}_Summative`;
    $('destinationPreview').textContent='Local/private Summative build — individualized student evidence is not published to GitHub';
    saveDraft();return;
  }
  const vals=[...state.selected.values()],counts=new Map();
  vals.forEach(x=>counts.set(x.ic.i_can_id,(counts.get(x.ic.i_can_id)||0)+1));
  $('selectedCount').textContent=`Total: ${vals.length} question${vals.length===1?'':'s'}`;
  const summary=$('icanSummary');
  if(!counts.size)summary.innerHTML='<span>No questions selected.</span>';
  else summary.innerHTML=[...counts.entries()].sort((a,b)=>a[0].localeCompare(b[0],undefined,{numeric:true})).map(([id,n])=>`<span><strong>${esc(shortIcan(id))}</strong>: ${n}</span>`).join('');
  $('filenamePreview').textContent=baseFilename(1);$('destinationPreview').textContent=storageName();$('nextBtn').disabled=vals.length===0;
  saveDraft();
}

let practicePlc=null,practicePlcStorageKey='';
function practiceFigurePercentFromPx(px){return Math.max(0,Math.min(300,Math.round((Number(px)||0)/260*100)))}
function practiceFigurePxFromPercent(pct){return Math.round(260*Math.max(0,Math.min(300,Number(pct)||0))/100)}
function practiceLayoutKey(){return `shared-print-layout-practice-v1:${itemToken()}:${customToken()||'default'}`}
function practiceInitialLayoutState(){
  if(state.practiceLayoutState&&typeof state.practiceLayoutState==='object')return state.practiceLayoutState;
  const q={},count=Math.max(1,state.versionCount,state.builtVersions.length||0);
  for(let v=1;v<=count;v++)for(const x of state.selected.values())q[`${v}::${x.f.family_id}`]={workspace:Number(x.workSize||0),figure:practiceFigurePercentFromPx(x.figureSize||state.allFigureSize)};
  return {whole:{workspace:Number(state.allWorkSize||0),figure:practiceFigurePercentFromPx(state.allFigureSize||260)},entities:{},questions:q,order:{}};
}
function practiceLayoutValues(version,fid){
  if(practicePlc)return practicePlc.effectiveQuestion(String(version),String(fid));
  const x=state.selected.get(String(fid));return {workspace:Number(x?.workSize||state.allWorkSize||0),figure:practiceFigurePercentFromPx(x?.figureSize||state.allFigureSize||260)};
}
function syncPracticeLegacyLayout(){
  if(!practicePlc)return;
  state.practiceLayoutState=practicePlc.exportState();
  state.allWorkSize=Number(state.practiceLayoutState.whole?.workspace??state.allWorkSize??0);
  state.allFigureSize=practiceFigurePxFromPercent(state.practiceLayoutState.whole?.figure??100);
  const v=String(state.activeVersion||1);
  for(const [fid,x] of state.selected){const z=practicePlc.effectiveQuestion(v,fid);x.workSize=Number(z.workspace||0);x.figureSize=practiceFigurePxFromPercent(z.figure)}
  saveDraft();
}
function relabelPracticeQuestions(version,ids){
  const pages=[...document.querySelectorAll('.paper-page')].filter(p=>String(p.dataset.version||'')===String(version));
  (ids||[]).forEach((id,pos)=>{for(const page of pages){const q=[...page.querySelectorAll('.workspace-question[data-family-id]')].find(el=>String(el.dataset.familyId||'')===String(id));if(!q)continue;const n=q.querySelector('[data-practice-number]');if(n)n.textContent=`${pos+1}.`;break}});
}
function applyPracticeOrderToState(version,ids){
  const v=Number(version)||1;
  if(state.builtVersions[v-1])state.builtVersions[v-1].order=ids.slice();
  else if(v===1){const byId=new Map(state.selected);const reordered=new Map();ids.forEach(id=>{if(byId.has(id))reordered.set(id,byId.get(id))});for(const [id,x] of byId)if(!reordered.has(id))reordered.set(id,x);state.selected=reordered}
}
function makePracticePage(entity,_ctx,pageNo){return createPaperPage(pageNo,Number(entity)||state.activeVersion).page}
function reflowPracticeWithSharedController(){
  if(!practicePlc)return;
  practicePlc.normalizeQuestionParts();practicePlc.refreshPages(false);practicePlc.apply(false,{commit:false,source:'practice-refresh'});
  practicePlc.reflowDynamicAll({ensureEven:false,makePage:makePracticePage});
  const v=String(state.activeVersion||1),ids=practicePlc.orderedIds(v);relabelPracticeQuestions(v,ids);practicePlc.refreshView();
}
function ensurePracticePlc(){
  const key=practiceLayoutKey();
  if(practicePlc&&practicePlcStorageKey===key)return practicePlc;
  practicePlcStorageKey=key;
  practicePlc=new window.PrintLayoutController({
    fields:[{key:'workspace',label:'Workspace',min:0,max:1200,step:1,default:Number(state.allWorkSize||0),unit:'px'},{key:'figure',label:'Figure size',min:0,max:300,step:1,default:practiceFigurePercentFromPx(state.allFigureSize||260),unit:'%'}],
    storageKey:key,initialState:practiceInitialLayoutState(),initialStateAuthoritative:true,getSelectedEntity:()=>'',mainMount:'#practiceLayoutControls',viewMount:'#practiceViewControls',stage:'#paperPages',pageSelector:'.paper-page',pageBodySelector:'.paper-body',entityAttr:'version',questionSelector:'.workspace-question[data-family-id]',questionAttr:'familyId',pagesPerEntity:2,sidebarWidth:350,figureBasePx:260,figureSelector:'.plc-figure:not(:empty)',scopeOwnsDescendants:true,wholeLayoutTitle:'Whole Practice Layout',wholeResetLabel:'Reset Practice Layout',pageLabel:p=>`Version ${p.dataset.version} · Page ${p.dataset.page||'?'}`,makePage:makePracticePage,
    onReorder:(v,ids)=>{applyPracticeOrderToState(v,ids);state.practiceLayoutState=practicePlc.exportState()},
    onCommit:()=>{syncPracticeLegacyLayout();reflowPracticeWithSharedController();renderPracticeQuestionControls()},
    onChange:(_st,ctx)=>{if(ctx?.commit)renderPracticeQuestionControls()}
  });
  return practicePlc;
}
function clampVersionCount(value){const n=Math.floor(Number(value)||1);return Math.max(1,Math.min(12,n))}
let previewTimer=null;
let paginationToken=0;
function schedulePreviewRender(){
  clearTimeout(previewTimer);
  previewTimer=setTimeout(()=>renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap()),60);
}
function exemplarInstance(x){const ex=x.f.exemplar||{};return {student_html:ex.student_html||'<p>Exemplar unavailable.</p>',answer:ex.answer||'',solution:ex.solution||'',generation_note:'Current approved bank exemplar.'}}
function activeInstanceFor(x,instanceMap=null){return instanceMap?.get(x.f.family_id)||x.baseInstance||exemplarInstance(x)}
function makeQuestionNode(x,i,instanceMap=null){
  const ex=activeInstanceFor(x,instanceMap);
  const q=document.createElement('article');q.className='workspace-question plc-question';q.dataset.familyId=x.f.family_id;
  q.innerHTML=`<div class="workspace-question-head"><span data-practice-number>${i+1}.</span></div><div class="plc-question-content">${rewriteRelativeResources(ex.student_html||'<p>Exemplar unavailable.</p>')}</div><div class="plc-figure"></div><div class="builder-workspace plc-workspace" aria-hidden="true"></div>`;
  return q;
}
function currentBuiltVersion(){
  if(!state.builtVersions.length)return null;
  return state.builtVersions[Math.max(0,state.activeVersion-1)]||null;
}
function currentPreviewInstanceMap(){return currentBuiltVersion()?.instances||null}
function currentPreviewVals(){
  const vals=[...state.selected.values()],built=currentBuiltVersion();
  if(!built?.order?.length)return vals;
  const byId=new Map(vals.map(x=>[x.f.family_id,x]));
  return built.order.map(fid=>byId.get(fid)).filter(Boolean);
}
function paperHeaderHTML(pageNo,version=state.activeVersion){
  const title=`Algebra 1 · ${displayTitle()}`;
  const left=pageNo===1?`<div><strong>${esc(title)}</strong><span>Name ______________________________</span></div>`:`<div><strong>${esc(title)}</strong><span>continued</span></div>`;
  return `${left}<span>Version ${version} · Page ${pageNo}</span>`;
}
function createPaperPage(pageNo,version=state.activeVersion){
  const page=document.createElement('section');page.className='paper-page';page.dataset.page=String(pageNo);page.dataset.version=String(version);
  const head=document.createElement('div');head.className='paper-head';head.innerHTML=paperHeaderHTML(pageNo,version);
  const body=document.createElement('div');body.className='paper-body';
  page.append(head,body);
  return {page,body};
}
async function waitForImages(root){
  const imgs=[...root.querySelectorAll('img')];
  await Promise.all(imgs.map(img=>img.complete?Promise.resolve():new Promise(resolve=>{img.addEventListener('load',resolve,{once:true});img.addEventListener('error',resolve,{once:true});setTimeout(resolve,2500)})));
}
async function typesetElement(root){
  try{
    if(window.MathJax?.startup?.promise)await window.MathJax.startup.promise;
    if(window.MathJax?.typesetPromise)await window.MathJax.typesetPromise([root]);
  }catch(_){ }
}
async function renderPaginatedPreview(vals,instanceMap=currentPreviewInstanceMap()){
  const token=++paginationToken;
  const stage=$('paperPages');if(!stage)return;
  if(!vals.length){stage.innerHTML='<div class="preview-empty">Choose questions to build a page preview.</div>';renderPracticeQuestionControls();return;}
  stage.innerHTML='<div class="preview-loading">Laying out printable pages…</div>';
  const version=state.activeVersion,first=createPaperPage(1,version);stage.innerHTML='';stage.appendChild(first.page);
  vals.forEach((x,i)=>first.body.appendChild(makeQuestionNode(x,i,instanceMap)));
  await typesetElement(stage);await waitForImages(stage);if(token!==paginationToken)return;
  ensurePracticePlc();reflowPracticeWithSharedController();renderPracticeQuestionControls();
}
function generatorSupports(x){return Boolean(window.AssessmentGeneration?.supports?.(x.f.family_id))}
function generateInstance(x){return window.AssessmentGeneration?.generate?.(x.f)||null}
function invalidateBuiltVersions(message='Question set changed. Build Versions again when ready.'){
  state.builtVersions=[];state.activeVersion=1;state.generationMessage=message;renderVersionTabs();
}
function renderVersionTabs(){
  const tabs=$('versionTabs'),status=$('generationStatus');if(!tabs||!status)return;
  if(!state.builtVersions.length){tabs.hidden=true;tabs.innerHTML='';status.textContent=state.generationMessage||'Design the base item first, then build the requested parallel versions.';status.className='generation-status';if($('saveBtn'))$('saveBtn').disabled=true;if($('printAllVersionsBtn'))$('printAllVersionsBtn').disabled=true;return;}
  tabs.hidden=false;if($('saveBtn'))$('saveBtn').disabled=false;if($('printAllVersionsBtn'))$('printAllVersionsBtn').disabled=false;tabs.innerHTML=state.builtVersions.map((_,i)=>`<button class="version-tab ${state.activeVersion===i+1?'active':''}" data-version="${i+1}">V${i+1}</button>`).join('');
  tabs.querySelectorAll('[data-version]').forEach(b=>b.onclick=()=>{state.activeVersion=Number(b.dataset.version);renderVersionTabs();$('workspaceFilename').textContent=baseFilename(state.activeVersion);renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap())});
  status.textContent=`${state.builtVersions.length} version${state.builtVersions.length===1?'':'s'} built from the current bank families. Use the tabs to inspect each form.`;status.className='generation-status good';
}
function previewCandidateHtml(inst){return `<div class="candidate-preview"><div class="candidate-label">Candidate instance</div><div class="candidate-question">${rewriteRelativeResources(inst.student_html||'')}</div><div class="candidate-actions"><button class="mini-btn use-candidate">Use this instance</button><button class="mini-btn keep-current">Keep current</button></div></div>`}
function createCandidate(fid){const x=state.selected.get(fid);if(!x||!generatorSupports(x))return;x.candidateInstance=generateInstance(x);renderWorkspace();}
function useCandidate(fid){const x=state.selected.get(fid);if(!x?.candidateInstance)return;x.baseInstance=x.candidateInstance;x.candidateInstance=null;invalidateBuiltVersions('Base question changed. Rebuild versions when ready.');renderWorkspace();saveDraft();}
function keepCurrent(fid){const x=state.selected.get(fid);if(!x)return;x.candidateInstance=null;renderWorkspace();}
function shuffleCopy(items){const a=items.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function choiceLetter(i){return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i]||String(i+1)}
function scrambleChoiceInstance(inst){
  if(!state.scrambleChoices||!inst?.student_html)return inst;
  const t=document.createElement('template');t.innerHTML=inst.student_html;
  const ol=t.content.querySelector('ol.choices');if(!ol)return inst;
  const lis=[...ol.children].filter(x=>x.tagName==='LI');if(lis.length<2)return inst;
  let correct=-1;const m=String(inst.answer||'').trim().match(/^([A-Z])\s*[.):-]/i);
  if(m)correct=m[1].toUpperCase().charCodeAt(0)-65;
  if(correct<0||correct>=lis.length){
    const answerText=String(inst.answer||'').replace(/^[A-Z]\s*[.):-]\s*/i,'').trim().toLowerCase();
    correct=lis.findIndex(li=>answerText&&answerText.includes(li.textContent.trim().toLowerCase()));
  }
  if(correct<0||correct>=lis.length)return inst;
  const items=lis.map((li,i)=>({html:li.innerHTML,correct:i===correct}));
  const mixed=shuffleCopy(items);ol.innerHTML='';mixed.forEach(x=>{const li=document.createElement('li');li.innerHTML=x.html;ol.appendChild(li)});
  const idx=mixed.findIndex(x=>x.correct),answerText=ol.children[idx]?.textContent?.trim()||'';
  return {...inst,student_html:t.innerHTML,answer:`${choiceLetter(idx)}. ${answerText}`};
}
function makeVersionInstances(vals,isBase){
  const map=new Map();
  for(const x of vals){let inst=isBase?(x.baseInstance||exemplarInstance(x)):generateInstance(x);if(!inst)inst=x.baseInstance||exemplarInstance(x);map.set(x.f.family_id,scrambleChoiceInstance(inst))}
  return map;
}
function buildVersions(){
  const vals=[...state.selected.values()];if(!vals.length)return;
  const unsupported=vals.filter(x=>!generatorSupports(x));
  if(unsupported.length){state.generationMessage=`Generation is not wired for: ${unsupported.map(x=>qidFor(x.f.family_id)).join(', ')}.`;renderVersionTabs();return;}
  const ids=vals.map(x=>x.f.family_id),versions=[];if(state.practiceLayoutState?.order)state.practiceLayoutState.order={};if(practicePlc)practicePlc.state.order={};
  for(let v=1;v<=state.versionCount;v++)versions.push({instances:makeVersionInstances(vals,v===1),order:state.scrambleOrder?shuffleCopy(ids):ids.slice()});
  state.builtVersions=versions;state.activeVersion=1;state.generationMessage='';renderVersionTabs();$('workspaceFilename').textContent=baseFilename(1);renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap());saveDraft();
}
function renderPracticeQuestionControls(){
  const list=$('selectedList');if(!list)return;
  const vals=currentPreviewVals();list.innerHTML='';
  vals.forEach((x,i)=>{
    const div=document.createElement('div');div.className='selected-control';const supported=generatorSupports(x),candidate=x.candidateInstance?previewCandidateHtml(x.candidateInstance):'';
    div.innerHTML=`<div class="selected-control-head"><strong>${i+1}. ${esc(qidFor(x.f.family_id))} · ${esc(x.f.family_name)}</strong><div class="control-buttons"><button class="mini-btn" data-up="${esc(x.f.family_id)}" ${i===0?'disabled':''}>↑</button><button class="mini-btn" data-down="${esc(x.f.family_id)}" ${i===vals.length-1?'disabled':''}>↓</button></div></div><div class="small muted">${esc(x.ic.i_can_id)}</div><button class="new-instance-btn" data-new-instance="${esc(x.f.family_id)}" ${supported?'':'disabled'}>${supported?'New question instance':'Instance generator not available'}</button>${candidate}<div data-practice-q-layout></div>`;
    list.appendChild(div);
    if(practicePlc){const mount=div.querySelector('[data-practice-q-layout]'),v=String(state.activeVersion||1),keys=familyHasFigure(x)?['workspace','figure']:['workspace'];practicePlc.mountQuestionControls(mount,v,x.f.family_id,keys,{reorder:false});mount.querySelector('.plc-reset')?.remove()}
  });
  list.querySelectorAll('[data-new-instance]').forEach(b=>b.onclick=()=>createCandidate(b.dataset.newInstance));
  list.querySelectorAll('.use-candidate').forEach(b=>b.onclick=()=>useCandidate(b.closest('.selected-control').querySelector('[data-new-instance]').dataset.newInstance));
  list.querySelectorAll('.keep-current').forEach(b=>b.onclick=()=>keepCurrent(b.closest('.selected-control').querySelector('[data-new-instance]').dataset.newInstance));
  list.querySelectorAll('[data-up]').forEach(b=>b.onclick=()=>practicePlc?practicePlc.moveQuestion(String(state.activeVersion||1),b.dataset.up,-1):moveSelected(b.dataset.up,-1));
  list.querySelectorAll('[data-down]').forEach(b=>b.onclick=()=>practicePlc?practicePlc.moveQuestion(String(state.activeVersion||1),b.dataset.down,1):moveSelected(b.dataset.down,1));
}
function renderWorkspace(){
  const title=displayTitle();$('workspaceTitle').textContent=title;$('workspaceFilename').textContent=baseFilename(state.activeVersion);
  $('versionCountInput').value=String(state.versionCount);$('scrambleOrder').checked=state.scrambleOrder;$('scrambleChoices').checked=state.scrambleChoices;
  $('generationPlan').textContent=`${state.versionCount} version${state.versionCount===1?'':'s'} planned from ${state.selected.size} bank famil${state.selected.size===1?'y':'ies'}`;
  $('buildVersionsBtn').textContent=state.versionCount===1?'Build 1 Version':`Build ${state.versionCount} Versions`;$('buildVersionsBtn').disabled=state.selected.size===0;
  renderVersionTabs();renderPracticeQuestionControls();renderPaginatedPreview(currentPreviewVals(),currentPreviewInstanceMap());
}
function moveSelected(fid,delta){const arr=[...state.selected.entries()],i=arr.findIndex(([k])=>k===fid),j=i+delta;if(i<0||j<0||j>=arr.length)return;[arr[i],arr[j]]=[arr[j],arr[i]];state.selected=new Map(arr);invalidateBuiltVersions('Question order changed. Build Versions again when ready.');renderWorkspace();saveDraft()}

function typeset(){if(window.MathJax?.typesetPromise)window.MathJax.typesetPromise().catch(()=>{})}
function showWorkspace(){state.product=$('productType').value;$('selectStep').classList.remove('active');$('workspaceStep').classList.add('active');window.scrollTo(0,0);renderWorkspace()}
function showSelect(){$('workspaceStep').classList.remove('active');$('selectStep').classList.add('active');window.scrollTo(0,0);renderGoal();updateSummary()}
async function clearAllSetup(){
  if(!window.confirm('Clear the current Assessment Builder setup? Saved output files will not be deleted.'))return;
  state.focus='';state.selected=new Map();state.versionCount=1;state.activeVersion=1;state.builtVersions=[];state.generationMessage='';state.suppressLatestRestore=true;
  state.allFigureSize=260;state.allWorkSize=0;state.practiceLayoutState=null;try{if(practicePlcStorageKey)localStorage.removeItem(practicePlcStorageKey)}catch(_){}practicePlc=null;practicePlcStorageKey='';state.scrambleOrder=true;state.scrambleChoices=true;
  state.checkpointPlan=null;state.checkpointPlanId='';state.checkpointExtensionsReady=false;state.checkpointBusy=false;state.checkpointEligibleIcanIds=new Set();state.checkpointAssembly=null;
  state.summativePlan=null;state.summativePlanId='';state.summativeFamiliesReady=false;state.summativeBusy=false;state.summativeEligibleIcanIds=new Set();state.summativeAssembly=null;state.summativeMakeupGapCount=0;state.summativeMakeupGapFamilyIds=[];
  $('itemLabel').value='';$('customName').value='';
  state.saveTarget=(isCheckpoint()||isSummative())?'local':'both';$('saveTarget').value=state.saveTarget;
  state.draftLoaded=true;
  try{localStorage.removeItem(DRAFT_KEY)}catch(_){}
  renderCheckpointPlan(null,false,null,null,null,null,null,null);
  renderSummativePlan(null,false,null,null,null,null,null,null);
  if(state.checkpointScopeLoaded)renderCheckpointEligibility();
  if(state.summativeScopeLoaded)renderSummativeEligibility();
  if(state.goal)renderGoal();
  updateSummary();
  if(isCheckpoint())setCheckpointStatus('Select the eligible I Can statements, then analyze the current local Portfolio evidence.','');
  if(isSummative())setSummativeStatus('Select at least four exact I Can statements across any units you want included.','');
  saveDraft();
  if($('workspaceStep').classList.contains('active'))showSelect();
  else window.scrollTo(0,0);
}

async function init(){
  $('productType').onchange=()=>{state.product=$('productType').value;updateModeUI();updateSummary()};
  $('itemLabel').oninput=updateSummary;$('customName').oninput=updateSummary;$('saveTarget').onchange=()=>{state.saveTarget=$('saveTarget').value;updateSummary()};
  $('analyzeCheckpointBtn').onclick=analyzeCheckpoint;$('saveExtensionRequestBtn').onclick=saveCheckpointRequest;$('refreshCheckpointBtn').onclick=refreshCheckpoint;$('assembleCheckpointBtn').onclick=assembleCheckpoint;$('openCheckpointOutputFolderBtn').onclick=openCheckpointOutputFolder;$('reloadCheckpointScopeBtn').onclick=()=>loadCheckpointEligibility(true);$('selectAllCheckpointScopeBtn').onclick=selectAllCheckpointScope;$('clearCheckpointScopeBtn').onclick=clearCheckpointScope;$('acceptAllTemporaryFamiliesBtn').onclick=acceptAllTemporaryFamilies;
  $('analyzeSummativeBtn').onclick=analyzeSummative;$('saveSummativeRequestBtn').onclick=saveSummativeRequest;$('refreshSummativeBtn').onclick=refreshSummative;$('reloadSummativeScopeBtn').onclick=()=>loadSummativeEligibility(true);$('selectAllSummativeScopeBtn').onclick=selectAllSummativeScope;$('clearSummativeScopeBtn').onclick=clearSummativeScope;$('acceptAllSummativeFamiliesBtn').onclick=acceptAllSummativeFamilies;$('openSummativeMcBookletBtn').onclick=()=>openSummativeArtifact('mc');$('openSummativeAnswerSheetsBtn').onclick=()=>openSummativeArtifact('answer');$('openSummativeMcKeyBtn').onclick=()=>openSummativeArtifact('mckey');$('openSummativeFrqKeyBtn').onclick=()=>openSummativeArtifact('frqkey');
  $('mgSelect').onchange=()=>{state.focus='';loadGoal($('mgSelect').value)};
  $('icanSelect').onchange=()=>{state.focus=$('icanSelect').value;renderGoal()};
  $('clearAllBtn').onclick=clearAllSetup;
  $('workspaceClearAllBtn').onclick=clearAllSetup;
  $('saveDraftBtn').onclick=downloadDraft;
  $('loadDraftBtn').onclick=()=>$('draftFileInput').click();
  $('draftFileInput').onchange=e=>{const file=e.target.files?.[0];loadDraftFile(file);e.target.value=''};
  $('nextBtn').onclick=showWorkspace;$('backBtn').onclick=showSelect;
  $('versionCountInput').oninput=e=>{state.versionCount=clampVersionCount(e.target.value);invalidateBuiltVersions('Version count changed. Build Versions when ready.');$('workspaceFilename').textContent=baseFilename(1);$('generationPlan').textContent=`${state.versionCount} version${state.versionCount===1?'':'s'} planned from ${state.selected.size} bank famil${state.selected.size===1?'y':'ies'}`;$('buildVersionsBtn').textContent=state.versionCount===1?'Build 1 Version':`Build ${state.versionCount} Versions`;saveDraft()};
  $('scrambleOrder').onchange=e=>{state.scrambleOrder=e.target.checked;invalidateBuiltVersions('Scramble setting changed. Build Versions again when ready.');renderWorkspace();saveDraft()};
  $('scrambleChoices').onchange=e=>{state.scrambleChoices=e.target.checked;invalidateBuiltVersions('Scramble setting changed. Build Versions again when ready.');renderWorkspace();saveDraft()};
  $('buildVersionsBtn').onclick=buildVersions;
  $('downloadPreviewBtn').onclick=downloadCurrentPreview;
  $('saveBtn').onclick=saveFinishedBuild;
  $('printBtn').onclick=printCurrentVersion;
  $('printAllVersionsBtn').onclick=printAllVersions;
  try{await loadCore();await restoreDraft();await loadGoal(state.mgid);updateModeUI();updateSummary()}catch(err){const s=$('bankStatus');s.className='status-pill error';s.textContent='Bank unavailable';$('familyRows').innerHTML=`<div class="error">${esc(err.message)}</div>`}
}
window.addEventListener('DOMContentLoaded',init);
