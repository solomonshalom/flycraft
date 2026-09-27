"""MaleCNS v1.0 (Janelia FlyEM, 2026, CC-BY; Berg et al. 2026, Cell, doi:10.1016/j.cell.2026.08.015) loaded into the
same Connectome structure as FlyWire.

Files (data/):
  body-annotations-male-cns-v1.0.feather      curated neuron annotations
  body-neurotransmitters-male-cns-v1.0.feather per-neuron NT predictions
  connectome-weights-male-cns-v1.0.feather    body -> body synapse counts (brain + VNC), all connections

Column mapping onto the FlyWire-style table used everywhere else:
  root_id=bodyId  cell_type=type  hemibrain_type=hemibrainType  cell_class=class  cell_sub_class=subclass
  super_class: descending_neuron->descending, *_sensory->sensory, vnc_motor->motor, ascending_neuron->ascending,
               visual_projection/visual_centrifugal kept, ol_intrinsic->optic, cb_intrinsic->central, vnc_intrinsic->vnc
  side: somaSide (fallback rootSide for sensory)  top_nt: consensus_nt (fallback predicted_nt)

Sign: inhibitory if the neuron's consensus transmitter is GABA or glutamate, excitatory otherwise (the MaleCNS
release gives one transmitter per neuron, not per-synapse fractions, so Shiu et al.'s majority-vote rule cannot
be applied literally; for neurons with a clear consensus the two rules coincide).

Density calibration: MaleCNS synapse detection is denser than FlyWire's. With all connections between traced
neurons, a male brain neuron receives on average 722 input synapses vs 391 for a FlyWire neuron. We scale the
per-synapse weight by the ratio (0.542) so that mean input per brain neuron matches the female model; nothing
else differs between the two sexes' models. (At the old >= 5-synapse threshold the ratio was 0.495.)
"""
from __future__ import annotations

import os, time
import numpy as np, pandas as pd, scipy.sparse as sp

from .connectome import Connectome, NT_SIGN, mean_input_synapses

ANNOT = "body-annotations-male-cns-v1.0.feather"
NT = "body-neurotransmitters-male-cns-v1.0.feather"
CONNS = "connectome-weights-male-cns-v1.0.feather"
NEURONS_CSV = "malecns_neurons.csv.gz"
BRAIN_SUPER = {"cb_intrinsic", "cb_sensory", "ol_intrinsic", "ol_sensory", "visual_projection", "visual_centrifugal",
               "descending_neuron", "ascending_neuron", "cb_motor", "cb_endocrine"}

SUPER = {"descending_neuron": "descending", "ascending_neuron": "ascending", "vnc_motor": "motor",
         "ol_sensory": "sensory", "cb_sensory": "sensory", "vnc_sensory": "sensory",
         "ol_intrinsic": "optic", "cb_intrinsic": "central", "vnc_intrinsic": "vnc",
         "visual_projection": "visual_projection", "visual_centrifugal": "visual_centrifugal",
         "endocrine": "endocrine", "sensory_ascending": "sensory_ascending"}
TRACED = {"Roughly traced", "Reviewed", "Prelim Roughly traced", "RT Hard to trace", "0.5assign", "Anchor"}


def _neuron_table(data_dir: str) -> pd.DataFrame:
    a = pd.read_feather(os.path.join(data_dir, ANNOT))
    a = a[a.statusLabel.isin(TRACED) & a.superclass.notna()].copy()
    nt = pd.read_feather(os.path.join(data_dir, NT)).set_index("body")
    a["top_nt"] = a.bodyId.map(nt.consensus_nt).fillna(a.bodyId.map(nt.predicted_nt)).fillna("acetylcholine").str.lower()
    a["top_nt_conf"] = a.bodyId.map(nt.predicted_nt_confidence)
    side = a.somaSide.fillna(a.rootSide).map({"L": "left", "R": "right", "M": "center"}).fillna("na")
    t = pd.DataFrame({
        "root_id": a.bodyId.astype(np.int64), "cell_type": a.type, "hemibrain_type": a.hemibrainType,
        "cell_class": a["class"], "cell_sub_class": a.subclass, "super_class": a.superclass.map(SUPER).fillna(a.superclass),
        "superclass_raw": a.superclass, "side": side, "top_nt": a.top_nt, "top_nt_conf": a.top_nt_conf,
        "flow": np.where(a.superclass.str.contains("sensory", na=False), "afferent",
                np.where(a.superclass.isin(["vnc_motor", "endocrine"]), "efferent", "intrinsic")),
        "dimorphism": a.dimorphism, "fru_dsx": a.fruDsx, "synonyms": a.synonyms, "flywire_type": a.flywireType,
        "entry_nerve": a.entryNerve, "instance": a.instance, "receptor_type": a.receptorType,
    })
    for c in ("pos_x", "pos_y", "pos_z"):
        t[c] = np.nan
    if "somaLocation" in a.columns:
        loc = a.somaLocation
        ok = loc.notna()
        try:
            xyz = np.array([list(v) if v is not None and len(v) == 3 else [np.nan] * 3 for v in loc.where(ok, None)], dtype=float)
            t["pos_x"], t["pos_y"], t["pos_z"] = xyz[:, 0], xyz[:, 1], xyz[:, 2]
        except Exception:
            pass
    return t.reset_index(drop=True)


