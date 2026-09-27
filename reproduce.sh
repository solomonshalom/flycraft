#!/usr/bin/env bash
# reproduce.sh — the command behind every result file in experiments/results/ (RESEARCH_NOTES.md sections in brackets).
#
#   ./reproduce.sh list            print every group with its output files and the command that makes them
#   ./reproduce.sh <group> [...]   run those groups (offline groups need only Python; arena groups need ./run.sh server)
#   ./reproduce.sh all             every offline group in order, then the figures and the number check (about 4.5 h on an M4 MacBook, 16 GB)
#   ./reproduce.sh arena           the arena groups (encounter trials, in-world learning; several hours, one at a time)
#   ./reproduce.sh archive         the release package: release/flycraft_<date>.tar.gz with the result csv / figures, every
#                                  arena and experiment log, the notes, README, paper draft, this script, and a sha256 MANIFEST
#
# The model of the paper is FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25 (female variant shiu_min1+known+eln0.25, male
# all_min1+eln0.25); every output file carries the variant in its name, so runs on other variants never overwrite these.
# Simulations are seeded; offline results reproduce to the digit on the same numba version (versions in README, "Running it").
# Arena runs depend on wall-clock speed (the body scales to brain time) and reproduce statistically, not tick for tick.
# Data files (data/) are downloaded separately (README, "Running it"); they are not part of this package.
set -uo pipefail
cd "$(dirname "$0")"
export PYTHONWARNINGS=ignore
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6}
PAPER="FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25"
PUBLISHED="FLYBRAIN_SIGNS=shiu FLYBRAIN_ELN=1"

# plain indexed arrays (macOS ships bash 3.2, which has no associative arrays)
ALL_GROUPS=(); OUTS=(); CMDS=(); NOTES=()
group() { ALL_GROUPS+=("$1"); OUTS+=("$2"); CMDS+=("$3"); NOTES+=("$4"); }
index_of() { local i; for i in "${!ALL_GROUPS[@]}"; do [ "${ALL_GROUPS[$i]}" = "$1" ] && { echo "$i"; return 0; }; done; return 1; }

# ---------------------------------------------------------------- core checks
group core-check "brain/tests: spike-for-spike agreement with Brian2; dt independence" \
  "python3 brain/tests/test_lif.py && python3 brain/tests/test_model_options.py && B2=\${TMPDIR:-/tmp}/flycraft_brian2 && mkdir -p \$B2 && python3 brain/tests/export_for_brian2.py --dataset flywire --out \$B2/flywire_export.npz && b2venv/bin/python brain/tests/brian2_reference.py --conn \$B2/flywire_export.npz --drive in_grn_sugar:100 --ms 1000 --seeds 3 --dt 0.1 --out \$B2/ref_sugar.npz && python3 brain/tests/compare_brian2.py --conn \$B2/flywire_export.npz --ref \$B2/ref_sugar.npz --dt 0.1" \
  "[14a, 14d, 22] Brian2 lives in its own venv (README, "Running it": python -m venv b2venv && b2venv/bin/pip install brian2 numpy cython); sugar GRNs 100 Hz, 1 s, 3 seeds, dt 0.1 ms: identical per-neuron spike counts in 2 of 3 seeds, the third within 0.8 % of spikes (a near-threshold event)"
group anchors "benchmark_flywire.csv, benchmark_flywire_shiu_min1+known+eln0.25.csv, fig8_benchmark.png" \
  "python3 experiments/benchmark.py --seeds 3 && $PAPER python3 experiments/benchmark.py --seeds 3" \
  "[14h, 16a] published circuit results with Shiu et al.'s own neuron ids: sugar -> MN9 curve, bitter suppression, JO-CE -> aBN1, sound -> GF"

# ---------------------------------------------------------------- innate arm: maps, windows, controls
group odor-code "odor_code_flywire.csv, odor_code_flywire_overlap.csv, odor_code_malecns.csv, odor_code_malecns_overlap.csv (Fig 9)" \
  "python3 experiments/odor_code.py --dataset flywire --seeds 2 && python3 experiments/odor_code.py --dataset malecns --seeds 1" \
  "[16a, 16j] does the antennal lobe tell odors apart? glomerular specificity and KC sparseness across sign rules and eLN scales (the script sweeps the variants itself)"
