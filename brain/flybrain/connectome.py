"""Load the FlyWire v783 connectome into a signed sparse matrix + neuron table.

Files (see data/):
  Supplemental_file1_neuron_annotations.tsv   labels (flyconnectome/flywire_annotations, Schlegel et al. 2024)
  shiu/Connectivity_783.parquet               Shiu et al. 2024's own v783 connection table (github.com/philshiu/
                                              Drosophila_brain_model): ALL 15.1 M connections (min 1 synapse,
                                              54.5 M synapses) with their per-neuron sign (+1 / -1). DEFAULT.
  proofread_connections_783.feather           Zenodo 10676866 (Dorkenwald et al. 2024), per (pre, post, neuropil);
                                              used for the `conn="zenodo"` variant (sign from the annotation
                                              table's top_nt; optional synapse-count threshold).

Shiu et al.'s published model uses every connection (their Methods give no threshold; their table has none) and
assigns each neuron a single sign: inhibitory if more than half of its output synapses are predicted GABAergic
or glutamatergic, excitatory otherwise (ACh, DA, OA, 5-HT). The first version of this code used the Zenodo
table with a >= 5-synapse threshold, which drops 37 % of all synapses; that variant is kept for the sensitivity
analysis (`conn="zenodo", min_syn=5`).

The first load builds a cache (connectome_783_<variant>.npz); later loads take a few seconds.

Two model options applied after loading (both off by default so that every earlier result is reproducible;
provenance is recorded in Connectome.variant, e.g. "shiu_min1+known+eln0.25"):

  signs="known"   (env FLYBRAIN_SIGNS)  Shiu et al.'s predicted majority-vote sign is overridden wherever the
                  annotation table records an immunohistochemically / transcriptomically KNOWN transmitter
                  (column known_nt, Schlegel et al. 2024: 88 k neurons). 11,010 neurons change sign, 9,200 of them
                  histaminergic photoreceptors (inhibitory in the fly; the prediction made them excitatory) and
                  16 antennal-lobe local neurons that are known GABA/glutamate but predicted otherwise.
  eln_scale=k     (env FLYBRAIN_ELN)    Multiplies the chemical output of the antennal lobe's excitatory local
                  neurons (the cholinergic eLNs, Shang et al. 2007; 150 neurons after the sign rule). In the
                  point-neuron model their 161 k synapses onto projection neurons make the antennal lobe a
                  runaway attractor: any single-glomerulus input activates 98 % of glomeruli (PNs ~80 Hz), so
                  every odor is the same odor to the rest of the brain (see RESEARCH_NOTES section 16). In the
                  fly, eLN->PN lateral excitation is weak and largely electrical (gap junctions: Yaksi & Wilson
                  2010; Huang et al. 2010), which a chemical-synapse sign rule cannot express. k = 0.25 keeps
                  glomerular identity (cognate glomerulus at 80-190 Hz, 19-25 % of glomeruli above 10 Hz, i.e.
                  PN tuning modestly broader than ORN tuning as in Olsen et al. 2007) and gives sparse Kenyon-
                  cell coding (1-5 % of KCs per odor). This is OUR constant; k = 1 is the published model.
  unclear_ln=...  (env FLYBRAIN_UNCLEAR_LN)  MaleCNS only: 67 of its 420 antennal-lobe local neurons carry the
                  transmitter prediction "unclear" (classifier confidence ~0.5) and default to excitatory, i.e.
                  they count as eLNs. "inhibitory" flips their sign, "silent" removes their output: a sensitivity
                  axis for the male's odor results (the female table has no unclear local neurons). Provenance
                  suffix "+unclearLN-inh" / "+unclearLN-off". `signs="known"` needs the annotation column
                  `known_nt`, which MaleCNS lacks: there the option applies nothing and adds no suffix.
"""
from __future__ import annotations

import os
import re
import time
import warnings
warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression")
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import scipy.sparse as sp

DATA_DIR = os.environ.get("FLYBRAIN_DATA", os.path.join(os.path.dirname(__file__), "..", "..", "data"))
ANNOT = "Supplemental_file1_neuron_annotations.tsv"
CONNS_ZENODO = "proofread_connections_783.feather"
CONNS_SHIU = os.path.join("shiu", "Connectivity_783.parquet")

# Neurotransmitter sign convention (Shiu et al. 2024; Eckstein et al. 2024):
# acetylcholine, dopamine, serotonin, octopamine -> excitatory (+1); GABA, glutamate -> inhibitory (-1)
NT_SIGN = {
    "acetylcholine": 1.0, "dopamine": 1.0, "serotonin": 1.0, "octopamine": 1.0,
    "gaba": -1.0, "glutamate": -1.0,
}


