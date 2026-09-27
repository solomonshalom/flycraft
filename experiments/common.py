"""Shared definitions for the experiment scripts: input groups, output groups, state neurons, trial runner.

Every group is a regex over the annotation table (see connectome.select); groups that are empty in a dataset
are dropped, so the same script runs on the female (FlyWire) and the male (MaleCNS).
"""
from __future__ import annotations

import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brain"))
import numpy as np, pandas as pd
from flybrain import connectome
from flybrain.lif import LIF, LIFParams

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RES, exist_ok=True)

# Shiu et al. 2024 anchor neuron (v630 id, unchanged in v783): MN9, proboscis rostrum protractor motor neuron.
SHIU_MN9 = [720575940660219265]
SHIU_SUGAR = [720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345, 720575940617000768,
              720575940630797113, 720575940632889389, 720575940621754367, 720575940621502051, 720575940640649691,
              720575940639332736, 720575940616885538, 720575940639198653, 720575940620900446, 720575940617937543,
              720575940632425919, 720575940633143833, 720575940612670570, 720575940628853239, 720575940629176663,
              720575940611875570]


def input_groups(cx):
    s = cx.select
    G = {
        "cVA (Or67d/DA1)": [s(cell_type=r"^ORN_DA1$")],
        "cVA-long (Or65a/DL3)": [s(cell_type=r"^ORN_DL3$")],
        "Or47b (VA1v)": [s(cell_type=r"^ORN_VA1v$")],
        "Or88a (VA1d)": [s(cell_type=r"^ORN_VA1d$")],
        "Or83c (DC3)": [s(cell_type=r"^ORN_DC3$")],
        "all pheromone ORNs": [s(cell_class="^olfactory$", cell_sub_class="pheromone")],
        "food odor": [s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$")],
        "CO2 (V)": [s(cell_type=r"^ORN_V$")],
        "aversive odor (DA2/DL4)": [s(cell_type=r"^ORN_(DA2|DL4)$")],
        "song/sound (JO-A)": [s(cell_type=r"^JO-A")],
        "sound (JO-B)": [s(cell_type=r"^JO-B")],
        "wind/gravity (JO-CE)": [s(cell_class="^mechanosensory", cell_sub_class="wind_gravity")],
        "touch (all head bristles)": [s(cell_type=r"^BM_")],
        "touch (antennal bristles)": [s(cell_type=r"^BM_Ant")],
        "touch (eye bristles)": [s(cell_type=r"^BM_InOm")],
        "sugar GRNs": [s(cell_class="^gustatory$", cell_sub_class="sugar/water|labellar bristle")],
        "bitter GRNs": [s(cell_class="^gustatory$", cell_sub_class="^bitter$")],
        "cVA + food": [s(cell_type=r"^ORN_DA1$"), s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$")],
        "cVA + touch": [s(cell_type=r"^ORN_DA1$"), s(cell_type=r"^BM_")],
        "cVA + song": [s(cell_type=r"^ORN_DA1$"), s(cell_type=r"^JO-A")],
        "Or47b + song": [s(cell_type=r"^ORN_VA1v$"), s(cell_type=r"^JO-A")],
        "Or47b + touch": [s(cell_type=r"^ORN_VA1v$"), s(cell_type=r"^BM_")],
        "food + touch": [s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$"), s(cell_type=r"^BM_")],
        "CO2 + touch": [s(cell_type=r"^ORN_V$"), s(cell_type=r"^BM_")],
        "pheromones + song + touch": [s(cell_class="^olfactory$", cell_sub_class="pheromone"), s(cell_type=r"^JO-A"), s(cell_type=r"^BM_")],
        "cVA + sugar": [s(cell_type=r"^ORN_DA1$"), s(cell_class="^gustatory$", cell_sub_class="sugar/water|labellar bristle")],
        # contact pheromone channel (leg ppk23/ppk25 GRNs; labeled in MaleCNS only)
        "contact pheromone (ppk23/25)": [s(any_of={"receptor_type": "ppk23|ppk25"})],
        "ppk23 only (male CHC)": [s(any_of={"receptor_type": "ppk23"})],
        "ppk25 only (female CHC)": [s(any_of={"receptor_type": "ppk25"})],
        "cVA + contact pheromone": [s(cell_type=r"^ORN_DA1$"), s(any_of={"receptor_type": "ppk23|ppk25"})],
        "ppk25 + touch": [s(any_of={"receptor_type": "ppk25"}), s(cell_type=r"^BM_")],
        "all pheromones + contact + touch": [s(cell_type=r"^ORN_(DA1|VA1v|VA1d|DL3|DC3)$"), s(any_of={"receptor_type": "ppk23|ppk25"}), s(cell_type=r"^BM_")],
    }
    return {k: v for k, v in G.items() if all(len(g) for g in v)}


def output_groups(cx):
    s = cx.select
    G = {
        "DNa L": s(cell_type=r"^DNa0[12]$", side="^left$"), "DNa R": s(cell_type=r"^DNa0[12]$", side="^right$"),
        "DNp09": s(cell_type=r"^DNp09$"), "MDN back": s(cell_type=r"^MDN$"), "GF jump": s(cell_type=r"^DNp01$"),
        "DN all": s(super_class="^descending$"),
        "pC1a recept": s(cell_type=r"^pC1a$"), "pC1b/c": s(cell_type=r"^pC1[bc]$"), "pC1d/e aggr": s(cell_type=r"^pC1[de]$"),
        "aIPg aggr": s(hemibrain_type=r"^aIPg"), "aSP-g": s(cell_type=r"^aSP-g"),
        "vpoEN/DN accept": s(any_of={"cell_type": r"^vpoEN$|^DNp37$"}), "DNp13 reject": s(cell_type=r"^DNp13$"),
        "oviDN egg": s(cell_type=r"^oviDN"), "mAL": s(cell_class="^mAL$"),
        "SAG": s(hemibrain_type=r"^SAG$"), "IPC": s(cell_type=r"^IPC$"),
        "feed MNs": s(any_of={"cell_sub_class": r"proboscis_motor_neuron|ingestion_motor_neuron|^pm$", "cell_type": r"^MN9$"}),
        "MN9": (cx.by_root_ids(SHIU_MN9) if cx.dataset == "flywire" else s(cell_type=r"^MN9$")),
        "song MNs": s(cell_type=r"^(ps1|i1|i2|hg[0-9]) MN"), "wing MNs": s(super_class="^motor$", cell_sub_class="^wm$"),
        "leg MNs": s(super_class="^motor$", cell_sub_class="^(fl|ml|hl)$"),
        "PAM (reward DA)": s(cell_class="^DAN$", cell_type=r"^PAM"), "PPL1 (punish DA)": s(cell_class="^DAN$", cell_type=r"^PPL1"),
        "MBON": s(cell_class="^MBON$"), "KC": s(cell_class="^Kenyon_Cell$"),
        "P1/pC1 male": s(cell_type=r"^pC1_|^P1_"), "pIP10 song cmd": s(cell_type=r"^pIP10"), "vPR6 song": s(cell_type=r"^vPR6"),
        "TN1 song": s(cell_type=r"^TN1"), "aSP22": s(cell_type=r"^aSP22"),
    }
    return {k: v for k, v in G.items() if len(v)}


def state_groups(cx):
    """Neurons whose tonic activity encodes an internal state in the real fly (all labeled in the connectome)."""
    s = cx.select
    G = {
        "virgin (SAG tonic)": s(hemibrain_type=r"^SAG$"),                    # sex-peptide pathway; active in virgins, silenced by mating
        "fed (IPC tonic)": s(cell_type=r"^IPC$"),                            # insulin-producing cells; active when fed
        "fed (DH44 tonic)": s(cell_type=r"^DH44$"),                          # internal sugar sensor
        "hungry (NPF tonic)": s(cell_type=r"^NPFL1-I$|^DNp29$"),             # NPF neurons; starvation raises NPF signalling
        "SIFa tonic": s(cell_type=r"^DNc0[12]$"),                            # SIFamide: hunger/arousal modulator
        "AstA tonic": s(cell_type=r"^AstA1$"),                               # allatostatin-A: satiety
        "aroused female (pC1a-c tonic)": s(cell_type=r"^pC1[abc]$"),         # female receptivity hub
        "aggressive female (pC1d/e tonic)": s(cell_type=r"^pC1[de]$"),       # female aggression hub
        "aggressive female (aIPg tonic)": s(hemibrain_type=r"^aIPg"),
        "courting male (P1/pC1 tonic)": s(cell_type=r"^pC1_|^P1_"),           # male courtship command cluster
    }
    return {k: v for k, v in G.items() if len(v)}


def make_sim(cx, gain=1.0, noise_hz=0.0, dt=0.2, legacy=False, seed=0):
    return LIF(cx.W, LIFParams(dt=dt, noise_hz=noise_hz, w_syn=0.275 * cx.w_syn_scale * gain, legacy=legacy), seed=seed)


def drive_of(groups, hz):
    """(idx, rate) for a list of (group_indices, hz) or a list of groups at one hz."""
    idx, rate = [], []
    for g in groups:
        if isinstance(g, tuple):
            gi, ghz = g
        else:
            gi, ghz = g, hz
        if len(gi):
            idx.append(np.asarray(gi)); rate.append(np.full(len(gi), ghz, np.float32))
    if not idx:
        return np.zeros(0, np.int64), np.zeros(0, np.float32)
    return np.concatenate(idx), np.concatenate(rate)


def run_trials(sim, groups, hz, ms, seeds, outputs, extra=None):
    """Run `seeds` independent trials of one condition; return list of row dicts with output rates (Hz)."""
    idx, rate = drive_of(groups, hz)
    rows = []
    for seed in range(seeds):
        sim.seed(seed); sim.reset(); sim.set_drive(idx, rate)
        t0 = time.perf_counter(); counts, _ = sim.run(ms); wall = time.perf_counter() - t0
        row = {"seed": seed, "n_driven": int(len(idx)), "total_spikes": int(counts.sum()),
               "active_frac": float((counts > 0).mean()), "wall_s": round(wall, 2)}
        if extra:
            row.update(extra)
        for k, v in outputs.items():
            row[k] = float(counts[v].sum() / len(v) / (ms / 1000)) if len(v) else float('nan')
        rows.append(row)
    return rows


def summarize(rows, keys):
    d = pd.DataFrame(rows)
    return {k: (d[k].mean(), d[k].std()) for k in keys if k in d}


def fmt(m, sd=None):
    return f"{m:6.1f}" if sd is None else f"{m:6.1f}±{sd:<4.1f}"
