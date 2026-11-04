---
type: template
tags: [process]
---

# Issue template

*Reference, not for review: a proposal pending Xiaoyang's own template.*

> **Owner:** Xiaoyang (coding lead). Drafted by Muk, 2026-09-25; his code SOP covers how code is written.

**The idea.** An issue is written in the shape of a Capability Capsule [Declaration](../schemas/declaration.md). A Declaration already says what a unit takes, gives, needs, changes and guarantees, and how each promise is checked. That is exactly what a coder, human or AI, needs to build one unit in isolation, and what the reviewer needs to verify it.

There are two kinds of issue, and they are not the same shape:

| Issue builds | The block is | Validated by |
|---|---|---|
| **a capsule** (a seed capsule, a model capsule) | its real `cc.declaration.v1` Declaration, exactly as it will be admitted | the `cc/schema` validator, once regenerated from the signed Declaration page (the v2.10 `validate_capsule.py` does not apply) |
| **control code** (a module: the evaluator, freeze, a gate) | a **work order**: the same section names, its own simpler shape. It is *not* a Declaration and is never admitted ("nothing that decides is a capsule") | review |

**Who verifies what.** Every check in the issue carries `verified_by`, a field that exists only in issues:

- `builder`: the coder writes the test and runs it. Evidence the unit works, never proof on its own.
- `reviewer`: Muk runs it at review. The coder is told what it checks, not how.

No unit is its own final judge. For a capsule, `verified_by` is stripped when the Declaration is admitted; the check's `author` field stays as the Check schema defines it.

**The flow.**

1. Muk writes the issue. It may only depend on **signed** [schemas](../schemas/schemas.md). An issue that needs an unsigned schema waits, and says so under "Blocked by".
2. The coder builds to it, writes a test for every `builder` check, runs them and pastes the evidence.
3. Muk re-runs the `builder` checks, then runs the `reviewer` checks.
4. All pass: merge. Any fail: back to the coder with the failing check ids.

If the coder finds a schema wrong or unclear, **they stop and comment on the issue**. They never change a schema or guess around it.

Copy one of the two blocks below into the new issue.

---

## A. Capsule issue

````markdown
# [capsule] <capsule name>: <one line on what it does>

**Component:** <link to its section on the part page>  ·  **Build step:** B1 | B2 | B3  ·  **Size:** S | M | L
**Schemas it depends on (signed):** cc.declaration.v1, cc.types.v1, cc.check.v1, ...
**Blocked by:** <issues, or unsigned schemas> | none

## Why
<Two or three lines: what cannot be demonstrated without this capsule.>

## Declaration (cc.declaration.v1; the author computes every file hash, and admission hashes the files again and refuses a mismatch)
```json
{
  "schema_version": "cc.declaration.v1",
  "identity": {
    "name": "<e.g. seed.count-spaces>",
    "kind": "tool | skill | prompt_section | mcp | a2a | subagent | agent_template",
    "carrier": {"ref": "<path relative to the capsule root>:<symbol>", "sha256": "<sha256 of that file>"},
    "summary": "<one line; no step, stage or capsule names>",
    "lineage": {"parent": null}
  },
  "ports": {
    "inputs":  [{"name": "<n>", "type": "<a cc.types.v1 type>", "required": true}],
    "outputs": [{"name": "<n>", "type": "<a cc.types.v1 type>", "check_id": "<check id>"}]
  },
  "needs": {
    "when": [{"id": "<n>", "path": "inputs.<n>", "op": "present", "evaluable_at": "both"}],
    "network": "none"
  },
  "changes": {"effect_class": "pure | read_only | idempotent | compensable | irreversible", "effects": []},
  "guarantees": {
    "checks": [{"id": "<check id>", "anchor": "deterministic", "target": "ports.outputs.<n>",
                "over": "outputs", "applies_at": "admission | node | both", "author": "<who wrote the check>",
                "runner": {"ref": "<test runner>", "sha256": "<sha256 of the runner file>"},
                "description": "<what passes>"}]
  }
}
```

## Who verifies each check
| check id | verified_by | what it checks |
|---|---|---|
| <id> | builder | <one line> |
| <id> | reviewer | <one line> |

## Out of scope
- <what this issue must not do, so it stays isolated>

## For the coder
- Build only what the Declaration says. Do not edit anything under `schemas/`.
- Write a test for every `builder` check, named by its check id; put each test case inline in the Candidate's `tests`.
- Run them and paste the command and its output under "Evidence".
- A schema is wrong or unclear: stop and comment here.

## Evidence (coder fills in)

## Review (architect fills in)
- [ ] the Declaration validates against cc.declaration.v1 and the current policy epoch
- [ ] every `builder` check re-run and passes
- [ ] every `reviewer` check run and passes
- [ ] merged, and submitted to admission as a Candidate
````

## B. Module issue (a work order)

````markdown
# [module] <module name>: <one line on what it does>

**Component:** <link to its section on the part page>  ·  **Build step:** B1 | B2 | B3  ·  **Size:** S | M | L
**Schemas it depends on (signed):** <every schema it reads or writes>
**Blocked by:** <issues, or unsigned schemas> | none

## Why
<Two or three lines.>

## Work order (not a Declaration)
```yaml
identity:
  name: <module name, e.g. cc.evaluator>
  code: <path:symbol>
  summary: <one line>
ports:                        # the interface; types are schema ids or plain JSON types
  inputs:  [{name: <n>, type: <e.g. cc.plan.v1, or string>}]
  outputs: [{name: <n>, type: <...>}]
needs:
  signed_schemas: [<cc.x.v1>, ...]
  issues_merged: [<#n>, ...]
  external: [{ref: <e.g. agent-core>, pin: <commit>}]
changes:
  writes: [<records or stores it writes, by schema id>]    # empty for a pure module
guarantees:
  checks:
    - {id: <check id>, verified_by: builder | reviewer, description: <what passes>}
estimate: <time>
```

## Out of scope
## For the coder
(as in A)
## Evidence (coder fills in)
## Review (architect fills in)
- [ ] every `builder` check re-run and passes
- [ ] every `reviewer` check run and passes
- [ ] writes nothing outside `changes.writes`, and no field outside the schemas it names
- [ ] merged
````

See the [filled module example](example-evaluator.md).
