(function(){
  "use strict";
  function $(id){return document.getElementById(id)}
  function num(v,d){var n=Number(v);return Number.isFinite(n)?n:d}
  function clone(el){return el.cloneNode(true)}
  function page(stack,n,extra){
    var p=document.createElement('section');p.className='runtime-letter-page'+(extra?' '+extra:'');p.dataset.page=String(n);
    var inner=document.createElement('div');inner.className='runtime-letter-inner';p.appendChild(inner);
    var pn=document.createElement('div');pn.className='runtime-page-number';pn.textContent='Page '+n;p.appendChild(pn);stack.appendChild(p);return {page:p,inner:inner};
  }
  function overflow(inner){return inner.scrollHeight>inner.clientHeight+2 || inner.scrollWidth>inner.clientWidth+2}
  function applyScale(root,ws,vis){root.style.setProperty('--runtime-workspace-scale',String(ws));root.style.setProperty('--runtime-visual-scale',String(vis))}
  function selectedProblem(){var s=$('runtimeProblem');return s?s.value:'all'}
  function effectiveWorkspace(block,allScale,oneScale){return selectedProblem()==='all'||selectedProblem()===block.dataset.problem?allScale*oneScale:allScale}
  function populateProblemSelect(source){var s=$('runtimeProblem');if(!s)return;s.innerHTML='<option value="all">All</option>';source.querySelectorAll('[data-problem]').forEach(function(el){var o=document.createElement('option');o.value=el.dataset.problem;o.textContent=el.dataset.problem;s.appendChild(o)})}
  function paginateSegment(segment,stack,pageNo,duplex){
    var startPageNo=pageNo;
    var header=segment.querySelector('.runtime-flow-header');var blocks=[].slice.call(segment.querySelectorAll(':scope > .runtime-flow-block'));
    var layout=segment.dataset.layout||'list';var p=page(stack,pageNo++);var inner=p.inner;
    if(header)inner.appendChild(clone(header));
    var holder=document.createElement('div');holder.className=layout==='grid2'?'runtime-common-grid':'runtime-practice-list';inner.appendChild(holder);
    var allScale=num($('runtimeAll')&&$('runtimeAll').value,100)/100;
    var oneScale=num($('runtimeOne')&&$('runtimeOne').value,100)/100;
    var visScale=num($('runtimeVisual')&&$('runtimeVisual').value,100)/100;
    blocks.forEach(function(src){
      var b=clone(src);b.style.setProperty('--runtime-workspace-scale',String(effectiveWorkspace(src,allScale,oneScale)));b.style.setProperty('--runtime-visual-scale',String(visScale));holder.appendChild(b);
      if(overflow(inner)){
        holder.removeChild(b);
        p=page(stack,pageNo++);inner=p.inner;holder=document.createElement('div');holder.className=layout==='grid2'?'runtime-common-grid':'runtime-practice-list';inner.appendChild(holder);holder.appendChild(b);
      }
    });
    var pagesMade=pageNo-startPageNo;
    if(duplex && pagesMade%2===1){page(stack,pageNo++,'runtime-duplex-blank')}
    return pageNo;
  }
  function repaginate(){
    var source=$('runtimeFlowSource'),stack=$('runtimePageStack');if(!source||!stack)return;stack.innerHTML='';var pageNo=1;
    var segments=[].slice.call(source.querySelectorAll(':scope > .runtime-flow-segment'));if(!segments.length)segments=[source];
    segments.forEach(function(seg){pageNo=paginateSegment(seg,stack,pageNo,source.dataset.duplex==='true')});
  }
  function updateOutputs(){
    [['runtimeAll','runtimeAllOut'],['runtimeOne','runtimeOneOut'],['runtimeVisual','runtimeVisualOut']].forEach(function(pair){var i=$(pair[0]),o=$(pair[1]);if(i&&o)o.textContent=i.value+'%'})
  }
  function bindFlow(){var source=$('runtimeFlowSource');if(!source)return;populateProblemSelect(source);['runtimeAll','runtimeOne','runtimeVisual','runtimeProblem'].forEach(function(id){var el=$(id);if(el)el.addEventListener('input',function(){updateOutputs();repaginate()})});var reset=$('runtimeReset');if(reset)reset.addEventListener('click',function(){if($('runtimeAll'))$('runtimeAll').value=100;if($('runtimeOne'))$('runtimeOne').value=100;if($('runtimeVisual'))$('runtimeVisual').value=100;if($('runtimeProblem'))$('runtimeProblem').value='all';updateOutputs();repaginate()});var pr=$('runtimePrint');if(pr)pr.addEventListener('click',function(){window.print()});updateOutputs();repaginate();setTimeout(repaginate,150);setTimeout(repaginate,650)}
  function bindSet(){var root=$('runtimeSetStack');if(!root)return;['runtimeAll','runtimeOne','runtimeVisual','runtimeProblem'].forEach(function(id){var el=$(id);if(el)el.addEventListener('input',function(){updateOutputs();applySet()})});var reset=$('runtimeReset');if(reset)reset.addEventListener('click',function(){if($('runtimeAll'))$('runtimeAll').value=100;if($('runtimeOne'))$('runtimeOne').value=100;if($('runtimeVisual'))$('runtimeVisual').value=100;if($('runtimeProblem'))$('runtimeProblem').value='all';updateOutputs();applySet()});var pr=$('runtimePrint');if(pr)pr.addEventListener('click',function(){window.print()});updateOutputs();applySet()}
  function applySet(){var all=num($('runtimeAll')&&$('runtimeAll').value,100)/100,one=num($('runtimeOne')&&$('runtimeOne').value,100)/100,vis=num($('runtimeVisual')&&$('runtimeVisual').value,100)/100,sel=selectedProblem();document.querySelectorAll('.runtime-set-page').forEach(function(p){var scale=(sel==='all'||sel===p.dataset.problem)?all*one:all;applyScale(p,scale,vis)})}
  function init(){bindFlow();bindSet();if(window.MathJax&&window.MathJax.startup&&window.MathJax.startup.promise){window.MathJax.startup.promise.then(function(){repaginate();applySet()}).catch(function(){})}}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
  window.GradingResponseRuntime={repaginate:repaginate,applySet:applySet};
})();
