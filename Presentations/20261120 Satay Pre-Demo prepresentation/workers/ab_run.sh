#!/bin/bash
# usage: ab_run.sh <wo 1..5> <arm N|C>   Runs one coding agent on one work order in its own arm directory.
set -u
N=$1; ARM=$2
AB=$HOME/predemo/ab
CODEX=/home/muk/.codex/packages/app-server-daemon/releases/0.170.0-aarch64-unknown-linux-musl/bin/codex
DIRS=(x observability_event_recorder expert_weight_cache weight_placement_planner expert_demand_predictor batch_layout_mapper)
CAP=$HOME/predemo/jiuwenswarm-work/jiuwenswarm/factory/ccs/${DIRS[$N]}
D=$AB/${RUNROOT:-runs}/wo$N-$ARM
rm -rf "$D"; mkdir -p "$D"
cp -a $HOME/predemo/llama.cpp-stock "$D/src"
git -C "$D/src" status --porcelain | head -1 | grep -q . && { echo "stock copy not clean"; exit 2; }
WO=$(cat "$AB/wo/WO$N.md")
if [ "$ARM" = C ]; then
  cp -a "$CAP" "$D/capsule"
  EXTRA="A vetted Capability Capsule (CC) for exactly this component is in $D/capsule . A CC is a bundle that carries a guide, method, ontology slice, source map, component manifest, tests and a verifier, with pinned hashes. Read its GUIDE.md first, then METHOD.md, SOURCE-MAP.md, ONTOLOGY.yaml and component.yaml, and use its tests and its verify capability as its VALIDATION.md describes (its python is ~/predemo/venv-factory/bin/python). Use it as you would a vetted tool or skill package; you may deviate where you can justify it, and say so."
else
  EXTRA="No capsule is provided for this task. Do not read anything under ~/predemo/jiuwenswarm-work, ~/predemo/ref, ~/predemo/receipts or ~/satay-cc-prefill-20261119. You may read the pristine source and ordinary system documentation."
fi
python3 - "$AB/arm_prompt.txt" "$D" "$EXTRA" "$WO" > "$D/prompt.txt" <<'PY'
import sys
t=open(sys.argv[1]).read().replace("__ARMDIR__",sys.argv[2]).replace("__ARMEXTRA__",sys.argv[3]).replace("__WO__",sys.argv[4])
print(t)
PY
echo "start $(date -u +%FT%TZ)" > "$D/timing.txt"
S=$(date +%s)
timeout 4200 $CODEX exec --skip-git-repo-check -s workspace-write -C "$D" "$(cat $D/prompt.txt)" > "$D/agent.log" 2>&1 < /dev/null
echo "exit $? end $(date -u +%FT%TZ) wall_s $(( $(date +%s) - S ))" >> "$D/timing.txt"
grep -A1 "tokens used" "$D/agent.log" | head -2 >> "$D/timing.txt"
grep -c "jiuwenswarm-work\|predemo/ref\|capsule" "$D/agent.log" | sed 's/^/capsule_mentions_in_log /' >> "$D/timing.txt"
[ -f "$D/candidate.diff" ] && sha256sum "$D/candidate.diff" >> "$D/timing.txt"
