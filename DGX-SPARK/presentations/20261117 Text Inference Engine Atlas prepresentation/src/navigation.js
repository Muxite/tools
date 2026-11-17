const legacyNodes={intent:'f_spec/intake',contract:'f_spec/freeze',inspect:'f_plan',plan:'f_plan',build:'f_build',profile:'f_lab/profile',verification:'f_lab/quality',evidence:'f_evidence',model:'startup/config',tokenizer:'interface/encode',weights:'startup/bind',placement:'startup/place',backend:'backend/dispatch',serving:'interface/accept',scheduler:'schedule/admit',batch:'schedule/batch',prefill:'generate/prefill',decode:'generate/step',attention:'model/attend',sequence:'state/append',dense:'model/dense',routing:'model/route',experts:'model/expert',merge:'model/combine',sampling:'generate/sample',output:'interface/emit',graph:'backend/lower',memory:'state',streaming:'state/fill',cpu:'backend/cpu',transfer:'backend/streams',parallel:'model/dispatch',cuda:'backend/dispatch',observability:'backend/signal',embedding:'model/embed',norm:'model/norm',head:'model/head',shared:'model/shared'};
function render(){
 const [path,q='']=location.hash.slice(1).split('?'),[view='engine',raw='']=path.split('/'),id=decodeURIComponent(raw),p=new URLSearchParams(q);
 const overlay=engines.includes(p.get('overlay'))?p.get('overlay'):engines.includes(id)?id:'Strata';
 const opts={overlay}, set=h=>location.hash=h;
 let mode=view==='factory'?'factory':'engine',layer=layerIndex.get(id),opId=p.get('op'),cc=canonical(p.get('cc')),outside=false;
 if(view==='cc'||view==='node'||view==='compare'||view==='diagrams'||view==='map'){
   if(view==='cc'||p.get('role')){
     cc=canonical(id&&view==='cc'?id:p.get('role'));const job=roleIndex.get(cc);
     if(job){const preferred=job.sites.find(([l])=>factoryId(l)===(job.kind==='factory'));[layer,opId]=preferred||job.sites[0];layer=layerIndex.get(layer)}
     else outside=atlas.excluded.includes(cc);
   }else{
     const topic=p.get('topic'),legacy=legacyNodes[id]||({routing:'model/route',serving:'schedule',state:'state',execution:'backend',resources:'backend',startup:'startup',moe:'model/route',factory:'f_plan',construction:'f_build',model:'model'})[topic];
     if(legacy){const [l,o]=legacy.split('/');layer=layerIndex.get(l);opId=o}
     outside=id==='media';
   }
   if(layer)mode=factoryId(layer.id)?'factory':'engine';
 }
 const page=view==='library'||view==='sources'?view:mode;
 document.querySelectorAll('nav a').forEach(a=>{if(a.dataset.tab===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 if(page==='library'){library(p);return}if(page==='sources'){evidence();return}
 if(outside){root.innerHTML='<h1>Historical media role</h1><p class="lead">This work belonged to the earlier multimodal inventory. The current engine contract covers text generation.</p>'+pill('Text engine','#engine');return}
 const layers=mode==='factory'?atlas.factory:atlas.engine,edges=mode==='factory'?atlas.factoryEdges:atlas.edges;
 if(!layers.includes(layer))layer=null;
 const op=layer?.ops.find(x=>x.id===opId),role=op?.cc.includes(cc)?roleIndex.get(cc):null;
 const tr=atlas.traces.find(x=>x.id===p.get('trace')),idx=Math.min(tr?.steps.length-1||0,Math.max(0,Number(p.get('step'))||0));
 const traceHref=(t,i)=>at(t.steps[i][0],t.steps[i][1],{overlay,trace:t.id,step:i});
 const walk=tr?'<div class="insight"><strong>'+esc(tr.title)+'</strong><p>'+esc(tr.steps[idx][3])+'</p><div class="steps">'+tr.steps.map(([l,o],i)=>'<a href="'+esc(traceHref(tr,i))+'" '+(i===idx?'aria-current="step"':'')+'>'+esc((i+1)+'. '+layerIndex.get(l).ops.find(x=>x.id===o).title)+'</a>').join('')+'</div></div>':'';
 const overview=mode==='engine'?'Text inference engine':'Software factory';
 const selectedEdge=p.get('edge'),edgeRows=op||layer?layer.edges:edges;
 const selected=edgeRows.find(([a,b,l])=>[a,b,l].join('|')===selectedEdge);
 const edgeNote=selected?'<section class="insight"><b>Handoff · '+esc(selected[2])+'</b><p>'+esc((layer?.ops||layers).find(x=>x.id===selected[0])?.title||selected[0])+' → '+esc((layer?.ops||layers).find(x=>x.id===selected[1])?.title||selected[1])+'</p></section>':'';
 const summary=mode==='engine'?'Follow requests down to model operations and kernels. Select a layer, then an operation to see its state, checks and construction CCs.':'Follow the contract through planning, implementation, external lab execution and acceptance. Edges carry the artifacts agents exchange.';
 const engineSummary='<h2>Layer relationships</h2><p>Read down for execution. The memory column shows state shared across calls. The host supplies compute, storage and transfers outside the image.</p>'+sec('Trace a request',list('Inspect the labeled handoffs. Expand an operation to see its inputs, consumers and the CCs that build it.'))+sec('Source overlay',list('The selected engine supplies pinned implementation examples. Where the inspected source has no binding, the graph keeps the general construction job visible.'));
 const factorySummary='<h2>Factory handoffs</h2><p>The workflow establishes order, dependencies and retry conditions. A CC supplies a reusable engineering job for an agent. The same CC can serve multiple work orders.</p>'+sec('Empty source tree',list('Bind the checkpoint, tokenizer, target and acceptance cases. Assign the missing operations, establish a reference forward pass, boot the image and replay a frozen request.'))+sec('Existing engine',list('Inspect the actual interface and qualify it first. Assign the unmet contract obligations to agents, then repeat the same acceptance cases.'));
 root.innerHTML='<h1>'+overview+'</h1><p class="lead">'+summary+'</p><div class="tools">'+(mode==='engine'?'<label>Source overlay <select id="overlay">'+engines.map(e=>'<option '+(e===overlay?'selected':'')+'>'+esc(e)+'</option>').join('')+'</select></label>':'')+atlas.traces.map(t=>'<a class="pill" data-walk="'+t.id+'" href="'+esc(traceHref(t,0))+'">'+esc(t.title)+'</a>').join('')+'</div>'+walk+
 '<div class="crumb">'+pill(overview,address(mode,'',opts))+(layer?' › '+pill(layer.title,address(mode,layer.id,opts)):'')+(op?' › '+pill(op.title,at(layer.id,op.id,opts)):'')+(role?' › '+esc(role.id):'')+'</div><div class="cols"><div class="graphwrap"><div id="graph"></div></div><aside class="sheet" id="inspector">'+edgeNote+(role?ccPanel(role,overlay):op?opPanel(layer,op,overlay):layer?'<div class="tagline">Subsystem</div><h2>'+esc(layer.title)+'</h2>'+list(layer.summary)+sec('Operations',layer.ops.map(o=>pill(o.title,at(layer.id,o.id,opts))).join(' ')):mode==='engine'?engineSummary:factorySummary)+'</aside></div>';
 drawAtlas(document.querySelector('#graph'),{layers,edges,layer,op,role,roles:roleIndex,mode,overlay,bindings:atlas.sources,group:p.get('group'),onGroup:(l,g)=>set(address(mode,l,{...opts,group:g})),trace:tr?{layers:tr.steps.map(s=>s[0]),ops:[tr.steps[idx][1]]}:null,
 onLayer:l=>set(address(mode,l,opts)),onOp:(l,o)=>set(at(l,o,opts)),onRole:k=>set(at(layer.id,op.id,{...opts,cc:k})),
 onEdge:(a,b,l)=>{if(!edgeRows.some(e=>e[0]===a&&e[1]===b&&e[2]===l)){if(roleIndex.has(b)&&op){set(at(layer.id,op.id,{...opts,cc:b}));return}}
 set(address(mode,layer?.id,{...opts,op:op?.id,edge:[a,b,l].join('|')}))}});
 if(root.querySelector('#overlay'))root.querySelector('#overlay').onchange=e=>set(address(mode,layer?.id,{op:op?.id,cc:role?.id,overlay:e.target.value,trace:tr?.id,step:tr?idx:''}));
 const choice=root.querySelector('#routing-case');if(choice){const update=()=>{const i=choice.selectedIndex;root.querySelector('#routing-out').textContent=['Return five routed IDs with five aligned weights.','Return six routed IDs with six aligned weights.','Return five routed IDs with five aligned weights. Evaluate the shared FFN under its own gate and add its output.'][i]+' Qualify this geometry against checkpoint tensors and backend dispatch.'};choice.onchange=update;update()}
}
window.addEventListener('hashchange',render);render();
