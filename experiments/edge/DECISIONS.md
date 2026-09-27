# Edge-case suite: decisions over the design (27 Sep 2026, RESEARCH_NOTES 23)

The design is `design_plan.md` (merged from seven arm analyses) and `design_critique.md` (completeness critic). Where
they disagree, this file wins.

## Ground rules
- New code only under `experiments/edge/` and `brain/tests/edge_*`. No existing script is edited in the offline suite.
- Every output under `experiments/results_edge/<step>/` via `_edge.safe_out` + `_edge.finish` + `_edge.sidecar`.
  Nothing is written into `experiments/results/` (safe_out refuses).
- Any smoke test that loads a connectome runs through `experiments/edge/with_lock.sh` (one at a time, >= 35 % free
  memory). Female connectome only for smoke tests; keep them short (`--seeds 1 --ms 100-300`). The male connectome
  (about 4-5 GB) is not loaded in smoke tests unless a reviewer asks for it, and then with `MIN_FREE=45`.
- Python: `$HOME/.pyenv/shims/python3` (3.12.8, numba 0.65.1). `NUMBA_NUM_THREADS=6` unless a step says otherwise.
- `benchmark.py` and `sensitivity.py` run on import: never import them (constants are in `_edge.py`; parse
  sensitivity.py's CONDITIONS with `ast`). `paper_numbers.py` writes on import: copy `steer()` instead.
- `grid_probe --check-against` against the reproduce.sh files is the engine's correctness test: at defaults it must
  reproduce the paper's files to the digit (same seeds 0..n-1, same thread count).

## Changes to the plan (from the critique, accepted)
1. S0 gate exits when the re-run queue process is gone (or its `figures` marker exists), never hangs.
2. S2 additionally checks: every compared file has mtime >= 2026-09-26 23:44, no `logs/rerun_20260926_done/*.failed`.
3. One simulation run per step where a step would otherwise repeat a long multi-run on retry; or skip outputs that exist.
4. S8 uses threads 3 (the arena's per-brain count) and 8; not 10 (identical to 8 by construction, T = min(threads, 8)).
5. S9: the zero-input check cannot fail by construction (no intrinsic currents, no noise): keep only the checks that
   can fail — self-sustained activity after the drive / hum is removed (act_n == 0 at the END of the 3-s off phase),
   and 10-s drift. The paper will say "no activity of its own" is a property of the model.
6. Promoted to P1: `grid_probe --ei` for the female deciders (subthreshold depolarisation, E and I input under cVA,
   JO-A, touch, cVA+touch at gains 1.0 and 1.4) and a reachability positive control preset `decider_reach` (drive the
   top-5 excitatory presynaptic cell types of each decider, and of oviDN, at 30 and 100 Hz: can the deciders fire at
   all?). Female `matched_null` promoted to P1. S15 also gets `--cond rewire=global,shuffle=0`.
7. The `freeze` preset gains specificity controls: food@100 plus each of sugar GRNs, bitter GRNs, JO-A, JO-CE, and a
   random set of non-touch sensory neurons the size of the touch set (1,417), 3 draws.
8. S19 (state on the hum) at 10 seeds. A structural table (no simulation) of hunger/fullness neurons: outgoing
   synapses, hops to MN9 / PAM / feed MNs, against SAG and pC1 — in `structure_probe.py`.
9. Male `touch_dose_male` promoted to P2. Male hum state at P2.
10. S23 cut to 6 cycles, 4 runs. S5 (Brian2 divergence) and S21 (eLN sweep) are P2. brian2-10s, micro-semantics,
    persistence-gain1.4 dropped to P3 (not run).
11. `structure_probe.py` (new, no simulation): decider paths (hops and signed propagated weight from each sensory class
    to each decider, top routes), hunger-neuron outputs, the 11,010 known-sign flips broken down by class, the eLN
    counts by predicted transmitter.

## Not run in the offline suite
Arena edge cases (section 3 of the plan) are decided after the offline suite and the arena log audit (S4), because
they need the Minecraft server, 5-9 GB and hours, and some need opt-in changes to bot.js / run_pair.sh / trials.sh.
