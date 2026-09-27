#!/usr/bin/env bash
# Finish the re-run of 25 Sep 2026 (RESEARCH_NOTES 22) where the memory stop cut it off, one step at a time, then the
# arena replication. Each finished step leaves a marker in logs/rerun_20260925_done/, so running this again resumes
# after the last finished step instead of repeating it.
#   caffeinate -i experiments/run_rerun_rest.sh
set -uo pipefail
cd "$(dirname "$0")/.."
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6} PYTHONWARNINGS=ignore
DONE=logs/rerun_20260925_done; mkdir -p "$DONE"
log() { echo "== $* $(date '+%F %T')"; }
mem() { memory_pressure 2> /dev/null | tail -1; }

# 1. the male part of the shuffle group (the three female shuffles finished before the stop)
if [ ! -f "$DONE/shuffle-male" ]; then
  log "shuffle (male, paper's model) | $(mem)"
  if FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 experiments/shuffle_control.py --dataset malecns --mode global --shuffles 2 --seeds 3 \
       > logs/reproduce_shuffle_male.out 2>&1; then touch "$DONE/shuffle-male"; log "ok"; else log "FAILED (logs/reproduce_shuffle_male.out)"; exit 1; fi
fi
# 2. the offline groups that did not run, in reproduce.sh's order
for g in sensitivity odor-dose contact-stop noise-floor precontact state conditioning expression figures; do
  [ -f "$DONE/$g" ] && continue
  log "$g | $(mem)"
  out=$(./reproduce.sh "$g"); echo "$out"
  if echo "$out" | grep -q "^   ok "; then touch "$DONE/$g"; else log "$g FAILED; stopping"; exit 1; fi
done
# 3. the arena replication (starts and stops the Minecraft server itself), then its summary figure
if [ ! -f "$DONE/arena-replication" ]; then
  log "arena replication | $(mem)"
  experiments/run_replication.sh 5 300 && python3 experiments/figure_replication.py && touch "$DONE/arena-replication"
fi
log "all done | $(mem)"
