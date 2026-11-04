# Continue the CC v2 task

## Intent

Build a small, useful CC standard that works with coding agents and scientific methods. The team is mostly undergraduates; keep authoring and execution simple. A capsule is a versioned package; its named capabilities are callable actions. Calls bind real inputs/resources; receipts describe actual execution and evidence.

Support native commands, images and host-registered JiuwenSwarm subagents through the same logical interface. Start trusted-local; add isolation where required. Keep JSON broad and schemas optional. A coding subagent should edit its assigned worktree using normal tools, then return changes and observed checks. Requests/templates can describe missing implementation decisions; executable releases cannot contain unresolved mandatory choices.

The Factory can wrap a paper repository into methodological capabilities. Its software product, such as an inference engine, may contain zero reusable CCs. Product delivery and reuse of tools are distinct. The Lab must verify the actual loaded binary/configuration/generation before scoring an engine.

## Current implementation

Start at [CC v2](<../AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/README.md>) and [the evidence page](<../AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/05-examples-and-conformance.md>).

- `cc: "2"` has one `capabilities` map, shared bindings, plain arguments and artifact references.
- The local host supports sealing, validation, native/image dispatch, registered native delegates, SQLite call identity, workspace leases, explicit reconciliation and optional semantic checks.
- Source/executable hashes, runtime identity, input/output references, actual workspace changes, assurance and observation limits appear in receipts.
- Replay safety uses host-generated keys before transport retries. Unknown effects are not automatically replayed. Late replies cannot overwrite operator reconciliation.
- Three independent adversarial reviewers found fifteen issues across development cycles. Fixes were replayed and independently checked. Review evidence is in the notebook's November 4 CC v2 batch.

## Recorded results and limits

| Demonstration | Actual source-machine result |
|---|---|
| Local reference host | 21 regression tests passed. |
| MAPIE | Fit/calibrate → model artifact → intervals → evaluation. Coverage 0.94 on 50 heldout synthetic samples; mean width 1.7601173275650268. |
| Negative scientific result | Labels shifted by +1000 yielded valid execution and coverage 0.0. |
| Upstream MCP | Real pinned OpenJiuwen StdioClient discovered/invoked generated tools; duplicate invocation returned the same call. |
| Coding subagent | Real pinned TaskTool/SysOperation delegation repaired code and executed two assertions while preserving dirty tracked/untracked files. Deterministic child driver, no live LLM. |
| Factory/Lab handoff | Actual pinned Strata manifest reader/full verification accepted a synthetic native product and rejected tampering. No engine loading or inference. |
| Container | Actual execution attempted; worker never started because Docker Desktop could not access/rename `sailor-ingest.sock`. |

The environment is reduced to the tested import paths. It is not a complete JiuwenSwarm installation; three unused declared dependencies were absent in the recorded environment. Windows results are not evidence of Linux, ARM64, CUDA or GB10 success. Native trusted-local has no OS isolation. Callback code identity does not capture all remote-model configuration or closure state.

## Set up on the new machine

Clone this repository, use Python 3.12, and run from its root:

```text
python TRANSFER/verify_transfer.py
python TRANSFER/bootstrap.py --profile basic --run
python TRANSFER/bootstrap.py --profile integration --plan
python TRANSFER/bootstrap.py --profile integration --run
```

`basic` installs the small local-host requirements and runs protocol/request regressions. `integration` creates `research/cc-v2-environment`, fetches exact source commits, installs the recorded dependency versions and reruns the deterministic scientific/upstream/product demonstrations. It also fetches the exact Strata source into `Strata/`, which the existing experiment harness expects. The setup refuses to overwrite a different or dirty checkout. The dependency projection adds OS markers for Windows-only packages; cross-platform installation remains to be verified on the target machine.

Do not reuse a source-machine virtual environment or serialized interpreter paths. Rebuild it. Model pickle artifacts are trusted demonstration material; a matching digest does not make untrusted pickle safe. Fetch upstream code by the pins in [sources.json](sources.json), not branch names. Missing credentials, wheels or unavailable commits must remain explicit setup failures.

## First work on the stronger machine

1. Verify the transfer and reproduce the basic suite. Establish target OS/Python/dependency identities.
2. Run the pinned integration profile, then execute the container equivalent with a working Docker engine. Keep image/native results and enforcement evidence separate.
3. Connect an actual configured JiuwenSwarm coding agent to the generated tools. Qualify permissions, session identity, cancellation and model/data-provider settings; deterministic dispatch is the baseline, not proof of live-agent behavior.
4. Run one useful paper-method or coding task end to end. Extend v2 only for a demonstrated unmet case.
5. For Strata/Muse, deliver a real native component/image/source build, verify the loaded candidate, pin model/workload/environment, and collect raw measurements under frozen criteria. Preserve local patches, restart and process-generation lineage.

Keep production tenancy, remote A2A recovery, general background pause/resume/cancellation, full Factory automation and GPU measurement as distinct qualification work. Do not add mandatory author fields merely to describe a future host feature.

## Transfer scope

The notebook's authored notes, research/design history, prompts, executable CC examples, reviews, supporting diagrams, Office documents, and bounded source packages are copied with byte hashes. The latest reviewed November 3 decks are also under `Presentations/2026-11-03`; two RSI reference designs are under `Supplementary`.

[source-files.json](source-files.json) records every copied source path and SHA-256. [excluded-files.json](excluded-files.json) records omitted research-paper PDFs, two bulk duplicate archives, migration history and other excluded files. Credentials, private planning working directories, caches, installed environments, runtime databases, external repositories and model weights are outside this transfer. Original sources remain on the old machine.

The original 62 MB migration inventory is retained as [a compressed historical receipt](historical-migration-manifest.jsonl.gz). It describes the original workspace, including excluded/linked sources; it is not a claim that all those sources are present. Historical archive links and Windows paths remain unchanged. Use current note entrypoints and the current CC folder for maintained navigation. The original full-vault validator also has one known unrelated broken repository link.

This is a normal content-replacement commit. Previous toolbox code remains recoverable from Git history at `bfd34b69f1823fece8e95645f7bea3b442f226bd`. No history rewrite or force push is needed.
