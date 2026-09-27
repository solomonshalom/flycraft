#!/usr/bin/env python3
"""Grid probe: the edge-case suite's simulation engine (design_plan.md 2.2 with DECISIONS.md 5-7; RESEARCH_NOTES 23).

One long CSV row per condition x rewiring x drive x seed [x bin]. At the defaults (window protocol, gain 1, 100 Hz,
dt 0.2, no noise) every row is computed exactly as experiments/common.run_trials computes it (seeds 0..n-1, same call
order, same rate expression), so --check-against a social_probe / state_probe / shuffle / sensitivity file must report
zero mismatches: that is the engine's correctness test.

Model       --dataset flywire|malecns  --conn  --min-syn (only a threshold with a cache in data/)  --signs  --eln
            --unclear-ln   (unset = the FLYBRAIN_* environment, as in connectome.load)
Conditions  --conditions base|sensitivity   sensitivity = sensitivity.py's CONDITIONS (checked against its source with ast)
            --cond 'k=v,...' (repeatable; replaces base) keys: label conn min_syn min_syn_mem signs eln unclear gain hz dt
                   t_ref delay legacy noise_hz eps_v eps_g kick_mv rewire(none|global|block|type) shuffle
            --gains a,b crossed with every condition that sets no gain.  Defaults --gain 1 --hz 100 --dt 0.2 --noise-hz 0
            min_syn_mem=K thresholds the min-1 table in memory (nothing is built into data/); K=5 must equal the min5 cache.
            rewire=M,shuffle=S rebuilds shuffle_control.rewire(W, default_rng(--rewire-seed-base + S)); intact rows added.
Drives      --drives all | 'A;B & C@30;...'  term = NAME[@hz] (no @hz: the condition's hz). NAME from input_groups,
            state_groups, the extra groups (Shiu sugar/bitter/JON-CE/JON-F, BM left/right, BM_Ant, BM_InOm, DA1 left/
            right/na), output_groups, 'sel:col=regex,...' or 'type:<cell type>'.  --anchors  --preset A[,B]
Presets     anchors anchors_rate freeze touch_dose persistence state_split states_lite sag_hunger matched_null
            decider_reach ovidn_reach touch_dose_male side_cva_male   (gradient: P3, not implemented)
Protocols   window (default) | settle (--settle-ms discarded first) | bins (--on-ms --first-bins KxMS --bin-ms --off-ms
            --off-first-bins KxMS --noise-off). --ei GROUPS (window/settle; 'deciders' = pC1a-e, aIPg, vpoEN, vpoDN,
            oviDNa/b) runs the read in --ei-step-ms chunks and writes <out>_neurons.csv: v above rest (mean, max, fraction
            of time within 1 mV of threshold), E = sum_i max(W_ij,0) r_i and I (syn*Hz), the mean-field depolarisation
            w_syn*tau_syn*(E-I) mV, active/all presynaptic partners and the top 3 presynaptic types by W_ij r_i.
Readouts    every output_groups group + aBN1, vpoEN, vpoDN (DNp37), pC1a..pC1e, oviDNa, oviDNb, oviIN, DNp13 L/R, MN9 both
            (FlyWire, benchmark's MN9 L+R) / MN9 L/R (male); '<name>' = the mean rate as run_trials, '<name> max1' = the
            largest single-neuron rate.
Output      --out FILE (required, never inside experiments/results/; written as FILE.tmp then renamed) + FILE.json
            sidecar. --check-against REF writes <stem>.check.txt: per-seed files compare only the rows run under the
            reference's model (variant from its name, gain/noise from its _gain/_noise tags or --check-gain/--check-noise,
            default numerics, window protocol; other rows are listed as not comparable); sensitivity files compare seed
            means/SDs per condition label, each (drive, seed) once. The persistence preset writes <stem>_persistence.csv
            (DECISIONS 5: act_n = 0 at the END of the off phase; 10-s drift of the 1-s bins and 0-1 s vs 1-10 s).

  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python3 experiments/edge/grid_probe.py --dataset flywire --drives all --seeds 2 \
      --out experiments/results_edge/x/all.csv --check-against experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv
  ... --preset freeze --cond conn=shiu,min_syn_mem=5 --cond conn=zenodo,min_syn_mem=5 --seeds 5 --ms 600 --out ...
  ... --preset persistence --seeds 2 --out ...        (10 s on / 3 s off; --on-ms / --off-ms shorten it)
  ... --preset decider_reach --seeds 3 --out ...      (prints each decider's top-5 presynaptic types)
  ... --ei deciders --drives 'cVA (Or67d/DA1);song/sound (JO-A);touch (all head bristles);cVA + touch' --gains 1,1.4 --out ...
"""
from __future__ import annotations

import argparse, ast, gc, os, re, sys, time
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge  # puts experiments/ and brain/ on the path
import numpy as np, pandas as pd
from common import connectome, input_groups, output_groups, state_groups, SHIU_SUGAR, SHIU_MN9
from flybrain.lif import LIF, LIFParams

DEF = LIFParams()


def _bool(v):
    v = str(v).strip().lower()
    if v in ("1", "true", "yes"):
        return True
    if v in ("0", "false", "no"):
        return False
    raise ValueError(f"not a boolean: {v!r}")


COND_KEYS = {"label": str, "conn": str, "min_syn": int, "min_syn_mem": int, "signs": str, "eln": float, "unclear": str,
             "gain": float, "hz": float, "dt": float, "t_ref": float, "delay": float, "legacy": _bool, "noise_hz": float,
             "eps_v": float, "eps_g": float, "kick_mv": float, "rewire": str, "shuffle": int}
PRESETS = ("anchors", "anchors_rate", "freeze", "touch_dose", "persistence", "state_split", "states_lite", "sag_hunger",
           "matched_null", "decider_reach", "ovidn_reach", "touch_dose_male", "side_cva_male", "gradient")
SEL_COLS = ("cell_type", "hemibrain_type", "cell_class", "cell_sub_class", "super_class", "side")
SENSORY_CLASSES = r"^(olfactory|gustatory|mechanosensory|visual|hygrosensory|thermosensory|unknown_sensory)$"
TOUCH, FOOD, CVA, JOA = "touch (all head bristles)", "food odor", "cVA (Or67d/DA1)", "song/sound (JO-A)"
SAG, NPF, IPC = "virgin (SAG tonic)", "hungry (NPF tonic)", "fed (IPC tonic)"
EI_DECIDERS = ["pC1a", "pC1b", "pC1c", "pC1d", "pC1e", "aIPg aggr", "vpoEN", "vpoDN (DNp37)", "oviDNa", "oviDNb"]
# decider_reach (DECISIONS 6): each female decider type; its top-5 presynaptic cell types by summed positive W
DECIDERS = [("pC1a", dict(cell_type=r"^pC1a$")), ("pC1b", dict(cell_type=r"^pC1b$")), ("pC1c", dict(cell_type=r"^pC1c$")),
            ("pC1d", dict(cell_type=r"^pC1d$")), ("pC1e", dict(cell_type=r"^pC1e$")), ("aIPg", dict(hemibrain_type=r"^aIPg")),
            ("vpoDN (DNp37)", dict(cell_type=r"^DNp37$")), ("vpoEN", dict(cell_type=r"^vpoEN$")), ("oviDN", dict(cell_type=r"^oviDN"))]
HEADLINE = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "MN9", "PAM (reward DA)",
            "PPL1 (punish DA)", "KC", "DN all", "pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "oviDN egg"]
SHOW = ["DNa L", "DNa R", "GF jump", "MDN back", "DNp13 reject", "pC1a recept", "pC1d/e aggr", "vpoEN/DN accept", "oviDN egg",
        "P1/pC1 male", "pIP10 song cmd", "feed MNs", "MN9", "PPL1 (punish DA)"]
DRIFT_FLOOR_HZ = 0.5      # persistence checks: tolerance never below this (10 % of ~0 Hz is noise)
TOL = 1e-9                # --check-against: |mine - reference| allowed

# sensitivity.py's CONDITIONS, copied verbatim (sensitivity.py runs on import); verified against its source at start-up
SENS_TAIL = [("stimulus 50 Hz", dict(hz=50)), ("stimulus 150 Hz (Shiu default r_poi; the body's maximum)", dict(hz=150)),
             ("dt 0.1 ms (Brian2 default)", dict(dt=0.1)), ("dt 0.5 ms", dict(dt=0.5)),
             ("legacy numerics (first version)", dict(legacy=True)),
             ("connections >= 5 synapses", dict(min_syn=5))]
