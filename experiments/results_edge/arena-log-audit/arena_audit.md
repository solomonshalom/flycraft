# Arena log audit (edge suite S4)

Written by `experiments/edge/arena_audit.py` from 140 logs (`fly*_off-*.csv` in logs; the encounter_stats.py filter: >= 50 rows, trial label `off_*`). Pairs (figures.py rule: same label, stamps <= 10 s apart, one fly1 + one fly2): 68; paired only within 60 s (the loaded replication): off_mf_t2_rep-clean_20260926-014512, off_mf_t5_rep-clean_20260926-020236; unpaired logs: 0. Contact = obs_taste_fly_female + obs_taste_fly_male > 0 (< 1.3 blocks); one row = one 50-ms brain tick; turn and azimuth are + = left (observe.js / motor.py).

Index check against `release/pre_rerun_20260926/results/encounter_trials.csv`: 140 of its 140 logs found, 0 differ in ticks / contact ticks / longest bout; 0 logs here are not in it.

## 0. The paper's numbers, reproduced first

Turn-toward index (replication_stats.py `toward`): mean of `ctl_turn × sign(near_az)` over the female logs' ticks before the log's first contact with `near_dist < 6` and `near_az` present, pooled over the ticks of all logs of the series (n = ticks).

| series | pairing | index (n ticks) | printed | match |
|---|---|---|---|---|
| published odor-free | ff | -0.19 (1974) | -0.19 | yes |
| published odor-free | mf | +0.08 (227) | +0.08 | yes |
| specific faint-smell | ff | +0.011 (257) | – | – |
| specific faint-smell | mf | +0.014 (754) | – | – |
| specific clean | ff | +0.000 (26755) | +0.000 (26755) | yes |
| specific clean | mf | -0.021 (419) | -0.021 (419) | yes |
| specific rep-clean | ff | +0.000 (15236) | +0.000 (15236) | yes |
| specific rep-clean | mf | +0.011 (121) | +0.011 (121) | yes |
| specific noise0.2 | ff | +0.002 (539) | +0.002 (539) | yes |
| specific noise0.2 | mf | +0.033 (1283) | +0.033 (1283) | yes |
| specific rep-noise0.2 | ff | +0.028 (767) | +0.028 (767) | yes |
| specific rep-noise0.2 | mf | +0.012 (383) | +0.012 (383) | yes |
| specific noise0.2-virgin | mf | -0.005 (668) | -0.005 (668) | yes |
| specific rep-noise0.2-virgin | mf | +0.040 (349) | +0.040 (349) | yes |

Pooled lean (replication_stats.py, 'Leaning towards the partner'): female logs of the specific-lobe series it pools (faint-smell, clean, rep-clean, noise0.2, rep-noise0.2, noise0.2-virgin, rep-noise0.2-virgin); per-log index = mean of `ctl_turn × sign(near_az)` over the same ticks, for logs with >= 1 such tick and a nonzero turn command on one of them ('turn at all'); two-sided exact sign test on towards (> 0) vs away (< 0).

| pairing | logs that turn | towards / away (zero) | nonzero | sign test p | pooled index | mean abs(turn) | index / mean abs(turn) | printed | match |
|---|---|---|---|---|---|---|---|---|---|
| mf | 35 | 24 / 9 (2) | 33 | 0.014 | +0.015 | 0.250 | +0.06 | 35; 24 / 9; p 0.014; +0.015; +0.06 | yes |
| ff | 22 | 13 / 9 (0) | 22 | 0.523 | +0.016 | 0.265 | +0.06 | 22; 13 / 9; p 0.523; +0.016; +0.06 | yes |

**Digit check: 14 / 14 printed values reproduced.** The paper's '24 of 33' is the 33 mf logs with a nonzero index out of 35 that turn at all (2 have an index of exactly 0).

## 1. Start check: the 6-s launch stagger

