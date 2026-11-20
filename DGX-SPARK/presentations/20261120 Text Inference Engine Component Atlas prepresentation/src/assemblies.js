const assemblyRecords = {
  request: {
    title:'Request interface', brief:'Client requests, prompt tokens and streamed text.',
    role:'The gateway accepts a completion request. The codec produces prompt token IDs and converts committed output IDs back into text.',
    children:['serving.engine_image_gateway','tokenizer.token_codec'],
    depends:[['scheduler.request_scheduler','Admits tokenized requests and handles cancellation.'],['observability.runtime_event_recorder','Supplies correlated records for diagnostic requests.']]
  },
  generation: {
    title:'Generation controller', brief:'Request scheduling, token batches and sampling.',
    role:'The scheduler selects work. The generation loop advances each sequence and sends vocabulary scores to the sampler.',
    children:['scheduler.request_scheduler','batch.batch_layout_builder','decode.generation_loop','sampling.token_sampler','decode.speculative_decoder'],
    depends:[['model.decoder_stack','Evaluates the scheduled prompt or decode rows.'],['memory.prefix_state_cache','Supplies a verified state handle when a reusable prompt prefix matches.']]
  },
  decoder: {
    title:'Decoder model', brief:'Token embeddings, decoder layers and vocabulary scores.',
    role:'Token embeddings enter the decoder stack. Repeated layers transform the hidden rows before the vocabulary head projects them to scores.',
    children:['model.token_embedding_layer','model.decoder_stack','@decoder/layer','model.vocabulary_projection_head'],
    depends:[['weights.checkpoint_reader','Supplies validated tensor bindings.'],['backend.kernel_dispatcher','Runs supported operators on the selected device.']]
  },
  'decoder/layer': {
    title:'Decoder layer', brief:'Attention and feed-forward computation with residual connections.',
    role:'The decoder stack supplies the order of normalization and residual additions. The checkpoint selects the attention or recurrent path and the dense or routed feed-forward block.',
    children:['attention.dense_attention_operator','attention.sparse_attention_operator','dense.dense_feed_forward_block','@decoder/layer/routed'],
    depends:[['memory.sequence_kv_cache','Supplies visible key/value rows and receives appended keys and values.'],['sequence.recurrent_state_operator','Updates persistent sequence state in a checkpoint with recurrent layers.']]
  },
  'decoder/layer/routed': {
    title:'Routed feed-forward block', brief:'Expert selection, grouped execution and weighted recombination.',
    role:'The router assigns expert IDs and weights to each token. The dispatcher groups rows, the selected experts evaluate them, and the combiner restores token order and applies the mixture weights.',
    children:['model.expert_router','merge.expert_row_dispatcher_and_combiner','model.expert_feed_forward_block'],
    depends:[['engine.expert_weight_cache','Supplies selected expert weights and retains each slot until its final reader finishes.'],['parallel.distributed_expert_exchange','Exchanges grouped rows and returns contributions when expert ownership spans devices.']]
  },
  weights: {
    title:'Model weights', brief:'Checkpoint tensors, placement and expert weight residency.',
    role:'The checkpoint reader binds tensor byte ranges. The placement planner budgets resident and streamed weights. The expert cache supplies ready handles for selected weights.',
    children:['weights.checkpoint_reader','placement.weight_placement_planner','engine.expert_weight_cache','engine.host_expert_store','routing.expert_demand_predictor','weights.engram_row_cache','weights.adapter_binder','weights.weight_pack_compiler'],
    depends:[['host.ssd','Stores checkpoint shards and packed expert bytes.'],['host.dram','Holds resident weights, staging buffers and expert slots.'],['memory.workspace_allocator','Provides the scratch requirements used in the placement budget.']]
  },
  state: {
    title:'Sequence state', brief:'Per-sequence keys, values, recurrent state and reusable prefixes.',
    role:'Sequence state persists between token steps. Prefix reuse can share a compatible saved state, and recurrent layers maintain their own state alongside attention caches.',
    children:['memory.sequence_kv_cache','memory.prefix_state_cache','sequence.recurrent_state_operator'],
    depends:[['batch.batch_layout_builder','Supplies sequence identities, positions and state mappings for scheduled rows.'],['host.dram','Stores active state pages and persistent tensors.']]
  },
  backend: {
    title:'Execution backend', brief:'Kernel dispatch, working memory and device execution.',
    role:'The backend binds model operations to supported kernels and buffers. Graph replay and distributed execution depend on compatible shapes, storage and deployment topology.',
    children:['backend.kernel_dispatcher','backend.quantized_matmul_kernel','backend.cpu_weight_repack','memory.workspace_allocator','weights.weight_block_decoder','graph.execution_graph_backend','parallel.distributed_execution_coordinator','parallel.distributed_expert_exchange'],
    depends:[['host.hostcpu','Runs host-side work and supported CPU kernels.'],['host.device','Executes device launches and records completion events.']]
  },
  observability: {
    title:'Runtime observability', brief:'Cross-cutting instrumentation inside the engine.',
    role:'The recorder correlates execution and wait events across requests, layers, experts and devices. Operators retrieve the resulting diagnostics through the image gateway.',
    children:['observability.runtime_event_recorder'],depends:[['serving.engine_image_gateway','Publishes the diagnostic interface.']]
  },
  host: {
    title:'Host platform', brief:'DGX Spark compute, unified memory and local storage.',
    role:'These platform resources supply compute, memory and checkpoint bytes to the engine image.',
    children:['host.hostcpu','host.device','host.dram','host.ssd'],depends:[]
  }
};
const assemblyOrder = ['request','generation','decoder','weights','state','backend'];
const assemblyModes = {
  'weights.weight_pack_compiler':'Build-time tooling',
  'weights.adapter_binder':'Conditional · adapters',
  'weights.weight_block_decoder':'Packed-weight format',
  'routing.expert_demand_predictor':'Experimental · prefetch',
  'dense.dense_feed_forward_block':'Checkpoint-dependent',
  'memory.prefix_state_cache':'Optional · prefix reuse',
  'graph.execution_graph_backend':'Capture/replay when compatible',
  'backend.cpu_weight_repack':'Conditional · CPU expert lane',
  'weights.engram_row_cache':'Conditional · Engram checkpoints',
  'engine.host_expert_store':'Conditional · host expert tier'
};
const assemblyOwners = new Map();
for (const [key, record] of Object.entries(assemblyRecords)) {
  for (const id of record.children.filter(x=>!x.startsWith('@'))) {
    if (!components.has(id) || assemblyOwners.has(id)) throw Error('Invalid assembly child '+id);
    assemblyOwners.set(id,key);
  }
}
function assemblyHome(id) {
  const key=assemblyOwners.get(id);
  if (key) return {id:key,title:assemblyRecords[key].title,href:'#assembly/'+key};
  if (components.get(id)?.scope==='Factory') return {id:'factory',title:'Software factory',href:'#factory'};
}
function assemblyCard(id) {
  const record=assemblyRecords[id];
  return '<a class="assembly-node" data-assembly="'+e(id)+'" href="#assembly/'+e(id)+'"><strong>'+e(record.title)+'</strong><span>'+e(record.brief)+'</span></a>';
}
function engineViewSwitch(mode) {
  return '<nav class="asm-switch" aria-label="Engine view">'+[['components','Components','#engine'],['actions','Actions','#engine/actions']].map(([id,text,url])=>
    '<a href="'+url+'"'+(id===mode?' aria-current="page"':'')+'>'+text+'</a>').join('')+'</nav>';
}
const assemblyOpenState=new Set();
function overviewDisclosure(key,label,body) {
  return '<details class="expand-assembly" data-expand="'+e(key)+'"'+(assemblyOpenState.has(key)?' open':'')+'><summary>'+e(label)+'</summary>'+body+'</details>';
}
function assemblyMembers(id) {
  return assemblyRecords[id].children.map(child=>{
    if (child.startsWith('@')) {
      const nested=child.slice(1), record=assemblyRecords[nested];
      return overviewDisclosure(nested,record.title,'<p>'+pill('Open '+record.title,'#assembly/'+nested)+'</p>'+assemblyMembers(nested));
    }
    const c=components.get(child), owner=builders(child), acts=served(child);
    return '<div class="asm-member" data-member="'+e(child)+'"><strong>'+cmpLink(c)+'</strong>'+
      '<div><small>Builder</small> '+owner.map(ccLink).join(' ')+'</div>'+owner.map(cc=>fact('Code delivered',cc.summary)).join('')+
      (operators(child).length?'<div><small>Tools and analyses</small> '+operators(child).map(ccLink).join(' ')+'</div>':'')+measuredChip(child)+
      overviewDisclosure(child,'Performs '+acts.length+' '+(acts.length===1?'action':'actions'),'<div class="pills">'+acts.map(actLink).join(' ')+'</div>')+'</div>';
  }).join('');
}
function expandedAssemblyCard(id) {
  const preview=assemblyRecords[id].children.slice(0,3).map(key=>key.startsWith('@')?assemblyRecords[key.slice(1)].title:components.get(key).name);
  const count=assemblyRecords[id].children.length;
  return '<article class="asm-card">'+assemblyCard(id)+'<p class="asm-preview">'+preview.map(e).join(' · ')+(count>3?' · …':'')+'</p>'+
    overviewDisclosure(id,'Explore components',assemblyMembers(id))+'</article>';
}
function assemblyOverview() {
  const step = payload => '<div class="asm-handoff"><span>'+e(payload)+'</span><b aria-hidden="true">→</b></div>';
  const reader=components.get('weights.checkpoint_reader'),builder=builders(reader.id)[0],read=actions.get(reader.primary);
  const sample='<div class="role-example" aria-label="Worker, component and action example">'+[['Worker',builder.name,'cc/'+builder.id],['Component',reader.name,'component/'+reader.id],['Action',read.title,'action/'+read.id]].map(([role,title,url])=>'<a class="pill" href="#'+e(url)+'"><small>'+e(role)+'</small><strong>'+e(title)+'</strong></a>').join('<span aria-hidden="true">→</span>')+'</div>';
  root.innerHTML='<div class="asm">'+engineViewSwitch('components')+'<h1>Text inference engine</h1><p class="lead">Muse Spark Open on one DGX Spark. Each builder supplies code for a named component. The engine contract sets its required behavior, supported variants and acceptance checks.</p>'+
    '<div class="tools asm-level"><span>Diagram detail</span><button type="button" class="basic" data-level="overview">Overview</button><button type="button" class="basic" data-level="components">Show components and CCs</button><button type="button" class="basic" data-level="actions">Show components and actions</button></div>'+
    '<section class="asm-frame" aria-label="Engine architecture"><div class="asm-title">Engine architecture</div><div class="asm-path" aria-label="Token execution path">'+
    expandedAssemblyCard('request')+step('Token IDs')+expandedAssemblyCard('generation')+step('Scheduled rows')+expandedAssemblyCard('decoder')+'</div>'+
    '<div class="asm-return"><b aria-hidden="true">↶</b><span>Vocabulary scores return to the controller for sampling. A continuing sequence takes another step.</span></div>'+
    '<div class="asm-title asm-support-title">Supporting assemblies</div><div class="asm-grid asm-support">'+assemblyOrder.slice(3).map(expandedAssemblyCard).join('')+'</div>'+
    '<a class="asm-band" data-boundary="observability" href="#assembly/observability"><strong>Runtime observability</strong><span>Cross-cutting request, layer and device events</span></a></section>'+
    '<a class="asm-band asm-host" data-boundary="host" href="#assembly/host"><strong>Host platform</strong><span>CPU · Accelerator · Unified memory · Checkpoint storage</span></a>'+
    sample+'<div class="tools" aria-label="Explore execution and dependencies">'+pill('Follow one token','#trace/token/0')+' '+pill('Follow a cold expert fetch','#trace/cold/0')+' '+pill('Inspect connections','#connections')+' '+pill('Engine implementation and acceptance','#readiness')+'</div></div>';
  function markLevel(){
    const ds=[...root.querySelectorAll('[data-expand]')];
    const level=ds.every(d=>!d.open)?'overview':ds.every(d=>d.open)?'actions':ds.every(d=>d.open===Object.hasOwn(assemblyRecords,d.dataset.expand))?'components':'';
    root.querySelectorAll('[data-level]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.level===level)));
  }
  markLevel();
  root.querySelectorAll('[data-level]').forEach(button=>button.onclick=()=>{
    for(const detail of root.querySelectorAll('[data-expand]')){
      const key=detail.dataset.expand;
      detail.open=button.dataset.level==='actions'||button.dataset.level==='components'&&Object.hasOwn(assemblyRecords,key);
      if(detail.open)assemblyOpenState.add(key);else assemblyOpenState.delete(key);
    }
  });
  root.querySelectorAll('[data-expand]').forEach(detail=>detail.addEventListener('toggle',()=>{
    if(detail.open)assemblyOpenState.add(detail.dataset.expand);else assemblyOpenState.delete(detail.dataset.expand);
    markLevel();
  }));
}
let engineActionQuery='';
function engineActionOverview() {
  const layerRows=atlas.engine.map(layer=>({layer,records:layer.ops.map(op=>actions.get(layer.id+'/'+op.id))}));
  const count=layerRows.reduce((n,item)=>n+item.records.length,0);
  function row(a) {
    const performers=participants(a.id);
    return '<li data-action-id="'+e(a.id)+'"><div>'+actLink(a)+(a.target?'':' <small>Conditional</small>')+'</div><div><small>Performed by </small>'+performers.map(c=>cmpLink(c)+(c.scope==='Extension'?' <small>(conditional)</small>':'')).join(' · ')+'</div></li>';
  }
  root.innerHTML='<div class="asm">'+engineViewSwitch('actions')+'<h1>Engine actions</h1><p class="lead">Select an action to inspect its checks and handoffs, or follow a component to its build CC.</p>'+
    '<label class="asm-search">Find an action or component <input type="search" id="action-search" placeholder="Name, component or layer" value="'+e(engineActionQuery)+'"></label> <span id="action-count" aria-live="polite"></span>'+
    '<div class="asm-action-list">'+layerRows.map(({layer,records})=>'<section class="asm-action-group" data-layer="'+e(layer.id)+'"><h2>'+e(layer.title)+'</h2>'+
    (layer.id==='host'?'<p>Platform providers execute hardware operations. Engine components discover capabilities and expose telemetry.</p>':'')+
    '<ul>'+records.map(row).join('')+'</ul></section>').join('')+'</div></div>';
  const rows=[...root.querySelectorAll('[data-action-id]')].map(el=>{
    const a=actions.get(el.dataset.actionId),people=participants(a.id);
    return {el,haystack:[a.id,a.title,a.layer,...people.flatMap(c=>[c.name,c.id])].join(' ').toLowerCase()};
  });
  function filter() {
    const q=engineActionQuery.trim().toLowerCase(),tokens=q.split(/\s+/);
    let visible=0;
    for (const {el,haystack} of rows) {
      el.hidden=!tokens.every(token=>haystack.includes(token));
      if (!el.hidden) visible++;
    }
    root.querySelectorAll('[data-layer]').forEach(section=>section.hidden=!section.querySelector('li:not([hidden])'));
    root.querySelector('#action-count').textContent=visible+' of '+count+' actions';
  }
  root.querySelector('#action-search').addEventListener('input',event=>{engineActionQuery=event.target.value;filter();});
  filter();
}
function assemblyCrumb(id) {
  const crumbs=[pill('Engine assemblies','#engine')];
  const parts=id.split('/');
  for (let n=1;n<parts.length;n++) {
    const parent=parts.slice(0,n).join('/');
    crumbs.push(pill(assemblyRecords[parent].title,'#assembly/'+parent));
  }
  crumbs.push('<span aria-current="page">'+e(assemblyRecords[id].title)+'</span>');
  return '<div class="crumb" aria-label="Assembly hierarchy">'+crumbs.join(' › ')+'</div>';
}
function assemblyChild(id) {
  if (id.startsWith('@')) return assemblyCard(id.slice(1));
  const c=components.get(id);
  const mode=assemblyModes[id] || (c.scope==='Extension' ? 'Conditional extension' : '');
  return '<a class="assembly-node" data-child="'+e(id)+'" href="#component/'+e(id)+'"><strong>'+e(c.name)+'</strong><span>'+e(c.summary)+'</span>'+
    (mode?'<small>'+e(mode)+'</small>':'')+'</a>';
}
function assemblyPage(id) {
  if (!Object.hasOwn(assemblyRecords,id)) return false;
  const record=assemblyRecords[id];
  const depRows=record.depends.map(([target,role])=>{
    const c=components.get(target), home=assemblyHome(target);
    return '<div data-dependency="'+e(target)+'">'+pill(c.name,'#component/'+target)+'<p>'+e(role)+'</p><small>Home · '+pill(home.title,home.href)+'</small></div>';
  });
  root.innerHTML='<div class="asm">'+assemblyCrumb(id)+'<h1>'+e(record.title)+'</h1><p class="lead">'+e(record.role)+'</p>'+
    '<section class="asm-frame"><h2>'+(id==='host'?'Provided resources':'Inside this assembly')+'</h2><div class="asm-grid">'+record.children.map(assemblyChild).join('')+'</div></section>'+
    (depRows.length?'<section class="asm-deps"><h2>External dependencies and interfaces</h2><div>'+depRows.join('')+'</div></section>':'')+
    '<div class="tools">'+pill('Inspect connections','#connections')+'</div></div>';
  return true;
}
