#!/usr/bin/env bash
# 20 Sep 2026: WHATS_LEFT_FLY.md "machine time" items 4 and 6 (RESEARCH_NOTES 20). Offline only; nothing else should run.
#   caffeinate -i experiments/run_queue6.sh > logs/queue6.out 2>&1 &      (caffeinate: the MacBook slept on battery on 19 Sep)
cd "$(dirname "$0")/.."
export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 PYTHONWARNINGS=ignore NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6}
echo "== queue6 starts $(date +%T)   $(pmset -g batt | tail -1)"
# the 3-seed files of 17-18 Sep are kept (seeds 0-2 are the same runs; the 5-seed files are supersets)
mkdir -p experiments/results/old_v1
for f in gain_sweep_flywire_shiu_min1+known+eln0.25 gain_sweep_malecns_all_min1+eln0.25 contact_stop_flywire contact_stop_malecns; do
  [ -f "experiments/results/$f.csv" ] && [ ! -f "experiments/results/old_v1/${f}_3seeds.csv" ] && cp "experiments/results/$f.csv" "experiments/results/old_v1/${f}_3seeds.csv"
done
# item 4: five seeds for the two gain sweeps of the paper's model and for the contact-stop axis (both sexes)
python3 -u experiments/gain_sweep.py --dataset flywire --seeds 5 > logs/gain_sweep_flywire_specific_5seeds.out 2>&1 || echo "   FAILED: gain_sweep flywire"
python3 -u experiments/gain_sweep.py --dataset malecns --seeds 5 > logs/gain_sweep_malecns_specific_5seeds.out 2>&1 || echo "   FAILED: gain_sweep malecns"
echo "== gain sweeps done $(date +%T)"
python3 -u experiments/contact_stop.py --dataset flywire --seeds 5 --noise 0.2 > logs/contact_stop_flywire_5seeds.out 2>&1 || echo "   FAILED: contact_stop flywire"
python3 -u experiments/contact_stop.py --dataset malecns --seeds 5 --noise 0.2 > logs/contact_stop_malecns_5seeds.out 2>&1 || echo "   FAILED: contact_stop malecns"
echo "== contact_stop done $(date +%T)"
# item 6: the pre-contact slowing as a dose row (the partner's odor at the levels the female reports at 1-3 blocks)
python3 -u experiments/precontact_dose.py --dataset flywire --seeds 3 > logs/precontact_dose_flywire.out 2>&1 || echo "   FAILED: precontact_dose"
echo "== queue6 done $(date +%T)   $(pmset -g batt | tail -1)"
