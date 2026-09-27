#!/usr/bin/env python3
"""Shuffled-connectome control: does the map come from the specific wiring or just from neuron density?

Degree-preserving rewiring (Maslov & Sneppen 2002): repeatedly pick two connections a->b and c->d and swap
their targets (a->d, c->b), rejecting self-loops and duplicates. Every neuron keeps its exact number of inputs
and outputs and every connection keeps its weight and sign (which travel with the presynaptic neuron); only
*who talks to whom* is randomized. `--mode block` restricts swaps to targets of the same super-class
(sensory / central / optic / descending / ...), preserving the coarse sensory -> central -> descending
architecture and randomizing only the identity of the partner within it.

If the shuffled brains reproduce the innate map, the map is a density artifact and the paper collapses.
  python experiments/shuffle_control.py --dataset flywire --shuffles 3 --mode global|block --swaps-per-edge 3
Writes experiments/results/shuffle_<dataset>_<variant>_<mode>.csv (rows for the intact connectome included).
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, scipy.sparse as sp
from common import RES, connectome, input_groups, output_groups, run_trials, fmt
from flybrain.lif import LIF, LIFParams


def rewire(W: sp.csr_matrix, rng: np.random.Generator, swaps_per_edge: float = 3.0, block: np.ndarray | None = None,
           batch: int = 1_000_000, verbose: bool = True) -> tuple[sp.csr_matrix, float]:
    C = W.tocoo(); pre = C.row.astype(np.int64); post = C.col.astype(np.int64); w = C.data.copy()
    N = W.shape[0]; E = len(pre)
    keys = np.sort(pre * N + post)
    target = int(swaps_per_edge * E); done = 0; touched = np.zeros(E, bool); t0 = time.time()
    while done < target:
        m = min(batch, E // 2)
        perm = rng.permutation(E)[:2 * m]; e1, e2 = perm[:m], perm[m:]
        a, b, c, d = pre[e1], post[e1], pre[e2], post[e2]
        ok = (a != c) & (b != d) & (a != d) & (c != b)
        if block is not None:
            ok &= block[b] == block[d]
        n1, n2 = a * N + d, c * N + b
        ok &= n1 != n2
        pos = np.searchsorted(keys, n1); ok &= ~((pos < len(keys)) & (keys[np.minimum(pos, len(keys) - 1)] == n1))
        pos = np.searchsorted(keys, n2); ok &= ~((pos < len(keys)) & (keys[np.minimum(pos, len(keys) - 1)] == n2))
        # new keys must be unique within the batch
        allnew = np.concatenate([n1[ok], n2[ok]]); _, cnt = np.unique(allnew, return_counts=True)
        if (cnt > 1).any():
            dup = set(_[cnt > 1].tolist()); bad = np.array([x in dup or y in dup for x, y in zip(n1[ok], n2[ok])], bool)
            idx_ok = np.flatnonzero(ok); ok[idx_ok[bad]] = False
        e1o, e2o = e1[ok], e2[ok]
        post[e1o], post[e2o] = d[ok], b[ok]
        touched[e1o] = True; touched[e2o] = True
        keys = np.sort(pre * N + post)
        done += int(ok.sum())
        if verbose:
            print(f"  [rewire] {done/E:.2f} swaps/edge, {touched.mean()*100:.1f}% edges moved ({time.time()-t0:.0f}s)", flush=True)
    Wn = sp.csr_matrix((w, (pre, post)), shape=(N, N), dtype=np.float32); Wn.sum_duplicates()
    return Wn, float(touched.mean())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="flywire")
    ap.add_argument("--shuffles", type=int, default=3)
    ap.add_argument("--mode", choices=["global", "block"], default="global")
    ap.add_argument("--swaps-per-edge", type=float, default=3.0)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--ms", type=float, default=800)
    ap.add_argument("--hz", type=float, default=100)
    a = ap.parse_args()
    cx = connectome.load(dataset=a.dataset); print(cx)
    IG = input_groups(cx); OG = output_groups(cx)
    keep_in = ["cVA (Or67d/DA1)", "food odor", "sound (JO-B)", "song/sound (JO-A)", "touch (all head bristles)", "sugar GRNs", "cVA + touch",
               "contact pheromone (ppk23/25)", "ppk25 + touch"]
    INPUTS = {"none": []} | {k: IG[k] for k in keep_in if k in IG}
    keep_out = ["DNa L", "DNa R", "GF jump", "MDN back", "DNp13 reject", "pC1d/e aggr", "aIPg aggr", "pC1a recept", "vpoEN/DN accept",
                "P1/pC1 male", "pIP10 song cmd", "feed MNs", "MN9", "PAM (reward DA)", "PPL1 (punish DA)", "KC", "DN all"]
    OUTPUTS = {k: OG[k] for k in keep_out if k in OG}
    show = [k for k in ("GF jump", "MDN back", "DNp13 reject", "feed MNs", "MN9", "DNa L", "DNa R", "PPL1 (punish DA)", "P1/pC1 male", "DN all") if k in OUTPUTS]
    block = None
    if a.mode == "block":
        sc = cx.neurons.super_class.fillna("na").astype(str).to_numpy()
        block = pd.factorize(sc)[0]
    rows = []
    def run_all(W, label, extra):
        sim = LIF(W, LIFParams(w_syn=0.275 * cx.w_syn_scale), seed=0)
        for name, groups in INPUTS.items():
            r = run_trials(sim, groups, a.hz, a.ms, a.seeds, OUTPUTS, extra=extra | {"input": name}); rows.extend(r); d = pd.DataFrame(r)
            print(f"{label:14s} {name:28s} act {d.active_frac.mean()*100:5.2f}% | " + " ".join(f"{k.split(' ')[0]} {fmt(d[k].mean())}" for k in show), flush=True)
    run_all(cx.W, "intact", {"connectome": "intact", "shuffle": -1, "frac_moved": 0.0})
    for s in range(a.shuffles):
        print(f"== shuffle {s} ({a.mode}, {a.swaps_per_edge} swaps/edge)")
        Wn, moved = rewire(cx.W, np.random.default_rng(100 + s), a.swaps_per_edge, block)
        assert np.array_equal(np.diff(Wn.indptr), np.diff(cx.W.tocsr().indptr)), "out-degree changed"
        run_all(Wn, f"shuffle{s}", {"connectome": a.mode, "shuffle": s, "frac_moved": moved})
    df = pd.DataFrame(rows)
    out = os.path.join(RES, f"shuffle_{a.dataset}_{cx.variant}_{a.mode}.csv"); df.to_csv(out, index=False); print("wrote", out)
