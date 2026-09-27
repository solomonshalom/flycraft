#!/usr/bin/env bash
# odor concentration sweep with left, right and bilateral presentations, under the three sign rules
cd "$(dirname "$0")/.."
export PYTHONWARNINGS=ignore NUMBA_NUM_THREADS=3
FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset flywire --seeds 3 > logs/odor_dose_flywire.out 2>&1
FLYBRAIN_SIGNS=shiu  FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset flywire --seeds 3 > logs/odor_dose_flywire_shiu.out 2>&1
FLYBRAIN_CONN=zenodo FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset flywire --seeds 3 > logs/odor_dose_flywire_zenodo.out 2>&1
FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset malecns --seeds 3 > logs/odor_dose_malecns.out 2>&1
echo done > logs/probes4_done.flag
