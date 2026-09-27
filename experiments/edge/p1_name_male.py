#!/usr/bin/env python3
"""Which male P1/pC1 neurons fire? (RESEARCH_NOTES 23; the gain-map-male pass mark "no single P1/pC1 neuron above about
5 Hz at <=1.4, otherwise name it" failed, and no earlier file records single neurons.)

Runs the paper's male model (FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25) under cVA, touch and their combination at gains 1.0
and 1.4 and writes the rate of every one of the 148 P1/pC1 neurons (cell_type ^pC1_|^P1_), with its type and side, plus the
group readouts of experiments/common.py for a check against map_gain_male.csv and touch_dose_male.csv.
  python experiments/edge/p1_name_male.py --seeds 3 --ms 1000 --out-dir experiments/results_edge/p1-name-male
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge
import numpy as np, pandas as pd
from common import input_groups, output_groups, make_sim, drive_of
from flybrain import connectome

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--gains", default="1.0,1.4")
ap.add_argument("--out-dir", required=True)
a = ap.parse_args()

tmp_n, out_n = _edge.safe_out(os.path.join(a.out_dir, "p1_name_male_neurons.csv"))
tmp_g, out_g = _edge.safe_out(os.path.join(a.out_dir, "p1_name_male_groups.csv"))

cx = connectome.load(dataset="malecns", signs="known", eln_scale=0.25)
print(cx, flush=True)
nb = cx.neurons
IN = input_groups(cx)
OUT = output_groups(cx)
p1 = np.asarray(OUT["P1/pC1 male"])
print(f"P1/pC1: {len(p1)} neurons, {nb.iloc[p1].cell_type.nunique()} types", flush=True)
cVA, touch = IN["cVA (Or67d/DA1)"], IN["touch (all head bristles)"]
DRIVES = {"none": ([], 100), "cVA (Or67d/DA1)": (cVA, 100), "touch (all head bristles)": (touch, 100),
          "cVA + touch": (cVA + touch, 100), "cVA + touch@200": ([(g, 100) for g in cVA] + [(g, 200) for g in touch], None)}
cols = ["cell_type", "side"] + [c for c in ("root_id", "bodyId", "id") if c in nb.columns][:1]
info = nb.iloc[p1][cols].reset_index(drop=True)
nrows, grows, t0 = [], [], time.time()
for g in [float(x) for x in a.gains.split(",")]:
    sim = make_sim(cx, gain=g)
    for dname, (groups, hz) in DRIVES.items():
        idx, rate = drive_of(groups, hz if hz is not None else 0)
        for seed in range(a.seeds):
            sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
            counts, _ = sim.run(a.ms)
            hzs = counts[p1] / (a.ms / 1000)
            d = info.copy(); d["gain"] = g; d["drive"] = dname; d["seed"] = seed; d["hz"] = hzs
            nrows.append(d)
            row = {"gain": g, "drive": dname, "seed": seed, "n_driven": int(len(idx))}
            for k, v in OUT.items():
                row[k] = float(counts[v].sum() / len(v) / (a.ms / 1000)) if len(v) else float("nan")
            row["P1/pC1 max1"] = float(hzs.max()); row["P1/pC1 n>0"] = int((hzs > 0).sum())
            grows.append(row)
        dd = pd.concat(nrows[-a.seeds:]).groupby(["cell_type", "side"]).hz.mean().sort_values(ascending=False)
        top = ", ".join(f"{t}/{s} {v:.1f}" for (t, s), v in dd.head(5).items() if v > 0)
        print(f"g{g:g} {dname:24s} max1 {max(r['P1/pC1 max1'] for r in grows[-a.seeds:]):5.1f}  top: {top}  ({time.time() - t0:.0f}s)", flush=True)
    del sim
pd.concat(nrows).to_csv(tmp_n, index=False); _edge.finish(tmp_n, out_n)
pd.DataFrame(grows).to_csv(tmp_g, index=False); _edge.finish(tmp_g, out_g)
_edge.sidecar(out_n, {"seeds": a.seeds, "ms": a.ms, "gains": a.gains, "n_p1": int(len(p1)), "drives": list(DRIVES)})
print("wrote", out_n, out_g)
