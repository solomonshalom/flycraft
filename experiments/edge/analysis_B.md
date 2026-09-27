
### [freeze-touch] Freeze is touch-specific (DECISIONS item 7 specificity controls). Paper l.93: 'Touch also switched off the neurons she steers with ... so a touched female freezes'; Note 4 freeze index 0.69 (food), 0.93 (cVA).
STEPS: freeze-minsyn: experiments/results_edge/freeze-minsyn/minsyn.csv (520 rows = 8 conditions x 13 drives x 5 seeds, 600 ms, all terms @100 Hz). Rows conn=shiu, min_syn_mem=1 are the paper's model. Index = 1 - mean(DNa L + DNa R with the extra input) / mean(DNa L + DNa R, food odor@100 alone), as in contact_stop.py; per-seed indices are paired by seed. Other columns read: 'DN all', 'MN9', 'aBN1', 'GF jump', 'recruited_spikes', 'active_frac'. Script not kept.
CRITERION: DECISIONS.md item 7 added the controls (food@100 plus sugar GRNs, bitter GRNs, JO-A, JO-CE and 3 random 1,417-neuron non-touch sensory sets) but fixed no numeric line. My scoring, using the suite's own freeze line (S10.3/S13: index >= 0.35): touch counts as specific if every control index in the paper's model is below 0.35 and below half of touch's index.
NUMBERS: Paper's model, n=5 seeds; pooled index (per-seed mean +- sd):
- food + touch 0.694 (0.69 +- 0.06): DNa L/R 20.3/12.3 -> 6.8/3.2 Hz.
- Controls added to food: sugar GRNs -0.03 (-0.04 +- 0.19); bitter GRNs -0.08 (-0.09 +- 0.11); JO-A -0.07 (-0.09 +- 0.18); JO-CE 0.09 (0.08 +- 0.17); random sensory d0 -0.12 (-0.14 +- 0.21), d1 -0.09 (-0.11 +- 0.19), d2 0.13 (0.11 +- 0.18). The largest single-seed control value is 0.36 (d2).
- The controls are live inputs: sugar drives MN9 to 72.7 Hz, JO-CE drives aBN1 to 22 Hz and JO-A drives GF to 4.5 Hz.
- 'DN all': touch raises it from 1.27 to 8.38 Hz; the controls give 1.28-2.30 Hz. Touch therefore silences DNa01/02 while most descending neurons speed up. DNp09 is 0 throughout.
- Other thresholds and tables: every control stays <= 0.27 at k <= 3. The one exception anywhere is Zenodo k=5, where JO-CE gives 0.33, above touch's 0.08.
- Caveat: the random sets are 74-76 % photoreceptors (1,046-1,074 of 1,417, per the log). The sugar, bitter, JO-A and JO-CE controls are the stronger test.
VERDICT KEEP
PAPER: No main-text change for specificity. (The wording of l.93 changes for other reasons; see the partial-touch item.)
NOTES: Note 4, add: "The freeze is specific to touch. Adding sugar, bitter, JO-A or JO-CE input, or 1,417 random non-touch sensory neurons, to the food odour instead of touch gives indices of -0.12 to 0.13 (5 seeds each), against 0.69 +- 0.06 for touch. Touch silences DNa01/02 while it raises the mean descending neuron from 1.3 to 8.4 Hz."

### [freeze-touch] Which connection threshold abolishes the freeze, and in which table. l.93: 'remove the connections made of fewer than five synapses ... and touch excites the steering neurons instead, so the freeze is carried by the weakest connections in the brain'; Note 4: 'reverses only under the >=5-synapse threshold'.
STEPS: minsyn.csv, 5 seeds, 600 ms, touch @100 Hz, known signs + eLN x0.25. Thresholds were applied in memory (min_syn_mem k = 1, 2, 3, 5) to the Shiu table and the Zenodo table (top_nt signs; 7,832 against 11,010 sign flips; 131 against 150 eLN, per logs/edge/guarded_freeze-minsyn.out). Engine checks:
- The k=5 in-memory threshold equals the min5 cache in both tables (minsyn.json: 2,700,429 connections, arrays identical).
- Shiu k=1, Zenodo k=1 and Zenodo k=5 food/cVA +- touch reproduce experiments/results/contact_stop_flywire.csv (means and sds of 8 readouts, max|diff| <= 6.7e-16).
- Shiu k=5 seeds 0-2 reproduce every food/cVA/touch cell of sensitivity_flywire_shiu_min1+known+eln0.25.csv, row 'connections >= 5 synapses', to the digit.
CRITERION: S13 (design_plan): keep the sentence if both tables keep an index >= 0.35 at k <= 3 and flip at k = 5 (index <= 0.1, with touch raising DNa). If the Shiu table still freezes at 5, narrow the sentence to the Zenodo table. If the flip happens at k = 2-3, say the freeze depends on 1-2-synapse connections. §4 item 7 already requires 'depends on' in place of 'carried by'.
NUMBERS: Pooled index (per-seed mean +- sd), n=5, at k = 1 / 2 / 3 / 5:
- Shiu table, food: 0.694 (0.69 +- 0.06) / 0.588 (0.59 +- 0.08) / 0.371 (0.37 +- 0.09) / -0.004 (-0.01 +- 0.15).
- Zenodo table, food: 0.708 (0.70 +- 0.12) / 0.554 (0.55 +- 0.05) / 0.306 (0.29 +- 0.13) / 0.083 (0.08 +- 0.09).
- Shiu table, cVA: 0.933 (0.93 +- 0.05) / 0.695 (0.69 +- 0.12) / 0.19 (cVA alone gives DNa L+R 5-19; in one seed touch raises it from 5.0 to 15.0) / not applicable (cVA alone gives DNa 0/0).
- Zenodo table, cVA: cVA alone gives DNa <= 0.6 Hz at every k, so no test.

Touch alone raises DNa R step by step as k rises (Shiu 0.83 / 2.5 / 7.7 / 18.7 Hz; Zenodo 1.5 / 3.3 / 9.5 / 17.8), DNa L 6.0 (Shiu) and 7.5 (Zenodo) at k=5.

At k=5 (Shiu / Zenodo):
- cVA + touch: DNa 0 -> 11.4 / 12.3 Hz.
- food + touch: no net change (20.1 -> 20.2 / 19.2 -> 17.6), but redistributed (DNa R 18.3 -> 22.3 / 10.5 -> 17.8).

