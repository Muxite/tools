'use strict';

const baselineJobs = [
  {
    id:'intent', title:'Capture intent', agent:'Intent intake agent', lane:'factory',
    cc:['compiler.intent_brief'], needs:[],
    work:'Use the Intent Compiler to capture the requested model, workload, target and success criteria. Ask for clarification when a choice changes scope. Record user preferences and observed facts with their sources.',
    output:'A reviewed intent brief that identifies the request, constraints and open decisions. The Contract Compiler can bind approved goals to model obligations and measurable gates.'
  },{
    id:'contract', title:'Compile the engine contract', agent:'Contract compilation agent', lane:'factory',
    cc:['compiler.engine_contract'], needs:[['intent','A reviewed intent brief identifying approved goals, constraints and open decisions.']],
    work:'Read the system ontology and the requested workload. Bind text-only generation, one device, the model and tokenizer revisions, position semantics, expert count and routed width, any shared branch, supported pack, memory ceiling and quality gates. In this example the starting pack already exists.',
    output:'A versioned contract with tensor and token conventions, a memory envelope, fixed test prompts and explicit acceptance thresholds. Unresolved checkpoint fields stay open until the pack is inspected.'
  },{
    id:'plan', title:'Issue work orders', agent:'Workflow planner', lane:'factory',
    cc:['factory.workflow_planning'], needs:[['contract','A revision naming the checkpoint, target and required outputs.']],
    work:'Inspect the empty repository. Declare interfaces for token batches, KV positions, route ID/weight pairs, weight handles and logits. Assign owners for both sides of each interface and publish fixture shapes before implementations arrive.',
    output:'Versioned interfaces, fixture seeds and work orders with named producers and consumers. The weights, request, model, router and state agents can start independently.'
  },{
    id:'weights', title:'Index the checkpoint', agent:'Weight loader agent', lane:'engine',
    cc:['weights.load_checkpoint'], needs:[['plan','Tensor naming, layout and weight-handle contracts plus access to the pinned checkpoint.']],
    work:'Read metadata and validate offsets, shapes, per-tensor types and expert addressing without loading the full model. Resolve every required tensor and expose an addressable slice for one expert.',
    output:'A hashed tensor inventory with packed byte spans, shape and type checks, and a verified sample slice. Placement needs actual sizes. Kernels need real encoded blocks.'
  },{
    id:'serving', title:'Build the image interface', agent:'Request agent', lane:'engine',
    cc:['serving.request_gateway','tokenizer.prepare_request','scheduler.request_lifecycle','batch.execution_layout'],
    needs:[['plan','Frozen token IDs, cancellation protocol, sequence identifiers and batch interface.']],
    work:'Publish the completions endpoint, listen port, mount contract and optional profiling switches in a versioned image interface manifest. Build the single-device admission loop. Exercise prompt encoding, positions, a cancelled request and streamed text using stub model outputs. Keep sequence identity through batch packing.',
    output:'An image interface manifest and executable request replay with expected token IDs, offsets, stop events and cancellation cleanup. The generation agent can replace the stub with the real forward call.'
  },{
    id:'reference', title:'Build a reference decoder block', agent:'Model math agent', lane:'engine',
    cc:['model.embedding_service','model.decoder_architecture','attention.dense_execution','model.logit_head'],
    needs:[['plan','Decoder ordering, tensor axes, mask and position semantics, and fixture weights.']],
    work:'Implement embedding lookup, normalization and residual order, causal attention and the vocabulary head on small tensors. Expose the routed FFN as a replaceable function. Use known-answer intermediate values and compare a token step to full-prefix recomputation.',
    output:'Inspectable hidden rows, attention output and logits for deterministic fixtures, including positions beyond zero. Kernel and integration agents can localize a first divergent layer.'
  },{
    id:'routing', title:'Implement the routed FFN', agent:'MoE math agent', lane:'engine',
    cc:['model.expert_routing','model.expert_ffn','merge.expert_contributions'], needs:[['plan','The score transform, rank bias, selected-score normalization, routed width, shared-branch policy and token-row layout.']],
    work:'Start with a token-by-token oracle. Then group rows by expert, run gate/up and down projections, and reconstruct weighted rows. Select IDs under the contract and keep each ID paired with its contribution weight.',
    output:'Expected IDs, weights and merged rows for ties, shared picks across tokens and a nontrivial permutation. The storage agent can replay the exact demanded IDs without a working full model.'
  },{
    id:'state', title:'Manage KV and workspace', agent:'Runtime memory agent', lane:'engine',
    cc:['memory.sequence_kv','memory.runtime_arenas'], needs:[['plan','KV shape and dtype, sequence lifetime, maximum context and arena interface.']],
    work:'Allocate position-indexed KV and temporary buffers. Exercise append, read, cancellation and reuse on a tiny budget. Export a size model for persistent and peak temporary allocations at each supported shape.',
    output:'A tested slot lifecycle and a peak-byte model with allocation lifetimes. Placement can reserve room for the live request before spending the remainder on experts.'
  },{
    id:'placement', title:'Budget resident and streamed bytes', agent:'Placement agent', lane:'engine',
    cc:['placement.partition_model','memory.runtime_arenas'], needs:[['weights','Real tensor byte sizes and addressable expert offsets.'],['state','Peak KV and scratch reservations at the contracted shapes.']],
    work:'Partition a single unified memory budget across the resident model, live state, expert slots, staging, runtime overhead and headroom. Check the largest demanded expert set and any transient unpacking. Choose a bounded schedule or reject a shape that cannot fit.',
    output:'A feasible placement manifest with slot capacities, staging limits and a forced-miss fixture. The streaming agent can allocate against a concrete byte ceiling.'
  },{
    id:'storage', title:'Serve exact expert demand', agent:'Expert storage agent', lane:'engine',
    cc:['engine.expert_streaming'], needs:[['placement','Feasible slot and staging limits plus file offsets.'],['routing','A replay of authoritative per-layer expert IDs and aligned weights.']],
    work:'Resolve a selected ID to packed storage bytes, join an in-flight fill, wait for readiness and hold the slot until its final consumer finishes. Force eviction, repeated IDs and cold misses.',
    output:'A cold-cache replay mapping every consumed handle to the expected expert and byte hash, plus peak bytes and exposed wait time. Compare with resident execution on the same small tensors.'
  },{
    id:'kernels', title:'Bind device operators', agent:'CUDA operator agent', lane:'engine',
    cc:['backend.execute_operators','weights.decode_blocks'], needs:[['weights','Sample packed blocks and declared type, strides and alignment.'],['reference','Known hidden rows and logits for reference attention and projections.'],['routing','Expected per-expert projections and weighted output.']],
    work:'Bind supported GPU operators, select by format and shape, and expose the actual kernel or fallback. Here the contract selects a quantized pack. Check decoded values and operator results separately at prefill and one-token decode shapes.',
    output:'A supported-shape table, dispatch trace and device-vs-reference error report with tolerances. Unsupported formats and forced fallbacks have explicit outcomes.'
  },{
    id:'assemble', title:'Generate the first text', agent:'Generation integration agent', lane:'engine',
    cc:['decode.advance_sequence','sampling.select_tokens','factory.source_integration'],
    needs:[['serving','Replayable tokenized request and expected response events.'],['state','Verified KV append and release interface.'],['storage','Verified slot readiness and forced-cold replay.'],['kernels','Bound operators and numerical parity fixtures.']],
    work:'Connect prompt prefill, next-token logits, sampling, stop handling and text streaming. Run the small deterministic end-to-end case first. Then exercise the actual checkpoint through the bounded storage path under the target memory budget.',
    output:'A reviewable source revision, reproducible build command and prompt replay with emitted IDs, per-step logits, peak bytes and clean shutdown. Record the first mismatch if a gate fails.'
  },{
    id:'image', title:'Build the runnable image', agent:'Image builder', lane:'factory',
    cc:['factory.builder'], needs:[['assemble','Reviewed source revision, dependency inputs and a known-good startup and decode command.'],['serving','Image interface manifest with endpoint, mount paths, readiness and diagnostic controls.']],
    work:'Resolve the executable and runtime dependencies into an image. Mount the separately identified checkpoint at startup. Use the published port and volume bindings on a clean target. Replay a completion from outside the image and retrieve an output trace when profiling is enabled.',
    output:'An image digest, dependency inventory, checkpoint digest and boot transcript. The lab can reproduce the exact executable and model combination.'
  },{
    id:'qualify', title:'Qualify the target run', agent:'Experiment agent', lane:'lab',
    cc:['factory.controlled_experiment'], needs:[['contract','Frozen workload, baseline, quality and resource thresholds.'],['image','Runnable image digest, pack digest and successful smoke replay.']],
    work:'Measure held-out quality, time to first token, decode latency, cold storage waits and peak unified memory on the target. Repeat warm and cold conditions separately. Route any failed gate to the agent that owns its first divergent artifact.',
    output:'A trial receipt with run conditions, quality and cost deltas, uncertainty and a scoped verdict. The planner and RSI can accept the build or reopen a specific work order.'
  }
];

