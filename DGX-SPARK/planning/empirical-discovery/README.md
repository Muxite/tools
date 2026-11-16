---
id: inference-factory-empirical-discovery-20261109
status: current-user-focus-research-and-coder-handoff
source: Sources/Prompts/2026-11-09-inference-factory-primary-objective.txt; Sources/Prompts/2026-11-09-inference-factory-workflow-clarifications.txt; Sources/Prompts/2026-11-09-continue-strata-research.txt
last_reviewed: 2026-11-10
next_action: Use real inference-improvement experiments to determine Manager responsibilities and initial CC portfolio; keep evidence and notes current
---


**Current focus — November 10:** [[Designs/Inference Factory - Empirical Discovery/Muse Spark procedures and CC handbook|Muse Spark Open on DGX Spark 128 GB: procedures and CC portfolio]]. Muse/Spark is the primary engine target; RTX/Jetson campaigns supply supporting evidence and reusable tools, not target qualification. The illustrated handbook uses named capability cards, six diagrams and multi-CC node toolkits; it maps 11 procedures to 12 tool candidates, four component families, Field Guide methodology and a conditional Specialist agent role. One useful CC remains sufficient for Friday.

# Current focus: discover the factory through inference improvement

**Jetson closeout now received:** [[Designs/Inference Factory - Empirical Discovery/Jetson closeout and CC implications|Per-type graph dispatch and portable-tool implications]]. Saved Orin results recompute to +23.64% Q4_K, +19.21% BF16 and −6.21% Q8; target qualification stays local. One useful CC remains sufficient for Friday.


**Latest Friday scope — one useful CC:** [[Designs/Inference Factory - Empirical Discovery/One useful CC demo|One tool OR one component is sufficient]]. Build/agent/Manager/mock-lab integration is optional enrichment. Prioritize concrete, reliable contracts and verifiable outputs; the full recovery pipeline is not a required demo.


**November 10 evidence update:** [[Designs/Inference Factory - Empirical Discovery/X86 closeout and Friday demo|X86 closeout inspected and preserved]]. Saved Granite Q8 reuse arithmetic supports +2.17% within its measured scope; this supersedes the earlier no-engine-win snapshot. Larger Qwen gains are upstream runtime trade-offs. Build/component/test demo proposed; live rehearsal and real lab-agent exchange remain unqualified.


**The main goal is to determine the Lab Manager design and every initially needed CC by doing real inference-engine improvement work.** Pursue a measured improvement on an existing model, explore the applicable body of methods, and retain the actual operations, tests, failures, decisions and artifacts that reveal which tools, methodologies and components matter. Friday's workshop shows a few proven capabilities selected from that campaign; it is not the campaign's scope or completion criterion.

This is the current interpretation of the user's [[Sources/Prompts/2026-11-09-inference-factory-primary-objective.txt|explicit focus]], [[Sources/Prompts/2026-11-09-inference-factory-workflow-clarifications.txt|boundary clarifications]] and [[Sources/Prompts/2026-11-09-continue-strata-research.txt|ongoing research/maintenance request]]. It does not redefine M1's authoritative PRD or claim operational deployment.

## Non-negotiable boundaries

- **Coding sandbox:** coding agents edit/instrument source and build images here, on the development machine. Its temporary implementation is not the final lab format.
- **Engine image:** the runnable inference engine is the product sent to our lab. It keeps its native launch interface; it is not a whole-engine CC wrapper.
- **Test sandbox:** separate from the coding sandbox; tests execute here. The other team owns the lab agent and sandbox choice/provisioning, which can be agent-operated from declared requirements.
- **Lab Manager:** our design responsibility is asynchronous coordination, job/attempt identity, admission, observation, cancellation/recovery and durable evidence registration, learned through experiments. This is distinct from another team's reasoning/provisioning lab agent.
- **Failure boundary:** the test sandbox may crash. Test control and durable acknowledged logs/traces/artifacts must remain outside it. Retain explicit partial coverage and loss intervals for data still buffered at crash; do not claim impossible recovery of unflushed GPU/process state.
- **Recording:** all work, tests and major operations need durable capture, including unsuccessful/blocked/unknown results, plus links from observations to Manager/CC design decisions.

## Portfolio to determine

