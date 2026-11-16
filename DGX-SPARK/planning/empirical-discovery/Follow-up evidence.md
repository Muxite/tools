---
id: inference-factory-followup-evidence-20261110
status: x86-followup-verified-jetson-transfer-blocked
source: Sources/Prompts/2026-11-10-closeout-transfer-followup.txt; research/inference-campaign-closeout-20261110/followup-evidence/source/CC-NEXT-EVIDENCE.md
last_reviewed: 2026-11-10
next_action: Receive Jetson ZIP through authenticated transfer; qualify the profile tool and supply exact JiuwenSwarm integration source
---
# Follow-up records correct qualification and readiness

**Jetson closeout now received:** [[Designs/Inference Factory - Empirical Discovery/Jetson closeout and CC implications|Per-type graph dispatch and portable-tool implications]]. Saved Orin results recompute to +23.64% Q4_K, +19.21% BF16 and −6.21% Q8; target qualification stays local. One useful CC remains sufficient for Friday.


The [received x86 evidence](../../../research/inference-campaign-closeout-20261110/followup-evidence/README.md) matches both user-supplied hashes; all 83 manifest entries verify. These are uncommitted additions based on x86 commit ecaa4b0, not a new engine build. The source document replaces the damaged pasted report as our evidence source.

- **up1 MUL_MAT: passed.** Raw stdout confirms 2517/2517. CLOSEOUT's statement that it was not run is incorrect. There are zero MUL_MAT_ID entries. Isolated operations cannot demonstrate a reuse-cache hit; no broader component qualification follows.
- **Recovery script: historically live-tested once.** The newly supplied log shows interrupted att-1, confirmed stop, clean att-2 and unchanged att-1. The agent reports about 13.5 seconds on November 9. Codex's static-only validation preceded the orchestrator's run. This resolves our earlier uncertainty, but not current-host readiness or integration with release-1/the other team's lab agent.
- **Component qualification gaps are concrete.** No paired OFF/ON launch count, raw F32 logits, targeted GPU alias/shape-switch/concurrent-stream/graphs-disabled tests, or Q8-reuse KLD run. Text/PPL and +2.17% performance evidence remain scoped observations. Host mocks are not CUDA execution.
- **Profile tool is the smallest useful first CC.** Our local rerun matches saved output: 600 launches, 221.852565 GB/s derived read bandwidth. All 13 classes misleadingly report zero write bytes despite writes not being collected. Fix to null/unavailable, rename the launch-bound heuristic, preserve exact identities/coverage and fail explicitly on unsupported formats. The direct long-form CSV has no .ncu-rep; another preserved BF16 wide-form report is not its source. Engine-library identity and exact NCU version are missing for the long-form capture; mark it unbound diagnostic evidence.
- **Build and integration gaps:** current builder is amd64/sm_120-only, Bake timeout/cancellation unqualified, total warm release invocation about 63.5 s versus 16 s Bake, and 33 GB of build archives omitted from the aggregate manifest. The x86 upstream JiuwenSwarm checkout lacks our modified CC v2 runner. Supply exact source/base; Build CC record schema v2 is unrelated to JiuwenSwarm CC v2.

[[Designs/Inference Factory - Empirical Discovery/One useful CC demo|One useful tool OR component remains the required demo]]. Expose/harden the existing profile parser first. A matched engagement capture is a subsequent owner-approved GPU task; compare equivalent token regions, not identical launch offsets when the optimization itself changes launch counts. Numerical/alias/graph tests precede wider component qualification. No new GPU work or services were changed here.

## Jetson acquisition

Direct LAN SSH timed out. Through x86, Jetson SSH was reachable but rejected public-key authentication from both available clients. First-seen host keys were enrolled via accept-new; no changed-key bypass or authorized_keys edits. No Jetson ZIP received, no Jetson findings asserted. A request to relay the ZIP through x86 or attach it is pending. The x86 follow-up cannot substitute for Jetson evidence.

## Further offline design analysis

The user requested analysis while away, so Jetson authentication remains untouched. [Detailed implementation priorities](../../../research/inference-campaign-closeout-20261110/followup-evidence/design-analysis.md) and [synthetic parser probes](../../../research/inference-campaign-closeout-20261110/followup-evidence/parser-probes.json) identify malformed numeric grouping, empty process identity and aggregate-overflow acceptance in the unchanged received parser. A completely removed trailing launch cannot be detected from remaining CSV alone; completeness requires external capture evidence. These are CPU-only probes, not GPU tests or CC implementation.

The newly supplied test summary says factory 7 failed/1 passed, versus CLOSEOUT 3 failed/5 passed. Assignment-root/basetemp effects are a possible explanation, not established from the summary. Do not call the factory ready or assume only stale expectations remain. It is outside the first tool demo.
