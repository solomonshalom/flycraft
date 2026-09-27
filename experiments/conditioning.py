#!/usr/bin/env python3
"""In-silico olfactory conditioning (Tully & Quinn style) in the learning arm (Fig 2).

CS+ (an odor class of the library, default 'vinegar') is paired with the US; CS- (default 'ester') is presented alone;
plasticity is ON only during training. Before and after training the network's response to CS+ and CS- is measured
with plasticity frozen: MBON output (all, and the reward- vs punishment-compartment MBONs), the turning DNs for a
LATERALIZED odor (CS on the left antenna only: DNa L - R is the approach index), DNp09 / MDN, feeding MNs, and which
KC->MBON compartments were depressed.

The US is either what the wiring itself delivers to the dopamine neurons (--us wiring: sugar GRNs at 100 Hz) or the
optogenetic-style activation of the identified reward / punishment DANs (--us dan --valence reward|punish); see
flybrain/plasticity.py. The odor code depends on the model variant (--signs, --eln; RESEARCH_NOTES 16): under the
published sign rule every odor drives the same Kenyon cells, so nothing odor-specific can be learned.

  python experiments/conditioning.py --signs known --eln 0.25 --us dan --valence reward [--cycles 3] [--seed 0]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RES, make_sim
import numpy as np, pandas as pd
from flybrain import connectome
from flybrain.plasticity import MBPlasticity, PlasticityConfig, REWARD_MBONS, PUNISH_MBONS
from flybrain.senses import SensoryEncoder

ap = argparse.ArgumentParser()
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

cx = connectome.load(dataset=a.dataset, signs=a.signs, eln_scale=a.eln); s = cx.select; print(cx)
senses = SensoryEncoder(cx, verbose=False)
SUGAR = s(cell_class="^gustatory$", cell_sub_class="sugar/water")
OUT = {"DNa L": s(cell_type=r"^DNa0[12]$", side="^left$"), "DNa R": s(cell_type=r"^DNa0[12]$", side="^right$"),
       "DNp09": s(cell_type=r"^DNp09$"), "MDN": s(cell_type=r"^MDN$"), "DN all": s(super_class="^descending$"),
       "feed MNs": s(any_of={"cell_sub_class": r"proboscis_motor_neuron|ingestion_motor_neuron|^pm$", "cell_type": r"^MN9$"}),
       "MBON": s(cell_class="^MBON$"), "PAM": s(cell_class="^DAN$", cell_type=r"^PAM"), "PPL1": s(cell_class="^DAN$", cell_type=r"^PPL1"),
       "KC": s(cell_class="^Kenyon_Cell$")}
sim = make_sim(cx, noise_hz=a.noise_hz, seed=a.seed)
pl = MBPlasticity(cx, sim, PlasticityConfig(eta=a.eta, tau_rec=0, us=a.us, us_hz=a.us_hz, tau_dan=a.tau_dan))
mbon_types = pl.mbon_type
OUT["MBON reward-comp"] = pl.mbon[np.isin(mbon_types, list(REWARD_MBONS))]
OUT["MBON punish-comp"] = pl.mbon[np.isin(mbon_types, list(PUNISH_MBONS))]
csp, csm = senses.odor(a.csp, r_max=a.hz), senses.odor(a.csm, r_max=a.hz)
print(f"CS+ {a.csp}: {len(csp[0])} ORNs   CS- {a.csm}: {len(csm[0])} ORNs   US: {a.us}" + (f" ({a.valence} DANs at {a.us_hz} Hz)" if a.us == "dan" else " (sugar GRNs at 100 Hz)"))


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


print("\n== pre-test (plasticity frozen)")
pre = test("pre")
w_pre = sim.data[pl.e_idx].copy()

us_desc = "sugar GRNs" if a.us == "wiring" else f"{a.valence} DANs"
print(f"\n== training: {a.cycles} cycles x [CS+ + {us_desc} {a.train_s}s | rest {a.rest_s:g}s | CS- alone {a.train_s}s | rest {a.rest_s:g}s], plasticity ON")
t0 = time.time(); step = 50.0
for c in range(a.cycles):
    for phase, secs in [("CS+ & US", a.train_s), ("rest", a.rest_s), ("CS- alone", a.train_s), ("rest", a.rest_s)]:
        if phase == "CS+ & US":
            us = (SUGAR, np.full(len(SUGAR), 100.0, np.float32)) if a.us == "wiring" else pl.us_drive(reward=float(a.valence == "reward"), punish=float(a.valence == "punish"))
            drive = cat(csp, us)
        elif phase == "CS- alone":
            pl.us_drive(0, 0); drive = csm
        else:
            pl.us_drive(0, 0); drive = (np.zeros(0, np.int64), np.zeros(0, np.float32))
        sim.set_drive(*drive); stats = None
        for _ in range(int(secs * 1000 / step)):
            counts, _ = sim.run(step)
            stats = pl.update(counts, step / 1000)
        if phase != "rest":
            print(f"  cycle {c+1} {phase:10s} KC->MBON w {stats['kc_mbon_w_frac']:.3f} (reward-comp {stats['w_frac_reward_comp']:.3f}, punish-comp {stats['w_frac_punish_comp']:.3f})  "
                  f"DAN {stats['dan_hz']:.1f} Hz  KC {stats['kc_hz']:.1f} Hz, {stats['kc_active']*100:.1f}% active  ({time.time()-t0:.0f}s)", flush=True)
w_post = sim.data[pl.e_idx].copy()

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
tag = (f"{a.dataset}_{cx.variant}_us-{a.us}" + (f"-{a.valence}" if a.us == "dan" else "") + (f"-{a.us_hz:g}hz" if a.us == "dan" and a.us_hz != 50 else "")
       + (f"-phasic{a.tau_dan:g}" if a.tau_dan > 0 else "") + f"_{a.csp}-vs-{a.csm}_seed{a.seed}" + (f"_{a.tag}" if a.tag else ""))
out = os.path.join(RES, f"conditioning_{tag}.csv")
tab = {}
for ph, res in (("pre", pre), ("post", post)):
    for cs in ("CS+", "CS-"):
        tab[f"{ph}_{cs}"] = {k: v for k, v in res[cs].items() if k not in ("MBON by type", "drive by type")}
df = pd.DataFrame(tab); df.loc["w_retained"] = float(w_post.sum() / w_pre.sum()); df.to_csv(out)
frac.to_csv(os.path.join(RES, f"conditioning_{tag}_compartments.csv"), header=["w_over_w0"])
print("wrote", out)