| Family | Desired outcome; form still learned from work |
|---|---|
| Build CC | Required initial reusable image-building capability with identified source/component inputs, engine image outputs and build evidence |
| Profiling/test CCs | Small cohesive set for real quality/state, unprofiled measurements, bounded diagnostic capture and saved-report interpretation |
| Tool CCs | Independently useful engineering operations discovered through actual friction/reuse, often thin wrappers around existing software |
| Methodology CCs | Reusable agent instructions, experimental procedures, templates or composed workflows with worked/failed cases |
| Component CCs | Reusable engine assets plus integration guidance and tests; possibly snippets, modules, classes/functions, kernels, libraries or binaries |

The taxonomy is user-directed; exact package counts, names, algorithms and component boundaries are not predetermined. Do not wrap every command as a capsule or wait for full packaging before doing experiments. Do not end with a speculative catalog alone. Investigate real incorporation of valuable component candidates, with ABI/data/state/dependency requirements and actual consumer build/test evidence.

## Supporting campaign context (November 9–10 history)

**Two-machine extension:** [[Designs/Inference Factory - Empirical Discovery/Two-machine campaign]] records the new Ryzen7/RTX5070Ti and Jetson Orin Nano 8 GB task split, Opus/Sonnet/Haiku/Codex organization and the user-relayed unfinished x86 snapshot. It remains the historical campaign machine/coordination route; the central empirical-discovery objective remains unchanged.

The supporting x86 campaign model is `ibm-granite/granite-3.1-1b-a400m-instruct` on an Ubuntu 24.04 Docker host with RTX5070Ti and 48 GB RAM. Existing containers remain undisturbed; the owner promises exclusive GPU use during tests, not exclusive CPU/storage. Verify actual capacity, checkpoint, precision, tokenizer and environment. A separate agent is running the Granite/Strata campaign: coordinate current state and task ownership rather than duplicate it.

Strata at `ffa80d73133ea5c548aefe57889a16e8085a938f` is a reference system to reverse-engineer, not an assumed Granite backend. A small fully resident MoE does not automatically exercise large-model offloading. Distinguish real inference, focused component fixtures, trace replay and source-derived hypotheses. Survey methods broadly, then select informative experiments from profile/source evidence; do not blindly exhaust all knobs or prescribe an engine architecture.

Measure quality and matched execution outcomes under a declared policy; distinguish engine changes, representation changes and changed workloads. Seek a real gain and continue after infrastructure works. If no gain is supported within budget, retain the failures and next discriminating experiment; never manufacture a win.

## Research and handoff

- [[Designs/Inference Factory - Empirical Discovery/Strata findings|New Strata findings and actual CPU-only evidence]].
- [Current shared two-machine prompt](../../../research/lab-manager-reuse-20261109/two-machine/ORCHESTRATOR-PROMPT.md): complete mission, machine assignments, reported campaign state, agent organization, references and illustrative exchange records; send to both Opus leads.
- [Earlier single-file research handoff](../../../research/lab-manager-reuse-20261109/AGENT-HANDOFF.md): detailed source findings retained as background; current machine allocation is in the newer prompt.
- [Research package start](../../../research/lab-manager-reuse-20261109/README.md): source snapshots, 27 software dossiers, 13 papers and validation receipts.
- [Deeper Strata study](../../../research/lab-manager-reuse-20261109/strata-study/README.md) and [optional experiment ideas](../../../research/lab-manager-reuse-20261109/strata-study/experiment-ideas.md).

The November 10 user direction makes Muse Spark Open on one 128 GB DGX Spark the primary handbook and engine-design target. The Granite/RTX and Jetson campaigns remain supporting empirical evidence, with their original workloads and qualification limits. The earlier Muse workshop supplies model-specific design context; no working Muse baseline or Spark measurement is established. This supersedes the previous interpretation that Muse/Spark was only background to the small-model campaign.

## Keep the focus current

For every critical new user clarification: preserve exact visible wording and a hash in Sources, update this interpretation and the affected prompt/design/runbook, explain what earlier interpretation changed, and retain prior source bytes. Surface the current focus through Home, Active Stage and the relevant handoff. Never rewrite historical measured results as new acceptance or let a compelling demo displace the main learning objective.
