# Arena log audit (edge suite S4)

Written by `experiments/edge/arena_audit.py` from 40 logs (`fly*_off-*.csv` in logs/edge_arena/sync-clean, logs/edge_arena/sync-noise0.2-notouch, logs/edge_arena/sync-noise0.2; the encounter_stats.py filter: >= 50 rows, trial label `off_*`). Pairs (figures.py rule: same label, stamps <= 10 s apart, one fly1 + one fly2): 20; unpaired logs: 0. Contact = obs_taste_fly_female + obs_taste_fly_male > 0 (< 1.3 blocks); one row = one 50-ms brain tick; turn and azimuth are + = left (observe.js / motor.py).

Index check against `release/pre_rerun_20260926/results/encounter_trials.csv`: 0 of its 140 logs found, 0 differ in ticks / contact ticks / longest bout; 40 logs here are not in it.

## 0. The paper's numbers, reproduced first

Turn-toward index (replication_stats.py `toward`): mean of `ctl_turn × sign(near_az)` over the female logs' ticks before the log's first contact with `near_dist < 6` and `near_az` present, pooled over the ticks of all logs of the series (n = ticks).

| series | pairing | index (n ticks) | printed | match |
|---|---|---|---|---|
| specific sync-clean | mf | +0.003 (2881) | – | – |
| specific sync-noise0.2 | ff | -0.018 (1181) | – | – |
| specific sync-noise0.2 | mf | +0.014 (613) | – | – |
| specific sync-noise0.2-notouch | ff | +0.030 (747) | – | – |

Pooled lean (replication_stats.py, 'Leaning towards the partner'): female logs of the specific-lobe series it pools (; not pooled here, as there: sync-clean, sync-noise0.2, sync-noise0.2-notouch); per-log index = mean of `ctl_turn × sign(near_az)` over the same ticks, for logs with >= 1 such tick and a nonzero turn command on one of them ('turn at all'); two-sided exact sign test on towards (> 0) vs away (< 0).

| pairing | logs that turn | towards / away (zero) | nonzero | sign test p | pooled index | mean abs(turn) | index / mean abs(turn) | printed | match |
|---|---|---|---|---|---|---|---|---|---|
| mf | 0 | 0 / 0 (0) | 0 | nan | +nan | nan | +nan | 35; 24 / 9; p 0.014; +0.015; +0.06 | NO |
| ff | 0 | 0 / 0 (0) | 0 | nan | +nan | nan | +nan | 22; 13 / 9; p 0.523; +0.016; +0.06 | NO |

**Digit check: 0 / 2 printed values reproduced.** The paper's '24 of 33' is the 33 mf logs with a nonzero index out of 0 that turn at all (0 have an index of exactly 0).

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

- Trial: `off_ff_t3_sync-noise0.2` (specific lobe, chamber sync-noise0.2, start t3: 4.0 blocks, fly1 faces +1.00, fly2 +1.00); the bout is 15.85 s in fly2's log `fly2_off-flywire-noise0.2-known-eln0.25_20260927-085805.csv` (fly1 15.15 s, fly2 15.85 s = run length in ticks × 0.05 s; the paper prints the female maximum to one decimal).
- fly2's brain logged its first row -0.01 s (wall) after fly1's; fly1 had logged 0 rows by then (0.00 s of brain time) and moved 0.00 blocks (path 0.00) from its start, straight along its heading (fly1 faces fly2's start: +1.00); fly1 first sensed any fly +0.01 s from fly2's first row. Logged start distance 4.00 blocks; distance at fly2's placement (fly1 at its row 0 vs fly2's first position) **4.00 blocks**; fly2's first reading (row 0) 4.00 blocks.
- The bout began +315.44 s from fly2's first row (row 2220 of fly2's log; fly2's first contact at its row 21), so fly2 had been placed, but the flies were more than 1.3 blocks apart between placement and the bout (flag_placed = False, flag_plan = False): **a genuine meeting**. Longest bout of this trial that began after the flies had been > 1.3 apart post-placement: fly1 15.15 s, fly2 15.85 s.
- Longest female bout once the 0 flag_placed trials () are dropped: **15.85 s (`off_ff_t3_sync-noise0.2`, sync-noise0.2, fly2)** over every specific-lobe series; 15.85 s (`off_ff_t3_sync-noise0.2`, sync-noise0.2, fly2) in the series first reported; nan s (``, , ) in the replication. Once the 0 flag_plan trials are dropped: 15.85 s (`off_ff_t3_sync-noise0.2`, sync-noise0.2, fly2); first reported 15.85 s (`off_ff_t3_sync-noise0.2`, sync-noise0.2, fly2); replication nan s (``, , ).