group social-map "social_probe_{flywire_shiu_min1,malecns_all_min1}_noise0.csv (published lobe), social_probe_{flywire_shiu_min1+known+eln0.25,malecns_all_min1+eln0.25}_noise0.csv (paper's model; Fig 1)" \
  "$PUBLISHED python3 experiments/social_probe.py --dataset flywire --seeds 5 && $PUBLISHED python3 experiments/social_probe.py --dataset malecns --seeds 5 && $PAPER python3 experiments/social_probe.py --dataset flywire --seeds 5 && $PAPER python3 experiments/social_probe.py --dataset malecns --seeds 3" \
  "[14f, 14i, 16i, 16j] the innate input x output map, both sexes, 1 s, 100 Hz"
group gain "gain_sweep_{flywire_shiu_min1,malecns_all_min1}.csv, gain_sweep_{flywire_shiu_min1+known+eln0.25,malecns_all_min1+eln0.25}.csv (Fig 4)" \
  "$PUBLISHED python3 experiments/gain_sweep.py --dataset flywire --seeds 3 && $PUBLISHED python3 experiments/gain_sweep.py --dataset malecns --seeds 3 && $PAPER python3 experiments/gain_sweep.py --dataset flywire --seeds 5 && $PAPER python3 experiments/gain_sweep.py --dataset malecns --seeds 5" \
  "[14g, 14j, 18a, 18b, 20a] per-synapse weight x0.5-2.0; the robustness rule is presence at 0.7, 1.0 and 1.4 (the paper's model: 5 seeds since 20 Sep; the 3-seed files are in results/old_v1/)"
group shuffle "shuffle_flywire_shiu_min1_{global,block}.csv, shuffle_flywire_shiu_min1+known+eln0.25_global.csv, shuffle_malecns_all_min1+eln0.25_global.csv (Fig 6)" \
  "$PUBLISHED python3 experiments/shuffle_control.py --dataset flywire --mode global --shuffles 3 --seeds 3 && $PUBLISHED python3 experiments/shuffle_control.py --dataset flywire --mode block --shuffles 2 --seeds 3 && $PAPER python3 experiments/shuffle_control.py --dataset flywire --mode global --shuffles 3 --seeds 3 && $PAPER python3 experiments/shuffle_control.py --dataset malecns --mode global --shuffles 2 --seeds 3" \
  "[14r, 14v, 18d] degree-preserving rewiring abolishes every response, both sexes"
group sensitivity "sensitivity_flywire_shiu_min1.csv (published lobe; the 14 Sep file sensitivity_flywire.csv came from an older script), sensitivity_flywire_shiu_min1+known+eln0.25.csv, sensitivity_malecns_all_min1+eln0.25.csv (Fig 7)" \
  "$PUBLISHED python3 experiments/sensitivity.py --dataset flywire --seeds 3 && $PAPER python3 experiments/sensitivity.py --dataset flywire --seeds 3 && $PAPER python3 experiments/sensitivity.py --dataset malecns --seeds 3" \
  "[14s, 18e, 18k] transmitter-sign rule x eLN scale (male: the 67 unclear LNs), stimulus rate, dt, numerics, connection table and threshold"
group odor-dose "odor_dose_flywire_shiu_min1+known+eln0.25.csv, odor_dose_flywire_shiu_min1+eln0.25.csv, odor_dose_flywire_zenodo_min1+known+eln0.25.csv, odor_dose_malecns_all_min1+eln0.25.csv (Fig 10)" \
  "$PAPER python3 experiments/odor_dose.py --dataset flywire --seeds 3 && FLYBRAIN_SIGNS=shiu FLYBRAIN_ELN=0.25 python3 experiments/odor_dose.py --dataset flywire --seeds 3 && FLYBRAIN_CONN=zenodo $PAPER python3 experiments/odor_dose.py --dataset flywire --seeds 3 && $PAPER python3 experiments/odor_dose.py --dataset malecns --seeds 3" \
  "[18c] left / right / bilateral odor at 25-150 Hz: the sign of chemotaxis is the sign rule's; no rule gives approach"
group contact-stop "contact_stop_flywire.csv, contact_stop_malecns.csv" \
  "python3 experiments/contact_stop.py --dataset flywire --seeds 5 --noise 0.2 && python3 experiments/contact_stop.py --dataset malecns --seeds 5 --noise 0.2" \
  "[19d, 20a] is 'touch shuts the turning DNs' wiring or labelling? the sign-rule x eLN x table axis, with and without the noise substrate (5 seeds since 20 Sep)"
