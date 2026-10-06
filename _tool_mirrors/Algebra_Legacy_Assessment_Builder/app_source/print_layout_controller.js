/* Shared Print/Layout Controller v4.3
   Canonical layout owner for print-first Curriculum Builder artifacts.
   Packing deliberately follows the already-working Practice Builder model:
   fixed printable body height + measured outer question heights + cumulative packing.
   One question contract: .plc-question > .plc-question-content + .plc-figure + .plc-workspace. */
(function(global){
  'use strict';

  const num=(v,f)=>Number.isFinite(Number(v))?Number(v):f;
  const clamp=(v,min,max,f)=>Math.max(min,Math.min(max,num(v,f)));

  class PrintLayoutController{
    constructor(config){
      this.c=config||{};
      this.fields=(this.c.fields||[]).map(f=>({min:0,max:100,step:1,default:0,unit:'px',...f}));
      this.fieldByKey=new Map(this.fields.map(f=>[f.key,f]));
      this.select=typeof this.c.entitySelect==='string'?document.querySelector(this.c.entitySelect):this.c.entitySelect;
      this.mainMount=typeof this.c.mainMount==='string'?document.querySelector(this.c.mainMount):this.c.mainMount;
      this.viewMount=typeof this.c.viewMount==='string'?document.querySelector(this.c.viewMount):this.c.viewMount;
      this.stage=typeof this.c.stage==='string'?document.querySelector(this.c.stage):this.c.stage;
      this.pageSelector=this.c.pageSelector;
      this.questionSelector=this.c.questionSelector;
      this.entityAttr=this.c.entityAttr;
      this.questionAttr=this.c.questionAttr;
      this.storageKey=String(this.c.storageKey||'shared-print-layout-v4');
      this.pagesPerEntity=Math.max(1,Number(this.c.pagesPerEntity||2));
      this.viewMode='work';
      this.dragging=false;
      this.state=this._normalize(this.c.initialState||{});
      if(!this.c.initialStateAuthoritative)this._restore();
      this._bindGlobalDrag();
      this.normalizeQuestionParts();
      this.refreshPages(false);
      this._renderMain();
      this._renderView();
      this.apply(false,{commit:false,source:'init'});
      window.addEventListener('resize',()=>{if(this.viewMode==='page')this._refreshPageView()});
    }

    _normalize(raw){
      raw=raw&&typeof raw==='object'?raw:{};
      const whole=raw.whole||raw.packet||{};
      const entities=raw.entities||raw.students||raw.versions||{};
      const out={whole:{},entities:{},questions:{},order:{}};
      this.fields.forEach(f=>out.whole[f.key]=this._field(f.key,whole[f.key]??f.default));
      Object.entries(entities).forEach(([k,v])=>{if(!v||typeof v!=='object')return;const o={};this.fields.forEach(f=>{if(Object.prototype.hasOwnProperty.call(v,f.key))o[f.key]=this._field(f.key,v[f.key])});out.entities[String(k)]=o});
      Object.entries(raw.questions||{}).forEach(([k,v])=>{if(!v||typeof v!=='object')return;const o={};this.fields.forEach(f=>{if(Object.prototype.hasOwnProperty.call(v,f.key))o[f.key]=this._field(f.key,v[f.key])});out.questions[String(k)]=o});
      Object.entries(raw.order||{}).forEach(([k,v])=>{if(Array.isArray(v))out.order[String(k)]=v.map(String)});
      return out;
    }
    _field(key,value){const f=this.fieldByKey.get(key);return f?clamp(value,f.min,f.max,f.default):num(value,0)}
    _qkey(e,q){return String(e)+'::'+String(q)}
    _restore(){try{const s=JSON.parse(localStorage.getItem(this.storageKey)||'null');if(s&&typeof s==='object')this.state=this._normalize(s)}catch(_e){}}
    _save(){try{localStorage.setItem(this.storageKey,JSON.stringify(this.state))}catch(_e){}}
    selectedEntity(){return this.select?String(this.select.value||''):String(this.c.getSelectedEntity?.()||'')}
    pages(){return [...document.querySelectorAll(this.pageSelector)]}
    pageBody(page){return page?.querySelector(this.c.pageBodySelector||'.plc-page-body')||page||null}
    pagesFor(entity,includeBlank=true){const e=String(entity);return this.pages().filter(p=>String(p.dataset[this.entityAttr]||'')===e&&(includeBlank||p.dataset.blankBack!=='1')).sort((a,b)=>Number(a.dataset.page||0)-Number(b.dataset.page||0))}
    questionsFor(entity){const e=String(entity);return this.pagesFor(e,false).flatMap(p=>[...p.querySelectorAll(this.questionSelector)])}
    questionElement(entity,qid){return this.questionsFor(entity).find(q=>String(q.dataset[this.questionAttr]||'')===String(qid))||null}
    questionHasFigure(entity,qid){const q=this.questionElement(entity,qid);return !!(q&&q.querySelector(':scope > .plc-figure:not(:empty)'))}
    effectiveEntity(entity){const o=this.state.entities[String(entity)]||{},r={};this.fields.forEach(f=>r[f.key]=this._field(f.key,o[f.key]??this.state.whole[f.key]));return r}
    effectiveQuestion(entity,qid){const base=this.effectiveEntity(entity),o=this.state.questions[this._qkey(entity,qid)]||{},r={};this.fields.forEach(f=>r[f.key]=this._field(f.key,o[f.key]??base[f.key]));return r}

    normalizeQuestionParts(){
      const legacy=this.c.legacyWorkspaceSelector||'.workspace,.workarea,.work-area,.work-space,.student-workspace,.answer-space,.response-space,.response-lines,[data-workspace],[class*="response-line"],[class*="work-line"],[class*="answer-line"]';
      this.pages().forEach(page=>page.querySelectorAll(this.questionSelector).forEach(q=>{
        q.classList.add('plc-question');
        let content=q.querySelector(':scope > .plc-question-content');
        if(!content){
          const candidate=q.querySelector(this.c.contentSelector||'.question-body,.frq-prompt');
          if(candidate){candidate.classList.add('plc-question-content');content=candidate}
        }
        let holder=q.querySelector(':scope > .plc-figure');
        if(!holder){holder=document.createElement('div');holder.className='plc-figure';const ws=q.querySelector(':scope > .plc-workspace');ws?q.insertBefore(holder,ws):q.appendChild(holder)}
        let workspace=q.querySelector(':scope > .plc-workspace');
        if(!workspace){workspace=document.createElement('div');workspace.className='plc-workspace';workspace.setAttribute('aria-hidden','true');q.appendChild(workspace)}
        if(!content||!holder)return;
        if(this.c.stripLegacyWorkspaces!==false)content.querySelectorAll(legacy).forEach(el=>el.remove());
        const wrappers=[...content.querySelectorAll('.graph-frame,.graph-block,.visual-block,.figure-block')].filter(el=>!el.parentElement?.closest('.graph-frame,.graph-block,.visual-block,.figure-block'));
        wrappers.forEach(el=>holder.appendChild(el));
        [...content.querySelectorAll('img,svg,canvas')].forEach(el=>{if(el.closest('.graph-frame,.graph-block,.visual-block,.figure-block'))return;holder.appendChild(el)});
        [...content.querySelectorAll('p')].forEach(p=>{if(!p.textContent.trim()&&!p.querySelector('img,svg,canvas'))p.remove()});
      }));
    }

    _applyQuestionVars(q,values){
      if(this.fieldByKey.has('workspace'))q.style.setProperty('--plc-workspace-height',this._field('workspace',values.workspace)+'px');
      if(this.fieldByKey.has('figure')){
        const scale=this._field('figure',values.figure),base=num(this.c.figureBasePx,320);
        q.style.setProperty('--plc-figure-scale',String(scale));
        q.style.setProperty('--plc-figure-width',Math.max(0,base*scale/100)+'px');
      }
    }
    apply(save=true,context={commit:true}){
      this.pages().forEach(page=>{
        const entity=String(page.dataset[this.entityAttr]||'');
        [...page.querySelectorAll(this.questionSelector)].forEach(q=>this._applyQuestionVars(q,this.effectiveQuestion(entity,String(q.dataset[this.questionAttr]||''))));
      });
      if(save)this._save();
      if(this.viewMode==='page')requestAnimationFrame(()=>this._refreshPageView());
      if(context.commit&&typeof this.c.onCommit==='function')this.c.onCommit(this.exportState(),context);
      if(typeof this.c.onAfterApply==='function')this.c.onAfterApply(this.exportState(),context);
    }

    _outerHeight(el){
      if(!el)return 0;
      const r=el.getBoundingClientRect(),cs=getComputedStyle(el);
      return r.height+(parseFloat(cs.marginTop)||0)+(parseFloat(cs.marginBottom)||0);
    }
    _visibleChildren(body){
      return [...(body?.children||[])].filter(el=>{const s=getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'});
    }
    _bodyUsed(body){return this._visibleChildren(body).reduce((sum,el)=>sum+this._outerHeight(el),0)}
    _bodyCapacity(body){return body?body.clientHeight:0}

    _withMeasurementMode(fn){
      if(this._measurementDepth){this._measurementDepth+=1;try{return fn()}finally{this._measurementDepth-=1}}
      this._measurementDepth=1;
      const hidden=this.c.hiddenClass||'screen-hidden',pages=this.pages();
      const pageState=pages.map(p=>({p,preview:p.classList.contains('plc-preview-hidden'),hidden:p.classList.contains(hidden),zoom:p.style.zoom,margin:p.style.margin}));
      const stageState=this.stage?{display:this.stage.style.display,flexWrap:this.stage.style.flexWrap,alignItems:this.stage.style.alignItems,justifyContent:this.stage.style.justifyContent,gap:this.stage.style.gap,minHeight:this.stage.style.minHeight,overflow:this.stage.style.overflow}:null;
      const pageMode=document.body.classList.contains('plc-page-mode');
      try{
        document.body.classList.remove('plc-page-mode');
        pageState.forEach(({p})=>{p.classList.remove('plc-preview-hidden',hidden);p.style.removeProperty('zoom');p.style.removeProperty('margin')});
        if(this.stage){['display','flex-wrap','align-items','justify-content','gap','min-height','overflow'].forEach(x=>this.stage.style.removeProperty(x))}
        return fn();
      }finally{
        pageState.forEach(({p,preview,hidden:h,zoom,margin})=>{p.classList.toggle('plc-preview-hidden',preview);p.classList.toggle(hidden,h);if(zoom)p.style.zoom=zoom;else p.style.removeProperty('zoom');if(margin)p.style.margin=margin;else p.style.removeProperty('margin')});
        if(this.stage&&stageState){this.stage.style.display=stageState.display;this.stage.style.flexWrap=stageState.flexWrap;this.stage.style.alignItems=stageState.alignItems;this.stage.style.justifyContent=stageState.justifyContent;this.stage.style.gap=stageState.gap;this.stage.style.minHeight=stageState.minHeight;this.stage.style.overflow=stageState.overflow}
        document.body.classList.toggle('plc-page-mode',pageMode);
        this._measurementDepth=0;
        if(this.viewMode==='page')requestAnimationFrame(()=>this._refreshPageView());
      }
    }
    _pageFitsRaw(page,tolerance=3){
      if(!page||page.dataset.blankBack==='1')return true;
      const body=this.pageBody(page);if(!body)return true;
      const capacity=this._bodyCapacity(body);if(capacity<=0)return true;
      return this._bodyUsed(body)<=capacity+tolerance;
    }
    pageFits(page,tolerance=3){return this._withMeasurementMode(()=>this._pageFitsRaw(page,tolerance))}
    _measureOverflowRaw(tolerance=3){
      const over=new Map();this.pages().forEach(page=>{if(page.dataset.blankBack==='1')return;const too=!this._pageFitsRaw(page,tolerance);page.classList.toggle(this.c.overfullClass||'overfull',too);if(too){const e=String(page.dataset[this.entityAttr]||'');if(!over.has(e))over.set(e,[]);over.get(e).push(this.c.pageLabel?this.c.pageLabel(page):(page.dataset.page||'?'))}});return over
    }
    measureOverflow(tolerance=3){return this._withMeasurementMode(()=>this._measureOverflowRaw(tolerance))}

    _questionMap(entity){return new Map(this.questionsFor(entity).map(q=>[String(q.dataset[this.questionAttr]||''),q]))}
    _orderedQuestionNodes(entity,ids){const map=this._questionMap(entity),order=(ids&&ids.length?ids:this._orderedIds(entity));return order.map(x=>map.get(String(x))).filter(Boolean)}

    reflowFixedEntity(entity,ids){return this._withMeasurementMode(()=>{
      const e=String(entity),pages=this.pagesFor(e,false);if(!pages.length)return {pages:0,overflow:[]};
      const bodies=pages.map(p=>this.pageBody(p)),ordered=this._orderedQuestionNodes(e,ids);
      bodies.forEach(body=>body&&body.querySelectorAll(this.questionSelector).forEach(q=>q.remove()));
      let pageIndex=0,body=bodies[0],capacity=this._bodyCapacity(body),used=this._bodyUsed(body);
      for(const q of ordered){
        this._applyQuestionVars(q,this.effectiveQuestion(e,String(q.dataset[this.questionAttr]||'')));
        body.appendChild(q);
        const h=this._outerHeight(q);
        if(used>0&&used+h>capacity&&pageIndex<pages.length-1){
          body.removeChild(q);pageIndex+=1;body=bodies[pageIndex];capacity=this._bodyCapacity(body);used=this._bodyUsed(body);body.appendChild(q);
        }
        used=this._bodyUsed(body);
      }
      this.refreshPages(false);return {pages:pages.length,overflow:this._measureOverflowRaw(3).get(e)||[]}
    })}

    reflowDynamicAll(options={}){return this._withMeasurementMode(()=>{
      if(!this.stage)return;
      const makePage=options.makePage||this.c.makePage,makeBlank=options.makeBlankPage||this.c.makeBlankPage,capture=options.captureContext||this.c.captureContext;
      if(typeof makePage!=='function')throw new Error('Dynamic pagination requires makePage(entity, context, pageNo).');
      const groups=new Map();
      this.pages().forEach(page=>{
        const e=String(page.dataset[this.entityAttr]||'');if(!e||page.dataset.blankBack==='1')return;
        let g=groups.get(e);if(!g){g={entity:e,context:typeof capture==='function'?capture(e,page):null,questions:[]};groups.set(e,g)}
        page.querySelectorAll(this.questionSelector).forEach(q=>g.questions.push(q));
      });
      const orderedGroups=[...groups.values()].sort((a,b)=>typeof this.c.entitySort==='function'?this.c.entitySort(a.entity,b.entity):String(a.entity).localeCompare(String(b.entity),undefined,{numeric:true}));
      this.stage.innerHTML='';
      orderedGroups.forEach(g=>{
        const seen=new Set();g.questions=g.questions.filter(q=>{const id=String(q.dataset[this.questionAttr]||'');if(seen.has(id))return false;seen.add(id);return true});
        const map=new Map(g.questions.map(q=>[String(q.dataset[this.questionAttr]||''),q])),order=this._orderedIdsFrom(map.keys(),g.entity),questions=order.map(id=>map.get(id)).filter(Boolean);
        let pageNo=1,page=makePage(g.entity,g.context,pageNo);this.stage.appendChild(page);
        let body=this.pageBody(page),capacity=this._bodyCapacity(body),used=this._bodyUsed(body);
        for(const q of questions){
          this._applyQuestionVars(q,this.effectiveQuestion(g.entity,String(q.dataset[this.questionAttr]||'')));
          body.appendChild(q);const h=this._outerHeight(q);
          if(used>0&&used+h>capacity){
            body.removeChild(q);pageNo+=1;page=makePage(g.entity,g.context,pageNo);this.stage.appendChild(page);body=this.pageBody(page);capacity=this._bodyCapacity(body);used=this._bodyUsed(body);body.appendChild(q);
          }
          used=this._bodyUsed(body);page.classList.toggle(this.c.overfullClass||'overfull',used>capacity+3);
        }
        if(options.ensureEven!==false&&pageNo%2===1&&typeof makeBlank==='function'){pageNo+=1;this.stage.appendChild(makeBlank(g.entity,g.context,pageNo))}
      });
      this.normalizeQuestionParts();this.refreshPages(false);this.apply(false,{commit:false,source:'reflow-dynamic'});return this._measureOverflowRaw(3)
    })}
    _orderedIdsFrom(iterable,entity){const current=[...iterable].map(String),saved=this.state.order[String(entity)]||[],out=saved.filter(x=>current.includes(x));current.forEach(x=>{if(!out.includes(x))out.push(x)});return out}

    _change(level,entity,qid,key,value,commit){
      const cleanEmpty=obj=>!!(obj&&Object.keys(obj).length===0);
      if(level==='whole'){
        this.state.whole[key]=this._field(key,value);
        if(this.c.scopeOwnsDescendants){Object.keys(this.state.entities).forEach(e=>{const o=this.state.entities[e];if(o&&Object.prototype.hasOwnProperty.call(o,key))delete o[key];if(cleanEmpty(o))delete this.state.entities[e]});Object.keys(this.state.questions).forEach(q=>{const o=this.state.questions[q];if(o&&Object.prototype.hasOwnProperty.call(o,key))delete o[key];if(cleanEmpty(o))delete this.state.questions[q]})}
      }else if(level==='entity'){
        const o=this.state.entities[entity]||(this.state.entities[entity]={});o[key]=this._field(key,value);
        if(this.c.scopeOwnsDescendants){const prefix=String(entity)+'::';Object.keys(this.state.questions).filter(q=>q.startsWith(prefix)).forEach(q=>{const qo=this.state.questions[q];if(qo&&Object.prototype.hasOwnProperty.call(qo,key))delete qo[key];if(cleanEmpty(qo))delete this.state.questions[q]})}
      }else{const k=this._qkey(entity,qid),o=this.state.questions[k]||(this.state.questions[k]={});o[key]=this._field(key,value)}
      this.apply(commit,{commit,level,entity,question:qid,field:key});
      if(typeof this.c.onChange==='function')this.c.onChange(this.exportState(),{commit,level,entity,question:qid,field:key});
    }

    _fieldControl(field,value,onPreview,onCommit){
      const box=document.createElement('div');box.className='plc-field';const head=document.createElement('div');head.className='plc-field-head';const label=document.createElement('span');label.textContent=field.label;
      const vw=document.createElement('span');vw.className='plc-value-wrap';const n=document.createElement('input');n.type='number';n.className='plc-number';n.min=field.min;n.max=field.max;n.step=field.step;n.value=String(value);const u=document.createElement('span');u.className='plc-unit';u.textContent=field.unit||'';vw.append(n,u);head.append(label,vw);
      const adj=document.createElement('div');adj.className='plc-adjust';const minus=document.createElement('button');minus.type='button';minus.textContent='−';const range=document.createElement('input');range.type='range';range.className='plc-range';range.min=field.min;range.max=field.max;range.step=field.step;range.value=String(value);const plus=document.createElement('button');plus.type='button';plus.textContent='+';adj.append(minus,range,plus);box.append(head,adj);
      const sync=(v,commit)=>{const x=this._field(field.key,v);range.value=String(x);n.value=String(x);(commit?onCommit:onPreview)(x)};
      range.addEventListener('input',e=>sync(e.target.value,false));range.addEventListener('change',e=>sync(e.target.value,true));n.addEventListener('change',e=>sync(e.target.value,true));minus.addEventListener('click',()=>sync(Number(range.value)-field.step,true));plus.addEventListener('click',()=>sync(Number(range.value)+field.step,true));return box;
    }
    _renderMain(){if(!this.mainMount)return;this.mainMount.innerHTML='';const entity=this.selectedEntity(),vals=entity?this.effectiveEntity(entity):this.state.whole;const h=document.createElement('h2');h.className='plc-scope-title';h.textContent=entity?(this.c.entityLayoutTitle||'Selected Layout'):(this.c.wholeLayoutTitle||'Whole Artifact Layout');this.mainMount.append(h);this.fields.forEach(f=>this.mainMount.append(this._fieldControl(f,vals[f.key],v=>this._change(entity?'entity':'whole',entity,'',f.key,v,false),v=>this._change(entity?'entity':'whole',entity,'',f.key,v,true))));const reset=document.createElement('button');reset.type='button';reset.className='plc-reset';reset.textContent=entity?(this.c.entityResetLabel||'Use Whole Artifact Layout'):(this.c.wholeResetLabel||'Reset Layout');reset.onclick=()=>this.resetScope();this.mainMount.append(reset)}
    mountQuestionControls(container,entity,qid,fieldKeys,options={}){if(!container)return;container.innerHTML='';container.classList.add('plc-question-layout');const vals=this.effectiveQuestion(entity,qid);(fieldKeys||[]).forEach(key=>{const f=this.fieldByKey.get(key);if(!f)return;container.append(this._fieldControl(f,vals[key],v=>this._change('question',String(entity),String(qid),key,v,false),v=>this._change('question',String(entity),String(qid),key,v,true)))});if(options.reorder!==false){const row=document.createElement('div');row.className='plc-order-row';const ids=this._orderedIds(String(entity)),i=ids.indexOf(String(qid));const up=document.createElement('button');up.type='button';up.className='plc-order-btn';up.textContent='↑';up.title='Move question up';up.setAttribute('aria-label','Move question up');up.disabled=i<=0;const down=document.createElement('button');down.type='button';down.className='plc-order-btn';down.textContent='↓';down.title='Move question down';down.setAttribute('aria-label','Move question down');down.disabled=i<0||i>=ids.length-1;up.onclick=()=>this.moveQuestion(entity,qid,-1);down.onclick=()=>this.moveQuestion(entity,qid,1);row.append(up,down);container.append(row)}const reset=document.createElement('button');reset.type='button';reset.className='plc-reset';reset.textContent=options.resetLabel||'Use Selected Layout';reset.onclick=()=>this.resetQuestion(entity,qid);container.append(reset)}
    moveQuestion(entity,qid,delta){const e=String(entity),ids=this._orderedIds(e),i=ids.indexOf(String(qid));if(i<0)return;const j=Math.max(0,Math.min(ids.length-1,i+delta));if(i===j)return;[ids[i],ids[j]]=[ids[j],ids[i]];this.state.order[e]=ids;this._save();if(typeof this.c.onReorder==='function')this.c.onReorder(e,ids.slice());if(typeof this.c.onCommit==='function')this.c.onCommit(this.exportState(),{commit:true,level:'order',entity:e})}
    _orderedIds(entity){return this._orderedIdsFrom(this.questionsFor(entity).map(q=>String(q.dataset[this.questionAttr]||'')),entity)}
    orderedIds(entity){return this._orderedIds(entity).slice()}
    resetQuestion(entity,qid){delete this.state.questions[this._qkey(entity,qid)];this.apply(true,{commit:true,level:'question-reset',entity:String(entity),question:String(qid)});if(typeof this.c.onChange==='function')this.c.onChange(this.exportState(),{commit:true,level:'question-reset',entity:String(entity),question:String(qid)})}
    resetScope(){const e=this.selectedEntity();if(e){delete this.state.entities[e];Object.keys(this.state.questions).filter(k=>k.startsWith(e+'::')).forEach(k=>delete this.state.questions[k])}else this.state=this._normalize(this.c.initialState||{});this._renderMain();this.apply(true,{commit:true,level:e?'entity-reset':'whole-reset',entity:e});if(typeof this.c.onChange==='function')this.c.onChange(this.exportState(),{commit:true,level:e?'entity-reset':'whole-reset',entity:e})}
    setSelectedEntity(){this._renderMain();if(this.viewMode==='page')this._refreshPageView()}
    refreshPages(refreshView=true){this.pages().forEach(p=>p.classList.add('plc-page'));if(refreshView&&this.viewMode==='page')this._refreshPageView()}
    refreshView(){if(this.viewMode==='page')this._refreshPageView()}
    exportState(){return JSON.parse(JSON.stringify(this.state))}

    _renderView(){if(!this.viewMount)return;this.viewMount.innerHTML='';const row=document.createElement('div');row.className='plc-view-toggle';for(const [mode,label] of [['work','Work View'],['page','2-Page View']]){const b=document.createElement('button');b.type='button';b.dataset.mode=mode;b.textContent=label;b.onclick=()=>this.setViewMode(mode);row.append(b)}this.viewMount.append(row);const note=document.createElement('div');note.className='plc-page-view-note';note.textContent='2-Page View shows actual printed page geometry side-by-side.';this.viewMount.append(note);this._syncView()}
    _syncView(){if(!this.viewMount)return;this.viewMount.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===this.viewMode))}
    setViewMode(mode){this.viewMode=mode==='page'?'page':'work';this._syncView();this.viewMode==='page'?this._refreshPageView():this._restoreWorkView()}
    _restoreWorkView(){document.body.classList.remove('plc-page-mode');this.pages().forEach(p=>{p.classList.remove('plc-preview-hidden');p.style.removeProperty('zoom');p.style.removeProperty('margin')});if(this.stage)['display','flex-wrap','align-items','justify-content','gap','min-height','overflow'].forEach(x=>this.stage.style.removeProperty(x))}
    _refreshPageView(){if(!this.stage)return;document.body.classList.add('plc-page-mode');const pages=this.pages(),selected=this.selectedEntity();let e=selected;if(!e){const f=pages.find(p=>!p.classList.contains(this.c.hiddenClass||'screen-hidden'))||pages[0];e=f?String(f.dataset[this.entityAttr]||''):''}const targets=pages.filter(p=>String(p.dataset[this.entityAttr]||'')===e).slice(0,2);pages.forEach(p=>p.classList.toggle('plc-preview-hidden',!targets.includes(p)));targets.forEach(p=>{p.style.zoom='1';p.style.margin='0'});this.stage.style.display='flex';this.stage.style.flexWrap='nowrap';this.stage.style.alignItems='flex-start';this.stage.style.justifyContent='center';this.stage.style.gap='12px';this.stage.style.overflow='auto';if(!targets.length)return;const sidebar=num(this.c.sidebarWidth,310),aw=Math.max(320,window.innerWidth-sidebar-42),ah=Math.max(320,window.innerHeight-42),pw=targets[0].offsetWidth||816,ph=targets[0].offsetHeight||1056,gap=12*(targets.length-1),scale=Math.max(.2,Math.min(1,(aw-gap)/(pw*targets.length),ah/ph));targets.forEach(p=>p.style.zoom=String(scale));this.stage.style.minHeight=Math.ceil(ph*scale+32)+'px'}
    _bindGlobalDrag(){document.addEventListener('pointerdown',e=>{if(e.target instanceof HTMLInputElement&&e.target.type==='range'&&(this.mainMount?.contains(e.target)||e.target.closest('.plc-question-layout')))this.dragging=true});document.addEventListener('pointerup',()=>{this.dragging=false});document.addEventListener('pointercancel',()=>{this.dragging=false})}
  }
  global.PrintLayoutController=PrintLayoutController;
})(window);
