#!/usr/bin/env python3
"""The arena series of the paper, and the replication of 25-26 Sep 2026 next to the series it repeats (RESEARCH_NOTES 22).

Reads experiments/results/encounter_trials.csv (run experiments/encounter_stats.py first) and the arena logs, and prints,
for every chamber and pairing, the numbers the paper's arena claims rest on: trials with contact, share of ticks in
contact, longest bout, walking, the female's turning DNs far -> contact, DNp13 far -> contact, acts per minute,
acceptance (DNp37 = vpoDN), the male's MDN, and the turn-toward index (turn command x side of the other fly, over the
pre-contact ticks within 6 blocks, as in paper_numbers.py section P). Female values are means over female fly-logs (both
flies in ff, fly2 in mf); +/- = sd across fly-logs. A replication chamber is `<prefix><chamber>` and is shown next to
`<chamber>`.
Writes experiments/results/replication_20260925.md and, with --tex, the LaTeX table of the paper's Appendix C.
  python experiments/replication_stats.py [--prefix rep-] [--tex paper/tables_arena.tex]
"""
import argparse, glob, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); LOGS = os.path.join(HERE, "..", "logs")
# the series of the paper, in the order the paper tells them: (variant, chamber, label, date)
SERIES = [("published", "odor-free", "Published smell centre, no smell in the box", "14 Sep"),
          ("specific", "faint-smell", "Changed smell centre, faint flower smell at the wall", "17 Sep"),
          ("specific", "clean", "Changed smell centre, clean box", "18 Sep"),
          ("specific", "noise0.2", "Clean box with the 0.2 Hz hum", "18--19 Sep"),
          ("specific", "noise0.2-virgin", "Clean box with the hum, virgin female", "24 Sep")]
# trials whose first contact was a launch artefact: run_pair.sh's 6-s stagger let fly1 walk onto fly2's start point, so the
# flies were never apart before touching (experiments/edge/arena_audit.py start_check, flag_placed; RESEARCH_NOTES 23c).
# They are left out of every row of the table.
PLACEMENT_ARTEFACTS = {("faint-smell", "off_ff_t1"), ("faint-smell", "off_ff_t3")}
# series that ran too slowly to compare (the laptop was so loaded that the body's slow-down to brain time failed:
# a median 0.8 s of wall time per 50-ms brain step; RESEARCH_NOTES 23c) - marked in the table
NOT_COMPARABLE = {("rep-clean", "mf")}


# the arena edge series of 27 Sep (experiments/run_arena_edge.sh): new brain seeds, both flies started together (--waitFor),
# logs in logs/edge_arena/<label>/, statistics from encounter_stats.py --logs ... --out (option --extra); shown as a last block
EDGE_SERIES = [("specific", "sync-noise0.2", "New seeds, flies started together: clean box with the hum", "27 Sep"),
               ("specific", "sync-noise0.2-notouch", "The same, with the females' touch switched off", "27 Sep"),
               ("specific", "sync-clean", "New seeds, flies started together: clean box", "27 Sep")]


def log_of(r):
    fs = glob.glob(os.path.join(LOGS, f"{r.fly}_off-*_{r.stamp}.csv")) or glob.glob(os.path.join(LOGS, "edge_arena", "*", f"{r.fly}_off-*_{r.stamp}.csv"))
    return pd.read_csv(fs[0]) if fs else None


def toward(rows):
    """turn-toward index over the pre-contact ticks within 6 blocks, pooled over the logs; mean turn command over all ticks"""
    tw, allturn = [], []
    for _, r in rows.iterrows():
        d = log_of(r)
        if d is None:
            continue
        contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
        first = int(np.argmax(contact.to_numpy())) if contact.any() else len(d)
        pre = d.iloc[:first]; pre = pre[(pre.near_dist < 6) & pre.near_az.notna()]
        tw += list(pre.ctl_turn * np.sign(pre.near_az)); allturn += list(d.ctl_turn)
    return (np.mean(tw) if tw else np.nan), len(tw), (np.mean(allturn) if allturn else np.nan)


def m(s, k):
    return s[k].mean() if k in s and s[k].notna().any() else np.nan