### Flagged trials

| trial | series | cfg | stagger s | fly1 rows / moved before fly2 | dist at placement | fly2 first near_dist (row) | first contact (s after fly2) | longest fly1 / fly2 s | placed | plan |
|---|---|---|---|---|---|---|---|---|---|---|

Logged first positions match trials.sh (within 0.2 blocks of POS + 0.5) for 20 of 20 trials. A negative stagger means fly1's brain logged after fly2's (it loaded later; fly1's body stood still where it was placed), so fly1 had no rows before fly2.

Across all 20 trials: stagger -0.02–0.23 s (median 0.01); fly1 rows before fly2 0–1; fly1 displacement before fly2 0.00–0.00 blocks. Trials (all variants) with contact among those that start facing each other (t1, t3; fly1 faces > 0.9): 7 of 8 (7 not flag_placed); the other starts: 10 of 12 (10 not flag_placed).

Trials with contact by start configuration (specific lobe; `placed` = of them flag_placed):

| cfg | faces | ff: trials, with contact (placed) | mf: trials, with contact (placed) |
|---|---|---|---|
| t1 | +1.00 | 2, 2 (0) | 2, 2 (0) |
| t2 | -1.00 | 2, 2 (0) | 2, 2 (0) |
| t3 | +1.00 | 2, 2 (0) | 2, 1 (0) |
| t4 | -1.00 | 2, 2 (0) | 2, 1 (0) |
| t5 | +0.00 | 2, 2 (0) | 2, 1 (0) |

### Series numbers without the flagged trials (female logs, as replication_stats.py)

| series | pairing | excluded | trials with contact | contact, % of ticks (mean ± sd over logs) | longest bout, s | dropped trials |
|---|---|---|---|---|---|---|
| specific sync-clean | mf | none | 2 / 5 | 1.0 ± 1.7 | 2.10 | – |
| specific sync-clean | mf | placed | 2 / 5 | 1.0 ± 1.7 | 2.10 | – |
| specific sync-clean | mf | plan | 2 / 5 | 1.0 ± 1.7 | 2.10 | – |
| specific sync-noise0.2 | ff | none | 5 / 5 | 46.1 ± 27.4 | 15.85 | – |
| specific sync-noise0.2 | ff | placed | 5 / 5 | 46.1 ± 27.4 | 15.85 | – |
| specific sync-noise0.2 | ff | plan | 5 / 5 | 46.1 ± 27.4 | 15.85 | – |
| specific sync-noise0.2 | mf | none | 5 / 5 | 3.7 ± 2.7 | 6.20 | – |
| specific sync-noise0.2 | mf | placed | 5 / 5 | 3.7 ± 2.7 | 6.20 | – |
| specific sync-noise0.2 | mf | plan | 5 / 5 | 3.7 ± 2.7 | 6.20 | – |
| specific sync-noise0.2-notouch | ff | none | 5 / 5 | 5.6 ± 3.0 | 3.60 | – |
| specific sync-noise0.2-notouch | ff | placed | 5 / 5 | 5.6 ± 3.0 | 3.60 | – |
| specific sync-noise0.2-notouch | ff | plan | 5 / 5 | 5.6 ± 3.0 | 3.60 | – |

### fly1's turning before and after its partner appears

Mean `ctl_turn` and mean `hz_turn_L − hz_turn_R` (Hz) over fly1's rows up to fly2's first `t_wall` (before) and after; mean ± sd over trials. The published lobe turns left whatever is where (a partner-independent bias shows as equal before and after).

| series | pairing | fly1 | trials | turn before | turn after | DNa L−R before, Hz | DNa L−R after, Hz |
|---|---|---|---|---|---|---|---|
| specific sync-noise0.2 | ff | flywire | 5 | +0.000 ± 0.000 | -0.006 ± 0.005 | +0.00 ± 0.00 | -0.31 ± 0.19 |
| specific sync-noise0.2-notouch | ff | flywire | 5 | -0.141 ± 0.271 | -0.075 ± 0.004 | -6.00 ± 11.40 | -3.49 ± 0.17 |
| specific sync-noise0.2 | mf | malecns | 5 | -0.001 ± 0.037 | +0.029 ± 0.004 | +0.00 ± 0.00 | +0.17 ± 0.06 |
| specific sync-clean | mf | malecns | 5 | +0.000 ± 0.000 | +0.058 ± 0.003 | +0.00 ± 0.00 | +1.21 ± 0.65 |

## 2. Lean check (female logs, specific lobe, every series)

**Note: these tests pool 3 specific-lobe chamber(s) that replication_stats.py does not (sync-clean, sync-noise0.2, sync-noise0.2-notouch), so they are not the paper's 24/33 set; rerun with `--logs` pointing at the paper's logs only to test the paper's claim.**

Ticks: before the log's first contact, `near_dist < 6`, `near_az` present (the paper's). Per log: **idx_raw** = mean(turn · sign(az)) (the paper's); **idx_farcorr** = mean((turn − b_far) · sign(az)), b_far = the log's mean `ctl_turn` over non-contact ticks with `near_dist` >= 6 (logs without such ticks drop out); **idx_allcorr** = the same with b_all = the log's mean `ctl_turn` over all ticks; **side_contrast** = (mean turn with the partner on the left − on the right) / 2, logs with >= 10 ticks per side (immune to any constant bias); **idx_minus_bias_x_side** = idx_raw − mean(turn) · mean(sign(az)) (the within-log covariance). Only logs that turn at all enter. Sign tests: two-sided exact on > 0 vs < 0, Holm over mf/ff per index and level. Clusters: the mean index of the logs in a start configuration (`cfg`, t1–t5), a series, or a trial (`trial_id`; the two females of an ff trial), then a sign test over clusters.

| index | level | mf: n, towards / away (0), mean of the per-log (per-cluster) values, p, p Holm | ff: the same |
|---|---|---|---|
| idx_raw | log | 10, 7 / 3 (0), +0.0088, 0.344, 0.688 | 20, 9 / 11 (0), -0.0007, 0.824, 0.824 |
| idx_raw | cfg | 5, 4 / 1 (0), +0.0088, 0.375, 0.750 | 5, 2 / 3 (0), -0.0007, 1.000, 1.000 |
| idx_raw | series | 2, 2 / 0 (0), +0.0088, 0.500, 1.000 | 2, 1 / 1 (0), -0.0007, 1.000, 1.000 |
| idx_raw | trial_id | 10, 7 / 3 (0), +0.0088, 0.344, 0.688 | 10, 5 / 5 (0), -0.0007, 1.000, 1.000 |
| idx_farcorr | log | 10, 6 / 4 (0), +0.0091, 0.754, 1.000 | 20, 8 / 12 (0), -0.0080, 0.503, 1.000 |
| idx_farcorr | cfg | 5, 4 / 1 (0), +0.0091, 0.375, 0.750 | 5, 2 / 3 (0), -0.0080, 1.000, 1.000 |
| idx_farcorr | series | 2, 1 / 1 (0), +0.0091, 1.000, 1.000 | 2, 1 / 1 (0), -0.0080, 1.000, 1.000 |
| idx_farcorr | trial_id | 10, 6 / 4 (0), +0.0091, 0.754, 1.000 | 10, 4 / 6 (0), -0.0080, 0.754, 1.000 |
| idx_allcorr | log | 10, 6 / 4 (0), +0.0099, 0.754, 1.000 | 20, 8 / 12 (0), -0.0058, 0.503, 1.000 |
| idx_allcorr | cfg | 5, 4 / 1 (0), +0.0099, 0.375, 0.750 | 5, 2 / 3 (0), -0.0058, 1.000, 1.000 |
| idx_allcorr | series | 2, 2 / 0 (0), +0.0099, 0.500, 1.000 | 2, 1 / 1 (0), -0.0058, 1.000, 1.000 |
| idx_allcorr | trial_id | 10, 6 / 4 (0), +0.0099, 0.754, 1.000 | 10, 5 / 5 (0), -0.0058, 1.000, 1.000 |
| side_contrast | log | 6, 3 / 3 (0), -0.0028, 1.000, 1.000 | 9, 3 / 6 (0), -0.0072, 0.508, 1.000 |
| side_contrast | cfg | 4, 3 / 1 (0), +0.0008, 0.625, 1.000 | 3, 1 / 2 (0), -0.0045, 1.000, 1.000 |
| side_contrast | series | 2, 1 / 1 (0), -0.0042, 1.000, 1.000 | 2, 0 / 2 (0), -0.0077, 0.500, 1.000 |
| side_contrast | trial_id | 6, 3 / 3 (0), -0.0028, 1.000, 1.000 | 5, 2 / 3 (0), -0.0070, 1.000, 1.000 |
| idx_minus_bias_x_side | log | 10, 7 / 3 (0), +0.0059, 0.344, 0.344 | 20, 5 / 14 (1), -0.0106, 0.064, 0.127 |
| idx_minus_bias_x_side | cfg | 5, 4 / 1 (0), +0.0059, 0.375, 0.750 | 5, 1 / 4 (0), -0.0106, 0.375, 0.750 |
| idx_minus_bias_x_side | series | 2, 2 / 0 (0), +0.0059, 0.500, 1.000 | 2, 0 / 2 (0), -0.0106, 0.500, 1.000 |
| idx_minus_bias_x_side | trial_id | 10, 7 / 3 (0), +0.0059, 0.344, 0.688 | 10, 3 / 7 (0), -0.0106, 0.344, 0.688 |

Time-shift nulls (2000 shifts, `np.random.default_rng(0)` per pairing and kind; the same draws for all three indices): near_az is rolled circularly (within-pre: inside the pre-contact segment, offset uniform over 10–90 % of its length; whole-log: over the log, 10–90 % of its length) while the tick selection and the turn stay real. P = share of shifts whose net (towards − away) is >= the observed; P(mean) the same for the mean per-log index.

| pairing | index | null | n logs | observed net / mean | null net mean ± sd | P(net) | P(mean) |
|---|---|---|---|---|---|---|---|
| mf | idx_raw | within-pre | 10 | +4 / +0.0088 | +0.3 ± 2.8 | 0.1645 | 0.3675 |
| mf | idx_farcorr | within-pre | 10 | +2 / +0.0091 | +0.6 ± 2.6 | 0.4280 | 0.2580 |
| mf | idx_allcorr | within-pre | 10 | +2 / +0.0099 | +1.0 ± 2.6 | 0.5095 | 0.2670 |
| mf | idx_raw | whole-log | 10 | +4 / +0.0088 | +0.3 ± 3.0 | 0.1805 | 0.2530 |
| mf | idx_farcorr | whole-log | 10 | +2 / +0.0091 | -1.6 ± 2.9 | 0.1855 | 0.0480 |
| mf | idx_allcorr | whole-log | 10 | +2 / +0.0099 | -1.2 ± 3.0 | 0.2235 | 0.0605 |
| ff | idx_raw | within-pre | 20 | -2 / -0.0007 | +6.1 ± 2.7 | 1.0000 | 1.0000 |
| ff | idx_farcorr | within-pre | 20 | -4 / -0.0080 | +3.8 ± 2.8 | 1.0000 | 0.9995 |
| ff | idx_allcorr | within-pre | 20 | -4 / -0.0058 | +5.2 ± 2.8 | 1.0000 | 0.9985 |
| ff | idx_raw | whole-log | 20 | -2 / -0.0007 | +4.5 ± 3.7 | 0.9865 | 0.9665 |
| ff | idx_farcorr | whole-log | 20 | -4 / -0.0080 | +2.2 ± 3.8 | 0.9715 | 0.9195 |
| ff | idx_allcorr | whole-log | 20 | -4 / -0.0058 | +3.6 ± 3.8 | 0.9905 | 0.8320 |

Per-log lean against the sign of (mean turn × mean side) over the same ticks: a lean that only reflects a turning bias times the side the partner happened to sit on has sign(idx_raw) = sign(mean_turn_pre × mean_side_pre).

| pairing | logs (turn, both signs nonzero) | sign(idx) = sign(bias × side) | of the towards logs | of the away logs | logs with far ticks | smell L−R agrees with sign(az), mean share of ticks |
|---|---|---|---|---|---|---|
| mf | 10 | 3 | 2 / 7 | 1 / 3 | 10 / 10 | 0.992 |
| ff | 19 | 18 | 9 / 9 | 9 / 10 | 20 / 20 | 0.987 |

**S4 criterion (keep the lean only if the far-bias-corrected mf sign test leans towards with p < 0.025 under Holm over mf/ff (Holm-adjusted p < 0.05) and the within-pre-contact shift null P < 0.05):** far-corrected mf 6 / 4, p = 0.754, Holm p = 1.000; within-pre shift P(net) = 0.1645 → **CHANGE** (pools chambers outside the paper set: sync-clean, sync-noise0.2, sync-noise0.2-notouch).

## 3. Body speed and stalls

Per row: wall gap = Δ`t_wall`; displacement = |Δ(x, z)|; walk = the previous row's `ctl_walk` (the drive the body executed over the gap); only rows with walk > 0.2. Per log: share of rows with gap > 0.8 s (stalled if > 5%), brain time (short if < 60 s), displacement per unit walk = mean(displacement) / mean(walk).

| gap bin, s (all logs) | rows | mean gap | mean displacement | mean walk | displacement per unit walk |
|---|---|---|---|---|---|
| (0.0, 0.1] | 15380 | 0.088 | 0.042 | 0.565 | 0.075 |
| (0.1, 0.2] | 75623 | 0.137 | 0.060 | 0.555 | 0.108 |
| (0.2, 0.4] | 9621 | 0.241 | 0.086 | 0.593 | 0.145 |
| (0.4, 0.8] | 881 | 0.558 | 0.099 | 0.645 | 0.153 |
| (0.8, 1.6] | 476 | 1.088 | 0.146 | 0.666 | 0.219 |
| (1.6, 3.2] | 65 | 2.080 | 0.246 | 0.699 | 0.351 |
| (3.2, inf] | 8 | 3.656 | 0.189 | 0.562 | 0.337 |

| series | pairing | logs | brain s (mean) | brain / wall | median gap s | rows with gap > 0.8 s | stalled / short logs | displacement per unit walk | blocks per brain-s | comparable |
|---|---|---|---|---|---|---|---|---|---|---|
| specific sync-clean | mf | 10 | 139 | 0.46 | 0.104 | 0.0% | 0 / 0 | 0.189 | 0.613 | yes |
| specific sync-noise0.2 | ff | 10 | 222 | 0.37 | 0.127 | 0.1% | 0 / 0 | 0.064 | 0.551 | yes |
| specific sync-noise0.2 | mf | 10 | 208 | 0.35 | 0.136 | 0.0% | 0 / 0 | 0.167 | 1.138 | yes |
| specific sync-noise0.2-notouch | ff | 10 | 163 | 0.27 | 0.157 | 1.6% | 2 / 0 | 0.135 | 1.880 | yes |

A series is comparable when its pooled share of rows with a gap over 0.8 s is <= 5 % and its mean brain time >= 60 s (S4). Stalled logs: fly1_off-flywire-noise0.2-maskbristle-known-eln0.25_20260927-093039.csv, fly2_off-flywire-noise0.2-maskbristle-known-eln0.25_20260927-093039.csv. Short logs: none.
