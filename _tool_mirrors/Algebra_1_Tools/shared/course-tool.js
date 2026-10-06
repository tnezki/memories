(function(){
  'use strict';
  const clamp=(n,min,max)=>Math.min(max,Math.max(min,n));
  const num=(v,fallback=0)=>{const n=Number(v);return Number.isFinite(n)?n:fallback};
  const escapeHtml=(s)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const decimals=(step)=>{const s=String(step);return s.includes('.')?Math.min(4,s.split('.')[1].length):0};
  function bindPrecisionControl(root,opts={}){
    if(typeof root==='string') root=document.querySelector(root);
    if(!root) return null;
    const range=root.querySelector('[data-role="range"]');
    const value=root.querySelector('[data-role="value"]');
    const minus=root.querySelector('[data-role="minus"]');
    const plus=root.querySelector('[data-role="plus"]');
    const stepSel=root.querySelector('[data-role="step"]');
    if(!range) return null;
    const min=num(opts.min, num(range.min,0));
    const max=num(opts.max, num(range.max,100));
    const suffix=opts.suffix||root.dataset.suffix||'';
    const emit=(source)=>{
      let v=clamp(num(range.value,min),min,max);
      range.value=String(v);
      if(value) value.textContent=v.toFixed(decimals(stepSel?num(stepSel.value,range.step||1):num(range.step,1)))+suffix;
      root.dispatchEvent(new CustomEvent('course-tool-change',{bubbles:true,detail:{value:v,source}}));
      if(typeof opts.onChange==='function') opts.onChange(v,source);
    };
    const step=()=>Math.max(.0001,num(stepSel?.value, num(range.step,1)));
    minus?.addEventListener('click',()=>{range.value=String(clamp(num(range.value)-step(),min,max));emit('minus')});
    plus?.addEventListener('click',()=>{range.value=String(clamp(num(range.value)+step(),min,max));emit('plus')});
    stepSel?.addEventListener('change',()=>emit('step'));
    range.addEventListener('input',()=>emit('range'));
    emit('init');
    return {get value(){return num(range.value)},set value(v){range.value=String(clamp(num(v,min),min,max));emit('set')}};
  }
  function bindMoveButtons(container,selector='[data-movable]'){
    container.addEventListener('click',e=>{
      const btn=e.target.closest('[data-move]'); if(!btn) return;
      const item=btn.closest(selector); if(!item) return;
      if(btn.dataset.move==='up' && item.previousElementSibling) item.parentNode.insertBefore(item,item.previousElementSibling);
      if(btn.dataset.move==='down' && item.nextElementSibling) item.parentNode.insertBefore(item.nextElementSibling,item);
      container.dispatchEvent(new CustomEvent('course-tool-reorder',{bubbles:true}));
    });
  }
  function uniqueBy(items,keyFn){const out=[],seen=new Set();for(const x of items||[]){const k=keyFn(x);if(seen.has(k))continue;seen.add(k);out.push(x)}return out}
  window.CourseToolUI={clamp,num,escapeHtml,bindPrecisionControl,bindMoveButtons,uniqueBy};
})();
