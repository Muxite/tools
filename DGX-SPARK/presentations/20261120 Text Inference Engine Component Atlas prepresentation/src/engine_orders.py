"""Bind the engine construction orders to the artifacts used by real inference."""


def complete_engine_orders(orders):
    """Update the existing work orders before the atlas serializes them."""
    jobs = {job["id"]: job for job in orders["jobs"]}

    def receipts(job_id, **providers):
        required = dict(jobs[job_id]["needs"])
        required.update(providers)
        jobs[job_id]["needs"] = [list(item) for item in required.items()]

    jobs["plan"]["output"] = (
        "Versioned interfaces, fixture seeds and work orders with named producers and consumers. "
        "The plan identifies who supplies the real checkpoint, tokenizer, model configuration, "
        "independent reference and target profile. Each component can start on fixtures while the "
        "checkpoint and target are inspected."
    )
    jobs["weights"]["work"] = (
        "Open the pinned checkpoint from the mounted model directory. Inspect metadata without loading "
        "the full model. Bind model and tokenizer identity, layer order, attention geometry, expert "
        "addressing and vocabulary-head binding, including tied weights when declared. Validate each "
        "required name, shape, type, scale layout, shard and byte range. Read one actual expert slice "
        "and reject a missing shard or truncated range."
    )
    jobs["weights"]["output"] = (
        "Checkpoint and configuration identities, a tensor directory keyed by layer and parameter, "
        "expert ranges and hashes for sample packed blocks. Each binding identifies its shard, offsets, "
        "logical shape, stored layout and type. Unknown architecture fields remain explicit."
    )
    jobs["serving"]["work"] += (
        " Pin the tokenizer files, implementation and template. Check actual prompt IDs, special tokens "
        "and incremental output decoding against a known transcript for that tokenizer revision."
    )
    jobs["reference"]["output"] = (
        "A callable small decoder and independent expected embedding rows, attention rows and "
        "vocabulary logits, including nonzero positions and a cached token step checked against full "
        "prefix recomputation. Record the reference implementation, input IDs, weights and tolerances."
    )
    jobs["state"]["output"] += (
        " Provide the buffer handle and last-use completion interface for asynchronous readers, "
        "and a pressure test that delays completion before attempting reuse."
    )
    jobs["placement"]["output"] += (
        " Publish one ledger in bytes for persistent weights, live KV, scratch, slots, staging, transient "
        "unpacking and headroom. Identify allocations backed by the same physical pages."
    )
    receipts(
        "storage",
        weights="Validated shard ranges and expected bytes keyed by checkpoint, layer, expert and tensor.",
        state="Working-buffer ownership and release rules, including last-use completion on the execution stream.",
    )
    jobs["storage"]["work"] += (
        " Bind each read to its source identity and destination slot generation. Test a short read, "
        "duplicate in-flight demand and delayed device completion. Publish a handle only after the "
        "transfer completes and prevent reuse while a reader still holds it."
    )
    jobs["kernels"]["work"] = (
        "Choose a library operator or a bounded custom implementation for each required projection, "
        "attention, routed FFN and row operation. Record the library revision, target capability, "
        "pack format, shape, strides, alignment and scratch requirements. Compare decoded block values "
        "and kernel outputs separately against independent references for prompt and decode shapes. "
        "Force an unsupported specialization and verify either a qualified fallback within budget "
        "or an explicit unsupported-input result."
    )
    jobs["kernels"]["output"] = (
        "A dispatch table naming actual implementations and dependency versions, device prerequisites, "
        "stream and buffer requirements, peak temporary bytes, and numerical parity at the supported "
        "shape boundaries. The image assembler receives the libraries needed at runtime."
    )
    receipts(
        "assemble",
        weights="Pinned pack and tokenizer identities, layer configuration and validated physical tensor handles.",
        reference="Independent expected intermediate rows and logits, fixed input IDs, tolerances and reference identity.",
        routing="Callable router, expert FFN and inverse-map combiner, with expected IDs, weights and restored rows.",
        placement="Accepted memory ledger, bounded slot and staging sizes, and infeasible-shape behavior.",
    )
    jobs["assemble"]["work"] = (
        "Connect request tokenization, scheduling and batch rows to the generation loop. Bind embedding, "
        "every configured decoder layer, normalization, KV append/read, FFN branches and vocabulary head "
        "to the validated tensors and dispatch table. At a routed layer, send IDs to the cache and row "
        "dispatcher, wait on weight readiness, run expert kernels, restore weighted rows and release "
        "slots after their last device reader. Sample and commit a token, stream decoded text, and pass "
        "the updated state to a second decode step. Exercise stop and cancellation cleanup. Start with "
        "the deterministic fixture. On the pinned pack, compare agreed intermediate rows, logits and "
        "greedy IDs against an independent reference, force a cold expert miss, and measure peak bytes "
        "against the placement ledger with the selected kernels."
    )
    jobs["assemble"]["output"] = (
        "A reviewed source revision, build instructions, identified dependencies and a replay from "
        "prompt through prefill and repeated decode. Record fixture and checkpoint identities, "
        "token IDs, logits and tolerances, cold-read evidence, measured peak bytes, response and "
        "cleanup results. A missing reference, target or pack leaves the corresponding gate open."
    )
    receipts(
        "image",
        kernels="Pinned backend libraries, runtime and device prerequisites, dispatch table and tested fallback behavior.",
        weights="Checkpoint, configuration and tokenizer identities plus expected read-only mount contents.",
    )
    jobs["image"]["work"] = (
        "Build the reviewed revision with pinned toolchain and dependencies. Collect the completed "
        "image and run it on the clean target with the identified checkpoint mounted. From inside "
        "the image verify library loading, device access and pack compatibility. From outside "
        "check readiness and send the frozen prompt. Compare returned IDs or the agreed deterministic "
        "response with the assembly replay, exercise repeated decode and stop, then retrieve the "
        "enabled diagnostics. Record startup failures and unsupported dispatch explicitly."
    )
    jobs["image"]["output"] = (
        "Collected build result with image and archive digests, source and dependency manifest, "
        "model and tokenizer identities, target and launch configuration, external completion "
        "transcript and smoke verdict. The lab consumes this identified result."
    )
    receipts(
        "qualify",
        assemble="Independent reference identity, numerical tolerances, replay inputs and assembly baseline for comparison.",
        image="Collected completed build, immutable image and pack digests, launch manifest and passing external smoke transcript.",
    )
    return orders
