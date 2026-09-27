"""Learning arm: dopamine-gated plasticity at Kenyon cell -> MBON synapses.

This is the fly's documented associative-learning mechanism (Aso et al. 2014; Hige et al. 2015; Handler et al.
2019): when a Kenyon cell (odor representation) has been active shortly before or while the dopamine neurons
innervating an MBON's compartment fire, the KC->MBON synapse is depressed. Each compartment's DANs carry one
valence (PAM = reward, PPL1 = punishment) and its MBON drives the opposite behaviour, so depression tips the
approach/avoidance balance toward the valence of the teaching signal.

Rule, applied once per tick of length dt (s):
    D_j   = synapse-weighted mean rate of the DANs presynaptic to MBON j (its compartment)  (Hz)
    e_i   = eligibility of KC i: its rate over the tick, or its decaying trace (tau_elig)    (Hz)
    dw_ij = -eta * (e_i / e_ref) * (D_j / D_ref) * dt * w0_ij            (depression only)
    w_ij  = clip(w_ij + dw_ij, w_min * w0_ij, w0_ij)  then slow recovery toward w0 (tau_rec)

The teaching signal (US). Two modes, chosen explicitly because they are different experiments:
  us="wiring"  Nothing is added: reward and punishment reach the DANs only if the connectome carries them
               there. Measured result (RESEARCH_NOTES 16): in the point-neuron model sugar, bitter and touch
               drive no DAN at all (0.0 Hz in every PAM and PPL1 type) — the sugar-reward pathway to PAM is
               octopaminergic/peptidergic (Burke et al. 2012), i.e. neuromodulatory, outside the model.
  us="dan"     The US is delivered the way optogenetic conditioning delivers it (Schroll et al. 2006; Claridge-
               Chang et al. 2009; Aso & Rubin 2016): the identified reward DANs (the appetitive PAM set:
               PAM-gamma5, -beta'2a, -beta2, -gamma4, -alpha1) are activated while the fly tastes sugar, the
               identified punishment DANs (PPL1-gamma1pedc, -gamma2alpha'1, -alpha3, -alpha'2alpha2) while it is
               hurt or tastes bitter. The DAN sets are selected by their dominant MBON target compartment in
               the connectome itself. Everything else — the odor code, the coincidence rule, the memory readout
               through MBONs to the descending neurons — is the fly's wiring. The US pathway is OURS.

With plasticity OFF the model is exactly Shiu et al.'s fixed connectome.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from .connectome import Connectome
from .lif import LIF

# The US dopamine neurons, by hemibrain type (Li et al. 2020), and the compartments (by MBON type) they teach.
# Reward: the appetitive PAM set whose activation substitutes for sugar (Aso & Rubin 2016; Yamagata et al. 2015;
# Huetteroth et al. 2015): PAM-gamma5 (PAM01), -beta'2a (PAM02), -beta2 (PAM04), -gamma4 (PAM08), -alpha1 (PAM11).
# Punishment: the shock-responsive PPL1 set (Aso et al. 2012; Aso & Rubin 2016): PPL1-gamma1pedc (PPL101),
# -gamma2alpha'1 (PPL103), -alpha'2alpha2 (PPL105), -alpha3 (PPL106). The compartment of each type is verified at
# start-up from its dominant MBON target in the connectome itself (printed), so a mislabeled type cannot slip in.
REWARD_DANS = ("PAM01", "PAM02", "PAM04", "PAM08", "PAM11")
PUNISH_DANS = ("PPL101", "PPL103", "PPL105", "PPL106")
REWARD_MBONS = {"MBON01": "gamma5beta'2a", "MBON02": "beta2beta'2a", "MBON03": "beta'2mp", "MBON05": "gamma4>gamma1gamma2", "MBON07": "alpha1"}
PUNISH_MBONS = {"MBON11": "gamma1pedc>alpha/beta", "MBON12": "gamma2alpha'1", "MBON31": "alpha'1", "MBON32": "gamma2", "MBON35": "gamma2",
                "MBON14": "alpha3", "MBON13": "alpha'2", "MBON18": "alpha2sc"}


@dataclass
class PlasticityConfig:
    eta: float = 0.3        # fraction of w0 lost per second of (e_ref, D_ref) pairing
    e_ref: float = 20.0     # Hz (an odor-driven KC under sparse coding fires ~10-40 Hz)
    d_ref: float = 20.0     # Hz
    w_min: float = 0.1      # floor as fraction of w0
    tau_rec: float = 600.0  # s, recovery toward w0 (0 = no recovery)
    tau_elig: float = 1.0   # s, KC eligibility trace (Handler et al. 2019: seconds-scale coincidence window)
    us: str = "wiring"      # "wiring" | "dan" (see module docstring)
    us_hz: float = 50.0     # Poisson activation rate of the US DANs while the US is present (us="dan")
    tau_dan: float = 0.0    # s; > 0 = phasic teaching signal: each DAN's rate minus its own running mean over tau_dan
                            # (real DAN odor and US responses are transient, ours are tonic under sustained Poisson
                            # drive; with tau_dan = 0 the tonic odor-evoked PPL1 activity of the model keeps teaching)


class MBPlasticity:
    def __init__(self, cx: Connectome, sim: LIF, cfg: PlasticityConfig | None = None, verbose: bool = True):
        self.cfg = cfg or PlasticityConfig()
        self.sim = sim
        kc = cx.select(cell_class="^Kenyon_Cell$")
        mbon = cx.select(cell_class="^MBON$")
        dan = cx.select(cell_class="^DAN$")
        self.kc, self.mbon, self.dan = kc, mbon, dan
        N = cx.n
        is_kc = np.zeros(N, bool); is_kc[kc] = True
        is_mbon = np.zeros(N, bool); is_mbon[mbon] = True

        # locate KC->MBON edges inside the CSR data array (so updates are in place)
        indptr, indices = sim.indptr, sim.indices
        rows = np.repeat(np.arange(N), np.diff(indptr))
        mask = is_kc[rows] & is_mbon[indices] & (sim.data > 0)
        self.e_idx = np.flatnonzero(mask)
        self.e_pre = rows[self.e_idx]
        self.e_post = indices[self.e_idx]
        self.w0 = sim.data[self.e_idx].copy()

        # DAN -> MBON compartment map from direct DAN->MBON connections
        W = sp.csr_matrix((np.abs(sim.data), indices, indptr), shape=(N, N))
        A = W[dan][:, mbon]                       # (n_dan, n_mbon) synapse counts
        self.A_syn = A.toarray().astype(np.float32)
        # compartment map: each MBON's DAN rate is the synapse-weighted mean over its presynaptic DANs (a DAN with
        # 400 synapses onto an MBON is that MBON's teacher; one with a stray synapse is not)
        self.A = self.A_syn / np.maximum(self.A_syn.sum(axis=0, keepdims=True), 1.0)
        self.mbon_pos = {m: j for j, m in enumerate(mbon)}
        self.post_col = np.array([self.mbon_pos[p] for p in self.e_post])
        kc_pos = {k: i for i, k in enumerate(kc)}
        self.pre_col = np.array([kc_pos[p] for p in self.e_pre])
        self.no_dan = int((A.sum(axis=0) == 0).sum())
        self.trace = np.zeros(len(kc), np.float32)
        self.dan_mean = np.zeros(len(dan), np.float32)

        # MBON compartments and the US DAN sets (by each DAN's dominant MBON target)
        types = cx.neurons.hemibrain_type.fillna(cx.neurons.cell_type).fillna("").astype(str)
        self.mbon_type = types.iloc[mbon].to_numpy()
        self.dan_type = types.iloc[dan].to_numpy()
        top = self.A_syn.argmax(axis=1)
        has = self.A_syn.max(axis=1) > 0
        top_type = np.where(has, self.mbon_type[top], "")
        self.reward_dan = dan[np.isin(self.dan_type, REWARD_DANS)]
        self.punish_dan = dan[np.isin(self.dan_type, PUNISH_DANS)]
        self.us_targets = {t: sorted(set(top_type[self.dan_type == t]) - {""}) for t in REWARD_DANS + PUNISH_DANS}
        bad = [t for t, m in self.us_targets.items() if m and not (set(m) & (set(REWARD_MBONS) if t in REWARD_DANS else set(PUNISH_MBONS)))]
        self.reward_cols = np.flatnonzero(np.isin(self.mbon_type, list(REWARD_MBONS)))
        self.punish_cols = np.flatnonzero(np.isin(self.mbon_type, list(PUNISH_MBONS)))
        self.in_reward = np.isin(self.post_col, self.reward_cols)
        self.in_punish = np.isin(self.post_col, self.punish_cols)
        self.us_reward = 0.0; self.us_punish = 0.0
        if verbose:
            print(f"[plasticity] {len(self.e_idx)} KC->MBON connections ({int(self.w0.sum())} synapses); "
                  f"{len(dan)} DANs -> {len(mbon)} MBONs; {self.no_dan} MBONs without direct DAN input; us={self.cfg.us}")
            desc = lambda ts: ", ".join(f"{t}->{'/'.join(self.us_targets[t]) or '?'}" for t in ts)
            print(f"[plasticity] reward DANs: {len(self.reward_dan)} ({desc(REWARD_DANS)})")
            print(f"[plasticity] punishment DANs: {len(self.punish_dan)} ({desc(PUNISH_DANS)})")
            if bad:
                print(f"[plasticity] WARNING: US DAN types whose dominant MBON target is outside the expected compartments: {bad}")

    # ---- teaching signal ----------------------------------------------------
    def us_drive(self, reward: float = 0.0, punish: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
        """(idx, rate) to add to the tick's sensory drive: the US DANs at us_hz x intensity (us='dan' only)."""
        self.us_reward, self.us_punish = float(reward), float(punish)
        if self.cfg.us != "dan":
            return np.zeros(0, np.int64), np.zeros(0, np.float32)
        idx, rate = [], []
        if reward > 0 and len(self.reward_dan):
            idx.append(self.reward_dan); rate.append(np.full(len(self.reward_dan), self.cfg.us_hz * min(reward, 1.0), np.float32))
        if punish > 0 and len(self.punish_dan):
            idx.append(self.punish_dan); rate.append(np.full(len(self.punish_dan), self.cfg.us_hz * min(punish, 1.0), np.float32))
        if not idx:
            return np.zeros(0, np.int64), np.zeros(0, np.float32)
        return np.concatenate(idx), np.concatenate(rate)

    # ---- the rule -----------------------------------------------------------
    def update(self, counts: np.ndarray, dt_s: float, learn: bool = True) -> dict:
        """Apply the rule for one tick (learn=False: plasticity frozen — weights untouched, statistics still returned)."""
        c = self.cfg
        kc_rate = (counts[self.kc] / dt_s).astype(np.float32)          # Hz per KC over this tick
        dan_rate = counts[self.dan] / dt_s
        decay = np.float32(np.exp(-dt_s / c.tau_elig)) if c.tau_elig > 0 else np.float32(0.0)
        self.trace = self.trace * decay + kc_rate * (1.0 - decay)
        w = self.sim.data[self.e_idx]
        if c.tau_dan > 0:                                           # phasic teaching signal (see PlasticityConfig)
            da = np.float32(np.exp(-dt_s / c.tau_dan))
            teach = np.maximum(dan_rate - self.dan_mean, 0.0)
            self.dan_mean = self.dan_mean * da + dan_rate.astype(np.float32) * (1.0 - da)
        else:
            teach = dan_rate
        if learn:
            elig = np.maximum(kc_rate, self.trace)
            D = teach @ self.A                                      # Hz per MBON (synapse-weighted mean over its DANs)
            e = elig[self.pre_col]
            dw = -c.eta * (e / c.e_ref) * (D[self.post_col] / c.d_ref) * dt_s * self.w0
            w = np.maximum(w + dw, c.w_min * self.w0)
            if c.tau_rec > 0:
                w += (self.w0 - w) * (dt_s / c.tau_rec)
            w = np.minimum(w, self.w0)
            self.sim.data[self.e_idx] = w.astype(np.float32)
        wr = float(w[self.in_reward].sum() / max(self.w0[self.in_reward].sum(), 1e-9)) if self.in_reward.any() else 1.0
        wp = float(w[self.in_punish].sum() / max(self.w0[self.in_punish].sum(), 1e-9)) if self.in_punish.any() else 1.0
        return {"kc_mbon_w_frac": float(w.sum() / self.w0.sum()), "w_frac_reward_comp": wr, "w_frac_punish_comp": wp,
                "dan_hz": float(dan_rate.mean()), "kc_hz": float(kc_rate.mean()), "kc_active": float((kc_rate > 0).mean()),
                "us_reward": self.us_reward, "us_punish": self.us_punish, "learning": int(learn)}

    def drive_by_mbon(self, counts: np.ndarray, dt_s: float) -> np.ndarray:
        """Synaptic drive each MBON receives from the KCs over a window: sum_i w_ij * rate_i (synapse-Hz), per MBON.
        The graded memory readout: what the plasticity did to an odor's input to each compartment, independent of
        whether the MBON's spike threshold is crossed."""
        kc_rate = counts[self.kc] / dt_s
        w = self.sim.data[self.e_idx]
        return np.bincount(self.post_col, weights=w * kc_rate[self.pre_col], minlength=len(self.mbon))

    def weights_by_compartment(self) -> dict:
        """Mean w/w0 per MBON type (which compartments hold the memory)."""
        w = self.sim.data[self.e_idx]
        out = {}
        for j, t in enumerate(self.mbon_type):
            m = self.post_col == j
            if m.any():
                out.setdefault(t, []).append(float(w[m].sum() / max(self.w0[m].sum(), 1e-9)))
        return {t: float(np.mean(v)) for t, v in out.items()}
