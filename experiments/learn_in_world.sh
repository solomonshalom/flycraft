#!/usr/bin/env bash
# Learning from the surroundings: one fly in a chamber with two flower patches of different odor classes.
#   west: --patchA (default poppy = 'ester')   with nectar  -> tasting it drives the reward DANs (US)
#   east: --patchB (default dandelion = 'vinegar'), no nectar (pure odor cue)   [BITTER=vinegar makes it a punisher]
# Three phases on the same brain: PRE (plasticity frozen) -> TRAIN (plasticity on, the fly learns from what it
# walks into) -> POST (frozen). Then experiments/learn_stats.py compares odor-evoked MBON/DN activity and the time
# spent at each patch before and after, and reads which compartments hold the memory.
# EXPOSE=1 (default): as a T-maze experimenter places the fly in each odor tube, the fly is put into patch A for the
# first half of TRAIN and into patch B for the second half (its own left-looping walk otherwise keeps it wherever it
# starts); it is put back at the centre for POST. EXPOSE=0: free-operant, no placement.
#
#   experiments/learn_in_world.sh [trial]        env: PRE=120 TRAIN=300 POST=120 (s wall), R=10 chamber radius,
#       A=poppy B=dandelion, NECTAR=ester (odor classes that taste of sugar), BITTER='' (classes that taste bitter),
#       AL=specific|published, US=dan|wiring, DS=flywire|malecns, PORT=8767 (brain), VIEW=3009 (viewer, 0 = off), FLY=fly1 (body name),
#       EXPOSE=1|0 (place the fly in each patch during training), HOLD=0 (with EXPOSE=1: put the fly back on the patch
#       centre every HOLD s of training, i.e. the experimenter keeps it on the food, as a sugar-coated filter paper does
#       in a T-maze tube; 0 = place once), PATCH_R=2 (patch half-width in blocks: 2 = 5x5 flowers, 3 = 7x7),
#       TAU_DAN=0 (phasic teaching signal, s),
#       EXTRA="..." extra brain args (e.g. --state virgin --seed 3).  Requires ./run.sh server (port 25565).
set -euo pipefail
cd "$(dirname "$0")/.."
TRIAL=${1:-learn}; PRE=${PRE:-120}; TRAIN=${TRAIN:-300}; POST=${POST:-120}; R=${R:-10}
FLY=${FLY:-fly1}     # the body's player name: must be an op on the arena server (fly1-4 are; non-ops are kicked for the build commands)
A=${A:-poppy}; B=${B:-dandelion}; NECTAR=${NECTAR:-ester}; BITTER=${BITTER:-}; CLASSES=${CLASSES:-ester,vinegar}   # odor classes of A and B, for the probe
AL=${AL:-specific}; US=${US:-dan}; DS=${DS:-flywire}; PORT=${PORT:-8767}; VIEW=${VIEW:-3009}; EXPOSE=${EXPOSE:-1}; TAU_DAN=${TAU_DAN:-0}
HOLD=${HOLD:-0}; PATCH_R=${PATCH_R:-2}
CX=$(python3 -c "import sys; r=int(sys.argv[1]); print(max(3, round(r*0.55)))" "$R")   # patch centres at x = -CX (A) and +CX (B), as arena.js places them
place() { node experiments/experimenter.js --port 25565 --cmd "/tp $FLY $1 64 0 $2 0" > /dev/null 2>&1 || echo "[learn] placement failed"; }
# keep the fly at (x, yaw) for $3 s: place it once (HOLD=0) or again every HOLD s
hold() { local x=$1 yaw=$2 secs=$3 t=0 step; while [ "$t" -lt "$secs" ]; do place "$x" "$yaw"; step=$secs; [ "$HOLD" -gt 0 ] && [ "$HOLD" -lt $((secs - t)) ] && step=$HOLD; sleep "$step"; t=$((t + step)); done; }
mkdir -p logs
python3 brain/run_brain.py --name "$FLY" --port "$PORT" --plasticity mb --us "$US" --al "$AL" --dataset "$DS" --tau-dan "$TAU_DAN" ${EXTRA:-} > "logs/learn_${TRIAL}_brain.out" 2>&1 &
BRAIN=$!
cleanup() {
  kill ${BOT:-} 2>/dev/null || true
  kill -TERM $BRAIN 2>/dev/null || true
  for _ in $(seq 1 20); do kill -0 $BRAIN 2>/dev/null || break; sleep 0.5; done
  kill -KILL $BRAIN 2>/dev/null || true
  wait $BRAIN 2>/dev/null || true
}
trap 'cleanup; exit 0' INT TERM
echo "[learn] loading brain ($DS, al=$AL, us=$US) ..."; sleep 45
python3 experiments/brainctl.py --port "$PORT" freeze
python3 experiments/brainctl.py --port "$PORT" probe --odors "$CLASSES" > "logs/learn_${TRIAL}_probe_pre.json"    # graded readout before anything happened
TOTAL=$((PRE + TRAIN + POST))
node bot/bot.js --name "$FLY" --brain "ws://127.0.0.1:$PORT" --viewer "$VIEW" --port 25565 --build-arena --layout patches \
     --patchA "$A" --patchB "$B" --patchR "$PATCH_R" --arenaRadius="$R" --arenaY=64 --nectar "$NECTAR" ${BITTER:+--bitter "$BITTER"} \
     --tp=0,64,0 --duration="$((TOTAL + TRAIN + 120))" --trial="$TRIAL" > "logs/learn_${TRIAL}_bot.out" 2>&1 &     # slack: HOLD placements stretch TRAIN; the body is stopped by this script
BOT=$!
echo "[learn] PRE: $PRE s (plasticity frozen)"; sleep "$PRE"
python3 experiments/brainctl.py --port "$PORT" unfreeze; date +"[learn] %T TRAIN: $TRAIN s (plasticity on)"
if [ "$EXPOSE" = 1 ]; then
  echo "[learn] placed in patch A ($A) for $((TRAIN / 2)) s (hold every ${HOLD}s)"; hold "-$CX" 90 $((TRAIN / 2))
  echo "[learn] placed in patch B ($B) for $((TRAIN - TRAIN / 2)) s (hold every ${HOLD}s)"; hold "$CX" -90 $((TRAIN - TRAIN / 2))
else
  sleep "$TRAIN"
fi
python3 experiments/brainctl.py --port "$PORT" freeze; date +"[learn] %T POST: $POST s (frozen)"
[ "$EXPOSE" = 1 ] && place 0 0
sleep "$POST"
kill $BOT 2>/dev/null || true; wait $BOT 2>/dev/null || true
python3 experiments/brainctl.py --port "$PORT" memory > "logs/learn_${TRIAL}_memory.json" || true
python3 experiments/brainctl.py --port "$PORT" probe --odors "$CLASSES" > "logs/learn_${TRIAL}_probe_post.json" || true   # graded readout after learning
cleanup
CSV=$(ls -t logs/${FLY}_mb-*.csv | head -1)
echo "[learn] done; log $CSV"
python3 experiments/learn_stats.py "$CSV" --pre "$PRE" --train "$TRAIN" --post "$POST" --patchA "$A" --patchB "$B" --r "$R"
