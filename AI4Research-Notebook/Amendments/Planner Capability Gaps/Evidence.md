---
id: amendment-pcg-evidence
status: source-snapshot
source: OpenJiuwen exact pin 9e3390195a9ea15235b2b5f7412cb2aa440622cc and M1 source commit d3d7f565c6c05ccf764fe0780fde149b7dc89b95
last_reviewed: 2026-10-21
next_action: Verify all source hashes at implementation checkout
---
# Portable evidence snapshot

Exact OpenJiuwen pin exists locally as Git object; it was inspected read-only with `git show` and `git ls-tree`, no checkout or fetch. Hashes below cover full source blobs at exact revisions.

## Native pin guard, M1 (`jiuwenswarm/research/native.py:16-28`)

M1 source blob SHA-256: `9757e216631d0042b9b666c53df3e7fac52d394f935cca263644e03f63e832cb`

```python
OPENJIUWEN_COMMIT='9e3390195a9ea15235b2b5f7412cb2aa440622cc'
direct=json.loads(distribution.read_text('direct_url.json') or '{}')
if direct.get('vcs_info',{}).get('commit_id')!=OPENJIUWEN_COMMIT:
    raise ResearchError('native_pin_mismatch', ...)
```

## Native Leader run-once semantics (exact pin, `openjiuwen/agent_teams/harness/native_harness.py:288-297`)

Blob SHA-256: `daa6860671ec9f627687c12f5d0aa969ed40d61d88305ab242cd2e3f14eae92d`

```python
async def run_once(...):
    """Run one non-streaming execution ...
    Bypasses the supervisor entirely ... plain DeepAgent.invoke — the spec's
    enable_task_loop decides whether it runs a single ReAct round or self-drives
    the full task loop ...
    """
```

M1 deliberately sets `enable_task_loop=False`, tool/MCP/subagent/skill lists empty, `max_iterations=1`, and verifies one audited bridge call in `native.py:117-145` (blob hash above).

## Workflow backend/reuse seam (exact pin)

`openjiuwen/agent_teams/workflow/engine/backends/base.py:39-47,118-135` SHA-256 `006a61ef0bc5e013803c942ea0282aa9ef489bde72bbc3bc077ccdce1b620780`; `engine/runner.py:294-312` SHA-256 `c3559c5b1de4f9d76727c80e99f7a317032d1f3d9e42376c30aa09f631bd1601`.

`AgentBackend.run(prompt, opts, schema_json, call_key=...)` is the single-shot IO seam; `run_workflow` accepts backend, resume/journal/WAL, strict, progress, cap, agent gate, budgets, abort event, and run id. M1 reuses the backend/workflow and intentionally forces serial frozen-order dispatch with retries disabled and persistence/replay off.

## Native Symphony capability interfaces (exact pin)

`openjiuwen/symphony/interfaces/capability.py:13-34` SHA-256 `03f380ae13b2f484262c12ca3f74cc273234f330855b8b495101811106986621`: asynchronous inventory + snapshot, with an optional atomic inventory/snapshot pair. `models/capability.py:61-93` SHA-256 `3429ad1f8c8dbdfde58ec27a963ee9896e80131d58a060d2874c4b9682cdcc74`: descriptor includes content hash, ports, classification, `available`, metadata; it has no typed preconditions/effects. `models/fingerprint.py:29-45,111-122` SHA-256 `c1da058f793e21976cb8b63fc803fbfe077304eb9d9c29ee93a118fb0bbcb5c4`: versioned semantic/quality view and graph identity. `orchestration/graph/build.py:157-165` SHA-256 `60d6d5c2a15836bd2458de5b053711f53eee099cd27df6256c79e9edbf602d98`: graph registry admits only `skill`, `subagent`, `agent` kinds.

These APIs exist in the pinned dependency; M1 already adapts scan and fingerprint results through `jiuwenswarm/symphony/adapter.py`. They are not an execution sandbox, effect monitor, or gate authority.
