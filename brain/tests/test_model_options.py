"""Unit tests for the sign rule, the eLN scale and the odor library (no data files needed).
  python -m pytest brain/tests/test_model_options.py -q     or     python brain/tests/test_model_options.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, pandas as pd, scipy.sparse as sp
from flybrain.connectome import Connectome, apply_model_options, parse_known_nt
from flybrain.senses import ODOR_LIBRARY


def test_parse_known_nt():
    assert parse_known_nt("gaba, MIP; acetylcholine-negative") == "gaba"
    assert parse_known_nt("acetylcholine; sNPF; acetylcholine, sNPF") == "acetylcholine"
    assert parse_known_nt("gaba-negative") is None
    assert parse_known_nt("acetylcholine-negative, glutamate-negative, gaba-negative") is None
    assert parse_known_nt("histamine; acetylcholine, histamine") == "histamine"
    assert parse_known_nt(None) is None and parse_known_nt(float("nan")) is None


def _toy():
    # 5 neurons: 0 = ORN (ACh, predicted +), 1 = LN predicted + but known GABA, 2 = LN cholinergic eLN (+),
    # 3 = PN, 4 = photoreceptor predicted + but known histamine
    n = 5
    neurons = pd.DataFrame({
        "cell_type": ["ORN_DM2", "lLN2P_b", "lLN1_bc", "DM2_adPN", "R1-6"],
        "cell_class": ["olfactory", "ALLN", "ALLN", "ALPN", "photoreceptor"],
        "known_nt": [None, "gaba, MIP; acetylcholine-negative", "acetylcholine", None, "histamine"],
        "side": ["left"] * n, "hemibrain_type": [None] * n, "cell_sub_class": [None] * n, "super_class": ["sensory"] * n,
    })
    W = sp.csr_matrix(np.array([[0, 3, 2, 10, 0], [0, 0, 4, 6, 0], [0, 5, 0, 8, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 7]], dtype=np.float32))
    return Connectome(neurons=neurons, W=W, root_ids=np.arange(n), idx_of={i: i for i in range(n)}, variant="toy")


def test_known_signs_flip_rows():
    cx = apply_model_options(_toy(), signs="known")
    W = cx.W.toarray()
    assert cx.n_sign_flipped == 2 and cx.variant == "toy+known"
    assert (W[1] <= 0).all() and W[1, 2] == -4 and W[1, 3] == -6      # known GABA LN now inhibitory
    assert (W[4] <= 0).all() and W[4, 4] == -7                          # histamine photoreceptor now inhibitory
    assert W[0, 3] == 10 and W[2, 3] == 8                               # untouched rows


def test_eln_scale_only_excitatory_lns():
    cx = apply_model_options(_toy(), signs="known", eln_scale=0.25)
    W = cx.W.toarray()
    assert cx.n_eln == 1 and cx.variant == "toy+known+eln0.25"
    assert W[2, 3] == 2.0 and W[2, 1] == 1.25                           # the eLN's output scaled
    assert W[1, 3] == -6 and W[0, 3] == 10                              # the inhibitory LN and the ORN untouched


def test_shiu_default_is_identity():
    cx0 = _toy(); w0 = cx0.W.toarray().copy()
    cx = apply_model_options(cx0, signs="shiu", eln_scale=1.0)
    assert np.array_equal(cx.W.toarray(), w0) and cx.variant == "toy"


def test_odor_library_shape():
    for cls, prof in ODOR_LIBRARY.items():
        assert prof and max(prof.values()) == 1.0, cls          # every class has a strongest glomerulus at 1.0
        assert all(0 < v <= 1 for v in prof.values())
    tops = {max(p, key=p.get) for c, p in ODOR_LIBRARY.items() if c != "food"}
    assert len(tops) == len(ODOR_LIBRARY) - 1                    # distinct strongest glomerulus per class


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