KNOWN_NTS = ("acetylcholine", "gaba", "glutamate", "dopamine", "serotonin", "octopamine", "histamine")
KNOWN_SIGN = dict(NT_SIGN, histamine=-1.0)   # histamine (photoreceptors) is inhibitory in the fly


def parse_known_nt(value) -> str | None:
    """First transmitter named in an annotation like 'gaba, MIP; acetylcholine-negative' -> 'gaba' (None if none)."""
    if not isinstance(value, str):
        return None
    for tok in re.split(r"[;,]", value.lower()):
        tok = tok.strip()
        for nt in KNOWN_NTS:
            if tok.startswith(nt) and "negative" not in tok:
                return nt
    return None


def apply_model_options(cx: "Connectome", signs: str = "shiu", eln_scale: float = 1.0,
                        unclear_ln: str = "excitatory") -> "Connectome":
    """Apply the sign rule, the unclear-LN rule and the eLN output scale to cx.W in place (see module docstring)."""
    n = cx.n
    row_sign = np.sign(np.asarray(cx.W.sum(axis=1)).ravel())
    scale = np.ones(n, dtype=np.float32)
    if signs == "known":
        if "known_nt" in cx.neurons.columns:
            known = cx.neurons.known_nt.map(parse_known_nt)
            ks = known.map(KNOWN_SIGN)
            m = ks.notna().to_numpy()
            flip = np.zeros(n, bool)
            flip[m] = (ks[m].to_numpy(dtype=np.float32) != row_sign[m]) & (row_sign[m] != 0)
            scale[flip] = -1.0
            row_sign[flip] *= -1
            cx.n_sign_flipped = int(flip.sum())
            cx.variant += "+known"
        else:
            signs = "shiu"          # no known-transmitter column (MaleCNS): nothing to apply, no provenance suffix
    elif signs != "shiu":
        raise ValueError(f"signs must be 'shiu' or 'known', got {signs!r}")
    if unclear_ln != "excitatory":
        if unclear_ln not in ("inhibitory", "silent"):
            raise ValueError(f"unclear_ln must be 'excitatory', 'inhibitory' or 'silent', got {unclear_ln!r}")
        ln = cx.select(cell_class="^ALLN$")
        nt = cx.neurons.top_nt.fillna("").astype(str).str.lower().to_numpy() if "top_nt" in cx.neurons.columns else np.full(n, "", dtype=object)
        unc = ln[nt[ln] == "unclear"]
        if len(unc):
            if unclear_ln == "inhibitory":
                flip = unc[row_sign[unc] > 0]
                scale[flip] *= -1.0
                row_sign[flip] *= -1
            else:
                scale[unc] = 0.0
            cx.n_unclear_ln = int(len(unc))
        else:
            unclear_ln = "excitatory"   # no unclear local neurons in this dataset: nothing to apply
    if eln_scale != 1.0:
        ln = cx.select(cell_class="^ALLN$")
        eln = ln[row_sign[ln] > 0]
        scale[eln] *= np.float32(eln_scale)
        cx.n_eln = int(len(eln))
        cx.variant += f"+eln{eln_scale:g}"
    if unclear_ln != "excitatory":
        cx.variant += "+unclearLN-" + ("inh" if unclear_ln == "inhibitory" else "off")
    if np.any(scale != 1.0):
        cx.W = sp.diags(scale, format="csr", dtype=np.float32) @ cx.W
        cx.W = sp.csr_matrix(cx.W, dtype=np.float32)
        cx.W.sort_indices()
    cx.signs, cx.eln_scale, cx.unclear_ln = signs, float(eln_scale), unclear_ln
    return cx


