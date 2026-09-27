
### [deciders] Note 5 (l.145): 'pC1a--e, aIPg, vpoDN and oviDN fire 0.0 Hz to every input and combination, at every gain up to 1.4 and in all 14 conditions'; main text l.95: the deciding neurons 'stay silent whatever the fly senses, in every version of the model'.
STEPS: gain-map-female (experiments/results_edge/gain-rate-map/map_gain.csv: 27 drives = none + all 26 social_probe inputs, gains 0.7 and 1.4, 3 seeds, 1000 ms, 162 rows); rate-map-female (gain-rate-map/map_rate.csv: 27 drives at 200 and 300 Hz, 3 seeds, 600 ms, 162 rows); sensmap-female (sensmap/sensmap_flywire.csv: 14 conditions x 36 drives incl. anchors x 3 seeds, 600 ms, 1512 rows); ei-deciders (ei-deciders/ei_deciders.csv: 5 drives x gains 1.0/1.4 x 3 seeds, 1000 ms). Gain 1.0 also from experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv (27 drives, 5 seeds; pooled groups only). Columns read: pC1a, pC1b, pC1c, pC1d, pC1e, 'aIPg aggr', vpoEN, 'vpoDN (DNp37)', oviDNa, oviDNb and the pooled 'pC1a recept', 'pC1b/c', 'pC1d/e aggr', 'vpoEN/DN accept', 'oviDN egg', each as '<name>' (group mean) and '<name> max1' (largest single neuron).
CRITERION: Fixed before the runs in design_plan.md. S11 (l.163-170): keep only if every decider, both mean and max1, is 0 for every drive at gains 0.7 and 1.4 and at 200 and 300 Hz; a decider responding at gain <= 1.4 or at 200 Hz makes the Note 5 sentence conditional. S10 (l.153-161): (1) the check-against file reports zero mismatches; (2) the six decider groups are 0.0 for every drive in all 14 conditions, and any non-zero cell must be named in Note 5. DECISIONS.md does not change these criteria.
NUMBERS: Values are max group mean / max single neuron in Hz, with n = rows.

All zero everywhere: pC1a, pC1b, pC1c, pC1e, vpoEN, vpoDN (DNp37), oviDNa and oviDNb are 0.00/0.00 in every set:
- gain 0.7: 81 rows
- gain 1.0: 108 sensmap-baseline rows, plus 15 E/I rows, plus 135 paper social_probe rows
- gain 1.4: 81 map rows plus 15 E/I rows
- 200 Hz: 81 rows; 300 Hz: 81 rows
- all 14 conditions: 1512 rows

The two exceptions:
- pC1d (2 neurons) at gain 1.4 (map_gain.csv), 6 of 81 gain-1.4 rows non-zero; overall max 3.50/4.00:
  - wind/gravity (JO-CE): 3.5 / 0.5 / 3.0 Hz by seed, so 2.33 +- 1.61 (mean +- sd, n=3); pooled 'pC1d/e aggr' 1.17 +- 0.80.
  - cVA-long (Or65a/DL3): 0.33 +- 0.29 (2 of 3 seeds).
  - aversive odour (DA2/DL4): 0.17 +- 0.29 (1 of 3 seeds).
- 'legacy numerics (first version)', 8 of its 108 rows non-zero; pC1d overall max 2.50/5.00 (600 ms, so 1 spike = 1.67 Hz):
  - pC1d: eye bristles 1.39 +- 0.96 (3/3 seeds); all head bristles 0.83 +- 1.44 (1/3); JO-CE 0.56 +- 0.96 (1/3); pheromones+song+touch 0.56 +- 0.48 (2/3); Or47b+touch 0.28 +- 0.48 (1/3).
  - pooled 'pC1d/e aggr' max 1.25/5.00.
  - 'aIPg aggr' 0.07/1.67: one spike in one of 23 neurons (Or47b+touch, seed 0).
  - The other 13 conditions are 0.00 in every decider column, mean and max1.

Per criterion:
- S11: passes at gain 0.7, 200 Hz and 300 Hz; fails at gain 1.4 (pC1d).
- S10.1: passes (sensmap_flywire.check.txt: 728 cells, 0 mismatches).
- S10.2: fails in 1 of 14 conditions (legacy numerics).

The brain is active in the same runs. At gain 1.4: touch -> DNp13 42.2 Hz and cVA -> DNa L/R 25/30 Hz. At 300 Hz: cVA+sugar -> MN9 108 Hz.

This resolves verify_wording_full.md 13a: pC1b/c and oviDN are now read at gains 0.7, 1.0 and 1.4, at 200/300 Hz and in all 14 conditions, not only at gain 1.0.
VERDICT REWORD
PAPER: l.95, replace the sentence with: "The neurons that decide whether a female accepts a male or attacks another female, and whether a male courts, stay silent, or nearly so, whatever the fly senses, in every version of the model." ("Nearly so" also covers the male P1 at gain 1.4, 2.1-2.3 Hz, verify_wording_full.md 13b.)
NOTES: Note 5, female part: "pC1a-c, pC1e, aIPg, vpoEN, vpoDN (DNp37) and oviDN fire 0.0 Hz, in every single neuron, to each of 26 inputs and combinations at gains 0.7, 1.0 and 1.4, at 200 and 300 Hz, and in all 14 conditions (3 seeds each). The exception is pC1d. At gain 1.4, wind on the antenna (JO-CE) makes it fire at 2.3 +- 1.6 Hz (3 seeds: 3.5, 0.5, 3.0 Hz), and two odours give it single spikes. Under the first-version numerics, touch and its combinations give it at most 2.5 Hz in single seeds (eye bristles 1.4 +- 1.0 Hz; at most 5 Hz in one neuron), and one aIPg neuron fires once."

### [deciders] Positive control: can the deciders fire at all when their own presynaptic partners are driven? If not, their silence to the senses would be an artefact of neurons the model cannot excite. Note 5 and l.95 do not say this; it underwrites them.
STEPS: decider-reach (experiments/results_edge/decider-reach/decider_reach.csv, 324 rows; decider_reach.json top5; logs/edge/guarded_decider-reach.out). For each decider type, its top-5 presynaptic cell types by summed positive W (own type and unlabelled neurons excluded) are driven, each alone and all five together, at 30 and 100 Hz; 3 seeds, 1000 ms. The target's own column is read, mean over the group and max1.
CRITERION: DECISIONS.md item 6 promoted this control to P1 ('can the deciders fire at all?') but set no numeric pass line. I scored it with the suite's 2 Hz presence line (design_plan S8): a decider counts as reachable if its group mean is >= 2 Hz with its top-5 types driven at 100 Hz.
NUMBERS: Group mean +- sd over 3 seeds (max single neuron), for top5 driven at 30 Hz / top5 at 100 Hz:
- pC1a: 30.0 +- 3.0 (36) / 68.5 +- 0.9 (76)
- pC1b: 42.2 +- 1.6 (45) / 93.3 +- 0.8 (97)
- pC1c: 52.3 +- 1.3 (64) / 105.3 +- 1.0 (119)
- pC1d: 47.0 +- 1.3 (49) / 103.5 +- 0.5 (105)
- pC1e: 20.2 +- 1.6 (27) / 64.2 +- 0.8 (76)
- aIPg (23 neurons): 2.7 +- 0.5 (21) / 23.4 +- 0.7 (64)
- vpoDN (DNp37): 49.2 +- 2.0 (61) / 103.2 +- 3.1 (120)
- vpoEN: 35.3 +- 1.0 (38) / 83.4 +- 0.7 (87)
- oviDN pooled (6): 5.2 +- 0.7 (24) / 19.5 +- 1.6 (53)
  - oviDNa (4): 7.8 / 29.3
  - oviDNb (2): 0.0 / 0.0 in every reach drive; no positive control for oviDNb.

Best single presynaptic type (at 30 / 100 Hz):
- pC1a: AN_SMP_2 25.2 +- 1.9 / 61.8 +- 2.9. AN_SMP_2 is the two SAG neurons (hemibrain_type SAG in data/Supplemental_file1_neuron_annotations.tsv) and carries 47.0 % of pC1a's excitatory input synapses (387 of 824).
- pC1b: AN_SMP_2 22.0 / 57.7
- pC1c: AN_SMP_2 22.2 / 56.3
- pC1d: SIP201f 34.0 at 100 Hz
- pC1e: AVLP297 19.0 at 100 Hz
- aIPg: pC1d 1.3 / 8.1
- DNp37: pC1a 23.5 / 62.3
- vpoEN: CB1484 16.5 / 57.3
- oviDN: SMP550 4.8 / 14.4 (oviDNa 21.6 at 100 Hz)

All 9 decider types pass the 2 Hz line at 100 Hz, and at 30 Hz as well (aIPg 2.7). The subtype oviDNb fails.

Engine check: the AN_SMP_2@30 rows equal state_probe_flywire_shiu_min1+known+eln0.25_state30.csv, SAG / input none, seeds 0-2, to the digit (total spikes 570/336/468; pC1a 26.5/23.0/26.0 Hz).
VERDICT KEEP
PAPER: No main-text change is needed. Optionally, after "stay silent, or nearly so, whatever the fly senses", add: "They can fire: driving their own inputs makes every one of them fire."
NOTES: Note 5, add: "Positive control: driving each decider's five strongest presynaptic cell types at 100 Hz makes it fire (3 seeds, 1 s): pC1a 69, pC1b 93, pC1c 105, pC1d 104, pC1e 64, aIPg 23, vpoEN 83, vpoDN 103 and oviDN 20 Hz (oviDNa 29 Hz; the two oviDNb stay at 0). pC1a's strongest input, 47 % of its excitatory synapses, comes from the two SAG neurons, which is why the virgin state wakes it and no sense does."

### [deciders] Why the deciders are silent. l.95: 'In the model the paths from those senses to the deciding neurons carry nothing'. Are they disconnected, far from threshold, or held down by inhibition?
STEPS: ei-deciders (experiments/results_edge/ei-deciders/ei_deciders_neurons.csv: 45 decider neurons x 5 drives (cVA, JO-A, touch, cVA+touch, pheromones+song+touch) x gains 1.0/1.4 x 3 seeds = 1350 rows). Columns: v_mean_mv and v_max_mv (voltage above rest; threshold is 7 mV above rest), frac_within_1mv, E_synhz and I_synhz (sum of W*presynaptic rate, synapse*Hz), dep_mv, n_pre_active, top3_pre. Structure: experiments/results_edge/structure/structure_flywire.md and structure_paths_flywire.csv, variant shiu_min1+known+eln0.25, columns hops, n_paths_le3, w_1..w_4, w_max, k_max, w_exc_3, route1.
CRITERION: DECISIONS.md items 6 and 11 (and design_critique.md item 2) asked for depolarisation below threshold, E and I input, and hops / signed propagated weight, but fixed no numeric pass line. My scoring: 'carry nothing' stands only if, for the named senses (pheromone, song, touch), decider E and I are near 0 and mean voltage moves by less than 1 mV (about 14 % of the 7 mV to threshold), and the structural paths are absent or far weaker than those of working reflexes.
NUMBERS: Mean voltage above rest, mean +- sd over neurons x 3 seeds, pk = peak; E / I in synapse*Hz. Gain 1.0 first, gain 1.4 in brackets.

- pC1d (2 neurons):
  - touch: +3.71 +- 0.06 mV, pk 5.28, E 4120 / I 1354 (1.4: +3.50, pk 6.44, E 5084 / I 3218).
  - cVA+touch: +3.72; pheromones+song+touch: +3.35 (1.4: pk 6.86 mV, within 1 mV of threshold 4.7 % of the time; closest approach 0.14 mV below threshold).
  - Main excitation: AVLP340 (+2900 to +3700). This is the same relay as the working touch -> DNp13 reflex.
  - cVA: -3.96 +- 0.54, E 508 / I 3490 (1.4: -10.10, I 6496), mainly AOTU064 (-1700 to -4600).
- pC1e: -3.6 to -4.9 mV under every drive except song (1.4: -10.7 to -14.2); inhibition is 8-18 x excitation (AVLP531, PS088, CB0584, CB0626).
- vpoEN (4 neurons):
  - touch and its combinations: -17.1 to -17.2 +- 1.8 mV, I 13,100-13,200 against E 370-380 (1.4: -31, I 17,000), mainly WED104 and PVLP021.
  - song: -0.04 mV, pk 1.2 (1.4: +0.22, pk 5.3).
- DNp37 (vpoDN): -0.18 to -0.41 mV (1.4: -0.54 to -0.90); I 158-369 > E 21-68.
- oviDN (6 neurons): -0.5 to -1.6 mV (1.4: -1.5 to -3.2); E 16-24 against I 415-1179, 15-74 x more inhibition than excitation (CB0584, oviIN).
- aIPg (23 neurons): about balanced, -0.93 to +0.12 mV (1.4: -0.8 to -2.3), pk 2.4 (1.4: 3.7).
- pC1c: +0.2 to +0.4 mV with touch (1.4, pheromones+song+touch: +2.1, pk 5.5); cVA -0.3 (1.4: -1.5).
- pC1a and pC1b receive almost nothing: E <= 68 at gain 1.0 and <= 281 at 1.4; |V| <= 0.3 mV at gain 1.0, <= 1 mV at 1.4; 1-16 active presynaptic partners of 205-377.
- Song (JO-A): moves pC1a-e by <= 0.05 mV (peaks <= 0.2 mV).
- cVA: mean voltage is below rest in all 9 decider types at both gains.
- Neuron-seed rows with I > E (excluding song), gain 1.0 / 1.4: DNp37, oviDN, pC1e and vpoEN 100 % / 100 %; pC1a 75 / 100; aIPg 55 / 86; pC1b 42 / 58; pC1c 25 / 50; pC1d 25 / 25.
- Firing threshold needs net E-I of 5091 synapse*Hz at gain 1.0 and 3636 at 1.4 (the mean-field formula used for dep_mv). Its check against measured voltage: r = 1.00, median |diff| 0.014 mV.

Structure (hops / paths within 3 steps / w_max with its k):
- cVA -> pC1a 2 / 5,170 / -5.5e-5; pC1b/c 2 / 53,744 / +1.4e-3; pC1d/e 2 / 33,633 / +1.7e-3 (k2, via M_lvPNm45); aIPg 3 / 42,469 / +3.3e-4; vpoEN/DN 3 / 15,494 / +9.4e-5; oviDN 3 / 15,935 / +1.6e-4.
- JO-A -> pC1a 3 / 885 / +1.8e-6; pC1b/c 2 / 10,370 / +7.1e-6; pC1d/e 2 / 43,674 / +7.4e-6; aIPg 2 / 86,461 / +3.1e-5; vpoEN/DN 1 (direct) / 211,800 / -6.7e-4; oviDN 3 / 3,344 / +2.5e-6.
- touch -> 2 hops to every decider (38,385 to 1,245,106 paths); w_max -1.1e-4, -5.1e-5, +2.2e-4, +1.5e-3, -4.1e-3, +8.7e-5 (same decider order).
- cVA+touch: -1.1e-4, +1.4e-3, +1.7e-3, +1.8e-3, -4.1e-3, +2.2e-4.
- pheromones+song+touch: 1-2 hops; -1.1e-4, +1.7e-3, +1.7e-3, +1.6e-3, -4.2e-3, +2.1e-4.
- Reference reflexes: touch -> DNp13 2 hops, +1.5e-3 (fires 36 Hz); sugar -> MN9 2 hops, +1.7e-3.
- 60 of 102 single sense -> decider pairs have net-negative w_max.
- The strongest positive pair (pheromone ORNs -> pC1d/e, +1.7e-3) is 1.16 x the weaker reference. In the spiking run, however, cVA hyperpolarises pC1d by 4 mV: the excitatory relay is not recruited and AOTU064 inhibition arrives instead.
- Some positive w is disinhibition (e.g. touch > CB0619 > AOTU064 > pC1d/e), which a silent relay cannot deliver.

Classification (mechanism):
- held down by inhibition: pC1e, oviDN, vpoEN (under touch), pC1d (under cVA), DNp37
- excited but below threshold: pC1d under touch (about half to 98 % of the way at peaks)
- functionally unreached: pC1a and pC1b (their main excitatory input is SAG), and every decider for song
- balanced: aIPg
VERDICT CHANGE
PAPER: l.95, replace "In the model the paths from those senses to the deciding neurons carry nothing, and I count this as the model's most important miss." with: "In the model those senses do reach the deciding neurons, within two or three connections, and the neurons can fire when their own inputs are driven. But song barely arrives, the male's pheromone pushes them further from firing, and touch lifts one pair only about halfway there. I count this as the model's most important miss."
NOTES: Note 5, add: "What reaches the deciders (1 s, 3 seeds; voltage above rest, where firing takes 7 mV):
- Touch drives pC1d through AVLP340, the relay of the touch -> DNp13 reflex, to +3.7 +- 0.1 mV (peak 5.3 mV; at gain 1.4 peak 6.9 mV, 0.14 mV short of firing).
- cVA pushes every decider below rest (pC1d -4.0 +- 0.5 and pC1e -4.0 +- 1.6 mV; -10 to -11 mV at gain 1.4), mainly through AOTU064 and CB0584.
- Touch holds vpoEN at -17 +- 2 mV (-31 mV at 1.4), with 13,000-17,000 synapse*Hz of inhibition against about 400 of excitation.
- pC1e and oviDN receive 8-74 times more inhibition than excitation under every drive.
- Song moves pC1a-e by less than 0.05 mV.
- pC1a and pC1b receive almost nothing (at most 280 synapse*Hz).
Every decider is 1-3 connections from every sense. 60 of 102 sense-decider pairs are net inhibitory. The strongest excitatory ones, pheromone neurons to pC1b/c and pC1d/e (1.4-1.7 x 10^-3 of their input), are as strong as touch -> DNp13 (1.5 x 10^-3) and sugar -> MN9 (1.7 x 10^-3), yet in the running model the cVA relay to pC1d/e stays silent and inhibition arrives instead."

RUN PROBLEMS [deciders]: No step failed. The runs look sound, but there are six things to know.

1. Check files: both reproduce the paper to the digit.
   - experiments/results_edge/ei-deciders/ei_deciders.check.txt: 405 cells compared at gain 1.0, 0 mismatches. The gain-1.4 rows are correctly listed as not comparable.
   - experiments/results_edge/sensmap/sensmap_flywire.check.txt: 728 cells over the 14 conditions, 0 mismatches.
   - The five step logs (logs/edge/guarded_{ei-deciders,decider-reach,gain-map-female,rate-map-female,sensmap-female}.out) show no errors, warnings or NaNs.
   - In ei_deciders_neurons.csv the only NaN values are in 'block' (all rows, expected) and 'top3_pre' (169 rows with no active presynaptic input, expected).

2. Three steps have no check file, by design: gain-map-female, rate-map-female and decider-reach. I ran substitute checks.
   - map_gain.csv cannot match experiments/results/gain_sweep_flywire_shiu_min1+known+eln0.25.csv to the digit, because the step read 1000 ms and the paper's gain_sweep.py reads 600 ms (default --ms 600). On the 12 shared inputs, seed 0-2 means agree within seed noise: touch -> DNp13 at 1.4 is 42.2 vs 42.2, sugar -> MN9 93.3 vs 94.7, JO-A -> GF 15.8 vs 16.3. Total spikes scale by 1.67 (= 1000/600) for steady drives, so gain is applied correctly.
   - At gain 1.4 the odour drives give a ratio of 1.70-1.82: activity is still building in the second half of the window. The gain-1.4 pC1d spikes may therefore depend on read length. JO-CE, the drive that makes pC1d fire, was never in the paper's gain sweep (its 13 inputs lack it).
   - decider_reach rows 'pC1a <- AN_SMP_2@30' equal the paper's state_probe SAG / none rows for seeds 0-2 to the digit.
   - In the E/I file, the mean-field dep_mv matches measured v_mean_mv with r = 1.00 (median |diff| 0.014 mV).

3. Directory names differ from step names. The task's gain-map-female and rate-map-female outputs are both in experiments/results_edge/gain-rate-map/ (map_gain.csv, map_rate.csv). sensmap-female wrote to experiments/results_edge/sensmap/. There are no gain-map-female, rate-map-female or sensmap-female directories.

4. Coverage gap: the E/I step did not include wind/gravity (JO-CE), the one drive that makes pC1d fire at gain 1.4. So there is no voltage or E/I record for the only firing case. The E/I drives follow DECISIONS item 6.

5. Outside the decider claims but in the same S11 step: its second criterion (sugar, bitter and touch give PAM and PPL1 at most 0.5 Hz) fails for bitter.
   - Bitter -> PPL1: 2.35 Hz at gain 1.4, 1.39 Hz at 200 Hz, 4.93 Hz at 300 Hz (3-seed means).
   - Sugar and touch stay at or below 0.02 Hz.
   - Whoever scores 'taste never reaches the teaching neurons' should see this.

6. decider_reach picks the top-5 presynaptic types pooled over all six oviDN. SMP550 dominates that list and targets oviDNa, so oviDNb (2 neurons) never fires in any reach drive and has no positive control.

>>> CHECK [deciders] Note 5 (l.145) / l.95: female deciders fire 0.0 Hz to every input at every gain up to 1.4 and in all 14 conditions; 'silent whatever the fly senses, in every version of the model'. Analyst verdict REWORD.: agrees=True
OWN: Pre-set criteria (design_plan.md). S11: every decider, mean and max1, must be 0 at gain 0.7/1.4 and 200/300 Hz; a response at gain <=1.4 makes the sentence conditional. S10: the check file must show 0 mismatches, and any non-zero decider cell must be named. REWORD is exactly the pre-set outcome.

