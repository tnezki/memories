(() => {
  function simplifyLabels(){
    const note=document.querySelector('.course-topbar-note'); if(note)note.textContent='Banks';
    const hero=document.getElementById('heroBankStatus'); if(hero)hero.textContent='Algebra banks + Portfolio';
    const checkpoint=document.querySelector('#checkpointPanel .eyebrow'); if(checkpoint)checkpoint.textContent='CHECKPOINT · PORTFOLIO-AWARE';
    const summative=document.querySelector('#summativePanel .eyebrow'); if(summative)summative.textContent='SUMMATIVE · PORTFOLIO-AWARE';
  }
  function init(){ simplifyLabels(); }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
})();
