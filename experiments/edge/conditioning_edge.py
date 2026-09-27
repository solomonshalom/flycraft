#!/usr/bin/env python3
"""Edge cases of the in-silico conditioning (design_plan.md 2.3, RESEARCH_NOTES 23): a copy of experiments/conditioning.py
with contingency controls, the learning constants exposed, and the fly's own taste channels as the US.

The simulation is conditioning.py's, call for call: the same pre-test, the same training loop (50-ms ticks, plasticity ON,
tau_rec 0), the same post-test and the same CSV schema. At defaults (--protocol forward) it must reproduce the paper's file
to the digit (same seed, same NUMBA_NUM_THREADS); --check-against tests that and writes <out>.check.txt (exit 0 either way).

Protocols, phases per cycle (T = --train-s, R = --rest-s, G = --gap-s; 'US' = the reward/punishment DANs at --us-hz for
--us dan, or the --wiring-us group at 100 Hz for --us wiring):
  forward     [CS+ & US T | rest R | CS- T | rest R]                       (conditioning.py)
  backward    [US T | CS+ T | rest R | CS- T | rest R]
  unpaired    [CS+ T | rest R | US T | rest R | CS- T | rest R]
  us-only     [US T | rest R | CS- T | rest R]
  trace       [CS+ T | gap G (no drive) | US T | rest R | CS- T | rest R]
  extinction  forward x --cycles, a mid-test (mid_* columns), then --ext-cycles x [CS+ T | rest R | CS- T | rest R]
--wiring-us: sugar = gustatory 'sugar/water' (conditioning.py's SUGAR), bitter = gustatory '^bitter$', touch = '^BM_',
labellar = gustatory 'sugar/water|labellar bristle'. With --us wiring, --valence only picks the compartment the summary
calls taught (it adds no US); a non-default one is still tagged ('us-wiring[-<group>]-punish'), so a parser that takes the
taught compartment from the name ('punish' in it, as paper_numbers.py does) reads the right one.

Output (all under --out-dir, never experiments/results/): conditioning_<tag>.csv, conditioning_<tag>_compartments.csv,
conditioning_<tag>.json (sidecar: every argument, the phase list, and per phase the mean DAN / PAM / PPL1 rate and the
synapse-weighted DAN rate onto the reward and punishment compartments over the whole phase) [, conditioning_<tag>.check.txt].
The tag is conditioning.py's plus every non-default argument, placed before _seed<n> so seeds of one condition group
together. --skip-existing exits 0 without simulating when this run's CSVs, sidecar (written last) and, with
--check-against, its check file already exist (so a queue step that loops over runs can be retried cheaply).

  python experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --us dan --valence reward \\
      --csp vinegar --csm ester --seed 0 --out-dir experiments/results_edge/cond --check-against \\
      experiments/results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_vinegar-vs-ester_seed0.csv
  python experiments/edge/conditioning_edge.py ... --protocol backward|unpaired|us-only|trace --gap-s 1|extinction --ext-cycles 3
  python experiments/edge/conditioning_edge.py ... --us wiring --wiring-us bitter|touch|labellar --valence punish
  python experiments/edge/conditioning_edge.py ... --w-min 0 --tau-elig 3
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge                                                              # puts experiments/ and brain/ on the path
from common import make_sim
import numpy as np, pandas as pd
from flybrain import connectome
from flybrain.plasticity import MBPlasticity, PlasticityConfig, REWARD_MBONS, PUNISH_MBONS
from flybrain.senses import SensoryEncoder

PROTOCOLS = ("forward", "backward", "unpaired", "us-only", "trace", "extinction")
ap = argparse.ArgumentParser()
ap.add_argument("--out-dir", required=True, help="output directory (refused if inside experiments/results/)")
ap.add_argument("--protocol", choices=PROTOCOLS, default="forward")
ap.add_argument("--gap-s", type=float, default=1.0, help="trace: CS+ offset to US onset (no drive)")
ap.add_argument("--ext-cycles", type=int, default=3, help="extinction: cycles of CS+ alone | CS- alone after the mid-test")
ap.add_argument("--w-min", type=float, default=0.1, help="weight floor as a fraction of w0 (PlasticityConfig.w_min)")
ap.add_argument("--tau-elig", type=float, default=1.0, help="KC eligibility trace, s (PlasticityConfig.tau_elig; 0 = none)")
ap.add_argument("--wiring-us", choices=["sugar", "bitter", "touch", "labellar"], default="sugar", help="the US group for --us wiring (100 Hz)")
ap.add_argument("--check-against", default=None, help="reference conditioning CSV: compare every cell (and its _compartments.csv)")
ap.add_argument("--skip-existing", action="store_true", help="exit 0 without simulating if this run's outputs are all there")
# conditioning.py's arguments, same defaults
ap.add_argument("--cycles", type=int, default=3)
ap.add_argument("--train-s", type=float, default=10)
ap.add_argument("--rest-s", type=float, default=5, help="rest between presentations (the KC eligibility trace, tau 1 s, has decayed by then)")
ap.add_argument("--test-s", type=float, default=1.0)
ap.add_argument("--noise-hz", type=float, default=0.0)
ap.add_argument("--hz", type=float, default=150, help="ORN rate for the strongest glomerulus of an odor class (150 = the body's maximum, R_OLF)")
ap.add_argument("--eta", type=float, default=0.3)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--signs", default=None, help="shiu | known (default: env FLYBRAIN_SIGNS or shiu)")
ap.add_argument("--eln", type=float, default=None, help="eLN output scale (default: env FLYBRAIN_ELN or 1)")
ap.add_argument("--csp", default="vinegar"); ap.add_argument("--csm", default="ester")
ap.add_argument("--us", choices=["wiring", "dan"], default="wiring")
ap.add_argument("--valence", choices=["reward", "punish"], default="reward")
ap.add_argument("--us-hz", type=float, default=50)
ap.add_argument("--tau-dan", type=float, default=0.0, help="phasic teaching signal: DAN rate minus its running mean over this many seconds (0 = tonic, default)")
ap.add_argument("--tag", default="")
a = ap.parse_args()
nd = lambda k: getattr(a, k) != ap.get_default(k)                         # non-default argument
STEP = 50.0                                                               # ms per plasticity tick (conditioning.py)


def ticks(secs, what):
    n = int(round(secs * 1000 / STEP))
    if secs < 0 or abs(n * STEP - secs * 1000) > 1e-6:
        raise SystemExit(f"--{what} {secs:g} s is not a non-negative multiple of the {STEP:g}-ms plasticity tick")
    return n


for k in ("train_s", "rest_s", "gap_s"):
    ticks(getattr(a, k), k.replace("_", "-"))
if a.test_s <= 0 or a.cycles < 0 or a.ext_cycles < 0:
    raise SystemExit("--test-s must be > 0, --cycles and --ext-cycles >= 0")
if a.check_against and not os.path.isfile(a.check_against):              # fail now, not after the whole run
    raise SystemExit(f"--check-against: no such file {a.check_against}")
_edge.safe_out(os.path.join(a.out_dir, "conditioning_probe.csv"))       # fail fast on a forbidden --out-dir (and create it)

cx = connectome.load(dataset=a.dataset, signs=a.signs, eln_scale=a.eln); s = cx.select; print(cx)

# ---- tag: conditioning.py's, plus every non-default argument before _seed<n> ----
cond = []
if a.protocol != "forward":
    cond.append(a.protocol + (f"-gap{a.gap_s:g}s" if a.protocol == "trace" else "") + (f"-ext{a.ext_cycles}" if a.protocol == "extinction" else ""))
for k, fmt in (("cycles", "cyc{}"), ("train_s", "train{:g}s"), ("rest_s", "rest{:g}s"), ("test_s", "test{:g}s"), ("hz", "orn{:g}hz"),
               ("noise_hz", "noise{:g}hz"), ("eta", "eta{:g}"), ("w_min", "wmin{:g}"), ("tau_elig", "elig{:g}s")):
    if nd(k):
        cond.append(fmt.format(getattr(a, k)))
tag = (f"{a.dataset}_{cx.variant}_us-{a.us}" + (f"-{a.valence}" if a.us == "dan" else "") + (f"-{a.us_hz:g}hz" if a.us == "dan" and a.us_hz != 50 else "")
       + (f"-{a.wiring_us}" if a.us == "wiring" and a.wiring_us != "sugar" else "") + ("-punish" if a.us == "wiring" and a.valence == "punish" else "")
       + (f"-phasic{a.tau_dan:g}" if a.tau_dan > 0 else "") + f"_{a.csp}-vs-{a.csm}" + "".join(f"_{c}" for c in cond)
       + f"_seed{a.seed}" + (f"_{a.tag}" if a.tag else ""))
at_defaults = not cond and (a.us == "dan" or a.wiring_us == "sugar")    # the simulation is conditioning.py's (a --tag changes no number)
out = os.path.join(a.out_dir, f"conditioning_{tag}.csv")
out_comp = os.path.join(a.out_dir, f"conditioning_{tag}_compartments.csv")
out_json = os.path.splitext(out)[0] + ".json"
out_chk = os.path.splitext(out)[0] + ".check.txt"
print(f"tag: {tag}")
if a.skip_existing and all(os.path.exists(p) for p in [out, out_comp, out_json] + ([out_chk] if a.check_against else [])):
    print(f"skip-existing: {out} and its companions exist; nothing run")
    raise SystemExit(0)

senses = SensoryEncoder(cx, verbose=False)
WIRING_US = {"sugar": lambda: s(cell_class="^gustatory$", cell_sub_class="sugar/water"),
             "bitter": lambda: s(cell_class="^gustatory$", cell_sub_class="^bitter$"),
             "touch": lambda: s(cell_type=r"^BM_"),
             "labellar": lambda: s(cell_class="^gustatory$", cell_sub_class="sugar/water|labellar bristle")}
WUS = WIRING_US[a.wiring_us]()
print(f"wiring US group '{a.wiring_us}': {len(WUS)} neurons" + ("" if a.us == "wiring" else " (unused: --us dan)"))
if a.us == "wiring" and not len(WUS):
    raise SystemExit(f"--wiring-us {a.wiring_us} selects no neuron in {a.dataset}")
OUT = {"DNa L": s(cell_type=r"^DNa0[12]$", side="^left$"), "DNa R": s(cell_type=r"^DNa0[12]$", side="^right$"),
       "DNp09": s(cell_type=r"^DNp09$"), "MDN": s(cell_type=r"^MDN$"), "DN all": s(super_class="^descending$"),
       "feed MNs": s(any_of={"cell_sub_class": r"proboscis_motor_neuron|ingestion_motor_neuron|^pm$", "cell_type": r"^MN9$"}),
       "MBON": s(cell_class="^MBON$"), "PAM": s(cell_class="^DAN$", cell_type=r"^PAM"), "PPL1": s(cell_class="^DAN$", cell_type=r"^PPL1"),
       "KC": s(cell_class="^Kenyon_Cell$")}
sim = make_sim(cx, noise_hz=a.noise_hz, seed=a.seed)
pl = MBPlasticity(cx, sim, PlasticityConfig(eta=a.eta, tau_rec=0, us=a.us, us_hz=a.us_hz, tau_dan=a.tau_dan,
                                            w_min=a.w_min, tau_elig=a.tau_elig))
mbon_types = pl.mbon_type
OUT["MBON reward-comp"] = pl.mbon[np.isin(mbon_types, list(REWARD_MBONS))]
OUT["MBON punish-comp"] = pl.mbon[np.isin(mbon_types, list(PUNISH_MBONS))]
csp, csm = senses.odor(a.csp, r_max=a.hz), senses.odor(a.csm, r_max=a.hz)
us_desc = f"{a.wiring_us} group ({len(WUS)}) at 100 Hz" if a.us == "wiring" else f"{a.valence} DANs at {a.us_hz:g} Hz"
print(f"CS+ {a.csp}: {len(csp[0])} ORNs   CS- {a.csm}: {len(csm[0])} ORNs   US: {a.us} ({us_desc})   protocol: {a.protocol}   "
      f"w_min {a.w_min:g}  tau_elig {a.tau_elig:g} s  eta {a.eta:g}")


def cat(*parts):
    parts = [p for p in parts if len(p[0])]
    if not parts:
        return np.zeros(0, np.int64), np.zeros(0, np.float32)
    return np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts])


def test(label):
    res = {}
    for name, cls in [("CS+", a.csp), ("CS-", a.csm)]:
        # bilateral presentation: MB / DN rates; left-antenna presentation: steering (approach index)
        sim.seed(a.seed); sim.reset(); sim.set_drive(*senses.odor(cls, r_max=a.hz))
        counts, _ = sim.run(a.test_s * 1000)
        r = {k: counts[v].sum() / max(len(v), 1) / a.test_s for k, v in OUT.items()}
        r["MBON by type"] = pd.Series(counts[pl.mbon] / a.test_s).groupby(mbon_types).mean()
        drv = pl.drive_by_mbon(counts, a.test_s)                       # graded readout: KC->MBON synaptic drive
        r["drive by type"] = pd.Series(drv).groupby(mbon_types).sum()
        r["drive reward-comp"] = float(drv[np.isin(mbon_types, list(REWARD_MBONS))].sum())
        r["drive punish-comp"] = float(drv[np.isin(mbon_types, list(PUNISH_MBONS))].sum())
        r["drive all"] = float(drv.sum())
        r["KC active"] = float((counts[OUT["KC"]] > 0).mean())
        sim.seed(a.seed + 100); sim.reset(); sim.set_drive(*senses.odor(cls, side="L", r_max=a.hz))
        cl, _ = sim.run(a.test_s * 1000)
        r["lat DNa L"] = cl[OUT["DNa L"]].sum() / len(OUT["DNa L"]) / a.test_s
        r["lat DNa R"] = cl[OUT["DNa R"]].sum() / len(OUT["DNa R"]) / a.test_s
        r["approach"] = r["lat DNa L"] - r["lat DNa R"]
        res[name] = r
        print(f"  [{label}] {name}: KC {r['KC active']*100:4.1f}% | MBON {r['MBON']:5.1f} Hz (reward-comp {r['MBON reward-comp']:5.1f}, punish-comp {r['MBON punish-comp']:5.1f}) "
              f"| KC->MBON drive reward-comp {r['drive reward-comp']/1000:6.1f}k punish-comp {r['drive punish-comp']/1000:6.1f}k all {r['drive all']/1000:6.1f}k "
              f"| PAM {r['PAM']:4.1f} PPL1 {r['PPL1']:5.1f} | DNa L/R {r['DNa L']:4.1f}/{r['DNa R']:4.1f} DN {r['DN all']:4.1f} feed {r['feed MNs']:4.1f} "
              f"| left-odor DNa L-R {r['approach']:+5.1f}", flush=True)
    return res


# ---- phases: (label, drive kind, seconds) ----
T, R, G = a.train_s, a.rest_s, a.gap_s
FORWARD = [("CS+ & US", "csp+us", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)]
CYCLE = {"forward": FORWARD, "extinction": FORWARD,
         "backward": [("US alone", "us", T), ("CS+ alone", "csp", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)],
         "unpaired": [("CS+ alone", "csp", T), ("rest", "none", R), ("US alone", "us", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)],
         "us-only": [("US alone", "us", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)],
         "trace": [("CS+ alone", "csp", T), ("gap", "none", G), ("US alone", "us", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)]}[a.protocol]
EXT = [("CS+ alone", "csp", T), ("rest", "none", R), ("CS- alone", "csm", T), ("rest", "none", R)]
NAMES = {"csp+us": "CS+ + {us}", "us": "{us}", "csp": "CS+ alone", "csm": "CS- alone", "none": "{label}"}
us_name = f"{a.wiring_us} GRNs" if a.us == "wiring" and a.wiring_us != "touch" else ("touch (BM)" if a.us == "wiring" else f"{a.valence} DANs")
describe = lambda ph: " | ".join(f"{NAMES[k].format(us=us_name, label=lb)} {sec:g}s" for lb, k, sec in ph)


def us_on():
    if a.us == "wiring":
        return WUS, np.full(len(WUS), 100.0, np.float32)
    return pl.us_drive(reward=float(a.valence == "reward"), punish=float(a.valence == "punish"))


PHASE_STATS = []                                                           # per phase, whole-phase means (sidecar)
hz_of = lambda tot, idx, secs: float(tot[idx].sum() / max(len(idx), 1) / secs)


def train(phases, n_cycles, label, t0):
    for c in range(n_cycles):
        for phase, kind, secs in phases:
            if kind == "csp+us":
                drive = cat(csp, us_on())
            elif kind == "us":
                drive = cat(us_on())
            else:
                pl.us_drive(0, 0)
                drive = {"csp": csp, "csm": csm}.get(kind, (np.zeros(0, np.int64), np.zeros(0, np.float32)))
            sim.set_drive(*drive); stats = None
            tot = np.zeros(sim.N, np.int64)                                # spike counts over the phase (read only)
            for _ in range(ticks(secs, "phase")):
                counts, _ = sim.run(STEP)
                stats = pl.update(counts, STEP / 1000)
                tot += counts
            if stats is not None:
                D = (tot[pl.dan] / secs) @ pl.A                            # synapse-weighted DAN rate onto each MBON (tonic)
                PHASE_STATS.append({"stage": label, "cycle": c + 1, "phase": phase, "kind": kind, "s": secs,
                                    "dan_hz": hz_of(tot, pl.dan, secs), "pam_hz": hz_of(tot, OUT["PAM"], secs), "ppl1_hz": hz_of(tot, OUT["PPL1"], secs),
                                    "us_reward_dan_hz": hz_of(tot, pl.reward_dan, secs), "us_punish_dan_hz": hz_of(tot, pl.punish_dan, secs),
                                    "dan_to_reward_comp_hz": float(D[pl.reward_cols].mean()) if len(pl.reward_cols) else float("nan"),
                                    "dan_to_punish_comp_hz": float(D[pl.punish_cols].mean()) if len(pl.punish_cols) else float("nan"),
                                    "kc_hz": hz_of(tot, pl.kc, secs), "w_frac": stats["kc_mbon_w_frac"],
                                    "w_frac_reward_comp": stats["w_frac_reward_comp"], "w_frac_punish_comp": stats["w_frac_punish_comp"]})
            if phase != "rest" and stats is not None:
                print(f"  {label} {c+1} {phase:10s} KC->MBON w {stats['kc_mbon_w_frac']:.3f} (reward-comp {stats['w_frac_reward_comp']:.3f}, punish-comp {stats['w_frac_punish_comp']:.3f})  "
                      f"DAN {stats['dan_hz']:.1f} Hz  KC {stats['kc_hz']:.1f} Hz, {stats['kc_active']*100:.1f}% active  ({time.time()-t0:.0f}s)", flush=True)


wall0 = time.time()
print("\n== pre-test (plasticity frozen)")
pre = test("pre")
w_pre = sim.data[pl.e_idx].copy()

print(f"\n== training ({a.protocol}): {a.cycles} cycles x [{describe(CYCLE)}], plasticity ON")
t0 = time.time()
train(CYCLE, a.cycles, "cycle", t0)
mid = w_mid = None
if a.protocol == "extinction":
    w_mid = sim.data[pl.e_idx].copy()
    print("\n== mid-test (plasticity frozen)")
    mid = test("mid")
    print(f"\n== extinction: {a.ext_cycles} cycles x [{describe(EXT)}], plasticity ON")
    train(EXT, a.ext_cycles, "ext", t0)
w_post = sim.data[pl.e_idx].copy()
print("\n  whole-phase means over cycles (Hz): DAN all / PAM / PPL1 | synapse-weighted DAN rate onto reward / punishment compartments")
ps = pd.DataFrame(PHASE_STATS)
if len(ps):
    print(ps.groupby(["stage", "phase"], sort=False)[["dan_hz", "pam_hz", "ppl1_hz", "dan_to_reward_comp_hz", "dan_to_punish_comp_hz"]].mean().round(2).to_string())

print("\n== post-test (plasticity frozen)")
post = test("post")

print("\n== change (post - pre), CS+ vs CS-")
keys = ["MBON", "MBON reward-comp", "MBON punish-comp", "DNa L", "DNa R", "DNp09", "MDN", "DN all", "feed MNs", "approach"]
for k in keys:
    print(f"  {k:17s} CS+ {post['CS+'][k]-pre['CS+'][k]:+7.2f}   CS- {post['CS-'][k]-pre['CS-'][k]:+7.2f}")
print("  KC->MBON drive retained (post/pre):")
for k in ["drive reward-comp", "drive punish-comp", "drive all"]:
    fr = lambda cs: post[cs][k] / pre[cs][k] if pre[cs][k] > 0 else float('nan')
    print(f"  {k:17s} CS+ {fr('CS+'):7.3f}   CS- {fr('CS-'):7.3f}")
dd = (post["CS+"]["drive by type"] / pre["CS+"]["drive by type"].replace(0, np.nan)) - (post["CS-"]["drive by type"] / pre["CS-"]["drive by type"].replace(0, np.nan))
print("  per-compartment drive retained, CS+ minus CS- (negative = CS+ input to this MBON was depressed more):")
print(dd.dropna().sort_values().head(8).round(3).to_string())
d = (post["CS+"]["MBON by type"] - pre["CS+"]["MBON by type"]) - (post["CS-"]["MBON by type"] - pre["CS-"]["MBON by type"])
print("\n  MBON types with the largest CS+-specific change (Hz, differential):")
print(d.sort_values().head(6).round(1).to_string()); print(d.sort_values().tail(4).round(1).to_string())
frac = pd.Series(w_post / np.maximum(w_pre, 1e-9)).groupby(mbon_types[pl.post_col]).mean().sort_values()
print("\n  most-depressed MBON compartments (mean w/w0):"); print(frac.head(8).round(3).to_string())
disc = (post["CS+"]["MBON"] - post["CS-"]["MBON"]) - (pre["CS+"]["MBON"] - pre["CS-"]["MBON"])
disc_r = (post["CS+"]["MBON reward-comp"] - post["CS-"]["MBON reward-comp"]) - (pre["CS+"]["MBON reward-comp"] - pre["CS-"]["MBON reward-comp"])
dapp = (post["CS+"]["approach"] - post["CS-"]["approach"]) - (pre["CS+"]["approach"] - pre["CS-"]["approach"])
print(f"\nRESULT: CS+/CS- MBON discrimination change {disc:+.1f} Hz (reward-compartment MBONs {disc_r:+.1f} Hz); "
      f"approach index change (CS+ minus CS-) {dapp:+.1f} Hz; KC->MBON weights retained {float(w_post.sum()/w_pre.sum()):.3f}")


def lindex(res, comp):
    """paper_numbers.py's learning index: CS- minus CS+ taught-compartment drive retained (res / pre)."""
    ret = lambda cs: res[cs][comp] / pre[cs][comp] if pre[cs][comp] > 0 else float('nan')
    return ret("CS-") - ret("CS+"), ret("CS+"), ret("CS-")