group noise-floor "noise_floor_flywire_shiu_min1+known+eln0.25.csv, noise_floor_malecns_all_min1+eln0.25.csv" \
  "$PAPER python3 experiments/noise_floor.py --dataset flywire --noise 0,0.02,0.05,0.1,0.2,0.3,0.5,1.0 --seeds 3 && $PAPER python3 experiments/noise_floor.py --dataset malecns --noise 0,0.1,0.2,0.3,0.5 --seeds 3" \
  "[19c] calibration of the background-noise walking substrate used in the 19b encounter trials (0.2 Hz)"
group precontact "precontact_dose_flywire_shiu_min1+known+eln0.25{,_window,_far,_near}.csv (Fig 14 / Figure 6-S3)" \
  "$PAPER python3 experiments/precontact_dose.py --dataset flywire --seeds 3 && $PAPER python3 experiments/precontact_dose.py --dataset flywire --set window --noise 0 --seeds 5 && $PAPER python3 experiments/precontact_dose.py --dataset flywire --set far --noise 0.2 --seeds 10 && $PAPER python3 experiments/precontact_dose.py --dataset flywire --set near --noise 0.2 --seeds 10" \
  "[20b, 21] the pre-contact slowing of 19b as a dose row: bilateral cVA + Or47b + CO2 at the far and near levels the female reports in the arena, 2 s settle + 2 s read, with and without the substrate; the Or47b x CO2 window at 0.05 steps (5 seeds); the far- and near-level cells on the substrate at 10 seeds"

# ---------------------------------------------------------------- state arm
group state "state_probe_flywire_shiu_min1_state30.csv, state_probe_flywire_shiu_min1_state100.csv, state_probe_malecns_all_min1_state30.csv (published lobe); state_probe_{flywire_shiu_min1+known+eln0.25,malecns_all_min1+eln0.25}_state30.csv (paper's model; Fig 5)" \
  "$PUBLISHED python3 experiments/state_probe.py --dataset flywire --seeds 5 && $PUBLISHED python3 experiments/state_probe.py --dataset flywire --seeds 3 --state-hz 100 && $PUBLISHED python3 experiments/state_probe.py --dataset malecns --seeds 5 && $PAPER python3 experiments/state_probe.py --dataset flywire --seeds 5 && $PAPER python3 experiments/state_probe.py --dataset malecns --seeds 5" \
  "[14k, 14p, 14w, 19e] tonic activity in the fly's own state neurons (SAG, IPC, DH44, NPF, SIFa, AstA, pC1, aIPg, P1) x social inputs"

# ---------------------------------------------------------------- learning arm (offline)
COND="python3 experiments/conditioning.py --dataset flywire --signs known --us dan"
group conditioning "conditioning_flywire_shiu_min1+known+eln0.25_us-dan-{reward,punish}_{vinegar-vs-ester,ester-vs-vinegar}_seed{0,1,2}.csv (+_compartments.csv); ..._us-wiring_...; ..._us-dan-{reward,punish}-20hz_...; ..._eln0.1_us-dan-...; ..._us-dan-*-phasic2_...; conditioning_malecns_all_min1+eln0.25_us-dan-{reward,punish}_*_seed0.csv (Figs 2, 2b, 2c)" \
  "for s in 0 1 2; do for v in reward punish; do $COND --eln 0.25 --valence \$v --csp vinegar --csm ester --seed \$s; $COND --eln 0.25 --valence \$v --csp ester --csm vinegar --seed \$s; done; done; \
   for s in 0 1 2; do python3 experiments/conditioning.py --dataset flywire --signs known --eln 0.25 --us wiring --csp vinegar --csm ester --seed \$s; done; python3 experiments/conditioning.py --dataset flywire --signs known --eln 0.25 --us wiring --csp ester --csm vinegar --seed 0; \
   for s in 0 1 2; do $COND --eln 0.25 --us-hz 20 --valence reward --csp vinegar --csm ester --seed \$s; $COND --eln 0.25 --us-hz 20 --valence reward --csp ester --csm vinegar --seed \$s; $COND --eln 0.1 --valence reward --csp vinegar --csm ester --seed \$s; $COND --eln 0.1 --valence reward --csp ester --csm vinegar --seed \$s; done; \
   for o in 'vinegar ester' 'ester vinegar'; do set -- \$o; $COND --eln 0.25 --us-hz 20 --valence punish --csp \$1 --csm \$2 --seed 0; $COND --eln 0.1 --valence punish --csp \$1 --csm \$2 --seed 0; $COND --eln 0.25 --tau-dan 2 --valence reward --csp \$1 --csm \$2 --seed 0; $COND --eln 0.25 --tau-dan 2 --valence punish --csp \$1 --csm \$2 --seed 0; done; $COND --eln 0.25 --tau-dan 2 --valence punish --csp ester --csm vinegar --seed 1; python3 experiments/conditioning.py --dataset flywire --signs known --eln 0.25 --us wiring --tau-dan 2 --csp vinegar --csm ester --seed 0; \
   for v in reward punish; do python3 experiments/conditioning.py --dataset malecns --eln 0.25 --us dan --valence \$v --csp vinegar --csm ester --seed 0; python3 experiments/conditioning.py --dataset malecns --eln 0.25 --us dan --valence \$v --csp ester --csm vinegar --seed 0; done" \
  "[16f, 16g, 16h, 18f, 18j] odor-sugar / odor-punishment conditioning: CS+ / CS- reciprocal pairs, 3 seeds, US dose 50 / 20 Hz, eLN x0.25 / x0.1, phasic US, no-US and wiring-US controls, the male"
