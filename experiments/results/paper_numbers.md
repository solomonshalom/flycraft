# Paper numbers, re-derived from the result files

(`python experiments/paper_numbers.py`; each line: computed value | the value typed in PAPER.md | verdict)

## A. Published anchors (`benchmark_flywire*.csv`, Results 1, Fig 8)

- sugar -> MN9, 100 Hz / 200 Hz response ratio (paper's model): **55 / 78 Hz = 71 %**
- bitter suppression: sugar 100 alone -> + bitter 100 (paper's model): computed **55 -> 3.3 Hz** | paper: 55 -> 3.3 Hz | ok
- JO-CE -> aBN1, JO-F -> aBN1 (paper's model): **13.3 / 0.0 Hz**
- sound (JO-A/B) -> giant fiber (paper's model): **22.0 Hz**
- head bristles -> feeding MNs (paper's model): **16.1 Hz**
- sugar -> MN9, 100 Hz / 200 Hz response ratio (published lobe): **58 / 83 Hz = 69 %**
- bitter suppression: sugar 100 alone -> + bitter 100 (published lobe): **58 -> 6.3 Hz**
- JO-CE -> aBN1, JO-F -> aBN1 (published lobe): **12.7 / 0.0 Hz**
- sound (JO-A/B) -> giant fiber (published lobe): **22.0 Hz**
- head bristles -> feeding MNs (published lobe): **15.8 Hz**
- sugar -> MN9 100/200 ratio, both lobes (draft 3: 69-75 %; 3-seed re-run of 25 Sep: 69 / 71 %): computed **69 / 71 %** | paper: 69 / 71 % | ok

## B. Gain window 0.7 / 1.0 / 1.4 (`gain_sweep_*.csv`, Results 2-3, Table 1, Fig 4)

female sweep: 5 seeds; male sweep: 5 seeds (mean over seeds, 600 ms, 100 Hz)
- Feeding: sugar GRNs -> MN9 (female): computed **33 / 76 / 94** | paper: 33 / 76 / 94 | ok
- Startle: JO-A -> giant fiber (female): computed **6 / 11 / 16** | paper: 6 / 11 / 16 | ok
- Startle: JO-B -> giant fiber (female), for the record: **0 / 4 / 11**
- Startle: JO-B -> giant fiber (male) at gain 0.5 / 0.7 / 1.0 / 1.4: computed **34 / 41 / 48 / 54** | paper: 34 / 41 / 48 / 54 | ok
- Rejection: touch -> DNp13 (female): computed **28 / 35 / 42** | paper: 28 / 36 / 42 | ok
- Rejection not gated by odor: cVA + touch -> DNp13: computed **27 / 36 / 37** | paper: 27 / 36 / 36 | ok
- Rejection not gated by odor: food + touch -> DNp13: computed **26 / 34 / 39** | paper: 26 / 34 / 39 | ok
- Male pheromone: cVA -> DNp13 (male): computed **7.8 / 30.2 / 26.2** | paper: 7.8 / 30 / 26 | ok
- Pheromone-specific: every other odor -> DNp13 (male), max over odors and gains <= 1.4: computed **0.0 Hz** | paper: 0 | ok
- Male song command: cVA -> pIP10 (male): computed **0 / 3 / 8** | paper: 0 / 3 / 8 | ok
- Male cVA -> MN9 / song MNs / PPL1: **MN9 8 / 32 / 36; song MNs 2 / 13 / 15; PPL1 0 / 12 / 28**
- Male contact chemosensation: ppk23/25 -> song (wing) MNs at gain 0.5 / 0.7 / 1.0 / 1.4: computed **10 / 20 / 22 / 11** | paper: 10 / 20 / 22 / 11 | ok
- Male contact chemosensation: ppk23/25 -> MDN: computed **0.0 / 26.8 / 1.8** | paper: 0 / 27 / 1.8 | ok
- Male touch -> MDN: computed **0.0 / 10.7 / 11.8** | paper: 0 / 10.7 / 11.8 | ok
- Male ppk25 alone -> song MNs / MDN: **3 / 12 / 9; 0 / 14 / 6**
- Decision neurons silent (female): max of pC1a / pC1d/e / aIPg / vpoDN over every input at gains <= 1.4: computed **0.0 / 0.0 / 0.0 / 0.0** | paper: 0.0 | ok
- Decision neurons silent (male): max P1 / aIPg at gains <= 1.0; at 1.4: computed **0.6 / 0.0; at 1.4: 2.3 / 1.9** | paper: 0.6 / 0.0; at 1.4: 2.3 / 1.9 | ok
- Odor rows need gain >= 1.0: max DNa L / R over odors at gain 0.7 (female): computed **0.8 / 0.0** | paper: 0.3 / 0.0 | ok
- cVA -> DNa L / R at gain 1.0 (female): computed **9 / 8** | paper: 9 / 8 | ok
- food -> DNa L / R at gain 1.0 (female): computed **20 / 12** | paper: 20 / 12 | ok
- food -> PPL1 (female): computed **4.9 / 17.2 / 36.4** | paper: 4.7 / 17 / 36 | ok
- food -> PAM (female), max over gains <= 1.4: computed **1.6** | paper: <= 1.5 | ok
- food -> giant fiber (female): computed **0.0 / 3.8 / 3.3** | paper: 0 / 3.8 / 3.3 | ok
- Or47b -> DNa L / R at 0.7 / 1.0 / 1.4 (female; the fragile absence): computed **0 / 0 / 24 ; 0 / 0 / 35** | paper: 0 / 0 / 24 ; 0 / 0 / 35 | ok
- Male labellar GRNs -> MN9, largest per-gain mean at gains <= 1.4: computed **0.8** | paper: 0.8 | ok

## C. Sensitivity tables (`sensitivity_*.csv`, Results 1-3, Table 1, Fig 7)

- female conditions in the table: computed **14** | paper: 14 | ok
- male conditions in the table (paper says 13): computed **13** | paper: 13 | ok
- sugar -> MN9 range, all female conditions but legacy; legacy: computed **64-95; legacy 371** | paper: 64-95; 371 | ok
- touch -> DNp13 range (female, all conditions): computed **28-51** | paper: 28-51 | ok
- cVA -> DNp13 / MN9 / pC1d/e / aIPg, max over female conditions: computed **0.0 / 0.0 / 0.0 / 0.0** | paper: 0.0 | ok
- touch -> MDN, max over female conditions: computed **1.2** | paper: 1.2 | ok
- food -> PPL1 by lobe variant (published / known x1 / Shiu x0.25 / known x0.5 / paper / x0.1): computed **111 / 101 / 17 / 27 / 17 / 17** | paper: 111 / 101 / 17 / 27 / 17 / 17 | ok
- food -> PAM by lobe variant: computed **21.3 / 13.2 / 0.1 / 0.5 / 0.1 / 0.1** | paper: 21 / 13 / 0.1 / 0.5 / 0.1 / 0.1 | ok
- PPL1 > PAM under food odor in every female condition: computed **True** | paper: True | ok
- odor -> punishment dopamine at x0.25: range of food / cVA -> PPL1 in the paper's model over stimulus rates: computed **5-20** | paper: 5-20 | ok
- KC mean rate under food odor by variant (published / known x1 / Shiu x0.25 / known x0.5 / paper): computed **32.9 / 24.5 / 1.5 / 3.9 / 1.2** | paper: 33 / 24.5 / 1.5 / 3.9 / 1.2 | ok
- food -> DNa L / R by variant (published, known x1, Shiu x0.25, paper, known x0.5, x0.1, >= 5 syn, Zenodo): computed **36 / 5; 29 / 5; 34 / 4; 21 / 13; 21 / 25; 28 / 9; 21 / 20; 27 / 9** | paper: 36 / 5; 29 / 5; 34 / 4; 21 / 13; 21 / 25; 28 / 9; 21 / 20; 27 / 9 | ok
- cVA -> DNa L / R by variant (same order; Zenodo >= 5 last): computed **33.6 / 3.9; 27.8 / 9.7; 23.6 / 5.3; 10.0 / 7.5; 20.0 / 24.7; 4.7 / 0.0; 0.0 / 0.0; 0.0 / 1.1; 0.0 / 0.0** | paper: 34 / 4; 28 / 10; 24 / 5; 10 / 7.5; 20 / 25; 5 / 0; 0 / 0; 0 / 1; 0 / 0 | ok
- cVA + touch -> DNp13 by variant (published / known x1 / Shiu x0.25 / known x0.5 / paper / x0.1) vs touch alone: computed **18.6 / 19.4 / 29.7 / 26.1 / 36.1 / 36.4 vs 36** | paper: 18.6 / 19.4 / 30 / 26 / 36 / 36 vs 36 | ok
- food -> giant fiber: paper's model; max under the other five lobe variants and the Zenodo table: computed **4.4; 0.6** | paper: 4.4; 0.6 | ok
- stimulus 50 / 150 Hz: food -> DNa L / R: computed **19 / 17; 30 / 5** | paper: 19 / 17; 30 / 5 | ok
- male cVA -> DNp13 range over all 13 conditions: computed **12-39** | paper: 12-39 | ok
- male cVA -> DNp13: baseline / published lobe / unclear LNs inhibitory / silent: computed **31.7 / 25 / 36 / 29** | paper: 31.7 / 25 / 36 / 29 | ok
- male cVA -> PPL1: unclear LNs excitatory / inhibitory / silent: computed **11.8 / 0.0 / 9.6** | paper: 11.8 / 0.0 / 9.6 | ok
- male contact pheromone -> MDN / song MNs / PPL1 (baseline); with >= 5 synapses: computed **29 / 21 / 39; 6.5 / 13** | paper: 29 / 21 / 39; 6.5 / 13 | ok
- male touch -> MDN: baseline / 50 Hz / 150 Hz: computed **11.5 / 0.0 / 28** | paper: 11.5 / 0 / 28 | ok
- male labellar GRNs -> MN9 max; P1 max; pIP10 max over all conditions: computed **1.1; 2.5; 6.9** | paper: 1.1; 2.5; 6.9 (the first two under the first-version numerics) | ok
- male touch and ppk25 + touch -> DNp13, max over conditions: computed **0.0** | paper: 0.0 | ok
- male cVA -> DNa L / R max over conditions (his steering is not olfactory): computed **1.9 / 4.7** | paper: 1.9 / 4.7 | ok
- male published lobe (x1): food -> PPL1 / PAM / KC; x1 with unclear LNs inhibitory: computed **121 / 42 / 34; 14 / 0 / 2** | paper: 121 / 42 / 34; 14 / 0 / 2 | ok

## D. Shuffled-connectome control (`shuffle_*_global.csv`, Fig 6)

- female: 3 rewirings x 3 seeds, 99.9 % of connections moved; intact key cells: sugar -> MN9 76, touch -> DNp13 35, cVA -> DNa 10, food -> PPL1 18, cVA -> DNp13 0, sound -> GF 5
-   female rewired: largest value of any readout under any input (max over rewired brains and seeds), top 3: **MDN back 7.2, PPL1 (punish DA) 3.2, aIPg aggr 0.6**
-   female rewired: mean of every readout over rewired trials, max: computed **2.1 Hz** | paper: 2 Hz | ok
- male: 2 rewirings x 3 seeds, 99.8 % of connections moved; intact key cells: sugar -> MN9 0, touch -> DNp13 0, cVA -> DNa 0, food -> PPL1 2, cVA -> DNp13 32, contact -> MDN 28, sound -> GF 49
-   male rewired: largest value of any readout under any input (max over rewired brains and seeds), top 3: **DNp13 reject 5.0, MDN back 4.4, PPL1 (punish DA) 2.3**
-   male rewired: mean of every readout over rewired trials, max: computed **2.2 Hz** | paper: 2 Hz | ok

## E. Innate map, paper's model (`social_probe_*_noise0.csv`, Results 3, 5; Fig 1)

- female decision neurons, max over every input: pC1a / pC1b/c / pC1d/e / aIPg / vpoDN / oviDN: computed **0.0 / 0.0 / 0.0 / 0.0 / 0.0 / 0.0** | paper: 0.0 | ok
- male P1 / pIP10, max over every input: computed **0.5 / 3.7** | paper: 0.5 / 3.5 | ok
- teaching signal not in the wiring: sugar / bitter / touch -> PAM, PPL1 (female): computed **sugar 0.0 / 0.0; bitter 0.0 / 0.0; touch 0.0 / 0.0** | paper: 0.0 / 0.0; 0.0 / 0.0; 0.0 / 0.0 | ok
- cVA -> DNa L / R (female, symmetric): computed **10 / 8** | paper: 10 / 8 | ok
- Or47b -> DNa L / R, DN all, KC (female: fly odor reaches nothing): computed **0.0 / 0.0, 0.01, 0.00** | paper: 0.0 / 0.0, 0.01, 0.00 | ok
- CO2 -> DNa L / R (female): **16 / 16**
- touch -> DNp13 / feeding MNs / MDN (female, 1 s): computed **35.6 / 16.2 / 0.2** | paper: 36 / 16 / 0 | ok
- male: touch -> MDN; ppk25 + touch -> MDN; cVA + touch -> DNp13: computed **10.7; 22.4; 7.3** | paper: 10.7; 22.4; 7.3 | ok
- male: contact pheromone -> MDN / wing MNs / song MNs / leg MNs: **28 / 30 / 22 / 2.9**
- male: ppk25 alone -> leg MNs / MDN: computed **1.5 / 13** | paper: 1.5 / 13 | ok
- male: Or47b / CO2 -> DN all, leg MNs (the female's odor reaches nothing in him): **0.75 / 0.12; 0.76 / 0.11**

## F. State arm (`state_probe_*_state30.csv`, Results 4, Table 1, Fig 5)

(published lobe -> paper's model; female 5 seeds, male 5 seeds, 1 s, state neurons 30 Hz)
- SAG tonic alone -> pC1a: computed **21.2 -> 21.2** | paper: 21.2 -> 21.2 | ok
- SAG tonic alone -> pC1b/c: computed **19.0 -> 19.0** | paper: 19.0 -> 19.0 | ok
- SAG tonic alone -> vpoDN: computed **5.7 -> 5.7** | paper: 5.7 -> 5.7 | ok
- SAG + touch -> pC1d/e: computed **6.3 -> 6.2** | paper: 6.3 -> 6.2 | ok
- SAG + cVA + touch -> pC1d/e (no longer masked by odor): computed **1.0 -> 7.1** | paper: 1.1 -> 7.1 | ok
- pC1a-c tonic -> vpoDN; + touch -> pC1d/e: computed **8.7 -> 8.7; 9.6 -> 9.4** | paper: 8.7 -> 8.7; 9.6 -> 9.4 | ok
- SAG + odor -> pC1a (cVA / Or47b / food), paper's model (published in brackets): computed **21.5 / 22.5 / 19.6 (17.5 / 17.8 / 16.1)** | paper: 21.5 / 22.5 / 19.6 (17.5 / 17.9 / 16.1) | ok
- aIPg tonic -> DNa L / R at rest; aIPg + cVA vs cVA without a state: computed **8.7 / 7.7; 24.8 / 21.8 vs 10.1 / 8.4** | paper: 8.7 / 7.7; 24.8 / 21.8 vs 10.1 / 8.4 | ok
- touch -> DNp13 across all female states (state-blind): computed **35.6-37.7** | paper: 35.6-37.9 | ok
- oviDN, max over every state and input (female): computed **0.0** | paper: 0.0 | ok
- hunger / satiety states (female): largest |change| of any readout under any input vs no state: **fed 3.2 (MN9 with cVA + sugar); fed 3.0 (MN9 with sugar GRNs); hungry 6.8 (MN9 with sugar GRNs); SIFa 4.0 (MN9 with cVA + sugar); AstA 2.2 (MN9 with cVA + sugar)**
- hunger / satiety states (male): largest |change| of any readout under any input vs no state: **fed 4.7 (MDN back with touch (all head bristles)); fed 5.0 (MDN back with cVA + touch); hungry 3.9 (MDN back with touch (all head bristles)); SIFa 5.8 (MDN back with ppk25 + touch); AstA 4.6 (MDN back with cVA + touch)**
- sugar -> MN9 under no state / NPF / AstA / DH44 / IPC / SAG / pC1a-c / aIPg (female): computed **79.4 / 86.2 / 77.8 / 82.4 / 80.0 / 83.8 / 83.6 / 83.0** | paper: 79.4 / 86.2 / 77.8 / 82.4 / 80.0 / 83.8 / 83.6 / 83.0 | ok
- sugar -> feeding-MN population, range across all female states: computed **24.8-26.7** | paper: 24.8-26.7 | ok
- P1 tonic alone -> pIP10 / TN1 / song MNs / wing MNs / DNp13 / MN9 (male): computed **50.4 -> 50.4; 8.2 -> 8.2; 27.6 -> 27.6; 9.1 -> 9.1; 20.6 -> 20.6; 2.7 -> 2.7** | paper: 50.4 -> 50.4; 8.2 -> 8.2; 27.6 -> 27.6; 9.1 -> 9.1; 20.6 -> 20.6; 2.7 -> 2.7 | ok
- P1 + food odor -> pIP10; P1 + Or47b -> pIP10: computed **40.5 -> 49.1; 41.0 -> 49.2** | paper: 40.7 -> 49.1; 41.7 -> 49.2 | ok
- P1 + odor -> MN9 (food / Or47b), published -> paper: computed **19.4 -> 2.6; 18.6 -> 0.7** | paper: 19.4 -> 2.6; 18.6 -> 0.7 | ok
- P1 + cVA -> DNp13; -> pIP10; -> MN9: computed **40.4 -> 53.9; 42.5 -> 45.3; 27.0 -> 30.9** | paper: 41 -> 54; 42 -> 45; 27 -> 31 | ok
- male cVA + touch -> MDN, no state; all pheromones + contact + touch -> MDN: computed **0.0 -> 25.2; 1.4 -> 52.6** | paper: 0.0 -> 25; 1.4 -> 53 | ok
- male aIPg tonic -> song MNs / wing MNs at rest; aIPg + cVA -> DNp13 vs no state: computed **4.0 / 1.2; 35 vs 30** | paper: 4 / 1.2; 35 vs 30 | ok
- male sugar -> MN9 max over all states (pooled taste labels): computed **0.0** | paper: 0 | ok

## G. Stop on contact (`contact_stop_*.csv`, Results 2, Table 1, Fig 12)

(female file: 16 conditions x 4 drives; seeds per cell not stored — see logs/contact_stop_flywire*.out)
female suppression index by condition (rows) and walking drive (columns):

| condition | Or47b (VA1v) | cVA (Or67d/DA1) | food odor | none |
|---|---|---|---|---|
| Shiu signs, eLN x0.25 | 0.91 | 0.77 | 0.54 | - |
| Shiu signs, eLN x0.25 + noise 0.2 Hz | 0.65 | 0.75 | 0.57 | 0.91 |
| Zenodo table, top_nt signs, >= 5 synapses (first version) | - | - | 0.08 | - |
| Zenodo table, top_nt signs, >= 5 synapses (first version) + noise 0.2 Hz | -1.91 | -1.86 | 0.05 | -1.51 |
| Zenodo table, top_nt signs, all connections | - | -0.00 | 0.71 | - |
| Zenodo table, top_nt signs, all connections + noise 0.2 Hz | 0.73 | 0.85 | 0.70 | 0.78 |
| known signs, eLN x0.1 | - | 0.70 | 0.74 | - |
| known signs, eLN x0.1 + noise 0.2 Hz | 0.71 | 0.86 | 0.74 | 0.70 |
| known signs, eLN x0.5 | 0.63 | 0.51 | 0.49 | - |
| known signs, eLN x0.5 + noise 0.2 Hz | 0.61 | 0.53 | 0.57 | 0.74 |
| known signs, eLN x1 | 0.45 | 0.50 | 0.56 | - |
| known signs, eLN x1 + noise 0.2 Hz | 0.47 | 0.40 | 0.57 | 0.43 |
| paper's model: known signs, eLN x0.25 | - | 0.93 | 0.69 | - |
| paper's model: known signs, eLN x0.25 + noise 0.2 Hz | 0.89 | 0.91 | 0.77 | 0.82 |
| published model: Shiu signs, eLN x1 | 0.48 | 0.35 | 0.51 | - |
| published model: Shiu signs, eLN x1 + noise 0.2 Hz | 0.42 | 0.47 | 0.48 | 0.59 |

- index range with food odor as the drive, every full-table variant, with and without the substrate: computed **0.48-0.77** | paper: 0.5-0.9 | ok
- index range over every cell with a real walking drive (DNa alone >= 2 Hz), every full-table variant, +- substrate: computed **0.35-0.93** | paper: 0.35-0.93 | ok
-   of which the published lobe (Shiu signs, eLN x1); the paper's model: computed **0.35-0.59; 0.69-0.93** | paper: 0.35-0.59; 0.69-0.93 | ok
- paper's model: cVA -> DNa L / R alone -> + touch: computed **9.3 / 8.2 -> 0.0 / 1.2** | paper: 9.3 / 8.2 -> 0.0 / 1.2 | ok
- Zenodo >= 5: cVA / Or47b alone -> + touch, DNa L / R (the bristles drive the DNa with no odor drive at all): computed **0.0 / 0.0 -> 7.2 / 17.5; 0.0 / 0.0 -> 8.0 / 16.5** | paper: 0 / 0 -> 7 / 17; 0 / 0 -> 8 / 17 | ok
- suppression index range, every sign rule / eLN scale / full table, with and without the substrate (excl. >= 5-synapse threshold): computed **-0.00-0.93** | paper: -0.00-0.93 | ok
- paper's model, no substrate: food -> DNa L / R alone -> + touch; index food / cVA: computed **20.3 / 12.3 -> 6.8 / 3.2; 0.69 / 0.93** | paper: 20.3 / 12.3 -> 6.8 / 3.2; 0.69 / 0.93 | ok
- paper's model, index range over drives (no substrate): computed **0.69-0.93** | paper: 0.69-0.93 | ok
- paper's model + 0.2 Hz substrate: index for food / cVA / Or47b / substrate alone: computed **0.77 / 0.91 / 0.89 / 0.82** | paper: 0.77 / 0.91 / 0.89 / 0.82 | ok
- all conditions with the substrate (excl. >= 5): index range: computed **0.40-0.91** | paper: 0.40-0.91 | ok
- Zenodo >= 5 synapses (first version): food alone -> + touch DNa L / R; index; touch alone -> DNa L / R: computed **27.8 / 10.5 -> 17.3 / 17.8; 0.08; 10.2 / 17.0 (with substrate)** | paper: 27.8 / 10.5 -> 17.3 / 17.8; 0.08; 10.2 / 17.0 | ok
- female MDN with touch, max over every condition and drive: computed **1.3** | paper: 1.3 | ok
- DNp13 with touch: paper's model / published / range over all conditions: computed **34 / 17 / 17-38** | paper: 34 / 17 / 17-38 | ok
- male: head bristles -> MDN with touch, eLN x0.25 settings (all drives, +- substrate): range: computed **2-34** | paper: 2-34 | ok
- male: head bristles -> MDN with touch under the published lobe (eLN x1): range: computed **0.0-23.0** | paper: 0.0-23.0 | ok
- male paper's model: ppk23/25 -> DNa L / R alone -> + touch; index: computed **8.2 / 4.7 -> 0.0 / 0.0; 1.00** | paper: 8.2 / 4.7 -> 0.0 / 0.0; 1.00 | ok
- male paper's model: ppk25 + touch -> MDN; cVA + touch -> MDN; leg MNs alone -> + touch (ppk): computed **23; 26; 2.9 -> 1.8** | paper: 23; 26; 2.9 -> 1.8 | ok
- male: cVA -> DNp13 alone -> with touch (paper's model): computed **30 -> 7.7** | paper: 30 -> 7.7 | ok

## H. The walking substrate (`noise_floor_*.csv`, Results 6, Fig 13)

- 1 s onset, female, no input, 0.2 Hz: DNa L / R; GF; feeding MNs; DNp13; active fraction: computed **7.0 / 7.0; 3.2; 2.8; 0.5; 19 %** | paper: 7.0 / 7.0; 3.2; 2.8; 0.5; 19 % | ok
- 1 s, 0.2 Hz: touch -> DNp13; touch -> DNa L / R; food -> DNa L / R; food + touch -> DNa; sugar -> feed MNs (vs 0 Hz): computed **35.3 (35.8); 2.7 / 1.2; 24.8 / 19.7 (23.0 / 14.0); 6.8 / 3.3; 24.7 (24.1)** | paper: 35.3 (35.8); 2.7 / 1.2; 24.8 / 19.7 (23 / 14); 6.8 / 3.3; 24.7 (24.1) | ok
- 1 s, giant fiber with no input at 0.2 / 0.3 / 0.5 Hz: computed **3.2 / 7.0 / 5.8** | paper: 3.2 / 7.0 / 5.8 | ok
- 10 s steady state, female, no input: DNa L / R at 0.1 / 0.2 / 0.3 Hz: computed **17.0 / 18.8; 18.1 / 20.4; 20.3 / 21.5** | paper: 17.0 / 18.8; 18.1 / 20.4; 20 / 22 | ok
- 10 s steady state, 0.2 Hz: touch -> DNa L / R and DNp13; GF no input; feeding MNs no input; DNp13 no input: computed **5.2 / 2.8, 28.9; 2.7; 5.2; 0.22** | paper: 5.2 / 2.8, 28.9; 2.7; 5.2; 0.22 | ok
- 10 s steady state, sugar -> MN9 at 0.2 Hz vs 1 s / 0 Hz: **99 vs 78**
- male, 1 s at 0.2 Hz, no input: leg MNs; DNa L / R; MDN; P1: computed **0.4; 1.2 / 1.5; 0.3; 0.20** | paper: 0.4; 1.2 / 1.5; 0.3; 0.20 | ok
- male, 1 s at 0.2 Hz: cVA -> DNp13 (vs 0 Hz); touch -> MDN (vs 0); ppk25 + touch -> MDN (vs 0); food -> DNp13: computed **22 (31); 17.8 (10.7); 28 (22); 0.3** | paper: 22 (31); 17.8 (10.7); 28 (22); 0.3 | ok
- male, 10 s steady state at 0.2 Hz: leg MNs; MDN; contact pheromone -> MDN / leg MNs: computed **1.2; 3.2; 10.8 / 3.0** | paper: 1.2; 3.2; 10.8 / 3.0 | ok

## I. Odor identity (`odor_code_*.csv`, Results 1, Table 1, Fig 9)

- female `shiu`: glomeruli > 10 Hz 98 % (range over odors 98-99); PNs active 81 %, PN mean 80 Hz; KC active 64.9-66.1 % (mean 65 %), KC mean 29.8 Hz; Jaccard same odor 0.99, different odors 0.99; eLN 188 Hz; n odors 10, seeds 2
- female `known`: glomeruli > 10 Hz 89 % (range over odors 2-98); PNs active 64 %, PN mean 55 Hz; KC active 0.0-57.2 % (mean 49 %), KC mean 18.9 Hz; Jaccard same odor 0.88, different odors 0.77; eLN 145 Hz; n odors 10, seeds 2
- female `known+eln0.5`: glomeruli > 10 Hz 64 % (range over odors 2-75); PNs active 36 %, PN mean 20 Hz; KC active 0.0-17.1 % (mean 11 %), KC mean 2.1 Hz; Jaccard same odor 0.78, different odors 0.53; eLN 104 Hz; n odors 10, seeds 2
- female `known+eln0.25`: glomeruli > 10 Hz 18 % (range over odors 2-28); PNs active 13 %, PN mean 5 Hz; KC active 0.0-5.4 % (mean 1 %), KC mean 0.2 Hz; Jaccard same odor 0.63, different odors 0.08; eLN 52 Hz; n odors 10, seeds 2
- female `known+eln0.1`: glomeruli > 10 Hz 3 % (range over odors 2-8); PNs active 2 %, PN mean 1 Hz; KC active 0.0-5.1 % (mean 1 %), KC mean 0.2 Hz; Jaccard same odor 0.51, different odors 0.01; eLN 10 Hz; n odors 10, seeds 2
- male `shiu`: glomeruli > 10 Hz 100 % (range over odors 100-100); PNs active 86 %, PN mean 82 Hz; KC active 55.3-64.1 % (mean 58 %), KC mean 28.0 Hz; Jaccard same odor nan, different odors 0.95; eLN 157 Hz; n odors 10, seeds 1
- male `known`: glomeruli > 10 Hz 100 % (range over odors 100-100); PNs active 86 %, PN mean 82 Hz; KC active 55.3-64.1 % (mean 58 %), KC mean 28.0 Hz; Jaccard same odor nan, different odors 0.95; eLN 157 Hz; n odors 10, seeds 1
- male `known+eln0.5`: glomeruli > 10 Hz 76 % (range over odors 71-80); PNs active 45 %, PN mean 27 Hz; KC active 1.8-6.5 % (mean 3 %), KC mean 0.4 Hz; Jaccard same odor nan, different odors 0.51; eLN 98 Hz; n odors 10, seeds 1
- male `known+eln0.25`: glomeruli > 10 Hz 18 % (range over odors 2-31); PNs active 15 %, PN mean 6 Hz; KC active 0.0-3.1 % (mean 0 %), KC mean 0.1 Hz; Jaccard same odor nan, different odors 0.06; eLN 48 Hz; n odors 10, seeds 1
- male `known+eln0.1`: glomeruli > 10 Hz 3 % (range over odors 2-8); PNs active 2 %, PN mean 2 Hz; KC active 0.0-2.6 % (mean 0 %), KC mean 0.1 Hz; Jaccard same odor nan, different odors 0.00; eLN 13 Hz; n odors 10, seeds 1
- paper's model: glomeruli %, KC % per odor, overlap within / between: computed **2-28 %; 0-5 %; 0.63 / 0.08** | paper: 2-28 %; 0-5 %; 0.63 / 0.08 | ok
- published lobe: PNs active %, glomeruli > 10 Hz, KC active %, overlap between odors: computed **81 % at 80 Hz; 58 of 59; 65 %; 0.99** | paper: 80 % at ~80 Hz; 57 of 59; 65 %; 0.99 | ok
- known signs x1 / x0.5 / x0.1: glomeruli %; overlap between odors: computed **89 % / 0.77; 64 % / 0.53; 3 % / 0.01** | paper: 89 % / 0.77; 64 % / 0.53; 3 % / 0.01 | ok

## J. Odor concentration sweep and steering (`odor_dose_*.csv`, Results 3, Table 1, Fig 10)

- **paper's rule** (3 seeds): steering food -4.8 / -2.7 / -6.6 / -3.7 / -9.2; food-type odors (food, sweet, vinegar, ester) steering range -9.2--0.7, bias range -8.2-6.3; CO2 / cVA / aversive steering range -2.8-2.3, bias -3.0-0.2; all odors: |steering| max 9.2, bias range -8.2-6.3
  paper: food -4.8 / -2.7 / -6.6 / -3.7 / -9.2; food-type odors -1 to -9; CO2 / cVA / aversive within +-2.8; bias -6 to +6
- **Shiu signs x0.25** (3 seeds): steering food +1.3 / +1.2 / +2.4 / +2.0 / +2.7; food-type odors (food, sweet, vinegar, ester) steering range -2.9-3.8, bias range 15.8-29.2; CO2 / cVA / aversive steering range -2.0-6.5, bias 0.0-18.5; all odors: |steering| max 6.5, bias range 0.0-29.2
  paper: steering within +-4; bias 15-29 for every odor at every dose
- **Zenodo table** (3 seeds): steering food +0.4 / +1.3 / +1.7 / -1.3 / -0.5; food-type odors (food, sweet, vinegar, ester) steering range -1.8-6.5, bias range 1.1-15.3; CO2 / cVA / aversive steering range 0.0-6.4, bias -0.1-6.4; all odors: |steering| max 6.5, bias range -0.1-15.3
  paper: steering within +-2 (a few +5-6 at 150); bias 5-15 food-type, 0 cVA / aversive
- **male** (3 seeds): steering food -0.2 / -0.8 / -0.7 / -1.4 / -1.2; food-type odors (food, sweet, vinegar, ester) steering range -1.4-2.6, bias range -3.2--0.1; CO2 / cVA / aversive steering range -0.2-2.6, bias -3.2--0.1; all odors: |steering| max 2.6, bias range -3.2--0.1
  paper: steering and bias <= 1.5 for every odor (cVA +2.6 at 150)
- food-type odor steering is negative at every dose (paper's rule): number of (odor, dose) cells with steering >= 0 among food / sweet / vinegar / ester: computed **0 of 20** | paper: 0 of 20 | ok
- bilateral food -> DNa L / R at 25 / 75 / 100 / 150 Hz: computed **16 / 18; 21 / 21; 23 / 14; 30 / 6** | paper: 16 / 18; 21 / 21; 23 / 14; 30 / 6 | ok
- bilateral cVA -> DNa L / R at 25 / 50 / 75 / 100 / 150 Hz (the dose curve's dip, 19b): computed **9.5 / 10.3; 11.5 / 11.0; 6.0 / 6.2; 9.2 / 8.0; 12.2 / 5.5** | paper: 9.5 / 10.3; 11.5 / 11.0; 6.0 / 6.2; 9.2 / 8.0; 12.2 / 5.5 | ok
- giant fiber, food-type odors bilateral, range over doses: computed **0.0-5.5** | paper: 0.0-5.5 | ok
- food -> PPL1 at 25 / 50 / 75 / 100 / 150 Hz; KC active %: computed **8 / 11 / 15 / 18 / 21; 3.0 / 4.4 / 5.3 / 6.0 / 7.2** | paper: 8 / 11 / 15 / 18 / 21; 3.0 / 4.4 / 5.3 / 6.0 / 7.2 | ok
- male cVA -> DNp13 at 25 / 50 / 75 / 100 / 150 Hz (dose-graded): computed **5.3 / 14.2 / 20.7 / 26.8 / 34.5** | paper: 5.3 / 14.2 / 20.5 / 26.8 / 34.5 | ok
- male: every other odor -> DNp13 max; GF max (every odor and dose): computed **0.0; 0.0** | paper: 0; 0.0 | ok
- male cVA: KC active % at 25-150 Hz: computed **0.1-0.3** | paper: 0.1-0.3 | ok

## K. Conditioning (`conditioning_*.csv`, Results 5, Table 1, Fig 2b)

- `flywire_shiu_min1+known+eln0.1_us-dan-punish_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.11-0.11, CS- 0.22-0.22; **learning index 0.11 +/- 0.00**; approach change (post - pre) CS+ -1.0--1.0, CS- 3.0-3.0 Hz; |dDNa L| + |dDNa R| for CS+ 2.0-2.0 Hz
- `flywire_shiu_min1+known+eln0.1_us-dan-punish_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.50-0.50; **learning index 0.40 +/- 0.00**; approach change (post - pre) CS+ 7.0-7.0, CS- -1.0--1.0 Hz; |dDNa L| + |dDNa R| for CS+ 6.0-6.0 Hz
- `flywire_shiu_min1+known+eln0.1_us-dan-reward_ester-vs-vinegar` (n = 3): taught-compartment drive retained CS+ 0.12-0.14, CS- 0.73-0.77; **learning index 0.63 +/- 0.02**; approach change (post - pre) CS+ -1.0-0.0, CS- -3.5-2.5 Hz; |dDNa L| + |dDNa R| for CS+ 2.0-2.5 Hz
- `flywire_shiu_min1+known+eln0.1_us-dan-reward_vinegar-vs-ester` (n = 3): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.70-0.73; **learning index 0.61 +/- 0.02**; approach change (post - pre) CS+ -3.5-5.5, CS- -1.0-0.0 Hz; |dDNa L| + |dDNa R| for CS+ 1.0-2.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish-20hz_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.09-0.09, CS- 0.19-0.19; **learning index 0.09 +/- 0.00**; approach change (post - pre) CS+ -6.5--6.5, CS- 8.5-8.5 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-4.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish-20hz_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.46-0.46; **learning index 0.36 +/- 0.00**; approach change (post - pre) CS+ 11.5-11.5, CS- -6.5--6.5 Hz; |dDNa L| + |dDNa R| for CS+ 5.5-5.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish-phasic2_ester-vs-vinegar` (n = 2): taught-compartment drive retained CS+ 0.09-0.10, CS- 0.24-0.24; **learning index 0.14 +/- 0.00**; approach change (post - pre) CS+ -6.5-5.5, CS- 0.0-3.0 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-8.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish-phasic2_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.53-0.53; **learning index 0.44 +/- 0.00**; approach change (post - pre) CS+ 8.0-8.0, CS- -6.5--6.5 Hz; |dDNa L| + |dDNa R| for CS+ 2.5-2.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish_ester-vs-vinegar` (n = 3): taught-compartment drive retained CS+ 0.09-0.10, CS- 0.17-0.18; **learning index 0.08 +/- 0.00**; approach change (post - pre) CS+ -6.5-1.0, CS- 0.5-11.5 Hz; |dDNa L| + |dDNa R| for CS+ 3.5-8.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-punish_vinegar-vs-ester` (n = 3): taught-compartment drive retained CS+ 0.09-0.10, CS- 0.40-0.47; **learning index 0.35 +/- 0.03**; approach change (post - pre) CS+ 0.5-11.5, CS- -6.5-5.5 Hz; |dDNa L| + |dDNa R| for CS+ 2.0-6.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward-20hz_ester-vs-vinegar` (n = 3): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.66-0.72; **learning index 0.59 +/- 0.03**; approach change (post - pre) CS+ -6.5-5.5, CS- 2.0-9.5 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-8.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward-20hz_vinegar-vs-ester` (n = 3): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.61-0.64; **learning index 0.53 +/- 0.02**; approach change (post - pre) CS+ 1.0-5.5, CS- -6.5-5.5 Hz; |dDNa L| + |dDNa R| for CS+ 4.5-8.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward-phasic2_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.11-0.11, CS- 0.76-0.76; **learning index 0.66 +/- 0.00**; approach change (post - pre) CS+ -6.5--6.5, CS- 4.5-4.5 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-4.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward-phasic2_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.11-0.11, CS- 0.65-0.65; **learning index 0.54 +/- 0.00**; approach change (post - pre) CS+ 6.0-6.0, CS- -6.5--6.5 Hz; |dDNa L| + |dDNa R| for CS+ 6.5-6.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward_ester-vs-vinegar` (n = 3): taught-compartment drive retained CS+ 0.10-0.11, CS- 0.66-0.70; **learning index 0.57 +/- 0.02**; approach change (post - pre) CS+ -6.5-5.5, CS- 1.5-8.0 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-8.5 Hz
- `flywire_shiu_min1+known+eln0.25_us-dan-reward_vinegar-vs-ester` (n = 3): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.59-0.64; **learning index 0.53 +/- 0.02**; approach change (post - pre) CS+ -0.5-5.5, CS- -6.5-5.5 Hz; |dDNa L| + |dDNa R| for CS+ 3.5-6.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-wiring-phasic2_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.90-0.90, CS- 0.96-0.96; **learning index 0.06 +/- 0.00**; approach change (post - pre) CS+ 6.0-6.0, CS- -6.5--6.5 Hz; |dDNa L| + |dDNa R| for CS+ 5.0-5.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-wiring_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.92-0.92, CS- 0.90-0.90; **learning index -0.01 +/- 0.00**; approach change (post - pre) CS+ -6.5--6.5, CS- 8.5-8.5 Hz; |dDNa L| + |dDNa R| for CS+ 4.0-4.0 Hz
- `flywire_shiu_min1+known+eln0.25_us-wiring_vinegar-vs-ester` (n = 3): taught-compartment drive retained CS+ 0.87-0.89, CS- 0.91-0.98; **learning index 0.05 +/- 0.03**; approach change (post - pre) CS+ 1.0-8.5, CS- -6.5-5.5 Hz; |dDNa L| + |dDNa R| for CS+ 3.5-6.5 Hz
- `malecns_all_min1+eln0.25_us-dan-punish_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.83-0.83; **learning index 0.73 +/- 0.00**; approach change (post - pre) CS+ 0.0-0.0, CS- 0.0-0.0 Hz; |dDNa L| + |dDNa R| for CS+ 0.0-0.0 Hz
- `malecns_all_min1+eln0.25_us-dan-punish_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.10-0.10, CS- 0.92-0.92; **learning index 0.82 +/- 0.00**; approach change (post - pre) CS+ 0.0-0.0, CS- 0.0-0.0 Hz; |dDNa L| + |dDNa R| for CS+ 0.0-0.0 Hz
- `malecns_all_min1+eln0.25_us-dan-reward_ester-vs-vinegar` (n = 1): taught-compartment drive retained CS+ 0.12-0.12, CS- 0.93-0.93; **learning index 0.81 +/- 0.00**; approach change (post - pre) CS+ 0.0-0.0, CS- 0.0-0.0 Hz; |dDNa L| + |dDNa R| for CS+ 0.0-0.0 Hz
- `malecns_all_min1+eln0.25_us-dan-reward_vinegar-vs-ester` (n = 1): taught-compartment drive retained CS+ 0.16-0.16, CS- 0.94-0.94; **learning index 0.78 +/- 0.00**; approach change (post - pre) CS+ 0.0-0.0, CS- 0.0-0.0 Hz; |dDNa L| + |dDNa R| for CS+ 0.0-0.0 Hz
- appetitive, reward DANs 50 Hz, eLN x0.25 (both orders): computed **0.55 +/- 0.03 (n = 6)** | paper: 0.54 +/- 0.02 (n = 6) | ok
- appetitive, reward DANs 20 Hz: computed **0.56 +/- 0.04 (n = 6)** | paper: 0.56 +/- 0.04 (n = 6) | ok
- appetitive, eLN x0.1: computed **0.62 +/- 0.02 (n = 6)** | paper: 0.62 +/- 0.02 (n = 6) | ok
- aversive, punishment DANs 50 Hz, eLN x0.25: computed **0.21 +/- 0.14 (n = 6)** | paper: 0.21 +/- 0.15 (n = 6) | ok
- aversive, 20 Hz; aversive, eLN x0.1: computed **0.23 +/- 0.13 (n = 2); 0.26 +/- 0.14 (n = 2)** | paper: 0.23 +/- 0.13 (n = 2); 0.26 +/- 0.15 (n = 2) | ok
- no US (`--us wiring`): computed **0.03 +/- 0.04 (n = 4)** | paper: 0.04 +/- 0.04 (n = 4) | ok
- male, reward / punishment DANs (eLN x0.25): computed **0.80 +/- 0.02 (n = 2); 0.77 +/- 0.04 (n = 2)** | paper: 0.80 +/- 0.02 (n = 2); 0.77 +/- 0.04 (n = 2) | ok
- CS+ taught-compartment drive retained (appetitive 50 Hz, both orders), range; CS-: computed **0.10-0.11; 0.59-0.70** | paper: 0.10-0.11; 0.59-0.66 | ok

## L. Expression probe (`expression_probe_*.csv`, Results 5, Fig 11)

- reward set, no odor: DNa L silenced - intact at tonic 10 / 20 / 40 Hz: computed **+5.5 / +5.0 / +4.0** | paper: +5.5 / +5.0 / +4.0 | ok
- reward set, no odor, intact: DNa L at 10 / 20 / 40 Hz (waking the targets alone drives the turning DNs): computed **23 / 26 / 30** | paper: 23 / 26.5 / 30 | ok
- reward set, odor left: approach index (silenced - intact) at 0 / 5 / 10 / 20 / 40 Hz: computed **-1.8 / -3.5 / +1.8 / +3.0 / +4.0** | paper: -1.9 / -3.5 / +1.8 / +3.0 / +4.0 | ok
- largest |silenced - intact| of DNp09 / MDN / feeding MNs over every set, odor and tonic level: computed **0.0 / 0.0 / 0.1** | paper: 0.0 / 0.0 / 0.0 | ok
- punishment set: the 28 descending targets, intact vs silenced (odor bilateral) at 0 / 5 / 10 / 20 / 40 Hz: computed **7.0 vs 7.1; 11.3 vs 10.8; 15.1 vs 14.8; 23.3 vs 23.0; 38.6 vs 38.8** | paper: 7.0 vs 7.1; 11.3 vs 10.8; 15.1 vs 14.8; 23.3 vs 23.0; 38.6 vs 38.8 | ok
- punishment set: max |intact - silenced| of the target DNs over odors and levels: computed **0.54 Hz** | paper: 0.6 | ok
- punishment set, MDN with the tonic drive at 40 Hz, intact / silenced (the targets' own activity): computed **18.6 / 18.6** | paper: 18.6 / 18.6 | ok

## M. Learning in the world (`logs/learn_world{5,6}_probe_{pre,post}.json`, `*_learn_stats.csv`, Results 5)

- world6: retained drive post / pre, reward-comp ester / vinegar; punish-comp vinegar / ester; LI appetitive (vin - est) / aversive (est - vin): computed **0.289 / 0.662; 0.131 / 0.438; 0.37 / 0.31** | paper: 0.289 / 0.662; 0.131 / 0.438; 0.37 / 0.31 | ok
- world5: retained drive post / pre, reward-comp ester / vinegar; punish-comp vinegar / ester; LI appetitive (vin - est) / aversive (est - vin): computed **0.271 / 0.286; 0.090 / 0.384; 0.02 / 0.29** | paper: 0.271 / 0.286; 0.090 / 0.384; 0.02 / 0.29 | ok
- world5: walk / turn while smelling poppies (A) and dandelions (B): pre; train; post: **pre walk 0.53 / 0.67, turn -0.07 / +0.01; train walk 0.49 / 0.68, turn +0.01 / +0.53; post walk 0.48 / 0.68, turn -0.12 / +0.58; sugar ticks 906 (45 s), bitter ticks 2126**
- world6: walk / turn while smelling poppies (A) and dandelions (B): pre; train; post: **pre walk nan / nan, turn +nan / +nan; train walk 0.48 / 0.67, turn -0.02 / +0.52; post walk 0.47 / 0.72, turn -0.06 / +0.55; sugar ticks 887 (44 s), bitter ticks 0**

## N. Encounter trials (`encounter_trials.csv` and the arena logs; Results 6, Table 2, Fig 3, 3b)

| lobe / chamber | cond | trials | female logs | brain s | trials with contact | logs with contact | contact % of ticks | longest bout s | first contact s | walk duty | path blocks | median dist | DNa L / R far -> contact | DNp13 far -> near -> contact | feed MNs far -> contact | GF far | MDN female contact | reject / feed / attack acts per min | jump events per min | male: MDN contact / near / far | male walk | male path | male P1 far / near / contact | male pIP10 (sing) far / contact | male sing acts per min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| published / odor-free | ff | 5 | 10 | 32 +/- 7 | 0 / 5 | 0 / 10 | 0.0 +/- 0.0 | 0.0 | - | 0.71 | 115 | 7.4 | 36.1 / 4.2 -> - | 0.0 -> 0.0 -> - | 0.1 -> - | 0.0 | - | 0 / 0 / 0.0 | 0 | - | - | - | - | - | - |
| published / odor-free | mf | 5 | 5 | 33 +/- 4 | 4 / 5 | 4 / 5 | 3.6 +/- 3.5 | 2.9 | 0.2 | 0.71 | 116 | 8.1 | 37.1 / 4.0 -> 20.9 / 0.1 | 0.0 -> 5.7 -> 16.5 | 0.0 -> 21.5 | 0.0 | 0.0 | 3 / 2 / 0.0 | 0 | 0.0 / 0.0 / 0.0 | 0.24 | 31 | 0.00 / 0.00 / 0.00 | 3.10 / 1.42 | 83.0 |
| specific / faint-smell | ff | 5 | 10 | 95 +/- 5 | 4 / 5 | 8 / 10 | 39.5 +/- 34.4 | 86.2 | 0.1 | 0.30 | 34 | 10.3 | 13.7 / 13.5 -> 0.4 / 0.1 | 5.0 -> 31.6 -> 32.9 | 4.3 -> 22.2 | 2.3 | 0.1 | 99 / 38 / 0.0 | 139 | - | - | - | - | - | - |
| specific / faint-smell | mf | 5 | 5 | 83 +/- 26 | 1 / 5 | 1 / 5 | 1.2 +/- 2.6 | 1.9 | 0.8 | 0.47 | 40 | 8.4 | 12.4 / 12.4 -> 2.7 / 1.2 | 5.7 -> 6.0 -> 33.0 | 4.5 -> 22.0 | 2.4 | 0.1 | 31 / 14 / 0.0 | 233 | 39.5 / 5.9 / 1.4 | 0.03 | 41 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 | 5.0 |
| specific / clean | ff | 5 | 10 | 135 +/- 6 | 0 / 5 | 0 / 10 | 0.0 +/- 0.0 | 0.0 | - | 0.00 | 0 | 4.3 | 0.0 / 0.0 -> - | 0.0 -> 0.0 -> - | 0.0 -> - | 0.0 | - | 0 / 0 / 0.0 | 0 | - | - | - | - | - | - |
| specific / clean | mf | 5 | 5 | 90 +/- 1 | 2 / 5 | 2 / 5 | 0.5 +/- 0.9 | 0.9 | 1.2 | 0.48 | 42 | 8.9 | 12.7 / 12.6 -> 0.0 / 0.3 | 5.1 -> 4.9 -> 31.6 | 4.8 -> 22.1 | 2.0 | 0.2 | 30 / 16 / 0.0 | 196 | 48.1 / 14.8 / 3.9 | 0.08 | 56 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 | 9.8 |
| specific / noise0.2 | ff | 5 | 10 | 84 +/- 6 | 3 / 5 | 6 / 10 | 11.2 +/- 14.9 | 15.1 | 15.4 | 0.51 | 62 | 12.1 | 15.5 / 16.3 -> 1.2 / 1.2 | 5.3 -> 16.2 -> 30.8 | 8.1 -> 21.3 | 1.6 | 0.4 | 44 / 32 / 2.0 | 143 | - | - | - | - | - | - |
| specific / noise0.2 | mf | 5 | 5 | 85 +/- 4 | 4 / 5 | 4 / 5 | 1.3 +/- 1.1 | 1.3 | 5.1 | 0.55 | 62 | 10.0 | 15.2 / 16.1 -> 2.0 / 1.8 | 5.1 -> 10.1 -> 30.6 | 8.1 -> 21.0 | 1.8 | 0.4 | 33 / 26 / 2.9 | 167 | 28.9 / 12.9 / 6.3 | 0.27 | 127 | 0.20 / 0.20 / 0.20 | 0.24 / 0.34 | 20.2 |
| specific / noise0.2-virgin | mf | 5 | 5 | 64 +/- 23 | 5 / 5 | 5 / 5 | 3.6 +/- 3.2 | 1.7 | 1.2 | 0.52 | 65 | 10.6 | 13.9 / 15.9 -> 0.3 / 1.4 | 4.1 -> 12.6 -> 31.7 | 7.6 -> 18.6 | 2.1 | 0.5 | 29 / 25 / 3.7 | 185 | 30.3 / 17.8 / 7.8 | 0.28 | 106 | 0.21 / 0.22 / 0.18 | 0.19 / 0.04 | 25.2 |

Table 2 of the paper (draft 1) reads: published ff 0/5, 0, 0.71, 36/4; published mf 4/5, 3.6, 0.71, 37/4 -> 21/0.1, 0 -> 16.5, MDN 0 walk 0.24; faint ff 4/5, 40 +/- 32, 0.30, 13.7/13.5 -> 0.4/0.1, 5.0 -> 32.9; faint mf 1/5, 1.2, 0.47, 12.4/12.4 -> 2.7/1.2, 5.7 -> 33.0, MDN 39.5 / 6 near, walk 0.03; clean ff 0/5, 0, 0.00; clean mf 2/5, 0.5, 0.48, 12.7/12.6 -> 0.0/0.3, 5.1 -> 31.6, MDN 48 / 15 / 4, walk 0.03; noise ff 3/5, 11 +/- 14, 0.51, 15.5/16.3 -> 1.2/1.2, 5.3 -> 30.9; noise mf 4/5, 1.3, 0.55, 15.2/16.1 -> 2.0/1.8, 5.1 -> 30.6, MDN 29 / 13 / 6, walk 0.27, P1 0.2

Odor in the chamber (max of any odor_* column over the trial, per chamber; 0 = no odorous block ever within 16 blocks): published/odor-free 0.00; specific/clean 0.00; specific/faint-smell 0.70; specific/noise0.2 0.00; specific/noise0.2-virgin 0.00; specific/rep-clean 0.00; specific/rep-noise0.2 0.00; specific/rep-noise0.2-virgin 0.00
- substrate act floors, female logs on the substrate: rejection / proboscis / attack events per min; DNp13 far; feed MNs far; GF far; jump events per min: computed **44 / 32 / 2.0; 5.3; 8.1; 1.6; 143** | paper: 44 / 32 / 2.0; 5.3; 8.1; 1.6; 143 | ok
- substrate ff: jump ticks as % of ticks: computed **11.9 %** | paper: 12 % | ok
- substrate male: leg-MN walk duty, path, MDN far, P1 far / near / contact, pIP10 far / near / contact, wing MNs? (sing = pIP10 readout): computed **walk 0.27, path 127, MDN far 6.3 near 12.9 contact 28.9; P1 0.20 / 0.20 / 0.20; pIP10 0.24 / 0.27 / 0.34** | paper: 0.27, 127, 6.2 / 12.9 / 28.9; P1 0.20 / 0.21 / 0.20; pIP10 0.24 / 0.22 / 0.34 | ok
- clean mf male: walk duty (untouched trials), path range, MDN contact / near / far; trial 3 path: computed **0.03, 26-31, 48 / 15 / 4; 158 at duty 0.29** | paper: 0.03, 26-31, 48 / 15 / 4; 158 at 0.29 | ok
- clean mf female: walk, path, DNa far, DNp13 far, GF far; contact: DNp13, feed MNs, DNa, walk: computed **0.48, 42, 12.7 / 12.6, 5.1, 2.0; 31.6, 22.1, 0.0 / 0.3** | paper: 0.48, 42, 12.7 / 12.6, 5.1, 1.9; 31.6, 22.1, 0.0 / 0.3 | ok
- clean ff females: max of any readout over the 10 logs (walk, path, DNa, DNp13, feed, GF); median distance: computed **0.00, 0.0, 0.00 / 0.00, 0.00, 0.00, 0.00; 4.3 blocks; brain time 135 +/- 6 s** | paper: 0.00, 0.0, 0.00 / 0.00, 0.00, 0.00, 0.00; 4.3; 135 +/- 6 | ok

**Approach: the female's turning DNs and turn command before a log's first contact, by distance to the other fly (pooled ticks over the female logs of each chamber), and after a touch ends (time since the last contact)**

| chamber / cond | flies | ticks 1.3-2 blocks: DNa L / R (n) | 2-3.5 (n) | 3.5-6 (n) | > 6 far (n) | turn command, all pre-contact ticks by bin | post-touch DNa L / R at 0-0.1 s / 0.1-0.25 / 0.25-2 / > 2 s (n) |
|---|---|---|---|---|---|---|---|
| specific / clean | mf | 7.8 / 8.9 (9) | 9.5 / 8.5 (20) | 12.2 / 9.9 (390) | 12.7 / 12.9 (5020) | -0.03 / +0.02 / +0.05 / -0.01 | 8.6/7.1 (7) / 6.5/9.4 (17) / 6.3/8.6 (121) / 12.5/12.2 (3319) |
| specific / noise0.2 | ff | 11.7 / 12.8 (29) | 11.7 / 16.1 (83) | 15.1 / 15.4 (427) | 15.7 / 16.4 (12131) | -0.03 / -0.10 / -0.01 / -0.02 | 8.2/11.8 (34) / 11.0/17.4 (61) / 12.0/14.5 (271) / 15.7/16.6 (1834) |
| specific / noise0.2 | mf | 7.2 / 11.9 (88) | 12.0 / 14.2 (170) | 14.5 / 15.9 (1025) | 14.8 / 16.5 (3311) | -0.11 / -0.05 / -0.03 / -0.04 | 5.5/5.5 (11) / 8.7/13.9 (23) / 9.7/12.1 (150) / 15.8/15.8 (3555) |
| specific / noise0.2-virgin | mf | 2.7 / 10.8 (37) | 8.6 / 13.5 (145) | 12.8 / 13.4 (486) | 13.4 / 15.0 (3198) | -0.19 / -0.10 / -0.01 / -0.04 | 6.5/13.5 (17) / 11.6/12.2 (37) / 11.0/15.3 (217) / 14.2/16.2 (2025) |
| specific / faint-smell | ff | 4.9 / 9.7 (35) | 7.9 / 9.5 (96) | 11.4 / 11.5 (126) | 13.0 / 13.0 (8947) | -0.10 / -0.04 / -0.00 / -0.00 | 9.5/6.4 (22) / 13.3/13.8 (21) / 14.8/18.0 (90) / 12.8/12.5 (2255) |
| specific / faint-smell | mf | 0.0 / 12.5 (4) | 8.4 / 8.9 (94) | 10.2 / 11.1 (656) | 12.6 / 12.7 (5523) | -0.25 / -0.01 / -0.02 / -0.00 | 15.9/10.9 (22) / 14.4/10.6 (18) / 5.7/7.0 (44) / 11.9/11.6 (1765) |

Paper (19b): substrate ff 10.8 / 13.5 at 1.3-2 (26 ticks), 11.5 / 16.2 at 2-3.5 (60), 15.2 / 15.3 at 3.5-6, 15.8 / 16.5 far; clean mf 7.8 / 8.9 (9), 9.5 / 8.5 (20), 10.5 / 11.2, 12.8 / 13.1 far; post-touch 5.9 / 5.6, 10 / 17, 11-15 / 13-15, 16 / 16; turn command 0.00 at every distance

## O. Pre-contact slowing as a dose row (`precontact_dose_flywire_*.csv`, machine-time item 6)

(3 seeds; 2 s settle, 2 s read; bilateral drive at level x 150 Hz)

| substrate | condition | DNa L / R (Hz) | DNp09 | walk duty (body readout) | turn | GF | DNp13 | MDN | PPL1 | active % |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | nothing | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | ff far: Or47b 0.10, CO2 0.003 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | ff near: Or47b 0.4, CO2 0.02 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | ff near: Or47b 0.6, CO2 0.02 | 9.0 +/- 0.5 / 12.8 +/- 1.2 | 0.0 | 0.52 | -0.10 | 4.2 | 0.0 | 0.0 | 4.9 | 2 |
| 0 | ff near: Or47b 0.9, CO2 0.02 | 0.2 +/- 0.3 / 0.4 +/- 0.7 | 0.0 | 0.02 | -0.01 | 0.2 | 0.0 | 0.0 | 0.1 | 1 |
| 0 | mf far: cVA 0.06, Or47b 0.10, CO2 0.003 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | mf far: cVA 0.10, Or47b 0.10, CO2 0.003 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | mf far: cVA 0.14, Or47b 0.10, CO2 0.003 | 15.2 +/- 0.8 / 15.2 +/- 1.0 | 0.0 | 0.64 | -0.00 | 2.9 | 0.0 | 0.0 | 8.4 | 2 |
| 0 | mf near: cVA 0.3, Or47b 0.4, CO2 0.02 | 8.5 +/- 2.3 / 10.8 +/- 1.8 | 0.0 | 0.47 | -0.06 | 2.2 | 0.0 | 0.0 | 5.8 | 2 |
| 0 | mf near: cVA 0.5, Or47b 0.6, CO2 0.02 | 4.5 +/- 1.1 / 6.3 +/- 0.6 | 0.0 | 0.30 | -0.05 | 1.5 | 0.0 | 0.0 | 3.4 | 2 |
| 0 | mf near: cVA 0.7, Or47b 0.9, CO2 0.02 | 5.2 +/- 1.6 / 5.9 +/- 0.8 | 0.0 | 0.31 | -0.02 | 1.2 | 0.0 | 0.0 | 3.4 | 2 |
| 0 | cVA alone 0.06 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | cVA alone 0.14 | 13.8 +/- 2.2 / 14.8 +/- 2.9 | 0.0 | 0.61 | -0.02 | 2.3 | 0.0 | 0.0 | 8.3 | 2 |
| 0 | cVA alone 0.3 | 14.5 +/- 2.5 / 16.0 +/- 1.6 | 0.0 | 0.64 | -0.04 | 0.6 | 0.0 | 0.0 | 8.7 | 2 |
| 0 | cVA alone 0.5 | 11.7 +/- 0.6 / 11.4 +/- 1.3 | 0.0 | 0.54 | +0.01 | 0.4 | 0.0 | 0.0 | 7.3 | 2 |
| 0 | cVA alone 0.7 | 11.5 +/- 0.8 / 9.5 +/- 1.8 | 0.0 | 0.50 | +0.05 | 0.2 | 0.0 | 0.0 | 7.4 | 2 |
| 0 | Or47b alone 0.1 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | Or47b alone 0.4 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | Or47b alone 0.9 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | CO2 alone 0.003 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0 | CO2 alone 0.02 | 0.0 +/- 0.0 / 0.0 +/- 0.0 | 0.0 | 0.00 | +0.00 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| 0.2 | nothing | 19.6 +/- 0.6 / 19.8 +/- 0.6 | 0.1 | 0.73 | -0.01 | 2.6 | 0.2 | 0.4 | 8.9 | 34 |
| 0.2 | ff far: Or47b 0.10, CO2 0.003 | 10.5 +/- 6.9 / 10.2 +/- 9.1 | 0.2 | 0.46 | +0.01 | 3.8 | 0.5 | 0.2 | 5.1 | 34 |
| 0.2 | ff near: Or47b 0.4, CO2 0.02 | 12.4 +/- 0.7 / 20.3 +/- 2.1 | 0.1 | 0.66 | -0.20 | 2.5 | 0.2 | 0.2 | 6.1 | 34 |
| 0.2 | ff near: Or47b 0.6, CO2 0.02 | 12.0 +/- 0.7 / 17.1 +/- 0.5 | 0.1 | 0.62 | -0.13 | 3.4 | 0.3 | 0.2 | 5.6 | 34 |
| 0.2 | ff near: Or47b 0.9, CO2 0.02 | 8.9 +/- 1.2 / 14.7 +/- 2.4 | 0.1 | 0.54 | -0.14 | 3.2 | 0.4 | 0.2 | 4.1 | 34 |
| 0.2 | mf far: cVA 0.06, Or47b 0.10, CO2 0.003 | 13.5 +/- 5.5 / 16.5 +/- 8.5 | 0.5 | 0.61 | -0.07 | 3.2 | 0.3 | 0.2 | 6.1 | 35 |
| 0.2 | mf far: cVA 0.10, Or47b 0.10, CO2 0.003 | 14.4 +/- 3.4 / 18.6 +/- 5.5 | 0.4 | 0.66 | -0.10 | 3.3 | 0.3 | 0.2 | 6.8 | 35 |
| 0.2 | mf far: cVA 0.14, Or47b 0.10, CO2 0.003 | 18.8 +/- 0.9 / 21.8 +/- 1.8 | 0.4 | 0.75 | -0.07 | 1.8 | 0.1 | 0.2 | 8.5 | 35 |
| 0.2 | mf near: cVA 0.3, Or47b 0.4, CO2 0.02 | 12.9 +/- 2.6 / 15.8 +/- 3.4 | 0.4 | 0.62 | -0.07 | 1.1 | 0.1 | 0.2 | 6.2 | 35 |
| 0.2 | mf near: cVA 0.5, Or47b 0.6, CO2 0.02 | 8.6 +/- 2.2 / 12.0 +/- 1.1 | 0.4 | 0.50 | -0.08 | 1.5 | 0.2 | 0.2 | 3.8 | 35 |
| 0.2 | mf near: cVA 0.7, Or47b 0.9, CO2 0.02 | 9.5 +/- 3.3 / 12.9 +/- 2.2 | 0.4 | 0.53 | -0.08 | 1.3 | 0.1 | 0.2 | 3.2 | 35 |
| 0.2 | cVA alone 0.06 | 15.8 +/- 6.7 / 16.7 +/- 8.9 | 0.2 | 0.63 | -0.02 | 3.4 | 0.3 | 0.1 | 6.9 | 34 |
| 0.2 | cVA alone 0.14 | 18.8 +/- 2.9 / 22.0 +/- 2.3 | 0.2 | 0.75 | -0.08 | 2.0 | 0.3 | 0.1 | 8.4 | 34 |
| 0.2 | cVA alone 0.3 | 17.2 +/- 2.3 / 18.5 +/- 0.9 | 0.2 | 0.70 | -0.03 | 0.8 | 0.3 | 0.1 | 8.4 | 34 |
| 0.2 | cVA alone 0.5 | 16.0 +/- 3.2 / 18.9 +/- 2.3 | 0.2 | 0.69 | -0.07 | 1.1 | 0.3 | 0.1 | 8.1 | 34 |
| 0.2 | cVA alone 0.7 | 14.8 +/- 1.3 / 14.9 +/- 3.2 | 0.2 | 0.63 | -0.00 | 0.7 | 0.3 | 0.1 | 7.6 | 34 |
| 0.2 | Or47b alone 0.1 | 16.8 +/- 7.9 / 15.2 +/- 9.5 | 0.3 | 0.62 | +0.04 | 2.8 | 0.2 | 0.2 | 7.0 | 34 |
| 0.2 | Or47b alone 0.4 | 14.1 +/- 0.9 / 20.2 +/- 2.2 | 0.2 | 0.68 | -0.15 | 3.2 | 0.2 | 0.2 | 6.4 | 34 |
| 0.2 | Or47b alone 0.9 | 11.1 +/- 1.3 / 15.1 +/- 1.9 | 0.2 | 0.58 | -0.10 | 4.1 | 0.2 | 0.2 | 4.7 | 34 |
| 0.2 | CO2 alone 0.003 | 18.2 +/- 2.0 / 22.6 +/- 1.3 | 0.5 | 0.75 | -0.11 | 3.1 | 0.3 | 0.2 | 9.0 | 34 |
| 0.2 | CO2 alone 0.02 | 20.6 +/- 2.3 / 21.0 +/- 3.7 | 0.5 | 0.75 | -0.01 | 2.4 | 0.3 | 0.2 | 9.1 | 34 |

- substrate 0 Hz: mf far -> near, mean DNa 5.1 -> 6.9 (+35 %), walk duty 0.21 -> 0.36; ff far -> near, DNa 0.0 -> 3.7 (+nan %), walk 0.00 -> 0.18; cVA alone 0.06 / 0.14 / 0.3 / 0.5 / 0.7: DNa 0.0 / 14.3 / 15.2 / 11.5 / 10.5; Or47b alone 0.1 / 0.4 / 0.9: 0.0 / 0.0 / 0.0; CO2 alone: 0.0 / 0.0
- substrate 0.2 Hz: mf far -> near, mean DNa 17.3 -> 11.9 (-31 %), walk duty 0.67 -> 0.55; ff far -> near, DNa 10.4 -> 14.2 (+37 %), walk 0.46 -> 0.61; cVA alone 0.06 / 0.14 / 0.3 / 0.5 / 0.7: DNa 16.2 / 20.4 / 17.9 / 17.5 / 14.8; Or47b alone 0.1 / 0.4 / 0.9: 16.0 / 17.1 / 13.1; CO2 alone: 20.4 / 20.8

## P. Cells looked at directly (male touch -> MDN by drive; male P1 / pIP10 / MN9 by input, gain and condition; jumps; a turn-toward index)

male head bristles -> MDN with touch, by condition (rows) and walking drive (columns):

| condition | Or47b (VA1v) | cVA (Or67d/DA1) | contact pheromone (ppk23/25) | food odor | none |
|---|---|---|---|---|---|
| eLN x0.25, unclear LNs inhibitory | 5.1 | 29.8 | 23.0 | 14.4 | - |
| eLN x0.25, unclear LNs inhibitory + noise 0.2 Hz | 8.1 | 24.8 | 29.4 | 7.4 | 15.5 |
| eLN x0.25, unclear LNs silent | 5.3 | 33.5 | 23.0 | 4.4 | - |
| eLN x0.25, unclear LNs silent + noise 0.2 Hz | 10.0 | 18.2 | 30.3 | 4.7 | 15.6 |
| paper's model: eLN x0.25 | 2.2 | 25.9 | 23.0 | 3.1 | - |
| paper's model: eLN x0.25 + noise 0.2 Hz | 10.8 | 15.0 | 29.1 | 2.7 | 17.7 |
| published model: eLN x1 | 0.0 | 0.0 | 23.0 | 0.0 | - |
| published model: eLN x1 + noise 0.2 Hz | 0.2 | 0.5 | 2.5 | 0.2 | 2.3 |

- male leg MNs alone -> + touch on the substrate alone (paper's model + noise): computed **0.4 -> 1.6** | paper: 0.4 -> 1.5 | ok
male gain sweep, every (gain <= 1.4, input) cell with P1 or aIPg > 0.1 Hz or MN9 > 0.5 Hz:

- gain 0.7, cVA (Or67d/DA1): P1 0.00, aIPg 0.00, MN9 7.50, pIP10 0.00
- gain 1, CO2 (V): P1 0.00, aIPg 0.00, MN9 1.83, pIP10 0.00
- gain 1, aversive odor (DA2/DL4): P1 0.00, aIPg 0.00, MN9 1.50, pIP10 0.00
- gain 1, cVA (Or67d/DA1): P1 0.05, aIPg 0.00, MN9 32.50, pIP10 3.33
- gain 1, cVA + touch: P1 0.48, aIPg 0.00, MN9 0.00, pIP10 0.00
- gain 1.4, aversive odor (DA2/DL4): P1 0.00, aIPg 0.00, MN9 1.50, pIP10 0.17
- gain 1.4, cVA (Or67d/DA1): P1 1.58, aIPg 1.40, MN9 36.50, pIP10 7.50
- gain 1.4, cVA + touch: P1 2.12, aIPg 0.44, MN9 0.00, pIP10 1.67
- gain 1.4, contact pheromone (ppk23/25): P1 0.00, aIPg 0.00, MN9 2.50, pIP10 0.00
- gain 1.4, sugar GRNs: P1 0.00, aIPg 0.00, MN9 0.83, pIP10 0.00
- male labellar GRNs -> MN9, per gain 0.5 / 0.7 / 1.0 / 1.4: computed **0.00 / 0.00 / 0.00 / 0.83** | paper: 0.00 / 0.00 / 0.00 / 0.83 | ok
male innate map, inputs with P1 > 0.1 or pIP10 > 0.5 Hz: cVA (Or67d/DA1): P1 0.05, pIP10 2.33; cVA + food: P1 0.02, pIP10 3.00; cVA + song: P1 0.08, pIP10 3.67; cVA + sugar: P1 0.08, pIP10 3.00; cVA + touch: P1 0.46, pIP10 0.00
- male sensitivity, excluding the first-version numerics: P1 max; pIP10 range; labellar -> MN9 max; touch -> MDN under the published lobe (x1): computed **0.6; 1.1-6.9; 0.0; 11.5** | paper: 0.6; 1.1-6.9; 0.0; 11.5 | ok

jumps and turning toward the other fly, from the arena logs (female logs; pre-contact = before the log's first contact; toward index = mean of turn command x sign(azimuth to the other fly), + = toward, over pre-contact ticks within 6 blocks; both signs follow observe.js / motor.py, + = left):

| chamber / cond | jump ticks (% of all ticks) | pre-contact ticks < 6 blocks | toward index | mean turn command | fraction of ticks with |turn| > 0.05 | mean |azimuth| (rad) |
|---|---|---|---|---|---|---|
| published / odor-free | ff | 0.0 | 1974 | -0.191 | +0.611 | 0.97 | 1.60 |
| published / odor-free | mf | 0.0 | 227 | +0.079 | +0.625 | 0.97 | 1.52 |
| specific / faint-smell | ff | 11.8 | 257 | +0.011 | -0.029 | 0.57 | 1.44 |
| specific / faint-smell | mf | 19.4 | 754 | +0.014 | -0.021 | 0.62 | 2.44 |
| specific / clean | ff | 0.0 | 26755 | +0.000 | +0.000 | 0.00 | 1.58 |
| specific / clean | mf | 16.3 | 419 | -0.021 | +0.050 | 0.59 | 2.33 |
| specific / noise0.2 | ff | 12.0 | 539 | +0.002 | -0.023 | 0.76 | 1.85 |
| specific / noise0.2 | mf | 13.9 | 1283 | +0.033 | -0.039 | 0.72 | 1.86 |
| specific / noise0.2-virgin | mf | 15.2 | 668 | -0.005 | -0.044 | 0.69 | 1.73 |

## Q. The virgin female on the substrate; the Or47b x CO2 window; the far levels at 10 seeds (RESEARCH_NOTES 21)

| female with a male, clean + 0.2 Hz substrate | logs | brain s | trials with contact | contact % | walk | DNa L / R far -> contact | DNp13 far -> contact | DNp37 accept far / near / contact | accept events / min | oviDN far / contact | pC1d/e + aIPg far / contact | SAG | male MDN far / contact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no state (19b) | 5 | 85 | 4 / 5 | 1.3 | 0.55 | 15.2 / 16.1 -> 2.0 / 1.8 | 5.1 -> 30.6 | 0.21 / 0.30 / 0.28 | 0.98 | 0.19 / 0.10 | 0.20 / 0.20 | 0.2 | 6.3 / 28.9 |
| virgin: SAG tonic 30 Hz (21) | 5 | 64 | 5 / 5 | 3.6 | 0.52 | 13.9 / 15.9 -> 0.3 / 1.4 | 4.1 -> 31.7 | 15.76 / 16.65 / 15.94 | 98.88 | 0.20 / 0.12 | 0.28 / 1.02 | 28.5 | 7.8 / 30.3 |
- virgin: trials with contact; contact % of ticks (mean +/- sd); no state: trials; contact %: computed **5 / 5; 3.6 +/- 3.2; 4 / 5; 1.3** | paper: 5 / 5; 3.6 +/- 3.2; 4 / 5; 1.3 | ok
- virgin: DNp37 (accept) far / near / contact; accept events / min, virgin vs no state: computed **15.8 / 16.6 / 15.9; 99 vs 1** | paper: 15.8 / 16.7 / 15.9; 99 vs 1 | ok
- virgin: pC1d/e + aIPg on contact, virgin vs no state; DNp13 far -> contact; walk; longest bout (s): computed **1.0 vs 0.2; 4.1 -> 31.7; 0.52; 1.7** | paper: 1.0 vs 0.2; 4.1 -> 31.7; 0.52; 1.7 | ok
- virgin: DNa L / R far -> contact; the male's MDN contact / near / far; his walk: computed **13.9 / 15.9 -> 0.3 / 1.4; 30 / 18 / 8; 0.28** | paper: 13.9 / 15.9 -> 0.3 / 1.4; 30 / 18 / 8; 0.28 | ok
- virgin: turn-toward index, all pre-contact ticks < 6 blocks; at 1.3-2 blocks; logs whose mean turn there is negative; per-log sign-flip p: computed **-0.005; +0.16; 5 / 5; 0.12** | paper: -0.005; +0.16; 5 / 5; 0.12 | ok

Or47b x CO2 window, no substrate (5 seeds, 2 s settle + 2 s read): DNa L / R mean +/- sd, GF, walk duty, seeds with mean DNa > 2 Hz
- Or47b 0.40 + CO2 0.02: DNa 2.0 +/- 4.6 / 2.7 +/- 6.0; GF 0.8; walk 0.11; driven seeds 1/5
- Or47b 0.45 + CO2 0.02: DNa 4.8 +/- 6.8 / 6.5 +/- 8.9; GF 1.4; walk 0.24; driven seeds 2/5
- Or47b 0.50 + CO2 0.02: DNa 4.3 +/- 5.9 / 4.7 +/- 6.4; GF 1.1; walk 0.21; driven seeds 2/5
- Or47b 0.55 + CO2 0.02: DNa 3.2 +/- 4.4 / 5.2 +/- 7.3; GF 1.6; walk 0.20; driven seeds 2/5
- Or47b 0.60 + CO2 0.02: DNa 7.3 +/- 4.1 / 10.8 +/- 6.2; GF 3.1; walk 0.42; driven seeds 4/5
- Or47b 0.65 + CO2 0.02: DNa 4.4 +/- 4.9 / 5.5 +/- 5.9; GF 1.4; walk 0.24; driven seeds 3/5
- Or47b 0.70 + CO2 0.02: DNa 2.0 +/- 4.3 / 2.0 +/- 4.0; GF 0.9; walk 0.10; driven seeds 1/5
- Or47b 0.75 + CO2 0.02: DNa 1.4 +/- 2.6 / 2.2 +/- 4.0; GF 1.0; walk 0.10; driven seeds 1/5
- Or47b 0.80 + CO2 0.02: DNa 0.9 +/- 2.0 / 1.2 +/- 2.7; GF 0.6; walk 0.06; driven seeds 1/5
- Or47b 0.85 + CO2 0.02: DNa 3.1 +/- 3.7 / 4.5 +/- 5.0; GF 2.1; walk 0.20; driven seeds 3/5
- Or47b 0.90 + CO2 0.02: DNa 2.4 +/- 3.1 / 3.5 +/- 4.3; GF 1.6; walk 0.16; driven seeds 2/5
- Or47b alone 0.40: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.45: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.50: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.55: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.60: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.65: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.70: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.75: DNa 1.4 +/- 3.0 / 1.6 +/- 3.6; GF 0.8; walk 0.08; driven seeds 1/5
- Or47b alone 0.80: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.85: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5
- Or47b alone 0.90: DNa 0.0 +/- 0.0 / 0.0 +/- 0.0; GF 0.0; walk 0.00; driven seeds 0/5

far levels on the 0.2 Hz substrate at 10 seeds (seeds 0-2 are the dose row's own and must reproduce it):
- nothing: DNa 14.9 +/- 6.2 / 15.7 +/- 7.5 (sem 1.9 / 2.4); the 3-seed row 19.6 / 19.8 (reproduced to the digit); walk 0.61; turn -0.02
- ff far: Or47b 0.10, CO2 0.003: DNa 11.8 +/- 7.1 / 11.4 +/- 9.1 (sem 2.2 / 2.9); the 3-seed row 10.5 / 10.2 (reproduced to the digit); walk 0.49; turn +0.01
- mf far: cVA 0.06, Or47b 0.10, CO2 0.003: DNa 11.2 +/- 6.1 / 11.4 +/- 8.1 (sem 1.9 / 2.6); the 3-seed row 13.5 / 16.5 (reproduced to the digit); walk 0.50; turn -0.00
- mf far: cVA 0.10, Or47b 0.10, CO2 0.003: DNa 11.0 +/- 5.5 / 11.6 +/- 7.1 (sem 1.7 / 2.2); the 3-seed row 14.4 / 18.6 (reproduced to the digit); walk 0.50; turn -0.01
- mf far: cVA 0.14, Or47b 0.10, CO2 0.003: DNa 14.8 +/- 5.0 / 17.7 +/- 6.8 (sem 1.6 / 2.2); the 3-seed row 18.8 / 21.8 (reproduced to the digit); walk 0.64; turn -0.07
- Or47b alone 0.1: DNa 14.1 +/- 7.0 / 13.3 +/- 7.0 (sem 2.2 / 2.2); the 3-seed row 16.8 / 15.2 (reproduced to the digit); walk 0.56; turn +0.02

near levels on the 0.2 Hz substrate at 10 seeds; far vs near at the same seed count (mean DNa of both sides, +/- sem over seeds):
- ff near: Or47b 0.4, CO2 0.02: DNa 13.8 +/- 3.7 / 18.1 +/- 4.1; walk 0.65; turn -0.11
- ff near: Or47b 0.6, CO2 0.02: DNa 11.8 +/- 1.2 / 16.6 +/- 1.6; walk 0.61; turn -0.12
- ff near: Or47b 0.9, CO2 0.02: DNa 9.7 +/- 2.1 / 15.7 +/- 2.2; walk 0.57; turn -0.15
- mf near: cVA 0.3, Or47b 0.4, CO2 0.02: DNa 12.5 +/- 2.1 / 17.2 +/- 3.2; walk 0.63; turn -0.12
- mf near: cVA 0.5, Or47b 0.6, CO2 0.02: DNa 9.0 +/- 1.5 / 14.2 +/- 2.2; walk 0.54; turn -0.13
- mf near: cVA 0.7, Or47b 0.9, CO2 0.02: DNa 8.1 +/- 2.0 / 12.6 +/- 1.5; walk 0.50; turn -0.11
- CO2 alone 0.02: DNa 18.4 +/- 5.0 / 18.8 +/- 7.1; walk 0.69; turn -0.01
- substrate alone: 15.3 +/- 2.1; mf far 13.0 +/- 1.8 -> mf near 12.3 +/- 0.3 (-5 %); ff far 11.6 +/- 2.5 -> ff near 14.3 +/- 0.6 (+23 %; -7 % against the substrate alone); CO2 alone 0.02: 18.6
- substrate, 10 seeds: far-level DNa means (min-max); far seed sd (min-max); the substrate alone L / R: computed **11.0-17.7; 5.0-9.1; 14.9 / 15.7** | paper: 11-18; 5-9; 15.0 / 15.7 | ok
- substrate, 10 seeds: near-level DNa L (min-max) / R (min-max); near seed sd (min-max); R - L (min-max); turn (max / min): computed **8.1-13.8 / 12.6-18.1; 1.2-4.1; 4.3-5.9; -0.11 / -0.15** | paper: 8-14 / 13-18; 1-4; 4-6; -0.11 / -0.14 | ok
- substrate, 10 seeds: paired near - far, male's odor; the other female's (mean +/- sem); CO2 alone 0.02 L / R: computed **-0.7 +/- 1.9; +2.7 +/- 2.4; 18.4 / 18.8** | paper: -0.7 +/- 1.9; +2.7 +/- 2.4; 18.4 / 18.8 | ok
- seed-cells of the 3-seed dose row against the 10-seed far / near files: differing / total (1 / 39 on 24 Sep, when the 10-seed files were made with 10 threads; 0 / 39 since the 25 Sep re-run made both with 6): computed **0 / 39** | paper: 0 / 39 | ok
- window: Or47b 0.60 + CO2 0.02 DNa L / R; Or47b-alone steps with DNa 0 / all steps: computed **7.3 / 10.8; 10 / 11** | paper: 7.3 / 10.8; 10 / 11 | ok

## R. Numbers added in draft 4 (`paper/flycraft.tex`, 25 Sep 2026): the freeze across gains, the male's cVA -> MN9

- freeze index (1 - DNa with touch / DNa alone), food odour / cVA drive, at gain 1.0; 1.4; 2.0: computed **0.69 / 0.93; 0.74 / 0.89; 0.86 / 0.93** | paper: 0.69 / 0.93; 0.74 / 0.89; 0.86 / 0.93 | ok
- male cVA -> MN9 at gain 0.7 / 1.0 / 1.4: computed **7.5 / 32.5 / 36.5** | paper: 7.5 / 32.5 / 36.5 | ok
- male cVA -> MN9 over the 13 male sensitivity conditions (min-max): computed **14.7-35.0** | paper: 14.7-35.0 | ok
- male cVA -> MN9 and DNp13 in the rewired brains (largest mean over the rewirings): computed **0.0** | paper: 0.0 | ok

---
155 cells compared with the paper's text, 0 differ beyond rounding (marked **DIFFERS**).
