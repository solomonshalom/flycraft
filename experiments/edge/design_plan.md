# Flycraft edge-case suite: merged design (read-only phase; nothing was run or modified)

## 0. Facts checked in the code, and how the arms' disagreements are settled

- **Output redirection works without editing any script.** Every simulation script does `from common import RES, ...`. This covers benchmark, conditioning, contact_stop, expression_probe, gain_sweep, noise_floor, odor_code, odor_dose, precontact_dose, sensitivity, shuffle_control, social_probe and state_probe. Setting `common.RES` before `runpy` runs a script therefore sends all of its output elsewhere.
  - Only `social_probe.py`, `compare_results.py`, `paper_numbers.py` and `replication_stats.py` have `--out`.
  - `noise_floor.py` has `--suffix`, but it merges into any existing file of the same name.
- **Default names that would overwrite reproduce.sh outputs:**
  - `gain_sweep` (no gain tag)
  - `state_probe` (no gain, seed or noise tag)
  - `contact_stop_<dataset>.csv` (no variant)
  - `odor_code_<dataset>.csv`
  - `odor_dose` at gain 1
  - `benchmark`, `sensitivity`, `expression_probe`, `shuffle_<variant>_<mode>`
  - `social_probe` at gain 1 without `--out`
  - `conditioning` files with `--tag`: `paper_numbers.py` globs `conditioning_*_seed*.csv` in `experiments/results` and would pool them.
- **Decision on outputs:** every edge output goes to `experiments/results_edge/<step>/`, one subdirectory per step, so steps cannot overwrite each other. The only exception is the 180 MB Brian2 exports, which go to `$TMPDIR`. No existing script is edited; new code goes only under `experiments/edge/` and `brain/tests/edge_*`. This replaces the arms' `$EDGE` rsync copy, `release/edge_20260927` and inline `python -c` wrappers.
- **Seeds.** `run_trials` always uses seeds 0..n−1. `odor_dose`, `odor_code` and `conditioning` seed per trial the same way. So a run with more seeds contains the paper's seeds, and those must match the paper files to the digit, which is a free determinism check. No seed-offset code is needed. The seed null for the dt sweep is split-half (seeds 0–4 against 5–9).
- **Chunk count.** `T = min(NUMBA_NUM_THREADS, 8)` (lif.py l.311), so 8 and 10 threads should give bit-identical results.
  - `LIFParams` is a mutable dataclass, and `noise_hz` is read on every `_call`, so the hum can be switched off mid-run.
  - `make_sim` call sites: social_probe passes gain and noise_hz; state_probe passes gain; sensitivity passes dt and legacy.
- **Rewiring.** `shuffle_control.rewire` can be imported (the script body is guarded by `__main__`). `default_rng(100+s)` rebuilds exactly the rewired brains of Fig 6.
- **Scripts that must never be imported** (they run on import): `benchmark.py` and `sensitivity.py`. Copy their constants instead.
- **contact_stop.** It passes signs and eLN explicitly. `FLYBRAIN_MIN_SYN` affects only the 6 Shiu-table rows; the Zenodo rows set `min_syn` themselves.
- **odor_code.** It ignores `FLYBRAIN_SIGNS` and `FLYBRAIN_ELN` (each variant is explicit), accepts any `known+elnX`, and scores Jaccard(empty, empty) as 0.
- **Script ages.** Every simulation script and lif.py is older than 25 Sep 23:40. Only compare_results, paper_numbers, replication_stats, figures_print and figure_replication changed later. So any simulation-file difference between the 26 Sep re-run and the frozen copy is nondeterminism.
- **Brian2.** The kick in `brian2_reference.py` is `w_syn·f_poi`, which scales with gain and w_syn_scale; the kernel kick is fixed at 68.75 mV. These agree only for the female at gain 1.
  - `$TMPDIR/flycraft_brian2/flywire_export.npz` exists (published model, 182 MB) and `b2venv/bin/python` exists.
- **Arena launch.** `run_pair.sh` has `sleep 6` between the bots and gives both brains the same `--seed`. `trials.sh` hard-codes seeds 1–5 and the 5 start positions.
- **Numbers re-checked:**
  - Frozen cVA steer: 0 / +1.67 / +0.58 / −0.17 / +2.33 Hz at 25–150 Hz. CO2: 0 / +0.92 / +1.08 / −0.42 / −2.83.
  - Published-lobe block shuffle: JO-A→GF 6.4 vs 10.6 Hz intact; JO-B 0.3 vs 4.8; touch→GF 77.7 and MDN 31.9 (intact 0.0 / 0.7); frac_moved 0.943.
- **Live queue at 00:20.** 5 of 15 steps done; shuffle is running (published block). The remaining steps take about 3–3.5 h (to roughly 03:45–04:00).
  - Memory: 58 % free, but swap 7.1 of 8 GB used.
  - Female steps peaked at 0.9–1.5 GB; core-check with Brian2 at 1.53 GB.
- **Threads:** 6 for every offline step, matching the paper files; the queue is serial, so there is no reason for 3 or 4. The arena uses 3 per brain.

## 1. Offline edge-case queue

### Launch and conventions

The queue can be started now; step S0 waits for the re-run to finish.

```
mkdir -p logs/edge experiments/results_edge
MEMLOG=logs/edge/guarded_mem.tsv PEAKS=logs/edge/guarded_peaks.tsv OUTDIR=logs/edge \
  caffeinate -i experiments/run_guarded.sh experiments/edge/steps_20260927.tsv logs/edge_done
```

- The step file is created in the run phase. Its lines are `name<TAB>gate<TAB>command`. Commands run with `bash -c` from the project root, with pyenv python3, `NUMBA_NUM_THREADS=6` and `PYTHONWARNINGS=ignore`.
- `OUTDIR` must exist before launch, because run_guarded does not create it.
- **[H]** means the prefix `set -e; O=experiments/results_edge/<step>; mkdir -p $O; R=experiments/edge/run_redirect.py; G=experiments/edge/grid_probe.py;`
- **[P]** means the paper's model: `export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25;`. On MaleCNS, `known` does nothing, so the variant is `all_min1+eln0.25`.
- **Gates:** 10 for analysis-only steps, 25 for female-connectome steps, 35 for male-connectome or shuffle steps.
- Time estimates are uncontended at 6 threads and include connectome loads (female about 30 s, male about 90 s). Calibration from the re-run logs: female sims take about 0.7 s of wall time per brain-second, male about 1.3.
- Every new script writes `<file>.tmp` and renames it at the end, so run_guarded's single retry is safe.

### Priority 1 (about 3.9 h)

**S0 `gate-rerun-finished`** · 0 min · gate 0
- Command: `while pgrep -f 'run_guarded.sh logs/rerun_2026092[6]_steps' >/dev/null || ! ls logs/rerun_20260926_done/figures* >/dev/null 2>&1; do sleep 120; done`
- The `[6]` keeps pgrep from matching its own command line.

**S1 `smoke-new-code`** · 5 min · 1.6 GB · gate 25
- Runs every new script at minimal size so a broken script fails fast:
  - `grid_probe --drives 'none;sugar GRNs' --seeds 1 --ms 100`
  - `run_redirect` with `social_probe --seeds 1 --ms 100 --out $O/s.csv`
  - `odor_code_plus --limit 1 --seeds 1`
  - `conditioning_edge --protocol backward --cycles 1 --train-s 1 --rest-s 1 --test-s 0.2`
  - `expression_harsh --modes structure`
  - `arena_audit --quick`
- Output: `$O/*`. Pass: every script exits 0.

**S2 `rerun-determinism-diff`** · 1 min · 0.3 GB · gate 10
- Tests Note 10, "to the digit on the same thread count".
- Command: [H] `python3 experiments/compare_results.py --old release/pre_rerun_20260926/results --new experiments/results --out $O/rerun_0926_vs_0925.md`
- Keep the sentence if every simulation CSV is identical to the digit (wall/timing columns ignored).
- If any differs, the determinism sentence is false; find the source before the paper says "to the digit".

**S3 `frozen-reanalysis`** · 1 min · 0.3 GB · gate 10
- Tests the Note 3, 6, 7 and 9 numbers from existing files.
- Command: [H] `python3 experiments/edge/edge_report.py --frozen release/pre_rerun_20260926/results --out $O/frozen.md`
- There is no pass criterion; it produces the corrected numbers listed in section 4.

**S4 `arena-log-audit`** · 3 min · 0.5 GB · gate 10
- Tests Notes 8 and 9: the 86-s bout, the 24/33 lean, and replication comparability.
- Command: [H] `python3 experiments/edge/arena_audit.py --results release/pre_rerun_20260926/results --out-dir $O`
- Keep the lean only if the far-bias-corrected male-female sign test gives p < 0.025 (Holm over mf/ff) and the within-pre-contact shift null gives P < 0.05.
- Keep the 86-s bout only if it starts after both flies are present and more than 1.3 blocks apart.
- Series whose rows are stalled for more than 5 % of the time, or with less than 60 s of brain time, are marked not comparable.

