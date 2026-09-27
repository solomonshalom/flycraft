#!/usr/bin/env python3
"""State arm, published lobe vs the paper's model: the cells the answer table rests on, side by side (RESEARCH_NOTES 19e).

  python experiments/state_compare.py --dataset flywire|malecns
Reads state_probe_<dataset>_<published variant>_state30.csv and state_probe_<dataset>_<paper variant>_state30.csv.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import RES

ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="flywire"); a = ap.parse_args()
pub, paper = {"flywire": ("shiu_min1", "shiu_min1+known+eln0.25"), "malecns": ("all_min1", "all_min1+eln0.25")}[a.dataset]
old = pd.read_csv(os.path.join(RES, f"state_probe_{a.dataset}_{pub}_state30.csv")); new = pd.read_csv(os.path.join(RES, f"state_probe_{a.dataset}_{paper}_state30.csv"))
outs = [c for c in new.columns if c in old.columns and c not in {"seed", "n_driven", "total_spikes", "active_frac", "wall_s", "state", "input"}]
show = [k for k in ("pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "oviDN egg", "P1/pC1 male", "pIP10 song cmd", "TN1 song", "song MNs", "wing MNs",
                    "MN9", "feed MNs", "DNa L", "DNa R", "MDN back", "PPL1 (punish DA)", "KC") if k in outs]
go = old.groupby(["state", "input"])[show].mean(); gn = new.groupby(["state", "input"])[show].mean()
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
print(f"== {a.dataset}: published lobe ({pub}) -> paper's model ({paper}); mean over seeds ({old.seed.nunique()} / {new.seed.nunique()}), 1 s, state neurons 30 Hz\n")
for state in gn.index.get_level_values(0).unique():
    print(f"--- {state}")
    for inp in gn.loc[state].index:
        if (state, inp) not in go.index:
            continue
        o, n = go.loc[(state, inp)], gn.loc[(state, inp)]
        cells = [f"{k.split(' ')[0]} {o[k]:.1f}->{n[k]:.1f}" for k in show if max(o[k], n[k]) >= 1]
        print(f"   {inp:32s} " + "  ".join(cells))
# the headline cells, in one table: state alone vs none alone
print("\n== state alone (input 'none'): published -> paper's model")
rows = []
for state in gn.index.get_level_values(0).unique():
    if (state, "none") in go.index:
        rows.append({"state": state} | {k: f"{go.loc[(state, 'none')][k]:.1f} -> {gn.loc[(state, 'none')][k]:.1f}" for k in show if max(go.loc[(state, 'none')][k], gn.loc[(state, 'none')][k]) >= 1})
print(pd.DataFrame(rows).fillna("").to_string(index=False))
# largest change of any hunger / satiety state relative to no state, both models
print("\n== hunger / satiety states: largest |change| vs no state over all inputs and readouts")
for label, g in (("published", go), ("paper", gn)):
    base = g.loc["none"]
    for state in [s for s in g.index.get_level_values(0).unique() if any(w in s for w in ("IPC", "DH44", "NPF", "SIFa", "AstA"))]:
        d = (g.loc[state] - base.reindex(g.loc[state].index)).abs()
        k = d.stack().idxmax(); print(f"   {label:9s} {state:22s} max |delta| {d.stack().max():5.1f} Hz  ({k[1]} with {k[0]})")
