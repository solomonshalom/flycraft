#!/usr/bin/env python3
"""Why the appetitive memory cannot be expressed, and what it would take (RESEARCH_NOTES 16f-16h, WHATS_LEFT item 8).

16f: the reward-compartment MBONs (gamma5beta'2a, beta2beta'2a, beta'2mp, gamma4, alpha1) are glutamatergic, i.e.
inhibitory under the sign rule, and their postsynaptic targets are silent at rest and under odor. An appetitive
memory (KC->MBON depression) *removes* their inhibition, which in a silent target removes nothing: driving all of
them reaches 0 descending neurons. In the fly the targets carry ongoing activity (tonic input, neuromodulation).

Test: give the MBONs' postsynaptic targets (every neuron receiving >= --min-syn synapses from the set, KCs and
MBONs excluded) tonic Poisson activity at T Hz, and measure the odor-evoked descending output with the set's MBONs
(a) intact and (b) silenced (their output scaled to 0 = the memory at its floor for every odor: an upper bound on
what depression of one odor's KC->MBON synapses could do). The difference (b) - (a) is the behavioural expression
the model could show, as a function of T. Same for the punishment-compartment set (MBON14 alpha3 etc.), whose
targets are partly awake already (16f). Odor on the LEFT antenna (approach index = DNa L - R) and bilaterally.
  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/expression_probe.py [--tonic 0 5 10 20 40] [--odor vinegar] [--seeds 3] [--ms 1000]
Writes experiments/results/expression_probe_<dataset>_<variant>.csv
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, output_groups, make_sim
from flybrain.plasticity import REWARD_MBONS, PUNISH_MBONS
from flybrain.senses import SensoryEncoder

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--tonic", type=float, nargs="+", default=[0, 5, 10, 20, 40], help="Hz of tonic drive on the MBON targets")
ap.add_argument("--odor", default="vinegar"); ap.add_argument("--hz", type=float, default=150)
ap.add_argument("--min-syn", type=int, default=10, help="a target receives at least this many synapses from the MBON set")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
a = ap.parse_args()

cx = connectome.load(dataset=a.dataset); print(cx, flush=True)
senses = SensoryEncoder(cx, verbose=False)
OG = output_groups(cx)
OUT = {k: OG[k] for k in ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DN all", "feed MNs", "MN9", "DNp13 reject", "MBON", "KC", "PPL1 (punish DA)", "PAM (reward DA)"] if k in OG}
types = cx.neurons.hemibrain_type.fillna(cx.neurons.cell_type).fillna("").astype(str).to_numpy()
mbon = cx.select(cell_class="^MBON$"); kc = cx.select(cell_class="^Kenyon_Cell$")
Wabs = abs(cx.W)
sets = {}
for name, tset in (("reward", REWARD_MBONS), ("punish", PUNISH_MBONS)):
    m = mbon[np.isin(types[mbon], list(tset))]
    syn = np.asarray(Wabs[m].sum(axis=0)).ravel()
    tg = np.flatnonzero(syn >= a.min_syn)
    tg = tg[~np.isin(tg, mbon) & ~np.isin(tg, kc)]
    sub = cx.neurons.iloc[tg]
    sign = np.sign(np.asarray(cx.W[m].sum(axis=1)).ravel())
    tgd = tg[(sub.super_class == "descending").to_numpy()]          # the set's own descending targets (read out separately)
    sets[name] = (m, tg, tgd)
    print(f"[{name}] {len(m)} MBONs ({', '.join(sorted(set(types[m])))}; {int((sign < 0).sum())} inhibitory, {int((sign > 0).sum())} excitatory) -> "
          f"{len(tg)} targets with >= {a.min_syn} synapses ({int(syn[tg].sum())} synapses): super_class {sub.super_class.value_counts().head(6).to_dict()}; "
          f"DNs {int((sub.super_class == 'descending').sum())}; top types {sub.cell_type.value_counts().head(8).to_dict()}", flush=True)

sim = make_sim(cx)
rows, t0 = [], time.time()
for sname, (m, tg, tgd) in sets.items():
    for T in a.tonic:
        for state in ("intact", "silenced"):
            sim.restore_weights()
            if state == "silenced":
                sim.scale_output(m, 0.0)
            for pres in ("none", "L", "both"):
                if pres == "none":
                    oi, orate = np.zeros(0, np.int64), np.zeros(0, np.float32)
                else:
                    oi, orate = senses.odor(a.odor, side=None if pres == "both" else "L", r_max=a.hz)
                idx = np.concatenate([oi, tg]) if T > 0 else oi
                rate = np.concatenate([orate, np.full(len(tg), T, np.float32)]) if T > 0 else orate
                for seed in range(a.seeds):
                    sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
                    tw = time.perf_counter(); counts, _ = sim.run(a.ms); wall = time.perf_counter() - tw
                    r = {"mbon_set": sname, "tonic_hz": T, "mbons": state, "odor": pres, "seed": seed, "n_targets": int(len(tg)), "wall_s": round(wall, 2),
                         "active_frac": float((counts > 0).mean()), "total_spikes": int(counts.sum()),
                         "set MBONs Hz": float(counts[m].sum() / len(m) / (a.ms / 1000)), "targets Hz": float(counts[tg].sum() / max(len(tg), 1) / (a.ms / 1000)),
                         "n_target_dns": int(len(tgd)), "target DNs Hz": float(counts[tgd].sum() / len(tgd) / (a.ms / 1000)) if len(tgd) else float("nan")}
                    for k, v in OUT.items():
                        r[k] = float(counts[v].sum() / len(v) / (a.ms / 1000))
                    r["approach (L-R)"] = r["DNa L"] - r["DNa R"]
                    rows.append(r)
                d = pd.DataFrame(rows[-a.seeds:])
                print(f"[{sname:6s}] tonic {T:4.0f} Hz  MBONs {state:8s} odor {pres:4s} | set MBONs {d['set MBONs Hz'].mean():5.1f} targets {d['targets Hz'].mean():5.1f} Hz "
                      f"| DNa L/R {d['DNa L'].mean():5.1f}/{d['DNa R'].mean():5.1f} (L-R {d['approach (L-R)'].mean():+5.1f}) DNp09 {d['DNp09'].mean():4.1f} MDN {d['MDN back'].mean():4.1f} "
                      f"DN all {d['DN all'].mean():4.1f} target DNs {d['target DNs Hz'].mean():5.1f} feed {d['feed MNs'].mean():4.1f} GF {d['GF jump'].mean():4.1f} | brain {d.active_frac.mean()*100:4.1f}% ({time.time()-t0:.0f}s)", flush=True)
    sim.restore_weights()
df = pd.DataFrame(rows)
out = os.path.join(RES, f"expression_probe_{a.dataset}_{cx.variant}.csv"); df.to_csv(out, index=False); print("wrote", out)
