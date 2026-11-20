function boundaryGuide() {
  return '<section class="ep-definition"><h2>What earns a component boundary?</h2>'+
    '<p>A component is source code with an identifiable caller, a behavior the caller can rely on, and a check that can demonstrate it. A larger component can own several such contracts.</p>'+
    '<dl><dt>Hash map</dt><dd>The implementation owns hashing, lookup and collision handling. A particular table in RAM is state. An internal map usually needs only a note inside its owner.</dd>'+
    '<dt>Cache</dt><dd>The cached bytes are data. The expert cache implementation controls filling, readiness and safe reuse, so an engineer can change and test it independently.</dd>'+
    '<dt>Operator</dt><dd>A matrix multiply can appear as one action. A grouped expert operator with a packed-row interface and independently replaceable kernels earns a subcomponent when its numerical behavior can be checked separately.</dd></dl></section>'+
    '<section class="ep-definition"><h2>How to read the evidence</h2><p><b>Mapped</b> identifies a change site and owner at the pinned revision. <b>Integrated</b> requires an agent receipt, reviewed diff and exact build. <b>Qualified</b> requires an independent endpoint run on that build. The demo specifies the latter two steps.</p></section>';
}

// The node positions and wire endpoints share the same 1100 × 410 coordinate space.
function endpointRelationshipMap(d) {
  const nodes = [
    ['service', 18, 46, 'Accept a prompt. Stream tokens and finish status.'],
    ['runtime', 301, 46, 'Schedule requests and advance prefill or decode.'],
    ['model', 584, 46, 'Evaluate the decoder and return logits.'],
    ['backend', 867, 46, 'Run graph operations on the selected hardware.'],
    ['tokens', 301, 241, 'Encode the prompt and sample permitted next tokens.'],
    ['sequence-state', 18, 241, 'Manage request-scoped KV and sequence state.'],
    ['weight-residency', 584, 241, 'Manage shared expert slots and ready handles.'],
    ['preparation', 867, 241, 'Convert, quantize and validate model weights.']
  ];
  const byId = new Map(d.parents.map(p => [p.id,p]));
  const edges = [
    ['M 230 81 H 296',263,70,'request','Completion service → Generation runtime','validated request'],
    ['M 513 81 H 579',546,70,'batch','Generation runtime → Model execution','token IDs, positions and sequences'],
    ['M 796 81 H 862',829,70,'graph','Model execution → Tensor execution backend','operations and tensor layouts'],
    ['M 339 134 V 164 H 126 V 139',225,158,'tokens to stream','Generation runtime → Completion service','generated tokens and finish status'],
    ['M 431 137 V 236',440,196,'IDs / logits','Generation runtime ↔ Token processing and sampling','prompt IDs, logits and an accepted token',true],
    ['M 620 137 V 205 H 124 V 236',234,199,'KV reads / writes','Model execution ↔ Sequence state','Request-scoped KV reads and updates',true],
    ['M 730 137 V 236',740,190,'expert handles','Model execution ↔ Weight residency','Selected expert demand and ready handles from shared slots',true],
    ['M 867 288 H 801',831,278,'pack','Model preparation and loading → Weight residency','Validated weight ranges and layout'],
    ['M 973 241 V 173 H 752 V 139',867,167,'model binding','Model preparation and loading → Model execution','architecture and tensor bindings']
  ];
  const wires = edges.map(([path,x,y,label,,,double]) => {
    const textAnchor = double ? 'start' : 'middle';
    return '<path d="'+path+'" marker-end="url(#ep-wire-end)"'+(double?' marker-start="url(#ep-wire-start)"':'')+'/>'+
      '<text x="'+x+'" y="'+y+'" text-anchor="'+textAnchor+'">'+label+'</text>';
  }).join('');
  const cards = nodes.map(([id,x,y,summary]) => '<a class="ep-parent ep-map-node" href="#endpoint/parent/'+id+
    '" style="--map-x:'+x/11+'%;--map-y:'+y/4.1+'%"><strong>'+byId.get(id).title+
    '</strong><small>'+summary+'</small></a>').join('');
  const relationships = edges.map(([,,,label,endpoints,payload]) => '<li><b>'+endpoints+'</b><span>'+payload+'</span></li>').join('')+'<li class="ep-budget-relation"><b>Shared memory budget · constraint</b><span>Sequence state and weight residency compete for the same bounded memory. The planner budgets both; this is not a data handoff.</span></li>';
  return '<div class="ep-heading"><span class="ep-eyebrow">Engine architecture</span><h1>The completions endpoint</h1><p>Follow a prompt into the decoder and a token back to the client. Open any component for its source, builders and acceptance checks.</p></div>'+
    '<section class="ep-wired" aria-label="Software components and their relationships"><div class="ep-map-canvas">'+
    '<svg viewBox="0 0 1100 410" preserveAspectRatio="none" aria-hidden="true"><defs>'+
    '<marker id="ep-wire-end" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><polygon points="0,0 8,4 0,8"/></marker>'+
    '<marker id="ep-wire-start" viewBox="0 0 8 8" refX="1" refY="4" markerWidth="6" markerHeight="6" orient="auto"><polygon points="8,0 0,4 8,8"/></marker></defs>'+wires+'<path class="ep-budget-wire" d="M 124 329 V 375 H 690 V 329"/><text x="407" y="393" text-anchor="middle" class="ep-budget-label">shared memory budget · constraint, not a data handoff</text></svg>'+cards+'</div>'+
    '<details class="ep-edge-list"><summary>Read the relationships and budget constraint</summary><ul>'+relationships+'</ul></details></section>'+
    '<div class="ep-ownership"><section><h2>Who changes the software?</h2><p>The <a href="#cc/compiler.engine_contract">Contract compiler</a> supplies a revision to the <a href="#cc/factory.workflow_planning">Workflow orchestrator</a>. It dispatches builders to change the components. Integration, build and independent qualification follow.</p></section>'+
    '<section><h2>Where does the data live?</h2><p>Host <a href="#component/host.dram">memory</a> and <a href="#component/host.ssd">storage</a> hold bytes. Sequence state is scoped to requests; expert slots can be shared across requests. The planner accounts for both within one memory budget.</p></section></div>'+
    '<div class="ep-links"><a href="#endpoint/coverage">Scope and source audit</a><a href="#construction">20 work orders</a><a href="#engine/actions">Engine actions</a><a href="#readiness">Target qualification</a><a href="#assemblies">Original assembly map</a></div>';
}
