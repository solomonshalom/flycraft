#!/usr/bin/env python3
"""Compare a re-run of the offline groups with the result files it replaced (RESEARCH_NOTES 22).

For every csv present in both directories: identical (every numeric cell equal, timing columns ignored), or how it
differs (shape, columns, largest absolute difference and the cells behind it). Files only in one directory are listed.
  python experiments/compare_results.py --old release/pre_rerun_20260925/results --new experiments/results
Writes experiments/results/rerun_20260925_diff.md.
"""
import argparse, glob, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--old", required=True); ap.add_argument("--new", default=os.path.join(HERE, "results"))
ap.add_argument("--out", default=os.path.join(HERE, "results", "rerun_20260925_diff.md")); a = ap.parse_args()
TIMING = ("wall", "elapsed", "ms/run", "time_s", "runtime")
old = {os.path.basename(f): f for f in glob.glob(os.path.join(a.old, "*.csv"))}
new = {os.path.basename(f): f for f in glob.glob(os.path.join(a.new, "*.csv"))}
lines, same, differ = [], [], []
for name in sorted(set(old) & set(new)):
    o, n = pd.read_csv(old[name]), pd.read_csv(new[name])
    if os.path.getmtime(new[name]) <= os.path.getmtime(old[name]) + 1:
        continue                                                   # not rewritten by the re-run
    cols = [c for c in o.columns if c in n.columns and not any(t in c.lower() for t in TIMING)]
    if o.shape != n.shape or list(o.columns) != list(n.columns):
        differ.append((name, f"shape {o.shape} -> {n.shape}" + ("" if list(o.columns) == list(n.columns) else "; columns differ"))); continue
    num = [c for c in cols if pd.api.types.is_numeric_dtype(o[c]) and pd.api.types.is_numeric_dtype(n[c])]
    oth = [c for c in cols if c not in num]
    # rows may come out in another order (e.g. noise_floor.py merges into an existing file): align on the key columns
    keys = oth + [c for c in ("seed", "gain", "hz", "noise_hz", "shuffle", "ms", "settle_ms", "us_hz", "eln_scale") if c in num]
    if keys and not o.duplicated(keys).any() and not n.duplicated(keys).any():
        o = o.sort_values(keys, kind="mergesort").reset_index(drop=True); n = n.sort_values(keys, kind="mergesort").reset_index(drop=True)
    d = (o[num].astype(float) - n[num].astype(float)).abs()
    both_nan = o[num].isna() & n[num].isna()
    d = d.where(~both_nan, 0.0).fillna(np.inf)
    txt_diff = int(sum((o[c].astype(str) != n[c].astype(str)).sum() for c in oth))
    if (d.values == 0).all() and txt_diff == 0:
        same.append(name); continue
    worst = d.max().sort_values(ascending=False)
    ncell = int((d.values > 0).sum())
    differ.append((name, f"{ncell} of {d.size} numeric cells differ; largest |diff| " + ", ".join(f"{c} {v:.3g}" for c, v in worst.head(4).items() if v > 0)
                   + (f"; {txt_diff} text cells differ" if txt_diff else "")))
lines.append(f"# Re-run of {pd.Timestamp.now():%d %b %Y}: result files compared with the ones they replaced\n")
lines.append(f"Old: `{a.old}`; new: `{a.new}`. Timing columns ignored. Files not rewritten by the re-run are skipped.\n")
lines.append(f"**Identical to the digit: {len(same)} files.** Differ: {len(differ)} files.\n")
for name, why in differ:
    lines.append(f"- `{name}`: {why}")
lines.append("\nIdentical: " + ", ".join(f"`{s}`" for s in same))
only_old = sorted(set(old) - set(new)); only_new = sorted(set(new) - set(old))
if only_old: lines.append("\nOnly in the old directory: " + ", ".join(only_old))
if only_new: lines.append("\nOnly in the new directory: " + ", ".join(only_new))
open(a.out, "w").write("\n".join(lines) + "\n"); print("\n".join(lines)); print("wrote", a.out)
