# Inspiration from other software

**Muk's rule: a shipped product outranks a paper.** The framing is "inspiration from other software",
not a literature review — the design is not novel in its parts, and saying so is a strength. Second
rule: **spread the references across the whole document**; do not condense the corporate connection into
one section.

Deliberately **not AI software**. Compilers, databases, build systems, CPUs, CDNs, package registries and
release engineering have all solved these problems, at scale, for decades.

## Citation rules

- **One row, one question.** No two references cited for the same point.
- **The biggest company that actually ships the mechanism**, cited only for what it demonstrably does.
- **Verified from the vendor's own documentation** before it ships. A reference that turns out not to
  work as claimed is worse than no reference.

## The map

All rows below were read in vendor documentation or primary source during the 2026-09-23 research pass,
except where marked.

### Foundation and admission

| Used in | Company | Mechanism | The one question it answers |
|---|---|---|---|
| Declared effects | **Google** | Chrome extension manifest permissions: an extension must list every API it uses in `manifest.json`, and even permissions granted at runtime must appear in `optional_permissions` first | Can a component use something it never declared? No — even a runtime grant must be declared up front |
| Admission before use | **Google** | Kubernetes admission controllers run after authentication and authorization but **before the object is persisted**; any one rejection kills the whole request. `ValidatingAdmissionPolicy` does it declaratively in CEL, with no webhook | Can a thing exist before a declarative check approved it? No |
| The gate's human route | **Google** | Chrome Web Store review combines automated and manual systems. Risk signals — a new developer, large code changes, **dangerous permission requests** such as `<all_urls>` — draw deeper scrutiny, and reviewers verify each requested permission is actually necessary | Which cases reach a human? The ones whose *declared contract* is riskiest — which is what makes the declaration worth having |
| Declared versus observed | **Google** | Kubernetes `spec` versus `status`: writes to the object **must ignore** `status`, which system components update through a separate `/status` subresource. `observedGeneration` records which spec generation the status reflects | Can the party that declares overwrite what is observed of it? Not through the main write path |
| Hash-pinned identity | **Docker / OCI** | An image digest "uniquely identifies content by taking a collision-resistant hash of the bytes", and content *should* be verified against it before use | Is the thing that ran the thing that was checked? Yes, if you reference by digest and verify |
| A schema added to for years | **Google** | Protocol Buffers: old binaries ignore new fields, unknown fields survive a parse-and-reserialize, deleted field numbers go on a `reserved` list and the compiler refuses to reuse them | How does one schema keep growing without breaking old readers? |
| Immutable versions | **PyPI / npm / crates.io** | "Once `package@version` has been used, you can never use it again" (npm). PyPI never reuses a filename. `cargo yank` hides a version without deleting it | Can a published version change after it was checked? No — only superseded, deprecated or yanked |

### Merge

| Used in | Company | Mechanism | The one question it answers |
|---|---|---|---|
| Recurrence triggers a block | **Amazon** | Redshift Automated Materialized Views watch recent queries, extract repeated joins and aggregations as candidates, and **build one only when expected benefit beats the cost to create and refresh it**. Capped at 200 per database; creation stops at 80% storage | Should repeated co-occurrence build a combined unit? Yes, gated by benefit minus maintenance cost, **not by frequency alone** |
| Never on one sighting | **Akamai** | Cache-on-second-hit: an object is cached only on its **second** request within a window, tracked by two rotating Bloom filters. In Akamai's data **74% of ~400M cached objects were used only once** | Should a single occurrence create a stored unit? No, and the cost of getting this wrong is most of your library |
| How much recurrence | **Oracle** | HotSpot tiered compilation promotes a method on fixed invocation and loop-back-edge counts, **scaled by how busy the compiler queue is** | How many observations make something hot? A small fixed count, scaled by load — not a statistical test |
| Keep both forms | **Oracle** | Database query rewrite uses a materialized view **only when the optimizer estimates it cheaper**; otherwise the base tables serve. "Materialized views can be added or dropped just like indexes without invalidating the SQL" | Do the originals stay usable, and who picks? Yes, and a cost-based chooser picks per query |
| Which pairs may merge | **Intel** | Macro-op fusion fuses only the pairs listed in the Optimization Reference Manual (Tables 3-1, 3-2), with per-generation conditions — and the list **shrank**: Ice Lake dropped `INC`/`DEC` and memory-operand fusion | May any adjacent pair be merged? No. The catalogue is explicit, versioned, and gets *smaller* |
| Per-pair preconditions | **NVIDIA** | TensorRT's fusion catalogue attaches a condition to each allowed pattern: "both activations must be ReLU", "FP16 or INT8 I/O, Turing+", "non-negative padding only" | What does a legality rule look like in practice? |
| Validated as a unit | **Oracle** | SQL Plan Management: a new plan enters history **unaccepted**, and the Evolve Advisor test-runs it against the best accepted plan. It is accepted only if it performs **as well as or better**, and is "not usable until the optimizer verifies plan performance" | Is a combined artifact trusted because of how it was derived, or measured first? Measured first |
| Revert what does not help | **Microsoft** | SQL Server / Azure SQL automatic tuning watches affected queries after forcing a plan or creating an index: "any action that didn't improve performance is automatically reverted". It only acts when estimated CPU gain exceeds 10 s | What if the merged unit turns out not to help? Revert it automatically, and require a minimum benefit before acting at all |
| Pin internals | **Google** | Bazel's remote cache keys on a hash of command, inputs and environment; reuse requires an exact match, and only the actions a requested target needs are built | Reuse only on exact content match, rebuild only on demand? Yes |
| A block with its own graph | **Amazon** | Step Functions nested workflows: a Task state starts another state machine, so a whole workflow runs as one step — explicitly "a library of modular reusable workflows" | How is a unit containing its own graph placed? As one node |

