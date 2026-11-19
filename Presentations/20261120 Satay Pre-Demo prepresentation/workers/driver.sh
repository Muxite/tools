#!/bin/bash
cd ~/predemo/ab
for n in 5 1 2 4 3; do
  ./ab_run.sh $n N &
  ./ab_run.sh $n C &
  wait
  echo "wo$n done $(date -u +%FT%TZ)" >> ~/predemo/ab/driver.log
done
echo ALL-DONE >> ~/predemo/ab/driver.log
