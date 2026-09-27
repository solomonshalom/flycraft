#!/usr/bin/env python3
"""Print versions of the paper's figures (WHATS_LEFT_FLY "until submission" item 2).  python experiments/figures_print.py
The screen figures of figures.py are kept; these are sized for a 183 mm (7.2 in) two-column page at 300 dpi, PNG + PDF:
  fig1_print_innate_map     the innate map, both sexes, the paper's model only (Fig 1)
  fig3_print_encounters     one trajectory panel per chamber and pairing, with the female's turning DNs and the distance (Fig 3)
  fig5_print_state_arm      the state arm, both sexes, state alone / + touch / + cVA + touch, both lobes side by side (Fig 5)
  fig7_print_sensitivity    the sensitivity tables, both sexes, the claims of Table 1 as columns (Fig 7)
  fig13_print_substrate     the walking substrate: 1 s calibration, 10 s steady state, the male (Fig 13)
  fig12_print_contact_stop  stop on contact across the sensitivity axis: female DNa and index, male MDN (Fig 12)
  fig2b_print_conditioning  conditioning with the fly's rule: drive retained, learning index, approach index (Fig 2b)
"""
import glob, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); LOGS = os.path.join(HERE, "..", "logs")
PAPER_F, PAPER_M = "shiu_min1+known+eln0.25", "all_min1+eln0.25"
plt.rcParams.update({"font.size": 6.5, "axes.titlesize": 7, "axes.labelsize": 6.5, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5})
VMAX = np.log10(151)


def save(fig, name):
    for ext in ("png", "pdf"):
        out = os.path.join(RES, f"{name}.{ext}"); fig.savefig(out, dpi=300, bbox_inches="tight"); print("wrote", out)
    plt.close(fig)


def letter(ax, s, x=-0.02, y=1.0):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=9, fontweight="bold", ha="right", va="bottom")


def heat(ax, m, cell_fs=4.4, lab_fs=5.6, xlab=True):
    im = ax.imshow(np.log10(np.maximum(m.to_numpy(dtype=float), 0) + 1), aspect="auto", cmap="magma", vmin=0, vmax=VMAX)
    ax.set_xticks(range(len(m.columns)))
    ax.set_xticklabels(m.columns if xlab else [""] * len(m.columns), rotation=60, ha="right", fontsize=lab_fs)
    ax.set_yticks(range(len(m))); ax.set_yticklabels(m.index, fontsize=lab_fs)
    ax.tick_params(length=1.5, pad=1.5)
    for i in range(len(m)):
        for j in range(len(m.columns)):
            v = m.iloc[i, j]
            if np.isfinite(v) and v >= 0.95:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=cell_fs, color="w" if v < 30 else "k")
    return im


OUT_SHORT = {"DNp13 reject": "DNp13", "PPL1 (punish DA)": "PPL1", "PAM (reward DA)": "PAM", "GF jump": "giant fiber", "MDN back": "MDN", "pC1d/e aggr": "pC1d/e", "aIPg aggr": "aIPg",
             "pC1a recept": "pC1a", "vpoEN/DN accept": "vpoEN/vpoDN", "oviDN egg": "oviDN", "P1/pC1 male": "P1", "pIP10 song cmd": "pIP10", "TN1 song": "TN1", "vPR6 song": "vPR6",
             "feed MNs": "feeding MNs", "KC": "Kenyon cells", "DN all": "all DNs"}
IN_SHORT = {"touch (all head bristles)": "touch (head bristles)", "cVA (Or67d/DA1)": "cVA (DA1)", "cVA-long (Or65a/DL3)": "cVA (DL3)", "contact pheromone (ppk23/25)": "contact pheromone (ppk23/25)",
            "ppk25 only (female CHC)": "ppk25 (female CHC)", "ppk23 only (male CHC)": "ppk23 (male CHC)", "song/sound (JO-A)": "song (JO-A)", "aversive odor (DA2/DL4)": "aversive odor (DA2/DL4)"}

