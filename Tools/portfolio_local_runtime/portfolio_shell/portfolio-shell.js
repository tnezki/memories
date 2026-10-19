(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const NAV = {
    'scan-grade': {section:'evidence',title:'Scan & Grade',summary:'Build the existing source-level grading request from new student work.',path:'/new-evidence',live:true},
    'teacher-graded': {section:'evidence',title:'Teacher-Graded Scans',summary:'Summarize your marks without regrading.',live:false,html:'<h3>Teacher-Graded Scans</h3><p>Planned next step: upload marked papers, read your scores and annotations, and review the I Can evidence before anything enters Portfolio.</p><p>Teacher judgments remain authoritative. This workflow will use the existing grading-result approval and state update pipeline, not a second grading system.</p>'},
    'observations': {section:'evidence',title:'Observations & Checklists',summary:'Use the existing walk-around checklist and direct observation tools.',path:'/teacher-observations',live:true},
    'nwea': {section:'evidence',title:'NWEA CSV Import',summary:'Bring external assessment data into a reviewed evidence context.',live:false,html:'<h3>NWEA CSV</h3><p>Next step: select an NWEA export, validate its columns and student matches against the current roster, map relevant measurements to learning targets, then approve an import.</p><p>NWEA scores will not be treated as automatic proof of I Can mastery. The source, date, and interpretation will remain visible.</p>'},
    'reports': {section:'reporting',title:'Student & Class Reports',summary:'View the existing reports from the current local state.',path:'/reports',live:true},
    'data-protocol': {section:'reporting',title:'MAPS Formative Assessment Data Protocol',summary:'Plan template-faithful reporting using the original district Word form.',live:false,html:'<h3>MAPS Data Protocol - template mapping</h3><p>This will fill the <strong>original three-page Word template</strong> without changing its layout.</p><ul><li><strong>Part A:</strong> Learning Target(s) Assessed, examples/expectations of proficiency, and teacher scoring questions.</li><li><strong>Part B:</strong> Above/At/Below Target percentages and student groups, in the existing Teacher A-D columns.</li><li><strong>Part C:</strong> Misconceptions or extensions, student initials, instructional strategies, reassessment plans, and SMART goals for up to two targets.</li></ul><p class="note">We will discuss the comparison threshold and which fields require teacher approval before implementing the actual fill. No counts or strategies will be invented.</p>'},
    'email': {section:'reporting',title:'Email Reports - Current Workflow',summary:'Prepare selected reports using the existing local email review.',path:'/email',live:true,note:'The existing email tool includes configured student, guardian, and support contacts. Student-only recipient mode has NOT been implemented yet. Preparing PDFs does not send emails; verify recipients in the sender before delivery.'},
    'student-only': {section:'reporting',title:'Student-Only Email',summary:'Prepare individual report delivery to students only.',live:false,html:'<h3>Student-only delivery</h3><p>Next step: choose a class or individual students, select <strong>Students only</strong>, and review the recipient list and reports before delivery.</p><p>Guardian and teacher/support addresses must not be added in student-only mode. Sending always requires explicit teacher confirmation.</p>'},
    'powerschool': {section:'reporting',title:'PowerSchool Exports',summary:'Use the existing report and grade export folder.',path:'/reports',live:true,note:'In the current reports page, open PowerSchool Exports. These are generated from the authoritative current Portfolio state.'},
    'contacts': {section:'setup',title:'Contacts & Support',summary:'Maintain the existing local recipient and support directory.',path:'/contacts-support',live:true},
    'roster': {section:'setup',title:'Update Roster',summary:'Maintain class rosters without discarding historical evidence.',path:'/update-roster',live:true}
  };
  const DEFAULT = {evidence:'scan-grade',reporting:'reports',setup:'contacts'};
  const HEADINGS = {evidence:'Add Evidence',reporting:'Reporting',setup:'Course Setup'};
  const validSection = s => Object.prototype.hasOwnProperty.call(DEFAULT,s);
  const sectionFromUrl = location.pathname === '/course-setup' ? 'setup' : (validSection(params.get('section')) ? params.get('section') : 'evidence');
  let section = sectionFromUrl;
  let currentTool = NAV[params.get('tool')]?.section === section ? params.get('tool') : DEFAULT[section];
  const courseOptions = Array.from($('course').options).map(x => x.value);
  const initialCourse = params.get('course');
  $('course').value = courseOptions.includes(initialCourse) ? initialCourse : (courseOptions.includes('Algebra 1')?'Algebra 1':courseOptions[0]);
  $('unit').value = /^[1-8]$/.test(params.get('unit') || '') ? params.get('unit') : '1';
  const frame = $('workFrame');
  const contextNote = $('contextNote');
  function withContext(path) {
    const u = new URL(path, location.origin);
    u.searchParams.set('course',$('course').value);
    u.searchParams.set('unit',$('unit').value);
    return u.pathname + u.search;
  }
  function saveLocation() {
    const dest = new URL(location.href);
    dest.pathname = section === 'setup' ? '/course-setup' : '/';
    dest.search = new URLSearchParams({section,tool:currentTool,course:$('course').value,unit:$('unit').value}).toString();
    history.replaceState(null,'',dest.pathname+dest.search);
  }
  function decorateFrame() {
    // The original working pages remain authoritative; hide only their now-redundant
    // 'Portfolio Home' links in the embedded view, never modify their server code.
    try {
      const doc = frame.contentDocument;
      if (!doc) return;
      for (const a of doc.querySelectorAll('a[href="/"]')) {
        if (/portfolio home/i.test(a.textContent||'')) a.hidden = true;
      }
      // The older roster page owns its two selectors. Align them with the
      // outer shell so a teacher cannot accidentally edit a different course.
      if (currentTool === 'roster') {
        const rosterCourse = doc.getElementById('course');
        const rosterUnit = doc.getElementById('unit');
        if (rosterCourse && Array.from(rosterCourse.options).some(o => o.value === $('course').value)) rosterCourse.value = $('course').value;
        if (rosterUnit && Array.from(rosterUnit.options).some(o => o.value === $('unit').value)) rosterUnit.value = $('unit').value;
      }
      // Existing evidence pages can change their unit locally. Mirror that
      // choice in the shell without changing the request they just navigated to.
      if (currentTool === 'scan-grade' || currentTool === 'observations') {
        const u = new URL(frame.contentWindow.location.href);
        const nextUnit = u.searchParams.get('unit');
        if (/^[1-8]$/.test(nextUnit || '') && $('unit').value !== nextUnit) {
          $('unit').value = nextUnit;
          saveLocation();
        }
      }
    } catch (_) { /* Same-origin local companion pages only. */ }
  }
  frame.addEventListener('load',decorateFrame);
  function render() {
    const tool = NAV[currentTool];
    if (!tool) return;
    $('sidebarTitle').textContent = HEADINGS[section];
    $('toolGroup').textContent = HEADINGS[section].toUpperCase();
    $('toolTitle').textContent = tool.title;
    $('toolSummary').textContent = tool.summary;
    for (const button of document.querySelectorAll('[data-section]')) {
      const active = button.dataset.section === section;
      button.classList.toggle('active',active);
      button.setAttribute('aria-pressed',String(active));
    }
    for (const group of document.querySelectorAll('[data-group]')) group.hidden = group.dataset.group !== section;
    for (const button of document.querySelectorAll('[data-tool]')) {
      const active = button.dataset.tool === currentTool;
      button.classList.toggle('active',active);
      button.setAttribute('aria-current',active ? 'page' : 'false');
    }
    contextNote.hidden = !tool.note;
    contextNote.textContent = tool.note || '';
    $('shellStatus').textContent = tool.live ? 'Using the current local Portfolio tools and state.' : 'Planned workflow - no evidence or reports have been changed.';
    const standalone = $('openSeparate');
    if (tool.live) {
      const url = withContext(tool.path);
      $('placeholder').hidden = true;
      frame.hidden = false;
      if (frame.getAttribute('src') !== url) frame.setAttribute('src',url);
      standalone.hidden = false;standalone.href = url;
    } else {
      frame.hidden = true;
      frame.removeAttribute('src');
      const placeholder = $('placeholder');
      placeholder.innerHTML = tool.html;
      placeholder.hidden = false;
      standalone.hidden = true;standalone.removeAttribute('href');
    }
    saveLocation();
  }
  document.querySelectorAll('[data-section]').forEach(button=>button.addEventListener('click',()=>{
    section=button.dataset.section;currentTool=DEFAULT[section];render();
  }));
  document.querySelectorAll('[data-tool]').forEach(button=>button.addEventListener('click',()=>{
    currentTool=button.dataset.tool;section=NAV[currentTool].section;render();
  }));
  $('course').addEventListener('change',render);
  $('unit').addEventListener('change',render);
  render();
})();
