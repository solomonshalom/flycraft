#!/usr/bin/env python3
"""Every number of the earlier Markdown draft of the paper (not included here), hard-coded below and re-derived from the result files.

Prints Table 1's evidence cells, Table 2, and the numbers the Results text rests on, computed from experiments/results/
and the arena logs in logs/, each next to the value typed in the paper, and flags the ones that differ (numbers are
compared with a tolerance of 0.55 Hz or 3 %, whichever is larger, so seed-mean rounding does not flag). Run it after
any result file changes; the paper should carry what it prints.

  python experiments/paper_numbers.py                                -> stdout and experiments/results/paper_numbers.md
"""
import argparse, glob, json, os, re, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); LOGS = os.path.join(HERE, "..", "logs")
PAPER_F, PAPER_M = "shiu_min1+known+eln0.25", "all_min1+eln0.25"
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(RES, "paper_numbers.md")); a = ap.parse_args()
LINES, NDIFF, NCHECK = [], 0, 0


def emit(s=""):
    print(s); LINES.append(s)


def section(title):
    emit(); emit(f"## {title}"); emit()


NUM = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?")      # a hyphen between digits is a range, not a sign


def same(c, d):
    """numeric-tolerant equality of two strings: same numbers in the same order within 0.55 or 3 %"""
    cn, dn = [float(x) for x in NUM.findall(c)], [float(x) for x in NUM.findall(d)]
    if not cn and not dn:
        return c.strip() == d.strip()
    if len(dn) == 1 and len(cn) > 1:                      # "0.0" against "0.0 / 0.0 / 0.0": every computed number must match
        return all(abs(x - dn[0]) <= max(0.55, 0.03 * abs(dn[0])) for x in cn)
    if len(cn) != len(dn) or not cn:
        return False
    return all(abs(x - y) <= max(0.55, 0.03 * abs(y)) for x, y in zip(cn, dn))


def check(label, computed, paper=None, where=""):
    """one line: label | computed | paper's value | verdict"""
    global NDIFF, NCHECK
    computed = str(computed)
    if paper is None:
        emit(f"- {label}: **{computed}**" + (f"  ({where})" if where else ""))
        return
    NCHECK += 1
    ok = same(computed, paper)
    if not ok:
        NDIFF += 1
    emit(f"- {label}: computed **{computed}** | paper: {paper} | {'ok' if ok else '**DIFFERS**'}" + (f"  ({where})" if where else ""))


