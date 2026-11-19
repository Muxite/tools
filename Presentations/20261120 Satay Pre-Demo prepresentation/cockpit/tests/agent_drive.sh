#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
cockpit=bin/cockpit

await_step() {
    local expected=$1 outcome=${2:-ok} status
    for ((attempt=0; attempt<22; attempt++)); do
        status=$("$cockpit" status)
        if jq -e --arg step "$expected" --arg outcome "$outcome" '
            .current_step == $step and .last_event.step == $step and
            .last_event.kind == "task" and .last_event.status == $outcome and
            (.state == "ready" or .state == "complete" or .state == "failed")
        ' <<< "$status" >/dev/null; then
            return 0
        fi
        if [[ $outcome == ok ]] && jq -e '.state == "failed"' <<< "$status" >/dev/null; then
            break
        fi
        sleep 1
    done
    printf 'Step %s expected %s. Last status %s\n' "$expected" "$outcome" "$status" >&2
    return 1
}

"$cockpit" status >/dev/null
"$cockpit" say "One model and one machine. Tonight’s timings are fixtures." >/dev/null
"$cockpit" run s05 >/dev/null
await_step s05 fail
"$cockpit" run s01 >/dev/null
await_step s01
for step in s02 s03 s04 s05 s06 s07 s08 s09 s10 s11 s12 s13 s14; do
    if [[ $step == s05 ]]; then
        "$cockpit" run s05 >/dev/null
    else
        "$cockpit" next >/dev/null
    fi
    await_step "$step"
    if [[ $step == s06 ]]; then
        "$cockpit" diff expert_weight_cache | jq -e '.view == "diff"' >/dev/null
    fi
    if [[ $step == s12 ]]; then
        "$cockpit" result B | jq -e '.stage == "fixture" and .receipt.ttft_ms == 140' >/dev/null
    fi
done
"$cockpit" say "The synthetic threshold was met. Hardware measurement is the next decision." >/dev/null
"$cockpit" status | jq -e '.state == "complete" and .current_step == "s14" and .pending_steps == []'