def stats(T, variant, ch, cond):
    """raw numbers for one chamber x pairing (None if there are no female logs)"""
    keep = [(ch, tr) not in PLACEMENT_ARTEFACTS for tr in T.trial]
    T = T[keep]
    fem = T[(T.variant == variant) & (T.chamber == ch) & (T.condition == cond) & (T.dataset == "flywire")]
    male = T[(T.variant == variant) & (T.chamber == ch) & (T.condition == cond) & (T.dataset == "malecns")]
    if fem.empty:
        return None
    cp = fem.contact_ticks / fem.ticks * 100
    tw, n_tw, turn = toward(fem)
    s = {"trials": fem.trial.nunique(), "logs": len(fem), "brain_mean": fem.brain_s.mean(), "brain_sd": fem.brain_s.std(),
         "trials_contact": fem[fem.contact_ticks > 0].trial.nunique(), "contact_mean": cp.mean(), "contact_sd": cp.std(),
         "longest": fem.longest_bout_s.max(), "walk": m(fem, "walk"),
         "dna_far": (m(fem, "turn_L_far"), m(fem, "turn_R_far")), "dna_contact": (m(fem, "turn_L_contact"), m(fem, "turn_R_contact")),
         "dnp13_far": m(fem, "reject_far"), "dnp13_contact": m(fem, "reject_contact"),
         "acts": (m(fem, "reject_events_per_min"), m(fem, "feed_events_per_min"), m(fem, "attack_events_per_min")),
         "accept": (m(fem, "accept_far"), m(fem, "accept_near"), m(fem, "accept_contact")), "accept_min": m(fem, "accept_events_per_min"),
         "aggr": (m(fem, "aggression_far"), m(fem, "aggression_contact")), "toward": tw, "n_toward": n_tw, "turn": turn}
    if len(male):
        s.update({"mdn": (m(male, "back_contact"), m(male, "back_near"), m(male, "back_far")), "male_walk": m(male, "walk"),
                  "p1": (m(male, "court_p1_far"), m(male, "court_p1_contact")), "sing": (m(male, "sing_far"), m(male, "sing_contact"))})
    return s


def f(x, d=1):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def md_rows(s):
    r = {"trials": s["trials"], "female logs": s["logs"], "brain s per log": f"{s['brain_mean']:.0f} ± {s['brain_sd']:.0f}",
         "trials with contact": f"{s['trials_contact']} / {s['trials']}", "contact, % of ticks": f"{f(s['contact_mean'])} ± {f(s['contact_sd'])}",
         "longest bout, s": f(s["longest"]), "walk duty": f(s["walk"], 2),
         "DNa L / R far → contact, Hz": f"{f(s['dna_far'][0])} / {f(s['dna_far'][1])} → {f(s['dna_contact'][0])} / {f(s['dna_contact'][1])}",
         "DNp13 far → contact, Hz": f"{f(s['dnp13_far'])} → {f(s['dnp13_contact'])}",
         "extrusion / proboscis / lunge acts per min": f"{f(s['acts'][0], 0)} / {f(s['acts'][1], 0)} / {f(s['acts'][2])}",
         "DNp37 (accept) far / near / contact, Hz": " / ".join(f(x) for x in s["accept"]), "acceptance acts per min": f(s["accept_min"], 0),
         "pC1d/e + aIPg far / contact, Hz": " / ".join(f(x) for x in s["aggr"]),
         "turn-toward index (pre-contact ticks < 6 blocks)": f"{s['toward']:+.3f} (n = {s['n_toward']})" if s["n_toward"] else "–",
         "mean turn command, all ticks": f"{s['turn']:+.3f}"}
    if "mdn" in s:
        r.update({"male: MDN contact / near / far, Hz": " / ".join(f(x, 0) for x in s["mdn"]), "male: walk duty": f(s["male_walk"], 2),
                  "male: P1 far / contact; pIP10 (song) far / contact, Hz": f"{f(s['p1'][0])} / {f(s['p1'][1])}; {f(s['sing'][0])} / {f(s['sing'][1])}"})
    return r


