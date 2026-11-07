"""Litery specjalne alfabetów zachodnio- i środkowoeuropejskich: Æ æ Œ œ Ø ø Þ þ ß ð µ ƒ ª º.

Ligatury (æ, œ, Æ, Œ) składamy z gotowych liter: druga litera zaczyna się na trzonie lub boku
pierwszej, więc styk ma te same przewężenia co reszta kroju.
"""

from __future__ import annotations

from ..shapes import Shape, band, box, corner, corners_of, cut_left, cut_right, diagonal, inner_corner, polygon, rect, ring
from ..style import ASC, CAP, DESC, FAR, OVS, XH, Style
from . import lower, upper
from .registry import glyph

SUPERIOR_SCALE = 0.62


def superior(s: Style, build, scale: float = SUPERIOR_SCALE, top: float = CAP, boost: float = 1.32) -> Shape:
    """Pomniejszona kopia glifu z grubszymi kreskami (żeby po skalowaniu nie był za chudy),
    wyrównana górą do `top`. W pogrubionych odmianach wzmocnienie jest mniejsze, bo kreski
    są już grube, a w małym rozmiarze światła zarosłyby."""
    if s.weight >= 600:
        boost = 1.0 + (boost - 1.0) * 0.4
    heavy = s.variant(stem=s.stem * boost, hair=s.hair * boost, bar=s.bar * boost,
                      stem_cap=s.stem_cap * boost, hair_cap=s.hair_cap * boost, width=s.width * 1.06)
    shape = build(heavy).affine(scale, 0, 0, scale, 0, 0)
    _, _, _, y1 = shape.bounds
    return shape.moved(0, top - y1)