S13 outcome:
- It fails its keep rule: Zenodo k=3 gives 0.31 < 0.35, and Shiu cVA k=3 gives 0.19.
- Both tables flip at k=5, so 'narrow to Zenodo' is not triggered. This settles verify_wording 7(3): the paper's own table also loses the freeze.
- The loss is graded: removing single-synapse connections (k=2) already costs 0.10-0.24.
VERDICT REWORD
PAPER: l.93: "The freeze survives every one of my alternatives but one: remove the connections made of fewer than five synapses, a common way of tidying a wiring diagram, and touch no longer quiets the steering neurons (on its own it now excites them), so the freeze depends on the weakest connections in the brain." (This is the same as analysis_A's corrected sentence.)
NOTES: Note 4: replace 'and reverses only under the >=5-synapse threshold' with: "It weakens step by step as weak connections are removed. Dropping connections of fewer than 2, 3 and 5 synapses takes it from 0.69 to 0.59, 0.37 and -0.00 in Shiu et al.'s table, and from 0.71 to 0.55, 0.31 and 0.08 in the Zenodo table (food odour; cVA 0.93, 0.70 and 0.19; 5 seeds). Meanwhile touch on its own drives the right steering neuron ever harder (0.8, 2.5, 7.7 and 18.7 Hz)." This replaces analysis_A's ambiguous 'food 0.37 and 0.31', which are the two tables at k=3, not the '1- and 2-synapse' steps.

### [freeze-touch] Does the freeze need all 1,417 bristles at 200 Hz, or do a partial, one-sided or weaker touch do it? (l.93 'a touched female freezes'; the arena drives all 1,417 BM_ neurons of both sides at 200 Hz on any contact.)
STEPS: touch-dose: experiments/results_edge/touch-dose/touch_dose.csv (275 rows, 5 seeds, 600 ms, paper's model).
- Rate block: all BM_ neurons at 0-300 Hz, alone and on food@100 or cVA@100.
- Fraction block: random 3/10/25/50 % subsets, draws 0-2, at 200 Hz on food@100; plus BM_Ant@200 and BM_InOm@200.
- Side block: 'BM left' (705) or 'BM right' (712) at 100 or 200 Hz on food or cVA.
Index against the rate block's food@100 / cVA@100 rows (same seeds), overall and per side (1 - DNa L_with / DNa L_alone, and the same for R). Engine check: food@100 +- touch@100 and cVA@100 +- touch@100 reproduce contact_stop_flywire.csv's paper-model rows (max|diff| 2.2e-16). Script not kept.
CRITERION: S14: keep 'a general reflex' if the freeze index is >= 0.35 on both DNa for left-only and for right-only touch, and for <= 25 % of the bristles at 200 Hz; it rises with touch rate and holds for 5 s; and DNp13 is >= 10 Hz at 200 Hz for <= 25 % and for one side. Otherwise say 'a whole-head touch' and rewrite the closing prediction.
NUMBERS: Rate, all 1,417 bristles, per-seed index mean +- sd (n=5) at 10 / 25 / 50 / 100 / 150 / 200 / 300 Hz:
- food: -0.25+-0.15 / -0.10+-0.14 / 0.32+-0.06 / 0.69+-0.06 / 0.76+-0.05 / 0.76+-0.07 / 0.83+-0.02.
- cVA: 0.13+-0.19 / 0.25+-0.26 / 0.68+-0.08 / 0.93+-0.05 / 0.95+-0.00 / 0.95+-0.00 / 0.94+-0.02.

Fraction at 200 Hz on food, 3 draws x 5 seeds (n=15):
- 3 % (43 neurons): -0.13+-0.17.
- 10 % (142): -0.44+-0.25; DNa rises from 16.3 to 23.2 Hz, e.g. DNa R 12.3 -> 29.0 in draw 0.
- 25 % (354): 0.12+-0.17 (draws 0.23 / 0.13 / 0.03).
- 50 % (708): 0.48+-0.12.
- 100 %: 0.76+-0.07 (n=5).
- BM_InOm, the 1,113 eye bristles: 0.59+-0.07. BM_Ant, 41 neurons: 0.12+-0.12. These two are not size-matched.

One side, per-seed index (index on DNa L / on DNa R):
- food, left@100: 0.21+-0.12 (0.22 / 0.23).
- food, right@100: 0.52+-0.14 (0.53 / 0.53).
- food, left@200: 0.16+-0.17 (-0.02 / 0.50).
- food, right@200: 0.69+-0.09 (0.70 / 0.68).
- cVA, left@100: 0.57 (L 0.27, R 0.92).
- cVA, left@200: 0.29 (L -0.25: DNa L rises from 9.3 to 11.7).
- cVA, right@200: 0.91+-0.06 (0.89 / 0.94).

S14 outcome: it FAILS for <= 25 % (0.12) and for left-only touch (0.16-0.29, with the left DNa spared or raised). It passes for right-only touch.

Through the arena decoder (walk = 1 - exp(-(DNp09 + DNaL + DNaR)/3 / 10 Hz)), food alone gives a walk drive of 0.66 and food + touch@100 gives 0.28 (0.73 -> 0.20 over 5 s at 200 Hz). The 'freeze' is therefore a drop in walking drive, not a halt.
VERDICT REWORD
PAPER: l.93: "A touch over most of her head also silenced the two steering neurons from which I read her walking, which I had not expected, so a female touched all over the head freezes; a touch to a few bristles does not." Full paragraph, merging analysis_A's reflex wording: "With the wiring alone, the fly has reflexes \note{4}. Sugar makes it work its mouthparts, and bitter makes it stop, though with every synapse a third stronger bitter only slows it. A loud sound fires its escape jump. A strong wind on the antenna makes it groom, though not with every synapse a third weaker. When a female's head is touched she extends her ovipositor, the movement a mated female uses to keep a male off \citep{mezzera2020ovipositor}. A touch over most of her head also silenced the two steering neurons from which I read her walking, which I had not expected, so a female touched all over the head freezes; a touch to a few bristles does not. The freeze survives every one of my alternatives but one: remove the connections made of fewer than five synapses, a common way of tidying a wiring diagram, and touch no longer quiets the steering neurons (on its own it now excites them), so the freeze depends on the weakest connections in the brain." l.121 (optional): 'how to freeze when touched all over the head'. l.101 stays as written: the arena stimulus is exactly the whole-head 200 Hz case.
NOTES: Note 4, add: "The freeze needs a strong touch. With all 1,417 bristles the index is -0.25, -0.10, 0.32, 0.69, 0.76, 0.76 and 0.83 at 10, 25, 50, 100, 150, 200 and 300 Hz (food odour; cVA 0.13 to 0.95; 5 seeds). At 200 Hz, random 3, 10, 25 and 50 % of the bristles give -0.13 +- 0.17, -0.44 +- 0.25, 0.12 +- 0.17 and 0.48 +- 0.12 (3 draws x 5 seeds), so a light touch speeds the steering neurons up. The freeze is lateralised: the right-side bristles alone give 0.69 +- 0.09, but the left-side ones give 0.16 +- 0.17 and spare the left steering neuron." Note 11 (from verify_wording 24c): "200 Hz for touch, applied to all 1,417 head and eye bristle neurons of both sides whenever the fly is within 1.3 blocks of another fly or presses on a wall."

### [freeze-touch] The freeze rises with touch rate and holds for 5 s (S14 second bullet; implicit in l.101 'stayed together because touch switched off their steering').
STEPS: touch-5s: experiments/results_edge/touch-dose/touch_5s.csv (50 rows = 2 drives x 5 seeds x 5 one-second bins, no off phase). Per-seed, per-bin index = 1 - (DNa L + DNa R)_touch / (DNa L + DNa R)_food. Engine check: bin 0 of food@100 equals social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv 'food odor' seeds 0-4 exactly (120 cells; total_spikes 79,247-81,841 identical). The rate trend is from touch_dose.csv (previous item). Script not kept.
CRITERION: S14: the index rises with touch rate and holds for 5 s (the 5-s run is food@100 +- all bristles @200 in 1-s bins).
NUMBERS: Index by 1-s bin, mean +- sd (n=5): 0.78+-0.05, 0.82+-0.04, 0.83+-0.04, 0.83+-0.03, 0.86+-0.02 (slope +0.015 per s). Over the whole 5 s: 0.826 +- 0.013 per seed (0.815-0.849).

Over 5 s (bins 0-4):
- food alone: DNa L/R 23.2/15.8 Hz.
- with touch: DNa L 7.2 -> 5.6 Hz, DNa R 0.0-0.7 Hz.
- DNp13 34.2-35.1 Hz, DN all 12.1-12.2 Hz, feed MNs 22.2-22.5 Hz, all flat.
- The state's aSP22 and GF stay at 0.0 with touch in every bin.

The rate trend is monotone from 10 Hz up to a plateau at 150-300 Hz (0.76-0.83 food, 0.94-0.95 cVA). The 10-s support is analysis_A's persistence run: with pheromones + song + touch, DNa stays <= 1 Hz for 10 s.
VERDICT KEEP
PAPER: No change (l.101's mechanism holds for the arena's whole-head 200 Hz touch).
NOTES: Note 4, add: "With every bristle at 200 Hz the freeze holds, and slightly deepens, over 5 s: 0.78 +- 0.05 in the first second and 0.86 +- 0.02 in the fifth (5 seeds)."

### [freeze-touch] What the freeze removes, given the self-sustained state (analysis_A persistence): odour-driven DNa is read in a ~2,000-neuron self-sustaining state. Is the freeze a selective silencing of DNa01/02 or a suppression of that state? (l.93 'Touch also switched off the neurons she steers with'.)
STEPS: minsyn.csv and touch_dose.csv (paper's model, 5 seeds, 600 ms); touch_5s.csv; persistence_g1.csv ('pheromones + song + touch@100' on/off bins). Non-driven active neurons = active_frac x 139,248 - n_driven. Columns: 'aSP22', 'oviIN', 'PPL1 (punish DA)', 'MBON', 'KC', 'GF jump', 'DN all', 'recruited_spikes'.
CRITERION: No pre-set numeric line; the task asks to take the self-sustained state into account. This also covers design_critique headline 1 (per-DN readout, DNp09 silent). The state's markers, from analysis_A (n=8 off-phase runs): DNa 16-18, PPL1 8.7, aSP22 10.7, oviIN 9.1, GF 3.1 Hz, about 1,980 non-driven neurons.
NUMBERS: cVA@100 alone (n=5): 1,768 non-driven active neurons, aSP22 7.3, oviIN 4.3, PPL1 5.46, MBON 1.09. The state is on.

cVA + touch@100: 1,024 non-driven active neurons (touch alone: 941); aSP22, oviIN and PPL1 all 0.0; MBON 0.19. The state never starts while touch lasts. By touch rate, cVA's PPL1 is 5.46 / 4.23 / 3.90 / 0.29 / 0.0 at 0 / 10 / 25 / 50 / >=100 Hz, and the non-driven count is 1,768 / 1,869 / 1,767 / 1,225 / 1,024.

Food@100: the state's aSP22 goes 8.83 -> 2.5 (touch 10 Hz) -> 0 (>= 25 Hz), and GF 3.83 -> 0 already at 10 Hz. DNa falls only from 50 Hz. The odour's own PPL1 (17.2 -> 16.9-18.4), oviIN (16.0 -> 14.8), MBON (5.9 -> 6.0) and KC (1.24 -> 1.31) are unchanged.

Touch raises 'DN all' from 1.27 to 8.38 (100 Hz) and 12.09 Hz (200 Hz). DNp09 is 0.

Rebound (persistence_g1.csv, 2 seeds): during 10 s of pheromones + song + touch, DNa <= 1 Hz and aSP22 0. Within 50-150 ms of all input stopping, DNa 15-25, aSP22 5-10 and PPL1 7-11 Hz appear, and the state then persists. Touch holds the state's outputs down; it does not erase what the smell set up.
VERDICT REWORD
PAPER: l.93: use 'silenced the two steering neurons from which I read her walking' (previous item) rather than 'switched off the neurons she steers with'. No further main-text change.
NOTES: Note 4, add: "Touch silences DNa01/02, not descending neurons in general: the mean descending neuron rises from 1.3 to 8.4 Hz. With cVA, touch at 50 Hz or more keeps the self-sustaining firing of Note 5 from starting at all while it lasts (PPL1 5.5 -> 0 Hz; 1,020 active non-driven neurons, as for touch alone, against 1,770). With the food odour it removes that firing's giant-fibre and aSP22 component but leaves the odour's own dopamine and memory-centre drive unchanged. When all input stops, the self-sustaining firing appears within 0.15 s."

### [freeze-touch] DNp13 ovipositor reflex under partial, one-sided and weaker touch. l.93: 'When a female's head is touched she extends her ovipositor'. Note 4: head bristles -> DNp13 28 / 35 / 42 Hz. (verify_wording 24c proposed narrowing this to 'all the bristles driven at once'.)
STEPS: touch_dose.csv, columns 'DNp13 reject' (the 2-neuron group mean), 'DNp13 L' and 'DNp13 R'; rate, fraction and side blocks; 5 seeds, 600 ms.
CRITERION: S14 third bullet: DNp13 >= 10 Hz at 200 Hz for <= 25 % of the bristles and for one side.
NUMBERS: All bristles, touch alone (n=5), at 10 / 25 / 50 / 100 / 150 / 200 / 300 Hz: 5.3+-1.6 / 15.7+-1.6 / 26.5+-2.2 / 35.2+-1.2 / 39.0+-0.7 / 35.7+-1.6 / 31.5+-2.6 Hz. MDN appears at 200-300 Hz (2.2+-0.4 and 8.9+-1.1).

At 200 Hz on food (n=15):
- 3 %: 0.1+-0.2.
- 10 %: 7.7+-3.0.
- 25 %: 19.7+-3.0 (draws 16.8 / 22.8 / 19.5).
- 50 %: 31.8+-1.5.
- 100 %: 35.7+-1.6 (n=5).
- Eye bristles (1,113): 21.8+-1.6. Antennal bristles (41): 3.0+-2.1.

One side, group mean (per neuron):
- left@200: 36.7+-1.0 (DNp13 L 73.3, R 0).
- right@200: 28.0+-1.9 (R 56.0, L 0).
- left@100 / right@100: 33.7 / 26.8.
The reflex is strictly ipsilateral.

S14 outcome: PASS (25 % gives 19.7 Hz; each side >= 26.8 Hz). It fails only at 10 % and below.
VERDICT KEEP
PAPER: l.93 unchanged: 'When a female's head is touched she extends her ovipositor'. Do NOT adopt verify_wording 24c's narrowing to 'all the bristles driven at once'; a quarter of the bristles or one side suffices.
NOTES: Note 4, after 'Head bristles -> DNp13 28 / 35 / 42 Hz': "It is graded and one-sided. All bristles at 10, 25, 50 and 100 Hz give 5, 16, 27 and 35 Hz. At 200 Hz, 10, 25 and 50 % of them give 8 +- 3, 20 +- 3 and 32 +- 2 Hz (3 draws x 5 seeds). Touch on one side drives only the DNp13 on that side, at 56-73 Hz."

### [freeze-touch] Does touch gate feeding? (Not in the paper; S14's pre-set rule decides whether Note 4 gets a sentence.)
STEPS: touch_dose.csv feeding block: 'sugar GRNs@100' (129 neurons), '& touch (all head bristles)@100', '& ...@200', and 'bitter GRNs@100 & touch@200'. Columns 'MN9', 'MN9 both' and 'feed MNs'; 5 seeds, 600 ms.
CRITERION: S14: if MN9 under sugar with the bristles driven falls below 80 % of sugar alone, add one sentence to Note 4 (touch gates feeding).
NUMBERS: MN9 (n=5):
- sugar alone: 76.0 +- 4.8 Hz (70.0-81.7).
- + touch@100: 3.7 +- 2.7 (4.8 % of sugar alone).
- + touch@200: 0.0 +- 0.0 (0 %).
'MN9 both' is identical.

'feed MNs' is 24.1 +- 1.9 with sugar alone and 26.5 +- 0.4 / 32.5 +- 0.4 with touch. Touch alone drives it to 16.1 +- 0.6 / 22.3 +- 0.4, so that 52-neuron group is not a feeding-specific readout.

Bitter + touch@200 gives MN9 0, which says nothing, since bitter alone already gives 0.

The pre-set rule is triggered (4.8 % and 0 %, both < 80 %).
VERDICT REWORD
PAPER: No main-text change is required by the rule. Optionally, at l.93: 'Sugar makes it work its mouthparts, and bitter, or a touch on the head, makes it stop.'
NOTES: Note 4, add one sentence: "Touch also stops feeding: with every head bristle driven at 100 or 200 Hz, sugar drives MN9 at 3.7 +- 2.7 and 0.0 Hz instead of 76.0 +- 4.8 Hz (5 seeds, 0.6 s)."

### [freeze-touch] Closing prediction, l.123: 'touch a walking fly on the head and its steering neurons should fall quiet, so that two flies bumping heads should stop together.'
STEPS: touch_dose.csv (rate, fraction and side blocks), touch_5s.csv and minsyn.csv, as in the items above.
CRITERION: S14: if the freeze is not a general reflex (>= 0.35 for <= 25 % of the bristles and for either side alone), 'say a whole-head touch and rewrite the closing prediction.' design_critique headline 1 and verify_wording 'female walking is DNa' also apply.
NUMBERS: The model's prediction depends on how much of the head is touched:
- More than half of the bristles on both sides at 200 Hz: index 0.48 +- 0.12 (50 %), 0.76 +- 0.07 (all), 0.83 +- 0.01 over 5 s.
- All bristles need >= 50-100 Hz: 0.32 at 50 Hz, 0.69 at 100 Hz (food).
- A head bump in a real fly touches few bristles. In the model 3-25 % gives -0.13 to 0.12, and 10 % RAISES DNa (index -0.44 +- 0.25).
- The left-side bristles alone spare or raise the left DNa (-0.02 food, -0.25 cVA at 200 Hz).
- Touch raises the mean DN (1.3 -> 8.4 Hz).
- Walking drive through the decoder falls from 0.73 to 0.20, not to 0.
- 'Should stop' also assumes DNa01/02 carry walking (the female model has no nerve cord; DNp09 is silent).
VERDICT REWORD
PAPER: l.123: "It also makes a prediction that experimenters can test: touch most of a walking fly's head, on both sides, and its DNa01/02 steering neurons should fall quiet while its ovipositor neuron DNp13 fires; a touch to a few bristles should not quiet them." (Drop 'so that two flies bumping heads should stop together'. In the model a light bump does the opposite.)
NOTES: Note 4 (support for the prediction): "The steering neurons fall quiet only when more than half of the bristles are driven, or all of them at 50-100 Hz or more. A touch to a tenth of them raises the steering neurons' rate (index -0.44 +- 0.25)."

### [freeze-touch] Bitter suppression across gains and stimulus rates (S12). l.93 'bitter makes it stop'; Note 4 'with Shiu et al.'s 29 sugar neurons 55 Hz, and 3.3 Hz with bitter added'. analysis_A's checker already set CHANGE from the same file; this finishes it.
STEPS: anchors-gain: experiments/results_edge/anchors/anchors_gain.csv (540 rows = 9 anchor drives x gains 0.7/0.8/0.9/1.0/1.2/1.4 x 10 seeds, 1000 ms); drives 'Shiu sugar@100' and 'Shiu sugar@100 & Shiu bitter@{25,50,100}'; column 'MN9'. anchors-rate: anchors_rate.csv has NO bitter drive (the preset lists JON-CE, JON-F, Shiu sugar, JO-A and JO-B only). Engine check: at gain 1.0, seeds 0-2 of all 7 anchor drives equal benchmark_flywire_shiu_min1+known+eln0.25.csv (270 cells with anchors_rate, 0 difference). Script not kept.
CRITERION: S12: keep if MN9 with bitter at 100 Hz stays below 25 % of sugar alone, with a monotone dose over 25/50/100 Hz, at every gain 0.7-1.4. A failure at 0.7 qualifies the reflex as the male MDN is qualified. Report the 10-seed bitter mean +- sd. S10.5 (the 14 conditions) passed in analysis_A.
NUMBERS: Sugar alone -> +bitter@25 / @50 / @100 MN9, mean +- sd (n=10), with the pooled @100 ratio and the per-seed ratio mean +- sd:
- gain 0.7: 0.1+-0.3 -> 0 / 0.1 / 0. Not testable: these 29 neurons do not drive MN9.
- 0.8: 7.2+-3.9 -> 7.4+-4.4 / 1.6+-1.6 / 0.2+-0.4. Ratio 0.03; the dose is not monotone at 25 Hz.
- 0.9: 36.9+-4.2 -> 27.4 / 9.7 / 1.8+-1.5. Ratio 0.05 (0.05+-0.04).
- 1.0: 51.7+-4.5 -> 39.9+-5.6 / 23.1+-5.2 / 4.4+-3.7. Ratio 0.085 (0.09+-0.08); 1 of 10 seeds >= 0.25 (0.30).
- 1.2: 62.8+-8.1 -> 55.2 / 41.2 / 15.7+-3.4. Ratio 0.250 (0.25+-0.06); 5 of 10 seeds >= 0.25. FAIL (not below).
- 1.4: 66.8+-5.1 -> 55.3 / 49.0 / 25.8+-4.6. Ratio 0.386 (0.39+-0.07); 10 of 10 seeds >= 0.25. FAIL.

The dose is monotone at 0.9-1.4. Bitter alone gives MN9 0 and PPL1 0 at every gain. The stimulus rate was never varied for bitter (the anchors in sensmap are pinned @100 Hz, and anchors_rate lacks bitter).

The 10-seed gain-1 value of 4.4 +- 3.7 Hz shows that Note 10's '3.3, earlier 1.7' change is seed noise.
VERDICT CHANGE
PAPER: l.93: "Sugar makes it work its mouthparts, and bitter makes it stop, though with every synapse a third stronger bitter only slows it." (This is analysis_A's checker wording, confirmed.)
NOTES: Note 4, after '55 Hz, and 3.3 Hz with bitter added': "(4.4 +- 3.7 Hz over 10 seeds, against 51.7 +- 4.5 alone). MN9 keeps 3-13 % of its sugar-alone rate in the 12 conditions of the sensitivity table that keep the stimulus at 100 Hz, falling steadily with bitter at 25, 50 and 100 Hz. By gain (10 seeds, 1 s) it keeps 3 % at 0.8, 5 % at 0.9, 9 % at 1.0, 25 % at 1.2 and 39 % at 1.4 (66.8 +- 5.1 -> 25.8 +- 4.6 Hz). At 0.7 these 29 sugar neurons do not drive MN9 at all (0.1 Hz). I did not vary bitter's stimulus rate." Note 10: replace the 1.7/3.3 sentence with 'bitter suppression, 3.3 Hz here, 4.4 +- 3.7 Hz over 10 seeds'.

### [freeze-touch] Grooming across gains and rates (S12): 'Wind on the antenna makes it groom' (l.93); Note 4 'Wind (JO-CE) -> the grooming neuron aBN1'. analysis_A's checker set CHANGE; this finishes it with anchors-gain and anchors-rate.
STEPS: anchors_gain.csv drives 'Shiu JON-CE@100' (69 neurons) and 'Shiu JON-F@100' (60), 10 seeds, 1 s. anchors_rate.csv 'Shiu JON-CE/JON-F@{25,50,150,300}', 5 seeds, 1 s. Column 'aBN1' (single neuron, root 720575940630907434). The whole 484-neuron JO-C/E group at gains 0.7/1.4 comes from analysis_A (map_gain.csv).
CRITERION: S12 (S10.5 for the conditions): aBN1 >= 5 Hz with JON-F below a third of JON-CE, at gains 0.7-1.4 and at 50-150 Hz. A failure at 0.7 qualifies the reflex as the male MDN is qualified ('fails the gentlest version of my first test').
NUMBERS: JON-CE -> aBN1, mean +- sd (n=10), gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4: 0.5+-0.7 / 3.3+-1.6 / 7.7+-2.2 (lowest seed 5) / 13.0+-2.4 / 22.2+-2.9 / 31.7+-2.9 Hz.
JON-F: 0.2+-0.4 / 0.1+-0.3 / 0.4+-0.5 / 0.2+-0.4 / 0.0 / 0.0 (F/CE ratio 0.40 at 0.7, <= 0.05 from 0.8 up).

By rate (n=5): JON-CE 0.0 / 0.2+-0.4 / 34.2+-1.6 / 64.6+-1.1 at 25 / 50 / 150 / 300 Hz; JON-F <= 0.2 at every rate.

S12 outcome: FAIL at gains 0.7 and 0.8 and at 25-50 Hz; PASS at 0.9-1.4 and 150-300 Hz. The whole JO-C/E group still gives 9.0+-1.0 at 0.7 (n=3), so the gain failure is specific to Shiu et al.'s 69-neuron set. With the analysis_A >= 5-synapse failure (JON-CE 0.6 vs JON-F 3.9), the reflex fails parts of tests 1 and 3.

Side note: at gain 1.4 JON-CE switches on the self-sustained state in 6 of 10 seeds (DNa L 8-20 Hz, PPL1 2.4-7.0, 10-20k recruited spikes against about 2.6k).
VERDICT CHANGE
PAPER: l.93: "A strong wind on the antenna makes it groom, though not with every synapse a third weaker." (This is analysis_A's 'not when the wind is weak, and not once the weakest connections are removed', shortened, with the gain-0.7 failure added. If space allows, append: 'nor once the weakest connections are removed'.)
NOTES: Note 4: "Wind (JO-CE, Shiu et al.'s 69 neurons) -> the grooming neuron aBN1 0.5 / 3.3 / 7.7 / 13.0 / 22.2 / 31.7 Hz at gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4 (10 seeds, 1 s; +- 0.7-2.9), with JO-F at most 0.4 Hz. It is 0.2 Hz at a 50 Hz stimulus and 34 and 65 Hz at 150 and 300 Hz (5 seeds). Under the >= 5-synapse threshold JO-CE gives 0.6 Hz and JO-F 3.9 Hz. The whole JO-C/E group (484 neurons) gives 9 / 26 / 44 Hz at gain 0.7 / 1.0 / 1.4. Like the male's backing, the reflex with Shiu et al.'s input set fails the gentlest version of my first test."

### [freeze-touch] Sound (JO-A) -> giant fibre across gains and rates. l.93 'A sound fires its escape jump'; Note 4 'Sound (JO-A) -> giant fibre 6 / 11 / 16 Hz'. analysis_A set REWORD from sensmap and the maps; this finishes it with anchors-gain (10 seeds) and anchors-rate.
STEPS: anchors_gain.csv 'song/sound (JO-A)@100' and 'sound (JO-B)@100', 10 seeds, 1 s, column 'GF jump'. anchors_rate.csv JO-A/JO-B at 25/50/150/300 Hz, 5 seeds. Odour -> GF comparison from analysis_A (sensmap and map_gain), read against the self-sustained state's GF (analysis_A persistence).
CRITERION: S10.4: JO-A -> GF >= 5 Hz at a 50 Hz stimulus, at 150 Hz and at >= 5 synapses, and >= 2x the largest odour -> GF. S12 adds the 10-seed gain series and the 25-300 Hz rates (same 5 Hz line).
NUMBERS: JO-A -> GF (n=10), gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4: 5.1+-1.0 (lowest seed 3.0) / 7.8+-0.8 / 9.6+-0.8 / 11.3+-1.1 / 13.9+-0.9 / 15.9+-1.6 Hz.
JO-B: 0.3+-0.3 / 1.1+-0.6 / 2.6+-0.8 / 4.8+-1.0 / 8.7+-1.2 / 11.5+-1.0.

By rate (n=5): JO-A 0.0 / 1.6+-0.4 / 18.1+-1.0 / 27.9+-0.7 at 25 / 50 / 150 / 300 Hz; JO-B 0.0 / 0.3+-0.5 / 11.2+-0.8 / 18.6+-0.6.

S10.4 still fails at a 50 Hz stimulus (1.6 Hz, and 0 at 25 Hz). It passes at gains 0.7-1.4 on average, but 0.7 is marginal (5.1, one seed at 3.0).

2x rule at gain 1.0: 11.3 (n=10) against the largest odour, 5.0+-1.4 (Or88a, n=3), is 2.25x (1.94x at n=3, 2.09x in the paper's gain_sweep).

The odour -> GF of about 3-5 Hz is the self-sustained state's giant-fibre firing (3.1+-0.4 Hz after smell offset, n=8), not a smell-specific route. Touch abolishes it (food GF 3.8 -> 0).

In 1 of 10 seeds at gain 1.4, JO-A tips DNa to 6.0/7.5 Hz (seed 5).
VERDICT REWORD
PAPER: l.93: "A loud sound fires its escape jump." (This is analysis_A's wording, confirmed.)
NOTES: Note 4: "Sound (JO-A) -> giant fibre 5.1 / 7.8 / 9.6 / 11.3 / 13.9 / 15.9 Hz at gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4 (10 seeds, 1 s; +- 0.8-1.6), and 18 and 28 Hz at 150 and 300 Hz, but 1.6 Hz at a 50 Hz stimulus and 0 at 25 Hz (5 seeds). It is 10-18 Hz in 13 of the 14 conditions. Smells reach the giant fibre at 3-5 Hz, and this is the giant-fibre firing of the self-sustaining state that smells switch on (Note 5), about a third to a half of what sound gives."

RUN PROBLEMS [freeze-touch]: None of the five steps is broken, and none has a .check.txt mismatch, because none has a .check.txt at all. The step commands for freeze-minsyn, touch-dose, touch-5s, anchors-gain and anchors-rate (experiments/edge/steps_20260927.tsv) carry no --check-against, so I ran the engine checks myself.

Engine checks (scripts in (scratch, not kept)):
- minsyn.csv reproduces experiments/results/contact_stop_flywire.csv (5-seed means and sds of 8 readouts) for Shiu k=1, Zenodo k=1 and Zenodo k=5 (food and cVA, each with and without touch). Max |diff| is 6.7e-16. Seeds 0-2 of Shiu k=5 equal the sensitivity file's 'connections >= 5 synapses' row cell for cell. minsyn.json confirms that the in-memory k=5 threshold equals the min5 cache in both tables (2,700,429 connections, arrays identical).
- touch_dose.csv, rate block: food@100 and cVA@100, with and without touch@100, equal contact_stop's paper-model rows (max |diff| 2.2e-16). Drives that appear in two blocks are identical.
- touch_5s.csv, bin 0 of food@100 (1 s from rest), equals social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv 'food odor' seeds 0-4 exactly (120 cells).
- anchors_gain.csv at gain 1.0, and anchors_rate.csv sugar at 25/50/150 Hz, seeds 0-2, equal benchmark_flywire_shiu_min1+known+eln0.25.csv: 270 cells, 0 difference, total_spikes identical.

Run health:
- logs/edge/guarded_{freeze-minsyn,touch-dose,touch-5s,anchors-gain,anchors-rate}.out: every step reports ok on attempt 1 (05:03-05:10), with no traceback, warning or retry.
- Sidecars: 6 threads / 6 chunks; lif sha 9c6fe7be4bc2aaed; grid_probe sha 5597fa5189e27d67; FLYBRAIN_SIGNS=known, FLYBRAIN_ELN=0.25.
- No NaN or negative readouts (only 'members' is NaN, as expected), no duplicate keys, and 'none' gives 0 spikes.

Coverage gaps and caveats that affect the verdicts:
1. anchors_rate has no bitter drive, and the sensmap anchors are pinned at @100 Hz, so bitter suppression was never run at another stimulus rate.
2. The random 1,417-neuron specificity sets are 74-76 % photoreceptors (visual 1,046-1,074 per the log). The live controls (sugar -> MN9 73 Hz, JO-CE -> aBN1 22 Hz) carry the specificity result.
3. BM_Ant (41 neurons) against BM_InOm (1,113) is not size-matched, so 'antennal vs eye bristles' is confounded by count. BM_Ant behaves like a random 3 % draw (43 neurons).
4. The fraction and side blocks are 600 ms from rest, on food/cVA at 100 Hz, gain 1, female, paper's model only. The 5-s run covers only the whole-head 200 Hz touch. freeze-minsyn uses touch at 100 Hz, not the arena's 200 Hz.
5. The per-seed freeze index is undefined wherever DNa alone is 0: cVA at Shiu k=5, and the whole Zenodo table under cVA. Pooled contact_stop-style indices are used there. The Shiu cVA k=3 per-seed index is unstable (-0.13 +- 1.07); its pooled value is 0.19.
6. The 'feed MNs' group (52 neurons) is driven by touch alone (16-22 Hz), so it is not a feeding readout. Use MN9 (Shiu et al.'s) for feeding.
7. analysis_A's corrected Note 4 phrase 'weakens when only the 1- and 2-synapse connections are removed (food 0.37 and 0.31, cVA 0.19)' conflates the two tables. 0.37 (Shiu) and 0.31 (Zenodo) are both k=3. The k=2 values are 0.59 and 0.55 (cVA 0.70).

Knock-on effects for analysis_A (self-sustained state):
- At gain 1.4, wind (Shiu JON-CE@100) switches the state on in 6 of 10 seeds within 1 s (DNa L 8-20 Hz, PPL1 2.4-7.0, recruited 10-20k spikes against about 2.6k). JON-F does so in 1 of 10, and JO-A tips DNa in 1 of 10.
- pC1d fires at gain 1.4 (0.45 +- 0.50 Hz) only in those 6 state seeds (0.5-1.5 Hz), 0 in the other 4. The Note 5 exception is therefore a by-product of the state.
- 'Touch, sound and sugar leave nothing' holds at gain 1 only.
- cVA + touch never enters the state while touch lasts, which agrees with analysis_A's 0/5. With the food odour, touch removes the state's GF and aSP22 component at 10-25 Hz. When touch ends together with the smell, the state appears within 0.15 s (persistence_g1.csv, pheromones + song + touch).

>>> CHECK [freeze-touch] 1. Freeze is touch-specific (DECISIONS item 7). Verdict KEEP, with a Note 4 addition.: agrees=True
OWN: Source: minsyn.csv, rows conn=shiu,min_syn_mem=1, 5 seeds. Index = 1 - mean(DNa L+R)/mean(food@100 alone).
- Touch: 0.694 (per seed 0.689 +- 0.057); DNa 20.3/12.3 -> 6.8/3.2.
- Controls, pooled (per seed): sugar -0.026 (-0.037+-0.189); bitter -0.082 (-0.092+-0.112); JO-A -0.071 (-0.088+-0.181); JO-CE 0.092 (0.080+-0.166); random d0 -0.122 (-0.141+-0.208); d1 -0.092 (-0.108+-0.190); d2 0.128 (0.110+-0.178).
- Largest single seed 0.36 (d2). Every pooled control is below 0.35 and below half of touch (0.347), so it passes.
- Liveness: sugar gives MN9 72.7; JO-CE gives aBN1 22.0.
- JO-A is weak evidence of a live input: GF goes 3.83 -> 4.50, and food alone already gives 3.83. JO-A's own drive shows in the Zenodo k=1 rows (GF 0 -> 9.5).
- DN all: touch 1.27 -> 8.38; controls 1.28-2.30. DNp09 is 0 throughout.
- Random sets are 1,074, 1,069 and 1,046 visual neurons of 1,417 (73.8-75.8 %).

Three things the verdict misses:
(a) No control matches touch's strength downstream. recruited_spikes: food alone 35,038; +touch 56,648 (+21,610); +each control 34,768-41,974 (-270 to +6,937). The test shows these inputs do not freeze; it does not show that an input of touch's size would fail to.
(b) 'The one exception anywhere' is imprecise. At Zenodo k=5 all seven controls (0.10-0.33) beat touch (0.083). At Shiu k=5, JO-CE (0.245) and d2 (0.062) beat touch (-0.004). At k<=3 the largest control is 0.272 (Zenodo k=2, JO-CE); that part is correct.
(c) 'Silences' is wrong for the food odour: the DNa keep 31 % (6.8/3.2 Hz). They are silenced only with cVA (0/1.2).
CORRECTED: Main text: no change.

Note 4: "The freeze is specific to touch. Adding sugar, bitter, JO-A or JO-CE input, or 1,417 random non-touch sensory neurons (three-quarters of them in the eye), to the food odour instead of touch gives indices of -0.12 to 0.13 (5 seeds each), against 0.69 +- 0.06 for touch. None of these inputs recruits as much of the brain as touch does. Touch cuts DNa01/02 by two-thirds while the mean descending neuron rises from 1.3 to 8.4 Hz."

>>> CHECK [freeze-touch] 2. Which connection threshold abolishes the freeze (S13). Verdict REWORD.: agrees=False
OWN: I reproduced every number in the verdict from minsyn.csv.

Index (pooled, n=5) at k = 1/2/3/5:
- Shiu food: 0.694 / 0.588 / 0.371 / -0.004.
- Zenodo food: 0.708 / 0.554 / 0.306 / 0.083.
- Shiu cVA: 0.933 / 0.695 / 0.192 at k=1/2/3. At k=3 the per-seed values are -0.13 +- 1.07, because seed 3 goes from 5.0 to 15.0.

Touch alone, DNa R: Shiu 0.83 / 2.5 / 7.67 / 18.67; Zenodo 1.5 / 3.33 / 9.5 / 17.83.

At k=5:
- cVA + touch: DNa 0 -> 11.4 (Shiu) and 12.3 (Zenodo).
- Food + touch: 20.1 -> 20.2 (Shiu) and 19.2 -> 17.6 (Zenodo).

Engine checks:
- Shiu k=1, Zenodo k=1 and Zenodo k=5 against contact_stop_flywire.csv: max|diff| 6.7e-16.
- Shiu k=5, seeds 0-2, against the sensitivity row 'connections >= 5 synapses': 18 cells, 3.6e-15.

Context from the log: k=2 removes 7.5M of 15.1M connections but only 14 % of synapses (54.2M -> 46.7M); k=3 removes 24 % and k=5 37 %.

The flip starts before k=5. At k=3, touch alone already drives the DNa (mean 4.0 Hz Shiu, 5.3 Zenodo), and in the Zenodo table cVA + touch raises the DNa from 0.17 to 1.75 (k=2) and from 0 to 5.1 (k=3).

At Zenodo k=5 the food index is 0.08 (<= 0.1), but touch still lowers the DNa sum slightly. The S13 condition 'touch raising DNa' is met there only by cVA and by touch alone.

The keep rule fails, as the verdict says. The proposed l.93 sentence 'survives every one of my alternatives but one' is therefore too strong:
- k=3 is below 0.35 in one table (Zenodo 0.31) and for one smell (Shiu cVA 0.19);
- analysis_A's published-sign cVA is 0.31 at n=3.

The Notes line '(cVA 0.93, 0.70 and 0.19)' reads as k=2/3/5 but is k=1/2/3, the same ambiguity it sets out to fix.
CORRECTED: l.93: "The freeze weakens as the weakest connections are removed. Drop those made of fewer than five synapses, a common way of tidying a wiring diagram, and it is gone: touch on its own now excites the steering neurons. The freeze depends on the weakest connections in the brain."

Note 4: "It weakens step by step as weak connections are removed. Dropping connections of fewer than 2, 3 and 5 synapses takes the index from 0.69 to 0.59, 0.37 and 0.00 in Shiu et al.'s table, and from 0.71 to 0.55, 0.31 and 0.08 in the Zenodo table (food odour, 5 seeds). With cVA it falls from 0.93 to 0.70 at 2 synapses and 0.19 at 3. At 5, cVA no longer drives the steering neurons, and touch raises them from 0 to 11-12 Hz. Touch on its own drives the right steering neurons ever harder: 0.8, 2.5, 7.7 and 18.7 Hz."

>>> CHECK [freeze-touch] 3. Partial, one-sided or weaker touch (S14 freeze bullets). Verdict REWORD.: agrees=False
OWN: Source: touch_dose.csv, index against the rate block's food@100 (DNa 20.3/12.3) and cVA@100 (9.3/8.2).

Rate, all 1,417 bristles, per seed (n=5), food:
- 10 Hz -0.249 +- 0.151
- 25 Hz -0.103 +- 0.136
- 50 Hz 0.319 +- 0.057
- 100 Hz 0.689 +- 0.057
- 150 Hz 0.764 +- 0.048
- 200 Hz 0.764 +- 0.072
- 300 Hz 0.832 +- 0.017
cVA: 0.126 / 0.254 / 0.685 / 0.932 / 0.952 / 0.952 / 0.943.

Fraction at 200 Hz on food (n=15):
- 3 %: -0.13 +- 0.17 (SE 0.04).
- 10 %: -0.44 +- 0.25; DNa (mean L,R) 16.3 -> 23.2; draw 0 DNa R 12.3 -> 29.0.
- 25 %: 0.12 +- 0.17 (draws, pooled 0.23 / 0.13 / 0.03).
- 50 %: 0.48 +- 0.12.
- 100 %: 0.76 +- 0.07.
- BM_InOm 0.59 +- 0.07; BM_Ant 0.12 +- 0.12.

One side, per seed (pooled L / R):
- Food, left@100 0.21 (0.22/0.23); right@100 0.52 (0.53/0.53); left@200 0.16 +- 0.17 (-0.02/0.50); right@200 0.69 +- 0.09 (0.70/0.68).
- cVA, left@100 0.57 (0.27/0.92); right@100 0.64 +- 0.31 (0.62/0.65, not in the verdict); left@200 0.29 (L -0.25, 9.3 -> 11.7); right@200 0.91 (0.89/0.94).

Run checks:
- The 20 side-block rows that repeat rate-block drives are identical.
- 'touch 100% d0@200' equals all@200.
- Food/cVA +- touch@100 reproduce contact_stop (sd ddof=1, 8e-17).

Decoder (motor.py: forward = DNp09 + DNa01/02, k 10 Hz): walk 0.66 -> 0.28 at 100 Hz, and 0.73 -> 0.20 over 5 s. Correct.

Problems with the proposed wording:
- 'Silenced' is wrong for the food odour: DNa L keeps 7.0 Hz at 200 Hz (34 %).
- 'The two steering neurons' is inaccurate: the readout is DNa01 and DNa02 on each side, four neurons.
- 'A few bristles' understates the threshold: 25 % (354 bristles) still fails, and the right half alone (712) works as well as the whole head at 100 Hz.
- Note 11: senses.py l.203 drives the bristles at R_BURST = 200 Hz on 'hit' (300 ms after damage), on isCollidedHorizontally, or on fly contact (observe.js l.261, < 1.3 blocks). The verdict drops verify_wording 24c's 'or hit'.
CORRECTED: l.93: "A touch over much of her head also turned down the steering neurons from which I read her walking, which I had not expected, so a female touched over much of her head freezes. A touch to a quarter of the bristles or fewer, or to the left side alone, does not." (Or use S14's pre-set 'a whole-head touch'.)

Note 4 (verdict text is fine, with 'at 200 Hz' added to the side clause): "... the right-side bristles alone at 200 Hz give 0.69 +- 0.09, but the left-side ones give 0.16 +- 0.17 and spare the left steering neurons."

Note 11: "200 Hz for touch, applied to all 1,417 head and eye bristle neurons of both sides whenever the fly is within 1.3 blocks of another fly, bumps into a block, or is hit."

>>> CHECK [freeze-touch] 4. The freeze rises with touch rate and holds for 5 s. Verdict KEEP.: agrees=True
OWN: Source: touch_5s.csv, per seed per bin (n=5).

Index by 1-s bin: 0.784 +- 0.047, 0.823 +- 0.038, 0.833 +- 0.037, 0.830 +- 0.033, 0.856 +- 0.024. Slope +0.0152 per s.
- The index deepens from bin 0 to bin 4 in 5 of 5 seeds (+0.03 to +0.17).
- Whole 5 s: 0.826 +- 0.013 (0.815-0.849).

Food alone: DNa 23.2/15.8.
With touch:
- DNa L 7.2 -> 5.6, DNa R 0-0.7;
- DNp13 34.2-35.1, DN all 12.14-12.21, feed MNs 22.2-22.5;
- aSP22 and GF 0 in every bin;
- PPL1 17.5-18.7, as for food alone.
Walk drive: 0.73 -> 0.20.

Engine check: bin 0 of food@100 equals social_probe 'food odor' seeds 0-4 (135 cells, 0 difference).

The rate trend is monotone from 10 to 150 Hz, then flat (0.76-0.83).

One caveat for l.101 (and the current l.247): 'switched off their steering' is too strong. DNa L keeps firing at 5.6-7.2 Hz and the decoder still gives a walk drive of 0.20.
CORRECTED: Note 4 addition as proposed: "With every bristle at 200 Hz the freeze holds, and slightly deepens, over 5 s: 0.78 +- 0.05 in the first second and 0.86 +- 0.02 in the fifth (5 seeds)."

Optional, l.101: 'because touch turned down their steering' in place of 'switched off'.

>>> CHECK [freeze-touch] 5. What the freeze removes, given the self-sustained state. Verdict REWORD.: agrees=True
OWN: Non-driven active neurons = active_frac x 139,248 - n_driven.

cVA@100 alone: 1,768 non-driven active; aSP22 7.33, oviIN 4.33, PPL1 5.46, MBON 1.09, GF 0.

cVA + touch at 10 / 25 / 50 / 100 / 150 / 200 / 300 Hz:
- PPL1 4.23 / 3.90 / 0.29 / 0 / 0 / 0 / 0;
- non-driven active 1,869 / 1,767 / 1,225 / 1,024 / 1,139 / 1,258 / 1,465;
- for comparison, touch alone gives 941 at 100 Hz.

Food alone: aSP22 8.83, GF 3.83. With touch:
- aSP22 2.5 at 10 Hz and 0 from 25 Hz;
- GF 0 from 10 Hz;
- PPL1 16.9-18.4, oviIN 14.8-18.0, MBON 6.0-6.4, KC 1.30-1.34, all unchanged;
- DN all 1.27 -> 8.38 (100 Hz) and 12.09 (200 Hz); DNp09 0.

persistence_g1, pheromones + song + touch, 2 seeds:
- During 10 s: DNa <= 1.5 Hz in 1-s bins (not <= 1); aSP22 0; PPL1 0.3-2.0 Hz, not 0.
- After offset: seed 0 has DNa R 40, aSP22 10 and PPL1 10 in the 50-100 ms bin. In seed 1, aSP22 first appears in the 150-200 ms bin. So 'within 0.2 s', not 0.15 s.

Corrections to the Note:
- 'Silences' should be 'quiets' (food: DNa keep 31 %).
- The numbers given for '50 Hz or more' are the 100 Hz ones. At 50 Hz: PPL1 0.3, 1,225 non-driven active.
- 'Does not erase what the smell set up' cannot be told apart from the state igniting afresh at offset. State only what was seen.
CORRECTED: l.93: as proposed ('turned down' rather than 'silenced'; see item 3).

Note 4: "Touch quiets DNa01/02, not descending neurons in general: the mean descending neuron rises from 1.3 to 8.4 Hz. With cVA, touch at 100 Hz keeps the self-sustaining firing of Note 5 from starting while it lasts (PPL1 5.5 -> 0 Hz; 1,020 active non-driven neurons, about as many as touch alone recruits, against 1,770), and nearly so at 50 Hz (PPL1 0.3). With the food odour it removes that firing's giant-fibre and aSP22 component but leaves the odour's own dopamine and memory-centre drive unchanged. When smell and touch stop together, the self-sustaining firing appears within 0.2 s."

>>> CHECK [freeze-touch] 6. DNp13 ovipositor reflex under partial, one-sided and weaker touch. Verdict KEEP; do not narrow l.93.: agrees=True
OWN: Touch alone, all bristles, 'DNp13 reject' (n=5), at 10 / 25 / 50 / 100 / 150 / 200 / 300 Hz: 5.3+-1.6 / 15.7+-1.6 / 26.5+-2.2 / 35.2+-1.2 / 39.0+-0.7 / 35.7+-1.6 / 31.5+-2.6. MDN 2.2+-0.3 at 200 Hz and 8.9+-1.1 at 300 Hz.

At 200 Hz on food (n=15):
- 3 %: 0.1 +- 0.2.
- 10 %: 7.7 +- 3.0.
- 25 %: 19.7 +- 3.0 (draws 16.8 / 22.8 / 19.5).
- 50 %: 31.8 +- 1.5.
- 100 %: 35.7 +- 1.6.
- Eye bristles 21.8 +- 1.6; antennal bristles 3.0 +- 2.1.

One side (group mean; per neuron):
- Food: left@200 36.7 (L 73.3 / R 0); right@200 28.0 (R 56.0); left@100 33.7 (L 67.3); right@100 26.8 (R 53.7).
- cVA: 33.3 to 37.8 (the driven side's neuron 56-76).
- The reflex is strictly ipsilateral.

The verdict's PASS holds under the '25 %' reading of 'for <= 25 %', the same reading it used for the freeze. Under a strict reading (every fraction up to 25 %) it fails at 3 % and 10 %.

The proposed Note leaves out that 3 % gives nothing. Its '56-73 Hz' is the 200 Hz range; across the side rows the range is 54-76.
CORRECTED: l.93 unchanged; I agree with rejecting 24c's narrowing.

Note 4: "It is graded and one-sided. All bristles at 10, 25, 50 and 100 Hz give 5, 16, 27 and 35 Hz. At 200 Hz, 3, 10, 25 and 50 % of them give 0, 8 +- 3, 20 +- 3 and 32 +- 2 Hz (3 draws x 5 seeds). Touch on one side drives only the DNp13 on that side, at 54-76 Hz."

>>> CHECK [freeze-touch] 7. Does touch gate feeding? (S14 rule: MN9 below 80 % of sugar alone.) Verdict REWORD, with a Note sentence and an optional main-text change.: agrees=False
OWN: MN9 (n=5):
- sugar GRNs@100: 76.0 +- 4.8 (70.0-81.7);
- + touch@100: 3.7 +- 2.7 (4.8 %);
- + touch@200: 0.0.
'MN9 both' is identical, and the rule is triggered.

'feed MNs': 24.1 +- 1.9 -> 26.5 +- 0.4 / 32.5 +- 0.4; touch alone 16.1 +- 0.6 / 22.3 +- 0.4. Bitter + touch@200 gives MN9 0, which is uninformative.

The verdict misses that 'feed MNs' is the arena decoder's own feeding readout. motor.py l.70 builds its 'feed' group from the proboscis, ingestion and pm motor neurons plus MN9, the same group as common.py l.77. In the arena, touch therefore raises decoded feeding events: per_per_hz 0.05 x 16-22 Hz gives about 0.8-1.1 events/s from touch alone.

'Touch also stops feeding', and the optional main-text 'bitter, or a touch on the head, makes it stop', both overclaim: touch stops MN9 but works the other mouthpart motor neurons harder.

Specificity is also untested: no sugar + non-touch control was run. Only food + sugar exists (minsyn: MN9 72.7).
CORRECTED: Main text: no change. Reject the optional l.93 wording.

Note 4: "Touch also shuts off MN9: with every head bristle driven at 100 or 200 Hz, sugar drives it at 3.7 +- 2.7 and 0.0 Hz instead of 76.0 +- 4.8 Hz (5 seeds, 0.6 s), while the other proboscis motor neurons fire more (24 -> 27 and 33 Hz; touch alone 16-22 Hz)."

>>> CHECK [freeze-touch] 8. Closing prediction l.123 ('touch a walking fly on the head ... two flies bumping heads should stop together'). Verdict REWORD.: agrees=True
OWN: Food index:
- all bristles: 0.32 at 50 Hz, 0.69 at 100 Hz, 0.76 at 200 Hz;
- 50 % at 200 Hz: 0.48 +- 0.12;
- 3-25 %: -0.13 to 0.12;
- 10 %: -0.44 +- 0.25 (the DNa speed up);
- left alone at 200 Hz: left DNa -0.02 (food) and -0.25 (cVA);
- right alone at 200 Hz: 0.69.

Other numbers: DN all 1.3 -> 8.4; walk 0.73 -> 0.20 over 5 s; DNp13 fires 20-37 Hz whenever 25 % or more are touched. The female model has no nerve cord.

Dropping 'bumping heads should stop together' is right: in the model a light, partial touch does not quiet the DNa and can speed them up.

'On both sides' is stricter than the model needs (the right half alone works), but it is a safe prediction.

Corrections to the Note: 'more than half' should be 'half or more' (50 % gives 0.48). 'At 50-100 Hz or more' should be '100 Hz or more' (50 Hz gives 0.32 < 0.35). 'Fall quiet' at 0.48 means the DNa roughly halve.
CORRECTED: l.123 as proposed: "... touch most of a walking fly's head, on both sides, and its DNa01/02 steering neurons should fall quiet while its ovipositor neuron DNp13 fires; a touch to a few bristles should not quiet them."

Note 4: "The steering neurons are cut by half or more only when half or more of the bristles are driven at 200 Hz, or all of them at 100 Hz or more (0.32 at 50 Hz). A touch to a tenth of them raises the steering neurons' rate (index -0.44 +- 0.25)."

>>> CHECK [freeze-touch] 9. Bitter suppression across gains (S12). Verdict CHANGE.: agrees=False
OWN: Source: anchors_gain.csv, MN9 (n=10, 1 s). Sugar alone -> +bitter at 25 / 50 / 100 Hz; ratio at 100 Hz, pooled (per seed):
- 0.7: 0.1+-0.3 -> 0 / 0.1 / 0. Untestable.
- 0.8: 7.2+-3.9 -> 7.4 / 1.6 / 0.2. Ratio 0.028; the 25 Hz step is not monotone.
- 0.9: 36.9+-4.2 -> 27.4 / 9.7 / 1.8+-1.5. Ratio 0.049.
- 1.0: 51.7+-4.5 -> 39.9 / 23.1 / 4.4+-3.7. Ratio 0.085 (0.09+-0.08); 1 seed >= 0.25 (0.30).
- 1.2: 62.8+-8.1 -> 55.2 / 41.2 / 15.7+-3.4. Ratio exactly 0.250 (0.25+-0.06); 5 of 10 seeds >= 0.25. FAIL.
- 1.4: 66.8+-5.1 -> 55.3 / 49.0 / 25.8+-4.6. Ratio 0.386 (0.39+-0.07); 10 of 10 seeds. FAIL.

Bitter alone: MN9 0 and PPL1 0 at every gain. Gain 1.0 seeds 0-2 give 3.33, exactly the paper's 3.3.

Engine checks:
- Gain 1.0, seeds 0-2 of the 7 anchor drives against benchmark_flywire_shiu_min1+known+eln0.25.csv: 147 cells, 0 difference.
- anchors_rate sugar at 25/50/150 Hz against the benchmark: identical.

CHANGE is right, but two phrases are wrong:
(a) 'A third stronger' does not match any tested gain: 1.4 is 40 % stronger, and the failure starts at 1.2, a fifth stronger.
(b) The Note's 'I did not vary bitter's stimulus rate' contradicts its own '25, 50 and 100 Hz' dose. What was never varied is the sugar rate (always 100 Hz); bitter never went above 100 Hz.
CORRECTED: l.93: "Sugar makes it work its mouthparts, and bitter makes it stop, though with every synapse a fifth stronger or more, bitter only slows it."

Note 4: as proposed, but replace the last sentence with: "Sugar was always given at 100 Hz, and bitter at no more than 100 Hz."

Note 10: as proposed ('3.3 Hz here, 4.4 +- 3.7 Hz over 10 seeds').

>>> CHECK [freeze-touch] 10. Grooming (JO-CE -> aBN1) across gains and rates (S12). Verdict CHANGE.: agrees=False
OWN: Source: anchors_gain.csv, aBN1 (n=10), at gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4:
- JON-CE: 0.5+-0.7 / 3.3+-1.6 / 7.7+-2.2 (lowest seed 5) / 13.0+-2.4 / 22.2+-2.9 / 31.7+-2.9.
- JON-F: 0.2 / 0.1 / 0.4 / 0.2 / 0 / 0.

anchors_rate (n=5), JON-CE at 25 / 50 / 150 / 300 Hz: 0.0 / 0.2+-0.4 / 34.2+-1.6 / 64.6+-1.1. JON-F <= 0.2 at every rate.

At gain 1.4, JON-CE sets off the state in 6 of 10 seeds (seeds 0, 3, 4, 7, 8, 9): DNa L 8-20, PPL1 2.4-7.0, recruited 10-20k against a median of 2.6k.

CHANGE is right. But 'not with every synapse a third weaker' understates the failure: at 0.8 (a fifth weaker) aBN1 is 3.3 +- 1.6 Hz, below the 5 Hz line. The >= 5-synapse failure (JON-CE 0.6 against JON-F 3.9) is a real failure of test 3, so that clause should not be optional.

The current draft's l.204 says these reflexes 'fail one each'. Grooming fails at least three conditions: gain <= 0.8, stimulus <= 50 Hz, and >= 5 synapses.
CORRECTED: l.93: "A strong wind on the antenna makes it groom, though not with every synapse a fifth weaker, nor once the weakest connections are removed."

Note 4: as proposed. The numbers are correct.

>>> CHECK [freeze-touch] 11. Sound (JO-A) -> giant fibre across gains and rates. Verdict REWORD ('A loud sound fires its escape jump').: agrees=True
OWN: Source: anchors_gain.csv, GF (n=10), at gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4:
- JO-A: 5.1+-1.0 (lowest seed 3.0) / 7.8+-0.8 / 9.6+-0.8 / 11.25+-1.1 / 13.85+-0.9 / 15.9+-1.6.
- JO-B: 0.2 / 1.1 / 2.5 / 4.8 / 8.7 / 11.4.

anchors_rate (n=5), at 25 / 50 / 150 / 300 Hz:
- JO-A: 0 / 1.6+-0.4 / 18.1+-1.0 / 27.9+-0.7.
- JO-B: 0 / 0.3 / 11.2 / 18.6.
S10.4 fails at a 50 Hz stimulus.

The 2x rule is borderline, not 2.25x. The verdict compares a 1-s, 10-seed JO-A mean with a 600-ms, 3-seed odour mean. Matched windows give:
- social_probe (1 s, n=5): JO-A 11.1 +- 0.7 against Or88a 5.5 +- 1.4, a ratio of 2.0x;
- sensmap (600 ms): 1.94x.

'Smells reach the GF at 3-5 Hz, and this is the state's GF firing' is contradicted inside the same 1-s file:
- cVA drives the state (DNa 10.1/8.4, PPL1 5.9, aSP22 8.9) with GF 0.0;
- Or83c and CO2 give GF 0 and 0.4;
- Or88a gives 5.5, above the state's 3.1 +- 0.4.
The odour -> GF range is 0-5.5 Hz and depends on the odour.

JO-A at gain 1.4 tips the DNa in seed 5 (6.0/7.5) and in seed 6 (DNa L 3.0).
CORRECTED: l.93: "A loud sound fires its escape jump." (agree)

Note 4: "Sound (JO-A) -> giant fibre 5.1 / 7.8 / 9.6 / 11.3 / 13.9 / 15.9 Hz at gain 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.4 (10 seeds, 1 s; +- 0.8-1.6), and 18 and 28 Hz at 150 and 300 Hz, but 1.6 Hz at a 50 Hz stimulus and 0 at 25 Hz (5 seeds). It is 10-18 Hz in 13 of the 14 conditions. Smells reach the giant fibre at 0-5.5 Hz, depending on the smell, about the level of the self-sustaining state of Note 5 (3 Hz), so sound leads the strongest smell by only about 2x."

>>> CHECK [freeze-touch] Run health and engine checks for freeze-minsyn, touch-dose, touch-5s and anchors (the task asks for .check.txt mismatches to be flagged).: agrees=True
OWN: None of these four steps has a .check.txt: none was run with --check-against, so the S13 edge_report check was never written. I substituted independent checks, all of which pass:
- minsyn Shiu k=1, Zenodo k=1 and Zenodo k=5 against contact_stop_flywire.csv (8 readouts, mean and sd): max 6.7e-16.
- Shiu k=5, seeds 0-2, against the sensitivity row: 18 cells, 3.6e-15.
- The in-memory k=5 threshold matches the min5 cache (2,700,429 connections, arrays identical, per the sidecar).
- touch_dose against contact_stop: 8e-17 with sd ddof=1.
- touch_5s bin 0 against social_probe 'food odor': 135 cells, 0.
- anchors at gain 1 against the benchmark: 147 cells, 0.

Other health checks:
- No NaN; 'none' drives give 0 spikes.
- The side-block duplicates are identical; '100 % d0' equals all@200.
- Logs end with 'wrote ...' and contain no tracebacks.
- Sign flips: 11,010 in the Shiu table and 7,832 in Zenodo at k=1. eLN counts are 150 and 131.

No sign that any run is broken.
CORRECTED: Optional: note in Note 10 that these four edge steps were checked against the paper's files by recomputation, not by --check-against.

>>> CHECK [freeze-touch] Line references and the current paper/flycraft.tex.: agrees=False
OWN: The verdicts cite draft-5 line numbers (l.93, 101, 121, 123). Those lines are in paper/archive/flycraft_draft5_20260926.tex. paper/flycraft.tex was rewritten on 27 Sep at 06:31, and several of its new sentences already conflict with these data:
- l.206: 'holds at every strength of synapse and every stimulus rate'. At gain 0.7 the freeze cannot be tested (food DNa 0.3 Hz), and touch at 10-25 Hz does not freeze (-0.25 / -0.10).
- l.206: 'starts to weaken when only the one- and two-synapse connections go'. It already weakens when only the one-synapse connections go (k=2: -0.10 food Shiu, -0.15 Zenodo, -0.24 cVA).
- l.204: 'three more pass most tests and fail one each'. Grooming fails gain <= 0.8, stimulus <= 50 Hz and >= 5 synapses.
- l.247: 'touch switched off the neurons I read their walking from'. DNa L keeps 5.6-7.2 Hz and the walk drive is 0.20.
- l.333: the prediction still says 'two flies bumping heads should stop together', which a partial touch contradicts (the 10 % index is -0.44).
CORRECTED: Apply items 2, 3, 8 and 10 to the current tex:
- l.206: 'it weakens as soon as the one-synapse connections are removed';
- l.247: 'turned down';
- l.333: take item 8's wording;
- l.204: replace 'fail one each' with 'fail at least one each'.

### [rewiring] l.93 'Scramble the wiring and every one of these reflexes disappears', with the test as l.89 defines it: 'vanish when the brain is rewired at random with every neuron keeping its number of connections'. Tested on the paper's model (female).
STEPS: Read experiments/results_edge/shuffle-plus/rewired_flywire_paper.csv: 504 rows = 4 conditions (intact; rewire=block shuffle 0 and 1; rewire=global shuffle 0) x 42 drives x 3 seeds, 800 ms window, shiu_min1+known+eln0.25. Also read the .check.txt, the .json and logs/edge/guarded_shuffle-plus-female.out. For each reflex I computed the per-brain 3-seed mean, sd and max1 of the target column, and specificity = target minus 'DN all'. Freeze index = 1 - DNa(L+R)(smell+touch) / DNa(L+R)(smell). Scratch scripts not kept., a8.py.
CRITERION: S15 (design_plan l.204-209; DECISIONS 6 adds the global condition). A reflex disappears if every rewired brain gives <= 2 Hz (3-seed mean) or its specificity over DN-all drops by >= 80 %. A reflex keeping >= 50 % gets a clause. Note 2 must report both nulls.
NUMBERS: Values are intact / block0 / block1 / global0, each a 3-seed mean +- sd.

Gone:
- Sugar GRNs (129) -> 'MN9': 75.8+-7.3 / 0 / 0 / 0.
- Shiu sugar (29) -> MN9: 53.3+-5.1 / 0 / 0 / 0.
- JO-B -> 'GF jump': 4.79+-0.36 / 0.62+-0.62 / 0 / 0.
- JON-CE (69) -> 'aBN1': 12.5+-3.3 / 0 / 0 / 0.
- Whole JO-C/E group (484) -> aBN1: 26.7+-0.7 / 0 / 0 / 0 (max1 0 in every rewired run).
- Food -> DNa L/R: 22.9/13.1 intact, at most 1.46/1.04 rewired.
- cVA -> DNa: 10.2/7.3 intact, 0 in every rewired brain.

Bitter suppression: nothing is left to suppress. Sugar+bitter@100 gives MN9 3.3+-3.8 against 53.3 intact, and 0 against 0 in every rewired brain.

Survives: JO-A -> GF 10.62+-0.62 / 5.21+-0.95 / 7.50+-0.00 / 0. DN all is 0.12 / 0.08 / 0.10. Block brains keep 49 % and 70 % of the intact specificity (pooled 60 %, single runs 41-70 %). Both block brains are > 2 Hz, so it did not disappear.

Touch -> 'DNp13 reject': 35.4+-1.3 / 3.75+-1.25 / 12.50+-0.62 / 0. DN all is 8.06 / 14.83 / 13.54 / 0.14. Specificity is +27.4 / -11.1 / -1.0, a drop of 140 % and 104 %, so it disappears by the specificity rule. Block1 is still > 2 Hz: DNp13 R 25 Hz, L 0.

Freeze, DNa L+R without -> with touch:
- Food: 36.0 -> 10.2 intact (index 0.72); 2.5 -> 131.0 in block0; 0 -> 101.0 in block1; 0 -> 0 in global0.
- cVA: 17.5 -> 1.0 intact (0.94); 0 -> 125.2; 0 -> 78.8; 0 -> 0.
- So the freeze reverses under the block null and cannot be tested under the global null.

The male was not in this run (global-shuffle-male-plus is pending).
VERDICT REWORD
PAPER: l.89: '...vanish when the brain is rewired at random, any neuron to any other, with every neuron keeping its number of connections, ...'

l.93, replacing the last sentence: 'Scramble the wiring, any neuron to any other, and every one of these reflexes disappears. Scrambling it only within each broad class of cell is harder to pass. In the female, a sound still fires the escape neuron at about 60 % of its normal rate, and touch, instead of freezing her, sets off escape, backing and walking all at once; the other reflexes still vanish.'
NOTES: Class-preserving rewiring of my model (2 brains, 94.35 % and 94.34 % of connections moved, 3 seeds each, 800 ms):
- Sugar -> MN9 is 0.0 in both brains (intact 75.8 +- 7.3 Hz), so bitter has nothing to suppress.
- JON-CE -> aBN1 is 0.0 (12.5 +- 3.3).
- JO-B -> GF is 0.6 +- 0.6 and 0.0 (4.8 +- 0.4).
- Smells drive DNa at most 1.5 Hz (food 22.9/13.1 intact).
- JO-A -> GF is 5.2 +- 1.0 and 7.5 +- 0.0 Hz (10.6 +- 0.6), with all descending neurons at 0.1 Hz: 49 % and 70 % of its intact specificity.
- Touch -> DNp13 falls to 3.8 +- 1.3 and 12.5 +- 0.6 Hz (35.4 +- 1.3), below the 14.8 and 13.5 Hz mean of all descending neurons.
- Food + touch drives DNa L+R at 131 and 101 Hz, against 2.5 and 0 for food alone, so the freeze reverses.

Unconstrained rewiring (brain 0 of the three): every one of these is 0.0.

### [rewiring] Note 2 (l.139): 'degree-preserving rewiring ..., which moves 99.8 % of connections and leaves every readout at 0--2 Hz (largest stray value 7 Hz)'. Note 4 (l.143): 'Every readout 0--2 Hz in a rewired brain.'
STEPS: Took the maximum of every group-mean readout (38 columns 'DNa L'..'MN9 both', excluding the driven SAG/IPC columns) over every drive and brain, plus single-run and max1 maxima. Recomputed the paper's 3-brain global file experiments/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv for comparison. Scratch scripts: a4.py, a5.py, a7.py.
CRITERION: S15: Note 2 reports both nulls. The literal claim is that every readout is 0-2 Hz in a rewired brain.
NUMBERS: global0 (frac_moved 0.99857, all 42 inputs, 1,596 brain x drive x readout cells):
- Every readout averages 0.0-0.54 Hz, except PPL1 at 2.11-3.33 Hz under the 9 touch-containing inputs. Touch alone gives 2.21+-0.05 and food+touch 3.33+-0.30; the largest single run is 3.67.
- One PPL1 neuron reaches 30-39 Hz ('PPL1 (punish DA) max1').
- 'DN all' is at most 0.18 Hz.

The paper's 3 global brains (8 inputs): pooled maximum 2.12 (food -> MDN), per-brain maximum 6.35, single run 7.19. Touch -> PPL1 per brain is 2.21 / 0.94 / 2.24.

Block brains: 194 (block0) and 135 (block1) of 1,596 cells are > 2 Hz. The maximum is 98.75 Hz (GF, food+touch, block0). Touch alone gives, block0 / block1 (n=3):
- GF 91.7+-1.0 / 55.8+-1.9
- MDN 39.7+-0.3 / 21.5+-1.0
- DNa L 62.5 / 52.5, DNa R 66.5 / 28.8
- feed MNs 23.7 / 19.7 (16.1 intact)
- PPL1 12.6 / 12.9
- aSP22 2.9 / 33.8
- DN all 14.8 / 13.5 (8.06 intact)
Strays from inputs without touch:
- JO-CE -> DNa R 5.0 (block0)
- antennal bristles -> DNa L 5.6 (block1)
- bitter GRNs -> PPL1 2.9 (block0; one neuron at 45-50 Hz)
- bitter GRNs -> oviIN 15.4 (block1)
- eye bristles -> GF 43.5 (block0)
VERDICT REWORD
PAPER: Note 2, replacing 'degree-preserving rewiring \citep{maslov2002specificity}, which moves 99.8\,\% of connections and leaves every readout at 0--2\,Hz (largest stray value 7\,Hz)':

'degree-preserving rewiring \citep{maslov2002specificity}, in two forms. With any target allowed (99.8\,\% of connections move), no sense reaches the descending neurons (together at most 0.2\,Hz, even under touch), and every readout averages 0--2\,Hz, except the punishment dopamine neurons at 2--3\,Hz whenever the head is touched (largest single value 7\,Hz). With targets kept within each broad cell class (94\,\% move; female, 2 brains), sugar, wind, JO-B and smells no longer reach their targets (at most 1.5\,Hz), so bitter has nothing to suppress, and the virgin neurons wake nobody. JO-A still drives the giant fibre at 5.2 and 7.5\,Hz (10.6 intact) and nothing else. Head touch drives the giant fibre at 56--92\,Hz, MDN 21--40, DNa 29--66 and the feeding motor neurons 20--24, while DNp13 falls to 3.8 and 12.5\,Hz (35 intact), below the 14\,Hz average of all descending neurons.'

Note 4, replacing 'Every readout 0--2\,Hz in a rewired brain.': 'Rewired at random, every readout is 0--2\,Hz (the punishment dopamine neurons 2--3\,Hz under touch); rewired within cell classes, only JO-A $\rightarrow$ giant fibre survives (Note 2).'
NOTES: Unconstrained rewiring (brain 0 of three, 99.86 % of connections moved, all 42 inputs, 3 seeds):
- Every readout averages 0.0-0.5 Hz, except PPL1 at 2.1-3.3 Hz under the 9 inputs that include touch (touch alone 2.21 +- 0.05; food + touch 3.33 +- 0.30). One PPL1 neuron reaches 39 Hz.
- All descending neurons together stay at or below 0.18 Hz.

Over the paper's three brains and 8 inputs: pooled maximum 2.1 Hz, per-brain maximum 6.4, single run 7.2 (food -> MDN).

Class-preserving rewiring (2 brains): touch gives, brain 0 / brain 1 (intact in brackets):
- GF 91.7 +- 1.0 / 55.8 +- 1.9 (0)
- MDN 39.7 +- 0.3 / 21.5 +- 1.0 (0.1)
- DNa L 62.5 / 52.5 and R 66.5 / 28.8 (0.4 / 0.6)
- feed MNs 23.7 / 19.7 (16.1)
- PPL1 12.6 / 12.9 (0)
- all DNs 14.8 / 13.5 (8.1)

Strays up to 15 Hz from inputs without touch: bitter -> oviIN 15.4, eye bristles -> GF 43.5 (brain 0).

### [rewiring] Which reflexes survive the class-preserving (block) null on the paper's model: does JO-A -> GF survive, and what is the touch burst?
STEPS: Same file. Per-brain means and specificity as in a2.py/a8.py. As an extra check I compared the block rows with the published-lobe block file experiments/results/shuffle_flywire_shiu_min1_block.csv, which uses the same default_rng(100/101).
CRITERION: S15: a reflex that keeps >= 50 % of its specificity (JO-A was expected to) gets a clause. A reflex disappears if both block brains are <= 2 Hz or its specificity drops >= 80 %.
NUMBERS: JO-A -> GF, block0 / block1 (n=3):
- 5.21+-0.95 / 7.50+-0.00 Hz against 10.62+-0.62 intact; single neuron (max1) 8.75-12.5 / 15.0.
- DN all is 0.08 / 0.10, and every other readout is 0.
- Specificity retained: 48.8 % / 70.4 %, pooled 59.6 %. This passes the S15 survival rule, so the clause is required.
- These values are bit-identical to the published-lobe block file (5.21 / 7.50). The rewired topology is the same, and JO-A does not pass through sign-flipped or eLN neurons.

Touch is not a surviving reflex. It becomes a non-specific burst: GF 73.8+-19.7, MDN 30.6+-10.0, DNa L 57.5+-5.8, DNa R 47.6+-20.8, feed MNs 21.7+-2.2, PPL1 12.8+-0.3, DN all 14.2+-0.7 (n=6 runs pooled over both brains). DNp13 is 8.1+-4.9 against 35.4 intact.

The freeze reverses: touch raises DNa L+R to 79-131 Hz.

Eye bristles -> DNp13 in block0 is 11.46+-0.36 against DN all 4.69 (52 % of intact specificity), but 0 in block1. This drive is not a paper claim.
VERDICT CHANGE
PAPER: True statement: under the class-preserving null the female's sound reflex (JO-A -> giant fibre) survives at about 60 % and stays specific. Every other female reflex vanishes. Touch -> DNp13 loses its specificity inside a burst of all descending groups, and the freeze reverses. Use the l.93 and Note 2 wording given in the two entries above.
NOTES: Class-preserving rewiring: JO-A -> giant fibre 5.2 +- 1.0 and 7.5 +- 0.0 Hz (10.6 +- 0.6 intact; n = 3 per brain), with every other readout at 0 and all descending neurons at 0.1 Hz; 60 % of its intact specificity.

Head touch (6 runs over 2 brains) instead drives:
- giant fibre 74 +- 20 Hz
- MDN 31 +- 10
- DNa 58 +- 6 / 48 +- 21
- all descending neurons 14.2 +- 0.7 (8.1 intact)
- DNp13 only 8 +- 5 Hz (35.4 intact)

### [rewiring] Are aBN1 grooming and bitter suppression abolished in rewired brains? verify_wording 10b/11a: they were never read under rewiring, so 'every one of these reflexes disappears' was unsupported for them.
STEPS: Drives used: 'Shiu JON-CE@100', 'Shiu JON-F@100', 'wind/gravity (JO-CE)', 'Shiu sugar@100', and 'Shiu sugar@100 & Shiu bitter@{25,50,100}' (anchors preset). Columns 'aBN1', 'aBN1 max1', 'MN9', 'MN9 max1'. Brains: block0, block1, global0.
CRITERION: S15: the reflex disappears if every rewired brain gives <= 2 Hz or its specificity drops >= 80 %.
NUMBERS: Grooming:
- JON-CE (69) -> aBN1: intact 12.50+-3.31 (10.0 / 11.25 / 16.25). It is 0.00 in all 9 rewired runs, max1 0.
- Whole JO-C/E group (484) -> aBN1: intact 26.67+-0.72, rewired 0.00 (DN all 0.89 / 0.98 / 0.01).
- JON-F -> aBN1: 0 everywhere.

Bitter suppression:
- Shiu sugar -> MN9: intact 53.33+-5.05.
- With bitter at 25 / 50 / 100 Hz: 37.9+-8.3 / 22.9+-9.0 / 3.3+-3.8.
- Every rewired run gives MN9 0.00 for sugar alone and for all three sugar+bitter drives, so there is no sugar response left to suppress.
- Sugar GRNs -> feed MNs: 0.00 / 0.59 / 0.02.
VERDICT KEEP
PAPER: No change is needed for these two. Grooming and bitter suppression now vanish under both nulls, so do not add verify_wording 10b's caveat '(I did not measure grooming or bitter suppression in a rewired brain)'. Test 2 is closed for them. Their test-3 problems stay as analysis_A states: grooming fails at >= 5 synapses and at 50 Hz, and bitter was not varied in rate.
NOTES: In all three rewired brains, JON-CE -> aBN1 is 0.0 Hz (intact 12.5 +- 3.3; whole JO-C/E group 26.7 +- 0.7), and sugar -> MN9 is 0.0 with or without bitter (intact 53.3 +- 5.1 -> 3.3 +- 3.8 with bitter at 100 Hz); n = 3 per brain.

### [rewiring] The virgin (SAG) state wakes pC1a-c and vpoDN (Note 6, l.97). It must not do so in rewired brains, or the state result would be trivial.
STEPS: Drives 'virgin (SAG tonic)@30' and 'virgin (SAG tonic)@30 & touch (all head bristles)@100', against touch alone and the NPF/IPC states. Columns pC1a, pC1b, pC1c, vpoEN, 'vpoDN (DNp37)', 'vpoEN/DN accept', pC1d, pC1e, their max1 columns, SAG, and recruited counts (active_frac x 139,248 - n_driven). Scratch script: a3.py.
CRITERION: S15: SAG must drive pC1a-c and vpoEN/DN at <= 1 Hz in the block brains. Also checked in the global brain.
NUMBERS: SAG itself fires at 33.1 Hz in every condition, so the drive is delivered.

Intact, same file (800 ms, n=3):
- pC1a 26.04+-2.01, pC1b 22.50+-3.31, pC1c 22.92+-2.19, vpoDN 20.83+-2.37, vpoEN 0, pooled vpoEN/DN 6.94+-0.79.
- These match the state_probe seeds 0-2 at 1000 ms (pC1a 26.5 / 23.0 / 26.0).
- 45 other neurons are active (39-54).

block0, block1 and global0: every decider mean and max1 is 0.00 in all 9 runs. Only 6.7-9.3 other neurons are active. PASS.

SAG x touch:
- Intact: pC1d 14.17+-0.95 against 0 for touch alone.
- block0: 6.67+-0.95 against 6.04+-0.36 for touch alone. pC1b/c is 3.33 vs 4.17 and vpoDN 3.12 vs 2.92, so SAG adds nothing.
- block1 and global0: 0 vs 0.

NPF and IPC give 0 on every decider in every brain.
VERDICT KEEP
PAPER: Unchanged. An optional clause for Note 6 after 'all from 0': 'and 0.0 in every rewired brain (three brains, both nulls)'.
NOTES: Virgin state in rewired brains: SAG fires at 33 Hz but pC1a-e, vpoEN and vpoDN stay at 0.0 Hz in every run, single neurons included, in 2 class-preserving brains and 1 unconstrained one (n = 3 each). In the intact brain, in the same runs, pC1a is 26.0 +- 2.0, pC1b/c 22.7 +- 2.7 and vpoDN 20.8 +- 2.4 Hz. With touch, SAG adds nothing in a rewired brain (pC1d 6.7 +- 1.0 against 6.0 +- 0.4 for touch alone), against 14.2 +- 1.0 against 0 intact.

### [rewiring] Persistence knock-on (analysis_A): every smell switches on a self-sustained state of about 2,000 neurons. Under rewiring, is the 'smell -> DNa/PPL1 disappears' result about a smell route or about that state, and is the state a generic property of the model's neurons or of its wiring?
STEPS: For the odour drives: recruited non-driven active neurons (active_frac x 139,248 - n_driven) and the state signature readouts (DNa L/R, PPL1, aSP22, oviIN), intact against rewired. Scratch script: a6.py.
CRITERION: No pre-set criterion. The state signature is taken from analysis_A: about 1,980 neurons, DNa about 17, PPL1 about 9, aSP22 about 11, oviIN about 9 Hz.
NUMBERS: Intact, n=3, within 800 ms: every odour except Or47b recruits 1,589-2,006 other neurons (cVA 1,841, food 1,900, CO2 2,006, aversive 2,002). Their readouts carry the state signature: DNa 7.5-24.6 Hz, PPL1 5.3-17.7, aSP22 5.0-10.2, oviIN 3.5-16.9. Or47b alone recruits 61 and drives DNa 0.

All rewired brains, same drives:
- 0-367 other neurons (food and cVA+food 286-367; the rest 0-27).
- DNa at most 1.9, PPL1 at most 2.9 (cVA+food), aSP22 0, oviIN 0.

Caveat: the window is 0.8 s, so ignition later than 0.8 s cannot be excluded.
VERDICT REWORD
PAPER: Add one sentence after analysis_A's new persistence text ('A smell leaves this brain running...'): 'No rewired brain does this: there a smell sets off at most a few hundred neurons, against about 2,000 in the real wiring, so the state belongs to the fly's wiring and not to my neurons.' In Note 2, the smell -> DNa part of the rewiring test should be read as 'the state vanishes', not as a smell-specific route vanishing.
NOTES: In the first 0.8 s, every odour except Or47b sets off the self-sustaining state in the intact brain: 1,589-2,006 other neurons active, DNa 7.5-25 Hz, PPL1 5-18 Hz. In the 3 rewired brains the same odours activate 0-367 other neurons, DNa is at most 1.9 Hz, PPL1 at most 2.9, and aSP22 and oviIN are 0 (n = 3 each).

### [rewiring] Side finding relevant to Note 5 / l.95 ('the paths from those senses to the deciding neurons carry nothing') and 'no state starts egg-laying': do the deciders stay silent in rewired brains?
STEPS: Touch-containing drives: columns pC1c, pC1d, 'vpoDN (DNp37)', 'oviDN egg' and their max1 columns ('oviDNa max1' for oviDN), intact against block. Scratch scripts: a3.py, a8.py.
CRITERION: No pre-set criterion. This is informational and consistent with analysis_A's finding that the deciders are held down by inhibition.
NUMBERS: Touch alone, intact: every decider and oviDN is 0.00.

block0 (n=3):
- pC1c 8.33+-0.36 (max1 16.7)
- pC1d 6.04+-0.36 (max1 12.1)
- vpoDN 2.92+-0.95 (max1 5.8)
- oviDN 1.11+-0.43 (oviDNa max1 6.7)

block1: pC1 and vpoDN 0; oviDN 1.53+-0.43 (oviDNa max1 9.2); aIPg 0.13.

global0: 0.
VERDICT KEEP
PAPER: Unchanged. An optional clause for Note 5: 'In a brain rewired within cell classes, touch does reach pC1c, pC1d and vpoDN (up to 8 Hz in one of two brains) and the egg-laying neurons (1-1.5 Hz in both), so their silence in the real brain comes from its wiring.'
NOTES: Rewired within cell classes, head touch drives pC1c 8.3 +- 0.4, pC1d 6.0 +- 0.4 and vpoDN 2.9 +- 1.0 Hz in one of two brains, and oviDN 1.1 +- 0.4 and 1.5 +- 0.4 Hz in both (one neuron up to 12.5 Hz). All of these are 0.0 in the intact brain (n = 3).

RUN PROBLEMS [rewiring]: The run looks healthy and nothing points to a broken run.
- The .check.txt reports 1140 cells compared and 0 mismatches (tolerance 1e-9): 30 intact rows and 30 global-shuffle-0 rows against experiments/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv. So the engine reproduces the paper's intact brain and its first unconstrained rewired brain to the digit.
- The block rows cannot have a reference, because no block file exists for the paper's model. I cross-checked them against experiments/results/shuffle_flywire_shiu_min1_block.csv (published lobe, same default_rng(100/101)):
  - frac_moved is identical (0.943511 / 0.943445).
  - The none, cVA, JO-A and JO-B rows are bit-identical (max |diff| 0.000; JO-A -> GF 5.21 / 7.50 in both).
  - Only drives that pass through sign-flipped or eLN neurons differ, as expected: touch by up to 14.8 Hz, food 0.6, sugar 0.016.
  So the same rewired topologies were built.
- The CSV is complete: 504 rows = 4 conditions x 42 drives x 3 seeds, with no duplicate rows. There are no NaN readouts (NaN only in min_syn_mem, draw and members, all by design) and no negative values.
- The 'none' drive gives 0 spikes in every condition. The duplicate JO-A/JO-B drives ('...@100') are bit-identical to the plain ones, as they should be.
- The log ends with 'wrote ...' after 1332 s, with no traceback or retry.
- The sidecar shows FLYBRAIN_SIGNS=known, ELN 0.25, NUMBA 6 threads, and sha256_lif 9c6fe7be4bc2aaed / script 5597fa5189e27d67, the same as the other edge steps.

Deviations from design_plan S15, all intended by DECISIONS 6:
- The output is named rewired_flywire_paper.csv, not block_flywire_paper.csv.
- A global shuffle-0 condition was added.

Caveats for the verdicts:
1. Only 2 class-preserving brains and 1 unconstrained brain. Seeds vary only the Poisson input, so the variance that matters is between brains, and it is large (JO-A -> GF 5.2 vs 7.5; touch -> GF 92 vs 56). The "60 %" and "every reflex vanishes" statements rest on n = 2 brains.
2. The global brain is the paper's rewiring 0. The new drives (aBN1, bitter, JO-CE, states) were not run in its rewirings 1-2, including the brain with the 6.35 Hz food -> MDN stray.
3. The window is 800 ms from rest. In the intact brain every odour except Or47b is already in the self-sustaining state within that window. In rewired brains, ignition later than 0.8 s cannot be excluded, and whether the touch burst in block brains (about 1,800-2,060 other neurons active) sustains itself was not tested.
4. Female only. The male under either null (global-shuffle-male-plus) is still pending, so the male cVA and MDN reflexes in the l.93 list are covered here only by the paper's original global male file.

Scratch scripts not kept. (a1-a8.py). No project files were modified and no simulations were run.

>>> CHECK [rewiring] Claim 1 (draft-5 l.89/l.93 'Scramble the wiring and every one of these reflexes disappears', S15 on the paper's model, female). Proposed verdict: REWORD.: agrees=True
OWN: RUN CHECK: experiments/results_edge/shuffle-plus/rewired_flywire_paper.csv has 504 rows = 4 conditions x 42 drives x 3 seeds (0-2). n_driven is identical across conditions. frac_moved is 0.943511 / 0.943445 (block 0/1) and 0.998568 (global 0), exactly the values in the paper files. The .check.txt reports 0 mismatches in 1,140 cells, and my own merge agrees: 24 intact and 24 global-0 rows match experiments/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv to 0.0 on 15 readouts (the check counts 30 rows because the JO-A@100 and JO-B@100 drives map to the same reference inputs). Block rows for JO-A, JO-B, cVA and none are bit-identical to shuffle_flywire_shiu_min1_block.csv; sugar differs by at most 0.016. Sidecar: known signs, eLN 0.25, 6 threads. The log ends normally. No sign of a broken run. RECOMPUTED (intact / B0 / B1 / G0, 3-seed mean +- sd): sugar GRNs->MN9 75.83+-7.32 / 0 / 0 / 0. Shiu sugar->MN9 53.33+-5.05 / 0 / 0 / 0. JO-B->GF 4.79+-0.36 / 0.62+-0.62 / 0 / 0. Shiu JON-CE->aBN1 12.50+-3.31 / 0 / 0 / 0. JO-CE(484)->aBN1 26.67+-0.72 / 0 / 0 / 0. Food->DNa L/R 22.92/13.12 / 1.46/1.04 / 0 / 0. cVA->DNa 10.21/7.29 / 0 / 0 / 0. Sugar+bitter@100 MN9 3.33+-3.82 intact, 0 in every rewired brain. JO-A->GF 10.62+-0.62 / 5.21+-0.95 / 7.50+-0.00 / 0, with DN all 0.12 / 0.08 / 0.10. Specificity 10.50 / 5.13 / 7.40 = 48.8 % and 70.4 % retained (pooled 59.6 %, single runs 41-70 %); raw rate 49 % and 71 %. Touch->DNp13 35.42+-1.30 / 3.75+-1.25 / 12.50+-0.62 / 0, with DN all 8.06 / 14.83 / 13.54 / 0.14. Specificity 27.35 / -11.08 / -1.04, a drop of 140 % and 104 %, so it is gone by rule. Freeze (DNa L+R, smell -> smell+touch): food 36.04 -> 10.21 (index 0.72); cVA 17.50 -> 1.04 (0.94); B0 food 2.50 -> 131.04, cVA 0 -> 125.21; B1 0 -> 101.04 and 0 -> 78.75; G0 0 -> 0. Every number in the verdict reproduces. ADDITIONS THE VERDICT MISSES: (1) Touch alone drives DNa L+R to 128.96 (B0) and 81.25 (B1) against 1.04 intact. The 'reversal' is therefore touch's own drive; the smell adds nothing. (2) In B1 one DNp13 (R) still fires 25.00+-1.25 Hz against 27.92 intact. That is 58 % of its own-side specificity, although the pre-set group readout fails. (3) Smells->DNa is at most 1.46 for single odours but 1.88 for cVA+food (B0). Food->PPL1 is 2.16 in B1 (intact 17.66), which is above 2 Hz but a specificity drop of 87 %, so it is still gone. (4) The male was never block-rewired, so the block sentence is female-only. (5) The target text has moved on. The verdict quotes paper/archive/flycraft_draft5_20260926.tex, but paper/flycraft.tex (06:31 today) is already rewritten: l.126 (definition), l.194 (tests), l.208 ('a sound still fires the escape neuron at about half strength and touch sets off an indiscriminate burst'), and the Notes are %%PENDING. 'About half' fits B0 (49 %) but understates the pooled 60 %. (6) Other current-draft sentences the block result touches: l.83 'scrambling the wiring removes all of it' and l.345 'scrambling the wires removes it' are true only for the random scramble. l.126 says 'a behaviour that survives rewiring cannot be due to the particular wiring', which applied to JO-A contradicts keeping it as a wiring reflex. The table at l.284 and l.203 ('3 have one weak spot', 'fail one each') give the sound reflex one failure (quiet sound), but it also fails to vanish under the class-preserving scramble.
CORRECTED: Verdict REWORD is right. Put the wording into the CURRENT draft rather than draft 5. l.208: 'Scramble the wiring at random, any neuron to any other, each keeping its number of connections, and every one of these reflexes disappears. That test is blunt, because in such a brain almost nothing gets from any sense to any descending neuron. A stricter scramble, which moves each connection only to a neuron of the same broad class as its old target, is harder to pass. In the female, a loud sound still fires the escape neuron, and none of the other neurons I read, at about 60 per cent of its normal rate. Touch sets off the escape, backing and steering neurons all at once, and the ovipositor neuron fires no more than the average descending neuron. Her other reflexes still vanish [note 2].' Say 'steering' rather than 'walking' (DNa01/02), and say 'her other reflexes' because the male was not block-rewired. l.126: end with '...cannot be due to the particular wiring alone (one reflex partly survives a stricter version; Note 2).' l.83 and l.345: 'scrambling the wiring at random removes all of it'. l.203 and table l.284: give the sound reflex its second weak spot ('...a quiet one does not, and it partly survives a class-preserving scramble'), or change '3 have one weak spot'. Notes: as proposed, with these fixes. 'Smells drive DNa at most 1.5 Hz' should read 'at most 1.9 Hz (cVA + food)'. Add 'touch alone drives DNa L+R at 129 and 81 Hz, so food adds nothing and no freeze can be measured' in place of 'so the freeze reverses'. Add 'one of the two DNp13 still fires 25 Hz in brain 1 (28 intact)'. Add 'Unconstrained rewiring: 1 brain for wind and bitter, 3 brains for the rest.'

>>> CHECK [rewiring] Claim 2 (draft-5 Note 2 l.139 'moves 99.8 % of connections and leaves every readout at 0--2 Hz (largest stray value 7 Hz)'; Note 4 l.143 'Every readout 0--2 Hz in a rewired brain'). Proposed verdict: REWORD.: agrees=True
OWN: Readouts are the 36 group-mean columns DNa L..MN9 both, excluding SAG and IPC; 42 drives x 36 = 1,512 cells per brain. The verdict's '1,596 cells' is 42 x 38, which includes SAG and IPC. With 38 columns the counts above 2 Hz are B0 198, B1 139, G0 13. With 36 columns they are B0 194, B1 135, G0 9. G0 (frac_moved 0.998568): every readout averages 0-0.538 Hz (the top one is MBON under pheromones+song+touch), except PPL1 at 2.11-3.33 Hz under the 9 drives that contain whole-head touch. Touch alone gives 2.21+-0.05 and food+touch 3.33+-0.30 (runs 3.20/3.67/3.13). Eye and antennal bristles alone give PPL1 0. Largest single-run group mean is 3.67. DN all is at most 0.178 (food+touch). max1 (single neuron) in G0: DN 54-58 Hz under every whole-head-touch drive and 17-18 Hz under food and cVA+food; PPL1 38.75; KC 57.5; MBON 48.75; PAM 25. hungry@30 gives DN max1 30.42 in all four conditions, including intact, so that is a directly driven NPF neuron and not a stray. DN spikes per 0.8-s trial (DN all x 1,303 x 0.8): touch 147 against 8,404 intact; food+touch 186 against 8,735; food 27 against 1,361. Paper's 3-brain global file, recomputed: pooled max 2.12 (food->MDN), per-brain max 6.35, single run 7.19. Touch->PPL1 per brain 2.21 / 0.94 / 2.24, so '2-3 Hz under touch' is not true of brain 1. DN all at most 0.153. frac_moved 0.998568-0.998588, which is 99.86 % and rounds to 99.9 %, not 99.8. The male file has 0.99808-0.99810; its pooled max is 2.19 (ppk23/25->DNp13) and single run 5.0. BLOCK: max 98.75 (GF, food+touch, B0). Touch (B0 / B1): GF 91.67+-0.95 / 55.83+-1.91; MDN 39.69+-0.31 / 21.46+-1.00; DNa L 62.50 / 52.50; DNa R 66.46 / 28.75; feed MNs 23.69 / 19.65 (16.09 intact); PPL1 12.60 / 12.89; aSP22 2.92 / 33.75; DN all 14.83 / 13.54 (8.06). Every number in the verdict reproduces. ERRORS IN THE PROPOSED WORDING: (a) 'no sense reaches the descending neurons' is false. Single DNs reach 54-58 Hz under touch and 17-18 Hz under food odour. This is the same overstatement verify_wording_full.md already refuted for item 10a. (b) '99.8 %' should be 99.9 % for the female. (c) 'at most 1.5 Hz' for smells holds only for DNa and single odours: cVA+food->DNa R is 1.88; PPL1 reaches 2.16 (food, B1) and 2.89 (cVA+food, B0). (d) 'JO-A ... and nothing else': in B1 PPL1 is 0.76 (one neuron at 16 Hz), and an unnamed DN fires 37.5-52.5 Hz (DN all max1; intact 43.75). (e) Feeding MNs at 20-24 Hz are the intact touch response (16.1) scaled up, not part of a new burst. (f) In the Notes, 'strays up to 15 Hz from inputs without touch ... eye bristles -> GF 43.5' contradicts itself: eye bristles are a touch input, and 43.5 > 15. Antennal bristles -> DNa L 5.6 (B1) is also touch, and intact antennal bristles already drive DNa R at 5.6. The real non-touch strays are bitter->oviIN 15.4 (B1; one neuron at 30-31 Hz), JO-CE->DNa R 5.0 (B0), bitter->PPL1 2.9 (B0; one neuron at 45-50 Hz), JO-CE->oviIN 3.1 (B1) and sugar->DNp09 2.1 (B1).
CORRECTED: REWORD is right; the literal '0-2 Hz' fails in both nulls. Note 2: 'degree-preserving rewiring [maslov2002specificity] in two forms. With any target allowed (99.9 % of connections move; 3 female brains, 2 male), almost nothing from the senses reaches the descending neurons. Their mean rate stays at or below 0.2 Hz even under touch (8.1 Hz intact), although single descending neurons reach 58 Hz. Every readout averages 0-2.2 Hz, except the punishment dopamine neurons, at 0.9-3.3 Hz when the whole head is touched. The largest single-run mean is 7 Hz (MDN, food odour). With each connection moved only to a neuron of its old target's broad class (94 % move; female, 2 brains), sugar, wind, the JO-B sound channel and smells no longer reach their targets (at most 1.9 Hz on the steering neurons), so bitter has nothing to suppress, and the virgin neurons wake nobody. JO-A still drives the giant fibre at 5.2 and 7.5 Hz (10.6 intact) and none of the other neurons I read above 1 Hz. Head touch drives the giant fibre at 56-92 Hz (0 intact), MDN at 21-40 (0.1) and DNa at 29-66 (0.4-0.6), while DNp13 falls to 3.8 and 12.5 Hz (35 intact), below the 14-15 Hz average of all descending neurons.' Note 4 tail: 'Rewired at random, every readout averages 0-2.2 Hz (punishment dopamine neurons up to 3.3 Hz under whole-head touch). Rewired within cell classes, of these reflexes only JO-A -> giant fibre survives (Note 2).' Notes strays line: 'Other inputs give at most 15 Hz (bitter -> oviIN 15.4, brain 1). Touching only the eye bristles drives the giant fibre at 43.5 Hz in brain 0 (0 intact).'

>>> CHECK [rewiring] Claim 3 (which reflexes survive the class-preserving null: JO-A -> GF survives and needs a clause; touch becomes a non-specific burst; freeze reverses). Proposed verdict: CHANGE.: agrees=True
OWN: Criterion: S15 (design_plan l.204-209). A reflex disappears if every block brain is <= 2 Hz or its specificity (target minus DN all) drops >= 80 %; a reflex keeping >= 50 % gets a clause. JO-A->GF: B0 5.21+-0.95 (runs 4.38 / 6.25 / 5.00), B1 7.50+-0.00 (3 identical runs; DN all differs by seed, 0.106 / 0.101 / 0.099, so the seeds did differ), intact 10.62+-0.62. GF max1 is 21.25 intact, 10.42 in B0 and 15.00 in B1, so one of the two GF neurons carries the response. Specificity retained: 48.8 % in B0 (just under the 50 % bar), 70.4 % in B1, 59.6 % pooled. The drops are 51 % and 30 %, so the reflex does not disappear and the clause is required. Other named readouts: all 0 in B0. B1 has PPL1 0.755 (one neuron at 16.25 Hz) and MBON 0.009. DN all max1 is 37.5 (B0) and 52.5 (B1) against 43.75 intact, so an unnamed descending neuron fires harder than GF. 'Every other readout 0' is therefore not strictly true. Published-lobe block file vs this run: JO-A, JO-B, cVA and none rows differ by exactly 0.0 on 15 readouts. Touch differs (DNp13 8.75/13.75 published lobe against 3.75/12.50 here; GF 98.75/56.67 against 91.67/55.83), as expected from the sign and eLN changes. Touch burst pooled over 6 runs: GF 73.75+-19.67; MDN 30.57+-10.01; DNa L 57.50+-5.80; DNa R 47.60+-20.78; feed MNs 21.67+-2.23; PPL1 12.75+-0.32; DN all 14.18+-0.71; DNp13 8.12+-4.87. These all reproduce. The pooled sds mostly reflect the difference between the two brains; per brain: GF 91.67+-0.95 / 55.83+-1.91, MDN 39.69+-0.31 / 21.46+-1.00, DNa R 66.46+-2.82 / 28.75+-2.25. 'All descending groups' is wrong. DNp09 is 5.2 / 0, oviDN 1.1 / 1.5, vpoEN/DN 1.0 / 0, MN9 2.5 / 0, and pC1 0. 'Freeze reverses': smell drives DNa L+R at only 0-2.5 Hz in block brains, touch alone drives it at 129 / 81, and food+touch at 131 / 101. So no freeze can be measured; the touch drive is simply there. Eye bristles->DNp13: 11.46+-0.36 in B0 with DN all 4.69 (51.6 % of intact specificity 13.13), and 0 in B1. Confirmed that it is not a paper claim. S15's SAG sub-test passes. SAG@30 drives pC1a, pC1b, pC1c, vpoEN and vpoDN at 0 in B0, B1 and G0, against 26.0 / 22.5 / 22.9 and vpoDN 20.8 intact. The 3-7.5 Hz on pC1c/vpoDN under SAG+touch in B0 comes from touch, not SAG.
CORRECTED: The substance of the CHANGE is right; reword the true statement as follows: 'Under the class-preserving null the female's sound reflex (JO-A -> giant fibre) survives at about 60 % (49 % and 70 % of its specificity in the two brains), with no other named readout above 1 Hz. Every other female reflex vanishes by the pre-set rule. Head touch no longer picks out DNp13 (3.8 and 12.5 Hz against a descending-neuron mean of 14.8 and 13.5; one DNp13 still at 25 Hz in brain 1) but drives the giant fibre, MDN and both DNa hard. With smells no longer driving DNa (at most 2.5 Hz), there is no freeze to measure, and touch alone drives DNa L+R at 81-129 Hz.' Notes: report per brain rather than pooled: 'giant fibre 91.7 +- 1.0 / 55.8 +- 1.9 Hz, MDN 39.7 +- 0.3 / 21.5 +- 1.0, DNa L 62.5 / 52.5, DNa R 66.5 / 28.8, PPL1 12.6 / 12.9, all descending neurons 14.8 / 13.5 (8.1 intact), DNp13 3.8 +- 1.3 / 12.5 +- 0.6 (35.4 +- 1.3); n = 3 per brain.' Replace 'every other readout at 0' with 'every other named readout below 1 Hz'. Replace 'a burst of all descending groups' with 'a burst in the escape, backing and steering neurons'.

>>> CHECK [rewiring] Claim 4 (persistence knock-on: under rewiring, smell -> DNa/PPL1 vanishing is about the ~2,000-neuron self-sustained state, and the state belongs to the fly's wiring, not the neurons). Proposed verdict: REWORD.: agrees=False
OWN: Recruited = active_frac x 139,248 - n_driven. N = 139,248 is the only N between 139,230 and 139,270 that makes every active_frac x N an integer (error 1e-11). Intact, 0.8 s, n=3. Single odours recruit: cVA 1,841; cVA-long 1,947; Or88a 1,886; Or83c 1,909; food 1,900; CO2 2,006; aversive 2,002; all pheromone ORNs 1,589 (seeds 1,450 / 1,547 / 1,770); Or47b 61. Mixes: cVA+food 1,767; cVA+song 1,848; cVA+sugar 2,184; Or47b+song 98. State signature in the single odours other than Or47b and the pheromone mix: DNa 7.3-22.9 (cVA R 7.29), PPL1 5.3-17.7, aSP22 6.9-10.2, oviIN 3.5-16.9. BUT all pheromone ORNs, despite recruiting 1,589, gives DNa 1.7/4.6, PPL1 0.7 and oviIN 0.2 (aSP22 6.5). It carries the signature only weakly in 0.8 s, although analysis_A found it reaches the state within 1 s (5/5). The verdict's '1,589-2,006 ... DNa 7.5-24.6' therefore takes its lower recruitment bound from a drive that fails its signature range, and its 24.6 and 5.0 come from the cVA+food mix. Rewired (B0 / B1 / G0): cVA, cVA-long, Or47b, Or88a and aversive recruit 0 in all three; Or83c 9-10; pheromone ORNs 11-14; CO2 21-27; food 352 / 349 / 289; cVA+food 360 / 367 / 286; cVA+sugar 87 / 97 / 62 (the sugar part; sugar alone gives 83 / 95 / 63), so 'the rest 0-27' misses it. Rewired maxima over all odour drives: DNa 1.88 (cVA+food, B0), PPL1 2.89 (cVA+food, B0), aSP22 0, oviIN 0. These reproduce. WHY THE CONCLUSION IS TOO STRONG: (1) In rewired brains most smells never get past the receptor neurons (0 recruited for cVA), so the test shows that the route into the state is gone. It does not show that a rewired network cannot hold such a state. (2) Neither the off-phase persistence nor the hum, which ignites the state in the intact brain (analysis_A), was run in any rewired brain. (3) Whole-head touch recruits 2,058 (B0) and 1,805 (B1) non-driven neurons in block brains, against 956 intact and 706 in G0, with PPL1 12.6-12.9 and a DN mean of 14 Hz. Whether that is a self-sustained state of the block brain is untested. (4) 'Not to my neurons' is trivially true, since model neurons have no activity of their own; the open question is whether the state needs this specific wiring. (5) The 0.8-s window is known to miss late ignition in the intact brain: Or47b+CO2 ignites after 1-2 s (analysis_A).
CORRECTED: Keep the reading that smell -> DNa/PPL1 vanishing under rewiring means the state is not reached, not that a smell-specific steering route is gone. Replace the proposed sentence with: 'In a rewired brain a smell never gets that far. In the first 0.8 s it sets off at most a few hundred other neurons, none at all for cVA, against about 2,000 in the real wiring. So it is the fly's wiring that carries a smell into this state. Whether a rewired brain could hold such a state once started, I did not test.' Notes: 'In the first 0.8 s, 7 of the 9 single odours set off the self-sustaining state in the intact brain: 1,841-2,006 other neurons active, DNa 7.3-23 Hz, PPL1 5-18 Hz (n = 3 each). All pheromone receptors together recruit 1,589 neurons but drive DNa only 1.7/4.6 Hz within 0.8 s, and Or47b recruits 61. In the 3 rewired brains the same odours activate 0-27 other neurons (food 289-352; cVA + food up to 367). DNa is at most 1.9 Hz and PPL1 at most 2.9, and aSP22 and oviIN are 0. The off phase and the hum were not run in rewired brains, and touch recruits about 1,800-2,100 neurons in the class-preserving brains.'

### [numerics] Note 1 (l.137): "$dt=0.2$ ms (results identical at 0.1--0.5 ms)". S7 also covers the freeze and the deciders under dt.
STEPS: dt-0.2-10seeds, dt-0.1-10seeds and dt-0.5-10seeds wrote experiments/results_edge/dt-sweep/social_dt{0.2,0.1,0.5}.csv. Each file has 270 rows (27 inputs x seeds 0-9), 1 s, gain 1, known signs + eLN x0.25, 6 threads. dt 0.1 and 0.5 ran through run_redirect --sim dt=...; the sidecars _redirect_social_probe_*.json give ref_steps/delay_steps 22/18 and 4/4. I read every readout column, plus total_spikes and active_frac. Recruited neurons = active_frac*139,248 - n_driven. For the freeze index 1-(L+R)(+touch)/(L+R)(alone) I used the columns 'DNa L' and 'DNa R' of 'food odor' vs 'food + touch' and 'cVA (Or67d/DA1)' vs 'cVA + touch', with a bootstrap SE over seeds. Each dt was compared with 0.2 by a Welch z (10 v 10). The split-half null is seeds 5-9 minus seeds 0-4 at dt 0.2. Scratch scripts not kept.,dt,dt2,state}.py.
CRITERION: S7 (design_plan l.124-134):
- Seeds 0-4 of social_dt0.2 must equal the paper file to the digit.
- Keep "the same within seed noise" for dt 0.1 against 0.2 only if every headline readout differs by less than 2 SE AND by no more than the split-half null. Headline readouts: MN9, feed MNs, DNp13, DNa L/R, the freeze indices for food+touch and cVA+touch, GF, PPL1, KC, and the six deciders.
- dt 0.5: report the size of the shift.
- If dt 0.1 and 0.2 differ by more than 2 SE on a headline number, quote the size.
S10.3 adds: freeze index >= 0.35 at dt 0.1 and 0.5.
DECISIONS.md does not change S7.
NUMBERS: Precondition: social_dt0.2 seeds 0-4 equal experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv in 3,780 of 3,780 cells (0 mismatches). PASS.

Headline readouts, mean +- SD, n = 10, given as dt 0.1 / 0.2 / 0.5 (z vs 0.2):
- sugar -> MN9: 87.1+-4.6 / 81.9+-4.8 / 86.4+-4.5. At 0.1: +5.2 Hz (+6.3 %), z 2.47, split-half +5.0. At 0.5: +4.5, z 2.17.
- sugar -> feed MNs: 26.4+-1.4 / 25.4+-1.6 / 28.4+-1.6. At 0.5: +3.0 (+12 %), z 4.2.
- touch -> DNp13: 36.7+-1.6 / 36.0+-0.8 / 38.0+-1.2. At 0.5: +2.05 (+5.7 %), z 4.4.
- touch -> feed MNs: 15.9 / 16.1 / 16.4.
- cVA -> DNa L/R: 9.9+-1.5 / 9.1+-2.5, 10.5+-1.5 / 9.2+-2.9, 10.4+-1.3 / 9.2+-0.8 (all |z| < 0.9).
- cVA -> PPL1: 6.0+-0.9 / 6.2+-0.9 / 6.8+-0.7 (+10 % at 0.5).
- cVA -> KC: 0.102 / 0.099 / 0.123 (+24 % at 0.5, z 4.6).
- food -> DNa L/R: 21.7+-1.6 / 14.8+-2.9, 22.7+-2.2 / 14.3+-1.9, 23.3+-1.9 / 18.1+-2.5. DNa R at 0.5: +26 %, z 3.8.
- food -> PPL1: 17.6 / 18.0 / 19.1 (z 3.8 at 0.5).
- food -> KC: 1.30 / 1.30 / 1.39.
- food+touch -> DNa L/R: 7.5 / 2.3, 7.8 / 2.8, 8.0 / 3.6.
- cVA+touch -> DNa L/R: 0.05 / 0.45, 0.05 / 0.75, 0.00 / 0.55. DNa R at 0.1: z -2.45.
- JO-A -> GF: 11.5+-0.6 / 11.3+-1.1 / 12.0+-0.8.
- JO-B -> GF: 5.1 / 4.8 / 5.6 (+17 % at 0.5).
- CO2 -> DNa R: 17.4 / 15.7 / 19.3 (+23 % at 0.5).
- Freeze index (bootstrap SE): food 0.734+-0.011 / 0.714+-0.011 / 0.721+-0.023; cVA 0.974+-0.004 / 0.959+-0.007 / 0.972+-0.003. The freeze holds (>= 0.35, S10.3 passes).
- Six deciders: 0.0 in all 810 runs.
- sugar, bitter, touch -> PAM and PPL1: 0.0 at every dt.

S7 rule at dt 0.1: FAILS.
- 2 of 24 headline pairs exceed 2 SE: sugar -> MN9 and cVA+touch -> DNa R.
- 6 more fail only the split-half half of the rule: food -> DNa L (-0.95 vs split 0.50), CO2 -> DNa R (+1.75 vs 0.10), CO2 -> PPL1, cVA -> KC, cVA+sugar -> MN9, and the cVA freeze index (+0.014 vs 0.005).

All 116 input x readout pairs with a rate >= 1 Hz:
- dt 0.1: 6 (5 %, the chance rate) at |z| >= 2 and 1 at |z| >= 3. Median shift 0.0 %. Readouts >= 5 Hz move from -23 % (all pheromone ORNs -> DNa R, 5.05 -> 3.90) to +29 % (Or88a -> DNa R, 10.7 -> 13.9). Largest in Hz: MN9, +5.2.
- dt 0.5: 67 (58 %) at |z| >= 2, all upward, 44 at |z| >= 3. Median +7.7 %. Largest in Hz: Or88a -> DNa R, +6.8 (10.7 -> 17.5).
- Total spikes at dt 0.5: +4.6 to +13.5 % for inputs in the self-sustained state, +1.9 to +4.1 % for the rest.

On/off:
- At the 2 Hz line only one 10-seed mean flips: cVA+song -> GF, 2.15+-1.03 at 0.2 against 1.75 at 0.1 and 1.90 at 0.5. The same readout also flips between seed halves at 0.2 (1.7 vs 2.6).
- Zero/non-zero flips occur only at <= 0.35 Hz.
- Self-sustained state: the same 11 odour-only inputs switch it on in 10 of 10 seeds at every dt (1,468-2,362 recruited neurons; aSP22 > 0). The other 16 inputs never do (<= 453 recruited, or per-input-stable touch combinations). No run changes class.
VERDICT CHANGE
PAPER: Note 1: replace "$dt=0.2$\,ms (results identical at 0.1--0.5\,ms)" with: "$dt=0.2$\,ms. At 0.1\,ms rates stay within seed noise: over 10 seeds of 1\,s, the largest shift, sugar $\rightarrow$ MN9 at 82 against 87\,Hz, is as large as the difference between two sets of five seeds. At 0.5\,ms the refractory period and delay round to 2.0\,ms, and rates rise by a median 8\,\% (at most 7\,Hz). At every step the deciders stay at 0.0\,Hz, the freeze index is 0.71--0.73 for food and 0.96--0.97 for cVA, and no readout crosses 2\,Hz except one that sits on that line (cVA with song $\rightarrow$ giant fibre, 1.8--2.2\,Hz)." Make the same change in the lif.py docstring, run_brain.py --dt help and PAPER.md l.68/l.348 (verify_wording_full item 2).
NOTES: Time step (female, my model, 27 inputs, 10 seeds of 1 s; mean +- SD at dt 0.1 / 0.2 / 0.5):
- sugar -> MN9 87.1+-4.6 / 81.9+-4.8 / 86.4+-4.5; feed MNs 26.4 / 25.4 / 28.4
- touch -> DNp13 36.7 / 36.0 / 38.0
- JO-A -> GF 11.5 / 11.3 / 12.0
- cVA -> DNa L/R 9.9/9.1, 10.5/9.2, 10.4/9.2; PPL1 6.0 / 6.2 / 6.8
- food -> DNa L/R 21.7/14.8, 22.7/14.3, 23.3/18.1; PPL1 17.6 / 18.0 / 19.1
- freeze index: food 0.73 / 0.71 / 0.72, cVA 0.97 / 0.96 / 0.97
- deciders 0.0 in all 810 runs

At 0.1 ms, 6 of 116 rates above 1 Hz differ from 0.2 ms by more than 2 SE (chance predicts about 6), with no systematic direction. The largest, MN9 +5.2 Hz (z 2.5), equals the 5.0 Hz difference between seeds 0-4 and 5-9 at 0.2 ms.

At 0.5 ms (refractory period and delay 2.0 ms), 67 of 116 rates rise significantly and none fall: median +8 %, at most +7 Hz (Or88a -> DNa R 10.7 -> 17.5). Total spikes rise most, 5-14 %, for inputs that switch on the self-sustained state, against 2-4 % for the others.

The same 11 smells switch that state on in every seed at every step. The only readout that crosses 2 Hz is cVA + song -> GF (2.2 -> 1.8/1.9 Hz), and it crosses between seed sets as well.

### [numerics] Note 10 (l.155), thread-count wording: the files that are not identical "differ in a few cells because the originals were made with other thread counts or older scripts". Also: does the thread count change a readout, and does anything cross 2 Hz? (S8, arena on 3 threads).
STEPS: threads-3 and threads-8 wrote experiments/results_edge/threads/social_T3.csv and social_T8.csv: 135 rows each (27 inputs x seeds 0-4), with NUMBA_NUM_THREADS 3 and 8, i.e. 3 and 8 chunks because T = min(threads, 8). Both were compared cell by cell with the T6 paper file, experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv, over 28 numeric columns (wall_s ignored). I also compared 5-seed input means against the T6 per-input seed SD (ddof 1), and counted 2 Hz crossings on both means and single runs. Determinism at the same thread count comes from social_dt0.2 seeds 0-4 (27 Sep, T6) against the same file (26 Sep, T6). Scratch scripts: .../scratchpad/edgeB/{det,thr}.py.
CRITERION: S8 (design_plan l.136-141) as amended by DECISIONS item 4: T3 and T8 replace T8 and T10 (T8 = T10 by construction). Keep if (1) T6-vs-T8 differences are no larger than the per-input seed SD and (2) no readout crosses the 2 Hz presence line. I applied the same test to T3. verify_wording_full item 3 found the sentence 'not false, only imprecise': it never names the 6 threads, the chunk rule, or the arena's 3 threads.
NUMBERS: T3 vs T6: 1 of 135 runs differs (Or47b + touch, seed 3), in 6 cells:
- DNp13 37.5 -> 39.5 Hz
- MDN 0 -> 0.25
- feed MNs 15.79 -> 15.71
- DN all 7.99 -> 7.98
- total spikes +45 (of about 164,500)

T8 vs T6: 2 of 135 runs differ, in 17 cells.
- CO2 + touch, seed 4: DNa L 4.5 -> 5.0, DNa R 2.0 -> 1.0, DNp13 31.5 -> 31.0, PPL1 9.0 -> 9.375, feed MNs -0.21, total spikes -249 of 213,700.
- cVA + song, seed 3: DNa L 9.5 -> 8.5, PPL1 6.125 -> 6.0, total spikes about +30 of 66,700.

T3 vs T8: 3 runs, 23 cells. The affected runs are high-activity multi-input drives (two with touch, one in the self-sustained state).

On 5-seed means (n = 5):
- The largest change is 0.40 Hz: Or47b+touch -> DNp13, 37.5 -> 37.9, against a T6 seed SD of 1.37 (ratio 0.29).
- At T8 the largest are 0.20 Hz: CO2+touch DNa R 1.2 -> 1.0 (SD 0.57, ratio 0.35), and cVA+song DNa L 9.1 -> 8.9 (ratio 0.21).
- Every change is at most 0.45 x the per-input seed SD. Criterion 1: PASS.

2 Hz line:
- No 5-seed mean crosses it at T3 or T8. Criterion 2: PASS.
- One single run crosses it: CO2 + touch seed 4, DNa R 2.0 -> 1.0 Hz at T8.

Same thread count: a third run (27 Sep) reproduces the 26 Sep T6 file in 3,780 of 3,780 cells.
VERDICT REWORD
PAPER: S8 passes, so the substance stands; the rewording adds precision (verify_wording_full item 3) and the measured size. Note 10: after "...and by at most 0.004 in the learned weights." insert: "The thread count matters because the simulator splits the neurons into min(threads, 8) chunks and sums their spikes chunk by chunk in single precision. The re-run used 6 threads, and each arena brain runs on 3. On 3 and on 8 threads the 1-s probe changed in 1 and 2 of its 135 runs, by at most 2\,Hz in one run and 0.4\,Hz in any five-seed mean, and no mean crossed 2\,Hz. On the same thread count a third run reproduced it to the digit."
NOTES: Threads (social probe, 27 inputs x 5 seeds, 1 s):
- 3 threads (3 chunks) changes 1 of 135 runs: Or47b + touch seed 3, DNp13 37.5 -> 39.5 Hz, +45 of 164,500 spikes.
- 8 threads changes 2 runs: CO2 + touch seed 4, DNa L/R 4.5/2.0 -> 5.0/1.0 Hz and PPL1 9.0 -> 9.4; cVA + song seed 3, DNa L 9.5 -> 8.5.
- On 5-seed means: at most 0.4 Hz (0.29 seed SD) at T3 and 0.2 Hz (0.35 seed SD) at T8. No mean crosses 2 Hz; one single-seed DNa R value does (2.0 -> 1.0).
- Six threads twice (26 and 27 Sep): identical to the digit in all 3,780 cells.

This thread-only effect (<= 0.4 Hz on 5-seed means) is much smaller than the 3.3 Hz maximum quoted for re-run vs originals. That 3.3 Hz must therefore come from files with fewer seeds, longer runs in the self-sustained state, or older scripts. This test cannot say which.

### [numerics] Held-out seeds: do the Note 4/5 headline numbers survive seeds 5-9, which were never used before? (design_critique 'Held-out seeds already paid for'.) Scope: the female 1-s probe. That covers the deciders' 0.0 (Note 5), taste/touch -> dopamine 0.0 (Note 7), and the 1-s analogues of Note 4's sugar -> MN9, sound -> GF, touch -> DNp13 and the freeze.
STEPS: experiments/results_edge/dt-sweep/social_dt0.2.csv, split into seeds 0-4 (identical to the paper file) and seeds 5-9 (new), n = 5 each. Per input x readout I computed mean +- SD, a Welch z (5 v 5), and flips at the 2 Hz line and at 0; the freeze index was computed per half. I also compared with the paper's 0.6-s sources: experiments/results/gain_sweep_flywire_shiu_min1+known+eln0.25.csv (gain 1.0, 5 seeds) and contact_stop_flywire.csv (3 seeds). Scratch script: .../scratchpad/edgeB/held.py.
CRITERION: No numeric line was fixed before the runs (design_critique only says 'evaluate them explicitly'). My scoring: a number survives if (a) the held-out 5-seed mean lies within 2 SE (Welch) of seeds 0-4, (b) no 0.0 claim becomes non-zero, and (c) no on/off verdict at the suite's 2 Hz presence line (S8) flips. The Note 4 values are 0.6-s means, so the 1-s seeds test seed stability, not the typed number itself.
NUMBERS: Seeds 0-4 (paper file) against seeds 5-9, mean +- SD, n = 5 each:
- sugar -> MN9: 79.4+-3.4 vs 84.4+-5.0 (+5.0 Hz, z 1.86)
- sugar -> feed MNs: 24.8+-1.7 vs 26.0+-1.4 (z 1.30)
- touch -> DNp13: 35.6+-1.0 vs 36.3+-0.4 (z 1.48)
- touch -> feed MNs: 16.2 vs 15.9; MDN 0.20 vs 0.05
- JO-A -> GF: 11.1+-0.6 vs 11.4+-1.5
- JO-B -> GF: 5.0 vs 4.6
- cVA -> DNa L/R: 10.1/8.4 vs 10.8/10.0 (z 0.73/0.86); PPL1 5.9 vs 6.4
- food -> DNa L/R: 22.4/14.0 vs 22.9/14.6; PPL1 17.8 vs 18.2
- food+touch -> DNa L/R: 8.0/3.1 vs 7.5/2.5; freeze index 0.695 vs 0.733
- cVA+touch -> DNa L/R: 0.0/0.7 vs 0.1/0.8; freeze index 0.962 vs 0.957
- CO2 -> DNa L/R: 15.8/15.6 vs 14.3/15.7
- pheromones+song+touch -> DNp13: 35.1 vs 34.1 (z -2.02, the only headline pair past 2 SE)
- Or47b -> DNa 0.0/0.0, DN all 0.01, KC 0.00 in both halves

Zero claims:
- All six decider groups are 0.0 in all 135 held-out runs.
- sugar, bitter and touch -> PAM and PPL1 are 0.0 in every held-out run.

Whole file: of 115 pairs with a rate >= 1 Hz, 4 (3.5 %) differ at |z| >= 2 and none at |z| >= 3. Total spikes per input agree within 0-4 %, except Or83c at +9.9 %: seed 4 switched the self-sustained state on late (27,636 spikes against 45-57k).

Flips between halves:
- At 2 Hz, only two non-claim readouts: all pheromone ORNs -> DNa L (1.7 vs 2.8) and cVA+song -> GF (1.7 vs 2.6).
- At 0, only values <= 0.1 Hz.

Against the 0.6-s sources:
- gain_sweep at gain 1.0 (5 seeds): MN9 76.0, GF 10.8, DNp13 35.2.
- contact_stop (3 seeds): food 20.3/12.3 -> 6.8/3.2 (index 0.69); cVA 9.3/8.2 -> 0/1.2 (index 0.93).
- The 1-s values sit higher because responses ramp up over 0.1-0.4 s (analysis_A persistence).
- The 1-s cVA freeze index is 0.96 in both halves, above Note 4's 0.93 (a window effect) but inside analysis_A's reworded range, 0.31-0.98.
- A 5-seed MN9 value carries a SE of about 2 Hz (10-seed SD 4.8).
VERDICT KEEP
PAPER: No change needed. Optional line for Note 10: "Five new seeds (5--9) reproduce every 1-s number of Notes 4 and 5 within seed noise, and the deciders and the teaching neurons stay at 0.0\,Hz in all of them."
NOTES: Held-out seeds (female 1-s probe, seeds 5-9 never run before, n = 5; seeds 0-4 are the paper file), given as 0-4 vs 5-9:
- sugar -> MN9 79.4+-3.4 vs 84.4+-5.0 Hz
- touch -> DNp13 35.6+-1.0 vs 36.3+-0.4
- JO-A -> GF 11.1+-0.6 vs 11.4+-1.5
- cVA -> DNa L/R 10.1/8.4 vs 10.8/10.0
- food -> DNa 22.4/14.0 vs 22.9/14.6
- freeze index: food 0.70 vs 0.73, cVA 0.96 vs 0.96
Every decider and every dopamine neuron stays at 0.0 Hz to taste and touch in all 135 new runs. Of 115 rates above 1 Hz, 4 differ by more than 2 SE, about what chance gives.

Not testable with these runs: the male numbers, gains 0.7 and 1.4, JO-CE -> aBN1 (no aBN1 column), Shiu's 29 sugar neurons with bitter, the 14 conditions, steering (see odor-dose-10seeds) and the clean box.

### [numerics] Brian2 agreement. l.89: "My version reproduces Shiu et al.'s own code spike for spike in two test runs out of three, and in the third a single neuron near its threshold tips the other way (Note 1)". Note 1: sugar, published model, dt 0.1 ms. S6 asks: does this hold for the model the paper actually uses, with the drives the social claims rest on, at production dt?
STEPS: brian2-paper-model (logs/edge/guarded_brian2-paper-model.out) exported the paper model (FLYBRAIN_SIGNS=known, ELN=0.25) and ran brain/tests/brian2_reference.py (Brian2 2.10.1, cython) and compare_brian2.py (kernel; per-seed totals, 3-seed group mean +- population SD, per-neuron r). Drives, 100 Hz, 1 s, 3 seeds:
- in_orn_cva (205 neurons = ORN_DA1 126 + ORN_DL3 79), dt 0.1
- in_bristle (1,417), dt 0.1
- in_grn_sugar (129), dt 0.1 and dt 0.2
Outputs: experiments/results_edge/brian2-paper-model/cmp_*.txt and ref_*.npz. I read the per-seed Brian2 counts from the npz files. The kernel totals were cross-checked against social_dt0.1/0.2 and the paper file. The Brian2 sugar counts were compared with the published-model reference $TMPDIR/flycraft_brian2/ref_sugar.npz. Scratch script: .../scratchpad/edgeB/b2.py.
CRITERION: S6 (design_plan l.108-122): KEEP only if, for every drive, every printed group is within max(2 seed-SD, 10 %), per-neuron r >= 0.99, and sugar is identical in at least 2 of 3 seeds at both dt. An odour or touch group more than 3 SD off, or r < 0.95, limits the Brian2 claim to taste. 'Seed-SD' is not defined. I used the larger of the two printed 3-seed SDs (population SD, as compare_brian2 prints); the result is the same with n-1.
NUMBERS: Identical seeds per drive (compare_brian2 does not save kernel per-neuron counts, so 'identical' means identical totals; for sugar at dt 0.2 every per-neuron mean is also identical).

Sugar, dt 0.2: 3 of 3 seeds identical.
- Totals 23,059 / 23,614 / 23,795 in both engines, r = 1.0000, 0 one-sided neurons, largest per-neuron difference 0.
- These are exactly the paper file's sugar seeds 0-2.

Sugar, dt 0.1: 2 of 3 identical (24,215; 24,782).
- Seed 0: kernel 23,868 vs Brian2 24,372 (-2.1 %).
- r = 0.9998; feed MNs 27.13+-1.27 vs 27.92+-0.45.
- Brian2's sugar seeds 1-2 are also identical in every neuron to its run on the published model, so the sugar test barely touches my changes.

Touch, dt 0.1: 2 of 3 identical (155,532; 157,054).
- Seed 0: 156,645 vs 156,491 (+0.10 %).
- r = 0.9999; DNp13 38.00 in both; feed MNs 15.96 vs 15.88; DNa R 0.83 vs 0.67. Every group passes.

cVA, dt 0.1: 0 of 3 identical.
- Kernel minus Brian2: +1,475 (+2.7 %), +10,202 (+23.9 %), -59 (-0.1 %).
- r = 0.9974. Of 2,369 active neurons, 108 fire in the kernel only and 75 in Brian2 only.
- DNa L: 10.00+-0.71 vs 8.00+-1.41 (-20 %, within 2 SD).
- DNa R: 6.83+-0.24 vs 4.33+-0.62 (-37 %). The gap of 2.5 Hz is 4.0 x the larger SD (3.3 x with n-1) against an allowed max(1.25, 0.68). FAIL, beyond 3 SD. The per-seed values implied by these SDs are {6.5, 7, 7} against {3.5, 4.5, 5}.
- PPL1: 5.31+-0.14 vs 4.02+-1.12 (-24 %, within 2 SD).
- DAN, MBON, KC and DN all are all lower in Brian2 but within 2 SD.

Why cVA diverges: every Brian2 cVA seed enters the self-sustained state (1,755-1,936 non-driven neurons active, against about 1,870 in the kernel). Brian2 seed 1 has 24 % fewer spikes, which is consistent with a later switch-on. The state amplifies differences. In the kernel over 10 seeds, the seed CV of total spikes is 1-17.5 % for inputs in the state (cVA 4.8 %) against 0.2-2.2 % for the others, and the DNa SD of state drives at dt 0.1 is 0.7-3.7 Hz (cVA 1.5 / 2.5). The engine gaps are therefore about one 10-seed SD, but beyond the 3-seed SD that the rule uses.

Result: taste passes (2/3 identical at 0.1, 3/3 at 0.2); touch passes; cVA fails. The pre-set consequence is to limit the claim to taste. Touch passes too.
VERDICT REWORD
PAPER: l.89: replace the sentence with: "My version reproduces a Brian2 transcription of Shiu et al.'s code spike for spike when taste or touch drives it, in seven test runs of nine, and the other two end within about 2\,\% of it. Smell is different. It switches on firing that keeps itself going (below), which magnifies the smallest difference, so with the male pheromone the two programs part in every run and the steering neurons end up 20--40\,\% apart, no more than two runs of either program differ from each other \note{1}."

Note 1: replace the Brian2 sentence with: "Against Brian2 2.10.1 \citep{stimberg2019brian}, a transcription of Shiu et al.'s model.py, at 100\,Hz for 1\,s with 3 seeds. Published model, sugar, $dt=0.1$\,ms: identical per-neuron spike counts in two seeds; the third diverges (23{,}689 against 23{,}512 spikes; per-neuron correlation 0.9999). My model: sugar at $dt=0.2$\,ms is identical in every neuron in all three seeds. At 0.1\,ms sugar and head bristles are identical in two seeds, and the third ends 2.1\,\% and 0.1\,\% apart (correlation 0.9998 and 0.9999; DNp13 38.0\,Hz in both). cVA at 0.1\,ms: no seed is identical, totals end 0.1, 2.7 and 24\,\% apart (correlation 0.9974), DNa L/R are 10.0/6.8 against 8.0/4.3\,Hz and PPL1 5.3 against 4.0\,Hz. cVA switches on the self-sustaining state (Note 5), in which one diverging spike grows. These gaps are within the 10-seed spread of such inputs, but for DNa R they are four times the 3-seed spread, so the spike-for-spike claim covers taste and touch only."

Do not keep 'a single neuron near its threshold': no file shows it, and S5 brian2-first-divergence has not run yet.
NOTES: Brian2 on my model (known signs, eLN x0.25; 100 Hz, 1 s, 3 seeds):
- Sugar, dt 0.2 (production): identical in every neuron in 3 of 3 seeds (23,059 / 23,614 / 23,795 spikes, the paper file's own runs).
- Sugar, dt 0.1: 2 of 3 identical; seed 0 is 23,868 vs 24,372 (r 0.9998).
- Head bristles, dt 0.1: 2 of 3 identical; seed 0 is +154 of 156,500 (r 0.9999); DNp13 38.0 vs 38.0 Hz.
- cVA (DA1 + DL3 ORNs), dt 0.1: 0 of 3 identical; totals +2.7 / +23.9 / -0.1 % (r 0.9974). Kernel against Brian2: DNa L 10.0+-0.7 vs 8.0+-1.4, DNa R 6.8+-0.2 vs 4.3+-0.6, PPL1 5.3+-0.1 vs 4.0+-1.1 Hz.

Every Brian2 cVA run enters the ~1,900-neuron self-sustained state; one does so late (24 % fewer spikes). DNa R is 4 x the 3-seed SD off, which by the pre-set rule limits spike-for-spike agreement to taste (touch also passes). The size of the gap is about one 10-seed SD of state-driven DNa (1.5-2.9 Hz).

Sugar alone barely exercises my changes: Brian2's sugar seeds 1-2 are identical, neuron for neuron, on the published and on my model.

RUN PROBLEMS [numerics]: No step failed and no run looks broken. Each of the six steps (dt-0.2/0.1/0.5-10seeds, threads-3/8, brian2-paper-model) passed on attempt 1 (logs/edge/queue_20260927.out), and each log ends with 'wrote ...'. There are no tracebacks and no NaNs. 'none' gives 0 spikes at every dt. n_driven is identical across dt, and every file has the expected shape: 270 rows for dt, 135 for threads.

1. None of these steps writes a .check.txt: the step commands have no --check-against. My manual checks replace it:
   - social_dt0.2 seeds 0-4 equal the paper file in 3,780/3,780 cells (the S7 precondition passes).
   - compare_brian2's kernel totals equal social_dt0.1 seeds 0-2 for sugar (23,868/24,215/24,782) and touch (156,645/155,532/157,054).
   - At dt 0.2 they equal the paper file's sugar seeds 0-2 (23,059/23,614/23,795; feed MNs 24.15).
   - So run_redirect --sim dt agrees with a direct LIFParams(dt), and the Brian2 export is the paper model.
   - Every production .check.txt elsewhere in results_edge shows 0 mismatches. The _smoke mismatches are the expected ones analysis_A already explained.

2. Missing provenance:
   - social_dt0.2 and both thread files ran plain social_probe, so they have no sidecar and the thread count is unrecorded.
   - T3 != T6 != T8 != T3 shows the setting took effect.
   - The dt 0.1 and 0.5 sidecars give ref/delay steps 22/18 and 4/4, as intended.

3. Brian2 step:
   - The log shows benign Brian2 'w_syn' namespace-resolution WARNINGs: it uses the group value, 275 uV = 0.275 mV, so the kick is 68.75 mV.
   - The step took 41 s, not the planned 12 min, but the per-seed wall times printed (Brian2 about 2 s, kernel 0.1-1.3 s) and the cross-checks above show it ran correctly.
   - compare_brian2.py does not save kernel per-neuron counts. At dt 0.1, 'identical' therefore rests on identical totals, and the per-seed kernel group rates are not recoverable (I inferred DNa R per seed from the printed means and population SDs).
   - The S6 'seed-SD' is unspecified; the DNa R failure holds under every reading.

4. The S7 split-half null is a single 5-v-5 draw. When it comes out small by chance (e.g. CO2 -> DNa R, 0.10 Hz), that half of the rule fails easily. I report both halves separately.

5. Still queued, not run: brian2-first-divergence (S5) and dt-rounding-control. So 'a single neuron near its threshold' and 'the dt 0.5 shift is rounding' remain untested.

6. Knock-on for whoever scores the freeze (analysis_A reflexes):
   - At 1 s, aSP22 is exactly 0 in every touch-combination run at every dt, while all 110 odour-only runs per dt are in the self-sustained state.
   - cVA+touch recruits only about 100 neurons beyond touch alone, with PPL1 0. So the cVA freeze (index 0.96) at 1 s amounts to touch keeping the brain out of the state.
   - food+touch and CO2+touch still recruit about 1,500-1,650 extra neurons (PPL1 17.7 and 8.7 Hz), yet their DNa stays suppressed. So the food freeze is not just the state being off.
   - Separately, the self-sustained state makes odour runs 2-10x more variable across seeds than the others. That is why the Or83c seed halves differ by 10 % and why cVA is the only Brian2 drive that diverges.

Scratch scripts not kept. (det.py, dt.py, dt2.py, state.py, held.py, thr.py, b2.py, dt_headline.csv). No project file was modified and no simulation was run.

>>> CHECK [numerics] Note 1 (draft 5 l.137): 'dt=0.2 ms (results identical at 0.1--0.5 ms)'. S7 dt sweep, verdict CHANGE.: agrees=True
OWN: I agree with CHANGE. My own scripts are in scratchpad/refuteB/dt1.py, dt2.py and dt3.py. 'Identical' is false: dt 0.5 shifts rates systematically. Every number in the verdict reproduces. Three details are imprecise and one rounding wording depends on the >= convention.

Files: experiments/results_edge/dt-sweep/social_dt{0.1,0.2,0.5}.csv. Each has 270 rows (27 inputs x seeds 0-9), no NaN, and 'none' = 0 everywhere. Sidecars: ref/delay steps 22/18 at dt 0.1 and 4/4 at dt 0.5; w_syn 0.275, kick 68.75, noise 0, 6 chunks, lif sha 9c6fe7be4bc2aaed. Logs end 'run_redirect: ok'. None of the three steps has a .check.txt, so the precondition is the engine check.

PRECONDITION: seeds 0-4 of social_dt0.2 (27 Sep) against experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv (26 Sep): 0 of 3,645 cells differ (135 runs x 27 columns, wall_s excluded; 3,780 if seed is counted). PASS.

HEADLINES, 10-seed mean +- SD (ddof 1), dt 0.1 / 0.2 / 0.5, with Welch z against 0.2 and the split-half difference (seeds 5-9 minus 0-4 at 0.2):
- sugar -> MN9: 87.1+-4.6 / 81.9+-4.8 / 86.4+-4.5; z01 2.47, split +5.0; z05 2.17.
- sugar -> feed MNs: 26.4 / 25.4 / 28.4; z05 4.24.
- touch -> DNp13: 36.65 / 35.95 / 38.0; z05 4.44.
- cVA -> DNa L/R: 9.9/9.1, 10.45/9.2, 10.4/9.15.
- cVA -> PPL1: 6.04 / 6.15 / 6.78.
- cVA -> KC: 0.102 / 0.099 / 0.123 (z05 4.55).
- food -> DNa L/R: 21.7/14.8, 22.65/14.3, 23.3/18.05 (R z05 3.77).
- food+touch -> DNa L/R: 7.45/2.25, 7.75/2.8, 7.95/3.6.
- cVA+touch -> DNa R: 0.45 / 0.75 / 0.55 (z01 -2.45).
- JO-A -> GF: 11.45 / 11.25 / 11.95.
- CO2 -> DNa R: 17.4 / 15.65 / 19.25 (split +0.10).
- Freeze index (ratio of seed means, bootstrap SE, 4,000 resamples): food 0.734+-0.011 / 0.714+-0.011 / 0.721+-0.020; cVA 0.974+-0.004 / 0.959+-0.007 / 0.972+-0.002. The lowest single seed is 0.573, so S10.3 (>= 0.35) passes.
- The six deciders are 0.0 in all 810 runs. PAM and PPL1 are 0.0 for sugar, bitter and touch at every dt.
- S7 at dt 0.1 FAILS as the verdict says: sugar -> MN9 (z 2.47, and 5.2 > 5.0 split) and cVA+touch -> DNa R (z -2.45). The rule then says to quote the size.
- Caveat on the split-half null: it is one realisation (a 5-v-5 difference, SD about 0.63 seed-SD). It can land near 0 by chance, e.g. CO2 -> DNa R split +0.10 against SD 2.0. So the '6 more fail only the split-half half' are weak evidence.

ALL PAIRS: 114, 116 or 117 pairs, depending on whether the >= 1 Hz filter applies to dt 0.2 only, to either side of each comparison, or to any dt.
- dt 0.1: 5, 6 or 6 pairs at |z| >= 2 and 1 at |z| >= 3. 55 move up and 58 down; median -0.1 %.
- dt 0.1, largest in Hz: MN9 +5.2. Largest relative: Or88a -> DNa R 10.7 -> 13.85 (+29 %, z 2.77, 2.6 x its split of 1.2). So MN9 is the largest shift only in Hz.
- dt 0.5: 66 or 67 pairs at |z| >= 2, all upward, and 43 or 44 at >= 3. Median +7.7 %; the largest is Or88a -> DNa R +6.8 Hz (+64 %).
- Among rates >= 5 Hz at dt 0.5 the change runs from -9 % to +64 %. DNa R in the self-sustaining state rises 19-31 % for Or83c, food, CO2 and DA2/DL4.
- 8 pairs fall at dt 0.5, none significantly (at most -0.45 Hz).
- Left-right steering (DNa L - R) keeps its sign for all 12 odour inputs at every dt. Or88a -1.9 -> -6.4 Hz (z -4.8); food +8.35 -> +5.25 (z -1.85).
- Total spikes at dt 0.5: +4.6 to +13.5 % for inputs in the state, +1.9 to +4.1 % for the rest.

2 Hz LINE (10-seed means):
- cVA+song -> GF: 1.75 / 2.15 / 1.90 (seed halves 1.7 / 2.6). The verdict names this one.
- It is not the only mean on the line: all pheromone ORNs -> DNa L is 2.00 / 2.25 / 2.25 (halves 1.7 / 2.8 at 0.2; 2.5 / 1.5 at 0.1). It stays above the line only because 2.00 counts as >= 2.
- Every zero/non-zero flip is at or below 0.35 Hz.

HELD-OUT SEEDS (critique item 65), seeds 5-9 against 0-4 at dt 0.2: 4 of 115 pairs at |z| >= 2 and 0 at >= 3. Two means cross 2 Hz between the halves (the two readouts above).

STATE: the same 11 inputs have aSP22 > 0 in 10 of 10 seeds at every dt, with 1,469-2,363 recruited neurons. They are 8 single odours plus cVA+food, cVA+song and cVA+sugar, so not 'odour-only' as the verdict says. Or47b alone recruits only 60-64 neurons in 1 s at every dt: the state is not switched on within 1 s by every smell. Inputs with touch recruit 1,044-2,651 neurons but have aSP22 = 0, so their state is ambiguous.

MECHANISM: the kernel applies a synapse one step after the rounded delay (wr_off = delay_steps + 1, as in Brian2). The effective latency is therefore 1.9 / 2.0 / 2.5 ms at dt 0.1 / 0.2 / 0.5, and the refractory period is 2.2 / 2.2 / 2.0 ms. The queued dt-rounding-control (t_ref 2.0, delay 2.4 at dt 0.1) matches this correctly but has not run. The rounding is therefore not yet shown to cause the rise.
CORRECTED: Paper, Note 1: replace '$dt=0.2$\,ms (results identical at 0.1--0.5\,ms)' with: '$dt=0.2$\,ms. At 0.1\,ms rates stay within seed noise: over 10 seeds of 1\,s, 6 of 116 rates above 1\,Hz differ from 0.2\,ms by more than two standard errors, as many as chance predicts and in both directions, and the largest in Hz, sugar $\rightarrow$ MN9 at 87 against 82\,Hz, equals the difference between two sets of five seeds. At 0.5\,ms, where the refractory period and the delay become 2.0\,ms, rates rise by a median 8\,\% and at most 7\,Hz, most in the steering neurons (Or88a $\rightarrow$ DNa R 10.7 against 17.5\,Hz), and none falls significantly. At every step the deciders stay at 0.0\,Hz, the freeze index is 0.71--0.73 for food and 0.96--0.97 for cVA, and no mean rate changes side of 2\,Hz except two that sit on that line (cVA with song $\rightarrow$ giant fibre, 1.8--2.2\,Hz; all pheromone neurons $\rightarrow$ left DNa, 2.0--2.3\,Hz).' Do not claim that the rounding causes the rise until dt-rounding-control has run. Make the same change in the lif.py docstring, run_brain.py --dt help and PAPER.md l.68/l.348.

Notes, changes to the verdict's text:
(1) '67 of 116 rates rise significantly and none fall' -> '...and none falls significantly (8 fall by at most 0.45 Hz); the largest relative rise is +64 % (Or88a -> DNa R); left-right steering keeps its sign for every odour at every dt (Or88a -1.9 -> -6.4 Hz at 0.5, z -4.8).'
(2) 'The same 11 smells' -> 'The same 11 inputs (8 single odours, and cVA with food, song or sugar; every odour input without touch except Or47b, which recruits only 60-64 neurons in 1 s)'.
(3) Add: 'all pheromone ORNs -> DNa L also sits on the 2 Hz line: 2.00 / 2.25 / 2.25 Hz; seed halves 1.7 / 2.8 at 0.2 ms'.
(4) Add a held-out-seed line: 'seeds 5-9 against 0-4 at 0.2 ms: 4 of 115 pairs at |z| >= 2, none >= 3; deciders 0.0'.
(5) Add: 'the effective synaptic latency is 1.9 / 2.0 / 2.5 ms; the cause of the dt 0.5 rise is pending dt-rounding-control'.

>>> CHECK [numerics] Note 10 (draft 5 l.155): the files that differ 'differ in a few cells because the originals were made with other thread counts or older scripts'. S8 as amended (T3 and T8 against the T6 paper file). Verdict REWORD.: agrees=True
OWN: I agree with REWORD. S8 passes, the counts reproduce exactly and the proposed paper sentence is accurate. The verdict's last notes paragraph is wrong, and the verdict misses a stronger confirmation. Script: scratchpad/refuteB/thr.py.

CELL-BY-CELL against the T6 paper file (27 columns, wall_s excluded):
- T3: 1 of 135 runs and 6 cells differ, all in Or47b+touch seed 3. DNp13 37.5 -> 39.5, MDN 0 -> 0.25, feed MNs 15.79 -> 15.71, DN all 7.99 -> 7.98, total spikes 164,451 -> 164,496.
- T8: 2 runs and 17 cells. CO2+touch seed 4: DNa L/R 4.5/2.0 -> 5.0/1.0, DNp13 31.5 -> 31.0, PPL1 9.0 -> 9.375, feed MNs 15.75 -> 15.54, total spikes 213,710 -> 213,461. cVA+song seed 3: DNa L 9.5 -> 8.5, PPL1 6.125 -> 6.0, total spikes 66,692 -> 66,721.
- T3 against T8: 3 runs, 23 cells.

5-SEED MEANS against the T6 per-input seed SD (ddof 1):
- T3: largest Or47b+touch DNp13 37.5 -> 37.9 (0.29 SD). Largest ratio: MDN 0.05 -> 0.10 (0.45 SD).
- T8: CO2+touch DNa R 1.2 -> 1.0 (0.35 SD); cVA+song DNa L 9.1 -> 8.9 (0.21 SD).
- No mean crosses 2 Hz. One single run does: CO2+touch seed 4 DNa R 2.0 -> 1.0. Criteria 1 and 2 pass.

DETERMINISM: social_dt0.2 seeds 0-4 (27 Sep) equal the paper file (26 Sep) in every cell. The paper file also equals release/pre_rerun_20260926 (25 Sep 20:14) apart from wall_s. That makes three T6 runs to the digit, not two as the verdict's notes say.

NEW EVIDENCE 1: the original 16 Sep probe file, release/pre_rerun_20260925/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv, equals the new T8 run to the digit (0 of 3,645 cells differ). Against T6 it differs in exactly the same 2 runs and 17 cells. For this file the entire original-vs-re-run difference is the chunk count, which confirms 'because the originals were made with other thread counts' directly.

NEW EVIDENCE 2: Note 10's 3.3 Hz is a single cell, not a mean. It is precontact_dose_flywire_shiu_min1+known+eln0.25_far.csv, row 'mf far: cVA 0.06, Or47b 0.10, CO2 0.003', noise 0.2 Hz, seed 1: DNa R 11.5 -> 14.75. That run reads 2 s after 2 s of settling, under the hum, in the self-sustaining state. The original was written 24 Sep 18:09, and RESEARCH_NOTES l.1847 says those hum dose cells were made with 10 threads.
- Every differing row in the _far and _near files is a hum (0.2 Hz) run.
- The verdict compares its 0.4 Hz five-seed-mean maximum with a single-cell 3.3 Hz. The like-for-like comparison is its 2.0 Hz largest single-run change.
- The verdict's 'this test cannot say which' is therefore too weak: the files say it is the thread count, in a hum run.

CODE CHECK (lif.py): buffers v, g and buf are float32. T = max(1, min(threads, 8)); neuron i sits in chunk i % T, and spikes are delivered chunk by chunk. par_min = 3000*T also depends on T.
CORRECTED: Paper, Note 10: keep the verdict's insertion. Tighten the mechanism clause and add the original-file identity: 'The thread count matters because the simulator splits the neurons into min(threads, 8) chunks, and the chunks set the order in which single-precision synaptic input is added up. The re-run used 6 threads, and each arena brain runs on 3. On 3 and on 8 threads the 1-s probe changed in 1 and 2 of its 135 runs, by at most 2\,Hz in one run and 0.4\,Hz in any five-seed mean, and no mean crossed 2\,Hz. The original probe file, made on 10 threads (8 chunks), is identical to the digit to the new 8-thread run. On the same thread count, three runs agree to the digit.'

Notes: replace the verdict's last paragraph with: 'The original 16 Sep probe file equals the 8-thread run in all 3,645 cells, and differs from the 6-thread re-run in exactly those 2 runs and 17 cells, so for that file the chunk count explains the whole difference. The 3.3 Hz maximum in Note 10 is one single-seed cell: precontact_dose_..._far.csv, mf far under the 0.2 Hz hum, seed 1, DNa R 11.5 -> 14.75 Hz. That is a 2-s read after 2-s settling in the self-sustaining state, from a file made with 10 threads on 24 Sep. Set it against the 2.0 Hz largest single-run change here, not against the 0.4 Hz five-seed-mean change. Six threads: 25, 26 and 27 Sep runs identical in all 3,645 cells.'

>>> CHECK [numerics] Brian2 agreement. Draft 5 l.89 says 'spike for spike in two test runs out of three... a single neuron near its threshold tips'; Note 1 covers published model, sugar, dt 0.1. The current flycraft.tex l.160 says 'in most test runs; where it does not, one neuron near its threshold tips the other way and the difference spreads'. S6 on the paper model. Verdict REWORD.: agrees=True
OWN: I agree with REWORD, and every number reproduces. The proposed l.89 sentence contains one false, garbled clause. It also quietly widens the rule set in advance, and several 'identical' and mechanism words are stronger than the files. Script: scratchpad/refuteB/b2.py. It read only the small group arrays of paper_export.npz through zipfile, not the connectome.

ENGINE CROSS-CHECK: the compare_brian2 kernel totals equal the social_dt0.1 CSV for sugar seeds 0-2 (23,868 / 24,215 / 24,782) and for touch (all head bristles) seeds 0-2 (156,645 / 155,532 / 157,054). They equal the paper file's sugar seeds 0-2 at dt 0.2 (23,059 / 23,614 / 23,795), so the export is the paper model. None of these steps has a .check.txt; the cross-check above plays that role. Nothing looks broken. The Brian2 'w_syn ... 275 uV' namespace warning resolves to the right 0.275 mV.

SUGAR, dt 0.2: 3 of 3 seeds have identical totals, per-neuron 3-seed means are identical (largest difference 0), r = 1.0000, and 0 neurons fire in one engine only. Feed 24.15+-1.55 in both.

SUGAR, dt 0.1:
- 2 of 3 seeds have identical totals (24,215; 24,782). Seed 0: 23,868 against 24,372 (-2.1 %). r = 0.9998; 1 neuron fires in Brian2 only.
- feed 27.13+-1.27 against 27.92+-0.45; passes.
- Brian2 seeds 1-2 match the published-model ref_sugar.npz neuron for neuron (0 neurons differ). Seed 0 differs in 362 neurons (23,512 published against 24,372 paper model).

TOUCH, dt 0.1:
- 2 of 3 seeds have identical totals (155,532; 157,054). Seed 0: 156,645 against 156,491 (+0.10 %). r = 0.9999.
- DNp13 38.0 in all 6 runs; feed 15.96 against 15.88; DNa R 0.83 against 0.67. Every group passes.

cVA (in_orn_cva = 205 neurons, DA1 + DL3; the paper's cVA row is DA1 only, 126 neurons), dt 0.1:
- 0 of 3 seeds identical. Kernel minus Brian2: +1,475, +10,202 and -59 spikes (+2.7 / +23.9 / -0.1 % of Brian2). r = 0.9974. 108 neurons fire in the kernel only, 75 in Brian2 only, 2,186 in both.
- Per-seed Brian2 values from the npz, with kernel values implied by the printed mean+-SD:
  - DNa L: {9, 6, 9} = 8.0+-1.41 against 10.0+-0.71.
  - DNa R: {5, 4.5, 3.5} = 4.33+-0.62 against {6.5, 7, 7} = 6.83+-0.24. The gap of 2.5 Hz is 4.0 x the larger population SD (3.3 x with n-1). FAIL, more than 3 SD. Every other group is within 2 SD, and r >= 0.99.
  - PPL1: {4.69, 2.44, 4.94} = 4.02 against 5.31+-0.14.
- Brian2 recruits 1,831 / 1,755 / 1,936 non-driven neurons, which is the self-sustaining state (the kernel's DA1-only cVA recruits 1,801-1,974 at dt 0.2).

KERNEL SEED SPREAD over 10 seeds:
- CV of total spikes, inputs in the state: 0.9-4.7 % at dt 0.1 and 1.0-17.5 % at dt 0.2 (Or83c). All other inputs: 0.2-2.2 %.
- DNa SD of state inputs at dt 0.1: L 0.74-3.73, R 0.91-2.9 Hz.

WORDING DEFECTS:
(a) 'no more than two runs of either program differ from each other' is ungrammatical and false for the data in hand. The per-seed DNa R sets {6.5, 7, 7} and {3.5, 4.5, 5} do not overlap, and Brian2 seed 1's total (42,700) is below every kernel total (52,902-60,108). 'Within noise' holds only against the 10-seed spread of other smell drives. The 205-neuron drive was never run at 10 seeds in the kernel.
(b) S6's pre-set consequence of an odour or touch group more than 3 SD off is 'limits the Brian2 claim to taste'. Extending it to 'taste and touch' departs from that rule. Touch passes on its own data, but the departure must be declared.
(c) At dt 0.1 'identical' means identical totals only: compare_brian2 does not save kernel per-neuron counts. Per-neuron identity is shown only at dt 0.2 (3-seed means).
(d) 'one diverging spike grows' and 'one does so late' are not measured. The npz holds counts only, and S5 brian2-first-divergence has not run (no results dir). The same applies to the current l.160 'one neuron near its threshold tips the other way', which must go.
(e) At the production dt 0.2 only sugar was compared. cVA and touch were compared at 0.1 only.
(f) Count check: my model gives 7 of 9 taste/touch runs identical. Including cVA and the published-model runs gives 9 of 15, so the current 'most test runs' is true but hides the systematic smell result.
CORRECTED: l.89 (current l.160): 'My version reproduces a Brian2 transcription of Shiu et al.'s code spike for spike when taste or touch drives it, in seven test runs of nine, and the other two end within about 2\,\% of it. Smell is different. It switches on firing that keeps itself going (below), which magnifies small differences. With the male pheromone the two programs part in every run, and Brian2's steering neurons fire 20--37\,\% less. That gap is about as large as the run-to-run spread of smell responses over ten runs of my own program, though larger than the spread of these three runs \note{1}.'

Note 1: 'Against Brian2 2.10.1 \citep{stimberg2019brian}, a transcription of Shiu et al.'s model.py, at 100\,Hz for 1\,s with 3 seeds. Published model, sugar, $dt=0.1$\,ms: identical per-neuron spike counts in two seeds; the third diverges (23{,}689 against 23{,}512 spikes; per-neuron correlation 0.9999). My model: sugar at the production $dt=0.2$\,ms is identical in every neuron in all three seeds. At 0.1\,ms sugar and head bristles give identical spike totals in two seeds, and the third ends 2.1\,\% and 0.1\,\% apart (correlation 0.9998 and 0.9999; DNp13 38.0\,Hz in both). Both cVA receptor types (DA1 and DL3) at 0.1\,ms: no seed is identical, totals end 0.1, 2.7 and 24\,\% apart (correlation 0.9974), DNa L/R are 10.0/6.8 against 8.0/4.3\,Hz and PPL1 5.3 against 4.0\,Hz. cVA switches on the self-sustaining state (Note 5), in which runs differ more: in my program the seed-to-seed spread of total spikes reaches 17.5\,\% for inputs in that state, against at most 2.2\,\% for the others. The DNa R gap is four times its 3-seed spread, so by the rule set in advance the spike-for-spike claim covers taste; touch, tested the same way, passed every comparison. Smell and touch were compared at 0.1\,ms only.'

Notes: keep the verdict's lists. Replace 'one does so late (24 % fewer spikes)' with 'one ends with 24 % fewer spikes, which fits a later switch-on (spike times were not saved)'. Add the per-seed DNa R values {6.5, 7, 7} against {3.5, 4.5, 5}. Add 'the 205-neuron cVA drive has no 10-seed kernel run; the 10-seed spread quoted is from the DA1-only and DL3-only drives (DNa R SD 2.5-2.9 and 1.6-1.9 Hz)'. Drop 'a single neuron near its threshold' everywhere until S5 runs.

### [smell-steering] Note 9 (l.153): 'cVA on one antenna turns the female towards it by 0.6--2.3 Hz, while food odours turn her away.' (l.110 leans on it: 'about the size of the pull his pheromone has on her steering neurons on its own')
STEPS: Loaded experiments/results_edge/odor-dose-10seeds/odor_dose_flywire_shiu_min1+known+eln0.25.csv (1,260 rows = 7 odours x 6 rates x 3 sides x 10 seeds). Copied steer() verbatim from experiments/paper_numbers.py l.315-318 (not imported): per seed, steer = (approach_L + approach_R)/2 on column 'approach (ipsi-contra)', then averaged over seeds. Per-seed values gave a t-based 95 % CI (df 9) and a 20,000-draw bootstrap CI; the two agree. cVA was compared with CO2 per rate (paired by seed, and Welch). Each run was then classed as in or out of the self-sustaining state: non-driven active neurons = active_frac x 139,248 - n_orn, with >= 1,000 counted as in the state. The distribution is bimodal: 1,104 runs are at 1,500-2,200, 150 are below 500 and 6 are in between. Scratch scripts not kept. (steer_ci.csv), state.py, cva.py, misc.py.
CRITERION: S22 (design_plan.md l.247-252): keep 'turns towards' only if the cVA steer (paper_numbers steer()) has a 95 % CI above 0 at 3 or more of the 5 rates (50-150 Hz) AND is larger than CO2's. Otherwise delete the clause.
NUMBERS: Steer, n = 10 seeds, mean +- sd [95 % CI].

cVA:
- 25 Hz: 0.00 +- 0.00. Nothing fires: 0/20 one-sided runs spike beyond the ORNs.
- 50 Hz: +0.68 +- 1.81 [-0.62, 1.97]
- 75 Hz: 0.00 +- 0.98 [-0.70, 0.70]
- 100 Hz: +0.28 +- 1.87 [-1.06, 1.61]
- 125 Hz: +1.58 +- 0.97 [0.89, 2.27]
- 150 Hz: +2.80 +- 1.23 [1.92, 3.68]
The CI is above 0 at 2 of 5 rates (2 of 6 counting 25 Hz).

CO2:
- 50 Hz: +0.23 +- 1.08 [-0.55, 1.00]
- 75 Hz: -0.05 +- 2.78
- 100 Hz: +0.03 +- 2.00
- 125 Hz: -1.00 +- 1.78 [-2.27, 0.27]
- 150 Hz: -2.00 +- 1.45 [-3.04, -0.96]

cVA minus CO2: +0.45, +0.05 and +0.25 Hz at 50/75/100 (p = 0.46 / 0.96 / 0.70). +2.58 [1.31, 3.84] at 125 and +4.80 [3.65, 5.95] at 150. cVA exceeds CO2 at 2 of 5 rates.

The 125/150 Hz values come from the left and right presentations being in different states:
- Left cVA at 100-150 Hz switches on the self-sustaining state in 10/10 runs. There DNa L-R is +0.40, +0.50 and +0.30 Hz (sd 1.9-3.7).
- Right cVA at 100-150 Hz does so in 0/10 runs. It drives only DNa R: 0.15, 2.65 +- 0.41 and 5.30 +- 0.26 Hz, with DNa L = 0.
- So 84 % (125 Hz) and 95 % (150 Hz) of the positive steer comes from the right antenna's out-of-state drive of one neuron.

Where both sides of a seed are in the state, the cVA steer is -0.67 +- 2.02 (50 Hz, n = 3) and -1.25 (75 Hz, n = 2).

Seeds 0-2 reproduce the paper's 3-seed values exactly (0 / +1.67 / +0.58 / -0.17 / +2.33). The paper's '0.6-2.3' drops the 0 at 25 Hz and the -0.17 at 100 Hz.
VERDICT CHANGE
PAPER: Note 9 (l.153), replace 'cVA on one antenna turns the female towards it by 0.6--2.3\,Hz, while food odours turn her away.' with: 'On the bench, food odours on one antenna turn her away (Note~5), and cVA on one antenna does not reliably turn her towards it.' In l.110, delete ', which is about the size of the pull his pheromone has on her steering neurons on its own' (consistent with verify_wording_full.md 22b).
NOTES: cVA on one antenna (female, known signs + eLN x 0.25, gain 1; 1-s runs from rest; 10 seeds). Steer is the mean of the left- and right-antenna presentations' same-side-minus-opposite-side steering-neuron rate. It is 0.0 +- 0.0, +0.7 +- 1.8, 0.0 +- 1.0 and +0.3 +- 1.9 Hz at 25, 50, 75 and 100 Hz; every 95 % CI includes 0, and at 25 Hz nothing fires. At 125 and 150 Hz it is +1.6 +- 1.0 and +2.8 +- 1.2 Hz, but these are not a turn within one state of the brain. On the left antenna, cVA at 100-150 Hz switches on the self-sustaining state (10 of 10 runs; left-right difference +0.3 to +0.5 Hz). On the right antenna it never does (0 of 10) and drives only the right steering neuron, at 2.7 +- 0.4 and 5.3 +- 0.3 Hz. CO2 gives +0.2, -0.1, 0.0, -1.0 and -2.0 Hz at 50-150 Hz. cVA exceeds CO2 only at 125 and 150 Hz (by 2.6 and 4.8 Hz).

### [smell-steering] Note 5 (l.145): 'No sign rule steers towards food (under mine, a 0.7--9 Hz avoidance of the four food odours at five strengths; ...)'
STEPS: Same file and the same copied steer(). Scored the 4 food-type odours (food, vinegar, ester, sweet): per odour and rate, the mean, sd and t-based 95 % CI over 10 seeds, plus the sign of every per-seed steer. Counted cells at the paper's 5 rates (25/50/75/100/150) and at all 6 (with 125). Compared seeds 0-2 with the full 10. Scratch scripts not kept., steer.py.
CRITERION: S22 (design_plan.md l.252): food-type avoidance is kept if the steer is negative in at least 90 % of cells.
NUMBERS: Mean steer is negative in 20/20 cells at the paper's 5 rates and in 24/24 cells at all 6 (100 %): the criterion PASSES. The 95 % CI is below 0 in 17/20 (21/24). The three exceptions are food 25 [-3.75, 0.50], ester 25 [-3.15, 0.80] and ester 100 [-3.73, 0.03]. Per-seed steers: 218/240 negative, 5 zero, 17 positive.

Range of the 10-seed means: -0.85 to -7.15 Hz. The 3-seed paper file gave -0.67 to -9.17. The largest change from 3 to 10 seeds is 3.2 Hz (food 25: -4.83 to -1.62).

Per odour, 25/50/75/100/125/150 Hz, mean +- sd, n = 10:
- food: -1.63 +- 2.98, -3.45 +- 2.12, -4.85 +- 2.29, -5.20 +- 2.08, -6.88 +- 2.40, -7.15 +- 2.63
- vinegar: -0.85 +- 1.17, -2.63 +- 3.10, -4.98 +- 2.33, -4.88 +- 3.15, -5.08 +- 1.71, -1.03 +- 1.23
- ester: -1.18 +- 2.75, -3.03 +- 1.80, -3.25 +- 2.06, -1.85 +- 2.63, -2.53 +- 1.64, -2.65 +- 1.68
- sweet: -1.78 +- 2.12, -2.68 +- 2.47, -3.83 +- 1.59, -2.90 +- 2.32, -4.53 +- 1.95, -5.35 +- 1.94

Pooled over the 4 odours (n = 40 per rate): -1.36 +- 2.30, -2.94 +- 2.35, -4.22 +- 2.13, -3.71 +- 2.84, -4.75 +- 2.44, -4.04 +- 3.04.
VERDICT REWORD
PAPER: Note 5 (l.145): '(under mine, a 1--7\,Hz avoidance of the four food odours at every strength from 25 to 150\,Hz; ...' (rest of the parenthesis as fixed in verify_wording_full.md item 15).
NOTES: Under my signs the four food odours on one antenna turn her away at every strength from 25 to 150 Hz (24 of 24 odour-strength cells, 10 seeds; 95 % CI below 0 in 21):
- food -1.6 to -7.2 Hz;
- vinegar -0.9 to -5.1;
- ester -1.2 to -3.3;
- sweet -1.8 to -5.4.
Per seed the steer is negative in 218 of 240 runs (5 zero, 17 positive), with a seed-to-seed sd of 1.2-3.1 Hz. The first three seeds alone gave -0.7 to -9.2.

### [smell-steering] Are these steering numbers read in the self-sustaining state (analysis_A persistence: DNa L/R ~16/18, PPL1 ~9, GF ~3 Hz, switched on within 0.1-0.3 s), and do left-right differences survive on top of it? (S22 + analysis_A knock-on (a))
STEPS: Classed every run by state (see claim 1). Compared the bilateral rows' DNa L/R, PPL1 and GF with the state signature from analysis_A: after offset, n = 8, DNa L 15.96 +- 1.72, R 17.97 +- 1.41, PPL1 8.72, GF 3.08. Also compared them with an in-file 1-s reference: CO2 on both antennae at 75-150 Hz plus aversive at 50-150 Hz. Computed the mean DNa level (L+R)/2 and |L-R| in in-state runs. Split each side's approach against the state's own asymmetry (L-R = -2.0). Tested the food-type steer against CO2 and aversive at the same rate (Welch, 75-150 Hz, where those are 10/10 in the state). Scratch scripts not kept., sum.py, sides.py.
CRITERION: No pre-set pass rule. The question comes from the task and analysis_A knock-on (a): odour-specific claims must be read against the state's odour-independent signature. Operational test: (i) share of runs in the state; (ii) whether the bilateral DNa sit at the state level; (iii) whether food-type L-R differences exceed the state's own and those of in-state control odours.
NUMBERS: (i) Share of runs in the state:
- 1,108/1,260 runs overall.
- All 720/720 food-type runs, at every rate and side.
- CO2 137/180: 0/30 at 25 Hz; 50 Hz L 1/10, R 7/10, both 9/10; 10/10 at 75 Hz and above.
- Aversive 144/180.
- cVA 107/180: one-sided 25 Hz 0/20; L/R 3/9 at 50, 7/4 at 75, 10/0 at 100-150; both 10/10 up to 100, 9/10 at 125, 5/10 at 150.

(ii) Bilateral DNa against the state:
- The 1-s in-state reference (CO2 both 75-150, aversive both 50-150; n = 90 runs): DNa L 15.3 +- 2.6, R 16.6 +- 2.6, PPL1 8.5 +- 0.8, GF 2.6 +- 2.0. This is the state signature.
- 25 of 42 bilateral rows have mean DNa within 3 Hz of 17 Hz.
- Bilateral food at 25/50 Hz: 14.6/16.6 and 18.2/18.6, which is the state level.
- Food and vinegar at 100-150 Hz keep the mean at 18.0-21.1 Hz but split it L-R by +7.4 to +28.0 Hz (food 150: 30.1/6.0; vinegar 150: 33.0/5.0). PPL1 rises to 15-22 Hz.
- Bilateral cVA sits below the state: DNa 8.6-11.1 / 2.2-13.3, PPL1 1.5-6.9.

(iii) Left-right differences on top of the state:
- steer() cancels the state's fixed L-R of about -2 Hz. Food-type steer is negative in 24/24 cells.
- It exceeds CO2's same-rate steer in 11/16 cells at 75-150 Hz (p < 0.05; food -4.8 to -5.9, sweet -2.9 to -3.8, vinegar -4.1 to -4.9 up to 125 Hz) and aversive's in 10/16.
- The in-state DNa level (L+R)/2 of food-type runs is 10.6-21.2 Hz per cell (food 15.2-19.2, vinegar 14.0-21.1, ester 10.6-15.9, sweet 11.8-21.2).
- Mean |L-R| in-state: 5.8 Hz for food-type odours against 2.7 Hz for CO2, aversive and cVA.
- Against the state's own asymmetry, the left-antenna presentation turns away in 22/24 cells, the right-antenna presentation in 19/24, and both in 17/24.
- At 100-150 Hz the right antenna carries 68-100 % of food and vinegar avoidance.
- Vinegar at 150 Hz on the left turns her towards it (L-R +4.9 against the state's -2.0).
- The in-state control odours themselves steer slightly away at high rates: CO2 -2.0 at 150; aversive -1.1 to -1.5 at 50-150.
VERDICT REWORD
PAPER: Note 5, after the food-avoidance clause, add: 'These are read in the self-sustaining state, which every food-odour run switched on: the odour leaves the two steering neurons' mean rate near the state's 17\,Hz and shifts it away from its own side.' Knock-on (not re-scored here): the bilateral food DNa of Note 4 / paper_numbers ('16 / 18; 21 / 21' at 25 / 75 Hz) are the state's level, not a dose response.
NOTES: Every food-odour run (720 of 720) and every CO2 or aversive run at 75 Hz and above is in the self-sustaining state. There, the steering neurons' mean rate stays at the state's level: 15-19 Hz for food and vinegar, 11-16 for ester, 12-21 for sweet, against 15.3/16.6 Hz for CO2 and the aversive odour on both antennae. The odour moves rate from one side to the other, by 5.8 Hz on average against 2.7 Hz for CO2, aversive and cVA. Food-odour steering is larger than CO2's at the same strength in 11 of 16 cases at 75-150 Hz. It is not symmetric: at 100-150 Hz most of the avoidance comes from the right antenna. With the odour on both antennae, food and vinegar at 100-150 Hz turn her left by 7-28 Hz. cVA is not read in one state, because its left and right presentations switch the state on at different rates (see cVA above).

RUN PROBLEMS [smell-steering]: No sign that the run is broken.

No .check.txt exists for this step. It ran through run_redirect without --check-against, so I did the digit check by hand:
- All 315 rows of experiments/results/odor_dose_flywire_shiu_min1+known+eln0.25.csv (seeds 0-2 x 7 odours x 25/50/75/100/150 Hz x L/R/both) are present in the edge file.
- All 19 value columns are equal, with max |diff| = 0. Only wall_s differs, and hz is written 25.0 instead of 25.

Run details:
- Sidecar _redirect_odor_dose_20260927_054220.json: status ok, sim {} (script defaults), FLYBRAIN_SIGNS=known, FLYBRAIN_ELN=0.25, NUMBA_NUM_THREADS 6, 6 chunks, 658.5 s.
- 1,260 rows, 10 per cell, no NaN.
- Log logs/edge/guarded_odor-dose-10seeds.out: 133 lines, no errors or retries.

One deviation, harmless: design_plan S22 lists rates 50-150, but the step file (steps_20260927.tsv l.29) ran 25-150. That is a superset, and 25 Hz is covered by the digit check as well.

Caveats on reading the file, not bugs:
(1) The one-sided 25 Hz rows for cVA, CO2 and aversive are exactly 0 because nothing fires (brain 0.1 %). Their steer of 0 means 'no response', not 'balanced'.
(2) steer() assumes the odour's effect is equal and opposite on the two sides. At 100-150 Hz, food and vinegar on both antennae drive L-R to +7 to +28 Hz. The 'fixed bias' is therefore partly odour-driven, and the steer/bias split is only approximate there.
(3) analysis_A knock-on (a) is confirmed. The steering neurons' levels in all odour rows (and PPL1 near 8-9, GF near 3) are mostly the self-sustaining state. Only the left-right split and the food and vinegar PPL1 rise (15-22 Hz) carry odour-specific information.

Scratch outputs are in (scratch, not kept) check.py, steer.py, steer_ci.csv, state.py, edge_annot.csv, cva.py, food.py, sides.py, bilat.py, sum.py, misc.py.

>>> CHECK [smell-steering] Claim 1. Note 9 (draft 5 l.153): 'cVA on one antenna turns the female towards it by 0.6--2.3 Hz' and l.110 'about the size of the pull his pheromone has...'. Analyst verdict: CHANGE (delete, replace with 'does not reliably turn her towards it').: agrees=True
OWN: My own scripts: (scratch, not kept) (repro.py, steer1.py, cva2.py, cva3.py, cva4.py, state.py, state2.py). I did not reuse the analyst's dose22 scripts.

File and engine check:
- File: experiments/results_edge/odor-dose-10seeds/odor_dose_flywire_shiu_min1+known+eln0.25.csv. 1,260 rows = 7 odours x 6 rates x 3 sides x 10 seeds, with no duplicates and no NaN.
- Sidecar: FLYBRAIN_SIGNS=known, ELN 0.25, 6 threads/6 chunks, gain 1 (default), 1000 ms.
- There is no .check.txt, because S22 had no --check-against. I checked it by hand: seeds 0-2 equal experiments/results/odor_dose_flywire_shiu_min1+known+eln0.25.csv in all 315 rows (all 5 paper rates including 25 Hz) and all 22 numeric columns, max |diff| 0. That file in turn equals release/pre_rerun_20260926/results/ (0 diff).
- 'approach (ipsi-contra)' = DNa L-R for L runs and R-L for R runs (exact).
- The run is not broken.

Steer (paper_numbers steer(), 10 seeds, mean +- sd [t 95 % CI]):
- cVA: 25 Hz 0.00 +- 0.00; 50 Hz +0.68 +- 1.81 [-0.62, 1.97]; 75 Hz 0.00 +- 0.98 [-0.70, 0.70]; 100 Hz +0.28 +- 1.87 [-1.06, 1.61]; 125 Hz +1.58 +- 0.97 [0.88, 2.27]; 150 Hz +2.80 +- 1.23 [1.92, 3.68].
- Per-seed signs (+/-/0) at 50-100 Hz: 6/3/1, 6/4/0, 6/4/0. No test would rescue those rates.
- CO2: +0.22, -0.05, +0.02, -1.00, -2.00 at 50-150 Hz.
- cVA minus CO2, paired: +0.45 (p 0.46), +0.05 (0.96), +0.25 (0.70), +2.58 [1.31, 3.84] (p 0.001), +4.80 [3.65, 5.95].
- S22 criterion (CI > 0 at 3 or more of 5 rates AND larger than CO2): FAILS, at 2 of 5. The pre-set consequence is to delete the clause.

Side by side:
- R cVA at 100/125/150 Hz: DNa L 0, DNa R 0.15 / 2.65 +- 0.41 / 5.30 +- 0.26; 0/10 in the state.
- L cVA at 100/125/150 Hz: 10/10 in the state, L-R +0.40 +- 3.67 / +0.50 +- 1.89 / +0.30 +- 2.37.
- Right share of the steer: 84 % at 125 Hz, 95 % at 150 Hz.
- Seeds with both sides in the state: -0.67 +- 2.02 at 50 Hz (n = 3), -1.25 at 75 Hz (n = 2).
- Seeds 0-2 give 0 / +1.67 / +0.58 / -0.17 / +2.33, which is the paper's range.

New evidence that makes the case stronger:
- Inside the state, the left antenna adds no lateral shift. At 100 Hz, left-only cVA L-R +0.40 equals bilateral cVA +0.45 (Welch p = 0.97; both 10/10 in the state).
- At 125 Hz, bilateral in-state cVA gives L-R +3.39 (n = 9) against left-only +0.50 (p = 0.012). So inside the state, adding the right antenna LOWERS DNa R, which is a turn away. That is the opposite sign to the right antenna's out-of-state response.

Caveats:
- The 'in state' rule (active x 139,248 - n_orn >= 1,000; N confirmed exactly) counts 13 late-ignition runs as in the state: PPL1 < 2 Hz, 6.8k-42k spikes.
- With PPL1 >= 2 Hz as the rule instead, one-sided cVA L/R is 3/7 at 50 Hz and 7/3 at 75 Hz. The 100-150 Hz split (10/0) does not change.

Which draft the line numbers refer to:
- l.110/l.145/l.153 are the lines of paper/archive/flycraft_draft5_20260926.tex.
- The working paper/flycraft.tex (27 Sep 06:31) has already dropped the 'size of the pull' sentence (now l.251, '15 lean towards him and 20 away').
- Its Notes 1-11 are %%PENDING.
- So the l.110 deletion is already done, and the Note 9 text has to be written into the new Note 9.
CORRECTED: The verdict CHANGE stands.

Paper, new Note 9 (the l.110 deletion is already in the working draft): 'On the bench, food odours on one antenna turn her away (Note~5). cVA on one antenna does not reliably turn her towards it: only on her right antenna, and only at the two highest strengths, does it drive the steering neuron on its own side.' The shorter form, '...does not reliably turn her towards it.', is also correct.

Notes: the analyst's text is accurate. Add one sentence: 'Within the self-sustaining state the left antenna adds no turn (at 100 Hz, L-R +0.4 against +0.5 with cVA on both antennae), and at 125 Hz adding the right antenna turns her away from it (L-R +3.4 against +0.5).'

>>> CHECK [smell-steering] Claim 2. Note 5 (draft 5 l.145): 'under mine, a 0.7--9 Hz avoidance of the four food odours at five strengths'. Analyst verdict: REWORD to '1--7 Hz ... at every strength from 25 to 150 Hz'.: agrees=True
OWN: Same file and the same copied steer(). Script not kept.

Pre-set criterion (S22: negative in at least 90 % of cells):
- The mean steer is negative in 20/20 cells at the paper's 5 rates and in 24/24 at all 6 rates. PASS.
- The 95 % CI is below 0 in 17/20 (21/24).
- The exceptions are food 25 [-3.75, 0.50], ester 25 [-3.15, 0.80] and ester 100 [-3.73, 0.03].
- Vinegar 25 is only just below 0 (upper limit -0.01).
- Per-seed steers: 218 negative, 5 zero, 17 positive out of 240 (odour x rate x seed). Each value is the mean of one L and one R run, so these are not 240 'runs'.

10-seed means, 25/50/75/100/125/150 Hz:
- food: -1.62, -3.45, -4.85, -5.20, -6.88, -7.15
- vinegar: -0.85, -2.62, -4.97, -4.88, -5.08, -1.02
- ester: -1.18, -3.02, -3.25, -1.85, -2.52, -2.65
- sweet: -1.78, -2.68, -3.82, -2.90, -4.53, -5.35
- The analyst's second decimals differ only by round-half-even (e.g. -1.625).
- Range -0.85 to -7.15; sd 1.17-3.15.
- Pooled over the 4 odours (n = 40 per rate): -1.36 +- 2.30, -2.94 +- 2.35, -4.22 +- 2.13, -3.71 +- 2.84, -4.75 +- 2.44, -4.04 +- 3.04.

Comparison with 3 seeds:
- The 3-seed range is -0.67 to -9.17, which reproduces verify_wording item 15.
- The largest change from 3 to 10 seeds is food 25: -4.83 to -1.63.

All 720 food-type runs are in the self-sustaining state on both sides, so steer() validly cancels the state's fixed L-R. The criterion is therefore not affected by the state issue. Which antenna carries the avoidance differs by odour (see claim 3).
CORRECTED: The verdict REWORD stands and the paper wording is right: '(under mine, a 1--7\,Hz avoidance of the four food odours at every strength from 25 to 150\,Hz; ...'.

One fix in the Notes: 'Per seed the steer is negative in 218 of 240 runs' should become 'Per seed (each value the mean of a left- and a right-antenna run) the steer is negative in 218 of 240 odour-strength-seed values (5 zero, 17 positive).'

Optional addition: 'The 95 % CI crosses 0 in 3 cells (food and ester at 25 Hz, ester at 100 Hz).'

>>> CHECK [smell-steering] Claim 3. Are the steering numbers read in the self-sustaining state, and do L-R differences survive on top of it? Analyst verdict: REWORD, with a new Note 5 sentence and Notes text.: agrees=False
OWN: The verdict (REWORD) is right, but the proposed wording has several errors. Scripts not kept., state2.py, bilat.py, sides.py, sides2.py, b17.py.

(i) Share of runs in the state. The counts reproduce:
- 1,108/1,260 overall; food-type 720/720.
- CO2 137, aversive 144, cVA 107.
- Distribution of non-driven active neurons: 150 below 500, 6 in between, 1,104 at 1,500-2,250.
- The analyst's claim that 'every CO2 or aversive run at 75 Hz and above' is in the state is FALSE for aversive: right antenna at 75 Hz is 6/10. The step text '75-150 Hz, where those are 10/10' is wrong for the same reason.
- The >= 1,000 rule also counts 13 late-ignition runs (PPL1 < 2 Hz, 6.8k-42k spikes). With PPL1 >= 2 Hz, bilateral cVA at 150 Hz is 3/10, not 5/10.

(ii) Bilateral rows against the state:
- The 1-s in-state reference reproduces: n = 90, DNa L 15.28 +- 2.63, R 16.64 +- 2.64 (mean 16.0), PPL1 8.50 +- 0.79, GF 2.58 +- 1.99, L-R -1.36 +- 3.63.
- '25 of 42' bilateral cells within 3 Hz of 17 is 24 (26 if two cells at 3.025 are counted).
- Bilateral food/vinegar at 100-150 Hz: L-R +7.4 to +28.0, PPL1 15-22. Bilateral cVA: DNa L 8.6-11.1, R 2.2-13.3, PPL1 1.5-6.9. Both confirmed.

(iii) Left-right differences on top of the state:
- Food-type steer is more negative than CO2's in 12/16 cells at 75-150 Hz (Welch p < 0.05; paired 12; Mann-Whitney 13), not 11. The analyst left out ester 75 (-3.20, p = 0.010).
- Against aversive it is 11/16, not 10 (ester 75: -2.02, p = 0.014).
- Mean |L-R| of 5.8 vs 2.7 Hz includes the bilateral runs. For one-sided runs only it is 5.2 vs 2.4 (at 75 Hz and above, 5.6 vs 2.4).
- In-state DNa level per cell (all sides): food 15.2-19.2, vinegar 14.0-21.1, ester 10.6-15.9, sweet 11.8-21.2. One-sided only: food 15.2-17.3, vinegar 14.8-19.2, ester 11.2-15.6, sweet 12.6-15.5. The Notes' '15-19 Hz for food and vinegar' is wrong for vinegar.

Per-antenna 'away' counts (22/19/17 of 24):
- These counts need a = -2.01 exactly. At a = -1.99 they are 22/18/16; with the in-file 1-s reference (a = -1.36), 23/15/14.
- Vinegar 25 R (L-R -2.00) counts as 'away' by 0.01 Hz, and 3 sweet R cells by 0.21-0.26 Hz.

Which antenna carries the avoidance depends on the odour:
- Food: the right antenna carries it at 100-150 Hz, 78-101 % for any a from -2 to 0. Left food L-R is -2.3/-2.8/-1.8, i.e. about the state's own value.
- Vinegar at 100-125 Hz: 68-80 % from the right at a = -2, but only 47-60 % at a = 0.
- Vinegar at 150 Hz, left antenna: L-R +4.9 +- 3.0, a turn towards it.
- Ester and sweet: the LEFT antenna carries it. Ester L-R on the left is -3.6 to -8.1, on the right -1.25 to -2.75 (about the state value). Sweet on the left -5.3 to -9.4, on the right about -2 up to 100 Hz.
- So the Notes' 'at 100-150 Hz most of the avoidance comes from the right antenna' is wrong for ester and sweet. The paper's 'shifts it away from its own side' holds only on average over the two antennae.

New knock-on, contradicting the brief's 'any smell at 90-100 Hz switches the state on':
- Right-antenna cVA at 100-150 Hz: 0/10 within 1 s.
- Bilateral cVA at 150 Hz: 5/10 (3/10 with the PPL1 rule).
- One-sided CO2, aversive and cVA at 25 Hz: 0/60.
- Strong cVA holds the brain below the state level: DNa mean 6.7-11.9, PPL1 1.5-6.9. The state's DNa level during drive therefore depends on the odour.

Knock-on attribution: draft 5 Note 4 contains no '16 / 18; 21 / 21'. That string is only in paper_numbers.py's bilateral-food check. Note 4's freeze baseline ('20 / 12 Hz by a food odour', gain sweep, 0.6 s) is the paper number to reread against the state.
CORRECTED: Paper, Note 5, after the food clause: 'These are read in the self-sustaining state, which every food-odour run switched on: the odour leaves the steering neurons' combined rate near the state's level of about 16\,Hz and, averaged over the two antennae, moves it away from the odour's side (for food and vinegar mostly through the right antenna, for ester and sweet through the left).' Fix the knock-on target: paper_numbers' bilateral-food check and the Note 4 freeze baseline, not a Note 4 sentence.

Notes text:

State coverage. Every food-odour run (720 of 720), every CO2 run at 75 Hz and above, and every aversive run at 100 Hz and above is in the self-sustaining state. The aversive odour on the right antenna at 75 Hz is in it in 6 of 10 runs.

What the state leaves unchanged. There, the steering neurons' combined rate stays near the state's level:
- 15-19 Hz for food, 14-21 for vinegar, 11-16 for ester and 12-21 for sweet;
- against 15.3/16.6 Hz for CO2 and the aversive odour on both antennae.

What the odour moves. The odour moves rate from one side to the other: mean |L-R| is 5.2 Hz against 2.4 for CO2, aversive and cVA on one antenna (5.8 against 2.7 counting both-antennae runs). Food-odour steering is larger than CO2's at the same strength in 12 of 16 cases at 75-150 Hz, and larger than the aversive odour's in 11.

Which antenna. It is not symmetric:
- At 100-150 Hz nearly all of the food avoidance and most of the vinegar avoidance comes from the right antenna.
- For ester and sweet most comes from the left.
- Vinegar at 150 Hz on the left antenna turns her towards it.
- With the odour on both antennae, food and vinegar at 100-150 Hz turn her left by 7-28 Hz.

cVA is not read in one state:
- On the left antenna it switches the state on at 100-150 Hz.
- On the right it never does within 1 s.
- On both antennae at 150 Hz it does so in only half the runs.

### [learning] Note 7 and l.99: the memory is associative. It forms only when the teaching signal comes with the odour ('when a dopamine teaching neuron fires at the same time'; '0.04 without a teaching signal').
STEPS: Step cond-contingency (experiments/results_edge/cond-contingency/, seed 0, 3 cycles, reward DANs at 50 Hz). The forward run (vinegar+/ester-) was checked against the paper file. Backward, unpaired and US-only were run in both odour orders. Learning index = post/pre of row 'drive reward-comp' for CS- minus the same for CS+, from the main CSV columns pre_CS+/pre_CS-/post_CS+/post_CS-, as in paper_numbers.py l.358-362. The _compartments.csv files hold mean w/w0 per MBON type; paper_numbers skips them. The control is the paper's no-teaching run in the same order and seed: experiments/results/conditioning_flywire_shiu_min1+known+eln0.25_us-wiring_{vinegar-vs-ester,ester-vs-vinegar}_seed0.csv. Per-phase DAN and KC rates come from the JSON sidecars ('phase_stats'). Scratch scripts not kept. (table li_all.csv) and dn.py.
CRITERION: S24: keep 'associative' only if (a) backward and unpaired are each within 0.1 of the no-teaching control in both orders, and (b) US-only leaves both odours' taught-compartment drive at 0.85 or more. Otherwise, 'part of the index comes from the US itself'.
NUMBERS: Forward, vinegar paired, seed 0: index +0.498 (CS+ 0.095, CS- 0.593). It is byte-identical to the paper file.

No-teaching control, seed 0: +0.024 (vinegar first) and -0.014 (ester first). The paper's pooled value is +0.033 +- 0.035 (n = 4, np.std).

(a) Backward: +0.031 (vinegar paired; CS+ 0.837, CS- 0.868) and -0.078 (ester paired; 0.875 / 0.798). Unpaired: +0.053 (0.826 / 0.879) and -0.022 (0.871 / 0.848). Distances from the matched control are 0.007, 0.064, 0.029 and 0.008, all below 0.1, so (a) PASSES. Backward and unpaired pooled: -0.004 +- 0.059 (n = 4, ddof 1).

(b) US-only:
- Vinegar-first order: vinegar (never presented) 0.927, ester 0.926.
- Ester-first order: ester (never presented) 0.948, vinegar 0.845.
- One cell of four is 0.005 below 0.85, so (b) FAILS narrowly. Mean 0.911 +- 0.045 (n = 4).
- The US-only index is -0.001 and -0.103. The teaching signal alone produces no positive index; it lowers every odour's drive by 5-15 %, against 2-13 % with no teaching signal (0.867-0.977).

Why the US alone costs something: training never returns to rest. All 156 rest phases in the 21 edge runs sit in the self-sustained state of analysis_A: PPL1 8.58 +- 0.28 Hz, KC 0.136 +- 0.005 Hz, all DANs 1.81 Hz. During 'US alone', KCs fire at 0.083-0.146 Hz, so the rule pairs the US with the state's background KCs.
VERDICT REWORD
PAPER: Main text unchanged. Note 7, after '0.03 without a teaching signal' (the value corrected in verify_wording 18a):

'The pairing is what counts: with the teaching signal given just before the paired odour, or 5 s after it ends, the index is -0.08 to +0.05 (one seed per odour order), as without one. The teaching signal alone lowers every odour's drive by 5-15 %.'
NOTES: Contingency controls (seed 0, 3 cycles, reward DANs 50 Hz, both odour orders): forward +0.50; backward +0.03 / -0.08; unpaired +0.05 / -0.02; no teaching signal +0.02 / -0.01. Pooled backward and unpaired -0.004 +- 0.059 (n = 4). Teaching signal alone: index -0.00 / -0.10, retained drive 0.845-0.948 (0.91 +- 0.05, n = 4). The pre-set US-only bound (>= 0.85) is missed by 0.005 in one cell (vinegar, 0.845). The US-alone loss comes from Kenyon cells that keep firing at about 0.1 Hz between presentations, because the brain stays in its self-sustained state throughout training.

### [learning] Note 7: '0.21 +- 0.14 for punishment'. Set beside the reward compartment's '0.04 without a teaching signal', it reads as associative punishment learning.
STEPS: From cond-contingency, backward pairing with the punishment (PPL1) set in both orders, compared with the no-teaching control read in the punishment compartment: 'drive punish-comp', post/pre, CS- minus CS+, from the paper's us-wiring files. This is the same computation as verify_wording 18c, extended with the backward runs.
CRITERION: S24 applied to punishment: backward within 0.1 of the no-teaching control in both orders.
NUMBERS: Backward punishment:
- Ester paired: -0.258 (ester 0.472, vinegar 0.213).
- Vinegar paired: +0.248 (vinegar 0.228, ester 0.476).

No-teaching control in the punishment compartment:
- Ester first: -0.236 (seed 0).
- Vinegar first: +0.256 (seed 0); +0.280 +- 0.035 over seeds 0-2.

Distances are 0.022 and 0.008, so backward matches control and the criterion PASSES.

The control itself is +-0.25 depending on odour order. With no teaching signal, vinegar keeps only 0.21-0.23 of its punishment-compartment drive and ester 0.46-0.48. The phase stats show why: vinegar drives the punishment compartments' DANs at 6.6-7.3 Hz (synapse-weighted) against 0.5 Hz for ester, and every rest adds 0.70 Hz from the self-sustained state.

Forward punishment (paper files): 0.077 +- 0.003 with ester paired and 0.348 +- 0.043 with vinegar paired (n = 3 each). The increments over the same-order control are +0.31 and +0.07. The pooled 0.21 +- 0.14 (n = 6, np.std) averages these.
VERDICT REWORD
PAPER: Note 7, replace '$0.21 \pm 0.14$ for punishment' with:

'for punishment 0.35 with vinegar paired and 0.08 with ester paired, only 0.07 and 0.31 above the same compartment without a teaching signal (+0.28 and -0.24, because vinegar lowers its own input there); backward pairing gives the no-teaching values (+0.25, -0.26)'

This agrees with verify_wording 18c.
NOTES: Punishment compartment: paired 0.35 +- 0.04 (vinegar) and 0.08 +- 0.003 (ester), n = 3 each. No teaching signal: +0.28 +- 0.04 (n = 3) and -0.24 (n = 1). Backward: +0.25 and -0.26 (n = 1 each).

### [learning] The memory is odour-specific across pairs. The paper reports one pair: '0.54 +- 0.02' and 'the other smell kept about three-fifths of its strength'. Does it hold when the odours share glomeruli (sweet vs ester)?
STEPS: Steps cond-pair-sweet-ester and cond-pair-floral-vinegar (experiments/results_edge/cond-pairs/): reward DANs and no-teaching (us-wiring), both orders, seed 0, 3 cycles, same index as above. Glomerular overlap is from brain/flybrain/senses.py ODOR_LIBRARY. Pre-test values were compared across every run that uses the same odour (68 comparisons).
CRITERION: S25: if the index is at least 0.3 in both orders and the no-teaching control is at most 0.1, report the index as a range over pairs. If it falls below 0.2, say specificity depends on how many Kenyon cells the two odours share. P2 cond-extra adds: index at least 0.3 for a pair with zero overlap.
NUMBERS: Glomeruli shared, of 6 each: sweet/ester 4 (DM2, DM4, VM2, VA2); vinegar/ester 2; floral/vinegar 0.

Sweet and ester:
- Ester paired: 0.429 (ester 0.097, sweet 0.526).
- Sweet paired: 0.147 (sweet 0.103, ester 0.250).
- Controls: -0.025 and +0.004.
- 0.147 is below 0.2, so the S25 second branch is triggered.

Floral and vinegar:
- Floral paired: 0.722 (0.120 / 0.841). Vinegar paired: 0.628 (0.101 / 0.729).
- Controls: -0.043 and +0.097. PASS.

Vinegar and ester (paper, 3 seeds per order): 0.527 +- 0.025 (vinegar paired) and 0.569 +- 0.028 (ester paired).

Mean over orders by pair: 0.68 (0 shared), 0.55 (2 shared), 0.29 (4 shared). The other odour keeps 0.73-0.84, 0.59-0.70 and 0.25-0.53 respectively.

The paired odour always sits at the 0.10 floor (0.095-0.120). All six no-teaching runs (pairs plus long training) give +0.009 +- 0.053 (n = 6), range -0.043 to +0.097.

The asymmetry (sweet paired leaves ester 0.25; ester paired leaves sweet 0.53) fits ester's code lying largely inside sweet's: sweet drives 6.0 % of KCs, ester 3.6 %. KC-level overlap was not measured in these runs.

Seed noise of the index is about 0.03 (n = 3), so the 0.15-0.72 spread is real. Each pair is n = 1 per order.
VERDICT REWORD
PAPER: l.99: '...reached the output neurons at a tenth of its old strength, while the other smell kept about three-fifths of its strength (between a quarter and four-fifths over the three pairs of smells I tried: the more smell receptors two smells share, the less the other one keeps), ...'

Note 7, add: 'Over three pairs of smells (one seed per order) the index is 0.72 and 0.63 for floral and vinegar, which share no glomerulus, 0.60 and 0.50 for ester and vinegar (two of six shared) and 0.43 and 0.15 for ester and sweet (four of six; pairing sweet leaves ester 0.25 of its drive). The paired smell always falls to 0.10-0.12, and without a teaching signal every pair stays between -0.04 and +0.10.'
NOTES: Index by pair (n = 1 per order unless noted): floral/vinegar 0.72 / 0.63; ester/vinegar 0.55 +- 0.03 (n = 6); sweet/ester 0.43 / 0.15. No teaching signal: -0.04 to +0.10 (0.01 +- 0.05, n = 6). The paired odour keeps 0.095-0.120; the other keeps 0.25-0.84.

### [learning] The memory holds with longer training: specificity does not erode (the CS- is not eaten away) at 6 cycles, and no expression appears.
STEPS: Step cond-long-training (experiments/results_edge/cond-long/): 6 cycles, reward DANs and no-teaching, both orders, seed 0. DN change = (post - pre) of the CS+ in the reward run minus the same in the matched no-teaching run, for rows DNa L, DNa R, DNp09, MDN, DN all, feed MNs (bilateral test) and 'approach' (left-antenna test). The 3-cycle paper files, seeds 0-2, give the spread of the same quantity.
CRITERION: S23, cut to 6 cycles by DECISIONS 10. Keep if the index is at least 0.3 in both orders, at least 0.2 above the matched no-teaching run, and the CS+-specific DN change over that control stays below 2 Hz. Otherwise, say specificity holds only for short training.
NUMBERS: Index at 6 cycles:
- Vinegar paired: 0.467 (CS+ 0.104, CS- 0.570).
- Ester paired: 0.528 (0.095 / 0.622).
- Controls: +0.044 and -0.026.
- Margins over control 0.42 and 0.55. PASS.
- Compared with 3 cycles, seed 0 (0.498 / 0.600), the other odour erodes only slightly: ester 0.593 to 0.570, vinegar 0.697 to 0.622.

DN criterion:
- Bilateral readouts: dDNa L -1.5, dDNa R -1.5, DN all -0.06 Hz; DNp09, MDN and feed MNs 0.
- With ester paired, all 16 saved spike readouts of the post-test are identical to the no-teaching run. The reward output neurons fire 0.00 Hz to ester, so depressing its input changes no spike.
- The lateral approach index fails the bound: -5.5 Hz with vinegar paired.
- The bound sits below single-run noise. At 3 cycles the same quantity is dDNa L -8.0 / +0.5 / -2.5 and approach -3.0 / -3.5 / -1.5 (seeds 0-2). In expression_harsh, silencing a whole output set moves the approach index by -5.5 to +6.5 Hz per seed.
- Vinegar's approach change is negative in 4 of 4 comparisons (sign test p = 0.125), which would be away from the rewarded odour. It is not significant.
VERDICT KEEP
PAPER: Unchanged. Optional clause in Note 7: 'six pairings instead of three give 0.47 and 0.53, the other odour keeping 0.57-0.62.'
NOTES: 6 cycles (n = 1 per order): index 0.47 / 0.53, no teaching signal +0.04 / -0.03, CS+ 0.10 / 0.09, CS- 0.57 / 0.62. Bilateral DN change over control is at most 1.5 Hz. The lateral approach index moves -5.5 Hz, within the per-seed range (-8 to +6.5 Hz) of any small weight change.

### [learning] l.99: 'The output neurons that hold the memory have no working route to the neurons that move the fly, so the memory is written in a notebook that nobody downstream reads.'
STEPS: Step expression-harsh, file experiments/results_edge/expression-harsh/expression_harsh_flywire_shiu_min1+known+eln0.25{.csv,_dn_types.csv,_structure.csv}. Vinegar at 150 Hz, 3 seeds, 1 s, paper model (known signs, eLN x0.25). Checked to the digit against experiments/results/expression_probe_flywire_shiu_min1+known+eln0.25.csv.

Modes: MBON sets driven at 0/20/50/100 Hz ('drive'); single types at 50 Hz ('types'); lateral-horn bypass, with ALPN synapses onto anything but KCs, AL neurons and ORNs cut (123,833 connections) and MBONs intact, silenced or driven; tonic kicks on non-DN targets with MBONs intact or silenced ('kick-nodn'); and structure.

Columns used: DNa L, DNa R, DN all, set MBONs Hz, non-DN targets Hz, target DNs Hz, PPL1 (punish DA), total_spikes, active_frac. Per DN type from the _dn_types.csv file (pivot sim_id x dn_type, seed means, count of types with |diff| > 5 Hz). Scratch scripts: edgeB/expr.py, dntypes.py, dn2.py.
CRITERION: S26: 'No working route' stands only if all three hold. (1) The punishment set at 100 Hz moves fewer than 3 DN types by more than 5 Hz, and DNa, MDN, DNp09 and GF by less than 5 Hz. (2) Under the lateral-horn bypass, odour activity reaching DNs through the MB is below 2 Hz and does not change when the MBONs are silenced. (3) The reward set at 20-100 Hz reaches no DN. Otherwise the text becomes 'a working route that the memory is too weak to use'.
NUMBERS: (1) FAILS. Punishment set, no odour, 20 / 50 / 100 Hz:
- DN types moved by more than 5 Hz: 24 / 25 / 27, all from 0.
- 100 Hz: DNge053 43, DNbe007 41, DNg13 39, DNb05 32, DNg100 27, DNa02 14, DNa01 8.7 Hz.
- DNa L 19.2+-2.1 / 23.3+-1.8 / 22.2+-2.6 Hz; DNa R 4.2 / 3.2 / 0.5 (intact 0/0). GF, MDN and DNp09 stay 0.
- MBON14 alone at 50 Hz: DNa L 18.0+-2.3 (16.0/20.5/17.5), R 4.0+-1.0, 20 DN types. With odour, the 100-Hz set moves 14 types (odour L) and 9 (both).

(2) FAILS. Bypass with odour L:
- Intact: DNa L 10.0+-6.6 (5.0/7.5/17.5), R 1.8, DN all 0.22, target DNs 1.8.
- Punishment set silenced: all 0.00. Reward set silenced: DNa L 25.5+-2.5, R 6.7.
- Under the bypass the smell reaches the DNs only through the output neurons.

(3) FAILS under odour. The reward set at 20-100 Hz with no odour drives nothing: only the 12 MBONs spike. During odour L it moves 2 / 15 / 20 DN types by more than 5 Hz, all decreases, at 20 / 50 / 100 Hz. DNa L goes 19.8 to 13.0 / 2.5 / 0.0; DNge053 36 to 1.7 at 100 Hz. It also switches off PPL1 (11.9 to 8.4 / 2.7 / 0.2 Hz).

Why the memory cannot use the route:
- A smell drives the output neurons weakly: reward set 0.5+-0.1 (L) and 6.2+-0.6 (both) Hz, punishment set 5.3 and 11.7 Hz.
- Silencing either whole set, the most a memory could do, moves DNa by at most 1.4 Hz (seed means). No DN type moves more than 5 Hz; the largest is 4.5 Hz (DNge053).

Structure:
- Reward set: 0 DNs at hop 1. At hop 2, DNa01/02 via excitatory relays (LAL030b, CB0356, SIP201f, CRE011; 124 synapses onto DNa02).
- Punishment set: 28 DNs at hop 1, including DNa02 L/R 30/67 inhibitory synapses from MBON31/32.

Relation to the self-sustained state: driving the punishment set recruits PPL1 at 10.5-13.3 Hz from rest. Under the bypass, silencing it lowers PPL1 from 8.8 to 3.0 Hz and removes all DN activity. The output neurons look like part of the loop that sets the steering rates. This is a hypothesis: the 1-s windows cannot test persistence.
VERDICT CHANGE
PAPER: l.99, replace the last sentence with:

'The output neurons that hold the memory do have a route to the neurons that move the fly: driven hard, the punishment ones switch the steering neurons on and the reward ones can switch them off. But a smell drives these output neurons only weakly and reaches the steering neurons more directly, so even silencing the output neurons outright barely changes what the legs receive. The memory is written in a notebook that is almost never opened.'
NOTES: Expression (3 seeds, 1 s, vinegar at 150 Hz): the route exists but the memory is too weak to use it.
- Driving the 20 punishment output neurons at 20-100 Hz with no smell moves 24-27 descending types by more than 5 Hz, the left steering neurons to 19-23 Hz from 0. MBON14 alone at 50 Hz moves 20 types (steering 18 / 4 Hz).
- Driving the 12 reward output neurons at 50-100 Hz during a smell silences 15-20 types (left steering 20 to 0-3 Hz).
- With the projection neurons' synapses outside the mushroom body cut, the smell reaches the steering neurons only through the output neurons: 10 Hz; 0 with the punishment set silenced, 26 with the reward set silenced.
- In the intact brain a smell drives the output neurons at only 0.5-12 Hz. Silencing either set moves the steering neurons by at most 1.4 Hz and no descending type by more than 4.5 Hz.

### [learning] Note 7: 'the reward output neurons, driven at 40 Hz, reach none'.
STEPS: expression-harsh 'drive' mode for the reward set (20/50/100 Hz x no odour / L / both); structure rows for set 'reward'; per-DN-type counts from _dn_types.csv. The paper's 40 Hz was a drive on the targets, not on the MBONs (verify_wording 19b).
CRITERION: S26(3): the reward set at 20-100 Hz reaches no DN.
NUMBERS: No odour, 20 / 50 / 100 Hz: total_spikes 230 / 550 / 1,001 (only the MBONs themselves). All DNs are 0.0 and 0 DN types move.

Odour on the left:
- DNa L 19.8+-2.5 goes to 13.0+-3.3 / 2.5+-2.0 / 0.0.
- 2 / 15 / 20 DN types fall by more than 5 Hz.
- PPL1 11.9 goes to 8.4 / 2.7 / 0.2.

Odour on both sides:
- DNa L 32.8 goes to 29.8 / 23.8 / 8.5.
- 1 / 5 / 20 types move.

Structure: 435 targets, 0 DNs. DNa01/02 are two synapses away through excitatory relays.
VERDICT CHANGE
PAPER: Note 7, replace 'the reward output neurons, driven at 40\,Hz, reach none' with:

'the reward output neurons have no descending neuron among their targets and drive nothing in a silent brain, but at 50-100\,Hz during a smell they silence 15-20 descending types, the left steering neurons from 20 to 0-3\,Hz'
NOTES: Reward set driven, 3 seeds, 1 s. No odour: 0 DNs at 20-100 Hz. Odour L: DNa L 19.8+-2.5 goes to 13.0+-3.3 / 2.5+-2.0 / 0.0 Hz at 20 / 50 / 100 Hz, with 2 / 15 / 20 DN types down by more than 5 Hz.

### [learning] Note 7: 'the 28 descending targets of the punishment output neurons fire the same (within 0.6 Hz) whether those neurons are intact or silenced'. Verify_wording 19c found this largely true by construction, because the DNs themselves were kicked.
STEPS: expression-harsh 'kick-nodn' mode: tonic 0/10/40 Hz on the punishment set's 996 non-DN targets only, MBONs intact or silenced, x3 odour presentations; column 'target DNs Hz'. 'drive' mode for the same column with the set driven.
CRITERION: S26 design (kick-nodn removes the by-construction problem): intact vs silenced within 0.6 Hz with the DNs not kicked.
NUMBERS: Silenced minus intact, target DNs Hz:
- Tonic 0: +0.27 (L), +0.15 (both).
- Tonic 10: -0.19 / -0.23 / -0.48 (none).
- Tonic 40: -0.04 / -0.24 / +0.31.
- Maximum |diff| 0.48 Hz. PASS, now not by construction.

Driving the set at 20 / 50 / 100 Hz with no odour raises these DNs from 0 to 6.2 / 7.0 / 7.6 Hz, and from 7.0 to 8.1-9.1 Hz with odour.
VERDICT REWORD
PAPER: Note 7:

'the 28 descending targets of the punishment output neurons fire within 0.5\,Hz of the same whether those neurons are intact or silenced (with tonic input of up to 40\,Hz given only to their other targets), although driving the set at 20-100\,Hz raises them from 0 to 6-8\,Hz'
NOTES: Punishment set, 28 DN targets, 3 seeds: max |silenced - intact| 0.48 Hz over tonic 0/10/40 Hz x 3 odour presentations. Driven set: 6.2-7.6 Hz from 0.

### [learning] Note 7: 'No descending neuron changes with training.'
STEPS: All 20 new conditioning runs plus the paper files: post - pre per CS for DNa L/R, DNp09, MDN, DN all, feed MNs and approach. The reward-run CS+ change minus the matched no-teaching change covers 10 comparisons: vinegar 3 seeds at 3 cycles, 6 cycles, both pair runs, and the ester/floral runs.
CRITERION: No pre-set edge criterion beyond S23's 2-Hz bound. Consistency with verify_wording 19a ('no descending neuron changes with the pairing').
NUMBERS: DNp09, MDN and feed MNs change 0.0 in every run; DN all by at most 0.13 Hz.

CS+ reward minus no-teaching, DNa L: -8.0, +0.5, -2.5, -1.5 (vinegar), 0, 0 (ester), +6.0 (sweet), 0 (ester vs sweet), +1.0 (floral), +3.0 (vinegar vs floral). Range -8 to +6 Hz, n = 10.

When ester is paired (3 cycles, 6 cycles, and vs sweet), the post-test is identical to the no-teaching run in all 16 saved spike rows.
VERDICT REWORD
PAPER: Note 7: 'No descending neuron changes with the pairing: the steering neurons shift by up to 8\,Hz between the tests before and after training, as much without a teaching signal, and the walking, backing and feeding neurons do not move.'

This agrees with 19a; the maximum is updated from 7 to 8 Hz.
NOTES: CS+-specific DNa change over the no-teaching run: -8 to +6 Hz (n = 10), no consistent sign across odours. When ester is paired, the post-test is spike-identical to the untaught run.

### [learning] RESEARCH_NOTES 16f: 'MBON14 (alpha3) alone at 30 Hz drives DNa L 14 / R 7 and DNge053 35, DNbe007 27, DNb05 26, DNg100 24, DNg13, DNg16'. The implementation review (impl_reviews.md l.249; RESEARCH_NOTES l.1922-1923) said 'MBON14 alone at 50 Hz gives DNa L 2.5 Hz now'.
STEPS: expression-harsh 'types' rows for MBON14 (3 seeds, 1,000 ms), against the smoke file experiments/results_edge/_smoke/expression_harsh/..._all.csv (200 ms, 1 seed).
CRITERION: None pre-set. Reproduce or refute 16f in the current model.
NUMBERS: Production run, MBON14 at 50 Hz, no odour:
- DNa L 18.0+-2.3 (16.0/20.5/17.5), R 4.0+-1.0 Hz; PPL1 10.5.
- 20 DN types above 5 Hz, including DNge053 31.7, DNbe007 25.2, DNb05 24.2, DNg100 20.3, DNg13 18.2 and DNg16 16.3. These are the same six types 16f names.

Smoke run: DNa L 2.5 Hz, 1,148 spikes in 0.2 s, against 11-16k spikes/s over 1 s. The response builds up over the first second, so the '2.5 Hz now' was a 200-ms, 1-seed artefact.
VERDICT KEEP
PAPER: No paper text beyond the l.99 change. In RESEARCH_NOTES, replace 'MBON14 alone at 50 Hz gives DNa L 2.5 Hz now' with 'MBON14 alone at 50 Hz gives DNa L 18 / R 4 Hz over 1 s (2.5 Hz in the first 200 ms), as 16f said'.
NOTES: MBON14 alone (4 neurons) at 50 Hz, 3 seeds, 1 s: DNa L/R 18.0+-2.3 / 4.0+-1.0 Hz and 20 descending types above 5 Hz (DNge053 32, DNbe007 25, DNb05 24, DNg100 20 Hz).

RUN PROBLEMS [learning]: No run is broken, and the check files match.

Checks and logs:
- cond-contingency/...vinegar-vs-ester_seed0.check.txt: PASS and byte-identical (80 cells in the main CSV, 35 in _compartments.csv, 0 differ). Its reference is identical to both release/pre_rerun_20260925 and pre_rerun_20260926 copies.
- expression_harsh...check.txt: MATCH TO THE DIGIT, 108 rows x 21 columns, 0 mismatches. The internal self-check (18 groups) is also identical. The reference expression_probe file differs from the release copies only in wall_s (max |diff| 0 in every other column).
- logs/edge/queue_20260927.out l.58-67: all five steps ran ok on attempt 1. No traceback, no NaN in any output.
- Pre-tests are deterministic: 68 comparisons of the same odour across all edge and paper runs, 0 mismatches.
- cond-pairs, cond-long and the non-forward protocols have no reference file by design.
- The 'sub' mode (P2 expression-subthreshold) was not run.

Caveats that bear on the verdicts:
1. **Index source.** The task text says the index comes from the _compartments.csv files. It does not: paper_numbers.py (l.352-362) skips them and uses rows 'drive reward-comp' / 'drive punish-comp' of the main CSV. The _compartments.csv files hold mean w/w0 per MBON type.
2. **Sample size.** Every edge conditioning cell is n = 1 (seed 0) per order. Index seed noise is about 0.03, so the pair differences are real, but two results sit on their bounds within that noise:
   - US-only vinegar at 0.845 against 0.85;
   - the vinegar-vs-floral control at 0.097 against 0.1.
3. **S23's 2-Hz DN bound is below single-run noise.** Any small weight change, including silencing an entire output set, moves DNa by up to +-4.5 Hz and the lateral approach index by up to +-6.5 Hz per seed.
4. **Self-sustained state (analysis_A).**
   - Training never returns to rest. All 156 rest phases in the 21 runs have PPL1 8.58 +- 0.28 Hz and KC 0.136 +- 0.005 Hz. That background is behind the 5-15 % US-alone loss and part of the punishment compartment's odour-driven depression.
   - Every odour row of expression-harsh is read at 66-77k spikes/s with 1.55 % of neurons active, i.e. in or near the state.
   - The output neurons appear to control the state: punishment MBON drive recruits PPL1 at 10-13 Hz; reward MBON drive during a smell cuts PPL1 from 12 to 0.2 Hz; under the bypass, silencing the punishment set drops PPL1 from 8.8 to 3.0 Hz and zeroes the DNs. This is a hypothesis; 1-s windows cannot test persistence.
   - Exception to analysis_A's 'any smell': floral at 150 Hz does not show the state's signature in its 1-s pre-test (PPL1 1.9 Hz, DNa L/R 1.0/11.0), and PPL1 falls to 1.3-4.9 Hz during floral training phases. Vinegar gives 16 Hz.
5. **The 16f discrepancy** came from a 200-ms smoke window. Short smoke runs should not be used to refute 1-s claims, because MB-output responses build up over 0.2-1 s.
6. **Numbers already corrected in verify_wording 18a** (0.55 +- 0.03, 0.59-0.70, 0.03 without a teaching signal) are assumed in the wording above.
7. **Environment variables.** cond-contingency, cond-pairs and cond-long pass --signs known --eln 0.25 on the command line instead of exporting FLYBRAIN_*. The output tags confirm the variant shiu_min1+known+eln0.25.

Scratch scripts not kept. (li.py, li_all.csv, dn.py, dn2.py, expr.py, dntypes.py, pre.py). No project files were modified and no simulations were run.

>>> CHECK [learning] 1. Note 7 / l.99: the memory is associative (S24 contingency). Analyst: REWORD, (a) PASS, (b) fails narrowly (0.845 < 0.85).: agrees=True
OWN: Checks: cond-contingency .check.txt PASS, 80 + 35 cells, byte-identical. The paper's conditioning files are byte-identical to release/flycraft_20260926. Index = post/pre of 'drive reward-comp' (CS- minus CS+).

Forward: +0.498 (0.0951 / 0.5933).

No-teaching control, seed 0: +0.024 (vinegar first) and -0.014 (ester first). Pooled: 0.033 +- 0.035 (np.std; 0.041 with ddof 1), n = 4.

(a) Backward +0.031 (0.837 / 0.868) and -0.078 (0.875 / 0.798). Unpaired +0.053 (0.826 / 0.879) and -0.022 (0.871 / 0.848).
- Distance from the seed-matched control: 0.007 / 0.064 / 0.029 / 0.008. Against the 3-seed vinegar-first mean (0.049) the vinegar-first distances are 0.018 and 0.004.
- PASS. Pooled -0.004 +- 0.058 (ddof 1), not 0.059.

(b) US-only retained drive:
- Vinegar first: vinegar (never presented) 0.927, ester 0.926.
- Ester first: ester (never presented) 0.948, vinegar 0.8452.
- The vinegar cell fails by 0.0048. Mean 0.912 +- 0.045, not 0.911. US-only index -0.001 / -0.103.

What the analyst's sentence leaves out: with no teaching signal the odours lose as much.
- No-teaching retained drive: 0.867-0.978 (not 0.977), 0.910 +- 0.032 over 8 cells. US-only: 0.912 +- 0.045.
- Vinegar alone without teaching keeps 0.867-0.903, so the failing cell sits only 0.02-0.06 below that.
- In the matched backward and unpaired runs, every odour keeps 0.04-0.10 less than in the seed-0 no-teaching run: vinegar 0.837 / 0.826 vs 0.895; ester 0.868 / 0.879 vs 0.919; ester 0.875 / 0.871 vs 0.917; vinegar 0.798 / 0.848 vs 0.903.
- So the US adds a loss of about 5 % that both odours share. That lowers the index; it does not add to it. The pre-set consequence ('part of the index comes from the US itself') is therefore false here. The notes must say explicitly that it was not applied, and why.

Mechanism (phase_stats in the 21 sidecars): confirmed.
- 156 rest phases: PPL1 8.58 +- 0.28, KC 0.136 +- 0.005, all DANs 1.81 +- 0.02, DAN onto the punishment compartment 0.703 Hz, onto the reward compartment 0.077 Hz.
- Reward 'US alone' phases: KC 0.083-0.093 Hz, DAN onto the reward compartment 33.7-34.2 Hz. (The 0.146 upper value comes from the punish runs.)
- The rule, 0.3 x (0.085/20) x (34/20) x 30 s, predicts about 6.5 % loss for a never-presented odour. Observed: 5.2-7.3 %.
- In the punishment compartment the backward US-alone costs about 0 (ester 0.472 vs 0.458 control). So state the mechanism for the reward compartment only.

The proposed sentence 'The teaching signal alone lowers every odour's drive by 5-15 %' is literally true but misattributed without the no-teaching comparison. It is too strong.

Draft 6 l.238 pending sentence 'taught much less' understates the result. Backward and US-only taught nothing beyond the no-teaching control.
CORRECTED: Main text l.99 (draft 5): unchanged.

Draft 6 l.238 pending sentence: 'A smell given after the sugar rather than with it, or sugar with no smell, taught nothing: the index was -0.10 to +0.05, as with no teaching signal at all.'

Note 7, after '0.03 without a teaching signal': 'The pairing is what counts. With the teaching signal given just before the paired smell, or 5 s after it, the index is -0.08 to +0.05 (one seed per odour order), as without one. Given alone, the teaching signal takes about the same from both smells: they keep 0.85-0.95 of their drive, against 0.87-0.98 with no teaching signal. It gives no index (-0.10 to 0.00).'

Notes: Contingency controls (seed 0, 3 cycles, reward DANs at 50 Hz, both odour orders):
- Forward +0.50. Backward +0.03 / -0.08. Unpaired +0.05 / -0.02. No teaching signal +0.02 / -0.01 (pooled 0.03 +- 0.04, n = 4).
- Backward and unpaired pooled: -0.004 +- 0.058 (n = 4, ddof 1).
- Teaching signal alone: index -0.00 / -0.10; retained drive 0.845-0.948 (0.91 +- 0.05, n = 4), against 0.87-0.98 (0.91 +- 0.03, n = 8) with no teaching signal.
- The pre-set US-only bound (>= 0.85 for both odours) is missed by 0.005 in one cell (vinegar 0.845; without teaching vinegar keeps 0.87-0.90). The pre-set consequence, that part of the index comes from the US itself, was not adopted: the US alone lowers both odours alike, by about 5 % in the matched backward and unpaired runs, and gives no positive index.
- In the reward compartment this loss fits the rule applied to Kenyon cells that keep firing at about 0.09 Hz during the US-alone phases. The brain stays in its self-sustained state throughout training (rest: PPL1 8.6 Hz, KC 0.14 Hz, n = 156 phases). The rule predicts 6.5 % for a never-presented smell; observed 5-7 %.

>>> CHECK [learning] 2. Note 7 '0.21 +- 0.14 for punishment', set beside the reward control 0.04 (S24 applied to backward punishment). Analyst: REWORD, criterion PASS.: agrees=True
OWN: Source: 'drive punish-comp', post/pre.

Backward punishment:
- Ester paired: -0.258 (0.4715 / 0.2132).
- Vinegar paired: +0.248 (0.2282 / 0.4761).

No-teaching control (us-wiring files, paper):
- Ester first, seed 0: -0.236.
- Vinegar first: +0.256 (seed 0); +0.280 +- 0.035 over seeds 0-2 (ddof 1; 0.029 with np.std).
- Distances from backward: 0.022 and 0.008. PASS.

Forward (paper, n = 3 each):
- Ester paired: 0.0776 / 0.0732 / 0.0789, so 0.077 +- 0.003 (ddof 1; 0.002 np.std).
- Vinegar paired: 0.300 / 0.366 / 0.379, so 0.348 +- 0.042 (not 0.043; np.std 0.034).
- Pooled: 0.2125 +- 0.138 (np.std), n = 6. Increments over the same-order control: +0.31 (ester paired) and +0.07 (vinegar paired). All confirmed.

Corrections:
- No-teaching ester keeps 0.458-0.549 of its punishment drive (n = 4; seed 1 is 0.549). The analyst's '0.46-0.48' covers seed 0 only. Vinegar keeps 0.217-0.229 (n = 4), confirmed.
- Phase stats: vinegar-alone phases drive the punishment-compartment DANs at 6.41-7.28 Hz (means 6.72-6.84), not 6.6-7.3. Ester: 0.46-0.66 Hz. Rest: 0.703 +- 0.026 Hz.

The analyst's wording is too weak on the plainest evidence:
- The paired smell reaches the floor in both orders: vinegar 0.097 / 0.094 / 0.091, ester 0.094 / 0.100 / 0.099.
- Backward leaves it exactly at the no-teaching level: vinegar 0.228 vs 0.227; ester 0.472 vs 0.458.
- This is a cleaner associative demonstration than the order-contaminated index.

The word 'only' in 'only 0.07 and 0.31 above' is wrong for 0.31, which is most of that order's index.

SD convention: the notes use ddof 1 while paper_numbers uses np.std. State which.
CORRECTED: Note 7, replace '$0.21 \pm 0.14$ for punishment' with: 'for punishment 0.35 with vinegar paired and 0.08 with ester paired. Without a teaching signal the same compartment already gives +0.28 and -0.24 in those orders, because vinegar lowers its own input there, so pairing adds 0.07 and 0.31. Pairing backwards gives the no-teaching values (+0.25, -0.26). On the paired smell alone the effect is plain: it falls to the floor (0.09-0.10) in both orders, against 0.22 (vinegar) and 0.46-0.55 (ester) without a teaching signal or with it given backwards.'

Notes: Punishment compartment ('drive punish-comp', post/pre):
- Paired index 0.35 +- 0.04 (vinegar) and 0.077 +- 0.003 (ester), n = 3 each, ddof 1.
- No teaching signal: +0.28 +- 0.04 (n = 3) and -0.24 (n = 1). Backward: +0.25 and -0.26 (n = 1 each).
- Paired smell kept 0.091-0.100 (n = 6). Without teaching: vinegar 0.22-0.23, ester 0.46-0.55 (n = 4 each). Backward: vinegar 0.23, ester 0.47.
- Vinegar drives the punishment-compartment DANs at about 7 Hz (6.4-7.3), ester at 0.5 Hz, and every rest adds 0.7 Hz.

>>> CHECK [learning] 3. Odour specificity across pairs (S25 plus P2 cond-extra). Analyst: REWORD, sweet/ester sweet-paired 0.147 < 0.2 triggers the second branch; floral/vinegar PASS.: agrees=True
OWN: Glomerular overlap (senses.py l.42-46):
- Sweet and ester share DM2, DM4, VM2, VA2: 4.
- Vinegar and ester share VA2, VM2: 2.
- Floral and vinegar share none: 0.

Indices ('drive reward-comp'):
- Ester paired vs sweet: 0.429 (0.097 / 0.526). Sweet paired: 0.147 (0.103 / 0.2495). Controls -0.025 and +0.004.
- Floral paired: 0.722 (0.1195 / 0.8415). Vinegar paired vs floral: 0.628 (0.101 / 0.729). Controls -0.043 and +0.097 (just under the 0.1 bound).
- Vinegar and ester, 3 seeds per order: 0.527 +- 0.025 (vinegar paired) and 0.569 +- 0.028 (ester paired), ddof 1.
- Mean index per pair: 0.68 / 0.55 / 0.29. The other smell keeps 0.73-0.84 / 0.59-0.70 / 0.25-0.53. The paired smell keeps 0.095-0.120.
- The six new no-teaching runs: +0.009 +- 0.053 (range -0.043 to +0.097). All 10 no-teaching runs: 0.018 +- 0.048.

Sanity checks:
- Pre-tests are identical across all 68 same-odour, seed-0 comparisons (0 differ).
- KC active in the pre-test: sweet 6.03 %, ester 3.57 %. All confirmed.
- S25 second branch applies (0.147). P2 zero-overlap pair PASS (0.72 and 0.63, both >= 0.3).

One addition. KC-level overlap does exist, but only from a smoke run: results_edge/_smoke/odor_code_plus/odor_code_plus_flywire_hz150_test10-glomeruli-library_overlap.csv, 1 seed, 100 ms, library odours.
- Jaccard: floral/vinegar 0.024, vinegar/ester 0.116, ester/sweet 0.243 (vinegar/sweet 0.425).
- Same order as the index. With KC active 1.8 % / 4.1 %, this puts about 64 % of ester's KCs inside sweet's code, and 28 % the other way. That fits the asymmetry (ester keeps 0.25; sweet keeps 0.53). Indicative only.

Wording notes:
- The proposed Note text uses seed-0 values for vinegar/ester (0.60 / 0.50) although 3-seed means exist (0.57 / 0.53).
- Draft 6 l.238 now says 'about two-thirds', not 'three-fifths'. Adapt the insertion.
CORRECTED: Main text (draft 5 l.99; draft 6 l.238): '...while the other smell kept about two-thirds of its strength (between a quarter and four-fifths over the three pairs of smells I tried; the more smell receptors two smells share, the less the other one keeps)...'

Note 7, add: 'Over three pairs of smells the index is:
- 0.72 and 0.63 for floral and vinegar, which share no glomerulus (one seed per order);
- 0.57 and 0.53 for ester and vinegar, which share two of six (three seeds per order);
- 0.43 and 0.15 for ester and sweet, which share four of six (one seed per order); pairing sweet leaves ester 0.25 of its drive.
The paired smell always falls to 0.10-0.12, and without a teaching signal every pair stays between -0.04 and +0.10.'

Notes:
- Index by pair: floral/vinegar 0.72 / 0.63 (n = 1 per order); ester/vinegar 0.55 +- 0.03 (n = 6); sweet/ester 0.43 / 0.15 (n = 1 per order). Seed SD of the index is about 0.03.
- No teaching signal: -0.04 to +0.10 (0.01 +- 0.05, n = 6 new runs).
- The paired odour keeps 0.095-0.120; the other keeps 0.25-0.84.
- Kenyon-cell overlap from a one-seed, 100-ms smoke run (Jaccard 0.02 / 0.12 / 0.24) ranks the pairs the same way; not a production measurement.

>>> CHECK [learning] 4. l.99 'no working route to the neurons that move the fly ... a notebook that nobody downstream reads' (S26). Analyst: CHANGE, all three S26 conditions fail.: agrees=True
OWN: Checks:
- .check.txt MATCH TO THE DIGIT: 108 rows x 21 columns against expression_probe (tonic 0 / 10 / 40 only).
- Self-check: 18 groups identical.
- Bypass cut: 123,833 ALPN connections (678,549 synapses). Other antennal-lobe exits were left in place (ALLN 17,011, ALIN 10,189, ALON 15,584, ORN 1,146, weighted), yet the punishment-silenced bypass gives 0 in every DN.

(1) FAIL. Punishment set, no odour, at 20 / 50 / 100 Hz:
- DN types moved by more than 5 Hz: 24 / 25 / 27, all upward.
- DNa L 19.2 +- 2.1 [18.5 / 21.5 / 17.5], 23.3 +- 1.8, 22.2 +- 2.6. DNa R 4.2 / 3.2 / 0.5. GF, MDN, DNp09 0. PPL1 10.5 / 11.7 / 13.3.
- At 100 Hz: DNge053 43.0, DNbe007 40.8, DNg13 39.3, DNb05 31.8, DNg100 27.0, DNa02 14.0, DNa01 8.7 Hz.
- MBON14 alone at 50 Hz: DNa L 18.0 +- 2.3 [16.0 / 20.5 / 17.5], R 4.0 +- 1.0, 20 types. With odour it moves 0 types (max 4.3 Hz).
- The 100-Hz set during odour moves 14 types (L; 6 up, 8 down) and 9 (both).

(2) FAIL. Bypass, odour L:
- Intact: DNa L 10.0 +- 6.6 [5.0 / 7.5 / 17.5], R 1.8, 11 DN types above 5 Hz. DN all (0.22) and target DNs (1.81) are below 2 Hz, so the first half of the criterion only fails on DNa.
- Punishment set silenced: every DN 0, PPL1 3.0.
- Reward set silenced: DNa L 25.5 +- 2.5, R 6.7.

(3) FAIL. See claim 5. The analyst's 'all decreases' is wrong: at 20 / 50 / 100 Hz, 1 / 1 / 2 of the 2 / 15 / 20 moved types go up.

Why the memory cannot use the route:
- Set MBON rates, intact: reward 0.50 +- 0.14 (L) and 6.19 +- 0.55 (both) Hz; punishment 5.27 and 11.72 Hz.
- Silencing a whole set in the intact brain (kick-nodn, tonic 0) moves DNa by at most 1.33 Hz as a seed mean (not 1.4; single seeds up to 4.5). The largest DN type change is 4.5 Hz (DNge053).

Structure: confirmed.
- Reward: 0 DNs at hop 1. DNa02 receives 96 + 28 = 124 excitatory synapses at hop 2 (LAL030b, CB0356, CRE011); DNa01 via SIP201f.
- Punishment: 28 DN neurons (13 types) at hop 1, 401 excitatory and 719 inhibitory synapses. DNa02 gets 67 / 30 inhibitory synapses from MBON32/31.
- Yet the driven set raises DNa02 to 13-14 Hz, so the excitation is polysynaptic.

The loop hypothesis is contradicted in the intact brain:
- Silencing the punishment set leaves DNa (20.0 vs 19.8) and PPL1 (11.5 vs 11.9) unchanged. The MBONs are necessary only under the bypass.
- The no-odour punishment drive recruits 18-33k spikes/s with asymmetric DNa (L about 20, R 0.5-4). The self-sustained state runs at about 58k from about 2,000 neurons with DNa 16/18. So this is probably not simply the state switching on, though 1-s windows cannot settle it.

'Driven hard' overstates the punishment case: 20 Hz already moves 24 types.
CORRECTED: l.99, replace the last sentence with: 'The output neurons that hold the memory do have a route to the neurons that move the fly. In a quiet brain, driving the punishment ones at 20 Hz or more switches the left steering neurons on. During a smell, the reward ones, driven harder, switch them off. But a smell drives these output neurons only weakly and reaches the steering neurons by a more direct path, so even silencing the output neurons outright changes what the legs receive by at most about a spike a second. The memory is written in a notebook that is almost never opened.'

Notes: keep the analyst's four bullets, with these changes:
- 'silencing either set moves the steering neurons by at most 1.3 Hz (seed means) and no descending type by more than 4.5 Hz'.
- Reward set with odour: '15-20 types, 14-18 of them down'.
- Add: 'The bypass leaves the antennal lobe's other exits intact, but with the punishment set silenced no descending neuron fires.'
- Replace the loop hypothesis with: 'Under the bypass the punishment output neurons are needed for all odour-driven descending activity and for most of PPL1 (8.8 to 3.0 Hz). In the intact brain they are not: silencing them leaves the steering neurons and PPL1 unchanged.'

>>> CHECK [learning] 5. Note 7 'the reward output neurons, driven at 40 Hz, reach none' (S26(3)). Analyst: CHANGE.: agrees=False
OWN: The CHANGE verdict is right, but the proposed wording is too strong in two places.

No odour, reward set at 20 / 50 / 100 Hz:
- total_spikes 230.3 / 550.3 / 1,000.7 = 12 MBONs x 19.2 / 45.9 / 83.4 Hz. Nothing else fires.
- The sidecar lists all 12 reward MBONs as inhibitory (n_excitatory 0). 'Drives nothing in a silent brain' is therefore true by construction, not a test result. This is the same class of problem as 19c.

Odour L:
- DNa L 19.83 +- 2.52 goes to 13.00 +- 3.28 / 2.50 +- 2.00 / 0.00.
- DN types moved by more than 5 Hz: 2 / 15 / 20. Of these 1 / 14 / 18 go down and 1 / 1 / 2 go up (DNp31 +5.3; DNbe001 +9.2 and +11.8). The analyst's 'all fall' is wrong.
- DNge053 36.2 goes to 27.2 / 10.5 / 1.7. DNa R only 14.2 to 11.8 / 8.8 / 10.3. PPL1 11.9 to 8.4 / 2.7 / 0.17. GF rises 5.2 to 7.2.

Odour both: DNa L 32.8 goes to 29.8 / 23.8 / 8.5; 1 / 5 / 20 types move (19 down at 100 Hz).

Structure: 435 targets, 16,173 synapses, 0 DNs. At hop 2, DNa02 receives 124 excitatory synapses and DNa01 46.

'Silence 15-20 descending types' overstates what happens: many are only reduced (DNa R stays at 10 Hz) and 1-2 increase.
CORRECTED: Note 7, replace 'the reward output neurons, driven at 40\,Hz, reach none' with: 'the reward output neurons, all inhibitory in the model, have no descending neuron among their targets, so in a quiet brain they can do nothing; during a smell, driven at 50-100\,Hz, they turn down 14-18 descending types, the left steering neurons from 20 to 0-3\,Hz'.

Notes: Reward set (12 MBONs, all inhibitory) driven; 3 seeds, 1 s, vinegar at 150 Hz.
- No odour: only the MBONs spike (230-1,001 spikes in total).
- Odour L: DNa L 19.8 +- 2.5 goes to 13.0 +- 3.3 / 2.5 +- 2.0 / 0.0 Hz at 20 / 50 / 100 Hz. 2 / 15 / 20 DN types move by more than 5 Hz (1 / 14 / 18 down). DNa R 14 goes to 9-12 Hz. PPL1 11.9 goes to 0.2 Hz at 100 Hz.
- Odour on both sides: DNa L 32.8 goes to 8.5 Hz at 100 Hz.

>>> CHECK [learning] 6. Note 7 'the 28 descending targets ... fire the same (within 0.6 Hz) whether intact or silenced'. Analyst: REWORD, PASS with kick-nodn (0.48 Hz).: agrees=True
OWN: Source: kick-nodn, column 'target DNs Hz', seed means, silenced minus intact.
- Tonic 0: L +0.27, both +0.15, none 0.
- Tonic 10: L -0.19, both -0.23, none -0.48.
- Tonic 40: L -0.03, both -0.23, none +0.31.
- Maximum 0.48 Hz. PASS, and not by construction: the DNs are not kicked, and the MBONs fire at 4-24 Hz in the intact rows.

Group-mean caveat: the 28 targets get excitatory (MBON35) and inhibitory (MBON31/32) synapses, so a mean could hide opposite changes. Per type, over the 9 target types active in any simulation (DNde003, MDN, DNp52 and DNpe023 are silent throughout), the largest silenced-minus-intact change is 3.3 Hz (DNa02, tonic 10). So nothing large is hidden.

Driven set: target DNs go from 0 to 6.15 / 7.04 / 7.64 Hz with no odour. With odour they go from 7.0 to 7.9-9.1; the analyst's 8.1 lower bound covers odour L only (both at 20 Hz = 7.89).
CORRECTED: Note 7: 'the 28 descending targets of the punishment output neurons fire within 0.5\,Hz of the same (no single type by more than 3.3\,Hz) whether those neurons are intact or silenced, with tonic input of up to 40\,Hz given only to their other targets; driving the set itself at 20-100\,Hz in a quiet brain raises them from 0 to 6-8\,Hz'.

Notes: Punishment set, 28 DN targets, 3 seeds. Max |silenced - intact| is 0.48 Hz for the group mean and 3.3 Hz for any single type, over tonic 0 / 10 / 40 Hz x 3 odour presentations. Driven set: 6.2-7.6 Hz from 0 (no odour); 7.9-9.1 from 7.0 (odour).

>>> CHECK [learning] 7. Note 7 'No descending neuron changes with training'. Analyst: REWORD, 'the steering neurons shift by up to 8 Hz ... as much without a teaching signal'.: agrees=False
OWN: Over 51 files (21 edge runs + 30 paper-model runs):
- DNp09, MDN and feed MNs change by 0.0 everywhere. DN all by at most 0.134 Hz (us-only edge run, CS-).

Raw |post - pre| DNa is at most:
- 7.5 Hz in any file (paper reward-20hz, vinegar seed 0, CS+);
- 7.0 with reward at 50 Hz;
- 6.5 with no teaching signal;
- 6.0 with and 6.0 without teaching in the edge runs.

The proposed 'shift by up to 8 Hz' is therefore wrong. The -8.0 is a difference of two shifts (vinegar seed 0: taught -4.0 vs control +4.0), not a shift. 19a's 'up to 7 Hz ... 6.5 Hz without' stands; do not update it to 8.

CS+-specific DNa L (taught shift minus matched no-teaching shift), n = 10:
- Values: -8.0, +0.5, -2.5, -1.5, 0, 0, +6.0, 0, +1.0, +3.0. Mean -0.15 +- 3.6. DNa R -3.5 to +1.5; approach -5.5 to +3.0.
- 4 of 10 exceed S23's 2-Hz bound but with no consistent sign.
- The no-teaching seeds alone scatter by that much: raw CS+ shifts +4.0 / -3.5 / +1.5. These tests are 1-s counts on 2 neurons, read in the self-sustained state.
- S23 on cond-long itself PASSES: CS+-specific DNa -1.5 / -1.5 (vinegar) and 0 / 0 (ester); index 0.47 / 0.53 against controls +0.04 / -0.03.

Ester paired (3 cycles, 6 cycles, vs sweet):
- post_CS+ equals the no-teaching run in 16 of 16 spike rows, although reward-compartment drive is 3,900-4,000 against 37,000-37,800.
- Ester as CS- in the vinegar-paired seed-0 run is also 16 of 16 identical (drive 24,444 vs 37,850).
CORRECTED: Note 7: 'No descending neuron changes consistently with the pairing. The steering neurons shift by up to 7\,Hz between the tests before and after training, as much without a teaching signal (6.5\,Hz), and the walking, backing and feeding neurons do not move. When the paired smell is ester, the test after training is spike for spike the same as without a teaching signal, although that smell's input to the reward output neurons has fallen to a tenth.'

Notes:
- The CS+-specific DNa change over the matched no-teaching run is -8 to +6 Hz (n = 10, mean -0.2 +- 3.6), with no consistent sign across odours or seeds.
- Raw shifts are at most 7.5 Hz with a teaching signal (any file) and 6.5 Hz without.
- DNp09, MDN and feeding MNs 0.0; DN all at most 0.13 Hz.
- With ester paired, the post-test equals the untaught run in all 16 spike readouts.
