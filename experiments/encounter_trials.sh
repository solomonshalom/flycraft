#!/usr/bin/env bash
# The rejection test with error bars: female-female vs male-female encounters, odor-free chamber, N trials each.
# Waits for any running flock demo to finish. Usage: experiments/encounter_trials.sh [N=5] [DUR=180]
# Env: NOISE=<Hz>  background Poisson rate on every neuron of both brains (a documented "walking substrate", ours; 0 = the
#                  published model, the default) -- the trial label and the log names carry it (noise0.3);
#      LABEL=<tag> suffix on the trial label (default: clean, or noise<NOISE>);
#      CONDS="ff mf" which pairings to run (ff = two females, mf = male fly1 + female fly2); STATE1/STATE2 imposed
#                  state per fly (run_pair.sh), e.g. CONDS=mf STATE2=virgin for a virgin female meeting a male;
#      CLEAR_R=<blocks> (default 45; 0 = skip) wipe every block we ever built within this radius of the origin before the
#                  trials and verify that no odorous block is left (experiments/survey_chamber.js): the 17 Sep trials
#                  (RESEARCH_NOTES 18h) ran with flower patches from an earlier learning run at the chamber's wall.
cd "$(dirname "$0")/.."
N=${1:-5}; DUR=${2:-180}
NOISE=${NOISE:-0}; CLEAR_R=${CLEAR_R:-45}
while pgrep -f "bot.js --name fly1" > /dev/null; do sleep 15; done
if [ "$CLEAR_R" != 0 ]; then
  echo "== clearing the world within $CLEAR_R blocks of the origin and checking for odorous blocks $(date)"
  node experiments/survey_chamber.js --port 25565 --radius "$CLEAR_R" --clear 2>&1 | grep "\[survey\]"
  [ "${PIPESTATUS[0]}" = 0 ] || { echo "chamber not clean, stopping"; exit 2; }
fi
if [ "$NOISE" != 0 ]; then export BRAIN_ARGS="--noise-hz $NOISE"; LABEL=${LABEL:-noise$NOISE}; else LABEL=${LABEL:-clean}; fi
export LABEL NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-3} VIEW1=0 VIEW2=0 NO_FOOD=1 ARENA_R=6 ARENA_Y=64
for cond in ${CONDS:-ff mf}; do
  case "$cond" in ff) DS1=flywire;; mf) DS1=malecns;; *) echo "unknown pairing $cond"; continue;; esac
  echo "== $cond trials (label $LABEL, brain args '${BRAIN_ARGS:-}', states '${STATE1:-}' / '${STATE2:-}') $(date)"
  DS1=$DS1 DS2=flywire experiments/trials.sh off "$N" "$DUR"
done
echo "== done $(date)"
