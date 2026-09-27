
### [numerics] 1. Brian2 'spike for spike … a single neuron tips' (l.89, Note 1 l.137, lif.py docstring)
PAPER: l.89: "My version reproduces Shiu et al.'s own code spike for spike in two test runs out of three, and in the third a single neuron near its threshold tips the other way \note{1}." Note 1 (l.137): "Against Brian2 2.10.1 …, sugar-taste neurons at 100 Hz for 1 s and 3 seeds at dt=0.1 ms: identical per-neuron spike counts for two seeds; the third diverges at a near-threshold event (23,689 against 23,512 spikes; per-neuron correlation 0.9999)."
VERDICT CONFIRMED headline=False
EVIDENCE: logs/reproduce_core-check.out (26 Sep 23:45) and logs/reproduce_brian2_20260925.out give the same numbers. Kernel against Brian2 totals: seed 0 23,689 vs 23,512 (+177 spikes, +0.75 %); seed 1 24,215 = 24,215; seed 2 24,782 = 24,782. The log shows the seed-0 divergence spread well beyond one neuron:
- Over neurons active in either run, 16 fire only in Brian2 and 6 only in the kernel (both 580, union 602). Seeds 1 and 2 match, so these 22 all come from seed 0.
- The ten largest per-neuron differences are 1.3–2.3 spikes on the 3-seed mean, i.e. 4–7 spikes each within seed 0.

The item's exact '284 of 592 active neurons differ' cannot be re-derived from saved files. compare_brian2.py never saves the kernel's counts, and the figure comes only from RESEARCH_NOTES.md l.1815 (a by-hand run). ref_sugar.npz (in $TMPDIR/flycraft_brian2 and the 25 Sep scratch copy, which are identical) gives 579 Brian2-active neurons in seed 0. The kernel's 0.41 % is about 571, so a union of 592 is consistent.

No file records that the divergence started at 'a single neuron near its threshold'. design_arms.json only proposes a new brian2_first_divergence.py to find the first mismatch.

Scope (reproduce.sh l.30 and ref_sugar.npz fields drive='in_grn_sugar:100', ms=1000, dt=0.1): only the published model (no FLYBRAIN_SIGNS/ELN on the export), only sugar drive (0.4 % of neurons active), only dt 0.1 (production is 0.2), only 1 s. The paper's own model, the male, and dense regimes such as cVA (6 % active) were never compared.

Two other points:
- brian2_reference.py is a transcription of Shiu et al.'s model.py (drive through PoissonGroup), not their code as published.
- The kernel keeps v, g and buf in float32 and snaps neurons within eps_v = 0.01 mV of rest (lif.py l.56, l.300-303). Exact identity is therefore not expected in general, and it may depend on the chunk count T (untested; run at T = 6).

The lif.py docstring l.16 cites 'brain/tests/ micro-network scripts, 14 Sep 2026'. brain/tests holds no such script (the files are brian2_reference, compare_brian2, export_for_brian2, optomotor*, test_lif, test_model_options, validate, vision_*), and grep for 'micro' there finds nothing. Note 1's numbers are accurate. The main-text sentence is what overstates.
WORDING: l.89: "My version agrees with a Brian2 transcription of Shiu et al.'s code. Run on the published model with the sugar-taste neurons driven for one second, two of three seeds give the same spike count in every neuron. In the third the two runs part and end 0.75 % apart in total spikes (per-neuron correlation 0.9999) \note{1}."

Note 1: "… the third diverges (23,689 against 23,512 spikes; 22 neurons fire in one run only, and 284 of the 592 active neurons end with different counts; per-neuron correlation 0.9999). The check covers only the published model, sugar drive, dt 0.1 ms and 1 s."

lif.py docstring: remove 'brain/tests/ micro-network scripts' or add those scripts.

