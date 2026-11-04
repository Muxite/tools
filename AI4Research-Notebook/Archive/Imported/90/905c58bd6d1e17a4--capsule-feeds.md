---
title: Capsule feeds, reusable knowledge, and retrieval research
date: 2026-10-07
tags: [capsules, agent-memory, retrieval, skills, research]
status: research-note
---

# Capsule feeds, reusable knowledge, and retrieval

Scope: evidence relevant to reusable task-independent capability context, external skill/tool feeds, experience memories, retrieval and composition. This note is exploratory input only. It does not change the maintained design package or imply runtime support. Primary papers and author-maintained project pages only; claims below distinguish reported findings from design inferences.

## Human synopsis

The reviewed papers study distinct reusable objects: executable skills, successful trajectories, generalized lessons, document summaries and plan recipes. Our architectural hypothesis is to keep reusable content separate from a run's frozen bindings and select a small, typed, source-linked subset for its consumer. The papers do not establish that boundary or validate capsule selection. Keeping these objects distinguishable lets an experiment measure their different scope, utility and failure modes.

Retrieval quality is not just nearest-neighbor relevance. The studies examine hierarchical discovery, role-aware context composition, retrieval of trajectories/lessons, and inspection of source material behind abstractions. Typed input/output eligibility is our proposed experiment, not a result these studies establish. The maintained design supplies the admission, pinning and authority boundary; a retrieval match does not change it.

## Evidence-to-design synthesis

| Research finding | Evidence that supports it | Existing capsule fields/responsibilities it touches | Inference / boundary |
|---|---|---|---|
| Reusable procedures can be executable, compositional artifacts rather than prompt text. | Voyager stores executable, temporally extended skills, retrieves them, and composes them in a persistent skill library; AgentSkillOS reports DAG orchestration outperforming flat provisioning even with oracle skills. | `identity.kind`, `carrier`, `body[]`, `summary`, `ports`, `members`, `structure`, `wiring`, `needs.external`, `guarantees.checks`. | Capsule declaration can describe a reusable procedure and composite, but its feed should not silently edit the frozen graph or infer permissions. The task graph/run records own invocation. |
| Context has multiple classes with different confidence and update rates. | ExpeL separately stores successful trajectories and generalized insights, updating insights against successes/failures. Generative Agents separate raw experience and reflections. | `identity.overlays[]` is a possible future carrier for experience/guidance layers; `provenance`, `identity.lineage`, check/eval evidence can identify source and validation. | Do not collapse verified package docs, raw run traces, generalized lessons, and executable tools into one “memory” field. Overlay support remains future direction in current inventory. |
| Task similarity alone is a weak general contract for choosing context. | Self-RAG finds fixed-count retrieval can add irrelevant passages; AgentSkillOS and GoSkills use structure/roles to organize what is retrieved; ExpeL uses task similarity for successful trajectories. | `summary`, typed `ports`, `needs.when`, dependency pins, checks, budget and effect declarations can serve as structured selectors/constraints. | Compose candidate scoring from multiple metadata signals (semantic similarity, declared capability, preconditions, schemas, version/admission, risk, cost); experiments should ablate each. These extra signals are proposed, not validated by cited papers. |
| Hierarchy and DAGs address different problems. | RAPTOR builds abstraction levels for retrieval over long documents. AgentSkillOS uses a capability tree to discover skills then DAGs to sequence/parallelize them. | Tree/index belongs to library/catalog; `structure`/`wiring` is the capsule's internal composite graph. | Avoid encoding discovery hierarchy as execution order. A catalog tree should be a derived index; the declared composite DAG is pinned executable structure. |
| Useful experience memory needs provenance, correction and revalidation. | ExpeL updates insight weights against success/failure evidence; ACE argues end-to-end rewriting causes context collapse and uses incremental curation. | `identity.lineage`, `provenance`, check `signal_source`, `owner`, `assurance`, `held_out`, versioned body hashes, evolution freeze. | A self-authored lesson is a hypothesis, not a guarantee. Promote only through versioned admission with evidence; retain both evidence link and extraction lineage. |
| Selection, loading and size are part of the capability contract operationally. | MemGPT uses explicit memory tiers and transfers content between them; RAPTOR selects different abstraction levels; GoSkills uses a bounded, role-labeled execution context. | `identity.load_mode`, task-independent `summary`, `budget.context_cost_tokens`, per-call token budget, typed ports and schema refs. | Make selection deterministic/auditable where feasible, bound context cost, and record selected exact hashes in run context. Load mode is a compatibility boundary, but exact feed protocol is not yet specified. |
| Reusable plan recipes may reduce repeated synthesis, but only if reusable semantics and dependencies remain explicit. | AgentSkillOS describes reusing orchestration recipes for similar tasks. | `identity.lineage`, body/carrier hash, `needs.external`, `members`/`structure`, budgets and checks. | A cache hit should resolve to a pinned admitted CC/recipe and re-check current preconditions/dependencies, not reuse a prior answer or grant old authority. |

