#!/usr/bin/env python3
"""Does any visual stimulus reach the descending neurons? Loom, flash, and photoreceptor sign."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder

W, H = 16, 12
cx = connectome.load()
senses = SensoryEncoder(cx, verbose=False)
motor = MotorDecoder(cx, verbose=False)
photo = np.concatenate([senses.groups["photo_L"], senses.groups["photo_R"]])
vpn = cx.select(super_class="^visual_projection$")
lc4 = cx.select(cell_type=r"^LC4$"); lplc2 = cx.select(cell_type=r"^LPLC2$"); t4 = cx.select(cell_type=r"^T4[a-d]$"); l1 = cx.select(cell_type=r"^L1$")
print(f"LC4 {len(lc4)}  LPLC2 {len(lplc2)}  T4 {len(t4)}  L1 {len(l1)}  visual projection neurons {len(vpn)}")

def make_sim(photo_sign):
    Wm = cx.W.copy()
    if photo_sign < 0:
        rows = np.zeros(cx.n, bool); rows[photo] = True
        Wm = Wm.tocsr()
        r = np.repeat(np.arange(cx.n), np.diff(Wm.indptr))
        Wm.data[rows[r]] *= -1
    return LIF(Wm, LIFParams(dt=0.5, noise_hz=0.0, w_syn=0.275 * cx.w_syn_scale), seed=3)

def frames(kind, n=20):
    for i in range(n):
        img = np.full((H, W), 0.8, np.float32)
        if kind == "loom":      # dark disc expanding at the centre of the RIGHT eye
            r = 0.5 + 5.5 * i / n
            yy, xx = np.mgrid[0:H, 0:W]
            imgR = img.copy(); imgR[((xx - W/2) ** 2 + (yy - H/2) ** 2) < r * r] = 0.05
            yield img, imgR
        elif kind == "flash_off":
            yield (img, img) if i < n // 2 else (img * 0.05, img * 0.05)
        elif kind == "flash_on":
            yield (img * 0.05, img * 0.05) if i < n // 2 else (img, img)
        elif kind == "bar_R":   # dark vertical bar sweeping across right eye
            imgR = img.copy(); imgR[:, min(W - 1, int(W * i / n))] = 0.05
            yield img, imgR
        else:
            yield img, img

def run(sim, kind, step_ms=50):
    sim.reset(); counts = np.zeros(cx.n, np.int32); tot = 0
    for L, R in frames(kind):
        obs = {"eyes": {"L": {"w": W, "h": H, "px": L.ravel().tolist()}, "R": {"w": W, "h": H, "px": R.ravel().tolist()}}}
        idx, rate = senses.encode(obs); sim.set_drive(idx, rate)
        c, _ = sim.run(step_ms); counts += c; tot += step_ms
    r = motor.rates(counts, tot / 1000)
    s = tot / 1000
    return r, {"LC4": counts[lc4].sum() / max(len(lc4), 1) / s, "LPLC2": counts[lplc2].sum() / max(len(lplc2), 1) / s,
               "T4": counts[t4].sum() / max(len(t4), 1) / s, "L1": counts[l1].sum() / max(len(l1), 1) / s,
               "VPN": counts[vpn].sum() / max(len(vpn), 1) / s}

for sign, label in [(+1, "photoreceptors as predicted (ACh, +)"), (-1, "photoreceptors histaminergic (-)")]:
    sim = make_sim(sign)
    print(f"\n== {label}")
    for kind in ["static", "loom", "flash_off", "flash_on", "bar_R"]:
        r, v = run(sim, kind)
        print(f"  {kind:9s} GF {r['jump']:5.1f}  DNa L/R {r['turn_L']:4.1f}/{r['turn_R']:4.1f}  DNp09 {r['forward']:4.1f}  popDN L/R {r['dn_L']:4.1f}/{r['dn_R']:4.1f} "
              f"| L1 {v['L1']:5.1f} T4 {v['T4']:5.1f} LC4 {v['LC4']:5.1f} LPLC2 {v['LPLC2']:5.1f} VPN {v['VPN']:5.1f} Hz | spikes {r['total_spikes']}")

print("\n== with 2 Hz background noise (baseline for inhibition to act on), histaminergic photoreceptors")
sim = make_sim(-1); sim.p.noise_hz = 2.0
for kind in ["static", "loom", "flash_off", "bar_R"]:
    r, v = run(sim, kind)
    print(f"  {kind:9s} GF {r['jump']:5.1f}  DNa L/R {r['turn_L']:4.1f}/{r['turn_R']:4.1f}  DNp09 {r['forward']:4.1f}  popDN L/R {r['dn_L']:4.1f}/{r['dn_R']:4.1f} "
          f"| L1 {v['L1']:5.1f} T4 {v['T4']:5.1f} LC4 {v['LC4']:5.1f} LPLC2 {v['LPLC2']:5.1f} VPN {v['VPN']:5.1f} Hz | spikes {r['total_spikes']}")
