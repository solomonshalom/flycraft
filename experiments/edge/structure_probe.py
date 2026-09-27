#!/usr/bin/env python3
"""Structure probe (edge-case suite, DECISIONS.md item 11): what the wiring alone says. No simulation; loads W only.

W is loaded once with the published options passed explicitly (the environment is not applied to the raw load), then
each model variant is built with connectome.apply_model_options. Default variants: the paper's model (known+eln0.25),
the published signs with the paper's eLN scale (shiu+eln0.25, what the paper calls "the published signs") and the
published model (shiu = Shiu et al.'s signs, eLN x1). On MaleCNS `known` applies nothing (no known_nt), so variants
that build the same model are run once.

 (a) every sensory input group of common.input_groups (combinations = the union of their neurons) -> each decider
     (female pC1a, pC1b/c, pC1d/e, aIPg, vpoEN/DN, oviDN; male P1/pC1, pIP10, aIPg, vpoEN/DN, mAL) and two responding
     references (DNp13, MN9):
       hops        shortest hop count from any source neuron to any target neuron over all connections (the same in
                   every variant); hops_exc: through excitatory connections only (depends on the sign rule)
       n_paths_k   simple neuron-level paths of length k = 1..3 (one per connection whatever its synapse count; no
                   self-connections; exact: walks minus the ones that revisit a neuron)
       w_k         signed propagated weight after k hops. Wn = W / sum_i |W_ij| (column j = the signed fraction of
                   neuron j's input synapses), x_0 = 1 on the sources, x_k = x_{k-1} @ Wn, w_k = mean of x_k over the
                   target neurons; w_1 is the signed fraction of the targets' input synapses that come from the sources.
                   w_rect_k: x_k clipped at 0 after every hop; w_exc_k: through Wn+ (excitatory connections) only
       routes      type chains (source > type > ... > target) with the largest |contribution| to w_k, k = 1..4. A
                   chain's contribution is the exact sum over every neuron walk through those types, so the chains of
                   one k add up to w_k. k <= 3 is exhaustive; k = 4 is searched over the --beam strongest first and
                   last types (k4_beam_share = the part of w_4 those chains carry)
 (b) hunger / fullness neurons (state_groups IPC, DH44, NPF, SIFa, AstA) against SAG and pC1a-c (male: P1/pC1), with
     sugar GRNs as a reference: outgoing synapses, postsynaptic partners, top partner types, and the (a) metrics to
     MN9, feed MNs, PAM and PPL1
 (c) the neurons whose sign signs=known flips (FlyWire only), by super_class / cell_class / known transmitter /
     direction, with their output synapses, and how many are photoreceptors (super_class sensory, cell_class visual)
 (d) the antennal-lobe local neurons (cell_class ALLN) by top_nt and by sign under the Shiu and the known signs, and
     which of them each eLN scale multiplies (ALLN with a positive row sign after the sign rule)

  python experiments/edge/structure_probe.py [--dataset flywire|malecns] [--variants known+eln0.25,shiu+eln0.25,shiu]
         [--max-hops 8] [--routes 3] [--beam 8] [--limit N] [--out-dir experiments/results_edge/structure]
Writes structure_{paths,routes,state,signflips,aln}_<dataset>.csv and structure_<dataset>.md (+ .json sidecar).
"""
from __future__ import annotations

import argparse, dataclasses, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge  # noqa: E402  (puts experiments/ and brain/ on sys.path)
import numpy as np, pandas as pd, scipy.sparse as sp
from common import connectome, input_groups, output_groups, state_groups

