(()=>{
'use strict';
const el = document.getElementById('view');
const notice = document.getElementById('notice');
const picker = document.getElementById('coursePicker');
const validRoutes = new Set(['dashboard','courses','curriculum','lessons','assessments','portfolio','distribution','settings']);
const safe = (v)=>window.CourseToolUI.escapeHtml(String(v??''));
let status = null;
let currentCourse = 'physics';
let resources = [];
let query = '';
let indexLoaded = false;
const yes = (v)=>v ? 'Available' : 'Not found';
const pill = (value,cls='')=>`<span class="pill ${cls}">${safe(value)}</span>`;
const row = (label,value)=>`<li><span>${safe(label)}</span><span class="value">${safe(value)}</span></li>`;
const headline = (section,title,description,right='')=>`<header class="page-head"><div><div class="eyebrow">${safe(section)}</div><h1>${safe(title)}</h1><p>${safe(description)}</p></div>${right}</header>`;
const card = (url,title,sub)=>`<a class="action-tile" href="#${safe(url)}"><strong>${safe(title)}</strong><small>${safe(sub)}</small></a>`;
const feature = (name,description,source)=>`<section class="feature">${pill('Integration pending','wip')}<br><strong>${safe(name)}</strong><p>${safe(description)}</p><p class="small-note">${safe(source)}</p></section>`;
const dashboard = ()=>{
const s=status;
return `${headline('Teacher workspace','Science Tools','A unified home for science curriculum. This foundation is read-only and does not access student records.',pill('Foundation build','wip'))}
<div class="metric-grid"><div class="metric"><div class="metric-label">ACTIVE COURSE</div><strong class="metric-value">1</strong><span class="metric-note">Physics foundation</span></div><div class="metric"><div class="metric-label">PUBLIC PHYSICS RESOURCES</div><strong class="metric-value">${s.public_resource_count}</strong><span class="metric-note">Available in public Physics lessons</span></div><div class="metric"><div class="metric-label">INSTRUCTIONAL PLAN</div><strong class="metric-value">107</strong><span class="metric-note">Days agreed; curriculum mapping not yet imported</span></div></div>
<div class="two-col"><section class="panel"><h2>Open a workspace</h2><p>Start by browsing existing original Physics resources and reviewing which systems will connect next.</p><div class="action-grid">${card('curriculum','Curriculum Library','Search local original Physics lesson files.')}${card('courses','Courses','View course registry and readiness.')}${card('lessons','Lesson Builder','See the shared lesson-builder integration plan.')}${card('settings','System Health','Verify roots and source access.')}</div></section>
<section class="panel"><h2>Foundation status</h2><ul class="status-list">${row('Physics repository',yes(s.physics_repository_found))}${row('Public lesson assets',yes(s.physics_public_lessons_found))}${row('Existing Physics Tools',yes(s.existing_physics_tools_found))}${row('Science Tools library folder',yes(s.science_library_folder_found))}${row('District student-data import','Not connected')}</ul></section></div>
<div class="hint" style="margin-top:18px"><strong>Existing teacher work stays in place.</strong> No CPM Tools files, Physics tools, assessment evidence, contacts, grades or lesson saves were imported or changed by this foundation.</div>`;
};
const courses = ()=> `${headline('Course setup','Courses','A single configurable framework. Physics is the first mapped course; additional sciences can be registered when their curriculum sources are approved.')}
<div class="course-card"><div class="course-logo">PHY</div><div><h2>Physics</h2><p>Existing repository: <code>physics/</code> · Original interactive lessons: <code>physics/lessons/</code></p><div class="course-badges">${pill('Foundation active')}${pill('107-day plan','muted')}</div></div>${pill('Content mapping next','wip')}</div>
<div class="hint" style="margin-top:18px">Course identity and registry live in <code>config/course_registry.json</code>. Chemistry, Biology and other courses are not silently added before their source material and course requirements are confirmed.</div>`;
const curriculum = ()=> {
const hasRoot=status.physics_public_lessons_found;
return `${headline('Public resource catalog','Curriculum Library','Browse original Physics lesson assets already in the physics repository. This does not read copyrighted teacher PDFs or the private synced Drive lesson directory.',pill('Read-only'))}
<div class="filters-bar"><input id="resourceSearch" type="search" placeholder="Search title or path (for example, motion)…" aria-label="Search public Physics resources" value="${safe(query)}"><button id="resourceRefresh" type="button">Refresh list</button></div><div id="resourceSummary" class="small-note"></div><div id="resourceList" class="list" style="margin-top:12px">${hasRoot?'Loading resource list…':'<div class="empty">Public Physics lessons directory is not available on this computer.</div>'}</div>
<div class="hint" style="margin-top:20px"><strong>Next curriculum pass:</strong> Link the approved 107-day course map, Physics Classroom readings, simulations, video labs and lesson sequences. This catalog currently indexes files, not their instructional quality or coverage.</div>`;
};
const planned = (route)=>{
if(route==='lessons') return `${headline('Shared builder','Lesson Builder','One interaction model for lessons, notes, practice, simulations and video labs.',pill('Not yet connected','wip'))}
<div class="hint"><strong>Existing Physics Tools remains the functioning lesson authoring system.</strong> This build does not replace or fork it.</div><div class="feature-stack">${feature('Lesson assembly','Preserve Notes → Thinking Sheet → Lab sequencing, student/teacher versions and working linked interactives.','Future integration from the existing Physics and CPM lesson engines.')}${feature('Library save & reopen','Apply consistent lesson naming, saved versions, teacher fine-tuning and print-ready preview.','Future shared editor and local library integration.')}${feature('Student distribution','Support Notability-ready, lightweight PDFs plus original interactive links.','Physics lesson Drive and public GitHub paths remain separate.')}${feature('Labs & simulations','Index classroom simulations and video labs alongside readings.','Map against the approved Physics pacing catalog.')}</div>`;
if(route==='assessments') return `${headline('Assessment system','Assessments','Common Practice, Quick Check, Checkpoint, Test and Custom workflows.',pill('Not yet connected','wip'))}
<div class="hint"><strong>No assessment data is being read or written.</strong> This screen documents the intended shared behavior without claiming the builder is ready.</div><div class="feature-stack">${feature('Shared assessment builder','Reuse CPM Tools assessment layout, item editing, student/teacher print preview and scan-friendly output.','Shared UI contract applies to all assessment types.')}${feature('Assessment evidence','Keep per-student assessment records and teacher-reviewed decisions separate from public curriculum files.','Portfolio integration after course map and data ownership are defined.')}</div>`;
if(route==='portfolio') return `${headline('Student progression','Portfolio','Plan course-specific evidence and mastery tracking without relocating current student work.',pill('Not yet connected','wip'))}
<div class="hint"><strong>Privacy boundary:</strong> The planned MAPS Student Data folder is the authority for rosters, verified contacts, NWEA and authorized student supports. There is no active import from it in this build.</div><div class="feature-stack">${feature('Private evidence','Retain assessment scans, student progress, teacher review history and practice assignments in private, teacher-authorized storage.','No private records are bundled with GitHub or transfer packages.')}${feature('Verified directory feed','Future read-only imports of student IDs, course rosters and approved recipients.','CSV-compatible snapshots; authority remains district-maintained Google Sheets.')}</div>`;
return `${headline('Student delivery','Distribution','Separate public original interactives from private lesson documents and teacher records.',pill('Planned integration','wip'))}
<div class="two-col"><section class="panel"><h2>Public interactive resources</h2><p>Original interactives and safe public assets go in <code>physics/lessons/</code>. The local Curriculum Library can currently preview these public assets in your browser.</p><a class="link-btn" href="#curriculum">Browse resources</a></section><section class="panel"><h2>Private classroom documents</h2><p>Student and teacher PDFs, restricted purchased material, private assessments and offline copies belong in the separately approved Google Drive synced lesson location—not the public Physics repo.</p><p class="small-note">Publishing, Drive exports and Notability links are not automated by this build.</p></section></div>`;
};
const settings = ()=>{
const s=status;
return `${headline('Local environment','Settings & Diagnostics','Read-only checks of known workspace locations and integration boundaries.',pill('Local-only'))}
<div class="diagnostics"><section class="panel"><h2>Source locations</h2><div class="diag-row"><span>Workspace root</span><strong>${safe(s.workspace_label)}</strong></div><div class="diag-row"><span>Physics repository</span><strong>${yes(s.physics_repository_found)}</strong></div><div class="diag-row"><span>Original Physics lesson assets</span><strong>${yes(s.physics_public_lessons_found)}</strong></div><div class="diag-row"><span>Existing Physics Tools</span><strong>${yes(s.existing_physics_tools_found)}</strong></div><div class="diag-row"><span>SCIENCE_Tools folder</span><strong>${yes(s.science_tools_folder_found)}</strong></div><div class="diag-row"><span>SCIENCE_Tools_Library folder</span><strong>${yes(s.science_library_folder_found)}</strong></div></section>
<section class="panel"><h2>Data and permissions</h2><div class="diag-row"><span>MAPS Student Data</span><strong>Intentionally disconnected</strong></div><div class="diag-row"><span>Student records bundled</span><strong>No</strong></div><div class="diag-row"><span>Write operations</span><strong>Disabled</strong></div><div class="diag-row"><span>Network binding</span><strong>127.0.0.1 only</strong></div><div class="diag-row"><span>App state</span><strong>UI-only course selection</strong></div><button class="link-btn" id="checkAgain" style="margin-top:16px">Recheck local sources</button></section></div>
<div class="hint" style="margin-top:18px">The shared course UI CSS/JS is bundled into this standalone shell. Future science builds should connect to reusable engines rather than duplicating their backend logic.</div>`;
};
const buildResourceRows = (items)=>items.map(r=>{
const href='/public/lessons/'+r.relative_path.split('/').map(encodeURIComponent).join('/');
return `<article class="resource-row"><div><div class="resource-title">${safe(r.name)}</div><div class="resource-path">lessons/${safe(r.relative_path)}</div></div><div class="resource-type">${safe(r.type)}</div><div class="resource-actions">${r.previewable?`<a href="${href}" class="link-btn" target="_blank" rel="noopener noreferrer">Open</a>`:''}<button type="button" class="link-btn copy-path" data-path="lessons/${safe(r.relative_path)}">Copy path</button></div></article>`;
}).join('');
function renderResourceList(){
const input=document.getElementById('resourceSearch');if(!input) return;
const needle=input.value.trim().toLowerCase();query=input.value;
const matched=resources.filter(r=>!needle || (r.name+' '+r.relative_path).toLowerCase().includes(needle));
const list=document.getElementById('resourceList');const summary=document.getElementById('resourceSummary');
if(summary)summary.textContent=`${matched.length} matching resources · ${resources.length} indexed locally`;
if(list)list.innerHTML=matched.length?buildResourceRows(matched.slice(0,200)):`<div class="empty">${resources.length?'No matching resources.':'No public Physics resources found.'}</div>`;
if(matched.length>200&&summary)summary.textContent+=' · displaying first 200';
}
async function loadResources(refresh=false){
if(refresh){indexLoaded=false;resources=[];}
if(indexLoaded){renderResourceList();return;}
try{
 const response=await fetch('/api/resources?course='+encodeURIComponent(currentCourse)+'&limit=3000'+(refresh?'&refresh=1':''));
 if(!response.ok)throw Error('HTTP '+response.status);
 const data=await response.json();
 resources=Array.isArray(data.items)?data.items:[];
 indexLoaded=true;
 renderResourceList();
 if(data.truncated){const s=document.getElementById('resourceSummary');if(s)s.textContent+=' · index limit reached';}
}catch(err){const list=document.getElementById('resourceList');if(list)list.innerHTML='<div class="empty">Unable to read public lesson resources.</div>';}
}
async function updateStatus(){
try{
 const response=await fetch('/api/status');if(!response.ok)throw Error('HTTP '+response.status);
 status=await response.json();
 picker.innerHTML=(status.courses||[]).map(c=>`<option value="${safe(c.id)}">${safe(c.name)}</option>`).join('');
 if(!status.courses.some(c=>c.id===currentCourse))currentCourse='physics';
 picker.value=currentCourse;
 render();
}catch(err){el.innerHTML='<h1>Science Tools</h1><div class="hint">Unable to reach the local Science Tools server. Relaunch from the .command file.</div>';}
}
function render(){
if(!status)return;
let route=location.hash.slice(1)||'dashboard';if(!validRoutes.has(route))route='dashboard';
for(const a of document.querySelectorAll('[data-route]')){const active=a.dataset.route===route;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
const markup=route==='dashboard'?dashboard():route==='courses'?courses():route==='curriculum'?curriculum():route==='settings'?settings():planned(route);
el.innerHTML=markup;
if(route==='curriculum'){
 const input=document.getElementById('resourceSearch');input?.addEventListener('input',renderResourceList);
 document.getElementById('resourceRefresh')?.addEventListener('click',()=>loadResources(true));
 loadResources();
}
if(route==='settings')document.getElementById('checkAgain')?.addEventListener('click',async()=>{notice.textContent='Checking local sources…';await updateStatus();notice.textContent='Local status refreshed.'});
}
function saveCourse(v){currentCourse=v;try{localStorage.setItem('science-tools-course',v)}catch(e){}indexLoaded=false;resources=[];query='';render();}
window.addEventListener('hashchange',render);
picker.addEventListener('change',e=>saveCourse(e.target.value));
el.addEventListener('click',async e=>{
 const button=e.target.closest('.copy-path');if(!button)return;
 const path=button.dataset.path;
 try{await navigator.clipboard.writeText(path);notice.textContent='Copied public path: '+path;}
 catch(err){notice.textContent='Clipboard access unavailable. Path: '+path;}
});
try{currentCourse=localStorage.getItem('science-tools-course')||'physics'}catch(e){}
updateStatus();
})();
