#!/usr/bin/env python3
"""Edge-case copy of brian2_reference.py (RESEARCH_NOTES 23, design 2.8): Shiu et al. 2024's Brian2 model on an export,
with spike times, a background hum and a fixed kick size. Without the three new options it is brian2_reference.py
(same equations, same seeding, same objects), so its counts equal that script's to the spike.

  --record-times   SpikeMonitor(record=True); saves spk_i_<s> and spk_step_<s> = round(t/ms/dt) (int64) per seed,
                   for the spike-for-spike comparison in edge_brian2_divergence.py
  --noise-hz R     PoissonGroup(N) at R Hz, one-to-one onto the neurons, with the same kick as the drive
                   (the kernel's noise_hz; the random streams differ, so compare rates, not spikes)
  --kick-mv K      fixed kick size in mV for drive and noise. Default is Shiu's w_syn * f_poi, which scales with
                   gain and w_syn_scale; the kernel's kick is fixed at 68.75 mV, so the two agree only for the
                   female at gain 1 unless this is given

Brian2 lives in its own venv (numpy + brian2, no numba): the sidecar is written without the numba fields.
  b2venv/bin/python brain/tests/edge_brian2_reference.py --conn $B/flywire_export.npz --drive in_grn_sugar:100 \\
      --ms 1000 --seeds 3 --dt 0.1 --record-times --out experiments/results_edge/<step>/ref_sugar_times.npz
Output npz: counts[seed, neuron], wall, ms, dt, drive, gain, w_syn, kick_mv (nan = w_syn*f_poi), noise_hz, and with
--record-times spk_i_<s> / spk_step_<s>. Sidecar: <out>.json.
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "edge"))
import _edge

ap = argparse.ArgumentParser()
ap.add_argument("--conn", required=True)
ap.add_argument("--drive", default="", help="comma list group:hz, e.g. in_grn_sugar:100,in_grn_bitter:100")
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--dt", type=float, default=0.1)
ap.add_argument("--gain", type=float, default=1.0)
ap.add_argument("--target", default="cython")
ap.add_argument("--record-times", action="store_true", help="record every spike (neuron, step) per seed")
ap.add_argument("--noise-hz", type=float, default=0.0, help="background Poisson kicks on every neuron (Hz)")
ap.add_argument("--kick-mv", type=float, default=None, help="fixed kick in mV (default w_syn*f_poi, as Shiu)")
ap.add_argument("--out", required=True)
a = ap.parse_args()
tmp, final = _edge.safe_out(a.out)

import brian2
from brian2 import (Hz, ms, mV, NeuronGroup, PoissonGroup, Synapses, SpikeMonitor, Network, defaultclock, prefs,
                    seed as b2seed, second, run)
prefs.codegen.target = a.target
defaultclock.dt = a.dt * ms

z = np.load(a.conn)
N = int(z["n"]); indptr, indices, data = z["indptr"], z["indices"], z["data"]
pre = np.repeat(np.arange(N), np.diff(indptr)).astype(np.int32); post = indices.astype(np.int32)
w_syn = 0.275 * float(z["w_syn_scale"]) * a.gain
kick_txt = f"{a.kick_mv:g} mV fixed" if a.kick_mv is not None else f"w_syn*f_poi = {w_syn * 250:.4f} mV"
print(f"{N} neurons, {len(pre)} connections, w_syn {w_syn:.4f} mV, dt {a.dt} ms, target {a.target}, kick {kick_txt}, "
      f"noise {a.noise_hz:g} Hz, record_times {a.record_times}", flush=True)

params = {'v_0': -52 * mV, 'v_rst': -52 * mV, 'v_th': -45 * mV, 't_mbr': 20 * ms, 'tau': 5 * ms,
          't_rfc': 2.2 * ms, 't_dly': 1.8 * ms, 'w_syn': w_syn * mV, 'f_poi': 250}
# the default expression is brian2_reference.py's, character for character; --kick-mv swaps in a fixed size
on_kick = 'v += w_syn * f_poi'
if a.kick_mv is not None:
    params['kick'] = a.kick_mv * mV
    on_kick = 'v += kick'
eqs = '''
dv/dt = (v_0 - v + g) / t_mbr : volt (unless refractory)
dg/dt = -g / tau               : volt (unless refractory)
rfc                            : second
'''
drive = []
for item in [s for s in a.drive.split(",") if s]:
    g, hz = item.split(":"); drive.append((z[g], float(hz)))
counts = np.zeros((a.seeds, N), dtype=np.int32)
walls, times = [], {}
for s in range(a.seeds):
    b2seed(s); np.random.seed(s)
    neu = NeuronGroup(N, eqs, threshold='v > v_th', reset='v = v_rst; g = 0 * mV', refractory='rfc', method='linear',
                      namespace=params, name='neu')
    neu.v = params['v_0']; neu.g = 0 * mV; neu.rfc = params['t_rfc']
    syn = Synapses(neu, neu, 'w : volt', on_pre='g += w', delay=params['t_dly'], name='syn')
    syn.connect(i=pre, j=post)
    syn.w = data * params['w_syn']
    objs = [neu, syn]
    for idx, hz in drive:   # Shiu: PoissonInput(target=neu[i], target_var='v', N=1, rate=r_poi, weight=w_syn*f_poi)
        pg = PoissonGroup(len(idx), rates=hz * Hz)
        ps = Synapses(pg, neu, on_pre=on_kick, namespace=params)
        ps.connect(i=np.arange(len(idx)), j=idx.astype(np.int32))
        objs += [pg, ps]
    if a.noise_hz > 0:      # the hum: every neuron its own Poisson source (kernel: noise_hz)
        png = PoissonGroup(N, rates=a.noise_hz * Hz)
        pns = Synapses(png, neu, on_pre=on_kick, namespace=params)
        pns.connect(j='i')
        objs += [png, pns]
    mon = SpikeMonitor(neu, record=a.record_times)
    net = Network(*objs, mon)
    t0 = time.time(); net.run(a.ms * ms, report='text', report_period=20 * second); wall = time.time() - t0
    counts[s] = np.asarray(mon.count)
    walls.append(wall)
    if a.record_times:
        si = np.asarray(mon.i, dtype=np.int64)
        st = np.round(np.asarray(mon.t / ms) / a.dt).astype(np.int64)
        assert np.array_equal(np.bincount(si, minlength=N), counts[s]), "spike list does not add up to the counts"
        times[f"spk_i_{s}"], times[f"spk_step_{s}"] = si, st
    rec = f", {len(times[f'spk_i_{s}'])} spike times" if a.record_times else ""
    print(f"seed {s}: {counts[s].sum()} spikes, {(counts[s] > 0).mean()*100:.2f}% active, {wall:.0f}s{rec}", flush=True)
np.savez(tmp, counts=counts, ms=a.ms, dt=a.dt, drive=a.drive, wall=np.array(walls), gain=a.gain, w_syn=w_syn,
         kick_mv=np.nan if a.kick_mv is None else a.kick_mv, noise_hz=a.noise_hz, target=a.target,
         record_times=a.record_times, **times)
_edge.finish(tmp, final)

extra = {"brian2": brian2.__version__, "conn": os.path.abspath(a.conn), "n": N, "connections": int(len(pre)),
         "w_syn_mv": w_syn, "kick": kick_txt, "spikes_per_seed": counts.sum(1).tolist(), "wall_s": walls}
try:
    side = _edge.sidecar(final, extra)
except ImportError:     # b2venv has no numba: the same record minus the numba fields
    info = {"written": time.strftime("%Y-%m-%d %H:%M:%S"), "argv": sys.argv, "cwd": os.getcwd(),
            "env": {k: v for k, v in os.environ.items() if k.startswith("FLYBRAIN_") or k == "NUMBA_NUM_THREADS"},
            "python": sys.version.split()[0], "numpy": np.__version__, "numba": None,
            "sha256_lif": _edge._sha(os.path.join(_edge.ROOT, "brain", "flybrain", "lif.py")),
            "sha256_script": _edge._sha(os.path.abspath(sys.argv[0])), **extra}
    stmp, side = _edge.safe_out(os.path.splitext(final)[0] + ".json")
    with open(stmp, "w") as f:
        json.dump(info, f, indent=1, default=str)
    _edge.finish(stmp, side)
print("wrote", final, "and", side)
