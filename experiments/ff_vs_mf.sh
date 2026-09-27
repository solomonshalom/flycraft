#!/usr/bin/env bash
# Female-female vs male-female encounters, same chamber, same duration. Tests: is the female's touch-evoked
# rejection output (DNp13) lower when the toucher is a male (cVA present)?
cd "$(dirname "$0")/.."
DUR=${DUR:-240}
NO_FOOD=${NO_FOOD:-} DS1=flywire DS2=flywire ARENA_R=6 ARENA_Y=64 TP1=-2,64,0 TP2=2,64,0 YAW1=-90 YAW2=90 DUR=$DUR TRIAL=ff${NO_FOOD:+_nofood} experiments/run_pair.sh off > logs/pair_ff.out 2>&1
sleep 3
NO_FOOD=${NO_FOOD:-} DS1=malecns DS2=flywire ARENA_R=6 ARENA_Y=64 TP1=-2,64,0 TP2=2,64,0 YAW1=-90 YAW2=90 DUR=$DUR TRIAL=mf${NO_FOOD:+_nofood} experiments/run_pair.sh off > logs/pair_mf.out 2>&1
echo done
