#!/usr/bin/env python3
"""The research assistant: follows the flies, guides them, and keeps field notes tied to the paper agenda.

Live, next to a running flock (brains + bots already up; see experiments/run_flock.sh):
    python assistant/assistant.py --trial live --world wild --follow fly1            # notes -> notes/field_live_<stamp>.md
Offline, over finished logs:
    python assistant/assistant.py --replay logs/fly1_off-flywire_X.csv logs/fly2_off-malecns_X.csv --window 60

What is deterministic and what is the model's: the per-epoch table and event list come from assistant/fieldnotes.py
(arithmetic on the brains' CSV logs and the body's snapshots — the record). The local language model (Ollama,
default qwen3:4b; --llm off to disable) only writes the short reading under each epoch, answers questions, and
proposes guidance; every proposal is validated here before the body carries it out.

Talk to it while it runs: type in this terminal, or chat in Minecraft (any non-fly player).  Commands it understands
without a model:  agenda | status | follow <fly|nearest|none> | bring <fly> to <fly> [blocks] | food <fly> [blocks]
| clear <fly> | summon <entity> near <fly> | time day|night | note <free text> | quit.  Anything else is a question
for the model, which may answer with one of the same actions.
"""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import fieldnotes as fn                      # noqa: E402
from agenda import Agenda, contribution, load_agenda, run_focus, tag_event   # noqa: E402
from llm import DEFAULT_MODEL, LocalLLM      # noqa: E402

NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "note": {"type": "string"},
        "agenda_items": {"type": "array", "items": {"type": "string"}},
        "unexpected": {"type": "boolean"},
        "suggestion": {"type": "string"},
    },
    "required": ["note", "agenda_items", "unexpected", "suggestion"],
}
ACTIONS = ["none", "follow", "bring", "place_food", "clear_food", "summon", "time"]
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "actions": {"type": "array", "items": {
            "type": "object",
            "properties": {"action": {"type": "string", "enum": ACTIONS}, "who": {"type": "string"}, "to": {"type": "string"},
                           "dist": {"type": "number"}, "block": {"type": "string"}, "entity": {"type": "string"}, "value": {"type": "string"}},
            "required": ["action"]}},
    },
    "required": ["reply", "actions"],
}
SUMMARY_SCHEMA = {"type": "object", "properties": {"summary": {"type": "string"}, "next_step": {"type": "string"}, "agenda_items": {"type": "array", "items": {"type": "string"}}},
                  "required": ["summary", "next_step", "agenda_items"]}


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def hms(t: float | None = None) -> str:
    return time.strftime("%H:%M:%S", time.localtime(t))


# --- the body ---------------------------------------------------------------------------------------------------
class Scribe:
    """Runs assistant/scribe.js and talks to it over its local WebSocket."""

    def __init__(self, name: str, port: int, roster: str, follow: str, ws_port: int, distance: float, height: float, out_path: str):
        self.name, self.ws_port = name, ws_port
        self.snapshot: dict | None = None
        self.events: queue.Queue = queue.Queue()
        self.results: dict[int, dict] = {}
        self.ids = itertools.count(1)
        self.ws = None
        self.lock = threading.Lock()
        cmd = ["node", os.path.join(HERE, "scribe.js"), "--name", name, "--port", str(port), "--follow", follow,
               "--ws", str(ws_port), "--distance", str(distance), "--height", str(height)]
        if roster:
            cmd += ["--roster", roster]
        self.out = open(out_path, "a")
        self.proc = subprocess.Popen(cmd, cwd=ROOT, stdout=self.out, stderr=subprocess.STDOUT)
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        from websockets.sync.client import connect
        deadline = time.time() + 90
        while self.proc.poll() is None:
            try:
                with connect(f"ws://127.0.0.1:{self.ws_port}", open_timeout=3) as ws:
                    self.ws = ws
                    for raw in ws:
                        m = json.loads(raw)
                        if m.get("type") == "snapshot":
                            self.snapshot = m
                        elif m.get("type") == "event":
                            self.events.put(m)
                        elif m.get("type") == "result":
                            self.results[m.get("id")] = m
            except Exception:  # noqa: BLE001  (body not up yet, or gone)
                self.ws = None
                if time.time() > deadline and self.snapshot is None:
                    print(f"[assistant] no connection to the body after 90 s; see its log", flush=True)
                    deadline = float("inf")
                time.sleep(2)

    def cmd(self, name: str, timeout: float = 6.0, **kw) -> dict:
        if self.ws is None:
            return {"ok": False, "msg": "body not connected"}
        i = next(self.ids)
        try:
            with self.lock:
                self.ws.send(json.dumps({"id": i, "cmd": name, **kw}))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "msg": f"send failed: {e}"}
        t0 = time.time()
        while time.time() - t0 < timeout:
            if i in self.results:
                return self.results.pop(i)
            time.sleep(0.05)
        return {"ok": False, "msg": "no reply from the body"}

    def say(self, text: str):
        for chunk in re.findall(r".{1,240}(?:\s|$)", text.strip()) or [text[:240]]:
            self.cmd("say", text=chunk.strip())
            time.sleep(0.3)

    def drain_events(self) -> list[dict]:
        out = []
        while True:
            try:
                out.append(self.events.get_nowait())
            except queue.Empty:
                return out

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.out.close()