@glyph("AE", "Æ", 12, 40)
def AE(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(840)
    xs = w * 0.40
    leg = band((0, 0), (xs, CAP), upper.cap_diag(s), 0, CAP, anchor="left")
    hull = polygon([(0, 0), (xs, CAP), (w, CAP), (w, 0)])
    e_mid = xs + (w - xs) * 0.9
    bars = rect(xs, CAP - hh, w, CAP) | rect(xs, 0, w, hh) | (upper.bar(s, upper.MID, 0, e_mid) & hull)
    return leg | rect(xs, 0, xs + st, CAP) | bars


@glyph("ae", "æ", ("round", 0.9), ("round", 0.86))
def ae(s: Style) -> Shape:
    a = lower.a_double(s)
    shift = s.w(lower.W_A) - s.stem
    return a | lower.e(s).moved(shift)


@glyph("oe", "œ", "round", ("round", 0.86))
def oe(s: Style) -> Shape:
    shift = s.w(lower.W_O) - s.stem
    return lower.o(s) | lower.e(s).moved(shift)


@glyph("OE", "Œ", "cap_round", 40)
def OE(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(880)
    xe = w * 0.5
    c = upper.cap_corners(s)
    body = box(0, 0, xe + st, CAP, bl=c["bl"], tl=c["tl"]) - box(
        st, hh, xe, CAP - hh, bl=inner_corner(s, c["bl"], st, hh), tl=inner_corner(s, c["tl"], st, hh))
    bars = rect(xe, CAP - hh, w, CAP) | rect(xe, 0, w, hh) | upper.bar(s, upper.MID, xe, xe + (w - xe) * 0.9)
    return body | bars


def _slashed(base: Shape, height: float, thickness: float) -> Shape:
    x0, _, x1, _ = base.bounds
    over = 26
    slash = diagonal((x0 - over, -over - OVS), (x1 + over, height + over), thickness, -over - OVS, height + over)
    return base | slash


@glyph("Oslash", "Ø", spacing_from="O")
def Oslash(s: Style) -> Shape:
    return _slashed(upper.O(s), CAP + OVS, s.hair_cap * 1.08)


@glyph("oslash", "ø", spacing_from="o")
def oslash(s: Style) -> Shape:
    return _slashed(lower.o(s), XH + OVS, s.hair * 1.08)


@glyph("Thorn", "Þ", "cap_stem", ("cap_round", 0.9))
def Thorn(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(upper.W_P)
    c = upper.cap_corners(s, 0.9)
    y0, y1 = CAP * 0.17, CAP * 0.83
    bowl = box(0, y0, w, y1, tr=c["tr"], br=c["br"]) - box(
        st, y0 + hh, w - st, y1 - hh, tr=inner_corner(s, c["tr"], st, hh), br=inner_corner(s, c["br"], st, hh))
    return rect(0, 0, st, CAP) | bowl


@glyph("thorn", "þ", "stem", "round")
def thorn(s: Style) -> Shape:
    return rect(0, DESC, s.stem, ASC) | lower.bowl(s, 0, s.w(lower.W_BOWL), "left")


@glyph("germandbls", "ß", "stem", ("round", 0.9))
def germandbls(s: Style) -> Shape:
    st, hh, w = s.stem, s.hair, s.w(476)
    top = ASC + OVS / 2
    up_w = w * 0.86
    ym = 404.0
    c = corners_of(s, s.radius)
    waist = corners_of(s, s.radius * 0.62)
    upper_part = box(0, ym - hh / 2, up_w, top, tl=c["tl"], tr=c["tr"], br=waist["br"]) - box(
        st, ym + hh / 2, up_w - st, top - hh,
        tl=inner_corner(s, c["tl"], st, hh), tr=inner_corner(s, c["tr"], st, hh), br=inner_corner(s, waist["br"], st, hh))
    lower_part = box(-200, -OVS, w, ym + hh / 2, tr=waist["tr"], br=c["br"]) - box(
        -FAR, -OVS + hh, w - st, ym - hh / 2, tr=inner_corner(s, waist["tr"], st, hh), br=inner_corner(s, c["br"], st, hh))
    lower_part = lower_part - rect(-FAR, ym - hh / 2 - 1, st + 1, ym + hh / 2 + 1)
    lower_part = cut_left(s, lower_part, st + s.w(60), -OVS - 1, -OVS + hh + 1)
    return upper_part | lower_part | rect(0, 0, st, ym)


@glyph("eth", "ð", "round", "round")
def eth(s: Style) -> Shape:
    st, hh, w = s.stem, s.hair, s.w(lower.W_O)
    top = 690.0
    c = corners_of(s, s.radius)
    hook = box(w * 0.36, XH, w, top, tr=c["tr"]) - box(-FAR, -FAR, w - st, top - hh, tr=inner_corner(s, c["tr"], st, hh))
    hook = cut_left(s, hook, w * 0.40, top - hh - 1, top + 1)
    cross = rect(w - st - s.w(78), 600 - s.bar / 2, w + s.w(36), 600 + s.bar / 2)
    return lower.o(s) | rect(w - st, XH / 2, w, top - c["tr"][1]) | hook | cross


@glyph("mu", [0xB5], "stem", "stem")
def mu(s: Style) -> Shape:
    return lower.u(s) | rect(0, DESC, s.stem, XH)


@glyph("florin", "ƒ", 20, 10)
def florin(s: Style) -> Shape:
    st, hh = s.stem, s.hair
    x = s.w(120)
    top, bottom = ASC + OVS / 2, DESC - OVS / 2
    tl = corner(s, s.radius * 0.9)
    br = corner(s, s.radius * 0.9)
    body = box(x, 0, x + st + 400, top, tl=tl) - box(x + st, -FAR, FAR, top - hh, tl=inner_corner(s, tl, st, hh))
    body = cut_right(s, body, x + st + s.w(lower.F_ARM), top - hh - 1, top + 1)
    hook = box(x - 300, bottom, x + st, XH, br=br) - box(-FAR, bottom + hh, x, FAR, br=inner_corner(s, br, st, hh))
    hook = cut_left(s, hook, x - s.w(110), bottom - 1, bottom + hh + 1)
    return body | hook | rect(x - s.w(70), XH - s.bar, x + st + s.w(96), XH)


@glyph("ordfeminine", "ª", 40, 40)
def ordfeminine(s: Style) -> Shape:
    return superior(s, lower.a_double)


@glyph("ordmasculine", "º", 40, 40)
def ordmasculine(s: Style) -> Shape:
    return superior(s, lower.o)


__all__ = ["superior", "ring", "SUPERIOR_SCALE"]
