"""Deterministic field notes from the fly brains' per-tick CSV logs (logs/<fly>_<arm>-<dataset>[-<state>]_<stamp>.csv).

Everything here is arithmetic on the log; nothing is interpreted. `assistant.py` uses it live (LogTail follows a
growing file), and it also works on finished logs:

    python assistant/fieldnotes.py logs/fly1_off-flywire_20260915-221642.csv logs/fly2_off-malecns_20260915-221643.csv --window 60
"""
from __future__ import annotations

import csv
import io
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field

import pandas as pd

# neuron-group readouts written by brain/flybrain/motor.py (hz_<key> columns): label, what it means, published role
READOUTS = {
    "dnp09": ("DNp09", "forward walking / pursuit descending neuron"),
    "forward": ("walking DNs", "DNp09 + DNa01/02: the walking drive (female)"),
    "turn_L": ("DNa01/02 left", "ipsilateral turning, left"),
    "turn_R": ("DNa01/02 right", "ipsilateral turning, right"),
    "back": ("MDN", "backward walking (moonwalker)"),
    "jump": ("giant fiber (DNp01)", "escape jump"),
    "aggression": ("pC1d/e + aIPg", "female aggression"),
    "feed": ("proboscis/ingestion MNs (MN9)", "feeding"),
    "egg": ("oviDN", "egg laying"),
    "accept": ("vpoDN (DNp37)", "female receptivity"),
    "reject": ("DNp13", "ovipositor extrusion = rejection"),
    "sing": ("pIP10", "song command (male)"),
    "song_mn": ("song wing MNs", "song (male)"),
    "wing_mn": ("wing MNs", "all wing motor neurons (male)"),
    "court_p1": ("P1/pC1", "male courtship cluster"),
    "leg_mn": ("leg MNs", "walking (male, nerve cord)"),
    "leg_mn_L": ("leg MNs left", ""), "leg_mn_R": ("leg MNs right", ""),
    "dn_L": ("all DNs left", ""), "dn_R": ("all DNs right", ""), "dn_all": ("all DNs", ""),
    "mb_kc": ("Kenyon cells", "mushroom body input"), "mb_mbon": ("MBONs", "mushroom body output"),
    "mb_dan": ("DANs", "dopamine teaching signal"),
    "sag": ("SAG", "sex-peptide pathway (virgin state)"), "ipc": ("IPCs", "insulin cells (fed state)"),
}
# readouts whose bursts are worth an event line, with the rate (Hz, 1 s rolling mean) that counts as a burst
BURST_GROUPS = {"reject": 5, "aggression": 3, "accept": 2, "egg": 2, "sing": 5, "song_mn": 5, "court_p1": 3, "jump": 1, "feed": 10, "back": 5}
ACTS = ["jump", "attack", "feed", "sing", "court", "egg", "accept", "reject"]
ACT_LABEL = {"jump": "jump (giant fiber)", "attack": "lunge", "feed": "proboscis extension", "sing": "song bout",
             "court": "courtship event", "egg": "egg-laying event", "accept": "acceptance event", "reject": "rejection (ovipositor extrusion)"}
# boolean sensory channels: column -> (label, agenda hint)
CHANNELS = {
    "obs_taste_fly_female": "touching a female", "obs_taste_fly_male": "touching a male",
    "obs_taste_sugar": "sugar under the tarsi", "obs_taste_water": "water", "obs_taste_bitter": "bitter",
    "obs_sound": "hearing song", "obs_mech_hit": "being hit", "obs_mech_in_water": "in water",
}
NEAR_BLOCKS = 2.0        # "near another fly" = nearest fly within this many blocks
CHANNEL_GAP_S = 2.0      # a sensory channel counts as 'off' only after this much brain time without input (debounce)
TELEPORT_BLOCKS = 5.0    # a per-tick position jump larger than this is a teleport, not walking

LOG_RE = re.compile(r"^(?P<fly>[^_]+)_(?P<arm>off|mb)(?:-(?P<ds>flywire|malecns))?(?:-(?P<rest>[^_]+))?_(?P<stamp>\d{8}-\d{6})(?P<spikes>_spikes)?\.csv$")
STATE_NAMES = {"virgin", "fed", "hungry", "aroused", "aggressive", "courting"}   # brain/flybrain/server.py STATES


