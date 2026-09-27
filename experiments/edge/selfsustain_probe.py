#!/usr/bin/env python3
"""Self-sustained firing after an input is switched off (RESEARCH_NOTES 23; edge-case follow-up to persistence-female).

The persistence step found that 10 s of any smell at 100 Hz, or the 0.2 Hz hum, leaves about 2,000 neurons firing on
their own for at least 3 s after all input stops (paper's model, female). This probe asks what that state is:
  - under which model settings it exists (variants: the paper's known+eln0.25, shiu+eln0.25, known (eLN x1), the
    published shiu; gains; the male),
  - how strong a smell must be to switch it on (drive rates),
  - how long it lasts (1-s bins over a long off phase),
  - whether it is one state or one per smell (Jaccard overlap of the neurons active in the last off bin),
  - which neurons make it up (super_class / cell_class / cell_type counts of the last off bin).

  python experiments/edge/selfsustain_probe.py --dataset flywire --variants known+eln0.25,shiu+eln0.25,known,shiu \
      --drives 'cVA (Or67d/DA1);food odor;song/sound (JO-A)' --rates 25,50,100 --gains 1 --on-ms 3000 --off-ms 20000 \
      --seeds 2 --out-dir experiments/results_edge/selfsustain
Writes selfsustain_<dataset>.csv (one row per variant x gain x drive x rate x seed x bin), _composition.csv (the neurons
active in the last off bin, by class), _overlap.csv (Jaccard between the final active sets), and a JSON sidecar.
"""
import argparse, gc, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge
import numpy as np, pandas as pd
from common import input_groups, output_groups, make_sim, drive_of
from flybrain import connectome

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", choices=["flywire", "malecns"], default="flywire")
ap.add_argument("--variants", default="known+eln0.25", help="comma list: <signs>[+eln<x>] (signs shiu|known)")
ap.add_argument("--drives", default="cVA (Or67d/DA1);food odor", help="';'-list of common.input_groups names")
ap.add_argument("--rates", default="100", help="comma list of drive rates (Hz)")
ap.add_argument("--gains", default="1", help="comma list of synaptic gains")
ap.add_argument("--noise-on", type=float, default=0.0, help="hum (Hz) during the on phase only (drive 'none' + this = the hum test)")
ap.add_argument("--on-ms", type=float, default=3000)
ap.add_argument("--off-ms", type=float, default=20000)
ap.add_argument("--bin-ms", type=float, default=1000)
ap.add_argument("--seeds", type=int, default=2)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--tag", default="")
ap.add_argument("--cut-sensory-input", action="store_true", help="remove every synapse onto a sensory neuron (super_class sensory), so the brain cannot re-excite its own sense organs")
a = ap.parse_args()

tag = f"_{a.tag}" if a.tag else ""
out_csv = os.path.join(a.out_dir, f"selfsustain_{a.dataset}{tag}.csv")
tmp_csv, out_csv = _edge.safe_out(out_csv)
tmp_cmp, out_cmp = _edge.safe_out(os.path.join(a.out_dir, f"selfsustain_{a.dataset}{tag}_composition.csv"))
tmp_ovl, out_ovl = _edge.safe_out(os.path.join(a.out_dir, f"selfsustain_{a.dataset}{tag}_overlap.csv"))

def parse_variant(v):
    signs, eln = v, 1.0
    if "+eln" in v:
        signs, e = v.split("+eln"); eln = float(e)
    if signs not in ("shiu", "known"):
        raise SystemExit(f"bad variant {v!r}")
    return signs, eln

