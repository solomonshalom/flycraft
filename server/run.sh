#!/usr/bin/env bash
# Start the Paper server in the foreground (Ctrl-C to stop). Logs in logs/latest.log
cd "$(dirname "$0")"
exec java -Xms512M -Xmx1536M -XX:+UseG1GC -jar paper.jar --nogui
