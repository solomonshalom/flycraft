#!/usr/bin/env python3
"""Statistics for a learn_in_world.sh run: what the fly did at each flower patch before, during and after learning.

  python experiments/learn_stats.py logs/<trial>_mb-...csv --pre 120 --train 300 --post 120 [--patchA poppy --patchB dandelion --r 10]
Phases are cut by the brain's own plasticity flag (pl_learning), or by wall time from the first tick for older logs. Patch zones are the west / east thirds of the chamber (x < -r/4, x > r/4);
"smelling A" = A is the dominant odor class at the antennae and above 0.5 (both patches are within smelling range everywhere).
For each phase: brain time, fraction of time in each zone, time smelling each odor class, MBON / turning / feeding
activity while smelling A vs B, proboscis extensions in each zone, reward (US) ticks, and the KC->MBON weight fractions.
"""
import argparse, json, os, sys
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("csv"); ap.add_argument("--pre", type=float, default=120); ap.add_argument("--train", type=float, default=300)
ap.add_argument("--post", type=float, default=120); ap.add_argument("--patchA", default="poppy"); ap.add_argument("--patchB", default="dandelion")
ap.add_argument("--r", type=float, default=10); ap.add_argument("--classA", default="ester"); ap.add_argument("--classB", default="vinegar")
a = ap.parse_args()

d = pd.read_csv(a.csv)
t = d.t_wall - d.t_wall.iloc[0]
if "pl_learning" in d.columns and d.pl_learning.notna().any():        # exact phase boundaries from the brain's own flag
    on = d.pl_learning.fillna(0).astype(int).to_numpy()
    first_on = int(np.argmax(on)) if on.any() else len(d)
    last_on = len(d) - 1 - int(np.argmax(on[::-1])) if on.any() else len(d)
    phase = np.where(np.arange(len(d)) < first_on, "pre", np.where(np.arange(len(d)) <= last_on, "train", "post"))
else:
    phase = np.where(t < a.pre, "pre", np.where(t < a.pre + a.train, "train", "post"))
