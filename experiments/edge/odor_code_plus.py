#!/usr/bin/env python3
"""Odor code, edge cases: finer eLN scales, eLN transmitter subsets, drive rates, every glomerulus and the odor library
(edge-case suite, RESEARCH_NOTES 23; design_plan.md section 2.5).

experiments/odor_code.py (Fig 9) runs on import, so it is not imported: its variant parser, its 10 test odours and its
row columns are copied here and checked against its source at start-up.

Models. The connectome is loaded ONCE, raw (signs shiu, eLN x1); connectome.load() is that raw load followed by
apply_model_options(), so applying the options to a copy gives the same W that odor_code.py simulates (the check below
tests it to the digit).
  --variants      odor_code.py syntax, comma list: shiu | known | known+elnX | shiu+elnX ('none' = no plain variant)
  --eln-subsets   [letters, default a-f] eLN = antennal-lobe LN with positive row sign under the known-transmitter rule
                  (eLN x1), split by top_nt into ach / mod (serotonin|dopamine|octopamine) / gg (gaba|glutamate) /
                  other. Each subset is W = diags(scale) @ W; every eLN not named stays x1:
                    a all eLN x0.25 (asserted equal to apply_model_options(known, 0.25))   b ACh x0.25
                    c non-ACh x0.25    d mod x0    e mod x0 + ACh x0.25    f gg eLNs flipped to -1
Drives (Poisson at every --hz for --ms, seeds 0..n-1 seeded per trial as in odor_code.py):
  test10     the 10 odours of odor_code.py (9 single glomeruli + the food blend)
  glomeruli  every ORN_<glomerulus> type alone (53 in FlyWire)
  library    senses.SensoryEncoder.odor(class, r_max=hz), both antennae, for each ODOR_LIBRARY class
Rows: every odor_code.py column, then hz, odor_set, model, eln_subset, ms, pn_driven_hz (mean PN rate over the driven
glomeruli), glomeruli_over_10hz_orn / n_glomeruli_orn (only PN glomeruli that receive an ORN_ type; odor_code.py's 59
PN groups also count 'multi' and glomeruli without ORNs; ORN_VM6l/m/v feed the PN group VM6), eln_fixed_hz and
eln_{ach,mod,gg,other}_hz (the FIXED eLN set of --eln-subsets, by class, in every model; odor_code.py's eln_hz/iln_hz
use the simulated model's own row sign, so a silenced or flipped eLN leaves them). pn_cognate_hz = the glomerulus
itself (test10: exactly as odor_code.py); for a library class its strongest glomerulus (NaN if tied, e.g. 'food').
Overlap (per variant x hz x odour set, every odour pair): KC Jaccard over seed pairs with NaN when both codes are
empty (nanmean; jaccard_zero scores those 0, as odor_code.py does), PN-vector cosine (per PN, and per glomerulus
mean), live = mean kc_active >= --live-min (0.5 %) for both odours; summary rows (kind=summary) for within / between
odours over all odours and over live ones only.
Check: rows of a --variants variant at test10, 100 Hz, 500 ms must equal experiments/results/odor_code_<dataset>.csv
(every column but wall_s, the seeds both have; read only), and jaccard_zero its _overlap.csv when --seeds matches.
A reference row missing from the run (no --limit) also counts as a difference. Report only; --strict exits 3 on a
difference (after writing). --skip-existing skips when the sidecar <stem>.json (written last) exists.

  python experiments/edge/odor_code_plus.py --dataset flywire --out-dir DIR [--variants known+eln0.25,...]
      [--eln-subsets [a-f]] [--hz 100,150] [--odors test10,glomeruli,library] [--seeds 2] [--ms 500] [--limit N]
      [--tag T] [--check-against auto|none|CSV] [--strict] [--skip-existing]
Writes DIR/<stem>.csv (rows), <stem>_overlap.csv, <stem>_codes.npz (active KC sets bit-packed, PN rates) and
<stem>.json; stem = odor_code_plus_<dataset>_hz<list>_<sets>[_elnsub][_<tag>].
"""
import argparse, dataclasses, gc, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge                                      # puts experiments/ and brain/ on sys.path
import numpy as np, pandas as pd, scipy.sparse as sp
from common import make_sim
from flybrain import connectome
from flybrain.senses import ODOR_LIBRARY, SensoryEncoder

