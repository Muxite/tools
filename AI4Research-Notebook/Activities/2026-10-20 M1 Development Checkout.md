---
id: activity-20261020-m1-checkout
status: observed
source: Sources/Prompts/2026-10-20-m1-development-checkout.txt
last_reviewed: 2026-10-20
next_action: Qualify Docker in Ubuntu-24.04 before building or launching the supplied image
---
# Separate M1 development checkout

Created [AI4Research-Development](../../AI4Research-Development/README.md) and an independent shallow clone at [jiuwenswarm-m1](../../AI4Research-Development/jiuwenswarm-m1), branch `ai4r_M1`, commit `98bd9d913f9ddae5f0d6a3ae256bff10f25ee743`. Git status was clean. The older JiuwenSwarm repositories were not changed.

The initial full-history clone was interrupted because it was slow; the shallow clone completed. The interrupted Git metadata remains in the sibling `jiuwenswarm-m1-incomplete-history` directory because automatic approval review rejected its removal with “blocked by policy.” It is not the development checkout.

Source inspection found actual M1 capsule workers, host checks, gate code, and a governed Codex subscription path. [[Experiments/First CC Demo]] records the recommended Scientific Evaluation/Verifier, Requirements, and Screening sequence and their dependencies. These are recommendations, not measured CC results.

The installed WSL distro is `Ubuntu-24.04`. A read-only Docker version check reported that Docker was unavailable there. No dependency installation, image build, container startup, account login, model turn, or runtime acceptance test was performed. The supplied `{}` operator configuration is suitable for inspection startup only; governed execution has additional readiness prerequisites.
