"""Znaki diakrytyczne, litery z akcentami i samodzielne znaki akcentów.

Każdy akcent rysujemy wokół punktu (0, 0) w dwóch wersjach: dla małych liter i spłaszczonej
dla wielkich (`cap=True`). Akcenty górne mają dół na y = 0 i środek w x = 0; akcenty dolne
(ogonek, cedylla) mają punkt zaczepienia (0, 0) na dole litery. Litera z akcentem to litera
bazowa plus akcent przesunięty do kotwicy; odstępy dziedziczy po literze bazowej.
"""

from __future__ import annotations

from typing import Callable, Union

from fontTools.agl import UV2AGL

from ..shapes import Shape, box, corner, cut_left, cut_right, inner_corner, outline, polygon, rect, ring
from ..style import ASC, CAP, OVS, XH, Style
from .common import apex, vertex
from .punct import dot_size, quote_shape
from .registry import REGISTRY, glyph

TOP_LOWER = XH + 96
TOP_CAP = CAP + 58
TOP_TALL = ASC + 40
OGONEK_DEPTH = 186
OGONEK_FOOT = 72

Mark = Callable[[Style, bool], Shape]


def _t(s: Style, cap: bool) -> tuple[float, float]:
    return (s.stem_cap, s.hair_cap) if cap else (s.stem, s.hair)


# --- kształty akcentów ---------------------------------------------------------------------

def acute(s: Style, cap: bool) -> Shape:
    st, _ = _t(s, cap)
    aw, ah, dx = (st * 1.04, 92.0, 104.0) if cap else (st * 1.1, 118.0, 92.0)
    x0 = -(aw + dx) / 2
    return polygon([(x0, 0), (x0 + aw, 0), (x0 + aw + dx, ah), (x0 + dx, ah)])


def grave(s: Style, cap: bool) -> Shape:
    return acute(s, cap).mirrored_x(0)


def hungarumlaut(s: Style, cap: bool) -> Shape:
    st, _ = _t(s, cap)
    one = acute(s, cap).affine(0.86, 0, 0, 1, 0, 0)
    gap = st * 1.25
    return one.moved(-gap / 2 - 6) | one.moved(gap / 2 + 6)


def circumflex(s: Style, cap: bool) -> Shape:
    st, _ = _t(s, cap)
    w, h = (296.0, 96.0) if cap else (268.0, 122.0)
    td = st * 0.82
    return apex((-w / 2, 0), (w / 2, 0), 0, st * 0.7, td, h)


def caron(s: Style, cap: bool) -> Shape:
    st, _ = _t(s, cap)
    w, h = (296.0, 96.0) if cap else (268.0, 122.0)
    return vertex((-w / 2, h), (w / 2, h), 0, st * 0.7, st * 0.82)


def tilde(s: Style, cap: bool) -> Shape:
    st, hh = _t(s, cap)
    w, h = (264.0, 78.0) if cap else (244.0, 96.0)
    t = hh * 1.02
    r = corner(s, 34, 22, 0.6)
    p = [(-w / 2, h * 0.2), (-w / 2 + w * 0.3, h * 0.8), (-w / 2 + w * 0.7, h * 0.2), (w / 2, h * 0.8)]
    return outline([
        (p[0][0], p[0][1] + t / 2), (p[1][0], p[1][1] + t / 2, r), (p[2][0], p[2][1] + t / 2, r), (p[3][0], p[3][1] + t / 2),
        (p[3][0], p[3][1] - t / 2), (p[2][0], p[2][1] - t / 2, r), (p[1][0], p[1][1] - t / 2, r), (p[0][0], p[0][1] - t / 2),
    ]).moved(0, t / 2 - h * 0.2 + 2)


def dotaccent(s: Style, cap: bool) -> Shape:
    d = dot_size(s)
    r = corner(s, d * 0.24)
    return box(-d / 2, 0, d / 2, d, r, r, r, r)


def dieresis(s: Style, cap: bool) -> Shape:
    d = dot_size(s)
    gap = d * (0.95 if cap else 0.9)
    return dotaccent(s, cap).moved(-gap / 2 - d / 2) | dotaccent(s, cap).moved(gap / 2 + d / 2)


