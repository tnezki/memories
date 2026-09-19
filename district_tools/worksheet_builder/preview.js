(() => {
  const magnifier = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"></circle><path d="M16 16l5 5"></path></svg>';
  let catalogIndex = new Map();
  let observer = null;

  function esc(value){return String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));}

  async function loadCatalog(){
    try{
      const r = await fetch("question_structure_catalog.json", {cache:"no-store"});
      if(!r.ok) return;
      const catalog = await r.json();
      const map = new Map();
      for(const course of (catalog.courses||[])){
        for(const topic of (course.topics||[])){
          for(const family of (topic.families||[])) map.set(family.id,{...family,course:course.name,topic:topic.label});
        }
      }
      catalogIndex = map;
    }catch(error){console.warn("Preview catalog unavailable",error);}
  }

  function samplePrompt(meta){
    const label=String(meta?.label||"").toLowerCase();
    if(label.includes("factor") && label.includes("visual")) return "Use the array model to list all factor pairs for 24.";
    if(label.includes("common factor")) return "Find all common factors of 18 and 30.";
    if(label.includes("divisibility")) return "Which of these numbers are divisible by 3? Explain using a divisibility rule.";
    if(label.includes("prime")) return "Is 37 prime or composite? Explain how you know.";
    if(label.includes("multiple") && !label.includes("multiplication")) return "List the first five multiples of 8, then identify which are also multiples of 6.";
    if(label.includes("base ten") && label.includes("addition")) return "Use base-ten blocks to model 238 + 146. Regroup when needed, then find the sum.";
    if(label.includes("base ten") && label.includes("subtraction")) return "Use base-ten blocks to model 402 − 175. Regroup when needed, then find the difference.";
    if(label.includes("base ten")) return "Write the whole number represented by the base-ten model.";
    if(label.includes("number line") && label.includes("place")) return "Place 68 on the number line and label the nearest tens.";
    if(label.includes("number line")) return "Use the number line to solve the problem and show the jumps you used.";
    if(label.includes("equivalent fraction")) return "Complete the model, then write a fraction equivalent to 3/4.";
    if(label.includes("compare") && label.includes("fraction")) return "Compare 5/8 and 3/4 using >, <, or =. Show a model or explain your reasoning.";
    if(label.includes("fraction") && label.includes("model") && label.includes("division")) return "Use the model to determine how many 1/4-size groups fit in 2 1/2 wholes.";
    if(label.includes("fraction") && label.includes("multip")) return "Find 3/5 of 20. Show a model or equation that represents your reasoning.";
    if(label.includes("fraction") && label.includes("addition")) return "Add the fractions shown by the model and write the sum in simplest form.";
    if(label.includes("fraction") && label.includes("subtraction")) return "Subtract the fractions shown and write the difference in simplest form.";
    if(label.includes("decimal") && label.includes("multip")) return "Use the standard algorithm to find 6.4 × 0.7. Show any regrouping.";
    if(label.includes("decimal") && label.includes("division")) return "Use long division to find 8.4 ÷ 0.6. Write the quotient as a decimal.";
    if(label.includes("decimal") && label.includes("money")) return "A snack costs $2.45 and a drink costs $1.80. What is the total cost?";
    if(label.includes("unit conversion") || label.includes("conversion")) return "Use the given conversion relationship to convert the measurement. Show your reasoning.";
    if(label.includes("perimeter")) return "Find the perimeter of the labeled figure. Show how you used all outside side lengths.";
    if(label.includes("area")) return "Find the area of the figure using the given dimensions or grid.";
    if(label.includes("coordinate")) return "Plot the ordered pair (4, 3) and identify its coordinates from the grid.";
    if(label.includes("ratio table")) return "Complete the ratio table so each column represents the same proportional relationship.";
    if(label.includes("double number line")) return "Use the double number line to find the missing value in the proportional relationship.";
    if(label.includes("dilation")) return "Dilate the figure by the stated scale factor and list the image coordinates.";
    if(label.includes("scale factor")) return "Compare the two similar figures and determine the scale factor from Figure 1 to Figure 2.";
    if(label.includes("budget")) return "Use the budget table and total income to determine the missing spending category.";
    if(label.includes("tax")) return "Read the short situation and identify the type of tax being described.";
    if(label.includes("gross") || label.includes("net income")) return "Use the wages and deductions to determine take-home pay and identify gross versus net income.";
    if(label.includes("probability")) return "Use the equally likely outcomes shown to determine the probability of the event.";
    if(label.includes("dot") || label.includes("line plot")) return "Use the data to create or choose the matching plot, then answer the question about the display.";
    if(label.includes("stem-and-leaf")) return "Create a stem-and-leaf plot for the data set, then identify the median.";
    if(label.includes("mean") || label.includes("median") || label.includes("mode") || label.includes("range")) return "Use the data set to find the requested measure of center or spread.";
    if(meta?.summary) return `${String(meta.summary).replace(/\.$/,"")}.`;
    return "This preview shows the structure of the selected question family. The generated worksheet will use original values and context.";
  }

  function ensureModal(){
    if(document.getElementById("questionPreviewOverlay")) return;
    const overlay=document.createElement("div");
    overlay.id="questionPreviewOverlay";overlay.className="preview-overlay";overlay.setAttribute("aria-hidden","true");
    overlay.innerHTML=`<section class="preview-modal" role="dialog" aria-modal="true" aria-labelledby="questionPreviewTitle"><div class="preview-modal-head"><div><div class="preview-kicker" id="questionPreviewKicker">Question structure preview</div><h2 id="questionPreviewTitle">Preview</h2></div><button class="preview-close" type="button" aria-label="Close preview">×</button></div><div class="preview-modal-body"><p class="preview-note">Representative preview only — the generated worksheet will use original values, context, and parallel-version parameters.</p><div class="preview-paper"><div class="preview-problem"><strong>1.</strong><span id="questionPreviewPrompt"></span></div><div class="preview-workspace"></div></div><div class="preview-meta-grid"><div><b>Grade / topic</b><span id="questionPreviewScope"></span></div><div><b>Representation</b><span id="questionPreviewRepresentation"></span></div><div><b>Response</b><span id="questionPreviewResponse"></span></div></div></div></section>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".preview-close").addEventListener("click",closePreview);
    overlay.addEventListener("click",e=>{if(e.target===overlay)closePreview();});
    document.addEventListener("keydown",e=>{if(e.key==="Escape"&&overlay.classList.contains("open"))closePreview();});
  }

  function openPreview(id){
    ensureModal();
    const meta=catalogIndex.get(id)||{};
    document.getElementById("questionPreviewTitle").textContent=meta.label||"Question preview";
    document.getElementById("questionPreviewKicker").textContent=meta.category||"Question structure preview";
    document.getElementById("questionPreviewPrompt").textContent=samplePrompt(meta);
    document.getElementById("questionPreviewScope").textContent=[meta.course,meta.topic].filter(Boolean).join(" · ")||"Selected math skill";
    document.getElementById("questionPreviewRepresentation").textContent=(meta.representations||[meta.visual||"As appropriate"]).join(", ");
    document.getElementById("questionPreviewResponse").textContent=(meta.response_modes||["constructed response"]).join(", ");
    const overlay=document.getElementById("questionPreviewOverlay");overlay.classList.add("open");overlay.setAttribute("aria-hidden","false");overlay.querySelector(".preview-close").focus();
  }

  function closePreview(){const overlay=document.getElementById("questionPreviewOverlay");if(!overlay)return;overlay.classList.remove("open");overlay.setAttribute("aria-hidden","true");}

  function decorate(){
    document.querySelectorAll(".skill-row").forEach(row=>{
      if(row.querySelector("[data-preview-family]")) return;
      const id=row.dataset.familyId;if(!id)return;
      const qty=row.querySelector(":scope > .qty");if(!qty)return;
      const stack=document.createElement("div");stack.className="preview-control-stack";
      qty.replaceWith(stack);stack.appendChild(qty);
      const button=document.createElement("button");button.type="button";button.className="preview-btn";button.dataset.previewFamily=id;button.innerHTML=`${magnifier}<span>Preview</span>`;button.title="Preview this question structure";button.setAttribute("aria-label","Preview this question structure");
      stack.appendChild(button);
    });
  }

  document.addEventListener("click",e=>{const button=e.target.closest("[data-preview-family]");if(button)openPreview(button.dataset.previewFamily);});
  document.addEventListener("DOMContentLoaded",async()=>{await loadCatalog();ensureModal();decorate();const mount=document.getElementById("familyMount");if(mount){observer=new MutationObserver(decorate);observer.observe(mount,{childList:true,subtree:true});}});
})();
