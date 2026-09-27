#!/usr/bin/env python3
"""Is "stop on contact" wiring or labelling? (RESEARCH_NOTES 18h, WHATS_LEFT item 3)

In the arena two females that touch stop walking: the bristle input shuts the turning DNs (DNa 12.6 / 12.5 Hz far ->
0.4 / 0.1 in contact). Offline it is `food + touch -> DNa` 6.7 / 3.1 vs `food alone` 21 / 13 under the paper's model
(known signs, eLN x0.25). This script runs that comparison -- and the same for cVA and for a background-noise walking
substrate -- under every transmitter-sign rule and connection table of the sensitivity axis (18e), so that the
suppression can be called the wiring's if it is there under all of them, or the sign rule's if it is not.

  python experiments/contact_stop.py --dataset flywire [--seeds 3] [--ms 600] [--noise 0.3]
Writes experiments/results/contact_stop_<dataset>.csv (one row per condition x input, mean and sd over seeds) and prints
the suppression index (1 - DNa with touch / DNa without) per condition.
"""
import argparse, gc, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, make_sim, run_trials

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=600)
ap.add_argument("--noise", type=float, default=0.3, help="background rate of the walking-substrate rows (0 = skip them)")
a = ap.parse_args()

# the sign-rule x eLN x connection-table axis of sensitivity.py (18e / 18k), same labels
if a.dataset == "flywire":
    CONDITIONS = [("paper's model: known signs, eLN x0.25", dict(signs="known", eln=0.25)),
                  ("published model: Shiu signs, eLN x1", dict(signs="shiu", eln=1.0)),
                  ("known signs, eLN x1", dict(signs="known", eln=1.0)),
                  ("Shiu signs, eLN x0.25", dict(signs="shiu", eln=0.25)),
                  ("known signs, eLN x0.5", dict(signs="known", eln=0.5)),
                  ("known signs, eLN x0.1", dict(signs="known", eln=0.1)),
                  ("Zenodo table, top_nt signs, >= 5 synapses (first version)", dict(conn="zenodo", min_syn=5, signs="known", eln=0.25)),
                  ("Zenodo table, top_nt signs, all connections", dict(conn="zenodo", min_syn=1, signs="known", eln=0.25))]
else:
    CONDITIONS = [("paper's model: eLN x0.25", dict(eln=0.25)), ("published model: eLN x1", dict(eln=1.0)),
                  ("eLN x0.25, unclear LNs inhibitory", dict(eln=0.25, unclear="inhibitory")),
                  ("eLN x0.25, unclear LNs silent", dict(eln=0.25, unclear="silent"))]
# (walking drive, the same with touch added): touch = all head bristles (BM_*)
PAIRS = [("food odor", "food + touch"), ("cVA (Or67d/DA1)", "cVA + touch"), ("Or47b (VA1v)", "Or47b + touch"), ("none", "touch (all head bristles)")]
if a.dataset == "malecns":
    PAIRS += [("contact pheromone (ppk23/25)", "ppk25 + touch")]
OUTS = ["DNa L", "DNa R", "DNp09", "MDN back", "DNp13 reject", "GF jump", "feed MNs", "leg MNs", "DN all"]

rows, t0 = [], time.time()
for label, opt in CONDITIONS:
    cx = connectome.load(dataset=a.dataset, conn=opt.get("conn"), min_syn=opt.get("min_syn"), signs=opt.get("signs"), eln_scale=opt.get("eln"), unclear_ln=opt.get("unclear"))
    print(cx, flush=True)
    IG = input_groups(cx); OG = output_groups(cx); IG["none"] = []
    outs = {o: OG[o] for o in OUTS if o in OG}
    sims = [("", make_sim(cx))] + ([(f" + noise {a.noise:g} Hz", make_sim(cx, noise_hz=a.noise))] if a.noise > 0 else [])
    for tag, sim in sims:
        for base, touched in PAIRS:
            if base not in IG or touched not in IG:
                continue
            if base == "none" and not tag:
                continue                                    # nothing drives the DNs without a substrate: no ratio to take
            r0 = pd.DataFrame(run_trials(sim, IG[base], 100, a.ms, a.seeds, outs)); r1 = pd.DataFrame(run_trials(sim, IG[touched], 100, a.ms, a.seeds, outs))
            row = {"condition": label + tag, "connectome": cx.variant, "signs": cx.signs, "eln_scale": cx.eln_scale, "unclear_ln": cx.unclear_ln, "noise_hz": a.noise if tag else 0.0,
                   "drive": base, "with_touch": touched}
            for o in outs:
                row[f"{o} alone"] = r0[o].mean(); row[f"{o} alone sd"] = r0[o].std(); row[f"{o} +touch"] = r1[o].mean(); row[f"{o} +touch sd"] = r1[o].std()
            dna0 = (r0["DNa L"] + r0["DNa R"]).mean() / 2; dna1 = (r1["DNa L"] + r1["DNa R"]).mean() / 2
            walk0 = dna0 if "leg MNs" not in outs else r0["leg MNs"].mean(); walk1 = dna1 if "leg MNs" not in outs else r1["leg MNs"].mean()
            row["DNa alone"] = dna0; row["DNa +touch"] = dna1; row["suppression"] = 1 - dna1 / dna0 if dna0 > 0.05 else np.nan
            row["walk alone"] = walk0; row["walk +touch"] = walk1
            rows.append(row)
            print(f"{label + tag:64s} {base:28s} DNa {r0['DNa L'].mean():5.1f}/{r0['DNa R'].mean():5.1f} -> +touch {r1['DNa L'].mean():5.1f}/{r1['DNa R'].mean():5.1f}"
                  f"  suppression {row['suppression']:5.2f}  DNp13 {r1['DNp13 reject'].mean():5.1f}  MDN {r1['MDN back'].mean():4.1f}"
                  + (f"  leg MNs {walk0:4.1f} -> {walk1:4.1f}" if "leg MNs" in outs else "") + f"  ({time.time()-t0:.0f}s)", flush=True)
        del sim
    del sims, cx, IG, OG; gc.collect()
df = pd.DataFrame(rows)
out = os.path.join(RES, f"contact_stop_{a.dataset}.csv"); df.to_csv(out, index=False); print("wrote", out)
