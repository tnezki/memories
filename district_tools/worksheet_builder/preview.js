(() => {
  const magnifier = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"></circle><path d="M16 16l5 5"></path></svg>';
  let catalogIndex = new Map();
  let observer = null;

  function esc(value){return String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));}
  function text(meta){return [meta?.label,meta?.summary,meta?.visual,...(meta?.representations||[])].filter(Boolean).join(" ").toLowerCase();}
  function has(meta,...terms){const t=text(meta);return terms.every(term=>t.includes(term));}

  async function loadCatalog(){
    try{
      const r=await fetch("question_structure_catalog.json",{cache:"no-store"});
      if(!r.ok)return;
      const catalog=await r.json();
      const map=new Map();
      for(const course of (catalog.courses||[]))for(const topic of (course.topics||[]))for(const family of (topic.families||[]))map.set(family.id,{...family,course:course.name,topic:topic.label});
      catalogIndex=map;
    }catch(error){console.warn("Preview catalog unavailable",error);}
  }

  function svgFrame(inner,w=520,h=220){return `<svg class="preview-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Representative question figure">${inner}</svg>`;}
  function line(x1,y1,x2,y2,extra=""){return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ${extra}/>`;}
  function txt(x,y,s,extra=""){return `<text x="${x}" y="${y}" ${extra}>${esc(s)}</text>`;}

  function coordinateGrid(){
    let g='';for(let i=0;i<=10;i++){const p=40+i*40;g+=line(p,20,p,420,'class="gridline"')+line(40,p-20,440,p-20,'class="gridline"');}
    g+=line(240,20,240,420,'class="axisline"')+line(40,220,440,220,'class="axisline"');
    g+='<polyline points="160,180 280,140 320,180 160,180" class="figureline"/>';
    g+=txt(150,172,'A')+txt(282,132,'B')+txt(324,174,'C');
    return svgFrame(g,480,440);
  }
  function numberLine(){
    let g=line(45,105,475,105,'class="axisline"');for(let i=0;i<=10;i++){const x=45+i*43;g+=line(x,96,x,114,'class="tickline"')+txt(x-6,135,String(i*10),'class="smalltxt"');}
    g+='<circle cx="337" cy="105" r="7" class="pointfill"/>'+txt(327,82,'68','class="labeltxt"');return svgFrame(g,520,165);
  }
  function doubleNumberLine(){
    let g=line(50,75,470,75,'class="axisline"')+line(50,155,470,155,'class="axisline"');
    [50,155,260,365,470].forEach((x,i)=>{g+=line(x,66,x,84,'class="tickline"')+line(x,146,x,164,'class="tickline"')+txt(x-5,55,String(i*3),'class="smalltxt"')+txt(x-8,190,i===3?'?':String(i*8),'class="smalltxt"');});
    g+=txt(10,80,'cups','class="labeltxt"')+txt(4,160,'ounces','class="labeltxt"');return svgFrame(g,520,210);
  }
  function fractionBars(){
    let g='';for(let i=0;i<4;i++){g+=`<rect x="${70+i*90}" y="45" width="90" height="55" class="cell ${i<3?'shade':''}"/>`;}
    for(let i=0;i<8;i++){g+=`<rect x="${70+i*45}" y="125" width="45" height="55" class="cell ${i<6?'shade2':''}"/>`;}
    g+=txt(28,78,'3/4','class="labeltxt"')+txt(28,158,'6/8','class="labeltxt"');return svgFrame(g,500,215);
  }
  function baseTen(){
    let g='';
    for(let h=0;h<2;h++){g+=`<rect x="${45+h*120}" y="35" width="92" height="92" class="hundred"/>`;for(let i=1;i<10;i++){g+=line(45+h*120+i*9.2,35,45+h*120+i*9.2,127,'class="thin"')+line(45+h*120,35+i*9.2,137+h*120,35+i*9.2,'class="thin"');}}
    for(let t=0;t<3;t++){g+=`<rect x="${315+t*28}" y="35" width="16" height="92" class="ten"/>`;for(let i=1;i<10;i++)g+=line(315+t*28,35+i*9.2,331+t*28,35+i*9.2,'class="thin"');}
    for(let i=0;i<8;i++){const y=155+Math.floor(i/4)*30;g+=`<rect x="${290+(i%4)*32}" y="${y}" width="18" height="18" class="one"/>`;}
    return svgFrame(g,470,235);
  }
  function stripModel(){return `<div class="preview-strip"><div class="strip-whole">84</div><div class="strip-parts"><span>28</span><span>?</span><span>?</span></div></div>`;}
  function shapeArray(){let g='';for(let r=0;r<3;r++)for(let c=0;c<8;c++)g+=`<circle cx="${72+c*48}" cy="${55+r*48}" r="15" class="shape ${c<5?'shade':''}"/>`;return svgFrame(g,460,190);}
  function scaleFigures(){return svgFrame('<polygon points="70,170 130,55 190,170" class="figureline"/><polygon points="285,170 385,25 470,170" class="figureline"/>'+txt(98,190,'6')+txt(63,112,'9')+txt(365,190,'10')+txt(300,102,'15')+txt(86,35,'Figure 1','class="labeltxt"')+txt(345,18,'Figure 2','class="labeltxt"'),520,215);}
  function polygon(){return svgFrame('<polygon points="100,55 310,75 405,175 190,190 80,130" class="figureline"/>'+txt(185,58,'8')+txt(350,112,'5')+txt(282,205,'10')+txt(72,100,'4'),500,235);}
  function angle(){return svgFrame(line(250,170,250,35,'class="axisline"')+line(250,170,410,105,'class="axisline"')+'<path d="M250 112 A58 58 0 0 1 304 148" class="arc"/>'+txt(290,120,'?°','class="labeltxt"'),500,215);}
  function dotPlot(){let g=line(55,150,465,150,'class="axisline"');for(let i=0;i<7;i++){const x=75+i*60;g+=line(x,143,x,158,'class="tickline"')+txt(x-5,180,String(i+2),'class="smalltxt"');const n=[1,3,2,4,2,1,2][i];for(let d=0;d<n;d++)g+=`<circle cx="${x}" cy="${130-d*25}" r="7" class="pointfill"/>`;};return svgFrame(g,520,205);}
  function probabilityModel(){let g='';for(let r=0;r<2;r++)for(let c=0;c<5;c++)g+=`<rect x="${75+c*70}" y="${45+r*70}" width="48" height="48" class="cell ${(r*5+c)<4?'shade':''}"/>`;return svgFrame(g,500,200);}
  function clock(){return svgFrame('<circle cx="250" cy="110" r="82" class="figureline"/>'+line(250,110,250,52,'class="axisline"')+line(250,110,302,136,'class="axisline"')+txt(242,22,'12','class="smalltxt"')+txt(330,116,'3','class="smalltxt"')+txt(246,210,'6','class="smalltxt"')+txt(157,116,'9','class="smalltxt"'),500,230);}
  function ruler(){let g=line(55,85,465,85,'class="axisline"');for(let i=0;i<=16;i++){const x=55+i*25.6;const h=i%4===0?32:i%2===0?22:14;g+=line(x,85,x,85-h,'class="tickline"');if(i%4===0)g+=txt(x-5,112,String(i/4),'class="smalltxt"');}return svgFrame(g,520,135);}
  function hundredChart(){let cells='';for(let r=0;r<10;r++)for(let c=0;c<10;c++){const n=r*10+c+1;cells+=`<span class="hundred-cell ${n%6===0?'mark':''}">${n}</span>`;}return `<div class="hundred-chart">${cells}</div>`;}
  function table(kind){
    if(kind==='budget')return '<table class="preview-table"><tr><th>Category</th><th>Amount</th></tr><tr><td>Rent</td><td>$1,450</td></tr><tr><td>Food</td><td>$900</td></tr><tr><td>Savings</td><td>$1,250</td></tr><tr><td>Other</td><td>?</td></tr></table>';
    if(kind==='ratio')return '<table class="preview-table"><tr><th>Boxes</th><th>2</th><th>5</th><th>8</th></tr><tr><th>Markers</th><td>6</td><td>15</td><td>?</td></tr></table>';
    if(kind==='frequency')return '<table class="preview-table"><tr><th>Value</th><th>2</th><th>3</th><th>4</th><th>5</th></tr><tr><th>Frequency</th><td>1</td><td>3</td><td>2</td><td>4</td></tr></table>';
    return '<table class="preview-table"><tr><th>x</th><th>1</th><th>2</th><th>3</th></tr><tr><th>y</th><td>4</td><td>8</td><td>12</td></tr></table>';
  }
  function algorithm(kind){
    if(kind==='division')return '<pre class="preview-algorithm">      14.4\n   ──────\n4 ) 57.6\n    4\n    ──\n    17\n    16\n    ──\n     16\n     16\n     ──\n      0</pre>';
    return '<pre class="preview-algorithm">    7.2\n  × 0.6\n  ─────\n    4.32</pre>';
  }

  function visualFor(meta){
    const t=text(meta);
    if(t.includes('coordinate')||t.includes('dilation')||t.includes('cartesian'))return coordinateGrid();
    if(t.includes('double number line'))return doubleNumberLine();
    if(t.includes('number line'))return numberLine();
    if(t.includes('base-ten')||t.includes('base ten'))return baseTen();
    if((t.includes('fraction')&&(t.includes('model')||t.includes('area')||t.includes('equivalent')||t.includes('shaded'))) || t.includes('pattern block') || t.includes('fraction bar') || t.includes('rectangle model'))return fractionBars();
    if(t.includes('strip')||t.includes('tape'))return stripModel();
    if(t.includes('shape array')||t.includes('count model'))return shapeArray();
    if(t.includes('scaled figure')||t.includes('scale factor'))return scaleFigures();
    if(t.includes('perimeter')||t.includes('polygon'))return polygon();
    if(t.includes('angle'))return angle();
    if(t.includes('dot plot')||t.includes('line plot'))return dotPlot();
    if(t.includes('probability'))return probabilityModel();
    if(t.includes('clock')||t.includes('time'))return clock();
    if(t.includes('ruler')||t.includes('length measure'))return ruler();
    if(t.includes('hundred chart')||t.includes('10x10'))return hundredChart();
    if(t.includes('budget'))return table('budget');
    if(t.includes('ratio table'))return table('ratio');
    if(t.includes('frequency'))return table('frequency');
    if(t.includes('table'))return table('generic');
    if(t.includes('long division')||t.includes('division algorithm'))return algorithm('division');
    if(t.includes('multiplication algorithm')||t.includes('vertical algorithm')||t.includes('standard algorithm'))return algorithm('multiply');
    if(t.includes('place-value chart')||t.includes('place value chart')||t.includes('structured table'))return table('generic');
    if(t.includes('graph'))return coordinateGrid();
    if(t.includes('plot'))return dotPlot();
    if(t.includes('diagram'))return polygon();
    if(t.includes('model'))return shapeArray();
    return '';
  }

  function promptFor(meta){
    const l=String(meta?.label||'').toLowerCase();
    if(l.includes('factor')&&l.includes('visual'))return 'Use the array model to list every factor pair of 24. Then write all factors of 24.';
    if(l.includes('common factor'))return 'Find all common factors of 18 and 30. Circle the greatest common factor.';
    if(l.includes('divisibility'))return 'Which numbers are divisible by 3? Use a divisibility rule to justify your choices: 126, 145, 231, 508.';
    if(l.includes('prime'))return 'Is 37 prime or composite? Explain how you know.';
    if(l.includes('multiple')&&!l.includes('multiplication'))return 'List the first five multiples of 8. Then identify which of those are also multiples of 6.';
    if(l.includes('base ten')&&l.includes('addition'))return 'Use the base-ten model to represent 238 + 146. Regroup when needed, then find the sum.';
    if(l.includes('base ten')&&l.includes('subtraction'))return 'Use the base-ten model to represent 402 − 175. Regroup when needed, then find the difference.';
    if(l.includes('base ten'))return 'Write the whole number represented by the base-ten blocks.';
    if(l.includes('number line')&&l.includes('place'))return 'Place 68 on the number line. Label the two nearest tens and explain which ten is closer.';
    if(l.includes('number line'))return 'Use the number line to solve 46 + 27. Show the jumps you used.';
    if(l.includes('equivalent fraction'))return 'Use the two models to explain why 3/4 and 6/8 are equivalent.';
    if(l.includes('compare')&&l.includes('fraction'))return 'Compare 5/8 and 3/4 using >, <, or =. Use a model or equivalent fractions to justify your answer.';
    if(l.includes('fraction')&&l.includes('division'))return 'Use a visual model to determine how many 1/4-size groups fit in 2 1/2 wholes. Write a division equation.';
    if(l.includes('fraction')&&l.includes('multip'))return 'Find 3/5 of 20. Show a model or equation that represents your reasoning.';
    if(l.includes('fraction')&&l.includes('add'))return 'Rewrite with common denominators, then find 2/3 + 3/8. Simplify your answer.';
    if(l.includes('fraction')&&l.includes('subtract'))return 'Rewrite with common denominators, then find 5/6 − 1/4. Simplify your answer.';
    if(l.includes('decimal')&&l.includes('multip'))return 'Complete the standard algorithm for 6.4 × 0.7. Show any regrouping and place the decimal correctly.';
    if(l.includes('decimal')&&l.includes('division'))return 'Use long division to find 57.6 ÷ 4. Write the quotient as a decimal.';
    if(l.includes('decimal')&&l.includes('money'))return 'A snack costs $2.45 and a drink costs $1.80. What is the total cost? Show your calculation.';
    if(l.includes('conversion'))return 'Use the conversion relationship 1 yard = 3 feet to convert 24 feet to yards. Show your reasoning.';
    if(l.includes('perimeter'))return 'Find the perimeter of the labeled polygon. Show how you used every outside side length.';
    if(l.includes('area'))return 'Find the area of the figure using the given dimensions. Include square units.';
    if(l.includes('angle'))return 'Find the missing angle measure shown in the diagram and classify the angle.';
    if(l.includes('coordinate'))return 'Plot the point (4, 3), then write the ordered pair of the labeled point already shown.';
    if(l.includes('ratio table'))return 'Complete the ratio table so every column represents the same proportional relationship.';
    if(l.includes('double number line'))return 'Use the double number line to find the missing value. Explain the scale factor you used.';
    if(l.includes('dilation'))return 'Dilate triangle ABC about the origin by a scale factor of 2. Plot the image and list the three image coordinates.';
    if(l.includes('scale factor'))return 'The two figures are scaled copies. Determine the scale factor from Figure 1 to Figure 2 and justify it with corresponding sides.';
    if(l.includes('budget'))return 'The monthly income is $4,200. Use the budget table to find the missing “Other” amount so the budget balances.';
    if(l.includes('tax'))return 'A homeowner pays a yearly amount based on the value of a house to support local services. Which type of tax is described?';
    if(l.includes('gross')||l.includes('net income'))return 'A worker earns $860 before deductions and takes home $684. Identify the gross income, net income, and total deductions.';
    if(l.includes('probability'))return 'Four of the ten equally likely tiles are shaded. What is the probability of selecting a shaded tile? Write the probability as a fraction.';
    if(l.includes('dot')||l.includes('line plot'))return 'Use the dot plot to identify the mode and the range of the data.';
    if(l.includes('stem-and-leaf'))return 'Create a stem-and-leaf plot for 22, 24, 27, 31, 31, 35, 38. Then identify the median.';
    if(l.includes('mean')||l.includes('median')||l.includes('mode')||l.includes('range'))return 'For the data set 4, 6, 6, 7, 12, find the mean, median, mode, and range.';
    if(l.includes('time')||l.includes('clock'))return 'Read the clock. Write the time, then find the time 35 minutes later.';
    if(meta?.summary)return `${String(meta.summary).replace(/\.$/,"")}. Use the representation shown and complete the requested response.`;
    return 'Complete the representative problem using the structure shown. Show enough work to make your reasoning clear.';
  }

  function choicesFor(meta){
    const l=String(meta?.label||'').toLowerCase();
    if(l.includes('tax'))return ['Property tax','Sales tax','Income tax','Payroll tax'];
    if(l.includes('payment method'))return ['It can be mailed.','It requires tracking the account balance.','It never uses a bank account.','It always earns interest.'];
    if(l.includes('reasonable unit')||l.includes('estimate'))return ['millimeters','centimeters','meters','kilometers'];
    if(l.includes('probability'))return ['2/5','4/5','5/4','1/4'];
    if(l.includes('prime'))return ['Prime, because its only positive factors are 1 and 37.','Composite, because 37 is odd.','Composite, because 3 + 7 = 10.','Prime, because every odd number is prime.'];
    if(l.includes('graph')||l.includes('table'))return ['The first representation only','The second representation only','Both representations','Neither representation'];
    return ['12','16','18','24'];
  }

  function responseFor(meta){
    const modes=(meta?.response_modes||[]).join(' ').toLowerCase();
    if(modes.includes('selected'))return `<div class="preview-choices">${choicesFor(meta).map((choice,i)=>`<label><span>${String.fromCharCode(65+i)}.</span> ${esc(choice)}</label>`).join('')}</div>`;
    if(modes.includes('explanation'))return '<div class="preview-response-lines"><span></span><span></span><span></span></div>';
    return '<div class="preview-answer-line">Answer: ____________________________________________</div><div class="preview-workspace"></div>';
  }

  function ensureModal(){
    if(document.getElementById('questionPreviewOverlay'))return;
    const overlay=document.createElement('div');overlay.id='questionPreviewOverlay';overlay.className='preview-overlay';overlay.setAttribute('aria-hidden','true');
    overlay.innerHTML=`<section class="preview-modal" role="dialog" aria-modal="true" aria-labelledby="questionPreviewTitle"><div class="preview-modal-head"><div><div class="preview-kicker" id="questionPreviewKicker">Question structure preview</div><h2 id="questionPreviewTitle">Preview</h2></div><button class="preview-close" type="button" aria-label="Close preview">×</button></div><div class="preview-modal-body"><p class="preview-note">Representative complete problem — the generated worksheet will use original values, context, visuals, and parallel-version parameters.</p><div class="preview-paper"><div class="preview-problem"><strong>1.</strong><span id="questionPreviewPrompt"></span></div><div id="questionPreviewVisual" class="preview-visual"></div><div id="questionPreviewResponseBlock"></div></div><div class="preview-meta-grid"><div><b>Grade / topic</b><span id="questionPreviewScope"></span></div><div><b>Representation</b><span id="questionPreviewRepresentation"></span></div><div><b>Response</b><span id="questionPreviewResponse"></span></div></div></div></section>`;
    document.body.appendChild(overlay);
    overlay.querySelector('.preview-close').addEventListener('click',closePreview);
    overlay.addEventListener('click',e=>{if(e.target===overlay)closePreview();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&overlay.classList.contains('open'))closePreview();});
  }

  function openPreview(id){
    ensureModal();
    const meta=catalogIndex.get(id)||{};
    document.getElementById('questionPreviewTitle').textContent=meta.label||'Question preview';
    document.getElementById('questionPreviewKicker').textContent=meta.category||'Question structure preview';
    document.getElementById('questionPreviewPrompt').textContent=promptFor(meta);
    const visual=visualFor(meta);const visualEl=document.getElementById('questionPreviewVisual');visualEl.innerHTML=visual;visualEl.hidden=!visual;
    document.getElementById('questionPreviewResponseBlock').innerHTML=responseFor(meta);
    document.getElementById('questionPreviewScope').textContent=[meta.course,meta.topic].filter(Boolean).join(' · ')||'Selected math skill';
    document.getElementById('questionPreviewRepresentation').textContent=(meta.representations||[meta.visual||'No separate visual']).join(', ');
    document.getElementById('questionPreviewResponse').textContent=(meta.response_modes||['constructed response']).join(', ');
    const overlay=document.getElementById('questionPreviewOverlay');overlay.classList.add('open');overlay.setAttribute('aria-hidden','false');overlay.querySelector('.preview-close').focus();
  }

  function closePreview(){const overlay=document.getElementById('questionPreviewOverlay');if(!overlay)return;overlay.classList.remove('open');overlay.setAttribute('aria-hidden','true');}

  function decorate(){
    document.querySelectorAll('.skill-row').forEach(row=>{
      if(row.querySelector('[data-preview-family]'))return;
      const id=row.dataset.familyId;if(!id)return;
      const qty=row.querySelector(':scope > .qty');if(!qty)return;
      const stack=document.createElement('div');stack.className='preview-control-stack';qty.replaceWith(stack);stack.appendChild(qty);
      const button=document.createElement('button');button.type='button';button.className='preview-btn';button.dataset.previewFamily=id;button.innerHTML=`${magnifier}<span>Preview</span>`;button.title='Preview this complete question structure';button.setAttribute('aria-label','Preview this complete question structure');stack.appendChild(button);
    });
  }

  document.addEventListener('click',e=>{const button=e.target.closest('[data-preview-family]');if(button)openPreview(button.dataset.previewFamily);});
  document.addEventListener('DOMContentLoaded',async()=>{await loadCatalog();ensureModal();decorate();const mount=document.getElementById('familyMount');if(mount){observer=new MutationObserver(decorate);observer.observe(mount,{childList:true,subtree:true});}});
})();
