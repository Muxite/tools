/* Each owner produces one bounded engineering change. The factory lab qualifies it. */
const sparkTrials=[
 {
  id:'coalesce',title:'Coalesce expert reads',badge:'ds4 extent coalescer',owner:'engine.expert_streaming',partners:['weights.prepare_artifact'],
  source:'https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/ds4_cuda.cu#L29486',label:'ds4 · adjacent extents',
  mechanism:'ds4 merges adjacent file extents when their destination slots are contiguous and stages through two buffers. The streamer owns both read planning and slot lifetime.',
  test:'Replay identical exact misses against the deployed file layout. Compare one read per extent, coalescing alone, then coalescing with two staging buffers. Repeat with deliberately scattered expert offsets at the same staging-byte ceiling.',
  decision:'Build when eligible contiguous runs occur often enough to lower exposed read wait and token latency. Reject if padding, extra copies or staging pressure eat the gain. Hash every delivered slot against its source extent.',
  artifact:'Extent-length histogram, system read calls per token, device bytes read per token, slot hashes and peak staging bytes.'
 },{
  id:'ready',title:'Execute ready experts first',badge:'Strata ready-first dispatcher',owner:'model.expert_ffn',partners:['engine.expert_streaming','merge.expert_contributions'],
  source:'https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/core/expert_source.cpp#L5250-L5285',label:'Strata · multi-token CPU dispatch',
  mechanism:'The dispatcher can execute already-available CPU expert rows while other exact-demand reads complete. Assignment identity must survive reordering so the same weighted rows reach the same tokens.',
  test:'Measure a wait-for-all barrier against ready-first dispatch with identical IDs, CPU threads and byte budget. Sweep resident fraction on multi-token prefill and include single-token decode as a control. Inject one delayed read.',
  decision:'Build for the phase where wall time falls within the agreed quality and memory gates. Stop if the batch has little independent ready work or threading aggravates memory contention.',
  artifact:'Per-expert ready/start/finish timeline, blocked time, completed assignment counts and reference-vs-restored token rows.'
 },{
  id:'forecast',title:'Early expert-demand prediction',badge:'Strata predictor',owner:'routing.forecast_expert_demand',partners:['engine.expert_streaming','observability.runtime_events'],
  source:'https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/core/expert_source.cpp#L3230-L3262',label:'Strata · nonresident-demand scoring',
  mechanism:'Spend spare I/O bandwidth on experts predicted before routing finishes. Only an exact selection authorizes consumption.',
  test:'Timestamp nonresident demand and first use. First replay an oracle that knows the next demanded IDs but pays the measured read time and bandwidth. If it can hide useful wait, compare causal hints on held-out requests against demand-only at equal cache and staging bytes.',
  decision:'Stop before training if even the oracle has too little lead time. Build if causal hints reduce p95 decode latency with unchanged exact output, including under deliberately wrong hints.',
  artifact:'Lead-time distribution, useful bytes ready before first use, wasted bytes, evicted demanded bytes and p95 inter-token latency.'
 },{
  id:'skip',title:'Quantization and skipped experts',badge:'Strata tail-skip policy',owner:'model.expert_ffn',partners:['model.expert_routing','engine.expert_streaming'],
  source:'https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/program/generate.cpp#L13817-L13863',label:'Strata · verify-path policy',
  mechanism:'For an eligible cache miss the execution policy can omit a low-ranked selected contribution. The FFN owner records what executed. The router continues to report the authoritative selection.',
  test:'Only with approximate execution authorized, run a two-by-two comparison of two admitted packs and skipping off/on. Match prompts, seed, slot byte budget and workload. Confirm the policy actually fired; record selection and executed contribution separately.',
  decision:'Reject for an exact-compute contract. For an approximate one, require held-out quality within tolerance and useful latency reduction versus skipping off for the same pack. Check rare domains and cold starts separately.',
  artifact:'Pack/policy matrix, skipped probability mass, executed rows, held-out quality intervals and decode latency.'
 },{
  id:'retention',title:'Request-aware cache eviction',badge:'research',owner:'engine.expert_streaming',partners:['observability.runtime_events'],
  source:'https://arxiv.org/abs/2401.14361',label:'MoE-Infinity · activation-aware offloading',
  mechanism:'MoE-Infinity uses request activation history to guide expert caching and prefetch. Isolate retention first. On Spark, an evicted expert may require an SSD read to return.',
  test:'Replay held-out request traces with LRU and a request-aware victim policy, identical cache bytes, no prefetch and only past observations. Use a future-aware eviction oracle solely to estimate available improvement. Repeat across topic switches.',
  decision:'Prototype when replay materially reduces demanded read bytes against LRU. Promote only if the physical run reduces exposed wait and decode latency after policy overhead. Stop when the demand set has little temporal reuse.',
  artifact:'Eviction decisions, reread bytes, cache turnover and latency split by request/domain.'
 },{
  id:'dispatch',title:'Choose CPU or GPU per expert batch',badge:'research',owner:'backend.execute_operators',partners:['model.expert_ffn','placement.partition_model'],
  source:'https://proceedings.iclr.cc/paper_files/paper/2025/hash/8cd1ce03ea58b3d7dfd809e4d42f08ea-Abstract-Conference.html',label:'Fiddler · CPU/GPU orchestration',
  mechanism:'Fiddler motivates choosing where to execute routed rows. Its discrete-memory transfer costs do not carry over to Spark. Both processors share memory bandwidth, and either path must still wait for missing storage bytes.',
  test:'On the same Spark and tensor format, time CPU and GPU expert kernels across row counts, first with ready weights, then with real cold fills. Use the measured crossover for a dispatch policy. Compare against the best fixed executor with the same thread and memory limits.',
  decision:'Build adaptive dispatch only if it beats the fixed baseline on held-out shapes and mixed prefill/decode while preserving numerical parity. Reject when CPU work starves storage workers or the GPU.',
  artifact:'Row-count crossover table, device utilization, CPU thread counts, concurrent bandwidth and expert-output error.'
 },{
  id:'precision',title:'Lower precision on selected cache misses',badge:'research',owner:'engine.expert_streaming',partners:['weights.prepare_artifact','backend.execute_operators'],
  source:'https://arxiv.org/abs/2411.01433',label:'HOBBIT · mixed-precision expert loading',
  mechanism:'HOBBIT considers loading a lower-precision representation for less critical expert misses. Cache identity must include precision and pack revision. Routing to the same expert can now produce different values depending on cache history.',
  test:'Compare fixed high precision, fixed low precision and selective low-precision fills. Match model, workload, byte budget and route policy. Replay identical prompts with cold and warm caches. Verify the actual kernel and dtype on each miss.',
  decision:'Build only if the adaptive policy meets quality gates across cache histories and earns a useful improvement over the best admissible fixed pack. Include disk space for both forms and peak decode workspace.',
  artifact:'Per-fill dtype and byte count, quality by cache state, pack footprint, fallback time and latency distribution.'
 },{
  id:'prune',title:'Expert pruning for a task domain',badge:'research',owner:'weights.prepare_artifact',partners:['model.expert_routing'],
  source:'https://proceedings.mlr.press/v262/sarkar24a.html',label:'UNCURL · task-specific expert pruning',
  mechanism:'Prepare a derived checkpoint with a fixed retained expert set per layer. Unlike cache eviction, a removed expert cannot be fetched on a miss. The experiment therefore needs permission to change the model.',
  test:'Choose the keep list on calibration requests only. At matched precision and physical memory, compare the original with several pruning budgets on disjoint in-domain and off-domain prompts. Validate router index remapping before timing either pack.',
  decision:'Build a domain-specific artifact only if its quality bounds and cold-storage gains meet contract gates. Stop if fewer stored parameters leave demanded bytes or p95 latency unchanged.',
  artifact:'Parent and derived digests, per-layer ID map, resident fraction, bytes read per generated token and quality deltas by domain.'
 }
];
function sparkTrialView(id){
 const chosen=sparkTrials.find(t=>t.id===id);
 const entries=chosen?[chosen]:sparkTrials;
 const link=id=>pill(id,'#cc/'+id);
 return '<div class="crumb">'+pill('Compare engines','#construction/designs')+(chosen?' '+pill('All Spark experiments','#construction/trials'):'')+'</div><h1>'+(chosen?esc(chosen.title):'Out-of-core MoE experiments')+'</h1>'+
 '<p class="lead">Start with an exact-demand trace on the target. For many short adjacent reads, try coalescing. For repeated misses on the same experts, try retention. Test prediction only when demand arrives early enough to hide a read.</p>'+
 '<section class="sheet"><h2>Shared trial conditions</h2><p>One Spark, one model, weights larger than usable unified memory. Freeze the image, pack, tokenized prompts, context, sampling and memory ceiling except for the variable under test. Include OS, KV, staging and scratch in peak memory. Separate warm process cache from warm filesystem cache and cold SSD reads. Report actual device I/O alongside logical bytes requested.</p><p>Set the minimum worthwhile improvement, quality tolerance and memory limit in the contract before testing. Alternate paired baseline and candidate runs. Advance only when repeated measurements clear the agreed gate; an interval spanning that gate is inconclusive. Timing and quality here are proposed tests.</p>'+link('compiler.engine_contract')+' '+link('factory.controlled_experiment')+'</section>'+
 '<div class="trial-grid">'+entries.map(t=>'<article class="sheet spark-trial"><span class="proof-chip '+(t.badge==='research'?'paper':'single')+'">'+esc(t.badge==='research'?'Research-backed Spark proposal':'One-engine example · '+t.badge)+'</span>'+(chosen?'':'<h2>'+esc(t.title)+'</h2>')+'<p><b>Owner</b> '+link(t.owner)+'</p><p><b>Works with</b> '+t.partners.map(link).join(' ')+'</p><p>'+esc(t.mechanism)+' '+ext(t.label,t.source)+'</p>'+sec('Cheapest decisive test',list(t.test))+sec('Build decision',list(t.decision))+sec('Handoff to the lab',list(t.artifact))+'</article>').join('')+'</div>';
}
