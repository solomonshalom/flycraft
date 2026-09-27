# flycraft

*What Does a Fly's Wiring Know? A Fruit-Fly Brain in Minecraft*

I rebuilt the published simulation of a whole fruit-fly brain, one model neuron for each of the roughly 139,000 real ones, changed two things in its smell centre, and gave it a body in Minecraft. Then I asked what the wiring alone knows about meeting another fly, and tried hard to break every answer.

The wiring knows how to react but not what it wants. The simulated fly works her mouthparts on sugar and holds out her ovipositor when her head is touched. The senses send mostly "no" or nothing to the neurons that decide whether to accept a male or fight. Keeping her two virgin neurons firing wakes her acceptance neurons, while keeping her hunger neurons firing does no more than keeping an unrelated group firing. Once I supply the teaching signal her taste fails to send, a memory forms, and she hardly ever uses it. Two flies in a box do not steer towards each other. Two females that bump into each other freeze on contact, and that is what keeps them together.

This one was fun to do, so the paper reads like an essay, in the manner of Bill Capra's *The Metaphysics of Farts*, though the tests are as strict as in my other papers. It has a section for readers with no biology.

- Paper: [`paper/flycraft.pdf`](./paper/flycraft.pdf) (LaTeX source: [`paper/flycraft.tex`](./paper/flycraft.tex))
- Author: Solomon Shalom Lijo (Independent Researcher)
- Contact: solomon@getromy.app
- License: [CC BY 4.0](./LICENSE)

## What's here

```
paper/            the paper; assemble.py puts flycraft.tex together from flycraft_preamble.tex,
                  flycraft_main.tex, flycraft_notes.tex and references_pool.tex
brain/            the brain: a numba rebuild of Shiu et al.'s (2024) model on FlyWire (female) and MaleCNS (male)
bot/              the body: a mineflayer bot that tells the brain what the fly senses and moves the way
                  its descending neurons say
experiments/      every probe, arena run and figure script, with the result files the paper cites
server/           scripts that fetch and set up a local Paper 1.20.4 server
assistant/        a side tool: a spectator bot that takes field notes with a local model (the paper does not use it)
reproduce.sh      the command behind every result file
RESEARCH_NOTES.md the lab notebook
```

## Running it

The connectome files are too big for the repo. They go in `data/`, and the top of `brain/flybrain/connectome.py` and `brain/flybrain/malecns.py` lists each file and where it comes from (FlyWire v783 through Shiu et al.'s table, Schlegel et al.'s annotations and Dorkenwald et al.'s Zenodo table, MaleCNS v1.0).

```bash
pip install numpy scipy pandas pyarrow numba websockets matplotlib
./reproduce.sh list        # every result group and the command that makes it
./reproduce.sh all         # the offline study (about 4.5 h on an M4 MacBook with 16 GB)
cd paper && ./build.sh     # the PDF (tectonic, or pdflatex twice)
```

The paper's runs used Python 3.12.8, numba 0.65.1, numpy 2.4.4, scipy 1.17.1, pandas 3.0.2 and pyarrow 25.0.1, with `NUMBA_NUM_THREADS=6`. Offline results reproduce to the digit on the same numba version and thread count. The Brian2 check in `core-check` wants its own venv (`python3 -m venv b2venv && b2venv/bin/pip install brian2 numpy cython`), and the arena logs that the figures step reads are too big for the repo, so they go in the release archive.

For the Minecraft side you need Java 17 or newer and Node 22 or newer. Run `ACCEPT_EULA=1 server/setup.sh` and `(cd bot && npm install)` once, then in three terminals `./run.sh server`, `./run.sh brain fly1 8765 off --al specific` and `./run.sh bot fly1 8765 3007 --build-arena`.

An AI coding assistant helped write the code and drafts of the paper, and copies of it checked the claims against the result files. Nobody outside the project has checked the work yet.

## Citation

```bibtex
@misc{shalomlijo2026flycraft,
  author       = {Shalom Lijo, Solomon},
  title        = {What Does a Fly's Wiring Know? A Fruit-Fly Brain in Minecraft},
  year         = {2026},
  howpublished = {Preprint},
  note         = {Forthcoming. Source available at \url{https://github.com/solomonshalom/flycraft}}
}
```
