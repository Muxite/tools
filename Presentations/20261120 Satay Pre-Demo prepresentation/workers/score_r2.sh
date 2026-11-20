#!/bin/bash
# usage: score_r2.sh <wo...> : score round-2 candidates (runs-r2 -> out-r2)
cd ~/predemo/ab; mkdir -p out-r2
for n in "$@"; do
  d=out-r2/wo$n-C
  [ -f runs-r2/wo$n-C/candidate.diff ] || { echo "no diff wo$n" >> out-r2/scored.log; continue; }
  ./score.sh $n runs-r2/wo$n-C/candidate.diff $d > $d.score.out 2>&1
  ./run_checks.sh $d > $d.run.out 2>&1
  echo "scored wo$n-C $(date -u +%FT%TZ)" >> out-r2/scored.log
done
