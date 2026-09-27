#!/usr/bin/env python3
"""Optomotor calibration: drift a vertical grating across both eyes and read the turning DNs.

A real fly turns in the direction of wide-field motion (optomotor response). We use this to
verify/choose the sign of the retinotopic horizontal axis (senses.eye_flip). Motion to the
fly's LEFT (image content moving toward column 0) should drive LEFT turning (DNa L > DNa R).
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder

W, H = 16, 12
cx = connectome.load()
sim = LIF(cx.W, LIFParams(dt=0.5, w_syn=0.275 * cx.w_syn_scale), seed=2)
motor = MotorDecoder(cx, verbose=False)

def grating(phase, period=4):
    col = np.arange(W)
    img = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (col + phase) / period))
    return np.tile(img, (H, 1)).astype(np.float32)

def run(senses, direction, ms=1000, step_ms=50, speed_cols_per_step=1.0):
    """direction +1: pattern moves toward column 0 (fly's LEFT in our image convention)."""
    sim.reset()
    counts = np.zeros(cx.n, np.int32)
    phase = 0.0
    for _ in range(int(ms / step_ms)):
        phase += direction * speed_cols_per_step
        img = grating(phase)
        obs = {"eyes": {"L": {"w": W, "h": H, "px": img.ravel().tolist()},
                        "R": {"w": W, "h": H, "px": img.ravel().tolist()}}}
        idx, rate = senses.encode(obs)
        sim.set_drive(idx, rate)
        c, _ = sim.run(step_ms)
        counts += c
    r = motor.rates(counts, ms / 1000)
    return r

for flip_name, flip in [("default  L:(F,F) R:(T,F)", {"L": (False, False), "R": (True, False)}),
                        ("mirrored L:(T,F) R:(F,F)", {"L": (True, False), "R": (False, False)}),
                        ("same     L:(F,F) R:(F,F)", {"L": (False, False), "R": (False, False)}),
                        ("same-T   L:(T,F) R:(T,F)", {"L": (True, False), "R": (True, False)})]:
    senses = SensoryEncoder(cx, eye_flip=flip, verbose=False)
    print(f"\n[{flip_name}]")
    for d, name in [(+1, "motion LEFT "), (-1, "motion RIGHT")]:
        t0 = time.perf_counter()
        r = run(senses, d)
        print(f"  {name}: DNa L {r['turn_L']:5.1f} Hz  R {r['turn_R']:5.1f} Hz  | pop DN L {r['dn_L']:4.1f} R {r['dn_R']:4.1f} | fwd {r['forward']:4.1f} | spikes {r['total_spikes']} ({time.perf_counter()-t0:.1f}s)")