### [numerics] 2. 'results identical at 0.1–0.5 ms' (Note 1 l.137; also lif.py docstring, run_brain.py --dt help, PAPER.md)
PAPER: Note 1 (l.137): "… sensory drive by Poisson kicks of 68.75 mV, $dt=0.2$ ms (results identical at 0.1--0.5 ms)."
VERDICT CONFIRMED headline=False
EVIDENCE: Frozen sensitivity files (release/pre_rerun_20260926/results/), 3 seeds × 600 ms, rows baseline (dt 0.2) / 'dt 0.1 ms' / 'dt 0.5 ms':
- **sensitivity_flywire_shiu_min1+known+eln0.25.csv** (the paper's model):
  - sugar→MN9 77.22 / 87.78 / 86.11 (dt 0.1 vs 0.2: +10.6 Hz, z≈2.5)
  - cVA→DNa L 10.00 / 7.50 / 7.78
  - sugar→feed MNs 24.05 / 26.66 / 28.89
  - food→GF 4.44 / 2.50 / 5.56
  - touch→DNp13 35.83 / 37.22 / 38.61
  - Only 4 of 22 readouts are identical across dt, and all four are 0.
- **sensitivity_flywire_shiu_min1.csv** (published lobe), dt 0.5 shifts that are systematic, not noise:
  - cVA→PPL1 107.29 → 117.53 (sd ≤ 0.57, z≈22)
  - cVA→KC 30.65 → 36.28 (+18 %, z≈40)
  - food→PAM 21.34 → 25.52
  - food→PPL1 110.7 → 121.1
  - sugar→MN9 80.56 → 86.11 (z≈7)
- **Male** (sensitivity_malecns_all_min1+eln0.25.csv):
  - cVA→PPL1 11.84 / 10.73 / 15.07 (+27 % at dt 0.5)
  - touch→MDN 11.53 / 14.86 / 8.19

test_lif output in logs/reproduce_core-check.out (published model, 500 ms, 3 seeds), dt 0.1 / 0.2 / 0.5:
- cVA→PPL1 105.6 / 105.9 / 116.4 (+10 %)
- cVA→KC 30.4 / 30.4 / 36.2 (+19 %)
- cVA total spikes 237,828 / 237,802 / 269,682 (+13 %)
- sugar feed 25.6 / 24.7 / 28.8

test_lif still prints 'AGREE' because its tolerance (test_lif.py l.67) is 3·max(sd, 0.15·mean, 1 Hz), at least 45 % of the larger mean.

Mechanism (lif.py l.292-293): ref_steps = round(2.2/dt) and delay_steps = round(1.8/dt). At dt 0.5 the refractory period becomes 2.0 ms and the delay 2.0 ms, so dt 0.5 is a slightly different model. The docstring itself says dt 0.2 was chosen so that both are whole steps. Differences between dt 0.1 and 0.2 are mostly within 3-seed noise.

Qualitatively nothing flips: pC1d/e and aIPg stay at 0.0 at every dt, and DNp13, GF and MN9 stay on.

The same wording appears in:
- run_brain.py l.17 ('results identical at 0.1-0.5')
- lif.py docstring l.21-22 ('0.1 / 0.2 / 0.5 ms give the same rates')
- PAPER.md l.68 and l.348 ('identical at dt 0.1, 0.2 and 0.5 ms')
WORDING: Note 1: "… $dt=0.2$ ms (qualitatively the same at 0.1 and 0.5 ms: the same readouts are on and off, and rates move by up to about 10 Hz. At 0.5 ms, where the refractory period and delay round to 2.0 ms, the published model's dopamine and Kenyon-cell rates rise by 10–19 %)."

Make the same change in the lif.py docstring, the run_brain.py --dt help and PAPER.md l.68/l.348. Also tighten test_lif's AGREE tolerance, or say it is ±45 %.

### [numerics] 3. Thread count / min(threads, 8) chunks (Note 10 l.155)
PAPER: Note 10 (l.155): "Of the 123 result files, 54 came out identical to the digit, and the others differ in a few cells because the originals were made with other thread counts or older scripts: …"
VERDICT PARTLY headline=False
EVIDENCE: **What holds:**
- The re-run's thread count is never named in the paper. reproduce.sh l.19 has `export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6}`, and RESEARCH_NOTES l.1812-1813 says the re-run used 6.
- Results depend on the chunk count, not on the thread count itself. lif.py l.311 sets `self.T = max(1, min(get_num_threads(), 8))`. Neuron i lives in chunk i % T (l.67). Spikes are delivered chunk by chunk (l.246-261) into float32 buffers (l.302), so T sets the summation order.
- This machine has hw.ncpu = 10, so a '10-thread' run is 8 chunks, and 8 and 10 threads give identical results by construction.

**What does not hold as stated:**
- flycraft.tex (draft 5) contains no '10-thread' wording. That phrase is in PAPER.md l.427 ('re-run with 10 threads instead of 6') and in RESEARCH_NOTES l.1778, l.1824 and l.1847 ('3, 5, 6 or 10 threads').
- Note 10's 'other thread counts' is therefore not false, only imprecise.

**Related omission:** each arena brain runs with NUMBA_NUM_THREADS=3 (experiments/encounter_trials.sh l.22), so T = 3. That chunking differs from the offline T = 6, and the paper does not say so.
WORDING: Note 10: "… because the originals were made with other thread counts or older scripts. The simulator splits the neurons into min(threads, 8) chunks, and the chunk count sets the order in which spikes are summed. The re-run used NUMBA_NUM_THREADS = 6; the originals used 3, 5, 6 or 10 threads, i.e. 3, 5, 6 or 8 chunks; each arena brain runs on 3."

PAPER.md l.427: "… re-run with 10 threads (8 chunks) instead of 6".

### [numerics] Critique 6: 'The published model has no activity of its own' holds by construction (l.95)
PAPER: l.95: "The model cannot walk by itself either. In a clean box with nothing to smell, two simulated females stood still for more than two minutes of brain time, every neuron at rest, because the published model has no activity of its own. … Walking, the most ordinary thing a fly does, was the first behaviour on my list that is not in the wiring."
VERDICT CONFIRMED headline=True
EVIDENCE: **By construction.** In brain/flybrain/lif.py:
- dv/dt = (v_0 − v + g)/τ_m with v_0 = v_rest = −52 mV, 7 mV below v_th = −45 mV (l.6, l.44-46).
- There is no intrinsic current, and noise_hz = 0.0 by default (l.54).
- The kernel integrates only neurons in the active set. That set starts empty and is filled only by kicks or synaptic arrivals (l.64-72, l.216-231).
- With zero input, every neuron therefore stays exactly at rest under any wiring, including the rewired nulls.
- The test_lif 'silence' rows in logs/reproduce_core-check.out confirm this: 0 spikes and 0.00 % active at dt 0.1, 0.2 and 0.5, in both numerics.

The absence of spontaneous activity is a property of the equations, so it cannot count as evidence about the wiring.

**The sentence's premise 'every neuron at rest' is also false in the logs.** All 20 female logs of the two-female clean box (5 original trials from 18-19 Sep plus 5 rep-clean trials from 26 Sep, fly1 and fly2; logs/fly*_off-flywire-known-eln0.25_20260918-23*, 20260919-013130, 20260926-01*) show:
- hz_total_spikes median 40,450–41,275 per 50-ms tick (brain_t_ms steps by 50), min 37,650
- hz_active_frac 0.08
- hz_dn_all 0.00, hz_mb_kc 0.00, ctl_walk 0.000

This activity is sensory drive: the photoreceptors are driven by luminance (senses.py l.58-59). Each female also smells the other: obs_smell_fly_L max 0.098–0.451 and obs_smell_co2_L max 0.0026–0.0149. So the box was not free of smell, and the brain was not silent.

The flies stood still because none of this input reached a descending neuron, not because nothing was firing.

**Effect on the conclusion.** 'Walking … not in the wiring' mixes up the wiring with a neuron model that has neither intrinsic activity nor noise. Spontaneous walking could not arise under any wiring. What the data do show is that the visual and faint-odour drive (8 % of neurons) never reaches the DNs.
WORDING: l.95: "The model cannot walk by itself either. In a clean box, with nothing to smell but each other, two simulated females stood still for more than two minutes of brain time. Their eyes kept about 8 % of the brain firing, but none of it reached a single descending neuron. The model neuron has no activity of its own: it rests 7 mV below threshold and has no noise, so nothing else could start the legs. A real fly put in an empty dish soon starts walking about \citep{martin2004portrait}. Walking, the most ordinary thing a fly does, was the first behaviour on my list that this model does not produce: the wiring does not carry what the fly sees to its walking neurons, and spontaneous activity was never in the model to begin with."

State 'no activity of its own' as a property of the model (for example in Note 1 or Note 11), not as a result.

>>> REFUTE [numerics] Critique 6: 'The published model has no activity of its own' holds by construction (l.95): upheld=True
EVIDENCE: I tried to refute the verifier and could not. Re-deriving the numbers confirms its core points, but part of its corrected wording goes too far the other way.

**Paper sentence (l.95):** "In a clean box with nothing to smell, two simulated females stood still for more than two minutes of brain time, every neuron at rest, because the published model has no activity of its own. ... Walking, the most ordinary thing a fly does, was the first behaviour on my list that is not in the wiring." l.125 repeats "every neuron at rest".

**1. "No activity of its own" is true by construction (CONFIRMED)**
- brain/flybrain/lif.py sets v_rest = v_reset = −52 mV and v_thr = −45 mV (l.44-46), and noise_hz = 0.0 (l.54).
- v starts at v_rest (l.302). Nothing is integrated unless it is in the active set.
- A neuron enters the active set only through a drive kick (forced_idx), a noise kick (noise_p > 0) or a synaptic arrival (l.229-241, l.258-276). Neurons back at rest are dropped from the set (l.114-124).
- So zero input gives zero spikes for any weight matrix W, including the rewired nulls.
- logs/reproduce_core-check.out l.5, 11, 18, 24 and 30 ('silence'): 0 spikes and 0.00 % active at every dt and in both numerics. This check cannot fail, so it is not evidence about the wiring.

**2. "Every neuron at rest" is false (CONFIRMED)**
I paired the logs through the frozen release/pre_rerun_20260926/results/encounter_trials.csv (chamber clean or rep-clean, condition ff). That gives 20 female logs: 10 original from 18-19 Sep and 10 replication from 26 Sep.
- hz_total_spikes per 50-ms tick (brain_t_ms steps by 50): median 40,450–41,275 per log, min 37,650, max 44,150.
- hz_active_frac: 0.08 on every row, with rare 0.07.
- Maximum of 0.0 in every log for hz_dn_all, dn_L, dn_R, turn_L, turn_R, dnp09, forward, mb_kc, mb_mbon, mb_dan, reject and sag.
- ctl_walk and ctl_turn are 0 throughout. The one 2.8-block displacement (rep t4, fly1) is a teleport at tick 2 with ctl_walk = 0.
- Brain time in the 10 original logs is 127–145 s (mean 135), so "more than two minutes" holds.

**3. "Nothing to smell" is false (CONFIRMED)**
- obs_smell_fly_L max 0.098–0.451 and obs_smell_fly_R max 0.135–0.648 per log.
- obs_smell_co2_L max 0.0026–0.0149.
- Food, cVA, aversive, sound, wind and speed are all 0.

**4. What the 8 % actually is — this is where the verifier's rewording overreaches**
- Photoreceptors (cell_type R1-6, R7, R8) in data/Supplemental_file1_neuron_annotations.tsv that are also among the model's 138,639 neurons (data/shiu/Completeness_783.csv): 10,582, which is 7.63 %.
- Every one of them has known_nt starting with histamine, except one with none. connectome.py l.72 (histamine = −1) and parse_known_nt (first token) make them inhibitory under the paper's 'known' sign rule.
- Adding the driven odour neurons (ORN_VA1v 94 and ORN_V 67) gives 10,743 neurons, 7.75 %. That rounds to the logged 0.08.
- 41,000 spikes per tick ÷ 10,743 ≈ 3.8 spikes per 50 ms, about 75 Hz. That is the luminance kick rate (at most 120 Hz, capped by the refractory period).
- The first tick, with zero fly smell, already has 43,794 spikes. Ticks with no fly smell (n = 408) have a median of 41,027; ticks with fly smell (n = 41,992) have 40,771. The odour adds nothing measurable.
- So the active 8 % is essentially the directly driven sensory neurons themselves. Given the rounding, at most about 1,000 other neurons could be firing, and possibly none.
- The photoreceptors are inhibitory, and this LIF model has no rebound or graded transmission, so visual drive can only silence its targets. It could not reach a descending neuron under any wiring, which again is by construction.
- The paper's own Methods (l.157) says vision is not modelled. RESEARCH_NOTES 14 and 19f say the LIF eye's drive "dies in the medulla" and "nothing at any DN".

The verifier's lines "Their eyes kept about 8 % of the brain firing" and "the wiring does not carry what the fly sees to its walking neurons" are therefore misleading. They imply visual activity spreading through the brain, and they swap one by-construction result presented as a wiring result for another.

**5. "Walking ... not in the wiring" is also overstated in scope**
- Walking does appear when a smell drives the steering neurons. Note 4 (l.143): food odour drives DNa01/02 at 20 / 12 Hz.
- l.101: a female "walked about on the male's pheromone".
- What is missing is walking of the fly's own accord, and that is absent because of the neuron model (no intrinsic current, no noise, rest 7 mV below threshold), not shown to be absent from the wiring.

**Headline: true.** This changes the conclusion "walking not in the wiring": it becomes a property of the neuron model, not a finding about the connectome.
WORDING: l.95: "The model cannot walk by itself either. In a clean box, with nothing to smell but each other, two simulated females stood still for more than two minutes of brain time. Their photoreceptors fired at the light of the white walls and each could faintly smell the other, but not one descending neuron fired. This is a property of the model rather than a finding about the wiring. A model neuron rests 7 mV below its threshold and has no noise and no currents of its own, so without input nothing in the brain starts, whatever the wiring. And in this model the photoreceptors are inhibitory and the eye beyond them is not modelled (Note 11), so what the fly sees cannot reach its legs either. A real fly put in an empty dish soon starts walking about \citep{martin2004portrait}. The model walks only when something, such as a smell, drives its steering neurons. Walking of its own accord, the most ordinary thing a fly does, was the first behaviour on my list that the model does not produce at all."

l.125: replace "every neuron at rest" with "no neuron beyond their eyes firing" (or "not one command to the legs").

Note 11 (Methods): add "The model has no spontaneous activity by construction: rest is 7 mV below threshold, there are no intrinsic currents and no noise (noise_hz = 0), so zero input gives zero spikes under any wiring. In the clean box the only firing neurons are the directly driven sensory neurons: about 10,600 photoreceptors (7.6 % of 138,639 neurons, all histaminergic and therefore inhibitory under the known-transmitter rule) and 161 fly-odour and CO2 receptor neurons, together 8 % of the brain."

Keep "Walking" out of the list of wiring results.

### [smell] 4a. eLN x0.25 is 'the most that keeps smells apart'
PAPER: l.91: "...so I turned their output down to a quarter, the most that keeps smells apart \note{3}."
VERDICT CONFIRMED headline=False
EVIDENCE: The frozen odor_code_flywire.csv (100 rows) and odor_code_malecns.csv (50 rows) hold only five variants: shiu (x1), known (x1), known+eln0.5, known+eln0.25 and known+eln0.1. No other eLN value appears in any frozen result filename. The finer sweep (0.15/0.2/0.3/0.35/0.4) is only planned (design_plan.md l.243, design_arms.json) and has no output (release/edge_20260927 does not exist). At x0.5 (female, known signs), 63-76 % of glomeruli are above 10 Hz per seed, 10-17 % of KCs are active and the between-odour KC Jaccard is 0.53 (0.66 over live odours). At x0.25 the between-odour value is 0.075. So 0.25 is the largest of four tested values that separates odours. Values from 0.3 to 0.45 were never tried.
WORDING: ...so I turned their output down to a quarter, the largest of the four settings I tried (1, 1/2, 1/4 and 1/10) that keeps smells apart; at a half, every odour still lights up about two-thirds of the glomeruli.

### [smell] 4b. '150 cholinergic local neurons'
PAPER: Note 3 (l.141): "Changes: the known transmitter where one is recorded (11{,}010 neurons, most of them photoreceptors) and the output of the 150 cholinergic local neurons $\times$\,0.25."
VERDICT CONFIRMED headline=False
EVIDENCE: brain/flybrain/connectome.py apply_model_options (l.124-127) defines eLNs as ALLN with a positive output row-sum after the sign rule, not by transmitter. data/Supplemental_file1_neuron_annotations.tsv has 429 ALLN. Their top_nt: ACh 80, GABA 147, Glu 148, 5-HT 40, DA 12, Oct 2. Their known_nt: ACh 44 (11 predicted ACh, 21 predicted 5-HT, 12 predicted DA) and GABA/Glu 16. RESEARCH_NOTES l.593-597 says 166 LNs are excitatory under Shiu signs: 72 predicted ACh, 40 5-HT, 12 DA, 40 GABA/Glu-predicted and 2 Oct. The known rule flips the 16 known GABA/Glu LNs (1 predicted ACh, 13 GABA, 2 5-HT), leaving 150. Reconstructed make-up of the 150: about 71 predicted ACh (47 %), 38 predicted 5-HT (21 recorded ACh), 12 predicted DA (all recorded ACh), 2 octopaminergic, and about 27 GABA/Glu-predicted. That gives about 71 cholinergic by prediction and about 104 (about 70 %) by prediction or record. About 27 are called inhibitory by the classifier. I did not recompute the row sums themselves because that needs the connectome loaded. The item's 'about half predicted cholinergic' is right for the classifier. RESEARCH_NOTES l.597 ('150 genuinely cholinergic') contradicts its own breakdown at l.593.
WORDING: ...and the output of the 150 antennal-lobe local neurons that the sign rule makes excitatory $\times$\,0.25 (about 70 of them predicted cholinergic and 33 more recorded as cholinergic; the rest are predicted serotonergic or octopaminergic, or come out excitatory by synapse vote despite a GABA/glutamate call).

### [smell] 4c. Overlaps 0.63 / 0.08 include empty KC codes
PAPER: Note 3 (l.141): "...with overlaps of 0.63 within and 0.08 between odours."
VERDICT PARTLY headline=False
EVIDENCE: experiments/odor_code.py l.79 computes Jaccard as |A∩B|/max(|A∪B|,1), so two empty codes score 0 instead of being undefined. odor_code_flywire.csv, known+eln0.25: kc_active is 0 in both seeds for VA1v and DA2. VM2 is 0.000773, i.e. 4 of 5,177 KCs, and its same-odour Jaccard is 1.0. odor_code_flywire_overlap.csv, known+eln0.25: over all 10 odours, within = 0.634 and between = 0.075 (the paper's 0.63 / 0.08; the two empty odours add same-odour values of 0.000). Excluding the 2 empty odours gives within 0.793 (n=8) and between 0.121 (median 0.045). Also excluding VM2 gives 0.763 / 0.159, the item's 0.76 / 0.16. What holds: empty codes pull both values down, and the real between-odour overlap is higher than 0.08. What does not: the item says '3 of 10 test odours reach no KCs', but only 2 reach none and VM2 reaches 4.
WORDING: Two of the ten test odours (VA1v, DA2) reach no Kenyon cell and a third (VM2) reaches only four; over the eight odours that reach any, the overlap is 0.79 within and 0.12 between odours (0.63 and 0.08 if empty codes are scored as zero overlap).

### [smell] 4d. '18 %' of glomeruli is the mean of a bimodal set
PAPER: Note 3 (l.141): "After them a single odour drives 18\,\% of glomeruli and 0--5\,\% of Kenyon cells, as in real flies \citep{honegger2011cellular}..."
VERDICT CONFIRMED headline=False
EVIDENCE: odor_code_flywire.csv, known+eln0.25, glomeruli_over_10hz averaged over 2 seeds. Six odours sit at 22.9-28.0 % (13.5-16.5 of 59 glomeruli): DM2 23.7, DL5 25.4, DA1 26.3, DM1 22.9, V 26.3, DC3 28.0 %. Three sit at 1.7-3.4 % (1-2 glomeruli, i.e. essentially only the cognate one, whose PNs fire at 38-102 Hz): VA1v 3.4, VM2 1.7, DA2 1.7 %. The food blend is 19.5 %. The mean of the 10 is 17.9 % (17.7 % over the 9 single odours), and no odour is near 18 %. KC active ranges from 0 to 5.5 % (the blend); single odours are 0-2.7 %.
WORDING: After them six of nine single odours drive 23--28\,\% of glomeruli and the other three only their own one or two (the food blend 20\,\%), and 0--5\,\% of Kenyon cells...

### [smell] 5. 'I report every smell result both ways'
PAPER: l.91: "I report every smell result both ways, and nothing that does not involve smell depends on the change."
VERDICT CONFIRMED headline=False
EVIDENCE: Only four smell results are given under both settings: the odour code (Note 3), the arena (Fig 3) and the approach index (Note 9, -0.19 / +0.08), plus the claim that the states are identical. Four are given under one setting only. (1) Learning: every conditioning file behind Note 7 is flywire +known+eln0.25 (with eln0.1 extras) or malecns+eln0.25. The one published-lobe file, conditioning_flywire_shiu_min1_noise0_seed0.csv (old protocol), shows MBON 81.6 -> 32.9 Hz for CS+ and 81.1 -> 32.75 for CS-, a drop of 48.7 vs 48.4, so there is no odour-specific memory. It is not reported. (2) The freeze: Note 4 gives only the changed-lobe values (contact_stop_flywire.csv: 20.3/12.3 -> 6.8/3.2, cVA 9.3/8.2 -> 0/1.2). Under 'published model: Shiu signs, eLN x1' the index is 0.35-0.51 without the hum and 0.42-0.59 with it, and DNa L stays at 15-24 Hz with touch. This is only folded into the range '0.35--0.93'. (3) Male cVA 'every other odour 0' comes from social_probe_malecns_all_min1+eln0.25 only. Under the published male (social_probe_malecns_all_min1_noise0), every odour drives MN9 at 19.3-21.6 Hz (cVA 27.1) and cVA drives DNp13 at 24.5. (4) Dose rows: odor_dose files exist only for eln0.25 variants (shiu_min1+known+eln0.25, shiu_min1+eln0.25, zenodo_min1+known+eln0.25, malecns+eln0.25). The 'published signs' row in Note 5 is Shiu signs x0.25, not the published smell centre. The cVA 0.6-2.3 Hz turn is under my change only. Not headline by itself, but the odour-specific memory in 'memory forms but is not expressed' holds only with the smell-centre change.
WORDING: I report the smell centre, the arena and the internal states both ways; the learning, the touch freeze, the male's cVA response and the odour-strength results are for my change only (under the published smell centre training weakens both odours alike, the freeze index is 0.35--0.59, and every odour drives the male's MN9 at 19--22\,Hz).

### [smell] 6. 'Nothing that does not involve smell depends on the change' (gain 1.4, male)
PAPER: l.91: "I report every smell result both ways, and nothing that does not involve smell depends on the change."
VERDICT CONFIRMED headline=False
EVIDENCE: Compared gain_sweep_{flywire_shiu_min1 (3 seeds), flywire_shiu_min1+known+eln0.25 (5 seeds), malecns_all_min1 (3), malecns_all_min1+eln0.25 (5)} on the non-smell inputs: JO-A, JO-B, head touch, sugar, and in the male also ppk25 and ppk23/25. Gain 0.5-0.7: max difference 5.1 Hz (female sugar->MN9 37.8 vs 32.7 at 0.7); male at most 0.6. Gain 1.0, female: max 4.6 Hz in the sweep (sugar->MN9 80.6 vs 76.0). But in social_probe_flywire_shiu_min1_noise0, sugar seed 4 ignites the published lobe: 284,010 vs about 24,000 spikes, PPL1 61, PAM 11, KC 17.5, DNa L 19.5 and MN9 58 against 78-81 in the other seeds. Under my change 0 of 5 seeds ignite. Gain 1.0, male: sugar->PAM 13.3 vs 0, PPL1 48.7 vs 11.7, KC 10.1 vs 0 and song MNs 4.4 vs 0. Two of 3 published seeds ignite in the sweep and 3 of 5 in social_probe_malecns_all_min1_noise0; 0 of 5 do under eln0.25. Gain 1.4, female: touch->DNp13 19.2 vs 42.0, DNa L 27.5 vs 2.0, MDN 0.8 vs 6.0, PPL1 133.5 vs 0 and KC 49.5 vs 0 (all 3 seeds). Sugar->MN9 63.9 vs 94.3, DNa L 15.8 vs 4.2 and PPL1 55.1 vs 0 (2 of 3 seeds). Gain 1.4, male: touch->PAM 14.2 vs 0, PPL1 45.0 vs 18.3, KC 12.3 vs 0, with MDN unchanged (11.9 vs 11.8). Sugar->pIP10 8.6 vs 0 and song MNs 21.5 vs 3.3. Gain 2.0: every non-smell input differs in both sexes (female sugar->MN9 35.6 vs 107.3). One consequence: Note 7's 'Sugar, bitter and touch drive 0.0 Hz in every dopamine neuron' is itself a non-smell result that depends on the change. The item's 'holds qualitatively at gain <=1.0' is slightly generous: it holds within 5 Hz at <=0.7, and at 1.0 only in the female's 3-seed sweep.
WORDING: At the published synapse strength in the female, and at 0.7 in both sexes, nothing that does not involve smell depends on the change (every such readout within 5\,Hz). Above that, taste and touch can set off the published smell centre. In the male this already happens at 1.0 (sugar drives the punishment dopamine neurons at 49 against 12\,Hz), and in one of five female runs with sugar at 1.0. In the female at 1.4, touch drives DNp13 at 19 against 42\,Hz and left steering at 27.5 against 2, and sugar drives MN9 at 64 against 94.

### [reflexes] 7. The freeze: how widely it was tested, and where the reversal was measured
PAPER: l.93: "The freeze survives every one of my alternatives but one: remove the connections made of fewer than five synapses, a common way of tidying a wiring diagram, and touch excites the steering neurons instead, so the freeze is carried by the weakest connections in the brain." Note 4: "the index is 0.69--0.93 from gain 1.0 to 2.0 and 0.35--0.93 in every condition that drives the DNa at all, and reverses only under the $\geq 5$-synapse threshold."
VERDICT CONFIRMED headline=False
EVIDENCE: All files are in release/pre_rerun_20260926/results/.

(1) Scope. contact_stop_flywire.csv has 56 rows and 16 condition labels. These are 8 connectome variants, each with and without the 0.2 Hz hum: shiu_min1+known+eln0.25, shiu_min1, shiu_min1+known, shiu_min1+eln0.25, shiu_min1+known+eln0.5, shiu_min1+known+eln0.1, zenodo_min5+known+eln0.25 and zenodo_min1+known+eln0.25. The CONDITIONS list in experiments/contact_stop.py matches. The paper's 14 female alternatives are the 14 rows of sensitivity_flywire_shiu_min1+known+eln0.25.csv. Six of them were never run with touch on a walking drive: stimulus 50 Hz, stimulus 150 Hz, dt 0.1, dt 0.5, legacy numerics, and 'connections >= 5 synapses' (shiu_min5+known+eln0.25). The sensitivity file has only 'food + touch -> DNp13'; it has no food+touch -> DNa column.

(2) Gains. gain_sweep_flywire_shiu_min1+known+eln0.25.csv, 5 seeds. Index = 1 - mean(DNa L,R) with touch / mean(DNa L,R) without.
- Gain 1.0: food 16.33 -> 5.00 (0.69); cVA 8.75 -> 0.58 (0.93).
- Gain 1.4: food 32.33 -> 8.25 (0.74); cVA 27.92 -> 3.08 (0.89).
- Gain 2.0: food 24.92 -> 3.50 (0.86); cVA 26.75 -> 2.00 (0.93).
- Gain 0.7: food drives DNa at 0.08 Hz and cVA at 0.0, so there is nothing to freeze. Gain 0.5 is all zeros.
The freeze can therefore only be tested at gain 1.0 or above.

(3) Reversal. It appears only in the zenodo_min5+known+eln0.25 rows (42-48):
- food: 19.17 -> 17.58 (index 0.08; L 27.8 -> 17.3, R 10.5 -> 17.8); with the hum, 0.05;
- cVA: 0 -> 12.33; Or47b: 0 -> 12.25;
- with the hum: cVA -1.86, Or47b -1.91, hum alone 5.42 -> 13.58 (-1.51).
The same Zenodo table with all connections still freezes (food 0.71, food+hum 0.70, hum alone 0.78). The paper's own table with the threshold (shiu_min5) was never run for the freeze. So the reversal was measured only on the Zenodo top_nt-sign table. design_critique.md says that table has the same connections as Shiu's and differs only in signs. I did not re-check that, because it would mean loading a connectome.

(4) Food drive. With food, the threshold removes the freeze but touch does not excite DNa on average (0.08 / 0.05). 'Touch excites the steering neurons instead' holds only for the cVA, Or47b and hum-only drives.

(5) Index range. Outside zenodo_min5, and where DNa alone is above 1 Hz, the index is 0.355-0.933. There is one extra row: Zenodo all-connections with cVA and no hum drives DNa at only 0.58 Hz and gives an index of 0.00.

(6) Wording. One removal experiment shows that the freeze depends on these connections, not that it is 'carried by' them. DNp09 is 0-0.67 Hz in every row, so the freeze is DNa suppression only.
WORDING: l.93: "The freeze held in seven of the eight wiring variants I ran it in (four sign and smell-centre settings, two strengths of the smell-centre change and two connection tables, each with and without the hum) and at every strength from 1.0 to 2.0; below 1.0 the smell no longer drives the steering neurons, so there is nothing to freeze. I did not run it at other stimulus rates, time steps or numerics. In the Zenodo version of the table, removing connections of fewer than five synapses abolishes it, and touch then excites the steering neurons when a pheromone or the hum drives them. So the freeze depends on the weakest connections, at least under that table's signs; I have not applied the threshold to the table the paper uses." Note 4: "...index 0.69-0.93 from gain 1.0 to 2.0 in the paper's model (DNa is not driven below 1.0) and 0.35-0.93 in the other seven variants, with and without the hum, wherever the drive gives DNa above 1 Hz. It is lost only under the >=5-synapse threshold of the Zenodo table (food 0.08; with cVA, Or47b or the hum alone, touch drives DNa to 12-14 Hz). The freeze was not run at other stimulus rates, time steps or numerics, or under the threshold on Shiu et al.'s table. Female walking is read from DNa01/02 + DNp09, and DNp09 is 0-0.7 Hz throughout, so the freeze is DNa suppression."

### [reflexes] 8. Male: "no other smell at all" / "every other odour 0"
PAPER: l.93: "The male brain answers the smell of cVA, a pheromone that males make, and no other smell at all." Note 4: "Male: cVA $\rightarrow$ DNp13 7.8 / 30 / 26\,Hz and MN9 7.5 / 32.5 / 36.5\,Hz, every other odour 0;"
VERDICT CONFIRMED headline=False
EVIDENCE: (1) Paper's model, gain 1.0. social_probe_malecns_all_min1+eln0.25_noise0.csv, 3 seeds, means per input.
- DNp13: 0.00 for all 7 other odours (cVA-long/Or65a, Or47b, Or88a, Or83c, food, CO2, aversive), against 31.3 for cVA.
- MN9: cVA-long 2.83, Or83c 1.67, CO2 1.67, aversive 1.33, others 0, against cVA 32.7.
- aSP22: cVA-long 11.7, Or83c 10.2, Or88a 9.5, CO2 8.7, aversive 4.0, Or47b 2.3, against cVA 5.3.
- PPL1: food 1.9.

(2) Gain sweep. gain_sweep_malecns_all_min1+eln0.25.csv, 5 seeds.
- DNp13 is 0 for every other odour at every gain from 0.5 to 2.0.
- Gain 1.0: MN9 aversive 1.50, CO2 1.83.
- Gain 1.4, other odours: PPL1 18.4 (Or88a) to 30.1 (food); song MNs 5.0-9.6; MDN 0 (food) to 5.3 (CO2). The item's 'MDN 1-5' should read 0-5.
- Gain 0.7: other odours are 0 on every readout.

(3) Dose. odor_dose_malecns_all_min1+eln0.25.csv, 25-150 Hz: DNp13 is 0 for every non-cVA odour at every dose. MN9 is 0-3.6 Hz (sweet 3.56, ester 2.22, food 2.0 at low doses).

(4) Published lobe (eLN x1).
- social_probe_malecns_all_min1_noise0.csv: MN9 19.3-21.6 Hz for all 7 other odours (cVA 27.1); DNp13 0-1.0; PPL1 113-124.
- gain_sweep_malecns_all_min1.csv at gain 1.0: MN9 18.3-20.6; DNp13 0-1.7 (cVA 24.7).

The claim holds for DNp13 only. The 'every other odour 0' attached to MN9 is wrong in the paper's model (up to about 3 Hz) and badly wrong under the published lobe, which the paper says it reports 'both ways'.
WORDING: l.93: "In the male, the rejection neuron DNp13 answers the smell of cVA, a pheromone that males make, and no other smell." Note 4: "Male: cVA -> DNp13 7.8 / 30 / 26 Hz and MN9 7.5 / 32.5 / 36.5 Hz. Every other odour gives DNp13 0 at every gain and at 25-150 Hz. They are not silent elsewhere: MN9 up to 3 Hz at gain 1.0; at 1.4, PPL1 18-30, song motor neurons 5-10 and MDN 0-5 Hz. Under the published smell centre every odour drives MN9 at 18-22 Hz, and only DNp13 stays specific to cVA."

### [reflexes] 9. MDN (backing) gain-window failures for leg taste and head touch
PAPER: l.93: "When his legs touch a female his backward-walking neurons fire, the ``moonwalker'' neurons of \citet{bidaye2014neuronal}, though this reflex is the weakest of the set and fails the gentlest version of my first test." Note 4: "and $\rightarrow$ MDN 27\,Hz at gain 1.0 only; head bristles $\rightarrow$ MDN 0 / 10.7 / 11.8\,Hz." (Also l.121: "the fly's map already holds a good deal: ... how to freeze when touched and how to back away.")
VERDICT CONFIRMED headline=True
EVIDENCE: (1) Gain sweep. gain_sweep_malecns_all_min1+eln0.25.csv, MDN back, mean of 5 seeds at gain 0.5 / 0.7 / 1.0 / 1.4 / 2.0:
- contact pheromone (ppk23/25): 0 / 0 / 26.83 / 1.83 / 0
- ppk25 only: 0 / 0 / 14.33 / 6.08 / 1.50
- head touch: 0 / 0 / 10.67 / 11.83 / 8.58
- cVA+touch: 0 / 0 / 25.92 / 6.92 / 4.00
- food+touch: 0 / 0 / 3.08 / 6.42 / 5.42
At gain 0.7 every input gives MDN 0.00. Leg taste therefore fails at both 0.7 and 1.4; head touch fails at 0.7.

(2) Sensitivity. sensitivity_malecns_all_min1+eln0.25.csv:
- touch -> MDN: 0.00 at stimulus 50 Hz; baseline 11.5, 150 Hz 27.5, dt 0.5 8.2, legacy numerics 35.7.
- contact pheromone -> MDN: 2.5 under legacy numerics, 6.5 at >=5 synapses, 24-32 in the other rows.

(3) Odour context. social_probe_malecns_all_min1+eln0.25_noise0.csv, gain 1.0, MDN with touch: Or47b+touch 2.75, food+touch 4.00, touch alone 10.67, cVA+touch 21.58, ppk25+touch 22.42, CO2+touch 46.75, all pheromones+contact+touch 58.75.

(4) Published lobe. contact_stop_malecns.csv under eLN x1:
- food/cVA/Or47b + touch: 0.00.
- with the hum: touch alone 2.33 and ppk25+touch 2.50, against 17.67 and 29.08 in the paper's model with the hum.

(5) Arena. brain/flybrain/senses.py l.193-200 drives grn_ppk25 plus every head bristle on contact with a female. The arena's backing is therefore ppk25+touch, and both of its parts are 0 at gain 0.7.

The paper's sentence is true about leg taste, but it names one route. Both routes fail the ±1/3 test, head touch also fails the stimulus-rate row and the published lobe, and l.121 still counts backing as held by the map.
WORDING: l.93: "When his legs touch a female his backward-walking neurons fire, the moonwalker neurons of Bidaye et al., but this reflex fails my tests. With every synapse turned down by a third it is gone, whether he tastes her with his legs or is touched on the head (0 Hz at gain 0.7). Through leg taste it is also gone when synapses are turned up (1.8 Hz at 1.4). Through head touch it is gone at a 50 Hz stimulus and under the published smell centre, and its size depends on what he smells (3-47 Hz). The backing in the box is a property of this model at its published strength, not a reflex I can call the wiring's." Note 4: "leg taste (ppk23/25) -> MDN 0 / 27 / 1.8 Hz; head bristles -> MDN 0 / 10.7 / 11.8 Hz, 0 at a 50 Hz stimulus, 3-47 Hz depending on the odour present, and 0-2.3 Hz under the published smell centre." l.121: drop "and how to back away", or write "how to freeze when touched (and, at the published strength only, how to back away)".

### [reflexes] 12. Wing motor neurons "10-22 Hz" and their specificity
PAPER: Note 4 (header "gain 0.7 / 1.0 / 1.4"): "leg taste (ppk23/25) $\rightarrow$ wing motor neurons 10--22\,Hz,"
VERDICT CONFIRMED headline=False
EVIDENCE: (1) Range. gain_sweep_malecns_all_min1+eln0.25.csv: contact pheromone (ppk23/25) -> 'song MNs' is 9.88 / 20.00 / 21.55 / 11.31 / 11.62 Hz at gain 0.5 / 0.7 / 1.0 / 1.4 / 2.0. The paper's own check (experiments/paper_numbers.py l.112) expects '10 / 20 / 22 / 11' at 0.5 / 0.7 / 1.0 / 1.4. So the '10' is gain 0.5, outside the note's stated gains; at 0.7-1.4 the range is 11-22 Hz.

(2) Specificity at gain 1.0. social_probe_malecns_all_min1+eln0.25_noise0.csv, song MNs (ps1/i1/i2/hg MNs, experiments/common.py l.79):
- wind (JO-CE) 13.95, cVA 12.62, head touch 10.10, JO-B 5.10;
- ppk25 alone 12.90, ppk23 alone (the male's own hydrocarbon) 22.86;
- contact pheromone 21.50.

(3) Specificity at gain 1.4 (gain sweep): touch 22.62, food+touch 20.69, cVA 14.71, JO-B 11.12, odours 5-10, against ppk23/25 11.31. Head touch drives these neurons twice as hard as leg taste does.

(4) Other readouts. The broader 'wing MNs' readout (all wm motor neurons) is more selective at gain 1.0: contact pheromone 30.45, against wind 6.45, cVA 4.93, touch 2.59, ppk25 alone 7.14. It still gives ppk23 alone 23.09, and it is not in the gain sweep.

(5) Sensitivity. sensitivity_malecns_all_min1+eln0.25.csv: contact pheromone -> song MNs 5.0 under legacy numerics, 12.7 at >=5 synapses, 18-22 in the other rows.
WORDING: Note 4: "leg taste (ppk23/25) -> wing (song) motor neurons 20 / 22 / 11 Hz. This is not specific to leg taste: at gain 1.0 wind gives 14, cVA 13 and head touch 10 Hz, and at 1.4 head touch gives 23 Hz. Over all wing motor neurons, contact pheromone gives 30 Hz against at most 7 for non-contact inputs." Alternatively, drop it from the list of reflexes.

>>> REFUTE [reflexes] 9. MDN (backing) gain-window failures for leg taste and head touch: upheld=True
EVIDENCE: VERDICT: CONFIRMED, with three corrections to the verifier's replacement wording. headline=true, because l.121 lists backing among the reflexes the map holds. The arena observation "males back out" still stands as something the model does at gain 1.0.

Paper sentences checked. l.93: "When his legs touch a female his backward-walking neurons fire, the ``moonwalker'' neurons of \citet{bidaye2014neuronal}, though this reflex is the weakest of the set and fails the gentlest version of my first test." Note 4: "and $\rightarrow$ MDN 27\,Hz at gain 1.0 only; head bristles $\rightarrow$ MDN 0 / 10.7 / 11.8\,Hz." l.121: "...how to freeze when touched and how to back away." l.89 defines "in the wiring" as passing all three tests.

All numbers below come from the frozen copy, release/pre_rerun_20260926/results/.

(1) Gain sweep, gain_sweep_malecns_all_min1+eln0.25.csv. Column "MDN back", 5 seeds per cell, pivoted as input x gain (mean) at gains 0.5 / 0.7 / 1.0 / 1.4 / 2.0:
- contact pheromone (ppk23/25): 0 / 0 / 26.83 / 1.83 / 0 (per-seed values at 1.4: 0.4-2.9)
- ppk25 only: 0 / 0 / 14.33 / 6.08 (SD 3.20) / 1.50
- head touch: 0 / 0 / 10.67 / 11.83 / 8.58
- cVA+touch: 0 / 0 / 25.92 / 6.92 / 4.00
- food+touch: 0 / 0 / 3.08 / 6.42 / 5.42
Every input gives exactly 0.00 at gain 0.7, in all 5 seeds. The verifier's numbers are exact.

(2) Sensitivity, sensitivity_malecns_all_min1+eln0.25.csv, 13 rows:
- touch->MDN: 11.53 baseline; 0.00 +/- 0.00 at a 50 Hz stimulus; 27.50 at 150 Hz; 14.86 at dt 0.1; 8.19 at dt 0.5; 35.69 under legacy numerics; 15.97 at >=5 synapses.
- ppk23/25->MDN: 2.50 under legacy numerics, 6.53 at >=5 synapses, 24.3-31.7 in the other rows.
- The eLN x1/x0.5/x0.1 and unclear-LN rows are identical to baseline for both inputs (11.53 and 29.17).

(3) Odour context, social_probe_malecns_all_min1+eln0.25_noise0.csv (3 seeds): Or47b+touch 2.75, food+touch 4.00, touch 10.67, cVA+touch 21.58, ppk25+touch 22.42, CO2+touch 46.75, all pheromones+contact+touch 58.75.

(4) Published lobe, contact_stop_malecns.csv:
- eLN x1, no hum: food/cVA/Or47b + touch all 0.00; ppk25+touch 23.00, the same as the paper's model.
- eLN x1 with the 0.2 Hz hum: touch 2.33, ppk25+touch 2.50, against 17.67 and 29.08 in the paper's model with the hum.

(5) Rewiring passes, shuffle_malecns_all_min1+eln0.25_global.csv: MDN at most 4.4 Hz, as Note 2 says.

(6) Arena input, brain/flybrain/senses.py l.193 and l.199-200: touching a female drives grn_ppk25 (ppk25 only, at R_TASTE 150 Hz) plus every bristle (R_BURST 200 Hz).

Where the paper holds up: l.93 is literally true for the route it names. ppk23/25->MDN fails on both sides of the first test (0 at 0.7, 1.8 at 1.4), and Note 4 already prints head touch as 0 / 10.7 / 11.8. The sentence is incomplete rather than false:
- the main text does not say that head touch also fails at 0.7;
- it leaves out the failures in test 3 (touch is 0 at 50 Hz; leg taste is 2.5 Hz under legacy numerics and 6.5 at >=5 synapses);
- it leaves out the odour dependence.
The real overstatement is l.121. It counts "how to back away" as held by the map, although by the paper's own rule at l.89 backing is not in the wiring.

Where the verifier's replacement wording goes too far:
(a) "Through head touch it is gone ... under the published smell centre" is not general. Under eLN x1 with no odour and no hum, touch alone gives 11.53 Hz (sensitivity row 6). The published lobe silences MDN only when an odour is present (0.00) or the hum is on (2.33). The same collapse hits the arena's leg-taste route, ppk25+touch: 2.50 with the hum, 23.00 without. So it is not specific to head touch.
(b) "Through leg taste it is also gone when synapses are turned up (1.8 Hz at 1.4)" is true for the pooled ppk23/25 stimulus. For ppk25 alone, which is what the arena delivers, the response falls from 14.3 to 6.1 Hz: halved, not gone.
(c) "A property of this model at its published strength" is too narrow for head touch, which persists at 1.4 and 2.0 (11.8 and 8.6). Only turning synapses down kills it. The accurate phrase is "at the published strength or above".
The "3-47 Hz" odour range is correct (2.75-46.75).
WORDING: l.93: "When his legs touch a female his backward-walking neurons fire, the ``moonwalker'' neurons of \citet{bidaye2014neuronal}, and so do they when his head is touched. But this is the weakest reflex of the set and it fails my first test. Turn every synapse down by a third and it is gone by either route (0\,Hz at gain 0.7), and his leg taste alone barely drives it when synapses are turned up (1.8\,Hz at 1.4). Through the head it needs a strong touch (0\,Hz at a 50\,Hz stimulus), its size depends on what he smells (3--47\,Hz), and under the published smell centre any smell or the hum silences it. So I count backing as a property of this model at the published strength or above, not as a reflex of the wiring."

Note 4: "...leg taste (ppk23/25) $\rightarrow$ wing motor neurons 10--22\,Hz, and $\rightarrow$ MDN 0 / 27 / 1.8\,Hz (ppk25 alone, the arena's input: 0 / 14 / 6.1); head bristles $\rightarrow$ MDN 0 / 10.7 / 11.8\,Hz, 0 at a 50\,Hz stimulus, 2.8--47\,Hz depending on the odour present, and 0--2.5\,Hz under the published smell centre whenever an odour or the hum is present (11.5\,Hz for touch alone in a silent brain)."

l.121: "...how to eat, how to jump, how to groom and how to freeze when touched." Alternatively keep "(and, at the published strength and above, how to back away)".

### [shuffle] 10a. Which null the paper used: the global degree-preserving null silences every input
PAPER: l.89: "It has to survive every synapse being turned up or down by about a third, vanish when the brain is rewired at random with every neuron keeping its number of connections, and hold under every reasonable alternative to my own choices, fourteen versions of the female model and thirteen of the male \note{2}." Note 2: "degree-preserving rewiring \citep{maslov2002specificity}, which moves 99.8\,\% of connections and leaves every readout at 0--2\,Hz (largest stray value 7\,Hz)"
VERDICT CONFIRMED headline=True
EVIDENCE: Files: release/pre_rerun_20260926/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv (3 rewirings x 3 seeds x 8 inputs), shuffle_flywire_shiu_min1_global.csv, shuffle_malecns_all_min1+eln0.25_global.csv (2 rewirings), shuffle_flywire_shiu_min1_block.csv (2 rewirings). The live experiments/results copies are numerically identical (only wall_s differs). Global null (paper's lobe), frac_moved 0.99857-0.99859: every input drives 'DN all' at 0.00-0.13 Hz mean, max 0.15 Hz in any rewired row. Touch (n_driven 1,417) gives DN all 0.13 against 8.06 intact, and active_frac 0.0147. That is about 2,050 of 139,255 neurons, roughly the 1,417 driven ones plus about 600 more. Male global (frac 0.9981): DN all at most 0.11 Hz. Pooled rewired means are at most 2.12 Hz (female, food odour->MDN) and 2.19 Hz (male, ppk23/25->DNp13). Per-brain means reach 6.35 Hz (female rewiring 2, food->MDN); single runs reach 7.19 Hz (female) and 5.0 Hz (male). So the paper's '0-2 Hz (largest stray 7 Hz)' is right as a pooled figure. It holds because this null stops all sensory-to-descending transmission, not only specific reflex routes. shuffle_control.py shows that --mode block is also degree-preserving: it swaps targets only within the same super_class. So 'degree-preserving' and 'every neuron keeping its number of connections' describe both nulls. Only the '99.8 %' (block moves 94.3 %) tells the reader which one was used, and the block null is never mentioned.
WORDING: l.89: "...vanish when the brain is rewired at random, any neuron to any other, with every neuron keeping its number of connections (a rewiring that stops every sense from reaching the descending neurons at all)..." Note 2: "unconstrained degree-preserving rewiring (Maslov & Sneppen 2002), which moves 99.8 % of connections. Because no sensory input then reaches a descending neuron (all DNs <= 0.15 Hz even with the 1,417 head bristles driven, against 8.1 Hz intact), every readout averages 0-2 Hz (largest single value 7 Hz). It shows that the responses need real wiring, but not which wiring."

### [shuffle] 10b. Reflexes never read in any rewired brain (grooming, bitter suppression, wing/song MNs)
PAPER: l.93: "Scramble the wiring and every one of these reflexes disappears." Note 4: "Every readout 0--2\,Hz in a rewired brain."
VERDICT CONFIRMED headline=False
EVIDENCE: Female shuffle files: the inputs are none, cVA, cVA+touch, food odor, JO-A, JO-B, sugar GRNs and touch. There is no bitter input, no sugar+bitter, no JO-CE (wind), and no aBN1 column. The male shuffle file adds ppk23/25 and ppk25+touch, but its readouts are pIP10 plus the shared set, with no 'song MNs' column. aBN1 is read only in benchmark_flywire*.csv, and JO-CE and bitter appear as inputs only in benchmark_* and social_probe_* (gain 1.0, intact). The l.93 paragraph lists sugar->mouthparts, bitter->stop, sound->jump, wind->groom, touch->ovipositor, the freeze, male cVA and male leg-touch->MDN. Two of these (bitter stop, wind grooming) were never measured under rewiring. Note 4's wing MNs 10-22 Hz were not measured either. The freeze could not be measured under the global null: DNa is 0.00 under cVA and food odour, so there is no drive left to suppress, and food+touch was not in the shuffle input set. Reflexes that were read and do vanish: sugar->MN9 75.8->0.00, JO-A->GF 10.62->0.00, touch->DNp13 35.42->0.00, cVA->DNa 10.2/7.3->0.00 (female, paper's lobe); male cVA->DNp13 31.9->0.00, cVA->MN9 33.1->0.00, ppk23/25->MDN 28.4->0.00, head touch->MDN 10.8->1.5.
WORDING: l.93: "Rewire the brain at random and every one of these reflexes that I measured disappears (I did not measure grooming or bitter suppression in a rewired brain)." Note 4: "Every readout measured in a rewired brain is 0-2 Hz on average; aBN1, bitter suppression and the male's wing motor neurons were not measured there."

### [shuffle] 10c. Class-preserving (block) null keeps part of the sound and touch reflexes
PAPER: l.93: "Scramble the wiring and every one of these reflexes disappears."
VERDICT CONFIRMED headline=True
EVIDENCE: shuffle_flywire_shiu_min1_block.csv: published female model only, 2 rewirings x 3 seeds, frac_moved 0.9435/0.9434. Values are means over the 6 rewired runs against the 3 intact seeds. JO-A->GF 6.35 Hz (per rewiring 5.2 and 7.5; single runs 4.4-7.5) against 10.62 intact, so 60 % remains. JO-B->GF 0.31 against 4.79. Touch->GF 77.7 (intact 0.0), MDN 31.9 (0.7), DNa L/R 54.6/49.1 (0.0/0.6), DNp13 11.25 (36.67, 31 % remains), feed MNs 22.06 (15.71), DN all 14.65 (8.04). cVA+touch gives the same (GF 80.8, MDN 31.4). Sugar->MN9 0.00 against 80.4, cVA->DNa 0/0 against 36.3/3.5, food->DNa 0.8/0.5 against 36.0/4.8. The item's numbers (6.4 vs 10.6, GF 78, MDN 32) reproduce. No block null exists for the paper's modified lobe or for the male. This block run supports input-output specificity for sugar and smell. It does not support 'every reflex disappears': the sound reflex mostly survives, and touch still drives DNp13 at a third of its rate inside a non-specific burst.
WORDING: Add after the l.93 sentence: "In a stricter rewiring that keeps each connection within its broad cell class, sugar and smells still reach nothing, but a sound still drives the escape neuron at about 60 % of its normal rate (6.4 against 10.6 Hz), and touch sets off an indiscriminate burst: escape 78 Hz, backward walking 32 Hz, both steering neurons 50-55 Hz, the ovipositor neuron at a third of its rate." Add to Note 2: "class-preserving rewiring (published model, 94 % of connections moved, 2 rewirings): sugar->MN9 0, smells->DNa <= 1 Hz, JO-A->GF 6.4 against 10.6 Hz, touch->GF 78, MDN 32, DNa 55/49, DNp13 11 (37 intact)."

### [shuffle] 11a. The three tests presented as a filter every reflex passes; grooming and bitter suppression never went through any of them
PAPER: l.89: "Because a simulation always does something, a behaviour counts as ``in the wiring'' here only if it passes three tests." l.93: "With the wiring alone, the fly has reflexes \note{4}. Sugar makes it work its mouthparts, and bitter makes it stop. A sound fires its escape jump. Wind on the antenna makes it groom." Closing (l.119): "the fly's map already holds a good deal: how to eat, how to jump, how to groom, how to freeze when touched and how to back away."
VERDICT CONFIRMED headline=True
EVIDENCE: Gain test: gain_sweep_flywire_shiu_min1+known+eln0.25.csv and gain_sweep_flywire_shiu_min1.csv have 13 inputs. None is bitter, sugar+bitter or JO-CE, and there is no aBN1 column. Rewiring: see 10b; no bitter, JO-CE or aBN1 in any shuffle_*.csv. Sensitivity: sensitivity_flywire*.csv and sensitivity_malecns*.csv have no aBN1, bitter or JO-CE column. The only measurements are benchmark_flywire.csv and benchmark_flywire_shiu_min1+known+eln0.25.csv. benchmark.py takes only --seeds and --ms, so these are gain 1.0, 100 Hz, dt 0.2, 3 seeds, and the two files differ only in the smell centre. There, JON-CE->aBN1 is 12.7 / 13.3 Hz, and sugar 55.0 -> 3.3 Hz with bitter 100 Hz (published lobe 57.7 -> 6.3). The paper's own exceptions are acknowledged: male leg-touch->MDN fails test 1, and the freeze reverses at >= 5 synapses. Grooming and bitter suppression are presented as passing without ever being tested.
WORDING: l.89, after the three tests: "Two of the reflexes below, grooming and the suppression of feeding by bitter, reproduce Shiu et al.'s results but I did not put them through these tests." l.93: "Wind on the antenna makes it groom, as Shiu et al. found (untested here for robustness)." Closing: "how to eat, how to jump, how to freeze when touched and how to back away, and, on Shiu et al.'s evidence, how to groom." Note 2: "Grooming (JO-CE->aBN1) and bitter suppression were measured only at gain 1.0 in the baseline conditions."

### [shuffle] 11b. JO-A (the paper's sound reflex) absent from the sensitivity table; JO-B stand-in fails at 50 Hz and >= 5 synapses
PAPER: Note 2: "and a sensitivity table over stimulus rate, time step, numerics, transmitter-sign rule, smell-centre scale, connection table and threshold (14 female and 13 male conditions)." Note 4: "Sound (JO-A) $\rightarrow$ giant fibre 6 / 11 / 16\,Hz."
VERDICT CONFIRMED headline=False
EVIDENCE: None of the sensitivity_*.csv tables has a column with 'JO-A'; the only sound input is 'sound (JO-B) -> GF jump'. Female, sensitivity_flywire_shiu_min1+known+eln0.25.csv, 14 rows: baseline 4.44 Hz; 50 Hz stimulus 0.28; connections >= 5 synapses (shiu_min5) 0.83; Zenodo >= 5 0.83; 150 Hz 10.28; legacy 10.56; the other rows 3.89-4.44. So JO-B is below 1 Hz in 3 of 14 female conditions. The published-signs table (sensitivity_flywire_shiu_min1.csv) and the older sensitivity_flywire.csv give the same values. In the male (sensitivity_malecns_all_min1+eln0.25.csv, 13 rows), JO-B->GF is 34.4-104.2 Hz in every row, so it passes. JO-A itself passes the gain test (gain_sweep female: 5.5 / 10.8 / 16.2 Hz at 0.7 / 1.0 / 1.4) and the global null (0.00). It keeps 60 % under the block null (10c). In the male it is 0 at every gain up to 1.4, so the male's sound reflex is JO-B only. The research notes (14s) already say sound->GF is 'present from 100 Hz up'.
WORDING: Note 2: "...(14 female and 13 male conditions; the sound input in this table is JO-B, whose drive of the giant fibre in the female, 4.4 Hz at baseline, falls to 0.3 Hz at a 50 Hz stimulus and 0.8 Hz under the >= 5-synapse threshold; JO-A was not in the table)." Or add JO-A to the sensitivity run and report it.

### [shuffle] 11c. "Smell responses need 1.0 or more" is female only
PAPER: Note 2: "Every synapse at 0.7, 1.0 and 1.4 times its published strength (smell responses need 1.0 or more, and for them the window is 1.0--1.4)"
VERDICT CONFIRMED headline=False
EVIDENCE: Female, gain_sweep_flywire_shiu_min1+known+eln0.25.csv, gain 0.7, 5 seeds: cVA, CO2, Or47b, Or88a and aversive odour give 0.0 on every readout. Food odour gives DNa L 0.2 and PPL1 4.9, with no DN response. So the statement holds in the female. Male, gain_sweep_malecns_all_min1+eln0.25.csv, gain 0.7: cVA->DNp13 7.8 Hz, MN9 7.5 Hz, song MNs 1.8 Hz, against 30.2 / 32.5 / 12.6 at 1.0. Note 4 already prints the male '7.8 / 30 / 26 Hz', which contradicts Note 2 as written. Other male odours are 0 at 0.7.
WORDING: Note 2: "(in the female, smell responses need 1.0 or more, and for them the window is 1.0-1.4; the male's cVA response is present but weak at 0.7, 7.8 Hz on DNp13 against 30 at 1.0)"

>>> REFUTE [shuffle] 10a. Which null the paper used: the global degree-preserving null silences every input: upheld=True
EVIDENCE: Verdict: CONFIRMED (upheld), but the verifier's corrected wording goes too far in one place and needs fixing. Headline: partial. It weakens the "in the wiring" test behind "reflexes in the wiring" and shows the sound-escape reflex is only partly wiring-specific. It does not overturn that conclusion.

Paper, l.89: "vanish when the brain is rewired at random with every neuron keeping its number of connections". Note 2 (l.139): "degree-preserving rewiring \citep{maslov2002specificity}, which moves 99.8\,\% of connections and leaves every readout at 0--2\,Hz (largest stray value 7\,Hz)". Note 4 (l.143): "Every readout 0--2\,Hz in a rewired brain."

Files: release/pre_rerun_20260926/results/shuffle_*.csv. The live experiments/results copies of all four files are identical (numeric max diff 0, wall_s aside). Readouts are per-neuron mean rates: common.run_trials computes counts[v].sum()/len(v)/(ms/1000). "DN all" is super_class=="descending", which is 1,303 neurons in data/Supplemental_file1_neuron_annotations.tsv.

1. The numbers I re-derived match the verifier's.
- Paper's female model (min1+known+eln0.25), global null:
  - frac_moved 0.998568 / 0.998574 / 0.998588. That is 99.86 %, which rounds to 99.9, not 99.8. Male is 0.99808-0.99810, so 99.8 %.
  - Pooled rewired max is 2.12 Hz (food odour -> MDN). The largest per-brain mean is 6.35 Hz (rewiring 2) and the largest single run is 7.19 Hz (food, shuffle 2, seed 2).
  - DN all is at most 0.15 Hz in any rewired run. Touch gives 0.13 Hz rewired against 8.06 Hz intact.
- Male global: pooled max 2.19 Hz (ppk23/25 -> DNp13), single run 5.0 Hz, DN all at most 0.11 Hz.
- So "0-2 Hz, largest 7 Hz" is right only with generous rounding (2.12 and 2.19 Hz).

2. The global null silences essentially all propagation. The core of the item holds.
Non-driven neurons that fire (active_frac x 139,255 minus n_driven), intact -> rewired:

| Input | Extra neurons firing | DN spikes per 0.8 s trial (DN all x 1,303 x 0.8) |
|---|---|---|
| cVA | 1,841 -> 0 | 1,729 -> 0 |
| JO-A | 33 -> 5 | 126 -> 0 |
| JO-B | 96 -> 3 | 236 -> 0.1 |
| sugar | 417 -> 58 | 1,351 -> 13 |
| food odour | 1,900 -> 287 | 1,361 -> 53 |
| touch | 957 -> 628 | 8,404 -> 130 (1.6 %) |

No intact response survives in any of the 3 female or 2 male brains. So nothing could ever fail this test.

3. Both nulls are degree-preserving.
- In shuffle_control.rewire, a swap of targets a->b, c->d to a->d, c->b keeps every in- and out-degree whether or not `block[b]==block[d]` is imposed.
- "Degree-preserving" and "every neuron keeping its number of connections" therefore describe both nulls. Only "99.8 %" points to the global one (block moved 94.35 / 94.34 %).
- Under the block null (shiu_min1, published smell centre, 2 brains), sugar -> MN9 still vanishes (80.4 -> 0 / 0), as do JO-B -> GF (4.8 -> 0.6 / 0) and food -> DNa L (36 -> 1.7 / 0).
- Three responses do not vanish:
  - JO-A -> GF, the paper's "sound fires its escape jump": 10.6 -> 5.2 / 7.5 Hz (pooled 6.35).
  - Touch -> feeding MNs: 15.7 -> 24.5 / 19.6.
  - Touch -> DNp13: 36.7 -> 8.8 / 13.8.
- Touch also drives GF to 78 Hz, MDN to 32 and DN all to 14.6 Hz.
- Intact JO-A -> GF is 10.62 Hz in both lobe variants, so this transfers to the paper's model. The block null is never mentioned in the paper.

4. Where the verifier's wording goes too far.
- "No sensory input then reaches a descending neuron (all DNs <= 0.15 Hz)" and "stops every sense from reaching the descending neurons at all" are wrong. 0.15 Hz is the mean over 1,303 DNs, not a per-neuron ceiling.
- Rewired touch still produces about 130 DN spikes per trial (max 159), and food odour about 53 (max 82).
- MDN, which is a DN, reaches 7.19 Hz in one run (pooled 2.12). Male DNp13 reaches 5.0 Hz (pooled 2.19).
- "Almost nothing" is correct; "at all" is not.
- "Every readout averages 0-2 Hz" should read 0-2.2 Hz.
WORDING: l.89: "...It has to survive every synapse being turned up or down by about a third, and vanish when every connection is handed to a random new partner anywhere in the brain, each neuron keeping its number of connections. That is a blunt test: in such a brain almost nothing gets from any sense to the descending neurons, so it shows the responses need the real wiring, not which part of it. It also has to hold under every reasonable alternative to my own choices, fourteen versions of the female model and thirteen of the male \note{2}."

Note 2: "unconstrained degree-preserving rewiring \citep{maslov2002specificity}: any connection may move to any target, and 99.8-99.9 % of them do (3 female, 2 male rewired brains). Almost no sensory drive then reaches the descending neurons. Their mean rate stays at or below 0.15 Hz even with all 1,417 head bristles driven (8.1 Hz intact), about 130 descending-neuron spikes per trial against 8,400. Every readout averages 0-2.2 Hz, and the largest single value is 7 Hz (MDN, food odour). No intact response survives this null, so it cannot tell specific wiring from any other real wiring. A stricter null, also degree-preserving, keeps each connection's target within its class (sensory, central, descending...). It moved 94 % of connections (published smell centre, 2 brains). Under it, sugar -> MN9 (80 -> 0 Hz), smell -> DNa and JO-B -> giant fibre still vanish. Sound (JO-A) -> giant fibre keeps 5-7.5 of 10.6 Hz. Head touch drives the giant fibre (78 Hz), MDN (32) and the feeding MNs (22) all at once, and DNp13 falls to 11 of 37 Hz."

Note 4 tail: "Every readout 0-2.2 Hz in a brain rewired without constraint (see Note 2 for the class-preserving null)."

>>> REFUTE [shuffle] 10c. Class-preserving (block) null keeps part of the sound and touch reflexes: upheld=True
EVIDENCE: Verdict: CONFIRMED, with refinements. Headline = true: it qualifies the evidence sentence for "reflexes in the wiring", but that conclusion still holds.

Paper, l.93: "Scramble the wiring and every one of these reflexes disappears." l.89 states the test as: "vanish when the brain is rewired at random with every neuron keeping its number of connections". Note 2 names only the degree-preserving null ("moves 99.8 % of connections and leaves every readout at 0-2 Hz (largest stray value 7 Hz)"). Note 4 says "Every readout 0-2 Hz in a rewired brain". The paper has no Fig 6, and the block null is not mentioned anywhere.

Attempts to refute:
(1) Wrong file or version. The block CSV is identical in release/pre_rerun_20260926, pre_rerun_20260925, flycraft_20260919 and the live experiments/results copy rewritten 27 Sep 00:53. All four give the same means, and frac_moved is 0.9435 / 0.9434 in each.
(2) Pairing. The intact rows are seeds 0-2 in the same file. Their JO-A->GF of 10.625 matches the intact rows in both global files, so the comparison is sound.
(3) Does the paper's sentence survive on its own terms? Literally, yes, for the global null. My check: every global readout is at most 7.19 Hz (single run, food->MDN, modified lobe), and the per-rewiring maximum is 6.35. But the block null also rewires at random with every neuron keeping its number of connections. rewire() in experiments/shuffle_control.py does degree-preserving target swaps with block[b]==block[d] on super_class. So by the paper's own l.89 definition the block brain qualifies, and one reflex does not vanish in it.
(4) Did the author mean JO-B? No. Note 4 defines the sound reflex as JO-A->GF 6/11/16 Hz. RESEARCH_NOTES 14v says the block null gives "sound -> giant fiber 0-0.6 Hz". That matches the JO-B per-rewiring means (0.625 and 0). So the log read JO-B and missed JO-A, which is where the overstatement came from.

My numbers (release/pre_rerun_20260926/results/shuffle_flywire_shiu_min1_block.csv; means over 2 rewirings x 3 seeds against 3 intact seeds):
- JO-A->GF: 6.354 against 10.625. Per rewiring 5.21 and 7.50; single runs 4.375-7.5, all above 2 Hz. DN-all is 0.09 (0.12 intact) and every other readout is 0. Specificity (GF minus DN-all) is 6.26 against 10.50, so 60 % remains (49 % and 70 % per rewiring). The reflex survives and stays specific; it is not a burst.
- JO-B->GF: 0.31 against 4.79 (maximum single run 1.25). Gone.
- Sugar->MN9: 0 against 80.42; feeding MNs 0.30 against 25.2. Gone.
- cVA->DNa L/R: 0/0 against 36.25/3.54. Food->DNa: 0.83/0.52 against 36.04/4.79. Gone.
- Touch: GF 77.7 (intact 0), MDN 31.9 (0.73), DNa 54.6/49.1 (0/0.62), DNp13 11.25 (36.67), feeding MNs 22.06 (15.71), DN-all 14.65 (8.04). DNp13 minus DN-all is -3.4 against +28.6, so the ovipositor reflex loses all specificity. By design_plan S15's criterion (specificity drop of at least 80 %) it has disappeared.
- Freeze: it reverses. cVA->DNa L is 0 and cVA+touch is 53.75 under block, where intact is 36.25 falling to 24.38.
- cVA+touch: GF 80.8, MDN 31.35.

Refinements to the verifier:
(a) The surviving sound reflex is the JO-A one only; JO-B's disappears. It also stays specific, which is the stronger point.
(b) "Both steering neurons 50-55 Hz" should read 49-55, and the wording should say the freeze reverses.
(c) Scope: the block null covers only the published lobe and the female. For non-smell reflexes the intact values match the paper's lobe (JO-A 10.62 in both; touch->DNp13 36.67 against 35.42), so the result probably transfers, but that is untested. Male untested.
(d) Separate issue (item 10b): grooming (aBN1) and bitter suppression were never read in any rewired brain, so "every one" is also unsupported for those two.
WORDING: Main text, l.93, replacing the sentence: "Rewire the brain at random, every neuron keeping its number of connections, and every one of these reflexes disappears. A stricter rewiring that also keeps each connection within its broad cell class (sensory, central, descending) is harder to pass. Sugar, smells and one of the two sound channels still reach nothing, but a sound on the other channel still fires the escape neuron, and nothing else, at about 60 % of its normal rate. Touch sets off an indiscriminate burst in which the steering neurons fire instead of falling silent."

Add to Note 2: "Class-preserving rewiring (swaps only between targets of the same super-class; published smell centre, female; 2 rewirings x 3 seeds; 94 % of connections moved): sugar->MN9 0 Hz (intact 80); cVA and food odour->DNa at most 0.8 Hz (36); JO-B->GF 0.3 (4.8); JO-A->GF 6.4 (10.6; 5.2 and 7.5 per rewiring, every other readout 0); touch->GF 78, MDN 32, DNa 55/49, DNp13 11 (intact 0, 0.7, 0/0.6, 37) against a mean of 15 over all descending neurons. Not run for the modified smell centre or the male. Grooming and bitter suppression were not read in any rewired brain." Change Note 4's closing phrase to "in a degree-preserving rewired brain".

>>> REFUTE [shuffle] 11a. The three tests presented as a filter every reflex passes; grooming and bitter suppression never went through any of them: upheld=True
EVIDENCE: Verdict: CONFIRMED, with two small points where the verifier's wording goes slightly too far. Headline: yes. It weakens "reflexes in the wiring" by overstating which reflexes passed the paper's own filter. The conclusion itself stands for the reflexes that were tested (sugar, sound, touch->DNp13, the freeze).

Paper text: l.89 "a behaviour counts as ``in the wiring'' here only if it passes three tests." l.93 "Sugar makes it work its mouthparts, and bitter makes it stop. ... Wind on the antenna makes it groom. ... Scramble the wiring and every one of these reflexes disappears." l.121 "how to eat, how to jump, how to groom, how to freeze when touched and how to back away." Note 4 heads its list "(female unless stated; gain 0.7 / 1.0 / 1.4)", but gives no gain triplet for bitter (a single 3.3 Hz) or grooming (no number). It closes with "Every readout 0-2 Hz in a rewired brain."

Re-derived from release/pre_rerun_20260926/results/:
1. Test 1 (gain). The input column of gain_sweep_flywire_shiu_min1+known+eln0.25.csv and gain_sweep_flywire_shiu_min1.csv has 13 values including "none": CO2, Or47b, Or88a, aversive, cVA, cVA+touch, food+touch, food, JO-A, JO-B, sugar GRNs, head bristles. None is bitter, sugar+bitter or JO-CE, and no file has an aBN1 column. old_v1/gain_sweep_* are the same. Neither reflex was ever run at 0.7 or 1.4.
2. Test 2 (rewiring). The inputs of all four shuffle_*.csv are cVA, cVA+touch, food, JO-A, JO-B, sugar, bristles and none (plus ppk in the male). No bitter, no JO-CE, no aBN1 column. One nuance the verifier missed: in the global null, sugar GRNs->MN9 is 0.00 Hz under both smell-centre settings (intact 75.8 / 80.4). So the bitter suppression vanishes trivially in a rewired brain, because there is no sugar response left to suppress. For grooming nothing implies the result, since aBN1 was never read in a rewired brain.
3. Test 3 (sensitivity). The 14 female conditions of sensitivity_flywire_shiu_min1+known+eln0.25.csv and the 13 male conditions have no bitter, JO-CE or aBN1 column. The second nuance: the only measurements, benchmark_flywire.csv (published model) and benchmark_flywire_shiu_min1+known+eln0.25.csv (the paper's model), cover 2 of the 14 female conditions. Both pass:
   - JON-CE->aBN1: seeds 13/10/15 = 12.7 Hz published, 12/12/16 = 13.3 Hz paper's model. JON-F->aBN1 is 0 in both.
   - MN9 L, sugar alone -> sugar + bitter at 100 Hz: seeds 66/53/54 -> 6/8/5 (57.7 -> 6.3) published, 50/56/59 -> 2/1/7 (55.0 -> 3.3) paper's model.
   - Bitter at 25/50/100 Hz is monotone: 55 -> 38.0 -> 19.7 -> 3.3.
   benchmark.py takes only --seeds and --ms, and make_sim defaults to gain 1.0, dt 0.2 and no noise. So both reflexes were measured at gain 1.0, 100 Hz, dt 0.2 and 3 seeds only.
4. The social probes do contain 'bitter GRNs' and 'wind/gravity (JO-CE)' rows, but they have no aBN1 column, bitter is given alone (MN9 0.0) and they are not one of the three tests. experiments/results_edge holds only _smoke runs and has no grid_probe (the planned grooming/bitter check). In the live experiments/results, aBN1 still appears only in the two benchmark files.
5. The project's own records agree:
   - RESEARCH_NOTES.md §18l gives the evidence for both rows as "(16a anchors)" only, while the other rows cite window, shuffle and sensitivity.
   - design_claims_ledger.md l.26/28/37/97 says grooming "never passed the three tests" and bitter "appears in no gain, shuffle or sensitivity file".
   - design_plan.md §4 item 11 says the same.

Where the verifier overreaches: its Note 2 sentence "measured only at gain 1.0 in the baseline conditions" is inexact. They were measured at gain 1.0 under both smell-centre settings, which is 2 of the 14 conditions. "I did not put them through these tests" is also slightly too strong: bitter passes test 2 by implication, and both pass the one sensitivity alternative that was run. The core finding stands, because neither reflex was ever gain-tested, and grooming was never read in a rewired brain.
WORDING: l.89, after the three-tests sentence, add: "Two reflexes below, grooming and bitter stopping the mouthparts, are Shiu et al.'s. I reproduced them at the published strength under both versions of the smell centre, but did not put them through the first test or the rest of the third."

l.93: "Sugar makes it work its mouthparts, and, as Shiu et al. found, bitter makes it stop. A sound fires its escape jump. Wind on the antenna makes it groom, again as in Shiu et al." Change the last sentence to: "Scramble the wiring and every one of these reflexes that I tested disappears." That covers item 10b, since aBN1 was never read in a rewired brain.

Closing, l.121: "how to eat, how to jump, how to freeze when touched and how to back away, and, on Shiu et al.'s evidence, how to groom."

Note 4: "...with Shiu et al.'s 29 sugar neurons 55 Hz, and 3.3 Hz with bitter added (57.7 -> 6.3 under the published smell centre). Wind (JO-CE) -> the grooming neuron aBN1 13 Hz (12.7 published; JO-F 0). These two were run only at gain 1.0 and 100 Hz, under both smell-centre settings. In a rewired brain sugar no longer drives MN9, so there is nothing for bitter to suppress, and aBN1 was not read there."

Note 2, add at the end: "Grooming and bitter suppression were run only at gain 1.0, in two of the 14 female conditions."

### [deciders] 13a. Decider coverage: 'at every gain up to 1.4 and in all 14 conditions' (female)
PAPER: Note 5 (l.145): "pC1a--e, aIPg, vpoDN and oviDN fire 0.0\,Hz to every input and combination, at every gain up to 1.4 and in all 14 conditions"; also l.95: "stay silent whatever the fly senses, in every version of the model."
VERDICT CONFIRMED headline=False
EVIDENCE: Frozen copy release/pre_rerun_20260926/results/. (1) gain_sweep_flywire_shiu_min1+known+eln0.25.csv (5 seeds) and gain_sweep_flywire_shiu_min1.csv (3 seeds) have only four decider columns: pC1a recept, pC1d/e aggr, aIPg aggr and vpoEN/DN accept. There is no pC1b/c column and no oviDN column. Inputs are 12 plus 'none' (13 unique), not '14 inputs plus none'; 14+none is the male sweep. All four columns are 0.0 in every row at gains 0.5, 0.7, 1.0 and 1.4. At 2.0: pC1d/e 6.7, aIPg 0.72, vpoEN/DN 0.28. (2) sensitivity_flywire_shiu_min1+known+eln0.25.csv has 14 rows. Its only decider columns are 'cVA -> pC1d/e aggr' and 'cVA -> aIPg aggr', both 0.0 in all 14 rows. The same holds for the published-lobe sensitivity file. (3) The full 'every input and combination' claim holds only at gain 1.0. social_probe_flywire_*_noise0.csv (26 inputs + none, 5 seeds, both lobes) reads pC1a, pC1b/c, pC1d/e, aIPg, vpoEN/DN and oviDN, and every per-seed value is 0.0. So pC1b/c and oviDN were read only at gain 1.0. pC1a and vpoDN were read at every gain but in no sensitivity condition. The 14 conditions test one input (cVA) on two deciders.
WORDING: pC1a--e, aIPg, vpoDN and oviDN fire 0.0 Hz to every one of 26 inputs and combinations at gain 1.0, under both smell centres. pC1a, pC1d/e, aIPg and vpoDN also stay at 0.0 for 12 inputs at every gain from 0.5 to 1.4. cVA drives neither pC1d/e nor aIPg in any of the 14 conditions. (pC1b/c and oviDN were read at gain 1.0 only.) In l.95, replace "in every version of the model" with "at every gain up to 1.4, and for cVA in every version of the model".

### [deciders] 13b. Male P1 'at or below 0.6 Hz' holds only at gain <= 1.0 (and male aIPg at 1.4)
PAPER: Note 5 (l.145): "male P1 stays at or below 0.6\,Hz" (in the sentence scoped "at every gain up to 1.4 and in all 14 conditions"); l.95: "...and whether a male courts, stay silent whatever the fly senses, in every version of the model."
VERDICT CONFIRMED headline=False
EVIDENCE: gain_sweep_malecns_all_min1+eln0.25.csv (5 seeds, 14 inputs + none). P1/pC1 male per-seed maximum: 0.0 at gains 0.5 and 0.7; 0.563 at 1.0 (cVA+touch, mean 0.48). At 1.4, cVA+touch gives 1.95/2.22/2.16/2.30/1.99 across seeds (mean 2.12) and cVA gives mean 1.58 (max 1.71). aIPg at 1.4: cVA mean 1.40, per-seed 0.94-1.88; cVA+touch 0.44. sensitivity_malecns_all_min1+eln0.25.csv (13 conditions, cVA -> P1): 2.50 Hz under 'legacy numerics (first version)', 0.65 at '>=5 synapses', <=0.26 elsewhere. aIPg is 0.49 under legacy numerics. social_probe_malecns_all_min1+eln0.25_noise0.csv (gain 1.0): P1 at most 0.47, aIPg 0.0. paper_numbers.md l.38 also computes '0.6 / 0.0; at 1.4: 2.3 / 1.9', but the short paper dropped the gain-1.4 half. The published-lobe male sweep peaks at 1.07 Hz at gain 1.4.
WORDING: Male P1 stays at or below 0.6 Hz at gains up to 1.0. At 1.4, cVA with touch raises it to 2.1--2.3 Hz and cVA raises aIPg to 1.4--1.9 Hz. Under the first-version numerics P1 reaches 2.5 Hz. In l.95, replace "stay silent ... in every version of the model" with "stay silent, or nearly so (male P1 at most 2.5 Hz), whatever the fly senses".

### [deciders] 13c. pIP10 range ('answers cVA only, at 2-3.5 Hz')
PAPER: Note 5 (l.145): "the song command pIP10 answers cVA only, at 2--3.5\,Hz."
VERDICT CONFIRMED headline=False
EVIDENCE: social_probe_malecns_all_min1+eln0.25_noise0.csv (gain 1.0, 3 seeds). pIP10 means: cVA 2.33, cVA+food 3.00, cVA+sugar 3.00, cVA+song 3.67 (per-seed max 4.5). Every input without cVA gives 0.0, and so do cVA+touch and cVA+contact pheromone. gain_sweep_malecns_all_min1+eln0.25.csv at gain 1.0: cVA 3.33 Hz; every other input 0.0. The range at gain 1.0 is therefore 2.3-3.7 Hz, not 2-3.5. paper_numbers.md l.88 computed 3.7 against the paper's 3.5 and passed it under its loose tolerance. The range is wider elsewhere: - At gain 1.4, cVA gives 7.5 Hz and non-cVA odours give 0.17-0.5. - Across the 13 sensitivity conditions, cVA gives 1.1-6.9 Hz. - Under the published smell centre (social_probe_malecns_all_min1_noise0.csv), pIP10 answers every odour: cVA 6.2, other odours 1.6-4.1, sugar 1.5. The 'cVA only' claim is true for the paper's model at gain <=1.0.
WORDING: ...and the song command pIP10 answers only cVA, alone or combined with food, sugar or song, at 2.3--3.7 Hz. (Under the published smell centre it answers every odour, at 1.6--6.2 Hz.)

### [deciders] 14a. Clean box 'every neuron at rest' and 'no eyes' vs the eye activity in the logs
PAPER: l.95: "In a clean box with nothing to smell, two simulated females stood still for more than two minutes of brain time, every neuron at rest, because the published model has no activity of its own." l.125: "...once stood in a clean white box for two minutes, every neuron at rest, like parked cars with the keys left in." l.123: "It has no chemistry beyond its synapses, no electrical connections and no eyes". Note 11 (l.157) lists vision under "Not modelled".
VERDICT CONFIRMED headline=False
EVIDENCE: The 10 clean female-female logs are logs/fly{1,2}_off-flywire-known-eln0.25_2026091{8,9}-*.csv with trial off_ff_t{1..5}_clean. Brain time is 135.1 +/- 6.5 s. In every log: - hz_total_spikes (counts.sum() per 50-ms tick, motor.py l.100) averages 40,456-41,271, range 37,856-43,939. - hz_active_frac is 0.080 in every tick. - Every other hz_* readout is 0.0 in every tick (DN all, DNa, DNp09, KC, MBON, DAN, feed, reject, SAG, IPC). The trial .out logs (logs/trial_off_ff_1_clean.out) show 'spikes 40464 ... DNa L/R 0.0/0.0 ... KC 0.0 MBON 0.0' and vision=lif, noise=0.0 Hz. Senses (same .out): photo_L 5,765 + photo_R 5,353 = 11,118 photoreceptors (R1-6/R7/R8) of 139,248 neurons, which is 7.98 %. That matches the 8 % active fraction; the ~94 VA1v ORNs add about 0.05 %. senses.py drives them at luminance x R_VISION = 120 Hz from the bot's eye images. The implied rate is ~40,300 spikes / (11,118 x 0.05 s), about 72 Hz per photoreceptor. RESEARCH_NOTES l.52, l.127 and l.140: the signal dies in the optic lobe ('silent beyond the lamina with histaminergic photoreceptors' under known signs). So about 11,000 neurons fire in every tick and the fly has an eye. What is true is that no central or descending readout fires. The replication rep-clean ff logs show the same (40,457-41,274 spikes/tick, active 0.080, all readouts 0).
WORDING: l.95: "...two simulated females stood still for more than two minutes of brain time. Their eyes fired, but not one neuron beyond the optic lobe did, because the model has no activity of its own." l.125: "...stood in a clean white box for two minutes with only their eyes firing, like parked cars with the keys left in." l.123: "...no electrical connections, and an eye whose signal never leaves the optic lobe". Note 11: move vision out of 'Not modelled' and say: "vision: photoreceptors driven by the bot's luminance at up to 120 Hz, whose signal dies in the lamina (a bridge to Lappalainen et al. exists, but no result uses it)." Note 5 can keep "every readout 0.00".

### [deciders] 14b. The clean box is not odourless (faint Or47b and CO2 each female smells)
PAPER: l.95: "In a clean box with nothing to smell, two simulated females stood still..."
VERDICT CONFIRMED headline=False
EVIDENCE: The same 10 clean ff logs, columns obs_smell_fly_L/R (-> orn_fly = 94 ORN_VA1v, Or47b; senses.py l.65, R_OLF 150 Hz) and obs_smell_co2_L/R (-> 67 ORN_V). - Or47b per antenna, steady value: 0.207 in the 8 logs that start 4 blocks apart; 0.098-0.135 in the 2 t5 logs that start 5.66 blocks apart. One-tick transients reach 0.42-0.65. - CO2 per antenna: 0.0058 (4 blocks) and 0.0026-0.0036 (t5); maximum 0.026. At R_OLF 150 Hz this drives the Or47b ORNs at about 15-31 Hz and the CO2 ORNs at 0.4-0.9 Hz, continuously. Food, cVA and aversive are 0 throughout, and there are no odor_ columns. The item's 'Or47b at 0.10 and CO2 at 0.003' fits only the two 5.7-block logs; the typical values are about twice that. RESEARCH_NOTES 19b l.1463 gives 'Or47b, up to 0.42 ... and CO2 at 0.003'. The input reaches nothing downstream, consistent with social_probe (Or47b at 100 Hz: DNa 0/0, DN all 0.01).
WORDING: "In a clean box, where the only smells were each other's body odour and a trace of CO2 (neither of which reaches any descending neuron), two simulated females stood still..." In Note 5 or Note 8, add: "each female smells the other's Or47b at 0.1--0.2 of the body's maximum and CO2 at 0.003--0.006".

### [deciders] 14c. 'because the published model has no activity of its own' holds by construction (critique: 'no activity of its own by construction')
PAPER: l.95: "...every neuron at rest, because the published model has no activity of its own. A real fly put in an empty dish soon starts walking about. Walking, the most ordinary thing a fly does, was the first behaviour on my list that is not in the wiring."
VERDICT CONFIRMED headline=True
EVIDENCE: brain/flybrain/lif.py l.6: dv/dt = (v_0 - v + g)/t_mbr with v_0 = v_reset = -52 mV and threshold -45 mV. There is no intrinsic or bias current; noise_hz defaults to 0.0 (l.54, 'Shiu default'); every v starts at v_rest (l.302). The clean-box runs were logged with noise=0.0 Hz. With no input, g stays 0 and no neuron can ever reach threshold, whatever the wiring. So 'stands still with nothing to sense' cannot fail for any connectome under this neuron model. The DNs are silent because nothing drives them, not because of the wiring. The hum series supports this: with 0.2 Hz of Poisson input to every neuron the same wiring walks (DNa ~14-17 Hz in the noise0.2 logs).
WORDING: "...because the model's neurons, as Shiu et al. built them, have no activity of their own: a neuron with no input never fires. So walking without a reason cannot come from this model whatever the wiring, and the clean box tests the neuron model, not the map." Then soften the next sentence to: "Walking, the most ordinary thing a fly does, needs some input or background activity that this model does not supply."

### [deciders] 15. Note 5 steering: 'No sign rule steers towards food ... under the published signs, a 16-29 Hz left turn whatever the odour'
PAPER: Note 5 (l.145): "No sign rule steers towards food (under mine, a 0.7--9\,Hz avoidance of the four food odours at five strengths; under the published signs, a 16--29\,Hz left turn whatever the odour)."
VERDICT PARTLY headline=False
EVIDENCE: Computed with the paper_numbers.py steer() definition (steer = (approach_L + approach_R)/2, bias = (approach_L - approach_R)/2, approach = ipsi-contra DNa, mean of 3 seeds) from the frozen odor_dose_*.csv files. (a) Mine (odor_dose_flywire_shiu_min1+known+eln0.25.csv): food-type steering is -0.67 to -9.17 Hz in 20/20 cells, so '0.7-9 Hz avoidance' is correct. (b) The 'published signs' file is odor_dose_flywire_shiu_min1+eln0.25.csv (Shiu signs, eLN x0.25). The sentence contrasts sign rules, so 'published signs' is accurate, and the item's first bullet ('not the published model') is refuted, as the critique says. But its steering component favours the food side in 17 of 20 food-type cells: - food: +1.33/+1.17/+2.42/+2.00/+2.67 at 25-150 Hz (per-seed minimum >= 0 at every dose); - sweet: +0.4 to +2.7; - ester: +1.6 to +3.8 above 25 Hz. The range is -2.9 to +3.8. Its bias: food-type odours 15.75-29.17 Hz, which is the paper's '16-29'. For the other odours, though: CO2 is 0.0 at 25 Hz (no DNa at all under one-sided drive), then 8.25-17.5. The aversive odour is 0.0 at 25 Hz, then 11.67-17.58. cVA is 14.9-18.5. So 'whatever the odour' is wrong. Over every odour and dose with DNa activity the bias is 8.3-29.2 Hz (the critique's 8.2-29.2). (c) Zenodo table (odor_dose_flywire_zenodo_min1+known+eln0.25.csv): vinegar +6.50 at 150 Hz (per-seed 5.5-7.5); sweet positive at every dose (+0.7 to +3.6); 14 of 20 food-type cells positive. 'No sign rule steers towards food' therefore overstates.
WORDING: "No sign rule gives a clear pull towards food. Under mine the four food odours are avoided by 0.7--9 Hz at all five strengths. Under the published signs (with my smell-centre change) a fixed left turn of 16--29 Hz for food odours (8--19 Hz for CO2, cVA and the aversive odour, which at 25 Hz drive nothing) masks a weak pull of up to 3.8 Hz towards the food side (food itself +1.2 to +2.7 Hz at every strength). On the Zenodo table the largest pull is +6.5 Hz towards vinegar at 150 Hz."

### [deciders] Critique: female walking is read only from DNa01/02 + DNp09, and DNp09 is silent (the freeze is DNa suppression by construction of the decoder)
PAPER: l.93: "Touch also switched off the neurons she steers with, which I had not expected, so a touched female freezes." l.101: "...and then stayed together, because touch switched off their steering while their ovipositors kept going." l.123: "touch a walking fly on the head and its steering neurons should fall quiet, so that two flies bumping heads should stop together." Note 11 (l.157) lists only "how firing becomes movement" as the author's choice.
VERDICT CONFIRMED headline=True
EVIDENCE: brain/flybrain/motor.py. The female (FlyWire) has no nerve cord (has_vnc False; the trial .out says 'walking read from descending neurons'). Walking = 1 - exp(-mean rate of the 'forward' group / 10 Hz). That group has 6 neurons: DNp09 x2, DNa01 x2, DNa02 x2 (logs/trial_off_ff_1_clean.out '[motor] forward 6 neurons'). Turning = tanh((DNa L - DNa R)/40). DNp09 is silent: - contact_stop_flywire.csv, all 56 rows (every sign/eLN/table variant, with and without the hum): 'DNp09 alone' 0.0-0.67 Hz and 'DNp09 +touch' 0.0-0.33 Hz. - social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv: DNp09 0.0 for every input except eye bristles (0.3). - Female arena logs (hz_dnp09): 0.00 in every no-hum series, 0.20 in the hum series (the hum's own injected rate). hz_forward equals exactly 2/3 of the mean DNa rate in every series (e.g. 7.875 -> 5.25, 14.16 -> 9.51). So walking and steering in the arena are DNa01/02 alone, diluted by the two silent DNp09. Touch does not silence the descending population. In the paper's-model food row, DN all (1,303 DNs) rises 1.27 -> 8.38 Hz while DNa falls 20.3/12.3 -> 6.8/3.2. In the arena, DN all is 3.6-4.1 Hz far and 11.9-13.4 Hz on contact. The freeze is therefore silencing of the two DN types the decoder reads, while most other DNs speed up. The touch drive is all 1,417 BM_ bristle neurons at 200 Hz.
WORDING: Note 11, add: "The female model has no nerve cord, so I read her walking from six descending neurons, DNp09 and DNa01/02 (forward drive 1 - exp(-rate/10 Hz), turning from DNa left minus right). DNp09 never fires above 0.7 Hz in any condition, so she walks and steers on DNa01/02 alone." l.93: "Touch also silenced DNa01/02, the neurons from which I read her walking and steering, although it raised the average descending neuron from 1.3 to 8.4 Hz, so, as I read the brain, a touched female freezes." l.101: "...stayed together, because touch silenced the neurons I read their walking from." l.123: keep the prediction about DNa01/02 falling quiet, and make "should stop together" conditional on those neurons carrying walking.

>>> REFUTE [deciders] 14c. 'because the published model has no activity of its own' holds by construction (critique: 'no activity of its own by construction'): upheld=False
EVIDENCE: Verdict: PARTLY. headline=true, because it bears on "walking not in the wiring".

Paper l.95: "In a clean box with nothing to smell, two simulated females stood still for more than two minutes of brain time, every neuron at rest, because the published model has no activity of its own. ... Walking, the most ordinary thing a fly does, was the first behaviour on my list that is not in the wiring."

What the verifier got right. brain/flybrain/lif.py l.6 and l.44-54 give v_rest = v_reset = -52 mV, threshold -45 mV, noise_hz = 0.0 by default, and no bias current. l.302 starts every v at v_rest. So a neuron with no input never fires. Offline this is trivially true: in release/pre_rerun_20260926/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv and noise_floor_flywire_...eln0.25.csv, the rows with input=none and noise 0 have total_spikes 0, active_frac 0 and wall_s 0.0. That check cannot fail. The clean-box logs have no noise tag, so they ran at noise 0. So "no activity of its own" is a property of the neuron model, and nothing in this brain can start moving unprompted.

Where the verifier's computation is wrong: it assumes the clean box had no input. It did have input. senses.py drives photoreceptors every tick (luminance x R_VISION), ORN_VA1v from the other fly's odour and ORN_V from CO2. I read all 20 clean female-female logs (logs/fly{1,2}_off-flywire-known-eln0.25_*.csv with trial off_ff_t*_clean or rep-clean):
- hz_total_spikes is 37,856-43,939 per 50-ms tick (mean about 40,900, roughly 0.8 M spikes/s).
- hz_active_frac is 0.07-0.08 in every tick, about 8 % of the roughly 139k neurons, around 10-11k.
- obs_smell_fly averages 0.12-0.21 of maximum and peaks at 0.13-0.65; CO2 peaks at 0.004-0.026.
- Every one of the 23 hz_ group readouts (DN all, DNa, DNp09, MB KC/MBON/DAN, MNs, and the rest) is exactly 0.000 in every tick.
- Brain time in the 10 original logs is 135.1 +/- 6.5 s, which matches Note 5's "135 +/- 6 s".

So:
1. "Every neuron at rest" is false. The verifier missed this and endorsed "g stays 0".
2. The descending neurons were silent because the light and odour that fired about 8 % of the brain never reached any of them. That is a result about the map under this model: RESEARCH_NOTES 19f says the photoreceptor drive dies in the medulla, and 18a says Or47b reaches nothing. It is not a zero-input identity.

Counterexamples to "whatever the wiring" and "tests the neuron model, not the map", all at noise 0 in the same clean box:
- The mf female (fly2 off_mf_t1-5_clean) walks on the male's cVA: walk duty 0.464-0.503, DNa L/R 11.9-13.0 / 11.75-13.2 Hz.
- The MaleCNS male in his four untouched clean trials has DN all 1.36-1.38 Hz and DNa L 2.3 Hz. The female has 0.000. Only the connectome differs.
- In a degree-preserving rewired female brain (the shuffle file), cVA gives DNa 0/0 against 10.2/7.3 intact, and food odour 0/0 against 22.9/13.1. Walking on an input is carried by the wiring.

Minor: the verifier gave "DNa ~14-17 Hz" on the hum. Across all hum (noise0.2) female logs the range is 3.5-19.9 Hz. The original ff series is 9.0-16.8 Hz and the rep-noise0.2 ff series is 3.5-10.3 Hz.

Net: the paper's clause "the published model has no activity of its own" is literally true. It does, however, present a guaranteed property of the neuron model as the whole cause and as a finding about the wiring. "Every neuron at rest" is wrong. The verifier's replacement fixes the framing but goes too far the other way ("cannot come from this model whatever the wiring", "tests the neuron model, not the map"), and it keeps an untrue premise. The softened sentence ("needs some input ... that this model does not supply") is also imprecise: the model walks on inputs, through the wiring.

Scratch scripts not kept. (a.py, b.py, c.py). They are read-only pandas reads.
WORDING: "The model cannot walk by itself either. In a clean box with no flowers, two simulated females stood still for more than two minutes of brain time. Light on their eyes and the smell of the other fly kept about 8 % of their neurons firing, but none of it reached a single descending neuron. The model's neurons, as Shiu et al. built them, have no activity of their own: a neuron with no input stays at rest, so nothing in this brain can start walking unprompted. Given a smell that reaches the walking neurons, such as a male's cVA in the same clean box, the same female walks about half the time. A real fly put in an empty dish soon starts walking about \citep{martin2004portrait}. Walking about unprompted, the most ordinary thing a fly does, was the first behaviour on my list that this model does not produce. That is partly by construction (no neuron has activity of its own) and partly the wiring (nothing in an empty box reaches the neurons that walk)."

Note 5 (l.145) addition: "Clean box, two females: every readout 0.00 in 10 recordings of 135 +/- 6 s of brain time each, while 7-8 % of neurons (about 41,000 spikes per 50 ms, from the eye and the partner's odour) fired; with no input at all the model is silent by construction."

>>> REFUTE [deciders] Critique: female walking is read only from DNa01/02 + DNp09, and DNp09 is silent (the freeze is DNa suppression by construction of the decoder): upheld=True
EVIDENCE: VERDICT: CONFIRMED, headline=true. It touches the conclusions "females stay together because touch stops steering" and "freeze when touched" as a wiring reflex. I re-derived every number from the files and could not refute the core point. Three of the verifier's side claims are too broad; they are listed at the end.

Paper sentences (paper/flycraft.tex):
- l.93: "Touch also switched off the neurons she steers with, which I had not expected, so a touched female freezes."
- l.101: "...and then stayed together, because touch switched off their steering while their ovipositors kept going."
- l.123: "touch a walking fly on the head and its steering neurons should fall quiet, so that two flies bumping heads should stop together."
- Note 11 lists only "how firing becomes movement" as my choice. The word DNp09 appears nowhere in the paper, and nothing says walking is read from the steering neurons.

1) The decoder (brain/flybrain/motor.py)
- Without a nerve cord (has_vnc False), walk = 1-exp(-rate('forward')/10 Hz) and turn = tanh((turn_L - turn_R)/40 Hz).
- The forward group is DNp09|DNa01|DNa02: 6 neurons (logs/trial_off_ff_1_clean.out: DNa02 x2, DNp09 x2, DNa01 x2). turn_L and turn_R are the same DNa01/02, 2 per side.
- So forward = (DNp09 + DNa_L + DNa_R)/3. I checked this against all 165 fly*_off-*.csv logs, female rows. hz_forward matches that formula to within 0.003 Hz in every log, and ctl_walk equals 1-exp(-hz_forward/10) exactly (max error 0.0).
- Consequence: walking and steering are read from the same 4 DNa neurons. Silencing them is the freeze by construction.

2) DNp09 does not respond to any sense
- contact_stop_flywire.csv (frozen copy), all 56 rows: 'DNp09 alone' 0.0-0.67 Hz, 'DNp09 +touch' 0.0-0.33 Hz.
- social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv: 0.0 for every input and seed, except eye bristles (seed values 0.5/0.5/0.5/0/0, mean 0.3).
- 0.0 in every row of the odor_dose (4 files), state_probe (5 files), expression_probe and precontact_dose (no-hum) files.
- Arena, female logs: hz_dnp09 mean is 0.000 in every no-hum series and 0.20 in every hum series, which is the hum's own 0.2 Hz. Single ticks reach 20 Hz with the hum.

3) Touch in the paper's model (contact_stop row 0, food odour)
- DNa L/R: 20.33/12.33 alone -> 6.83/3.17 with touch. Suppression 0.69.
- DN all: 1.27 -> 8.38 Hz.
- cVA row: DNa 9.33/8.17 -> 0/1.17 (0.93); DN all 1.61 -> 8.29.
- social_probe: touch alone gives DN all 8.03-8.09 Hz (none: 0.00).
- The touch drive is all 1,417 BM_ neurons (1,113 of them BM_InOm eye bristles) at R_BURST = 200 Hz (senses.py l.33 and l.200; the .out logs).
- dn_all has 1,303 neurons.

4) Arena, my model, per label (far = near_dist >= 3.5; contact = taste of the other fly)

| Series | DNa far | DNa contact | Walk far | Walk contact | DN all far | DN all contact |
|---|---|---|---|---|---|---|
| off_ff (flower) | 12.5 | 0.22 | 0.49 | 0.01 | 3.8 | 12.3 |
| ff hum | 16.0 | 1.23 | 0.57 | 0.07 | 4.1 | 12.9 |
| ff rep-hum | 16.4 | 0.62 | 0.58 | 0.04 | 3.9 | 13.0 |
| mf / mf_clean / mf hum / virgin | 12.4-17.1 | 0.14-1.96 | 0.48-0.61 | 0.01-0.10 | 3.5-4.2 | 12.2-13.2 |
| mf_rep-clean (only 18 contact ticks) | 14.8 | 5.15 | - | 0.25 | 2.4 | 11.9 |

- The females stay together because the walk drive falls to about 0, and that drive is read from DNa. A turning loss alone would not keep them together, so "because touch switched off their steering" only makes sense once the decoder is disclosed.
- The verifier's ranges (DN all 3.6-4.1 far, 11.9-13.4 on contact) match mine within series variation.

Where the verifier goes too far
(a) "DNp09 never fires above 0.7 Hz in any condition": not quite. In noise_floor_flywire_shiu_min1+known+eln0.25.csv, DNp09 reaches a 1.33 Hz mean (seed max 2.0) at 0.3-1 Hz noise. The gain_sweep and sensitivity tables do not record DNp09 at all. The accurate statement is "0 Hz to every sense; with the hum, about the hum's own rate".
(b) "most other DNs speed up": not established. Only the mean over 1,303 DNs is recorded, and no per-DN-type touch file exists. The rise could come from a subset, for example grooming DNs or DNp13. Putting "although it raised the average descending neuron" into l.93 hints that the fly "should" walk, which the data do not show. That fact belongs in Note 4.
(c) The bench food row is a 69 % cut (6.8/3.2 Hz left), not silence. "Switched off" or "silenced" is fair only for the arena (86-99 %) and for the cVA row.

Also relevant to l.123: antennal bristles alone raise DNa R from 0 to 5.4 Hz (L 1.3). The model's "head touch" is mostly eye bristles.

Scratch scripts not kept.
WORDING: l.93: "Touch also quietened the neurons she steers with, DNa01/02, which I had not expected. Those are also the neurons I read her walking from, so a touched female freezes." Add after "so the freeze is carried by the weakest connections in the brain": "It is a fall in those two neurons only; her descending neurons as a whole fire more on touch (Note 4)."

Note 4, after the freeze numbers: "Touch here is all 1,417 head and eye bristle neurons at 200 Hz. The mean rate of the 1,303 descending neurons rises with it, from 1.3 to 8.4 Hz with food odour and from 1.6 to 8.3 Hz with cVA. The freeze is therefore a fall in the neurons my walking readout uses, not in descending output as a whole. Antennal bristles alone raise DNa R to about 5 Hz."

l.101: "...and then stayed together, because touch quietened the neurons I read their walking and steering from, while their ovipositors kept going."

l.121: "how to freeze when touched" -> "how to quiet its steering neurons when touched".

l.123: "touch a walking fly on the head and eyes and its steering neurons, DNa01/02, should fall quiet; if those neurons carry walking as well as steering, as my readout assumes, two flies bumping heads should stop together."

Note 11, after "how firing becomes movement": "(the female has no nerve cord, so I read her walking from six descending neurons, DNp09 and DNa01/02, as 1 - exp(-mean rate/10 Hz), and her turning from DNa left minus right, tanh of the difference over 40 Hz; DNp09 answers no sense, 0 Hz without the hum and the hum's own 0.2 Hz with it, so she walks and steers on DNa01/02 alone)".

### [states] 16a. NPF raises sugar->MN9 by +6.8 Hz vs +3.6 to +4.4 Hz for unrelated states
PAPER: l.97: "Hunger is another matter. Keeping the fly's hunger and fullness neurons firing changes nothing, in either sex." Note 6, l.147: "IPC, DH44, NPF, SIFa and AstA change no readout specifically (at most 7\,Hz on MN9, as much as unrelated states)."
VERDICT CONFIRMED headline=True
EVIDENCE: release/pre_rerun_20260926/results/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv (the paper's model), rows input=='sugar GRNs', column MN9, mean of 5 seeds: none 79.4 (74/80/79/81/83); NPF 86.2 (84/91/86/83/87), so +6.8; the unrelated states give SAG +4.4, pC1d/e +4.4, pC1a-c +4.2, aIPg +3.6; the other hunger and satiety states give DH44 +3.0, IPC +0.6, SIFa -0.4, AstA -1.6. NPF is therefore 1.5-1.9x every unrelated state, so "as much as unrelated states" is wrong for NPF. The "at most 7 Hz" part holds. Statistics, scipy: NPF vs none paired t=3.97, p=0.017 (uncorrected); NPF vs the 20 pooled unrelated-state values, Welch p=0.15, so it cannot be told apart from them at n=5. The feeding-MN population (feed MNs) moves 24.8 -> 25.9 under NPF, against +0.6 to +2.0 for unrelated states, which is not specific. Under the published lobe (state_probe_flywire_shiu_min1_state30.csv) NPF gives +5.0, inside the unrelated band of +3.6 to +7.8. That file is contaminated by runaway seeds: none seed 4 has 284k spikes and MN9 58; NPF seed 0 has 303k spikes and MN9 54. The 100 Hz file gives NPF -3.3 (sd 13.6) and DH44 +8.0 (sd 1.0). "In either sex": in both male files sugar->MN9 is 0.0 and feed MNs are about 0.4 Hz in every state (pooled MaleCNS taste labels, RESEARCH_NOTES 19f). The male test therefore cannot show a hunger effect on feeding. Its largest hunger/satiety change is MDN +3.9 to +5.8 Hz with touch. Under the published male lobe, NPF and SIFa + sugar raise PPL1 by +26 and +34 Hz: 5/5 runaway seeds against 3/5 with no state, and P1 also gives 5/5, so the effect is not specific. Headline: the result qualifies "hunger does nothing" but does not reverse it.
WORDING: Main text: "Keeping the fly's hunger and fullness neurons firing changed nothing that unrelated states did not also change, in a brain with no background activity (in the male the feeding readout is silent in any state, so there the test says nothing about feeding)." Note 6: "IPC, DH44, NPF, SIFa and AstA change no readout specifically. The largest shift is NPF's on MN9 with sugar, 79.4 -> 86.2 Hz (+6.8, 5 seeds), against +3.6 to +4.4 for the virgin, aroused and aggressive states (NPF vs those, p = 0.15). The feeding motor population moves by at most 2 Hz under any state."

### [states] 16b. Hunger neurons recruit zero spikes at rest (proposed as the stronger supporting fact)
PAPER: l.97: "In real flies these neurons work mostly by releasing neuropeptides into the brain \citep{pool2014feeding}, and a wiring diagram records their wires but not their chemistry." (the fact is proposed as support; the paper does not state it)
VERDICT PARTLY headline=False
EVIDENCE: All state_probe_*.csv files, input=='none'. Recruited neurons = active_frac x N - n_driven (N = 139,248 female, 164,439 male). The Poisson draws of driven neurons are identical across files (AstA spikes 71/57/63/45/46 and DH44 197/177/167/158/168 in every file), so extra spikes measure recruitment. Female, 30 Hz, both lobes: NPF 4 driven -> 4 active, IPC 18 -> 18, DH44 6 -> 6, AstA 2 -> 2, so exactly zero recruited. SIFa recruits 0 in the paper's model and 1-2 neurons (about 6 spikes/s) in the published lobe. Male, 30 Hz, both lobes: NPF 4 -> 7-8 active (3-4 recruited, spikes 141/131/118/109/111 vs 130/126/113/100/104, so +7.4 spikes/s); SIFa 4 -> 6 (+11 spikes/s); IPC, DH44 and AstA recruit 0. Female, 100 Hz (published): NPF 4 -> 6-7, SIFa 4 -> 6, IPC/DH44/AstA 0. For contrast, SAG 2 driven -> 37-105 active (241-570 spikes/s) and pC1a-c 6 -> 78-119 active. "Zero" is exact only for IPC, DH44, AstA everywhere and for NPF in the female at 30 Hz. The male's NPF and SIFa recruit a handful of neurons (at most about 11 spikes/s).
WORDING: "At rest the hunger and satiety neurons excite almost nothing downstream. Driven at 30 Hz in the female, IPC, DH44, NPF and AstA recruit no other neuron. In the male, NPF and SIFa recruit 2-4 neurons for about 10 spikes a second. The two virgin neurons (SAG), by contrast, recruit 37-105 neurons."

### [states] 16c. Say "in a silent brain" until S19 (hunger on the hum) has run
PAPER: l.97: "Keeping the fly's hunger and fullness neurons firing changes nothing, in either sex."
VERDICT CONFIRMED headline=True
EVIDENCE: experiments/state_probe.py calls make_sim(cx, gain=a.gain) with no noise argument; experiments/common.py make_sim defaults to noise_hz=0.0. Every state probe therefore ran with no background activity: no-state rows have total_spikes 0 at rest. A grep for NPF over release/pre_rerun_20260926/results/ finds only the five state_probe files, so no hum/substrate run of any hunger state exists. S19 in design_plan.md is still pending. The zero recruitment in 16b is itself a consequence of the silent brain: NPF's targets sit below threshold with nothing else driving them. Headline: this narrows the scope of the "hunger does nothing" conclusion.
WORDING: "In a brain with no background activity, keeping the fly's hunger and fullness neurons firing changes nothing specific in the female, and nothing measurable in the male, whose feeding readout is silent anyway." (Keep this until the hum run exists.)

### [states] 17a. "vpoDN 5.7 Hz" is the pooled vpoEN + DNp37 readout
PAPER: Note 6, l.147: "SAG $\rightarrow$ pC1a 21, pC1b/c 19 and vpoDN 5.7\,Hz, all from 0; with touch, pC1d/e 6.2\,Hz." Main text l.97: "her deciding neurons wake up, together with the neuron that opens her genital plate to accept a male."
VERDICT CONFIRMED headline=False
EVIDENCE: experiments/common.py output_groups: "vpoEN/DN accept": s(any_of={"cell_type": "^vpoEN$|^DNp37$"}). In data/Supplemental_file1_neuron_annotations.tsv that is 4 vpoEN (2 L, 2 R) plus 2 DNp37, whose hemibrain_type is vpoDN, so 6 neurons. The readout is counts summed over the group / 6 / s. state_probe_flywire_shiu_min1(+known+eln0.25)_state30.csv, SAG tonic, input none, column "vpoEN/DN accept" = 5.73 Hz in both files, about 34 spikes/s over 6 neurons. No results file splits the two types. Indirect evidence that vpoDN itself fires: the arena readout "accept" in brain/flybrain/motor.py is ^DNp37$ only, and under the same SAG 30 Hz state it gives hz_accept 15.3-16.5 Hz (logs/fly2_off-flywire-virgin-noise0.2-known-eln0.25_*.csv, 10 logs, mean about 15.9). Two DNp37 neurons at about 16-17 Hz would account for nearly all of the pooled 34 spikes/s. So the genital-plate sentence is probably right, but "vpoDN 5.7 Hz" understates vpoDN's own rate by about 3x and mixes in its upstream vpoEN.
WORDING: "SAG -> pC1a 21, pC1b/c 19 Hz, and 5.7 Hz averaged over the four vpoEN and two vpoDN (DNp37) neurons, all from 0." Once the split readout exists, better: "vpoDN (DNp37) about 17 Hz" (the arena's DNp37-only readout under the same state gives 15-16.5 Hz).

### [states] 17b. "identical under both smell-centre settings" holds only for the state-alone rows (max 0.3 Hz)
PAPER: Note 6, l.147: "The state results are identical under both smell-centre settings."
VERDICT PARTLY headline=False
EVIDENCE: Compared shiu_min1_state30 against shiu_min1+known+eln0.25_state30 (female) and all_min1_state30 against all_min1+eln0.25_state30 (male), taking the mean over seeds for each (state, input) cell. State-alone rows (input none): max |diff| 0.3 Hz in the female (aIPg -> DNa L) and 0.0 in the male; per seed at most 1.5 Hz. The item's "only" is too narrow. State + non-smell inputs also agree: touch within 2.0 Hz (the largest is IPC + touch -> DNp13), sound (JO-A) within 0.4, and in the male touch, contact pheromone and ppk25+touch give 0.0. State + odour cells differ by up to 110 Hz (57 of 80 female and 56 of 88 male state x input cells differ by more than 5 Hz). For example, cVA+touch -> DNp13 is 17.7-19.0 under the published lobe and 35.3-37.9 under the paper's. State + sugar cells differ by up to 13 Hz (female PPL1) and 92 Hz (male PPL1) because of runaway seeds. Every number Note 6 prints is in an agreeing row (SAG alone, pC1a-c alone, P1 alone, SAG + touch -> pC1d/e 6.3/6.2, touch -> DNp13, oviDN 0) except the hunger line: NPF sugar->MN9 +5.0 vs +6.8, and under the published male lobe NPF/SIFa + sugar -> PPL1 +26/+34 Hz. So the blanket claim is overstated, as the item says, but the numbers Note 6 prints (apart from the hunger line) do hold under both settings.
WORDING: "The state-alone results, and the state results with touch or sound, are the same under both smell-centre settings (within 0.3 and 2 Hz). Results with an odour, or with sugar under the published lobe, are not."

### [states] 17c. "mated" is the no-state run
PAPER: Note 6, l.147: "DNp13 fires at 36\,Hz virgin or mated, and oviDN stays at 0 under every state." Main text l.97: "a mated female extends her ovipositor no more often than a virgin."
VERDICT CONFIRMED headline=False
EVIDENCE: experiments/state_probe.py docstring: "With no state drive the model is, in effect, a mated (SAG silent), starved (IPC silent), unaroused fly." The "mated" comparison is state=='none'. Touch -> DNp13: none 35.6 (paper's model) / 36.1 (published) against SAG 36.2 / 36.2. Nothing mating-specific was imposed: no sex-peptide or SPSN drive and no post-mating state. "Mated" is simply SAG silent, which is also the default of every other experiment in the paper.
WORDING: "DNp13 fires at 36 Hz whether or not the virgin neurons are driven (the undriven brain stands in for a mated female), and oviDN stays at 0 under every state."

### [states] 17d. Song MNs at 28 Hz are not state-specific (contact pheromone alone gives 21)
PAPER: Note 6, l.147: "P1 $\rightarrow$ pIP10 50, TN1 8 and the song motor neurons 28\,Hz \citep{vonphilipsborn2011neuronal}." Main text l.97: "Keep a male's courtship neurons firing and his brain sends its song command to the wing, with nobody there to sing to."
VERDICT CONFIRMED headline=False
EVIDENCE: state_probe_malecns_all_min1+eln0.25_state30.csv, column "song MNs" (14 neurons: ps1, i1, i2, hg1-4 MN). P1 state, input none: 27.6 Hz. With no state, contact pheromone (ppk23/25) alone gives 21.3 Hz, and "all pheromones + contact + touch" alone gives 30.9 Hz, above the P1-alone value. cVA+touch gives 14.4, cVA 12.0, touch 10.5. The published-lobe file gives the same. By contrast pIP10 is specific (50.4 under P1 against at most 3.8 without P1 in the paper's model, at most 8.3 in the published), and so is TN1 (8.2 against at most 2.0). The song-command claim therefore rests on pIP10/TN1, not on the song MNs.
WORDING: "P1 -> pIP10 50 Hz (at most 4 without the state) and TN1 8 Hz (at most 2). The song motor neurons reach 28 Hz, but contact pheromone alone drives them at 21 Hz, so only pIP10 and TN1 are specific to the state."

### [states] 17e. "One class": P1 is 148 neurons of 45 types
PAPER: Note 6, l.147: "\emph{Internal states} (one class of the fly's own state neurons driven at 30\,Hz)."
VERDICT CONFIRMED headline=False
EVIDENCE: experiments/common.py state_groups: "courting male (P1/pC1 tonic)": cell_type ^pC1_|^P1_. In data/malecns_neurons.csv.gz this matches 148 neurons (74 L, 74 R) of 45 types, all named pC1_* (pC1_1a ... pC1_19); none is named P1_. Dimorphism: 126 male-specific, 22 potentially. fru/dsx: 49 coexpress_high, 39 coexpress_low, 48 dsx_high, 6 dsx_low, 6 NA. The group is therefore the whole male pC1 cluster, including dsx-only neurons, and not a single class. n_driven in state_probe_malecns_*: 148. For comparison, the other driven sets: SAG 2, pC1a-c 6, pC1d/e 4, female aIPg 23 (male 16), IPC 18 (male 16), DH44 6, NPF 4, SIFa 4, AstA 2.
WORDING: "Internal states (a labelled group of the fly's own state neurons driven at 30 Hz: SAG 2 neurons, pC1a-c 6, aIPg 23, IPC 18, DH44 6, NPF 4, SIFa 4, AstA 2; in the male, the whole pC1/P1 cluster of 148 neurons in 45 MaleCNS types)."

### [states] 17f. At 100 Hz (published file), pC1a-c lowers touch->DNp13 from 36 to 29 Hz
PAPER: Note 6, l.147: "DNp13 fires at 36\,Hz virgin or mated, and oviDN stays at 0 under every state." Main text l.97: "It also gets two things wrong, since no state starts egg-laying and a mated female extends her ovipositor no more often than a virgin."
VERDICT CONFIRMED headline=False
EVIDENCE: state_probe_flywire_shiu_min1_state100.csv (published lobe, 3 seeds), input "touch (all head bristles)", column "DNp13 reject": none 36.3 (35/38/36); pC1a-c 29.0 (29.5/29.5/28), so -7.3 in every seed. The virgin state SAG at 100 Hz also lowers it, to 32.8 (31/35.5/32), -3.5 in every seed. With cVA+touch: none 17.3, pC1a-c 12.2, SAG 16.5. At 30 Hz the rejection output is state-blind (35.6-37.7 in the paper's model, 35.7-37.7 published), so the paper's sentence holds at 30 Hz only. At the stronger dose the virgin/aroused state lowers rejection, the real-fly direction, which weakens the "mated extends no more often than a virgin" miss. No 100 Hz run exists under the paper's lobe.
WORDING: "DNp13 fires at 36 Hz with the virgin neurons driven at 30 Hz or not driven, and oviDN stays at 0 under every state. Driven at 100 Hz (published lobe, 3 seeds), the virgin neurons lower it to 33 Hz and pC1a-c to 29 Hz." In the main text: "...and, at the dose used, a mated female extends her ovipositor no more often than a virgin."

>>> REFUTE [states] 16a. NPF raises sugar->MN9 by +6.8 Hz vs +3.6 to +4.4 Hz for unrelated states: upheld=True
EVIDENCE: VERDICT: upheld, but it is a wording correction (PARTLY on substance). headline=true only in that it qualifies "hunger does nothing"; it does not reverse it.

Paper sentences. Main text, l.97: "Keeping the fly's hunger and fullness neurons firing changes nothing, in either sex." Note 6, l.147: "IPC, DH44, NPF, SIFa and AstA change no readout specifically (at most 7\,Hz on MN9, as much as unrelated states)."

Which file is right: the paper's model is PAPER_F = "shiu_min1+known+eln0.25" (experiments/paper_numbers.py l.15, l.195). So the file is release/pre_rerun_20260926/results/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv, rows input=='sugar GRNs', column MN9, seeds 0-4.

My numbers, re-derived. They match the verifier to the digit.
- No state: 79.4 (74/80/79/81/83).
- NPF: 86.2 (84/91/86/83/87), so +6.8.
- Unrelated states: SAG +4.4, pC1a-c +4.2, pC1d/e +4.4, aIPg +3.6.
- Other hunger/satiety states: DH44 +3.0, IPC +0.6, SIFa -0.4, AstA -1.6.
- Across every input, the largest MN9 shift from any unrelated state is +4.6 (SAG with cVA+sugar). NPF's +6.8 is therefore 1.5x the largest unrelated shift.
- Feeding-MN population: NPF +1.14; unrelated states +0.62 to +1.99; range over all states 24.8-26.7.
- For each hunger state, the largest change on any readout under any input is MN9: NPF 6.8, SIFa 4.0, IPC 3.2, DH44 3.0, AstA 2.2.

Statistics (scipy):
- NPF vs no state: paired p=0.017, Welch p=0.011, uncorrected. Bonferroni over the 5 hunger states gives 0.085.
- NPF vs the 4 unrelated states pooled: Welch p=0.154, Mann-Whitney p=0.19.
- NPF vs each unrelated state: Welch p=0.22-0.35, paired p=0.15-0.37.
- NPF vs the per-seed mean of the unrelated states, paired: p=0.12.
- One-way ANOVA across all 10 states: p=0.17.
- The unrelated states pooled vs no state: p=0.05. So "any tonic drive nudges MN9 up" is the better description.

Why "as much as unrelated states" fails: NPF's point estimate exceeds every unrelated state, so the phrase is not literally true in the paper's model. The substance does hold: NPF cannot be told apart from the unrelated states at n=5, and no other hunger state comes near them.

The published lobe (the reading that would refute the verifier): in state_probe_flywire_shiu_min1_state30.csv the note is literally right. NPF gives +5.0 and DH44 +7.2, against unrelated +3.6 to +7.8 (aIPg +7.8, pC1a-c +6.4). That file is not the paper's model, though, and runaway seeds contaminate it:
- no state, seed 4: 284,010 spikes, MN9 58;
- NPF, seed 0: 303,278 spikes, MN9 54.
Its DH44 -12.2 Hz on PPL1 with sugar comes entirely from that runaway seed 4 in the no-state row (PPL1 0,0,0,0,61.1). So it cannot rescue the wording.

Also checked:
- At 100 Hz, NPF gives -3.3 and DH44 +8.0 (sd 1.0), as the verifier says. The verifier's NPF sd of 13.6 is slightly off: 59/84/84 gives 14.4 (ddof=1).
- Male, paper's model (state_probe_malecns_all_min1+eln0.25_state30.csv):
  - Sugar drives MN9 at 0.0 in every state, and the feeding MNs sit at 0.35-0.42 Hz. The male test therefore cannot show a hunger effect on feeding.
  - The largest hunger/satiety change is on MDN: IPC 4.7, DH44 5.0, NPF 3.9, SIFa 5.8 (ppk25+touch: 31.2 vs 25.4 sd 4.5), AstA 4.6. That is within noise and within the P1 and aIPg band.
- Published male lobe: NPF +26.1 and SIFa +34.2 on PPL1 with sugar. Runaway seeds (over 170k spikes) occur in NPF 5/5, SIFa 5/5 and P1 5/5, against no state 3/5. The verifier is right that these are not specific.

Supporting fact the verifier left out: at rest (input 'none'), the hunger states produce total spikes within about 50 of what their own driven neurons fire (total minus n_driven x 30 Hz: female IPC -47, DH44 -7, NPF -5, SIFa -5, AstA -4; male -34 to +6). SAG recruits +313, pC1a-c +529, pC1d/e +395, aIPg +2,140 and P1 +18,468. This backs the "synapses vs chemistry" line directly.

Assessment of the verifier's corrected wording: it is accurate and does not go too far. "Changed nothing that unrelated states did not also change" matches ANOVA p=0.17 and NPF-vs-unrelated p=0.12-0.35. "In a brain with no background activity" is true: the probe runs with no noise, and design_plan section 4 item 16 asks for "in a silent brain" until S19 runs. I would add the zero-recruitment fact and the ANOVA to Note 6.

Scratch scripts not kept. (read-only pandas/scipy).
WORDING: Main text (l.97): "Hunger is another matter. The fly's hunger and fullness neurons, kept firing, switch on no other neuron in a brain with no background activity. With sugar on the tongue they move the feeding neuron no more, within noise, than unrelated states do. In the male the feeding neurons are silent in every state, so there the test says nothing about feeding."

Note 6 (replace the IPC... sentence): "IPC, DH44, NPF, SIFa and AstA fire no neuron but their own at rest (total spikes within 50 of the driven cells', against +313 to +2,140 for SAG, pC1 and aIPg). They change no readout specifically. The largest shift is NPF's on MN9 with sugar, 79.4 -> 86.2\,Hz (+6.8, 5 seeds), against +3.6 to +4.4\,Hz for the virgin, aroused and aggressive states (NPF vs those, Welch p = 0.15; across all ten states, ANOVA p = 0.17). The fed states move MN9 by +0.6 and +3.0\,Hz, SIFa and AstA by -0.4 and -1.6\,Hz, and the feeding motor population by at most 2\,Hz under any state. In the male, sugar drives MN9 at 0\,Hz in every state (pooled taste labels), and the largest hunger or satiety change on any readout is 3.9-5.8\,Hz on MDN with touch."

(Also drop or qualify the later "The state results are identical under both smell-centre settings", per design_plan section 4 item 17. It holds only for the state-alone rows. The published-lobe state x input cells differ because of runaway seeds.)

>>> REFUTE [states] 16c. Say "in a silent brain" until S19 (hunger on the hum) has run: upheld=True
EVIDENCE: I could not refute it. I re-derived everything from release/pre_rerun_20260926/results/ and the verifier's main point holds. Two parts of its supporting argument and one clause of its suggested wording are wrong, though.

Paper, l.97: "Keeping the fly's hunger and fullness neurons firing changes nothing, in either sex." Note 6 (l.147) says: "IPC, DH44, NPF, SIFa and AstA change no readout specifically (at most 7 Hz on MN9, as much as unrelated states)."

1. There was no background activity in any hunger test (CONFIRMED)
- experiments/state_probe.py calls `make_sim(cx, gain=a.gain)` with no noise argument, and experiments/common.py has `def make_sim(cx, gain=1.0, noise_hz=0.0, ...)`.
- The state="none", input="none" rows have total_spikes = 0 and active_frac = 0 in all five state_probe CSVs (female eln0.25 and shiu at 30 Hz, shiu at 100 Hz, male eln0.25 and all at 30 Hz). logs/reproduce_state.out and logs/state_probe_*.out print "act 0.0%" for none/none.
- No hunger state exists anywhere with the hum:
  - experiments/results_edge/ holds only `_smoke` (arena_audit, conditioning_edge and similar), with no state probe.
  - Every run_pair.sh / run_flock.sh log I checked uses `--state virgin` or courting, never fed or hungry.
  - S19 is still pending in design_plan.md l.229, and DECISIONS.md item 8 raises it to 10 seeds. design_critique.md item 3 adds that "the male is never tested on the hum".
- "No background activity" describes the setup more exactly than "silent brain". During the input trials the brain is not silent: sensory drive at 100 Hz activates 1.4-6 % of neurons. The hum (0.2 Hz on every neuron) is what is missing, and the arena behaviours all ran on it.

2. "Nothing" really means "nothing specific", even without the hum
I used the paper's model files: state_probe_flywire_shiu_min1+known+eln0.25_state30.csv and state_probe_malecns_all_min1+eln0.25_state30.csv, 5 seeds each. Each hunger state is compared with the no-state row for the same input, using the Welch SE of the difference.

Female, 891 hunger cells:
- Largest change: NPF with sugar GRNs, MN9 79.4 ± 3.4 → 86.2 ± 3.1 Hz, +6.8 (SE 2.05, t = 3.3).
- Unrelated states on the same cell: SAG +4.4, pC1a-c +4.2, pC1d/e +4.4, aIPg +3.6. NPF against SAG differs by 2.4 Hz with SE 2.4, so the two cannot be told apart.
- The other hunger states on that cell: IPC +0.6, DH44 +3.0, SIFa -0.4, AstA -1.6.
- Next largest: SIFa with cVA + sugar, DNa L +3.6 (t = 4.8). pC1d/e does +3.4 on that cell.
- Feeding MNs move by at most 1.3 Hz.

Male, 1,308 hunger cells:
- Largest change: SIFa with ppk25 + touch, MDN 25.4 → 31.2, +5.75 (paired SE 1.5).
- IPC with touch, MDN 9.9 → 14.6, +4.65 (t = 3.4). All five hunger states raise touch → MDN by +2.1 to +4.7.
- The unrelated states move the same cells as much or more. P1 changes touch → MDN by +6.2 and cVA + touch → MDN by -14.0; aIPg changes them by -1.6 and -4.2.

3. The verifier's clause "whose feeding readout is silent anyway" is WRONG
- In the male, sugar → MN9 is 0 in every state, because MaleCNS pools the sugar and bitter taste neurons under one label.
- But MN9 itself fires at 32.9 Hz under cVA with no state, and the five hunger states leave it at 32.1-33.5. The feeding readout was live and did not change.
- The male's changes (up to 5.75 Hz, t up to 3.4) can be measured cell by cell. They are just not specific to hunger. So "nothing measurable" overstates it in the other direction, and "nothing specific" fits both sexes.

4. The verifier's claim that "zero recruitment is itself a consequence of the silent brain" is overstated
At rest, with active neurons counted as active_frac × N (female N = 139,248, male N = 164,439):
- Female hunger states recruit exactly 0 neurons beyond the ones they drive.
- In the same silent brain, SAG drives only 2 neurons and recruits 55; pC1a-c recruits 94 and aIPg 167.
- Male NPF recruits 3.6 neurons and SIFa 2.
So zero recruitment partly reflects how weak these neurons' synaptic output is, not only the silence. A below-threshold effect could still appear on the hum, and a null result is exactly the kind of result the hum could overturn. So the scope caveat is needed.

Headline: yes. It narrows "hunger does nothing" but does not overturn it.

Scratch scripts not kept. (a.py through e.py). No project files were changed.
WORDING: "In a brain with no background activity, keeping the fly's hunger and fullness neurons firing changes nothing that unrelated states do not also change, in either sex." Keep this until S19 (hunger on the hum) has run. For Note 6: "IPC, DH44, NPF, SIFa and AstA change no readout specifically, measured without the hum: at most 6.8 Hz on the female's MN9 with sugar, where unrelated states give 3.6-4.4 Hz, and at most 5.8 Hz on the male's MDN with touch, where P1 and aIPg move the same cells by 1.6-14 Hz. In the male, sugar does not reach MN9 because of the pooled taste labels, but MN9 fires at 33 Hz on cVA and no hunger state changes that." Do not use the verifier's "nothing measurable in the male, whose feeding readout is silent anyway".

### [learning] 18a - offline appetitive numbers (CS- kept drive, learning index, no-US control)
PAPER: Offline, in the design of \citet{tully1985classical} (three cycles of 10\,s), the paired odour keeps 0.10--0.11 of its drive and the other 0.59--0.66: learning index $0.54 \pm 0.02$ ($n=6$), 0.04 without a teaching signal, $0.21 \pm 0.14$ for punishment, 0.80 and 0.77 in the male. (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: release/pre_rerun_20260926/results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_{vinegar-vs-ester,ester-vs-vinegar}_seed{0,1,2}.csv, row 'drive reward-comp', retained = post_CS±/pre_CS±. CS+ 0.0951/0.0959/0.0967 (vinegar+) and 0.0967/0.1030/0.1074 (ester+), so 0.10-0.11 is right. CS- 0.5933/0.6335/0.6411 and 0.6970/0.6606/0.6559, so the range is 0.59-0.70; the paper's 0.66 top is stale (ester+ seed0 gives 0.697). LI (CS- minus CS+) = 0.498, 0.538, 0.544, 0.600, 0.558, 0.549: mean 0.548, sd 0.030 (np.std, the paper_numbers convention; 0.033 with ddof=1), so 0.55 +/- 0.03, not 0.54 +/- 0.02. The paper's values are the older 18f table (0.62-0.66, 0.54 +/- 0.02), i.e. from before the 25 Sep regeneration that Note 10 says the paper uses. No-US: us-wiring_vinegar-vs-ester seeds 0/1/2 give LI 0.024/0.084/0.040 and us-wiring_ester-vs-vinegar has seed0 only, LI -0.014. Mean 0.033 (sd 0.035), n=4, split 3+1 across the odour orders; the paper says 0.04. The male figures, 0.798 and 0.771 (n=2 each, seed 0), are correct.
WORDING: Offline, the paired odour keeps 0.10-0.11 of its drive (the rule's floor) and the other 0.59-0.70: learning index 0.55 +/- 0.03 (n = 6: both odour orders x 3 seeds), 0.03 without a teaching signal (n = 4; three runs in one odour order, one in the other), ... 0.80 and 0.77 in the male (n = 2 each, no no-teaching control).

### [learning] 18b - 'a tenth' is the floor constant w_min = 0.1
PAPER: After three pairings the smell that came with sugar reached the output neurons at a tenth of its old strength, while the other smell kept about three-fifths of its strength, and the same happened in Minecraft when the fly walked on flowers that tasted of sugar. (l.99)
VERDICT CONFIRMED headline=False
EVIDENCE: brain/flybrain/plasticity.py l.58: PlasticityConfig.w_min = 0.1 ('floor as fraction of w0'); l.164: w = np.maximum(w + dw, c.w_min * self.w0). Note 7 itself says 'floor 10 %'. The CS+ retained drive in all 6 appetitive runs is 0.095-0.107, the floor plus KC-rate noise between the pre and post tests; the punishment CS+ runs give 0.091-0.100, and the male 0.100/0.100. So 'a tenth' is a constant I set, not a measured amount of learning. Timing: the per-cycle lines in logs/reproduce_conditioning.out (the 25 Sep regeneration) give the reward-compartment mean weight after cycle 1 / cycle 3 as 0.953/0.944, 0.953/0.945, 0.955/0.946 (vinegar+) and 0.972/0.961, 0.972/0.962, 0.972/0.962 (ester+). That puts 83-85 % (vinegar+) and 72-74 % (ester+) of the three-cycle depression in cycle 1, and CS- blocks do not move it. The rule's constants make this expected: eta 0.3/s, e_ref = d_ref = 20 Hz, US DANs at 50 Hz, so a KC firing at r Hz loses 0.0375*r of w0 per s and hits the floor after 24/r s (1.2 s at 20 Hz; any KC at 2.4 Hz or more within the first 10-s pairing). One limit: CS+-specific drive is not logged per cycle, so 'within the first pairing' is inferred for the drive-weighted readout, not measured directly.
WORDING: Paired with sugar, the smell's synapses fell to the floor I set for the rule, a tenth of their old strength, mostly within the first pairing, while the other smell kept about 0.6-0.7 of its strength.

### [learning] 18c - punishment index 0.21 +/- 0.14 hides the odour order
PAPER: ... learning index $0.54 \pm 0.02$ ($n=6$), 0.04 without a teaching signal, $0.21 \pm 0.14$ for punishment, 0.80 and 0.77 in the male. (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: conditioning_..._us-dan-punish_{vinegar-vs-ester,ester-vs-vinegar}_seed{0,1,2}.csv, row 'drive punish-comp'. The file name gives the CS+ first (the log line reads 'CS+ vinegar ... CS- ester'). LI with vinegar paired: 0.300/0.366/0.379, mean 0.348. LI with ester paired: 0.078/0.073/0.079, mean 0.077. Pooled mean 0.2125, sd 0.138, so the printed 0.21 +/- 0.14 is numerically right but averages a 4.5-fold order asymmetry. The paper sets it beside 0.04, which is the reward-compartment control. The punishment compartment's own no-US control (us-wiring files, drive punish-comp) is +0.256/+0.320/+0.264 (vinegar order, mean +0.280) and -0.236 (ester order, n=1). Associative increment = paired LI minus same-order control: 0.348 - 0.280 = +0.07 with vinegar paired; 0.077 - (-0.236) = +0.31 with ester paired. In CS+ terms, vinegar's punishment input falls to 0.09 with the US against 0.22 without it, and ester's to 0.10 against 0.46.
WORDING: ... for punishment 0.35 with vinegar paired and 0.08 with ester paired (pooled 0.21 +/- 0.14). Vinegar lowers its own punishment input without any teaching signal (control +0.28 in that order, -0.24 in the other), so pairing adds +0.07 with vinegar and +0.31 with ester.

### [learning] 18d - in-world '0.29 with bitter' is matched by a run with no bitter
PAPER: In the world, 0.37 with sugar and 0.29 with bitter. (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: logs/learn_world{5,6}_probe_{pre,post}.json, retained = post/pre drive per odour class; aversive index = ester minus vinegar punish-comp, as in paper_numbers.py section M. world5 (sugar on poppies/ester, bitter on dandelions/vinegar): ester 0.384, vinegar 0.090, index 0.294. world6 (sugar only, BITTER= empty; learn_stats shows us_punish_ticks = 0 in every phase): ester 0.438, vinegar 0.131, index 0.306. The 'aversive' index is as large with no bitter at all, so it is vinegar's tonic odour-evoked PPL1 depressing its own input (16f/16g; offline no-US +0.28 in the vinegar order), not learning. The appetitive world6 index is right: vinegar 0.662 minus ester 0.289 = 0.373.
WORDING: In the world (one run each), 0.37 with sugar alone. The punishment-compartment index of 0.29 in the run with bitter is not learning: the run with no bitter anywhere gives 0.31, because vinegar lowers its own input.

### [learning] 18e - in-world results are n = 1; 'the same happened in Minecraft' is weaker
PAPER: After three pairings the smell that came with sugar reached the output neurons at a tenth of its old strength, while the other smell kept about three-fifths of its strength, and the same happened in Minecraft when the fly walked on flowers that tasted of sugar. (l.99)
VERDICT CONFIRMED headline=False
EVIDENCE: Seven fly1_mb-*_learn_stats.csv logs map to trials smoke2, world1-6. world6 is the only sugar-only run with separated patches and world5 the only separated sugar+bitter run, so each in-world number is n = 1 (one brain, one seed). world4, with overlapping odours, gives an appetitive index of only 0.07 (ester 0.140 vs vinegar 0.211). world6 retained reward-compartment drive: sugar-paired ester 0.289, unpaired vinegar 0.662. Offline: paired 0.095-0.107, unpaired 0.59-0.70. So in Minecraft the paired smell kept about 3x the offline fraction (0.29 vs 0.10), and the index was 0.37 against 0.55.
WORDING: ... and in one Minecraft run, in which the fly walked on flowers that tasted of sugar, a weaker version of the same happened: the sugar-paired smell kept 0.29 of its strength and the other 0.66.

### [learning] 18f - 'Tully & Quinn' was not three 10-s cycles
PAPER: Offline, in the design of \citet{tully1985classical} (three cycles of 10\,s), the paired odour keeps 0.10--0.11 of its drive ... (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: logs/reproduce_conditioning.out and each cond_*.out print the protocol as '3 cycles x [CS+ + reward DANs 10s | rest 5s | CS- alone 10s | rest 5s]'. The test is the synaptic drive post/pre with plasticity frozen, not a choice. Tully & Quinn (1985) trained once: 60 s of CS+ with 12 shock pulses, fresh air, then 60 s of CS- without shock, followed by a T-maze choice test and a performance index averaged over reciprocal groups. The shared features are only the differential (CS+/CS-) and reciprocal (both odour orders) structure. conditioning.py's own docstring says 'Tully & Quinn style'.
WORDING: Offline, in a differential, reciprocal design after Tully & Quinn (the paired odour with the teaching signal, the other without, both odour orders), shortened to three 10-s pairings with 5-s rests, the paired odour keeps ...

### [learning] 18g - '0.0 Hz in every dopamine neuron' is female only
PAPER: Sugar, bitter and touch drive 0.0\,Hz in every dopamine neuron, so the teaching signal drives the identified reward (PAM) or punishment (PPL1) set at 50\,Hz when the fly tastes sugar or bitter. (Note 7, l.149); main text l.99: "In the model, sugar and bitter tastes never reach the teaching neurons, so I supplied the teaching signal myself whenever the fly tasted sugar ..."
VERDICT CONFIRMED headline=False
EVIDENCE: Female, social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv, 5 seeds: sugar GRNs, bitter GRNs and touch (all head bristles) give PAM = PPL1 = 0.0 in every seed. gain_sweep_flywire_...+eln0.25.csv: 0.0 up to gain 1.4 (touch 0.02 PPL1 at 1.4; sugar 5.7 PPL1 at gain 2.0). Male, gain_sweep_malecns_all_min1+eln0.25.csv, input 'sugar GRNs', 5 seeds: PPL1 0 / 0 / 11.71 / 53.75 / 91.67 Hz at gain 0.5 / 0.7 / 1.0 / 1.4 / 2.0, PAM 0 up to 1.0. social_probe_malecns_...: sugar GRNs -> PPL1 12.2 Hz (12.19/11.25/13.0 by seed), and contact pheromone -> PPL1 39 Hz. senses.py l.69: in MaleCNS 'grn_sugar' is the pooled labellar GRNs (no sugar/bitter split). Male bitter is not tested separately and touch gives 0.0. The per-type 'every dopamine neuron' figure (16d) is from a scratch run not in the repo; the files hold only PAM/PPL1 group means. There is also no male no-US conditioning control.
WORDING: In the female, sugar, bitter and touch drive 0.0 Hz in every dopamine neuron. In the male, whose taste neurons are not split by taste, the pooled labellar taste neurons drive the punishment (PPL1) set at 11.7 Hz at gain 1.0 (54 Hz at 1.4) and the reward (PAM) set not at all. Main text: 'In the female model, sugar and bitter never reach the teaching neurons (in the male, taste reaches only the punishment ones) ...'

### [learning] 19a - 'No descending neuron changes with training'
PAPER: No descending neuron changes with training; the reward output neurons, driven at 40\,Hz, reach none, and the 28 descending targets of the punishment output neurons fire the same (within 0.6\,Hz) whether those neurons are intact or silenced. (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: All conditioning_*_seed*.csv files: post minus pre for rows DNa L, DNa R, DNp09, MDN, DN all, feed MNs, approach, for CS+ and CS-. The 20 paper-model runs (eLN x0.25; reward 50 Hz, punish 50 Hz, no-US) have dDNa L from -7.0 to +4.0 and dDNa R from -4.0 to +4.5 Hz; max |dDNa| is 7.0 with a US and 6.5 with no US (us-wiring). Across every conditioning file the max is 7.5 Hz (reward-20hz vinegar+ seed0). The approach index changes -6.5 to +11.5 with a US and up to +8.5 without. DNp09, MDN and feed MNs change 0.0 everywhere; DN all changes at most 0.13 Hz. The DNa changes follow the odour (vinegar vs ester), not the pairing, and the no-US control reproduces them (16g, 18f). The male's DNa, DNp09, MDN and feeding change 0.0 in all 4 runs.
WORDING: No descending neuron changes with the pairing. The steering neurons shift by up to 7 Hz between the tests before and after training, but as much without a teaching signal (6.5 Hz), and the walking, backing and feeding neurons do not move.

### [learning] 19b - 'the reward output neurons, driven at 40 Hz, reach none'
PAPER: ... the reward output neurons, driven at 40\,Hz, reach none, ... (Note 7, l.149)
VERDICT CONFIRMED headline=False
EVIDENCE: experiments/expression_probe.py puts the tonic Poisson drive on tg, every neuron with >= 10 synapses from the MBON set, KCs and MBONs excluded (idx = concatenate([oi, tg])). The MBONs are never driven. logs/reproduce_expression.out: the 12 reward MBONs (MBON01/02/03/05/07, all inhibitory) have 435 targets, all central, 0 DNs. So 'reach no descending neuron directly' is true, but '40 Hz' was the drive on their targets; the MBONs themselves fired 22-27 Hz at T=40 ('set MBONs Hz'). expression_probe_flywire_shiu_min1+known+eln0.25.csv, reward set, silenced minus intact (3 seeds), no odour: DNa L +5.5 / +5.0 / +4.0 Hz at T = 10/20/40, DNa R +1.2/+3.3/+1.0. Odour on the left: DNa L -3.7 at T=5, approach -3.5 to +4.3. Odour on both sides: DNa L +1.0 to +3.0. DNp09, MDN and feed MNs 0.0 throughout. The only direct drive of the reward MBONs (30 and 60 Hz, 'reaches no DN, 0.0 % of brain') is the 16f scratch 'mbon_dn', which is not in the repo; no mbon_dn/us_probe script or output exists.
WORDING: The reward output neurons have no descending neuron among their 435 targets. When those targets are given tonic input (10-40 Hz), silencing the reward output neurons raises the left steering neuron by 4-5.5 Hz and changes nothing else.

### [learning] 19c - 'within 0.6 Hz' is true by construction
PAPER: ... and the 28 descending targets of the punishment output neurons fire the same (within 0.6\,Hz) whether those neurons are intact or silenced. (Note 7, l.149)
VERDICT PARTLY headline=False
EVIDENCE: expression_probe.py: the 28 DNs (tgd) are a subset of tg, so they receive the tonic Poisson kicks themselves. lif.py l.10/53: kick_mv = 0.275*250 = 68.75 mV against a 7-mV gap to threshold, so every kick fires the neuron unless it is refractory. Expression file, punish set, 'target DNs Hz' intact -> silenced: no odour 10.8->10.4, 14.7->14.8, 23.8->23.8, 39.3->39.8 at T=5/10/20/40; odour both 11.3->10.8, 15.1->14.8, 23.3->23.0, 38.6->38.8. Max |diff| over every odour and level is 0.54 Hz (T=40, odour L). At T >= 20 the rate is almost entirely the kicks and cannot be pushed below them, so the item holds there. It does not hold at T = 0, where the DNs are not kicked and the MBONs fire 5.3 (L) and 11.7 Hz (both): intact vs silenced is 7.0 vs 7.3 (L) and 7.0 vs 7.1 (both), a genuine null of 0.3 Hz or less. At T=5 about 6 Hz of each DN's rate comes from synapses and still moves at most 0.5 Hz. So the statement is largely, not wholly, true by construction.
WORDING: ... fire the same whether those neurons are intact or silenced: within 0.3 Hz without tonic input (7.0 vs 7.1-7.3 Hz under odour), and within 0.6 Hz with it, although there the tonic input is given to those descending neurons themselves and sets most of their rate.

### [learning] 19d - 'no working route ... notebook that nobody downstream reads' contradicts 16f
PAPER: The output neurons that hold the memory have no working route to the neurons that move the fly, so the memory is written in a notebook that nobody downstream reads. (l.99)
VERDICT CONFIRMED headline=False
EVIDENCE: RESEARCH_NOTES.md 16f (l.736-739): 'The cholinergic punishment-compartment MBONs are different: MBON14 (alpha3) alone at 30 Hz drives DNa L 14 / R 7 and a set of descending neurons (DNge053 35 Hz, DNbe007 27, DNb05 26, DNg100 24, DNg13, DNg16).' That is four DN types quantified at 24-35 Hz plus two unquantified; the source is scratch only, with no script or output in the repo. The repo's own files also show a route: the punishment set (14 of 20 excitatory) has 28 descending targets with >= 10 synapses (reproduce_expression.out), and silencing the reward set moves DNa L by 4-5.5 Hz once its targets are active (19b). What the data do support is that odours drive the output neurons only weakly (expression file at T=0: reward set 0.5 Hz with odour on one side, 6.2 Hz on both; punishment set 5.3-11.7 Hz; conditioning: ester reward-compartment MBONs 0.0 Hz before training), so depressing their input takes away little. And no DN change depends on the pairing (19a).
WORDING: The route from the output neurons to the neurons that move the fly exists: one punishment output neuron driven on its own at 30 Hz moves the steering neurons and four other descending types. But a smell drives the output neurons only weakly, and weakening that input changes nothing the legs receive. The memory is written in a notebook that is almost never opened.

### [learning] 19e - 'It walked and turned as before' rests on few ticks; world6 has no pre-training baseline
PAPER: The fly did nothing with the memory. It walked and turned as before, and in one run it walked straight back onto the flowers that tasted bitter. (l.99)
VERDICT PARTLY headline=False
EVIDENCE: Recomputed from the raw logs with learn_stats.py's definitions (phase from pl_learning; smelling = the dominant odour class > 0.5). world5 (fly1_...20260917-164631.csv): pre/post ticks smelling poppies (ester) 144/140, walk 0.53->0.48, turn -0.07->-0.12; smelling dandelions (vinegar) 14/8, walk 0.67->0.68, turn +0.01->+0.58. world6 (...170429.csv, the only odour-specific appetitive run): the pre phase has 300 ticks but 0 smelling either flower (max odour 0.28), so there is no pre-training baseline. Post is 143/5 ticks and can only be compared with training (walk 0.48/0.67, turn -0.02/+0.52), as 20f(ix) already notes. world4 (...162815.csv): dandelions pre/post 365/333 ticks, walk 0.67->0.65, turn +0.61->+0.59, but its memory was not odour-specific (reward-comp 0.14 vs 0.21). So the item is right that world6 has no baseline and that world5's dandelion comparison rests on 14/8 ticks. It overstates by saying the whole claim rests on those: world5's poppy comparison (144/140) and world4's dandelion comparison (365/333) are adequate and show no change.
WORDING: The fly did nothing with the memory. Where a before-and-after comparison exists, it walked and turned as before; in the run with the clearest memory it never reached either flower before training, so its behaviour can only be compared with how it behaved during training. In one run it walked straight back onto the flowers that tasted bitter.

### [arena] 20a. The 86.2-s bout and the launch stagger (l.101, Fig 3b caption, Table 1)
PAPER: l.101: "the females walked, bumped into each other by chance, and then stayed together, because touch switched off their steering while their ovipositors kept going. A real female walks away. These two stood pressed together for up to eighty-six seconds". Fig 3 caption: "in b they meet and stay together for 86 seconds". Table 1, faint-smell two females: Longest meeting 86.2.
VERDICT CONFIRMED headline=False
EVIDENCE: Scratch scripts not kept., bouts.py, firstbout.py. They pair the fly1 and fly2 logs per trial label from release/pre_rerun_20260926/results/encounter_trials.csv (fly, stamp) and use logs/fly{1,2}_off-*_<stamp>.csv. Contact = obs_taste_fly_female + obs_taste_fly_male > 0, as in encounter_stats.py.

The launch stagger:
- experiments/run_pair.sh starts fly1's bot (with --build-arena) and then sleeps 6 s before starting fly2's bot.
- In the logs, fly1 logs 13-34 ticks, about 3.1-3.6 s of wall time, before fly2's first row (t_wall).

The 86.2-s bout is faint-smell off_ff_t3 (stamp 20260917-141245). figures_print.py pick() puts the longest bout in panel b, so this is Fig 3b.
- fly1 started at x=2.5, z=0.5, facing west towards fly2's start.
- In its 28 ticks before fly2 existed, fly1 walked 4.53 blocks, to x=-2.03, which is past fly2's spawn point (-1.5, 0.5).
- fly2's row 0 has no partner. Its row 1 (its second tick, brain 0.10 s) has near_dist 0.61 and contact=1.
- That bout lasted 86.20 s (fly2 log; 86.25 s in fly1's log). It was the only bout of the trial: 1724 of 1740 ticks in contact, 99 %.
- The flies did not meet by chance. The second fly was put in beside the first.

Other trials where the partner appeared within 3 blocks and contact came within 40 ticks:
- faint ff t1: fly1 walked 2.89 blocks; 0.99 blocks apart when fly2 appeared; contact at fly2's row 0; first bout 6.5 s.
- rep-noise0.2 ff t1: 2.21 blocks; 1.89 apart; contact at row 4.
- rep-noise0.2 ff t3: 1.45 blocks; 2.57 apart; contact at row 7.
- Also affected, not named in the item: published-lobe mf t1 and t3. The male walked 2.1 blocks; 1.95 and 1.76 apart; contact at row 4. So 2 of that row's 4/5 trials with contact are launch contacts.

In faint t1 and rep-hum t1/t3 only the first contact is affected. Their longest bouts began later (at 77.9, 34.8 and 139.8 s), so they do not set the Longest column. They do inflate the trials-with-contact and contact % columns.

Longest bouts without the flagged trials:
- faint ff: 25.7 s (t2, fly1 log). The item's "about 26 s" holds for this series.
- Across all series, the longest unaffected bout is 31.15 s: rep-noise0.2 ff t2 in fly1's log (26.85 s in fly2's log). Table 1 takes the maximum over both fly-logs, and its 31.1 is unaffected.

Contact without the flagged trials:
- faint ff: 2/3 trials, mean 20 % (paper: 4/5, 39.5 %).
- rep hum ff: 3/3, 58 % (paper: 59.1 %).

The freeze itself survives. Genuine meetings still give bouts of about 24-31 s.
WORDING: l.101: "...the females walked, and when they touched they stayed together, because touch switched off their steering while their ovipositors kept going. A real female walks away. Pairs that met stood pressed together for up to about half a minute (26 s in this box, 31 s in the replication), extending their ovipositors at each other."

Note 8: "In three trials with two females (and two with a male) the first fly, launched about 3 s before the second, had walked onto the second's starting point, so those pairs began in contact. One of them stayed in contact for the whole 86-s trial. I leave these trials out of the meeting statistics."

Fig 3b: show faint-smell t2 (25.7 s), or change the caption to "in b the second fly appeared beside the first (a launch artefact) and they stayed together for the whole 86-s trial".

Table 1, faint two females: 2/3 trials with contact, 20 % contact, longest meeting 25.7 s, with a footnote on the excluded launch-contact trials. Apply the same footnote to rep-hum ff t1/t3 and published mf t1/t3.

### [arena] 20b. Start distance (4 vs 5.7 blocks) and which starts face each other (Note 8)
PAPER: Note 8: "13 × 13 blocks, white walls, no food; the flies start 4 blocks apart; 5 trials per condition".
VERDICT CONFIRMED headline=False
EVIDENCE: experiments/trials.sh POS (x,z; Minecraft /tp yaw degrees, where 0 = +z, 90 = -x, -90 = +x, 180 = -z; bot.js l.117):
- t1: (-2,0) yaw -90 vs (2,0) yaw 90. Face to face, 4 blocks.
- t2: (0,-2) yaw 180 vs (0,2) yaw 0. Facing away, 4 blocks.
- t3: (2,0) yaw 90 vs (-2,0) yaw -90. Face to face, 4 blocks.
- t4: (0,2) yaw 0 vs (0,-2) yaw 180. Facing away, 4 blocks.
- t5: (-2,-2) yaw -135 vs (2,2) yaw 45. 5.66 blocks; each heading is perpendicular to the line between them (dot product 0).

The first log rows of all 70 trials confirm this. For example, x,z,yaw = (-1.5, 0.5, 4.712) vs (2.5, 0.5, 1.571) in t1; the mineflayer yaw 4.712 rad means facing +x. The distance is 5.66 in every t5.

Because of the launch stagger (20a), the real distance when the partner appeared varied widely:
- two-female walking series: 0.6-10 blocks;
- published-lobe series: 1.8-10 blocks.

Contacts in the clean box:
- male-female, clean: t1 and t3 only (fly2 first contact at rows 26 and 23);
- male-female, rep-clean: t1 and t3 only (rows 8 and 7);
- faint-smell male-female: its one contact is also t3.

In these face-to-face contacts the female moved 88-97 % of her path straight towards a male who did not move (scratch approach.py: her_frac 0.88-0.97, male net movement 0). So every clean male-female contact came from a face-to-face start.
WORDING: Note 8: "...the flies start 4 blocks apart in five fixed positions, used in the same order in every series: facing each other (trials 1 and 3), facing away (2 and 4), or 5.7 blocks apart along a diagonal, facing opposite ways at right angles to it (5). The first fly is launched about 3 s before the second."

Near l.101 or l.110: "In the clean box every male-female contact came from the two face-to-face starts, where the female walked straight into the motionless male within a second or so."

### [arena] 20c. Seeds and starts shared across brains and series (effective n)
PAPER: Note 8: "5 trials per condition". Table 1 caption: "five trials per row, ± the standard deviation across fly-logs".
VERDICT CONFIRMED headline=False
EVIDENCE: Seeds:
- trials.sh calls `run_pair.sh "$ARM" --seed "$i"` for trial i.
- run_pair.sh passes "$@" to both run_brain.py calls, so both brains of a pair get seed i.
- run_replication.sh reaches the same trials.sh through encounter_trials.sh. trials.sh is identical in release/flycraft_20260919.
- RESEARCH_NOTES 19b says the clean series used the "same seeds and starts" as the 17 Sep series.
- I could not see the 14 Sep seeds in the logs; the logs do not record seeds.

Starts: the start positions and yaws in the first log rows are identical by trial number in all 8 series (start.py).

Two-female contact %: the ± is over 10 fly-logs that are near-duplicates within each pair (largest within-pair difference 1.25 points). For example:
- faint: 39.5 ± 34.4 over logs, 39.5 ± 36.4 over the 5 pairs;
- rep hum: 59.1 ± 15.8 vs ± 16.8;
- hum: 11.2 ± 14.9 vs ± 15.8.

So the effective n is 5 pairs, and the replication repeats the same 5 seed/start configurations. I did not test whether the same seeds give correlated neural noise.
WORDING: Note 8 and Table 1 caption: "Each series used seeds 1-5 (the same seed for both brains of a pair) and the same five starts, so every row is five configurations, and the replication repeats them with new runs, not new seeds. ± is the standard deviation across the five pairs (the two fly-logs of a female pair share their contacts)."

### [arena] 21. "nobody sang or fought" (l.101)
PAPER: l.101: "On the hum, females met and stayed together, males met females and backed out, and nobody sang or fought."
VERDICT PARTLY headline=False
EVIDENCE: Sources: encounter_trials.csv (sing_events_per_min, attack_events_per_min, sing_/aggression_ columns) and per-tick logs (ctl_sing, ctl_attack, hz_song_mn, hz_sing = pIP10, hz_aggression = pC1d/e + aIPg, obs_sound). Scratch scripts: acts.py, acts2.py, singc.py. How the acts work:
- motor.py fires the sing act from the song-MN rate whenever it is above 0, and falls back to pIP10 otherwise.
- bot.js l.75 turns each sing act into chat '♪', which the partner hears as sound (observe.js l.104).
- Each attack act makes the body hit the nearest fly within 3.5 blocks (bot.js l.73).

Singing holds as the item says:
- The male logs 20.3 / 22.1 sing acts a minute on the plain hum (orig / rep) and 25.2 / 25.5 in the virgin series. Far from her the rate is 19-23 a minute, which is the hum's song-MN floor (3.6-3.9 Hz far; offline floor 2.0-2.7 Hz).
- In contact, the pooled rate rises to 58-127 a minute: 5, 7, 21 and 31 acts, with song MNs at 15-16 Hz. This is the ppk to song/wing-MN reflex of Note 4.
- The female heard ♪ on 4-5 % of her ticks.
- pIP10 stays at its injected floor: 0.19-0.24 Hz far and 0.07-0.34 Hz on contact.
- So the body did 'sing' above the floor on contact, but the song command did not.

Fighting is only partly as the item says:
- The injected 0.2 Hz aggression floor predicts 0.2 × 0.2 × 60 = 2.4 lunges a minute.
- Plain hum lunges: ff 2.0 / 2.5 a minute, mf 2.9 / 3.0 a minute, pooled far rate 2.2-2.3. Aggression neurons are 0.20-0.24 Hz on contact. So the plain hum is at the floor, and "nobody fought" holds there as "no more than the floor".
- The item's upper values of 3.7-5.0 a minute are the virgin series. There, pC1d/e + aIPg reach 1.02 / 1.09 Hz on contact (5 × the floor) and 0.27-0.28 Hz far. Pooled contact lunge rates are 27 and 16 a minute (4 and 6 acts), against 3.1 and 4.5 a minute far.
- The paper never reports that the virgin's aggression neurons rise above the floor.

The item's rewording is right for the plain hum. "No aggression-neuron activity above the floor" would be false if extended to the virgin.
WORDING: l.101: "On the hum, females met and stayed together, males met females and backed out, and neither the male's song command nor the female's aggression neurons rose above the hum's own floor. The male's wing motor neurons did buzz when she touched his legs, the leg-taste reflex of Note 4, which his body played as song."

Note 8: add "the male's body makes 20-25 'song' acts a minute on the hum's floor and 60-130 a minute in contact (song MNs 15 Hz, pIP10 0.2 Hz)."

Virgin passage or Note 6: "on contact the virgin's aggression neurons reached about 1 Hz (floor 0.2), and she lunged more often in contact."

### [arena] 22a. Reproduction of the lean and the "24 of 33" wording (l.110, Note 9)
PAPER: Note 9: "the female leans towards the male in 24 of the 33 male--female recordings that turn at all and away in 9 (two-sided sign test, p=0.014; pooled index +0.015, 6 % of her turning), and female pairs lean either way (13 and 9, p=0.52)". l.110: "in 24 of 33 recordings".
VERDICT CONFIRMED headline=False
EVIDENCE: I copied replication_stats.py's pooled block exactly into (scratch, not kept) It uses the frozen encounter_trials.csv, variant 'specific', the 7 series faint-smell, clean, noise0.2, noise0.2-virgin and the three rep- series, and the flywire logs. It keeps pre-contact ticks with near_dist < 6 and near_az not NaN, and a log is kept if sum|ctl_turn| > 0. Index = mean(ctl_turn × sign(near_az)). The sign convention checks out: ctl_turn +1 is a left turn (motor.py), and az > 0 means the partner is on the left (observe.js, mineflayer yaw).

Results:
- Male-female: 35 of 35 female logs pass the "turn at all" filter. 24 have a positive index, 9 negative, and 2 exactly 0 (clean t3 and rep-clean t3, where the tick products cancel). Two-sided sign test p = 0.0135.
- Pooled index +0.0152, mean |turn| 0.250, ratio 0.061.
- Female pairs: 22 logs turn, 13/9, p = 0.523.

So every number reproduces, but 35 logs turn at all and 33 have a nonzero index.
WORDING: Note 9: "...leans towards the male in 24 and away in 9 of the 35 male-female recordings that turn at all (two have an index of exactly zero)...". Then the bias-corrected result replaces this (22b).

### [arena] 22b. The lean after removing her own turning bias; the "one trace" and "size of the pull" sentences (l.110, Note 9)
PAPER: l.110: "The one trace of it is in pairs of a male and a female, where the female's turning leaned towards the male a little more often than away from him, in 24 of 33 recordings, by about a twentieth of her turning, which is about the size of the pull his pheromone has on her steering neurons on its own."
VERDICT CONFIRMED headline=True
EVIDENCE: Scratch script (scratch, not kept) uses the same 35 logs and the same pre-contact ticks as 22a. The corrected index is mean((ctl_turn − b) × sign(near_az)).

By choice of bias b:
- b = mean ctl_turn over the log's non-contact ticks with near_dist ≥ 6 (far-field bias): 15 towards / 20 away, p = 0.50, mean +0.009.
- b = all ticks, or all non-contact ticks: 17/18, p = 1.0.
- b = pre-contact ticks ≥ 6 only (28 logs have them): 13/15, p = 0.85.
- Within-log side contrast, 0.5 × (mean turn when he is on the left − mean turn when he is on the right), in logs with ≥ 10 ticks per side: 6/6, n = 12.

Why the raw lean appears:
- 30 of 35 females turn right on average before contact.
- b_far < 0 in 27 of 35.
- The male is mostly on her right (mean sign(az) < 0) in 27 of 35.
- By series, the raw 24/9 comes from faint (5/0) and the hum series (5/0, 3/2, 4/1, 4/1), not the clean boxes (1/3, 2/2).
- By start configuration t1-t5, all 5 raw means are positive (cluster sign test p = 0.0625). The corrected means are −0.001, +0.010, +0.024, −0.002 and +0.015.
- Holm over the male-female and female-pair tests gives 0.027 for the raw test.

The "size of the pull" comparison can in fact be converted. The decoder's turn is tanh(ΔHz/40) (motor.py k_turn_hz = 40), so an index of 0.015 is about 0.6 Hz of DNa L−R, the bottom of the 0.6-2.3 Hz range. The item is overstated on this point, but the text gives no conversion, compares a unilateral bench stimulus with a bilateral arena situation, and the lean itself goes away. So the sentence should go.
WORDING: l.110: replace the sentence with "In pairs of a male and a female, the female's raw turning leaned towards the male in 24 of 33 recordings, but that is her own steady right turn meeting a male who happened to be on her right. With her turning far from him subtracted, 15 recordings lean towards him and 20 away."

Note 9: "...24 towards and 9 away (35 recordings turn at all). After subtracting each female's mean turn when he is 6 or more blocks away, 15 towards and 20 away (p = 0.50; pooled +0.009). Female pairs 13 and 9 (p = 0.52)."

Drop "pooled index +0.015, 6 % of her turning" or report it with the corrected value.

### [arena] 22c. cVA steering range and sign at 100 Hz (Note 9)
PAPER: Note 9: "cVA on one antenna turns the female towards it by 0.6--2.3 Hz, while food odours turn her away."
VERDICT CONFIRMED headline=False
EVIDENCE: Source: release/pre_rerun_20260926/results/odor_dose_flywire_shiu_min1+known+eln0.25.csv, with steer() copied from paper_numbers.py: the mean over the L and R presentations of 'approach (ipsi-contra)', 3 seeds (0-2). Scratch script: steer.py.

cVA by stimulus rate:
- 25 Hz: 0.00
- 50 Hz: +1.67 (per seed 4, 0, 1; t = 1.39, p = 0.30)
- 75 Hz: +0.58 (t = 0.73, p = 0.54)
- 100 Hz: −0.17 (per seed +2.75, −2.75, −0.5; p = 0.93)
- 150 Hz: +2.33 (t = 1.94, p = 0.19)

So "0.6-2.3" leaves out 0 at 25 Hz and −0.2 at 100 Hz, which is the paper's own bench rate. No rate is significant at n = 3.

CO2 moves her by similar amounts: +0.92, +1.08, −0.42, −2.83 Hz.

Food does turn her away: −4.8, −2.7, −6.6, −3.7, −9.2 Hz (p ≤ 0.026 at 75-150 Hz).
WORDING: Note 9: "cVA on one antenna moves her steering neurons by −0.2 to +2.3 Hz towards it depending on its strength (0 at 25 Hz, −0.2 at 100 Hz; 3 seeds, none significant, and CO2 moves them as much), while food odours turn her away by 2.7-9.2 Hz."

### [arena] 22d. "she never walked towards him" (l.110, the virgin)
PAPER: l.110: "In the box her acceptance neuron fired whether the male was near or far, and she signalled acceptance nearly a hundred times a minute, yet she never walked towards him."
VERDICT PARTLY headline=False
EVIDENCE: "Never" is too absolute:
- Virgin contact happened in 5/5 trials in both series.
- In the pre-contact window under 6 blocks, her own displacement had a net component towards him in 7 of 10 virgin logs: +2.1 blocks on average in the original series and +1.5 in the replication, 26-31 % of her path (scratch approach.py, male positions matched by t_wall).
- This is partly forced, because the window ends at contact. The plain hum series show the same (0.23-0.24).

The item's evidence reproduces, but it does not show steering towards him:
- Replication virgin index: +0.040 (Table 1). My own run of paper_numbers' section Q code on the original virgin series gives −0.005.
- Original virgin series, closest bin (1.3-2 blocks, 37 ticks): +0.16, per-log sign-flip p = 0.12.
- RESEARCH_NOTES 21b says her turn in that bin is negative in all 5 logs whichever side he was on, so this is bias.
- With her far-field turning bias subtracted (lean2.py), the virgin logs give 1/4 towards/away in the original series and 2/3 in the replication (3/7 in all), mean −0.003.

So "did not reliably" understates how null the steering is, while "never walked towards him" overstates it.
WORDING: l.110: "...yet she did not steer towards him. Her turning was no more towards him than her own turning bias predicts, and she reached him only by walking into him."

Note 9: "virgin: index −0.005 and +0.040 in the two series; with her far-field turning subtracted, 3 of 10 recordings lean towards him."

>>> REFUTE [arena] 22b. The lean after removing her own turning bias; the "one trace" and "size of the pull" sentences (l.110, Note 9): upheld=True
EVIDENCE: VERDICT: I could not refute this. The verifier is CONFIRMED and headline=true: the "faint lean" part of the "nobody approaches" conclusion goes. Two of the verifier's corrected phrases need fixing (see the end).

Paper l.110, as written: "The one trace of it is in pairs of a male and a female, where the female's turning leaned towards the male a little more often than away from him, in 24 of 33 recordings, by about a twentieth of her turning, which is about the size of the pull his pheromone has on her steering neurons on its own."

How I checked it: my own script is (scratch, not kept), with lean_more.py and bins.py beside it; it is not the verifier's lean2.py. Input was release/pre_rerun_20260926/results/encounter_trials.csv: variant=specific, dataset=flywire, all 7 specific-lobe series (faint-smell, clean, noise0.2, noise0.2-virgin, rep-clean, rep-noise0.2, rep-noise0.2-virgin), matched to logs/{fly}_off-*_{stamp}.csv. The last log was modified on 26 Sep at 19:25, so no log changed after the freeze.
- Ticks: before first contact (obs_taste_fly_female+male > 0), near_dist < 6, near_az present. These are the ticks of replication_stats.py.
- Index: ctl_turn x sign(near_az).
- Sign convention: in bot.js a positive turn increases yaw, and in observe.js az = atan2(-dx,-dz) - yaw. A positive product therefore means turning towards the partner, so the convention is right.

1. The paper's numbers reproduce exactly. There are 35 male-female logs; all 35 turn at all. 24 lean towards, 9 away and 2 are exactly 0. Two-sided sign test p = 0.014; Holm over male-female and female pairs gives 0.027. Pooled over ticks (3,977), the index is +0.0152 against a mean |turn| of 0.250 (6.1 %). "24 of 33" is therefore 33 nonzero logs out of 35 that turn, not "33 that turn at all".

2. The lean goes away when her own turning bias is removed. Corrected index = mean((turn - b) x side), 35 logs:

| b (her bias) | towards / away | p | mean of per-log values | pooled over ticks |
|---|---|---|---|---|
| mean turn, non-contact ticks >= 6 blocks | 15 / 20 | 0.50 | +0.009 | -0.0016 |
| pre-contact ticks >= 6 only (28 logs) | 13 / 15 | 0.85 | | |
| all ticks | 17 / 18 | 1.0 | | |
| non-contact ticks | 17 / 18 | 1.0 | | |

3. Within one recording, her turning does not change with his side. Comparing her turn with him on the left against him on the right, with a constant bias cancelling out:
   - at least 10 ticks per side: 6 / 6 (12 logs);
   - at least 5 per side: 7 / 6;
   - at least 1 per side: 10 / 11 (21 logs), mean -0.009.
   Splitting the raw index into within-log covariance plus mean turn x mean side: the covariance part is 14 / 11 with 10 zeros, mean -0.001. The product part is 24 / 11, mean +0.0265, which is the whole raw mean (+0.0255).

4. Why the raw lean appears:
   - She turns right before contact in 30 of 35 logs. Her far-field bias is to the right in 27 of 35.
   - The male is mostly on her right in 27 of 35 logs, both near and far (>= 6 blocks).
   - At >= 6 blocks the raw product "leans towards him" 28 / 7 (p = 0.001). Yet the far-field left-minus-right comparison within logs is 17 / 16 (p = 1.0, mean -0.002). So the bias is not caused by his side, and subtracting b does not over-correct.
   - Female pairs show the same right bias (b_far < 0 in 19 of 22) with no cVA source.
   - Across logs: in the 8 logs with him mostly on her left, she still turns right in 7. Relative to her far bias, logs with him on her left and on her right do not differ (-0.016 vs -0.020, Mann-Whitney p = 0.74).

5. The existing S4 output agrees. experiments/results_edge/arena-log-audit/arena_audit.md (written 27 Sep, 01:11) gives the same tables. Its bias-preserving null, which shifts near_az within the pre-contact segment, gives P(net) = 0.153 for the raw index, with a null mean of +10.2 against the observed +15. By its own S4 rule the result is "CHANGE". Its whole-log shift gives P = 0.046 for the raw index, but that null does not keep her pre-contact side distribution; the far-corrected version is P = 0.85.

6. Closer ranges do not rescue it. At 1.3-2 blocks the far-corrected split is 15 / 8 (p = 0.21), and female pairs show the same, 14 / 7 (p = 0.19). So nothing specific to the male and nothing significant.

7. The "size of the pull" comparison. With the hz_turn_L and hz_turn_R columns in the logs, the raw lean is +0.71 Hz of DNa L-R (40*atanh(0.0152) = 0.61 Hz). That is at the bottom of the bench cVA figure: in odor_dose_flywire_shiu_min1+known+eln0.25.csv, the one-antenna (ipsi-contra) difference averaged over sides is +1.67, +0.58, -0.17 and +2.33 Hz at 50, 75, 100 and 150 Hz, n = 3 each. So the paper's comparison is not wrong in magnitude, and the verifier is right that item 22 overstates the unit complaint. But the far-corrected lean is -0.07 Hz pooled over ticks, so the comparison has nothing left to compare and should go.

8. Where the verifier's wording goes too far or mislabels:
   - (a) "pooled +0.009" is the mean of per-log values. The paper's "pooled index" is pooled over ticks, and on that definition the corrected value is -0.002.
   - (b) "steady right turn": near him she turns further right than her far bias in 25 of 35 logs (Wilcoxon p = 0.046; -0.044 vs -0.026). Female pairs do the same (14 / 22, p = 0.06), and it does not depend on his side. "Her own right turn, whichever side he is on" is accurate; "steady" is not.
   - (c) "happened to be on her right" suggests chance. The data only show he was mostly on her right (27 of 35), probably because of the geometry of a right-circling fly.
   - (d) "24 of 33" should be 24 of 35, with 9 away and 2 neither.
WORDING: l.110, replace the sentence "The one trace of it ... on its own." with:
"Pairs of a male and a female looked at first as if they had a trace of it. The female's turning leaned towards the male in 24 of 35 recordings and away in 9. But she turned right whichever side he was on, and he was mostly on her right. Within a recording her turning did not change with his side. With her own turning far from him subtracted, 15 recordings lean towards him and 20 away."

Note 9, replace from "Pooled over every series of my model, the female leans towards the male..." up to "(13 and 9, $p=0.52$)." with:
"Pooled over every series of my model, the raw index is positive in 24 of the 35 male--female recordings, negative in 9 and exactly zero in 2 (two-sided sign test $p=0.014$, Holm over the two pairings $0.027$; pooled index $+0.015$, 6\,\% of her turning). She turns right in 30 of the 35 and the male is mostly on her right in 27, which makes the product positive without any steering towards him. After subtracting each female's mean turn when he is 6 or more blocks away, 15 lean towards him and 20 away ($p=0.50$; pooled index $-0.002$, i.e. $-0.07$\,Hz of DNa left minus right). In the 12 recordings with at least ten moments on each side, her turn with him on the left minus on the right splits 6 and 6. Female pairs lean 13 and 9 raw ($p=0.52$) and 11 and 11 corrected."

Keep the next sentence, "cVA on one antenna turns the female towards it by 0.6--2.3\,Hz...", only under item 22's separate fix (the -0.2 Hz at 100 Hz, n = 3). Drop "which is about the size of the pull his pheromone has on her steering neurons on its own". Do not write "pooled +0.009": that is a mean of per-log values, not the pooled index.

### [meta] 23a: Note 10, "One number changed"
PAPER: Note 10: "One number changed (bitter suppression, now 3.3\,Hz; the earlier 1.7 came from a two-seed file)." The paper still prints the old values elsewhere. Note 7: "the paired odour keeps 0.10--0.11 of its drive and the other 0.59--0.66: learning index $0.54 \pm 0.02$ ($n=6$), 0.04 without a teaching signal". Note 5: "the song command pIP10 answers cVA only, at 2--3.5\,Hz".
VERDICT CONFIRMED headline=False
EVIDENCE: I recomputed these from the conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_{vinegar-vs-ester,ester-vs-vinegar}_seed{0,1,2}.csv files. For each run: retained drive = post/pre of row 'drive reward-comp'; LI = CS- retained minus CS+ retained.

Before the 25 Sep re-run (release/pre_rerun_20260925/results):
- CS- 0.593, 0.632, 0.641, 0.657, 0.661, 0.651
- LI 0.5395 +/- 0.0205
- no-US control (us-wiring, n=4) 0.040

After the re-run, which is what the paper rests on (release/pre_rerun_20260926/results; the live experiments/results is identical):
- CS- 0.593, 0.634, 0.641, 0.697, 0.661, 0.656, so the range is 0.59-0.70
- LI 0.5477 +/- 0.0301, i.e. 0.55 +/- 0.03
- no-US 0.033, i.e. 0.03
- The 0.04 jump is ester-vs-vinegar seed0 (post_CS- 58380/88860 = 0.657 became 0.697). That is ten times the "at most 0.004 in the learned weights" Note 10 gives.

Male pIP10 (social_probe_malecns_all_min1+eln0.25_noise0.csv, mean over 3 seeds):
- before: cVA 2.33, cVA+food 3.0, cVA+song 3.50, cVA+sugar 3.0
- after: cVA+song 3.67, so the range is 2.3-3.7

Diffing the computed values in the two paper_numbers.md copies (pre_rerun_20260925 against pre_rerun_20260926) shows the same changes: 0.54+/-0.02 -> 0.55+/-0.03; 0.59-0.66 -> 0.59-0.70; no US 0.04 -> 0.03; male P1/pIP10 max 0.5/3.5 -> 0.5/3.7; and bitter 1.7 -> 3.3. Values that changed but do not appear in the short paper: MN9 ratio 75 -> 71 %, P1+odour -> MN9, dose-row cells. The script marked every changed value 'ok', so the tex was never updated.
WORDING: Note 10: "Five numbers in this text changed. Bitter suppression is now 3.3 Hz (the earlier 1.7 came from a two-seed file). The other odour keeps 0.59-0.70 of its drive (was 0.59-0.66). The learning index is 0.55 +/- 0.03 (was 0.54 +/- 0.02), and 0.03 without a teaching signal (was 0.04). The male's pIP10 answers cVA at 2.3-3.7 Hz (was 2-3.5). The retained drives moved by up to 0.04." Update Note 7 and Note 5 to match: "the other 0.59--0.70: learning index 0.55 +/- 0.03 (n = 6), 0.03 without a teaching signal" and "pIP10 answers cVA only, at 2.3--3.7 Hz". Change "by at most 0.004 in the learned weights" to "by at most 0.004 in the learned weights and 0.04 in an odour's retained drive".

### [meta] 23b: "A script checks 155 numbers" and "recomputes every number" (paper_numbers.py)
PAPER: Note 10: "A script checks 155 numbers of this paper against the result files, and none differ." Author line: "and a script recomputes every number in it from the result files."
VERDICT CONFIRMED headline=False
EVIDENCE: 1. The expectations are hard-coded. experiments/paper_numbers.py takes only --out (l.16) and never opens flycraft.tex. Each check() compares against a string literal: the docstring says "Every number in PAPER.md", and the output header says "the value typed in PAPER.md" (draft 3). Several literals do not match the short paper's text, and all still pass:
   - touch->DNp13: literal "28 / 36 / 42"; tex says 28 / 35 / 42
   - pIP10: literals "0 / 3 / 8" and "0.5 / 3.5"; tex says 2-3.5
   - punishment: literal "0.21 +/- 0.15"; tex says 0.14
   - PNs: literal "80 %"; tex says 81 %
   Many of the 155 cells (e.g. food->PPL1 by lobe variant) are not in the short paper at all.

2. The tolerance is too loose. same() accepts |x-y| <= max(0.55, 0.03|y|). I copied same() into (scratch, not kept) and all of these return True:
   - LI '0.00 +/- 0.03' against '0.54 +/- 0.02'
   - '0.05-0.70' against '0.59-0.66'
   - p '0.55' against '0.014'
   - freeze index '0.93' against '0.69'
   - overlap '0.59 / 0.52' against '0.63 / 0.08'
   - '4.0' against '3.5' Hz
   The item's "passes any number below 1" is slightly too strong: 0.0 against 0.9 fails. But any value within 0.55 passes, which covers almost the whole range of an index, fraction or p-value.

3. Many numbers are never checked (grep of paper_numbers.py, and section J of the frozen paper_numbers.md):
   - Note 1: none of 15,090,883 / 54.5 M / 164,439 / 25.6 M / 0.542 / 23,689 vs 23,512 / r 0.9999.
   - Note 3: the counts 685, 5,177, 11,010 and 150, and the "18 %", are unchecked. Its percentages (80 %, 65 %, 0.99, 0-5 %, 0.63/0.08) are checked, but at this tolerance.
   - Note 5: the steering ranges "0.7--9 Hz" and "16--29 Hz" are only printed with emit(), never check()ed. The computed values are -9.2 to -0.7 for food-type odours; the bias is 15.8-29.2 for food-type odours but 0.0-18.5 for CO2/cVA/aversive. The pIP10 range is checked only as its max, and 3.7 passes as 3.5.
   - Note 9: the cVA "0.6--2.3 Hz" is not checked. The sign test (24/9 of 35, p=0.014, +0.015, 13/9 p=0.52) is computed by replication_stats.py (results/replication_20260925.md l.118-119) but compared with nothing.
   - Note 10: the file counts "123" / "54" come only from compare_results.py and are not checked.
   - The "155" and "0 differ" are paper_numbers.md l.467 of the frozen copy.
WORDING: Either fix the script: parse flycraft.tex (or take the expected values from it), use a tolerance of half a unit in the last printed digit, and add the Note 1/3 counts, the Note 5 ranges, the Note 9 cVA range and sign test, and the file counts. Or reword. Note 10: "A script (paper_numbers.py) recomputes 155 values from the result files and compares them, within 0.55 or 3 %, with values typed from an earlier draft. It does not read this text. It does not cover the model and smell-centre counts (Notes 1 and 3), the steering ranges of Note 5, or the file counts. The Note 9 sign test is recomputed by replication_stats.py but not compared." Author line: "... and scripts recompute most of its numbers from the result files."

### [meta] 23c: Replication comparability (median wall gap 0.8 s, bodies moving 2-5x farther per brain-second)
PAPER: Note 10: "The replication ran 25 trials under their own labels: the clean box at 300\,s, and the hum and virgin boxes at 600\,s, because other work on the same laptop had slowed the brains (the clean male--female trials got only 14 $\pm$ 6\,s of brain time each, against 90 originally)." Main text l.112: "For this version I ran three of the boxes again, 25 new trials under labels of their own ... The females in the clean box stood still, the females on the hum met and stayed together, the male backed out of every meeting".
VERDICT PARTLY headline=False
EVIDENCE: Source: logs/fly*_off-*.csv, paired and labelled as in encounter_stats.py. Wall gap = diff(t_wall) per tick. Path = sum of per-tick xz steps. Script not kept.

Where the item holds, the clean male-female replication (rep-clean mf):
- Female: pooled median gap 0.792 s (per log 0.31-1.31) against 0.159 s originally. Path per brain-second 1.77 blocks (per log 0.89-2.67) against 0.47 (0.42-0.58), which is 3.8x. Per unit of walk command, 2.71 against 0.81 blocks per brain-s walking (3.3x).
- Male: median gap 1.02 s against 0.17 s; path per brain-second 1.07 against 0.67 (1.6x; 2.1x per walk unit).
- bot.js RT_SCALE (l.30-33, 68-69, 88) is meant to slow the body to brain time. At these gaps it did not.

Where it does not hold, the other 15 replication trials:
- Hum: median gaps 0.19-0.20 s against 0.165-0.176 s originally.
- Virgin: 0.21-0.23 s against 0.19-0.21 s.
- Path per brain-second against the originals: hum ff 0.61 vs 0.74 (0.8x), hum mf female 1.02 vs 0.73 (1.4x), hum male 1.74 vs 1.59 (1.1x), virgin female 1.44 vs 1.11 (1.3x), virgin male 1.80 vs 1.91 (0.9x).
- Only single trials were loaded: the last hum mf trial (0.75/0.81 s) and the first virgin trial (0.55/0.64 s).
- Pooled over all replication ticks the median gap is 0.194 s, against 0.155 s for the original changed-lobe series.

rep-clean ff: nobody moved (path 0), so the gap does not matter there.

Note 10 already discloses the brain-time shortfall of the clean mf trials, but not that their bodies moved about 3-4x farther per brain-second.
WORDING: Add to Note 10: "In the clean male-female replication the laptop was so loaded (a median 0.8 s of wall time per 50-ms brain step, against 0.16 s originally) that the body's slow-down to brain time failed. The female covered about four times as much ground per second of brain time (1.8 against 0.5 blocks), so that series is not comparable with the original. The hum and virgin replications ran at 0.19-0.23 s per step (originals 0.17-0.21 s) and moved 0.8-1.4 times as far per brain-second." Either drop rep-clean mf from Fig. replication and Table 1 or mark it.

### [meta] 24a: Body reflexes (step-up and float) in bot/bot.js not listed as mine
PAPER: Note 11: "Mine: the simulation constants (Shiu et al.'s), the male's scale, the smell-centre change, which blocks smell of what, how far a smell carries (16 blocks), the stimulus rates (100\,Hz on the bench, at most 150\,Hz in the body, 200\,Hz for touch), how firing becomes movement, the learning constants and teaching signal, and the hum." Also l.59: "Nothing in the body says ``if touched, back away''."
VERDICT CONFIRMED headline=False
EVIDENCE: The reflexes exist and are on in every arena trial:
- bot/bot.js l.11-13: "Body-level reflexes ... on by default, --no-reflexes turns them off: step up onto a one-block obstacle when walking into it; float when in water."
- l.29: REFLEXES = !argv['no-reflexes'].
- l.98-101: jump when isInWater; jump when (goWalk||goBack) && isCollidedHorizontally && onGround.
- No arena script passes --no-reflexes (grep of experiments/*.sh and run.sh; run_pair.sh l.20/22 launch bot.js without it).

The step-up reflex fired in the arena. Taking ticks with y above the floor (64) and no brain jump command in the previous 20 ticks:
- clean mf male 355, of which 223 came within 10 ticks of a wall collision
- hum mf male 186
- virgin male 196
- rep-hum male 295
- rep-virgin male 131
- almost none in females

The float reflex never engaged: obs_mech_in_water is 0 in all 307,864 logged ticks.

l.59 stays true, because the reflexes never start, stop or turn walking.
WORDING: Note 11, add to "Mine": "two body reflexes that stand in for the missing nerve cord: stepping up onto a one-block obstacle when walking into it (it fired at the walls) and floating in water (never used). Neither starts, stops or turns walking."

### [meta] 24b: Sensory kick fixed at 68.75 mV at every gain and in the male
PAPER: Note 1: "sensory drive by Poisson kicks of 68.75\,mV". Note 2: "Every synapse at 0.7, 1.0 and 1.4 times its published strength". Note 11: "Mine: the simulation constants (Shiu et al.'s), the male's scale, ..."
VERDICT CONFIRMED headline=False
EVIDENCE: The kick is fixed:
- brain/flybrain/lif.py l.10 documents Shiu's rule as "PoissonInput on v at r_poi with weight w_syn * f_poi (f_poi = 250, i.e. a 68.75 mV kick)".
- l.53: kick_mv = 0.275*250.0 # "independent of gain here".
- server.py l.50 and experiments/common.py l.108 scale only w_syn (0.275 x w_syn_scale x gain). No script overrides kick_mv (grep).

Under Shiu's rule (w_syn x 250) the kick would be:
- female: 48.1 mV at gain 0.7, 96.3 mV at 1.4
- male (scale 0.542): 37.3 mV at gain 1.0, 26.1 mV at 0.7

Consequence, reasoned from the constants (no simulation was run): every one of these kicks is far above the 7 mV gap from rest (-52) to threshold (-45). In lif.py (l.232-240) a kick is added to v unless the neuron is refractory, and then the neuron fires. So one kick gives one spike under either rule, and the rates should not change. The hum uses the same kick. This is a choice that departs from Shiu's code, and it is not declared in Note 11. It is disclosure only.
WORDING: Note 1: "sensory drive by Poisson kicks of 68.75 mV, fixed at every gain and in the male (Shiu et al.'s code sets the kick to 250 x the per-synapse weight; any kick above 7 mV fires a resting neuron, so this does not change rates)". Add "the fixed sensory kick" to "Mine" in Note 11.

### [meta] 24c: Arena touch = all 1,417 head bristles, both sides, at 200 Hz on any contact
PAPER: l.93: "When a female's head is touched she extends her ovipositor ... Touch also switched off the neurons she steers with ... so a touched female freezes." Note 11: "the stimulus rates (100\,Hz on the bench, at most 150\,Hz in the body, 200\,Hz for touch)". l.101: "bumped into each other by chance, and then stayed together, because touch switched off their steering".
VERDICT CONFIRMED headline=False
EVIDENCE: How touch is wired:
- brain/flybrain/senses.py l.76: 'bristle' = every cell_type ^BM_, with no left/right split (only the ORN and thermo groups are split, l.99-102).
- l.200: drive('bristle', 1.0 if (hit or collided or fly_contact) else 0, R_BURST).
- R_BURST = 200 Hz (l.33).
- bot/observe.js l.261: fly contact = any fly within 1.3 blocks, from any direction. l.288: collided = bot.entity.isCollidedHorizontally, i.e. against a block or wall.

The neurons driven: data/Supplemental_file1_neuron_annotations.tsv has 1,417 BM_ neurons, all mechanosensory. 705 are left and 712 right; 1,113 are BM_InOm (eye bristles). In the male, about 819 are BM_ by type (malecns_neurons.csv.gz).

The item understates it: walls trigger the burst too. Counting ticks of wall collision without fly contact against fly-contact ticks:
- clean mf female 1,658 vs 41
- hum ff 2,902 vs 1,767
- faint-smell ff 2,519 vs 7,294
- rep-hum ff 1,769 vs 17,087

Note 11 discloses only the 200 Hz rate.

This narrows "females stay together because touch stops steering" without refuting it. The stimulus is a maximal bilateral whole-head and eye burst, which no real head bump produces, and the paper has no specificity control (design_critique).
WORDING: Note 11: "... 200 Hz for touch, applied to all 1,417 head and eye bristle neurons of both sides at once (1,113 of them on the eye) whenever the fly is within 1.3 blocks of another fly, pressed against a wall, or hit". l.93: "When all the bristles on a female's head are driven at once, she extends her ovipositor". l.123 prediction: say it concerns a strong, bilateral touch to the head.

### [meta] 25a: Missing citation for "A real female walks away"
PAPER: l.101: "A real female walks away. These two stood pressed together for up to eighty-six seconds, extending their ovipositors at each other."
VERDICT CONFIRMED headline=False
EVIDENCE: The sentence has no citation, and nothing in the bibliography covers female-female separation. The only nearby support, l.51 ("A female who has mated recently walks off ... \citep{greenspan2000courtship}"), is about a mated female rejecting a male. The long draft (paper/archive/flycraft_long_20260926.tex l.481) had the same uncited sentence ("A real female walks away from another female"). Its only female-female reference, Nilsen et al. 2004 ("Two females that meet over food sometimes fight"), is not in the short paper and does not say females part. RESEARCH_NOTES l.1154, PAPER.md l.233/320 and design_claims_ledger.md l.75 ("uncited") agree.

Candidate source, checked by web search: Ramdya et al. 2015, Nature 519:233-236, doi:10.1038/nature14024. Flies respond to appendage touches from other flies with movement, and this drives collective odour avoidance. It is about touch-evoked movement in general, not female pairs specifically, so the wording should match it.
WORDING: "Real flies that touch each other tend to move off \citep{ramdya2015mechanosensory}; these two stood pressed together for up to eighty-six seconds, extending their ovipositors at each other." Add the bib entry: Ramdya, P., Lichocki, P., Cruchet, S., Frisch, L., Tse, W., Floreano, D., & Benton, R. (2015). Mechanosensory interactions drive collective behaviour in Drosophila. Nature, 519, 233-236. If that source is not wanted, soften the sentence to "I know of no report of two real females staying pressed together like this".

### [meta] 25b: Missing citation for "Real virgins wait for the male"
PAPER: l.110: "In the box her acceptance neuron fired whether the male was near or far, and she signalled acceptance nearly a hundred times a minute, yet she never walked towards him. Real virgins wait for the male too."
VERDICT CONFIRMED headline=False
EVIDENCE: The sentence has no citation, and design_claims_ledger.md l.91 lists it as "uncited". It is supported indirectly by l.51 ("A virgin slows down and lets him."), where Greenspan & Ferveur 2000 is cited at the end of the same passage, but l.110 itself cites nothing. The long draft l.500 was also uncited.

A primary source, checked by web search: Bussell, Yapici, Zhang, Dickson & Vosshall 2014, Current Biology 24:1584-1595. Female receptivity is pausing (not slower walking) in response to male courtship cues, plus opening of the vaginal plates; Abd-B neurons control the pausing.
WORDING: "Real virgins do not seek the male out either; they pause when he courts them \citep{greenspan2000courtship,bussell2014abdominal}." Add the bib entry: Bussell, J. J., Yapici, N., Zhang, S. X., Dickson, B. J., & Vosshall, L. B. (2014). Abdominal-B neurons control Drosophila virgin female receptivity. Current Biology, 24, 1584-1595.
