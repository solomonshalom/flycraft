"""Per-tick CSV log for analysis (one row per observation/decision)."""
from __future__ import annotations

import csv
import os
import time


class Recorder:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        self.f = open(path, "w", newline="")
        self.w = None
        self.n = 0

    def write(self, row: dict) -> None:
        if self.w is None:
            self.w = csv.DictWriter(self.f, fieldnames=list(row.keys()), extrasaction="ignore", restval="")
            self.w.writeheader()
        self.w.writerow(row)
        self.n += 1
        if self.n % 20 == 0:
            self.f.flush()

    def close(self) -> None:
        self.f.flush()
        self.f.close()


def flatten(prefix: str, d: dict, out: dict) -> dict:
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            flatten(f"{prefix}{k}_", v, out)
        elif isinstance(v, (int, float, bool, str)) or v is None:
            out[f"{prefix}{k}"] = v
    return out
