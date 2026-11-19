#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p run
cockpit=bin/cockpit
tmux_private=(tmux -S "$PWD/run/tmux.sock")
own_server=0
test_dir=
cleanup() {
    if (( own_server )); then
        "$cockpit" down >/dev/null 2>&1 || "${tmux_private[@]}" kill-server 2>/dev/null || true
    fi
    if [[ -n $test_dir ]]; then
        rm -rf -- "$test_dir"
    fi
}
trap cleanup EXIT

printf 'Cockpit tests  %s\n' "$(date -u +%FT%TZ)"
printf '\n[syntax] Bash and Python\n'
shell_count=0
for script in bin/* demo/*.sh tests/*.sh; do
    bash -n "$script"
    shell_count=$((shell_count + 1))
done
python_files=(*.py panes/*.py tests/*.py)
PYTHONPYCACHEPREFIX="$PWD/run/pycache" python3 -m py_compile "${python_files[@]}"
printf '%s Bash scripts and %s Python files passed\n' "$shell_count" "${#python_files[@]}"

printf '\n[atomicity] 8 concurrent writers\n'
test_dir=$(mktemp -d "$PWD/run/test-atomic-XXXXXX")
pids=()
for writer in {1..8}; do
    (
        export COCKPIT_RUN=${test_dir##*/} COCKPIT_STAGE=fixture
        for number in {1..6}; do
            bin/ev note ok --data "{\"writer\":\"$writer\",\"number\":$number}" >/dev/null
        done
    ) &
    pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
python3 -B tests/support.py atomic "$test_dir"

if "${tmux_private[@]}" list-sessions >/dev/null 2>&1; then
    printf 'A server is already using the cockpit test socket. Integration needs an unused socket.\n' >&2
    exit 1
fi
printf '\n[tmux] Private server startup\n'
if ! setup=$("$cockpit" up); then
    printf '%s\n' "$setup"
    printf '%s\n' '[blocked] Unattached autopilot, tmux capture-pane, agent drive, recording, tmux quiet CPU and pane respawn.'
    printf '\n[fallback] Actual fixture commands and ledger with tmux display and job transport substituted\n'
    python3 -B tests/support.py standalone --capture
    printf '\nFAIL: tmux integration is blocked. No private tmux server was started.\n'
    exit 1
fi
own_server=1
printf '%s\n' "$setup"
dir=run/$(jq -r '.run' <<< "$setup")

await_status() {
    local filter=$1 status
    for ((attempt=0; attempt<40; attempt++)); do
        status=$("$cockpit" status)
        if jq -e "$filter" <<< "$status" >/dev/null; then
            printf '%s\n' "$status"
            return 0
        fi
        if jq -e '.state == "failed"' <<< "$status" >/dev/null; then break; fi
        sleep 1
    done
    printf 'Expected %s. Last status %s\n' "$filter" "$status" >&2
    return 1
}

printf '\n[autopilot] All 14 fixture steps in an unattached server\n'
[[ -z $("${tmux_private[@]}" list-clients -t cockpit) ]]
"$cockpit" autopilot --speed 2
await_status '.state == "complete" and .current_step == "s14" and .pending_steps == []' |
    jq '{state,current_step,pending_steps}'
python3 -B tests/support.py fixture "$dir"
bundle=$("$cockpit" bundle | jq -er '.bundle')
bin/verify-bundle "$bundle"

printf '\n[layout] 200x55 and 160x45 capture-pane snapshots\n'
{
    for size in 200x55 160x45; do
        "${tmux_private[@]}" resize-window -t cockpit:demo -x "${size%x*}" -y "${size#*x}"
        sleep 2
        for name in plan data experiment cc result; do
            id=$("$cockpit" status | jq -er --arg name "$name" '.panes[$name].id')
            printf '\n=== %s %s ===\n' "$size" "${name^^}"
            "${tmux_private[@]}" capture-pane -p -t "$id"
        done
        "$cockpit" diff expert_weight_cache >/dev/null
        sleep 2
        printf '\n=== %s DIFF ===\n' "$size"
        "${tmux_private[@]}" capture-pane -p -t "$id"
        "$cockpit" view results >/dev/null
    done
} > docs/layout-capture.txt

printf '\n[quiet] 10-second pane CPU measurement\n'
bin/ev quiet on >/dev/null
status=$("$cockpit" status)
jq -e '.quiet and all(.panes[]; .dead == false)' <<< "$status" >/dev/null
python3 -B tests/support.py quiet "$status"
bin/ev quiet off >/dev/null

printf '\n[recovery] Kill only the private DATA pane and recover with cockpit run\n'
old=$("$cockpit" status | jq -er '.panes.data.pid')
tr '\0' ' ' < "/proc/$old/cmdline" | grep -F "panes/data.py $PWD/$dir" >/dev/null
kill -TERM "$old"
await_status '.panes.data.dead' | jq '.panes.data'
"$cockpit" run s12 | jq -e '.recovered == ["data"]'
await_status '.current_step == "s12" and .last_event.status == "ok" and (.panes.data.dead | not)' |
    jq -e --argjson old "$old" '.panes.data.pid != $old'
"$cockpit" down

printf '\n[agent] Drive via status, next, run, say, diff and result, with recording\n'
"$cockpit" up
"$cockpit" record start
tests/agent_drive.sh | jq '{state,current_step,pending_steps,view,result_arm}'
bin/wording add "Threshold met" "Synthetic threshold met" "Fixture receipts" | jq -e '.reason == "Fixture receipts"'
"$cockpit" record stop
bundle=$("$cockpit" bundle | jq -er '.bundle')
bin/verify-bundle "$bundle"
python3 -B tests/support.py recording "$bundle"
"$cockpit" down
own_server=0
for attempt in {1..10}; do
    [[ -S $PWD/run/tmux.sock ]] || break
    sleep 0.1
done
[[ ! -S $PWD/run/tmux.sock ]]
printf '\nPASS: private tmux server stopped.\n'
