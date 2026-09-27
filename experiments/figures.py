#!/usr/bin/env python3
"""Paper figures from experiments/results and logs/.  python experiments/figures.py
Fig 1 innate maps (both sexes, mean +/- sd over seeds) · Fig 2 conditioning · Fig 3 arena encounters · Fig 4 gain
robustness · Fig 5 state arm · Fig 6 shuffled-connectome control · Fig 7 sensitivity · Fig 8 published anchors.
"""
import glob, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.ticker
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); LOGS = os.path.join(HERE, "..", "logs")
os.makedirs(RES, exist_ok=True)
META = {"input", "seed", "n_driven", "total_spikes", "active_frac", "wall_s", "state", "gain", "connectome", "shuffle", "frac_moved", "condition", "hz"}
DROP = {"KC", "MBON", "DN all", "leg MNs", "wing MNs", "mAL", "aSP-g", "SAG", "IPC", "aSP22"}


def heatmap(m, sd, title, out, fs=(13, None)):
    outs = list(m.columns)
    fig, ax = plt.subplots(figsize=(fs[0], fs[1] or 0.42 * len(m) + 2.2))
    im = ax.imshow(np.log10(m.to_numpy() + 1), aspect="auto", cmap="magma", vmin=0, vmax=np.log10(151))
    ax.set_xticks(range(len(outs))); ax.set_xticklabels(outs, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(m))); ax.set_yticklabels(m.index, fontsize=8)
    for i in range(len(m)):
        for j in range(len(outs)):
            v = m.iloc[i, j]; s = sd.iloc[i, j] if sd is not None else 0
            if v >= 1:
                ax.text(j, i, f"{v:.0f}" + (f"\n±{s:.0f}" if s >= 1 else ""), ha="center", va="center", fontsize=5.5, color="w" if v < 30 else "k")
    cb = fig.colorbar(im, ax=ax, fraction=0.02); cb.set_label("log10(Hz + 1)")
    ax.set_title(title, fontsize=10); fig.tight_layout(); fig.savefig(out, dpi=160); plt.close(fig); print("wrote", out)


# --- Fig 1: innate social sensorimotor map ------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "social_probe_*.csv"))):
    d = pd.read_csv(path)
    outs = [c for c in d.columns if c not in META and c not in DROP]
    g = d.groupby("input", sort=False)[outs]
    tag = os.path.basename(path).replace("social_probe_", "").replace(".csv", "")
    heatmap(g.mean(), g.std(), f"Fig 1 — innate sensorimotor map, {tag}: fixed connectome, 100 Hz input, 1 s, mean ± sd of {d.seed.nunique()} seeds", os.path.join(RES, f"fig1_social_map_{tag}.png"))

# --- Fig 2: conditioning -----------------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "conditioning_*.csv"))):
    if path.endswith("_compartments.csv"):
        continue
    d = pd.read_csv(path, index_col=0)
    keys = [k for k in ["MBON", "MBON reward-comp", "MBON punish-comp", "drive reward-comp", "drive punish-comp", "DNa L", "DNa R", "approach", "DN all", "feed MNs", "PAM", "PPL1"] if k in d.index]
    if not keys:
        continue
    fig, axes = plt.subplots(1, len(keys), figsize=(2.1 * len(keys), 3.2))
    for ax, k in zip(axes, keys):
        vals = [d.loc[k, "pre_CS+"], d.loc[k, "post_CS+"], d.loc[k, "pre_CS-"], d.loc[k, "post_CS-"]]
        ax.bar([0, 1, 2.5, 3.5], vals, color=["#bbb", "#d62728", "#bbb", "#1f77b4"])
        ax.set_xticks([0, 1, 2.5, 3.5]); ax.set_xticklabels(["pre", "post", "pre", "post"], fontsize=8)
        ax.set_title(k, fontsize=9); ax.set_ylabel("Hz", fontsize=8)
        ax.text(0.5, -0.32, "CS+ (paired w/ US)", transform=ax.transAxes, ha="center", fontsize=7, color="#d62728")
        ax.text(0.5, -0.42, "CS- (alone)", transform=ax.transAxes, ha="center", fontsize=7, color="#1f77b4")
    tag = os.path.basename(path).replace("conditioning_", "").replace(".csv", "")
    fig.suptitle(f"Fig 2 — in-silico appetitive conditioning, learning arm ({tag})", fontsize=10)
    fig.tight_layout(); out = os.path.join(RES, f"fig2_conditioning_{tag}.png"); fig.savefig(out, dpi=160); plt.close(fig); print("wrote", out)

