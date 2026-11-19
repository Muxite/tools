#!/bin/bash
# Commit + push Satay pre-demo work off the machine. Usage: sync.sh "commit subject"
set -eu
MSG="${1:-Sync Satay pre-demo work}"
R=$HOME/predemo-push/tools
BR=satay-predemo-20261119
D="Presentations/20261120 Satay Pre-Demo prepresentation"
if [ ! -d "$R/.git" ]; then
  mkdir -p "$HOME/predemo-push"
  git clone -q --depth 1 -b satay-cc-friday-20261120 https://github.com/Muxite/tools.git "$R"
  git -C "$R" checkout -q -B "$BR"
fi
cd "$R"
mkdir -p "$D/workers" "$D/docs" "$D/runs"
cp_dir() { # src dst  (no rsync dependency)
  rm -rf "$2"; mkdir -p "$2"
  (cd "$1" && tar --exclude='./run' --exclude='__pycache__' --exclude='*.pyc' -cf - .) | (cd "$2" && tar -xf -)
}
[ -d "$HOME/predemo/cockpit" ] && cp_dir "$HOME/predemo/cockpit" "$D/cockpit"
[ -d "$HOME/predemo/receipts" ] && cp_dir "$HOME/predemo/receipts" "$D/receipts"
[ -d "$HOME/predemo/runs" ] && cp_dir "$HOME/predemo/runs" "$D/runs"
[ -d "$HOME/predemo/docs-sync" ] && cp_dir "$HOME/predemo/docs-sync" "$D/docs"
for f in one_shot.sh sync.sh preflight.sh w1.txt w2.txt w3.txt wcc.txt wfix.txt wprep.txt prov.sh prov2.sh; do [ -f "$HOME/predemo/$f" ] && cp "$HOME/predemo/$f" "$D/workers/$f"; done
# JiuwenSwarm worktree: the five new capsules, factory fix diff, new tasks/contracts
W=/home/muk/predemo/jiuwenswarm-work
if [ -d "" ]; then
  mkdir -p "/jiuwenswarm"
  for c in observability_event_recorder expert_weight_cache weight_placement_planner expert_demand_predictor batch_layout_mapper; do
    [ -d "/jiuwenswarm/factory/ccs/" ] && cp_dir "/jiuwenswarm/factory/ccs/" "/jiuwenswarm/ccs/"
  done
  (cd "" && git diff -- jiuwenswarm tests :!jiuwenswarm/factory/ccs > "/home/muk/predemo/factory-source.diff" 2>/dev/null; true)
  cp "/home/muk/predemo/factory-source.diff" "/jiuwenswarm/factory-source.diff" 2>/dev/null || true
  for f in ""/jiuwenswarm/factory/contracts/star-* ""/jiuwenswarm/factory/tasks/star-* ""/jiuwenswarm/factory/tasks/STAR-README.md; do [ -f "" ] && { mkdir -p "/jiuwenswarm/factory-new"; cp "" "/jiuwenswarm/factory-new/"; }; done
fi
# keep logs small: only the tail of each worker/build log
mkdir -p "$D/logs"
for f in "$HOME"/predemo/logs/*.log; do [ -f "$f" ] && tail -n 200 "$f" > "$D/logs/$(basename "$f")"; done
# refuse anything big or secret-looking
BIG=$(find "$D" -type f -size +5M | head -3)
[ -n "$BIG" ] && { echo "refusing, large files: $BIG"; exit 3; }
SEC=$(grep -rIl -E 'ghp_[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH) PRIVATE KEY|sk-[A-Za-z0-9]{30,}' "$D" 2>/dev/null | head -3)
[ -n "$SEC" ] && { echo "refusing, secret-like content: $SEC"; exit 4; }
git add -A "$D"
if git diff --cached --quiet; then echo "nothing to commit"; exit 0; fi
N=$(git config user.name || true); E=$(git config user.email || true)
[ -z "$N" ] && N=Muxite
[ -z "$E" ] && E=Muxite@users.noreply.github.com
git -c user.name="$N" -c user.email="$E" commit -q -m "$MSG

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
git push -q origin "$BR" 2>&1 | tail -3
git log --oneline -1
git rev-parse HEAD
