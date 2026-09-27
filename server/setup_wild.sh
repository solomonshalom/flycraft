#!/usr/bin/env bash
# A second server directory with a normal, generated world ("wild") for dropping flies into a big Minecraft world.
# Shares paper.jar with the arena server; runs on its own port so both can be up at once.
#   ACCEPT_EULA=1 server/setup_wild.sh [seed]      then   ./run.sh wild
set -euo pipefail
cd "$(dirname "$0")"
[ -f paper.jar ] || { echo "run server/setup.sh first (downloads paper.jar)"; exit 1; }
SEED=${1:-20260914}
mkdir -p wild
if [ "${ACCEPT_EULA:-0}" = "1" ]; then echo "eula=true" > wild/eula.txt; else echo "Set ACCEPT_EULA=1 to accept https://aka.ms/MinecraftEULA"; exit 1; fi
cat > wild/server.properties <<PROPS
# flycraft wild world — local only, generated terrain, animals on (CO2 sources), no hostile mobs
online-mode=false
server-ip=127.0.0.1
server-port=25566
level-type=minecraft:normal
level-name=world
level-seed=$SEED
gamemode=survival
difficulty=peaceful
pvp=true
spawn-protection=0
allow-flight=true
view-distance=10
simulation-distance=8
max-players=16
spawn-monsters=false
spawn-animals=true
spawn-npcs=true
generate-structures=true
enable-command-block=true
motd=flycraft wild
max-tick-time=-1
PROPS
cp ops.json wild/ops.json
cp -n whitelist.json wild/ 2>/dev/null || true
echo "[wild] ready: ./run.sh wild   (port 25566, seed $SEED)"
