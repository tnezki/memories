(() => {
  function download(url){
    const a=document.createElement('a');
    a.href=url;
    a.style.display='none';
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
  function checkpointPlanId(){
    try{return state.checkpointPlanId||state.checkpointPlan?.plan_id||''}catch(_){return ''}
  }
  function summativePlanId(){
    try{return state.summativePlanId||state.summativePlan?.plan_id||''}catch(_){return ''}
  }
  function replaceClick(id,handler){
    const old=document.getElementById(id); if(!old)return;
    const fresh=old.cloneNode(true); old.replaceWith(fresh); fresh.addEventListener('click',handler);
  }
  function bindDirectRequestDownloads(){
    replaceClick('saveExtensionRequestBtn',()=>{
      const plan=checkpointPlanId();
      if(!plan){ if(typeof setCheckpointStatus==='function')setCheckpointStatus('Analyze selected evidence first.','warn'); return; }
      download(`/api/checkpoint/request.zip?plan_id=${encodeURIComponent(plan)}`);
      if(typeof setCheckpointStatus==='function')setCheckpointStatus('AI request downloaded. Upload that ZIP to Curriculum Build, then use Load Returned Families after the result is applied.','good');
    });
    replaceClick('saveSummativeRequestBtn',()=>{
      const plan=summativePlanId();
      if(!plan){ if(typeof setSummativeStatus==='function')setSummativeStatus('Analyze selected evidence first.','warn'); return; }
      download(`/api/summative/request.zip?plan_id=${encodeURIComponent(plan)}`);
      if(typeof setSummativeStatus==='function')setSummativeStatus('Summative AI request downloaded. Upload that ZIP to Curriculum Build, then use Load Returned Families after the result is applied.','good');
    });
  }
  function simplifyLabels(){
    const note=document.querySelector('.course-topbar-note'); if(note)note.textContent='Banks';
    const hero=document.getElementById('heroBankStatus'); if(hero)hero.textContent='Algebra banks + Portfolio';
    const checkpoint=document.querySelector('#checkpointPanel .eyebrow'); if(checkpoint)checkpoint.textContent='CHECKPOINT · PORTFOLIO-AWARE';
    const summative=document.querySelector('#summativePanel .eyebrow'); if(summative)summative.textContent='SUMMATIVE · PORTFOLIO-AWARE';
  }
  function init(){ bindDirectRequestDownloads(); simplifyLabels(); }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
})();