**S5 `brian2-first-divergence`** · 8 min · 1.6 GB · gate 25
- Tests Note 1, "spike for spike".
- Command, [H] without [P] (published model):
  ```
  B=${TMPDIR:-/tmp}/flycraft_brian2
  test -f $B/flywire_export.npz || env -u FLYBRAIN_SIGNS -u FLYBRAIN_ELN python3 brain/tests/export_for_brian2.py --dataset flywire --out $B/flywire_export.npz
  b2venv/bin/python brain/tests/edge_brian2_reference.py --conn $B/flywire_export.npz --drive in_grn_sugar:100 --ms 1000 --seeds 3 --dt 0.1 --record-times --out $O/ref_sugar_times.npz
  export NUMBA_CACHE_DIR=${TMPDIR:-/tmp}/flycraft_edge_nbcache
  D="python3 brain/tests/edge_brian2_divergence.py --conn $B/flywire_export.npz --ref $O/ref_sugar_times.npz --dt 0.1"
  $D --out $O/div_default.json
  $D --eps-v 0 --eps-g 0 --out $O/div_eps0.json
  $D --eps-v 0 --eps-g 0 --float64 --out $O/div_eps0_f64.json
  ```
- Keep and sharpen the sentence if the first mismatch is at a neuron within about 0.01 mV of threshold, and seed 0 becomes identical with eps = 0 (or eps = 0 plus float64) while seeds 1–2 stay identical.
- If the first mismatch is more than 0.05 mV from threshold, or the divergence survives eps = 0 plus float64, there is a semantic difference: drop "spike for spike".

**S6 `brian2-paper-model`** · 12 min · 2.0 GB · gate 25
- Tests Brian2 agreement for the model the paper actually uses, with the drives the social claims rest on, at production dt.
- Command: [H][P]
  ```
  S=${TMPDIR:-/tmp}/flycraft_edge_b2; mkdir -p $S
  python3 brain/tests/export_for_brian2.py --dataset flywire --out $S/paper_export.npz
  for D in in_orn_cva in_bristle in_grn_sugar; do
    b2venv/bin/python brain/tests/brian2_reference.py --conn $S/paper_export.npz --drive $D:100 --ms 1000 --seeds 3 --dt 0.1 --out $O/ref_${D}_dt0.1.npz
    python3 brain/tests/compare_brian2.py --conn $S/paper_export.npz --ref $O/ref_${D}_dt0.1.npz --dt 0.1 > $O/cmp_${D}_dt0.1.txt
  done
  b2venv/bin/python brain/tests/brian2_reference.py --conn $S/paper_export.npz --drive in_grn_sugar:100 --ms 1000 --seeds 3 --dt 0.2 --out $O/ref_sugar_dt0.2.npz
  python3 brain/tests/compare_brian2.py --conn $S/paper_export.npz --ref $O/ref_sugar_dt0.2.npz --dt 0.2 > $O/cmp_sugar_dt0.2.txt
  ```
- Keep if, for every drive, every printed group is within max(2 seed-SD, 10 %) with per-neuron r ≥ 0.99, and sugar is identical in at least 2 of 3 seeds at both dt.
- An odour or touch group more than 3 SD off, or r < 0.95, limits the Brian2 claim to taste.

**S7 `dt-sweep-female`** · 13 min · 1.5 GB · gate 25
- Tests Note 1, "identical at 0.1–0.5 ms", plus the freeze and the deciders under dt.
- Command: [H][P]
  ```
  python3 experiments/social_probe.py --dataset flywire --seeds 10 --out $O/social_dt0.2.csv
  for dt in 0.1 0.5; do python3 $R --res $O --sim dt=$dt experiments/social_probe.py -- --dataset flywire --seeds 10 --out $O/social_dt$dt.csv; done
  ```
- Seeds 0–4 of `social_dt0.2` must equal the re-run paper file to the digit.
- Keep "the same within seed noise" for dt 0.1 against 0.2 if every headline readout differs by less than 2 SE and by no more than the split-half null. Headline readouts: MN9, feed MNs, DNp13, DNa L/R, the freeze indices for food+touch and cVA+touch, GF, PPL1, KC, and the six deciders.
- dt 0.5: report the size of the shift.
- If 0.1 and 0.2 differ beyond 2 SE on a headline number, quote the size or re-run the headline numbers at 0.1.

**S8 `thread-sweep-female`** · 5 min · 1.4 GB · gate 25
- Tests Note 10's thread-count sentence.
- Command: [H][P] `for T in 8 10; do NUMBA_NUM_THREADS=$T python3 experiments/social_probe.py --dataset flywire --seeds 5 --out $O/social_T$T.csv; done`
- The comparison baseline is the re-run's T6 file, `experiments/results/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv`.
- Keep if T8 equals T10 bit for bit, T6 against T8 differences are no larger than the per-input seed SD, and no readout crosses the 2 Hz presence line.
- If T8 differs from T10, something other than chunking depends on threads.

**S9 `persistence-female`** · 7 min · 1.5 GB · gate 25
- Tests the 0.6–1 s from-rest protocol, "no activity of its own", and "walking is not in the wiring".
- Command: [H][P] `python3 $G --dataset flywire --preset persistence --seeds 2 --out $O/persistence_g1.csv`
- Pass conditions:
  - For the sensory drives, 1-s bins 2–10 are within max(10 %, 2 seed-SD) of each other with no trend.
  - The 0–1 s mean is within 10 % of the 1–10 s mean for every headline readout.
  - After drive offset every count is 0 from the second 50-ms bin on, and `act_n` is 0.
  - After the hum transients the brain is silent within 100 ms of the noise being switched off.
- Drift or latching: quote the numbers as 1-s responses from rest. Persistence after offset: say the model is history-dependent.

**S10 `sensitivity-fullmap-female`** · 22 min · 2.0 GB · gate 25
- Tests Note 5 (deciders "in all 14 conditions"), the freeze "every alternative but one", JO-A, aBN1 and bitter under the third test, and "nothing that does not involve smell depends on the change".
- Command: [H][P] `python3 $G --dataset flywire --conditions sensitivity --drives all --anchors --seeds 3 --ms 600 --out $O/sensmap_flywire.csv --check-against experiments/results/sensitivity_flywire_shiu_min1+known+eln0.25.csv`
- Pass conditions:
  1. The check-against file reports zero mismatches.
  2. The six decider groups are 0.0 for every drive in all 14 conditions (any non-zero cell gets named in Note 5).
  3. The freeze index is at least 0.35 in every condition where DNa alone reaches 2 Hz, including 50/150 Hz, dt 0.1/0.5, legacy numerics and the Shiu table at ≥5 synapses.
  4. JO-A→GF is at least 5 Hz at 50 Hz, 150 Hz and ≥5 synapses, and at least twice the largest odour→GF.
  5. aBN1 from JON-CE is at least 5 Hz with JON-F below a third of it, and bitter at 100 Hz holds MN9 below 25 % of sugar alone, in every condition.

**S11 `gain-rate-map-female`** · 11 min · 1.6 GB · gate 25
- Tests "at every gain up to 1.4", "whatever the fly senses", "taste never reaches the teaching neurons", and the JO-A rate range.
- Command: [H][P]
  ```
  python3 $G --dataset flywire --drives all --gains 0.7,1.4 --seeds 3 --ms 1000 --out $O/map_gain.csv
  python3 $G --dataset flywire --drives all --cond hz=200 --cond hz=300 --seeds 3 --ms 600 --out $O/map_rate.csv
  ```