@dataclass
class Connectome:
    neurons: pd.DataFrame            # one row per neuron, index = dense idx 0..N-1
    W: sp.csr_matrix                 # W[pre, post] = sign * syn_count (row = presynaptic)
    root_ids: np.ndarray             # root_id per dense idx
    idx_of: dict = field(default_factory=dict)  # root_id -> dense idx
    w_syn_scale: float = 1.0        # per-synapse weight multiplier so datasets have matched input density (see malecns.py)
    dataset: str = "flywire"
    variant: str = "shiu"           # which connection table / threshold built W (provenance for the methods section)
    signs: str = "shiu"             # sign rule actually applied ("shiu" = predicted majority vote; "known" = overridden by known_nt)
    eln_scale: float = 1.0          # output scale of the antennal lobe's excitatory local neurons (1 = published model)
    unclear_ln: str = "excitatory"  # MaleCNS: what its 67 "unclear"-transmitter AL local neurons do (excitatory = published default)
    n_sign_flipped: int = 0
    n_eln: int = 0
    n_unclear_ln: int = 0

    @property
    def n(self) -> int:
        return len(self.root_ids)

    def __repr__(self) -> str:
        opts = (f", signs={self.signs}" + (f" ({self.n_sign_flipped} flipped)" if self.n_sign_flipped else "")
                + (f", eLN x{self.eln_scale:g} ({self.n_eln} neurons)" if self.eln_scale != 1.0 else "")
                + (f", unclear LNs {self.unclear_ln} ({self.n_unclear_ln})" if self.unclear_ln != "excitatory" else ""))
        return (f"Connectome({self.dataset}/{self.variant}: {self.n} neurons, {self.W.nnz} connections, "
                f"{float(np.abs(self.W.data).sum()):.0f} synapses, w_syn_scale={self.w_syn_scale:.3f}{opts})")

    # ---- group selection -------------------------------------------------
    def select(self, cell_type: str | None = None, hemibrain_type: str | None = None,
               cell_class: str | None = None, cell_sub_class: str | None = None,
               super_class: str | None = None, side: str | None = None,
               any_of: dict | None = None) -> np.ndarray:
        """Dense indices of neurons matching *all* given regex filters (case-insensitive).

        any_of: {column: regex} — matches if ANY of those columns matches.
        """
        m = np.ones(self.n, dtype=bool)
        def col_match(col, pat):
            if col not in self.neurons.columns:
                return np.zeros(self.n, dtype=bool)
            return self.neurons[col].fillna("").astype(str).str.contains(pat, regex=True, flags=re.I).to_numpy()
        for col, pat in [("cell_type", cell_type), ("hemibrain_type", hemibrain_type),
                         ("cell_class", cell_class), ("cell_sub_class", cell_sub_class),
                         ("super_class", super_class), ("side", side)]:
            if pat is not None:
                m &= col_match(col, pat)
        if any_of:
            mm = np.zeros(self.n, dtype=bool)
            for col, pat in any_of.items():
                mm |= col_match(col, pat)
            m &= mm
        return np.flatnonzero(m)

    def by_root_ids(self, ids) -> np.ndarray:
        return np.array([self.idx_of[int(r)] for r in ids if int(r) in self.idx_of], dtype=np.int64)

    def describe(self, idx: np.ndarray, top: int = 6) -> str:
        sub = self.neurons.iloc[idx]
        return f"{len(idx)} neurons; types={sub.cell_type.value_counts().head(top).to_dict()}; sides={sub.side.value_counts().to_dict()}"


def _annotations(data_dir: str) -> pd.DataFrame:
    ann = pd.read_csv(os.path.join(data_dir, ANNOT), sep="\t", dtype=str, low_memory=False)
    return ann.drop_duplicates("root_id").reset_index(drop=True)


def _build_cache(data_dir: str, cache: str, conn: str, min_syn: int) -> None:
    t0 = time.time()
    ann = _annotations(data_dir)
    root_ids = ann.root_id.astype(np.int64).to_numpy()
    idx_of = pd.Series(np.arange(len(root_ids)), index=root_ids)
    n = len(root_ids)
    if conn == "shiu":
        path = os.path.join(data_dir, CONNS_SHIU)
        print(f"[connectome] building cache from {ANNOT} + {CONNS_SHIU} (Shiu et al. 2024 table, all connections) ...", flush=True)
        df = pd.read_parquet(path, columns=["Presynaptic_ID", "Postsynaptic_ID", "Excitatory x Connectivity"])
        df = df.rename(columns={"Presynaptic_ID": "pre", "Postsynaptic_ID": "post", "Excitatory x Connectivity": "w"})
        df = df[(df.w.abs() >= min_syn) & df.pre.isin(idx_of.index) & df.post.isin(idx_of.index)]
        pi = idx_of[df.pre.to_numpy()].to_numpy(); po = idx_of[df.post.to_numpy()].to_numpy()
        w = df.w.to_numpy(dtype=np.float32)
    elif conn == "zenodo":
        path = os.path.join(data_dir, CONNS_ZENODO)
        print(f"[connectome] building cache from {ANNOT} + {CONNS_ZENODO} (>= {min_syn} synapses, sign = top_nt) ...", flush=True)
        c = pd.read_feather(path, columns=["pre_pt_root_id", "post_pt_root_id", "syn_count"])
        df = c.groupby(["pre_pt_root_id", "post_pt_root_id"], as_index=False).syn_count.sum()
        df = df.rename(columns={"pre_pt_root_id": "pre", "post_pt_root_id": "post", "syn_count": "syn"})
        df = df[(df.syn >= min_syn) & df.pre.isin(idx_of.index) & df.post.isin(idx_of.index)]
        pi = idx_of[df.pre.to_numpy()].to_numpy(); po = idx_of[df.post.to_numpy()].to_numpy()
        nt = ann.top_nt.fillna("acetylcholine").str.lower().map(NT_SIGN).fillna(1.0).to_numpy(dtype=np.float32)
        w = df.syn.to_numpy(dtype=np.float32) * nt[pi]
    else:
        raise ValueError(conn)
    W = sp.csr_matrix((w, (pi, po)), shape=(n, n), dtype=np.float32)
    W.sum_duplicates()
    np.savez_compressed(cache, root_ids=root_ids, indptr=W.indptr, indices=W.indices, data=W.data)
    print(f"[connectome] cached {os.path.basename(cache)}: {n} neurons, {W.nnz} connections, "
          f"{float(np.abs(W.data).sum()):.0f} synapses, {time.time()-t0:.1f}s", flush=True)


