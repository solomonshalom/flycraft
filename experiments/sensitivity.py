#!/usr/bin/env python3
"""Sensitivity of the key results to *our* choices: the model variant (transmitter-sign rule x eLN output scale;
MaleCNS: what its 67 "unclear"-transmitter local neurons do), stimulus rate, time step, numerics, connection table
and threshold. (Gain is covered by gain_sweep.py; touch-bristle subsets are inputs in social_probe.py.)

The baseline is the model the environment selects (FLYBRAIN_SIGNS / FLYBRAIN_ELN; the paper's model is known signs
with eLN x0.25) and the output file carries its variant, so the published-model table (sensitivity_flywire.csv,
RESEARCH_NOTES 14s) is kept. One connectome is held in memory at a time.
  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/sensitivity.py --dataset flywire|malecns [--seeds 3] [--ms 600]
Writes experiments/results/sensitivity_<dataset>_<variant>.csv and prints one row per condition.
"""
import argparse, gc, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, make_sim, run_trials

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=600)
a = ap.parse_args()

# (input, output) pairs: the claims of the answer table (RESEARCH_NOTES 15, 16l); pairs absent from a dataset are skipped
PAIRS = [("sugar GRNs", "MN9"), ("sugar GRNs", "feed MNs"),
         ("touch (all head bristles)", "DNp13 reject"), ("cVA + touch", "DNp13 reject"), ("food + touch", "DNp13 reject"),
         ("touch (all head bristles)", "MDN back"), ("ppk25 + touch", "DNp13 reject"),
         ("cVA (Or67d/DA1)", "DNa L"), ("cVA (Or67d/DA1)", "DNa R"), ("food odor", "DNa L"), ("food odor", "DNa R"),
         ("sound (JO-B)", "GF jump"), ("food odor", "GF jump"), ("aversive odor (DA2/DL4)", "GF jump"),
         ("cVA (Or67d/DA1)", "PPL1 (punish DA)"), ("food odor", "PPL1 (punish DA)"), ("food odor", "PAM (reward DA)"),
         ("food odor", "KC"), ("cVA (Or67d/DA1)", "KC"),
         ("cVA (Or67d/DA1)", "DNp13 reject"), ("cVA (Or67d/DA1)", "MN9"), ("cVA (Or67d/DA1)", "song MNs"),
         ("cVA (Or67d/DA1)", "pC1d/e aggr"), ("cVA (Or67d/DA1)", "aIPg aggr"), ("cVA (Or67d/DA1)", "P1/pC1 male"), ("cVA (Or67d/DA1)", "pIP10 song cmd"),
         ("contact pheromone (ppk23/25)", "MDN back"), ("contact pheromone (ppk23/25)", "song MNs"), ("contact pheromone (ppk23/25)", "PPL1 (punish DA)")]

# conditions: dict keys conn / min_syn / signs / eln / unclear select the connectome (None = the environment's choice),
# hz / dt / legacy the simulation
CONDITIONS = [("baseline (env model options, all conns, 100 Hz, dt 0.2)", dict())]
if a.dataset == "flywire":
    CONDITIONS += [("published model: Shiu signs, eLN x1", dict(signs="shiu", eln=1.0)),
                   ("known signs, eLN x1", dict(signs="known", eln=1.0)),
                   ("Shiu signs, eLN x0.25", dict(signs="shiu", eln=0.25)),
                   ("known signs, eLN x0.5", dict(signs="known", eln=0.5)),
                   ("known signs, eLN x0.1", dict(signs="known", eln=0.1))]
else:
    CONDITIONS += [("published model: eLN x1", dict(signs="shiu", eln=1.0)),
                   ("eLN x0.5", dict(eln=0.5)), ("eLN x0.1", dict(eln=0.1)),
                   ("eLN x0.25, unclear LNs inhibitory", dict(unclear="inhibitory")),
                   ("eLN x0.25, unclear LNs silent", dict(unclear="silent")),
                   ("eLN x1, unclear LNs inhibitory", dict(eln=1.0, unclear="inhibitory"))]
CONDITIONS += [("stimulus 50 Hz", dict(hz=50)), ("stimulus 150 Hz (Shiu default r_poi; the body's maximum)", dict(hz=150)),
               ("dt 0.1 ms (Brian2 default)", dict(dt=0.1)), ("dt 0.5 ms", dict(dt=0.5)),
               ("legacy numerics (first version)", dict(legacy=True)),
               ("connections >= 5 synapses", dict(min_syn=5))]
if a.dataset == "flywire":
    CONDITIONS += [("Zenodo table, top_nt signs, >= 5 synapses (first version)", dict(conn="zenodo", min_syn=5)),
                   ("Zenodo table, top_nt signs, all connections", dict(conn="zenodo", min_syn=1))]

key_of = lambda o: (o.get("conn"), o.get("min_syn"), o.get("signs"), o.get("eln"), o.get("unclear"))
groups = {}
for label, opt in CONDITIONS:
    groups.setdefault(key_of(opt), []).append((label, opt))
rows, t0, base_variant = [], time.time(), None
for (conn, min_syn, signs, eln, unclear), conds in groups.items():
    cx = connectome.load(dataset=a.dataset, conn=conn, min_syn=min_syn, signs=signs, eln_scale=eln, unclear_ln=unclear)
    print(cx, flush=True)
    base_variant = base_variant or cx.variant
    IG = input_groups(cx); OG = output_groups(cx)
    for label, opt in conds:
        sim = make_sim(cx, dt=opt.get("dt", 0.2), legacy=opt.get("legacy", False))
        hz = opt.get("hz", 100)
        res = {"condition": label, "connectome": cx.variant, "signs": cx.signs, "eln_scale": cx.eln_scale, "unclear_ln": cx.unclear_ln,
               "hz": hz, "dt": opt.get("dt", 0.2), "legacy": opt.get("legacy", False)}
        for inp in sorted(set(p[0] for p in PAIRS)):
            if inp not in IG:
                continue
            outs = {o: OG[o] for i2, o in PAIRS if i2 == inp and o in OG}
            if not outs:
                continue
            r = run_trials(sim, IG[inp], hz, a.ms, a.seeds, outs)
            d = pd.DataFrame(r)
            for o in outs:
                res[f"{inp} -> {o}"] = d[o].mean(); res[f"{inp} -> {o} sd"] = d[o].std()
            res[f"{inp} active%"] = d.active_frac.mean() * 100
        rows.append(res)
        show = [("sugar GRNs", "MN9"), ("touch (all head bristles)", "DNp13 reject"), ("food + touch", "DNp13 reject"), ("cVA (Or67d/DA1)", "DNa L"),
                ("cVA (Or67d/DA1)", "DNa R"), ("food odor", "DNa L"), ("food odor", "DNa R"), ("food odor", "GF jump"), ("sound (JO-B)", "GF jump"),
                ("food odor", "PPL1 (punish DA)"), ("food odor", "KC"), ("cVA (Or67d/DA1)", "DNp13 reject"), ("cVA (Or67d/DA1)", "MN9"),
                ("contact pheromone (ppk23/25)", "MDN back")]
        print(f"{label:52s} " + " ".join(f"{i.split(' ')[0]}->{o.split(' ')[0]} {res[f'{i} -> {o}']:6.1f}" for i, o in show if f"{i} -> {o}" in res)
              + f"  ({time.time()-t0:.0f}s)", flush=True)
        del sim
    del cx, IG, OG; gc.collect()
df = pd.DataFrame(rows)
out = os.path.join(RES, f"sensitivity_{a.dataset}_{base_variant}.csv"); df.to_csv(out, index=False); print("wrote", out)