taught = "drive punish-comp" if a.valence == "punish" else "drive reward-comp"
for lb, res in (("mid", mid), ("post", post)):
    if res is not None:
        li = {c: lindex(res, c) for c in ("drive reward-comp", "drive punish-comp")}
        print(f"LEARNING INDEX [{lb}] ({a.protocol}, taught = {taught.split()[1]}): {li[taught][0]:+.3f} (CS+ {li[taught][1]:.3f}, CS- {li[taught][2]:.3f}); "
              + "; ".join(f"{c.split()[1]} {v[0]:+.3f}" for c, v in li.items()))

# ---- outputs (conditioning.py's schema; extinction appends mid_* columns) ----
tab = {}
for ph, res in (("pre", pre), ("post", post)) + ((("mid", mid),) if mid is not None else ()):
    for cs in ("CS+", "CS-"):
        tab[f"{ph}_{cs}"] = {k: v for k, v in res[cs].items() if k not in ("MBON by type", "drive by type")}
df = pd.DataFrame(tab); df.loc["w_retained"] = float(w_post.sum() / w_pre.sum())
if w_mid is not None:
    df.loc["w_retained", ["mid_CS+", "mid_CS-"]] = float(w_mid.sum() / w_pre.sum())
tmp, out = _edge.safe_out(out); df.to_csv(tmp); _edge.finish(tmp, out)
tmp, out_comp = _edge.safe_out(out_comp)
if w_mid is None:
    frac.to_csv(tmp, header=["w_over_w0"])
