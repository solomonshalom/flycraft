#!/usr/bin/env python3
"""Run an existing experiment script with its output sent elsewhere, optionally with LIF parameter overrides.

Every simulation script does `from common import RES, make_sim, ...`, so setting common.RES before running it
sends all of its output to --res without editing the script (design_plan.md section 2.1).

  python3 experiments/edge/run_redirect.py --res DIR [--sim KEY=VAL ...] SCRIPT [-- ARGS ...]
  e.g.  run_redirect.py --res experiments/results_edge/dt --sim dt=0.1 t_ref=2.0 experiments/social_probe.py -- --seeds 10 --out experiments/results_edge/dt/s.csv

SCRIPT is the last word before `--`. --sim takes any LIFParams field but w_syn (dt, t_ref, delay, eps_v, eps_g,
kick_mv, noise_hz, legacy, ...; gain stays the script's --gain), several per flag or the flag repeated. Overrides are
applied inside LIF.__init__, so they win over whatever the script passes, in every LIF it builds (also the ones
built directly, shuffle_control.py), e.g. noise_hz replaces a script's own noise-free and noisy sims alike; the
effective parameters (with or without --sim) are printed for the first LIF and for every later one that differs.
Refuses a --res, or any path in ARGS, inside experiments/results/; also refuses a SCRIPT that sets its own RES,
and while the script runs any open() for writing inside experiments/results/ raises.
Writes DIR/_redirect_<script>_<stamp>.json (argv, overrides, effective params, files written) and lists the files
written under DIR.
"""
import argparse, ast, builtins, dataclasses, io, os, runpy, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _edge  # puts experiments/ and brain/ on the path

argv = sys.argv[1:]
cut = argv.index("--") if "--" in argv else len(argv)
pre, args = argv[:cut], argv[cut + 1:]
ap = argparse.ArgumentParser(usage="%(prog)s --res DIR [--sim KEY=VAL ...] SCRIPT [-- ARGS ...]")
ap.add_argument("--res", required=True, help="directory that replaces experiments/results for SCRIPT")
ap.add_argument("--sim", nargs="+", action="extend", default=[], metavar="KEY=VAL", help="LIFParams overrides")
if not pre or pre[-1].startswith("-"):
    ap.parse_args(pre); ap.error("SCRIPT missing (it is the last word before --)")
script = os.path.abspath(pre[-1])
if not (script.endswith(".py") and os.path.isfile(script)):
    ap.error(f"SCRIPT (the last word before --) must be an existing .py file: {pre[-1]}")
a = ap.parse_args(pre[:-1])

# ---- refuse anything that could land in experiments/results/ (before any import that touches the disk) ----
res = os.path.abspath(a.res)
if _edge._inside(res, _edge.RESULTS):
    sys.exit(f"run_redirect: refusing --res inside experiments/results/: {a.res}")
for tok in args:
    for part in {tok, tok.partition("=")[2]} - {""}:
        if _edge._inside(part, _edge.RESULTS):
            sys.exit(f"run_redirect: refusing an argument inside experiments/results/: {tok}")