group expression "expression_probe_flywire_shiu_min1+known+eln0.25.csv (Fig 11)" \
  "$PAPER python3 experiments/expression_probe.py --seeds 3" \
  "[18g] tonic drive on the MBONs' targets x MBON silencing: the memory is not expressible in this model"

# ---------------------------------------------------------------- figures
group figures "experiments/results/fig*.png, fig*_print_*.{png,pdf}, paper_numbers.md" \
  "python3 experiments/encounter_stats.py && python3 experiments/figures.py && python3 experiments/figures_print.py && python3 experiments/paper_numbers.py" \
  "every figure from the csv files above and the arena logs in logs/; the print versions (figures_print.py); every number of the earlier Markdown draft re-derived and checked (paper_numbers.py)"

# ---------------------------------------------------------------- arena (needs ./run.sh server on port 25565; one at a time)
group arena-encounters "logs/fly{1,2}_off-*_<stamp>.csv (trial labels off_ff_t<i>, off_mf_t<i>[, _clean, _noise0.2, _noise0.2-virgin]); encounter_trials.csv; Fig 3, 3b" \
  "AL=published experiments/encounter_trials.sh 5 180; experiments/encounter_trials.sh 5 300; NOISE=0 experiments/encounter_trials.sh 5 300; NOISE=0.2 experiments/encounter_trials.sh 5 300; CONDS=mf STATE2=virgin NOISE=0.2 LABEL=noise0.2-virgin experiments/encounter_trials.sh 5 300" \
  "[14u, 18h, 19b, 21] 5 female-female + 5 male-female trials per condition: published lobe (14 Sep, 180 s); specific lobe in the chamber with the faint flower smell (17 Sep; to reproduce it you would have to rebuild the world4-6 patches at x = +-15 first); clean chamber; clean + 0.2 Hz substrate; clean + substrate with a virgin female (SAG tonic, 24 Sep; LABEL without '_' so encounter_stats.py keeps it a chamber of its own). The 14 Sep and 17 Sep series were run with the encounter_trials.sh of their day (no LABEL, no clearing); the current script clears the world first"
group arena-replication "logs/fly{1,2}_off-*_<stamp>.csv with trial labels off_ff_t<i>_rep-clean, off_mf_t<i>_rep-clean, ..._rep-noise0.2, off_mf_t<i>_rep-noise0.2-virgin; experiments/results/replication_20260925.md, paper/tables_arena.tex, fig_replication" \
  "experiments/run_replication.sh 5 300 && python3 experiments/figure_replication.py" \
  "[22] the clean, substrate and virgin series again, under labels of their own (a LABEL must not contain '_'), summarised next to the series they repeat"
group arena-learning "logs/fly1_mb-flywire-dan-known-eln0.25_<stamp>.csv, logs/learn_world{1..6}*.out, learn_world{4,5,6}_probe_{pre,post}.json" \
  "PRE=120 TRAIN=300 POST=120 R=10 experiments/learn_in_world.sh world1; HOLD=8 PATCH_R=3 BITTER=vinegar PRE=90 TRAIN=360 POST=90 VIEW=0 experiments/learn_in_world.sh world3; HOLD=8 PATCH_R=3 BITTER=vinegar PRE=60 TRAIN=360 POST=60 VIEW=0 R=10 experiments/learn_in_world.sh world4; HOLD=8 PATCH_R=3 BITTER=vinegar PRE=60 TRAIN=360 POST=60 VIEW=0 R=28 experiments/learn_in_world.sh world5; HOLD=8 PATCH_R=3 BITTER= PRE=60 TRAIN=360 POST=60 VIEW=0 R=28 experiments/learn_in_world.sh world6" \
  "[16k, 18i] one fly, two flower patches, pre / train / post; learn_stats.py on the log and brainctl.py probe before / after (world1 R=10 patches at x=+-6; world4 the same chamber, 7x7 patches; world5/6 R=28, patches 30 blocks apart)"

