#!/usr/bin/env python3
"""Summarize brain logs: python experiments/analyze.py logs/*.csv"""
import sys
import pandas as pd

for path in sys.argv[1:]:
    d = pd.read_csv(path)
    n = len(d)
    if n == 0:
        print(path, "empty"); continue
    dur = d.brain_t_ms.iloc[-1] / 1000
    print(f"\n== {path}: {n} ticks, {dur:.1f} s brain time, mean wall {d.wall_ms.mean():.0f} ms/tick")
    rate_cols = [c for c in d.columns if c.startswith("hz_") and c not in ("hz_total_spikes", "hz_active_frac")]
    print("mean rates (Hz):", {c[3:]: round(float(d[c].mean()), 2) for c in rate_cols})
    drives = [c for c in ("ctl_walk", "ctl_back", "ctl_feed_drive", "ctl_aggr_drive", "ctl_song_drive") if c in d.columns]
    print("mean drives:", {c[4:]: round(float(d[c].mean()), 3) for c in drives}, " mean turn:", round(float(d.ctl_turn.mean()), 3), " mean |turn|:", round(float(d.ctl_turn.abs().mean()), 3))
    events = [c for c in ("ctl_jump", "ctl_attack", "ctl_feed", "ctl_sing", "ctl_court", "ctl_egg", "ctl_accept", "ctl_reject") if c in d.columns]
    print("events per minute of brain time:", {c[4:]: round(float(d[c].astype(bool).sum()) / max(dur / 60, 1e-9), 2) for c in events})
    if "ctl_forward" in d.columns:   # first-version logs
        print("control on-fraction:", {c[4:]: round(float(d[c].mean()), 3) for c in d.columns if c.startswith("ctl_") and c != "ctl_turn"})
    print("mean total spikes/tick:", round(d.hz_total_spikes.mean(), 0), " brain/wall time ratio:", round(dur / max((d.t_wall.iloc[-1] - d.t_wall.iloc[0]), 1e-9), 2) if "t_wall" in d else "")
    if "near_dist" in d and d.near_dist.notna().any():
        nd = d.near_dist.dropna()
        near = d.near_dist < 3.5
        print(f"other fly: median dist {nd.median():.1f}, frac < 3 blocks {(nd < 3).mean():.3f}, attacks while near {int((d.ctl_attack.astype(bool) & near).sum())}")
        for k in ("hz_aggression", "hz_reject", "hz_feed", "hz_sing", "hz_court_p1", "hz_turn_L", "hz_turn_R"):
            if k in d.columns and near.any() and (~near).any():
                print(f"   {k[3:]:10s} near {d.loc[near, k].mean():6.2f} Hz  far {d.loc[~near, k].mean():6.2f} Hz")
    if "pl_kc_mbon_w_frac" in d:
        print(f"KC->MBON weight fraction: start {d.pl_kc_mbon_w_frac.iloc[0]:.3f} end {d.pl_kc_mbon_w_frac.iloc[-1]:.3f}")
    if {"x", "z"} <= set(d.columns):
        path_len = ((d.x.diff() ** 2 + d.z.diff() ** 2) ** 0.5).sum()
        print(f"path length {path_len:.1f} blocks; bounding box x[{d.x.min():.0f},{d.x.max():.0f}] z[{d.z.min():.0f},{d.z.max():.0f}]")
