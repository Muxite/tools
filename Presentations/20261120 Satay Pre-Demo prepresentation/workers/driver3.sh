#!/bin/bash
# Round 2: capsule 1.1.1, all five, 2 at a time, into runs-r2
export RUNROOT=runs-r2
cd ~/predemo/ab
mkdir -p runs-r2
for pair in "5 1" "2 4" "3"; do
  for n in $pair; do ./ab_run.sh $n C & done
  wait
  echo "r2 pair $pair done $(date -u +%FT%TZ)" >> ~/predemo/ab/driver3.log
done
echo R2-ALL-DONE >> ~/predemo/ab/driver3.log