# --- Fig 3: arena trajectories + neural traces for the latest two-fly runs --------------------------
from datetime import datetime
by_label = {}
for f in sorted(glob.glob(os.path.join(LOGS, "fly*_*.csv"))):
    stamp = f.rsplit("_", 1)[-1].replace(".csv", "")
    try:                                   # pair the two flies of a run by trial label and start time (their stamps can differ by a
        lab = str(pd.read_csv(f, usecols=["trial"], nrows=5).trial.iloc[0])    # second, across a minute boundary too)
        t0 = datetime.strptime(stamp, "%Y%m%d-%H%M%S")
    except Exception:
        continue
    by_label.setdefault(lab if lab != "nan" else "", []).append((t0, stamp, f))
runs = {}
for lab, items in by_label.items():
    items.sort()
    i = 0
    while i < len(items):
        if i + 1 < len(items) and (items[i + 1][0] - items[i][0]).total_seconds() <= 10:
            runs[f"{lab}_{items[i][1]}" if lab else items[i][1]] = [items[i][2], items[i + 1][2]]; i += 2
        else:
            i += 1
pairs = sorted(runs.items(), key=lambda kv: kv[0].rsplit("_", 1)[-1])
for stamp, fs in pairs[-5:]:
    ds = [pd.read_csv(f) for f in fs]
    if any(len(d) < 50 for d in ds): continue
    arm = os.path.basename(fs[0]).split("_")[1]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), gridspec_kw={"width_ratios": [1, 1.4, 1.4]})
    ax = axes[0]
    for d, c, name in zip(ds, ["#d62728", "#1f77b4"], [os.path.basename(f).split("_")[0] for f in fs]):
        ax.plot(d.x, d.z, c, lw=0.7, alpha=0.8, label=name); ax.plot(d.x.iloc[0], d.z.iloc[0], "o", color=c); ax.plot(d.x.iloc[-1], d.z.iloc[-1], "s", color=c)
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("z"); ax.legend(fontsize=8); ax.set_title(f"trajectories ({arm}, {stamp})", fontsize=9)
    ax = axes[1]
    d = ds[0]; t = d.brain_t_ms / 1000
    for k, c in [("hz_turn_L", "#d62728"), ("hz_turn_R", "#1f77b4"), ("hz_feed", "#2ca02c"), ("hz_aggression", "k"), ("hz_reject", "#9467bd"), ("hz_sing", "#ff7f0e")]:
        if k in d: ax.plot(t, d[k].rolling(10, min_periods=1).mean(), c, lw=0.9, label=k[3:])
    ax.set_xlabel("brain time (s)"); ax.set_ylabel("Hz (10-tick mean)"); ax.legend(fontsize=7, ncol=3); ax.set_title(f"{os.path.basename(fs[0]).split('_')[0]} readouts", fontsize=9)
    ax = axes[2]
    if "near_dist" in d:
        ax.plot(t, d.near_dist, "k", lw=0.8, label="distance to other fly"); ax.axhline(3, color="gray", ls="--", lw=0.6)
        ax2 = ax.twinx()
        if "ctl_walk" in d: ax2.plot(t, d.ctl_walk.rolling(10, min_periods=1).mean(), "#ff7f0e", lw=0.7, alpha=0.7, label="walk drive"); ax2.set_ylabel("walk drive", fontsize=8)
    ax.set_xlabel("brain time (s)"); ax.set_ylabel("blocks"); ax.set_title("proximity", fontsize=9); ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout(); out = os.path.join(RES, f"fig3_encounter_{arm}_{stamp}.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 4: gain robustness -------------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "gain_sweep_*.csv"))):
    d = pd.read_csv(path); ds = os.path.basename(path).replace("gain_sweep_", "").replace(".csv", "")
    outs = [c for c in d.columns if c not in META and c not in DROP]
    inputs = [i for i in d.input.unique() if i != "none"]
    ncol = (len(outs) + 1 + 1) // 2
    fig, axes = plt.subplots(2, ncol, figsize=(2.9 * ncol, 6.4)); axes = axes.ravel()
    for ax, k in zip(axes, outs + ["active_frac"]):
        for inp in inputs:
            sub = d[d.input == inp].groupby("gain")[k]
            ax.errorbar(sub.mean().index, sub.mean().values * (100 if k == "active_frac" else 1), yerr=sub.std().values * (100 if k == "active_frac" else 1), fmt="o-", ms=3, lw=1, capsize=2, label=inp)
        ax.set_xscale("log"); ax.set_xticks(sorted(d.gain.unique())); ax.set_xticklabels([f"{g:g}" for g in sorted(d.gain.unique())], fontsize=7)
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator()); ax.axvspan(0.7, 1.4, color="#eee", zorder=0)
        ax.set_title(k + (" (% neurons)" if k == "active_frac" else " (Hz)"), fontsize=9); ax.axvline(1.0, color="gray", lw=0.6, ls="--"); ax.tick_params(labelsize=7)
    for ax in axes[len(outs) + 1:]: ax.axis("off")
    axes[0].legend(fontsize=5.5, loc="upper left")
    fig.suptitle(f"Fig 4 — gain robustness ({ds}): responses vs per-synapse weight multiplier; shaded = the 0.7-1.4 window a result must survive", fontsize=10)
    fig.tight_layout(); out = os.path.join(RES, f"fig4_gain_{ds}.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 5: state arm ------------------------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "state_probe_*.csv"))):
    d = pd.read_csv(path); tag = os.path.basename(path).replace("state_probe_", "").replace(".csv", "")
    outs = [c for c in d.columns if c not in META and c not in DROP]
    d["cond"] = d.state + "  |  " + d.input
    g = d.groupby("cond", sort=False)[outs]
    heatmap(g.mean(), g.std(), f"Fig 5 — state arm ({tag}): tonic drive of the fly's own state neurons x social inputs, 1 s, mean ± sd of {d.seed.nunique()} seeds", os.path.join(RES, f"fig5_state_{tag}.png"), fs=(14, None))

# --- Fig 6: shuffled connectome control ------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "shuffle_*.csv"))):
    d = pd.read_csv(path); tag = os.path.basename(path).replace("shuffle_", "").replace(".csv", "")
    outs = [c for c in d.columns if c not in META and c not in DROP]
    d["cond"] = d.connectome.where(d.connectome == "intact", "shuffle " + d.shuffle.astype(str)) + "  |  " + d.input
    g = d.groupby("cond", sort=False)[outs]
    heatmap(g.mean(), g.std(), f"Fig 6 — degree-preserving shuffled connectome ({tag}): intact vs rewired ({d.frac_moved.max()*100:.0f} % of connections moved)", os.path.join(RES, f"fig6_shuffle_{tag}.png"), fs=(14, None))

# --- Fig 7: sensitivity -------------------------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "sensitivity_*.csv"))):
    d = pd.read_csv(path); tag = os.path.basename(path).replace("sensitivity_", "").replace(".csv", "")
    cols = [c for c in d.columns if " -> " in c and not c.endswith(" sd")]
    m = d.set_index("condition")[cols]; sd = d.set_index("condition")[[c + " sd" for c in cols]]; sd.columns = cols
    heatmap(m, sd, f"Fig 7 — sensitivity of key responses to our own choices ({tag})", os.path.join(RES, f"fig7_sensitivity_{tag}.png"), fs=(14, 0.5 * len(m) + 3))

# --- Fig 8: published anchors ------------------------------------------------------------------------
for path in sorted(glob.glob(os.path.join(RES, "benchmark_*.csv"))):
    d = pd.read_csv(path)
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.4))
    ax = axes[0]; sub = d[d.condition.str.startswith("sugar GRNs @")].groupby("hz")["MN9 L"]
    ax.errorbar(sub.mean().index, sub.mean().values, yerr=sub.std().values, fmt="o-", capsize=2); ax.set_xlabel("sugar GRN input (Hz)"); ax.set_ylabel("MN9 (Hz)"); ax.set_title("sugar -> MN9 (Shiu Fig 1)", fontsize=9)
    ax = axes[1]; rows = ["sugar 100 Hz alone", "sugar 100 Hz + bitter 25 Hz", "sugar 100 Hz + bitter 50 Hz", "sugar 100 Hz + bitter 100 Hz", "bitter 100 Hz alone"]
    vals = [d[d.condition == r]["MN9 L"].mean() for r in rows]; err = [d[d.condition == r]["MN9 L"].std() for r in rows]
    ax.bar(range(len(rows)), vals, yerr=err, capsize=2, color="#d62728"); ax.set_xticks(range(len(rows))); ax.set_xticklabels(["sugar", "+bitter 25", "+bitter 50", "+bitter 100", "bitter"], fontsize=7, rotation=20); ax.set_ylabel("MN9 (Hz)"); ax.set_title("bitter suppression", fontsize=9)
    ax = axes[2]; sub = d[d.condition.str.startswith("water GRNs @")].groupby("hz")["MN9 L"]
    ax.errorbar(sub.mean().index, sub.mean().values, yerr=sub.std().values, fmt="o-", capsize=2, color="#1f77b4"); ax.set_xlabel("water GRN input (Hz)"); ax.set_ylabel("MN9 (Hz)"); ax.set_title("water -> MN9", fontsize=9)
    ax = axes[3]; rows = ["JON-CE @ 100 Hz", "JON-F @ 100 Hz"]; vals = [d[d.condition == r]["aBN1"].mean() for r in rows]; err = [d[d.condition == r]["aBN1"].std() for r in rows]
    ax.bar([0, 1], vals, yerr=err, capsize=2, color=["#2ca02c", "#bbb"]); ax.set_xticks([0, 1]); ax.set_xticklabels(["JO-CE", "JO-F"]); ax.set_ylabel("aBN1 (Hz)"); ax.set_title("antennal grooming (validated in vivo)", fontsize=9)
    fig.suptitle("Fig 8 — published circuit results reproduced with Shiu et al.'s own neurons", fontsize=10)
    fig.tight_layout(); out = os.path.join(RES, "fig8_benchmark.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)


# --- Fig 2b: conditioning across seeds and reciprocal odor pairs (learning index) ---------------------
groups = {}
for path in sorted(glob.glob(os.path.join(RES, "conditioning_*_seed*.csv"))):
    if path.endswith("_compartments.csv"):
        continue
    base = os.path.basename(path).replace("conditioning_", "").replace(".csv", "")
    key = base.rsplit("_seed", 1)[0]
    groups.setdefault(key, []).append(pd.read_csv(path, index_col=0))
groups = {k: v for k, v in groups.items() if "us-" in k and "-vs-" in k}      # new-format runs only (14t's old file has no drive rows)
for fig_name, keys in (("fig2b_conditioning_summary", [k for k in groups if "phasic" not in k]), ("fig2c_conditioning_phasic", [k for k in groups if "phasic" in k])):
    if not keys:
        continue
    metrics = [("drive reward-comp", "KC->MBON drive, reward compartments\n(post/pre)", True), ("drive punish-comp", "KC->MBON drive, punishment compartments\n(post/pre)", True),
               ("MBON reward-comp", "reward-compartment MBONs (Hz, post-pre)", False), ("MBON punish-comp", "punishment-compartment MBONs (Hz, post-pre)", False),
               ("approach", "approach index DNa L-R,\nodor on left antenna (Hz, post-pre)", False)]
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.8 * len(metrics), 4.4))
    order = sorted(keys, key=lambda k: (("wiring" in k), ("punish" in k), k))
    for ax, (k, label, ratio) in zip(axes, metrics):
        xt, xl = [], []
        for gi, key in enumerate(order):
            runs = groups[key]
            for ci, cs in enumerate(("CS+", "CS-")):
                vals = []
                for d in runs:
                    if k not in d.index:
                        continue
                    pre, post = float(d.loc[k, f"pre_{cs}"]), float(d.loc[k, f"post_{cs}"])
                    vals.append((post / pre if pre > 0 else np.nan) if ratio else post - pre)
                vals = [v for v in vals if np.isfinite(v)]
                if not vals:
                    continue
                x = gi * 3 + ci
                ax.bar(x, np.mean(vals), yerr=np.std(vals) if len(vals) > 1 else 0, color="#d62728" if cs == "CS+" else "#1f77b4", alpha=0.85, capsize=3)
                ax.scatter([x] * len(vals), vals, color="k", s=8, zorder=3)
            us = key.split("us-")[1].split("_")[0].replace("dan-", "").replace("-phasic2", "") if "us-" in key else ""
            pair = key.split("_")[-1] if "-vs-" in key else key
            csp, csm = pair.split("-vs-") if "-vs-" in pair else (pair, "")
            var = key.split("_us-")[0]; var = var.split("+", 1)[1] if "+" in var else "published"      # model variant, shown when not the paper's
            xt.append(gi * 3 + 0.5); xl.append(f"US: {us}\n{csp}+ / {csm}-\n(n={len(runs)})" + (f"\n{var}" if var != "known+eln0.25" else ""))
        ax.set_xticks(xt); ax.set_xticklabels(xl, fontsize=6, rotation=45, ha="right"); ax.set_title(label, fontsize=8)
        ax.axhline(1 if ratio else 0, color="k", lw=0.5)
    title = "Fig 2b — conditioning with the fly's rule (US = identified DANs, or the wiring alone); red = CS+, blue = CS-; mean ± sd over seeds"
    if "phasic" in fig_name:
        title = "Fig 2c — same, with a phasic teaching signal (DAN rate above its 2 s running mean)"
    fig.suptitle(title, fontsize=10)
    fig.tight_layout(); out = os.path.join(RES, f"{fig_name}.png"); fig.savefig(out, dpi=160); plt.close(fig); print("wrote", out)