rows, comp, finals = [], [], {}
t0 = time.time()
for v in a.variants.split(","):
    signs, eln = parse_variant(v)
    cx = connectome.load(dataset=a.dataset, signs=signs, eln_scale=eln)
    if a.cut_sensory_input:
        import scipy.sparse as sp
        keep = (cx.neurons.super_class.fillna("") != "sensory").to_numpy().astype(float)
        n_cut = int(cx.W[:, np.flatnonzero(keep == 0)].nnz)
        cx.W = (cx.W @ sp.diags(keep)).tocsr(); cx.W.eliminate_zeros(); cx.variant += "+nosensoryin"
        print(f"cut {n_cut} connections onto {int((keep == 0).sum())} sensory neurons", flush=True)
    print(cx, flush=True)
    IN, OUT = input_groups(cx), output_groups(cx)
    OUT = {k: OUT[k] for k in ("DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "MN9", "feed MNs", "PPL1 (punish DA)",
                               "PAM (reward DA)", "KC", "MBON", "DN all", "pC1a recept", "pC1d/e aggr", "vpoEN/DN accept", "P1/pC1 male",
                               "pIP10 song cmd") if k in OUT}
    nb = cx.neurons
    for g in [float(x) for x in a.gains.split(",")]:
        sim = make_sim(cx, gain=g)
        for dname in a.drives.split(";"):
            if dname != "none" and dname not in IN:
                print(f"  skip {dname!r}: not an input group of {a.dataset}"); continue
            groups = [] if dname == "none" else IN[dname]
            for hz in [float(x) for x in a.rates.split(",")]:
                idx, rate = drive_of(groups, hz)
                for s in range(a.seeds):
                    sim.seed(s); sim.reset(); sim.p.noise_hz = a.noise_on; sim.set_drive(idx, rate)
                    t_ms, phase = 0.0, "on"
                    last = None
                    for ph, dur in (("on", a.on_ms), ("off", a.off_ms)):
                        if ph == "off":
                            sim.set_drive(np.zeros(0, np.int64), np.zeros(0, np.float32)); sim.p.noise_hz = 0.0
                        done = 0.0
                        while done < dur - 1e-9:
                            b = min(a.bin_ms, dur - done)
                            counts, _ = sim.run(b)
                            done += b; t_ms += b
                            act = counts > 0
                            if len(idx):
                                act_nd = act.copy(); act_nd[idx] = False
                            else:
                                act_nd = act
                            row = {"variant": cx.variant, "gain": g, "drive": dname, "rate_hz": hz, "noise_on": a.noise_on, "seed": s,
                                   "phase": ph, "t_end_ms": t_ms, "bin_ms": b, "spikes_per_s": counts.sum() / (b / 1000),
                                   "n_active": int(act.sum()), "n_active_undriven": int(act_nd.sum())}
                            for k, gi in OUT.items():
                                row[k] = float(counts[gi].sum() / len(gi) / (b / 1000))
                            rows.append(row)
                            last = act_nd
                        sim.p.noise_hz = 0.0
                    key = (cx.variant, g, dname, hz, s)
                    finals[key] = np.flatnonzero(last)
                    if len(finals[key]):
                        sub = nb.iloc[finals[key]]
                        for col in ("super_class", "cell_class", "cell_type"):
                            vc = sub[col].fillna("na").value_counts()
                            for name, n in (vc.head(15) if col == "cell_type" else vc).items():
                                comp.append({"variant": cx.variant, "gain": g, "drive": dname, "rate_hz": hz, "seed": s, "level": col, "name": name, "n": int(n)})
                    r_last = rows[-1]
                    print(f"  {cx.variant} g{g:g} {dname:24s} {hz:5.0f} Hz s{s}: end of off {r_last['n_active_undriven']:5d} neurons "
                          f"{r_last['spikes_per_s']:8.0f} sp/s DNa {r_last.get('DNa L', 0):5.1f}/{r_last.get('DNa R', 0):5.1f}  ({time.time() - t0:.0f}s)", flush=True)
        del sim; gc.collect()
    del cx; gc.collect()

pd.DataFrame(rows).to_csv(tmp_csv, index=False); _edge.finish(tmp_csv, out_csv)
pd.DataFrame(comp).to_csv(tmp_cmp, index=False); _edge.finish(tmp_cmp, out_cmp)
keys = [k for k in finals if len(finals[k])]
ovl = []
for i, k1 in enumerate(keys):
    for k2 in keys[i + 1:]:
        s1, s2 = set(finals[k1]), set(finals[k2])
        ovl.append({"a": "|".join(map(str, k1)), "b": "|".join(map(str, k2)), "n_a": len(s1), "n_b": len(s2), "jaccard": len(s1 & s2) / len(s1 | s2)})
pd.DataFrame(ovl).to_csv(tmp_ovl, index=False); _edge.finish(tmp_ovl, out_ovl)
_edge.sidecar(out_csv, {"cut_sensory_input": a.cut_sensory_input, "variants": a.variants, "drives": a.drives, "rates": a.rates, "gains": a.gains, "on_ms": a.on_ms,
                        "off_ms": a.off_ms, "bin_ms": a.bin_ms, "seeds": a.seeds, "noise_on": a.noise_on})
print("wrote", out_csv, out_cmp, out_ovl)
