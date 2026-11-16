# 20261112 START HERE RSI Expert Streaming prepresentation

This narrow JiuwenSwarm software factory takes an existing llama.cpp engine and a contract. An agent combines Capability Capsules to inspect it, integrate components, build an image from source, run it in a lab and assess the result. Improvement is the objective, not a guaranteed outcome of every attempt.

**Factory: improve an engine during a task. RSI: improve the reusable capability so a later agent does that engineering task better.**

## Verified baseline

- Repository: https://github.com/Stellven/jiuwenswarm
- Tag: cc-baseline-2026-11-12
- Resolved commit: 4fe167f91c112d7a5db9fba8da92f22d8a19f842
- Feature branch: ai4r/iterative-cc-factory.
- Capsule: engine.expert_streaming@2.0.0.
- Reported runtime checkout: /home/muk/projects/jiuwenswarm on Satay, Jetson Orin Nano Super 8GB.
- Companion engine/lab repository: https://github.com/Muxite/siminfeng at /home/muk/projects/siminfeng. Resolve the exact companion source and recipe identities from build receipts before comparisons; this package does not invent one universal companion pin.
- Work is currently paused. This package starts no jobs and does not resume rendering, builds or inference.

## Read in this order

1. 20261112 RSI Agent Assignment prepresentation.md
2. 20261112 Code First Demo Playbook prepresentation.md
3. 20261112 Evidence Status and Corrections prepresentation.md
4. source/jiuwenswarm/factory/ccs/expert_streaming/cc.yaml and its STREAMING.md, EVIDENCE.md, SOURCE-MAP.md, ONTOLOGY.yaml.
5. The original RSI-HANDOFF.md and RUNBOOK.md snapshots, interpreted using the corrections supplied here.

One agent can use multiple CCs in the same task and decision cycle. There is no one-agent-per-CC requirement. It can combine guidance, components, build tools and evidence tools, return to an earlier capability and revise pending actions. Parallel calls are appropriate only when independent and resource-safe; Satay's heavy jobs remain serialized.

This package includes exact selected source snapshots for reading. It is not a complete runtime, model download, image archive or full evidence export. Original relative links in source snapshots may require the pinned repository. Credentials are excluded.

## First exploration on Satay, after work resumes

Use the existing environment; do not recreate it or reset the active checkout.

    cd /home/muk/projects/jiuwenswarm
    git rev-parse HEAD
    git status --short
    git rev-parse 'cc-baseline-2026-11-12^{commit}'
    .venv/bin/jiuwenswarm factory --help
    .venv/bin/jiuwenswarm factory capsules --plain
    .venv/bin/jiuwenswarm factory story artifacts/factory/evidence/factory-bd173c082bf34ae3b8471938c19b8068 --plain

These commands were checked against source, not executed on Satay here. Prefer exported evidence for initial reading. Run 5's PLAN.txt and records expose revisions without needing its live database. The supported factory plan TASK --rev 13 command requires the original task's factory home.

Use a separate candidate checkout for RSI edits. Keep the baseline tag and presentation artifacts stable.

## Current demo priority

Run 5 is shelved from the presentation. Follow the updated Code First Demo Playbook: selective component application, incremental builds and targeted screens, confirmed evidence for performance claims, and a polished replay plus architecture diagram. The RSI baseline remains unchanged.
