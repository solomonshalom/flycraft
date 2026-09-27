#!/usr/bin/env python3
"""Calibrate a documented "walking substrate": background Poisson kicks on every neuron (--noise-hz of run_brain.py).

In a truly odor-free chamber nothing drives the female's turning DNs (RESEARCH_NOTES 18a, 18c), so a female-female
pair stands still and the encounter question cannot be asked. The published model has no spontaneous activity, so
the substrate has to be ours and is reported as such. This script measures, per noise rate, what the substrate does
on its own (no input) and what it does to the reflexes the answer table rests on (touch -> DNp13, touch -> DNa
suppression, sugar -> MN9, food odor -> DNa), so that the rate used in the arena can be chosen and defended.

  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/noise_floor.py --dataset flywire|malecns [--seeds 3] [--ms 1000]
Writes experiments/results/noise_floor_<dataset>_<variant>.csv
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, make_sim, run_trials, fmt

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--noise", default="0,0.02,0.05,0.1,0.2,0.5,1.0", help="comma list of background rates (Hz per neuron)")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--hz", type=float, default=100.0)
ap.add_argument("--suffix", default="", help="appended to the output name (e.g. _10s for a steady-state run with --ms 10000)")
a = ap.parse_args()
cx = connectome.load(dataset=a.dataset); print(cx)
IG = input_groups(cx); OG = output_groups(cx)
keep_in = ["touch (all head bristles)", "food odor", "food + touch", "sugar GRNs", "cVA (Or67d/DA1)", "contact pheromone (ppk23/25)", "ppk25 + touch"]
INPUTS = {"none": []} | {k: IG[k] for k in keep_in if k in IG}
keep_out = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "MN9", "leg MNs", "wing MNs", "song MNs",
            "pC1d/e aggr", "aIPg aggr", "P1/pC1 male", "KC", "PPL1 (punish DA)", "PAM (reward DA)", "DN all"]
OUTPUTS = {k: OG[k] for k in keep_out if k in OG}
show = [k for k in ("DNa L", "DNa R", "DNp09", "leg MNs", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "KC", "DN all") if k in OUTPUTS]
rows, t0 = [], time.time()
for noise in [float(x) for x in a.noise.split(",")]:
    sim = make_sim(cx, noise_hz=noise)
    for iname, groups in INPUTS.items():
        r = run_trials(sim, groups, a.hz, a.ms, a.seeds, OUTPUTS, extra={"noise_hz": noise, "input": iname})
        rows += r; d = pd.DataFrame(r)
        print(f"noise {noise:4.2f} | {iname:28s} act {d.active_frac.mean()*100:4.1f}% | " +
              " ".join(f"{k.split(' ')[0]} {fmt(d[k].mean(), d[k].std())}" for k in show) + f" ({time.time()-t0:.0f}s)", flush=True)
    del sim
df = pd.DataFrame(rows)
out = os.path.join(RES, f"noise_floor_{a.dataset}_{cx.variant}{a.suffix}.csv")
if os.path.exists(out):                       # extra rates are added to the table, rerun rates replace their rows
    old = pd.read_csv(out); old = old[~old.noise_hz.isin(df.noise_hz.unique())]
    df = pd.concat([old, df], ignore_index=True).sort_values(["noise_hz", "input", "seed"], kind="stable")
df.to_csv(out, index=False); print("wrote", out)
