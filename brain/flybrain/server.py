"""WebSocket brain server: receives observations from the Minecraft bot, returns controls."""
from __future__ import annotations

import asyncio
import json
import os
import time

import numpy as np

from . import connectome
from .lif import LIF, LIFParams
from .motor import MotorConfig, MotorDecoder
from .plasticity import MBPlasticity, PlasticityConfig, REWARD_MBONS, PUNISH_MBONS
from .recorder import Recorder, flatten
from .senses import SensoryEncoder

# Imposed internal states = tonic Poisson activity in the fly's own state neurons (all labeled in the connectome).
# With none of these the model is, in effect, a mated (SAG silent), starved (IPC silent), unaroused fly.
STATES = {
    "virgin": dict(hemibrain_type=r"^SAG$"),            # sex-peptide pathway: active in virgins, silenced by mating
    "fed": dict(cell_type=r"^IPC$"),                    # insulin-producing cells: active when fed
    "hungry": dict(cell_type=r"^NPFL1-I$|^DNp29$"),     # NPF neurons
    "aroused": dict(cell_type=r"^pC1[abc]$"),           # female receptivity hub (pC1a-c)
    "aggressive": dict(cell_type=r"^pC1[de]$"),         # female aggression hub (pC1d/e)
    "courting": dict(cell_type=r"^pC1_|^P1_"),          # male P1 courtship command cluster
}


# What in the world counts as the unconditioned stimulus (learning arm, --us dan): OUR design, listed here.
#   reward     = tasting sugar (standing on / next to a nectar or sugar block)             -> appetitive PAM DANs
#   punishment = being hurt (health loss), tasting bitter, or standing in heat            -> PPL1 punishment DANs
def us_from_obs(obs: dict) -> tuple[float, float]:
    ta, me, th = obs.get("taste") or {}, obs.get("mechano") or {}, obs.get("thermo") or {}
    hot = th.get("hot", 0); hot = max(hot.values()) if isinstance(hot, dict) else float(hot or 0)
    reward = float(ta.get("sugar", 0) or 0)
    punish = max(float(ta.get("bitter", 0) or 0), 1.0 if me.get("hit") else 0.0, min(1.0, 2.0 * float(hot)))
    return reward, punish


