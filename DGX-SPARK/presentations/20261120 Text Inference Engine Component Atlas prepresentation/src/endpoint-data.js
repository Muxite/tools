// Canonical endpoint records and pinned source examples.
const endpointData = {
  "revision": "9048bad8d6e3a0f9f1726e238e451181c7e02613",
  "parents": [
    {
      "id": "service",
      "title": "Completion service",
      "summary": "Accept and stream client requests.",
      "children": [
        {
          "id": "gateway",
          "title": "Gateway and streaming",
          "legacyIds": [
            "serving.engine_image_gateway"
          ],
          "caller": "Client",
          "action": "Accept and stream a completion; propagate cancellation.",
          "acceptance": "Interleave two requests, cancel one, and verify the other finishes with its own output.",
          "source": {
            "path": "tools/server/server-queue.cpp",
            "symbol": "server_queue::post",
            "line": 28
          },
          "status": "source example",
          "builderIds": [
            "serving.build_engine_image_gateway"
          ]
        }
      ]
    },
    {
      "id": "runtime",
      "title": "Generation runtime",
      "summary": "Schedule and advance generation.",
      "children": [
        {
          "id": "orchestration",
          "title": "Request and batch orchestration",
          "legacyIds": [
            "scheduler.request_scheduler",
            "batch.batch_layout_builder",
            "decode.generation_loop"
          ],
          "caller": "Gateway",
          "action": "Schedule sequence rows, advance the model and release completed requests.",
          "acceptance": "Interleave unequal sequences and cancellation; compare positions and outputs to isolated runs.",
          "source": {
            "path": "tools/server/server-context.cpp",
            "symbol": "server_slot",
            "line": 150
          },
          "status": "source example",
          "builderIds": [
            "scheduler.build_request_scheduler",
            "batch.build_batch_layout_builder",
            "decode.build_generation_loop"
          ]
        },
        {
          "id": "speculation",
          "title": "Speculative decoding",
          "legacyIds": [
            "decode.speculative_decoder"
          ],
          "caller": "Generation loop",
          "action": "Propose and verify draft tokens when configured.",
          "acceptance": "Compare accepted output against target-only decoding with deterministic settings.",
          "source": {
            "path": "tools/server/server-context.cpp",
            "symbol": "common_speculative_get_output_limits",
            "line": 63
          },
          "status": "conditional",
          "builderIds": [
            "decode.build_speculative_decoder"
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "--dspark",
              "line": 2536,
              "note": "DSpark drafter: --dspark on|off|none|auto, --dspark-block, --dspark-conf."
            },
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "--dspark-depth",
              "line": 229,
              "note": "Maximum drafts per round."
            },
            {
              "path": "src/dsv41/ds4_model.cu",
              "symbol": "the DSpark blocks",
              "line": 586,
              "note": "Drafter blocks from an EXL3 pack or a GGUF drafter pack made from DeepSeek's checkpoint (tools/ds4/drafter_pack.py)."
            }
          ],
          "llamaStatus": "llama.cpp's server has a speculative path; Strata adds the DSpark drafter for DeepSeek V4.1."
        },
        {
          "id": "telemetry",
          "title": "Runtime event recording",
          "legacyIds": [
            "observability.runtime_event_recorder"
          ],
          "caller": "Engine operators",
          "action": "Collect correlated request and execution events.",
          "acceptance": "Trace two interleaved requests and verify identifiers and timing remain distinct.",
          "source": {
            "path": "tools/server/server-common.cpp",
            "symbol": "server_slot_stats::to_json",
            "line": 146
          },
          "status": "partial source example",
          "builderIds": [
            "observability.build_runtime_event_recorder"
          ]
        }
      ]
    },
    {
      "id": "tokens",
      "title": "Token processing and sampling",
      "summary": "Translate text and choose constrained output tokens.",
      "children": [
        {
          "id": "codec",
          "title": "Token and chat codec",
          "legacyIds": [
            "tokenizer.token_codec"
          ],
          "caller": "Gateway",
          "action": "Render and tokenize the prompt; decode output tokens.",
          "acceptance": "Compare exact prompt bytes, token IDs, and split UTF-8 output with an independent tokenizer.",
          "source": {
            "path": "include/llama.h",
            "symbol": "llama_tokenize",
            "line": 1305
          },
          "status": "source example",
          "builderIds": [
            "tokenizer.build_token_codec"
          ]
        },
        {
          "id": "sampling",
          "title": "Sampling and constraints",
          "legacyIds": [
            "sampling.token_sampler"
          ],
          "caller": "Generation loop",
          "action": "Select the next token from scores under configured rules.",
          "acceptance": "Compare a fixed score fixture and seed with an independent sampler; check grammar-invalid tokens are rejected.",
          "source": {
            "path": "src/llama-sampler.cpp",
            "symbol": "llama_sampler_sample",
            "line": 896
          },
          "status": "source example",
          "builderIds": [
            "sampling.build_token_sampler"
          ]
        }
      ]
    },
    {
      "id": "model",
      "title": "Model execution",
      "summary": "Execute architecture-specific decoder and expert operations.",
      "children": [
        {
          "id": "decoder",
          "title": "Embedding, layers and output",
          "legacyIds": [
            "model.token_embedding_layer",
            "model.decoder_stack",
            "model.vocabulary_projection_head"
          ],
          "caller": "Generation control",
          "action": "Build and execute the model graph to produce scores.",
          "acceptance": "Compare intermediate rows and logits to an independent model reference on a fixed pack.",
          "source": {
            "path": "src/models/muse-spark.cpp",
            "symbol": "llama_model_muse_spark::load_arch_hparams",
            "line": 3
          },
          "status": "source example",
          "builderIds": [
            "model.build_token_embedding_layer",
            "model.build_decoder_stack",
            "model.build_vocabulary_projection_head"
          ]
        },
        {
          "id": "attention",
          "title": "Attention operators",
          "legacyIds": [
            "attention.dense_attention_operator",
            "attention.sparse_attention_operator"
          ],
          "caller": "Decoder layers",
          "action": "Compute attention using the selected architecture and visible sequence state.",
          "acceptance": "Compare masked attention outputs with an independent small matrix fixture.",
          "source": {
            "path": "src/llama-graph.cpp",
            "symbol": "llm_graph_context::build_attn_mha",
            "line": 3009
          },
          "status": "variant-dependent",
          "builderIds": [
            "attention.build_dense_attention_operator",
            "attention.build_sparse_attention_operator"
          ]
        },
        {
          "id": "feedforward",
          "title": "Dense feed-forward",
          "legacyIds": [
            "dense.dense_feed_forward_block"
          ],
          "caller": "Decoder layers",
          "action": "Apply the configured dense feed-forward operation.",
          "acceptance": "Compare output rows against a separate scalar implementation.",
          "source": {
            "path": "src/llama-graph.cpp",
            "symbol": "llm_graph_context::build_ffn",
            "line": 1979
          },
          "status": "checkpoint-dependent",
          "builderIds": [
            "dense.build_dense_feed_forward_block"
          ]
        },
        {
          "id": "expert_router",
          "title": "Expert routing",
          "legacyIds": [
            "model.expert_router"
          ],
          "caller": "Decoder layers",
          "action": "Choose expert IDs and weights for each row.",
          "acceptance": "Compare selected expert IDs, paired weights, tie handling and normalization with an independent routing fixture.",
          "source": {
            "path": "src/llama-graph.cpp",
            "symbol": "llm_graph_context::build_moe_ffn",
            "line": 2252
          },
          "status": "source example",
          "builderIds": [
            "model.build_expert_router"
          ],
          "operatingCCs": [
            "analysis.expert_routing_profile"
          ]
        },
        {
          "id": "expert_row_dispatcher_and_combiner",
          "title": "Expert computation and combination",
          "legacyIds": [
            "merge.expert_row_dispatcher_and_combiner",
            "model.expert_feed_forward_block"
          ],
          "caller": "Decoder layers",
          "action": "Dispatch selected rows, run experts and combine contributions.",
          "acceptance": "With fixed expert selections, compare packed expert rows and weighted combined output with independent scalar arithmetic.",
          "source": {
            "path": "src/llama-graph.cpp",
            "symbol": "llm_graph_context::build_moe_ffn",
            "line": 2252
          },
          "status": "source example",
          "builderIds": [
            "merge.build_expert_row_dispatcher_and_combiner",
            "model.build_expert_feed_forward_block"
          ]
        },
        {
          "id": "adapters",
          "title": "Adapter binding",
          "legacyIds": [
            "weights.adapter_binder"
          ],
          "caller": "Model graph",
          "action": "Select and bind request-specific adapters.",
          "acceptance": "Interleave two adapters and compare each result with isolated execution.",
          "source": {
            "path": "src/llama-adapter.cpp",
            "symbol": "llama_adapter_lora::get_weight",
            "line": 140
          },
          "status": "conditional",
          "builderIds": [
            "weights.build_adapter_binder"
          ]
        }
      ]
    },
    {
      "id": "preparation",
      "title": "Model preparation and loading",
      "summary": "Prepare model artifacts and validate their loading.",
      "children": [
        {
          "id": "weight_pack_compiler",
          "title": "Quantization and pack conversion",
          "legacyIds": [
            "weights.weight_pack_compiler"
          ],
          "caller": "Offline model preparation operator",
          "action": "Convert an identified model to a declared packed format.",
          "acceptance": "Verify tensor identity, format metadata and independent decoded values in the output pack against the declared error budget.",
          "source": {
            "path": "src/llama-quant.cpp",
            "symbol": "llama_model_quantize",
            "line": 1498
          },
          "status": "source example",
          "builderIds": [
            "weights.build_weight_pack_compiler"
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_experts_rule.hpp",
              "symbol": "expert-profile.bin",
              "line": 53,
              "note": "Routing profile that can drive hotness-aware mixed precision and pack order."
            }
          ],
          "additionalSources": [
            {
              "path": "tools/quantize/quantize.cpp",
              "symbol": "--tensor-type",
              "line": 124,
              "note": "Per-tensor type overrides, the mechanism for mixed precision."
            }
          ],
          "localSources": [
            {
              "path": "evidence/pack-conversion/convert_ds41_upstream.py",
              "label": "convert_ds41_upstream.py",
              "note": "Precedent conversion: the DeepSeek V4.1 Flash IQ2_XXS pack used by Strata to upstream deepseek41 keys, weights copied byte for byte and read back."
            },
            {
              "path": "evidence/pack-conversion/conversion.log",
              "label": "conversion.log",
              "note": "Conversion receipt."
            }
          ],
          "contractNote": "Contract choice: hotness-aware mixed precision. A routing profile marks hot and cold experts; hot experts keep more bits and cold experts fewer, within the pack's accuracy budget.",
          "operatingCCs": [
            "tool.model_quantizer",
            "tool.pack_converter",
            "analysis.expert_routing_profile"
          ]
        },
        {
          "id": "checkpoint_reader",
          "title": "Checkpoint loader",
          "legacyIds": [
            "weights.checkpoint_reader"
          ],
          "caller": "Model initialization",
          "action": "Load and validate model tensor metadata and ranges.",
          "acceptance": "Compare tensor names and shapes to a known fixture and reject truncated model data.",
          "source": {
            "path": "src/llama.cpp",
            "symbol": "llama_model_load_from_file",
            "line": 459
          },
          "status": "source example",
          "builderIds": [
            "weights.build_checkpoint_reader"
          ]
        }
      ]
    },
    {
      "id": "sequence-state",
      "title": "Sequence state",
      "summary": "Maintain request-specific KV and recurrent state and optionally reuse compatible prefixes.",
      "children": [
        {
          "id": "sequence-memory",
          "title": "Sequence memory",
          "legacyIds": [
            "memory.sequence_kv_cache",
            "sequence.recurrent_state_operator"
          ],
          "caller": "Model graph",
          "action": "Append, read and release KV pages or recurrent state.",
          "acceptance": "Compare incremental decode with fresh prefill and verify released state cannot affect another request.",
          "source": {
            "path": "src/llama-kv-cache.h",
            "symbol": "llama_kv_cache",
            "line": 20
          },
          "status": "recurrent path conditional",
          "builderIds": [
            "memory.build_sequence_kv_cache",
            "sequence.build_recurrent_state_operator"
          ]
        },
        {
          "id": "prefix",
          "title": "Prefix reuse",
          "legacyIds": [
            "memory.prefix_state_cache"
          ],
          "caller": "Generation control",
          "action": "Find and retain compatible reusable prefix state.",
          "acceptance": "Compare resumed logits with fresh prefill and reject incompatible model or adapter identities.",
          "source": {
            "path": "tools/server/server-context.cpp",
            "symbol": "server_slot",
            "line": 150
          },
          "status": "optional; exact target interface unbound",
          "builderIds": [
            "memory.build_prefix_state_cache"
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "CONVERSATION SLOTS",
              "line": 545,
              "note": "ds4 conversation slots save and restore a conversation's state (STRATA_DS4_SLOT_KEEP)."
            },
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "restore point",
              "line": 19,
              "note": "Restore points inside a prompt (marks=, tail=) let a request with the same start resume there."
            },
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "STRATA_DS4_REUSE",
              "line": 563,
              "note": "STRATA_DS4_REUSE=0 turns all reuse off for A/B tests."
            }
          ],
          "llamaStatus": "llama.cpp's server reuses a slot's cached prompt; Strata adds conversation slots and restore points."
        }
      ]
    },
    {
      "id": "weight-residency",
      "title": "Weight residency",
      "summary": "Plan weight placement and make selected expert weights ready within the shared memory budget.",
      "children": [
        {
          "id": "weight_placement_planner",
          "title": "Weight placement planner",
          "legacyIds": [
            "placement.weight_placement_planner"
          ],
          "caller": "Model loader and deployment configuration",
          "action": "Plan resident and storage-backed assignments within the target memory budget.",
          "acceptance": "Reconcile the planned memory ledger with physical backing and peak measurement; reject an infeasible budget.",
          "source": {
            "path": "common/fit.cpp",
            "symbol": "common_params_fit_impl",
            "line": 264
          },
          "status": "partial source example; target budget policy unbound",
          "builderIds": [
            "placement.build_weight_placement_planner"
          ]
        },
        {
          "id": "expert_weight_cache",
          "title": "Expert weight cache",
          "legacyIds": [
            "engine.expert_weight_cache"
          ],
          "caller": "Model graph",
          "action": "Supply selected expert weights and protect slots through their last reader.",
          "acceptance": "Force duplicate misses and delayed completion; verify fetched bytes and output against resident execution and reject stale slot handles.",
          "source": {
            "path": "src/llama-moe-cache.cpp",
            "symbol": "llama_moe_cache::build_lookup",
            "line": 891
          },
          "status": "partial source example; storage-backed target design unbound",
          "builderIds": [
            "engine.build_expert_weight_cache"
          ],
          "operatingCCs": [
            "tool.moe_cache_size_tuner",
            "analysis.expert_copy_replay",
            "analysis.request_fault_io"
          ]
        },
        {
          "id": "prediction",
          "title": "Expert demand prediction",
          "legacyIds": [
            "routing.expert_demand_predictor"
          ],
          "caller": "Expert weight cache",
          "action": "Offer optional early hints without changing authoritative routing.",
          "acceptance": "On held-out traces report coverage, timely coverage and unused bytes against a no-prediction baseline.",
          "source": null,
          "status": "experimental; unbound to pinned runtime",
          "builderIds": [
            "routing.build_expert_demand_predictor"
          ]
        },
        {
          "id": "engram_row_cache",
          "title": "Engram row cache",
          "legacyIds": [
            "weights.engram_row_cache"
          ],
          "caller": "Generation loop and Engram decoder layers",
          "action": "Read the Engram table rows a token window needs ahead of use and keep recent rows in a bounded RAM cache.",
          "acceptance": "Compare cached rows and logits with direct table reads, including misses and eviction; check that the cache stays within budget.",
          "source": {
            "path": "src/llama-model-loader.h",
            "symbol": "struct lazy_read",
            "line": 87,
            "note": "On-demand row reads for per-layer token embeddings (--lazy-mode). No row cache."
          },
          "additionalSources": [
            {
              "path": "common/arg.cpp",
              "symbol": "--lazy-mode",
              "line": 2685,
              "note": "Option that enables on-demand reads."
            }
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_engram_io.hpp",
              "symbol": "EgRowCache",
              "line": 40,
              "note": "Engram rows read off the decode critical path, with a row cache."
            },
            {
              "path": "src/dsv41/ds4_model.cu",
              "symbol": "DS4_ENGRAM_CACHE_MB",
              "line": 3419,
              "note": "Row cache size (0 disables it)."
            },
            {
              "path": "src/dsv41/ds4_model.cu",
              "symbol": "DS4_ENGRAM_THREADS",
              "line": 3416,
              "note": "Read threads (two by default)."
            }
          ],
          "llamaStatus": "llama.cpp reads Engram rows on demand (--lazy-mode, lazy_read) and has no row cache; repeated rows rely on the OS page cache.",
          "status": "conditional; not in llama.cpp",
          "builderIds": [
            "weights.build_engram_row_cache"
          ]
        },
        {
          "id": "host_expert_store",
          "title": "Expert store and admission policy (host expert tier)",
          "legacyIds": [
            "engine.host_expert_store"
          ],
          "caller": "Expert weight cache and CPU expert lane",
          "action": "Keep a RAM tier of whole experts filled by unbuffered reads, admit and evict them under a policy, and seed the tier in profile order.",
          "acceptance": "Replay a routing trace per policy under a small budget; compare bytes with the file and check that pinned slots are never evicted.",
          "source": {
            "path": "src/llama-mmap.cpp",
            "symbol": "llama_mmap::impl",
            "line": 708,
            "note": "The pack is memory-mapped; host-resident experts live in the OS page cache."
          },
          "strataSources": [
            {
              "path": "src/dsv41/ds4_store.hpp",
              "symbol": "ExpertStore",
              "line": 38,
              "note": "RAM tier of whole experts with unbuffered reads and a replacement policy."
            },
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "--ssd-cache",
              "line": 2529,
              "note": "RAM tier size in GB."
            },
            {
              "path": "src/dsv41/ds4_main.cpp",
              "symbol": "--ssd-policy",
              "line": 2530,
              "note": "Policy: lru, lfu or lfulru."
            },
            {
              "path": "src/dsv41/ds4_model.cu",
              "symbol": "tensors.txt",
              "line": 401,
              "note": "Pack tensor order, which a profile-ordered pack sets."
            },
            {
              "path": "src/dsv41/ds4_experts_rule.hpp",
              "symbol": "expert-profile.bin",
              "line": 53,
              "note": "Routing counts per layer used to seed and order experts."
            }
          ],
          "llamaStatus": "No engine-owned host tier: llama.cpp relies on mmap and the OS page cache.",
          "status": "conditional; not in llama.cpp",
          "builderIds": [
            "engine.build_host_expert_store"
          ],
          "operatingCCs": [
            "analysis.page_residency"
          ]
        }
      ]
    },
    {
      "id": "backend",
      "title": "Tensor execution backend",
      "summary": "Allocate buffers, decode packed blocks and run kernels.",
      "children": [
        {
          "id": "execute",
          "title": "Kernel, memory and graph execution",
          "legacyIds": [
            "backend.kernel_dispatcher",
            "memory.workspace_allocator",
            "graph.execution_graph_backend"
          ],
          "caller": "Model graph",
          "action": "Select kernels, allocate buffers and execute compatible graphs.",
          "acceptance": "Compare device output to an independent reference; force an unsupported shape and delayed buffer reader.",
          "source": {
            "path": "ggml/src/ggml-backend.cpp",
            "symbol": "ggml_backend_sched_graph_compute",
            "line": 2469
          },
          "status": "source example",
          "builderIds": [
            "backend.build_kernel_dispatcher",
            "memory.build_workspace_allocator",
            "graph.build_execution_graph_backend"
          ]
        },
        {
          "id": "distributed",
          "title": "Distributed execution",
          "legacyIds": [
            "parallel.distributed_execution_coordinator",
            "parallel.distributed_expert_exchange"
          ],
          "caller": "Model graph",
          "action": "Coordinate work and expert rows across devices when configured.",
          "acceptance": "Compare multi-device outputs with a single-device reference and inject a failed peer.",
          "source": {
            "path": "ggml/src/ggml-backend.cpp",
            "symbol": "ggml_backend_sched_graph_compute",
            "line": 2469
          },
          "status": "conditional; expert exchange unbound",
          "builderIds": [
            "parallel.build_distributed_execution_coordinator",
            "parallel.build_distributed_expert_exchange"
          ]
        },
        {
          "id": "weight_block_decoder",
          "title": "Runtime packed-weight decoder",
          "legacyIds": [
            "weights.weight_block_decoder"
          ],
          "caller": "Tensor execution backend",
          "action": "Interpret or repack supported weight blocks for execution.",
          "acceptance": "Compare signed extrema, scales and decoded Q4 blocks to an independent decoder.",
          "source": {
            "path": "ggml/src/ggml-quants.c",
            "symbol": "dequantize_row_q4_0",
            "line": 462
          },
          "status": "format-specific source example",
          "builderIds": [
            "weights.build_weight_block_decoder"
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_q6k.cuh",
              "symbol": "Q6_K superblock",
              "line": 3,
              "note": "One value of a ggml Q6_K superblock, as dequantize_row_q6_K computes it."
            },
            {
              "path": "src/dsv41/ds4_iq1m_codes.inc",
              "symbol": "iq1s_grid_gpu",
              "line": 1,
              "note": "IQ1_M and IQ1_S code table generated from ggml's grid."
            }
          ],
          "operatingCCs": [
            "analysis.quant_kernel_profile"
          ]
        },
        {
          "id": "quantized_matmul",
          "title": "Quantized matmul kernels",
          "legacyIds": [
            "backend.quantized_matmul_kernel"
          ],
          "caller": "Kernel dispatcher",
          "action": "Multiply activations by packed low-bit weights on the GPU: matrix-vector kernels for decode, tiled kernels for prefill and expert-grouped launches for MoE.",
          "acceptance": "Compare each format with a dequantize-then-FP64 reference at block, tile and expert-group boundaries; force the dequantize fallback.",
          "source": {
            "path": "ggml/src/ggml-cuda/mmvq.cu",
            "symbol": "ggml_cuda_mul_mat_vec_q",
            "line": 1460,
            "note": "Decode: quantized matrix-vector product."
          },
          "additionalSources": [
            {
              "path": "ggml/src/ggml-cuda/mmq.cu",
              "symbol": "ggml_cuda_mul_mat_q",
              "line": 164,
              "note": "Prefill: tiled quantized matmul."
            },
            {
              "path": "ggml/src/ggml-cuda/mmq.cu",
              "symbol": "ggml_cuda_should_use_mmq",
              "line": 395,
              "note": "Chooses the tiled path by type, architecture, batch size and expert count."
            },
            {
              "path": "ggml/src/ggml-cuda/mmq-config-blackwell.cuh",
              "symbol": "ggml_cuda_mmq_get_config_blackwell",
              "line": 1,
              "note": "Tile configuration for Blackwell (GB10)."
            },
            {
              "path": "ggml/src/ggml-cuda/vecdotq.cuh",
              "symbol": "vec_dot_iq2_xxs_q8_1",
              "line": 1111,
              "note": "IQ2_XXS block dot product."
            },
            {
              "path": "ggml/src/ggml-cuda/mmid.cu",
              "symbol": "ggml_cuda_launch_mm_ids_helper",
              "line": 166,
              "note": "MoE: rows grouped by selected expert ID."
            },
            {
              "path": "ggml/src/ggml-cuda/convert.cu",
              "symbol": "ggml_get_to_fp16_cuda",
              "line": 555,
              "note": "Dequantize fallback."
            }
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_iq.cu",
              "symbol": "block_iq2_xxs",
              "line": 62,
              "note": "GPU IQ kernels for low-bit routed experts; the IQ2_XXS block is 66 bytes."
            },
            {
              "path": "src/dsv41/ds4_tq.cu",
              "symbol": "TQK6",
              "line": 1,
              "note": "GPU kernels for trellis-quantized routed experts."
            },
            {
              "path": "src/dsv41/ds4_gguf.cu",
              "symbol": "BF16 matrices and MXFP4 experts",
              "line": 3,
              "note": "GPU path for a GGUF's BF16 matrices and MXFP4 experts."
            }
          ],
          "llamaStatus": "Present at the pin for ggml block formats including IQ2_XXS: mmvq for decode, mmq with a Blackwell tile configuration for prefill, mmid for MoE grouping.",
          "status": "source example",
          "builderIds": [
            "backend.build_quantized_matmul_kernel"
          ],
          "operatingCCs": [
            "analysis.quant_kernel_profile"
          ]
        },
        {
          "id": "cpu_expert_lane",
          "title": "CPU expert lane kernels and weight repack",
          "legacyIds": [
            "backend.cpu_weight_repack"
          ],
          "caller": "Kernel dispatcher, for experts placed on the CPU",
          "action": "Compute host-resident experts on the CPU and repack eligible formats into interleaved blocks at load.",
          "acceptance": "Compare CPU-lane outputs with a scalar reference per format, with repack on and off; confirm that formats without a repack path keep the plain layout.",
          "source": {
            "path": "ggml/src/ggml-cpu/arch/arm/quants.c",
            "symbol": "ggml_vec_dot_iq2_xxs_q8_K",
            "line": 3634,
            "note": "ARM IQ2_XXS dot product used by the CPU expert lane."
          },
          "additionalSources": [
            {
              "path": "ggml/src/ggml-cpu/repack.cpp",
              "symbol": "ggml_repack_get_optimal_repack_type",
              "line": 4930,
              "note": "Repack eligibility. No IQ2_XXS repack path exists at this pin."
            }
          ],
          "strataSources": [
            {
              "path": "src/dsv41/ds4_iq_cpu.cpp",
              "symbol": "native",
              "line": 52,
              "note": "CPU lane for a GGUF's low-bit experts."
            },
            {
              "path": "src/dsv41/ds4_mx_kern.inc",
              "symbol": "mx_rows",
              "line": 3,
              "note": "CPU lane int8 MXFP4 rows for the x86 tiers."
            }
          ],
          "llamaStatus": "CPU dot products exist for IQ2_XXS; repack.cpp has no IQ2_XXS repack path, so those experts keep the plain layout.",
          "status": "conditional; IQ2_XXS repack absent",
          "builderIds": [
            "backend.build_cpu_weight_repack"
          ],
          "operatingCCs": [
            "analysis.quant_kernel_profile"
          ]
        }
      ]
    }
  ],
  "boundaries": [
    {
      "id": "api",
      "title": "Public API",
      "status": "source-backed interface",
      "source": {
        "path": "include/llama.h",
        "symbol": "llama_decode",
        "line": 1005
      },
      "detail": "Context, token, model and batch entry points; the server is one caller.",
      "caller": "Embedding application or completion service",
      "implementingCCs": [
        "serving.build_engine_image_gateway"
      ],
      "collaboratingCCs": [
        "decode.build_generation_loop"
      ],
      "acceptance": "Call the public interface on a fixed prompt and compare output and error behavior with an independent client fixture."
    },
    {
      "id": "server",
      "title": "Server, streaming and cancellation",
      "status": "source-backed",
      "source": {
        "path": "tools/server/server-queue.cpp",
        "symbol": "server_queue::post",
        "line": 28
      },
      "detail": "HTTP, tasks, slot scheduling and cancellation are server responsibilities."
    },
    {
      "id": "grammar",
      "title": "Grammar and constrained sampling",
      "status": "source-backed",
      "source": {
        "path": "src/llama-sampler.cpp",
        "symbol": "llama_sampler_init_grammar",
        "line": 2809
      },
      "detail": "Constraints complement token selection and chat/schema handling."
    },
    {
      "id": "factory",
      "title": "Software factory",
      "status": "proposed organizational capability",
      "source": null,
      "detail": "Contract, orchestration, integration, image and qualification workers are not llama.cpp runtime modules."
    },
    {
      "id": "host",
      "title": "Host platform",
      "status": "external provider",
      "source": null,
      "detail": "Compute, memory and storage provide services outside the engine."
    },
    {
      "id": "multimodal",
      "title": "Multimodal and auxiliary tools",
      "status": "outside text target",
      "source": {
        "path": "tools/mtmd/CMakeLists.txt",
        "symbol": "add_library(mtmd",
        "line": 38
      },
      "detail": "The repository also contains multimodal, conversion, benchmark and example tools."
    },
    {
      "id": "build-test",
      "title": "Build and tests",
      "status": "source-backed",
      "source": {
        "path": "tests/test-backend-ops.cpp",
        "symbol": "main",
        "line": 14685
      },
      "detail": "Build, backend tests and server tests are engineering evidence, not inference components.",
      "caller": "Release workflow and qualification lab",
      "implementingCCs": [
        "factory.image_builder",
        "factory.qualification_lab"
      ],
      "collaboratingCCs": [
        "factory.source_integration_workbench"
      ],
      "acceptance": "Rebuild an identified revision with pinned dependencies and run backend and server tests, retaining the result receipt."
    },
    {
      "id": "audit-conversion",
      "title": "Conversion and GGUF",
      "status": "Scoped source-family audit",
      "source": {
        "path": "ggml/src/gguf.cpp",
        "symbol": "gguf_init_from_file",
        "line": 1017
      },
      "caller": "Offline model preparation and model initialization",
      "implementingCCs": [
        "weights.build_weight_pack_compiler",
        "weights.build_checkpoint_reader"
      ],
      "collaboratingCCs": [
        "weights.build_weight_block_decoder"
      ],
      "reviewedPaths": [
        "conversion/muse_spark.py",
        "convert_hf_to_gguf.py",
        "ggml/src/gguf.cpp",
        "gguf-py"
      ],
      "detail": "Conversion produces model artifacts; GGUF supplies format metadata and tensor storage. Reviewed paths are representative, not a file-by-file proof.",
      "acceptance": "Compare tensor identity, shapes and independently decoded blocks with source data; reject malformed or truncated packs.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-loader",
      "title": "Loader, architecture and adapters",
      "status": "Scoped source-family audit",
      "source": {
        "path": "src/models/muse-spark.cpp",
        "symbol": "llama_model_muse_spark::build_arch_graph",
        "line": 223
      },
      "caller": "Model initialization and graph construction",
      "implementingCCs": [
        "weights.build_checkpoint_reader",
        "model.build_decoder_stack"
      ],
      "collaboratingCCs": [
        "weights.build_adapter_binder",
        "weights.build_weight_pack_compiler"
      ],
      "reviewedPaths": [
        "src/llama-model-loader.cpp",
        "src/models/muse-spark.cpp",
        "src/llama-adapter.cpp",
        "conversion/muse_spark.py"
      ],
      "detail": "Loader binds model data; architecture builds the graph; adapter logic applies optional model changes. Muse conversion registration and graph exist in the pinned source; target pack qualification is open.",
      "acceptance": "Compare intermediate rows and logits with an independent reference; isolate interleaved adapter requests.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-context",
      "title": "Public context and batch",
      "status": "Scoped source-family audit",
      "source": {
        "path": "src/llama-context.cpp",
        "symbol": "llama_context::decode",
        "line": 2140
      },
      "caller": "Application or server",
      "implementingCCs": [
        "decode.build_generation_loop",
        "batch.build_batch_layout_builder"
      ],
      "collaboratingCCs": [
        "serving.build_engine_image_gateway",
        "memory.build_sequence_kv_cache"
      ],
      "reviewedPaths": [
        "include/llama.h",
        "src/llama-context.cpp",
        "src/llama-batch.cpp"
      ],
      "detail": "Public APIs and context coordinate model evaluation and batch rows; the server is one caller.",
      "acceptance": "Run a fixed prompt through the public interface and verify batch positions and independent outputs.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-server",
      "title": "Server HTTP, slots and cancellation",
      "status": "Scoped source-family audit",
      "source": {
        "path": "tools/server/server-queue.cpp",
        "symbol": "server_response_reader::stop",
        "line": 608
      },
      "caller": "HTTP client",
      "implementingCCs": [
        "serving.build_engine_image_gateway",
        "scheduler.build_request_scheduler"
      ],
      "collaboratingCCs": [
        "decode.build_generation_loop",
        "memory.build_sequence_kv_cache"
      ],
      "reviewedPaths": [
        "tools/server/server-http.cpp",
        "tools/server/server-slot-sched.cpp",
        "tools/server/server-context.cpp",
        "tools/server/server-queue.cpp"
      ],
      "detail": "HTTP, scheduling and cancellation are server responsibilities; their existence does not prove the proposed engine contract is integrated.",
      "acceptance": "Cancel one interleaved stream and verify the other completes with correct output and state release.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-tokens",
      "title": "Token processing and grammar",
      "status": "Scoped source-family audit",
      "source": {
        "path": "src/llama-sampler.cpp",
        "symbol": "llama_sampler_init_grammar",
        "line": 2809
      },
      "caller": "Generation runtime",
      "implementingCCs": [
        "tokenizer.build_token_codec",
        "sampling.build_token_sampler"
      ],
      "collaboratingCCs": [
        "decode.build_generation_loop",
        "serving.build_engine_image_gateway"
      ],
      "reviewedPaths": [
        "src/llama-vocab.cpp",
        "src/llama-sampler.cpp",
        "src/llama-grammar.cpp",
        "common/chat.cpp"
      ],
      "detail": "Vocabulary, prompt formatting, sampling and constrained decoding have distinct responsibilities.",
      "acceptance": "Compare exact token IDs and grammar-constrained choices against independent fixtures.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-graph",
      "title": "Graph and GGML backend",
      "status": "Scoped source-family audit",
      "source": {
        "path": "ggml/src/ggml-cuda/ggml-cuda.cu",
        "symbol": "ggml_cuda_compute_forward",
        "line": 2726
      },
      "caller": "Model execution",
      "implementingCCs": [
        "backend.build_kernel_dispatcher",
        "graph.build_execution_graph_backend"
      ],
      "collaboratingCCs": [
        "memory.build_workspace_allocator",
        "model.build_decoder_stack"
      ],
      "reviewedPaths": [
        "src/llama-graph.cpp",
        "ggml/src/ggml-backend.cpp",
        "ggml/src/ggml-cuda/ggml-cuda.cu",
        "ggml/src/ggml-quants.c"
      ],
      "detail": "Graph construction, dispatch, backend kernels and packed-value decoding are related but separate; CUDA is one backend example.",
      "acceptance": "Compare kernel and decoded outputs with independent references across supported boundary shapes and formats.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "audit-memory",
      "title": "Sequence state and weight residency",
      "status": "Scoped source-family audit",
      "source": {
        "path": "src/llama-moe-cache.cpp",
        "symbol": "llama_moe_cache::build_lookup",
        "line": 891
      },
      "caller": "Model execution and generation runtime",
      "implementingCCs": [
        "memory.build_sequence_kv_cache",
        "engine.build_expert_weight_cache",
        "placement.build_weight_placement_planner"
      ],
      "collaboratingCCs": [
        "routing.build_expert_demand_predictor",
        "memory.build_prefix_state_cache"
      ],
      "reviewedPaths": [
        "src/llama-kv-cache.cpp",
        "src/llama-memory-recurrent.cpp",
        "src/llama-moe-cache.cpp",
        "common/fit.cpp"
      ],
      "detail": "Sequence state owns KV and recurrent lifetimes; weight residency owns placement, expert slots and optional predictions. They share a bounded memory budget with backend workspace. The source cache demonstrates device residency, not the proposed storage-backed path; prediction remains unbound.",
      "acceptance": "Reconcile live KV, resident weights, cache slots, workspace and transient transfers against the shared limit and measured peak; reject infeasible admission. Compare resumed logits with fresh prefill; force a cache miss and delayed reader; evaluate predictor coverage, timeliness and unused bytes on held-out traces.",
      "integrationStatus": "Predictor and storage-backed cache integration are unbound.",
      "qualificationStatus": "No target endpoint or speed qualification established."
    },
    {
      "id": "audit-build",
      "title": "Build and server tests",
      "status": "Scoped source-family audit",
      "source": {
        "path": "tests/test-backend-ops.cpp",
        "symbol": "main",
        "line": 14685
      },
      "caller": "Release workflow and qualification lab",
      "implementingCCs": [
        "factory.image_builder",
        "factory.qualification_lab"
      ],
      "collaboratingCCs": [
        "factory.source_integration_workbench"
      ],
      "reviewedPaths": [
        "CMakeLists.txt",
        "tests/test-backend-ops.cpp",
        "tools/server/CMakeLists.txt",
        "tools/server/tests/unit/test_completion.py"
      ],
      "detail": "Build targets and tests provide engineering evidence; they do not by themselves establish a target-machine qualification.",
      "acceptance": "Build the identified revision with pinned dependencies, run relevant backend and server tests, and retain receipts.",
      "integrationStatus": "Proposed CC mapping; integrated implementation not established.",
      "qualificationStatus": "Target endpoint qualification open."
    },
    {
      "id": "shared-memory-contract",
      "title": "Shared memory budget contract",
      "status": "Proposed cross-component contract",
      "source": {
        "path": "common/fit.cpp",
        "symbol": "common_params_fit_impl",
        "line": 264
      },
      "caller": "Admission and model placement",
      "implementingCCs": [
        "placement.build_weight_placement_planner",
        "memory.build_sequence_kv_cache",
        "engine.build_expert_weight_cache",
        "memory.build_workspace_allocator"
      ],
      "collaboratingCCs": [
        "scheduler.build_request_scheduler",
        "memory.build_prefix_state_cache"
      ],
      "reviewedPaths": [
        "common/fit.cpp",
        "src/llama-kv-cache.cpp",
        "src/llama-moe-cache.cpp",
        "ggml/src/ggml-alloc.c"
      ],
      "detail": "Weight residency plans slots and staging alongside live sequence state and backend workspace. The components account for physical backing and agree on admission limits; a shared budget does not merge their ownership or lifetimes.",
      "acceptance": "Reconcile a byte ledger for live KV and recurrent state, resident weights, expert slots, workspace and transient transfers with physical backing and measured peak. Exercise simultaneous growth and delayed readers; reject a workload that cannot fit without invalidating live state.",
      "integrationStatus": "Proposed target contract; integration not established by source examples.",
      "qualificationStatus": "Target-machine budget and peak-memory qualification open."
    }
  ],
  "scenarios": [
    {
      "id": "quantization",
      "title": "New quantization format",
      "owner": "preparation",
      "collaborators": [
        "backend",
        "model"
      ],
      "inputs": "Source tensors, format specification and error budget",
      "output": "Identified packed model",
      "acceptance": "Independently decode blocks and compare projection outputs and model quality against declared tolerances. Profile the share of TTFT and decode spent in quantized matmul and dequantization on GPU and CPU before and after.",
      "source": {
        "path": "src/llama-quant.cpp",
        "symbol": "llama_model_quantize",
        "line": 1498
      },
      "implementingCCs": [
        "weights.build_weight_pack_compiler"
      ],
      "collaboratingCCs": [
        "weights.build_weight_block_decoder",
        "weights.build_checkpoint_reader",
        "backend.build_kernel_dispatcher",
        "backend.build_quantized_matmul_kernel",
        "backend.build_cpu_weight_repack"
      ],
      "operatingCCs": [
        "tool.model_quantizer",
        "tool.pack_converter",
        "analysis.quant_kernel_profile",
        "analysis.expert_routing_profile"
      ]
    },
    {
      "id": "architecture",
      "title": "New model architecture",
      "owner": "model",
      "collaborators": [
        "preparation",
        "sequence-state",
        "weight-residency",
        "backend"
      ],
      "inputs": "Architecture specification, tokenizer and tensors",
      "output": "Loadable model and executable graph",
      "acceptance": "Compare independent intermediate rows and logits; model pack qualification remains open.",
      "source": {
        "path": "src/models/muse-spark.cpp",
        "symbol": "llama_model_muse_spark::build_arch_graph",
        "line": 223
      },
      "additionalSources": [
        {
          "path": "conversion/muse_spark.py",
          "symbol": "MuseSparkForConditionalGeneration",
          "line": 37
        }
      ],
      "implementingCCs": [
        "model.build_decoder_stack"
      ],
      "collaboratingCCs": [
        "weights.build_checkpoint_reader",
        "attention.build_dense_attention_operator",
        "backend.build_kernel_dispatcher"
      ]
    },
    {
      "id": "routing",
      "title": "Routing-rule change",
      "owner": "model",
      "collaborators": [
        "weight-residency",
        "backend"
      ],
      "inputs": "Scores, routing rule and expert count",
      "output": "Paired expert IDs and weights",
      "acceptance": "Check ties, normalization and weighted output against independent arithmetic fixtures.",
      "source": {
        "path": "src/llama-graph.cpp",
        "symbol": "llm_graph_context::build_moe_ffn",
        "line": 2252
      },
      "implementingCCs": [
        "model.build_expert_router"
      ],
      "collaboratingCCs": [
        "merge.build_expert_row_dispatcher_and_combiner",
        "model.build_expert_feed_forward_block",
        "engine.build_expert_weight_cache"
      ]
    },
    {
      "id": "kernel",
      "title": "Kernel substitution",
      "owner": "backend",
      "collaborators": [
        "model",
        "sequence-state",
        "weight-residency"
      ],
      "inputs": "Supported shapes, types and layouts",
      "output": "Selected backend execution",
      "acceptance": "Compare boundary shapes with an independent reference and exercise fallback.",
      "source": {
        "path": "ggml/src/ggml-cuda/ggml-cuda.cu",
        "symbol": "ggml_cuda_compute_forward",
        "line": 2726
      },
      "implementingCCs": [
        "backend.build_kernel_dispatcher"
      ],
      "collaboratingCCs": [
        "memory.build_workspace_allocator",
        "graph.build_execution_graph_backend"
      ]
    },
    {
      "id": "kv",
      "title": "KV policy change",
      "owner": "sequence-state",
      "collaborators": [
        "runtime",
        "model"
      ],
      "inputs": "Sequence positions and allocation policy",
      "output": "Valid per-sequence state",
      "acceptance": "Compare incremental logits with fresh prefill and test release with interleaved requests.",
      "source": {
        "path": "src/llama-kv-cache.cpp",
        "symbol": "llama_kv_cache::find_slot",
        "line": 938
      },
      "implementingCCs": [
        "memory.build_sequence_kv_cache"
      ],
      "collaboratingCCs": [
        "scheduler.build_request_scheduler",
        "attention.build_dense_attention_operator"
      ]
    },
    {
      "id": "grammar",
      "title": "Constrained decoding",
      "owner": "tokens",
      "collaborators": [
        "runtime",
        "service"
      ],
      "inputs": "Grammar, scores and sequence state",
      "output": "Valid selected tokens",
      "acceptance": "Exercise valid and invalid continuations and compare to an independent grammar fixture.",
      "source": {
        "path": "src/llama-sampler.cpp",
        "symbol": "llama_sampler_init_grammar",
        "line": 2809
      },
      "implementingCCs": [
        "sampling.build_token_sampler"
      ],
      "collaboratingCCs": [
        "decode.build_generation_loop",
        "serving.build_engine_image_gateway"
      ]
    },
    {
      "id": "cancellation",
      "title": "Streaming cancellation",
      "owner": "service",
      "collaborators": [
        "runtime",
        "sequence-state"
      ],
      "inputs": "Active stream and cancellation signal",
      "output": "Terminal stream and released state",
      "acceptance": "Cancel one interleaved request; another completes with identical tokens and no leaked state.",
      "source": {
        "path": "tools/server/server-queue.cpp",
        "symbol": "server_response_reader::stop",
        "line": 608
      },
      "implementingCCs": [
        "serving.build_engine_image_gateway"
      ],
      "collaboratingCCs": [
        "scheduler.build_request_scheduler",
        "memory.build_sequence_kv_cache"
      ]
    }
  ],
  "strataRevision": "ffa80d73133ea5c548aefe57889a16e8085a938f"
};