def ring_mark(s: Style, cap: bool) -> Shape:
    st, hh = _t(s, cap)
    w, h = (176.0, 150.0) if cap else (164.0, 164.0)
    return ring(s, -w / 2, 0, w / 2, h, st * 0.72, hh * 0.86, {
        "bl": corner(s, 52), "br": corner(s, 52), "tr": corner(s, 52), "tl": corner(s, 52)})


def macron(s: Style, cap: bool) -> Shape:
    w = 268.0 if cap else 240.0
    return rect(-w / 2, 6, w / 2, 6 + s.bar)


def breve(s: Style, cap: bool) -> Shape:
    st, hh = _t(s, cap)
    w, h = (248.0, 92.0) if cap else (236.0, 112.0)
    side, base = min(st * 0.78, w * 0.3), min(hh * 0.92, h * 0.62)
    c = corner(s, 64, 52)
    return box(-w / 2, 0, w / 2, h, bl=c, br=c) - box(-w / 2 + side, base, w / 2 - side, h + 1,
                                                       bl=inner_corner(s, c, side, base),
                                                       br=inner_corner(s, c, side, base))


def ogonek(s: Style, cap: bool) -> Shape:
    """Ogonek w kształcie L: pionowa kreska pod literą, zaokrąglony narożnik, stopka w prawo."""
    st, hh = _t(s, cap)
    t, th = st * 0.9, hh * 0.9
    bottom = -OGONEK_DEPTH
    end = t / 2 + OGONEK_FOOT
    bl = corner(s, t * 1.15, t * 1.0)
    shape = outline([
        (-t / 2, OVS + th * 0.75), (-t / 2, bottom, bl), (end + 200, bottom), (end + 200, bottom + th),
        (t / 2, bottom + th, inner_corner(s, bl, t, th)), (t / 2, OVS + th * 0.75),
    ])
    return cut_right(s, shape, end, bottom - 1, bottom + th + 1)


def cedilla(s: Style, cap: bool) -> Shape:
    """Kanciasta cedylla: krótki trzonek pod literą i haczyk otwarty w lewo."""
    st, hh = _t(s, cap)
    # grubości ograniczone, żeby w Bold haczyk nie zszedł poniżej linii fontu (-250)
    t, th = min(st * 0.8, 104.0), min(hh * 0.86, 74.0)
    top = -40.0
    bottom = top - 2 * th - max(th * 0.7, 40.0)
    right, left = 92.0, -86.0
    c = corner(s, 40, 36)
    shape = outline([
        (-t / 2, OVS + th), (-t / 2, top - th),
        (right - t, top - th, inner_corner(s, c, t, th)), (right - t, bottom + th, inner_corner(s, c, t, th)),
        (left - 200, bottom + th), (left - 200, bottom),
        (right, bottom, c), (right, top, c), (t / 2, top), (t / 2, OVS + th),
    ])
    return cut_left(s, shape, left, bottom - 1, bottom + th + 1)


def caron_alt(s: Style, cap: bool) -> Shape:
    """Haczyk ď ľ ť Ľ: kreska jak apostrof, dół na y = 0, lewa krawędź w x = 0."""
    q = quote_shape(s)
    x0, y0, _, _ = q.bounds
    return q.moved(-x0, -y0)


# --- kotwice ------------------------------------------------------------------------------

