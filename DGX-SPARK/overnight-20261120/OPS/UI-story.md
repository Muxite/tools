ROLE ui-story (preview port 5183, branch ui/story-results, worktree ~/predemo-spark/wt-ui-story)

Make the demo tell its story, and make the results look good and honest:
- **English default across the whole app:** i18n fallbackLng and the initial language en. Place the "Factory runs" and "Capability Capsules" nav entries prominently.
- **Overview/landing page for a run:**
  - the question asked (the contract)
  - the 5 CCs used
  - task graph progress
  - key result tiles
  - links to the evidence
- **Measurements:**
  - **Arms:** an arm table and charts for:
    - A (stock documented)
    - A+ (stock plus native MoE cache)
    - C1–C5 (each CC)
    - D (all five)
    - S (Strata)
  - **Columns:** TTFT and the inverse-TTFT ratio vs A, gap to Strata closed, decode tok/s, and peak memory, with confidence intervals and n.
  - **Evidence links:** every number links to its ledger row and evidence file.
  - **Run labels:** label "reconnaissance (noisy)" runs clearly, separate from final ones.
  - **Sourcing:** never show a result without its source.
- **Report view:** report.md rendered with a table of contents.
- **Live session view:** a clear "running now" indicator, the current step, the latest agent message and elapsed time. Add a launch dialog for a new session (template, contract, CCs), wired to the existing backend.
- **Visual polish:**
  - consistent typography and spacing
  - dark and light modes
  - empty and loading states
  - no clutter

**Data:** OPS/LEDGER.jsonl rows and the run result.json files written by bin/capped (see ~/predemo-spark/OPS/runs/*). Add a backend endpoint for the measurements ledger if one is missing, with pytest tests. Use synthetic data only in tests, never in demo views.
