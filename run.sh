#!/usr/bin/env bash
# Convenience launcher.  Open three terminals (or use experiments/run_pair.sh):
#   ./run.sh server                          # Paper 1.20.4, offline mode, localhost:25565 (superflat arena)
#   ./run.sh wild                            # second server: generated terrain world, localhost:25566
#   ./run.sh brain fly1 8765 off             # brain: name, ws port, plasticity off|mb
#   ./run.sh bot   fly1 8765 3007 --build-arena   # body: name, brain port, viewer port, extra bot args
#   ./run.sh assistant flock wild fly1        # research assistant: trial label, world, fly to follow (+ extra args)
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
  server) exec server/run.sh ;;
  wild)   cd server/wild 2>/dev/null || { echo "run ACCEPT_EULA=1 server/setup_wild.sh first"; exit 1; }; exec java -Xms1G -Xmx2G -XX:+UseG1GC -jar ../paper.jar --nogui ;;
  brain)  shift; NAME=${1:-fly1}; PORT=${2:-8765}; PL=${3:-off}; shift 3 || true
          exec python3 brain/run_brain.py --name "$NAME" --port "$PORT" --plasticity "$PL" "$@" ;;
  bot)    shift; NAME=${1:-fly1}; PORT=${2:-8765}; VIEW=${3:-3007}; shift 3 || true
          exec node bot/bot.js --name "$NAME" --brain "ws://127.0.0.1:$PORT" --viewer "$VIEW" "$@" ;;
  assistant) shift; TRIAL=${1:-live}; WORLD=${2:-wild}; FOLLOW=${3:-nearest}; shift 3 || true
          exec python3 assistant/assistant.py --trial "$TRIAL" --world "$WORLD" --follow "$FOLLOW" "$@" ;;
  *) sed -n 2,8p "$0"; exit 1 ;;
esac
