#!/usr/bin/env bash
# 17 Sep 2026, second queue: waits for run_queue3.sh (controls + encounter trials), then WHATS_LEFT items 6 and 7 and
# the male shuffle control (RESEARCH_NOTES 15, "what must still be done" 4).
#   nohup experiments/run_queue4.sh > logs/queue4.out 2>&1 &
cd "$(dirname "$0")/.."
export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 PYTHONWARNINGS=ignore
while pgrep -f run_queue3.sh > /dev/null; do sleep 30; done
echo "== queue3 finished; queue4 starts $(date +%T)"
# item 6: appetitive learning in the world with a real dose of sugar: the experimenter holds the fly on a 7x7 poppy patch
# (re-placed every 8 s), vinegar flowers bitter; PRE/TRAIN/POST 90/360/90 s wall
HOLD=8 PATCH_R=3 BITTER=vinegar PRE=90 TRAIN=360 POST=90 VIEW=0 experiments/learn_in_world.sh world3 > logs/learn_world3.out 2>&1 || echo "   FAILED: learn_in_world world3"
echo "== in-world learning done $(date +%T)"
# item 7: male odor learning (MaleCNS has no known_nt column: --signs known is a no-op there; eLN x0.25 applies)
cond() { NUMBA_NUM_THREADS=3 python3 -u experiments/conditioning.py --dataset malecns --eln 0.25 --us dan "$@"; }
cond --valence reward --csp vinegar --csm ester --seed 0 > logs/cond_malecns_dan_reward_vinegar-ester_s0.out 2>&1 &
cond --valence reward --csp ester --csm vinegar --seed 0 > logs/cond_malecns_dan_reward_ester-vinegar_s0.out 2>&1 &
wait
cond --valence punish --csp vinegar --csm ester --seed 0 > logs/cond_malecns_dan_punish_vinegar-ester_s0.out 2>&1 &
cond --valence punish --csp ester --csm vinegar --seed 0 > logs/cond_malecns_dan_punish_ester-vinegar_s0.out 2>&1 &
wait
echo "== male conditioning done $(date +%T)"
# male shuffle control under eLN x0.25 (2 shuffles; 25.6 M connections take a while to rewire)
NUMBA_NUM_THREADS=6 python3 -u experiments/shuffle_control.py --dataset malecns --mode global --shuffles 2 --seeds 3 > logs/shuffle_malecns_global_specific.out 2>&1 || echo "   FAILED: male shuffle"
echo "== queue4 done $(date +%T)"
