#!/usr/bin/env python3
"""Figure for the paper (draft 6, "The deciders stay quiet"): the female's decision neurons can fire, and the senses
tell them no (RESEARCH_NOTES 23; experiments/edge/analysis_A.md).

  a  the strongest rate each decider type reaches to any sense in any setting (26 inputs and combinations at gains
     0.7 / 1.0 / 1.4, at 200 and 300 Hz, and in the 14 versions of the female model; 3 seeds each), against its rate
     when its own five strongest input cell types are driven at 100 Hz (the positive control)
  b  what three senses do to each decider's membrane potential (mean over its neurons and 3 seeds, mV above rest;
     a neuron fires 7 mV above rest), gain 1.0
Reads experiments/results_edge/{gain-rate-map,sensmap,decider-reach,ei-deciders}/; writes
experiments/results_edge/figures/fig_deciders.{pdf,png} (paper/build.sh copies the pdf).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = _edge.EDGE_RESULTS
OUT = os.path.join(E, "figures"); os.makedirs(OUT, exist_ok=True)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"   # dataviz reference palette slots 1-3 and 7 (validated, light)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.linewidth": 0.6})

# decider types, top to bottom; the column that reads each in the grid_probe files
TYPES = [("pC1a", "pC1a", "pC1a"), ("pC1b", "pC1b", "pC1b"), ("pC1c", "pC1c", "pC1c"), ("pC1d", "pC1d", "pC1d"),
         ("pC1e", "pC1e", "pC1e"), ("aIPg", "aIPg aggr", "aIPg aggr"), ("vpoEN", "vpoEN", "vpoEN"),
         ("vpoDN (DNp37)", "vpoDN (DNp37)", "vpoDN (DNp37)"), ("oviDN", "oviDN egg", None)]

sens = pd.concat([pd.read_csv(os.path.join(E, "gain-rate-map", f)) for f in ("map_gain.csv", "map_rate.csv")] +
                 [pd.read_csv(os.path.join(E, "sensmap", "sensmap_flywire.csv"))], ignore_index=True)
sens = sens[sens.drive != "none"]
cond_keys = [c for c in ("label", "gain", "hz", "drive") if c in sens.columns]
reach = pd.read_csv(os.path.join(E, "decider-reach", "decider_reach.csv"))
ei = pd.read_csv(os.path.join(E, "ei-deciders", "ei_deciders_neurons.csv"))
ei = ei[ei.gain == 1.0]

rows = []
for name, col, eigroup in TYPES:
    by_cond = sens.groupby(cond_keys, dropna=False)[col].mean()           # mean over seeds, per condition x drive
    r = reach[reach.drive == f"{name} <- top5@100"][col].mean()
    v = {}
    for d, key in (("cVA (Or67d/DA1)", "cVA"), ("song/sound (JO-A)", "song"), ("touch (all head bristles)", "touch")):
        if eigroup is None:
            sel = ei[(ei.drive == d) & ei.group.isin(["oviDNa", "oviDNb"])]
        else:
            sel = ei[(ei.drive == d) & (ei.group == eigroup)]
        v[key] = sel.v_mean_mv.mean()
    rows.append({"type": name, "sense_max": float(by_cond.max()), "own_inputs": float(r), **v})
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "fig_deciders_data.csv"), index=False)
print(df.round(2).to_string(index=False))

fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"wspace": 0.55})
y = np.arange(len(df))[::-1]
for ax in (a, b):
    ax.set_yticks(y); ax.set_yticklabels(df.type); ax.tick_params(length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.5); ax.set_axisbelow(True)

# a: one row per decider, a light rule from 0 to the control value, two markers
for yi, (_, r) in zip(y, df.iterrows()):
    a.plot([0, r.own_inputs], [yi, yi], color=GRID, lw=1.2, zorder=1, solid_capstyle="round")
a.scatter(df.sense_max, y, s=26, color=ORANGE, marker="o", zorder=3, edgecolors="white", linewidths=0.6, label="strongest response to any sense, any setting")
a.scatter(df.own_inputs, y, s=26, color=BLUE, marker="D", zorder=3, edgecolors="white", linewidths=0.6, label="own five strongest inputs driven at 100 Hz")
for yi, (_, r) in zip(y, df.iterrows()):
    a.text(r.own_inputs + 3, yi, f"{r.own_inputs:.0f}", va="center", fontsize=6, color=INK2)
    a.text(max(r.sense_max, 0) - 3, yi, f"{r.sense_max:.1f}", va="center", ha="right", fontsize=6, color=INK2)
a.set_xlim(-14, 125); a.set_xlabel("firing rate (Hz)")
a.set_title("a   They can fire, but no sense makes them", loc="left", fontsize=7.5, fontweight="bold")
a.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), frameon=False, fontsize=6, ncol=1, handletextpad=0.3)

# b: membrane potential shift under three senses; rest at 0, firing at +7
b.axvline(0, color=INK2, lw=0.6); b.axvline(7, color=INK2, lw=0.8, ls=(0, (3, 2)))
b.text(7.2, y[0] + 0.55, "fires", fontsize=6, color=INK2, va="bottom"); b.text(0.2, y[0] + 0.55, "rest", fontsize=6, color=INK2, va="bottom")
for key, col, mk, off in (("cVA", ORANGE, "o", 0.18), ("song", AQUA, "s", 0.0), ("touch", VIOLET, "D", -0.18)):
    b.scatter(df[key], y + off, s=22, color=col, marker=mk, zorder=3, edgecolors="white", linewidths=0.6,
              label={"cVA": "the male's pheromone (cVA)", "song": "song (JO-A)", "touch": "touch on the head"}[key])
b.set_xlim(-19, 9); b.set_xlabel("membrane potential, mV above rest")
b.set_title("b   What the senses send them", loc="left", fontsize=7.5, fontweight="bold")
b.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), frameon=False, fontsize=6, ncol=1, handletextpad=0.3)

for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, f"fig_deciders.{ext}"), dpi=300, bbox_inches="tight")
print("wrote", os.path.join(OUT, "fig_deciders.pdf"))
