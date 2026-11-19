# Cockpit

Cockpit runs and records an agent-driven tmux demo. The supplied 14-step script uses a local stock Git repository, five patch files and **fixture** receipts. The ABBA timings are synthetic.

## Quickstart

Run these from the cockpit directory. After starting autopilot, wait for `cockpit status` to show `complete` before stopping the recording.

```bash
bin/cockpit up
bin/cockpit record start
bin/cockpit autopilot
bin/cockpit record stop
bin/cockpit bundle
```

Use `bin/cockpit attach` in another terminal to watch. The layout targets 200×55 and supports 160×45. Press **C-b Space** then a control key, or use **C-b** directly with **n** next, **b** back, **d/D** diff forward/back, **r** results, **p** pause/resume, **q** quiet on/off and **?** help. Use **j/k**, **PgUp/PgDn** and **g** in the diff viewer. PLAN, CC and RESULTS also scroll when content exceeds their panes. To detach, use **C-b :** and enter `detach-client`. Run `bin/cockpit down` when finished.

`bin/cockpit status` returns JSON and reports asynchronous step outcomes. `bin/verify-bundle run/<id>/BUNDLE` checks the manifest and receipt references. Capture starts with `record start`, so a bundle made without recording contains the ledger and references only.

Requires Bash, Python 3.10+, jq, flock, Git, tmux and asciinema. The recorder checks `PATH` and then `~/.local/bin/asciinema`. Cockpit uses the private socket `run/tmux.sock`. Scratch files and runs stay under `run/`.

- [Agent cookbook](docs/AGENT.md)
- [Real step substitutions](docs/REAL-STEPS.md)
- [Design](DESIGN.md)
- [Last test run](tests/LAST_RUN.txt)
- [Layout snapshots](docs/layout-capture.txt)
