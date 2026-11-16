---
id: cc-demo-engine-milestone-20261111
status: superseded-demo-direction
source: Sources/Prompts/20261111 Engine Milestone Update prepresentation.txt
last_reviewed: 2026-11-11
next_action: Read the November 12 expert-streaming prompt
---

> **EARLIER GUIDANCE: superseded for the current demo.** Use [the November 12 expert-streaming prompt](<20261112 Satay Expert Streaming Demo Agent Prompt prepresentation.md>). This file remains a dated technical/history reference; its generic build order, thread-naming emphasis and old pending-result statements do not define the current assignment.


# 20261111 CC Demo Engine Milestone prepresentation

## Current source and evidence status

Remote refs independently checked: `main` and `jetson/c1` both point to `682c6377da20d9229ef1fdb705f63a7a751d14cb` in https://github.com/Muxite/siminfeng . Read `c2/STATUS.md`, then `c2/METHODS.md` and `c2/MEASUREMENT-GAPS.md`. Paths formerly under `campaign/` are now rooted at the repository. Historical logs retain their original paths; do not rewrite evidence bytes.

The current status identifies llama.cpp `cf34d311` plus expert-fill/pregate patches 03–09. This supersedes the old Granite/31288c9 component recommendation as the primary demo source. The older gate/up unfusion patch remains a fallback illustration, not an assumed compatible intervention for the current models.

The user reports a serial GPU queue of about 5–6 hours: 9B fit/speed; Gemma-4-E4B QAT fit/speed; 140-question accuracy for each; 35B fit/speed/70-question accuracy; J-OM12 build/profile. This is a reported queue estimate, not a completion time or verified result. In-progress folders are deliberately absent from the push. Do not launch competing GPU work.

## Demonstration choice

Keep Builder CC as the first integration priority. Package the current expert-fill/pregate component and an integration skill around its actual source and settings. Use its validated OFF configuration as the control and preserve a rollback. Choose the precise model/configuration only after the current fit, speed and quality results arrive. The demo proves integration, identified build, real inference and evidence handoff; it does not require every component setting to be faster.

The concrete reliability demonstration is requested configuration → effective configuration → invalid-setting rejection. The reported K=10 silently becoming K=8 is an understandable reason for a reusable verification tool. Show the repaired behavior from an actual run, or a labeled recording against identified revisions. Do not pretend an already-integrated fix was newly authored during the talk.

The fit-resume bug is a useful optional CC-assisted repair task. Require the owning coder to reproduce it first, then demonstrate that a changed command/protocol creates a new attempt and an identical completed successful attempt reuses evidence. Retain failed and interrupted attempts. This repair is not a replacement for the promised engine component integration.

## Required coder follow-up

1. Repair fit identity/resume before relying on automatic pipeline replay. Include effective argv, model/image identity, watchdog policy and relevant environment/protocol inputs in compatibility checks. A failed earlier fit must not hide a changed request. Test the actual preflight path, not only command construction or dry-run.
2. Export requested and effective settings with the build/run receipt. Reject invalid settings; prove actual component engagement separately. Do not treat an enabled log line as performance evidence.
3. Exclude the superseded 600 MiB-watchdog results from current comparison tables. Preserve their explanation and original bytes. The reported 128 MiB floor is a scoped policy for the fully resident models, not a universal recommendation for the 35B.
4. Compare models on the same 70 question IDs and identical MCQ/extraction/scoring protocol. The ladder README says the 70 IDs are nested in the 140. Re-score the 9B and Gemma saved item records on those exact IDs, verifying dataset hashes and coverage; keep their full 140-question results as supplementary evidence. Show sample size, intervals, parse failures and reasoning-text handling. Published thinking-mode scores remain separate context, never the measured comparison column.
5. For J-OM12, link the new image and thread-state profile to the existing timing evidence. The roughly 480 ms is an attribution question, not a proven removable cost. The status recommends 100 Hz sampling because 500 Hz had material overhead. Use separate unprofiled runs for the speed claim.
6. Treat IQ3_S at approximately 2.5 tok/s as an estimate until measured. Near-35B accuracy and quantization fidelity remain hypotheses. The 35B KL comparison against a higher-precision reference is still unmeasured; do not imply the queued MCQ run supplies it.
7. Plan peak disk use before further downloads or builds: the user reports 17 GB free at 86% usage, versus a 12.7 GiB proposed download plus build/profile/output needs. Do not delete image/model baselines needed for rollback or comparability merely to fit the download. Redacted logs should remain redacted in all demo exports.

## Presentation update

**Presentation boundary:** the ten minutes belong entirely to the CC/software-factory presenter. RSI profiling, diagnosis and the next improvement are on the RSI presenter’s separate time. End with a brief artifact handoff; RSI results are not a readiness requirement for this talk.

Use a current status card with three distinct labels: reported fixed, queued, and measured with a published evidence bundle. Memory-floor policy, unsupported preflight flag, invalid-setting fallback, token redaction and duplicate-tarball cleanup are reported fixes; their existence does not prove the pending model comparisons.

The 9B's 10.79 tok/s in `c2/STATUS.md` is explicitly a single smoke run. Do not present it as the final gated result. Existing J-OM11 figures in that source remain earlier results, not J-OM12 outcomes. Wait for the milestone bundle before selecting the final accuracy-versus-speed chart.

Keep the ten-minute sequence: CC roles → baseline/component → skill-guided integration or repair → Builder → Manager/demo lab → evidence handoff. Use a prepared run/recording for long operations. There is no RSI profiling or improvement slide in this presenter’s ten minutes. J-OM12, accuracy-frontier exploration and subsequent optimization are context for the receiving collaborator, not prerequisites for showing the CC workflow.

## Limits of this update

Remote branch identity and the named documentation/specification were inspected. No new engine build, GPU experiment, benchmark score or security audit ran here. Notebook and presentation guidance are updated; the code-owning repository remains unchanged. Queue progress is not being monitored automatically.
