// Each component has one home on the map. Return edges revisit that same node.
const {engineStages, engineHandoffs, factoryStages, factoryHandoffs} = (() => {
  const pack = 'weights.weight_pack_compiler';
  const reader = 'weights.checkpoint_reader';
  const placement = 'placement.weight_placement_planner';
  const adapter = 'weights.adapter_binder';
  const gateway = 'serving.engine_image_gateway';
  const codec = 'tokenizer.token_codec';
  const scheduler = 'scheduler.request_scheduler';
  const prefix = 'memory.prefix_state_cache';
  const batch = 'batch.batch_layout_builder';
  const generation = 'decode.generation_loop';
  const draft = 'decode.speculative_decoder';
  const embedding = 'model.token_embedding_layer';
  const decoder = 'model.decoder_stack';
  const attention = 'attention.dense_attention_operator';
  const sparse = 'attention.sparse_attention_operator';
  const kv = 'memory.sequence_kv_cache';
  const recurrent = 'sequence.recurrent_state_operator';
  const dense = 'dense.dense_feed_forward_block';
  const router = 'model.expert_router';
  const rows = 'merge.expert_row_dispatcher_and_combiner';
  const cache = 'engine.expert_weight_cache';
  const predictor = 'routing.expert_demand_predictor';
  const expert = 'model.expert_feed_forward_block';
  const exchange = 'parallel.distributed_expert_exchange';
  const head = 'model.vocabulary_projection_head';
  const sampler = 'sampling.token_sampler';
  const kernel = 'backend.kernel_dispatcher';
  const graph = 'graph.execution_graph_backend';
  const workspace = 'memory.workspace_allocator';
  const blocks = 'weights.weight_block_decoder';
  const distributed = 'parallel.distributed_execution_coordinator';
  const events = 'observability.runtime_event_recorder';
  const qmatmul = 'backend.quantized_matmul_kernel';
  const cpulane = 'backend.cpu_weight_repack';
  const engram = 'weights.engram_row_cache';
  const store = 'engine.host_expert_store';
  const cpu = 'host.hostcpu';
  const accelerator = 'host.device';
  const dram = 'host.dram';
  const storage = 'host.ssd';

  const engineStages = [
    {
      title: 'Model startup',
      caption: 'The engine binds checkpoint tensors and budgets space for requests and streamed weights.',
      main: [reader, placement], side: [pack, adapter]
    },
    {
      title: 'Request intake',
      caption: 'The gateway accepts a request. The codec formats the prompt and returns model token IDs.',
      main: [gateway, codec], side: []
    },
    {
      title: 'Scheduling and generation',
      caption: 'A prompt span or a decode token becomes a batch row with a position and state handle.',
      main: [scheduler, batch, generation], side: [prefix, draft]
    },
    {
      title: 'Embedding and attention',
      caption: 'Token IDs become hidden rows. Each decoder block applies its configured attention or state update.',
      main: [embedding, decoder, attention], side: [kv, sparse, recurrent, engram]
    },
    {
      title: 'Feed-forward layers and experts',
      caption: 'A routed block groups rows by expert and recombines their weighted outputs. A dense block has its own feed-forward path.',
      main: [router, rows, expert], side: [cache, store, predictor, dense, exchange]
    },
    {
      title: 'Next token and response',
      caption: 'The head produces vocabulary scores. The sampler selects a token for commit, streaming and the next decode step.',
      main: [head, sampler], side: []
    },
    {
      title: 'Shared execution backend',
      caption: 'Model steps use kernels, working buffers and optional graph replay throughout a request.',
      main: [graph, kernel], side: [qmatmul, cpulane, workspace, blocks, distributed, events]
    },
    {
      title: 'Host compute, memory and storage',
      caption: 'Engine submissions reach the host CPU, accelerator and physical memory at the relevant execution step.',
      main: [cpu, accelerator], side: [dram, storage]
    }
  ];

  const engineHandoffs = [
    [pack, reader, 'Converted weight pack and manifest, when conversion is needed', 'branch'],
    [storage, reader, 'Checkpoint shards and tensor directory bytes', 'platform'],
    [reader, placement, 'Validated tensor sizes, formats and storage ranges', 'flow'],
    [reader, decoder, 'Bound layer tensors with validated projections, normalization weights and residual-gate parameters', 'support'],
    [reader, head, 'Bound vocabulary projection weights or the verified shared embedding binding', 'support'],
    [attention, kv, 'New keys and values with sequence IDs, positions and destination page slots', 'support'],
    [kernel, cache, 'Last-reader completion fence for the identified expert slot generation', 'support'],
    [workspace, kernel, 'Scratch buffer handles and byte bounds for the selected eager kernel', 'support'],
    [decoder, kernel, 'Eager operator invocation with bound operands, shapes and execution stream', 'flow'],
    [reader, embedding, 'Vocabulary identity and bound embedding table', 'support'],
    [placement, cache, 'Expert placement, source ranges and slot budget', 'support'],
    [adapter, decoder, 'Request-specific adapter handles for affected projections', 'branch'],
    [gateway, codec, 'Prompt or messages and template settings', 'flow'],
    [codec, scheduler, 'Encoded prompt IDs and request identity', 'flow'],
    [prefix, scheduler, 'Matching prefix length and resumable state handle', 'branch'],
    [scheduler, batch, 'Admitted tokens, sequence slots and execution budget', 'flow'],
    [batch, generation, 'Prompt spans or decode rows with positions and state handles', 'flow'],
    [generation, embedding, 'Prompt IDs or last committed decode IDs', 'flow'],
    [embedding, decoder, 'Hidden rows in token order', 'flow'],
    [decoder, attention, 'Query, key and value rows with position and mask rules', 'flow'],
    [kv, attention, 'Visible key and value rows for this sequence', 'support'],
    [attention, decoder, 'Attended rows for output projection and residual addition', 'rejoin'],
    [decoder, sparse, 'Queries, index state and permitted candidate budget', 'branch'],
    [kv, sparse, 'Indexed key and value rows', 'support'],
    [sparse, decoder, 'Attention rows over the selected positions', 'rejoin'],
    [decoder, recurrent, 'Configured hybrid-layer input and previous sequence state', 'branch'],
    [recurrent, decoder, 'Updated state and recurrent output rows', 'rejoin'],
    [decoder, dense, 'Hidden rows for a configured dense feed-forward layer', 'branch'],
    [dense, decoder, 'Transformed rows for residual addition', 'rejoin'],
    [decoder, router, 'Gate scores or a token-keyed expert lookup', 'flow'],
    [router, rows, 'Selected expert IDs and mixture weights per token', 'flow'],
    [router, cache, 'Authoritative demand for selected expert weights', 'flow'],
    [predictor, cache, 'Optional early fetch hints before selection', 'branch'],
    [storage, cache, 'Byte ranges for missing expert weights', 'platform'],
    [cache, expert, 'Ready weight handles protected through final use', 'support'],
    [rows, expert, 'Token rows grouped by expert and group offsets', 'flow'],
    [rows, exchange, 'Routed rows and destination assignments on multiple devices', 'branch'],
    [exchange, rows, 'Returned remote expert rows mapped to source tokens', 'rejoin'],
    [expert, rows, 'Expert outputs in grouped row order', 'rejoin'],
    [rows, decoder, 'Weighted expert results restored to token order', 'rejoin'],
    [decoder, head, 'Final normalized hidden rows', 'flow'],
    [head, sampler, 'Vocabulary logits for each selected output row', 'flow'],
    [sampler, generation, 'Selected token ID and continue or finish decision', 'rejoin'],
    [generation, scheduler, 'Updated sequence position and next-step eligibility', 'loop'],
    [generation, codec, 'Committed output IDs and terminal status', 'flow'],
    [codec, gateway, 'Decoded text chunks for the response stream', 'flow'],
    [generation, draft, 'Committed context and target verification state', 'branch'],
    [draft, generation, 'Verified prefix and synchronized sequence state', 'rejoin'],
    [decoder, graph, 'Typed model operations, shapes and buffer bindings', 'support'],
    [graph, kernel, 'Lowered operations or compatible recorded launches', 'support'],
    [workspace, graph, 'Working buffers with valid execution lifetimes', 'support'],
    [blocks, kernel, 'Decoded values or kernel-compatible weight blocks', 'support'],
    [distributed, generation, 'Rank-local batch and validated transferred state', 'branch'],
    [kernel, cpu, 'Host work items for CPU kernels', 'platform'],
    [kernel, accelerator, 'Device kernel launches and synchronization events', 'platform'],
    [dram, accelerator, 'Weight, state and activation bytes for device work', 'platform'],
    [kernel, events, 'Kernel identity, timestamps and completion events', 'support'],
    [events, gateway, 'Correlated trace and counters for diagnostics', 'support'],
    [kernel, qmatmul, 'Quantized matmul or expert-grouped launch with packed format, shapes and selected expert IDs', 'support'],
    [kernel, cpulane, 'CPU expert-lane matmul over host-resident packed or repacked blocks', 'support'],
    [storage, engram, 'Engram table rows at token-derived offsets', 'platform'],
    [engram, decoder, 'Ready Engram rows for the current token window', 'support'],
    [storage, store, 'Whole expert byte ranges read with unbuffered I/O', 'platform'],
    [store, cache, 'Host-tier expert bytes for a device-cache fill', 'support'],
    [store, cpulane, 'Host-tier expert bytes read in place by the CPU lane', 'support']
  ];

  const intent = 'compiler.intent_compiler';
  const contract = 'compiler.contract_compiler';
  const planner = 'factory.workflow_planner';
  const source = 'factory.source_integration_workbench';
  const image = 'factory.image_builder';
  const lab = 'factory.qualification_lab';
  const factoryStages = [
    {title: 'Intent', caption: 'Capture the requested outcome, constraints and open questions.', main: [intent], side: []},
    {title: 'Contract', caption: 'The Contract compiler uses the reviewed brief and system ontology to create the engine contract.', main: [contract], side: []},
    {title: 'Agent dispatch', caption: 'The Workflow orchestrator dispatches agents with the builder capabilities required by the contract.', main: [planner], side: []},
    {title: 'Source integration', caption: 'Apply and test the component change in the identified source tree.', main: [source], side: []},
    {title: 'Image build', caption: 'Collect the completed build and identify its reproducible image.', main: [image], side: []},
    {title: 'Independent qualification', caption: 'Measure the candidate against the frozen workload and return a scoped verdict.', main: [lab], side: []}
  ];
  const factoryHandoffs = [
    [intent, contract, 'Reviewed intent brief, sourced constraints and review decision', 'flow'],
    [contract, planner, 'Approved engine contract, obligations and acceptance gates', 'flow'],
    [planner, source, 'Component work order, assigned CCs and dependency identities', 'flow'],
    [source, image, 'Tested candidate revision and build request', 'flow'],
    [image, lab, 'Collected build result, image digest and manifest', 'flow'],
    [contract, lab, 'Frozen workload, resource limits and pass criteria', 'support'],
    [lab, planner, 'Scoped verdict, measurements and evidence for acceptance or repair', 'loop']
  ];
  return {engineStages, engineHandoffs, factoryStages, factoryHandoffs};
})();