K = 4                                                            # propagated weight and routes for k = 1..4 hops
DEC = {"flywire": ["pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "oviDN egg"],
       "malecns": ["P1/pC1 male", "pIP10 song cmd", "aIPg aggr", "vpoEN/DN accept", "mAL", "oviDN egg"]}
REFS = ["DNp13 reject", "MN9"]                                   # responding reflexes: positive references
HUNGER = ["fed (IPC tonic)", "fed (DH44 tonic)", "hungry (NPF tonic)", "SIFa tonic", "AstA tonic"]
COMPARE = {"flywire": ["virgin (SAG tonic)", "aroused female (pC1a-c tonic)"],
           "malecns": ["virgin (SAG tonic)", "courting male (P1/pC1 tonic)"]}
STATE_TGT = ["MN9", "feed MNs", "PAM (reward DA)", "PPL1 (punish DA)"]
REF_PAIRS = [("touch (all head bristles)", "DNp13 reject"), ("sugar GRNs", "MN9")]
SHORT = {"pC1a recept": "pC1a", "pC1d/e aggr": "pC1d/e", "aIPg aggr": "aIPg", "vpoEN/DN accept": "vpoEN/DN",
         "oviDN egg": "oviDN", "DNp13 reject": "DNp13 (ref)", "MN9": "MN9 (ref)", "P1/pC1 male": "P1/pC1",
         "pIP10 song cmd": "pIP10", "PAM (reward DA)": "PAM", "PPL1 (punish DA)": "PPL1"}


# ---- graph helpers (pure functions of sparse matrices) ----
def binary_nodiag(W):
    """Unweighted adjacency (float64, 1 per connection) without self-connections, and how many were dropped."""
    rows = np.repeat(np.arange(W.shape[0], dtype=np.int64), np.diff(W.indptr))
    keep = rows != W.indices
    A = sp.csr_matrix((np.ones(int(keep.sum())), (rows[keep], W.indices[keep])), shape=W.shape)
    return A, int((~keep).sum())


def bfs(Adj, S, max_hops):
    """Hop distance from the set S to every neuron along Adj's nonzero entries (-1 = not reached within max_hops)."""
    dist = np.full(Adj.shape[0], -1, np.int16); dist[S] = 0
    f = np.zeros(Adj.shape[0]); f[S] = 1.0
    AT = Adj.T
    for h in range(1, max_hops + 1):
        new = ((AT @ f) > 0) & (dist < 0)
        if not new.any():
            break
        dist[new] = h; f = new.astype(np.float64)
    return dist


class Paths:
    """Simple-path counts of length 1..3 from a source set S to a target set T (disjoint), A binary without diagonal.
    Length 1 and 2 walks are paths; a length-3 walk s>a>b>t is not a path iff b = s or a = t, so
    p3 = walks3 - sum_s r(s) d_T(s) - sum_t v1(t) r(t) + #(s>t>s>t), r = number of reciprocal partners."""
    def __init__(self, A):
        self.A = A
        self.R = A.multiply(A.T).tocsr()                          # R[i,j] = 1 if i->j and j->i
        self.r = np.asarray(self.R.sum(axis=1)).ravel()

    def source(self, S):
        s0 = np.zeros(self.A.shape[0]); s0[S] = 1.0
        AT = self.A.T
        v1 = AT @ s0; v2 = AT @ v1; v3 = AT @ v2
        return v1, v2, v3, AT @ (self.r * s0), self.R.T @ s0

    def count(self, vec, T):
        v1, v2, v3, u, q = vec
        p3 = v3[T].sum() - u[T].sum() - (v1[T] * self.r[T]).sum() + q[T].sum()
        return [int(round(x)) for x in (v1[T].sum(), v2[T].sum(), p3)]


def col_normalised(Wv):
    """Wn = W / sum_i |W_ij| per postsynaptic column (float64; a column with no input stays 0). Shares W's indices."""
    cs = np.bincount(Wv.indices, weights=np.abs(Wv.data).astype(np.float64), minlength=Wv.shape[1])
    inv = np.divide(1.0, cs, out=np.zeros(Wv.shape[1]), where=cs > 0)
    return sp.csr_matrix((Wv.data.astype(np.float64) * inv[Wv.indices], Wv.indices, Wv.indptr), shape=Wv.shape)


def forward(Wn, S, k, rect=False):
    """[x_0 .. x_k], x_0 = 1 on S, x_j = x_{j-1} @ Wn (clipped at 0 if rect)."""
    x = np.zeros(Wn.shape[0]); x[S] = 1.0
    xs, WT = [x], Wn.T
    for _ in range(k):
        y = WT @ xs[-1]
        xs.append(np.maximum(y, 0.0) if rect else y)
    return xs


def backward(Wn, T, k):
    """[b_0 .. b_k], b_0 = 1/|T| on T, b_j = Wn @ b_{j-1}; w_j = x_0 . b_j = x_i . b_{j-i}."""
    b = np.zeros(Wn.shape[0]); b[T] = 1.0 / len(T)
    bs = [b]
    for _ in range(k):
        bs.append(Wn @ bs[-1])
    return bs


def _top(v, k):
    nz = np.flatnonzero(v)
    if len(nz) > k:
        nz = nz[np.argpartition(-np.abs(v[nz]), k - 1)[:k]]
    return nz[np.argsort(-np.abs(v[nz]))]


def routes(f, b, coo, TYPE, ntypes, Wn, WnC, top, beam):
    """Type-chain decomposition of w_1..w_4. f / b: forward / backward vectors (index = hops); coo = (row, col, value)
    of Wn restricted to rows with f[1] != 0. Returns [(k, chain of type codes, contribution, exact)], the exact sums
    per k (k <= 3) and the part of w_4 carried by the beam's (first, last) type pairs."""
    out, sums = [], {}
    c1 = float(f[0] @ b[1]); sums[1] = c1
    if c1 != 0:
        out.append((1, (), c1, True))
    c = np.bincount(TYPE, weights=f[1] * b[1], minlength=ntypes); sums[2] = float(c.sum())       # S > X > T
    out += [(2, (int(X),), float(c[X]), True) for X in _top(c, top)]
    rr, cc, vv = coo                                                                             # S > X > Y > T
    m = b[1][cc] != 0
    if m.any():
        key = TYPE[rr[m]].astype(np.int64) * ntypes + TYPE[cc[m]]
        uk, inv = np.unique(key, return_inverse=True)
        s = np.bincount(inv, weights=f[1][rr[m]] * vv[m] * b[1][cc[m]])
        sums[3] = float(s.sum())
        out += [(3, (int(uk[i] // ntypes), int(uk[i] % ntypes)), float(s[i]), True) for i in _top(s, top)]
    else:
        sums[3] = 0.0
    cX = np.bincount(TYPE, weights=f[1] * b[3], minlength=ntypes)                               # S > X > Y > Z > T
    cZ = np.bincount(TYPE, weights=f[3] * b[1], minlength=ntypes)
    G = {}
    for Z in _top(cZ, beam):
        cols = np.flatnonzero((TYPE == Z) & (b[1] != 0))
        G[int(Z)] = WnC[:, cols] @ b[1][cols]
    covered = 0.0
    for X in _top(cX, beam):
        rows = np.flatnonzero((TYPE == X) & (f[1] != 0))
        FX = Wn[rows].T @ f[1][rows]
        for Z, GZ in G.items():
            cy = np.bincount(TYPE, weights=FX * GZ, minlength=ntypes)
            covered += float(cy.sum())
            out += [(4, (int(X), int(Y), Z), float(cy[Y]), False) for Y in _top(cy, top)]
    return out, sums, covered


# ---- output helpers ----
def write_csv(df, path):
    tmp, final = _edge.safe_out(path)
    df.to_csv(tmp, index=False)
    return _edge.finish(tmp, final)


def md_table(df):
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)


def rel(x, y):
    m = max(abs(x), abs(y))
    return 0.0 if m < 1e-15 else abs(x - y) / m


def vc(s):
    return {str(k): int(v) for k, v in s.value_counts().items()}


def fw(w):
    return "0" if not w or not np.isfinite(w) else f"{w:+.1e}"


def vdesc(vi, ds):
    """Name a variant (signs = what apply_model_options applied; on MaleCNS known applies nothing)."""
    if vi["eln"] == 0.25 and (vi["signs"] == "known" or ds == "malecns"):
        return "the paper's model"
    if vi["signs"] == "shiu" and vi["eln"] == 0.25:
        return "the published signs, the paper's eLN x0.25"
    if vi["signs"] == "shiu" and vi["eln"] == 1.0:
        return "the published model"
    return f"signs {vi['signs']}, eLN x{vi['eln']:g}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", default="flywire", choices=["flywire", "malecns"])
    ap.add_argument("--conn", default="shiu", help="FlyWire connection table (shiu = the paper's; ignored for malecns)")
    ap.add_argument("--variants", default="known+eln0.25,shiu+eln0.25,shiu", help="comma list: known|shiu [+elnX]")
    ap.add_argument("--max-hops", type=int, default=8)
    ap.add_argument("--routes", type=int, default=3, help="routes kept per (source, target, variant)")
    ap.add_argument("--beam", type=int, default=8, help="first/last types searched for the 4-hop routes")
    ap.add_argument("--limit", type=int, default=0, help="smoke test: only the first N sensory groups")
    ap.add_argument("--out-dir", default=os.path.join(_edge.EDGE_RESULTS, "structure"))
    a = ap.parse_args()
    t_start = time.time()
    ds = a.dataset
    variants = []
    for v in a.variants.split(","):
        v = v.strip(); head, _, tail = v.partition("+")
        if head not in ("known", "shiu") or (tail and not tail.startswith("eln")):
            ap.error(f"bad variant {v!r} (known|shiu [+elnX])")
        variants.append((v, head, float(tail[3:]) if tail else 1.0))

    cx0 = connectome.load(dataset=ds, conn=a.conn, min_syn=1, signs="shiu", eln_scale=1.0, unclear_ln="excitatory")
    print(cx0, flush=True)
    N, nrn, W0 = cx0.n, cx0.neurons, cx0.W
    col = lambda c: nrn[c].fillna("").astype(str) if c in nrn.columns else pd.Series([""] * N)
    lab = col("cell_type")
    lab = lab.where(lab != "", col("hemibrain_type"))
    lab = lab.where(lab != "", "(" + col("super_class") + "/" + col("cell_class") + ")")
    TYPE, TNAMES = pd.factorize(lab.to_numpy())
    TYPE = TYPE.astype(np.int64); NT = len(TNAMES)
    absW0 = np.abs(W0.data).astype(np.float64)
    out_syn0 = np.bincount(np.repeat(np.arange(N), np.diff(W0.indptr)), weights=absW0, minlength=N)
    in_syn0 = np.bincount(W0.indices, weights=absW0, minlength=N)
    rs0 = np.sign(np.asarray(W0.sum(axis=1)).ravel())            # Shiu row sign, as apply_model_options computes it

    IG, OG, SG = input_groups(cx0), output_groups(cx0), state_groups(cx0)
    union = lambda gs: np.unique(np.concatenate([np.asarray(g, np.int64) for g in gs]))
    SENS = {k: union(v) for k, v in IG.items()}
    if a.limit:
        SENS = dict(list(SENS.items())[:a.limit])
    DECS = [k for k in DEC[ds] + REFS if k in OG]
    STATES = {k: SG[k] for k in HUNGER + COMPARE[ds] if k in SG}
    ROLE = {k: ("hunger/fullness" if k in HUNGER else "comparison") for k in STATES}
    if "sugar GRNs" in IG:
        STATES["sugar GRNs"] = union(IG["sugar GRNs"]); ROLE["sugar GRNs"] = "reference"
    STGT = [k for k in STATE_TGT if k in OG]
    SRC = {**{k: np.asarray(v, np.int64) for k, v in STATES.items()}, **SENS}
    PAIRS = {}                                                     # source -> [(part, target)]
    for s in SENS:
        PAIRS.setdefault(s, []).extend(("decider", t) for t in DECS)
    for s in STATES:
        PAIRS.setdefault(s, []).extend(("state", t) for t in STGT)
    TGT = {t: np.asarray(OG[t], np.int64) for t in set(DECS) | set(STGT)}
    print(f"{len(SENS)} sensory groups x {len(DECS)} targets; {len(STATES)} state sources x {len(STGT)} targets; "
          f"{NT} type labels", flush=True)

    # ---- variant-independent structure: hops over all connections, simple-path counts, direct synapses ----
    t0 = time.time()
    A, n_self = binary_nodiag(W0)
    P = Paths(A)
    struct = {}
    for s, S in SRC.items():
        dist = bfs(A, S, a.max_hops); pv = P.source(S)
        sub = W0[S]
        for part, t in PAIRS[s]:
            T = TGT[t]; dT = dist[T]; ok = dT >= 0
            hops = int(dT[ok].min()) if ok.any() else np.nan
            p = P.count(pv, T)
            struct[(s, t)] = dict(
                n_src=len(S), n_tgt=len(T), overlap=int(np.intersect1d(S, T).size), tgt_in_syn=float(in_syn0[T].mean()),
                syn_direct=int(np.abs(sub.data[np.isin(sub.indices, T)]).sum()),
                hops=hops, n_tgt_at_hops=int((dT == hops).sum()) if ok.any() else 0, n_tgt_le3=int((ok & (dT <= 3)).sum()),
                n_paths_1=p[0], n_paths_2=p[1], n_paths_3=p[2], n_paths_le3=sum(p))
    del A, P
    print(f"structure: {len(struct)} pairs, {n_self} self-connections ignored for paths, {time.time()-t0:.0f}s", flush=True)

    # ---- per variant: propagated weight, excitatory hops, routes ----
    rows, route_rows, checks = [], [], {"route_sum_relerr": 0.0, "fwd_bwd_relerr": 0.0}
    vinfo = {}
    for vname, signs, eln in variants:
        t0 = time.time()
        cxv = connectome.apply_model_options(dataclasses.replace(cx0), signs, eln, "excitatory")
        if any(vi["variant"] == cxv.variant for vi in vinfo.values()):   # MaleCNS: known == shiu
            print(f"[{vname}] builds the same model as an earlier variant ({cxv.variant}): skipped", flush=True)
            del cxv
            continue
        Wv = cxv.W
        vinfo[vname] = dict(variant=cxv.variant, signs=cxv.signs, eln=cxv.eln_scale, n_sign_flipped=cxv.n_sign_flipped,
                            n_eln=cxv.n_eln)
        print(f"[{vname}] {cxv}", flush=True)
        rsv = np.sign(np.asarray(Wv.sum(axis=1)).ravel())
        Wn = col_normalised(Wv); WnC = Wn.tocsc()
        Wnp = sp.csr_matrix((np.maximum(Wn.data, 0.0), Wn.indices, Wn.indptr), shape=Wn.shape)
        Ap = sp.csr_matrix(((Wv.data > 0).astype(np.float64), Wv.indices, Wv.indptr), shape=Wv.shape)
        B = {t: backward(Wn, T, K) for t, T in TGT.items()}
        for s, S in SRC.items():
            fl, fr, fe = forward(Wn, S, K), forward(Wn, S, K, rect=True), forward(Wnp, S, K)
            dex = bfs(Ap, S, a.max_hops)
            rf1 = np.flatnonzero(fl[1]); sub = Wn[rf1].tocoo()
            coo = (rf1[sub.row], sub.col.astype(np.int64), sub.data)
            for part, t in PAIRS[s]:
                T = TGT[t]; b = B[t]; dT = dex[T]
                row = dict(dataset=ds, variant=cxv.variant, part=part, source=s, combo=len(IG.get(s, [0])) > 1,
                           target=t, **struct[(s, t)], src_frac_exc=float((rsv[S] > 0).mean()),
                           hops_exc=int(dT[dT >= 0].min()) if (dT >= 0).any() else np.nan)
                w = [float(fl[k][T].mean()) for k in range(1, K + 1)]
                for k in range(1, K + 1):
                    row[f"w_{k}"] = w[k - 1]
                    checks["fwd_bwd_relerr"] = max(checks["fwd_bwd_relerr"], rel(float(fl[0] @ b[k]), w[k - 1]))
                for k in range(1, K + 1):
                    row[f"w_rect_{k}"] = float(fr[k][T].mean())
                for k in range(1, K + 1):
                    row[f"w_exc_{k}"] = float(fe[k][T].mean())
                km = int(np.argmax(np.abs(w)))
                row["w_max"], row["k_max"] = (w[km], km + 1) if w[km] != 0 else (0.0, np.nan)
                rts, sums, covered = routes(fl, b, coo, TYPE, NT, Wn, WnC, a.routes, a.beam)
                for k in (1, 2, 3):
                    checks["route_sum_relerr"] = max(checks["route_sum_relerr"], rel(sums[k], w[k - 1]))
                row["k4_beam_share"] = covered / w[3] if w[3] else np.nan
                name = lambda ch: " > ".join([s] + [str(TNAMES[x]) for x in ch] + [t])
                rts.sort(key=lambda r: -abs(r[2]))
                keep = [("top", i + 1, r) for i, r in enumerate(rts[:a.routes])]
                for k in range(1, K + 1):
                    rk = [r for r in rts if r[0] == k]
                    if rk:
                        keep.append(("best_at_k", 1, rk[0]))
                for i, r in enumerate(rts[:a.routes]):                  # the "top" routes only
                    row[f"route{i+1}"], row[f"route{i+1}_k"], row[f"route{i+1}_w"] = name(r[1]), r[0], r[2]
                for kind, rank, (k, ch, cval, exact) in keep:
                    route_rows.append(dict(dataset=ds, variant=cxv.variant, part=part, source=s, target=t, kind=kind,
                                           rank=rank, k=k, route=name(ch), contribution=cval,
                                           share_of_wk=cval / w[k - 1] if w[k - 1] else np.nan, w_k=w[k - 1], exact=exact))
                rows.append(row)
        print(f"[{vname}] {sum(len(PAIRS[s]) for s in SRC)} pairs, {time.time()-t0:.0f}s", flush=True)
        del Wn, WnC, Wnp, Ap, B, cxv, Wv
    paths = pd.DataFrame(rows)
    rts_df = pd.DataFrame(route_rows)

    # combinations are the union of disjoint single groups, so their linear w_k must be the sum of the singles'
    single_of = {tuple(np.sort(np.asarray(v[0]))): k for k, v in IG.items() if len(v) == 1 and k in SENS}
    err = 0.0
    for k, v in IG.items():
        comps = [single_of.get(tuple(np.sort(np.asarray(g)))) for g in v]
        if len(v) < 2 or k not in SENS or None in comps or sum(len(g) for g in v) != len(SENS[k]):
            continue
        for (vn, t), d in paths[(paths.part == "decider") & paths.source.isin([k] + comps)].groupby(["variant", "target"]):
            d = d.set_index("source")
            for j in range(1, K + 1):
                err = max(err, rel(d.loc[k, f"w_{j}"], d.loc[comps, f"w_{j}"].sum()))
    checks["combo_additivity_relerr"] = err

    # ---- (b) state sources: outgoing synapses and partners (raw synapse counts), wide per-target summary ----
    st_rows = []
    for vn in paths.variant.unique():
        for s in STATES:
            S = SRC[s]; sub = W0[S]
            post = np.unique(sub.indices); pre = np.unique(W0[:, S].tocoo().row)
            ts = np.bincount(TYPE[sub.indices], weights=np.abs(sub.data).astype(np.float64), minlength=NT)
            tops = ", ".join(f"{TNAMES[i]} ({ts[i]:.0f})" for i in _top(ts, 5))
            d = paths[(paths.variant == vn) & (paths.part == "state") & (paths.source == s)].set_index("target")
            r = dict(dataset=ds, variant=vn, source=s, role=ROLE[s], n=len(S), out_syn=float(out_syn0[S].sum()),
                     out_syn_per_neuron=float(out_syn0[S].mean()), n_post=len(post), in_syn=float(in_syn0[S].sum()),
                     n_pre=len(pre), frac_exc=float(d.src_frac_exc.iloc[0]) if len(d) else np.nan, top_post_types=tops)
            for t in STGT:
                if t in d.index:
                    for c in ("syn_direct", "hops", "hops_exc", "n_paths_le3", "w_1", "w_2", "w_3", "w_4", "w_max", "k_max"):
                        r[f"{c}|{t}"] = d.loc[t, c]
            st_rows.append(r)
    state = pd.DataFrame(st_rows)

    # ---- (c) known-sign flips, as apply_model_options computes them ----
    flips, fl_summary = pd.DataFrame(), {}
    rs_known = rs0.copy()
    if "known_nt" in nrn.columns:
        known = nrn.known_nt.map(connectome.parse_known_nt)
        ks = known.map(connectome.KNOWN_SIGN)
        m = ks.notna().to_numpy()
        flip = np.zeros(N, bool)
        flip[m] = (ks[m].to_numpy(dtype=np.float32) != rs0[m]) & (rs0[m] != 0)
        rs_known[flip] *= -1
        chk = connectome.apply_model_options(dataclasses.replace(cx0), "known", 1.0, "excitatory")
        photo = ((col("super_class") == "sensory") & (col("cell_class") == "visual")).to_numpy()
        f = pd.DataFrame({"super_class": col("super_class").to_numpy()[flip], "cell_class": col("cell_class").to_numpy()[flip],
                          "cell_sub_class": col("cell_sub_class").to_numpy()[flip], "cell_type": lab.to_numpy()[flip],
                          "known_nt": known.to_numpy()[flip], "top_nt": col("top_nt").to_numpy()[flip],
                          "direction": np.where(rs0[flip] > 0, "exc->inh", "inh->exc"), "out_syn": out_syn0[flip],
                          "photoreceptor": photo[flip]})
        flips = (f.groupby(["super_class", "cell_class", "known_nt", "top_nt", "direction", "photoreceptor"], dropna=False)
                  .agg(n=("out_syn", "size"), out_syn=("out_syn", "sum")).reset_index().sort_values("n", ascending=False))
        fp = f[f.photoreceptor]
        fl_summary = dict(n_flipped=int(flip.sum()), n_flipped_apply_model_options=int(chk.n_sign_flipped),
                          n_known=int(m.sum()), n_photoreceptor=int(len(fp)), n_photoreceptor_total=int(photo.sum()),
                          n_photoreceptor_pred_exc=int((photo & (rs0 > 0)).sum()),
                          n_photoreceptor_no_output=int((photo & (rs0 == 0)).sum()),
                          n_histamine_flipped_not_photoreceptor=int(((f.known_nt == "histamine") & ~f.photoreceptor).sum()),
                          photoreceptor_types=vc(fp.cell_type), photoreceptor_sub_class=vc(fp.cell_sub_class.replace("", "(none)")),
                          by_direction=vc(f.direction), by_known_nt=vc(f.known_nt), by_super_class=vc(f.super_class),
                          out_syn_flipped=float(f.out_syn.sum()), out_syn_all=float(out_syn0.sum()),
                          out_syn_photoreceptor=float(fp.out_syn.sum()),
                          n_alln=int((f.cell_class == "ALLN").sum()),
                          n_central_complex=int((f.cell_class == "CX").sum()))
        del chk

    # ---- (d) antennal-lobe local neurons: transmitter and sign under both rules ----
    ln = cx0.select(cell_class="^ALLN$")
    alpn = cx0.select(cell_class="^ALPN$")
    sub = W0[ln].tocoo()
    to_pn = np.bincount(sub.row, weights=np.abs(sub.data) * np.isin(sub.col, alpn), minlength=len(ln))
    kn = nrn.known_nt.map(connectome.parse_known_nt).to_numpy()[ln] if "known_nt" in nrn.columns else np.full(len(ln), None)
    sgn = lambda x: np.where(x > 0, "+", np.where(x < 0, "-", "0"))
    L = pd.DataFrame({"top_nt": col("top_nt").to_numpy()[ln], "known_nt": pd.Series(kn).fillna("").to_numpy(),
                      "sign_shiu": sgn(rs0[ln]), "sign_known": sgn(rs_known[ln]), "out_syn": out_syn0[ln], "out_syn_to_alpn": to_pn})
    aln = (L.groupby(["top_nt", "known_nt", "sign_shiu", "sign_known"], dropna=False)
            .agg(n=("out_syn", "size"), out_syn=("out_syn", "sum"), out_syn_to_alpn=("out_syn_to_alpn", "sum")).reset_index())
    aln["eln_scaled_under_shiu"] = aln.sign_shiu == "+"
    aln["eln_scaled_under_known"] = aln.sign_known == "+"
    eln_counts = {"n_alln": int(len(ln)), "eln_shiu": int((rs0[ln] > 0).sum()), "eln_known": int((rs_known[ln] > 0).sum()),
                  "eln_shiu_by_top_nt": vc(L[L.sign_shiu == "+"].top_nt), "eln_known_by_top_nt": vc(L[L.sign_known == "+"].top_nt)}
    for vn, vi in vinfo.items():                                   # the eLN set apply_model_options scaled
        if vi["eln"] != 1.0:
            eln_counts[f"n_eln_apply_model_options[{vn}]"] = vi["n_eln"]

    # ---- write ----
    od = a.out_dir
    files = [write_csv(paths, os.path.join(od, f"structure_paths_{ds}.csv")),
             write_csv(rts_df, os.path.join(od, f"structure_routes_{ds}.csv")),
             write_csv(state, os.path.join(od, f"structure_state_{ds}.csv")),
             write_csv(aln, os.path.join(od, f"structure_aln_{ds}.csv"))]
    if len(flips):
        files.append(write_csv(flips, os.path.join(od, f"structure_signflips_{ds}.csv")))

    # ---- markdown summary ----
    V = list(paths.variant.unique())
    L_ = [f"# Structure probe: {ds} (no simulation)", "",
          f"{time.strftime('%Y-%m-%d %H:%M')}. `{' '.join(sys.argv)}`. Raw load: {cx0}. Variants: "
          + ", ".join(f"`{vi['variant']}` ({vdesc(vi, ds)})" for vi in vinfo.values()) + f". {time.time()-t_start:.0f} s.", "",
          "Definitions (module docstring): hops over all connections; paths = simple neuron-level paths of length <= 3; "
          "w_k = mean over the target neurons of x_k = x_{k-1} @ Wn from x_0 = 1 on the sources, Wn = W / column sum of |W| "
          "(w_1 = signed fraction of the targets' input synapses coming from the sources). `w_max` = the w_k (k = 1..4) with "
          "the largest |w_k|, shown as `value kK`.", "", "## Checks", ""]
    if fl_summary:
        L_.append(f"- known-sign flips: {fl_summary['n_flipped']:,} recomputed here; apply_model_options "
                  f"{fl_summary['n_flipped_apply_model_options']:,}; connectome.py docstring and paper: 11,010.")
    L_.append(f"- eLN (ALLN with a positive row sign): {eln_counts['eln_shiu']} under the Shiu signs, {eln_counts['eln_known']} "
              "under the known signs; " + ", ".join(f"{k.split('[')[1][:-1]}: {v}" for k, v in eln_counts.items()
                                                      if k.startswith("n_eln_apply")) + " (connectome.py docstring: 150).")
    L_.append(f"- routes: the exact chains of k = 1..3 add up to w_k (max relative error {checks['route_sum_relerr']:.1e}); "
              f"forward and backward w_k agree (max relative error {checks['fwd_bwd_relerr']:.1e}); every combination's "
              f"w_k is the sum of its single groups' (max relative error {checks['combo_additivity_relerr']:.1e}).")
    L_ += ["", "## (a) Sensory input -> deciders", "",
           "### Hops / simple paths within 3 hops (all connections; the same in every variant)", ""]
    dec = paths[paths.part == "decider"]
    tcols = [t for t in DECS]
    tab = lambda d, f_: pd.DataFrame([{"source": s, **{SHORT.get(t, t): f_(d[(d.source == s) & (d.target == t)].iloc[0])
                                                       for t in tcols}} for s in SENS])
    d0 = dec[dec.variant == V[0]]
    L_.append(md_table(tab(d0, lambda r: f"{'-' if pd.isna(r.hops) else int(r.hops)} / {r.n_paths_le3:,}")))
    for vn in V:
        dv = dec[dec.variant == vn]
        L_ += ["", f"### `{vn}`: strongest signed propagated weight w_max (and its k)", ""]
        L_.append(md_table(tab(dv, lambda r: f"{fw(r.w_max)} k{int(r.k_max)}" if r.w_max else "0")))
        L_ += ["", f"### `{vn}`: excitatory-only hops / w_exc_3 (upper bound of what can excite)", ""]
        L_.append(md_table(tab(dv, lambda r: f"{'-' if pd.isna(r.hops_exc) else int(r.hops_exc)} / {fw(r.w_exc_3)}")))
        refs, refx = [], []
        L_.append("")
        for s, t in REF_PAIRS:
            r = dv[(dv.source == s) & (dv.target == t)]
            if len(r):
                r = r.iloc[0]; refs.append(abs(r.w_max)); refx.append(r.w_exc_3)
                L_.append(f"- reference {s} -> {t}: hops {r.hops}, {r.n_paths_le3:,} paths, w_max {fw(r.w_max)} (k{r.k_max:.0f}), "
                          f"w_exc_3 {fw(r.w_exc_3)}; top route `{r.get('route1', '')}` ({fw(r.get('route1_w', 0))})")
        dd = dv[dv.target.isin(DEC[ds]) & ~dv.combo]                   # single groups: a combination is their sum
        if len(dd):
            rel_ = lambda x, ref: f" = {abs(x) / min(ref):.2f}x the weaker reference's" if ref and min(ref) else ""
            for what, i in (("|w_max|", dd.w_max.abs().idxmax()), ("positive w_max", dd.w_max.idxmax()),
                            ("w_exc_3", dd.w_exc_3.idxmax())):
                b_ = dd.loc[i]; v_ = b_.w_exc_3 if what == "w_exc_3" else b_.w_max
                L_.append(f"- largest decider {what} (single sensory groups): {b_.source} -> {b_.target}, {fw(v_)}"
                          + (f" (k{b_.k_max:.0f})" if what != "w_exc_3" else "") + rel_(v_, refx if what == "w_exc_3" else refs) + ".")
            L_.append(f"- {int((dd.w_max < 0).sum())} of {len(dd)} single-group sensory-decider pairs have a negative w_max (net inhibitory).")
            L_ += ["", f"Strongest single sensory group per decider under `{vn}` (top route; share of that w_k):", ""]
            for t in DEC[ds]:
                x = dd[dd.target == t]
                if len(x):
                    r = x.loc[x.w_max.abs().idxmax()]
                    rr = rts_df[(rts_df.variant == vn) & (rts_df.source == r.source) & (rts_df.target == t) & (rts_df.kind == "top")]
                    rt = rr.iloc[0] if len(rr) else None
                    L_.append(f"- {t}: {r.source}, w_max {fw(r.w_max)} (k{r.k_max:.0f}), hops {r.hops}"
                              + (f"; `{rt.route}` {fw(rt.contribution)} (k{rt.k}, {rt.share_of_wk:.0%} of w_{rt.k})" if rt is not None else ""))
    L_ += ["", "## (b) Hunger / fullness neurons against SAG and pC1 (synapse counts from the raw table)", ""]
    for vn in V:
        sv = state[state.variant == vn]
        if not len(sv):
            continue
        L_ += [f"### `{vn}`: cells = hops / paths <= 3 / w_max", ""]
        tb = []
        for r in sv.to_dict("records"):
            x = {"source": r["source"], "role": r["role"], "n": r["n"], "out syn": f"{r['out_syn']:,.0f}",
                 "per neuron": f"{r['out_syn_per_neuron']:,.0f}", "partners": r["n_post"], "exc": f"{r['frac_exc']:.2f}"}
            for t in STGT:
                h = r.get(f"hops|{t}")
                x[SHORT.get(t, t).replace(" (ref)", "")] = (f"{'-' if h is None or pd.isna(h) else int(h)} / {int(r.get(f'n_paths_le3|{t}', 0)):,} / "
                                      f"{fw(r.get(f'w_max|{t}', 0))}")
            tb.append(x)
        L_ += [md_table(pd.DataFrame(tb)), ""]
    sv = state[state.variant == V[0]]
    L_ += ["Top postsynaptic types (synapses):", ""] + [f"- {r.source}: {r.top_post_types}" for r in sv.itertuples()]
    L_ += ["", "Neuroendocrine cells (IPC, DH44, ...) act mostly by hormone release, which W does not contain; the rows above "
           "are their synaptic outputs only."]
    if fl_summary:
        fs = fl_summary
        L_ += ["", "## (c) Neurons whose sign signs=known flips", "",
               f"- {fs['n_flipped']:,} of {fs['n_known']:,} neurons with a known transmitter; "
               f"{fs['by_direction']} ; {fs['out_syn_flipped']/fs['out_syn_all']:.1%} of all output synapses.",
               f"- photoreceptors (super_class sensory, cell_class visual): {fs['n_photoreceptor']:,} "
               f"({fs['n_photoreceptor']/max(fs['n_flipped'], 1):.1%} of the flips; of {fs['n_photoreceptor_total']:,} photoreceptors); "
               f"types {fs['photoreceptor_types']}; sub-classes {fs['photoreceptor_sub_class']}. Of all photoreceptors "
               f"{fs['n_photoreceptor_pred_exc']:,} are predicted excitatory and {fs['n_photoreceptor_no_output']:,} have no "
               f"output synapse (sign 0, never flipped); {fs['n_histamine_flipped_not_photoreceptor']} histaminergic flips are "
               "not photoreceptors. (connectome.py docstring: 9,200 photoreceptors.)",
               f"- known transmitter of the flipped neurons: {fs['by_known_nt']}.",
               f"- antennal-lobe local neurons flipped: {fs['n_alln']}; central complex (cell_class CX): {fs['n_central_complex']}.",
               "", "By super_class:", ""]
        g = flips.groupby("super_class").agg(n=("n", "sum"), out_syn=("out_syn", "sum")).sort_values("n", ascending=False).reset_index()
        L_.append(md_table(g.assign(out_syn=g.out_syn.map(lambda x: f"{x:,.0f}"))))
        L_ += ["", "Top 15 cell_class (all super_classes):", ""]
        g = (flips.groupby(["super_class", "cell_class", "direction"]).agg(n=("n", "sum"), out_syn=("out_syn", "sum"))
             .sort_values("n", ascending=False).head(15).reset_index())
        L_.append(md_table(g.assign(out_syn=g.out_syn.map(lambda x: f"{x:,.0f}"))))
    elif ds != "flywire" or "known_nt" not in nrn.columns:
        L_ += ["", "## (c) Known-sign flips", "", "No `known_nt` column in this dataset: signs=known applies nothing."]
    L_ += ["", "## (d) Antennal-lobe local neurons (cell_class ALLN) by predicted transmitter and sign", "",
           f"{eln_counts['n_alln']} ALLN. eLN (positive row sign, what an eLN scale multiplies): {eln_counts['eln_shiu']} under the "
           f"Shiu signs, by top_nt {eln_counts['eln_shiu_by_top_nt']}; {eln_counts['eln_known']} under the known signs, by top_nt "
           f"{eln_counts['eln_known_by_top_nt']}.", ""]
    g = (aln.groupby(["top_nt", "sign_shiu", "sign_known"]).agg(n=("n", "sum"), out_syn=("out_syn", "sum"),
                                                                out_syn_to_alpn=("out_syn_to_alpn", "sum")).reset_index())
    L_.append(md_table(g.assign(out_syn=g.out_syn.map(lambda x: f"{x:,.0f}"), out_syn_to_alpn=g.out_syn_to_alpn.map(lambda x: f"{x:,.0f}"))))
    L_ += ["", "Files: " + ", ".join(f"`{os.path.basename(p)}`" for p in files), ""]
    md = os.path.join(od, f"structure_{ds}.md")
    tmp, final = _edge.safe_out(md)
    with open(tmp, "w") as fh:
        fh.write("\n".join(L_))
    files.append(_edge.finish(tmp, final))
    _edge.sidecar(md, {"variants": vinfo, "checks": checks, "signflips": fl_summary, "eln": eln_counts,
                       "n_self_connections": n_self, "files": [os.path.relpath(p, _edge.ROOT) for p in files],
                       "wall_s": round(time.time() - t_start, 1)})
    print("checks:", {k: f"{v:.1e}" for k, v in checks.items()})
    if fl_summary:
        print(f"sign flips: {fl_summary['n_flipped']} (apply_model_options {fl_summary['n_flipped_apply_model_options']}), "
              f"photoreceptors {fl_summary['n_photoreceptor']}, ALLN {fl_summary['n_alln']}")
    print(f"eLN: shiu {eln_counts['eln_shiu']}, known {eln_counts['eln_known']}; "
          + ", ".join(f"{k}={v}" for k, v in eln_counts.items() if k.startswith("n_eln")))
    print("wrote", *[os.path.relpath(p, _edge.ROOT) for p in files], f"({time.time()-t_start:.0f}s)", sep="\n  ")


if __name__ == "__main__":
    main()
