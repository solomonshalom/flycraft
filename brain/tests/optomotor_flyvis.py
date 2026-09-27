#!/usr/bin/env python3
"""Optomotor test with the neural optic lobe: a grating drifting left vs right across both eyes.

A real fly turns with wide-field motion (optomotor response): motion to its left -> left turn. With flyvis
driving the optic-lobe neurons, does the turning-DN asymmetry (DNa L - R) follow the motion direction, and
with which sign? Also reports HS/VS and the visual drive level. Runs both eye_flip settings so the
retinotopic orientation assumption can be chosen from the result.
  python brain/tests/optomotor_flyvis.py [--ms 800] [--seeds 2]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder
from flybrain.vision import OpticLobe

ap = argparse.ArgumentParser(); ap.add_argument("--ms", type=float, default=800); ap.add_argument("--seeds", type=int, default=2)
ap.add_argument("--tick-ms", type=float, default=50); ap.add_argument("--r-max", type=float, default=100.0)
a = ap.parse_args()
W = H = 24
cx = connectome.load(dataset="flywire"); motor = MotorDecoder(cx, verbose=False); s = cx.select
OUT = {"HS": s(cell_type=r"^HS[ENS]"), "VS": s(cell_type=r"^VS"), "LC4": s(cell_type=r"^LC4$"), "GF": s(cell_type=r"^DNp01$"),
       "DNa L": motor.groups["turn_L"], "DNa R": motor.groups["turn_R"], "DNp09": s(cell_type=r"^DNp09$"), "DN all": s(super_class="^descending$")}

def grating(phase, period=6):
    col = np.arange(W); img = 0.5 + 0.45 * np.sign(np.sin(2 * np.pi * (col + phase) / period)); return np.tile(img, (H, 1)).astype(np.float32)

for flip_name, flip in [("default  L:(F,F) R:(T,F)", {"L": (False, False), "R": (True, False)}), ("mirrored L:(T,F) R:(F,F)", {"L": (True, False), "R": (False, False)})]:
    senses = SensoryEncoder(cx, eye_flip=flip, verbose=False)
    sim = LIF(cx.W, LIFParams(w_syn=0.275 * cx.w_syn_scale), seed=0)
    ol = OpticLobe(cx, senses, sim=sim, r_max=a.r_max, verbose=False)
    print(f"\n[{flip_name}]")
    for d, name in [(+1, "motion LEFT "), (-1, "motion RIGHT"), (0, "static      ")]:
        res = []
        for seed in range(a.seeds):
            sim.reset(); sim.seed(seed); ol.reset()
            counts = np.zeros(cx.n, np.int32); n = int(a.ms / a.tick_ms); phase = 0.0; t0 = time.perf_counter()
            for _ in range(n):
                phase += d * 1.0; img = grating(phase)
                eyes = {"L": {"w": W, "h": H, "px": img.ravel().tolist()}, "R": {"w": W, "h": H, "px": img.ravel().tolist()}}
                idx, rate = ol.process_sync(eyes); sim.set_drive(idx, rate); c, _ = sim.run(a.tick_ms); counts += c
            res.append({k: counts[v].sum() / len(v) / (a.ms / 1000) for k, v in OUT.items()} | {"drive": rate.mean(), "wall": time.perf_counter() - t0})
        m = {k: np.mean([r[k] for r in res]) for k in res[0]}
        print(f"  {name}: DNa L {m['DNa L']:5.1f}  R {m['DNa R']:5.1f}  (L-R {m['DNa L']-m['DNa R']:+5.1f}) | HS {m['HS']:5.1f} VS {m['VS']:5.1f} LC4 {m['LC4']:4.1f} GF {m['GF']:5.1f} DNp09 {m['DNp09']:4.1f} DN all {m['DN all']:4.2f} | drive {m['drive']:.1f} Hz ({m['wall']:.1f}s)", flush=True)
