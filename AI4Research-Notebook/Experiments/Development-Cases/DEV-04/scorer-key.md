## Scorer key — DEV-04 (do not provide to execution agent)

- Equal model/tools/limits and frozen prompts/fixtures; clean state per run.
- Pair each task/repetition and randomize/counterbalance arm order; propose 3 paired dev repeats/task.
- Primary quality outcome is predefined rubric score difference; secondary includes time/usage and completion/failure.
- Blind independent scoring and adjudication rule; retain raw artifacts.
- Held-out contents withheld; lock split/hashes before proposer tuning; no held-out result claims before execution.
- Critical errors: unequal budgets without justification; scorer sees condition; calls 3 repetitions evidence of generality; fabricated outcomes.