def _female_density(data_dir: str) -> float:
    """Mean input synapses per neuron in the female model (same connection rule), for the calibration."""
    from . import connectome as cxmod
    fem = cxmod.load(data_dir, dataset="flywire")
    return mean_input_synapses(fem.W)


def _build_cache(data_dir: str, cache: str, min_syn: int) -> None:
    t0 = time.time()
    print(f"[malecns] building cache (connections >= {min_syn} synapses) ...", flush=True)
    t = _neuron_table(data_dir)
    t.to_csv(os.path.join(data_dir, NEURONS_CSV), index=False)
    root_ids = t.root_id.to_numpy()
    idx_of = pd.Series(np.arange(len(root_ids)), index=root_ids)
    c = pd.read_feather(os.path.join(data_dir, CONNS))
    cols = {k.lower(): k for k in c.columns}
    pre_c = next(cols[k] for k in cols if k in ("body_pre", "bodyid_pre", "pre", "bodypre", "pre_body", "pre_pt_root_id"))
    post_c = next(cols[k] for k in cols if k in ("body_post", "bodyid_post", "post", "bodypost", "post_body", "post_pt_root_id"))
    w_c = next(cols[k] for k in cols if k in ("weight", "syn_count", "count", "n_syn", "synapses"))
    df = c[[pre_c, post_c, w_c]].rename(columns={pre_c: "pre", post_c: "post", w_c: "syn"})
    df = df[(df.syn >= min_syn) & df.pre.isin(idx_of.index) & df.post.isin(idx_of.index)]
    pi = idx_of[df.pre.to_numpy()].to_numpy(); po = idx_of[df.post.to_numpy()].to_numpy()
    sign = t.top_nt.map(NT_SIGN).fillna(1.0).to_numpy(dtype=np.float32)
    W = sp.csr_matrix((df.syn.to_numpy(dtype=np.float32) * sign[pi], (pi, po)), shape=(len(root_ids),) * 2, dtype=np.float32)
    W.sum_duplicates()
    brain = np.flatnonzero(t.superclass_raw.isin(BRAIN_SUPER).to_numpy())
    male_density = mean_input_synapses(W, brain)
    female_density = _female_density(data_dir)
    scale = female_density / male_density
    np.savez_compressed(cache, root_ids=root_ids, indptr=W.indptr, indices=W.indices, data=W.data,
                        w_syn_scale=scale, male_density=male_density, female_density=female_density)
    print(f"[malecns] cached {os.path.basename(cache)}: {len(root_ids)} neurons, {W.nnz} connections, "
          f"{float(np.abs(W.data).sum()):.0f} synapses; input density brain neurons {male_density:.1f} vs female "
          f"{female_density:.1f} -> w_syn_scale {scale:.3f}; {time.time()-t0:.1f}s", flush=True)


def load(data_dir: str, min_syn: int = 1) -> Connectome:
    cache = os.path.join(data_dir, f"connectome_malecns_min{min_syn}.npz")
    if not os.path.exists(cache):
        _build_cache(data_dir, cache, min_syn)
    z = np.load(cache)
    root_ids = z["root_ids"]; n = len(root_ids)
    W = sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(n, n))
    csv = os.path.join(data_dir, NEURONS_CSV)
    if not os.path.exists(csv):
        _neuron_table(data_dir).to_csv(csv, index=False)
    t = pd.read_csv(csv, dtype={"root_id": np.int64}, low_memory=False)
    if len(t) != n or not np.array_equal(t.root_id.to_numpy(), root_ids):
        os.remove(cache); os.remove(csv)
        return load(data_dir, min_syn)
    for c in ("cell_type", "hemibrain_type", "cell_class", "cell_sub_class", "super_class", "side", "top_nt"):
        t[c] = t[c].astype("string").astype(object)
    idx_of = {int(r): i for i, r in enumerate(root_ids)}
    return Connectome(neurons=t, W=W, root_ids=root_ids, idx_of=idx_of, w_syn_scale=float(z["w_syn_scale"]),
                      dataset="malecns", variant=f"all_min{min_syn}")
