#!/usr/bin/env python3
"""Arena log audit (edge suite S4; design_plan.md 2.7, DECISIONS.md): the 86-s bout, the 24/33 lean, replication comparability.

Log reads only (logs/fly*_off-*.csv; no connectome, no lock needed). Each log is classified as encounter_stats.py does
(variant from the log name, chamber and start configuration t1-t5 from the trial label), and fly1 is paired with fly2
per trial label with starts within 10 s, as figures.py does. Contact = obs_taste_fly_female + obs_taste_fly_male > 0
(the touch sense, < 1.3 blocks); one row = one 50-ms brain tick.
  0. reproduces the paper's numbers first (replication_stats.py): the turn-toward index per series, the pooled lean
     (mf 24 towards / 9 away of 35 logs that turn, p = 0.014) and the replication indices; a digit check.
  1. start_check (per trial): what fly1 did during run_pair.sh's 6-s launch stagger (`sleep 6` between the bots), the
     distance when fly2 was placed, flags for trials whose first contact came before both flies were present and more
     than 1.3 blocks apart, series numbers without them, and fly1's turning before / after its partner appears.
  2. lean_check (per female log, specific lobe): raw, far-bias-corrected, all-tick-corrected indices and the within-log
     side contrast; sign tests (Holm over mf/ff), cluster sign tests by start configuration, series and trial; circular
     time-shift nulls of near_az (within the pre-contact segment, and the whole log); lean vs sign(mean turn x mean side).
  3. body_speed (per log): wall-clock gap per row, displacement per unit walk by gap bin, stalled share, short logs.
Writes to --out-dir: start_check.csv, lean_check.csv, body_speed.csv, arena_audit.md, plus start_series.csv,
lean_tests.csv, body_speed_bins.csv and the sidecar arena_audit.json (verdicts under "verdicts").
  python experiments/edge/arena_audit.py --out-dir experiments/results_edge/arena-log-audit \
      [--results release/pre_rerun_20260926/results] [--logs logs [logs/edge_arena ...]] [--shifts 2000] [--seed 0] [--quick]
"""
from __future__ import annotations

import argparse, glob, os, re, sys
from datetime import datetime
from math import comb

import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge  # noqa: E402

COLS = ["t_wall", "brain_t_ms", "x", "z", "trial", "ctl_walk", "ctl_turn", "hz_turn_L", "hz_turn_R", "obs_taste_fly_female",
        "obs_taste_fly_male", "obs_smell_fly_L", "obs_smell_fly_R", "near_dist", "near_az"]
TICK_S = 0.05                        # brain time per row (encounter_stats: longest bout = ticks x 0.05)
TOUCH = 1.3                          # observe.js: obs_taste_fly_* = 1 within 1.3 blocks
NEAR, FAR = 6.0, 6.0                 # lean window (replication_stats.toward) and far ticks for the bias (near_dist >= 6)
PLAN_DIST, PLAN_ROWS = 3.0, 40       # design 2.7 flag: distance at fly2's first sensing < 3 and first contact within 40 rows
GAP_BINS = [0, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, np.inf]
STALL_GAP, STALL_SHARE, MIN_BRAIN_S = 0.8, 0.05, 60.0
ORDER = ["odor-free", "faint-smell", "clean", "noise0.2", "noise0.2-virgin"]   # replication_stats.SERIES order
REP_PREFIX = "rep-"                  # replication_stats.py --prefix default
QUICK_SERIES = "noise0.2"


def in_paper_pool(v):
    """replication_stats.main's pooled lean set: specific lobe, chambers faint-smell / clean / noise0.2 / noise0.2-virgin + rep-*"""
    return v["variant"] == "specific" and (v["chamber"] in ORDER[1:] or v["chamber"].startswith(REP_PREFIX))


# ---------------------------------------------------------------- small statistics
def signp(pos, neg):
    """two-sided exact sign test, as replication_stats.py"""
    n = pos + neg
    return min(1.0, 2 * sum(comb(n, k) for k in range(max(pos, neg), n + 1)) / 2 ** n) if n else np.nan


def holm(ps):
    """Holm-adjusted p for a dict name -> p (NaN left out)"""
    items = sorted((p, k) for k, p in ps.items() if np.isfinite(p)); m, run, out = len(items), 0.0, {}
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p)); out[k] = run
    return {k: out.get(k, np.nan) for k in ps}


def runs(b):
    """(start, length) of every run of True in a bool array"""
    x = np.diff(np.concatenate([[0], b.astype(np.int8), [0]]))
    s, e = np.flatnonzero(x == 1), np.flatnonzero(x == -1)
    return list(zip(s.tolist(), (e - s).tolist()))


