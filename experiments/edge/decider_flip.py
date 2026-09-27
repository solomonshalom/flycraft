#!/usr/bin/env python3
"""Is the deciders' silence a few wrong sign guesses? (RESEARCH_NOTES 23; the hostile-referee review of draft 6)

The E/I analysis (ei-deciders, analysis_A.md) traced most of the inhibition the senses send to the female's deciders to
a handful of cell types whose GABA identity is a classifier's prediction, not a measurement:
AOTU064 (onto pC1d under cVA), AVLP531, PS088, CB0584 (onto pC1e), WED104, PVLP021 (onto vpoEN under touch); and oviIN
(onto oviDN; GABA measured by FISH, Wang et al. 2020). This probe removes that inhibition in three ways and asks whether
the deciders then answer the senses:
  silence6   the six predicted-GABA types' output x 0
  flip6      the six types' output x -1 (i.e. excitatory: what the deciders see if every one of these guesses is wrong)
  silence7   the six plus oviIN x 0
  intact     the paper's model
Also writes the six types' transmitter predictions and confidences.
  python experiments/edge/decider_flip.py --seeds 3 --out-dir experiments/results_edge/decider-flip
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge
import numpy as np, pandas as pd, scipy.sparse as sp
from common import input_groups, output_groups, make_sim, run_trials
from flybrain import connectome

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--hz", type=float, default=100)
ap.add_argument("--gains", default="1.0")
ap.add_argument("--out-dir", required=True)
a = ap.parse_args()

PRED = ["AOTU064", "AVLP531", "PS088", "CB0584", "WED104", "PVLP021"]
tmp, out = _edge.safe_out(os.path.join(a.out_dir, "decider_flip.csv"))
tmp_t, out_t = _edge.safe_out(os.path.join(a.out_dir, "decider_flip_types.csv"))

cx = connectome.load(dataset="flywire", signs="known", eln_scale=0.25)
print(cx, flush=True)
nb = cx.neurons
pred_idx = np.flatnonzero(nb.cell_type.isin(PRED).to_numpy())
ovi_idx = np.flatnonzero((nb.cell_type == "oviIN").to_numpy())
info = nb.iloc[np.r_[pred_idx, ovi_idx]][["cell_type", "side", "top_nt", "top_nt_conf", "known_nt"]].copy(); info["top_nt_conf"] = pd.to_numeric(info.top_nt_conf, errors="coerce")
info["row_sign"] = [float(np.sign(cx.W[i].sum())) for i in np.r_[pred_idx, ovi_idx]]
info["out_synapses"] = [float(abs(cx.W[i]).sum()) for i in np.r_[pred_idx, ovi_idx]]
info.to_csv(tmp_t, index=False); _edge.finish(tmp_t, out_t)
print(info.groupby("cell_type").agg(n=("side", "size"), top_nt=("top_nt", "first"), conf=("top_nt_conf", "mean"), sign=("row_sign", "mean")).round(2), flush=True)

IN = input_groups(cx)
DRIVES = ["none", "cVA (Or67d/DA1)", "song/sound (JO-A)", "touch (all head bristles)", "cVA + touch", "pheromones + song + touch",
          "Or47b + song", "Or47b + touch", "cVA + song"]
s = cx.select
OUT = output_groups(cx)
for t in ("pC1a", "pC1b", "pC1c", "pC1d", "pC1e", "vpoEN", "DNp37"):
    OUT[t] = s(cell_type=f"^{t}$")
OUT = {k: v for k, v in OUT.items() if len(v)}
W0 = cx.W
VARIANTS = {"intact": None, "silence6": (pred_idx, 0.0), "flip6": (pred_idx, -1.0), "silence7": (np.r_[pred_idx, ovi_idx], 0.0)}
rows, t0 = [], time.time()
for vname, mod in VARIANTS.items():
    if mod is None:
        W = W0
    else:
        scale = np.ones(cx.n); scale[mod[0]] = mod[1]
        W = (sp.diags(scale) @ W0).tocsr(); W.eliminate_zeros()
    cx.W = W
    for g in [float(x) for x in a.gains.split(",")]:
        sim = make_sim(cx, gain=g)
        for d in DRIVES:
            groups = [] if d == "none" else IN[d]
            r = run_trials(sim, groups, a.hz, a.ms, a.seeds, OUT, extra={"variant": vname, "gain": g, "input": d})
            rows += r
            df = pd.DataFrame(r)
            print(f"{vname:9s} g{g:g} {d:28s} " + " ".join(f"{k.split(' ')[0]} {df[k].mean():5.1f}" for k in
                  ("pC1a", "pC1b", "pC1c", "pC1d", "pC1e", "aIPg aggr", "vpoEN", "DNp37", "oviDN egg", "DNp13 reject", "DNa L", "DNa R") if k in df)
                  + f"  ({time.time() - t0:.0f}s)", flush=True)
        del sim
cx.W = W0
pd.DataFrame(rows).to_csv(tmp, index=False); _edge.finish(tmp, out)
_edge.sidecar(out, {"pred_types": PRED, "n_pred": int(len(pred_idx)), "n_oviIN": int(len(ovi_idx)), "seeds": a.seeds, "ms": a.ms, "hz": a.hz, "gains": a.gains})
print("wrote", out, out_t)
