# Papers: id to title

Every paper in this folder, 126 of them. Each paper is here twice under two names: `<id>.pdf`
and `<id> - <short name>.pdf`, likewise for `.txt`. The two names are **hard links to the same file**:
one copy on this disk, and git stores the content once. But a folder copy to another device, or a git
checkout, writes two independent copies, so this folder is about twice its on-disk size wherever it lands.
The short name matches the paper's summary in `summaries/` where one exists.

**Tools use the bare-id name.** `tundlekit papers abs|body|grep` read `<id>.txt` (`tundlekit/papers.py:65-68`),
`papers fetch` checks for `<id>.pdf` (`papers.py:261`), and notes under `ai4research/notes/` cite line numbers in
`papers/<id>.txt`. tundlekit ignores the titled names, so do not delete the bare-id files.

⚠ **Links break silently.** `tundlekit papers fetch --reextract` replaces `<id>.txt` with a new file, and so
does any editor or sync tool that saves by replacing. The titled name then keeps the old content. To repair,
delete the titled file and link it again; to check, every pair should have the same file ID
(`fsutil file queryFileID` on Windows, `stat -c %i` on Linux).

Titles are arXiv's own `citation_title` metadata; page counts are read from the PDF.

## Why each paper is here

- `orig` cited in the original Capability Capsule presentation (`AI4Research Capability Capsule Presentation - Muk.pptx`)
- `deck` cited in the 2026-09-22 workshop deck draft (`capsule-openjiuwen/deck/deck-draft.md`)
- `read` Tier 1 or 2 of the reading list of 2026-09-21, now folded into `obby/Evidence.md`, plus 2608.25091, the paper whose reading refuted a citation
- `select` capability selection and retrieval, which moved to the capsule model on 2026-09-21 (Tier 4 routing papers)
- `prior` was in this folder before 2026-09-21 and is not `orig`; most of these back the general report
- `sum` has a written summary in `summaries/`. A blank means present and unread, not read and found wanting

Curated on 2026-09-21. Of 70 capsule papers added that day, 24 were kept. The 46 left out are 28 that
the capsule work cites only as background, surveys or teammate seams, and 18 from the literature sweep
that nothing cites. All 46 are in `capsule-openjiuwen/papers/` and re-fetchable with
`tundlekit papers fetch <id> --dir papers`. The capsule work cites 58 papers in all; 30 are here.

116 papers · 9 orig · 20 deck · 10 read · 90 with summaries

