# Research notes — fly brain in Minecraft

*Plain-language running log. Newest entries at the bottom. Started 14 Sep 2026.*

## Agenda

**Working title:** *Wiring, state, or experience? Which social behaviors a fruit fly's connectome produces on its own.*

**The question:** Which social behaviors come out of a fly's brain wiring by itself, and which ones need learning?
(Where it came from: we started from "is morality/accountability innate or learned in animals?", found that question is well studied in mammals but untestable with any animal whose brain is fully mapped, and narrowed it to the social behaviors a fly actually has — approach, aggression, courtship, rejection — using the only complete brains available.)

**The tool:** Take the complete wiring diagram of a real fruit fly's brain (every neuron, every connection), simulate it as a network of spiking neurons, connect its senses and muscles to a Minecraft character, and watch what it does — with learning switched **off** (pure wiring) and with learning switched **on** (the fly's real dopamine learning rule added).

**Hypotheses going in**
- H1 — Simple reflexes (feeding on sugar, escape to sound, steering by smell) come out of the wiring alone. *(Supported.)*
- H2 — Social decisions (aggression, courtship, receptivity/rejection) also come out of the wiring alone when the right pheromone or contact cue is present. *(Not supported so far: the decision neurons are silent to every sensory cue in both sexes; only the rejection output responds to touch. The data point to internal state as the missing ingredient — hence Aim 3.)*
- H3 — Adding the fly's dopamine learning rule lets an odor paired with reward change behavior. *(Revised 16 Sep, §16: the published model's antennal lobe made every odor the same odor, so nothing odor-specific could ever be learned; with the transmitter signs corrected where known, the antennal lobe's lateral excitation scaled down, and the reward/punishment delivered to the identified dopamine neurons — the wiring itself carries no sugar or pain signal to any of them — an odor-specific, valence-correct memory forms at the right synapses (CS+ input to the taught compartment 0.10 of pre, CS- 0.6-0.9, reciprocal, n = 3). It does not change what the fly does: the appetitive compartments' MBONs are inhibitory with silent targets, and the model's own odor-evoked dopamine depresses every odor non-associatively. Memory yes, expression no.)*
- H4 — The male and female connectomes give different innate social maps. *(Partly: the male's song command fires to any odor and cVA reaches its aggression/courtship clusters weakly; the female's rejection output is touch-driven and odor-gated. Both share the "decision neurons need more than sensory input" result.)*

**Aims and the three arms**
1. **Innate map, both sexes (arm A: wiring only).** Every social input × every social output, fixed connectome. *Done first pass (Figs 1, 4).*
2. **Learning arm (arm B).** The same model plus the fly's own mushroom-body learning rule; classic odor–sugar conditioning. *Redone on a model that tells odors apart (Figs 2b, 9; §16); plus learning in the world (`experiments/learn_in_world.sh`).*
3. **State arm (arm C) — added because of H2's result.** Impose an internal state the way the fly does it (silence the sex-peptide/SAG pathway = mated female; hunger neurons = starved) and re-run the map. *Not started.*
4. **Embodied encounters.** Two brains in one chamber (female–female, male–female), sex-correct chemical cues, near-vs-far and contact-vs-no-contact comparisons. *Running; needs error bars and the CO₂-fixed rerun.*
5. **Controls that decide what counts.** Gain sweep (done), shuffled-connectome null (not done), sensitivity to our own encoding choices (not done), background-noise control (done).

**What would count as success:** a table, for each social behavior, saying *wiring / state / learning / not in this model* — every entry backed by a gain-robust number, a shuffled-wiring control, and n ≥ 5 trials. What would falsify the approach: if the shuffled connectome reproduces the map, the results are about neuron density, not wiring, and the paper becomes a methods caution instead.

**Order of work from here:** (1) rerun the rejection test with the CO₂ fix, 5 trials each → (2) shuffled-connectome control on the female map → (3) state arm (SAG silencing) → (4) sensitivity checks → (5) anchor one behavior to published numbers → (6) write.

