(() => {
  const baseFetch=window.fetch.bind(window);
  let libraryPromise=null;
  const dec64=s=>{const bin=atob(String(s||'').replace(/\s/g,'')),bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);return new TextDecoder('utf-8').decode(bytes);};
  const enc64=s=>{const bytes=new TextEncoder().encode(s);let bin='';const chunk=0x8000;for(let i=0;i<bytes.length;i+=chunk)bin+=String.fromCharCode(...bytes.subarray(i,i+chunk));return btoa(bin);};
  async function json(path){const r=await baseFetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`Could not load ${path}: HTTP ${r.status}`);return r.json();}
  function qroot(path){return '../../_question_structure/'+String(path).replace(/^\.\//,'');}
  function normalizeCourses(doc){if(Array.isArray(doc.courses))return doc.courses;const name=doc.course_label||doc.course;return name?[{name,default_topic:doc.default_topic||doc.topics?.[0]?.id||null,topics:doc.topics||[]}]:[];}
  async function library(){
    if(libraryPromise)return libraryPromise;
    libraryPromise=(async()=>{
      const manifest=await json('../../_question_structure/catalogs/math_family_library_manifest.json');
      const [familyDocs,mapDocs,previewDocs]=await Promise.all([
        Promise.all((manifest.family_sources||[]).map(s=>json(qroot(s.path)))),
        Promise.all((manifest.course_map_sources||[]).map(s=>json(qroot(s.path)))),
        Promise.all((manifest.preview_sources||[]).map(p=>json(qroot(p))))
      ]);
      const familyMap={};for(const d of familyDocs)for(const f of (d.families||[])){if(familyMap[f.family_id])throw new Error('Duplicate family ID '+f.family_id);familyMap[f.family_id]=f;}
      const previews={};for(const d of previewDocs)Object.assign(previews,d.specimens||{});
      const courses=[];const names=new Set();for(const d of mapDocs)for(const c of normalizeCourses(d)){if(names.has(c.name))throw new Error('Duplicate course '+c.name);names.add(c.name);courses.push(c);}
      const publicFamily=id=>{const f=familyMap[id];if(!f)throw new Error('Missing family '+id);const route=f.generator?.render_route;return {id,category:f.category||'Math',label:f.label,summary:f.evidence_job,representations:f.representation_modes,response_modes:f.response_modes,difficulty:['intro','standard','mastery'],wording_profile:f.default_wording_profile||'direct_concise',quality_status:f.status||'current',...(route&&route!=='html_mathjax'?{visual:route}:{}),preview_specimen:previews[id]||null,runtime_quality_rules:[
        'Family metadata is planning metadata, not student-facing prompt prose.',
        'Instantiate a concrete solvable task from the exact canonical family contract.',
        'Honor visual_policy: student visuals contain givens only; solution visuals may show completed constructions.',
        'Resolve all mathematical values/data/figures; no generic fallback prompt or generic fallback visual.',
        'Independently solve every generated candidate and verify prompt, representation, and answer alignment.',
        'Refresh candidates remain in the same family and preserve evidence/representation/difficulty demand.'
      ]};};
      const publicCourses=courses.map(c=>({name:c.name,default_topic:c.default_topic||c.topics?.[0]?.id||null,topics:(c.topics||[]).map(t=>({id:t.id,label:t.label,families:(t.family_ids||[]).map(publicFamily)}))}));
      const catalog={schema:'math-worksheet-question-structure-catalog/0.5-manifest',status:'CURRENT',updated:manifest.updated,canonical_family_library_manifest:'_question_structure/catalogs/math_family_library_manifest.json',reference_model:{purpose:'Browse canonical reusable math question families by course/topic.',copyright_rule:manifest.source_use_rule},courses:publicCourses,generic_families:[],preview_quality_coverage:{total_family_rows:publicCourses.flatMap(c=>c.topics).flatMap(t=>t.families).length,missing_specimen_rows:publicCourses.flatMap(c=>c.topics).flatMap(t=>t.families).filter(f=>!f.preview_specimen).length}};
      const bank={schema:'math-worksheet-generator-bank/0.3-manifest',architecture_version:'math-family-contracts/1.2-manifest',status:'CURRENT',updated:manifest.updated,authority:'Runtime compatibility aggregate composed from canonical family sources registered in math_family_library_manifest.json.',source_use_rule:manifest.source_use_rule,default_wording_profile:'direct_concise',canonical_family_library_manifest:'_question_structure/catalogs/math_family_library_manifest.json',generator_rules:{family_first:'Resolve exact family before authoring.',no_freeform_drift:'Do not substitute a generic prompt.',student_solution_visuals:'Honor visual_policy; never reveal a completed construction in the student view.',concise_default:'Use direct_concise unless functional context is required.',parallel_forms:'Preserve family/evidence/difficulty slot-for-slot.',refresh_candidates:'Create three independently solved same-family candidates per slot.',qa:'Verify prompt, representation, visual policy, and answer alignment.'},courses:publicCourses,family_contracts:familyMap};
      return {manifest,previews:{schema:'math-family-preview-specimens/runtime',specimens:previews},catalog,bank};
    })();return libraryPromise;
  }
  window.fetch=async(input,init)=>{
    const raw=typeof input==='string'?input:input.url,resolved=new URL(raw,document.baseURI),path=resolved.pathname;
    if(path.endsWith('/district_tools/worksheet_builder/family_preview_specimens.json')){try{const d=await library();return new Response(JSON.stringify(d.previews),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});}catch(e){console.error(e);return new Response('{}',{status:500});}}
    if(path.endsWith('/district_tools/worksheet_builder/question_structure_catalog.json')){try{const d=await library();return new Response(JSON.stringify(d.catalog),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});}catch(e){console.error(e);return baseFetch(input,init);}}
    if(resolved.hostname==='api.github.com' && path.endsWith('/repos/tnezki/memories/contents/_question_structure/catalogs/math_worksheet_generator_bank.json')){
      const r=await baseFetch(input,init);if(!r.ok)return r;try{const api=await r.clone().json(),d=await library(),txt=JSON.stringify(d.bank,null,2)+'\n';api.content=enc64(txt);api.size=new TextEncoder().encode(txt).length;return new Response(JSON.stringify(api),{status:200,headers:{'Content-Type':'application/vnd.github+json','Cache-Control':'no-store'}});}catch(e){console.error('Manifest generator-bank composition failed',e);return r;}
    }
    return baseFetch(input,init);
  };
  document.addEventListener('DOMContentLoaded',()=>{const note=document.querySelector('main section.card .note');if(note)note.innerHTML='<b>Full math-family library:</b> choose one or more filters. Lower Elementary through Calculus are active and may be mixed in one request.';});
})();
