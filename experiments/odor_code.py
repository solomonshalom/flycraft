#!/usr/bin/env python3
"""Does the model tell odors apart?  Antennal-lobe specificity and Kenyon-cell sparseness (Fig 9).

For each model variant (sign rule x eLN output scale) and each odor (single glomeruli, the food blend, cVA),
drive the ORNs at 100 Hz for 500 ms and measure how far the odor's identity survives:
  * antennal lobe: rate of the cognate glomerulus' PNs, fraction of the 59 glomeruli whose PNs exceed 10 Hz,
    excitatory / inhibitory LN rates
  * mushroom body: fraction of Kenyon cells active, mean KC rate, and the overlap (Jaccard) of the active KC
    sets between every pair of odors (1.0 = the same code for every odor = nothing to learn)
  * downstream: MBON, PAM, PPL1, turning DNs, fraction of the brain active
Variants: published (Shiu signs, eLN x1), known-transmitter signs, and known signs with eLN output x0.5/0.25/0.1.

  python experiments/odor_code.py [--dataset flywire|malecns] [--seeds 2] [--ms 500]
Writes results/odor_code_<dataset>.csv (one row per variant x odor x seed) and results/odor_code_<dataset>_overlap.csv.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RES, make_sim
import numpy as np, pandas as pd
from flybrain import connectome

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="flywire")
ap.add_argument("--seeds", type=int, default=2)
ap.add_argument("--ms", type=float, default=500)
ap.add_argument("--hz", type=float, default=100)
ap.add_argument("--variants", default="shiu,known,known+eln0.5,known+eln0.25,known+eln0.1")
a = ap.parse_args()

VARIANTS = []
for v in a.variants.split(","):
    signs = "known" if v.startswith("known") else "shiu"
    eln = float(v.split("eln")[1]) if "eln" in v else 1.0
    VARIANTS.append((v, signs, eln))

rows, overlap_rows = [], []
for vname, signs, eln in VARIANTS:
    cx = connectome.load(dataset=a.dataset, signs=signs, eln_scale=eln); s = cx.select; n = cx.neurons
    print(cx, flush=True)
    PN = s(cell_class="^ALPN$"); LN = s(cell_class="^ALLN$"); KC = s(cell_class="^Kenyon_Cell$"); MBON = s(cell_class="^MBON$")
    PAM = s(cell_class="^DAN$", cell_type="^PAM"); PPL1 = s(cell_class="^DAN$", cell_type="^PPL1")
    DNaL = s(cell_type=r"^DNa0[12]$", side="^left$"); DNaR = s(cell_type=r"^DNa0[12]$", side="^right$"); DN = s(super_class="^descending$")
    sign = np.sign(np.asarray(cx.W.sum(axis=1)).ravel())
    eLN, iLN = LN[sign[LN] > 0], LN[sign[LN] < 0]
    glom = n.cell_type.fillna("").iloc[PN].str.extract(r"^([A-Z]+\d*[a-z]*)_")[0].fillna("multi").to_numpy()
    ODORS = {g: s(cell_type=rf"^ORN_{g}$") for g in ("DM2", "DL5", "DA1", "VA1v", "DM1", "VM2", "V", "DC3", "DA2")}
    ODORS["food blend (DM1+DM2+DM4+VA2+VM2)"] = s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$")
    ODORS = {k: v for k, v in ODORS.items() if len(v)}
    sim = make_sim(cx)
    codes = {}
    for oname, idx in ODORS.items():
        for seed in range(a.seeds):
            sim.seed(seed); sim.reset(); sim.set_drive(idx, np.full(len(idx), a.hz, np.float32))
            t0 = time.perf_counter(); c, _ = sim.run(a.ms); wall = time.perf_counter() - t0
            r = c / (a.ms / 1000.0); pn = pd.Series(r[PN]).groupby(glom).mean()
            cog = oname.split(" ")[0]
            kc = r[KC]
            row = dict(variant=vname, signs=signs, eln_scale=eln, odor=oname, seed=seed, n_orn=len(idx), wall_s=round(wall, 2),
                       pn_cognate_hz=float(pn.get(cog, np.nan)), pn_mean_hz=float(r[PN].mean()), pn_active=float((r[PN] > 0).mean()),
                       glomeruli_over_10hz=float((pn > 10).mean()), n_glomeruli=int(len(pn)),
                       eln_hz=float(r[eLN].mean()) if len(eLN) else np.nan, iln_hz=float(r[iLN].mean()) if len(iLN) else np.nan,
                       kc_active=float((kc > 0).mean()), kc_hz=float(kc.mean()), kc_hz_of_active=float(kc[kc > 0].mean()) if (kc > 0).any() else 0.0,
                       mbon_hz=float(r[MBON].mean()), pam_hz=float(r[PAM].mean()), ppl1_hz=float(r[PPL1].mean()),
                       dna_l_hz=float(r[DNaL].mean()), dna_r_hz=float(r[DNaR].mean()), dn_all_hz=float(r[DN].mean()),
                       active_frac=float((c > 0).mean()), total_spikes=int(c.sum()))
            rows.append(row); codes[(oname, seed)] = kc > 0
            print(f"[{vname:16s}] {oname[:12]:12s} s{seed} | PN cognate {row['pn_cognate_hz']:5.0f} Hz, glomeruli>10Hz {row['glomeruli_over_10hz']*100:3.0f}% "
                  f"| KC {row['kc_active']*100:5.1f}% active | MBON {row['mbon_hz']:5.1f} PAM {row['pam_hz']:4.1f} PPL1 {row['ppl1_hz']:5.1f} "
                  f"| DNa L/R {row['dna_l_hz']:4.1f}/{row['dna_r_hz']:4.1f} | brain {row['active_frac']*100:4.1f}% ({wall:.1f}s)", flush=True)
    names = list(ODORS)
    for i, x in enumerate(names):
        for y in names[i:]:
            jac = []
            for sx in range(a.seeds):
                for sy in range(a.seeds):
                    if x == y and sx == sy:
                        continue
                    A, B = codes[(x, sx)], codes[(y, sy)]
                    jac.append((A & B).sum() / max((A | B).sum(), 1))
            overlap_rows.append(dict(variant=vname, odor_a=x, odor_b=y, same_odor=(x == y), jaccard=float(np.mean(jac)) if jac else np.nan))
    d = pd.DataFrame([r for r in overlap_rows if r["variant"] == vname])
    print(f"  [{vname}] KC-set Jaccard: same odor across seeds {d[d.same_odor].jaccard.mean():.2f}; different odors {d[~d.same_odor].jaccard.mean():.2f}", flush=True)
    del sim, cx

out = os.path.join(RES, f"odor_code_{a.dataset}.csv"); pd.DataFrame(rows).to_csv(out, index=False)
pd.DataFrame(overlap_rows).to_csv(os.path.join(RES, f"odor_code_{a.dataset}_overlap.csv"), index=False)
print("wrote", out)
