# FIRST-VERSION numpy implementation, kept only for brain/tests/test_lif.py (equivalence test). Do not use.
"""Leaky integrate-and-fire simulation of the whole connectome.

Parameters follow Shiu et al. 2024 (Nature) — the published whole-brain LIF model:
  v_rest = v_reset = -52 mV, v_thr = -45 mV, tau_m = 20 ms, tau_syn = 5 ms,
  refractory 2.2 ms, synaptic delay 1.8 ms, 0.275 mV per synapse, connections >= 5 synapses.

Dynamics (per neuron):
  tau_m dv/dt = (v_rest - v) + g
  tau_s dg/dt = -g ;  on presynaptic spike (after delay): g += 0.275 mV * signed synapse count

Sensory neurons are driven the way Shiu et al. drive them: as Poisson spike trains at a
target rate ("forced" spikes). Nothing else is injected; all downstream activity comes
from the wiring.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp


@dataclass
class LIFParams:
    v_rest: float = -52.0
    v_reset: float = -52.0
    v_thr: float = -45.0
    tau_m: float = 20.0       # ms
    tau_syn: float = 5.0      # ms
    t_ref: float = 2.2        # ms
    delay: float = 1.8        # ms
    w_syn: float = 0.275      # mV per synapse
    dt: float = 0.5           # ms  (Shiu: 0.1; 0.5 is ~5x faster and behaviorally equivalent at this scale)
    noise_hz: float = 0.0     # optional background Poisson rate on every neuron (0 = Shiu default)


class LIF:
    def __init__(self, W: sp.csr_matrix, params: LIFParams | None = None, seed: int = 0):
        self.p = params or LIFParams()
        self.N = W.shape[0]
        W = W.tocsr()
        W.sort_indices()
        self.indptr = W.indptr
        self.indices = W.indices
        self.data = W.data.astype(np.float32)   # plasticity modules edit this array in place
        self.rng = np.random.default_rng(seed)

        p = self.p
        self.ref_steps = max(1, int(round(p.t_ref / p.dt)))
        self.delay_steps = max(1, int(round(p.delay / p.dt)))
        self.decay_g = np.float32(np.exp(-p.dt / p.tau_syn))
        self.a_m = np.float32(p.dt / p.tau_m)
        self.dt_s = p.dt / 1000.0

        self.v = np.full(self.N, p.v_rest, dtype=np.float32)
        self.g = np.zeros(self.N, dtype=np.float32)
        self.ref_until = np.zeros(self.N, dtype=np.int64)
        self.buf = np.zeros((self.delay_steps + 1, self.N), dtype=np.float32)
        self.t = 0
        self.forced_idx = np.zeros(0, dtype=np.int64)
        self.forced_rate = np.zeros(0, dtype=np.float32)

    # ---- drive --------------------------------------------------------------
    def set_drive(self, idx: np.ndarray, rate_hz: np.ndarray) -> None:
        """Force Poisson spiking at rate_hz on neurons idx (replaces the previous drive)."""
        if len(idx):
            # merge duplicates by max rate
            order = np.argsort(idx, kind="stable")
            idx, rate_hz = idx[order], rate_hz[order]
            uniq, start = np.unique(idx, return_index=True)
            rate = np.maximum.reduceat(rate_hz, start)
            keep = rate > 0
            self.forced_idx, self.forced_rate = uniq[keep], rate[keep].astype(np.float32)
        else:
            self.forced_idx = np.zeros(0, dtype=np.int64)
            self.forced_rate = np.zeros(0, dtype=np.float32)

    # ---- core ---------------------------------------------------------------
    def _propagate(self, spk: np.ndarray, out: np.ndarray) -> None:
        """out += W[spk, :] summed over rows (signed synapse counts * w_syn)."""
        if len(spk) == 0:
            return
        starts = self.indptr[spk]
        lens = self.indptr[spk + 1] - starts
        total = int(lens.sum())
        if total == 0:
            return
        rep_starts = np.repeat(starts, lens)
        offs = np.arange(total, dtype=np.int64) - np.repeat(np.cumsum(lens) - lens, lens)
        e = rep_starts + offs
        out += np.bincount(self.indices[e], weights=self.data[e], minlength=self.N).astype(np.float32) * self.p.w_syn

    def step(self) -> np.ndarray:
        p, t = self.p, self.t
        slot = t % (self.delay_steps + 1)
        self.g += self.buf[slot]
        self.buf[slot] = 0.0

        # integrate
        self.v += self.a_m * (p.v_rest - self.v + self.g)
        self.g *= self.decay_g
        inref = self.ref_until > t
        self.v[inref] = p.v_reset

        spk = self.v >= p.v_thr
        if len(self.forced_idx):
            fire = self.rng.random(len(self.forced_idx)) < self.forced_rate * self.dt_s
            spk[self.forced_idx[fire]] = True
        if p.noise_hz > 0:
            spk |= self.rng.random(self.N) < (p.noise_hz * self.dt_s)
        spk_idx = np.flatnonzero(spk)
        if len(spk_idx):
            self.v[spk_idx] = p.v_reset
            self.ref_until[spk_idx] = t + self.ref_steps
            self._propagate(spk_idx, self.buf[(t + self.delay_steps) % (self.delay_steps + 1)])
        self.t = t + 1
        return spk_idx

    def run(self, ms: float, record_mask: np.ndarray | None = None):
        """Advance by `ms` of brain time. Returns (spike counts per neuron, [(step, idx)...] for recorded)."""
        n_steps = max(1, int(round(ms / self.p.dt)))
        counts = np.zeros(self.N, dtype=np.int32)
        rec = []
        for _ in range(n_steps):
            s = self.step()
            if len(s):
                counts[s] += 1
                if record_mask is not None:
                    r = s[record_mask[s]]
                    if len(r):
                        rec.append((self.t - 1, r))
        return counts, rec

    def reset(self) -> None:
        self.v[:] = self.p.v_rest
        self.g[:] = 0
        self.buf[:] = 0
        self.ref_until[:] = 0
        self.t = 0
