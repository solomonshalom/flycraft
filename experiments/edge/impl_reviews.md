

######## run_redirect (experiments/edge/run_redirect.py)
I reviewed `experiments/edge/run_redirect.py` and fixed four problems in it, none of which changes results. At default settings (no `--sim`) it matches a direct run of `social_probe` exactly, and `--sim dt=0.1` is printed and takes effect. It refuses `--res`, or any argument, inside `experiments/results/`, and nothing was written there (still 250 entries). It is now 132 lines, against about 60 in the spec.

**Bugs fixed** (all in `experiments/edge/run_redirect.py`, no other file changed):
1. **`--sim w_syn=…` was accepted.** It would have silently replaced the script's gain scaling and the male density scale in every sim, so a `gain_sweep` would have run every gain at one weight. It is now refused (exit 2) with a pointer to the script's `--gain`. It is not in the spec's key list either.
2. **A bad number in `--sim`** (e.g. `dt=abc`) crashed with a traceback. It now gives an argparse error (exit 2).
3. **Default runs recorded no LIF parameters.** The `LIF.__init__` wrapper now always records them for the sidecar. With no `--sim` it passes the script's own params object on untouched, so the default path is the same as a direct run (checked below). The default-run sidecar now has `lif_params` with dt 0.2, ref_steps 11, delay_steps 9.
4. **`files_under()` could crash in `finally`.** If a file vanished mid-walk, `os.stat` would raise and hide the target script's real error. It now skips such files.

**Checked, no problem found:**
- **Seeds and units:** the script touches neither; they stay in `run_trials` (seeds 0..n-1, rate = count / ms).
- **Wrapper:** its signature matches `LIF.__init__`, and it reaches `make_sim` and `shuffle_control`'s own `LIF(...)` through the same class.
- **Params object:** `dataclasses.replace` gives each sim its own copy. No experiment script keeps or changes its own `LIFParams`, so nothing leaks between conditions.
- **Memory:** no extra copies of W.
- **`common.RES`:** it is patched before `runpy`, and no module had already read it.
- **Inputs:** no target script reads its inputs from `RES`.
- **Threads and env:** unchanged; `numba_threads` 6 and the `FLYBRAIN_*` variables are recorded.
- **Refusals** (each exits 1, nothing created): `--res experiments/results/foo`, `--res experiments/results_edge/../results/foo`, `-- --out experiments/results/s.csv` and `--out=experiments/results/s.csv`, and `figures.py`, which sets its own RES at line 11.
- **Write guard:** a throwaway scratchpad script's `open("experiments/results/nonexist_dir_zz/x.csv","w")` raised `PermissionError: run_redirect: refusing to write into experiments/results/…`.
- **Overrides:** `--sim dt=0.1 t_ref=2.0 --sim delay=2.4 noise_hz=0.2 legacy=yes` reached both a `make_sim(gain=1.4, dt=0.5)` sim (which kept w_syn 0.385) and direct `LIF(...)` builds.

**Smoke runs after the fixes** (each alone, `FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25`, 6 threads, O=experiments/results_edge/_smoke/run_redirect):
- `experiments/edge/with_lock.sh python3 experiments/edge/run_redirect.py --res $O experiments/social_probe.py -- --seeds 1 --ms 100 --out $O/s_review.csv`
  - `run_redirect: LIF #1 with --sim {}: ... w_syn=0.275 dt=0.2 kick_mv=68.75 noise_hz=0 legacy=False ... ref_steps=11 delay_steps=9`
  - `run_redirect: ok, …; files written …: s_review.csv`
- `… --sim dt=0.1 experiments/social_probe.py -- --seeds 1 --ms 100 --out $O/s_dt0.1_review.csv`
  - `LIF #1 with --sim {'dt': 0.1}: ... dt=0.1 ... ref_steps=22 delay_steps=18`
- `… --sim dt=0.1 --sim t_ref=2.0 --sim delay=2.4 experiments/social_probe.py -- --dataset flywire --seeds 1 --ms 100 --out $O/s_rounded_review.csv`
  - `ref_steps=20 delay_steps=24`

**Digit check** (27×29 tables, `wall_s` dropped):