SUBSETS = {   # letter: (label, {eLN class: output factor}); -1 flips the sign
    "a": ("all eLN x0.25", {"ach": 0.25, "mod": 0.25, "gg": 0.25, "other": 0.25}),
    "b": ("ACh x0.25", {"ach": 0.25}),
    "c": ("non-ACh x0.25", {"mod": 0.25, "gg": 0.25, "other": 0.25}),
    "d": ("mod x0", {"mod": 0.0}),
    "e": ("mod x0, ACh x0.25", {"mod": 0.0, "ach": 0.25}),
    "f": ("gg flipped", {"gg": -1.0}),
}
MOD, GG = ("serotonin", "dopamine", "octopamine"), ("gaba", "glutamate")
TEST10 = ("DM2", "DL5", "DA1", "VA1v", "DM1", "VM2", "V", "DC3", "DA2")
FOOD = ("DM1", "DM2", "DM4", "VA2", "VM2")
SETS_OK = ("test10", "glomeruli", "library")
SHORT = {"test10": "test10", "glomeruli": "glom", "library": "lib"}

ap = argparse.ArgumentParser(description="odor_code.py edge cases (design_plan.md 2.5)")
ap.add_argument("--dataset", default="flywire", choices=("flywire", "malecns"))
ap.add_argument("--out-dir", required=True)
ap.add_argument("--variants", default="known+eln0.25", help="odor_code.py syntax, comma list; 'none' = subsets only")
ap.add_argument("--eln-subsets", nargs="?", const="a-f", default="", help="letters a-f (bare flag = all)")
ap.add_argument("--hz", default="100", help="comma list of ORN drive rates")
ap.add_argument("--odors", default="test10", help="comma list of test10,glomeruli,library")
ap.add_argument("--seeds", type=int, default=2)
ap.add_argument("--ms", type=float, default=500)
ap.add_argument("--limit", type=int, default=0, help="first N odours of each set (0 = all)")
ap.add_argument("--live-min", type=float, default=0.005, help="mean kc_active for an odour to count as live")
ap.add_argument("--tag", default="")
ap.add_argument("--check-against", default="auto", help="auto = experiments/results/odor_code_<dataset>.csv; none")
ap.add_argument("--strict", action="store_true", help="exit 3 if the check finds a difference")
ap.add_argument("--skip-existing", action="store_true", help="exit 0 if the rows file already exists")
a = ap.parse_args()


def parse_variants(spec):
    """odor_code.py's --variants parser (copied), plus 'none'."""
    out = []
    for v in spec.split(","):
        v = v.strip()
        if not v or v == "none":
            continue
        signs = "known" if v.startswith("known") else "shiu"
        eln = float(v.split("eln")[1]) if "eln" in v else 1.0
        out.append((v, signs, eln))
    return out


def parse_letters(spec):
    spec = spec.replace(",", "").replace(" ", "").lower()
    if len(spec) == 3 and spec[1] == "-":
        spec = "".join(chr(c) for c in range(ord(spec[0]), ord(spec[2]) + 1))
    if set(spec) - set(SUBSETS):
        ap.error(f"--eln-subsets: unknown letters {sorted(set(spec) - set(SUBSETS))}")
    return sorted(set(spec))


# drift guard: the copied pieces must still be odor_code.py's
_src = open(os.path.join(_edge.EXP, "odor_code.py")).read()
for frag in ('for g in ("DM2", "DL5", "DA1", "VA1v", "DM1", "VM2", "V", "DC3", "DA2")',
             'ODORS["food blend (DM1+DM2+DM4+VA2+VM2)"] = s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$")',
             'signs = "known" if v.startswith("known") else "shiu"', 'eln = float(v.split("eln")[1]) if "eln" in v else 1.0',
             'glom = n.cell_type.fillna("").iloc[PN].str.extract(r"^([A-Z]+\\d*[a-z]*)_")[0].fillna("multi").to_numpy()',
             'sim.seed(seed); sim.reset(); sim.set_drive(idx, np.full(len(idx), a.hz, np.float32))'):
    if frag not in _src:
        raise SystemExit(f"odor_code.py changed; re-copy: {frag}")

