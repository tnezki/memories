(() => {
  const magnifier = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.8 15.8 21 21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  let catalogIndex = new Map();
  let specimenIndex = {};
  let observer = null;
  const esc = s => String(s ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

  async function loadData(){
    try{
      const [catalogRes,specRes]=await Promise.all([
        fetch('question_structure_catalog.json',{cache:'no-store'}),
        fetch('family_preview_specimens.json',{cache:'no-store'})
      ]);
      if(catalogRes.ok){
        const catalog=await catalogRes.json();
        const map=new Map();
        for(const course of (catalog.courses||[])) for(const topic of (course.topics||[])) for(const family of (topic.families||[])) map.set(family.id,{...family,course:course.name,topic:topic.label});
        catalogIndex=map;
      }
      if(specRes.ok){ const data=await specRes.json(); specimenIndex=data.specimens||{}; }
    }catch(error){ console.warn('Preview data unavailable',error); }
  }

  function svgFrame(inner,w=620,h=400){return `<svg class="preview-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Representative question figure">${inner}</svg>`;}
  function line(x1,y1,x2,y2,cls=''){return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;}
  function text(x,y,s,cls=''){return `<text x="${x}" y="${y}" class="${cls}">${esc(s)}</text>`;}

  function graphTransform(bounds,w=620,h=410,pad=42){
    const [xmin,xmax,ymin,ymax]=bounds; const sx=(w-2*pad)/(xmax-xmin), sy=(h-2*pad)/(ymax-ymin);
    return {w,h,pad,x:v=>pad+(v-xmin)*sx,y:v=>h-pad-(v-ymin)*sy,xmin,xmax,ymin,ymax};
  }
  function gridBase(bounds,w=620,h=410){
    const T=graphTransform(bounds,w,h), parts=[];
    for(let x=Math.ceil(T.xmin);x<=Math.floor(T.xmax);x++) parts.push(line(T.x(x),T.y(T.ymin),T.x(x),T.y(T.ymax),x===0?'axisline':'gridline'));
    for(let y=Math.ceil(T.ymin);y<=Math.floor(T.ymax);y++) parts.push(line(T.x(T.xmin),T.y(y),T.x(T.xmax),T.y(y),y===0?'axisline':'gridline'));
    return {T,parts};
  }
  function polygonMarkup(points,labels,T,cls='figureline'){
    const pts=points.map(([x,y])=>`${T.x(x)},${T.y(y)}`).join(' '); let out=`<polygon points="${pts}" class="${cls}"/>`;
    points.forEach(([x,y],i)=>{ if(labels?.[i]) out+=text(T.x(x)+7,T.y(y)-8,labels[i],'labeltxt'); }); return out;
  }
  function renderVisual(v){
    if(!v || v.type==='none') return '';
    if(v.type==='two_polygons_grid'){
      const {T,parts}=gridBase(v.bounds); parts.push(polygonMarkup(v.a,v.labels_a,T,'figureline')); parts.push(polygonMarkup(v.b,v.labels_b,T,'figureline2')); return svgFrame(parts.join(''));
    }
    if(v.type==='polygon_grid'){
      const {T,parts}=gridBase(v.bounds); parts.push(polygonMarkup(v.points,v.labels,T,'figureline')); return svgFrame(parts.join(''));
    }
    if(v.type==='points_grid'){
      const {T,parts}=gridBase(v.bounds); for(const [x,y,label] of v.points){parts.push(`<circle cx="${T.x(x)}" cy="${T.y(y)}" r="6" class="pointfill"/>`);parts.push(text(T.x(x)+8,T.y(y)-8,label,'labeltxt'));} return svgFrame(parts.join(''));
    }
    if(v.type==='line_graph'){
      const {T,parts}=gridBase(v.bounds); for(const L of v.lines||[]){const x1=T.xmin,x2=T.xmax,y1=L.m*x1+L.b,y2=L.m*x2+L.b;parts.push(line(T.x(x1),T.y(y1),T.x(x2),T.y(y2),'relationline')); if(L.label)parts.push(text(T.x(x2)-125,T.y(y2)-8,L.label,'smalltxt'));} for(const p of v.points||[])parts.push(`<circle cx="${T.x(p[0])}" cy="${T.y(p[1])}" r="5" class="pointfill"/>`);return svgFrame(parts.join(''));
    }
    if(v.type==='piecewise_graph'){
      const {T,parts}=gridBase(v.bounds); const pts=v.points.map(([x,y])=>`${T.x(x)},${T.y(y)}`).join(' ');parts.push(`<polyline points="${pts}" class="relationline"/>`); v.points.forEach(([x,y])=>parts.push(`<circle cx="${T.x(x)}" cy="${T.y(y)}" r="5" class="pointfill"/>`)); parts.push(text(500,388,v.x_label||'x','smalltxt'));parts.push(text(48,24,v.y_label||'y','smalltxt'));return svgFrame(parts.join(''));
    }
    if(v.type==='blank_axes'){
      const {parts}=gridBase(v.bounds);parts.push(text(500,388,v.x_label||'x','smalltxt'));parts.push(text(48,24,v.y_label||'y','smalltxt'));return svgFrame(parts.join(''));
    }
    if(v.type==='blank_number_line'){
      const min=v.min,max=v.max,w=620,y=100,left=45,right=575,step=(right-left)/(max-min); let g=line(left,y,right,y,'axisline');
      for(let n=min;n<=max;n++){const x=left+(n-min)*step;g+=line(x,y-9,x,y+9,'tickline'); if(n%2===0)g+=text(x-8,y+32,n,'smalltxt');} return svgFrame(g,620,150);
    }
    if(v.type==='table'){
      let html='<table class="preview-table"><tr>'+v.headers.map(x=>`<th>${esc(x)}</th>`).join('')+'</tr>'; for(const row of v.rows)html+='<tr>'+row.map((x,i)=>i===0?`<th>${esc(x)}</th>`:`<td>${esc(x)}</td>`).join('')+'</tr>'; return html+'</table>';
    }
    if(v.type==='scaled_triangles'){
      return svgFrame('<polygon points="80,315 180,115 280,315" class="figureline"/><polygon points="365,315 515,15 600,315" class="figureline"/>'+text(155,345,String(v.a_sides[0]),'labeltxt')+text(85,205,String(v.a_sides[1]),'labeltxt')+text(470,345,String(v.b_sides[0]),'labeltxt')+text(375,165,String(v.b_sides[1]),'labeltxt')+text(125,80,'Figure A','labeltxt')+text(445,28,'Figure B','labeltxt'),640,370);
    }
    if(v.type==='right_triangle'){
      return svgFrame('<polygon points="145,320 145,90 455,320" class="figureline"/><rect x="145" y="290" width="30" height="30" class="rightmark"/>'+text(105,210,String(v.legs[0]),'labeltxt')+text(285,350,String(v.legs[1]),'labeltxt')+text(320,190,String(v.hypotenuse),'labeltxt'),600,380);
    }
    if(v.type==='angle_named'){
      return svgFrame(line(300,250,130,90,'axisline')+line(300,250,500,105,'axisline')+text(110,82,v.left,'labeltxt')+text(288,278,v.vertex,'labeltxt')+text(510,100,v.right,'labeltxt'),620,330);
    }
    if(v.type==='linear_pair'){
      return svgFrame(line(90,235,540,235,'axisline')+line(315,235,405,70,'axisline')+'<path d="M257 235 A58 58 0 0 1 286 184" class="arc"/><path d="M346 184 A58 58 0 0 1 373 235" class="arc"/>'+text(205,185,String(v.known)+'°','labeltxt')+text(390,185,String(v.unknown),'labeltxt'),620,310);
    }
    if(v.type==='histogram'){
      const max=Math.max(...v.counts), baseY=315, left=90, bw=105, scale=210/max; let g=line(left,baseY,565,baseY,'axisline')+line(left,baseY,left,60,'axisline');
      v.counts.forEach((c,i)=>{const h=c*scale,x=left+i*bw+8;g+=`<rect x="${x}" y="${baseY-h}" width="${bw-16}" height="${h}" class="histbar"/>`+text(x+8,baseY+28,v.bins[i],'smalltxt')+text(x+35,baseY-h-8,String(c),'smalltxt');});return svgFrame(g,640,370);
    }
    if(v.type==='two_dotplots'){
      function plot(vals,y0,label){const min=Math.min(...v.a,...v.b),max=Math.max(...v.a,...v.b),left=90,right=550,step=(right-left)/(max-min);let g=text(25,y0+6,label,'labeltxt')+line(left,y0,right,y0,'axisline');const counts={};vals.forEach(n=>counts[n]=(counts[n]||0)+1);for(let n=min;n<=max;n++){const x=left+(n-min)*step;g+=line(x,y0-7,x,y0+7,'tickline')+text(x-5,y0+27,n,'smalltxt');for(let k=0;k<(counts[n]||0);k++)g+=`<circle cx="${x}" cy="${y0-20-k*23}" r="6" class="pointfill"/>`;}return g;}return svgFrame(plot(v.a,165,'A')+plot(v.b,350,'B'),640,400);
    }
    return '';
  }

  function responseHtml(kind){
    if(kind==='constructed_explanation') return '<div class="preview-response-lines"><span></span><span></span><span></span></div>';
    if(kind==='constructed_graph') return '<div class="preview-workspace preview-workspace-tall"></div>';
    if(kind==='constructed_work') return '<div class="preview-answer-line">Answer: ____________________________________</div><div class="preview-workspace"></div>';
    return '<div class="preview-answer-line">Answer: ____________________________________________</div>';
  }

  function ensureModal(){
    if(document.getElementById('questionPreviewOverlay')) return;
    const overlay=document.createElement('div'); overlay.id='questionPreviewOverlay'; overlay.className='preview-overlay'; overlay.setAttribute('aria-hidden','true');
    overlay.innerHTML=`<section class="preview-modal" role="dialog" aria-modal="true" aria-labelledby="questionPreviewTitle"><div class="preview-modal-head"><div><div class="preview-kicker" id="questionPreviewKicker">Question structure preview</div><h2 id="questionPreviewTitle">Preview</h2></div><button class="preview-close" type="button" aria-label="Close preview">×</button></div><div class="preview-modal-body"><p class="preview-note" id="questionPreviewNote">Curated representative problem — generated worksheets must preserve this family architecture while using new values/context.</p><div class="preview-paper" id="questionPreviewPaper"><div class="preview-problem"><strong>1.</strong><span id="questionPreviewPrompt"></span></div><div id="questionPreviewVisual" class="preview-visual"></div><div id="questionPreviewResponseBlock"></div></div><div class="preview-meta-grid"><div><b>Grade / topic</b><span id="questionPreviewScope"></span></div><div><b>Representation</b><span id="questionPreviewRepresentation"></span></div><div><b>Response</b><span id="questionPreviewResponse"></span></div></div></div></section>`;
    document.body.appendChild(overlay);
    overlay.querySelector('.preview-close').addEventListener('click',closePreview);
    overlay.addEventListener('click',e=>{if(e.target===overlay)closePreview();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&overlay.classList.contains('open'))closePreview();});
  }

  function openPreview(id){
    ensureModal(); const meta=catalogIndex.get(id)||{}, spec=specimenIndex[id];
    document.getElementById('questionPreviewTitle').textContent=meta.label||id;
    document.getElementById('questionPreviewKicker').textContent=meta.category||'Question structure preview';
    const paper=document.getElementById('questionPreviewPaper');
    if(!spec){
      document.getElementById('questionPreviewNote').textContent='This family does not yet have a curated preview specimen. It is intentionally not previewed with an invented generic question.';
      document.getElementById('questionPreviewPrompt').innerHTML='<b>Preview pending quality review.</b>';
      document.getElementById('questionPreviewVisual').innerHTML='';
      document.getElementById('questionPreviewVisual').hidden=true;
      document.getElementById('questionPreviewResponseBlock').innerHTML='';
      paper.classList.add('preview-pending');
    }else{
      paper.classList.remove('preview-pending');
      document.getElementById('questionPreviewNote').textContent='Curated representative problem — generated worksheets must preserve this family architecture while using new values/context.';
      document.getElementById('questionPreviewPrompt').innerHTML=spec.prompt_html;
      const visual=renderVisual(spec.visual), visualEl=document.getElementById('questionPreviewVisual'); visualEl.innerHTML=visual; visualEl.hidden=!visual;
      document.getElementById('questionPreviewResponseBlock').innerHTML=responseHtml(spec.response);
    }
    document.getElementById('questionPreviewScope').textContent=[meta.course,meta.topic].filter(Boolean).join(' · ')||'Selected math skill';
    document.getElementById('questionPreviewRepresentation').textContent=(meta.representations||['none']).join(', ');
    document.getElementById('questionPreviewResponse').textContent=(meta.response_modes||['constructed']).join(', ');
    const overlay=document.getElementById('questionPreviewOverlay'); overlay.classList.add('open'); overlay.setAttribute('aria-hidden','false'); overlay.querySelector('.preview-close').focus();
  }
  function closePreview(){const overlay=document.getElementById('questionPreviewOverlay');if(!overlay)return;overlay.classList.remove('open');overlay.setAttribute('aria-hidden','true');}

  function decorate(){
    document.querySelectorAll('.skill-row').forEach(row=>{
      if(row.querySelector('[data-preview-family]'))return; const id=row.dataset.familyId;if(!id)return; const qty=row.querySelector(':scope > .qty');if(!qty)return;
      const stack=document.createElement('div');stack.className='preview-control-stack';qty.replaceWith(stack);stack.appendChild(qty);
      const button=document.createElement('button');button.type='button';button.className='preview-btn';button.dataset.previewFamily=id;button.innerHTML=`${magnifier}<span>Preview</span>`;button.title='Preview this question family';button.setAttribute('aria-label','Preview this question family');stack.appendChild(button);
    });
  }
  document.addEventListener('click',e=>{const button=e.target.closest('[data-preview-family]');if(button)openPreview(button.dataset.previewFamily);});
  document.addEventListener('DOMContentLoaded',async()=>{await loadData();ensureModal();decorate();const mount=document.getElementById('familyMount');if(mount){observer=new MutationObserver(decorate);observer.observe(mount,{childList:true,subtree:true});}});
})();
