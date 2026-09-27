#!/usr/bin/env python3
"""Where do the numba kernel and Brian2 part ways? (RESEARCH_NOTES 23, design 2.8, step S5 "brian2-first-divergence")

compare_brian2.py compares spike counts; this compares every spike. For each seed it runs the kernel on the export
the Brian2 reference used, with the reference's drive, and:
  pass 1   counts (unmasked run);  record mask = every neuron active in Brian2 or in the kernel
  pass 2   the same run with the mask -> (step, neuron) list; asserts pass 2 counts == pass 1 counts
  split    run(a) then run(b) == run(a+b) (the trace below depends on it)
  compare  sorted (step, neuron) lists after a step offset calibrated on --calib-seed (0 expected: both record the
           step whose integration crossed threshold; 0 is used if no offset aligns half the spikes, e.g. the hum)
  trace    at the first mismatched step: re-run deterministically to step-20, then one dt at a time, and report the
           neuron's kernel state each step: v, g, the arrival, the integrated v that meets threshold, and its margin
           v_thr - v_int. A margin within ~0.01 mV is a rounding / eps-snap event; > 0.05 mV is a semantic difference;
           v already above threshold before the step means a kick (different random draw, or discarded while refractory).
A reference made with --noise-hz draws the hum from another stream than the kernel: expect rates, not spikes, to agree.
Options change the kernel only: --eps-v/--eps-g (0 = never snap to rest), --float64 (v, g, buf, weights and w_syn in
float64; numba compiles a float64 specialisation). NUMBA_CACHE_DIR defaults to $TMPDIR/flycraft_edge_nbcache so the
new specialisations never land in brain/flybrain/__pycache__.

  python3 brain/tests/edge_brian2_divergence.py --conn $B/flywire_export.npz --ref $O/ref_sugar_times.npz --dt 0.1 \\
      [--seeds 0 1 2] [--eps-v 0 --eps-g 0] [--float64] --out $O/div_default.json
The reference must come from edge_brian2_reference.py --record-times. Writes --out (JSON report), <out>_seeds.csv,
<out>_trace.csv and the sidecar <out>.sidecar.json. Exits 1 (after writing) if an internal assert fails.
"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "experiments", "edge"))
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(os.environ.get("TMPDIR", "/tmp"), "flycraft_edge_nbcache"))
import numpy as np, pandas as pd, scipy.sparse as sp
import _edge
from flybrain import lif
from flybrain.lif import LIF, LIFParams

ap = argparse.ArgumentParser()
ap.add_argument("--conn", required=True)
ap.add_argument("--ref", required=True, help="edge_brian2_reference.py output made with --record-times")
ap.add_argument("--dt", type=float, default=None, help="must equal the reference's dt (default: read from --ref)")
ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
ap.add_argument("--eps-v", type=float, default=None, help="kernel snap-to-rest threshold on |v - v_rest| (mV)")
ap.add_argument("--eps-g", type=float, default=None, help="kernel snap-to-rest threshold on |g| (mV)")
ap.add_argument("--float64", action="store_true", help="kernel state and weights in float64")
ap.add_argument("--calib-seed", type=int, default=1, help="seed the step offset is calibrated on (else the first)")
ap.add_argument("--max-offset", type=int, default=3)
ap.add_argument("--window", type=int, default=20, help="steps traced before the first mismatch")
ap.add_argument("--after", type=int, default=2, help="steps traced after it")
ap.add_argument("--max-trace", type=int, default=4, help="mismatched neurons traced at that step")
ap.add_argument("--out", required=True)
a = ap.parse_args()
base = os.path.splitext(a.out)[0]
outs = {k: _edge.safe_out(p) for k, p in
        (("json", a.out), ("seeds", base + "_seeds.csv"), ("trace", base + "_trace.csv"))}


class LIF64(LIF):
    """The kernel with float64 v, g, buf, weights and w_syn (lif.LIF._call passes w_syn as float32)."""
    def __init__(self, W, p, seed=0):
        super().__init__(W, p, seed)
        self.v, self.g, self.buf = (x.astype(np.float64) for x in (self.v, self.g, self.buf))
        self.data = self.data.astype(np.float64); self.data0 = self.data.copy()

    def _call(self, k, counts, mask, rec_step, rec_id):   # lif.LIF._call, w_syn as float64
        p = self.p
        extra_cap = len(self.forced_idx) + (int(4 * p.noise_hz * self.dt_s * self.N) + 64 if p.noise_hz > 0 else 0)
        extra_buf = np.zeros(max(1, extra_cap), dtype=np.int64)
        n_rec = lif._run(k, self.t, self.v, self.g, self.ref_until, self.buf, self.indptr, self.indices,
                         self.data, np.float64(p.w_syn), p.v_rest, p.v_reset, p.v_thr, self.a_m, self.b_g,
                         self.c_g, self.e_m, self.ref_steps, self.wr_off, self.forced_idx, self.forced_p,
                         p.kick_mv, float(p.noise_hz * self.dt_s), p.legacy, p.eps_v, p.eps_g,
                         counts, mask, rec_step, rec_id, self.spk_buf, self.spk_n, extra_buf, self.flag, self.active,
                         self.act_buf, self.act_n, self.par_min)
        self.t += k
        return n_rec


# ---- reference, export, kernel ----
z = np.load(a.conn); r = np.load(a.ref)
N = int(z["n"])
dt, ms = float(r["dt"]), float(r["ms"])
if a.dt is not None and abs(a.dt - dt) > 1e-9:
    raise SystemExit(f"--dt {a.dt} differs from the reference's dt {dt}: a spike-for-spike comparison needs the same dt")
missing = [s for s in a.seeds if f"spk_i_{s}" not in r.files]
if missing:
    raise SystemExit(f"{a.ref} has no spike times for seeds {missing}: make it with edge_brian2_reference.py --record-times")
ref_counts = r["counts"]
if ref_counts.shape[1] != N:
    raise SystemExit(f"{a.ref} has {ref_counts.shape[1]} neurons, {a.conn} has {N}: not the reference's export")
n_steps = max(1, int(round(ms / dt)))    # as LIF.run; the kernel's recorded steps are 0..n_steps-1
notes = []
try:    # the reference's sidecar names its export: a spike-for-spike comparison against another one means nothing
    ref_conn = json.load(open(os.path.splitext(a.ref)[0] + ".json")).get("conn")
except (OSError, ValueError):
    ref_conn = None
if ref_conn and os.path.realpath(ref_conn) != os.path.realpath(a.conn):
    notes.append(f"the reference was made from {ref_conn}, not {os.path.realpath(a.conn)}")
gain = float(r["gain"]) if "gain" in r.files else 1.0
noise_hz = float(r["noise_hz"]) if "noise_hz" in r.files else 0.0
kick_ref = float(r["kick_mv"]) if "kick_mv" in r.files else np.nan
drive = [s for s in str(r["drive"]).split(",") if s]
idx = np.concatenate([z[d.split(":")[0]] for d in drive]) if drive else np.zeros(0, np.int64)
rate = (np.concatenate([np.full(len(z[d.split(":")[0]]), float(d.split(":")[1]), np.float32) for d in drive])
        if drive else np.zeros(0, np.float32))
groups = {k: set(z[k].tolist()) for k in z.files if k.startswith(("in_", "out_"))}
W = sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(N, N))

w_syn = 0.275 * float(z["w_syn_scale"]) * gain
over = {k: v for k, v in (("eps_v", a.eps_v), ("eps_g", a.eps_g)) if v is not None}
p = LIFParams(dt=dt, w_syn=w_syn, noise_hz=noise_hz, **over)
kick = kick_ref if np.isfinite(kick_ref) else w_syn * 250.0   # Brian2's kick: fixed, or w_syn * f_poi
if kick != p.kick_mv:
    notes.append(f"kernel kick set to Brian2's {kick:.4f} mV (default {p.kick_mv:.4f})"); p.kick_mv = kick
if len(drive) > 1 or (len(idx) and not (np.diff(idx) > 0).all()):
    notes.append("Brian2 draws kicks per drive group in its own order, the kernel over the sorted union (overlaps at the "
                 "max rate): unless the groups are disjoint and ascending, spikes will not match and a mismatch on a "
                 "driven neuron is a random-stream difference, not a semantic one")
if noise_hz > 0:
    notes.append(f"noise {noise_hz:g} Hz: the kernel and Brian2 draw the hum from different streams, spikes will not match")
sim = (LIF64 if a.float64 else LIF)(W, p, seed=0)
del W
nslot = sim.buf.shape[0]
print(f"{N} neurons, dt {dt} ms, {ms:g} ms, drive {','.join(drive) or 'none'}, w_syn {w_syn:.4f} mV, kick {p.kick_mv:g} mV, "
      f"eps_v {p.eps_v:g}, eps_g {p.eps_g:g}, {'float64' if a.float64 else 'float32'}, chunks T={sim.T}, "
      f"NUMBA_CACHE_DIR={os.environ['NUMBA_CACHE_DIR']}", flush=True)
for n in notes:
    print("note:", n)


def fresh(s):
    sim.seed(s); sim.reset(); sim.set_drive(idx, rate)


def keys(step, i):
    return np.unique(np.asarray(step, np.int64) * N + np.asarray(i, np.int64))


def kernel_lists(s):
    """pass 1 (counts), pass 2 (masked, the list), and the split-run check."""
    fresh(s); t0 = time.perf_counter(); c1, _ = sim.run(ms); wall = time.perf_counter() - t0
    mask = (ref_counts[s] > 0) | (c1 > 0)
    fresh(s); c2, rec = sim.run(ms, mask)
    h = n_steps // 2
    fresh(s); ca, _ = sim.run(h * dt); cb, _ = sim.run((n_steps - h) * dt)
    ks = np.concatenate([np.full(len(ii), st, np.int64) for st, ii in rec]) if rec else np.zeros(0, np.int64)
    ki = np.concatenate([ii for _, ii in rec]) if rec else np.zeros(0, np.int64)
    return c1, ks, ki, bool(np.array_equal(c1, c2)), bool(np.array_equal(ca + cb, c1)), wall


def trace(s, S, neurons, b2key, kkey):
    """Kernel state of `neurons` from step S-window to S+after (never past the run's last step, where the recorded list
    ends), one dt at a time after a deterministic re-run. Returns the rows, the spike counts up to `end`, and `end`."""
    fresh(s)
    start, end = max(0, S - a.window), min(S + a.after, n_steps - 1)
    acc = np.zeros(N, np.int64)
    if start:
        c, _ = sim.run(start * dt); acc += c
    rows = []
    for t in range(start, end + 1):
        assert sim.t == t
        slot = t % nslot
        pre = []
        for i in neurons:   # emulate _integrate for neuron i (same dtypes, same operation order)
            ref_until = int(sim.ref_until[i]); arrival = sim.buf[slot, i]
            gi = sim.g[i] if t <= ref_until else sim.g[i] + arrival
            v_int = (p.v_rest + (float(sim.v[i]) - p.v_rest) * sim.a_m + float(gi) * sim.b_g) if t >= ref_until else np.nan
            pre.append((i, t < ref_until, int(sim.active[i]), float(arrival), float(sim.g[i]), float(sim.v[i]), v_int))
        c, _ = sim.run(dt); acc += c
        for i, refr, act, arr, g0, v0, v_int in pre:
            rows.append(dict(seed=s, neuron=int(i), step=t, t_ms=round(t * dt, 4), rel_step=t - S, refractory=refr,
                             active=act, arrival_mv=arr, g_mv=g0, v_before=v0, v_int=v_int, margin_mv=p.v_thr - v_int,
                             kernel_spike=bool(c[i] > 0), b2_spike=bool(t * N + i in b2key),
                             kernel_list=bool(t * N + i in kkey), v_after=float(sim.v[i])))
    return rows, acc, end


# ---- per seed, the calibration seed first ----
calib = a.calib_seed if a.calib_seed in a.seeds else a.seeds[0]
order = [calib] + [s for s in a.seeds if s != calib]
offset, offset_hits, res, trace_rows, failed = None, {}, {}, [], []
for s in order:
    c1, ks, ki, masked_ok, split_ok, wall = kernel_lists(s)
    bi, bs = r[f"spk_i_{s}"].astype(np.int64), r[f"spk_step_{s}"].astype(np.int64)
    kk = keys(ks, ki)
    if offset is None:
        offset_hits = {o: int(np.intersect1d(keys(bs + o, bi), kk, assume_unique=True).size)   # 0, -1, 1, ...: ties go
                       for o in sorted(range(-a.max_offset, a.max_offset + 1), key=lambda o: (abs(o), o))}  # to small |o|
        offset = max(offset_hits, key=offset_hits.get)
        if offset_hits[offset] < len(bs) / 2:   # no alignment at all (e.g. the hum): the calibration means nothing
            notes.append(f"best offset {offset:+d} matched only {offset_hits[offset]} of {len(bs)} spikes: using 0")
            print("note:", notes[-1]); offset = 0
        print(f"step offset calibrated on seed {s}: {offset:+d} "
              f"({offset_hits[offset]} of {len(bs)} Brian2 spikes match; next best offset {(sorted(offset_hits.values(), reverse=True) + [0])[1]})")
    kb = keys(bs + offset, bi)
    only_b, only_k = np.setdiff1d(kb, kk, True), np.setdiff1d(kk, kb, True)
    out = dict(seed=s, spikes_b2=int(ref_counts[s].sum()), spikes_kernel=int(c1.sum()),
               counts_identical=bool(np.array_equal(c1, ref_counts[s])),
               neurons_count_differs=int((c1 != ref_counts[s]).sum()),
               b2_list_matches_counts=bool(np.array_equal(np.bincount(bi, minlength=N), ref_counts[s])),
               kernel_list_matches_counts=bool(np.array_equal(np.bincount(ki, minlength=N), c1) and len(kk) == len(ks)),
               masked_equals_unmasked=masked_ok, split_run_equals_whole=split_ok,
               lists_identical=bool(len(only_b) == 0 and len(only_k) == 0),
               n_match=int(len(kb) - len(only_b)), n_b2_only=int(len(only_b)), n_kernel_only=int(len(only_k)),
               kernel_wall_s=round(wall, 3), first_mismatch=None)
    for k in ("b2_list_matches_counts", "kernel_list_matches_counts", "masked_equals_unmasked", "split_run_equals_whole"):
        if not out[k]:
            failed.append(f"seed {s}: {k}")
    print(f"seed {s}: Brian2 {out['spikes_b2']} / kernel {out['spikes_kernel']} spikes; counts identical "
          f"{out['counts_identical']} ({out['neurons_count_differs']} neurons differ); spike lists identical "
          f"{out['lists_identical']} (match {out['n_match']}, Brian2 only {out['n_b2_only']}, kernel only "
          f"{out['n_kernel_only']}); masked==unmasked {masked_ok}, split==whole {split_ok}; kernel {wall:.2f}s", flush=True)
    if not out["lists_identical"]:
        S = int(min(np.concatenate([only_b, only_k]) // N))
        nb = (only_b[only_b // N == S] % N).tolist(); nk = (only_k[only_k // N == S] % N).tolist()
        # an offset can shift Brian2's spikes outside the kernel's steps 0..n_steps-1: nothing to trace there
        tr = sorted(set(nb) | set(nk))[:a.max_trace] if 0 <= S < n_steps else []
        rows, rerun_ok = [], None
        if tr:
            rows, acc, end = trace(s, S, tr, set(kb.tolist()), set(kk.tolist()))
            rerun_ok = bool(np.array_equal(acc, np.bincount(ki[ks <= end], minlength=N)))
            if not rerun_ok:
                failed.append(f"seed {s}: stepped re-run differs from the recorded list")
        traced = []
        for i in tr:
            ri = [x for x in rows if x["neuron"] == i]
            at = next(x for x in ri if x["rel_step"] == 0)
            before = [abs(x["margin_mv"]) for x in ri if x["rel_step"] <= 0 and np.isfinite(x["margin_mv"])]
            m = at["margin_mv"]
            cls = ("refractory at the mismatch" if not np.isfinite(m) else
                   "kick-driven (random stream or a kick discarded while refractory)" if at["v_before"] > p.v_thr
                   else "near threshold (|margin| <= 0.01 mV)"
                   if abs(m) <= 0.01 else "intermediate (0.01-0.05 mV)" if abs(m) <= 0.05 else "far (> 0.05 mV): semantic")
            consistent = all(x["kernel_spike"] == x["kernel_list"] for x in ri) and all(
                x["kernel_spike"] == (np.isfinite(x["v_int"]) and x["v_int"] > p.v_thr) for x in ri)
            if not consistent:
                failed.append(f"seed {s}: trace of neuron {i} disagrees with the kernel's own spikes")
            near = lambda st, ii: [int(t) - S for t in st[(ii == i) & (np.abs(st - S) <= a.window)]]
            traced.append(dict(neuron=int(i), groups=[k for k, g in groups.items() if i in g],
                               side="brian2 only" if i in nb else "kernel only", margin_mv=m,
                               min_abs_margin_window=min(before) if before else None, v_int=at["v_int"], cls=cls,
                               b2_spikes_rel=near(bs + offset, bi), kernel_spikes_rel=near(ks, ki),
                               trace_consistent=bool(consistent)))
        out["first_mismatch"] = dict(step=S, t_ms=round(S * dt, 4), b2_only=nb, kernel_only=nk,
                                     rerun_consistent=rerun_ok, traced=traced)
        trace_rows += rows
        print(f"  first mismatch at step {S} (t = {S * dt:.1f} ms): Brian2 only {nb}, kernel only {nk}; "
              f"stepped re-run consistent {rerun_ok}")
        for x in traced:
            print(f"  neuron {x['neuron']} {x['groups']} ({x['side']}): margin v_thr - v_int = {x['margin_mv']:+.6f} mV "
                  f"-> {x['cls']}; Brian2 spikes at {x['b2_spikes_rel']}, kernel at {x['kernel_spikes_rel']} (steps from mismatch)")
        if tr:
            tt = pd.DataFrame([x for x in rows if x["neuron"] == tr[0]])
            with pd.option_context("display.width", 200, "display.max_columns", 20):
                print(tt[["rel_step", "step", "refractory", "active", "arrival_mv", "g_mv", "v_before", "v_int",
                          "margin_mv", "kernel_spike", "b2_spike"]].to_string(index=False, float_format=lambda v: f"{v:.6f}"))
        else:
            print("  (mismatch outside the kernel's steps under the calibrated offset: not traced)")
    res[s] = out

# ---- summary and outputs ----
seeds = [res[s] for s in a.seeds]
print("\nsummary:", "; ".join(
    f"seed {x['seed']}: " + ("identical, spike for spike" if x["lists_identical"] else
                             f"first mismatch {x['first_mismatch']['t_ms']} ms, " + ", ".join(
                                 f"n{t['neuron']} {t['margin_mv']:+.2e} mV ({t['cls'].split(' (')[0]})"
                                 for t in x["first_mismatch"]["traced"])) for x in seeds))
if failed:
    print("ASSERT FAILED:", "; ".join(failed))
report = dict(ref=os.path.abspath(a.ref), conn=os.path.abspath(a.conn), dt=dt, ms=ms, drive=drive, gain=gain,
              w_syn_mv=w_syn, kick_mv=p.kick_mv, noise_hz=noise_hz, eps_v=p.eps_v, eps_g=p.eps_g, float64=a.float64,
              chunks_T=sim.T, step_offset=offset, offset_calib_seed=calib, offset_hits=offset_hits, notes=notes,
              asserts_failed=failed, seeds=seeds)
with open(outs["json"][0], "w") as f:
    json.dump(report, f, indent=1, default=float)
pd.DataFrame([{k: v for k, v in x.items() if k != "first_mismatch"} | (
    {"first_step": x["first_mismatch"]["step"], "first_t_ms": x["first_mismatch"]["t_ms"],
     "first_neurons": " ".join(str(t["neuron"]) for t in x["first_mismatch"]["traced"]),
     "first_margin_mv": (x["first_mismatch"]["traced"] or [{}])[0].get("margin_mv"),
     "first_class": (x["first_mismatch"]["traced"] or [{}])[0].get("cls")} if x["first_mismatch"] else {}) for x in seeds]
             ).to_csv(outs["seeds"][0], index=False)
pd.DataFrame(trace_rows, columns=["seed", "neuron", "step", "t_ms", "rel_step", "refractory", "active", "arrival_mv",
                                  "g_mv", "v_before", "v_int", "margin_mv", "kernel_spike", "b2_spike", "kernel_list",
                                  "v_after"]).to_csv(outs["trace"][0], index=False, float_format="%.9g")
for tmp, final in outs.values():
    _edge.finish(tmp, final)
side = _edge.sidecar(base + ".sidecar.json", {"ref": os.path.abspath(a.ref), "conn": os.path.abspath(a.conn),
                                              "float64": a.float64, "eps_v": p.eps_v, "eps_g": p.eps_g,
                                              "NUMBA_CACHE_DIR": os.environ["NUMBA_CACHE_DIR"]})
print("wrote", ", ".join(f for _, f in outs.values()), "and", side)
sys.exit(1 if failed else 0)