SENS_F = ([("baseline (env model options, all conns, 100 Hz, dt 0.2)", dict()),
           ("published model: Shiu signs, eLN x1", dict(signs="shiu", eln=1.0)),
           ("known signs, eLN x1", dict(signs="known", eln=1.0)),
           ("Shiu signs, eLN x0.25", dict(signs="shiu", eln=0.25)),
           ("known signs, eLN x0.5", dict(signs="known", eln=0.5)),
           ("known signs, eLN x0.1", dict(signs="known", eln=0.1))] + SENS_TAIL
          + [("Zenodo table, top_nt signs, >= 5 synapses (first version)", dict(conn="zenodo", min_syn=5)),
             ("Zenodo table, top_nt signs, all connections", dict(conn="zenodo", min_syn=1))])
SENS_M = ([("baseline (env model options, all conns, 100 Hz, dt 0.2)", dict()),
           ("published model: eLN x1", dict(signs="shiu", eln=1.0)),
           ("eLN x0.5", dict(eln=0.5)), ("eLN x0.1", dict(eln=0.1)),
           ("eLN x0.25, unclear LNs inhibitory", dict(unclear="inhibitory")),
           ("eLN x0.25, unclear LNs silent", dict(unclear="silent")),
           ("eLN x1, unclear LNs inhibitory", dict(eln=1.0, unclear="inhibitory"))] + SENS_TAIL)


