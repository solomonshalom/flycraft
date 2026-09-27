"""Read the fly's descending / motor neurons out as body drives — continuous, threshold-free.

Only neurons with a published behavioral role are used as named readouts:
  DNp09        forward walking / pursuit        (Bidaye et al. 2020; Zacarias et al. 2018)
  DNa01, DNa02 ipsilateral turning while walking (Rayshubskiy et al. 2020; Chen et al. 2018;
               Braun et al. 2024: walking is encoded by a DN population, so forward = DNp09 + DNa01/02)
  MDN          backward walking ("moonwalker")  (Bidaye et al. 2014)
  DNp01 (GF)   giant fiber: escape jump/takeoff (Card & Strausfeld 2010)
  pC1d/e, aIPg female aggression                (Schretter et al. 2020; Deutsch et al. 2020)
  proboscis + ingestion motor neurons: feeding  (Shiu et al. 2024 used MN9)
  oviDN        egg laying                       (Wang et al. 2020)
  vpoDN (DNp37) female sexual receptivity       (Wang et al. 2021)
  DNp13        ovipositor extrusion / rejection (female)
  pIP10        courtship song command (MALE ONLY — absent in FlyWire, present in MaleCNS)
  leg / wing motor neurons (MaleCNS: the nerve cord is present, so walking and song are read from the
               fly's own motor neurons, the last neural stage before muscle)

How rates become movement ("more neural, less mechanical"):
  * No thresholds. Each drive is a saturating function of a population rate, d = 1 - exp(-rate / k), in [0, 1].
    The body applies walking as a duty cycle (fraction of physics ticks spent walking), so speed follows the
    motor-neuron rate continuously; turning is tanh of the left-minus-right rate; backing competes with walking.
  * Discrete acts (lunge, proboscis extension, song bout, egg-laying, acceptance, rejection) are Poisson events
    whose rate is proportional to the corresponding neurons' firing rate — the brain draws them, so the log
    records what the body actually did. The giant fiber's spikes are the jump (one spike = one takeoff).
  * With the nerve cord present (MaleCNS) walking is the leg motor-neuron population (forward drive = mean leg
    MN rate; turning adds the left-minus-right leg MN rate); song is the wing motor neurons. Without it (FlyWire)
    the descending neurons are the last stage available.
  * The population-turn heuristic of the first version (left-minus-right of *all* descending neurons) is off by
    default (`pop_turn_w = 0`); it is kept only as an option for comparison.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .connectome import Connectome


@dataclass
class MotorConfig:
    k_walk_hz: float = 10.0       # DN walking population rate that gives 63 % of maximal walking drive
    k_leg_hz: float = 8.0         # MaleCNS: leg MN population rate for the same
    k_back_hz: float = 10.0       # MDN rate
    k_turn_hz: float = 40.0       # L-R DNa rate difference (Hz) that gives a tanh of 0.76
    k_leg_turn_hz: float = 8.0    # MaleCNS: leg MN L-R rate difference for the same
    k_act_hz: float = 10.0        # saturating constant for act intensities (feed, court, ...)
    lunge_per_hz: float = 0.2     # attack events per second per Hz of aggression-neuron rate (5 Hz -> 1 lunge/s)
    per_per_hz: float = 0.05      # proboscis-extension events per second per Hz of feeding-MN rate (40 Hz -> 2/s)
    song_per_hz: float = 0.1      # song bouts per second per Hz of song command/wing-MN rate
    event_per_hz: float = 0.1     # egg-laying / acceptance / rejection events per second per Hz
    pop_turn_w: float = 0.0       # first-version heuristic (0 = identified neurons only)
    k_pop_hz: float = 5.0


class MotorDecoder:
    def __init__(self, cx: Connectome, cfg: MotorConfig | None = None, verbose: bool = True, seed: int = 0):
        self.cx = cx
        self.cfg = cfg or MotorConfig()
        self.rng = np.random.default_rng(seed)
        s = cx.select
        self.groups = {
            "dnp09": s(cell_type=r"^DNp09$"),
            "forward": s(cell_type=r"^DNp09$|^DNa0[12]$"),   # walking DNs: DNp09 + DNa01/DNa02 (turn *while walking*)
            "turn_L": s(cell_type=r"^DNa0[12]$", side="^left$"),
            "turn_R": s(cell_type=r"^DNa0[12]$", side="^right$"),
            "back": s(cell_type=r"^MDN$"),
            "jump": s(cell_type=r"^DNp01$"),
            "aggression": s(any_of={"cell_type": r"^pC1[de]$", "hemibrain_type": r"^aIPg"}),
            "feed": s(any_of={"cell_sub_class": r"proboscis_motor_neuron|ingestion_motor_neuron|^pm$", "cell_type": r"^MN9$"}),
            "egg": s(cell_type=r"^oviDN"),
            "accept": s(cell_type=r"^DNp37$"),
            "reject": s(cell_type=r"^DNp13$"),                                                   # ovipositor extrusion (female rejection) DN
            "sing": s(any_of={"cell_type": r"^pIP10", "hemibrain_type": r"^pIP10"}),          # male song command DN
            "song_mn": s(cell_type=r"^(ps1|i1|i2|hg[0-9]) MN"),                                  # song wing-muscle MNs (MaleCNS)
            "wing_mn": s(super_class="^motor$", cell_sub_class="^wm$"),                          # all wing MNs (MaleCNS)
            "court_p1": s(cell_type=r"^pC1_|^P1_"),                                              # male P1/pC1 courtship cluster (MaleCNS)
            "leg_mn": s(super_class="^motor$", cell_sub_class="^(fl|ml|hl)$"),                    # leg motor neurons (MaleCNS)
            "leg_mn_L": s(super_class="^motor$", cell_sub_class="^(fl|ml|hl)$", side="^left$"),
            "leg_mn_R": s(super_class="^motor$", cell_sub_class="^(fl|ml|hl)$", side="^right$"),
            "dn_L": s(super_class="^descending$", side="^left$"),
            "dn_R": s(super_class="^descending$", side="^right$"),
            "dn_all": s(super_class="^descending$"),
            "mb_kc": s(cell_class="^Kenyon_Cell$"),
            "mb_mbon": s(cell_class="^MBON$"),
            "mb_dan": s(cell_class="^DAN$"),
            "sag": s(hemibrain_type=r"^SAG$"),
            "ipc": s(cell_type=r"^IPC$"),
        }
        self.has_vnc = len(self.groups["leg_mn"]) > 0
        if verbose:
            for k, v in self.groups.items():
                print(f"[motor]  {k:11s} {cx.describe(v)}")
            print(f"[motor]  nerve cord present: {self.has_vnc} -> walking read from {'leg motor neurons' if self.has_vnc else 'descending neurons'}")

    def rates(self, counts: np.ndarray, window_s: float) -> dict:
        out = {}
        for k, idx in self.groups.items():
            out[k] = float(counts[idx].sum()) / (len(idx) * window_s) if len(idx) else 0.0
        out["total_spikes"] = int(counts.sum())
        out["active_frac"] = float((counts > 0).mean())
        return out

    @staticmethod
    def _sat(rate: float, k: float) -> float:
        return float(1.0 - np.exp(-max(rate, 0.0) / k))

    def _event(self, rate_hz: float, per_hz: float, window_s: float) -> bool:
        lam = max(rate_hz, 0.0) * per_hz * window_s
        return bool(self.rng.random() < 1.0 - np.exp(-lam))

    def decode(self, counts: np.ndarray, window_s: float) -> tuple[dict, dict]:
        r = self.rates(counts, window_s)
        c = self.cfg
        if self.has_vnc:
            walk = self._sat(r["leg_mn"], c.k_leg_hz)
            turn = np.tanh((r["turn_L"] - r["turn_R"]) / c.k_turn_hz) + np.tanh((r["leg_mn_L"] - r["leg_mn_R"]) / c.k_leg_turn_hz)
        else:
            walk = self._sat(r["forward"], c.k_walk_hz)
            turn = np.tanh((r["turn_L"] - r["turn_R"]) / c.k_turn_hz)
        if c.pop_turn_w:
            turn += c.pop_turn_w * np.clip((r["dn_L"] - r["dn_R"]) / c.k_pop_hz, -1, 1)
        back = self._sat(r["back"], c.k_back_hz)
        song_rate = r["song_mn"] if len(self.groups["song_mn"]) and r["song_mn"] > 0 else r["sing"]
        controls = {
            "walk": round(walk, 3),                       # duty cycle of forward walking in [0, 1]
            "back": round(back, 3),                       # duty cycle of backward walking (wins over walk if larger)
            "turn": round(float(np.clip(turn, -1, 1)), 3),   # +1 = turn left at the maximal rate
            "jump": bool(counts[self.groups["jump"]].sum() > 0),
            "attack": self._event(r["aggression"], c.lunge_per_hz, window_s),
            "feed": self._event(r["feed"], c.per_per_hz, window_s),
            "sing": self._event(song_rate, c.song_per_hz, window_s) if (len(self.groups["sing"]) or len(self.groups["song_mn"])) else False,
            "court": self._event(r["court_p1"], c.event_per_hz, window_s) if len(self.groups["court_p1"]) else False,
            "egg": self._event(r["egg"], c.event_per_hz, window_s),
            "accept": self._event(r["accept"], c.event_per_hz, window_s),
            "reject": self._event(r["reject"], c.event_per_hz, window_s),
            # intensities (for plots / analysis; the events above are what the body does)
            "feed_drive": round(self._sat(r["feed"], c.k_act_hz), 3),
            "aggr_drive": round(self._sat(r["aggression"], c.k_act_hz), 3),
            "song_drive": round(self._sat(song_rate, c.k_act_hz), 3),
        }
        return controls, r