# ------------------------------------------------------------------ Fig 1 print: innate map, paper's model, both sexes
COLS_F = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "MN9", "pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "oviDN egg", "PAM (reward DA)", "PPL1 (punish DA)", "KC"]
COLS_M = ["DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "DNp13 reject", "feed MNs", "MN9", "leg MNs", "wing MNs", "song MNs", "P1/pC1 male", "pIP10 song cmd", "TN1 song", "aIPg aggr", "vpoEN/DN accept", "PAM (reward DA)", "PPL1 (punish DA)", "KC"]
pf = pd.read_csv(os.path.join(RES, f"social_probe_flywire_{PAPER_F}_noise0.csv")); pm = pd.read_csv(os.path.join(RES, f"social_probe_malecns_{PAPER_M}_noise0.csv"))
mf = pf[pf.input != "none"].groupby("input", sort=False)[[c for c in COLS_F if c in pf.columns]].mean(); mm = pm[pm.input != "none"].groupby("input", sort=False)[[c for c in COLS_M if c in pm.columns]].mean()
for m in (mf, mm):
    m.index = [IN_SHORT.get(i, i) for i in m.index]; m.columns = [OUT_SHORT.get(c, c) for c in m.columns]
fig = plt.figure(figsize=(7.2, 9.4)); gs = GridSpec(2, 1, figure=fig, height_ratios=[len(mf), len(mm)], hspace=0.42)
ax1 = fig.add_subplot(gs[0]); im = heat(ax1, mf); letter(ax1, "a"); ax1.set_title(f"female (FlyWire), the paper's model, {pf.seed.nunique()} seeds", loc="left", pad=3)
ax2 = fig.add_subplot(gs[1]); heat(ax2, mm); letter(ax2, "b"); ax2.set_title(f"male (MaleCNS), the paper's model, {pm.seed.nunique()} seeds", loc="left", pad=3)
cb = fig.colorbar(im, ax=[ax1, ax2], fraction=0.012, pad=0.01); cb.set_label("rate (Hz), log scale"); cb.set_ticks([0, np.log10(2), np.log10(6), np.log10(11), np.log10(31), np.log10(101)]); cb.set_ticklabels(["0", "1", "5", "10", "30", "100"]); cb.ax.tick_params(labelsize=5.5, length=1.5)
save(fig, "fig1_print_innate_map")

# ------------------------------------------------------------------ Fig 5 print: state arm, both lobes, both sexes
STATE_SHORT = {"none": "no state", "virgin (SAG tonic)": "SAG (virgin)", "fed (IPC tonic)": "IPC (fed)", "fed (DH44 tonic)": "DH44 (fed)", "hungry (NPF tonic)": "NPF (hungry)", "SIFa tonic": "SIFa", "AstA tonic": "AstA",
               "aroused female (pC1a-c tonic)": "pC1a-c (aroused)", "aggressive female (pC1d/e tonic)": "pC1d/e (aggressive)", "aggressive female (aIPg tonic)": "aIPg (aggressive)", "courting male (P1/pC1 tonic)": "P1 (courting)"}
INPUTS5 = ["none", "touch (all head bristles)", "cVA + touch"]; INP_SHORT5 = {"none": "alone", "touch (all head bristles)": "+ touch", "cVA + touch": "+ cVA + touch"}
SCOLS_F = ["pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "oviDN egg", "DNa L", "DNa R", "DNp09", "MDN back", "GF jump", "feed MNs", "MN9", "PPL1 (punish DA)"]
SCOLS_M = ["P1/pC1 male", "pIP10 song cmd", "TN1 song", "song MNs", "wing MNs", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "DNa L", "DNa R", "leg MNs", "MDN back", "GF jump", "feed MNs", "MN9", "PPL1 (punish DA)"]


def state_matrix(path, cols):
    d = pd.read_csv(path); d = d[d.input.isin(INPUTS5)]
    d["row"] = [f"{STATE_SHORT.get(s, s)} {INP_SHORT5[i]}" for s, i in zip(d.state, d.input)]
    order = [f"{STATE_SHORT.get(s, s)} {INP_SHORT5[i]}" for s in dict.fromkeys(d.state) for i in INPUTS5]
    m = d.groupby("row")[[c for c in cols if c in d.columns]].mean().reindex(order); m.columns = [OUT_SHORT.get(c, c) for c in m.columns]
    return m, d.seed.nunique()


fig = plt.figure(figsize=(7.2, 9.6)); gs = GridSpec(2, 2, figure=fig, height_ratios=[30, 24], hspace=0.30, wspace=0.55)
panels = [("a", "female, published lobe", f"state_probe_flywire_shiu_min1_state30.csv", SCOLS_F), ("b", "female, the paper's model", f"state_probe_flywire_{PAPER_F}_state30.csv", SCOLS_F),
          ("c", "male, published lobe", "state_probe_malecns_all_min1_state30.csv", SCOLS_M), ("d", "male, the paper's model", f"state_probe_malecns_{PAPER_M}_state30.csv", SCOLS_M)]
for k, (let, title, name, cols) in enumerate(panels):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        continue
    ax = fig.add_subplot(gs[k // 2, k % 2]); m, ns = state_matrix(p, cols)
    if k % 2 == 1:
        m.index = [""] * len(m)                                        # the row labels are the left panel's
    im = heat(ax, m, cell_fs=4.0, lab_fs=5.2); letter(ax, let, x=-0.02 if k % 2 == 1 else -0.35); ax.set_title(f"{title} ({ns} seeds)", loc="left", pad=3)
    for r in range(3, len(m), 3):
        ax.axhline(r - 0.5, color="w", lw=0.5)
cb = fig.colorbar(im, ax=fig.axes, fraction=0.012, pad=0.01); cb.set_label("rate (Hz), log scale"); cb.set_ticks([0, np.log10(2), np.log10(6), np.log10(11), np.log10(31), np.log10(101)]); cb.set_ticklabels(["0", "1", "5", "10", "30", "100"]); cb.ax.tick_params(labelsize=5.5, length=1.5)
save(fig, "fig5_print_state_arm")

# ------------------------------------------------------------------ Fig 7 print: sensitivity, the claims of Table 1 as columns
COND_SHORT = {"baseline (env model options, all conns, 100 Hz, dt 0.2)": "the paper's model", "published model: Shiu signs, eLN x1": "published lobe (Shiu signs, eLN x1)", "published model: eLN x1": "published lobe (eLN x1)",
              "stimulus 150 Hz (Shiu default r_poi; the body's maximum)": "stimulus 150 Hz", "dt 0.1 ms (Brian2 default)": "dt 0.1 ms", "legacy numerics (first version)": "first-version numerics",
              "Zenodo table, top_nt signs, >= 5 synapses (first version)": "Zenodo table, >= 5 synapses", "Zenodo table, top_nt signs, all connections": "Zenodo table, all connections"}
PAIRS_F = [("sugar GRNs", "MN9"), ("touch (all head bristles)", "DNp13 reject"), ("cVA + touch", "DNp13 reject"), ("food + touch", "DNp13 reject"), ("touch (all head bristles)", "MDN back"),
           ("cVA (Or67d/DA1)", "DNa L"), ("cVA (Or67d/DA1)", "DNa R"), ("food odor", "DNa L"), ("food odor", "DNa R"), ("food odor", "GF jump"), ("sound (JO-B)", "GF jump"),
           ("food odor", "PPL1 (punish DA)"), ("food odor", "PAM (reward DA)"), ("food odor", "KC"), ("cVA (Or67d/DA1)", "DNp13 reject"), ("cVA (Or67d/DA1)", "pC1d/e aggr"), ("cVA (Or67d/DA1)", "aIPg aggr")]
PAIRS_M = [("sugar GRNs", "MN9"), ("cVA (Or67d/DA1)", "DNp13 reject"), ("ppk25 + touch", "DNp13 reject"), ("touch (all head bristles)", "MDN back"), ("contact pheromone (ppk23/25)", "MDN back"),
           ("contact pheromone (ppk23/25)", "song MNs"), ("contact pheromone (ppk23/25)", "PPL1 (punish DA)"), ("cVA (Or67d/DA1)", "DNa L"), ("cVA (Or67d/DA1)", "DNa R"), ("cVA (Or67d/DA1)", "PPL1 (punish DA)"),
           ("cVA (Or67d/DA1)", "KC"), ("cVA (Or67d/DA1)", "MN9"), ("cVA (Or67d/DA1)", "song MNs"), ("cVA (Or67d/DA1)", "P1/pC1 male"), ("cVA (Or67d/DA1)", "pIP10 song cmd"), ("sound (JO-B)", "GF jump"),
           ("food odor", "PPL1 (punish DA)"), ("food odor", "KC")]
IN7 = {"sugar GRNs": "sugar", "touch (all head bristles)": "touch", "cVA (Or67d/DA1)": "cVA", "contact pheromone (ppk23/25)": "ppk23/25", "sound (JO-B)": "JO-B", "food odor": "food", "cVA + touch": "cVA + touch", "food + touch": "food + touch", "ppk25 + touch": "ppk25 + touch"}


def sens_matrix(path, pairs):
    d = pd.read_csv(path).set_index("condition")
    cols = [f"{i} -> {o}" for i, o in pairs if f"{i} -> {o}" in d.columns]
    m = d[cols].copy(); m.columns = [f"{IN7.get(i, i)} → {OUT_SHORT.get(o, o)}" for i, o in pairs if f"{i} -> {o}" in d.columns]; m.index = [COND_SHORT.get(c, c) for c in m.index]
    return m


sf = sens_matrix(os.path.join(RES, f"sensitivity_flywire_{PAPER_F}.csv"), PAIRS_F); sm = sens_matrix(os.path.join(RES, f"sensitivity_malecns_{PAPER_M}.csv"), PAIRS_M)
fig = plt.figure(figsize=(7.2, 7.4)); gs = GridSpec(2, 1, figure=fig, height_ratios=[len(sf), len(sm)], hspace=0.95)
ax1 = fig.add_subplot(gs[0]); im = heat(ax1, sf, cell_fs=4.6, lab_fs=5.6); letter(ax1, "a", x=-0.36); ax1.set_title(f"female: {len(sf)} conditions x the claims of Table 1 (3 seeds, 600 ms)", loc="left", pad=3)
ax2 = fig.add_subplot(gs[1]); heat(ax2, sm, cell_fs=4.6, lab_fs=5.6); letter(ax2, "b", x=-0.36); ax2.set_title(f"male: {len(sm)} conditions (3 seeds, 600 ms)", loc="left", pad=3)
cb = fig.colorbar(im, ax=[ax1, ax2], fraction=0.012, pad=0.01); cb.set_label("rate (Hz), log scale"); cb.set_ticks([0, np.log10(2), np.log10(6), np.log10(11), np.log10(31), np.log10(101)]); cb.set_ticklabels(["0", "1", "5", "10", "30", "100"]); cb.ax.tick_params(labelsize=5.5, length=1.5)
save(fig, "fig7_print_sensitivity")

# ------------------------------------------------------------------ Fig 3 print: one trajectory per chamber and pairing
T = pd.read_csv(os.path.join(RES, "encounter_trials.csv"))
CHAMBERS = [("published", "odor-free", "published smell centre"), ("specific", "faint-smell", "faint flower smell"),
            ("specific", "clean", "clean box"), ("specific", "noise0.2", "clean box with the hum")]


# trials whose first contact was a launch artefact: run_pair.sh's 6-s stagger let fly1 walk onto fly2's start point, so the
# flies were never apart before touching (experiments/edge/arena_audit.py start_check, flag_placed; RESEARCH_NOTES 23c)
PLACEMENT_ARTEFACTS = {("faint-smell", "off_ff_t1"), ("faint-smell", "off_ff_t3")}


def pick(v, ch, c):
    fem = T[(T.variant == v) & (T.chamber == ch) & (T.condition == c) & (T.dataset == "flywire")]
    fem = fem[[(ch, tr) not in PLACEMENT_ARTEFACTS for tr in fem.trial]]
    if not len(fem):
        return None
    tr = fem.sort_values(["longest_bout_s", "path_blocks"], ascending=False).trial.iloc[0] if fem.longest_bout_s.max() > 0 else sorted(fem.trial.unique())[0]
    rows = T[(T.variant == v) & (T.chamber == ch) & (T.trial == tr)]
    files = {}
    for _, r in rows.iterrows():
        fs = glob.glob(os.path.join(LOGS, f"{r.fly}_off-*_{r.stamp}.csv"))
        if fs:
            files[r.fly] = (r.dataset, pd.read_csv(fs[0]))
    return tr, files


COL = {"flywire": "#1f77b4", "flywire2": "#9467bd", "malecns": "#d62728"}
fig = plt.figure(figsize=(7.2, 6.0)); gso = GridSpec(2, 1, figure=fig, hspace=0.42); gsi = [gso[k].subgridspec(2, 4, height_ratios=[1.35, 1.0], hspace=0.12, wspace=0.38) for k in range(2)]
for ri, c in enumerate(("ff", "mf")):
    for ci, (v, ch, title) in enumerate(CHAMBERS):
        got = pick(v, ch, c)
        axt = fig.add_subplot(gsi[ri][0, ci]); axs = fig.add_subplot(gsi[ri][1, ci])
        if got is None or len(got[1]) < 2:
            axt.axis("off"); axs.axis("off"); continue
        tr, files = got
        fly1, fly2 = files.get("fly1"), files.get("fly2")
        cx0 = np.mean([fly1[1].x.iloc[0], fly2[1].x.iloc[0]]); cz0 = np.mean([fly1[1].z.iloc[0], fly2[1].z.iloc[0]])
        axt.add_patch(plt.Rectangle((-6, -6), 13, 13, fill=False, ls="--", lw=0.5, color="0.6"))       # the chamber: blocks -6..6, walls at -6 and +7
        seen_f = 0
        for name, (ds, d) in (("fly1", fly1), ("fly2", fly2)):
            col = COL["malecns"] if ds == "malecns" else (COL["flywire"] if seen_f == 0 else COL["flywire2"]); seen_f += ds == "flywire"
            axt.plot(d.x, d.z, color=col, lw=0.6, alpha=0.85, label=("male" if ds == "malecns" else "female") + (" 1" if ds == "flywire" and c == "ff" and name == "fly1" else " 2" if ds == "flywire" and c == "ff" else ""))
            axt.plot(d.x.iloc[0], d.z.iloc[0], "o", color=col, ms=3, mew=0); axt.plot(d.x.iloc[-1], d.z.iloc[-1], "s", color=col, ms=3, mew=0)
        fem = fly2 if c == "mf" else fly1; dfem = fem[1]
        contact = (dfem.get("obs_taste_fly_female", 0).astype(float) + dfem.get("obs_taste_fly_male", 0).astype(float)) > 0
        if contact.any():
            axt.plot(dfem.x[contact], dfem.z[contact], ".", color="k", ms=1.5, mew=0, zorder=5, label="contact")
        axt.set_aspect("equal"); axt.set_xlim(-7.2, 8.2); axt.set_ylim(-7.2, 8.2); axt.set_xticks([]); axt.set_yticks([])
        for sp in axt.spines.values():
            sp.set_visible(False)
        lb = T[(T.variant == v) & (T.chamber == ch) & (T.trial == tr) & (T.dataset == "flywire")].longest_bout_s.max()   # the trial's longest meeting, as in the arena table
        axt.set_title(f"{title}\n{'two females' if c == 'ff' else 'male + female'}, trial {tr.split('_')[2][1:]}\n" + (f"longest meeting {lb:.1f} s" if lb > 0 else "no contact"), fontsize=5.4, loc="left", pad=2)
        if ri == 0 and ci == 0:
            axt.legend(loc="lower left", fontsize=5, frameon=True, framealpha=0.9, edgecolor="none", handlelength=1.2, borderaxespad=0.1)
        letter(axt, "abcdefgh"[ri * 4 + ci], x=0.0, y=1.02)
        t = dfem.brain_t_ms / 1000
        axs.plot(t, dfem.hz_turn_L.rolling(10, min_periods=1).mean(), color="#1f77b4", lw=0.6, label="left")
        axs.plot(t, dfem.hz_turn_R.rolling(10, min_periods=1).mean(), color="#ff7f0e", lw=0.6, label="right")
        if c == "mf":
            dm = fly1[1]; axs.plot(dm.brain_t_ms / 1000, dm.hz_back.rolling(10, min_periods=1).mean(), color="#d62728", lw=0.6, ls=":", label="male backing (MDN)")
        axs.set_ylim(0, max(45, float(np.nanmax(dfem.hz_turn_L.rolling(10, min_periods=1).mean().max())) * 1.05))
        ax2 = axs.twinx(); ax2.plot(t, dfem.near_dist, color="0.35", lw=0.5, label="distance"); ax2.set_ylim(0, 13); ax2.tick_params(labelsize=5, length=1.5)
        if contact.any():
            seg = np.flatnonzero(np.diff(np.r_[0, contact.astype(int).to_numpy(), 0]))
            for s0, s1 in zip(seg[::2], seg[1::2]):
                axs.axvspan(t.iloc[s0], t.iloc[min(s1, len(t) - 1)], color="k", alpha=0.12, lw=0)
        axs.tick_params(labelsize=5, length=1.5); axs.set_xlabel("brain time (s)", labelpad=1)
        if ci == 0:
            axs.set_ylabel("female steering neurons (Hz)", labelpad=1)
        if ci == 3:
            ax2.set_ylabel("distance (blocks)", labelpad=1)
        if ri == 0 and ci == 0:
            h1, l1 = axs.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
            axs.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=4.8, frameon=True, framealpha=0.9, edgecolor="none", ncol=3, handlelength=1.2, borderaxespad=0.2)
        if ri == 1 and ci == 0:
            h1, l1 = axs.get_legend_handles_labels(); axs.legend(h1[2:], l1[2:], loc="upper right", fontsize=4.8, frameon=True, framealpha=0.9, edgecolor="none", handlelength=1.2, borderaxespad=0.2)
save(fig, "fig3_print_encounters")

# ------------------------------------------------------------------ Fig 13 print: the substrate, 1 s onset vs 10 s steady state, and the male
nf = pd.read_csv(os.path.join(RES, f"noise_floor_flywire_{PAPER_F}.csv")); nf10 = pd.read_csv(os.path.join(RES, f"noise_floor_flywire_{PAPER_F}_10s.csv"))
nm = pd.read_csv(os.path.join(RES, f"noise_floor_malecns_{PAPER_M}.csv")); nm10 = pd.read_csv(os.path.join(RES, f"noise_floor_malecns_{PAPER_M}_10s.csv"))
fig, axes = plt.subplots(1, 3, figsize=(7.2, 4.1), gridspec_kw={"wspace": 0.5})
ax = axes[0]
for inp, out, label, c in [("none", "DNa L", "DNa L, nothing to smell", "#1f77b4"), ("none", "DNa R", "DNa R, nothing to smell", "#ff7f0e"), ("none", "GF jump", "giant fiber, nothing", "#2ca02c"), ("none", "feed MNs", "feeding MNs, nothing", "#8c564b"),
                          ("none", "DNp13 reject", "DNp13, nothing", "#9467bd"), ("touch (all head bristles)", "DNp13 reject", "touch → DNp13", "#7f3c8d"), ("touch (all head bristles)", "DNa L", "touch → DNa L", "#17becf"), ("food odor", "DNa L", "food odor → DNa L", "#bcbd22"), ("sugar GRNs", "MN9", "sugar → MN9", "#e377c2")]:
    g = nf[nf.input == inp].groupby("noise_hz")[out]
    ax.errorbar(g.mean().index, g.mean().values, yerr=g.std().values, fmt="o-", ms=2.2, lw=0.7, capsize=1.5, elinewidth=0.5, label=label, color=c)
ax.set_xscale("symlog", linthresh=0.02); ax.axvline(0.2, color="0.5", ls="--", lw=0.6); ax.set_xlabel("background Poisson rate per neuron (Hz)"); ax.set_ylabel("rate (Hz)"); ax.set_title("a  female, 1 s from rest (3 seeds)", loc="left")
ax.legend(fontsize=4.8, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2), handlelength=1.4, columnspacing=0.6); ax.set_xticks([0, 0.02, 0.05, 0.1, 0.2, 0.5, 1]); ax.set_xticklabels(["0", "0.02", "0.05", "0.1", "0.2", "0.5", "1"])
ax = axes[1]
show = [("none", "DNa L", "DNa L, nothing", "#1f77b4"), ("none", "DNa R", "DNa R, nothing", "#ff7f0e"), ("touch (all head bristles)", "DNa L", "touch → DNa L", "#17becf"), ("none", "GF jump", "giant fiber", "#2ca02c"), ("none", "feed MNs", "feeding MNs", "#8c564b"), ("touch (all head bristles)", "DNp13 reject", "touch → DNp13", "#7f3c8d")]
xs = [0.1, 0.2, 0.3]
handles = []
for k, (inp, out, label, c) in enumerate(show):
    g1 = nf[nf.input == inp].groupby("noise_hz")[out].mean(); g10 = nf10[nf10.input == inp].groupby("noise_hz")[out]
    x1 = [x for x in xs if x in g1.index]; x10 = [x for x in xs if x in g10.mean().index]
    ax.plot([x - 0.008 for x in x1], g1.loc[x1].values, "o", color=c, ms=3, mfc="w", mew=0.8)
    ax.errorbar([x + 0.008 for x in x10], g10.mean().loc[x10].values, yerr=g10.std().loc[x10].values, fmt="s", color=c, ms=3, capsize=1.5, elinewidth=0.5)
    for x in xs:
        if x in g1.index and x in g10.mean().index:
            ax.annotate("", xy=(x + 0.008, g10.mean().loc[x]), xytext=(x - 0.008, g1.loc[x]), arrowprops=dict(arrowstyle="->", color=c, lw=0.5, shrinkA=2, shrinkB=2))
    handles.append(plt.Line2D([], [], color=c, marker="s", ls="", ms=3, label=label))
handles += [plt.Line2D([], [], color="k", marker="o", mfc="w", ls="", ms=3, label="1 s from rest"), plt.Line2D([], [], color="k", marker="s", ls="", ms=3, label="10 s steady state (2 seeds)")]
ax.set_xlim(0.06, 0.34); ax.set_xticks(xs); ax.set_xlabel("background rate (Hz per neuron)"); ax.set_ylabel("rate (Hz)"); ax.set_title("b  female: 1 s onset vs 10 s steady state", loc="left")
ax.legend(handles=handles, fontsize=4.8, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2), handlelength=1.4, columnspacing=0.6); ax.axvline(0.2, color="0.5", ls="--", lw=0.6)
ax = axes[2]
for inp, out, label, c in [("none", "leg MNs", "leg MNs, nothing", "#1f77b4"), ("none", "MDN back", "MDN, nothing", "#d62728"), ("none", "DNa L", "DNa L, nothing", "#17becf"), ("cVA (Or67d/DA1)", "DNp13 reject", "cVA → DNp13", "#9467bd"),
                          ("touch (all head bristles)", "MDN back", "touch → MDN", "#ff7f0e"), ("ppk25 + touch", "MDN back", "ppk25 + touch → MDN", "#8c564b"), ("contact pheromone (ppk23/25)", "MDN back", "ppk23/25 → MDN", "#2ca02c"), ("none", "P1/pC1 male", "P1, nothing", "k")]:
    g = nm[nm.input == inp].groupby("noise_hz")[out]
    ax.errorbar(g.mean().index, g.mean().values, yerr=g.std().values, fmt="o-", ms=2.2, lw=0.7, capsize=1.5, elinewidth=0.5, label=label, color=c)
    g10 = nm10[nm10.input == inp].groupby("noise_hz")[out]
    if len(g10.mean()):
        ax.plot(g10.mean().index + 0.012, g10.mean().values, "s", color=c, ms=3, mfc=c, mew=0)
ax.set_xscale("symlog", linthresh=0.05); ax.axvline(0.2, color="0.5", ls="--", lw=0.6); ax.set_xlabel("background Poisson rate per neuron (Hz)"); ax.set_ylabel("rate (Hz)"); ax.set_title("c  male: 1 s (circles), 10 s at 0.2 Hz (squares)", loc="left")
ax.legend(fontsize=4.8, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2), handlelength=1.4, columnspacing=0.6); ax.set_xticks([0, 0.1, 0.2, 0.3, 0.5]); ax.set_xticklabels(["0", "0.1", "0.2", "0.3", "0.5"])
save(fig, "fig13_print_substrate")


