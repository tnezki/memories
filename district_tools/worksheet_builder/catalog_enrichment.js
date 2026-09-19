(() => {
  const baseFetch=window.fetch.bind(window);
  let dataPromise=null;
  const dec64=s=>{const bin=atob(String(s||'').replace(/\s/g,'')),bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);return new TextDecoder('utf-8').decode(bytes);};
  const enc64=s=>{const bytes=new TextEncoder().encode(s);let bin='';const chunk=0x8000;for(let i=0;i<bytes.length;i+=chunk)bin+=String.fromCharCode(...bytes.subarray(i,i+chunk));return btoa(bin);};
  async function localJson(path,fallback){try{const r=await baseFetch(path,{cache:'no-store'});return r.ok?await r.json():fallback;}catch{return fallback;}}
  async function extensionData(){
    if(!dataPromise)dataPromise=Promise.all([
      localJson('algebra1_catalog.json',{courses:[]}),
      localJson('algebra1_family_contracts.json',{families:[]}),
      localJson('algebra1_course_map.json',{topics:[]}),
      localJson('family_preview_specimens_alg1.json',{specimens:{}}),
      localJson('family_preview_specimens.json',{specimens:{}}),
      localJson('family_preview_specimens_le7.json',{specimens:{}})
    ]).then(([catalog,families,map,algPrev,basePrev,le7Prev])=>({catalog,families,map,algPrev,previews:{specimens:{...(basePrev.specimens||{}),...(le7Prev.specimens||{}),...(algPrev.specimens||{})}}}));
    return dataPromise;
  }
  function mergeCatalog(base,ext,previews){
    const out=structuredClone(base),names=new Set((out.courses||[]).map(c=>c.name));
    for(const c of (ext.courses||[]))if(!names.has(c.name)){(out.courses||(out.courses=[])).push(c);names.add(c.name);}
    const specs=previews.specimens||{};
    out.runtime_quality_contract={status:'HARD',rules:[
      'Family metadata is planning metadata, not student-facing prompt prose.',
      'Instantiate a concrete solvable task from the matching canonical family contract.',
      'Resolve all mathematical values/data/figures; no generic fallback prompt or generic fallback visual.',
      'Independently solve each instantiated item and verify prompt, representation, and answer alignment.',
      'Curated previews lock evidence architecture and representation role, not exact wording or values.',
      'Refresh candidates remain in the same family and preserve response/representation/difficulty demand.'
    ]};
    let missing=0,total=0;
    for(const course of (out.courses||[]))for(const topic of (course.topics||[]))for(const family of (topic.families||[])){total++;if(specs[family.id])family.preview_specimen=specs[family.id];else missing++;family.runtime_quality_rules=out.runtime_quality_contract.rules;}
    out.preview_quality_coverage={total_family_rows:total,missing_specimen_rows:missing,status:missing===0?'COMPLETE':'INCOMPLETE'};
    return out;
  }
  function mergeBank(bank,extFamilies,algMap){
    const out=structuredClone(bank),famMap=out.family_contracts||(out.family_contracts={});
    for(const f of (extFamilies.families||[])){if(!famMap[f.family_id])famMap[f.family_id]=f;}
    const source=(algMap.topics||[]), publicFamily=id=>{const f=famMap[id];if(!f)throw new Error('Algebra 1 map references missing family '+id);return {id,category:f.category||'Math',label:f.label,summary:f.evidence_job,representations:f.representation_modes,response_modes:f.response_modes,difficulty:['intro','standard','mastery'],...(f.generator?.render_route&&f.generator.render_route!=='html_mathjax'?{visual:f.generator.render_route}:{}),wording_profile:f.default_wording_profile||'direct_concise',quality_status:f.status||'pilot'};};
    const algCourse={name:algMap.course_label||algMap.course||'Algebra 1',default_topic:source[0]?.id||null,topics:source.map(t=>({id:t.id,label:t.label,families:(t.family_ids||[]).map(publicFamily)}))};
    const names=new Set((out.courses||[]).map(c=>c.name));if(!names.has(algCourse.name))(out.courses||(out.courses=[])).push(algCourse);
    out.architecture_version='math-family-contracts/1.1-modular';out.updated='2026-09-19';out.canonical_family_library_manifest='_question_structure/catalogs/math_family_library_manifest.json';out.authority='Generated compatibility aggregate composed from the base registry plus canonical course extensions. Family definitions remain canonical in their registered source files.';
    return out;
  }
  window.fetch=async(input,init)=>{
    const raw=typeof input==='string'?input:input.url,resolved=new URL(raw,document.baseURI),path=resolved.pathname;
    if(path.endsWith('/district_tools/worksheet_builder/family_preview_specimens.json')){
      const d=await extensionData();return new Response(JSON.stringify(d.previews),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});
    }
    if(path.endsWith('/district_tools/worksheet_builder/question_structure_catalog.json')){
      const r=await baseFetch(input,init);if(!r.ok)return r;try{const base=await r.clone().json(),d=await extensionData(),merged=mergeCatalog(base,d.catalog,d.previews);return new Response(JSON.stringify(merged),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});}catch(e){console.error('Catalog extension failed',e);return r;}
    }
    if(resolved.hostname==='api.github.com' && path.endsWith('/repos/tnezki/memories/contents/_question_structure/catalogs/math_worksheet_generator_bank.json')){
      const r=await baseFetch(input,init);if(!r.ok)return r;try{const api=await r.clone().json(),bank=JSON.parse(dec64(api.content)),d=await extensionData(),merged=mergeBank(bank,d.families,d.map);api.content=enc64(JSON.stringify(merged,null,2)+'\n');api.size=new TextEncoder().encode(JSON.stringify(merged,null,2)+'\n').length;return new Response(JSON.stringify(api),{status:200,headers:{'Content-Type':'application/vnd.github+json','Cache-Control':'no-store'}});}catch(e){console.error('Generator-bank extension failed',e);return r;}
    }
    return baseFetch(input,init);
  };
  document.addEventListener('DOMContentLoaded',()=>{
    const note=document.querySelector('main section.card .note');
    if(note)note.innerHTML='<b>Multi-grade / course pilot:</b> choose one or more filters. Lower Elementary, Grades 4–8, and Algebra 1 are active. Geometry, Algebra 2, Precalculus, and Calculus will be added as their reference sets are incorporated.';
  });
})();
