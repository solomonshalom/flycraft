"""The paper agenda, read from RESEARCH_NOTES.md (`## Agenda` + every "What must still be done" list), and rules that
tag what the flies do with the agenda item it bears on.  The assistant keeps every note and every guidance suggestion
tied to one of these items; this module is the single place that knows what they are.

    python assistant/agenda.py            # print the agenda as the assistant sees it
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.join(HERE, "..", "RESEARCH_NOTES.md")


@dataclass
class Item:
    id: str          # H1..H4 hypotheses, A1..A5 aims, T1..Tn "still to do before this is a paper"
    text: str
    status: str = ""


@dataclass
class Agenda:
    title: str = ""
    question: str = ""
    hypotheses: list[Item] = field(default_factory=list)
    aims: list[Item] = field(default_factory=list)
    todo: list[Item] = field(default_factory=list)
    order: str = ""
    success: str = ""

    def items(self) -> list[Item]:
        return self.hypotheses + self.aims + self.todo

    def ids(self) -> list[str]:
        return [i.id for i in self.items()]

    def get(self, id_: str) -> Item | None:
        return next((i for i in self.items() if i.id == id_), None)

    def render(self, width: int = 160) -> str:
        out = [f"Working title: {self.title}", f"Question: {self.question}", "", "Hypotheses:"]
        for h in self.hypotheses:
            out.append(f"  {h.id}  {h.text[:width]}" + (f"  — {h.status[:width]}" if h.status else ""))
        out.append("Aims:")
        for a in self.aims:
            out.append(f"  {a.id}  {a.text[:width]}" + (f"  — {a.status[:width]}" if a.status else ""))
        if self.todo:
            out.append("Still to do before this is a paper:")
            for t in self.todo:
                out.append(f"  {t.id}  {t.text[:width]}")
        if self.order:
            out.append(f"Order of work: {self.order}")
        if self.success:
            out.append(f"Success = {self.success}")
        return "\n".join(out)


def _clean(s: str) -> str:
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def _status(s: str) -> tuple[str, str]:
    m = re.search(r"\*\(([^)]*)\)\*\s*$", s) or re.search(r"\*\((.*)\)\*\s*$", s, re.S) or re.search(r"\*([^*]+)\*\s*$", s)
    if m:
        return _clean(s[: m.start()]), _clean(m.group(1))
    return _clean(s), ""


def load_agenda(path: str = NOTES) -> Agenda:
    ag = Agenda()
    if not os.path.exists(path):
        return ag
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^## Agenda\s*$(.*?)^---\s*$", text, re.S | re.M)
    sec = m.group(1) if m else ""
    t = re.search(r"\*\*Working title:\*\*\s*(.+)", sec)
    ag.title = _clean(t.group(1)) if t else ""
    q = re.search(r"\*\*The question:\*\*\s*(.+)", sec)
    ag.question = _clean(q.group(1)) if q else ""
    # hypotheses: "- H1 — text *(status, possibly spanning continuation lines)*"
    for hm in re.finditer(r"^- (H\d+)\s*[—-]+\s*(.+?)(?=^- H\d+|^\s*$|^\*\*)", sec, re.M | re.S):
        txt, st = _status(hm.group(2).strip())
        ag.hypotheses.append(Item(hm.group(1), txt, st))
    aims_block = re.search(r"\*\*Aims and the three arms\*\*(.*?)(?:\n\*\*|\Z)", sec, re.S)
    if aims_block:
        for am in re.finditer(r"^(\d+)\.\s+(.+?)(?=^\d+\.\s|\Z)", aims_block.group(1), re.M | re.S):
            txt, st = _status(am.group(2).strip())
            ag.aims.append(Item(f"A{am.group(1)}", txt, st))
    o = re.search(r"\*\*Order of work from here:\*\*\s*(.+)", sec)
    ag.order = _clean(o.group(1)) if o else ""
    s = re.search(r"\*\*What would count as success:\*\*\s*(.+)", sec)
    ag.success = _clean(s.group(1)) if s else ""
    # every "What must still be done ..." list (section 15's, plus dated additions in later sections); items keep
    # their own numbers, so T7-T10 from section 16 follow T1-T6 from section 15
    seen: set[str] = set()
    for tb in re.finditer(r"\*\*What must still be done[^*]*\*\*(.*?)(?:\n###|\n## |\n\*\*[A-Z]|\Z)", text, re.S):
        for tm in re.finditer(r"^(\d+)\.\s+(.+?)(?=^\d+\.\s|\Z)", tb.group(1), re.S | re.M):
            tid = f"T{tm.group(1)}"
            if tid not in seen:
                seen.add(tid)
                ag.todo.append(Item(tid, _clean(tm.group(2))[:400]))
    ag.todo.sort(key=lambda i: int(i.id[1:]))
    return ag


# --- tagging: which agenda items an event or a run bears on ----------------------------------------------------
SOCIAL_READOUTS = {"reject", "accept", "aggression", "sing", "song_mn", "court_p1", "egg"}


def tag_event(e: dict, run: dict | None = None, agenda: Agenda | None = None) -> list[str]:
    """Rule-based tags (H*/A*/T*) for one fieldnotes event; `run` = {'arm': off|mb, 'state': '', 'dataset': ...}."""
    run = run or {}
    tags: list[str] = []
    k = e.get("kind")
    ch = e.get("channel", "")
    if k in ("near", "apart") or "fly_" in ch:
        tags += ["A4", "T1"]                                   # embodied encounters; encounter statistics
    if k == "burst" and e.get("readout") in SOCIAL_READOUTS:
        tags += ["H2", "A4"]
        if e.get("readout") in ("sing", "song_mn", "court_p1"):
            tags.append("H4")
    if k == "act" and e.get("act") in ("reject", "accept", "attack", "egg", "court", "sing"):
        tags += ["H2", "A4"]
        if e.get("act") in ("sing", "court"):
            tags.append("H4")
    if (k == "act" and e.get("act") in ("feed", "jump")) or (k == "burst" and e.get("readout") in ("feed", "jump", "back")) \
            or ch in ("obs_taste_sugar", "obs_taste_bitter", "obs_taste_water", "obs_mech_hit"):
        tags.append("H1")                                       # reflexes from wiring alone
    if ch == "obs_sound":
        tags += ["H1", "A4"]
    if run.get("arm") == "mb":
        tags += ["H3", "A2"]
    if run.get("state"):
        tags += ["A3", "T2"]
    if agenda is not None:
        tags = [t for t in tags if agenda.get(t)]
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out


def run_focus(runs: list[dict], agenda: Agenda) -> list[str]:
    """Which agenda items a trial with these runs (one dict per fly) serves, before anything happens."""
    f = []
    if len(runs) >= 2:
        f += ["A4", "T1"]
    if any(r.get("arm") == "mb" for r in runs):
        f += ["A2", "H3"]
    if any(r.get("state") for r in runs):
        f += ["A3", "T2"]
    if len(runs) == 1 and not f:
        f += ["A1", "H1"]
    if len({r.get("dataset") for r in runs}) > 1:
        f.append("H4")
    return [t for t in dict.fromkeys(f) if agenda.get(t)]


def contribution(tag_counts: dict[str, int], agenda: Agenda, n_trials_same_setup: int | None = None) -> str:
    """Plain-language 'what this trial contributed to the agenda' block."""
    if not tag_counts:
        return "Nothing in this trial bore on an agenda item yet."
    lines = []
    for id_, n in sorted(tag_counts.items(), key=lambda kv: -kv[1]):
        it = agenda.get(id_)
        if it:
            lines.append(f"- {id_} ({n} events): {it.text[:110]}{'…' if len(it.text) > 110 else ''}")
    if n_trials_same_setup is not None:
        need = max(0, 5 - n_trials_same_setup)
        lines.append(f"- Trials with this setup so far: {n_trials_same_setup}; the agenda's bar is n ≥ 5 per comparison"
                     + (f" ({need} more needed)." if need else " (met)."))
    return "\n".join(lines)


if __name__ == "__main__":
    print(load_agenda().render())
