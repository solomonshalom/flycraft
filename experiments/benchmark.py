#!/usr/bin/env python3
"""Published-result anchors (Shiu et al. 2024, Nature), using the exact neurons they used (root IDs from their
figures.ipynb; v630 IDs that persist in v783). Female only.

  1. Sugar GRNs -> MN9: rate curve over 10-200 Hz; "100 Hz gives roughly 80 % of maximal MN9 firing".
  2. Bitter GRNs suppress the sugar response of MN9.
  3. Water GRNs activate MN9 (and ~391 neurons at the drive giving ~40 Hz MN9).
  4. JO-CE activation drives aBN1 (antennal grooming); JO-F activation does not (validated by optogenetics).
  5. Sound (JO-A/B) -> giant fiber (DNp01) escape response; mechanosensory bristles -> MDN backing.
  python experiments/benchmark.py [--seeds 3] [--ms 1000]
Writes experiments/results/benchmark_flywire.csv and prints pass/fail.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import RES, connectome, make_sim, run_trials, SHIU_SUGAR, SHIU_MN9

SUGAR_L = [720575940620589838, 720575940631147148, 720575940608305161, 720575940629388135, 720575940630968335, 720575940606801282,
           720575940617398502, 720575940616167218, 720575940620296641, 720575940627961104]
BITTER = [720575940621778381, 720575940602353632, 720575940617094208, 720575940619197093, 720575940626287336, 720575940618600651,
          720575940627692048, 720575940630195909, 720575940646212996, 720575940610483162, 720575940645743412, 720575940627578156,
          720575940622298631, 720575940621008895, 720575940629146711, 720575940610259370, 720575940610481370, 720575940619028208,
          720575940614281266, 720575940613061118, 720575940604027168]
WATER = [720575940612950568, 720575940631898285, 720575940606002609, 720575940612579053, 720575940622902535, 720575940616177458,
         720575940660292225, 720575940622486922, 720575940613786774, 720575940629852866, 720575940625861168, 720575940613996959,
         720575940617857694, 720575940644965399, 720575940625203504, 720575940630553415, 720575940635172191, 720575940634796536]
JON_CE = [720575940619341105, 720575940630122015, 720575940611061526, 720575940615848788, 720575940628444667, 720575940627941431, 720575940632449619,
          720575940650244342, 720575940631866508, 720575940638681845, 720575940628978450, 720575940609522461, 720575940621442224, 720575940602506208,
          720575940629022149, 720575940627109991, 720575940630020111, 720575940615986459, 720575940618684481, 720575940620382889, 720575940630080071,
          720575940626565455, 720575940630319671, 720575940602720940, 720575940630564179, 720575940637632419, 720575940615809349, 720575940626042149,
          720575940637054835, 720575940602132509, 720575940614188149, 720575940616951124, 720575940628101126, 720575940629055721, 720575940616589878,
          720575940622449388, 720575940614427195, 720575940625797617, 720575940638664437, 720575940618467195, 720575940621729757, 720575940613971485,
          720575940627585688, 720575940629650997, 720575940630059847, 720575940608742409, 720575940614351477, 720575940633153375, 720575940622937528,
          720575940604753437, 720575940611783464, 720575940618599872, 720575940609541917, 720575940637410869, 720575940630070343, 720575940621397417,
          720575940614035485, 720575940610018266, 720575940626307902, 720575940634634606, 720575940614060829, 720575940624799290, 720575940641921421,
          720575940623298559, 720575940625559358, 720575940629138959, 720575940621625597, 720575940625962568, 720575940632767383, 720575940624915230]
JON_F = [720575940606239243, 720575940626956777, 720575940604973746, 720575940622222856, 720575940642517284, 720575940629719404, 720575940616613022,
         720575940604299454, 720575940615473186, 720575940622217992, 720575940606800341, 720575940629267498, 720575940637366335, 720575940624224408,
         720575940609543197, 720575940633364179, 720575940629502009, 720575940606431189, 720575940625733960, 720575940638529525, 720575940617524053,
         720575940628935564, 720575940624308355, 720575940631170346, 720575940627704375, 720575940625885512, 720575940614929245, 720575940647493241,
         720575940618888368, 720575940625087546, 720575940606657493, 720575940617273560, 720575940640591861, 720575940639410035, 720575940621532413,
         720575940627523584, 720575940621521917, 720575940621097398, 720575940625915338, 720575940606222428, 720575940627868471, 720575940622179497,
         720575940608297774, 720575940614026269, 720575940613012959, 720575940628100614, 720575940606611401, 720575940628649465, 720575940610008217,
         720575940623791152, 720575940625571240, 720575940634923621, 720575940609530653, 720575940635968745, 720575940625703434, 720575940613105311,
         720575940629386819, 720575940623077389, 720575940625763015, 720575940628359017]
MN9_R = [720575940645521262]; ABN1 = [720575940630907434]

ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=3); ap.add_argument("--ms", type=float, default=1000)
a = ap.parse_args()
cx = connectome.load(dataset="flywire"); print(cx)
ids = lambda L: cx.by_root_ids(L)
G = {"sugar (Shiu, R+L)": ids(SHIU_SUGAR + SUGAR_L), "bitter (Shiu)": ids(BITTER), "water (Shiu)": ids(WATER), "JON-CE (Shiu)": ids(JON_CE), "JON-F (Shiu)": ids(JON_F),
     "sugar/water GRNs (annotation)": cx.select(cell_class="^gustatory$", cell_sub_class="sugar/water"),
     "JO-A/B (annotation)": cx.select(cell_class="^mechanosensory", cell_sub_class="auditory"), "bristles BM_": cx.select(cell_type=r"^BM_")}
for k, v in G.items():
    print(f"  {k:32s} {len(v):4d} neurons found")
OUT = {"MN9 L": ids(SHIU_MN9), "MN9 R": ids(MN9_R), "MN9 both": ids(SHIU_MN9 + MN9_R), "aBN1": ids(ABN1), "GF": cx.select(cell_type=r"^DNp01$"),
       "MDN": cx.select(cell_type=r"^MDN$"), "feed MNs": cx.select(cell_sub_class=r"proboscis_motor_neuron|ingestion_motor_neuron"),
       "DN all": cx.select(super_class="^descending$")}
sim = make_sim(cx)
rows = []
def cond(label, groups, hz, note=""):
    r = run_trials(sim, groups, hz, a.ms, a.seeds, OUT, extra={"condition": label, "hz": hz}); d = pd.DataFrame(r); rows.extend(r)
    print(f"{label:44s} MN9 L/R {d['MN9 L'].mean():5.1f}/{d['MN9 R'].mean():5.1f}  feed {d['feed MNs'].mean():5.1f}  aBN1 {d['aBN1'].mean():5.1f}  "
          f"GF {d['GF'].mean():5.1f}  MDN {d['MDN'].mean():5.1f}  active {d.active_frac.mean()*100:5.2f}% (n={d.active_frac.mean()*cx.n:.0f}) {note}", flush=True)
    return d
print("\n-- 1. sugar -> MN9 rate curve")
curve = {}
for hz in (10, 25, 50, 75, 100, 150, 200):
    curve[hz] = cond(f"sugar GRNs @ {hz} Hz", [G["sugar (Shiu, R+L)"]], hz)["MN9 both"].mean()
frac100 = curve[100] / max(curve[200], 1e-9)
print(f"   MN9 at 100 Hz / at 200 Hz = {frac100:.2f}   (Shiu et al.: ~0.8)")
print("\n-- 2. bitter suppression (sugar 100 Hz + bitter)")
base = cond("sugar 100 Hz alone", [G["sugar (Shiu, R+L)"]], 100)["MN9 both"].mean()
for bhz in (25, 50, 100):
    cond(f"sugar 100 Hz + bitter {bhz} Hz", [(G["sugar (Shiu, R+L)"], 100), (G["bitter (Shiu)"], bhz)], 100)
cond("bitter 100 Hz alone", [G["bitter (Shiu)"]], 100)
print("\n-- 3. water -> MN9")
for hz in (20, 60, 100, 150, 200, 260):
    cond(f"water GRNs @ {hz} Hz", [G["water (Shiu)"]], hz)
print("\n-- 4. antennal grooming: JON-CE vs JON-F -> aBN1")
ce = cond("JON-CE @ 100 Hz", [G["JON-CE (Shiu)"]], 100)["aBN1"].mean()
jf = cond("JON-F @ 100 Hz", [G["JON-F (Shiu)"]], 100)["aBN1"].mean()
print("\n-- 5. escape and backing")
gf = cond("JO-A/B sound @ 100 Hz", [G["JO-A/B (annotation)"]], 100)["GF"].mean()
mdn = cond("head bristles @ 100 Hz", [G["bristles BM_"]], 100)["MDN"].mean()
df = pd.DataFrame(rows); out = os.path.join(RES, f"benchmark_flywire{"" if cx.variant == "shiu_min1" else "_" + cx.variant}.csv"); df.to_csv(out, index=False)
print("\nRESULTS")
print(f"  sugar->MN9 rises with input and 100 Hz gives {frac100*100:.0f}% of the 200 Hz response (Shiu ~80%): {'PASS' if 0.6 <= frac100 <= 1.0 and curve[100] > 5 else 'CHECK'}")
sb = df[df.condition == 'sugar 100 Hz + bitter 100 Hz']['MN9 both'].mean()
print(f"  bitter suppresses sugar->MN9 ({base:.1f} -> {sb:.1f} Hz): {'PASS' if sb < base else 'CHECK'}")
print(f"  JON-CE drives aBN1 ({ce:.1f} Hz) and JON-F does not ({jf:.1f} Hz): {'PASS' if ce > 2 and jf < ce / 3 else 'CHECK'}")
print(f"  sound -> giant fiber ({gf:.1f} Hz): {'PASS' if gf > 1 else 'CHECK'}   bristles -> MDN ({mdn:.1f} Hz)")
print("wrote", out)
