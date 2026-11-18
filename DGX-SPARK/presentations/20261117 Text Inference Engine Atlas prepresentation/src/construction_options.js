const constructionOptions = [
  {
    "id": "route_trace",
    "agent": "Runtime instrumentation engineer",
    "title": "Record expert demand and readiness",
    "cc": [
      "observability.runtime_events"
    ],
    "needs": [
      [
        "routing",
        "Qualified selector emitting aligned token, layer, expert ID and weight records."
      ],
      [
        "storage",
        "Fill and release events keyed by layer, expert and slot generation."
      ]
    ],
    "output": "A versioned trace joins authoritative demand to fill completion and first use. The prediction engineer can score hints, while the lab can bound observer overhead with instrumentation disabled.",
    "work": "Activate when a residency or prefetch question requires timestamps that existing counters cannot provide. Sample route selection, exact demand, transfer completion and first consumption on a correlated timeline. Preserve recorded token and expert order.",
    "lane": "option"
  },
  {
    "id": "forecast",
    "agent": "Expert demand prediction engineer",
    "title": "Predict early weight demand",
    "cc": [
      "routing.forecast_expert_demand",
      "engine.expert_streaming"
    ],
    "needs": [
      [
        "route_trace",
        "Time-ordered demand and readiness trace with a held-out workload partition."
      ],
      [
        "storage",
        "Exact miss path that serves the correct expert independently of hints."
      ]
    ],
    "output": "An opt-in hint producer and a held-out comparison of useful bytes, unused bytes, exposed wait and end-to-end token latency. Keep prediction disabled when it fails the contract’s gain and quality gates.",
    "work": "Activate when measured demand stalls leave enough time to stage weights and the transfer budget allows speculative reads. Train or tune only on features available before the authoritative decision. Inject wrong hints and compare final model outputs to the exact demand-only path.",
    "lane": "option"
  },
  {
    "id": "capture",
    "agent": "Execution graph engineer",
    "title": "Capture stable decode launches",
    "cc": [
      "graph.lower_capture_replay",
      "backend.execute_operators"
    ],
    "needs": [
      [
        "kernels",
        "Passing eager execution with recorded launch shapes, dtypes and buffer dependencies."
      ],
      [
        "state",
        "Documented buffer lifetimes and stable addresses or supported update rules."
      ]
    ],
    "output": "A capture key, replay implementation and eager fallback. The lab can compare identical decode shapes after warm-up and account separately for capture overhead and peak memory.",
    "work": "Activate when host launch gaps are material and the backend supports capture of the actual segment. Key captures on relevant shapes and state, invalidate stale addresses and rerun parity across cache hits, shape transitions and fallback.",
    "lane": "option"
  },
  {
    "id": "prefix_reuse",
    "agent": "Sequence cache engineer",
    "title": "Reuse matching prompt state",
    "cc": [
      "memory.reusable_sessions",
      "memory.sequence_kv"
    ],
    "needs": [
      [
        "state",
        "Passing append/release behavior for KV pages and sequence state."
      ],
      [
        "serving",
        "Request descriptors with token IDs and identities for the model, tokenizer and any state-changing options."
      ]
    ],
    "output": "A prefix index and shared-page lifetime rules. Scheduling consumes a reusable token count and a valid state handle. The lab measures saved prefill work and retained bytes under the deployment workload.",
    "work": "Activate for workloads with repeated compatible prefixes or continued sessions. Verify a branch from a partial page, concurrent siblings, eviction and an adapter mismatch. Compare cached continuation logits to fresh full prefill.",
    "lane": "option"
  },
  {
    "id": "pack_convert",
    "agent": "Weight format engineer",
    "title": "Convert and qualify a weight pack",
    "cc": [
      "weights.prepare_artifact",
      "weights.decode_blocks"
    ],
    "needs": [
      [
        "weights",
        "Revisioned tensor inventory with source layouts, scales and expected logical dimensions."
      ],
      [
        "contract",
        "Permitted representation changes, target formats and numerical error gates."
      ]
    ],
    "output": "A checksummed target pack plus decoded-block and tensor comparisons. The loader and kernel engineers can consume the qualified layout; the lab can assess logits and task-level effects of any precision change.",
    "work": "Activate when the source pack cannot feed a selected kernel or when a measured access bottleneck motivates a different layout. For lossless repacking check decoded equivalence, tails and scale order. For quantization compare to the original weights and report error rather than asserting lossless equivalence.",
    "lane": "option"
  },
  {
    "id": "dense_path",
    "agent": "Feed-forward operator engineer",
    "title": "Implement configured dense FFN layers",
    "cc": [
      "dense.feed_forward",
      "model.decoder_architecture"
    ],
    "needs": [
      [
        "contract",
        "Inspected checkpoint layer map identifying dense FFN layers and their activation rule."
      ],
      [
        "weights",
        "Validated bindings for the required gate, up and down projections or the model’s ungated equivalents."
      ]
    ],
    "output": "A dense FFN callable at the declared layer indices, with intermediate and final reference comparisons. Engine assembly receives the new branch only for the checkpoints that require it.",
    "work": "Activate when the actual checkpoint declares dense FFNs. Bind projections, biases and activation ordering; compare ragged prompt batches and single-token decode against an independent dense reference before approving a fused epilogue.",
    "lane": "option"
  }
];
