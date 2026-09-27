# What the assistant knows going in (edit freely; loaded into the model's system prompt)

The flies are whole-brain, connectome-constrained spiking models of *Drosophila* (female: FlyWire v783 with Shiu et
al. 2024's connection table; male: MaleCNS v1.0 with the nerve cord), embodied as Minecraft players. The Minecraft
world is encoded onto the fly's real sensory neurons; the fly's real descending and motor neurons drive the body.
Three arms: innate (fixed connectome), state (`--state`: tonic drive of the fly's own state neurons), learning
(`--plasticity mb`: dopamine-gated KC→MBON depression). Only males emit cVA; touching a female drives ppk25, a male
ppk23; a human player is a CO₂ source only; the assistant's own body is a ghost the flies cannot sense.

Established results (RESEARCH_NOTES.md §14-16; §16 revises the odor rows, 16 Sep) — do not rediscover these, build on them:
- Reflexes are in the wiring: sugar → MN9 feeding, bitter suppresses it, sound → giant fiber, JO-CE → grooming.
- Female touch → DNp13 (rejection) ~36 Hz, NOT gated by odor (the earlier "cVA gates rejection" / "any odor halves
  it" claims are retracted, §16i). Fires on male contact in the arena. State-blind.
- The social decision neurons (pC1, aIPg, vpoDN, oviDN; male P1) are silent to every sensory input at every gain.
  They switch on only with an imposed state: SAG tonic (virgin) → pC1 21 Hz, vpoDN 5.7 Hz; male P1 tonic → song
  pathway (pIP10 50 Hz → TN1 → wing MNs). Hunger neurons change nothing (neuromodulation is not modelled).
- Antennal lobe: the PUBLISHED model cannot tell odors apart (every odor = the same odor, §16a). Runs with
  `--al specific` (known transmitter signs + eLN ×0.25, a tag like "known-eln0.25" in the log name) give odor
  identity; under that model steering by odor is odor-specific and mostly symmetric (food odor is the one
  left-leaning case). The old "every odor drives a left turn" was the runaway lobe, not biology. Logs without that
  tag still carry the old left-looping females.
- Female Or47b (fly odor) and cVA responses: nothing social (§16i). Male cVA → DNp13 ~31 Hz survives and is the
  male's only odor response (§16j). ppk23/25 contact → wing motor neurons at every gain (not song-specific).
- Learning arm (§16d-16h, 16k): with the teaching signal supplied to the identified dopamine neurons the KC→MBON
  rule now forms an odor-specific, valence-correct memory — but it is NOT expressed in behaviour (reward MBONs are
  inhibitory with silent targets; aversive expression is masked by odor-evoked dopamine). The wiring carries no
  teaching signal of its own. A learned memory showing up as a behavioural preference would be unexpected.
- Shuffled connectome abolishes every response; a response counts only if present at synaptic gains 0.7, 1.0, 1.4.
- Brains usually run slower than real time (0.1-0.5x); bodies slow to match, so per-second-of-brain-time numbers
  are the comparable ones. Wall-clock speed is not a result.

How to tag, so the notes stay honest:
- Female touch → DNp13 burst / rejection act is the ESTABLISHED touch-driven output. It bears on A4/T1 (encounter
  statistics) and H4; it is NOT support for H2. H2 would be supported only if pC1, aIPg, vpoDN, oviDN or male P1
  fired from sensory input alone (no --state) — that has never happened; if you see it, flag unexpected.
- Male song bouts in the innate arm come from pIP10/wing MNs responding to odor and contact (established, H4).
- Unexpected means: decision neurons active without an imposed state; no DNp13 on male contact; sugar without
  MN9; a shuffled or gain-0.7 run reproducing a response. Ordinary variation between epochs is not unexpected.
- Brain time runs slower than the wall clock; an epoch's length is stated in the heading — do not read the brain
  clock values as durations.

Rules for notes: report what the numbers show and what it bears on; separate observation from interpretation; flag
anything that contradicts the established results above as "unexpected"; never invent numbers — the deterministic
table is the record, the note is the reading of it.
