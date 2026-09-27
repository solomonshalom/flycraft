# Arena log audit (edge suite S4)

Written by `experiments/edge/arena_audit.py` from 20 logs (`fly*_off-*.csv` in logs; the encounter_stats.py filter: >= 50 rows, trial label `off_*`) — QUICK: series noise0.2 only. Pairs (figures.py rule: same label, stamps <= 10 s apart, one fly1 + one fly2): 10; unpaired logs: 0. Contact = obs_taste_fly_female + obs_taste_fly_male > 0 (< 1.3 blocks); one row = one 50-ms brain tick; turn and azimuth are + = left (observe.js / motor.py).

Index check against `release/pre_rerun_20260926/results/encounter_trials.csv`: 20 of its 140 logs found (the rest are outside --quick), 0 differ in ticks / contact ticks / longest bout; 0 logs here are not in it.

## 0. The paper's numbers, reproduced first

Turn-toward index (replication_stats.py `toward`): mean of `ctl_turn × sign(near_az)` over the female logs' ticks before the log's first contact with `near_dist < 6` and `near_az` present, pooled over the ticks of all logs of the series (n = ticks).

| series | pairing | index (n ticks) | printed | match |
|---|---|---|---|---|
| specific noise0.2 | ff | +0.002 (539) | +0.002 (539) | yes |
| specific noise0.2 | mf | +0.033 (1283) | +0.033 (1283) | yes |

Pooled lean (replication_stats.py, 'Leaning towards the partner'): female logs of the specific-lobe series it pools (noise0.2); per-log index = mean of `ctl_turn × sign(near_az)` over the same ticks, for logs with >= 1 such tick and a nonzero turn command on one of them ('turn at all'); two-sided exact sign test on towards (> 0) vs away (< 0).

| pairing | logs that turn | towards / away (zero) | nonzero | sign test p | pooled index | mean abs(turn) | index / mean abs(turn) | printed | match |
|---|---|---|---|---|---|---|---|---|---|
| mf | 5 | 5 / 0 (0) | 5 | 0.062 | +0.033 | 0.281 | +0.12 | 35; 24 / 9; p 0.014; +0.015; +0.06 | – (quick) |
| ff | 8 | 4 / 4 (0) | 8 | 1.000 | +0.002 | 0.281 | +0.01 | 22; 13 / 9; p 0.523; +0.016; +0.06 | – (quick) |

**Digit check: 2 / 2 printed values reproduced.** The paper's '24 of 33' is the 33 mf logs with a nonzero index out of 5 that turn at all (0 have an index of exactly 0).

## 1. Start check: the 6-s launch stagger

`run_pair.sh` starts fly1's bot, sleeps 6 s, then starts fly2's; fly1's brain is already stepping, so fly1 walks before its partner exists. Per trial: fly1's rows with `t_wall` <= fly2's first `t_wall`, fly1's straight-line displacement and path over them; `dist_at_placement` = |fly1's position at its last such row − fly2's first logged position|; fly2's first non-NaN `near_dist`; first contact of the trial = the earlier first-contact `t_wall` of the two logs. **flag_placed** = the trial has contact, `dist_at_placement` <= 1.3 (or the contact came before fly2's first row), and fly2's log shows no row from row 1 on with `near_dist` > 1.3 before it: the flies were never both present and more than 1.3 blocks apart before touching (fly2's row 0 is not used: it can still be read at fly2's pre-teleport spawn). **flag_plan** (design 2.7) = fly2's first `near_dist` < 3 and its first contact within 40 rows.

