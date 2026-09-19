(() => {
  const baseFetch=window.fetch.bind(window);
  let previewPromise=null;
  async function previews(){
    if(!previewPromise) previewPromise=Promise.all([
      baseFetch('family_preview_specimens.json',{cache:'no-store'}).then(r=>r.ok?r.json():({specimens:{}})).catch(()=>({specimens:{}})),
      baseFetch('family_preview_specimens_le7.json',{cache:'no-store'}).then(r=>r.ok?r.json():({specimens:{}})).catch(()=>({specimens:{}}))
    ]).then(([a,b])=>({specimens:{...(a.specimens||{}),...(b.specimens||{})}}));
    return previewPromise;
  }
  window.fetch=async(input,init)=>{
    const raw=typeof input==='string'?input:input.url,resolved=new URL(raw,document.baseURI);
    if(!resolved.pathname.endsWith('/district_tools/worksheet_builder/question_structure_catalog.json'))return baseFetch(input,init);
    const catalogResponse=await baseFetch(input,init);if(!catalogResponse.ok)return catalogResponse;
    try{
      const catalog=await catalogResponse.clone().json(),previewData=await previews(),specimens=previewData.specimens||{};
      catalog.runtime_quality_contract={status:'HARD',rules:[
        'Family metadata is planning metadata, not student-facing prompt prose.',
        'Use the matching canonical family record to instantiate a concrete solvable task; do not paraphrase summary, evidence job, or student action into the prompt.',
        'Resolve every required placeholder to explicit mathematical values, expressions, data, context, or figures.',
        'No generic fallback question or generic fallback visual is allowed.',
        'Do not append filler such as Use the representation shown and complete the requested response.',
        'A graph family must render the correct graph semantics: systems show two relations; transformations show source and image figures; slope/equation families show the intended line; nonvisual algebra families receive no decorative graph.',
        'Independently solve the instantiated item and verify prompt, visual, and answer alignment before it is placed on the worksheet.',
        'When a curated preview specimen exists, preserve its evidence architecture and representation role while changing values/context for generated worksheet items.'
      ]};
      let missing=0,total=0;
      for(const course of (catalog.courses||[]))for(const topic of (course.topics||[]))for(const family of (topic.families||[])){total++;if(specimens[family.id])family.preview_specimen=specimens[family.id];else missing++;family.runtime_quality_rules=catalog.runtime_quality_contract.rules;}
      catalog.preview_quality_coverage={total_family_rows:total,missing_specimen_rows:missing,status:missing===0?'COMPLETE':'INCOMPLETE'};
      return new Response(JSON.stringify(catalog),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});
    }catch(error){console.error('Could not enrich worksheet catalog',error);return catalogResponse;}
  };
})();
