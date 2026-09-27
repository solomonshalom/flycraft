#!/usr/bin/env bash
# The arena replication of 25-26 Sep 2026 (RESEARCH_NOTES 22): the three series the paper's arena argument leans on, run
# again under labels of their own so that encounter_stats.py keeps them apart from the series they repeat
# (the chamber is the 4th `_` field of the trial label, so a LABEL must not contain `_`).
#   rep-clean            two females and a male + female in the clean chamber            (repeats 19b `clean`)
#   rep-noise0.2         the same on the 0.2 Hz substrate                                  (repeats 19b/c `noise0.2`)
#   rep-noise0.2-virgin  a virgin female (SAG tonic) with a male on the substrate          (repeats 21b `noise0.2-virgin`)
# With WAIT=1 it first waits for a running ./reproduce.sh to finish (the arena must not share the CPU with the offline
# groups; do not set it when running this from reproduce.sh itself). Starts the Minecraft server if it is not up, runs the
# series one after another, stops the server it started, then summarises.
#   WAIT=1 caffeinate -i experiments/run_replication.sh [N=5] [DUR=300]      (SERIES="clean noise virgin" by default)
set -uo pipefail
cd "$(dirname "$0")/.."
N=${1:-5}; DUR=${2:-300}
log() { echo "== $* $(date '+%F %T')"; }
if [ "${WAIT:-0}" = 1 ]; then while pgrep -f "reproduce.sh" > /dev/null; do sleep 60; done; fi
log "starting the arena replication"
STARTED=0
if ! nc -z 127.0.0.1 25565 2> /dev/null; then
  ( cd server && exec java -Xms512M -Xmx1536M -XX:+UseG1GC -jar paper.jar --nogui > ../logs/replication_server.out 2>&1 ) &
  SERVER=$!; STARTED=1
  for i in $(seq 1 120); do nc -z 127.0.0.1 25565 2> /dev/null && break; sleep 5; done
  nc -z 127.0.0.1 25565 2> /dev/null || { echo "server did not come up"; kill $SERVER 2> /dev/null; exit 1; }
  sleep 20
  log "server up (pid $SERVER)"
fi
SERIES=${SERIES:-clean noise virgin}         # which series to run (the 26 Sep resume ran SERIES="noise virgin" with DUR=600)
for s_ in $SERIES; do case "$s_" in
  clean)  NOISE=0   LABEL=rep-clean                                  experiments/encounter_trials.sh "$N" "$DUR" ;;
  noise)  NOISE=0.2 LABEL=rep-noise0.2                               experiments/encounter_trials.sh "$N" "$DUR" ;;
  virgin) CONDS=mf STATE2=virgin NOISE=0.2 LABEL=rep-noise0.2-virgin experiments/encounter_trials.sh "$N" "$DUR" ;;
esac; done
log "trials done"
if [ "$STARTED" = 1 ]; then kill -TERM "$SERVER" 2> /dev/null; wait "$SERVER" 2> /dev/null; log "server stopped"; fi
python3 experiments/encounter_stats.py > logs/replication_encounter_stats.out 2>&1
python3 experiments/replication_stats.py --tex paper/tables_arena.tex > logs/replication_stats.out 2>&1
log "summary: experiments/results/replication_20260925.md, paper/tables_arena.tex"
