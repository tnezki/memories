(() => {
  function checkpointPlanId(){
    try{return state.checkpointPlanId||state.checkpointPlan?.plan_id||''}catch(_){return ''}
  }
  function summativePlanId(){
    try{return state.summativePlanId||state.summativePlan?.plan_id||''}catch(_){return ''}
  }

  function picker(kind){
    const input=document.createElement('input');
    input.type='file';
    input.accept='.zip,.json,application/zip,application/json';
    input.style.display='none';
    document.body.appendChild(input);
    input.addEventListener('change',async()=>{
      const file=input.files?.[0];
      input.remove();
      if(file)await upload(kind,file);
    },{once:true});
    input.click();
  }

  async function upload(kind,file){
    const checkpoint=kind==='checkpoint';
    const planId=checkpoint?checkpointPlanId():summativePlanId();
    const setStatus=checkpoint
      ? (typeof setCheckpointStatus==='function'?setCheckpointStatus:null)
      : (typeof setSummativeStatus==='function'?setSummativeStatus:null);
    if(!planId){
      setStatus?.('Analyze selected evidence first so this result can be matched to a plan.','warn');
      return;
    }
    setStatus?.(`Importing ${file.name}…`,'');
    try{
      const endpoint=checkpoint?'/api/checkpoint/import-result':'/api/summative/import-result';
      const r=await fetch(`${endpoint}?plan_id=${encodeURIComponent(planId)}`,{
        method:'POST',
        headers:{
          'Content-Type':file.type||'application/octet-stream',
          'X-Result-Filename':encodeURIComponent(file.name)
        },
        body:file
      });
      const data=await r.json().catch(()=>({}));
      if(!r.ok||!data.ok)throw new Error(data.error||`Import failed (${r.status})`);
      if(checkpoint){
        renderCheckpointPlan(
          data.plan,
          !!data.extensions_ready,
          data.request_url||null,
          data.extension_response||null,
          data.family_review||null,
          data.response_validation||null,
          data.replacement_request_url||null,
          data.assembly||null
        );
        setCheckpointStatus(data.message||'Returned Checkpoint families imported. Review each family below.','good');
      }else{
        renderSummativePlan(
          data.plan,
          !!data.families_ready,
          data.request_url||null,
          data.family_response||null,
          data.family_review||null,
          data.response_validation||null,
          data.replacement_request_url||null,
          data.assembly||null
        );
        setSummativeStatus(data.message||'Returned Summative families imported. Review each family below.','good');
      }
    }catch(err){
      setStatus?.(`Could not import returned families: ${err.message}`,'error');
    }
  }

  function replaceButton(id,kind){
    const old=document.getElementById(id);
    if(!old)return;
    const fresh=old.cloneNode(true);
    old.replaceWith(fresh);
    fresh.addEventListener('click',()=>picker(kind));
  }

  function bind(){
    replaceButton('refreshCheckpointBtn','checkpoint');
    replaceButton('refreshSummativeBtn','summative');
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',()=>setTimeout(bind,0));
  }else{
    setTimeout(bind,0);
  }
})();
