#!/usr/bin/env bash
# Drop N flies into a world.  Usage:  experiments/run_flock.sh "f,m,f" [wild|arena] [seconds]
#   sexes: f = female (FlyWire brain), m = male (MaleCNS brain + nerve cord)
#   world: wild (server/wild on port 25566, generated terrain) or arena (superflat, port 25565)
# Env: ARM=off|mb plasticity, US=dan|wiring teaching signal for ARM=mb (default dan: sugar/pain -> identified DANs),
#      AL=specific|published antennal lobe (default specific: odors are told apart; see RESEARCH_NOTES 16),
#      STATE=virgin,fed,... imposed internal state (see run_brain.py --state), NECTAR=all|<odor classes> which flowers
#      taste of sugar, TP="x,y,z" drop point (default: near world spawn; flies are spread 2 blocks apart), TRIAL label,
#      VIEW=1 to open a browser viewer per fly (ports 3007+), EXTRA="..." extra brain args.
set -euo pipefail
cd "$(dirname "$0")/.."
SEXES=${1:-f,m}; WORLD=${2:-wild}; DUR=${3:-0}
ARM=${ARM:-off}; US=${US:-dan}; AL=${AL:-specific}; NECTAR=${NECTAR:-all}; TRIAL=${TRIAL:-flock}; VIEW=${VIEW:-1}
PORT=$([ "$WORLD" = wild ] && echo 25566 || echo 25565)
IFS=',' read -r -a SX <<< "$SEXES"
N=${#SX[@]}
mkdir -p logs
ROSTER=logs/roster_${TRIAL}.json
python3 - "$SEXES" "$ROSTER" <<'PY'
import json, sys
sx = sys.argv[1].split(","); names = {f"fly{i+1}": ("male" if s.strip().lower().startswith("m") else "female") for i, s in enumerate(sx)}
json.dump(names, open(sys.argv[2], "w")); print("[flock] roster", names)
PY
PIDS=(); BOTS=()
cleanup() { kill "${PIDS[@]}" "${BOTS[@]}" 2>/dev/null; wait "${PIDS[@]}" "${BOTS[@]}" 2>/dev/null; }
trap 'cleanup; exit 0' INT TERM
for i in $(seq 0 $((N-1))); do
  DS=$([ "${SX[$i]:0:1}" = m ] || [ "${SX[$i]:0:1}" = M ] && echo malecns || echo flywire)
  python3 brain/run_brain.py --name "fly$((i+1))" --port $((8765+i)) --plasticity "$ARM" --us "$US" --al "$AL" --dataset "$DS" ${STATE:+--state "$STATE"} ${EXTRA:-} > "logs/flock_${TRIAL}_brain$((i+1)).out" 2>&1 &
  PIDS+=($!)
done
echo "[flock] loading $N brains ..."; sleep 45
for i in $(seq 0 $((N-1))); do
  VP=$([ "$VIEW" = 1 ] && echo $((3007+i)) || echo 0)
  TPARG=""
  if [ -n "${TP:-}" ]; then IFS=',' read -r X Y Z <<< "$TP"; TPARG="--tp=$((X + 2*i)),$Y,$Z"; fi
  node bot/bot.js --name "fly$((i+1))" --brain "ws://127.0.0.1:$((8765+i))" --viewer "$VP" --port "$PORT" --roster "$ROSTER" \
       --sex "$([ "${SX[$i]:0:1}" = m ] || [ "${SX[$i]:0:1}" = M ] && echo male || echo female)" $TPARG --duration="$DUR" --trial="$TRIAL" --nectar "$NECTAR" \
       $([ "$WORLD" = arena ] && [ "$i" = 0 ] && echo "--build-arena --arenaY=64") > "logs/flock_${TRIAL}_bot$((i+1)).out" 2>&1 &
  BOTS+=($!); sleep 4
done
echo "[flock] $N flies in '$WORLD' (viewers http://localhost:3007..). Ctrl-C stops everything; logs/flock_${TRIAL}_*.out"
wait "${BOTS[@]}"     # bots exit at --duration; the brains are then shut down (they never exit on their own)
cleanup
