#!/usr/bin/env python3
"""Innate social sensorimotor map: stimulate each social input, read every social output.

Fixed connectome (plasticity off). Each input class is driven as Poisson kicks at --hz for --ms of brain
time; outputs are mean firing rates over the trial; --seeds independent trials (default 5) give error bars.
This is the circuit-level answer to "what does the wiring alone do with a social stimulus?".

  python experiments/social_probe.py --dataset flywire|malecns [--seeds 5] [--ms 1000] [--hz 100] [--noise-hz 0]
Writes experiments/results/social_probe_<dataset>_<variant>_noise<n>.csv and prints a table.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, make_sim, run_trials, fmt

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=5)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--hz", type=float, default=100)
ap.add_argument("--noise-hz", type=float, default=0.0)
ap.add_argument("--gain", type=float, default=1.0)
ap.add_argument("--dataset", choices=["flywire", "malecns"], default="flywire")
ap.add_argument("--out", default=None)
a = ap.parse_args()

cx = connectome.load(dataset=a.dataset)
print(cx)
INPUTS = {"none": []} | input_groups(cx)
OUTPUTS = output_groups(cx)
print("outputs:", {k: len(v) for k, v in OUTPUTS.items()})
sim = make_sim(cx, gain=a.gain, noise_hz=a.noise_hz)
rows, t0 = [], time.time()
show = [k for k in ("DNa L", "DNa R", "MDN back", "GF jump", "pC1a recept", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject",
                    "P1/pC1 male", "pIP10 song cmd", "song MNs", "feed MNs", "MN9", "PAM (reward DA)", "PPL1 (punish DA)") if k in OUTPUTS]
for name, groups in INPUTS.items():
    r = run_trials(sim, groups, a.hz, a.ms, a.seeds, OUTPUTS, extra={"input": name})
    rows += r
    d = pd.DataFrame(r)
    print(f"{name:32s} act {d.active_frac.mean()*100:4.1f}% | " + " ".join(f"{k.split(' ')[0]} {fmt(d[k].mean(), d[k].std())}" for k in show)
          + f"  ({time.time()-t0:.0f}s)", flush=True)
df = pd.DataFrame(rows)
out = a.out or os.path.join(RES, f"social_probe_{a.dataset}_{cx.variant}_noise{a.noise_hz:g}{'' if a.gain == 1 else f'_gain{a.gain:g}'}.csv")
df.to_csv(out, index=False)
print("wrote", out)