VARIANTS = parse_variants(a.variants)
SUBS = parse_letters(a.eln_subsets) if a.eln_subsets else []
HZ = [float(h) for h in a.hz.split(",") if h.strip()]
SETS = [x.strip() for x in a.odors.split(",") if x.strip()]
if set(SETS) - set(SETS_OK):
    ap.error(f"--odors: unknown {sorted(set(SETS) - set(SETS_OK))}; choose from {SETS_OK}")
if not (VARIANTS or SUBS) or not HZ or not SETS:
    ap.error("nothing to run")
UNCLEAR = (os.environ.get("FLYBRAIN_UNCLEAR_LN") or "excitatory").lower()   # as connectome.load does for odor_code.py

stem = (f"odor_code_plus_{a.dataset}_hz{'-'.join(f'{h:g}' for h in HZ)}_{'-'.join(SETS)}"
        + ("_elnsub" if SUBS else "") + (f"_{a.tag}" if a.tag else ""))
P_ROWS = os.path.join(a.out_dir, stem + ".csv")
P_OV = os.path.join(a.out_dir, stem + "_overlap.csv")
P_NPZ = os.path.join(a.out_dir, stem + "_codes.npz")
P_JSON = os.path.join(a.out_dir, stem + ".json")   # _edge.sidecar(P_ROWS) writes it after every other output
if a.skip_existing and all(os.path.exists(p) for p in (P_ROWS, P_OV, P_NPZ, P_JSON)):
    import json
    old = json.load(open(P_JSON))
    cfg = dict(variants=[list(v) for v in parse_variants(a.variants)], seeds=a.seeds, ms=a.ms, limit=a.limit,
               eln_subsets=sorted(parse_letters(a.eln_subsets) if a.eln_subsets else []))
    was = dict(variants=old.get("variants"), seeds=old.get("seeds"), ms=old.get("ms"), limit=old.get("limit", 0),
               eln_subsets=sorted(old.get("eln_subsets") or {}))
    if was != cfg:                      # the stem does not name the variants: never skip over a different run
        raise SystemExit(f"--skip-existing: {P_JSON} was made by another configuration ({was} vs {cfg}); use --tag or another --out-dir")
    st = str(old.get("check", {}).get("status", ""))
    print("exists, skipped:", P_ROWS, "| earlier check:", st)
    sys.exit(3 if a.strict and st.startswith("DIFFERS") else 0)   # a retry must not turn a failed check into a pass
TMP = {p: _edge.safe_out(p)[0] for p in (P_ROWS, P_OV, P_NPZ)}   # refuses experiments/results/ before any simulation

# ---- one raw load; groups and drives from its neuron table (the same table for every variant) ----
raw = connectome.load(dataset=a.dataset, signs="shiu", eln_scale=1.0, unclear_ln="excitatory")
print("raw:", raw, flush=True)
s, n = raw.select, raw.neurons
PN = s(cell_class="^ALPN$"); LN = s(cell_class="^ALLN$"); KC = s(cell_class="^Kenyon_Cell$"); MBON = s(cell_class="^MBON$")
PAM = s(cell_class="^DAN$", cell_type="^PAM"); PPL1 = s(cell_class="^DAN$", cell_type="^PPL1")
DNaL = s(cell_type=r"^DNa0[12]$", side="^left$"); DNaR = s(cell_type=r"^DNa0[12]$", side="^right$"); DN = s(super_class="^descending$")
glom = n.cell_type.fillna("").iloc[PN].str.extract(r"^([A-Z]+\d*[a-z]*)_")[0].fillna("multi").to_numpy()
ORN_GLOMS = sorted(set(n.cell_type.dropna().astype(str).str.extract(r"^ORN_(.+)$")[0].dropna()))
_pn_g = set(glom) - {"multi"}
# ORN glomerulus -> its PN group under odor_code.py's name pattern (ORN_VM6l/m/v -> VM6_adPN); None if no PN group
PN_OF = {g: g if g in _pn_g else (re.sub(r"[a-z]+$", "", g) if re.sub(r"[a-z]+$", "", g) in _pn_g else None) for g in ORN_GLOMS}
PN_ORN = sorted({v for v in PN_OF.values() if v})   # PN groups that receive ORNs
print(f"[glomeruli] {len(ORN_GLOMS)} ORN types -> {len(PN_ORN)} PN groups; no PN group: "
      f"{[g for g, v in PN_OF.items() if not v]}; mapped: { {g: v for g, v in PN_OF.items() if v and v != g} }", flush=True)