def _center(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds
    return (x0 + x1) / 2


Height = Union[float, Callable[[Style], float], None]


def i_dot_bottom(s: Style) -> float:
    """Dół kropki nad i (kropka nad ż ma stać na tej samej wysokości)."""
    d = dot_size(s)
    return ASC + (d - 92.4) * 0.3 - d


def top(mark: Mark, cap: bool, x: Callable[[Style, Shape], float] | None = None, y: Height = None,
        nudge: float = 0.0):
    def place(s: Style, base: Shape) -> Shape:
        if y is None:
            bottom = TOP_CAP if cap else TOP_LOWER
        else:
            bottom = y(s) if callable(y) else y
        cx = _center(base) if x is None else x(s, base)
        return mark(s, cap).moved(cx + nudge, bottom)
    return place


def below(mark: Mark, cap: bool, x: Callable[[Style, Shape], float] | None = None):
    def place(s: Style, base: Shape) -> Shape:
        _, y0, _, _ = base.bounds
        cx = _center(base) if x is None else x(s, base)
        return mark(s, cap).moved(cx, max(y0, -OVS))
    return place


def stem_center(cap: bool = False, offset: float = 0.0):
    def at(s: Style, base: Shape) -> float:
        x0, _, _, _ = base.bounds
        return x0 + (s.stem_cap if cap else s.stem) / 2 + offset
    return at


def right_edge(fraction_of_stem: float, cap: bool = False):
    def at(s: Style, base: Shape) -> float:
        _, _, x1, _ = base.bounds
        return x1 - (s.stem_cap if cap else s.stem) * fraction_of_stem
    return at


def width_fraction(fraction: float):
    def at(s: Style, base: Shape) -> float:
        x0, _, x1, _ = base.bounds
        return x0 + (x1 - x0) * fraction
    return at


def t_stem(s: Style, base: Shape) -> float:
    from .lower import T_LEFT
    x0, _, _, _ = base.bounds
    return x0 + s.w(T_LEFT) + s.stem / 2


def stroke_bar(s: Style, cap: bool, x0: float, x1: float, y_mid: float) -> Shape:
    """Ukośna kreska ł/Ł o pionowych końcach, wznosząca się w prawo."""
    th = (s.hair_cap if cap else s.hair) * 0.98
    rise = (x1 - x0) * 0.52
    tv = th * (1 + 0.52 ** 2) ** 0.5
    y0 = y_mid - rise / 2 - tv / 2
    return polygon([(x0, y0), (x1, y0 + rise), (x1, y0 + rise + tv), (x0, y0 + tv)])


def lslash_bar(cap: bool):
    def place(s: Style, base: Shape) -> Shape:
        st = s.stem_cap if cap else s.stem
        if cap:
            return stroke_bar(s, True, -s.w(72), st + s.w(96), CAP * 0.46)
        return stroke_bar(s, False, -s.w(76), st + s.w(76), 330)
    return place


def d_bar(cap: bool):
    """Pozioma kreska Đ/Ð przez trzon albo đ przez wydłużenie d."""
    def place(s: Style, base: Shape) -> Shape:
        if cap:
            hh, st = s.hair_cap, s.stem_cap
            return rect(-s.w(64), CAP / 2 - hh / 2, st + s.w(84), CAP / 2 + hh / 2)
        _, _, x1, _ = base.bounds
        return rect(x1 - s.stem - s.w(84), 620 - s.bar / 2, x1 + s.w(40), 620 + s.bar / 2)
    return place


def apostrophe_after(cap: bool):
    def place(s: Style, base: Shape) -> Shape:
        if cap:
            return caron_alt(s, cap).moved(s.stem_cap + s.w(46), CAP - 200)
        _, _, x1, y1 = base.bounds
        stem_right = x1 if y1 >= ASC - 1 else t_stem(s, base) + s.stem / 2
        top_y = ASC if y1 >= ASC - 1 else y1
        return caron_alt(s, cap).moved(stem_right + s.w(38), top_y - 200)
    return place


# --- rejestracja ----------------------------------------------------------------------------

def compose(base: str, *marks):
    def build(s: Style) -> Shape:
        shape = REGISTRY[base].build(s)
        out = shape
        for mark in marks:
            out = out | mark(s, shape)
        return out
    return build


def agl_name(char: str) -> str:
    return UV2AGL.get(ord(char), f"uni{ord(char):04X}")


def accented(char: str, base: str, *marks, own_right: float | None = None) -> None:
    """Litera z akcentem. own_right: akcent wystaje w prawo (ď, ľ, ť), więc prawe światło liczymy
    od obrysu całości zamiast od litery bazowej."""
    name = agl_name(char)
    if own_right is None:
        glyph(name, char, spacing_from=base)(compose(base, *marks))
    else:
        glyph(name, char, REGISTRY[base].left, own_right)(compose(base, *marks))


L, C = False, True
TALL_ACUTE = top(acute, L, x=stem_center(offset=26), y=TOP_TALL)

LOWER = {
    "grave": ("àèìòù", "aeıou", top(grave, L, nudge=-10)),
    "acute": ("áéíóúýćńśźŕ", "aeıouycnszr", top(acute, L, nudge=10)),
    "circumflex": ("âêîôû", "aeıou", top(circumflex, L)),
    "tilde": ("ãñõ", "ano", top(tilde, L)),
    "dieresis": ("äëïöüÿ", "aeıouy", top(dieresis, L, y=TOP_LOWER + 12)),
    "ring": ("åů", "au", top(ring_mark, L, y=TOP_LOWER - 8)),
    "caron": ("čěňřšž", "cenrsz", top(caron, L)),
    "breve": ("ă", "a", top(breve, L)),
    "hungarumlaut": ("őű", "ou", top(hungarumlaut, L, nudge=6)),
    "dotaccent": ("ż", "z", top(dotaccent, L, y=i_dot_bottom)),
    "cedilla": ("çş", "cs", below(cedilla, L)),
}
UPPER = {
    "grave": ("ÀÈÌÒÙ", "AEIOU", top(grave, C, nudge=-8)),
    "acute": ("ÁÉÍÓÚÝĆŃŚŹŔ", "AEIOUYCNSZR", top(acute, C, nudge=8)),
    "circumflex": ("ÂÊÎÔÛ", "AEIOU", top(circumflex, C)),
    "tilde": ("ÃÑÕ", "ANO", top(tilde, C)),
    "dieresis": ("ÄËÏÖÜŸ", "AEIOUY", top(dieresis, C, y=TOP_CAP + 4)),
    "ring": ("ÅŮ", "AU", top(ring_mark, C, y=CAP + 44)),
    "caron": ("ČĎĚŇŘŠŤŽ", "CDENRSTZ", top(caron, C)),
    "breve": ("Ă", "A", top(breve, C)),
    "hungarumlaut": ("ŐŰ", "OU", top(hungarumlaut, C, nudge=6)),
    "dotaccent": ("Ż", "Z", top(dotaccent, C, y=TOP_CAP + 4)),
    "cedilla": ("ÇŞŢ", "CST", below(cedilla, C)),
}

BASE_NAMES = {"ı": "dotlessi"}

for table in (LOWER, UPPER):
    for kind, (chars, bases, mark) in table.items():
        for ch, base in zip(chars, bases):
            accented(ch, BASE_NAMES.get(base, base), mark)

accented("ţ", "t", below(cedilla, L, x=t_stem))
accented("ĺ", "l", TALL_ACUTE)
accented("Ĺ", "L", top(acute, C, x=stem_center(cap=True, offset=34)))
accented("ą", "a", below(ogonek, L, x=right_edge(0.62)))
accented("ę", "e", below(ogonek, L, x=width_fraction(0.64)))
accented("Ą", "A", below(ogonek, C, x=right_edge(0.66, cap=True)))
accented("Ę", "E", below(ogonek, C, x=width_fraction(0.7)))
accented("ł", "l", lslash_bar(L))
accented("Ł", "L", lslash_bar(C))
accented("đ", "d", d_bar(L))
accented("Đ", "D", d_bar(C))
accented("Ð", "D", d_bar(C))
accented("ď", "d", apostrophe_after(L), own_right=34)
accented("ľ", "l", apostrophe_after(L), own_right=30)
accented("ť", "t", apostrophe_after(L), own_right=24)
accented("Ľ", "L", apostrophe_after(C))


# --- samodzielne znaki akcentów ----------------------------------------------------------------

def spacing_mark(name: str, code: int, mark: Mark, y: float, side: float = 36) -> None:
    glyph(name, [code], side, side)(lambda s: mark(s, False).moved(0, y))


spacing_mark("grave", 0x60, grave, TOP_LOWER)
spacing_mark("acute", 0xB4, acute, TOP_LOWER)
spacing_mark("circumflex", 0x2C6, circumflex, TOP_LOWER)
spacing_mark("caron", 0x2C7, caron, TOP_LOWER)
spacing_mark("tilde", 0x2DC, tilde, TOP_LOWER)
spacing_mark("dieresis", 0xA8, dieresis, TOP_LOWER + 12)
spacing_mark("ring", 0x2DA, ring_mark, TOP_LOWER - 8)
spacing_mark("macron", 0xAF, macron, TOP_LOWER + 20)
spacing_mark("breve", 0x2D8, breve, TOP_LOWER)
spacing_mark("dotaccent", 0x2D9, dotaccent, TOP_LOWER + 10)
spacing_mark("hungarumlaut", 0x2DD, hungarumlaut, TOP_LOWER)
spacing_mark("cedilla", 0xB8, cedilla, 0)
spacing_mark("ogonek", 0x2DB, ogonek, 0)
