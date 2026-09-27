#!/usr/bin/env python3
"""Start one fly brain.  Example:  python run_brain.py --name fly1 --port 8765 --plasticity off --state virgin,fed"""
import argparse
import asyncio
import os

from flybrain.server import Brain, serve, STATES

HERE = os.path.dirname(os.path.abspath(__file__))

p = argparse.ArgumentParser()
p.add_argument("--name", default="fly1")
p.add_argument("--dataset", choices=["flywire", "malecns"], default="flywire", help="flywire = female brain (v783); malecns = male brain + nerve cord (v1.0)")
p.add_argument("--host", default="127.0.0.1")
p.add_argument("--port", type=int, default=8765)
p.add_argument("--brain-ms", type=float, default=50.0, help="brain time simulated per observation (the bot observes every --tick ms, default 50)")
p.add_argument("--dt", type=float, default=0.2, help="integration step (ms); exact integrator; 0.1 and 0.5 give qualitatively the same results, rates within about 10 Hz (RESEARCH_NOTES 23)")
p.add_argument("--mask", default="", help="comma list of sensory channels never driven (senses.py group names, e.g. bristle = no touch); a lesion control, RESEARCH_NOTES 23")
p.add_argument("--noise-hz", type=float, default=0.0, help="background Poisson rate on all neurons")
p.add_argument("--gain", type=float, default=1.0, help="multiplier on the per-synapse weight (1 = published calibration)")
p.add_argument("--plasticity", choices=["off", "mb"], default="off", help="off = fixed connectome (innate arm); mb = dopamine-gated KC->MBON learning (learning arm)")
p.add_argument("--us", choices=["wiring", "dan"], default="wiring", help="learning arm: teaching signal = whatever the wiring delivers to the dopamine neurons (wiring) or direct activation of the identified reward/punishment DANs by sugar / pain (dan; optogenetic-style US)")
p.add_argument("--us-hz", type=float, default=50.0, help="activation rate of the US dopamine neurons while the US is present")
p.add_argument("--tau-dan", type=float, default=0.0, help="learning arm: phasic teaching signal (DAN rate minus its running mean over this many seconds; 0 = tonic)")
p.add_argument("--signs", choices=["shiu", "known"], default=None, help="transmitter sign rule: shiu = predicted majority vote (published), known = overridden by known transmitters (default: env FLYBRAIN_SIGNS or shiu)")
p.add_argument("--eln", type=float, default=None, help="output scale of the antennal lobe's excitatory local neurons (1 = published; 0.25 keeps odors distinct; default: env FLYBRAIN_ELN or 1)")
p.add_argument("--unclear-ln", choices=["excitatory", "inhibitory", "silent"], default=None, help="MaleCNS: what its 67 unclear-transmitter antennal-lobe local neurons do (default: env FLYBRAIN_UNCLEAR_LN or excitatory = published)")
p.add_argument("--al", choices=["published", "specific"], default=None, help="shorthand: 'specific' = --signs known --eln 0.25 (an antennal lobe that tells odors apart); 'published' = --signs shiu --eln 1")
p.add_argument("--state", default="", help="comma list of imposed internal states (tonic drive of the fly's own state neurons): " + ", ".join(STATES))
p.add_argument("--state-hz", type=float, default=30.0, help="tonic rate for --state neurons")
p.add_argument("--vision", choices=["lif", "flyvis"], default="lif", help="lif = photoreceptors into the spiking optic lobe (dies in the medulla); flyvis = graded connectome-constrained optic lobe (Lappalainen et al. 2024) driving the same neurons")
p.add_argument("--pop-turn-w", type=float, default=0.0, help="first-version heuristic: weight of population L-R descending asymmetry in turning (0 = identified neurons only)")
p.add_argument("--log-dir", default=os.path.join(HERE, "..", "logs"))
p.add_argument("--seed", type=int, default=0)
p.add_argument("--record-spikes", action="store_true")
a = p.parse_args()

os.environ["FLYBRAIN_DATASET"] = a.dataset
if a.al == "specific":
    a.signs, a.eln = a.signs or "known", 0.25 if a.eln is None else a.eln
elif a.al == "published":
    a.signs, a.eln = "shiu", 1.0
brain = Brain(a.name, a.brain_ms, a.dt, a.noise_hz, a.plasticity, a.pop_turn_w, a.log_dir, a.seed, a.record_spikes,
              state=a.state, state_hz=a.state_hz, gain=a.gain, vision=a.vision, signs=a.signs, eln_scale=a.eln, us=a.us, us_hz=a.us_hz, tau_dan=a.tau_dan, unclear_ln=a.unclear_ln, mask=a.mask)
try:
    asyncio.run(serve(brain, a.host, a.port))
except KeyboardInterrupt:
    pass
finally:
    brain.close()