- Keep if every decider (mean and max1) is 0 for every drive at 0.7 and 1.4 and at 200 and 300 Hz, and sugar, bitter and touch give PAM and PPL1 at most 0.5 Hz in all of these.
- A decider responding at gain ≤1.4, or at 200 Hz (the body's rate), makes the Note 5 sentence conditional.

**S12 `anchors-female`** · 8 min · 1.6 GB · gate 25
- Tests grooming and bitter suppression, which never passed the three tests, and bitter at 10 seeds.
- Command: [H][P]
  ```
  python3 $G --dataset flywire --preset anchors --gains 0.7,0.8,0.9,1.0,1.2,1.4 --seeds 10 --ms 1000 --out $O/anchors_gain.csv
  python3 $G --dataset flywire --preset anchors_rate --seeds 5 --ms 1000 --out $O/anchors_rate.csv
  ```
- Keep if MN9 with bitter at 100 Hz stays below 25 % of sugar alone, with a monotone dose over 25/50/100, at every gain; and aBN1 is at least 5 Hz with JON-F below a third of JON-CE at gains 0.7–1.4 and at 50–150 Hz.
- A failure at 0.7 qualifies the reflex the same way the male MDN is qualified. Report the 10-seed bitter mean ± SD.

**S13 `minsyn-scan-female`** · 8 min · 2.0 GB · gate 25
- Tests "reverses only under the ≥5-synapse threshold" and "carried by the weakest connections".
- Command: [H][P] `python3 $G --dataset flywire --preset freeze` with eight `--cond` rows: `conn=shiu,min_syn_mem=1`, `conn=shiu,min_syn_mem=2`, `conn=shiu,min_syn_mem=3`, `conn=shiu,min_syn_mem=5`, and the same four with `conn=zenodo`. Then `--seeds 5 --ms 600 --out $O/minsyn.csv`.
- edge_report first checks that Shiu k=1 equals the paper's model row, and Zenodo k=5 equals the "Zenodo ≥5" row, of `experiments/results/contact_stop_flywire.csv` to the digit.
- Keep the sentence if both tables keep an index of at least 0.35 at k ≤ 3 and flip at k = 5 (index ≤ 0.1, with touch raising DNa).
- If the Shiu table still freezes at 5, narrow the sentence to the Zenodo table. If the flip happens at k = 2–3, say the freeze depends on 1–2-synapse connections.

**S14 `touch-dose-female`** · 6 min · 1.5 GB · gate 25
- Tests the freeze and the ovipositor reflex under realistic touch, the closing prediction, and whether touch gates feeding.
- Command: [H][P]
  ```
  python3 $G --dataset flywire --preset touch_dose --seeds 5 --ms 600 --out $O/touch_dose.csv
  python3 $G --dataset flywire --drives 'food odor@100;food odor@100 & touch (all head bristles)@200' --protocol bins --on-ms 5000 --bin-ms 1000 --off-ms 0 --seeds 5 --out $O/touch_5s.csv
  ```
- Keep "a general reflex" if:
  - the freeze index is at least 0.35 on both DNa for left-only and for right-only touch, and for ≤25 % of bristles at 200 Hz;
  - it rises with touch rate and holds for 5 s;
  - DNp13 is at least 10 Hz at 200 Hz for ≤25 % of bristles and for one side.
- Otherwise say "a whole-head touch" and rewrite the closing prediction.
- If MN9 under sugar with bristles falls below 80 % of sugar alone, add one sentence in Note 4 (touch gates feeding).

**S15 `block-shuffle-female-plus`** · 25 min · 3.0 GB · gate 35
- Tests "Scramble the wiring and every reflex disappears", on the paper's model, including aBN1, bitter and the SAG state.
- Command: [H][P] `python3 $G --dataset flywire --drives all --anchors --preset states_lite --cond rewire=block,shuffle=0 --cond rewire=block,shuffle=1 --seeds 3 --ms 800 --out $O/block_flywire_paper.csv --check-against experiments/results/shuffle_flywire_shiu_min1+known+eln0.25_global.csv` (the intact rows are what gets checked).
- A reflex "disappears" if every block brain gives at most 2 Hz, or its specificity (target minus DN-all) drops by at least 80 %. Reflexes keeping 50 % or more (JO-A is expected to) get a clause.
- SAG must drive pC1a–c and vpoEN/DN at most 1 Hz in block brains.
- Note 2 then reports both nulls.

**S16 `state-split-female`** · 3 min · 1.5 GB · gate 25
- Tests Note 6, "vpoDN 5.7 Hz" (a pooled readout).
- Command: [H][P] `python3 $G --dataset flywire --preset state_split --seeds 10 --ms 1000 --out $O/state_split.csv`
- This is a relabel: the split readouts name the neuron that fires. If vpoEN carries it rather than DNp37, the genital-plate sentence changes.

**S17 `state-gain-window-female`** · 8 min · 1.5 GB · gate 25
- Tests whether the virgin state holds inside the paper's own gain window.
- Command: [H][P] `for g in 0.7 1.4; do python3 $R --res $O/gain$g experiments/state_probe.py -- --dataset flywire --seeds 5 --gain $g; done`
- Add "at gains 0.7–1.4" if at both gains SAG alone gives pC1a ≥ 5 Hz and vpoEN/DN > 1 Hz, SAG+touch gives more pC1d/e than touch alone, the no-state deciders stay at 0.0 and oviDN stays at 0.
- If pC1a is below 2 Hz at 0.7, the virgin state has a gain window.

**S18 `state-10seeds-female`** · 7 min · 1.5 GB · gate 25
- Tests held-out seeds for 21 / 19 / 5.7, the NPF +6.8 Hz shift, and whether DNp13 is state-blind.
- Command: [H][P] `python3 $R --res $O experiments/state_probe.py -- --dataset flywire --seeds 10`
- Seeds 0–4 must equal the re-run file to the digit. Seeds 5–9 must reproduce the SAG values within 2 SEM.
- Compare the NPF MN9 shift against the band of unrelated states at n = 10 (Welch).
- DNp13 under SAG or pC1a–c should be within 2 SEM of no state.

**S19 `state-hum-female`** · 8 min · 1.5 GB · gate 25
- Tests "hunger changes nothing", which was measured only in a silent brain.
- Command: [H][P] `python3 $R --res $O --sim noise_hz=0.2 experiments/state_probe.py -- --dataset flywire --seeds 5`
- Keep if every hunger state's mean change from "none" on the hum is within 2 SEM and within the unrelated-state band on feed MNs, MN9, DNa L/R, PPL1, PAM and MDN.
- If a change is larger than about 3 Hz and larger than the unrelated states', qualify the sentence. Also check that SAG gives DNp37 near the arena's 15.8 Hz.

**S20 `p1-matched-null-male`** · 6 min · 4.5 GB · gate 35
- Tests "P1 switches on song": pIP10 50, TN1 8.
- Command: [H][P] `python3 $G --dataset malecns --preset matched_null --seeds 3 --ms 1000 --out $O/matched_null_male.csv`
- Keep if, in at least 19 of 20 draws of 148 output-matched central neurons, pIP10 stays at most 10 Hz and TN1 at most 2 Hz.
- If the median draw gives pIP10 of 25 Hz or more, the sentence becomes "a lot of central drive reaches the song command".

**S21 `eln-sweep-100hz`** · 6 min · 1.4 GB · gate 25
- Tests "a quarter, the most that keeps smells apart", and the Note 3 overlaps.
- Command: [H] `python3 experiments/edge/odor_code_plus.py --dataset flywire --variants known+eln0.15,known+eln0.2,known+eln0.25,known+eln0.3,known+eln0.35,known+eln0.4,known+eln0.5 --hz 100 --seeds 3 --odors test10 --out-dir $O`
- Criterion, fixed before the run: live-only between-odour KC Jaccard ≤ 0.25, within-odour at least twice between, and mean glomerular spread ≤ 35 %.
- 0.25 is "the most" only if 0.3 fails; otherwise reword. The `known+eln0.25` rows must equal the re-run `odor_code_flywire.csv` for seeds 0–1.

**S22 `odor-dose-10seeds`** · 13 min · 1.4 GB · gate 25
- Tests Note 9, "cVA turns her towards it by 0.6–2.3 Hz", food avoidance, and the thread/seed noise on steering.
- Command: [H][P] `python3 $R --res $O experiments/odor_dose.py -- --dataset flywire --seeds 10 --rates 50 75 100 125 150`
- Seeds 0–2 at rates 50/75/100/150 must equal the re-run file.
- Keep "turns towards" only if the cVA steer (paper_numbers `steer()`) has a 95 % CI above 0 at 3 or more of the 5 rates and exceeds CO2's; otherwise delete the clause.
- Food-type avoidance is kept if it is negative in at least 90 % of cells.

**S23 `cond-long-training`** · 15 min · 2 GB · gate 25
- Tests "odour-specific": does the CS− erode with longer training?
- Command: [H] `for o in 'vinegar ester' 'ester vinegar'; do set -- $o; for us in 'dan --valence reward' 'wiring'; do python3 $R --res $O experiments/conditioning.py -- --dataset flywire --signs known --eln 0.25 --us $us --cycles 10 --csp $1 --csm $2 --seed 0 --tag cyc10; done; done`
- Keep if the index is at least 0.3 in both orders and at least 0.2 above the matched no-teaching-signal run, and the CS+-specific DN change over that control stays below 2 Hz.
- Otherwise say that specificity holds only for short training.

**S24 `cond-contingency`** · 16 min · 2 GB · gate 25
- Tests "0.04 without a teaching signal" as proof of association (backward, unpaired and US-only controls).
- Command: [H]
  ```
  C="python3 experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --us dan --seed 0 --out-dir $O"
  $C --valence reward --protocol forward --csp vinegar --csm ester --check-against experiments/results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_vinegar-vs-ester_seed0.csv
  for o in 'vinegar ester' 'ester vinegar'; do set -- $o
    for p in backward unpaired us-only; do $C --valence reward --protocol $p --csp $1 --csm $2; done
    $C --valence punish --protocol backward --csp $1 --csm $2
  done
  ```
- The forward run must equal the check-against file to the digit.
- Keep "associative" if backward and unpaired are within 0.1 of the no-teaching control in both orders, and US-only leaves both odours' taught-compartment drive at 0.85 or more.
- Otherwise part of the index comes from the US itself.

**S25 `cond-pair-sweet-ester`** · 6 min · 2 GB · gate 25
- Tests "0.54 ± 0.02" as a one-pair result, using the hardest pair (4 of 6 glomeruli shared).
- Command: [H] `for o in 'sweet ester' 'ester sweet'; do set -- $o; for us in 'dan --valence reward' wiring; do python3 $R --res $O experiments/conditioning.py -- --dataset flywire --signs known --eln 0.25 --us $us --csp $1 --csm $2 --seed 0; done; done`
- If the index is at least 0.3 in both orders and the no-teaching control at most 0.1, report the index as a range over pairs.
- If it is below 0.2, say specificity depends on how many Kenyon cells the two odours share.

**S26 `expression-harsh`** · 10 min · 2.5 GB · gate 25
- Tests "reach none", "no working route" and "a notebook nobody downstream reads".
- Command: [H][P] `python3 experiments/edge/expression_harsh.py --dataset flywire --modes drive,types,bypass,kick-nodn,structure --seeds 3 --out-dir $O`
- "No working route" stands only if:
  - the punishment set at 100 Hz moves fewer than 3 DN types by more than 5 Hz, and DNa, MDN, DNp09 and GF by less than 5 Hz;
  - under the lateral-horn bypass, odour activity reaching DNs through the MB is below 2 Hz and does not change when the MBONs are silenced;
  - the reward set at 20–100 Hz reaches no DN.
- Otherwise the text becomes "a working route that the memory is too weak to use".

**S27 `edge-report`** · 1 min · gate 10
- Command: `python3 experiments/edge/edge_report.py --all --out experiments/results_edge/EDGE_REPORT.md`
- Output: a KEEP / REWORD / CHANGE verdict per claim, each with its paper line.

### Priority 2 (about 2.25 h)

| step | gate | min | GB | command ([H][P] unless noted) | tests; pass |
|---|---|---|---|---|---|
| `sensitivity-fullmap-male` | 35 | 25 | 4.0 | `python3 $G --dataset malecns --conditions sensitivity --drives all --seeds 3 --ms 600 --out $O/sensmap_malecns.csv --check-against experiments/results/sensitivity_malecns_all_min1+eln0.25.csv` | "no other smell at all": keep for DNp13 if every non-cVA odour is ≤2 Hz in all 13 conditions; give MN9/PPL1/song-MN specificity per condition; P1 mean and max1; MDN per condition |
| `gain-map-male` | 35 | 10 | 4.0 | `python3 $G --dataset malecns --drives all --gains 0.7,1.4 --seeds 3 --ms 1000 --out $O/map_gain_male.csv` | P1 per neuron: no single P1/pC1 neuron above about 5 Hz at ≤1.4, otherwise name it; pIP10 answers only cVA-containing drives |
| `global-shuffle-male-plus` | 35 | 12 | 5.0 | `python3 $G --dataset malecns --drives all --preset states_lite --cond rewire=global,shuffle=0 --seeds 3 --ms 800 --out $O/global_male.csv --check-against experiments/results/shuffle_malecns_all_min1+eln0.25_global.csv` | song/wing MNs, and P1-state → pIP10, at ≤2 Hz in the Fig 6 male brain |
| `state-dose-female` | 25 | 10 | 1.5 | `python3 $R --res $O/s100 experiments/state_probe.py -- --dataset flywire --seeds 5 --state-hz 100; for h in 10 20 60; do python3 $R --res $O/s$h experiments/state_probe.py -- --dataset flywire --seeds 3 --state-hz $h; done` | monotone from 10 Hz, pC1a/SAG ratio 0.6–0.8; touch→DNp13 under SAG or pC1a–c against none (Welch; >3 Hz at p<0.01 qualifies the "state-blind" miss); hunger recruits about 0 spikes at 100 Hz |
| `state-nulls-female` | 25 | 9 | 1.6 | `python3 $G --dataset flywire --preset matched_null --seeds 3 --out $O/matched_f.csv; python3 $G --dataset flywire --preset sag_hunger --seeds 10 --out $O/sag_hunger.csv` | matched draws give pC1a–c and vpoEN/DN ≤1 Hz in ≥19/20; SAG+hunger within 2 SEM of SAG alone |
| `odor-code-plus` | 25 | 12 | 2.0 | [H] `odor_code_plus.py` ×3: (a) `--variants known+eln0.25,known+eln0.3,known+eln0.35 --hz 150 --odors test10`; (b) `--variants known+eln0.25 --hz 100,150 --odors glomeruli,library`; (c) `--eln-subsets --hz 100 --odors test10` | ≥70 % of glomeruli give a KC code of 0.5–10 %; library classes overlap ≤0.3; say which subset carries the runaway (fixes "150 cholinergic") |
| `cond-extra-female` | 25 | 12 | 2.0 | redirect `conditioning.py`: `--eta 1.0 --tag eta1.0` (reward and wiring, both orders); pair floral/vinegar (reward and wiring, both orders) | erosion at high eta; index ≥0.3 for a zero-overlap pair |
| `cond-male-noUS` | 35 | 6 | 3.5 | [H] `for o in 'vinegar ester' 'ester vinegar'; do set -- $o; python3 $R --res $O experiments/conditioning.py -- --dataset malecns --eln 0.25 --us wiring --csp $1 --csm $2 --seed 0; done` | male 0.80/0.77 needs a control: ≤0.1 in both compartments and orders |
| `expression-subthreshold` | 25 | 10 | 3.0 | `python3 experiments/edge/expression_harsh.py --dataset flywire --modes sub --sub-rates 50,100,150 --n-src 50 --seeds 3 --out-dir $O` | 18g's verdict holds if silencing either set moves DNa and every DN type by <5 Hz while the targets fire at 1–10 Hz |
| `dt-rounding-control` | 25 | 7 | 1.5 | `python3 $R --res $O --sim dt=0.1 --sim t_ref=2.0 --sim delay=2.4 experiments/social_probe.py -- --dataset flywire --seeds 10 --out $O/social_dt0.1_rounded.csv` | reproduces the dt 0.5 shift within 2 SE, so the shift is rounding |
| `brian2-10s` | 25 | 6 | 1.6 | [H] only: `B=${TMPDIR:-/tmp}/flycraft_brian2; b2venv/bin/python brain/tests/brian2_reference.py --conn $B/flywire_export.npz --drive in_grn_sugar:100 --ms 10000 --seeds 2 --dt 0.1 --out $O/ref10s.npz; python3 brain/tests/compare_brian2.py --conn $B/flywire_export.npz --ref $O/ref10s.npz --dt 0.1 > $O/cmp10s.txt` | rates stay within 2 SD and r ≥0.99 after trajectories part; reword to "identical until a near-threshold spike flips" |
| `micro-semantics` | 25 | 5 | 0.3 | [H] `python3 brain/tests/edge_micro_semantics.py --out $O/k.json; b2venv/bin/python brain/tests/edge_micro_semantics_brian2.py --out $O/b.json; python3 brain/tests/edge_micro_semantics.py --compare $O/k.json $O/b.json > $O/cmp.txt` | the refractory rule has real tests again: scenarios 1–4 identical at dt 0.1 and 0.2 |
| `persistence-gain1.4` | 25 | 5 | 1.5 | `python3 $G --dataset flywire --preset persistence --gain 1.4 --seeds 2 --out $O/persistence_g1.4.csv` | same criteria as S9 at the window's upper edge |
| `odor-dose-gain1.4` | 25 | 5 | 1.5 | `python3 $R --res $O experiments/odor_dose.py -- --dataset flywire --seeds 5 --gain 1.4 --rates 50 100 150` | steering signs at 1.4; odours already give 0 DNa at 0.7, so fix that in the text |
| `edge-report-2` | 10 | 1 | | as S27 | |

**Total:** P1 about 234 min plus P2 about 135 min, roughly 6.2 h uncontended. On a shared machine expect about ×1.3; if time runs short, cut P2 from the bottom.

### Priority 3 (optional; list only)

Female, about 25 GB-min each or less unless noted:
- dt 0.05 at 10 seeds (13 min)
- threads 1/2 plus hum at T6/T8 (16)
- 20-s hum runs at T6/T8/dt 0.1 (20)
- low-hum 10-s steady state, noise_floor 0.01/0.02/0.05 via redirect `--suffix _10s_low` (8; male +10)
- gains 1.6/1.8/2.0 map (10)
- 200 Hz at gain 1.4 for 5 s (6)
- min-syn k = 4/7/10 and hum rows (8)
- fine gain sweeps via redirect `gain_sweep`: female (5), male (9, 3.5 GB)
- global rewirings on the paper's female model with anchors, `--cond rewire=global,shuffle=0..1` (10)
- type-preserving rewiring (40)
- 3 extra global rewirings with `--rewire-seed-base 300` (20)
- decider E/I and voltage via `grid_probe --ei` (female 8; male 15, 4.5 GB)
- `decider_paths.py`, no simulation (female 5; male 10, 4.5 GB)
- oviDN positive control, preset `ovidn_reach` (4)
- state at ≥5 synapses (4)
- mated state as SAG silenced on the hum (10)
- other sign rules at 10 seeds via redirect `odor_dose` (16)
- published-lobe `odor_dose` (15)
- gradient-steering bench, preset `gradient` (10)
- non-smell behaviour on the published lobe at gains 0.7/1.4 (8)
- sign rule against eLN split via redirect `gain_sweep` (8)
- freeze across eLN scales (10)
- published runaway over all glomeruli (5)
- conditioning: floor and eligibility (12), US dose (9), balanced no-US (3), aversive pairs (6), taste as the US in context (10), extinction and trace (7), held-out seeds (5)

Male:
- touch dose and arena composite, preset `touch_dose_male` (8, 3.5 GB)
- count-matched one-sided cVA, preset `side_cva_male` (5, 3.5 GB)
- block rewiring, 2 brains (35 min, 5 GB; run alone, suggested gate 45)
- state gain window (15, 4.5 GB), dose and subsets (60), held-out seeds (30)

Brian2:
- hum with `--noise-hz` (15)
- male with `--kick-mv` (35, 3.5 GB, gate 35)
- food and sugar+bitter drives (15)

## 2. New code (no existing script is edited)

Shared helper **`experiments/edge/_edge.py`**:
- `safe_out(path)`: refuse any path under `experiments/results/`; create parent directories; return a temp path that is renamed at the end.
- `sidecar(path, extra)`: write a JSON sidecar with argv, cwd, the `FLYBRAIN_*` variables, `NUMBA_NUM_THREADS`, `numba.get_num_threads()`, `T=min(threads,8)`, python and numba versions, and sha256 of `brain/flybrain/lif.py` and of the script.
- The constants copied from benchmark.py: `SUGAR_L`, `BITTER`, `JON_CE`, `JON_F`, `ABN1`. Import `SHIU_SUGAR` and `SHIU_MN9` from common.

### 2.1 `experiments/edge/run_redirect.py` (about 60 lines)

- Usage: `run_redirect.py --res DIR [--sim KEY=VAL ...] SCRIPT -- ARGS`
- Refuse if `DIR` resolves inside `experiments/results`; otherwise create it.
- Put `experiments/` on the path, import `common`, and set `common.RES = abspath(DIR)`.
- `--sim` keys: `dt`, `t_ref`, `delay`, `eps_v`, `eps_g`, `kick_mv`, `noise_hz`, `legacy`. When given, replace `common.make_sim` with a function that:
  - builds `LIFParams(dt, noise_hz, w_syn=0.275*cx.w_syn_scale*gain, legacy)` from the caller's arguments;
  - applies `dataclasses.replace(p, **overrides)`, so the overrides always win over what the script passes;
  - returns `LIF(cx.W, p, seed)`;
  - prints the effective params on the first call.
- Write the sidecar `DIR/_redirect_<script>_<stamp>.json`, set `sys.argv = [SCRIPT] + ARGS`, and run `runpy.run_path(SCRIPT, run_name="__main__")`.
- At the end, print the files written under `DIR`.

### 2.2 `experiments/edge/grid_probe.py` (the main engine; replaces 11 proposed scripts)

It replaces: `dt_sweep`, `long_run`, `persistence_probe`, `touch_dose`, `anchor_robustness`, `minsyn_scan`, `side_probe`, `state_edge`, `state_null`, the shuffle-plus variant of `shuffle_control`, and the rate side of `decider_drive`.

**Model arguments**
- `--dataset {flywire,malecns}`.
- `--conn`, `--min-syn {1,5}`, `--signs`, `--eln`, `--unclear-ln`. `None` means the environment, as in `connectome.load`.
- `--min-syn` accepts only values that already have a cache. Any other threshold must use `--min-syn-mem K`, so nothing is ever built into `data/`.

**Condition arguments**
- `--conditions {base,sensitivity}`. `sensitivity` holds the CONDITIONS lists copied verbatim from `experiments/sensitivity.py` (female 14, male 13), with the same labels, per-condition `hz`/`dt`/`legacy`, and grouping by connectome key.
  - At start-up, parse `sensitivity.py` with `ast` and assert the lists are identical, so later drift is caught.
- `--cond 'k=v,...'` (repeatable). Keys: `label`, `conn`, `min_syn`, `min_syn_mem`, `signs`, `eln`, `unclear`, `gain`, `hz`, `dt`, `t_ref`, `delay`, `legacy`, `noise_hz`, `eps_v`, `eps_g`, `kick_mv`, `rewire` (`none|global|block|type`), `shuffle`.
- `--gains a,b` is crossed with every condition.
- Defaults: `--gain 1`, `--hz 100`, `--dt 0.2`, `--noise-hz 0`.

**Model building**
- Load once per connectome key; `del` and `gc.collect()` between keys.
- `min_syn_mem=k`:
  - Load with explicit `conn`, `min_syn=1`, `signs='shiu'`, `eln_scale=1.0`, `unclear_ln='excitatory'`. The arguments must be explicit so the environment is not applied to the raw load.
  - Copy `W`, set `data[abs(data) < k] = 0`, call `eliminate_zeros()`, and set the variant to `f"{conn}_min{k}mem"`.
  - Then call `connectome.apply_model_options(cx, signs, eln, unclear)`.
  - Sanity check: for k = 5 the non-zero count must equal the `data` length of `data/connectome_783_<conn>_min5.npz`, otherwise abort. This matters because the Shiu table is thresholded per row before duplicates are summed.
- LIF: `LIF(W, LIFParams(dt, t_ref, delay, noise_hz, w_syn=0.275*scale*gain, legacy, eps_v, eps_g, kick_mv), seed=0)`, identical to `make_sim` at the defaults.
- Rewiring:
  - `from shuffle_control import rewire`.
  - `rng = np.random.default_rng(seed_base + shuffle)`, with `--rewire-seed-base` default 100 and `--swaps-per-edge 3`.
  - Blocks: `block` = factorize `super_class.fillna('na')`; `type` = factorize `cell_type.fillna(super_class).fillna('na')`.
  - Assert the out-degree is unchanged, record `frac_moved`, and build the rewired LIF exactly as shuffle_control does (gain 1).
  - Intact rows are always included (`shuffle = -1`). Free `Wn` after use.

**Drives**
- `--drives all` = `{"none": []} | input_groups(cx)`, in social_probe's order.
- Otherwise a `;`-separated list. A drive's terms are joined by ` & `; each term is `NAME[@hz]` (default `--hz`).
- `NAME` is resolved in this order:
  1. `input_groups`
  2. `state_groups`
  3. the extra input groups: `Shiu sugar` (SHIU_SUGAR+SUGAR_L), `Shiu bitter`, `Shiu JON-CE`, `Shiu JON-F` (FlyWire), `BM left` / `BM right` (`^BM_` with `side ^left$` / `^right$`), `BM_Ant`, `BM_InOm`, `DA1 left` / `DA1 right` / `DA1 na`
  4. `output_groups` (so MBON sets can be driven)
  5. `sel:col=regex,...` passed to `cx.select`
- `--anchors` (FlyWire) appends the anchor drives listed below. `--preset A[,B]` appends preset drives.
- Note that `set_drive` merges duplicate neurons by taking the maximum rate.

**Presets**
- `anchors`:
  - `Shiu sugar@100`
  - `Shiu sugar@100 & Shiu bitter@{25,50,100}`
  - `Shiu bitter@100`, `Shiu JON-CE@100`, `Shiu JON-F@100`
  - `song/sound (JO-A)@100`, `sound (JO-B)@100`
- `anchors_rate`: JON-CE, JON-F, Shiu sugar, JO-A and JO-B, each at 25, 50, 150 and 300 Hz.
- `freeze`: none, food odor, food + touch, cVA (Or67d/DA1), cVA + touch, touch (all head bristles), all at 100 Hz.
- `touch_dose` (female; adds a `block` column):
  - Block 1 (rate): bases none, food odor@100 and cVA@100, each × BM_ at 0/10/25/50/100/150/200/300 Hz.
  - Block 2 (fraction): BM_ subsets of 3/10/25/50/100 %, draws 0–2, using `default_rng(draw).choice(BM, round(p*len), replace=False)`, at 200 Hz with food@100; plus BM_Ant@200 and BM_InOm@200 with food@100.
  - Block 3 (side): BM left / BM right / both at 100 and 200 Hz, with food@100 and with cVA@100.
  - Block 6 (feeding): sugar@100; sugar@100 & BM@100; sugar@100 & BM@200; bitter@100 & BM@200.
- `persistence`: forces `--protocol bins`, with 10 s on (10 bins of 100 ms, then 1-s bins) and 3 s off (4 bins of 50 ms, then 1-s bins).
  - Noise-0 drives: touch, cVA, food odor, JO-A, JO-B, sugar GRNs and pheromones + song + touch at 100 Hz; plus `Or47b (VA1v)@90 & CO2 (V)@3`.
  - Hum-transient conditions: noise 0.05 and 0.2 with drive none, and the noise switched to 0 at offset.
- `state_split`: states {none, virgin (SAG tonic)@30, aroused female (pC1a-c tonic)@30} × inputs {none, touch (all head bristles)@100, song/sound (JO-A)@100}.
- `states_lite`:
  - Female: SAG, NPF and IPC at 30 Hz, each alone and with touch@100.
  - Male: P1, NPF and IPC at 30 Hz, each alone and with contact pheromone@100.
- `sag_hunger`: none, SAG, SAG & NPF, SAG & IPC, SAG & AstA, SAG & DH44 (all at 30 Hz) × {none, touch, sugar GRNs, cVA} at 100 Hz.
- `matched_null`:
  - Groups: female SAG, NPF, IPC; male P1, NPF, IPC. Draw −1 is the real group.
  - For draws 0–19: the pool is every neuron of the group's majority `super_class`, excluding the group and all readout neurons.
  - Each member is replaced by a uniform random candidate whose row sum of |W| is within ±25 % of the member's (±50 % if fewer than 10 candidates), without replacement, using `rng = default_rng(1000+draw)`.
  - Drive at 30 Hz with inputs none and touch@100 (female) or none (male). Record the chosen root ids in a `members` column.
- P3 presets, specified by the arms:
  - `touch_dose_male`: rate block with none and cVA; composites Or47b@100 & ppk25@150 & BM@200, each with one path removed.
  - `side_cva_male`: DA1 left (51); 3 random draws of 51 of the right DA1 ORNs; all right; na; all DA1; at 50, 100 and 150 Hz.
  - `ovidn_reach`: the top 5 excitatory presynaptic types of oviDN by summed positive W, each alone and together, at 30 and 100 Hz.
  - `gradient`: side-split ORN groups as in senses.py, with the observe.js `conc()` levels for a partner at 1.5, 3 and 5 blocks on the left or right; settle 1 s, read 2 s.

**Readouts**
- Every `output_groups(cx)` group, plus these extras:
  - `aBN1` (root id 720575940630907434)
  - `vpoEN` (`^vpoEN$`), `vpoDN (DNp37)` (`^DNp37$`)
  - `pC1a`, `pC1b`, `pC1c`, `pC1d`, `pC1e` (exact types)
  - `oviDNa` (`^oviDNa`), `oviDNb` (`^oviDNb$`), `oviIN` (`^oviIN$`)
  - `DNp13 L` / `DNp13 R`, and `MN9 L` / `MN9 R` in the male
- Each readout gives two columns: `<name>`, the mean rate computed exactly as `run_trials` does, and `<name> max1`, the largest single-neuron rate.

**Protocols**
- `window` (default): per seed, `sim.seed(s); sim.reset(); sim.set_drive(idx, rate); counts = sim.run(ms)`. This is identical to `run_trials`.
- `settle`: add `--settle-ms` of discarded time before the read.
- `bins`: `--on-ms`, `--first-bins KxMS`, `--bin-ms`, `--off-ms`, `--noise-off`.
  - At the end of the on-phase, call `set_drive(empty)`; if `--noise-off` is given, set `sim.p.noise_hz = noise_off`, and restore it after the seed.
  - Assert that every bin is a multiple of dt, because `run()` rounds `ms/dt`.
  - Each bin writes a row with `phase`, `bin_start_ms`, `bin_ms` and `act_n_end = int(sim.act_n.sum())`.
- `--ei GROUPS` (P3): the window is run in 1-ms chunks, reading `sim.v[idx]` after each chunk. It writes `<out>_neurons.csv` with:
  - `v_mean` and `v_max` in mV above rest, and the fraction of time within 1 mV of threshold;
  - E and I for each neuron j: E = Σᵢ max(W_ij, 0)·rᵢ, I the same for negative weights;
  - the mean-field depolarisation 0.275·scale·gain·0.005·(E−I) mV;
  - the top 3 presynaptic types by W_ij·rᵢ.

**Output**
- `--seeds N` (seeds 0..N−1) and `--ms`.
- `--out` is required and goes through `safe_out`. One long CSV row per condition × shuffle × drive × seed [× bin], with columns:
  - identity: every condition field plus `variant`, `frac_moved`, `drive`, `drive_terms` (`name@hz|...`), `block`, `members`, `seed`
  - totals: `n_driven`, `total_spikes`, `recruited_spikes` (total minus the driven neurons' spikes), `active_frac`, `wall_s`
  - the readout columns
- Plus the JSON sidecar.

**`--check-against FILE`**
- Per-seed reference files (social_probe; state_probe; shuffle intact rows where `connectome=='intact'`): compare every shared output column for matching (drive, seed), which must match to within 1e-9.
- Sensitivity files: compare seed means with the `'<input> -> <output>'` cell of the same condition label.
- Write `<out>.check.txt` with counts and mismatches, and exit 0. `edge_report` treats any mismatch as blocking.

### 2.3 `experiments/edge/conditioning_edge.py`

A copy of `conditioning.py` with these changes:
- `--out-dir` is required (through `safe_out`).
- `--w-min` (0.1) and `--tau-elig` (1.0) are passed to `PlasticityConfig`, which keeps `tau_rec=0`.
- `--wiring-us {sugar,bitter,touch,labellar}`: `gustatory & sub_class 'sugar/water'` / `'^bitter$'` / `cell_type ^BM_` / `'sugar/water|labellar bristle'`. Print the group size and abort if it is 0.
- `--protocol` with `--gap-s` and `--ext-cycles`. Phases per cycle:
  - `forward`: [CS+&US T | rest R | CS− T | rest R]
  - `backward`: [US T | CS+ T | rest R | CS− T | rest R]
  - `unpaired`: [CS+ T | rest R | US T | rest R | CS− T | rest R]
  - `us-only`: [US T | rest R | CS− T | rest R]
  - `trace`: [CS+ T | gap G | US T | rest R | CS− T | rest R]
  - `extinction`: forward × cycles, then a mid-test (`mid_*` columns), then ext-cycles × [CS+ T | rest | CS− T | rest]
- The tag encodes every non-default argument, and a JSON sidecar records the arguments.
- The CSV schema is identical to `conditioning.py`.
- `--check-against`: the forward protocol at defaults must reproduce the paper file to the digit.

### 2.4 `experiments/edge/expression_harsh.py`

MBON sets and targets are built exactly as in `expression_probe.py` (REWARD/PUNISH_MBONS; targets with ≥ `--min-syn 10` synapses, excluding MBONs and KCs). Odour: vinegar at 150 Hz via `SensoryEncoder`, with presentations none / L / both.

Modes:
- `drive`: set MBONs at `--mbon-hz 0,20,50,100` × odour.
- `types`: MBON14, MBON11, MBON01 and MBON07 alone at 50 Hz.
- `bypass`: `sim.cut_edges(is ALPN, ~(KC | cell_class ^AL | olfactory))`, then MBONs intact, silenced (`scale_output(m, 0)`), or driven at 50 and 100 Hz. Log KC active % intact against bypassed to show the KC code is unchanged.
- `kick-nodn`: tonic 0/10/40 Hz on the targets minus descending neurons, MBONs intact or silenced.
- `structure` (no simulation): DNs reached within 1–3 hops of each set, with the signed synapse fraction.
- `sub` (P2):
  - `W_aug = vstack([hstack([W, 0]), hstack([S, 0])])`, where S is `n_src × N` with +1 on every non-descending target column.
  - `LIF(W_aug, LIFParams(w_syn=0.275*scale))`.
  - Sources at `--sub-rates`; keep rows where the targets fire 1–10 Hz with no odour and the MBONs silenced; report those calibration rows.

Call `sim.restore_weights()` between conditions. Outputs:
- `expression_harsh_<ds>_<variant>.csv`: one row per sim, with mode, set, type, bypass, mbons, mbon_hz, tonic_hz, odour, seed, active_frac, set-MBON Hz, targets Hz, DNa L/R, DNp09, MDN, GF, DNp13, DN all, set-DN-targets Hz.
- `_dn_types.csv`: long format, sim_id × DN type × Hz.
- `_structure.csv`.

### 2.5 `experiments/edge/odor_code_plus.py`

- Uses the `--variants` parser of `odor_code.py`.
- `--eln-subsets` adds variants a–f. They are built from `load(signs='known', eln_scale=1)`: row sign, then eLN = ALLN with positive row sign, split by `top_nt` into ach / mod (serotonin|dopamine|octopamine) / gg (gaba|glutamate) / other (print the counts). Each variant is `W = diags(scale) @ W`:
  - (a) all eLN ×0.25 (assert this equals `apply_model_options`)
  - (b) ACh only ×0.25
  - (c) non-ACh ×0.25
  - (d) mod ×0
  - (e) mod ×0 and ACh ×0.25
  - (f) gg-positive neurons flipped to −1
- `--hz` comma list (one load per variant); `--odors test10,glomeruli,library`:
  - `test10`: the 10 odours of `odor_code.py`
  - `glomeruli`: every `ORN_<g>` type
  - `library`: `SensoryEncoder.odor(cls, r_max=hz)`, bilateral, for each ODOR_LIBRARY class
- `--limit`, `--seeds`, `--ms 500`, `--out-dir`.
- Rows: all `odor_code.py` columns, plus `glomeruli_over_10hz_orn` computed only over glomeruli that have ORNs, and the cognate PN rate.
- Save KC active sets to an npz. Overlap CSV: KC Jaccard with NaN when both codes are empty (nanmean over seed pairs), a `live` flag (mean kc_active ≥ 0.005), and PN-vector cosine; summary rows for within and between, over all odours and over live ones only.
- Check: `known+eln0.25`, test10, 100 Hz, seeds 0–1 must equal the re-run `odor_code_flywire.csv` rows.

### 2.6 `experiments/edge/edge_report.py`

- `--frozen DIR`, pandas only, computes:
  - live-only Jaccard (Note 3)
  - CS− range, learning index and no-US per order, and the aversive increment over the matched no-US per order (Note 7)
  - world5 / world6 punishment index (probe JSONs)
  - state identity scope: cells differing by more than 1 Hz between lobes, split by input class (Note 6)
  - cVA and CO2 steering with 95 % CI (Note 9)
  - dt shifts in the sensitivity file (Note 1)
  - male other-odour cells at gain 1.4; P1 and aIPg at 1.4; pIP10 range
  - clean-box `hz_active_frac` and `hz_total_spikes` (the eye is active)
  - NPF against the unrelated-state band
- `--all` additionally evaluates every pass criterion in section 1 from `experiments/results_edge/*` against the re-run files. It fails loudly on any `.check.txt` mismatch or any failed digit check (seeds 0..k against paper files).
- Outputs: `EDGE_REPORT.md` and `edge_verdicts.csv` with columns step, claim, paper line, metric, value, threshold, verdict (KEEP / REWORD / CHANGE).

### 2.7 `experiments/edge/arena_audit.py` (log reads only)

Port the logic of the scratchpad prototypes `lean2.py`, `start2.py` and `stall.py`. That directory is session-scoped and may disappear.

Pairing of logs: fly1 with fly2 per trial label, starts within 10 s, as `figures.py` does.

1. `start_check`:
   - fly1 rows before fly2's first `t_wall`, fly1's displacement over them, and the distance at fly2's first non-NaN `near_dist`;
   - flag the trial if that distance is under 3 blocks and the first contact comes within 40 rows;
   - recompute trials with contact, contact %, and longest bout without the flagged trials;
   - fly1's `ctl_turn` and `hz_turn_L-R` before and after the partner appears (for the published lobe).
2. `lean_check` over the female logs of variant `specific`, pre-contact, `near_dist < 6`:
   - indices: raw; far-bias-corrected `mean((turn − b_far)·sign(az))`, where `b_far` is the mean `ctl_turn` over non-contact ticks with `near_dist ≥ 6`; all-tick-corrected; within-log side contrast (logs with at least 10 ticks per side);
   - sign tests per pairing with Holm correction over mf/ff; cluster sign tests by start configuration (t1–t5) and by series;
   - time-shift nulls: a circular shift of `near_az` within the pre-contact segment (offset uniform over 10–90 % of its length, 2,000 shifts, seed 0), and a whole-log shift;
   - the per-log lean against the sign of (mean turn × mean side).
3. `body_speed`: the wall-clock gap per row binned at 0.1/0.2/0.4/0.8/1.6/3.2 s, displacement per unit walk per bin, the share of rows with gaps over 0.8 s per log, and flags for logs with more than 5 % such rows or less than 60 s of brain time.

Outputs go to `--out-dir` (`start_check.csv`, `lean_check.csv`, `body_speed.csv`, `arena_audit.md`). `--quick` runs on one series.

### 2.8 `brain/tests/edge_brian2_reference.py` and `edge_brian2_divergence.py`

**Reference script.** A copy of `brian2_reference.py` plus:
- `--record-times`: a `SpikeMonitor(record=True)`, saving `spk_i_<s>` and `spk_step_<s> = round(t/ms/dt)` as int64;
- `--noise-hz`: `PoissonGroup(N)` connected to the neurons one-to-one with `v += w_syn*f_poi`;
- `--kick-mv`: a fixed kick size.

**Divergence script.**
- Arguments: `--conn`, `--ref`, `--dt`, `--seeds 0 1 2`, `--eps-v`, `--eps-g`, `--float64`, `--out` (JSON).
- Per seed:
  - build `LIF(W, LIFParams(dt, w_syn=0.275*scale, eps_v, eps_g))`; with `--float64`, cast `sim.v`, `sim.g` and `sim.buf` to float64;
  - pass 1 gets the counts; the record mask is every neuron active in either run; pass 2 runs `sim.run(1000, mask)`;
  - compare the sorted (step, neuron) lists, calibrating the step offset on seed 1;
  - report whether counts are identical, the first mismatch, and that neuron's kernel `v` over the 20 preceding steps. To get it, re-run deterministically to step−20, then step by one dt at a time.

### 2.9 P2 `brain/tests/edge_micro_semantics.py` and `edge_micro_semantics_brian2.py`

A shared JSON spec of scenarios, each at dt 0.1 and 0.2:
1. One neuron kicked at the steps spike + ref−1, spike + ref, spike + ref+1.
2. A→B with a subthreshold weight, timed to land on B's refractory edge.
3. An inhibitory synapse onto a kicked neuron.
4. Two arrivals and a kick in the same step.
5. A 30-neuron random recurrent net with one Poisson group, 1 s, seeds 0–4.

Kernel side: a timed kick is `set_drive([i],[1000/dt])` for one step. Brian2 side: `SpikeGeneratorGroup` with `on_pre v += 68.75*mV`. Both write (step, neuron) lists; `--compare` diffs them.

### 2.10 P3 `experiments/edge/decider_paths.py` (no simulation)

Specified in the deciders arm: hop counts, propagated signed weight (Wn = W / column |W| sum), Dijkstra on −log(Wn+), and per-decider input breakdown. The male part needs 4.5 GB.

## 3. Arena edge cases (all optional; need `./run.sh server`)

- **How to run them:**
  - Run only when the offline queues are finished, with memory_pressure showing at least 50 % free (ff) or 55 % (mf).
  - Use `NUMBA_NUM_THREADS=3` per brain.
  - Never run them inside run_guarded with pauses active: a SIGSTOP freezes the bots while the server keeps running, and the clients time out.
  - Always pass `--out` to `replication_stats.py` and never `--tex`.
  - `encounter_stats.py` rewrites `experiments/results/encounter_trials.csv`.
  - LABEL must not contain `_`.

| case | cost | memory | new code | tests |
|---|---|---|---|---|
| `sync-hum-ff`: `SYNC=1 SEED0=100 CONDS=ff NOISE=0.2 LABEL=sync-noise0.2 experiments/encounter_trials.sh 5 600` | 60 min | 5.5 GB | bot.js `--waitFor=<name>` (wait for the partner's entity, re-teleport, then start the timer, Observer and brain); run_pair.sh `${SYNC:+--waitFor=...}`; trials.sh `--seed $((SEED0+i))` and `SEED2` for fly2 | "met by chance and stayed together" without the launch-stagger artefact; ≥3/5 genuine meetings with ≥1 bout of 10 s or more |
| `offset-facing-approach`: `POS_SET='...' CONDS=mf NOISE=0 LABEL=offset-clean` | 32 min | 7 GB | trials.sh `POS_SET` override | "no approach": closest approach ≥1.4 blocks in the 4 offset starts |
| `rep2-clean-mf`: `CONDS=mf NOISE=0 LABEL=rep2-clean ... 5 300` | 32 min | 7 GB | none | the stalled replication (median wall gap 0.8 s) |
| `hum-level-ff` at 0.1 and 0.3 Hz | 65 min | 5.5 GB | none | whether "meet and stay" is specific to the 0.2 Hz hum |
| `male-male-hum` via trials.sh `DS1=DS2=malecns LABEL=mm-noise0.2 BRAIN_ARGS='--noise-hz 0.2' NO_FOOD=1` | 32 min | 9 GB | none | "nobody fought" in the pairing where real flies fight |
| `courting-male-virgin`: `CONDS=mf STATE1=courting STATE2=virgin NOISE=0.2` | 32 min | 7 GB | none | the virgin female with a male that actually sings |
| `world7` (bitter on ester, `NECTAR=none`) and `world6b` | 40 min each | 5 GB | none | an in-world aversive memory not explained by vinegar's own PPL1 drive; n=2 for 0.37 |
| `anosmic-female-arena` | 120 min | 6 GB | `run_brain --mask-smell` | whether the lean is geometric |

## 4. Wording that must change whatever the new runs show (paper/flycraft.tex)

1. **l.89 and Note 1 (l.137), "spike for spike … a single neuron tips":**
   - The third seed diverges from one event and ends with 284 of 592 active neurons at different counts (23,689 vs 23,512 spikes; r = 0.9999).
   - Tested only on the published model, sugar drive, dt 0.1, 1 s.
   - The lif.py docstring cites "micro-network scripts" that are not in `brain/tests`.
2. **Note 1, "results identical at 0.1–0.5 ms":** false.
   - Sugar→MN9 is 77.2 / 87.8 / 86.1 Hz; cVA→DNa L 10.0 / 7.5 / 7.8; in test_lif, PPL1 +10 % and KC +19 % at dt 0.5.
   - Write "qualitatively the same". Fix the same wording in the lif.py docstring, the `run_brain.py --dt` help and the long draft; test_lif's "AGREE" tolerance is about 45 %.
3. **Note 10:** name `NUMBA_NUM_THREADS=6`, and say the simulator uses min(threads, 8) chunks, so the "10-thread" run was 8 chunks.
4. **l.91 and Note 3:**
   - "the most that keeps smells apart": only ×1 / 0.5 / 0.25 / 0.1 were tested.
   - "150 cholinergic local neurons" should read "150 local neurons the sign rule makes excitatory"; only about half are predicted cholinergic.
   - The overlaps 0.63 / 0.08 count odours with empty KC codes; 3 of 10 test odours reach no KCs; over live odours the values are 0.76 / 0.16.
   - "18 %" is the mean of a bimodal set (6 odours at 23–28 %, 3 at 2–3 %).
5. **l.91, "I report every smell result both ways":** not true in the short paper (conditioning, the freeze, male cVA and the dose rows appear under one setting).
6. **l.91, "nothing that does not involve smell depends on the change":** holds only qualitatively at gain ≤1.0.
   - At 1.4 the published lobe is set off by touch and taste: touch→DNp13 19 vs 42 Hz, DNa L 27.5 vs 2; sugar→MN9 64 vs 94.
   - In the male, sugar→PPL1 differs already at gain 1.0.
7. **l.93 and Note 4, the freeze:**
   - "survives every one of my alternatives but one" was tested in 8 connectome variants ± the hum and at gains ≥1.0 only.
   - "carried by the weakest connections" should be "depends on", and the reversal was measured only on the Zenodo table.
8. **l.93 and Note 4, "no other smell at all" / "every other odour 0":** true for DNp13 only.
   - Other odours give MN9 1.3–2.8 Hz at gain 1.0.
   - At gain 1.4 they give PPL1 18–30, song MNs 5–10 and MDN 1–5 Hz.
   - Under the published lobe every odour drives MN9 at 19–22 Hz.
9. **l.93, "fails the gentlest version of my first test":**
   - Leg taste→MDN fails at both 0.7 and 1.4 (0 / 26.8 / 1.8 Hz).
   - Head touch→MDN fails at 0.7, is 0 at a 50 Hz stimulus, and depends on the odour context (2.8–46.8 Hz).
10. **l.93, Note 2 and Note 4, "Scramble the wiring and every one of these reflexes disappears" / "every readout 0–2 Hz in a rewired brain":**
    - This is true of the degree-preserving global null, which silences every input (DN-all ≤0.2 Hz even with 1,417 bristles driven).
    - Grooming, bitter suppression and song/wing MNs were never read in any rewired brain.
    - The class-preserving (block) null keeps JO-A→GF at 6.4 vs 10.6 Hz and raises touch→GF to 78 and MDN to 32. Name the null.
11. **Note 2, the three tests:** they are stated as a filter every reflex passes, but grooming (aBN1) and bitter suppression were never tested for gain, rewiring or sensitivity, and JO-A never appears in the sensitivity table (JO-B fails at 50 Hz and at ≥5 synapses). "Smell responses need 1.0 or more" is female only.
12. **Note 4, "wing motor neurons 10–22 Hz":** 11–22 Hz at the paper's gains (the 10 is gain 0.5), and not specific (wind 14, touch 10, cVA 12.6).
13. **l.95 and Note 5, deciders:**
    - "at every gain up to 1.4 and in all 14 conditions": the gain sweep lacks pC1b/c and oviDN and covers 14 inputs plus none; the sensitivity table has only cVA→pC1d/e and cVA→aIPg.
    - "Male P1 stays at or below 0.6 Hz" holds only at gain ≤1.0 (2.1–2.3 Hz at 1.4, 2.5 under the first-version numerics); male aIPg is 1.4–1.9 Hz at 1.4.
    - pIP10 is 2.3–3.7 Hz at gain 1.0.
14. **l.95 and l.125, "every neuron at rest"; l.123 and Note 11, "no eyes":**
    - The clean-box logs show about 41,000 spikes per 50-ms tick with 8 % of neurons active, all in the eye. DNs and KCs are at 0.
    - Write "an eye whose signal dies in the medulla".
    - The clean box is also not odourless: each female smells the other's Or47b at 0.10 and CO2 at 0.003.
15. **Note 5, "No sign rule steers towards food … under the published signs, a 16–29 Hz left turn whatever the odour":**
    - That file is Shiu signs ×0.25, not the published model.
    - Its steering component is +1.2 to +2.7 Hz towards food, hidden by the bias.
    - Zenodo gives vinegar +6.5 Hz at 150 Hz.
    - The bias is 0 for CO2 and the aversive odour at 25 Hz.
16. **l.97 and Note 6, "Hunger … changes nothing":**
    - NPF raises sugar→MN9 by +6.8 Hz, against +3.6 to +4.4 for unrelated states.
    - The stronger supporting fact is that hunger neurons recruit zero spikes at rest.
    - Say "in a silent brain" until S19 has run.
17. **Note 6, states:**
    - "vpoDN 5.7 Hz" is the pooled vpoEN+DNp37 readout.
    - "identical under both smell-centre settings" is true only for the state-alone rows (max 0.3 Hz).
    - "mated" is the no-state run.
    - Song MNs at 28 Hz are not state-specific (contact pheromone alone gives 21).
    - "one class" P1 is 148 neurons of 45 types.
    - In the published file at 100 Hz, pC1a–c lowers touch→DNp13 from 36 to 29 Hz.
18. **l.99 and Note 7, learning:**
    - The drive kept by the other odour is 0.59–0.70, the learning index 0.55 ± 0.03, and the no-teaching control 0.03 (n = 4, unbalanced 3+1).
    - "A tenth" is the floor constant w_min = 0.1, reached within the first pairing.
    - Punishment 0.21 ± 0.14 hides the odour order: the associative increment is +0.07 when vinegar is paired and +0.31 when ester is.
    - "0.29 with bitter" should be dropped: world6, with no bitter, gives 0.31.
    - Each in-world result is n = 1, and "the same happened in Minecraft" is weaker (0.29 of the drive kept, against 0.10 offline).
    - "Tully & Quinn" was not three 10-s cycles.
    - "0.0 Hz in every dopamine neuron" is female only (the male's labellar GRNs drive PPL1 at 11.7 Hz).
19. **Note 7 and l.99, expression:**
    - "No descending neuron changes with training" should be "no pairing-specific change" (DNa moves up to 7.5 Hz with or without the teaching signal).
    - "Reward output neurons, driven at 40 Hz, reach none": the probe drove their targets, not the MBONs, and silencing the reward MBONs shifts DNa by 4–5.5 Hz.
    - "Within 0.6 Hz" is true by construction, because those 28 DNs are themselves kicked.
    - "No working route … notebook that nobody downstream reads" contradicts 16f (MBON14 alone at 30 Hz drives DNa at 14 / 7 Hz and four DN types at 24–35 Hz).
    - "It walked and turned as before" rests on 14 / 8 ticks in world5, and world6 has no pre-training phase.
20. **l.101 and l.110, Note 8, Fig 3b and Table 1:**
    - The 86.2-s bout began at fly2's second tick, after fly1 had walked 4.5 blocks during the 6-s launch stagger in `run_pair.sh`. The same happened in faint-smell ff t1 and replication hum ff t1/t3; without these trials the longest real bout is about 26 s.
    - "Start 4 blocks apart" should be 4 or 5.7 blocks; 2 of the 5 starts face each other, and every clean male-female contact happened in those.
    - Both brains and every series share seeds 1–5 and the same start rotation, so the effective n for ff contact % is 5 pairs.
21. **l.101, "nobody sang or fought":** write "no song-command or aggression-neuron activity above the hum's floor". The male sing-act counter logs 20–25 acts a minute on the hum, and female lunges run at 2.9–5.0 a minute against a 2-a-minute floor.
22. **l.110 and Note 9, the lean:**
    - "24 of 33" should say 35 logs turn at all and 33 have a nonzero index.
    - After subtracting her own turning bias the split is 15 / 20 (p = 0.50), so drop the "one trace" sentence and "the size of the pull his pheromone has", which also compares a turn index with Hz.
    - "cVA … turns the female towards it by 0.6–2.3 Hz" leaves out −0.2 Hz at 100 Hz; n = 3, none significant, CO2 similar.
    - "she never walked towards him" should be "did not reliably" (the replication index is +0.040; the closest distance bin +0.16, p = 0.12).
23. **Note 10 and the author line:**
    - "One number changed" is wrong: the other odour's kept drive (0.66→0.70) and the learning index (0.54→0.55) also changed.
    - "A script checks 155 numbers … none differ" and "recomputes every number" do not hold:
      - `paper_numbers.py` compares against values hard-coded from the old draft;
      - its tolerance, max(0.55, 3 %), passes any number below 1;
      - it never checks the Note 1/3 counts, the Note 5 ranges, the Note 9 cVA range and sign test, or the file counts.
    - Tighten the tolerance to half a unit of the last printed digit and parse flycraft.tex, or reword.
    - The loaded replication (median wall gap 0.8 s) made bodies move 2–5× farther per brain-second, so it is not comparable.
24. **Note 11 and l.93 (what is mine):**
    - The body has built-in step-up and float reflexes (`REFLEXES` in bot.js, on by default).
    - The kick is fixed at 68.75 mV at every gain and in the male (Shiu's code scales it with w_syn).
    - The arena drives all 1,417 head bristles on both sides at 200 Hz on any contact.
25. **Missing citations:** "A real female walks away" (l.101) and "Real virgins wait for the male" (l.110).

**Machine notes.** One step at a time with the gates above. Swap was already 7.1 of 8 GB at 00:20: if swap stays above about 6.5 GB and memory is below 35 % free, hold the male steps (S20 and the P2 male steps). No arena run while any queue is active. To re-run a step, delete `logs/edge_done/<name>`. Step peaks go to `logs/edge/guarded_peaks.tsv`.