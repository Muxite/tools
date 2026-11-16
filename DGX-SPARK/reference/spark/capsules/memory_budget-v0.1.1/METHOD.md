# Memory budget and SSD qualification

Candidate material capsule, not centrally promoted. A process memory cap is not evidence of SSD inference. This method qualifies the experimental boundary before interpreting an optimization.

## Inputs and execution

Pin model bytes/hash, engine image, workload, quantization, CPU/GPU placement, context, sampler and runtime switches. Disable swap for the owned container, apply a finite timeout and CPU budget, and run through the host queue. Observe memory.current, memory.peak, memory.max, memory.events, memory.stat and io.stat with output-progress timestamps. Retain failures and OOM status.

First compare the ordinary loading path with mmap and weight repacking disabled where supported. Do not assume these are semantically or operationally identical; verify output and record the difference.

## Page-cache ownership trap

Shared file pages can be resident and charged outside the new container. In the recorded shared-file tests, the no-repack path showed approximately 391 MB of charged memory despite an approximately 12.1 GB model. Those fast runs did not qualify out-of-memory SSD behavior.

When this confound matters, create one owned model inode, verify byte identity, fsync it, then use POSIX_FADV_DONTNEED only on that owned file before an isolated run. This is an explicit, justified exception to avoiding model duplication. Do not evict shared model files or the whole host cache. Advice is not a guarantee; require observed device reads, especially after response output begins.

## Evidence and limits

On Spark, GPT-OSS-20B MXFP4 at SHA256 27cd6c432c7672cb812a92f611cf3ba7bbc35928262bb1e1253ff4ee6ae35901 loaded with normal settings at 16 GiB but was OOM-killed at 8 GiB. With --no-repack -lm mmap, the owned-file 8 GiB test generated 64 tokens and recorded block reads during output. Full results and repetitions belong in the evidence index.

This qualifies CPU inference with a constrained budget, not full GPU allocation accounting, general accuracy, optimized SSD scheduling or scaling beyond physical RAM. Preserve a resident control and compare complete output. GPU allocation accounting and genuinely oversized models remain separate qualification gates. Sampled output timing is not exact per-token I/O attribution.
