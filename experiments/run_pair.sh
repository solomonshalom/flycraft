#!/usr/bin/env bash
# Two flies in one arena (the social-behavior setup). Requires the server to be running.
#   experiments/run_pair.sh off     # both flies: fixed connectome (innate arm)
#   experiments/run_pair.sh mb      # both flies: mushroom-body plasticity on (learning arm)
# Logs land in logs/<name>_<arm>_<timestamp>.csv ; Ctrl-C stops everything.
set -euo pipefail
cd "$(dirname "$0")/.."
# Env overrides: NO_FOOD=1 odor-free chamber, DS1/DS2 dataset per fly (flywire=female, malecns=male), ARENA_R radius (blocks), ARENA_Y floor height (use 64 for the browser viewer), TP1/TP2 start positions, YAW1/YAW2 facing (deg), DUR seconds (0 = until Ctrl-C), TRIAL label,
# SYNC=1 both bots wait for each other before starting brain, log and clock (RESEARCH_NOTES 23; off = the old 6-s stagger),
# STATE1/STATE2 imposed internal state per fly (run_brain.py --state, e.g. virgin for the female, courting for the male); extra args go to both brains
ARM=${1:-off}; shift || true
US=${US:-dan}; AL=${AL:-specific}      # teaching signal for ARM=mb; antennal lobe variant (see RESEARCH_NOTES 16)
TP1=${TP1:--8,-60,0}; TP2=${TP2:-8,-60,0}; YAW1=${YAW1:--90}; YAW2=${YAW2:-90}; DUR=${DUR:-0}; TRIAL=${TRIAL:-$ARM}
DS1=${DS1:-flywire}; DS2=${DS2:-flywire}     # dataset per fly: flywire (female) | malecns (male)
python3 brain/run_brain.py --name fly1 --port 8765 --plasticity "$ARM" --us "$US" --al "$AL" --dataset "$DS1" ${STATE1:+--state "$STATE1"} "$@" & B1=$!
python3 brain/run_brain.py --name fly2 --port 8766 --plasticity "$ARM" --us "$US" --al "$AL" --dataset "$DS2" ${STATE2:+--state "$STATE2"} "$@" & B2=$!
cleanup() { kill $B1 $B2 $N1 $N2 2>/dev/null; wait $B1 $B2 2>/dev/null; }
trap 'cleanup; exit 0' INT TERM
sleep 40   # let both brains load (MaleCNS takes longer)
SEX1=$([ "$DS1" = malecns ] && echo male || echo female); SEX2=$([ "$DS2" = malecns ] && echo male || echo female)
node bot/bot.js --name fly1 --brain ws://127.0.0.1:8765 --viewer "${VIEW1:-3007}" --sex "$SEX1" --others "$SEX2" --build-arena ${NO_FOOD:+--noFood} --arenaRadius="${ARENA_R:-16}" --arenaY="${ARENA_Y:--60}" --tp="$TP1" --yaw="$YAW1" --duration="$DUR" --trial="$TRIAL" ${SYNC:+--waitFor=fly2} & N1=$!
sleep 6
node bot/bot.js --name fly2 --brain ws://127.0.0.1:8766 --viewer "${VIEW2:-3008}" --sex "$SEX2" --others "$SEX1" --tp="$TP2" --yaw="$YAW2" --duration="$DUR" --trial="$TRIAL" ${SYNC:+--waitFor=fly1} & N2=$!
wait $N1 $N2
cleanup