def tex_row(pair, s):
    tw = f"{s['toward']:+.3f}".replace("-", "$-$") if s["n_toward"] else "--"
    mdn = f(s["mdn"][0], 0) if "mdn" in s else "--"
    longest = f(s["longest"]) if s["trials_contact"] else "--"
    return (f"{pair} & {s['trials_contact']}/{s['trials']} & {f(s['contact_mean'])} $\\pm$ {f(s['contact_sd'])} & {longest} & {f(s['walk'], 2)} & "
            f"{f(s['dna_far'][0])}/{f(s['dna_far'][1])} $\\rightarrow$ {f(s['dna_contact'][0])}/{f(s['dna_contact'][1])} & "
            f"{f(s['dnp13_far'])} $\\rightarrow$ {f(s['dnp13_contact'])} & {tw} & {mdn} \\\\").replace("–/–", "--").replace("– ", "-- ").replace("–", "--")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--prefix", default="rep-")
    ap.add_argument("--out", default=os.path.join(RES, "replication_20260925.md")); ap.add_argument("--tex", default=None)
    ap.add_argument("--extra", default=None, help="encounter_stats.py csv of the 27 Sep edge series (shown as a last block in --tex)")
    a = ap.parse_args()
    T = pd.read_csv(os.path.join(RES, "encounter_trials.csv"))
    extra = []
    if a.extra:
        X = pd.read_csv(a.extra); T = pd.concat([T, X[X.chamber.isin([s[1] for s in EDGE_SERIES])]], ignore_index=True)
        extra = [s for s in EDGE_SERIES if s[1] in set(X.chamber)]
    lines = []
    emit = lambda s="": (print(s), lines.append(s))
    emit(f"# Arena replication (chambers `{a.prefix}*`) next to the series the paper reports"); emit()
    emit("Female values are means over female fly-logs (both flies in ff, fly2 in mf), ± = sd across fly-logs; contact = within "
         "1.3 blocks (the touch sense); far = > 3.5 blocks; the turn-toward index is the turn command × the side the other fly "
         "is on, over the ticks within 6 blocks before a log's first contact (+ = toward). Written by experiments/replication_stats.py.")
    reps = sorted(c for c in T[T.variant == "specific"].chamber.unique() if str(c).startswith(a.prefix))
    pairs = [(c[len(a.prefix):], c) for c in reps] or [(c, None) for c in ("clean", "noise0.2", "noise0.2-virgin")]
    if not reps:
        emit(); emit(f"(no `{a.prefix}*` chambers in encounter_trials.csv yet; showing the originals)")
    for orig, rep in pairs:
        for cond in ("ff", "mf"):
            o = stats(T, "specific", orig, cond); r = stats(T, "specific", rep, cond) if rep else None
            if o is None and r is None:
                continue
            ro, rr = (md_rows(o) if o else {}), (md_rows(r) if r else {})
            emit(); emit(f"## {orig} · {cond}" + (f"  (replication: `{rep}`)" if rep else "")); emit()
            emit("| | reported series | replication |"); emit("|---|---|---|")
            for k in list(ro or rr) + [k for k in rr if k not in ro]:
                emit(f"| {k} | {ro.get(k, '–')} | {rr.get(k, '–')} |")
    # does a fly lean towards its partner at all? per fly-log turn-toward indices pooled over every series of the paper's
    # model (original and replication), with a two-sided sign test; the index is set against the fly's mean |turn command|
    from math import comb
    series = ["faint-smell", "clean", "noise0.2", "noise0.2-virgin"] + [c for c in reps]
    emit(); emit("## Leaning towards the partner, pooled over every series of the paper's model (original and replication)"); emit()
    emit("| pairing | fly-logs that turn at all | leaning towards / away | sign test p (two-sided) | pooled index | mean abs(turn) | index / mean abs(turn) |")
    emit("|---|---|---|---|---|---|---|")
    for cond in ("mf", "ff"):
        vals, tw, ab = [], [], []
        for ch in series:
            for _, r in T[(T.variant == "specific") & (T.chamber == ch) & (T.condition == cond) & (T.dataset == "flywire")].iterrows():
                d = log_of(r)
                if d is None:
                    continue
                contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
                first = int(np.argmax(contact.to_numpy())) if contact.any() else len(d)
                pre = d.iloc[:first]; pre = pre[(pre.near_dist < 6) & pre.near_az.notna()]
                if len(pre) == 0 or pre.ctl_turn.abs().sum() == 0:
                    continue
                v = pre.ctl_turn * np.sign(pre.near_az); vals.append(v.mean()); tw += list(v); ab += list(pre.ctl_turn.abs())
        vals = np.array(vals); pos, neg = int((vals > 0).sum()), int((vals < 0).sum()); n = pos + neg
        p = min(1.0, 2 * sum(comb(n, k) for k in range(max(pos, neg), n + 1)) / 2 ** n) if n else float("nan")
        emit(f"| {cond} | {len(vals)} | {pos} / {neg} | {p:.3f} | {np.mean(tw):+.3f} | {np.mean(ab):.3f} | {np.mean(tw) / np.mean(ab):+.2f} |")
    open(a.out, "w").write("\n".join(lines) + "\n"); print("wrote", a.out)
    if a.tex:
        t = [r"\begin{table}[h]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{3.2pt}", r"\renewcommand{\arraystretch}{1.12}",
             r"\resizebox{\textwidth}{!}{%", r"\begin{tabular}{@{}lcccccccc@{}}", r"\toprule",
             r"Pair & Trials with & Contact & Longest & Walking & Steering neurons, & Ovipositor neuron, & Toward & Male MDN \\",
             r" & contact & (\% of time) & meeting (s) & (share) & far $\rightarrow$ contact (L/R, Hz) & far $\rightarrow$ contact (Hz) & index & on contact (Hz) \\",
             r"\midrule"]
        blocks = [(v, ch, lab, date) for v, ch, lab, date in SERIES] + [("specific", c, f"Again: {dict((s[1], s[2]) for s in SERIES).get(c[len(a.prefix):], c)}", "25--26 Sep") for c in reps]
        for i, (v, ch, lab, date) in enumerate(blocks):
            rows = [(cond, stats(T, v, ch, cond)) for cond in ("ff", "mf")]
            rows = [(c, s) for c, s in rows if s is not None]
            if not rows:
                continue
            if i and ch.startswith(a.prefix) and not blocks[i - 1][1].startswith(a.prefix):
                t.append(r"\midrule")
            t.append(r"\multicolumn{9}{@{}l}{\emph{" + lab.replace(" Hz", r"\,Hz") + f" ({date})" + r"}} \\")
            for cond, s in rows:
                t.append(tex_row({"ff": "two females", "mf": "male + female"}[cond] + (r"$^\dagger$" if (ch, cond) in NOT_COMPARABLE else ""), s))
        for i, (v, ch, lab, date) in enumerate(extra):
            rows = [(c, s) for c, s in ((cond, stats(T, v, ch, cond)) for cond in ("ff", "mf")) if s is not None]
            if not rows:
                continue
            if i == 0:
                t.append(r"\midrule")
            t.append(r"\multicolumn{9}{@{}l}{\emph{" + lab + f" ({date})" + r"}} \\")
            for cond, s in rows:
                t.append(tex_row({"ff": "two females", "mf": "male + female"}[cond], s))
        t += [r"\bottomrule", r"\end{tabular}}",
              r"\caption{Every box, series by series, with the replication (``Again'') at the bottom. Female values are means over the female fly-logs (both flies in a female pair, the female in a male--female pair), five trials per row, $\pm$ the standard deviation across fly-logs; contact means within 1.3 blocks, the range of the touch sense; far means more than 3.5 blocks away. Walking is the share of time the fly spent walking. Far values include moments against a wall, which the body feels as touch, so the walls, not the hum, set the ovipositor neuron's far values (about 20\,Hz against a wall, under 0.5\,Hz away from walls and flies, 0.2\,Hz with touch switched off). Trials ran 300\,s (180\,s in the 14 Sep series; 600\,s in the replication's hum and virgin series, because other work on the laptop had slowed the brains). The toward index is the turn command times the side the other fly is on, over the moments within six blocks before a first contact (positive = towards). The faint-smell female pairs lost two of their five trials, which began in contact because the first fly was let loose a few seconds before the second (Note 8). $^\dagger$The laptop was so loaded during this series that the body's slow-down to brain time failed, so it cannot be compared with the original." + (r" The last block repeats three of the series above (two females, and a male and a female, on the hum; a male and a female in the clean box) with new brain seeds and both flies started together, in trials of 600\,s (300\,s in the clean box), and adds a fourth on the hum in which the females' touch, of the walls as well as of each other, was switched off." if extra else "") + r" Written by \texttt{experiments/replication\_stats.py}.}",
              r"\label{tab:arena}", r"\end{table}"]
        open(a.tex, "w").write("\n".join(t) + "\n"); print("wrote", a.tex)


if __name__ == "__main__":
    main()
