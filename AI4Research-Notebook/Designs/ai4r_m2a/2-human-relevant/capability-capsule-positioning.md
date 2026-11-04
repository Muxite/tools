---
id: ai4r-m2a-cc-positioning
status: proposed-runtime-unverified
source: ai4r_m2a/3-agent-reference/sources/cc-packaging-request.txt
last_reviewed: 2026-10-30
next_action: Implement the declared packaging and qualification contracts, then attach measured evidence
---
# How to talk about Capability Capsules

[Home](../README.md) · [Full packaging and trust contract](capsule-packaging-and-trust.md)

## Recommended angle

**Portable, vetted capability packages for dependable research agents.** Lead with the freedom of the sandboxed agent and the quality of its available capabilities. Then explain the checks, evidence and repeatable environment that make each package useful. CI is development plumbing and need not occupy the architecture contribution line.

## Short contribution line

Architected Capability Capsules: portable, containerized packages of tools, skills, MCP integrations and bounded subagents, with dedicated verification, declared effects and evidence-based qualification for reproducible agentic research.

## Longer explanation

I designed Capability Capsules to give a sandboxed research agent a broad, dependable set of capabilities. Each capsule packages related tools, skills, MCP integrations or bounded subagents with pinned dependencies, declared effects, guards, acceptance gates and dedicated verifiers. Qualification and recorded performance history govern which capabilities are eligible for a task and at what trust level. Container images support repeatable setup, while explicit lifecycle ownership allows capabilities and their dependencies to be added or removed cleanly.

The same packages are designed for use outside AI4R through ordinary tool, skill, MCP and subagent interfaces. Their evidence and declared change boundaries also support controlled RSI: historical results can guide what to optimize, while protected policy determines what may be changed. The tradeoff is more upfront development and maintenance. The architecture is designed and, according to the project update on 30 October 2026, is being built and trialed; broad accuracy or efficiency gains have not yet been established by capsule-by-capsule benchmarks.

## Research grounding and claim limits

SWE-agent studies how agent-facing interfaces affect software-engineering performance. This motivates attention to capability interfaces and feedback, not a claim that CC packaging has reproduced its results. [SWE-agent, Yang et al.](https://arxiv.org/abs/2405.15793)

Reflexion evaluates using feedback retained across trials to improve subsequent decisions. This supports investigating evidence-informed improvement; it does not validate our trust thresholds, RSI permissions or autonomous promotion rules. [Reflexion, Shinn et al.](https://arxiv.org/abs/2303.11366)

Docker documents digest-pinned image selection. That supports identifying the exact shipped environment, but an identical image is not proof of identical scientific results or a reproducible rebuild. [Docker image pull documentation](https://docs.docker.com/reference/cli/docker/image/pull/)

The synthesis into CC packaging is our design proposal. Say “research-informed design, under implementation and trial,” not “proven to increase accuracy.” State measured task-specific gains only when the relevant matched evidence exists. Broader spatiotemporal composability is intended future work, deliberately deferred; present clean add/remove as the implemented target of this milestone, not as that broader achievement. The author's report of active implementation does not change this package's unverified runtime statuses.
