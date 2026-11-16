# Continuing this work

## Active DGX Spark inference-factory work

For the Jetson-to-DGX Spark migration, Strata baseline, current engine experiments and factory loops, read [DGX-SPARK/README.md](DGX-SPARK/README.md), then INTENT.md, CURRENT-STATE.md and NEXT-AGENT.md there. This November 15 context supersedes older setup-only summaries for the Spark work. Follow its source precedence and measurement limits; historical requests do not authorize fresh runs. The remaining instructions below still govern the preserved CC protocol notebook.

1. Read `TRANSFER/CONTINUE.md` and the CC v2 README before making changes.
2. Treat `AI4Research-Notebook` as a preserved notebook snapshot. Its own `AGENTS.md` explains source authority. Original prompts, archive files, historical receipts and v1 snapshots must retain their bytes.
3. Current implementation is under `AI4Research-Notebook/Designs/CC Protocols/reference`. Prefer small, concrete changes demonstrated by use cases. Keep broad JSON unless domain constraints prevent meaningful errors.
4. Use `TRANSFER/bootstrap.py` for workspace-relative setup. Old absolute paths in source-machine receipts are historical. Do not copy credentials, installed environments, weights or runtime databases into Git.
5. Separate declaration validation, local replay, actual upstream invocation, live-agent execution and hardware measurement. Never infer a hardware/image/live-model pass from a fixture.
6. Verify exported bytes using `TRANSFER/verify_transfer.py`. Run the CC protocol/request checkers after relevant changes. The historical full vault migration checker expects the original machine's linked repositories and omitted archives; its result is not the portable CC test result.
7. This repository is public. Keep local configuration and credentials outside tracked files.

The current handoff is a tested feasibility implementation. Production isolation, distributed task lifecycle and actual Spark measurements require further qualification. Do not silently turn a declaration or trusted-local execution into an isolation guarantee.
