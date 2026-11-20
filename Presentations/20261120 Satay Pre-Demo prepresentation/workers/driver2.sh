#!/bin/bash
# Builder-methodology run: one agent per work order uses the revised capsule (arm C only). 2 at a time.
cd ~/predemo/ab
for pair in "5 1" "2 4" "3"; do
  for n in $pair; do ./ab_run.sh $n C & done
  wait
  echo "pair $pair done $(date -u +%FT%TZ)" >> ~/predemo/ab/driver2.log
done
echo ALL-DONE >> ~/predemo/ab/driver2.log