d["phase"] = phase
zone = np.where(d.x < -a.r / 4, "A", np.where(d.x > a.r / 4, "B", "mid"))
d["zone"] = zone
oa = d[[c for c in d.columns if c.startswith(f"odor_{a.classA}_")]].max(axis=1) if any(c.startswith(f"odor_{a.classA}_") for c in d.columns) else pd.Series(0, index=d.index)
ob = d[[c for c in d.columns if c.startswith(f"odor_{a.classB}_")]].max(axis=1) if any(c.startswith(f"odor_{a.classB}_") for c in d.columns) else pd.Series(0, index=d.index)
d["smellA"], d["smellB"] = oa.fillna(0), ob.fillna(0)
print(f"== {os.path.basename(a.csv)}: {len(d)} ticks, {d.brain_t_ms.iloc[-1]/1000:.0f} s brain time; patch A = {a.patchA} ({a.classA}, west, nectar), patch B = {a.patchB} ({a.classB}, east)")
rows = []
for ph in ("pre", "train", "post"):
    p = d[d.phase == ph]
    if len(p) == 0:
        continue
    bt = (p.brain_t_ms.iloc[-1] - p.brain_t_ms.iloc[0]) / 1000
    inA, inB = (p.zone == "A").mean(), (p.zone == "B").mean()
    sA, sB = (p.smellA > p.smellB) & (p.smellA > 0.5), (p.smellB > p.smellA) & (p.smellB > 0.5)   # the dominant odor, and close
    def when(mask, col):
        return float(p.loc[mask, col].mean()) if mask.any() and col in p else float("nan")
    r = dict(phase=ph, ticks=len(p), brain_s=round(bt, 1), frac_in_A=round(inA, 3), frac_in_B=round(inB, 3),
             frac_smell_A=round(float(sA.mean()), 3), frac_smell_B=round(float(sB.mean()), 3),
             mbon_A=when(sA, "hz_mb_mbon"), mbon_B=when(sB, "hz_mb_mbon"), kc_A=when(sA, "hz_mb_kc"), kc_B=when(sB, "hz_mb_kc"),
             turn_A=when(sA, "ctl_turn"), turn_B=when(sB, "ctl_turn"), walk_A=when(sA, "ctl_walk"), walk_B=when(sB, "ctl_walk"),
             feedhz_A=when(sA, "hz_feed"), feedhz_B=when(sB, "hz_feed"),
             feeds_A=int(p.loc[p.zone == "A", "ctl_feed"].astype(bool).sum()) if "ctl_feed" in p else 0,
             feeds_B=int(p.loc[p.zone == "B", "ctl_feed"].astype(bool).sum()) if "ctl_feed" in p else 0,
             us_reward_ticks=int((p.pl_us_reward > 0).sum()) if "pl_us_reward" in p else 0,
             us_punish_ticks=int((p.pl_us_punish > 0).sum()) if "pl_us_punish" in p else 0,
             w_all=(round(float(p.pl_kc_mbon_w_frac.dropna().iloc[-1]), 3) if "pl_kc_mbon_w_frac" in p and p.pl_kc_mbon_w_frac.notna().any() else None),
             w_reward=(round(float(p.pl_w_frac_reward_comp.dropna().iloc[-1]), 3) if "pl_w_frac_reward_comp" in p and p.pl_w_frac_reward_comp.notna().any() else None),
             w_punish=(round(float(p.pl_w_frac_punish_comp.dropna().iloc[-1]), 3) if "pl_w_frac_punish_comp" in p and p.pl_w_frac_punish_comp.notna().any() else None))
    rows.append(r)
    print(f"  [{ph:5s}] {bt:5.0f} s brain | in A {inA*100:4.1f}%  in B {inB*100:4.1f}% | smelling A {sA.mean()*100:4.1f}%  B {sB.mean()*100:4.1f}% "
          f"| MBON when smelling A {r['mbon_A']:5.1f} / B {r['mbon_B']:5.1f} Hz | turn A {r['turn_A']:+.2f} B {r['turn_B']:+.2f} | walk A {r['walk_A']:.2f} B {r['walk_B']:.2f} "
          f"| feeds A {r['feeds_A']} B {r['feeds_B']} | US reward ticks {r['us_reward_ticks']} punish {r['us_punish_ticks']} | w all {r['w_all']} reward-comp {r['w_reward']} punish-comp {r['w_punish']}")
out = a.csv.replace(".csv", "_learn_stats.csv"); pd.DataFrame(rows).to_csv(out, index=False); print("wrote", out)
trial = str(d.trial.iloc[0]) if "trial" in d else ""
for ph in ("pre", "post"):                                     # graded readout (brainctl probe): KC->MBON drive per compartment, per odor class
    f = os.path.join(os.path.dirname(a.csv), f"learn_{trial}_probe_{ph}.json")
    if os.path.exists(f):
        try:
            pr = json.load(open(f)).get("probe", {})
            print(f"  probe {ph:4s}: " + " | ".join(f"{cls}: KC {v['kc_active']*100:.1f}% MBON {v['mbon_hz']:.1f} Hz, drive reward-comp {v.get('drive_reward_comp', 0)/1000:.1f}k punish-comp {v.get('drive_punish_comp', 0)/1000:.1f}k" for cls, v in pr.items()))
            if ph == "post":
                pre = json.load(open(f.replace("_post", "_pre"))).get("probe", {})
                for cls, v in pr.items():
                    if cls in pre:
                        rr = lambda k: v.get(k, 0) / pre[cls].get(k, 1) if pre[cls].get(k, 0) > 0 else float("nan")
                        print(f"  retained drive (post/pre) {cls:8s}: reward-comp {rr('drive_reward_comp'):.3f}  punish-comp {rr('drive_punish_comp'):.3f}  all {rr('drive_all'):.3f}")
        except Exception as e:
            print("  probe file unreadable:", e)
mem = os.path.join(os.path.dirname(a.csv), f"learn_{trial}_memory.json") if trial else None
if mem and os.path.exists(mem):
    try:
        w = json.load(open(mem)).get("w_by_compartment", {})
        low = sorted(w.items(), key=lambda kv: kv[1])[:8]
        print("  memory (most depressed KC->MBON compartments, w/w0):", ", ".join(f"{k} {v:.3f}" for k, v in low))
    except Exception as e:
        print("  memory file unreadable:", e)
