# 2606.07591 · ResearchClawBench: A Benchmark for End-to-End Autonomous Scientific Research

InternScience, Shanghai AI Laboratory · arXiv Jun 2026 · 73 pp (14 body)
Read: p1-9 (motivation, related work, construction, harness, metric). Results tables read at abstract level

## Summary
A benchmark of **40 real research tasks across 10 scientific domains** where each task
is built from a published paper that is **hidden** from the system. The system gets the
question, ~4 related papers and the **raw data**, and must produce code, intermediate
results and a report. Scoring uses expert rubrics anchored so that **50 = matches the
target paper** and above 50 = new discovery (Reference-Anchored Discovery Score, RADS).

## How it works (p5-9)
- Task τ = (question q, literature L, raw data D, hidden target paper p★, evaluation
  artifacts A); output y = (code/process π, intermediate outputs o, report r) (p6)
- Domains: astronomy, chemistry, earth, energy, information, life, materials, maths,
  neuroscience, physics; tasks are diagnostic analysis or metric optimisation
- **Construction by domain experts**: pick papers with clear questions and accessible
  data, rewrite into executable tasks, build **weighted rubrics** from the target paper's
  key artifacts, **re-run experiments to check the rubric is reproducible**, cross-check
  between experts (p7-8, Fig. 3)
- **ResearchHarness**: a small ReAct loop with web, file and shell tools (search via
  Serper, fetch via Jina, PDF via MinerU), compaction at 128k tokens, so native LLMs can
  be compared without their own scaffolds (p8)
- Judging: rubric items scored by an LLM judge, plus supplementary dimensions
  (comprehensiveness, depth, instruction following, professionalism) (Fig. 2)

## Results (p2-3)
- 7 autonomous research agents (incl. Claude Code, Codex, OpenClaw, EvoScientist, ARIS,
  nanobot, Research Claw) and 17 native LLMs
- **Best agent Claude Code: 21.5**; best-per-task agent frontier mean 24.6; best LLM
  Claude-Opus-4.7: 20.7; LLM frontier mean 26.5, against 50 for re-discovery
- Failures concentrate in **experimental protocol mismatch, evidence mismatch, missing
  scientific core** (p2)

## Limitations
- 40 tasks; rubric scoring still goes through an LLM judge, though against expert,
  reproduction-checked criteria
- Anchoring on the target paper can penalise valid different routes (the authors give
  room above 50 for this)

## Relevance
- REPORT.md §3.7: the best candidate for AI4Research's first external benchmark, because
  it scores **produced artifacts against expert criteria derived from a hidden paper**,
  from raw data, across domains, not an LLM's taste in isolation
- "Evidence mismatch" as a top failure is exactly the property AI4Research's evidence ABI
  and verdict gates target; a run here would test whether that pays off
- Named SoTA research agents are general coding agents (Claude Code, Codex), which is
  also where the openJiuwen harness competes
