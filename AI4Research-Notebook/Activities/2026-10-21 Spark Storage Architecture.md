---
id: activity-spark-storage-architecture
status: completed-documentation
source: Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt
last_reviewed: 2026-10-21
next_action: Inventory the actual Spark and qualify resource admission, shared inference and CPU VM support
---
# Spark storage and shared inference architecture

Captured the exact resource/storage direction. Wrote [[Designs/Spark Shared Services and Storage]] and reconciled the M2 roadmap, VM/container/factory designs, feasibility review and navigation. Previous bytes/hashes are retained in the review batch.

Official NVIDIA guidance excludes supported Spark GPU passthrough. The revised design puts model storage and GPU inference on the host with scoped relays in ARM64 CPU labs. Supplied 2 TB capacity is retained as user-provided configuration; actual filesystem bytes and CPU-guest support are unmeasured. Disk shares total 100 percent including 20 percent free headroom. Unified-memory envelopes, peak reservations, cache targets, reference-aware retention and bounded generalist iteration apply during development.

No Spark connection, download, cleanup, installation, VM/GPU/model trial or deployment occurred. Runtime acceptance remains NOT_RUN. Source/diagram/documentation receipts are in Resources/review-batches/2026-10-21-spark-storage-design. Original sources and unrelated working-tree changes were preserved.
