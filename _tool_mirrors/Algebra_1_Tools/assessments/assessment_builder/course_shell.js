(() => {
  if (document.querySelector('.course-topbar')) return;
  const body=document.body;
  const top=document.createElement('div');
  top.className='course-topbar';
  top.innerHTML='<div class="brand">Algebra 1 Tools</div><div class="crumb">Assessment Builder</div><div class="spacer"></div><span>Course Tools</span>';
  body.insertBefore(top,body.firstChild);

  const hero=document.createElement('div');
  hero.className='course-hero';
  hero.innerHTML='<section class="course-hero-inner"><div><h1>Assessment Builder</h1><p>Choose what you are teaching, select approved Algebra bank families by I Can, then assemble and print using the shared course-tool controls. Checkpoint and Summative keep their Portfolio-aware evidence routing.</p></div><div class="course-status-badge">Algebra banks + Portfolio ready</div></section>';
  const shell=document.querySelector('.app-shell');
  body.insertBefore(hero,shell);

  const sidebar=document.querySelector('.selection-sidebar');
  if(sidebar){
    const head=document.createElement('div');
    head.className='course-step-head';
    head.innerHTML='<div class="course-step-num">1</div><div><h2>What are you teaching?</h2><p>Choose the product, unit, item label, and delivery destination. Then narrow the bank by Mastery Goal and I Can.</p></div>';
    sidebar.insertBefore(head,sidebar.firstChild);

    const destination=document.getElementById('destinationCard');
    const summary=document.querySelector('.selection-summary');
    const filename=document.querySelector('.filename-card');
    if(destination&&summary&&filename){
      const grid=document.createElement('div');grid.className='course-summary-grid';
      destination.parentNode.insertBefore(grid,destination);
      grid.append(destination,summary,filename);
    }

    const next=document.getElementById('nextBtn'), clear=document.getElementById('clearAllBtn'), draft=document.querySelector('.draft-tools');
    if(next&&clear){
      const row=document.createElement('div');row.className='course-action-row';
      next.parentNode.insertBefore(row,next);row.append(next,clear);if(draft)row.append(draft);
    }
  }

  const bankHeader=document.querySelector('.bank-header');
  if(bankHeader){
    const title=bankHeader.querySelector('h2');
    if(title) title.style.marginTop='2px';
  }

  const workspaceTop=document.querySelector('.workspace-top');
  if(workspaceTop){
    const first=workspaceTop.firstElementChild;
    if(first){
      const p=first.querySelector('#workspaceSub');
      if(p) p.textContent='Selected bank families become editable assessment cards with the shared print/layout controls.';
    }
  }
})();
