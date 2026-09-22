(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const num=(v,d)=>Number.isFinite(Number(v))?Number(v):d;
  const clone=el=>el.cloneNode(true);
  const state={work:{},visual:1};

  function makePage(stack,n,title){
    const p=document.createElement('section');p.className='worksheet-page';p.dataset.page=String(n);
    const inner=document.createElement('div');inner.className='page-inner';p.appendChild(inner);
    if(n>1){const c=document.createElement('div');c.className='page-continuation';c.textContent=title+' · continued';inner.appendChild(c)}
    stack.appendChild(p);return {page:p,inner};
  }
  function overflow(inner){return inner.scrollHeight>inner.clientHeight+2 || inner.scrollWidth>inner.clientWidth+2}
  function blocks(source){return [...source.children].filter(x=>x.classList.contains('problem')||x.classList.contains('section-divider'))}
  function problemIds(source){return [...source.querySelectorAll(':scope > .problem')].map(x=>x.dataset.problem)}
  function selected(){return $('runtimeProblem')?.value||'all'}
  function allScale(){return num($('runtimeAll')?.value,100)/100}
  function selectedScale(){return num($('runtimeOne')?.value,100)/100}
  function visualScale(){return num($('runtimeVisual')?.value,100)/100}

  function populate(source){
    const s=$('runtimeProblem'); if(!s)return;
    s.innerHTML='<option value="all">All</option>';
    problemIds(source).forEach(id=>{
      const o=document.createElement('option');o.value=id;o.textContent=id;s.appendChild(o);
      if(state.work[id]==null)state.work[id]=1;
    });
  }

  // Workspace sizes are absolute per-problem values, not multipliers.
  // "All workspaces" writes the same value to every problem. Once a single
  // problem is selected, "Workspace" changes only that problem.
  function effective(id){return state.work[id]??1}

  function syncSelection(){
    const id=selected(),one=$('runtimeOne');
    if(!one)return;
    if(id==='all'){
      one.disabled=true;
      one.value='100';
    }else{
      one.disabled=false;
      one.value=String(Math.round((state.work[id]??1)*100));
    }
    updateOutputs();
  }

  function applyAllWorkspace(){
    const v=allScale();
    Object.keys(state.work).forEach(k=>state.work[k]=v);
    if(selected()!=='all')syncSelection();
  }

  function applySelectedWorkspace(){
    const id=selected();
    if(id==='all')return;
    state.work[id]=selectedScale();
  }

  function updateOutputs(){
    if($('runtimeAllOut'))$('runtimeAllOut').textContent=$('runtimeAll').value+'%';
    if($('runtimeOneOut'))$('runtimeOneOut').textContent=selected()==='all'?'—':$('runtimeOne').value+'%';
    if($('runtimeVisualOut'))$('runtimeVisualOut').textContent=$('runtimeVisual').value+'%';
  }

  function renderClone(src){
    const b=clone(src);
    if(b.classList.contains('problem')){
      const baseWs=parseFloat(b.dataset.baseWorkspace||'.62');
      const baseGraph=parseFloat(b.dataset.baseGraph||'3.25');
      b.style.setProperty('--workspace-height',(baseWs*effective(src.dataset.problem))+'in');
      b.style.setProperty('--problem-workspace-height',(baseWs*effective(src.dataset.problem))+'in');
      b.style.setProperty('--problem-graph-width',(baseGraph*visualScale())+'in');
    }
    return b;
  }

  function repaginate(){
    const source=$('runtimeFlowSource'),stack=$('runtimePageStack');if(!source||!stack)return;
    stack.innerHTML='';let n=1;const title=source.dataset.title||document.title;
    let pg=makePage(stack,n++,title),inner=pg.inner;
    const header=source.querySelector(':scope > .runtime-flow-header');
    if(header)inner.appendChild(clone(header));
    let holder=document.createElement('div');holder.className='flow-list';inner.appendChild(holder);
    for(const src of blocks(source)){
      let b=renderClone(src);holder.appendChild(b);
      if(overflow(inner)){
        holder.removeChild(b);
        pg=makePage(stack,n++,title);inner=pg.inner;holder=document.createElement('div');holder.className='flow-list';inner.appendChild(holder);holder.appendChild(b);
        if(overflow(inner)&&b.classList.contains('problem')) b.classList.add('oversize-problem');
      }
    }
  }

  function reset(){
    if($('runtimeAll'))$('runtimeAll').value='100';
    if($('runtimeOne'))$('runtimeOne').value='100';
    if($('runtimeVisual'))$('runtimeVisual').value='100';
    if($('runtimeProblem'))$('runtimeProblem').value='all';
    Object.keys(state.work).forEach(k=>state.work[k]=1);
    state.visual=1;
    syncSelection();
    updateOutputs();
    repaginate();
  }

  function bind(){
    const source=$('runtimeFlowSource');if(!source)return;populate(source);
    $('runtimeAll')?.addEventListener('input',()=>{applyAllWorkspace();updateOutputs();repaginate()});
    $('runtimeProblem')?.addEventListener('change',()=>{syncSelection();repaginate()});
    $('runtimeOne')?.addEventListener('input',()=>{applySelectedWorkspace();updateOutputs();repaginate()});
    $('runtimeVisual')?.addEventListener('input',()=>{state.visual=visualScale();updateOutputs();repaginate()});
    $('runtimeReset')?.addEventListener('click',reset);
    $('runtimePrint')?.addEventListener('click',()=>window.print());
    syncSelection();
    updateOutputs();
    repaginate();
    setTimeout(repaginate,120);
  }

  async function init(){
    if(window.MathJax?.startup?.promise){
      try{await window.MathJax.startup.promise;}catch(e){console.warn('MathJax startup warning',e)}
    }
    bind();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
