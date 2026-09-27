"""Leaky integrate-and-fire simulation of the whole connectome (numba kernel).

The semantics are those of the published whole-brain model of Shiu et al. 2024 (Nature), taken from their
Brian2 code (github.com/philshiu/Drosophila_brain_model, model.py), not from the paper's prose:

  dv/dt = (v_0 - v + g) / t_mbr   (unless refractory)     v_0 = v_rst = -52 mV, v_th = -45 mV, t_mbr = 20 ms
  dg/dt = -g / tau                (unless refractory)     tau = 5 ms
  threshold  v > v_th ;  reset  v = v_rst, g = 0 ;  refractory 2.2 ms
  synapse    g += w  after a 1.8 ms delay,  w = sign * synapse_count * 0.275 mV
  activation PoissonInput on v at r_poi with weight w_syn * f_poi (f_poi = 250, i.e. a 68.75 mV kick):
             the neuron spikes at the next step unless it is refractory, in which case as soon as it is not
  integration method 'linear' (exact for this linear system), Brian2 default dt = 0.1 ms

All of this is reproduced here: exact integration, g reset to 0 at every spike, Poisson kicks for activation,
Brian2's phase order (integrate -> threshold -> synapses/kicks -> reset), and Brian2's actual refractory rule,
established by direct micro-network tests against Brian2 (14 Sep 2026; scripts not kept): while a neuron is refractory
(2.2 ms after a spike) v and g are not integrated AND every input to them -- synaptic arrivals and kicks --
is discarded, not accumulated. A neuron therefore ignores the world for 2.2 ms after each spike. This is what
limits a Poisson-driven neuron to 1/(2.2 ms + 1/rate) (82 Hz at 100 Hz drive, as in Brian2), and it matters
downstream: without it, feeding motor neurons fire 1.8x too fast under sugar drive. dt = 0.2 ms by
default so that the 1.8 ms delay and the 2.2 ms refractory period are whole numbers of steps
(0.1 and 0.2 ms give the same rates within seed noise; at 0.5 ms the rounded refractory period and delay raise
rates by a median 8 %, see the paper's Note 1; brain/tests/brian2_reference.py runs
the real Brian2 model on the same connectome for comparison).

Event-driven bookkeeping (pure speed, no change in semantics): only neurons that are not exactly at rest --
those with pending synaptic input, a non-zero g, a membrane potential more than `eps` from rest, or inside the
refractory period -- are integrated each step. A neuron whose v and g have decayed to within eps (0.01 mV /
0.001 mV; the threshold gap is 7 mV) of rest is snapped to rest and dropped until its next input.

`LIFParams(legacy=True)` reproduces the first version of this code (forward Euler, no g reset, g decaying
during the refractory period, forced spikes instead of kicks) for the numerics-sensitivity analysis only.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp
from numba import get_num_threads, njit, prange


@dataclass
class LIFParams:
    v_rest: float = -52.0
    v_reset: float = -52.0
    v_thr: float = -45.0
    tau_m: float = 20.0        # ms
    tau_syn: float = 5.0       # ms
    t_ref: float = 2.2         # ms
    delay: float = 1.8         # ms
    w_syn: float = 0.275       # mV per synapse (times dataset density scale, times gain)
    dt: float = 0.2            # ms (Shiu/Brian2: 0.1; 0.2 keeps delay and refractory period exact)
    kick_mv: float = 0.275 * 250.0   # Shiu et al.: PoissonInput weight = w_syn * f_poi; independent of gain here
    noise_hz: float = 0.0      # optional background Poisson kicks on every neuron (0 = Shiu default)
    legacy: bool = False       # first-version numerics, sensitivity analysis only
    eps_v: float = 1e-2        # mV: |v - v_rest| below which a quiet neuron is snapped to rest
    eps_g: float = 1e-3        # mV: |g| below which it counts as zero


@njit(cache=True)
def _seed(s):
    np.random.seed(s)


@njit(cache=True)
def _activate(i, active, act_buf, act_n):
    """Add neuron i to the active set (its chunk is i % T, so chunks partition the neurons and threads never race)."""
    if active[i] == 0:
        active[i] = 1
        c = i % act_buf.shape[0]
        act_buf[c, act_n[c]] = i
        act_n[c] += 1


@njit(parallel=True, cache=True, nogil=True)
def _integrate(t, slot, v, g, ref_until, buf, v_rest, v_reset, v_thr, a_m, b_g, c_g, e_m, legacy, eps_v, eps_g,
               active, act_buf, act_n, spk_buf, spk_n, flag):
    """One step of integration + threshold over the active set, each chunk compacted in place by its own thread."""
    T = act_buf.shape[0]
    nslot = buf.shape[0]
    for c in prange(T):
        m = 0
        n_spk = 0
        for k in range(act_n[c]):
            i = act_buf[c, k]
            gi = g[i] + buf[slot, i]
            buf[slot, i] = 0.0
            keep = True
            if legacy:
                vi = v[i] + e_m * (v_rest - v[i] + gi)
                gi = gi * c_g
                if t < ref_until[i]:
                    vi = v_reset
                v[i] = vi
                g[i] = gi
                if vi >= v_thr:
                    spk_buf[c, n_spk] = i
                    n_spk += 1
                    flag[i] = 1
            else:
                # Brian2 '(unless refractory)': while refractory, v and g are neither integrated nor modified --
                # synaptic arrivals (on_pre) and kicks during the window are discarded, not accumulated.
                # An arrival consumed here corresponds to on_pre one step earlier, hence the strict '>'.
                if t <= ref_until[i]:
                    gi = g[i]
                if t >= ref_until[i]:
                    vi = v_rest + (v[i] - v_rest) * a_m + gi * b_g   # exact ('linear') update
                    gi = gi * c_g
                    v[i] = vi
                    g[i] = gi
                    if vi > v_thr:
                        spk_buf[c, n_spk] = i
                        n_spk += 1
            if t >= ref_until[i] and abs(v[i] - v_rest) < eps_v and abs(g[i]) < eps_g:
                pending = False
                for q in range(nslot):
                    if buf[q, i] != 0.0:
                        pending = True
                        break
                if not pending:
                    v[i] = v_rest
                    g[i] = 0.0
                    active[i] = 0
                    keep = False
            if keep:
                act_buf[c, m] = i
                m += 1
        act_n[c] = m
        spk_n[c] = n_spk


@njit(cache=True, nogil=True)
def _integrate_serial(t, slot, v, g, ref_until, buf, v_rest, v_reset, v_thr, a_m, b_g, c_g, e_m, legacy, eps_v, eps_g,
               active, act_buf, act_n, spk_buf, spk_n, flag):
    """Serial twin of _integrate for small active sets (a parallel region costs ~100 us to launch)."""
    T = act_buf.shape[0]
    nslot = buf.shape[0]
    for c in range(T):
        m = 0
        n_spk = 0
        for k in range(act_n[c]):
            i = act_buf[c, k]
            gi = g[i] + buf[slot, i]
            buf[slot, i] = 0.0
            keep = True
            if legacy:
                vi = v[i] + e_m * (v_rest - v[i] + gi)
                gi = gi * c_g
                if t < ref_until[i]:
                    vi = v_reset
                v[i] = vi
                g[i] = gi
                if vi >= v_thr:
                    spk_buf[c, n_spk] = i
                    n_spk += 1
                    flag[i] = 1
            else:
                # Brian2 '(unless refractory)': while refractory, v and g are neither integrated nor modified --
                # synaptic arrivals (on_pre) and kicks during the window are discarded, not accumulated.
                # An arrival consumed here corresponds to on_pre one step earlier, hence the strict '>'.
                if t <= ref_until[i]:
                    gi = g[i]
                if t >= ref_until[i]:
                    vi = v_rest + (v[i] - v_rest) * a_m + gi * b_g   # exact ('linear') update
                    gi = gi * c_g
                    v[i] = vi
                    g[i] = gi
                    if vi > v_thr:
                        spk_buf[c, n_spk] = i
                        n_spk += 1
            if t >= ref_until[i] and abs(v[i] - v_rest) < eps_v and abs(g[i]) < eps_g:
                pending = False
                for q in range(nslot):
                    if buf[q, i] != 0.0:
                        pending = True
                        break
                if not pending:
                    v[i] = v_rest
                    g[i] = 0.0
                    active[i] = 0
                    keep = False
            if keep:
                act_buf[c, m] = i
                m += 1
        act_n[c] = m
        spk_n[c] = n_spk


@njit(cache=True, nogil=True)
def _run(n_steps, t0, v, g, ref_until, buf, indptr, indices, data, w_syn,
         v_rest, v_reset, v_thr, a_m, b_g, c_g, e_m, ref_steps, wr_off,
         forced_idx, forced_p, kick, noise_p, legacy, eps_v, eps_g,
         counts, rec_mask, rec_step, rec_id, spk_buf, spk_n, extra_buf, flag, active, act_buf, act_n, par_min):
    N = v.shape[0]
    nslot = buf.shape[0]
    T = act_buf.shape[0]
    n_rec = 0
    rec_cap = rec_step.shape[0]
    for s in range(n_steps):
        t = t0 + s
        slot = t % nslot
        wslot = (t + wr_off) % nslot
        if act_n.sum() >= par_min:
            _integrate(t, slot, v, g, ref_until, buf, v_rest, v_reset, v_thr, a_m, b_g, c_g, e_m, legacy, eps_v, eps_g,
                       active, act_buf, act_n, spk_buf, spk_n, flag)
        else:
            _integrate_serial(t, slot, v, g, ref_until, buf, v_rest, v_reset, v_thr, a_m, b_g, c_g, e_m, legacy, eps_v, eps_g,
                              active, act_buf, act_n, spk_buf, spk_n, flag)

        # ---- activation: Poisson kicks (Shiu) or forced spikes (legacy); background noise likewise ----
        n_extra = 0
        if legacy:
            for k in range(forced_idx.shape[0]):
                if np.random.random() < forced_p[k]:
                    i = forced_idx[k]
                    if flag[i] == 0:
                        flag[i] = 1
                        extra_buf[n_extra] = i
                        n_extra += 1
            if noise_p > 0.0:
                mm = np.random.binomial(N, noise_p)
                for j in range(mm):
                    i = np.random.randint(0, N)
                    if flag[i] == 0 and n_extra < extra_buf.shape[0]:
                        flag[i] = 1
                        extra_buf[n_extra] = i
                        n_extra += 1
        else:
            for k in range(forced_idx.shape[0]):
                if np.random.random() < forced_p[k]:
                    i = forced_idx[k]
                    if t >= ref_until[i]:            # kicks during the refractory window are discarded (Brian2)
                        v[i] += kick
                        _activate(i, active, act_buf, act_n)
            if noise_p > 0.0:
                mm = np.random.binomial(N, noise_p)
                for j in range(mm):
                    i = np.random.randint(0, N)
                    if t >= ref_until[i]:
                        v[i] += kick
                        _activate(i, active, act_buf, act_n)

        # ---- spikes: count, record, propagate (delayed), reset ----
        for c in range(T):
            for k in range(spk_n[c]):
                i = spk_buf[c, k]
                counts[i] += 1
                v[i] = v_reset
                if not legacy:
                    g[i] = 0.0
                ref_until[i] = t + ref_steps
                flag[i] = 0
                _activate(i, active, act_buf, act_n)
                if rec_mask[i] and n_rec < rec_cap:
                    rec_step[n_rec] = t
                    rec_id[n_rec] = i
                    n_rec += 1
                for e in range(indptr[i], indptr[i + 1]):
                    j = indices[e]
                    buf[wslot, j] += data[e] * w_syn
                    _activate(j, active, act_buf, act_n)
        for k in range(n_extra):
            i = extra_buf[k]
            counts[i] += 1
            v[i] = v_reset
            ref_until[i] = t + ref_steps
            flag[i] = 0
            _activate(i, active, act_buf, act_n)
            if rec_mask[i] and n_rec < rec_cap:
                rec_step[n_rec] = t
                rec_id[n_rec] = i
                n_rec += 1
            for e in range(indptr[i], indptr[i + 1]):
                j = indices[e]
                buf[wslot, j] += data[e] * w_syn
                _activate(j, active, act_buf, act_n)
    return n_rec


class LIF:
    def __init__(self, W: sp.csr_matrix, params: LIFParams | None = None, seed: int = 0):
        self.p = params or LIFParams()
        self.N = W.shape[0]
        W = W.tocsr()
        W.sort_indices()
        self.indptr = W.indptr.astype(np.int64)
        self.indices = W.indices.astype(np.int64)
        self.data = W.data.astype(np.float32)   # plasticity / silencing edit this array in place
        self.data0 = self.data.copy()

        p = self.p
        self.ref_steps = max(1, int(round(p.t_ref / p.dt)))
        self.delay_steps = max(1, int(round(p.delay / p.dt)))
        # Brian2: on_pre at step k+D acts on the integration of step k+D+1 -> one extra slot in the ring
        self.wr_off = self.delay_steps if p.legacy else self.delay_steps + 1
        self.dt_s = p.dt / 1000.0
        self.a_m = float(np.exp(-p.dt / p.tau_m))
        self.c_g = float(np.exp(-p.dt / p.tau_syn))
        self.b_g = float(p.tau_syn / (p.tau_m - p.tau_syn) * (self.a_m - self.c_g))
        self.e_m = float(p.dt / p.tau_m)

        self.v = np.full(self.N, p.v_rest, dtype=np.float32)
        self.g = np.zeros(self.N, dtype=np.float32)
        self.ref_until = np.zeros(self.N, dtype=np.int64)
        self.buf = np.zeros((self.wr_off + 1, self.N), dtype=np.float32)
        self.t = 0
        self.forced_idx = np.zeros(0, dtype=np.int64)
        self.forced_p = np.zeros(0, dtype=np.float64)
        self.forced_rate = np.zeros(0, dtype=np.float32)

        self.T = max(1, min(get_num_threads(), 8))     # chunks = threads; neuron i lives in chunk i % T
        self.par_min = 3000 * self.T                    # active neurons above which the parallel pass pays off (launch ~100 us)
        cap = (self.N + self.T - 1) // self.T
        self.spk_buf = np.zeros((self.T, cap), dtype=np.int64)
        self.spk_n = np.zeros(self.T, dtype=np.int64)
        self.flag = np.zeros(self.N, dtype=np.uint8)
        self.active = np.zeros(self.N, dtype=np.uint8)
        self.act_buf = np.zeros((self.T, cap), dtype=np.int64)
        self.act_n = np.zeros(self.T, dtype=np.int64)
        self._no_mask = np.zeros(self.N, dtype=np.bool_)
        self._empty_i64 = np.zeros(0, dtype=np.int64)
        self.seed(seed)

    # ---- drive --------------------------------------------------------------
    def seed(self, s: int) -> None:
        _seed(int(s))

    def set_drive(self, idx: np.ndarray, rate_hz: np.ndarray) -> None:
        """Poisson activation at rate_hz on neurons idx (replaces the previous drive; duplicates -> max rate)."""
        idx = np.asarray(idx, dtype=np.int64)
        rate_hz = np.asarray(rate_hz, dtype=np.float32)
        if len(idx):
            order = np.argsort(idx, kind="stable")
            idx, rate_hz = idx[order], rate_hz[order]
            uniq, start = np.unique(idx, return_index=True)
            rate = np.maximum.reduceat(rate_hz, start)
            keep = rate > 0
            self.forced_idx, self.forced_rate = uniq[keep], rate[keep].astype(np.float32)
        else:
            self.forced_idx = np.zeros(0, dtype=np.int64)
            self.forced_rate = np.zeros(0, dtype=np.float32)
        self.forced_p = (self.forced_rate.astype(np.float64) * self.dt_s)

    # ---- lesions ------------------------------------------------------------
    def scale_output(self, idx: np.ndarray, factor: float) -> None:
        """Multiply every outgoing synapse of neurons idx by factor (0 = silence, Shiu-style)."""
        for i in np.asarray(idx, dtype=np.int64):
            self.data[self.indptr[i]:self.indptr[i + 1]] *= np.float32(factor)

    def restore_weights(self) -> None:
        self.data[:] = self.data0

    def cut_edges(self, pre_mask: np.ndarray, post_mask: np.ndarray) -> int:
        """Zero every synapse from a neuron in pre_mask onto a neuron in post_mask (e.g. to hand a whole region's
        internal dynamics to another model). Returns the number of connections cut."""
        rows = np.repeat(np.arange(self.N), np.diff(self.indptr))
        sel = pre_mask[rows] & post_mask[self.indices] & (self.data != 0)
        self.data[sel] = 0.0
        return int(sel.sum())

    # ---- core ---------------------------------------------------------------
    def _call(self, k, counts, mask, rec_step, rec_id):
        p = self.p
        extra_cap = len(self.forced_idx) + (int(4 * p.noise_hz * self.dt_s * self.N) + 64 if p.noise_hz > 0 else 0)
        extra_buf = np.zeros(max(1, extra_cap), dtype=np.int64)
        n_rec = _run(k, self.t, self.v, self.g, self.ref_until, self.buf, self.indptr, self.indices,
                     self.data, np.float32(p.w_syn), p.v_rest, p.v_reset, p.v_thr, self.a_m, self.b_g,
                     self.c_g, self.e_m, self.ref_steps, self.wr_off, self.forced_idx, self.forced_p,
                     p.kick_mv, float(p.noise_hz * self.dt_s), p.legacy, p.eps_v, p.eps_g,
                     counts, mask, rec_step, rec_id, self.spk_buf, self.spk_n, extra_buf, self.flag, self.active,
                     self.act_buf, self.act_n, self.par_min)
        self.t += k
        return n_rec

    def run(self, ms: float, record_mask: np.ndarray | None = None):
        """Advance by `ms` of brain time. Returns (spike counts per neuron, [(step, idx)...] for recorded)."""
        n_steps = max(1, int(round(ms / self.p.dt)))
        counts = np.zeros(self.N, dtype=np.int32)
        rec = []
        if record_mask is None:
            self._call(n_steps, counts, self._no_mask, self._empty_i64, self._empty_i64)
            return counts, rec
        mask = np.ascontiguousarray(record_mask, dtype=np.bool_)
        n_masked = int(mask.sum())
        done = 0
        while done < n_steps:
            k = min(n_steps - done, 250)
            cap = max(1, n_masked * k)
            rec_step = np.zeros(cap, dtype=np.int64)
            rec_id = np.zeros(cap, dtype=np.int64)
            n_rec = self._call(k, counts, mask, rec_step, rec_id)
            done += k
            if n_rec:
                steps, ids = rec_step[:n_rec], rec_id[:n_rec]
                bounds = np.flatnonzero(np.diff(steps)) + 1
                for st, ii in zip(np.split(steps, bounds), np.split(ids, bounds)):
                    rec.append((int(st[0]), ii.copy()))
        return counts, rec

    def reset(self) -> None:
        self.v[:] = self.p.v_rest
        self.g[:] = 0
        self.buf[:] = 0
        self.ref_until[:] = 0
        self.flag[:] = 0
        self.active[:] = 0
        self.act_n[:] = 0
        self.t = 0
