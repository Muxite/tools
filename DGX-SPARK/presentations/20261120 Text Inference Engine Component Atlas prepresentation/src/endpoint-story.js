// Each assignment refers to the same stable worker identity used by the CC catalog.
const endpointStory = (() => {
  const ranking = (id, title, summary, star, ...legacyIds) => ({id, title, summary, star, legacyIds});
  const revision = endpointData.revision;
  const pinned = (path, line, label) => ({label, url:"https://github.com/ggml-org/llama.cpp/blob/"+revision+"/"+path+"#L"+line});
  const stepSources = {
    "Admit the model":[pinned("conversion/muse_spark.py",37,"Muse converter registration"), pinned("src/models/muse-spark.cpp",223,"Muse text inference graph")],
    "Compile a mixed-precision pack":[pinned("tools/quantize/quantize.cpp",146,"Per-tensor precision overrides")],
    "Resolve weights and execute":[pinned("src/llama-moe-cache.h",35,"MoE cache interface")],
    "Exercise the endpoint":[pinned("common/arg.cpp",2735,"Host expert placement and cache flags"),pinned("tools/server/README.md",622,"Streaming token protocol")],
    "Dispatch a bounded change":[{label:"Existing offline predictor evaluation method (local reference)",url:"../../reference/factory-source/jiuwenswarm/factory/ccs/expert_prediction/METHOD.md"}],
    "Pick the work from the trace":[pinned("src/llama-moe-cache.h",23,"Host misses and device slots")]
  };
  const step = (title, body, ...legacyIds) => ({title, body, legacyIds, sources:stepSources[title] || []});
  return {
    rankings: [
      ranking("cache","Expert weight cache","A selected expert must be usable before its rows can run. Measure how long demand waits, whether an early fill arrives in time, and whether a slot is reused while still in use.",true,"engine.expert_streaming"),
      ranking("router","Expert router","The selected IDs and mixture weights determine the model’s answer and supply the ground truth for judging a predictor.",true,"model.expert_routing"),
      ranking("placement","Weight placement planner","The resident set, KV reservation and available slots determine how often an expert must move. Change this budget and the same predictor can face a different workload.",true,"placement.partition_model"),
      ranking("quantization","Quantization and weight-pack preparation","Precision and block layout change bytes per expert, feasible residency, eligible kernels and numerical error.",true,"weights.prepare_artifact"),
      ranking("prediction","Expert demand predictor","An early hint can hide a measured wait. Test its lead time, unused bytes and effect on client latency. Integration and performance on this target are open.",true,"routing.forecast_expert_demand"),
      ranking("kernels","Packed-weight kernel dispatch","A smaller representation helps only when a target kernel can consume its layout efficiently.",false,"backend.execute_operators","weights.decode_blocks"),
      ranking("experts","Routed expert execution and combination","Selected experts must receive the right rows and apply mixture weights exactly where the model specifies.",false,"model.expert_ffn","merge.expert_contributions"),
      ranking("scheduling","Request scheduling and batching","Batch composition changes queue time, throughput and the opportunity for requests to reuse experts.",false,"scheduler.request_lifecycle","batch.execution_layout"),
      ranking("state","Sequence-state management","KV growth competes for memory with expert slots. Position and sequence ownership must survive batching and cancellation.",false,"memory.sequence_kv"),
      ranking("loop","Generation loop","Repeated decode turns correct model outputs into a completion with an observable stop reason.",false,"decode.advance_sequence")
    ],
    walkthroughs: [
      {id:"request",title:"Request to streamed token",summary:"Follow one completion from the client, through a routed layer, and back to the client.",steps:[
        step("Submit a completion","The client supplies prompt text and generation settings. The service validates the request and gives it an identity for streaming and cancellation.","serving.request_gateway"),
        step("Tokenize and schedule","The codec returns vocabulary IDs. The scheduler selects runnable prompt or decode work and constructs a batch with positions and sequence identities.","tokenizer.prepare_request","scheduler.request_lifecycle","batch.execution_layout"),
        step("Evaluate the model","The decoder binds the selected architecture and builds the forward graph. Attention consults the sequence’s KV state. A routed layer sends selected expert IDs and mixture weights to expert execution.","model.decoder_architecture","memory.sequence_kv","model.expert_routing"),
        step("Resolve weights and execute","Resolve selected experts against the resident set. The backend executes the expert operations and returns results for weighted combination. A prefetch hint can only change readiness.","engine.expert_streaming","backend.execute_operators","merge.expert_contributions"),
        step("Sample and stream","The model returns logits. Apply the requested sampling and grammar rules, emit the accepted token, and advance sequence state until the stop condition. The client receives chunks and a final status.","sampling.select_tokens","decode.advance_sequence","serving.request_gateway")
      ]},
      {id:"checkpoint",title:"Checkpoint to packed-weight kernel",summary:"Can expert matrices use lower precision while the router retains higher precision on this target?",steps:[
        step("Admit the model","Pin checkpoint, tokenizer and architecture. Check tensor names, shapes, shard ranges, vocabulary IDs and routed-layer semantics against the model binding. Reject an unsupported architecture before promising execution.","weights.load_checkpoint","model.decoder_architecture","tokenizer.prepare_request"),
        step("Compile a mixed-precision pack","Use the model’s actual tensor map to identify router and expert matrices. Assign an approved block type to experts and a supported higher precision to router tensors. Record exceptions, source hash, tool revision, recipe and output digest. Reuse a pack that already satisfies this contract.","weights.prepare_artifact"),
        step("Validate scales and layout","Read back each tensor’s actual type, block layout, byte range and scales. Compare signed extrema, tails and sampled expert projections against an independent decoder. A valid GGUF header alone cannot establish compatibility.","weights.load_checkpoint","weights.decode_blocks"),
        step("Bind the target kernel and budget","Verify the backend operation for the actual type, shape and strides. Include repacking, workspace, KV and expert slots in peak memory. Reject an infeasible configuration or explicitly qualify its fallback.","backend.execute_operators","placement.partition_model","memory.runtime_arenas"),
        step("Qualify the completion","On held-out prompts compare router IDs, mixture weights, logits and agreed quality measures with a pinned higher-precision reference. Compare resident and cold execution of the same pack. Record target memory, latency and throughput. Muse Spark Open qualification remains open.","model.expert_routing","factory.controlled_experiment")
      ]}
    ],
    demo:{
      title:"Can earlier expert readiness shorten decode?",
      summary:"A proposed agent-built change to a real llama.cpp completions endpoint. Start with a measured bottleneck, then follow the change from contract to client.",
      baseline:"Use the pinned server and a supported MoE GGUF on the target. Freeze model and tokenizer digests, backend, CPU expert placement, concurrency, prompt fixtures, output length and cache budget. Record the host, driver and build flags. Run the identical binary twice before estimating a candidate gain.",
      metrics:[
        {label:"Primary · decode latency",value:"Milliseconds per generated token: (arrival of last token − arrival of first token) / (generated tokens − 1). Count token IDs; exclude stop-only frames and samples shorter than two tokens."},
        {label:"Client experience",value:"Time from POST to first token, total elapsed time and aggregate generated tokens per second, with prompt length and concurrency."},
        {label:"Memory and movement",value:"Peak unified memory, bytes moved, extra prefetch bytes, lead time and exposed wait for selected experts. Report host-to-device traffic and storage reads separately."},
        {label:"Correctness",value:"Compare deterministic token IDs and finish reasons for baseline and candidate. For a changed precision recipe, freeze numerical tolerances and a held-out quality gate before the run."}
      ],
      steps:[
        step("Build and identify the baseline","At revision 9048bad8d6e3a0f9f1726e238e451181c7e02613 on the CUDA target, configure with cmake -S . -B build -DGGML_CUDA=ON and build with cmake --build build --config Release --target llama-server -j. Record the compiler, artifact digest, launch command and model digest.","factory.builder"),
        step("Set one memory cap for both owners","Choose two supported context or concurrency settings. For each setting, obtain the actual sequence-state allocation, reserve fixed weights, backend workspace and headroom, then set the expert-cache limit from the remaining capacity. Restart the server for each configuration. Keep the same cap, model, context setting and cache limit within each baseline/candidate pair. Record how many expert slots fit and measure peak unified memory under load.","memory.sequence_kv","placement.partition_model","engine.expert_streaming","memory.runtime_arenas"),
        step("Exercise the endpoint","Start build/bin/llama-server -m MODEL.gguf --host 127.0.0.1 --port 8080 --cpu-moe --moe-cache-mib BUDGET. Substitute the pinned local model and a positive budget in MiB. POST /completion with a fixed prompt, stream=true, temperature=0, cache_prompt=false and n_predict=64. Capture token IDs and monotonic client arrival times. Keep fresh-process cold and warmed trials separate.","serving.request_gateway","observability.runtime_events"),
        step("Pick the work from the trace","Instrument authoritative selection time, lookup, transfer and readiness. The pinned MoE cache can use a device buffer for host-resident experts and compute a share of misses on CPU. Verify the active path. If waits are negligible, compare kernel time and batch queueing, select the larger measured contributor, and preregister the replacement intervention and endpoint metric.","engine.expert_streaming","backend.execute_operators","scheduler.request_lifecycle"),
        step("Dispatch a bounded change","Contract compiler freezes permitted inputs, memory and byte budgets, output parity, the metric and the rollback condition. Workflow orchestrator dispatches the predictor and cache builders. Screen hints on held-out requests with the existing offline evaluator; add an optional hint path using only information available before selection. Preserve demand fallback, deduplicate fills and protect in-use slots. Log the contract revision, assignments and attempt IDs.","compiler.engine_contract","factory.workflow_planning","routing.forecast_expert_demand","engine.expert_streaming"),
        step("Integrate and identify the candidate","The source integration agent supplies the reviewed diff, parent commit and regression results. The image assembler records the exact executable or image digest. Use that digest to serve a real completion and retain the client transcript with its token IDs.","factory.source_integration","factory.builder"),
        step("Cancel one of two active requests","Run two requests that share expert weights. Cancel one while an expert fill is in flight. Check that its sequence pages become eligible for reuse, the other request keeps valid state and expert handles, and the surviving request matches its isolated output. Record reusable slots and allocated bytes separately: making a page reusable inside a pool can leave the process allocation unchanged.","scheduler.request_lifecycle","memory.sequence_kv","engine.expert_streaming"),
        step("Issue the independent verdict","A different agent runs at least six matched trial pairs per cache condition, alternating baseline-first and candidate-first. Compute paired median decode-time savings per workload. Require the lower bound of a paired 95% bootstrap interval to exceed the absolute median baseline-vs-baseline variation, output parity on every fixture, and both declared budgets to pass. Otherwise retain the result as inconclusive or rejected. Publish raw timings, fixtures, digest and verdict together.","factory.controlled_experiment")
      ],
      limitations:"Experiment specification. The historical offline predictor evaluates trace coverage and timing; it supplies no endpoint speed measurement. The pinned cache source establishes host/device residency behavior. Disk-backed fetching, Muse support, and a performance gain each require independent target evidence."
    }
  };
})();
