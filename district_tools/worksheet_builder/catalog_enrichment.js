(() => {
  const baseFetch = window.fetch.bind(window);
  let previewPromise = null;
  async function previews(){
    if(!previewPromise) previewPromise=baseFetch('family_preview_specimens.json',{cache:'no-store'}).then(r=>r.ok?r.json():({specimens:{}})).catch(()=>({specimens:{}}));
    return previewPromise;
  }
  window.fetch = async (input,init) => {
    const raw=typeof input==='string'?input:input.url;
    const resolved=new URL(raw,document.baseURI);
    if(!resolved.pathname.endsWith('/district_tools/worksheet_builder/question_structure_catalog.json')) return baseFetch(input,init);
    const catalogResponse=await baseFetch(input,init);
    if(!catalogResponse.ok) return catalogResponse;
    try{
      const catalog=await catalogResponse.clone().json();
      const previewData=await previews();
      const specimens=previewData.specimens||{};
      catalog.runtime_quality_contract={status:'HARD',rules:[
        'Family metadata is planning metadata, not student-facing prompt prose.',
        'Use the matching family record in MATH_WORKSHEET_GENERATOR_BANK.json to instantiate a concrete solvable task; do not paraphrase summary, evidence job, or student action into the prompt.',
        'Resolve every required placeholder to explicit mathematical values, expressions, data, context, or figures.',
        'No generic fallback question or generic fallback visual is allowed.',
        'Do not append filler such as Use the representation shown and complete the requested response.',
        'A graph family must render the correct graph semantics: systems show two relations; transformations show source and image figures; slope/equation families show the intended line; nonvisual algebra families receive no decorative graph.',
        'Independently solve the instantiated item and verify prompt, visual, and answer alignment before it is placed on the worksheet.'
      ]};
      for(const course of (catalog.courses||[])) for(const topic of (course.topics||[])) for(const family of (topic.families||[])){
        if(specimens[family.id]) family.preview_specimen=specimens[family.id];
        family.runtime_quality_rules=catalog.runtime_quality_contract.rules;
      }
      return new Response(JSON.stringify(catalog),{status:200,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});
    }catch(error){
      console.error('Could not enrich worksheet catalog',error);
      return catalogResponse;
    }
  };
})();
