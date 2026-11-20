const constructionDeliverables = {
  intent: 'Reviewed intent brief',
  contract: 'Engine contract',
  plan: 'Component work orders',
  weights: 'Checkpoint reader',
  serving: 'Engine image gateway and request pipeline',
  reference: 'Reference decoder block',
  routing: 'Routed expert block',
  state: 'Sequence KV manager and workspace allocator',
  placement: 'Weight placement planner',
  storage: 'Expert weight cache',
  kernels: 'Kernel dispatcher and weight block decoder',
  assemble: 'Generation loop and token sampler',
  image: 'Runnable engine image',
  qualify: 'Target qualification receipt',
  route_trace: 'Runtime event recorder',
  forecast: 'Expert demand predictor',
  capture: 'Execution graph backend',
  prefix_reuse: 'Prefix state cache',
  pack_convert: 'Converted weight pack',
  dense_path: 'Dense feed-forward block'
};
function componentOrderTitle(job) {
  return constructionDeliverables[job.id];
}
const constructionPhases = [
  ['Factory inputs','intent','contract','plan'],
  ['Parallel engine foundations','weights','serving','reference','routing','state'],
  ['Placement and compute','placement','kernels'],
  ['Expert storage','storage'],
  ['Runtime assembly','assemble'],
  ['Image and qualification','image','qualify']
];
const constructionModes = {build:'Build component',change:'Change component',use:'Use component'};
function constructionURL(mode,id='') {
  return '#construction'+(mode==='actions'?'/actions':'')+(id?'/'+id:'');
}
function displayedOrderTitle(job,mode) {
  return mode==='actions'?job.title:componentOrderTitle(job);
}
function constructionModeLinks(mode,id='') {
  return '<nav class="tools" aria-label="Work order view">'+[['components','Component deliverables'],['actions','Agent actions']].map(([key,label])=>
    '<a class="pill" '+(mode===key?'aria-current="page" ':'')+'href="'+constructionURL(key,id)+'">'+label+'</a>').join(' ')+'</nav>';
}
function constructionReceiptLink(id,mode) {
  return pill(displayedOrderTitle(jobs.get(id),mode),constructionURL(mode,id));
}
function constructionAssignments(job,showDetails) {
  return job.assignments.map(([id,mode])=>{
    const cc=capsules.get(id), factory=cc.kind==='factory', parts=targets(id);
    const label=factory?'Invoke factory capability':constructionModes[mode];
    const componentLinks=parts.map(cmpLink).join(' ');
    const attributes=' data-assignment-mode="'+e(factory?'invoke':mode)+'" data-cc="'+e(id)+'"';
    if(!showDetails) {
      if(factory)return '<div class="order-actor"'+attributes+'><small>Invoke factory CC</small> '+ccLink(cc)+'</div>';
      const jobRole=mode==='use'?'Component used':mode==='change'?'Component changed':'Component delivered';
      return '<div class="order-actor"'+attributes+'><div><small>'+jobRole+'</small> '+componentLinks+'</div><div><small>Engineering CC</small> '+ccLink(cc)+'</div></div>';
    }
    const performed=parts.map(c=>'<div class="pills">'+served(c.id).map(actLink).join(' ')+'</div>').join('');
    return '<article class="insight"'+attributes+'><div class="tagline">'+e(label)+'</div><h3>'+componentLinks+'</h3>'+
      '<p><b>'+(factory?'Capability CC':mode==='use'?'Existing capability':'Engineering CC')+'</b> '+ccLink(cc)+'</p>'+fact(mode==='use'&&!factory?'Existing interface used':deliveryLabel(cc),mode==='use'&&!factory?parts.map(c=>c.summary).join(' '):cc.summary)+
      (factory?fact('Capability output',parts.map(c=>c.outputs).join(' ')):'')+
      details(factory?'Factory actions performed':'Actions performed by the component',performed)+'</article>';
  }).join('');
}
function constructionTile(job,mode) {
  const core=job.assignments.flatMap(([id,assignment])=>assignment==='build'||assignment==='change'?targets(id):[]);
  const primary=core[0]&&actions.get(core[0].primary);
  const example=primary&&mode==='components'?'<p class="order-example"><small>Example action</small> '+cmpLink(core[0])+' → '+actLink(primary)+'</p>':'';
  const actionGroups=job.assignments.flatMap(([id])=>targets(id)).map(c=>
    '<p><strong>'+e(c.name)+'</strong></p><div class="pills">'+served(c.id).map(actLink).join(' ')+'</div>').join('');
  return '<article class="build-card lane-'+e(job.lane)+'"><small>'+e(lanes[job.lane])+' · '+e(job.agent)+'</small>'+
    '<h3><a data-job="'+e(job.id)+'" href="'+constructionURL(mode,job.id)+'">'+e(displayedOrderTitle(job,mode))+'</a></h3>'+
    '<div class="build-ccs">'+constructionAssignments(job,false)+'</div>'+example+details('Handoff and acceptance',fact('Engineering handoff',job.output)+fact('Acceptance evidence',job.evidence))+details('All actions performed',actionGroups)+'<p class="build-input"><b>Starts after</b> '+
    (job.needs.map(([id])=>constructionReceiptLink(id,mode)).join(' ')||'the user supplies the model, machine and workload intent')+'</p></article>';
}
function constructionRehearsal(mode) {
  const panel=root.querySelector('#ready-jobs');
  const baseline=data.jobs.filter(j=>j.lane!=='option');
  const ready=baseline.filter(j=>!acceptedBuildJobs.includes(j.id)&&j.needs.every(([id])=>acceptedBuildJobs.includes(id)));
  const last=jobs.get(acceptedBuildJobs.at(-1));
  panel.innerHTML='<div aria-live="polite"><p><b>'+ready.length+(ready.length===1?' work order':' work orders')+' ready</b> · '+acceptedBuildJobs.length+' of '+baseline.length+' example receipts accepted.</p>'+
    (last?'<p><b>Last receipt · '+e(displayedOrderTitle(last,mode))+'</b><br>'+e(last.output)+'</p>'+fact('Acceptance evidence',last.evidence):'')+
    (ready.length?'<div class="build-ready">'+ready.map(j=>'<button data-accept="'+e(j.id)+'" type="button">Accept · '+e(displayedOrderTitle(j,mode))+'</button>').join('')+'</div>':'<p>The planner has received the image and qualification evidence.</p>')+
    '</div><button class="basic" id="undo-build" type="button" '+(last?'':'disabled')+'>Undo last receipt</button>';
  panel.onclick=event=>{
    const button=event.target.closest('button');
    if(!button)return;
    if(button.id==='undo-build')acceptedBuildJobs.pop();
    else if(ready.some(j=>j.id===button.dataset.accept))acceptedBuildJobs.push(button.dataset.accept);
    constructionRehearsal(mode);
    (panel.querySelector('[data-accept]')||panel.querySelector('#undo-build')).focus({preventScroll:true});
  };
}
function constructionHub(mode='components') {
  const overview=mode==='actions'?'Agent actions for building the engine':'Engine components from scratch';
  const rehearsal='<section class="sheet build-sim"><h2>Try the handoffs</h2><p>Accept example receipts to reveal jobs that can start in parallel. Existing qualified artifacts can satisfy a dependency, and new measurements can reopen a work order.</p><div id="ready-jobs"></div></section>';
  const phases=mode==='actions'?constructionPhases:[...constructionPhases.slice(1),constructionPhases[0]];
  const tiles=phases.map(([name,...ids])=>'<section class="build-group"><h2>'+e(name)+'</h2><div class="build-grid">'+ids.map(id=>constructionTile(jobs.get(id),mode)).join('')+'</div></section>').join('');
  root.innerHTML='<h1>'+overview+'</h1><p class="lead">Build one text MoE engine for a checkpoint larger than the device’s memory. The Contract compiler uses reviewed intent and the system ontology to create the engine contract. The Workflow orchestrator uses it to dispatch agents with the required builder capabilities. Each order names the component or artifact and its acceptance check.</p>'+
    constructionModeLinks(mode)+'<div class="tools">'+pill('Compare engine designs','#construction/designs')+' '+pill('Out-of-core experiments','#construction/trials')+
    ' <button class="pill" type="button" data-build-jump="conditional-jobs">Contract-dependent work ↓</button></div>'+
    (mode==='components'?'<section class="sheet construction-path"><h2>Engine delivery path</h2><div class="pills">'+[
      ['weights','Checkpoint reader'],['serving','Request pipeline'],['reference','Reference decoder'],['routing','Routed expert block'],['assemble','Integrated generation loop'],['image','Runnable image'],['qualify','Qualification receipt']
    ].map(([id,label])=>pill(label,constructionURL(mode,id))).join(' ')+'</div><p>The reader, request pipeline and decoder work can proceed in parallel. Their tested outputs feed runtime assembly, image creation and qualification.</p></section>':'')+
    (mode==='actions'?rehearsal+tiles:tiles+rehearsal)+
    '<section class="build-group" id="conditional-jobs" tabindex="-1"><h2>Contract-dependent work</h2><p>The checkpoint, workload or observed bottleneck activates these jobs. A converted pack reopens placement and kernel checks. Dense FFN layers require a tested dense path before assembly.</p><div class="build-grid">'+
    data.jobs.filter(j=>j.lane==='option').map(j=>constructionTile(j,mode)).join('')+'</div></section>'+
    '<div id="engine-variations" tabindex="-1">'+engineVariations()+'</div>';
  constructionRehearsal(mode);
  root.querySelector('[data-build-jump]').onclick=()=>{
    const section=root.querySelector('#conditional-jobs');
    section.focus({preventScroll:true});section.scrollIntoView();
  };
  tabActive('construction');
  return true;
}
function constructionDetail(id,mode='components') {
  const job=jobs.get(id);
  if(!job)return false;
  const next=data.jobs.filter(j=>j.needs.some(([up])=>up===id));
  const linkTo=other=>constructionReceiptLink(other,mode);
  const conditions=data.gates.filter(([up,down])=>id===up||id===down);
  const prerequisites=job.needs.map(([up,receipt])=>'<li>'+linkTo(up)+' '+e(receipt)+'</li>').join('');
  const consumers=next.map(j=>'<li>'+linkTo(j.id)+' '+e(j.needs.find(([up])=>up===id)[1])+'</li>').join('');
  root.innerHTML='<div class="crumb">'+pill('From scratch',constructionURL(mode))+'</div>'+constructionModeLinks(mode,id)+
    '<article id="work-order" class="sheet lane-'+e(job.lane)+'"><small>'+e(lanes[job.lane])+' · '+e(job.agent)+'</small>'+
    '<h1>'+e(displayedOrderTitle(job,mode))+'</h1>'+
    
    sec('Engineering handoff','<p>'+e(job.output)+'</p>')+sec('Acceptance evidence','<p>'+e(job.evidence)+'</p>')+
    '<section><h2>Component assignments</h2>'+constructionAssignments(job,true)+'</section>'+sec('Start when',prerequisites?'<ul>'+prerequisites+'</ul>':'<p>The user supplies the model, machine and workload intent.</p>')+
    sec('Agent work','<p>'+e(job.work)+'</p>')+
    (conditions.length?sec('When a variant is enabled','<ul>'+conditions.map(([up,down,receipt])=>'<li>'+linkTo(up)+' → '+linkTo(down)+' '+e(receipt)+'</li>').join('')+'</ul>'):'')+
    sec('Who uses it',consumers?'<ul>'+consumers+'</ul>':'<p>'+(job.lane==='option'?'The planner sends the enabled variant through image build and controlled qualification.':'The planner receives the scoped verdict and supporting measurements.')+'</p>')+'</article>';
  tabActive('construction');
  return true;
}
