#!/usr/bin/env python3
"""Figure for the arena replication of 25-26 Sep 2026: the reported series next to its replication, per fly-log.

Four panels over the five replicated conditions (clean ff, clean mf, hum ff, hum mf, hum + virgin female mf):
a share of the trial in contact; b the female's turning DNs far vs in contact; c the turn-toward index per log;
d the male's MDN on contact. Reads experiments/results/encounter_trials.csv and the arena logs (via replication_stats).
  python experiments/figure_replication.py [--prefix rep-]      -> experiments/results/fig_replication.{png,pdf}
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from replication_stats import RES, log_of

ap = argparse.ArgumentParser(); ap.add_argument("--prefix", default="rep-"); a = ap.parse_args()
T = pd.read_csv(os.path.join(RES, "encounter_trials.csv")); T = T[T.variant == "specific"]
CONDS = [("clean", "ff", "clean\n\u2640\u2640"), ("clean", "mf", "clean\n\u2642\u2640"), ("noise0.2", "ff", "hum\n\u2640\u2640"),
         ("noise0.2", "mf", "hum\n\u2642\u2640"), ("noise0.2-virgin", "mf", "hum\n\u2642 + virgin \u2640")]
REP, ORIG = "#c0392b", "0.45"


def toward_log(r):
    d = log_of(r)
    if d is None:
        return np.nan
    contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
    first = int(np.argmax(contact.to_numpy())) if contact.any() else len(d)
    pre = d.iloc[:first]; pre = pre[(pre.near_dist < 6) & pre.near_az.notna()]
    return float((pre.ctl_turn * np.sign(pre.near_az)).mean()) if len(pre) else np.nan


def rows(ch, cond, ds):
    return T[(T.chamber == ch) & (T.condition == cond) & (T.dataset == ds)]


fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.8)); axs = axs.ravel()
x = np.arange(len(CONDS)); w = 0.2
for k, (ch, cond, lab) in enumerate(CONDS):
    for j, (chm, col) in enumerate(((ch, ORIG), (a.prefix + ch, REP))):
        fem = rows(chm, cond, "flywire")
        if fem.empty:
            continue
        xx = x[k] + (j - 0.5) * 2 * w
        cp = fem.contact_ticks / fem.ticks * 100
        axs[0].scatter(np.full(len(cp), xx), cp, s=7, color=col, zorder=3)
        axs[0].plot([xx - w * 0.7, xx + w * 0.7], [cp.mean()] * 2, color=col, lw=1.5)
        far = (fem.turn_L_far + fem.turn_R_far) / 2; con = (fem.turn_L_contact + fem.turn_R_contact) / 2
        axs[1].plot([xx - w * 0.5, xx + w * 0.5], [far.mean(), con.mean()], color=col, lw=1.2, marker="o", ms=3)
        tw = [toward_log(r) for _, r in fem.iterrows()]
        axs[2].scatter(np.full(len(tw), xx), tw, s=7, color=col, zorder=3)
        male = rows(chm, cond, "malecns")
        if cond == "mf" and len(male):
            k2 = [c for c in CONDS if c[1] == "mf"].index((ch, cond, lab))
            xm = k2 + (j - 0.5) * 2 * w
            v = male.back_contact.dropna()
            axs[3].scatter(np.full(len(v), xm), v, s=7, color=col, zorder=3)
            if len(v):
                axs[3].plot([xm - w * 0.7, xm + w * 0.7], [v.mean()] * 2, color=col, lw=1.5)
axs[0].set_ylabel("contact (% of the trial)"); axs[0].set_title("a  time spent touching", fontsize=9, loc="left")
axs[1].set_ylabel("steering neurons (Hz)"); axs[1].set_title("b  far  →  in contact", fontsize=9, loc="left")
axs[2].axhline(0, color="0.7", lw=0.6); axs[2].set_ylabel("turn-toward index"); axs[2].set_ylim(-0.3, 0.3)
axs[2].set_title("c  turning towards the other", fontsize=9, loc="left")
axs[3].set_ylabel("male moonwalker on contact (Hz)"); axs[3].set_title("d  the male backs off", fontsize=9, loc="left")
for ax in axs[:3]:
    ax.set_xticks(x); ax.set_xticklabels([c[2] for c in CONDS], fontsize=7)
mf = [c for c in CONDS if c[1] == "mf"]
axs[3].set_xticks(range(len(mf))); axs[3].set_xticklabels([c[2] for c in mf], fontsize=7)
for ax in axs:
    ax.tick_params(labelsize=7); ax.yaxis.label.set_size(8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
axs[0].scatter([], [], color=ORIG, s=7, label="reported (18–24 Sep)"); axs[0].scatter([], [], color=REP, s=7, label="replication (25–26 Sep)")
fig.legend(*axs[0].get_legend_handles_labels(), fontsize=8, frameon=False, loc="upper center", ncol=2)
fig.tight_layout(rect=(0, 0, 1, 0.95))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(RES, f"fig_replication.{ext}"), dpi=300)
print("wrote", os.path.join(RES, "fig_replication.{png,pdf}"))
