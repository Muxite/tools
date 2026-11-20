function engineReadiness() {
  const component = id => cmpLink(components.get(id));
  const order = id => pill(jobs.get(id).title,'#construction/'+id);
  const action = id => actLink(actions.get(id));
  const refs = (...indices) => indices.map(index=>{
    const ref=atlas.muse.refs[index];
    return '<a class="pill" href="'+e(ref.url)+'" target="_blank" rel="noopener noreferrer">'+e(ref.title)+' ↗</a>';
  }).join(' ');
  const gate = (title, ownerIds, orders, work, check, links) =>
    '<details class="insight"><summary><strong>'+e(title)+'</strong></summary>'+
    '<p><strong>Component owners</strong></p><div class="pills">'+ownerIds.map(component).join(' ')+'</div>'+
    fact('Integration work',work)+fact('Acceptance evidence',check)+
    '<p><strong>Work orders</strong></p><div class="pills">'+orders.map(order).join(' ')+'</div>'+
    (links?'<div class="tools">'+links+'</div>':'')+'</details>';
  const intro='<h1>Engine integration readiness</h1><p class="lead">The first delivery target is a reproducible text completion from an identified Muse pack on one DGX Spark. These gates specify the evidence a build must produce. The atlas records no qualifying run for that pack.</p>';
  const facts='<section class="sheet"><h2>Facts to freeze before coding against the pack</h2>'+
    fact('Artifact identities','Record the authorized checkpoint revision and shard digests, tensor directory, tokenizer, prompt template, generation settings and independent reference revision. Pin the runtime image, toolchain and selected backend.')+
    fact('Per-layer configuration','Read widths, Q/KV head geometry, layer types, the full/sliding mask schedule, RoPE/NoPE schedule and window, normalization parameters and residual gate configuration. Read expert counts, routed width, projection dimensions, bias, score scaling and shared-expert policy from the selected model.')+
    fact('Capacity and acceptance','Inventory packed bytes, scales and kernel alignment. Reserve unified memory for resident weights, live KV, scratch, staging and concurrent expert slots. Freeze workload, quality tolerances, cold/warm timing gates and rejection behavior before measuring.')+
    '<p>The published configuration defaults to 62 layers and eight routed picks. The actual pack determines allocation and dispatch. The inspected SGLang Muse path accepts zero shared experts.</p>'+
    '<div class="tools">'+order('contract')+' '+order('weights')+' '+refs(0,5,18)+'</div></section>';
  const execution='<section class="sheet"><h2>Pack to next token</h2><p>Follow each gate to its owners and work orders. A failed comparison identifies the first interface that needs investigation.</p>'+
    gate('1. Bind the pack and establish a feasible memory plan',
      ['weights.checkpoint_reader','placement.weight_placement_planner','memory.workspace_allocator'],['weights','state','placement'],
      'Validate tensor identities, logical dimensions, types, packed scales and byte ranges against the layer manifest. Expose an addressable expert slice and calculate a slot budget under the contracted request shape.',
      'Reject a truncated tensor or incompatible layout at startup. Match a decoded weight block to a trusted decoder. Record peak allocated bytes and the capacity left for a forced cold miss.',action('startup/layout')+' '+action('startup/place'))+
    gate('2. Turn a client prompt into admitted, positioned rows',
      ['serving.engine_image_gateway','tokenizer.token_codec','scheduler.request_scheduler','batch.batch_layout_builder'],['serving'],
      'Bind the chosen template and tokenizer. Preserve the request ID, token position and sequence state handle through prompt chunking, cancellation and batch packing.',
      'Compare the rendered prompt and exact token IDs with the pinned tokenizer. Interleave unequal prompts and cancel one. The surviving request keeps its positions and never reads the released slot.',refs(15))+
    gate('3. Match embeddings, attention and both residual boundaries',
      ['model.token_embedding_layer','model.decoder_stack','attention.dense_attention_operator','memory.sequence_kv_cache'],['reference','state','kernels'],
      'Normalize embeddings, apply the configured pre-norm, project Q/K/V and normalize Q/K. Apply the layer’s RoPE/NoPE and full/sliding mask, update KV, normalize and gate the attention output, then apply its projection and learned residual join. Preserve the separate post-FFN residual join and final model norm.',
      'Capture reference tensors before and after each residual join and compare full prefill with incremental decode across a window boundary. A masked attention kernel passing alone leaves head mapping, gate placement and state visibility to be checked.',refs(8,9,11,12,13))+
    gate('4. Assemble and verify the routed feed-forward path',
      ['model.expert_router','merge.expert_row_dispatcher_and_combiner','engine.expert_weight_cache','model.expert_feed_forward_block'],['routing','storage','reference'],
      'Use FP32 router scores and rank with correction bias. Gather original selected scores, normalize and scale. Project into expert width with the prescribed norm, group token rows, wait for selected weights, evaluate gate/up/down, post-normalize each expert output, apply mixture weights, accumulate in token order and project back to model width. Bind a dense branch only for a layer declaring it.',
      'For the normalized illustrative routing fixture, select E0 and E2 with weights 5/7 and 2/7. On the actual checkpoint test its k and scale. Compare forced-cold output with resident output, including empty groups, reordered completions and uneven row counts.',action('model/route')+' '+action('model/combine')+' '+refs(2,6,7,19))+
    gate('5. Produce vocabulary scores and commit a token',
      ['model.vocabulary_projection_head','sampling.token_sampler','decode.generation_loop','tokenizer.token_codec'],['reference','assemble','serving'],
      'Apply final normalized hidden rows to the vocabulary head. Multiply logits by the configured output multiplier before tanh softcapping. Sample with the request policy, commit the selected ID, advance the sequence and emit text or a finish event.',
      'Compare full vocabulary logits on a fixed prompt before sampling. With deterministic settings compare token IDs, stop position and streamed UTF-8 across prefill and successive decode steps. Record the earliest divergent layer or token.',refs(14)+' '+action('generate/commit'))+
    gate('6. Qualify the image independently on the target',
      ['factory.image_builder','factory.qualification_lab','observability.runtime_event_recorder'],['assemble','image','qualify'],
      'Build the reviewed revision and collect the completed image digest. Mount the identified pack and tokenizer on a clean target. Drive completions from an external client, holding prompt set, sampler and resource limits fixed.',
      'Publish image, pack and workload identities, output IDs, quality deltas, cold and warm first-token/decode timings and peak unified memory. Report a verdict for each contract threshold. Exercise cancellation, cleanup and a forced expert miss under load.',component('serving.engine_image_gateway'))+'</section>';
  const reuse='<section class="sheet"><h2>Library reuse and engine-owned code</h2><p>The implementation team can evaluate the following reuse boundaries against the selected pack.</p>'+
    fact('Dependency manifest','For every reused library, pin its version or revision, build flags and required device features. Record the component owner, supported formats and shapes, fallback, and parity fixture. Carry these identities into the image and probe the chosen path from inside the container on the DGX Spark.')+
    fact('Tokenizer and model reference','Use the pinned tokenizer and upstream reference model for known-answer data. The engine owns request formatting, token handoff and streaming behavior. Compare special IDs, template bytes and split UTF-8 output.')+
    fact('Numerical kernels','Reuse a compatible GEMM, attention or grouped expert kernel after verifying shape, dtype, strides, quantized layout, synchronization and numerical error. The engine owns dispatch guards, fallback selection and Muse-specific operator ordering, normalization, routing and residual joins.')+
    fact('Storage and device libraries','Use supported file I/O, allocation, transfer and stream primitives. The engine owns tensor-to-byte-range identity, placement, slot pinning, in-flight fill coalescing and last-reader release. A cold exact-demand comparison establishes the baseline for any prefetch experiment.')+
    '<div class="tools">'+component('backend.kernel_dispatcher')+' '+component('weights.weight_block_decoder')+' '+component('engine.expert_weight_cache')+' '+refs(3,4,17)+'</div></section>';
  const limits='<section class="sheet"><h2>Evidence still required</h2><p>The source audit establishes operator semantics and candidate implementations. The selected checkpoint, tokenizer bytes, approved reference outputs, target memory fit and sustained data-access cost still need independent evidence. Historical Strata measurements concern a different identified engine and pack. Keep optional sparse attention, recurrence, distributed execution and speculative decoding conditional on the deployment contract.</p><div class="tools">'+order('qualify')+' '+refs(1,18)+'</div></section>';
  root.innerHTML=intro+'<div class="tools">'+pill('Engine assemblies','#engine')+' '+pill('Follow one token','#trace/token/0')+' '+pill('Follow a cold expert fetch','#trace/cold/0')+' '+pill('From scratch','#construction')+'</div>'+facts+execution+reuse+limits;
}
