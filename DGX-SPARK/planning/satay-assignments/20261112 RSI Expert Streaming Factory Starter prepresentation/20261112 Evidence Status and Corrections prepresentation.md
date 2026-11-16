# 20261112 Evidence Status and Corrections prepresentation

No new Satay inference, build, benchmark or rehearsal was performed for this package.

| Item | Status |
| --- | --- |
| Baseline tag | Fetched and resolved to 4fe167f91c112d7a5db9fba8da92f22d8a19f842. |
| Capsule | Source inspected: engine.expert_streaming@2.0.0, eight component materials, guidance/method/reference materials and two inspection tools. |
| Run 4 | Tagged handoff reports 903.95 -> 785.22 ms/token, one lab run per endpoint: about 13.1% lower time/token or 15.1% higher throughput. Task factory-bd173c082bf34ae3b8471938c19b8068. Not independently rerun here. |
| J-OM13 | Tagged handoff reports separate ABBA evidence, 841.5 vs 711.4 ms/token, twelve runs, identical output. Additional -t 4 tuning is a separate comparison. Inspect actual spec/report/verdict before presenting. |
| Run 5 | Latest user report and the handoff's later section: stopped at decision 21, no component kept. Opening “still running” text is stale. Task factory-53db494559954fc6a690a9a014afbf21. |
| Revision 13 | Tagged handoff identifies CONFIG_MISSING, preserved builds and added settings-reporting dependencies. This proves a decision change, not a speed win. |
| J-XS4 | Latest operator report: experiments/jetson/OM/J-XS4-activity/activity.html in siminfeng; separate unscored capture with matching output, 79% of selected experts predicted, 92% readiness for predicted vs 55% unpredicted. Raw denominators were not inspected here; verify expert-count versus byte/event definitions. |
| J-XS2 | Older source handoff describes 79% prediction, 82% vs 40% byte readiness and INVALID A/B. This is a different capture. Do not combine its values with J-XS4. |
| Tests | Operator reports 290 factory tests passed once after final merge; not rerun here. |
| Video | Operator reports twelve rendered scenes/310 seconds under revision, then user redirected to code/results and paused work. Completion and rehearsal unverified. |
| Inventory | Tagged handoff reports 16 catalog entries / 21 callable capabilities; old six-CC runbook and meeting 9/12 counts are historical. Demo scope is the relevant few capabilities. |
| Planted slowdown | Tagged handoff states it was removed from baseline and preserved only on a disclosed controlled-seed branch. Never use it as an organic RSI gain. |

Real headroom includes applicability ranking, effective-config prerequisites, interpreting actual per-token activity and missing-required-evidence handling. Generic evidence requirements do not currently gate all acceptance. Adaptive policies and placement remain optional later research.

The tagged handoff also identifies a race between graph precondition checks and job submission. This is a host-system concern; do not claim atomic stale-work prevention or count its repair as a capsule improvement without explaining the distinction.

Current user direction supersedes compulsory slides: show actual code and results, ideally recorded on screen. Keep remote work paused. This document corrects interpretation; original source snapshots remain unchanged.
