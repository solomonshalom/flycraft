#!/usr/bin/env python3
"""Pre-contact slowing as a dose row: is the 20-35 % drop of the female's turning DNs in the last two blocks before a
first contact (RESEARCH_NOTES 19b) the dose curve of the partner's odor? (WHATS_LEFT_FLY, machine-time item 6)

In the arena a female that is about to meet another fly smells, bilaterally and together, the partner's body odor
(Or47b -> VA1v), its CO2 (ORN_V) and, if the partner is male, cVA (Or67d / Or65a -> DA1 / DL3), at levels the body
reports as fractions of the 150 Hz maximum (`obs_smell_*` in the arena logs): far (> 3.5 blocks) cVA 0.06-0.14,
Or47b ~0.10, CO2 0.003; at 1-3 blocks cVA 0.3-0.7, Or47b 0.4-0.9, CO2 0.02. This script drives the female brain
(the paper's model) with exactly those mixtures, with and without the 0.2 Hz walking substrate of 19c, lets it settle
for --settle ms (the arena's steady state, not the 1 s onset of 19c) and reads the turning DNs and the body's walking
drive (1 - exp(-rate / 10 Hz) of DNp09 + DNa01/02, motor.py) over the next --ms.

  FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 python experiments/precontact_dose.py [--seeds 3] [--settle 2000] [--ms 2000]
Writes experiments/results/precontact_dose_<dataset>_<variant>.csv (one row per condition x substrate x seed).
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, output_groups, make_sim

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--settle", type=float, default=2000, help="ms of brain time before the reading (the arena's steady state)")
ap.add_argument("--ms", type=float, default=2000, help="ms of brain time read out")
ap.add_argument("--noise", default="0,0.2", help="walking substrates (Hz per neuron): 0 = the clean mf chamber, 0.2 = the substrate chambers")
ap.add_argument("--r-max", type=float, default=150.0, help="the body's R_OLF: level 1.0 = 150 Hz on the receptor neurons")
ap.add_argument("--set", default="main", choices=("main", "window", "far", "near"),
                help="main = the dose row of Fig 14; window = Or47b 0.40-0.90 in 0.05 steps, with and without CO2 0.02 (is the "
                     "Or47b 0.6 + CO2 0.02 response a narrow window?); far / near = the far- / near-level cells, for more seeds on the substrate. "
                     "Sets other than main write precontact_dose_<dataset>_<variant>_<set>.csv")
a = ap.parse_args()

cx = connectome.load(dataset=a.dataset); print(cx, flush=True)
s = cx.select
CH = {"cVA": s(cell_type=r"^ORN_(DA1|DL3)$"), "Or47b": s(cell_type=r"^ORN_VA1v$"), "CO2": s(cell_type=r"^ORN_V$")}   # senses.py orn_cva / orn_fly / orn_co2
OG = output_groups(cx)
keep = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "DN all", "KC", "PPL1 (punish DA)", "pC1a recept", "pC1d/e aggr"]
OUT = {k: OG[k] for k in keep if k in OG}
FWD = s(cell_type=r"^DNp09$|^DNa0[12]$")            # the body's walking population (motor.py "forward", k = 10 Hz)

# (label, cVA, Or47b, CO2) as fractions of the body's maximum, read from the 19b arena logs
LEVELS = [("nothing", 0, 0, 0),
          ("ff far: Or47b 0.10, CO2 0.003", 0, 0.10, 0.003),
          ("ff near: Or47b 0.4, CO2 0.02", 0, 0.4, 0.02), ("ff near: Or47b 0.6, CO2 0.02", 0, 0.6, 0.02), ("ff near: Or47b 0.9, CO2 0.02", 0, 0.9, 0.02),
          ("mf far: cVA 0.06, Or47b 0.10, CO2 0.003", 0.06, 0.10, 0.003), ("mf far: cVA 0.10, Or47b 0.10, CO2 0.003", 0.10, 0.10, 0.003),
          ("mf far: cVA 0.14, Or47b 0.10, CO2 0.003", 0.14, 0.10, 0.003),
          ("mf near: cVA 0.3, Or47b 0.4, CO2 0.02", 0.3, 0.4, 0.02), ("mf near: cVA 0.5, Or47b 0.6, CO2 0.02", 0.5, 0.6, 0.02),
          ("mf near: cVA 0.7, Or47b 0.9, CO2 0.02", 0.7, 0.9, 0.02)]
LEVELS += [(f"cVA alone {v:g}", v, 0, 0) for v in (0.06, 0.14, 0.3, 0.5, 0.7)]
LEVELS += [(f"Or47b alone {v:g}", 0, v, 0) for v in (0.10, 0.4, 0.9)]
LEVELS += [(f"CO2 alone {v:g}", 0, 0, v) for v in (0.003, 0.02)]
if a.set == "window":        # RESEARCH_NOTES 20b: Or47b 0.6 + CO2 0.02 drives DNa 9 / 13 Hz, 0.4 and 0.9 nothing
    STEPS = [round(0.40 + 0.05 * i, 2) for i in range(11)]
    LEVELS = [(f"Or47b {v:.2f} + CO2 0.02", 0, v, 0.02) for v in STEPS] + [(f"Or47b alone {v:.2f}", 0, v, 0) for v in STEPS]
elif a.set == "far":         # the far levels, whose seed spread on the substrate was +-7-9 Hz at 3 seeds
    LEVELS = [lv for lv in LEVELS if lv[0] == "nothing" or " far: " in lv[0] or lv[0] == "Or47b alone 0.1"]
elif a.set == "near":        # the near levels at the same seed count as the far set (the substrate's own spread is +-6-7 Hz at 10 seeds)
    LEVELS = [lv for lv in LEVELS if " near: " in lv[0] or lv[0] == "CO2 alone 0.02"]


def drive(cva, fly, co2):
    idx, rate = [], []
    for g, lvl in ((CH["cVA"], cva), (CH["Or47b"], fly), (CH["CO2"], co2)):
        if lvl > 0 and len(g):
            idx.append(g); rate.append(np.full(len(g), lvl * a.r_max, np.float32))
    if not idx:
        return np.zeros(0, np.int64), np.zeros(0, np.float32)
    return np.concatenate(idx), np.concatenate(rate)


rows, t0 = [], time.time()
for noise in [float(x) for x in a.noise.split(",")]:
    sim = make_sim(cx, noise_hz=noise)
    for label, cva, fly, co2 in LEVELS:
        idx, rate = drive(cva, fly, co2); rs = []
        for seed in range(a.seeds):
            sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
            if a.settle > 0:
                sim.run(a.settle)
            tw = time.perf_counter(); counts, _ = sim.run(a.ms); wall = time.perf_counter() - tw
            r = {"noise_hz": noise, "condition": label, "cVA": cva, "Or47b": fly, "CO2": co2, "cVA_hz": cva * a.r_max, "Or47b_hz": fly * a.r_max, "CO2_hz": co2 * a.r_max,
                 "seed": seed, "settle_ms": a.settle, "ms": a.ms, "wall_s": round(wall, 2), "active_frac": float((counts > 0).mean())}
            for k, v in OUT.items():
                r[k] = float(counts[v].sum() / len(v) / (a.ms / 1000))
            fwd = float(counts[FWD].sum() / len(FWD) / (a.ms / 1000))
            r["forward DNs"] = fwd; r["walk duty"] = float(1 - np.exp(-fwd / 10.0)); r["turn"] = float(np.tanh((r["DNa L"] - r["DNa R"]) / 40))
            rows.append(r); rs.append(r)
        d = pd.DataFrame(rs)
        print(f"noise {noise:3.1f} | {label:42s} DNa {d['DNa L'].mean():5.1f}±{d['DNa L'].std():4.1f} / {d['DNa R'].mean():5.1f}±{d['DNa R'].std():4.1f}  DNp09 {d['DNp09'].mean():4.1f}  "
              f"walk {d['walk duty'].mean():.2f}  turn {d['turn'].mean():+.2f}  GF {d['GF jump'].mean():4.1f}  DNp13 {d['DNp13 reject'].mean():4.1f}  MDN {d['MDN back'].mean():4.1f}  "
              f"PPL1 {d['PPL1 (punish DA)'].mean():4.1f}  act {d.active_frac.mean()*100:4.1f}%  ({time.time()-t0:.0f}s)", flush=True)
    del sim
df = pd.DataFrame(rows)
out = os.path.join(RES, f"precontact_dose_{a.dataset}_{cx.variant}" + ("" if a.set == "main" else f"_{a.set}") + ".csv")
df.to_csv(out, index=False); print("wrote", out)
