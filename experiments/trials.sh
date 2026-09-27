#!/usr/bin/env bash
# Repeated two-fly encounters for error bars.  Usage: experiments/trials.sh <arm off|mb> <n_trials> [DUR seconds]
# Env: DS1/DS2 datasets, ARENA_R (default 6), LABEL (suffix on the trial label, e.g. clean / noise0.3), BRAIN_ARGS (extra
# run_brain.py options for both brains, e.g. "--noise-hz 0.3"), SEED0 (brain seeds are SEED0+1..SEED0+N; default 0 = the seeds of every
# series before 27 Sep), SYNC=1 (synchronised start, run_pair.sh). Start positions/facings rotate per trial; logs carry trial=<label>.
set -euo pipefail
cd "$(dirname "$0")/.."
ARM=${1:-off}; N=${2:-5}; DUR=${3:-120}
export ARENA_R=${ARENA_R:-6} ARENA_Y=${ARENA_Y:-64} DS1=${DS1:-flywire} DS2=${DS2:-flywire}
POS=("-2,64,0 2,64,0 -90 90" "0,64,-2 0,64,2 180 0" "2,64,0 -2,64,0 90 -90" "0,64,2 0,64,-2 0 180" "-2,64,-2 2,64,2 -135 45")
for i in $(seq 1 "$N"); do
  read -r p1 p2 y1 y2 <<< "${POS[$(( (i-1) % ${#POS[@]} ))]}"
  echo "== trial $i/$N  arm=$ARM  $DS1 @ $p1 vs $DS2 @ $p2"
  # shellcheck disable=SC2086  # BRAIN_ARGS is a word list on purpose
  TP1=$p1 TP2=$p2 YAW1=$y1 YAW2=$y2 DUR=$DUR TRIAL="${ARM}_${DS1:0:1}${DS2:0:1}_t${i}${LABEL:+_$LABEL}" experiments/run_pair.sh "$ARM" --seed "$(( ${SEED0:-0} + i ))" ${BRAIN_ARGS:-} > "logs/trial_${ARM}_${DS1:0:1}${DS2:0:1}_${i}${LABEL:+_$LABEL}.out" 2>&1 || true
  sleep 3
done
echo "done; summarize with: python experiments/analyze.py logs/fly*_${ARM}*.csv"