# ------------------------------------------------------------------ Fig 12 print: stop on contact across the sensitivity axis, both sexes
DRIVES12 = {"food odor": ("food odor", "#2ca02c"), "cVA (Or67d/DA1)": ("cVA", "#9467bd"), "Or47b (VA1v)": ("Or47b (fly odor)", "#8c564b"),
            "contact pheromone (ppk23/25)": ("ppk23/25 alone → ppk25 + bristles", "#d62728"), "none": ("substrate alone", "0.4")}
COND12 = {"paper's model: known signs, eLN x0.25": "paper's model (known signs, eLN ×0.25)", "published model: Shiu signs, eLN x1": "published lobe (Shiu signs, eLN ×1)",
          "Zenodo table, top_nt signs, >= 5 synapses (first version)": "Zenodo table, ≥ 5 synapses (first version)", "Zenodo table, top_nt signs, all connections": "Zenodo table, all connections",
          "paper's model: eLN x0.25": "paper's model (eLN ×0.25)", "published model: eLN x1": "published lobe (eLN ×1)"}


def rows12(d):
    """condition rows in file order; a substrate row is labelled by its suffix only, under its condition"""
    conds = list(dict.fromkeys(d.condition))
    return conds, ["+ 0.2 Hz substrate" if c.endswith(" + noise 0.2 Hz") else COND12.get(c, c.replace(" x", " ×")) for c in conds]


