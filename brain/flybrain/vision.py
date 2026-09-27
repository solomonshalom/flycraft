"""Neural vision: a flyvis optic lobe (Lappalainen et al. 2024, Nature) driving the connectome's own optic-lobe neurons.

Why: fly motion vision runs on graded, non-spiking lamina/medulla neurons with cell-type-specific time
constants. A uniform spiking LIF cannot express that, so in the pure connectome model vision dies in the
medulla (notes, section 3a). flyvis is a connectome-constrained model of exactly those cells -- 65 cell types,
721 columns, graded dynamics with per-type time constants and resting potentials fitted so the network predicts
motion -- i.e. it is the fly's optic lobe wiring run with the right neuron model. We run one flyvis network per
eye on the bot's eye image and *activate* the FlyWire/MaleCNS neurons of the same cell types (58 of the 65 are
labeled in FlyWire, ~1 cell per column per side) at rates set by the flyvis activity of the matching column.
From there on the spiking connectome takes over: lobula plate tangential cells, LC/LPLC loom detectors, LC10
courtship-pursuit cells, and the descending neurons are all downstream of these types.

Column matching: the annotation table has no column ids, so each optic-lobe neuron's retinotopic position is
propagated through the connectome from the photoreceptors: photoreceptors get (u, v) from their anchor points
(senses._retinotopy, same orientation assumption as before), lamina cells inherit the synapse-weighted mean
position of their photoreceptor inputs, medulla cells of their lamina inputs, and so on for four hops. flyvis
columns are matched by nearest position in the eye-image plane. The orientation of the map is therefore the
one assumption already flagged for photoreceptors (README), now testable end-to-end with the optomotor check.

Activity -> rate: flyvis activities are voltage-like; a cell's rate is r_max * clip((a - a_rest) / a_scale, 0, 1),
where a_rest is its own activity under uniform grey (per cell), so only depolarisation above rest drives spikes.

The optic lobe runs in a worker thread pipelined one tick behind the spiking brain (the LIF kernel releases
the GIL), which adds one tick (50 ms) of visual latency -- the real fly's is 30-50 ms.
"""
from __future__ import annotations

import glob
import os
import sys
import threading
import time

import numpy as np
import scipy.sparse as sp

from .connectome import Connectome

FLYVIS_ALIAS = {"Am": "Am1", "R1": "R1-6", "R2": "R1-6", "R3": "R1-6", "R4": "R1-6", "R5": "R1-6", "R6": "R1-6",
                "CT1(Lo1)": None, "CT1(M10)": None}   # None = not mapped (single giant cell, not columnar)


def _import_flyvis():
    try:
        import flyvis  # noqa: F401
        return
    except ImportError:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [os.environ.get("FLYVIS_SITE", "")] + glob.glob(os.path.join(here, "..", "..", ".venv-flyvis", "lib", "python3.*", "site-packages"))
    for c in cands:
        if c and os.path.isdir(c) and c not in sys.path:
            sys.path.append(c)
    import flyvis  # noqa: F401  (raises if still missing: pip install flyvis; flyvis download-pretrained)