IDS = dict(kc_root_ids=raw.root_ids[KC].copy(), pn_root_ids=raw.root_ids[PN].copy(), pn_glom=glom.astype(str))


def lim(d):
    return dict(list(d.items())[:a.limit]) if a.limit > 0 else d


ODOR_SETS = {}   # set -> odour -> (per-hz (idx, rate), cognate glomerulus or None, driven glomeruli)
flat = lambda idx: {hz: (idx, np.full(len(idx), hz, np.float32)) for hz in HZ}
if "test10" in SETS:
    O = {g: s(cell_type=rf"^ORN_{g}$") for g in TEST10}
    O["food blend (DM1+DM2+DM4+VA2+VM2)"] = s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$")
    O = {k: v for k, v in O.items() if len(v)}
    ODOR_SETS["test10"] = lim({k: (flat(v), k.split(" ")[0], list(FOOD) if k.startswith("food") else [k]) for k, v in O.items()})
if "glomeruli" in SETS:
    ODOR_SETS["glomeruli"] = lim({g: (flat(s(cell_type=rf"^ORN_{g}$")), PN_OF[g], [PN_OF[g]] if PN_OF[g] else []) for g in ORN_GLOMS})
if "library" in SETS:
    enc = SensoryEncoder(raw, verbose=False)
    L = {}
    for cls, prof in ODOR_LIBRARY.items():
        drv = {hz: enc.odor(cls, r_max=hz) for hz in HZ}
        if not len(drv[HZ[0]][0]):
            continue
        top = [g for g, w in prof.items() if w == max(prof.values())]
        L[cls] = (drv, PN_OF.get(top[0]) if len(top) == 1 else None,
                  list(dict.fromkeys(PN_OF[g] for g in prof if len(enc.groups[f"glom_{g}"]) and PN_OF.get(g))))
    ODOR_SETS["library"] = lim(L)
    del enc
for k, v in ODOR_SETS.items():
    print(f"[odors] {k}: {len(v)} odours: " + ", ".join(f"{o}({len(d[HZ[0]][0])})" for o, (d, _, _) in v.items()), flush=True)


def options(signs, eln):
    """What connectome.load(dataset, signs=signs, eln_scale=eln) returns, without reloading."""
    return connectome.apply_model_options(dataclasses.replace(raw, W=raw.W.copy()), signs, eln, UNCLEAR)


def cosine(x, y):
    nx, ny = float(np.linalg.norm(x)), float(np.linalg.norm(y))
    return float(np.dot(x, y) / (nx * ny)) if nx > 0 and ny > 0 else np.nan


def nanmean(v):
    v = np.asarray(v, float)
    return float(np.nanmean(v)) if np.isfinite(v).any() else np.nan


rows, ov_rows, keys, kc_bits, pn_mat = [], [], [], [], []


