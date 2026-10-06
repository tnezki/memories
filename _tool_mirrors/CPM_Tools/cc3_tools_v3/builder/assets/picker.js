(() => {
  const INDEX_URL = '/library/textbooks/cc3e3/cards/index.json';
  const PACK_BASE = '/library/textbooks/cc3e3/cards/';
  const STATUS_URL = '/library/textbooks/cc3e3/source_status.json';
  const STORAGE_KEY = 'cc3e3_builder_selection_v1';
  const ORDER_KEY = 'cc3e3_builder_order_v1';
  const CUSTOM_KEY = 'cc3e3_builder_custom_cards_v1';
  const BREAK_KEY = 'cc3e3_builder_breaks_v1';
  const SETTINGS_KEY = 'cc3e3_builder_settings_v2';
  const CARD_OPTIONS_KEY = 'cc3e3_builder_card_options_v3';
  const SOURCE_OVERRIDE_KEY = 'cc3e3_builder_source_overrides_v1';
  const SECTION_HEADING_KEY = 'cc3e3_builder_section_headings_v1';
  const ASSESSMENT_HANDOFF_KEY = 'cc3e3_assessment_handoff_v1';
  const ASSESSMENT_SESSION_KEY = 'cc3e3_assessment_version_session_v1';
  const ACTIVE_SET_ID = new URLSearchParams(location.search).get('set');

  const els = {
    grid: document.getElementById('cardGrid'),
    resultSummary: document.getElementById('resultSummary'),
    selectedCount: document.getElementById('selectedCount'),
    search: document.getElementById('searchInput'),
    chapter: document.getElementById('chapterFilter'),
    lesson: document.getElementById('lessonFilter'),
    types: document.getElementById('typeFilters'),
    sourceStatus: document.getElementById('sourceStatus'),
    assemble: document.getElementById('assembleBtn'),
    clearSaved: document.getElementById('clearSavedBtn')
  };

  let index = [];
  let cards = new Map();
  let loadedPacks = new Set();
  let sourceStatus = {};
  let activeType = 'all';
  let selected = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));
  let chapterLoadToken = 0;

  function escapeHtml(s='') { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

  function normalizePreview(root) {
    root.querySelectorAll('img[data-missing-src], img:not([src])').forEach(img => img.remove());
    root.querySelectorAll('[style]').forEach(node => {
      node.style.removeProperty('font-size');
      node.style.removeProperty('line-height');
      node.style.removeProperty('font-family');
      node.style.removeProperty('letter-spacing');
      if (!node.getAttribute('style')?.trim()) node.removeAttribute('style');
    });
    root.querySelectorAll('a').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
  }

  function saveSelection() {
    const extractedOrdered = index.filter(c => selected.has(c.card_id)).map(c => c.card_id);
    const customCards = JSON.parse(localStorage.getItem(CUSTOM_KEY) || '{}');
    const currentOrder = JSON.parse(localStorage.getItem(ORDER_KEY) || '[]');
    const keep = currentOrder.filter(id => customCards[id] || selected.has(id));
    const seen = new Set(keep);
    extractedOrdered.forEach(id => { if (!seen.has(id)) { keep.push(id); seen.add(id); } });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(extractedOrdered));
    localStorage.setItem(ORDER_KEY, JSON.stringify(keep));
    els.selectedCount.textContent = `${selected.size} selected`;
    els.assemble.disabled = selected.size === 0 && !Object.keys(customCards).length;
  }

  function clearAssemblyStateForDirectBuild() {
    [BREAK_KEY, CARD_OPTIONS_KEY, CUSTOM_KEY, SOURCE_OVERRIDE_KEY, SECTION_HEADING_KEY, ASSESSMENT_HANDOFF_KEY, ASSESSMENT_SESSION_KEY].forEach(key => localStorage.removeItem(key));
  }

  function directBuildFromParams(params) {
    const mode = params.get('assemble');
    if (mode !== 'chapter' && mode !== 'section') return false;
    const requestedChapter = String(params.get('chapter') || '').trim();
    const requestedSection = String(params.get('section') || '').trim();
    if (!requestedChapter) throw new Error('Choose a chapter before opening assembled content.');
    let metas = index.filter(meta => chapterFor(meta) === requestedChapter);
    let title = `CC3 Chapter ${requestedChapter}`;
    if (mode === 'section') {
      if (!/^\d+\.\d+\.\d+$/.test(requestedSection)) throw new Error('Choose a numbered section before opening assembled content.');
      metas = metas.filter(meta => String(meta.lesson || '') === requestedSection);
      title = `CC3 Section ${requestedSection}`;
    }
    if (!metas.length) throw new Error(`No captured cards were found for ${mode === 'section' ? `Section ${requestedSection}` : `Chapter ${requestedChapter}`}.`);
    const ids = metas.map(meta => meta.card_id);
    clearAssemblyStateForDirectBuild();
    selected = new Set(ids);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
    localStorage.setItem(ORDER_KEY, JSON.stringify(ids));
    localStorage.setItem(SETTINGS_KEY, JSON.stringify({spacing:'normal',margin:'normal',figure:'normal',workspace:'medium',title,showTitle:true}));
    location.replace('/builder/assemble.html');
    return true;
  }

  function chapterFor(meta) {
    if (meta.chapter != null && String(meta.chapter).trim()) return String(meta.chapter).replace(/^0+/, '') || '0';
    const lesson = String(meta.lesson || '');
    const match = lesson.match(/^(\d+)/);
    if (match) return String(Number(match[1]));
    const cardMatch = String(meta.card_id || '').match(/-ch0*(\d+)-/i);
    return cardMatch ? String(Number(cardMatch[1])) : 'Other';
  }

  function lessonsForChapter(chapter) {
    const seen = new Set(), out = [];
    index.filter(c => chapterFor(c) === chapter).forEach(c => {
      if (!seen.has(c.lesson)) { seen.add(c.lesson); out.push(c.lesson); }
    });
    return out;
  }

  function lessonLabel(lesson) {
    if (lesson === 'intro') return 'Chapter Introduction';
    if (lesson === 'closure') return 'Chapter Closure';
    const first = index.find(c => c.lesson === lesson && c.card_type === 'title');
    if (first) return first.title;
    return lesson;
  }

  function rebuildLessonOptions(preferred=null) {
    const chapter = els.chapter.value;
    const lessons = lessonsForChapter(chapter);
    els.lesson.innerHTML = '';
    const all = document.createElement('option');
    all.value = 'all'; all.textContent = `All available content in Chapter ${chapter}`;
    els.lesson.appendChild(all);
    lessons.forEach(lesson => {
      const o = document.createElement('option');
      o.value = lesson; o.textContent = lessonLabel(lesson);
      els.lesson.appendChild(o);
    });
    if (preferred && lessons.includes(preferred)) els.lesson.value = preferred;
    updateSourceStatus();
  }

  function updateSourceStatus() {
    if (!els.sourceStatus) return;
    const chapter = els.chapter.value;
    const lesson = els.lesson.value;
    if (lesson === 'all') {
      const gaps = Object.entries(sourceStatus).filter(([,v]) => String(v.chapter) === chapter && v.status !== 'captured');
      if (gaps.length) {
        els.sourceStatus.className = 'source-status warn';
        els.sourceStatus.textContent = `${gaps.length} lesson capture${gaps.length===1?'':'s'} in this chapter still have source gaps. Captured lessons are fully usable.`;
      } else {
        els.sourceStatus.className = 'source-status ok';
        els.sourceStatus.textContent = 'Chapter source capture is complete.';
      }
      return;
    }
    const key = lesson === 'closure' ? `${chapter}.closure` : lesson;
    const info = sourceStatus[key];
    if (info && info.status !== 'captured') {
      els.sourceStatus.className = 'source-status warn';
      els.sourceStatus.textContent = 'Source gap: only the lesson title / Learning Focus is available from this capture. Student problems are not included yet.';
    } else {
      els.sourceStatus.className = 'source-status ok';
      els.sourceStatus.textContent = 'Student-facing source captured.';
    }
  }

  function visibleCards() {
    const q = els.search.value.trim().toLowerCase();
    return index.filter(meta => {
      if (chapterFor(meta) !== els.chapter.value) return false;
      if (els.lesson.value !== 'all' && meta.lesson !== els.lesson.value) return false;
      if (activeType !== 'all' && meta.card_type !== activeType) return false;
      if (!q) return true;
      const hay = `${meta.title || ''} ${meta.lesson || ''} ${meta.section || ''} ${meta.card_type || ''} ${meta.search_text || ''}`.toLowerCase();
      return hay.includes(q);
    });
  }

  function typeClass(type) { return `type-${String(type).replace(/[^a-z0-9_-]/gi,'-')}`; }

  function render() {
    const visible = visibleCards();
    const chapterTotal = index.filter(c => chapterFor(c) === els.chapter.value).length;
    els.resultSummary.textContent = `${visible.length} of ${chapterTotal} cards shown in Chapter ${els.chapter.value}`;
    els.grid.innerHTML = '';
    if (!visible.length) {
      els.grid.innerHTML = '<div class="empty-state">No cards match these filters.</div>';
      return;
    }
    const frag = document.createDocumentFragment();
    visible.forEach(meta => {
      const data = cards.get(meta.card_id);
      const article = document.createElement('article');
      article.className = `pick-card${selected.has(meta.card_id) ? ' selected' : ''}`;
      article.dataset.id = meta.card_id;
      const gapBadge = meta.source_status && meta.source_status !== 'captured' ? '<span class="source-gap-tag">Source gap</span>' : '';
      article.innerHTML = `
        <div class="pick-card-header">
          <input class="pick-check" type="checkbox" aria-label="Select ${escapeHtml(meta.title)}" ${selected.has(meta.card_id) ? 'checked' : ''}>
          <div class="pick-headtext">
            <div class="pick-title">${escapeHtml(meta.title)}</div>
            <div class="pick-meta">${escapeHtml(meta.lesson)} · ${escapeHtml(meta.section)}</div>
          </div>
          ${gapBadge}<span class="type-tag ${typeClass(meta.card_type)}">${escapeHtml(meta.card_type)}</span>
        </div>
        <div class="pick-preview">${data ? '' : '<p class="loading-preview">Loading preview…</p>'}</div>
        <div class="pick-card-footer"><button class="expand-btn">Expand preview</button></div>`;
      const preview = article.querySelector('.pick-preview');
      if (data) { preview.innerHTML = data.html || '<p>Preview unavailable.</p>'; normalizePreview(preview); }
      const checkbox = article.querySelector('.pick-check');
      checkbox.addEventListener('change', () => {
        checkbox.checked ? selected.add(meta.card_id) : selected.delete(meta.card_id);
        article.classList.toggle('selected', checkbox.checked);
        saveSelection();
      });
      article.querySelector('.expand-btn').addEventListener('click', () => {
        article.classList.toggle('expanded');
        article.querySelector('.expand-btn').textContent = article.classList.contains('expanded') ? 'Collapse preview' : 'Expand preview';
      });
      frag.appendChild(article);
    });
    els.grid.appendChild(frag);
  }

  async function loadPack(packPath) {
    if (!packPath || loadedPacks.has(packPath)) return;
    const pack = await fetch(PACK_BASE + packPath, {cache:'no-store'}).then(r => {
      if (!r.ok) throw new Error(`Could not load ${packPath}`);
      return r.json();
    });
    (pack.cards || []).forEach(card => cards.set(card.card_id, card));
    loadedPacks.add(packPath);
  }

  async function loadChapter(chapter) {
    const token = ++chapterLoadToken;
    const metas = index.filter(c => chapterFor(c) === chapter);
    const packs = [...new Set(metas.map(c => c.pack).filter(Boolean))];
    els.grid.innerHTML = '<div class="empty-state">Loading chapter cards…</div>';
    await Promise.all(packs.map(loadPack));
    if (token !== chapterLoadToken) return false;
    return true;
  }

  async function showChapter(preferredLesson=null) {
    rebuildLessonOptions(preferredLesson);
    updateSourceStatus();
    await loadChapter(els.chapter.value);
    render();
  }

  async function init() {
    const [idx, status] = await Promise.all([
      fetch(INDEX_URL, {cache:'no-store'}).then(r => r.json()),
      fetch(STATUS_URL, {cache:'no-store'}).then(r => r.ok ? r.json() : {}).catch(() => ({}))
    ]);
    index = idx.cards || [];
    sourceStatus = status || {};
    selected = new Set([...selected].filter(id => index.some(c => c.card_id === id)));

    const params = new URLSearchParams(location.search);
    if (directBuildFromParams(params)) return;

    const chapterSet = [...new Set(index.map(chapterFor))].sort((a,b) => Number(a)-Number(b));
    chapterSet.forEach(chapter => {
      const o = document.createElement('option'); o.value = chapter; o.textContent = `Chapter ${chapter}`; els.chapter.appendChild(o);
    });
    const typeSet = ['all', ...new Set(index.map(c => c.card_type))];
    typeSet.forEach(type => {
      const b = document.createElement('button');
      b.className = `filter-chip${type === 'all' ? ' active' : ''}`;
      b.textContent = type === 'all' ? 'All' : type[0].toUpperCase() + type.slice(1).replace(/_/g,' ');
      b.addEventListener('click', () => {
        activeType = type;
        els.types.querySelectorAll('button').forEach(x => x.classList.toggle('active', x === b));
        render();
      });
      els.types.appendChild(b);
    });

    const requestedLesson = params.get('lesson');
    let requestedChapter = params.get('chapter');
    if (!requestedChapter && requestedLesson && /^\d+/.test(requestedLesson)) requestedChapter = requestedLesson.match(/^\d+/)[0];
    els.chapter.value = requestedChapter && chapterSet.includes(requestedChapter) ? requestedChapter : chapterSet[0];
    saveSelection();
    await showChapter(requestedLesson);
  }

  els.search.addEventListener('input', render);
  els.chapter.addEventListener('change', async () => { await showChapter(); });
  els.lesson.addEventListener('change', () => { updateSourceStatus(); render(); });
  document.querySelectorAll('[data-quick]').forEach(btn => btn.addEventListener('click', () => {
    const mode = btn.dataset.quick;
    if (mode === 'clear') selected.clear();
    if (mode === 'visible') visibleCards().forEach(c => selected.add(c.card_id));
    if (mode === 'questions') visibleCards().filter(c => c.card_type === 'question').forEach(c => selected.add(c.card_id));
    if (mode === 'lesson') {
      const lesson = els.lesson.value;
      (lesson === 'all' ? visibleCards() : index.filter(c => chapterFor(c)===els.chapter.value && c.lesson === lesson)).forEach(c => selected.add(c.card_id));
    }
    saveSelection(); render();
  }));
  els.assemble.addEventListener('click', () => { saveSelection(); location.href = ACTIVE_SET_ID ? `/builder/assemble.html?set=${encodeURIComponent(ACTIVE_SET_ID)}` : '/builder/assemble.html'; });
  els.clearSaved.addEventListener('click', () => { selected.clear(); localStorage.removeItem(ORDER_KEY); saveSelection(); render(); });

  init().catch(err => {
    console.error(err);
    els.grid.innerHTML = '<div class="empty-state">Could not load the extracted card library.</div>';
  });
})();