const constructionJobs=[...baselineJobs,...constructionOptions];
// Activating a variant adds these gates to the baseline dependency graph.
const conditionalGates=[
 ['pack_convert','placement','Recompute slot capacity and transient expansion from the qualified pack.'],
 ['pack_convert','kernels','Repeat dispatch and parity checks with the new pack digest and block layout.'],
 ['dense_path','assemble','Include the verified dense callable at the checkpoint-declared layer indices.'],
 ['capture','assemble','Integrate graph replay after eager parity and address-lifetime checks pass.'],
 ['prefix_reuse','assemble','Enable session reuse after hit, invalidation and eviction replays agree with fresh prefill.'],
 ['route_trace','qualify','Compare tracing enabled and disabled on the same image, prompts and cache state.'],
 ['forecast','qualify','Compare exact-demand and hint-enabled runs under the same cache budget and quality gates.']
];
const jobIndex=new Map(constructionJobs.map(j=>[j.id,j]));
const lanes={factory:'Factory',engine:'Engine',lab:'Lab',option:'Contract option'};
const groups=[
 ['Intent and contract','intent','contract'],['Work orders','plan'],['Parallel foundations','weights','serving','reference','routing','state'],
 ['Placement and kernels','placement','kernels'],['Storage integration','storage'],['Generation','assemble'],
 ['Image and qualification','image','qualify']
];
const jobLink=(id,label)=>pill(label||jobIndex.get(id).title,address('construction',id));

