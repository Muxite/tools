/* Contract-dependent engine mechanisms for the standalone construction/designs view. */
function engineVariations() {
  const cards = [
  {
    "title": "Router scoring and shared experts",
    "group": "checkpoint",
    "status": "Target design",
    "activate": "Read the checkpoint configuration, gate tensors and any independent shared-expert tensors.",
    "target": "One engine can supply multiple selectors. For each layer bind its scoring transform, correction bias, routed width, selected-score normalization and shared path. Five routed plus one shared executes a different function from six routed.",
    "roles": [
      "model.expert_routing",
      "model.expert_ffn",
      "merge.expert_contributions"
    ],
    "check": "Construct a bias that changes the last selected ID. Compare aligned mixture weights, shared-branch contribution when declared, and the final weighted hidden row against the checkpoint reference.",
    "examples": [
      {
        "engine": "ds4",
        "text": "The scored path ranks with an optional bias and gathers weights from the original transformed scores.",
        "refs": [
          {
            "title": "Score selection and weighting",
            "url": "https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/ds4.c#L13062"
          }
        ]
      }
    ]
  },
  {
    "title": "Prefix reuse and expert residency",
    "group": "budget",
    "status": "Target design",
    "activate": "Repeated prefixes justify retaining KV between requests.",
    "target": "Prefix KV, expert slots and prefetch buffers draw from one 128 GB pool. A prefix hit can save prefill while the displaced expert adds a storage stall on every decode step. The break-even point depends on prefix reuse, route locality and context length.",
    "roles": [
      "memory.reusable_sessions",
      "memory.sequence_kv",
      "engine.expert_streaming",
      "placement.partition_model",
      "factory.controlled_experiment"
    ],
    "check": "Sweep the prefix and expert cache allocations at fixed total bytes. Record time to first token, inter-token latency, peak bytes and exact-demand storage waits across repeated and unique prefixes.",
    "examples": [
      {
        "engine": "ds4",
        "text": "The exact-demand expert cache checks that selected experts fit after reserving headroom. The shared-budget comparison is a proposed Spark trial.",
        "refs": [
          {
            "title": "Expert slot admission",
            "url": "https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/ds4_cuda.cu#L29069"
          }
        ]
      }
    ]
  },
  {
    "title": "Quantization and skipped experts",
    "group": "budget",
    "status": "Target design",
    "activate": "Compare two supported weight packs under a fixed quality gate.",
    "target": "Smaller blocks can keep more experts resident and reduce bytes per miss. Kernel fallback, decode cost and numerical error can offset that gain. Strata’s tail-skip policy can also change which selected experts execute. Freeze skipping off for the quantization comparison, then qualify skipping separately.",
    "roles": [
      "weights.prepare_artifact",
      "backend.execute_operators",
      "engine.expert_streaming",
      "factory.controlled_experiment"
    ],
    "check": "Log pack digest, dispatch path, selected and executed experts, bytes read and task score. Compare quality and decode latency with identical prompts and cache conditions.",
    "examples": [
      {
        "engine": "Strata",
        "text": "Tail-skip eligibility depends on cache residency, backend configuration and expert format.",
        "refs": [
          {
            "title": "Tail-skip policy",
            "url": "https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/program/generate.cpp#L13817-L13863"
          }
        ]
      }
    ],
    "audit": "Strata tail-skip policy"
  },
  {
    "title": "Expert pruning for a task domain",
    "group": "budget",
    "status": "Target design",
    "activate": "The contract permits a derived model for a bounded task domain.",
    "target": "An offline pruning trial can shrink the pack and working set, but experts removed for one domain may matter on another. Treat the result as a new model revision.",
    "roles": [
      "weights.prepare_artifact",
      "model.expert_routing",
      "factory.controlled_experiment"
    ],
    "check": "Deliver surviving expert IDs, router-to-pack mapping and pack digest. Compare held-out in-domain and out-of-domain quality, packed bytes and cold latency against the original. This is a proposed capability within weight preparation.",
    "examples": [
      {
        "engine": "Research",
        "text": "UNCURL studies task-aware offline pruning of experts per layer. Target-engine integration remains unverified in this audit.",
        "refs": [
          {
            "title": "UNCURL · Sarkar et al.",
            "url": "https://proceedings.mlr.press/v262/sarkar24a.html"
          }
        ]
      }
    ],
    "audit": "research"
  },
  {
    "title": "Request-specific adapters",
    "status": "Reference extension",
    "activate": "Enable when the service contract permits LoRA adapters that change the effective model for a request.",
    "target": "Adapters are outside the current Muse build. Adding them introduces base-model identity, projection compatibility, residency and per-request isolation obligations.",
    "roles": [
      "weights.adapter_binding",
      "batch.execution_layout"
    ],
    "check": "Interleave two adapters and compare each request with its isolated run; remove them and recover the base output.",
    "examples": [
      {
        "engine": "llama.cpp",
        "text": "The projection graph adds the scaled B(Ax) delta to the base result.",
        "refs": [
          {
            "title": "LoRA deltas enter the actual projection graph",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/src/llama-graph.cpp#L1703-L1718"
          }
        ]
      },
      {
        "engine": "SGLang",
        "text": "The manager prepares active adapter IDs, pool fetches and captured-batch metadata.",
        "refs": [
          {
            "title": "Per-batch adapter routing and residency are prepared before execution",
            "url": "https://github.com/sgl-project/sglang/blob/1aa45c661758b2ff99dc8c57ec849175ab4625ed/python/sglang/srt/lora/lora_manager.py#L497-L535"
          }
        ]
      }
    ],
    "group": "compose"
  },
  {
    "title": "Recurrent and hybrid sequence state",
    "status": "Reference extension",
    "activate": "Enable only when the checkpoint defines recurrent transitions or a hybrid recurrent/attention stack.",
    "target": "The current Muse contract uses attention state. A recurrent implementation in another model family supplies a construction example, not a substitute for Muse attention.",
    "roles": [
      "sequence.recurrent_execution",
      "memory.sequence_kv",
      "model.decoder_architecture"
    ],
    "check": "Compare chunked prefill with repeated decode, then reset, copy and restore both state kinds at sequence boundaries.",
    "examples": [
      {
        "engine": "llama.cpp",
        "text": "The Qwen3Next graph calls a recurrent transition and then gated normalization.",
        "refs": [
          {
            "title": "Qwen graph invokes a recurrent state transition",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/src/models/qwen3next.cpp#L526-L536"
          }
        ]
      },
      {
        "engine": "ds4",
        "text": "The Qwen GDN scan validates persistent state buffers and dispatches admitted head dimensions.",
        "refs": [
          {
            "title": "Qwen CUDA recurrent scan checks state and geometry before launch",
            "url": "https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/ds4_qwen4_cuda.cuh#L1805-L1823"
          }
        ]
      }
    ],
    "group": "checkpoint"
  },
  {
    "title": "Indexed sparse attention",
    "status": "Reference extension",
    "activate": "Enable when the checkpoint defines candidate indexing, or when a separately qualified sparse replacement is explicitly allowed.",
    "target": "Sparse attention is not part of the current Muse baseline. Candidate selection changes visible context and needs its own oracle; compatible shapes alone do not establish equivalent model behavior.",
    "roles": [
      "attention.sparse_execution",
      "memory.sequence_kv"
    ],
    "check": "Check candidate IDs and causal visibility first, then compare attention output using exactly the same selected set.",
    "examples": [
      {
        "engine": "SGLang",
        "text": "Configured DSA layers construct an indexer; decode converts selected top-k indices to KV page access before sparse attention. This closes a previous evidence gap.",
        "refs": [
          {
            "title": "Configured DSA models construct and share actual indexers",
            "url": "https://github.com/sgl-project/sglang/blob/1aa45c661758b2ff99dc8c57ec849175ab4625ed/python/sglang/srt/models/deepseek_v2.py#L2168-L2207"
          },
          {
            "title": "Sparse decode turns selected indices into KV page access",
            "url": "https://github.com/sgl-project/sglang/blob/1aa45c661758b2ff99dc8c57ec849175ab4625ed/python/sglang/srt/layers/attention/dsa_backend.py#L3152-L3178"
          }
        ]
      },
      {
        "engine": "Strata",
        "text": "The previously audited QSA score, shortlist and decode path is another model-specific sparse binding. Its candidate policy is not interchangeable with DSA.",
        "refs": [
          {
            "title": "QSA selected-candidate decode",
            "url": "https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/kernels/cuda/qsa_decode_attn.cu#L1217"
          }
        ]
      }
    ],
    "group": "checkpoint"
  },
  {
    "title": "Model splitting and expert exchange",
    "status": "Reference extension",
    "activate": "Enable model splitting when execution spans devices or ranks. Enable expert exchange when token owners and selected expert owners differ.",
    "target": "On one Spark, assign storage-backed expert streaming. In a multi-device build, check composition explicitly. The inspected llama.cpp pipeline path requires the MoE cache size to be zero. Combining both requires new integration and validation.",
    "roles": [
      "engine.expert_streaming",
      "parallel.model_execution",
      "parallel.expert_exchange",
      "placement.partition_model",
      "merge.expert_contributions"
    ],
    "check": "Compare with an unsharded reference and use tagged rows to prove correct ownership, ordering and exactly-once weighted return.",
    "examples": [
      {
        "engine": "llama.cpp",
        "text": "Layer-pipeline mode checks device/event support and explicitly excludes a nonzero MoE cache. Tensor split also has an architecture admission guard.",
        "refs": [
          {
            "title": "Pipeline execution is enabled only under explicit device and cache guards",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/src/llama-context.cpp#L574-L603"
          },
          {
            "title": "Tensor split admission depends on architecture implementation",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/src/llama-model.cpp#L397-L403"
          }
        ]
      },
      {
        "engine": "SGLang",
        "text": "DeepEP dispatch/combine carries hidden rows, selected IDs and weights through a checked stage lifecycle.",
        "refs": [
          {
            "title": "Expert dispatch and combine share a checked stage lifecycle",
            "url": "https://github.com/sgl-project/sglang/blob/1aa45c661758b2ff99dc8c57ec849175ab4625ed/python/sglang/srt/layers/moe/token_dispatcher/deepep.py#L1047-L1099"
          }
        ]
      },
      {
        "engine": "ds4",
        "text": "TP peers negotiate matching ownership and execution-mode flags before proceeding.",
        "refs": [
          {
            "title": "Tensor-parallel peers negotiate matching execution modes",
            "url": "https://github.com/antirez/ds4/blob/b3f50180ec2c7324892be1f50bc83555ccb8d5e7/ds4_tp.c#L2516-L2537"
          }
        ]
      }
    ],
    "group": "guard"
  },
  {
    "title": "Draft-and-verify decoding",
    "status": "Reference extension",
    "activate": "Enable when the contract allows speculation and the target verifier can preserve the required token distribution and committed sequence state.",
    "target": "The current baseline uses ordinary decoding. A draft model is optional: suffix or n-gram proposals can use history alone. Proposal speed does not establish correct acceptance or a net speedup.",
    "roles": [
      "decode.speculative_execution",
      "decode.advance_sequence",
      "sampling.select_tokens"
    ],
    "check": "Force rejection at each draft position and compare subsequent target state with ordinary decoding; measure proposal and verification costs separately.",
    "examples": [
      {
        "engine": "Strata",
        "text": "Source arbitration selects a bounded continuation with a sufficient suffix match.",
        "refs": [
          {
            "title": "Draft arbitration chooses an eligible continuation source",
            "url": "https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/spec/draft_source.cpp#L13-L33"
          }
        ]
      },
      {
        "engine": "SGLang",
        "text": "The n-gram worker explicitly has no draft model and resets a CPU corpus.",
        "refs": [
          {
            "title": "N-gram speculation uses corpus proposals without a draft model",
            "url": "https://github.com/sgl-project/sglang/blob/1aa45c661758b2ff99dc8c57ec849175ab4625ed/python/sglang/srt/speculative/ngram_worker.py#L152-L159"
          }
        ]
      },
      {
        "engine": "llama.cpp",
        "text": "Accepted counts are passed back to the sequence proposer through its accept interface.",
        "refs": [
          {
            "title": "Accepted draft counts return to the proposer state interface",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/common/speculative.cpp#L3522-L3547"
          }
        ]
      }
    ],
    "group": "budget"
  },
  {
    "title": "Early expert-demand prediction",
    "status": "Optional target work",
    "activate": "Enable when transfer latency can be hidden with causal advance features and a bounded hint budget.",
    "target": "The router selects the IDs and weights. The streamer serves exact misses. A predictor can start reads early using a bounded hint budget. A wrong hint may waste bytes or cause a stall, but every consumed expert must still match the authoritative selection.",
    "roles": [
      "routing.forecast_expert_demand",
      "engine.expert_streaming",
      "observability.runtime_events",
      "factory.controlled_experiment"
    ],
    "check": "Separate predicted, demanded, resident and executed sets. Report lead time, useful completed reads and wasted bytes; bad predictions must preserve the exact-demand output.",
    "examples": [
      {
        "engine": "Strata",
        "text": "Startup validates future-router tensors and connects lookahead to warming or optional swap-space hints.",
        "refs": [
          {
            "title": "Lookahead startup connects optional predictions to the expert source",
            "url": "https://github.com/Niko1221/Strata/blob/c77572806996349b49995e4f98d41b5294d36a21/src/program/generate.cpp#L9609-L9647"
          }
        ]
      },
      {
        "engine": "llama.cpp",
        "text": "The inspected MoE cache plans from already-selected IDs. That establishes exact-demand residency, not a causal future predictor.",
        "refs": [
          {
            "title": "Exact-demand cache reads selected IDs before planning uploads",
            "url": "https://github.com/ggml-org/llama.cpp/blob/9048bad8d6e3a0f9f1726e238e451181c7e02613/src/llama-moe-cache.cpp#L790-L821"
          }
        ]
      }
    ],
    "group": "compose",
    "audit": "Strata predictor"
  }
];
  const groups=[
    ['compose','Can work together','Preserve the interface between the two jobs and verify the combined result.'],
    ['checkpoint','Checkpoint decides','Bind the operator and its parameters to the selected model and layer.'],
    ['budget','Single-Spark tradeoff','Hold the workload fixed and measure quality, memory and latency together.'],
    ['guard','Implementation constraint','Check the pinned backend’s admission rules before assigning integration work.']
  ];
  function showCard(card){
    const trial=sparkTrials.find(t=>t.title===card.title);
    const badge=card.audit==='research' ? '<span class="proof-chip paper">Research candidate</span>' :
      card.audit ? '<span class="proof-chip single">One-engine evidence · '+esc(card.audit)+'</span>' : '';
    return '<article class="listing"><h3>'+esc(card.title)+'</h3>'+badge+'<div>'+[...new Set(card.examples.map(x=>x.engine))].filter(e=>e!=='Research').map(e=>'<span class="ref-engine" data-engine="'+esc(e)+'">'+esc(e)+'</span>').join('')+'</div><p>'+esc(card.target)+'</p>'+
      '<p><b>Planner assigns</b></p><div class="pills">'+card.roles.map(id=>pill(id,'#cc/'+canonical(id))).join(' ')+'</div>'+
      (trial?'<p><b>Trial owner</b> '+pill(trial.owner,'#cc/'+trial.owner)+' '+pill('Inspect decision experiment','#construction/trial-'+trial.id)+'</p>':'')+
      '<details><summary>Activation, evidence and acceptance</summary><p>'+esc(card.activate)+'</p>'+
      card.examples.map(example=>'<div class="cap-row"><b>'+esc(example.engine)+'</b><p>'+esc(example.text)+'</p>'+example.refs.map(r=>ext(r.title,r.url)).join(' · ')+'</div>').join('')+
      '<p><strong>Acceptance</strong> · '+esc(card.check)+'</p></details></article>';
  }
  const active=atlas.roles.filter(r=>r.target && r.kind!=='factory');
  const common=active.filter(r=>engines.every(engine=>r.examples.some(x=>x.engine===engine)));
  return '<section id="variations-section"><h2>Which features fit together?</h2><p class="lead">'+common.length+' of '+active.length+' target engine CCs have source examples in all four engines. One codebase can support many variants. The checkpoint fixes the required computation, and the planner qualifies each enabled combination within the single-Spark budget.</p>'+
    '<div class="comparison-key">'+groups.map(([key,title])=>'<span class="cmp-tag cmp-'+key+'">'+esc(title)+'</span>').join('')+'</div>'+
    '<p class="caption">Purple marks a mechanism verified in one audited engine. Pink marks a published research method whose integration in these four engines is unverified. Both labels describe evidence coverage.</p>'+
    '<section class="sheet"><h2>Out-of-core MoE experiments</h2><p>Each candidate has an owning CC, a baseline, a test on one Spark and a build decision.</p><div class="pills">'+sparkTrials.map(t=>'<a class="proof-chip '+(t.badge==='research'?'paper':'single')+'" href="#construction/trial-'+t.id+'">'+esc(t.title)+'</a>').join(' ')+'</div><p>'+pill('Read all eight experiments','#construction/trials')+'</p></section>'+
    groups.map(([key,title,detail])=>'<section class="comparison-group cmp-'+key+'"><h2>'+esc(title)+'</h2><p>'+esc(detail)+'</p><div class="cards">'+cards.filter(card=>card.group===key).map(showCard).join('')+'</div></section>').join('')+'</section>';
}
