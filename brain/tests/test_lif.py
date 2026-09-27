#!/usr/bin/env python3
"""Checks on the simulation core.

1. The numba kernel in `legacy` mode reproduces the first-version numpy implementation (same semantics,
   different RNG stream -> rates must agree within Poisson noise).
2. The Shiu-faithful kernel gives the same rates at dt = 0.1 / 0.2 / 0.5 ms (0.1 = Brian2 default).
3. Speed of each.
Run:  python brain/tests/test_lif.py [--dataset flywire|malecns]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain import lif_legacy_numpy as old
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder

ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="flywire"); ap.add_argument("--ms", type=float, default=500); ap.add_argument("--seeds", type=int, default=3)
a = ap.parse_args()
cx = connectome.load(dataset=a.dataset)
senses = SensoryEncoder(cx, verbose=False); motor = MotorDecoder(cx, verbose=False)
s = cx.select
OUT = {"feed": motor.groups["feed"], "DNa L": motor.groups["turn_L"], "DNa R": motor.groups["turn_R"], "GF": motor.groups["jump"],
       "MDN": motor.groups["back"], "DNp13": s(cell_type=r"^DNp13$"), "PPL1": s(cell_class="^DAN$", cell_type=r"^PPL1"), "KC": s(cell_class="^Kenyon_Cell$")}
COND = {"silence": {}, "sugar@100": {"grn_sugar": 100}, "sugar+bitter@100": {"grn_sugar": 100, "grn_bitter": 100},
        "cVA@100": {"orn_cva": 100}, "touch@100": {"bristle": 100}, "sound JO-B@100": {"jo_sound": 100}}

def drive_of(cond):
    idx, rate = [], []
    for g, hz in cond.items():
        ii = senses.groups[g]; idx.append(ii); rate.append(np.full(len(ii), hz, np.float32))
    return (np.concatenate(idx) if idx else np.zeros(0, int)), (np.concatenate(rate) if rate else np.zeros(0, np.float32))

def measure(make_sim, label):
    sim = make_sim()
    res = {}
    for name, cond in COND.items():
        idx, rate = drive_of(cond)
        rows = []; wall = 0
        for seed in range(a.seeds):
            if hasattr(sim, "seed"): sim.seed(seed)
            else: sim.rng = np.random.default_rng(seed)
            sim.reset(); sim.set_drive(idx, rate)
            t0 = time.perf_counter(); counts, _ = sim.run(a.ms); wall += time.perf_counter() - t0
            rows.append({k: counts[v].sum() / max(len(v), 1) / (a.ms / 1000) for k, v in OUT.items()} | {"spikes": int(counts.sum()), "active%": 100 * (counts > 0).mean()})
        m = {k: np.mean([r[k] for r in rows]) for k in rows[0]}; sd = {k: np.std([r[k] for r in rows]) for k in rows[0]}
        res[name] = (m, sd)
        print(f"  {label:28s} {name:18s} {wall/a.seeds*1000:7.0f} ms/run | " + " ".join(f"{k} {m[k]:6.1f}±{sd[k]:<4.1f}" for k in OUT) + f" | spikes {m['spikes']:9.0f} active {m['active%']:.2f}%", flush=True)
    return res

W = cx.W; g = 0.275 * cx.w_syn_scale
print(f"\n== {a.dataset}: {cx.n} neurons, {W.nnz} connections; {a.ms:.0f} ms x {a.seeds} seeds\n")
print("-- 1. legacy semantics: old numpy vs numba kernel (dt 0.5)")
r_old = measure(lambda: old.LIF(W, old.LIFParams(dt=0.5, w_syn=g), seed=0), "numpy legacy dt0.5")
r_new = measure(lambda: LIF(W, LIFParams(dt=0.5, w_syn=g, legacy=True), seed=0), "numba legacy dt0.5")
print("-- 2. Shiu-faithful kernel at three time steps")
r01 = measure(lambda: LIF(W, LIFParams(dt=0.1, w_syn=g), seed=0), "numba shiu dt0.1")
r02 = measure(lambda: LIF(W, LIFParams(dt=0.2, w_syn=g), seed=0), "numba shiu dt0.2")
r05 = measure(lambda: LIF(W, LIFParams(dt=0.5, w_syn=g), seed=0), "numba shiu dt0.5")

def agree(ra, rb, label):
    bad = []
    for name in COND:
        for k in OUT:
            ma, sa = ra[name][0][k], ra[name][1][k]; mb, sb = rb[name][0][k], rb[name][1][k]
            tol = 3 * max(sa, sb, 0.15 * max(ma, mb), 1.0)
            if abs(ma - mb) > tol: bad.append(f"{name}/{k}: {ma:.1f} vs {mb:.1f}")
    print(f"{label}: " + ("AGREE" if not bad else "DIFFER -> " + "; ".join(bad)))
agree(r_old, r_new, "old numpy vs numba legacy")
agree(r01, r02, "shiu dt0.1 vs dt0.2")
agree(r01, r05, "shiu dt0.1 vs dt0.5")
agree(r_new, r02, "legacy vs shiu semantics (expected to differ)")
