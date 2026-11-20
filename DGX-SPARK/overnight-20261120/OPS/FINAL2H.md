# Final 2 hours plan (owner, ~14:16Z). Hard stop for new GPU work at about 15:30Z; demo-ready by about 16:15Z.

## GPU lane, strictly in this order (screening vs pooled A+30, 2 warmups and 4 pairs per size)
1. C4 predictor: finish the run in progress and publish.
2. D (all CCs combined, frozen 10abe9abbf8f): screen and publish. This is the "all five together" result.
3. C5 mapper repair: build now on CPUs 12-19 (nice 19), then screen and publish.
4. C2 placement tier (layer 27 manual on A+30): screen and publish only if time remains before 15:30Z.

No more ABBA confirmations, new iterations, quantization work or new CCs. Anything not measured by 15:30Z is reported as "built, not measured".

## CPU lane, in parallel
- **Final report (`report.md` plus native export), headline table first.** Rows:
  - S vs A-matched vs A+30.
  - C3 30 quiet ABBA: null and negative.
  - C3-direct 30 quiet ABBA: warm parity plus the cold-start win.
  - C3 60: 10/10 pairs faster, TTFT -24.9/-90.8 s, quiet subset -26.8/-100.2 s, I/O cause.
  - C4, D, C5, C2: screening.
  - C1: functional.
  - Each row carries a plain-English line and a verified/screening label.
- **The loop story.** Recorder report, then planner decisions, then C3 iteration 1 (negative), then the mechanism (page-cache starvation), then iteration 2 (direct seed). Include links to each report and decision.
- **UI.** A final snapshot with all results. The Overview and Measurements pages show the headline. Each CC card shows its own result.
- **Live-view demo.** A short live session that completes in about 3-5 minutes (e.g. the recorder on the Granite fixture) and can be started from the UI Launch button during the demo. Rehearse it once.
- **Click path.** `OPS/DEMO-SCRIPT.md`: 6-8 steps in order, with what to say at each: Contract, then Ontology, Capsules, Iterations (report to decision), Measurements, Report, then Live launch.

## Wrap-up (15:30-16:15Z)
- Chromium rehearsal over tailscale at http://<tailnet-ip>:5173. No page errors on any step in DEMO-SCRIPT.
- Commit everything. Leave the demo services running with no model loaded (GPU idle), and write a final STATUS line.
