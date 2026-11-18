'use strict';
const atlas=JSON.parse(document.querySelector('#dataset').textContent);
const roleIndex=new Map(atlas.roles.map(r=>[r.id,r]));
const allLayers=[...atlas.engine,...atlas.factory],layerIndex=new Map(allLayers.map(l=>[l.id,l]));
const root=document.querySelector('main');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const array=v=>Array.isArray(v)?v:[v];
const list=v=>array(v).map(s=>'<p>'+esc(s)+'</p>').join('');
const ext=(t,u)=>u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(t)+'</a>':esc(t);
const pill=(t,h)=>'<a class="pill" href="'+esc(h)+'">'+esc(t)+'</a>';
const sec=(h,s)=>s?'<section><h3>'+esc(h)+'</h3>'+s+'</section>':'';
const details=(t,s)=>s?'<details><summary>'+esc(t)+'</summary>'+s+'</details>':'';
const engines=['Strata','llama.cpp','ds4','SGLang'];
const factoryId=id=>atlas.factory.some(l=>l.id===id);
const canonical=id=>atlas.aliases[id]||id;
function address(mode,layer='',params={}){
 const p=new URLSearchParams();for(const [k,v] of Object.entries(params))if(v!==undefined&&v!==null&&v!=='')p.set(k,v);
 return '#'+mode+(layer?'/'+encodeURIComponent(layer):'')+(p.size?'?'+p:'');
}
function at(layer,op,params={}){return address(factoryId(layer)?'factory':'engine',layer,{...params,op})}
function sourceRow(s){return '<article class="insight"><div class="tagline">'+esc(s.engine)+' · '+esc(s.component)+'</div><b>'+ext(s.symbol,s.url)+'</b><p>'+esc(s.detail)+'</p><p><strong>Check</strong> · '+esc(s.check)+'</p><small>'+esc(s.path)+'</small></article>'}
function assetRow(a){return '<article class="insight"><b>'+ext(a.name,a.source)+'</b><p>'+esc(a.status)+'</p><p>'+esc(a.scope)+'</p><small>'+ext(a.evidenceLabel,a.evidence)+' · '+esc(a.revision?.slice(0,12))+'</small></article>'}
function transfer(r,e){
 const t=atlas.transfers.find(x=>canonical(x.role)===r.id);
 if(!t)return '';
 const c=t.cases[e];return details('Transfer to '+e,'<p>'+esc(t.shared)+'</p>'+sec('Adapt',list(c.adapt))+sec('Qualify',list(c.check))+list(c.status))
}
function routingCase(){
 return '<section><h3>Routing contract</h3><label>Per-token rule <select id="routing-case"><option>5 routed</option><option>6 routed</option><option>5 routed + 1 shared</option></select></label><p id="routing-out"></p></section>';
}
function ccPanel(r,overlay){
 const ex=atlas.assets.filter(a=>r.ex.includes(a.name)), rows=atlas.sources.filter(s=>s.assigned===r.id&&s.engine===overlay);
 return '<div class="tagline">'+(r.kind==='factory'?'Software factory':'Engine construction')+' CC</div><h2><code>'+esc(r.id)+'</code></h2>'+
 sec('Engineering job',list(r.why))+sec('When to use it',list(r.when))+sec('Produces',list(r.outputs))+
 (r.id==='model.expert_routing'?routingCase():'')+sec('Verification',list(r.check))+
 details('Contract choices and capabilities',list(r.decisions)+list(r.capabilities))+
 details('Build or integrate',sec('Inputs',list(r.inputs))+sec('From scratch',list(r.greenfield))+sec('Existing source',list(r.integration)))+
 details('Included jobs',r.variantJobs.map(x=>sec(x.id,list(x.reason)+list(x.check))).join(''))+
 transfer(r,overlay)+details(overlay+' · '+rows.length+' source bindings',rows.map(sourceRow).join(''))+
 sec('Existing work',ex.length?details(ex.length+' asset records',ex.map(assetRow).join('')):'<p class="muted">Design only in the local inventory.</p>')+
 details('Related evidence',atlas.assets.filter(a=>r.reuse.includes(a.name)&&!r.ex.includes(a.name)).map(assetRow).join(''))+
 details('Other worksites',r.sites.map(([l,o])=>pill(layerIndex.get(l).ops.find(x=>x.id===o).title,at(l,o,{cc:r.id,overlay}))).join(' '));
}
function opPanel(layer,op,overlay){
 const relevant=atlas.sources.filter(s=>s.engine===overlay&&op.cc.includes(s.assigned));
 const exact=relevant.filter(s=>(op.bindings||[]).includes(s.previous)||(op.bindings||[]).includes(s.id));
 const linked=layer.edges.filter(([a,b])=>a===op.id||b===op.id);
 return '<div class="tagline">'+esc(layer.title)+'</div><h2>'+esc(op.title)+'</h2>'+list(op.detail)+sec('Optimize',list(op.metric))+sec('Check',list(op.check))+
 (op.condition?sec('Applies when',list(op.condition)):'')+sec('CCs',op.cc.map(k=>pill(k,at(layer.id,op.id,{cc:k,overlay}))).join(' '))+
 sec('Data flow',linked.map(([a,b,l])=>{const other=a===op.id?b:a;return '<p>'+esc(a===op.id?'Sends ':'Receives ')+esc(l)+(a===op.id?' to ':' from ')+pill(layer.ops.find(n=>n.id===other).title,at(layer.id,other,{overlay}))+'</p>'}).join(''))+
 sec(overlay+' implementation',exact.length?exact.map(sourceRow).join(''):'<p class="muted">No operation-specific source binding recorded for this revision.</p>')+
 details('Related CC bindings · '+(relevant.length-exact.length),relevant.filter(s=>!exact.includes(s)).map(sourceRow).join(''));
}
function library(query){
 const q=query.get('q')||'';
 root.innerHTML='<h1>CC library</h1><p class="lead">Find a job by operation, capability, former identity or source symbol.</p><div class="tools"><input id="search" type="search" aria-label="Search CCs"><select id="scope" aria-label="CC scope"><option>All CCs</option><option>Engine</option><option>Software factory</option></select></div><div id="results"></div>';
 const input=root.querySelector('#search'),scope=root.querySelector('#scope');input.value=q;scope.value=query.get('scope')||'All CCs';
 function update(){
 const terms=input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
 const jobs=atlas.roles.filter(r=>{const hay=[r.id,r.why,r.capabilities,...Object.keys(atlas.aliases).filter(k=>atlas.aliases[k]===r.id),...atlas.sources.filter(s=>s.assigned===r.id).map(s=>s.symbol)].join(' ').toLowerCase();return terms.every(x=>hay.includes(x))&&(scope.value==='All CCs'||(scope.value==='Software factory')===(r.kind==='factory'))});
 root.querySelector('#results').innerHTML='<p class="caption">'+jobs.length+' CCs</p><div class="cards">'+jobs.map(r=>'<a class="listing" href="#cc/'+esc(r.id)+'"><strong>'+esc(r.id)+'</strong><p>'+esc(r.why)+'</p></a>').join('')+'</div>';
 history.replaceState(null,'',address('library','',{q:input.value,scope:scope.value==='All CCs'?'':scope.value}));
 }
 input.oninput=update;scope.onchange=update;update();
}
function evidence(){
 const docs='https://github.com/Muxite/tools/blob/548ed63a137382c2c9e1b7b64e537f50da4245db/';
 const notes=docs+'DGX-SPARK/planning/muse-workshop/';
 root.innerHTML='<h1>Evidence</h1><p class="lead">Source bindings establish implementation choices. Asset records distinguish declarations, local fixtures and measured runs.</p><div class="cards">'+atlas.repositories.map(r=>'<article class="listing"><h2>'+esc(r.engine)+'</h2><p>'+ext(r.pin.slice(0,12),r.base+'/tree/'+r.pin)+' · '+atlas.sources.filter(x=>x.engine===r.engine).length+' text-engine bindings</p>'+pill('Inspect on graph',address('engine','',{overlay:r.engine}))+'</article>').join('')+'</div>'+
 '<div class="sheet"><h2>Integration history</h2><p>The native parent supplied 42 top-level and eight nested CC manifests. The workflow merge retained all 50. The subsequent snapshot added throughput_campaign and revised standard_benchmark with cancellation support. The historical two Strata screens reported +8.30% and +9.28% against a 10% threshold on their frozen workload.</p>'+
 ext('Native workflow integration',docs+'DGX-SPARK/NATIVE-WORKFLOW-INTEGRATION.md')+
 '<h3>Design references</h3><p>The 17-page <i>Inference Engine: Layered Architecture and Profiling Plan</i> supplies the startup, request, scheduler, generation, model, kernel and host vocabulary. Its memory column spans execution layers. The graph treats the host as a deployment dependency and attributes queue, state and launch waits individually.</p>'+ext('Inference layers and profiling',notes+'Inference%20layers%20and%20profiling.md')+' · '+ext('Post-presentation design revision',notes+'Post-presentation%20design%20revision.md')+
 details('Existing assets · '+atlas.assets.length,atlas.assets.map(assetRow).join(''))+
 details('Pinned source index · '+atlas.sources.length,atlas.sources.map(sourceRow).join(''))+
 details('Inventory decisions',Object.entries(atlas.mergers).map(([a,b])=>'<p>'+esc(a)+' → '+pill(b,'#cc/'+b)+'</p>').join('')+'<p>Image, audio and diffusion work is outside the text-engine contract.</p>')+'</div>';
}
