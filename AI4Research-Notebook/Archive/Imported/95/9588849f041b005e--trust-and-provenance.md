# Trust, provenance and reusable knowledge feeds

Research snapshot: 2026-10-07. Local exploratory notes only; not architecture, task allocation or permission. Primary sources were read through their relevant full-text sections. No benchmark or tool was executed here.

## Human synopsis

A useful capsule feed needs more than relevant text. Keep source identity, evidence scope and trust separate from the advice itself. Retrieved code, learned experience and condensed summaries can influence behavior; none should silently become policy, permissions or an accepted result. Existing design already separates admission, frozen bindings, evidence and gate authority. The research below suggests concrete ways to test those boundaries in M2, especially when adding experience overlays or external skill catalogs.

The most useful tightening to explore is preserving provenance through every transformation: raw source → extracted lesson → retrieval/index entry → chosen invocation context. A hash preserves bytes, not correctness. A familiar repository or reassuring scanner result is a signal, not admission. Test both legitimate utility and unwanted effects; blocking every action is not a useful secure system.

## Primary evidence cards

### T1. Defeating Prompt Injections by Design (CaMeL)

Debenedetti et al. First submitted 2025-03-24; inspected v2, 2025-06-24. [Paper/version](https://arxiv.org/abs/2503.18813v2) · [full text](https://arxiv.org/html/2503.18813v2) · [author code](https://github.com/google-research/camel-prompt-injection).

Evidence: §§2, 3.1, 5 and 6.4 distinguish protected control flow from argument/data-flow manipulation. Separate planning and quarantined extraction alone do not stop an attacker-controlled recipient or filename from reaching a tool. The interpreter tracks origins/permitted readers and applies tool policies. §3 assumes trusted user input and uncompromised memory; text-only manipulation, misleading summaries and phishing are explicit non-goals. §7 discusses side channels. The code README labels the interpreter a research artifact with possible bugs/security gaps.

Our inference: test effects on individual argument values, not only allowed tool names or graph shape. This reinforces runner/model-disclosure/effect boundaries; it does not validate our implementation or require adopting CaMeL's interpreter. Its security “capability” is an authorization concept, distinct from our capability capsule. Old search summaries quote v1's 67% utility; v2 reports 77% vs 84% undefended. Neither figure transfers to AI4Research.

### T2. Securing AI Agents with Information-Flow Control (Fides)

Costa et al. First submitted 2025-05-29; inspected v2, 2025-09-03. [Paper](https://arxiv.org/abs/2505.23643v2) · [full text](https://arxiv.org/html/2505.23643v2) · [author tutorial](https://github.com/microsoft/fides).

Evidence: §§4.1–4.4 and 5 propagate confidentiality/integrity labels, check policies and selectively hide/reveal data. Proposition 1 distinguishes non-interference for integrity from explicit secrecy for confidentiality: secret-dependent control-flow observations are not eliminated by the latter. Correct trusted tool wrappers, labels and policies are assumptions. Appendix D reports efficiency limits, including roughly 2–3× token use in their comparison. Results are AgentDojo-based, with additional labeling and adapted evaluation.

Our inference: a future context feed could carry separately enforced origin/audience metadata, and policy-aware selection might avoid impossible bindings. This is an M2 experiment, not a claim that attaching labels to JSON secures a system. Measure utility, label failures, permitted-reader mistakes and cost; do not substitute a probabilistic “trusted” label for authoritative access controls. Current disclosure rules cover audience gating but do not claim a general IFC implementation.

### T3. AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases

Chen et al. Inspected arXiv v1, 2024-07-17. [Paper](https://arxiv.org/abs/2407.12784v1) · [full text](https://arxiv.org/html/2407.12784v1). Relevant §§3.2, 4 and Appendix A.2.

Evidence: attacks inject a small number of demonstrations into an accessible retrieval store and optimize query triggers; the experiment covers three specific agent applications. §3.2 assumes partial database access. §4 distinguishes retrieval success, target generation conditional on retrieval, and end-to-end action success; these must not be collapsed into the abstract's headline “attack success.” Benign utility can look almost unchanged while triggered behavior is corrupted. This is not a generic measured rate for arbitrary capsule feeds.

Our inference: normal-case quality alone cannot admit an experience library. Test targeted retrieval and behavior separately, retain the selected entries and investigate how an attacker could write them. Direct store-write access and external-content-induced writes are different threat models; T4 covers the latter. A successful recall of a relevant-looking record is not evidence that the record is true or safe to follow.

### T4. From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents

Dash et al. First submitted 2026-06-03; inspected v2, 2026-06-18. [Paper](https://arxiv.org/abs/2606.04329v2) · [full text](https://arxiv.org/html/2606.04329v2). Relevant §§2.2, 3.1, 4.1–4.5, 5.

Evidence: MPBench tests persistent writes and later behavior in two agents using GPT-OSS-120B/default configurations. Four write channels include compaction and experience-to-procedure. Its ASR measures poisoned writes; retrieval success is conditioned on write success. The benchmark includes 3,240 attack and 2,997 benign examples, static-context and actual tool-retrieval modes. Semantic equivalence/outcomes use an LLM judge with manual sample checking. Existing input detectors incompletely cover these attacks.

Our inference: M2 experience overlays need a write/derivation boundary as well as a retrieval boundary. Test a clean new session after exposure; inspect whether advice survives compaction and becomes a procedure. Preserve audience/origin metadata on generated lessons instead of implicitly upgrading stored text to trusted instruction. Two agents and one base model do not establish a universal causal ranking of memory policies. Proposed write-path defenses are directions, not demonstrated proof of prevention.

### T5. Context Matters: Repository-Aware Security Analysis of the Agent Skill Ecosystem

Holzbauer et al. First submitted 2026-03-17; inspected v2, 2026-06-01. [Paper](https://arxiv.org/abs/2603.16572v2) · [full text](https://arxiv.org/html/2603.16572v2). The v1 title was *Malicious Or Not: Adding Repository Context to Agent Skill Classification*; do not count versions as two papers.

Evidence: §§5–7 report disagreement across skill scanners and inspect repository context. The 0.52% residual suspicious figure describes 15 of 2,887 sampled scanner-flagged skill/repository combinations, not an ecosystem-wide measured malicious prevalence. Context analysis uses capped text and LLM assessment; manual checking is small, and §7 explicitly disclaims definitive ground truth. Repository namespace hijacking and mutable external references are identified supply-chain risks.

Our inference: use contextual risk signals plus immutable source snapshots and implementation/dependency pins; do not admit solely on a scanner vote, GitHub stars, or a coherent README. Current declaration hashes address byte identity; a later catalog importer also needs origin continuity, changed-reference detection and reasoned admission. Static congruence is insufficient to claim runtime safety.

### T6. Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?

Bhagwatkar et al. First submitted 2025-10-06; inspected v2, 2026-03-23. [Paper](https://arxiv.org/abs/2510.05244v2) · [full text](https://arxiv.org/html/2510.05244v2). Relevant §§7–10, Appendix D.

Evidence: analyzes benchmark defects, including removal of task-essential content, brittle utility checks and forced tool invocation. Separate benign utility, attack success and utility under attack are necessary to interpret a defense. A sanitizer's perfect scores on existing attacks do not survive their adaptive cascade; Table 6 reports nonzero bypasses in the studied Slack suite. Impact statement assumes trusted user tasks and secure tools and notes extra model calls can disclose sensitive data.

Our inference: an AI4Research boundary trial should retain task solvability, record actual unauthorized effects, and measure useful completion beside refusal. Do not convert a detector score or saturated public benchmark into a universal security claim. Treat this critique as one study's evidence; inspect any reused benchmark revision and oracle before relying on its score. It does not justify deleting existing M1 requirements or relaxing gates.

### T7. Design Patterns for Securing LLM Agents against Prompt Injections

Beurer-Kellner et al. Inspected v1, 2025-06-10. [Paper](https://arxiv.org/abs/2506.08837v1) · [full text](https://arxiv.org/html/2506.08837v1). Relevant §3, scientific/code case studies in §4 and §5 recommendations.

Evidence: develops six structural patterns and ten case studies with explicit utility/security trade-offs. A fixed plan can still produce misleading text; sandboxed execution can still leak allowed-read information through outputs. The coding-assistant case distinguishes restricted actions from exposing untrusted documentation to a privileged agent. These are conceptual designs/case studies rather than a comparative AI4Research experiment.

Our inference: prefer narrow, purpose-specific tool and context interfaces. A sidecar log read is still untrusted text to its caller, and a registered command needs parameter/effect constraints. A product output verifier cannot retroactively undo a disclosed secret or host effect. Existing separate development tooling and pre-effect controls already express this boundary; future adapters need demonstrations, not another authority layer.

## Candidate M2 experiments, not requirements

| Question | Minimal use-based comparison | Observe | Existing seam |
|---|---|---|---|
| Does a lesson feed improve useful completion without changing authority? | Same accepted task and admitted Capability Capsule (CC) with no lesson vs selected lessons; include a plausible but invalid lesson | Task/consumer outcome, selected entries, source retention, cost, improper effect attempts | Future overlays, context recipe, runner policy |
| Does compaction preserve source identity? | Same mixed-source session before/after summarization, then a clean next session | Whether an untrusted suggestion becomes an asserted instruction or retained procedure | Evidence lineage; future memory write/admission |
| Can an allowed tool receive an unauthorized argument? | Same fixed graph, authorized destination vs destination found in untrusted text | Actual effect, refusal/unknown, legitimate task completion | Effects, model bridge, disclosure controls |
| Do catalog updates preserve admitted identity? | Simulate changed content or namespace with the same discovery URL | Frozen run still uses its pin; changed candidate stays inactive; missing original is visible | Carrier/body/dependency hashes and admission |
| Is apparent safety just broken utility? | Benign case and semantically valid attacked case with essential data retained | Correct result, unwanted effects, refused legitimate operations, budget | Sidecar evidence; native product checks |

Use safe local fixtures/owned targets; no real attack against external systems is proposed. Include contrasting successful and failing cases. Numerical thresholds, campaign sizes and APIs are deliberately unchosen. Do not let these notes become extra M1 ACs.

## Agent anti-patterns to remember

- Treating retrieval rank, repetition or a stored memory as permission.
- Losing origin/audience information during extraction, summarization or compaction.
- Using a fixed graph as proof that effect parameters cannot be manipulated.
- Reading every diagnostic log into an unrestricted command-writing context.
- Equating content hashes with correctness, publishers with stable URLs, or scanners with ground truth.
- Reporting conditional retrieval/write success as end-to-end safety or attack success.
- Measuring refusals without checking that legitimate work remains possible.
- Exporting private review data to an extra sanitizer/judge without the same audience checks.

## Audit state and remaining work

All seven cards have primary full-text section reads. Version pages checked on 2026-10-07. No author-code implementation was executed and no exact repository dependency commit was established; code links are leads only. Comparisons between papers are inference, not a replication. Next useful pass: audit transformation provenance against current declaration fields, and search counterevidence about performance under context selection and adaptive defense testing. Keep quantitative claims at their exact population/denominator.