def overlap(vname, hz, sname, names, codes, pnv, glv, kca):
    live = {x: float(np.mean(kca[x])) >= a.live_min for x in names}
    out = []
    for i, x in enumerate(names):
        for y in names[i:]:
            jac, jz, cos, gcos = [], [], [], []
            for sx in range(a.seeds):
                for sy in range(a.seeds):
                    if x == y and sx == sy:
                        continue
                    A, B = codes[(x, sx)], codes[(y, sy)]
                    jz.append((A & B).sum() / max((A | B).sum(), 1))            # odor_code.py's score (empty/empty = 0)
                    u = (A | B).sum(); jac.append((A & B).sum() / u if u else np.nan)
                    cos.append(cosine(pnv[(x, sx)], pnv[(y, sy)])); gcos.append(cosine(glv[(x, sx)], glv[(y, sy)]))
            out.append(dict(variant=vname, hz=hz, odor_set=sname, kind="pair", scope="", odor_a=x, odor_b=y, same_odor=(x == y),
                            live_a=live[x], live_b=live[y], live=live[x] and live[y], n_seed_pairs=len(jz),
                            n_empty_pairs=int(np.isnan(np.asarray(jac, float)).sum()), jaccard=nanmean(jac),
                            jaccard_zero=float(np.mean(jz)) if jz else np.nan, pn_cosine=nanmean(cos), pn_glom_cosine=nanmean(gcos)))
    d = pd.DataFrame(out)
    summ = {}
    for same in (True, False):
        for scope in ("all", "live"):
            m = (d.same_odor == same) & (d.live if scope == "live" else True)
            dd = d[m]
            summ[(same, scope)] = r = dict(variant=vname, hz=hz, odor_set=sname, kind="summary", scope=scope, odor_a="", odor_b="",
                                           same_odor=same, n_pairs=int(len(dd)), n_live_odors=int(sum(live.values())), n_odors=len(names),
                                           jaccard=nanmean(dd.jaccard), jaccard_zero=nanmean(dd.jaccard_zero),
                                           pn_cosine=nanmean(dd.pn_cosine), pn_glom_cosine=nanmean(dd.pn_glom_cosine))
            out.append(r)
    f = lambda v: "  nan" if not np.isfinite(v) else f"{v:5.2f}"
    print(f"  [{vname} {hz:g}Hz {sname}] live {sum(live.values())}/{len(names)} | KC Jaccard within all {f(summ[(True, 'all')]['jaccard'])} "
          f"live {f(summ[(True, 'live')]['jaccard'])}; between all {f(summ[(False, 'all')]['jaccard'])} live {f(summ[(False, 'live')]['jaccard'])} "
          f"(odor_code.py score {f(summ[(False, 'all')]['jaccard_zero'])}) | PN cosine between {f(summ[(False, 'all')]['pn_cosine'])} "
          f"within {f(summ[(True, 'all')]['pn_cosine'])}", flush=True)
    return out