def csv(name):
    p = os.path.join(RES, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def f1(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else (f"{x:.1f}" if abs(x) < 100 else f"{x:.0f}")


def rng(vals, nd=1):
    v = [x for x in vals if np.isfinite(x)]
    return f"{min(v):.{nd}f}-{max(v):.{nd}f}" if v else "nan"


# ================================================================== A. published anchors (benchmark.py)
section("A. Published anchors (`benchmark_flywire*.csv`, Results 1, Fig 8)")
for tag, name in (("paper's model", f"benchmark_flywire_{PAPER_F}.csv"), ("published lobe", "benchmark_flywire.csv")):
    b = csv(name)
    if b is None:
        continue
    g = b.groupby("condition")["MN9 L"].mean()
    r = g["sugar GRNs @ 100 Hz"] / g["sugar GRNs @ 200 Hz"]
    check(f"sugar -> MN9, 100 Hz / 200 Hz response ratio ({tag})", f"{g['sugar GRNs @ 100 Hz']:.0f} / {g['sugar GRNs @ 200 Hz']:.0f} Hz = {r*100:.0f} %", None)
    check(f"bitter suppression: sugar 100 alone -> + bitter 100 ({tag})", f"{g['sugar 100 Hz alone']:.0f} -> {g['sugar 100 Hz + bitter 100 Hz']:.1f} Hz", "55 -> 3.3 Hz" if tag == "paper's model" else None)
    gb = b.groupby("condition")[["aBN1", "GF", "feed MNs"]].mean()
    check(f"JO-CE -> aBN1, JO-F -> aBN1 ({tag})", f"{gb.loc['JON-CE @ 100 Hz', 'aBN1']:.1f} / {gb.loc['JON-F @ 100 Hz', 'aBN1']:.1f} Hz", None)
    check(f"sound (JO-A/B) -> giant fiber ({tag})", f"{gb.loc['JO-A/B sound @ 100 Hz', 'GF']:.1f} Hz", None)
    check(f"head bristles -> feeding MNs ({tag})", f"{gb.loc['head bristles @ 100 Hz', 'feed MNs']:.1f} Hz", None)
check("sugar -> MN9 100/200 ratio, both lobes (draft 3: 69-75 %; 3-seed re-run of 25 Sep: 69 / 71 %)", " / ".join(f"{csv(n).groupby('condition')['MN9 L'].mean()['sugar GRNs @ 100 Hz'] / csv(n).groupby('condition')['MN9 L'].mean()['sugar GRNs @ 200 Hz']*100:.0f}" for n in ("benchmark_flywire.csv", f"benchmark_flywire_{PAPER_F}.csv") if csv(n) is not None) + " %", "69 / 71 %")

# ================================================================== B. gain windows (gain_sweep.py)
section("B. Gain window 0.7 / 1.0 / 1.4 (`gain_sweep_*.csv`, Results 2-3, Table 1, Fig 4)")
GF_, GM_ = csv(f"gain_sweep_flywire_{PAPER_F}.csv"), csv(f"gain_sweep_malecns_{PAPER_M}.csv")


def gain(d, inp, out, gains=(0.7, 1.0, 1.4), nd=0):
    g = d[d.input == inp].groupby("gain")[out].mean()
    return " / ".join(f"{g[x]:.{nd}f}" if x in g else "?" for x in gains)


emit(f"female sweep: {GF_.seed.nunique()} seeds; male sweep: {GM_.seed.nunique()} seeds (mean over seeds, 600 ms, 100 Hz)")
check("Feeding: sugar GRNs -> MN9 (female)", gain(GF_, "sugar GRNs", "MN9"), "33 / 76 / 94")
check("Startle: JO-A -> giant fiber (female)", gain(GF_, "song/sound (JO-A)", "GF jump"), "6 / 11 / 16")
check("Startle: JO-B -> giant fiber (female), for the record", gain(GF_, "sound (JO-B)", "GF jump"))
g = GM_[GM_.input == "sound (JO-B)"].groupby("gain")["GF jump"].mean()
check("Startle: JO-B -> giant fiber (male) at gain 0.5 / 0.7 / 1.0 / 1.4", " / ".join(f"{g[x]:.0f}" for x in (0.5, 0.7, 1.0, 1.4)), "34 / 41 / 48 / 54")
check("Rejection: touch -> DNp13 (female)", gain(GF_, "touch (all head bristles)", "DNp13 reject"), "28 / 36 / 42")
check("Rejection not gated by odor: cVA + touch -> DNp13", gain(GF_, "cVA + touch", "DNp13 reject"), "27 / 36 / 36")
check("Rejection not gated by odor: food + touch -> DNp13", gain(GF_, "food + touch", "DNp13 reject"), "26 / 34 / 39")
check("Male pheromone: cVA -> DNp13 (male)", gain(GM_, "cVA (Or67d/DA1)", "DNp13 reject", nd=1), "7.8 / 30 / 26")
oth = GM_[(GM_.gain <= 1.4) & GM_.input.isin(["food odor", "aversive odor (DA2/DL4)", "Or88a (VA1d)", "Or47b (VA1v)", "CO2 (V)"])]
check("Pheromone-specific: every other odor -> DNp13 (male), max over odors and gains <= 1.4", f"{oth['DNp13 reject'].max():.1f} Hz", "0")
check("Male song command: cVA -> pIP10 (male)", gain(GM_, "cVA (Or67d/DA1)", "pIP10 song cmd"), "0 / 3 / 8")
check("Male cVA -> MN9 / song MNs / PPL1", f"MN9 {gain(GM_, 'cVA (Or67d/DA1)', 'MN9')}; song MNs {gain(GM_, 'cVA (Or67d/DA1)', 'song MNs')}; PPL1 {gain(GM_, 'cVA (Or67d/DA1)', 'PPL1 (punish DA)')}")
g = GM_[GM_.input == "contact pheromone (ppk23/25)"].groupby("gain")
check("Male contact chemosensation: ppk23/25 -> song (wing) MNs at gain 0.5 / 0.7 / 1.0 / 1.4", " / ".join(f"{g['song MNs'].mean()[x]:.0f}" for x in (0.5, 0.7, 1.0, 1.4)), "10 / 20 / 22 / 11")
check("Male contact chemosensation: ppk23/25 -> MDN", gain(GM_, "contact pheromone (ppk23/25)", "MDN back", nd=1), "0 / 27 / 1.8")
check("Male touch -> MDN", gain(GM_, "touch (all head bristles)", "MDN back", nd=1), "0 / 10.7 / 11.8")
check("Male ppk25 alone -> song MNs / MDN", f"{gain(GM_, 'ppk25 only (female CHC)', 'song MNs')}; {gain(GM_, 'ppk25 only (female CHC)', 'MDN back')}")
dec_f = GF_[GF_.gain <= 1.4][["pC1a recept", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept"]].max()
check("Decision neurons silent (female): max of pC1a / pC1d/e / aIPg / vpoDN over every input at gains <= 1.4", " / ".join(f"{v:.1f}" for v in dec_f), "0.0")
dec_m = GM_[GM_.gain <= 1.0][["P1/pC1 male", "aIPg aggr"]].max(); dec_m14 = GM_[GM_.gain == 1.4][["P1/pC1 male", "aIPg aggr"]].max()
check("Decision neurons silent (male): max P1 / aIPg at gains <= 1.0; at 1.4", f"{dec_m['P1/pC1 male']:.1f} / {dec_m['aIPg aggr']:.1f}; at 1.4: {dec_m14['P1/pC1 male']:.1f} / {dec_m14['aIPg aggr']:.1f}", "0.6 / 0.0; at 1.4: 2.3 / 1.9")
od = GF_[(GF_.gain == 0.7) & GF_.input.isin(["cVA (Or67d/DA1)", "food odor", "aversive odor (DA2/DL4)", "Or88a (VA1d)", "Or47b (VA1v)", "CO2 (V)"])]
check("Odor rows need gain >= 1.0: max DNa L / R over odors at gain 0.7 (female)", f"{od['DNa L'].max():.1f} / {od['DNa R'].max():.1f}", "0.3 / 0.0")
check("cVA -> DNa L / R at gain 1.0 (female)", f"{gain(GF_, 'cVA (Or67d/DA1)', 'DNa L', (1.0,))} / {gain(GF_, 'cVA (Or67d/DA1)', 'DNa R', (1.0,))}", "9 / 8")
check("food -> DNa L / R at gain 1.0 (female)", f"{gain(GF_, 'food odor', 'DNa L', (1.0,))} / {gain(GF_, 'food odor', 'DNa R', (1.0,))}", "20 / 12")
check("food -> PPL1 (female)", gain(GF_, "food odor", "PPL1 (punish DA)", nd=1), "4.7 / 17 / 36")
check("food -> PAM (female), max over gains <= 1.4", f"{GF_[(GF_.gain <= 1.4) & (GF_.input == 'food odor')]['PAM (reward DA)'].max():.1f}", "<= 1.5")
check("food -> giant fiber (female)", gain(GF_, "food odor", "GF jump", nd=1), "0 / 3.8 / 3.3")
check("Or47b -> DNa L / R at 0.7 / 1.0 / 1.4 (female; the fragile absence)", f"{gain(GF_, 'Or47b (VA1v)', 'DNa L')} ; {gain(GF_, 'Or47b (VA1v)', 'DNa R')}", "0 / 0 / 24 ; 0 / 0 / 35")
check("Male labellar GRNs -> MN9, largest per-gain mean at gains <= 1.4", f"{GM_[(GM_.gain <= 1.4) & (GM_.input == 'sugar GRNs')].groupby('gain')['MN9'].mean().max():.1f}", "0.8")

# ================================================================== C. sensitivity tables
section("C. Sensitivity tables (`sensitivity_*.csv`, Results 1-3, Table 1, Fig 7)")
SF, SM = csv(f"sensitivity_flywire_{PAPER_F}.csv"), csv(f"sensitivity_malecns_{PAPER_M}.csv")
SFn = SF[~SF.condition.str.startswith("legacy")]; SMn = SM[~SM.condition.str.startswith("legacy")]
check("female conditions in the table", f"{len(SF)}", "14")
check("male conditions in the table (paper says 13)", f"{len(SM)}", "13")
check("sugar -> MN9 range, all female conditions but legacy; legacy", f"{rng(SFn['sugar GRNs -> MN9'], 0)}; legacy {SF[SF.condition.str.startswith('legacy')]['sugar GRNs -> MN9'].iloc[0]:.0f}", "64-95; 371")
check("touch -> DNp13 range (female, all conditions)", rng(SF["touch (all head bristles) -> DNp13 reject"], 0), "28-51")
check("cVA -> DNp13 / MN9 / pC1d/e / aIPg, max over female conditions", " / ".join(f"{SF[c].max():.1f}" for c in ("cVA (Or67d/DA1) -> DNp13 reject", "cVA (Or67d/DA1) -> MN9", "cVA (Or67d/DA1) -> pC1d/e aggr", "cVA (Or67d/DA1) -> aIPg aggr")), "0.0")
check("touch -> MDN, max over female conditions", f"{SF['touch (all head bristles) -> MDN back'].max():.1f}", "1.2")
S150 = "stimulus 150 Hz (Shiu default r_poi; the body's maximum)"
V = {"published": "published model: Shiu signs, eLN x1", "known x1": "known signs, eLN x1", "Shiu x0.25": "Shiu signs, eLN x0.25", "known x0.5": "known signs, eLN x0.5", "paper": "baseline (env model options, all conns, 100 Hz, dt 0.2)", "known x0.1": "known signs, eLN x0.1", ">= 5 syn": "connections >= 5 synapses", "Zenodo all": "Zenodo table, top_nt signs, all connections", "Zenodo >= 5": "Zenodo table, top_nt signs, >= 5 synapses (first version)"}
S = SF.set_index("condition")
order = ["published", "known x1", "Shiu x0.25", "known x0.5", "paper", "known x0.1"]
check("food -> PPL1 by lobe variant (published / known x1 / Shiu x0.25 / known x0.5 / paper / x0.1)", " / ".join(f"{S.loc[V[k], 'food odor -> PPL1 (punish DA)']:.0f}" for k in order), "111 / 101 / 17 / 27 / 17 / 17")
check("food -> PAM by lobe variant", " / ".join(f"{S.loc[V[k], 'food odor -> PAM (reward DA)']:.1f}" for k in order), "21 / 13 / 0.1 / 0.5 / 0.1 / 0.1")
check("PPL1 > PAM under food odor in every female condition", str(bool((SF["food odor -> PPL1 (punish DA)"] > SF["food odor -> PAM (reward DA)"]).all())), "True")
check("odor -> punishment dopamine at x0.25: range of food / cVA -> PPL1 in the paper's model over stimulus rates", f"{rng([S.loc[V['paper'], 'food odor -> PPL1 (punish DA)'], S.loc['stimulus 50 Hz', 'food odor -> PPL1 (punish DA)'], S.loc[V['paper'], 'cVA (Or67d/DA1) -> PPL1 (punish DA)'], S.loc[S150, 'food odor -> PPL1 (punish DA)']], 0)}", "5-20")
check("KC mean rate under food odor by variant (published / known x1 / Shiu x0.25 / known x0.5 / paper)", " / ".join(f"{S.loc[V[k], 'food odor -> KC']:.1f}" for k in order[:5]), "33 / 24.5 / 1.5 / 3.9 / 1.2")
check("food -> DNa L / R by variant (published, known x1, Shiu x0.25, paper, known x0.5, x0.1, >= 5 syn, Zenodo)", "; ".join(f"{S.loc[V[k], 'food odor -> DNa L']:.0f} / {S.loc[V[k], 'food odor -> DNa R']:.0f}" for k in ("published", "known x1", "Shiu x0.25", "paper", "known x0.5", "known x0.1", ">= 5 syn", "Zenodo all")), "36 / 5; 29 / 5; 34 / 4; 21 / 13; 21 / 25; 28 / 9; 21 / 20; 27 / 9")
check("cVA -> DNa L / R by variant (same order; Zenodo >= 5 last)", "; ".join(f"{S.loc[V[k], 'cVA (Or67d/DA1) -> DNa L']:.1f} / {S.loc[V[k], 'cVA (Or67d/DA1) -> DNa R']:.1f}" for k in ("published", "known x1", "Shiu x0.25", "paper", "known x0.5", "known x0.1", ">= 5 syn", "Zenodo all", "Zenodo >= 5")), "34 / 4; 28 / 10; 24 / 5; 10 / 7.5; 20 / 25; 5 / 0; 0 / 0; 0 / 1; 0 / 0")
check("cVA + touch -> DNp13 by variant (published / known x1 / Shiu x0.25 / known x0.5 / paper / x0.1) vs touch alone", " / ".join(f"{S.loc[V[k], 'cVA + touch -> DNp13 reject']:.1f}" for k in order) + f" vs {S.loc[V['paper'], 'touch (all head bristles) -> DNp13 reject']:.0f}", "18.6 / 19.4 / 30 / 26 / 36 / 36 vs 36")
check("food -> giant fiber: paper's model; max under the other five lobe variants and the Zenodo table", f"{S.loc[V['paper'], 'food odor -> GF jump']:.1f}; {max(S.loc[V[k], 'food odor -> GF jump'] for k in ('published', 'known x1', 'Shiu x0.25', 'known x0.5', 'known x0.1', 'Zenodo all', 'Zenodo >= 5')):.1f}", "4.4; 0.6")
check("stimulus 50 / 150 Hz: food -> DNa L / R", f"{S.loc['stimulus 50 Hz', 'food odor -> DNa L']:.0f} / {S.loc['stimulus 50 Hz', 'food odor -> DNa R']:.0f}; {S.loc[S150, 'food odor -> DNa L']:.0f} / {S.loc[S150, 'food odor -> DNa R']:.0f}", "19 / 17; 30 / 5")
Sm = SM.set_index("condition")
check("male cVA -> DNp13 range over all 13 conditions", rng(SM["cVA (Or67d/DA1) -> DNp13 reject"], 0), "12-39")
check("male cVA -> DNp13: baseline / published lobe / unclear LNs inhibitory / silent", f"{Sm.loc['baseline (env model options, all conns, 100 Hz, dt 0.2)', 'cVA (Or67d/DA1) -> DNp13 reject']:.1f} / {Sm.loc['published model: eLN x1', 'cVA (Or67d/DA1) -> DNp13 reject']:.0f} / {Sm.loc['eLN x0.25, unclear LNs inhibitory', 'cVA (Or67d/DA1) -> DNp13 reject']:.0f} / {Sm.loc['eLN x0.25, unclear LNs silent', 'cVA (Or67d/DA1) -> DNp13 reject']:.0f}", "31.7 / 25 / 36 / 29")
check("male cVA -> PPL1: unclear LNs excitatory / inhibitory / silent", " / ".join(f"{Sm.loc[c, 'cVA (Or67d/DA1) -> PPL1 (punish DA)']:.1f}" for c in ("baseline (env model options, all conns, 100 Hz, dt 0.2)", "eLN x0.25, unclear LNs inhibitory", "eLN x0.25, unclear LNs silent")), "11.8 / 0.0 / 9.6")
check("male contact pheromone -> MDN / song MNs / PPL1 (baseline); with >= 5 synapses", f"{Sm.loc['baseline (env model options, all conns, 100 Hz, dt 0.2)', 'contact pheromone (ppk23/25) -> MDN back']:.0f} / {Sm.loc['baseline (env model options, all conns, 100 Hz, dt 0.2)', 'contact pheromone (ppk23/25) -> song MNs']:.0f} / {Sm.loc['baseline (env model options, all conns, 100 Hz, dt 0.2)', 'contact pheromone (ppk23/25) -> PPL1 (punish DA)']:.0f}; {Sm.loc['connections >= 5 synapses', 'contact pheromone (ppk23/25) -> MDN back']:.1f} / {Sm.loc['connections >= 5 synapses', 'contact pheromone (ppk23/25) -> song MNs']:.0f}", "29 / 21 / 39; 6.5 / 13")
check("male touch -> MDN: baseline / 50 Hz / 150 Hz", f"{Sm.loc['baseline (env model options, all conns, 100 Hz, dt 0.2)', 'touch (all head bristles) -> MDN back']:.1f} / {Sm.loc['stimulus 50 Hz', 'touch (all head bristles) -> MDN back']:.1f} / {Sm.loc[S150, 'touch (all head bristles) -> MDN back']:.0f}", "11.5 / 0 / 28")
check("male labellar GRNs -> MN9 max; P1 max; pIP10 max over all conditions", f"{SM['sugar GRNs -> MN9'].max():.1f}; {SM['cVA (Or67d/DA1) -> P1/pC1 male'].max():.1f}; {SM['cVA (Or67d/DA1) -> pIP10 song cmd'].max():.1f}", "1.1; 2.5; 6.9 (the first two under the first-version numerics)")
check("male touch and ppk25 + touch -> DNp13, max over conditions", f"{SM['ppk25 + touch -> DNp13 reject'].max():.1f}", "0.0")
check("male cVA -> DNa L / R max over conditions (his steering is not olfactory)", f"{SM['cVA (Or67d/DA1) -> DNa L'].max():.1f} / {SM['cVA (Or67d/DA1) -> DNa R'].max():.1f}", "1.9 / 4.7")
check("male published lobe (x1): food -> PPL1 / PAM / KC; x1 with unclear LNs inhibitory", f"{Sm.loc['published model: eLN x1', 'food odor -> PPL1 (punish DA)']:.0f} / {Sm.loc['published model: eLN x1', 'food odor -> PAM (reward DA)']:.0f} / {Sm.loc['published model: eLN x1', 'food odor -> KC']:.0f}; {Sm.loc['eLN x1, unclear LNs inhibitory', 'food odor -> PPL1 (punish DA)']:.0f} / {Sm.loc['eLN x1, unclear LNs inhibitory', 'food odor -> PAM (reward DA)']:.0f} / {Sm.loc['eLN x1, unclear LNs inhibitory', 'food odor -> KC']:.0f}", "121 / 42 / 34; 14 / 0 / 2")

# ================================================================== D. shuffle
section("D. Shuffled-connectome control (`shuffle_*_global.csv`, Fig 6)")
for tag, name in (("female", f"shuffle_flywire_{PAPER_F}_global.csv"), ("male", f"shuffle_malecns_{PAPER_M}_global.csv")):
    d = csv(name)
    outs = [c for c in d.columns if c not in {"seed", "n_driven", "total_spikes", "active_frac", "wall_s", "connectome", "shuffle", "frac_moved", "input"}]
    rew = d[(d.connectome != "intact") & (d.input != "none")]; intact = d[(d.connectome == "intact")].groupby("input")[outs].mean()
    top = rew[outs].max().sort_values(ascending=False)
    emit(f"- {tag}: {rew.shuffle.nunique()} rewirings x {rew.seed.nunique()} seeds, {d.frac_moved.max()*100:.1f} % of connections moved; intact key cells: " +
         ", ".join(f"{i.split(' ')[0]} -> {o.split(' ')[0]} {intact.loc[i, o]:.0f}" for i, o in [("sugar GRNs", "MN9"), ("touch (all head bristles)", "DNp13 reject"), ("cVA (Or67d/DA1)", "DNa L"), ("food odor", "PPL1 (punish DA)"), ("cVA (Or67d/DA1)", "DNp13 reject"), ("contact pheromone (ppk23/25)", "MDN back"), ("sound (JO-B)", "GF jump")] if i in intact.index and o in intact.columns))
    check(f"  {tag} rewired: largest value of any readout under any input (max over rewired brains and seeds), top 3", ", ".join(f"{k} {v:.1f}" for k, v in top.head(3).items()), None)
    check(f"  {tag} rewired: mean of every readout over rewired trials, max", f"{rew.groupby('input')[outs].mean().max().max():.1f} Hz", "2 Hz")

# ================================================================== E. innate map (social_probe.py)
section("E. Innate map, paper's model (`social_probe_*_noise0.csv`, Results 3, 5; Fig 1)")
PF, PM = csv(f"social_probe_flywire_{PAPER_F}_noise0.csv"), csv(f"social_probe_malecns_{PAPER_M}_noise0.csv")
gf = PF.groupby("input").mean(numeric_only=True); gm = PM.groupby("input").mean(numeric_only=True)
check("female decision neurons, max over every input: pC1a / pC1b/c / pC1d/e / aIPg / vpoDN / oviDN", " / ".join(f"{gf[c].max():.1f}" for c in ("pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "oviDN egg")), "0.0")
check("male P1 / pIP10, max over every input", f"{gm['P1/pC1 male'].max():.1f} / {gm['pIP10 song cmd'].max():.1f}", "0.5 / 3.5")
check("teaching signal not in the wiring: sugar / bitter / touch -> PAM, PPL1 (female)", "; ".join(f"{i.split(' ')[0]} {gf.loc[i, 'PAM (reward DA)']:.1f} / {gf.loc[i, 'PPL1 (punish DA)']:.1f}" for i in ("sugar GRNs", "bitter GRNs", "touch (all head bristles)")), "0.0 / 0.0; 0.0 / 0.0; 0.0 / 0.0")
check("cVA -> DNa L / R (female, symmetric)", f"{gf.loc['cVA (Or67d/DA1)', 'DNa L']:.0f} / {gf.loc['cVA (Or67d/DA1)', 'DNa R']:.0f}", "10 / 8")
check("Or47b -> DNa L / R, DN all, KC (female: fly odor reaches nothing)", f"{gf.loc['Or47b (VA1v)', 'DNa L']:.1f} / {gf.loc['Or47b (VA1v)', 'DNa R']:.1f}, {gf.loc['Or47b (VA1v)', 'DN all']:.2f}, {gf.loc['Or47b (VA1v)', 'KC']:.2f}", "0.0 / 0.0, 0.01, 0.00")
check("CO2 -> DNa L / R (female)", f"{gf.loc['CO2 (V)', 'DNa L']:.0f} / {gf.loc['CO2 (V)', 'DNa R']:.0f}")
check("touch -> DNp13 / feeding MNs / MDN (female, 1 s)", f"{gf.loc['touch (all head bristles)', 'DNp13 reject']:.1f} / {gf.loc['touch (all head bristles)', 'feed MNs']:.1f} / {gf.loc['touch (all head bristles)', 'MDN back']:.1f}", "36 / 16 / 0")
check("male: touch -> MDN; ppk25 + touch -> MDN; cVA + touch -> DNp13", f"{gm.loc['touch (all head bristles)', 'MDN back']:.1f}; {gm.loc['ppk25 + touch', 'MDN back']:.1f}; {gm.loc['cVA + touch', 'DNp13 reject']:.1f}", "10.7; 22.4; 7.3")
check("male: contact pheromone -> MDN / wing MNs / song MNs / leg MNs", f"{gm.loc['contact pheromone (ppk23/25)', 'MDN back']:.0f} / {gm.loc['contact pheromone (ppk23/25)', 'wing MNs']:.0f} / {gm.loc['contact pheromone (ppk23/25)', 'song MNs']:.0f} / {gm.loc['contact pheromone (ppk23/25)', 'leg MNs']:.1f}")
check("male: ppk25 alone -> leg MNs / MDN", f"{gm.loc['ppk25 only (female CHC)', 'leg MNs']:.1f} / {gm.loc['ppk25 only (female CHC)', 'MDN back']:.0f}", "1.5 / 13")
check("male: Or47b / CO2 -> DN all, leg MNs (the female's odor reaches nothing in him)", f"{gm.loc['Or47b (VA1v)', 'DN all']:.2f} / {gm.loc['Or47b (VA1v)', 'leg MNs']:.2f}; {gm.loc['CO2 (V)', 'DN all']:.2f} / {gm.loc['CO2 (V)', 'leg MNs']:.2f}")

# ================================================================== F. state arm
section("F. State arm (`state_probe_*_state30.csv`, Results 4, Table 1, Fig 5)")
ST = {("f", "paper"): csv(f"state_probe_flywire_{PAPER_F}_state30.csv"), ("f", "pub"): csv("state_probe_flywire_shiu_min1_state30.csv"),
      ("m", "paper"): csv(f"state_probe_malecns_{PAPER_M}_state30.csv"), ("m", "pub"): csv("state_probe_malecns_all_min1_state30.csv")}
G = {k: v.groupby(["state", "input"]).mean(numeric_only=True) for k, v in ST.items()}


def st(sex, state, inp, out, nd=1):
    return f"{G[(sex, 'pub')].loc[(state, inp), out]:.{nd}f} -> {G[(sex, 'paper')].loc[(state, inp), out]:.{nd}f}"


emit(f"(published lobe -> paper's model; female {ST[('f','paper')].seed.nunique()} seeds, male {ST[('m','paper')].seed.nunique()} seeds, 1 s, state neurons 30 Hz)")
check("SAG tonic alone -> pC1a", st("f", "virgin (SAG tonic)", "none", "pC1a recept"), "21.2 -> 21.2")
check("SAG tonic alone -> pC1b/c", st("f", "virgin (SAG tonic)", "none", "pC1b/c"), "19.0 -> 19.0")
check("SAG tonic alone -> vpoDN", st("f", "virgin (SAG tonic)", "none", "vpoEN/DN accept"), "5.7 -> 5.7")
check("SAG + touch -> pC1d/e", st("f", "virgin (SAG tonic)", "touch (all head bristles)", "pC1d/e aggr"), "6.3 -> 6.2")
check("SAG + cVA + touch -> pC1d/e (no longer masked by odor)", st("f", "virgin (SAG tonic)", "cVA + touch", "pC1d/e aggr"), "1.1 -> 7.1")
check("pC1a-c tonic -> vpoDN; + touch -> pC1d/e", f"{st('f', 'aroused female (pC1a-c tonic)', 'none', 'vpoEN/DN accept')}; {st('f', 'aroused female (pC1a-c tonic)', 'touch (all head bristles)', 'pC1d/e aggr')}", "8.7 -> 8.7; 9.6 -> 9.4")
ODORS3 = ("cVA (Or67d/DA1)", "Or47b (VA1v)", "food odor")
check("SAG + odor -> pC1a (cVA / Or47b / food), paper's model (published in brackets)", " / ".join(f"{G[('f', 'paper')].loc[('virgin (SAG tonic)', i), 'pC1a recept']:.1f}" for i in ODORS3) + " (" + " / ".join(f"{G[('f', 'pub')].loc[('virgin (SAG tonic)', i), 'pC1a recept']:.1f}" for i in ODORS3) + ")", "21.5 / 22.5 / 19.6 (17.5 / 17.9 / 16.1)")
check("aIPg tonic -> DNa L / R at rest; aIPg + cVA vs cVA without a state", f"{G[('f', 'paper')].loc[('aggressive female (aIPg tonic)', 'none'), 'DNa L']:.1f} / {G[('f', 'paper')].loc[('aggressive female (aIPg tonic)', 'none'), 'DNa R']:.1f}; {G[('f', 'paper')].loc[('aggressive female (aIPg tonic)', 'cVA (Or67d/DA1)'), 'DNa L']:.1f} / {G[('f', 'paper')].loc[('aggressive female (aIPg tonic)', 'cVA (Or67d/DA1)'), 'DNa R']:.1f} vs {G[('f', 'paper')].loc[('none', 'cVA (Or67d/DA1)'), 'DNa L']:.1f} / {G[('f', 'paper')].loc[('none', 'cVA (Or67d/DA1)'), 'DNa R']:.1f}", "8.7 / 7.7; 24.8 / 21.8 vs 10.1 / 8.4")
dn = G[("f", "paper")].xs("touch (all head bristles)", level="input")["DNp13 reject"]
check("touch -> DNp13 across all female states (state-blind)", rng(dn.values), "35.6-37.9")
check("oviDN, max over every state and input (female)", f"{G[('f', 'paper')]['oviDN egg'].max():.1f}", "0.0")
show_f = [k for k in ("pC1a recept", "pC1b/c", "pC1d/e aggr", "aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "oviDN egg", "MN9", "feed MNs", "DNa L", "DNa R", "MDN back", "PPL1 (punish DA)", "KC", "GF jump", "DNp09") if k in G[("f", "paper")].columns]
for sex, states, show in (("f", ["fed (IPC tonic)", "fed (DH44 tonic)", "hungry (NPF tonic)", "SIFa tonic", "AstA tonic"], show_f),
                          ("m", ["fed (IPC tonic)", "fed (DH44 tonic)", "hungry (NPF tonic)", "SIFa tonic", "AstA tonic"], [k for k in ("aIPg aggr", "vpoEN/DN accept", "DNp13 reject", "P1/pC1 male", "pIP10 song cmd", "TN1 song", "song MNs", "wing MNs", "MN9", "feed MNs", "DNa L", "DNa R", "MDN back", "PPL1 (punish DA)", "KC", "leg MNs") if k in G[("m", "paper")].columns])):
    g = G[(sex, "paper")]; base = g.loc["none"]; worst = []
    for s_ in states:
        if s_ not in g.index.get_level_values(0):
            continue
        dd = (g.loc[s_][show] - base.reindex(g.loc[s_].index)[show]).abs(); k = dd.stack().idxmax()
        worst.append((s_, dd.stack().max(), k[1], k[0]))
    check(f"hunger / satiety states ({'female' if sex == 'f' else 'male'}): largest |change| of any readout under any input vs no state", "; ".join(f"{s_.split(' ')[0]} {v:.1f} ({o} with {i})" for s_, v, o, i in worst), None)
sug = G[("f", "paper")].xs("sugar GRNs", level="input")
check("sugar -> MN9 under no state / NPF / AstA / DH44 / IPC / SAG / pC1a-c / aIPg (female)", " / ".join(f"{sug.loc[s_, 'MN9']:.1f}" for s_ in ("none", "hungry (NPF tonic)", "AstA tonic", "fed (DH44 tonic)", "fed (IPC tonic)", "virgin (SAG tonic)", "aroused female (pC1a-c tonic)", "aggressive female (aIPg tonic)")), "79.4 / 86.2 / 77.8 / 82.4 / 80.0 / 83.8 / 83.6 / 83.0")
check("sugar -> feeding-MN population, range across all female states", rng(sug["feed MNs"].values), "24.8-26.7")
check("P1 tonic alone -> pIP10 / TN1 / song MNs / wing MNs / DNp13 / MN9 (male)", "; ".join(st("m", "courting male (P1/pC1 tonic)", "none", o) for o in ("pIP10 song cmd", "TN1 song", "song MNs", "wing MNs", "DNp13 reject", "MN9")), "50.4 -> 50.4; 8.2 -> 8.2; 27.6 -> 27.6; 9.1 -> 9.1; 20.6 -> 20.6; 2.7 -> 2.7")
check("P1 + food odor -> pIP10; P1 + Or47b -> pIP10", f"{st('m', 'courting male (P1/pC1 tonic)', 'food odor', 'pIP10 song cmd')}; {st('m', 'courting male (P1/pC1 tonic)', 'Or47b (VA1v)', 'pIP10 song cmd')}", "40.7 -> 49.1; 41.7 -> 49.2")
check("P1 + odor -> MN9 (food / Or47b), published -> paper", f"{st('m', 'courting male (P1/pC1 tonic)', 'food odor', 'MN9')}; {st('m', 'courting male (P1/pC1 tonic)', 'Or47b (VA1v)', 'MN9')}", "19.4 -> 2.6; 18.6 -> 0.7")
check("P1 + cVA -> DNp13; -> pIP10; -> MN9", f"{st('m', 'courting male (P1/pC1 tonic)', 'cVA (Or67d/DA1)', 'DNp13 reject')}; {st('m', 'courting male (P1/pC1 tonic)', 'cVA (Or67d/DA1)', 'pIP10 song cmd')}; {st('m', 'courting male (P1/pC1 tonic)', 'cVA (Or67d/DA1)', 'MN9')}", "41 -> 54; 42 -> 45; 27 -> 31")
check("male cVA + touch -> MDN, no state; all pheromones + contact + touch -> MDN", f"{st('m', 'none', 'cVA + touch', 'MDN back')}; {st('m', 'none', 'all pheromones + contact + touch', 'MDN back')}", "0.0 -> 25; 1.4 -> 53")
check("male aIPg tonic -> song MNs / wing MNs at rest; aIPg + cVA -> DNp13 vs no state", f"{G[('m', 'paper')].loc[('aggressive female (aIPg tonic)', 'none'), 'song MNs']:.1f} / {G[('m', 'paper')].loc[('aggressive female (aIPg tonic)', 'none'), 'wing MNs']:.1f}; {G[('m', 'paper')].loc[('aggressive female (aIPg tonic)', 'cVA (Or67d/DA1)'), 'DNp13 reject']:.0f} vs {G[('m', 'paper')].loc[('none', 'cVA (Or67d/DA1)'), 'DNp13 reject']:.0f}", "4 / 1.2; 35 vs 30")
check("male sugar -> MN9 max over all states (pooled taste labels)", f"{G[('m', 'paper')].xs('sugar GRNs', level='input')['MN9'].max():.1f}", "0")

# ================================================================== G. stop on contact
section("G. Stop on contact (`contact_stop_*.csv`, Results 2, Table 1, Fig 12)")
CF, CM = csv("contact_stop_flywire.csv"), csv("contact_stop_malecns.csv")
emit(f"(female file: {CF.condition.nunique()} conditions x {CF.drive.nunique()} drives; seeds per cell not stored — see logs/contact_stop_flywire*.out)")
notz5 = CF[~CF.condition.str.contains(">= 5")]
pivf = CF.pivot_table(index="condition", columns="drive", values="suppression").round(2)
emit("female suppression index by condition (rows) and walking drive (columns):"); emit(); emit("| condition | " + " | ".join(pivf.columns) + " |"); emit("|---|" + "---|" * len(pivf.columns))
for c_, r in pivf.iterrows():
    emit(f"| {c_} | " + " | ".join("-" if not np.isfinite(v) else f"{v:.2f}" for v in r.values) + " |")
emit()
food_all = notz5[notz5.drive == "food odor"]
check("index range with food odor as the drive, every full-table variant, with and without the substrate", rng(food_all.suppression.values, 2), "0.5-0.9")
driven = notz5[notz5["DNa alone"] >= 2.0]
check("index range over every cell with a real walking drive (DNa alone >= 2 Hz), every full-table variant, +- substrate", rng(driven.suppression.values, 2), "0.35-0.93")
pubv = driven[driven.condition.str.startswith("published")]; papv = driven[driven.condition.str.startswith("paper")]
check("  of which the published lobe (Shiu signs, eLN x1); the paper's model", f"{rng(pubv.suppression.values, 2)}; {rng(papv.suppression.values, 2)}", "0.35-0.59; 0.69-0.93")
pmc = CF[CF.condition == "paper's model: known signs, eLN x0.25"].set_index("drive")
check("paper's model: cVA -> DNa L / R alone -> + touch", f"{pmc.loc['cVA (Or67d/DA1)', 'DNa L alone']:.1f} / {pmc.loc['cVA (Or67d/DA1)', 'DNa R alone']:.1f} -> {pmc.loc['cVA (Or67d/DA1)', 'DNa L +touch']:.1f} / {pmc.loc['cVA (Or67d/DA1)', 'DNa R +touch']:.1f}", "9.3 / 8.2 -> 0.0 / 1.2")
z5c = CF[CF.condition.str.contains(">= 5") & (CF.noise_hz == 0)].set_index("drive")
check("Zenodo >= 5: cVA / Or47b alone -> + touch, DNa L / R (the bristles drive the DNa with no odor drive at all)", f"{z5c.loc['cVA (Or67d/DA1)', 'DNa L alone']:.1f} / {z5c.loc['cVA (Or67d/DA1)', 'DNa R alone']:.1f} -> {z5c.loc['cVA (Or67d/DA1)', 'DNa L +touch']:.1f} / {z5c.loc['cVA (Or67d/DA1)', 'DNa R +touch']:.1f}; {z5c.loc['Or47b (VA1v)', 'DNa L alone']:.1f} / {z5c.loc['Or47b (VA1v)', 'DNa R alone']:.1f} -> {z5c.loc['Or47b (VA1v)', 'DNa L +touch']:.1f} / {z5c.loc['Or47b (VA1v)', 'DNa R +touch']:.1f}", "0 / 0 -> 7 / 17; 0 / 0 -> 8 / 17")
check("suppression index range, every sign rule / eLN scale / full table, with and without the substrate (excl. >= 5-synapse threshold)", rng(notz5.suppression.values, 2), "-0.00-0.93")
pm = CF[CF.condition == "paper's model: known signs, eLN x0.25"].set_index("drive")
check("paper's model, no substrate: food -> DNa L / R alone -> + touch; index food / cVA", f"{pm.loc['food odor', 'DNa L alone']:.1f} / {pm.loc['food odor', 'DNa R alone']:.1f} -> {pm.loc['food odor', 'DNa L +touch']:.1f} / {pm.loc['food odor', 'DNa R +touch']:.1f}; {pm.loc['food odor', 'suppression']:.2f} / {pm.loc['cVA (Or67d/DA1)', 'suppression']:.2f}", "20.3 / 12.3 -> 6.8 / 3.2; 0.69 / 0.93")
check("paper's model, index range over drives (no substrate)", rng(pm.suppression.values, 2), "0.69-0.93")
pmn = CF[CF.condition == "paper's model: known signs, eLN x0.25 + noise 0.2 Hz"].set_index("drive")
check("paper's model + 0.2 Hz substrate: index for food / cVA / Or47b / substrate alone", " / ".join(f"{pmn.loc[d_, 'suppression']:.2f}" if d_ in pmn.index and np.isfinite(pmn.loc[d_, 'suppression']) else "-" for d_ in ("food odor", "cVA (Or67d/DA1)", "Or47b (VA1v)", "none")), "0.77 / 0.91 / 0.89 / 0.82")
check("all conditions with the substrate (excl. >= 5): index range", rng(notz5[notz5.noise_hz > 0].suppression.values, 2), "0.40-0.91")
z5 = CF[CF.condition.str.contains(">= 5") & (CF.noise_hz == 0)].set_index("drive")
check("Zenodo >= 5 synapses (first version): food alone -> + touch DNa L / R; index; touch alone -> DNa L / R", f"{z5.loc['food odor', 'DNa L alone']:.1f} / {z5.loc['food odor', 'DNa R alone']:.1f} -> {z5.loc['food odor', 'DNa L +touch']:.1f} / {z5.loc['food odor', 'DNa R +touch']:.1f}; {z5.loc['food odor', 'suppression']:.2f}; " + (f"{CF[CF.condition.str.contains('>= 5') & (CF.noise_hz > 0)].set_index('drive').loc['none', 'DNa L +touch']:.1f} / {CF[CF.condition.str.contains('>= 5') & (CF.noise_hz > 0)].set_index('drive').loc['none', 'DNa R +touch']:.1f} (with substrate)"), "27.8 / 10.5 -> 17.3 / 17.8; 0.08; 10.2 / 17.0")
check("female MDN with touch, max over every condition and drive", f"{CF['MDN back +touch'].max():.1f}", "1.3")
check("DNp13 with touch: paper's model / published / range over all conditions", f"{pm.loc['food odor', 'DNp13 reject +touch']:.0f} / {CF[CF.condition == 'published model: Shiu signs, eLN x1'].set_index('drive').loc['food odor', 'DNp13 reject +touch']:.0f} / {rng(CF['DNp13 reject +touch'].values, 0)}", "34 / 17 / 17-38")
m25 = CM[CM.eln_scale == 0.25]; m1 = CM[CM.eln_scale == 1.0]
check("male: head bristles -> MDN with touch, eLN x0.25 settings (all drives, +- substrate): range", rng(m25["MDN back +touch"].values, 0), "2-34")
check("male: head bristles -> MDN with touch under the published lobe (eLN x1): range", rng(m1["MDN back +touch"].values, 1), "0.0-23.0")
mp = CM[CM.condition == "paper's model: eLN x0.25"].set_index("drive")
check("male paper's model: ppk23/25 -> DNa L / R alone -> + touch; index", f"{mp.loc['contact pheromone (ppk23/25)', 'DNa L alone']:.1f} / {mp.loc['contact pheromone (ppk23/25)', 'DNa R alone']:.1f} -> {mp.loc['contact pheromone (ppk23/25)', 'DNa L +touch']:.1f} / {mp.loc['contact pheromone (ppk23/25)', 'DNa R +touch']:.1f}; {mp.loc['contact pheromone (ppk23/25)', 'suppression']:.2f}", "8.2 / 4.7 -> 0.0 / 0.0; 1.00")
check("male paper's model: ppk25 + touch -> MDN; cVA + touch -> MDN; leg MNs alone -> + touch (ppk)", f"{mp.loc['contact pheromone (ppk23/25)', 'MDN back +touch']:.0f}; {mp.loc['cVA (Or67d/DA1)', 'MDN back +touch']:.0f}; {mp.loc['contact pheromone (ppk23/25)', 'leg MNs alone']:.1f} -> {mp.loc['contact pheromone (ppk23/25)', 'leg MNs +touch']:.1f}", "23; 26; 2.9 -> 1.8")
check("male: cVA -> DNp13 alone -> with touch (paper's model)", f"{mp.loc['cVA (Or67d/DA1)', 'DNp13 reject alone']:.0f} -> {mp.loc['cVA (Or67d/DA1)', 'DNp13 reject +touch']:.1f}", "30 -> 7.7")

# ================================================================== H. walking substrate
section("H. The walking substrate (`noise_floor_*.csv`, Results 6, Fig 13)")
NF, NF10 = csv(f"noise_floor_flywire_{PAPER_F}.csv"), csv(f"noise_floor_flywire_{PAPER_F}_10s.csv")
NM, NM10 = csv(f"noise_floor_malecns_{PAPER_M}.csv"), csv(f"noise_floor_malecns_{PAPER_M}_10s.csv")
n = NF.groupby(["noise_hz", "input"]).mean(numeric_only=True)
check("1 s onset, female, no input, 0.2 Hz: DNa L / R; GF; feeding MNs; DNp13; active fraction", f"{n.loc[(0.2, 'none'), 'DNa L']:.1f} / {n.loc[(0.2, 'none'), 'DNa R']:.1f}; {n.loc[(0.2, 'none'), 'GF jump']:.1f}; {n.loc[(0.2, 'none'), 'feed MNs']:.1f}; {n.loc[(0.2, 'none'), 'DNp13 reject']:.1f}; {n.loc[(0.2, 'none'), 'active_frac']*100:.0f} %", "7.0 / 7.0; 3.2; 2.8; 0.5; 19 %")
check("1 s, 0.2 Hz: touch -> DNp13; touch -> DNa L / R; food -> DNa L / R; food + touch -> DNa; sugar -> feed MNs (vs 0 Hz)", f"{n.loc[(0.2, 'touch (all head bristles)'), 'DNp13 reject']:.1f} ({n.loc[(0.0, 'touch (all head bristles)'), 'DNp13 reject']:.1f}); {n.loc[(0.2, 'touch (all head bristles)'), 'DNa L']:.1f} / {n.loc[(0.2, 'touch (all head bristles)'), 'DNa R']:.1f}; {n.loc[(0.2, 'food odor'), 'DNa L']:.1f} / {n.loc[(0.2, 'food odor'), 'DNa R']:.1f} ({n.loc[(0.0, 'food odor'), 'DNa L']:.1f} / {n.loc[(0.0, 'food odor'), 'DNa R']:.1f}); {n.loc[(0.2, 'food + touch'), 'DNa L']:.1f} / {n.loc[(0.2, 'food + touch'), 'DNa R']:.1f}; {n.loc[(0.2, 'sugar GRNs'), 'feed MNs']:.1f} ({n.loc[(0.0, 'sugar GRNs'), 'feed MNs']:.1f})", "35.3 (35.8); 2.7 / 1.2; 24.8 / 19.7 (23 / 14); 6.8 / 3.3; 24.7 (24.1)")
check("1 s, giant fiber with no input at 0.2 / 0.3 / 0.5 Hz", " / ".join(f"{n.loc[(x, 'none'), 'GF jump']:.1f}" for x in (0.2, 0.3, 0.5)), "3.2 / 7.0 / 5.8")
n10 = NF10.groupby(["noise_hz", "input"]).mean(numeric_only=True)
check("10 s steady state, female, no input: DNa L / R at 0.1 / 0.2 / 0.3 Hz", "; ".join(f"{n10.loc[(x, 'none'), 'DNa L']:.1f} / {n10.loc[(x, 'none'), 'DNa R']:.1f}" for x in (0.1, 0.2, 0.3)), "17.0 / 18.8; 18.1 / 20.4; 20 / 22")
check("10 s steady state, 0.2 Hz: touch -> DNa L / R and DNp13; GF no input; feeding MNs no input; DNp13 no input", f"{n10.loc[(0.2, 'touch (all head bristles)'), 'DNa L']:.1f} / {n10.loc[(0.2, 'touch (all head bristles)'), 'DNa R']:.1f}, {n10.loc[(0.2, 'touch (all head bristles)'), 'DNp13 reject']:.1f}; {n10.loc[(0.2, 'none'), 'GF jump']:.1f}; {n10.loc[(0.2, 'none'), 'feed MNs']:.1f}; {n10.loc[(0.2, 'none'), 'DNp13 reject']:.2f}", "5.2 / 2.8, 28.9; 2.7; 5.2; 0.22")
check("10 s steady state, sugar -> MN9 at 0.2 Hz vs 1 s / 0 Hz", f"{n10.loc[(0.2, 'sugar GRNs'), 'MN9']:.0f} vs {n.loc[(0.0, 'sugar GRNs'), 'MN9']:.0f}")
m = NM.groupby(["noise_hz", "input"]).mean(numeric_only=True)
check("male, 1 s at 0.2 Hz, no input: leg MNs; DNa L / R; MDN; P1", f"{m.loc[(0.2, 'none'), 'leg MNs']:.1f}; {m.loc[(0.2, 'none'), 'DNa L']:.1f} / {m.loc[(0.2, 'none'), 'DNa R']:.1f}; {m.loc[(0.2, 'none'), 'MDN back']:.1f}; {m.loc[(0.2, 'none'), 'P1/pC1 male']:.2f}", "0.4; 1.2 / 1.5; 0.3; 0.20")
check("male, 1 s at 0.2 Hz: cVA -> DNp13 (vs 0 Hz); touch -> MDN (vs 0); ppk25 + touch -> MDN (vs 0); food -> DNp13", f"{m.loc[(0.2, 'cVA (Or67d/DA1)'), 'DNp13 reject']:.0f} ({m.loc[(0.0, 'cVA (Or67d/DA1)'), 'DNp13 reject']:.0f}); {m.loc[(0.2, 'touch (all head bristles)'), 'MDN back']:.1f} ({m.loc[(0.0, 'touch (all head bristles)'), 'MDN back']:.1f}); {m.loc[(0.2, 'ppk25 + touch'), 'MDN back']:.0f} ({m.loc[(0.0, 'ppk25 + touch'), 'MDN back']:.0f}); {m.loc[(0.2, 'food odor'), 'DNp13 reject']:.1f}", "22 (31); 17.8 (10.7); 28 (22); 0.3")
m10 = NM10.groupby(["noise_hz", "input"]).mean(numeric_only=True)
check("male, 10 s steady state at 0.2 Hz: leg MNs; MDN; contact pheromone -> MDN / leg MNs", f"{m10.loc[(0.2, 'none'), 'leg MNs']:.1f}; {m10.loc[(0.2, 'none'), 'MDN back']:.1f}; {m10.loc[(0.2, 'contact pheromone (ppk23/25)'), 'MDN back']:.1f} / {m10.loc[(0.2, 'contact pheromone (ppk23/25)'), 'leg MNs']:.1f}", "1.2; 3.2; 10.8 / 3.0")

# ================================================================== I. odor identity
section("I. Odor identity (`odor_code_*.csv`, Results 1, Table 1, Fig 9)")
for tag, name in (("female", "odor_code_flywire.csv"), ("male", "odor_code_malecns.csv")):
    d = csv(name); ov = csv(name.replace(".csv", "_overlap.csv"))
    for v in dict.fromkeys(d.variant):
        s_ = d[d.variant == v]; o = ov[ov.variant == v]
        emit(f"- {tag} `{v}`: glomeruli > 10 Hz {s_.glomeruli_over_10hz.mean()*100:.0f} % (range over odors {s_.groupby('odor').glomeruli_over_10hz.mean().min()*100:.0f}-{s_.groupby('odor').glomeruli_over_10hz.mean().max()*100:.0f}); "
             f"PNs active {s_.pn_active.mean()*100:.0f} %, PN mean {s_.pn_mean_hz.mean():.0f} Hz; KC active {s_.groupby('odor').kc_active.mean().min()*100:.1f}-{s_.groupby('odor').kc_active.mean().max()*100:.1f} % (mean {s_.kc_active.mean()*100:.0f} %), KC mean {s_.kc_hz.mean():.1f} Hz; "
             f"Jaccard same odor {o[o.same_odor].jaccard.mean():.2f}, different odors {o[~o.same_odor].jaccard.mean():.2f}; eLN {s_.eln_hz.mean():.0f} Hz; n odors {s_.odor.nunique()}, seeds {s_.seed.nunique()}")
d = csv("odor_code_flywire.csv"); ov = csv("odor_code_flywire_overlap.csv")
p = d[d.variant == "known+eln0.25"]; po = ov[ov.variant == "known+eln0.25"]
check("paper's model: glomeruli %, KC % per odor, overlap within / between", f"{p.groupby('odor').glomeruli_over_10hz.mean().min()*100:.0f}-{p.groupby('odor').glomeruli_over_10hz.mean().max()*100:.0f} %; {p.groupby('odor').kc_active.mean().min()*100:.0f}-{p.groupby('odor').kc_active.mean().max()*100:.0f} %; {po[po.same_odor].jaccard.mean():.2f} / {po[~po.same_odor].jaccard.mean():.2f}", "2-28 %; 0-5 %; 0.63 / 0.08")
p = d[d.variant == "shiu"]; po = ov[ov.variant == "shiu"]
check("published lobe: PNs active %, glomeruli > 10 Hz, KC active %, overlap between odors", f"{p.pn_active.mean()*100:.0f} % at {p.pn_mean_hz.mean():.0f} Hz; {p.glomeruli_over_10hz.mean()*59:.0f} of 59; {p.kc_active.mean()*100:.0f} %; {po[~po.same_odor].jaccard.mean():.2f}", "80 % at ~80 Hz; 57 of 59; 65 %; 0.99")
check("known signs x1 / x0.5 / x0.1: glomeruli %; overlap between odors", "; ".join(f"{d[d.variant == v].glomeruli_over_10hz.mean()*100:.0f} % / {ov[(ov.variant == v) & ~ov.same_odor].jaccard.mean():.2f}" for v in ("known", "known+eln0.5", "known+eln0.1")), "89 % / 0.77; 64 % / 0.53; 3 % / 0.01")

# ================================================================== J. odor dose / steering
section("J. Odor concentration sweep and steering (`odor_dose_*.csv`, Results 3, Table 1, Fig 10)")


def steer(d):
    piv = d.pivot_table(index=["odor", "hz", "seed"], columns="side", values="approach (ipsi-contra)")
    s_ = ((piv["L"] + piv["R"]) / 2).rename("steer").reset_index(); b = ((piv["L"] - piv["R"]) / 2).rename("bias").reset_index()
    return s_.merge(b).groupby(["odor", "hz"]).mean(numeric_only=True)


for tag, name, paper in (("paper's rule", f"odor_dose_flywire_{PAPER_F}.csv", "food -4.8 / -2.7 / -6.6 / -3.7 / -9.2; food-type odors -1 to -9; CO2 / cVA / aversive within +-2.8; bias -6 to +6"),
                         ("Shiu signs x0.25", "odor_dose_flywire_shiu_min1+eln0.25.csv", "steering within +-4; bias 15-29 for every odor at every dose"),
                         ("Zenodo table", "odor_dose_flywire_zenodo_min1+known+eln0.25.csv", "steering within +-2 (a few +5-6 at 150); bias 5-15 food-type, 0 cVA / aversive"),
                         ("male", f"odor_dose_malecns_{PAPER_M}.csv", "steering and bias <= 1.5 for every odor (cVA +2.6 at 150)")):
    d = csv(name)
    if d is None:
        continue
    s_ = steer(d)
    food = s_.loc[["food", "sweet", "vinegar", "ester"]] if tag != "male" else s_
    food_steer = " / ".join(f"{s_.loc[('food', h), 'steer']:+.1f}" for h in (25, 50, 75, 100, 150))
    emit(f"- **{tag}** ({d.seed.nunique()} seeds): steering food {food_steer}; "
         f"food-type odors (food, sweet, vinegar, ester) steering range {rng(food.steer.values)}, bias range {rng(food.bias.values)}; "
         f"CO2 / cVA / aversive steering range {rng(s_.loc[[o for o in ('CO2', 'cVA', 'aversive') if o in s_.index.get_level_values(0)]].steer.values)}, bias {rng(s_.loc[[o for o in ('CO2', 'cVA', 'aversive') if o in s_.index.get_level_values(0)]].bias.values)}; "
         f"all odors: |steering| max {s_.steer.abs().max():.1f}, bias range {rng(s_.bias.values)}")
    emit(f"  paper: {paper}")
d = csv(f"odor_dose_flywire_{PAPER_F}.csv"); s_ = steer(d)
check("food-type odor steering is negative at every dose (paper's rule): number of (odor, dose) cells with steering >= 0 among food / sweet / vinegar / ester", f"{int((s_.loc[['food', 'sweet', 'vinegar', 'ester']].steer >= 0).sum())} of {len(s_.loc[['food', 'sweet', 'vinegar', 'ester']])}", "0 of 20")
bi = d[d.side == "both"].groupby(["odor", "hz"]).mean(numeric_only=True)
check("bilateral food -> DNa L / R at 25 / 75 / 100 / 150 Hz", "; ".join(f"{bi.loc[('food', h), 'DNa L']:.0f} / {bi.loc[('food', h), 'DNa R']:.0f}" for h in (25, 75, 100, 150)), "16 / 18; 21 / 21; 23 / 14; 30 / 6")
check("bilateral cVA -> DNa L / R at 25 / 50 / 75 / 100 / 150 Hz (the dose curve's dip, 19b)", "; ".join(f"{bi.loc[('cVA', h), 'DNa L']:.1f} / {bi.loc[('cVA', h), 'DNa R']:.1f}" for h in (25, 50, 75, 100, 150)), "9.5 / 10.3; 11.5 / 11.0; 6.0 / 6.2; 9.2 / 8.0; 12.2 / 5.5")
check("giant fiber, food-type odors bilateral, range over doses", rng(bi.loc[["food", "sweet", "vinegar", "ester"]]["GF jump"].values), "0.0-5.5")
check("food -> PPL1 at 25 / 50 / 75 / 100 / 150 Hz; KC active %", " / ".join(f"{bi.loc[('food', h), 'PPL1 (punish DA)']:.0f}" for h in (25, 50, 75, 100, 150)) + "; " + " / ".join(f"{bi.loc[('food', h), 'KC active %']:.1f}" for h in (25, 50, 75, 100, 150)), "8 / 11 / 15 / 18 / 21; 3.0 / 4.4 / 5.3 / 6.0 / 7.2")
dm = csv(f"odor_dose_malecns_{PAPER_M}.csv"); bm = dm[dm.side == "both"].groupby(["odor", "hz"]).mean(numeric_only=True)
check("male cVA -> DNp13 at 25 / 50 / 75 / 100 / 150 Hz (dose-graded)", " / ".join(f"{bm.loc[('cVA', h), 'DNp13 reject']:.1f}" for h in (25, 50, 75, 100, 150)), "5.3 / 14.2 / 20.5 / 26.8 / 34.5")
check("male: every other odor -> DNp13 max; GF max (every odor and dose)", f"{bm.drop('cVA')['DNp13 reject'].max():.1f}; {bm['GF jump'].max():.1f}", "0; 0.0")
check("male cVA: KC active % at 25-150 Hz", rng(bm.loc['cVA']['KC active %'].values), "0.1-0.3")

# ================================================================== K. conditioning
section("K. Conditioning (`conditioning_*.csv`, Results 5, Table 1, Fig 2b)")
groups = {}
for path in sorted(glob.glob(os.path.join(RES, "conditioning_*_seed*.csv"))):
    if path.endswith("_compartments.csv"):
        continue
    base = os.path.basename(path).replace("conditioning_", "").replace(".csv", "")
    if "us-" not in base or "-vs-" not in base:
        continue
    groups.setdefault(base.rsplit("_seed", 1)[0], []).append(pd.read_csv(path, index_col=0))
LI = {}
for key, runs in sorted(groups.items()):
    comp = "drive punish-comp" if "punish" in key else "drive reward-comp"
    csp = [float(d.loc[comp, "post_CS+"] / d.loc[comp, "pre_CS+"]) for d in runs]; csm = [float(d.loc[comp, "post_CS-"] / d.loc[comp, "pre_CS-"]) for d in runs]
    li = np.array(csm) - np.array(csp); LI[key] = (li.mean(), li.std(), len(li))
    dapp = [float((d.loc["approach", "post_CS+"] - d.loc["approach", "pre_CS+"])) for d in runs]; dapm = [float((d.loc["approach", "post_CS-"] - d.loc["approach", "pre_CS-"])) for d in runs]
    ddn = [float(abs(d.loc["DNa L", "post_CS+"] - d.loc["DNa L", "pre_CS+"]) + abs(d.loc["DNa R", "post_CS+"] - d.loc["DNa R", "pre_CS+"])) for d in runs]
    emit(f"- `{key}` (n = {len(runs)}): taught-compartment drive retained CS+ {rng(csp, 2)}, CS- {rng(csm, 2)}; **learning index {li.mean():.2f} +/- {li.std():.2f}**; "
         f"approach change (post - pre) CS+ {rng(dapp)}, CS- {rng(dapm)} Hz; |dDNa L| + |dDNa R| for CS+ {rng(ddn)} Hz")


def li(key):
    return f"{LI[key][0]:.2f} +/- {LI[key][1]:.2f} (n = {LI[key][2]})" if key in LI else "missing"


# pool the two odor orders of each design
def pooled(*keys):
    vals = []
    for k in keys:
        if k in groups:
            comp = "drive punish-comp" if "punish" in k else "drive reward-comp"
            vals += [float(d.loc[comp, "post_CS-"] / d.loc[comp, "pre_CS-"]) - float(d.loc[comp, "post_CS+"] / d.loc[comp, "pre_CS+"]) for d in groups[k]]
    return f"{np.mean(vals):.2f} +/- {np.std(vals):.2f} (n = {len(vals)})" if vals else "missing"


P = f"flywire_{PAPER_F}_us-dan-"
check("appetitive, reward DANs 50 Hz, eLN x0.25 (both orders)", pooled(P + "reward_vinegar-vs-ester", P + "reward_ester-vs-vinegar"), "0.54 +/- 0.02 (n = 6)")
check("appetitive, reward DANs 20 Hz", pooled(P + "reward-20hz_vinegar-vs-ester", P + "reward-20hz_ester-vs-vinegar"), "0.56 +/- 0.04 (n = 6)")
check("appetitive, eLN x0.1", pooled("flywire_shiu_min1+known+eln0.1_us-dan-reward_vinegar-vs-ester", "flywire_shiu_min1+known+eln0.1_us-dan-reward_ester-vs-vinegar"), "0.62 +/- 0.02 (n = 6)")
check("aversive, punishment DANs 50 Hz, eLN x0.25", pooled(P + "punish_vinegar-vs-ester", P + "punish_ester-vs-vinegar"), "0.21 +/- 0.15 (n = 6)")
check("aversive, 20 Hz; aversive, eLN x0.1", f"{pooled(P + 'punish-20hz_vinegar-vs-ester', P + 'punish-20hz_ester-vs-vinegar')}; {pooled('flywire_shiu_min1+known+eln0.1_us-dan-punish_vinegar-vs-ester', 'flywire_shiu_min1+known+eln0.1_us-dan-punish_ester-vs-vinegar')}", "0.23 +/- 0.13 (n = 2); 0.26 +/- 0.15 (n = 2)")
check("no US (`--us wiring`)", pooled(f"flywire_{PAPER_F}_us-wiring_vinegar-vs-ester", f"flywire_{PAPER_F}_us-wiring_ester-vs-vinegar"), "0.04 +/- 0.04 (n = 4)")
check("male, reward / punishment DANs (eLN x0.25)", f"{pooled(f'malecns_{PAPER_M}_us-dan-reward_vinegar-vs-ester', f'malecns_{PAPER_M}_us-dan-reward_ester-vs-vinegar')}; {pooled(f'malecns_{PAPER_M}_us-dan-punish_vinegar-vs-ester', f'malecns_{PAPER_M}_us-dan-punish_ester-vs-vinegar')}", "0.80 +/- 0.02 (n = 2); 0.77 +/- 0.04 (n = 2)")
check("CS+ taught-compartment drive retained (appetitive 50 Hz, both orders), range; CS-", f"{rng([float(d.loc['drive reward-comp', 'post_CS+'] / d.loc['drive reward-comp', 'pre_CS+']) for k in (P + 'reward_vinegar-vs-ester', P + 'reward_ester-vs-vinegar') for d in groups[k]], 2)}; {rng([float(d.loc['drive reward-comp', 'post_CS-'] / d.loc['drive reward-comp', 'pre_CS-']) for k in (P + 'reward_vinegar-vs-ester', P + 'reward_ester-vs-vinegar') for d in groups[k]], 2)}", "0.10-0.11; 0.59-0.66")

# ================================================================== L. expression probe
section("L. Expression probe (`expression_probe_*.csv`, Results 5, Fig 11)")
E = csv(f"expression_probe_flywire_{PAPER_F}.csv"); ge = E.groupby(["mbon_set", "mbons", "odor", "tonic_hz"]).mean(numeric_only=True)
check("reward set, no odor: DNa L silenced - intact at tonic 10 / 20 / 40 Hz", " / ".join(f"{ge.loc[('reward', 'silenced', 'none', h), 'DNa L'] - ge.loc[('reward', 'intact', 'none', h), 'DNa L']:+.1f}" for h in (10, 20, 40)), "+5.5 / +5.0 / +4.0")
check("reward set, no odor, intact: DNa L at 10 / 20 / 40 Hz (waking the targets alone drives the turning DNs)", " / ".join(f"{ge.loc[('reward', 'intact', 'none', h), 'DNa L']:.0f}" for h in (10, 20, 40)), "23 / 26.5 / 30")
check("reward set, odor left: approach index (silenced - intact) at 0 / 5 / 10 / 20 / 40 Hz", " / ".join(f"{ge.loc[('reward', 'silenced', 'L', h), 'approach (L-R)'] - ge.loc[('reward', 'intact', 'L', h), 'approach (L-R)']:+.1f}" for h in (0, 5, 10, 20, 40)), "-1.9 / -3.5 / +1.8 / +3.0 / +4.0")
check("largest |silenced - intact| of DNp09 / MDN / feeding MNs over every set, odor and tonic level", " / ".join(f"{max(abs(ge.loc[(s_, 'silenced', o, h), c] - ge.loc[(s_, 'intact', o, h), c]) for s_ in ('reward', 'punish') for o in ('none', 'L', 'both') for h in sorted(E.tonic_hz.unique()) if (s_, 'silenced', o, h) in ge.index):.1f}" for c in ("DNp09", "MDN back", "feed MNs")), "0.0 / 0.0 / 0.0")
if "target DNs Hz" in E.columns:
    td = E[E.mbon_set == "punish"].groupby(["mbons", "odor", "tonic_hz"])["target DNs Hz"].mean()
    check("punishment set: the 28 descending targets, intact vs silenced (odor bilateral) at 0 / 5 / 10 / 20 / 40 Hz", "; ".join(f"{td.loc[('intact', 'both', h)]:.1f} vs {td.loc[('silenced', 'both', h)]:.1f}" for h in (0, 5, 10, 20, 40) if ('intact', 'both', h) in td.index), "7.0 vs 7.1; 11.3 vs 10.8; 15.1 vs 14.8; 23.3 vs 23.0; 38.6 vs 38.8")
    check("punishment set: max |intact - silenced| of the target DNs over odors and levels", f"{max(abs(td.loc[('intact', o, h)] - td.loc[('silenced', o, h)]) for o in ('none', 'L', 'both') for h in sorted(E.tonic_hz.unique()) if ('intact', o, h) in td.index and ('silenced', o, h) in td.index):.2f} Hz", "0.6")
check("punishment set, MDN with the tonic drive at 40 Hz, intact / silenced (the targets' own activity)", f"{ge.loc[('punish', 'intact', 'both', 40), 'MDN back']:.1f} / {ge.loc[('punish', 'silenced', 'both', 40), 'MDN back']:.1f}", "18.6 / 18.6")

# ================================================================== M. learning in the world
section("M. Learning in the world (`logs/learn_world{5,6}_probe_{pre,post}.json`, `*_learn_stats.csv`, Results 5)")
for w, paper in (("world6", "0.289 / 0.662; 0.131 / 0.438; 0.37 / 0.31"), ("world5", "0.271 / 0.286; 0.090 / 0.384; 0.02 / 0.29")):
    pre = json.load(open(os.path.join(LOGS, f"learn_{w}_probe_pre.json")))["probe"]; post = json.load(open(os.path.join(LOGS, f"learn_{w}_probe_post.json")))["probe"]
    r = {cls: {k: post[cls][k] / pre[cls][k] for k in ("drive_reward_comp", "drive_punish_comp") if pre[cls].get(k)} for cls in post}
    li_r = r["vinegar"]["drive_reward_comp"] - r["ester"]["drive_reward_comp"]; li_p = r["ester"]["drive_punish_comp"] - r["vinegar"]["drive_punish_comp"]
    check(f"{w}: retained drive post / pre, reward-comp ester / vinegar; punish-comp vinegar / ester; LI appetitive (vin - est) / aversive (est - vin)", f"{r['ester']['drive_reward_comp']:.3f} / {r['vinegar']['drive_reward_comp']:.3f}; {r['vinegar']['drive_punish_comp']:.3f} / {r['ester']['drive_punish_comp']:.3f}; {li_r:.2f} / {li_p:.2f}", paper)
for f in sorted(glob.glob(os.path.join(LOGS, "fly1_mb-*_learn_stats.csv"))):
    tr = str(pd.read_csv(f.replace("_learn_stats.csv", ".csv"), usecols=["trial"], nrows=3).trial.iloc[0])
    if tr not in ("world5", "world6"):
        continue
    s_ = pd.read_csv(f).set_index("phase")
    check(f"{tr}: walk / turn while smelling poppies (A) and dandelions (B): pre; train; post", "; ".join(f"{ph} walk {s_.loc[ph, 'walk_A']:.2f} / {s_.loc[ph, 'walk_B']:.2f}, turn {s_.loc[ph, 'turn_A']:+.2f} / {s_.loc[ph, 'turn_B']:+.2f}" for ph in ("pre", "train", "post") if ph in s_.index) + f"; sugar ticks {int(s_.loc['train', 'us_reward_ticks'])} ({s_.loc['train', 'us_reward_ticks']*0.05:.0f} s), bitter ticks {int(s_.loc['train', 'us_punish_ticks'])}", None)

# ================================================================== N. encounters (Table 2)
section("N. Encounter trials (`encounter_trials.csv` and the arena logs; Results 6, Table 2, Fig 3, 3b)")
T = csv("encounter_trials.csv")
fem = T[T.dataset == "flywire"]; male = T[T.dataset == "malecns"]
order = [("published", "odor-free", "ff"), ("published", "odor-free", "mf"), ("specific", "faint-smell", "ff"), ("specific", "faint-smell", "mf"), ("specific", "clean", "ff"), ("specific", "clean", "mf"), ("specific", "noise0.2", "ff"), ("specific", "noise0.2", "mf"), ("specific", "noise0.2-virgin", "mf")]
emit("| lobe / chamber | cond | trials | female logs | brain s | trials with contact | logs with contact | contact % of ticks | longest bout s | first contact s | walk duty | path blocks | median dist | DNa L / R far -> contact | DNp13 far -> near -> contact | feed MNs far -> contact | GF far | MDN female contact | reject / feed / attack acts per min | jump events per min | male: MDN contact / near / far | male walk | male path | male P1 far / near / contact | male pIP10 (sing) far / contact | male sing acts per min |")
emit("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for v, ch, c in order:
    s_ = fem[(fem.variant == v) & (fem.chamber == ch) & (fem.condition == c)]
    if not len(s_):
        continue
    m_ = male[(male.variant == v) & (male.chamber == ch) & (male.condition == c)]
    cpct = s_.contact_ticks / s_.ticks * 100
    row = [f"{v} / {ch}", c, f"{s_.trial.nunique()}", f"{len(s_)}", f"{s_.brain_s.mean():.0f} +/- {s_.brain_s.std():.0f}", f"{s_[s_.contact_ticks > 0].trial.nunique()} / {s_.trial.nunique()}", f"{int((s_.contact_ticks > 0).sum())} / {len(s_)}",
           f"{cpct.mean():.1f} +/- {cpct.std():.1f}", f"{s_.longest_bout_s.max():.1f}", f"{s_.first_contact_s.min():.1f}" if s_.first_contact_s.notna().any() else "-", f"{s_.walk.mean():.2f}", f"{s_.path_blocks.mean():.0f}", f"{s_.median_dist.mean():.1f}",
           f"{s_.turn_L_far.mean():.1f} / {s_.turn_R_far.mean():.1f} -> {s_.turn_L_contact.mean():.1f} / {s_.turn_R_contact.mean():.1f}" if s_.turn_L_contact.notna().any() else f"{s_.turn_L_far.mean():.1f} / {s_.turn_R_far.mean():.1f} -> -",
           f"{s_.reject_far.mean():.1f} -> {s_.reject_near.mean():.1f} -> {s_.reject_contact.mean():.1f}" if s_.reject_contact.notna().any() else f"{s_.reject_far.mean():.1f} -> {s_.reject_near.mean():.1f} -> -",
           f"{s_.feed_far.mean():.1f} -> {s_.feed_contact.mean():.1f}" if s_.feed_contact.notna().any() else f"{s_.feed_far.mean():.1f} -> -", f"{s_.jump_far.mean():.1f}", f"{s_.back_contact.mean():.1f}" if s_.back_contact.notna().any() else "-",
           f"{s_.reject_events_per_min.mean():.0f} / {s_.feed_events_per_min.mean():.0f} / {s_.attack_events_per_min.mean():.1f}", f"{s_.jump_events_per_min.mean():.0f}"]
    if len(m_):
        row += [f"{m_.back_contact.mean():.1f} / {m_.back_near.mean():.1f} / {m_.back_far.mean():.1f}" if m_.back_contact.notna().any() else f"- / {m_.back_near.mean():.1f} / {m_.back_far.mean():.1f}", f"{m_.walk.mean():.2f}", f"{m_.path_blocks.mean():.0f}",
                f"{m_.court_p1_far.mean():.2f} / {m_.court_p1_near.mean():.2f} / {m_.court_p1_contact.mean():.2f}" if m_.court_p1_contact.notna().any() else f"{m_.court_p1_far.mean():.2f} / {m_.court_p1_near.mean():.2f} / -",
                f"{m_.sing_far.mean():.2f} / {m_.sing_contact.mean():.2f}" if m_.sing_contact.notna().any() else f"{m_.sing_far.mean():.2f} / -", f"{m_.sing_events_per_min.mean():.1f}"]
    else:
        row += ["-"] * 6
    emit("| " + " | ".join(row) + " |")
emit()
emit("Table 2 of the paper (draft 1) reads: published ff 0/5, 0, 0.71, 36/4; published mf 4/5, 3.6, 0.71, 37/4 -> 21/0.1, 0 -> 16.5, MDN 0 walk 0.24; faint ff 4/5, 40 +/- 32, 0.30, 13.7/13.5 -> 0.4/0.1, 5.0 -> 32.9; faint mf 1/5, 1.2, 0.47, 12.4/12.4 -> 2.7/1.2, 5.7 -> 33.0, MDN 39.5 / 6 near, walk 0.03; clean ff 0/5, 0, 0.00; clean mf 2/5, 0.5, 0.48, 12.7/12.6 -> 0.0/0.3, 5.1 -> 31.6, MDN 48 / 15 / 4, walk 0.03; noise ff 3/5, 11 +/- 14, 0.51, 15.5/16.3 -> 1.2/1.2, 5.3 -> 30.9; noise mf 4/5, 1.3, 0.55, 15.2/16.1 -> 2.0/1.8, 5.1 -> 30.6, MDN 29 / 13 / 6, walk 0.27, P1 0.2")
emit()
# what the flies smelled, per chamber
emit("Odor in the chamber (max of any odor_* column over the trial, per chamber; 0 = no odorous block ever within 16 blocks): " + "; ".join(f"{v}/{ch} {g.odor_max.max():.2f}" for (v, ch), g in T.groupby(["variant", "chamber"])))
# the substrate's act floors (noise ff, far from the other fly)
nf_ = fem[(fem.chamber == "noise0.2") & (fem.condition == "ff")]
check("substrate act floors, female logs on the substrate: rejection / proboscis / attack events per min; DNp13 far; feed MNs far; GF far; jump events per min", f"{nf_.reject_events_per_min.mean():.0f} / {nf_.feed_events_per_min.mean():.0f} / {nf_.attack_events_per_min.mean():.1f}; {nf_.reject_far.mean():.1f}; {nf_.feed_far.mean():.1f}; {nf_.jump_far.mean():.1f}; {nf_.jump_events_per_min.mean():.0f}", "44 / 32 / 2.0; 5.3; 8.1; 1.6; 143")
ff_n = fem[(fem.chamber == "noise0.2") & (fem.condition == "ff")]
check("substrate ff: jump ticks as % of ticks", f"{(ff_n.jump_events_per_min * ff_n.brain_s / 60 / ff_n.ticks * 100).mean():.1f} %", "12 %")
mn_ = male[male.chamber == "noise0.2"]
check("substrate male: leg-MN walk duty, path, MDN far, P1 far / near / contact, pIP10 far / near / contact, wing MNs? (sing = pIP10 readout)", f"walk {mn_.walk.mean():.2f}, path {mn_.path_blocks.mean():.0f}, MDN far {mn_.back_far.mean():.1f} near {mn_.back_near.mean():.1f} contact {mn_.back_contact.mean():.1f}; P1 {mn_.court_p1_far.mean():.2f} / {mn_.court_p1_near.mean():.2f} / {mn_.court_p1_contact.mean():.2f}; pIP10 {mn_.sing_far.mean():.2f} / {mn_.sing_near.mean():.2f} / {mn_.sing_contact.mean():.2f}", "0.27, 127, 6.2 / 12.9 / 28.9; P1 0.20 / 0.21 / 0.20; pIP10 0.24 / 0.22 / 0.34")
cm_ = male[male.chamber == "clean"]
check("clean mf male: walk duty (untouched trials), path range, MDN contact / near / far; trial 3 path", f"{cm_[cm_.contact_ticks == 0].walk.mean():.2f}, {cm_[cm_.contact_ticks == 0].path_blocks.min():.0f}-{cm_[cm_.contact_ticks == 0].path_blocks.max():.0f}, {cm_.back_contact.mean():.0f} / {cm_.back_near.mean():.0f} / {cm_.back_far.mean():.0f}; {cm_[cm_.trial == 'off_mf_t3_clean'].path_blocks.iloc[0]:.0f} at duty {cm_[cm_.trial == 'off_mf_t3_clean'].walk.iloc[0]:.2f}", "0.03, 26-31, 48 / 15 / 4; 158 at 0.29")
cf_ = fem[(fem.chamber == "clean") & (fem.condition == "mf")]
check("clean mf female: walk, path, DNa far, DNp13 far, GF far; contact: DNp13, feed MNs, DNa, walk", f"{cf_.walk.mean():.2f}, {cf_.path_blocks.mean():.0f}, {cf_.turn_L_far.mean():.1f} / {cf_.turn_R_far.mean():.1f}, {cf_.reject_far.mean():.1f}, {cf_.jump_far.mean():.1f}; {cf_.reject_contact.mean():.1f}, {cf_.feed_contact.mean():.1f}, {cf_.turn_L_contact.mean():.1f} / {cf_.turn_R_contact.mean():.1f}", "0.48, 42, 12.7 / 12.6, 5.1, 1.9; 31.6, 22.1, 0.0 / 0.3")
cff = fem[(fem.chamber == "clean") & (fem.condition == "ff")]
check("clean ff females: max of any readout over the 10 logs (walk, path, DNa, DNp13, feed, GF); median distance", f"{cff.walk.max():.2f}, {cff.path_blocks.max():.1f}, {cff.turn_L_all.max():.2f} / {cff.turn_R_all.max():.2f}, {cff.reject_all.max():.2f}, {cff.feed_all.max():.2f}, {cff.jump_all.max():.2f}; {cff.median_dist.mean():.1f} blocks; brain time {cff.brain_s.mean():.0f} +/- {cff.brain_s.std():.0f} s", "0.00, 0.0, 0.00 / 0.00, 0.00, 0.00, 0.00; 4.3; 135 +/- 6")
# the approach question, from the raw logs: turning DNs before the first contact, by distance bin, pooled over female logs
emit(); emit("**Approach: the female's turning DNs and turn command before a log's first contact, by distance to the other fly (pooled ticks over the female logs of each chamber), and after a touch ends (time since the last contact)**"); emit()
emit("| chamber / cond | flies | ticks 1.3-2 blocks: DNa L / R (n) | 2-3.5 (n) | 3.5-6 (n) | > 6 far (n) | turn command, all pre-contact ticks by bin | post-touch DNa L / R at 0-0.1 s / 0.1-0.25 / 0.25-2 / > 2 s (n) |")
emit("|---|---|---|---|---|---|---|---|")
BINS = [(1.3, 2.0), (2.0, 3.5), (3.5, 6.0), (6.0, 1e9)]
for v, ch, c in [("specific", "clean", "mf"), ("specific", "noise0.2", "ff"), ("specific", "noise0.2", "mf"), ("specific", "noise0.2-virgin", "mf"), ("specific", "faint-smell", "ff"), ("specific", "faint-smell", "mf")]:
    s_ = fem[(fem.variant == v) & (fem.chamber == ch) & (fem.condition == c)]
    pre_L, pre_R, pre_n, pre_t = [[] for _ in BINS], [[] for _ in BINS], [0] * len(BINS), [[] for _ in BINS]
    post = {k: [[], []] for k in ("0-0.1", "0.1-0.25", "0.25-2", ">2")}
    for _, r in s_.iterrows():
        fs = glob.glob(os.path.join(LOGS, f"{r.fly}_off-*_{r.stamp}.csv"))
        if not fs:
            continue
        d = pd.read_csv(fs[0])
        contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
        first = int(np.argmax(contact.to_numpy())) if contact.any() else len(d)
        pre = d.iloc[:first]
        for i, (lo, hi) in enumerate(BINS):
            mk = (pre.near_dist >= lo) & (pre.near_dist < hi)
            pre_L[i] += list(pre.loc[mk, "hz_turn_L"]); pre_R[i] += list(pre.loc[mk, "hz_turn_R"]); pre_n[i] += int(mk.sum()); pre_t[i] += list(pre.loc[mk, "ctl_turn"])
        if contact.any():
            t = d.brain_t_ms.to_numpy() / 1000; last_end = np.nan; since = np.full(len(d), np.nan)
            for i in range(1, len(d)):
                if contact.iloc[i - 1] and not contact.iloc[i]:
                    last_end = t[i]
                if not contact.iloc[i] and np.isfinite(last_end):
                    since[i] = t[i] - last_end
            for k, (lo, hi) in (("0-0.1", (0, 0.1)), ("0.1-0.25", (0.1, 0.25)), ("0.25-2", (0.25, 2)), (">2", (2, 1e9))):
                mk = (since > lo) & (since <= hi)
                post[k][0] += list(d.loc[mk, "hz_turn_L"]); post[k][1] += list(d.loc[mk, "hz_turn_R"])
    cells = [f"{np.mean(pre_L[i]):.1f} / {np.mean(pre_R[i]):.1f} ({pre_n[i]})" if pre_n[i] else "- (0)" for i in range(len(BINS))]
    turn = " / ".join(f"{np.mean(pre_t[i]):+.2f}" if pre_n[i] else "-" for i in range(len(BINS)))
    pst = " / ".join(f"{np.mean(post[k][0]):.1f}/{np.mean(post[k][1]):.1f} ({len(post[k][0])})" if post[k][0] else "-" for k in ("0-0.1", "0.1-0.25", "0.25-2", ">2"))
    emit(f"| {v} / {ch} | {c} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {turn} | {pst} |")
emit()
emit("Paper (19b): substrate ff 10.8 / 13.5 at 1.3-2 (26 ticks), 11.5 / 16.2 at 2-3.5 (60), 15.2 / 15.3 at 3.5-6, 15.8 / 16.5 far; clean mf 7.8 / 8.9 (9), 9.5 / 8.5 (20), 10.5 / 11.2, 12.8 / 13.1 far; post-touch 5.9 / 5.6, 10 / 17, 11-15 / 13-15, 16 / 16; turn command 0.00 at every distance")

# ================================================================== O. pre-contact dose row (item 6)
PD = csv(f"precontact_dose_flywire_{PAPER_F}.csv")
if PD is not None:
    section("O. Pre-contact slowing as a dose row (`precontact_dose_flywire_*.csv`, machine-time item 6)")
    g = PD.groupby(["noise_hz", "condition"], sort=False).mean(numeric_only=True); sd = PD.groupby(["noise_hz", "condition"], sort=False).std(numeric_only=True)
    emit(f"({PD.seed.nunique()} seeds; {PD.settle_ms.iloc[0]/1000:g} s settle, {PD.ms.iloc[0]/1000:g} s read; bilateral drive at level x 150 Hz)"); emit()
    emit("| substrate | condition | DNa L / R (Hz) | DNp09 | walk duty (body readout) | turn | GF | DNp13 | MDN | PPL1 | active % |"); emit("|---|---|---|---|---|---|---|---|---|---|---|")
    for (nz, cond), r in g.iterrows():
        emit(f"| {nz:g} | {cond} | {r['DNa L']:.1f} +/- {sd.loc[(nz, cond), 'DNa L']:.1f} / {r['DNa R']:.1f} +/- {sd.loc[(nz, cond), 'DNa R']:.1f} | {r['DNp09']:.1f} | {r['walk duty']:.2f} | {r['turn']:+.2f} | {r['GF jump']:.1f} | {r['DNp13 reject']:.1f} | {r['MDN back']:.1f} | {r['PPL1 (punish DA)']:.1f} | {r['active_frac']*100:.0f} |")
    emit()
    for nz in sorted(PD.noise_hz.unique()):
        gg = g.loc[nz]
        far_mf = gg[gg.index.str.startswith("mf far")]; near_mf = gg[gg.index.str.startswith("mf near")]
        far_ff = gg[gg.index.str.startswith("ff far")]; near_ff = gg[gg.index.str.startswith("ff near")]
        dna = lambda x: (x["DNa L"] + x["DNa R"]).mean() / 2
        emit(f"- substrate {nz:g} Hz: mf far -> near, mean DNa {dna(far_mf):.1f} -> {dna(near_mf):.1f} ({(dna(near_mf)/dna(far_mf)-1)*100:+.0f} %), walk duty {far_mf['walk duty'].mean():.2f} -> {near_mf['walk duty'].mean():.2f}; "
             f"ff far -> near, DNa {dna(far_ff):.1f} -> {dna(near_ff):.1f} ({(dna(near_ff)/dna(far_ff)-1)*100 if dna(far_ff) > 0 else float('nan'):+.0f} %), walk {far_ff['walk duty'].mean():.2f} -> {near_ff['walk duty'].mean():.2f}; "
             f"cVA alone 0.06 / 0.14 / 0.3 / 0.5 / 0.7: DNa {' / '.join(f'{dna(gg.loc[[c]]):.1f}' for c in gg.index if c.startswith('cVA alone'))}; Or47b alone 0.1 / 0.4 / 0.9: {' / '.join(f'{dna(gg.loc[[c]]):.1f}' for c in gg.index if c.startswith('Or47b alone'))}; CO2 alone: {' / '.join(f'{dna(gg.loc[[c]]):.1f}' for c in gg.index if c.startswith('CO2 alone'))}")
else:
    section("O. Pre-contact dose row: `precontact_dose_flywire_*.csv` not found (run experiments/precontact_dose.py)")

# ================================================================== P. the cells the first pass flagged, looked at directly
section("P. Cells looked at directly (male touch -> MDN by drive; male P1 / pIP10 / MN9 by input, gain and condition; jumps; a turn-toward index)")
piv = CM.pivot_table(index="condition", columns="drive", values="MDN back +touch").round(1)
emit("male head bristles -> MDN with touch, by condition (rows) and walking drive (columns):"); emit(); emit("| condition | " + " | ".join(piv.columns) + " |"); emit("|---|" + "---|" * len(piv.columns))
for c_, r in piv.iterrows():
    emit(f"| {c_} | " + " | ".join("-" if not np.isfinite(v) else f"{v:.1f}" for v in r.values) + " |")
emit()
lp = CM.pivot_table(index="condition", columns="drive", values=["leg MNs alone", "leg MNs +touch"]).round(1)
PMN = "paper's model: eLN x0.25 + noise 0.2 Hz"
check("male leg MNs alone -> + touch on the substrate alone (paper's model + noise)", f"{lp.loc[PMN, ('leg MNs alone', 'none')]:.1f} -> {lp.loc[PMN, ('leg MNs +touch', 'none')]:.1f}", "0.4 -> 1.5")
gm_ = GM_.groupby(["gain", "input"])[["P1/pC1 male", "aIPg aggr", "MN9", "pIP10 song cmd"]].mean()
sub = gm_[(gm_.index.get_level_values(0) <= 1.4) & ((gm_["P1/pC1 male"] > 0.1) | (gm_["MN9"] > 0.5) | (gm_["aIPg aggr"] > 0.1))]
emit("male gain sweep, every (gain <= 1.4, input) cell with P1 or aIPg > 0.1 Hz or MN9 > 0.5 Hz:"); emit()
for (g_, i_), r in sub.iterrows():
    emit(f"- gain {g_:g}, {i_}: P1 {r['P1/pC1 male']:.2f}, aIPg {r['aIPg aggr']:.2f}, MN9 {r['MN9']:.2f}, pIP10 {r['pIP10 song cmd']:.2f}")
check("male labellar GRNs -> MN9, per gain 0.5 / 0.7 / 1.0 / 1.4", " / ".join(f"{gm_.loc[(g_, 'sugar GRNs'), 'MN9']:.2f}" for g_ in (0.5, 0.7, 1.0, 1.4)), "0.00 / 0.00 / 0.00 / 0.83")
pm_ = PM.groupby("input").mean(numeric_only=True); pm_ = pm_[(pm_["P1/pC1 male"] > 0.1) | (pm_["pIP10 song cmd"] > 0.5)]
emit("male innate map, inputs with P1 > 0.1 or pIP10 > 0.5 Hz: " + "; ".join(f"{i_}: P1 {r['P1/pC1 male']:.2f}, pIP10 {r['pIP10 song cmd']:.2f}" for i_, r in pm_.iterrows()))
check("male sensitivity, excluding the first-version numerics: P1 max; pIP10 range; labellar -> MN9 max; touch -> MDN under the published lobe (x1)", f"{SMn['cVA (Or67d/DA1) -> P1/pC1 male'].max():.1f}; {rng(SMn['cVA (Or67d/DA1) -> pIP10 song cmd'].values)}; {SMn['sugar GRNs -> MN9'].max():.1f}; {Sm.loc['published model: eLN x1', 'touch (all head bristles) -> MDN back']:.1f}", "0.6; 1.1-6.9; 0.0; 11.5")
emit(); emit("jumps and turning toward the other fly, from the arena logs (female logs; pre-contact = before the log's first contact; toward index = mean of turn command x sign(azimuth to the other fly), + = toward, over pre-contact ticks within 6 blocks; both signs follow observe.js / motor.py, + = left):"); emit()
emit("| chamber / cond | jump ticks (% of all ticks) | pre-contact ticks < 6 blocks | toward index | mean turn command | fraction of ticks with |turn| > 0.05 | mean |azimuth| (rad) |"); emit("|---|---|---|---|---|---|---|")
for v, ch, c in order:
    s_ = fem[(fem.variant == v) & (fem.chamber == ch) & (fem.condition == c)]
    jumps, tot, tw, tr_, big, azs = 0, 0, [], [], 0, []
    for _, r in s_.iterrows():
        fs = glob.glob(os.path.join(LOGS, f"{r.fly}_off-*_{r.stamp}.csv"))
        if not fs:
            continue
        d = pd.read_csv(fs[0]); jumps += int(d.ctl_jump.astype(bool).sum()); tot += len(d)
        contact = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
        first = int(np.argmax(contact.to_numpy())) if contact.any() else len(d)
        pre = d.iloc[:first]; pre = pre[(pre.near_dist < 6) & pre.near_az.notna()]
        tw += list(pre.ctl_turn * np.sign(pre.near_az)); tr_ += list(pre.ctl_turn); big += int((pre.ctl_turn.abs() > 0.05).sum()); azs += list(pre.near_az.abs())
    if tot:
        emit(f"| {v} / {ch} | {c} | {jumps / tot * 100:.1f} | {len(tw)} | {np.mean(tw) if tw else float('nan'):+.3f} | {np.mean(tr_) if tr_ else float('nan'):+.3f} | {big / max(len(tw), 1):.2f} | {np.mean(azs) if azs else float('nan'):.2f} |")

# ================================================================== Q. 24 Sep additions (RESEARCH_NOTES 21)
section("Q. The virgin female on the substrate; the Or47b x CO2 window; the far levels at 10 seeds (RESEARCH_NOTES 21)")
vf = fem[(fem.variant == "specific") & (fem.chamber == "noise0.2-virgin") & (fem.condition == "mf")]
nf0 = fem[(fem.variant == "specific") & (fem.chamber == "noise0.2") & (fem.condition == "mf")]
vm = male[(male.variant == "specific") & (male.chamber == "noise0.2-virgin")]; nm0 = male[(male.variant == "specific") & (male.chamber == "noise0.2")]
if len(vf):
    emit("| female with a male, clean + 0.2 Hz substrate | logs | brain s | trials with contact | contact % | walk | DNa L / R far -> contact | DNp13 far -> contact | "
         "DNp37 accept far / near / contact | accept events / min | oviDN far / contact | pC1d/e + aIPg far / contact | SAG | male MDN far / contact |")
    emit("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tag, s_, m_ in (("no state (19b)", nf0, nm0), ("virgin: SAG tonic 30 Hz (21)", vf, vm)):
        g = lambda k: s_[k].mean() if k in s_ else float("nan")
        emit(f"| {tag} | {len(s_)} | {s_.brain_s.mean():.0f} | {s_[s_.contact_ticks > 0].trial.nunique()} / {s_.trial.nunique()} | {(s_.contact_ticks / s_.ticks).mean()*100:.1f} | "
             f"{s_.walk.mean():.2f} | {g('turn_L_far'):.1f} / {g('turn_R_far'):.1f} -> {g('turn_L_contact'):.1f} / {g('turn_R_contact'):.1f} | {g('reject_far'):.1f} -> {g('reject_contact'):.1f} | "
             f"{g('accept_far'):.2f} / {g('accept_near'):.2f} / {g('accept_contact'):.2f} | {g('accept_events_per_min'):.2f} | {g('egg_far'):.2f} / {g('egg_contact'):.2f} | "
             f"{g('aggression_far'):.2f} / {g('aggression_contact'):.2f} | {g('sag_all'):.1f} | {m_.back_far.mean():.1f} / {m_.back_contact.mean():.1f} |")
    # the numbers PAPER.md carries for the virgin series (Results 6, Table 1, Supplementary file 1, Figure 6-S3)
    cpv = vf.contact_ticks / vf.ticks * 100
    check("virgin: trials with contact; contact % of ticks (mean +/- sd); no state: trials; contact %", f"{vf[vf.contact_ticks > 0].trial.nunique()} / {vf.trial.nunique()}; {cpv.mean():.1f} +/- {cpv.std():.1f}; "
          f"{nf0[nf0.contact_ticks > 0].trial.nunique()} / {nf0.trial.nunique()}; {(nf0.contact_ticks / nf0.ticks).mean()*100:.1f}", "5 / 5; 3.6 +/- 3.2; 4 / 5; 1.3")
    check("virgin: DNp37 (accept) far / near / contact; accept events / min, virgin vs no state", f"{vf.accept_far.mean():.1f} / {vf.accept_near.mean():.1f} / {vf.accept_contact.mean():.1f}; "
          f"{vf.accept_events_per_min.mean():.0f} vs {nf0.accept_events_per_min.mean():.0f}", "15.8 / 16.7 / 15.9; 99 vs 1")
    check("virgin: pC1d/e + aIPg on contact, virgin vs no state; DNp13 far -> contact; walk; longest bout (s)", f"{vf.aggression_contact.mean():.1f} vs {nf0.aggression_contact.mean():.1f}; "
          f"{vf.reject_far.mean():.1f} -> {vf.reject_contact.mean():.1f}; {vf.walk.mean():.2f}; {vf.longest_bout_s.max():.1f}", "1.0 vs 0.2; 4.1 -> 31.7; 0.52; 1.7")
    check("virgin: DNa L / R far -> contact; the male's MDN contact / near / far; his walk", f"{vf.turn_L_far.mean():.1f} / {vf.turn_R_far.mean():.1f} -> {vf.turn_L_contact.mean():.1f} / "
          f"{vf.turn_R_contact.mean():.1f}; {vm.back_contact.mean():.0f} / {vm.back_near.mean():.0f} / {vm.back_far.mean():.0f}; {vm.walk.mean():.2f}", "13.9 / 15.9 -> 0.3 / 1.4; 30 / 18 / 8; 0.28")
    tw_all, tw_bin, per_log = [], [], []
    for _, r in vf.iterrows():
        d = pd.read_csv(glob.glob(os.path.join(LOGS, f"{r.fly}_off-*_{r.stamp}.csv"))[0])
        k = (d.get("obs_taste_fly_female", 0).astype(float) + d.get("obs_taste_fly_male", 0).astype(float)) > 0
        pre = d.iloc[:int(np.argmax(k.to_numpy())) if k.any() else len(d)]; pre = pre[pre.near_az.notna()]
        w6 = pre[pre.near_dist < 6]; tw_all += list(w6.ctl_turn * np.sign(w6.near_az))
        b = pre[(pre.near_dist >= 1.3) & (pre.near_dist < 2.0)]
        if len(b):
            tw_bin += list(b.ctl_turn * np.sign(b.near_az)); per_log.append((b.ctl_turn.to_numpy(), np.sign(b.near_az).to_numpy()))
    obs = float(np.mean(tw_bin)); rng_ = np.random.default_rng(0)
    null = [np.mean(np.concatenate([t_ * s_ * rng_.choice([-1, 1]) for t_, s_ in per_log])) for _ in range(20000)]
    same_sign = sum(1 for t_, _ in per_log if t_.mean() < 0)
    check("virgin: turn-toward index, all pre-contact ticks < 6 blocks; at 1.3-2 blocks; logs whose mean turn there is negative; per-log sign-flip p",
          f"{np.mean(tw_all):+.3f}; {obs:+.2f}; {same_sign} / {len(per_log)}; {np.mean(np.abs(null) >= abs(obs)):.2f}", "-0.005; +0.16; 5 / 5; 0.12")
    emit()
PW = csv(f"precontact_dose_flywire_{PAPER_F}_window.csv")
if PW is not None:
    emit(f"Or47b x CO2 window, no substrate ({PW.seed.nunique()} seeds, {PW.settle_ms.iloc[0]/1000:g} s settle + {PW.ms.iloc[0]/1000:g} s read): DNa L / R mean +/- sd, GF, walk duty, seeds with mean DNa > 2 Hz")
    for cond, d in PW.groupby("condition", sort=False):
        emit(f"- {cond}: DNa {d['DNa L'].mean():.1f} +/- {d['DNa L'].std():.1f} / {d['DNa R'].mean():.1f} +/- {d['DNa R'].std():.1f}; GF {d['GF jump'].mean():.1f}; walk {d['walk duty'].mean():.2f}; "
             f"driven seeds {int(((d['DNa L'] + d['DNa R']) / 2 > 2).sum())}/{len(d)}")
    emit()
PF = csv(f"precontact_dose_flywire_{PAPER_F}_far.csv")
if PF is not None and PD is not None:
    emit(f"far levels on the 0.2 Hz substrate at {PF.seed.nunique()} seeds (seeds 0-2 are the dose row's own and must reproduce it):")
    for cond, d in PF.groupby("condition", sort=False):
        o = PD[(PD.noise_hz == 0.2) & (PD.condition == cond)].sort_values("seed"); d3 = d[d.seed < 3].sort_values("seed")
        same3 = len(o) == len(d3) and np.allclose(o[["DNa L", "DNa R"]].values, d3[["DNa L", "DNa R"]].values)
        emit(f"- {cond}: DNa {d['DNa L'].mean():.1f} +/- {d['DNa L'].std():.1f} / {d['DNa R'].mean():.1f} +/- {d['DNa R'].std():.1f} (sem {d['DNa L'].sem():.1f} / {d['DNa R'].sem():.1f}); "
             f"the 3-seed row {o['DNa L'].mean():.1f} / {o['DNa R'].mean():.1f} ({'reproduced to the digit' if same3 else 'NOT reproduced'}); walk {d['walk duty'].mean():.2f}; turn {d['turn'].mean():+.2f}")

PN = csv(f"precontact_dose_flywire_{PAPER_F}_near.csv")
if PN is not None and PF is not None:
    emit(); emit(f"near levels on the 0.2 Hz substrate at {PN.seed.nunique()} seeds; far vs near at the same seed count (mean DNa of both sides, +/- sem over seeds):")
    both = pd.concat([PF, PN]); both["dna"] = (both["DNa L"] + both["DNa R"]) / 2
    for cond, d in PN.groupby("condition", sort=False):
        emit(f"- {cond}: DNa {d['DNa L'].mean():.1f} +/- {d['DNa L'].std():.1f} / {d['DNa R'].mean():.1f} +/- {d['DNa R'].std():.1f}; walk {d['walk duty'].mean():.2f}; turn {d['turn'].mean():+.2f}")
    def grp(prefix):
        g_ = both[both.condition.str.startswith(prefix)]; per_seed = g_.groupby("seed").dna.mean()
        return per_seed.mean(), per_seed.sem()
    nothing = both[both.condition == "nothing"].dna
    (mff, sff), (mnf, snf), (fff, sfff), (fnf, sfnf) = grp("mf far"), grp("mf near"), grp("ff far"), grp("ff near")
    emit(f"- substrate alone: {nothing.mean():.1f} +/- {nothing.sem():.1f}; mf far {mff:.1f} +/- {sff:.1f} -> mf near {mnf:.1f} +/- {snf:.1f} ({(mnf / mff - 1) * 100:+.0f} %); "
         f"ff far {fff:.1f} +/- {sfff:.1f} -> ff near {fnf:.1f} +/- {sfnf:.1f} ({(fnf / fff - 1) * 100:+.0f} %; {(fnf / nothing.mean() - 1) * 100:+.0f} % against the substrate alone); "
         f"CO2 alone 0.02: {both[both.condition == 'CO2 alone 0.02'].dna.mean():.1f}")

    # the numbers PAPER.md carries for the 10-seed substrate cells and the window (Figure 6-S3 legend, Methods)
    fm = PF[PF.condition != "nothing"].groupby("condition")[["DNa L", "DNa R"]]; nm = PN[PN.condition.str.contains(" near: ")].groupby("condition")[["DNa L", "DNa R"]]
    nothing10 = PF[PF.condition == "nothing"][["DNa L", "DNa R"]].mean()
    check("substrate, 10 seeds: far-level DNa means (min-max); far seed sd (min-max); the substrate alone L / R", f"{fm.mean().min().min():.1f}-{fm.mean().max().max():.1f}; "
          f"{fm.std().min().min():.1f}-{fm.std().max().max():.1f}; {nothing10['DNa L']:.1f} / {nothing10['DNa R']:.1f}", "11-18; 5-9; 15.0 / 15.7")
    check("substrate, 10 seeds: near-level DNa L (min-max) / R (min-max); near seed sd (min-max); R - L (min-max); turn (max / min)",
          f"{nm.mean()['DNa L'].min():.1f}-{nm.mean()['DNa L'].max():.1f} / {nm.mean()['DNa R'].min():.1f}-{nm.mean()['DNa R'].max():.1f}; {nm.std().min().min():.1f}-{nm.std().max().max():.1f}; "
          f"{(nm.mean()['DNa R'] - nm.mean()['DNa L']).min():.1f}-{(nm.mean()['DNa R'] - nm.mean()['DNa L']).max():.1f}; "
          f"{PN[PN.condition.str.contains(' near: ')].groupby('condition').turn.mean().max():+.2f} / {PN[PN.condition.str.contains(' near: ')].groupby('condition').turn.mean().min():+.2f}",
          "8-14 / 13-18; 1-4; 4-6; -0.11 / -0.14")
    pdiff = lambda a_, b_: (grp(b_) - grp(a_))
    def grp(prefix):
        return both[both.condition.str.startswith(prefix)].groupby("seed").dna.mean()
    dm, df_ = grp("mf near") - grp("mf far"), grp("ff near") - grp("ff far")
    co2_ = both[both.condition == "CO2 alone 0.02"][["DNa L", "DNa R"]].mean()
    check("substrate, 10 seeds: paired near - far, male's odor; the other female's (mean +/- sem); CO2 alone 0.02 L / R", f"{dm.mean():+.1f} +/- {dm.sem():.1f}; {df_.mean():+.1f} +/- {df_.sem():.1f}; "
          f"{co2_['DNa L']:.1f} / {co2_['DNa R']:.1f}", "-0.7 +/- 1.9; +2.7 +/- 2.4; 18.4 / 18.8")
    rep_n, rep_diff = 0, 0
    for X in (PF, PN):
        for cond, d in X.groupby("condition"):
            o = PD[(PD.noise_hz == 0.2) & (PD.condition == cond)].set_index("seed")[["DNa L", "DNa R"]]
            for sd_ in range(3):
                if sd_ in o.index:
                    rep_n += 1; rep_diff += int(not np.allclose(o.loc[sd_].values, d[d.seed == sd_][["DNa L", "DNa R"]].values[0]))
    check("seed-cells of the 3-seed dose row against the 10-seed far / near files: differing / total (1 / 39 on 24 Sep, when the 10-seed files were made with 10 threads; 0 / 39 since the 25 Sep re-run made both with 6)", f"{rep_diff} / {rep_n}", "0 / 39")
if PW is not None:
    w6 = PW[PW.condition == "Or47b 0.60 + CO2 0.02"][["DNa L", "DNa R"]].mean()
    alone = PW[PW.condition.str.startswith("Or47b alone")].groupby("condition")[["DNa L", "DNa R"]].mean()
    check("window: Or47b 0.60 + CO2 0.02 DNa L / R; Or47b-alone steps with DNa 0 / all steps", f"{w6['DNa L']:.1f} / {w6['DNa R']:.1f}; {int((alone.max(axis=1) == 0).sum())} / {len(alone)}", "7.3 / 10.8; 10 / 11")

# ================================================================== R. draft 4 additions (paper/flycraft.tex, 25 Sep 2026)
section("R. Numbers added in draft 4 (`paper/flycraft.tex`, 25 Sep 2026): the freeze across gains, the male's cVA -> MN9")
g_ = GF_.groupby(["gain", "input"])[["DNa L", "DNa R"]].mean()
def freeze_ix(gain, base, touched):
    return 1 - g_.loc[(gain, touched)].mean() / g_.loc[(gain, base)].mean()
check("freeze index (1 - DNa with touch / DNa alone), food odour / cVA drive, at gain 1.0; 1.4; 2.0",
      "; ".join(f"{freeze_ix(gg, 'food odor', 'food + touch'):.2f} / {freeze_ix(gg, 'cVA (Or67d/DA1)', 'cVA + touch'):.2f}" for gg in (1.0, 1.4, 2.0)),
      "0.69 / 0.93; 0.74 / 0.89; 0.86 / 0.93")
gmn9 = GM_.groupby(["gain", "input"])["MN9"].mean()
check("male cVA -> MN9 at gain 0.7 / 1.0 / 1.4", " / ".join(f"{gmn9.loc[(gg, 'cVA (Or67d/DA1)')]:.1f}" for gg in (0.7, 1.0, 1.4)), "7.5 / 32.5 / 36.5")
check("male cVA -> MN9 over the 13 male sensitivity conditions (min-max)", f"{SM['cVA (Or67d/DA1) -> MN9'].min():.1f}-{SM['cVA (Or67d/DA1) -> MN9'].max():.1f}", "14.7-35.0")
shm_ = csv(f"shuffle_malecns_{PAPER_M}_global.csv")
check("male cVA -> MN9 and DNp13 in the rewired brains (largest mean over the rewirings)",
      f"{shm_[(shm_.shuffle >= 0) & (shm_.input == 'cVA (Or67d/DA1)')].groupby('shuffle')[['MN9', 'DNp13 reject']].mean().max().max():.1f}", "0.0")

emit(); emit(f"---"); emit(f"{NCHECK} cells compared with the paper's text, {NDIFF} differ beyond rounding (marked **DIFFERS**).")
with open(a.out, "w") as fh:
    fh.write("# Paper numbers, re-derived from the result files\n\n(`python experiments/paper_numbers.py`; each line: computed value | the value typed in PAPER.md | verdict)\n" + "\n".join(LINES) + "\n")
print("wrote", a.out)
