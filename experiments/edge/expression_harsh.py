#!/usr/bin/env python3
"""Harsh tests of "the memory cannot be expressed" (edge-case suite, design_plan 2.4; RESEARCH_NOTES 16f, 18g, 23).

MBON sets and targets exactly as experiments/expression_probe.py: the reward (REWARD_MBONS) and punishment
(PUNISH_MBONS) compartment MBONs; targets = every neuron receiving >= --min-syn synapses from the set, KCs and MBONs
excluded; the set's descending targets are read out separately. Odor: vinegar at 150 Hz (SensoryEncoder), presented
none / on the left antenna (approach index = DNa L - R) / on both. Modes (--modes, comma-separated):
  drive      the set's MBONs themselves driven at --mbon-hz (0 = intact, no drive) x odor: do the MBONs reach a DN?
  types      one MBON type alone (--types; MBON14, MBON11, MBON01, MBON07) at --type-hz x odor; targets and DN
             targets are the type's own (same rule), `set` names the parent set
  bypass     lateral-horn bypass: every ALPN synapse onto anything but KCs, AL neurons (cell_class ^AL) and ORNs is
             cut (LIF.cut_edges), so odor reaches the DNs only through the mushroom body; MBONs intact, silenced
             (scale_output 0) or driven at --bypass-hz. Unbypassed intact rows are the KC-code reference (KC active %);
             the synapses still leaving the AL by other routes (ORNs, ALLN/ALIN/ALON) are printed and in the sidecar
  kick-nodn  tonic Poisson kicks (--tonic) on the set's targets MINUS its descending neurons, MBONs intact or
             silenced (expression_probe kicked the 28 DN targets too, so their "within 0.6 Hz" was by construction)
  structure  no simulation: DNs first reached 1..--hops hops from each set and type. Layer h = every non-KC, non-MBON
             neuron outside earlier layers with >= --min-syn synapses summed from layer h-1 (hop 1 = the targets);
             per DN the synapses from the previous layer, E/I, their share of its input, the top presynaptic types;
             signed_frac = (E-I)/(E+I) of those synapses, signed_of_input = (E-I)/(all input to the DN(s)), both
             for 'layer' and 'dn' rows
  sub (P2)   a subthreshold tonic state instead of kicks: --n-src extra source neurons with +1 synapse onto every
             non-DN target (W_aug = [[W, 0], [S, 0]]; LIF(W_aug, LIFParams(w_syn=0.275*scale))), sources driven at
             --sub-rates; a (set, rate) is calibrated (sub_calibrated) if its non-DN targets fire 1-10 Hz with no
             odor and the MBONs silenced
Weights are restored between conditions; every sim is seed s = 0..--seeds-1, reset, set_drive, run(--ms), as
run_trials. Self-check: rows identical by construction (drive at 0 Hz, kick-nodn at 0 Hz intact, bypass off intact)
must agree to the digit. --check-against the expression_probe file compares every row that is the same simulation
as one of its rows -- those 0-Hz rows, kick-nodn 0 Hz silenced, and kick-nodn at any --tonic for a set with no DN
target (reward: targets minus DNs = all its targets) -- cell by cell (1e-9; needs its --ms 1000 and seeds 0..2) and
writes <main>.check.txt (exit 0 either way).
  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/edge/expression_harsh.py --dataset flywire --out-dir DIR \\
      [--modes drive,types,bypass,kick-nodn,structure] [--seeds 3] [--ms 1000] [--tag T] \\
      [--check-against experiments/results/expression_probe_flywire_shiu_min1+known+eln0.25.csv]
  ... --modes sub --sub-rates 50,100,150 --n-src 50 --seeds 3
Writes DIR/expression_harsh_<dataset>_<variant>[_T].csv (one row per sim), ..._dn_types.csv (long: sim_id x DN type
x Hz; types silent in every sim dropped), ..._structure.csv (rows 'layer' and 'dn'), a JSON sidecar next to the first.
"""
import argparse, gc, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge  # puts experiments/ and brain/ on the path
import numpy as np, pandas as pd, scipy.sparse as sp
from common import connectome, output_groups, make_sim
from flybrain.lif import LIF, LIFParams
from flybrain.plasticity import REWARD_MBONS, PUNISH_MBONS
from flybrain.senses import SensoryEncoder