def parse_log_name(path: str) -> dict:
    """fly1_off-flywire_<stamp>.csv, fly2_mb-malecns-virgin+fed-dan_<stamp>.csv, fly1_off-flywire-zenodo_<stamp>.csv ...
    -> {fly, arm, ds, state, variant, stamp}; `variant` collects any tag pieces that are not states (teaching signal, sign rule)."""
    m = LOG_RE.match(os.path.basename(path))
    if not m:
        return {"fly": os.path.basename(path).split("_")[0], "arm": "?", "ds": "?", "state": "", "variant": "", "stamp": ""}
    d = m.groupdict()
    d["ds"] = d["ds"] or "flywire"
    states, variant = [], []
    for piece in (d.pop("rest") or "").split("-"):
        if not piece:
            continue
        (states if all(x in STATE_NAMES for x in piece.split("+")) else variant).append(piece)
    d["state"] = "+".join(states); d["variant"] = "-".join(variant)
    d.pop("spikes", None)
    return d


def _coerce(df: pd.DataFrame) -> pd.DataFrame:
    """CSV text -> numbers/booleans (pandas 3 infers `str` columns, older pandas `object`; handle both)."""
    for c in df.columns:
        if c in ("trial", "sex", "near_name"):
            continue
        s = df[c]
        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_bool_dtype(s):
            continue
        low = s.astype(str).str.strip().str.lower()
        if low.isin(["true", "false", "", "none", "nan"]).all():
            df[c] = low.eq("true")
        else:
            df[c] = pd.to_numeric(s, errors="coerce")
    return df


def load_log(path: str) -> pd.DataFrame:
    return _coerce(pd.read_csv(path, low_memory=False))


class LogTail:
    """Incrementally read a CSV that another process is still writing (only complete lines are consumed)."""

    def __init__(self, path: str):
        self.path = path
        self.meta = parse_log_name(path)
        self.fly = self.meta["fly"]
        self.header: list[str] | None = None
        self.pos = 0
        self.rows_read = 0

    def read_new(self) -> pd.DataFrame:
        with open(self.path, "rb") as f:
            f.seek(self.pos)
            data = f.read()
        if not data:
            return pd.DataFrame()
        cut = data.rfind(b"\n")
        if cut < 0:
            return pd.DataFrame()
        chunk, self.pos = data[: cut + 1], self.pos + cut + 1
        text = chunk.decode("utf-8", errors="replace")
        if self.header is None:
            first, _, rest = text.partition("\n")
            self.header = next(csv.reader([first]))
            text = rest
        if not text.strip():
            return pd.DataFrame(columns=self.header)
        rows = list(csv.reader(io.StringIO(text)))
        rows = [r for r in rows if len(r) == len(self.header)]
        self.rows_read += len(rows)
        return _coerce(pd.DataFrame(rows, columns=self.header))


@dataclass
class ChannelState:
    """Carries on/off state of sensory channels and bursts across windows so events are not repeated."""
    on: dict = field(default_factory=dict)        # channel -> brain time (s) it switched on
    last_on: dict = field(default_factory=dict)   # channel -> last brain time (s) it was seen on
    burst: dict = field(default_factory=dict)     # readout -> (start s, peak Hz)
    near: str | None = None
    near_since: float = 0.0
    last_pos: tuple | None = None
    last_hp: float | None = None


def _brain_s(df: pd.DataFrame) -> pd.Series:
    return df["brain_t_ms"].astype(float) / 1000.0