def rowaxis(ax, labels, show=True):
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels if show else [""] * len(labels), fontsize=5.6); ax.set_ylim(len(labels) - 0.5, -0.5)
    ax.tick_params(length=1.5, pad=1.5); ax.grid(axis="x", lw=0.3, color="0.85")
    for t in ax.get_yticklabels():
        if t.get_text().startswith("paper's"):
            t.set_fontweight("bold")
    for r in range(2, len(labels), 2):                                     # one band per condition: its row and its substrate row
        ax.axhline(r - 0.5, color="0.8", lw=0.4)


def dumbbell(ax, d, conds, a_col, t_col, drives, dy):
    """drive alone (open) -> drive + head bristles (filled), one line per condition x drive"""
    for i, c in enumerate(conds):
        sub = d[d.condition == c].set_index("drive")
        for k, drv in enumerate(drives):
            if drv not in sub.index:
                continue
            y = i + (k - (len(drives) - 1) / 2) * dy; col = DRIVES12[drv][1]; x0, x1 = sub.loc[drv, a_col], sub.loc[drv, t_col]
            ax.plot([x0, x1], [y, y], "-", color=col, lw=0.6, alpha=0.8)
            ax.plot(x0, y, "o", ms=2.6, mfc="w", mec=col, mew=0.6); ax.plot(x1, y, "o", ms=2.6, color=col, mew=0)