MODES = ["drive", "types", "bypass", "kick-nodn", "structure", "sub"]


def csv_list(f):
    return lambda s: [f(x) for x in s.split(",") if x.strip()]


ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True, choices=["flywire", "malecns"])
ap.add_argument("--out-dir", required=True)
ap.add_argument("--tag", default="", help="suffix of the output names (several runs into one --out-dir)")
ap.add_argument("--modes", type=csv_list(str), default=["drive", "types", "bypass", "kick-nodn", "structure"])
ap.add_argument("--odor", default="vinegar"); ap.add_argument("--hz", type=float, default=150, help="odor r_max")
ap.add_argument("--presentations", type=csv_list(str), default=["none", "L", "both"])
ap.add_argument("--min-syn", type=int, default=10, help="a target receives at least this many synapses from the set")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--mbon-hz", type=csv_list(float), default=[0, 20, 50, 100], help="drive: MBON set rates (0 = intact)")
ap.add_argument("--types", type=csv_list(str), default=["MBON14", "MBON11", "MBON01", "MBON07"])
ap.add_argument("--type-hz", type=float, default=50)
ap.add_argument("--bypass-hz", type=csv_list(float), default=[50, 100], help="bypass: MBON drive rates")
ap.add_argument("--tonic", type=csv_list(float), default=[0, 10, 40], help="kick-nodn: Hz on the non-DN targets")
ap.add_argument("--hops", type=int, default=3)
ap.add_argument("--sub-rates", type=csv_list(float), default=[50, 100, 150])
ap.add_argument("--n-src", type=int, default=50)
ap.add_argument("--sub-band", type=csv_list(float), default=[1, 10], help="calibrated non-DN target rate, Hz")
ap.add_argument("--check-against", default=None, help="expression_probe CSV: compare every row that is the same simulation as one of its rows, to the digit")
a = ap.parse_args()
bad = [m for m in a.modes if m not in MODES]
if bad:
    ap.error(f"unknown modes {bad}; choose from {MODES}")
if not set(a.presentations) <= {"none", "L", "both"}:
    ap.error("--presentations: none, L, both")
if a.check_against and not os.path.isfile(a.check_against):              # fail now, not after the whole run
    ap.error(f"--check-against: no such file {a.check_against}")
_edge.safe_out(os.path.join(a.out_dir, "expression_harsh_probe.csv"))   # fail fast on a forbidden --out-dir (and create it)
sims = [m for m in a.modes if m not in ("structure", "sub")]

