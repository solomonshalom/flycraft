#!/usr/bin/env bash
# Sequential offline experiment queue (avoids CPU thrash). Waits for any running state_probe to finish first.
cd "$(dirname "$0")/.."
while pgrep -f "experiments/state_probe.py --dataset flywire" > /dev/null; do sleep 15; done
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-5}
echo "== male state probe $(date)";   python3 experiments/state_probe.py --dataset malecns --seeds 5 --ms 1000 --state-hz 30 2>&1 | grep -v -E "UserWarning|m &= " > logs/state_probe_malecns_v2.out
echo "== shuffle global $(date)";     python3 experiments/shuffle_control.py --dataset flywire --shuffles 3 --mode global --seeds 3 2>&1 | grep -v -E "UserWarning|m &= " > logs/shuffle_flywire_global.out
echo "== sensitivity $(date)";        python3 experiments/sensitivity.py --dataset flywire --seeds 3 2>&1 | grep -v -E "UserWarning|m &= " > logs/sensitivity_flywire.out
echo "== conditioning $(date)";       python3 experiments/conditioning.py --dataset flywire --seed 0 2>&1 | grep -v -E "UserWarning|m &= " > logs/conditioning_v2.out
echo "== shuffle block $(date)";      python3 experiments/shuffle_control.py --dataset flywire --shuffles 2 --mode block --seeds 3 2>&1 | grep -v -E "UserWarning|m &= " > logs/shuffle_flywire_block.out
echo "== state probe SAG 100Hz $(date)"; python3 experiments/state_probe.py --dataset flywire --seeds 3 --ms 1000 --state-hz 100 2>&1 | grep -v -E "UserWarning|m &= " > logs/state_probe_flywire_hz100.out
echo "== queue done $(date)"