class Brain:
    def __init__(self, name: str, brain_ms: float, dt: float, noise_hz: float, plasticity: str,
                 pop_turn_w: float, log_dir: str, seed: int, record_spikes: bool, state: str = "", state_hz: float = 30.0,
                 gain: float = 1.0, vision: str = "lif", signs: str | None = None, eln_scale: float | None = None,
                 us: str = "wiring", us_hz: float = 50.0, tau_dan: float = 0.0, unclear_ln: str | None = None,
                 mask: str = ""):
        self.name, self.brain_ms = name, brain_ms
        print(f"[{name}] loading connectome ...", flush=True)
        self.cx = connectome.load(signs=signs, eln_scale=eln_scale, unclear_ln=unclear_ln)
        print(f"[{name}] {self.cx}", flush=True)
        self.sim = LIF(self.cx.W, LIFParams(dt=dt, noise_hz=noise_hz, w_syn=0.275 * self.cx.w_syn_scale * gain), seed=seed)
        self.senses = SensoryEncoder(self.cx)
        self.senses.mask = {m for m in mask.split(",") if m}
        unknown = self.senses.mask - set(self.senses.groups)
        if unknown:
            raise SystemExit(f"--mask: unknown input channel(s) {sorted(unknown)}; channels: {sorted(self.senses.groups)}")
        self.vision = vision
        if vision == "flyvis":
            from .vision import OpticLobe
            self.senses.optic_lobe = OpticLobe(self.cx, self.senses, sim=self.sim)
        self.motor = MotorDecoder(self.cx, MotorConfig(pop_turn_w=pop_turn_w), seed=seed)
        self.plast = MBPlasticity(self.cx, self.sim, PlasticityConfig(us=us, us_hz=us_hz, tau_dan=tau_dan)) if plasticity == "mb" else None
        # imposed internal state(s): tonic drive added to every tick's sensory drive
        self.state_idx, self.state_rate = np.zeros(0, np.int64), np.zeros(0, np.float32)
        self.state = [s for s in state.split(",") if s]
        for s in self.state:
            idx = self.cx.select(**STATES[s])
            print(f"[{name}] state '{s}': {self.cx.describe(idx)} at {state_hz} Hz", flush=True)
            self.state_idx = np.concatenate([self.state_idx, idx]); self.state_rate = np.concatenate([self.state_rate, np.full(len(idx), state_hz, np.float32)])
        stamp = time.strftime("%Y%m%d-%H%M%S")
        ds = os.environ.get("FLYBRAIN_DATASET", "flywire")
        tag = f"{plasticity}-{ds}" + (f"-{'+'.join(self.state)}" if self.state else "") + (f"-{us}" if plasticity == "mb" else "") + (f"-phasic{tau_dan:g}" if plasticity == "mb" and tau_dan > 0 else "")
        if noise_hz > 0:                                # a background-noise "walking substrate" is ours: it goes in the name (RESEARCH_NOTES 19a)
            tag += f"-noise{noise_hz:g}"
        if self.senses.mask:                            # a removed input channel goes in the name too (RESEARCH_NOTES 23)
            tag += "-mask" + "+".join(sorted(self.senses.mask))
        if self.cx.signs != "shiu" or self.cx.eln_scale != 1.0 or self.cx.unclear_ln != "excitatory":
            tag += "-" + self.cx.variant.split("+", 1)[1].replace("+", "-")
        self.rec = Recorder(os.path.join(log_dir, f"{name}_{tag}_{stamp}.csv"))
        self.record_mask = None
        self.spikes = []
        if record_spikes:
            self.record_mask = np.zeros(self.cx.n, bool)
            for g in ("dn_all", "aggression", "feed", "mb_mbon", "mb_dan"):
                self.record_mask[self.motor.groups[g]] = True
            self.spike_path = os.path.join(log_dir, f"{name}_{tag}_{stamp}_spikes.npz")
        self.tick = 0
        self.frozen = False
        print(f"[{name}] ready  (plasticity={plasticity}{', us=' + us if plasticity == 'mb' else ''}, state={self.state or 'none'}, vision={vision}, "
              f"model={self.cx.variant}, brain_ms/tick={brain_ms}, dt={dt} ms, noise={noise_hz} Hz, gain={gain})", flush=True)

    def process(self, obs: dict) -> dict:
        t0 = time.perf_counter()
        idx, rate = self.senses.encode(obs)
        if len(self.state_idx):
            idx = np.concatenate([idx, self.state_idx]); rate = np.concatenate([rate, self.state_rate])
        if self.plast is not None:                      # teaching signal from the world (see us_from_obs)
            ui, ur = self.plast.us_drive(*us_from_obs(obs))
            if len(ui):
                idx = np.concatenate([idx, ui]); rate = np.concatenate([rate, ur])
        self.sim.set_drive(idx, rate)
        counts, rec = self.sim.run(self.brain_ms, self.record_mask)
        if rec:
            self.spikes.extend(rec)
        window_s = self.brain_ms / 1000.0
        controls, rates = self.motor.decode(counts, window_s)
        pstats = self.plast.update(counts, window_s, learn=not self.frozen) if self.plast else {}
        wall = time.perf_counter() - t0
        self.tick += 1
        row = {"tick": self.tick, "t_wall": time.time(), "brain_t_ms": self.sim.t * self.sim.p.dt,
               "wall_ms": round(wall * 1000, 1)}
        meta = obs.get("meta") or {}
        for k in ("x", "y", "z", "yaw", "hp", "game_tick", "trial", "sex"):
            row[k] = meta.get(k)
        flatten("ctl_", controls, row)
        flatten("hz_", {k: round(v, 2) if isinstance(v, float) else v for k, v in rates.items()}, row)
        flatten("obs_smell_", {k: v for k, v in (obs.get("smell") or {}).items() if k != "odors"}, row)
        flatten("odor_", (obs.get("smell") or {}).get("odors"), row)
        flatten("obs_taste_", obs.get("taste"), row)
        flatten("obs_mech_", obs.get("mechano"), row)
        flatten("obs_", {"sound": obs.get("sound", 0)}, row)
        flatten("near_", meta.get("near_fly") or {"name": None, "dist": None, "az": None}, row)
        flatten("pl_", pstats, row)
        if self.senses.optic_lobe is not None:
            row["vis_frames"] = self.senses.optic_lobe.n_frames; row["vis_ms"] = round(self.senses.optic_lobe.wall_ms, 1)
        self.rec.write(row)
        if self.tick % 40 == 0:
            acts = ",".join(k for k in ("jump", "attack", "feed", "sing", "court", "egg", "accept", "reject") if controls.get(k))
            mb = f" | KC {rates['mb_kc']:.1f} MBON {rates['mb_mbon']:.1f}" + (f" w {pstats['kc_mbon_w_frac']:.3f} (R {pstats['w_frac_reward_comp']:.3f} P {pstats['w_frac_punish_comp']:.3f}) us {pstats['us_reward']:.0f}/{pstats['us_punish']:.0f}" if pstats else "")
            print(f"[{self.name}] tick {self.tick} wall {wall*1000:.0f}ms spikes {rates['total_spikes']} "
                  f"walk {controls['walk']:.2f} back {controls['back']:.2f} turn {controls['turn']:+.2f} | "
                  f"DNa L/R {rates['turn_L']:.1f}/{rates['turn_R']:.1f} p09 {rates['dnp09']:.1f} legMN {rates['leg_mn']:.1f} "
                  f"aggr {rates['aggression']:.1f} feed {rates['feed']:.1f} sing {rates['sing']:.1f} P1 {rates['court_p1']:.1f} "
                  f"DNp13 {rates['reject']:.1f}{mb} | acts: {acts or '-'}", flush=True)
        return {"controls": controls, "rates": rates, "wall_ms": round(wall * 1000, 1), "brain_ms": self.brain_ms, "tick": self.tick}

    def probe(self, odors, hz: float = 150.0, ms: float = 1000.0) -> dict:
        """Graded memory readout on an idle brain (call it before the body connects or after it has left): each odor
        class of the library is presented bilaterally at `hz` for `ms` with the membrane state reset, and the KC->MBON
        synaptic drive per compartment (plasticity.drive_by_mbon) plus the KC / MBON activity are returned. The same
        measure as experiments/conditioning.py, so an in-world memory can be read the way the offline one is."""
        out = {}
        for cls in odors:
            self.sim.reset(); self.sim.set_drive(*self.senses.odor(cls, r_max=hz))
            counts, _ = self.sim.run(ms)
            kc, mbon = self.motor.groups["mb_kc"], self.motor.groups["mb_mbon"]
            r = {"kc_active": float((counts[kc] > 0).mean()), "mbon_hz": float(counts[mbon].sum() / max(len(mbon), 1) / (ms / 1000))}
            if self.plast is not None:
                drv = self.plast.drive_by_mbon(counts, ms / 1000); types = self.plast.mbon_type
                r["drive_reward_comp"] = float(drv[np.isin(types, list(REWARD_MBONS))].sum())
                r["drive_punish_comp"] = float(drv[np.isin(types, list(PUNISH_MBONS))].sum())
                r["drive_all"] = float(drv.sum())
                by = {}
                for t, v in zip(types, drv):
                    by[t] = by.get(t, 0.0) + float(v)
                r["drive_by_type"] = by
            out[cls] = r
        self.sim.reset()
        return out

    def close(self):
        self.rec.close()
        if self.record_mask is not None and self.spikes:
            steps = np.concatenate([np.full(len(i), s) for s, i in self.spikes])
            ids = np.concatenate([i for _, i in self.spikes])
            np.savez_compressed(self.spike_path, step=steps, neuron=ids, dt_ms=self.sim.p.dt,
                                root_ids=self.cx.root_ids[ids])


