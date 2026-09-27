#!/usr/bin/env bash
# Build the paper: copy the print figures from ../experiments/results and compile (tectonic if present, else pdflatex twice).
# The arena table (tables_arena.tex) is written by: python3 experiments/replication_stats.py --tex paper/tables_arena.tex
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p figures
for f in fig3_print_encounters fig_replication; do
  [ -f "../experiments/results/$f.pdf" ] && cp "../experiments/results/$f.pdf" figures/
done
for f in fig_deciders; do
  [ -f "../experiments/results_edge/figures/$f.pdf" ] && cp "../experiments/results_edge/figures/$f.pdf" figures/
done
if command -v tectonic > /dev/null; then tectonic --keep-logs flycraft.tex; else pdflatex flycraft.tex && pdflatex flycraft.tex; fi
