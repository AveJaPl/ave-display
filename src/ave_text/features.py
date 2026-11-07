"""Cechy OpenType Ave Text w składni plików .fea (fontTools.feaLib).

- tnum: cyfry tabelaryczne (stała szerokość) zamiast proporcjonalnych,
- kern: kerning par (dochodzi w kamieniu milowym odstępów).
"""

from __future__ import annotations

from .glyphs.registry import REGISTRY
from .glyphs.symbols import DIGIT_NAMES
from .kerning import kern_feature
from .style import Style


def tnum() -> str:
    pairs = [(d, f"{d}.tf") for d in DIGIT_NAMES if f"{d}.tf" in REGISTRY]
    lines = ["feature tnum {"] + [f"    sub {a} by {b};" for a, b in pairs] + ["} tnum;"]
    return "\n".join(lines)


def feature_file(s: Style, built) -> str:
    parts = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "", tnum(), "", kern_feature(built)]
    return "\n".join(parts) + "\n"
