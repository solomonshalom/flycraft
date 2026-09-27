**Critique of the flycraft edge-case plan: concrete fixes (read-only; I ran no simulations and changed no files)**

**Checked by reading files**
- **The re-run is already deterministic.** 11 files have been rewritten so far by the 26 Sep re-run: benchmark ×2, odor_code ×4, social_probe ×4, gain_sweep ×4 and the published-lobe global shuffle. Each is identical to `release/pre_rerun_20260926/results/` (max numeric difference 0, wall time ignored).
- **S13's k=5 sanity check will pass.** The `shiu_min1` and `zenodo_min1` caches each have 15,090,883 connections. Each has 2,700,429 with |w| ≥ 5, which matches both `*_min5.npz` exactly. The two tables therefore hold the same connections and differ only in signs, so S13's 8 rows are really 4 thresholds × 2 sign sources.
- **The female walks only through DNa.** DNp09 is 0.0–0.67 Hz in every row of `contact_stop_flywire.csv`, both alone and with touch. `motor.py` reads female walking as a saturating function of DNp09 + DNa01/02. So in the arena the freeze is just DNa suppression, by how the decoder is built. Meanwhile touch raises "DN all" from about 1.3 to 8.4 Hz.
- **§4 item 15 is half wrong.** The paper says "under the published signs", and that is accurate for the Shiu-signs ×0.25 file. The rest of the item stands:
  - Food steering there is +1.2 to +2.7 Hz towards food.
  - The bias ranges from 8.2 to 29.2 Hz, not 16–29, and is 0 at 25 Hz for CO2 and the aversive odour.

**Headline claims with no edge case yet**
1. **"Touched female freezes" / "stayed together because touch switched off steering".**
   - There is no specificity control. Touch drives 1,417 neurons; sugar with cVA already cuts DNa by 25 %.
   - Add to the `freeze` preset: food@100 plus each of sugar, bitter, JO-A, JO-CE, and a random set of 1,417 non-touch sensory neurons.
   - Add a per-DN-type readout under touch, to show which walking-related DNs the decoder ignores.
   - Note 11 should say female walking is read from DNa01/02 + DNp09, and DNp09 is silent.
2. **"The paths … to the deciding neurons carry nothing"** is called the model's most important miss, but only P3 tests it.
   - Promote `--ei` (female) to P1: depolarisation below threshold and E/I input for pC1a–e, aIPg and vpoDN under cVA, JO-A, touch and cVA+touch at gains 1.0 and 1.4.
   - Add a reachability positive control to the same step: drive each decider's top 5 presynaptic types, like `ovidn_reach`, and promote `ovidn_reach` to P2. Otherwise "no state starts egg-laying" has no positive control.
3. **"Hunger changes nothing … in either sex".**
   - The male is never tested on the hum.
   - S19 at 5 seeds cannot tell NPF's +6.8 Hz from the +3.6–4.4 Hz band of unrelated states. Use 10 seeds.
   - Add a structural table from W (no simulation): outgoing synapses and hops to MN9 and PAM for NPF, IPC, DH44, AstA and SIFa against SAG and pC1.
4. **The virgin state.**
   - Promote the female `matched_null` from P2 to P1. It is the first thing a reviewer asks for this result.
   - S15 tests SAG→pC1 only under the block null. Add `--cond rewire=global,shuffle=0` to S15.
5. **"Males … backed out"** rests on MDN, and the paper itself says that reflex fails test 1. Promote `touch_dose_male` from P3 to P2.
6. **"The published model has no activity of its own"** holds by construction: there are no intrinsic currents and no noise, and rest is below threshold. S9's zero-input check cannot fail. Keep only the checks that can: self-sustained activity after the drive or noise is removed, and 10-s drift. Reword the sentence as a property of the model.
7. **The published-lobe left circling** has no check. From existing files, add to S3: DNa L−R for every input in `social_probe_flywire_shiu_min1` and the published gain sweep.
8. **Note 3's "11,010 … most of them photoreceptors"** is not re-derived by any step. Add it to S3 as a structural count.

**Steps that cannot run as written, or would overwrite or pool files**
1. **S1 smoke fails on required arguments.**
   - `grid_probe` needs `--out`.
   - `conditioning_edge` needs `--out-dir`; `expression_harsh` and `odor_code_plus` need `--out-dir` and `--dataset`.
   - Add them. Also add two asserts, because S5's method depends on both:
     - masked and unmasked runs give the same counts;
     - `run(a)` then `run(b)` equals `run(a+b)`.
