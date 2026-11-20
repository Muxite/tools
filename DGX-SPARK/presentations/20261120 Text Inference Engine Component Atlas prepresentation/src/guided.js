// Every step follows a named component handoff. A step may follow another
// producer into the same consumer when its inputs arrive independently.
const guidedWalks = (() => {
  const gateway = 'serving.engine_image_gateway', codec = 'tokenizer.token_codec';
  const scheduler = 'scheduler.request_scheduler', batch = 'batch.batch_layout_builder';
  const generation = 'decode.generation_loop', embedding = 'model.token_embedding_layer';
  const decoder = 'model.decoder_stack', attention = 'attention.dense_attention_operator';
  const router = 'model.expert_router', rows = 'merge.expert_row_dispatcher_and_combiner';
  const expert = 'model.expert_feed_forward_block', head = 'model.vocabulary_projection_head';
  const sampler = 'sampling.token_sampler', reader = 'weights.checkpoint_reader';
  const placement = 'placement.weight_placement_planner', cache = 'engine.expert_weight_cache';
  return {
    token: {
      title: 'A request to its first output token',
      intro: 'Follow an illustrative three-token prompt through one routed decoder block and back to the response stream. The IDs and scalar expert outputs are example values.',
      steps: [
        [gateway,codec,'interface/format','Format the request','The client supplies a prompt and completion settings. The gateway passes the prompt to the model’s template and tokenizer.'],
        [codec,scheduler,'interface/submit','Queue the prompt','The encoded prompt contains IDs [12, 35, 9]. The scheduler receives these IDs with the request identity.'],
        [scheduler,batch,'schedule/batch','Assign three positions','The scheduler admits the request and assigns prompt positions 0, 1 and 2 to its sequence.'],
        [batch,generation,'generate/prefill','Start prefill','Batch rows carry the three token IDs, their logical positions and the state handle for this request.'],
        [generation,embedding,'model/embed','Look up the prompt','The model’s embedding table supplies one hidden row for each of IDs 12, 35 and 9.'],
        [embedding,decoder,'model/norm','Enter the decoder','The decoder receives three hidden rows in prompt order and applies the checkpoint’s layer sequence.'],
        [decoder,attention,'model/attend','Apply the causal mask','For the query at position 2, the attention operator can read keys and values for positions 0, 1 and 2.'],
        [attention,decoder,'model/attout','Return attended rows','Attention returns rows in query order. The decoder projects the rows and adds the residual before its feed-forward sublayer.'],
        [decoder,router,'model/route','Select experts','For one row, scores [0.50, 0.30, 0.20] and ranking biases [0, 0, 0.15] select E0 and E2. Their original scores normalize to weights 5/7 and 2/7.'],
        [router,rows,'model/dispatch','Record the assignments','The dispatcher receives (E0, 5/7) and (E2, 2/7) for the same token row. It keeps the inverse map back to that token.'],
        [rows,expert,'model/expert','Run the selected experts','Rows grouped for E0 and E2 can execute once their weights are ready. Follow the cold expert walk to inspect that separate input.'],
        [expert,rows,'model/combine','Restore token order','Suppose the same output coordinate is 4 from E0 and 11 from E2. The combiner restores their token row and computes (5 × 4 + 2 × 11) / 7 = 6.'],
        [rows,decoder,'model/layerout','Complete the block','The combined rows return in token order for residual addition. The decoder repeats its configured blocks before final normalization.'],
        [decoder,head,'model/head','Score the vocabulary','The head projects the final normalized hidden row for prompt position 2 into one score per vocabulary entry.'],
        [head,sampler,'generate/sample','Choose an output ID','The sampler receives the vocabulary scores and applies the request’s settings. Suppose the chosen ID is 47.'],
        [sampler,generation,'generate/commit','Commit the token','The generation loop commits ID 47 and its continuation decision. For a continuing request, the scheduler can admit the next decode step.'],
        [generation,codec,'interface/detok','Decode the committed ID','The codec receives ID 47 with its decoder state and emits any complete UTF-8 text available at this boundary.'],
        [codec,gateway,'interface/emit','Stream the response','The gateway emits the decoded text in the completion stream. Later decode steps repeat until a stop condition or cancellation.']
      ]
    },
    cold: {
      title: 'A cold expert fetch',
      intro: 'Follow one routed token whose E0 weights are resident and whose E2 weights are on storage. The row and its weights arrive through separate inputs to expert execution.',
      steps: [
        [reader,placement,'startup/place','Locate the weight range','At startup the reader identifies the shard, byte range, shape and format for E2. The planner receives the validated inventory.'],
        [placement,cache,'state/residency','Budget the slots','The placement plan keeps E0 resident and assigns E2 to storage. It bounds the space available for streamed weights after accounting for live state and working buffers.'],
        [router,cache,'model/ready','Demand the missing expert','The router selects E0 and E2 for this token. On the authoritative E2 request, the cache finds a miss, reserves a slot and requests the validated range.'],
        ['host.ssd',cache,'state/fill','Fill the reserved slot','Storage supplies the bytes for E2. A second request for the same in-flight range can wait for the existing fill. The slot becomes readable only after completion.'],
        [rows,expert,'model/dispatch','Deliver the token rows','On the compute path the dispatcher has grouped the token rows by expert and retained their inverse mapping. E2’s rows also need the ready weight handle.'],
        [cache,expert,'model/expert','Pass the ready weight handle','The cache supplies E2’s ready handle and holds its slot through the expert calculation. A last-use completion signal permits reuse.'],
        [expert,rows,'model/combine','Return the expert outputs','Each expert returns rows in grouped order. The combiner uses the original token mapping and the router’s mixture weights.'],
        [rows,decoder,'model/layerout','Rejoin the decoder','The weighted rows return to the decoder in token order. Compare a forced cold miss with resident execution to check that streaming preserves the result.']
      ]
    }
  };
})();