def fmt(x, d=3, sign=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


# ---------------------------------------------------------------- logs, classification, pairing
def start_configs():
    """trials.sh POS: trial i starts at POS[(i-1) % 5] = fly1 pos, fly2 pos, fly1 yaw, fly2 yaw (Minecraft deg: 0 = +z, 90 = -x)"""
    txt = open(os.path.join(_edge.EXP, "trials.sh")).read()
    m = re.search(r"^POS=\((.*)\)$", txt, re.M)
    out = {}
    for i, s in enumerate(re.findall(r'"([^"]+)"', m.group(1)), 1):
        p1, p2, y1, y2 = s.split()
        (x1, _, z1), (x2, _, z2) = [tuple(map(float, p.split(","))) for p in (p1, p2)]
        face = lambda yaw, dx, dz: (-np.sin(np.radians(yaw)) * dx + np.cos(np.radians(yaw)) * dz) / np.hypot(dx, dz)
        out[f"t{i}"] = {"fly1": (x1, z1), "fly2": (x2, z2), "dist": float(np.hypot(x2 - x1, z2 - z1)),
                        "fly1_faces": round(float(face(float(y1), x2 - x1, z2 - z1)), 2), "fly2_faces": round(float(face(float(y2), x1 - x2, z1 - z2)), 2)}
    return out


def contact_of(d):
    """encounter_stats.py: female + male > 0, a NaN in either makes the tick non-contact (no fillna)"""
    c = np.zeros(len(d))
    for k in ("obs_taste_fly_female", "obs_taste_fly_male"):
        if k in d:
            c = c + d[k].astype(float).to_numpy()
    return c > 0


def load_logs(dirs, only_chambers=None, npos=5):
    """every fly*_off-*.csv that encounter_stats.py would keep, with its classification and per-log arrays; cfg = the
    trials.sh start position (t6 reuses POS[0]: trials.sh cycles POS[(i-1) % npos])"""
    L = {}
    for dd in dirs:
        for f in sorted(glob.glob(os.path.join(dd, "fly*_off-*.csv"))):
            try:
                d = pd.read_csv(f, usecols=lambda c: c in COLS)
            except Exception:
                continue
            if len(d) < 50 or "trial" not in d or not str(d.trial.iloc[-1]).startswith("off_"):
                continue
            base = os.path.basename(f); trial = str(d.trial.iloc[-1]); parts = trial.split("_")
            tag = base.split("_")[1]; variant = "specific" if "eln0.25" in tag else "published"
            chamber = parts[3] if len(parts) > 3 else ("odor-free" if variant == "published" else "faint-smell")
            if only_chambers and chamber not in only_chambers:
                continue
            stamp = base.rsplit("_", 1)[-1].replace(".csv", "")
            c = contact_of(d); first = int(np.argmax(c)) if c.any() else len(d)
            az = d.near_az.to_numpy(float); nd = d.near_dist.to_numpy(float); turn = d.ctl_turn.to_numpy(float)
            sel = (nd < NEAR) & ~np.isnan(az); sel[first:] = False
            mt = re.fullmatch(r"t(\d+)", parts[2]); cfg = f"t{(int(mt.group(1)) - 1) % npos + 1}" if mt else parts[2]
            L[base] = dict(file=f, base=base, d=d, trial=trial, label0=str(d.trial.iloc[0]), condition=parts[1], cfg=cfg,
                           fly=base.split("_")[0], dataset=tag.split("-")[1], tag=tag, variant=variant, chamber=chamber, stamp=stamp,
                           t0=datetime.strptime(stamp, "%Y%m%d-%H%M%S"), contact=c, first=first, has_contact=bool(c.any()),
                           az=az, nd=nd, turn=turn, sel=sel)
    return L


def pair_logs(L, fallback_s=60):
    """figures.py: group by trial label, sort by start stamp, pair neighbours <= 10 s apart; here also require fly1 + fly2.
    A second pass pairs what is left within fallback_s (a log's stamp is when its brain finished loading: in the loaded
    replication the male's came 12 s after the female's)"""
    by = {}
    for k, v in L.items():
        by.setdefault(v["trial"], []).append((v["t0"], v["fly"], k))
    pairs, rule, unpaired = {}, {}, []
    for lab, items in by.items():
        for win in (10, fallback_s):
            items.sort(); i = 0; left = []
            while i < len(items):
                if i + 1 < len(items) and (items[i + 1][0] - items[i][0]).total_seconds() <= win and {items[i][1], items[i + 1][1]} == {"fly1", "fly2"}:
                    a, b = (items[i], items[i + 1]) if items[i][1] == "fly1" else (items[i + 1], items[i])
                    tk = f"{lab}_{a[0]:%Y%m%d-%H%M%S}"; pairs[tk] = (a[2], b[2]); rule[tk] = f"<= {win} s"; i += 2
                else:
                    left.append(items[i]); i += 1
            items = left
        unpaired += [x[2] for x in items]
    for tk, (a, b) in pairs.items():
        L[a]["pair"] = L[b]["pair"] = tk
    return pairs, rule, unpaired


def series_key(vc):
    """(variant, chamber) in the paper's order: published first, then ORDER, each original before its rep- replication"""
    base = vc[1].replace("rep-", "")
    return (vc[0] != "published", ORDER.index(base) if base in ORDER else 99, vc[1].startswith("rep-"), vc[1])


def series_order(keys):
    return sorted(keys, key=series_key)


# ---------------------------------------------------------------- 0. the paper's numbers
def toward_pooled(logs):
    """replication_stats.toward: mean of turn x sign(az) over all pre-contact ticks < 6 blocks, pooled over the logs"""
    tw = np.concatenate([v["turn"][v["sel"]] * np.sign(v["az"][v["sel"]]) for v in logs]) if logs else np.array([])
    return (float(np.mean(tw)) if len(tw) else np.nan), len(tw)


def turned(v):
    return v["sel"].sum() > 0 and np.abs(v["turn"][v["sel"]]).sum() > 0


def pooled_lean(logs):
    """replication_stats.main, 'Leaning towards the partner': per-log index over logs that turn at all; sign test"""
    use = [v for v in logs if turned(v)]
    vals = np.array([np.mean(v["turn"][v["sel"]] * np.sign(v["az"][v["sel"]])) for v in use])
    tw = np.concatenate([v["turn"][v["sel"]] * np.sign(v["az"][v["sel"]]) for v in use]) if use else np.array([np.nan])
    ab = np.concatenate([np.abs(v["turn"][v["sel"]]) for v in use]) if use else np.array([np.nan])
    pos, neg = int((vals > 0).sum()), int((vals < 0).sum())
    return dict(logs=len(use), pos=pos, neg=neg, zero=len(use) - pos - neg, p=signp(pos, neg), index=float(np.mean(tw)),
                abs_turn=float(np.mean(ab)), ratio=float(np.mean(tw) / np.mean(ab)))


# the printed values: replication_20260925.md (release/pre_rerun_20260926/results) and flycraft.tex l.110 / l.153
PAPER_SERIES = {("specific", "clean", "ff"): ("+0.000", 26755), ("specific", "rep-clean", "ff"): ("+0.000", 15236),
                ("specific", "clean", "mf"): ("-0.021", 419), ("specific", "rep-clean", "mf"): ("+0.011", 121),
                ("specific", "noise0.2", "ff"): ("+0.002", 539), ("specific", "rep-noise0.2", "ff"): ("+0.028", 767),
                ("specific", "noise0.2", "mf"): ("+0.033", 1283), ("specific", "rep-noise0.2", "mf"): ("+0.012", 383),
                ("specific", "noise0.2-virgin", "mf"): ("-0.005", 668), ("specific", "rep-noise0.2-virgin", "mf"): ("+0.040", 349)}
PAPER_PUBLISHED = {"ff": "-0.19", "mf": "+0.08"}          # l.153, two decimals
PAPER_POOLED = {"mf": dict(logs="35", split="24 / 9", nonzero="33", p="0.014", index="+0.015", ratio="+0.06"),
                "ff": dict(logs="22", split="13 / 9", nonzero="22", p="0.523", index="+0.016", ratio="+0.06")}


# ---------------------------------------------------------------- 1. start check
def start_row(tk, a, b, cfgs):
    da, db = a["d"], b["d"]; tA, tB = da.t_wall.to_numpy(float), db.t_wall.to_numpy(float); t2 = tB[0]
    before = tA <= t2; nb = int(before.sum()); il = max(nb - 1, 0)
    xa, za, xb, zb = da.x.to_numpy(float), da.z.to_numpy(float), db.x.to_numpy(float), db.z.to_numpy(float)
    step = np.hypot(np.diff(xa[:il + 1]), np.diff(za[:il + 1]))
    s2 = np.flatnonzero(~np.isnan(b["nd"])); s1 = np.flatnonzero(~np.isnan(a["nd"]))
    fc1 = int(np.argmax(a["contact"])) if a["has_contact"] else -1; fc2 = int(np.argmax(b["contact"])) if b["has_contact"] else -1
    t_fc = min(tA[fc1] if fc1 >= 0 else np.inf, tB[fc2] if fc2 >= 0 else np.inf)
    has_c = np.isfinite(t_fc)
    # were both flies present and > 1.3 blocks apart at some moment before the trial's first contact? Evidence: the distance
    # at placement (below), and fly2's own readings from its row 1 on (row 0 can still be taken at fly2's pre-teleport spawn: rep-clean ff t5 reads 2.00
    # there against 5.66 from row 1)
    apart = (tB < t_fc) & (b["nd"] > TOUCH); apart[0] = False; i_apart = int(np.argmax(apart)) if apart.any() else -1
    # placement = when the later of the two brains logged its first row; each fly's position at its last row by then (with a
    # positive stagger: fly1's row il against fly2's row 0; with a negative one: fly1's row 0 against fly2's row by then)
    t_both = max(tA[0], t2)
    ia = max(int(np.searchsorted(tA, t_both, side="right")) - 1, 0); ib = max(int(np.searchsorted(tB, t_both, side="right")) - 1, 0)
    d_place = float(np.hypot(xa[ia] - xb[ib], za[ia] - zb[ib]))
    cfg = cfgs.get(a["cfg"], {})
    off = lambda x, z, p: float(np.hypot(x - p[0] - 0.5, z - p[1] - 0.5)) if p else np.nan
    r = dict(trial_key=tk, variant=a["variant"], chamber=a["chamber"], condition=a["condition"], trial=a["trial"], cfg=a["cfg"],
             fly1=a["base"], fly2=b["base"], fly1_dataset=a["dataset"], fly2_dataset=b["dataset"],
             cfg_dist=cfg.get("dist", np.nan), cfg_fly1_faces=cfg.get("fly1_faces", np.nan), cfg_fly2_faces=cfg.get("fly2_faces", np.nan),
             stagger_s=float(t2 - tA[0]), fly1_rows_before_fly2=nb,
             fly1_moved_before_fly2=float(np.hypot(xa[il] - xa[0], za[il] - za[0])) if nb else 0.0,
             fly1_path_before_fly2=float(step.sum()) if nb else 0.0,
             start_dist_logged=float(np.hypot(xa[0] - xb[0], za[0] - zb[0])),
             fly1_start_off=off(xa[0], za[0], cfg.get("fly1")), fly2_start_off=off(xb[0], zb[0], cfg.get("fly2")), dist_at_placement=d_place,
             fly2_first_sense_row=int(s2[0]) if len(s2) else -1, dist_at_fly2_first_sense=float(b["nd"][s2[0]]) if len(s2) else np.nan,
             fly1_first_sense_s=float(tA[s1[0]] - t2) if len(s1) else np.nan,
             fly1_first_contact_row=fc1, fly2_first_contact_row=fc2, first_contact_rel_fly2_s=float(t_fc - t2) if has_c else np.nan,
             fly2_first_apart_row=i_apart)
    r["apart_before_contact"] = bool(has_c and ((d_place > TOUCH and t_fc > t_both) or i_apart >= 0))
    r["flag_placed"] = bool(has_c and not r["apart_before_contact"])
    r["flag_plan"] = bool(np.isfinite(r["dist_at_fly2_first_sense"]) and r["dist_at_fly2_first_sense"] < PLAN_DIST and 0 <= fc2 <= PLAN_ROWS)
    for who, v in (("fly1", a), ("fly2", b)):
        rr = runs(v["contact"]); t = v["d"].t_wall.to_numpy(float)
        r[f"{who}_contact_pct"] = float(v["contact"].mean() * 100)
        if rr:
            s, n = max(rr, key=lambda x: x[1])
            r[f"{who}_longest_bout_s"] = n * TICK_S; r[f"{who}_longest_start_row"] = s; r[f"{who}_longest_start_rel_fly2_s"] = float(t[s] - t2)
            r[f"{who}_longest_is_first_bout"] = bool(s == rr[0][0])
            ok = (t >= t2) & (v["nd"] > TOUCH); ok[0] = ok[0] and who == "fly1"     # fly2's row 0 can be pre-teleport
            ap = np.flatnonzero(ok)                                  # bouts that begin after the flies were > 1.3 apart post-placement
            r[f"{who}_longest_after_apart_s"] = max([n_ * TICK_S for s_, n_ in rr if len(ap) and s_ > ap[0]], default=0.0)
        else:
            r[f"{who}_longest_bout_s"] = 0.0; r[f"{who}_longest_start_row"] = -1; r[f"{who}_longest_start_rel_fly2_s"] = np.nan
            r[f"{who}_longest_is_first_bout"] = False; r[f"{who}_longest_after_apart_s"] = 0.0
    lr = (da.hz_turn_L - da.hz_turn_R).to_numpy(float)
    r["fly1_turn_before"] = float(np.mean(a["turn"][before])) if nb else np.nan; r["fly1_turn_after"] = float(np.mean(a["turn"][~before]))
    r["fly1_LR_before_hz"] = float(np.mean(lr[before])) if nb else np.nan; r["fly1_LR_after_hz"] = float(np.mean(lr[~before]))
    return r


def series_table(L, S):
    """female logs per series (replication_stats.stats): trials with contact, contact %, longest bout; all / without flagged trials"""
    fl = {t: f for t, f in zip(S.trial_key, S.flag_placed)}; fp = {t: f for t, f in zip(S.trial_key, S.flag_plan)}
    rows = []
    fem = [v for v in L.values() if v["dataset"] == "flywire"]
    for vc in series_order({(v["variant"], v["chamber"]) for v in fem}):
        for cond in ("ff", "mf"):
            g = [v for v in fem if (v["variant"], v["chamber"], v["condition"]) == (*vc, cond)]
            if not g:
                continue
            for excl, keep in (("none", lambda v: True), ("placed", lambda v: not fl.get(v.get("pair"), False)),
                               ("plan", lambda v: not fp.get(v.get("pair"), False))):
                gg = [v for v in g if keep(v)]
                cp = np.array([v["contact"].mean() * 100 for v in gg])
                lb = [max([n for _, n in runs(v["contact"])], default=0) * TICK_S for v in gg]
                rows.append(dict(variant=vc[0], chamber=vc[1], condition=cond, excluded=excl, trials=len({v["trial"] for v in gg}),
                                 logs=len(gg), trials_contact=len({v["trial"] for v in gg if v["has_contact"]}),
                                 contact_pct_mean=float(cp.mean()) if len(cp) else np.nan, contact_pct_sd=float(cp.std(ddof=1)) if len(cp) > 1 else np.nan,
                                 longest_bout_s=float(max(lb)) if lb else np.nan,
                                 excluded_trials=";".join(sorted({v["trial"] for v in g} - {v["trial"] for v in gg}))))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 2. lean check
def lean_row(v):
    s, t, az, nd, c = v["sel"], v["turn"], v["az"], v["nd"], v["contact"]
    ts, sg = t[s], np.sign(az[s]); nL, nR = int((sg > 0).sum()), int((sg < 0).sum())
    far = (~c) & (nd >= FAR); b_far = float(np.mean(t[far])) if far.any() else np.nan; b_all = float(np.mean(t))
    r = dict(variant=v["variant"], chamber=v["chamber"], condition=v["condition"], trial=v["trial"], cfg=v["cfg"], fly=v["fly"],
             log=v["base"], trial_id=f"{v['chamber']}/{v['trial']}", pair=v.get("pair", ""), rows=len(t), first_contact_row=v["first"] if v["has_contact"] else -1,
             n_pre6=int(s.sum()), turned=bool(turned(v)), nL=nL, nR=nR, mean_turn_pre=float(ts.mean()) if len(ts) else np.nan,
             mean_side_pre=float(sg.mean()) if len(sg) else np.nan, n_far=int(far.sum()), b_far=b_far, b_all=b_all)
    r["idx_raw"] = float(np.mean(ts * sg)) if len(ts) else np.nan
    r["idx_farcorr"] = float(np.mean((ts - b_far) * sg)) if len(ts) and np.isfinite(b_far) else np.nan
    r["idx_allcorr"] = float(np.mean((ts - b_all) * sg)) if len(ts) else np.nan
    r["side_contrast"] = float((ts[sg > 0].mean() - ts[sg < 0].mean()) / 2) if nL >= 10 and nR >= 10 else np.nan
    r["bias_x_side"] = r["mean_turn_pre"] * r["mean_side_pre"] if len(ts) else np.nan
    r["idx_minus_bias_x_side"] = r["idx_raw"] - r["bias_x_side"] if len(ts) else np.nan
    if abs(r["idx_minus_bias_x_side"]) < 1e-12:                   # all ticks on one side: exactly 0 up to rounding
        r["idx_minus_bias_x_side"] = 0.0
    od = (v["d"].obs_smell_fly_L - v["d"].obs_smell_fly_R).to_numpy(float)[s] if "obs_smell_fly_L" in v["d"] else np.array([])
    m = np.abs(od) > 1e-6
    r["smell_side_agrees"] = float(np.mean(np.sign(od[m]) == sg[m])) if m.any() else np.nan
    return r


def sign_tests(D, idx, level):
    out = {}
    for cond in ("mf", "ff"):
        x = D[(D.condition == cond) & D.turned & D[idx].notna()]
        if level != "log":
            x = x.groupby(level)[idx].mean().reset_index()
        pos, neg = int((x[idx] > 0).sum()), int((x[idx] < 0).sum())
        out[cond] = dict(condition=cond, stat=idx, level=level, n=len(x), pos=pos, neg=neg, zero=len(x) - pos - neg,
                         mean=float(x[idx].mean()) if len(x) else np.nan, p=signp(pos, neg))
    h = holm({c: out[c]["p"] for c in out})
    for c in out:
        out[c]["p_holm"] = h[c]
    return list(out.values())


def shift_nulls(logs, D, shifts, seed):
    """circular shift of near_az (a) within the pre-contact segment, offset uniform over 10-90 % of its length, and (b) over
    the whole log, offset uniform over 10-90 % of the log; selection (pre-contact, < 6 blocks) and turn stay real. One rng per
    pairing x kind, default_rng(seed); the same draws serve the raw, far-corrected and all-corrected indices."""
    out = []
    bias = {r.log: (r.b_far, r.b_all) for r in D.itertuples()}
    for cond in ("mf", "ff"):
        use = [v for v in logs if v["condition"] == cond and turned(v)]
        if not use:
            continue
        for kind in ("within-pre", "whole-log"):
            rng = np.random.default_rng(seed)
            nul = {k: np.zeros((shifts, 2)) for k in ("raw", "farcorr", "allcorr")}
            prep = []
            for v in use:
                f = v["first"]; n = len(v["az"]); bf, ba = bias[v["base"]]
                span = f if kind == "within-pre" else n
                lo = max(1, span // 10); hi = max(lo + 1, span - span // 10)
                prep.append((v["az"][:f] if kind == "within-pre" else v["az"], v["sel"][:f] if kind == "within-pre" else v["sel"],
                             v["turn"][:f] if kind == "within-pre" else v["turn"], lo, hi, bf, ba))
            for it in range(shifts):
                vals = {k: [] for k in nul}
                for az, s, t, lo, hi, bf, ba in prep:
                    a = np.roll(az, int(rng.integers(lo, hi)))[s]; tt = t[s]; ok = ~np.isnan(a); g = np.sign(a[ok]); tt = tt[ok]
                    if not ok.any():
                        continue
                    vals["raw"].append(np.mean(tt * g)); vals["allcorr"].append(np.mean((tt - ba) * g))
                    if np.isfinite(bf):
                        vals["farcorr"].append(np.mean((tt - bf) * g))
                for k, vv in vals.items():
                    vv = np.array(vv); nul[k][it] = ((vv > 0).sum() - (vv < 0).sum(), vv.mean() if len(vv) else np.nan)
            for k, col in (("raw", "idx_raw"), ("farcorr", "idx_farcorr"), ("allcorr", "idx_allcorr")):
                x = D[(D.condition == cond) & D.turned & D[col].notna()][col]
                on, om = int((x > 0).sum() - (x < 0).sum()), float(x.mean())
                N = nul[k]
                out.append(dict(condition=cond, stat=f"idx_{k}", level=f"shift-{kind}", n=len(x), obs_net=on, obs_mean=om,
                                null_net_mean=float(N[:, 0].mean()), null_net_sd=float(N[:, 0].std()),
                                null_mean_mean=float(np.nanmean(N[:, 1])), p=float((N[:, 0] >= on).mean()),
                                p_mean=float((N[:, 1] >= om).mean()), shifts=shifts, seed=seed))
    return out


# ---------------------------------------------------------------- 3. body speed
def body_rows(v):
    d = v["d"]; gap = d.t_wall.diff().to_numpy(float); disp = np.hypot(d.x.diff(), d.z.diff()).to_numpy(float)
    w = d.ctl_walk.shift(1).to_numpy(float); m = (w > 0.2) & ~np.isnan(gap) & ~np.isnan(disp)
    brain_s = float(d.brain_t_ms.iloc[-1] / 1000); wall_s = float(d.t_wall.iloc[-1] - d.t_wall.iloc[0])
    r = dict(variant=v["variant"], chamber=v["chamber"], condition=v["condition"], trial=v["trial"], fly=v["fly"], dataset=v["dataset"],
             log=v["base"], rows=len(d), brain_s=brain_s, wall_s=wall_s, brain_per_wall=brain_s / wall_s if wall_s > 0 else np.nan,
             median_gap_s=float(np.nanmedian(gap)), share_gap_gt_0p8=float(np.nanmean(gap > STALL_GAP)),
             walk_rows=int(m.sum()), walk_duty=float(d.ctl_walk.mean()), path_blocks=float(np.nansum(disp)),
             disp_per_walk=float(disp[m].mean() / w[m].mean()) if m.any() else np.nan,
             blocks_per_brain_s=float(np.nansum(disp) / brain_s) if brain_s > 0 else np.nan)
    r["flag_stalled"] = r["share_gap_gt_0p8"] > STALL_SHARE; r["flag_short"] = brain_s < MIN_BRAIN_S
    r["comparable"] = not (r["flag_stalled"] or r["flag_short"])
    return r, pd.DataFrame(dict(gap=gap[m], disp=disp[m], w=w[m], variant=v["variant"], chamber=v["chamber"]))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--results", default=os.path.join(_edge.ROOT, "release", "pre_rerun_20260926", "results"),
                    help="dir with the paper's encounter_trials.csv, used only to cross-check the log index")
    ap.add_argument("--logs", nargs="+", default=[os.path.join(_edge.ROOT, "logs")], help="dirs searched for fly*_off-*.csv")
    ap.add_argument("--shifts", type=int, default=2000); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--quick", action="store_true", help=f"one series only ({QUICK_SERIES}; both pairings); pooled digit checks skipped")
    a = ap.parse_args()
    out = os.path.abspath(a.out_dir)
    paths = {k: os.path.join(out, f"{k}.csv") for k in ("start_check", "start_series", "lean_check", "lean_tests", "body_speed", "body_speed_bins")}
    paths["md"] = os.path.join(out, "arena_audit.md")
    for p in paths.values():
        _edge.safe_out(p)                                   # refuse experiments/results/ before any work

    cfgs = start_configs()
    L = load_logs(a.logs, [QUICK_SERIES] if a.quick else None, npos=len(cfgs))
    if not L:
        raise SystemExit("no arena logs found")
    pairs, rule, unpaired = pair_logs(L)
    md, verdicts = [], {}
    emit = lambda s="": md.append(s)
    emit("# Arena log audit (edge suite S4)"); emit()
    emit(f"Written by `experiments/edge/arena_audit.py` from {len(L)} logs (`fly*_off-*.csv` in {', '.join(os.path.relpath(x, _edge.ROOT) for x in a.logs)}; "
         f"the encounter_stats.py filter: >= 50 rows, trial label `off_*`){' — QUICK: series ' + QUICK_SERIES + ' only' if a.quick else ''}. "
         f"Pairs (figures.py rule: same label, stamps <= 10 s apart, one fly1 + one fly2): {sum(x == '<= 10 s' for x in rule.values())}"
         f"{'; paired only within 60 s (the loaded replication): ' + ', '.join(k for k, x in rule.items() if x != '<= 10 s') if any(x != '<= 10 s' for x in rule.values()) else ''}"
         f"; unpaired logs: {len(unpaired)}"
         + (f" ({', '.join(sorted(unpaired))})" if unpaired else "") + ". Contact = obs_taste_fly_female + obs_taste_fly_male > 0 (< 1.3 blocks); "
         "one row = one 50-ms brain tick; turn and azimuth are + = left (observe.js / motor.py).")
    relabel = [v["base"] for v in L.values() if v["label0"] != v["trial"]]
    if relabel:
        emit(); emit(f"Logs whose first-row label differs from the last (classified by the last, as encounter_stats.py): {', '.join(relabel)}")
    ref = os.path.join(a.results, "encounter_trials.csv")
    if os.path.exists(ref):                                  # the index must be the paper's: same logs, same per-log numbers
        T = pd.read_csv(ref); miss, bad = 0, []
        for r in T.itertuples():
            k = next((b for b, v in L.items() if v["fly"] == r.fly and v["stamp"] == str(r.stamp) and v["trial"] == r.trial), None)
            if k is None:
                miss += 1; continue
            v = L[k]; lb = max([n for _, n in runs(v["contact"])], default=0) * TICK_S
            if (len(v["d"]), int(v["contact"].sum()), round(lb, 2)) != (r.ticks, r.contact_ticks, round(r.longest_bout_s, 2)):
                bad.append(k)
        extra = len(L) - (len(T) - miss)
        emit(); emit(f"Index check against `{os.path.relpath(ref, _edge.ROOT)}`: {len(T) - miss} of its {len(T)} logs found"
                     f"{' (the rest are outside --quick)' if a.quick and miss else ''}, {len(bad)} differ in ticks / contact ticks / longest bout"
                     f"{': ' + ', '.join(bad) if bad else ''}; {extra} logs here are not in it.")
        verdicts["index_matches_paper_csv"] = not bad and (miss == 0 or a.quick)

    # ------------------------------------------------ 0. reproduce
    fem = [v for v in L.values() if v["dataset"] == "flywire"]
    spec_ch = [c for _, c in series_order({(v["variant"], v["chamber"]) for v in fem if in_paper_pool(v)})]
    other_ch = [c for _, c in series_order({(v["variant"], v["chamber"]) for v in fem if v["variant"] == "specific" and not in_paper_pool(v)})]
    emit(); emit("## 0. The paper's numbers, reproduced first"); emit()
    emit("Turn-toward index (replication_stats.py `toward`): mean of `ctl_turn × sign(near_az)` over the female logs' ticks before the "
         "log's first contact with `near_dist < 6` and `near_az` present, pooled over the ticks of all logs of the series (n = ticks)."); emit()
    emit("| series | pairing | index (n ticks) | printed | match |"); emit("|---|---|---|---|---|")
    checks = []
    for vc in series_order({(v["variant"], v["chamber"]) for v in fem}):
        for cond in ("ff", "mf"):
            g = [v for v in fem if (v["variant"], v["chamber"], v["condition"]) == (*vc, cond)]
            if not g:
                continue
            ix, n = toward_pooled(g)
            want = PAPER_SERIES.get((*vc, cond))
            if vc[0] == "published":
                want = (PAPER_PUBLISHED[cond], None); got = fmt(ix, 2, True)
            else:
                got = fmt(ix, 3, True)
            ok = None if want is None else (got == want[0] and (want[1] is None or want[1] == n))
            if ok is not None:
                checks.append(ok)
            emit(f"| {vc[0]} {vc[1]} | {cond} | {got} ({n}) | {'–' if want is None else want[0] + ('' if want[1] is None else f' ({want[1]})')} | "
                 f"{'–' if ok is None else ('yes' if ok else 'NO')} |")
    emit(); emit(f"Pooled lean (replication_stats.py, 'Leaning towards the partner'): female logs of the specific-lobe series it pools "
                 f"({', '.join(spec_ch)}{'; not pooled here, as there: ' + ', '.join(other_ch) if other_ch else ''}); per-log index = mean of `ctl_turn × sign(near_az)` over the same ticks, for logs with >= 1 such "
                 "tick and a nonzero turn command on one of them ('turn at all'); two-sided exact sign test on towards (> 0) vs away (< 0)."); emit()
    emit("| pairing | logs that turn | towards / away (zero) | nonzero | sign test p | pooled index | mean abs(turn) | index / mean abs(turn) | printed | match |")
    emit("|---|---|---|---|---|---|---|---|---|---|")
    pooled = {}
    for cond in ("mf", "ff"):
        P = pooled_lean([v for v in fem if in_paper_pool(v) and v["condition"] == cond]); pooled[cond] = P
        got = dict(logs=str(P["logs"]), split=f"{P['pos']} / {P['neg']}", nonzero=str(P["pos"] + P["neg"]), p=f"{P['p']:.3f}",
                   index=f"{P['index']:+.3f}", ratio=f"{P['ratio']:+.2f}")
        want = PAPER_POOLED[cond]; ok = None if a.quick else all(got[k] == want[k] for k in want)
        if ok is not None:
            checks.append(ok)
        emit(f"| {cond} | {got['logs']} | {got['split']} ({P['zero']}) | {got['nonzero']} | {got['p']} | {got['index']} | {P['abs_turn']:.3f} | {got['ratio']} | "
             f"{want['logs']}; {want['split']}; p {want['p']}; {want['index']}; {want['ratio']} | {'– (quick)' if ok is None else ('yes' if ok else 'NO')} |")
    emit(); emit(f"**Digit check: {sum(checks)} / {len(checks)} printed values reproduced.** The paper's '24 of 33' is the 33 mf logs with a "
                 f"nonzero index out of {pooled['mf']['logs']} that turn at all ({pooled['mf']['zero']} have an index of exactly 0).")
    verdicts["digit_check"] = f"{sum(checks)}/{len(checks)}"
    print(f"digit check: {sum(checks)}/{len(checks)} printed values reproduced")

    # ------------------------------------------------ 1. start check
    S = pd.DataFrame([dict(start_row(tk, L[x], L[y], cfgs), pair_rule=rule[tk]) for tk, (x, y) in sorted(pairs.items(), key=lambda kv: L[kv[1][0]]["t0"])])
    SS = series_table(L, S)
    emit(); emit("## 1. Start check: the 6-s launch stagger"); emit()
    emit("`run_pair.sh` starts fly1's bot, sleeps 6 s, then starts fly2's; fly1's brain is already stepping, so fly1 walks before its "
         "partner exists. Per trial: fly1's rows with `t_wall` <= fly2's first `t_wall`, fly1's straight-line displacement and path over "
         "them; `dist_at_placement` = |fly1's position at its last such row − fly2's first logged position| (if fly1's brain logged "
         "later, its first position against fly2's at that moment); fly2's first non-NaN "
         "`near_dist`; first contact of the trial = the earlier first-contact `t_wall` of the two logs. **flag_placed** = the trial has "
         f"contact, `dist_at_placement` <= {TOUCH} (or the contact came before both brains logged), and fly2's log shows no row from row 1 on "
         f"with `near_dist` > {TOUCH} before it: the flies were never both present and more than {TOUCH} blocks apart before touching (fly2's "
         f"row 0 is not used: it can still be read at fly2's pre-teleport spawn). **flag_plan** (design 2.7) = fly2's first `near_dist` "
         f"< {PLAN_DIST:g} and its first contact within {PLAN_ROWS} rows."); emit()
    emit("Start configurations (trials.sh POS; `faces` = cos of the angle between a fly's heading and the direction to its partner, "
         "1 = facing, −1 = facing away):"); emit()
    emit("| cfg | fly1 | fly2 | distance | fly1 faces | fly2 faces |"); emit("|---|---|---|---|---|---|")
    for k, c in cfgs.items():
        emit(f"| {k} | {c['fly1']} | {c['fly2']} | {c['dist']:.2f} | {c['fly1_faces']:+.2f} | {c['fly2_faces']:+.2f} |")
    fs = [v for v in L.values() if v["dataset"] == "flywire"]
    if len(S):
        # the longest bout of the paper: max over female logs (replication_stats: fem.longest_bout_s.max())
        best = max(fs, key=lambda v: max([n for _, n in runs(v["contact"])], default=0))
        row = S[(S.fly1 == best["base"]) | (S.fly2 == best["base"])]
        emit(); emit("### The longest bout"); emit()
        if len(row):
            r = row.iloc[0]; who = "fly1" if r.fly1 == best["base"] else "fly2"
            def fem_long(X, which):
                """longest female bout (ticks x 0.05 s) over the trials X of the specific lobe; which = all | first | rep"""
                c = [(r_[f"{w}_longest_bout_s"], r_.trial, r_.chamber, w) for _, r_ in X.iterrows() for w in ("fly1", "fly2")
                     if r_[f"{w}_dataset"] == "flywire" and r_.variant == "specific"
                     and (which == "all" or (which == "rep") == str(r_.chamber).startswith("rep-"))]
                return max(c, default=(np.nan, "", "", ""))
            say = lambda t: f"{t[0]:.2f} s (`{t[1]}`, {t[2]}, {t[3]})"
            genuine = bool(not r.flag_placed and r[f"{who}_longest_start_rel_fly2_s"] >= 0 and r.dist_at_placement > TOUCH)
            emit(f"- Trial: `{r.trial}` ({r.variant} lobe, chamber {r.chamber}, start {r.cfg}: {r.cfg_dist:.1f} blocks, fly1 faces {r.cfg_fly1_faces:+.2f}, "
                 f"fly2 {r.cfg_fly2_faces:+.2f}); the bout is {r[f'{who}_longest_bout_s']:.2f} s in {who}'s log `{best['base']}` "
                 f"(fly1 {r.fly1_longest_bout_s:.2f} s, fly2 {r.fly2_longest_bout_s:.2f} s = run length in ticks × 0.05 s; the paper prints the female "
                 f"maximum to one decimal).")
            emit(f"- fly2's brain logged its first row {r.stagger_s:.2f} s (wall) after fly1's; fly1 had logged {r.fly1_rows_before_fly2} rows by then "
                 f"({r.fly1_rows_before_fly2 * TICK_S:.2f} s of brain time) and moved {r.fly1_moved_before_fly2:.2f} blocks (path {r.fly1_path_before_fly2:.2f}) "
                 f"from its start, straight along its heading (fly1 faces fly2's start: {r.cfg_fly1_faces:+.2f}); fly1 first sensed any fly "
                 f"{r.fly1_first_sense_s:+.2f} s from fly2's first row. Logged start distance {r.start_dist_logged:.2f} blocks; distance at fly2's placement "
                 f"(fly1 at its row {max(r.fly1_rows_before_fly2 - 1, 0)} vs fly2's first position) **{r.dist_at_placement:.2f} blocks**; fly2's first reading "
                 f"(row {r.fly2_first_sense_row}) {r.dist_at_fly2_first_sense:.2f} blocks{', inside the 1.3-block touch range' if r.dist_at_fly2_first_sense <= TOUCH else ''}.")
            emit(f"- The bout began {r[f'{who}_longest_start_rel_fly2_s']:+.2f} s from fly2's first row (row {r[f'{who}_longest_start_row']} of {who}'s log; "
                 f"fly2's first contact at its row {r.fly2_first_contact_row}), so fly2 {'had' if r[f'{who}_longest_start_rel_fly2_s'] >= 0 else 'had NOT yet'} been "
                 f"placed, but the flies were {'never ' if not r.apart_before_contact else ''}more than {TOUCH} blocks apart between placement and the "
                 f"bout (flag_placed = {bool(r.flag_placed)}, flag_plan = {bool(r.flag_plan)}): **{'a genuine meeting' if genuine else 'not a meeting, a placement artefact'}**. "
                 f"Longest bout of this trial that began after the flies had been > {TOUCH} apart post-placement: fly1 {r.fly1_longest_after_apart_s:.2f} s, "
                 f"fly2 {r.fly2_longest_after_apart_s:.2f} s.")
            fl, flp = S[~S.flag_placed], S[~S.flag_plan]
            lp = {w: fem_long(fl, w) for w in ("all", "first", "rep")}; lpl = {w: fem_long(flp, w) for w in ("all", "first", "rep")}
            emit(f"- Longest female bout once the {int(S.flag_placed.sum())} flag_placed trials ({', '.join(S[S.flag_placed].chamber + ' ' + S[S.flag_placed].trial)}) "
                 f"are dropped: **{say(lp['all'])}** over every specific-lobe series; {say(lp['first'])} in the series first reported; "
                 f"{say(lp['rep'])} in the replication. Once the {int(S.flag_plan.sum())} flag_plan trials are dropped: {say(lpl['all'])}; first reported "
                 f"{say(lpl['first'])}; replication {say(lpl['rep'])}.")
            verdicts.update(longest_bout_trial=r.trial, longest_bout_chamber=r.chamber, longest_bout_s=float(r[f"{who}_longest_bout_s"]),
                            longest_bout_dist_at_placement=float(r.dist_at_placement), longest_bout_genuine=genuine,
                            longest_bout_without_placed_s=float(lp["all"][0]), longest_bout_without_placed_first_reported_s=float(lp["first"][0]),
                            longest_bout_without_placed_replication_s=float(lp["rep"][0]), longest_bout_without_plan_s=float(lpl["all"][0]))
        emit(); emit("### Flagged trials"); emit()
        F = S[S.flag_placed | S.flag_plan]
        emit("| trial | series | cfg | stagger s | fly1 rows / moved before fly2 | dist at placement | fly2 first near_dist (row) | first contact (s after fly2) | longest fly1 / fly2 s | placed | plan |")
        emit("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in F.itertuples():
            emit(f"| {r.trial} | {r.variant} {r.chamber} | {r.cfg} | {r.stagger_s:.2f} | {r.fly1_rows_before_fly2} / {r.fly1_moved_before_fly2:.2f} | "
                 f"{r.dist_at_placement:.2f} | {fmt(r.dist_at_fly2_first_sense, 2)} ({r.fly2_first_sense_row}) | {fmt(r.first_contact_rel_fly2_s, 2, True)} | "
                 f"{r.fly1_longest_bout_s:.2f} / {r.fly2_longest_bout_s:.2f} | {'x' if r.flag_placed else ''} | {'x' if r.flag_plan else ''} |")
        face = S.cfg_fly1_faces > 0.9
        moved = S[(S.fly1_start_off > 0.2) | (S.fly2_start_off > 0.2)]
        emit(); emit(f"Logged first positions match trials.sh (within 0.2 blocks of POS + 0.5) for {len(S) - len(moved)} of {len(S)} trials"
                     f"{': not ' + ', '.join(f'{c} {t} (fly1 off by {o1:.2f}, fly2 by {o2:.2f})' for c, t, o1, o2 in zip(moved.chamber, moved.trial, moved.fly1_start_off, moved.fly2_start_off)) if len(moved) else ''}. "
                     "A negative stagger means fly1's brain logged after fly2's (it loaded later; fly1's body stood still where it was placed), "
                     "so fly1 had no rows before fly2.")
        emit(); emit(f"Across all {len(S)} trials: stagger {S.stagger_s.min():.2f}–{S.stagger_s.max():.2f} s (median {S.stagger_s.median():.2f}); "
                     f"fly1 rows before fly2 {S.fly1_rows_before_fly2.min()}–{S.fly1_rows_before_fly2.max()}; fly1 displacement before fly2 "
                     f"{S.fly1_moved_before_fly2.min():.2f}–{S.fly1_moved_before_fly2.max():.2f} blocks. Trials (all variants) with contact among those that start facing "
                     f"each other (t1, t3; fly1 faces > 0.9): {int(S[face].first_contact_rel_fly2_s.notna().sum())} of {int(face.sum())} "
                     f"({int(S[face & ~S.flag_placed].first_contact_rel_fly2_s.notna().sum())} not flag_placed); the other starts: "
                     f"{int(S[~face].first_contact_rel_fly2_s.notna().sum())} of {int((~face).sum())} ({int(S[~face & ~S.flag_placed].first_contact_rel_fly2_s.notna().sum())} not flag_placed).")
        emit(); emit("Trials with contact by start configuration (specific lobe; `placed` = of them flag_placed):"); emit()
        emit("| cfg | faces | ff: trials, with contact (placed) | mf: trials, with contact (placed) |"); emit("|---|---|---|---|")
        sp = S[S.variant == "specific"]
        for k, c in cfgs.items():
            cell = lambda x: f"{len(x)}, {int(x.first_contact_rel_fly2_s.notna().sum())} ({int(x.flag_placed.sum())})"
            emit(f"| {k} | {c['fly1_faces']:+.2f} | {cell(sp[(sp.cfg == k) & (sp.condition == 'ff')])} | {cell(sp[(sp.cfg == k) & (sp.condition == 'mf')])} |")
        emit(); emit("### Series numbers without the flagged trials (female logs, as replication_stats.py)"); emit()
        emit("| series | pairing | excluded | trials with contact | contact, % of ticks (mean ± sd over logs) | longest bout, s | dropped trials |")
        emit("|---|---|---|---|---|---|---|")
        for r in SS.itertuples():
            emit(f"| {r.variant} {r.chamber} | {r.condition} | {r.excluded} | {r.trials_contact} / {r.trials} | {fmt(r.contact_pct_mean, 1)} ± {fmt(r.contact_pct_sd, 1)} | "
                 f"{fmt(r.longest_bout_s, 2)} | {r.excluded_trials or '–'} |")
        emit(); emit("### fly1's turning before and after its partner appears"); emit()
        emit("Mean `ctl_turn` and mean `hz_turn_L − hz_turn_R` (Hz) over fly1's rows up to fly2's first `t_wall` (before) and after; mean ± sd over trials. "
             "The published lobe turns left whatever is where (a partner-independent bias shows as equal before and after)."); emit()
        emit("| series | pairing | fly1 | trials | turn before | turn after | DNa L−R before, Hz | DNa L−R after, Hz |"); emit("|---|---|---|---|---|---|---|---|")
        for (vr, ch, cond, ds), g in S.groupby(["variant", "chamber", "condition", "fly1_dataset"], sort=False):
            emit(f"| {vr} {ch} | {cond} | {ds} | {len(g)} | {g.fly1_turn_before.mean():+.3f} ± {g.fly1_turn_before.std():.3f} | {g.fly1_turn_after.mean():+.3f} ± {g.fly1_turn_after.std():.3f} | "
                 f"{g.fly1_LR_before_hz.mean():+.2f} ± {g.fly1_LR_before_hz.std():.2f} | {g.fly1_LR_after_hz.mean():+.2f} ± {g.fly1_LR_after_hz.std():.2f} |")

    # ------------------------------------------------ 2. lean check
    lf = [v for v in fem if v["variant"] == "specific"]
    D = pd.DataFrame([lean_row(v) for v in lf])
    D["series"] = D.chamber
    tests = []
    for idx in ("idx_raw", "idx_farcorr", "idx_allcorr", "side_contrast", "idx_minus_bias_x_side"):
        for level in ("log", "cfg", "series", "trial_id"):
            tests += sign_tests(D, idx, level)
    tests += shift_nulls(lf, D, a.shifts, a.seed)
    TT = pd.DataFrame(tests)
    emit(); emit("## 2. Lean check (female logs, specific lobe, every series)"); emit()
    if other_ch:
        emit(f"**Note: these tests pool {len(other_ch)} specific-lobe chamber(s) that replication_stats.py does not ({', '.join(other_ch)}), "
             f"so they are not the paper's 24/33 set; rerun with `--logs` pointing at the paper's logs only to test the paper's claim.**"); emit()
    emit(f"Ticks: before the log's first contact, `near_dist < {NEAR:g}`, `near_az` present (the paper's). Per log: "
         "**idx_raw** = mean(turn · sign(az)) (the paper's); **idx_farcorr** = mean((turn − b_far) · sign(az)), b_far = the log's mean `ctl_turn` "
         f"over non-contact ticks with `near_dist` >= {FAR:g} (logs without such ticks drop out); **idx_allcorr** = the same with b_all = the log's "
         "mean `ctl_turn` over all ticks; **side_contrast** = (mean turn with the partner on the left − on the right) / 2, logs with >= 10 ticks "
         "per side (immune to any constant bias); **idx_minus_bias_x_side** = idx_raw − mean(turn) · mean(sign(az)) (the within-log covariance). "
         "Only logs that turn at all enter. Sign tests: two-sided exact on > 0 vs < 0, Holm over mf/ff per index and level. Clusters: the mean "
         "index of the logs in a start configuration (`cfg`, t1–t5), a series, or a trial (`trial_id`; the two females of an ff trial), then a sign test over clusters."); emit()
    emit("| index | level | mf: n, towards / away (0), mean of the per-log (per-cluster) values, p, p Holm | ff: the same |"); emit("|---|---|---|---|")
    ST = TT[~TT.level.str.startswith("shift")]
    for (idx, level), g in ST.groupby(["stat", "level"], sort=False):
        c = {r.condition: r for r in g.itertuples()}
        cell = lambda r: f"{int(r.n)}, {int(r.pos)} / {int(r.neg)} ({int(r.zero)}), {fmt(r.mean, 4, True)}, {fmt(r.p)}, {fmt(r.p_holm)}" if r is not None else "–"
        emit(f"| {idx} | {level} | {cell(c.get('mf'))} | {cell(c.get('ff'))} |")
    emit(); emit(f"Time-shift nulls ({a.shifts} shifts, `np.random.default_rng({a.seed})` per pairing and kind; the same draws for all three indices): "
                 "near_az is rolled circularly (within-pre: inside the pre-contact segment, offset uniform over 10–90 % of its length; whole-log: "
                 "over the log, 10–90 % of its length) while the tick selection and the turn stay real. P = share of shifts whose net "
                 "(towards − away) is >= the observed; P(mean) the same for the mean per-log index."); emit()
    emit("| pairing | index | null | n logs | observed net / mean | null net mean ± sd | P(net) | P(mean) |"); emit("|---|---|---|---|---|---|---|---|")
    for r in TT[TT.level.str.startswith("shift")].itertuples():
        emit(f"| {r.condition} | {r.stat} | {r.level[6:]} | {r.n} | {int(r.obs_net):+d} / {r.obs_mean:+.4f} | {r.null_net_mean:+.1f} ± {r.null_net_sd:.1f} | {r.p:.4f} | {r.p_mean:.4f} |")
    emit(); emit("Per-log lean against the sign of (mean turn × mean side) over the same ticks: a lean that only reflects a turning bias "
                 "times the side the partner happened to sit on has sign(idx_raw) = sign(mean_turn_pre × mean_side_pre)."); emit()
    emit("| pairing | logs (turn, both signs nonzero) | sign(idx) = sign(bias × side) | of the towards logs | of the away logs | logs with far ticks | smell L−R agrees with sign(az), mean share of ticks |")
    emit("|---|---|---|---|---|---|---|")
    for cond in ("mf", "ff"):
        x = D[(D.condition == cond) & D.turned]; y = x[(x.idx_raw != 0) & (x.bias_x_side != 0)]
        ag = np.sign(y.idx_raw) == np.sign(y.bias_x_side)
        emit(f"| {cond} | {len(y)} | {int(ag.sum())} | {int(ag[y.idx_raw > 0].sum())} / {int((y.idx_raw > 0).sum())} | {int(ag[y.idx_raw < 0].sum())} / {int((y.idx_raw < 0).sum())} | "
             f"{int((x.n_far > 0).sum())} / {len(x)} | {fmt(x.smell_side_agrees.mean())} |")
    g = lambda cond, idx, level: TT[(TT.condition == cond) & (TT.stat == idx) & (TT.level == level)]
    fc, sh = g("mf", "idx_farcorr", "log"), g("mf", "idx_raw", "shift-within-pre")
    if len(fc) and len(sh):
        # "p < 0.025 (Holm over mf/ff)" = Holm at family-wise 0.05 over the two pairings: the smaller raw p is compared with
        # 0.025, i.e. Holm-adjusted p < 0.05 (adjusted p < 0.025 would correct twice); the lean must also point towards
        towards = int(fc.pos.iloc[0]) > int(fc.neg.iloc[0])
        keep = bool(towards and fc.p_holm.iloc[0] < 0.05 and sh.p.iloc[0] < 0.05)
        verdicts.update(lean_mf_farcorr_split=f"{int(fc.pos.iloc[0])}/{int(fc.neg.iloc[0])}", lean_mf_farcorr_p=float(fc.p.iloc[0]),
                        lean_mf_farcorr_p_holm=float(fc.p_holm.iloc[0]), lean_mf_shift_within_P=float(sh.p.iloc[0]), lean_keep=keep,
                        lean_extra_chambers=other_ch)
        emit(); emit(f"**S4 criterion (keep the lean only if the far-bias-corrected mf sign test leans towards with p < 0.025 under Holm over mf/ff "
                     f"(Holm-adjusted p < 0.05) and the within-pre-contact shift null P < 0.05):** far-corrected mf {int(fc.pos.iloc[0])} / "
                     f"{int(fc.neg.iloc[0])}, p = {fc.p.iloc[0]:.3f}, Holm p = {fc.p_holm.iloc[0]:.3f}; within-pre shift P(net) = {sh.p.iloc[0]:.4f} → "
                     f"**{'KEEP' if keep else 'CHANGE'}**{' (pools chambers outside the paper set: ' + ', '.join(other_ch) + ')' if other_ch else ''}.")

    # ------------------------------------------------ 3. body speed
    B, bins = [], []
    for v in L.values():
        r, b = body_rows(v); B.append(r); bins.append(b)
    B = pd.DataFrame(B); G = pd.concat(bins, ignore_index=True)
    G["gap_bin"] = pd.cut(G.gap, GAP_BINS).astype(str)
    BB = []
    for key, gg in [(("all", "all"), G)] + [(k, x) for k, x in G.groupby(["variant", "chamber"])]:
        for gb, x in gg.groupby("gap_bin", sort=False):
            BB.append(dict(variant=key[0], chamber=key[1], gap_bin=gb, lo=float(x.gap.min()), rows=len(x), mean_gap_s=float(x.gap.mean()),
                           mean_disp=float(x.disp.mean()), mean_walk=float(x.w.mean()), disp_per_walk=float(x.disp.mean() / x.w.mean())))
    BB = pd.DataFrame(BB).sort_values(["variant", "chamber", "lo"]).drop(columns="lo")
    emit(); emit("## 3. Body speed and stalls"); emit()
    emit(f"Per row: wall gap = Δ`t_wall`; displacement = |Δ(x, z)|; walk = the previous row's `ctl_walk` (the drive the body executed over "
         f"the gap); only rows with walk > 0.2. Per log: share of rows with gap > {STALL_GAP} s (stalled if > {STALL_SHARE:.0%}), brain time "
         f"(short if < {MIN_BRAIN_S:g} s), displacement per unit walk = mean(displacement) / mean(walk)."); emit()
    emit("| gap bin, s (all logs) | rows | mean gap | mean displacement | mean walk | displacement per unit walk |"); emit("|---|---|---|---|---|---|")
    for r in BB[BB.variant == "all"].itertuples():
        emit(f"| {r.gap_bin} | {r.rows} | {r.mean_gap_s:.3f} | {r.mean_disp:.3f} | {r.mean_walk:.3f} | {r.disp_per_walk:.3f} |")
    emit(); emit("| series | pairing | logs | brain s (mean) | brain / wall | median gap s | rows with gap > 0.8 s | stalled / short logs | displacement per unit walk | blocks per brain-s | comparable |")
    emit("|---|---|---|---|---|---|---|---|---|---|---|")
    comp = {}
    for (vr, ch), gs in sorted(B.groupby(["variant", "chamber"]), key=lambda kv: series_key(kv[0])):
        for cond, x in gs.groupby("condition"):
            share = float((x.share_gap_gt_0p8 * x.rows).sum() / x.rows.sum()); ok = share <= STALL_SHARE and x.brain_s.mean() >= MIN_BRAIN_S
            comp[f"{vr} {ch} {cond}"] = bool(ok)
            emit(f"| {vr} {ch} | {cond} | {len(x)} | {x.brain_s.mean():.0f} | {x.brain_per_wall.mean():.2f} | {x.median_gap_s.median():.3f} | {share:.1%} | "
                 f"{int(x.flag_stalled.sum())} / {int(x.flag_short.sum())} | {fmt(x.disp_per_walk.mean())} | {fmt(x.blocks_per_brain_s.mean())} | {'yes' if ok else 'NO'} |")
    verdicts["series_comparable"] = comp
    emit(); emit("A series is comparable when its pooled share of rows with a gap over 0.8 s is <= 5 % and its mean brain time >= 60 s "
                 f"(S4). Stalled logs: {', '.join(B[B.flag_stalled].log) or 'none'}. Short logs: {', '.join(B[B.flag_short].log) or 'none'}.")

    # ------------------------------------------------ write
    for key, df in (("start_check", S), ("start_series", SS), ("lean_check", D), ("lean_tests", TT), ("body_speed", B), ("body_speed_bins", BB)):
        tmp, final = _edge.safe_out(paths[key]); df.to_csv(tmp, index=False); _edge.finish(tmp, final)
    tmp, final = _edge.safe_out(paths["md"]); open(tmp, "w").write("\n".join(md) + "\n"); _edge.finish(tmp, final)
    verdicts = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in verdicts.items()}
    _edge.sidecar(paths["md"], {"logs": len(L), "pairs": len(pairs), "shifts": a.shifts, "seed": a.seed, "quick": a.quick,
                                "results": os.path.relpath(a.results, _edge.ROOT), "verdicts": verdicts})
    for k, v in verdicts.items():
        print(f"{k}: {v}")
    print("wrote", ", ".join(os.path.relpath(p, _edge.ROOT) for p in paths.values()))


if __name__ == "__main__":
    main()
