"""Wielkie litery A-Z w układzie pionowym.

Te same reguły co w małych literach (kanciaste brzuszki, cięte końcówki, ukośne kreski przycięte
do obrysu), ale z grubościami i promieniami wersalików (stem_cap, hair_cap, radius_cap).
Wysokość wersalików 700 j. jest wspólna z Ave Display.
"""

from __future__ import annotations

from ..shapes import (
    Shape, box, corners_of, cut_left, cut_right, diagonal, inner_corner,
    polygon, rect, ring, band,
)
from ..style import CAP, FAR, OVS, Style
from .common import apex, diag_thickness, k_shape, s_shape, vertex
from .registry import glyph

MID = CAP / 2 + 8
TERMINAL_ROUND = 0.4

W_A = 612
W_B_LOW, W_B_UP = 520, 488
W_C = 500
W_D = 540
W_E, W_E_MID = 446, 408
W_F = 430
W_G = 544
W_H = 520
W_J = 396
W_K = 532
W_L = 420
W_M = 668
W_N = 540
W_O = 562
W_P = 504
W_R = 516
W_S = 480
W_T = 524
W_U = 524
W_V = 596
W_W = 884
W_X = 572
W_Y = 576
W_Z = 500


def cap_corners(s: Style, factor: float = 1.0):
    return corners_of(s, s.radius_cap * factor)


def cap_diag(s: Style, factor: float = 0.94) -> float:
    return diag_thickness(s, factor, s.stem_cap)


def bar(s: Style, y_mid: float, x0: float, x1: float) -> Shape:
    hh = s.hair_cap
    return rect(x0, y_mid - hh / 2, x1, y_mid + hh / 2)


@glyph("A", "A", 12, 12)
def A(s: Style) -> Shape:
    w, st = s.w(W_A), s.stem_cap
    flat = st * 0.9
    body = apex((0, 0), (w, 0), w / 2, flat, cap_diag(s), CAP)
    hull = polygon([(0, 0), (w / 2 - flat / 2, CAP), (w / 2 + flat / 2, CAP), (w, 0)])
    return body | (bar(s, CAP * 0.31, 0, w) & hull)


@glyph("B", "B", "cap_stem", ("cap_round", 0.9))
def B(s: Style) -> Shape:
    st, hh = s.stem_cap, s.hair_cap
    lo, up = s.w(W_B_LOW), s.w(W_B_UP)
    c = cap_corners(s)
    waist = cap_corners(s, 0.62)
    ym = CAP * 0.535
    upper = box(0, ym - hh / 2, up, CAP, br=waist["br"], tr=c["tr"]) - box(
        st, ym + hh / 2, up - st, CAP - hh, br=inner_corner(s, waist["br"], st, hh), tr=inner_corner(s, c["tr"], st, hh))
    lower = box(0, 0, lo, ym + hh / 2, br=c["br"], tr=waist["tr"]) - box(
        st, hh, lo - st, ym - hh / 2, br=inner_corner(s, c["br"], st, hh), tr=inner_corner(s, waist["tr"], st, hh))
    return upper | lower


def open_cap_round(s: Style, w: float) -> tuple[Shape, dict]:
    st, hh = s.stem_cap, s.hair_cap
    c = cap_corners(s)
    reach = w + c["tr"][0] * (1 - TERMINAL_ROUND)
    outer = box(0, -OVS, reach, CAP + OVS, c["bl"], c["br"], c["tr"], c["tl"])
    counter = box(st, -OVS + hh, FAR, CAP + OVS - hh,
                  bl=inner_corner(s, c["bl"], st, hh), tl=inner_corner(s, c["tl"], st, hh))
    return outer - counter, c


@glyph("C", "C", "cap_round", ("cap_round", 0.72))
def C(s: Style) -> Shape:
    w, hh = s.w(W_C), s.hair_cap
    shape, _ = open_cap_round(s, w)
    shape = cut_right(s, shape, w, CAP / 2, FAR, y_ref=CAP + OVS - hh / 2)
    return cut_right(s, shape, w, -FAR, CAP / 2, y_ref=-OVS + hh / 2)