**The counter-example worth showing:** Docker's `RUN` cache keys on the **command string**, not on content,
so `RUN apt-get update` can serve stale results indefinitely. That is precisely the drift that pinning by
hash prevents, and it is a one-line argument for `body[].sha256`.

---

## Where we go against the grain

**This section is the most useful thing the research produced, and it stays in the documents.** A design
that has hunted for its own counterexamples is worth more than one that has not.

### 1. "Label for quality, block only for safety" is the minority position

Mature release engineering **blocks and rolls back on ordinary quality signals**, not only on safety:

- **Google SRE error budget policy:** once the budget is spent, the team will "halt all changes and
  releases other than P0 issues or security fixes".
- **Google SRE canarying:** a bad canary means "pause and roll back the deployment".
- **AWS deployment pipelines:** automatic rollback when the high-severity alarm fires during bake time.
- **Spinnaker/Kayenta:** a canary scoring below the marginal threshold fails.

**How the position survives, in sharpened form.** In every one of those systems what is blocked is a
**new change**, and the last known-good version keeps serving. None of them removes a capability outright
and leaves the user with nothing. So the rule becomes:

> **Block a regression against a known-good version. Label a capsule that has no better replacement.**

Blocking the *only* version of a capability has no support in any of these sources, and that is the case
the schema is actually about. Adopt the sharpened wording everywhere.

### 2. "Nothing is retired by merging" is stricter than industry

Redshift **drops** AutoMVs that are unused or no longer beneficial, and drops them under storage
pressure. Azure SQL drops unused indexes and drops a new index that did not help.

**The correction:** nothing is retired **by the act of merging** — A and B survive the creation of A-B.
But a merged block is an ordinary library member afterwards and can be retired later on evidence, like
anything else. That is both what industry does and what the librarian already does elsewhere in the
schema. Say it that way; "all three coexist forever" was too strong.

### 3. "Build up, never split" has no industry precedent at all

- **LLVM** splits: `HotColdSplitting` cuts cold regions into new functions, and the partial inliner
  inlines only part of one.
- **Oracle** dissolves: view merging inlines a view's body into the outer query and removes the boundary
  entirely, whenever that is cheaper. Compiler inlining does the same to functions.

Hierarchy is routinely **flattened** for optimisation. So "no split operation" is **Muk's design choice**
— made because splitting is complicated and unnecessary when every capsule can exist as a set of one —
and it must be presented as a choice, not as what everyone does.

### 4. Minimum observations: standard for judging, a departure for merging

**Corrected after the second research pass.** Two different minimums were being conflated:

- **A minimum before a quality claim counts is standard practice**, with good precedent:
  - **Envoy** computes no success-rate verdict for a host below `success_rate_request_volume`, and runs
    no outlier detection at all unless `success_rate_minimum_hosts` have enough traffic.
  - **SonarQube** ignores its coverage and duplication conditions until there are at least 20 new lines.
  - **Kayenta** gives "no data" its own metric class, excludes it from the score, and fails the canary
    outright when half or more of the metrics are missing.
  - **Google SRE** puts it arithmetically: at ten requests an hour, one failure is a 10% error rate.

  So `unmeasured` as a first-class state, excluded from the rate, is well supported.
- **A minimum before *merging* is the departure.** For deciding to build a combined unit, everyone uses
  **small fixed counts** plus a **benefit floor**, then validates and reverts — HotSpot's invocation
  thresholds, LuaJIT's 56 iterations, Akamai's second hit. None waits for statistical confidence, because
  their observations are cheap. Ours are rare and expensive, so the caution moves to the front and a
  person approves. That is the part with no precedent.

**A further caveat:** Optimizely's sequential testing (mSPRT) is designed so results can be checked at
any time *without* a sample size fixed in advance, which weakens "a fixed minimum N" as universal best
practice. Unverified — a search summary only, so do not cite it without reading the whitepaper.

### 5. Required-ness belongs in the gate, not in the schema