def load(data_dir: str | None = None, dataset: str | None = None, conn: str | None = None,
         min_syn: int | None = None, signs: str | None = None, eln_scale: float | None = None,
         unclear_ln: str | None = None) -> Connectome:
    """dataset: 'flywire' (default; female, brain only) or 'malecns' (male, brain + VNC).
    conn (flywire only): 'shiu' (default; Shiu et al.'s full v783 table) or 'zenodo' (Dorkenwald et al. table).
    min_syn: synapse-count threshold per connection (default 1 = all connections; the first version used 5).
    signs: 'shiu' (default, predicted signs) or 'known' (overridden by known transmitters); eln_scale: output scale
    of the antennal lobe's excitatory local neurons (default 1; see module docstring); unclear_ln: 'excitatory'
    (default) | 'inhibitory' | 'silent' for MaleCNS's unclear-transmitter local neurons.
    Environment overrides: FLYBRAIN_DATASET, FLYBRAIN_CONN, FLYBRAIN_MIN_SYN, FLYBRAIN_SIGNS, FLYBRAIN_ELN, FLYBRAIN_UNCLEAR_LN."""
    data_dir = data_dir or DATA_DIR
    dataset = (dataset or os.environ.get("FLYBRAIN_DATASET") or "flywire").lower()
    min_syn = int(min_syn if min_syn is not None else os.environ.get("FLYBRAIN_MIN_SYN", 1))
    signs = (signs or os.environ.get("FLYBRAIN_SIGNS") or "shiu").lower()
    eln_scale = float(eln_scale if eln_scale is not None else os.environ.get("FLYBRAIN_ELN", 1.0))
    unclear_ln = (unclear_ln or os.environ.get("FLYBRAIN_UNCLEAR_LN") or "excitatory").lower()
    if dataset == "malecns":
        from . import malecns
        return apply_model_options(malecns.load(data_dir, min_syn=min_syn), signs, eln_scale, unclear_ln)
    conn = (conn or os.environ.get("FLYBRAIN_CONN") or "shiu").lower()
    variant = f"{conn}_min{min_syn}"
    cache = os.path.join(data_dir, f"connectome_783_{variant}.npz")
    if not os.path.exists(cache):
        _build_cache(data_dir, cache, conn, min_syn)
    z = np.load(cache)
    root_ids = z["root_ids"]
    n = len(root_ids)
    W = sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(n, n))
    ann = _annotations(data_dir)
    ann = ann.set_index(ann.root_id.astype(np.int64)).loc[root_ids].reset_index(drop=True)
    for c in ("pos_x", "pos_y", "pos_z"):
        ann[c] = pd.to_numeric(ann[c], errors="coerce")
    idx_of = {int(r): i for i, r in enumerate(root_ids)}
    return apply_model_options(Connectome(neurons=ann, W=W, root_ids=root_ids, idx_of=idx_of, variant=variant), signs, eln_scale, unclear_ln)


def mean_input_synapses(W: sp.csr_matrix, post_idx: np.ndarray | None = None) -> float:
    """Mean total input synapses per neuron (over post_idx, default all) — the density statistic used to
    calibrate the per-synapse weight between datasets."""
    col = np.asarray(np.abs(W).sum(axis=0)).ravel()
    return float(col.mean() if post_idx is None else col[post_idx].mean())
