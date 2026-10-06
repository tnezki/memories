(() => {
  const INDEX_URL = '/library/textbooks/cc3e3/cards/index.json';
  const CARD_BASE = '/library/textbooks/cc3e3/cards/';
  const PACK_BASE = '/library/textbooks/cc3e3/cards/';
  const STORAGE_KEY = 'cc3e3_builder_selection_v1';
  const ORDER_KEY = 'cc3e3_builder_order_v1';
  const BREAK_KEY = 'cc3e3_builder_breaks_v1';
  const SETTINGS_KEY = 'cc3e3_builder_settings_v2';
  const CARD_OPTIONS_KEY = 'cc3e3_builder_card_options_v3';
  const CUSTOM_KEY = 'cc3e3_builder_custom_cards_v1';
  const SOURCE_OVERRIDE_KEY = 'cc3e3_builder_source_overrides_v1';
  const SECTION_HEADING_KEY = 'cc3e3_builder_section_headings_v1';
  const ASSESSMENT_HANDOFF_KEY = 'cc3e3_assessment_handoff_v1';
  const ASSESSMENT_SESSION_KEY = 'cc3e3_assessment_version_session_v1';
  const ASSESSMENT_BUNDLE_SCHEMA = 'teacher_tools_assessment_versions/1';

  const FIGURE_RATIO = {small:0.35, normal:0.55, large:0.85};
  const WORKSPACE_HEIGHT = {small:0.5, medium:1.0, large:2.0};
  const PX_PER_IN = 96;
  const DOCUMENT_SCHEMA = 'teacher_tools_document/1';
  const CORE_VERSION = 'teacher-tools-core/0.2-cc3-pilot';

  const els = {
    list: document.getElementById('assemblyList'), pages: document.getElementById('pages'),
    count: document.getElementById('assemblyCount'), pageSummary: document.getElementById('pageSummary'),
    title: document.getElementById('docTitle'), showTitle: document.getElementById('showTitle'),
    addContentBtn: document.getElementById('addContentBtn'),
    addContentMenu: document.getElementById('addContentMenu'), editorModal: document.getElementById('customEditorModal'),
    editorTitle: document.getElementById('editorTitle'), customLabel: document.getElementById('customLabel'),
    customLabelCaption: document.getElementById('customLabelCaption'), richEditor: document.getElementById('richEditor'),
    saveCustomCard: document.getElementById('saveCustomCard'), mathPanel: document.getElementById('mathPanel'),
    mathInput: document.getElementById('mathInput'), mathDisplay: document.getElementById('mathDisplay'),
    mathPreview: document.getElementById('mathPreview'),
    placementMode: document.getElementById('placementMode'), placementReference: document.getElementById('placementReference'),
    placementHint: document.getElementById('placementHint'), mathTemplateSelect: document.getElementById('mathTemplateSelect'),
    mathExampleSelect: document.getElementById('mathExampleSelect'),
    editorImageFile: document.getElementById('editorImageFile'), editorImageBtn: document.getElementById('editorImageBtn'),
    editorEyebrow: document.getElementById('editorEyebrow'), customLabelWrap: document.getElementById('customLabelWrap'),
    sectionHeadingWrap: document.getElementById('sectionHeadingWrap'), sectionHeadingInput: document.getElementById('sectionHeadingInput'),
    editorSourceNote: document.getElementById('editorSourceNote'), placementPanel: document.getElementById('placementPanel'),
    saveStatus: document.getElementById('saveStatus'), saveSet: document.getElementById('saveSet'), saveSetAs: document.getElementById('saveSetAs'),
    saveModal: document.getElementById('saveModal'), saveSetName: document.getElementById('saveSetName'), confirmSaveSet: document.getElementById('confirmSaveSet'),
    visualModal: document.getElementById('visualModal'), visualType: document.getElementById('visualType'), visualControls: document.getElementById('visualControls'),
    visualPreview: document.getElementById('visualPreview'), visualStatus: document.getElementById('visualStatus'), generateVisualBtn: document.getElementById('generateVisualBtn'), randomizeVisualBtn: document.getElementById('randomizeVisualBtn'), insertVisualBtn: document.getElementById('insertVisualBtn'), editorEditVisualBtn: document.getElementById('editorEditVisualBtn'),
    assessmentVersionPanel: document.getElementById('assessmentVersionPanel'), assessmentVersionTabs: document.getElementById('assessmentVersionTabs'), assessmentVersionSummary: document.getElementById('assessmentVersionSummary'), newAssessmentVersion: document.getElementById('newAssessmentVersion'), printAllVersions: document.getElementById('printAllVersions'), assessmentPrintAll: document.getElementById('assessmentPrintAll'),
    summativePacketPanel: document.getElementById('summativePacketPanel'), frqPacketRow: document.getElementById('frqPacketRow'), frqPacketLabel: document.getElementById('frqPacketLabel'), frqPacketVersions: document.getElementById('frqPacketVersions'), frqPacketAll: document.getElementById('frqPacketAll'), mcPacketRow: document.getElementById('mcPacketRow'), mcPacketVersions: document.getElementById('mcPacketVersions'), mcPacketAll: document.getElementById('mcPacketAll'), demoPrint: document.getElementById('demoPrint'),
    globalFigureControl: document.getElementById('globalFigureControl'), globalFigureSlider: document.getElementById('globalFigureSlider'), globalFigureOutput: document.getElementById('globalFigureOutput'),
    globalWorkspaceControl: document.getElementById('globalWorkspaceControl'), globalWorkspaceSlider: document.getElementById('globalWorkspaceSlider'), globalWorkspaceOutput: document.getElementById('globalWorkspaceOutput')
  };

  let indexMap = new Map();
  let cards = new Map();
  let loadedPacks = new Map();
  let order = JSON.parse(localStorage.getItem(ORDER_KEY) || localStorage.getItem(STORAGE_KEY) || '[]');
  let breaks = new Set(JSON.parse(localStorage.getItem(BREAK_KEY) || '[]'));
  let settings = Object.assign({
    spacing:'normal', margin:'normal', figure:'normal', workspace:'medium', figurePx:null, workspaceIn:null,
    title:'Chapter 1 Practice', showTitle:true
  }, JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}'));
  let cardOptions = JSON.parse(localStorage.getItem(CARD_OPTIONS_KEY) || '{}');
  let customCards = JSON.parse(localStorage.getItem(CUSTOM_KEY) || '{}');
  let sourceOverrides = JSON.parse(localStorage.getItem(SOURCE_OVERRIDE_KEY) || '{}');
  let sectionHeadings = JSON.parse(localStorage.getItem(SECTION_HEADING_KEY) || '{}');
  let paginateTimer = null;
  let editingCustomId = null;
  let editingSourceId = null;
  let editingCustomType = 'problem';
  let savedEditorRange = null;
  let mathPreviewTimer = null;
  const launchParams = new URLSearchParams(location.search);
  let currentSavedSetId = launchParams.get('set') || null;
  const handoffSource = launchParams.get('handoff') || null;
  let currentSavedSetName = '';
  let saveAsMode = false;
  let visualTargetId = null;
  let editingVisualIndex = null;
  let pendingVisual = null;
  let visualInsertMode = 'card';
  let editorVisualEditNode = null;
  let assessmentBundle = null;
  let assessmentActiveIndex = 0;
  let printingAllAssessmentVersions = false;

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order.filter(id => !isCustomId(id))));
    localStorage.setItem(ORDER_KEY, JSON.stringify(order));
    localStorage.setItem(BREAK_KEY, JSON.stringify([...breaks]));
    settings.title = els.title.value;
    settings.showTitle = els.showTitle.checked;
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    localStorage.setItem(CARD_OPTIONS_KEY, JSON.stringify(cardOptions));
    localStorage.setItem(CUSTOM_KEY, JSON.stringify(customCards));
    localStorage.setItem(SOURCE_OVERRIDE_KEY, JSON.stringify(sourceOverrides));
    localStorage.setItem(SECTION_HEADING_KEY, JSON.stringify(sectionHeadings));
    persistAssessmentActiveRecipe();
    if(currentSavedSetId) updateSaveStatus(`Unsaved changes: ${currentSavedSetName || 'Library item'}`,false);
  }

  function escapeHtml(s='') { return String(s).replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c])); }
  function isCustomId(id) { return String(id).startsWith('custom-'); }
  function isQuestionMeta(meta) { return meta && (meta.card_type === 'question' || meta.card_type === 'custom_problem'); }
  const SECTION_STYLE = {
    'Launch':'launch',
    'Closure':'closure',
    'Explore':'explore',
    'Methods & Meanings':'methods',
    'Review & Preview':'review'
  };

  function sourceOverride(id) { return !isCustomId(id) ? (sourceOverrides[id] || null) : null; }
  function effectiveCardHtml(id) {
    const data=cards.get(id);
    if(!data) return '';
    return sourceOverride(id)?.html ?? data.html ?? '';
  }
  function sectionKey(meta) {
    return meta && SECTION_STYLE[meta.section] ? `${meta.lesson}::${meta.section}` : '';
  }
  function sectionHeading(meta) {
    const key=sectionKey(meta);
    return key ? (sectionHeadings[key] || meta.section) : '';
  }
  function sectionStyle(meta) { return meta ? (SECTION_STYLE[meta.section] || '') : ''; }
  function sameSection(aId,bId) {
    const a=indexMap.get(aId), b=indexMap.get(bId);
    return !!a && !!b && !!sectionKey(a) && sectionKey(a)===sectionKey(b);
  }

  function sanitizeTeacherHtml(html='') {
    const box = document.createElement('div');
    box.innerHTML = html;
    box.querySelectorAll('script,style,iframe,object,embed,form,input,button,textarea,select').forEach(n => n.remove());
    box.querySelectorAll('*').forEach(node => {
      [...node.attributes].forEach(attr => {
        const n = attr.name.toLowerCase();
        const v = attr.value.trim().toLowerCase();
        if (n.startsWith('on') || (['href','src'].includes(n) && v.startsWith('javascript:'))) node.removeAttribute(attr.name);
      });
    });
    // MathJax replaces TeX text with rendered markup while editing. Before a
    // teacher-created card is stored, restore each formula to its compact,
    // editable TeX source. This keeps saved cards deterministic and prevents
    // caret/selection state from leaking into the stored HTML.
    box.querySelectorAll('.teacher-math[data-tex]').forEach(span => {
      const tex = normalizeLegacyMathTex(span.dataset.tex || '');
      const display = span.dataset.display === 'block';
      span.dataset.tex = tex;
      span.dataset.display = display ? 'block' : 'inline';
      span.setAttribute('contenteditable','false');
      span.setAttribute('spellcheck','false');
      span.textContent = display ? `\\[${tex}\\]` : `\\(${tex}\\)`;
    });
    return box.innerHTML;
  }

  function normalizeSubparts(root) {
    [...root.querySelectorAll('h3,h4')].forEach(label => {
      const txt = label.textContent.trim();
      if (!/^[a-z]\.$/i.test(txt)) return;
      let body = label.nextElementSibling;
      while (body && !body.textContent.trim() && !body.querySelector('img,table,svg,math')) body = body.nextElementSibling;
      if (!body || body.classList.contains('subpart-row')) return;
      const row = document.createElement('div');
      row.className = 'subpart-row';
      const lab = document.createElement('div');
      lab.className = 'subpart-label';
      lab.textContent = txt;
      const wrap = document.createElement('div');
      wrap.className = 'subpart-body';
      label.parentNode.insertBefore(row, label);
      row.append(lab, wrap);
      wrap.appendChild(body);
      label.remove();
    });
  }

  function normalizeContent(root) {
    root.querySelectorAll('img[data-missing-src], img:not([src])').forEach(img => img.remove());
    root.querySelectorAll('[style]').forEach(node => {
      if (node.classList.contains('teacher-math')) return;
      node.style.removeProperty('font-size');
      node.style.removeProperty('line-height');
      node.style.removeProperty('font-family');
      node.style.removeProperty('letter-spacing');
      if (!node.getAttribute('style')?.trim()) node.removeAttribute('style');
    });
    root.querySelectorAll('a').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
    normalizeSubparts(root);
  }

  function optionsFor(id) {
    if (!cardOptions[id]) cardOptions[id] = {workspace:null, figures:{}, visuals:[]};
    if (!cardOptions[id].figures) cardOptions[id].figures = {};
    if (!Array.isArray(cardOptions[id].visuals)) cardOptions[id].visuals = [];
    if ('plane' in cardOptions[id]) delete cardOptions[id].plane;
    return cardOptions[id];
  }

  function isAdjustableImage(img) {
    const src = img.getAttribute('src') || '';
    const alt = img.getAttribute('alt') || '';
    if (/CPM\.svg|Caret|ExternalLink|languageObjective|majorConceptualIdeas|standardsForMathematicalPractice|launch-rocket|closure-flag/i.test(src)) return false;
    if (/decorative icon/i.test(alt)) return false;
    return true;
  }

  function visualFigureUnits(root) {
    const nodes=[...root.querySelectorAll('img[src]:not([data-missing-src]), svg[role="img"], svg.graph, svg.choice-graph')];
    const units=[];
    const seenChoiceContainers=new Set();
    nodes.forEach(node=>{
      if(node.tagName.toLowerCase()==='img'){
        if(isAdjustableImage(node)) units.push({nodes:[node],kind:'figure',label:node.getAttribute('alt')||''});
        return;
      }
      if(node.closest('mjx-container,.teacher-math')) return;
      if(node.classList.contains('choice-graph')){
        const container=node.closest('ol.choices,ul.choices') || node.parentElement;
        if(seenChoiceContainers.has(container)) return;
        seenChoiceContainers.add(container);
        const group=[...container.querySelectorAll('svg.choice-graph')];
        units.push({nodes:group.length?group:[node],kind:'choice-graphs',label:'Choice graphs'});
        return;
      }
      units.push({nodes:[node],kind:'figure',label:node.getAttribute('aria-label')||''});
    });
    return units;
  }

  function sourceFigureUnits(id) {
    const data = cards.get(id);
    if (!data) return [];
    const tmp = document.createElement('div');
    tmp.innerHTML = effectiveCardHtml(id);
    normalizeContent(tmp);
    return visualFigureUnits(tmp);
  }

  function sourceImageCount(id) { return sourceFigureUnits(id).length; }

  function sourceFigureLabel(id, idx) {
    const unit=sourceFigureUnits(id)[idx];
    if(!unit) return `Fig ${idx+1}`;
    if(unit.kind==='choice-graphs') return 'Choice graphs';
    return `Fig ${idx+1}`;
  }

  function attachedVisuals(id) { return optionsFor(id).visuals; }
  function cardImageCount(id) { return sourceImageCount(id) + attachedVisuals(id).length; }
  function isAttachedVisualIndex(id, idx) { return idx >= sourceImageCount(id); }
  function attachedVisualIndex(id, idx) { return idx - sourceImageCount(id); }

  function pageContentWidthPx() {
    const margins = {narrow:0.42, normal:0.58, wide:0.78};
    const side = margins[settings.margin] ?? margins.normal;
    return Math.round((8.5 - 2 * side) * PX_PER_IN);
  }

  function globalFigurePx() {
    const max = pageContentWidthPx();
    if (settings.figurePx !== null && settings.figurePx !== '' && Number.isFinite(Number(settings.figurePx))) {
      return Math.max(0, Math.min(max, Math.round(Number(settings.figurePx))));
    }
    const ratio = FIGURE_RATIO[settings.figure] ?? FIGURE_RATIO.normal;
    return Math.round(max * ratio / 10) * 10;
  }

  function effectiveFigurePx(id, idx) {
    const value = Number(optionsFor(id).figures?.[idx]);
    let raw;
    if(Number.isFinite(value)) raw=value;
    else {
      const unit=sourceFigureUnits(id)[idx];
      raw=unit?.kind==='choice-graphs' ? Math.min(180,Math.max(110,Math.round(globalFigurePx()*0.4))) : globalFigurePx();
    }
    return Math.max(0, Math.min(pageContentWidthPx(), Math.round(raw)));
  }

  function applyFigureSize(node, px) {
    if(!node) return;
    if(px<=0){ node.style.display='none'; return; }
    node.style.display='block';
    node.style.width=`${px}px`;
    node.style.maxWidth='100%';
    node.style.height='auto';
    node.style.maxHeight='none';
    node.dataset.figureWidthPx=String(px);
  }

  function globalWorkspaceIn() {
    if (settings.workspaceIn !== null && settings.workspaceIn !== '' && Number.isFinite(Number(settings.workspaceIn))) {
      return Math.max(0, Math.min(5, Number(settings.workspaceIn)));
    }
    return WORKSPACE_HEIGHT[settings.workspace] || 1.0;
  }
  function effectiveWorkspaceIn(id) {
    const value = Number(optionsFor(id).workspace);
    return Number.isFinite(value) ? Math.max(0, Math.min(5, value)) : globalWorkspaceIn();
  }

  function problemLabel(meta, data, id=null) {
    if (meta.card_type === 'custom_problem') return (data.problem_label || '').trim();
    const override=id ? sourceOverride(id) : null;
    return String(override?.problem_label ?? meta.title ?? '').trim();
  }

  function customMeta(data) {
    const label = (data.problem_label || data.label || '').trim();
    const fallback = data.card_type === 'custom_problem' ? 'Custom problem' : data.card_type === 'custom_heading' ? 'Custom heading' : 'Directions / text';
    return {
      card_id: data.card_id,
      title: label || fallback,
      lesson: data.lesson || 'Custom', section: data.section || 'Teacher', card_type: data.card_type, path: null
    };
  }

  function repairLegacyMathMarkup(html) {
    const tmp=document.createElement('div');
    tmp.innerHTML=html || '';
    let changed=false;
    tmp.querySelectorAll('.teacher-math[data-tex]').forEach(span=>{
      const before=span.dataset.tex || '';
      const tex=normalizeLegacyMathTex(before);
      const display=span.dataset.display==='block';
      if(tex!==before){ span.dataset.tex=tex; changed=true; }
      if(span.getAttribute('contenteditable')!=='false'){ span.setAttribute('contenteditable','false'); changed=true; }
      if(span.getAttribute('spellcheck')!=='false'){ span.setAttribute('spellcheck','false'); changed=true; }
      const expected=display ? `\\[${tex}\\]` : `\\(${tex}\\)`;
      if(span.textContent!==expected || span.querySelector('mjx-container')){ span.textContent=expected; changed=true; }
    });
    return {html:tmp.innerHTML,changed};
  }

  function installCustomCards() {
    let repaired=false;
    Object.values(customCards).forEach(data => {
      if (!data || !data.card_id) return;
      const fixed=repairLegacyMathMarkup(data.html);
      if(fixed.changed){ data.html=fixed.html; repaired=true; }
      indexMap.set(data.card_id, customMeta(data));
      cards.set(data.card_id, data);
    });
    if(repaired) localStorage.setItem(CUSTOM_KEY, JSON.stringify(customCards));
  }

  function renderList() {
    els.count.textContent = `${order.length} card${order.length===1?'':'s'}`;
    els.list.innerHTML = '';
    if (!order.length) {
      els.list.innerHTML = '<div class="assembly-empty">No cards selected. Return to the picker or add teacher-created content.</div>';
      return;
    }
    order.forEach((id, i) => {
      const meta = indexMap.get(id); if (!meta) return;
      const data = cards.get(id);
      const assessmentQuestion = !!(data?.assessment_family_id && data?.assessment_family_snapshot && meta.card_type === 'custom_problem');
      const imgCount = cardImageCount(id);
      const sourceCount = sourceImageCount(id);
      const isQuestion = isQuestionMeta(meta);
      const row = document.createElement('div'); row.className = `assembly-item${breaks.has(id) ? ' break-before' : ''}`;
      const figureMax = pageContentWidthPx();
      const figureRows = Array.from({length:imgCount}, (_, idx) => {
        const value = effectiveFigurePx(id, idx);
        const attached = isAttachedVisualIndex(id, idx);
        const visual = attached ? attachedVisuals(id)[attachedVisualIndex(id, idx)] : null;
        const label = attached ? (visual?.label || `Inserted visual ${attachedVisualIndex(id, idx)+1}`) : sourceFigureLabel(id,idx);
        return `
        <div class="mini-control-row figure-control${attached?' inserted-visual-control':''}" data-figure-index="${idx}">
          <span title="${escapeHtml(label)}">${escapeHtml(label)}</span>
          <input class="layout-slider figure-slider" type="range" min="0" max="${figureMax}" step="10" value="${value}" aria-label="${escapeHtml(label)} width">
          <output>${value} px</output>
          <div class="range-nudges" aria-label="${escapeHtml(label)} fine adjustment">
            <button class="range-nudge" type="button" data-delta="-1" title="Decrease">−</button>
            <button class="range-nudge" type="button" data-delta="1" title="Increase">+</button>
            <select class="range-step" aria-label="Figure adjustment step"><option value="1">1</option><option value="5">5</option><option value="10" selected>10</option><option value="25">25</option></select>
          </div>
          ${attached?'<button class="visual-edit-btn" type="button" title="Edit visual">Edit visual</button><button class="visual-remove-btn" type="button" title="Remove visual">×</button>':''}
        </div>`;
      }).join('');
      const questionRow = isQuestion ? (() => {
        const value = effectiveWorkspaceIn(id);
        return `
        <div class="mini-control-row workspace-control">
          <span>Workspace</span>
          <input class="layout-slider workspace-slider" type="range" min="0" max="5" step="0.25" value="${value}" aria-label="Question workspace height">
          <output>${formatInches(value)} in</output>
          <div class="range-nudges" aria-label="Workspace fine adjustment">
            <button class="range-nudge" type="button" data-delta="-1" title="Decrease">−</button>
            <button class="range-nudge" type="button" data-delta="1" title="Increase">+</button>
            <select class="range-step" aria-label="Workspace adjustment step"><option value="0.25" selected>.25</option><option value="0.5">.5</option><option value="1">1</option></select>
          </div>
        </div>`;
      })() : '';
      const edited = !isCustomId(id) && !!sourceOverride(id);
      const sectionEdited = !isCustomId(id) && !!sectionKey(meta) && !!sectionHeadings[sectionKey(meta)] && sectionHeadings[sectionKey(meta)] !== meta.section;
      const editTitle = isCustomId(id) ? 'Edit teacher-created card' : 'Edit this card for this document';
      const restoreBtn = (!isCustomId(id) && (edited || sectionEdited)) ? '<button class="restore-btn" type="button">Restore original</button>' : '';
      row.innerHTML = `
        <div class="assembly-item-main"><div class="assembly-item-title">${escapeHtml(meta.title)}${(edited||sectionEdited)?'<span class="edited-badge">Edited</span>':''}</div><div class="assembly-item-meta">${escapeHtml(meta.lesson)} · ${escapeHtml(meta.card_type.replace('_',' '))}</div></div>
        <div class="assembly-item-actions">
          <button class="icon-btn up" title="Move up" ${i===0?'disabled':''}>↑</button>
          <button class="icon-btn down" title="Move down" ${i===order.length-1?'disabled':''}>↓</button>
          <button class="icon-btn edit" title="${editTitle}">✎</button>
          <button class="icon-btn remove" title="Remove">×</button>
        </div>
        <div class="card-layout-controls">${figureRows}${questionRow}${assessmentQuestion?'<button class="new-question-btn" type="button">↻ New question</button>':''}<button class="insert-visual-btn" type="button">+ Insert visual / printable</button></div>
        <div class="assembly-item-bottom">
          <button class="break-btn${breaks.has(id)?' active':''}">${breaks.has(id)?'Page break before':'Add page break before'}</button>
          ${restoreBtn}
        </div>`;
      row.querySelector('.up').onclick = () => move(i,-1);
      row.querySelector('.down').onclick = () => move(i,1);
      row.querySelector('.remove').onclick = () => removeCard(id, i);
      row.querySelector('.edit')?.addEventListener('click', () => isCustomId(id) ? openCustomEditor(null, id) : openSourceEditor(id));
      row.querySelector('.restore-btn')?.addEventListener('click', () => restoreSourceCard(id));
      row.querySelector('.break-btn').onclick = () => { breaks.has(id)?breaks.delete(id):breaks.add(id); save(); renderAll(); };
      row.querySelector('.new-question-btn')?.addEventListener('click',()=>regenerateAssessmentQuestion(id));
      row.querySelector('.insert-visual-btn').onclick = () => openVisualBuilder(id);
      row.querySelectorAll('.figure-control').forEach(control => {
        const idx=Number(control.dataset.figureIndex);
        const slider=control.querySelector('.figure-slider');
        const output=control.querySelector('output');
        const commitFigureValue=(next)=>{
          const min=Number(slider.min||0),max=Number(slider.max||figureMax);
          const value=Math.max(min,Math.min(max,Number(next)));
          slider.value=String(value);
          optionsFor(id).figures[idx]=value;
          output.textContent=`${value} px`;
          save(); schedulePaginate();
        };
        slider.oninput=()=>commitFigureValue(slider.value);
        control.querySelectorAll('.range-nudge').forEach(btn=>btn.addEventListener('click',()=>{
          const step=Number(control.querySelector('.range-step')?.value||10);
          commitFigureValue(Number(slider.value)+Number(btn.dataset.delta||0)*step);
        }));
        control.querySelector('.range-step')?.addEventListener('change',e=>{slider.step=String(e.target.value)});
        if(isAttachedVisualIndex(id, idx)){
          const vIdx=attachedVisualIndex(id, idx);
          control.querySelector('.visual-edit-btn')?.addEventListener('click',()=>openVisualBuilder(id,vIdx));
          control.querySelector('.visual-remove-btn')?.addEventListener('click',()=>{
            attachedVisuals(id).splice(vIdx,1);
            const next={};
            Object.entries(optionsFor(id).figures||{}).forEach(([k,v])=>{
              const n=Number(k);
              if(n<idx) next[n]=v;
              else if(n>idx) next[n-1]=v;
            });
            optionsFor(id).figures=next;
            save();renderAll();
          });
        }
      });
      if(isQuestion){
        const slider=row.querySelector('.workspace-slider');
        const output=row.querySelector('.workspace-control output');
        const control=row.querySelector('.workspace-control');
        const commitWorkspaceValue=(next)=>{
          const min=Number(slider.min||0),max=Number(slider.max||5);
          const value=Math.max(min,Math.min(max,Number(next)));
          slider.value=String(value);
          optionsFor(id).workspace=value;
          output.textContent=`${formatInches(value)} in`;
          save(); schedulePaginate();
        };
        slider.oninput=()=>commitWorkspaceValue(slider.value);
        control.querySelectorAll('.range-nudge').forEach(btn=>btn.addEventListener('click',()=>{
          const step=Number(control.querySelector('.range-step')?.value||0.25);
          commitWorkspaceValue(Number(slider.value)+Number(btn.dataset.delta||0)*step);
        }));
        control.querySelector('.range-step')?.addEventListener('change',e=>{slider.step=String(e.target.value)});
      }
      els.list.appendChild(row);
    });
  }

  function assessmentAnswerHtml(number, answer, solution){
    const a=escapeHtml(answer||''); const s=escapeHtml(solution||'');
    return `<p><strong>${number}.</strong> ${a}</p>${s?`<p>${s}</p>`:''}`;
  }

  function assessmentFamilyUsedSignatures(familyId){
    const out=[];
    (assessmentBundle?.recipes||[]).forEach(recipe=>{
      Object.values(recipe?.custom_cards||{}).forEach(card=>{
        if(card?.card_type!=='custom_problem' || card?.assessment_family_id!==familyId) return;
        out.push(card.assessment_variant_signature || `${card.html||''}\n${card.assessment_variant_answer||''}`);
      });
    });
    return out.filter(Boolean);
  }

  function regenerateAssessmentQuestion(id){
    const data=customCards[id];
    const family=data?.assessment_family_snapshot;
    const engine=window.CC3AssessmentVariants;
    if(!data || !family || !engine?.build){ alert('This question does not have a same-family generator attached.'); return; }
    const max=Math.max(2,Number(engine.MAX_VARIANTS)||8);
    let next=(Number(data.assessment_variant_index)||0)+1;
    if(next>=max) next=1;
    const slot=Math.max(0,(parseInt(String(data.problem_label||'1'),10)||1)-1);
    const used=[...assessmentFamilyUsedSignatures(data.assessment_family_id),data.assessment_variant_signature||`${data.html||''}\n${data.assessment_variant_answer||''}`];
    const instance=engine.buildUnique?engine.buildUnique(family,next,slot,used):engine.build(family,next,slot);
    const sig=instance.signature||(engine.signature?engine.signature(instance):`${instance.student_html||''}\n${instance.answer||''}`);
    data.html=instance.student_html||data.html;
    data.assessment_variant_index=instance.variant_index??next;
    data.assessment_variant_signature=sig;
    data.assessment_variant_answer=instance.answer||'';
    data.assessment_variant_solution=instance.solution||'';
    const keyId=data.assessment_key_card_id;
    if(keyId && customCards[keyId]){
      const key=customCards[keyId];
      key.assessment_variant_index=data.assessment_variant_index;
      key.html=assessmentAnswerHtml(slot+1,instance.answer,instance.solution);
    }
    save(); renderAll();
  }

  function formatInches(value) {
    const n = Number(value);
    if (Number.isInteger(n)) return String(n);
    return n.toFixed(2).replace(/0$/,'').replace(/\.0$/,'');
  }

  function removeCard(id, i) {
    breaks.delete(id);
    delete cardOptions[id];
    order.splice(i,1);
    if (isCustomId(id)) {
      delete customCards[id];
      indexMap.delete(id);
      cards.delete(id);
    }
    save(); renderAll();
  }

  function move(i, delta) {
    const j=i+delta; if(j<0||j>=order.length) return;
    [order[i],order[j]]=[order[j],order[i]]; save(); renderAll();
  }

  function appendAttachedVisuals(root, id) {
    const offset=sourceImageCount(id);
    attachedVisuals(id).forEach((visual,vi)=>{
      if(!visual?.url) return;
      const wrap=document.createElement('div'); wrap.className='inserted-visual';
      const img=document.createElement('img');
      img.src=visual.url; img.alt=visual.label || 'Inserted classroom visual';
      const px=effectiveFigurePx(id,offset+vi);
      applyFigureSize(img,px);
      wrap.appendChild(img); root.appendChild(wrap);
    });
  }

  function makePrintCard(id, orderIndex=-1) {
    const meta=indexMap.get(id), data=cards.get(id);
    const el=document.createElement('section');
    const style=sectionStyle(meta);
    const prevId=orderIndex>0 ? order[orderIndex-1] : null;
    const nextId=orderIndex>=0 && orderIndex<order.length-1 ? order[orderIndex+1] : null;
    const sectionStart=!!style && !sameSection(prevId,id);
    const sectionEnd=!!style && !sameSection(id,nextId);
    el.className='print-card'; el.dataset.type=meta.card_type; el.dataset.id=id;
    if(style){
      el.classList.add('section-grouped',`section-${style}`);
      if(sectionStart) el.classList.add('section-start');
      if(sectionEnd) el.classList.add('section-end');
      if(sectionStart){
        const heading=document.createElement('div');
        heading.className='section-heading';
        heading.textContent=sectionHeading(meta);
        el.appendChild(heading);
      }
    }

    const body=document.createElement('div');
    body.className='print-card-body';
    body.innerHTML=isCustomId(id) ? sanitizeTeacherHtml(data.html || '') : effectiveCardHtml(id);
    normalizeContent(body);
    visualFigureUnits(body).forEach((unit,idx)=>{
      const px=effectiveFigurePx(id,idx);
      unit.nodes.forEach(node=>applyFigureSize(node,px));
    });

    appendAttachedVisuals(body,id);

    if (isQuestionMeta(meta)) {
      const shell=document.createElement('div'); shell.className='question-grid';
      const number=document.createElement('div'); number.className='problem-number'; number.textContent=problemLabel(meta,data,id);
      const content=document.createElement('div'); content.className='problem-content'; content.appendChild(body);
      shell.append(number,content); el.appendChild(shell);
      const workspace=document.createElement('div');
      workspace.className='question-workspace question-workspace-indented';
      workspace.style.height=`${effectiveWorkspaceIn(id)}in`;
      el.appendChild(workspace);
    } else {
      el.appendChild(body);
    }
    return el;
  }

  function assessmentHeaderMeta(){
    const origin=assessmentBundle?.origin||{};
    const rawTitle=String(settings.title||origin.base_title||'Assessment').trim();
    const title=(rawTitle.replace(/\s*[-–—]\s*Version\s+[A-H]\s*$/i,'').trim()||String(origin.base_title||'Assessment').trim()||'Assessment');
    const course=String(origin.course_label||'Core Connections Course 3').trim();
    const scopeTitle=String(origin.scope_title||'').trim();
    return {title,subtitle:scopeTitle?`${course} — ${scopeTitle}`:course,version:assessmentVersionLabel(assessmentActiveIndex)};
  }

  function newPaper(pageNo, first=false, manual=false) {
    const paper=document.createElement('div');
    paper.className=`paper margin-${settings.margin} spacing-${settings.spacing}`;
    const inner=document.createElement('div'); inner.className='paper-inner';
    if(first && assessmentBundle){
      const meta=assessmentHeaderMeta();
      const header=document.createElement('div'); header.className='assessment-print-header';
      const left=document.createElement('div'); left.className='assessment-header-left';
      if(settings.showTitle){
        const title=document.createElement('div'); title.className='assessment-header-title'; title.textContent=meta.title;
        const subtitle=document.createElement('div'); subtitle.className='assessment-header-subtitle'; subtitle.textContent=meta.subtitle;
        left.append(title,subtitle);
      }
      const divider=document.createElement('div'); divider.className='assessment-header-divider';
      const right=document.createElement('div'); right.className='assessment-header-right';
      const name=document.createElement('div'); name.className='assessment-header-name'; name.innerHTML='<span class="assessment-name-label">Name:</span><span class="assessment-name-line"></span>';
      const version=document.createElement('div'); version.className='assessment-header-version'; version.textContent=`Version ${meta.version}`;
      right.append(name,version); header.append(left,divider,right); inner.appendChild(header);
    } else if(first && settings.showTitle && settings.title.trim()){
      const h=document.createElement('div');h.className='doc-title';h.textContent=settings.title.trim();inner.appendChild(h);
    }
    if(manual){ const rib=document.createElement('div');rib.className='manual-break-ribbon';rib.textContent='PAGE BREAK';paper.appendChild(rib); }
    const num=document.createElement('div');num.className='page-number';num.textContent=pageNo;paper.append(inner,num);els.pages.appendChild(paper);
    return {paper,inner};
  }

  function paginate() {
    els.pages.innerHTML='';
    if(!order.length){
      els.pages.innerHTML='<div class="empty-state" style="width:min(700px,100%)">Choose textbook cards or add teacher-created content to see the Letter-page assembly preview.</div>';
      els.pageSummary.textContent='0 pages'; return;
    }
    let pageNo=1; let page=newPaper(pageNo,true,false);
    const maxH=page.inner.clientHeight;
    order.forEach((id, idx) => {
      const manual=breaks.has(id) && idx>0;
      if(manual){ pageNo++; page=newPaper(pageNo,false,true); }
      const card=makePrintCard(id, idx); page.inner.appendChild(card);
      if(card.scrollHeight > maxH){
        const warning=document.createElement('div');warning.className='oversize-warning';warning.textContent='This card is taller than one printable page. Reduce figures/workspace or split the content.';card.prepend(warning);
      }
      const headerCount = pageNo===1 ? ((settings.showTitle && settings.title.trim()?1:0) + (assessmentBundle?1:0)) : 0;
      if(page.inner.scrollHeight > page.inner.clientHeight + 1 && page.inner.children.length > headerCount+1){
        page.inner.removeChild(card);
        pageNo++; page=newPaper(pageNo,false,false); page.inner.appendChild(card);
      }
    });
    els.pageSummary.textContent=`${pageNo} page${pageNo===1?'':'s'}`;
    els.pages.querySelectorAll('img').forEach(img=>{
      if(!img.complete) img.addEventListener('load', schedulePaginate,{once:true});
    });
    typesetPages();
  }

  function typesetPages() {
    if (!window.MathJax?.typesetPromise) return Promise.resolve();
    window.MathJax.typesetClear?.([els.pages]);
    return window.MathJax.typesetPromise([els.pages]).catch(err => console.warn('Math typeset failed', err));
  }

  function schedulePaginate(){ clearTimeout(paginateTimer); paginateTimer=setTimeout(paginate,120); }
  function renderAll(){renderList();schedulePaginate();}

  function syncControls(){
    els.title.value=settings.title;els.showTitle.checked=settings.showTitle!==false;
    document.querySelectorAll('.segmented').forEach(group=>group.querySelectorAll('button').forEach(btn=>btn.classList.toggle('active',btn.dataset.value===settings[group.dataset.setting])));
    if(els.globalFigureSlider){
      const max=pageContentWidthPx();
      const value=globalFigurePx();
      els.globalFigureSlider.max=String(max);
      els.globalFigureSlider.value=String(value);
      if(els.globalFigureOutput) els.globalFigureOutput.value=`${value} px`;
    }
    if(els.globalWorkspaceSlider){
      const value=globalWorkspaceIn();
      els.globalWorkspaceSlider.value=String(value);
      if(els.globalWorkspaceOutput) els.globalWorkspaceOutput.value=`${Number(value.toFixed(2))} in`;
    }
  }

  function bindGlobalRangeControls(){
    if(els.globalFigureControl && els.globalFigureSlider){
      const slider=els.globalFigureSlider, output=els.globalFigureOutput;
      const commit=value=>{
        const min=Number(slider.min||0), max=Number(slider.max||pageContentWidthPx());
        value=Math.max(min,Math.min(max,Math.round(Number(value)||0)));
        slider.value=String(value); settings.figurePx=value;
        if(output) output.value=`${value} px`;
        save(); renderAll();
      };
      slider.addEventListener('input',()=>commit(slider.value));
      els.globalFigureControl.querySelectorAll('.range-nudge').forEach(btn=>btn.addEventListener('click',()=>{
        const step=Number(els.globalFigureControl.querySelector('.range-step')?.value||10);
        commit(Number(slider.value)+Number(btn.dataset.delta||0)*step);
      }));
      els.globalFigureControl.querySelector('.range-step')?.addEventListener('change',e=>{slider.step=String(e.target.value)});
    }
    if(els.globalWorkspaceControl && els.globalWorkspaceSlider){
      const slider=els.globalWorkspaceSlider, output=els.globalWorkspaceOutput;
      const commit=value=>{
        const min=Number(slider.min||0), max=Number(slider.max||5);
        value=Math.max(min,Math.min(max,Math.round((Number(value)||0)*100)/100));
        slider.value=String(value); settings.workspaceIn=value;
        if(output) output.value=`${Number(value.toFixed(2))} in`;
        save(); renderAll();
      };
      slider.addEventListener('input',()=>commit(slider.value));
      els.globalWorkspaceControl.querySelectorAll('.range-nudge').forEach(btn=>btn.addEventListener('click',()=>{
        const step=Number(els.globalWorkspaceControl.querySelector('.range-step')?.value||0.25);
        commit(Number(slider.value)+Number(btn.dataset.delta||0)*step);
      }));
      els.globalWorkspaceControl.querySelector('.range-step')?.addEventListener('change',e=>{slider.step=String(e.target.value)});
    }
  }

  function newCustomId() { return `custom-${Date.now()}-${Math.random().toString(36).slice(2,8)}`; }

  function placementLabel(id) {
    const meta=indexMap.get(id);
    if(!meta) return id;
    const type=String(meta.card_type || '').replace(/_/g,' ');
    const title=String(meta.title || '').trim() || type || 'Card';
    return `${title}${isCustomId(id)?' (custom)':''}`;
  }

  function populatePlacementControls(editingId=null) {
    const ids=order.filter(id=>id!==editingId && indexMap.has(id));
    els.placementReference.innerHTML='';
    ids.forEach(id=>{
      const o=document.createElement('option'); o.value=id; o.textContent=placementLabel(id); els.placementReference.appendChild(o);
    });
    const keep=els.placementMode.querySelector('option[value="keep"]');
    keep.hidden=!editingId;
    if(!ids.length){
      els.placementMode.value=editingId?'keep':'after';
      els.placementMode.disabled=!editingId;
      els.placementReference.disabled=true;
    }else if(editingId){
      els.placementMode.disabled=false; els.placementMode.value='keep'; els.placementReference.disabled=true;
      const currentIndex=order.indexOf(editingId);
      const preferred=order[currentIndex-1] || order[currentIndex+1] || ids[ids.length-1];
      if(preferred && ids.includes(preferred)) els.placementReference.value=preferred;
    }else{
      els.placementMode.disabled=false; els.placementMode.value='after'; els.placementReference.disabled=false;
      els.placementReference.value=ids[ids.length-1];
    }
    updatePlacementHint();
  }

  function updatePlacementHint() {
    const mode=els.placementMode.value;
    const ref=els.placementReference.value;
    els.placementReference.disabled = mode==='keep' || !els.placementReference.options.length;
    if(!els.placementReference.options.length){
      els.placementHint.textContent = editingCustomId ? 'This card will stay in its current position.' : 'The document is empty, so this card will be placed first.';
      return;
    }
    if(mode==='keep'){ els.placementHint.textContent='This card will stay in its current position.'; return; }
    els.placementHint.textContent=`This card will be placed ${mode} ${placementLabel(ref)}.`;
  }

  function applyCustomPlacement(id, isNew) {
    const mode=els.placementMode.value;
    const ref=els.placementReference.value;
    if(!isNew && mode==='keep') return;
    const current=order.indexOf(id);
    if(current>=0) order.splice(current,1);
    if(!ref || !order.includes(ref)){ order.push(id); return; }
    const refIndex=order.indexOf(ref);
    order.splice(mode==='before'?refIndex:refIndex+1,0,id);
  }

  function resetMathEditorPanel() {
    els.mathPanel.hidden=true; els.mathInput.value=''; els.mathDisplay.checked=false; els.mathPreview.textContent='Choose a template, symbol, or example.';
    if(els.mathTemplateSelect) els.mathTemplateSelect.value='';
    if(els.mathExampleSelect) els.mathExampleSelect.value='';
  }

  function prepareMathObjectsInEditor() {
    els.richEditor.querySelectorAll('.teacher-math[data-tex]').forEach(span=>{
      const tex=normalizeLegacyMathTex(span.dataset.tex || '');
      const display=span.dataset.display==='block';
      span.setAttribute('contenteditable','false'); span.setAttribute('spellcheck','false');
      span.textContent=display ? `\\[${tex}\\]` : `\\(${tex}\\)`;
    });
  }

  function showEditorModal() {
    resetMathEditorPanel();
    selectEditorVisual(null);
    els.editorModal.hidden=false; document.body.classList.add('modal-open');
    setTimeout(()=>{
      els.richEditor.focus();
      if(window.MathJax?.typesetPromise){
        window.MathJax.typesetPromise([els.richEditor]).catch(()=>{});
      }
    },0);
  }

  function openCustomEditor(type=null, id=null) {
    editingSourceId = null;
    editingCustomId = id;
    const existing = id ? customCards[id] : null;
    editingCustomType = type || existing?.editor_type || (existing?.card_type === 'custom_problem' ? 'problem' : existing?.card_type === 'custom_heading' ? 'heading' : 'text');
    const labels = {
      problem:['Custom problem','Problem number / label','Custom 1'],
      text:['Directions / text','Card label','Teacher directions'],
      heading:['Heading','Card label','Section heading']
    };
    const spec=labels[editingCustomType];
    els.editorEyebrow.textContent='TEACHER-CREATED CARD';
    els.editorTitle.textContent=spec[0];
    els.customLabelWrap.hidden=false;
    els.customLabelCaption.textContent=spec[1];
    els.customLabel.value=existing?.problem_label || existing?.label || spec[2];
    els.sectionHeadingWrap.hidden=true;
    els.editorSourceNote.hidden=true;
    els.placementPanel.hidden=false;
    els.richEditor.innerHTML=existing?.html || (editingCustomType==='problem' ? '<p>Enter the custom problem here.</p>' : editingCustomType==='heading' ? '<h2>Section heading</h2>' : '<p>Enter directions or text here.</p>');
    prepareMathObjectsInEditor();
    els.saveCustomCard.textContent=id?'Save changes':'Add to document';
    populatePlacementControls(id);
    showEditorModal();
  }

  function openSourceEditor(id) {
    const meta=indexMap.get(id), data=cards.get(id);
    if(!meta || !data || isCustomId(id)) return;
    editingCustomId=null;
    editingSourceId=id;
    els.editorEyebrow.textContent='ASSEMBLY OVERRIDE';
    els.editorTitle.textContent=`Edit ${meta.title}`;
    if(isQuestionMeta(meta)){
      els.customLabelWrap.hidden=false;
      els.customLabelCaption.textContent='Problem number / label';
      els.customLabel.value=problemLabel(meta,data,id);
    }else{
      els.customLabelWrap.hidden=true;
      els.customLabel.value='';
    }
    const key=sectionKey(meta);
    els.sectionHeadingWrap.hidden=!key;
    if(key) els.sectionHeadingInput.value=sectionHeading(meta);
    els.editorSourceNote.hidden=false;
    els.placementPanel.hidden=true;
    els.richEditor.innerHTML=effectiveCardHtml(id);
    prepareMathObjectsInEditor();
    els.saveCustomCard.textContent='Save assembly override';
    showEditorModal();
  }

  function closeCustomEditor() {
    els.editorModal.hidden=true; document.body.classList.remove('modal-open');
    editingCustomId=null; editingSourceId=null; savedEditorRange=null;
  }

  function restoreSourceCard(id) {
    const meta=indexMap.get(id);
    delete sourceOverrides[id];
    const key=sectionKey(meta);
    if(key) delete sectionHeadings[key];
    save(); renderAll();
  }

  function saveCustomEditor() {
    const clean=sanitizeTeacherHtml(els.richEditor.innerHTML).trim();
    if(!clean){ alert('Add some content before saving this card.'); return; }

    if(editingSourceId){
      const id=editingSourceId;
      const meta=indexMap.get(id), data=cards.get(id);
      const override={html:clean};
      if(isQuestionMeta(meta)) override.problem_label=els.customLabel.value.trim() || meta.title;
      sourceOverrides[id]=override;
      const key=sectionKey(meta);
      if(key){
        const heading=els.sectionHeadingInput.value.trim();
        if(heading && heading!==meta.section) sectionHeadings[key]=heading;
        else delete sectionHeadings[key];
      }
      save(); closeCustomEditor(); renderAll();
      return;
    }

    const id=editingCustomId || newCustomId();
    const typeMap={problem:'custom_problem',text:'custom_text',heading:'custom_heading'};
    const existing=customCards[id] || {};
    const data={...existing,
      schema_version:1, card_id:id, textbook_id:'teacher', chapter:null, lesson:'Custom', section:'Teacher',
      card_type:typeMap[editingCustomType], editor_type:editingCustomType,
      html:clean
    };
    if(editingCustomType==='problem') data.problem_label=els.customLabel.value.trim();
    else data.label=els.customLabel.value.trim();
    const isNew=!editingCustomId;
    customCards[id]=data;
    indexMap.set(id,customMeta(data)); cards.set(id,data);
    applyCustomPlacement(id,isNew);
    if(isQuestionMeta(indexMap.get(id)) && !cardOptions[id]) cardOptions[id]={workspace:null,figures:{},visuals:[]};
    save(); closeCustomEditor(); renderAll();
  }

  function execEditorCommand(cmd, value=null) {
    els.richEditor.focus();
    document.execCommand(cmd,false,value);
    saveEditorSelection();
  }

  function saveEditorSelection() {
    const sel=window.getSelection();
    if(!sel?.rangeCount) return;
    const range=sel.getRangeAt(0);
    if(els.richEditor.contains(range.commonAncestorContainer)) savedEditorRange=range.cloneRange();
  }

  function restoreEditorSelection() {
    if(!savedEditorRange) { els.richEditor.focus(); return; }
    const sel=window.getSelection(); sel.removeAllRanges(); sel.addRange(savedEditorRange); els.richEditor.focus();
  }

  function insertHtmlAtEditor(html) {
    restoreEditorSelection();
    document.execCommand('insertHTML',false,html);
    saveEditorSelection();
  }

  function openMathPanel() {
    saveEditorSelection();
    els.mathPanel.hidden=false; els.mathInput.focus(); updateMathPreview();
  }

  function normalizeLegacyMathTex(value) {
    // HTML attributes do not treat backslash as an escape character.
    // Older visual-math controls accidentally inserted two backslashes before
    // commands (for example \\frac), which MathJax interprets as a line break
    // followed by plain text. Collapse only doubled slashes immediately before
    // command names; intentional matrix/cases row separators remain intact.
    return String(value || '').replace(/\\\\(?=(?:frac|sqrt|pm|pi|theta|le|ge|ne|approx|infty|sum|int|rightarrow|leftrightarrow|in|cup|cap|left|right|begin|end)\b)/g, '\\');
  }

  function updateMathPreview() {
    clearTimeout(mathPreviewTimer);
    mathPreviewTimer=setTimeout(()=>{
      const tex=normalizeLegacyMathTex(els.mathInput.value.trim());
      els.mathPreview.textContent=tex ? (els.mathDisplay.checked?`\\[${tex}\\]`:`\\(${tex}\\)`) : 'Type a formula.';
      if(tex && window.MathJax?.typesetPromise){
        window.MathJax.typesetClear?.([els.mathPreview]);
        window.MathJax.typesetPromise([els.mathPreview]).catch(()=>{});
      }
    },120);
  }

  function insertMathSnippet(raw, replaceAll=false) {
    if(!raw) return;
    const marker=raw.indexOf('|');
    const snippet=normalizeLegacyMathTex(raw.replace('|',''));
    const input=els.mathInput;
    if(replaceAll){
      input.value=snippet;
      const caret=marker>=0?marker:snippet.length;
      input.focus(); input.setSelectionRange(caret,caret);
    }else{
      const start=input.selectionStart ?? input.value.length;
      const end=input.selectionEnd ?? start;
      input.setRangeText(snippet,start,end,'end');
      const caret=start+(marker>=0?marker:snippet.length);
      input.focus(); input.setSelectionRange(caret,caret);
    }
    updateMathPreview();
  }

  function insertMath() {
    const tex=normalizeLegacyMathTex(els.mathInput.value.trim()); if(!tex) return;
    const display=els.mathDisplay.checked;
    restoreEditorSelection();
    const sel=window.getSelection();
    let range=sel?.rangeCount ? sel.getRangeAt(0) : null;
    if(!range || !els.richEditor.contains(range.commonAncestorContainer)){
      range=document.createRange(); range.selectNodeContents(els.richEditor); range.collapse(false);
    }
    range.deleteContents();

    // Treat a formula as one atomic editor object. The browser caret is moved
    // explicitly to a plain-text spacer after the formula, so teachers can
    // keep typing normally instead of remaining trapped in/selected on MathJax.
    const span=document.createElement('span');
    span.className=display?'teacher-math teacher-math-display':'teacher-math';
    span.dataset.tex=tex; span.dataset.display=display?'block':'inline';
    span.setAttribute('contenteditable','false'); span.setAttribute('spellcheck','false');
    span.textContent=display ? `\\[${tex}\\]` : `\\(${tex}\\)`;
    range.insertNode(span);

    let caretNode;
    if(display){
      const br=document.createElement('br'); span.after(br);
      caretNode=document.createTextNode('\u200B'); br.after(caretNode);
    }else{
      caretNode=document.createTextNode('\u00A0'); span.after(caretNode);
    }
    const after=document.createRange(); after.setStart(caretNode,caretNode.data.length); after.collapse(true);
    sel.removeAllRanges(); sel.addRange(after); savedEditorRange=after.cloneRange();
    els.richEditor.focus();

    if(window.MathJax?.typesetPromise){
      window.MathJax.typesetPromise([span]).catch(()=>{});
    }
    els.mathPanel.hidden=true; els.mathInput.value='';
  }

  async function uploadEditorImage(file) {
    if(!file) return;
    const allowed=['image/png','image/jpeg','image/gif','image/webp'];
    if(!allowed.includes(file.type)){ alert('Use a PNG, JPG, GIF, or WebP image.'); return; }
    if(file.size > 15 * 1024 * 1024){ alert('Image must be 15 MB or smaller.'); return; }
    const previous=els.editorImageBtn.textContent;
    els.editorImageBtn.disabled=true; els.editorImageBtn.textContent='Uploading…';
    try{
      const response=await fetch('/api/uploads/custom-image',{
        method:'POST',
        headers:{'Content-Type':file.type,'X-Filename':encodeURIComponent(file.name)},
        body:file
      });
      const result=await response.json().catch(()=>({}));
      if(!response.ok || !result.url) throw new Error(result.error || `Upload failed (${response.status})`);
      insertHtmlAtEditor(`<img src="${escapeHtml(result.url)}" alt="${escapeHtml(file.name)}">`);
    }catch(err){
      alert(`Could not upload image: ${err.message}`);
    }finally{
      els.editorImageBtn.disabled=false; els.editorImageBtn.textContent=previous;
      els.editorImageFile.value='';
    }
  }

  function updateSaveStatus(message=null, saved=false) {
    if(!els.saveStatus) return;
    if(message){ els.saveStatus.textContent=message; els.saveStatus.classList.toggle('saved',saved); return; }
    if(currentSavedSetId){
      els.saveStatus.textContent=currentSavedSetName ? `Saved set: ${currentSavedSetName}` : 'Saved set loaded';
      els.saveStatus.classList.add('saved');
    }else{
      els.saveStatus.textContent='Not saved to library'; els.saveStatus.classList.remove('saved');
    }
  }

  function snapshotRecipe() {
    return {
      schema:DOCUMENT_SCHEMA,
      core_version:CORE_VERSION,
      content_package:'cc3e3',
      title:settings.title,
      order:[...order],
      breaks:[...breaks],
      settings:JSON.parse(JSON.stringify(settings)),
      card_options:JSON.parse(JSON.stringify(cardOptions)),
      custom_cards:JSON.parse(JSON.stringify(customCards)),
      source_overrides:JSON.parse(JSON.stringify(sourceOverrides)),
      section_headings:JSON.parse(JSON.stringify(sectionHeadings))
    };
  }

  function documentRecipe() {
    save();
    return snapshotRecipe();
  }

  function applyRecipe(recipe) {
    if(!recipe || recipe.schema!==DOCUMENT_SCHEMA) throw new Error('This Library item uses an unsupported document format.');
    order=Array.isArray(recipe.order)?[...recipe.order]:[];
    breaks=new Set(Array.isArray(recipe.breaks)?recipe.breaks:[]);
    settings=Object.assign({spacing:'normal',margin:'normal',figure:'normal',workspace:'medium',title:'Untitled',showTitle:true},recipe.settings||{});
    cardOptions=recipe.card_options && typeof recipe.card_options==='object' ? JSON.parse(JSON.stringify(recipe.card_options)) : {};
    customCards=recipe.custom_cards && typeof recipe.custom_cards==='object' ? JSON.parse(JSON.stringify(recipe.custom_cards)) : {};
    sourceOverrides=recipe.source_overrides && typeof recipe.source_overrides==='object' ? JSON.parse(JSON.stringify(recipe.source_overrides)) : {};
    sectionHeadings=recipe.section_headings && typeof recipe.section_headings==='object' ? JSON.parse(JSON.stringify(recipe.section_headings)) : {};
  }

  async function loadSavedSetIfRequested() {
    if(!currentSavedSetId) return;
    const r=await fetch(`/api/saved-sets/${encodeURIComponent(currentSavedSetId)}`,{cache:'no-store'});
    const data=await r.json().catch(()=>({}));
    if(!r.ok || !data.recipe) throw new Error(data.error || 'Could not open this Library item.');
    currentSavedSetName=data.name || '';
    const savedBundle=normalizedAssessmentBundle(data.assessment_bundle);
    if(savedBundle){
      assessmentBundle=savedBundle;
      assessmentActiveIndex=savedBundle.active_index;
      applyRecipe(savedBundle.recipes[assessmentActiveIndex]);
      try{localStorage.setItem(ASSESSMENT_SESSION_KEY,JSON.stringify(savedBundle));}catch{}
    }else{
      applyRecipe(data.recipe);
    }
  }

  function assessmentWorkspaceFor(mode){return mode==='selected_response'?0.15:mode==='short_response'?0.65:mode==='table_response'?0.8:mode==='graph_response'?1.35:mode==='equation_response'?1.0:1.1;}

  function buildAssessmentRecipeFromOrigin(versionIndex){
    const origin=assessmentBundle?.origin||{};
    const families=Array.isArray(origin.families)?origin.families:[];
    const engine=window.CC3AssessmentVariants;
    if(!families.length || !engine?.build) throw new Error('The assessment does not contain same-family source data. Rebuild it from Assessment Builder.');
    const label=assessmentVersionLabel(versionIndex), custom={},order=[],breaks=[],options={};
    families.forEach((f,i)=>{
      const used=assessmentFamilyUsedSignatures(f.family_id);
      const instance=engine.buildUnique?engine.buildUnique(f,versionIndex,i,used):engine.build(f,versionIndex,i);
      const sig=instance.signature||(engine.signature?engine.signature(instance):`${instance.student_html||''}\n${instance.answer||''}`);
      const id=`custom-assessment-v${label.toLowerCase()}-${String(f.teacher_question_id||'q').toLowerCase()}-${String(i+1).padStart(2,'0')}`;
      const keyId=origin.include_key?`custom-assessment-v${label.toLowerCase()}-key-${String(f.teacher_question_id||'q').toLowerCase()}-${String(i+1).padStart(2,'0')}`:null;
      order.push(id);
      custom[id]={schema_version:1,card_id:id,textbook_id:'teacher',chapter:f.chapter,lesson:f.section||'Assessment',section:'Assessment',card_type:'custom_problem',editor_type:'problem',problem_label:`${i+1}.`,html:instance.student_html||'',assessment_family_id:f.family_id,assessment_family_snapshot:JSON.parse(JSON.stringify(f)),teacher_question_id:f.teacher_question_id,question_structure_id:f.question_structure_id,response_mode:f.response_mode,representation_mode:f.representation_mode,assessment_version:label,assessment_variant_index:instance.variant_index??versionIndex,assessment_variant_signature:sig,assessment_variant_answer:instance.answer||'',assessment_variant_solution:instance.solution||'',assessment_key_card_id:keyId};
      options[id]={workspace:assessmentWorkspaceFor(f.response_mode),figures:{},visuals:[]};
    });
    if(origin.include_key && families.length){
      const heading=`custom-assessment-v${label.toLowerCase()}-answer-key-heading`;
      order.push(heading);breaks.push(heading);custom[heading]={schema_version:1,card_id:heading,textbook_id:'teacher',chapter:Number(origin.chapter||1),lesson:'Answer Key',section:'Assessment',card_type:'custom_heading',editor_type:'heading',label:'Answer Key',html:'<h2>Answer Key</h2>'};
      families.forEach((f,i)=>{
        const qid=`custom-assessment-v${label.toLowerCase()}-${String(f.teacher_question_id||'q').toLowerCase()}-${String(i+1).padStart(2,'0')}`;
        const question=custom[qid], id=question.assessment_key_card_id;
        order.push(id); custom[id]={schema_version:1,card_id:id,textbook_id:'teacher',chapter:f.chapter,lesson:'Answer Key',section:'Assessment',card_type:'custom_text',editor_type:'text',label:`${i+1}. ${f.teacher_question_id||''}`,html:assessmentAnswerHtml(i+1,question.assessment_variant_answer,question.assessment_variant_solution),assessment_question_card_id:qid,assessment_family_id:f.family_id,assessment_variant_index:question.assessment_variant_index};
      });
    }
    const baseTitle=String(origin.base_title||'Assessment').trim()||'Assessment';
    const title=`${baseTitle} - Version ${label}`;
    return {schema:DOCUMENT_SCHEMA,core_version:CORE_VERSION,content_package:'cc3e3',title,order,breaks,settings:{spacing:'normal',margin:'normal',figure:'normal',workspace:'medium',title,showTitle:true},card_options:options,custom_cards:custom,source_overrides:{},section_headings:{}};
  }

  function normalizedAssessmentBundle(raw) {
    if(!raw || raw.schema!==ASSESSMENT_BUNDLE_SCHEMA || !Array.isArray(raw.recipes) || !raw.recipes.length) return null;
    const bundle=JSON.parse(JSON.stringify(raw));
    bundle.version_count=Math.max(1,Math.min(Number(bundle.version_count)||1,bundle.recipes.length));
    bundle.active_index=Math.max(0,Math.min(Number(bundle.active_index)||0,bundle.version_count-1));
    return bundle;
  }

  function persistAssessmentActiveRecipe() {
    if(!assessmentBundle || printingAllAssessmentVersions) return;
    settings.title=els.title?.value ?? settings.title;
    settings.showTitle=els.showTitle?.checked ?? settings.showTitle;
    assessmentBundle.recipes[assessmentActiveIndex]=snapshotRecipe();
    assessmentBundle.active_index=assessmentActiveIndex;
    try{ localStorage.setItem(ASSESSMENT_SESSION_KEY,JSON.stringify(assessmentBundle)); }catch{}
  }

  function applyAssessmentHandoffIfRequested() {
    if(currentSavedSetId || handoffSource !== 'assessment') return false;
    let payload=null;
    try{ payload=JSON.parse(localStorage.getItem(ASSESSMENT_HANDOFF_KEY) || 'null'); }catch{}
    if(payload){
      localStorage.removeItem(ASSESSMENT_HANDOFF_KEY);
      const bundle=normalizedAssessmentBundle(payload);
      if(bundle){
        assessmentBundle=bundle; assessmentActiveIndex=bundle.active_index;
        applyRecipe(bundle.recipes[assessmentActiveIndex]);
        try{localStorage.setItem(ASSESSMENT_SESSION_KEY,JSON.stringify(bundle));}catch{}
        return true;
      }
      if(payload.schema===DOCUMENT_SCHEMA){ applyRecipe(payload); return true; }
    }
    try{ payload=JSON.parse(localStorage.getItem(ASSESSMENT_SESSION_KEY) || 'null'); }catch{}
    const session=normalizedAssessmentBundle(payload);
    if(!session) return false;
    assessmentBundle=session; assessmentActiveIndex=session.active_index;
    applyRecipe(session.recipes[assessmentActiveIndex]);
    return true;
  }

  function assessmentVersionLabel(index){ return String.fromCharCode(65+index); }

  function recipeHasSummativeKinds(recipe) {
    return Object.values(recipe?.custom_cards||{}).some(card=>card?.assessment_question_kind==='mc' || card?.assessment_question_kind==='frq');
  }

  function isSplitSummativeAssessment() {
    return !!assessmentBundle && assessmentBundle.recipes.some(recipeHasSummativeKinds);
  }

  function packetKindCount(recipe,kind) {
    return Object.values(recipe?.custom_cards||{}).filter(card=>card?.assessment_question_kind===kind).length;
  }

  function renderPacketVersionButtons(container,kind,count) {
    if(!container) return;
    container.innerHTML=Array.from({length:count},(_,i)=>`<button type="button" class="packet-version-btn" data-packet-kind="${kind}" data-packet-version="${i}" aria-label="Print ${kind==='mc'?'MC questions':'Bubble and FRQ packet'} Version ${assessmentVersionLabel(i)}">${assessmentVersionLabel(i)}</button>`).join('');
  }

  function renderAssessmentVersionControls() {
    if(!els.assessmentVersionPanel) return;
    const on=!!assessmentBundle;
    els.assessmentVersionPanel.hidden=!on;
    const split=on && isSplitSummativeAssessment();
    if(els.printAllVersions) els.printAllVersions.hidden=!on || assessmentBundle.version_count<2 || split;
    if(els.demoPrint) els.demoPrint.hidden=split;
    if(els.summativePacketPanel) els.summativePacketPanel.hidden=!split;
    if(!on) return;
    const count=assessmentBundle.version_count;
    els.assessmentVersionSummary.textContent=`Version ${assessmentVersionLabel(assessmentActiveIndex)} of ${count}`;
    els.assessmentVersionTabs.innerHTML=Array.from({length:count},(_,i)=>`<button type="button" class="assessment-version-tab ${i===assessmentActiveIndex?'active':''}" data-assessment-version="${i}" aria-label="Open Version ${assessmentVersionLabel(i)}">${assessmentVersionLabel(i)}</button>`).join('');
    els.assessmentVersionTabs.querySelectorAll('[data-assessment-version]').forEach(btn=>btn.addEventListener('click',()=>switchAssessmentVersion(Number(btn.dataset.assessmentVersion))));
    const max=Math.max(count,Number(assessmentBundle.max_versions)||8);
    els.newAssessmentVersion.disabled=count>=max;
    els.newAssessmentVersion.title=els.newAssessmentVersion.disabled?'Maximum assessment versions reached':'Add a new version from the same question families';
    if(split){
      const recipe=assessmentBundle.recipes[assessmentActiveIndex];
      const mcCount=packetKindCount(recipe,'mc'), frqCount=packetKindCount(recipe,'frq');
      if(els.frqPacketRow) els.frqPacketRow.hidden=!(mcCount||frqCount);
      if(els.mcPacketRow) els.mcPacketRow.hidden=!mcCount;
      if(els.frqPacketLabel) els.frqPacketLabel.textContent=mcCount&&frqCount?'Bubble + FRQ':mcCount?'Bubble sheet':'FRQ packet';
      renderPacketVersionButtons(els.frqPacketVersions,'frq',count);
      renderPacketVersionButtons(els.mcPacketVersions,'mc',count);
      if(els.frqPacketAll) els.frqPacketAll.hidden=count<2;
      if(els.mcPacketAll) els.mcPacketAll.hidden=count<2;
    }
  }

  function activateAssessmentRecipe(index,{persist=true,render=true}={}) {
    if(!assessmentBundle || index<0 || index>=assessmentBundle.version_count) return false;
    assessmentActiveIndex=index; assessmentBundle.active_index=index;
    applyRecipe(assessmentBundle.recipes[index]);
    installCustomCards(); syncControls();
    if(persist) save();
    renderAssessmentVersionControls();
    if(render) renderAll();
    return true;
  }

  function switchAssessmentVersion(index) {
    if(!assessmentBundle || index===assessmentActiveIndex || index<0 || index>=assessmentBundle.version_count) return;
    save();
    activateAssessmentRecipe(index,{persist:true,render:true});
  }

  function addAssessmentVersion() {
    if(!assessmentBundle) return;
    save();
    const max=Math.max(1,Number(assessmentBundle.max_versions)||8);
    if(assessmentBundle.version_count>=max){ alert('Maximum assessment versions reached.'); return; }
    const nextIndex=assessmentBundle.version_count;
    try{
      assessmentBundle.recipes.push(buildAssessmentRecipeFromOrigin(nextIndex));
      assessmentBundle.version_count=assessmentBundle.recipes.length;
      activateAssessmentRecipe(nextIndex,{persist:true,render:true});
    }catch(err){ alert(err.message||'Could not create a new version.'); }
  }

  function waitForPageImages(timeoutMs=1800) {
    const imgs=[...els.pages.querySelectorAll('img')].filter(img=>!img.complete);
    if(!imgs.length) return Promise.resolve();
    return Promise.all(imgs.map(img=>new Promise(resolve=>{
      let done=false; const finish=()=>{if(done)return;done=true;resolve();};
      img.addEventListener('load',finish,{once:true}); img.addEventListener('error',finish,{once:true}); setTimeout(finish,timeoutMs);
    })));
  }

  async function renderPagesNow() {
    clearTimeout(paginateTimer); paginate(); await waitForPageImages(); paginate(); await typesetPages();
  }

  function summativeQuestionIds(kind) {
    return order.filter(id=>cards.get(id)?.assessment_question_kind===kind);
  }

  function packetQuestionNumber(id,fallback=1) {
    const raw=String(cards.get(id)?.problem_label||'').trim();
    const match=raw.match(/\d+/);
    return match ? Number(match[0]) : fallback;
  }

  function bubbleSheetHtml(mcIds) {
    const items=mcIds.map((id,idx)=>{
      const n=packetQuestionNumber(id,idx+1);
      const bubbles=['A','B','C','D'].map(letter=>`<span class="mc-bubble-choice">${letter}</span>`).join('');
      return `<div class="mc-bubble-item"><span class="mc-bubble-number">${n}.</span>${bubbles}</div>`;
    }).join('');
    return `<div class="mc-bubble-sheet"><div class="mc-bubble-title">Multiple Choice Answer Sheet</div><div class="mc-bubble-grid">${items}</div></div>`;
  }

  function installPacketTextCard(id,html,label='') {
    customCards[id]={schema_version:1,card_id:id,textbook_id:'teacher',chapter:Number(assessmentBundle?.origin?.chapter||1),lesson:'Summative',section:'Assessment',card_type:'custom_text',editor_type:'text',label,html};
    cardOptions[id]={workspace:0,figures:{},visuals:[]};
  }

  function prepareSummativePacket(kind) {
    const mcIds=summativeQuestionIds('mc');
    const frqIds=summativeQuestionIds('frq');
    const tempIds=[];
    breaks=new Set();
    settings.showTitle=true;
    if(kind==='mc'){
      if(!mcIds.length){ order=[]; return {mcIds,frqIds,tempIds}; }
      const directionsId='custom-summative-packet-mc-directions';
      installPacketTextCard(directionsId,'<div class="packet-section-intro"><strong>Multiple Choice</strong><span>Choose the best answer. Record answers on the separate answer sheet.</span></div>','Multiple Choice');
      tempIds.push(directionsId);
      mcIds.forEach(id=>{ optionsFor(id).workspace=0; });
      order=[directionsId,...mcIds];
    }else{
      const bubbleId='custom-summative-packet-bubble';
      const introId='custom-summative-packet-frq-directions';
      if(mcIds.length){
        installPacketTextCard(bubbleId,bubbleSheetHtml(mcIds),'Multiple Choice Answer Sheet');
        tempIds.push(bubbleId);
      }
      if(frqIds.length){
        installPacketTextCard(introId,'<div class="packet-section-intro packet-frq-intro"><strong>Free Response</strong><span>Show your work and reasoning.</span></div>','Free Response');
        tempIds.push(introId);
      }
      order=[...(mcIds.length?[bubbleId]:[]),...(frqIds.length?[introId]:[]),...frqIds];
    }
    installCustomCards();
    return {mcIds,frqIds,tempIds};
  }

  function renderedPacketPageCount(){ return els.pages.querySelectorAll('.paper').length; }

  async function fitFrqPacketToTwoPages(frqIds) {
    await renderPagesNow();
    let count=renderedPacketPageCount();
    if(count<=2 || !frqIds.length) return count;
    settings.spacing='compact';
    await renderPagesNow(); count=renderedPacketPageCount();
    if(count<=2) return count;
    settings.margin='narrow';
    await renderPagesNow(); count=renderedPacketPageCount();
    if(count<=2) return count;

    for(let round=0;round<8 && count>2;round++){
      frqIds.forEach(id=>{
        const opt=optionsFor(id);
        const current=effectiveWorkspaceIn(id);
        opt.workspace=Math.max(0.45,Math.round((current-0.15)*100)/100);
        const figureCount=cardImageCount(id);
        for(let i=0;i<figureCount;i++){
          const currentPx=effectiveFigurePx(id,i);
          opt.figures[i]=Math.max(165,Math.round(currentPx*0.9));
        }
      });
      await renderPagesNow();
      count=renderedPacketPageCount();
    }
    return count;
  }

  async function buildSummativePacketChunk(versionIndex,kind) {
    assessmentActiveIndex=versionIndex;
    assessmentBundle.active_index=versionIndex;
    applyRecipe(assessmentBundle.recipes[versionIndex]);
    installCustomCards();
    const packet=prepareSummativePacket(kind);
    if(!order.length) return {html:'',pages:0};
    let pageCount;
    if(kind==='frq') pageCount=await fitFrqPacketToTwoPages(packet.frqIds);
    else { await renderPagesNow(); pageCount=renderedPacketPageCount(); }
    const label=assessmentVersionLabel(versionIndex);
    return {html:`<div class="assessment-version-pages summative-${kind}-packet" data-assessment-version="${label}">${els.pages.innerHTML}</div>`,pages:pageCount};
  }

  async function printSummativePacket(kind,versionIndexes) {
    if(!assessmentBundle || printingAllAssessmentVersions || !isSplitSummativeAssessment()) return;
    save();
    const originalIndex=assessmentActiveIndex;
    const chunks=[];
    const pageCounts=[];
    printingAllAssessmentVersions=true;
    try{
      for(const index of versionIndexes){
        const built=await buildSummativePacketChunk(index,kind);
        if(built.html){ chunks.push(built.html); pageCounts.push({index,pages:built.pages}); }
      }
      if(!chunks.length){ alert(kind==='mc'?'This assessment does not contain MC questions.':'This assessment does not contain a bubble sheet or FRQ questions.'); return; }
      els.assessmentPrintAll.innerHTML=chunks.join('');
      assessmentActiveIndex=originalIndex; assessmentBundle.active_index=originalIndex;
      applyRecipe(assessmentBundle.recipes[originalIndex]); installCustomCards(); syncControls(); renderList(); await renderPagesNow(); renderAssessmentVersionControls();
      if(kind==='frq'){
        const over=pageCounts.filter(item=>item.pages>2);
        if(over.length){
          const labels=over.map(item=>`Version ${assessmentVersionLabel(item.index)} (${item.pages} pages)`).join(', ');
          alert(`The Bubble + FRQ packet was tightened automatically, but ${labels} still exceeds the two-page target. Reduce figure/workspace sizes if you want to force two pages.`);
        }
      }
      document.body.classList.add('print-summative-packet');
      els.assessmentPrintAll.setAttribute('aria-hidden','false');
      window.print();
    } finally {
      document.body.classList.remove('print-summative-packet');
      els.assessmentPrintAll.setAttribute('aria-hidden','true');
      els.assessmentPrintAll.innerHTML='';
      printingAllAssessmentVersions=false;
      assessmentActiveIndex=originalIndex; assessmentBundle.active_index=originalIndex;
      applyRecipe(assessmentBundle.recipes[originalIndex]); installCustomCards(); syncControls(); renderAssessmentVersionControls(); renderAll();
      try{localStorage.setItem(ASSESSMENT_SESSION_KEY,JSON.stringify(assessmentBundle));}catch{}
    }
  }

  function allAssessmentVersionIndexes(){ return Array.from({length:assessmentBundle?.version_count||0},(_,i)=>i); }

  async function printAllAssessmentVersions() {
    if(!assessmentBundle || assessmentBundle.version_count<2 || printingAllAssessmentVersions) return;
    save();
    const originalIndex=assessmentActiveIndex;
    const chunks=[];
    printingAllAssessmentVersions=true;
    try{
      for(let i=0;i<assessmentBundle.version_count;i++){
        assessmentActiveIndex=i; applyRecipe(assessmentBundle.recipes[i]); installCustomCards(); syncControls(); renderList();
        await renderPagesNow();
        chunks.push(`<div class="assessment-version-pages" data-assessment-version="${assessmentVersionLabel(i)}">${els.pages.innerHTML}</div>`);
      }
      els.assessmentPrintAll.innerHTML=chunks.join('');
      assessmentActiveIndex=originalIndex; assessmentBundle.active_index=originalIndex; applyRecipe(assessmentBundle.recipes[originalIndex]); installCustomCards(); syncControls(); renderList(); await renderPagesNow(); renderAssessmentVersionControls();
      document.body.classList.add('print-all-versions'); els.assessmentPrintAll.setAttribute('aria-hidden','false');
      window.print();
    } finally {
      document.body.classList.remove('print-all-versions'); els.assessmentPrintAll.setAttribute('aria-hidden','true'); els.assessmentPrintAll.innerHTML='';
      printingAllAssessmentVersions=false;
      assessmentActiveIndex=originalIndex; assessmentBundle.active_index=originalIndex; applyRecipe(assessmentBundle.recipes[originalIndex]); installCustomCards(); syncControls(); renderAssessmentVersionControls(); renderAll();
      try{localStorage.setItem(ASSESSMENT_SESSION_KEY,JSON.stringify(assessmentBundle));}catch{}
    }
  }

  function openSaveDialog(forceSaveAs=false) {
    saveAsMode=forceSaveAs || !currentSavedSetId;
    els.saveSetName.value=saveAsMode ? (currentSavedSetName ? `${currentSavedSetName} Copy` : settings.title || 'Untitled document') : (currentSavedSetName || settings.title || 'Untitled document');
    document.getElementById('saveModalTitle').textContent=saveAsMode?'Save document as':'Save document';
    els.saveModal.hidden=false; document.body.classList.add('modal-open');
    setTimeout(()=>{els.saveSetName.focus();els.saveSetName.select();},0);
  }

  function closeSaveDialog(){ els.saveModal.hidden=true; document.body.classList.remove('modal-open'); }

  async function saveSetToLibrary() {
    const name=els.saveSetName.value.trim();
    if(!name){ alert('Give this Library item a name.'); return; }
    els.confirmSaveSet.disabled=true; els.confirmSaveSet.textContent='Saving…';
    try{
      const recipe=documentRecipe();
      if(assessmentBundle) persistAssessmentActiveRecipe();
      const payload={name,recipe};
      if(assessmentBundle) payload.assessment_bundle=JSON.parse(JSON.stringify(assessmentBundle));
      if(!saveAsMode && currentSavedSetId) payload.id=currentSavedSetId;
      const r=await fetch('/api/saved-sets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const data=await r.json().catch(()=>({}));
      if(!r.ok || !data.id) throw new Error(data.error || `Save failed (${r.status})`);
      currentSavedSetId=data.id; currentSavedSetName=data.name || name;
      const url=new URL(location.href); url.searchParams.set('set',currentSavedSetId); history.replaceState({},'',url);
      closeSaveDialog(); updateSaveStatus(`Saved: ${currentSavedSetName}`,true);
    }catch(err){ alert(`Could not save this document: ${err.message}`); }
    finally{ els.confirmSaveSet.disabled=false; els.confirmSaveSet.textContent='Save to library'; }
  }

  function visualField(label,html){ return `<div class="visual-field"><label>${label}</label>${html}</div>`; }

  function visualToggle(label,key,checked,help=''){ return `<label class="visual-toggle"><input data-vk="${key}" type="checkbox"${checked?' checked':''}><span><b>${label}</b>${help?`<small>${help}</small>`:''}</span></label>`; }

  function visualNumeric(label,key,value,steps=[1,5]){
    const options=steps.map((v,i)=>`<option value="${v}"${i===0?' selected':''}>${v}</option>`).join('');
    return `<div class="visual-number-control">
      <div class="visual-number-label">${label}</div>
      <div class="visual-number-main">
        <button class="visual-nudge" type="button" data-vdelta="-1" data-vtarget="${key}" aria-label="Decrease ${label}">−</button>
        <input data-vk="${key}" type="number" value="${escapeHtml(value)}" aria-label="${label} value">
        <button class="visual-nudge" type="button" data-vdelta="1" data-vtarget="${key}" aria-label="Increase ${label}">+</button>
      </div>
      <label class="visual-step-row"><span>Step</span><select class="visual-step" data-vstep-for="${key}" aria-label="${label} step size">${options}</select></label>
    </div>`;
  }

  function visualDetails(title,body,open=true){ return `<details class="visual-fine-tune"${open?' open':''}><summary>${title}</summary><div class="visual-fine-tune-body">${body}</div></details>`; }

  function graphWindowControls(params){
    const val=(k,d)=>params[k] ?? d;
    return `<div class="visual-control-section"><div class="visual-control-section-title">Window</div><div class="visual-numeric-list">${visualNumeric('x min','xmin',val('xmin',-10),[1,5,10])}${visualNumeric('x max','xmax',val('xmax',10),[1,5,10])}${visualNumeric('y min','ymin',val('ymin',-10),[1,5,10])}${visualNumeric('y max','ymax',val('ymax',10),[1,5,10])}</div></div>`;
  }

  function graphFineControls(params){
    const val=(k,d)=>params[k] ?? d;
    return visualDetails('Grid & axes fine tuning',`<div class="visual-numeric-list">${visualNumeric('x minor grid step','x_minor',val('x_minor',1),[0.25,0.5,1,2,5])}${visualNumeric('y minor grid step','y_minor',val('y_minor',1),[0.25,0.5,1,2,5])}${visualNumeric('major line every','major_every',val('major_every',5),[1,2,5])}${visualNumeric('x number label step','x_label_step',val('x_label_step',5),[1,2,5,10])}${visualNumeric('y number label step','y_label_step',val('y_label_step',5),[1,2,5,10])}</div>${visualField('Axis end arrows','<select data-vk="axis_arrows"><option value="both">Both ends</option><option value="positive">Positive ends only</option><option value="none">None</option></select>')}<div class="visual-toggle-stack">${visualToggle('Minor grid','show_minor',val('show_minor',true)!==false,'Light construction grid')}${visualToggle('Major grid','show_major',val('show_major',true)!==false,'Emphasize every major interval')}${visualToggle('Number labels','show_numbers',val('show_numbers',true)!==false,'Keep labels next to the axes')}</div><div class="visual-two-col">${visualField('x-axis label',`<input data-vk="xlabel" value="${escapeHtml(val('xlabel',''))}" placeholder="optional">`)}${visualField('y-axis label',`<input data-vk="ylabel" value="${escapeHtml(val('ylabel',''))}" placeholder="optional">`)}</div>`);
  }

  function wireVisualNudges(){
    els.visualControls.querySelectorAll('.visual-nudge').forEach(btn=>btn.addEventListener('click',()=>{
      const key=btn.dataset.vtarget,input=els.visualControls.querySelector(`[data-vk="${key}"]`),step=Number(els.visualControls.querySelector(`[data-vstep-for="${key}"]`)?.value||1);
      if(!input) return;
      const min=input.min===''?-Infinity:Number(input.min),max=input.max===''?Infinity:Number(input.max);
      const next=Math.max(min,Math.min(max,Number(input.value||0)+Number(btn.dataset.vdelta||0)*step));
      input.value=Number.isInteger(next)?String(next):String(Number(next.toFixed(4)));
      input.dispatchEvent(new Event('input',{bubbles:true}));
    }));
  }

  function normalizeLegacyVisual(type,params={}){
    if(type!=='parent_function') return {type,params};
    const parents={linear:'y = x',quadratic:'y = x^2',absolute:'y = abs(x)',cubic:'y = x^3',sqrt:'y = sqrt(x)',reciprocal:'y = 1/x'};
    return {type:'function_graph',params:{...params,expressions:params.expressions || parents[params.function] || 'y = x',x_minor:params.x_minor??1,y_minor:params.y_minor??1,major_every:params.major_every??5,x_label_step:params.x_label_step??5,y_label_step:params.y_label_step??5,show_minor:params.show_minor??true,show_major:params.show_major??true,show_numbers:params.show_numbers??true,axis_arrows:params.axis_arrows??'both'}};
  }

  function renderVisualControls(params={}) {
    const t=els.visualType.value;
    const val=(k,d)=>params[k] ?? d;
    if(t==='blank_graph') els.visualControls.innerHTML=graphWindowControls(params)+graphFineControls(params);
    else if(t==='function_graph') els.visualControls.innerHTML=`${visualField('Expressions — one per line',`<textarea class="visual-expression-input" data-vk="expressions" rows="4" placeholder="y = x^2\ny = 2*x + 3">${escapeHtml(Array.isArray(val('expressions','y = x'))?val('expressions','y = x').join('\n'):val('expressions','y = x'))}</textarea>`)}<div class="visual-help">Calculator-style graphing: use x, +, −, *, /, ^, abs(), sqrt(), sin(), cos(), tan(), exp(), log(), or ln(). Simple vertical lines such as x = 3 also work.</div>${graphWindowControls(params)}${graphFineControls(params)}`;
    else if(t==='number_line') els.visualControls.innerHTML=`<div class="visual-control-section"><div class="visual-control-section-title">Range</div><div class="visual-numeric-list">${visualNumeric('Minimum','xmin',val('xmin',-10),[1,5,10])}${visualNumeric('Maximum','xmax',val('xmax',10),[1,5,10])}</div></div>${visualDetails('Ticks & labels',`<div class="visual-numeric-list">${visualNumeric('Tick spacing','tick_step',val('tick_step',1),[0.5,1,2,5,10])}${visualNumeric('Number label spacing','label_step',val('label_step',1),[1,2,5,10])}</div>${visualField('Arrow ends','<select data-vk="arrows"><option value="both">Both ends</option><option value="positive">Positive end only</option><option value="none">No arrows</option></select>')}<div class="visual-toggle-stack">${visualToggle('Tick marks','show_ticks',val('show_ticks',true)!==false)}${visualToggle('Number labels','show_labels',val('show_labels',true)!==false)}</div>${visualField('Axis label',`<input data-vk="axis_label" value="${escapeHtml(val('axis_label',''))}" placeholder="optional">`)}`)}`;
    else if(t==='graph_paper') els.visualControls.innerHTML=`<div class="visual-numeric-list">${visualNumeric('Columns','cols',val('cols',20),[1,5])}${visualNumeric('Rows','rows',val('rows',20),[1,5])}</div>${visualDetails('Grid fine tuning',`${visualNumeric('Major line every','major_every',val('major_every',5),[1,2,5])}<div class="visual-toggle-stack">${visualToggle('Minor grid','show_minor',val('show_minor',true)!==false)}${visualToggle('Major grid','show_major',val('show_major',true)!==false)}${visualToggle('Outer border','show_border',val('show_border',true)!==false)}</div>`)}`;
    else if(t==='diamond') els.visualControls.innerHTML=`${visualField('Random pattern','<select data-vk="pattern"><option value="product_sum">Product + sum given</option><option value="sides">Side numbers given</option><option value="mixed">Mixed givens</option><option value="blank">Blank diamond</option></select>')}<div class="visual-two-col">${visualField('Top / product',`<input data-vk="top" value="${escapeHtml(val('top',''))}" placeholder="blank">`)}${visualField('Bottom / sum',`<input data-vk="bottom" value="${escapeHtml(val('bottom',''))}" placeholder="blank">`)}${visualField('Left',`<input data-vk="left" value="${escapeHtml(val('left',''))}" placeholder="blank">`)}${visualField('Right',`<input data-vk="right" value="${escapeHtml(val('right',''))}" placeholder="blank">`)}</div>${visualDetails('Diamond fine tuning',`<div class="visual-numeric-list">${visualNumeric('Random minimum','random_min',val('random_min',-12),[1,5])}${visualNumeric('Random maximum','random_max',val('random_max',12),[1,5])}${visualNumeric('Value font size','font_size',val('font_size',28),[1,2,4])}</div><div class="visual-toggle-stack">${visualToggle('Allow zero when randomizing','allow_zero',val('allow_zero',false)===true)}${visualToggle('Divider lines','show_diagonals',val('show_diagonals',true)!==false)}</div>`)}`;
    else if(t==='input_output_table') els.visualControls.innerHTML=`${visualField('Orientation','<select data-vk="orientation"><option value="vertical">Vertical</option><option value="horizontal">Horizontal</option></select>')}<div class="visual-numeric-list">${visualNumeric('Rows / pairs','count',val('count',6),[1,2])}</div><div class="visual-two-col">${visualField('Input label',`<input data-vk="input_label" value="${escapeHtml(val('input_label','Input'))}">`)}${visualField('Output label',`<input data-vk="output_label" value="${escapeHtml(val('output_label','Output'))}">`)}</div>${visualDetails('Table fine tuning',`${visualNumeric('Line weight','line_weight',val('line_weight',1.2),[0.25,0.5,1])}<div class="visual-toggle-stack">${visualToggle('Header labels','show_header',val('show_header',true)!==false)}</div>`)}`;
    else if(t==='area_model') els.visualControls.innerHTML=`${visualField('Row labels',`<input data-vk="rows" value="${escapeHtml((val('rows',['x','1'])||[]).join(', '))}">`)}${visualField('Column labels',`<input data-vk="cols" value="${escapeHtml((val('cols',['x','1'])||[]).join(', '))}">`)}${visualDetails('Area model fine tuning',`${visualNumeric('Label font size','label_size',val('label_size',24),[1,2,4])}<div class="visual-toggle-stack">${visualToggle('Show outside labels','show_labels',val('show_labels',true)!==false)}</div>`)}`;
    else if(t==='fraction_bar') els.visualControls.innerHTML=`<div class="visual-numeric-list">${visualNumeric('Parts','parts',val('parts',4),[1,2])}${visualNumeric('Shaded','shaded',val('shaded',0),[1,2])}</div>${visualDetails('Fraction bar fine tuning',`${visualNumeric('Outline weight','outline_weight',val('outline_weight',1.5),[0.25,0.5,1])}<div class="visual-toggle-stack">${visualToggle('Unit-fraction labels','show_labels',val('show_labels',false)===true)}</div>`)}`;
    else if(t==='hundred_grid') els.visualControls.innerHTML=`${visualNumeric('Shaded cells','shaded',val('shaded',0),[1,5,10])}${visualDetails('Hundred grid fine tuning',`${visualField('Shading order','<select data-vk="shading_order"><option value="row">Across rows</option><option value="column">Down columns</option></select>')}${visualNumeric('Major line every','major_every',val('major_every',5),[1,5])}<div class="visual-toggle-stack">${visualToggle('Major divider lines','show_major',val('show_major',true)!==false)}</div>`)}`;
    else if(t==='unit_circle') els.visualControls.innerHTML=`${visualField('Angle labels','<select data-vk="mode"><option value="blank">Blank</option><option value="angles">Degrees</option><option value="degrees_radians">Radians</option></select>')}${visualDetails('Unit circle fine tuning',`<div class="visual-toggle-stack">${visualToggle('Axes','show_axes',val('show_axes',true)!==false)}${visualToggle('Radial guide lines','show_rays',val('show_rays',false)===true)}${visualToggle('Angle points','show_points',val('show_points',true)!==false)}${visualToggle('x / y labels','show_axis_labels',val('show_axis_labels',false)===true)}</div>`)}`;
    ['orientation','mode','pattern','axis_arrows','arrows','shading_order'].forEach(k=>{const select=els.visualControls.querySelector(`[data-vk="${k}"]`);if(select&&params[k]!=null)select.value=params[k]});
    els.visualControls.querySelectorAll('input[type="checkbox"][data-vk]').forEach(el=>{if(params[el.dataset.vk]!=null)el.checked=!!params[el.dataset.vk]});
    els.visualControls.querySelectorAll('[data-vk]').forEach(el=>{
      const dirty=()=>{pendingVisual=null;els.insertVisualBtn.disabled=true;els.visualStatus.textContent='Settings changed — generate a new preview.'};
      el.addEventListener('input',dirty);el.addEventListener('change',dirty);
    });
    wireVisualNudges();
  }

  function readVisualParams(){
    const out={};
    const numericKeys=new Set(['xmin','xmax','ymin','ymax','x_minor','y_minor','x_label_step','y_label_step','tick_step','label_step','cols','rows','major_every','count','parts','shaded','random_min','random_max','font_size','line_weight','label_size','outline_weight']);
    els.visualControls.querySelectorAll('[data-vk]').forEach(el=>{
      let v=el.type==='checkbox'?el.checked:el.value; const k=el.dataset.vk;
      if(numericKeys.has(k) && el.type==='number') v=Number(v);
      if(['rows','cols'].includes(k) && el.type!=='number') v=v.split(',').map(x=>x.trim()).filter(Boolean);
      if(k==='expressions') v=String(v).split(/\n+/).map(x=>x.trim()).filter(Boolean);
      out[k]=v;
    });
    return out;
  }

  function showPendingVisual(asset){
    pendingVisual=asset;
    els.visualPreview.innerHTML=`<img src="${escapeHtml(asset.url)}" alt="${escapeHtml(asset.label||'Generated visual')}">`;
    els.visualStatus.textContent='Ready to insert. You can still change settings and generate again.';
    els.insertVisualBtn.disabled=false;
  }

  function visualFromEditorNode(node){
    if(!node) return null;
    let params={};
    try{params=JSON.parse(decodeURIComponent(node.dataset.visualParams||''))||{}}catch(_){params={}}
    const normalized=normalizeLegacyVisual(node.dataset.visualType||'blank_graph',params);
    return {type:normalized.type,params:normalized.params,url:node.getAttribute('src')||'',label:node.getAttribute('alt')||'Generated visual'};
  }

  function openVisualBuilder(id,index=null,mode='card',editorNode=null){
    visualTargetId=id; editingVisualIndex=index; pendingVisual=null; visualInsertMode=mode; editorVisualEditNode=editorNode||null;
    let existing=(mode==='card' && index!==null && id) ? attachedVisuals(id)[index] : null;
    if(mode==='editor-edit') existing=visualFromEditorNode(editorVisualEditNode);
    if(existing){ const normalized=normalizeLegacyVisual(existing.type,existing.params||{}); existing={...existing,...normalized}; }
    els.visualType.value=existing?.type || 'blank_graph';
    renderVisualControls(existing?.params || {});
    document.getElementById('visualModalTitle').textContent=existing?(mode==='editor-edit'?'Edit visual in editor':'Edit inserted visual'):(mode==='editor'?'Insert visual into editor':'Insert visual / printable');
    els.insertVisualBtn.textContent=existing?(mode==='editor-edit'?'Update editor visual':'Update visual'):(mode==='editor'?'Insert at cursor':'Insert visual');
    els.visualStatus.textContent='';
    if(existing) showPendingVisual(existing);
    else { els.visualPreview.innerHTML='<span>Choose settings and generate a preview.</span>'; els.insertVisualBtn.disabled=true; }
    els.visualModal.hidden=false; document.body.classList.add('modal-open');
  }

  function closeVisualBuilder(){
    const returnToEditor=(visualInsertMode==='editor' || visualInsertMode==='editor-edit') && !els.editorModal.hidden;
    els.visualModal.hidden=true; visualTargetId=null; editingVisualIndex=null; pendingVisual=null; visualInsertMode='card'; editorVisualEditNode=null;
    if(returnToEditor){ document.body.classList.add('modal-open'); setTimeout(restoreEditorSelection,0); }
    else if(els.saveModal.hidden && els.editorModal.hidden) document.body.classList.remove('modal-open');
  }

  function randInt(min,max){ return Math.floor(Math.random()*(max-min+1))+min; }

  function randomChoice(items){ return items[randInt(0,items.length-1)]; }

  function detectGraphFamily(expression){
    const raw=String(expression||'').toLowerCase().replace(/\s+/g,'');
    if(/^x=/.test(raw)) return 'vertical';
    const rhs=raw.includes('=')?raw.split('=').slice(1).join('='):raw;
    if(rhs.includes('sqrt(')) return 'sqrt';
    if(rhs.includes('abs(')) return 'absolute';
    if(/\^3(?:$|[+\-])/.test(rhs) || /\)\^3/.test(rhs)) return 'cubic';
    if(/\^2(?:$|[+\-])/.test(rhs) || /\)\^2/.test(rhs)) return 'quadratic';
    if(rhs.includes('/x') || /\/\(x/.test(rhs) || /1\/\(?x/.test(rhs)) return 'reciprocal';
    return 'linear';
  }

  function innerInteger(min,max,fraction=.18){
    const span=Math.max(1,max-min),lo=Math.ceil(min+span*fraction),hi=Math.floor(max-span*fraction);
    if(lo<=hi) return randInt(lo,hi);
    return Math.round((min+max)/2);
  }

  function signedTerm(value){
    if(!value) return '';
    return value>0?` + ${value}`:` - ${Math.abs(value)}`;
  }

  function shiftedX(h){
    if(!h) return 'x';
    return h>0?`(x - ${h})`:`(x + ${Math.abs(h)})`;
  }

  function scaled(core,a){
    if(a===1) return core;
    if(a===-1) return `-${core}`;
    return `${a}*${core}`;
  }

  function randomizeGraphExpression(expression,current){
    const family=detectGraphFamily(expression);
    const xmin=Number(current.xmin??-10),xmax=Number(current.xmax??10),ymin=Number(current.ymin??-10),ymax=Number(current.ymax??10);
    const h=innerInteger(xmin,xmax),k=innerInteger(ymin,ymax);
    const a=randomChoice([-3,-2,-1,-0.5,0.5,1,2,3]);
    const xh=shiftedX(h);
    if(family==='vertical') return `x = ${h}`;
    if(family==='quadratic') return `y = ${scaled(`${xh}^2`,a)}${signedTerm(k)}`;
    if(family==='absolute') return `y = ${scaled(`abs(${h?xh:'x'})`,a)}${signedTerm(k)}`;
    if(family==='cubic') return `y = ${scaled(`${xh}^3`,a)}${signedTerm(k)}`;
    if(family==='sqrt') return `y = ${scaled(`sqrt(${h?xh:'x'})`,a)}${signedTerm(k)}`;
    if(family==='reciprocal') return `y = ${a}/${h?xh:'x'}${signedTerm(k)}`;
    const b=innerInteger(ymin,ymax);
    return `y = ${a}x${signedTerm(b)}`;
  }

  function randomVisualParams(){
    const t=els.visualType.value;
    const current=readVisualParams();
    if(t==='blank_graph'){
      const choices=[[-5,5],[-10,10],[-20,20],[0,10],[0,20]];
      const [lo,hi]=choices[randInt(0,choices.length-1)];
      return {...current,xmin:lo,xmax:hi,ymin:lo,ymax:hi,xlabel:current.xlabel||'',ylabel:current.ylabel||''};
    }
    if(t==='function_graph'){
      const expressions=(Array.isArray(current.expressions)?current.expressions:[current.expressions||'y = x']).filter(Boolean);
      return {...current,expressions:expressions.map(expr=>randomizeGraphExpression(expr,current))};
    }
    if(t==='number_line'){
      const choices=[[-5,5],[-10,10],[-20,20],[0,10],[0,20],[10,30]];
      const [xmin,xmax]=choices[randInt(0,choices.length-1)];
      return {...current,xmin,xmax};
    }
    if(t==='diamond'){
      const lo=Math.min(Number(current.random_min??-12),Number(current.random_max??12)), hi=Math.max(Number(current.random_min??-12),Number(current.random_max??12)), allowZero=!!current.allow_zero;
      let a=randInt(lo,hi),b=randInt(lo,hi);
      if(!allowZero){ while(a===0) a=randInt(lo,hi); while(b===0) b=randInt(lo,hi); }
      const product=a*b,sum=a+b,pattern=current.pattern||'product_sum';
      if(pattern==='sides') return {top:'',bottom:'',left:a,right:b,pattern};
      if(pattern==='blank') return {top:'',bottom:'',left:'',right:'',pattern};
      if(pattern==='mixed') return Math.random()<.5?{top:product,bottom:'',left:a,right:'',pattern}:{top:'',bottom:sum,left:'',right:b,pattern};
      return {top:product,bottom:sum,left:'',right:'',pattern};
    }
    if(t==='input_output_table') return {...current,count:randInt(4,10)};
    if(t==='area_model'){
      const a=randInt(1,9), b=randInt(1,9);
      return {rows:['x',String(a)],cols:['x',String(b)]};
    }
    if(t==='fraction_bar'){
      const parts=randInt(2,12), shaded=randInt(1,Math.max(1,parts-1));
      return {parts,shaded};
    }
    if(t==='hundred_grid') return {shaded:randInt(1,99)};
    if(t==='unit_circle'){ const modes=['blank','angles','degrees_radians']; return {mode:modes[randInt(0,modes.length-1)]}; }
    return current;
  }

  async function randomizeVisual(){
    renderVisualControls(randomVisualParams());
    pendingVisual=null; els.insertVisualBtn.disabled=true;
    els.visualPreview.innerHTML='<span>Randomized settings. Generating preview…</span>';
    await generateVisualPreview();
  }

  async function generateVisualPreview(){
    els.generateVisualBtn.disabled=true; els.visualStatus.textContent='Generating visual…';
    try{
      const type=els.visualType.value, params=readVisualParams();
      const r=await fetch('/api/visuals/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type,params})});
      const data=await r.json().catch(()=>({}));
      if(!r.ok || !data.url) throw new Error(data.error || `Generation failed (${r.status})`);
      showPendingVisual({type,params,url:data.url,label:data.label || 'Generated visual'});
    }catch(err){ pendingVisual=null; els.insertVisualBtn.disabled=true; els.visualStatus.textContent=`Could not generate visual: ${err.message}`; }
    finally{ els.generateVisualBtn.disabled=false; }
  }

  function insertPendingVisual(){
    if(!pendingVisual) return;
    if(visualInsertMode==='editor' || visualInsertMode==='editor-edit'){
      const asset=JSON.parse(JSON.stringify(pendingVisual));
      const encoded=encodeURIComponent(JSON.stringify(asset.params || {}));
      if(visualInsertMode==='editor-edit' && editorVisualEditNode){
        editorVisualEditNode.src=asset.url; editorVisualEditNode.alt=asset.label||'Generated visual'; editorVisualEditNode.dataset.visualType=asset.type||''; editorVisualEditNode.dataset.visualParams=encoded; editorVisualEditNode.title='Click, then use Edit visual; or double-click to edit.';
      }else{
        insertHtmlAtEditor(`<p class="teacher-visual-block"><img class="teacher-inline-visual" src="${escapeHtml(asset.url)}" alt="${escapeHtml(asset.label||'Generated visual')}" data-visual-type="${escapeHtml(asset.type||'')}" data-visual-params="${escapeHtml(encoded)}" title="Click, then use Edit visual; or double-click to edit."></p><p><br></p>`);
      }
      closeVisualBuilder();
      return;
    }
    if(!visualTargetId) return;
    const list=attachedVisuals(visualTargetId);
    if(editingVisualIndex===null) list.push(JSON.parse(JSON.stringify(pendingVisual)));
    else list[editingVisualIndex]=JSON.parse(JSON.stringify(pendingVisual));
    save(); closeVisualBuilder(); renderAll();
  }

  async function loadCardPack(packPath){
    if(!packPath) return null;
    if(loadedPacks.has(packPath)) return loadedPacks.get(packPath);
    const promise=fetch(PACK_BASE+packPath,{cache:'no-store'}).then(async r=>{
      if(!r.ok) throw new Error(`Could not load card pack ${packPath}`);
      const pack=await r.json();
      (pack.cards||[]).forEach(card=>cards.set(card.card_id,card));
      return pack;
    });
    loadedPacks.set(packPath,promise);
    return promise;
  }

  async function loadSelectedSourceCards(){
    const sourceIds=order.filter(id=>!isCustomId(id));
    const packPaths=[...new Set(sourceIds.map(id=>indexMap.get(id)?.pack).filter(Boolean))];
    await Promise.all(packPaths.map(loadCardPack));
    const legacy=sourceIds.filter(id=>!cards.has(id) && indexMap.get(id)?.path);
    await Promise.all(legacy.map(async id=>{
      const meta=indexMap.get(id);
      cards.set(id,await fetch(CARD_BASE+meta.path,{cache:'no-store'}).then(r=>r.json()));
    }));
  }

  function chapterForMeta(meta){
    if(meta?.chapter != null && String(meta.chapter).trim()) return String(meta.chapter).replace(/^0+/,'') || '0';
    const lesson=String(meta?.lesson || '');
    const match=lesson.match(/^(\d+)/);
    if(match) return String(Number(match[1]));
    const cardMatch=String(meta?.card_id || '').match(/-ch0*(\d+)-/i);
    return cardMatch ? String(Number(cardMatch[1])) : 'Other';
  }

  function applyDirectTextbookAssembly(indexCards){
    if(currentSavedSetId || handoffSource) return false;
    const mode=launchParams.get('assemble');
    if(mode!=='chapter' && mode!=='section') return false;
    const requestedChapter=String(launchParams.get('chapter') || '').trim();
    const requestedSection=String(launchParams.get('section') || '').trim();
    if(!requestedChapter) throw new Error('Choose a chapter before opening assembled content.');
    let metas=indexCards.filter(meta=>chapterForMeta(meta)===requestedChapter);
    let title=`CC3 Chapter ${requestedChapter}`;
    if(mode==='section'){
      if(!/^\d+\.\d+\.\d+$/.test(requestedSection)) throw new Error('Choose a numbered section before opening assembled content.');
      metas=metas.filter(meta=>String(meta.lesson || '')===requestedSection);
      const titleCard=metas.find(meta=>meta.card_type==='title');
      title=titleCard?.title ? `${requestedSection} — ${titleCard.title}` : `CC3 Section ${requestedSection}`;
    }
    if(!metas.length) throw new Error(`No captured cards were found for ${mode==='section' ? `Section ${requestedSection}` : `Chapter ${requestedChapter}`}.`);
    order=metas.map(meta=>meta.card_id);
    breaks=new Set(); cardOptions={}; customCards={}; sourceOverrides={}; sectionHeadings={}; assessmentBundle=null; assessmentActiveIndex=0;
    settings={spacing:'normal',margin:'normal',figure:'normal',workspace:'medium',figurePx:null,workspaceIn:null,title,showTitle:true};
    [BREAK_KEY,CARD_OPTIONS_KEY,CUSTOM_KEY,SOURCE_OVERRIDE_KEY,SECTION_HEADING_KEY,ASSESSMENT_HANDOFF_KEY,ASSESSMENT_SESSION_KEY].forEach(key=>localStorage.removeItem(key));
    localStorage.setItem(STORAGE_KEY,JSON.stringify(order));
    localStorage.setItem(ORDER_KEY,JSON.stringify(order));
    localStorage.setItem(SETTINGS_KEY,JSON.stringify(settings));
    return true;
  }

  async function init(){
    await loadSavedSetIfRequested();
    applyAssessmentHandoffIfRequested();
    const idx=await fetch(INDEX_URL,{cache:'no-store'}).then(r=>r.json());
    const indexCards=idx.cards||[];
    indexMap=new Map(indexCards.map(c=>[c.card_id,c]));
    applyDirectTextbookAssembly(indexCards);
    installCustomCards();
    order=order.filter(id=>indexMap.has(id));
    await loadSelectedSourceCards();
    installCustomCards();
    syncControls();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order.filter(id => !isCustomId(id))));
    localStorage.setItem(ORDER_KEY, JSON.stringify(order));
    localStorage.setItem(BREAK_KEY, JSON.stringify([...breaks]));
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    localStorage.setItem(CARD_OPTIONS_KEY, JSON.stringify(cardOptions));
    localStorage.setItem(CUSTOM_KEY, JSON.stringify(customCards));
    localStorage.setItem(SOURCE_OVERRIDE_KEY, JSON.stringify(sourceOverrides));
    localStorage.setItem(SECTION_HEADING_KEY, JSON.stringify(sectionHeadings));
    if(assessmentBundle){
      const back=document.getElementById('backPicker');
      const topBack=document.querySelector('.appbar-link');
      if(currentSavedSetId){
        if(back) back.textContent='← Back to Library';
        if(topBack){ topBack.href='/saved/index.html'; topBack.textContent='← Library'; }
      }else{
        if(back) back.textContent='← Back to Assessment Builder';
        if(topBack){ topBack.href='/assessments/index.html'; topBack.textContent='← Assessment Builder'; }
      }
    }
    renderAssessmentVersionControls();
    renderAll(); updateSaveStatus();
  }

  document.querySelectorAll('.segmented button').forEach(btn=>btn.addEventListener('click',()=>{
    const group=btn.closest('.segmented');settings[group.dataset.setting]=btn.dataset.value;syncControls();save();renderAll();
  }));
  bindGlobalRangeControls();
  [els.title,els.showTitle].forEach(el=>el.addEventListener(el===els.title?'input':'change',()=>{save();schedulePaginate();}));
  document.getElementById('clearAssembly').onclick=()=>{
    if(!confirm('Clear all selected and teacher-created cards from this assembly?')) return;
    order=[];breaks.clear();cardOptions={};customCards={};sourceOverrides={};sectionHeadings={};save();renderAll();
  };
  document.getElementById('backPicker').onclick=()=>{save();location.href=(currentSavedSetId && assessmentBundle)?'/saved/index.html':(currentSavedSetId?`/builder/index.html?set=${encodeURIComponent(currentSavedSetId)}`:(assessmentBundle?'/assessments/index.html':'/builder/index.html'));};
  els.newAssessmentVersion?.addEventListener('click',addAssessmentVersion);
  els.printAllVersions?.addEventListener('click',printAllAssessmentVersions);
  els.summativePacketPanel?.addEventListener('click',e=>{
    const button=e.target.closest('[data-packet-version]');
    if(!button) return;
    const index=Number(button.dataset.packetVersion),kind=button.dataset.packetKind;
    if(!Number.isInteger(index) || !['mc','frq'].includes(kind)) return;
    printSummativePacket(kind,[index]);
  });
  els.frqPacketAll?.addEventListener('click',()=>printSummativePacket('frq',allAssessmentVersionIndexes()));
  els.mcPacketAll?.addEventListener('click',()=>printSummativePacket('mc',allAssessmentVersionIndexes()));
  document.getElementById('demoPrint').onclick=async()=>{save();clearTimeout(paginateTimer);paginate();await typesetPages();window.print();};
  els.saveSet.addEventListener('click',()=>{ if(currentSavedSetId){ saveAsMode=false; els.saveSetName.value=currentSavedSetName || settings.title || 'Untitled document'; saveSetToLibrary(); } else openSaveDialog(true); });
  els.saveSetAs.addEventListener('click',()=>openSaveDialog(true));
  document.querySelectorAll('[data-close-save]').forEach(x=>x.addEventListener('click',closeSaveDialog));
  els.confirmSaveSet.addEventListener('click',saveSetToLibrary);
  els.saveSetName.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();saveSetToLibrary();}});

  document.querySelectorAll('[data-close-visual]').forEach(x=>x.addEventListener('click',closeVisualBuilder));
  els.visualType.addEventListener('change',()=>{renderVisualControls({});pendingVisual=null;els.visualPreview.innerHTML='<span>Choose settings and generate a preview.</span>';els.visualStatus.textContent='';els.insertVisualBtn.disabled=true;});
  els.generateVisualBtn.addEventListener('click',generateVisualPreview);
  els.randomizeVisualBtn?.addEventListener('click',randomizeVisual);
  els.insertVisualBtn.addEventListener('click',insertPendingVisual);

  els.addContentBtn.addEventListener('click',()=>{els.addContentMenu.hidden=!els.addContentMenu.hidden;});
  els.addContentMenu.querySelectorAll('[data-add-type]').forEach(btn=>btn.addEventListener('click',()=>{
    els.addContentMenu.hidden=true; openCustomEditor(btn.dataset.addType);
  }));
  document.addEventListener('click',e=>{
    if(!els.addContentMenu.hidden && !e.target.closest('.add-content-wrap')) els.addContentMenu.hidden=true;
  });
  document.querySelectorAll('[data-close-editor]').forEach(x=>x.addEventListener('click',closeCustomEditor));
  els.saveCustomCard.addEventListener('click',saveCustomEditor);
  els.placementMode.addEventListener('change',updatePlacementHint);
  els.placementReference.addEventListener('change',updatePlacementHint);
  els.richEditor.addEventListener('keyup',saveEditorSelection); els.richEditor.addEventListener('mouseup',saveEditorSelection); els.richEditor.addEventListener('focus',saveEditorSelection);
  function selectEditorVisual(node){ editorVisualEditNode=node?.classList?.contains('teacher-inline-visual')?node:null; if(els.editorEditVisualBtn) els.editorEditVisualBtn.hidden=!editorVisualEditNode; }
  els.richEditor.addEventListener('click',e=>{ const img=e.target.closest?.('img.teacher-inline-visual'); selectEditorVisual(img||null); });
  els.richEditor.addEventListener('dblclick',e=>{ const img=e.target.closest?.('img.teacher-inline-visual'); if(!img)return; e.preventDefault(); selectEditorVisual(img); openVisualBuilder(null,null,'editor-edit',img); });
  els.editorEditVisualBtn?.addEventListener('click',()=>{if(editorVisualEditNode) openVisualBuilder(null,null,'editor-edit',editorVisualEditNode);});
  document.querySelectorAll('.rich-toolbar [data-cmd]').forEach(btn=>btn.addEventListener('click',()=>execEditorCommand(btn.dataset.cmd)));
  document.getElementById('editorBlockStyle').addEventListener('change',e=>execEditorCommand('formatBlock',e.target.value));
  document.getElementById('editorLinkBtn').addEventListener('click',()=>{
    saveEditorSelection(); const url=prompt('Link URL'); if(url) execEditorCommand('createLink',url);
  });
  els.editorImageBtn.addEventListener('click',()=>{
    saveEditorSelection(); els.editorImageFile.click();
  });
  els.editorImageFile.addEventListener('change',()=>uploadEditorImage(els.editorImageFile.files?.[0]));
  document.getElementById('editorImageUrlBtn').addEventListener('click',()=>{
    saveEditorSelection(); const url=prompt('Image URL'); if(!url) return; const alt=prompt('Alt text (optional)')||'';
    insertHtmlAtEditor(`<img src="${escapeHtml(url)}" alt="${escapeHtml(alt)}">`);
  });
  document.getElementById('editorTableBtn').addEventListener('click',()=>{
    saveEditorSelection();
    insertHtmlAtEditor('<table><tbody><tr><td>&nbsp;</td><td>&nbsp;</td></tr><tr><td>&nbsp;</td><td>&nbsp;</td></tr></tbody></table><p><br></p>');
  });
  document.getElementById('editorMathBtn').addEventListener('click',openMathPanel);
  document.getElementById('editorVisualBtn').addEventListener('click',()=>{ saveEditorSelection(); openVisualBuilder(null,null,'editor'); });
  document.querySelectorAll('[data-math-snippet]').forEach(btn=>btn.addEventListener('click',()=>insertMathSnippet(btn.dataset.mathSnippet)));
  els.mathTemplateSelect.addEventListener('change',()=>{ if(els.mathTemplateSelect.value) insertMathSnippet(els.mathTemplateSelect.value); els.mathTemplateSelect.value=''; });
  els.mathExampleSelect.addEventListener('change',()=>{ if(els.mathExampleSelect.value) insertMathSnippet(els.mathExampleSelect.value,true); els.mathExampleSelect.value=''; });
  document.getElementById('cancelMathBtn').addEventListener('click',()=>{els.mathPanel.hidden=true;restoreEditorSelection();});
  document.getElementById('insertMathBtn').addEventListener('click',insertMath);
  els.mathInput.addEventListener('input',updateMathPreview); els.mathDisplay.addEventListener('change',updateMathPreview);

  window.addEventListener('resize',schedulePaginate);
  window.addEventListener('beforeprint',()=>document.body.classList.add('printing-exact')); 
  window.addEventListener('afterprint',()=>document.body.classList.remove('printing-exact'));
  init().catch(err=>{console.error(err);els.pages.innerHTML='<div class="empty-state">Could not load the selected cards.</div>';});
})();
