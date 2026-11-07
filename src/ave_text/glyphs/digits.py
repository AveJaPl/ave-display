"""Cyfry wersalikowe (wysokość 700 j.), proporcjonalne.

Kanciaste jak O: zaokrąglone narożniki, cięte końcówki (2, 3, 5, 6, 9), czwórka z ukośnikiem
(czytelniejsza w tekście niż „otwarta” czwórka). Cyfry tabelaryczne dochodzą przez cechę tnum.
"""

from __future__ import annotations

from ..shapes import Shape, box, corner, cut_left, cut_right, diagonal, inner_corner, outline, polygon, rect, ring
from ..style import CAP, FAR, OVS, Style
from .registry import glyph
from .upper import cap_corners, cap_diag

W_ZERO = 472
W_TWO = 452
W_THREE = 440
W_FOUR = 508
W_FIVE = 448
W_SIX = 468
W_SEVEN = 440
W_EIGHT = 476
ONE_FLAG = 150


def _st(s: Style) -> float:
    return s.stem_cap * 0.96


@glyph("zero", "0", ("cap_round", 0.9), ("cap_round", 0.9))
def zero(s: Style) -> Shape:
    return ring(s, 0, -OVS, s.w(W_ZERO), CAP + OVS, _st(s), s.hair_cap, cap_corners(s, 0.9))


@glyph("one", "1", 24, ("cap_stem", 0.9))
def one(s: Style) -> Shape:
    st, hh = _st(s), s.hair_cap
    x = s.w(ONE_FLAG)
    depth = x * 0.78
    tv = hh * 1.2
    flag = polygon([(0, CAP - depth - tv), (x + 1, CAP - tv), (x + 1, CAP), (0, CAP - depth)])
    return rect(x, 0, x + st, CAP) | flag


@glyph("two", "2", 38, ("cap_round", 0.75))
def two(s: Style) -> Shape:
    st, hh, w = _st(s), s.hair_cap, s.w(W_TWO)
    top = CAP + OVS
    c = cap_corners(s, 0.9)
    y0 = CAP * 0.45 - hh / 2
    y1 = y0 + hh
    start = s.w(6)
    shape = outline([
        (start - 200, top),
        (w, top, c["tr"]),
        (w, y0, c["br"]),
        (st, y0, inner_corner(s, c["tl"], st, hh)),
        (st, hh),
        (w, hh), (w, 0), (0, 0),
        (0, y1, c["tl"]),
        (w - st, y1, inner_corner(s, c["br"], st, hh)),
        (w - st, top - hh, inner_corner(s, c["tr"], st, hh)),
        (start - 200, top - hh),
    ])
    return cut_left(s, shape, start, top - hh - 1, top + 1)


def _stacked(s: Style, w: float, ym: float, upper_inset: float) -> tuple[Shape, Shape]:
    """Dwa kanciaste brzuszki jeden nad drugim (3 i 8): górny węższy o upper_inset z każdej strony."""
    st, hh = _st(s), s.hair_cap
    c = cap_corners(s, 0.85)
    waist = cap_corners(s, 0.6)
    upper = box(upper_inset, ym - hh / 2, w - upper_inset, CAP + OVS, waist["bl"], waist["br"], c["tr"], c["tl"])
    upper = upper - box(upper_inset + st, ym + hh / 2, w - upper_inset - st, CAP + OVS - hh,
                        inner_corner(s, waist["bl"], st, hh), inner_corner(s, waist["br"], st, hh),
                        inner_corner(s, c["tr"], st, hh), inner_corner(s, c["tl"], st, hh))
    lower = box(0, -OVS, w, ym + hh / 2, c["bl"], c["br"], waist["tr"], waist["tl"])
    lower = lower - box(st, -OVS + hh, w - st, ym - hh / 2,
                        inner_corner(s, c["bl"], st, hh), inner_corner(s, c["br"], st, hh),
                        inner_corner(s, waist["tr"], st, hh), inner_corner(s, waist["tl"], st, hh))
    return upper, lower