def run_model(vname, signs, eln, subset, cx):
    print(cx, flush=True)
    sign = np.sign(np.asarray(cx.W.sum(axis=1)).ravel())
    eLN, iLN = LN[sign[LN] > 0], LN[sign[LN] < 0]
    sim = make_sim(cx)
    for hz in HZ:
        for sname, odors in ODOR_SETS.items():
            codes, pnv, glv, kca = {}, {}, {}, {}
            for oname, (drv, cog, gl) in odors.items():
                idx, rate = drv[hz]
                for seed in range(a.seeds):
                    sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
                    t0 = time.perf_counter(); c, _ = sim.run(a.ms); wall = time.perf_counter() - t0
                    r = c / (a.ms / 1000.0); pn = pd.Series(r[PN]).groupby(glom).mean()
                    kc = r[KC]
                    po = pn[pn.index.isin(PN_ORN)]
                    pd_ = pn.reindex(gl).dropna()
                    row = dict(variant=vname, signs=signs, eln_scale=eln, odor=oname, seed=seed, n_orn=len(idx), wall_s=round(wall, 2),
                               pn_cognate_hz=float(pn.get(cog, np.nan)) if cog else np.nan, pn_mean_hz=float(r[PN].mean()), pn_active=float((r[PN] > 0).mean()),
                               glomeruli_over_10hz=float((pn > 10).mean()), n_glomeruli=int(len(pn)),
                               eln_hz=float(r[eLN].mean()) if len(eLN) else np.nan, iln_hz=float(r[iLN].mean()) if len(iLN) else np.nan,
                               kc_active=float((kc > 0).mean()), kc_hz=float(kc.mean()), kc_hz_of_active=float(kc[kc > 0].mean()) if (kc > 0).any() else 0.0,
                               mbon_hz=float(r[MBON].mean()), pam_hz=float(r[PAM].mean()), ppl1_hz=float(r[PPL1].mean()),
                               dna_l_hz=float(r[DNaL].mean()), dna_r_hz=float(r[DNaR].mean()), dn_all_hz=float(r[DN].mean()),
                               active_frac=float((c > 0).mean()), total_spikes=int(c.sum()),
                               # edge columns
                               hz=hz, odor_set=sname, model=cx.variant, eln_subset=subset, ms=a.ms,
                               pn_driven_hz=float(pd_.mean()) if len(pd_) else np.nan,
                               glomeruli_over_10hz_orn=float((po > 10).mean()) if len(po) else np.nan, n_glomeruli_orn=int(len(po)),
                               eln_fixed_hz=float(r[ELN].mean()) if len(ELN) else np.nan,
                               **{f"eln_{k}_hz": float(r[v].mean()) if len(v) else np.nan for k, v in ECLS.items()})
                    rows.append(row)
                    codes[(oname, seed)] = kc > 0; pnv[(oname, seed)] = r[PN]; glv[(oname, seed)] = pn.to_numpy()
                    kca.setdefault(oname, []).append(row["kc_active"])
                    keys.append(f"{vname}|{hz:g}|{sname}|{oname}|{seed}"); kc_bits.append(np.packbits(kc > 0)); pn_mat.append(r[PN].astype(np.float32))
                    print(f"[{vname:14s} {hz:4g}Hz {SHORT[sname]}] {oname[:12]:12s} s{seed} | PN cognate {row['pn_cognate_hz']:5.0f} Hz, "
                          f"glomeruli>10Hz {row['glomeruli_over_10hz']*100:3.0f}% (ORN-only {row['glomeruli_over_10hz_orn']*100:3.0f}%) "
                          f"| eLN ach/mod/gg {row['eln_ach_hz']:5.1f}/{row['eln_mod_hz']:5.1f}/{row['eln_gg_hz']:5.1f} "
                          f"| KC {row['kc_active']*100:5.1f}% | MBON {row['mbon_hz']:5.1f} PAM {row['pam_hz']:4.1f} PPL1 {row['ppl1_hz']:5.1f} "
                          f"| DNa L/R {row['dna_l_hz']:4.1f}/{row['dna_r_hz']:4.1f} | brain {row['active_frac']*100:4.1f}% ({wall:.1f}s)", flush=True)
            ov_rows.extend(overlap(vname, hz, sname, list(odors), codes, pnv, glv, kca))
    del sim; gc.collect()


# ---- the fixed eLN set and its transmitter classes (ALLN with positive row sign, known signs, eLN x1) ----
# computed before any simulation, so a failed (a) assertion stops the run before hours of plain variants
sub_info = {}
base = options("known", 1.0)
row_sign = np.sign(np.asarray(base.W.sum(axis=1)).ravel())
ELN = LN[row_sign[LN] > 0]
nt = n.top_nt.fillna("").astype(str).str.lower().to_numpy() if "top_nt" in n.columns else np.full(len(n), "", object)
ent = nt[ELN]
ecls = np.where(ent == "acetylcholine", "ach", np.where(np.isin(ent, MOD), "mod", np.where(np.isin(ent, GG), "gg", "other")))
ECLS = {k: ELN[ecls == k] for k in ("ach", "mod", "gg", "other")}
sub_info["eln_counts"] = {k: int(len(v)) for k, v in ECLS.items()}
sub_info["eln_counts_by_nt"] = {k: int(v) for k, v in pd.Series(ent).replace("", "(none)").value_counts().items()}
print(f"[eln-subsets] {len(ELN)} eLNs (ALLN with positive row sign, known signs, eLN x1): {sub_info['eln_counts']}; "
      f"by top_nt {sub_info['eln_counts_by_nt']}", flush=True)