def fig12_print_contact_stop():
    cf, cm = pd.read_csv(os.path.join(RES, "contact_stop_flywire.csv")), pd.read_csv(os.path.join(RES, "contact_stop_malecns.csv"))
    df_, dm_ = [x for x in DRIVES12 if x in set(cf.drive)], [x for x in DRIVES12 if x in set(cm.drive)]
    conds_f, lab_f = rows12(cf); conds_m, lab_m = rows12(cm)
    fig = plt.figure(figsize=(7.2, 6.3))
    gs = GridSpec(2, 2, figure=fig, height_ratios=[len(conds_f), len(conds_m) + 1.5], width_ratios=[1.15, 1], left=0.27, right=0.985, top=0.96, bottom=0.07, hspace=0.26, wspace=0.05)
    axa, axb, axc, axl = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    z5 = [i for i, c in enumerate(conds_f) if ">= 5" in c]
    for ax in (axa, axb):
        for i in z5:
            ax.axhspan(i - 0.5, i + 0.5, color="#fde0dd", lw=0, zorder=0)
    dumbbell(axa, cf, conds_f, "DNa alone", "DNa +touch", df_, 0.17)
    rowaxis(axa, lab_f); axa.set_xlim(-0.8, 30.5); axa.set_xlabel("turning DNs DNa01/02, mean of both sides (Hz)", labelpad=1.5)
    letter(axa, "a", x=-0.02); axa.set_title("female (FlyWire): the turning DNs", loc="left", pad=3)
    for i, c in enumerate(conds_f):                                         # b: the suppression index; hollow = not driven (DNa alone < 2 Hz)
        sub = cf[cf.condition == c].set_index("drive")
        for k, drv in enumerate(df_):
            if drv not in sub.index or not np.isfinite(sub.loc[drv, "suppression"]):
                continue
            y = i + (k - (len(df_) - 1) / 2) * 0.17; col = DRIVES12[drv][1]; driven = sub.loc[drv, "DNa alone"] >= 2.0
            axb.plot(sub.loc[drv, "suppression"], y, "o", ms=2.8, mfc=col if driven else "w", mec=col, mew=0.6)
    axb.axvspan(0.5, 1.0, color="0.93", lw=0, zorder=0); axb.axvline(0, color="k", lw=0.5)
    rowaxis(axb, lab_f, show=False); axb.set_xlim(-2.05, 1.05); axb.set_xticks([-2, -1.5, -1, -0.5, 0, 0.5, 1])
    axb.set_xlabel("1 − DNa(+ touch) / DNa(alone)", labelpad=1.5)
    letter(axb, "b", x=-0.02); axb.set_title("female: suppression index", loc="left", pad=3)
    if z5:
        axb.text(-1.98, z5[0], "cVA, Or47b: DNa 0 → 12 Hz with touch", fontsize=4.8, color="#b2182b", va="center", ha="left")
    dumbbell(axc, cm, conds_m, "MDN back alone", "MDN back +touch", dm_, 0.15)
    rowaxis(axc, lab_m); axc.set_xlim(-0.8, 36); axc.set_xlabel("MDN, backward walking (Hz)", labelpad=1.5)
    letter(axc, "c", x=-0.02); axc.set_title("male (MaleCNS): MDN (backward walking)", loc="left", pad=3)
    axl.axis("off")
    hs = [plt.Line2D([], [], color=DRIVES12[x][1], marker="o", ls="-", lw=0.6, ms=3, label=DRIVES12[x][0]) for x in DRIVES12]
    hs += [plt.Line2D([], [], color="k", marker="o", mfc="w", mew=0.6, ls="", ms=3, label="a, c: the walking drive alone"),
           plt.Line2D([], [], color="k", marker="o", ls="", ms=3, label="a, c: drive + head bristles (100 Hz)"),
           plt.Line2D([], [], color="k", marker="o", mfc="w", mew=0.6, ls="", ms=3, label="b: hollow = DNa alone < 2 Hz (not driven)"),
           plt.Rectangle((0, 0), 1, 1, color="0.93", label="b: index > 0.5 (< 0 = the bristles excite)"),
           plt.Rectangle((0, 0), 1, 1, color="#fde0dd", label="the ≥ 5-synapse connection threshold")]
    axl.legend(handles=hs, loc="center left", fontsize=5.6, frameon=False, handlelength=1.8, title="walking drive (100 Hz, 600 ms, 5 seeds)", title_fontsize=5.8, alignment="left")
    save(fig, "fig12_print_contact_stop")