def summarize(df: pd.DataFrame, meta: dict | None = None) -> dict:
    """One fly, one window of rows -> numbers a person can read."""
    meta = meta or {}
    if df is None or len(df) == 0:
        return {"fly": meta.get("fly", "?"), "ticks": 0}
    t = _brain_s(df)
    x, z = df["x"].astype(float), df["z"].astype(float)
    dx, dz = x.diff().fillna(0), z.diff().fillna(0)
    step = (dx ** 2 + dz ** 2) ** 0.5
    walked = float(step[step < TELEPORT_BLOCKS].sum())
    teleports = int((step >= TELEPORT_BLOCKS).sum())
    brain_span = float(t.iloc[-1] - t.iloc[0]) + 0.05
    wall_span = float(df["t_wall"].astype(float).iloc[-1] - df["t_wall"].astype(float).iloc[0]) + 1e-6
    turn = df["ctl_turn"].astype(float)
    s = {
        "fly": meta.get("fly") or str(df["sex"].iloc[0] if "sex" in df else "?"),
        "sex": str(df["sex"].iloc[-1]) if "sex" in df else "?",
        "arm": meta.get("arm", "?"), "dataset": meta.get("ds", "?"), "state": meta.get("state", ""),
        "ticks": int(len(df)),
        "t0": float(t.iloc[0]), "t1": float(t.iloc[-1]),
        "brain_s": round(brain_span, 1), "wall_s": round(wall_span, 1), "brain_over_wall": round(brain_span / wall_span, 2),
        "walked_blocks": round(walked, 1), "speed_blocks_per_brain_s": round(walked / brain_span, 2),
        "teleports": teleports,
        "walk_duty": round(float(df["ctl_walk"].astype(float).mean()), 2),
        "back_duty": round(float(df["ctl_back"].astype(float).mean()), 2),
        "turn_bias": round(float(turn.mean()), 2),              # + = left
        "turn_abs": round(float(turn.abs().mean()), 2),
        "acts": {a: int(df[f"ctl_{a}"].astype(bool).sum()) for a in ACTS if f"ctl_{a}" in df},
        "readouts": {}, "senses": {}, "smell": {},
        "spikes_per_tick": round(float(df["hz_total_spikes"].astype(float).mean()), 0) if "hz_total_spikes" in df else None,
        "active_frac": round(float(df["hz_active_frac"].astype(float).mean()), 3) if "hz_active_frac" in df else None,
        "pos": (round(float(x.iloc[-1]), 1), round(float(df["y"].astype(float).iloc[-1]), 1), round(float(z.iloc[-1]), 1)),
        "hp_min": float(df["hp"].astype(float).min()) if "hp" in df else None,
    }
    for k in READOUTS:
        c = f"hz_{k}"
        if c in df:
            v = df[c].astype(float)
            if v.max() > 0:
                s["readouts"][k] = {"mean": round(float(v.mean()), 1), "peak": round(float(v.max()), 1)}
    for c, label in CHANNELS.items():
        if c in df:
            frac = float(df[c].astype(bool).mean())
            if frac > 0:
                s["senses"][label] = round(frac, 3)
    for ch in ("food", "co2", "fly", "cva", "aversive"):
        L, R = f"obs_smell_{ch}_L", f"obs_smell_{ch}_R"
        if L in df and R in df:
            m = float((df[L].astype(float) + df[R].astype(float)).mean() / 2)
            if m > 0.001:
                s["smell"][ch] = round(m, 3)
    # per-class odor identity (learning-arm logs: odor_<class>_L/R, flower families by colour)
    s["odors"] = {}
    for c in df.columns:
        m = re.match(r"^odor_(\w+)_L$", c)
        if m and f"odor_{m.group(1)}_R" in df:
            v = float((pd.to_numeric(df[c], errors="coerce").fillna(0) + pd.to_numeric(df[f"odor_{m.group(1)}_R"], errors="coerce").fillna(0)).mean() / 2)
            if v > 0.001:
                s["odors"][m.group(1)] = round(v, 3)
    if "near_dist" in df:
        nd = pd.to_numeric(df["near_dist"], errors="coerce")
        if nd.notna().any():
            names = df.loc[nd.notna(), "near_name"].astype(str)
            s["near"] = {"min_dist": round(float(nd.min()), 2), "mean_dist": round(float(nd.mean()), 1),
                         "frac_within_2": round(float((nd < NEAR_BLOCKS).mean()), 3),
                         "who": names.mode().iloc[0] if len(names) else None}
    if any(c.startswith("pl_") for c in df.columns):
        s["plasticity"] = {c[3:]: round(float(pd.to_numeric(df[c], errors="coerce").fillna(0).iloc[-1]), 4) for c in df.columns if c.startswith("pl_")}
    return s


