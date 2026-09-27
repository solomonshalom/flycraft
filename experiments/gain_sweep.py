#!/usr/bin/env python3
"""Robustness of key responses to the per-synapse weight (gain). Both datasets.

The per-synapse weight is the one free constant in the model (0.275 mV, Shiu et al.; MaleCNS scaled to match
input density). A claim counts as "from the wiring" only if it holds across gains 0.7-1.4 (RESEARCH_NOTES 14g: 0.5x
transmits almost nothing, 2.0x runs away) and is absent with no input. The model variant comes from the environment
(FLYBRAIN_SIGNS / FLYBRAIN_ELN) and is part of the output file name.
  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/gain_sweep.py --dataset flywire --gains 0.5 0.7 1.0 1.4 2.0 --seeds 3
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, make_sim, run_trials, fmt

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--gains", type=float, nargs="+", default=[0.5, 0.7, 1.0, 1.4, 2.0])
ap.add_argument("--ms", type=float, default=600)
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--hz", type=float, default=100)
a = ap.parse_args()
cx = connectome.load(dataset=a.dataset); print(cx)
IG = input_groups(cx)
keep_in = ["cVA (Or67d/DA1)", "food odor", "sound (JO-B)", "touch (all head bristles)", "sugar GRNs", "ppk25 only (female CHC)",
           "cVA + touch", "contact pheromone (ppk23/25)", "song/sound (JO-A)",
           # added 17 Sep under the specific lobe: odor -> giant fiber (16i), odor does not gate touch -> DNp13 (16i), fly odor, CO2
           "food + touch", "aversive odor (DA2/DL4)", "Or88a (VA1d)", "Or47b (VA1v)", "CO2 (V)"]
INPUTS = {"none": []} | {k: IG[k] for k in keep_in if k in IG}
OG = output_groups(cx)
keep_out = ["DNa L", "DNa R", "GF jump", "MDN back", "DNp13 reject", "pC1d/e aggr", "aIPg aggr", "pC1a recept", "vpoEN/DN accept",
            "P1/pC1 male", "pIP10 song cmd", "song MNs", "feed MNs", "MN9", "PAM (reward DA)", "PPL1 (punish DA)", "KC"]
OUTPUTS = {k: OG[k] for k in keep_out if k in OG}
rows, t0 = [], time.time()
for gain in a.gains:
    sim = make_sim(cx, gain=gain)
    for name, groups in INPUTS.items():
        r = run_trials(sim, groups, a.hz, a.ms, a.seeds, OUTPUTS, extra={"gain": gain, "input": name})
        rows += r; d = pd.DataFrame(r)
        print(f"gain {gain:4.2f} {name:28s} active {d.active_frac.mean()*100:5.1f}% | " +
              " ".join(f"{k.split(' ')[0]} {d[k].mean():6.1f}" for k in OUTPUTS) + f"  ({d.wall_s.mean():.1f}s/run, {time.time()-t0:.0f}s)", flush=True)
df = pd.DataFrame(rows)
out = os.path.join(RES, f"gain_sweep_{a.dataset}_{cx.variant}.csv"); df.to_csv(out, index=False); print("wrote", out)
