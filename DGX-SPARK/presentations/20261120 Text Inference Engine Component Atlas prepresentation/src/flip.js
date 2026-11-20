function identityCard(id) {
  const cc=capsules.get(data.aliases[id]||id);
  return '<dt>'+pill(cc.name,'#cc/'+cc.id)+'</dt><dd>'+e(cc.summary)+'<div class="pills">'+targets(cc.id).map(cmpLink).join(' ')+'</div></dd>';
}
function workAssignments(job) {
  const order=jobs.get(job.id);
  return '<section><h2>Component assignments</h2>'+order.assignments.map(([key,mode])=>{
    const cc=capsules.get(key);
    if(cc.kind==='factory')return '<article class="insight"><div class="tagline">Invoke factory capability</div><strong>'+ccLink(cc)+'</strong><p class="cc-summary">'+e(cc.summary)+'</p></article>';
    return '<article class="insight"><div class="tagline">'+({build:'Build component',change:'Change component',use:'Use component'})[mode]+'</div><strong>'+targets(key).map(cmpLink).join(' · ')+'</strong><p><b>Build CC</b> '+ccLink(cc)+'</p><p class="cc-summary">'+e(cc.summary)+'</p></article>';
  }).join('')+'</section>';
}
function designCoverage(){
  const homes=new Map();
  for(const c of all){const title=assemblyHome(c.id).title;if(!homes.has(title))homes.set(title,[]);homes.get(title).push(c);}
  const count=k=>data.ccs.filter(cc=>ccKind(cc)===k).length, scoped=s=>all.filter(c=>c.scope===s).length;
  return '<section class="sheet" id="coverage"><h2>Design coverage</h2><p>'+count('builder')+' builder CCs cover '+scoped('Engine')+' in-scope components and '+scoped('Extension')+' conditional extensions. '+count('factory')+' factory workers produce the engineering artifacts. '+count('tool')+' tool CCs and '+count('analysis')+' analysis CCs operate or analyze components. '+scoped('Host')+' host providers supply compute, memory and storage.</p>'+operatingCoverage()+[...homes].map(([group,rows])=>{
    return details(group+' · '+rows.length,rows.map(c=>'<article class="insight"><h3>'+cmpLink(c)+'</h3>'+relatedCCs(c.id).map(cc=>'<p>'+ccLink(cc)+'</p>'+fact(deliveryLabel(cc),cc.summary)).join('')+'<div class="pills">'+served(c.id).map(a=>pill(a.title,'#action/'+a.id)).join(' ')+'</div></article>').join(''));
  }).join('')+'</section>';
}
function tabActive(tab) {
  for(const a of document.querySelectorAll('header nav a')){
    if(a.dataset.tab===tab)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  }
}
function handoffPath(from,to){return '#handoff/'+from+'/'+to;}
function stagesFor(factory){
  return (factory?factoryStages:engineStages).map(g=>({...g,main:g.main.map(id=>components.get(id)),side:g.side.map(id=>components.get(id))}));
}
function overview(factory){
  const stages=stagesFor(factory), edges=factory?factoryHandoffs:engineHandoffs;
  const draw=(id)=>location.hash='#component/'+id;
  const stageMenu='<div class="tools stage-menu" aria-label="Jump to a stage">'+stages.map((g,i)=>'<button type="button" class="basic" data-stage="'+i+'">'+e(g.title)+'</button>').join('')+'</div>';
  const stageLinks=stages.map((g,i)=>'<section><h3>'+e(g.title)+'</h3><p>'+e(g.caption)+'</p><div class="pills">'+[...g.main,...g.side].map(c=>factory?ccLink(relatedCCs(c.id)[0]):pill(c.name,'#component/'+c.id)).join(' ')+'</div></section>').join('');
  root.innerHTML='<h1>'+ (factory?'Software factory':'Muse Spark Open on DGX Spark')+'</h1><p class="lead">'+(factory?'Follow the components that turn a reviewed request into a qualified engine image.':'Follow the components in inference order, from checkpoint startup through the first generated token. Follow the repeat edge for subsequent tokens.')+'</p>'+actorViewSwitch(factory?'factory':'engine',false)+'<div class="tools">'+(factory?pill('Design coverage','#integration/coverage'):pill('Follow a request','#component/serving.engine_image_gateway')+' '+pill('Cold expert fetch','#component/engine.expert_weight_cache'))+' '+pill('Build from scratch','#construction')+'</div>'+stageMenu+'<div class="cols"><div class="graphwrap"><div id="graph"></div></div><aside class="sheet" id="inspector"><h2>'+(factory?'Factory component order':'Engine component order')+'</h2><p>'+(factory?'Each factory CC performs its own action. Its output is a brief, contract, work order, source change, image, or qualification verdict.':'The main path follows one request. Adjacent components provide shared state, backend services and checkpoint-dependent alternatives.')+'</p>'+stageLinks+'</aside></div>';
  drawAtlas(document.querySelector('#graph'),{mode:factory?'factory':'engine',layers:factory?atlas.factory:atlas.engine,
    path:primitives=>orderedPathGraph({...primitives,groups:stages,edges,open:draw}),names:new Map(all.map(c=>[c.id,c.name])),
    onEdge:(s,t)=>location.hash=handoffPath(s,t)});
  root.querySelectorAll('[data-stage]').forEach(button=>button.onclick=()=>{
    const first=stages[Number(button.dataset.stage)].main[0];
    const item=root.querySelector('[data-ax-id="'+first.id+'"]');
    item.scrollIntoView({block:'center',inline:'nearest'});item.focus({preventScroll:true});
  });
}
function endpointOwner(id) {
  const parent=endpointData.parents.find(p=>p.children.some(child=>child.legacyIds.includes(id)));
  if(!parent)return '';
  return '<p class="crumb">Endpoint component · '+link('endpoint/parent/'+parent.id,parent.title)+'</p>';
}
function componentPage(c) {
  const owners=relatedCCs(c.id), acts=served(c.id);
  const recipes=data.jobs.filter(j=>j.assignments.some(([id])=>owners.some(cc=>cc.id===id)));
  const edges=[...engineHandoffs,...factoryHandoffs],home=assemblyHome(c.id);
  const downstream=edges.filter(([s])=>s===c.id),upstream=edges.filter(([,t])=>t===c.id);
  const connections=(rows,down)=>rows.map(([s,t,payload])=>'<li>'+cmpLink(components.get(down?t:s))+' <span>'+e(payload)+'</span> '+link(handoffPath(s,t).slice(1),'Inspect handoff')+'</li>').join('');
  const boundary=c.scope==='Host'?'Supplied by the deployment platform.':c.scope==='Extension'?c.when:'';
  const build=owners.map(cc=>'<article>'+kindBadge(cc)+' '+ccLink(cc)+fact(deliveryLabel(cc),cc.summary)+fact('Integration point',cc.connection)+'</article>').join('');
  const nav=pill(c.scope==='Factory'?'Software factory':'Engine',c.scope==='Factory'?'#factory':'#engine')+(home&&home.href!=='#factory'?' › '+pill(home.title,home.href):'');
  const children=c.id==='model.decoder_stack'?'<div class="tools">'+pill('Explore a decoder layer','#assembly/decoder/layer')+'</div>':'';
  const by=c.scope==='Factory'?owners.map(cc=>ccLink(cc)+fact('Integration point',cc.connection)).join(''):build||'<p>The machine supplies this component.</p>';
  const supply=owners.filter(cc=>cc.kind==='engine').map(cc=>details('Implement or integrate a library',fact('Existing implementation candidates',cc.integration)+fact('Integration check',cc.check)+ccLink(cc))).join('');
  const jobsHtml=recipes.map(j=>pill(componentOrderTitle(j),'#construction/'+j.id)).join(' ');
  const evidence=owners.map(cc=>pill(cc.name+' · evidence','#evidence/'+cc.id)).join(' ');
  root.innerHTML='<div class="crumb">'+nav+'</div><h1>'+e(c.name)+'</h1>'+formerNote(c)+endpointOwner(c.id)+ (c.scope==='Factory'?fact('Artifact delivered on invocation',owners[0].summary)+fact('How it is used',c.summary):fact(c.scope==='Host'?'Platform service':'What this code does',c.summary))+children+
    '<div class="component-profile"><div><section class="sheet" id="inspector"><h2>Operating interface</h2>'+fact('Consumes',c.inputs)+fact('Provides',c.outputs)+fact('Scope',boundary)+
    (c.scope==='Host'?fact('Platform responsibility',c.boundary):'')+'</section><section class="sheet"><h2>'+(c.scope==='Factory'?'Factory capability':c.scope==='Host'?'Provided by':'Built by')+'</h2>'+by+supply+'</section>'+
    '<section class="sheet"><h2>Actions performed</h2><div class="pills">'+acts.map(actLink).join(' ')+'</div></section>'+measuredBlock(c.id)+operatorBlock(c.id)+sourceBlock(c.id)+'</div>'+
    '<div><section class="sheet"><h2>Used by</h2><p>'+e(c.consumer)+'</p>'+(downstream.length?'<ul class="component-links">'+connections(downstream,true)+'</ul>':'')+'</section>'+
    (upstream.length?'<details class="sheet"><summary>Inputs from other components · '+upstream.length+'</summary><ul class="component-links">'+connections(upstream,false)+'</ul></details>':'')+
    (c.evidence?section('Platform acceptance evidence',e(c.evidence)):'')+((jobsHtml||evidence)?'<details class="sheet"><summary>Implementation, checks and evidence</summary>'+fact('Responsibility boundary',c.boundary)+owners.map(cc=>fact('Acceptance evidence',cc.evidence)).join('')+sec('Source evidence',evidence)+sec('Work orders',jobsHtml)+'</details>':'')+'</div></div>';
}
function handoff(s,t){
  const edge=[...engineHandoffs,...factoryHandoffs].find(([a,b])=>a===s&&b===t);if(!edge)return false;
  root.innerHTML='<h1>'+e(edge[2])+'</h1><div class="sheet"><div class="tagline">Component handoff</div><h2>'+cmpLink(components.get(s))+' → '+cmpLink(components.get(t))+'</h2>'+fact('Producer',components.get(s).summary)+fact('Consumer',components.get(t).summary)+pill('Return to overview',components.get(s).scope==='Factory'?'#factory':'#engine')+'</div>';return true;
}
function route(){
  app.classList.remove('endpoint');
  const [path,query='']=location.hash.slice(1).split('?');
  const [view,...segments]=path.split('/'), id=segments.join('/'),p=new URLSearchParams(query);
  let key=p.get('cc')||p.get('role')||(view==='cc'?id:null);
  if(key){const cc=capsules.get(key)||capsules.get(data.aliases[key]);if(cc){app.innerHTML=ccView(cc);tabActive('library');return true;}}
  if(view==='endpoint'||((!view||view==='engine')&&!id&&!p.size)){
    window.renderEndpoint(app);tabActive('engine');return true;
  }
  if((view==='assemblies'||view==='map'||view==='factory')&&!id&&!p.size){if(view==='factory')overview(true);else assemblyOverview();tabActive(view==='factory'?'factory':'engine');return true;}
  if(view==='engine'&&id==='actions'){engineActionOverview();tabActive('engine');return true;}
  if(view==='factory'&&id==='actions'){factoryActionOverview();return true;}
  if(view==='construction'&&(id===''||id==='actions'||jobs.has(id)||segments[0]==='actions'&&jobs.has(segments[1]))){
    const mode=segments[0]==='actions'?'actions':'components',job=mode==='actions'?segments[1]:id;
    if(job)constructionDetail(job,mode);else constructionHub(mode);tabActive('construction');return true;
  }
  if(view==='assembly'&&assemblyPage(id)){tabActive('engine');return true;}
  if(view==='trace'&&guidedView(segments[0],segments[1])){tabActive('engine');return true;}
  if(view==='readiness'){engineReadiness();tabActive('engine');return true;}
  if(view==='connections'){connectionInventory();tabActive('engine');return true;}
  if(view==='component'||view==='interface'){
    const c=components.get(id);if(c){componentPage(c);if(view==='interface'){document.querySelector('#inspector').setAttribute('tabindex','-1');document.querySelector('#inspector').focus();}tabActive(c.scope==='Factory'?'factory':'engine');return true;}
  }
  if(view==='handoff'&&handoff(...segments)){tabActive(components.get(segments[0]).scope==='Factory'?'factory':'engine');return true;}
  let a=actions.get(view==='action'?id:(view==='engine'||view==='factory')&&p.has('op')&&!p.has('trace')?id+'/'+p.get('op'):'');
  if(a){app.innerHTML=actionView(a);tabActive(a.id.startsWith('f_')?'factory':'engine');return true;}
  if(view==='evidence'&&(capsules.has(id)||data.aliases[id])){app.innerHTML=evidenceView(capsules.get(id)||capsules.get(data.aliases[id]));tabActive('sources');return true;}
  if(view==='integration'&&id==='coverage'||view==='coverage'){app.innerHTML='<h1>Factory integration</h1>'+designCoverage();tabActive('integration');return true;}
  if(view==='catalog'){library(p);tabActive('library');return true;}
  if(view==='orders'||view==='order'){if(jobs.has(id))constructionDetail(id,'components');else constructionHub('components');tabActive('construction');return true;}
  return false;
}
function normalizeLabels(){
  for(const a of root.querySelectorAll('a[href^="#construction/"]')){
    const job=jobs.get(a.hash.slice('#construction/'.length));
    if(job&&a.textContent.trim()===job.title)a.textContent=componentOrderTitle(job);
  }
  for(const a of root.querySelectorAll('a[href^="#cc/"]')){
    const key=a.hash.slice(4),cc=capsules.get(key)||capsules.get(data.aliases[key]);
    if(cc){a.href='#cc/'+cc.id;if(a.textContent.trim()===key)a.textContent=cc.name;}
  }
}
for(const job of data.jobs){
  const original=jobIndex.get(job.id);
  Object.assign(original,{needs:job.needs,work:job.work,output:job.output});
}
for(const cc of capsules.values()){
  const r=roleIndex.get(cc.legacy);
  if(!r)continue; // CCs added in the 20261120 edition have no record in the original atlas.
  r.title=cc.name;r.review.summary=cc.summary;r.workerRequirement=cc.requirement;
  const c=targets(cc.id)[0];
  r.inputs=c.inputs;r.outputs=c.outputs;
  r.handoff={...r.handoff,artifact:cc.summary,consumer:c.consumer,proof:cc.evidence};
}
return {actorExample,ccID:key=>data.aliases[key]||key,route,normalizeLabels,identityCard,workAssignments,designCoverage,library};
