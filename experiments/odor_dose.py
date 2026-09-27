#!/usr/bin/env python3
"""Odor concentration sweep: does the model fly steer toward or away from an odor, and does the sign depend on the
concentration? (RESEARCH_NOTES 16i: food odor on the LEFT antenna at the body's maximal 150 Hz gave DNa L 19 / R 24,
i.e. the turning DNs favoured the side away from the odor; a real fly avoids high concentrations of food odors and
approaches low ones. Until this is measured, chemotaxis in the world is undefined.)

For each odor (the library's food / vinegar / ester / sweet / aversive classes, cVA, CO2) and ORN rate 25-150 Hz
(150 Hz = the body's maximum R_OLF), the odor is presented on the LEFT antenna only, on the RIGHT antenna only and
bilaterally. The approach index is the ipsilateral-minus-contralateral turning-DN rate (DNa L - R for a left odor,
DNa R - L for a right odor): > 0 = the turning DNs favour the odor's side = turn toward it. The left and right
presentations separate steering from a fixed turning bias: steering = (approach_L + approach_R) / 2, and the fixed
bias = (approach_L - approach_R) / 2 (a bias that turns the fly left whatever the odor's side counts as approach for a
left odor and avoidance for a right one; RESEARCH_NOTES 14s, 18c). Fixed connectome, --seeds trials of --ms each.
  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/odor_dose.py --dataset flywire|malecns [--seeds 3] [--ms 1000]
Writes experiments/results/odor_dose_<dataset>_<variant>.csv
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, output_groups, make_sim
from flybrain.senses import SensoryEncoder

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--rates", type=float, nargs="+", default=[25, 50, 75, 100, 150])
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--gain", type=float, default=1.0)
a = ap.parse_args()

cx = connectome.load(dataset=a.dataset); print(cx, flush=True)
senses = SensoryEncoder(cx, verbose=False)
OG = output_groups(cx)
keep_out = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DN all", "feed MNs", "MN9", "DNp13 reject", "PAM (reward DA)", "PPL1 (punish DA)", "KC", "MBON", "leg MNs", "song MNs"]
OUT = {k: OG[k] for k in keep_out if k in OG}
KC = OUT["KC"]


def odor_drive(name, side, hz):
    if name in ("cVA", "CO2", "aversive (DA2/DL4)"):
        g = {"cVA": "orn_cva", "CO2": "orn_co2", "aversive (DA2/DL4)": "orn_aversive"}[name] + (f"_{side}" if side else "")
        idx = senses.groups[g]
        return idx, np.full(len(idx), hz, np.float32)
    return senses.odor(name, side=side, r_max=hz)


ODORS = ["food", "vinegar", "ester", "sweet", "aversive", "cVA", "CO2"]
sim = make_sim(cx, gain=a.gain)
rows, t0 = [], time.time()
for odor in ODORS:
    for hz in a.rates:
        for side in ("L", "R", None):
            idx, rate = odor_drive(odor, side, hz)
            if not len(idx):
                continue
            for seed in range(a.seeds):
                sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
                tw = time.perf_counter(); counts, _ = sim.run(a.ms); wall = time.perf_counter() - tw
                r = {"odor": odor, "hz": hz, "side": side or "both", "seed": seed, "n_orn": int(len(idx)), "wall_s": round(wall, 2),
                     "active_frac": float((counts > 0).mean()), "total_spikes": int(counts.sum())}
                for k, v in OUT.items():
                    r[k] = float(counts[v].sum() / len(v) / (a.ms / 1000))
                r["KC active %"] = float((counts[KC] > 0).mean() * 100)
                r["approach (L-R)"] = r["DNa L"] - r["DNa R"]                      # kept for the left presentation
                r["approach (ipsi-contra)"] = (r["DNa L"] - r["DNa R"]) if side != "R" else (r["DNa R"] - r["DNa L"])
                rows.append(r)
            d = pd.DataFrame(rows[-a.seeds:])
            print(f"{odor:18s} {hz:4.0f} Hz {side or 'both':4s} | DNa L {d['DNa L'].mean():5.1f} R {d['DNa R'].mean():5.1f} (ipsi-contra {d['approach (ipsi-contra)'].mean():+5.1f}) "
                  f"DNp09 {d['DNp09'].mean():4.1f} MDN {d['MDN back'].mean():4.1f} GF {d['GF jump'].mean():4.1f} | PPL1 {d['PPL1 (punish DA)'].mean():5.1f} PAM {d['PAM (reward DA)'].mean():4.1f} "
                  f"| KC {d['KC active %'].mean():4.1f}% MBON {d['MBON'].mean():4.1f} | brain {d.active_frac.mean()*100:4.1f}% ({time.time()-t0:.0f}s)", flush=True)
df = pd.DataFrame(rows)
out = os.path.join(RES, f"odor_dose_{a.dataset}_{cx.variant}" + ("" if a.gain == 1 else f"_gain{a.gain:g}") + ".csv")
df.to_csv(out, index=False); print("wrote", out)
