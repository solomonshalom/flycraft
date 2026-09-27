#!/usr/bin/env python3
"""Talk to a running brain over its websocket (a second client next to the body).

  python experiments/brainctl.py --port 8765 freeze      # plasticity off (memory kept, no further change)
  python experiments/brainctl.py --port 8765 unfreeze    # plasticity on
  python experiments/brainctl.py --port 8765 memory      # KC->MBON weight fraction per MBON compartment (json)
  python experiments/brainctl.py --port 8765 reset       # membrane state to rest (weights untouched)
  python experiments/brainctl.py --port 8765 probe --odors ester,vinegar   # graded memory readout: KC->MBON drive per compartment for each odor class (idle brain only)
"""
import argparse, asyncio, json
import websockets

ap = argparse.ArgumentParser()
ap.add_argument("cmd", choices=["freeze", "unfreeze", "memory", "reset", "probe"])
ap.add_argument("--odors", default="ester,vinegar"); ap.add_argument("--hz", type=float, default=150); ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--port", type=int, default=8765)
ap.add_argument("--host", default="127.0.0.1")
a = ap.parse_args()
msg = {"freeze": {"cmd": "plasticity", "on": False}, "unfreeze": {"cmd": "plasticity", "on": True},
       "memory": {"cmd": "memory"}, "reset": {"cmd": "reset"},
       "probe": {"cmd": "probe", "odors": a.odors.split(","), "hz": a.hz, "ms": a.ms}}[a.cmd]


async def main():
    async with websockets.connect(f"ws://{a.host}:{a.port}", max_size=8 * 1024 * 1024) as ws:
        await ws.send(json.dumps(msg))
        print(await ws.recv())

asyncio.run(main())
