#!/usr/bin/env bash
# with_lock.sh CMD ... — run a short test that loads a connectome while a long queue shares the laptop (RESEARCH_NOTES 23).
# Only one such test runs at a time (a mkdir lock), and only when macOS reports at least MIN_FREE % (default 35) of memory
# free. Use it for every smoke test of the edge-case code; the queues themselves use run_guarded.sh.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PATH="$HOME/.pyenv/shims:$PATH" NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6} PYTHONWARNINGS=ignore
L=${TMPDIR:-/tmp}/flycraft_edge_smoke.lock
until mkdir "$L" 2> /dev/null; do sleep 5; done
trap 'rmdir "$L" 2> /dev/null' EXIT
free_pct() { memory_pressure 2> /dev/null | awk -F': ' '/free percentage/ {gsub("%", "", $2); print $2+0}'; }
while f=$(free_pct); [ "${f:-0}" -lt "${MIN_FREE:-35}" ]; do echo "with_lock: ${f}% free, waiting for ${MIN_FREE:-35}%" >&2; sleep 20; done
"$@"