# ------------------------------------------------------------------ Fig 2b print: conditioning with the fly's rule, every design
def fig2b_print_conditioning():
    groups = {}
    for p in sorted(glob.glob(os.path.join(RES, "conditioning_*_seed*.csv"))):
        if p.endswith("_compartments.csv"):
            continue
        groups.setdefault(os.path.basename(p).replace("conditioning_", "").replace(".csv", "").rsplit("_seed", 1)[0], []).append(pd.read_csv(p, index_col=0))
    F, F1, M = f"flywire_{PAPER_F}_us-", "flywire_shiu_min1+known+eln0.1_us-", f"malecns_{PAPER_M}_us-"
    designs = [("appetitive\n50 Hz", F + "dan-reward"), ("appetitive\n20 Hz", F + "dan-reward-20hz"), ("appetitive\neLN ×0.1", F1 + "dan-reward"),
               ("aversive\n50 Hz", F + "dan-punish"), ("aversive\n20 Hz", F + "dan-punish-20hz"), ("aversive\neLN ×0.1", F1 + "dan-punish"),
               ("no US\n(wiring)", F + "wiring"), ("male\nappetitive", M + "dan-reward"), ("male\naversive", M + "dan-punish")]
    CSC = {"CS+": "#d62728", "CS-": "#1f77b4"}
    fig = plt.figure(figsize=(7.2, 5.6)); gs = GridSpec(4, 1, figure=fig, left=0.085, right=0.99, top=0.96, bottom=0.1, hspace=0.62)
    axs = [fig.add_subplot(gs[i]) for i in range(4)]
    ret = lambda d, comp, cs: float(d.loc[comp, f"post_{cs}"] / d.loc[comp, f"pre_{cs}"])
    xl = []
    for gi, (name, key) in enumerate(designs):
        runs = groups.get(key + "_vinegar-vs-ester", []) + groups.get(key + "_ester-vs-vinegar", [])
        xl.append(f"{name}\n(n = {len(runs)})")
        if not runs:
            continue
        taught = "drive punish-comp" if "punish" in key else "drive reward-comp"; other = "drive reward-comp" if "punish" in key else "drive punish-comp"
        for ax, comp in ((axs[0], taught), (axs[1], other)):
            for ci, cs in enumerate(("CS+", "CS-")):
                v = [ret(d, comp, cs) for d in runs]; x = gi + (ci - 0.5) * 0.36
                ax.bar(x, np.mean(v), width=0.34, yerr=np.std(v) if len(v) > 1 else 0, color=CSC[cs], alpha=0.8, error_kw=dict(lw=0.5, capsize=1.5, capthick=0.5))
                ax.plot([x] * len(v), v, ".", color="k", ms=2.2, mew=0)
        li = [ret(d, taught, "CS-") - ret(d, taught, "CS+") for d in runs]
        axs[2].bar(gi, np.mean(li), width=0.5, yerr=np.std(li) if len(li) > 1 else 0, color="0.6", error_kw=dict(lw=0.5, capsize=1.5, capthick=0.5))
        axs[2].plot([gi] * len(li), li, ".", color="k", ms=2.2, mew=0); axs[2].text(gi, max(np.mean(li) + np.std(li), 0) + 0.04, f"{np.mean(li):.2f}", ha="center", va="bottom", fontsize=5.4)
        ap_ = [(d.loc["approach", "post_CS+"] - d.loc["approach", "pre_CS+"]) - (d.loc["approach", "post_CS-"] - d.loc["approach", "pre_CS-"]) for d in runs]
        axs[3].errorbar(gi, np.mean(ap_), yerr=np.std(ap_) if len(ap_) > 1 else 0, fmt="s", color="0.3", ms=2.8, lw=0.6, capsize=1.5, capthick=0.5)
        axs[3].plot([gi + 0.18] * len(ap_), ap_, ".", color="k", ms=2.2, mew=0)
    titles = ["compartment that received the US: KC → MBON drive, post / pre", "the other compartment (no US delivered to it): drive retained, post / pre",
              "learning index = CS− retained − CS+ retained, taught compartment", "behaviour: change of the approach index (DNa L − R, odor on the left antenna), CS+ minus CS−, post − pre"]
    ylabels = ["post / pre", "post / pre", "learning index", "Δ approach (Hz)"]
    for i, ax in enumerate(axs):
        ax.set_xlim(-0.6, len(designs) - 0.4); ax.set_xticks(range(len(designs))); ax.set_xticklabels(xl if i == 3 else [""] * len(designs), fontsize=5.8)
        ax.tick_params(length=1.5, pad=1.5); ax.set_ylabel(ylabels[i], labelpad=1.5); letter(ax, "abcd"[i], x=-0.06); ax.set_title(titles[i], loc="left", pad=3)
        for xb in (5.5, 6.5):
            ax.axvline(xb, color="0.6", lw=0.5, ls=":")
    for ax in axs[:2]:
        ax.axhline(1, color="k", lw=0.5); ax.set_ylim(0, 1.12)
    axs[2].axhline(0, color="k", lw=0.5); axs[2].set_ylim(-0.05, 1.0); axs[3].axhline(0, color="k", lw=0.5)
    axs[0].legend(handles=[plt.Rectangle((0, 0), 1, 1, color=CSC["CS+"], alpha=0.8, label="CS+ (paired with the US)"), plt.Rectangle((0, 0), 1, 1, color=CSC["CS-"], alpha=0.8, label="CS−"),
                           plt.Line2D([], [], color="k", marker=".", ls="", ms=3, label="one run (seed × odor order)")], loc="lower right", bbox_to_anchor=(1.0, 1.0), fontsize=5.4, frameon=False, ncol=3, handlelength=1.2, borderaxespad=0.2)
    save(fig, "fig2b_print_conditioning")


fig12_print_contact_stop()
fig2b_print_conditioning()
