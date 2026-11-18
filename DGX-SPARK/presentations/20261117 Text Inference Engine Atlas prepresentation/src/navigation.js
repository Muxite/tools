const legacyNodes={intent:'f_spec/intake',contract:'f_spec/freeze',inspect:'f_plan',plan:'f_plan',build:'f_build',profile:'f_lab/profile',verification:'f_lab/quality',evidence:'f_evidence',model:'startup/config',tokenizer:'interface/encode',weights:'startup/bind',placement:'startup/place',backend:'backend/dispatch',serving:'interface/accept',scheduler:'schedule/admit',batch:'schedule/batch',prefill:'generate/prefill',decode:'generate/step',attention:'model/attend',sequence:'state/append',dense:'model/dense',routing:'model/route',experts:'model/expert',merge:'model/combine',sampling:'generate/sample',output:'interface/emit',graph:'backend/lower',memory:'state',streaming:'state/fill',cpu:'backend/cpu',transfer:'backend/streams',parallel:'model/dispatch',cuda:'backend/dispatch',observability:'backend/signal',embedding:'model/embed',norm:'model/norm',head:'model/head',shared:'model/shared'};
function render(){
 const wasGraph=document.querySelector('#graph')?.contains(document.activeElement);
 const [path,q='']=location.hash.slice(1).split('?'),[view='engine',raw='']=path.split('/'),id=decodeURIComponent(raw),p=new URLSearchParams(q);
 const overlay=engines.includes(p.get('overlay'))?p.get('overlay'):engines.includes(id)?id:'Strata';
 const opts={}, set=h=>location.hash=h;
 let mode=view==='factory'?'factory':'engine',layer=layerIndex.get(id),opId=p.get('op'),cc=canonical(p.get('cc')),outside=false;
 if(view==='cc'||view==='node'||view==='compare'||view==='diagrams'||view==='map'){
   if(view==='cc'||p.get('role')){
     cc=canonical(id&&view==='cc'?id:p.get('role'));const job=roleIndex.get(cc);
     if(job){const legacySite=id==='memory.kv_tiering'?['state','tier']:id==='model.normalization'?['model','norm']:id==='model.expert_routing'||id==='routing.top_k'?['model','route']:null;
     const preferred=(legacySite&&job.sites.some(([l,o])=>l===legacySite[0]&&o===legacySite[1])?legacySite:null)||job.review.site.split('/');[layer,opId]=preferred||job.sites[0];layer=layerIndex.get(layer)}
     else outside=atlas.excluded.includes(cc);
   }else{
     const topic=p.get('topic'),legacy=legacyNodes[id]||({routing:'model/route',serving:'schedule',state:'state',execution:'backend',resources:'backend',startup:'startup',moe:'model/route',factory:'f_plan',construction:'f_build',model:'model'})[topic];
     if(legacy){const [l,o]=legacy.split('/');layer=layerIndex.get(l);opId=o}
     outside=id==='media';
   }
   if(layer)mode=factoryId(layer.id)?'factory':'engine';
 }
 const page=['library','sources','quantization','construction'].includes(view)?view:mode;
 document.querySelectorAll('nav a').forEach(a=>{if(a.dataset.tab===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 if(page==='construction'){construction(id);return}if(page==='library'){library(p);return}if(page==='sources'){evidence(id,p);return}if(page==='quantization'){quantization();return}
 if(outside){root.innerHTML='<h1>Historical media role</h1><p class="lead">This work belonged to the earlier multimodal inventory. The current engine contract covers text generation.</p>'+pill('Text engine','#engine');return}
 const fullLayers=mode==='factory'?atlas.factory:atlas.engine,edges=mode==='factory'?atlas.factoryEdges:atlas.edges;
 if(!fullLayers.includes(layer))layer=null;
 const extension=roleIndex.get(cc)?.target===false||layer?.ops.find(o=>o.id===opId)?.target===false;
 const layers=fullLayers.map(l=>{
   const ops=l.ops.filter(o=>o.target!==false||(extension&&l.id===layer?.id&&o.id===opId)).map(o=>({...o,cc:o.cc.filter(k=>roleIndex.get(k).target!==false||k===cc)}));
   const ids=new Set(ops.map(o=>o.id));
   return {...l,ops,edges:l.edges.filter(([a,b])=>ids.has(a)&&ids.has(b))};
 });
 layer=layers.find(l=>l.id===layer?.id);
 const op=layer?.ops.find(x=>x.id===opId),role=op?.cc.includes(cc)?roleIndex.get(cc):null;
 const tr=atlas.traces.find(x=>x.id===p.get('trace')),idx=Math.min(tr?.steps.length-1||0,Math.max(0,Number(p.get('step'))||0));
 const traceHref=(t,i)=>at(t.steps[i][0],t.steps[i][1],{trace:t.id,step:i});
 const walk=tr?'<div class="insight"><strong>'+esc(tr.title)+'</strong><p>'+esc(tr.steps[idx][3])+'</p><div class="steps">'+tr.steps.map(([l,o],i)=>'<a href="'+esc(traceHref(tr,i))+'" '+(i===idx?'aria-current="step"':'')+'>'+esc((i+1)+'. '+layerIndex.get(l).ops.find(x=>x.id===o).title)+'</a>').join('')+'</div></div>':'';
 const overview=mode==='engine'?'Muse Spark Open on DGX Spark':'Software factory';
 const selectedEdge=p.get('edge'),edgeRows=op||layer?layer.edges:edges;
 const selected=selectedEdge?.split('|');
 function endpointTitle(id){if(id.startsWith('@group/'))return id.slice(7);return (layer?.ops||layers).find(x=>x.id===id)?.title||roleIndex.get(id)?.id||id}
 const matchEnd=(actual,shown)=>actual===shown||('@group/'+(layer?.ops.find(x=>x.id===actual)?.group||''))===shown;
 const members=selected&&layer?layer.edges.filter(([a,b])=>matchEnd(a,selected[0])&&matchEnd(b,selected[1])):[];
 const edgeNote=selected?.length===3?'<section class="insight"><b>Handoff · '+esc(selected[2])+'</b><p>'+esc(endpointTitle(selected[0]))+' → '+esc(endpointTitle(selected[1]))+'</p>'+members.filter(e=>e[0]!==selected[0]||e[1]!==selected[1]).map(([a,b,l])=>'<p>'+pill(endpointTitle(a),at(layer.id,a,opts))+' → '+pill(endpointTitle(b),at(layer.id,b,opts))+' · '+esc(l)+'</p>').join('')+'</section>':'';
 const summary=mode==='engine'?'Text generation on one 128 GB DGX Spark. The model exceeds unified memory. Follow a routed token to its expert weights on storage, or open a subsystem to see which CCs own its operations.':'The planner assigns work orders and CCs to agents. Each CC bundles capabilities the agent can use. Follow the artifacts from the contract to the verified image.';
 const engineSummary='<h2>Request execution</h2><p>Read down for execution. The memory column shows state shared across calls. The host supplies compute, storage and transfers outside the image.</p>'+sec('Prefill and decode',list('Prefill processes a prompt span and establishes sequence state. Decode usually advances one committed token per sequence and reads its retained KV. Both invoke the same model with different shapes.'))+sec('Routed weights',list('The router owns the expert IDs and mixture weights. Residency and streaming determine when the selected weights are ready. A prediction can start a fetch, but only the authoritative route decides which outputs to combine.'))+sec('Inspect on graph',pill('Token admission',at('schedule','admit',opts))+' '+pill('Expert routing',at('model','route',opts))+' '+pill('Kernel dispatch',at('backend','dispatch',opts)));
 const factoryOwners=[['compiler.engine_contract','Turn requirements into a frozen contract.'],['factory.workflow_planning','Inspect gaps and issue work orders.'],['factory.source_integration','Produce a reviewable repository diff.'],['factory.builder','Build an image with the executable and its dependencies.'],['factory.controlled_experiment','Turn a pinned image and test question into a scoped verdict.']].map(([key,job])=>'<p>'+pill(key,'#cc/'+key)+' '+esc(job)+'</p>').join('');
 const factorySummary='<h2>Five factory CCs</h2>'+factoryOwners+receiptGuide()+'<p>The workflow establishes order, dependencies and retry conditions. A CC supplies a reusable engineering job for an agent. Each agent can receive several CCs, and several agents can use the same CC on different work orders.</p>'+pill('Example agent assignments',at('f_plan','workorder',opts))+sec('Empty source tree',list('Bind the checkpoint, tokenizer, target and acceptance cases. Assign the missing operations, establish a reference forward pass, boot the image and replay a frozen request.'))+sec('Existing engine',list('Inspect the actual interface and qualify it first. Assign the unmet contract obligations to agents, then repeat the same acceptance cases.'));
 root.innerHTML='<h1>'+overview+'</h1><p class="lead">'+summary+'</p><div class="tools">'+pill('Build from scratch','#construction')+atlas.traces.map(t=>'<a class="pill" data-walk="'+t.id+'" href="'+esc(traceHref(t,0))+'">'+esc(t.title)+'</a>').join('')+'</div><details class="corekey"><summary><span>◆ Essential</span> · ◇ Contains essential operations</summary><p>'+esc(atlas.baseline)+' Unmarked jobs can become required under a different contract.</p></details>'+walk+
 (layer?'<div class="crumb">'+pill(overview,address(mode,'',opts))+(layer?' › '+pill(layer.title,address(mode,layer.id,opts)):'')+(op?' › '+pill(op.title,at(layer.id,op.id,opts)):'')+(role?' › '+esc(role.id):'')+'</div>':'')+'<div class="cols"><div class="graphwrap"><div id="graph"></div></div><aside class="sheet" id="inspector">'+edgeNote+(role?ccPanel(role,overlay):op?opPanel(layer,op,overlay):layer?'<div class="tagline">Subsystem</div><h2>'+esc(layer.title)+'</h2>'+list(layer.summary)+sec('Operations',layer.ops.map(o=>pill(o.title,at(layer.id,o.id,opts))).join(' ')):mode==='engine'?engineSummary:factorySummary)+'</aside></div>';
 drawAtlas(document.querySelector('#graph'),{layers,edges,layer,op,role,roles:roleIndex,mode,overlay,bindings:[],cross:atlas.cross,group:p.get('group'),onGroup:(l,g)=>set(address(mode,l,{...opts,group:g})),trace:tr?{layers:tr.steps.map(s=>s[0]),ops:[tr.steps[idx][1]]}:null,
 onLayer:l=>set(address(mode,l,opts)),onOp:(l,o)=>set(at(l,o,opts)),onRole:(k,l,o)=>{const place=layer?.ops.find(v=>v.id===(o||op?.id)&&v.cc.includes(k))||layer?.ops.find(v=>v.cc.includes(k));if(place)set(at(l||layer.id,place.id,{cc:k,...(tr&&place.id===op?.id?{trace:tr.id,step:idx}:{})}))},
 onEdge:(a,b,l)=>{if(!edgeRows.some(e=>e[0]===a&&e[1]===b&&e[2]===l)){if(roleIndex.has(b)){const from=layer?.ops.find(o=>o.id===a&&o.cc.includes(b))||layer?.ops.find(o=>o.cc.includes(b));if(from)set(at(layer.id,from.id,{cc:b}));return}}
 set(address(mode,layer?.id,{...opts,op:op?.id,group:p.get('group'),edge:[a,b,l].join('|')}))}});
 if(wasGraph){const targetId=role?.id||op?.id;
 const target=targetId?Array.from(root.querySelectorAll('#graph [data-ax-id]')).find(n=>n.dataset.axId===targetId):root.querySelector('#graph button, #graph [tabindex="0"]');target?.focus({preventScroll:true})}
 if(role&&innerWidth<=980){const panel=root.querySelector('#inspector');panel.tabIndex=-1;panel.focus({preventScroll:true});panel.scrollIntoView({block:'start'})}
 updateRouting();
}
// Preserve the entry being left so browser Back restores this diagram or filtered list.
const backButton=document.querySelector('#page-back');
let depth=history.state?.atlasDepth||0;
function rememberView(){
 const opened=[...root.querySelectorAll('details')].map((d,i)=>d.open?i:-1).filter(i=>i>=0);
 history.replaceState({...history.state,atlasDepth:depth,atlasView:{y:scrollY,opened}},'');
}
function navigate(){
 const saved=history.state?.atlasView;
 depth=history.state?.atlasDepth??depth+1;
 history.replaceState({...history.state,atlasDepth:depth},'');
 backButton.disabled=depth===0;
 render();
 if(saved){const ds=root.querySelectorAll('details');for(const i of saved.opened)if(ds[i])ds[i].open=true;requestAnimationFrame(()=>window.scrollTo(0,saved.y))}
 else if(innerWidth>980 || !root.querySelector('#inspector code'))window.scrollTo(0,0);
}
document.addEventListener('click',rememberView,true);
document.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')rememberView()},true);
backButton.onclick=()=>{if(depth>0)history.back()};
history.replaceState({...history.state,atlasDepth:depth},'');
window.addEventListener('hashchange',navigate);navigate();
