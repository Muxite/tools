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
 {id:'intent', title:'Capture intent', owner:'Intent Compiler', color:'factory',cc:['compiler.intent_brief'],
 existing:'M1’s intent capsule reads a qualified intake record, resolves original text and source references, and emits intent_ir.json on its intent port. M1plus adds a pinned m1-8 release with its own carrier, checking bundle and profile.',
 join:'Let the intent agent choose how to clarify the request. It can inspect the checkpoint, ask the user about a goal, or reuse a reviewed decision. Preserve the request, evidence and resulting brief. The M1 capsule is one implementation reference; its prompt, checks and artifact format are optional.',
 receipt:'Reviewed intent brief with request reference, source identities, approved goals and open questions. The Contract Compiler consumes this revision.',
 refs:[['m1','Baseline intent capsule','jiuwenswarm/research/capsules/intent.py#L8'],['plus','Modified intent release','jiuwenswarm/research/intent_release.py#L36'],['plus','Intent output port','jiuwenswarm/research/capsules/intent_m1_8.py#L8']]},
 {id:'contract', title:'Bind the contract',owner:'Engine factory',color:'factory',cc:['compiler.engine_contract'],
 existing:'The contract-loop branch loads, freezes and evaluates factory contracts. The native implementation checks supported adapter types and verifies that a requested contract agrees with the admitted task.',
 join:'Implement the reviewed brief plus ontology → engine contract translation. Bind checkpoint and tokenizer digests, one-device memory limits, permitted source changes and acceptance gates. State the acceptance criteria and what would count as evidence. An agent can design a fixture, differential test or measurement suited to the work. Keep the criterion stable across attempts; revise the contract explicitly if the goal changes.',
 receipt:'A versioned engine contract and immutable reference fixture. The planner and independent lab must resolve the same contract from the task.',
 refs:[['loop','Contract-loop freeze and evaluation','jiuwenswarm/factory/contract.py#L59'],['native','Task-bound contract lookup','jiuwenswarm/factory/contract.py#L55']]},
 {id:'plan',title:'Compose work orders',owner:'Dynamic workflow',color:'factory',cc:['factory.workflow_planning'],
 existing:'M1plus emits a plan_proposal or records infeasibility against the frozen capability set. The dynamical-workflow branch defines named ports, bindings, stage references and reusable subworkflows. The integrated native registry composes CC capabilities into a dependency graph.',
 join:'Inspect available artifacts and unresolved obligations. Choose the next useful investigation, give its agent the relevant CCs, and bind the inputs it needs. Reuse a subworkflow when its local ordering fits. When evidence changes, the workflow can launch another investigation, run independent jobs together or stop.',
 receipt:'A decision record names the evidence considered, chosen job, assigned CCs, input artifact revisions and budget. The native graph can record and execute that decision incrementally.',
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
function evidenceChoices(){
 const cases=[
   ['Selected IDs agree, weights differ','Give the diagnosis agent the routing CC. Let it construct a tie or bias fixture that distinguishes a ranking error from a normalization error. Reuse the current image and capture intermediate scores before assigning a source edit.','model.expert_routing','A minimal counterexample, the first divergent value and the source revision.'],
   ['Outputs agree, cold decode stalls','Give the storage agent the streaming and runtime-events CCs. Trace exact demand to first use. A second agent can replay the same route trace against a different cache budget while the first measures physical reads.','engine.expert_streaming observability.runtime_events','A correlated trace plus a recommendation to change storage policy, gather more data or close the investigation.'],
   ['Existing evidence meets the obligation','Let the experiment agent check the prior receipt against the current image, pack, workload and acceptance criteria. Reuse a matching result. If only the pack changed, qualify the affected obligation again.','factory.controlled_experiment','A scoped acceptance or a new work order identifying the missing evidence.']
 ];
 return '<section class="sheet"><h2>One contract, different next jobs</h2><p>Suppose the goal is accurate routed output within a cold-decode latency budget. Select an observation to see one possible agent decision. Each example starts from a different artifact.</p>'+cases.map(([title,decision,cc,out])=>details(title,'<p>'+esc(decision)+'</p><div class="pills">'+cc.split(' ').map(k=>pill(k,'#cc/'+k)).join(' ')+'</div><p><b>Handoff</b> · '+esc(out)+'</p>')).join('')+'</section>';
}
// A single fictional fixture follows the handoff without implying a measured run.
const factoryExamples={
 intent:['What does an intent brief contain?','The requester asks for local text generation on one Spark with eight routed experts. Capture the model revision, device count and desired cold-decode latency. If latency has no agreed workload or threshold, keep that question open.','The next agent receives the reviewed brief, its source request and the unresolved latency question.'],
 contract:['What obligation can a worker test?','For a tiny selector fixture, use scores [0.50, 0.30, 0.20], ranking bias [0, 0, 0.15] and k = 2. Rank with bias, gather original scores and normalize. The expected pairs are (E0, 5/7) and (E2, 2/7). The small fixture exercises the rule used by the wider target selector.','Record expected IDs, weights and tolerance. Keep this arithmetic gate distinct from full-checkpoint quality and cold-decode timing.'],
 plan:['How does one observation change the assignment?','The trace selects E0 and E2, but returns weights 10/17 and 7/17. Those numbers match normalization of the biased ranking scores. Assign the routing CC to inspect the score gather. An expert-storage edit would leave this arithmetic unchanged.','A work order names the failing fixture, current source revision, first suspected divergence and acceptance check.'],
 build:['What does the builder hand back?','The source agent delivers a diff that gathers original scores after ranking. The builder accepts the revision and returns an attempt ID. Only a successful collected result supplies the build identity the benchmark can consume.','Retain the diff, source revision, image identity and collected attempt together. On restart, reconcile the recorded attempt before issuing another build.'],
 lab:['What would persuade the lab?','Run the original fixture on the candidate image and an independent case whose bias changes the winner. Verify IDs and normalized weights. If arithmetic passes but cold decode misses its latency gate, keep the numerical receipt and assign a storage investigation.','Return a scoped verdict tied to the image, pack, workload and criteria. An accepted selector is one completed obligation.']
};
function presentationCoverage(){
 const sections=[
  ['Model and routing',r=>r.target&&r.review.site.startsWith('model/')],
  ['Serving and generation',r=>r.target&&/^(interface|schedule|generate)\//.test(r.review.site)],
  ['Weights, memory and kernels',r=>r.target&&/^(startup|state|backend)\//.test(r.review.site)],
  ['Factory',r=>r.kind==='factory'],['Reference extensions',r=>!r.target]
 ];
 return '<section class="sheet" id="coverage"><h2>Design coverage</h2><p>Each of the '+atlas.roles.length+' CCs has a primary worksite, an engineering responsibility, capabilities and an evidence handoff. Open a group to inspect any assignment.</p><div class="coverage-list">'+sections.map(([title,include])=>{
  const rows=atlas.roles.filter(include);
  return details(title+' · '+rows.length+' CCs','<div class="pills">'+rows.map(r=>pill(r.id,'#cc/'+r.id)).join(' ')+'</div>');
 }).join('')+'</div><p>'+pill('All CCs','#library')+' '+pill('Check source evidence','#sources')+'</p></section>';
}
function presenterBrief(){
 return '<section class="sheet"><h2>Start with one routing decision</h2><p>The selector returns the right expert IDs but the wrong weights. The routing CC tells the agent which score tensor belongs at each interface. The workflow uses that finding to commission a focused edit. The lab can reject or accept the resulting image against the same fixture.</p><div class="pills">'+pill('Inspect the fixture','#integration/contract')+' '+pill('See the next assignment','#integration/plan')+' '+pill('Check the lab verdict','#integration/lab')+'</div></section>'+
 presentationCoverage()+'<section class="sheet"><h2>First coding assignment</h2><p>Give a routing worker the selector fixture and an admitted source tree. Deliver a failing test, a scoped fix and an image that passes an independent test. Give the integration worker the completed build receipt and have the lab consume it through the existing result binding.</p><p><b>Done when</b> the incorrect image fails, the corrected image passes, and restarting after submission reuses the same build attempt. The factory already has a native builder and benchmark entry point. Implementing and running this slice is the next milestone.</p><div class="pills">'+pill('Routing work order','#construction/routing')+' '+pill('Source and image handoff','#integration/build')+' '+pill('Lab CC','#cc/factory.controlled_experiment')+'</div></section>';
}
function integrationView(id){
 const step=factoryConnections.find(s=>s.id===id)||factoryConnections[0];

 const links=step.refs.map(args=>factoryCodeLink(...args)).join(' · ');
 const select=s=>address('integration',s.id);
 const talkNext={contract:['Follow this finding','plan'],plan:['Inspect the independent check','lab'],lab:['Return to coverage','']};
 const talkLink=talkNext[id];
 root.innerHTML='<h1>Factory integration</h1><p class="lead">The Intent Compiler captures the goal. The Contract Compiler binds it to the system ontology and acceptance criteria. From there, agents choose their next work using the CC catalog, current artifacts and remaining budget.</p>'+
 '<div class="cards"><article class="listing"><h2>CCs · structure</h2><p>A CC bundles capabilities with knowledge of the component, its dependencies, interfaces and evidence of correctness. The routing CC knows how scores, expert IDs and weights fit together. Several agents can draw on it.</p></article><article class="listing"><h2>Workflows · timing</h2><p>A subworkflow orders a local job, such as reproducing one incorrect router output. The enclosing workflow decides when to start it, what else can run, when to revisit a decision and when enough evidence exists to stop.</p></article><article class="listing"><h2>Artifacts · handoff</h2><p>A versioned routing fixture, diff, image or trace can serve several jobs. A consumer checks its identity and scope before reusing it. A new finding can change the next assignment while the artifact remains available.</p></article></div>'+
 (id?'':presenterBrief())+'<h2>Implementation references</h2><nav class="integration-flow" aria-label="Factory integration components">'+factoryConnections.map((s,i)=>'<a class="lane-'+s.color+'" href="'+select(s)+'" '+(s===step?'aria-current="step"':'')+'><small>'+esc(s.owner)+'</small><b>'+esc(s.title)+'</b></a>').join('')+'</nav>'+
 '<section id="integration-detail" class="sheet"><h2>'+esc(step.title)+'</h2><div class="pills">'+step.cc.map(k=>pill(k,'#cc/'+k)).join(' ')+'</div>'+
 '<section class="worked-example"><div class="tagline">Illustrative handoff</div><h3>'+esc(factoryExamples[step.id][0])+'</h3>'+list(factoryExamples[step.id].slice(1))+'</section>'+
 sec('In the branches',list(step.existing))+sec('Proposed factory design',list(step.join))+sec('Handoff',list(step.receipt))+'<p>'+links+'</p>'+(talkLink?pill(talkLink[0],address('integration',talkLink[1])):'')+'</section>'+
 evidenceChoices()+'<p>'+pill('Presentation overview','#integration')+'</p>'+
 '<section class="sheet"><h2>One real binding</h2><p>A benchmark screen can consume the builder’s completed attempt through <code>factory.interconnect/1</code>. The destination input is <code>request</code>. Its source is the <code>build</code> node’s <code>attempt_id</code> port on the <code>result</code> channel. The binding inserts the value at <code>/build_attempt_id</code> in a request with <code>stage = screen</code>. An acknowledgement alone leaves the benchmark waiting.</p><p>Version 1 selects one source per binding. When a step needs to combine several receipts into one structured input, give that assembly to an explicit component with a validated output.</p>'+factoryCodeLink('native','Interconnect binding example','docs/architecture/factory/INTERCONNECT.md#L25')+'</section>'+
 '<section class="sheet"><h2>First end-to-end check</h2><p>Start with one pinned source tree, a tiny routing fixture, one admitted task and a bounded budget. Give the workflow a numerical routing obligation and let it select checks and engineering work from the available evidence. Restart after build submission and check that recovery reconciles the same attempt. Inject an incorrect expert weight and verify that the lab rejects the image. Repeat with an already-qualified selector. Check that the agent can reuse the passing artifact and skip a redundant edit. Record why the two runs made different choices.</p><p>This slice qualifies the integration. Full Muse construction adds the remaining engine CC implementations, storage-backed execution and target quality and performance trials.</p>'+pill('Full construction walkthrough','#construction')+'</section>'+
 '<details class="sheet"><summary>Branch lineage and scope</summary><p>Inspected Stellven/jiuwenswarm branches: ai4r_M1, ai4r_M1plus, ai4r/contract-loop, cc-dgx-spark, dynamical-workflow and integration/native-cc-workflows. All five source revisions are ancestors of the inspected integration revision. The native guide records removal of the M1 services. M1 is a reference for recording intent, release identity and evidence. The factory can choose new agent behaviors, artifact schemas and checking methods. The native branch supplies a concrete execution option for decisions made during a run.</p>'+
 factoryCodeLink('spark','Spark builder ancestor','jiuwenswarm/factory/ccs/builder/run.py')+' · '+factoryCodeLink('native','Native integration scope','docs/architecture/factory/NATIVE-WORKFLOWS.md')+'</details>';
}