function jobCard(job){
 return '<article class="build-card lane-'+job.lane+'"><small>'+esc(lanes[job.lane])+' · '+esc(job.agent)+'</small><h3><a data-job="'+job.id+'" href="'+address('construction',job.id)+'">'+esc(job.title)+'</a></h3><div class="build-ccs">'+job.cc.map(cc=>pill(cc,'#cc/'+cc)).join(' ')+'</div><p class="build-input"><b>Starts after</b> '+(job.needs.map(([up])=>jobLink(up)).join(' ')||'the user supplies the build intent')+'</p></article>';
}
// This rehearsal records only the example receipts the reader chooses to accept.
const acceptedBuildJobs=[];
function drawReadyJobs(){
 const panel=document.querySelector('#ready-jobs');
 const ready=baselineJobs.filter(job=>!acceptedBuildJobs.includes(job.id)&&job.needs.every(([id])=>acceptedBuildJobs.includes(id)));
 const last=jobIndex.get(acceptedBuildJobs.at(-1));
 panel.innerHTML='<div aria-live="polite"><p><b>'+ready.length+' work orders ready</b> · '+acceptedBuildJobs.length+' of '+baselineJobs.length+' example receipts accepted.</p>'+
 (last?'<p><b>Last receipt · '+esc(last.agent)+'</b><br>'+esc(last.output)+'</p>':'')+
 (ready.length?'<div class="build-ready">'+ready.map(job=>'<button data-accept="'+job.id+'" type="button">Accept · '+esc(job.title)+'</button>').join('')+'</div>':'<p>The example image and qualification receipt have reached the planner.</p>')+'</div>'+
 '<button class="basic" id="undo-build" type="button" '+(last?'':'disabled')+'>Undo last receipt</button>';
 panel.onclick=event=>{
   const button=event.target.closest('button');
   if(!button)return;
   if(button.id==='undo-build')acceptedBuildJobs.pop();
   else if(ready.some(j=>j.id===button.dataset.accept))acceptedBuildJobs.push(button.dataset.accept);
   drawReadyJobs();
   (panel.querySelector('[data-accept]')||panel.querySelector('#undo-build')).focus({preventScroll:true});
 };
}
function construction(id){
 if(id==='trials'||id.startsWith('trial-')&&sparkTrials.some(t=>id==='trial-'+t.id)){
   root.innerHTML=sparkTrialView(id.slice(6));
   return;
 }
 if(id==='designs'){
   root.innerHTML='<div class="crumb">'+pill('From scratch','#construction')+'</div><h1>Engine design choices</h1><div id="engine-variations">'+engineVariations()+'</div>';
   return;
 }
 const job=jobIndex.get(id);
 if(job){
   const extra=conditionalGates.filter(([producer,consumer])=>producer===id||consumer===id);
   const gates=extra.length?sec('When a variant is enabled','<ul>'+extra.map(([producer,consumer,receipt])=>'<li>'+jobLink(producer)+' → '+jobLink(consumer)+' '+esc(receipt)+'</li>').join('')+'</ul>'):'';
   const next=constructionJobs.filter(j=>j.needs.some(([up])=>up===id));
   root.innerHTML='<div class="crumb">'+pill('From scratch','#construction')+'</div><article id="work-order" class="sheet lane-'+job.lane+'"><small>'+esc(lanes[job.lane])+' · '+esc(job.agent)+'</small><h1>'+esc(job.title)+'</h1><div class="pills">'+job.cc.map(cc=>pill(cc,'#cc/'+cc)).join(' ')+'</div>'+sec('Start when',job.needs.length?'<ul>'+job.needs.map(([up,receipt])=>'<li>'+jobLink(up)+' '+esc(receipt)+'</li>').join('')+'</ul>':'<p>The user supplies the model, machine and workload intent.</p>')+sec('Agent work',list(job.work))+sec('Acceptance evidence',list(job.output))+gates+sec('Who uses it',next.length?'<ul>'+next.map(j=>'<li>'+jobLink(j.id)+' '+esc(j.needs.find(([up])=>up===id)[1])+'</li>').join('')+'</ul>':list(job.lane==='option'?'The planner sends the variant through image build and controlled qualification before promotion.':'The planner and RSI receive the scoped verdict and supporting measurements.'))+'</article>';
   return;
 }
 root.innerHTML='<h1>Build an engine from scratch</h1><p class="lead">One illustrative assignment for a text MoE whose weights exceed one device’s memory. The Intent Compiler captures the request. The Contract Compiler binds the reviewed brief to the system ontology and fixes the obligations and leaves permitted implementation choices open. The planner can reuse evidence, assign several CCs to one agent, or revise the next job.</p><p><b>Example ontology choices</b> · One device removes the inter-rank exchange job. Weights larger than available memory activate exact-demand streaming. The checkpoint supplies routed width and shared-expert policy to the same routing CC.</p><div class="build-key">'+Object.entries(lanes).map(([key,label])=>'<span class="lane-'+key+'">'+esc(label)+'</span>').join('')+'</div><p class="build-note">Select a work order for its start evidence and the artifact its consumer needs. Jobs with ready inputs can overlap. For example, kernel qualification can continue while the storage agent builds cold fills.</p>'+
 '<div class="tools"><a class="pill" href="#construction/designs">Compare engine designs →</a><button class="pill" type="button" data-build-jump="conditional-jobs">Contract-dependent work ↓</button></div>'+
 '<section class="sheet build-sim"><h2>Try the handoffs</h2><p>Accept example receipts to see which agents can start in parallel. This rehearses one possible ordering. The live workflow can branch on evidence. Open any work order below to inspect the evidence first.</p><div id="ready-jobs"></div></section>'+
 groups.map(([title,...ids])=>'<section class="build-group"><h2>'+esc(title)+'</h2><div class="build-grid">'+ids.map(id=>jobCard(jobIndex.get(id))).join('')+'</div></section>').join('')+
 '<section class="build-group" id="conditional-jobs" tabindex="-1"><h2>Contract-dependent work</h2><p>Activate these work orders when the model, workload or a measured bottleneck calls for them. The planner adds a dependency wherever a variant changes the build. A converted pack reopens placement and kernel checks. A checkpoint with dense FFN layers makes the dense-path receipt mandatory for assembly.</p><div class="build-grid">'+constructionOptions.map(jobCard).join('')+'</div></section><div id="engine-variations" tabindex="-1">'+engineVariations()+'</div>';
 drawReadyJobs();
 for(const b of root.querySelectorAll('[data-build-jump]'))b.onclick=()=>{const section=document.getElementById(b.dataset.buildJump);section.focus({preventScroll:true});section.scrollIntoView()};
}