function guidedView(traceId, index) {
  const walk = Object.hasOwn(guidedWalks,traceId) && guidedWalks[traceId];
  const step = index === undefined || index === '' ? 0 : Number(index);
  if (!walk || !Number.isInteger(step) || step < 0 || step >= walk.steps.length) return false;
  const [from,to,actionId,title,explanation] = walk.steps[step];
  const current = components.get(from), next = components.get(to);
  const edge = engineHandoffs.find(([s,t]) => s === from && t === to);
  const route = i => '#trace/' + traceId + '/' + i;
  const stepNav = '<nav class="tools" aria-label="Walkthrough steps">' +
    (step ? '<a class="pill" rel="prev" href="'+route(step-1)+'">Previous step</a>' : '') +
    (step+1 < walk.steps.length ? '<a class="pill" rel="next" href="'+route(step+1)+'">Next step</a>' : pill('Return to engine map','#engine')) +
    '</nav>';
  const outline = walk.steps.map((s,i)=>'<li><a '+(i===step?'aria-current="step" ':'')+'href="'+route(i)+'">'+e(s[3])+'</a></li>').join('');
  const repeat = traceId==='token' && (step===15 || step===17)
    ? '<p>'+pill('Inspect next-step eligibility',handoffPath('decode.generation_loop','scheduler.request_scheduler'))+'</p>' : '';
  const related = traceId==='token' && step===10 ? '<p>'+pill('Follow a cold expert fetch','#trace/cold/0')+'</p>' : '';
  root.innerHTML='<section data-trace="'+traceId+'" data-step="'+step+'"><div class="tagline">Engine walkthrough</div><h1>'+e(walk.title)+'</h1><p class="lead">'+e(walk.intro)+'</p>'+
    '<div class="cols"><section class="graphwrap"><div id="graph"></div></section><aside id="inspector" class="sheet"><div class="tagline">Step '+(step+1)+' of '+walk.steps.length+'</div><h2>'+e(title)+'</h2><p>'+e(explanation)+'</p>'+
    fact('Payload',edge[2])+'<div class="pills">'+pill('Inspect handoff',handoffPath(from,to))+' '+actLink(actions.get(actionId))+'</div>'+repeat+related+stepNav+
    details('All steps','<ol>'+outline+'</ol>')+'<div class="pills">'+pill('Engine map','#engine')+'</div></aside></div></section>';
  drawAtlas(root.querySelector('#graph'),{mode:'engine',layers:atlas.engine,names:new Map([[from,current.name],[to,next.name]]),
    onEdge:()=>{location.hash=handoffPath(from,to);},
    path:({node,wire,region,finish})=>{
      region(10,10,980,232,'STEP '+(step+1)+' OF '+walk.steps.length+' · '+title);
      wire(from,to,'hands off','M382 132 H620',500,132,'call',160);
      node({id:from,title:current.name,x:42,y:90,w:340,h:84,code:'CURRENT · PRODUCER',tone:'focus',selected:true,onClick:()=>{location.hash='#component/'+from;}});
      node({id:to,title:next.name,x:620,y:90,w:340,h:84,code:'NEXT · CONSUMER',tone:'layer',onClick:()=>{location.hash='#component/'+to;}});
      finish(255);
    }});
  tabActive('engine');
  return true;
}

function connectionInventory() {
  const categories = {flow:'Main flow',branch:'Branch',rejoin:'Rejoin',loop:'Repeat',support:'Shared service',platform:'Host platform'};
  const sections = engineStages.map(stage=>{
    const home = new Set([...stage.main,...stage.side]);
    const rows = engineHandoffs.filter(([s])=>home.has(s)).map(([s,t,payload,kind])=>{
      return '<article class="insight" data-handoff-row><div class="tagline">'+e(categories[kind]||kind)+'</div><h3>'+cmpLink(components.get(s))+' → '+cmpLink(components.get(t))+'</h3><p>'+e(payload)+'</p>'+pill('Inspect handoff',handoffPath(s,t))+'</article>';
    });
    return rows.length ? '<section class="sheet"><h2>'+e(stage.title)+'</h2>'+rows.join('')+'</section>' : '';
  });
  root.innerHTML='<div data-engine-handoffs><h1>Engine connections</h1><p class="lead">'+engineHandoffs.length+
    ' directed handoffs, grouped by the stage of the component supplying the payload.</p><div class="tools">'+pill('Engine map','#engine')+' '+pill('Follow a request','#trace/token/0')+' '+pill('Cold expert fetch','#trace/cold/0')+'</div>'+sections.join('')+'</div>';
  tabActive('engine');
  return true;
}
