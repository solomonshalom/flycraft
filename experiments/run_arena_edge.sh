#!/usr/bin/env bash
# Arena edge cases of 27 Sep 2026 (RESEARCH_NOTES 23): the encounter series the audit found weakest, run again with a
# synchronised start (SYNC=1: neither fly walks before the other is placed; the old 6-s launch stagger put fly1 on fly2's
# start point in some trials), new brain seeds (SEED0=100: seeds 101-105; every earlier series used 1-5), and, as a
# lesion control, touch removed (--mask bristle).
#   sync-noise0.2          two females / male + female on the 0.2 Hz hum     (repeats 19b/c `noise0.2`, 22b `rep-noise0.2`)
#   sync-noise0.2-notouch  two females on the hum with no touch input        (does touch keep them together?)
#   sync-clean             male + female in the clean box, 300 s               (the replication's clean mf ran too slowly)
# Logs go to logs/edge_arena/<label>/ so that no script that globs logs/ (encounter_stats, replication_stats, figures,
# paper_numbers) pools them with the paper's series; experiments/edge/arena_audit.py --logs reads them.
# Waits for the offline queues (run_guarded.sh) to finish and for memory (the male brain + a female + the server need
# about 7 GB), starts and stops the server, clears the chamber once.
#   caffeinate -i experiments/run_arena_edge.sh [SERIES="ff-hum ff-notouch mf-hum mf-clean"] [DUR=600]
set -uo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.pyenv/shims:$PATH"
DUR=${DUR:-600}; N=${N:-5}; SERIES=${SERIES:-ff-hum ff-notouch mf-hum mf-clean}
log() { echo "== $* $(date '+%F %T')"; }
free_pct() { memory_pressure 2> /dev/null | awk -F': ' '/free percentage/ {gsub("%", "", $2); print $2+0}'; }
while pgrep -f "run_guarded.sh" > /dev/null; do sleep 60; done
log "offline queues finished"
wait_mem() { while f=$(free_pct); [ "${f:-0}" -lt "$1" ]; do log "waiting for memory: ${f}% free, need $1%"; sleep 120; done; }
wait_mem 45
( cd server && exec java -Xms512M -Xmx1536M -XX:+UseG1GC -jar paper.jar --nogui > ../logs/edge_arena/server.out 2>&1 ) &
SERVER=$!
for i in $(seq 1 120); do nc -z 127.0.0.1 25565 2> /dev/null && break; sleep 5; done
nc -z 127.0.0.1 25565 2> /dev/null || { echo "server did not come up"; kill $SERVER 2> /dev/null; exit 1; }
sleep 20; log "server up (pid $SERVER)"
node experiments/survey_chamber.js --port 25565 --radius 45 --clear 2>&1 | grep "\[survey\]"
[ "${PIPESTATUS[0]}" = 0 ] || { echo "chamber not clean, stopping"; kill $SERVER; exit 2; }
export NUMBA_NUM_THREADS=3 VIEW1=0 VIEW2=0 NO_FOOD=1 ARENA_R=6 ARENA_Y=64 SYNC=1 SEED0=100
series() {   # $1 pairing ff|mf, $2 label (no '_'), $3 extra brain args, $4 duration
  local ds1=flywire; [ "$1" = mf ] && ds1=malecns
  mkdir -p "logs/edge_arena/$2"
  wait_mem $([ "$1" = mf ] && echo 45 || echo 35)
  log "$1 $2 ($N x ${4}s, brain args '$3')"
  DS1=$ds1 DS2=flywire LABEL="$2" BRAIN_ARGS="$3 --log-dir logs/edge_arena/$2" experiments/trials.sh off "$N" "$4"
  mv logs/trial_off_"${ds1:0:1}"f_*_"$2".out "logs/edge_arena/$2/" 2> /dev/null
}
for s in $SERIES; do case "$s" in
  ff-hum)     series ff sync-noise0.2         "--noise-hz 0.2"               "$DUR" ;;
  ff-notouch) series ff sync-noise0.2-notouch "--noise-hz 0.2 --mask bristle" "$DUR" ;;
  mf-hum)     series mf sync-noise0.2         "--noise-hz 0.2"               "$DUR" ;;
  mf-clean)   series mf sync-clean            ""                             300 ;;
esac; done
kill -TERM "$SERVER" 2> /dev/null; wait "$SERVER" 2> /dev/null; log "server stopped"
python3 experiments/edge/arena_audit.py --logs logs/edge_arena/*/ --out-dir experiments/results_edge/arena-edge > logs/edge_arena/audit.out 2>&1
log "done: experiments/results_edge/arena-edge/"
