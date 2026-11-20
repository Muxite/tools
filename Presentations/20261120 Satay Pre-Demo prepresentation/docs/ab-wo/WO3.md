WORK ORDER 3: weight placement planner readback (llama.cpp pinned at 9048bad8d6e3a0f9f1726e238e451181c7e02613)
Build, as a source diff, the engine side of a weight placement planner: load an explicit placement plan file and turn it into tensor buffer-type overrides equivalent to `-ot`, and log the effective assignment.
- Option `--placement-plan <file>` (register in `common/arg.cpp`, env `LLAMA_ARG_PLACEMENT_PLAN`), honoured only when the gate `LLAMA_PLACEMENT_PLAN=1` is also set. Plan file: JSON `{"version":1,"overrides":[{"pattern":"<tensor name regex>","buft":"CPU"}]}`, at most 4 MiB, at most 4095 entries; unknown fields or versions are an error reported as inactive.
- Each tensor placed exactly once; unmatched tensors keep the stock default. Missing file or bad JSON means inactive with a reason, never a crash.
- INFO log lines (`-lv 4`): exactly one `weight_placement_planner: active cap_bytes=<n> peak_bytes=<n>` or one `weight_placement_planner: inactive (<reason>)`; one `weight_placement_planner: stats assigned=<n> stock=<n>` at exit.
- Invariants: output byte identical to stock with the gate unset, and identical to stock `-ot` for the same assignments with the gate set.
- Allowed paths: `common/arg.cpp`, `common/common.h`, `common/common.cpp`, `src/`, CMake files for new sources.