@glyph("three", "3", 28, ("cap_round", 0.9))
def three(s: Style) -> Shape:
    st, hh, w = _st(s), s.hair_cap, s.w(W_THREE)
    c = cap_corners(s, 0.85)
    waist = cap_corners(s, 0.6)
    ym = CAP * 0.54
    inset = s.w(16)
    upper = box(-200, ym - hh / 2, w - inset, CAP + OVS, br=waist["br"], tr=c["tr"]) - box(
        -FAR, ym + hh / 2, w - inset - st, CAP + OVS - hh,
        br=inner_corner(s, waist["br"], st, hh), tr=inner_corner(s, c["tr"], st, hh))
    lower = box(-200, -OVS, w, ym + hh / 2, br=c["br"], tr=waist["tr"]) - box(
        -FAR, -OVS + hh, w - st, ym - hh / 2,
        br=inner_corner(s, c["br"], st, hh), tr=inner_corner(s, waist["tr"], st, hh))
    shape = upper | lower
    shape = cut_left(s, shape, s.w(14), CAP + OVS - hh - 1, CAP + OVS + 1)
    shape = cut_left(s, shape, w * 0.3, ym - hh / 2 - 1, ym + hh / 2 + 1)
    return cut_left(s, shape, 0, -OVS - 1, -OVS + hh + 1)


@glyph("four", "4", 14, 28)
def four(s: Style) -> Shape:
    st, hh, w = _st(s), s.hair_cap, s.w(W_FOUR)
    x = w - st - s.w(58)
    y_bar = CAP * 0.22
    diag = diagonal((0, y_bar + hh), (x + st, CAP), cap_diag(s, 0.9), y_bar, CAP)
    return rect(x, 0, x + st, CAP) | rect(0, y_bar, w, y_bar + hh) | (diag & rect(0, 0, x + st, CAP))


@glyph("five", "5", 38, ("cap_round", 0.9))
def five(s: Style) -> Shape:
    st, hh, w = _st(s), s.hair_cap, s.w(W_FIVE)
    c = cap_corners(s, 0.85)
    y_top = CAP * 0.60
    bowl = box(0, -OVS, w, y_top, br=c["br"], tr=c["tr"]) - box(
        -FAR, -OVS + hh, w - st, y_top - hh, br=inner_corner(s, c["br"], st, hh), tr=inner_corner(s, c["tr"], st, hh))
    bowl = cut_left(s, bowl, 0, -OVS - 1, -OVS + hh + 1)
    return bowl | rect(0, y_top - hh, st, CAP) | rect(0, CAP - hh, w - s.w(10), CAP)


@glyph("six", "6", ("cap_round", 0.9), 30)
def six(s: Style) -> Shape:
    st, hh, w = _st(s), s.hair_cap, s.w(W_SIX)
    c = cap_corners(s, 0.85)
    y_top = CAP * 0.58
    outer = box(0, -OVS, w, CAP + OVS, c["bl"], c["br"], c["tr"], c["tl"])
    upper = box(st, y_top, FAR, CAP + OVS - hh, tl=inner_corner(s, c["tl"], st, hh))
    lower = box(st, -OVS + hh, w - st, y_top - hh,
                inner_corner(s, c["bl"], st, hh), inner_corner(s, c["br"], st, hh),
                inner_corner(s, c["tr"], st, hh), corner(s, 10))
    shape = outer - upper - lower
    return cut_right(s, shape, w - c["tr"][0] * 0.55, y_top + 1, FAR, y_ref=CAP + OVS - hh / 2)


@glyph("seven", "7", 22, 18)
def seven(s: Style) -> Shape:
    hh, w = s.hair_cap, s.w(W_SEVEN)
    diag = diagonal((w * 0.2, 0), (w, CAP - hh), cap_diag(s, 0.95), 0, CAP - hh / 2)
    return rect(0, CAP - hh, w, CAP) | (diag & rect(0, 0, w, CAP))


@glyph("eight", "8", ("cap_round", 0.9), ("cap_round", 0.9))
def eight(s: Style) -> Shape:
    upper, lower = _stacked(s, s.w(W_EIGHT), CAP * 0.545, s.w(18))
    return upper | lower


@glyph("nine", "9", 30, ("cap_round", 0.9))
def nine(s: Style) -> Shape:
    w = s.w(W_SIX)
    return six(s).rotated_180(w / 2, CAP / 2)
