#!/usr/bin/env python3
"""State arm: impose an internal state the way the fly does it -- tonic activity in the fly's own state
neurons (SAG = virgin, IPC/DH44 = fed, NPF/SIFa = hungry/aroused, pC1 = aroused/aggressive female, P1 = courting
male) -- and re-run the social input x output map. Every neuron here is labeled in the connectome; nothing is
added to the wiring. With no state drive the model is, in effect, a mated (SAG silent), starved (IPC silent),
unaroused fly.

  python experiments/state_probe.py --dataset flywire|malecns [--state-hz 30] [--hz 100] [--seeds 5] [--ms 1000]
Writes experiments/results/state_probe_<dataset>_<variant>_state<hz>.csv
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, input_groups, output_groups, state_groups, make_sim, run_trials, fmt

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--state-hz", type=float, default=30.0)
ap.add_argument("--hz", type=float, default=100.0)
ap.add_argument("--seeds", type=int, default=5)
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--gain", type=float, default=1.0)
a = ap.parse_args()
cx = connectome.load(dataset=a.dataset); print(cx)
IG = input_groups(cx); OG = output_groups(cx); SG = state_groups(cx)
keep_in = ["cVA (Or67d/DA1)", "touch (all head bristles)", "cVA + touch", "song/sound (JO-A)", "food odor", "sugar GRNs",
           "Or47b (VA1v)", "contact pheromone (ppk23/25)", "ppk25 + touch", "all pheromones + contact + touch", "cVA + sugar"]
INPUTS = {"none": []} | {k: IG[k] for k in keep_in if k in IG}
keep_out = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept",
            "DNp13 reject", "oviDN egg", "SAG", "IPC", "feed MNs", "MN9", "P1/pC1 male", "pIP10 song cmd", "vPR6 song", "TN1 song",
            "song MNs", "wing MNs", "leg MNs", "PAM (reward DA)", "PPL1 (punish DA)", "KC", "DN all"]
OUTPUTS = {k: OG[k] for k in keep_out if k in OG}
print("states:", {k: len(v) for k, v in SG.items()})
show = [k for k in ("pC1a recept", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "oviDN egg", "P1/pC1 male", "pIP10 song cmd",
                    "TN1 song", "song MNs", "feed MNs", "DNa L", "DNa R", "MDN back") if k in OUTPUTS]
sim = make_sim(cx, gain=a.gain)
rows, t0 = [], time.time()
for sname, sidx in [("none", np.zeros(0, np.int64))] + list(SG.items()):
    for iname, groups in INPUTS.items():
        drive = [(sidx, a.state_hz)] + [(g, a.hz) for g in groups]
        r = run_trials(sim, drive, a.hz, a.ms, a.seeds, OUTPUTS, extra={"state": sname, "input": iname})
        rows += r; d = pd.DataFrame(r)
        print(f"{sname:34s} | {iname:30s} act {d.active_frac.mean()*100:4.1f}% | " +
              " ".join(f"{k.split(' ')[0]} {fmt(d[k].mean(), d[k].std())}" for k in show) + f" ({time.time()-t0:.0f}s)", flush=True)
df = pd.DataFrame(rows)
out = os.path.join(RES, f"state_probe_{a.dataset}_{cx.variant}_state{a.state_hz:g}.csv"); df.to_csv(out, index=False); print("wrote", out)