tree = ast.parse(open(script).read())
binds = [n for n in ast.walk(tree) if (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RES" for t in n.targets))
         or (isinstance(n, ast.ImportFrom) and n.module != "common" and any((x.asname or x.name) == "RES" for x in n.names))]
if binds:
    sys.exit(f"run_redirect: {os.path.basename(script)} sets its own RES (line {binds[0].lineno}); redirecting it would not work")
uses_common = any(isinstance(n, ast.ImportFrom) and n.module == "common" and any(x.name == "RES" for x in n.names) for n in ast.walk(tree))
if not uses_common:
    print(f"run_redirect: note: {os.path.basename(script)} does not import RES from common; only ARGS decide where it writes")

# ---- --sim overrides ----
from flybrain import lif
DEF = {f.name: f.default for f in dataclasses.fields(lif.LIFParams)}
over = {}
for kv in a.sim:
    k, eq, v = kv.partition("=")
    if not eq or k not in DEF or k == "w_syn":  # w_syn would silently drop the script's gain and the male density scale
        ap.error(f"--sim {kv}: expected KEY=VAL with KEY one of {', '.join(x for x in DEF if x != 'w_syn')} (gain: the script's --gain)")
    if isinstance(DEF[k], bool):
        if v.lower() not in ("1", "0", "true", "false", "yes", "no"):
            ap.error(f"--sim {kv}: {k} is a boolean")
        over[k] = v.lower() in ("1", "true", "yes")
    else:
        try:
            over[k] = float(v)
        except ValueError:
            ap.error(f"--sim {kv}: {k} needs a number")

# every LIF goes through here: with no --sim the script's own params object is passed on untouched (only recorded)
built = []  # effective params of every distinct LIF built; the first and every changed one are printed
init0 = lif.LIF.__init__
def _init(self, W, params=None, seed=0):
    init0(self, W, dataclasses.replace(params or lif.LIFParams(), **over) if over else params, seed=seed)
    eff = dataclasses.asdict(self.p) | {"ref_steps": self.ref_steps, "delay_steps": self.delay_steps}
    if eff not in built:
        print(f"run_redirect: LIF #{len(built) + 1} with --sim {over}: " + " ".join(f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}"
              for k, v in eff.items()), flush=True)
        built.append(eff)
lif.LIF.__init__ = _init
print(f"run_redirect: --sim overrides {over} (applied in LIF.__init__, win over the script's own values)" if over else
      "run_redirect: no --sim overrides; LIF parameters are the script's own")

# ---- redirect RES, guard open(), run ----
import common
os.makedirs(res, exist_ok=True)
common.RES = res
_open = builtins.open
def _guarded(file, mode="r", *aa, **kw):
    if isinstance(file, (str, bytes, os.PathLike)) and any(c in mode for c in "wax+") and _edge._inside(os.fsdecode(file), _edge.RESULTS):
        raise PermissionError(f"run_redirect: refusing to write into experiments/results/: {os.fsdecode(file)}")
    return _open(file, mode, *aa, **kw)
builtins.open = io.open = _guarded

def rel(p):  # project-relative when inside the project
    return os.path.relpath(p, _edge.ROOT) if _edge._inside(p, _edge.ROOT) else p

def files_under(d):  # path -> mtime; a file that vanishes mid-walk is skipped (this also runs in `finally`)
    out = {}
    for r, _, fs in os.walk(d):
        for f in fs:
            try:
                out[os.path.join(r, f)] = os.stat(os.path.join(r, f)).st_mtime_ns
            except OSError:
                pass
    return out

name = os.path.splitext(os.path.basename(script))[0]
side = os.path.join(res, f"_redirect_{name}_{time.strftime('%Y%m%d_%H%M%S')}.json")
info = {"script": rel(script), "sha256_target": _edge._sha(script), "script_args": args,
        "res": rel(res), "sim": over}
_edge.sidecar(side, info | {"status": "running"})
before, t0, status, argv0 = files_under(res), time.time(), "ok", sys.argv
sys.argv = [script] + args
print(f"run_redirect: RES -> {rel(res)}; running {rel(script)} {' '.join(args)}", flush=True)
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        status = f"exit {e.code}"; raise
except BaseException as e:
    status = f"failed: {type(e).__name__}: {e}"; raise
finally:
    sys.argv = argv0
    after = files_under(res)
    new = sorted(rel(p) for p, m in after.items() if before.get(p) != m and p != side)
    print(f"run_redirect: {status}, {time.time() - t0:.0f}s; files written under {rel(res)}:")
    for p in new:
        print("  ", p)
    _edge.sidecar(side, info | {"status": status, "wall_s": round(time.time() - t0, 1), "lif_params": built, "files": new})
