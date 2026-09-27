#!/usr/bin/env python3
"""Does vision reach the descending neurons once the optic lobe is neural (flyvis) instead of uniform LIF?

Each stimulus is preceded by an adaptation period in which the first frame is held (so measuring a static
pattern does not measure its onset flash), then measured for --ms. Stimuli: grey, static grating, gratings
drifting left/right, a fast loom (expanding dark disc over 300 ms, then held), a flash. We read the optic-lobe
drive by cell type, the lobula plate tangential cells (HS / VS), loom detectors (LC4, LPLC2), LC10, the giant
fiber and the turning / walking DNs.
  python brain/tests/vision_bridge.py [--ms 600] [--adapt-ms 1000] [--r-max 100]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder
from flybrain.vision import OpticLobe

ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="flywire"); ap.add_argument("--ms", type=float, default=600)
ap.add_argument("--adapt-ms", type=float, default=1000); ap.add_argument("--tick-ms", type=float, default=50); ap.add_argument("--r-max", type=float, default=100.0)
ap.add_argument("--adapt-tau", type=float, default=1.0)
a = ap.parse_args()
W = H = 24
cx = connectome.load(dataset=a.dataset)
senses = SensoryEncoder(cx, verbose=False); motor = MotorDecoder(cx, verbose=False)
sim = LIF(cx.W, LIFParams(w_syn=0.275 * cx.w_syn_scale), seed=0)
ol = OpticLobe(cx, senses, sim=sim, r_max=a.r_max, adapt_tau=a.adapt_tau)
s = cx.select
OUT = {"HS": s(cell_type=r"^HS[ENS]"), "VS": s(cell_type=r"^VS"), "LC4": s(cell_type=r"^LC4$"), "LPLC2": s(cell_type=r"^LPLC2$"), "LPLC1": s(cell_type=r"^LPLC1$"),
       "LC10": s(cell_type=r"^LC10"), "LC16": s(cell_type=r"^LC16$"), "LC6": s(cell_type=r"^LC6$"), "VPN all": s(super_class="^visual_projection$"),
       "GF": s(cell_type=r"^DNp01$"), "DNa L": motor.groups["turn_L"], "DNa R": motor.groups["turn_R"], "DNp09": s(cell_type=r"^DNp09$"),
       "MDN": s(cell_type=r"^MDN$"), "DN all": s(super_class="^descending$")}
OUT = {k: v for k, v in OUT.items() if len(v)}
ct = cx.neurons.cell_type.fillna("").to_numpy()
TYPES = ["L1", "L2", "Mi1", "Tm3", "Tm9", "T4a", "T4b", "T5a", "T5b", "TmY3"]
yy, xx = np.mgrid[0:H, 0:W]

def frame(kind, i, n):
    img = np.full((H, W), 0.5, np.float32)
    if kind == "grating static": img[:] = 0.5 + 0.45 * np.sign(np.sin(2 * np.pi * xx / 6))
    elif kind == "grating left": img[:] = 0.5 + 0.45 * np.sign(np.sin(2 * np.pi * (xx + i) / 6))
    elif kind == "grating right": img[:] = 0.5 + 0.45 * np.sign(np.sin(2 * np.pi * (xx - i) / 6))
    elif kind == "loom fast":       # dark disc expanding to full size in 6 frames (300 ms), then held
        r = 1 + 11 * min(i, 6) / 6; img[((xx - W / 2) ** 2 + (yy - H / 2) ** 2) < r * r] = 0.05
    elif kind == "flash":
        img[:] = 0.9 if i >= 0 else 0.5
    return img

for kind in ["grey", "grating static", "grating left", "grating right", "loom fast", "flash"]:
    sim.reset(); sim.seed(0); ol.reset()
    n_ad = int(a.adapt_ms / a.tick_ms); n = int(a.ms / a.tick_ms)
    # adaptation: hold the first frame of the stimulus (grey for the moving/loom/flash cases so their onset is inside the window)
    first = frame(kind, 0, n) if kind == "grating static" else np.full((H, W), 0.5, np.float32)
    for _ in range(n_ad):
        eyes = {"L": {"w": W, "h": H, "px": first.ravel().tolist()}, "R": {"w": W, "h": H, "px": first.ravel().tolist()}}
        idx, rate = ol.process_sync(eyes); sim.set_drive(idx, rate); sim.run(a.tick_ms)
    counts = np.zeros(cx.n, np.int32); tdrive = np.zeros(cx.n); t_ol = t_sim = 0.0
    for i in range(n):
        img = frame(kind, i, n)
        eyes = {"L": {"w": W, "h": H, "px": img.ravel().tolist()}, "R": {"w": W, "h": H, "px": img.ravel().tolist()}}
        t0 = time.perf_counter(); idx, rate = ol.process_sync(eyes); t_ol += time.perf_counter() - t0
        tdrive[idx] += rate / n
        sim.set_drive(idx, rate)
        t0 = time.perf_counter(); c, _ = sim.run(a.tick_ms); t_sim += time.perf_counter() - t0; counts += c
    sec = a.ms / 1000
    r = {k: counts[v].sum() / len(v) / sec for k, v in OUT.items()}
    print(f"{kind:15s} drive {tdrive[ol.covered].mean():5.1f} Hz [" + " ".join(f"{t} {tdrive[ct == t].mean():4.1f}" for t in TYPES) + "]")
    print(f"{'':15s} " + " ".join(f"{k} {r[k]:5.1f}" for k in OUT) + f" | active {(counts > 0).mean()*100:.1f}% | optic lobe {t_ol/n*1000:.0f} ms/tick, brain {t_sim/n*1000:.0f} ms/tick", flush=True)
