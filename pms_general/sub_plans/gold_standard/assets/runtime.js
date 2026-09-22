(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const num=(v,d)=>Number.isFinite(Number(v))?Number(v):d;
  const clone=el=>el.cloneNode(true);
  const state={work:{},visual:{}};

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
  function sliderValue(id,d=100){return num($(id)?.value,d)/100}

  function populate(source){
    const s=$('runtimeProblem'); if(!s)return;
    s.innerHTML='<option value="all">All</option>';
    problemIds(source).forEach(id=>{
      const o=document.createElement('option');o.value=id;o.textContent=id;s.appendChild(o);
      if(state.work[id]==null)state.work[id]=1;
      if(state.visual[id]==null)state.visual[id]=1;
    });
  }

  function setSelectedControlsEnabled(enabled){
    if($('runtimeOne'))$('runtimeOne').disabled=!enabled;
    if($('runtimeVisual'))$('runtimeVisual').disabled=!enabled;
  }

  function syncSelection(){
    const id=selected();
    const one=$('runtimeOne'), vis=$('runtimeVisual');
    if(id==='all'){
      if(one)one.value='100';
      if(vis)vis.value='100';
      setSelectedControlsEnabled(false);
    }else{
      if(one)one.value=String(Math.round((state.work[id]??1)*100));
      if(vis)vis.value=String(Math.round((state.visual[id]??1)*100));
      setSelectedControlsEnabled(true);
    }
    updateOutputs();
  }

  function setAllWorkspaces(){
    const v=sliderValue('runtimeAll');
    Object.keys(state.work).forEach(k=>state.work[k]=v);
    const id=selected();
    if(id!=='all'&&$('runtimeOne'))$('runtimeOne').value=String(Math.round(v*100));
  }

  function applySelectedWorkspace(){
    const id=selected();
    if(id==='all')return;
    state.work[id]=sliderValue('runtimeOne');
  }

  function applySelectedVisual(){
    const id=selected();
    if(id==='all')return;
    state.visual[id]=sliderValue('runtimeVisual');
  }

  function updateOutputs(){
    if($('runtimeAllOut'))$('runtimeAllOut').textContent=$('runtimeAll').value+'%';
    if($('runtimeOneOut'))$('runtimeOneOut').textContent=$('runtimeOne').value+'%';
    if($('runtimeVisualOut'))$('runtimeVisualOut').textContent=$('runtimeVisual').value+'%';
  }

  function renderClone(src){
    const b=clone(src);
    if(b.classList.contains('problem')){
      const id=src.dataset.problem;
      const baseWs=parseFloat(b.dataset.baseWorkspace||'.62');
      const baseGraph=parseFloat(b.dataset.baseGraph||'3.25');
      const wsScale=state.work[id]??1;
      const graphScale=state.visual[id]??1;
      b.style.setProperty('--workspace-height',(baseWs*wsScale)+'in');
      b.style.setProperty('--problem-workspace-height',(baseWs*wsScale)+'in');
      b.style.setProperty('--problem-graph-width',(baseGraph*graphScale)+'in');
      if(id===selected())b.classList.add('runtime-selected-problem');
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
        if(overflow(inner)&&b.classList.contains('problem'))b.classList.add('oversize-problem');
      }
    }
  }

  function reset(){
    if($('runtimeAll'))$('runtimeAll').value='100';
    if($('runtimeOne'))$('runtimeOne').value='100';
    if($('runtimeVisual'))$('runtimeVisual').value='100';
    if($('runtimeProblem'))$('runtimeProblem').value='all';
    Object.keys(state.work).forEach(k=>state.work[k]=1);
    Object.keys(state.visual).forEach(k=>state.visual[k]=1);
    syncSelection();updateOutputs();repaginate();
  }

  function bind(){
    const source=$('runtimeFlowSource');if(!source)return;populate(source);syncSelection();
    $('runtimeAll')?.addEventListener('input',()=>{setAllWorkspaces();updateOutputs();repaginate()});
    $('runtimeProblem')?.addEventListener('change',()=>{syncSelection();repaginate()});
    $('runtimeOne')?.addEventListener('input',()=>{applySelectedWorkspace();updateOutputs();repaginate()});
    $('runtimeVisual')?.addEventListener('input',()=>{applySelectedVisual();updateOutputs();repaginate()});
    $('runtimeReset')?.addEventListener('click',reset);
    $('runtimePrint')?.addEventListener('click',()=>window.print());
    updateOutputs();repaginate();setTimeout(repaginate,120);
  }

  async function init(){
    if(window.MathJax?.startup?.promise){
      try{await window.MathJax.startup.promise;}catch(e){console.warn('MathJax startup warning',e)}
    }
    bind();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