Start configurations (trials.sh POS; `faces` = cos of the angle between a fly's heading and the direction to its partner, 1 = facing, −1 = facing away):

| cfg | fly1 | fly2 | distance | fly1 faces | fly2 faces |
|---|---|---|---|---|---|
| t1 | (-2.0, 0.0) | (2.0, 0.0) | 4.00 | +1.00 | +1.00 |
| t2 | (0.0, -2.0) | (0.0, 2.0) | 4.00 | -1.00 | -1.00 |
| t3 | (2.0, 0.0) | (-2.0, 0.0) | 4.00 | +1.00 | +1.00 |
| t4 | (0.0, 2.0) | (0.0, -2.0) | 4.00 | -1.00 | -1.00 |
| t5 | (-2.0, -2.0) | (2.0, 2.0) | 5.66 | +0.00 | -0.00 |

### The longest bout

- Trial: `off_ff_t4_noise0.2` (specific lobe, chamber noise0.2, start t4: 4.0 blocks, fly1 faces -1.00, fly2 -1.00); the bout is 15.05 s in fly2's log `fly2_off-flywire-noise0.2-known-eln0.25_20260919-005044.csv` (fly1 9.75 s, fly2 15.05 s = run length in ticks × 0.05 s; the paper prints the female maximum to one decimal).
- fly2's brain logged its first row 3.18 s (wall) after fly1's; fly1 had logged 21 rows by then (1.05 s of brain time) and moved 1.13 blocks (path 1.13) from its start, straight along its heading (fly1 faces fly2's start: -1.00); fly1 first sensed any fly -0.07 s from fly2's first row. Logged start distance 4.00 blocks; distance at fly2's placement (fly1 at its row 20 vs fly2's first position) **5.13 blocks**; fly2's first reading (row 1) 5.20 blocks.
- The bout began +237.18 s from fly2's first row (row 1271 of fly2's log; fly2's first contact at its row 959), so fly2 had been placed, but the flies were more than 1.3 blocks apart between placement and the bout (flag_placed = False, flag_plan = False): **a genuine meeting**. Longest bout of this trial that began after the flies had been > 1.3 apart post-placement: fly1 9.75 s, fly2 15.05 s.
- Longest female bout once the 0 flag_placed trials () are dropped: **15.05 s (`off_ff_t4_noise0.2`, noise0.2, fly2)** over every specific-lobe series; 15.05 s (`off_ff_t4_noise0.2`, noise0.2, fly2) in the series first reported; nan s (``, , ) in the replication. Once the 0 flag_plan trials are dropped: 15.05 s (`off_ff_t4_noise0.2`, noise0.2, fly2); first reported 15.05 s (`off_ff_t4_noise0.2`, noise0.2, fly2); replication nan s (``, , ).

### Flagged trials

| trial | series | cfg | stagger s | fly1 rows / moved before fly2 | dist at placement | fly2 first near_dist (row) | first contact (s after fly2) | longest fly1 / fly2 s | placed | plan |
|---|---|---|---|---|---|---|---|---|---|---|

Logged first positions match trials.sh (within 0.2 blocks of POS + 0.5) for 10 of 10 trials. A negative stagger means fly1's brain logged after fly2's (it loaded later; fly1's body stood still where it was placed), so fly1 had no rows before fly2.

Across all 10 trials: stagger 3.17–3.59 s (median 3.38); fly1 rows before fly2 13–22; fly1 displacement before fly2 0.11–5.17 blocks. Trials (all variants) with contact among those that start facing each other (t1, t3; fly1 faces > 0.9): 2 of 4 (2 not flag_placed); the other starts: 5 of 6 (5 not flag_placed).

Trials with contact by start configuration (specific lobe; `placed` = of them flag_placed):

| cfg | faces | ff: trials, with contact (placed) | mf: trials, with contact (placed) |
|---|---|---|---|
| t1 | +1.00 | 1, 0 (0) | 1, 0 (0) |
| t2 | -1.00 | 1, 1 (0) | 1, 1 (0) |
| t3 | +1.00 | 1, 1 (0) | 1, 1 (0) |
| t4 | -1.00 | 1, 1 (0) | 1, 1 (0) |
| t5 | +0.00 | 1, 0 (0) | 1, 1 (0) |

### Series numbers without the flagged trials (female logs, as replication_stats.py)

| series | pairing | excluded | trials with contact | contact, % of ticks (mean ± sd over logs) | longest bout, s | dropped trials |
|---|---|---|---|---|---|---|
| specific noise0.2 | ff | none | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | ff | placed | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | ff | plan | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | mf | none | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |
| specific noise0.2 | mf | placed | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |
| specific noise0.2 | mf | plan | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |

### fly1's turning before and after its partner appears

Mean `ctl_turn` and mean `hz_turn_L − hz_turn_R` (Hz) over fly1's rows up to fly2's first `t_wall` (before) and after; mean ± sd over trials. The published lobe turns left whatever is where (a partner-independent bias shows as equal before and after).

| series | pairing | fly1 | trials | turn before | turn after | DNa L−R before, Hz | DNa L−R after, Hz |
|---|---|---|---|---|---|---|---|
| specific noise0.2 | ff | flywire | 5 | +0.033 ± 0.074 | -0.017 ± 0.009 | +1.62 ± 3.33 | -0.80 ± 0.42 |
| specific noise0.2 | mf | malecns | 5 | -0.009 ± 0.032 | +0.025 ± 0.004 | -0.60 ± 0.78 | +0.18 ± 0.04 |

## 2. Lean check (female logs, specific lobe, every series)

Ticks: before the log's first contact, `near_dist < 6`, `near_az` present (the paper's). Per log: **idx_raw** = mean(turn · sign(az)) (the paper's); **idx_farcorr** = mean((turn − b_far) · sign(az)), b_far = the log's mean `ctl_turn` over non-contact ticks with `near_dist` >= 6 (logs without such ticks drop out); **idx_allcorr** = the same with b_all = the log's mean `ctl_turn` over all ticks; **side_contrast** = (mean turn with the partner on the left − on the right) / 2, logs with >= 10 ticks per side (immune to any constant bias); **idx_minus_bias_x_side** = idx_raw − mean(turn) · mean(sign(az)) (the within-log covariance). Only logs that turn at all enter. Sign tests: two-sided exact on > 0 vs < 0, Holm over mf/ff per index and level. Clusters: the mean index of the logs in a start configuration (`cfg`, t1–t5), a series, or a trial (`trial_id`; the two females of an ff trial), then a sign test over clusters.

| index | level | mf: n, towards / away (0), mean of the per-log (per-cluster) values, p, p Holm | ff: the same |
|---|---|---|---|
| idx_raw | log | 5, 5 / 0 (0), +0.0524, 0.062, 0.125 | 8, 4 / 4 (0), +0.0169, 1.000, 1.000 |
| idx_raw | cfg | 5, 5 / 0 (0), +0.0524, 0.062, 0.125 | 4, 3 / 1 (0), +0.0169, 0.625, 0.625 |
| idx_raw | series | 1, 1 / 0 (0), +0.0524, 1.000, 1.000 | 1, 1 / 0 (0), +0.0169, 1.000, 1.000 |
| idx_raw | trial_id | 5, 5 / 0 (0), +0.0524, 0.062, 0.125 | 4, 3 / 1 (0), +0.0169, 0.625, 0.625 |
| idx_farcorr | log | 5, 3 / 2 (0), +0.0350, 1.000, 1.000 | 8, 5 / 3 (0), +0.0108, 0.727, 1.000 |
| idx_farcorr | cfg | 5, 3 / 2 (0), +0.0350, 1.000, 1.000 | 4, 3 / 1 (0), +0.0108, 0.625, 1.000 |
| idx_farcorr | series | 1, 1 / 0 (0), +0.0350, 1.000, 1.000 | 1, 1 / 0 (0), +0.0108, 1.000, 1.000 |
| idx_farcorr | trial_id | 5, 3 / 2 (0), +0.0350, 1.000, 1.000 | 4, 3 / 1 (0), +0.0108, 0.625, 1.000 |
| idx_allcorr | log | 5, 4 / 1 (0), +0.0346, 0.375, 0.750 | 8, 5 / 3 (0), +0.0121, 0.727, 0.750 |
| idx_allcorr | cfg | 5, 4 / 1 (0), +0.0346, 0.375, 0.750 | 4, 3 / 1 (0), +0.0121, 0.625, 0.750 |
| idx_allcorr | series | 1, 1 / 0 (0), +0.0346, 1.000, 1.000 | 1, 1 / 0 (0), +0.0121, 1.000, 1.000 |
| idx_allcorr | trial_id | 5, 4 / 1 (0), +0.0346, 0.375, 0.750 | 4, 3 / 1 (0), +0.0121, 0.625, 0.750 |
| side_contrast | log | 1, 0 / 1 (0), -0.0217, 1.000, 1.000 | 3, 2 / 1 (0), +0.0331, 1.000, 1.000 |
| side_contrast | cfg | 1, 0 / 1 (0), -0.0217, 1.000, 1.000 | 3, 2 / 1 (0), +0.0331, 1.000, 1.000 |
| side_contrast | series | 1, 0 / 1 (0), -0.0217, 1.000, 1.000 | 1, 1 / 0 (0), +0.0331, 1.000, 1.000 |
| side_contrast | trial_id | 1, 0 / 1 (0), -0.0217, 1.000, 1.000 | 3, 2 / 1 (0), +0.0331, 1.000, 1.000 |
| idx_minus_bias_x_side | log | 5, 2 / 1 (2), +0.0006, 1.000, 1.000 | 8, 2 / 5 (1), +0.0057, 0.453, 0.906 |
| idx_minus_bias_x_side | cfg | 5, 2 / 1 (2), +0.0006, 1.000, 1.000 | 4, 2 / 2 (0), +0.0057, 1.000, 1.000 |
| idx_minus_bias_x_side | series | 1, 1 / 0 (0), +0.0006, 1.000, 1.000 | 1, 1 / 0 (0), +0.0057, 1.000, 1.000 |
| idx_minus_bias_x_side | trial_id | 5, 2 / 1 (2), +0.0006, 1.000, 1.000 | 4, 2 / 2 (0), +0.0057, 1.000, 1.000 |

Time-shift nulls (2000 shifts, `np.random.default_rng(0)` per pairing and kind; the same draws for all three indices): near_az is rolled circularly (within-pre: inside the pre-contact segment, offset uniform over 10–90 % of its length; whole-log: over the log, 10–90 % of its length) while the tick selection and the turn stay real. P = share of shifts whose net (towards − away) is >= the observed; P(mean) the same for the mean per-log index.

| pairing | index | null | n logs | observed net / mean | null net mean ± sd | P(net) | P(mean) |
|---|---|---|---|---|---|---|---|
| mf | idx_raw | within-pre | 5 | +5 / +0.0524 | +2.2 ± 1.3 | 0.0305 | 0.0850 |
| mf | idx_farcorr | within-pre | 5 | +1 / +0.0350 | +0.3 ± 1.4 | 0.6300 | 0.1850 |
| mf | idx_allcorr | within-pre | 5 | +3 / +0.0346 | +0.7 ± 1.6 | 0.1730 | 0.1820 |
| mf | idx_raw | whole-log | 5 | +5 / +0.0524 | -0.2 ± 1.7 | 0.0030 | 0.0000 |
| mf | idx_farcorr | whole-log | 5 | +1 / +0.0350 | -2.0 ± 1.7 | 0.1215 | 0.0030 |
| mf | idx_allcorr | whole-log | 5 | +3 / +0.0346 | -1.6 ± 1.9 | 0.0290 | 0.0030 |
| ff | idx_raw | within-pre | 8 | +0 / +0.0169 | +0.6 ± 2.3 | 0.7545 | 0.3865 |
| ff | idx_farcorr | within-pre | 8 | +2 / +0.0108 | -0.1 ± 2.2 | 0.3195 | 0.2270 |
| ff | idx_allcorr | within-pre | 8 | +2 / +0.0121 | -0.1 ± 2.2 | 0.3080 | 0.2480 |
| ff | idx_raw | whole-log | 8 | +0 / +0.0169 | +0.9 ± 2.3 | 0.8140 | 0.3980 |
| ff | idx_farcorr | whole-log | 8 | +2 / +0.0108 | +0.0 ± 2.2 | 0.3400 | 0.2225 |
| ff | idx_allcorr | whole-log | 8 | +2 / +0.0121 | +0.0 ± 2.2 | 0.3390 | 0.2455 |

Per-log lean against the sign of (mean turn × mean side) over the same ticks: a lean that only reflects a turning bias times the side the partner happened to sit on has sign(idx_raw) = sign(mean_turn_pre × mean_side_pre).

| pairing | logs (turn, both signs nonzero) | sign(idx) = sign(bias × side) | of the towards logs | of the away logs | logs with far ticks | smell L−R agrees with sign(az), mean share of ticks |
|---|---|---|---|---|---|---|
| mf | 5 | 4 | 4 / 5 | 0 / 0 | 5 / 5 | 1.000 |
| ff | 8 | 8 | 4 / 4 | 4 / 4 | 8 / 8 | 0.989 |

**S4 criterion (keep the lean only if the far-bias-corrected mf sign test leans towards with p < 0.025 under Holm over mf/ff (Holm-adjusted p < 0.05) and the within-pre-contact shift null P < 0.05):** far-corrected mf 3 / 2, p = 1.000, Holm p = 1.000; within-pre shift P(net) = 0.0305 → **CHANGE**.

## 3. Body speed and stalls

Per row: wall gap = Δ`t_wall`; displacement = |Δ(x, z)|; walk = the previous row's `ctl_walk` (the drive the body executed over the gap); only rows with walk > 0.2. Per log: share of rows with gap > 0.8 s (stalled if > 5%), brain time (short if < 60 s), displacement per unit walk = mean(displacement) / mean(walk).

| gap bin, s (all logs) | rows | mean gap | mean displacement | mean walk | displacement per unit walk |
|---|---|---|---|---|---|
| (0.0, 0.1] | 1 | 0.100 | 0.000 | 0.865 | 0.000 |
| (0.1, 0.2] | 23192 | 0.166 | 0.046 | 0.558 | 0.082 |
| (0.2, 0.4] | 4505 | 0.236 | 0.067 | 0.527 | 0.126 |
| (0.4, 0.8] | 100 | 0.499 | 0.059 | 0.580 | 0.103 |
| (0.8, 1.6] | 3 | 1.028 | 0.058 | 0.442 | 0.132 |

| series | pairing | logs | brain s (mean) | brain / wall | median gap s | rows with gap > 0.8 s | stalled / short logs | displacement per unit walk | blocks per brain-s | comparable |
|---|---|---|---|---|---|---|---|---|---|---|
| specific noise0.2 | ff | 10 | 84 | 0.28 | 0.168 | 0.0% | 0 / 0 | 0.063 | 0.743 | yes |
| specific noise0.2 | mf | 10 | 82 | 0.28 | 0.172 | 0.0% | 0 / 0 | 0.172 | 1.162 | yes |

A series is comparable when its pooled share of rows with a gap over 0.8 s is <= 5 % and its mean brain time >= 60 s (S4). Stalled logs: none. Short logs: none.