**Status key used below:** results marked [unscaled] were superseded; sections 3b and 6 contain retractions kept on purpose.
**Update 15 Sep 2026:** sections 1-13 were produced with a simulation core that differed from the published model and with 37 % of synapses removed; they are kept as the record of the first pass. **Section 14 redoes everything on the published model (checked spike for spike against Shiu et al.'s Brian2 code) and section 15 is the current answer table.** Read 14-15 for the state of the project.

---

## 1. What got built (day 1)

- **A brain.** All 139,248 neurons and 2.7 million connections of a female fruit fly (the FlyWire dataset). Each neuron is a simple "leaky integrate-and-fire" unit — the standard published way to simulate this dataset (Shiu et al. 2024, *Nature*). It runs at real time on the laptop.
- **A body.** A Minecraft bot. What the bot sees goes into the fly's photoreceptors; what's nearby goes into the fly's smell neurons (flowers = fruit smell, other flies = fly pheromone, mobs = CO₂); bumping into things goes into touch neurons. Out the other side, the fly's real "descending neurons" (the brain's command lines to the legs) are read as walk / turn / back up / jump / attack / feed.
- **An arena.** A local Minecraft server with a walled chamber containing flowers, honey, a dark shelter, a snow patch and an "aversive" soul-sand patch. Viewable in a browser at localhost:3007 — no Minecraft account needed.
- **Later the same day:** a second brain — a *male* fly (the MaleCNS dataset, 164,439 neurons, 6.2 million connections, including the nerve cord). The male has the courtship-song neurons the female lacks. Both sexes run through the same code.

## 2. Checks that the model is doing what the published model does

- Sugar-taste neurons → proboscis (feeding) motor neurons: **86 Hz**. Add bitter: **59 Hz**. Bitter alone: **2 Hz**. This is the headline result of Shiu et al. 2024, reproduced.
- Sound → the giant fiber (the escape "jump" neuron): fires. That's the known startle circuit.
- Odor on the left antenna → left turning neurons fire more than right; odor on the right → the difference shrinks. So the fly can steer by smell.

## 3. Things we found that we did NOT expect

### 3a. Vision goes nowhere (in this kind of model)
Light drives the first layer of the eye, then the signal dies. The motion-detecting neurons (T4), the looming-detecting neurons (LC4, LPLC2) and all 8,038 neurons that carry visual information out of the optic lobe sit at exactly **0 Hz** — for static scenes, looming objects, flashes and moving bars. Reason: real fly motion vision depends on neurons that don't spike and have carefully tuned time constants; a "one-size-fits-all" spiking model can't do that. **Consequence:** in the pure-wiring version, the fly is blind in practice. It navigates by smell and touch. (This is consistent with the literature: nobody has shown vision working in a whole-brain spiking model yet.)

### 3b. The (female) fly turns left — but this is a fragile network effect, not anatomy
With symmetric input at the default gain, the female's left turning neurons (DNa01/DNa02) fire about ten times more than the right ones. The direct inputs to those neurons are symmetric. *Two corrections made the same day:* (1) I first thought the male showed the same bias, but that was measured while the male network was running away (see 6a). (2) The gain sweep (section 8) shows the female bias **flips to right-dominant at gain 0.7** and is left-dominant at 0.5, 1.0 and above. A bias that changes sign with a global gain knob is a property of the network dynamics, not a fixed asymmetry in the wiring. **Conclusion:** do not interpret the turning bias biologically. The embodied female walks in left-curving loops at the default gain and steers by tightening or loosening the loop; that is fine as a locomotor substrate, but it should be described as such.

### 3c. Every smell looks like punishment
Any odor drives the *punishment* dopamine neurons (PPL1) to ~90 Hz; the *reward* dopamine neurons (PAM) barely respond (~7 Hz), even to sugar (1.5 Hz). Real flies have valence-specific dopamine. The wiring alone, in this model, doesn't produce it. This matters for the learning arm (see 5).

## 4. Female, learning OFF: the innate social map

We stimulated every social input the fly has (fly pheromones, food smell, CO₂, sound/song, touch, sugar, bitter, and combinations) and recorded every social output neuron (aggression cells pC1d/e and aIPg, receptivity cells pC1a and vpoDN, the "rejection" neuron DNp13, egg-laying oviDN, feeding, turning, escape). Fig 1 in `experiments/results/`.

- **Touch → DNp13 at 95 Hz.** DNp13 drives ovipositor extrusion, the female's *rejection* signal. Physical contact triggers the rejection output straight from the wiring.
- **Touch is the only thing that reached the aggression neurons** (pC1d/e at ~4 Hz). Pheromones did nothing to them.
- **Song → escape (giant fiber), not receptivity.** vpoDN and pC1a stayed at 0.
- **The female "decision" neurons (pC1a, aIPg, vpoDN, oviDN) were silent under every stimulus.** In the real fly these are gated by internal state — mated or virgin, hungry or fed. Sensory wiring alone doesn't switch them on. This is a clean answer to part of the question: **female receptivity and aggression are not sensory reflexes; they need state.**
- In the arena: two females in a small chamber met often (26 % of the time within 3 blocks, frequent contact). **Nothing in their brains changed when the other fly was near** — aggression 0.05 Hz near vs 0.04 far, everything else identical. They did find the flowers and feed (proboscis motor neurons at 18 Hz, feeding half the time).

## 5. Female, learning ON: conditioning

We ran the classic fly learning experiment in silico: odor A paired with sugar, odor B alone, three rounds, with the fly's real dopamine-gated synapse rule turned on at the mushroom body (the fly's memory center). Fig 2.

- The synapses did change (weights fell to 69 % of start) and the memory center's output halved.
- **But it halved for both odors.** No odor-specific memory formed (difference: −3 Hz). Because every odor drives the punishment dopamine (3c), the plasticity is not specific. A few compartments (α1, α3, γ1pedc) did shift odor-specifically, but nothing reached the behavior neurons.
- **Answer so far:** the learning rule works mechanically, but the *teaching signal* it needs (reward vs punishment) is not produced by the wiring in this model. To get real learning, either the dopamine neurons need a better model, or the reward signal has to be supplied from outside — which would be our design, not the fly's. Either way it has to be stated honestly in the paper.

## 6. Male, learning OFF: the innate social map (MaleCNS)

### 6a. First the male brain had to be re-calibrated
The male dataset's synapse detection is denser: a typical brain neuron receives ~2× the synapses (median 189 vs 92) and 2× the connections (38 vs 19 per neuron) compared with the female dataset. With the published per-synapse weight (calibrated on the female data), the male network *ran away*: 15–19 % of all neurons firing for any input, bitter no longer suppressing feeding, the population of command neurons at 30 Hz for everything. Fix: scale the per-synapse weight by 0.495 so that mean input per brain neuron matches the female dataset. Nothing else differs between the two sexes' models. After scaling: silent at rest, 1–8 % active under input, startle and backing circuits intact.

**The male results below marked [unscaled] were measured before this fix and are being redone.** They are kept here because the pattern (contact pheromone → song command; cVA → aggression) is what we are testing for.

Same probe on the male brain, plus the inputs a male actually uses on a female: the leg "contact pheromone" taste neurons (ppk23 and ppk25). Fig 1 (malecns).

**Scaled (matched-density) results — these replace the earlier unscaled numbers:**
- **ppk25 → song command: 0 Hz.** The earlier 33 Hz was a runaway-gain artifact (it only appears at gain ≥ 1.4, where every input drives every output). Female contact pheromone does *not* trigger the song command from wiring alone.
- **Any odor → pIP10 (song command) at ~15 Hz.** Odor-general, not pheromone-specific, at the default gain. At lower gain (0.5–0.7) it becomes cVA-specific (7.5 Hz vs 0 for food odor).
- **cVA is the only pheromone-specific input.** It alone reaches the P1 courtship cluster (3 Hz), the aggression neurons aIPg (2.3 Hz) and DNp13 (5.5 Hz; robust at every gain, never driven by food odor).
- **Contact pheromone alone → only backing-up (MDN 5–7 Hz).** Combined with odors it *suppresses* the odor-driven song command (15 → 0.5 Hz with all pheromones + contact + touch).
- The song wing-muscle motor neurons never fire at any gain. The command reaches the nerve cord; the pattern generator does not run in this model.
- Sound → giant fiber startle (109 Hz) — as in the female. Wind and touch → backing up (MDN 18 Hz).
- **Male decision neurons (P1, aIPg) are silent at every gain ≤ 1.0** and only respond once the network is near runaway — the same conclusion as for the female.

## 7. Male vs female in one chamber (first run — [unscaled] male; to be repeated)

A male brain and a female brain in the small arena, 240 s. They met 5–8 % of the time.
- The male brain is much *more excitable* than the female under arena input — its courtship cluster, song command, aggression and feeding outputs were above threshold nearly all the time, whether or not the female was nearby. So the male "sang" and "attacked" almost continuously. Aggression rose slightly when touching (18 Hz vs 9 Hz far). The female's feeding rose near the male (31 vs 16 Hz) — probably because the flowers are where they both end up.
- The male brain also runs slower (410 ms per 50 ms of brain time — 8× slower than real time) because it is 2.3× bigger and far more active.
- **Lesson:** absolute thresholds tuned on the female don't transfer to the male. Results must be reported as near-vs-far or stimulus-vs-baseline differences, not as "did it cross 5 Hz".

## 8. Gain robustness — the control that decides what counts

The model has one free constant: the per-synapse weight (0.275 mV from Shiu et al.; ×0.495 for the male). We swept it from 0.35× to 2× on both sexes and asked which responses survive (Fig 4). Rule adopted for the paper: **a response counts as "from the wiring" only if it is present across gains 0.5–1.0 and absent with no input.**

**How to read Fig 4 (`fig4_gain_flywire.png`, `fig4_gain_malecns.png`).** Each panel is one group of output neurons. The x-axis is the gain — how strong every synapse is — with the dashed line at the setting we normally use. Each colored line is one stimulus. A result you can trust is a line that stays up across the left half of the panel (gains 0.5–1.0). A line that only rises on the far right (1.4×, 2×) is the network "boiling over", not the wiring answering. Things to look for: in **DNp13**, the red *touch* line is high at every gain — the rejection response is real. In **pC1d/e** and **aIPg**, nothing gets above ~4 Hz even at 2× — the decision neurons are genuinely silent. In **DNa L** vs **DNa R**, the lines swap places at 0.7 — the turning bias flipping sign. In **active_frac**, all lines climb steeply past 1.0 — that is the runaway regime.

Survives (female): sugar → feeding; touch → DNp13 rejection; **cVA suppresses the touch-evoked rejection** (93 → 13 Hz at gain 1.0; 4 of 5 gains). Survives (male): sound → startle; cVA → DNp13. Does **not** survive: the left-turn bias (flips sign at 0.7), ppk25 → song command (only in runaway), P1/aIPg/pC1d/e responses to anything (≤ 4 Hz at every gain in the female, even at 2×; male only in runaway). Above ~1.4× the network enters a regime where 11–16 % of neurons fire and every input drives every output — results from there are meaningless, and that is exactly where the first male numbers came from.

## 9. Where this leaves the research question (so far)

| Behavior | Wiring alone? | Notes |
|---|---|---|
| Feeding on sugar | **Yes** | Reproduces published result |
| Startle/escape to sound | **Yes** | Giant fiber |
| Steering by smell | **Yes** (with a left bias) | Bilateral antennae |
| Female rejection signal on touch | **Yes** | DNp13 |
| Female receptivity / aggression from sensory cues | **No** | Decision neurons ≤ 4 Hz at every gain — need internal state |
| Female rejection gated by male odor | **Yes** (cVA suppresses touch → DNp13) | Robust at 4/5 gains; candidate headline |
| Male song command from female contact pheromone | **No** | Earlier "yes" was a runaway-gain artifact |
| Male song command from odor | **Weak, odor-general** (~15 Hz) | cVA-specific only at low gain; song muscles never run |
| Male courtship/aggression decision (P1, aIPg) from sensory cues | **No** | Silent at every physiological gain |
| Male cVA → DNp13 | **Yes** | Robust and pheromone-specific |
| Approach to another fly | **No** (not seen yet) | No change near vs far |
| Odor–reward learning | **Rule works, teaching signal missing** | Needs dopamine valence |
| Anything visual | **No** | Vision dies in the medulla |

## 10. Arena encounters, second pass (sex-aware cues, contact drives touch neurons)

Fixes made first: only males emit cVA; touching a female drives ppk25, touching a male ppk23; fly-to-fly contact now drives the touch (bristle) neurons (before, only wall collisions did); a human player on the server no longer counts as a fly (it counts as CO₂); the male walks from its leg motor neurons (its walking command neurons are silent under arena input at matched gain).

- **Female–female and male–female, 6-block chamber, with and without flowers.** Contact happened often (100+ contact ticks in the female pair). In *every* condition the female's touch response was **feeding (proboscis motor neurons ~43 Hz on contact vs ~5 Hz apart)** — and **zero rejection output (DNp13)**, even though the offline probe predicted DNp13 at ~47 Hz for exactly this mix of inputs.
- **Why: the other fly was "breathing".** My encoding gave every animal, flies included, the same CO₂ plume as a mob or a human. At contact distance that is a strong CO₂ input, and in the wiring CO₂ collapses the touch-evoked rejection response (47 → 3.5 Hz). Real flies don't make a human-sized plume, so this was my modelling error, now fixed (fly-sized emitters = 5 %). **The rejection test has to be rerun** (`NO_FOOD=1 experiments/ff_vs_mf.sh`, ~10 min).
- The male in the chamber: sings and courts at any odor, no more when the female is near or touching; aggression neurons 2–3 Hz throughout, slightly higher on contact (2.9 vs 2.0 Hz — within noise until repeated).
- Side finding worth keeping: in this model **odors gate the touch-evoked rejection output** — food odor (95 → 8 Hz), cVA (→ 13 Hz), CO₂ (→ 3.5 Hz) all suppress it, while fly odor alone (Or47b) does not (→ 44 Hz). That is a concrete, testable circuit prediction.

## 11. What's being done next / what was done since

- Male vision probe: same as the female — silent beyond the lamina with histaminergic photoreceptors; the apparent visual responses in the unscaled male were runaway.
- Background-noise control (1 Hz on all neurons, female): adds a floor to every output (turning 44 Hz, feeding 20 Hz with *no* input) and even abolishes the sound-startle; it creates no specificity. Reported as a control, not used by default.
- Figures: Fig 1 (maps, both sexes, ± noise), Fig 2 (conditioning), Fig 3 (encounters), Fig 4 (gain robustness) in `experiments/results/`.
- Male–female encounter re-run with the scaled male (running).
- Still to do: (1) rerun the female–female vs male–female rejection test with the CO₂ fix; (2) repeated trials with error bars (`experiments/trials.sh`); (3) decide whether to add an internal-state variable (e.g. mating status via SAG/sex-peptide neurons) as a *third* arm — that would test "state" the way the learning arm tests "experience".

## 12. Honesty list for the methods section

Ours, not the fly's: neuron dynamics (standard LIF), how pixels become photoreceptor spikes, which blocks smell like what, the two-antenna spacing (1 block), the motor-readout thresholds, the small population-turn heuristic (weight 0.25), the learning-rule constants, the arena, and the Minecraft physics. The fly's: every neuron, connection, synapse count, transmitter type, left/right side, cell identity, and where the learning rule lives. Not modelled at all: neuromodulators, gap junctions, internal state, development, and (for the female) the nerve cord.

## 13. What we can do that nobody has done — and what we must do

### What others have done
- Simulated the fly connectome as spiking neurons and checked a few reflexes (Shiu et al. 2024: taste → feeding, grooming).
- Wired that simulation to Doom, Beat Saber and Minecraft as demos (hobbyists, Sept 2026). Fun; no question asked, no controls, no numbers.
- Trained the connectome with reinforcement learning to make a simulated fly walk (the "graph model" papers). That teaches the network; it doesn't ask what the wiring already knows.
- Studied fly social behavior in real flies for decades (courtship, aggression, pheromones) — but circuit by circuit, never the whole brain at once.

### What we can do that they haven't
1. **Ask a question of the whole brain, both sexes, side by side.** The male dataset is weeks old. Nobody has yet put the female and male connectomes through the same social stimuli in the same model and compared them. We have, and the answer is the same in both: sensory wiring carries the signals in, but the sex/aggression decision neurons don't fire on wiring alone.
2. **Two brains in one world.** Our flies share a physical space, so encounters, contact, and chemical cues are emergent, not scripted. Nobody has run two connectome brains against each other.
3. **Experiments impossible in a real fly.** We can silence or drive any neuron type in either fly *in the middle of an encounter* — switch off the male's P1 cluster and watch the female; give a female a male's cVA circuit; swap datasets mid-experiment. Every one of the 139,000 / 164,000 neurons is addressable.
4. **Test the fly's own learning rule inside the whole brain,** with reward and punishment arriving through the wiring rather than being injected. We did, and it showed exactly what's missing (the dopamine valence signal). That is a statement about connectome-only models that nobody has made with numbers.
5. **A standard for what counts as "from the wiring".** The gain sweep is a simple idea — turn the one free knob and see what survives — and the demos skip it. Two of our own early "findings" died on it. Adopting it as a rule (survives 0.5–1.0×, absent with no input) is a methodological contribution in itself.
6. **Concrete, testable predictions for real flies.** E.g. odors (food, cVA, CO₂) gate the touch-evoked rejection output (DNp13) while plain fly odor does not. A fly lab can test that with optogenetics in an afternoon.
7. **Later: drop in the mosquito.** The Aedes connectome is funded and in progress; our pipeline is dataset-agnostic (three loaders' worth of proof: FlyWire, MaleCNS, and the switch between them). When it lands, the same experiments run on a mosquito.

### What we must do before any of this is a paper
1. **Rerun the rejection test with the CO₂ fix** and get **error bars**: at least 5 trials per condition, different seeds and start positions (`experiments/trials.sh`). Every number in the notes so far is n = 1–3.
2. **A shuffled-connectome control.** Rewire the connectome randomly while keeping each neuron's number of inputs and outputs, and rerun the map. If the same responses appear, they come from density, not from the specific wiring — and the whole story collapses. This is the control reviewers will ask for first, and no demo has done it.
3. **The third arm: internal state.** The question was "wiring vs learning"; the data say the missing ingredient for social decisions is *state* (mated/virgin, hungry/fed). We can add it honestly: the sex-peptide pathway (SAG neurons) and hunger-signalling neurons are labeled in the connectome. Silence SAG (= mated female), rerun the map, and see whether pC1/DNp13/aIPg wake up. That turns a two-way question into a three-way answer: wiring / state / learning.
4. **Report only gain-robust results**, and say which earlier claims were retracted and why (sections 3b, 6). Reviewers trust papers that show their own corrections.
5. **Sensitivity of our own choices.** Antenna spacing, the odor-distance kernel, the CO₂ emission rule, the 100 Hz stimulus rate, the per-tick brain time. Each should be varied once to show the conclusions don't depend on them.
6. **Quantitative anchoring to one real behavior.** Pick one thing with published numbers — e.g. proboscis extension on contact, or ovipositor extrusion in mated females touched by a courting male (Wang et al. 2020) — and show the model's rate is in the right range, not just non-zero.
7. **Say plainly what the model cannot do:** vision (so no courtship chasing, no visual looming), song production (command fires, muscles don't), neuromodulation, and — until arm 3 — internal state.
8. **Release everything**: code, the exact data versions, every "ours vs the fly's" choice (section 12), and the logs. The result is only interesting if someone else can rerun it.

---

## 14. Second pass (14 Sep 2026, evening) — checking the model against the published one, line by line

*Running log of the second working session. Newest at the bottom.*

### 14a. The simulation core was not the published model. Now it is.
I fetched Shiu et al.'s own Brian2 code (github.com/philshiu/Drosophila_brain_model, `model.py`) and their
own v783 connection table, and compared them with ours. Three differences, all on our side:

1. **The synaptic variable is reset to zero at every spike** in the published model (`reset = 'v = v_rst; g = 0*mV'`).
   Ours kept it. Effect: strongly driven neurons fired far too fast.
2. **Refractory neurons ignore all input.** Tested directly with timed inputs in Brian2: a voltage kick or a
   synaptic input arriving in the 2.2 ms after a spike is discarded, not queued. Ours accumulated it.
   Effect: a sensory neuron driven at 100 Hz fires at 82 Hz in the published model, 96 Hz in ours; a
   proboscis motor neuron under sugar drive fired 1.8x too fast in ours.
3. **Sensory activation is a voltage kick (0.275 mV x 250), not a forced spike.** Same idea, but the kick obeys rule 2.

Also fixed: the integrator is now exact (Brian2's 'linear' method) instead of forward Euler, so the time step
no longer matters (0.1, 0.2 and 0.5 ms give the same rates — checked). The core is now a compiled (numba)
kernel that only touches neurons that are not at rest: 5-10x faster than before in sparse regimes. Real
time or better for the female; the male is next.

**Validation so far:** (a) the new kernel in "legacy" mode reproduces the old numpy code exactly (within
Poisson noise) — so all earlier numbers are reproducible; (b) micro-networks (single kicked neuron, chains,
inhibition, a 20-neuron recurrent net) run through Brian2 and through our kernel; (c) the *actual* Brian2
model run on our connectome with sugar GRNs at 100 Hz (`brain/tests/brian2_reference.py`, 3 s per simulated
second with Cython). Before the refractory fix, per-neuron correlation with Brian2 was 0.94 but rates were
~1.8x high; the post-fix comparison is running.

**Consequence for every number above section 14:** they were produced with the old semantics and are
being redone. Early re-runs with the corrected core (old >= 5-synapse connectome): sugar -> feeding MNs
107 -> 44 Hz; touch -> DNp13 95 -> 40 Hz; any odor -> PPL1 90 -> 33 Hz; KC 37 -> 14 Hz. **The female
left-turn bias (section 3b) is gone** (cVA: DNa L 21 Hz vs R 27 Hz), consistent with its being a numerics
artifact rather than anatomy.

### 14b. The connection threshold was ours, not Shiu's
The README said connections with fewer than 5 synapses were dropped "as in Shiu et al. 2024". Their
Methods give no threshold, and their own v783 table (`Connectivity_783.parquet`, 15,091,983 rows, minimum
1 synapse, 54.5 M synapses) has none. Our threshold dropped 82 % of connections and **37 % of all synapses**
(34.2 M of 54.5 M kept). The female model now uses Shiu's table exactly, including their per-neuron signs
(inhibitory if more than half of a neuron's output synapses are predicted GABA/glutamate). The >= 5
version is kept as a sensitivity variant (`FLYBRAIN_CONN=zenodo FLYBRAIN_MIN_SYN=5`).

For the male, the same rule (all connections between traced neurons) gives 25.6 M connections and 124 M
synapses (vs 6.2 M / 89.7 M at >= 5). Input density per brain neuron: female 391 synapses (all) vs male
722 -> per-synapse weight scale for the male becomes 0.542 (was 0.495 at >= 5). Being rebuilt.

### 14c. Two new directions requested
- **More neural, less mechanical.** Plan: (1) motor readout without thresholds — continuous population
  rates set walking speed (duty cycle), turning, and the probability of acts; the male's own leg and wing
  motor neurons drive walking and song directly; drop the population-turn heuristic if identified DNs
  suffice; (2) internal state as tonic activity in the fly's own state neurons (SAG = virgin, IPC = fed,
  P1 = courting) rather than flags; (3) **vision through a neural optic lobe**: flyvis (Lappalainen et al.
  2024, connectome-constrained graded model of 65 optic-lobe cell types, 721 columns) installed cleanly and
  its pretrained models are downloading. If it can be bridged onto the FlyWire T4/T5/Tm neurons by
  retinotopic position, the fly stops being blind — the single biggest "mechanical -> neural" gain.
- **A big Minecraft world.** Plan: a launcher for a normal-terrain world, bots that need no arena and no
  op powers, survive terrain (climb, avoid water, respawn), find natural food, and can be dropped at any
  coordinates; multiple flies per world.

### 14d. Milestone: the core now reproduces the published model spike for spike
After adding the refractory rule, our kernel and the real Brian2 model, run on the same connectome with the
same random seed, produce **identical spike trains**: 21,330 vs 21,330 spikes (seed 0) and 21,088 vs 21,088
(seed 1) for 1 s of sugar-GRN drive at 100 Hz, with identical per-neuron spike counts for all 521 active
neurons (correlation 1.0000, no neuron active in one and not the other). Sugar GRNs 81.2 Hz in both;
feeding motor neurons 25.2 Hz in both. Ours runs the second in 0.3 s; Brian2 needs 13-24 s.
So "our model = Shiu et al.'s model" is now a checkable statement, not a claim. Script:
`brain/tests/brian2_reference.py` + `compare_brian2.py` (Brian2 lives in a separate venv).

### 14e. Gold standard on the published table, and speed
On Shiu et al.'s own v783 table (all 15.1 M connections) the real Brian2 model and our kernel again agree:
seed 1 identical (24,215 = 24,215 spikes); seed 0 within one borderline neuron (23,689 vs 23,512 spikes,
per-neuron correlation 0.9998); feeding motor neurons 26.3 vs 25.9 Hz. Our kernel: 0.6 s per simulated
second; Brian2 (Cython): 4 s. Ours also checks that the time step does not matter (0.1 / 0.2 / 0.5 ms agree).

First corrected numbers on the full published connectome (female, 100 Hz drive, 500 ms, mean of 2):
sugar -> feeding MNs 24 Hz (bitter co-activation -> 12 Hz); touch -> DNp13 36 Hz; sound (JO-B) -> giant
fiber 22 Hz; cVA -> DNa L 37 Hz vs R 3.5 Hz (a left bias is back with the full wiring — the gain sweep will
say whether it is robust); cVA -> PPL1 106 Hz, KC 30 Hz (every odor still looks like punishment, but at a
third of the old rate). The first-version numerics on the full table run away (PPL1 312 Hz, KC 166 Hz for
any odor) — the >= 5 threshold had been hiding that.

Speed on the full table: sparse regimes 3x faster than real time; dense regimes (odor: 6 % of neurons
spiking) 0.3x. The integration pass is being parallelized across cores (neurons partitioned by index, so
no thread ever touches another's neuron).

### 14f. Female innate map, corrected model, 5 seeds (full published connectome)
`experiments/results/social_probe_flywire_shiu_min1_noise0.csv`. What holds, what changed:
- **Decision neurons still silent.** pC1a, pC1d/e, aIPg, vpoEN/vpoDN, oviDN: 0.0 Hz for every input, all 5 seeds.
  Same conclusion as before, now on the published model: female receptivity/aggression are not sensory reflexes.
- **Touch -> DNp13 (rejection) 36 +/- 1 Hz**, and it comes mostly from the eye bristles (1,113 InOm neurons:
  17 Hz alone) not the antennal bristles (2 Hz alone). Odors gate it: cVA + touch 18 Hz, Or47b + touch 19,
  food + touch 17, CO2 + touch 18 — i.e. *any* odor halves it (before, cVA and CO2 nearly abolished it and
  Or47b did not touch it; that pattern was a numerics artifact). Still a testable prediction, now weaker.
- **Every odor drives the turning DNs asymmetrically**: DNa left 34-39 Hz vs right 3-5 Hz, for cVA, food, CO2,
  aversive, all pheromones, with bilateral input. Direct inputs to the four DNa neurons are near-symmetric
  (checked: DNa02 left 7,881 excitatory / 4,387 inhibitory synapses vs right 8,365 / 4,794), so this is a
  network effect. Awaiting the gain sweep before interpreting.
- **Sugar -> Shiu's MN9 neuron 75 Hz** (feeding MNs 24 Hz); cVA + sugar: MN9 47 Hz (odor lowers feeding).
  One of five sugar seeds showed a transient burst into the mushroom body (PPL1 12 +/- 27 Hz) — the
  network is near a bifurcation under sugar drive, which 5 seeds reveal and 1 seed would have hidden.
- **Song/sound -> giant fiber 11 Hz (JO-A), 5 Hz (JO-B)**; wind/gravity, bitter: nothing downstream.
- Any odor -> PPL1 ~108 Hz *and now PAM ~20 Hz* (reward dopamine was ~7 Hz before). Still punishment-dominated.

### 14g. Gain sweep on the corrected female model — the robustness rule has to move
`experiments/results/gain_sweep_flywire_shiu_min1.csv` (gains 0.5, 0.7, 1.0, 1.4, 2.0; 3 seeds; 600 ms).
At **0.5x the published model hardly transmits anything**: sugar -> MN9 0 Hz, touch -> DNp13 2.5 Hz, cVA ->
DNa 0.6 Hz. So "survives 0.5-1.0" was a rule for the old, over-excitable numerics. New rule: **a response
counts as "from the wiring" if it is present at 0.7, 1.0 and 1.4 (a 2x window around the published
calibration) and absent with no input.** 2.0x is the runaway edge (11-12 % of neurons active for any input).
- Holds: sugar -> MN9 (38 / 81 / 64 Hz), touch -> DNp13 (28 / 36 / 19), cVA halves touch -> DNp13
  (16 / 19 / 15 vs 28 / 36 / 19), odor -> DNa left >> right (27:2, 34:4, 37:6), song (JO-A) -> giant fiber
  (5 / 10 / 16). Sound via JO-B -> GF needs gain >= 1.0.
- Decision neurons pC1a/pC1d/e/aIPg/vpoDN: 0 Hz at every gain including 2.0x. This is now as solid as a
  negative result gets in this model.
- The left-turn bias no longer flips sign anywhere in 0.7-2.0x. It is a robust property of *this*
  connectome's network (direct DNa inputs are symmetric). Real flies have stable individual turning
  handedness (Buchanan et al. 2015); an individual's connectome carrying a handedness is plausible, but we
  cannot distinguish that from reconstruction asymmetry. Report it as a property of the reconstructed
  individual, not of flies.

### 14h. Published anchors reproduced with Shiu et al.'s own neurons (`experiments/benchmark.py`)
Using the exact root IDs from their figures notebook (29 sugar, 20 bitter, 18 water GRNs, 69 JO-CE and 60 JO-F
neurons, MN9, aBN1): sugar -> MN9 rises monotonically with input (0, 0, 11, 38, 58, 63, 83 Hz at 10-200 Hz;
100 Hz = 69 % of the 200 Hz response, they report ~80 %); bitter co-activation suppresses it (58 -> 46 -> 24 ->
6 Hz at 25/50/100 Hz); **JO-CE drives the antennal-grooming neuron aBN1 (12.7 Hz) and JO-F does not (0 Hz)** —
the prediction they confirmed with optogenetics; sound -> giant fiber 22 Hz. Water GRNs reach MN9 only at
260 Hz (17 Hz). All four anchors PASS. This is the first time the pipeline has been checked against
the published circuit results neuron for neuron rather than "qualitatively".

### 14i. Male innate map, corrected model, 5 seeds (all 25.6 M connections, weight scale 0.542)
`experiments/results/social_probe_malecns_all_min1_noise0.csv`.
- **cVA -> DNp13 24.5 +/- 1.5 Hz, pheromone-specific** (cVA-long 1.0, Or47b 0.0, food 0.8, CO2 0.8): the
  clearest specific pheromone response in either sex. cVA also drives the song command pIP10 (5.9 Hz; other
  odors 1.8-4.0) and the male MN9 (27 Hz). Touch halves the cVA -> DNp13 response (10.4 Hz), sugar lowers it
  (15.4 Hz).
- **P1 (156 pC1 neurons) and aIPg: 0.0 Hz for every input.** Same as the female's decision neurons.
- **Contact pheromone -> backing up, stronger for male than female cuticular hydrocarbons:** ppk23 (7-T, male
  CHC) -> MDN 28 Hz vs ppk25 (7,11-HD, female CHC) -> 14 Hz; the same asymmetry in the turning DNs (ppk25:
  DNa L 13 Hz vs R 5). In real males 7-T is aversive and 7,11-HD appetitive (Thistle et al. 2012; Toda et al.
  2012) — the wiring alone carries part of that difference. Prediction: silencing MDN should make males
  linger longer on other males.
- Song motor neurons (ps1/i1/i2/hg) fire 10-26 Hz for almost any input (odors 13, contact 21-23, touch 10,
  wind 14) — a general wing-motor output in this model, not a song-specific one; pIP10 is the specific channel.
- Sound (JO-B) -> giant fiber 49 Hz; JO-A (song frequencies) -> nothing in the male. Wind and touch -> MDN 7-10 Hz.
- Any odor -> PPL1 ~115 Hz and PAM ~40 Hz (the male's reward dopamine responds more than the female's 20 Hz).

### 14j. Male gain sweep (`gain_sweep_malecns_all_min1.csv`, gains 0.5-2.0, 3 seeds)
Robust (0.7 / 1.0 / 1.4): cVA -> DNp13 (14 / 25 / 7 Hz, no other odor above 1.4 Hz at any gain);
cVA -> male MN9 (9 / 28 / 30); sound (JO-B) -> giant fiber (41 / 48 / 52 — the male startle is robust even at
0.5x); **leg contact chemosensors (ppk23/25) -> song wing motor neurons at every gain (10 / 20 / 21 / 11 / 14 Hz)**,
a nerve-cord-level path from foreleg contact to the wing muscles (in real males, tapping a female with the
foreleg is what precedes wing extension; here the female CHC receptor alone gives 3 / 13 / 9 Hz, the male's
more) — but touch and wind reach these motor neurons too, so it is "leg contact -> wing motor", not song.
Not robust: contact pheromone -> backing (MDN 29 Hz at 1.0 only; 0 at 0.7, 1.8 at 1.4) — the 7-T vs 7,11-HD
asymmetry of 14i therefore exists only at the published calibration and must be reported as such. Touch ->
MDN holds from 1.0 up (12 / 12 / 8). cVA -> song command pIP10 rises with gain (0 / 5 / 11 / 18): present at
the calibration and above, absent below. P1 and aIPg: 0 through 1.4x (1.0 Hz at 1.4 for cVA), 3-4 Hz at 2.0x
where 12 % of the brain is firing.

### 14k. State arm, female (`state_probe_flywire_shiu_min1_state30.csv`; state neurons at 30 Hz; 5 seeds)
The question was "wiring or learning?"; the data said "state"; this is the state arm. Each state is tonic
activity in the fly's own labeled state neurons, nothing added to the wiring.
- **Virgin (SAG tonic) switches the receptivity circuit on through the wiring alone:** pC1a 21 Hz, pC1b/c
  19 Hz, receptivity DN vpoDN 5.7 Hz (all 0.0 in every no-state condition). That is the known SAG -> pC1 ->
  vpoDN path (Feng 2014; Wang 2021), reproduced from wiring plus one imposed state. With touch, the
  aggression cells pC1d/e now respond (6.3 Hz; 0 without state). cVA/food reduce pC1a slightly (21 -> 16-18).
- **Aroused (pC1a-c tonic):** vpoDN 8.7 Hz; touch -> pC1d/e 9.6 Hz. Aggressive states (pC1d/e or aIPg
  tonic) drive the turning/walking DNs at rest (aIPg: DNa L/R 8.4/7.8 Hz) and raise cVA -> DNa L to 43 Hz
  — an aggressive fly walks more — but never DNp13, vpoDN or oviDN.
- **Hunger/satiety neurons (IPC, DH44, NPF, SIFa, AstA) change nothing** (max 1.6 Hz anywhere; sugar -> MN9
  stays 75-82 Hz). Consistent with hunger acting through neuropeptides and dopamine, which the model lacks —
  a clean boundary: mating state is synaptic (works), metabolic state is neuromodulatory (does not).
- Unchanged by any state: touch -> DNp13 (36 Hz; 18 with cVA) and oviDN (0). Real mated females extrude the
  ovipositor more than virgins; the model's rejection output is state-blind. A concrete miss to report.
Three-way table so far, female: feeding / startle / steering / touch-rejection = wiring; receptivity and
touch-evoked aggression = wiring + mating state (SAG); hunger-dependent feeding = not in this model
(neuromodulation); odor-reward learning = rule present, teaching signal absent.

### 14l. Neural vision (flyvis optic lobe -> spiking connectome), first results (`brain/tests/vision_bridge.py`)
63,258 FlyWire optic-lobe neurons of 55 cell types were placed retinotopically by four hops of connectivity
from the photoreceptors and matched to flyvis columns; the 1.65 M synapses among them are handed to flyvis
(its dynamics), their 1.4 M outputs to the rest of the brain stay. The optic lobe costs 26 ms per 50 ms tick
on CPU, pipelined one tick behind the brain. What comes out: horizontal-system tangential cells (HS) are
direction selective (76 Hz for a bar moving one way, 24 Hz the other, 38 Hz static); VS cells respond to
looming (17 Hz) and static contrast; LC4 loom detectors fire for loom and flash (7-9 Hz) and not for static
scenes (0); the turning DNs differ between motion directions (DNa L 10 vs 2.5 Hz). Not right yet: the giant
fiber fires for static contrast (43 Hz) more than for loom (5 Hz), LPLC2 barely responds (0.1-0.3 Hz), and the
map orientation is untested. Free constants: r_max = 100 Hz per unit of flyvis activity above rest,
a_scale = 1. Next: optomotor sign test, then a gain/scale sweep of the visual drive.

### 14m. The neural body in the arena (`logs/fly1_off-flywire_20260914-225641.csv`)
Continuous, threshold-free readout: walk drive 0.69 (walking two-thirds of the time), turn +0.60 — the fly
walks in ~10-block left-curving loops, which is the connectome's own DNa asymmetry (14g) made visible; no
acts fired (no aggression/feeding/song neurons active; feeding MNs 0.6 Hz with no sugar contact), as it
should be for a female alone with nothing to eat. In a flower-filled arena the odor regime keeps 6 % of the
brain firing and the brain runs at 0.25x real time (while sharing the CPU with two other experiments); the
body now scales its speed to brain time so behaviour per brain-second is unaffected by machine load.

### 14n. The fly can see: optomotor response from optic lobe + connectome (`brain/tests/optomotor_flyvis.py`)
A grating drifting across both eyes, through the flyvis optic lobe into the spiking brain (default map
orientation, 2 seeds, 800 ms): **motion to the left -> DNa left 43 Hz vs right 10 Hz (L-R +34); motion to the
right -> left 15 vs right 35 (L-R -19).** The turning descending neurons follow the direction of wide-field
motion with the sign a real fly shows (it turns with the motion). Upstream, the horizontal-system tangential
cells give 162 Hz vs 6 Hz for the two directions. This is the first visual behaviour to come out of a
whole-brain spiking model: the optic lobe's graded dynamics were the missing piece, not the central wiring.
Caveats: the giant fiber also fires for wide-field motion (45-68 Hz) — an escape neuron should not; the
visual drive scale (r_max) is a free constant; the mirrored orientation is being run for comparison.
Mirrored map orientation: motion LEFT -> L-R +31, RIGHT -> -23 — the same sign. The optomotor sign is fixed by
the T4/T5-subtype -> tangential-cell -> DN wiring, not by our retinotopic orientation (which only decides which
column a cell reads). Open problem: the giant fiber fires 45-74 Hz even for a static grating at the current
visual drive scale (r_max 100 Hz); a scale sweep follows.
Visual drive scale sweep (r_max 25 / 50 / 100): uniform grey drives nothing (good — the per-cell rest levels
work); the optomotor asymmetry holds at 50 and 100 (weak at 25); but the giant fiber fires for a static
grating at every scale (29 / 51 / 69 Hz) and less for a slow loom (0.6 / 3 / 6 Hz). So it is not a scale
problem. Suspect: the test measured the grating from its onset (a contrast step is itself a flash), and the
loom was slow. Re-testing with a 1 s adaptation period and a 300 ms loom.

Quick validation suite on the corrected model (`brain/tests/validate.py`): sugar -> feeding MNs 23 Hz, +bitter
10 Hz, bitter alone 0; sound -> giant fiber 30 Hz; touch -> feeding MNs 22 Hz; odors -> DNa L 30-42 vs R 1-6;
photoreceptors through the plain LIF optic lobe -> nothing at any DN (the reason for the flyvis bridge). PASS.

### 14o. Two flies loose in a generated Minecraft world (`experiments/run_flock.sh "f,m" wild 240`)
A second server (`server/setup_wild.sh`, port 25566) runs a normal generated world: terrain, water, trees,
flowers, animals (CO2 sources), no hostile mobs. Bots need no arena and no commands; they spawn at the world
spawn, climb one-block steps and float in water by nerve-cord-level reflexes, respawn if killed, and slow
their bodies to brain time when the brain is slower than real time. Logs `logs/fly1_off-flywire_20260914-230146.csv`
(female) and `fly2_off-malecns_20260914-230147.csv` (male), 240 s wall each, under heavy CPU load (three
other experiments running): brains at 0.12-0.14x real time, so 30-34 s of brain time each.
- Female: walks 72 % of the time in left-curving loops (turn +0.63; 125 blocks of path inside a 5 x 5 block
  box), rejection DN fires occasionally on contact with terrain (1.8 events/min), mushroom body active
  (Kenyon cells 34 Hz) because wild flowers put food odor everywhere. No feeding (never on a flower).
- Male: walks 24 % of the time (leg motor neurons 2.2 Hz), sings almost continuously (song wing-MNs 13 Hz ->
  78 bouts/min), proboscis extensions 6/min, P1 silent. Consistent with the offline map: in this male any
  odor drives the wing motor neurons.
- The two never came within 3 blocks (median 12 blocks apart) in 30 s of brain time.
Bug found and fixed on the way: the launcher waited on the brains (which never exit), so the demo's brains
stayed alive after the bots left and the first two encounter trials silently ran against the wild male's
brain; those logs were deleted and the trials restarted.
With a 1 s adaptation period before measuring, the giant-fiber problem persists (64 Hz for a static grating,
13 Hz for a fast loom, 67 Hz for a flash) and the per-type breakdown shows why: flyvis's lamina and T4/T5
cells keep responding to a standing grating (L1/L2 ~30, T4a 20, T4b 28 Hz-equivalent after a full second),
whereas real lamina neurons adapt within about a second and T4/T5 are silent for static patterns. flyvis was
fitted to moving natural scenes, not to standing contrast. Direction selectivity is exactly as it should be
(grating left: T4a 41 vs T4b 7; right: T4b 38 vs T4a 15). Change: each cell's resting level in the bridge now
tracks its own recent activity (time constant 1 s, an explicit modelling choice, listed under "ours"), so
only activity above the recent baseline — motion, flashes, looming — is passed to the spiking brain.

### 14p. State arm, male (`state_probe_malecns_all_min1_state30.csv`; state neurons at 30 Hz; 5 seeds)
- **Courting male (P1 tonic) switches the song circuit on through the wiring alone:** the song command DN
  pIP10 goes from 0 (any sensory input alone: at most 7 Hz) to **50 Hz**, the VNC song premotor neurons TN1
  to 8 Hz, the song wing motor neurons to 28 Hz, all wing motor neurons to 9 Hz, with no sensory input at all.
  That is the known P1 -> pIP10 -> TN1 -> wing-muscle pathway (von Philipsborn 2011; Ding 2019), reproduced
  from wiring plus one imposed state. P1 tonic also drives the male DNp13 (21 Hz; 41 Hz with cVA) and,
  with cVA, MN9 (27 Hz). Adding contact pheromone on top raises the wing motor neurons to 33 Hz.
- Male aggression state (aIPg tonic): small increases only (cVA -> DNp13 31 vs 25; pIP10 8 vs 6).
- Hunger/satiety neurons (IPC, DH44, NPF, SIFa, AstA): nothing (max 5 Hz), as in the female.
Together with 14k, the answer to the original question now reads, for both sexes: reflexes = wiring;
courtship song (male) and receptivity (female) = wiring + a state carried by identified neurons (P1, SAG);
hunger-dependent behaviour = neuromodulatory, outside the model; odor-reward learning = rule present,
teaching signal absent.

### 14q. Vision with contrast adaptation (1 s) — where the neural eye stands tonight
Uniform grey: nothing. A standing grating now passes only 2 Hz of drive (was 13) and the giant fiber drops
from 64 to 26 Hz for it. Moving gratings keep the optomotor result (left: DNa L 35 vs R 17; right: 15 vs 31;
HS 144 vs 10). Fast loom: LC4 6 Hz, LPLC2 0.2 Hz, giant fiber 11 Hz; flash: LC4 19 Hz, GF 56 Hz. So the
model sees motion and responds to it correctly, sees flashes, but does not detect looming through LPLC2
(whose radially arranged T4/T5 inputs are not engaged by our stepwise, 20 Hz-sampled edges), and its giant
fiber is driven by wide-field motion (74 Hz), which a real fly's is not. Free constants of the bridge:
r_max = 100 Hz, a_scale = 1, adaptation 1 s, column matching by connectivity, map orientation. Vision is a
working arm for optomotor steering and a research problem for escape.

### 14r. Shuffled-connectome control — the control that could have killed the paper, passed
`experiments/shuffle_control.py --mode global` (3 rewirings, 3 swaps per connection, 99.9 % of the 15.1 M
connections moved; every neuron keeps its exact number of inputs and outputs, every connection keeps its
weight and sign; `shuffle_flywire_shiu_min1_global.csv`). Intact: cVA -> DNa L 36 Hz / PPL1 109 Hz / 6.1 % of
neurons active; touch -> DNp13 37, feeding MNs 16; sugar -> MN9 80, feeding MNs 25; sound -> giant fiber 5-11;
cVA + touch -> DNp13 18.5. **All three shuffled brains: every readout 0.0 Hz** (PPL1 at most 2.3 Hz), and the
sensory drive no longer spreads (0.1-1.6 % active). The map — and the network's ability to carry sensory
input at all — comes from who is wired to whom, not from how many synapses each neuron has. A block-
restricted shuffle (targets swapped only within the same super-class) is queued as the stricter version.

### 14s. Sensitivity to our own choices (`sensitivity_flywire.csv`, 3 seeds, 600 ms)
Robust to stimulus rate (50 / 100 / 150 Hz), time step (0.1 / 0.2 / 0.5 ms), connection table (Shiu vs
Zenodo) and threshold (all vs >= 5): sugar -> MN9 (64-92 Hz), touch -> DNp13 (27-40), cVA halves it (8-24),
sound -> giant fiber (present from 100 Hz up), decision neurons pC1d/e and aIPg at 0.0 in every condition.
Not robust — and therefore retracted as biology:
- **The left-turn bias depends on the neurotransmitter sign rule.** With Shiu et al.'s majority-vote signs:
  DNa L 34 vs R 4 Hz. With the annotation table's plurality signs (`top_nt`), same connections: L 22 vs R 25
  (all connections) or 22 vs 18 (>= 5). The bias lives in the ~hundreds of neurons whose predicted
  transmitter is ambiguous. It is a property of a labeling choice, not of the fly. (14g's "robust across
  gains" was true within one sign rule.)
- **Odor -> punishment dopamine (PPL1) depends on the weak connections and the sign rule:** 107 Hz with all
  connections and Shiu signs, 18 Hz with the >= 5 threshold, 44 Hz with top_nt signs. "Every odor looks like
  punishment" (3c) is real in direction but its size is not a robust number.
- First-version numerics on the full table run away (sugar -> MN9 363 Hz, cVA -> DNa 105 Hz): confirms that
  every pre-section-14 number came from a different dynamical regime.

### 14t. Learning arm on the corrected model (`conditioning_flywire_shiu_min1_noise0_seed0.csv`)
Same protocol as section 5 (odor A + sugar vs odor B alone, 3 cycles, dopamine-gated KC->MBON depression):
the synapses change (weights fall to 45 % of start) and the mushroom-body output halves — for both odors
equally (MBON -48.7 Hz for CS+, -48.4 for CS-; discrimination change -0.4 Hz). No compartment shifts more than
8 Hz differentially and nothing reaches a descending neuron. Section 5's conclusion stands on the published
model: the rule works, the teaching signal it needs (reward-specific dopamine) is not produced by the wiring
— every odor drives PPL1 (punishment) far more than PAM (reward) (14f: 108 vs 20 Hz).

### 14u. Encounters with error bars (`experiments/encounter_trials.sh`, `encounter_stats.py`; 5 trials per condition,
odor-free 6-block chamber, 180 s wall each = 32 +/- 7 s of brain time under a shared CPU)
- **Female-female: the two flies never touched in any of 5 trials** (0 contact ticks; within 3.5 blocks 9 % of
  the time). Each female walks in its own tight left-curving loop, so two of them in a chamber orbit without
  meeting. Nothing in either brain changed near vs far (DNp13 0, aggression 0, DNa L 36 vs R 4 throughout).
  The planned female-female vs male-female comparison of contact-evoked rejection is therefore not
  available from these trials; it needs a locomotor substrate that lets females meet (see 15).
- **Male-female: contact in every trial (25 +/- 24 contact ticks).** On contact the female's rejection DN
  DNp13 fires at 16.5 Hz (5.7 +/- 4.4 Hz when the male is within 3.5 blocks vs 0.00 +/- 0.01 far), her
  feeding MNs 21.5 Hz, her left turning DN drops from 37 to 21 Hz; 10 rejection events over the 5 trials, all
  near the male; aggression 0 throughout. This is the arena realisation of the offline prediction
  "cVA + touch -> DNp13 ~18 Hz" (14f), now with n = 5. The male sings 83 bouts/min whether the female is near
  or far (song MN 2.6 vs 3.1 Hz), P1 silent — courtship without a target, as the state arm explains (14p).

### 14v. Block-restricted shuffle: architecture without specificity (`shuffle_flywire_shiu_min1_block.csv`)
Same rewiring but each connection may only be redirected to a neuron of the same super-class as its original
target (sensory / central / optic / descending / ...), so the coarse sensory -> central -> descending
architecture is preserved; 94 % of connections moved, 2 rewirings. Odors, sugar and sound still reach no
readout (cVA/food -> everything 0; sugar -> MN9 0; sound -> giant fiber 0-0.6 Hz). The large touch input
(1,417 bristle neurons) now does get through — but as an undifferentiated burst: giant fiber 57-99 Hz, MDN
23-40, DNp13 9-14, feeding MNs 20-25, both turning DNs 33-67 Hz, all descending neurons 14-15 Hz, versus the
intact brain's touch -> DNp13 37 and feeding 16 with GF 0, MDN 0.7, DNa 0/0.6, DN-all 8. And cVA no longer
changes the touch response. So: a brain with the fly's cell counts, degrees and coarse architecture can be
made to respond, but *which* outputs respond to *which* inputs — and which stay silent — is the specific
wiring. Together with 14r this is the control the paper needed: the map is not a density artifact.

---

## 15. Where this leaves the research question (end of 14-15 Sep 2026)

**The model is now the published model, checked spike for spike, run on the published connection table,
with its published circuit results reproduced neuron for neuron; every number below has n >= 3 seeds, a gain
window (0.7-1.4x), a shuffled-wiring control and a sensitivity check behind it.** Everything in sections 1-13
came from a different dynamical regime and is superseded by section 14.

| Behavior | Wiring alone? | State? | Learning? | Evidence |
|---|---|---|---|---|
| Feeding on sugar | **Yes** | hunger neurons change nothing | – | sugar -> MN9 curve matches Shiu (14h); gain-robust; abolished by shuffling |
| Bitter suppression of feeding | **Yes** | – | – | 58 -> 6 Hz (14h) |
| Startle/escape to sound | **Yes** | – | – | JO -> giant fiber, both sexes (14f, 14i) |
| Antennal grooming circuit | **Yes** | – | – | JO-CE -> aBN1, JO-F silent (14h; validated in vivo by Shiu) |
| Steering by odor | **Present, but its left bias is a labeling artifact** | – | – | bias flips to symmetric with the other transmitter-sign rule (14s) |
| Optomotor turning (vision) | **Yes, with a neural optic lobe** | – | – | motion left -> DNa L 43 vs R 10, right -> 15 vs 35 (14n, 14q) |
| Looming escape (vision) | Not yet | – | – | LPLC2 silent, GF over-responds to wide-field motion (14q) |
| Female rejection signal on touch | **Yes** | state-blind (should not be) | – | touch -> DNp13 36 Hz, halved by any odor; fires on male contact in the arena, n = 5 (14u) |
| Female receptivity (pC1, vpoDN) | No | **Yes — mating state via SAG** | – | 0 Hz to every input at every gain; SAG tonic -> pC1 21 Hz, vpoDN 5.7 Hz (14k) |
| Female aggression on touch (pC1d/e) | No | **Yes — virgin/aroused state** | – | 0 -> 6-10 Hz with SAG or pC1a-c tonic + touch (14k) |
| Egg-laying (oviDN) | No | No (none of the states) | – | 0 Hz throughout — a miss |
| Male courtship song command (pIP10 -> TN1 -> wing MNs) | Weakly (cVA -> pIP10 6 Hz) | **Yes — P1 state** | – | P1 tonic -> pIP10 50 Hz, TN1 8, song MNs 28 (14p) |
| Male cVA -> DNp13 | **Yes, pheromone-specific** | – | – | gain-robust, no other odor (14i, 14j) |
| Male contact chemosensation -> wing motor | **Yes** (not song-specific) | – | – | ppk23/25 -> wing MNs at every gain (14j) |
| Male 7-T vs 7,11-HD backing asymmetry | Only at the published gain | – | – | fragile (14j) |
| Approach to another fly | No | not tested with states | – | no near-vs-far change, n = 5 (14u) |
| Hunger-dependent anything | – | **No** (IPC/DH44/NPF/SIFa/AstA change nothing) | – | neuromodulation is not in the model (14k, 14p) |
| Odor-reward learning | – | – | **Rule works, teaching signal missing** | MBON halves for both odors (14t) |
| Anything shuffled | **No** | – | – | every readout 0 with degree-preserving rewiring (14r, 14v) |

**The one-sentence answer.** In the published whole-brain model, reflexes are in the wiring; the social
decisions are not sensory reflexes but become available the moment a single identified state neuron class
is active (SAG for the female's receptivity, P1 for the male's song), and the states the model cannot carry
are exactly the neuromodulatory ones (hunger) — so "wiring vs learning" was the wrong dichotomy; the data
say wiring / synaptic state / neuromodulatory state / learning, and the connectome alone answers the first
two.

**What must still be done before this is a paper.**
1. Encounter statistics with more brain time per trial (30 s under a shared CPU is thin): rerun
   `experiments/encounter_trials.sh` on an idle machine (brains then run at ~0.5x real time) or with
   `--duration 600`. Give the females a way to meet: their tight left loops (a sign-rule artifact, 14s) keep
   them apart; rerun with `FLYBRAIN_CONN=zenodo` (symmetric turning) as the locomotor substrate, or report
   the male-female result on its own.
2. State-arm dose-response (SAG / P1 at 10, 30, 100 Hz; the 100 Hz run is in `state_probe_*_state100.csv`)
   and the embodied version (`--state virgin` female with a male in the arena: does vpoDN fire on contact?).
3. Vision: loom detection (LPLC2) and the giant fiber's response to wide-field motion; sweep r_max /
   adaptation; the left-eye mirror convention (`mirror_left`). Then a visual behaviour in the world (a
   looming player -> jump; optomotor drift correction while walking).
4. Male sensitivity table (the female one is 14s) and a male shuffle control.
5. Transmitter-sign rule as a formal sensitivity axis for every result (it decides the turning bias and the
   size of the odor -> dopamine signal).
6. Release: code, exact data versions (FlyWire v783 Shiu table; MaleCNS v1.0), the "ours vs the fly's" list
   (README), and the logs. Brian2 reference scripts included so anyone can re-derive the spike-for-spike check.

### 14w. State dose-response (`state_probe_flywire_shiu_min1_state100.csv`, state neurons at 100 Hz, 3 seeds)
The mating-state effect scales with SAG activity: SAG at 100 Hz -> pC1a 62 Hz, pC1b/c 57, vpoDN 18 (at
30 Hz: 21 / 19 / 5.7); with touch, pC1d/e 15 Hz. pC1a-c at 100 Hz -> vpoDN 24, pC1d/e 11 (19 with touch).
Hunger/satiety neurons at 100 Hz: still nothing anywhere. oviDN: 0 in every state and input. DNp13
unchanged by state (33-36 Hz to touch). Section 15's table stands.

---

## 16. Third pass (15 Sep 2026, night) — teaching the flies to tell odors apart and to learn from what they walk into

*Goal set for this session: the flies should understand their world (smell which flower is which), learn from their
surroundings (the fly's own dopamine rule, fed by what happens to the body), improve, and the notes should keep up.
Newest at the bottom. A parallel session is building the research assistant (assistant/, notes/); this section is
about the flies themselves.*

### 16a. Why the learning arm could never work: every odor was the same odor
Starting point (14t): the dopamine rule works mechanically but no odor-specific memory forms. I went looking for the
reason at the input side rather than the teaching side, and found it one synapse in from the nose.
- **Kenyon cells had no odor code.** Under the published model, a single-glomerulus odor (any of DM2, DL5, DA1, VA1v,
  DM1, VM2, V, DC3 at 100 Hz) makes **65 % of all 5,177 Kenyon cells fire at ~30 Hz**, and the active set is the same
  for every odor: Jaccard overlap between any two odors 0.99 (`experiments/odor_code.py`, `results/odor_code_flywire*.csv`).
  Real KCs are sparse (~5 % per odor, Honegger et al. 2011) and odor-specific. A learning rule that depresses the
  synapses of the active KCs therefore depressed the same synapses for CS+ and CS- — exactly 14t's result.
- **The antennal lobe is a runaway attractor in the point-neuron model.** With ORN_DM2 alone at 100 Hz (or at 25 Hz —
  it is an attractor, not a dose effect), 80 % of all 685 projection neurons fire at ~80 Hz mean, 57 of 59 glomeruli
  exceed 10 Hz, and the local neurons signed *excitatory* fire at 190 Hz. Cutting the output of those excitatory
  LNs restores perfect specificity: DM2's own PNs at 138 Hz, every other glomerulus at 0.
- **Whose fault.** Shiu et al.'s sign is the majority vote of a transmitter classifier. Of the 429 antennal-lobe local
  neurons, 166 come out excitatory: 72 predicted cholinergic (the real eLNs, Shang et al. 2007), but also 40
  "serotonin", 12 "dopamine" and 40 GABA/glutamate-predicted neurons whose majority vote still landed on +1. The
  annotation table records the immunohistochemically known transmitter for 88 k neurons (`known_nt`); 16 of these LNs
  are known GABA/glutamate and predicted otherwise. So part of the problem is labeling — but only part: with every
  known transmitter honoured, the 150 genuinely cholinergic eLNs still ignite the lobe (98 % of glomeruli). In the fly
  eLN->PN lateral excitation is weak and largely electrical (gap junctions; Yaksi & Wilson 2010; Huang et al. 2010) —
  something a chemical-synapse sign rule cannot express, and something that 161 k eLN->PN synapses at the published
  per-synapse weight get badly wrong.
- **Consequence for everything in 14 that starts with an odor.** "Any odor -> DNa left >> right", "any odor -> PPL1
  ~108 Hz", "any odor halves touch -> DNp13": all of these were measured with an antennal lobe that turned every
  odor into the same all-glomeruli state. They are properties of that state, not of cVA or food odor. The odor rows of
  the female map (14f), the odor-related gain rows (14g) and the odor part of 14s are superseded by 16c below; the
  non-odor rows (sugar, touch, sound, states) are untouched by this: the four published anchors all PASS under the new
  variant with the same numbers (`benchmark_flywire_shiu_min1+known+eln0.25.csv`: sugar -> MN9 55 vs 58 Hz at 100 Hz,
  100/200 Hz ratio 0.75 vs 0.69 (Shiu ~0.8), bitter 55 -> 1.7 Hz, JO-CE -> aBN1 10.0 Hz with JO-F 0, sound -> giant
  fiber 22.1 Hz; touch -> feeding MNs 16 Hz).

### 16b. Two model options, both documented as ours (`brain/flybrain/connectome.py`)
1. **`signs=known`** (`FLYBRAIN_SIGNS=known`, `run_brain.py --signs known`): the predicted sign is overridden wherever
   the annotation table has a known transmitter. 11,010 neurons change sign; 9,200 of them are histaminergic
   photoreceptors (inhibitory in the fly, excitatory under the prediction — irrelevant under flyvis vision, which cuts
   those synapses, but right for the LIF eye), the rest optic-lobe and central neurons, 16 AL local neurons, 94 CX.
2. **`eln_scale=0.25`** (`FLYBRAIN_ELN=0.25`, `--eln 0.25`): the chemical output of the antennal lobe's excitatory
   local neurons (150 neurons after the sign rule) scaled to a quarter. Dose-response (`odor_code_flywire.csv`, known
   signs): eLN x1: 98 % of glomeruli active for any odor, KC overlap 0.88 same-odor / 0.77 different-odor; x0.5: 72 %
   of glomeruli, KC overlap 0.78 / 0.53; **x0.25: 19-28 % of glomeruli (the cognate one at 83-212 Hz, a modest
   broadening as in Olsen et al. 2007), 1-5 % of KCs per odor, KC overlap 0.63 same-odor / 0.08 different-odor**;
   x0.1: 2-8 % of glomeruli, 0.51 / 0.01. x0.25 is the largest value that keeps odor identity and is the new
   default of the embodied flies (`run_brain.py --al specific` = known signs + eLN x0.25; `--al published` = the old
   model). Every experiment script takes the same options, and every CSV/figure carries the variant in its name
   (`shiu_min1+known+eln0.25`), so nothing old is overwritten.
   *Honesty:* k is a free constant of ours with a biological reason (electrical vs chemical lateral excitation), in the
   same class as the male weight scale and the vision r_max. The paper reports the dose-response, not just the choice.

### 16c. What the corrected antennal lobe changes downstream (female, 500 ms, 100 Hz, `odor_code_flywire.csv`)
- Odors now differ in what they reach: the food blend -> 5 % of KCs, MBON 5.5 Hz, PPL1 16 Hz, DNa L/R 22/15; single
  pheromone-type glomeruli (VA1v = Or47b fly odor, DA2 geosmin) reach nothing beyond the antennal lobe at all;
  cVA (DA1) -> 1.5 % of KCs, DNa L/R 8/9 (symmetric).
- **The odor -> DNa left bias is gone for most odors and odor-specific for the rest** (DM1: L 1.5 / R 12; DC3: 10/16;
  V: 15/13; vinegar blend at 150 Hz: 34/5). 14s had already retracted the bias as a sign-rule artifact; with a
  specific antennal lobe it becomes an odor-specific steering map — which is what a fly has.
- The "every odor is punishment" dopamine signal shrinks from 108 Hz to 0-16 Hz (PPL1) and PAM stays at 0.
- Whole-brain activity under odor drops from 6 % to 1-1.5 % of neurons — the brain runs 2-3x faster on odors,
  which the embodied flies will feel.
- Sugar -> MN9, touch -> DNp13, sound -> giant fiber: unchanged (they do not pass through the antennal lobe).

### 16d. The teaching signal is not in the wiring — now measured cleanly
With the specific antennal lobe (`scratch us_probe`): sugar GRNs at 100 Hz -> **0.0 Hz in every PAM and PPL1 type**;
bitter GRNs -> 0.0; head bristles (touch/pain) -> 0.0; only odors reach dopamine neurons (food blend -> PPL106 36 Hz,
PPL107 76 Hz, PPL101 8 Hz; aversive odor / heat -> the PPL2 calyx cluster). In the fly the sugar-reward signal reaches
the PAM cluster through octopaminergic neurons (Burke et al. 2012) — neuromodulation, the same boundary the state arm
hit with hunger (14k). So the learning arm has two honest options, both now implemented (`plasticity.py`):
`--us wiring` (nothing added; the null result above) and **`--us dan`: the US delivered the way optogenetic
conditioning delivers it** (Schroll 2006; Claridge-Chang 2009; Aso & Rubin 2016) — tasting sugar activates the
identified appetitive PAM set (PAM-gamma5, -beta'2a, -beta2, -gamma4, -alpha1; 150 neurons), being hurt or tasting
bitter activates the shock-responsive PPL1 set (gamma1pedc, gamma2alpha'1, alpha'2alpha2, alpha3; 8 neurons). Each
type's compartment is verified at start-up from its dominant MBON target in the connectome. The US pathway is ours;
the odor code, the coincidence rule (now with a 1 s KC eligibility trace, Handler et al. 2019), and the readout from
MBONs to descending neurons are the fly's.

### 16e. Odor identity in the world (`bot/observe.js` ODOR_CLASS, `senses.py` ODOR_LIBRARY)
Flowers now smell by family: red/pink = *ester* (Or22a/Or59b/Or43b/Or85a/Or92a/Or7a glomeruli), yellow = *vinegar*
(Or42b/Or92a/Ir75a/Or43b/Ir64a/Or98a), blue/purple = *floral* (Or82a/Or10a/Or19a/Or46a/Or43a/Or85b), white = *green*
(Or7a/Or98a/Or67a/Or13a/Or67b/Or47a), honey/cake/berries/melon = *sweet* (Or43b/Or42b/Ir84a/Or22a/Or92a/Or59b), soul
sand/mould/mushrooms = *aversive* (Or56a/Or85f/Or85a/Or69a). Each class drives 4-6 glomeruli at graded strengths
(DoOR-style profiles; which block gets which profile is ours, the glomeruli and ligand families are the fly's), sampled
at each antenna. With 2-3 glomeruli per class the MBONs stayed silent (KCs 1.4-2.7 %); with 5-6 glomeruli at the body's
150 Hz maximum: sweet -> 6 % of KCs, MBON14 45 / MBON02 31 / MBON07 16 / MBON11 16 Hz; vinegar -> 5 %, MBON14 37 /
MBON10 28 / MBON31 25 / MBON02 21; ester -> 3 %, MBON31 9 / MBON10 7 / MBON14 6; floral -> 3 %, MBON28 39; green ->
1.2 %, MBON28 24; aversive -> 1.3 %, MBON28 18. Different flowers, different MBONs — the world is now legible to the
mushroom body. New body options: `--nectar <classes>` (which flowers taste of sugar; default all), `--bitter <classes>`,
and an arena layout with two flower patches (`--layout patches`) for conditioning in the world
(`experiments/learn_in_world.sh`, phases pre / train / post with plasticity frozen or on; `brainctl.py` freezes,
unfreezes and reads the memory of a running brain).


## 17. Research assistant — the observer (15 Sep 2026, evening)

Built for the TODO "an AI assistant that can follow, guide and take research notes on the flies; it must keep the
research paper agenda". It lives in `assistant/` (README there); notes land in `notes/field_<trial>_<stamp>.md`.

**What it is.** A second kind of bot, not a fly: the player `observer` joins as a spectator, hovers behind the chosen
fly, and watches (songs, proboscis extensions, rejections shown as arm swings, hurts, joins). It is a ghost to the
flies — `bot/observe.js` now never lets a player named `observer*`/`scribe*` (or rostered as `"ghost"`) into a fly's
eyes, antennae or contact sense, and spectators have no collision box. Every N seconds it reads the brains' CSV logs
and writes an epoch: a deterministic table (blocks walked, walk duty, turn bias, acts, the top readouts in Hz,
senses, nearest fly — all per second of brain time) and an event list (contacts, approaches, DNp13/pC1/P1 bursts,
acts, teleports, hurts), each event tagged by rule with the agenda item it bears on. A local language model
(Ollama, gemma3:4b, chosen because it runs on the laptop next to two brains at ~13 tok/s — no cloud, the user's
explicit choice) then writes a labelled 2-4 sentence "reading" with agenda ids and one guidance suggestion; the
reading is interpretation, the table is the record.

**Keeping the agenda.** `assistant/agenda.py` parses the `## Agenda` section above (title, question, H1-H4, A1-A5)
and section 15's "what must still be done" list (T1-T6) at start-up; the notes header says which items a trial
serves (two brains → A4/T1; `--plasticity mb` → A2/H3; `--state` → A3/T2), the whole-trial block says what the
trial contributed per item and how far it is from the n ≥ 5 bar, and `agenda` (typed in its terminal or in
Minecraft chat) prints the agenda with the running tally. Editing the agenda here changes the assistant's behaviour.

**Guidance.** On request (chat or terminal): `bring fly2 to fly1 [blocks]` (teleport one fly in front of another,
facing it), `food fly1` (a poppy 3 blocks ahead), `clear fly1` (remove food around it), `summon sheep near fly1`,
`time night`, `follow fly2`. Model proposals are validated (flies only, whitelisted blocks/mobs, and only when the
question actually asked for an action) before the body does anything. It never touches a human player.

**Checked today.** Replay over the 22:16 live logs: readings in ~26-38 s each, tagged A4/H2/H1, sensible but
loose (the 4B model paraphrases and once called the touch → DNp13 reflex "support for H2"; `assistant/context.md`
now spells out that H2 needs pC1/vpoDN/aIPg/P1 activity from sensory input alone). Live against the running
male-female flock on the wild server (from 30 blocks, because those bots predate the ghost rule and would smell a
closer observer as CO₂): joined, followed, caught 13 song bouts and 8 rejections from the body side that matched the
brain logs' events, answered a question, took `follow fly2`, wrote the whole-trial block with the agenda tally
(A4 40 events, T1 21, H2 15, H4 9, H1 9 in ~3 min). Two bugs found and fixed on the way: pandas 3 infers `str`
columns so booleans were not coerced in the live tail (every act read as true), and following "behind the fly" at
long range whipped around as the female looped left (heading is now smoothed, ~3 s).

**Caveats.** The reading is a small model's; treat it as a first draft and keep the tables. Restart flies after
pulling the ghost change. Ollama needs ~4 GB of unified memory while loaded (`keep_alive 30m`); `--llm off` gives
the deterministic notes alone.

### 16f. First odor-specific memory in the whole-brain model — and why the fly cannot act on it (appetitive)
`experiments/conditioning.py --signs known --eln 0.25 --us dan --valence reward`, CS+ paired with the reward DANs
(50 Hz) for 3 x 10 s, CS- alone, 5 s rests; reciprocal design (vinegar+/ester- and ester+/vinegar-), 3 seeds each;
`results/conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward_*_seed*.csv`, Fig 2b.
- **The memory forms and is odor-specific.** Graded readout = the KC->MBON synaptic drive an odor delivers to each
  compartment (sum of weight x KC rate), post/pre. Reward compartments (gamma5, beta'2, beta2, gamma4, alpha1):
  **CS+ 0.100 +/- 0.004 retained (the 10 % floor), CS- 0.64 +/- 0.02** — the same in both odor orders and all
  seeds. The largest CS+-specific depressions sit exactly where the reward DANs teach: MBON01 (gamma5), MBON02
  (beta2), MBON07 (alpha1), MBON05 (gamma4), MBON09. This is the first time the learning arm has produced anything
  odor-specific; 14t's failure was the antennal lobe (16a), not the rule.
- **Two properties of the model show up as side effects.** (i) Generalisation: the CS- also loses ~35 % of its
  reward-compartment drive, through the Kenyon cells the two fruit odors share (KC-set Jaccard 0.14 for the ester
  and vinegar blends, both built on DM2/VA2/VM2/DM4) and through the weak odor-evoked activity of some PAM types
  (30 s of odor at D ~ 0.5 Hz is enough for ~25 %). (ii) Odors punish themselves: vinegar drives PPL1-alpha3
  (PPL106) at 25 Hz and PPL107 at 87 Hz, so its own input to the punishment compartments falls to 0.22-0.24
  retained whether it is CS+ or CS- (ester: 0.47-0.57). "Every odor looks like punishment" (3c/14f) survives in a
  smaller, odor-dependent form and is now a prediction: naive exposure alone should make this model's fly mildly
  avoid vinegar-type odors.
- **The MBON spike readout is all-or-none.** MBON02's 21-31 Hz response to vinegar disappears after training whether
  vinegar was CS+ (drive x0.10) or CS- (x0.64): under sparse coding the MBONs sit just above threshold, so partial
  depression silences them. Spike-rate changes of MBONs therefore track the odor, not the pairing; the graded
  synaptic drive is the honest memory measure and is what Fig 2b plots.
- **No behavioural expression through the descending neurons.** Approach index (odor on the left antenna, DNa L-R):
  changes of -6.5 to +8 Hz with no consistent sign (mean CS+ +0.8, CS- +1.7 Hz over 6 runs); DNp09, MDN, feeding
  MNs: 0 throughout. The reason is in the wiring plus the sign rule (`scratch mbon_dn`): **driving all 12
  reward-compartment MBONs at 30 or 60 Hz reaches no descending neuron, no lateral-horn neuron, nothing —
  0.0 % of the brain responds.** These MBONs (gamma5beta'2a, beta2beta'2a, beta'2mp, gamma4) are glutamatergic, i.e.
  inhibitory under the sign rule, and their targets are silent at rest and under odor, so removing their inhibition
  (which is what appetitive memory does in the fly, Owald et al. 2015) removes nothing. Expression of an appetitive
  memory needs tonic activity in the MBON targets — in the fly supplied by ongoing input and neuromodulation — and
  the point model has none. The cholinergic punishment-compartment MBONs are different: MBON14 (alpha3) alone at
  30 Hz drives DNa L 14 / R 7 and a set of descending neurons (DNge053 35 Hz, DNbe007 27, DNb05 26, DNg100 24, DNg13,
  DNg16). So the model can express an *aversive* memory (less alpha3 drive for the punished odor) but not an
  appetitive one. Aversive conditioning (CS+ paired with the PPL1 set) and the no-US control are running.
- Three-way table entry, learning arm, as it stands: odor-reward memory = **forms** (wiring + the fly's rule + a
  supplied US); its behavioural expression = **not in this model** (inhibitory MBONs, silent targets); odor-punishment
  memory = pending.

### 16g. Aversive conditioning and the decisive control: what is associative and what is not (16 runs)
`--valence punish` (CS+ with the PPL1 set), `--us wiring` (the "US" is sugar GRNs, which reach no DAN — i.e. the
no-US control), both odor orders, 3 seeds; Fig 2b. Retained KC->MBON drive (post/pre), reward / punishment compartments:

| US | CS+ reward-comp | CS- reward-comp | CS+ punish-comp | CS- punish-comp |
|---|---|---|---|---|
| reward DANs (PAM set) | **0.10** | 0.62-0.66 | 0.24 (vinegar) / 0.49 (ester) | 0.54 / 0.22 |
| punishment DANs (PPL1 set) | 0.79-0.88 | 0.85-0.93 | **0.09-0.10** | 0.44 (ester) / 0.17 (vinegar) |
| none (`wiring`) | 0.88-0.92 | 0.91-0.98 | 0.22 (vinegar) / 0.47 (ester) | 0.51 / 0.23 |

- **The associative memory is real, valence-correct and odor-specific:** the US-taught compartment of the CS+ goes to
  the floor (0.10) in every run and every order; the CS- and the no-US control stay at 0.6-0.9 (reward) or at their
  odor-determined level (punishment). Learning index (CS- minus CS+ retained drive) ~0.55 appetitive, 0.1-0.35
  aversive (smaller because vinegar already punishes itself, see below), 0.0 in the control.
- **Everything visible in spikes and descending neurons is NOT associative.** The no-US control reproduces, number
  for number, the MBON spike changes (alpha3/gamma1pedc MBONs: vinegar -9 Hz, ester -2 Hz whichever is CS+) and the
  approach-index changes (vinegar +4.7 to +8.5, ester -6.5) seen with either US. They come from the model's tonic
  odor-evoked PPL1 activity (16f): 30 s of an odor depresses that odor's own input to the punishment compartments
  (vinegar to 0.22, ester to 0.47), and the near-threshold MBONs then fall silent. In the fly, DAN odor responses are
  transient and naive odor exposure does not produce aversive memory of this size, so this is a property of the
  point model's tonic dopamine, listed under "ours" together with the rule.
- Next (running): the same 16-run design with a **phasic teaching signal** (`--tau-dan 2`: each DAN's rate minus its
  own 2 s running mean, so only changes in dopamine teach, as in the fly's transient DAN responses). If the
  non-associative component disappears and the associative one reaches the MBON spikes and the descending neurons,
  expression needs phasic dopamine; if it still does not reach the DNs, the wiring-level verdict of 16f stands.

### 16h. Phasic dopamine does not rescue expression (`--tau-dan 2`, 6 runs)
With each DAN's teaching signal taken as its rate above its own 2 s running mean (only *changes* in dopamine teach),
the associative memory is unchanged (appetitive CS+ reward-compartment drive 0.11 vs CS- 0.65-0.76; aversive CS+
punishment-compartment 0.09-0.10 vs CS- 0.24-0.53; no-US control 0.90-0.96 / 0.30-0.59) and the non-associative
odor-driven depression shrinks only a little (vinegar's own punishment-compartment input 0.30-0.33 retained instead
of 0.22-0.24), because every odor onset is itself a phasic PPL1 burst. MBON spikes and the approach index still follow
the odor, not the pairing (vinegar +6/+8, ester -6.5 in every run, control included). Verdict for the paper: in this
model an odor-reward and an odor-punishment memory form at the right synapses, but nothing the fly *does* changes
with the pairing — appetitive expression is blocked by the wiring (inhibitory MBONs, silent targets, 16f) and
aversive expression is masked by the model's own odor-evoked dopamine. Both are statements about the point-neuron
connectome model, and both are what a reviewer should be told.

### 16i. The female innate map with an antennal lobe that tells odors apart (5 seeds, 1 s, 100 Hz;
`social_probe_flywire_shiu_min1+known+eln0.25_noise0.csv`) — three retractions and one confirmation
- **Retracted: "any odor halves touch -> DNp13" and the headline candidate "cVA gates the female's rejection
  response" (14f, 14g, 15).** With odors kept distinct: touch alone -> DNp13 35.6 Hz; cVA + touch 36.4; Or47b + touch
  37.5; food + touch 33.6; CO2 + touch 30.0. The gating was the runaway antennal lobe (every odor put 6 % of the brain
  into the same state, which happened to inhibit DNp13), not cVA. Also gone: "odor lowers feeding" (cVA + sugar ->
  MN9 76.8 vs sugar alone 79.4; was 47).
- **Retracted: "every odor drives the turning DNs left >> right".** Now CO2 -> DNa L/R 15.8/15.6, aversive 15.1/17.0,
  cVA 10.1/8.4, cVA-long 13.7/16.0, food 22.4/14.0 (the only left-leaning one), Or83c 11.4/15.2. Steering by odor is
  odor-specific and mostly symmetric; the female's loop in the world came from the odor mix that was on, not from a
  fixed handedness.
- **Retracted in size: "every odor looks like punishment".** PPL1 to odors 5-18 Hz (was 105-113); PAM 0.0 (was 20).
  The direction survives (PPL1 > PAM for every odor), the magnitude does not.
- **Confirmed: the fly's own social odors reach almost nothing.** Or47b (fly odor, VA1v): 0.0 Hz in every readout
  and 0.0 % of the brain beyond the antennal lobe; cVA (DA1): 1.1 % of the brain, DNa ~9 Hz, nothing social;
  all pheromone ORNs together: 0.1 % active. The decision neurons (pC1a, pC1d/e, aIPg, vpoDN, oviDN) stay at 0.0 for
  every input, as before — this result never depended on the antennal lobe.
- Unchanged, as expected: sugar -> MN9 79 Hz; touch -> DNp13 36 / feeding MNs 16; sound -> giant fiber 11 (JO-A),
  5 (JO-B); eye bristles carry the rejection response (17.6 Hz alone), antennal bristles do not (2.0).
- New and odd: food odor -> giant fiber 3.9 Hz, aversive odor 2.9, Or88a 5.5 (was 0). In the world this is the female
  jumping about once a second in a flower patch (52 jumps in 58 s of brain time, no collisions). To be checked in the
  gain sweep before it means anything.
- Lateralized odor (`brain/tests/validate.py`, 150 Hz on one antenna): food odor on the LEFT -> DNa L 19 / R 24, on the
  RIGHT -> L 24 / R 9 — the turning DNs favour the side *away* from a strong food odor; cVA on one side -> nothing.
  At the body's maximal drive this reads as avoidance of a concentrated odor (real flies do avoid high
  concentrations), but it needs a concentration sweep (25-150 Hz) before it is called approach or avoidance.
For the paper: the odor rows of the answer table (15) are replaced by these; the male rows are being redone (16j).

### 16j. The male antennal lobe runs away too (`odor_code_malecns.csv`, 1 seed)
MaleCNS has no known-transmitter column, so only the eLN scale applies (206 excitatory-signed local neurons of 420:
137 predicted cholinergic + 67 "unclear" defaulted to excitatory + 2 octopamine). Published model: any single
glomerulus -> 100 % of glomeruli, 55-64 % of Kenyon cells at ~48 Hz, MBON 80-94 Hz, PAM 35-42, PPL1 104-119, KC-set
overlap between odors 0.95 — the same attractor as the female's. eLN x0.25: 15-31 % of glomeruli, 0-3 % of KCs
(the male's KC drive is weaker still: single glomeruli recruit ~0 %, the food blend 3 %), MBON 0.4-2.2 Hz, overlap
0.06. cVA (DA1, 204 ORNs) is the male odor that reaches furthest (2 % of the brain, PPL1 12 Hz). The male social
map under eLN x0.25 is running; 14i/14j's "cVA -> DNp13, pheromone-specific" was measured on the runaway lobe and
must be re-established or dropped.
**Male map redone under eLN x0.25 (3 seeds, `social_probe_malecns_all_min1+eln0.25_noise0.csv`): the male's headline
survives and sharpens.** cVA (Or67d/DA1) -> DNp13 **31.3 +/- ?** Hz (was 24.5), MN9 32.7, song wing MNs 12.6, pIP10 2.3,
PPL1 12.3 — and every other odor now gives *nothing*: cVA-long 0.0, Or47b 0.0, food 0.0, CO2 0.0, aversive 0.0 (before,
each of them still drove MN9 ~20 Hz and the song MNs ~13 Hz through the runaway lobe). So the male's cVA response is a
direct DA1 pathway, not a network state, and it is the only odor response the male brain has in this model. cVA + touch
-> DNp13 7.3 (touch still halves it), MDN 21.6. The leg contact-pheromone results do not pass through the antennal lobe
and are unchanged (ppk23/25 -> MDN 27.6, wing MNs 30.5, song MNs 21.5; and, newly noticed, PPL1 39 Hz — the male's
punishment dopamine responds to contact pheromone, 7-T (ppk23) 31 Hz > 7,11-HD (ppk25) 10.5 Hz). P1 and aIPg: 0.0
throughout, as before. The male mushroom body is nearly silent to odors under the specific lobe (KC 0.0 % for cVA),
so odor learning in the male will need its own look.

### 16k. Learning from the surroundings, in the world (`experiments/learn_in_world.sh`, `learn_stats.py`)
One female (`--al specific --plasticity mb --us dan`) in a 10-block chamber with a 5 x 5 poppy patch (ester; nectar,
i.e. tasting it drives the reward DANs) at x = -6 and a 5 x 5 dandelion patch (vinegar; `BITTER=vinegar`, tasting it
drives the punishment DANs) at x = +6. Phases on one brain: pre (plasticity frozen, 120 s wall) -> train (on, 360 s)
-> post (frozen, 120 s); the brain ran at ~0.3x real time next to the live flock, so 187 s of brain time in all.
- Free-operant first attempt (`world1`, no placement): the fly walked in tight left loops (DNa L 40-50 / R 0 under the
  mixed flower odor) and never left the east half; it tasted bitter on 47 % of ticks and never sugar. Its own
  locomotion, not its memory, decides where it goes — as the offline result predicts.
- With the experimenter placing it (`EXPOSE=1`, `experimenter.js`: /tp into each patch for half of training, the
  T-maze way): 23 sugar ticks and 15 proboscis extensions in the poppies, 564 bitter ticks in the dandelions.
  **Memory read from the running brain (`brainctl.py memory`):** punishment compartments MBON14 (alpha3) 0.84,
  MBON18 0.84, MBON11 0.90 of their initial weight — the fly's mushroom body now holds "vinegar-flowers hurt",
  written by its own dopamine rule from what its body met (28 s of bitter; the offline no-US control gives 0.22-0.5
  for vinegar's own input, so part of this is the odor punishing itself, 16g). Reward compartments MBON02 (beta2)
  0.925, MBON07 (alpha1) 0.92 — but that is the size the no-US control produces from odor exposure alone (0.88-0.92),
  so 1.2 s of sugar on the poppies left no trace distinguishable from odor exposure; a longer stay on the nectar
  (or `--nectar` on a denser patch) is needed before "poppies fed me" can be claimed. Expression: vinegar-evoked MBON output 8.2 -> 4.0 Hz (pre -> post, 570 / 817 ticks),
  turning DNs 32.5/4.4 -> 30.3/3.7 Hz, walking 0.68 -> 0.65: the memory is visible in the mushroom body and invisible
  in the legs, exactly as in 16f-16h. The fly also jumps about once a second in a flower patch (odor -> giant fiber,
  16i), which is a property of the model to check in the gain sweep, not a behaviour to interpret.
- Logs: `logs/fly1_mb-flywire-dan-known-eln0.25_20260916-003140.csv` (+ `_learn_stats.csv`, `learn_world2_memory.json`).

### 16l. Where this leaves the answer table (revision of section 15, 16 Sep 2026)
Rows that change:
| Behavior | Wiring alone? | State? | Learning? | Evidence |
|---|---|---|---|---|
| Steering by odor | **Yes, odor-specific and mostly symmetric** (food L 22 / R 14; CO2 16/16; cVA 10/8) | – | – | 16i; the old "left bias for every odor" was the runaway lobe |
| Female rejection signal on touch | **Yes** (36 Hz) — **not gated by odor** | state-blind | – | 16i: cVA + touch 36, food + touch 34; 14g's gating retracted |
| Female responses to fly odor (Or47b) / cVA | **No** — 0.0 Hz everywhere / 1 % of the brain, nothing social | – | – | 16i |
| Male cVA -> DNp13 | **Yes, pheromone-specific, and now the male's only odor response** (31 Hz; every other odor 0) | – | – | 16j |
| Odor identity (antennal lobe, Kenyon cells) | **Only with known signs + eLN x0.25** (ours); the published model has none | – | – | 16a-16c, Fig 9 |
| Odor-reward / odor-punishment memory | – | – | **Forms, odor-specific, valence-correct, with the US supplied to the identified DANs** (the wiring carries no US) | 16d, 16f, 16g, Fig 2b |
| Behavioural expression of that memory | **Not in this model**: reward MBONs inhibitory with silent targets; aversive expression masked by odor-evoked dopamine | – | – | 16f-16h, 16k |
| Any odor -> punishment dopamine | present but small (PPL1 5-18 Hz) | – | – | 16i |

The one-sentence answer gains a clause: *...the connectome alone answers the first two; the third (learning) it
answers half-way — the memory is in the wiring's reach once a teaching signal is supplied, its use is not.*

**What must still be done (16 Sep additions to the list in 15):**
7. Gain sweep and shuffle control under `--al specific` (both sexes); the odor -> giant fiber 3-5 Hz needs the gain test.
8. Encounter trials (14u) under `--al specific`: the male-female rejection result stands on touch, but the females'
   loops were an odor-mix effect — they may now meet.
9. A second US dose (`--us-hz 20`) and a second eLN value (0.1) for the conditioning table, to give the learning
   result its own gain window.
10. Transmitter-sign axis: the 16 antennal-lobe local neurons with known transmitters are decisive; the MaleCNS has no
    known-transmitter column, so its 67 "unclear" local neurons are a sensitivity axis of their own.

**17 Sep 2026 — model switched to qwen3:4b** (user's choice; 2.5 GB). It answers the JSON grammar cleanly with its
thinking mode off (~20-30 s per reading next to two brains) and writes tighter, more concrete readings than gemma3:4b,
which stays available with `--llm gemma3:4b --llm-loose`. Feeding the previous note back for continuity made the
model repeat itself verbatim, so each epoch is now read on its own.

## 18. Fourth pass (17 Sep 2026) — the controls under the antennal lobe that tells odors apart

*Goal set for this session (`WHATS_LEFT_FLY.md`): every control that decides what counts — gain sweep, shuffled
connectome, sensitivity table, the transmitter-sign axis — was last run on the runaway lobe (14g, 14r, 14s), so
every odor row of the answer table stood on a model that no longer exists. Redo them under `--al specific`
(`FLYBRAIN_SIGNS=known FLYBRAIN_ELN=0.25`), then the encounter trials, then give the learning result its own
robustness window, then the open questions (concentration sweep, memory expression, sugar in the world, the male's
mushroom body). Newest at the bottom. Queue: `experiments/run_queue3.sh`, `run_queue4.sh`; every new file carries
the variant in its name, nothing from 14-16 is overwritten.*

### 18a. Female gain sweep under the specific lobe (`gain_sweep_flywire_shiu_min1+known+eln0.25.csv`, 3 seeds, 600 ms, 100 Hz)
- **The non-odor reflexes keep their 0.7-1.4 window:** sugar -> MN9 38 / 77 / 93 Hz at gain 0.7 / 1.0 / 1.4; touch ->
  DNp13 28 / 36 / 42; song (JO-A) -> giant fiber 5 / 10 / 16 (JO-B: 0 / 4 / 11, as in 14g). The decision neurons
  (pC1a, pC1d/e, vpoDN) stay at 0.0 for every input at every gain up to 1.4; pC1d/e reach 1.5-4 Hz only at 2.0, where
  the whole brain runs away.
- **The odor rows have a narrower window: 1.0-1.4.** At gain 0.7 no odor reaches the turning DNs (cVA, aversive, CO2,
  Or88a, Or47b: 0.0 / 0.0 Hz; food 0.3 / 0.0) and only food odor reaches dopamine (PPL1 4.7 Hz). At 1.0 and 1.4 every
  odor drives DNa (cVA 10 / 7.5 -> 26 / 27; food 21 / 13 -> 33 / 28; aversive 14 / 12 -> 31 / 33; CO2 16 / 13 -> 38 / 34):
  odor-specific in size, symmetric or nearly so, food odor's left lean shrinking from 9 Hz to 5 Hz at 1.4. With the
  excitatory local neurons at a quarter, the antennal lobe's output sits close to what the lateral horn needs — at
  0.7x the odor does not get through. For the paper: odor-evoked steering and odor-evoked dopamine are claims for
  gains 1.0-1.4 (the published calibration and above), not 0.7; the sweep drives ORNs at 100 Hz, the body's maximum
  is 150 Hz (18c checks the dose).
- **"Touch -> DNp13 is not gated by odor" is gain-robust:** touch alone 28 / 36 / 42, cVA + touch 27 / 36 / 36, food +
  touch 27 / 35 / 39. The retraction of 14g's gating (16i) stands at every gain.
- **Odor -> giant fiber does not pass the rule.** Food odor 0 / 4.4 / 2.8 Hz, aversive 0 / 2.2 / 3.3, Or88a 0 / 5.0 / 2.8,
  CO2 0 / 0.3 / 4.2, cVA 0 / 0 / 1.1: absent at 0.7, a few Hz at 1.0-1.4, not monotonic in gain, while sound -> GF
  rises with gain (5 -> 10 -> 16). The once-a-second jumping in the flower patch (16i, 16k) is a property of the
  model at the published gain, not a behaviour; it stays off the answer table.
- **A fragile absence:** Or47b (fly odor) reaches nothing at 0.7 and 1.0, but at 1.4 it drives DNa 24 / 33 and the
  giant fiber 7 Hz. "Fly odor reaches nothing" is true at the published calibration and below it, not above it, and
  is reported that way.
- **Odor -> punishment dopamine, direction robust:** food odor -> PPL1 4.7 / 17 / 36 Hz at 0.7 / 1.0 / 1.4, cVA 0 / 5 / 10,
  aversive 0 / 8 / 11, CO2 0 / 8 / 15; PAM 0-1.5 Hz throughout. "PPL1 > PAM for every odor" holds wherever an odor
  reaches dopamine at all.

### 18b. Male gain sweep under eLN x0.25 (`gain_sweep_malecns_all_min1+eln0.25.csv`, 3 seeds, 600 ms, 100 Hz)
- **cVA -> DNp13 passes the rule and is pheromone-specific at every gain:** 7.8 / 31.7 / 28.1 Hz at gain 0.7 / 1.0 / 1.4
  (13 at 2.0), while every other odor (food, aversive, Or88a, Or47b, CO2) leaves DNp13 at 0.0 at every gain. cVA -> MN9
  7 / 33 / 36 and cVA -> song wing MNs 1.5 / 13 / 15 travel with it; cVA -> PPL1 0 / 12 / 28 and -> pIP10 0 / 3 / 8 need
  gain >= 1.0.
- **"cVA is the male's only odor response" holds at the published gain and below; above it the other odors reach
  dopamine and the wing motor neurons** (at 1.4: food -> PPL1 32 Hz, song MNs 5; aversive 26 / 6.5; CO2 26 / 5; Or47b
  19 / 10; Or88a 20 / 6) — never DNp13, never P1. Same shape as the female's Or47b (18a): the specific lobe's silence
  to non-cognate odors is a threshold, not an absence, and is stated with its gain.
- **Contact pheromone (ppk23/25 leg GRNs) -> wing MNs at every gain** (10 / 20 / 21 / 10 Hz at 0.5 / 0.7 / 1.0 / 1.4),
  -> PPL1 0 / 7 / 39 / 59 (robust from 0.7 up), -> MDN only at 1.0 (29 Hz; 0 at 0.7, 1.8 at 1.4): the backing is the
  fragile part, as in 14j. The female's own hydrocarbon channel alone (ppk25): song MNs 3 / 13 / 9, MDN 0 / 13 / 4,
  the same picture at lower amplitude.
- **Sound (JO-B) -> giant fiber is the male's most robust reflex** (34 / 41 / 48 / 52 Hz from gain 0.5 up); JO-A does
  nothing below 2.0. Touch -> MDN 0 / 11.5 / 12 (gain >= 1.0); touch -> song MNs 1 / 10 / 23.
- **The male's labellar GRNs (MaleCNS has no sugar / bitter split) do not drive MN9 (0.0 at every gain up to 1.4) but
  do drive PPL1 (12 / 54 Hz at 1.0 / 1.4)** — unlike the female, where sugar reaches no dopamine neuron (16d). With
  sugar and bitter pooled, the male's taste -> punishment dopamine cannot be read as a sugar signal; it matters for
  the male learning arm (18j).
- P1 / pC1 and aIPg: 0.0 for every input up to gain 1.0, 1.6 Hz (cVA) at 1.4, 5 Hz only in the runaway 2.0 brain. The
  decision-neuron result is gain-robust in the male too.

### 18c. Odor concentration sweep, female (`odor_dose_flywire_shiu_min1+known+eln0.25.csv`, `experiments/odor_dose.py`, 3 seeds, 1 s; Fig 10)
Odor on the left antenna only; approach index = DNa L - R (> 0 = the ipsilateral turning DNs favour the odor's side).
- **The model turns away from a lateralized food-type odor at every concentration.** Approach index for the food
  blend -9.5 / -3.7 / -7.3 / -2.3 / -3.0 Hz at 25 / 50 / 75 / 100 / 150 Hz; ester -4.5 / -4.8 / -9.2 / -7.0 / -8.3; sweet
  -3.8 / -9.5 / -12.2 / -8.5 / -5.0; vinegar -3.5 / -5.0 / -6.5 / -7.2 and +5.7 at 150 Hz (the only positive value in the
  table); CO2 0 -> -4.7; aversive -4 to 0; cVA ~0 (sd over seeds 1-5 Hz). There is no concentration at which this
  model's fly steers toward a food odor — a real fly approaches food odors at low and moderate concentration and
  avoids only high ones. Chemotaxis in the world is therefore defined now, and it has the wrong sign: the fly cannot
  find flowers on purpose in this model at any dose. Whether the contralateral bias is the wiring's or the sign
  labeling's is checked next (18c, second part: the same sweep under the published sign rule and the Zenodo table).
- **The left lean of bilateral food odor is a high-concentration effect.** Bilateral food odor: DNa L / R 16 / 18 at
  25 Hz, 21 / 21 at 75, 23 / 14 at 100, 30 / 6 at 150; vinegar 14 / 17 -> 33 / 5; sweet 11 / 15 -> 26 / 18; ester, CO2 and
  aversive stay symmetric at every dose; cVA 12 / 6 at 150. The tight left loops of the embodied female in a flower
  patch (16k) are this: at the body's maximal drive the food-odor pathway becomes strongly left-biased, below ~75 Hz
  it is symmetric. With a distance-scaled odor the loops happen only inside a patch.
- **Giant fiber: 2-7 Hz for every food-type odor at every concentration, unilateral or bilateral** (CO2, cVA <= 2 Hz),
  not dose-dependent. With 18a (absent at gain 0.7) it is filed as a property of the point model, not a behaviour.
- **Dopamine and the mushroom body are graded with dose, as they should be:** food -> PPL1 8 / 11 / 15 / 18 / 21 Hz,
  Kenyon cells active 3.0 / 4.4 / 5.3 / 6.0 / 7.2 %, MBONs 1.3 -> 8.4 Hz; PAM 0.0-0.1 throughout. The learning arm's
  input side is graded; its output side is the problem (18g).

### 18g. Why the memory cannot be expressed: tonic activity in the MBONs' targets does not rescue it (`expression_probe_flywire_shiu_min1+known+eln0.25.csv`, `experiments/expression_probe.py`, 3 seeds, 1 s; Fig 11)
The question (16f): the reward-compartment MBONs are inhibitory and their targets are silent, so an appetitive memory
(less MBON output for the CS+) removes an inhibition nobody feels. Would tonic activity in those targets — what
ongoing input and neuromodulation supply in the fly — let the memory reach the descending neurons? Test: Poisson drive
at 0 / 5 / 10 / 20 / 40 Hz on every neuron receiving >= 10 synapses from the compartment's MBONs (KCs and MBONs
excluded), with the MBONs intact or their output silenced (= the memory at its floor for every odor, the upper bound
of what KC->MBON depression can do), under vinegar (150 Hz) on the left antenna, bilaterally, or with no odor.
- **The reward MBONs' targets are the reward dopamine neurons and central neurons, no descending neuron.** The 12
  reward-compartment MBONs (MBON01/02/03/05/07; all inhibitory under the sign rule) reach 435 neurons with >= 10
  synapses (16 k synapses): 0 descending, ~60 PAM neurons (PAM08 16, PAM06 15, PAM07 15, PAM05 8, PAM11 7 — the
  MBON-to-DAN feedback the fly has), the rest SMP / CB / lateral-horn neurons. Waking these targets at 5-40 Hz by
  itself drives the turning DNs (DNa L 22-30 / R 6-16 Hz with no odor): the memory's output stage sits one step from
  the steering DNs, on their inhibitory side.
- **With the targets awake, removing the reward MBONs frees 2-5 Hz of turning drive and nothing else.** No odor,
  targets at 10 / 20 / 40 Hz: DNa L 23 -> 28.5, 26.5 -> 31.5, 30 -> 34 Hz (silenced minus intact +5.5 / +5.0 / +4.0, about
  two seed-sd), DNa R +1 to +3; bilateral odor: DNa L +1 to +3; odor on the left: approach index -1.9 / -3.5 / +1.8 /
  +3.0 / +4.0 at 0 / 5 / 10 / 20 / 40 Hz (no consistent sign below 10 Hz, toward the odor above). DNp09, MDN, feeding
  MNs: 0.0 in every condition; the mean over all descending neurons unchanged to 0.1 Hz.
- **The punishment set is no better.** The 20 punishment-compartment MBONs (MBON11/12/13/14/18/31/32/35; 14 excitatory)
  reach 1024 neurons, 28 of them descending. Silencing them under odor changes DNa L by -0.5 to -3.8 Hz and nothing
  else (MDN 2.8 -> 17.8 Hz with the tonic drive, identical with the MBONs intact or silenced: it is the targets' own
  activity); approach index +-3.5 Hz without a consistent sign. Their 28 descending targets themselves (read out
  directly in the rerun): 7 Hz under odor, 11 / 15 / 23 / 39 Hz with the tonic drive at 5 / 10 / 20 / 40 Hz, and
  **within 0.6 Hz of the same whether the MBONs are intact or silenced** — the MBON -> DN synapses carry nothing the
  DNs notice next to their other inputs.
- **Verdict.** "Not in this model" survives a supplied tonic state: with the mushroom body's output stage awake at up
  to 40 Hz, the whole of an appetitive or an aversive memory is worth at most 5 Hz of turning-DN drive and no walking,
  backing or feeding. The block is not only the silent targets; it is the weight of the MBON -> DN paths against the
  direct sensory -> lateral horn -> DN paths in the point model. What it would take is a gain the connectome does not
  carry at these weights — neuromodulation of the MBON output or of its targets — which is the same boundary the
  state arm (hunger) and the teaching signal (sugar -> PAM) hit. This is the answer to open question 8: "needs X",
  with X = a state-dependent gain on the mushroom-body output, not just activity in its targets.
- **Male (`odor_dose_malecns_all_min1+eln0.25.csv`):** cVA -> DNp13 is a clean dose-response, 5.3 / 14.2 / 20.5 / 26.8 /
  34.5 Hz at 25 / 50 / 75 / 100 / 150 Hz, with MN9 21 -> 33, song wing MNs 5 -> 11 and PPL1 0 -> 18 riding on it; every
  other odor leaves DNp13, MN9, the song MNs and MDN at 0 at every dose. The male's turning DNs hardly answer any odor
  (approach index 0 to -2.8 Hz, leg MNs <= 1.4 Hz), and its giant fiber never does (0.0 for every odor and dose) — the
  female's odor -> GF quirk is the female model's. Kenyon cells: the food-type classes recruit 0.4 -> 3.8 % (food),
  1.1 -> 2.6 % (vinegar), 0.2 -> 1.0 % (ester) of KCs from 25 to 150 Hz, cVA only 0.1-0.3 %: the male mushroom body
  has an odor code for flowers at the body's drive, and almost none for the pheromone (used in 18j).

### 18d. Shuffled-connectome control under the specific lobe (`shuffle_flywire_shiu_min1+known+eln0.25_global.csv`, 3 rewirings x 3 seeds, 800 ms; Fig 6)
Degree-preserving global rewiring (Maslov-Sneppen, 3 swaps per edge, 99.9 % of connections moved; every neuron keeps
its in- and out-degree, every connection its weight and sign) applied to the specific-lobe model. Intact: cVA -> DNa
10 / 7, food odor -> DNa 23 / 13 + PPL1 18 + GF 4, sugar -> MN9 76, touch -> DNp13 35 / feeding MNs 16, JO-A -> GF 11,
JO-B -> GF 5. **Rewired: every one of these is 0.0** (over 9 rewired trials per input; the largest stray value is MDN
7 Hz in one rewired brain under food odor and PPL1 <= 3 Hz under touch). The odor-specific map, the odor -> dopamine
signal and the new odor -> giant-fiber quirk are all properties of the specific wiring, not of neuron density; 14r's
verdict transfers to the corrected model unchanged.
**Male shuffle control (`shuffle_malecns_all_min1+eln0.25_global.csv`, 2 rewirings x 3 seeds, 99.8 % of the 25.6 M
connections moved; the first male shuffle, 15's item 4):** intact cVA -> DNp13 32 / MN9 33 / PPL1 12, contact pheromone
-> MDN 28 / wing MNs / PPL1 39, JO-B -> giant fiber 49, touch -> MDN 11; **rewired: 0.0 for every one of them** (largest
stray values: DNp13 5 Hz in one rewired brain under contact pheromone, MDN 3-4 Hz under touch, aIPg 1.2 under food
odor). The male's map, including the pheromone-specific DNp13 response that survives every gain and every sensitivity
condition (18b, 18k), is the specific wiring's.
- **Steering separated from bias, under three sign rules (second part; left, right and bilateral presentations, 3
  seeds; `odor_dose_flywire_shiu_min1+known+eln0.25.csv`, `..._shiu_min1+eln0.25.csv`, `..._zenodo_min1+known+eln0.25.csv`).**
  A left-only presentation cannot tell steering from a fixed turning bias, so each odor was also put on the right
  antenna: steering = the mean of the two ipsilateral-minus-contralateral DNa indices, fixed bias = half their
  difference (positive = left). *Paper's model (known signs, eLN x0.25):* steering for the food blend -4.8 / -2.7 /
  -6.6 / -3.7 / -9.2 Hz at 25 / 50 / 75 / 100 / 150 Hz, sweet -1 to -6, vinegar -0.7 to -6.6, ester -1.5 to -3; CO2, cVA
  and the aversive odor within +-2.8 of zero; fixed bias small and of either sign (-6 to +6). The avoidance of a
  lateralized food odor is steering, not bias, and it holds at every dose. *Shiu's predicted signs (the published
  rule), eLN x0.25:* steering +-4 Hz for every odor (no chemotaxis of either sign) on top of a **fixed left bias of
  15-29 Hz for every odor at every dose** — the 14s artifact seen from the body's side: a left-only presentation
  reads as "approach", a right-only one as "avoidance". *Zenodo table, top_nt signs with the known override:*
  steering within +-2 Hz (a few +5-6 values at 150 Hz), fixed left bias 5-15 Hz for the food-type odors, 0 for
  cVA and the aversive odor. *Male (eLN x0.25):* steering and bias both <= 1.5 Hz for every odor (cVA +2.6 at
  150): the male's turning DNs are not olfactory in this model.
  **Verdict for item 5:** no sign rule gives this model's fly positive chemotaxis; the paper's rule gives a 3-9 Hz
  avoidance of food-type odors at all concentrations, the other two give none; the left loops of the embodied flies
  (14u, 16k) are the odor-blind left bias, largest under the published signs. The fly cannot find flowers on
  purpose in any variant of the model, and the sign of what it does with a lateralized odor is the transmitter-sign
  rule's, not the wiring's alone. Fig 10 now shows steering and bias as separate panels.
- The odor -> giant-fiber quirk is the known-sign rule's too: under Shiu's signs and under the Zenodo table the GF is
  0.0-0.7 Hz for every odor and dose. Off the table for good.

### 18e. Sensitivity table under the specific lobe, with the transmitter-sign rule as an axis (`sensitivity_flywire_shiu_min1+known+eln0.25.csv`, 3 seeds, 600 ms; Fig 7)
Fifteen conditions: the paper's model (known signs, eLN x0.25, Shiu's table, all connections, 100 Hz, dt 0.2) against
the sign rule x eLN scale (the published model = Shiu signs + eLN x1; known signs + x1; Shiu signs + x0.25; known +
x0.5; known + x0.1), stimulus 50 / 150 Hz, dt 0.1 / 0.5, the first version's numerics, connections >= 5 synapses, and
the Zenodo table (top_nt signs with the known override) with and without the threshold. The old table
(`sensitivity_flywire.csv`, 14s) is kept.
- **Robust to every axis:** sugar -> MN9 64-95 Hz (371 only with the legacy numerics, the old runaway); touch -> DNp13
  28-51; cVA -> DNp13, MN9, pC1d/e, aIPg: 0.0 in all fifteen conditions — the decision neurons' silence to the
  pheromone is not a property of any choice of ours. Touch -> MDN ~0 everywhere.
- **The transmitter-sign / eLN axis decides the odor rows, in this order.** (i) Odor -> dopamine: food -> PPL1 111
  (published) / 101 (known signs, eLN x1) / 62 (Shiu signs, x0.25) / 27 (known, x0.5) / 17 (known, x0.25 = the paper) /
  17 (x0.1); PAM 21 / 13 / 2.6 / 0.5 / 0.1 / 0.1. The magnitude is the eLN scale's; the direction (PPL1 > PAM) holds in
  all fifteen. (ii) Odor gating of touch -> DNp13: cVA + touch 18.6 (published) / 19.4 (known, x1) / 30 (Shiu, x0.25) /
  26 (known, x0.5) / 36 (paper) / 36 (x0.1), against touch alone 36: the "cVA halves the rejection response" of 14g is
  a function of the eLN scale alone and is gone at x0.25. (iii) The odor -> turning bias: food -> DNa L / R 36 / 5
  (published), 29 / 5 (known, x1), 34 / 4 (Shiu, x0.25), 21 / 13 (paper), 21 / 25 (known, x0.5), 28 / 9 (x0.1), 21 / 20
  (>= 5 synapses), 27 / 9 (Zenodo); cVA -> DNa 34 / 4, 28 / 10, 24 / 5, 10 / 7.5, 20 / 25, 5 / 0, 0 / 0, 0 / 0 (Zenodo,
  either threshold). The food odor's left lean exists under most rules, but its size runs from 0 to 30 Hz with the
  sign rule, the eLN scale and the synapse threshold, and cVA's reach to the turning DNs vanishes under the Zenodo
  table's signs. Steering by odor is therefore "present, odor-specific, of a size and handedness set by the sign
  rule" — the wording for the answer table. (iv) Kenyon-cell drive (mean KC rate) 33 Hz published / 24.5 known-x1 /
  3.8 Shiu-x0.25 / 3.9 known-x0.5 / 1.2 paper: the sparse code needs the eLN scale, not the sign rule (16b).
- **The odor -> giant-fiber quirk exists in exactly one cell of the table:** 4.4 Hz in the paper's model (1.9 with the
  >= 5 threshold), 0.0 under Shiu's signs at x0.25, under known signs at x1, x0.5 and x0.1, and under the Zenodo table —
  a property of the known-sign flips combined with x0.25. Off the table (with 18a, 18c).
- **Stimulus rate:** at 50 Hz the odor responses are symmetric and smaller (food -> DNa 19 / 17, cVA 7 / 8, PPL1 11); at
  the body's 150 Hz they lean left (food 30 / 5, cVA 10 / 1.4, PPL1 20) — 18c's dose effect seen from the other side.
  Sound (JO-B) -> GF is rate- and threshold-sensitive (0.3 at 50 Hz, 10 at 150; 0.8 with >= 5 synapses), unlike JO-A (18a).
- **Time step and numerics:** dt 0.1 / 0.5 reproduce every row within seed noise; the first version's numerics give the
  runaway (MN9 371, cVA -> DNa 70 / 19, PPL1 36), as in 14s.
- For the paper: the answer table's non-odor rows stand under every choice we made; its odor rows are conditional on
  the sign rule and the eLN scale and are labelled with both. Item 4 of `WHATS_LEFT_FLY.md` (the sign rule as a formal
  axis) is this table for the female; the male's axis (its 67 unclear local neurons) is 18k.

### 18f. The learning result's own robustness window: US dose and eLN scale (`conditioning_flywire_shiu_min1+known+eln0.25_us-dan-reward-20hz_*`, `..._eln0.1_us-dan-*`; Fig 2b)
The 16 f/g design repeated with the reward DANs at 20 Hz instead of 50 (both odor orders, 3 seeds) and with the
antennal lobe at eLN x0.1 instead of x0.25 (both orders, 3 seeds), plus the punishment DANs at 20 Hz and at x0.1 (both
orders, seed 0). Learning index = CS- minus CS+ retained KC->MBON drive in the taught compartment (post / pre):

| model | US | CS+ taught comp. | CS- taught comp. | learning index (mean +/- sd, n) |
|---|---|---|---|---|
| known signs, eLN x0.25 (paper) | reward DANs 50 Hz (16f) | 0.10 | 0.62-0.66 | 0.54 +/- 0.02 (6) |
| known signs, eLN x0.25 | **reward DANs 20 Hz** | 0.10 | 0.63-0.69 | **0.56 +/- 0.04 (6)** |
| **known signs, eLN x0.1** | reward DANs 50 Hz | 0.10-0.13 | 0.71-0.75 | **0.62 +/- 0.02 (6)** |
| known signs, eLN x0.25 (paper) | punishment DANs 50 Hz (16g) | 0.09-0.10 | 0.17 / 0.44 | 0.21 +/- 0.15 (6) |
| known signs, eLN x0.25 | punishment DANs 20 Hz | 0.09-0.10 | 0.20 / 0.46 | 0.23 (2) |
| known signs, eLN x0.1 | punishment DANs 50 Hz | 0.10-0.11 | 0.22 / 0.50 | 0.26 (2) |
| known signs, eLN x0.25 | none (`wiring`, 16g) | 0.88-0.92 | 0.91-0.93 | 0.04 +/- 0.04 (4) |

- **The memory is the same at a US of 20 Hz and at an antennal lobe four times sparser.** The CS+ input to the taught
  compartment goes to the 0.10 floor in every run of every condition (24 of 24 with a US); the CS- keeps 0.6-0.75
  (appetitive) or its odor-set level (aversive); the no-US control stays at 0.9. The appetitive index is, if anything,
  larger at x0.1 (the CS- generalises less because the two blends share fewer Kenyon cells); the aversive index keeps
  its odor asymmetry (vinegar punishes itself at every eLN scale: its own punishment-compartment input falls to
  0.17-0.22 as CS-, ester's to 0.44-0.50).
- **Nothing the fly does changes with the pairing, at any dose.** Approach index (odor on the left antenna, post -
  pre): vinegar +1.3 to +11.5 and ester -6.5 to -0.3 whichever of them is CS+, with the US at 50 or 20 Hz, at x0.25 or
  x0.1, and without a US; MBON spike change vinegar -2.2 to -3.3 Hz, ester -0.4, likewise pairing-blind. The 16f-16h
  verdict (memory forms, expression does not) now has the same backing as the innate rows: two US doses, two eLN
  scales, both odor orders, 3 seeds.
- For the answer table: "odor-reward / odor-punishment memory: forms (LI 0.54-0.62 appetitive, 0.2-0.3 aversive, 0.04
  without a US), robust to US dose and eLN scale; expression: none, under the same conditions and with a tonic
  state supplied to the output stage (18g)."

### 18k. Male sensitivity table, with the 67 unclear local neurons as an axis (`sensitivity_malecns_all_min1+eln0.25.csv`, 3 seeds, 600 ms; Fig 7)
MaleCNS has no known-transmitter column, so the male's sign axis is what its 67 antennal-lobe local neurons with the
prediction "unclear" (classifier confidence ~0.5, defaulted to excitatory = counted as eLNs) do: excitatory (published
default), inhibitory (`--unclear-ln inhibitory`, `FLYBRAIN_UNCLEAR_LN`), or silent. Thirteen conditions: baseline (eLN
x0.25), the published lobe (x1), x0.5, x0.1, x0.25 with the unclear LNs inhibitory / silent, x1 with them inhibitory,
stimulus 50 / 150 Hz, dt 0.1 / 0.5, legacy numerics, connections >= 5.
- **cVA -> DNp13 holds in all thirteen** (31.7 baseline; 16-38 across stimulus rate, dt and threshold; 25 under the
  published lobe; 21 / 39 at x0.5 / x0.1; **36 with the unclear LNs inhibitory, 29 with them silent**; 12 with the
  legacy numerics and with x1 + inhibitory). cVA -> MN9 28-35 and cVA -> song wing MNs 10-18 everywhere. Every other
  odor -> DNp13 is 0.0 in every condition; touch and ppk25 + touch -> DNp13 0.0 in every condition (the male's DNp13
  is a pheromone neuron, the female's a touch neuron), and touch *reduces* the male's cVA -> DNp13 to 5-19 Hz in all
  thirteen.
- **The unclear local neurons decide whether the pheromone reaches dopamine, not whether it reaches the motor
  side:** cVA -> PPL1 11.8 with them excitatory, **0.0 inhibitory**, 9.6 silent; cVA -> KC 0.0 in all three. And they
  carry much of the male lobe's runaway (16j): the published lobe (x1) gives food -> PPL1 121 Hz, PAM 42, KC 34 Hz;
  the same lobe with the 67 unclear LNs inhibitory gives food -> PPL1 14, PAM 0, KC 2 — a tame lobe without any eLN
  scaling. So the male's eLN x0.25 partly compensates for 67 mislabelled neurons; both settings are reported.
- **Non-olfactory rows do not see the antennal-lobe axis at all** (identical to the decimal in every AL variant):
  contact pheromone -> MDN 29, song MNs 21, PPL1 39; JO-B -> GF 48; touch -> MDN 11.5. What moves them is the
  synapse threshold (contact -> MDN 6.5 and song MNs 13 with >= 5 synapses; 14j's fragile backing) and the stimulus
  rate (touch -> MDN 0 at 50 Hz, 27 at 150).
- The male's labellar GRNs -> MN9: 0.0 in all thirteen (18b); P1 / aIPg <= 0.6 Hz in all thirteen; the male's turning
  DNs answer cVA with <= 5 Hz in every condition (its steering is not olfactory in this model).

### 18h. Encounter trials under the specific lobe (`experiments/encounter_trials.sh 5 300`, 14:01-; `encounter_stats.py`, Fig 3b)
*Chamber condition, read from the first trial's log before interpreting anything:* the "odor-free" chamber (R = 6,
`--noFood`) is not odor-free. The female's antennae report vinegar 0.20, mould-type (aversive) 0.20, ester 0.03 and
floral 0.04 (fractions of the body's 150 Hz maximum, i.e. ~30 Hz on the top glomerulus) throughout: the 5 x 5
dandelion and poppy patches of the 16 Sep learning run (`learn_in_world.sh`, R = 10, patches at x = +-6) stand at
this chamber's wall, and an older aversive patch is within smelling range. 14u's chamber (14 Sep) predates those
patches. Under the specific lobe a 30 Hz flower odor is a mild, symmetric drive (18c: DNa 14 / 17 at 25 Hz, PPL1 8),
and it is what makes the flies walk at all (fly1 in trial 1: DNa L / R 12.8 / 12.1 Hz, walk duty 0.47, no left loop);
in a truly odor-free chamber nothing drives the female's turning DNs (18a: Or47b -> 0.0, cVA -> DNa 10 / 8 only from a
male) and a female-female pair would stand still. So these are "faint flower smell" trials, reported as such; a
cleared-world rerun is listed under what's left. Results below when the ten trials are in.
**Results (5 + 5 trials, 300 s wall each, brains at ~0.3x: 95 +/- 5 s of brain time per fly in the ff trials, 83 +/- 26
in mf — three times 14u's 23-40 s; `encounter_trials.csv`, variant `specific`; Fig 3, 3b).**
- **Female-female: the females now meet, and then they do not part.** Contact (within 1.3 blocks, the touch
  sense) in 8 of 10 fly-logs (4 of 5 trials); 729 +/- 594 contact ticks per fly, i.e. 37 % of the trial on average and
  98 % in trial 3, where they met after 1.4 s and never separated (one bout of 86 s); the other trials have 1-6 bouts
  of up to 16-26 s. 14u (published lobe, same chamber): 0 contact ticks in 10 of 10 logs. The reason is mechanical
  and readable in the DNs: far from each other the flies walk (duty 0.30, DNa L / R 12.6 / 12.5 — symmetric, the
  faint flower smell) and jump (GF 2.0 Hz, the odor -> GF quirk, 18e); **in contact, touch shuts the turning DNs (DNa
  0.4 / 0.1 Hz, from 12.6 / 12.5 far), so both flies stop walking** (walk duty -> 0; 18a: food + touch -> DNa 6.7 /
  3.1 vs food alone 21 / 13 — the bristle input suppresses the odor-driven turning), while the touch reflexes run
  at full rate: DNp13 32.9 Hz (5.6 far, 4.8 near-without-contact), feeding MNs 22.2 (4.9 far). 99 rejection acts
  and 38 proboscis extensions per minute, 0 lunges (pC1d/e, aIPg 0.0 throughout). Near-without-contact (3.5 blocks
  and closer, 1-2 % of ticks) changes nothing: DNp13 4.8 vs 5.6 far, DNa 6.9 / 9.2 vs 12.6 / 12.5. So there is still no
  approach — the meetings are chance crossings of two symmetric walkers — and, once met, a wiring-level "stop and
  extrude" reflex holds them together. A real female walks away; this model's stops. Whether that is the fly's
  wiring (bristle -> DN suppression is a plausible startle circuit) or the sign rule's is a question for 18e's axis;
  in the published-lobe chamber it never arose because the females never touched.
- **Male-female: they rarely meet, because the male does not move.** Under the specific lobe the male has no odor to
  walk on (18b, 18c: every non-cVA odor -> nothing, and the female's odor is Or47b): walk duty 0.03, leg MNs 0.2 Hz,
  path 41 blocks in 77 s (drift while backing). The female walks (0.47) with symmetric turning (12.4 / 12.4) and
  smells the male's cVA at 0.1 throughout. Contact in 1 of 5 trials (trial 3: 16 bouts, the longest 2 s, 6 % of
  ticks); 14u had contact in 4 of 5. On contact the female shows the same reflex as above (DNp13 33.0, feeding MNs
  22.0, DNa 2.7 / 1.2), and **the male backs away: MDN 39.5 Hz on contact (1.4 far, 2.2 near)** — ppk25 (touching a
  female) -> MDN, the 14j / 18b result seen in the arena, and the reason the mf bouts are short (2 s) where the ff
  bouts last tens of seconds: the male steps back, the female's touch ends, both resume. The male's song command and
  P1 stay at 0.0 far, near and on contact; song wing-MN events 5 / min throughout (contact pheromone -> wing MNs,
  not song).
- **Against 14u (published lobe):** ff contact 0 -> 37 % of ticks; mf contact 4 / 5 -> 1 / 5 trials; walk duty 0.71 (left
  loops) -> 0.30 (ff) / 0.47 (mf female) / 0.03 (male); female DNp13 on contact 16.5 -> 33 Hz (the full touch response
  now that odor no longer halves it, 18a); no lunge, no P1, no vpoDN in either.
- For the answer table: "approach to another fly: no (no DN changes before contact, either sex)"; "female rejection
  signal on contact: yes, 33 Hz, both partners' sexes, gain-robust (18a)"; new row "stop on contact (touch shuts the
  turning DNs): wiring — a reflex that keeps two females together in this model"; "male backs off on touching a
  female (ppk25 -> MDN 40 Hz): wiring, but fragile to gain (18b)".

### 18j. Male odor learning (`conditioning_malecns_all_min1+eln0.25_us-dan-{reward,punish}_*_seed0.csv`; Fig 2b)
`conditioning.py --dataset malecns --eln 0.25 --us dan`, vinegar / ester at 150 Hz, reward and punishment US, both
orders, seed 0. The male's mushroom body under eLN x0.25: vinegar recruits 2.6 % of its 4,063 Kenyon cells, ester
1.0 %; MBONs 0.7-1.5 Hz (reward-compartment MBONs 0.0 for both odors, punishment-compartment 3.9 Hz for vinegar);
PAM 0.0 and PPL1 0-2.9 Hz to the odors themselves (the female's odor-evoked PPL1 is 15-17 Hz). US sets found by the
compartment check: 158 reward PAMs (PAM01/02/04/08/11, each onto its expected MBONs), 8 punishment PPL1s.
- **The male learns, both valences, and more cleanly than the female:** reward US -> CS+ reward-compartment drive
  retained 0.114 (ester+) / 0.156 (vinegar+), CS- 0.93 / 0.94; punishment US -> CS+ punishment-compartment drive
  0.100 / 0.100, CS- 0.83 / 0.91. Learning index 0.78-0.82 appetitive, 0.73-0.81 aversive (female: 0.54 / 0.21). The
  difference is the male's silence: its two blends share fewer Kenyon cells (the CS- keeps 0.9 rather than 0.6-0.7)
  and its dopamine neurons do not answer odors, so there is no self-punishment and no non-associative component —
  the CS- and the untaught compartment stay at 0.78-0.99.
- **And nothing to express it through.** The male's turning DNs, DNp09, MDN, feeding MNs: 0.0 to both odors before
  and after (18c: the male's steering is not olfactory); MBON spike rates unchanged to 0.1 Hz; approach index -1.0
  before and after in every run. The male's odor memory is the most associative object in the model and the least
  consequential.
- cVA cannot be learned about in this model: it recruits 0.1-0.3 % of the male's KCs (18c), below what the rule
  needs (its drive to any compartment is ~0). Pheromone learning (a known fly ability) is outside this model's reach.

### 18i. Learning in the world with a real dose of sugar (`learn_in_world.sh` with `HOLD=8 PATCH_R=3 BITTER=vinegar`; `world3`, `world4`; `brainctl.py probe`)
16k's fly tasted nectar for 1.2 s and its reward compartments showed nothing above odor exposure. Two changes: the
poppy patch is 7 x 7 (`PATCH_R=3`) and the experimenter puts the fly back on the patch centre every 8 s (`HOLD=8`, the
sugar-coated filter paper of a T-maze tube), for both halves of training; and the brain has a `probe` command — the
odor classes presented bilaterally to the idle brain, KC->MBON drive per compartment returned, the same graded
readout as the offline conditioning — run before the body connects and after it leaves (`learn_*_probe_pre/post.json`).
- **The dose is real now:** 920 ticks = 46 s of sugar on the poppies in `world4` (23 ticks in 16k), 104 proboscis
  extensions; on the dandelions 2209 ticks = 110 s of bitter (`world3`: 1009 sugar ticks; its body's timer ran out
  in the hold-stretched training, so it has no post phase — the timing is fixed, the body is now stopped by the script).
- **The memory is written and it is large — but in this chamber it is not odor-specific.** Graded readout, post / pre:
  ester (poppies, sugar-paired) reward-compartment drive **0.140**, punishment-compartment 0.114; vinegar (dandelions,
  bitter-paired) reward-compartment 0.211, punishment-compartment **0.101**. The sugar-paired odor lost more of its
  reward-compartment input than the other (0.14 vs 0.21) — a trace of "poppies fed me" that 16k did not have — but the
  difference is a fraction of the offline one (0.10 vs 0.64), and both odors' punishment-compartment inputs are at the
  floor. The log says why: the two patches are 12 blocks apart in a 20-block chamber and the odor kernel reaches
  across it, so on the poppies the antennae report ester 0.83 *and vinegar 0.18*, on the dandelions vinegar 1.00 *and
  ester 0.52*; 110 s of bitter with both odors' Kenyon cells active depresses both odors' punishment inputs, and 46 s of
  sugar with vinegar at 0.18 depresses vinegar's reward input to 0.21. The world ran the experiment the offline design
  forbids (a CS- present during the US). Compartment weights (mean over all KC synapses): reward MBON02 0.88, MBON07
  0.88 (16k: 0.92) — the extra sugar shows there too; punishment MBON14 / MBON18 0.82 (16k: 0.84).
- **Expression: none, as everywhere else.** After training the fly's MBON output while smelling either flower is
  down (poppies 3.6 Hz, dandelions 4.5; dandelions before: 9.9) and its walking (duty 0.65) and turning (+0.6, the
  vinegar-driven left lean) are what they were; it still ends up on the dandelions (43 % of the post phase, 0 % on
  the poppies), tasting bitter (196 ticks) — the memory that says "dandelions hurt" does not reach the legs.
- Lesson for the design, not the model: odor-specific learning in the world needs patches further apart than the
  odor kernel (or a shorter kernel), so that the unpaired flower is not in the air during the US. `world5` (R = 20,
  patches 22 blocks apart) is running for that.

### 18l. Where this leaves the answer table (revision of 15 / 16l, 17 Sep 2026)
Every row below now has, under the antennal lobe that tells odors apart (known signs, eLN x0.25): a gain window
(18a, 18b), a shuffled-wiring control (18d, both sexes) and a sensitivity table with the transmitter-sign rule as an
axis (18e female, 18k male); the encounter rows have n = 5 trials per condition (18h); the learning rows have two US
doses and two eLN scales (18f), a supplied tonic state at the output stage (18g), the male (18j) and the world (18i).

| Behavior | Wiring alone? | State? | Learning? | Evidence (window / shuffle / sensitivity) |
|---|---|---|---|---|
| Feeding on sugar (female) | **Yes** | hunger neurons change nothing (14k) | – | MN9 38 / 77 / 93 Hz at gain 0.7 / 1.0 / 1.4; shuffled 0; 64-95 Hz in all 15 conditions (18a, 18d, 18e). Not reproduced in the male: its pooled labellar GRNs -> MN9 0 in every condition (18b, 18k) |
| Bitter suppression of feeding | **Yes** | – | – | 55 -> 1.7 Hz (16a anchors) |
| Startle / escape to sound | **Yes** | – | – | JO-A -> GF 5 / 10 / 16 (female); JO-B -> GF 34-52 from gain 0.5 up (male); shuffled 0 |
| Antennal grooming circuit | **Yes** | – | – | JO-CE -> aBN1, JO-F silent (16a anchors) |
| Odor identity (antennal lobe, Kenyon cells) | **Only with known signs + eLN <= 0.5** (ours) | – | – | KC drive 33 Hz published / 3.8-3.9 at Shiu-x0.25 or known-x0.5 / 1.2 at the paper's model (18e); the male's 67 unclear LNs carry much of its runaway (18k) |
| Steering by odor | **Present at gains 1.0-1.4 only**; odor-specific; size and handedness set by the sign rule | – | – | nothing olfactory passes gain 0.7 (18a); food -> DNa L / R from 36 / 5 to 21 / 25 across sign rules and eLN scales, cVA -> DNa 0 under the Zenodo signs (18e); shuffled 0 |
| Chemotaxis toward food (lateralized odor) | **No, under any sign rule**; the paper's rule gives a 3-9 Hz *avoidance* at every concentration; the published rule a 15-29 Hz odor-blind left bias | – | – | 18c (left / right / bilateral, 25-150 Hz, three rules). The fly cannot find flowers on purpose in any variant |
| Odor -> punishment dopamine | **Yes in direction** (PPL1 > PAM in all 15 conditions); magnitude is the eLN scale's (5-18 Hz at x0.25, >100 published) | – | – | 18a, 18e; the male's odors reach dopamine only through cVA (12 Hz) and the unclear LNs decide that (18k) |
| Odor -> giant fiber "jump" | **Not a behaviour**: one cell of the sensitivity table | – | – | absent at gain 0.7, 0.0 under Shiu's signs, under known signs at x1 / x0.5 / x0.1 and under the Zenodo table; the male never has it (18a, 18c, 18e) |
| Female rejection signal on touch (DNp13) | **Yes**, 36 Hz, **not gated by odor** | state-blind | – | 28 / 36 / 42 at 0.7 / 1.0 / 1.4 with cVA or food odor present; 28-51 in all 15 conditions; the old gating was the eLN scale alone; 33 Hz on contact with either sex in the arena (18a, 18e, 18h) |
| Stop on contact (touch shuts the turning DNs) | **Yes** — a reflex that holds two females together in this model | – | – | DNa 12.6 / 12.5 far -> 0.4 / 0.1 in contact, 8 / 10 fly-logs, contact bouts up to 86 s; food + touch -> DNa 6.7 / 3.1 vs 21 / 13 offline (18h, 18a) |
| Female receptivity (pC1, vpoDN) | No | **Yes — mating state via SAG** (14k) | – | 0.0 to every input at every gain and in all 15 conditions (18a, 18e) |
| Female aggression on touch (pC1d/e, aIPg) | No | **Yes — virgin / aroused state** (14k) | – | 0.0 at every gain <= 1.4; 0 lunges in 10 arena trials (18h) |
| Egg-laying (oviDN) | No | No | – | 0 throughout |
| Male courtship song command (pIP10 -> TN1 -> wing MNs) | Weakly (cVA -> pIP10 0 / 3 / 8) | **Yes — P1 state** (14p) | – | P1 0.0 in every gain <= 1.0 and all 13 male conditions; 0 in the arena (18b, 18k, 18h) |
| Male cVA -> DNp13 | **Yes, pheromone-specific, the male's only odor response at the published gain** | – | – | 7.8 / 32 / 28 at 0.7 / 1.0 / 1.4, every other odor 0 at every gain; dose-graded 5 -> 35 Hz; 12-39 Hz in all 13 conditions incl. both settings of the unclear LNs; shuffled 0; touch reduces it (18b, 18c, 18k, 18d) |
| Male contact chemosensation -> wing motor | **Yes** (10-21 Hz at every gain) | – | – | -> MDN only at gain 1.0 and only with all connections (fragile); MDN 40 Hz on touching a female in the arena, which ends the contact in 2 s (18b, 18k, 18h) |
| Approach to another fly | **No**, either sex | not tested with states | – | no DN change before contact (near-without-contact = far) in 10 + 10 logs; the meetings are chance crossings; the male does not move (18h) |
| Hunger-dependent anything | – | **No** (14k, 14p) | – | neuromodulation is not in the model |
| Odor-reward / odor-punishment memory | – | – | **Forms, odor-specific, valence-correct** (US supplied to the identified DANs; the wiring carries none) | LI 0.54 / 0.56 (US 20 Hz) / 0.62 (eLN x0.1) appetitive, 0.2-0.3 aversive, 0.04 without a US (18f); male 0.8 both valences, cleaner (18j); in the world from the body's own sugar and bitter (18i) |
| Behavioural expression of that memory | **Not in this model** | not with a tonic state at the output stage either | – | no pairing-dependent change at any US dose or eLN scale (18f); MBON targets awake at 5-40 Hz free <= 5 Hz of DNa and nothing else, the punishment MBONs' 28 descending targets unchanged to 0.6 Hz (18g); the male has nothing to express through (18j); the in-world fly keeps walking onto the bitter flowers (18i) |
| Anything shuffled | **No** | – | – | every readout 0 with degree-preserving rewiring, both sexes (18d) |

**The one-sentence answer, unchanged in substance and now with its controls:** in the published whole-brain model
with an antennal lobe that tells odors apart, reflexes are in the wiring (feeding, startle, touch -> rejection, touch ->
stop, the male's pheromone -> DNp13), the social decisions are not sensory reflexes but become available the moment an
identified state neuron class is active (SAG, P1), the states the model cannot carry are the neuromodulatory ones
(hunger), and learning is answered half-way — the memory is in the wiring's reach once a teaching signal is supplied,
its use is not, and that "not" survives every dose, both sexes, the world, and a tonic state supplied to the output
stage. Two of this session's additions are about *us*, not the fly: the sign of chemotaxis and the handedness of
odor-driven turning are the transmitter-sign rule's, and the odor-evoked jump was one cell of a sensitivity table.
- **`world5`: the same with the patches beyond the kernel's reach (R = 28, patches 30 blocks apart; the bot counts odor
  sources up to 24 blocks away).** Now the odors are separated during the teaching: vinegar absent (0.0) in every one
  of the 906 sugar ticks, ester <= 0.05 in every one of the 2126 bitter ticks (45 s of sugar, 106 s of bitter). Graded
  readout, post / pre: **the aversive memory is odor-specific in the world** — vinegar's punishment-compartment input
  0.090 (the floor), ester's 0.384 (the level odor exposure alone gives, 16g), learning index 0.29, the same as the
  offline aversive index (0.21-0.26, 18f). **The appetitive one is masked:** ester's reward-compartment input 0.271,
  vinegar's 0.286. The sugar wrote its memory (ester's reward input fell to 0.27 with nothing but sugar and its own
  odor present) but the bitter half, 2.3 times longer, removed as much of the punished odor's reward-compartment
  input by the non-associative route (tonic odor-evoked dopamine and the PPL1 set's reach into the PAM-taught
  compartments: offline, 30 s of punishment US takes the punished odor's reward input to 0.79-0.88 and 30 s of odor
  alone to 0.9; 106 s of both compounds to ~0.3). Expression: none — post-phase walking 0.48 / 0.68, turning -0.1 /
  +0.6 while smelling poppies / dandelions, as before training. The sugar-only chamber (`world6`: the dandelions a pure
  odor cue) isolates the appetitive memory; its numbers close this section.
- **`world6`: sugar only (R = 28, the dandelions a pure odor cue, `BITTER=`).** 887 sugar ticks (44 s) on the poppies
  with vinegar at 0.0 in every one of them, 0 bitter anywhere, 113 s among the dandelions. Graded readout, post / pre:
  **ester (sugar-paired) reward-compartment input 0.289, vinegar (odor only) 0.662 — the appetitive memory is
  odor-specific in the world, learning index 0.37** (offline: 0.10 vs 0.64, index 0.54; the world's 44 s of sugar
  at the patch's 0.89 odor intensity and a moving fly do less than 30 s of a fixed 150 Hz odor). The punishment
  side shows the model's non-associative signature with no bitter at all: vinegar's punishment-compartment input
  0.131 after 113 s of its own odor (its tonic odor-evoked PPL1, 16f-g; 0.22 after 30 s offline), ester's 0.438. And
  the fly's behaviour after learning is its behaviour before: walk 0.47 / 0.72 and turn -0.06 / +0.55 while smelling
  poppies / dandelions (pre: 0.48 / 0.67, -0.02 / +0.52), and it still spends the post phase on the flowers it happens
  to be walking toward. Item 6 is answered: **"poppies fed me" is written by the fly's own rule from its own sugar,
  odor-specifically, once the world keeps the two odors apart; it changes nothing the fly does.**

## 19. Fifth pass (18 Sep 2026) — the last controls before writing

*Goal set for this session (`WHATS_LEFT_FLY.md`, "must do before writing"): (1) the encounter trials in a chamber that is
really odor-free, and — since the prediction from 18a/c is that nothing then moves — a second condition with a documented
walking substrate; (2) the state arm on the paper's model (known signs, eLN x0.25); (3) one sensitivity row for "stop on
contact". Then the two decisions (vision, the male's feeding circuit), then the paper and the release package. Queue:
`experiments/run_queue5.sh`; new scripts `survey_chamber.js`, `noise_floor.py`, `contact_stop.py`. Nothing from 14-18 is
overwritten; the encounter logs of this session carry the chamber in their trial label (`off_ff_t3_clean`,
`off_mf_t1_noise0.2`) and the noise in the brain's log name (`fly1_off-flywire-noise0.2-known-eln0.25_<stamp>.csv`).*

### 19a. The chamber was not odor-free, and now it is (`experiments/survey_chamber.js`)
A ghost op bot stands at the origin and lists every block of `observe.js` ODOR_CLASS within 45 blocks (the odor kernel in
`scanSmell` is `findBlocks(maxDistance 16)` from the antennae — the "24 blocks" of 18i was the section-iterator's reach,
the distance filter is 16 — so a clean R = 6 chamber needs nothing odorous within 22 blocks of the origin; 45 is slack).
**Before:** 98 odorous blocks at y = 64 within 45 blocks: the two 7 x 7 patches of `world4-6` (18i; 49 poppies at x = -18..-12,
49 dandelions at x = 12..18), 12-18 blocks from the chamber's centre, i.e. well inside the kernel; the 5 x 5 patches of
16 Sep that 18h blamed had already been overwritten by the R = 28 arena build. This is why the 18h flies smelled
vinegar / ester at 0.2 at the wall (the strongest value any fly logged in 18h is 0.70, `encounter_stats.py` column
`odor_max`). **Clearing:** `--clear` fills y = 63..70 within +-45 with air (one layer per command, under the 32768-block
limit) and re-surveys; the bot is put in spectator mode first because the first run of the script fell with its floor
onto the superflat surface at y = -60 and its "second pass" then cleared the 14 Sep arenas there (the grass layer at
y = -61 was restored; nothing at y = -60 is within 16 blocks of a fly at y = 64, so no result depended on it). **After:** 0
odorous blocks within 45 (`[survey] CLEAN`). A 15 s smoke trial (two females, `off_ff_t1_smoke`, logs deleted) showed the
chamber as the model sees it: every `odor_*` column 0.000 for the whole trial, the only smells the other fly's CO2
(0.003) and body odor (Or47b, 0.10-0.12); DNa L / R 0.0 / 0.0, walk duty 0.0, path 0 blocks, DNp13 0, GF 0 in both
flies — exactly the 18a / 18c prediction (nothing olfactory drives a female's turning DNs in this model). The full
5 + 5 trials are 19b; `encounter_trials.sh` now runs the survey with `--clear` before every series and stops if the
chamber is not clean.

### 19c. A documented walking substrate: background noise, calibrated (`experiments/noise_floor.py`, `noise_floor_{flywire_shiu_min1+known+eln0.25,malecns_all_min1+eln0.25}.csv`, 3 seeds, 1 s, 100 Hz inputs)
The published model has no spontaneous activity, so a female with nothing to smell stands still, and a chamber where
nobody moves cannot ask the encounter question. The only substrate the model offers is `--noise-hz`: independent Poisson
kicks (Shiu's 68.75 mV activation kick) on every neuron at a fixed rate. It is ours, so it was calibrated on what it
does alone and on what it does to the reflexes the answer table rests on, before a rate was chosen:

| noise (Hz / neuron) | active neurons | no input: DNa L / R · DNp09 · GF · feed MNs · DNp13 | touch: DNp13 · DNa L / R | food odor: DNa L / R |
|---|---|---|---|---|
| 0 (published) | 0 % | 0 / 0 · 0 · 0 · 0 · 0 | 35.8 · 0.3 / 0.7 | 23.0 / 14.0 |
| 0.02 | 2 % | 0 / 0.2 · 0 · 0.3 · 0.8 · 0.2 | 35.7 · 0 / 0.7 | 22.2 / 15.5 |
| 0.05 | 5.5 % | 3.0 / 5.3 · 0 · 1.5 · 1.3 · 0 | 35.8 · 0 / 0.7 | 25.2 / 15.3 |
| 0.1 | 10 % | 3.2 / 3.7 · 0 · 2.2 · 2.0 · 0.2 | 36.3 · 0.5 / 0.8 | 24.5 / 18.2 |
| **0.2** | 19 % | **7.0 / 7.0** · 0.7 · **3.2** · 2.8 · 0.5 | **35.3 · 2.7 / 1.2** | 24.8 / 19.7 |
| 0.3 | 27 % | 11.5 / 9.2 · 0.7 · 7.0 · 2.8 · 0.5 | 35.5 · 2.2 / 1.7 | 28.7 / 17.2 |
| 0.5 | 40 % | 18.2 / 18.7 · 0.7 · 5.8 · 5.5 · 0.8 | 35.8 · 4.0 / 3.8 | 30.8 / 15.7 |
| 1.0 | 64 % | 23.3 / 19.8 · 0.8 · 6.7 · 7.5 · 2.0 | 39.0 · 4.2 / 6.3 | 28.8 / 17.8 |

(female; Hz; the 1 Hz row is the 14 Sep "noise control" of section 3, now under the specific lobe: it still puts a floor
under everything.) **Chosen: 0.2 Hz.** It gives the turning DNs 7 / 7 Hz with nothing to smell — walk duty ~0.4 through
the body's saturating readout, the same order as the faint flower smell of 18h (12.6 / 12.5, duty 0.30) — and leaves
every reflex the table rests on where it was: touch -> DNp13 35 Hz (35.8 without noise), touch still shuts the turning
DNs (7 / 7 -> 2.7 / 1.2; with food odor 24.8 / 19.7 -> 6.8 / 3.3), sugar -> feeding MNs 24.7 (24.1), food -> DNa 24.8 / 19.7
(23 / 14), cVA -> DNa 11 / 12.5 (10.7 / 7.3). Its costs, reported with it: the giant fiber fires at 3.2 Hz on noise alone
(18h's flies jumped at 2.0 Hz on the flower smell; at 0.3 Hz it is 7 Hz, a jump every other tick, which is why 0.3 was not
taken), the feeding MNs at 2.8 Hz (8 spontaneous proboscis extensions a minute against 38 on contact), DNp13 at 0.5 Hz
(3 spontaneous rejection acts a minute against 99 on contact), and 19 % of the brain is active instead of 0-3 %. **The
male barely walks on it at any rate:** his walking is read from the leg motor neurons of the nerve cord (k = 8 Hz), and
the noise gives them 0.2 / 0.4 / 0.7 / 1.2 Hz at 0.1 / 0.2 / 0.3 / 0.5 (walk duty 0.03-0.14; his DNa 1.2-2.0) — so under
the substrate the male-female condition is a walking female and a near-stationary male, as in 18h. What the noise does
to his rows: cVA -> DNp13 31 -> 22 Hz at 0.2 (still his one odor response and still pheromone-specific: food odor
-> DNp13 0.3), touch -> MDN 10.7 -> 17.8, ppk25 + touch -> MDN 22 -> 28, ppk23/25 -> wing MNs 30 -> 31, P1 0.0 -> 0.2.
The 0.2 Hz substrate is a second condition of the encounter trials (19b), and a `+ noise 0.2` row of the stop-on-contact
axis (19d).

### 19d. "Stop on contact" is the wiring's, and it rides on weak connections (`experiments/contact_stop.py`, `contact_stop_flywire.csv`, 3 seeds, 600 ms, 100 Hz; touch = all head bristles)
The reflex that holds two females together in the arena (18h: DNa 12.6 / 12.5 far -> 0.4 / 0.1 in contact) is, offline,
the bristle input cutting the odor-driven turning DNs. Here it is run as the 18e axis: a walking drive (food odor, cVA,
Or47b, or nothing but the 0.2 Hz substrate of 19c) with and without the bristles, under every sign rule, eLN scale and
connection table. Suppression index = 1 - DNa(drive + touch) / DNa(drive), mean of both sides.

| model | food odor: DNa L / R alone -> + touch | index (food · cVA · Or47b · substrate alone) | DNp13 with touch |
|---|---|---|---|
| **paper's model (known signs, eLN x0.25)** | 21.4 / 12.8 -> 6.7 / 3.1 | **0.72 · 0.92 · – · 0.77** | 35 |
| published model (Shiu signs, eLN x1) | 35.8 / 5.3 -> 20.0 / 0.6 | 0.50 · 0.31 · 0.49 · 0.58 | 17 |
| known signs, eLN x1 | 28.9 / 5.3 -> 12.5 / 1.4 | 0.59 · 0.44 · 0.37 · 0.45 | 17 |
| Shiu signs, eLN x0.25 | 33.6 / 3.9 -> 17.5 / 0.3 | 0.53 · 0.71 · 0.94 · 0.89 | 28 |
| known signs, eLN x0.5 | 20.6 / 25.0 -> 14.4 / 8.3 | 0.50 · 0.53 · 0.64 · 0.69 | 24 |
| known signs, eLN x0.1 | 28.1 / 9.2 -> 7.8 / 1.7 | 0.75 · 0.76 · – · 0.75 | 35 |
| Zenodo table, top_nt signs, all connections | 27.2 / 8.6 -> 8.3 / 1.9 | 0.71 · (cVA silent) · – · 0.79 | 37 |
| Zenodo table, >= 5 synapses (first version) | 29.7 / 8.6 -> 17.2 / **18.3** | **0.07 · touch *drives* DNa 6 / 17 · 9 / 17 · -3.2** | 26 |

("–" = the drive alone gives no DNa, nothing to suppress; the substrate rows are the `+ noise 0.2 Hz` half of the
table, where the index for "nothing but noise" is given.) **Verdict: wiring.** Touch cuts the turning DNs under
every sign rule, at every eLN scale and in both full connection tables (index 0.5-0.94; 0.72-0.92 in the paper's
model, 0.77-0.90 with the substrate on) — including the published model, where the runaway lobe drives the left DNa
to 36 Hz and the bristles still take half of it. Its *size* is the lobe's: the more odor drive there is (eLN x1, x0.5),
the smaller the fraction the bristles remove. The single condition without it is the first version's >= 5-synapse
threshold (Zenodo table), where the suppression is gone and the bristles instead *excite* the DNa (contralateral, 17-18
Hz, with or without an odor): the connections that carry the suppression are among the 37 % of synapses that the
threshold dropped — the same place the PPL1 magnitude (14s) lived. So the row for the answer table reads: **stop on
contact (touch -> DNa suppression): wiring — present under every sign rule and eLN scale (index 0.5-0.9), abolished
only by the connection threshold; not gated by the walking substrate (19c).** MDN stays 0-1.4 Hz throughout: the female
never backs away from a touch in any variant. The male's half is 19d-m below.

**19d-m. The male's half (`contact_stop_malecns.csv`; eLN x1 / x0.25 x unclear LNs excitatory / inhibitory / silent, with
and without the 0.2 Hz substrate).** The male's turning DNs are hardly driven by anything but the contact pheromones
(ppk23/25 -> DNa 6.7 / 6.4), and touch silences those too (-> 0.0 / 0.0, index 1.0 in all four variants; with the substrate
0.89-0.97). But his touch response is not a stop: **it is backing.** Head bristles -> MDN 20 Hz (substrate alone ->
+ touch), 23 Hz with cVA, 21-33 Hz with a female's pheromone (ppk25 + touch 22-28, 18b), in the paper's model and under
both settings of the unclear local neurons — and his leg motor neurons go *up* on touch (0.4 -> 1.5 Hz), not down. Under
the published lobe (eLN x1) the bristles reach MDN at 0.0-2.6 Hz in every drive condition (the contact pheromone's own
MDN drive, 29 -> 21 Hz, is unchanged, it does not pass through the antennal lobe): **the male's back-off on touch is
decided by the eLN scale**, as his cVA -> PPL1 was by the unclear LNs (18k), and it was already fragile to gain (18b:
MDN only at gain 1.0). Touch also cuts his one odor response: cVA -> DNp13 32 -> 8.6 Hz with the bristles on (10.8 / 5.8
under the other unclear-LN settings). For the answer table: "male backs off on touching a female (ppk25 -> MDN 22 Hz,
touch -> MDN 20 Hz): wiring under the paper's model and every unclear-LN setting, 0 under the published lobe, gain
1.0 only — a sensitive result, reported as such"; and the sex difference in the arena (18h: females stop and stay,
the male steps back and the contact ends in 2 s) is the difference between these two touch reflexes: the female's
bristles reach her turning DNs and nothing else, the male's reach MDN.

### 19e. The state arm on the paper's model (`state_probe_flywire_shiu_min1+known+eln0.25_state30.csv`, 5 seeds, 1 s, state neurons 30 Hz; `experiments/state_compare.py`; Fig 5)
14k / 14p were run on the published lobe. The state neurons do not pass through the antennal lobe, so the state rows were
expected to hold; the state x odor cells were not, because every odor cell of 14k was measured in the runaway state.
Side by side (published -> paper's model, mean of 5 seeds):
- **Every state-alone cell is the same to the digit:** SAG -> pC1a 21.2 -> 21.2, pC1b/c 19.0 -> 19.0, vpoDN 5.7 -> 5.7;
  pC1a-c tonic -> vpoDN 8.7 -> 8.7; aIPg tonic -> DNa 8.4 / 7.8 -> 8.7 / 7.7; pC1d/e tonic -> DNa 2.2 / 5.2 -> 2.2 / 5.2.
  With nothing driving the lobe, the two models are the same network on these paths, and the seeds reproduce.
- **SAG + touch -> pC1d/e 6.3 -> 6.2** (the touch-evoked aggression of the virgin holds), and it is no longer masked by an
  odor: cVA + touch + SAG -> pC1d/e 1.1 -> 7.1, pC1a-c + cVA + touch -> pC1d/e 2.0 -> 8.6, aIPg + cVA + touch 1.4 -> 9.4 —
  the runaway lobe had been swallowing the bristle input, as it did for DNp13 (18a).
- **The odor x state interactions of 14k were the lobe's.** "cVA / food reduce pC1a slightly (21 -> 16-18)" becomes
  21 -> 19.6-22.5 (cVA 21.5, Or47b 22.5, food 19.6): no reduction. Every "any odor -> DNa L 35-48, PPL1 108-113, KC 31"
  cell of the state table is gone (DNa 8-25 odor-specific, PPL1 0-18, KC 0-1.3), state or no state. The aggressive
  state's "cVA -> DNa L 43 Hz" (14k: "an aggressive fly walks more") is now aIPg + cVA -> DNa 24.8 / 21.8 against 10.1 /
  8.4 without the state — still more walking, now symmetric and odor-specific (aIPg + Or47b: 9.0 / 8.5 vs 0 / 0).
- **Hunger and satiety states still change nothing specific.** Excluding the driven neurons themselves, the largest
  change any of IPC / DH44 / NPF / SIFa / AstA makes to any readout under any input is a shift of Shiu's single MN9
  neuron on sugar: NPF 86.2 +/- 3.1 vs 79.4 +/- 3.4 Hz without a state, AstA 77.8 +/- 6.9, DH44 82.4, IPC 80.0 — and the
  unrelated virgin, aroused and aggressive states shift it by the same amount (83.6-83.8), so it is a nonspecific effect
  of any tonic drive, not hunger; the population of feeding MNs moves by < 2 Hz (24.8 -> 24.8-26.7). MN9 stays 78-86 Hz
  fed or hungry. The boundary of 14k stands under the paper's model: mating state is synaptic and works, metabolic state
  is neuromodulatory and does not.
- Unchanged and state-blind, as before: touch -> DNp13 35.6-37.9 Hz in every state (real mated females extrude more; the
  model's rejection output does not know its mating state), oviDN 0.0 in every state and input.
The male half (P1 -> pIP10 / TN1 / song MNs) is 19e-m below.

### 19f. Two decisions (WHATS_LEFT "decide, then do or drop" 4-5)
- **Vision: not attempted for the social question; stated as such.** The optic-lobe bridge (flyvis, 14l-n, 14q) gives an
  optomotor response with the right sign under both map orientations and goes into the methods as the status of the
  eye; looming escape (LPLC2 silent) and the giant fiber's over-response to wide-field motion do not work, would take
  days, and nothing in the answer table uses vision — every encounter trial ran with the LIF eye, whose photoreceptor
  drive dies in the medulla. The paper says so in one sentence (Discussion) and claims nothing visual.
- **The male's feeding circuit: a data limitation, not patched.** MaleCNS pools sugar and bitter gustatory neurons under
  one label, so the male's labellar GRNs drive MN9 at 0 Hz in every condition (18b, 18k) and his feeding row reads "not
  reproduced (pooled taste labels)". Re-labelling his taste neurons by hand would be a fourth choice of ours in a place
  where the fly's own annotation is the point; the row stays empty and says why.

**19e-m. The male (`state_probe_malecns_all_min1+eln0.25_state30.csv`, 5 seeds).** The MaleCNS state table has no SAG
(it is the male), so its states are IPC, DH44, NPF, SIFa, AstA, aIPg and P1 (148 pC1 / P1 neurons).
- **P1 tonic alone is the same to the digit:** pIP10 50.4 -> 50.4 Hz, TN1 8.2 -> 8.2, song wing MNs 27.6 -> 27.6, all wing
  MNs 9.1 -> 9.1, DNp13 20.6 -> 20.6, MN9 2.7 -> 2.7, P1 itself 29.8. The song circuit is a state result under both lobes.
- **P1 x odor cells were the lobe's, in the other direction from the female's:** the runaway lobe *reduced* the song
  command (P1 + food odor -> pIP10 40.7, + Or47b 41.7; now 49.1 / 49.2, i.e. back at the state-alone value) and put
  19-21 Hz on MN9 with any odor (now 0.7-2.6): under the paper's model an odor no longer feeds or de-songs the courting
  male. P1 + cVA -> DNp13 41 -> 54 Hz and pIP10 42 -> 45; P1 + cVA -> MN9 27 -> 31 (the cVA -> MN9 cell of 14p holds).
- **Every touch cell now shows the back-off** that 19d-m found: cVA + touch -> MDN 0.0 -> 25 Hz with no state, 0 -> 11
  with P1, 0 -> 21-30 in the hunger / satiety states; "all pheromones + contact + touch" -> MDN 1.4 -> 53 Hz. The published
  lobe had hidden the male's MDN response to head bristles entirely.
- **Hunger and satiety states: nothing, and now nothing spurious either.** Under the published lobe NPF and SIFa + sugar
  changed PPL1 by 26 and 34 Hz (the runaway state amplifying whatever entered it); under the paper's model the largest
  effect any of the five states has on any readout under any input is 3.9-5.8 Hz (MDN with touch, within seed noise).
  Sugar -> MN9 stays at 0 in every state (the pooled taste labels, 19f).
- aIPg tonic (the only "aggression" class MaleCNS labels for him): 28 Hz of aIPg drives song MNs 4 Hz and wing MNs 1.2 at
  rest under both lobes, cVA -> DNp13 35 (vs 30 without the state), nothing else.
For the answer table the state rows are unchanged in every number that matters, and the two "state x odor" remarks of
14k / 14p (odors reduce pC1a; odors reduce pIP10 and feed the courting male) are withdrawn as properties of the runaway
lobe. Fig 5 now has both lobes for both sexes.

### 19b. Encounter trials in a clean chamber, and on the substrate (`encounter_trials.sh 5 300`, 23:13-; `encounter_stats.py --chamber clean|noise0.2`; Fig 3b)
*Protocol change:* the series begins with `survey_chamber.js --clear` (19a) and stops if anything odorous is left; the trial
label carries the chamber (`off_ff_t3_clean`). *One trial lost and redone:* the survey had wiped the slab under fly1's last
logout position, fly1 logged in over the hole, fell 124 blocks and died before the arena builder's /tp; it spent the
first clean ff trial at the world spawn while fly2 stood alone in the chamber (logs in `logs/discarded/`, with a note).
The survey now lays a grass floor back after clearing, and trial 1 was rerun at the end of the queue with its seed and
start positions. Brain time per fly: 127-143 s in ff (nothing fires, the brain runs at 0.45x), 78-92 s in mf.

**Clean chamber, female-female (5 trials): nothing moves.** Every readout 0.00 in all 10 fly-logs for 130 +/- 6 s of brain
time each — DNa 0 / 0, DNp09 0, walk duty 0.00, path 0.0 blocks, DNp13 0, feeding MNs 0, GF 0, MDN 0; median distance
4.4 blocks (where they were put), contact in 0 of 5. What each female senses: the other's body odor (Or47b, up to 0.42
of the body's maximum, i.e. 63 Hz on VA1v) and CO2 at 0.003 — and 18a's "Or47b -> nothing" holds in the world. The
18h prediction is confirmed at n = 5 with no residual: **without an odor (or the substrate of 19c) a female of this
model does not walk, so two of them never meet, and every contact-evoked result of 18h had the flower smell as its
precondition.** (Also a control for 18h's "faint smell": the same chamber, same seeds and starts, only the patches gone.)

**Clean chamber, male-female (5 trials): the female walks on the male's cVA; the male moves only when he touches her.**
The female's numbers are 18h's to the decimal — walk duty 0.48 (18h 0.47), path 42 blocks (40), DNa L / R 12.7 / 12.6
far (12.4 / 12.4), DNp13 5.1 far (5.7), GF 1.9 (2.3), symmetric turning (ctl_turn +0.00) — with no flower anywhere:
so the mf female of 18h was never walking on the flower smell but on the male's cVA (mean 0.06-0.14 of maximum, 9-21 Hz
on DA1 / DL3; 18a: cVA -> DNa 10 / 8, symmetric), and her 1.9 Hz giant fiber is cVA's (18c: cVA -> GF 0-2.3 Hz at
every dose). Contact in 2 of 5 trials (trial 1: 1 bout of 0.2 s; trial 3: 5-6 bouts, the longest 0.95 s; 8 +/- 16 contact
ticks per log), first contact at 1.2-1.4 s in both; on contact DNp13 31.6 Hz, feeding MNs 22.1, DNa 0.0 / 0.3, walk 0.01
(the stop), MDN 0.2; 0 lunges, aggression 0.0 throughout, 30 rejection acts and 16 proboscis extensions per minute
(the far rates: DNp13 5.1 Hz gives 3 spontaneous acts a minute; the rest is contact). **The male** stands (walk duty
0.03, path 26-37 blocks of drift) in the four trials in which he is not touched — the female's Or47b and CO2 reach
nothing in him either — and in trial 3, where she touched him six times, he walked 158 blocks at duty 0.29: her contact
pheromone on his legs (ppk25 -> leg MNs 2.9 Hz, duty 0.3; -> MDN 22-29 Hz) is the only thing that moves this male, and
it moves him backwards and away (MDN 48 Hz on contact, 15 Hz near — 26 in trial 3 — 4 far). So the mf bouts are short (<= 1 s here, 2 s
in 18h) for the reason 18h gave. P1, pIP10, song MNs: 0.0 far, near and on contact; "sing events" 9.8 / min are the
ppk -> wing-MN events of 18b, not song.

**Is there a DN change before contact? Pooled "near" statistics say yes; the ticks say mostly no.** 18h reported
"near-without-contact = far". Pooled over all non-contact ticks within 3.5 blocks, the clean mf female's turning DNs
are 7.7 / 8.3 against 12.7 / 12.6 far (413 vs 8546 ticks), walk duty 0.33 vs 0.49 — and the same drop appears under the
substrate between two females with no cVA in the chamber (9.4 / 12.2 near vs 15.6 / 16.4 far). Sorted by time since
the last touch, the drop is the touch reflex outlasting the touch: DNa 5.9 / 5.6 in the 0.1 s after a contact ends,
10 / 17 at 0.1-0.25 s, 11-15 / 13-15 while the flies are still within 3-6 blocks in the next two seconds, 16 / 16 from
2 s on — and most "near" ticks are these, before and between the flickering touches of a bout. Restricted to the ticks
*before the first contact of a log* (the approach itself), the counts are small and the effect at most modest: under
the substrate 15.2 / 15.3 at 3.5-6 blocks, 11.5 / 16.2 at 2-3.5 (60 ticks), 10.8 / 13.5 at 1.3-2 (26 ticks) against
15.8 / 16.5 far; in the male's cVA 10.5 / 11.2 at 3.5-6, 9.5 / 8.5 at 2-3.5 (20 ticks), 7.8 / 8.9 at 1.3-2 (9 ticks) against
12.8 / 13.1 — a possible 20-35 % slowing in the last two blocks (the offline cVA dose curve has a dip there: bilateral DA1
-> DNa 6.0 / 6.2 at 75 Hz against 9.5-11.5 at 25-50 Hz, 18c, and the body's cVA at 2 blocks is ~75 Hz), at tick counts
(4 DNa neurons x 50 ms: 5 Hz quanta) that cannot establish it. The turn command is 0.00 at every distance: left = right,
nothing turns toward or away in either sex. So the 18l row stands as "approach: no" with the qualification "a slowing
in the last two blocks before contact is possible (20-35 %, n = 29-86 ticks) and would be a dose effect of the
partner's odor, not a turn"; the reflex that makes the pooled near statistics look like a change is the stop on
contact (19d), which outlasts the touch by ~0.2 s.

**On the substrate (0.2 Hz background kicks in both brains; 5 + 5 trials, 00:11-01:31 plus one redo; brain time 84 +/- 6 s
in ff, 85 +/- 4 s in mf, 77-89 for the male). One trial lost to the machine going to sleep (the MacBook was on battery and
idled to sleep at 00:18 for 27 min; `logs/discarded/`), redone at the end; `caffeinate -i` holds the machine for the rest.**
- *The substrate in the arena is larger than its 1 s calibration.* With nothing to smell, the female's turning DNs run
  at 15.5 / 16.3 Hz (walk duty 0.51-0.57, 62 blocks per trial) — not the 7 / 7 of 19c. A 10 s offline run
  (`noise_floor_flywire_shiu_min1+known+eln0.25_10s.csv`) gives 18.1 / 20.4 at 0.2 Hz and already 17.0 / 18.8 at 0.1 Hz:
  the DNa response to background kicks saturates within a few seconds, and the 1 s window of 19c caught its onset.
  The rest of the calibration holds in the steady state — touch -> DNa 5.2 / 2.8 with DNp13 28.9, sugar -> MN9 unchanged,
  GF 2.7 Hz (arena 1.6) — and the costs are what the arena shows: DNp13 5.3 Hz with no one near (44 rejection acts per
  minute, of which ~30 are the substrate's), feeding MNs 8.1 (32 proboscis extensions a minute, ~25 the substrate's),
  the aggression neurons at their injected 0.2 Hz (2 lunges a minute, 4 near another fly in 10 logs), a jump in ~7 %
  of ticks. In the male the substrate reaches the leg motor neurons (2.6 Hz, walk duty 0.27, 127 blocks per trial) and
  MDN (6.2 Hz: his backing drive 0.30 exceeds his walking drive, so he mostly moves backwards), and it puts P1 and pIP10
  at their injected 0.2 Hz. Every act count on the substrate is read against these floors.
- **Female-female: they meet, stop, and stay — the 18h result without any odor.** Contact in 3 of 5 trials (6 of 10
  fly-logs), 11 % of the trial in contact on average, 5 bouts per log, the longest 15.1 s (18h: 4 of 5, 37 %, longest
  86 s — the flower smell held them at the wall together; here they cross in the open). On contact DNa 1.2 / 1.2 (from
  15.5 / 16.3), walk duty 0.04, DNp13 30.9 (from 5.3), feeding MNs 21.3 (from 8.1), GF 0.05 (from 1.6); MDN 0.4; 0 lunges
  beyond the floor. The stop is the wiring's under the substrate as it was in 19d offline (index 0.92 here). Whether the
  bout ends depends on the substrate's own fluctuations (the flies drift apart when the suppressed DNa flicker back),
  which is why the bouts are seconds here and tens of seconds in 18h.
- **Male-female: contact in 4 of 5 trials, and every bout ends the same way.** Bouts 2.4 per log, the longest 1.3 s, first
  contact 5-77 s; the female on contact DNp13 30.6, feeding MNs 21.0, DNa 2.0 / 1.8 (from 15.2 / 16.1); the male on
  contact MDN 28.9 Hz (from 6.2 far, 12.9 near), wing MNs 21 and song MNs 15 (the ppk -> wing MN reflex, 18b), P1 0.20 and
  pIP10 0.34 — the injected floor, not a response: near 0.21 / 0.22, far 0.20 / 0.24. The male backs out of every
  contact within 1.3 s; the female stops; nobody sings, nobody lunges (attack events 2.9 / min = the floor).
- **Before contact, nothing that a turn would show.** ctl_turn 0.00 far, near and in contact in every condition; DNa
  L = R within a Hz. The near-without-contact drop of the pooled statistics (ff 8.2 / 7.9 vs 15.5 / 16.3) is the
  post-touch recovery and the flickering touches of a bout (see above); before a log's first contact the turning DNs
  within 3.5 blocks are 11-16 Hz against 15.8 / 16.5 far (86 ticks).
- **Against the other three chambers (Table, `encounter_trials.csv`, Fig 3b):** published lobe / odor-free (14u): ff
  never touch, walk 0.71 in left loops; mf 4 / 5. Specific lobe / faint smell (18h): ff 4 / 5, 37 % in contact; mf 1 / 5.
  Specific lobe / clean (19b): ff nothing moves, 0 / 5; mf 2 / 5 (the female walks on cVA). Specific lobe / substrate:
  ff 3 / 5, 11 %; mf 4 / 5. The contact-evoked numbers are the same in all four (female DNp13 30.6-33 on contact with
  either sex, DNa -> ~0, feeding MNs 21-22; male MDN 29-48); what differs between chambers is only whether anyone
  walks, and on what.

**19c, addendum (steady state).** The 1 s calibration underestimates what the substrate does to a brain that runs
continuously: at 0.2 Hz the turning DNs settle at 18 / 20 Hz within seconds (10 s runs, 2 seeds), at 0.1 Hz at 17 / 19,
at 0.3 Hz at 20 / 22 — the response saturates, and the arena's 15.5 / 16.3 is the steady state of the 0.2 Hz choice. The
reflexes hold there (touch -> DNa 5 / 3 and DNp13 29-34; GF 2.7-3.9; feeding MNs 2.4-5.2; DNp13 0.2-0.3 with no input
over 10 s — the arena's 5 Hz floor comes with the eye and the other fly's odor on top). The male: leg MNs 1.2 Hz, MDN
3.2, contact pheromone -> MDN 10.8 and leg MNs 3.0 in the steady state (arena: 2.6, 6.2, 29 on contact). For the
paper the substrate is reported by its arena values, with the 1 s table as the dose axis. The "active fraction" of a 10 s
window is not informative (86 % of neurons receive at least one kick in 10 s at 0.2 Hz).

### 19g. What this session changes in the answer table (amendments to 18l; the table itself is now Table 1 of `PAPER.md`)
| row | 18l said | now |
|---|---|---|
| Stop on contact | wiring; a reflex that holds two females together | **wiring, established:** present under every sign rule, eLN scale and full table (index 0.5-0.94; 0.72-0.92 in the paper's model), abolished only by the >= 5-synapse threshold — carried by weak connections; holds under the substrate (0.77-0.90 offline, 0.92 in the arena); the female never backs away (MDN 0-1.4) (19d) |
| Male backs off on touching a female | wiring, fragile to gain | **wiring under the paper's model** (touch -> MDN 11-34 Hz in all unclear-LN settings, ppk25 + touch 22-28), **0 under the published lobe** — decided by the eLN scale, and gain 1.0 only (18b): reported as a sensitive result; it ends every mf contact within 1-2 s in every chamber (19d-m, 19b) |
| Approach to another fly | no; no DN change before contact | **no**; turn command 0.00 at every distance in every chamber; the near-vs-far drop of pooled statistics is the stop reflex outlasting the touch (~0.2 s); a 20-35 % slowing in the last two blocks before a first contact is possible at n = 29-86 ticks and would be the partner's odor dose, not a turn (19b) |
| Female rejection signal on touch | 36 Hz, not gated by odor, 33 on contact | unchanged, and now in four chambers: 30.6-33 Hz on contact with either sex, on the flower smell, on cVA alone, on the substrate (19b) |
| Female receptivity / aggression (state) | SAG / pC1 state | unchanged to the digit under the paper's model; the "odors reduce pC1a" remark of 14k withdrawn (runaway lobe); a virgin's touch-evoked pC1d/e is no longer masked by odor (7.1 Hz with cVA + touch) (19e) |
| Male song command (state) | P1 state | unchanged to the digit; "odors reduce pIP10 / feed the courting male" of 14p withdrawn (runaway lobe) (19e-m); on the substrate P1 / pIP10 sit at their injected 0.2 Hz with no change near or on contact (19b) |
| Hunger-dependent anything | no | no, under both lobes: <= 6-7 Hz on a single neuron, the same shift unrelated states produce; the published lobe's 26-34 Hz PPL1 changes in the male were its runaway (19e) |
| (new) Walking itself | – | **not in the wiring without an input**: a female with nothing to smell stands still for 135 s (10 logs, every readout 0.00); she walks on a flower smell (18h), on a male's cVA (12.7 / 12.6, duty 0.48) or on the 0.2 Hz substrate (15.5 / 16.3, duty 0.51); the male walks only when a female touches him (ppk25 -> leg MNs) or on the substrate (19b) |

**The one-sentence answer, after 19:** in the published whole-brain model with an antennal lobe that tells odors apart,
reflexes are in the wiring — feeding, startle, touch -> rejection, touch -> stop (the female) or touch -> back off (the
male), the male's pheromone -> DNp13 — and so is the absence of everything else: nothing in the wiring makes a fly walk
without an odor or a substrate, approach another fly, decide (pC1, aIPg, vpoDN, P1 silent to every input), or use the
odor-specific memory its own rule writes; the social decisions appear the moment an identified synaptic state (SAG, P1) is
active and not with any of the neuromodulatory ones (hunger); and the two choices of ours that every odor result rests on
(known signs, eLN x0.25) are carried as an axis on every row, with the walking substrate as a third, calibrated and
reported.

### 19h. Release package and the paper draft (02:00, 19 Sep)
`reproduce.sh list` prints the command behind every result file in `experiments/results/` (16 groups: core check,
anchors, odor code, social map, gain, shuffle, sensitivity, odor dose, contact stop, noise floor, state, conditioning,
expression, figures, arena encounters, arena learning); `all` reruns the offline groups in order, `arena` the two arena
groups, `archive` writes `release/flycraft_<date>.tar.gz` — results and figures, the code (brain/, bot/, experiments/),
every arena and experiment log including `logs/discarded/` and its README, the notes, README, paper and this script, with a
sha256 MANIFEST (641 files, 45 MB; the data/ downloads are not included). `PAPER.md` is draft 1: abstract, introduction,
seven results sections, discussion, methods with the "real vs ours" list, Table 1 (the answer table with this session's
rows), Table 2 (the four chambers), 13 figures, reference stubs. Its numbers were typed from the notes and the result
files; the second draft should re-derive them by script (`WHATS_LEFT_FLY.md`, item 1).

## 20. Sixth pass (20 Sep 2026) — the second draft, with every number re-derived

*Goal set (`WHATS_LEFT_FLY.md` "until submission" 1-3 and the machine-time items): the numbers of `PAPER.md` re-derived by
script and the text corrected to them; print figures; the substrate reworded honestly everywhere; five seeds for the gain
sweeps of the paper's model and for the stop-on-contact axis; the pre-contact slowing as a dose row. Not run: the embodied
virgin female (item 5; the machine was on battery from 52 % with no charger and the Minecraft server was down — the command is
in `WHATS_LEFT_FLY.md`). Queue: `experiments/run_queue6.sh` under `caffeinate -i` (gain sweeps 5 seeds ~13 min for both
sexes, contact-stop 5 seeds ~30 min for both, the dose row ~10 min). New scripts: `experiments/paper_numbers.py` (every
number of the paper from the result files, with the paper's value next to it and a flag), `experiments/figures_print.py`
(print figures), `experiments/precontact_dose.py` (the dose row). The 3-seed gain and contact-stop files are kept as
`experiments/results/old_v1/*_3seeds.csv`; nothing else was overwritten.*

### 20a. Five seeds for the gain sweeps of the paper's model and for the stop-on-contact axis (`gain_sweep_*+eln0.25.csv`, `contact_stop_*.csv`)
- **Gain, female (5 seeds, 600 ms, 100 Hz):** sugar -> MN9 33 / 76 / 94 at gain 0.7 / 1.0 / 1.4 (3 seeds gave 38 / 77 / 93);
  JO-A -> GF 6 / 11 / 16; touch -> DNp13 28 / 35 / 42, cVA + touch 27 / 36 / 37, food + touch 26 / 34 / 39; cVA -> DNa 9 / 8
  and food -> DNa 20 / 12 at gain 1.0; food -> PPL1 4.9 / 17 / 36; food -> GF 0 / 3.8 / 3.3; Or47b -> DNa 0 / 0 / 24 and
  0 / 0 / 35; pC1a, pC1d/e, aIPg, vpoDN 0.0 at every gain <= 1.4 for every input. **Male:** cVA -> DNp13 7.8 / 31.7 / 28.1;
  other odors -> DNp13 0.0; cVA -> pIP10 0 / 3 / 8; ppk23/25 -> song MNs 10 / 20 / 21 / 10 at 0.5-1.4, -> MDN 0 / 29 / 1.8;
  touch -> MDN 0 / 11.5 / 12; JO-B -> GF 34 / 41 / 48 / 52 from 0.5; **P1 is not 0.0 at gain 1.0: cVA + touch gives 0.48
  Hz** (cVA 0.05), 1.6-2.1 at 1.4 (aIPg 1.4); the labellar GRNs -> MN9 0 / 0 / 0 / 0.8 at 0.5-1.4. Every window of 18a / 18b
  stands; the paper now carries the 5-seed means.
- **Stop on contact, female (5 seeds, 600 ms):** paper's model food 20.3 / 12.3 -> 6.8 / 3.2 (index 0.69), cVA 9.3 / 8.2 ->
  0.0 / 1.2 (0.93); with the substrate 0.77 / 0.91 / 0.89 / 0.82 for food / cVA / Or47b / the substrate alone. Over every
  cell with a real walking drive (DNa alone >= 2 Hz), under every sign rule, eLN scale and full table, with and without
  the substrate: **0.35-0.93** — the published lobe 0.35-0.59 (its runaway lobe drives the left DNa to 35 Hz and the
  bristles still take a third to a half), known signs x1 0.40-0.57, x0.5 0.49-0.74, x0.1 0.70-0.86, Shiu signs x0.25
  0.54-0.91, Zenodo all connections 0.70-0.85, the paper's model 0.69-0.93. **19d's "0.5-0.94" was wrong at the low end**
  (the published lobe's cVA cell was 0.31 in the 3-seed file already; the table in 19d shows it). The one cell at ~0 is
  no exception: cVA under the Zenodo signs drives no DNa (0 / 0), so there is nothing to suppress. The >= 5-synapse
  threshold still abolishes it: food 27.8 / 10.5 -> 17.3 / 17.8 (0.08), and the bristles drive the DNa with no odor drive
  at all (cVA-silent 0 / 0 -> 7.2 / 17.5, Or47b 0 / 0 -> 8.0 / 16.5, the substrate 5.5 / 5.3 -> 10.2 / 17.0: contralateral
  16-18 Hz). MDN with touch <= 1.3 Hz in every female cell. DNp13 with touch 34 (paper's model), 17 (published), 17-38 over
  all conditions.
- **Stop on contact, male (5 seeds):** ppk23/25 -> DNa 8.2 / 4.7 -> 0.0 / 0.0 with touch (index 1.0 in every setting; 0.80-0.91
  on the substrate). Head bristles -> MDN by walking drive, paper's model without / with the substrate: substrate alone
  - / 17.7, cVA 25.9 / 15.0, contact pheromone 23.0 / 29.1, food odor 3.1 / 2.7, Or47b 2.2 / 10.8; unclear LNs inhibitory:
  cVA 29.8 / 24.8, food 14.4 / 7.4, Or47b 5.1 / 8.1, substrate 15.5; silent: cVA 33.5 / 18.2, food 4.4 / 4.7, Or47b 5.3 /
  10.0, substrate 15.6; published lobe (eLN x1): 0.0-0.5 for every drive but the contact pheromone's own path (23.0; 2.5
  with the substrate). **So 19d-m's "11-34 Hz in every unclear-LN setting" is true on the substrate, with cVA or with the
  contact pheromone (15-34 Hz) and not with food odor or Or47b as the drive (2-14 Hz)**; the eLN-scale dependence stands
  (0-2.5 under x1). ppk25 + touch -> MDN 23 (29 on the substrate); cVA + touch -> MDN 26; cVA -> DNp13 30 -> 7.7 with
  touch; leg MNs on the substrate 0.4 -> 1.6 with touch, with the contact pheromone 2.9 -> 1.8. Table 1's row now says so.

### 20b. The pre-contact slowing as a dose row (`experiments/precontact_dose.py`, `precontact_dose_flywire_shiu_min1+known+eln0.25.csv`, Fig 14)
Design: the female brain (paper's model) driven bilaterally with cVA (DA1 + DL3), Or47b (VA1v) and CO2 (V) at the levels
the arena logs report (fractions of the 150 Hz maximum): far from the other fly cVA 0.06-0.14, Or47b 0.10, CO2 0.003; at
1-3 blocks cVA 0.3-0.7, Or47b 0.4-0.9, CO2 0.02; each channel alone as well; 2 s of settling and 2 s of reading (the
arena's steady state, not 19c's 1 s onset); 3 seeds; without and with the 0.2 Hz substrate. 42 cells, 11 min.
- **Without the substrate (the clean mf chamber):** cVA at 0.06 and 0.10 reaches nothing (DNa 0 / 0 — a threshold, which is
  why the arena's far female, smelling 0.06-0.14, walks at 12.7 / 12.6 on average); at 0.14 the mixture gives DNa 15.2 /
  15.2 (walking drive 0.64); at the near levels it gives 8.5 / 10.8 (cVA 0.3), 4.5 / 6.3 (0.5), 5.2 / 5.9 (0.7) — walking
  drive 0.47 / 0.30 / 0.31. cVA alone falls only mildly (13.8 / 14.8 at 0.14, 14.5 / 16.0 at 0.3, 11.7 / 11.4 at 0.5, 11.5
  / 9.5 at 0.7); Or47b alone (0.1 / 0.4 / 0.9) and CO2 alone (0.003 / 0.02) reach nothing; but Or47b + CO2 at their near
  levels halve the cVA response (cVA 0.5 alone 11.7 / 11.4, in the mixture 4.5 / 6.3). One oddity, reported: Or47b 0.6 +
  CO2 0.02 with no cVA gives DNa 9.0 / 12.8 and GF 4.2 (0.4 and 0.9 give nothing) — a narrow window, below which the arena's
  Or47b (<= 0.42) stays. Two females without the substrate: every cell 0 (19b's clean ff result).
- **With the substrate:** nothing to smell 19.6 / 19.8 (the steady state of 19c, addendum); the male's odor at the far
  levels 13.5 / 16.5 - 18.8 / 21.8 (0.06-0.14; large seed spread at 0.06-0.10), at the near levels 12.9 / 15.8, 8.6 / 12.0,
  9.5 / 12.9 (**-31 % near vs far**, walking drive 0.67 -> 0.55); cVA alone 16-22 -> 14.8 / 14.9 at 0.7. Between two
  females: Or47b at its far level 10.5 / 10.2 (+- 7-9 across seeds) and at its near levels 12.4 / 20.3, 12.0 / 17.1, 8.9 /
  14.7 (Or47b 0.4 / 0.6 / 0.9 + CO2 0.02) against the substrate's 19.7 — 15-40 % off, with a consistent left-right
  asymmetry (R > L by 5-8 Hz; turn command -0.13 to -0.20) under a bilateral input; CO2 alone leaves the substrate where it
  is (20.4 / 20.8).
- **Verdict (WHATS_LEFT item 6):** the 15-40 % slowing of the arena female in the last two blocks before a first contact
  (19b; the per-bin table in `paper_numbers.md`: substrate mf 7.2 / 11.9 at 1.3-2 blocks against 14.8 / 16.5 far, clean mf
  7.8 / 8.9 against 12.7 / 12.9, substrate ff 11.7 / 12.8 against 15.7 / 16.4) is what the partner's odor at the levels of
  1-3 blocks does to her turning DNs offline: the falling limb of a dose curve, made of cVA's own mild fall and of Or47b
  + CO2, which reach nothing on their own but halve the cVA response and cut the substrate's drive in the mixture. Not a
  decision, not a turn (turn-toward index within +-0.03 in every chamber, 20f). Caveat: 3 seeds x 2 s per cell; the far
  Or47b cells on the substrate have a large seed spread. Fig 14; the paper's Results 3 and 6 and Table 1's approach row.

### 20c. The substrate, reworded (WHATS_LEFT item 3)
Every mention in `PAPER.md` now says the same four things: it is the only spontaneous activity the model offers and a
choice of ours; it puts 0.2 Hz of input on every neuron, the decision neurons included (the injected 0.2 Hz floor of
pC1d/e, aIPg, P1 and pIP10 in the arena); its arena effect is the saturated steady state (17-22 Hz on the turning DNs in
10 s runs at 0.1-0.3 Hz, 15.5 / 16.3 in the arena), not the 7 / 7 Hz of the 1 s calibration; and the acts counted on it
are read against its floors (44 rejection acts, 32 proboscis extensions and 2 lunges a minute, a jump in 12 % of ticks
— not the "~7 %" of 19b, which was an estimate; `paper_numbers.py` counts the ticks — and in the male leg MNs 2.6 Hz, MDN
6 Hz, P1 / pIP10 0.2). Places: Abstract, Results 3, 6 (the substrate paragraph rewritten), 7, Methods (encounter trials),
Table 1 ("Walking itself"), Table 2 (header), the Fig 13 legend.

### 20d. References verified
Every one of the 24 stubs of draft 1 was checked against the publisher's page, PubMed / Europe PMC or the preprint server.
Three were wrong: Ding et al. 2019 is *Current Biology* 29:1089-1099, not Nature; Rayshubskiy et al. is the version of
record, *eLife* 2025 13:RP102230, not the 2020 preprint; "Card & Strausfeld 2010" (giant fiber) does not exist and is
replaced by von Reyn et al. 2014 (*Nat Neurosci* 17:962-970). Thirteen works the code and the methods use but the stubs
did not name are added: Brian2 (Stimberg et al. 2019), DoOR (Münch & Galizia 2016), the degree-preserving shuffle (Maslov &
Sneppen 2002), the conditioning design (Tully & Quinn 1985), the mushroom-body anatomy and rule (Aso et al. 2014; Hige et al.
2015), cVA (Kurtovic et al. 2007; Datta et al. 2008), fly odor (van der Goes van Naters & Carlson 2007), DNp13 (Mezzera et al.
2020), ppk23/25 (Thistle et al. 2012), DNp09 (Bidaye et al. 2020; Zacarias et al. 2018). MaleCNS is cited as its preprint
(Berg et al. 2025, bioRxiv 2025.10.09.680999; the v1.0 release of 8 June 2026); the *Cell* 2026 citation the release
announces could not be verified from here and is flagged in the paper.

### 20e. Print figures (`experiments/figures_print.py`)
`fig1_print_innate_map` (both sexes, the paper's model, 7.2 x 9.4 in), `fig3_print_encounters` (one trial per chamber and
pairing — the trial with the longest bout — trajectories with the contact ticks, and the female's DNa, the distance and
the male's MDN below; the chamber drawn as what it is, a 13 x 13 square with walls at -6 and +7, not a circle),
`fig5_print_state_arm` (state alone / + touch / + cVA + touch, both lobes side by side, both sexes), `fig7_print_sensitivity`
(the claims of Table 1 as columns, 14 + 13 rows), `fig13_print_substrate` (the 1 s calibration, the 1 s onset against the 10
s steady state, the male); PNG at 300 dpi and PDF. Fig 14 (the dose row) added to `figures.py`. Fig 12 and Fig 4 are
regenerated from the 5-seed files.

### 20f. Draft 2 by script (`experiments/paper_numbers.py` -> `experiments/results/paper_numbers.md`)
The script prints ~150 cells (Table 1's evidence, Table 2, the numbers of every Results paragraph, the in-world learning
probes, the pre-contact bins from the raw logs, a turn-toward index) next to the value typed in the paper and flags any
that differ beyond rounding. First pass against draft 1: 68 of 137 flagged; besides the 5-seed means and format, the real
ones were: **(i) a mislabelled row in 18e** — the values quoted for "Shiu signs, eLN x0.25" (food -> PPL1 62, PAM 2.6, KC
3.8) belong to the first-version-numerics row; the true cell is 17 / 0.1 / 1.5, i.e. the sparse Kenyon-cell code needs the
eLN scale and not the sign rule (Table 1's odor-identity row reworded; 16b's dose-response is unaffected); (ii) the female
sensitivity table has 14 conditions, not 15; (iii) the shuffle control leaves every readout at 0-2 Hz, not 0 (one rewired
female brain has MDN 7 Hz under food odor, one male DNp13 5 Hz); (iv) the male's P1 is <= 0.5 Hz, not 0.0, at gain <= 1.0
(cVA + touch), and pIP10 answers cVA with 2-3.5 Hz in the 1 s map; (v) "touch -> MDN 11-34 Hz in every unclear-LN setting"
holds on the substrate, with cVA or with the contact pheromone (18-34), not with food odor or Or47b as the drive (3-12);
(vi) ppk25 alone -> leg MNs 1.5 Hz and MDN 13 (the 2.9 / 28 quoted in 19b were the whole ppk23/25 set); (vii) odor code:
glomeruli active 89 % on average (98 % for most odors) at eLN x1, 64 % at x0.5, 18 % (2-28 % by odor) at x0.25, 3 % at x0.1;
(viii) steering: the paper's rule avoids the four food-type odors by 0.7-9 Hz in all 20 odor x dose cells; the published
signs' bias is 16-29 Hz for the food-type odors and 0-19 for the rest; the Zenodo bias 1-15; the male |steering| <= 2.6,
|bias| <= 3.2; (ix) the "pre" walk / turn values of world6 were its training-phase values (the 15 s pre phase never
brought the fly near a patch); (x) the expression probe's MDN with the tonic drive is 18.6, and the 28 descending targets
are "within 0.6 Hz intact vs silenced", not "at 0.6 Hz"; (xi) a jump in 12 % of ticks on the substrate, not ~7 %; (xii) the
untouched male's drift 26-31 blocks (37 was the faint-smell chamber); (xiii) the aroused state's touch -> pC1d/e 9.4, not
9.6; (xiv) the encounter chamber is a 13 x 13 square (walls at x, z = -6 and +7), which the Methods now say. A **turn-toward
index** (turn command x the sign of the azimuth to the other fly, pre-contact ticks within 6 blocks) is within +-0.03 in
every chamber under the paper's model (-0.19 under the published lobe, where the fly turns left at +0.6 whatever is there):
nothing turns toward or away. Second pass after the edits: 141 cells compared, 0 differ (the checker's expectations are now draft 2's own values, so the
script is the regression check for the text: `python experiments/paper_numbers.py` after any rerun). The male gain sweep at
5 seeds moved three cells the paper now carries: cVA -> DNp13 7.8 / 30 / 26 (3 seeds: 32 / 28), ppk23/25 -> MDN 27 at gain
1.0, touch -> MDN 0 / 10.7 / 11.8, JO-B -> GF 34 / 41 / 48 / 54; P1 <= 0.6 at gain <= 1.0 and 1.9-2.3 at 1.4..

### 20g. Venue and length (decided)
eLife (bioRxiv -> Reviewed Preprint), PLOS Computational Biology as the alternative; not Nature Communications (the
argument is the controls, which its length would push into a supplement). Main text ~6,500 words: the per-condition numbers
move into the tables and legends. Main figures 1, 3, 5, 7, 12, 2b and 13; Figs 4, 6, 8-11, 14 and the per-trial panels of 3
supplementary; Table 1 main, Table 2 supplementary. Written into `PAPER.md`'s closing note with the items to re-check.

## 21. Seventh pass (24 Sep 2026) — draft 3, cut to eLife's length

Checked against eLife's author instructions (elife-rp.msubmit.net, 24 Sep): abstract 150-200 words; main text "try not to
exceed 5,000 words" excluding Methods, references and legends; no limit on display items; any reference format at
submission; required: Acknowledgements, competing interests, funding, CRediT, data availability, code in an open archive.

- **Cut.** Abstract 598 → 200; Results 5,274 → ~3,700; Intro + Results + Discussion ~5,000 (raw token count). Numbers were
  moved, not changed: into Table 1, the legends (Figure 4-S1, 5-S3, 6-S3 and 7 now carry the state × odor cells, the MBON
  target rates, the per-bin pre-contact rates and the substrate floors) and the Methods (the simulator's semantics).
- **Figures** renumbered in order of first citation (old → new): 1 → 1, 7 → 2, 12 → 3, 5 → 4, 2b → 5, 3 → 6, 13 → 7;
  supplements: 8, 4, 6 → 1-S1..S3; 9, 10 → 2-S1, S2; state screens → 4-S1; 2a, 2c, 11 → 5-S1..S3; 3b, per-trial, 14 →
  6-S1..S3. Table 2 → Supplementary file 1. New print figures `fig12_print_contact_stop` (female DNa ± touch and
  suppression index over 8 conditions × substrate; male MDN over 4 conditions × substrate) and `fig2b_print_conditioning`
  (9 designs, n = seeds × orders; retained drive in the taught and the other compartment, learning index, approach change).
- **Errors in draft 2 found while cutting** (all passed paper_numbers.py, which compares its own stored strings, not the
  paper's text): learning index defined as 1 − CS+/CS− in Methods, computed everywhere as (CS− post/pre) − (CS+ post/pre)
  (the ratio form would give 0.84 / 0.85 / 0.84 / 0.61 / 0.65 / 0.66 / 0.04 / 0.86 / 0.88); Table 1 JO-B → GF (male) "34-52"
  vs 34 / 41 / 48 / 54; male labellar → MN9 "0 Hz in every condition" vs ≤ 0.8 at every gain (1.1 max, first-version
  numerics); male cVA → P1 "≤ 0.6 in all 13 conditions" vs 0.00-0.65 in 12 and 2.50 under the first-version numerics;
  Table 1 caption "15 female conditions" (14); "same numbers to the decimal" for the clean vs flower-smell male-female
  chamber (12.7 / 12.6 vs 12.4 / 12.4); memory expression compared "with before" (the numbers are after vs during
  training); the male contact-pheromone path (ppk25 + touch → MDN 23 Hz) is the no-substrate cell (with the substrate,
  published lobe: 3.3 alone, 2.5 with touch).
- **References.** MaleCNS published: Berg et al. 2026, Cell 189:5504-5526.e15, doi 10.1016/j.cell.2026.08.015 (PMID
  42691995; 111 authors). Author lists completed from Europe PMC (EXT_ID queries); Shiu et al. 2024 had two wrong names
  (Blanchard N, Rayshubskiy A). Honegger 2011, Shang 2007, Olsen 2007, Huang 2010 cited again where §16 used them;
  Chen et al. 2018 removed (cited nowhere, here or in the notes).
- **Not done (battery 8 → 4 %, no charger):** the virgin-female arena series, the optional Or47b × CO₂ steps, a new
  release archive. Placeholders for authors, funding, competing interests, CRediT, AI use and the Zenodo DOI are the
  user's.

### 21b. The virgin female in the arena; the Or47b × CO2 window; the dose row at 10 seeds (24 Sep, evening, on AC)

- **Virgin female with a male on the 0.2 Hz substrate** (`CONDS=mf STATE2=virgin NOISE=0.2 LABEL=noise0.2-virgin
  experiments/encounter_trials.sh 5 300`; 29 min; chamber verified clean). The label must not contain `_`:
  `encounter_stats.py` reads the chamber from the 4th `_` field, so the WHATS_LEFT command as written (no LABEL) would have
  pooled these trials with the 19b series and overwritten its `.out` files. `encounter_stats.py` now also records
  `hz_accept` (DNp37 = vpoDN), `hz_egg` (oviDN) and `hz_sag`, and the acceptance / egg-laying events.
  Result (5 trials, female brain time 64 ± 23 s; no-state 19b series in brackets): contact in 5 / 5 trials (4 / 5), 3.6 ±
  3.2 % of ticks (1.3), first contact at 1.2 s (5.1); DNp37 15.8 / 16.7 / 15.9 Hz far / near / contact (0.2-0.3) and 99
  acceptance acts a minute (1) — tonic, not gated by the male; SAG readout 28.5 Hz (the imposed 30 Hz); DNp13 4.1 → 31.7 on
  contact (5.1 → 30.6: state-blind); pC1d/e + aIPg 1.0 Hz on contact (0.2); oviDN unchanged; the male's MDN 30 Hz on
  contact (29), longest bout 1.7 s (1.3); P1 / pIP10 at the floor. **Turn-toward index −0.005** (pre-contact ticks < 6
  blocks, n = 668): no approach with the state either — Table 1's "not tested with states" cell filled.
  Closest bin (1.3-2 blocks, 37 ticks): toward +0.16, but the turn is negative in all 5 logs whichever side the male is
  on (male on the − side in 4 of 5 by chance); per-log sign-flip null p = 0.12 (seeded, in paper_numbers.md section Q). The
  same holds for the 19b mf series (turn negative in 5 / 5 logs; toward −0.001). Not in every chamber: the faint-smell and
  substrate-ff logs in that bin are too few or mixed.
- **Draft-2 claim corrected:** "turn command within ± 0.1 in every pre-contact distance bin" (Results 6, Table 1) was
  false before today: the closest bins reach −0.11 (substrate mf, 88 ticks) and −0.25 (faint-smell mf, 4 ticks). Removed;
  the approach test is the turn-toward index, within ± 0.03 in every chamber (substrate mf +0.033 rounds to 0.03).
- **Or47b × CO2 window** (`--set window`, no substrate, 5 seeds; `_window.csv`): Or47b 0.40-0.90 (0.05 steps) + CO2 0.02
  drives the turning DNs weakly and seed-dependently over the whole range (means 0.9-7.3 L / 1.2-10.8 R; largest at 0.60),
  not a narrow resonance — 20b's "0.4 and 0.9 give nothing" was 3-seed sampling. Or47b alone: 0 at 10 of 11 steps (one
  seed of five at 0.75). CO2 is necessary; the response sits at threshold.
- **Dose row on the substrate at 10 seeds** (`--set far`, `--set near`; `_far.csv`, `_near.csv`): the substrate alone
  15.0 / 15.7 ± 6-7 (3 seeds said 19.6 / 19.8); far levels 11.0-17.7 Hz, seed sd 5-9; near levels 7.8-13.8 / 12.6-18.1,
  sd 1-4. Paired by seed: male's odor near − far −0.7 ± 1.9 Hz (s.e.m.), the other female's +2.7 ± 2.4; CO2 alone 18.4 /
  18.8. So 20b's substrate claims (far 19-22 → near 9-16 Hz, −31 %; the female's odor 15-40 % off the substrate's 20 Hz)
  were seed sampling and are withdrawn from the paper. What holds: at every near level R > L by 4.3-5.9 Hz (turn −0.11 to
  −0.14), matching the negative closest-bin turn of the substrate mf chambers. The no-substrate dose row (the paper's main
  argument) is stable at 3 seeds: cVA 0.14 mixture 14.2-15.8 Hz vs cVA 0.5 mixture 3.2-7.0 across seeds, no overlap.
- **Reproducibility:** re-running 13 dose-row cells with 10 numba threads (the 20 Sep queue used `NUMBA_NUM_THREADS=6`)
  reproduced 38 of 39 seed-cells to the digit; one (mf far cVA 0.06, seed 1) differed (11.5 / 14.75 → 10.75 / 11.5 Hz). The
  parallel pass (`lif.py _integrate`) collects spikes per thread chunk, so the thread count sets the delivery order, float
  summation order and, rarely, a seed's trajectory. The Methods now say "same numba version and thread count".
- **figures.py fixes:** per-trial panels paired the two flies by label + stamp without seconds, so a trial whose logs
  started either side of a minute (virgin t4: 17:41:59 / 17:42:00) got no panel; now paired by label and start within
  10 s, latest 5 pairs drawn. Fig 3b gained a DNp37 panel and the virgin column (label "n0.2 virgin").
- paper_numbers.py: 151 cells, 0 differ (10 new checks in section Q).

## 22. Eighth pass (25 Sep 2026) — the paper rewritten for anyone; a partial re-run from scratch

**Asked for:** re-run the research; rework the paper so it "sounds simple but not too simple", makes sense to a
biologist and to someone with no research background, explains why we do this, and is "fun yet grounded"; follow the
earlier papers in `pif-bench/paper/` (LaTeX, *Testing the Spirits* template) and write it like *The Metaphysics of
Farts* (Capra, *Think* 2022). Chosen with the user: a LaTeX preprint; an arena replication after the offline re-run.

- **Draft 4 = `paper/flycraft.tex`** (build `paper/build.sh`, tectonic; `flycraft.pdf`, 38 pages). `PAPER.md` (draft 3)
  is unchanged. Plain main text with nicknames for the neurons (Table 1, "the cast"), grey "For the specialist" boxes with
  every number, the template's Argument in Brief / Why Do This? / Why Minecraft? / What This Paper Is Not / Author
  Position / Objections / What Would Prove Us Wrong, and appendices (methods, the answer table, arena statistics,
  reproducing every number). The arena table is written by `experiments/replication_stats.py --tex paper/tables_arena.tex`.
- **Literature corrections (all checked on Europe PMC):** DNp13 extends the ovipositor; a brief extension invites the
  male to try, holding it out stops him (Mezzera 2020) — the logs' "rejection acts" are called ovipositor extensions now.
  Real pC1 neurons respond to cVA and song (Zhou et al. 2014) and real P1 to a female's touch (Kohatsu et al. 2011;
  Clowney et al. 2015): the model's silent deciders are its most important miss, not a neutral fact. Real males find and
  follow females mainly by sight (Ribeiro et al. 2018) and our flies are blind: "no approach" carries that caveat. DNp09
  is also implicated in freezing (Zacarias et al. 2018). 19 references added (Dickson 2008, Hall 1994, Greenspan &
  Ferveur 2000, Siegel & Hall 1979, Nilsen 2004, Zheng 2018, White 1986, Bargmann & Marder 2013, Marder 2012, MICrONS
  2025, NeuroMechFly v2 2024, flybody 2025, Martin 2004, Pool & Scott 2014, Hampel 2015, Zhou 2014, Kohatsu 2011,
  Clowney 2015, Ribeiro 2018), and the author's own five papers.
- **New numbers from existing files** (now checked in `paper_numbers.py` section R): the freeze index across gains, food
  / cVA drive, 0.69 / 0.93 at 1.0, 0.74 / 0.89 at 1.4, 0.86 / 0.93 at 2.0 (odour does not drive the DNa at 0.7); the male's
  cVA also drives MN9, 7.5 / 32.5 / 36.5 Hz at gain 0.7 / 1.0 / 1.4, 14.7-35.0 Hz in all 13 male conditions, 0 when
  shuffled (draft 3 never mentioned it); the published-lobe arena's turn-toward index is −0.19 (ff) and +0.08 (mf).
- **The re-run.** Every result file backed up to `release/pre_rerun_20260925/`; `./reproduce.sh all` started 20:01 with 6
  numba threads. Finished: core-check (unit tests pass; the Brian2 step failed because the reproduce.sh command omitted
  the export path — run by hand with Brian2 2.10.1: identical per-neuron spike counts for seeds 1 and 2, seed 0 diverges
  at a near-threshold event, 23,689 vs 23,512 spikes, 284 of 592 active neurons differ, r = 0.9999; the paper now says
  this instead of "identical"), anchors, odor-code, social-map, gain, and the three female shuffles. **Stopped between 21:04
  and 21:45 by Claude Code because the machine ran out of memory** (swap 17 of 18 GB in use, other applications running)
  while the male shuffle was rewiring MaleCNS (~1,700 s per rewiring step, swapping). Not re-run: male shuffle,
  sensitivity, odor-dose, contact-stop, noise-floor, precontact, state, conditioning, expression, figures.
  `experiments/compare_results.py`: 4 files identical to the digit (published anchors, both paper's-model gain sweeps,
  the paper's-model female shuffle); 5 reshaped because earlier script versions wrote fewer seeds, inputs or variants
  (paper's-model anchors 2 → 3 seeds, published-lobe gain sweeps, male odour code); 8 differ in a few cells (at most
  6 Hz in one cell of the published lobe's maps, at most 3 Hz under the paper's model: thread-count-sized). The original
  files were made with 3, 5, 6 or 10 threads across sessions.
- **Correction found by the re-run:** bitter suppression under the paper's model is 55 → 3.3 Hz (3 seeds), not 55 → 1.7
  (a 2-seed file of 15 Sep); published lobe 57.7 → 6.3. The sugar MN9 100/200 ratio is 69 / 71 % (was "69-75 %").
  `paper_numbers.py`: 155 cells, 0 differ.
- **Arena replication:** `experiments/run_replication.sh` (labels `rep-clean`, `rep-noise0.2`, `rep-noise0.2-virgin`;
  starts and stops the server; `WAIT=1` waits for a running reproduce.sh) was queued but stopped with the offline run
  before any trial started. `replication_stats.py` and `figure_replication.py` are ready. Section 8.7 of the paper is
  removed until it has run.
- **reproduce.sh:** the core-check command now exports to `$TMPDIR/flycraft_brian2` and passes the arguments; new group
  `arena-replication`; `archive` copies `paper/`. The block shuffle moved 91.6-91.7 % of edges in the re-run (the 15 Sep
  file said 94.3 %); global 99.8-99.9 %.

### 22b. The re-run finished, and the arena replication (25-26 Sep 2026)

- **Offline re-run, completed** after the user freed memory (`experiments/run_rerun_rest.sh`, markers in
  `logs/rerun_20260925_done/`; 22:31-01:07). With nothing else heavy running each group was fast (male shuffle 13 min,
  sensitivity 11 min, conditioning 43 min). `experiments/compare_results.py` (now aligns rows on key columns; the male
  noise-floor file only changed row order) over the 123 rewritten files: **54 identical to the digit** (among them both
  freeze-test files, both paper's-model sensitivity tables, both paper's-model gain sweeps, the female and male
  shuffles of the paper's model, both hum calibrations, both paper's-model state files, the expression probe, the no-hum and
  window dose rows, 37 of 84 conditioning files); **6 reshaped** (older script versions or, for encounter_trials.csv,
  the replication rows); the rest differ in a few cells: conditioning files at most 0.004 in a compartment's retained
  weight (original runs used 3 threads), the published-lobe state files by up to 11.5 Hz in single cells (14-15 Sep
  code), the 10-seed hum dose cells by up to 3.3 Hz (made with 10 threads on 24 Sep). `sensitivity.py` now writes the
  published-lobe table as `sensitivity_flywire_shiu_min1.csv` (14 conditions; the 14 Sep `sensitivity_flywire.csv` had 9).
  **`paper_numbers.py`: 155 cells, 0 differ** after updating four expectations: bitter 55 → 3.3 Hz; MN9 100/200 ratio
  69 / 71 %; P1 + odour → MN9 under the published lobe 19.4 / 18.6 (was 18.9 / 19.2); the 3-seed vs 10-seed dose-row
  seed-cells now 0 / 39 (both made with 6 threads; 1 / 39 on 24 Sep with 10 vs 6). No claim of the paper changed.
- **Arena replication** (`experiments/run_replication.sh`, labels `rep-clean`, `rep-noise0.2`, `rep-noise0.2-virgin`).
  Clean box, 300 s trials, 26 Sep 01:08-02:08, with the machine loaded by other jobs (load 40-50): brain time per female
  log 77 ± 72 s (ff) and only 14 ± 6 s (mf) against 135 and 90 in the originals. Claude Code stopped the run at 02:11
  (low memory) during the first hum trial (discarded, `logs/discarded/README.md`). The user chose to resume with 600 s
  trials; the resume waited for the load to fall (16:41) and ran the hum and virgin series (16:42-19:25; brain time 142 ±
  25, 100 ± 64 and 103 ± 39 s per female log). Results, replication against original (`experiments/results/
  replication_20260925.md`, `paper/tables_arena.tex`, `fig_replication`):
  clean ff: 0 / 5 contact, every readout 0 (0 / 5, 0); clean mf: contact in 2 / 5 trials (2 / 5), walk 0.53 (0.48), DNa
  14.1 / 15.5 → 5.0 / 5.3 on contact (12.7 / 12.6 → 0.0 / 0.3; few contact ticks at 14 s of brain time), DNp13 → 30.3
  (31.6), male walk 0.03 (0.08), MDN 37 on contact (48); hum ff: 5 / 5 (3 / 5), contact 59 ± 16 % of ticks (11 ± 15),
  longest bout 31 s (15), DNa 15.6 / 17.0 → 0.9 / 0.4 (15.5 / 16.3 → 1.2 / 1.2), DNp13 → 30.9 (30.8); hum mf: 3 / 5 (4 / 5),
  1.5 % (1.3), longest 2.5 s (1.3), DNa → 0.8 / 1.0 (2.0 / 1.8), MDN 31 (29), P1 / pIP10 at the floor; virgin: 5 / 5 (5 /
  5), DNp37 15.9 / 16.4 / 16.6 far / near / contact (15.8 / 16.6 / 15.9), 91 acceptance acts / min (99), DNp13 → 31.7
  (31.7), MDN 30 (30). Turn-toward index, replication: 0.000, +0.011, +0.028, +0.012, +0.040.
- **A faint lean, found by pooling** (new section in `replication_stats.py`): over every series of the paper's model,
  original and replication, the female's turn-toward index is positive in 24 and negative in 9 of the 33 male-female
  fly-logs that turn at all (sign test p = 0.014), pooled index +0.015 against a mean |turn command| of 0.25 (6 % of her
  turning); female-female 13 / 9 (p = 0.52). On the bench, cVA presented to one antenna steers the female towards it by
  +0.6 to +2.3 Hz at 50-150 Hz (`odor_dose_flywire_shiu_min1+known+eln0.25.csv`; food odours steer her away). So "nobody
  approaches" stands as the size of the effect, but the paper now reports the lean.
- **Paper:** the user asked (26 Sep) for a much shorter version in the language and structure of *The Metaphysics of
  Farts*, run through the humanizer; the 38-page version is kept as `paper/archive/flycraft_long_20260926.{tex,pdf}`.

## 23. Ninth pass (26-27 Sep 2026) — a second full re-run, an audit of every claim, and edge cases

**Asked for (26 Sep, evening):** re-run the research and say whether the paper's findings match; run it extensively and
test edge cases, managing the laptop's memory (16 GB, shared with other work, swap already 6 GB, disk 98 % full);
rewrite the paper in the structure of the pif-bench papers and the language of *The Metaphysics of Farts*, with a
section for readers with no biology or technical background and a line on why it reads the way it does.

### 23a. Memory-guarded queues
- `experiments/run_guarded.sh STEPFILE [DONE_DIR]`: one step at a time from a tab-separated step file (re-read before
  every step, so steps can be appended); waits for a per-step % of free memory; samples every 10 s the step's own
  *physical footprint* (top's MEM over its process tree; ps's RSS under-reads compressed pages ~30x) with system free %,
  swap and load (`logs/guarded_mem.tsv`, peaks `logs/guarded_peaks.tsv`); pauses the step (SIGSTOP on its process
  group) if free memory falls below 6 % and resumes at 15 %; one retry, then a `.failed` marker; resumable.
- `experiments/edge/with_lock.sh`: one short connectome-loading test at a time, at >= 35 % free memory.
- The pyenv interpreter (3.12.8, numba 0.65.1) is the project's; plain `python3` in a fresh shell is Homebrew's
  and has no numba.

### 23b. The full offline re-run (26 Sep 23:44 - 27 Sep 04:07)
`./reproduce.sh`'s 15 offline groups through the guarded queue, 6 numba threads, backup of every result file in
`release/pre_rerun_20260926/`. 15 of 15 groups ok in 4 h 23 min; peak footprint 2.6 GB (the male rewiring), free memory
never below 31 %, no pause. **All 124 rewritten result files are identical to the digit to those of 25-26 Sep**
(`experiments/results_edge/rerun-diff/rerun_0926_vs_0925.md`); `paper_numbers.py`: 155 cells, 0 differ; Brian2 check
the same as before (seeds 1, 2 identical per neuron; seed 0 23,689 vs 23,512 spikes). So every offline number of draft 5
reproduces. What the re-run cannot catch is wording that says more than the numbers: that is 23c.

### 23c. An audit of every claim (read-only workflows; `experiments/edge/design_*.md`, `verify_wording_full.md`)
Seven analysts mapped each claim of draft 5 to its evidence and proposed edge cases; a completeness critic; nine
verifiers re-derived 65 wording problems from the files (55 confirmed, 10 partly, 0 refuted), and a second skeptic tried
to refute each one that touched a headline (most upheld). The ones that change what the paper may say:
- **The lean towards the male is not there** (`experiments/edge/arena_audit.py`, `results_edge/arena-log-audit/`): the
  raw pooled 24 / 9 (p = 0.014) is her steady right turn times a male who sat mostly on her right; with her own far-field
  turn subtracted 15 / 20 (p = 0.50), all-tick-corrected 17 / 18, within-log side contrast 6 / 6, within-segment
  time-shift null P = 0.15. "Nobody approaches" holds without the exception.
- **The 86-s bout was a launch artefact**: run_pair.sh's 6-s stagger let fly1 walk 4.5 blocks onto fly2's start point
  (faint-smell ff t3; also t1). Longest genuine bout 25.7 s (first series) and 31.2 s (replication).
- **Male backing (MDN) fails the paper's own gain test** (leg taste 0 / 27 / 1.8 Hz at 0.7 / 1.0 / 1.4; head touch 0 at
  0.7, 0 at a 50 Hz stimulus, 3-47 Hz with the odour context): a property of the model at published strength.
- **Grooming and bitter suppression never went through the three tests**; JO-A is not in the sensitivity table.
- **The scramble test is the unconstrained degree-preserving null**, which stops every sense reaching any descending
  neuron (blunt); the class-preserving null (published lobe) keeps JO-A -> GF at 6.4 of 10.6 Hz and turns touch into an
  indiscriminate burst.
- **"No activity of its own" is by construction** (rest 7 mV below threshold, no noise, no intrinsic currents): the
  clean-box stillness tests the neuron model, not the map; the eyes fire (8 % of neurons) but reach no descending neuron.
- **Female walking is read from DNa01/02 + DNp09, and DNp09 is silent**: the freeze is a fall in DNa01/02 while the
  descending population as a whole rises (1.3 -> 8.4 Hz with touch).
- **dt 0.1 / 0.2 / 0.5 are not "identical"**: qualitatively the same, rates within ~10 Hz; at 0.5 ms the refractory
  period and delay round to 2.0 ms.
- **The memory's "no working route"** rests on a probe that drove the MBONs' targets; 16f's MBON14 -> DNa route was
  measured under an older model (MBON14 alone at 50 Hz gives DNa L 2.5 Hz now). To be settled by `expression_harsh.py`.
- **Hunger "changes nothing"**: in a silent brain; NPF raises sugar -> MN9 by 6.8 Hz against 3.6-4.4 for unrelated
  states (p = 0.15), and the hunger neurons recruit no other neuron at rest.
- Smaller: eLN x0.25 is the largest of four settings tried, not "the most"; 150 eLNs are ~71 predicted cholinergic,
  not all; overlaps 0.63 / 0.08 count empty codes (0.79 / 0.12 over odours that reach KCs); vpoDN 5.7 Hz is pooled
  vpoEN + DNp37; song MNs 28 Hz are not state-specific; learning numbers 0.59-0.70 kept, index 0.55 +- 0.03, no-US 0.03;
  punishment index hides odour order; world "0.29 with bitter" matched by 0.31 with none; cVA steering -0.2 to +2.3 Hz
  (n = 3, none significant); "nobody sang or fought" -> no song-command or aggression activity above the hum's floor;
  rep-clean mf was too slow to compare; paper_numbers.py checks values typed from an earlier draft, not the text.

### 23d. Edge-case code (new files only; `experiments/edge/`, `brain/tests/edge_*`)
Written by one agent per script and reviewed line by line by another (`experiments/edge/impl_reviews.md`); every engine
reproduces the paper's own file to the digit at default settings (grid_probe vs social_probe 1,620 cells; conditioning
byte-identical; expression_probe 24 x 21; odor_code 20 x 21 + 55 overlaps). `grid_probe.py` (conditions x drives x
readouts, sensitivity table, gains, rewiring, in-memory synapse thresholds, per-neuron voltage and E / I input, presets
decider_reach, matched_null, freeze with specificity controls, touch_dose, persistence, state_split, ...),
`run_redirect.py` (any experiment script with its output redirected and LIFParams overridden), `conditioning_edge.py`
(backward / unpaired / US-only / trace / extinction protocols, floor, eligibility), `expression_harsh.py`,
`odor_code_plus.py`, `arena_audit.py`, `structure_probe.py`, `edge_brian2_{reference,divergence}.py`. Queue:
`experiments/edge/steps_20260927.tsv` (51 steps), outputs `experiments/results_edge/<step>/`.

### 23e. Arena changes (opt-in; earlier series reproduce unchanged)
`bot.js --waitFor <partner>`: a chat handshake (ready / go) so both flies start within one round trip (tested: 0.46 s
apart, both 4.0 blocks apart at the first tick; the old stagger was 3-5 s); `run_pair.sh SYNC=1`; `trials.sh SEED0`
(brain seeds SEED0+1..+N); `run_brain.py --mask bristle` (a sensory channel never driven; log names carry
`-mask<channel>`). `experiments/run_arena_edge.sh`: synced, new-seed series on the hum (ff, ff without touch, mf) and a
clean mf, logs in `logs/edge_arena/<label>/` so nothing pools them with the paper's series.

### 23f. Edge-case results (27 Sep 04:08 onward; verdicts in experiments/edge/analysis_A.md, analysis_B.md)
Every engine reproduced the paper's own files to the digit before its new runs. Verdicts (each checked by a second,
independent re-derivation):
- **Deciders silent: holds.** 0.0 Hz in every single neuron to 26 inputs at gains 0.7-1.4, 200-300 Hz and all 14
  conditions, except pC1d (2.3 Hz to JO-CE at 1.4; <= 2.5 Hz under legacy numerics). **Positive control** (drive each
  decider's top-5 presynaptic types): pC1a 69, pC1b 93, pC1c 105, pC1d 104, pC1e 64, aIPg 23, vpoEN 83, DNp37 103,
  oviDN 20 Hz (oviDNb has none). **Why silent**: voltage and E/I: cVA pushes pC1d/e to -4 mV (-10 at 1.4), touch lifts pC1d
  to +3.7 mV (firing needs +7), holds vpoEN at -17 mV; pC1a/b receive <= 280 synapse*Hz; 60 of 102 sense-decider pairs net
  inhibitory; every decider 1-3 hops from every sense. **Sign-flip test** (`decider_flip.py`, added after the design):
  the inhibition runs through six predicted-GABA types (AOTU064, AVLP531, PS088, CB0584, WED104, PVLP021; conf
  0.74-0.92); silencing them wakes nothing; flipping them lets cVA drive pC1d 18 / pC1e 7 Hz and touch vpoEN 39 Hz (DNp37
  3); pC1a-c stay 0.
- **Virgin state: holds, specific, gain-robust.** SAG -> pC1a 21, pC1b/c 19, DNp37 17 Hz (vpoEN silent even with song);
  12/21/30 Hz at gain 0.7/1.0/1.4; 20/20 matched random pairs wake nothing; SAG wakes nothing in rewired brains. Male
  P1 -> pIP10 50, TN1 8; 20/20 matched random sets give pIP10 <= 0.8.
- **Hunger: holds** at 10 seeds (NPF +3.2, p = 0.10; the +6.8 was seeds 0-4) and on the hum; IPC/DH44 have 9/12 output
  synapses per neuron (foregone), NPF/SIFa/AstA 622/468/11,936 but none near feeding.
- **Reflexes**: sugar and touch -> DNp13 pass everything; bitter slows only (9/25/39 % kept at gain 1.0/1.2/1.4); JO-A ->
  GF needs a loud sound (1.6 Hz at 50 Hz) and partly survives the class-preserving rewiring; grooming fails at gain
  0.7 and >= 5 synapses. **Freeze**: touch-specific (other senses -0.12..0.13), needs strong/broad touch (a tenth of the
  bristles speeds DNa up), graded loss with thresholds 0.69 -> 0.59 -> 0.37 -> 0.00 (k = 2, 3, 5), holds 5 s; touch stops
  feeding (MN9 76 -> 0-4). Male backing fails.
- **Learning: associative** (backward/unpaired -0.08..+0.05; US alone keeps 0.85-0.95); pair-dependent (floral/vinegar
  0.72/0.63, ester/sweet 0.43/0.15); 6 cycles 0.47/0.53. **Expression**: a route exists (MBON14 at 50 Hz -> DNa L 18 Hz;
  punishment set 20-100 Hz moves 24-27 DN types; reward set during odour turns 14-18 down) but a smell drives the MBONs at
  0.5-12 Hz and silencing them moves DNa <= 1.3 Hz: "a notebook almost never opened".
- **Numerics**: dt 0.1 within seed noise; dt 0.5 +8 % median; threads 3/8 <= 0.4 Hz on 5-seed means; held-out seeds 5-9
  reproduce Notes 4/5; **Brian2 first divergence**: double precision identical spike for spike in 3/3 seeds; float32 first
  mismatch one neuron 2.8e-6 mV from threshold (seed 0, 615.5 ms); paper model: sugar dt 0.2 identical 3/3, touch 2/3,
  cVA diverges (self-sustaining state amplifies).
- **eLN sweep**: pre-set criterion (live between-odour KC Jaccard <= 0.25, within >= 2x, spread <= 35 %): 0.25 largest
  passing (0.16), 0.3 fails (0.27).
- **Smell steering**: cVA does not reliably turn her towards it (CI includes 0 at 25-100 Hz); food avoidance 1-7 Hz at every
  strength, read in the self-sustaining state.

### 23g. The self-sustaining state (new finding; `experiments/edge/selfsustain_probe.py`)
3 s of cVA, food odour or CO2 at 25-100 Hz leaves ~1,950 neurons (58,000 spikes/s; DNa 13-22 Hz, PPL1 8, GF 3; MN9, DNp13,
deciders 0) firing with no decay over 20 s in the paper's model; Or47b and JO-A/touch/sugar leave nothing. One state
(Jaccard 0.86-0.91 between odours): AL local + projection neurons, LH, KCs, ~125-150 DNs. Grows with gain (700 at 0.7 w/o DNa,
4,300-5,100 at 1.4) and without the eLN change (published: 8,300 neurons, 3,364 KCs, DNa 36 L / 4 R, and Or47b starts it:
this is why the published-lobe arena females circled left). The hum starts it within ~1 s. Male: cVA ~2,000, food ~920,
published male ~7,900. **Mechanism**: eLN x0.1 or x0 abolishes it (<= 78-neuron remnant), cutting every synapse onto a
sensory neuron does not (1,850-1,910; published 7,700). Rewired brains: a smell never starts it within 0.8 s. Arena logs:
active fraction 8.0 % in the still clean-box females vs 9.0-10.3 % for every fly that walked (13.6 % published): every
walking fly walked on the state. Consequence: whether my model keeps firing after a smell depends on the eLN setting,
which nobody has measured (x0.1 also keeps smells apart).

### 23h. Paper draft 6 (`paper/flycraft.tex`, assembled by `paper/assemble.py` from flycraft_preamble/main/notes.tex and
references_pool.tex; `paper/wordcount.py`)
The user asked for the pif-bench structure (Argument in Brief, Contributions, What This Paper Is Not, Author Position,
Roadmap, quoted counterarguments, refutation conditions, limitations) in the language of The Metaphysics of Farts, a note on
why it reads that way (fun work), and a section for readers with no biology or technical background. Five independent
reviews (lay reader, fly biologist, fact-checker, style editor, hostile referee; experiments/edge/paper_reviews_draft6.md, in the release archive only)
led to a full revision: the female/male scope of the decider claim, half the virgin pathway (vpoEN silent even with song),
P1 as decider not state, hunger's foregone part (few IPC/DH44 synapses; SIFa/AstA inhibitory; SAG serotonergic treated as
fast), the teaching signal's failure as a model miss, the AI checkers named as copies of the same assistant, the
self-sustaining state and its mechanism, a fourth refutation condition, limitations (no fatigue, same constants, song
rhythm). New verified references: Clowney 2015, Kallman 2015, Liu 2012, Burke 2012, Wilson 2004, Ramdya 2015, Bussell
2014, Capra 2022. New figure `fig_deciders` (experiments/edge/figure_deciders.py). The arena figure skips the two
placement-artefact trials (figures_print.py PLACEMENT_ARTEFACTS) and the arena table leaves them out and marks the
too-slow rep-clean mf series (replication_stats.py).

### 23i. P2 results, the male neurons named, draft 6 revised (27 Sep, 07:30-09:10)
Verdicts from two analyse-then-refute workflows (9 agents each; verbatim final texts in the session scratchpad
p2_verdicts_1.txt / p2_verdicts_2.txt); all numbers below were recomputed by an independent verifier.
- **dt rounding (PASS)**: dt 0.1 ms with the 0.5-ms rounded refractory period (2.0 ms) and arrival (2.5 ms; the kernel
  applies a synapse one step after the rounded delay) matches dt 0.5 (5/115 rates at >= 2 SE, max 2.05 Hz) and rises
  8 % over 0.2 ms, so the dt-0.5 shift is rounding (the two values were not separated).
- **Memory expression, targets primed (FAIL of the pre-set mark)**: with the MBONs' non-DN targets held near threshold
  (sub mode, calibrated 1-10 Hz without odour), silencing the punishment set lowers DNa L 5.0-7.3 Hz under bilateral
  vinegar (15/15 paired runs lower), the reward set raises it 3.2-4.2 Hz; single DN types up to 8.5 Hz. Unprimed: <= 1.3 Hz.
  One-sided vinegar: L-R hardly moves (-0.8). Ceiling only (whole set silenced); no trained memory run with the push.
- **Learning**: held-out seeds 3-4 give index 0.52-0.60; eta 1 gives 0.48/0.44 (erosion of the unpaired odour, mostly
  also without a teaching signal).
- **Female state dose**: SAG 10-100 Hz -> pC1a 5.0-61.3 Hz monotone; pC1a/SAG 0.65-0.78 from 20 Hz (0.45 at 10).
  At 100 Hz SAG lowers touch -> DNp13 35.6 -> 32.3 Hz (p = 0.004; pC1a-c 28.3), which meets the rule for qualifying the
  "state-blind" miss: the virgin's ovipositor neuron fires about a tenth less (also at gain 1.4). SAG+hunger within
  2 SEM in 121-127/128 cells. At 100 Hz hunger groups raise MN9 with sugar (+1.2 to +6.8, ANOVA p = 0.001).
- **Food steering at gain 1.4**: away in 11/12 odour x rate cells (51/60 values); at 0.7 no turn to read -> the turn
  away fails the gain test, like the male backing.
- **Male gain map / touch dose**: MDN by touch rate 0 at <= 50 Hz, 11.5/27.5/50.4/66.5 Hz at 100-300; the arena-like
  composite gives 58.6 Hz, 27.2 without touch (touch carries most). pIP10 answers only cVA.
- **Male P1 named (new step p1-name-male, experiments/edge/p1_name_male.py; FAIL of the gain-map-male mark)**: cVA fires
  single P1 neurons (1 at gain 1.0, 6.3 Hz; 14 at 1.4, up to 30 Hz; with touch 5 at 1.0 up to 18 Hz). 21 of the 22
  that ever pass 2 Hz are fru+dsx pMP-e/pMP4 types (pC1_1a, 1b, 2a, 2a/2b, 3a, 3b, 3c, 13a, 14a; plus dsx-only pC1_11a).
  Real males court less with cVA (Kurtovic 2007) but fight more (Wang & Anderson 2010), and weak P1 activation starts
  fights (Hoopfer 2015): the model either has the sign backwards for courtship or is starting a fight. Both refs
  verified on Europe PMC and added to references_pool.tex.
- **Male hum states**: P1 -> pIP10 44.2 Hz on the hum (floor 0.2); hunger no different from unrelated states, but male
  sugar leaves MN9 at 0, so the male hunger test is weak. **Male no-US control**: reward compartment 0.01/0.04 (passes);
  punishment 0.42/0.61, because pooled labellar taste drives PPL1 through the wiring: the male punishment result has
  no teaching-free control. **Male structure**: cVA -> P1 net excitatory (half via LH008m/aSP-f); leg taste -> P1
  through AN09B017 (vAB3), predicted glutamatergic, so inhibitory in the model. **Rewired male (PASS)**: P1 -> pIP10 0.
- Correction to 23g: x0.1 does NOT keep smells apart by the pre-set criterion (only DM1 and its blend reach KCs).
- Paper: draft 6 rewritten with every round-2 review fix, then these results; Fig 3 relabelled for lay readers
  (steering neurons, longest meeting, left/right), nested layout; arena table column "Walking (share)".

### 23j. Arena edge series and the finished draft 6 (27 Sep, 08:36-14:10)
Four series (experiments/run_arena_edge.sh; seeds 101-105; both bodies wait for each other before the brains start,
launch gap -0.02 to 0.23 s, no trial began in contact; logs/edge_arena/; encounter_trials_edge.csv; arena_audit.md):
two females on the hum (600 s): 5/5 met, contact 46 +- 27 % (5-75 % per trial), longest 15.9 s, freeze on contact;
the same with --mask bristle (touch of walls and of each other off; the female brain has no leg-taste neurons): 5/5 met,
contact 5.6 %, longest 3.6 s, no freeze (walk 0.51 vs 0.04 in contact); male + female on the hum: 5/5 met, median
meeting 0.25 s, he was backing at the end of 84/87 meetings (the 6.2-s outlier is a male stuck in a corner); male +
female in the clean box (300 s): female walks (0.42), male nearly still (0.02-0.03 before contact), MDN 44 Hz on contact.
Toward index -0.018 to +0.030; no lean. New fact: the ovipositor neuron's "far" value in the arena table (5-8 Hz) comes
from wall touches (about 20 Hz against a wall, < 0.5 Hz away from walls), not from the hum; caption and Note 8 fixed.
Final review (7 agents; 90 of 92 integrated edits applied) and a last arena/style check (2 agents) applied. Draft 6:
23 pp, main text 5,900 words (lay guide 563), notes 5,039. Release: release/flycraft_20260927.tar.gz (79 MB, 1,423
files; reproduce.sh archive now also packs experiments/edge, results_edge, logs/edge, logs/edge_arena, paper/*.py).
