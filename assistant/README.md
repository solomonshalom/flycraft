# The research assistant — follows, guides, and takes notes on the flies

A second kind of bot in the world: not a fly, a **field assistant**. It runs entirely on this laptop (a local
language model through Ollama; no cloud, no keys) and does three things:

| | how | where |
|---|---|---|
| **follows** | joins the server as a spectator named `observer`, hovers behind the chosen fly (or the nearest one), watches contacts, songs, proboscis extensions, rejections, hurts, joins/leaves | `scribe.js` |
| **guides** | stages what the agenda needs: `bring fly2 to fly1` (put one fly in front of another, facing it), `food fly1` (a poppy 3 blocks ahead), `clear fly1` (remove food around it), `summon sheep near fly1`, `time night`, `follow fly2` | `scribe.js` + `assistant.py act()` |
| **takes notes** | every epoch: a deterministic table (walked, walk duty, turn bias, acts, top readouts in Hz, senses, nearest fly) + an event list (contacts, bursts of DNp13/pC1/P1…, acts, approaches) from the brains' CSV logs; then the model's short *reading*, tagged with the agenda item it bears on | `fieldnotes.py`, `agenda.py`, `assistant.py` |

**It keeps the paper agenda.** `agenda.py` reads the `## Agenda` section of `RESEARCH_NOTES.md` (title, question,
H1–H4, aims A1–A5) and section 15's "what must still be done" list (T1–T6). Every event is tagged by rule
(contact/approach → A4/T1, social readout bursts → H2, feeding/escape → H1, `--plasticity mb` runs → A2/H3,
`--state` runs → A3/T2), every model note names its agenda items, the header of each notes file says which items
the trial serves, the whole-trial block says what the trial contributed and how far it is from the n ≥ 5 bar, and
`agenda` (in the terminal or in chat) prints the agenda with the running tally. Edit the agenda in
`RESEARCH_NOTES.md` and the assistant follows.

The flies cannot sense it: `bot/observe.js` treats players named `observer*`/`scribe*` (or rostered as `"ghost"`)
as ghosts (no vision, no CO₂, no touch), and a spectator has no collision box. It never emits ♪ and never touches
a human player.

## Run
```
ollama serve                                   # once; the default model is qwen3:4b (2.5 GB; gemma3:4b also works via --llm)
experiments/run_flock.sh "f,m" wild            # the flies, as usual
python assistant/assistant.py --trial flock --world wild --follow fly1        # notes -> notes/field_flock_<stamp>.md
```
Options: `--interval 60` epoch length (s), `--llm off` (deterministic notes only) or `--llm gemma3:4b --llm-loose` etc. (gemma answers better without the JSON grammar),
`--no-body` (notes only, no bot), `--distance 4 --height 2` (hover offset), `--append-research-notes` (add the
trial summary to `RESEARCH_NOTES.md` at the end), `--logs a.csv b.csv` to name the logs (default: the newest log per
rostered fly modified in the last 15 min), `--idle-exit 120` (stop when the logs stop growing).

Offline, over any finished logs (also the quickest way to see what it writes):
```
python assistant/assistant.py --replay logs/fly1_off-flywire_X.csv logs/fly2_off-malecns_X.csv --window 60
python assistant/fieldnotes.py logs/fly1_off-flywire_X.csv --window 60      # the deterministic part alone
python assistant/agenda.py                                                  # the agenda as it sees it
```

Talk to it: type in its terminal, or chat in Minecraft as any non-fly player. Deterministic commands
(`agenda`, `status`, `follow …`, `bring … to …`, `food …`, `clear …`, `summon … near …`, `time …`, `note <text>`,
`quit`) work without a model; anything else goes to the model, which answers in ≤ 60 words and may propose one of
the same actions — proposals are validated (`act()`: only flies, a whitelist of blocks and mobs) before the body
carries them out. Chat replies never contain ♪.

## What is the record and what is the model's
The tables and event lists are arithmetic on the logs (`fieldnotes.py`) — rates per second of *brain* time, so
they are comparable across runs whatever the wall-clock speed. The indented "Reading of epoch N" lines are the
model's interpretation and are labelled with the model name; a 4B model paraphrases loosely and can mis-tag, so
treat them as a first draft. `context.md` is the standing knowledge it is given (established results, the
left-turn artifact, the robustness rule) — edit it when the science moves. Prompt cost: ~2.5k tokens per reading;
the system prefix is byte-stable so Ollama reuses its cache; generation is capped at 350 tokens.

## Files
`scribe.js` body · `fieldnotes.py` log analysis · `agenda.py` agenda + tagging · `llm.py` Ollama client ·
`context.md` standing knowledge · `assistant.py` the loop. Notes go to `notes/` (not in git); the body's stdout to
`logs/assistant_<trial>_body.out`.
