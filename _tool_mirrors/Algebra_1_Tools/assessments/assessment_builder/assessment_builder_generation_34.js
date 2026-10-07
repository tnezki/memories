(function(){
  const prior=window.AssessmentGeneration;
  const NAMES=['Jordan','Maya','Sam','Alex','Riley','Taylor','Morgan','Casey','Avery','Cameron'];
  const pick=a=>a[Math.floor(Math.random()*a.length)];
  const ri=(a,b,nonzero=false)=>{let n;do{n=Math.floor(Math.random()*(b-a+1))+a}while(nonzero&&n===0);return n};
  const shuffle=a=>{a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
  const letter=i=>'ABCD'[i]||String(i+1);
  const math=s=>`\\(${s}\\)`;
  const choiceHtml=choices=>`<ol class="choices">${choices.map(c=>`<li>${c}</li>`).join('')}</ol>`;
  const inst=(student_html,answer,solution,note='Generated from the current approved family structure.')=>({student_html,answer,solution,generation_note:note});
  function mc(prompt,choices,correct,solution){
    const mixed=shuffle(choices.map((text,i)=>({text,correct:i===correct}))); const idx=mixed.findIndex(x=>x.correct);
    return inst(`<p>${prompt}</p>${choiceHtml(mixed.map(x=>x.text))}`,`${letter(idx)}. ${mixed[idx].text.replace(/<[^>]*>/g,'')}`,solution||'');
  }
  const table=(rows,x='x',y='y')=>`<table class="data-table"><tr><th>${x}</th><th>${y}</th></tr>${rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')}</table>`;
  const horizTable=(xs,ys,x='x',y='y')=>`<table class="data-table"><tr><th>${x}</th>${xs.map(v=>`<th>${v}</th>`).join('')}</tr><tr><th>${y}</th>${ys.map(v=>`<td>${v}</td>`).join('')}</tr></table>`;
  const lin=(m,b)=>b===0?`y=${m===1?'x':m===-1?'-x':`${m}x`}`:`y=${m===1?'x':m===-1?'-x':`${m}x`}${b>0?'+':''}${b}`;
  const money=n=>`$${Number(n).toFixed(2).replace(/\.00$/,'')}`;
  const staticEx=f=>{const ex=f?.exemplar||{};return inst(ex.student_html||'<p>Exemplar unavailable.</p>',ex.answer||'',ex.solution||'','Approved fixed representation; kept unchanged for this version.');};

  function g03(fid,f){
    let a,b,c,x,y,m,n,v,k,correct,choices,student;
    switch(fid){
      case 'U1-MG03-IC01-A':
        m=pick([-6,-5,-4,-3,2,3,4,5,6]);b=ri(-9,9);x=ri(-6,6,true);v=m*x+b;
        return inst(`<p>Evaluate ${math(`${m}x${b>=0?'+':''}${b}`)} when ${math(`x=${x}`)}.</p><div class="response-surface">Value: ______</div>`,String(v),`Substitute x=${x}.`);
      case 'U1-MG03-IC01-B':
        x=pick([2.5,3.5,4.5,5.5,6.5,7.5]);v=4*x;
        return inst(`<p>The perimeter of a square is ${math('P=4s')}. Find the perimeter when ${math(`s=${x}`)} cm.</p><div class="response-surface">Perimeter: ______</div>`,`${v} cm`,'Substitute the side length into P=4s.');
      case 'U1-MG03-IC01-C':
        x=-ri(2,7);b=ri(1,6);v=x*x+b;
        return inst(`<p>Evaluate ${math(`x^2+${b}`)} when ${math(`x=${x}`)}. A student writes ${math(`${x}^2+${b}=-${x*x}+${b}=${-x*x+b}`)}.</p><p>Explain the error and give the correct value.</p><div class="response-surface">Diagnosis:</div>`,String(v),`The negative input must be grouped: (${x})^2=${x*x}.`);
      case 'U1-MG03-IC01-D':
        m=pick([2,3,4,5,6]);b=ri(1,8);x=-ri(2,7);correct=`${m}(${x})-${b}`;
        return mc(`For ${math(`${m}x-${b}`)} when ${math(`x=${x}`)}, which substitution is correct?`,[math(correct),math(`${m}(${Math.abs(x)})-${b}`),math(`${m}${x}-${b}`),math(`${m}(${x}-${b})`)],0,'Replace x by the given negative value and group it.');
      case 'U1-MG03-IC01-E':
        a=ri(-5,5,true);b=ri(-5,5,true);m=pick([2,3,4]);n=pick([2,3,4]);v=m*a+n*b;
        return inst(`<p>Evaluate ${math(`${m}a+${n}b`)} when ${math(`a=${a}`)} and ${math(`b=${b}`)}.</p><div class="response-surface">Value: _____</div>`,String(v),'Substitute both values before evaluating.');
      case 'U1-MG03-IC01-F':
        m=pick([3,4,5,6]);b=ri(-5,5);x=ri(-6,6,true);
        return inst(`<p>When ${math(`x=${x}`)}, complete the substitution for ${math(`${m}x${b>=0?'+':''}${b}`)}:</p><p>${math(`${m}(\\square)${b>=0?'+':''}${b}`)}</p><div class="response-surface">Blank: _____</div>`,String(x),'The blank is the supplied value of x.');
      case 'U1-MG03-IC01-G':
        x=-ri(2,7);b=ri(1,6);v=x*x-b;
        choices=[String(v),String(-(x*x)-b),String(x*x+b),String(-v)];
        return mc(`Evaluate ${math(`x^2-${b}`)} when ${math(`x=${x}`)}.`,choices,0,'Square the grouped negative input first.');
      case 'U1-MG03-IC01-H':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-6,6,true);
        return inst(`<p>A student evaluates ${math(`${m}x${b>=0?'+':''}${b}`)} by writing ${math(`${m}(${x})${b>=0?'+':''}${b}`)}. What value was substituted for ${math('x')}?</p><div class="response-surface">x = _____</div>`,String(x),'Read the value that replaced x.');
      case 'U1-MG03-IC01-I':
        m=pick([2,3,4]);x=ri(-5,5,true);correct=`${m}(${x})^2-(${x})`;
        return mc(`Which setup correctly evaluates ${math(`${m}x^2-x`)} when ${math(`x=${x}`)}?`,[math(correct),math(`${m}(${x})^2-x`),math(`${m}(${Math.abs(x)})^2-(${x})`),math(`${m}(${x}^2)-${Math.abs(x)}`)],0,'Replace every occurrence of x.');
      case 'U1-MG03-IC01-J':
        m=pick([2,3,4,5]);x=ri(-4,5,true);
        return inst(`<p>For ${math(`${m}x+x^2`)} when ${math(`x=${x}`)}, a student writes ${math(`${m}(${x})+x^2`)}. Explain the error and correct the setup.</p><div class="response-surface">Explain:</div>`,`The second x was not replaced. The correct setup is ${m}(${x})+(${x})^2.`,'Every occurrence of the variable must be replaced.');

      case 'U1-MG03-IC02-A':
        a=ri(12,24);m=pick([2,3,4]);x=ri(2,5);k=pick([2,3]);v=a-m*x+(2**k);
        return inst(`<p>Evaluate ${math(`${a}-${m}(${x})+2^${k}`)}.</p><div class="response-surface">Value: ______</div>`,String(v),'Use order of operations.');
      case 'U1-MG03-IC02-B':
        a=ri(2,5);b=ri(2,5);m=pick([2,3,4]);n=pick([2,3,4]);k=pick([2,3]);c=(m*(a+b)+n);let den=(k*k+2);while(c%den!==0){n++;c=m*(a+b)+n}v=c/den;
        return inst(`<p>Evaluate ${math(`\\frac{${m}(${a}+${b})+${n}}{${k}^2+2}`)}.</p><div class="response-surface">Show the numerator and denominator values.</div>`,String(v),'Simplify numerator and denominator, then divide.');
      case 'U1-MG03-IC02-C':
        a=ri(5,9);m=pick([2,3,4]);b=ri(5,8);c=ri(1,4);v=a+m*(b-c);
        return inst(`<p>A student evaluates ${math(`${a}+${m}(${b}-${c})`)} as follows:</p><p>${math(`${a}+${m}(${b-c})=${a+m}(${b-c})=${(a+m)*(b-c)}`)}</p><p>Identify the first error and give the correct value.</p><div class="response-surface">First error + correction:</div>`,`The first error is adding ${a}+${m} before multiplying; the correct value is ${v}.`,'Multiplication comes before the outside addition.');
      case 'U1-MG03-IC02-D':
        a=ri(10,20);m=pick([2,3]);b=ri(2,6);c=ri(1,4);k=2;
        return inst(`<p>What should you do first in ${math(`${a}-${m}(${b}+${c})^${k}`)}?</p><div class="response-surface">First step: _____</div>`,`Add ${b}+${c}.`,'Do the innermost grouping first.');
      case 'U1-MG03-IC02-E':
        a=ri(14,24);m=pick([2,3]);b=pick([2,3,4]);c=ri(1,6);v=a-m*(b**2)+c;
        return mc(`Evaluate ${math(`${a}-${m}(${b}^2)+${c}`)}.`,[String(v),String((a-m)*(b**2)+c),String(a-m*b+c),String(a-m*(b+c)**2)],0,'Apply exponents before multiplication and subtraction.');
      case 'U1-MG03-IC02-F':
        a=ri(6,10);b=ri(1,4);c=pick([4,6,8]);
        return inst(`<p>After simplifying the parentheses in ${math(`(${a}-${b})^2+${c}\\div2`)}, what expression remains?</p><div class="response-surface">Next expression: _____</div>`,`${a-b}^2+${c}÷2`,'Replace the grouped expression by its value.');
      case 'U1-MG03-IC02-G':
        a=ri(5,9);m=pick([2,3,4]);b=ri(4,7);c=ri(1,3);correct=`${a}+${m}(${b-c})`;
        return mc(`Which is a correct first step for ${math(`${a}+${m}(${b}-${c})`)}?`,[math(correct),math(`${a+m}(${b}-${c})`),math(`${a}+${m*b}-${c}`),math(`${a*m}(${b}-${c})`)],0,'Simplify the parentheses first.');
      case 'U1-MG03-IC02-H':
        a=ri(2,5);b=ri(2,5);c=ri(1,3);m=pick([2,3]);v=m*((a**2)+(b-c));
        return inst(`<p>Evaluate ${math(`${m}[${a}^2+(${b}-${c})]`)}.</p><div class="response-surface">Value: _____</div>`,String(v),'Follow grouping and exponent rules.');
      case 'U1-MG03-IC02-I':
        a=pick([18,24,30,36,42]);b=pick([2,3,6]);c=pick([2,3,4]);v=(a/b)*c;
        return inst(`<p>Evaluate ${math(`${a}\\div${b}\\cdot${c}`)} from left to right.</p><div class="response-surface">Value: _____</div>`,String(v),'Multiplication and division have equal priority, so work left to right.');
      case 'U1-MG03-IC02-J':
        a=ri(2,5);b=ri(1,4);m=pick([2,3,4]);v=m*((a+b)**2);const wrongOrder=(m*(a+b))**2;
        return inst(`<p>A student evaluates ${math(`${m}(${a}+${b})^2`)} as ${math(`${m*(a+b)}^2=${wrongOrder}`)}. Explain the first error and give the correct value.</p><div class="response-surface">Explain:</div>`,`After ${a}+${b}=${a+b}, square ${a+b} before multiplying by ${m}. The correct value is ${v}.`,'The exponent applies before the outside multiplication.');

      case 'U1-MG03-IC03-A':
        a=-ri(3,8);m=pick([2,3,4]);b=-ri(2,6);c=-ri(2,7);v=a+m*b-c;
        return inst(`<p>Evaluate ${math(`${a}+${m}(${b})-(${c})`)}.</p><div class="response-surface">Value: ______</div>`,String(v),'Evaluate multiplication and signed addition/subtraction.');
      case 'U1-MG03-IC03-B':
        m=pick([2,3,4]);n=pick([2,3,4]);a=-ri(2,6);b=ri(2,6);v=m*a-n*b;
        return inst(`<p>Evaluate ${math(`${m}a-${n}b`)} when ${math(`a=${a}`)} and ${math(`b=${b}`)}.</p><div class="response-surface">Substitution + value:</div>`,String(v),'Substitute both signed values carefully.');
      case 'U1-MG03-IC03-C':
        a=ri(2,7);return inst(`<p>Evaluate both ${math(`-${a}^2`)} and ${math(`(-${a})^2`)}. Explain why the answers are different.</p><div class="response-surface">Values + explanation:</div>`,`-${a*a} and ${a*a}`,'Without parentheses, the exponent applies before the leading negative.');
      case 'U1-MG03-IC03-D':
        a=-ri(4,9);m=pick([2,3,4]);b=-ri(2,6);v=a+m*b;
        return mc(`Evaluate ${math(`${a}+${m}(${b})`)}.`,[String(v),String(-v),String(a-m*b),String(Math.abs(v))],0,'Multiply first, then combine signed values.');
      case 'U1-MG03-IC03-E':
        a=ri(-9,9);b=ri(2,9);return inst(`<p>Complete the rewrite:</p><p>${math(`${a}-(-${b})=${a}\\;\\square\\;${b}`)}</p>`,'+','Subtracting a negative becomes addition.');
      case 'U1-MG03-IC03-F':
        a=ri(2,6);b=ri(2,7);c=ri(2,6);k=ri(2,7);const v1=(-a)*b,v2=c*(-k);return inst(`<p>Which is greater: ${math(`-${a}(${b})`)} or ${math(`${c}(-${k})`)}?</p><div class="response-surface">Greater expression: _____</div>`,v1>v2?`-${a}(${b}), because ${v1} > ${v2}.`:`${c}(-${k}), because ${v2} > ${v1}.`,'Evaluate both expressions, then compare.');
      case 'U1-MG03-IC03-G':
        m=-pick([2,3,4]);x=-ri(2,5);v=m*(x*x);return inst(`<p>Evaluate ${math(`${m}x^2`)} when ${math(`x=${x}`)}.</p><div class="response-surface">Value: _____</div>`,String(v),'Substitute with parentheses, square, then multiply by the coefficient.');
      case 'U1-MG03-IC03-H':
        a=ri(-6,8);b=-ri(2,9);v=a-b;return mc(`Evaluate ${math(`${a}-(${b})`)}.`,[String(v),String(a+b),String(-v),String(Math.abs(a)-Math.abs(b))],0,'Subtracting a negative is addition.');
      case 'U1-MG03-IC03-I':
        a=-ri(2,6);b=-ri(2,6);c=-ri(1,6);v=a*b+c;return inst(`<p>Before calculating, predict whether ${math(`(${a})(${b})+(${c})`)} is positive or negative. Then evaluate it.</p><div class="response-surface">Prediction + value:</div>`,`${v>0?'Positive':'Negative'}; ${v}.`,'Use sign rules first, then evaluate.');
      case 'U1-MG03-IC03-J':
        a=ri(3,12);return inst(`<p>A student says ${math(`-(-${a})=-${a}`)}. Explain the sign error and give the correct value.</p><div class="response-surface">Explain:</div>`,`${math(`-(-${a})`)} means the opposite of -${a}, so it equals ${a}.`,'The opposite of a negative is positive.');

      case 'U1-MG03-IC04-A':
        a=pick([19.7,19.8,20.1,20.2]);b=pick([14.8,14.9,15.1,15.2]);c=pick([58,62,64]);v=a*b+c;const claim=Math.round(v);return inst(`<p>Without redoing every step exactly, decide whether ${claim} is a reasonable value for ${math(`${a}(${b})+${c}`)}. Support your decision with an estimate.</p><div class="response-surface">Estimate + judgment:</div>`,`Yes; about 20·15+60=360, so ${claim} is reasonable.`,'Use nearby friendly numbers.');
      case 'U1-MG03-IC04-B':
        n=ri(5,9);a=pick([2.5,2.75,3.25,3.5]);v=n*a;const absurd=Math.round(v*10);return inst(`<p>A student calculates that ${n} notebooks costing ${money(a)} each will cost $${absurd}. Is that reasonable? Give a quick check, not a full written multiplication algorithm.</p><div class="response-surface">Check:</div>`,`No; ${n} notebooks at about $${Math.round(a)} each should cost about $${n*Math.round(a)}, not $${absurd}.`,'Use a nearby whole-dollar estimate.');
      case 'U1-MG03-IC04-C':
        a=pick([38.2,42.6,48.2,52.4]);b=pick([0.49,0.51,0.52]);v=a*b;const wrongScale=Math.round(v*1000)/10;return inst(`<p>A student reports ${math(`${a}(${b})=${wrongScale}`)}. Without doing the exact multiplication first, explain why the result cannot be correct. Then state a reasonable approximate result.</p><div class="response-surface">Reasoning:</div>`,`It should be about ${Math.round(a/2)}, because multiplying by about 0.5 should roughly halve ${a}.`,'Estimate the multiplier as about one-half.');
      case 'U1-MG03-IC04-D':
        a=pick([41.2,51.2,61.3]);b=pick([3.8,3.9,4.1]);v=a*b;const mag=Math.pow(10,Math.round(Math.log10(v)));choices=[mag/10,mag,mag*10,mag*100].map(x=>x.toLocaleString('en-US'));
        return mc(`Without calculating exactly, which is a reasonable value for ${math(`${a}(${b})`)}?`,choices,1,'Estimate with nearby whole numbers and choose the matching magnitude.');
      case 'U1-MG03-IC04-E':
        a=pick([19.7,29.7,39.6]);b=pick([4.2,5.8,6.2]);c=pick([10,15,20]);const est=Math.round(a/10)*10*Math.round(b)+c;
        return inst(`<p>Estimate ${math(`${a}(${b})+${c}`)} using friendly numbers.</p><div class="response-surface">Estimate: _____</div>`,`About ${est}; for example ${Math.round(a/10)*10}·${Math.round(b)}+${c}=${est}.`,'Use nearby friendly numbers.');
      case 'U1-MG03-IC04-F':
        a=pick([4.8,5.1,6.2]);b=pick([2.1,2.9,3.2]);v=a*b;const wrongDecimal=Math.round(v*10)*10/1;
        return inst(`<p>A student reports ${math(`${a}(${b})=${wrongDecimal}`)}. Explain why the result is not reasonable using an estimate.</p><div class="response-surface">Explain:</div>`,`${a}≈${Math.round(a)} and ${b}≈${Math.round(b)}, so the product should be about ${Math.round(a)*Math.round(b)}, not about ${wrongDecimal}.`,'Compare the reported magnitude to an estimate.');
      case 'U1-MG03-IC04-G':
        a=pick([392,398,404,408]);b=pick([8,10]);v=a/b;return inst(`<p>Two students get ${v} and ${v*10} for ${math(`${a}\\div${b}`)}. Which answer is more reasonable? Explain with an estimate.</p><div class="response-surface">Answer:</div>`,`${v}, because ${Math.round(a/10)*10}÷${b} is about ${Math.round(v)}.`,'Estimate the quotient to compare magnitudes.');
      case 'U1-MG03-IC04-H':
        a=-ri(8,16);m=pick([2,3,4]);b=-ri(3,8);v=a+m*b;return inst(`<p>A student says ${math(`${a}+${m}(${b})=${Math.abs(v)}`)}. Is the sign reasonable? Explain.</p><div class="response-surface">Answer:</div>`,`No. Both terms are negative, so the sum must be negative; the exact value is ${v}.`,'Use operation signs before exact arithmetic.');
      case 'U1-MG03-IC04-I':
        n=ri(5,9);a=ri(3,6);b=a+1;const low=n*a,high=n*b,claimBounds=high+ri(5,20);return inst(`<p>${n} items each cost between $${a} and $${b}. Could the total be $${claimBounds}? Explain with bounds.</p><div class="response-surface">Answer:</div>`,`No. The total must be between $${low} and $${high}.`,'Multiply the item count by the low and high unit prices.');
      case 'U1-MG03-IC04-J':
        b=pick([4,5,8,10]);n=ri(5,12);a2=b*n;a=Number((a2+pick([-0.9,-0.4,0.3,0.7])).toFixed(1));const b2=b;const bdec=Number((b2+pick([-0.2,-0.1,0.1,0.2])).toFixed(1));return inst(`<p>Use compatible numbers: ${math(`${a}\\approx${a2}`)} and ${math(`${bdec}\\approx${b2}`)}, so ${math(`${a}\\div${bdec}`)} is about <b>_____</b>.</p>`,String(n),'Divide the compatible numbers.');
    }
    return null;
  }

  function g04(fid,f){
    let a,b,c,x,y,m,n,v,x1,x2,y1,y2,student,rows,correct,choices;
    switch(fid){
      case 'U1-MG04-IC01-A':
        m=pick([2,3,4,-2,-3]);b=ri(-4,5);const xsInput=[-4,-1,2,5,8],rs=xsInput.map(t=>[t,m*t+b]);x=pick(xsInput.slice(1,4));
        return inst(`<p>Use the table. Write the ordered pair for the row with input ${math(String(x))}.</p>${table(rs,'Input','Output')}<div class="response-surface">Ordered pair: ______</div>`,`(${x}, ${m*x+b})`,'Read input first and output second.');
      case 'U1-MG04-IC01-B':
        x=ri(2,8);y=ri(10,30);return inst(`<p>A machine takes ${x} minutes of run time as an input and produces ${y} parts as an output. Write the ordered pair and explain what each coordinate represents.</p><div class="response-surface">Pair + meaning:</div>`,`(${x},${y}); ${x} is minutes input and ${y} is parts output.`,'Input is the first coordinate; output is the second.');
      case 'U1-MG04-IC01-C':
        x=ri(-6,7,true);y=ri(-6,10,true);return inst(`<p>A table row shows input ${x} and output ${y}. A student records the ordered pair as ${math(`(${y},${x})`)}.</p><p>Explain the error and write the correct ordered pair.</p><div class="response-surface">Diagnosis:</div>`,`(${x},${y}); the student wrote output first instead of input first.`,'Ordered pairs use (input, output).');
      case 'U1-MG04-IC01-D':
        m=pick([2,3,-2,-3]);b=ri(-4,4);const xs2=[-2,0,3,5,7],rs2=xs2.map(t=>[t,m*t+b]);x=3;y=m*x+b;return mc(`Use the table. Which ordered pair matches input ${x}?${table(rs2,'Input','Output')}`,[math(`(${x},${y})`),math(`(${y},${x})`),math(`(${x},${-y})`),math(`(0,${x})`)],0,'Use the row whose input is the requested value.');
      case 'U1-MG04-IC01-E':
        x=ri(-8,8,true);y=ri(-8,10,true);return inst(`<p>For the ordered pair ${math(`(${x},${y})`)}, what is the input and what is the output?</p><div class="response-surface">Input: _____ &nbsp; Output: _____</div>`,`Input = ${x}; output = ${y}.`,'First coordinate is input; second is output.');
      case 'U1-MG04-IC01-F':
        x=ri(-4,8);y=ri(-4,12);return inst(`<p>An output of ${y} is produced when ${x} is used as the input. Write this information as an ordered pair.</p><div class="response-surface">Ordered pair: ______</div>`,`(${x},${y})`,'Write input first, output second.');
      case 'U1-MG04-IC01-G':
        m=pick([2,3,4,5]);b=ri(1,9);return inst(`<p>In ${math(`C=${m}t+${b}`)}, identify the input variable and the output variable.</p><div class="response-surface">Input: _____ &nbsp; Output: _____</div>`,'Input = t; output = C.','The output variable is isolated and depends on the input variable.');
      case 'U1-MG04-IC01-H':
        m=pick([2,3,4,5]);b=ri(1,9);return mc(`The equation ${math(`C=${m}t+${b}`)} models cost ${math('C')} from time ${math('t')}. Which statement is correct?`,['Input: t; output: C','Input: C; output: t',`Input: ${m}; output: ${b}`,`Input: ${b}; output: ${m}`],0,'t is the independent/input variable and C is the output.');
      case 'U1-MG04-IC01-I':
      case 'U1-MG04-IC01-J':
        return staticEx(f);

      case 'U1-MG04-IC02-A':
        m=pick([-5,-4,-3,2,3,4,5]);b=ri(-6,6);x=ri(-5,7);y=m*x+b;return inst(`<p>The rule is ${math(lin(m,b))}. Find the output when the input is ${math(`x=${x}`)}.</p><div class="response-surface">Output: ______</div>`,String(y),'Substitute the input into the rule.');
      case 'U1-MG04-IC02-B':
        m=pick([2,3,4,5]);b=ri(1,6);x=ri(2,8);y=m*x-b;return inst(`<p>A rule says: “Multiply the input by ${m}, then subtract ${b}.” Write a rule using x and y, then find the output for input ${x}.</p><div class="response-surface">Rule + output:</div>`,`${math(`y=${m}x-${b}`)}; output ${y}.`,'Translate the verbal operations in order.');
      case 'U1-MG04-IC02-C':
        a=ri(2,6);m=pick([2,3,4]);return inst(`<p>The rule says, “Add ${a} to the input, then multiply the result by ${m}.” A student writes ${math(`y=${m}x+${a}`)}. Explain the error and write a correct rule.</p><div class="response-surface">Diagnosis + rule:</div>`,`${math(`y=${m}(x+${a})`)}, or ${math(`y=${m}x+${m*a}`)}.`,'The addition happens before the multiplication.');
      case 'U1-MG04-IC02-D':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,6);x=ri(-4,7);y=m*x+b;return mc(`For ${math(lin(m,b))}, what is the output when ${math(`x=${x}`)}?`,[String(y),String(m+x+b),String(m*x),String(y+pick([-3,-2,2,3]))],0,'Substitute x and evaluate.');
      case 'U1-MG04-IC02-E':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-4,6);x=-ri(1,6);y=m*x+b;return inst(`<p>Use ${math(lin(m,b))}. Find the output when ${math(`x=${x}`)}.</p><div class="response-surface">Output: _____</div>`,String(y),'Substitute the negative input carefully.');
      case 'U1-MG04-IC02-F':
        m=pick([2,3,4,5]);b=ri(-6,6);x=ri(-5,7);y=m*x+b;return inst(`<p>For ${math(lin(m,b))} and ${math(`x=${x}`)}, complete the substitution and find y:</p><p>${math(`y=${m}(\\square)${b>=0?'+':''}${b}=\\square`)}</p>`,`${x}; ${y}`,'First blank is the input; second is the resulting output.');
      case 'U1-MG04-IC02-G':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x=ri(-4,7);y=m*x+b;return inst(`<p>Use ${math(lin(m,b))} to complete the table row.</p>${table([[x,'?']])}<div class="response-surface">Output: _____</div>`,String(y),'Evaluate the rule at the table input.');
      case 'U1-MG04-IC02-H':
        m=pick([2,3,4]);b=ri(1,6);x=ri(2,7);y=m*x+b;return mc(`Rule: Multiply the input by ${m}, then add ${b}. What output comes from input ${x}?`,[String(y),String((x+b)*m),String(m*x),String(x+b)],0,'Apply the operations in the stated order.');
      case 'U1-MG04-IC02-I':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x1=ri(-3,2);x2=x1+pick([2,3,4]);y1=m*x1+b;y2=m*x2+b;return inst(`<p>Use ${math(lin(m,b))}. Find the outputs for ${math(`x=${x1}`)} and ${math(`x=${x2}`)}.</p><div class="response-surface">Outputs: _____ , _____</div>`,`${y1}, ${y2}`,'Evaluate the rule separately for each input.');
      case 'U1-MG04-IC02-J':
        m=pick([2,3,4,5]);b=ri(1,6);x=ri(2,6);y=m*x-b;student=pick(NAMES);return inst(`<p>For ${math(`y=${m}x-${b}`)} and ${math(`x=${x}`)}, ${student} writes ${math(`${m}+${x}-${b}=${m+x-b}`)}. Explain the error and find the correct output.</p><div class="response-surface">Explain:</div>`,`${m}x means ${m} times x, not ${m}+x. The output is ${m}(${x})-${b}=${y}.`,'Use multiplication for the coefficient.');

      case 'U1-MG04-IC03-A':
        b=ri(-5,5);x=ri(-4,4,true);y=x*x+b;return inst(`<p>Use the rule ${math(`y=x^2${b>=0?'+':''}${b}`)} to find the corresponding output for ${math(`x=${x}`)}.</p>${table([[x,'?']])}<div class="response-surface">Corresponding output: ______</div>`,String(y),'Substitute the input into the quadratic rule.');
      case 'U1-MG04-IC03-B':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-5,7);y=m*x+b;return inst(`<p>The rule is ${math(lin(m,b))}. What input produces an output of ${y}?</p><div class="response-surface">Input: ______</div>`,String(x),'Set the rule equal to the output and solve for x.');
      case 'U1-MG04-IC03-C':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-5,7);y=m*x+b;return inst(`<p>Use ${math(lin(m,b))}. What input produces an output of ${math(String(y))}?</p><div class="response-surface">Input: ______</div>`,String(x),'Solve the linear rule for the input.');
      case 'U1-MG04-IC03-D':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x=ri(-4,7);y=m*x+b;return mc(`Use ${math(lin(m,b))}. Find the corresponding output when ${math(`x=${x}`)}.`,[String(y),String(m+x+b),String(m*x),String(y+pick([-3,-2,2,3]))],0,'Evaluate the rule at the stated input.');
      case 'U1-MG04-IC03-E':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-4,7);y=m*x+b;return mc(`For ${math(lin(m,b))}, which input gives an output of ${y}?`,[String(x),String(x+1),String(x-1),String(y)],0,'Solve the rule equation for x.');
      case 'U1-MG04-IC03-F':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-4,7);y=m*x+b;return inst(`<p>Use ${math(lin(m,b))} to complete the ordered pair ${math(`(\\square,${y})`)}.</p><div class="response-surface">Input: _____</div>`,String(x),'Solve for x, then use it as the first coordinate.');
      case 'U1-MG04-IC03-G':
        m=pick([3,4,5,6]);b=pick([4,6,8,10]);x=ri(2,6);y=m*x+b;return inst(`<p>A bike rental costs ${math(`C=${m}h+${b}`)}, where ${math('h')} is the number of hours and ${math('C')} is the cost in dollars. Find the cost for ${x} hours.</p><div class="response-surface">Cost: $_____</div>`,`$${y}`,'Evaluate the linear context rule.');
      case 'U1-MG04-IC03-H':
        m=pick([2,3,4]);b=ri(1,5);x=ri(2,7);y=m*x+b;return inst(`<p>Rule: Multiply the input by ${m}, then add ${b}. The output is ${y}. What was the input?</p><div class="response-surface">Input: _____</div>`,String(x),'Undo the operations in reverse order.');
      case 'U1-MG04-IC03-I':
        n=pick([2,3,4]);b=ri(1,6);x=n*ri(1,6);y=x/n+b;return inst(`<p>For ${math(`y=\\frac{x}{${n}}+${b}`)}, what input gives an output of ${y}?</p><div class="response-surface">Input: _____</div>`,String(x),'Subtract the constant, then multiply by the denominator.');
      case 'U1-MG04-IC03-J':
        m=pick([2,3,4,5]);b=ri(-5,5);x=ri(-3,5);y=m*x+b;x2=ri(-3,6);y2=m*x2+b;return inst(`<p>Use ${math(lin(m,b))}:</p><p>When ${math(`x=${x}`)}, ${math('y=')} <b>_____</b>.<br>When ${math(`y=${y2}`)}, ${math('x=')} <b>_____</b>.</p>`,`${y}; ${x2}`,'Evaluate forward for the first blank and solve backward for the second.');

      case 'U1-MG04-IC04-A':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);const xsTable=[-2,0,3],ys=xsTable.map(t=>'?');const ans=xsTable.map(t=>m*t+b);return inst(`<p>Use ${math(lin(m,b))} to complete the table.</p>${horizTable(xsTable,ys)}<div class="response-surface">Complete all outputs.</div>`,ans.join(', '),'Evaluate the rule at each input.');
      case 'U1-MG04-IC04-B':
        m=pick([3,4,5,6]);b=pick([5,6,8,10]);const hrs=[0,2,5],costs=hrs.map(t=>'?'),ansc=hrs.map(t=>`$${m*t+b}`);return inst(`<p>A bike rental costs $${b} to start plus $${m} per hour. Complete the table.</p>${horizTable(hrs,costs,'Hours','Cost ($)')}<div class="response-surface">Complete the costs.</div>`,ansc.join(', '),'Use cost = starting fee + hourly rate × hours.');
      case 'U1-MG04-IC04-C':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-4,5);const xs3=[0,2,4],good=xs3.map(t=>m*t+b),badIndex=ri(0,2),shown=good.slice();shown[badIndex]+=pick([-2,-1,1,2]);return inst(`<p>The rule is ${math(lin(m,b))}.</p>${table(xs3.map((t,i)=>[t,shown[i]]))}<p>One row is wrong. Correct it.</p><div class="response-surface">Correction:</div>`,`For x=${xs3[badIndex]}, y=${good[badIndex]}.`,'Evaluate the rule at each displayed input.');
      case 'U1-MG04-IC04-D':
        m=pick([-3,-2,2,3,4]);b=ri(-4,5);x1=ri(-2,2);x2=x1+1;return inst(`<p>Use ${math(lin(m,b))}. Add the next two rows to the table.</p>${table([[x1,m*x1+b],[x2,m*x2+b]])}<div class="response-surface">Add two rows:</div>`,`(${x2+1},${m*(x2+1)+b}) and (${x2+2},${m*(x2+2)+b})`,'Continue with the next consecutive inputs.');
      case 'U1-MG04-IC04-E':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x1=ri(-1,1);rows=[0,1,2,3].map(t=>[x1+t,t===3?'?':m*(x1+t)+b]);return inst(`<p>Use ${math(lin(m,b))} to complete the next row of the table.</p>${table(rows)}`,String(m*(x1+3)+b),'Evaluate the rule at the final input.');
      case 'U1-MG04-IC04-F':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x=ri(-4,6);y=m*x+b;return mc(`Which ordered pair matches the rule ${math(lin(m,b))}?`,[math(`(${x},${y})`),math(`(${x},${m+x+b})`),math(`(${y},${x})`),math(`(${x},${-y})`)],0,'Substitute x and identify the matching output.');
      case 'U1-MG04-IC04-G':
        m=pick([1,2,3]);b=ri(3,8);x1=-ri(1,3);x2=ri(2,5);return inst(`<p>Use ${math(`y=${b}-${m===1?'x':`${m}x`}`)} to fill both outputs.</p>${table([[x1,'?'],[x2,'?']])}`,`${b-m*x1}; ${b-m*x2}`,'Evaluate the decreasing rule for both inputs.');
      case 'U1-MG04-IC04-H':
        m=pick([2,3,4]);b=ri(-4,5);const xs4=[-1,0,2],ys4=xs4.map(()=>'?'),answers=xs4.map(t=>m*t+b);return inst(`<p>Rule: Multiply the input by ${m}, then ${b>=0?'add':'subtract'} ${Math.abs(b)}. Complete the table.</p>${horizTable(xs4,ys4)}`,answers.join(', '),'Apply the verbal rule to each input.');
      case 'U1-MG04-IC04-I':
        m=pick([-3,-2,1,2,3]);b=ri(-4,5);return inst(`<p>Use ${math(lin(m,b))}. Choose two different integer inputs and write two correct input-output rows.</p>${table([['_____','_____'],['_____','_____']])}`,'Answers vary; any two rows satisfying the rule are correct.','Choose any two integer inputs and evaluate the rule.');
      case 'U1-MG04-IC04-J':
        m=pick([-3,-2,2,3]);b=ri(-4,6);const mid=[1,2,3];return inst(`<p>Use ${math(lin(m,b))}. Add the rows for ${math('x=0')} and ${math('x=4')}.</p>${table(mid.map(t=>[t,m*t+b]))}<div class="response-surface">New rows:</div>`,`(0,${b}) and (4,${4*m+b})`,'Evaluate the rule at the inputs just before and after the displayed range.');
      case 'U1-MG04-IC04-K':
        m=pick([-4,-3,-2,2,3,4]);b=ri(-5,5);x1=ri(-3,3);x2=x1+2;const missing=x1+1;const known=[x1-2,x1-1,x1,x2].map(t=>[t,m*t+b]);return inst(`<p>Use ${math(lin(m,b))}. Add the missing row between inputs ${x1} and ${x2}.</p>${table(known)}<div class="response-surface">Missing row: _____</div>`,`(${missing}, ${m*missing+b})`,'The missing input is halfway between the two consecutive-gap endpoints.');
    }
    return null;
  }

  function generate(family){
    const fid=String(family?.family_id||'');
    if(fid.startsWith('U1-MG03-'))return g03(fid,family);
    if(fid.startsWith('U1-MG04-'))return g04(fid,family);
    return prior?.generate?.(family)||null;
  }
  function supports(fid){
    fid=String(fid||'');
    return Boolean(prior?.supports?.(fid)||/^U1-MG03-IC0[1-4]-[A-J]$/.test(fid)||/^U1-MG04-IC0[1-3]-[A-J]$/.test(fid)||/^U1-MG04-IC04-[A-K]$/.test(fid));
  }
  window.AssessmentGeneration={supports,generate};
})();
