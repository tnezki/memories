(() => {
  const legacyBox = document.querySelector('.custom-box');
  if (!legacyBox) return;

  const legacy = {
    enabled: document.getElementById('customEnabled'),
    description: document.getElementById('customDescription'),
    count: document.getElementById('customCount')
  };
  if (!legacy.enabled || !legacy.description || !legacy.count) return;

  let nextId = 1;
  let items = [];
  let trayObserver = null;

  const style = document.createElement('style');
  style.textContent = `
    .custom-box{display:none!important}
    .custom-multi-panel{margin-top:4px;border:1px dashed #91aac0;border-radius:14px;padding:14px;background:#fbfdff;display:grid;gap:12px}
    .custom-multi-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
    .custom-multi-head strong{color:#173f6a;font-size:14px}
    .custom-multi-list{display:grid;gap:10px}
    .custom-entry{border:1px solid #d4dde7;border-radius:12px;background:#fff;padding:12px;display:grid;gap:9px}
    .custom-entry-head{display:flex;align-items:center;justify-content:space-between;gap:12px}
    .custom-entry-title{font-size:13px;font-weight:900;color:#1d4264}
    .custom-entry-actions{display:flex;align-items:center;gap:8px}
    .custom-entry textarea{width:100%;min-height:88px;border:1px solid #c1cbd6;border-radius:9px;padding:10px 11px;font:inherit;resize:vertical}
    .custom-remove{border:0;background:transparent;color:#8a3940;font-size:20px;line-height:1;cursor:pointer;padding:4px 6px}
    .custom-add-btn{width:100%;min-height:58px;border:2px dashed #7da2c1;border-radius:12px;background:#f4f9fd;color:#17486d;font:inherit;font-weight:900;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px}
    .custom-add-btn:hover{background:#eaf3fa;border-color:#4f82aa}
    .custom-add-btn .big-plus{font-size:32px;line-height:1;font-weight:700}
    .custom-summary-badge{padding:7px 10px;border-radius:999px;background:#eaf3fa;color:#17486d;font-size:11px;font-weight:900;white-space:nowrap}
    @media(max-width:620px){.custom-entry-head{align-items:flex-start}.custom-entry-actions{flex-wrap:wrap;justify-content:flex-end}}
  `;
  document.head.appendChild(style);

  const panel = document.createElement('div');
  panel.className = 'custom-multi-panel';
  panel.innerHTML = `
    <div class="custom-multi-head">
      <div><strong>Custom question structures</strong><div class="small muted">Add as many teacher-defined question types as you need. Each custom structure keeps its own quantity and description.</div></div>
    </div>
    <div id="customMultiList" class="custom-multi-list"></div>
    <button id="addAnotherCustom" class="custom-add-btn" type="button"><span class="big-plus">+</span><span>Add another custom question structure</span></button>
  `;
  legacyBox.insertAdjacentElement('afterend', panel);

  const list = panel.querySelector('#customMultiList');
  const addButton = panel.querySelector('#addAnotherCustom');

  function clamp(n){ return Math.max(1, Math.min(10, Math.round(Number(n) || 1))); }
  function total(){ return items.reduce((sum, item) => sum + item.count, 0); }
  function allDescriptionsComplete(){ return items.every(item => item.description.trim().length > 0); }

  function manifestText(){
    const payload = items.map((item, i) => ({
      custom_id: `custom_${i+1}`,
      requested_count: item.count,
      description: item.description.trim()
    }));
    return 'MULTI_CUSTOM_STRUCTURES_V1\n' + JSON.stringify(payload, null, 2);
  }

  function syncLegacy(){
    const on = items.length > 0;
    if (legacy.enabled.checked !== on) {
      legacy.enabled.checked = on;
      legacy.enabled.dispatchEvent(new Event('change', {bubbles:true}));
    }
    legacy.count.value = String(total() || 1);
    legacy.description.value = on && allDescriptionsComplete() ? manifestText() : '';
    legacy.description.dispatchEvent(new Event('input', {bubbles:true}));
    decorateSelectedTray();
  }

  function render(){
    list.innerHTML = '';
    items.forEach((item, index) => {
      const card = document.createElement('div');
      card.className = 'custom-entry';
      card.dataset.customId = String(item.id);
      card.innerHTML = `
        <div class="custom-entry-head">
          <div class="custom-entry-title">Custom question structure ${index+1}</div>
          <div class="custom-entry-actions">
            <div class="qty">
              <button class="qty-btn" data-custom-minus="${item.id}" type="button">−</button>
              <input class="qty-input" data-custom-count="${item.id}" type="number" min="1" max="10" value="${item.count}" aria-label="Quantity for custom question structure ${index+1}">
              <button class="qty-btn" data-custom-plus="${item.id}" type="button">+</button>
            </div>
            <button class="custom-remove" data-custom-remove="${item.id}" type="button" title="Remove custom question structure ${index+1}">×</button>
          </div>
        </div>
        <textarea data-custom-description="${item.id}" placeholder="Describe the question type, representation, or pattern you want.">${escapeHtml(item.description)}</textarea>
      `;
      list.appendChild(card);
    });
    bindEntryEvents();
    syncLegacy();
  }

  function escapeHtml(value){
    return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }

  function itemById(id){ return items.find(item => item.id === Number(id)); }

  function bindEntryEvents(){
    list.querySelectorAll('[data-custom-minus]').forEach(btn => btn.addEventListener('click', () => {
      const item = itemById(btn.dataset.customMinus); if (!item) return;
      item.count = clamp(item.count - 1); render();
    }));
    list.querySelectorAll('[data-custom-plus]').forEach(btn => btn.addEventListener('click', () => {
      const item = itemById(btn.dataset.customPlus); if (!item) return;
      item.count = clamp(item.count + 1); render();
    }));
    list.querySelectorAll('[data-custom-count]').forEach(input => input.addEventListener('input', () => {
      const item = itemById(input.dataset.customCount); if (!item) return;
      item.count = clamp(input.value); input.value = String(item.count); syncLegacy();
    }));
    list.querySelectorAll('[data-custom-description]').forEach(area => area.addEventListener('input', () => {
      const item = itemById(area.dataset.customDescription); if (!item) return;
      item.description = area.value; syncLegacy();
    }));
    list.querySelectorAll('[data-custom-remove]').forEach(btn => btn.addEventListener('click', () => {
      items = items.filter(item => item.id !== Number(btn.dataset.customRemove)); render();
    }));
  }

  function addCustom(){
    const item = {id: nextId++, count: 1, description: ''};
    items.push(item);
    render();
    requestAnimationFrame(() => list.querySelector(`[data-custom-description="${item.id}"]`)?.focus());
  }

  function clearAll(){ items = []; render(); }

  function decorateSelectedTray(){
    const tray = document.getElementById('selectedTray');
    if (!tray) return;
    const control = tray.querySelector('[data-custom-tray-count]');
    if (!control) return;
    const row = control.closest('.selected-item');
    if (!row || row.dataset.multiCustomDecorated === '1') return;
    row.dataset.multiCustomDecorated = '1';
    row.innerHTML = `
      <div><strong>${items.length} custom question structure${items.length===1?'':'s'}</strong><span class="selected-meta">Edit individual descriptions and quantities above.</span></div>
      <div class="custom-summary-badge">${total()} question${total()===1?'':'s'}</div>
      <button class="remove-btn" data-remove-all-custom type="button" title="Remove all custom question structures">×</button>
    `;
    row.querySelector('[data-remove-all-custom]')?.addEventListener('click', clearAll);
  }

  addButton.addEventListener('click', addCustom);

  document.getElementById('resetBtn')?.addEventListener('click', () => {
    setTimeout(() => { items = []; nextId = 1; render(); }, 0);
  });

  const tray = document.getElementById('selectedTray');
  if (tray) {
    trayObserver = new MutationObserver(decorateSelectedTray);
    trayObserver.observe(tray, {childList:true, subtree:true});
  }

  render();
})();
