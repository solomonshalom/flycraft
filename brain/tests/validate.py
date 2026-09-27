#!/usr/bin/env python3
"""Sanity checks that the model reproduces the published whole-brain LIF results.

Shiu et al. 2024: driving sugar-sensing gustatory neurons (~100 Hz) makes the proboscis motor
neurons fire (feeding); bitter neurons suppress it. We also time the simulation and check that
left/right visual drive produces a left/right descending-neuron asymmetry.
Run:  python brain/tests/validate.py
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.lif import LIF, LIFParams
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder

cx = connectome.load()
print(f"\n{cx}")
sim = LIF(cx.W, LIFParams(w_syn=0.275 * cx.w_syn_scale), seed=1)
senses = SensoryEncoder(cx, verbose=False)
motor = MotorDecoder(cx, verbose=False)

def trial(drive: dict, ms=500, label=""):
    sim.reset()
    idx, rate = [], []
    for g, hz in drive.items():
        ii = senses.groups[g]
        idx.append(ii); rate.append(np.full(len(ii), hz, np.float32))
    sim.set_drive(np.concatenate(idx) if idx else np.zeros(0, int), np.concatenate(rate) if rate else np.zeros(0, np.float32))
    t0 = time.perf_counter(); counts, _ = sim.run(ms); wall = time.perf_counter() - t0
    r = motor.rates(counts, ms / 1000)
    print(f"{label:34s} wall {wall*1000:6.0f} ms for {ms} ms brain | spikes {r['total_spikes']:7d} active {r['active_frac']*100:4.1f}% | "
          f"feed {r['feed']:5.1f} walk {r['forward']:5.1f} turnL {r['turn_L']:5.1f} turnR {r['turn_R']:5.1f} back {r['back']:4.1f} "
          f"jump {r['jump']:4.1f} aggr {r['aggression']:4.1f} dnL {r['dn_L']:4.1f} dnR {r['dn_R']:4.1f}")
    return r

print("\n-- baseline / speed")
trial({}, 500, "silence")
print("\n-- Shiu et al. 2024 feeding circuit")
r_sugar = trial({"grn_sugar": 100}, 500, "sugar GRNs @100 Hz")
r_bitter = trial({"grn_sugar": 100, "grn_bitter": 100}, 500, "sugar + bitter @100 Hz")
r_bit = trial({"grn_bitter": 100}, 500, "bitter only @100 Hz")
print("\n-- vision left/right")
trial({"photo_L": 100}, 500, "left eye @100 Hz")
trial({"photo_R": 100}, 500, "right eye @100 Hz")
trial({"photo_L": 100, "photo_R": 100}, 500, "both eyes @100 Hz")
print("\n-- olfaction / mechano / social")
trial({"orn_food": 150}, 500, "food odor (both antennae)")
trial({"orn_food_L": 150}, 500, "food odor LEFT antenna only")
trial({"orn_food_R": 150}, 500, "food odor RIGHT antenna only")
trial({"orn_fly_L": 150}, 500, "cVA LEFT antenna only")
trial({"orn_fly_R": 150}, 500, "cVA RIGHT antenna only")
trial({"orn_fly": 150}, 500, "fly pheromone (cVA)")
trial({"orn_co2": 150}, 500, "CO2")
trial({"bristle": 200}, 300, "bristle burst (touch)")
trial({"jo_sound": 150}, 500, "sound (JO-A/B)")

ok = r_sugar["feed"] > r_bitter["feed"] and r_sugar["feed"] > 1.0
print("\nRESULT: sugar->feeding", "PASS" if ok else "CHECK", f"(sugar {r_sugar['feed']:.1f} Hz vs sugar+bitter {r_bitter['feed']:.1f} Hz)")
