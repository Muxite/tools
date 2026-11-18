/* Selected branch revisions for the presentation. */
const factoryPins={
 m1:'32c77d69d7b64705194dc56d5aac39d02be4924e',
 plus:'98c6d01bf0d9680ef6175842ac7dc66bc9894ec2',
 workflow:'73da54106ba56bd856c1074b05ff17eb8de4d2fb',
 spark:'aa74fab77312e4349c885d53ebc01a228c4c62e5',
 loop:'736544de57c7a5ddeacee86558088756a2786249',
 native:'a2310f0fb8a24ef04f42542aa21ff15ff4c0e917'
};
const factoryConnections=[
 {id:'intent', title:'Capture intent', owner:'M1 and M1plus', color:'factory',cc:['compiler.intent_brief'],
 existing:'M1’s intent capsule reads a qualified intake record, resolves original text and source references, and emits intent_ir.json on its intent port. M1plus adds a pinned m1-8 release with its own carrier, checking bundle and profile.',
 join:'Expose that transformation through a sealed native Intent Compiler capability. Supply referenced input bytes through the native host, preserve their identities and record review status. Resolve a missing constraint before releasing the brief.',
 receipt:'Reviewed intent brief with request reference, source identities, approved goals and open questions. The Contract Compiler consumes this revision.',
 refs:[['m1','Baseline intent capsule','jiuwenswarm/research/capsules/intent.py#L8'],['plus','Modified intent release','jiuwenswarm/research/intent_release.py#L36'],['plus','Intent output port','jiuwenswarm/research/capsules/intent_m1_8.py#L8']]},
 {id:'contract', title:'Bind the contract',owner:'Engine factory',color:'factory',cc:['compiler.engine_contract'],
 existing:'The contract-loop branch loads, freezes and evaluates factory contracts. The native implementation checks supported adapter types and verifies that a requested contract agrees with the admitted task.',
 join:'Implement the reviewed brief plus ontology → engine contract translation. Bind checkpoint and tokenizer digests, one-device memory limits, permitted source changes and acceptance gates. Select an existing validator only if it covers those fields; extend admission for the missing obligations.',
 receipt:'A versioned engine contract and immutable reference fixture. The planner and independent lab must resolve the same contract from the task.',
 refs:[['loop','Contract-loop freeze and evaluation','jiuwenswarm/factory/contract.py#L59'],['native','Task-bound contract lookup','jiuwenswarm/factory/contract.py#L55']]},
 {id:'plan',title:'Compose work orders',owner:'Dynamic workflow',color:'factory',cc:['factory.workflow_planning'],
 existing:'M1plus emits a plan_proposal or records infeasibility against the frozen capability set. The dynamical-workflow branch defines named ports, bindings, stage references and reusable subworkflows. The integrated native registry composes CC capabilities into a dependency graph.',
 join:'Map each atlas job to one or more available sealed releases and capability names, then validate input and result port schemas. Store agent assignment separately from CC identity so multiple agents can share a CC. Surface a missing release as an unfilled work order.',
 receipt:'A revisioned graph with explicit artifact dependencies. Independent leaves become ready once their input receipts exist. Source edits that touch the same interface need an integration owner.',
 refs:[['plus','Planner proposal and infeasibility','jiuwenswarm/research/capsules/planner.py'],['workflow','Composition and expansion','jiuwenswarm/software_factory/workflow_definitions.py#L114'],['native','Native port contract','docs/architecture/factory/INTERCONNECT.md']]},
 {id:'build',title:'Edit and build',owner:'Native CC host',color:'engine',cc:['factory.source_integration','model.expert_routing','factory.builder'],
 existing:'The native workflow persists invocation intent before Host.call. Source workbench and builder are existing CC entry points. Lab Manager owns task-scoped job admission, attempts and resource budgets.',
 join:'For the first slice, give a worker the routing CC and a tiny known-answer fixture. Have it implement a specified selector in an admitted source tree and return a diff and test evidence. Bind the resulting source identity to the builder. Replace fixture-only work with a real engine work order after the handoff passes.',
 receipt:'Reviewed source diff, source identity, builder attempt and collected result. The lab needs the completed build identity and associated image lineage.',
 refs:[['native','Source workbench','jiuwenswarm/factory/ccs/source_workbench/run.py'],['native','Builder entry point','jiuwenswarm/factory/ccs/builder/run.py'],['native','Native workflow tick','jiuwenswarm/software_factory/cc_workflow.py#L314']]},
 {id:'lab',title:'Evaluate and revise',owner:'Lab and planner',color:'lab',cc:['factory.controlled_experiment','factory.workflow_planning'],
 existing:'The benchmark CC consumes an admitted build. The workflow retains submit acknowledgement and collected result separately. A graph append takes an expected revision and a decision. A recorded Spark campaign demonstrates a bounded iteration on Strata.',
 join:'Translate the engine contract into lab fixtures and independent gates. Route failure evidence to the worker that owns the first divergent output. Append a bounded repair or stop when the contract passes or its budget is exhausted.',
 receipt:'Task, graph revision, attempt, image and pack identities, metrics and scoped verdict. An unresolved attempt blocks dependent work. Only the lab verdict can qualify the candidate.',
 refs:[['native','Benchmark entry point','jiuwenswarm/factory/ccs/standard_benchmark/run.py'],['native','Revision-checked append','jiuwenswarm/software_factory/cc_workflow.py#L192'],['native','Recorded campaign result','docs/architecture/factory/qualifications/20261116-round2-summary.json']]}
];
function factoryCodeLink(key,title,path){
 return ext(title,'https://github.com/Stellven/jiuwenswarm/blob/'+factoryPins[key]+'/'+path);
}
function integrationView(id){
 const step=factoryConnections.find(s=>s.id===id)||factoryConnections[0];
 const position=factoryConnections.indexOf(step);
 const links=step.refs.map(args=>factoryCodeLink(...args)).join(' · ');
 const select=s=>address('integration',s.id);
 root.innerHTML='<h1>Factory integration</h1><p class="lead">M1 supplies a starting point for intent and planning. Dynamic workflow orders the jobs. The native CC host executes sealed capabilities, and the lab owns resource admission and independent evaluation.</p>'+
 '<nav class="integration-flow" aria-label="Factory integration steps">'+factoryConnections.map((s,i)=>'<a class="lane-'+s.color+'" href="'+select(s)+'" '+(s===step?'aria-current="step"':'')+'><small>'+esc(s.owner)+'</small><b>'+esc(s.title)+'</b></a>'+(i<factoryConnections.length-1?'<span aria-hidden="true">→</span>':'')).join('')+'</nav>'+
 '<section id="integration-detail" class="sheet"><h2>'+esc(step.title)+'</h2><div class="pills">'+step.cc.map(k=>pill(k,'#cc/'+k)).join(' ')+'</div>'+
 sec('In the branches',list(step.existing))+sec('Work to connect it',list(step.join))+sec('Handoff',list(step.receipt))+'<p>'+links+'</p><div class="pills">'+(position?pill('← '+factoryConnections[position-1].title,select(factoryConnections[position-1])):'')+(position+1<factoryConnections.length?pill(factoryConnections[position+1].title+' →',select(factoryConnections[position+1])):'')+'</div></section>'+
 '<section class="sheet"><h2>One real binding</h2><p>A benchmark screen can consume the builder’s completed attempt through <code>factory.interconnect/1</code>. The destination input is <code>request</code>. Its source is the <code>build</code> node’s <code>attempt_id</code> port on the <code>result</code> channel. The binding inserts the value at <code>/build_attempt_id</code> in a request with <code>stage = screen</code>. An acknowledgement alone leaves the benchmark waiting.</p><p>Version 1 selects one source per binding. When a step needs to combine several receipts into one structured input, give that assembly to an explicit component with a validated output.</p>'+factoryCodeLink('native','Interconnect binding example','docs/architecture/factory/INTERCONNECT.md#L25')+'</section>'+
 '<section class="sheet"><h2>First end-to-end check</h2><p>Start with one pinned source tree, a tiny routing fixture, one admitted task and a bounded budget. Prove intent → contract → work order → source diff → image → independent verdict. Restart after build submission and check that recovery reconciles the same attempt. Inject an incorrect expert weight and verify that the lab rejects the image. Use the resulting receipt to issue one repair.</p><p>This slice qualifies the integration. Full Muse construction adds the remaining engine CC implementations, storage-backed execution and target quality and performance trials.</p>'+pill('Full construction walkthrough','#construction')+'</section>'+
 '<details class="sheet"><summary>Branch lineage and scope</summary><p>Inspected Stellven/jiuwenswarm branches: ai4r_M1, ai4r_M1plus, ai4r/contract-loop, cc-dgx-spark, dynamical-workflow and integration/native-cc-workflows. All five source revisions are ancestors of the inspected integration revision. The native guide records removal of the M1 services. M1 artifacts and checks guide the port; that ancestry alone does not provide a live M1 service or a greenfield Muse build.</p>'+
 factoryCodeLink('spark','Spark builder ancestor','jiuwenswarm/factory/ccs/builder/run.py')+' · '+factoryCodeLink('native','Native integration scope','docs/architecture/factory/NATIVE-WORKFLOWS.md')+'</details>';
}
