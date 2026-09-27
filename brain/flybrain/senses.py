"""Map Minecraft observations onto the fly's sensory neurons.

This is the one part of the pipeline that is *our design*, not the fly's. Every mapping is
listed here explicitly so it can be reported in a methods section.

Observation schema (from bot/observe.js), all intensities in [0, 1]:
  eyes:    {L: {w, h, px: [...]}, R: {...}}   luminance images, row-major, top row first
  smell:   {food, co2, fly, cva, aversive, odors: {class: {L, R}}}   (each float or {L, R}; cva only from male flies;
            odors = per odor CLASS concentrations at the two antennae, see ODOR_LIBRARY; food/aversive are kept for
            bodies that do not send odors)
  taste:   {sugar, water, bitter, fly_female, fly_male}   (touching another fly, by its sex)
  mechano: {speed, wind, hit, collided, on_ground, in_water}
  sound:   float
  thermo:  {hot, cold}

Odor identity (ODOR_LIBRARY). A Minecraft block does not have a smell, so which block smells like what is OUR
design. What is the fly's: the glomeruli, their receptors and their ligand classes (Couto et al. 2005; Hallem &
Carlson 2006; Semmelhack & Wang 2009; Münch & Galizia 2016 (DoOR)). Each odor class drives a few glomeruli at graded
strengths, so that different flower families produce different antennal-lobe and Kenyon-cell codes — the substrate
that odor learning needs (the earlier single "food" channel drove five glomeruli identically for every food block).
"""
from __future__ import annotations

import numpy as np

from .connectome import Connectome

# maximum Poisson drive rates (Hz). Shiu et al. stimulate sensory neurons at 50-200 Hz.
R_VISION = 120.0
R_OLF = 150.0
R_TASTE = 150.0
R_MECH = 150.0
R_BURST = 200.0
R_THERMO = 100.0


# odor class -> {glomerulus: relative strength}.  Receptor / ligand family in the comment; block -> class in observe.js.
ODOR_LIBRARY = {
    # A natural odor drives 5-6 glomeruli at graded strengths (DoOR); the strongest two make the class distinctive, the
    # weaker ones are shared, as real odor profiles overlap. This size recruits 4-8 % of Kenyon cells (Honegger et al.
    # 2011: ~5 % per odor); 2-3 glomeruli left the MBONs silent (RESEARCH_NOTES 16).
    "ester":    {"DM2": 1.0, "DM4": 0.8, "VM2": 0.6, "DM5": 0.5, "VA2": 0.4, "DL5": 0.3},       # Or22a/Or59b/Or43b/Or85a/Or92a/Or7a: fruit esters (ethyl butyrate) — red/pink flowers
    "vinegar":  {"DM1": 1.0, "VA2": 0.8, "DP1l": 0.6, "VM2": 0.4, "DC4": 0.4, "VM5v": 0.3},     # Or42b/Or92a/Ir75a/Or43b/Ir64a/Or98a: fermentation (ethyl acetate, acetic acid) — yellow flowers
    "floral":   {"VA6": 1.0, "DL1": 0.8, "DC1": 0.6, "VA7l": 0.5, "DA4l": 0.5, "VM5d": 0.3},    # Or82a/Or10a/Or19a/Or46a/Or43a/Or85b: geranyl acetate, methyl salicylate, limonene — blue/purple flowers
    "green":    {"DL5": 1.0, "VM5v": 0.8, "DM6": 0.6, "DC2": 0.5, "VA3": 0.5, "DM3": 0.3},      # Or7a/Or98a/Or67a/Or13a/Or67b/Or47a: benzaldehyde, green-leaf volatiles — white flowers
    "sweet":    {"VM2": 1.0, "DM1": 0.8, "VL2a": 0.7, "DM2": 0.6, "VA2": 0.5, "DM4": 0.4},      # Or43b/Or42b/Ir84a/Or22a/Or92a/Or59b: ripe fruit, honey, phenylacetaldehyde — honey, cake, berries, melon
    "aversive": {"DA2": 1.0, "DL4": 0.8, "DM5": 0.5, "D": 0.4},                                  # Or56a (geosmin: mould)/Or85f/Or85a/Or69a — soul sand, mycelium, mushrooms
    "food":     {"DM1": 1.0, "DM2": 1.0, "DM4": 1.0, "VA2": 1.0, "VM2": 1.0},                    # the first version's undifferentiated food channel
}


