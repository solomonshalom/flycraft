#!/usr/bin/env bash
# 18 Sep 2026: WHATS_LEFT_FLY.md "must do before writing" 1-3, in one queue (RESEARCH_NOTES 19).
#   nohup experiments/run_queue5.sh > logs/queue5.out 2>&1 &
# Offline items first (they want the whole CPU), the arena trials after (two brains at 3 threads each; nothing else running).
cd "$(dirname "$0")/.."
export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 PYTHONWARNINGS=ignore
echo "== queue5 starts $(date +%T)"
# item 3: is "stop on contact" (touch shuts the turning DNs) wiring or labelling? sign-rule x eLN x table axis, both sexes
NUMBA_NUM_THREADS=6 python3 -u experiments/contact_stop.py --dataset flywire --seeds 3 --noise 0.2 > logs/contact_stop_flywire.out 2>&1 || echo "   FAILED: contact_stop flywire"
NUMBA_NUM_THREADS=6 python3 -u experiments/contact_stop.py --dataset malecns --seeds 3 --noise 0.2 > logs/contact_stop_malecns.out 2>&1 || echo "   FAILED: contact_stop malecns"
echo "== contact_stop done $(date +%T)"
# item 2: the state arm on the paper's model (SAG / P1 do not pass through the antennal lobe; the table must show it)
NUMBA_NUM_THREADS=6 python3 -u experiments/state_probe.py --dataset flywire --seeds 5 > logs/state_probe_flywire_specific.out 2>&1 || echo "   FAILED: state_probe flywire"
NUMBA_NUM_THREADS=6 python3 -u experiments/state_probe.py --dataset malecns --seeds 5 > logs/state_probe_malecns_specific.out 2>&1 || echo "   FAILED: state_probe malecns"
echo "== state probes done $(date +%T)"
# item 1: encounter trials in a clean chamber (the world within 45 blocks of the origin is wiped and checked first), then
# the same with a documented walking substrate (0.2 Hz background kicks on every neuron of both brains; noise_floor.py)
NOISE=0 experiments/encounter_trials.sh 5 300 > logs/encounter_trials_clean.out 2>&1 || echo "   FAILED: encounter trials clean"
echo "== clean-chamber trials done $(date +%T)"
NOISE=0.2 experiments/encounter_trials.sh 5 300 > logs/encounter_trials_noise0.2.out 2>&1 || echo "   FAILED: encounter trials noise"
echo "== noise trials done $(date +%T)"
# --- tail rewritten at 01:08 while the noise mf series ran (bytes above unchanged): the machine slept 00:18-00:45 on battery
# (noise ff trial 2 lost, trial 3 stalled during its build); caffeinate -i now holds it awake; the optional virgin series is
# dropped to save the battery (64 % at 01:06). Redo the two lost trials, then the steady-state substrate check, then stats.
CONDS=ff NOISE=0 CLEAR_R=0 LABEL=clean experiments/encounter_trials.sh 1 300 > logs/encounter_trials_clean_redo1.out 2>&1 || echo "   FAILED: clean ff trial 1 redo"
echo "== clean ff trial 1 redone $(date +%T)"
export NUMBA_NUM_THREADS=3 VIEW1=0 VIEW2=0 NO_FOOD=1 ARENA_R=6 ARENA_Y=64
DS1=flywire DS2=flywire TP1=0,64,-2 TP2=0,64,2 YAW1=180 YAW2=0 DUR=300 TRIAL=off_ff_t2_noise0.2 experiments/run_pair.sh off --seed 2 --noise-hz 0.2 > logs/trial_off_ff_2_noise0.2_redo.out 2>&1 || echo "   FAILED: noise ff trial 2 redo"
echo "== noise ff trial 2 redone $(date +%T)"
FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 NUMBA_NUM_THREADS=6 python3 -u experiments/noise_floor.py --dataset flywire --noise 0.1,0.2,0.3 --ms 10000 --seeds 2 --suffix _10s > logs/noise_floor_flywire_10s.out 2>&1 || echo "   FAILED: noise_floor 10 s"
FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 NUMBA_NUM_THREADS=6 python3 -u experiments/noise_floor.py --dataset malecns --noise 0.2 --ms 10000 --seeds 2 --suffix _10s > logs/noise_floor_malecns_10s.out 2>&1 || echo "   FAILED: noise_floor male 10 s"
python3 experiments/encounter_stats.py > logs/encounter_stats_19.out 2>&1
python3 experiments/figures.py > logs/figures_19.out 2>&1
echo "== queue5 done $(date +%T)"
