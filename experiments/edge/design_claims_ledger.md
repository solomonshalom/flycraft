R = `release/pre_rerun_20260926/results/`. PN = `R/paper_numbers.md`. REP = `R/replication_20260925.md`. TA = `paper/tables_arena.tex`, which is byte-identical to `release/pre_rerun_20260926/tables_arena.tex`. RN = `RESEARCH_NOTES.md`. I recomputed every value from the frozen CSVs with small pandas reads. I also read a few static logs in `logs/` (learn_stats, learn_world probes, clean-box arena logs) and the code. Nothing was run or modified.

| claim | note | file/cell | confirmed? | strength-of-wording issue |
|---|---|---|---|---|
| dunce, fruitless, Siegel & Hall 1979, Greenspan 2000, Marder 2012; the rebuffed male courts less afterwards | main P1-2 | citations | literature, not checkable in results | none |
| FlyWire 139,255 neurons, "about fifty million synapses"; male CNS published Sep 2026 | main P3 | Dorkenwald 2024; README.md l.216 (54.5 M synapses in Shiu's table) | literature/README | "about fifty million" is fine against 54.5 M |
| Shiu model: sugar neurons drive the mouthpart neuron | main P3 | R/benchmark_flywire_shiu_min1+known+eln0.25.csv, `sugar 100 Hz alone`, MN9 L 55.0 | yes | none |
| Worm with 302 neurons (1986); debate about what it explains; MICrONS | main P4 | citations | literature | none |
| Red flowers smell of fruit, yellow of vinegar | main P5 | bot/observe.js ODOR_CLASS (poppy/red_tulip → ester; dandelion/sunflower → vinegar) | yes | "fruit" stands for the ester class |
| Body reports 20 times a second (50 ms loop) | main P5, Fig 1 | PN §M (ticks × 0.05 s) | yes | none |
| "Nothing in the body says 'if touched, back away'" | main P5 | bot/bot.js l.84-101: locomotion comes from the brain drive; REFLEXES (float in water, step-up jump on wall collision) default on (l.29) and are not disabled in experiments/run_pair.sh | yes, literally | The body does have a step-up/float reflex. Note 11 should say so. |
| Every neuron a leaky bucket; "Nothing is tuned to make the fly behave" | main P6, Fig 1 | brain/flybrain/lif.py | yes | The eLN ×0.25 and male 0.542 scales are chosen by me, but not fitted to behaviour. OK as worded. |
| Reproduces Shiu spike for spike in 2 of 3 runs; "in the third a single neuron near its threshold tips the other way" | main P6, N1 | no result file; RN §22 l.1813-1816, §14e | notes only | Understated. The divergence starts at one near-threshold event, but 284 of 592 active neurons end with different counts (23,689 vs 23,512 spikes). |
| Test 1: "survive every synapse being turned up or down by about a third" | main P6, N2 | gain_sweep_* (0.7 / 1.0 / 1.4) | yes as a design | Stated as a hard filter, but not applied evenly. Smell only works at 1.0-1.4; the MDN reflex fails; grooming and bitter were never gain-tested. |
| Test 2: vanish under degree-preserving rewiring | main P6, N2 | R/shuffle_*_global.csv | yes | See the shuffle rows below |
| Test 3: "every reasonable alternative", 14 female and 13 male versions | main P6, N2 | R/sensitivity_flywire_shiu_min1+known+eln0.25.csv (14 rows); R/sensitivity_malecns_all_min1+eln0.25.csv (13 rows) | yes (counts) | "every": the female table has 22 readout cells. Decider neurons appear only as cVA → pC1d/e and cVA → aIPg. |
| Published model: every smell the same; 81 % of 685 PNs, 65 % of 5,177 KCs, Jaccard 0.99 | main P7, N3 | R/odor_code_flywire.csv, variant shiu: pn_active 0.804 (=551/685), kc_active 0.653 (=3380/5177); R/odor_code_flywire_overlap.csv 0.99 | yes | none |
| "about fifty small clusters" (glomeruli) | main P7 | odor_code n_glomeruli = 59 | yes, loosely | none |
| Culprit is the 150 cholinergic local neurons | main P7, N3 | brain/flybrain/connectome.py l.29; RN l.597, 616 | yes (code/notes) | none |
| Known transmitter used where recorded, "11,010 neurons, most of them photoreceptors" | N3 | RN l.612: 11,010 change sign, 9,200 are photoreceptors | yes (notes) | 11,010 is the number whose sign changes |
| eLN output turned to a quarter, "the most that keeps smells apart" | main P7 | odor_code overlap between odours: ×1 0.77, ×0.5 0.53, ×0.25 0.08, ×0.1 0.01 | partial | "the most" is not shown. Only 1 / 0.5 / 0.25 / 0.1 were tested. |
| After the change: 18 % of glomeruli, 0-5 % of KCs, overlap 0.63 within / 0.08 between odours | N3 | PN §I, known+eln0.25 | yes | none |
| "I report every smell result both ways" | main P7 | paper text | NO | The short paper gives published-lobe values only for the arena and the approach index. Conditioning, freeze, male cVA and the dose rows appear under one setting. |
| "nothing that does not involve smell depends on the change" | main P7 | R/sensitivity_flywire: sugar → MN9 77.2 vs 80.6 (published signs); touch → MDN 0.0 vs 0.8; bitter 55 → 3.3 vs 58 → 6.3 (PN §A) | mostly | Small (≤3.4 Hz) non-smell shifts come from the sign rule. Say "qualitatively". |
| Sugar → mouthparts, MN9 33 / 76 / 94 Hz | main P8, N4 | R/gain_sweep_flywire_shiu_min1+known+eln0.25.csv, sugar GRNs / MN9 | yes | none |
| Shiu's 29 sugar neurons give 55 Hz; 3.3 Hz with bitter | N4 | benchmark n_driven 29; MN9 L 55.0 → 3.3 | yes | Bitter appears in no gain, shuffle or sensitivity file |
| Sound fires the escape jump; JO-A → GF 6 / 11 / 16 Hz | main P8, N4 | gain sweep, song/sound (JO-A); shuffle includes JO-A | yes | The sensitivity table has only JO-B → GF: 0.3 Hz at 50-Hz stimulus, 0.8 Hz under both ≥5-synapse rows. JO-B is 0 at gain 0.7. |
| Wind makes it groom (aBN1) | main P8, N4 | benchmark JON-CE → aBN1 13.3 Hz (JON-F 0); social_probe wind/gravity | yes, at gain 1.0 only | Not in any gain sweep, shuffle or sensitivity file, so it never passed the three tests |
| Head touch → ovipositor; DNp13 28 / 35 / 42 Hz; 28-51 Hz in all 14 conditions | main P8, N4 | gain sweep; sensitivity touch → DNp13 27.8-50.8 | yes | none |
| Touch switches off steering (freeze): food 20 / 12 → 6.8 / 3.2 Hz (index 0.69); cVA 9 / 8 → 0 / 1.2 Hz (0.93) | main P8, N4 | R/contact_stop_flywire.csv, paper's-model row | yes | none |
| Freeze index 0.69-0.93 from gain 1.0 to 2.0 | N4 | PN §R, from gain sweep | yes | Cannot be tested at 0.7 because odour drives no DNa there |
| Freeze "survives every one of my alternatives but one"; index 0.35-0.93 wherever the DNa are driven | main P8, N4 | contact_stop_flywire: 16 rows = 8 model variants ± hum | yes within that file | Overstated. Stimulus 50/150 Hz, dt 0.1/0.5, legacy numerics and the paper's own table at ≥5 synapses were never run for the freeze. The sensitivity CSV has no food+touch → DNa cell. |
| ≥5-synapse threshold reverses the freeze; "carried by the weakest connections" | main P8, N4 | contact_stop Zenodo ≥5: food 27.8 / 10.5 → 17.3 / 17.8 (index 0.08); cVA 0 / 0 → 7.2 / 17.5 | yes | Measured only on the Zenodo table with top_nt signs. "Carried by" is an inference; "depends on" is safer. |
| Male answers cVA "and no other smell at all"; N4 "every other odour 0" | main P8, N4 | R/gain_sweep_malecns_all_min1+eln0.25.csv: other odours → DNp13 0 at every gain. At gain 1.4 food/CO2/Or47b/Or88a/aversive → PPL1 18-30 Hz, song MNs 5-10 Hz, MDN 1-5 Hz. R/social_probe_malecns (gain 1.0): CO2/Or83c/aversive/cVA-long → MN9 1.3-2.8 Hz; food → PPL1 1.9 Hz | NO for "at all" | True only for DNp13 (and roughly for MN9 at gain 1.0) |
| Male legs touch female → MDN; ppk23/25 → MDN 27 Hz at gain 1.0 only; "fails the gentlest version of my first test" | main P8, N4 | gain_sweep_malecns ppk23/25 → MDN 0 / 26.8 / 1.8 | yes (numbers) | "gentlest version" understates it: fails at 0.7 and at 1.4. Head touch → MDN 0 / 10.7 / 11.8, and 0 at 50-Hz stimulus (sensitivity_malecns). |
| N4 ppk23/25 → wing motor neurons 10-22 Hz | N4 | song MNs 10 / 20 / 22 / 11 at gain 0.5 / 0.7 / 1.0 / 1.4 | minor mismatch | 11-22 Hz at the paper's gains; the 10 is gain 0.5 |
| "Scramble the wiring and every one of these reflexes disappears"; N2/N4 every readout 0-2 Hz, largest stray 7 Hz, 99.8 % moved | main P8, N2, N4 | R/shuffle_flywire_…_global.csv: mean max 2.12 Hz, single-trial max 7.2 (MDN), frac_moved 0.9986. Male file: mean max 2.19 Hz, frac_moved 0.9981 | yes for the inputs tested | Grooming (JO-CE) and bitter are not in the shuffle files; the freeze is untestable there (no DNa drive) |
| Deciders silent "whatever the fly senses, in every version of the model" | main P9 | R/social_probe_flywire (27 inputs): pC1a / pC1b/c / pC1d/e / aIPg / vpoDN / oviDN max 0.0. Gain sweep: pC1a, pC1d/e, aIPg, vpoDN 0.0 at ≤1.4 | female yes; male NO | Male P1 2.1-2.3 Hz and aIPg 1.4-1.9 Hz at gain 1.4; P1 2.5 Hz under legacy numerics |
| N5: those neurons at 0.0 Hz "at every gain up to 1.4 and in all 14 conditions" | N5 | gain sweep has no pC1b/c or oviDN column. Sensitivity has only cVA → pC1d/e and cVA → aIPg | NO (coverage) | Only the gain-1.0 map covers all six neurons over all inputs |
| N5 "male P1 stays at or below 0.6 Hz" | N5 | PN §B: 0.6 at ≤1.0; 2.3 at 1.4 | NO at 1.4 | Add "at gain ≤1.0" |
| N5 pIP10 answers cVA only, at 2-3.5 Hz | N5 | social_probe_malecns: cVA 2.3, +food 3.0, +sugar 3.0, +song 3.7 Hz; gain 1.4 cVA 7.5 Hz | minor mismatch | 2.3-3.7 Hz at gain 1.0 |
| Real pC1 respond to cVA and song; real P1 to touch | main P9 | Zhou 2014; Kohatsu 2011 | literature | none |
| Clean box: two females still for more than 2 min of brain time, "every neuron at rest" | main P9, N5 | R/encounter_trials.csv clean ff: 10 logs, 135 ± 6 s (min 127), every readout 0.00 | readouts yes; "every neuron" NO | In each clean-box log (e.g. logs/fly1_off-flywire-known-eln0.25_20260918-231854.csv) hz_total_spikes ≈ 41,000 per 50-ms tick and hz_active_frac = 0.08 throughout. This is the eye (RN §19f). DN all and KC are 0. |
| "the published model has no activity of its own" | main P9 | R/precontact_dose_…csv, "nothing" at 0 Hz: active 0 % | yes (offline, no eye) | none |
| A real fly in an empty dish soon walks | main P9 | Martin 2004 | literature | none |
| Virgin (SAG) state: pC1a 21, pC1b/c 19, vpoDN 5.7 Hz, all from 0; with touch pC1d/e 6.2 Hz | main P10, N6 | R/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv; PN §F | yes | State results come only from gain 1.0; no gain, shuffle or sensitivity test (not claimed, but the three-test rule is not applied) |
| Male P1 state → pIP10 50, TN1 8, song MNs 28 Hz | main P10, N6 | state_probe_malecns: 50.4 / 8.2 / 27.6 Hz | yes | none |
| Hunger/fullness "changes nothing, in either sex"; N6 "at most 7 Hz on MN9, as much as unrelated states" | main P10, N6 | state_probe_flywire: NPF sugar → MN9 79.4 → 86.2 Hz (+6.8; SD 3.1-3.4, n = 5). Unrelated states +3.6 to +4.4. Male max 5.8 Hz (SIFa, MDN) | partial | "changes nothing" is too strong. NPF's +6.8 exceeds every non-feeding state and points the hunger way (within about 2 SEM). |
| No state starts egg-laying | main P10, N6 | oviDN max 0.0 over every state and input | yes | none |
| Mated female extends ovipositor no more often than a virgin; DNp13 36 Hz either way | main P10, N6 | touch → DNp13: 35.6 (no state) vs 36.2 Hz (SAG) | yes | "Mated" means the no-state run; say so |
| N6 "state results are identical under both smell-centre settings" | N6 | PN §F: identical for state-alone cells. With odour: SAG+cVA+touch → pC1d/e 1.0 vs 7.1; SAG+cVA → pC1a 17.5 vs 21.5; P1+food → MN9 19.4 vs 2.6; P1+food → pIP10 40.5 vs 49.1 | NO as worded | Limit to "without an odour" |
| Sugar and bitter "never reach the teaching neurons"; N7 0.0 Hz in every dopamine neuron | main P11, N7 | social_probe_flywire PAM/PPL1 per-seed max 0.0 for sugar/bitter/touch; gain sweep sugar/touch → PAM/PPL1 0.0 at gain 0.5-1.4 | yes | "every dopamine neuron" means the PAM and PPL1 sets only |
| Learning constants 0.3 /s, floor 10 %, 1 s trace; US 50 Hz; three 10-s cycles (Tully) | N7 | brain/flybrain/plasticity.py l.55-62; experiments/conditioning.py l.26-28 | yes | none |
| Sugar-paired odour keeps "a tenth" (0.10-0.11) | main P11, N7 | R/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_*: CS+ 0.095-0.107 | yes | none |
| Other odour "about three-fifths"; N7 0.59-0.66 | main P11, N7 | CS- 0.593-0.697 (reward_ester-vs-vinegar seed0 is 0.697; it was 0.657 before the 25 Sep re-run) | NO | Should read 0.59-0.70 |
| Learning index 0.54 ± 0.02 (n = 6) | N7 | recomputed 0.548 ± 0.030 | minor mismatch | 0.55 ± 0.03 |
| 0.04 without a teaching signal | N7 | us-wiring, n = 4: 0.03 ± 0.04 | minor mismatch | none |
| 0.21 ± 0.14 for punishment | N7 | recomputed 0.212 ± 0.138 | yes | Hides odour order: vinegar-paired 0.30-0.38, ester-paired 0.07-0.08 |
| Male 0.80 and 0.77 | N7 | conditioning_malecns: n = 2 each (one seed per order) | yes | none |
| "the same happened in Minecraft"; N7 0.37 with sugar | main P11, N7 | logs/learn_world6_probe_{pre,post}.json (PN §M): ester 0.289 vs vinegar 0.662 | yes | Much weaker than offline (0.29 vs 0.10 kept) |
| N7 0.29 with bitter | N7 | world5: vinegar punishment compartment 0.090 vs ester 0.384 | number yes, meaning NO | World6 had 0 bitter ticks and gives the same aversive index, 0.31 (0.131 / 0.438), from odour-driven PPL1 alone. World5's appetitive index was 0.02. |
| "It walked and turned as before" | main P11 | logs/fly1_mb-…_20260917-162815_learn_stats.csv (world4): walk_B 0.672 → 0.655, turn_B 0.610 → 0.593 (365 / 385 ticks) | partial | World5 pre/post on B rests on 14 / 8 ticks (turn +0.01 → +0.59). World6 has no pre phase (RN §20f ix). |
| "in one run it walked straight back onto the flowers that tasted bitter" | main P11 | world4 post: frac_in_B 0.434, 196 bitter ticks (RN §18i) | yes | none |
| N7 "No descending neuron changes with training" | N7 | PN §K: after reward training, CS+ abs dDNa 3.5-8.5 Hz, approach change -6.5 to +5.5. No-teaching control 3.5-6.5 Hz | partial | Changes happen but match the control. Say "no training-specific change". |
| N7 "the reward output neurons, driven at 40 Hz, reach none" | N7 | R/expression_probe_flywire_…csv; RN §18g: the reward MBONs have 0 DN targets, but with their targets driven at 10/20/40 Hz, silencing the MBONs raises DNa L +5.5 / +5.0 / +4.0 Hz (about 2 seed-SD), approach +1.8 to +4.0 Hz | NO as worded | It was the targets that were driven at 40 Hz, and the MBONs do shift steering by 4-5.5 Hz |
| The 28 DN targets of the punishment MBONs within 0.6 Hz intact vs silenced | N7 | PN §L: 0.54 Hz | yes | none |
| "a notebook that nobody downstream reads" | main P11 | follows from the rows above | interpretation | Worth at most about 5 Hz of turning, not zero |
| Box 13 blocks across, white walls, no food | main P12, N8 | experiments/encounter_trials.sh (ARENA_R=6, NO_FOOD=1); RN §20f xiv | yes | none |
| Flies start 4 blocks apart | N8 | experiments/trials.sh POS: trials 1-4 at 4 blocks; trial 5 at (-2,-2) / (2,2) = 5.7 blocks | partial | Say "4-6 blocks" |
| 5 trials per condition, 300 s (180 s first series, 600 s replication hum/virgin); contact within 1.3 blocks | N8 | TA; observe.js l.261 (1.3); RN §22b | yes | none |
| Published smell centre: two females circle left and never meet | main P12 | TA 0/5 trials with contact, DNa 36.1 / 4.2 Hz; PN §P mean turn +0.611 (+ = left) | yes | none |
| Faint flower smell left by an earlier run | main P12 | PN §N odor_max 0.70 in faint-smell, 0.00 in every other chamber | yes | none |
| Females met by chance and stayed together; steering off, ovipositors on | main P12 | TA faint ff: 4/5, 39.5 ± 34.4 %, DNa 13.7 / 13.5 → 0.4 / 0.1 Hz, DNp13 5.0 → 32.9 Hz, toward index +0.011 | yes | none |
| Pressed together for up to 86 s | main P12, Fig 3 | faint ff trial t3, longest bout 86.2 s. figures_print.py l.138 shows the longest-bout trial | yes | The caption does not say the shown trial is the longest one |
| A real female walks away | main P12 | uncited | literature | Add a citation |
| Male and female met far less; each meeting ended within seconds, male walking backwards | main P12 | TA faint mf: 1/5, 1.2 %, longest 1.9 s, MDN 40 Hz on contact | yes | Only one trial had contact |
| Clean box: nothing moved except the female walking on his pheromone; he stood still until touched, then backed away | main P12 | TA clean ff all 0; clean mf female walk 0.48, male walk 0.03 when untouched, MDN 48 / 15 / 4 Hz | yes | none |
| Hum: 0.2 Hz Poisson input to every neuron, about one spike per 5 s, measured alone | main P12, N8 | R/noise_floor_* | yes | none |
| Floors: DNp13 5.3 Hz, 2 lunges a minute, a jump in 12 % of moments | N8 | PN §N: 5.3; 2.0 per min; 11.9 % | yes | none |
| On the hum females met and stayed together; males met and backed out | main P12 | TA hum ff 3/5, 11.2 %, 15.1 s (replication 5/5, 59 %, 31 s); mf MDN 29 / 31 Hz | yes | none |
| "nobody sang or fought" | main P12 | R/encounter_trials.csv: male pIP10 0.19-0.34 Hz and P1 0.18-0.22 Hz (the hum floor). The male's sing-act counter (song MNs, motor.py l.124) logs 20-25 acts/min on the hum, 10/min in the clean box, 83/min under the published lobe. Female lunges 2.9-5.0/min in male-female hum series vs the 2/min floor | partial | Say "no song command or aggression-neuron activity above the hum's floor", and give a floor for sing acts |
| "in no box did it steer towards its partner by more than a whisker"; N9 -0.02 to +0.03, 0.00 to +0.04, -0.19 / +0.08 | main P13, N9 | TA toward column | yes | The replication virgin's +0.040 is 16 % of the mean absolute turn (0.25) |
| Female leaned towards the male "in 24 of 33 recordings"; p = 0.014; +0.015; 6 % | main P13, N9 | REP pooled table: 35 male-female logs "turn at all", 24 toward / 9 away / 2 zero, p 0.014, +0.015, 0.250, +0.06 | partial | 33 is the number that lean either way, not the number that turn at all (35) |
| "about a twentieth of her turning" | main P13 | 6 % | yes | none |
| Female pairs 13 and 9, p = 0.52 | N9 | REP | yes | none |
| N9 "cVA on one antenna turns the female towards it by 0.6-2.3 Hz"; main P13 "about the size of the pull his pheromone has" | main P13, N9 | R/odor_dose_flywire_shiu_min1+known+eln0.25.csv, cVA steering (mean of L/R, 3 seeds): 25 Hz 0.0, 50 +1.7, 75 +0.6, 100 -0.2, 150 +2.3. Per-seed side values run from -6 to +8 | NO | The 100-Hz cell is -0.2 and the sign is inconsistent across seeds. The main-text comparison also sets a turn index against Hz. |
| Food odours turn her away | N9, N5 | 20 of 20 food-type cells -0.7 to -9.2 Hz | yes | none |
| Flies are blind; real males find females by sight | main P13 | Ribeiro 2018 | literature | See the eye row below |
| Virgin's acceptance neuron fires near or far; about 100 acts/min | main P13 | PN §Q: DNp37 15.8 / 16.6 / 15.9 Hz; 99/min (replication 91) | yes | none |
| "she never walked towards him" | main P13 | virgin toward index -0.005 (original), +0.040 (replication, the largest of any series), +0.16 at 1.3-2 blocks (p = 0.12, PN §Q) | partial | "never" is too strong; "did not reliably" fits |
| Real virgins wait for the male | main P13 | uncited | literature | Add a citation |
| Replication: 3 boxes, 25 new trials | main P14, N10 | encounter_trials.csv rep-*: 10 + 10 + 5 trials | yes | none |
| Replication clean females still | main P14 | TA rep clean ff 0/5, all 0 | yes | none |
| Replication hum females met and stayed together | main P14 | TA rep hum ff 5/5, 59.1 %, 31.1 s | yes | none |
| "the male backed out of every meeting" | main P14 | rep male logs with contact: MDN on contact 20-37 Hz per log (min 20.0) vs 4-8 Hz far | yes, per log | Individual bouts were not recorded |
| Virgin signalled acceptance to no one in particular | main P14 | rep DNp37 15.9 / 16.4 / 16.6 Hz | yes | none |
| The map holds how to eat, jump, groom, freeze and back away | main P15 | rows above | partial | Grooming never passed tests 1-3; backing away fails test 1 |
| The map does not hold whom to court, when to fight, or a reason to walk | main P15 | decider and clean-box rows | yes (female) | Male P1 reaches 2 Hz at gain 1.4 |
| States that work are the synaptic ones | main P10, P15 | state rows | interpretation | See the NPF +6.8 Hz row |
| "no chemistry beyond its synapses, no electrical connections and no eyes"; N11 vision not modelled | main P16, N11 | Every arena trial ran with the eye: photoreceptors driven, about 8 % of neurons active (RN §19f: "photoreceptor drive dies in the medulla") | partial | "No eyes" is wrong. Say "an eye whose signal never gets past the medulla". |
| Closing: "for two minutes, every neuron at rest" | main P17 | same as the clean-box row | NO for every neuron | none |
| "a script recomputes every number in it"; N10 "A script checks 155 numbers of this paper … none differ" | author line, N10 | experiments/paper_numbers.py: expected values hard-coded from PAPER.md/draft 4 (l.2, l.54), not parsed from flycraft.tex. Tolerance max(0.55, 3 %) (l.37-40) lets any sub-1 value pass (CS- 0.66 vs 0.70, LI 0.54 vs 0.55 pass). Not checked: N1/N3 counts, N5 0.7-9 / 16-29 (printed, never compared), N9 0.6-2.3 and the sign test, N10 file counts. PN shows 155 / 0 | partial | Overclaim. "Every number" and "none differ" are not supported. |
| LIF constants (-52 / -45 mV, 20 / 5 ms, 2.2 ms, 1.8 ms, 0.275 mV, 68.75 mV, dt 0.2 ms) | N1 | brain/flybrain/lif.py l.41-53 | yes | none |
| "results identical at 0.1-0.5 ms" | N1 | R/sensitivity_flywire: sugar → MN9 77.2 / 87.8 (dt 0.1) / 86.1 (dt 0.5); cVA → DNa L 10.0 / 7.5 / 7.8; food → GF 4.4 / 2.5 / 5.6; max difference 10.6 Hz | NO | Say "qualitatively the same" |
| 15,090,883 connections, 54.5 M synapses; MaleCNS 164,439 neurons, 25.6 M connections, scale 0.542 | N1 | README.md l.8, 56, 216 | yes (README) | none |
| Brian2 2.10.1, 3 seeds: 2 identical; 23,689 vs 23,512 spikes; r 0.9999 | N1 | RN l.1813-1816 | notes only, no result file | 284 of 592 neurons differ |
| "smell responses need 1.0 or more" | N2 | female DNa at gain 0.7 ≤ 0.8 Hz; male cVA → DNp13 7.8 Hz and MN9 7.5 Hz at 0.7 | partial | True for the female only |
| Replication clean box at 300 s, hum/virgin at 600 s; clean male-female 14 ± 6 s vs 90 s | N10 | encounter_trials rep-clean mf brain_s 14.2 ± 6.5; clean 90.0 ± 1.4 | yes | none |
| 123 files, 54 identical to the digit | N10 | R/rerun_20260925_diff.md | yes | none |
| Under my model at most 3.3 Hz (4.5 Hz steering); at most 0.004 in learned weights | N10 | diff: precontact far DNa R 3.25; odor_dose approach 4.5; w_over_w0 ≤ 0.00367 | yes, literally | The drive ratio the paper reports moved by 0.04 (CS- 0.657 → 0.697) |
| "One number changed (bitter suppression 3.3; earlier 1.7)" | N10 | RN §22 / §22b; prior backup release/pre_rerun_20260925 | NO | CS- retention (0.66 → 0.70) and appetitive LI (0.54 → 0.55) also changed, and the paper still carries the old values |
| Smell carries 16 blocks; 100 Hz bench, 150 Hz body, 200 Hz touch | N11 | observe.js l.196; senses.py l.30-33, 200 | yes | none |
| Female nerve cord not modelled; Lappalainen bridge exists but no result uses it | N11 | RN §14n, §19f | yes | none |
| Arena table (every row) | Table | TA vs PN §N and REP | yes | none |

**What most needs fixing:**
1. "Every neuron at rest" (P9, P17) and "no eyes" (P16, Note 11): the arena logs show about 8 % of neurons active from the eye.
2. Note 1 "identical at 0.1-0.5 ms": the sensitivity table shows differences of up to about 10 Hz.
3. Note 7 numbers: CS- retention should be 0.59-0.70, the appetitive index 0.55 ± 0.03 and the no-teaching control 0.03. Note 10's "one number changed" is wrong for the same reason.
4. The "0.29 with bitter" in-world result: the world6 run with no bitter gives 0.31.
5. The expression-probe wording ("reach none") and "no descending neuron changes".
6. The cVA steering of 0.6-2.3 Hz (the file has -0.2 at 100 Hz) and the approach sentence that rests on it.
7. "No sign rule steers towards food" and "16-29 Hz whatever the odour".
8. The male "no other smell at all": other odours drive PPL1, song MNs and MDN at gain 1.4.
9. Decider coverage "at every gain … all 14 conditions", and male P1 at gain 1.4.
10. "Hunger changes nothing" and the state results "identical" under both smell-centre settings.
11. The three-test rule is stated as absolute, but grooming, bitter and parts of sound and the freeze were never tested against it.
12. "Nobody sang or fought", "she never walked towards him", and "24 of 33 that turn at all" (the file says 35).
13. paper_numbers.py cannot back "every number": its expected values come from the old draft and its tolerance hides sub-1 mismatches.