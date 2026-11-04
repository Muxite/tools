# CC v2 ease-of-use revision

Original transfer checkpoint: `41c709ffdd68367bfc149f2446d37dd140b1c4f5`.

This revision makes semantic checks opt-in. `guarantees` advertises checkable commitments; a normal call invokes no checker. Requested advisory failures/unavailability/exceptions retain valid results. Explicit required checks gate acceptance, with execution and assessment still reported separately.

`Host.run` and CLI `run` seal current code automatically. Session grants can be authorized once and inherited only within the selected capability's effect ceiling. Existing artifact validation, workspace leases, implementation identity and reconciliation remain active. M1's scheduler was not changed.

The result-first fixture saves an artifact with broad JSON metadata, then reviews the same artifact against an explicit acceptance policy. A negative review does not rerun or erase the producer. The 34-test regression suite covers default zero-check behavior, advisory failure/unavailability/exception including SystemExit, required checks, CLI exit status, session scope, automatic source sealing, invocation conflicts and valid partial outputs.

Actual same-machine checks also used the pinned upstream StdioClient, TaskTool/SysOperation and MAPIE. They remain deterministic feasibility checks, not live-model, container-isolation, production deployment or GPU evidence. Original reports remain unchanged; new observations are under `evidence/`.

`before/` and `before-manifest.json` preserve exact pre-revision bytes. `validation.json` records the new test/evidence scope. Current source hashes are refreshed in the transfer inventory with the original hash retained as `baseline_sha256` for changed copies. The original transfer summary and old experiment receipts retain their historical meanings.