# --- Fig 9: does the model tell odors apart? antennal-lobe specificity and Kenyon-cell sparseness ------------
for path in sorted(glob.glob(os.path.join(RES, "odor_code_*.csv"))):
    if path.endswith("_overlap.csv"):
        continue
    d = pd.read_csv(path); tag = os.path.basename(path).replace("odor_code_", "").replace(".csv", "")
    ov = pd.read_csv(path.replace(".csv", "_overlap.csv"))
    variants = list(dict.fromkeys(d.variant))
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8))
    for ax, (col, label) in zip(axes[:3], [("glomeruli_over_10hz", "fraction of glomeruli with PNs > 10 Hz"), ("kc_active", "fraction of Kenyon cells active"), ("mbon_hz", "MBON mean rate (Hz)")]):
        for oi, odor in enumerate(dict.fromkeys(d.odor)):
            m = d[d.odor == odor].groupby("variant")[col].mean().reindex(variants)
            ax.plot(range(len(variants)), m.to_numpy(), marker="o", ms=3, lw=1, label=odor[:22])
        ax.set_xticks(range(len(variants))); ax.set_xticklabels(variants, rotation=30, ha="right", fontsize=7); ax.set_title(label, fontsize=9)
    axes[0].legend(fontsize=5.5, ncol=2)
    ax = axes[3]
    same = ov[ov.same_odor].groupby("variant").jaccard.mean().reindex(variants); diff = ov[~ov.same_odor].groupby("variant").jaccard.mean().reindex(variants)
    ax.plot(range(len(variants)), same.to_numpy(), marker="o", label="same odor, other seed"); ax.plot(range(len(variants)), diff.to_numpy(), marker="s", label="different odors")
    ax.set_xticks(range(len(variants))); ax.set_xticklabels(variants, rotation=30, ha="right", fontsize=7); ax.set_title("KC active-set overlap (Jaccard)", fontsize=9); ax.legend(fontsize=7); ax.set_ylim(0, 1.05)
    fig.suptitle(f"Fig 9 — odor identity through the model ({tag}): published signs vs known signs vs eLN output scale (single glomeruli + food blend, 100 Hz, 500 ms)", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, f"fig9_odor_code_{tag}.png"); fig.savefig(out, dpi=160); plt.close(fig); print("wrote", out)