Files and runs:
- Files: map_gain.csv (162 rows), map_rate.csv (162), sensmap_flywire.csv (1512 = 14 labels x 36 drives x 3 seeds), ei_deciders.csv (30), the paper's social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv (135, pooled groups).
- Settings: noise 0, variant shiu_min1+known+eln0.25.
- Engine check: sensmap_flywire.check.txt 728 cells, 0 mismatches; ei_deciders.check.txt 405 cells, 0 mismatches.
- map_gain and map_rate have no check file. I tried the paper's gain_sweep, but it runs 600 ms against the map's 1000 ms, so they cannot be compared to the digit.
- The runs are not broken: 'none' gives 0 spikes. At gain 1.4, touch -> DNp13 42.2 Hz and cVA -> DNa L/R 25.2/30.0; at 300 Hz, cVA+sugar -> MN9 107.8; JO-A -> GF 16.3 (gain 1.4) and 28.1 (300 Hz).

Non-zero cells (all decider columns, mean and max1):
- Only pC1d, the pooled 'pC1d/e aggr' and, once, aIPg.
- Gain 1.4: 6 of 81 rows.
  - JO-CE 3.5 / 0.5 / 3.0 Hz by seed = 2.33 +- 1.61 (n=3); max1 4.0; aggr 1.17 +- 0.80.
  - cVA-long 0.33 +- 0.29; aversive 0.17 +- 0.29 (single spikes).
- Legacy numerics: 8 of 108 rows.
  - pC1d: eye bristles [2.5, 0.83, 0.83] = 1.39 +- 0.96; all bristles 0.83 +- 1.44; JO-CE 0.56 +- 0.96; pheromones+song+touch 0.56 +- 0.48; Or47b+touch 0.28 +- 0.48; max1 5.0.
  - aIPg: 0.072 (max1 1.67 = 1 spike, 1 of 23 neurons, Or47b+touch, seed 0).
- Gain 0.7, 200 Hz, 300 Hz, the E/I rows and the other 13 conditions: all 0.
- All analyst numbers reproduce.

