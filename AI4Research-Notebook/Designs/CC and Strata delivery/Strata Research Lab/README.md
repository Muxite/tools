---
id: one-cc-lab-entry
status: proposed-runtime-unverified
source: Sources/Prompts/2026-11-03-one-cc-implementation.txt
last_reviewed: 2026-11-03
next_action: Follow the linked evidence and qualify remaining target-machine checks
---
# Strata Research Lab

Read [the lab walkthrough](guide/Start%20here.md), [the projection and Git source probe](probes/README.md) and [qualification status](guide/Qualification.md). Run the recovery drill with `python -B guide/recovery_drill.py`. Replay the Strata probes with a separate trusted checkout of the recorded revision.

Both workshop attachments carry identical [factory brief](shared/examples/brief.json), [product](shared/examples/product.json) and [evaluation](shared/examples/evaluation.json) bytes. Run `python -B shared/validate.py` from the extracted folder. Install Python 3.10+, jsonschema 4.x and referencing first. Fixture locators represent future artifacts.
