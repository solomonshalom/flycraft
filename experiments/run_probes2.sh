#!/usr/bin/env bash
# the odor concentration sweep under the other sign rules (is the contralateral bias wiring or labeling?)
cd "$(dirname "$0")/.."
export PYTHONWARNINGS=ignore NUMBA_NUM_THREADS=3
while [ ! -f logs/probes_done.flag ]; do sleep 20; done
FLYBRAIN_SIGNS=shiu  FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset flywire --seeds 3 > logs/odor_dose_flywire_shiu.out 2>&1
FLYBRAIN_CONN=zenodo FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 -u experiments/odor_dose.py --dataset flywire --seeds 3 > logs/odor_dose_flywire_zenodo.out 2>&1
echo done > logs/probes2_done.flag
# rerun the expression probe with the sets' own descending targets as a readout
FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 -u experiments/expression_probe.py > logs/expression_probe_flywire.out 2>&1
echo done > logs/probes3_done.flag
