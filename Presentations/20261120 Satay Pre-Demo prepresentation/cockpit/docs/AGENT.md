# Drive a demo from the shell

Have the operator run `bin/cockpit up`. They can also start recording before handing you the demo. Use the same working directory for the commands below.

1. Run `bin/cockpit status`. Read `current_step`, `state`, `pending_steps` and `last_event`. The stock script starts with `s01` pending. Use `bin/cockpit say "One model, one machine. These timings are fixtures."` for the opening caption.
2. Run `bin/cockpit next` to schedule one step. Poll `bin/cockpit status` about once a second until the step completes. A successful scheduling response means the worker started. Check the last task event and `state` for its outcome. While `quiet` is true, wait for the command to finish before changing the caption or view.
3. After `s04`, use `bin/cockpit diff expert_weight_cache` to show the owning capsule’s patch. Advance through source verification, the image receipt and the activation gate with `next`.
4. Advance through the ABBA comparison and arm receipts. Use `bin/cockpit result A` and `bin/cockpit result B` after `s11`. Each returns the stage, receipt path, SHA-256 and metrics. Say the stage aloud whenever presenting a comparison.
5. Advance through `s14`. The finished run has `state: "complete"` and no pending steps. Keep the baseline definition and claim-to-receipt mapping fixed. Use `say` to adjust the wording in the dated log.

If a step fails, read `last_error` and the relevant run event or output path. Once its prerequisites are available, use `bin/cockpit run s05` to retry `s05`, or substitute the failed step ID. The director checks for dead panes before scheduling work and respawns them on the same private server. Retrying appends new attempt events and leaves earlier receipts in place.