def sens_from_source(dataset):
    """CONDITIONS as experiments/sensitivity.py builds them for `dataset` (parsed with ast, never imported)."""
    tree = ast.parse(open(os.path.join(_edge.EXP, "sensitivity.py")).read())
    conds = []

    def lit(n):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict" and not n.args:
            return {k.arg: lit(k.value) for k in n.keywords}
        if isinstance(n, (ast.List, ast.Tuple)):
            v = [lit(e) for e in n.elts]
            return v if isinstance(n, ast.List) else tuple(v)
        return ast.literal_eval(n)

    def walk(stmts):
        for s in stmts:
            if isinstance(s, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CONDITIONS" for t in s.targets):
                conds[:] = lit(s.value)
            elif isinstance(s, ast.AugAssign) and isinstance(s.target, ast.Name) and s.target.id == "CONDITIONS":
                conds.extend(lit(s.value))
            elif isinstance(s, ast.If):
                t = s.test
                if (isinstance(t, ast.Compare) and isinstance(t.left, ast.Attribute) and t.left.attr == "dataset"
                        and len(t.ops) == 1 and isinstance(t.comparators[0], ast.Constant)):
                    hit = (dataset == t.comparators[0].value) == isinstance(t.ops[0], ast.Eq)
                    walk(s.body if hit else s.orelse)
    walk(tree.body)
    return [tuple(c) for c in conds]


# ---------------------------------------------------------------------------------------------------- conditions
def parse_cond(s):
    d = {}
    for kv in s.split(","):
        if not kv.strip():
            continue
        k, eq, v = kv.partition("=")
        k = k.strip().replace("-", "_")
        if not eq or k not in COND_KEYS:
            raise SystemExit(f"--cond {s!r}: bad key {k!r} (keys: {', '.join(COND_KEYS)})")
        d[k] = COND_KEYS[k](v.strip())
    if d.get("rewire", "none") not in ("none", "global", "block", "type"):
        raise SystemExit(f"--cond {s!r}: rewire must be none|global|block|type")
    return d


def auto_label(d):
    return ",".join(f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}" for k, v in d.items() if k != "label") or "base"


def resolve_cond(d, a):
    """Every field explicit: environment defaults resolved the way connectome.load resolves them."""
    env = os.environ.get
    c = {"label": d["label"]}
    c["conn"] = (d.get("conn") or a.conn or env("FLYBRAIN_CONN") or "shiu").lower() if a.dataset == "flywire" else "all"
    c["min_syn_mem"] = d.get("min_syn_mem")
    if c["min_syn_mem"] is not None:
        if d.get("min_syn", 1) != 1:
            raise SystemExit("min_syn_mem thresholds the min-1 table: do not combine it with min_syn != 1")
        c["min_syn"] = 1
    else:
        c["min_syn"] = int(d["min_syn"] if d.get("min_syn") is not None else a.min_syn if a.min_syn is not None
                           else env("FLYBRAIN_MIN_SYN", 1))
    c["signs"] = (d.get("signs") or a.signs or env("FLYBRAIN_SIGNS") or "shiu").lower()
    c["eln"] = float(d["eln"] if d.get("eln") is not None else a.eln if a.eln is not None else env("FLYBRAIN_ELN", 1.0))
    c["unclear"] = (d.get("unclear") or a.unclear_ln or env("FLYBRAIN_UNCLEAR_LN") or "excitatory").lower()
    c["gain"] = float(d["gain"])
    c["hz"] = float(d.get("hz", a.hz))
    c["dt"] = float(d.get("dt", a.dt))
    for k in ("t_ref", "delay", "eps_v", "eps_g", "kick_mv"):
        c[k] = float(d.get(k, getattr(DEF, k)))
    c["legacy"] = bool(d.get("legacy", False))
    c["noise_hz"] = float(d.get("noise_hz", a.noise_hz))
    c["rewire"] = d.get("rewire", "none")
    c["shuffle"] = -1 if c["rewire"] == "none" else int(d.get("shuffle", 0))
    return {k: c[k] for k in COND_KEYS}


def build_conditions(a):
    raw = []
    if a.conditions == "sensitivity":
        mine = SENS_F if a.dataset == "flywire" else SENS_M
        src = sens_from_source(a.dataset)
        if [(l, dict(o)) for l, o in mine] != [(l, dict(o)) for l, o in src]:
            raise SystemExit("grid_probe: sensitivity.py's CONDITIONS changed; update SENS_F / SENS_M")
        raw += [dict(o, label=l) for l, o in mine]
    if a.conditions == "base" or (a.conditions is None and not a.cond):
        raw.append({"label": "base"})
    for s in a.cond:
        d = parse_cond(s)
        d.setdefault("label", auto_label(d))
        raw.append(d)
    gains = [float(g) for g in a.gains.split(",")] if a.gains else [a.gain]
    crossed = []
    for d in raw:
        crossed += [d] if "gain" in d else [dict(d, gain=g) for g in gains]
    full = []
    for d in crossed:
        c = resolve_cond(d, a)
        if c["rewire"] != "none":                         # intact rows always come with a rewiring (shuffle -1)
            full.append(dict(c, label="intact", rewire="none", shuffle=-1))
        full.append(c)
    seen, out = set(), []
    for c in full:                                        # label kept in the key: two sensitivity labels that resolve alike
        k = tuple(c[f] for f in COND_KEYS)                # (env unset: baseline = published model) both stay checkable
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out


def cache_path(dataset, conn, k):
    return os.path.join(connectome.DATA_DIR, f"connectome_783_{conn}_min{k}.npz" if dataset == "flywire"
                        else f"connectome_malecns_min{k}.npz")


def cx_key(c):
    return (c["conn"], c["min_syn"], c["min_syn_mem"], c["signs"], c["eln"], c["unclear"])


def load_cx(dataset, key):
    """connectome.load with every option explicit; min_syn_mem thresholds the min-1 table in memory."""
    conn, min_syn, mem, signs, eln, unclear = key
    kw = dict(dataset=dataset, conn=conn if dataset == "flywire" else None)
    if mem is None:
        return connectome.load(min_syn=min_syn, signs=signs, eln_scale=eln, unclear_ln=unclear, **kw), {}
    cx = connectome.load(min_syn=1, signs="shiu", eln_scale=1.0, unclear_ln="excitatory", **kw)
    W = cx.W.copy()
    W.data[np.abs(W.data) < mem] = 0
    W.eliminate_zeros()
    info = {"min_syn_mem": mem, "nnz": int(W.nnz)}
    if mem == 5:                                           # the Shiu table is thresholded per row before summing
        z = np.load(cache_path(dataset, conn, 5))
        n5 = int(z["data"].shape[0])
        same = (n5 == W.nnz and np.array_equal(z["indptr"], W.indptr) and np.array_equal(z["indices"], W.indices)
                and np.array_equal(z["data"], W.data))
        info.update(min5_cache_nnz=n5, min5_arrays_identical=bool(same))
        print(f"[min_syn_mem] k=5 sanity: {W.nnz} connections in memory vs {n5} in {os.path.basename(cache_path(dataset, conn, 5))}"
              f" -> {'PASS' if n5 == W.nnz else 'FAIL'} (arrays identical: {same})", flush=True)
        if n5 != W.nnz:
            raise SystemExit("min_syn_mem=5 does not reproduce the min5 cache: aborting")
    if dataset == "malecns":
        print("[min_syn_mem] note: MaleCNS keeps the min-1 w_syn_scale", flush=True)
    cx.W, cx.variant = W, f"{conn}_min{mem}mem"
    connectome.apply_model_options(cx, signs, eln, unclear)
    return cx, info


def build_W(cx, rewire, shuffle, a):
    if rewire == "none":
        return cx.W, 0.0
    from shuffle_control import rewire as _rewire
    nb, block = cx.neurons, None
    if rewire == "block":
        block = pd.factorize(nb.super_class.fillna("na").astype(str).to_numpy())[0]
    elif rewire == "type":
        block = pd.factorize(nb.cell_type.fillna(nb.super_class).fillna("na").astype(str).to_numpy())[0]
    print(f"== rewire {rewire} shuffle {shuffle} (default_rng({a.rewire_seed_base + shuffle}), {a.swaps_per_edge:g} swaps/edge)", flush=True)
    Wn, moved = _rewire(cx.W, np.random.default_rng(a.rewire_seed_base + shuffle), a.swaps_per_edge, block)
    assert np.array_equal(np.diff(Wn.indptr), np.diff(cx.W.tocsr().indptr)), "out-degree changed"
    return Wn, moved


def params_of(c, cx):
    """make_sim's LIFParams at the defaults (w_syn = 0.275 * scale * gain, in that order)."""
    return LIFParams(dt=c["dt"], t_ref=c["t_ref"], delay=c["delay"], noise_hz=c["noise_hz"],
                     w_syn=0.275 * cx.w_syn_scale * c["gain"], legacy=c["legacy"], eps_v=c["eps_v"], eps_g=c["eps_g"],
                     kick_mv=c["kick_mv"])


# ---------------------------------------------------------------------------------------------------- groups, drives
def extra_groups(cx):
    s, ids = cx.select, cx.by_root_ids
    G = {}
    if cx.dataset == "flywire":
        G.update({"Shiu sugar": ids(SHIU_SUGAR + _edge.SUGAR_L), "Shiu bitter": ids(_edge.BITTER),
                  "Shiu JON-CE": ids(_edge.JON_CE), "Shiu JON-F": ids(_edge.JON_F)})
    G.update({"BM left": s(cell_type=r"^BM_", side="^left$"), "BM right": s(cell_type=r"^BM_", side="^right$"),
              "BM_Ant": s(cell_type=r"^BM_Ant"), "BM_InOm": s(cell_type=r"^BM_InOm"),
              "DA1 left": s(cell_type=r"^ORN_DA1$", side="^left$"), "DA1 right": s(cell_type=r"^ORN_DA1$", side="^right$"),
              "DA1 na": s(cell_type=r"^ORN_DA1$", side="^na$")})
    return {k: v for k, v in G.items() if len(v)}


def readouts(cx):
    s = cx.select
    R = dict(output_groups(cx))
    X = {"aBN1": cx.by_root_ids(_edge.ABN1), "vpoEN": s(cell_type=r"^vpoEN$"), "vpoDN (DNp37)": s(cell_type=r"^DNp37$")}
    X.update({t: s(cell_type=rf"^{t}$") for t in ("pC1a", "pC1b", "pC1c", "pC1d", "pC1e")})
    X.update({"oviDNa": s(cell_type=r"^oviDNa"), "oviDNb": s(cell_type=r"^oviDNb$"), "oviIN": s(cell_type=r"^oviIN$"),
              "DNp13 L": s(cell_type=r"^DNp13$", side="^left$"), "DNp13 R": s(cell_type=r"^DNp13$", side="^right$")})
    if cx.dataset == "flywire":
        X["MN9 both"] = cx.by_root_ids(SHIU_MN9 + _edge.MN9_R)
    else:
        X.update({"MN9 L": s(cell_type=r"^MN9$", side="^left$"), "MN9 R": s(cell_type=r"^MN9$", side="^right$")})
    R.update({k: v for k, v in X.items() if len(v)})
    return {k: np.asarray(v, np.int64) for k, v in R.items()}


@dataclass
class Drive:
    name: str
    terms: list                        # [(term name, neuron idx, hz or None = the condition's hz)]
    block: str = ""
    draw: int | None = None
    members: str = ""                  # root ids of a drawn / matched set
    over: dict = field(default_factory=dict)   # call-time overrides for this drive (noise_hz)


class Resolver:
    def __init__(self, cx):
        self.cx = cx
        self.IG, self.SG, self.XG, self.OG = input_groups(cx), state_groups(cx), extra_groups(cx), output_groups(cx)
        nb = cx.neurons
        self.lab = nb.cell_type.fillna(nb.hemibrain_type).fillna("").astype(str).to_numpy()

    def has(self, name):
        return any(name in G for G in (self.IG, self.SG, self.XG, self.OG))

    def term(self, name):
        if name in self.IG:
            return np.concatenate([np.asarray(g, np.int64) for g in self.IG[name]])
        for G in (self.SG, self.XG, self.OG):
            if name in G:
                return np.asarray(G[name], np.int64)
        if name.startswith("sel:"):
            kw = {}
            for kv in name[4:].split(","):
                k, _, v = kv.partition("=")
                if k.strip() not in SEL_COLS:
                    raise SystemExit(f"{name!r}: sel columns are {SEL_COLS}")
                kw[k.strip()] = v.strip()
            idx = self.cx.select(**kw)
        elif name.startswith("type:"):
            idx = np.flatnonzero(self.lab == name[5:])
        else:
            raise SystemExit(f"unknown drive name {name!r} (not an input, state, extra or output group; use sel: or type:)")
        if not len(idx):
            raise SystemExit(f"{name!r} selects no neuron")
        return np.asarray(idx, np.int64)

    def drive(self, spec, block="", **kw):
        terms = []
        for part in spec.split(" & "):
            part = part.strip()
            m = re.match(r"^(.*)@([0-9.]+(?:[eE][-+]?[0-9]+)?)$", part)
            name, hz = (m.group(1).strip(), float(m.group(2))) if m else (part, None)
            if name != "none":
                terms.append((name, self.term(name), hz))
        return Drive(spec, terms, block, **kw)


def rids(cx, idx):
    return ";".join(str(int(r)) for r in cx.root_ids[np.sort(idx)])


def preset_drives(p, res, a, info):
    cx, D, female = res.cx, res.drive, res.cx.dataset == "flywire"
    out = []

    def need(*names):
        miss = [n for n in names if not res.has(n)]
        if miss:
            print(f"[{p}] skipped on {cx.dataset}: no {miss}", flush=True)
        return not miss
    if p == "gradient":
        raise SystemExit("preset gradient is P3 and not implemented (needs senses.py's side split and observe.js conc())")
    if p == "anchors":
        if need("Shiu sugar", "Shiu bitter", "Shiu JON-CE", "Shiu JON-F"):
            specs = (["Shiu sugar@100"] + [f"Shiu sugar@100 & Shiu bitter@{h}" for h in (25, 50, 100)]
                     + ["Shiu bitter@100", "Shiu JON-CE@100", "Shiu JON-F@100", f"{JOA}@100", "sound (JO-B)@100"])
            out += [D(s, "anchors") for s in specs]
    elif p == "anchors_rate":
        if need("Shiu sugar", "Shiu JON-CE", "Shiu JON-F"):
            out += [D(f"{n}@{h}", "anchors_rate") for n in ("Shiu JON-CE", "Shiu JON-F", "Shiu sugar", JOA, "sound (JO-B)")
                    for h in (25, 50, 150, 300)]
    elif p == "freeze":
        out += [D(s, "freeze:base") for s in ("none", f"{FOOD}@100", "food + touch@100", f"{CVA}@100", "cVA + touch@100", f"{TOUCH}@100")]
        # DECISIONS 7: specificity controls -- other large inputs on top of food
        out += [D(f"{FOOD}@100 & {n}@100", "freeze:specificity") for n in ("sugar GRNs", "bitter GRNs", JOA, "wind/gravity (JO-CE)")]
        bm, food = res.term(TOUCH), res.term(FOOD)
        sens = np.union1d(cx.select(super_class="^sensory$"), cx.select(cell_class=SENSORY_CLASSES))
        pool = np.setdiff1d(sens, np.concatenate([bm, food]))     # non-touch sensory, not already driven by the base
        info.setdefault("freeze_random", [])
        for d in range(3):
            sub = np.sort(np.random.default_rng(d).choice(pool, len(bm), replace=False))
            comp = cx.neurons.cell_class.iloc[sub].fillna("na").value_counts()
            print(f"[freeze] random sensory d{d}: {len(sub)} of {len(pool)} (touch set {len(bm)}); "
                  + ", ".join(f"{k} {v}" for k, v in comp.head(5).items()), flush=True)
            info["freeze_random"].append({"draw": d, "n": int(len(sub)), "pool": int(len(pool)), "classes": comp.to_dict()})
            out.append(Drive(f"{FOOD}@100 & random sensory d{d}@100", [(FOOD, food, 100.0), (f"random sensory d{d}", sub, 100.0)],
                             "freeze:specificity", draw=d, members=rids(cx, sub)))
    elif p == "touch_dose":
        bm, food = res.term(TOUCH), res.term(FOOD)
        for base in ("none", f"{FOOD}@100", f"{CVA}@100"):
            for r in (0, 10, 25, 50, 100, 150, 200, 300):
                out.append(D(base if r == 0 else f"{TOUCH}@{r}" if base == "none" else f"{base} & {TOUCH}@{r}", "touch_dose:rate"))
        for f in (0.03, 0.10, 0.25, 0.50, 1.0):
            for d in (range(3) if f < 1 else [0]):             # 100 %: one draw (every draw is the whole set)
                sub = np.sort(np.random.default_rng(d).choice(bm, int(round(f * len(bm))), replace=False))
                nm = f"touch {f * 100:g}% d{d}"
                out.append(Drive(f"{FOOD}@100 & {nm}@200", [(FOOD, food, 100.0), (nm, sub, 200.0)], "touch_dose:fraction",
                                 draw=d, members=rids(cx, sub)))
        out += [D(f"{FOOD}@100 & {t}@200", "touch_dose:fraction") for t in ("BM_Ant", "BM_InOm")]
        out += [D(f"{b}@100 & {t}@{r}", "touch_dose:side") for b in (FOOD, CVA) for r in (100, 200) for t in ("BM left", "BM right", TOUCH)]
        out += [D(s, "touch_dose:feeding") for s in ("sugar GRNs@100", f"sugar GRNs@100 & {TOUCH}@100",
                                                      f"sugar GRNs@100 & {TOUCH}@200", f"bitter GRNs@100 & {TOUCH}@200")]
    elif p == "persistence":
        out += [D(f"{n}@100", "persistence:drive") for n in (TOUCH, CVA, FOOD, JOA, "sound (JO-B)", "sugar GRNs", "pheromones + song + touch")]
        out.append(D("Or47b (VA1v)@90 & CO2 (V)@3", "persistence:drive"))
        out += [Drive(f"none (hum {h:g} Hz, off at offset)", [], "persistence:hum", over={"noise_hz": h}) for h in (0.05, 0.2)]
    elif p == "state_split":
        for s in ("none", f"{SAG}@30", "aroused female (pC1a-c tonic)@30"):
            for i in ("none", f"{TOUCH}@100", f"{JOA}@100"):
                out.append(D(" & ".join(x for x in (s, i) if x != "none") or "none", "state_split"))
    elif p == "states_lite":
        states = [SAG, NPF, IPC] if female else ["courting male (P1/pC1 tonic)", NPF, IPC]
        inp = TOUCH if female else "contact pheromone (ppk23/25)"
        for s in states:
            if need(s, inp):
                out += [D(f"{s}@30", "states_lite"), D(f"{s}@30 & {inp}@100", "states_lite")]
    elif p == "sag_hunger":
        states = ["none", f"{SAG}@30"] + [f"{SAG}@30 & {h}@30" for h in (NPF, IPC, "AstA tonic", "fed (DH44 tonic)")]
        for s in states:
            for i in ("none", f"{TOUCH}@100", "sugar GRNs@100", f"{CVA}@100"):
                out.append(D(" & ".join(x for x in (s, i) if x != "none") or "none", "sag_hunger"))
    elif p == "matched_null":
        out += matched_null(res, info)
    elif p in ("decider_reach", "ovidn_reach"):
        out += decider_reach(res, info, only=["oviDN"] if p == "ovidn_reach" else None)
    elif p == "touch_dose_male":
        for base in ("none", f"{CVA}@100"):
            for r in (0, 10, 25, 50, 100, 150, 200, 300):
                out.append(D(base if r == 0 else f"{TOUCH}@{r}" if base == "none" else f"{base} & {TOUCH}@{r}", "touch_dose_male:rate"))
        full = [("Or47b (VA1v)", 100), ("ppk25 only (female CHC)", 150), (TOUCH, 200)]
        if need(*[n for n, _ in full]):
            for drop in [None] + [n for n, _ in full]:
                out.append(D(" & ".join(f"{n}@{h}" for n, h in full if n != drop), "touch_dose_male:composite"))
    elif p == "side_cva_male":
        if need("DA1 left", "DA1 right"):
            L, R = res.term("DA1 left"), res.term("DA1 right")
            for h in (50, 100, 150):
                out.append(D(f"DA1 left@{h}", "side_cva_male"))
                for d in range(3):
                    sub = np.sort(np.random.default_rng(d).choice(R, min(len(L), len(R)), replace=False))
                    nm = f"DA1 right {len(sub)} d{d}"
                    out.append(Drive(f"{nm}@{h}", [(nm, sub, float(h))], "side_cva_male", draw=d, members=rids(cx, sub)))
                out += [D(f"DA1 right@{h}", "side_cva_male")] + ([D(f"DA1 na@{h}", "side_cva_male")] if res.has("DA1 na") else [])
                out.append(D(f"{CVA}@{h}", "side_cva_male"))
    return out


def matched_null(res, info):
    """Real state group (draw -1) and 20 output-matched random sets from the group's majority super_class."""
    cx = res.cx
    female = cx.dataset == "flywire"
    groups = [(SAG, "SAG"), (NPF, "NPF"), (IPC, "IPC")] if female else [("courting male (P1/pC1 tonic)", "P1"), (NPF, "NPF"), (IPC, "IPC")]
    inputs = ["none", f"{TOUCH}@100"] if female else ["none"]
    Wa = abs(cx.W)
    outsum = np.asarray(Wa.sum(axis=1)).ravel()
    del Wa
    ro = np.unique(np.concatenate(list(readouts(cx).values())))
    sc_all = cx.neurons.super_class.fillna("na").astype(str).to_numpy()
    out = []
    info.setdefault("matched_null", {})
    for gname, short in groups:
        if not res.has(gname):
            print(f"[matched_null] no {gname} on {cx.dataset}", flush=True)
            continue
        G = res.term(gname)
        sc = pd.Series(sc_all[G]).mode().iloc[0]
        base = (sc_all == sc)
        base[G] = False
        base[ro] = False
        n_fb = 0
        for d in range(-1, 20):
            if d < 0:
                sub = G
            else:
                rng, avail, pick = np.random.default_rng(1000 + d), base.copy(), []
                for m in G:
                    t = outsum[m]
                    cand = np.flatnonzero(avail & (np.abs(outsum - t) <= 0.25 * t))
                    if len(cand) < 10:
                        cand = np.flatnonzero(avail & (np.abs(outsum - t) <= 0.5 * t))
                    if not len(cand):                            # nothing within +-50 %: the nearest free neuron
                        n_fb += 1
                        free = np.flatnonzero(avail)
                        cand = free[[np.argmin(np.abs(outsum[free] - t))]]
                    j = int(rng.choice(cand))
                    pick.append(j)
                    avail[j] = False
                sub = np.sort(np.array(pick, np.int64))
            nm = f"{short} real" if d < 0 else f"{short} matched d{d}"
            for i in inputs:
                terms = [(nm, sub, 30.0)] + ([(TOUCH, res.term(TOUCH), 100.0)] if i != "none" else [])
                out.append(Drive(f"{nm}@30" + (f" & {i}" if i != "none" else ""), terms, f"matched_null:{short}", draw=d, members=rids(cx, sub)))
        info["matched_null"][short] = {"n": int(len(G)), "super_class": sc, "pool": int(base.sum()), "fallbacks": n_fb}
        print(f"[matched_null] {short}: {len(G)} neurons, pool {base.sum()} {sc} neurons, 20 draws ({n_fb} nearest-neighbour fallbacks)", flush=True)
    return out


def decider_reach(res, info, only=None):
    """Each decider type's top-5 presynaptic cell types by summed positive W, each alone and all 5 together, 30 / 100 Hz.
    The decider's own type(s) and unlabelled neurons are not candidates; every neuron of a chosen type is driven (its sign
    mix is printed: a type with inhibitory members adds inhibition)."""
    cx = res.cx
    out = []
    info.setdefault("decider_reach", {})
    row_sign = np.sign(np.asarray(cx.W.sum(axis=1)).ravel())
    for dname, sel in DECIDERS:
        if only and dname not in only:
            continue
        T = cx.select(**sel)
        if not len(T):
            print(f"[decider_reach] {dname}: not in {cx.dataset}", flush=True)
            continue
        WT = cx.W[:, T]
        pos = np.asarray(WT.maximum(0).sum(axis=1)).ravel()
        neg = np.asarray(WT.minimum(0).sum(axis=1)).ravel()
        own = set(res.lab[T])
        df = pd.DataFrame({"type": res.lab, "pos": pos, "neg": neg})
        df = df[(df.type != "") & ~df.type.isin(own) & ((df.pos > 0) | (df.neg < 0))]
        g = df.groupby("type").agg(pos=("pos", "sum"), neg=("neg", "sum"), n_pre=("pos", lambda x: int((x > 0).sum())))
        top = g[g.pos > 0].nlargest(5, "pos")
        tot = float(pos.sum())
        print(f"[decider_reach] {dname} ({len(T)} neurons, {tot:.0f} excitatory input synapses): top-5 presynaptic types", flush=True)
        rec, members = [], []
        for k, (t, r) in enumerate(top.iterrows()):
            idx = np.flatnonzero(res.lab == t)
            sg = row_sign[idx]
            sign = "+" if (sg >= 0).all() else "-" if (sg <= 0).all() else f"mixed({(sg > 0).sum()}+/{(sg < 0).sum()}-)"
            print(f"    {k + 1}. {t:18s} n={len(idx):3d} ({int(r.n_pre)} presynaptic)  +W {r.pos:6.0f} syn ({r.pos / max(tot, 1) * 100:4.1f} %)"
                  f"  -W {r.neg:5.0f}  sign {sign}", flush=True)
            rec.append({"type": t, "n": int(len(idx)), "n_pre": int(r.n_pre), "pos_syn": float(r.pos), "neg_syn": float(r.neg),
                        "share": float(r.pos / max(tot, 1)), "sign": sign})
            members.append((t, idx))
        info["decider_reach"][dname] = {"n": int(len(T)), "exc_input_syn": tot, "top5": rec}
        for h in (30.0, 100.0):
            for t, idx in members:
                out.append(Drive(f"{dname} <- {t}@{h:g}", [(f"type:{t}", idx, h)], f"decider_reach:{dname}"))
            if members:
                out.append(Drive(f"{dname} <- top5@{h:g}", [(f"type:{t}", idx, h) for t, idx in members], f"decider_reach:{dname}"))
    return out


def build_drives(res, a, presets, info):
    specs = []
    if a.drives:
        for s in a.drives.split(";"):
            s = s.strip()
            if s == "all":
                specs += ["none"] + list(res.IG)          # social_probe's order
            elif s:
                specs.append(s)
    drives = [res.drive(s) for s in specs]
    for p in presets:
        drives += preset_drives(p, res, a, info)
    if not drives:
        if specs or presets:                               # a preset empty on this dataset must not become 'all'
            raise SystemExit(f"no drive to run on {res.cx.dataset}: presets {presets} gave none")
        drives = [res.drive(s) for s in ["none"] + list(res.IG)]
    seen, out = set(), []
    for d in drives:
        if (d.name, d.block) not in seen:
            seen.add((d.name, d.block))
            out.append(d)
    return out


# ---------------------------------------------------------------------------------------------------- simulation
def drive_arrays(d, c):
    """common.drive_of for this drive under condition c (duplicates kept: n_driven is run_trials' len(idx))."""
    idx = [t[1] for t in d.terms if len(t[1])]
    rate = [np.full(len(t[1]), c["hz"] if t[2] is None else t[2], np.float32) for t in d.terms if len(t[1])]
    if not idx:
        return np.zeros(0, np.int64), np.zeros(0, np.float32)
    return np.concatenate(idx), np.concatenate(rate)


def terms_str(d, c):
    return "|".join(f"{n}@{(c['hz'] if h is None else h):g}" for n, _, h in d.terms)


def rates(counts, R, ms):
    sec = ms / 1000
    out = {k: float(counts[v].sum() / len(v) / sec) for k, v in R.items()}     # run_trials' expression
    out.update({f"{k} max1": float(counts[v].max() / sec) for k, v in R.items()})
    return out


def schedule(total, first, bin_ms):
    """Bin lengths: `first` = [(k, ms), ...] then bin_ms bins; the last bin takes what is left."""
    out, t = [], 0.0
    for k, ms in first:
        for _ in range(k):
            if t + ms <= total + 1e-9:
                out.append(float(ms))
                t += ms
    while t < total - 1e-9:
        b = min(bin_ms, total - t)
        out.append(float(b))
        t += b
    return out


def parse_bins(s):
    if not s:
        return []
    out = []
    for part in s.split(","):
        k, _, ms = part.lower().partition("x")
        out.append((int(k), float(ms)))
    return out


def multiple_of(x, dt):
    return abs(x / dt - round(x / dt)) < 1e-6


@dataclass
class EI:
    targets: np.ndarray
    group_of: dict
    step: float
    Wc: object = None
    rows: list = field(default_factory=list)


def ei_rows(ei, counts, V, ms, sim, res, ident, seed):
    r = counts.astype(np.float64) / (ms / 1000)
    p, out = sim.p, []
    for j, t in enumerate(ei.targets):
        lo, hi = ei.Wc.indptr[j], ei.Wc.indptr[j + 1]
        pre, w = ei.Wc.indices[lo:hi], ei.Wc.data[lo:hi].astype(np.float64)
        rp = r[pre]
        c = w * rp
        E, I = float(c[w > 0].sum()), 0.0 - float(c[w < 0].sum())
        top = ""
        if len(pre):
            ser = pd.Series(c).groupby(np.where(res.lab[pre] == "", "(unlabelled)", res.lab[pre])).sum()
            ser = ser[ser != 0]
            top = "|".join(f"{k}:{ser[k]:+.0f}" for k in ser.abs().sort_values(ascending=False).index[:3])
        vv = V[:, j].astype(np.float64) - p.v_rest
        out.append(dict(ident, seed=seed, group=ei.group_of[int(t)], idx=int(t), root_id=int(res.cx.root_ids[t]),
                        cell_type=res.lab[t], side=str(res.cx.neurons.side.iloc[t]), rate_hz=float(r[t]),
                        v_mean_mv=float(vv.mean()), v_max_mv=float(vv.max()),
                        frac_within_1mv=float((V[:, j] > p.v_thr - 1.0).mean()), E_synhz=E, I_synhz=I,
                        dep_mv=float(p.w_syn * p.tau_syn / 1000 * (E - I)), n_pre=int(len(pre)),
                        n_pre_active=int((rp > 0).sum()), top3_pre=top))
    return out


def run_drive(sim, c, d, R, a, ident, res, ei=None):
    idx, rate = drive_arrays(d, c)
    uniq = np.unique(idx)
    rows, noise0 = [], sim.p.noise_hz
    for s in range(a.seeds):
        if "noise_hz" in d.over:
            sim.p.noise_hz = d.over["noise_hz"]
        base = dict(ident, noise_hz=sim.p.noise_hz, seed=s)
        sim.seed(s); sim.reset(); sim.set_drive(idx, rate)
        if a.protocol == "bins":
            t = 0.0
            for phase, sched in (("on", a.on_sched), ("off", a.off_sched)):
                if phase == "off" and sched:
                    sim.set_drive(np.zeros(0, np.int64), np.zeros(0, np.float32))
                    if a.noise_off is not None:
                        sim.p.noise_hz = a.noise_off
                for b, bms in enumerate(sched):
                    t0 = time.perf_counter(); counts, _ = sim.run(bms); wall = time.perf_counter() - t0
                    tot = int(counts.sum())
                    row = dict(base, phase=phase, bin=b, bin_start_ms=t, bin_ms=bms, noise_now=sim.p.noise_hz,
                               act_n_end=int(sim.act_n.sum()), n_driven=int(len(idx)), total_spikes=tot,
                               recruited_spikes=tot - int(counts[uniq].sum()) if phase == "on" else tot,
                               active_frac=float((counts > 0).mean()), wall_s=round(wall, 3))
                    row.update(rates(counts, R, bms))
                    rows.append(row)
                    t += bms
        else:
            t0 = time.perf_counter()
            if a.protocol == "settle":
                sim.run(a.settle_ms)
            if ei is not None:
                n = int(round(a.ms / ei.step))
                counts, V = np.zeros(sim.N, np.int32), np.empty((n, len(ei.targets)), np.float32)
                for i in range(n):
                    cc, _ = sim.run(ei.step)
                    counts += cc
                    V[i] = sim.v[ei.targets]
            else:
                counts, _ = sim.run(a.ms)
            wall = time.perf_counter() - t0
            tot = int(counts.sum())
            row = dict(base, n_driven=int(len(idx)), total_spikes=tot, recruited_spikes=tot - int(counts[uniq].sum()),
                       active_frac=float((counts > 0).mean()), wall_s=round(wall, 2))
            row.update(rates(counts, R, a.ms))
            rows.append(row)
            if ei is not None:
                ei.rows += ei_rows(ei, counts, V, a.ms, sim, res, {k: ident[k] for k in ("cond_id", "label", "gain", "hz", "variant",
                                                                                         "rewire", "shuffle", "drive", "block")}, s)
        sim.p.noise_hz = noise0
    return rows


def summary_line(rows, R, c, d, t_start):
    df = pd.DataFrame(rows)
    if "phase" in df:
        on = df[df.phase == "on"]
        w = on.bin_ms / on.bin_ms.groupby(on.seed).transform("sum")
        m = {k: float((on[k] * w).groupby(on.seed).sum().mean()) for k in SHOW if k in R}
        end = df[df.phase == "off"]
        tail = f" | end act_n {int(end[end.bin_start_ms == end.bin_start_ms.max()].act_n_end.max()) if len(end) else 'na'}"
        act = on.active_frac.mean()
    else:
        m = {k: df[k].mean() for k in SHOW if k in R}
        tail, act = "", df.active_frac.mean()
    lab = c["label"] + ("" if c["gain"] == 1 else f" g{c['gain']:g}")
    return (f"{lab[:26]:26s} {d.name[:46]:46s} act {act * 100:4.1f}% | " + " ".join(f"{k.split(' ')[0]} {v:5.1f}" for k, v in m.items())
            + tail + f"  ({time.time() - t_start:.0f}s)")


# ---------------------------------------------------------------------------------------------------- checks
def tkey(pairs):
    return "|".join(sorted(f"{n}@{float(h):g}" for n, h in pairs))


def tkey_of(s):
    if not isinstance(s, str) or not s:
        return ""
    return tkey(t.rsplit("@", 1) for t in s.split("|"))


def _same(x, y):
    try:
        x, y = float(x), float(y)
    except (TypeError, ValueError):
        return x == y
    return (np.isnan(x) and np.isnan(y)) or abs(x - y) <= TOL


def ref_kind(path):
    """Kind of a --check-against file from its header; checked before any simulation so a bad file fails fast."""
    if not os.path.exists(path):
        raise SystemExit(f"--check-against: no such file {path}")
    cols = set(pd.read_csv(path, nrows=0).columns)
    if "condition" in cols and any(" -> " in c for c in cols):
        return "sensitivity"
    if not {"seed", "input"} <= cols:
        raise SystemExit(f"--check-against {path}: not a social_probe / state_probe / shuffle / sensitivity file")
    return "state_probe" if "state" in cols else "shuffle" if {"connectome", "shuffle"} <= cols else "social_probe"


def ref_model(path, a):
    """The model a per-seed reference ran: its variant (if the file name carries one), gain and noise (file-name tags,
    or --check-gain / --check-noise; state_probe and shuffle names carry neither), default numerics, window protocol."""
    b = os.path.basename(path)
    v = re.search(r"_((?:shiu|zenodo|all)_min\d+[^_]*)_", b)
    g = re.search(r"_gain([0-9]+(?:\.[0-9]+)?)", b)
    n = re.search(r"_noise([0-9]+(?:\.[0-9]+)?)", b)
    return {"variant": v.group(1) if v else None,
            "gain": a.check_gain if a.check_gain is not None else float(g.group(1)) if g else 1.0,
            "noise_hz": a.check_noise if a.check_noise is not None else float(n.group(1)) if n else 0.0}


def not_comparable(r, model, numerics=("dt", "t_ref", "delay", "eps_v", "eps_g", "kick_mv")):
    """Why row r was not run under the reference's model ('' = comparable): such rows are skipped, not mismatches."""
    why = []
    if r["protocol"] != "window":
        why.append(f"protocol {r['protocol']}")
    if model.get("variant") and r["variant"] != model["variant"]:
        why.append(f"variant {r['variant']}")
    if abs(float(r["gain"]) - model["gain"]) > 1e-12:
        why.append(f"gain {r['gain']:g}")
    if abs(float(r["noise_hz"]) - model["noise_hz"]) > 1e-12:
        why.append(f"noise {r['noise_hz']:g} Hz")
    why += [f"{k} {r[k]:g}" for k in numerics if float(r[k]) != float(getattr(DEF, k))]
    if "dt" in numerics and bool(r["legacy"]):
        why.append("legacy")
    return ", ".join(why)


def check_against(df, path, a):
    """Per-seed files (social_probe, state_probe, shuffle): every shared numeric column for the same drive and seed,
    for the rows run under the reference's model (ref_model; other rows are listed as not comparable).
    Sensitivity files: seed mean / sd / active% per '<input> -> <output>' cell of the same condition label (gain 1).
    A drive run twice (e.g. an --anchors drive equal to an 'all' drive) counts once per seed."""
    ref = pd.read_csv(path)
    mine = df.copy()
    mine["_t"] = mine.drive_terms.map(tkey_of)
    mine["_con"] = np.where(mine.rewire == "none", "intact", mine.rewire)
    mism, lines, per = [], [], {}
    if ref_kind(path) == "sensitivity":
        kind = "sensitivity"
        base = {"variant": None, "gain": 1.0, "noise_hz": 0.0}
        ok = [not not_comparable(r, base, numerics=("t_ref", "delay", "eps_v", "eps_g", "kick_mv"))
              for r in mine.to_dict("records")]
        mine = mine[np.asarray(ok, bool)] if len(mine) else mine
        for rr in ref.to_dict("records"):
            lab = rr["condition"]
            sub0 = mine[(mine.label == lab) & (mine._con == "intact")]
            st = per.setdefault(lab, dict(cells=0, mism=0, missing=0))
            if sub0.empty:
                st["missing"] += 1
                continue
            if "connectome" in rr and sub0.variant.iloc[0] != rr["connectome"]:
                st["mism"] += 1
                mism.append(f"{lab}: variant {sub0.variant.iloc[0]} vs {rr['connectome']}")
            hz = float(sub0.hz.iloc[0])
            for col in ref.columns:
                if " -> " in col and not col.endswith(" sd"):
                    inp, outn = col.split(" -> ", 1)
                    what = [(outn, "mean", col), (outn, "std", col + " sd")]
                elif col.endswith(" active%"):
                    inp, what = col[:-len(" active%")], [("active_frac", "act", col)]
                else:
                    continue
                if pd.isna(rr[col]):
                    continue
                sub = sub0[sub0._t == ("" if inp == "none" else tkey([(inp, hz)]))].drop_duplicates("seed")
                for o, how, rc in what:
                    if rc not in rr or pd.isna(rr[rc]):
                        continue
                    if sub.empty or o not in sub.columns:
                        st["missing"] += 1
                        continue
                    v = sub[o].mean() if how == "mean" else sub[o].std() if how == "std" else sub[o].mean() * 100
                    st["cells"] += 1
                    if not _same(v, rr[rc]):
                        st["mism"] += 1
                        mism.append(f"{lab} | {rc}: {v!r} vs {rr[rc]!r}")
        for lab, st in per.items():
            lines.append(f"condition {lab!r}: {st['cells']} cells compared, {st['mism']} mismatches, {st['missing']} missing")
    else:
        kind = ref_kind(path)
        model = ref_model(path, a)
        m = re.search(r"_state([0-9.]+)\.csv$", path)
        hz_st = a.check_state_hz or (float(m.group(1)) if m else 30.0)
        hz_in = a.check_hz

        def rkey(r):
            ts = ([(r["state"], hz_st)] if kind == "state_probe" and r["state"] != "none" else []) + \
                 ([(r["input"], hz_in)] if r["input"] != "none" else [])
            con, sh = (r["connectome"], int(r["shuffle"])) if kind == "shuffle" else ("intact", -1)
            return (con, sh, tkey(ts), int(r["seed"]))
        idx = {rkey(r): r for r in ref.to_dict("records")}
        skip = {"seed", "wall_s", "input", "state", "connectome", "shuffle"}
        cols = [c for c in ref.columns if c in mine.columns and c not in skip and pd.api.types.is_numeric_dtype(ref[c])]
        for r in mine.to_dict("records"):
            cid = (r["cond_id"], r["label"], r["gain"], r["_con"], r["shuffle"])
            st = per.setdefault(cid, dict(rows=0, cells=0, mism=0, nomatch=0, skipped=0, why=""))
            why = not_comparable(r, model)
            if why:
                st["skipped"] += 1
                st["why"] = st["why"] or why
                continue
            k = (r["_con"], int(r["shuffle"]), r["_t"], int(r["seed"]))
            rr = idx.get(k)
            if rr is None:
                st["nomatch"] += 1
                continue
            st["rows"] += 1                                     # a drive run twice (two blocks) is checked twice
            for c in cols:
                st["cells"] += 1
                if not _same(r[c], rr[c]):
                    st["mism"] += 1
                    mism.append(f"{r['label']} | {r['drive']} | seed {r['seed']} | {c}: {r[c]!r} vs {rr[c]!r}")
        for (cid, lab, g, con, sh), st in per.items():
            lines.append(f"condition {cid} {lab!r} gain {g:g} {con}{'' if sh < 0 else f' shuffle {sh}'}: {st['rows']} rows compared "
                         f"({st['cells']} cells), {st['mism']} mismatches, {st['nomatch']} rows without a reference row"
                         + (f", {st['skipped']} rows not comparable ({st['why']})" if st["skipped"] else ""))
        lines.insert(0, f"reference model: variant {model['variant'] or '(not in the file name: any)'}, gain {model['gain']:g}, "
                        f"noise {model['noise_hz']:g} Hz, default numerics, window protocol")
        lines.insert(0, f"columns compared: {', '.join(cols)}")
    n_cells = sum(st["cells"] for st in per.values())
    total = f"TOTAL: {n_cells} cells compared, {len(mism)} mismatches (tolerance {TOL:g})"
    warn = ["WARNING: no cell was compared"] if n_cells == 0 else []
    txt = [f"check-against {path} (kind {kind})"] + lines + [total] + warn + (["mismatches (first 100):"] + mism[:100] if mism else [])
    return "\n".join(txt), {"file": path, "kind": kind, "cells": n_cells, "mismatches": len(mism)}


def persistence_checks(df, R, a):
    """DECISIONS 5: (1) no self-sustained activity: act_n = 0 and no spike at the END of the off phase; (2) 10-s drift:
    the 1-s on-bins after the first second lie within max(10 %, 2 seed-SD, floor) of each other with no trend, and the
    0-1 s rate is within max(10 %, floor) of the 1-s bins' mean."""
    rows, lines = [], []
    heads = [k for k in HEADLINE if k in R]
    for (cid, drive), g in df[df.protocol == "bins"].groupby(["cond_id", "drive"], sort=False):
        on, off = g[g.phase == "on"], g[g.phase == "off"]
        base = {"cond_id": cid, "label": g.label.iloc[0], "gain": g.gain.iloc[0], "drive": drive, "block": g.block.iloc[0],
                "noise_on": g.noise_hz.iloc[0]}
        on_ms = float((on.bin_ms.groupby(on.seed).sum()).max()) if len(on) else 0.0
        brain = dict(base, readout="(brain)")
        if len(off):
            last = off[off.bin_start_ms == off.bin_start_ms.max()]
            live = off[off.total_spikes > 0]
            t_sil = float((live.bin_start_ms + live.bin_ms).groupby(live.seed).max().max() - on_ms) if len(live) else 0.0
            brain.update(end_act_n_max=int(last.act_n_end.max()), end_spikes_max=int(last.total_spikes.max()),
                         silent_by_ms=t_sil, silent_at_end=bool(last.act_n_end.max() == 0 and last.total_spikes.max() == 0))
        rows.append(brain)
        full = on[(on.bin_ms == a.bin_ms) & (on.bin_start_ms >= 1000 - 1e-9)]
        first = on[on.bin_start_ms < 1000 - 1e-9]
        fails = []
        for k in heads:
            rec = dict(base, readout=k)
            if len(full.bin_start_ms.unique()) >= 2:
                m = full.groupby("bin_start_ms")[k].mean()
                sd = full.groupby("bin_start_ms")[k].std().fillna(0.0)
                rest = float(m.mean())
                tol = max(0.10 * abs(rest), 2 * float(sd.mean()), DRIFT_FLOOR_HZ)
                x = (m.index.to_numpy() + a.bin_ms / 2) / 1000
                slope = float(np.polyfit(x, m.to_numpy(), 1)[0]) if len(m) >= 3 else 0.0
                trend = abs(slope) * (x[-1] - x[0])
                rec.update(rest_hz=rest, bin_min=float(m.min()), bin_max=float(m.max()), tol=tol, slope_hz_per_s=slope,
                           drift_ok=bool(m.max() - m.min() <= tol and trend <= tol))
                if len(first):
                    f = float(((first[k] * first.bin_ms).groupby(first.seed).sum() / first.bin_ms.groupby(first.seed).sum()).mean())
                    rec.update(first_s_hz=f, first_ok=bool(abs(f - rest) <= max(0.10 * abs(rest), DRIFT_FLOOR_HZ)))
                if not rec["drift_ok"] or not rec.get("first_ok", True):
                    fails.append(f"{k} ({rec.get('first_s_hz', float('nan')):.1f} | {rec['bin_min']:.1f}-{rec['bin_max']:.1f} Hz)")
            rows.append(rec)
        sil = brain.get("silent_at_end")
        lines.append(f"{str(base['label'])[:20]:20s} {drive[:44]:44s} silent at end of off: {'yes' if sil else 'NO' if sil is not None else 'n/a'}"
                     + (f" (spikes stop {brain['silent_by_ms']:.0f} ms after offset; end act_n {brain['end_act_n_max']})" if sil is not None else "")
                     + (f" | drift/first-second fails: {', '.join(fails)}" if fails else " | drift ok" if len(full.bin_start_ms.unique()) >= 2 else " | drift n/a (< 2 one-second bins)"))
    return pd.DataFrame(rows), lines


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", choices=["flywire", "malecns"], default="flywire")
    ap.add_argument("--conn", default=None)
    ap.add_argument("--min-syn", type=int, default=None)
    ap.add_argument("--signs", default=None)
    ap.add_argument("--eln", type=float, default=None)
    ap.add_argument("--unclear-ln", default=None)
    ap.add_argument("--conditions", choices=["base", "sensitivity"], default=None)
    ap.add_argument("--cond", action="append", default=[], metavar="K=V,...")
    ap.add_argument("--gain", type=float, default=1.0)
    ap.add_argument("--gains", default=None, help="comma list crossed with every condition")
    ap.add_argument("--hz", type=float, default=100.0)
    ap.add_argument("--dt", type=float, default=0.2)
    ap.add_argument("--noise-hz", type=float, default=0.0)
    ap.add_argument("--drives", default=None, help="'all' or 'A;B & C@30;...'")
    ap.add_argument("--anchors", action="store_true")
    ap.add_argument("--preset", default=None, help=",".join(PRESETS))
    ap.add_argument("--protocol", choices=["window", "settle", "bins"], default="window")
    ap.add_argument("--settle-ms", type=float, default=1000.0)
    ap.add_argument("--on-ms", type=float, default=None)
    ap.add_argument("--first-bins", default=None, help="KxMS[,KxMS] at the start of the on phase")
    ap.add_argument("--bin-ms", type=float, default=None)
    ap.add_argument("--off-ms", type=float, default=None)
    ap.add_argument("--off-first-bins", default=None, help="KxMS[,KxMS] at the start of the off phase")
    ap.add_argument("--noise-off", type=float, default=None, help="background rate from drive offset on")
    ap.add_argument("--ei", default=None, help="readout groups (or 'deciders') for voltage and E/I input")
    ap.add_argument("--ei-step-ms", type=float, default=1.0)
    ap.add_argument("--rewire-seed-base", type=int, default=100)
    ap.add_argument("--swaps-per-edge", type=float, default=3.0)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--ms", type=float, default=1000.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check-against", default=None)
    ap.add_argument("--check-hz", type=float, default=100.0, help="input rate of the reference file")
    ap.add_argument("--check-state-hz", type=float, default=None, help="state rate of a state_probe reference (default: from its name)")
    ap.add_argument("--check-gain", type=float, default=None, help="gain of a per-seed reference (default: its _gain tag, else 1)")
    ap.add_argument("--check-noise", type=float, default=None, help="noise of a per-seed reference (default: its _noise tag, else 0)")
    a = ap.parse_args()
    if a.check_against:
        ref_kind(a.check_against)                          # fail before hours of simulation, not after

    presets = [p.strip() for p in (a.preset or "").split(",") if p.strip()] + (["anchors"] if a.anchors else [])
    bad = [p for p in presets if p not in PRESETS]
    if bad:
        ap.error(f"unknown preset {bad}; known: {', '.join(PRESETS)}")
    if a.dataset == "flywire":
        _edge.check_constants()
    if "persistence" in presets:                           # 10 s on (10 x 100 ms, then 1 s), 3 s off (4 x 50 ms, then 1 s)
        if a.protocol != "bins":
            print("[persistence] protocol -> bins", flush=True)
        a.protocol = "bins"
        a.on_ms = 10000.0 if a.on_ms is None else a.on_ms
        a.first_bins = "10x100" if a.first_bins is None else a.first_bins
        a.off_ms = 3000.0 if a.off_ms is None else a.off_ms
        a.off_first_bins = "4x50" if a.off_first_bins is None else a.off_first_bins
        a.noise_off = 0.0 if a.noise_off is None else a.noise_off
    a.on_ms = a.ms if a.on_ms is None else a.on_ms
    a.bin_ms = min(1000.0, a.on_ms) if a.bin_ms is None else a.bin_ms
    a.off_ms = 0.0 if a.off_ms is None else a.off_ms
    a.on_sched = schedule(a.on_ms, parse_bins(a.first_bins), a.bin_ms)
    a.off_sched = schedule(a.off_ms, parse_bins(a.off_first_bins), a.bin_ms)
    if a.ei and a.protocol == "bins":
        ap.error("--ei samples the read window: use --protocol window or settle")

    conds = build_conditions(a)
    for i, c in enumerate(conds):
        c["cond_id"] = i
        if c["min_syn_mem"] is None and not os.path.exists(cache_path(a.dataset, c["conn"], c["min_syn"])):
            raise SystemExit(f"min_syn {c['min_syn']}: no cache {cache_path(a.dataset, c['conn'], c['min_syn'])}; "
                             f"use --cond min_syn_mem={c['min_syn']} (nothing is ever built into data/)")
        if c["min_syn_mem"] is not None:                   # thresholds the min-1 cache (and k=5 compares with min5)
            for k in (1,) + ((5,) if c["min_syn_mem"] == 5 else ()):
                if not os.path.exists(cache_path(a.dataset, c["conn"], k)):
                    raise SystemExit(f"min_syn_mem: no cache {cache_path(a.dataset, c['conn'], k)} (nothing is ever built into data/)")
        if a.protocol == "bins":
            for b in a.on_sched + a.off_sched:
                if not multiple_of(b, c["dt"]):
                    raise SystemExit(f"bin {b} ms is not a multiple of dt {c['dt']} (run() rounds ms/dt)")
        if a.ei and not (multiple_of(a.ei_step_ms, c["dt"]) and multiple_of(a.ms, a.ei_step_ms)):
            raise SystemExit(f"--ei-step-ms {a.ei_step_ms} must be a multiple of dt {c['dt']} and divide --ms {a.ms}")
    tmp, out = _edge.safe_out(a.out)
    stem = os.path.splitext(out)[0]
    print(f"grid_probe: {len(conds)} condition(s), presets {presets or '-'}, protocol {a.protocol}, seeds {a.seeds}, "
          + (f"on {a.on_ms:g} / off {a.off_ms:g} ms ({len(a.on_sched)}+{len(a.off_sched)} bins)" if a.protocol == "bins" else f"{a.ms:g} ms"),
          flush=True)
    for c in conds:
        print("  condition", c["cond_id"], {k: c[k] for k in COND_KEYS}, flush=True)

    rows, ei_all, info, t_start = [], [], {"load": {}, "frac_moved": {}}, time.time()
    by_key = {}
    for c in conds:
        by_key.setdefault(cx_key(c), []).append(c)
    for key, cl in by_key.items():
        cx, linfo = load_cx(a.dataset, key)
        print(cx, flush=True)
        info["load"][cx.variant] = linfo
        res, R = Resolver(cx), readouts(cx)
        drives = build_drives(res, a, presets, info)
        print(f"{len(drives)} drives x {a.seeds} seeds; readouts: {', '.join(f'{k} {len(v)}' for k, v in R.items())}", flush=True)
        ei = None
        if a.ei:
            names = []
            for n in (x.strip() for x in a.ei.split(",")):
                if n == "deciders":                        # the ones this dataset has
                    names += [x for x in EI_DECIDERS if x in R]
                elif n in R:
                    names.append(n)
                else:
                    raise SystemExit(f"--ei: unknown readout {n!r}; readouts are {list(R)}")
            gof = {}
            for n in names:
                for t in R[n]:
                    gof.setdefault(int(t), []).append(n)
            ei = EI(np.array(sorted(gof), np.int64), {t: "/".join(v) for t, v in gof.items()}, a.ei_step_ms)
        by_w = {}
        for c in cl:
            by_w.setdefault((c["rewire"], c["shuffle"]), []).append(c)
        for (rw, sh), wl in sorted(by_w.items(), key=lambda kv: (kv[0][0] != "none", kv[0])):
            W, moved = build_W(cx, rw, sh, a)
            info["frac_moved"][f"{cx.variant}|{rw}|{sh}"] = moved
            if ei is not None:
                ei.Wc = W[:, ei.targets].tocsc()
            by_s = {}
            for c in wl:
                by_s.setdefault((c["dt"], c["t_ref"], c["delay"], c["legacy"]), []).append(c)
            for skey, sl in by_s.items():
                sim = None
                for c in sl:
                    p = params_of(c, cx)
                    if sim is None:
                        sim = LIF(W, p, seed=0)
                    else:
                        sim.p = p                          # the fields a condition changes are read on every call
                    for d in drives:
                        ident = {"cond_id": c["cond_id"], **{k: c[k] for k in COND_KEYS}, "variant": cx.variant,
                                 "frac_moved": moved, "protocol": a.protocol, "drive": d.name, "drive_terms": terms_str(d, c),
                                 "block": d.block, "draw": d.draw, "members": d.members}
                        r = run_drive(sim, c, d, R, a, ident, res, ei)
                        rows += r
                        print(summary_line(r, R, c, d, t_start), flush=True)
                del sim
                gc.collect()
            if ei is not None:
                ei.Wc = None
            del W                                          # a rewired W is freed here; cx.W goes with cx below
            gc.collect()
        if ei is not None:
            ei_all += ei.rows
        pd.DataFrame(rows).to_csv(tmp, index=False)       # checkpoint after every connectome
        del cx, res, R, drives
        gc.collect()

    df = pd.DataFrame(rows)
    df = df[[c for c in df.columns if c != "members"] + ["members"]]
    df.to_csv(tmp, index=False)
    _edge.finish(tmp, out)
    written = [out]
    print(f"wrote {out} ({len(df)} rows, {time.time() - t_start:.0f}s)", flush=True)
    if a.ei:
        t2, o2 = _edge.safe_out(stem + "_neurons.csv")
        pd.DataFrame(ei_all).to_csv(t2, index=False)
        written.append(_edge.finish(t2, o2))
        print(f"wrote {o2} ({len(ei_all)} neuron rows)", flush=True)
    if a.protocol == "bins" and "persistence" in presets:
        R0 = set(c for c in df.columns if not c.endswith(" max1"))
        pc, lines = persistence_checks(df, R0, a)
        t3, o3 = _edge.safe_out(stem + "_persistence.csv")
        pc.to_csv(t3, index=False)
        written.append(_edge.finish(t3, o3))
        print("persistence checks (DECISIONS 5):\n  " + "\n  ".join(lines), flush=True)
        info["persistence"] = {"silent_at_end_all": bool(pc["silent_at_end"].dropna().all()) if "silent_at_end" in pc else None,
                               "drift_fails": int((pc.get("drift_ok", pd.Series(dtype=bool)) == False).sum())}  # noqa: E712
        print(f"wrote {o3}", flush=True)
    if a.check_against:
        txt, summ = check_against(df, a.check_against, a)
        t4, o4 = _edge.safe_out(stem + ".check.txt")
        with open(t4, "w") as f:
            f.write(txt + "\n")
        written.append(_edge.finish(t4, o4))
        info["check"] = summ
        print(txt if summ["mismatches"] else "\n".join(l for l in txt.split("\n") if not l.startswith("columns")), flush=True)
        print(f"wrote {o4}", flush=True)
    info.update(conditions=conds, presets=presets, protocol=a.protocol, n_rows=int(len(df)), outputs=written,
                on_sched=a.on_sched if a.protocol == "bins" else None, off_sched=a.off_sched if a.protocol == "bins" else None)
    _edge.sidecar(out, info)


if __name__ == "__main__":
    main()