## Paper cards (agent reference)

### 1. Voyager: An Open-Ended Embodied Agent with Large Language Models

- Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar. Submitted 2023-05-25; current paper v2 dated 2023-10-19; arXiv:2305.16291. [Paper and version history](https://arxiv.org/abs/2305.16291) · [author project/code](https://voyager.minedojo.org/).
- Full-text review: §§2.2–2.3 describe executable code skills, task-plan/environment-feedback embedding retrieval (top five), feedback/error-driven refinement and an LLM self-verification gate; §§3.3–3.4 evaluate progress and ablate components; Appendix B.4.4 evaluates retrieval on 309 samples and reports 96.5% top-5 accuracy; §4 discusses limitations. Reuse is also evaluated on a new Minecraft world.
- Supports: executable reusable procedures and transfer by skill retrieval/composition. It does not establish generic correctness, safe reuse across unrelated domains, or capsule admission policy.
- Mapping: implementation `carrier`/`body`, task-independent `summary`, `ports`, composite `members`/`structure`/`wiring`, output checks. Selection is separate from the per-run frozen graph.
- Limitation: one Minecraft environment, hand-coded API, GPT-4/GPT-3.5 and older embedding model; the self-verifier is another GPT-4 call and can miss task success. The paper reports remaining skill-generation failures and hallucinated impossible tasks (§4). These results do not establish independent assurance or cross-domain guarantees.

### 2. ExpeL: LLM Agents Are Experiential Learners

- Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang. Submitted 2023-08-20; v3 2024-12-20; AAAI 2024. [Paper/version history](https://arxiv.org/abs/2308.10144) · [author code](https://github.com/LeapLabTHU/ExpeL).
- Full-text sections 4.1–4.4: gathers success/failure trajectories; retrieves successful examples by task embedding similarity; compares failed/successful pairs and groups of successes to propose insights. Insight operators are ADD, EDIT, UPVOTE, DOWNVOTE; importance decrements can remove weakly supported entries. Inference combines the full insight list with top-k retrieved successful trajectories. The authors explicitly discuss retrieval as a future way to handle growth of the insight list.
- Supports: keep exemplars and abstractions as separate feed types; draw on both success/failure feedback; deduplicate or reduce weak lessons over accumulated evidence; retrieve task-similar examples.
- Mapping: lineage/provenance for trajectory and insight derivation; overlays are a future-design candidate for guidance/experience; quality/evaluation fields should report measured scope. A check or evidence record should remain distinct from generated advice.
- Limitation: deterministic interactive benchmarks and prompting-era implementations; extracted insights are LLM-authored, not proof. Similarity retrieval is used for success demos, while extracted insights are all prepended in the described setup, so this does not validate an optimal retrieval policy for large libraries.

### 3. Generative Agents: Interactive Simulacra of Human Behavior

- Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein. Submitted 2023-04-07; current arXiv v2 dated 2023-08-06; UIST 2023. [Paper/version history](https://arxiv.org/abs/2304.03442) · [author project/code](https://github.com/joonspk-research/generative_agents).
- Full-text review: §4.1 stores observations in a memory stream and ranks them by equal-weight normalized recency, embedding-cosine relevance and LLM-scored importance; retrieved memories are bounded by context capacity. §4.2 creates higher-level reflections from accumulated observations, which enter retrieval like other memories. Ablations disable observation, reflection and planning; §8.2 notes the retrieval weighting needs improvement and reports high simulation cost.
- Supports: different retrieval dimensions can matter; raw episodic records and abstract reflections serve distinct roles; reflection can become later retrievable memory.
- Mapping: an experience feed could use provenance, time, scope and source reliability; any published lesson would need `lineage` and separately validated guarantees.
- Limitation: 25-agent social sandbox; human ratings focus on believability, not correctness or safe capability transfer. “Importance” is not a trustworthy admission signal.

### 4. Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models (ACE)

- Qizheng Zhang et al. Submitted 2025-10-06; v3 2026-03-29; ICLR 2026. [Paper/version history](https://arxiv.org/abs/2510.04618) · [author project/code](https://ace-agent.github.io/).
- Full-text paper motivates brevity bias and context collapse from rewriting a single context. ACE uses generator, reflector and curator to update a structured playbook incrementally; reports improvements on agent and domain tasks and analyzes token/latency costs. It uses execution feedback without labeled supervision in evaluated setups.
- Supports: incremental structured curation is a testable alternative to repeatedly summarizing/replacing the whole feed; compare total lifecycle cost and retained details.
- Mapping: candidate context overlays, lineage, provenance, evaluation suite/metrics and per-call context budgets. ACE is a context adaptation mechanism, not a capsule registry, verifier or authorization boundary.
- Limitation: benchmark/model-specific; results depend on feedback quality and evaluation protocols. Self-generated playbook updates remain untrusted until independently checked.

### 5. MemGPT: Towards LLMs as Operating Systems

- Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez. Submitted 2023-10-12; arXiv:2310.08560. [Paper/version history](https://arxiv.org/abs/2310.08560) · [author project](https://memgpt.ai/).
- Evidence: virtual context management uses fast/slow memory tiers and model-directed control/interrupts to move content into/out of limited context; evaluated in document analysis and multi-session chat.
- Supports: explicitly modeling context residency and read/write operations rather than treating memory as a single unlimited prompt; load and eviction decisions can be part of runtime behavior.
- Mapping: `load_mode`, context token estimate/budget, resources and service injections. Capsule declarations can state dependencies and limits; memory policy and permissions belong to runtime/run configuration.
- Limitation: memory tiering does not ensure relevant or truthful recall; model-directed writes can contaminate stores. Evaluations do not establish access-control or provenance requirements for reusable capability libraries.

### 6. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

- Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh Khanna, Anna Goldie, Christopher D. Manning. Submitted 2024-01-31; ICLR 2024. [Paper/version history](https://arxiv.org/abs/2401.18059) · [author code](https://github.com/parthsarthi03/raptor).
- Full text: recursively embeds, clusters, and summarizes chunks to create a tree of increasingly abstract summaries, then retrieves at multiple levels. Reports improvements on QA benchmarks, especially tasks requiring synthesis over whole documents.
- Supports: hierarchical retrieval can expose both specific chunks and global summaries; retrieval level is a meaningful selector for long reference feeds.
- Mapping: likely a library-side index over `identity.body[]` / overlays; retain original pinned body hashes as the evidence source. Summaries are derived retrieval aids, not substitutes for source integrity.
- Limitation: document QA, not capability/skill selection; summaries can omit details and its scores do not show that abstracted context is safe to execute.

### 7. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

- Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi. Submitted 2023-10-17; ICLR 2024. [Paper/version history](https://arxiv.org/abs/2310.11511) · [OpenReview paper](https://openreview.net/forum?id=hSyW5go0v8).
- Evidence: argues fixed-count retrieval regardless of need/relevance can hurt; trains special reflection tokens for adaptive retrieval and critique of retrieved passages/generations. Evaluates QA, reasoning, fact verification and long-form factuality/citation.
- Supports: test whether a retrieval should occur and whether a retrieved item supports the task; selective retrieval can beat unconditional injection in its benchmark settings.
- Mapping: `needs.when` (applicability/state), `summary` as candidate discovery metadata, checks/acceptance and signal source for declared outputs. Selection still cannot assign protected verifier criteria.
- Limitation: learned retrieval/critique policy and document QA setting; model self-critique is not independent assurance, and results do not specify capsule-specific matching.

### 8. Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale (AgentSkillOS)

- Hao Li, Chunjiang Mu, Jianhao Chen, Siyue Ren, Zhiyao Cui, Yiqun Zhang, Lei Bai, Shuyue Hu. Submitted 2026-03-02, v1. [Paper/version](https://arxiv.org/abs/2603.02176) · [author repository](https://github.com/ynulihao/AgentSkillOS).
- Full text §§2–4: builds an offline capability tree, retrieves candidates, then composes alternative execution DAGs. Across 30 artifact tasks and skill pools of 200, 1K and 200K entries, it reports tree retrieval near oracle and DAG execution above flat invocation, including with the same oracle skills.
- Supports: separate discovery from composition; compare a catalog hierarchy and executable DAGs. Mapping: catalog index separate from declaration `structure`; DAG `members`/`wiring` plus typed `ports`; bind selected declaration and plan hashes into run evidence.
- Limits: one model family, curated tasks and LLM-pairwise artifact judging; not evidence of safe execution or general transfer.

### 9. Group of Skills: Group-Structured Skill Retrieval for Agent Skill Libraries (GoSkills)

- Kun Zeng, Yu Huo, Siyu Zhang, Zi Ye, Yuecheng Zhuo, Haoyue Liu, Yuquan Lu, Junhao Wen, Xiaoying Tang. Submitted 2026-05-07, v1. [Paper/version](https://arxiv.org/abs/2605.06978).
- Full text §3–§5: anchor-centered groups on a typed skill graph are rendered under a context budget with Start, Support, Check and Avoid roles; SkillsBench and ALFWorld evaluations compare this with flat/structural baselines.
- Supports testing role-aware retrieval and bounded context. Mapping: candidate roles could inform `members[].role`; ports/schema/wiring expose requirements; checks remain `guarantees.checks`. This renderer is not an authored declaration field.
- Limits: preprint, bounded tests; visible-requirement coverage is not correctness or safe effect composition.

## M2 experiments worth running

1. **Candidate retrieval ablation:** fixed lexical/embedding top-k vs hierarchy traversal vs combined selectors. Measure top-1/top-k admitted-capsule recall, irrelevant context rate, token cost, dispatch mismatch and task completion. Use fixed library snapshots, held-out tasks and a blinded label set; include near-duplicate and misleading summaries.
2. **Typed metadata utility:** compare summary-only retrieval with summary + typed ports/schema + preconditions + dependency pins + effect class + check coverage + budget. Measure binding errors and false eligibility as well as completion. Test unknown/stale `needs.when` values explicitly; they must not become a silent pass.
3. **Experience feed admission:** compare raw successful traces, reflection/lesson overlays, and lessons supported by multiple independent runs plus a check. Include misleading one-off successes and corrected failures. Keep creator and solver contexts isolated; measure pack discovery/use, transfer to held-out task variants, harmful regressions, evidence traceability and reviewer time. Never treat success counts as proof of invariant correctness or let a same-task authoring run leak verifier details into a supposed reusable skill.
4. **Composition:** flat top-k versus typed role groups versus declared composite DAG. Include independent branches (parallelism), dependency chains, duplicate/overlapping skills, incompatible schema versions, and partial failure. Measure output validity, effect traceability, total latency/cost, and whether every member's checks/effects remain visible.
5. **Abstraction level / reversible memory:** raw source only, summary only, hierarchical summaries with source back-links, and raw-plus-abstraction. Construct questions where omitted details matter; measure answer grounding and ability to recover the source. Track summary hash/version.
6. **Retrieval/load budget:** vary number/size of injected capsules; measure performance, context cost, latency and selection stability. Record exact candidates considered, selected hashes, scores/reasons and dropped items in run evidence. Test stale library versions and cache invalidation.
7. **Recipe/cache validity:** replay a cached composition on semantically similar but boundary-different requests, changed dependencies, changed effect availability and changed output schema. Require precondition/dependency checks and exact pinned revisions; compare to fresh replanning.
8. **Evidence promotion lifecycle:** synthetic evidence store with source run, evaluator, fixture, model, timestamp and capsule hashes. Test whether update creates a new immutable version, maintains old run resolvability, and prevents a generated lesson from changing protected checks or runtime policy.

## Anti-patterns / failure modes to guard against

- One giant “memory” field blending source documents, summaries, run traces, lessons, tools and permission language.
- Selecting by embedding similarity alone or by summary keyword overlap; no eligibility check against typed ports, preconditions, dependency/version pins, declared effects or required checks.
- Treating LLM-generated reflections, skill popularity/installs, judged quality, or a single successful run as evidence of a guarantee.
- Overwriting a feed in place, dropping source links, or allowing a run to float onto a newly admitted version after planning.
- Conflating a library/category tree with an execution DAG; category parentage does not imply dependency or ordering.
- Presenting several skills flat and asking the executing model to infer start point, support roles, data flow, output ownership and checks.
- Retrieving only a lossy abstract; no immutable raw source or reproducible version/hash behind the summary.
- Reusing cached answers instead of reusable procedures, or reusing a procedure without checking current state and external pins.
- Letting the capability author, a sub-agent, or its generated memory decide permissions, verifier criteria, or successor release. Selection is not authorization; gate and runner duties remain separate.
- Claiming that a schema pin, hash, or declared network field alone enforces runtime confinement; the existing declaration explicitly leaves enforcement to the runner.

## Research holes / next useful papers

- Calibration and error rates for probabilistic metadata extraction/skill matching; false-positive binding cost versus missed capability cost.
- Retrieval policies over typed preconditions/effects and contract compatibility rather than natural-language descriptions.
- Memory deletion, contradiction handling, evidence expiry and invalidation after dependency/model changes.
- Composite check/effect propagation and whether flat member checks preserve system-level postconditions.

## Version and counter-evidence audit

### Current-version audit: three most useful skill-system studies

1. **AgentSkillOS**, [arXiv record](https://arxiv.org/abs/2603.02176): the record lists v1, submitted 2026-03-02. Locators: §2.1; §§2.2.1–2.2.3; §§3–4.2. In the 200K condition, its active tree is capped at the top 10K by install count; the remainder is dormant-indexed (§4.1). The benchmark is curated, 30 tasks, and LLM-pairwise judged (§§3.2, 4.1).
2. **GoSkills**, [arXiv record](https://arxiv.org/abs/2605.06978): current record v1, submitted 2026-05-07. Locators: §3 method; §4 evaluations; §5 ablations; §6 limits. It retrieves/contextualizes only—no execution, argument binding, precondition checks or runtime repair (§§3, 6); §4.1 uses three repeats per model-method-benchmark combination. Ablations include a contract-matched presentation control.
3. **SkillsBench**, [arXiv v4](https://arxiv.org/abs/2602.12670v4), revised 2026-06-14. Checked §§3–5.1.3, §6.1 and Appendices D.6/F/M. Current matched study: 87 tasks, 8 domains, 18 model-harness configurations; curated Skills improve average pass rate by 16.6 percentage points, with negative deltas on 13 tasks. Heavy workflows, strategy displacement and solver/debug mismatch appear in failure analysis. A separate self-generation diagnostic uses only three configurations: generated Skills lose 8.1–11.5 points against no Skills, while curated ones gain 18.2–24.8. Its 12-trajectory audit finds unused packs, authoring displacing solving, confident errors and an apparent win involving benchmark-instance leakage. Creator/solver interference and an effort-level mismatch are confounds. §6.1 calls for length-matched irrelevant-text and retrieval-only documentation controls. **Our inference:** test focused curated context, context cost and regressions; neither the aggregate nor this diagnostic establishes a universal policy for capsule creation or admission.

### Empirical retrieval-distractor evidence

- **Making Retrieval-Augmented Language Models Robust to Irrelevant Context** — Ori Yoran, Tomer Wolfson, Ori Ram, Jonathan Berant. First submitted 2023-10-02; current arXiv v2 2024-05-05. [Paper/version](https://arxiv.org/abs/2310.01558) · [author repository](https://github.com/oriyor/ret-robust). Full-text locators: §§1–2 (problem and methods), §3 (datasets/models), §4 (main and distractor results, including “Adding Retrieval to In-context Exemplars can Hurt Performance”), §5 (error analysis). They evaluate five ODQA datasets; random retrieved passages reduce few-shot Llama-2-13B accuracy by >10 points on average in their setting, and even top-1 Google retrieval hurts StrategyQA and Fermi. NLI filtering prevents some regressions but also discards useful passages; fine-tuning on mixed relevant/irrelevant examples improves robustness. This directly supports testing no-retrieval/back-off and irrelevant-feed controls. Limit: QA passages, older Llama models and narrow retrieval setup—not capability routing.
- **Lost in the Middle: How Language Models Use Long Contexts** — Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang. Submitted 2023-07-06; accepted by TACL (2023). [Paper/version](https://arxiv.org/abs/2307.03172) · [author code](https://github.com/nelson-liu/lost-in-the-middle). Full-text locators: §2.1 (controlled multi-document QA with one answer-bearing document and distractors), §2.2 (key-value retrieval), §3 (models/analysis). It reports strong position sensitivity: relevant evidence is often used best at the beginning or end and worse in the middle. Adding distractor documents increases context length without changing the answer-bearing evidence and can reduce performance. This is a separate mechanism from semantic irrelevance: even a relevant context can be missed due to position. Limit: stress tests on context use, not skill-library retrieval or a universal prescription for context ordering.

**M2 consequence from the counter-evidence:** include length-matched irrelevant, random, and near-neighbor distractors; test no-retrieval and back-off decisions; vary selected-feed position; and score false positive/false negative binding. Measure whether a candidate provides positive evidence for task requirements, not just semantic similarity. Keep this as an experiment proposal: cited evidence is from QA retrieval and skills benchmarks, not the JiuwenSwarm runtime.

## Candidate feed model and metadata selection questions

The current inventory gives a useful starting separation without specifying a full retrieval service. Treat these as *research categories*, not new canonical fields:

| Feed object | What it contains | Candidate identity/evidence links | Scope to preserve |
|---|---|---|---|
| Admitted capability | Executable implementation plus its stable contract | `identity.name/version_label/kind`, `carrier`, `body[]`, declaration/contract hashes, admission record | Capability contract, effects, preconditions, dependencies and checks; exact version selected for run |
| Reference package | Factual or procedural source material loaded to support work | `body[]` or a future overlay with immutable source/hash; extractor version if summarized | Reference provenance and which source clauses support a derived summary |
| Experience record | Observed trajectory, result, error or feedback from a particular run | Run ID, graph/CC hashes, model/harness, environment, time, signal source and raw evidence | Must remain scoped to task/environment/version; success/failure does not generalize by itself |
| Distilled lesson | A human- or model-authored cross-run generalization | Parent experience refs, author/builder, extraction method/model/prompt, supporting/contradicting evidence, review/admission state | Advisory until validated; no new guarantees, permissions, verifier criteria, or runtime policy |
| Composition recipe | Candidate ordering/data-flow template over multiple capabilities | Member declaration hashes, roles, typed artifacts, dependency and compatibility evidence | Must re-check present preconditions and preserve effects/checks; catalog grouping is not runtime structure |
| Selection manifest | Per-task record of candidates considered, chosen items and why | Query/task reference, selector version, library snapshot, selected content/declaration hashes, scores/reasons, load budget | Belongs to planning/run evidence, not reusable CC contract; allow replay and audit |

**Candidate selector dimensions to ablate (not current authored schema keys):** semantic/lexical match; capability family and task-class applicability; input/output artifact types and schema compatibility; explicit positive and negative applicability; `needs.when` satisfiability and freshness; external dependency pin status; effect/risk compatibility; declared output/check coverage; evidence scope/assurance; version/admission status; token/context cost and load mode. The current `summary` is task-independent and useful for coarse discovery, but alone cannot establish fit. A retrieval score must never override a hard incompatibility (bad pin, unmet precondition, incompatible port, prohibited network/effect, missing required check).

A useful pipeline hypothesis for an M2 prototype is: coarse discovery over admitted catalog metadata → hard eligibility filtering → rerank a small candidate set → resolve optional experience/reference feeds separately → compose typed candidates → bind exact hashes into the plan → emit a selection manifest. This is an inference from complementary papers, not a demonstrated end-to-end result. Test it against a simple top-k baseline and measure false binding, missed binding, context cost and downstream task quality.


## Evidence review coverage

- **Full text reviewed:** ExpeL §§4.1–4.4; Voyager §§2.2–2.3, 3.3–3.4, 4 and App. B.4.4; Generative Agents §§4.1–4.2 and 8.2; ACE method, ablations and limitations; MemGPT virtual context/memory sections; RAPTOR retrieval experiments and Appendix E hallucination analysis; Self-RAG retrieval/adaptation and evaluation sections; AgentSkillOS §§2.1–2.2 and §§3–4.2; GoSkills §§3–6; SkillsBench v4 §§3–6.1 and Apps D.6/F.2–F.3/M; Yoran et al. §§1–5; Liu et al. §§2–3. Full text means arXiv HTML/PDF sections were opened and used; section locators above identify the passages behind the note.
- **Record/version or author project checked, without a full text audit:** GitSkills v3 arXiv record/abstract and its dataset description. It is supplementary corpus context, not a main capability-effect claim.
- **Author repositories/project pages:** Voyager and ExpeL implementations, RAPTOR and Generative Agents repositories, ACE project, and AgentSkillOS repository were checked for project identity/access. The paper claims above are drawn from the papers themselves, not repositories or secondary summaries.
- **Version checks as of 2026-10-07:** SkillsBench v4 (2026-06-14), ACE v3 (2026-03-29), ExpeL v3 (2024-12-20), Voyager v2 (2023-10-19), Generative Agents v2 (2023-08-06), Yoran et al. v2 (2024-05-05), Liu et al. v3 (2023-11-20), AgentSkillOS v1 (2026-03-02), and GoSkills v1 (2026-05-07). AgentSkillOS and GoSkills are recent preprints; their results are provisional.

