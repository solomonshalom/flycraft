#!/usr/bin/env bash
# run_guarded.sh — run a list of steps one at a time, never two at once, with the machine's memory watched
# (RESEARCH_NOTES 23). Made for a 16 GB laptop that other work shares.
#
#   caffeinate -i experiments/run_guarded.sh STEPFILE [DONE_DIR]
#
# STEPFILE has one step per line:  name <TAB> min_free_pct <TAB> command   (blank lines and # comments are skipped).
# The file is re-read before every step, so steps may be appended while the queue runs.
#   - Before a step starts, the queue waits until macOS reports at least min_free_pct % of memory free.
#   - While a step runs, a sampler writes the step's own memory (the physical footprint of its whole process tree), the system's free
#     memory, swap and load to logs/guarded_mem.tsv every 10 s, and the step's peak to logs/guarded_peaks.tsv.
#   - If free memory falls below CRIT_PCT (default 6 %) the step is paused (SIGSTOP on its process group) until it is back
#     above RESUME_PCT (default 15 %) or PAUSE_MAX seconds have passed (default 1200), so the queue never adds to a
#     memory emergency it did not start. Pauses are logged.
#   - A finished step leaves DONE_DIR/<name>; a failed one is retried once after the memory gate, then leaves
#     DONE_DIR/<name>.failed and the queue moves on. Running the queue again resumes after the last finished step.
set -uo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.pyenv/shims:$PATH"                 # Python 3.12.8 + numba 0.65.1 (versions in README, "Running it")
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-6} PYTHONWARNINGS=ignore
STEPS=${1:?usage: run_guarded.sh STEPFILE [DONE_DIR]}; DONE=${2:-logs/guarded_done}; mkdir -p "$DONE" logs
CRIT_PCT=${CRIT_PCT:-6}; RESUME_PCT=${RESUME_PCT:-15}; PAUSE_MAX=${PAUSE_MAX:-1200}
MEMLOG=${MEMLOG:-logs/guarded_mem.tsv}; PEAKS=${PEAKS:-logs/guarded_peaks.tsv}
[ -f "$MEMLOG" ] || printf 'time\tstep\ttree_rss_mb\tfree_pct\tswap_used_mb\tload1\tpaused\n' > "$MEMLOG"
[ -f "$PEAKS" ] || printf 'step\tstart\tend\tseconds\tpeak_tree_rss_mb\tmin_free_pct\tpauses\tstatus\n' > "$PEAKS"
log() { echo "== $* $(date '+%F %T')"; }
free_pct() { memory_pressure 2> /dev/null | awk -F': ' '/free percentage/ {gsub("%", "", $2); print $2+0}'; }
swap_mb() { sysctl -n vm.swapusage | awk '{for (i = 1; i <= NF; i++) if ($i == "used") {v = $(i + 2); sub("M", "", v); print int(v)}}'; }
load1() { sysctl -n vm.loadavg | awk '{print $2}'; }
tree_pids() {   # process $1 and all its descendants, as "-pid A -pid B ..." for top
  ps -A -o pid= -o ppid= | awk -v root="$1" '{p[$1] = $2} END {
    for (x in p) { y = x; while (y != "" && y != 0 && y != 1) { if (y == root) { printf " -pid %s", x; break } y = p[y] } } }'
}
tree_rss_mb() {   # summed physical footprint (MB) of process $1 and its descendants: top's MEM, which unlike ps's RSS
                  # counts pages the memory compressor has squeezed (RSS under-reads a sleeping numpy array ~30x)
  local pids; pids=$(tree_pids "$1"); [ -z "$pids" ] && { echo 0; return; }
  top -l 1 $pids -stats pid,mem 2> /dev/null | awk '$1 ~ /^[0-9]+$/ {v = $2; u = substr(v, length(v)); sub(/[BKMG+-]+$/, "", v)
    s += (u == "G") ? v * 1024 : (u == "K") ? v / 1024 : (u == "B") ? v / 1048576 : v} END {printf "%d", s}'
}
wait_for_memory() {   # $1 = min free %
  local need=$1 f waited=0
  while f=$(free_pct); [ "${f:-0}" -lt "$need" ]; do
    [ $((waited % 600)) -eq 0 ] && log "waiting for memory: ${f}% free, need ${need}%"
    sleep 30; waited=$((waited + 30))
  done
}
run_step() {   # $1 name, $2 command; returns the command's exit status
  local name=$1 cmd=$2 start peak=0 minfree=100 pauses=0 paused=0 pstart=0 rc rss f
  start=$(date +%s)
  set -m; bash -c "$cmd" > "${OUTDIR:-logs}/guarded_${name}.out" 2>&1 & local pid=$!; set +m
  while kill -0 "$pid" 2> /dev/null; do
    rss=$(tree_rss_mb "$pid"); f=$(free_pct); f=${f:-100}
    [ "$rss" -gt "$peak" ] && peak=$rss; [ "$f" -lt "$minfree" ] && minfree=$f
    if [ "$paused" = 0 ] && [ "$f" -lt "$CRIT_PCT" ]; then
      kill -STOP -- "-$pid" 2> /dev/null; paused=1; pstart=$(date +%s); pauses=$((pauses + 1)); log "PAUSED $name: ${f}% free"
    elif [ "$paused" = 1 ] && { [ "$f" -ge "$RESUME_PCT" ] || [ $(($(date +%s) - pstart)) -ge "$PAUSE_MAX" ]; }; then
      kill -CONT -- "-$pid" 2> /dev/null; paused=0; log "resumed $name: ${f}% free"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$name" "$rss" "$f" "$(swap_mb)" "$(load1)" "$paused" >> "$MEMLOG"
    sleep 10
  done
  wait "$pid"; rc=$?
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$(date -r "$start" '+%F %T')" "$(date '+%F %T')" $(($(date +%s) - start)) \
    "$peak" "$minfree" "$pauses" "$([ $rc = 0 ] && echo ok || echo "rc=$rc")" >> "$PEAKS"
  return $rc
}
log "guarded queue: $STEPS -> $DONE (threads $NUMBA_NUM_THREADS; $(free_pct)% free; python $(python3 -c 'import sys, numba; print(sys.version.split()[0], "numba", numba.__version__)'))"
while :; do
  next=""
  while IFS=$'\t' read -r name need cmd; do
    case "$name" in ''|'#'*) continue ;; esac
    [ -f "$DONE/$name" ] || [ -f "$DONE/$name.failed" ] || { next=$name; break; }
  done < "$STEPS"
  [ -z "$next" ] && break
  line=$(awk -F'\t' -v n="$next" '$1 == n {print; exit}' "$STEPS"); need=$(echo "$line" | cut -f2); cmd=$(echo "$line" | cut -f3-)
  ok=0
  for attempt in 1 2; do
    wait_for_memory "$need"
    log "$next (attempt $attempt; $(free_pct)% free, load $(load1))"
    if run_step "$next" "$cmd"; then ok=1; break; fi
    log "$next FAILED (attempt $attempt; logs/guarded_${next}.out)"
  done
  if [ $ok = 1 ]; then touch "$DONE/$next"; log "$next ok"; else touch "$DONE/$next.failed"; fi
done
log "queue finished ($(ls "$DONE" | grep -c -v failed) ok, $(ls "$DONE" | grep -c failed) failed)"
