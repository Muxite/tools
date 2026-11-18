/* Contract-dependent engine mechanisms for the standalone construction/designs view. */
function engineVariations() {
  const cards = [
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
    ]
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
    ]
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
    ]
  },
  {
    "title": "Model splitting and expert exchange",
    "status": "Reference extension",
    "activate": "Enable model splitting when execution spans devices or ranks. Enable expert exchange when token owners and selected expert owners differ.",
    "target": "This target is one DGX Spark. Storage-backed expert streaming is required; multi-device collectives and remote expert exchange are outside its baseline.",
    "roles": [
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
    ]
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
    ]
  },
  {
    "title": "Early expert-demand prediction",
    "status": "Optional target work",
    "activate": "Enable when transfer latency can be hidden with causal advance features and a bounded hint budget.",
    "target": "Exact-demand storage reads remain required on Muse. Prediction is an optional optimization: only the authoritative router determines the IDs and weights consumed. Adoption and benefit on this target remain unqualified.",
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
    ]
  }
];
  return '<section class="sheet" id="variations-section" tabindex="-1"><h2>When the engine contract changes</h2>' +
    '<p>These mechanisms appear in inspected paths across Strata, llama.cpp, ds4 and SGLang. Each citation covers a particular family and execution mode. Enable a capability because the contract needs it, then bind its interface and independent check.</p>' +
    '<p><strong>Current target</strong> · Text generation with Muse Spark Open on one 128 GB DGX Spark, with model weights larger than usable memory. The baseline requires bounded expert streaming and authoritative routed IDs and weights. It does not assume adapters, recurrence, sparse attention, multi-device execution or speculation. The inspected Muse path is routed-only; a shared expert is enabled only for a checkpoint that declares it.</p>' +
    '<div class="cards">' + cards.map(card =>
      '<article class="listing"><div class="tagline">' + esc(card.status) + '</div><h3>' + esc(card.title) + '</h3>' +
      '<div aria-label="Selected engine examples">' + [...new Set(card.examples.map(x=>x.engine))].map(engine=>'<span class="ref-engine" data-engine="'+esc(engine)+'">'+esc(engine)+'</span>').join('') + '</div>' +
      '<p><strong>Activate when</strong> · ' + esc(card.activate) + '</p>' +
      '<p><strong>On this target</strong> · ' + esc(card.target) + '</p>' +
      '<div class="pills">' + card.roles.map(id => pill(id, '#cc/' + canonical(id))).join(' ') + '</div>' +
      '<details><summary>Inspected mechanisms and checks</summary>' +
      card.examples.map(example => '<div class="cap-row"><strong>' + esc(example.engine) + '</strong><p>' + esc(example.text) + '</p><p>' + example.refs.map(ref => ext(ref.title, ref.url)).join(' · ') + '</p></div>').join('') +
      '<p><strong>Check the boundary</strong> · ' + esc(card.check) + '</p></details></article>'
    ).join('') + '</div>' +
    '<p class="caption">Source inspected at the linked revisions. These examples establish implementation mechanisms, not successful transfer to Muse or measured DGX Spark performance. An unlisted binding is an audit gap, not proof that an engine lacks the mechanism. New formats, mode combinations and backends need their own admission and conformance checks.</p></section>';
}
