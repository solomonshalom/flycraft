#!/usr/bin/env python3
"""Encounter trials with error bars: female-female vs male-female, near (< 3.5 blocks) vs far, per trial.

Reads every logs/fly*_off-*.csv whose `trial` label starts with off_ff / off_mf, pairs the two flies of each
trial, and reports for the FEMALE of each pair (fly2 in mf, both flies in ff) the rejection DN (DNp13),
aggression, feeding and turning rates near vs far, plus contact ticks and rejection/attack events. Trials are
grouped by the brain's model variant, read from the log name: `off-flywire_<stamp>` = the published antennal lobe
(14u), `off-flywire-known-eln0.25_<stamp>` = the specific lobe (RESEARCH_NOTES 16-18).
The chamber is read from the trial label's suffix (trials.sh LABEL): none = the 17 Sep chamber with a faint flower
smell at its wall (18h) or, for the published lobe, the 14 Sep odor-free chamber (14u); `clean` = the world around the
origin wiped and checked (survey_chamber.js, 19b); `noise<Hz>` = clean + a background-noise walking substrate (19c).
Writes experiments/results/encounter_trials.csv and prints mean +/- sd over trials per variant, chamber and condition.
  python experiments/encounter_stats.py [--variant specific|published] [--chamber clean|noise0.2|...]
"""
import argparse, glob, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); LOGS = os.path.join(HERE, "..", "logs"); RES = os.path.join(HERE, "results")
ap = argparse.ArgumentParser(); ap.add_argument("--variant", default=None, help="only print this variant (the csv always has all)")
ap.add_argument("--chamber", default=None, help="only print this chamber (faint-smell | clean | noise<Hz>)")
ap.add_argument("--logs", nargs="+", default=[LOGS], help="directories searched for fly*_off-*.csv (default logs/; the 27 Sep arena edge series are in logs/edge_arena/<label>/)")
ap.add_argument("--out", default=os.path.join(RES, "encounter_trials.csv"))
a = ap.parse_args()
rows = []
for f in sorted(f for dd in a.logs for f in glob.glob(os.path.join(dd, "fly*_off-*.csv"))):
    try:
        d = pd.read_csv(f)
    except Exception:
        continue
    if len(d) < 50 or "trial" not in d or not str(d.trial.iloc[-1]).startswith("off_"):
        continue
    trial = str(d.trial.iloc[-1]); cond = trial.split("_")[1]; who = os.path.basename(f).split("_")[0]
    tag = os.path.basename(f).split("_")[1]                 # off-flywire[-known-eln0.25]
    ds = tag.split("-")[1]
    variant = "specific" if "eln0.25" in tag else "published"
    parts = trial.split("_")
    chamber = parts[3] if len(parts) > 3 else ("odor-free" if variant == "published" else "faint-smell")
    stamp = os.path.basename(f).rsplit("_", 1)[-1].replace(".csv", "")
    near = d.near_dist < 3.5
    contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
    starts = (contact & ~contact.shift(1, fill_value=False)); bouts = int(starts.sum())
    longest = int(contact.groupby((~contact).cumsum()).sum().max()) if contact.any() else 0          # ticks of the longest unbroken contact
    r = {"variant": variant, "chamber": chamber, "trial": trial, "condition": cond, "fly": who, "dataset": ds, "stamp": stamp, "brain_s": d.brain_t_ms.iloc[-1] / 1000, "ticks": len(d),
         "contact_bouts": bouts, "longest_bout_s": longest * 0.05, "first_contact_s": float(d.brain_t_ms[contact].iloc[0] / 1000) if contact.any() else np.nan,
         "odor_max": float(d[[c for c in d.columns if c.startswith("odor_")]].max().max()) if any(c.startswith("odor_") for c in d.columns) else 0.0,   # no odor_ column = no odorous block was ever in range
         "frac_near": float(near.mean()), "contact_ticks": int(contact.sum()), "median_dist": float(d.near_dist.median()),
         "walk": float(d.ctl_walk.mean()) if "ctl_walk" in d else np.nan,
         "path_blocks": float(((d.x.diff() ** 2 + d.z.diff() ** 2) ** 0.5).sum()) if {"x", "z"} <= set(d.columns) else np.nan}
    for k in ("hz_reject", "hz_aggression", "hz_feed", "hz_turn_L", "hz_turn_R", "hz_sing", "hz_court_p1", "hz_back", "hz_jump", "hz_accept", "hz_egg", "hz_sag"):
        if k in d:
            r[f"{k[3:]}_all"] = float(d[k].mean())
            r[f"{k[3:]}_near"] = float(d.loc[near, k].mean()) if near.any() else np.nan
            r[f"{k[3:]}_far"] = float(d.loc[~near, k].mean()) if (~near).any() else np.nan
            r[f"{k[3:]}_contact"] = float(d.loc[contact, k].mean()) if contact.any() else np.nan
    for k in ("ctl_reject", "ctl_attack", "ctl_feed", "ctl_sing", "ctl_jump", "ctl_accept", "ctl_egg"):
        if k in d:
            r[f"{k[4:]}_events_per_min"] = float(d[k].astype(bool).sum() / max(r["brain_s"] / 60, 1e-9))
            r[f"{k[4:]}_events_near"] = int((d[k].astype(bool) & near).sum())
    rows.append(r)
