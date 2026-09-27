#!/usr/bin/env python3
"""Gold-standard check: run Shiu et al. 2024's *actual* Brian2 model on the same connectome and drive.

The model below is transcribed from github.com/philshiu/Drosophila_brain_model/model.py (equations, threshold,
reset, refractoriness, delay, PoissonInput weight = w_syn * f_poi). It needs Brian2 (kept out of the main
environment):  python -m venv b2venv && b2venv/bin/pip install brian2 numpy
Inputs come from export_for_brian2.py.  Example:
  b2venv/bin/python brain/tests/brian2_reference.py --conn flywire_export.npz --drive in_grn_sugar:100 --ms 1000 --seeds 3 --out ref_sugar.npz
Output npz: counts[seed, neuron] and the wall time; compare with the numba kernel via compare_brian2.py.
"""
import argparse, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--conn", required=True)
ap.add_argument("--drive", default="", help="comma list group:hz, e.g. in_grn_sugar:100,in_grn_bitter:100")
ap.add_argument("--ms", type=float, default=1000)
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--dt", type=float, default=0.1)
ap.add_argument("--gain", type=float, default=1.0)
ap.add_argument("--target", default="cython")
ap.add_argument("--out", required=True)
a = ap.parse_args()

from brian2 import (Hz, ms, mV, NeuronGroup, PoissonGroup, Synapses, SpikeMonitor, Network, defaultclock, prefs,
                    seed as b2seed, second, run)
prefs.codegen.target = a.target
defaultclock.dt = a.dt * ms

z = np.load(a.conn)
N = int(z["n"]); indptr, indices, data = z["indptr"], z["indices"], z["data"]
pre = np.repeat(np.arange(N), np.diff(indptr)).astype(np.int32); post = indices.astype(np.int32)
w_syn = 0.275 * float(z["w_syn_scale"]) * a.gain
print(f"{N} neurons, {len(pre)} connections, w_syn {w_syn:.4f} mV, dt {a.dt} ms, target {a.target}", flush=True)

params = {'v_0': -52 * mV, 'v_rst': -52 * mV, 'v_th': -45 * mV, 't_mbr': 20 * ms, 'tau': 5 * ms,
          't_rfc': 2.2 * ms, 't_dly': 1.8 * ms, 'w_syn': w_syn * mV, 'f_poi': 250}
eqs = '''
dv/dt = (v_0 - v + g) / t_mbr : volt (unless refractory)
dg/dt = -g / tau               : volt (unless refractory)
rfc                            : second
'''
drive = []
for item in [s for s in a.drive.split(",") if s]:
    g, hz = item.split(":"); drive.append((z[g], float(hz)))
counts = np.zeros((a.seeds, N), dtype=np.int32)
walls = []
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
        ps = Synapses(pg, neu, on_pre='v += w_syn * f_poi', namespace=params)
        ps.connect(i=np.arange(len(idx)), j=idx.astype(np.int32))
        objs += [pg, ps]
    mon = SpikeMonitor(neu, record=False)
    net = Network(*objs, mon)
    t0 = time.time(); net.run(a.ms * ms, report='text', report_period=20 * second); wall = time.time() - t0
    counts[s] = np.asarray(mon.count)
    walls.append(wall)
    print(f"seed {s}: {counts[s].sum()} spikes, {(counts[s] > 0).mean()*100:.2f}% active, {wall:.0f}s", flush=True)
np.savez(a.out, counts=counts, ms=a.ms, dt=a.dt, drive=a.drive, wall=np.array(walls))
print("wrote", a.out)