class SensoryEncoder:
    def __init__(self, cx: Connectome, eye_flip: dict | None = None, verbose: bool = True):
        self.cx = cx
        self.optic_lobe = None   # set to a vision.OpticLobe to replace the raw photoreceptor drive by the flyvis optic lobe
        self.mask = set()        # input channels (group names below, e.g. "bristle") that are never driven
        s = cx.select
        self.groups = {
            # vision: outer photoreceptors R1-6 (motion/contrast pathway) + R7/R8 (color) driven by luminance
            "photo_L": s(cell_type=r"^R(1-6|1-R6|7|8)", side="^left$"),      # FlyWire: R1-6/R7/R8; MaleCNS: R1-R6/R7y/R7p/R8y/R8p
            "photo_R": s(cell_type=r"^R(1-6|1-R6|7|8)", side="^right$"),
            # olfaction by glomerulus (Schlegel et al. 2024 ORN_<glomerulus> labels), split by antenna
            # (side = nerve-entry side). ORNs project to both antennal lobes; the wiring does the bilateral comparison.
            "orn_food": s(cell_type=r"^ORN_(DM1|DM2|DM4|VA2|VM2)$"),      # fruit/yeast esters (Or42b, Or22a, Or59b, Or92a, Or43b)
            "orn_co2": s(cell_type=r"^ORN_V$"),                            # Gr21a/Gr63a CO2 (V glomerulus)
            "orn_fly": s(cell_type=r"^ORN_VA1v$"),                         # Or47b: fly-derived odor (any sex)
            "orn_cva": s(cell_type=r"^ORN_(DA1|DL3)$"),                     # Or67d/Or65a: cVA, a MALE pheromone
            "orn_aversive": s(cell_type=r"^ORN_(DA2|DL4)$"),               # geosmin (Or56a) + Or49a: aversive
            # taste
            "grn_sugar": s(cell_class="^gustatory$", cell_sub_class="sugar/water|labellar bristle"),   # MaleCNS has no sugar/bitter split: labellar GRNs
            "grn_bitter": s(cell_class="^gustatory$", cell_sub_class="^bitter$"),
            "grn_ppk25": s(any_of={"receptor_type": "ppk25"}),   # leg GRNs for female cuticular hydrocarbons (7,11-HD) — MaleCNS labels
            "grn_ppk23": s(any_of={"receptor_type": "ppk23"}),   # leg GRNs for male cuticular hydrocarbons (7-T)
            # mechanosensation
            "jo_wind": s(cell_class="^mechanosensory", cell_sub_class="wind_gravity"),    # Johnston's organ C/E
            "jo_sound": s(cell_class="^mechanosensory", cell_sub_class="auditory"),       # Johnston's organ A/B
            "bristle": s(cell_type=r"^BM_"),                                                # head/eye bristle mechanosensors (both datasets)
            "groom_touch": s(cell_class="^mechanosensory", cell_sub_class="grooming"),
            # thermo / hygro
            "thermo_hot": s(cell_class="^thermosensory$", cell_sub_class="heating"),
            "thermo_cold": s(cell_class="^thermosensory$", cell_sub_class="cooling|cold"),
            "hygro_moist": s(cell_class="^hygrosensory$", cell_sub_class="moist|humid"),
        }
        # one ORN group per glomerulus used by the odor library (ORN_<glomerulus> labels, both datasets)
        for glom in sorted({g for prof in ODOR_LIBRARY.values() for g in prof}):
            self.groups[f"glom_{glom}"] = s(cell_type=rf"^ORN_{glom}$")
        side = cx.neurons.side.fillna("").to_numpy()
        for g in ("orn_food", "orn_co2", "orn_fly", "orn_cva", "orn_aversive", "thermo_hot", "thermo_cold") + tuple(k for k in self.groups if k.startswith("glom_")):
            idx = self.groups[g]
            self.groups[g + "_L"] = idx[(side[idx] == "left") | (side[idx] == "na") | (side[idx] == "center")]
            self.groups[g + "_R"] = idx[(side[idx] == "right") | (side[idx] == "na") | (side[idx] == "center")]
        if verbose:
            for k, v in self.groups.items():
                if not k.startswith("glom_"):
                    print(f"[senses] {k:13s} {cx.describe(v)}")
            print("[senses] odor library: " + "; ".join(f"{c}: " + ",".join(f"{g}({len(self.groups['glom_' + g])})" for g in prof) for c, prof in ODOR_LIBRARY.items()))
        self.eye_flip = eye_flip or {"L": (False, False), "R": (True, False)}
        self.eye_uv = {side: self._retinotopy(self.groups[f"photo_{side}"], side) for side in ("L", "R")}

    def _retinotopy(self, idx: np.ndarray, side: str) -> np.ndarray:
        """Approximate retinotopic (u, v) in [0,1]^2 for each photoreceptor from its EM anchor point.

        FAFB axes: x = left-right, y = dorsal(-)/ventral(+), z = anterior/posterior (sectioning axis).
        The lamina is a sheet whose dorso-ventral extent maps to elevation and antero-posterior
        extent to azimuth, so we use y -> v (row) and z -> u (column). Orientation signs are an
        assumption (see the paper's Limitations) and configurable via eye_flip.
        """
        P = self.cx.neurons.iloc[idx][["pos_x", "pos_y", "pos_z"]].to_numpy(dtype=np.float64)
        P = np.nan_to_num(P, nan=np.nanmedian(P, axis=0))
        u = P[:, 2]; v = P[:, 1]
        def norm(a):
            lo, hi = np.percentile(a, 1), np.percentile(a, 99)
            return np.clip((a - lo) / max(hi - lo, 1e-9), 0, 1)
        u, v = norm(u), norm(v)
        fu, fv = self.eye_flip[side]
        if fu: u = 1 - u
        if fv: v = 1 - v
        return np.stack([u, v], axis=1)

    # ------------------------------------------------------------------
    def odor(self, cls: str, intensity: float = 1.0, side: str | None = None, r_max: float = 100.0) -> tuple[np.ndarray, np.ndarray]:
        """(idx, rate) for one odor class of the library at `intensity` (ORNs of one antenna if side='L'/'R')."""
        idx, rate = [], []
        for glom, wgt in ODOR_LIBRARY[cls].items():
            g = self.groups[f"glom_{glom}" + (f"_{side}" if side else "")]
            if len(g):
                idx.append(g); rate.append(np.full(len(g), wgt * intensity * r_max, np.float32))
        if not idx:
            return np.zeros(0, np.int64), np.zeros(0, np.float32)
        return np.concatenate(idx), np.concatenate(rate)

    def encode(self, obs: dict) -> tuple[np.ndarray, np.ndarray]:
        idx_parts, rate_parts = [], []

        def drive(name: str, intensity, r_max: float):
            # intensity: float (bilateral) or {"L": x, "R": y} (per antenna)
            if name in self.mask:                        # an input channel removed on purpose (run_brain.py --mask; RESEARCH_NOTES 23)
                return
            if isinstance(intensity, dict):
                for sfx in ("L", "R"):
                    g = self.groups.get(f"{name}_{sfx}", self.groups[name])
                    val = float(intensity.get(sfx, 0) or 0)
                    if len(g) and val > 0:
                        idx_parts.append(g)
                        rate_parts.append(np.full(len(g), float(np.clip(val, 0, 1)) * r_max, dtype=np.float32))
                return
            g = self.groups[name]
            if len(g) == 0 or not intensity or intensity <= 0:
                return
            idx_parts.append(g)
            rate_parts.append(np.full(len(g), float(np.clip(intensity, 0, 1)) * r_max, dtype=np.float32))

        eyes = obs.get("eyes") or {}
        if self.optic_lobe is not None and eyes.get("L") and eyes.get("R"):
            self.optic_lobe.submit(eyes)                 # pipelined: this tick's frame is processed while the brain runs
            oi, orate = self.optic_lobe.latest()         # last completed frame drives the optic-lobe neurons
            if len(oi):
                idx_parts.append(oi); rate_parts.append(orate)
            eyes = {}
        for side in ("L", "R"):
            e = eyes.get(side)
            g = self.groups[f"photo_{side}"]
            if not e or len(g) == 0:
                continue
            w, h = int(e["w"]), int(e["h"])
            px = np.asarray(e["px"], dtype=np.float32).reshape(h, w)
            uv = self.eye_uv[side]
            col = np.minimum((uv[:, 0] * w).astype(int), w - 1)
            row = np.minimum((uv[:, 1] * h).astype(int), h - 1)
            lum = px[row, col]
            idx_parts.append(g)
            rate_parts.append(lum * R_VISION)

        sm = obs.get("smell") or {}
        odors = sm.get("odors")
        if odors:                                   # odor identity: each class drives its own glomeruli (ODOR_LIBRARY)
            for cls, conc in odors.items():
                prof = ODOR_LIBRARY.get(cls)
                if not prof:
                    continue
                for glom, wgt in prof.items():
                    if isinstance(conc, dict):
                        drive(f"glom_{glom}", {k: wgt * float(v or 0) for k, v in conc.items()}, R_OLF)
                    else:
                        drive(f"glom_{glom}", wgt * float(conc or 0), R_OLF)
        else:
            drive("orn_food", sm.get("food", 0), R_OLF)
            drive("orn_aversive", sm.get("aversive", 0), R_OLF)
        drive("orn_co2", sm.get("co2", 0), R_OLF)
        drive("orn_fly", sm.get("fly", 0), R_OLF)
        drive("orn_cva", sm.get("cva", 0), R_OLF)

        ta = obs.get("taste") or {}
        drive("grn_sugar", max(ta.get("sugar", 0), 0.5 * ta.get("water", 0)), R_TASTE)
        drive("grn_bitter", ta.get("bitter", 0), R_TASTE)
        drive("grn_ppk25", ta.get("fly_female", 0), R_TASTE)   # touching a female
        drive("grn_ppk23", ta.get("fly_male", 0), R_TASTE)     # touching a male

        me = obs.get("mechano") or {}
        drive("jo_wind", 0.5 * me.get("speed", 0) + me.get("wind", 0), R_MECH)
        drive("jo_sound", obs.get("sound", 0), R_MECH)
        fly_contact = bool(ta.get("fly_female", 0) or ta.get("fly_male", 0))
        drive("bristle", 1.0 if (me.get("hit") or me.get("collided") or fly_contact) else 0.0, R_BURST)   # physical contact incl. another fly
        drive("groom_touch", 1.0 if me.get("in_water") else 0.0, R_MECH)

        th = obs.get("thermo") or {}
        drive("thermo_hot", th.get("hot", 0), R_THERMO)
        drive("thermo_cold", th.get("cold", 0), R_THERMO)
        drive("hygro_moist", 1.0 if me.get("in_water") else 0.0, R_THERMO)

        if not idx_parts:
            return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.float32)
        return np.concatenate(idx_parts), np.concatenate(rate_parts)
