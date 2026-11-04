---
title: Resource-aware planning research
status: exploratory
captured: 2026-10-16
tags:
  - planning
  - resources
  - evidence
---

# Resource-aware planning

**Current focus, October 19:** AI4Research is not built. Start with [pre-build recommendations](prebuild-recommendations.md): what to focus on, how to revise existing experiment families, questions and provisional answers, needed evidence, and approaches to avoid. Today's work requires standalone profiling evidence, not AI4Research integration.

This folder is an exploratory discussion space for project-wide task, machine, and resource planning. Its notes collect questions and evidence for later review; they do not set requirements, architecture, or implementation authority. The imported GPU report is one-machine evidence, not a measurement of this repository's current machine or a validated planner model.

Start with [planner implications](planner-implications.md) for candidate planning questions, then read [evidence and next questions](evidence-and-next-questions.md) for the dated evidence log and a measurement agenda.

The October 19 direction focuses on predicting low-level hardware demand from historical task vectors and informing future chip development. Read the [copyable experiment-agent brief](experiment-agent-brief.md) and [literature review](literature/README.md). Those documents use project sources and primary literature; they do not use the imported artifact as evidence.

The hardware-specific follow-up is the [GB10 profiling plan](gb10-profiling-plan.md). It treats the GB10 as the primary Linux/aarch64 UMA target, the Ryzen 7 3700X + RTX 5070 Ti as a related but non-matched Blackwell system, and connects OCI capsule execution, Linux cgroups, Nsight/DCGM signals, and future AI4Research profile records. It is exploratory research; it does not amend the product architecture or sidecar contract.

The [presentation outline](presentation-outline.md) leads with chip-development value and records the live deck's Page ID for future updates.

The captured source bundle is [the report](sources/2026-10-16-shared-gpu/report.md), [HTML report](sources/2026-10-16-shared-gpu/report.html), [chart data](sources/2026-10-16-shared-gpu/chart-data.json), and [capture metadata](sources/2026-10-16-shared-gpu/capture.json). The report is imported and not independently validated; its raw gauge ledger, dataset CSVs, and compact traces remain on the other machine.

Use these notes to frame small, discriminating experiments and to record provenance and uncertainty. Promote any future requirement or architecture decision through the repository's normal authority process.