else:
    fm = pd.Series(w_mid / np.maximum(w_pre, 1e-9)).groupby(mbon_types[pl.post_col]).mean()
    pd.DataFrame({"w_over_w0": frac, "w_over_w0_mid": fm.reindex(frac.index)}).to_csv(tmp)
_edge.finish(tmp, out_comp)
print("wrote", out)


def compare(new_path, ref_path):
    """Every shared cell exactly equal (round-trip parse), no reference row/column missing; plus byte identity."""
    new = pd.read_csv(new_path, index_col=0, float_precision="round_trip")
    ref = pd.read_csv(ref_path, index_col=0, float_precision="round_trip")
    rows = [r for r in ref.index if r in new.index]; cols = [c for c in ref.columns if c in new.columns]
    x, y = new.loc[rows, cols].to_numpy(float), ref.loc[rows, cols].to_numpy(float)
    eq = (x == y) | (np.isnan(x) & np.isnan(y))
    diff = np.where(eq, 0.0, np.abs(x - y))
    with open(new_path, "rb") as f1, open(ref_path, "rb") as f2:
        same_bytes = f1.read() == f2.read()
    miss_r, miss_c = [r for r in ref.index if r not in new.index], [c for c in ref.columns if c not in new.columns]
    extra_c = [c for c in new.columns if c not in ref.columns]
    bad = [(rows[i], cols[j], x[i, j], y[i, j]) for i, j in zip(*np.nonzero(~eq))]
    ok = not bad and not miss_r and not miss_c
    lines = [f"{os.path.basename(new_path)} vs {ref_path}: {'PASS' if ok else 'FAIL'}; {eq.size} cells compared, {len(bad)} differ, "
             f"max |diff| {float(np.nanmax(diff)) if diff.size else float('nan'):.3g}; byte-identical {'yes' if same_bytes else 'no'}"
             + (f"; reference rows missing {miss_r}" if miss_r else "") + (f"; reference columns missing {miss_c}" if miss_c else "")
             + (f"; extra columns {extra_c}" if extra_c else "")]
    lines += [f"  {r} / {c}: new {xv!r} ref {yv!r}" for r, c, xv, yv in bad[:50]]
    return ok, same_bytes, len(bad), lines