def detect_events(df: pd.DataFrame, st: ChannelState, fly: str) -> list[dict]:
    """State transitions worth a line in the notes: {t (brain s), fly, kind, text, tags?}."""
    ev: list[dict] = []
    if df is None or len(df) == 0:
        return ev
    t = _brain_s(df).to_numpy()
    xs, ys, zs = df["x"].astype(float).to_numpy(), df["y"].astype(float).to_numpy(), df["z"].astype(float).to_numpy()

    def at(i):
        return f"({xs[i]:.0f},{ys[i]:.0f},{zs[i]:.0f})"

    # sensory channels on/off
    for c, label in CHANNELS.items():
        if c not in df:
            continue
        v = df[c].astype(bool).to_numpy()
        for i in range(len(v)):
            on = st.on.get(c)
            if v[i]:
                st.last_on[c] = float(t[i])
                if on is None:
                    st.on[c] = float(t[i])
                    ev.append({"t": float(t[i]), "fly": fly, "kind": "on", "channel": c, "text": f"{fly} starts {label} at {at(i)}"})
            elif on is not None and t[i] - st.last_on[c] >= CHANNEL_GAP_S:
                ev.append({"t": st.last_on[c], "fly": fly, "kind": "off", "channel": c, "text": f"{fly} stops {label} after {st.last_on[c] - on + 0.05:.1f} s"})
                del st.on[c]
    # proximity to another fly
    if "near_dist" in df:
        nd = pd.to_numeric(df["near_dist"], errors="coerce").to_numpy()
        nn = df["near_name"].astype(str).to_numpy()
        for i in range(len(nd)):
            close = (not math.isnan(nd[i])) and nd[i] < NEAR_BLOCKS
            if close and st.near is None:
                st.near, st.near_since = nn[i], float(t[i])
                ev.append({"t": float(t[i]), "fly": fly, "kind": "near", "who": nn[i], "text": f"{fly} within {NEAR_BLOCKS:.0f} blocks of {nn[i]} ({nd[i]:.1f}) at {at(i)}"})
            elif not close and st.near is not None:
                ev.append({"t": float(t[i]), "fly": fly, "kind": "apart", "who": st.near, "text": f"{fly} and {st.near} apart again after {t[i] - st.near_since:.1f} s"})
                st.near = None
    # discrete acts (merge repeats within 1 s of brain time)
    for a in ACTS:
        c = f"ctl_{a}"
        if c not in df:
            continue
        idx = [i for i, v in enumerate(df[c].astype(bool).to_numpy()) if v]
        i = 0
        while i < len(idx):
            j = i
            while j + 1 < len(idx) and t[idx[j + 1]] - t[idx[j]] <= 1.0:
                j += 1
            n = j - i + 1
            ev.append({"t": float(t[idx[i]]), "fly": fly, "kind": "act", "act": a, "n": n,
                       "text": f"{fly}: {ACT_LABEL[a]}" + (f" x{n} within {t[idx[j]] - t[idx[i]]:.1f} s" if n > 1 else "") + f" at {at(idx[i])}"})
            i = j + 1
    # readout bursts (1 s rolling mean crosses the threshold)
    for k, thr in BURST_GROUPS.items():
        c = f"hz_{k}"
        if c not in df:
            continue
        v = df[c].astype(float)
        win = max(1, int(round(1.0 / max(0.01, (t[-1] - t[0]) / max(1, len(t) - 1)))))
        r = v.rolling(win, min_periods=1).mean().to_numpy()
        for i in range(len(r)):
            b = st.burst.get(k)
            if r[i] >= thr and b is None:
                st.burst[k] = [float(t[i]), float(v.iloc[i])]
            elif b is not None:
                b[1] = max(b[1], float(v.iloc[i]))
                if r[i] < thr * 0.5:
                    label = READOUTS[k][0]
                    ev.append({"t": b[0], "fly": fly, "kind": "burst", "readout": k, "peak": round(b[1], 1), "dur": round(t[i] - b[0], 1),
                               "text": f"{fly}: {label} burst, peak {b[1]:.0f} Hz for {t[i] - b[0]:.1f} s"})
                    del st.burst[k]
    # teleports / hurt
    for i in range(len(xs)):
        p = (xs[i], ys[i], zs[i])
        if st.last_pos is not None and math.dist(p, st.last_pos) >= TELEPORT_BLOCKS:
            ev.append({"t": float(t[i]), "fly": fly, "kind": "teleport", "text": f"{fly} moved {math.dist(p, st.last_pos):.0f} blocks in one tick (teleport/respawn) to {at(i)}"})
        st.last_pos = p
    if "hp" in df:
        for i, hp in enumerate(df["hp"].astype(float).to_numpy()):
            if st.last_hp is not None and hp < st.last_hp:
                ev.append({"t": float(t[i]), "fly": fly, "kind": "hurt", "text": f"{fly} lost health ({st.last_hp:.0f} -> {hp:.0f})"})
            st.last_hp = hp
    ev.sort(key=lambda e: e["t"])
    return ev