`run_pair.sh` starts fly1's bot, sleeps 6 s, then starts fly2's; fly1's brain is already stepping, so fly1 walks before its partner exists. Per trial: fly1's rows with `t_wall` <= fly2's first `t_wall`, fly1's straight-line displacement and path over them; `dist_at_placement` = |fly1's position at its last such row − fly2's first logged position| (if fly1's brain logged later, its first position against fly2's at that moment); fly2's first non-NaN `near_dist`; first contact of the trial = the earlier first-contact `t_wall` of the two logs. **flag_placed** = the trial has contact, `dist_at_placement` <= 1.3 (or the contact came before both brains logged), and fly2's log shows no row from row 1 on with `near_dist` > 1.3 before it: the flies were never both present and more than 1.3 blocks apart before touching (fly2's row 0 is not used: it can still be read at fly2's pre-teleport spawn). **flag_plan** (design 2.7) = fly2's first `near_dist` < 3 and its first contact within 40 rows.

Start configurations (trials.sh POS; `faces` = cos of the angle between a fly's heading and the direction to its partner, 1 = facing, −1 = facing away):

| cfg | fly1 | fly2 | distance | fly1 faces | fly2 faces |
|---|---|---|---|---|---|
| t1 | (-2.0, 0.0) | (2.0, 0.0) | 4.00 | +1.00 | +1.00 |
| t2 | (0.0, -2.0) | (0.0, 2.0) | 4.00 | -1.00 | -1.00 |
| t3 | (2.0, 0.0) | (-2.0, 0.0) | 4.00 | +1.00 | +1.00 |
| t4 | (0.0, 2.0) | (0.0, -2.0) | 4.00 | -1.00 | -1.00 |
| t5 | (-2.0, -2.0) | (2.0, 2.0) | 5.66 | +0.00 | -0.00 |

### The longest bout

- Trial: `off_ff_t3` (specific lobe, chamber faint-smell, start t3: 4.0 blocks, fly1 faces +1.00, fly2 +1.00); the bout is 86.25 s in fly1's log `fly1_off-flywire-known-eln0.25_20260917-141245.csv` (fly1 86.25 s, fly2 86.20 s = run length in ticks × 0.05 s; the paper prints the female maximum to one decimal).
- fly2's brain logged its first row 3.40 s (wall) after fly1's; fly1 had logged 28 rows by then (1.40 s of brain time) and moved 4.53 blocks (path 4.54) from its start, straight along its heading (fly1 faces fly2's start: +1.00); fly1 first sensed any fly -0.03 s from fly2's first row. Logged start distance 4.00 blocks; distance at fly2's placement (fly1 at its row 27 vs fly2's first position) **0.54 blocks**; fly2's first reading (row 1) 0.61 blocks, inside the 1.3-block touch range.
- The bout began +0.18 s from fly2's first row (row 28 of fly1's log; fly2's first contact at its row 1), so fly2 had been placed, but the flies were never more than 1.3 blocks apart between placement and the bout (flag_placed = True, flag_plan = True): **not a meeting, a placement artefact**. Longest bout of this trial that began after the flies had been > 1.3 apart post-placement: fly1 0.00 s, fly2 0.00 s.
- Longest female bout once the 2 flag_placed trials (faint-smell off_ff_t1, faint-smell off_ff_t3) are dropped: **31.15 s (`off_ff_t2_rep-noise0.2`, rep-noise0.2, fly1)** over every specific-lobe series; 25.70 s (`off_ff_t2`, faint-smell, fly1) in the series first reported; 31.15 s (`off_ff_t2_rep-noise0.2`, rep-noise0.2, fly1) in the replication. Once the 6 flag_plan trials are dropped: 31.15 s (`off_ff_t2_rep-noise0.2`, rep-noise0.2, fly1); first reported 25.70 s (`off_ff_t2`, faint-smell, fly1); replication 31.15 s (`off_ff_t2_rep-noise0.2`, rep-noise0.2, fly1).

### Flagged trials

| trial | series | cfg | stagger s | fly1 rows / moved before fly2 | dist at placement | fly2 first near_dist (row) | first contact (s after fly2) | longest fly1 / fly2 s | placed | plan |
|---|---|---|---|---|---|---|---|---|---|---|
| off_mf_t1 | published odor-free | t1 | 4.53 | 20 / 2.08 | 2.02 | 1.95 (1) | +1.07 | 0.05 / 0.05 |  | x |
| off_mf_t3 | published odor-free | t3 | 4.77 | 23 / 2.09 | 1.95 | 1.76 (1) | +0.92 | 1.30 / 1.55 |  | x |
| off_ff_t1 | specific faint-smell | t1 | 3.43 | 24 / 2.89 | 1.11 | 0.99 (0) | +0.00 | 16.05 / 16.55 | x | x |
| off_ff_t3 | specific faint-smell | t3 | 3.40 | 28 / 4.53 | 0.54 | 0.61 (1) | +0.18 | 86.25 / 86.20 | x | x |
| off_ff_t1_rep-noise0.2 | specific rep-noise0.2 | t1 | 3.56 | 21 / 2.21 | 1.94 | 1.89 (1) | +0.95 | 19.60 / 23.10 |  | x |
| off_ff_t3_rep-noise0.2 | specific rep-noise0.2 | t3 | 3.51 | 21 / 1.45 | 2.56 | 2.57 (0) | +1.39 | 20.30 / 15.55 |  | x |

Logged first positions match trials.sh (within 0.2 blocks of POS + 0.5) for 69 of 70 trials: not rep-clean off_ff_t4_rep-clean (fly1 off by 2.83, fly2 by 0.00). A negative stagger means fly1's brain logged after fly2's (it loaded later; fly1's body stood still where it was placed), so fly1 had no rows before fly2.

Across all 70 trials: stagger -15.79–5.25 s (median 3.41); fly1 rows before fly2 0–55; fly1 displacement before fly2 0.00–5.17 blocks. Trials (all variants) with contact among those that start facing each other (t1, t3; fly1 faces > 0.9): 19 of 28 (17 not flag_placed); the other starts: 19 of 42 (19 not flag_placed).

Trials with contact by start configuration (specific lobe; `placed` = of them flag_placed):

| cfg | faces | ff: trials, with contact (placed) | mf: trials, with contact (placed) |
|---|---|---|---|
| t1 | +1.00 | 5, 2 (1) | 7, 5 (0) |
| t2 | -1.00 | 5, 3 (0) | 7, 4 (0) |
| t3 | +1.00 | 5, 3 (1) | 7, 7 (0) |
| t4 | -1.00 | 5, 2 (0) | 7, 3 (0) |
| t5 | +0.00 | 5, 2 (0) | 7, 3 (0) |

### Series numbers without the flagged trials (female logs, as replication_stats.py)

| series | pairing | excluded | trials with contact | contact, % of ticks (mean ± sd over logs) | longest bout, s | dropped trials |
|---|---|---|---|---|---|---|
| published odor-free | ff | none | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| published odor-free | ff | placed | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| published odor-free | ff | plan | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| published odor-free | mf | none | 4 / 5 | 3.6 ± 3.5 | 2.85 | – |
| published odor-free | mf | placed | 4 / 5 | 3.6 ± 3.5 | 2.85 | – |
| published odor-free | mf | plan | 2 / 3 | 4.4 ± 4.1 | 2.85 | off_mf_t1;off_mf_t3 |
| specific faint-smell | ff | none | 4 / 5 | 39.5 ± 34.4 | 86.25 | – |
| specific faint-smell | ff | placed | 2 / 3 | 20.4 ± 16.8 | 25.70 | off_ff_t1;off_ff_t3 |
| specific faint-smell | ff | plan | 2 / 3 | 20.4 ± 16.8 | 25.70 | off_ff_t1;off_ff_t3 |
| specific faint-smell | mf | none | 1 / 5 | 1.2 ± 2.6 | 1.95 | – |
| specific faint-smell | mf | placed | 1 / 5 | 1.2 ± 2.6 | 1.95 | – |
| specific faint-smell | mf | plan | 1 / 5 | 1.2 ± 2.6 | 1.95 | – |
| specific clean | ff | none | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific clean | ff | placed | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific clean | ff | plan | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific clean | mf | none | 2 / 5 | 0.5 ± 0.9 | 0.95 | – |
| specific clean | mf | placed | 2 / 5 | 0.5 ± 0.9 | 0.95 | – |
| specific clean | mf | plan | 2 / 5 | 0.5 ± 0.9 | 0.95 | – |
| specific rep-clean | ff | none | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific rep-clean | ff | placed | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific rep-clean | ff | plan | 0 / 5 | 0.0 ± 0.0 | 0.00 | – |
| specific rep-clean | mf | none | 2 / 5 | 1.8 ± 3.7 | 0.55 | – |
| specific rep-clean | mf | placed | 2 / 5 | 1.8 ± 3.7 | 0.55 | – |
| specific rep-clean | mf | plan | 2 / 5 | 1.8 ± 3.7 | 0.55 | – |
| specific noise0.2 | ff | none | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | ff | placed | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | ff | plan | 3 / 5 | 11.2 ± 14.9 | 15.05 | – |
| specific noise0.2 | mf | none | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |
| specific noise0.2 | mf | placed | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |
| specific noise0.2 | mf | plan | 4 / 5 | 1.3 ± 1.1 | 1.30 | – |
| specific rep-noise0.2 | ff | none | 5 / 5 | 59.1 ± 15.8 | 31.15 | – |
| specific rep-noise0.2 | ff | placed | 5 / 5 | 59.1 ± 15.8 | 31.15 | – |
| specific rep-noise0.2 | ff | plan | 3 / 3 | 57.9 ± 14.0 | 31.15 | off_ff_t1_rep-noise0.2;off_ff_t3_rep-noise0.2 |
| specific rep-noise0.2 | mf | none | 3 / 5 | 1.5 ± 1.5 | 2.45 | – |
| specific rep-noise0.2 | mf | placed | 3 / 5 | 1.5 ± 1.5 | 2.45 | – |
| specific rep-noise0.2 | mf | plan | 3 / 5 | 1.5 ± 1.5 | 2.45 | – |
| specific noise0.2-virgin | mf | none | 5 / 5 | 3.6 ± 3.2 | 1.70 | – |
| specific noise0.2-virgin | mf | placed | 5 / 5 | 3.6 ± 3.2 | 1.70 | – |
| specific noise0.2-virgin | mf | plan | 5 / 5 | 3.6 ± 3.2 | 1.70 | – |
| specific rep-noise0.2-virgin | mf | none | 5 / 5 | 6.3 ± 7.2 | 4.55 | – |
| specific rep-noise0.2-virgin | mf | placed | 5 / 5 | 6.3 ± 7.2 | 4.55 | – |
| specific rep-noise0.2-virgin | mf | plan | 5 / 5 | 6.3 ± 7.2 | 4.55 | – |

### fly1's turning before and after its partner appears

Mean `ctl_turn` and mean `hz_turn_L − hz_turn_R` (Hz) over fly1's rows up to fly2's first `t_wall` (before) and after; mean ± sd over trials. The published lobe turns left whatever is where (a partner-independent bias shows as equal before and after).

| series | pairing | fly1 | trials | turn before | turn after | DNa L−R before, Hz | DNa L−R after, Hz |
|---|---|---|---|---|---|---|---|
| published odor-free | ff | flywire | 5 | +0.585 ± 0.050 | +0.617 ± 0.003 | +29.55 ± 3.34 | +32.13 ± 0.19 |
| published odor-free | mf | malecns | 5 | +0.080 ± 0.007 | +0.076 ± 0.002 | +0.54 ± 0.45 | +0.13 ± 0.06 |
| specific faint-smell | ff | flywire | 5 | -0.076 ± 0.075 | +0.008 ± 0.009 | -3.30 ± 3.36 | +0.33 ± 0.38 |
| specific faint-smell | mf | malecns | 5 | +0.012 ± 0.013 | +0.064 ± 0.006 | -0.28 ± 0.41 | +1.75 ± 0.18 |
| specific clean | ff | flywire | 5 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.00 ± 0.00 | +0.00 ± 0.00 |
| specific clean | mf | malecns | 5 | +0.000 ± 0.000 | +0.060 ± 0.006 | +0.00 ± 0.00 | +1.26 ± 0.71 |
| specific noise0.2 | ff | flywire | 5 | +0.033 ± 0.074 | -0.017 ± 0.009 | +1.62 ± 3.33 | -0.80 ± 0.42 |
| specific noise0.2 | mf | malecns | 5 | -0.009 ± 0.032 | +0.025 ± 0.004 | -0.60 ± 0.78 | +0.18 ± 0.04 |
| specific noise0.2-virgin | mf | malecns | 5 | +0.031 ± 0.054 | +0.026 ± 0.002 | +0.73 ± 2.02 | +0.12 ± 0.09 |
| specific rep-clean | ff | flywire | 5 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.00 ± 0.00 | +0.00 ± 0.00 |
| specific rep-clean | mf | malecns | 5 | +0.000 ± nan | +0.059 ± 0.015 | +0.00 ± nan | +1.30 ± 0.46 |
| specific rep-noise0.2 | ff | flywire | 5 | -0.093 ± 0.074 | -0.007 ± 0.008 | -4.35 ± 3.33 | -0.34 ± 0.34 |
| specific rep-noise0.2 | mf | malecns | 5 | +0.060 ± 0.087 | +0.027 ± 0.005 | +1.99 ± 3.13 | +0.21 ± 0.26 |
| specific rep-noise0.2-virgin | mf | malecns | 5 | +0.034 ± 0.017 | +0.029 ± 0.004 | +1.01 ± 0.85 | +0.18 ± 0.07 |

## 2. Lean check (female logs, specific lobe, every series)

Ticks: before the log's first contact, `near_dist < 6`, `near_az` present (the paper's). Per log: **idx_raw** = mean(turn · sign(az)) (the paper's); **idx_farcorr** = mean((turn − b_far) · sign(az)), b_far = the log's mean `ctl_turn` over non-contact ticks with `near_dist` >= 6 (logs without such ticks drop out); **idx_allcorr** = the same with b_all = the log's mean `ctl_turn` over all ticks; **side_contrast** = (mean turn with the partner on the left − on the right) / 2, logs with >= 10 ticks per side (immune to any constant bias); **idx_minus_bias_x_side** = idx_raw − mean(turn) · mean(sign(az)) (the within-log covariance). Only logs that turn at all enter. Sign tests: two-sided exact on > 0 vs < 0, Holm over mf/ff per index and level. Clusters: the mean index of the logs in a start configuration (`cfg`, t1–t5), a series, or a trial (`trial_id`; the two females of an ff trial), then a sign test over clusters.

| index | level | mf: n, towards / away (0), mean of the per-log (per-cluster) values, p, p Holm | ff: the same |
|---|---|---|---|
| idx_raw | log | 35, 24 / 9 (2), +0.0255, 0.014, 0.027 | 22, 13 / 9 (0), -0.0031, 0.523, 0.523 |
| idx_raw | cfg | 5, 5 / 0 (0), +0.0255, 0.062, 0.125 | 5, 3 / 2 (0), -0.0083, 1.000, 1.000 |
| idx_raw | series | 7, 5 / 2 (0), +0.0255, 0.453, 0.906 | 3, 2 / 1 (0), +0.0019, 1.000, 1.000 |
| idx_raw | trial_id | 35, 24 / 9 (2), +0.0255, 0.014, 0.027 | 11, 7 / 4 (0), -0.0031, 0.549, 0.549 |
| idx_farcorr | log | 35, 15 / 20 (0), +0.0090, 0.500, 0.999 | 22, 11 / 11 (0), -0.0021, 1.000, 1.000 |
| idx_farcorr | cfg | 5, 3 / 2 (0), +0.0090, 1.000, 1.000 | 5, 3 / 2 (0), -0.0071, 1.000, 1.000 |
| idx_farcorr | series | 7, 4 / 3 (0), +0.0090, 1.000, 1.000 | 3, 2 / 1 (0), -0.0001, 1.000, 1.000 |
| idx_farcorr | trial_id | 35, 15 / 20 (0), +0.0090, 0.500, 0.500 | 11, 8 / 3 (0), -0.0021, 0.227, 0.453 |
| idx_allcorr | log | 35, 17 / 18 (0), +0.0098, 1.000, 1.000 | 22, 13 / 9 (0), -0.0057, 0.523, 1.000 |
| idx_allcorr | cfg | 5, 4 / 1 (0), +0.0098, 0.375, 0.750 | 5, 2 / 3 (0), -0.0107, 1.000, 1.000 |
| idx_allcorr | series | 7, 4 / 3 (0), +0.0098, 1.000, 1.000 | 3, 2 / 1 (0), -0.0017, 1.000, 1.000 |
| idx_allcorr | trial_id | 35, 17 / 18 (0), +0.0098, 1.000, 1.000 | 11, 7 / 4 (0), -0.0057, 0.549, 1.000 |
| side_contrast | log | 12, 6 / 6 (0), -0.0052, 1.000, 1.000 | 6, 4 / 2 (0), +0.0008, 0.688, 1.000 |
| side_contrast | cfg | 5, 2 / 3 (0), +0.0021, 1.000, 1.000 | 4, 2 / 2 (0), -0.0053, 1.000, 1.000 |
| side_contrast | series | 7, 3 / 4 (0), -0.0033, 1.000, 1.000 | 2, 1 / 1 (0), +0.0008, 1.000, 1.000 |
| side_contrast | trial_id | 12, 6 / 6 (0), -0.0052, 1.000, 1.000 | 5, 3 / 2 (0), -0.0026, 1.000, 1.000 |
| idx_minus_bias_x_side | log | 35, 14 / 11 (10), -0.0010, 0.690, 1.000 | 22, 4 / 7 (11), -0.0023, 0.549, 1.000 |
| idx_minus_bias_x_side | cfg | 5, 2 / 3 (0), -0.0010, 1.000, 1.000 | 5, 2 / 3 (0), -0.0037, 1.000, 1.000 |
| idx_minus_bias_x_side | series | 7, 4 / 3 (0), -0.0010, 1.000, 1.000 | 3, 1 / 1 (1), -0.0013, 1.000, 1.000 |
| idx_minus_bias_x_side | trial_id | 35, 14 / 11 (10), -0.0010, 0.690, 1.000 | 11, 3 / 4 (4), -0.0023, 1.000, 1.000 |

Time-shift nulls (2000 shifts, `np.random.default_rng(0)` per pairing and kind; the same draws for all three indices): near_az is rolled circularly (within-pre: inside the pre-contact segment, offset uniform over 10–90 % of its length; whole-log: over the log, 10–90 % of its length) while the tick selection and the turn stay real. P = share of shifts whose net (towards − away) is >= the observed; P(mean) the same for the mean per-log index.

| pairing | index | null | n logs | observed net / mean | null net mean ± sd | P(net) | P(mean) |
|---|---|---|---|---|---|---|---|
| mf | idx_raw | within-pre | 35 | +15 / +0.0255 | +10.2 ± 4.2 | 0.1530 | 0.3085 |
| mf | idx_farcorr | within-pre | 35 | -5 / +0.0090 | +1.7 ± 4.0 | 0.9705 | 0.2645 |
| mf | idx_allcorr | within-pre | 35 | -1 / +0.0098 | +1.9 ± 4.1 | 0.8325 | 0.2645 |
| mf | idx_raw | whole-log | 35 | +15 / +0.0255 | +6.9 ± 4.6 | 0.0460 | 0.0380 |
| mf | idx_farcorr | whole-log | 35 | -5 / +0.0090 | -1.1 ± 4.7 | 0.8545 | 0.0730 |
| mf | idx_allcorr | whole-log | 35 | -1 / +0.0098 | -1.1 ± 4.7 | 0.5850 | 0.0670 |
| ff | idx_raw | within-pre | 22 | +4 / -0.0031 | +4.2 ± 3.3 | 0.5950 | 0.8900 |
| ff | idx_farcorr | within-pre | 22 | +0 / -0.0021 | +0.4 ± 3.4 | 0.6210 | 0.8660 |
| ff | idx_allcorr | within-pre | 22 | +4 / -0.0057 | +2.0 ± 3.4 | 0.3570 | 0.8910 |
| ff | idx_raw | whole-log | 22 | +4 / -0.0031 | +1.7 ± 3.9 | 0.3595 | 0.7250 |
| ff | idx_farcorr | whole-log | 22 | +0 / -0.0021 | +0.3 ± 3.9 | 0.6285 | 0.5805 |
| ff | idx_allcorr | whole-log | 22 | +4 / -0.0057 | -0.8 ± 3.8 | 0.1655 | 0.7100 |

Per-log lean against the sign of (mean turn × mean side) over the same ticks: a lean that only reflects a turning bias times the side the partner happened to sit on has sign(idx_raw) = sign(mean_turn_pre × mean_side_pre).

| pairing | logs (turn, both signs nonzero) | sign(idx) = sign(bias × side) | of the towards logs | of the away logs | logs with far ticks | smell L−R agrees with sign(az), mean share of ticks |
|---|---|---|---|---|---|---|
| mf | 33 | 27 | 21 / 24 | 6 / 9 | 35 / 35 | 0.997 |
| ff | 22 | 22 | 13 / 13 | 9 / 9 | 22 / 22 | 0.996 |

**S4 criterion (keep the lean only if the far-bias-corrected mf sign test leans towards with p < 0.025 under Holm over mf/ff (Holm-adjusted p < 0.05) and the within-pre-contact shift null P < 0.05):** far-corrected mf 15 / 20, p = 0.500, Holm p = 0.999; within-pre shift P(net) = 0.1530 → **CHANGE**.

## 3. Body speed and stalls

Per row: wall gap = Δ`t_wall`; displacement = |Δ(x, z)|; walk = the previous row's `ctl_walk` (the drive the body executed over the gap); only rows with walk > 0.2. Per log: share of rows with gap > 0.8 s (stalled if > 5%), brain time (short if < 60 s), displacement per unit walk = mean(displacement) / mean(walk).

| gap bin, s (all logs) | rows | mean gap | mean displacement | mean walk | displacement per unit walk |
|---|---|---|---|---|---|
| (0.0, 0.1] | 740 | 0.094 | 0.027 | 0.581 | 0.047 |
| (0.1, 0.2] | 75906 | 0.161 | 0.047 | 0.542 | 0.086 |
| (0.2, 0.4] | 38536 | 0.258 | 0.089 | 0.530 | 0.168 |
| (0.4, 0.8] | 4964 | 0.527 | 0.105 | 0.502 | 0.209 |
| (0.8, 1.6] | 1534 | 1.115 | 0.114 | 0.530 | 0.215 |
| (1.6, 3.2] | 746 | 2.143 | 0.162 | 0.535 | 0.303 |
| (3.2, inf] | 84 | 3.993 | 0.210 | 0.519 | 0.404 |

| series | pairing | logs | brain s (mean) | brain / wall | median gap s | rows with gap > 0.8 s | stalled / short logs | displacement per unit walk | blocks per brain-s | comparable |
|---|---|---|---|---|---|---|---|---|---|---|
| published odor-free | ff | 10 | 32 | 0.18 | 0.275 | 0.1% | 0 / 10 | 0.253 | 3.596 | NO |
| published odor-free | mf | 10 | 30 | 0.17 | 0.276 | 0.5% | 0 / 10 | 0.236 | 2.320 | NO |
| specific faint-smell | ff | 10 | 95 | 0.32 | 0.153 | 0.0% | 0 / 0 | 0.055 | 0.352 | yes |
| specific faint-smell | mf | 10 | 80 | 0.31 | 0.160 | 0.0% | 0 / 2 | 0.097 | 0.479 | yes |
| specific clean | ff | 10 | 135 | 0.45 | 0.104 | 0.0% | 0 / 0 | – | 0.000 | yes |
| specific clean | mf | 10 | 87 | 0.29 | 0.161 | 0.0% | 0 / 0 | 0.150 | 0.572 | yes |
| specific rep-clean | ff | 10 | 77 | 0.26 | 0.214 | 3.8% | 4 / 6 | – | 0.016 | yes |
| specific rep-clean | mf | 10 | 12 | 0.04 | 1.023 | 53.8% | 10 / 10 | 0.299 | 1.420 | NO |
| specific noise0.2 | ff | 10 | 84 | 0.28 | 0.168 | 0.0% | 0 / 0 | 0.063 | 0.743 | yes |
| specific noise0.2 | mf | 10 | 82 | 0.28 | 0.172 | 0.0% | 0 / 0 | 0.172 | 1.162 | yes |
| specific rep-noise0.2 | ff | 10 | 142 | 0.24 | 0.188 | 0.5% | 0 / 0 | 0.076 | 0.614 | yes |
| specific rep-noise0.2 | mf | 10 | 96 | 0.16 | 0.231 | 5.3% | 4 / 4 | 0.196 | 1.380 | NO |
| specific noise0.2-virgin | mf | 10 | 60 | 0.20 | 0.218 | 1.6% | 1 / 6 | 0.212 | 1.509 | yes |
| specific rep-noise0.2-virgin | mf | 10 | 98 | 0.16 | 0.226 | 4.7% | 3 / 2 | 0.218 | 1.621 | yes |

A series is comparable when its pooled share of rows with a gap over 0.8 s is <= 5 % and its mean brain time >= 60 s (S4). Stalled logs: fly1_off-flywire-known-eln0.25_20260926-012635.csv, fly1_off-flywire-known-eln0.25_20260926-013220.csv, fly1_off-malecns-eln0.25_20260926-013903.csv, fly1_off-malecns-eln0.25_20260926-014512.csv, fly1_off-malecns-eln0.25_20260926-015006.csv, fly1_off-malecns-eln0.25_20260926-015614.csv, fly1_off-malecns-eln0.25_20260926-020236.csv, fly1_off-malecns-noise0.2-eln0.25_20260924-173609.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-180928.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-182017.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-183219.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-184213.csv, fly2_off-flywire-known-eln0.25_20260926-012635.csv, fly2_off-flywire-known-eln0.25_20260926-013220.csv, fly2_off-flywire-known-eln0.25_20260926-013901.csv, fly2_off-flywire-known-eln0.25_20260926-014500.csv, fly2_off-flywire-known-eln0.25_20260926-015005.csv, fly2_off-flywire-known-eln0.25_20260926-015610.csv, fly2_off-flywire-known-eln0.25_20260926-020224.csv, fly2_off-flywire-noise0.2-known-eln0.25_20260926-180928.csv, fly2_off-flywire-noise0.2-known-eln0.25_20260926-182015.csv, fly2_off-flywire-virgin-noise0.2-known-eln0.25_20260926-183213.csv. Short logs: fly1_off-flywire-known-eln0.25_20260926-012056.csv, fly1_off-flywire-known-eln0.25_20260926-012635.csv, fly1_off-flywire-known-eln0.25_20260926-013220.csv, fly1_off-flywire_20260914-231527.csv, fly1_off-flywire_20260914-231923.csv, fly1_off-flywire_20260914-232307.csv, fly1_off-flywire_20260914-232656.csv, fly1_off-flywire_20260914-235006.csv, fly1_off-malecns-eln0.25_20260917-143605.csv, fly1_off-malecns-eln0.25_20260926-013903.csv, fly1_off-malecns-eln0.25_20260926-014512.csv, fly1_off-malecns-eln0.25_20260926-015006.csv, fly1_off-malecns-eln0.25_20260926-015614.csv, fly1_off-malecns-eln0.25_20260926-020236.csv, fly1_off-malecns-noise0.2-eln0.25_20260924-173609.csv, fly1_off-malecns-noise0.2-eln0.25_20260924-174200.csv, fly1_off-malecns-noise0.2-eln0.25_20260924-174750.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-180928.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-182017.csv, fly1_off-malecns-noise0.2-eln0.25_20260926-183219.csv, fly1_off-malecns_20260914-233047.csv, fly1_off-malecns_20260914-233437.csv, fly1_off-malecns_20260914-233825.csv, fly1_off-malecns_20260914-234215.csv, fly1_off-malecns_20260914-234605.csv, fly2_off-flywire-known-eln0.25_20260917-143604.csv, fly2_off-flywire-known-eln0.25_20260926-012056.csv, fly2_off-flywire-known-eln0.25_20260926-012635.csv, fly2_off-flywire-known-eln0.25_20260926-013220.csv, fly2_off-flywire-known-eln0.25_20260926-013901.csv, fly2_off-flywire-known-eln0.25_20260926-014500.csv, fly2_off-flywire-known-eln0.25_20260926-015005.csv, fly2_off-flywire-known-eln0.25_20260926-015610.csv, fly2_off-flywire-known-eln0.25_20260926-020224.csv, fly2_off-flywire-noise0.2-known-eln0.25_20260926-180928.csv, fly2_off-flywire-noise0.2-known-eln0.25_20260926-182015.csv, fly2_off-flywire-virgin-noise0.2-known-eln0.25_20260924-173608.csv, fly2_off-flywire-virgin-noise0.2-known-eln0.25_20260924-174159.csv, fly2_off-flywire-virgin-noise0.2-known-eln0.25_20260924-174749.csv, fly2_off-flywire-virgin-noise0.2-known-eln0.25_20260926-183213.csv, fly2_off-flywire_20260914-231526.csv, fly2_off-flywire_20260914-231923.csv, fly2_off-flywire_20260914-232307.csv, fly2_off-flywire_20260914-232656.csv, fly2_off-flywire_20260914-233046.csv, fly2_off-flywire_20260914-233436.csv, fly2_off-flywire_20260914-233824.csv, fly2_off-flywire_20260914-234214.csv, fly2_off-flywire_20260914-234605.csv, fly2_off-flywire_20260914-235006.csv.