cx = connectome.load(dataset=a.dataset); print(cx, flush=True)
N = cx.n
OG = output_groups(cx)
OUT = {k: OG[k] for k in ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DN all", "feed MNs", "MN9", "DNp13 reject", "MBON", "KC", "PPL1 (punish DA)", "PAM (reward DA)"] if k in OG}
nb = cx.neurons
types = nb.hemibrain_type.fillna(nb.cell_type).fillna("").astype(str).to_numpy()            # as expression_probe
ctype = nb.cell_type.fillna(nb.hemibrain_type).fillna(nb.super_class).fillna("?").astype(str).to_numpy()  # DN / presyn labels
mbon = cx.select(cell_class="^MBON$"); kc = cx.select(cell_class="^Kenyon_Cell$")
dn_idx = cx.select(super_class="^descending$")
isdn = np.zeros(N, bool); isdn[dn_idx] = True
Wabs = abs(cx.W)


def targets(m):
    """expression_probe's rule, verbatim: >= min_syn synapses from the set, MBONs and KCs excluded."""
    syn = np.asarray(Wabs[m].sum(axis=0)).ravel()
    tg = np.flatnonzero(syn >= a.min_syn)
    return tg[~np.isin(tg, mbon) & ~np.isin(tg, kc)], syn


sets, info = {}, {}
for name, tset in (("reward", REWARD_MBONS), ("punish", PUNISH_MBONS)):
    sets[name] = {"m": mbon[np.isin(types[mbon], list(tset))], "parent": name, "type": ""}
for T in a.types:
    m = mbon[types[mbon] == T]
    if not len(m):
        print(f"[types] {T}: no neuron of this type, skipped", flush=True); continue
    sets[T] = {"m": m, "parent": "reward" if T in REWARD_MBONS else "punish" if T in PUNISH_MBONS else "-", "type": T}
for name, S in sets.items():
    tg, syn = targets(S["m"])
    S.update(tg=tg, tgd=tg[isdn[tg]], tgn=tg[~isdn[tg]])
    sign = np.sign(np.asarray(cx.W[S["m"]].sum(axis=1)).ravel())
    sub = nb.iloc[tg]
    info[name] = {"n_mbons": int(len(S["m"])), "mbon_types": sorted(set(types[S["m"]])), "n_inhibitory": int((sign < 0).sum()),
                  "n_excitatory": int((sign > 0).sum()), "n_targets": int(len(tg)), "target_synapses": int(syn[tg].sum()),
                  "n_target_dns": int(len(S["tgd"])), "target_dn_types": sorted(set(ctype[S["tgd"]]))}
    print(f"[{name}] {len(S['m'])} MBONs ({', '.join(sorted(set(types[S['m']])))}; {int((sign < 0).sum())} inhibitory, {int((sign > 0).sum())} excitatory) -> "
          f"{len(tg)} targets with >= {a.min_syn} synapses ({int(syn[tg].sum())} synapses), {len(S['tgd'])} DNs, {len(S['tgn'])} non-DN; "
          f"super_class {sub.super_class.value_counts().head(5).to_dict()}", flush=True)

tag = f"_{a.tag}" if a.tag else ""
base = os.path.join(a.out_dir, f"expression_harsh_{a.dataset}_{cx.variant}{tag}")
written, extra = [], {"sets": info, "args": vars(a)}


def write_csv(df, path):
    tmp, final = _edge.safe_out(path); df.to_csv(tmp, index=False); _edge.finish(tmp, final)
    written.append(final); print("wrote", final, flush=True)


# ---- structure (no simulation) ----------------------------------------------------------------------------------
if "structure" in a.modes:
    in_tot = np.asarray(Wabs.sum(axis=0)).ravel()
    excl = np.zeros(N, bool); excl[mbon] = True; excl[kc] = True
    srows = []
    for name, S in sets.items():
        seen = excl.copy(); seen[S["m"]] = True
        prev = S["m"]
        for h in range(1, a.hops + 1):
            syn = np.asarray(Wabs[prev].sum(axis=0)).ravel()
            nxt = np.flatnonzero((syn >= a.min_syn) & ~seen); seen[nxt] = True
            if h == 1:
                assert np.array_equal(nxt, S["tg"]), "hop 1 must be expression_probe's targets"
            dns = nxt[isdn[nxt]]
            Wp = cx.W[prev][:, dns].tocsc()
            pos, neg = Wp.copy(), Wp.copy()
            pos.data = np.clip(pos.data, 0, None); neg.data = -np.clip(neg.data, None, 0)
            exc = np.asarray(pos.sum(axis=0)).ravel(); inh = np.asarray(neg.sum(axis=0)).ravel()
            tot = exc.sum() + inh.sum()
            dtc = pd.Series(exc + inh, index=ctype[dns]).groupby(level=0).sum().sort_values(ascending=False) if len(dns) else pd.Series(dtype=float)
            L = {"row": "layer", "set": name, "parent": S["parent"], "hop": h, "root_id": 0, "dn_type": "", "side": "",   # root_id 0: keeps the column int64
                 "n_layer": int(len(nxt)), "n_dn": int(len(dns)),
                 "n_dn_types": int(dtc.size), "syn_from_prev": float(tot), "exc": float(exc.sum()), "inh": float(inh.sum()),
                 "signed_frac": float((exc.sum() - inh.sum()) / tot) if tot else np.nan,
                 "signed_of_input": float((exc.sum() - inh.sum()) / in_tot[dns].sum()) if len(dns) else np.nan,
                 "frac_of_input": float(tot / in_tot[dns].sum()) if len(dns) else np.nan,
                 "top": "|".join(f"{k}:{v:.0f}" for k, v in dtc.head(8).items())}
            srows.append(L)
            for j, d in enumerate(dns):
                lo, hi = Wp.indptr[j], Wp.indptr[j + 1]
                pre = pd.Series(np.abs(Wp.data[lo:hi]), index=ctype[prev[Wp.indices[lo:hi]]]).groupby(level=0).sum().nlargest(3)
                s_ = exc[j] + inh[j]
                srows.append({"row": "dn", "set": name, "parent": S["parent"], "hop": h, "root_id": int(cx.root_ids[d]), "dn_type": ctype[d],
                              "side": nb.side.iloc[d], "syn_from_prev": float(s_), "exc": float(exc[j]), "inh": float(inh[j]),
                              "signed_frac": float((exc[j] - inh[j]) / s_) if s_ else np.nan,
                              "signed_of_input": float((exc[j] - inh[j]) / in_tot[d]) if in_tot[d] else np.nan,
                              "frac_of_input": float(s_ / in_tot[d]) if in_tot[d] else np.nan,
                              "top": "|".join(f"{k}:{v:.0f}" for k, v in pre.items())})
            print(f"[structure] {name:7s} hop {h}: {len(nxt):6d} neurons, {len(dns):4d} DNs ({L['n_dn_types']} types; {tot:.0f} synapses from hop {h-1}, "
                  f"E-I/E+I {L['signed_frac']:+.2f}, {L['frac_of_input']*100 if len(dns) else 0:.1f}% of their input) top {L['top'][:110]}", flush=True)
            prev = nxt
            if not len(prev):
                break
    write_csv(pd.DataFrame(srows), base + "_structure.csv")

# ---- bypass diagnostic: what still leaves the AL once the ALPN -> non-(KC|AL|ORN) synapses are cut ------------------
if "bypass" in a.modes:
    pn = np.zeros(N, bool); pn[cx.select(cell_class="^ALPN$")] = True
    keep = np.zeros(N, bool)
    for g in (kc, cx.select(cell_class="^AL"), cx.select(cell_class="^olfactory$")):
        keep[g] = True
    if not pn.any():
        sys.exit("bypass: no ALPN in this dataset")
    out_of = lambda pre: float(Wabs[pre].dot((~keep).astype(np.float32)).sum()) if len(pre) else 0.0   # |W| onto non-kept neurons
    leak = {cls: round(out_of(cx.select(cell_class=f"^{cls}$")), 1) for cls in ("olfactory", "ALLN", "ALIN", "ALON")}
    pn_out = round(out_of(np.flatnonzero(pn)), 1)
    extra["bypass"] = {"alpn": int(pn.sum()), "alpn_synapses_cut": pn_out, "remaining_al_exit_synapses": leak}
    print(f"[bypass] {int(pn.sum())} ALPNs; |W| {pn_out:.0f} onto non-(KC|AL|ORN) will be cut; other AL exits left intact, |W| (eLNs x scale): {leak}", flush=True)

del Wabs; gc.collect()

# ---- simulations ------------------------------------------------------------------------------------------------
rows, dnr = [], []
dn_codes, dn_names = pd.factorize(ctype[dn_idx])
dn_n = np.bincount(dn_codes, minlength=len(dn_names)).astype(float)
sec = a.ms / 1000
if sims or "sub" in a.modes:
    senses = SensoryEncoder(cx, verbose=False)
    ODOR = {p: (np.zeros(0, np.int64), np.zeros(0, np.float32)) if p == "none" else senses.odor(a.odor, side=None if p == "both" else "L", r_max=a.hz)
            for p in a.presentations}
t0 = time.time()


def drive(pres, *extra_groups):
    """odor presentation + (idx, hz) groups; a group at 0 Hz adds nothing (identical to expression_probe at T = 0)."""
    oi, orate = ODOR[pres]
    idx, rate = [oi], [orate]
    for g, hz in extra_groups:
        if hz > 0 and len(g):
            idx.append(np.asarray(g, np.int64)); rate.append(np.full(len(g), hz, np.float32))
    return np.concatenate(idx), np.concatenate(rate)


def run_cond(sim, S, cond, idx, rate):
    for seed in range(a.seeds):
        sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
        tw = time.perf_counter(); counts, _ = sim.run(a.ms); wall = time.perf_counter() - tw
        counts = counts[:N]                                     # sub: drop the source neurons
        hz = lambda v: float(counts[v].sum() / len(v) / sec) if len(v) else float("nan")
        r = {"sim_id": len(rows), "mode": "", "set": S["parent"], "type": S["type"], "bypass": False, "mbons": "intact", "mbon_hz": 0.0,
             "tonic_hz": 0.0, "sub_rate": 0.0, "n_src": 0}
        r.update(cond)
        r.update({"seed": seed, "n_driven": int(len(idx)), "n_targets": int(len(S["tg"])), "n_target_dns": int(len(S["tgd"])), "wall_s": round(wall, 2),
                  "active_frac": float((counts > 0).mean()), "total_spikes": int(counts.sum()),
                  "set MBONs Hz": hz(S["m"]), "targets Hz": hz(S["tg"]), "non-DN targets Hz": hz(S["tgn"]), "target DNs Hz": hz(S["tgd"]),
                  "KC active %": float((counts[kc] > 0).mean() * 100)})
        for k, v in OUT.items():
            r[k] = hz(v)
        r["approach (L-R)"] = r["DNa L"] - r["DNa R"]
        rows.append(r)
        dnr.append(np.bincount(dn_codes, weights=counts[dn_idx], minlength=len(dn_names)) / dn_n / sec)
    d = pd.DataFrame(rows[-a.seeds:])
    lab = S["type"] or S["parent"]
    print(f"[{cond['mode']:9s} {lab:6s}] byp {int(cond.get('bypass', False))} MBONs {cond.get('mbons', 'intact'):8s} {cond.get('mbon_hz', 0):4.0f} Hz "
          f"tonic {cond.get('tonic_hz', 0):3.0f} sub {cond.get('sub_rate', 0):3.0f} odor {cond['odor']:4s} | set MBONs {d['set MBONs Hz'].mean():5.1f} "
          f"nonDN tg {d['non-DN targets Hz'].mean():5.1f} tgDN {d['target DNs Hz'].mean():5.1f} | DNa L/R {d['DNa L'].mean():5.1f}/{d['DNa R'].mean():5.1f} "
          f"DNp09 {d['DNp09'].mean():4.1f} MDN {d['MDN back'].mean():4.1f} GF {d['GF jump'].mean():4.1f} DNp13 {d['DNp13 reject'].mean():4.1f} "
          f"DN all {d['DN all'].mean():4.1f} | KC {d['KC active %'].mean():4.1f}% brain {d.active_frac.mean()*100:4.1f}% ({time.time()-t0:.0f}s)", flush=True)


sim = make_sim(cx) if sims else None
main_sets = ("reward", "punish")
if "drive" in a.modes:
    for sname in main_sets:
        S = sets[sname]
        for hz in a.mbon_hz:
            sim.restore_weights()
            for pres in a.presentations:
                run_cond(sim, S, {"mode": "drive", "mbons": "driven" if hz > 0 else "intact", "mbon_hz": hz, "odor": pres}, *drive(pres, (S["m"], hz)))
    sim.restore_weights()
if "types" in a.modes:
    for T in a.types:
        if T not in sets:
            continue
        S = sets[T]
        sim.restore_weights()
        for pres in a.presentations:
            run_cond(sim, S, {"mode": "types", "mbons": "driven", "mbon_hz": a.type_hz, "odor": pres}, *drive(pres, (S["m"], a.type_hz)))
    sim.restore_weights()
if "bypass" in a.modes:
    states = [(False, "intact", 0.0), (True, "intact", 0.0), (True, "silenced", 0.0)] + [(True, "driven", h) for h in a.bypass_hz]
    for sname in main_sets:
        S = sets[sname]
        for byp, state, hz in states:
            sim.restore_weights()
            if byp:
                ncut = sim.cut_edges(pn, ~keep)
                extra["bypass"]["connections_cut"] = ncut
            if state == "silenced":
                sim.scale_output(S["m"], 0.0)
            for pres in a.presentations:
                run_cond(sim, S, {"mode": "bypass", "bypass": byp, "mbons": state, "mbon_hz": hz, "odor": pres}, *drive(pres, (S["m"], hz)))
    sim.restore_weights()
    print(f"[bypass] {extra['bypass'].get('connections_cut', 0)} ALPN connections cut per bypassed condition", flush=True)
if "kick-nodn" in a.modes:
    for sname in main_sets:
        S = sets[sname]
        for T in a.tonic:
            for state in ("intact", "silenced"):
                sim.restore_weights()
                if state == "silenced":
                    sim.scale_output(S["m"], 0.0)
                for pres in a.presentations:
                    run_cond(sim, S, {"mode": "kick-nodn", "mbons": state, "tonic_hz": T, "odor": pres}, *drive(pres, (S["tgn"], T)))
    sim.restore_weights()
del sim; gc.collect()

if "sub" in a.modes:
    Wc = cx.W.tocsr()
    for sname in main_sets:
        S = sets[sname]
        tgn, ns = np.sort(S["tgn"]), a.n_src
        # W_aug = [[W, 0], [S, 0]]: same rows for the brain (zero columns appended), n_src new rows with +1 on each non-DN target
        indptr = np.concatenate([Wc.indptr.astype(np.int64), Wc.indptr[-1] + np.arange(1, ns + 1, dtype=np.int64) * len(tgn)])
        Waug = sp.csr_matrix((np.concatenate([Wc.data.astype(np.float32), np.ones(ns * len(tgn), np.float32)]),
                              np.concatenate([Wc.indices.astype(np.int64), np.tile(tgn, ns)]), indptr), shape=(N + ns, N + ns))
        ssim = LIF(Waug, LIFParams(w_syn=0.275 * cx.w_syn_scale))
        del Waug; gc.collect()
        src = np.arange(N, N + ns)
        print(f"[sub] {sname}: {ns} sources x {len(tgn)} non-DN targets ({ns * len(tgn)} synapses of +1)", flush=True)
        for rate in a.sub_rates:
            for state in ("intact", "silenced"):
                ssim.restore_weights()
                if state == "silenced":
                    ssim.scale_output(S["m"], 0.0)
                for pres in a.presentations:
                    run_cond(ssim, S, {"mode": "sub", "mbons": state, "sub_rate": rate, "n_src": ns, "odor": pres}, *drive(pres, (src, rate)))
        del ssim; gc.collect()
    del Wc

# ---- outputs ----------------------------------------------------------------------------------------------------
if rows:
    df = pd.DataFrame(rows)
    df["sub_calibrated"] = pd.Series(pd.NA, index=df.index, dtype="boolean")   # sub rows only
    sb = df[df["mode"] == "sub"]
    if len(sb):
        lo, hi = a.sub_band[0], a.sub_band[-1]
        cal = sb[(sb.odor == "none") & (sb.mbons == "silenced")].groupby(["set", "sub_rate"])["non-DN targets Hz"].mean()
        if not len(cal):
            print("[sub] calibration needs --presentations with none", flush=True)
        for (s_, r_), v in cal.items():
            ok = bool(lo <= v <= hi)
            df.loc[(df["mode"] == "sub") & (df.set == s_) & (df.sub_rate == r_), "sub_calibrated"] = ok
            print(f"[sub] calibration {s_:6s} sources {r_:4.0f} Hz: non-DN targets {v:5.2f} Hz (no odor, MBONs silenced) -> {'CALIBRATED' if ok else 'outside'} {lo:g}-{hi:g} Hz", flush=True)
        extra["sub_calibration"] = {f"{s_}@{r_:g}": float(v) for (s_, r_), v in cal.items()}

    # self-check: conditions that are the same simulation by construction must agree to the digit
    skip = {"sim_id", "mode", "wall_s", "bypass", "mbons", "mbon_hz", "tonic_hz", "sub_rate", "n_src", "type", "sub_calibrated"}
    num = [c for c in df.columns if c not in skip and c not in ("set", "odor", "seed") and pd.api.types.is_numeric_dtype(df[c])]
    same = df[((df["mode"] == "drive") & (df.mbon_hz == 0)) | ((df["mode"] == "kick-nodn") & (df.tonic_hz == 0) & (df.mbons == "intact"))
              | ((df["mode"] == "bypass") & ~df.bypass.astype(bool) & (df.mbons == "intact"))]
    n_grp, worst = 0, 0.0
    for _, g in same.groupby(["set", "odor", "seed"]):
        if g["mode"].nunique() > 1:
            n_grp += 1
            v = g[num].to_numpy(float)
            worst = max(worst, float(np.nanmax(np.abs(v - v[0]), initial=0.0)))
            nan_bad = bool((np.isnan(v) != np.isnan(v[0])).any())
            worst = np.inf if nan_bad else worst
    if n_grp:
        print(f"[self-check] {n_grp} (set, odor, seed) groups run in >1 mode with identical drive: max |diff| {worst:g} over {len(num)} columns "
              f"-> {'IDENTICAL' if worst == 0 else 'DIFFERENT'}", flush=True)
        extra["self_check"] = {"groups": n_grp, "max_abs_diff": worst}

    main = base + ".csv"
    write_csv(df, main)
    M = np.vstack(dnr)
    live = np.flatnonzero(M.max(axis=0) > 0)
    dl = pd.DataFrame({"sim_id": np.repeat(df.sim_id.to_numpy(), len(live)), "dn_type": np.tile(np.asarray(dn_names)[live], len(df)),
                       "n": np.tile(dn_n[live].astype(int), len(df)), "Hz": M[:, live].ravel()})
    write_csv(dl, base + "_dn_types.csv")
    extra["dn_types"] = {"total": int(len(dn_names)), "active_in_any_sim": int(len(live))}
    print(f"[dn types] {len(live)} of {len(dn_names)} DN types fire in at least one sim", flush=True)

    if a.check_against:
        # the same simulation as an expression_probe row: any 0-Hz drive / kick-nodn / unbypassed-intact row, and every
        # kick-nodn row of a set with no DN target (the reward set: its targets minus DNs are all its targets)
        ref = pd.read_csv(a.check_against, float_precision="round_trip").rename(columns={"mbon_set": "set"})   # exact parse
        ref["tonic_hz"] = ref.tonic_hz.astype(float)
        ours = df[((df["mode"] == "drive") & (df.mbon_hz == 0))
                  | ((df["mode"] == "kick-nodn") & ((df.tonic_hz == 0) | (df.n_target_dns == 0)))
                  | ((df["mode"] == "bypass") & ~df.bypass.astype(bool) & (df.mbons == "intact"))]
        key = ["set", "tonic_hz", "mbons", "odor", "seed"]
        cols = [c for c in ref.columns if c in ours.columns and c not in key + ["wall_s"]]
        mg = ours.merge(ref, on=key, suffixes=("", "_ref"))
        lines, n_bad, dmax = [], 0, 0.0
        for c in cols:
            x, y = mg[c].to_numpy(float), mg[c + "_ref"].to_numpy(float)
            both_nan = np.isnan(x) & np.isnan(y)
            d = np.where(both_nan, 0.0, np.abs(x - y)); d[np.isnan(d)] = np.inf
            bad_i = np.flatnonzero(d > 1e-9)
            n_bad += len(bad_i); dmax = max(dmax, float(d.max(initial=0.0)))
            for i in bad_i[:5]:
                lines.append(f"  MISMATCH {c}: {mg.iloc[i][key].to_dict()} mode {mg.iloc[i]['mode']} ours {x[i]:.10g} ref {y[i]:.10g}")
        head = (f"check-against {a.check_against}: {len(mg)} rows (of {len(ours)} comparable rows; tonic {sorted(set(mg.tonic_hz))}; ref rows {len(ref)}) x {len(cols)} columns, "
                f"{n_bad} mismatched cells (max |diff| {dmax:g}) -> {'MATCH TO THE DIGIT' if n_bad == 0 and len(mg) else 'MISMATCH'}"
                + ("" if a.ms == 1000 else f"  [note: --ms {a.ms:g}; the reference was run at 1000 ms]"))
        print(head, flush=True)
        tmp, chk = _edge.safe_out(os.path.splitext(main)[0] + ".check.txt")
        with open(tmp, "w") as f:
            f.write(head + "\n" + "\n".join(lines) + "\n")
        _edge.finish(tmp, chk); written.append(chk); print("wrote", chk)
        extra["check"] = {"rows": int(len(mg)), "cols": len(cols), "mismatched_cells": n_bad, "max_abs_diff": dmax}

if a.check_against and not rows:
    print("[check-against] skipped: no simulation mode run", flush=True)
if written:
    extra["files"] = written
    extra["wall_total_s"] = round(time.time() - t0, 1)
    print("wrote", _edge.sidecar(written[0] if not rows else base + ".csv", extra))