2. **edge_report must not import `paper_numbers.py`** to get `steer()`. At module level it calls `parse_args()` and writes `experiments/results/paper_numbers.md`. Copy `steer()` (l.315) instead.
3. **Arena logs would be pooled into the paper.** `encounter_stats`, `replication_stats`, `figures_print` and `paper_numbers` all glob `logs/fly*_off-*.csv`, and LOGS is hard-coded, so `run_redirect` cannot change it. The next reproduce/figures run would add new series to the 24/33 lean and the table. Move each edge trial's logs to `logs/edge_arena/` straight away, and have `arena_audit` read from there.
4. **S2 could report false "identical" results.** A re-run step that failed leaves the old file, which compares as identical. Add these checks:
   - every compared file has mtime ≥ 26 Sep 23:44;
   - there is no `logs/rerun_20260926_done/*.failed`;
   - diff the per-group commands in the 25 Sep and 26 Sep logs before blaming nondeterminism, because `reproduce.sh` changed on 26 Sep at 19:31.
5. **S0 can hang forever.** If the re-run queue dies before `figures`, S0 never ends. Exit when `! pgrep` holds, or after a maximum wait.
6. **A late failure repeats a whole multi-run step.** With `set -e`, a failure near the end of S23, S24 or S17 reruns everything in it on the retry (about 26 min for S23). Put one run per step, or skip runs whose output already exists.
7. **S9's "act_n is 0" cannot pass right after offset.** With eps_v = 0.01 mV and τ_m = 20 ms, snapping to rest takes about 130 ms. Require act_n = 0 at the end of the 3-s off phase.
8. **The swap rule is not enforced.** `run_guarded` gates on free % only, so "hold male steps if swap > 6.5 GB" does nothing unless a pre-command enforces it. The rule also assumes 8 GB of swap; at 00:44 `vm.swapusage` showed 4.0 of 5.1 GB. Use gate 40 plus a swap-fraction wait for S20 and the P2 male steps.
9. **Male no-US control.** In `cond-male-noUS`, the male's sugar GRNs drive PPL1 at 11.7 Hz, so `--us wiring` is not free of a teaching signal. Report the punishment compartment separately; do not require ≤ 0.1 in both.

**Decorative: cut or replace**
- **S8's T10 run** is identical to T8 by construction (T = min(threads, 8)). Replace it with T3, the arena's thread count per brain, which tests whether offline and arena results are comparable.
- **Merge S16 into S18.** Run it through `grid_probe` with the split readouts at 10 seeds and `--check-against` the state_probe file.
- **P2 `brian2-10s`, `micro-semantics` and `persistence-gain1.4`**: none of them can change a claim. Move them to P3.
- **P2 `sensitivity-fullmap-male`**: "no other smell at all" already fails in existing files beyond DNp13, so reword and cut the step. Keep `gain-map-male` for P1 per neuron.
- **S5 and S21**: §4 rewords both claims regardless. Move S5 (two new scripts) to P2, and put S21 in P2 or P3.

**Too costly for their value, or under-costed**
- **S23** is about 26–30 min, not 15. The 25 Sep conditioning group averaged about 1 min per 3-cycle run, uncontended; 10 cycles is about 3.2× that, over 8 runs. Cut it to 3 runs, or use 6 cycles.
- **Arena `anosmic-female-arena` (120 min)**: the lean probably goes after S4 anyway. Replace it with **`hum-ff-no-touch`** (touch input masked on contact). That is the direct causal test of "stayed together because touch switched off steering".
- **Arena `sync-hum-ff`** changes the seeds and the launch sync together. Split them, so that a "new seeds only" replication exists. Every series so far shares seeds 1–5, and the replication used them too.
- **`hum-level-ff` (65 min)** is low priority.

**Held-out seeds already paid for**
- State in S7: seeds 5–9 of `social_dt0.2` are held-out seeds at production dt for every Note 4/5 number. Evaluate them explicitly.
- For S13, also check the Shiu k=5 row against the sensitivity file's "connections >= 5 synapses" row.

**Wording to add to §4**
- Female walking is DNa by how the decoder is built.
- "No activity of its own" is true by construction.
- Item 15: keep only the food-steering and bias-range corrections.