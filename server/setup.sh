#!/usr/bin/env bash
# Download PaperMC 1.20.4 (runs on Java 17) and configure a local, offline-mode research server.
# Usage: ACCEPT_EULA=1 ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"
VER=1.20.4
UA="flycraft/0.1 (research; local server)"
if [ ! -f paper.jar ]; then
  echo "[server] fetching latest Paper $VER build ..."
  URL=$(curl -sL "https://fill.papermc.io/v3/projects/paper/versions/$VER/builds" -H "User-Agent: $UA" \
        | python3 -c 'import json,sys; b=json.load(sys.stdin)[0]; print(b["downloads"]["server:default"]["url"])')
  curl -L -o paper.jar "$URL" -H "User-Agent: $UA"
fi
if [ "${ACCEPT_EULA:-0}" = "1" ]; then
  echo "eula=true" > eula.txt   # https://aka.ms/MinecraftEULA
else
  echo "Set ACCEPT_EULA=1 to accept the Minecraft EULA (https://aka.ms/MinecraftEULA) and write eula.txt"; exit 1
fi
cat > server.properties <<'PROPS'
# flycraft research server — local only
online-mode=false
server-ip=127.0.0.1
server-port=25565
level-type=minecraft:flat
level-name=arena
gamemode=survival
difficulty=peaceful
pvp=true
spawn-protection=0
allow-flight=true
view-distance=8
simulation-distance=6
max-players=8
spawn-monsters=false
spawn-animals=false
spawn-npcs=false
generate-structures=false
enable-command-block=true
motd=flycraft arena
max-tick-time=-1
PROPS
# op the fly bots (offline-mode UUID = md5("OfflinePlayer:<name>") as UUIDv3)
python3 - <<'PY'
import hashlib, json, uuid
ops = []
for name in ["fly1", "fly2", "fly3", "fly4", "observer"]:
    h = bytearray(hashlib.md5(f"OfflinePlayer:{name}".encode()).digest())
    h[6] = (h[6] & 0x0F) | 0x30; h[8] = (h[8] & 0x3F) | 0x80
    ops.append({"uuid": str(uuid.UUID(bytes=bytes(h))), "name": name, "level": 4, "bypassesPlayerLimit": False})
json.dump(ops, open("ops.json", "w"), indent=2)
print("[server] ops.json written for", [o["name"] for o in ops])
PY
echo "[server] ready: ./run.sh"