def summary_table(summaries: list[dict]) -> str:
    rows = ["| fly | walked (blocks) | speed | walk duty | turn bias (+L) | acts | top readouts (mean/peak Hz) | senses | nearest fly |",
            "|---|---|---|---|---|---|---|---|---|"]
    for s in summaries:
        if not s.get("ticks"):
            rows.append(f"| {s.get('fly', '?')} | no new rows | | | | | | | |"); continue
        acts = ", ".join(f"{k} {v}" for k, v in s["acts"].items() if v) or "–"
        top = sorted(((k, v) for k, v in s["readouts"].items() if k not in ("dn_L", "dn_R", "dn_all", "leg_mn_L", "leg_mn_R", "forward", "mb_kc")),
                     key=lambda kv: -kv[1]["mean"])[:5]
        tops = ", ".join(f"{READOUTS[k][0]} {v['mean']:.0f}/{v['peak']:.0f}" for k, v in top) or "all silent"
        senses = ", ".join(f"{k} {v * 100:.1f}%" if v < 0.01 else f"{k} {v * 100:.0f}%" for k, v in s["senses"].items()) or "–"
        smell = ", ".join(f"{k} {v:.2f}" for k, v in s["smell"].items())
        if smell:
            senses += f"; smell {smell}"
        odors = ", ".join(f"{k} {v:.2f}" for k, v in s.get("odors", {}).items())
        if odors:
            senses += f"; odors {odors}"
        pl = s.get("plasticity") or {}
        if pl:
            keep = {k: v for k, v in pl.items() if k in ("kc_mbon_w_frac", "w_frac_reward_comp", "w_frac_punish_comp", "us_reward", "us_punish")}
            senses += "; memory " + ", ".join(f"{k.replace('w_frac_', '').replace('_comp', '')} {v}" for k, v in (keep or pl).items())
        near = s.get("near")
        nearest = f"{near['who']} min {near['min_dist']} (≤2 blocks {near['frac_within_2'] * 100:.0f}%)" if near else "none in range"
        rows.append(f"| {s['fly']} ({s['sex']}, {s['dataset']}, {s['arm']}{', ' + s['state'] if s['state'] else ''}) | {s['walked_blocks']}"
                    f"{' (+' + str(s['teleports']) + ' tp)' if s['teleports'] else ''} | {s['speed_blocks_per_brain_s']} b/s | {s['walk_duty']} | {s['turn_bias']:+.2f} | {acts} | {tops} | {senses} | {nearest} |")
    return "\n".join(rows)


def epoch_markdown(n: int, summaries: list[dict], events: list[dict], wall_from: str, wall_to: str) -> str:
    live = [s for s in summaries if s.get("ticks")]
    if live:
        t0, t1 = min(s["t0"] for s in live), max(s["t1"] for s in live)
        ratio = ", ".join(f"{s['fly']} {s['brain_over_wall']}x" for s in live)
        head = f"## Epoch {n} — {t1 - t0:.0f} s of brain time (brain clock {t0:.0f}–{t1:.0f} s; wall {wall_from}–{wall_to}; brain/wall {ratio})"
    else:
        head = f"## Epoch {n} — no new brain rows (wall {wall_from}–{wall_to})"
    out = [head, "", summary_table(summaries), ""]
    if events:
        out.append("Events (brain s):")
        for e in events:
            tags = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
            out.append(f"- {e['t']:.1f} {e['text']}{tags}")
        out.append("")
    return "\n".join(out)


def trial_totals(dfs: dict[str, pd.DataFrame], metas: dict[str, dict]) -> list[dict]:
    return [summarize(df, metas.get(fly, {"fly": fly})) for fly, df in dfs.items()]


if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--window", type=float, default=60.0, help="epoch length in seconds of brain time")
    a = ap.parse_args()
    dfs = {parse_log_name(p)["fly"]: load_log(p) for p in a.logs}
    metas = {parse_log_name(p)["fly"]: parse_log_name(p) for p in a.logs}
    states = {fly: ChannelState() for fly in dfs}
    tmax = max(float(df["brain_t_ms"].max()) / 1000 for df in dfs.values())
    n, t0 = 0, 0.0
    while t0 < tmax:
        n += 1
        sums, evs = [], []
        for fly, df in dfs.items():
            w = df[(df["brain_t_ms"] / 1000 >= t0) & (df["brain_t_ms"] / 1000 < t0 + a.window)]
            sums.append(summarize(w, metas[fly]))
            evs += detect_events(w, states[fly], fly)
        evs.sort(key=lambda e: e["t"])
        print(epoch_markdown(n, sums, evs, f"+{t0:.0f}s", f"+{t0 + a.window:.0f}s"))
        t0 += a.window
    print("## Whole trial\n")
    print(summary_table(trial_totals(dfs, metas)))