async def serve(brain: Brain, host: str, port: int):
    import websockets

    async def handler(ws):
        print(f"[{brain.name}] bot connected", flush=True)
        try:
            async for msg in ws:
                data = json.loads(msg)
                if data.get("cmd") == "reset":
                    brain.sim.reset(); await ws.send(json.dumps({"ok": True})); continue
                if data.get("cmd") == "memory":       # which compartments hold the memory (learning arm)
                    await ws.send(json.dumps({"ok": True, "w_by_compartment": brain.plast.weights_by_compartment() if brain.plast else {}})); continue
                if data.get("cmd") == "probe":        # graded memory readout: odor classes presented to the idle brain
                    res = await asyncio.get_running_loop().run_in_executor(None, brain.probe, data.get("odors") or ["ester", "vinegar"], float(data.get("hz", 150)), float(data.get("ms", 1000)))
                    await ws.send(json.dumps({"ok": True, "probe": res})); continue
                if data.get("cmd") == "plasticity":   # freeze / unfreeze learning without restarting the brain
                    brain.frozen = not bool(data.get("on", True)); await ws.send(json.dumps({"ok": True, "frozen": brain.frozen})); continue
                reply = await asyncio.get_running_loop().run_in_executor(None, brain.process, data)
                await ws.send(json.dumps(reply))
        except websockets.ConnectionClosed:
            pass
        finally:
            print(f"[{brain.name}] bot disconnected", flush=True)

    async with websockets.serve(handler, host, port, max_size=8 * 1024 * 1024):
        print(f"[{brain.name}] listening on ws://{host}:{port}", flush=True)
        await asyncio.Future()