@glyph("D", "D", "cap_stem", "cap_round")
def D(s: Style) -> Shape:
    w, st, hh = s.w(W_D), s.stem_cap, s.hair_cap
    c = cap_corners(s)
    return box(0, 0, w, CAP, tr=c["tr"], br=c["br"]) - box(
        st, hh, w - st, CAP - hh, tr=inner_corner(s, c["tr"], st, hh), br=inner_corner(s, c["br"], st, hh))


@glyph("E", "E", "cap_stem", 40)
def E(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(W_E)
    return rect(0, 0, st, CAP) | rect(0, CAP - hh, w, CAP) | bar(s, MID, 0, s.w(W_E_MID)) | rect(0, 0, w, hh)


@glyph("F", "F", "cap_stem", 30)
def F(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(W_F)
    return rect(0, 0, st, CAP) | rect(0, CAP - hh, w, CAP) | bar(s, MID - 10, 0, s.w(W_E_MID) * 0.96)


@glyph("G", "G", "cap_round", ("cap_stem", 0.92))
def G(s: Style) -> Shape:
    w, st, hh = s.w(W_G), s.stem_cap, s.hair_cap
    c = cap_corners(s)
    shape = ring(s, 0, -OVS, w, CAP + OVS, st, hh, c)
    y_bar = CAP * 0.47
    shape = shape - rect(w - st - 2, y_bar, FAR, CAP + OVS - hh + 1)
    shape = cut_right(s, shape, w - c["tr"][0] * (1 - TERMINAL_ROUND), y_bar + 1, FAR, y_ref=CAP + OVS - hh / 2)
    return shape | rect(w * 0.5, y_bar - hh, w, y_bar)


@glyph("H", "H", "cap_stem", "cap_stem")
def H(s: Style) -> Shape:
    st, w = s.stem_cap, s.w(W_H)
    return rect(0, 0, st, CAP) | rect(w - st, 0, w, CAP) | bar(s, MID, 0, w)


@glyph("I", "I", "cap_stem", "cap_stem")
def I(s: Style) -> Shape:  # noqa: E743
    return rect(0, 0, s.stem_cap, CAP)


@glyph("J", "J", 22, "cap_stem")
def J(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(W_J)
    c = cap_corners(s, 0.9)
    hook = box(-200, -OVS, w, CAP, br=c["br"]) - box(-FAR, -OVS + hh, w - st, FAR, br=inner_corner(s, c["br"], st, hh))
    return cut_left(s, hook, 0, -OVS - 1, -OVS + hh + 1)


@glyph("K", "K", "cap_stem", 8)
def K(s: Style) -> Shape:
    return k_shape(s, s.stem_cap, s.w(W_K), CAP, CAP, cap_diag(s), joint=0.2, leg_start=0.32)


@glyph("L", "L", "cap_stem", 16)
def L(s: Style) -> Shape:
    return rect(0, 0, s.stem_cap, CAP) | rect(0, 0, s.w(W_L), s.hair_cap)


@glyph("M", "M", "cap_stem", "cap_stem")
def M(s: Style) -> Shape:
    st, w = s.stem_cap, s.w(W_M)
    middle = vertex((0, CAP), (w, CAP), w / 2, st * 0.8, cap_diag(s, 0.86), bottom_y=CAP * 0.22)
    return rect(0, 0, st, CAP) | rect(w - st, 0, w, CAP) | middle


@glyph("N", "N", "cap_stem", "cap_stem")
def N(s: Style) -> Shape:
    st, w = s.stem_cap, s.w(W_N)
    diag = diagonal((0, CAP), (w, 0), cap_diag(s, 0.92)) & rect(0, 0, w, CAP)
    return rect(0, 0, st, CAP) | rect(w - st, 0, w, CAP) | diag


@glyph("O", "O", "cap_round", "cap_round")
def O(s: Style) -> Shape:  # noqa: E743
    return ring(s, 0, -OVS, s.w(W_O), CAP + OVS, s.stem_cap, s.hair_cap, cap_corners(s))


def bowl_top(s: Style, w: float, bottom: float) -> Shape:
    st, hh = s.stem_cap, s.hair_cap
    c = cap_corners(s, 0.9)
    return box(0, bottom, w, CAP, tr=c["tr"], br=c["br"]) - box(
        st, bottom + hh, w - st, CAP - hh, tr=inner_corner(s, c["tr"], st, hh), br=inner_corner(s, c["br"], st, hh))


@glyph("P", "P", "cap_stem", ("cap_round", 0.9))
def P(s: Style) -> Shape:
    return rect(0, 0, s.stem_cap, CAP) | bowl_top(s, s.w(W_P), CAP * 0.39)


@glyph("Q", "Q", "cap_round", "cap_round")
def Q(s: Style) -> Shape:
    w = s.w(W_O)
    tail = band((w * 0.56, s.hair_cap + 34), (w * 0.79, -112), cap_diag(s, 0.92), -112, s.hair_cap + 34)
    return O(s) | tail


@glyph("R", "R", "cap_stem", 14)
def R(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(W_R)
    bottom = CAP * 0.42
    shape = rect(0, 0, st, CAP) | bowl_top(s, w * 0.95, bottom)
    leg = diagonal((w * 0.38, bottom + hh), (w + s.w(4), 0), cap_diag(s), 0, bottom + hh / 2)
    return shape | leg


@glyph("S", "S", ("cap_round", 0.85), ("cap_round", 0.85))
def S(s: Style) -> Shape:
    return s_shape(s, s.w(W_S), CAP + OVS, -OVS, s.stem_cap, s.hair_cap, s.radius_cap * 0.95)


@glyph("T", "T", 18, 18)
def T(s: Style) -> Shape:
    st, w = s.stem_cap, s.w(W_T)
    return rect(0, CAP - s.hair_cap, w, CAP) | rect(w / 2 - st / 2, 0, w / 2 + st / 2, CAP)


@glyph("U", "U", "cap_stem", "cap_stem")
def U(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(W_U)
    c = cap_corners(s)
    return box(0, -OVS, w, CAP, bl=c["bl"], br=c["br"]) - box(
        st, -OVS + hh, w - st, FAR, bl=inner_corner(s, c["bl"], st, hh), br=inner_corner(s, c["br"], st, hh))


@glyph("V", "V", 10, 10)
def V(s: Style) -> Shape:
    w = s.w(W_V)
    return vertex((0, CAP), (w, CAP), w / 2, s.stem_cap * 0.8, cap_diag(s))


@glyph("W", "W", 10, 10)
def W(s: Style) -> Shape:
    w, td = s.w(W_W), cap_diag(s, 0.88)
    flat = s.stem_cap * 0.6
    b1, b2, mid = w * 0.265, w * 0.735, w / 2
    return vertex((0, CAP), (mid + flat / 2, CAP), b1, flat, td) | vertex((mid - flat / 2, CAP), (w, CAP), b2, flat, td)


@glyph("X", "X", 10, 10)
def X(s: Style) -> Shape:
    w, td = s.w(W_X), cap_diag(s, 0.92)
    return (diagonal((0, CAP), (w, 0), td) | diagonal((0, 0), (w, CAP), td)) & rect(0, 0, w, CAP)


@glyph("Y", "Y", 10, 10)
def Y(s: Style) -> Shape:
    st, w = s.stem_cap, s.w(W_Y)
    y_v = CAP * 0.40
    arms = vertex((0, CAP), (w, CAP), w / 2, st, cap_diag(s), bottom_y=y_v)
    return arms | rect(w / 2 - st / 2, 0, w / 2 + st / 2, y_v + 1)


@glyph("Z", "Z", 30, 30)
def Z(s: Style) -> Shape:
    hh, w = s.hair_cap, s.w(W_Z)
    diag = diagonal((0, hh), (w, CAP - hh), cap_diag(s, 0.95), 0, CAP) & rect(0, 0, w, CAP)
    return rect(s.w(8), CAP - hh, w, CAP) | rect(0, 0, w, hh) | diag