| Comparison | Result |
|---|---|
| `direct.csv` vs `s.csv` (first agent's run) | identical (max \|diff\| 0) |
| `direct.csv` vs `s_review.csv` (after fixes) | identical |
| `s_dt0.1.csv` (before fixes) vs `s_dt0.1_review.csv` (after) | identical |
| `direct.csv` vs `s_dt0.1_review.csv` | 133 cells in 26 rows differ; only the "none" row matches |

**Remaining risks:**
- **`--sim` overrides every LIF a script builds.** `noise_hz` would merge the deliberate noise-free and noisy sims in `contact_stop`, `noise_floor` and `precontact_dose`. `dt` would merge `sensitivity`'s dt conditions, and its `dt` column would still show its own labels. None of the planned `--sim` uses (`social_probe` with dt/t_ref/delay, `state_probe` with noise_hz) are affected. The sidecar records the values each LIF actually got.
- **The argument guard also refuses read-only inputs under `experiments/results/`** (e.g. a `--check-against` file). None of the planned `$R` commands pass one.
- **The write guard only covers `open()`**, not `os.replace`, memmap or C-level writers. The target scripts write through pandas `to_csv`, which goes through `open()`.
- **Minor:**
  - The sidecar name has one-second resolution; two runs into the same DIR within a second would share it. Every run takes at least 4 s.
  - `RES` rebound by attribute or tuple assignment escapes the check on the script's source, but its writes still hit the `open()` guard.

**Queue command lines** (from project root, with the [H] prefix, [P] where the plan says so):
- **S1 smoke:** `python3 $R --res $O experiments/social_probe.py -- --seeds 1 --ms 100 --out $O/s.csv`
- **dt sweep:** `for dt in 0.1 0.5; do python3 $R --res $O --sim dt=$dt experiments/social_probe.py -- --dataset flywire --seeds 10 --out $O/social_dt$dt.csv; done`
- **dt-rounding-control:** `python3 $R --res $O --sim dt=0.1 --sim t_ref=2.0 --sim delay=2.4 experiments/social_probe.py -- --dataset flywire --seeds 10 --out $O/social_dt0.1_rounded.csv`
- **State gain:** `for g in 0.7 1.4; do python3 $R --res $O/gain$g experiments/state_probe.py -- --dataset flywire --seeds 5 --gain $g; done`
- **State 10 seeds:** `python3 $R --res $O experiments/state_probe.py -- --dataset flywire --seeds 10`
- **State on the hum:** `python3 $R --res $O --sim noise_hz=0.2 experiments/state_probe.py -- --dataset flywire --seeds 5`
- **state-dose-female:** `python3 $R --res $O/s100 experiments/state_probe.py -- --dataset flywire --seeds 5 --state-hz 100; for h in 10 20 60; do python3 $R --res $O/s$h experiments/state_probe.py -- --dataset flywire --seeds 3 --state-hz $h; done`
- **Odor dose:** `python3 $R --res $O experiments/odor_dose.py -- --dataset flywire --seeds 10 --rates 50 75 100 125 150`
- **Odor dose at gain 1.4:** `python3 $R --res $O experiments/odor_dose.py -- --dataset flywire --seeds 5 --gain 1.4 --rates 50 100 150`
- **Conditioning, 10 cycles** (the other pairs, `--eta 1.0 --tag eta1.0`, and the male no-US step use the same form): `for o in 'vinegar ester' 'ester vinegar'; do set -- $o; for us in 'dan --valence reward' 'wiring'; do python3 $R --res $O experiments/conditioning.py -- --dataset flywire --signs known --eln 0.25 --us $us --cycles 10 --csp $1 --csm $2 --seed 0 --tag cyc10; done; done`
  - The male step runs under `MIN_FREE=45` / gate 35.

**Deviations from spec 2.1:** I kept the first agent's four deviations:
- Overrides go inside `LIF.__init__` rather than replacing `make_sim`, so they also reach `shuffle_control`'s own `LIF(...)`.
- `--sim` takes any LIFParams field except `w_syn` (my change).
- Extra refusals and the `open()` guard.
- The length.

I added one: effective params are printed and recorded even without `--sim`.

Smoke outputs in `experiments/results_edge/_smoke/run_redirect/` can all be deleted: `direct.csv`, `s.csv`, `s_dt0.1.csv`, `s_review.csv`, `s_dt0.1_review.csv`, `s_rounded_review.csv` and five `_redirect_social_probe_*.json`.


######## grid_probe (experiments/edge/grid_probe.py)
I reviewed `grid_probe.py` line by line against the spec, DECISIONS.md and the scripts it copies. It holds up where it matters: at default settings it reproduces the paper's files to the digit. I found one real bug that would have blocked S10, plus five smaller problems, and fixed all of them in that file only. Every re-run check reports 0 mismatches.

**What I checked and found correct**
- **Engine vs `run_trials`:** same seeds 0..n-1, same call order, same `LIFParams` and `w_syn` expression, same drive concatenation, rate formula and `n_driven`.
- **Simulator reuse:** one simulator is shared only within the same (dt, t_ref, delay, legacy), because the LIF fixes those at construction. The fields a condition changes are read on every run.
- **No leaks between drives or seeds:** noise is restored after every seed, and the drive is set again every seed. `scale_output` and `cut_edges` are never used.
- **Units:** rates are Hz over the bin or window length. Bin lengths must be whole multiples of dt. The mean-field estimate is `w_syn × 0.005 s × (E−I)`.
- **Rewire and min_syn_mem:** rewiring is identical to `shuffle_control`, and `min_syn_mem` thresholding is correct.
- **Output paths:** every output goes through `safe_out`, and nothing writes into `experiments/results/`. There is no N×N dense matrix.

**Bugs found and fixed**
1. **False mismatch that would block S10 (confirmed by running it).** S10 is planned with `--anchors`. The anchor drive `sound (JO-B)@100` repeats the `all` drive `sound (JO-B)`, so the sensitivity check took the seed SD over 6 duplicated rows. On baseline plus 50 Hz it reported `sound (JO-B) -> GF jump sd: 1.13855 vs 1.27294` (ratio exactly √(4/5)). The full S10 would hit this in every 100 Hz condition. Fix: each (drive, seed) is counted once. The same run now gives 104 cells, 0 mismatches.
2. **Per-seed checks compared rows the reference never ran.** Rows at another gain, variant, noise, dt/eps/kick or protocol were counted as mismatches; for example `--ei … --gains 1,1.4` would fail on its gain-1.4 rows. Now only rows run under the reference's model are compared, and the rest are listed as "not comparable".
   - The model's variant, gain and noise come from the file name, or from two new options, `--check-gain` and `--check-noise`.
   - A "WARNING: no cell was compared" line appears if nothing matched.
   - The sensitivity branch applies the same filter, which also drops settle-protocol rows.
3. **An unsupported `--check-against` file crashed only after the whole simulation.** A contact_stop file, for example, died on a missing `input` column and lost the sidecar. The file is now checked before any simulation.
4. **A preset that gives no drives on a dataset silently ran all inputs instead.** It now exits with a message.
5. **The previous connectome's W stayed in memory during the next connectome's load.** The loop variable kept it alive. W is now freed after each wiring (and the `--ei` column slice with it), which matters for multi-connectome runs like S13 and the male runs.
6. **Small guards:**
   - `min_syn_mem` now checks that the min-1 (and min-5) cache exists before loading, so nothing can be built into `data/`.
   - Duplicate conditions are now recognised by label too, so two sensitivity labels that resolve to the same model both stay checkable.
   - The `decider_reach` docstring now says the decider's own type is excluded and that whole types are driven.

**Smoke re-runs after the fixes** (with_lock.sh, female, `FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25`, outputs in `experiments/results_edge/_smoke/grid_probe_review/`)
- **Digit check:** `--drives all --preset state_split --seeds 2 --ms 1000 --check-against …social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv` gave `60 rows compared (1620 cells), 0 mismatches`. The same CSV checked offline against `state_probe_…_state30.csv` gave `36 rows (828 cells), 0 mismatches`, including all 12 rows with SAG or pC1a-c driven at 30 Hz.
- **Sensitivity check, 2 of the 14 conditions** (scratch wrapper, `--anchors`, 3 seeds, 600 ms): 1 mismatch before the fix, 0 after.
- **`--ei`:** `--ei deciders --drives 'cVA + touch' --gains 1,1.4 --seeds 1 --ms 1000 --check-against social_probe…` gave gain 1 at 27 cells, 0 mismatches, and gain 1.4 as "1 rows not comparable (gain 1.4)". It wrote 90 neuron rows; measured voltage agrees with the mean-field estimate (pC1d 3.69 vs 3.80 mV).
- **k=5:** `--cond min_syn_mem=5,conn=shiu` printed `k=5 sanity: 2700429 … vs 2700429 … -> PASS (arrays identical: True)`.
- **Offline checker tests (no simulation):** the earlier smoke files still give 0 mismatches for social_probe (1458 cells) and the rewire run (38 cells). A planted 1e-6 error is still caught. A file of another variant gives 0 compared plus the warning.
- **Not re-run:** rewire. Only the memory release after it changed.

**Remaining risks**
- **Freeze random sensory sets are about 75 % photoreceptors.** That follows the spec literally, but it is a weak specificity control.
- **`decider_reach` drives whole types**, some of them mixed-sign; for example AN_SMP_1 has 1 excitatory and 4 inhibitory neurons.
- **The IPC matched null** draws from a pool of only 62 neurons.
- **Anchor rates are fixed.** Their explicit `@100` rates do not follow the sensitivity conditions at 50 and 150 Hz.
- **The sensitivity branch** compares the first copy of a duplicated drive only. The per-seed branch still compares every copy.
- **Not tested:** the male paths (male `min_syn_mem` keeps the min-1 `w_syn_scale`) and the full 14-condition S10.
- **Persistence off-phase bins** are 4 × 50 ms, then 1000, 1000 and 800 ms.
- **Result, not a bug:** after cVA, food, pheromones + song + touch, Or47b + CO2 and the 0.2 Hz hum, about 50,000 neurons are still active 500 ms after offset. S9 will say whether this lasts to the end of the 3-s off phase.

**Commands for the queue** (the plan's [H][P] prefix; `G=experiments/edge/grid_probe.py`; `R=experiments/results`)
- S1: `python3 $G --dataset flywire --drives 'none;sugar GRNs' --seeds 1 --ms 100 --out $O/smoke_grid.csv`
- S9: `python3 $G --dataset flywire --preset persistence --seeds 2 --out $O/persistence_g1.csv`
- S10: `python3 $G --dataset flywire --conditions sensitivity --drives all --anchors --seeds 3 --ms 600 --out $O/sensmap_flywire.csv --check-against $R/sensitivity_flywire_shiu_min1+known+eln0.25.csv`
- S11:
  - `python3 $G --dataset flywire --drives all --gains 0.7,1.4 --seeds 3 --ms 1000 --out $O/map_gain.csv`
  - `python3 $G --dataset flywire --drives all --cond hz=200 --cond hz=300 --seeds 3 --ms 600 --out $O/map_rate.csv`
- S12:
  - `python3 $G --dataset flywire --preset anchors --gains 0.7,0.8,0.9,1.0,1.2,1.4 --seeds 10 --ms 1000 --out $O/anchors_gain.csv`
  - `python3 $G --dataset flywire --preset anchors_rate --seeds 5 --ms 1000 --out $O/anchors_rate.csv`
- S13 (also runs the DECISIONS 7 freeze controls): `python3 $G --dataset flywire --preset freeze --cond conn=shiu,min_syn_mem=1 --cond conn=shiu,min_syn_mem=2 --cond conn=shiu,min_syn_mem=3 --cond conn=shiu,min_syn_mem=5 --cond conn=zenodo,min_syn_mem=1 --cond conn=zenodo,min_syn_mem=2 --cond conn=zenodo,min_syn_mem=3 --cond conn=zenodo,min_syn_mem=5 --seeds 5 --ms 600 --out $O/minsyn.csv`
- S14:
  - `python3 $G --dataset flywire --preset touch_dose --seeds 5 --ms 600 --out $O/touch_dose.csv`
  - `python3 $G --dataset flywire --drives 'food odor@100;food odor@100 & touch (all head bristles)@200' --protocol bins --on-ms 5000 --bin-ms 1000 --off-ms 0 --seeds 5 --out $O/touch_5s.csv`
- S15 (gate 35): `python3 $G --dataset flywire --drives all --anchors --preset states_lite --cond rewire=block,shuffle=0 --cond rewire=block,shuffle=1 --cond rewire=global,shuffle=0 --seeds 3 --ms 800 --out $O/block_flywire_paper.csv --check-against $R/shuffle_flywire_shiu_min1+known+eln0.25_global.csv`
- S16: `python3 $G --dataset flywire --preset state_split --seeds 10 --ms 1000 --out $O/state_split.csv --check-against $R/state_probe_flywire_shiu_min1+known+eln0.25_state30.csv`
- DECISIONS 6, P1:
  - `python3 $G --dataset flywire --ei deciders --drives 'cVA (Or67d/DA1);song/sound (JO-A);touch (all head bristles);cVA + touch' --gains 1,1.4 --seeds 3 --ms 1000 --out $O/ei_deciders.csv --check-against $R/social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv`
  - `python3 $G --dataset flywire --preset decider_reach --seeds 3 --ms 1000 --out $O/decider_reach.csv`
  - `python3 $G --dataset flywire --preset matched_null --seeds 3 --ms 1000 --out $O/matched_f.csv`
- S20 (gate 35): `python3 $G --dataset malecns --preset matched_null --seeds 3 --ms 1000 --out $O/matched_null_male.csv`
- P2:
  - `python3 $G --dataset malecns --conditions sensitivity --drives all --seeds 3 --ms 600 --out $O/sensmap_malecns.csv --check-against $R/sensitivity_malecns_all_min1+eln0.25.csv`
  - `python3 $G --dataset malecns --drives all --gains 0.7,1.4 --seeds 3 --ms 1000 --out $O/map_gain_male.csv`
  - `python3 $G --dataset malecns --drives all --preset states_lite --cond rewire=global,shuffle=0 --seeds 3 --ms 800 --out $O/global_male.csv --check-against $R/shuffle_malecns_all_min1+eln0.25_global.csv`
  - `python3 $G --dataset flywire --preset sag_hunger --seeds 10 --ms 1000 --out $O/sag_hunger.csv`
  - `python3 $G --dataset malecns --preset touch_dose_male --seeds 3 --ms 600 --out $O/touch_dose_male.csv`

**Deviations from the spec**
- The two new options, `--check-gain` and `--check-noise`, exist so a reference whose file name carries no gain tag (such as a state_probe run at gain 0.7) can still be checked.
- An empty preset now exits instead of running all inputs.
- Everything else follows the original author's stated deviations, which I kept: freeze pool also excludes the food-odor neurons, one draw at 100 % touch, `gradient` not implemented, the DECISIONS 5 persistence checks with a 0.5 Hz floor.

The smoke outputs in `_smoke/grid_probe_review/` can be deleted. The scratch wrapper is `(scratch, not kept)`.

The script is at `experiments/edge/grid_probe.py`.


######## conditioning_edge (experiments/edge/conditioning_edge.py)
I reviewed `experiments/edge/conditioning_edge.py` and changed only that file. The simulation core is correct: it is conditioning.py's, call for call. After my fixes the forward run at default arguments still reproduces the paper's CSV and `_compartments.csv` byte for byte.

**Checked and correct (no change needed)**
- **Training loop:** 50-ms ticks, `pl.update(counts, 0.05)`, `us_drive(0,0)` outside US phases, and the same `cat` drives. `set_drive` sorts its indices, so drive order cannot matter.
- **Tests:** seeds `seed` and `seed+100` with a reset each time, the same readout group order, and pre-test / post-test runs with learning frozen.
- **PlasticityConfig:** `tau_rec=0`. `w_min 0.1` and `tau_elig 1.0` equal its defaults, so passing them changes nothing.
- **Isolation:** one condition per process, so no drive, weight or noise state can leak between conditions. No N x N arrays.
- **Outputs:** everything goes through `safe_out`. Units are consistent (ms passed to `sim.run`, s passed to `update`, Hz = counts / s).

**Bugs found and fixed**
1. **Taste-US tag.** A non-default `--valence` was left out of the tag for `--us wiring`. The spec says the tag encodes every non-default argument, and the taste-US arm scores bitter/touch on the punishment compartment. A paper_numbers-style parser (`'punish' in key`) would have scored those runs on the reward compartment. Reward and punish runs also overwrote each other's sidecar. The tag is now `us-wiring[-<group>]-punish`, and names at default arguments are unchanged.
2. **Missing `--check-against` file.** It crashed only after the full run, with a nonzero exit, so run_guarded would retry the whole run and fail again. It is now refused before the connectome loads.
3. **`at_defaults` label.** It ignored `--wiring-us`, so a bitter run was labelled "at defaults". It also counted `--tag`, which changes no number. It now means "the simulation is conditioning.py's".
4. **No skip-existing (DECISIONS item 3).** S24 loops over 9 runs under `set -e`, so a late failure repeated every run on retry. I added `--skip-existing`: it exits 0 after the connectome load and before any simulation, when the CSVs, the sidecar (written last) and, with a check, the `.check.txt` all exist.
5. **DAN rate for the taste-US pass criterion.** The printed per-phase DAN rate is from the last 50-ms tick only, too noisy for "within 1 Hz of the CS- phase". The sidecar now has `phase_stats` with whole-phase means: all DANs, PAM, PPL1, the US DAN sets, the synapse-weighted DAN rate onto the reward and punishment compartments, KC rate and weight fractions. These are read from `counts` only. A summary table is printed after training; the per-tick log lines are left as conditioning.py prints them.
6. **Small guards and records.** `--test-s <= 0` and negative cycle counts are now rejected. The reference file's modification time goes into the `.check.txt` and the sidecar, so edge_report can apply the DECISIONS item 2 rule (files must postdate 2026-09-26 23:44).

**Smoke tests after the fixes** (all through `with_lock.sh`, female connectome, 6 threads; outputs in `experiments/results_edge/_smoke/conditioning_edge/`, which can be deleted):
- **Forward, full run, with the digit check:** `with_lock.sh python3 experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --us dan --valence reward --csp vinegar --csm ester --seed 0 --out-dir experiments/results_edge/_smoke/conditioning_edge --check-against experiments/results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_vinegar-vs-ester_seed0.csv`. It took 2:16 including the load (88 s of simulation).
  - `RESULT: ... -2.4 Hz (reward-compartment MBONs -5.6 Hz); approach ... +12.0 Hz; KC->MBON weights retained 0.950`
  - `...seed0.csv vs ...: PASS; 80 cells compared, 0 differ, max |diff| 0; byte-identical yes`
  - `..._compartments.csv vs ...: PASS; 35 cells compared, 0 differ, max |diff| 0; byte-identical yes`
  - `CHECK: PASS (to the digit: yes)`
  - The whole-phase means: during CS+ & US, PAM 22.0 Hz, reward DANs 45.0 Hz, PPL1 13.4 Hz. During CS- alone, PPL1 is about 8.2 Hz.
- **Backward, short:** `... --us dan --valence reward --protocol backward --cycles 1 --train-s 1 --rest-s 1 --test-s 0.2` exits 0 in 19 s. `LEARNING INDEX [post] (backward, taught = reward-comp): +0.035 (CS+ 0.958, CS- 0.993)`, the same as the author's run.
- **Bitter as the US, short:** `... --us wiring --wiring-us bitter --valence punish` (same short phases) exits 0. The bitter group is 65 neurons. The tag is `..._us-wiring-bitter-punish_..._cyc1_train1s_rest1s_test0.2s_seed0`. `LEARNING INDEX [post] (forward, taught = punish-comp): +0.238`.
- **`--skip-existing`** on the finished backward run printed "nothing run" and exited 0.
- **Short run with a check that should fail:** it wrote `CHECK: FAIL` with the reference time `modified 2026-09-26 00:23:07` and exited 0, as the plan's convention requires.
- **Guards, no connectome loaded:** a missing check file, an `--out-dir` under experiments/results/ (no directory created), `--test-s 0` and `--gap-s 0.33` are all refused.

**Remaining risks**
- The reference CSV was written 26 Sep 00:23; the re-run has not reached the conditioning group yet. S24's check is only meaningful after S0, and edge_report should require the reference time recorded in the `.check.txt` to be at or after 2026-09-26 23:44.
- The male paths (`--dataset malecns`, `--wiring-us labellar`) are not smoke-tested, because the rules forbid loading the male connectome. Male `--us wiring` with the default sugar group aborts if the group is empty in MaleCNS; that is intended.
- Offline `tau_rec` is 0, so extinction cannot recover the CS+ by construction; the protocol only documents that.
- The taste-US DAN criterion should be read from the sidecar's `phase_stats`, not from the per-tick log lines.
- In zsh, an unquoted `$C` does not split into words. The queue runs its steps through `bash -c`, so its commands are unaffected.

**Queue command lines** (run as `bash -c` from the project root, pyenv python3, `NUMBA_NUM_THREADS=6`):
- **S1 smoke (gate 25):** `python3 experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --us dan --valence reward --csp vinegar --csm ester --seed 0 --protocol backward --cycles 1 --train-s 1 --rest-s 1 --test-s 0.2 --out-dir $O`
- **S24 `cond-contingency` (gate 25):**
  ```
  set -e; O=experiments/results_edge/cond-contingency; mkdir -p $O
  C="python3 experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --us dan --seed 0 --out-dir $O --skip-existing"
  $C --valence reward --protocol forward --csp vinegar --csm ester --check-against experiments/results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_vinegar-vs-ester_seed0.csv
  for o in 'vinegar ester' 'ester vinegar'; do set -- $o
    for p in backward unpaired us-only; do $C --valence reward --protocol $p --csp $1 --csm $2; done
    $C --valence punish --protocol backward --csp $1 --csm $2
  done
  ```
- **Optional P3 arms:** define `C0="python3 experiments/edge/conditioning_edge.py --dataset flywire --signs known --eln 0.25 --seed 0 --out-dir $O --skip-existing"`, and `C` as `C0` plus `--us dan --valence reward`.
  - Taste as the US: `for w in bitter touch; do $C0 --us wiring --wiring-us $w --valence punish --csp $1 --csm $2; done`
  - Male taste US (gate 35, male rules): `python3 experiments/edge/conditioning_edge.py --dataset malecns --eln 0.25 --us wiring --wiring-us labellar --valence punish --csp $1 --csm $2 --seed 0 --out-dir $O --skip-existing`
  - Floor and eligibility: `for x in '--w-min 0' '--w-min 0.3' '--tau-elig 0.2' '--tau-elig 3'; do $C --csp $1 --csm $2 $x; done`
  - Extinction and trace: `$C --protocol extinction --ext-cycles 3 --csp vinegar --csm ester; for g in 0.5 1 3; do $C --protocol trace --gap-s $g --csp vinegar --csm ester; done`

**Deviations from the spec**
- **Kept from the author:** exit 0 with `CHECK: PASS|FAIL`, which the plan's convention for `--check-against` requires; strict phase lengths (multiples of the 50-ms tick); the abort on an empty `--wiring-us` group only when `--us wiring` is used; the extinction `mid_*` columns appended after the four standard ones.
- **Added in this review:** `-punish` in the tag for `--us wiring`, `--skip-existing`, `phase_stats` in the sidecar, and the reference file time in the check.


######## expression_harsh (experiments/edge/expression_harsh.py)
I found no bug that makes the script's results differ from `reproduce.sh` at default settings. The digit check now passes: 24 rows × 21 columns against the paper's `expression_probe` file, max |diff| 0. I edited only `experiments/edge/expression_harsh.py` (now 395 lines) and fixed four smaller problems. Two remaining risks change the queue commands.

**Checked and correct:**
- Neuron selection matches `expression_probe`: same sets, targets and DN targets (435 / 1024 targets, 0 / 28 DNs).
- Drive arrays are identical at 0 Hz, and for the reward set in kick-nodn at any tonic rate.
- Seeds run 0..n−1 with seed, reset and set_drive before every run. Hz is counts / n / (ms/1000).
- Weights are restored before every condition and after every mode. `noise_hz` is never changed.
- Nothing can be written into `experiments/results/`. There are no dense N×N matrices; the extra network for `sub` is sparse, built once per set and freed.

**Bugs fixed:**
1. **A missing `--check-against` file crashed only after the whole run**, after the main CSV was already written. With one retry, the queue would have re-run everything. It now fails at startup.
2. **The check was weak.** It compared only 0-Hz rows. It now also compares bypass-off intact rows, and reward kick-nodn rows at every tonic rate the paper's file has (the reward set has no DN targets, so these are the same simulation as the paper's). Tonic rate is now part of the match key. At queue defaults this checks about 90 rows, including real tonic drive.
3. **The reference CSV was read with pandas' default float parser**, which is off by one unit in the last place. That gave max |diff| 2.2e-16 instead of 0. It is now read exactly.
4. **`signed_frac` in `_structure.csv` meant two different things.** Layer rows divided by E+I, DN rows by the DN's total input. `signed_frac` is now (E−I)/(E+I) for both. A new column, `signed_of_input`, is (E−I) over total input for both. `edge_report.py` does not exist yet, so nothing reads the old meaning.

Also: a notice is printed when `--check-against` is given but no simulation mode runs, and the docstring and help text are updated.

**Smoke runs** (all `FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 experiments/edge/with_lock.sh python3 experiments/edge/expression_harsh.py --dataset flywire --out-dir experiments/results_edge/_smoke/expression_harsh ...`):
- **Digit check:** `--modes drive,kick-nodn --mbon-hz 0 --tonic 0,10 --seeds 1 --ms 1000 --tag check --check-against experiments/results/expression_probe_flywire_shiu_min1+known+eln0.25.csv`. I ran it at 1000 ms because the task asked for the digit check, and it only matches at the paper's 1000 ms; it took 23 s.
  - `check-against ...: 24 rows (of 24 comparable rows; tonic [0.0, 10.0]; ref rows 180) x 21 columns, 0 mismatched cells (max |diff| 0) -> MATCH TO THE DIGIT`
  - `[self-check] 6 ... groups ... max |diff| 0 over 24 columns -> IDENTICAL`
- **All six modes, 200 ms:** `--modes drive,types,bypass,kick-nodn,structure,sub --hops 2 --mbon-hz 0,50 --tonic 0,10 --bypass-hz 50 --sub-rates 100,115,130 --seeds 1 --ms 200 --tag all --check-against ...`
  - Exit 0, 108 sims, self-check IDENTICAL.
  - Hop 1 matches expression_probe's targets. Hop 2 reaches 90 DNs (reward) and 399 DNs (punish).
  - The check reports MISMATCH, as expected at 200 ms.
- I deleted the old `_td` and `_rest` outputs, which came from the earlier version of the script. The `_check` and `_all` outputs remain; the sidecar's script hash matches the final file.

**Remaining risks:**
1. **The bypass does change the Kenyon-cell code.** The spec says the bypass should leave it unchanged, but it doesn't. With vinegar on both antennae (300 ms, seed 0), KCs active rise from 4.54 % to 7.71 %. The cut also removes ALPN input to APL (|W| 3,648), dopamine neurons (4,187) and MBONs (1,393). Keeping APL gives 6.63 %; keeping APL, DPM, MBONs and dopamine neurons gives 5.08 %. More KC drive favours finding a mushroom-body route, so a null result is conservative. A positive result, though, could partly come from the cut itself. Other antennal-lobe exits stay uncut (ALLN, ALIN, ALON, ORNs: |W| about 43.9 k, against 678.5 k cut). I left the spec's cut unchanged.
2. **`--sub-rates 50,100,150` calibrates nothing.** Non-DN targets fire 0 Hz at 100 Hz sources, 5.0 Hz at 115 (both sets, so calibrated) and 11–15 Hz at 130 (200 ms, 1 seed). The P2 step needs a finer grid around 115 Hz.
3. **Punishment-set kick-nodn at tonic above 0 cannot be digit-checked.** It leaves the DN targets unkicked on purpose, so it differs from the paper's rows by design.
4. **The check exits 0 either way.** The queue must read `<main>.check.txt` or the sidecar's `check` field. The reference file is dated 26 Sep 01:07 and the re-run queue may rewrite it; the check compares with whatever is there.
5. **The MBON14 claim in RESEARCH_NOTES 16f was made under an older model.** Here MBON14 alone at 50 Hz with no odour gives DNa L 2.5 Hz (200 ms, 1 seed), against 16f's 14 Hz at 30 Hz. Treat 16f's numbers as not comparable.
6. **Runtime estimate:** the default S26 run is 306 one-second sims, about 5–6 minutes including the 3-hop structure pass.

**Queue commands** ([H] and [P] prefixes as in `design_plan.md`):
- **S1:** `export FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25; python3 experiments/edge/expression_harsh.py --dataset flywire --modes structure --out-dir $O`
- **S26:** `[H][P] python3 experiments/edge/expression_harsh.py --dataset flywire --modes drive,types,bypass,kick-nodn,structure --seeds 3 --out-dir $O --check-against experiments/results/expression_probe_flywire_shiu_min1+known+eln0.25.csv`
- **P2 expression-subthreshold:** `[H][P] python3 experiments/edge/expression_harsh.py --dataset flywire --modes sub --sub-rates 105,110,115,120,125 --n-src 50 --seeds 3 --out-dir $O --tag sub`

Files are in `experiments/results_edge/_smoke/expression_harsh/`:
- `expression_harsh_flywire_shiu_min1+known+eln0.25_check.check.txt`
- `expression_harsh_flywire_shiu_min1+known+eln0.25_check.json`
- `expression_harsh_flywire_shiu_min1+known+eln0.25_all.csv`
- `expression_harsh_flywire_shiu_min1+known+eln0.25_all_structure.csv`
- `expression_harsh_flywire_shiu_min1+known+eln0.25_all.json`


######## odor_code_plus (experiments/edge/odor_code_plus.py)
I found and fixed four bugs and hardened three more spots, all in `experiments/edge/odor_code_plus.py`. After the last edit the digit check is still identical: 20 rows, 21 columns, 55 overlap pairs, no cell differs.

**Bugs found and fixed**
1. **VM6 was dropped as a glomerulus.** The PN name pattern gives 51 PN groups that receive ORNs, not 50: ORN_VM6l, VM6m and VM6v all feed the PN group VM6 (VM6_adPN). The old code left VM6 out of `glomeruli_over_10hz_orn`, so the denominator was 50. It also gave NaN for the matching-glomerulus PN rate (`pn_cognate_hz`) and for `pn_driven_hz` on those three glomeruli. A new `PN_OF` map fixes this. VM6l/m/v now read 100/110/120 Hz and `n_glomeruli_orn` is 51. test10 rows work exactly as in `odor_code.py`.
2. **eLN rates were not comparable across subsets.** `eln_hz` and `iln_hz` use each model's own row signs. Scaling a neuron's output to ×0 removes its row, so in (d) and (e) the 52 modulatory eLNs dropped out of `eln_hz`, and in (f) the flipped GABA/glutamate eLNs moved into `iln_hz`. I added `eln_fixed_hz` and `eln_{ach,mod,gg,other}_hz`, taken over the fixed set of 150 eLNs, in every model; the progress line shows them too. These columns explain why (d) and (e) come out identical to the digit: the cholinergic eLNs fire at 0.0 Hz once the modulatory eLNs' output is removed, so scaling them by 0.25 changes nothing. This is a model result, not a code bug.
3. **The (a) equality check ran too late.** It ran after all the plain variants, so a failure threw away that work. It now runs before any simulation. The raw weight matrix is also released before the subset runs (`raw.select` kept it alive after `del raw`).
4. **A retry could turn a failed check into a pass.** With `--skip-existing` and `--strict`, a retry skipped the run and exited 0 after the first run had exited 3. Now it only skips when all four outputs exist, including the JSON sidecar, which is written last. It re-exits 3 if the stored check said DIFFERS. It refuses to skip if the stored variants, seeds, ms, limit or subsets differ, because the output file name does not include the variants.

**Hardening**
- The check now counts a reference row the run should have produced but didn't as a difference (not applied under `--limit`), and records the reference file's time (26 Sep 23:47).
- A crash inside the check is caught, recorded as `DIFFERS (check failed…)`, and the sidecar is still written.
- The sidecar stores `limit`, and the transmitter counts as integers rather than strings.

**Smoke runs after the fixes** (all through `with_lock.sh`, female connectome; peak memory about 1.1 GB with subsets)
1. `--dataset flywire --variants known+eln0.25 --seeds 2 --strict` → `CHECK vs odor_code_flywire.csv: IDENTICAL (20 rows x 21 columns, variants known+eln0.25, seeds [0, 1], 10 odours; 0 cells differ, max |diff| 0; overlap 55 pairs, 0 differ)`
2. `--variants shiu,known,known+eln0.5,known+eln0.1 --eln-subsets --limit 1 --seeds 1` (500 ms) → `(a) W == apply_model_options(known, eln 0.25): identical (15090883 connections, 150 eLNs)`; `CHECK: IDENTICAL (4 rows, variants known,known+eln0.1,known+eln0.5,shiu, seed 0)`. So the plain `shiu` and eLN ×1 paths also match the paper file.
3. `--limit 1 --eln-subsets --seeds 1 --ms 200 --tag ms200` → eLNs split ach 71 / mod 52 / gg 27; eLN rates (ach/mod/gg, Hz) and KCs active per model:

| Model | eLN ach/mod/gg (Hz) | KCs active |
|---|---|---|
| (a) | 38 / 108 / 45 | 0.7 % |
| (b) | 100 / 214 / 95 | 39.6 % |
| (c) | 63 / 147 / 60 | 5.8 % |
| (d) = (e) | 0.0 / 6.7 / 0.4 | 0.3 % |
| (f) | 90 / 194 / 82 | 27.1 % |

4. `--variants known+eln0.25 --hz 150 --odors test10,glomeruli,library --seeds 1 --ms 100` → all 53 glomeruli and 7 library classes run, 51 PN groups, VM6 mapped.
5. A made-up reference (one cell changed by 1e-9, one overlap pair changed) with `--strict` → `DIFFERS … 1 cells differ … overlap 55 pairs, 1 differ`, exit 3. The retry with `--skip-existing --strict` also exits 3.
6. `--out-dir experiments/results/x` → refused before loading anything. No `.tmp` files are left.

**Checked and found correct:**
- Seeds run 0..n-1 and each trial calls `seed`, `reset` and `set_drive` in `odor_code.py`'s order.
- No weights, noise or cut edges carry over between models: each model gets a new simulation and nothing edits weights.
- Rates are counts divided by ms/1000.
- There is no dense N×N matrix.
- `FLYBRAIN_SIGNS` and `FLYBRAIN_ELN` are ignored, as in `odor_code.py`. `FLYBRAIN_CONN`, `FLYBRAIN_MIN_SYN` and `FLYBRAIN_UNCLEAR_LN` are honoured, as in `odor_code.py`.

**Remaining risks**
- The digit match depends on `NUMBA_NUM_THREADS=6`.
- The check only runs at `--ms 500`, with 100 in `--hz`, test10, and a `--variants` entry that the reference also has. At `--seeds 3` (S21), the rows for seeds 0–1 of known+eln0.25 and known+eln0.5 are checked, but the overlap check is skipped.
- MaleCNS with `FLYBRAIN_UNCLEAR_LN=silent` would stop at the (a) check on the eLN count, because silenced LNs have empty rows. That case is not in the queue.
- The "150 cholinergic" wording: 71 is a count by predicted top transmitter. `known_nt` confirms acetylcholine for only 44 antennal-lobe local neurons, so "the runaway runs through the modulatory eLNs" rests on transmitter predictions.
- Smoke outputs are in `experiments/results_edge/_smoke/odor_code_plus/` and can be deleted. The `_elnsub.json` there predates the `limit` field.

**Commands for the queue** (with the [H] prefix; defaults are `--seeds 2 --ms 500`)
- S1: `python3 experiments/edge/odor_code_plus.py --dataset flywire --limit 1 --seeds 1 --out-dir $O --strict`
- S21: `python3 experiments/edge/odor_code_plus.py --dataset flywire --variants known+eln0.15,known+eln0.2,known+eln0.25,known+eln0.3,known+eln0.35,known+eln0.4,known+eln0.5 --hz 100 --seeds 3 --odors test10 --out-dir $O --strict --skip-existing`
- P2 odor-code-plus:
  - (a) `python3 experiments/edge/odor_code_plus.py --dataset flywire --variants known+eln0.25,known+eln0.3,known+eln0.35 --hz 150 --odors test10 --out-dir $O --skip-existing`
  - (b) `python3 experiments/edge/odor_code_plus.py --dataset flywire --variants known+eln0.25 --hz 100,150 --odors glomeruli,library --out-dir $O --skip-existing`
  - (c) `python3 experiments/edge/odor_code_plus.py --dataset flywire --variants known,known+eln0.25 --eln-subsets --hz 100 --odors test10 --out-dir $O --strict --skip-existing`

  In (c) I added `known` so the eLN ×1 runaway reference, with its per-class eLN rates, is in the same file; it costs about 20 extra sims and is also checked against the paper file.

**No deviations from the spec.** The per-class eLN columns and the VM6 mapping are added outputs, not changes to anything the spec defines.


######## arena_audit (experiments/edge/arena_audit.py)
I found four real bugs in `experiments/edge/arena_audit.py` and fixed them. None of them changes any verdict on the current logs. The full run still reproduces 14 of 14 printed values, and two runs gave byte-identical files. The script only reads logs, but I ran every check through `with_lock.sh` as asked.

**File changed (only this one):** `experiments/edge/arena_audit.py`. I regenerated `experiments/results_edge/arena-log-audit/` with the fixed script.

**Bugs found and fixed**
1. **The keep-the-lean rule was corrected twice.** The code kept the lean only if the Holm-adjusted p was below 0.025. The design's "p < 0.025 (Holm over mf/ff)" is Holm at 0.05 over two tests: the smaller raw p is compared with 0.025, which means Holm-adjusted p < 0.05. The old rule in effect asked for raw p < 0.0125. The rule also accepted a significant lean away from the male. It now requires more towards than away, Holm-adjusted p < 0.05, and the within-pre-contact shift P < 0.05. The md prints raw and Holm p, and the JSON adds `lean_mf_farcorr_p` and `lean_extra_chambers`. The verdict is still CHANGE: 15 towards / 20 away, p = 0.500, Holm 0.999, shift P = 0.153.
2. **The step-0 pooled lean pooled every specific-lobe chamber.** replication_stats.py only pools faint-smell, clean, noise0.2, noise0.2-virgin and the rep-* chambers. Arena logs from a new series (in `logs/` or via `--logs logs/edge_arena`) would have entered the "reproduced" 24/33. It now uses the same set as replication_stats. If the lean tests include chambers outside that set, section 2 and the verdict line say so. I tested this with two relabelled copies of one noise0.2 trial pair in the scratchpad, since deleted. The digit check stayed 14/14, the warning appeared, and trial t7 mapped to start t2.
3. **The placement distance was wrong when fly1's brain logged after fly2's (negative stagger).** It compared fly1's first row with fly2's row 0, which could be up to 15.8 s older. It is now taken when the later of the two brains logs its first row. The "contact before placement" test uses that same moment. Two trials changed and no flag moved:
   - rep-noise0.2 mf t3: 4.00 → 3.85 blocks
   - rep-noise0.2-virgin mf t1: 4.00 → 2.53 blocks
4. **Two inputs differed from how existing code reads them:**
   - Contact used `fillna(0)`, which encounter_stats.py does not. There are no NaNs today, so no number changed.
   - Trial labels past t5 had no start configuration. They now map to the trials.sh position the way trials.sh cycles, t6 → t1.

**What I checked and found correct:**
- the turn-toward index and the "turns at all" filter against replication_stats.py and paper_numbers.py section P;
- the exact sign test, Holm, and the bout runs (ticks × 0.05 s, brain_t_ms / 1000, t_wall in seconds);
- pairing (the 10-s rule, then the 60-s fallback);
- shift nulls: `default_rng(0)` per pairing and kind, offsets drawn from 10–90 % of the segment, one-sided P;
- `safe_out` refuses before any work: `--out-dir experiments/results/x` exits 1 and creates nothing.

The spec's checklist items on connectomes, seeds and simulator state don't apply, because nothing is simulated.

**Commands run** (with_lock.sh sets the pyenv PATH):
1. `experiments/edge/with_lock.sh python3 experiments/edge/arena_audit.py --quick --out-dir experiments/results_edge/_smoke/arena_audit`
   - `digit check: 2/2 printed values reproduced`
   - `index_matches_paper_csv: True`
2. `experiments/edge/with_lock.sh python3 experiments/edge/arena_audit.py --results release/pre_rerun_20260926/results --out-dir experiments/results_edge/_smoke/arena_audit/full`, then the same with `--out-dir experiments/results_edge/arena-log-audit`
   - `digit check: 14/14 printed values reproduced`, `index_matches_paper_csv: True`
   - `longest_bout_s: 86.25`, `longest_bout_genuine: False`, `longest_bout_without_placed_s: 31.15` (25.7 in the series first reported)
   - `lean_mf_farcorr_split: 15/20`, `lean_mf_farcorr_p_holm: 0.9991`, `lean_mf_shift_within_P: 0.153`, `lean_keep: False`
   - Compared with the author's run: all CSVs identical except those two `dist_at_placement` values. The md differs only in the criterion and pooled-set lines. Both runs gave identical files.
3. `PATH="$HOME/.pyenv/shims:$PATH" python3 experiments/edge/arena_audit.py --quick --out-dir experiments/results/x` → refused, exit 1.

**Remaining risks**
- **Teleport rows in body speed:** a few start-of-log teleport rows are counted as walking (one row of 8.66 blocks in 2.61 s, one of exactly 2.83 blocks, one of 3.26 blocks in 0.17 s). This lifts the 1.6–3.2 s bin's displacement per unit walk by about 7 % (0.303 against about 0.28). The trend and the comparability flags are unaffected.
- **Start positions:** these are parsed from the trials.sh `POS` array. A future `POS_SET` override (the offset-facing-approach case) would mislabel start distances and facings.
- **flag_plan:** it reads fly2's row 0, as the spec says, and that reading can be stale. `flag_placed` does not use it.
- **--quick coverage:** it does not exercise the 60-s pairing fallback or the pooled digit checks. Only the full run does.
- **S1 smoke command:** `--out-dir` is required, so the bare `arena_audit --quick` would fail.

**Command lines for the queue**
- **S1:** `python3 experiments/edge/arena_audit.py --quick --out-dir $O/arena_audit`
- **S4** (`arena-log-audit`, gate 10): `python3 experiments/edge/arena_audit.py --results release/pre_rerun_20260926/results --out-dir $O` with `O=experiments/results_edge/arena-log-audit`
- **Later arena edge logs:** `python3 experiments/edge/arena_audit.py --logs logs/edge_arena --out-dir experiments/results_edge/<step>`. Pointing it at `logs/edge_arena` alone keeps them out of the paper's set.

**Deviation from the spec:** I read "p < 0.025 (Holm over mf/ff)" as Holm-adjusted p < 0.05 (fix 1), and the page says so. The author's extra outputs, the 60-s pairing fallback and the placement-flag definition stay as the author listed them.


######## structure_probe (experiments/edge/structure_probe.py)
**Review of `experiments/edge/structure_probe.py`**

I found no bug that changes a number, and none of the risk areas you listed applies. I fixed two spec issues and two small defects, then re-ran the full female run. Every digit check passes. The MaleCNS option is still untested.

**Fixed in `experiments/edge/structure_probe.py`**
1. **"Published signs" was read as the published model only.** The paper and the critique use "the published signs" for Shiu signs with eLN ×0.25. The default variants are now `known+eln0.25,shiu+eln0.25,shiu`, so both readings are covered. The summary names each variant (the paper's model / the published signs with eLN ×0.25 / the published model).
2. **The male run would have broken once a third variant was added.** On MaleCNS, `known` applies nothing, so `known+eln0.25` and `shiu+eln0.25` both come out as `all_min1+eln0.25`. The state table and summary would then have mixed the two sets of rows. The script now skips any variant that builds the same model as an earlier one.
3. **Loose variant parsing.** A typo such as `knwon+eln0.25` silently ran the Shiu signs. It now stops with an error before the connectome loads.
4. **Latent duplicate routes.** When a pair has fewer than 3 routes, the `route1..3` columns could repeat a best-at-k route. They are now filled from the top routes only. The current data never triggered this.
5. **Two additions:**
   - The state table now has `w_1|<target>` for all four targets. The spec asks for k = 1..4 and it was missing.
   - Part (c) now reports the counts that explain the 9,200 gap (see the risks below).

**Checked and correct**
- **Maths:**
  - The simple-path correction for 3 hops is right.
  - The breadth-first search is right.
  - Forward and backward weights agree.
  - The routes for k = 1..3 add up exactly to w_k.
  - At k = 4 the search is limited to the 8 strongest first and last types, and this is documented.
- **Selections:** the groups come from `common` (Shiu's MN9 root id). Source and target sets never overlap.
- **No state leaks:** the raw `W0` is never changed, because `apply_model_options` builds a new matrix on a shallow copy.
- **Outputs and memory:**
  - Outputs go through `safe_out` into `results_edge/structure`, never `experiments/results/`.
  - There is no N×N dense matrix, and each variant's matrices are freed before the next.
  - Environment variables are ignored and each variant is set explicitly, so the paper's model is `shiu_min1+known+eln0.25`, the same string reproduce.sh produces.
- **Smoke run equals full run:** the `--limit 2` rows are identical to the full-run rows (largest |Δw| = 0; paths, hops and top route all equal).

**Commands run** (all through `with_lock.sh`)
1. A scratch script to check the photoreceptor count: 11,010 flips, of which 8,359 are photoreceptors, out of 11,391 photoreceptors.
2. Smoke run:
   `experiments/edge/with_lock.sh python3 experiments/edge/structure_probe.py --dataset flywire --limit 2 --variants known+eln0.25,shiu+eln0.25,shiu,shiu --out-dir experiments/results_edge/_smoke/structure_probe`
   It printed `[shiu] builds the same model as an earlier variant (shiu_min1): skipped` and took 24 s.
3. A scratch script that drops the `known_nt` column to imitate MaleCNS. Part (c) was skipped, `shiu+eln0.25` was deduplicated, and eLN came out at 166.
4. Full run: `experiments/edge/with_lock.sh python3 experiments/edge/structure_probe.py --dataset flywire`. It took 63 s and peaked at 1.38 GB. Key output lines:
   ```
   [known+eln0.25] ... signs=known (11010 flipped), eLN x0.25 (150 neurons)
   [shiu+eln0.25] ... eLN x0.25 (166 neurons)
   checks: {'route_sum_relerr': '7.0e-13', 'fwd_bwd_relerr': '6.3e-13', 'combo_additivity_relerr': '1.7e-14'}
   sign flips: 11010 (apply_model_options 11010), photoreceptors 8359, ALLN 16
   eLN: shiu 166, known 150; n_eln_apply_model_options[known+eln0.25]=150, n_eln_apply_model_options[shiu+eln0.25]=166
   ```
   The paths file now has 720 rows (3 × 240) and the routes file 4,146. I deleted both smoke directories afterwards.

Results are in `experiments/results_edge/structure/`: `structure_{paths,routes,state,signflips,aln}_flywire.csv`, `structure_flywire.md` and `structure_flywire.json`.

**Remaining risks**
- **Male untested.** The male table has 25.6 M connections against the female's 15.1 M, so I expect a peak of about 2.3–2.5 GB and two variants after deduplication. Swap was 5.5 of 6.1 GB, with a MaleCNS shuffle job running, so I did not run it.
- **9,200 photoreceptors is not reproduced.** No count I tried gives it, so treat the 9,200 in the `connectome.py` docstring as stale. The paper's "most of them photoreceptors" holds:
  - 8,359 photoreceptors flip, 76 % of all flips.
  - 8,620 photoreceptors are predicted excitatory.
  - 837 have no output synapses, so they have no sign and never flip.
  - 5 of the histamine flips are not photoreceptors: 4 ascending neurons and 1 L3.
- **Weights scale with group size.** w_k counts 1 per source neuron, so the "×-reference" ratios in the summary are not corrected for group size (touch has 1,417 neurons, sugar 129).
- **`k4_beam_share` can fall outside 0–1** when w_4 cancels, from −25.6 to +29 at worst.
- **A variant with eLN ×0 would get wrong all-connection hops.** Those hops ignore weights, so zeroed connections still count. This does not affect the defaults.

**Queue command lines**
- Female, gate 25, no `[P]` prefix needed because the environment is ignored:
  `python3 experiments/edge/structure_probe.py --dataset flywire`
- Male, gate 35 plus the swap-fraction wait (or `MIN_FREE=45 experiments/edge/with_lock.sh` for a one-off). It writes separate `*_malecns` files:
  `python3 experiments/edge/structure_probe.py --dataset malecns`


######## brian2_divergence (brain/tests/edge_brian2_reference.py and brain/tests/edge_brian2_divergence.py)
I found and fixed three bugs in `edge_brian2_divergence.py`; `edge_brian2_reference.py` was correct and is unchanged. At default settings the divergence script now matches Brian2 and the reproduce.sh kernel spike for spike, and nothing was written into `experiments/results/`.

**Files**
- `brain/tests/edge_brian2_divergence.py` (fixed)
- `brain/tests/edge_brian2_reference.py` (unchanged)

**Bugs fixed**
1. **False assert failure at the end of the run.** The trace stepped to `S + after`, past the last step of the recorded list. If the first mismatch fell in the last `--after` steps (2 by default), `rerun_ok` counted kernel spikes the list does not have. The script then printed "ASSERT FAILED" and exited 1, and under `set -e` that stops S5 before the eps runs.
   - I confirmed it with a doctored reference that adds one Brian2 spike at step 1999 of 2000. The pre-fix copy printed `stepped re-run consistent False` and exited 1. The fixed script prints `True` and exits 0.
   - Fix: `n_steps` is now one global, computed as in `LIF.run`. The trace stops at `min(S+after, n_steps-1)` and the re-run check uses that end. A mismatch outside steps 0..n_steps-1 (possible with a positive offset) is reported but not traced.
2. **Offset tie-break.** When offsets tied (for example a reference with no Brian2 spikes), `max()` returned -3. Offsets are now tried in the order 0, -1, 1, …, so ties go to the smallest shift.
3. **No check that the reference matches `--conn`.** The script now exits if the neuron counts differ. It also adds a note if the reference's sidecar names a different export (for example S6's `paper_export.npz`), since a spike-for-spike comparison against another export means nothing.

I also added a note for drives with several groups, or a group not in ascending order. Brian2 draws kicks per group and the kernel over the sorted union, so a mismatch on a driven neuron there is a random-stream difference, not a semantic one. This does not affect S5 (one sorted group).

**Checked and found correct**
- **Seeds:** the reference uses 0..n-1; the divergence script defaults to 0 1 2, with the offset calibrated on seed 1.
- **Units:** `spk_step` is `round(t/ms/dt)`; the offset came out +0.
- **Kick size:** stays 68.75 mV for the female. The export has `w_syn_scale` 1.0, and all input groups are sorted.
- **State between seeds:** every pass does seed, then reset, then set_drive; nothing is left over from the previous seed.
- **Memory:** no dense N×N matrix is built, and the float64 version stays in the `$TMPDIR` cache.
- **Trace:** its v_int emulation follows `_integrate`'s dtypes and order of operations, and the consistency checks confirm it.
- **Outputs:** every file goes through `safe_out`; the sidecar is `<out>.sidecar.json`.

**Smoke runs after the fixes** (via `with_lock.sh`, one at a time)
1. `python3 brain/tests/edge_brian2_divergence.py --conn $B/flywire_export.npz --ref experiments/results_edge/_smoke/edge_brian2_reference/ref_sugar_times.npz --dt 0.1 --seeds 0 --out experiments/results_edge/_smoke/edge_brian2_divergence/div_default.json` gave:
   - `step offset calibrated on seed 0: +0 (4465 of 4465 ...)`
   - `counts identical True ... spike lists identical True ... masked==unmasked True, split==whole True`
   - `summary: seed 0: identical, spike for spike`, exit 0, 5.9 s, 573 MB peak.
2. **Digit check** against the reproduce.sh kernel path: `NUMBA_CACHE_DIR=$TMPDIR/flycraft_edge_nbcache python3 brain/tests/compare_brian2.py --conn $B/flywire_export.npz --ref .../ref_sugar_times.npz --dt 0.1` gave:
   - `kernel seed 0: 4465 spikes | brian2: 4465 spikes`
   - `in_grn_sugar 82.95 / 82.95`, `out_feed 19.81 / 19.81`, `r = 1.0000`, `active in brian2 only: 0, kernel only: 0`
3. Doctored last-step reference: pre-fix copy exit 1 (false assert), fixed script exit 0. The doctored files are `experiments/results_edge/_smoke/edge_brian2_divergence/ref_fake_laststep.npz` and `div_fake_laststep.*`, both deletable.

The earlier Brian2 digit check (original vs edge reference, identical at 4465 spikes) still holds, because the reference script is unchanged.

**Remaining risks**
- **Untested path:** 3 seeds with seed 1 calibrated first was not run, because smoke tests are limited to 1 seed. The logic is the same loop.
- **Reference memory:** during the 3-seed run the previous seed's Brian2 objects stay alive while the next are built, as in `brian2_reference.py`. The design measured the original at 1.53 GB, which is fine for gate 25.
- **Hum references (`--noise-hz`, not S5):** the record mask covers almost every neuron, so `LIF.run` allocates about 0.5 GB of record buffers per 250-step chunk (in lif.py).
- **"far (> 0.05 mV): semantic" label:** it is based on the kernel's margin at the mismatch step. For a Brian2-only spike on a driven neuron (`groups` includes `in_*`), it may reflect the refractory-kick rule or the random stream rather than the integration. Read it together with the `groups` field.
- **`set -e`:** the script exits 1 only when an internal assert fails; that stops the later S5 runs, which is intended. A mismatch alone exits 0.

**Queue commands (S5, [H], without [P])**
```
set -e; O=experiments/results_edge/brian2-first-divergence; mkdir -p $O
B=${TMPDIR:-/tmp}/flycraft_brian2
test -f $B/flywire_export.npz || env -u FLYBRAIN_SIGNS -u FLYBRAIN_ELN python3 brain/tests/export_for_brian2.py --dataset flywire --out $B/flywire_export.npz
b2venv/bin/python brain/tests/edge_brian2_reference.py --conn $B/flywire_export.npz --drive in_grn_sugar:100 --ms 1000 --seeds 3 --dt 0.1 --record-times --out $O/ref_sugar_times.npz
export NUMBA_CACHE_DIR=${TMPDIR:-/tmp}/flycraft_edge_nbcache
D="python3 brain/tests/edge_brian2_divergence.py --conn $B/flywire_export.npz --ref $O/ref_sugar_times.npz --dt 0.1"
$D --out $O/div_default.json
$D --eps-v 0 --eps-g 0 --out $O/div_eps0.json
$D --eps-v 0 --eps-g 0 --float64 --out $O/div_eps0_f64.json
```
The queue should run these with `NUMBA_NUM_THREADS=6`. Seeds default to 0 1 2 with the offset calibrated on seed 1.
