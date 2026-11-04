---
id: cc-pilot-task-prompts
status: proposed
source: AI4Research-Notebook/Experiments/Development-Cases/README.md
last_reviewed: 2026-10-20
next_action: Have the adapter consume only prompt.txt plus fixture files; freeze input-only hashes after audit.
---
# CC pilot task prompts

Agent-facing prompts and fixtures are separated by development case. Use the prompt and fixture links in [[Experiments/Development-Cases/README|Development Cases]]. The adapter's input list excludes every `scorer-key.md` and manifest file. The `manifest.json` in each case folder contains hashes of the prompt and fixture files only.

Scorer keys live separately beside each case and must be loaded only by the independent scorer after output capture. Held-out cases remain uncreated with an independent custodian. The runnable M1 adapter remains pending code audit; all cases are proposed and unrun.