Evidence the analyst did not use:
1. anchors_gain.csv, Shiu JON-CE@100 (69 neurons against the paper's 484-neuron JO-CE set), 10 seeds: pC1d is 0.0 at gains 0.7/0.8/0.9/1.0/1.2. At 1.4 it is 0.45 +- 0.50 Hz (6 of 10 seeds non-zero, max1 3.0). So the pC1d response is a gain-1.4 effect, and it is smaller with a smaller JO-CE set.
2. More all-zero runs: touch_dose.csv (275 rows, touch 10-300 Hz and subsets); touch_5s.csv; minsyn.csv (520 rows, 8 min-syn variants); anchors_rate.csv (100); the sensory drives in persistence_g1.csv (10 s).
3. The hum (state-hum, noise 0.2 Hz, 10 seeds, state 'none'):
   - Every pooled decider sits at a 0.05-0.45 Hz floor, and no input raises it (pC1d/e aggr: none 0.25 +- 0.17, touch 0.38 +- 0.27, cVA 0.12 +- 0.18).
   - So '0.0 Hz' is true only without the hum.
4. At gain 1.4, pC1d's 3.5 and 3.0 Hz exceed the suite's 2 Hz presence line in 2 of 3 seeds, so 'nearly so' is a little soft.
CORRECTED: l.95: the analyst's text is acceptable: "...stay silent, or nearly so, whatever the fly senses, in every version of the model."

Note 5, female part, replacing the analyst's version:
"pC1a-c, pC1e, vpoEN, vpoDN (DNp37) and oviDN fire 0.0 Hz, in every single neuron, to each of 26 inputs and combinations at gains 0.7, 1.0 and 1.4, at 200 and 300 Hz, and in all 14 conditions (3 seeds each), and also to touch at 10-300 Hz. pC1d fires only at the extremes. At gain 1.4, wind on the antenna (JO-CE) drives it at 2.3 +- 1.6 Hz (3 seeds: 3.5, 0.5, 3.0 Hz). With Shiu et al.'s 69 JO-CE neurons it fires at 0.45 +- 0.50 Hz (10 seeds), and at 0 at every gain up to 1.2. Two odours give it single spikes. Under the first-version numerics, touch, its combinations and wind give it at most 2.5 Hz in single seeds (eye bristles 1.4 +- 1.0 Hz; at most 5 Hz in one neuron), and one of the 23 aIPg neurons fires once. On the hum every decider stays at its 0.1-0.5 Hz floor whatever the input (10 seeds)."

This fixes three problems in the analyst's version:
- It left out wind under legacy numerics.
- It listed aIPg as 0.0 'in all 14 conditions' and then excepted it.
- It left out the hum.

>>> CHECK [deciders] Positive control (decider-reach): the deciders can fire when their top-5 presynaptic types are driven. Analyst verdict KEEP (Note 5 addition).: agrees=True
OWN: Criterion: DECISIONS.md item 6 set no numeric line. The analyst's 2 Hz presence line (from S8) is a reasonable choice.

File: decider_reach.csv (324 rows = 9 blocks x 12 drives x 3 seeds, gain 1.0, 1000 ms); target columns as named.

All reproduced. Top5, 30 / 100 Hz, mean +- sd (n=3), with max1:
- pC1a 30.0 +- 3.0 (36) / 68.5 +- 0.9 (76)
- pC1b 42.2 +- 1.6 / 93.3 +- 0.8
- pC1c 52.3 +- 1.3 / 105.3 +- 1.0
- pC1d 47.0 +- 1.3 / 103.5 +- 0.5
- pC1e 20.2 +- 1.6 / 64.2 +- 0.8
- aIPg 2.7 +- 0.5 (21) / 23.4 +- 0.7 (64)
- DNp37 49.2 +- 2.0 / 103.2 +- 3.1
- vpoEN 35.2 +- 1.0 / 83.4 +- 0.7
- 'oviDN egg' 5.2 +- 0.7 / 19.5 +- 1.6; oviDNa 7.8 / 29.2; oviDNb 0.0 in all 36 oviDN-block rows

Presynaptic share (decider_reach.json and the log): AN_SMP_2 is 387 of 824 = 47.0 % of pC1a's excitatory synapses. The annotation TSV lists both AN_SMP_2 neurons as hemibrain_type SAG, top_nt serotonin, modelled with + sign.

Engine check: pC1a <- AN_SMP_2@30 against state_probe ..._state30.csv (SAG, input none, seeds 0-2): 69 cells, 0 mismatches (total spikes 570/336/468; pC1a 26.5/23.0/26.0).

SAG itself fires 0.0 Hz to every sensory drive in social_probe (gain 1.0), map_gain, map_rate and all 14 sensmap conditions. That supports the analyst's causal clause, but only when it is stated as this observation.

Caveats:
- aIPg's top two inputs are other deciders (pC1d 14.8 %, pC1e 5.1 %). Its control works mainly through pC1d (8.1 +- 1.2 Hz from pC1d@100 alone), and at 30 Hz it is only 2.7 Hz, barely over the line.
- Other deciders are also among the top-5 inputs: pC1a for pC1b, pC1c and DNp37; vpoEN and pC1c for DNp37.
- AN_SMP_1 (in pC1a's top 5) is mixed sign (1+/4-).
- oviDNb has no positive control, because the top 5 were chosen for the pooled oviDN group and SMP550 reaches only oviDNa.
- The optional main-text line 'makes every one of them fire' is therefore slightly too strong.
CORRECTED: Main text, optional: "They can fire: driving their own inputs makes each of them fire." The single oviDNb exception belongs in the Note.

Note 5, add: "Positive control: driving each decider's five strongest presynaptic cell types at 100 Hz makes it fire (3 seeds, 1 s): pC1a 69, pC1b 93, pC1c 105, pC1d 104, pC1e 64, aIPg 23 (mostly through pC1d), vpoEN 83, vpoDN 103 and oviDN 20 Hz. oviDNa fires at 29 Hz. The two oviDNb stay at 0, because their inputs were not among the five, so they have no positive control. pC1a's strongest input, 47 % of its excitatory synapses, comes from the two SAG neurons. SAG fires 0.0 Hz to every sensory input in every map, and the virgin state drives it directly."

>>> CHECK [deciders] l.95 'the paths from those senses to the deciding neurons carry nothing' is wrong: the senses reach the deciders but mostly inhibit them or leave them below threshold. Analyst verdict CHANGE.: agrees=True
OWN: Criterion: DECISIONS items 6 and 11 set no numeric line. Under the analyst's 1 mV / near-zero E and I rule, 'carry nothing' fails clearly. Several drives move a decider by far more than 1 mV (pC1d under touch, all deciders under cVA, vpoEN under touch, pC1e), so CHANGE is right.

File: ei_deciders_neurons.csv (1350 rows = 45 neurons x 5 drives x 2 gains x 3 seeds). rate_hz is 0 in every row. dep_mv against v_mean_mv: r = 0.99999, median |diff| 0.014 mV (max 1.06). The firing threshold needs E - I = 7/(0.275*gain*5 ms) = 5091 synapse*Hz at gain 1.0 and 3636 at 1.4.

Reproduced, gain 1.0 (gain 1.4 in brackets):
- pC1d:
  - touch +3.71 +- 0.06 mV, peak 5.28, E 4120 / I 1354 (+3.50, peak 6.44).
  - pheromones+song+touch at 1.4: peak 6.86 mV, 0.14 short of threshold. Time within 1 mV is at most 4.7 % in one neuron-seed; the mean is 1.6 %.
  - Main excitation AVLP340 +2924 to +3700, which is route 1 of touch -> DNp13 (AN_AVLP_GNG_18 > AVLP340).
  - cVA -3.96 +- 0.54, E 508 / I 3490 (-10.10), AOTU064 -1664 to -4625.
- pC1e: -3.55 to -4.88 (-10.7 to -14.2); I/E 8.4-18.1. Under cVA the inhibition comes from AVLP531, CB0584 and PS088, not AOTU064.
- vpoEN under touch: -17.2 +- 1.8 (-31.1), I 13,214 / E 380; mainly WED104 and PVLP021.
- DNp37: -0.18 to -0.41, I 158-369 against E 21-68.
- Pooled oviDN: -0.52 to -1.56 (-1.5 to -3.2), E 16-24 against I 415-1179 (I/E 17-74; 15-41 at 1.4); mainly CB0584.
- aIPg: -0.93 to +0.12.
- pC1a/pC1b: mean E at most 68 (281 at 1.4).
- cVA: mean voltage below rest in all 10 subgroups at both gains, but pC1a/b/DNp37 move by only 0.1-0.2 mV.
- Share of rows with I > E: as the analyst gives.

Structure (structure_paths_flywire.csv, variant known+eln0.25):
- All hops, path counts and w_max values reproduce, and 60 of 102 single sense-decider pairs are net-negative.
- Pheromone ORNs -> pC1d/e: 1.725e-3 (k2, via M_lvPNm45). That is 1.16 x touch -> DNp13 (1.483e-3); sugar -> MN9 is 1.739e-3.

Errors and omissions:
1. Song does reach vpoEN, the decider reported to answer song in real females. JO-A -> vpoEN/DN is a direct connection (1 hop; JO-A4 +78-82 in the top 3), with excitation via CB1908 and CB0264 and inhibition via CB2364 and CB3911.
   - Gain 1.0: E 98 against I 129, mean -0.04 mV, peak 1.2.
   - Gain 1.4: E 388 > I 278, mean +0.22, peaks 2.7-5.3 mV in all 12 neuron-seeds.
   - So 'every decider unreached for song' is wrong for vpoEN; 'song barely arrives' holds at gain 1.0.
2. Touch -> aIPg (+1.45e-3, disinhibition via CB0619 > AOTU064) is in the same range as the pheromone -> pC1 pairs. w_k for k >= 2 is a propagated normalised weight, not a fraction of the neuron's input.
3. 'The cVA relay stays silent' was not measured. pC1d's total excitation under cVA is only 463-534 synapse*Hz, about a tenth of what firing needs, and M_lvPNm45 is not in the top 3, so it contributes at most about 300.
4. pC1e and oviDN get no input from song (E = I = 0), so 'every drive' must exclude song.
5. JO-A -> vpoEN is 1 hop, so the paths are 'one to three connections', not 'two or three'.
6. -17 to -31 mV below rest (-69 to -83 mV absolute) is possible only because the model's synapses are current-based, with no reversal potential. Better to quote I/E ratios, or add this caveat.
CORRECTED: l.95: "In the model those senses do reach the deciding neurons, within one to three connections, and the neurons can fire when their own inputs are driven. But song barely arrives, the male's pheromone pushes them further from firing, and touch lifts one pair only about halfway there. I count this as the model's most important miss."

Note 5, add: "What reaches the deciders (1 s, 3 seeds; voltage above rest, where firing takes 7 mV):
- Touch drives pC1d through AVLP340, the relay of the touch -> DNp13 reflex, to +3.7 +- 0.1 mV (peak 5.3 mV). At gain 1.4 the peak is 6.9 mV, 0.14 mV short of firing.
- cVA pushes every decider below rest: pC1d -4.0 +- 0.5 mV (mainly through AOTU064) and pC1e -4.0 +- 1.6 mV (through AVLP531, PS088 and CB0584). At gain 1.4 both reach -10 to -11 mV.
- Touch holds vpoEN at -17 +- 2 mV, with about 13,000 synapse*Hz of inhibition against 400 of excitation. (The model's synapses have no reversal potential, so these depths are upper bounds.)
- pC1e and oviDN receive 8-74 times more inhibition than excitation under every input except song, which reaches neither.
- Song moves pC1a-e by less than 0.05 mV. It reaches vpoEN through a direct connection, but inhibition nearly cancels it: peak 1.2 mV, and 5.3 mV at gain 1.4.
- pC1a and pC1b receive almost no excitation (at most 280 synapse*Hz).
Every decider is one to three connections from every sense, and 60 of 102 sense-decider pairs are net inhibitory. The strongest excitatory pairs have propagated weights of 1.4-1.7 x 10^-3, as large as touch -> DNp13 (1.5 x 10^-3) and sugar -> MN9 (1.7 x 10^-3): pheromone neurons to pC1b/c and pC1d/e, and touch to aIPg (through two inhibitory neurons). Yet in the running model, cVA gives pC1d only about 500 synapse*Hz of excitation, a tenth of what firing needs, and inhibition arrives instead."

### [reflexes] Engine correctness (S10 item 1): the edge engine reproduces the paper's sensitivity file at every one of the 14 female conditions
STEPS: sensmap-female (experiments/results_edge/sensmap/sensmap_flywire.csv, .check.txt, .json); cross-check against freeze-minsyn/minsyn.csv
CRITERION: S10.1: check-against experiments/results/sensitivity_flywire_shiu_min1+known+eln0.25.csv reports zero mismatches.
NUMBERS: sensmap_flywire.check.txt: 14 conditions x 52 cells = 728 cells, 0 mismatches, 0 missing (tolerance 1e-9). The JSON sidecar and log agree (410 s run, 1512 rows = 14 conditions x 36 drives x 3 seeds). As an extra check, seeds 0-2 of freeze-minsyn/minsyn.csv (shiu and zenodo at min_syn_mem 1 and 5) are bit-identical to sensmap conditions 0, 11, 12 and 13 on every readout for none, food, food+touch, cVA, cVA+touch and touch. So the in-memory k=5 threshold equals the min5 cache. No NaN or negative readouts, the 'none' drive gives 0 spikes, and there are no duplicate rows. The check covers only the paper table's 52 cells per condition, not the new columns (anchors, JO-A, aBN1, deciders).
VERDICT KEEP
PAPER: (no change)
NOTES: The edge-case engine reproduced all 728 cells of the 14-condition female sensitivity table to the digit (seeds 0-2, 6 threads).

### [reflexes] Sugar -> MN9 passes the third test (all 14 female conditions) and holds at gains 0.7-1.4 and at 200-300 Hz
STEPS: sensmap-female; gain-map-female (map_gain.csv); rate-map-female (map_rate.csv)
CRITERION: No numeric item of its own in S10/S11. It is judged against the paper's Note 4 (33/76/94 Hz) and the implicit requirement that MN9 is driven in every condition, gain and rate.
NUMBERS: Drive 'sugar GRNs' (129 neurons), column 'MN9' (Shiu's MN9), mean +- sd, n=3 seeds (0-2). sensmap (600 ms): baseline 77.2+-6.3; 50 Hz 63.9+-15.1; 150 Hz 92.8+-10.0; dt 0.1 87.8+-3.5; dt 0.5 86.1+-1.0; legacy 371.1+-2.5; published 80.6+-1.0; >=5 syn 92.2+-3.5; Zenodo >=5 95.0+-3.3; Zenodo all 79.4+-9.6 (the eLN-only rows 2/4/5 are bit-identical to baseline, and row 3 to row 1). The range is 63.9-95.0 Hz in 13 of 14 conditions, and 371 under legacy numerics. Shiu's 29 sugar neurons ('Shiu sugar@100') give 46.7-58.9 Hz (legacy 200). map_gain.csv (1000 ms): gain 0.7 38.0+-2.6, gain 1.4 94.7+-4.2 (paper gain_sweep, 600 ms, 5 seeds: 32.7 / 94.3). map_rate.csv (600 ms): 200 Hz 98.9+-9.2, 300 Hz 112.8+-8.6. Sugar gives PAM = PPL1 = 0.00 in every condition, gain and rate.
VERDICT KEEP
PAPER: (no change) Sugar makes it work its mouthparts.
NOTES: Sugar -> MN9 33 / 76 / 94 Hz at gain 0.7 / 1.0 / 1.4; 99 +- 9 and 113 +- 9 Hz at 200 and 300 Hz; 64-95 Hz in 13 of the 14 conditions (371 Hz under the legacy numerics) (n = 3).

### [reflexes] Bitter suppression of sugar -> MN9 passes the third test (all 14 conditions) and holds at gains 0.7-1.4 and at 200-300 Hz
STEPS: sensmap-female (the --anchors drives). gain-map-female and rate-map-female have no anchors.
CRITERION: S10.5: with bitter at 100 Hz, MN9 stays below 25 % of sugar alone in every condition. S12 adds a monotone dose over bitter 25/50/100 at every gain. S11: bitter is not tested there.
NUMBERS: sensmap, column 'MN9', drives 'Shiu sugar@100' and 'Shiu sugar@100 & Shiu bitter@{25,50,100}', n=3, 600 ms. With-bitter / sugar-alone (ratio): baseline 2.78+-2.55 / 55.56+-1.92 (0.050); published 7.78+-5.85 / 58.89+-5.36 (0.132); dt 0.1 4.44 / 50.56 (0.088); dt 0.5 2.22 / 55.00 (0.040); legacy 5.56 / 200.0 (0.028); >=5 syn 5.00 / 47.78 (0.105); Zenodo >=5 5.56 / 46.67 (0.119); Zenodo all 3.33 / 52.78 (0.063). Every ratio is 0.03-0.13 (criterion < 0.25), and the dose is monotone in all 14 conditions (baseline 55.6 -> 36.7 -> 22.2 -> 2.8). Coverage: the anchor terms are hard-coded @100, so the 50 Hz and 150 Hz rows are bit-identical to baseline. The anchors give 8 distinct outcomes over the 14 conditions (0=2=4=5=6=7, 1=3). Bitter was never run at another stimulus rate. The gain and rate maps contain no sugar+bitter drive, so gains 0.7/1.4 and 200/300 Hz are unmeasured. S12 anchors-gain was running at 05:09. anchors_rate has no bitter drive.
VERDICT REWORD
PAPER: Main text unchanged ('bitter makes it stop'). Note 4, after '3.3 Hz with bitter added': 'and 3-13 % of sugar alone in every condition of the sensitivity table in which it was run, falling steadily with bitter at 25, 50 and 100 Hz; I did not vary its stimulus rate, and its gain test is in Note 2.' (Replace the gain clause with the S12 result when anchors-gain finishes.)
NOTES: Bitter at 100 Hz on Shiu et al.'s 29 sugar neurons: MN9 55.6 +- 1.9 -> 2.8 +- 2.5 Hz at baseline (n = 3, 600 ms). Across the sign, smell-centre, time-step, numerics, threshold and table conditions, MN9 with bitter is 2.2-7.8 Hz against 46.7-58.9 Hz alone (5.6 against 200 under the legacy numerics), a ratio of 0.03-0.13. The dose is monotone over 25/50/100 Hz in every condition. Not run at 50/150/200/300 Hz or at gains 0.7/1.4 in these steps.

### [reflexes] Sound (JO-A) -> giant fibre passes the third test (all 14 conditions) and holds at gains 0.7-1.4 and at 200-300 Hz
STEPS: sensmap-female; gain-map-female; rate-map-female
CRITERION: S10.4: JO-A -> GF is at least 5 Hz at 50 Hz, at 150 Hz and at >=5 synapses, and at least twice the largest odour -> GF.
NUMBERS: Drive 'song/sound (JO-A)' (99 neurons, at each condition's rate), column 'GF jump', n=3. sensmap: baseline 9.72+-0.48; 50 Hz 1.11+-1.27 (seeds 0.83 / 2.50 / 0.00; max1 1.7 / 5.0 / 0) FAIL; 150 Hz 17.50+-0.83; dt 0.1 11.39+-0.48; dt 0.5 11.94+-1.73; legacy 16.39+-0.96; published and every eLN row 9.72; >=5 syn 10.28+-0.48; Zenodo >=5 10.28; Zenodo all 10.00+-1.44. So it is >=5 Hz in 13 of 14 conditions (9.7-17.5 Hz). Largest odour -> GF (over the 9 odour drives): baseline Or88a 5.00+-1.44 (ratio 1.94, just under 2x); 50 Hz food 3.33 (JO-A is below it, ratio 0.33); 150 Hz Or88a 5.28 (3.3x); >=5 syn Or88a 3.61 (2.85x); Zenodo >=5 0. Odours reach GF at 0-5.6 Hz across the 14 conditions. map_gain (1000 ms): gain 0.7 5.83+-0.29 (lowest seed 5.5), gain 1.4 16.33+-1.15; largest odour 0 / 5.67 (Or47b). map_rate: 200 Hz 23.06+-0.96, 300 Hz 28.06+-1.27; largest odour 4.72 / 5.56 (Or88a). JO-B -> GF for comparison: 0.28 at 50 Hz and 0.83 at >=5 syn.
VERDICT REWORD
PAPER: Main text: 'A loud sound fires its escape jump.' Note 4: 'Sound (JO-A) -> giant fibre 6 / 11 / 16 Hz, 23 and 28 Hz at 200 and 300 Hz, and 10-18 Hz in 13 of the 14 conditions; at a 50 Hz stimulus it falls to 1 Hz. Smells reach the giant fibre at up to 5 Hz.'
NOTES: JO-A -> GF (n = 3): 9.7 +- 0.5 Hz at baseline; 9.7-17.5 Hz in 13 of 14 conditions (>=5 synapses 10.3 +- 0.5; 150 Hz 17.5 +- 0.8); 1.1 +- 1.3 Hz at a 50 Hz stimulus. Gain 0.7 / 1.4: 5.8 +- 0.3 / 16.3 +- 1.2 Hz; 200 / 300 Hz: 23.1 +- 1.0 / 28.1 +- 1.3 Hz. The strongest odour -> GF is 5.0 +- 1.4 Hz (Or88a) at baseline, so sound leads smell there by only 1.9x.

### [reflexes] Wind (JO-CE) -> grooming neuron aBN1, with JO-F not driving it, passes the third test (all 14 conditions) and holds at gains 0.7-1.4 and at 200-300 Hz
STEPS: sensmap-female (anchors 'Shiu JON-CE@100', 'Shiu JON-F@100', and the 'wind/gravity (JO-CE)' drive); gain-map-female and rate-map-female ('wind/gravity (JO-CE)' only)
CRITERION: S10.5: aBN1 from JON-CE is at least 5 Hz with JON-F below a third of it, in every condition. The S12 gain and rate part is pending.
NUMBERS: Column 'aBN1' (root id 720575940630907434), n=3. Shiu JON-CE@100 (69 neurons): baseline 12.2+-4.2 (8.3 / 11.7 / 16.7); published 11.7+-2.9; dt 0.1 11.1+-2.5; dt 0.5 15.0+-2.9; legacy 17.2+-5.1; Zenodo all 12.2+-2.5; >=5 syn 0.56+-0.96 (0 / 0 / 1.7) and Zenodo >=5 0.56+-0.96 FAIL. Shiu JON-F@100 (60 neurons): 0 in 11 conditions, 0.56 legacy, and 3.89+-1.92 (5.0 / 1.7 / 5.0) in both >=5 tables. So selectivity reverses there: JO-F > JO-CE. Pass in 12 of 14 anchor conditions. The 50/150 Hz anchor rows are copies of baseline (pinned @100). The whole JO-C/E group ('wind/gravity (JO-CE)', 484 neurons, at each condition's rate): baseline 25.6+-1.0; 50 Hz 0.56+-0.96 FAIL; 150 Hz 50.0+-0.0; >=5 syn 3.33+-2.89; Zenodo >=5 2.78+-2.55. map_gain: gain 0.7 9.0+-1.0, gain 1.4 44.3+-2.1. map_rate: 200 Hz 61.7+-1.7, 300 Hz 75.0+-1.7. JO-F was not run in the gain or rate maps.
VERDICT CHANGE
PAPER: Main text: 'Wind on the antenna makes it groom, though not when the wind is weak, and not once the weakest connections are removed (then the grooming neuron answers the wrong antennal neurons).' If the freeze sentence is kept, it can also say: 'The same threshold also costs the grooming reflex.' Note 4: 'Wind (JO-CE, Shiu et al.'s 69 neurons) -> the grooming neuron aBN1 12 Hz, and 11-17 Hz in 12 of the 14 conditions, with JO-F at 0-0.6 Hz; under the >=5-synapse threshold, in both tables, JO-CE gives 0.6 Hz and JO-F 3.9 Hz. The whole JO-C/E group gives 9 / 26 / 44 Hz at gain 0.7 / 1.0 / 1.4 and 62 and 75 Hz at 200 and 300 Hz, but 0.6 Hz at a 50 Hz stimulus.'
NOTES: JON-CE -> aBN1 12.2 +- 4.2 Hz, JON-F 0.0 (n = 3, 600 ms, baseline). The ratio holds in 12 of 14 conditions (JON-CE 11.1-17.2 Hz, JON-F <= 0.6). At >=5 synapses (Shiu and Zenodo tables): JON-CE 0.6 +- 1.0, JON-F 3.9 +- 1.9 Hz. Whole JO-C/E group -> aBN1: 0.6 +- 1.0 Hz at 50 Hz, 25.6 +- 1.0 at 100, 50.0 at 150, 61.7 +- 1.7 at 200, 75.0 +- 1.7 at 300; 9.0 +- 1.0 / 44.3 +- 2.1 Hz at gain 0.7 / 1.4 (1000 ms). JO-F was not run at other gains or rates.

### [reflexes] Head touch -> DNp13 (ovipositor) passes the third test (all 14 conditions) and holds at gains 0.7-1.4 and at 200-300 Hz
STEPS: sensmap-female; gain-map-female; rate-map-female
CRITERION: No numeric S10/S11 item of its own. It is judged against Note 4: 28 / 35 / 42 Hz, and 28-51 Hz in all 14 conditions.
NUMBERS: Drive 'touch (all head bristles)' (1,417 neurons), column 'DNp13 reject', n=3. sensmap: baseline 35.8+-0.8; 50 Hz 27.8+-1.3; 150 Hz 38.9+-0.5; dt 0.1 37.2+-1.0; dt 0.5 38.6+-1.3; legacy 50.8+-1.4; published 36.4+-1.3; >=5 syn 27.8+-2.1; Zenodo >=5 28.1+-2.1; Zenodo all 35.3+-1.0. Range 27.8-50.8 Hz, and these cells matched the paper file to the digit. map_gain (1000 ms): 28.7+-1.5 at 0.7, 42.2+-0.8 at 1.4. map_rate: 36.7+-0.8 at 200 Hz, 32.8+-2.7 at 300 Hz (a slight fall from 200 to 300). Touch -> PAM/PPL1 is 0 at gain 1 in 13 of 14 conditions and <= 0.06 Hz at gain 1.4.
VERDICT KEEP
PAPER: (no change) When a female's head is touched she extends her ovipositor.
NOTES: Head bristles -> DNp13 28 / 35 / 42 Hz at gain 0.7 / 1.0 / 1.4 (28-51 in all 14 conditions); 37 +- 1 and 33 +- 3 Hz at 200 and 300 Hz (n = 3).

### [reflexes] The freeze (index = 1 - DNa(food+touch)/DNa(food), and the same with cVA) passes the third test in every condition where DNa alone reaches 2 Hz, and holds at gains 0.7-1.4 and at 200-300 Hz; it reverses only under the >=5-synapse threshold
STEPS: sensmap-female; gain-map-female; rate-map-female (supporting check: freeze-minsyn/minsyn.csv)
CRITERION: S10.3: the freeze index is at least 0.35 in every condition where DNa alone reaches 2 Hz, including 50/150 Hz, dt 0.1/0.5, legacy numerics and the Shiu table at >=5 synapses.
NUMBERS: Index from the DNa L+R sums over seeds, as in contact_stop.py (touch at the drive's rate, 600 ms, n=3). Columns 'DNa L' and 'DNa R'; drives 'food odor' / 'food + touch' and 'cVA (Or67d/DA1)' / 'cVA + touch'. Food (DNa alone mean -> index, per-seed mean+-sd): baseline 17.1 -> 0.715 (0.71+-0.07); 50 Hz 0.523; 150 Hz 0.688; dt 0.1 0.737; dt 0.5 0.669; legacy 0.979; published 0.500; known x1 0.593; Shiu x0.25 0.526; eLN 0.5 0.500; eLN 0.1 0.746; Zenodo all 0.713; >=5 syn (Shiu) -0.014 (-0.03+-0.20; DNa 21.1/19.7 -> 19.4/21.9) FAIL; Zenodo >=5 0.072 FAIL. cVA, applicable in 11 conditions (DNa alone >= 2 Hz): baseline 0.921; 50 Hz 0.692; 150 Hz 0.927; dt 0.1 0.959; dt 0.5 0.941; legacy 0.978; published 0.311 (per seed 0.33 / 0.24 / 0.35; 0.31+-0.06; DNa 33.6/3.9 -> 25.3/0.6) FAIL; known x1 0.444; Shiu x0.25 0.712; eLN 0.5 0.534; eLN 0.1 0.765. Not applicable at >=5 (cVA drives DNa 0/0, and touch raises it to 5.8/17.5 in the Shiu table and 5.8/16.7 in Zenodo) or in Zenodo all (0.56 Hz). At 5 seeds the paper's contact_stop gives the published cVA index as 0.355, so the 0.35 bound depends on the seeds. Gain 0.7: food drives DNa to only 0.33 Hz and cVA to 0, so the freeze cannot be tested there. Gain 1.4: food 0.754 (31.8 -> 7.8), cVA 0.867. 200 Hz: food 0.739, cVA 0.943. 300 Hz: food 0.700, cVA 0.966. Supporting check: in minsyn.csv (5 seeds) the Shiu table at k=5 gives food index -0.004; the freeze erodes with k (0.69 / 0.59 / 0.37 / -0.00 at k=1/2/3/5).
VERDICT REWORD
PAPER: Main text: 'The freeze survives every one of my alternatives but one: remove the connections made of fewer than five synapses, a common way of tidying a wiring diagram, and touch no longer quiets the steering neurons (with cVA as the smell it excites them), so the freeze depends on the weakest connections in the brain.' Note 4: '...the index is 0.69-0.93 from gain 1.0 to 2.0 (below 1.0 smells do not drive the DNa), 0.70-0.97 at 200 and 300 Hz, and 0.31-0.98 in every other condition that drives the DNa; it is lost only under the >=5-synapse threshold, in both connection tables (food: -0.01 and 0.07).'
NOTES: Freeze index over the 14 conditions (n = 3, 600 ms, touch at the drive's rate): food 0.50-0.98 (baseline 0.72 +- 0.07), cVA 0.31-0.98. The lowest is cVA under the published model, 0.31 +- 0.06 (0.36 at n = 5 in contact_stop). At >=5 synapses: food -0.01 +- 0.20 (Shiu table) and 0.07 +- 0.12 (Zenodo), and touch drives DNa from 0/0 to 5.8/17.5 Hz with cVA. Gain 1.4: 0.75 (food), 0.87 (cVA). 200 / 300 Hz: 0.74 / 0.70 (food), 0.94 / 0.97 (cVA). At gain 0.7 no smell drives the DNa (food 0.3 Hz), so the freeze cannot be tested there.

### [reflexes] Deciders (pC1a-e, aIPg, vpoEN/vpoDN, oviDN) fire 0.0 Hz to every input in all 14 conditions, at every gain up to 1.4 and at 200-300 Hz (Note 5)
STEPS: sensmap-female; gain-map-female; rate-map-female
CRITERION: S10.2: the six decider groups are 0.0 for every drive in all 14 conditions (any non-zero cell is named in Note 5). S11: every decider, mean and max1, is 0 for every drive at gains 0.7 and 1.4 and at 200 and 300 Hz; a response at gain <= 1.4 or at 200 Hz makes the Note 5 sentence conditional.
NUMBERS: Columns 'pC1a recept', 'pC1b/c', 'pC1d/e aggr', 'aIPg aggr', 'vpoEN/DN accept', 'oviDN egg', 'pC1a'..'pC1e', 'vpoEN', 'vpoDN (DNp37)', 'oviDNa', 'oviDNb', each with a max1 column. sensmap: 0.0 in 13 of 14 conditions (36 drives x 3 seeds each). Legacy numerics (8 of 1512 rows non-zero): pC1d fires to touch (all head bristles) 0 / 2.5 / 0 Hz (max1 5.0), eye bristles 2.5 / 0.8 / 0.8 (max1 3.3), JO-CE 1.7 / 0 / 0, Or47b+touch 0.8 / 0 / 0, and pheromones+song+touch 0 / 0.8 / 0.8; aIPg reaches 0.07. map_gain gain 0.7: all 0. Gain 1.4 (1000 ms): pC1d fires to 'wind/gravity (JO-CE)' at 3.5 / 0.5 / 3.0 Hz (2.33+-1.61; max1 4 / 1 / 3; pC1d/e group 1.75 / 0.25 / 1.5), to cVA-long at 0.5 / 0.5 / 0, and to aversive odour at 0 / 0.5 / 0. map_rate at 200 and 300 Hz: all 0. The paper's gain_sweep had no JO-CE input, which is why this was missed.
VERDICT REWORD
PAPER: Main text: 'The neurons that decide whether a female accepts a male or attacks another female, and whether a male courts, stay all but silent whatever the fly senses: in every version of the model the most any of them fires is a few spikes a second.' Note 5: 'pC1a-e, aIPg, vpoDN and oviDN fire 0.0 Hz to every input and combination at gains 0.7 and 1.0, at 200 and 300 Hz, and in 13 of the 14 conditions; the exceptions are pC1d, at 2.3 Hz to wind/gravity (JO-C/E) at gain 1.4 and up to 2.5 Hz to head or eye bristles under the legacy numerics.'
NOTES: Deciders, female (n = 3): 0.0 in all 36 drives x 13 of 14 conditions, at gain 0.7, and at 200/300 Hz. pC1d (2 neurons): 2.3 +- 1.6 Hz (single neuron at most 4 Hz) to JO-C/E at gain 1.4 (1000 ms), <= 0.5 Hz to cVA-long and to aversive odour at 1.4, and up to 2.5 Hz (single neuron 5 Hz) to head or eye bristles under the legacy numerics.

### [reflexes] Sugar, bitter and touch drive 0.0 Hz in every dopamine (teaching) neuron (Note 7; main text 'sugar and bitter tastes never reach the teaching neurons'), including at gains 0.7-1.4 and 200-300 Hz
STEPS: gain-map-female; rate-map-female (and sensmap-female for the 14 conditions)
CRITERION: S11: sugar, bitter and touch give PAM and PPL1 at most 0.5 Hz at gains 0.7 and 1.4 and at 200 and 300 Hz.
NUMBERS: Columns 'PAM (reward DA)' and 'PPL1 (punish DA)' (and their max1 columns); drives 'sugar GRNs', 'bitter GRNs' (65 neurons), 'touch (all head bristles)'; n=3. Sugar: 0.00 everywhere. Touch: 0 at 0.7, 200 and 300 Hz; PPL1 0.02 at gain 1.4 (0.06 / 0 / 0). Bitter: gain 1.4 PPL1 2.35+-1.28 (2.25 / 1.13 / 3.69; max1 10 / 6 / 19 Hz), PAM 0.06 FAIL; 200 Hz PPL1 1.39+-1.53 (1.15 / 0 / 3.02; max1 8.3 / 0 / 20) FAIL; 300 Hz PPL1 4.93+-2.29 (3.12 / 4.17 / 7.5; max1 23 / 28 / 48) FAIL; gain 0.7 0. sensmap at gain 1: sugar, bitter and touch all 0.00 in 13 of 14 conditions. Under legacy numerics touch -> PPL1 is 19.6+-7.8 Hz (max1 up to 153) and PAM 0.85. The paper's gain_sweep had no bitter input.
VERDICT REWORD
PAPER: Main text: 'In the model, at its standard settings, sugar and bitter tastes do not reach the teaching neurons, so I supplied the teaching signal myself...' Note 7: 'At gain 1.0 and 100 Hz, sugar, bitter and touch drive 0.0 Hz in every dopamine neuron (in 13 of the 14 conditions); sugar reaches none at any gain or rate I tried, but bitter begins to reach the punishment set when every synapse is turned up (PPL1 2.4 Hz at 1.4) or at 200-300 Hz (1.4-4.9 Hz).'
NOTES: Bitter GRNs -> PPL1 (n = 3): 0 at gains 0.7 and 1.0; 2.4 +- 1.3 Hz at 1.4 (one neuron up to 19 Hz); 1.4 +- 1.5 and 4.9 +- 2.3 Hz at 200 and 300 Hz (one neuron up to 48 Hz); PAM <= 0.1 Hz. Sugar 0.0 everywhere. Touch <= 0.06 Hz, except 19.6 +- 7.8 Hz PPL1 under the legacy numerics.

RUN PROBLEMS [reflexes]: The run is not broken. The one .check.txt (experiments/results_edge/sensmap/sensmap_flywire.check.txt) reports 728 cells compared and 0 mismatches over the 14 conditions (tolerance 1e-9). The logs (logs/edge/guarded_{sensmap,gain-map,rate-map}-female.out) end with 'wrote ...' and show no traceback or retry. None of the three CSVs has a NaN or a negative readout, the 'none' drive gives 0 spikes everywhere, and every cell has exactly 3 seeds. Seeds 0-2 of freeze-minsyn/minsyn.csv are bit-identical to sensmap conditions 0, 11, 12 and 13, so a separate run agrees with this one and the in-memory threshold agrees with the min5 cache. map_gain.csv and map_rate.csv have no .check.txt, by design of the step file. Their sidecars carry the same script and lif hashes (5597fa5189e27d67 / 9c6fe7be4bc2aaed) and 6 threads as sensmap. Their values match the paper's gain_sweep within seed noise, but they cannot be compared to the digit: map_gain is 1000 ms against gain_sweep's 600 ms.

Coverage gaps, which matter for the verdicts:
(1) The anchors preset pins every anchor term at @100. So in the 'stimulus 50 Hz' and '150 Hz' conditions the Shiu sugar/bitter/JON-CE/JON-F/JO-A@100 rows are bit-identical to baseline. Bitter suppression and the JON-CE/JON-F ratio were never run at another stimulus rate.
(2) The gain and rate maps use '--drives all' without --anchors. They contain no sugar+bitter drive and no JON-F drive, so bitter suppression and the 'JO-F not' half of grooming are unmeasured at gains 0.7/1.4 and at 200/300 Hz. S12 anchors-gain was running from 05:09 and will cover gains. The anchors_rate preset has no bitter drive, so bitter at other rates stays untested.
(3) At gain 1.0, the smell-centre-only conditions leave every non-smell readout bit-identical (conditions 0=2=4=5 and 1=3). The 14 conditions therefore give only 10 distinct tests for the non-smell reflexes, and 8 for the anchors. This bit-identity also confirms that the smell-centre change touches nothing outside smell at gain 1.0.
(4) Legacy numerics give extreme rates (sugar -> MN9 371 Hz, DNa up to 84 Hz, touch -> PPL1 20 Hz, pC1d up to 5 Hz). These match the paper's own sensitivity file, so they come from the old numerics and not from a broken run.
(5) The sensmap freeze is n = 3, and the published-model cVA index (0.31) crosses the 0.35 bound that the paper took from the 5-seed contact_stop file (0.355). That bound depends on the seeds.

Scratch scripts not kept. (reflex_edge.py, dec.py, sanity.py, fz.py).

>>> CHECK [reflexes] 1. Sugar -> MN9 passes the third test (14 female conditions), gains 0.7-1.4 and 200-300 Hz. Analyst: KEEP.: agrees=True
OWN: Engine checks: sensmap_flywire.check.txt shows 728 cells compared and 0 mismatches. I also checked other files myself. anchors_gain.csv at gain 1.0, seeds 0-2, reproduces benchmark_flywire_shiu_min1+known+eln0.25.csv to the digit (MN9 50/56/59, total_spikes 8872/8975/9068). anchors_rate.csv sugar@50 and @150 also match. minsyn.csv matches sensmap and contact_stop rows exactly (difference 0). No runaway seed in the paper's model affects these claims.

sensmap_flywire.csv, drive 'sugar GRNs' (129 neurons), column 'MN9' (Shiu root id), n=3 (seeds 0-2), 600 ms. Mean +- sd: base 77.2+-6.3; 50 Hz 63.9+-15.1 (46.7/70/75); 150 Hz 92.8+-10.0; dt0.1 87.8+-3.5; dt0.5 86.1+-1.0; legacy 371.1+-2.5; published 80.6+-1.0; Shiu x0.25 80.6; eLN x1/0.5/0.1 77.2 (bit-identical to base); >=5 92.2+-3.5; Zenodo >=5 95.0+-3.3; Zenodo all 79.4+-9.6. That is 63.9-95.0 Hz in 13/14 conditions, plus 371 under legacy.

Shiu's 29 neurons ('Shiu sugar@100'): 46.7-58.9 Hz, and 200+-40 under legacy.

map_gain.csv (1000 ms, n=3): gain 0.7 38.0+-2.6; gain 1.4 94.7+-4.2. The paper's gain_sweep (600 ms, n=5) gives 32.7+-8.6 / 76.0+-4.8 / 94.3+-8.8.

map_rate.csv (600 ms, n=3): 200 Hz 98.9+-9.2; 300 Hz 112.8+-8.6.

PAM, PPL1 and their max1 columns are 0.00 for sugar in every row of all three files.

The analyst missed one thing. anchors_gain.csv (n=10, 1000 ms) shows that Shiu's 29-neuron set barely drives MN9 at low gain: 0.1+-0.3 / 7.2+-3.9 / 36.9+-4.2 / 51.7+-4.5 / 62.8+-8.1 / 66.8+-5.1 Hz at gain 0.7/0.8/0.9/1.0/1.2/1.4. anchors_rate.csv (n=5, 1 s): 0 / 10.4+-2.1 / 67.8+-3.0 / 86.8+-3.3 Hz at 25/50/150/300 Hz. So the gain-0.7 pass holds only for the 129-neuron set.
CORRECTED: Verdict KEEP is right, and the main text stays unchanged.

In the Notes line, attach n to each source; the trailing '(n = 3)' is wrong for 33/76/94, which are n=5. Suggested line: 'Sugar -> MN9 33 / 76 / 94 Hz at gain 0.7 / 1.0 / 1.4 (n = 5, 600 ms); 99 +- 9 and 113 +- 9 Hz at 200 and 300 Hz, and 64-95 Hz in 13 of the 14 conditions (371 Hz under the legacy numerics) (n = 3). Shiu et al.'s 29 sugar neurons drive MN9 only from gain 0.9 (0.1 Hz at 0.7, 7 Hz at 0.8; n = 10).'

>>> CHECK [reflexes] 2. Bitter suppression of sugar -> MN9 passes the third test and holds at gains 0.7-1.4 and 200-300 Hz. Analyst: REWORD, with the gain clause left pending.: agrees=False
OWN: The third-test numbers are confirmed. sensmap, column 'MN9', drives 'Shiu sugar@100' and 'Shiu sugar@100 & Shiu bitter@{25,50,100}', n=3, 600 ms.

Ratio of MN9 with bitter@100 to sugar alone: base 2.78/55.56 = 0.050; dt0.1 0.088; dt0.5 0.040; legacy 5.56/200 = 0.028; published and Shiu x0.25 7.78/58.89 = 0.132 (the highest per-seed ratio is 0.242); >=5 0.105; Zenodo >=5 0.119; Zenodo all 0.063.

The dose is monotone in every row. There are only 8 distinct outcomes: 50 Hz, 150 Hz, known x1, eLN 0.5 and eLN 0.1 are hash-identical to baseline, and Shiu x0.25 is identical to published. The drive is pinned @100, so stimulus rate was never varied for bitter.

S12 has now finished (anchors/anchors_gain.csv, written 05:10, n=10, 1000 ms), and it FAILS the pre-set rule ('<25 % with a monotone dose at every gain'). Sugar alone -> +bitter@100 (ratio) by gain:
- 0.7: 0.1+-0.3 -> 0.0. Not testable; sugar gives no MN9.
- 0.8: 7.2+-3.9 -> 0.2+-0.4 (0.03). Dose not monotone: 7.2 -> 7.4 -> 1.6 -> 0.2.
- 0.9: 36.9+-4.2 -> 1.8+-1.5 (0.05).
- 1.0: 51.7+-4.5 -> 4.4+-3.7 (0.085). Seeds 0-2 give 2/1/7, identical to the paper's benchmark.
- 1.2: 62.8+-8.1 -> 15.7+-3.4 (0.250). Exactly at the bound, not below it.
- 1.4: 66.8+-5.1 -> 25.8+-4.6 (0.386; per-seed up to 0.48). FAIL.
The dose is monotone from 0.9 to 1.4.

anchors_rate.csv has no bitter drive, and map_gain/map_rate have no sugar+bitter drive, so the rate test is still unmeasured.
CORRECTED: CHANGE, not REWORD: the claim 'holds at gains 0.7-1.4' is false. The analyst's 'its gain test is in Note 2' is too weak, because the gain test has been run and it fails.

Main text: 'Sugar makes it work its mouthparts, and bitter makes it stop, though with every synapse a third stronger bitter only slows it.'

Note 4, after '3.3 Hz with bitter added': 'MN9 keeps 3-13 % of its sugar-alone rate in the 12 conditions of the sensitivity table that keep the stimulus at 100 Hz, falling steadily with bitter at 25, 50 and 100 Hz. By gain (10 seeds, 1 s) it keeps 5 % at 0.9, 9 % at 1.0, 25 % at 1.2 and 39 % at 1.4 (66.8 +- 5.1 -> 25.8 +- 4.6 Hz). At 0.7 these 29 sugar neurons do not drive MN9 at all (0.1 Hz). I did not vary bitter's stimulus rate.'

>>> CHECK [reflexes] 3. Sound (JO-A) -> giant fibre passes the third test and holds at gains 0.7-1.4 and 200-300 Hz. Analyst: REWORD.: agrees=True
OWN: sensmap, drive 'song/sound (JO-A)' (99 neurons, at each condition's rate), column 'GF jump', n=3, 600 ms:
- base 9.72+-0.48 (10.0/9.17/10.0)
- 50 Hz 1.11+-1.27 (0.83/2.5/0). FAIL, and food odour -> GF is 3.33, higher than sound.
- 150 Hz 17.5+-0.83
- dt0.1 11.39; dt0.5 11.94+-1.73; legacy 16.39
- published and all eLN rows 9.72
- >=5 10.28+-0.48; Zenodo >=5 10.28; Zenodo all 10.0+-1.44
So it is >=5 Hz in 13/14 conditions (9.7-17.5 Hz).

Largest odour -> GF over the 9 odour drives:
- base Or88a 5.00+-1.44, ratio 1.94. This fails the 2x rule at n=3, but the paper's gain_sweep at n=5 gives 10.83 vs 5.17 = 2.09, so the result is seed-marginal.
- 150 Hz 5.28 (3.3x); dt0.5 food 5.56 (2.15x); >=5 3.61 (2.85x).

map_gain (1 s): 0.7 5.83+-0.29 (lowest seed 5.5); 1.4 16.33+-1.15 against odour 5.67 (Or47b).
map_rate: 200 Hz 23.06+-0.96; 300 Hz 28.06+-1.27; odour up to 5.56.
anchors_rate (n=5, 1 s): 0 / 1.6+-0.4 / 18.1+-1.0 / 27.9+-0.7 Hz at 25/50/150/300 Hz.
anchors_gain (n=10, 1 s): 5.1+-1.0 at gain 0.7, with the lowest seed at 3.0.

The largest per-condition odour -> GF mean is 5.67 in the edge files, and 7.0 in the paper's gain_sweep (Or47b at 1.4). The analyst's 'up to 5 Hz' is therefore too low.

Side flag: 'GF jump max1' is exactly twice the mean in every JO-A row. Only one of the two giant fibres fires.
CORRECTED: Verdict REWORD is right, and 'A loud sound fires its escape jump' is fine for the main text.

Note 4: 'Sound (JO-A) -> giant fibre 6 / 11 / 16 Hz, 23 and 28 Hz at 200 and 300 Hz, and 10-18 Hz in 13 of the 14 conditions. At a 50 Hz stimulus it falls to 1-2 Hz (0 at 25 Hz). Smells also reach the giant fibre, at up to 5 Hz at gain 1.0 and 7 Hz at 1.4, about half the rate sound gives.'

Notes: say the 2x margin over smell is 1.9x at n = 3 and 2.1x at n = 5.

>>> CHECK [reflexes] 4. Wind (JO-CE) -> aBN1, with JO-F not driving it, passes the third test and holds at gains 0.7-1.4 and 200-300 Hz. Analyst: CHANGE.: agrees=True
OWN: sensmap, column 'aBN1', n=3, 600 ms.

Shiu JON-CE@100 (69 neurons):
- base 12.22+-4.19 (8.3/11.7/16.7)
- dt0.1 11.11; dt0.5 15.0; legacy 17.22+-5.09; published 11.67; Zenodo all 12.22
- >=5 and Zenodo >=5: 0.56+-0.96

Shiu JON-F@100 (60 neurons): 0 in 11 rows, 0.56 under legacy, and 3.89+-1.92 in both >=5 rows (5.0/1.7/5.0 Hz, i.e. 3/1/3 spikes).

The analyst's '12 of 14' is inflated. The 50 and 150 Hz rows ran the anchor at 100 Hz and are copies of baseline, so they do not test rate. When the anchor is run at 50 Hz (anchors_rate.csv, n=5, 1 s), JON-CE -> aBN1 is 0.2+-0.4 (FAIL). At 150 Hz it is 34.2+-1.6 and at 300 Hz 64.6+-1.1, with JON-F <= 0.2. The true count is 11 of 14.

The whole 'wind/gravity (JO-CE)' group (484 neurons, at each condition's rate): base 25.6+-1.0; 50 Hz 0.56+-0.96; 150 Hz 50.0; >=5 3.33+-2.89; Zenodo >=5 2.78+-2.55. It also passes 11 of 14.

S12 is now done (anchors_gain.csv, n=10, 1 s). JON-CE -> aBN1: 0.5+-0.7 / 3.3+-1.6 / 7.7+-2.2 / 13.0+-2.4 / 22.2+-2.9 / 31.7+-2.9 Hz at gain 0.7/0.8/0.9/1.0/1.2/1.4. JON-F stays <= 0.4+-0.5 at every gain. The rule 'aBN1 >= 5 Hz at gains 0.7-1.4 and at 50-150 Hz' fails at 0.7, 0.8 and 50 Hz.

The whole group at gain 0.7 still gives 9.0+-1.0 (map_gain), and 44.3+-2.1 at 1.4. The analyst's 'JO-F was not run at other gains or rates' is now false.
CORRECTED: Verdict CHANGE is right, but the proposed wording needs fixing: the gain-0.7 failure is missing, the count should be 11 of 14, and 'answers the wrong antennal neurons' rests on 1-3 spikes.

Main text: 'Wind on the antenna makes it groom, though not when the wind is weak, and not once the weakest connections are removed.' Optionally add, after the freeze sentence: 'The same threshold also costs the grooming reflex.'

Note 4: 'Wind (JO-CE, Shiu et al.'s 69 neurons) -> the grooming neuron aBN1 13.0 +- 2.4 Hz, with JO-F at 0.2 Hz (n = 10, 1 s). It is 11-17 Hz, with JO-F at most 0.6, in 10 of the 12 conditions that keep the stimulus at 100 Hz. It is 34 Hz at a 150 Hz stimulus but 0.2 Hz at 50 Hz. Under the >= 5-synapse threshold, in both tables, JO-CE gives 0.6 Hz and JO-F 3.9 Hz. By gain it is 0.5 / 3.3 / 7.7 / 13 / 22 / 32 Hz at 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4, with JO-F at most 0.4 throughout. The whole JO-C/E group (484 neurons) gives 9 / 26 / 44 Hz at gain 0.7 / 1.0 / 1.4 and 62 and 75 Hz at 200 and 300 Hz, but 0.6 Hz at 50 Hz and about 3 Hz at >= 5 synapses.'

Like the male MDN, the Shiu input set fails the gentlest version of the first test (gain 0.7).

>>> CHECK [reflexes] 5. The freeze (1 - DNa(smell+touch)/DNa(smell)) passes the third test wherever DNa alone reaches 2 Hz, holds at gains 0.7-1.4 and 200-300 Hz, and reverses only under >=5 synapses. Analyst: REWORD.: agrees=True
OWN: Formula as in contact_stop.py: 1 - mean(L+R with touch)/mean(L+R alone), from sensmap columns 'DNa L' and 'DNa R', n=3, 600 ms.

Food:
- base 0.715 (per seed 0.71+-0.07); 50 Hz 0.523; 150 Hz 0.688; dt0.1 0.737; dt0.5 0.669; legacy 0.979
- published 0.500; known x1 0.593; Shiu x0.25 0.526; eLN 0.5 0.500; eLN 0.1 0.746; Zenodo all 0.713
- >=5: -0.014 (21.1/19.7 -> 19.4/21.9; per seed -0.03+-0.20)
- Zenodo >=5: 0.072

cVA:
- base 0.921; 50 Hz 0.692; 150 Hz 0.927; dt0.1 0.959; dt0.5 0.941; legacy 0.978
- published 0.311 (0.33/0.24/0.35). This fails the 0.35 bound; the paper's contact_stop at n=5 gives 0.355.
- known x1 0.444; Shiu x0.25 0.712; eLN 0.5 0.534; eLN 0.1 0.765 (DNa alone 2.36 Hz)
- Not applicable at >=5 (DNa 0/0; with touch 5.8/17.5 Shiu, 5.8/16.7 Zenodo) or in Zenodo all (DNa alone 0.56 Hz). The index there is 0.25.

Or47b, where applicable: 0.37-0.98.
Touch alone at >=5 drives DNa to 6.1/19.2 (Shiu) and 7.5/18.1 (Zenodo).
map_gain: at 0.7 food drives DNa to only 0.33 Hz, so the freeze cannot be tested. At 1.4: food 0.754, cVA 0.867, Or47b 0.902.
map_rate: food 0.739 / 0.700 and cVA 0.943 / 0.966 at 200 / 300 Hz.

Wording problem: 'drives the DNa at all' is contradicted by Zenodo-all cVA (0.56 Hz, index 0.25) and 300 Hz Or47b (0.14 Hz, index -2.0). The paper's own contact_stop already gives Zenodo-all cVA -0.00.

minsyn.csv (n=5) shows the freeze eroding gradually as the threshold k rises:
- Shiu food: 0.69 / 0.59 / 0.37 / -0.00 at k = 1/2/3/5
- Zenodo food: 0.71 / 0.55 / 0.31 / 0.08
- Shiu cVA: 0.93 / 0.70 / 0.19 / n.a.
So the S13 keep-rule (>= 0.35 at k <= 3 in both tables) fails at k=3.

Specificity (minsyn, k=1): adding sugar, bitter, JO-A, JO-CE or random sensory sets to food instead of touch gives -0.12 to +0.13.
CORRECTED: Verdict REWORD is right.

Main text: 'The freeze survives every one of my alternatives but one: remove the connections made of fewer than five synapses, a common way of tidying a wiring diagram, and touch no longer quiets the steering neurons (on its own it now excites them), so the freeze depends on the weakest connections in the brain.'

Note 4: '...the index is 0.69-0.93 from gain 1.0 to 2.0 (at 0.7 smells do not drive the DNa), 0.70-0.97 at 200 and 300 Hz, and 0.31-0.98 in every other condition in which the smell drives the DNa to at least 2 Hz. The lowest, cVA under the published model, is 0.31 +- 0.06 with 3 seeds and 0.36 with 5. The freeze is lost under the >= 5-synapse threshold in both connection tables (food -0.01 and 0.07). It already weakens when only the 1- and 2-synapse connections are removed (food 0.37 and 0.31, cVA 0.19). Other senses added in place of touch give -0.12 to 0.13.'

>>> CHECK [reflexes] 6. Deciders (pC1a-e, aIPg, vpoEN/vpoDN, oviDN) fire 0.0 Hz to every input in all 14 conditions, at every gain up to 1.4 and at 200-300 Hz (Note 5). Analyst: REWORD.: agrees=True
OWN: Columns: the 6 group columns plus pC1a..e, vpoEN, vpoDN (DNp37), oviDNa and oviDNb, each with its max1.

sensmap: 8 of 1512 rows are non-zero, all under legacy (cond 10). pC1d per seed:
- touch (all head) 0/2.5/0 (max1 5.0)
- eye bristles 2.5/0.83/0.83 (max1 3.3)
- JO-CE 1.67/0/0
- Or47b+touch 0.83/0/0
- pheromones+song+touch 0/0.83/0.83
The analyst missed one: aIPg aggr 0.072 in seed 0 of Or47b+touch, which is one aIPg neuron at 1.67 Hz (a single spike).

map_gain at 0.7: all 0. At 1.4 (1 s): pC1d to 'wind/gravity (JO-CE)' 3.5/0.5/3.0 = 2.33+-1.61 (max1 4/1/3); cVA-long 0.5/0.5/0; aversive odour 0/0.5/0.
map_rate at 200 and 300 Hz: all 0.

The analyst missed an independent replicate: anchors_gain.csv (n=10, 1 s), Shiu JON-CE@100 at gain 1.4 gives pC1d 0.45+-0.50, non-zero in 6 of 10 seeds, single neuron at most 3 Hz. Every anchor drive at gains 0.7-1.2 gives 0.

The paper's gain_sweep is 0 up to 1.4 but has no JO-CE input. It is non-zero only at 2.0 (pC1d/e up to 6.7). anchors_rate.csv and minsyn.csv: all 0.
S11's rule was that a response at gain <= 1.4 makes the Note 5 sentence conditional. It is triggered.
CORRECTED: Verdict REWORD is right.

Main text, as proposed: '...stay all but silent whatever the fly senses: in every version of the model the most any of them fires is a few spikes a second.'

Note 5: 'pC1a-e, aIPg, vpoDN and oviDN fire 0.0 Hz to every input and combination at gains 0.7 and 1.0, at 200 and 300 Hz, and in 13 of the 14 conditions. The exceptions are pC1d, at 2.3 Hz to wind/gravity (JO-C/E) at gain 1.4 (0.5 Hz, 10 seeds, with Shiu et al.'s 69 JO-C/E neurons) and at most 0.3 Hz to two odours there, and up to 2.5 Hz to head or eye bristles under the legacy numerics, where one aIPg neuron also fired once.'

>>> CHECK [reflexes] 7. Sugar, bitter and touch drive 0.0 Hz in every dopamine (teaching) neuron (Note 7 and main text), including at gains 0.7-1.4 and 200-300 Hz. Analyst: REWORD.: agrees=True
OWN: Columns 'PAM (reward DA)' and 'PPL1 (punish DA)' plus their max1 columns. Drives 'sugar GRNs', 'bitter GRNs' (65 neurons) and 'touch (all head bristles)'.

sensmap: all 0 in 13 of 14 conditions, including bitter at 50 and 150 Hz. Under legacy, touch drives:
- PPL1 19.58+-7.91 (25.6/10.6/22.5). The analyst wrote +-7.8; the correct sd is 7.9.
- max1 153/67/137
- PAM 0.85+-0.36, max1 up to 38 Hz
Eye bristles under legacy drive PPL1 at 31.9.

map_gain:
- 0.7: all 0
- 1.4: bitter PPL1 2.35+-1.28 (2.25/1.13/3.69; max1 10/6/19); PAM 0.06 (max1 up to 5)
- 1.4: touch PPL1 0.02 (max1 1); sugar 0

map_rate:
- bitter PPL1 1.39+-1.53 at 200 Hz (1.15/0/3.02; max1 8.3/0/20)
- bitter PPL1 4.93+-2.29 at 300 Hz (3.12/4.17/7.5; max1 23/28/48)
- sugar and touch 0
S11 (<= 0.5 Hz) fails for bitter at 1.4, 200 and 300 Hz. anchors_gain: Shiu bitter@100 (20 neurons) gives 0 at every gain.

The analyst missed that '13 of 14' rests on seeds 0-2. In social_probe_flywire_shiu_min1_noise0.csv (published model, n=5), sugar seed 4 runs away (284,010 spikes; PPL1 61, PAM 11 Hz). In gain_sweep_flywire_shiu_min1.csv at 1.4, sugar drives PPL1 at 55 Hz and touch at 134 Hz. So the claim holds only for the paper's own smell centre.

At the body's taste rate (<= 150 Hz) and touch rate (200 Hz), at gain 1.0, it holds.
CORRECTED: Verdict REWORD is right, and the analyst's main-text change ('at its standard settings... do not reach') is good.

Note 7: 'Under my model at gain 1.0, sugar, bitter and touch drive 0.0 Hz in every dopamine neuron at 50-150 Hz and in 13 of the 14 conditions (under the legacy numerics touch drives PPL1 at 20 Hz). Sugar reaches none at any gain or rate I tried. Bitter begins to reach the punishment set when every synapse is turned up (PPL1 2.4 Hz at 1.4) or at 200-300 Hz (1.4-4.9 Hz), above the 150 Hz I use for taste in the body. Under the published smell centre, one sugar run in five ignites the memory centre (PPL1 61 Hz).'

Notes: legacy touch -> PPL1 is 19.6 +- 7.9 Hz.

### [states] Note 6 (l.147): 'SAG -> pC1a 21, pC1b/c 19 and vpoDN 5.7 Hz, all from 0; with touch, pC1d/e 6.2 Hz.' Main text (l.97): 'her deciding neurons wake up, together with the neuron that opens her genital plate'. Which neuron actually fires?
STEPS: S18 state-10seeds (state_probe, 10 seeds, silent) + S16 state-split (grid_probe preset state_split, 10 seeds, split readouts) + state-hum (10 seeds, 0.2 Hz hum)
CRITERION: S18: seeds 0-4 equal the paper file to the digit; seeds 5-9 reproduce the SAG values within 2 SEM. S16: the split readouts name the neuron that fires; if vpoEN rather than DNp37 carries it, the genital-plate sentence changes.
NUMBERS: experiments/results_edge/state-10seeds/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv, state=='virgin (SAG tonic)', input=='none', n=10, mean +- sd:
- 'pC1a recept' 21.15 +- 3.89
- 'pC1b/c' 18.88 +- 3.35
- 'vpoEN/DN accept' 5.72 +- 1.13
Seeds 0-4 against seeds 5-9: 21.20/21.10, 19.00/18.75 and 5.73/5.70, at most 0.24 SEM apart (pass).

experiments/results_edge/state-split/state_split.csv, drive 'virgin (SAG tonic)@30', n=10:
- 'vpoEN' 0.00; 'vpoEN max1' is 0.00 in all 90 rows
- 'vpoDN (DNp37)' 17.15 +- 3.38; the two neurons fire at 18.6 +- 3.7 ('max1') and 15.7 +- 3.2
- 'pC1a' 21.15 +- 3.89, 'pC1b' 18.85 +- 3.40, 'pC1c' 18.90 +- 3.33
- The pooled column is exactly (4 x vpoEN + 2 x DNp37) / 6.

With touch (drive 'virgin (SAG tonic)@30 & touch (all head bristles)@100'), n=10:
- 'pC1d/e aggr' 6.88 +- 1.11, made of 'pC1d' 13.75 +- 2.23 and 'pC1e' 0.00
- Touch alone gives 0.00; all 10 seeds are at 5.25 Hz or more.
- Held-out check FAILS for this number: seeds 0-4 give 6.20, seeds 5-9 give 7.55 (3.1 SEM of seeds 0-4; 2.35 SE of the difference; Welch p=0.047).

On the hum (state-hum file, n=10):
- SAG gives pC1a 19.6 +- 3.4, pC1b/c 17.6 +- 2.8 and vpoEN/DN 5.13 +- 0.88. If vpoEN stays silent, 3x the pooled value is about 15.4 Hz for DNp37; the arena's DNp37-only readout gives 15.3-16.5.
- SAG + touch gives pC1d/e 6.12 +- 0.59, against 0.38 +- 0.27 for touch alone.
- Hum against silent for SAG alone: every p >= 0.14.
- The no-state deciders sit at the hum floor, at most 0.45 Hz.
VERDICT CHANGE
PAPER: Note 6: "SAG -> pC1a 21, pC1b/c 19 and vpoDN (DNp37) 17 Hz, all from 0; the vpoEN neurons that feed vpoDN stay silent. With touch, pC1d 14 Hz; pC1e stays silent." Main text l.97 stays as written. The split shows that the neuron that fires is vpoDN, the genital-plate neuron.
NOTES: Virgin state (SAG at 30 Hz, 10 seeds, no background activity):
- pC1a 21.2 +- 3.9 Hz, pC1b 18.9 +- 3.4, pC1c 18.9 +- 3.3.
- vpoDN (the two DNp37 neurons) 17.2 +- 3.4 Hz, at 18.6 and 15.7 each; vpoEN 0.0. Averaged over all six vpoEN/vpoDN neurons, 5.7 +- 1.1.
- With touch: pC1d 13.8 +- 2.2 and pC1e 0.0. Pooled pC1d/e is 6.9 +- 1.1 (6.2 over seeds 0-4, 7.6 over seeds 5-9).
- All of these are 0.0 without the state.
- Seeds 0-4 reproduce the published file to the digit, and seeds 5-9 reproduce the state-alone values within 0.3 SEM.
- With the hum (10 seeds): pC1a 19.6 +- 3.4, pC1b/c 17.6 +- 2.8, pooled vpoEN/vpoDN 5.1 +- 0.9, and pC1d/e with touch 6.1 +- 0.6 Hz.

### [states] Does the virgin-state result hold at gains 0.7 and 1.4 (S17)?
STEPS: state-gain: state_probe at --gain 0.7 and 1.4, 5 seeds each (gain0.7/ and gain1.4/). Gain 1.0 is the paper file experiments/results/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv.
CRITERION: S17: add 'at gains 0.7-1.4' if, at both gains, all of these hold:
- SAG alone gives pC1a >= 5 Hz and vpoEN/DN > 1 Hz;
- SAG + touch gives more pC1d/e than touch alone;
- the no-state deciders stay at 0.0;
- oviDN stays at 0.
If pC1a is below 2 Hz at gain 0.7, the virgin state has a gain window.
NUMBERS: SAG alone (input 'none'), gain 0.7 / 1.0 / 1.4, n=5 each, mean +- sd:
- 'pC1a recept' 11.90 +- 3.70 / 21.20 +- 5.62 / 30.30 +- 4.04
- 'pC1b/c' 9.30 +- 3.56 / 19.00 +- 4.64 / 29.30 +- 4.77
- 'vpoEN/DN accept' 1.60 +- 0.72 / 5.73 +- 1.55 / 11.37 +- 1.43

SAG + touch, 'pC1d/e aggr': 0.15 +- 0.14 / 6.20 +- 0.97 / 9.15 +- 1.04. Touch alone gives 0.00 at every gain. At gain 0.7 the per-seed values are 0.25, 0.25, 0.25, 0, 0.

State 'none': pC1a, pC1b/c, pC1d/e, aIPg, vpoEN/DN and oviDN are 0.00 for all 9 inputs at every gain.

'oviDN egg' is 0.00 in all 450 rows at each gain.

Every S17 criterion passes. pC1a at gain 0.7 is 11.9 Hz, far above 2, so there is no gain window. The touch -> pC1d/e interaction nearly disappears at gain 0.7 (0.15 Hz).
VERDICT REWORD
PAPER: Note 6: "SAG -> pC1a 12 / 21 / 30 and pC1b/c 9 / 19 / 29 Hz at gain 0.7 / 1.0 / 1.4, all from 0; with touch, pC1d/e 0.2 / 6 / 9 Hz." Optionally add in the main text: "at every strength of connection I tested".
NOTES: Gain window (5 seeds per gain):
- SAG alone gives pC1a 11.9 +- 3.7 / 21.2 +- 5.6 / 30.3 +- 4.0 Hz and pC1b/c 9.3 +- 3.6 / 19.0 +- 4.6 / 29.3 +- 4.8 Hz at gain 0.7 / 1.0 / 1.4.
- Averaged over vpoEN and vpoDN: 1.6 +- 0.7 / 5.7 +- 1.5 / 11.4 +- 1.4 Hz.
- With touch, pC1d/e 0.15 +- 0.14 / 6.2 +- 1.0 / 9.2 +- 1.0 Hz. Touch alone gives 0 at each gain.
- Without the state, every decider and oviDN is 0.0 at each gain.

### [states] Hunger and fullness states change nothing specific (l.97: 'changes nothing, in either sex'; Note 6: 'at most 7 Hz on MN9, as much as unrelated states'; NPF +6.8 Hz against 3.6-4.4 for unrelated states). Tested at n = 10 and on the hum.
STEPS: S18 state-10seeds (silent, n=10) and S19 state-hum (0.2 Hz hum, n=10). No male hum run exists yet (state-hum-male is queued at P2).
CRITERION: S18: compare NPF's shift on MN9 with sugar against the unrelated-state band at n=10 (Welch).
S19: KEEP if every hunger state's change from 'none' on the hum is within 2 SEM AND inside the unrelated-state band on feed MNs, MN9, DNa L/R, PPL1, PAM and MDN. If a change is larger than about 3 Hz and larger than the unrelated states', qualify the sentence.
NUMBERS: Silent, n=10, input 'sugar GRNs', column 'MN9':
- No state: 81.90 +- 4.79.
- NPF: 85.10 +- 3.28, a shift of +3.2 (Welch against none p=0.10). Seeds 0-4 give +6.8 and seeds 5-9 give -0.4, so the paper's +6.8 was a 5-seed fluctuation.
- Unrelated band: -0.2 to +3.5 (SAG +3.5, pC1a-c +0.5, pC1d/e -0.1, aIPg -0.2).
- Other hunger and fullness states: DH44 +3.5, SIFa +1.5, AstA 0.0, IPC -0.4.
- NPF against the pooled unrelated states: Welch p=0.09 (Mann-Whitney 0.15). ANOVA over all 10 states: p=0.43.

Largest hunger shift over all 810 cells (silent) is MN9 with 'cVA + sugar' (no state 76.4):
- SIFa +5.2 (p=0.12) and IPC +4.5 (p=0.03, uncorrected).
- Unrelated states reach +3.6 on this cell. Against the pooled unrelated states, SIFa p=0.42 and IPC p=0.30; ANOVA over the 10 states p=0.46.

On every other key readout (silent), the largest hunger shift is at most 1.7 Hz (feed MNs, DNa), 0.6 (PPL1), 0.1 (MDN) and 0.01 (PAM). Unrelated states move DNa by up to 16.5.

Recruitment at rest (input 'none', active_frac x 139,248 minus n_driven):
- IPC, DH44, NPF, SIFa and AstA recruit 0 neurons in all 10 seeds.
- SAG recruits 55 (35-103), pC1a-c 103, pC1d/e 68, aIPg 167.

On the hum (state-hum file), 315 key cells:
- 301 are within 2 SE, 247 are inside the band and 238 pass both, so the S19 KEEP condition formally fails.
- The qualify trigger fires in 7 cells, all MN9. Examples: JO-A with NPF or SIFa +14.3 against a band maximum of +14.2; sugar with SIFa -9.5 and DH44 +7.6 against a band of -7.4 to +7.0; Or47b with DH44 -11.7 and AstA +10.3. Every one has p >= 0.17 and SE 6.5-13.6 Hz.
- MN9 on the hum is bistable: with no state and no input it runs at 1-95 Hz depending on the seed (sd up to 40).
- Each flagged hunger shift is within 0.1-2.1 Hz of the unrelated state that shares its random numbers (same number of driven neurons). Examples: JO-A MN9 NPF +14.3 against pC1d/e +14.2; with sugar, DH44 against pC1a-c +0.6 Hz (paired).
- Excluding MN9, the largest hunger shift on the hum is 3.45 Hz (NPF, DNa L with JO-A); unrelated states reach 14.5.
- Feed MNs: hunger at most -1.57 against unrelated -1.56. PPL1 +1.2 against -2.4. MDN -0.3 against -0.5. PAM 0.03 against 0.03.
VERDICT REWORD
PAPER: Main text l.97: "Hunger is another matter. Keeping the fly's hunger and fullness neurons firing changes nothing that unrelated states do not change as well, in either sex, and in the female this holds with background activity too."
Note 6, in place of 'IPC, DH44, NPF, SIFa and AstA change no readout specifically (at most 7 Hz on MN9, as much as unrelated states)': "IPC, DH44, NPF, SIFa and AstA switch on no neuron but their own at rest, and change no readout more than unrelated states do. With sugar they move MN9 by -0.4 to +3.5 Hz, and the virgin, aroused and aggressive states by -0.2 to +3.5 Hz. The largest shift anywhere is 5 Hz on MN9 with cVA and sugar (SIFa), which cannot be told apart from the unrelated states."
NOTES: Hunger and fullness (10 seeds):
- With sugar, MN9 is 81.9 +- 4.8 Hz without a state and 85.1 +- 3.3 under NPF (+3.2, p = 0.10). The earlier +6.8 came from the first 5 seeds; the next 5 give -0.4.
- DH44 +3.5, SIFa +1.5, AstA 0.0, IPC -0.4. Unrelated states: -0.2 to +3.5 (NPF against them, p = 0.09; across all ten states, ANOVA p = 0.43).
- Largest hunger shift over all 810 cells: +5.2 Hz, SIFa on MN9 with cVA and sugar. Unrelated states give up to +3.6 there (p = 0.42).
- At rest the five hunger and fullness groups recruit 0 neurons in every seed. SAG recruits 55, pC1a-c 103 and aIPg 167.
- With the hum (10 seeds), hunger states move the 52 feeding motor neurons by at most 1.6 Hz, DNa by at most 3.5, PPL1 by 1.2 and MDN by 0.3. Unrelated states move these by up to 1.6, 14.5, 2.4 and 0.5.
- On the hum the single MN9 neuron flips between about 1 and 95 Hz from one noise draw to the next. There it can only exclude changes larger than about 15 Hz, and its largest hunger shifts match the unrelated states that share the same noise draw within 2 Hz.
- The male was tested without the hum only.

### [states] DNp13 is state-blind (Note 6: 'DNp13 fires at 36 Hz virgin or mated'; main text: 'a mated female extends her ovipositor no more often than a virgin').
STEPS: S18 state-10seeds (silent, n=10), state-hum (n=10), state-gain 0.7 and 1.4 (n=5), state-split per-side readouts
CRITERION: S18: DNp13 under SAG or pC1a-c within 2 SEM of no state. P2 state-dose (not yet run): a change > 3 Hz at p < 0.01 would qualify the 'state-blind' miss.
NUMBERS: 'DNp13 reject', silent, n=10.
With touch (no state 35.95 +- 0.80):
- SAG 36.10 +- 0.74: +0.15, 0.44 SE of the difference, 0.6 SEM of the no-state mean (pass).
- pC1a-c 36.65 +- 1.08: +0.70, 1.65 SE of the difference, but 2.8 SEM of the no-state mean; Welch p=0.12.
With cVA + touch (no state 36.90 +- 1.37):
- SAG -0.65 (1.07 SE).
- pC1a-c -0.95 (1.33 SE; 2.2 SEM of the no-state mean).
All 9 states fall within -0.95 to +1.35 Hz. The largest shift is IPC +1.35, Welch p=0.005, so unrelated states move DNp13 more than SAG does.

Hum, n=10, with touch (no state 36.55 +- 2.61): SAG -0.8 (p=0.46), pC1a-c -2.3 (p=0.04). All states fall within -2.3 to 0.

Gains, n=5:
- Gain 0.7 (no state 28.3): SAG -1.1 (p=0.22).
- Gain 1.0 (paper file; no state 35.6): SAG +0.6 (p=0.27).
- Gain 1.4: no state 41.9 +- 1.9 against SAG 37.9 +- 3.0, -4.0 Hz (Welch p=0.04); pC1a-c -1.8 (p=0.30).

Split readouts (state_split.csv): DNp13 L 43.2 and R 28.7 with touch alone, against 43.4 and 28.8 with SAG + touch.

Pass if SEM means the SE of the difference. Under the stricter 'SEM of the no-state mean' reading, pC1a-c misses by 0.7-0.95 Hz. At gain 1.4 the virgin state lowers DNp13 by 10 %, which is short of the P2 qualify threshold (p < 0.01).
VERDICT REWORD
PAPER: Note 6: "DNp13 fires at 36 Hz whether or not the virgin neurons are driven (the undriven brain stands in for a mated female)." Main text: "...and, at the strength I drove them, a mated female extends her ovipositor no more often than a virgin."
NOTES: Touch -> DNp13 (10 seeds): 36.0 +- 0.8 Hz without a state and 36.1 +- 0.7 with the virgin neurons; every state stays within 1.4 Hz. With the hum, every state stays within 2.3 Hz of 36.6. At gain 1.4 the virgin state lowers it from 41.9 +- 1.9 to 37.9 +- 3.0 Hz (5 seeds, p = 0.04).

### [states] oviDN stays at 0 under every state (Note 6) / 'no state starts egg-laying' (l.97).
STEPS: S18 state-10seeds, S16 state-split, S17 state-gain, state-hum
CRITERION: S17: oviDN stays at 0 at gains 0.7 and 1.4. Claim: 0 under every state.
NUMBERS: 'oviDN egg':
- 0.00 in all 900 rows of state-10seeds (10 states x 9 inputs x 10 seeds).
- 0.00 in all 450 rows at gain 0.7 and in all 450 at gain 1.4.
- In state_split.csv, 'oviDNa max1' and 'oviDNb max1' are 0.00 in all 90 rows.

On the hum the per-state mean is 0.12-0.25 Hz (no state 0.19), the noise floor. The largest state-minus-none cell is +0.13 Hz.

'oviIN' (the inhibitory oviposition neuron upstream of oviDN) fires 1.35 +- 0.67 Hz under SAG and 3.20 +- 0.92 under pC1a-c, against 0 without a state (n=10).
VERDICT KEEP
PAPER: Unchanged: "oviDN stays at 0 under every state". Optionally add "at every gain from 0.7 to 1.4".
NOTES: oviDN (6 neurons) is 0.0 Hz in every state x input x seed: 900 runs at gain 1.0 and 450 each at gains 0.7 and 1.4. With the hum it stays at the hum's floor (0.1-0.25 Hz) under every state.

### [states] P1 -> pIP10 50, TN1 8 (the male's courtship neurons switch on the song command), and is it specific?
STEPS: S20 matched-null male: matched_null_male.csv, grid_probe preset matched_null, MaleCNS all_min1+eln0.25, 3 seeds, 20 draws of 148 output-matched central neurons
CRITERION: S20: KEEP if, in at least 19 of 20 draws of 148 output-matched central neurons, pIP10 stays at or below 10 Hz and TN1 at or below 2 Hz. If the median draw gives pIP10 of 25 Hz or more, the sentence becomes 'a lot of central drive reaches the song command'.
NUMBERS: experiments/results_edge/matched-null/matched_null_male.csv, 3-seed means per draw.

Real P1 (draw -1): 'pIP10 song cmd' 50.33 (52 / 49.5 / 49.5), 'TN1 song' 7.88, 'song MNs' 27.24, recruited_spikes 18,130.

The 20 null draws:
- pIP10: 0.00 in 19 draws and 0.83 in one; single-neuron max ('pIP10 song cmd max1') 1.7.
- TN1: 0.00 in all 20.
- Song MNs: at most 1.98 (median 0.23).
- pIP10 <= 10 and TN1 <= 2 in 20/20 draws, and in every seed of every draw. Median pIP10 is 0.
- recruited_spikes: 340-35,289 (median 1,388). The difference is not explained by total drive.

Paper file experiments/results/state_probe_malecns_all_min1+eln0.25_state30.csv, P1 with input 'none', n=5: pIP10 50.40 +- 1.24, TN1 8.17 +- 0.48, song MNs 27.59 +- 1.22. Without P1, pIP10 is at most 3.8 and TN1 at most 1.8.

The matched-null real rows equal the paper file (225 cells, 0 mismatches).
VERDICT KEEP
PAPER: Keep "P1 -> pIP10 50, TN1 8". Optionally add: "No random set of 148 central neurons with the same output strength does this (20 of 20 sets: pIP10 at most 1 Hz, TN1 0)." The song-MN clause still needs the earlier fix (contact pheromone alone gives 21 Hz).
NOTES: P1 (148 neurons at 30 Hz, 5 seeds): pIP10 50.4 +- 1.2 Hz and TN1 8.2 +- 0.5 Hz; without the state they are at most 3.8 and 1.8. In 20 draws of 148 random central neurons matched for total output strength (3 seeds each):
- pIP10 is at most 0.8 Hz (median 0) and TN1 is 0.
- The song motor neurons stay at or below 2 Hz, against 27 Hz under P1.
- The draws recruited 340-35,289 spikes, against 18,130 for P1.

### [states] The female virgin-state result is specific: output-matched random neurons in place of SAG do not wake pC1a-c or vpoEN/DN (P2 state-nulls-female).
STEPS: matched-null female: matched_f.csv, grid_probe preset matched_null, groups SAG, NPF and IPC, 20 draws plus the real group, inputs none and touch@100, 3 seeds
CRITERION: P2 state-nulls-female: matched draws give pC1a-c and vpoEN/DN <= 1 Hz in >= 19/20 draws. Its second half, SAG + hunger within 2 SEM of SAG alone (sag_hunger.csv), has not run yet.
NUMBERS: experiments/results_edge/matched-null/matched_f.csv, 3-seed means per draw.

Real SAG (draw -1, seeds 0-2): 'pC1a recept' 25.17, 'pC1b/c' 22.08, 'vpoEN/DN accept' 6.78, 'vpoDN (DNp37)' 20.33, recruited_spikes 394. With touch, 'pC1d/e aggr' 6.75.

The 20 SAG null draws (2 output-matched ascending neurons each, pool of 1,748):
- pC1a, pC1b/c, vpoEN/DN, vpoDN and pC1d/e are 0.00, both alone and with touch; every single-neuron max1 is 0.00. That is 20/20.
- recruited_spikes median 1 (0-30).

NPF and IPC: the real groups give 0.00 on all deciders, like their nulls. NPF recruits 0 spikes against a null median of 3 (maximum 534).

The real rows equal the paper file (414 cells, 0 mismatches).
VERDICT KEEP
PAPER: Optional clause for Note 6: "Two random neurons with the same output strength in place of SAG wake none of these neurons (20 of 20 pairs)."
NOTES: Matched null (3 seeds per draw): in 20 draws of 2 ascending neurons matched to SAG's total output strength, pC1a-c and vpoEN/vpoDN stay at 0.0 Hz, both alone and with touch. Real SAG in the same runs gives pC1a 25, pC1b/c 22 and vpoDN 20 Hz.

RUN PROBLEMS [states]: No .check.txt mismatches. None of the runs look broken.

**Reproduction checks**
- experiments/results_edge/state-split/state_split.check.txt: 1035 cells, 0 mismatches (tolerance 1e-9). It covers the 45 rows for seeds 0-4; seeds 5-9 have no reference.
- The state-10seeds file equals experiments/results/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv to the digit for seeds 0-4: 450 rows, 23 numeric columns, 0 differences, and DataFrame.equals is true once wall_s is dropped.
- Seeds 5-9 cross-check: grid_probe (state_split.csv) and state_probe (state-10seeds) agree on all 90 shared rows x 23 columns, 0 differences.
- The matched-null steps ran without --check-against. I checked their real-group rows against the paper state files by hand: female 414 cells, male 225 cells, 0 mismatches.

**Run health**
- All 7 steps finished ok on attempt 1 (logs/edge/queue_20260927.out, lines 20-33).
- No NaN or duplicate rows in any file.
- Sidecars show NUMBA 6 threads, sha256_lif 9c6fe7be4bc2aaed, the paper variants, and noise 0.2 applied only in state-hum.

**Design caveats**
1. **Drive and hum share one random stream.** lif.py lines 229-239 draw the drive and the hum from one sequential np.random stream, driven neurons first. Rows that drive the same number of neurons get identical random numbers: SAG/AstA (2), pC1d/e/NPF/SIFa (4) and pC1a-c/DH44 (6). NPF and SIFa at rest give identical spike totals in every seed, and on the hum MN9 per seed is identical within each of those sets. So state-vs-none comparisons use different Poisson realisations and must be unpaired (Welch). The 'paired p=0.017' in verify_wording_full.md 16a is not a valid pairing.
2. **MN9 is bistable on the hum.** With no state and no input it runs at 1-95 Hz depending on the seed (sd up to 40 Hz). This produces the 7 MN9 cells that formally trip the S19 qualify rule.
3. **The null pools are not all central neurons.** The female SAG null draws from ascending neurons (pool 1,748). The female IPC null pool has only 62 endocrine neurons, so its 20 draws of 18 use just 33 distinct neurons and overlap heavily.
4. **Some readouts come from one setting only.** Split readouts exist only at gain 1.0 without the hum. The hum value for DNp37 (about 15 Hz) is inferred from the pooled column.

**Still pending in the queue**
- state-dose-female (P2)
- sag-hunger, the second half of state-nulls-female (P2)
- state-hum-male (P2)
- global-shuffle-male-plus (P2: P1 -> pIP10 in a rewired male). shuffle-plus-female was running at 05:10, and experiments/results_edge/shuffle-plus/ is still empty.

So "in either sex" is untested on the hum, and the 100 Hz state dose and SAG + hunger remain open.

Scratch scripts not kept. No project files were modified and no simulations were run.

>>> CHECK [states] 1. Note 6 'SAG -> pC1a 21, pC1b/c 19 and vpoDN 5.7 Hz ... with touch, pC1d/e 6.2 Hz'; main text l.97 'together with the neuron that opens her genital plate'. Analyst: CHANGE Note 6, keep main text.: agrees=True
OWN: Pre-set criterion (S18 + S16): seeds 0-4 must equal the paper file to the digit, seeds 5-9 must reproduce 21 / 19 / 5.7 within 2 SEM, and the split readout must name the neuron that fires. Verdict: CHANGE is right for Note 6 and the main text stays, but the proposed wording needs four fixes (see corrected wording).

Run integrity:
- state-10seeds seeds 0-4 against experiments/results/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv: 450 rows x 23 numeric columns, max |diff| 0. The paper file is also identical to release/pre_rerun_20260926.
- state_split.check.txt: 1,035 cells, 0 mismatches. Its 45 unreferenced rows (seeds 5-9) are identical to the 10-seed state_probe rows, so all 90 split rows match the state_probe file to the digit.
- Logs are ok and there are no NaNs.

State 'virgin (SAG tonic)', input 'none', n=10, mean +- sd:
- pC1a 21.15 +- 3.89; pC1b 18.85 +- 3.40; pC1c 18.90 +- 3.33 (pooled pC1b/c 18.88 +- 3.35).
- Seeds 0-4 against seeds 5-9: pC1a 21.20 / 21.10, pC1b/c 19.00 / 18.75, vpoEN/DN 5.733 / 5.700. That is at most 0.12 SEM of seeds 0-4, a pass.

state_split.csv, drive 'virgin (SAG tonic)@30':
- 'vpoEN' is 0.00 and 'vpoEN max1' is 0.00 in all 90 rows. vpoEN also stays at 0 with SAG + JO-A song.
- 'vpoDN (DNp37)' 17.15 +- 3.38. DNp37 is 2 neurons, hemibrain_type vpoDN, in the annotations TSV.
- Per seed, the faster DNp37 neuron fires at 18.6 +- 3.7 and the slower at 15.7 +- 3.2. These are faster/slower per seed, not fixed L/R identities.
- Pooled 'vpoEN/DN accept' = (4 x vpoEN + 2 x DNp37) / 6 exactly (5.72 +- 1.13).

Things the analyst omitted:
- SAG alone already drives pC1d at 2.30 +- 1.36 Hz (pooled pC1d/e 1.15 +- 0.68), not 0.
- SAG + touch: pC1d 13.75 +- 2.23, pC1e 0.00, pooled pC1d/e 6.88 +- 1.11. Touch alone gives 0.00.
- Over seeds 0-4, pC1d with touch is 12.4 (= 2 x 6.2); over seeds 5-9 it is 15.1.
- The pooled pC1d/e held-out check fails as the analyst says: 6.20 against 7.55, 3.1 SEM of seeds 0-4, 2.35 SE of the difference, Welch p=0.047. This number was not in the pre-set list (21/19/5.7).
- cVA + touch shows no such drift (7.10 against 6.45).
- Matched null (results_edge/matched-null/matched_f.csv): all 20 output-matched 2-neuron draws give pC1a/b/c, pC1d and DNp37 = 0.00 over 3 seeds each. 'SAG real' gives pC1a 25.2 and DNp37 20.3. This supports the specificity behind the main-text sentence.

On the hum (n=10):
- SAG gives pC1a 19.6 +- 3.4, pC1b/c 17.6 +- 2.8 and vpoEN/DN 5.13 +- 0.88.
- SAG + touch gives pC1d/e 6.12 +- 0.59, against touch alone 0.38 +- 0.27.
- The no-state decider floor is at most 0.45 Hz.
- Hum against silent: p = 0.36 / 0.38 / 0.22 / 0.135. pC1d/e is 0.135, not >= 0.14, which is trivial.
- 3 x 5.13 = 15.4 Hz. The arena hz_accept (DNp37 only) in 10 fly2 virgin-noise0.2 logs is 15.35-16.52, mean 15.88, so they agree.
CORRECTED: Note 6, 10-seed version. Use this only if Note 6 moves to the 10-seed file and paper_numbers.py is pointed at it; otherwise use 12 for pC1d:
"SAG -> pC1a 21, pC1b/c 19 and vpoDN (DNp37) 17 Hz, all from 0; the four vpoEN neurons stay silent, even with song. With touch, pC1d rises from 2 to 14 Hz (touch alone 0) and pC1e stays silent."

Do not write 'the vpoEN neurons that feed vpoDN'. That wiring was not checked here; it comes from Wang et al. 2021, so cite it if kept.

Main text l.97: KEEP.

Notes:
- Virgin state (SAG 30 Hz, 10 seeds, no hum): pC1a 21.2 +- 3.9, pC1b 18.9 +- 3.4, pC1c 18.9 +- 3.3 Hz.
- vpoDN (2 DNp37) 17.2 +- 3.4 Hz; per seed, the faster at 18.6 +- 3.7 and the slower at 15.7 +- 3.2. vpoEN 0.0 in every run. Pooled over all six vpoEN/vpoDN neurons: 5.7 +- 1.1.
- pC1d 2.3 +- 1.4 without touch and 13.8 +- 2.2 with it; pC1e 0.0. Pooled pC1d/e with touch is 6.9 +- 1.1 (6.2 over seeds 0-4, 7.6 over seeds 5-9).
- All of these are 0.0 without the state.
- Seeds 0-4 equal the published file to the digit, and seeds 5-9 reproduce the state-alone values within 0.3 SEM.
- 20 random pairs of central neurons matched to SAG's output drive none of them (0.0).
- With the hum: pC1a 19.6 +- 3.4, pC1b/c 17.6 +- 2.8, pooled vpoEN/vpoDN 5.1 +- 0.9, and pC1d/e with touch 6.1 +- 0.6 Hz (touch alone 0.4). The arena's DNp37 readout gives 15.9 Hz (15.4-16.5, 10 recordings).

>>> CHECK [states] 2. The virgin state at gains 0.7 and 1.4 (S17). Analyst: every criterion passes, no gain window, REWORD with a gain triplet.: agrees=True
OWN: Pre-set criterion (S17): add 'at gains 0.7-1.4' if, at both gains:
- SAG alone gives pC1a >= 5 Hz and vpoEN/DN > 1 Hz;
- SAG + touch gives more pC1d/e than touch alone;
- the no-state deciders stay at 0.0;
- oviDN stays at 0.
A gain window exists if pC1a is below 2 Hz at 0.7.

Run integrity:
- Sidecars show w_syn 0.1925 and 0.385 (0.275 x gain), so the gain was applied. Status ok, 450 rows x 5 seeds each, no NaNs.
- These runs have no reference file, so there is no check.txt.

SAG alone (input 'none'), gain 0.7 / 1.0 (paper file) / 1.4, n=5, mean +- sd:
- pC1a 11.90 +- 3.70 / 21.20 +- 5.62 / 30.30 +- 4.04
- pC1b/c 9.30 +- 3.56 / 19.00 +- 4.64 / 29.30 +- 4.77
- vpoEN/DN 1.60 +- 0.72 / 5.73 +- 1.55 / 11.37 +- 1.43. At 0.7, seeds 1 and 4 are exactly 1.00, so the '> 1 Hz' test passes on the mean only.
- SAG alone also gives pC1d/e 0.00 / 1.20 / 4.90 and aIPg 0 / 0 / 0.14.
- Neurons recruited at 1.4: 789-1,451, against 35-103 at 1.0.

SAG + touch, pC1d/e: 0.15 +- 0.14 (per seed 0.25, 0.25, 0.25, 0, 0) / 6.20 +- 0.97 / 9.15 +- 1.04. Touch alone gives 0.00 at every gain.
- At 0.7 the test passes by the letter on 3 spikes in 5 runs (one-sample p ~ 0.07), so the touch interaction is effectively absent at 0.7.
- At 1.4, touch adds only about 4.3 Hz on top of SAG's own 4.9.

State 'none': every decider (pC1a, pC1b/c, pC1d/e, aIPg, vpoEN/DN) and oviDN is 0.00 in every row at each gain. 'oviDN egg' is 0.00 in all 450 rows at each gain.

No vpoEN/vpoDN split exists at 0.7 or 1.4. DNp37 at about 4.8 / 34 Hz is inferred from 3 x the pooled value, not measured.

Verdict: all criteria pass and there is no gain window (pC1a 11.9 Hz at 0.7), so REWORD is right. 'At gains 0.7-1.4' must not attach to the touch -> pC1d/e clause.
CORRECTED: Note 6:
"At gain 0.7 / 1.0 / 1.4 (5 seeds each), SAG -> pC1a 12 / 21 / 30 Hz, pC1b/c 9 / 19 / 29 Hz and the vpoEN/vpoDN group 1.6 / 5.7 / 11 Hz, all from 0. The boost that touch gives pC1d/e needs gain 1.0 or more: 0.15 / 6.2 / 9.2 Hz with touch, against 0 / 1.2 / 4.9 without it."

The gain triplet stays a 5-seed, pooled pC1d/e number, even if the gain-1.0 line of Note 6 switches to the 10-seed pC1d value.

Main text: the optional 'at every strength of connection I tested' is fine for the deciding neurons and the vpo group. It should not be read as covering the touch interaction.

Notes:
- Gain window (5 seeds per gain): SAG alone gives pC1a 11.9 +- 3.7 / 21.2 +- 5.6 / 30.3 +- 4.0 Hz and pC1b/c 9.3 +- 3.6 / 19.0 +- 4.6 / 29.3 +- 4.8 Hz at gain 0.7 / 1.0 / 1.4.
- vpoEN/vpoDN pooled: 1.6 +- 0.7 / 5.7 +- 1.5 / 11.4 +- 1.4 Hz. No split was run at 0.7 or 1.4.
- pC1d/e is 0 / 1.2 +- 0.9 / 4.9 +- 1.0 without touch and 0.15 +- 0.14 / 6.2 +- 1.0 / 9.2 +- 1.0 with touch. Touch alone gives 0 at each gain.
- Without the state, every decider and oviDN is 0.0 at each gain.

>>> CHECK [states] 3. Hunger/fullness states change nothing specific (l.97 'changes nothing, in either sex'; Note 6 'at most 7 Hz on MN9, as much as unrelated states'). Analyst: REWORD.: agrees=False
OWN: Short answer: REWORD is the right verdict, but the proposed paper wording is too strong in three places.

Pre-set criteria:
- S18: compare NPF's MN9 shift with sugar against the unrelated-state band at n=10 (Welch).
- S19: KEEP if every hunger shift on the hum is within 2 SEM AND inside the band on feed MNs, MN9, DNa L/R, PPL1, PAM and MDN. Qualify the sentence if a shift is larger than about 3 Hz and beyond the band.

S18, silent, n=10, input 'sugar GRNs', column 'MN9' (a single neuron, SHIU_MN9):
- No state 81.90 +- 4.79.
- Hunger states: NPF 85.10 +- 3.28 (+3.20, Welch p=0.10), DH44 +3.5, SIFa +1.5, AstA 0.0, IPC -0.4.
- Unrelated states: SAG +3.5, pC1a-c +0.5, pC1d/e -0.1, aIPg -0.2.
- NPF against the pooled unrelated states: Welch p=0.090, Mann-Whitney 0.148. ANOVA over the 10 states: p=0.43.
- Result: PASS.
- Seeds 0-4 give NPF +6.8 and seeds 5-9 give -0.4. The old unrelated band (+3.6 to +4.4) was also a seeds 0-4 artefact: the no-state value was low there (79.4), and seeds 5-9 give unrelated shifts of -4.6 to +2.6.
- Caveat not reported by the analyst: NPF, SIFa and pC1d/e share the same random numbers (n_driven 4). In a paired test on those shared draws, NPF - pC1d/e = +3.3 Hz, paired p=0.02 uncorrected (0.08 after Bonferroni over the 4 pairs).

Silent, all 810 hunger cells (18 readouts):
- Largest shift: MN9 with cVA + sugar (no state 76.4), SIFa +5.2 (p=0.12) and IPC +4.5 (p=0.03). Unrelated states reach +3.6 there. Against the pooled unrelated states, SIFa p=0.42 and IPC p=0.30; ANOVA p=0.46.
- 10 cells lie beyond the unrelated band by more than 0.5 Hz of shift. Besides the two MN9 cells:
  - feed MNs with cVA + sugar: SIFa +1.71 (p=0.011) against a band maximum of +1.30;
  - touch -> DNp13: IPC +1.35 (p=0.005), AstA +1.05, SIFa +1.00 (p=0.008) and NPF +0.95, against a band maximum of +0.70.
- So 'change no readout more than unrelated states do' is literally false. What holds is that none can be told apart from them.
- 27 of 216 non-constant hunger cells have p < 0.05 against no state, all small, against about 11 expected by chance.
- Largest hunger shift by readout, against unrelated states: DNa 1.7 (16.5), PPL1 0.56 (2.48), MDN 0.10 (0.12), PAM 0.01 (0.03), KC 0.02.
- Recruitment at rest: IPC, DH44, NPF, SIFa and AstA recruit 0 neurons in 10 of 10 seeds. SAG recruits a mean of 55 (35-103), pC1a-c 103 (72-215), pC1d/e 68 (55-90) and aIPg 167 (154-179).

S19, hum, n=10, 315 cells:
- 301 are within 2 SE of the difference (260 if SEM of the no-state mean).
- 247 are strictly inside the band (266 if the band includes 0).
- 238 pass both, so KEEP formally FAILS.
- The qualify trigger fires in 7 cells, all MN9: JO-A with NPF or SIFa +14.3 (band max 14.2); food with DH44 -3.3 (band -3.2); sugar with DH44 +7.6 and SIFa -9.5 (band -7.4 to +7.0); Or47b with DH44 -11.7 and AstA +10.3. Every one has p >= 0.17.
- By the pre-set rule, the sentence must be qualified.

Mitigation, which I verified:
- States with the same number of driven neurons get the same hum draw. Per-seed MN9 correlates at r = 1.00 for NPF, SIFa and pC1d/e, for DH44 and pC1a-c, and for AstA and SAG (with sugar, r = 0.22-0.92).
- Over all 36 paired MN9 cells, the hunger state differs from its same-draw unrelated state by at most 2.1 Hz. IPC has no partner.
- MN9 with no state and no input runs at 1-95 Hz depending on the seed (37.6 +- 39.9). The SE of the difference on MN9 ranges up to 17.2 Hz (median 11.2), so against no state MN9 excludes only shifts above about 20-30 Hz, not 15 as the analyst wrote.
- Excluding MN9, the largest hunger shift is 3.45 Hz (NPF, DNa L with JO-A, p=0.22); unrelated states reach 14.45. Feed MNs 1.57 against 1.56; PPL1 1.20 against 2.42; MDN 0.30 against 0.47; PAM 0.03 against 0.03.
- The 14 cells outside 2 SE are spread over PAM, DNa, feed MNs, PPL1 and MDN, about the 16 expected by chance.

Male (experiments/results/state_probe_malecns_all_min1+eln0.25_state30.csv): sugar -> MN9 is 0.0 and feed MNs are 0.35-0.42 Hz in every state. The male test therefore cannot show a feeding effect, and there is no male hum run.
CORRECTED: Main text l.97:
"Hunger is another matter. Keeping the fly's hunger and fullness neurons firing changes nothing that unrelated states do not change as well (in the female also with background activity, as far as her one erratic feeding motor neuron can show; the male's feeding neurons ignore sugar in any state, so in him the test says little)."

Note 6:
"IPC, DH44, NPF, SIFa and AstA switch on no neuron but their own at rest, and no shift they cause can be told apart from those of the virgin, aroused and aggressive states (10 seeds). With sugar, MN9 moves by -0.4 to +3.5 Hz under them and -0.2 to +3.5 Hz under the unrelated states (NPF against those, p = 0.09). The largest shift is +5.2 Hz, SIFa on MN9 with cVA and sugar (unrelated states +3.6, p = 0.42). With the hum, no other readout moves by more than 3.5 Hz. MN9 flips between about 1 and 95 Hz from one noise draw to the next, and there each hunger state stays within 2.1 Hz of the unrelated state given the same draw."

Notes:
- Silent, 10 seeds: sugar -> MN9 is 81.9 +- 4.8 Hz without a state and 85.1 +- 3.3 under NPF (+3.2, p = 0.10). The earlier +6.8 came from seeds 0-4 (seeds 5-9: -0.4).
- DH44 +3.5, SIFa +1.5, AstA 0.0, IPC -0.4. Unrelated states -0.2 to +3.5 (ANOVA over ten states p = 0.43). Against pC1d/e given the same random numbers, NPF is +3.3 Hz (paired p = 0.02 uncorrected).
- Hunger states exceed the unrelated band by at most 1.6 Hz: MN9 with cVA + sugar +5.2 against +3.6, feed MNs +1.7 against +1.3, touch -> DNp13 up to +1.35 against +0.7. None of these stands out against the pooled unrelated states.
- At rest the five groups recruit 0 neurons in every seed; SAG recruits 35-103, pC1a-c 72-215 and aIPg 154-179.
- Hum, 10 seeds: hunger states move feed MNs by at most 1.6 Hz, DNa by 3.5, PPL1 by 1.2 and MDN by 0.3. Unrelated states move them by 1.6, 14.5, 2.4 and 0.5.
- The pre-set test (every cell within 2 SEM and inside the band) passes in 238 of 315 cells. All 7 cells that call for a qualification are MN9, and each is within 2.1 Hz of its same-draw unrelated state.
- Male: silent only, and sugar does not drive his MN9 in any state.

>>> CHECK [states] 4. DNp13 is state-blind (Note 6 '36 Hz virgin or mated'; main text 'a mated female extends her ovipositor no more often than a virgin'). Analyst: REWORD.: agrees=True
OWN: Pre-set criterion (S18): DNp13 under SAG or pC1a-c within 2 SEM of no state. P2 state-dose (not yet run; no results_edge dir) would qualify the claim on a change > 3 Hz at p < 0.01.

Column 'DNp13 reject', silent, n=10.

With touch (no state 35.95 +- 0.80; SEM 0.25, so the 2-SEM bound is 0.51):
- SAG 36.10 +- 0.74: +0.15 = 0.44 SE of the difference, 0.59 SEM of the no-state mean. PASS.
- pC1a-c 36.65 +- 1.08: +0.70 = 1.65 SE of the difference, 2.78 SEM of the no-state mean; p=0.12.

With cVA + touch (no state 36.90 +- 1.37; the 2-SEM bound is 0.87):
- SAG -0.65 (1.07 SE of the difference, 1.50 SEM).
- pC1a-c -0.95 (1.33 SE, 2.19 SEM).

The criterion's outcome depends on the reading. SAG passes under both. pC1a-c passes if SEM means the SE of the difference and fails narrowly if it means the SEM of the no-state mean: it exceeds the bound by 0.19 and 0.08 Hz. The analyst's 'misses by 0.7-0.95 Hz' misstates this, since 0.7-0.95 are the shifts themselves.

All 9 states fall within -0.95 to +1.35 Hz. The largest shift is IPC +1.35 (p=0.005), and the hunger states cluster at +0.95 to +1.35 with touch.

Hum, n=10:
- Touch, no state 36.55 +- 2.61: SAG -0.85 (p=0.46), pC1a-c -2.30 (p=0.037). All states -2.30 to -0.40.
- cVA + touch: SAG -1.00 (p=0.36), pC1a-c -1.85 (p=0.08).

Gains, touch, n=5:
- 0.7: no state 28.3 +- 1.5; SAG -1.1 (p=0.22).
- 1.0 (paper file): 35.6 +- 1.0; SAG +0.6 (p=0.27); pC1a-c +1.3 (p=0.051).
- 1.4: 41.9 +- 1.9 against SAG 37.9 +- 3.0, -4.0 Hz (Welch p=0.042; 4.75 SEM of the no-state mean). pC1a-c -1.8 (p=0.30). cVA + touch SAG -2.0 (p=0.14).

At 100 Hz state drive (experiments/results/state_probe_flywire_shiu_min1_state100.csv, published smell centre, 3 seeds):
- Touch: none 36.3 (35 / 38 / 36), SAG 32.8 (31 / 35.5 / 32), pC1a-c 29.0 (29.5 / 29.5 / 28).
- The analyst's notes omit this, yet it is what 'at the strength I drove them' rests on.

Split (state_split.csv): DNp13 L 43.2 and R 28.7 with touch alone, against 43.4 and 28.8 with SAG + touch.

oviDN: 0.0 in every silent row (10 seeds, 3 gains). On the hum it is 0.15-0.32 Hz under the states, at the no-state floor of up to 0.25.

Verdict: REWORD is right. The miss holds for the virgin state at 30 Hz and gain <= 1.0, silent or with the hum. At gain 1.4 and at 100 Hz the virgin state lowers DNp13 by about 10 % (the real-fly direction). That is short of the P2 threshold of p < 0.01, but 'at the strength I drove them' does not cover the gain.
CORRECTED: Note 6:
"DNp13 fires at 36 Hz whether or not the virgin neurons are driven at 30 Hz (the undriven brain stands in for a mated female), and oviDN stays at 0 under every state. Stronger settings lower it a little: 41.9 -> 37.9 Hz at gain 1.4 (5 seeds, p = 0.04), and 36.3 -> 32.8 Hz with the virgin neurons at 100 Hz (published smell centre, 3 seeds)."

Main text:
"...and, at the model's standard settings, a mated female extends her ovipositor no more often than a virgin."

Notes:
- Touch -> DNp13 (10 seeds): 36.0 +- 0.8 Hz without a state and 36.1 +- 0.7 with the virgin neurons. Every state stays within 1.4 Hz, the largest shift being IPC's +1.35.
- With the hum, every state stays within 2.3 Hz of 36.6.
- At gain 0.7 / 1.4, the virgin state changes it by -1.1 (p = 0.22) / -4.0 Hz (41.9 +- 1.9 -> 37.9 +- 3.0, 5 seeds, p = 0.04).
- At 100 Hz (published smell centre, 3 seeds), SAG lowers it to 32.8 and pC1a-c to 29.0, from 36.3.
- oviDN is 0.0 in every silent run and at the hum's floor (<= 0.3 Hz) with the hum.

### [persistence] The 1-s-from-rest bench protocol is representative: no drift or latching over 10 s of drive (implicit in every bench number; Notes 4-5).
STEPS: Read S9 in experiments/edge/design_plan.md (l.143-151), DECISIONS.md item 5, design_critique.md items 6-7, and grid_probe.py (persistence preset l.415-418, run_drive bins protocol l.661-709, persistence_checks l.889-933). Loaded experiments/results_edge/persistence/persistence_g1.csv (520 rows = 10 drives x 2 seeds x 26 bins). For each drive and each of the 18 HEADLINE readouts I took three means: the seed-mean of each 1-s bin from 1 to 10 s, the time-weighted mean over 0-1 s (ten 100-ms bins) and the same over 0-0.6 s. From these I computed: the range of the bin means; the pre-set tolerance max(10 %, 2 x mean across-seed SD) without the code's 0.5 Hz floor; a linear slope with SE over all 18 points; and the counting-noise range expected from the within-seed SD of the 1-s bins (2.97 x wsd / sqrt 2). Scratch scripts not kept. (table: drift_table.csv), traj.py.
CRITERION: S9 (design_plan l.147-151) as amended by DECISIONS 5. For the sensory drives, the 1-s bins 2-10 lie within max(10 %, 2 seed-SD) of each other with no trend, and the 0-1 s mean is within 10 % of the 1-10 s mean for every headline readout. Pre-set consequence of a failure: 'Drift or latching: quote the numbers as 1-s responses from rest.' grid_probe also applies an undeclared 0.5 Hz floor (DRIFT_FLOOR_HZ).
NUMBERS: File experiments/results_edge/persistence/persistence_g1.csv, readout columns = group mean rate, 2 seeds (0, 1), gain 1, shiu_min1+known+eln0.25. Values are 0-1 s vs 1-10 s means (per-seed values in brackets).

Sensory drives:
- Touch -> 'DNp13 reject': 36.50 (37.0, 36.0) vs 37.08 (36.78, 37.39), -1.6 %. 'feed MNs' +0.5 %. 'DN all' 0.0 %.
- Pheromones + song + touch -> DNp13: 35.25 vs 35.03, +0.6 %. DNa L/R stay 0.14/0.08 Hz for all 10 s, so the freeze holds.
- JO-A -> 'GF jump': 10.75 (10.5, 11.0) vs 11.53 (11.61, 11.44), -6.7 %.
- JO-B -> GF: 5.00 vs 5.61, -10.9 %.
- Sugar -> MN9: 77.0 (74, 80) vs 85.1 (87.4, 82.7), -9.5 %. 'feed MNs' 23.6 (22.0, 25.3) vs 26.7 (27.0, 26.4), -11.4 %.
- Food odour -> DNa L/R: 23.5/14.25 vs 23.3/17.1 (DNa R -16.7 %). PPL1 17.2 vs 18.6, -7.4 %.
- cVA -> DNa L/R: 10.0/9.0 vs 10.5/10.3 (DNa R -12.9 %). PPL1 5.97 (5.56, 6.38) vs 7.15 (7.08, 7.22), -16.5 %.
- 0-0.6 s windows sit further below: JO-B GF 3.75 (-33 %), cVA PPL1 5.26 (-26 %), JO-A GF 9.58 (-17 %), cVA DNa 8.75/8.75 (-16 %).

Drift after the first second:
- No trend in any of these drives: every slope is within 1.9 SE of zero, and the trend over 8 s is at most 1.1 Hz (MN9 2.1 Hz).
- The formal drift failures (cVA DNa L, cVA PPL1, food GF, JO-A GF, JO-B GF, sugar MN9) are range failures on 1-2-neuron readouts. Observed ranges are 0.65-1.27x the range expected from counting noise.
- The first-second shortfalls are systematic: responses ramp up over 0.1-0.4 s. For example, cVA total rate is 15-21k spikes/s in 0-100 ms against about 63k steady, and sugar feed MNs are 13.7-21 Hz in 0-400 ms.

Latching:
- 'Or47b (VA1v)@90 & CO2 (V)@3': 0 in every headline for 0-1 s. The 1-2 s bin reaches 13.5k and 22.0k spikes/s (9k before). It then latches into the self-sustained state: over 1-10 s DNa L/R 7.08/10.92, GF 3.22, PPL1 4.08 Hz, against 0/0/0/0 in 0-1 s.
- Hum 0.2 Hz: 0-1 s vs 1-10 s gives DNa L/R 9.25/9.75 vs 19.11/21.58, MN9 13.0 vs 86.7, PPL1 4.59 vs 8.90.
- Hum 0.05 Hz: MN9 1.0 vs 70.1; DNa 1.75 vs 6.0.
- The hum 0.2 values over 1-10 s match the paper's experiments/results/noise_floor_flywire_shiu_min1+known+eln0.25_10s.csv row none@0.2 (DNa 19.3/20.8 and 17.0/20.0; MN9 66/93; PPL1 9.0/8.0).

Failure counts: 68 of 180 readout-drive cells fail the pre-set criterion strictly. 32 fail with the code's floor, and the JSON reports drift_fails = 23.
VERDICT REWORD
PAPER: Every number from the bench is the response to the first second (or 0.6 s) of an input given to a brain at rest. Held for ten seconds, these responses do not drift, and they rise by at most a sixth, except where a smell tips the brain into the self-sustaining state described below (Note 1).
NOTES: Bench numbers are mean rates over the first 0.6 s (gain sweep, sensitivity, contact and freeze) or 1 s (social probe, states) of an input given to a brain at rest. Over 10 s (2 seeds, 1-s bins) they do not drift after the first second: every slope is within 1.9 SE of zero. Several responses build up over the first 0.1-0.4 s, so the short windows sit 0-17 % below the 10-s level (0-1 s against 1-10 s):
- touch -> DNp13 36.5 against 37.1 Hz;
- pheromones + song + touch -> DNp13 35.3 against 35.0, with DNa at 0.1 Hz throughout;
- JO-A -> GF 10.8 against 11.5;
- JO-B -> GF 5.0 against 5.6;
- sugar -> MN9 77 against 85, feed MNs 23.6 against 26.7;
- food odour -> DNa L/R 23.5/14.3 against 23.3/17.1, PPL1 17.2 against 18.6;
- cVA -> DNa L/R 10.0/9.0 against 10.5/10.3, PPL1 6.0 against 7.2.
Over 0-0.6 s the shortfall reaches 33 % (JO-B -> GF 3.8 Hz).

The exception is Or47b at 90 Hz with CO2 at 3 Hz. It drives nothing for the first 1-2 s and then switches on the self-sustained state (Note 5): over 1-10 s, DNa L/R 7.1/10.9, GF 3.2 and PPL1 4.1 Hz.

On the hum the first second is not representative. At 0.2 Hz, DNa L/R are 9.3/9.8 Hz in the first second against 19.1/21.6 over 1-10 s, and MN9 13 against 87 Hz.

### [persistence] After the drive is switched off, activity dies away: act_n == 0 at the END of the 3-s off phase, with no self-sustained activity.
STEPS: From the off-phase rows (phase=='off', four 50-ms bins then 1000/1000/800-ms bins, noise_now 0 in every row), I recorded per run:
- the last bin with total_spikes > 0;
- the first bin boundary with act_n_end == 0;
- the last-bin act_n_end and total_spikes;
- active neurons (active_frac x 139,248).
For runs still active I computed time-weighted readout means over off bins 4-6 (0.2-3.0 s after offset) and the change in rate across those bins. I cross-checked against experiments/results_edge/persistence/persistence_g1_persistence.csv (silent_at_end column) and the log logs/edge/guarded_persistence-female.out. I confirmed the drive is really removed: DNp13 goes from 35 to 0 Hz after the pheromone+song+touch offset, and touch/JO/sugar fall silent within 50-100 ms. Scripts not kept., state.py.
CRITERION: DECISIONS 5 (amending S9 bullet 3, per critique item 7): act_n_end == 0 and no spike in the last off bin (12.2-13.0 s). A pass means no self-sustained activity. Pre-set consequence of persistence after offset: 'say the model is history-dependent.'
NUMBERS: Source columns: persistence_g1.csv act_n_end, total_spikes, active_frac and the readouts. Silent at the end: 4 of 8 noise-0 drives. Self-sustained: 4 of 8 (n = 8 runs), and these are exactly the drives that contain a smell.

Silent drives:
- Touch, JO-A, JO-B and sugar each leave their last spike in the first 50-ms bin (sugar seed 0 in the second bin, 21 spikes).
- act_n is 0-67 neurons at 0.2 s and 0 by 1.2 s.

Self-sustained drives (cVA, food odour, pheromones + song + touch, Or47b@90 + CO2@3):
- Last bin: 44,412-47,777 spikes in 0.8 s; act_n_end 48,141-52,449.
- Over 0.2-3.0 s after offset (n = 8): 58,304 +- 507 spikes/s from 1,978 +- 17 active neurons; act_n at 3.0 s 50,520 +- 1,838.
- No decay: the change from off bin 4 to off bin 6 is -5.5 to +2.3 %.
- Readouts: DNa L 15.96 +- 1.72, DNa R 17.97 +- 1.41, GF jump 3.08 +- 0.43, PPL1 8.72 +- 0.29, aSP22 10.69 +- 0.78, oviIN 9.08 +- 0.81, MBON 1.62 +- 0.08, KC 0.14 +- 0.01, DN all 1.81 +- 0.03, PAM 0.02.
- Exactly 0: DNp09, MDN, DNp13, MN9, feed MNs, pC1a-e, aIPg, vpoEN/DN, oviDN, mAL, SAG, IPC.
- The state is the same whichever smell set it off (SD across runs about 1 %).
- Through motor.py (forward = mean of DNp09 x2 + DNa01/02 x4, k_walk 10 Hz) this state gives walk = 1 - exp(-1.13) = 0.68.

The grid_probe summary 'spikes stop 3000 ms after offset' means spikes are still present in the last bin.
VERDICT CHANGE
PAPER: A smell leaves this brain running. After ten seconds of any smell, about 2,000 neurons, the steering neurons among them, kept firing for at least three seconds after the smell was taken away. Touch, sound and sugar left nothing behind within a tenth of a second. The model therefore depends on what it sensed before, not only on what it senses now.
NOTES: Persistence (10 s of input, then 3 s with no input and no hum; 2 seeds; my version of the model, known signs and eLN x 0.25, gain 1):

Touch, JO-A, JO-B and sugar at 100 Hz leave no spike after 50-100 ms, and every neuron is back at rest by 1.2 s.

Every input containing a smell (cVA, food odour, pheromones + song + touch, Or47b at 90 Hz + CO2 at 3 Hz) leaves the same self-sustained state, with no decay over the 3 s (n = 8 runs):
- 58,300 +- 500 spikes/s from 1,978 +- 17 neurons;
- DNa L/R 16.0 +- 1.7 / 18.0 +- 1.4 Hz;
- GF 3.1 +- 0.4, PPL1 8.7 +- 0.3, aSP22 10.7 +- 0.8, oviIN 9.1 +- 0.8, MBON 1.6, KC 0.14, all DNs 1.8 Hz;
- DNp09, MDN, DNp13, MN9, feed MNs, pC1a-e, aIPg, vpoEN/DN and oviDN at 0.
Through the arena's decoder that DNa rate would walk about two-thirds of the time.

How long the state lasts beyond 3 s, and whether it exists under the published signs or at other gains, was not tested.

### [persistence] After the hum is switched off, the brain falls silent: the hum is only a transient drive.
STEPS: Hum rows in persistence_g1.csv: 'none (hum 0.05 Hz, off at offset)' and 'none (hum 0.2 Hz, off at offset)'. The hum ran for 10 s and noise_now = 0 in the off phase. For each run I found the on-phase time at which the total rate jumps to the self-sustained level, profiled the off phase as above, and compared the on-phase 1-10 s levels with the paper's 10-s noise-floor file experiments/results/noise_floor_flywire_shiu_min1+known+eln0.25_10s.csv.
CRITERION: S9 bullet 4 as amended by DECISIONS 5: the brain is silent (act_n == 0 and no spike) at the end of the 3-s off phase after the hum is removed. The original S9 wording asked for silence within 100 ms.
NUMBERS: 0 of 4 hum runs fall silent.

Large self-sustained state (n = 3: 0.05 Hz seed 0, 0.2 Hz seeds 0 and 1):
- Onset: at 0.2 Hz at about 0.3 s (seed 0; 74.6k spikes/s in the 0.3-0.4 s bin) and about 0.9-1.0 s (seed 1). At 0.05 Hz at about 4.5 s (seed 0; the 4-5 s bin reaches 28.3k, then 66k).
- 0.2-3.0 s after the hum is off: 60,265 +- 166 spikes/s from 2,006 +- 16 neurons; act_n_end 50,555-51,948.
- Readouts: DNa L/R 18.04 +- 1.24 / 19.11 +- 1.25, MN9 101.2 +- 0.4, feed MNs 6.05 +- 0.03, PPL1 8.85 +- 0.31, GF 2.56 +- 0.21 Hz.
- Change across the off bins: -1.0 to +5.4 %.

Small loop (n = 1: 0.05 Hz seed 1, which never entered the large state):
- A loop switched on at about 5 s (MN9 95 Hz in the 5-6 s bin) and runs on with no input: 1,896 spikes/s from 33 neurons, act_n 1,210, MN9 104 Hz, feed MNs 6.2 Hz (about 3 of 52 MNs), DN all 0.23 Hz.
- Sugar at 100 Hz drives MN9 to 85 Hz but does not latch this loop: MN9 is 0 within 100 ms of offset.

While the hum is on, MN9 flips between about 0 and about 100 Hz (0.2 Hz seed 0: 99, 10, 1, 44, 101 Hz in seconds 6-10).

The paper's hum floor (10-s file, none@0.2: DNa 19.3/20.8 and 17.0/20.0, PPL1 9.0/8.0, GF 2.3/3.1, MN9 66/93) is this self-sustained state.
VERDICT CHANGE
PAPER: For l.101, after 'it is my addition, and I measured what it does on its own': 'It does more than add noise. Within about a second it tips the brain into a state that keeps itself going, with the steering neurons at about 20 spikes a second and the neuron that works the mouthparts at about 100, and the brain stays in that state after the hum is switched off.'
NOTES: The hum (0.05 or 0.2 Hz on every neuron for 10 s, then off; 2 seeds each) never leaves the brain silent.

At 0.2 Hz it switches on the self-sustained state (Note 5) after 0.3 and about 1 s; at 0.05 Hz after about 4.5 s in one seed. Three seconds after the hum is removed, those three runs still fire:
- 60,300 +- 200 spikes/s from 2,006 +- 16 neurons;
- DNa L/R 18.0/19.1 Hz, MN9 101 Hz, feed MNs 6.1 Hz, PPL1 8.9 Hz, GF 2.6 Hz.

The fourth run (0.05 Hz, seed 1) switched on only a 33-neuron loop at about 5 s. That loop keeps MN9 at 104 Hz with no input; sugar does not switch it on.

The hum floors (DNa about 20 Hz, PPL1 about 9 Hz, MN9 66-93 Hz at 0.2 Hz, 10-s file) are therefore mostly this self-sustained state rather than a direct effect of the input.

### [persistence] 'The published model has no activity of its own' (l.95; also l.125 'every neuron at rest', l.123 'it does not hold a reason to walk'). True by construction for the neurons.
STEPS: Per DECISIONS 5 the zero-input check was not run, because it cannot fail. I confirmed by construction:
- brain/flybrain/lif.py: v_rest = v_reset = -52 mV, threshold -45 mV, noise_hz default 0, no bias current;
- the paper's zero-input rows: social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv input 'none' has total_spikes 0 in seeds 0-4; noise_floor_flywire_shiu_min1+known+eln0.25.csv input 'none' at noise 0 has 0 in seeds 0-2.
I then combined this with the S9 persistence results for claims 2-3 to test whether the network, once started, runs without input. I also checked which model variant was tested: the sidecar persistence_g1.json gives FLYBRAIN_SIGNS=known and FLYBRAIN_ELN=0.25, the same variant as the clean-box logs.
CRITERION: DECISIONS 5 / critique item 6. 'No activity of its own' holds by construction for the neuron model and is to be stated as a property of the model, not as a result. The part that can fail is self-sustained activity after input is removed (act_n == 0 at the end of the off phase). On failure: 'say the model is history-dependent.'
NUMBERS: By construction: 0 spikes with no input (social_probe 'none' 5/5 seeds, noise_floor 'none'@0 3/3 seeds).

Self-sustained network activity after input is removed:
- 8/8 smell runs and 3/4 hum runs enter one state: 58,839 +- 1,012 spikes/s from 1,986 +- 20 neurons (n = 11), with DNa L/R 16.5 +- 1.8 / 18.3 +- 1.4 Hz and GF 2.9 +- 0.5 Hz. It is unchanged over 3 s.
- The remaining hum run keeps a 33-neuron loop with MN9 at 104 Hz.
- 0/8 runs of touch, sound or sugar persist.

The variant tested is the author's (shiu_min1 + known signs + eLN x 0.25), not the published Shiu-sign model, which was not tested for persistence (persistence-gain1.4 was dropped to P3).

The clean-box females (10 logs of 135 +- 6 s) never entered the state: every readout was 0.00.
VERDICT REWORD
PAPER: l.95: 'The model cannot start walking by itself either. In a clean box with no flowers, two simulated females stood still for more than two minutes of brain time. Light and the other fly's smell kept about 8 % of their neurons firing, but none of it reached a descending neuron. The model's neurons have no activity of their own, so a brain that starts at rest stays still until something reaches its central neurons. Once a smell or the hum has done so, my version of the brain keeps going by itself: about 2,000 neurons, the steering neurons among them, fire on for at least three seconds after every input stops. A real fly put in an empty dish soon starts walking about \citep{martin2004portrait}. Starting to walk unprompted, the most ordinary thing a fly does, was the first behaviour on my list that this model does not produce.'

l.125: replace 'every neuron at rest' with 'with only their eyes firing'.

l.123: replace 'it does not hold a reason to walk' with 'it does not hold a reason to start walking'.
NOTES: No activity of its own is a property of the neuron model, not a finding. Rest and reset are at -52 mV, threshold at -45 mV, and there is no intrinsic current and no noise unless the hum is on. A brain with no input therefore never spikes: the 'none' rows give 0 spikes in 5 and 3 seeds.

The network is not inert once started. In my version (known signs, eLN x 0.25), 10 s of any smell at 90-100 Hz (8/8 runs) or of the hum (3/4 runs) leaves about 1,990 neurons firing on their own:
- 58,800 +- 1,000 spikes/s (n = 11);
- DNa L/R 16.5/18.3 Hz, GF 2.9 Hz;
- no decay over the 3 s measured.
The fourth hum run keeps a 33-neuron loop with MN9 at 104 Hz.

Touch, sound and sugar leave nothing. The published-sign model was not tested. The clean-box pairs never entered this state.

RUN PROBLEMS [persistence]: The run is sound. No sign that it is broken:
- 520 rows = 10 drives x 2 seeds x 26 bins. The sidecar persistence_g1.json shows FLYBRAIN_SIGNS=known, ELN 0.25, NUMBA_NUM_THREADS 6, 6 chunks.
- The first second of the 7 drives that overlap the paper reproduces experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv seeds 0-1 to the digit: 336/336 readout cells, total_spikes and n_driven exact, max |diff| 3.6e-15. So ten 100-ms runs equal one 1-s run.
- The hum-0.2 on-phase matches the paper's 10-s noise-floor file.
- In the off phase noise_now is 0 in every row, and drive removal works (touch, JO-A/B and sugar silent within 50-100 ms; DNp13 goes from 35 to 0).
- The self-sustained activity is therefore a property of the model (known+eln0.25), not an engine bug.

Check files:
- There is no .check.txt for this step: the S9 command has no --check-against, so my manual reproduction above replaces it.
- The other production check files show 0 mismatches: ei-deciders (405 cells), state-split (1035 cells), sensmap (all conditions).
- The mismatches under experiments/results_edge/_smoke/ are expected or superseded: expression_harsh _all was run at --ms 200 against a 1000-ms reference; the conditioning cyc1 file is labelled 'a mismatch is expected'; grid_probe_review/sens2_before has 1 SD mismatch (JO-B GF sd 1.14 vs 1.27) that the production sensmap no longer shows.

Weaknesses in the checker (not in the simulation):
1. The drift tolerance max(10 %, 2 x mean 2-seed SD) is too tight for the range of 9 bins. It fails under pure counting noise on 1-2-neuron readouts; observed ranges are 0.65-1.27x the noise expectation. So the reported drift_fails = 23 overstates drift. No sensory drive has a trend.
2. grid_probe adds a 0.5 Hz floor (DRIFT_FLOOR_HZ) that the design does not have.
3. The summary line reports the maximum act_n over seeds, which hides that hum 0.05 seed 1 is in a small 33-neuron MN9 loop rather than the large state. 'spikes stop 3000 ms after offset' actually means spikes are still present in the last bin.

Scope limits: 2 seeds, gain 1, the author's variant only. The published-sign model and gain 1.4 (persistence-gain1.4, dropped to P3) were not run. The off phase is only 3 s, so how long the state lasts is unknown (no decay seen).

Knock-on effects for claims outside this step, worth checking:
- (a) Any 100-Hz odour ignites the self-sustained state within 0.1-0.2 s (cVA 15-21k spikes/s in 0-100 ms, then about 63k). The bench odour rows for DNa, PPL1, GF, aSP22 and oviIN are therefore largely the state's odour-independent signature (state alone: DNa about 17, PPL1 about 9, GF about 3 Hz). Odour-specific claims (cVA or food steering, odour -> PPL1, the freeze baseline under cVA or food) should be read against it.
- (b) On the hum MN9 sits near 100 Hz with no sugar and flips on and off. Any MN9 reading made on the hum (S19 hunger-on-hum, feeding in the arena) sits on that floor.
- (c) The hum's 'walking' is this self-sustained state, which persists without the hum.

Scratch scripts not kept. (repro.py, drift.py, drift_table.csv, off.py, state.py, traj.py).

>>> CHECK [persistence] 1. The 1-s-from-rest bench protocol is representative: no drift or latching over 10 s of drive (analyst verdict REWORD).: agrees=False
OWN: VERDICT: REWORD is correct, but the proposed paper wording is wrong in two places, 'rise by at most a sixth' and 'except where a smell tips...'.

Pre-set criterion: S9 as amended by DECISIONS 5. It fails. With the design's tolerance max(10 %, 2 x mean seed-SD) and no floor, 68 of 180 drive x HEADLINE cells fail. With grid_probe's undeclared DRIFT_FLOOR_HZ = 0.5, 32 fail. JSON drift_fails = 23 counts only drift_ok (range/trend) failures; the 26 first-second failures are left out, and together they make 32. Most of the 68 are ~0 Hz readouts. For the 7 non-latching drives, 11 of the 21 readouts at 1 Hz or more fail: 7 on range/trend and 6 on the first second (some fail both).

Engine check. There is no .check.txt for S9 because the step ran without --check-against, so I checked it myself. All three match to the digit:
- 0-1 s, seeds 0-1, all 7 matching drives = social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv (total_spikes identical, readouts within 7e-15).
- 0-0.6 s = gain_sweep_flywire_shiu_min1+known+eln0.25.csv, gain 1.0, seeds 0-1.
- Hum 0.2, 0-10 s = noise_floor_..._10s.csv none@0.2 (853,569 and 802,498 spikes).
The run is not broken.

File persistence_g1.csv (520 rows, seeds 0-1, gain 1, female, known signs + eLN x 0.25). Each pair is 0-1 s vs 1-10 s:
- touch -> DNp13: 36.50 vs 37.08.
- PST -> DNp13: 35.25 vs 35.03. DNa L/R are 1.0/0.25 Hz in 0-1 s, then 0.14/0.08, so 'DNa 0.1 Hz throughout' is not exact.
- JO-A GF: 10.75 vs 11.53.
- JO-B GF: 5.00 vs 5.61.
- sugar: MN9 77.0 vs 85.06; feed MNs 23.64 vs 26.70.
- food: DNa L/R 23.5/14.25 vs 23.31/17.11; PPL1 17.22 vs 18.60.
- cVA: DNa L/R 10.0/9.0 vs 10.47/10.33; PPL1 5.97 vs 7.15; DN all 1.69 vs 1.90.

The largest shortfall is -16.7 % (food DNa R), which is a RISE of +20 %, not 'a sixth'.

0-0.6 s, same seeds: JO-B GF 3.75 (-33 %, rise +50 %), cVA PPL1 5.26 (-26 %, +36 %), cVA DN all -20 %, JO-A GF 9.58 (-17 %, +20 %), cVA DNa 8.75/8.75 (-16/-15 %), food DNa R -15 %, sugar feed MNs -14 %, MN9 -11 %.

Signs: among readouts of 1 Hz or more in the sensory drives, 15 of 21 shortfalls are negative; the 5 positive ones are +0.4 to +0.8 %. So the ramp is systematic, except for touch (~0).

No drift after 1 s:
- For readouts of 1 Hz or more, the max |slope/SE| is 1.89 (food PPL1). cVA KC reaches z = 2.4, but only at 0.002 Hz/s.
- The 8-s trend is at most 1.10 Hz (JO-A GF); sugar MN9 is 2.13 Hz.
- The six substantive range failures (cVA DNa L, cVA PPL1, food GF, JO-A GF, JO-B GF, sugar MN9) are 0.90-1.19x the range expected from counting noise, not 0.65-1.27. PPL1 is a 16-neuron readout, not a 1-2-neuron one.
- The analyst's 'sugar feed MNs 13.7-21 Hz in 0-400 ms' is seed 0 only; seed 1 is 16.9-28.1.

What the analyst missed: every smell drive is in the self-sustained state almost from the start.
- cVA recruited spikes: 4.4k/10.4k per s in 0-0.1 s, 34-54k by 0.1-0.2 s, then about 53k.
- Food: 47-49k already in 0-0.1 s.
- In the 1-s on-bins, 1,876 (cVA), 1,944 (food) and 1,869 (Or47b+CO2) non-driven neurons fire, against 1,985-2,008 after offset.
- So the smell bench numbers are read in that state. The true exceptions are Or47b@90+CO2@3 (0 in every headline readout in 0-1 s; the state starts in the 1-2 s bin; 1-10 s DNa 7.08/10.92, GF 3.22, PPL1 4.08) and the hum (0.2 Hz: DNa 9.25/9.75 vs 19.11/21.58, MN9 13.0 vs 86.7).

Window scope is wider than 'first second (or 0.6 s)':
- odour code 0.5 s;
- gain sweep, sensitivity, contact_stop 0.6 s;
- shuffle nulls 0.8 s;
- social/state/noise-floor/odor_dose/expression 1 s;
- precontact_dose 2 s after a 2-s settle;
- conditioning uses 10-s cycles.

The freeze holds at 10 s on the hum (10-s file, food vs food+touch): index 0.69 and 0.75.
CORRECTED: PAPER: "Every reflex and probe number from the bench is the mean over the first 0.5 to 1 s of an input given to a brain at rest. Held for ten seconds, none of them drifts after the first second. Most build up over the first few tenths of a second, so the 1-s numbers sit up to a sixth below the level they settle at, and the 0.6-s numbers up to a third below it. Smells are read in the self-sustaining state described below, which cVA and a food odour switch on within a fifth of a second (Note 5). Two inputs are exceptions. A weak fly odour switches that state on only after one to two seconds, and the hum's first second is not representative (Note 1)."

NOTES: "Bench windows are measured from rest:
- 0.5 s for the odour code;
- 0.6 s for the gain sweep, sensitivity and freeze;
- 0.8 s for rewired brains;
- 1 s for the probes, states and doses;
- learning uses 10-s cycles.

Over 10 s of drive (female, known signs, eLN x 0.25, gain 1, seeds 0-1, 1-s bins), nothing drifts after the first second. Every slope of a readout above 1 Hz is within 1.9 SE of zero, and no trend exceeds 1.1 Hz over 8 s (MN9 2.1 Hz). Most responses build up over 0.1-0.4 s.

0-1 s against 1-10 s:
- touch -> DNp13 36.5 against 37.1 Hz;
- pheromones + song + touch -> DNp13 35.3 against 35.0, with DNa at most 1 Hz (0.1 Hz after the first second);
- JO-A -> GF 10.8 against 11.5;
- JO-B -> GF 5.0 against 5.6;
- sugar -> MN9 77 against 85, feed MNs 23.6 against 26.7;
- food odour -> DNa L/R 23.5/14.3 against 23.3/17.1, PPL1 17.2 against 18.6;
- cVA -> DNa L/R 10.0/9.0 against 10.5/10.3, PPL1 6.0 against 7.2.

Over 0-0.6 s: JO-A -> GF 9.6, cVA -> DNa 8.8/8.8 and PPL1 5.3, JO-B -> GF 3.8 Hz (up to 33 % below).

While cVA, the food odour or the pheromone mix is on, about 1,900 neurons fire within 0.1-0.3 s. These are the same neurons that run on after the smell is removed (Note 5), so smell numbers are read in that state.

Or47b at 90 Hz with CO2 at 3 Hz drives nothing in the first second. It switches the state on between 1 and 2 s: over 1-10 s, DNa L/R 7.1/10.9, GF 3.2 and PPL1 4.1 Hz.

On the hum the first second is not representative. At 0.2 Hz, DNa L/R are 9.3/9.8 Hz in the first second against 19.1/21.6 over 1-10 s, and MN9 13 against 87 Hz. The 10-s hum file is exactly the first 10 s of this run."

>>> CHECK [persistence] 2. After the drive is switched off, activity dies away (act_n == 0 and no spike at the end of the 3-s off phase) (analyst verdict CHANGE).: agrees=False
OWN: VERDICT: CHANGE is confirmed, and every number was reproduced exactly. The paper wording is TOO STRONG in 'After ten seconds of any smell'.

Pre-set criterion: DECISIONS 5 (act_n_end == 0 and no spike in the last off bin, 12.2-13.0 s). On failure, 'say the model is history-dependent'. The criterion fails for 4 of 8 noise-0 drives. persistence_g1_persistence.csv silent_at_end agrees.

Silent drives:
- Touch, JO-A and JO-B spike only in off bin 0 (296/236, 3/3 and 5/16 spikes).
- Sugar spikes 368/95 in bin 0, plus 21 spikes in 50-100 ms for seed 0.
- act_n_end: 0 at 0.15-0.2 s for JO-A/B; 5-67 at 0.2 s for touch and sugar; 0 by 1.2 s.

Smell drives (cVA, food, PST, Or47b@90+CO2@3):
- Last bin 44,412-47,777 spikes in 0.8 s; act_n_end 48,141-52,449.
- Over 0.2-3.0 s, n = 8: 58,304 +- 507 spikes/s from 1,978 +- 17 neurons; act_n at 3.0 s 50,520 +- 1,838.
- Change from off bin 4 to off bin 6: -5.5 to +2.3 %.
- DNa L 15.96 +- 1.72, DNa R 17.97 +- 1.41, GF 3.08 +- 0.43, PPL1 8.72 +- 0.29, aSP22 10.69 +- 0.78, oviIN 9.09 +- 0.81, MBON 1.62 +- 0.08, KC 0.14, DN all 1.81 +- 0.03, PAM 0.02.
- Exactly 0 in all 8: DNp09, MDN, DNp13, MN9, feed MNs, pC1a-e, aIPg, vpoEN/DN, oviDN, mAL, SAG, IPC.
- Walk duty (motor.py, the 6-neuron DNp09+DNa01/02 group, k 10 Hz): 1 - exp(-11.31/10) = 0.68. 'walk' is a duty cycle, so 'two-thirds of the time' is correct.

Why the wording is too strong:
(a) 'After ten seconds' misattributes the cause. The state starts while the smell is on: cVA within 0.1-0.2 s, food within 0.1 s, Or47b+CO2 in the 1-2 s bin.
(b) 'Any smell' is not supported. Persistence was tested for only 4 smell-containing drives. In the 1-s social_probe file (5 seeds), Or47b alone at 100 Hz (total ~9.6k, 0/5), Or47b+song, Or47b+touch and cVA+touch (0/5) never reach the state. CO2, Or83c, Or88a, aversive, cVA, cVA-long, food and all pheromone ORNs do (5/5).
(c) The clean-box females smelled each other at a median of obs 0.207 x 150 Hz = 31 Hz Or47b and about 0.9 Hz CO2, and never entered the state in 135 s. This is consistent with the S9 drive of 90/3 Hz needing 1-2 s, so it is not a contradiction.

Only the female was tested, at gain 1, under known signs + eLN x 0.25. The grid_probe label 'spikes stop 3000 ms after offset' means the brain is still firing at the end.
CORRECTED: PAPER: "A smell leaves this brain running. Each of the four smells I tried switched on, while it was still present, firing that keeps itself going in about 2,000 neurons, the steering neurons among them. cVA and a food odour did so within a fifth of a second, and a weak fly odour after one to two seconds. When the smell was taken away after ten seconds, that firing went on unchanged for the three seconds I watched. Touch, sound and sugar left nothing behind within a tenth of a second. The model therefore depends on what it sensed before, not only on what it senses now."

NOTES: "Persistence (female, known signs, eLN x 0.25, gain 1; 10 s of input, then 3 s with no input and no hum; 2 seeds each):

Touch, JO-A, JO-B and sugar at 100 Hz leave no spike after 50-100 ms, and every neuron is back at rest by 1.2 s.

Each smell-containing input (cVA, food odour, pheromones + song + touch, Or47b at 90 Hz + CO2 at 3 Hz) leaves the same self-sustained state, with no decay over 3 s (n = 8 runs):
- 58,300 +- 500 spikes/s from 1,978 +- 17 neurons;
- DNa L/R 16.0 +- 1.7 / 18.0 +- 1.4 Hz;
- GF 3.1 +- 0.4, PPL1 8.7 +- 0.3, aSP22 10.7 +- 0.8, oviIN 9.1 +- 0.8, MBON 1.6, KC 0.14, all DNs 1.8 Hz;
- DNp09, MDN, DNp13, MN9, feed MNs, pC1a-e, aIPg, vpoEN/DN and oviDN at 0.
Through the arena's decoder that DNa rate gives a walking duty of 0.68.

The state is already present during the smell: about 1,900 non-driven neurons fire within 0.1-0.3 s of cVA or food odour, and within 1-2 s of Or47b + CO2.

Not every smell switches it on. Over 1 s (5 seeds), Or47b alone at 100 Hz and cVA + touch never did, and the clean-box partner odour (Or47b about 31 Hz, CO2 about 1 Hz) never did in 135 s.

Not tested: how long the state lasts beyond 3 s, and whether it exists in the male, under the published signs or at other gains."

>>> CHECK [persistence] 3. After the hum is switched off, the brain falls silent: the hum is only a transient drive (analyst verdict CHANGE).: agrees=True
OWN: VERDICT: CHANGE is confirmed, and the paper wording is essentially right. The Notes wording MISIDENTIFIES the state, and a few details are off.

Pre-set criterion: S9 bullet 4 as amended by DECISIONS 5, silence at the end of the off phase. 0 of 4 hum runs are silent. act_n_end is 50,555, 1,210, 51,576 and 51,948; last-bin spikes are 48,407, 1,517, 48,292 and 49,640 in 0.8 s.

Missed point: the hum state is NOT the smell state of claim 2. It is that state plus a separate MN9 loop.
- Hum, 3 runs, 0.2-3.0 s after offset: 60,265 +- 166 spikes/s from 2,006 +- 16 neurons; DNa 18.04 +- 1.24 / 19.11 +- 1.25; MN9 101.2 +- 0.4; feed MNs 6.05 +- 0.03; PPL1 8.85 +- 0.31; GF 2.56 +- 0.21.
- Smell, 8 runs: 58,304 spikes/s from 1,978 neurons, with MN9 = 0 and feed MNs = 0.
- The differences (+1,961 spikes/s, +28 neurons) match the stand-alone loop in hum 0.05 seed 1: 1,896 spikes/s from 33 neurons, MN9 104.3, feed MNs 6.23, DN all 0.23, act_n 1,210.
- The MN9 loop is present in 4 of 4 hum runs. The big state is present in 3 of 4.

Onsets differ between the two components.
- MN9 loop: 0.2 Hz at about 0.75 s (seed 1; MN9 100 Hz in 0.8-0.9 s) and about 0.95 s (seed 0); 0.05 Hz at about 2.6 s (seed 0; 39 Hz in the 2-3 s bin) and about 5.0 s (seed 1; 95 Hz in the 5-6 s bin).
- Big state (recruited spikes): 0.2 Hz at 0.3 s (seed 0; 74.6k in 0.3-0.4 s) and 0.9-1.0 s (seed 1); 0.05 Hz in the 4-5 s bin (seed 0; 28.3k, then 66k), about 4.6 s rather than '4.5'.

MN9 'flips between 0 and 100' in only 1 of 4 runs: 0.2 Hz seed 0 reads 99, 10, 1, 44, 101 Hz over 5-10 s. The other three stay at about 100 once on.

Sugar at 100 Hz for 10 s (2 seeds) gives MN9 85 Hz and 0 within 100 ms of offset. Smells never switch the MN9 loop on (0/8).

The paper's 10-s file (none@0.2: DNa 19.25/20.80 and 17.00/20.00, MN9 65.8/92.9, PPL1 8.95/7.99) is identical to this run's 0-10 s, not its 1-10 s. The hum-on levels over 1-10 s (DNa 19.1/21.6) sit 1-3 Hz above the free-running level after offset (DNa 17.7/18.7 in the two 0.2 Hz runs), so 'mostly this state' holds.

Paper wording:
- 'Within about a second' holds at 0.2 Hz (0.3 and about 1 s, n = 2).
- 'mouthparts at about 100' is 101 Hz after offset but 73/101 Hz while the hum is on.
CORRECTED: PAPER (l.101): "It does more than add noise. Within about a second, in both runs, it tips the brain into firing that keeps itself going, with the steering neurons at about 20 spikes a second and the neuron that works the mouthparts at up to 100. This firing goes on for at least three seconds after the hum is switched off."

NOTES: "The hum (0.05 or 0.2 Hz on every neuron for 10 s, then off; 2 seeds each) never leaves the brain silent. It switches on two loops that then run without input.

(1) The ~2,000-neuron state of Note 5. At 0.2 Hz it starts after 0.3 s and about 1 s. At 0.05 Hz it starts after 4-5 s in one seed of two.

(2) A separate loop of about 30 neurons that holds MN9 at about 100 Hz and about 3 feeding motor neurons. It switched on in all four runs, at 0.75-1.0 s at 0.2 Hz and at about 2.6 and 5 s at 0.05 Hz. No smell (0 of 8 runs) and no sugar (0 of 2) switches it on.

Three seconds after the hum is removed, the three runs with both loops fire at 60,300 +- 200 spikes/s from 2,006 +- 16 neurons: DNa L/R 18.0/19.1 Hz, MN9 101, feed MNs 6.1, PPL1 8.9, GF 2.6 Hz. The fourth run keeps only the small loop: 1,900 spikes/s from 33 neurons, MN9 104 Hz.

The hum floors (10-s file, 0.2 Hz: DNa about 20 Hz, PPL1 about 9 Hz, MN9 66-93 Hz) are therefore mostly these two loops, with the hum adding 1-3 Hz on the DNa."

>>> CHECK [persistence] 4. 'The published model has no activity of its own' (l.95; l.125 'every neuron at rest'; l.123 'no reason to walk') (analyst verdict REWORD).: agrees=False
OWN: VERDICT: REWORD is right. The claim holds by construction for the neurons: rest -52 mV, threshold -45 mV, noise 0, no intrinsic current. It fails for the network once input has started it: history dependence is the pre-set consequence of DECISIONS 5.

Zero-input rows:
- social_probe_..._noise0.csv 'none': 0 spikes in seeds 0-4;
- noise_floor_flywire_shiu_min1+known+eln0.25.csv 'none'@0: 0 in seeds 0-2.

Sidecar persistence_g1.json: FLYBRAIN_SIGNS=known, FLYBRAIN_ELN=0.25, female FlyWire, gain 1. The published signs were not tested.

The proposed wording has four problems.
(a) The pooled 'one state, n = 11: 58,839 +- 1,012 spikes/s, 1,986 +- 20 neurons, DNa 16.5 +- 1.8 / 18.3 +- 1.4, GF 2.9 +- 0.5' (my recomputation agrees) mixes two things. The 8 smell runs give 58,304 +- 507 spikes/s from 1,978 +- 17 neurons with MN9 = 0. The 3 hum runs give 60,265 +- 166 from 2,006 +- 16, with MN9 101 and feed MNs 6: that is the same state plus the separate ~30-neuron MN9 loop, which is present in 4/4 hum runs. So the SD is inflated and MN9 is bimodal.
(b) 'Once a smell ... has done so' generalises too far. In the 1-s probe (5 seeds), Or47b alone at 100 Hz and cVA+touch never reach the state. The clean-box partner odour (Or47b about 31 Hz, CO2 about 0.9 Hz: median obs 0.207/0.006 x 150 Hz) never did in 10 logs of 135 +- 6 s (brain_s 127-145), where hz_dn_all max is 0.00 in every log.
(c) 'after every input stops' reads as 'after any input', which is false for touch, sound and sugar. It should say 'after all input stops'.
(d) 'Light and the other fly's smell kept about 8 % of their neurons firing' is misleading. hz_active_frac 0.08 is essentially the driven sensors themselves: 10,582 photoreceptors (7.63 %) plus 161 ORNs (7.75 %). At most about 1,000 other neurons fire, possibly none (verify_wording_full.md, REFUTE block).

Also:
- 'with only their eyes firing' at l.125 contradicts l.123 'no eyes' and Note 11 'vision not modelled' unless those change too (verify_wording 14a), and it leaves out the 161 ORNs.
- Once in the state, DNa at 16-18 Hz gives a walking duty of 0.68 with no input. So l.123 'a reason to start walking' is the right fix, and 'Walking ... not in the wiring' must become 'starting to walk unprompted'.
CORRECTED: PAPER l.95: "The model cannot start walking by itself either. In a clean box with no flowers, two simulated females stood still for more than two minutes of brain time. Their light and smell sensors fired, about 8 % of their neurons, but not one descending neuron did. A model neuron has no activity of its own, so a brain at rest stays still until an input drives its descending neurons. Once one of the smells I tried, or the hum, has done so, my version of the brain keeps going by itself. About 2,000 neurons, the steering neurons among them, fire on for at least three seconds after all input stops. A real fly put in an empty dish soon starts walking about \citep{martin2004portrait}. Starting to walk unprompted, the most ordinary thing a fly does, was the first behaviour on my list that this model does not produce."

l.125: replace 'every neuron at rest' with 'with only their sense organs firing'. This works only if l.123 'no eyes' is also changed (e.g. 'an eye whose signal never leaves the optic lobe'); otherwise use 'without a command reaching their legs'.

l.123: 'it does not hold a reason to start walking'.

NOTES: "No activity of its own is a property of the neuron model, not a finding. Rest and reset are at -52 mV and threshold at -45 mV, with no intrinsic current and no noise unless the hum is on. With no input the brain never spikes: 0 spikes in 5 and in 3 seeds.

The network is not inert once started. In my version of the female brain (known signs, eLN x 0.25, gain 1):
- 10 s of each of four smells (8/8 runs) leaves 1,978 +- 17 neurons firing on their own at 58,300 +- 500 spikes/s, with DNa L/R 16.0/18.0 Hz, GF 3.1 Hz and MN9 0, and no decay over the 3 s measured.
- The hum leaves the same state (3/4 runs) plus a separate ~30-neuron loop that holds MN9 at about 100 Hz (4/4 runs).

Touch, sound and sugar leave nothing. Not every smell starts the state: Or47b alone and cVA with touch did not within 1 s, and the clean-box females, smelling each other at about 31 Hz Or47b, never entered it. The published-sign model and the male were not tested."