def subset_cx(k):
    scale = np.ones(base.n, np.float32)
    for c, f in SUBSETS[k][1].items():
        scale[ECLS[c]] *= np.float32(f)
    W = sp.diags(scale, format="csr", dtype=np.float32) @ base.W
    W = sp.csr_matrix(W, dtype=np.float32); W.sort_indices()
    return dataclasses.replace(base, W=W, variant=base.variant + f"+elnsub-{k}")


if "a" in SUBS:
    ref, Wa = options("known", 0.25), subset_cx("a").W
    same = (Wa.shape == ref.W.shape and Wa.nnz == ref.W.nnz and np.array_equal(Wa.indptr, ref.W.indptr)
            and np.array_equal(Wa.indices, ref.W.indices) and np.array_equal(Wa.data, ref.W.data))
    if not same or ref.n_eln != len(ELN):
        raise SystemExit(f"subset (a) differs from apply_model_options(known, 0.25): W same {same}, n_eln {ref.n_eln} vs {len(ELN)}")
    print(f"[eln-subsets] (a) W == apply_model_options(known, eln 0.25): identical ({Wa.nnz} connections, {ref.n_eln} eLNs)", flush=True)
    sub_info["a_equals_apply_model_options"] = True
    del ref, Wa
if not SUBS:
    del base
gc.collect()

# ---- plain variants (odor_code.py's models) ----
for vname, signs, eln in VARIANTS:
    cx = options(signs, eln)
    run_model(vname, signs, eln, "", cx)
    del cx; gc.collect()
raw.W = None; gc.collect()          # every later model is built from base (raw stays referenced by raw.select)

# ---- eLN subsets ----
for k in SUBS:
    cx = subset_cx(k)
    run_model(f"elnsub-{k}", "known", 0.25 if k == "a" else np.nan, SUBSETS[k][0], cx)
    del cx; gc.collect()
if SUBS:
    del base
gc.collect()

# ---- write ----
pd.DataFrame(rows).to_csv(TMP[P_ROWS], index=False); _edge.finish(TMP[P_ROWS], P_ROWS)
ov = pd.DataFrame(ov_rows)
for c in ("n_seed_pairs", "n_empty_pairs", "n_pairs", "n_live_odors", "n_odors"):
    ov[c] = ov[c].astype("Int64")                    # pair and summary rows share the table: keep counts integer
ov.to_csv(TMP[P_OV], index=False); _edge.finish(TMP[P_OV], P_OV)
np.savez_compressed(TMP[P_NPZ], keys=np.array(keys), kc_active_bits=np.stack(kc_bits), n_kc=len(KC),
                    pn_hz=np.stack(pn_mat), **IDS)
_edge.finish(TMP[P_NPZ], P_NPZ)