**Protocol Buffers removed `required` on purpose.** Its guidance is to write `// required` as
documentation instead, because a required field can become unnecessary later but can never be removed.

This is direct counter-precedent to marking fields required *in the schema* — and it is exactly what "one
schema, progressively activated" should mean: **the schema marks nothing required; the gate's policy
epoch decides what is enforced**, and that policy is versioned and can be relaxed. Fold this into §0.7.

### 6. A mutable name over an immutable hash

Docker tags deliberately move, on top of digests that never do. The right shape is a **name for people
and a hash for the gate** — which `identity.name` plus `identity.body[].sha256` already is.

### 7. Yank is soft, and is not revocation

PyPI and crates.io still install a yanked version when it is pinned or locked, and a yank can be
rescinded. So deprecation and revocation are genuinely different mechanisms, and the schema is right to
separate them — but nothing in these registries provides the hard kill switch, so revocation is ours.

### 8. A human route is a property of the tier, not of the gate

Apple notarization is fully automated; App Review is not. Same company, two trust tiers, two gates. So
the human route should attach to the **trust level**, which is what provisional versus certified already
does.

### 9. Admission does not cover use

Kubernetes admission control runs on create, update and delete — **reads bypass it entirely**. Admission
governs entry, not every use. The design deliberately checks at *both* admission and dispatch, so this
is a place where it goes **beyond** the precedent rather than following it, and should say so.

### 10. Nesting is sometimes forbidden outright

Redshift AutoMVs may not reference other materialized views — no MV of an MV. If a merged block A-B may
later merge with C, the design goes beyond that precedent. Record it as an open risk.

---

## Where research is still cited

Second, and only where industry does not cover it: **AllocBench** (2607.23332) for why the party that
proposes a build must not be the party that builds it, and **Cordis** (2608.25512) for the boundary of
composability.

## Dropped for want of evidence

- **Apple App Store entitlements and App Review** — Apple's pages do not state whether review is human or
  automated, so they do not support the human-route claim. Chrome Web Store does, and is used instead.
- **Android permissions** — the requirement to declare is documented; what happens on an undeclared
  request is not. Chrome extensions cover the same point with better sourcing.
- **Meta Gatekeeper** and **Amazon Mechanical Turk gold questions** — still unverified; do not ship until
  a primary source is read.

---

## Second research pass: what changed (2026-09-23)

### New support

| Position | Precedent |
|---|---|
| Over-blocking is its own failure | **Envoy** panic threshold, 50% by default: with too few healthy hosts it disregards health status entirely and balances across all of them. `max_ejection_percent` refuses an ejection that would breach a cap |
| Deprecate and revoke are different | **Kubernetes** probes: a failed *readiness* probe removes a pod from Service endpoints while it keeps running; a failed *liveness* probe restarts it |
| `unmeasured` is a first-class state | **Kayenta** "no data" class, excluded from the score |
| Grading the grader | **PIT** mutation testing seeds faults and measures which the *test suite* catches; **AWS CloudWatch Synthetics** runs scripted known-input canaries on a schedule |
| Progressive activation | **AWS** one-box → waves, with bake times of at least 1h, 12h and 2–4h, and a default 4–5 business days to all Regions |
| Undo is semantic, not real | **Sagas** (Garcia-Molina & Salem, 1987): a compensating transaction "undoes, from a semantic point of view… but does not necessarily return the database to the state that existed", and "no effort is made to notify or abort transactions that might have seen the results" |
| Name the point of no return | **Microsoft** Azure saga pattern: the **pivot transaction**, after which steps must be retryable and idempotent, and "compensating transactions might not always succeed" |
| Exactly-once stops at the boundary | **Kafka/Confluent**: an RPC to an outside store "would not be guaranteed exactly once" |

### New contradictions

**11. Nobody promises that unloading happens.** POSIX says a successful `dlclose` does not guarantee the
symbols are gone; musl makes it a no-op; Java makes class unloading optional; .NET unload is cooperative
and may never complete; OSGi keeps the class loader until dependents refresh; **Erlang purges old code
by killing the processes still running it**; a forced Linux module unload taints the kernel. "Uninstall"
must mean *no longer routed, and drained* — never *gone*. This is now the M5 framing.

**12. A failing judge is removed, not labelled.** Crowdsourcing removes a worker who falls below the
accuracy threshold on hidden test questions and discards their judgments. Keeping a failing checker in
service behind a warning has no precedent. So the labelling rule stops at the judge: label the capsule,
remove the judge.

**13. Feature toggles are inventory with a carrying cost.** Hodgson's article is explicit, and cites
Knight Capital. "Declared but inert" fields are the same debt, and the schema should expect to retire
toggles rather than accumulate them.

### Still unverified — do not ship

Appen's test-question thresholds (help pages 404), the OSGi classloader-leak reading, the exact ordering
of Kubernetes pod shutdown, and Optimizely's mSPRT.
