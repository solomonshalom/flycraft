#!/usr/bin/env python3
"""Export a connectome + named neuron groups as plain npz so brian2_reference.py (numpy-only venv) can use them.

  python brain/tests/export_for_brian2.py --dataset flywire --out /path/flywire_export.npz
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from flybrain import connectome
from flybrain.senses import SensoryEncoder
from flybrain.motor import MotorDecoder

ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="flywire"); ap.add_argument("--out", required=True)
a = ap.parse_args()
cx = connectome.load(dataset=a.dataset)
senses = SensoryEncoder(cx, verbose=False); motor = MotorDecoder(cx, verbose=False)
W = cx.W.tocsr(); W.sort_indices()
groups = {}
for k in ("grn_sugar", "grn_bitter", "orn_cva", "orn_food", "bristle", "jo_sound", "jo_wind", "orn_co2"):
    groups["in_" + k] = senses.groups[k]
for k in ("feed", "turn_L", "turn_R", "jump", "back", "aggression", "dn_all", "mb_kc", "mb_dan", "mb_mbon"):
    groups["out_" + k] = motor.groups[k]
groups["out_DNp13"] = cx.select(cell_type=r"^DNp13$")
groups["out_PPL1"] = cx.select(cell_class="^DAN$", cell_type=r"^PPL1")
groups["out_PAM"] = cx.select(cell_class="^DAN$", cell_type=r"^PAM")
np.savez(a.out, indptr=W.indptr.astype(np.int64), indices=W.indices.astype(np.int64), data=W.data.astype(np.float32),
         w_syn_scale=cx.w_syn_scale, n=cx.n, **{k: np.asarray(v, dtype=np.int64) for k, v in groups.items()})
print("wrote", a.out, {k: len(v) for k, v in groups.items()})