# ---- check against the paper's odor_code file (read only) ----
def check():
    if a.check_against == "none":
        return {"status": "skipped (--check-against none)"}
    names = [v for v, _, _ in VARIANTS]
    if not (100.0 in HZ and "test10" in SETS and a.ms == 500 and names):
        return {"status": "skipped (needs a --variants variant, --hz 100, --odors test10, --ms 500)"}
    ref_p = os.path.join(_edge.RESULTS, f"odor_code_{a.dataset}.csv") if a.check_against == "auto" else a.check_against
    if not os.path.exists(ref_p):
        return {"status": f"skipped (no {ref_p})"}
    ref, mine = pd.read_csv(ref_p), pd.read_csv(P_ROWS)
    mine = mine[(mine.odor_set == "test10") & (mine.hz == 100.0) & mine.variant.isin(names)]
    m = mine.merge(ref, on=["variant", "odor", "seed"], suffixes=("", "_ref"))
    if not len(m):
        return {"status": f"skipped (no shared rows; reference variants {sorted(ref.variant.unique())})"}
    cols = [c for c in ref.columns if c not in ("variant", "odor", "seed", "wall_s")]
    ndiff, maxd, worst = 0, 0.0, {}
    for c in cols:
        x, y = m[c], m[c + "_ref"]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            xa, ya = x.to_numpy(float), y.to_numpy(float)
            bad = ~((xa == ya) | (np.isnan(xa) & np.isnan(ya)))
            if bad.any():
                maxd = max(maxd, float(np.nanmax(np.abs(xa - ya)[bad])))
        else:
            bad = (x.astype(str) != y.astype(str)).to_numpy()
        if bad.any():
            worst[c] = int(bad.sum())
        ndiff += int(bad.sum())
    # every reference row this run should have made (all odours unless --limit), so a lost odour cannot pass silently
    exp = ref[ref.variant.isin(m.variant.unique()) & (ref.seed < a.seeds)]
    missing = 0 if a.limit > 0 else int(len(exp) - len(m))
    res = dict(reference=ref_p, reference_mtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(ref_p))),
               rows=int(len(m)), columns=len(cols), variants=sorted(m.variant.unique()),
               seeds=sorted(int(v) for v in m.seed.unique()), odors=int(m.odor.nunique()), cells_differ=ndiff,
               max_abs_diff=maxd, columns_differ=worst, rows_missing=missing)
    ref_ov = os.path.splitext(ref_p)[0] + "_overlap.csv"
    n_ref_seeds = int(ref[ref.variant.isin(names)].seed.nunique())
    if a.seeds == n_ref_seeds and os.path.exists(ref_ov):
        ro, mo = pd.read_csv(ref_ov), pd.read_csv(P_OV)
        mo = mo[(mo.kind == "pair") & (mo.odor_set == "test10") & (mo.hz == 100.0) & mo.variant.isin(names)]
        mm = mo.merge(ro, on=["variant", "odor_a", "odor_b"], suffixes=("", "_ref"))
        xa, ya = mm.jaccard_zero.to_numpy(float), mm.jaccard_ref.to_numpy(float)
        bad = ~((xa == ya) | (np.isnan(xa) & np.isnan(ya)))
        n_exp = int(ro.variant.isin(m.variant.unique()).sum())
        res.update(overlap_pairs=int(len(mm)), overlap_differ=int(bad.sum()) + (0 if a.limit > 0 else max(n_exp - int(len(mm)), 0)),
                   overlap_max_abs_diff=float(np.nanmax(np.abs(xa - ya)[bad])) if bad.any() else 0.0)
    else:
        res["overlap"] = f"skipped (--seeds {a.seeds} vs {n_ref_seeds} in the reference)"
    res["status"] = "IDENTICAL" if ndiff == 0 and missing == 0 and res.get("overlap_differ", 0) == 0 else "DIFFERS"
    return res


try:
    chk = check()
except Exception as e:                  # the outputs are already written: record the failure, never lose the sidecar
    chk = {"status": f"DIFFERS (check failed: {type(e).__name__}: {e})"}
print(f"CHECK vs {os.path.basename(chk.get('reference', 'odor_code'))}: {chk['status']}"
      + (f" ({chk['rows']} rows x {chk['columns']} columns, variants {','.join(chk['variants'])}, seeds {chk['seeds']}, "
         f"{chk['odors']} odours; {chk['cells_differ']} cells differ, max |diff| {chk['max_abs_diff']:g}"
         + (f"; overlap {chk['overlap_pairs']} pairs, {chk['overlap_differ']} differ" if "overlap_pairs" in chk else f"; overlap {chk.get('overlap')}")
         + (f"; {chk['rows_missing']} reference rows missing" if chk["rows_missing"] else "")
         + (f"; columns {chk['columns_differ']}" if chk["columns_differ"] else "") + ")" if "rows" in chk else ""), flush=True)
side = _edge.sidecar(P_ROWS, dict(variants=VARIANTS, eln_subsets={k: SUBSETS[k][0] for k in SUBS}, hz=HZ, odor_sets=SETS,
                                  odors={k: list(v) for k, v in ODOR_SETS.items()}, seeds=a.seeds, ms=a.ms, limit=a.limit, live_min=a.live_min,
                                  unclear_ln=UNCLEAR, subsets=sub_info, check=chk, outputs=[P_ROWS, P_OV, P_NPZ]))
print("wrote", P_ROWS, P_OV, P_NPZ, side, sep="\n  ")
if a.strict and chk["status"].startswith("DIFFERS"):
    sys.exit(3)