df = pd.DataFrame(rows)
if df.empty:
    print("no trial logs found"); raise SystemExit
out = a.out; df.to_csv(out, index=False)
pd.set_option("display.width", 220)
for (variant, chamber), dv in df.groupby(["variant", "chamber"]):
    if (a.variant and variant != a.variant) or (a.chamber and chamber != a.chamber):
        continue
    print(f"\n#### antennal lobe: {variant}; chamber: {chamber} (strongest flower odor reported by any fly: {dv.odor_max.max():.2f})")
    fem = dv[dv.dataset == "flywire"]
    for cond, sub in fem.groupby("condition"):
        print(f"\n== {cond}: female flies, {sub.trial.nunique()} trials, {len(sub)} fly-logs, brain time {sub.brain_s.mean():.0f} +/- {sub.brain_s.std():.0f} s; "
              f"walk duty {sub.walk.mean():.2f}, path {sub.path_blocks.mean():.0f} blocks")
        print(f"   near (<3.5 blocks) {sub.frac_near.mean()*100:.1f} +/- {sub.frac_near.std()*100:.1f} % of ticks; contact ticks {sub.contact_ticks.mean():.1f} +/- {sub.contact_ticks.std():.1f} "
              f"= {(sub.contact_ticks / sub.ticks).mean()*100:.1f} % of the trial (fly-logs with contact: {int((sub.contact_ticks > 0).sum())}/{len(sub)}; trials: {sub[sub.contact_ticks > 0].trial.nunique()}/{sub.trial.nunique()}); "
              f"bouts per log {sub.contact_bouts.mean():.1f}, longest {sub.longest_bout_s.max():.1f} s, first contact at {sub.first_contact_s.min():.1f} s; median distance {sub.median_dist.mean():.1f}")
        for k in ("reject", "aggression", "feed", "turn_L", "turn_R", "back", "jump", "accept", "egg", "sag"):
            if f"{k}_near" in sub:
                print(f"   {k:10s} all {sub[f'{k}_all'].mean():6.2f}   near {sub[f'{k}_near'].mean():6.2f} +/- {sub[f'{k}_near'].std():5.2f}   far {sub[f'{k}_far'].mean():6.2f} +/- {sub[f'{k}_far'].std():5.2f}   contact {sub[f'{k}_contact'].mean():6.2f} Hz")
        for k in ("reject", "attack", "feed", "jump", "accept", "egg"):
            if f"{k}_events_per_min" in sub:
                print(f"   {k} events/min {sub[f'{k}_events_per_min'].mean():.2f} +/- {sub[f'{k}_events_per_min'].std():.2f} (near: {sub[f'{k}_events_near'].sum()} total)")
    male = dv[dv.dataset == "malecns"]
    if len(male):
        print(f"\n== male in mf: {len(male)} logs, brain {male.brain_s.mean():.0f} s; walk duty {male.walk.mean():.2f}, path {male.path_blocks.mean():.0f} blocks; "
              f"sing near {male.sing_near.mean():.2f} far {male.sing_far.mean():.2f} contact {male.sing_contact.mean():.2f} Hz; "
              f"court_p1 near {male.court_p1_near.mean():.2f} far {male.court_p1_far.mean():.2f}; aggression near {male.aggression_near.mean():.2f} far {male.aggression_far.mean():.2f}; "
              f"back near {male.back_near.mean():.2f} contact {male.back_contact.mean():.2f}; sing events/min {male.sing_events_per_min.mean():.1f}")
print("wrote", out)