# --- Fig 10: odor concentration sweep (chemotaxis sign, giant fiber, dopamine vs ORN rate) ---------------------------
for path in sorted(glob.glob(os.path.join(RES, "odor_dose_*.csv"))):
    d = pd.read_csv(path); tag = os.path.basename(path).replace("odor_dose_", "").replace(".csv", "")
    odors = list(dict.fromkeys(d.odor))
    if "approach (ipsi-contra)" in d.columns and (d.side == "R").any():        # steering = mean of the left and right presentations; bias = half their difference
        piv = d.pivot_table(index=["odor", "hz", "seed"], columns="side", values="approach (ipsi-contra)")
        d = d.merge(((piv["L"] + piv["R"]) / 2).rename("steering (ipsi-contra, L&R mean)").reset_index(), on=["odor", "hz", "seed"], how="left")
        d = d.merge(((piv["L"] - piv["R"]) / 2).rename("fixed left bias").reset_index(), on=["odor", "hz", "seed"], how="left")
        panels = [("steering (ipsi-contra, L&R mean)", "L", "steering: ipsi - contra DNa,\nmean of left and right odor (Hz)"), ("fixed left bias", "L", "fixed turning bias\n(half the L-R difference, Hz)"), ("DNa L", "both", "DNa L, bilateral odor (Hz)"), ("DNa R", "both", "DNa R, bilateral odor (Hz)"),
                  ("GF jump", "both", "giant fiber (Hz)"), ("PPL1 (punish DA)", "both", "PPL1 (Hz)"), ("KC active %", "both", "Kenyon cells active (%)"), ("active_frac", "both", "brain active (fraction)")]
    else:
        panels = [("approach (L-R)", "L", "approach index DNa L - R,\nodor on the LEFT antenna (Hz)"), ("DNa L", "both", "DNa L, bilateral odor (Hz)"), ("DNa R", "both", "DNa R, bilateral odor (Hz)"),
              ("GF jump", "both", "giant fiber (Hz)"), ("PPL1 (punish DA)", "both", "PPL1 (Hz)"), ("PAM (reward DA)", "both", "PAM (Hz)"),
              ("KC active %", "both", "Kenyon cells active (%)"), ("active_frac", "both", "brain active (fraction)")]
    fig, axes = plt.subplots(2, 4, figsize=(16, 7)); axes = axes.ravel()
    for ax, (col, side, label) in zip(axes, panels):
        for odor in odors:
            sub = d[(d.odor == odor) & (d.side == side)].groupby("hz")[col]
            if len(sub.mean()):
                ax.errorbar(sub.mean().index, sub.mean().values, yerr=sub.std().values, fmt="o-", ms=3, lw=1, capsize=2, label=odor)
        ax.set_title(label, fontsize=9); ax.set_xlabel("ORN rate (Hz)", fontsize=8); ax.tick_params(labelsize=7)
        if col in ("approach (L-R)", "steering (ipsi-contra, L&R mean)", "fixed left bias"):
            ax.axhline(0, color="k", lw=0.5)
    axes[0].legend(fontsize=6)
    fig.suptitle(f"Fig 10 — odor concentration sweep ({tag}): steering sign, giant fiber, dopamine and Kenyon cells vs ORN rate (150 Hz = the body's maximum); mean ± sd of {d.seed.nunique()} seeds", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, f"fig10_odor_dose_{tag}.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 11: can the memory be expressed? tonic drive on the MBON targets x MBON silencing --------------------------
for path in sorted(glob.glob(os.path.join(RES, "expression_probe_*.csv"))):
    d = pd.read_csv(path); tag = os.path.basename(path).replace("expression_probe_", "").replace(".csv", "")
    sets = list(dict.fromkeys(d.mbon_set))
    panels = [("approach (L-R)", "L", "approach index DNa L - R (odor left)"), ("DN all", "both", "all descending neurons (Hz)"), ("DNp09", "both", "DNp09 (Hz)"),
              ("MDN back", "both", "MDN (Hz)"), ("feed MNs", "both", "feeding MNs (Hz)"), ("targets Hz", "both", "the MBONs' targets (Hz)"), ("active_frac", "both", "brain active (fraction)")]
    fig, axes = plt.subplots(len(sets), len(panels), figsize=(2.9 * len(panels), 3.3 * len(sets)), squeeze=False)
    for i, sname in enumerate(sets):
        for ax, (col, side, label) in zip(axes[i], panels):
            for state, c in (("intact", "#1f77b4"), ("silenced", "#d62728")):
                sub = d[(d.mbon_set == sname) & (d.mbons == state) & (d.odor == side)].groupby("tonic_hz")[col]
                ax.errorbar(sub.mean().index, sub.mean().values, yerr=sub.std().values, fmt="o-", ms=3, lw=1, capsize=2, color=c, label=f"{sname}-compartment MBONs {state}")
                if col != "approach (L-R)":
                    sub0 = d[(d.mbon_set == sname) & (d.mbons == state) & (d.odor == "none")].groupby("tonic_hz")[col]
                    ax.plot(sub0.mean().index, sub0.mean().values, ":", color=c, lw=0.8, label=f"no odor, {state}")
            ax.set_title(label, fontsize=8); ax.set_xlabel("tonic drive on the MBONs' targets (Hz)", fontsize=7); ax.tick_params(labelsize=7)
        axes[i][0].legend(fontsize=5.5)
    fig.suptitle(f"Fig 11 — memory expression probe ({tag}): odor-evoked output with the compartment's MBONs intact vs silenced (= memory at its floor) as their targets receive tonic activity", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, f"fig11_expression_{tag}.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 3b: encounter statistics per antennal-lobe variant (female flies) ------------------------------------------
p = os.path.join(RES, "encounter_trials.csv")
if os.path.exists(p):
    d = pd.read_csv(p)
    if "variant" in d.columns:
        fem = d[d.dataset == "flywire"]
        metrics = [("walk", "walk duty"), ("frac_near", "near (< 3.5 blocks),\nfraction of ticks"), ("contact_ticks", "contact ticks per fly-log"), ("reject_far", "DNp13 far (Hz)"),
                   ("reject_near", "DNp13 near (Hz)"), ("reject_contact", "DNp13 on contact (Hz)"), ("reject_events_per_min", "rejection acts / min"), ("accept_all", "DNp37 acceptance (Hz),\nall ticks")]
        metrics = [m for m in metrics if m[0] in fem.columns]
        if "chamber" not in fem.columns:
            fem = fem.assign(chamber="")
        chambers = ["odor-free", "faint-smell", "clean"] + sorted(c for c in fem.chamber.unique() if str(c).startswith("noise"))
        groups = [(v, ch, c) for v in ("published", "specific") for ch in chambers for c in ("ff", "mf") if len(fem[(fem.variant == v) & (fem.chamber == ch) & (fem.condition == c)])]
        fig, axes = plt.subplots(1, len(metrics), figsize=(3.2 * len(metrics), 4.4))
        for ax, (k, label) in zip(axes, metrics):
            for gi, (v, ch, c) in enumerate(groups):
                sub = fem[(fem.variant == v) & (fem.chamber == ch) & (fem.condition == c)][k].dropna()
                ax.bar(gi, sub.mean() if len(sub) else 0, yerr=sub.std() if len(sub) > 1 else 0, color="#1f77b4" if c == "ff" else "#d62728", alpha=0.55 if v == "published" else 1.0, capsize=3)
                ax.scatter([gi] * len(sub), sub, color="k", s=8, zorder=3)
            short = {"odor-free": "odor-\nfree", "faint-smell": "faint\nsmell", "clean": "clean", "noise0.2": "noise\n0.2", "noise0.2-virgin": "n0.2\nvirgin"}
            ax.set_xticks(range(len(groups))); ax.set_xticklabels([f"{v[:4]}\n{short.get(ch, ch)}\n{c}" for v, ch, c in groups], fontsize=5.5); ax.set_title(label, fontsize=8); ax.tick_params(labelsize=7)
        fig.suptitle("Fig 3b — encounter trials, female flies: published vs specific antennal lobe, by chamber (odor-free 14u / faint flower smell 18h / clean 19b / clean + noise substrate 19c / the same with a virgin female 21); "
                     "female-female (blue) vs male-female (red); dots = fly-logs", fontsize=8)
        fig.tight_layout(); out = os.path.join(RES, "fig3b_encounter_summary.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 12: stop on contact across the sensitivity axis (RESEARCH_NOTES 19d) -----------------------------------------
for ds in ("flywire", "malecns"):
    p = os.path.join(RES, f"contact_stop_{ds}.csv")
    if not os.path.exists(p):
        continue
    d = pd.read_csv(p)
    drives = [x for x in ("food odor", "cVA (Or67d/DA1)", "Or47b (VA1v)", "contact pheromone (ppk23/25)", "none") if x in set(d.drive)]
    conds = list(dict.fromkeys(d.condition))
    fig, axes = plt.subplots(1, 3, figsize=(16, 0.32 * len(conds) + 2.5), gridspec_kw={"width_ratios": [1.3, 1, 1]})
    ax = axes[0]                                   # DNa with and without touch, per condition, one marker pair per drive
    for i, c in enumerate(conds):
        sub = d[d.condition == c]
        for k, drv in enumerate(drives):
            r = sub[sub.drive == drv]
            if not len(r):
                continue
            y = i + (k - len(drives) / 2) * 0.13
            ax.plot([r["DNa alone"].iloc[0], r["DNa +touch"].iloc[0]], [y, y], "-", color=f"C{k}", lw=1, alpha=0.8)
            ax.plot(r["DNa alone"].iloc[0], y, "o", color=f"C{k}", ms=4); ax.plot(r["DNa +touch"].iloc[0], y, "x", color=f"C{k}", ms=5)
    ax.set_yticks(range(len(conds))); ax.set_yticklabels(conds, fontsize=7); ax.invert_yaxis(); ax.set_xlabel("turning DNs DNa01/02, mean of both sides (Hz)\no = drive alone, x = drive + head bristles", fontsize=8)
    ax.legend(handles=[plt.Line2D([], [], color=f"C{k}", marker="o", ls="", ms=4, label=drv if drv != "none" else "substrate alone") for k, drv in enumerate(drives)], fontsize=7, loc="lower right"); ax.grid(axis="x", lw=0.3); ax.tick_params(labelsize=7)
    ax = axes[1]                                   # suppression index
    for k, drv in enumerate(drives):
        r = d[d.drive == drv].set_index("condition").reindex(conds)
        ax.plot(r.suppression, range(len(conds)), "o", color=f"C{k}", ms=4, label=drv)
    ax.axvline(0, color="k", lw=0.5); ax.axvspan(0.5, 1.0, color="#eee", zorder=0); ax.set_xlim(min(-1.2, np.floor(d.suppression.min() * 2) / 2 - 0.1), 1.05); ax.set_yticks(range(len(conds))); ax.set_yticklabels([]); ax.invert_yaxis()
    ax.set_xlabel("suppression index  1 - DNa(+touch) / DNa(alone)\n(shaded: > 0.5; negative = the bristles drive the DNa)", fontsize=8); ax.grid(axis="x", lw=0.3); ax.tick_params(labelsize=7)
    ax = axes[2]                                   # what else the bristles do: DNp13 (female) / MDN (male) with touch
    key = "MDN back +touch" if ds == "malecns" else "DNp13 reject +touch"
    for k, drv in enumerate(drives):
        r = d[d.drive == drv].set_index("condition").reindex(conds)
        ax.plot(r[key], range(len(conds)), "s", color=f"C{k}", ms=4)
    ax.set_yticks(range(len(conds))); ax.set_yticklabels([]); ax.invert_yaxis(); ax.set_xlabel(f"{key.replace(' +touch', '')} with the bristles on (Hz)", fontsize=8); ax.grid(axis="x", lw=0.3); ax.tick_params(labelsize=7)
    fig.suptitle(f"Fig 12 — stop on contact ({ds}): head-bristle input vs the turning DNs under every sign rule, eLN scale and connection table, with and without the 0.2 Hz walking substrate (5 seeds, 600 ms)", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, f"fig12_contact_stop_{ds}.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 13: the walking substrate calibrated (RESEARCH_NOTES 19c) --------------------------------------------------------
paths = sorted(glob.glob(os.path.join(RES, "noise_floor_*.csv")))
if paths:
    fig, axes = plt.subplots(1, len(paths), figsize=(7.5 * len(paths), 5.2), squeeze=False)
    for ax, p in zip(axes[0], paths):
        d = pd.read_csv(p); tag = os.path.basename(p).replace("noise_floor_", "").replace(".csv", "")
        show = [("none", "DNa L", "turning DNa L, no input"), ("none", "DNa R", "turning DNa R, no input"), ("none", "GF jump", "giant fiber, no input"), ("none", "feed MNs", "feeding MNs, no input"),
                ("none", "DNp13 reject", "DNp13, no input"), ("none", "leg MNs", "leg MNs, no input"), ("touch (all head bristles)", "DNp13 reject", "touch -> DNp13"), ("touch (all head bristles)", "DNa L", "touch -> DNa L"),
                ("touch (all head bristles)", "MDN back", "touch -> MDN"), ("food odor", "DNa L", "food -> DNa L"), ("sugar GRNs", "MN9", "sugar -> MN9"), ("cVA (Or67d/DA1)", "DNp13 reject", "cVA -> DNp13")]
        for inp, out, label in show:
            if inp not in set(d.input) or out not in d.columns:
                continue
            g = d[d.input == inp].groupby("noise_hz")[out]
            if g.mean().max() < 0.5:
                continue
            ax.errorbar(g.mean().index, g.mean().values, yerr=g.std().values, fmt="o-", ms=3, lw=1, capsize=2, label=label)
        ax.set_xscale("symlog", linthresh=0.02); ax.axvline(0.2, color="gray", ls="--", lw=0.8); ax.set_xlabel("background Poisson rate per neuron (Hz); dashed = the 0.2 Hz used in the arena", fontsize=8)
        ax.set_ylabel("Hz"); ax.set_title(tag, fontsize=9); ax.legend(fontsize=6, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.16)); ax.tick_params(labelsize=7)
    fig.suptitle("Fig 13 — the walking substrate calibrated: what background noise does alone (no input) and to the reflexes the answer table rests on (3 seeds, 1 s)", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, "fig13_noise_floor.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)

# --- Fig 14: the pre-contact slowing as a dose row (precontact_dose.py; RESEARCH_NOTES 20b) -----------------------------------
p = os.path.join(RES, "precontact_dose_flywire_shiu_min1+known+eln0.25.csv")
if os.path.exists(p):
    d = pd.read_csv(p); conds = list(dict.fromkeys(d.condition)); noises = sorted(d.noise_hz.unique())
    fig, axes = plt.subplots(2, len(noises), figsize=(6.8 * len(noises), 7.5), squeeze=False, sharex=True)
    for j, nz in enumerate(noises):
        s = d[d.noise_hz == nz]; g = s.groupby("condition", sort=False); m = g.mean(numeric_only=True).reindex(conds); sd = g.std(numeric_only=True).reindex(conds)
        x = np.arange(len(conds)); ax = axes[0][j]
        ax.errorbar(x - 0.12, m["DNa L"], yerr=sd["DNa L"], fmt="o", ms=4, capsize=2, color="#1f77b4", label="DNa L"); ax.errorbar(x + 0.12, m["DNa R"], yerr=sd["DNa R"], fmt="o", ms=4, capsize=2, color="#ff7f0e", label="DNa R")
        ax.plot(x, m["DNp09"], "s", ms=3, color="#2ca02c", label="DNp09"); ax.set_ylabel("Hz"); ax.set_title(f"substrate {nz:g} Hz: the female's turning DNs under the partner's odor at the levels the body reports", fontsize=9); ax.legend(fontsize=7); ax.grid(axis="y", lw=0.3)
        for k, cname in enumerate(conds):
            if cname.startswith("mf near") or cname.startswith("ff near"):
                ax.axvspan(k - 0.5, k + 0.5, color="#fff2cc", zorder=0)
        ax = axes[1][j]; ax.errorbar(x, m["walk duty"], yerr=sd["walk duty"], fmt="o", ms=4, capsize=2, color="k", label="walk duty (body readout)")
        ax2 = ax.twinx(); ax2.plot(x, m["GF jump"], "^", ms=3, color="#9467bd", label="giant fiber (Hz)"); ax2.plot(x, m["DNp13 reject"], "v", ms=3, color="#d62728", label="DNp13 (Hz)"); ax2.set_ylabel("Hz")
        ax.set_ylabel("walk duty"); ax.set_xticks(x); ax.set_xticklabels(conds, rotation=60, ha="right", fontsize=6.5); h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, fontsize=7); ax.grid(axis="y", lw=0.3)
    fig.suptitle(f"Fig 14 — pre-contact slowing as a dose row: bilateral cVA + Or47b + CO2 at the far (> 3.5 blocks) and near (1-3 blocks, shaded) levels of the arena; {d.settle_ms.iloc[0]/1000:g} s settle + {d.ms.iloc[0]/1000:g} s read, mean ± sd of {d.seed.nunique()} seeds", fontsize=9)
    fig.tight_layout(); out = os.path.join(RES, "fig14_precontact_dose.png"); fig.savefig(out, dpi=150); plt.close(fig); print("wrote", out)