class OpticLobe:
    def __init__(self, cx: Connectome, senses, sim=None, model: str = "flow/0000/000", dt: float = 1 / 60, substeps: int = 3,
                 kernel_size: int = 5, r_max: float = 100.0, a_scale: float = 1.0, hops: int = 4, min_syn: float = 3.0,
                 mirror_left: bool = False, adapt_tau: float = 1.0, verbose: bool = True):
        # adapt_tau (s): contrast adaptation. flyvis cells keep responding to a standing pattern (its L1/L2 and
        # T4/T5 stay ~30 Hz-equivalent for a static grating), which real lamina neurons do not: they adapt within
        # ~1 s. Each cell's 'rest' therefore tracks its own recent activity with this time constant, so only
        # activity above the recent baseline (motion, flashes, looming) is passed on. 0 = off (fixed grey rest).
        self.adapt_tau = adapt_tau
        # mirror_left: the two optic lobes are mirror images; flyvis was fitted on one. If True the left eye's image is
        # flipped horizontally before the optic lobe so that 'front' is on the same side for both networks (untested
        # which convention flyvis assumes; off by default, the optomotor sign is the same either way).
        self.mirror_left = mirror_left
        _import_flyvis()
        import torch
        from flyvis import NetworkView
        from flyvis.datasets.rendering import BoxEye
        self.torch = torch
        self.cx, self.senses = cx, senses
        self.dt, self.substeps, self.r_max, self.a_scale = dt, substeps, r_max, a_scale
        t0 = time.time()
        self.net = NetworkView(model).init_network().eval()
        cn = self.net.connectome
        self.node_type = cn.nodes.type[:].astype(str)
        nu, nv = cn.nodes.u[:].astype(float), cn.nodes.v[:].astype(float)
        self.eye = BoxEye(extent=15, kernel_size=kernel_size)
        # flyvis node -> position in the (resized, square) image plane, BoxEye convention: y = d(u + v/2), x = d*v
        d = float(self.eye.kernel_size)
        y, x = d * (nu + nv / 2), d * nv
        rc = self.eye.receptor_centers.float()
        y0, y1 = float(rc[:, 0].min()), float(rc[:, 0].max()); x0, x1 = float(rc[:, 1].min()), float(rc[:, 1].max())
        self.node_xy = np.stack([(x - x0) / (x1 - x0), (y - y0) / (y1 - y0)], axis=1)   # (n_nodes, 2) in [0,1]^2 (col, row)
        # retinotopic coordinates for the connectome's optic-lobe neurons, then the match
        self.maps = {}
        for side in ("L", "R"):
            self.maps[side] = self._build_map(side, hops, min_syn, verbose)
        # flyvis now owns the dynamics *inside* the optic lobe: the connectome's synapses between covered neurons are
        # cut so their activity is not propagated twice; their outputs to everything else (LPTCs, LC/LPLC, DNs) stay.
        self.covered = np.zeros(cx.n, bool)
        for side in self.maps:
            self.covered[self.maps[side][0]] = True
        self.n_cut = 0
        if sim is not None:
            self.n_cut = sim.cut_edges(self.covered, self.covered)
        with torch.no_grad():
            self.state = self.net.steady_state(1.0, dt, batch_size=2, value=0.5)
            self.rest0 = self.state.nodes.activity.detach().cpu().numpy()[0].copy()   # (n_nodes,) rest under grey
            self.rest = np.stack([self.rest0, self.rest0])                            # per eye, adapting
        self.lock = threading.Lock()
        self.latest_out = (np.zeros(0, np.int64), np.zeros(0, np.float32))
        self.worker = None
        self.n_frames = 0
        self.wall_ms = 0.0
        if verbose:
            n_map = sum(len(m[0]) for m in self.maps.values())
            print(f"[vision] flyvis {model}: {len(self.node_type)} cells, {n_map} connectome neurons driven "
                  f"({', '.join(f'{s}:{len(self.maps[s][0])}' for s in self.maps)}); {self.n_cut} intra-optic-lobe connections "
                  f"handed to flyvis; {time.time()-t0:.1f}s", flush=True)

    # ---- column matching ---------------------------------------------------------------------------
    def _build_map(self, side: str, hops: int, min_syn: float, verbose: bool):
        cx, senses = self.cx, self.senses
        N = cx.n
        sidename = {"L": "left", "R": "right"}[side]
        ct = cx.neurons.cell_type.fillna("").to_numpy()
        onside = (cx.neurons.side.fillna("").to_numpy() == sidename)
        fw_names = {}
        for t in set(self.node_type):
            name = FLYVIS_ALIAS.get(t, t)
            if name is not None:
                fw_names.setdefault(name, []).append(t)
        cand = onside & np.isin(ct, list(fw_names))
        coords = np.zeros((N, 2), np.float64); has = np.zeros(N, np.float64)
        photo = senses.groups[f"photo_{side}"]
        coords[photo] = senses.eye_uv[side]; has[photo] = 1.0
        A = sp.csr_matrix((np.abs(cx.W.data), cx.W.indices, cx.W.indptr), shape=(N, N)).T.tocsr()   # A[post, pre]
        for hop in range(hops):
            num = A @ (coords * has[:, None]); den = A @ has
            new = cand & (has == 0) & (den >= min_syn)
            coords[new] = num[new] / den[new, None]; has[new] = 1.0
            if verbose:
                print(f"[vision] {side} hop {hop+1}: {int((has > 0)[cand].sum())}/{int(cand.sum())} optic-lobe neurons placed", flush=True)
        # match each placed connectome neuron to the nearest flyvis node of its type in the image plane
        from scipy.spatial import cKDTree
        fw_idx, node_idx, per_type = [], [], {}
        for name, ftypes in fw_names.items():
            fw = np.flatnonzero(cand & (has > 0) & (ct == name))
            if len(fw) == 0:
                continue
            if len(ftypes) > 1:                     # R1-6: six flyvis types share one FlyWire label -> spread cells over them
                ftypes = sorted(ftypes)
            for k, t in enumerate(ftypes):
                nodes = np.flatnonzero(self.node_type == t)
                tree = cKDTree(self.node_xy[nodes])
                sub = fw[k::len(ftypes)]
                q = coords[sub]                     # (u, v) = (col, row) in [0,1]^2
                _, j = tree.query(q)
                fw_idx.append(sub); node_idx.append(nodes[j]); per_type[t] = len(sub)
        fw_idx = np.concatenate(fw_idx) if fw_idx else np.zeros(0, np.int64)
        node_idx = np.concatenate(node_idx) if node_idx else np.zeros(0, np.int64)
        if verbose:
            print(f"[vision] {side}: matched {len(fw_idx)} neurons of {len(per_type)} types; e.g. " +
                  ", ".join(f"{t}:{per_type[t]}" for t in ("L1", "Mi1", "Tm3", "T4a", "T5a") if t in per_type), flush=True)
        return fw_idx.astype(np.int64), node_idx.astype(np.int64)

    # ---- per-tick processing --------------------------------------------------------------------------
    def frames_to_rates(self, imgs: dict) -> tuple[np.ndarray, np.ndarray]:
        """imgs: {"L": (h, w) array in [0,1], "R": ...}. Advances the optic lobe by `substeps` steps of dt."""
        torch = self.torch
        imL = imgs["L"][:, ::-1] if self.mirror_left else imgs["L"]
        seq = np.stack([np.repeat(imL[None], self.substeps, 0), np.repeat(imgs["R"][None], self.substeps, 0)])   # (2, T, h, w)
        with torch.no_grad():
            x = torch.tensor(seq, dtype=torch.float32)
            hexals = self.eye(x)                                             # (2, T, 1, 721)
            self.net.stimulus.zero(2, self.substeps); self.net.stimulus.add_input(hexals)
            states = self.net.forward(self.net.stimulus(), self.dt, self.state, as_states=True)
            self.state = states[-1]
            act = self.state.nodes.activity.detach().cpu().numpy()          # (2, n_nodes)
        idx, rates = [], []
        for b, side in enumerate(("L", "R")):
            fw, nodes = self.maps[side]
            a = (act[b, nodes] - self.rest[b, nodes]) / self.a_scale
            idx.append(fw); rates.append((self.r_max * np.clip(a, 0, 1)).astype(np.float32))
        if self.adapt_tau > 0:
            k = min(1.0, self.substeps * self.dt / self.adapt_tau)
            self.rest += k * (act - self.rest)
        return np.concatenate(idx), np.concatenate(rates)

    def reset(self) -> None:
        with self.torch.no_grad():
            self.state = self.net.steady_state(1.0, self.dt, batch_size=2, value=0.5)
        self.rest = np.stack([self.rest0, self.rest0])

    def submit(self, eyes: dict) -> None:
        """Start processing this tick's eye images in the background (drops the frame if the previous one is still running)."""
        if self.worker is not None and self.worker.is_alive():
            return
        imgs = {}
        for side in ("L", "R"):
            e = eyes.get(side)
            if not e:
                return
            imgs[side] = np.asarray(e["px"], dtype=np.float32).reshape(int(e["h"]), int(e["w"]))
        def run():
            t0 = time.perf_counter()
            out = self.frames_to_rates(imgs)
            with self.lock:
                self.latest_out = out; self.n_frames += 1; self.wall_ms = (time.perf_counter() - t0) * 1000
        self.worker = threading.Thread(target=run, daemon=True); self.worker.start()

    def latest(self) -> tuple[np.ndarray, np.ndarray]:
        with self.lock:
            return self.latest_out

    def process_sync(self, eyes: dict) -> tuple[np.ndarray, np.ndarray]:
        imgs = {s: np.asarray(eyes[s]["px"], dtype=np.float32).reshape(int(eyes[s]["h"]), int(eyes[s]["w"])) for s in ("L", "R")}
        return self.frames_to_rates(imgs)
