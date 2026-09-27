#!/usr/bin/env python3
"""Compare the numba kernel with a Brian2 reference run (brian2_reference.py) on the same export.

  python brain/tests/compare_brian2.py --conn export.npz --ref ref.npz [--dt 0.2] [--legacy]
Prints per-group rates (Brian2 vs kernel), the per-neuron spike-count correlation, and the number of neurons
that are active in one but not the other.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, scipy.sparse as sp
from flybrain.lif import LIF, LIFParams

ap = argparse.ArgumentParser()
ap.add_argument("--conn", required=True); ap.add_argument("--ref", required=True)
ap.add_argument("--dt", type=float, default=0.2); ap.add_argument("--legacy", action="store_true"); ap.add_argument("--gain", type=float, default=1.0)
a = ap.parse_args()
z = np.load(a.conn); r = np.load(a.ref)
N = int(z["n"]); W = sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(N, N))
ms = float(r["ms"]); ref_counts = r["counts"]; seeds = ref_counts.shape[0]
drive = [s for s in str(r["drive"]).split(",") if s]
idx = np.concatenate([z[d.split(":")[0]] for d in drive]) if drive else np.zeros(0, int)
rate = np.concatenate([np.full(len(z[d.split(":")[0]]), float(d.split(":")[1]), np.float32) for d in drive]) if drive else np.zeros(0, np.float32)
sim = LIF(W, LIFParams(dt=a.dt, w_syn=0.275 * float(z["w_syn_scale"]) * a.gain, legacy=a.legacy), seed=0)
my = np.zeros_like(ref_counts)
for s in range(seeds):
    sim.seed(s); sim.reset(); sim.set_drive(idx, rate)
    t0 = time.perf_counter(); c, _ = sim.run(ms); wall = time.perf_counter() - t0
    my[s] = c
    print(f"kernel seed {s}: {c.sum()} spikes, {(c > 0).mean()*100:.2f}% active, {wall:.1f}s  | brian2: {ref_counts[s].sum()} spikes, {(ref_counts[s] > 0).mean()*100:.2f}% active, {float(r['wall'][s]):.0f}s")
groups = [k for k in z.files if k.startswith("out_") or k.startswith("in_")]
print(f"\n{'group':16s} {'n':>5s} {'brian2 Hz':>12s} {'kernel Hz':>12s}")
for k in groups:
    g = z[k]
    rb = ref_counts[:, g].sum(1) / len(g) / (ms / 1000); rm = my[:, g].sum(1) / len(g) / (ms / 1000)
    print(f"{k:16s} {len(g):5d} {rb.mean():7.2f}±{rb.std():<4.2f} {rm.mean():7.2f}±{rm.std():<4.2f}")
mb, mm = ref_counts.mean(0), my.mean(0)
act = (mb > 0) | (mm > 0)
print(f"\nper-neuron mean-count correlation over {act.sum()} neurons active in either: r = {np.corrcoef(mb[act], mm[act])[0,1]:.4f}")
print(f"active in brian2 only: {((mb > 0) & (mm == 0)).sum()}   active in kernel only: {((mm > 0) & (mb == 0)).sum()}   both: {((mb > 0) & (mm > 0)).sum()}")
top = np.argsort(-np.abs(mb - mm))[:10]
print("largest per-neuron differences (idx, brian2, kernel):", [(int(i), float(mb[i]), float(mm[i])) for i in top])
