(() => {
  'use strict';
  const MAX_VARIANTS = 8;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const tex = value => String.raw`\(${value}\)`;
  const table = (headers, rows) => `<table><thead><tr>${headers.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${x===null?'?':esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  const choices = items => `<ol class="choices" type="A">${items.map(x=>`<li>${x}</li>`).join('')}</ol>`;
  const visualUrl = (kind, params={}) => {
    const q = new URLSearchParams({kind});
    Object.entries(params).forEach(([k,v]) => {
      if (Array.isArray(v)) q.set(k, v.join(','));
      else if (v !== undefined && v !== null) q.set(k, String(v));
    });
    return `/api/assessment-visual?${q.toString()}`;
  };
  function hashSeed(text){ let h=2166136261>>>0; for(const ch of String(text)){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)>>>0;} return h>>>0; }
  function rngFor(f, variantIndex, slot=0){ let state=hashSeed(`${f.family_id}|${variantIndex}|${slot}`)||1; return () => { state=(Math.imul(state,1664525)+1013904223)>>>0; return state/4294967296; }; }
  const pick=(r,arr)=>arr[Math.floor(r()*arr.length)%arr.length];
  const ri=(r,min,max)=>Math.floor(r()*(max-min+1))+min;
  const nonzero=(r,min=-6,max=6)=>{let n=0;while(!n)n=ri(r,min,max);return n;};
  const fmt=n=>Number.isInteger(n)?String(n):String(Math.round(n*100)/100);
  const signed=n=>n<0?` - ${Math.abs(n)}`:` + ${n}`;
  const lin=(a,b)=>`${a===1?'':a===-1?'-':a}x${b?signed(b):''}`;
  const linearValue=(a,b,x)=>a*x+b;
  function base(f){ return {student_html:f?.exemplar?.student_html||'', answer:f?.exemplar?.answer||'', solution:f?.exemplar?.solution||'', variant_index:0}; }
  function rotateChoicesHtml(html, shift){
    const box=document.createElement('div'); box.innerHTML=html||'';
    box.querySelectorAll('ol.choices,ul.choices').forEach(list=>{
      const items=[...list.children]; if(items.length<2)return; const k=shift%items.length;
      items.slice(k).concat(items.slice(0,k)).forEach(li=>list.appendChild(li));
    });
    return box.innerHTML;
  }
  function surfaceFallback(f,v){
    let html=f?.exemplar?.student_html||''; let answer=f?.exemplar?.answer||''; let solution=f?.exemplar?.solution||'';
    html=html.replace(/(src=["'])assets\//gi,'$1/banks/assets/').replace(/(href=["'])assets\//gi,'$1/banks/assets/');
    const variable=['x','n','t','p','m','k'][v%6];
    if(variable!=='x'){
      html=html.replace(/\bx\b/g,variable); answer=answer.replace(/\bx\b/g,variable); solution=solution.replace(/\bx\b/g,variable);
    }
    if(/class=["']choices/.test(html)) html=rotateChoicesHtml(html,v);
    return {student_html:html,answer,solution,variant_index:v};
  }
  function patternRule(f,v,r){
    const start=ri(r,2,10), d=ri(r,2,7), seq=[0,1,2,3].map(i=>start+i*d), name=f.family_name||'';
    if(/Error/i.test(name)){ const bad=[...seq,start+4*d]; bad[3]+=pick(r,[1,2,-1]); return {student_html:`<p>${bad.join(', ')}</p><p><strong>Find the first error.</strong></p>`,answer:`${bad[3]} is the first error; it should be ${seq[3]}.`,solution:`The pattern changes by ${d} each step.`,variant_index:v}; }
    if(/Next|Choose the Next/i.test(name)){ const ans=start+4*d, distract=[ans-d,ans-1,ans+1,ans+d].filter((x,i,a)=>a.indexOf(x)===i).slice(0,3); const opts=[ans,...distract].sort(()=>r()-.5); return {student_html:`<p>${seq.join(', ')}, ...</p><p><strong>Next value?</strong></p>${choices(opts)}`,answer:String(ans),solution:`Add ${d}.`,variant_index:v}; }
    if(/Later|Predict/i.test(name)){ const n=ri(r,7,15), ans=start+(n-1)*d; return {student_html:`<p>${seq.join(', ')}, ...</p><p><strong>Find the ${n}th term.</strong></p>`,answer:String(ans),solution:`Start at ${start} and add ${d} for each step.`,variant_index:v}; }
    if(/Rule in Words|Describe|Growth/i.test(name)) return {student_html:`<p>${seq.join(', ')}, ...</p><p><strong>Describe the rule.</strong></p>`,answer:`Add ${d} each step.`,solution:`Consecutive terms differ by ${d}.`,variant_index:v};
    return {student_html:`<p>${seq.join(', ')}, ...</p><p><strong>State the change.</strong></p>`,answer:`+${d}`,solution:`Each term increases by ${d}.`,variant_index:v};
  }
  function patternGraphTable(f,v,r){
    const name=f.family_name||'', m=ri(r,2,6), b=ri(r,-3,6);
    if(/Out-of-Place/i.test(name)){
      const xs=[0,1,2,3], badIndex=(v+1)%xs.length, pts=xs.map((x,i)=>[x,linearValue(m,b,x)+(i===badIndex?pick(r,[1,2,-1]):-0)]);
      return {student_html:`<p>Rule: <strong>${tex(`y=${lin(m,b)}`)}</strong></p><p>${pts.map(([x,y])=>`(${x}, ${y})`).join(', ')}</p><p><strong>Which pair does not fit?</strong></p>`,answer:`(${pts[badIndex][0]}, ${pts[badIndex][1]})`,solution:`For x=${pts[badIndex][0]}, the rule gives y=${linearValue(m,b,pts[badIndex][0])}.`,variant_index:v};
    }
    if(/Compare Table and Equation/i.test(name)){
      const rateA=m, rateB=m+(v%2?2:-1), rows=[[1,rateA],[2,2*rateA],[4,4*rateA]], winner=rateA>rateB?'A':rateB>rateA?'B':'They are equal';
      return {student_html:`<p><strong>Relationship A</strong></p>${table(['x','y'],rows)}<p><strong>Relationship B:</strong> ${tex(`y=${rateB}x`)}</p><p><strong>Which has the greater unit rate?</strong></p>`,answer:winner,solution:`A has unit rate ${rateA}; B has unit rate ${rateB}.`,variant_index:v};
    }
    if(/Compare Two Input-Output Rules|Compare Outputs/i.test(name)){
      const m2=m+pick(r,[1,2]), x=ri(r,2,6), y1=m*x+b, y2=m2*x+b;
      return {student_html:`<p>A: ${tex(`y=${lin(m,b)}`)} &nbsp;&nbsp; B: ${tex(`y=${lin(m2,b)}`)}</p><p><strong>At x=${x}, which output is greater?</strong></p>`,answer:y1>y2?'A':'B',solution:`A=${y1}; B=${y2}.`,variant_index:v};
    }
    if(/List Ordered Pairs/i.test(name)){
      const rows=[0,1,2,3].map(x=>[x,linearValue(m,b,x)]); return {student_html:`${table(['x','y'],rows)}<p><strong>List the ordered pairs.</strong></p>`,answer:rows.map(([x,y])=>`(${x}, ${y})`).join(', '),solution:'Pair each input with its output.',variant_index:v};
    }
    if(/Match Rule and Table|Match Rule to Graph/i.test(name)){
      const rows=[0,1,2,3].map(x=>[x,linearValue(m,b,x)]); return {student_html:`${table(['x','y'],rows)}<p><strong>Which rule matches the table?</strong></p>${choices([tex(`y=${lin(m,b)}`),tex(`y=${lin(m+1,b)}`),tex(`y=${lin(m,b+2)}`),tex(`y=${lin(-m,b)}`)])}`,answer:`y=${lin(m,b)}`,solution:`The output changes by ${m}; at x=0, y=${b}.`,variant_index:v};
    }
    const rows=[0,1,2,3].map(x=>[x,linearValue(m,b,x)]); return {student_html:`${table(['x','y'],rows)}<p><strong>Write the rule.</strong></p>`,answer:`y=${lin(m,b)}`,solution:`The rate is ${m} and the starting value is ${b}.`,variant_index:v};
  }
  function patternIO(f,v,r){
    const a=pick(r,[2,3,4,-2,-1]), b=ri(r,-4,6), name=f.family_name||'';
    if(/Input for|Reverse|Missing Input/i.test(name)){
      const x=ri(r,1,7), y=linearValue(a,b,x); return {student_html:`<p>Rule: ${tex(`y=${lin(a,b)}`)}</p><p><strong>What input gives ${tex(`y=${y}`)}?</strong></p>`,answer:String(x),solution:`Solve ${y}=${lin(a,b)}.`,variant_index:v};
    }
    if(/Write.*Rule/i.test(name)){
      const rows=[0,1,2,3].map(x=>[x,linearValue(a,b,x)]); return {student_html:`${table(['x','y'],rows)}<p><strong>Write a rule.</strong></p>`,answer:`y=${lin(a,b)}`,solution:`The output changes by ${a}; when x=0, y=${b}.`,variant_index:v};
    }
    if(/Function Machine/i.test(name)){
      const x=ri(r,2,8), y=linearValue(a,b,x); return {student_html:`<p>Rule: multiply by ${a}, then ${b<0?'subtract':'add'} ${Math.abs(b)}.</p><p><strong>Input ${x} → output?</strong></p>`,answer:String(y),solution:`${a}(${x})${b?signed(b):''}=${y}.`,variant_index:v};
    }
    const xs=[-2,0,2,4], rows=xs.map((x,i)=>[x,(i===((v+1)%xs.length))?null:linearValue(a,b,x)]), missing=xs[(v+1)%xs.length], ans=linearValue(a,b,missing);
    return {student_html:`<p>Use ${tex(`y=${lin(a,b)}`)}.</p>${table(['x','y'],rows)}<p><strong>Complete the table.</strong></p>`,answer:`Missing output: ${ans}.`,solution:`Substitute x=${missing}.`,variant_index:v};
  }
  function evaluateVar(f,v,r){
    if(/Compare/i.test(f.family_name||'')){
      const p=ri(r,2,7), q=ri(r,-3,5), x=ri(r,2,6), A=x+p, B=2*x+q; return {student_html:`<p>A: ${tex(`x+${p}`)} &nbsp;&nbsp; B: ${tex(`2x${q?signed(q):''}`)}</p><p>${tex(`x=${x}`)}</p><p><strong>Which is greater?</strong></p>`,answer:A>B?'A':B>A?'B':'Equal',solution:`A=${A}; B=${B}.`,variant_index:v};
    }
    const a=nonzero(r,-5,5), b=ri(r,-6,8), x=ri(r,-5,7), y=linearValue(a,b,x); const html=`<p><strong>Evaluate ${tex(`y=${lin(a,b)}`)} when ${tex(`x=${x}`)}.</strong></p>`;
    if(f.response_mode==='selected_response'){ const opts=[y,y+a,y-b,-y].filter((x,i,a)=>a.indexOf(x)===i).slice(0,4).sort(()=>r()-.5); return {student_html:html+choices(opts),answer:String(y),solution:`Substitute x=${x}: y=${y}.`,variant_index:v}; }
    return {student_html:html,answer:String(y),solution:`Substitute x=${x}: y=${y}.`,variant_index:v};
  }
  const contextPairs=[['time (min)','distance (m)'],['hours','cost ($)'],['practice (min)','score'],['days','plant height (cm)']];
  function graphStory(f,v,r){
    const q=f.teacher_question_id||'', name=f.family_name||'', [xl,yl]=pick(r,contextPairs);
    if(q==='Q001' || /Axes Tell/i.test(name)){
      const m=ri(r,2,6), b=ri(r,0,10); return {student_html:`<img class="graph" src="${visualUrl('line',{m,b,xmin:0,xmax:10,ymin:0,ymax:70,xlabel:xl,ylabel:yl,context:1})}" alt="context graph"><p><strong>What does each axis represent?</strong></p>`,answer:`x-axis: ${xl}; y-axis: ${yl}.`,solution:'Read the axis labels and units.',variant_index:v};
    }
    if(q==='Q002' || /Interpret One Point/i.test(name) || /Match a Point/i.test(name) || /Cite One Point/i.test(name)){
      const x=ri(r,2,8)*5, y=ri(r,4,12)*10; const img=`<img class="graph" src="${visualUrl('point',{x,y,xmin:0,xmax:50,ymin:0,ymax:160,xlabel:xl,ylabel:yl,context:1})}" alt="context point graph">`;
      if(/Match a Point/i.test(name)) return {student_html:`${img}${choices([`At ${x} ${xl.split(' ')[0]}, the value is ${y} ${yl}.`,`At ${y} ${xl.split(' ')[0]}, the value is ${x} ${yl}.`,`The rate is ${y} per ${x}.`,`The graph stops at ${x}.`])}<p><strong>Which statement matches the point?</strong></p>`,answer:`At ${x} ${xl.split(' ')[0]}, the value is ${y} ${yl}.`,solution:'Read x first, then y.',variant_index:v};
      if(/Cite One Point/i.test(name)) return {student_html:`${img}<p><strong>Use the point (${x}, ${y}) as evidence in one sentence.</strong></p>`,answer:`Example: At ${x} on the x-axis, the y-value is ${y}.`,solution:'Use both coordinates and the graph quantities.',variant_index:v};
      return {student_html:`${img}<p><strong>What does the point (${x}, ${y}) mean?</strong></p>`,answer:`At ${x} ${xl}, ${yl} is ${y}.`,solution:'State the meaning of both coordinates with units.',variant_index:v};
    }
    if(q==='Q003' || /Constant Interval|Cite One Segment/i.test(name)){
      const a=ri(r,2,4), b=a+ri(r,2,3), y=ri(r,5,12)*10; const img=`<img class="graph" src="${visualUrl('piecewise',{a,b,y,xmax:10,ymax:160,xlabel:xl,ylabel:yl})}" alt="piecewise context graph">`;
      const prompt=/Cite One Segment/i.test(name)?'What does the horizontal segment show?':`Describe what happens from ${a} to ${b} on the x-axis.`;
      return {student_html:`${img}<p><strong>${prompt}</strong></p>`,answer:`The y-value stays at ${y}; it is constant on that interval.`,solution:`The graph is horizontal from ${a} to ${b}.`,variant_index:v};
    }
    if(/Choose the Axis/i.test(name)){ const pair=pick(r,[['hours studied','quiz score'],['number of tickets','total cost'],['time','distance'],['items','total weight']]); return {student_html:`<p>A table records <strong>${pair[0]}</strong> and <strong>${pair[1]}</strong>.</p><p><strong>Which variable belongs on the x-axis?</strong></p>`,answer:pair[0],solution:'Use the independent/input variable on the x-axis.',variant_index:v}; }
    if(/Label Both Axes/i.test(name)){ const pair=pick(r,[['number of tickets','total cost'],['minutes','distance'],['hours worked','total pay']]); return {student_html:`<p>A graph compares <strong>${pair[0]}</strong> and <strong>${pair[1]}</strong>.</p><p><strong>Label the x- and y-axes.</strong></p>`,answer:`x: ${pair[0]}; y: ${pair[1]}.`,solution:'Place the input/independent quantity on x.',variant_index:v}; }
    if(/Compare Two Changes/i.test(name)){ const y0=ri(r,1,5), d1=ri(r,2,5), d2=d1+ri(r,2,5); return {student_html:`${table(['x','y'],[[0,y0],[2,y0+d1],[4,y0+d1+d2]])}<p><strong>Which interval has the larger change in y: 0 to 2 or 2 to 4?</strong></p>`,answer:'2 to 4.',solution:`The changes are ${d1} and ${d2}.`,variant_index:v}; }
    if(/Change from Two Points/i.test(name)){ const x1=ri(r,1,4), x2=x1+ri(r,2,5), y1=ri(r,2,8), dy=ri(r,3,9), y2=y1+dy; return {student_html:`<p>Use the points ${tex(`(${x1},${y1})`)} and ${tex(`(${x2},${y2})`)}.</p><p><strong>How does y change?</strong></p>`,answer:`y increases by ${dy}.`,solution:`${y2}-${y1}=${dy}.`,variant_index:v}; }
    const m=pick(r,[2,3,4]), img=`<img class="graph" src="${visualUrl('line',{m,b:0,xmin:0,xmax:10,ymin:0,ymax:50,xlabel:xl,ylabel:yl,context:1})}" alt="context graph">`;
    if(/Wrong Description/i.test(name)) return {student_html:`${img}<p><strong>Which description is wrong?</strong></p>${choices(['y increases as x increases.','The graph rises left to right.','y stays constant as x increases.','The relation has positive change.'])}`,answer:'y stays constant as x increases.',solution:'The line rises, so y is increasing.',variant_index:v};
    if(/Matching Story/i.test(name)) return {student_html:`${img}<p><strong>Which story matches?</strong></p>${choices(['The dependent quantity increases steadily.','The dependent quantity decreases steadily.','The dependent quantity stays constant.','The input decreases as the output increases.'])}`,answer:'The dependent quantity increases steadily.',solution:'The graph rises at a constant rate.',variant_index:v};
    if(/Contradiction/i.test(name)) return {student_html:`${img}<p>A student says, “The dependent quantity decreases as the input increases.”</p><p><strong>What is wrong?</strong></p>`,answer:'The graph increases, not decreases.',solution:'It rises from left to right.',variant_index:v};
    return {student_html:`${img}<p><strong>Write one statement supported by the graph.</strong></p>`,answer:'Example: The dependent quantity increases at a constant rate.',solution:'Use a visible point or segment as evidence.',variant_index:v};
  }
  function coordPlot(f,v,r){
    const name=f.family_name||'', x=nonzero(r,-7,7), y=nonzero(r,-7,7);
    if(/Plot Three/i.test(name)){ const pts=[[x,y],[nonzero(r,-7,7),nonzero(r,-7,7)],[nonzero(r,-7,7),nonzero(r,-7,7)]]; return {student_html:`<img class="graph" src="${visualUrl('blank',{xmin:-10,xmax:10,ymin:-10,ymax:10})}" alt="blank coordinate plane"><p><strong>Plot ${pts.map(p=>tex(`(${p[0]},${p[1]})`)).join(', ')}.</strong></p>`,answer:pts.map(p=>`(${p[0]},${p[1]})`).join(', '),solution:'Plot x first, then y.',variant_index:v}; }
    if(/Plot from a Table/i.test(name)){ const rows=[[x,y],[x+2,y+3],[x+4,y+6]]; return {student_html:`${table(['x','y'],rows)}<img class="graph" src="${visualUrl('blank',{xmin:-10,xmax:10,ymin:-10,ymax:10})}" alt="blank coordinate plane"><p><strong>Plot the ordered pairs.</strong></p>`,answer:rows.map(p=>`(${p[0]},${p[1]})`).join(', '),solution:'Each row is one ordered pair.',variant_index:v}; }
    if(/Plot/i.test(name)) return {student_html:`<img class="graph" src="${visualUrl('blank',{xmin:-10,xmax:10,ymin:-10,ymax:10})}" alt="blank coordinate plane"><p><strong>Plot and label ${tex(`P(${x},${y})`)}.</strong></p>`,answer:`P(${x},${y})`,solution:'Move horizontally to x, then vertically to y.',variant_index:v};
    return {student_html:`<img class="graph" src="${visualUrl('point',{x,y,xmin:-10,xmax:10,ymin:-10,ymax:10,label:'P'})}" alt="coordinate plane with point P"><p><strong>Name the point.</strong></p>`,answer:`(${x}, ${y})`,solution:'Read x first, then y.',variant_index:v};
  }
  function variableRole(f,v,r){ const pairs=[['time (min)','distance (m)'],['hours worked','total pay'],['items bought','total cost'],['weeks','plant height']]; const [a,b]=pick(r,pairs), name=f.family_name||''; if(/Choose x and y/i.test(name))return{student_html:`<p>Compare <strong>${a}</strong> and <strong>${b}</strong>.</p><p><strong>Which is x? Which is y?</strong></p>`,answer:`x: ${a}; y: ${b}.`,solution:'Use the input/independent variable as x.',variant_index:v}; if(/Table/i.test(name))return{student_html:`${table([a,b],[[1,4],[2,8],[3,12]])}<p><strong>Which column is input? Which is output?</strong></p>`,answer:`Input: ${a}; output: ${b}.`,solution:'The output depends on the input.',variant_index:v}; return{student_html:`<p>${b} is measured as ${a} changes.</p><p><strong>Identify the independent and dependent variables.</strong></p>`,answer:`Independent: ${a}; dependent: ${b}.`,solution:'The dependent quantity responds to the independent quantity.',variant_index:v}; }
  function dataPlan(f,v,r){ const contexts=[['backpack weight','walking speed'],['practice time','free-throw percentage'],['screen time','sleep hours'],['temperature','ice-cream sales'],['hours slept','reaction time']]; const [a,b]=pick(r,contexts), name=f.family_name||''; if(/Write a Data Question/i.test(name))return{student_html:`<p>Variables: <strong>${a}</strong> and <strong>${b}</strong>.</p><p><strong>Write a data question.</strong></p>`,answer:`Example: Does ${a} relate to ${b}?`,solution:'The question must use both variables.',variant_index:v}; if(/Irrelevant/i.test(name))return{student_html:`<p>To study whether ${a} relates to ${b}, a student records ${a}, ${b}, and favorite color.</p><p><strong>Which variable is not needed?</strong></p>`,answer:'Favorite color.',solution:'It is not one of the paired quantities.',variant_index:v}; return{student_html:`<p>Question: Does ${a} relate to ${b}?</p><p><strong>What two variables should be measured?</strong></p>`,answer:`${a} and ${b}.`,solution:'Collect the two quantities named in the question.',variant_index:v}; }
  function pairedTable(f,v,r){ const a=ri(r,1,5), d=ri(r,2,5), rows=[[a,a+d],[a+2,a+d+3],[a+4,a+d+6]], name=f.family_name||''; if(/Missing Pair/i.test(name))return{student_html:`${table(['x','y'],rows)}<p><strong>Write the pair for x=${rows[1][0]}.</strong></p>`,answer:`(${rows[1][0]}, ${rows[1][1]})`,solution:'Read both values from the same row.',variant_index:v}; if(/Complete/i.test(name)){ const hidden=[[rows[0][0],rows[0][1]],[rows[1][0],null],[rows[2][0],rows[2][1]]]; return{student_html:`${table(['x','y'],hidden)}<p>Given pair: ${tex(`(${rows[1][0]},${rows[1][1]})`)}.</p><p><strong>Complete the table.</strong></p>`,answer:String(rows[1][1]),solution:'Use the given ordered pair.',variant_index:v}; } return{student_html:`<p>Pairs: ${rows.map(p=>`(${p[0]},${p[1]})`).join(', ')}</p><p><strong>Put the data in a two-column table.</strong></p>`,answer:rows.map(p=>`(${p[0]},${p[1]})`).join(', '),solution:'Keep each pair together in one row.',variant_index:v}; }
  function dataEvidence(f,v,r){ const start=ri(r,50,65), rows=[[10,start],[20,start+8],[30,start+16],[40,start+23]], name=f.family_name||''; if(/Counterexample/i.test(name)){ const k=ri(r,2,6), badX=ri(r,2,4), delta=pick(r,[1,2,-1]), xs=[1,2,3,4], rr=xs.map(x=>[x,k*x+(x===badX?delta:0)]), badY=k*badX+delta; return{student_html:`${table(['x','y'],rr)}<p>Claim: ${tex(`y=${k}x`)}.</p><p><strong>Find a counterexample.</strong></p>`,answer:`(${badX}, ${badY})`,solution:`For x=${badX}, ${k}x=${k*badX}, not ${badY}.`,variant_index:v}; } if(/Supported Claim|Unsupported/i.test(name)){ const opts=['y tends to increase as x increases.','y tends to decrease as x increases.','y is always the same.','There is no pattern.']; return{student_html:`${table(['Practice','Score'],rows)}<p><strong>${/Unsupported/i.test(name)?'Which claim is unsupported?':'Which claim is supported?'}</strong></p>${choices(opts)}`,answer:/Unsupported/i.test(name)?'y tends to decrease as x increases.':'y tends to increase as x increases.',solution:'Compare the direction of change across rows.',variant_index:v}; } return{student_html:`${table(['Practice (min)','Score'],rows)}<p><strong>Give one piece of evidence that more practice is associated with higher scores.</strong></p>`,answer:`Example: ${10} minutes corresponds to ${start}, while ${40} minutes corresponds to ${start+23}.`,solution:'Cite a specific row or pair.',variant_index:v}; }
  function scatter(f,v,r){ const name=f.family_name||''; let trend=/negative/i.test(name)?'negative':/no clear|flat|none/i.test(name)?'none':'positive'; const xs=[1,2,3,4,5,6,7,8]; let ys=xs.map(x=>trend==='positive'?2*x+ri(r,-1,1):trend==='negative'?18-2*x+ri(r,-1,1):ri(r,5,15)); if(/outlier/i.test(name))ys[6]=trend==='negative'?18:3; const img=`<img class="graph" src="${visualUrl('scatter',{x:xs,y:ys,xmin:0,xmax:9,ymin:0,ymax:20,xlabel:'x',ylabel:'y'})}" alt="scatter plot">`; if(/outlier/i.test(name))return{student_html:`${img}<p><strong>Identify the outlier.</strong></p>`,answer:`(${xs[6]}, ${ys[6]})`,solution:'It lies far from the overall pattern.',variant_index:v}; if(/predict/i.test(name))return{student_html:`${img}<p><strong>Estimate y when x=9.</strong></p>`,answer:trend==='positive'?'About 18.':trend==='negative'?'About 0 to 2.':'A precise prediction is not supported.',solution:'Use the overall trend, not one point.',variant_index:v}; return{student_html:`${img}<p><strong>Describe the association.</strong></p>`,answer:trend==='positive'?'Positive association.':trend==='negative'?'Negative association.':'No clear association.',solution:'Describe the overall direction of the points.',variant_index:v}; }
  function ratioEquivalent(f,v,r){ const factor=ri(r,2,5), x=ri(r,2,7), y=ri(r,2,9), name=f.family_name||''; if(/Proportion/i.test(name)){ const a=ri(r,2,7), b=ri(r,4,12), c=a*factor; return{student_html:`<p>${a} notebooks cost $${b}. Let c be the cost of ${c} notebooks.</p><p><strong>Write a proportion.</strong></p>`,answer:`${a}/${b} = ${c}/c`,solution:'Keep corresponding quantities in the same order.',variant_index:v}; } const rows=[[x,y],[x*2,y*2],[x*3,y*3],[x*factor,y*factor]]; if(/Nonproportional Row/i.test(name)){ const bad=rows.map(a=>[...a]);bad[2][1]+=1;return{student_html:`${table(['x','y'],bad)}<p><strong>Which row does not fit?</strong></p>`,answer:`(${bad[2][0]}, ${bad[2][1]})`,solution:`The constant ratio should be ${y}/${x}.`,variant_index:v}; } return{student_html:`${table(['x','y'],rows)}<p><strong>Is the relationship proportional?</strong></p>`,answer:'Yes.',solution:`The ratio y/x is constant: ${y}/${x}.`,variant_index:v}; }
  function unitRate(f,v,r){ const units=ri(r,3,8), rate=pick(r,[2,2.5,3,4,5]), total=units*rate, name=f.family_name||''; if(/reasonable|Estimate/i.test(name)){ const target=units*2; const exact=target*rate; return{student_html:`<p>${units} items cost $${fmt(total)}.</p><p><strong>Estimate the cost of ${target} items.</strong></p>`,answer:`About $${fmt(exact)}.`,solution:`The unit rate is $${fmt(rate)} per item.`,variant_index:v}; } return{student_html:`<p>${units} items cost $${fmt(total)}.</p><p><strong>Find the unit rate.</strong></p>`,answer:`$${fmt(rate)} per item.`,solution:`${fmt(total)} ÷ ${units} = ${fmt(rate)}.`,variant_index:v}; }
  function ratioCompare(f,v,r){ const r1=ri(r,3,7), r2=r1+ri(r,1,4), a=ri(r,2,5), b=ri(r,2,5); return{student_html:`<p>A: ${a*r1} miles in ${a} h &nbsp;&nbsp; B: ${b*r2} miles in ${b} h</p><p><strong>Which rate is greater?</strong></p>`,answer:'B',solution:`A=${r1} mi/h; B=${r2} mi/h.`,variant_index:v}; }
  function propSolve(f,v,r){ const a=ri(r,2,8), b=ri(r,3,10), k=ri(r,2,5), c=b*k, x=a*k; return{student_html:`<p><strong>Solve: ${tex(`\\frac{${a}}{${b}}=\\frac{x}{${c}}`)}</strong></p>`,answer:String(x),solution:`${c} is ${k} times ${b}, so x=${a}·${k}=${x}.`,variant_index:v}; }
  function ratioTable(f,v,r){ const k=ri(r,2,6), rows=[[2,2*k],[4,4*k],[7,7*k]], hide=(v+1)%3, shown=rows.map((row,i)=>[row[0],i===hide?null:row[1]]); return{student_html:`${table(['x','y'],shown)}<p><strong>Complete the proportional table.</strong></p>`,answer:String(rows[hide][1]),solution:`Use y=${k}x.`,variant_index:v}; }
  function ratioError(f,v,r){ const a=ri(r,2,6), b=ri(r,4,9), factor=ri(r,2,4); return{student_html:`<p>${a} items cost $${b}. A student says ${a*factor} items cost $${b+factor}.</p><p><strong>Explain the error.</strong></p>`,answer:`The cost should scale by ${factor}, so it should be $${b*factor}.`,solution:'Equivalent ratios require the same multiplicative scale factor.',variant_index:v}; }
  function propGraph(f,v,r){ const k=ri(r,2,6), offset=/Not Through/i.test(f.family_name||'')?ri(r,2,5):0; const img=`<img class="graph" src="${visualUrl('line',{m:k,b:offset,xmin:0,xmax:10,ymin:0,ymax:70,xlabel:'x',ylabel:'y'})}" alt="line graph">`; if(/Constant|unit rate|Find k/i.test(f.family_name||''))return{student_html:`${img}<p><strong>Find the unit rate / constant of proportionality.</strong></p>`,answer:String(k),solution:'Read rise per 1 unit of run.',variant_index:v}; return{student_html:`${img}<p><strong>Is the graph proportional?</strong></p>`,answer:offset===0?'Yes.':'No.',solution:offset===0?'It is a straight line through the origin.':'It does not pass through the origin.',variant_index:v}; }
  function diamond(f,v,r){ const a=nonzero(r,-8,8), b=nonzero(r,-8,8), product=a*b, sum=a+b; if(/Signed/i.test(f.family_name||'')) return{student_html:`<img class="graph" src="${visualUrl('diamond',{top:product,bottom:sum,left:'',right:''})}" alt="diamond problem"><p><strong>Complete the diamond.</strong></p>`,answer:`${a} and ${b}`,solution:`The side numbers multiply to ${product} and add to ${sum}.`,variant_index:v}; return{student_html:`<img class="graph" src="${visualUrl('diamond',{top:'',bottom:'',left:a,right:b})}" alt="diamond problem"><p><strong>Complete the diamond.</strong></p>`,answer:`Product ${product}; sum ${sum}.`,solution:`Multiply for the top and add for the bottom.`,variant_index:v}; }
  function tilesRead(f,v,r){ const name=f.family_name||'', neg=/Negative|All-Negative/i.test(name), x2=/x²|x\^2|Polynomial|square/i.test(name), a=ri(r,1,4), b=ri(r,1,5); const p={x:neg?0:a,neg_x:neg?a:0,one:neg&&/All-Negative/i.test(name)?0:b,neg_one:neg&&/All-Negative/i.test(name)?b:0,x2:x2?1:0}; const img=`<img class="graph" src="${visualUrl('tiles',p)}" alt="algebra tiles">`; const expr=`${x2?'x^2 + ':''}${neg?'-':''}${a===1?'':a}x${(p.neg_one?` - ${b}`:` + ${b}`)}`; if(/Count Variable|negative x-tiles/i.test(name))return{student_html:`${img}<p><strong>How many ${neg?'negative ':''}x-tiles?</strong></p>`,answer:String(a),solution:'Count the long variable tiles.',variant_index:v}; if(/Unit Tiles|Constant/i.test(name))return{student_html:`${img}<p><strong>How many unit tiles?</strong></p>`,answer:String(b),solution:'Count the unit tiles.',variant_index:v}; if(/Coefficient/i.test(name))return{student_html:`${img}<p><strong>Coefficient of x?</strong></p>`,answer:String(neg?-a:a),solution:'Use the signed number of x-tiles.',variant_index:v}; if(/Sign/i.test(name))return{student_html:`${img}<p><strong>What is the sign of the x-term?</strong></p>`,answer:neg?'Negative.':'Positive.',solution:'Use the tile sign/color.',variant_index:v}; return{student_html:`${img}<p><strong>Write the expression.</strong></p>`,answer:expr.replace('1x','x'),solution:'Count each tile type and preserve signs.',variant_index:v}; }
  function tilesBuild(f,v,r){ const neg=/Negative/i.test(f.family_name||''), a=ri(r,2,4), b=ri(r,1,5), expr=`${neg?'-':''}${a}x${neg?`-${b}`:`+${b}`}`; if(f.response_mode==='selected_response'){ const good=`${a} ${neg?'negative':'positive'} x-tiles and ${b} ${neg?'negative':'positive'} unit tiles`; const opts=[good,`${b} x-tiles and ${a} unit tiles`,`${a} ${neg?'positive':'negative'} x-tiles and ${b} unit tiles`,`one x²-tile and ${b} unit tiles`]; return{student_html:`<p><strong>Which tile set represents ${tex(expr)}?</strong></p>${choices(opts)}`,answer:good,solution:'Match the coefficient and constant to tile counts and signs.',variant_index:v}; } return{student_html:`<p><strong>Model ${tex(expr)} with algebra tiles.</strong></p><div class="response-surface">Draw or place the tiles.</div>`,answer:`${a} ${neg?'negative':'positive'} x-tiles and ${b} ${neg?'negative':'positive'} unit tiles.`,solution:'Match each term to its tile type.',variant_index:v}; }
  function zeroPair(f,v,r){ const a=ri(r,2,4), pairs=ri(r,1,2), b=ri(r,1,4), img=`<img class="graph" src="${visualUrl('tiles',{x:a+pairs,neg_x:pairs,one:b})}" alt="algebra tiles with zero pairs">`; return{student_html:`${img}<p><strong>Simplify the model by removing zero pairs.</strong></p>`,answer:`${a}x+${b}`,solution:`Each x and -x pair is 0.`,variant_index:v}; }
  function minusMeaning(f,v,r){ const n=ri(r,2,9), name=f.family_name||''; if(/Subtract a Negative/i.test(name))return{student_html:`<p><strong>Rewrite: ${tex(`x-(-${n})`)}</strong></p>`,answer:`x+${n}`,solution:'Subtracting a negative is adding.',variant_index:v}; if(/Negative Term/i.test(name))return{student_html:`<p>${tex(`-${n}x`)}</p><p><strong>What does the sign tell you?</strong></p>`,answer:'The coefficient is negative.',solution:`The term is ${n}x below zero/opposite in sign.`,variant_index:v}; if(/Negative Number/i.test(name))return{student_html:`<p>${tex(`-${n}`)}</p><p><strong>What does the minus sign mean?</strong></p>`,answer:'It is part of the negative number.',solution:'The sign belongs to the number.',variant_index:v}; return{student_html:`<p>${tex(`${n+5}-${n}`)}</p><p><strong>What does the minus sign mean?</strong></p>`,answer:'Subtraction.',solution:'It is the subtraction operation.',variant_index:v}; }
  function likeTerms(f,v,r){ const a=ri(r,2,7), b=ri(r,2,7), c=ri(r,1,6), name=f.family_name||''; if(/Not Like/i.test(name))return{student_html:`<p><strong>Which pair is not like terms?</strong></p>${choices([`${a}x and -${b}x`,`${a}y and ${b}y`,`${a}x² and ${b}x²`,`${a}x and ${b}x²`])}`,answer:`${a}x and ${b}x²`,solution:'Different powers are not like terms.',variant_index:v}; if(/Error/i.test(name))return{student_html:`<p>A student says ${tex(`${a}x`)} and ${tex(`${a}x^2`)} are like terms.</p><p><strong>Correct the claim.</strong></p>`,answer:'They are not like terms.',solution:'The variable powers must match.',variant_index:v}; return{student_html:`<p>${tex(`${a}x+${c}+${b}x-${c+2}`)}</p><p><strong>Name the like terms.</strong></p>`,answer:`${a}x and ${b}x; ${c} and -${c+2}.`,solution:'Like terms have the same variable part.',variant_index:v}; }
  function combineLike(f,v,r){ const a=ri(r,2,7), b=ri(r,2,7), c=ri(r,-6,6), d=ri(r,-6,6), coeff=a+b, constant=c+d; const expr=`${a}x+${b}x${c?signed(c):''}${d?signed(d):''}`; return{student_html:`<p><strong>Simplify: ${tex(expr)}</strong></p>`,answer:`${coeff}x${constant?signed(constant):''}`,solution:`Combine x-terms and constants separately.`,variant_index:v}; }
  function equivalentDistrib(f,v,r){ const a=ri(r,2,5), b=ri(r,1,6), c=ri(r,1,5), coeff=a+c, constant=a*b; const expr=`${a}(x+${b})+${c}x`; if(f.response_mode==='selected_response'){ const ans=`${coeff}x+${constant}`, opts=[ans,`${a+c}x+${b}`,`${a*c}x+${constant}`,`${coeff}x-${constant}`]; return{student_html:`<p>${tex(expr)}</p><p><strong>Choose the simplified form.</strong></p>${choices(opts)}`,answer:ans,solution:`Distribute ${a}, then combine like terms.`,variant_index:v}; } return{student_html:`<p><strong>Simplify: ${tex(expr)}</strong></p>`,answer:`${coeff}x+${constant}`,solution:`${a}x+${constant}+${c}x=${coeff}x+${constant}.`,variant_index:v}; }
  function equivalentExplain(f,v,r){ const a=ri(r,2,6), b=ri(r,2,8), c=ri(r,1,a), left=`${a}x+${b}-${c}x`, right=`${a-c}x+${b}`; if(/First Bad Step/i.test(f.family_name||''))return{student_html:`<p>${tex(`${a}x+${b}+${c}x=${a+c}x+${b}=${a+c+b}x`)}</p><p><strong>First incorrect step?</strong></p>`,answer:'The second step.',solution:'A constant cannot be combined with an x-term.',variant_index:v}; return{student_html:`<p>${tex(left)} and ${tex(right)}</p><p><strong>Are they equivalent? Explain.</strong></p>`,answer:'Yes.',solution:`Combine ${a}x-${c}x to get ${(a-c)}x.`,variant_index:v}; }
  function expressionCompare(f,v,r){ const name=f.family_name||'', a=ri(r,2,6), b=ri(r,1,8), c=b+ri(r,1,5); if(/Not Enough|depends/i.test(name))return{student_html:`<p>A: ${tex(`x+${b}`)} &nbsp;&nbsp; B: ${tex(`${a}x`)}</p><p><strong>Can you tell which is greater without knowing x?</strong></p>`,answer:'No; it depends on x.',solution:'Different x-values can change the comparison.',variant_index:v}; const left=`${a}x+${c}`, right=`${a}x+${b}`; if(f.response_mode==='selected_response')return{student_html:`<p>A: ${tex(left)} &nbsp;&nbsp; B: ${tex(right)}</p><p><strong>Which is greater?</strong></p>${choices(['A','B','equal','depends on x'])}`,answer:'A',solution:`The x-terms match and ${c}>${b}.`,variant_index:v}; return{student_html:`<p>A: ${tex(left)} &nbsp;&nbsp; B: ${tex(right)}</p><p><strong>Which is greater? Explain.</strong></p>`,answer:'A',solution:`Both have ${a}x; compare constants ${c} and ${b}.`,variant_index:v}; }
  function compareTiles(f,v,r){ const a=ri(r,1,4), b=ri(r,1,5), c=b+ri(r,1,3), A=visualUrl('tiles',{x:a,one:c}), B=visualUrl('tiles',{x:a,one:b}); return{student_html:`<div class="visual-pair"><div><strong>A</strong><img class="graph" src="${A}" alt="tile model A"></div><div><strong>B</strong><img class="graph" src="${B}" alt="tile model B"></div></div><p><strong>Which expression is greater?</strong></p>`,answer:'A',solution:`Both have ${a}x; A has the greater constant.`,variant_index:v}; }
  function oneStep(f,v,r){ if(/Multiplication/i.test(f.family_name||'')){ const a=ri(r,2,9), x=ri(r,2,10), b=a*x; return{student_html:`<p><strong>Solve: ${tex(`${a}x=${b}`)}</strong></p>`,answer:`x=${x}`,solution:`Divide both sides by ${a}.`,variant_index:v}; } const b=ri(r,2,10), x=ri(r,2,12), c=x+b; return{student_html:`<p><strong>Solve: ${tex(`x+${b}=${c}`)}</strong></p>`,answer:`x=${x}`,solution:`Subtract ${b} from both sides.`,variant_index:v}; }
  function twoStep(f,v,r){ const name=f.family_name||''; if(/Fraction/i.test(name)){ const d=ri(r,2,5), b=ri(r,1,5), k=ri(r,2,8), x=d*k, c=k+b; return{student_html:`<p><strong>Solve: ${tex(`\\frac{x}{${d}}+${b}=${c}`)}</strong></p>`,answer:`x=${x}`,solution:`Subtract ${b}, then multiply by ${d}.`,variant_index:v}; } const a=/Negative Coefficient/i.test(name)?-ri(r,2,4):ri(r,2,5), b=ri(r,1,7), x=ri(r,-5,8), c=a*x+b; if(/Error/i.test(name))return{student_html:`<p>${tex(`${a}x+${b}=${c}`)}</p><p>${tex(`${a}x=${c-b}`)}</p><p>${tex(`x=${c-b}`)}</p><p><strong>Fix the error.</strong></p>`,answer:`x=${x}`,solution:`After ${a}x=${c-b}, divide by ${a}.`,variant_index:v}; return{student_html:`<p><strong>Solve: ${tex(`${a}x+${b}=${c}`)}</strong></p>`,answer:`x=${x}`,solution:`Undo +${b}, then divide by ${a}.`,variant_index:v}; }
  function bothSides(f,v,r){ const x=ri(r,2,8), a=ri(r,3,6), c=ri(r,1,a-1), b=ri(r,-6,3), d=(a-c)*x+b; return{student_html:`<p><strong>Solve: ${tex(`${a}x${b?signed(b):''}=${c}x${d?signed(d):''}`)}</strong></p>`,answer:`x=${x}`,solution:`Move variable terms to one side and constants to the other.`,variant_index:v}; }
  function checkSolution(f,v,r){ const a=ri(r,2,5), x=ri(r,-4,7), b=ri(r,-5,6), c=a*x+b, candidate=/Reject/i.test(f.family_name||'')?x+1:x; return{student_html:`<p>Equation: ${tex(`${a}x${b?signed(b):''}=${c}`)}</p><p><strong>Does ${tex(`x=${candidate}`)} work?</strong></p>`,answer:candidate===x?'Yes.':'No.',solution:`Substitution gives ${a*candidate+b}${candidate===x?' = ':' ≠ '}${c}.`,variant_index:v}; }
  function balanceModel(f,v,r){ const name=f.family_name||'', b=ri(r,2,8), x=ri(r,4,14), c=x-b; if(/Repair|Unbalanced/i.test(name)){ const wrong=c; return{student_html:`<p>${tex(`x-${b}=${c} \\rightarrow x=${wrong}`)}</p><p><strong>Repair the step.</strong></p>`,answer:`Add ${b} to both sides: x=${x}.`,solution:'Use the same operation on both sides.',variant_index:v}; } if(/Explain|Why|Preserves/i.test(name))return{student_html:`<p>${tex(`x-${b}=${c}`)}</p><p><strong>Why does adding ${b} to both sides preserve equality?</strong></p>`,answer:'Both sides change by the same amount, so they remain equal.',solution:'Apply the same operation to both sides.',variant_index:v}; return{student_html:`<p>${tex(`x-${b}=${c}`)}</p><p><strong>What should you do to both sides first?</strong></p>`,answer:`Add ${b}.`,solution:'Use inverse operations equally on both sides.',variant_index:v}; }
  function tileEquation(f,v,r){ const a=ri(r,2,4), leftC=ri(r,1,4), rightC=leftC+ri(r,3,7), rightX=1, L=visualUrl('tiles',{x:a,one:leftC}), R=visualUrl('tiles',{x:rightX,one:rightC}); const eq=`${a}x+${leftC}=x+${rightC}`; return{student_html:`<div class="tile-equation"><img class="graph" src="${L}" alt="left tile expression"><span class="equals">=</span><img class="graph" src="${R}" alt="right tile expression"></div><p><strong>${/Solve/i.test(f.family_name||'')?'Solve for x.':'Write the equation.'}</strong></p>`,answer:/Solve/i.test(f.family_name||'')?`x=${(rightC-leftC)/(a-rightX)}`:eq,solution:'Read the tiles on each side of the equals sign.',variant_index:v}; }
  function numberSolutions(f,v,r){ const name=f.family_name||'', a=ri(r,2,5), b=ri(r,1,7); if(/No Solution|none/i.test(name))return{student_html:`<p><strong>How many solutions? ${tex(`${a}x+${b}=${a}x+${b+3}`)}</strong></p>`,answer:'No solution.',solution:'The x-terms cancel and leave a false statement.',variant_index:v}; if(/Infinite|all|many/i.test(name))return{student_html:`<p><strong>How many solutions? ${tex(`${a}(x+${b})=${a}x+${a*b}`)}</strong></p>`,answer:'Infinitely many solutions.',solution:'Both sides simplify to the same expression.',variant_index:v}; return bothSides(f,v,r); }
  function workStep(f,v,r){ const a=ri(r,2,6), b=ri(r,2,6); return{student_html:`<p>${tex(`${a}x+${b}x-2`)}</p><p><strong>Write the next valid step.</strong></p>`,answer:`${a+b}x-2`,solution:'Combine the like x-terms.',variant_index:v}; }
  function build(f, variantIndex=0, slot=0){
    const v=Math.max(0,Number(variantIndex)||0); if(v===0)return base(f); const r=rngFor(f,v,slot); const s=f.question_structure_id||'';
    try{
      switch(s){
        case 'PATTERN_RULE': return patternRule(f,v,r);
        case 'PATTERN_INPUT_OUTPUT': return patternIO(f,v,r);
        case 'PATTERN_GRAPH_TABLE_RULE': return patternGraphTable(f,v,r);
        case 'CC3_PATTERN_ERROR_ANALYSIS': return patternRule(f,v,r);
        case 'EXPR_EVALUATE_VAR': return evaluateVar(f,v,r);
        case 'COORD_PLOT_POINT': return coordPlot(f,v,r);
        case 'FUNC_GRAPH_STORY': return graphStory(f,v,r);
        case 'FUNC_LINEAR_NONLINEAR': return graphStory(f,v,r);
        case 'CC3_GRAPH_SCALE_READ': return surfaceFallback(f,v);
        case 'CC3_DATA_PLAN': return dataPlan(f,v,r);
        case 'CC3_PAIRED_DATA_TABLE': return pairedTable(f,v,r);
        case 'CC3_DATA_EVIDENCE': return dataEvidence(f,v,r);
        case 'CC3_VARIABLE_ROLE': return variableRole(f,v,r);
        case 'DATA_SCATTER_CORRELATION': return scatter(f,v,r);
        case 'DATA_GRAPH_TABLE_MATCH': return surfaceFallback(f,v);
        case 'RATIO_EQUIVALENT': return ratioEquivalent(f,v,r);
        case 'RATIO_UNIT_RATE': return unitRate(f,v,r);
        case 'RATIO_MIX_COMPARE': return ratioCompare(f,v,r);
        case 'PROP_SOLVE': return propSolve(f,v,r);
        case 'RATIO_TABLE_COMPLETE': return ratioTable(f,v,r);
        case 'RATIO_ERROR_ANALYSIS': return ratioError(f,v,r);
        case 'RATIO_DOUBLE_NUMBER_LINE': return unitRate(f,v,r);
        case 'FUNC_PROP_GRAPH_K': return propGraph(f,v,r);
        case 'PROP_GRAPH_CONSTANT': return propGraph(f,v,r);
        case 'CC3_DIAMOND_RELATION': return diamond(f,v,r);
        case 'CC3_ALGEBRA_TILES_READ': return tilesRead(f,v,r);
        case 'CC3_ALGEBRA_TILES_BUILD': return tilesBuild(f,v,r);
        case 'CC3_ZERO_PAIR': return zeroPair(f,v,r);
        case 'CC3_MINUS_MEANING': return minusMeaning(f,v,r);
        case 'CC3_LIKE_TERMS_IDENTIFY': return likeTerms(f,v,r);
        case 'CC3_COMBINE_LIKE_TERMS': return combineLike(f,v,r);
        case 'EXPR_EQUIVALENT_DISTRIB': return equivalentDistrib(f,v,r);
        case 'CC3_EQUIVALENT_EXPRESSION_EXPLAIN': return equivalentExplain(f,v,r);
        case 'CC3_EXPRESSION_COMPARE': return expressionCompare(f,v,r);
        case 'CC3_EXPRESSION_COMPARE_TILES': return compareTiles(f,v,r);
        case 'CC3_WORK_STEP_RECORDING': return workStep(f,v,r);
        case 'CC3_TILE_EQUATION_MODEL': return tileEquation(f,v,r);
        case 'EQ_BALANCE_MODEL': return balanceModel(f,v,r);
        case 'EQ_ONE_STEP': return oneStep(f,v,r);
        case 'EQ_TWO_STEP': return twoStep(f,v,r);
        case 'EQ_VARIABLE_BOTH_SIDES': return bothSides(f,v,r);
        case 'EQ_MULTI_STEP': return bothSides(f,v,r);
        case 'EQ_NUMBER_SOLUTIONS': return numberSolutions(f,v,r);
        case 'CC3_CHECK_SOLUTION': return checkSolution(f,v,r);
        default: return surfaceFallback(f,v);
      }
    }catch(err){ console.warn('Same-family variant fallback',f?.family_id,err); return surfaceFallback(f,v); }
  }
  function signature(instance){ return `${instance?.student_html||''}\n${instance?.answer||''}`; }
  function buildUnique(f, preferredIndex=1, slot=0, usedSignatures=[]){
    const used=new Set((usedSignatures||[]).filter(Boolean));
    if(Number(preferredIndex)===0){ const first=build(f,0,slot); return {...first,signature:signature(first)}; }
    const start=Math.max(1,Number(preferredIndex)||1);
    for(let offset=0;offset<MAX_VARIANTS-1;offset++){
      const idx=1+((start-1+offset)%(MAX_VARIANTS-1));
      const candidate=build(f,idx,slot), sig=signature(candidate);
      if(!used.has(sig)) return {...candidate,variant_index:idx,signature:sig};
    }
    const fallback=build(f,start,slot); return {...fallback,signature:signature(fallback)};
  }
  window.CC3AssessmentVariants={build,buildUnique,signature,MAX_VARIANTS,visualUrl};
})();
