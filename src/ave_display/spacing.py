"""Światła boczne i kerning.

Światła liczone są w układzie pionowym od skrajnego punktu obrysu (albo od trzonu,
gdy glif ma `left_edge`). Wartości kerningu dobrane z profili glifów (porównanie
pola światła między parą z parą HH) i sprawdzone wizualnie na podglądach.
"""


class SB:
    STEM = 56
    ROUND = 44
    BAR = 30
    DIAG = 32
    TIP = 140
    LEG = 10
    PUNCT = 50


SPACE_WIDTH = 320

GROUPS = {
    "A": ["A", "Aogonek"],
    "L": ["L", "Lslash"],
    "round_right": ["O", "Oacute", "D", "zero"],
    "round_left": ["O", "Oacute", "Q", "C", "Cacute", "G", "zero", "six"],
    "quote": ["quotesingle", "quotedbl"],
    "dot": ["period", "comma"],
    "dash": ["hyphen", "endash"],
}

KERNING: list[tuple[str, str, int]] = [
    ("V", "@A", -260), ("W", "@A", -230), ("Y", "@A", -260), ("T", "@A", -215),
    ("F", "@A", -185), ("P", "@A", -135), ("seven", "@A", -185), ("@quote", "@A", -195),
    ("@A", "@quote", -30),

    ("@L", "T", -200), ("@L", "V", -205), ("@L", "W", -175), ("@L", "Y", -235),
    ("@L", "@quote", -200), ("@L", "@dash", -120),

    ("R", "T", -60), ("R", "V", -125), ("R", "W", -115), ("R", "Y", -165),
    ("B", "V", -95), ("B", "W", -85), ("B", "Y", -125),
    ("@round_right", "V", -75), ("@round_right", "W", -65), ("@round_right", "Y", -115),
    ("@round_right", "X", -55),

    ("V", "@round_left", -45), ("W", "@round_left", -35), ("Y", "@round_left", -60),
    ("K", "@round_left", -110), ("X", "@round_left", -55),

    ("T", "J", -200), ("V", "J", -145), ("W", "J", -115), ("Y", "J", -215), ("F", "J", -60),

    ("T", "@dot", -220), ("V", "@dot", -225), ("W", "@dot", -185), ("Y", "@dot", -245),
    ("F", "@dot", -200), ("P", "@dot", -200), ("seven", "@dot", -150),

    ("@dash", "T", -80), ("T", "@dash", -80), ("@dash", "V", -75), ("V", "@dash", -75),
    ("@dash", "Y", -115), ("Y", "@dash", -115),
]


def expand(token: str) -> list[str]:
    return GROUPS[token[1:]] if token.startswith("@") else [token]


def kerning_pairs() -> dict[tuple[str, str], int]:
    pairs: dict[tuple[str, str], int] = {}
    for left, right, value in KERNING:
        for a in expand(left):
            for b in expand(right):
                pairs[(a, b)] = value
    return pairs
