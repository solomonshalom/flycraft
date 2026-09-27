#!/usr/bin/env bash
# 17 Sep 2026: the controls under the specific antennal lobe (WHATS_LEFT_FLY.md items 1, 3, 4), then the encounter
# trials (item 2). Sequential, one experiment at a time (the CPU is the bottleneck; two conditioning runs share it).
#   nohup experiments/run_queue3.sh > logs/queue3.out 2>&1 &
cd "$(dirname "$0")/.."
export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 PYTHONWARNINGS=ignore
T=${NUMBA_NUM_THREADS:-6}
run() { local out=$1; shift; echo "== $out  $(date +%T)"; NUMBA_NUM_THREADS=$T python3 -u "$@" > "logs/$out" 2>&1 || echo "   FAILED: $out"; }
# item 1: gain sweep (both sexes), shuffled-connectome control, sensitivity table (with the sign-rule axis = item 4)
run gain_sweep_flywire_specific.out     experiments/gain_sweep.py --dataset flywire --seeds 3
run gain_sweep_malecns_specific.out     experiments/gain_sweep.py --dataset malecns --seeds 3
run shuffle_flywire_global_specific.out experiments/shuffle_control.py --dataset flywire --mode global --shuffles 3 --seeds 3
run sensitivity_flywire_specific.out    experiments/sensitivity.py --dataset flywire --seeds 3
# item 3: the learning result's own gain window: US dose 20 Hz and eLN x0.1, both odor orders, 3 seeds (two at a time)
cond() { NUMBA_NUM_THREADS=3 python3 -u experiments/conditioning.py --signs known --us dan "$@"; }
for s in 0 1 2; do
  echo "== conditioning reward, US 20 Hz, seed $s  $(date +%T)"
  cond --valence reward --eln 0.25 --us-hz 20 --csp vinegar --csm ester --seed $s > logs/cond_known_dan_reward_20hz_vinegar-ester_s$s.out 2>&1 &
  cond --valence reward --eln 0.25 --us-hz 20 --csp ester --csm vinegar --seed $s > logs/cond_known_dan_reward_20hz_ester-vinegar_s$s.out 2>&1 &
  wait
  echo "== conditioning reward, eLN x0.1, seed $s  $(date +%T)"
  cond --valence reward --eln 0.1 --csp vinegar --csm ester --seed $s > logs/cond_known_dan_reward_eln0.1_vinegar-ester_s$s.out 2>&1 &
  cond --valence reward --eln 0.1 --csp ester --csm vinegar --seed $s > logs/cond_known_dan_reward_eln0.1_ester-vinegar_s$s.out 2>&1 &
  wait
done
echo "== conditioning punish, US 20 Hz and eLN x0.1, seed 0  $(date +%T)"
cond --valence punish --eln 0.25 --us-hz 20 --csp vinegar --csm ester --seed 0 > logs/cond_known_dan_punish_20hz_vinegar-ester_s0.out 2>&1 &
cond --valence punish --eln 0.25 --us-hz 20 --csp ester --csm vinegar --seed 0 > logs/cond_known_dan_punish_20hz_ester-vinegar_s0.out 2>&1 &
wait
cond --valence punish --eln 0.1 --csp vinegar --csm ester --seed 0 > logs/cond_known_dan_punish_eln0.1_vinegar-ester_s0.out 2>&1 &
cond --valence punish --eln 0.1 --csp ester --csm vinegar --seed 0 > logs/cond_known_dan_punish_eln0.1_ester-vinegar_s0.out 2>&1 &
wait
# item 4 (male half): the 67 unclear local neurons as a sensitivity axis
run sensitivity_malecns_specific.out    experiments/sensitivity.py --dataset malecns --seeds 3
echo "== offline queue done $(date +%T)"
# item 2: encounter trials under the specific lobe (run_pair defaults to --al specific), 5 trials per condition, 300 s wall each
experiments/encounter_trials.sh 5 300 > logs/encounter_trials_specific.out 2>&1
echo "== encounter trials done $(date +%T)"
