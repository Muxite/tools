---
id: cc-v2-10-requests-and-materialization
status: v2-reference-implementation
source: November 4 CC v2 revision
last_reviewed: 2026-11-04
next_action: Qualify selected adapter and consumer evidence policy
---
# Requests and templates · companion

The construction owner is [02 · Factory](02-compiler-and-release.md). `cc-request/2` names desired v2 fields and explicit open JSON Pointers. Instantiate a template, supply real source and answers, validate, then seal a release.

| Form | Callable? | Remaining work |
|---|---|---|
| Brief | No | Produce software; zero CCs is valid. |
| Template/request | No | Resolve named choices and implement. |
| Completed package | After validation/sealing/admission | Bind resources and authority. |
| Sealed release | Under eligible adapter/policy | Call an action, start a served capability or read material. |
| Service instance | Existing execution | Use its API, inspect, stop or reconcile. |
| Running call | Existing execution | Observe/reconcile, do not materialize again after disconnect. |

Preserve fixed fields and request identity. Unexpected privilege, dependency, changed ports or behavior requires a requirement revision. Request text grants no build/network/model/publication authority. The generic resolver fills holes; it cannot invent code or interpret arbitrary constraints.

Return actual source, answers, evidence and release linkage. Incomplete work stays incomplete. Edits after sealing produce a new release. See [01](01-declaration.md) for bindings and [08](08-coding-capsule.md) for native sessions.