| arXiv id | Title | pp | why | sum |
|---|---|---|---|---|
| [2308.00352](https://arxiv.org/abs/2308.00352) | MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework | 29 | prior | sum |
| [2310.03714](https://arxiv.org/abs/2310.03714) | DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines | 32 | prior | sum |
| [2312.04511](https://arxiv.org/abs/2312.04511) | An LLM Compiler for Parallel Function Calling | 22 | prior | sum |
| [2409.13740](https://arxiv.org/abs/2409.13740) | Language agents achieve superhuman synthesis of scientific knowledge | 25 | prior | sum |
| [2410.05080](https://arxiv.org/abs/2410.05080) | ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery | 60 | prior | sum |
| [2410.07095](https://arxiv.org/abs/2410.07095) | MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering | 29 | prior | sum |
| [2410.10762](https://arxiv.org/abs/2410.10762) | AFlow: Automating Agentic Workflow Generation | 38 | prior | sum |
| [2411.04468](https://arxiv.org/abs/2411.04468) | Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks | 31 | prior | sum |
| [2411.14199](https://arxiv.org/abs/2411.14199) | OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs | 53 | prior | sum |
| [2501.04227](https://arxiv.org/abs/2501.04227) | Agent Laboratory: Using LLM Agents as Research Assistants | 84 | prior | sum |
| [2502.10855](https://arxiv.org/abs/2502.10855) | Towards Effective Extraction and Evaluation of Factual Claims | 50 | prior | sum |
| [2502.18864](https://arxiv.org/abs/2502.18864) | Accelerating scientific discovery with Co-Scientist | 157 | prior | sum |
| [2503.18813](https://arxiv.org/abs/2503.18813) | Defeating Prompt Injections by Design | 125 | prior | sum |
| [2504.01848](https://arxiv.org/abs/2504.01848) | PaperBench: Evaluating AI's Ability to Replicate AI Research | 30 | prior | sum |
| [2504.07079](https://arxiv.org/abs/2504.07079) | SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills | 40 | orig | sum |
| [2504.08066](https://arxiv.org/abs/2504.08066) | The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search | 69 | prior | sum |
| [2505.13400](https://arxiv.org/abs/2505.13400) | Robin: A multi-agent system for automating scientific discovery | 30 | prior | sum |
| [2505.18705](https://arxiv.org/abs/2505.18705) | AI-Researcher: Autonomous Scientific Innovation | 38 | prior | sum |
| [2505.22954](https://arxiv.org/abs/2505.22954) | Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents | 72 | orig deck | sum |
| [2506.07446](https://arxiv.org/abs/2506.07446) | Fact in Fragments: Deconstructing Complex Claims via LLM-based Atomic Fact Extraction and Verification | 32 | prior | sum |
| [2506.08837](https://arxiv.org/abs/2506.08837) | Design Patterns for Securing LLM Agents against Prompt Injections | 32 | prior | sum |
| [2506.11763](https://arxiv.org/abs/2506.11763) | DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents | 31 | prior | sum |
| [2507.01903](https://arxiv.org/abs/2507.01903) | AI4Research: A Survey of Artificial Intelligence for Scientific Research | 121 | prior | sum |
| [2507.21046](https://arxiv.org/abs/2507.21046) | A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence | 77 | orig | sum |
| [2508.15804](https://arxiv.org/abs/2508.15804) | ReportBench: Evaluating Deep Research Agents via Academic Survey Tasks | 18 | prior | sum |
| [2509.26603](https://arxiv.org/abs/2509.26603) | DeepScientist: Advancing Frontier-Pushing Scientific Findings Progressively | 19 | prior | sum |
| [2510.23601](https://arxiv.org/abs/2510.23601) | Alita-G: Self-Evolving Generative Agent for Agent Generation | 15 | orig deck | sum |
| [2511.02824](https://arxiv.org/abs/2511.02824) | Kosmos: An AI Scientist for Autonomous Discovery | 42 | prior | sum |
| [2511.19635](https://arxiv.org/abs/2511.19635) | Agint: Agentic Graph Compilation for Software Engineering Agents | 18 | prior | sum |
| [2512.17259](https://arxiv.org/abs/2512.17259) | Verifiability-First Agents: Provable Observability and Lightweight Audit Agents for Controlling Autonomous LLM Systems | 5 | prior |  |
| [2601.08815](https://arxiv.org/abs/2601.08815) | Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems | 22 | prior | sum |
| [2601.11868](https://arxiv.org/abs/2601.11868) | Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces | 84 | prior | sum |
| [2601.13217](https://arxiv.org/abs/2601.13217) | Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision | 42 | prior | sum |
| [2602.08990](https://arxiv.org/abs/2602.08990) | InternAgent-1.5: A Unified Agentic Framework for Long-Horizon Autonomous Scientific Discovery | 64 | prior | sum |
| [2602.21045](https://arxiv.org/abs/2602.21045) | PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based Scholarly Q&A | 25 | prior | sum |
| [2602.22302](https://arxiv.org/abs/2602.22302) | Agent Behavioral Contracts: Formal Specification and Runtime Enforcement for Reliable Autonomous AI Agents | 71 | prior | sum |
| [2602.22700](https://arxiv.org/abs/2602.22700) | IMMACULATE: A Practical LLM Auditing Framework via Verifiable Computation | 14 | prior |  |
| [2602.23452](https://arxiv.org/abs/2602.23452) | CiteAudit: You Cited It, But Did You Read It? A Benchmark for Verifying Scientific References in the LLM Era | 13 | prior | sum |
| [2603.05344](https://arxiv.org/abs/2603.05344) | Building Effective AI Coding Agents for the Terminal: Scaffolding, Harness, Context Engineering, and Lessons Learned | 81 | prior |  |
| [2603.05912](https://arxiv.org/abs/2603.05912) | DeepFact: Co-Evolving Benchmarks and Agents for Deep Research Factuality | 31 | prior | sum |
| [2603.08127](https://arxiv.org/abs/2603.08127) | EvoScientist: Towards Multi-Agent Evolving AI Scientists for End-to-End Scientific Discovery | 21 | prior |  |
| [2603.20356](https://arxiv.org/abs/2603.20356) | Agentproof: Static Verification of Agent Workflow Graphs | 26 | prior | sum |
| [2603.21019](https://arxiv.org/abs/2603.21019) | SkillProbe: Security Auditing for Emerging Agent Skill Marketplaces via Multi-Agent Collaboration | 16 | deck |  |
| [2604.00392](https://arxiv.org/abs/2604.00392) | Beyond Task Completion: A Verification-vs.-Conformance Gap in Tool-Evolving Agents | 12 | orig deck | sum |
| [2604.01687](https://arxiv.org/abs/2604.01687) | CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification | 23 | orig deck | sum |
| [2604.03141](https://arxiv.org/abs/2604.03141) | Beyond Precision: Importance-Aware Recall for Factuality Evaluation in Long-Form LLM Generation | 13 | prior | sum |
| [2604.03173](https://arxiv.org/abs/2604.03173) | Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents | 25 | prior | sum |
| [2604.03515](https://arxiv.org/abs/2604.03515) | Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures | 42 | prior | sum |
| [2604.04074](https://arxiv.org/abs/2604.04074) | FactReview: Evidence-Grounded Peer Review with Execution-Based Claim Verification | 16 | prior | sum |
| [2604.05333](https://arxiv.org/abs/2604.05333) | Graph-of-Skills: Dependency-Aware Structural Retrieval for Massive Agent Skills | 28 | select |  |
| [2604.05550](https://arxiv.org/abs/2604.05550) | AutoSOTA: An End-to-End Automated Research System for State-of-the-Art AI Model Discovery | 43 | prior | sum |
| [2604.08501](https://arxiv.org/abs/2604.08501) | sciwrite-lint: Verification Infrastructure for the Age of Science Vibe-Writing | 20 | prior | sum |
| [2604.13092](https://arxiv.org/abs/2604.13092) | PlanCompiler: A Deterministic Compilation Architecture for Structured Multi-Step LLM Pipelines | 31 | prior | sum |
| [2604.17870](https://arxiv.org/abs/2604.17870) | GraSP: Graph-Structured Skill Compositions for LLM Agents | 16 | deck |  |
| [2604.25256](https://arxiv.org/abs/2604.25256) | AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery | 28 | prior | sum |
| [2605.00798](https://arxiv.org/abs/2605.00798) | RunAgent: Interpreting Natural-Language Plans with Constraint-Guided Execution | 17 | prior | sum |
| [2605.06365](https://arxiv.org/abs/2605.06365) | From Agent Loops to Deterministic Graphs: Execution Lineage for Reproducible AI-Native Work | 16 | prior | sum |
| [2605.06635](https://arxiv.org/abs/2605.06635) | Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents | 12 | prior | sum |
| [2605.08956](https://arxiv.org/abs/2605.08956) | Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery | 20 | prior | sum |
| [2605.10052](https://arxiv.org/abs/2605.10052) | Swarm Skills: A Portable, Self-Evolving Multi-Agent System Specification for Coordination Engineering | 14 | prior | sum |
| [2605.10990](https://arxiv.org/abs/2605.10990) | Skill Drift Is Contract Violation: Proactive Maintenance for LLM Agent Skill Libraries | 22 | read |  |
| [2605.13716](https://arxiv.org/abs/2605.13716) | SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems | 23 | read |  |
| [2605.16976](https://arxiv.org/abs/2605.16976) | Securing LLM Agents Need Intent-to-Execution Integrity | 11 | prior | sum |
| [2605.19576](https://arxiv.org/abs/2605.19576) | Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries | 9 | deck | sum |
| [2605.24050](https://arxiv.org/abs/2605.24050) | More Skills, Worse Agents? Skill Shadowing Degrades Performance When Expanding Skill Libraries | 18 | deck read | sum |
| [2605.27922](https://arxiv.org/abs/2605.27922) | Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows | 16 | prior | sum |
| [2606.00644](https://arxiv.org/abs/2606.00644) | ForeSci: Evaluating LLM Agents for Forward-Looking AI Research Judgment | 26 | prior |  |
| [2606.00822](https://arxiv.org/abs/2606.00822) | SkillPager: Query-Adaptive Intra-Skill Navigation via Semantic Node Retrieval | 20 | select |  |
| [2606.02060](https://arxiv.org/abs/2606.02060) | Where Do Deep-Research Agents Go Wrong? Span-Level Error Localization in Agent Trajectories | 28 | prior | sum |
| [2606.03056](https://arxiv.org/abs/2606.03056) | SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale | 19 | orig | sum |
| [2606.07591](https://arxiv.org/abs/2606.07591) | ResearchClawBench: A Benchmark for End-to-End Autonomous Scientific Research | 73 | prior | sum |
| [2606.07904](https://arxiv.org/abs/2606.07904) | Contract2Tool: Learning Preconditions and Effects for Reliable Tool-Augmented LLM Agents | 10 | prior | sum |
| [2606.11851](https://arxiv.org/abs/2606.11851) | StatefulDiscovery: Evidence-Calibrated Claim Formation in Open-Ended Scientific Discovery | 28 | prior | sum |
| [2606.11926](https://arxiv.org/abs/2606.11926) | Toward Generalist Autonomous Research via Hypothesis-Tree Refinement | 36 | prior | sum |
| [2606.12344](https://arxiv.org/abs/2606.12344) | Claw-SWE-Bench: A Benchmark for Evaluating OpenClaw-style Agent Harnesses on Coding Tasks | 35 | prior | sum |
| [2606.13662](https://arxiv.org/abs/2606.13662) | EurekAgent: Agent Environment Engineering is All You Need For Autonomous Scientific Discovery | 12 | prior | sum |
| [2606.15497](https://arxiv.org/abs/2606.15497) | Towards End-to-End Automation of AI Research | 182 | prior | sum |
| [2606.19819](https://arxiv.org/abs/2606.19819) | CREDENCE: Claim Reduction for Decomposition & Enhanced Credibility -- Semantic Metrics and Convergence Analysis | 40 | prior | sum |
| [2606.20683](https://arxiv.org/abs/2606.20683) | From Question Answering to Task Completion: A Survey on Agent System and Harness Design | 29 | prior | sum |
| [2606.24530](https://arxiv.org/abs/2606.24530) | NatureBench: Can Coding Agents Match the Published SOTA of Nature-Family Papers? | 35 | prior | sum |
| [2606.26924](https://arxiv.org/abs/2606.26924) | A Deterministic Control Plane for LLM Coding Agents | 45 | prior | sum |
| [2606.30246](https://arxiv.org/abs/2606.30246) | Clarus: Coordinating Autonomous Research Agents toward Web-Scale Scientific Collaboration | 28 | prior |  |
| [2607.02345](https://arxiv.org/abs/2607.02345) | SkillFuzz: Fuzzing Skill Composition for Implicit Intents Discovery in Open Skill Marketplaces | 12 | deck | sum |
| [2607.06000](https://arxiv.org/abs/2607.06000) | Context-to-Execution Integrity for LLM Agents | 20 | prior |  |
| [2607.06001](https://arxiv.org/abs/2607.06001) | Information Limits and Attractor Dynamics in Economies of Frontier LLM Agents: A Pre-Registered Test | 15 | prior | sum |
| [2607.07436](https://arxiv.org/abs/2607.07436) | The Blind Curator: How a Biased Judge Silently Disables Skill Retirement in Self-Evolving Agents | 17 | deck read | sum |
| [2607.10487](https://arxiv.org/abs/2607.10487) | Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents | 20 | deck |  |
| [2607.13083](https://arxiv.org/abs/2607.13083) | Phantom Guardrails: When Self-Improving Agent Harnesses Fix Failures That Never Happened | 13 | deck |  |
| [2607.23332](https://arxiv.org/abs/2607.23332) | AllocBench: Measuring Online Tool Allocation Capability in LLM Agents | 24 | orig deck | sum |
| [2608.00808](https://arxiv.org/abs/2608.00808) | Turning Interaction History into Execution State: A Runtime Layer for Long-Horizon Coding Agents | 8 | prior | sum |
| [2608.01050](https://arxiv.org/abs/2608.01050) | Don't Offer What Can't Be Done: Deterministic Executability Gating for LLM Skill Selection at Scale | 7 | deck read | sum |
| [2608.02680](https://arxiv.org/abs/2608.02680) | TraceCompiler: Skill-Guided Mining and Compilation of LLM Agent Traces into Mostly Deterministic Workflows | 17 | prior | sum |
| [2608.03836](https://arxiv.org/abs/2608.03836) | Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers | 25 | deck |  |
| [2608.05179](https://arxiv.org/abs/2608.05179) | Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap | 119 | prior | sum |
| [2608.05810](https://arxiv.org/abs/2608.05810) | When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents | 9 | read | sum |
| [2608.06196](https://arxiv.org/abs/2608.06196) | Comparative Approaches to Agent Retrieval over Large Skill Libraries | 9 | select |  |
| [2608.07545](https://arxiv.org/abs/2608.07545) | DarwinX: Evolving Agent Harnesses Through Natural Selection | 33 | deck |  |
| [2608.12851](https://arxiv.org/abs/2608.12851) | Practice Makes Unsafe: Skill Misevolution in Self-Improving LLM Agents | 21 | deck |  |
| [2608.14590](https://arxiv.org/abs/2608.14590) | Toward Safe LLM Agents: A Survey of Specification, Verification, and Enforcement | 28 | prior | sum |
| [2608.18398](https://arxiv.org/abs/2608.18398) | LEDGER: Claim-to-Evidence Trace Graphs for Auditing LLM Agents | 15 | prior |  |
| [2608.24306](https://arxiv.org/abs/2608.24306) | Who is the Agent to Blame? Localizing Faithfulness and Citation Mistakes in Agentic Deep Research | 26 | prior | sum |
| [2608.25091](https://arxiv.org/abs/2608.25091) | Auto-Policy, not Auto-Skill: Compiled Agent Skills for the Physical World | 6 | read |  |
| [2608.25500](https://arxiv.org/abs/2608.25500) | CaSKG: Counterfactual-Causal Skill Graphs for Scalable Agent Skill Retrieval | 11 | select |  |
| [2608.25512](https://arxiv.org/abs/2608.25512) | A Programming Paradigm for Spatiotemporal Composability | 92 | orig deck | sum |
| [2608.25770](https://arxiv.org/abs/2608.25770) | HypoForge: A Self-Improving Multi-Agent Framework for Automated Hypothesis Generation and Testing via Scientific Skill Learning | 9 | prior | sum |
| [2608.27969](https://arxiv.org/abs/2608.27969) | openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents | 19 | prior | sum |
| [2609.01939](https://arxiv.org/abs/2609.01939) | Bonded Recourse for Smart-Contract Settlement of Compensable Agent Side Effects | 9 | read |  |
| [2609.02246](https://arxiv.org/abs/2609.02246) | LLM-as-a-Judge Is Not an Oracle: Why Self-Improving Agents Need Deterministic Guardrails | 20 | deck read |  |
| [2609.05079](https://arxiv.org/abs/2609.05079) | TruthInsightBench: An Evidence-Grounded Benchmark for Automated Evaluation of Open-Ended Scientific Discovery Agents | 27 | prior | sum |
| [2609.05269](https://arxiv.org/abs/2609.05269) | CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls | 20 | prior | sum |
| [2609.05364](https://arxiv.org/abs/2609.05364) | Design Docs Are All You Need: An AI-native Machine-Learning Performance Tool | 5 | prior |  |
| [2609.06366](https://arxiv.org/abs/2609.06366) | AutoKD: Autonomous Knowledge Discovery | 14 | prior | sum |
| [2609.09113](https://arxiv.org/abs/2609.09113) | SAEScientist-Bench: Can AI Agents Conduct Autonomous SAE Interpretability Research? | 41 | prior | sum |
| [2609.09233](https://arxiv.org/abs/2609.09233) | Subagents vs Agent Skills: Executing Reusable Knowledge for Long-Horizon Agentic Tasks | 14 | deck |  |
| [2609.09898](https://arxiv.org/abs/2609.09898) | Grounded Evaluation and Repair for NL-to-PDDL Problem Generation | 16 | prior | sum |
| [2609.16313](https://arxiv.org/abs/2609.16313) | Cognitive Admission Control: Risk-Conditioned Assurance for Consequential Actions in Agentic Distributed Systems | 15 | read | sum |

## Added 2026-09-21: cited in DESIGN.md, abstract checked only

Copied from `capsule-openjiuwen/papers/`. Titles taken from the first page of each PDF.

| id | title | pages | status | summary |
|---|---|---|---|---|
| [2605.09998](https://arxiv.org/abs/2605.09998) | Continual Harness: Online Adaptation for Self-Improving Foundation Agents | 28 | cited |  |
| [2605.30621](https://arxiv.org/abs/2605.30621) | Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents | 24 | cited |  |
| [2606.28374](https://arxiv.org/abs/2606.28374) | Recursive Self-Evolving Agents via Held-Out Selection | 15 | cited |  |
| [2608.05604](https://arxiv.org/abs/2608.05604) | SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries | 28 | cited |  |
| [2608.08453](https://arxiv.org/abs/2608.08453) | What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files | 10 | cited |  |
| [2608.11079](https://arxiv.org/abs/2608.11079) | SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure | 17 | cited |  |
| [2608.18050](https://arxiv.org/abs/2608.18050) | StagedWorkspace: A Versioned Workspace for Knowledge-Work Agents | 25 | cited |  |
| [2608.30785](https://arxiv.org/abs/2608.30785) | SkillZip Pro: Execution-Aware Dynamic Compression of Progressively Loaded Skills for Self-Evolving Agents | 30 | cited |  |
| [2609.01600](https://arxiv.org/abs/2609.01600) | CordisBench: Can Language Models Reason About Component Lifecycles in Dynamic Agent Harnesses? | 13 | cited |  |
| [2609.14119](https://arxiv.org/abs/2609.14119) | Same Name, Different Server: A Security Census of Silent Drift in the Model Context Protocol Ecosystem | 14 | cited |  |
