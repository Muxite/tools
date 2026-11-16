# Spark factory handoff — 2026-11-14

Copy these files off the Spark together:

- `spark-factory-review.tar.gz` and its `.sha256` sidecar: analysis, exact focused
  source overlay/tests, verified evidence exports, benchmark data/licenses, small
  model pack descriptors, dependency manifests and cleanup audit.
- `spark-arm64-images.tar.gz` and its `.sha256` sidecar: agent, builder, CLI and
  qualified Strata images, including their shared layers. Needed for native runtime
  reuse; not needed just to review results on an x86 laptop.
- `image-archive-verification.json` and `handoff-verification.json`: local receipts.

No remote transfer has been performed. Keep originals until the destination copy
passes verification. From the destination directory:

```sh
sha256sum -c spark-factory-review.tar.gz.sha256
sha256sum -c spark-arm64-images.tar.gz.sha256
tar -xzf spark-factory-review.tar.gz
python3 spark-factory-review/verify.py
```

Verification requires only standard Python 3, not CUDA, a virtualenv or the Spark.
The archive was extracted and checked locally before handoff; repeat these checks
on the destination. No existing source checkout or mission state is modified.

Start with:

1. `source/docs/architecture/factory/SPARK-HANDOFF-ANALYSIS.md`
2. `source/docs/architecture/factory/SPARK-DEPENDENCY-CLEANUP-AUDIT.md`
3. `source/docs/architecture/factory/SPARK-FACTORY-EXPERIMENTS-2026-11-14.md`
4. `evidence/spark-prefill-factory-002-loop-2/` for the complete measured comparison;
   `evidence/spark-factory-agent-review-001/` for the real agent's next design.

## Source and dependencies

`source/` is an exact focused working-tree overlay, including authored untracked
files. `SOURCE-PROVENANCE.json` lists the full-project base commit and file hashes.
It is not the entire WorkSwarm repository or its history. Obtain that repository
at the recorded commit, then overlay these paths in an isolated checkout to resume
full-project development. Preserve the supplied package files instead of replacing
its lock with an unbounded install of all optional project dependencies.
The original `.git` worktree pointer, personal profiles and environments are absent.

The ARM64 agent image also contains the packaged full agent runtime; the CLI and
builder are separate. To import images on a compatible Docker host:

```sh
gzip -dc spark-arm64-images.tar.gz | docker image load
```

Verify loaded image IDs against `receipts/final-role-images.json`,
`receipts/factory-loop-cli-image.json` and the image archive verification receipt.
The receipt distinguishes OCI index digests from configuration digests: this
Spark daemon reports index IDs; another Docker image store may display config IDs.
Use the recorded descriptor/config/layer identities rather than treating these two
representations as interchangeable. Loading is not validation that GPU inference
works on another architecture/driver.
Actual engine reruns require a compatible GB10/ARM64 CUDA host, NVIDIA container
runtime, a configured host queue, model assets and independently supplied agent
credentials. No credentials, driver installation or live queue state are bundled.

`host-tools/jobq` includes the resolved standalone queue executable and its origin
hash, not the shared queue's jobs. Configure a fresh queue on a new machine; never
start a worker against copied historical queue state. Some launcher defaults still
use Spark-specific paths, documented in the audit. Agent dependencies are captured
inside the image and in `receipts/agent-closure.json`; compiler dependencies are in
the builder image and `receipts/builder-toolchain.json`.

The model pack is descriptors/tokenizer/profile only. The six GGUF files total
256,811,098,112 bytes and are NOT bundled; see `assets/deepseek-full-identity-v1.json`.
Do not silently edit historical paths/contracts and call the result a replay.
Create new asset inventories/contracts/task IDs for relocated execution, preserving
original evidence and hashes. Evidence exports are read-only snapshots, not a
resumable raw mission database. Source secret-shaped test fixtures are deliberately
preserved with reviewed hash-bound explanations in `SOURCE-SCAN.json`; actual
credential profiles are excluded. Evidence exports are sanitized and may differ
from raw artifact hashes, with mappings recorded in each `artifacts.json`.

## Cleanup

Nothing was deleted. Review the cleanup audit's exact paths and conditions. First
verify both archives offhost. Keep the mission store and original experiment data
until any resume/forensic requirement is retired. Test scratch is a separate class
from real results. Build contexts are candidates after archived images and source
manifests are verified. The 11.28 GiB GPT-OSS private copy is unrelated to the current
DeepSeek run but supports historical probes; removing it retires that local replay.
Do not prune the shared Docker daemon or delete external environments/queues/models.
The runtime still has path dependencies outside the project; images reduce this
coupling but relocation has not been qualified on a second host.