# --- the notes file -----------------------------------------------------------------------------------------------
class Notes:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.f = open(path, "a", encoding="utf-8")

    def write(self, text: str):
        self.f.write(text.rstrip("\n") + "\n\n")
        self.f.flush()

    def close(self):
        self.f.close()


# --- the assistant --------------------------------------------------------------------------------------------------
class Assistant:
    def __init__(self, a: argparse.Namespace):
        self.a = a
        self.agenda: Agenda = load_agenda()
        self.context = open(os.path.join(HERE, "context.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "context.md")) else ""
        self.trial = a.trial
        self.roster_path = os.path.join(ROOT, "logs", f"roster_{a.trial}.json")
        self.roster = json.load(open(self.roster_path)) if os.path.exists(self.roster_path) else {}
        self.tails: dict[str, fn.LogTail] = {}
        self.states: dict[str, fn.ChannelState] = {}
        self.runs: dict[str, dict] = {}
        self.epoch_n = 0
        self.tag_counts: Counter = Counter()
        self.last_epoch_md = ""
        self.last_note = ""
        self.all_events: list[dict] = []
        self.totals: dict[str, list] = {}
        self.guidance_log: list[str] = []
        self.body_buffer: list[dict] = []        # body events waiting for the next epoch (chat is handled at once)
        self.running = True
        self.llm: LocalLLM | None = None
        if a.llm and a.llm.lower() != "off":
            llm = LocalLLM(a.llm, a.llm_url, strict=not a.llm_loose)
            ok, msg = llm.available()
            print(f"[assistant] model: {msg}" + ("" if ok else "  -> running without a model"), flush=True)
            self.llm = llm if ok else None
        self.jobs: queue.Queue = queue.Queue()
        self.inflight = 0                        # model jobs queued or running
        self._system_cache: str | None = None
        threading.Thread(target=self._llm_worker, daemon=True).start()
        self.notes = Notes(os.path.join(ROOT, a.notes_dir, f"field_{a.trial}_{stamp()}.md"))
        self.scribe: Scribe | None = None

    # ---- logs ----
    def attach_logs(self, paths: list[str]):
        for p in paths:
            t = fn.LogTail(p)
            self.tails[t.fly] = t
            self.states[t.fly] = fn.ChannelState()
            self.runs[t.fly] = {"fly": t.fly, "arm": t.meta["arm"], "dataset": t.meta["ds"], "state": t.meta["state"], "variant": t.meta.get("variant", ""), "path": p}
            self.totals[t.fly] = []
            if t.fly not in self.roster:          # sex from the log itself when there is no roster (replay)
                try:
                    with open(p, encoding="utf-8") as f:
                        head, first = f.readline().strip().split(","), f.readline().strip().split(",")
                    if "sex" in head and len(first) == len(head):
                        self.roster[t.fly] = first[head.index("sex")]
                except Exception:  # noqa: BLE001
                    pass

    def find_logs(self, fresh_min: float) -> list[str]:
        flies = list(self.roster) or sorted({fn.parse_log_name(p)["fly"] for p in glob.glob(os.path.join(ROOT, "logs", "fly*_*.csv"))})
        out = []
        for fly in flies:
            cands = sorted(glob.glob(os.path.join(ROOT, "logs", f"{fly}_*.csv")), key=os.path.getmtime)
            cands = [c for c in cands if not c.endswith("_spikes.csv")]
            if not cands:
                continue
            newest = cands[-1]
            age = (time.time() - os.path.getmtime(newest)) / 60
            if age <= fresh_min:
                out.append(newest)
            else:
                print(f"[assistant] {fly}: newest log is {age:.0f} min old ({os.path.basename(newest)}); skipping (use --logs to force)", flush=True)
        return out

    # ---- header ----
    def write_header(self, mode: str):
        flies = ", ".join(f"{r['fly']} ({self.roster.get(r['fly'], '?')}, {r['dataset']}, {r['arm']}{', state ' + r['state'] if r['state'] else ''}{', ' + r['variant'] if r.get('variant') else ''})" for r in self.runs.values())
        focus = run_focus(list(self.runs.values()), self.agenda)
        focus_txt = "; ".join(f"{i}: {self.agenda.get(i).text[:90]}" for i in focus) or "none identified"
        self.notes.write(f"# Field notes — trial `{self.trial}` ({time.strftime('%Y-%m-%d %H:%M')}, {mode})\n\n"
                         f"- Flies: {flies or 'none found'}\n"
                         f"- Assistant: {'body ' + self.a.name + ' following ' + self.a.follow + ' at ' + str(self.a.distance) + ' blocks' if self.scribe else 'no body (notes only)'}; "
                         f"model {self.llm.model if self.llm else 'off'}; epoch {self.a.interval if mode == 'live' else self.a.window} s\n"
                         f"- Paper: *{self.agenda.title}*\n"
                         f"- This trial serves: {focus_txt}\n\n"
                         f"Numbers in the tables are brain-time rates from the brains' CSV logs (assistant/fieldnotes.py); the indented "
                         f"'reading' under each epoch is the local model's interpretation and may be wrong.")

    # ---- one epoch ----
    def epoch(self, dfs: dict | None = None, wall_from: str = "", wall_to: str = "") -> str:
        self.epoch_n += 1
        sums, evs = [], []
        for fly, tail in self.tails.items():
            df = dfs[fly] if dfs is not None else tail.read_new()
            s = fn.summarize(df, tail.meta)
            sums.append(s)
            if s.get("ticks"):
                self.totals[fly].append(df)
            for e in fn.detect_events(df, self.states[fly], fly):
                e["tags"] = tag_event(e, self.runs[fly], self.agenda)
                evs.append(e)
        body_lines = self._body_events()
        evs.sort(key=lambda e: e["t"])
        for e in evs:
            self.tag_counts.update(e.get("tags", []))
        self.all_events += evs
        md = fn.epoch_markdown(self.epoch_n, sums, evs[:80] + ([{"t": evs[80]["t"], "text": f"… {len(evs) - 80} more events", "tags": []}] if len(evs) > 80 else []), wall_from, wall_to)
        if body_lines:
            md += "Seen from the body (wall clock):\n" + "\n".join(f"- {l}" for l in body_lines) + "\n"
        if self.scribe and self.scribe.snapshot:
            md += self._snapshot_line() + "\n"
        self.notes.write(md)
        self.last_epoch_md = md
        print(f"[assistant] epoch {self.epoch_n}: " + "; ".join(f"{s['fly']} {s.get('walked_blocks', 0)} blocks, {sum(s.get('acts', {}).values())} acts" for s in sums if s.get("ticks")) + f"; {len(evs)} events", flush=True)
        if self.llm and (self.epoch_n % max(1, self.a.narrate_every) == 0) and any(s.get("ticks") for s in sums):
            self._enqueue_narration(self.epoch_n, md)
        return md

    def poll_body(self):
        """Called every second: answer chat at once, keep everything else for the epoch."""
        if not self.scribe:
            return
        for e in self.scribe.drain_events():
            if e.get("kind") == "chat":
                if not e.get("is_fly"):
                    self.handle_message(e.get("who", "?"), e.get("text", ""))
            else:
                self.body_buffer.append(e)

    def _body_events(self) -> list[str]:
        if not self.scribe:
            return []
        self.poll_body()
        lines = []
        for e in self.body_buffer:
            k = e.get("kind")
            label = {"song": "sang (♪)", "feed": "proboscis extension (arm swing)", "reject": "rejection (off-hand swing)", "hurt": "was hurt",
                     "died": "died", "joined": "joined the world", "left": "left the world"}.get(k, k)
            lines.append(f"{hms(e['t'])} {e.get('who', '?')} {label}")
        self.body_buffer = []
        # collapse repeats
        c = Counter(lines)
        return [f"{l} ×{n}" if n > 1 else l for l, n in c.items()]

    def _snapshot_line(self) -> str:
        s = self.scribe.snapshot
        parts = [f"{f['name']} at ({f['x']:.0f},{f['y']:.0f},{f['z']:.0f}) on {f['block_below'] or '?'}" + (" [food here]" if f.get("on_food") else "") + (" [in water]" if f.get("in_water") else "") for f in s.get("flies", [])]
        pairs = ", ".join(f"{p['a']}–{p['b']} {p['dist']} blocks" for p in s.get("pairs", []))
        extra = []
        if s.get("humans"):
            extra.append("humans present: " + ", ".join(h["name"] for h in s["humans"]))
        if s.get("mobs"):
            extra.append("mobs near the followed fly: " + ", ".join(f"{m['name']} {m['dist_to_followed']}" for m in s["mobs"][:5]))
        return f"Body snapshot {hms(s['t'])}: " + "; ".join(parts) + (f"; distances {pairs}" if pairs else "") + (("; " + "; ".join(extra)) if extra else "") + f"; following {s.get('following')}."

    # ---- the model ----
    def _system(self) -> str:
        # byte-identical every call, so Ollama can reuse its prompt cache for this prefix
        if self._system_cache is None:
            self._system_cache = ("You are the research assistant of a neuroscience project, taking field notes on simulated fruit flies in Minecraft. "
                                  "Write like a careful lab notebook: short, concrete, no hype, no restating numbers already in the table. "
                                  "Tag notes with agenda ids (H1-H4 hypotheses, A1-A5 aims, T1-T6 to-do items) only.\n\n"
                                  f"{self.context}\n\nTHE PAPER AGENDA:\n{self.agenda.render(width=140)}\n")
        return self._system_cache

    @staticmethod
    def _condense(md: str, max_events: int = 28) -> str:
        """The record for the model: the table plus the most telling events (social first), never the whole list."""
        head, _, rest = md.partition("Events (brain s):\n")
        if not rest:
            return md
        ev_lines, tail = [], []
        for line in rest.split("\n"):
            (ev_lines if line.startswith("- ") else tail).append(line)
        def prio(l: str) -> int:
            if "burst" in l or "rejection" in l or "acceptance" in l or "lunge" in l or "egg" in l or "courtship" in l: return 0
            if "touching" in l: return 1
            if "within 2 blocks" in l or "apart again" in l: return 2
            if "proboscis" in l or "song bout" in l or "jump" in l or "lost health" in l or "teleport" in l: return 3
            if "hearing song" in l: return 9
            return 5
        keep = sorted(sorted(ev_lines, key=lambda l: float(re.match(r"- ([\d.]+)", l).group(1)) if re.match(r"- ([\d.]+)", l) else 0), key=prio)[:max_events]
        keep.sort(key=lambda l: float(re.match(r"- ([\d.]+)", l).group(1)) if re.match(r"- ([\d.]+)", l) else 0)
        dropped = len(ev_lines) - len(keep)
        return head + "Events (brain s):\n" + "\n".join(keep) + (f"\n- … {dropped} lesser events omitted" if dropped > 0 else "") + "\n" + "\n".join(l for l in tail if l.strip())

    def _enqueue_narration(self, n: int, md: str):
        # keep at most one narration waiting; a slow model must never make the notes fall behind
        with self.jobs.mutex:
            pending = [j for j in self.jobs.queue if j[0] == "narrate"]
        if pending:
            return
        self.inflight += 1
        self.jobs.put(("narrate", n, self._condense(md)))

    def _llm_worker(self):
        while True:
            job = self.jobs.get()
            try:
                if job[0] == "narrate":
                    self._narrate(job[1], job[2])
                elif job[0] == "answer":
                    self._answer(job[1], job[2])
                elif job[0] == "summary":
                    self._trial_summary(job[1])
                    job[2].set()
            except Exception as e:  # noqa: BLE001
                print(f"[assistant] model job failed: {e}", flush=True)
            finally:
                if job[0] == "narrate":
                    self.inflight -= 1

    def _narrate(self, n: int, md: str):
        user = (f"Epoch {n} record:\n{md}\n\n"
                f"Write the reading for epoch {n} — about THIS epoch's record only (each epoch is different; do not repeat earlier notes): "
                "2-4 plain sentences on what the flies did and what it bears on, "
                "agenda_items = the ids it bears on (e.g. [\"A4\", \"H2\"]), unexpected = true only if something contradicts the established results, "
                "suggestion = ONE concrete guidance action ('bring fly2 to fly1', 'food fly1', 'follow fly2', 'clear fly1') or 'none'.")
        t0 = time.time()
        r = self.llm.chat_json(self._system(), user, NOTE_SCHEMA)
        if not r:
            self.notes.write(f"> reading of epoch {n}: model failed ({self.llm.last_error})")
            return
        ids = [i for i in r.get("agenda_items", []) if self.agenda.get(i)]
        self.last_note = r["note"]
        flag = " **UNEXPECTED**" if r.get("unexpected") else ""
        sugg = r.get("suggestion", "").strip()
        self.notes.write(f"> **Reading of epoch {n}** ({self.llm.model}, {time.time() - t0:.0f} s){flag} [{', '.join(ids) or 'no agenda item'}]: {r['note']}"
                         + (f"\n> Suggested guidance: {sugg}" if sugg and sugg.lower() != "none" else ""))
        print(f"[assistant] reading {n}: {r['note'][:160]}", flush=True)

    # ---- questions and guidance ----
    def handle_message(self, who: str, text: str):
        text = text.strip()
        if not text:
            return
        self.notes.write(f"**{who} ({hms()}):** {text}")
        reply = self.command(text)
        if reply is not None:
            self._reply(who, reply)
        elif self.llm:
            self.jobs.put(("answer", who, text))
            self._reply(who, "thinking…") if who != "console" else None
        else:
            self._reply(who, "No model is loaded; I understand: agenda, status, follow <fly>, bring <fly> to <fly> [blocks], food <fly> [blocks], clear <fly>, summon <entity> near <fly>, time day|night, note <text>.")

    def _reply(self, who: str, text: str):
        self.notes.write(f"**{self.a.name}:** {text}")
        print(f"[assistant] -> {who}: {text}", flush=True)
        if self.scribe and who != "console":
            self.scribe.say(text)

    def command(self, text: str) -> str | None:
        """Deterministic commands; returns None if the text is not one of them."""
        t = text.strip().rstrip(".").strip()
        low = t.lower()
        m_bring = re.match(r"^bring\s+(\S+)\s+(?:to|near)\s+(\S+)(?:\s+(\d+(?:\.\d+)?))?$", low)
        m_food = re.match(r"^(?:food|feed|flower)\s+(\S+)(?:\s+(\d+(?:\.\d+)?))?$", low)
        m_clear = re.match(r"^clear\s+(\S+)$", low)
        m_follow = re.match(r"^follow\s+(\S+)$", low)
        m_summon = re.match(r"^summon\s+(\S+)\s+near\s+(\S+)(?:\s+(\d+))?$", low)
        m_time = re.match(r"^time\s+(day|night|noon|midnight)$", low)
        if low in ("agenda", "paper"):
            return self._agenda_status()
        if low == "status":
            return self._status()
        if low in ("quit", "exit", "stop"):
            self.running = False
            return "stopping; writing the trial summary"
        if low.startswith("note "):
            self.notes.write(f"**Researcher note ({hms()}):** {t[5:].strip()}")
            return "noted"
        if m_follow:
            return self.act({"action": "follow", "who": m_follow.group(1)})
        if m_bring:
            return self.act({"action": "bring", "who": m_bring.group(1), "to": m_bring.group(2), "dist": float(m_bring.group(3) or 3)})
        if m_food:
            return self.act({"action": "place_food", "who": m_food.group(1), "dist": float(m_food.group(2) or 3)})
        if m_clear:
            return self.act({"action": "clear_food", "who": m_clear.group(1)})
        if m_summon:
            return self.act({"action": "summon", "entity": m_summon.group(1), "who": m_summon.group(2), "dist": float(m_summon.group(3) or 4)})
        if m_time:
            return self.act({"action": "time", "value": m_time.group(1)})
        return None

    def act(self, action: dict) -> str:
        """Validate one guidance action and have the body carry it out. Only flies, blocks and mobs are ever touched."""
        kind = action.get("action", "none")
        if kind == "none":
            return "no action"
        if not self.scribe:
            return f"cannot {kind}: running without a body (--no-body)"
        flies = set(self.roster) | {f["name"] for f in (self.scribe.snapshot or {}).get("flies", [])}
        who, to = action.get("who", ""), action.get("to", "")
        if kind in ("bring", "place_food", "clear_food", "summon") and who not in flies:
            return f"cannot {kind}: '{who}' is not a fly ({', '.join(sorted(flies)) or 'none seen'})"
        if kind == "follow" and who not in flies and who not in ("nearest", "none"):
            return f"cannot follow '{who}': not a fly"
        if kind == "bring" and to not in flies:
            return f"cannot bring: '{to}' is not a fly"
        dist = float(action.get("dist") or 3)
        dist = min(max(dist, 1.0), 12.0)
        if kind == "follow":
            r = self.scribe.cmd("follow", who=who)
        elif kind == "bring":
            r = self.scribe.cmd("bring", who=who, to=to, dist=dist)
        elif kind == "place_food":
            block = action.get("block") or "poppy"
            if block not in fn_food_blocks():
                block = "poppy"
            r = self.scribe.cmd("place_near", who=who, block=block, dist=dist)
        elif kind == "clear_food":
            r = self.scribe.cmd("clear_near", who=who, radius=8)
        elif kind == "summon":
            ent = re.sub(r"[^a-z_]", "", (action.get("entity") or "sheep").lower()) or "sheep"
            if ent not in SAFE_MOBS:
                return f"cannot summon '{ent}': allowed are {', '.join(sorted(SAFE_MOBS))}"
            r = self.scribe.cmd("summon", entity=ent, near=who, dist=dist)
        elif kind == "time":
            v = action.get("value") or "day"
            r = self.scribe.cmd("time", value=v if v in ("day", "night", "noon", "midnight") else "day")
        else:
            return f"unknown action {kind}"
        msg = f"{kind}: {r.get('msg', '?')}" + ("" if r.get("ok") else " (failed)")
        self.guidance_log.append(f"{hms()} {msg}")
        self.notes.write(f"*Guidance ({hms()}): {msg}*")
        return msg

    def _answer(self, who: str, question: str):
        snap = self._snapshot_line() if (self.scribe and self.scribe.snapshot) else "No body snapshot."
        user = (f"Question from {who}: {question}\n\nLatest epoch record:\n{self._condense(self.last_epoch_md, 16) if self.last_epoch_md else '(none yet)'}\n\n{snap}\n\n"
                f"Guidance so far: {'; '.join(self.guidance_log[-5:]) or 'none'}\n\n"
                "Answer in at most 60 words (this goes to in-game chat). Include actions ONLY if the question asks you to do something; "
                f"allowed actions: {', '.join(ACTIONS)} (who/to are fly names).")
        r = self.llm.chat_json(self._system(), user, ANSWER_SCHEMA)
        if not r:
            self._reply(who, f"model failed: {self.llm.last_error}")
            return
        self._reply(who, r.get("reply", "").strip() or "(no reply)")
        # carry out proposed actions only when the question actually asked for one; otherwise they are suggestions
        asked = bool(re.search(r"\b(bring|put|place|move|follow|summon|clear|teleport|set time|make it)\b", question.lower()))
        for act in (r.get("actions") or [])[:3]:
            kind = act.get("action", "none")
            if kind == "none":
                continue
            complete = (kind == "time") or bool(act.get("who")) and (kind != "bring" or bool(act.get("to")))
            if asked and complete:
                self._reply(who, self.act(act))
            elif complete:
                self.notes.write(f"*Model suggested (not carried out, nobody asked): {kind} {act.get('who', '')}{' to ' + act['to'] if act.get('to') else ''}*")

    def _status(self) -> str:
        parts = []
        for fly, dfs in self.totals.items():
            n = sum(len(d) for d in dfs)
            parts.append(f"{fly}: {n} ticks logged in {len(dfs)} epochs")
        if self.scribe and self.scribe.snapshot:
            parts.append(self._snapshot_line())
        parts.append(f"agenda tags so far: {dict(self.tag_counts) or 'none'}")
        if self.llm:
            parts.append(f"model: {self.llm.stats()}")
        return " | ".join(parts)

    def _agenda_status(self) -> str:
        return self.agenda.render(width=100) + "\n\nThis trial so far:\n" + contribution(self.tag_counts, self.agenda)

    # ---- the end ----
    def finish(self, append_research_notes: bool):
        import pandas as pd
        dfs = {fly: pd.concat(parts, ignore_index=True) for fly, parts in self.totals.items() if parts}
        metas = {fly: self.tails[fly].meta for fly in dfs}
        totals = fn.trial_totals(dfs, metas)
        contrib = contribution(self.tag_counts, self.agenda)
        md = (f"## Whole trial `{self.trial}` ({time.strftime('%Y-%m-%d %H:%M')})\n\n{fn.summary_table(totals)}\n\n"
              f"Agenda contribution:\n{contrib}\n\n" + (f"Guidance given:\n" + "\n".join(f"- {g}" for g in self.guidance_log) + "\n\n" if self.guidance_log else "") +
              (f"Model use: {self.llm.stats()}\n" if self.llm else ""))
        self.notes.write(md)
        if self.llm and dfs:
            done = threading.Event()
            self.jobs.put(("summary", md, done))
            done.wait(240)
        self.notes.close()
        if append_research_notes:
            self._append_research_notes(md)
        print(f"[assistant] notes: {self.notes.path}", flush=True)

    def _trial_summary(self, md: str):
        user = (f"Whole-trial record:\n{md}\n\n"
                "Write the trial summary for the lab notebook: 3-6 sentences (what was tested, what happened, which agenda items it "
                "advances and what it does NOT show), then the single most useful next step given the 'Order of work'.")
        r = self.llm.chat_json(self._system(), user, SUMMARY_SCHEMA)
        if r:
            ids = [i for i in r.get("agenda_items", []) if self.agenda.get(i)]
            self.notes.write(f"> **Trial summary** ({self.llm.model}) [{', '.join(ids) or 'no agenda item'}]: {r['summary']}\n> Next step: {r['next_step']}")
            self.last_summary = r
        else:
            self.notes.write(f"> trial summary: model failed ({self.llm.last_error})")

    def _append_research_notes(self, md: str):
        path = os.path.join(ROOT, "RESEARCH_NOTES.md")
        text = open(path, encoding="utf-8").read()
        rel = os.path.relpath(self.notes.path, ROOT)
        block = (f"\n\n### Assistant field notes — trial `{self.trial}` ({time.strftime('%Y-%m-%d %H:%M')})\n"
                 f"Full notes: `{rel}`. " + (f"Summary ({self.llm.model}): {getattr(self, 'last_summary', {}).get('summary', '')}\n" if getattr(self, "last_summary", None) else "\n")
                 + "\nAgenda contribution:\n" + contribution(self.tag_counts, self.agenda) + "\n")
        with open(path, "a", encoding="utf-8") as f:
            f.write(block if text.endswith("\n") else "\n" + block)
        print(f"[assistant] appended a summary to RESEARCH_NOTES.md", flush=True)


SAFE_MOBS = {"sheep", "cow", "pig", "chicken", "rabbit", "cat", "wolf", "zombie", "skeleton", "spider", "creeper", "villager", "bee", "frog"}


def fn_food_blocks() -> set[str]:
    src = open(os.path.join(ROOT, "bot", "observe.js"), encoding="utf-8").read()
    m = re.search(r"const FOOD = new Set\(\[(.*?)\]\)", src, re.S)
    return set(re.findall(r"'([a-z_]+)'", m.group(1))) if m else {"poppy", "dandelion"}


# --- console -------------------------------------------------------------------------------------------------------
def console(asst: Assistant):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        asst.handle_message("console", line)
        if not asst.running:
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trial", default="live", help="trial label: reads logs/roster_<trial>.json and names the notes file")
    ap.add_argument("--logs", nargs="*", help="brain CSV logs to follow (default: newest per rostered fly, modified in the last --fresh minutes)")
    ap.add_argument("--fresh", type=float, default=15.0)
    ap.add_argument("--world", choices=["wild", "arena"], default="wild")
    ap.add_argument("--port", type=int, help="Minecraft port (default from --world: wild 25566, arena 25565)")
    ap.add_argument("--name", default="observer", help="the body's player name (must be op'd; 'observer' is, on both servers)")
    ap.add_argument("--follow", default="nearest", help="fly name | nearest | none")
    ap.add_argument("--distance", type=float, default=4.0)
    ap.add_argument("--height", type=float, default=2.0)
    ap.add_argument("--ws", type=int, default=8790)
    ap.add_argument("--no-body", action="store_true", help="notes only; do not join the world")
    ap.add_argument("--interval", type=float, default=30.0, help="live epoch length (wall seconds)")
    ap.add_argument("--llm", default=DEFAULT_MODEL, help="Ollama model name, or 'off'")
    ap.add_argument("--llm-url", default="http://127.0.0.1:11434")
    ap.add_argument("--llm-loose", action="store_true", help="ask for JSON in the prompt instead of grammar-constraining it (better for gemma3)")
    ap.add_argument("--narrate-every", type=int, default=1, help="ask the model for a reading every N epochs")
    ap.add_argument("--notes-dir", default="notes")
    ap.add_argument("--append-research-notes", action="store_true", help="append the trial summary to RESEARCH_NOTES.md at the end")
    ap.add_argument("--replay", nargs="*", help="offline: finished logs to annotate; no body")
    ap.add_argument("--window", type=float, default=60.0, help="replay epoch length (brain seconds)")
    ap.add_argument("--max-epochs", type=int, default=0, help="stop after N epochs (0 = until the flies stop / Ctrl-C)")
    ap.add_argument("--idle-exit", type=float, default=120.0, help="live: exit when no fly log has grown for this many seconds (0 = never)")
    a = ap.parse_args()

    asst = Assistant(a)
    try:
        if a.replay:
            asst.attach_logs(a.replay)
            asst.write_header("replay")
            dfs = {fly: fn.load_log(t.path) for fly, t in asst.tails.items()}
            tmax = max(float(df["brain_t_ms"].max()) / 1000 for df in dfs.values())
            t0 = 0.0
            while t0 < tmax and asst.running and (not a.max_epochs or asst.epoch_n < a.max_epochs):
                win = {fly: df[(df["brain_t_ms"] / 1000 >= t0) & (df["brain_t_ms"] / 1000 < t0 + a.window)] for fly, df in dfs.items()}
                asst.epoch(win, f"+{t0:.0f}s", f"+{t0 + a.window:.0f}s")
                t0 += a.window
                while asst.llm and asst.inflight > 0:        # offline: let every reading finish, in order
                    time.sleep(0.5)
            asst.finish(a.append_research_notes)
            return
        # live
        logs = a.logs or asst.find_logs(a.fresh)
        if not logs:
            print("[assistant] no fresh fly logs found; is a flock running? (or pass --logs)", flush=True)
        asst.attach_logs(logs)
        for t in asst.tails.values():
            t.read_new()          # skip what happened before we arrived; the notes start now
        if not a.no_body:
            port = a.port or (25566 if a.world == "wild" else 25565)
            asst.scribe = Scribe(a.name, port, asst.roster_path if os.path.exists(asst.roster_path) else "", a.follow, a.ws, a.distance, a.height,
                                 os.path.join(ROOT, "logs", f"assistant_{a.trial}_body.out"))
            print(f"[assistant] body '{a.name}' joining localhost:{port}, following {a.follow}; log logs/assistant_{a.trial}_body.out", flush=True)
        asst.write_header("live")
        threading.Thread(target=console, args=(asst,), daemon=True).start()
        print(f"[assistant] taking notes every {a.interval:.0f} s -> {asst.notes.path}. Type 'agenda', 'status', 'follow fly2', 'bring fly2 to fly1', 'food fly1', a question, or 'quit'.", flush=True)
        last_wall = time.time()
        last_growth = time.time()
        sizes = {fly: os.path.getsize(t.path) for fly, t in asst.tails.items()}
        while asst.running:
            time.sleep(1.0)
            asst.poll_body()
            for fly, t in asst.tails.items():
                sz = os.path.getsize(t.path)
                if sz != sizes[fly]:
                    sizes[fly] = sz; last_growth = time.time()
            if time.time() - last_wall >= a.interval:
                asst.epoch(None, hms(last_wall), hms())
                last_wall = time.time()
                if a.max_epochs and asst.epoch_n >= a.max_epochs:
                    break
            if a.idle_exit and asst.tails and time.time() - last_growth > a.idle_exit:
                print(f"[assistant] fly logs have not grown for {a.idle_exit:.0f} s; the trial seems over", flush=True)
                break
    except KeyboardInterrupt:
        print("\n[assistant] stopping", flush=True)
    finally:
        if not a.replay:
            if asst.tails:
                asst.epoch(None, hms(), hms())
            asst.finish(a.append_research_notes)
        if asst.scribe:
            asst.scribe.stop()


if __name__ == "__main__":
    main()