check = None
if a.check_against:
    ref_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(a.check_against)))
    lines = [f"check-against {a.check_against} (modified {ref_mtime})", f"run: {' '.join(sys.argv)}",
             f"protocol {a.protocol}, simulation as conditioning.py at defaults: {'yes' if at_defaults else 'NO (a mismatch is expected)'}; "
             f"NUMBA_NUM_THREADS {os.environ.get('NUMBA_NUM_THREADS', '-')}, {sim.T} chunks"]
    ok, same_bytes, n_bad, ln = compare(out, a.check_against); lines += ln
    ref_comp = a.check_against[:-4] + "_compartments.csv" if a.check_against.endswith(".csv") else None
    if ref_comp and os.path.exists(ref_comp):
        ok_c, same_c, n_bad_c, ln = compare(out_comp, ref_comp); lines += ln
        ok, same_bytes, n_bad = ok and ok_c, same_bytes and same_c, n_bad + n_bad_c
    else:
        lines.append(f"no reference compartments file next to {a.check_against}")
    lines.append(f"CHECK: {'PASS' if ok else 'FAIL'} (to the digit: {'yes' if ok and same_bytes else 'no'})")
    tmp, chk = _edge.safe_out(out_chk)
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
    _edge.finish(tmp, chk)
    print("\n".join(lines)); print("wrote", chk)
    check = {"reference": a.check_against, "reference_mtime": ref_mtime, "pass": ok, "byte_identical": same_bytes, "cells_differ": n_bad, "file": chk}

phase_list = [("cycle", c + 1, lb, k, sec) for c in range(a.cycles) for lb, k, sec in CYCLE]
if a.protocol == "extinction":
    phase_list += [("mid-test", 0, "test", "frozen", 4 * a.test_s)] + [("ext", c + 1, lb, k, sec) for c in range(a.ext_cycles) for lb, k, sec in EXT]
_edge.sidecar(out, {"args": vars(a), "variant": str(cx.variant), "tag": tag, "at_defaults": at_defaults,
                    "us": us_desc, "wiring_us_n": int(len(WUS)), "n_csp_orns": int(len(csp[0])), "n_csm_orns": int(len(csm[0])),
                    "plasticity": {"eta": a.eta, "tau_rec": 0, "w_min": a.w_min, "tau_elig": a.tau_elig, "us_hz": a.us_hz, "tau_dan": a.tau_dan,
                                   "tick_ms": STEP},
                    "phases": phase_list, "phase_stats": PHASE_STATS, "files": [out, out_comp], "check": check,
                    "wall_s": round(time.time() - wall0, 1)})
