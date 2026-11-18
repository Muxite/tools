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
const essentialTag=value=>value?'<span class="coretag">◆ Essential</span> ':'';
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
function references(rows){
 return rows.map(r=>'<article class="cap-row"><b>'+ext(r.title,r.url)+'</b><p>'+esc(r.detail)+'</p></article>').join('');
}
function museRows(id){
 return Object.entries(atlas.muse.byRole).filter(([k])=>canonical(k)===id).flatMap(([,refs])=>refs).filter((r,i,rs)=>rs.findIndex(x=>x.url===r.url&&x.detail===r.detail)===i);
}
function routingCase(){
 return '<section class="guide"><h3>From one hidden row to expert weights</h3><p>The public reference configuration uses eight routed picks from 256 experts. The inspected Muse implementation accepts routed experts only. Confirm the selected checkpoint’s config and tensor shapes before fixing kernel geometry.</p><ol><li>Project the routing input onto the expert gate. Apply the configured logit multiplier and sigmoid to get one score per expert.</li><li>Add the learned correction bias for ranking. Select distinct expert IDs using the configured routed width.</li><li>Gather the original sigmoid scores at those IDs. Multiply each by route_scale / (selected_score_sum + epsilon). Keep each weight paired with its selected ID.</li><li>Pass the pairs to dispatch. The weight cache can start or join reads for missing experts. Dispatch must preserve the inverse token map until the weighted outputs are combined.</li></ol><h3>A bias changes the winner</h3><p>Small arithmetic fixture with four experts, two picks, unit route scale and zero epsilon. Inputs below are already sigmoid scores.</p><label>Correction on E2 <select id="routing-case"><option value="0.08">+0.08</option><option value="0">Zero</option></select></label><div id="routing-out" aria-live="polite"></div><p><b>Test the interface.</b> Compare ID–weight pairs, then the final weighted output. Exercise a tie at the cutoff and a padded token. Force a cold expert read and verify that storage delays leave the selected pair unchanged.</p></section>';
}
function updateRouting(){
 const select=root.querySelector('#routing-case');if(!select)return;
 const paint=()=>{
  const score=[0.80,0.63,0.60,0.10],bias=Number(select.value);
  const rows=score.map((s,i)=>({id:i,score:s,rank:s+(i===2?bias:0)}));
  const picks=[...rows].sort((a,b)=>b.rank-a.rank).slice(0,2);
  const sum=picks.reduce((s,r)=>s+r.score,0),wrong=picks.reduce((s,r)=>s+r.rank,0);
  root.querySelector('#routing-out').innerHTML='<table><thead><tr><th>Expert</th><th>Score</th><th>Rank score</th><th>Returned weight</th></tr></thead><tbody>'+rows.map(r=>'<tr><td>E'+r.id+'</td><td>'+r.score.toFixed(2)+'</td><td>'+r.rank.toFixed(2)+'</td><td>'+(picks.includes(r)?(r.score/sum).toFixed(4):'—')+'</td></tr>').join('')+'</tbody></table><p><b>Selected</b> '+picks.map(r=>'E'+r.id).join(' and ')+'. '+(bias?'Normalizing the biased scores would give '+picks.map(r=>(r.rank/wrong).toFixed(4)).join(' and ')+'. Those values would change the mixture.':'With zero correction, ranking and mixture calculations start from the same scores.')+'</p>';
 };select.onchange=paint;paint();
}
function normalizationGuide(){
 return '<section class="guide"><h3>Normalization at a decoder site</h3><p>Record the input row, hidden axis, checkpoint epsilon, effective gain and dtype. At an ordinary weighted RMS site, compute the row RMS in the reference precision and apply the effective gain. The input-scale variant first multiplies the row by its gain, then normalizes that scaled row. With nonuniform gain these give different directions or magnitudes.</p><p><b>Worked fixture.</b> With x = [1, 1], gain = [1, 2] and zero epsilon for illustration, post-RMS gain yields [1, 2]. Scaling first yields [0.6325, 1.2649]. Run the real test with the site’s epsilon and dtype. For zero-centered gamma, derive the effective weight with the site’s configured gain center.</p><p><b>Integration check.</b> Capture the branch input, normalized output and residual stream at the same decoder boundary. Compare an unfused FP32 reference with the optimized path on a near-zero row, a mixed-magnitude row and nonuniform gain. Verify who adds the residual and exactly when, then test the next layer input to catch a double addition.</p></section>';
}
const kindTerms={component:'Reusable code an agent can integrate into the engine or factory.',tool:'An executable instrument an agent runs to inspect, transform or measure.',skill:'Integration know-how an agent applies to the target source.',method:'A repeatable procedure with a decision rule or acceptance check.'};
function kindLabel(k){return '<span class="cap-kind cap-'+k+'">'+esc(k)+'</span>'}
function kindStrip(r){return [...new Set(r.contents.map(c=>c.kind))].map(kindLabel).join(' ')}
function capabilityKey(){return details('Capability types',Object.entries(kindTerms).map(([k,v])=>'<p>'+kindLabel(k)+' '+esc(v)+'</p>').join(''))}
function ccDescriptions(ids){
 return '<dl class="cc-descriptions">'+ids.map(id=>'<dt>'+pill(id,'#cc/'+id)+'</dt><dd>'+esc(roleIndex.get(id).review.summary)+'</dd>').join('')+'</dl>';
}
function ccPanel(r,overlay){
 const ex=atlas.assets.filter(a=>r.ex.includes(a.name)), rows=atlas.sources.filter(s=>s.assigned===r.id);
 const target=museRows(r.id),museCode=target.filter(s=>!s.url.includes('/Muxite/tools/'));
 const picks=engines.map(e=>r.examples.find(s=>s.engine===e)).filter(Boolean);
 const examples=references([...museCode.slice(0,1),...picks.slice(0,2)].filter((s,i,rs)=>rs.findIndex(v=>v.url===s.url)===i));
 return '<div class="tagline">'+(r.kind==='factory'?'Software factory':r.target===false?'Reference extension':'Muse engine construction')+' CC</div><h2>'+esc(r.title)+'</h2><p class="cc-summary">'+esc(r.review.summary)+'</p><code>'+esc(r.id)+'</code> '+essentialTag(r.essential)+
 sec('What it owns',list(r.review.boundary))+ (r.id==='model.expert_routing'?routingCase():r.id==='model.decoder_architecture'?normalizationGuide():'')+
 sec('Interface to preserve','<b>Consumes</b>'+list(r.inputs)+'<b>Produces</b>'+list(r.outputs))+sec('Check the result',list(r.check))+sec('Proposed agent handoff',handoffPanel(r.handoff))+(r.tierHandoff?details('When moving KV pages between tiers',handoffPanel(r.tierHandoff)):'')+(r.id==='observability.runtime_events'?nvtxGuide():'')+(['weights.prepare_artifact','weights.decode_blocks','factory.controlled_experiment'].includes(r.id)?pill('Quantization experiments','#quantization'):'')+
 (examples?sec('Implementation evidence',examples+'<div class="pills">'+engines.filter(e=>r.examples.some(s=>s.engine===e)).map(e=>pill(e+' examples',address('sources',r.id,{engine:e}))).join(' ')+'</div>'):'')+details('Design notes',references(target.filter(s=>s.url.includes('/Muxite/tools/'))))+details('Agent capabilities · '+r.contents.length,'<p>Choose the capabilities required by the work order. These are proposed contents.</p>'+r.contents.map(c=>'<article class="cap-row">'+kindLabel(c.kind)+' <b>'+esc(c.name)+'</b><p>'+esc(c.detail)+'</p></article>').join('')+capabilityKey())+
 details('Build or integrate',sec('From scratch',list(r.greenfield))+sec('Existing source',list(r.integration)))+
 details('Pinned engine examples · '+rows.length,rows.map(sourceRow).join(''))+
 details('Existing factory and lab assets · '+ex.length,ex.map(assetRow).join(''))+
 details('Operations served',r.sites.map(([l,o])=>pill(layerIndex.get(l).ops.find(x=>x.id===o).title,at(l,o,{cc:r.id}))).join(' '));
}
function assignmentExample(){
 const rows=[
  ['Storage agent','Implement bounded reads and slot eviction.',['engine.expert_streaming','memory.runtime_arenas']],
  ['Execution agent','Wait for the selected slot and release it after the expert kernel completes.',['engine.expert_streaming','model.expert_ffn']],
  ['Lab agent','Force a cold miss and verify output and peak memory.',['factory.controlled_experiment']]
 ];
 return sec('Example work orders', '<p>Each agent receives the CCs needed for its assigned output. Two agents share the streaming CC so both implement the same slot-lifetime contract.</p>'+rows.map(([name,task,ids])=>'<article class="cap-row"><b>'+esc(name)+'</b><p>'+esc(task)+'</p>'+ids.map(id=>pill(roleIndex.get(id).title,'#cc/'+id)).join(' ')+'</article>').join(''));
}
function workedExample(example,overlay){
 if(!example)return '';
 const table=example.rows?'<dl class="receipt">'+example.rows.map(([field,value])=>'<dt>'+esc(field)+'</dt><dd>'+esc(value)+'</dd>').join('')+'</dl>':'';
 const [l,o]=example.next.split('/');
 const dest=layerIndex.get(l).ops.find(op=>op.id===o);
 return '<section class="worked-example"><div class="tagline">Illustrative example</div><h3>'+esc(example.title)+'</h3>'+list(example.body[0])+table+example.body.slice(1).map(list).join('')+pill(dest.title,at(l,o,{overlay}))+'</section>';
}
function opPanel(layer,op,overlay){
 const relevant=atlas.sources.filter(s=>op.cc.includes(s.assigned));
 const exact=relevant.filter(s=>(op.bindings||[]).includes(s.previous)||(op.bindings||[]).includes(s.id));
 const linked=layer.edges.filter(([a,b])=>a===op.id||b===op.id);
 return '<div class="tagline">'+esc(layer.title)+'</div><h2>'+esc(op.title)+'</h2>'+essentialTag(op.essential)+list(op.detail)+workedExample(op.example,overlay)+(layer.id==='f_plan'&&['assign','workorder'].includes(op.id)?assignmentExample():'')+sec('Optimize',list(op.metric))+sec('Check',list(op.check))+
 (op.condition?sec('Applies when',list(op.condition)):'')+sec('CCs for this operation',op.cc.map(k=>pill(roleIndex.get(k).title,at(layer.id,op.id,{cc:k,overlay}))).join(' '))+
 sec('Data flow',linked.map(([a,b,l])=>{const other=a===op.id?b:a;return '<p>'+esc(a===op.id?'Sends ':'Receives ')+esc(l)+(a===op.id?' to ':' from ')+pill(layer.ops.find(n=>n.id===other).title,at(layer.id,other,{overlay}))+'</p>'}).join(''))+
 sec('Implementation examples',exact.slice(0,2).map(sourceRow).join(''))+
 details('Related CC bindings · '+(relevant.length-exact.length),relevant.filter(s=>!exact.includes(s)).map(sourceRow).join(''));
}
function library(query){
 const q=query.get('q')||'';
 root.innerHTML='<h1>All CCs</h1><p class="lead">A CC bundles capabilities for a job. An agent can receive several CCs, and several agents can use the same CC. Search by responsibility, capability or source symbol.</p><div class="tools"><input id="search" type="search" aria-label="Search CCs"><select id="scope" aria-label="CC scope"><option>All CCs</option><option>Engine</option><option>Software factory</option><option>Reference extensions</option></select><select id="captype" aria-label="Capability type"><option value="">All capability types</option>'+Object.keys(kindTerms).map(k=>'<option>'+k+'</option>').join('')+'</select></div>'+capabilityKey()+'<div id="results"></div>';
 const input=root.querySelector('#search'),scope=root.querySelector('#scope');input.value=q;scope.value=query.get('scope')||'All CCs';const type=root.querySelector('#captype');type.value=query.get('type')||'';
 function update(){
 const terms=input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
 const jobs=atlas.roles.filter(r=>{const hay=[r.id,r.title,r.review.summary,r.why,r.capabilities,...r.contents.map(c=>[c.name,c.detail,c.kind].join(" ")),...Object.keys(atlas.aliases).filter(k=>atlas.aliases[k]===r.id),...atlas.sources.filter(s=>s.assigned===r.id).map(s=>s.symbol)].join(' ').toLowerCase();return (!type.value||r.contents.some(c=>c.kind===type.value))&&terms.every(x=>hay.includes(x))&&(scope.value==='All CCs'||(scope.value==='Reference extensions'?r.target===false:r.target!==false&&(scope.value==='Software factory')===(r.kind==='factory')))});
 root.querySelector('#results').innerHTML='<p class="caption">'+jobs.length+' CCs</p><div class="cards">'+jobs.map(r=>'<a class="listing" href="#cc/'+esc(r.id)+'"><strong>'+esc(r.title)+'</strong><p class="cc-summary">'+esc(r.review.summary)+'</p>'+essentialTag(r.essential)+'<code>'+esc(r.id)+'</code><div class="caption">'+(r.target===false?'Reference extension':r.kind==='factory'?'Software factory':'Engine')+'</div><p>'+esc(r.why)+'</p><div>'+kindStrip(r)+'</div></a>').join('')+'</div>';
 history.replaceState(history.state,'',address('library','',{q:input.value,type:type.value,scope:scope.value==='All CCs'?'':scope.value}));
 }
 input.oninput=update;scope.onchange=update;type.onchange=update;update();
}
function implementationPaths(){
 const paths=[
   {engine:'ds4',title:'Routed rows and weighted output',intro:'Follow the CPU batched routed path. The dispatcher owns the forward permutation and the inverse mapping used to restore each token.',steps:[
     ['Score and select','For scored routing, rank with the optional correction bias, gather the original transformed scores at the winning IDs, then normalize and scale. Some layers select IDs by token lookup.','model.expert_routing','ds4.c#L13062'],
     ['Group by expert','Count assignments per expert, prefix-sum the counts and scatter pair indices into contiguous ranges. A pair index retains both the token and its choice slot.','merge.expert_contributions','ds4.c#L13427'],
     ['Execute expert rows','The Q8 path prepares one quantized input row per token for reuse by its selected experts. Expert workers use the pair table to find those rows.','model.expert_ffn','ds4.c#L13443'],
     ['Restore token order','Down-projection accumulation follows the stored assignments into token output rows. Test grouped execution against a token-by-token reference with two tokens sharing an expert.','merge.expert_contributions','ds4.c#L13507']]},
   {engine:'Strata',title:'An expert read reaches the cache',intro:'Trace one file-backed cache fill. Three events matter to a worker implementing storage-backed MoE: the storage read completes, the demanded bytes become available, and the staging buffer becomes reusable.',steps:[
     ['Read a staged expert','A prefetch worker claims a staging slot by layer and expert, reads its bytes and publishes completion under the stage lock. A failed read removes the slot mapping.','engine.expert_streaming','src/core/expert_source.cpp#L1369'],
     ['Join or fill on demand','The consumer waits for an in-flight read of the same key, then rechecks the key before accepting the pointer. An unclaimed miss takes the synchronous fill path.','engine.expert_streaming','src/core/expert_source.cpp#L2148'],
     ['Submit the cache fill','The dispatcher requests bytes after it has a candidate cache slot. A failed fill records the failing layer and expert. A successful fill registers the source buffer against the copy stream.','engine.expert_streaming','src/core/expert_source.cpp#L5492'],
     ['Protect the source buffer','For pinned staging memory, record a CUDA event behind the copy. If the event cannot be created or recorded, synchronize the stream. Force overlapping fills in a test and check that every expert still reads its own weights.','engine.expert_streaming','src/core/expert_source.cpp#L2102']]}
 ];
 return '<section id="paths-section" tabindex="-1" class="sheet"><h2>Implementation paths</h2>'+paths.map(path=>{
   const repo=atlas.repositories.find(r=>r.engine===path.engine);
   const steps=path.steps.map(([title,body,cc,location])=>'<li><strong>'+esc(title)+'</strong><p>'+esc(body)+'</p>'+pill(cc,'#cc/'+cc)+' '+ext('Source ↗',repo.base+'/blob/'+repo.pin+'/'+location)+'</li>').join('');
   return details(path.engine+' · '+path.title,'<p>'+esc(path.intro)+'</p><ol>'+steps+'</ol>');
 }).join('')+'</section>';
}
function evidence(id,params){
 if(id&&sourceSlice(id,params.get('engine')))return;
 const docs='https://github.com/Muxite/tools/blob/548ed63a137382c2c9e1b7b64e537f50da4245db/';
 const notes=docs+'DGX-SPARK/planning/muse-workshop/';
 const destinations=[['paths-section','Implementation paths'],['matrix-section','Engine evidence by CC'],['history-section','Integration history']];
 const shortcuts='<div class="tools" aria-label="Evidence sections">'+destinations.map(([id,label])=>'<button type="button" class="pill" data-section="'+id+'">'+label+'</button>').join('')+'</div>';
 root.innerHTML='<h1>Implementation evidence</h1>'+shortcuts+implementationPaths()+ownershipMatrix()+'<p class="lead">Source bindings establish implementation choices. Asset records distinguish declarations, local fixtures and measured runs.</p><div class="cards">'+atlas.repositories.map(r=>'<article class="listing"><h2>'+esc(r.engine)+'</h2><p>'+ext(r.pin.slice(0,12),r.base+'/tree/'+r.pin)+' · '+new Set(atlas.roles.flatMap(cc=>cc.examples.filter(x=>x.engine===r.engine).map(x=>x.url))).size+' distinct source locations</p>'+'</article>').join('')+'</div>'+
 receiptGuide()+sec('Muse Spark Open and DGX Spark',references(atlas.muse.refs))+'<div class="sheet" id="history-section" tabindex="-1"><h2>Integration history</h2><p>The native parent supplied 42 top-level and eight nested CC manifests. The workflow merge retained all 50. The subsequent snapshot added throughput_campaign and revised standard_benchmark with cancellation support. The historical two Strata screens reported +8.30% and +9.28% against a 10% threshold on their frozen workload.</p>'+
 ext('Native workflow integration',docs+'DGX-SPARK/NATIVE-WORKFLOW-INTEGRATION.md')+
 '<h3>Design references</h3><p>The 17-page <i>Inference Engine: Layered Architecture and Profiling Plan</i> supplies the startup, request, scheduler, generation, model, kernel and host vocabulary. Its memory column spans execution layers. The graph treats the host as a deployment dependency and attributes queue, state and launch waits individually.</p>'+ext('Inference layers and profiling',notes+'Inference%20layers%20and%20profiling.md')+' · '+ext('Post-presentation design revision',notes+'Post-presentation%20design%20revision.md')+
 details('Existing assets · '+atlas.assets.length,atlas.assets.map(assetRow).join(''))+
 details('Pinned source index · '+atlas.sources.length,atlas.sources.map(sourceRow).join(''))+
 details('Inventory decisions',Object.entries(atlas.mergers).map(([a,b])=>'<p>'+esc(a)+' → '+pill(b,'#cc/'+b)+'</p>').join('')+'<p>Image, audio and diffusion work is outside the text-engine contract.</p>')+'</div>';
 for(const button of root.querySelectorAll('[data-section]')){
   button.onclick=()=>{
     const section=document.getElementById(button.dataset.section);
     section.focus({preventScroll:true});
     section.scrollIntoView({block:'start'});
   };
 }
}
