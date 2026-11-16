# DGX Spark software factory: agent context package

Snapshot date: **2026-11-15, America/Toronto**. Some source documents use November 16 UTC; those original names and timestamps are preserved. This is an engineering handoff, not a new presentation, experiment authorization, or claim that every included source is production-ready.

## Start here

The user's intention is to move the active inference-engine software-factory work from Jetson Orin Nano to DGX Spark, use Strata as the working baseline, and run evidence-driven loops that build, measure and improve engines and the reusable methods supporting that work. Build a software factory **using Capability Capsules**, not merely a growing catalog of capsules. The useful product is a reproducible engine/configuration and a trustworthy learning loop, including negative results.

Read these first, in order:

1. [Intent and decision precedence](INTENT.md).
2. [Current state and measured limits](CURRENT-STATE.md).
3. [Factory loop and responsibility boundaries](FACTORY-LOOP.md).
4. [Resume procedure and next milestones](NEXT-AGENT.md).
5. [Evidence map and source authority](EVIDENCE-MAP.md).
6. [Machine-readable handoff](handoff.json) and [source inventory](SOURCE-INDEX.json).

For current detailed engineering, read the captured [connected development](reference/factory-source/docs/architecture/factory/CONNECTED-DEVELOPMENT-2026-11-16.md), [night results](reference/factory-source/docs/architecture/factory/NIGHT-BRANCH-RESULTS.md), [factory loop](reference/factory-source/docs/architecture/factory/INFERENCE-FACTORY-LOOP.md), and [Spark runbook](reference/factory-source/docs/architecture/factory/SPARK-E2E-RUNBOOK.md). Read connected development **after** the development review: it closes some gaps listed in that earlier review.

The reference tree contains selected factory implementation, capsule declarations/materials, tests, deployment files, SSH tools, request records and retained experiment evidence. It is a source/evidence reference snapshot, **not a standalone installed checkout**. Do not execute its historical request files automatically. Obtain a complete compatible factory checkout and admit a fresh bounded campaign.

Run `python DGX-SPARK/verify_package.py` from the repository root to verify every packaged file against the manifest. This checks transport integrity, not the truth of measurements or a new runtime pass.

Large model weights, image tarballs, installed environments, authentication state and runtime databases are excluded. Their source locations and available identities remain in the retained handoff receipts. The original remote work remains untouched.