list() {
  local i
  for i in "${!ALL_GROUPS[@]}"; do
    printf '\n## %s   %s\n   files:   %s\n   command: %s\n' "${ALL_GROUPS[$i]}" "${NOTES[$i]}" "${OUTS[$i]}" "${CMDS[$i]}"
  done
}
run() {
  local g=$1 i
  i=$(index_of "$g") || { echo "unknown group: $g (./reproduce.sh list)"; return 1; }
  echo "== $g  $(date +%T)"; echo "   ${CMDS[$i]}"
  mkdir -p logs
  bash -c "${CMDS[$i]}" > "logs/reproduce_${g}.out" 2>&1 && echo "   ok  $(date +%T)" || echo "   FAILED (logs/reproduce_${g}.out)  $(date +%T)"
}
archive() {
  local stamp; stamp=$(date +%Y%m%d)
  local dir="release/flycraft_${stamp}"
  rm -rf "$dir"; mkdir -p "$dir/experiments" "$dir/logs" "$dir/brain"
  cp -R experiments/results "$dir/experiments/results"
  cp experiments/*.py experiments/*.sh experiments/*.js "$dir/experiments/"
  # the edge-case suite of 27 Sep (RESEARCH_NOTES 23): its code, design and analyses, results, queue and arena logs
  mkdir -p "$dir/experiments/edge"; cp experiments/edge/*.py experiments/edge/*.sh experiments/edge/*.md experiments/edge/*.json experiments/edge/*.tsv "$dir/experiments/edge/" 2> /dev/null
  cp -R experiments/results_edge "$dir/experiments/results_edge"
  [ -d logs/edge ] && cp -R logs/edge "$dir/logs/edge"; [ -d logs/edge_arena ] && cp -R logs/edge_arena "$dir/logs/edge_arena"
  cp -R brain/flybrain brain/run_brain.py brain/tests "$dir/brain/"; rm -rf "$dir/brain/flybrain/__pycache__" "$dir/brain/tests/__pycache__" "$dir/experiments/__pycache__"
  mkdir -p "$dir/bot"; cp bot/*.js bot/package.json "$dir/bot/"
  for f in README.md LICENSE RESEARCH_NOTES.md PAPER.md WHATS_LEFT_FLY.md reproduce.sh run.sh; do [ -f "$f" ] && cp "$f" "$dir/"; done
  mkdir -p "$dir/paper"; cp paper/*.tex paper/*.py paper/build.sh "$dir/paper/"; [ -f paper/flycraft.pdf ] && cp paper/flycraft.pdf "$dir/paper/"; cp -R paper/figures "$dir/paper/figures" 2> /dev/null
  # every per-tick arena log (csv), every experiment stdout (out) and every memory / probe readout (json); no spike dumps
  find logs -maxdepth 1 \( -name '*.csv' -o -name '*.out' -o -name '*.json' -o -name '*.md' \) -exec cp {} "$dir/logs/" \;
  [ -d logs/discarded ] && cp -R logs/discarded "$dir/logs/discarded"     # the lost trials and why (README.md inside)
  ( cd "$dir" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 shasum -a 256 > MANIFEST.sha256 )
  tar -czf "${dir}.tar.gz" -C release "flycraft_${stamp}"
  echo "wrote ${dir}.tar.gz ($(du -h "${dir}.tar.gz" | cut -f1); $(wc -l < "$dir/MANIFEST.sha256") files; data/ is not included — see README, 'Running it')"
}
case "${1:-list}" in
  list) list ;;
  archive) archive ;;
  all) for g in core-check anchors odor-code social-map gain shuffle sensitivity odor-dose contact-stop noise-floor precontact state conditioning expression figures; do run "$g"; done ;;
  arena) for g in arena-encounters arena-learning; do run "$g"; done ;;   # arena-replication is run on its own (it repeats three arena-encounters series)
  *) for g in "$@"; do run "$g"; done ;;
esac
