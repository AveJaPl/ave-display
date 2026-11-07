"""Glify techniczne i interpunkcja.

Kropki są kwadratowe (jak kropka nad i), przecinek i cudzysłowy mają ogonek pochylony
równolegle do trzonów Ave Display. Znaki wiszące (cudzysłowy górne) sięgają wysokości
wersalików, nawiasy obejmują wydłużenia dolne i górne.
"""

from __future__ import annotations

import math

from ..shapes import Shape, box, corner, corners_of, cut_left, cut_right, diagonal, inner_corner, outline, polygon, rect
from ..style import CAP, DISPLAY_SLANT, FAR, OVS, XH, Style
from .common import vertex
from .registry import glyph

QUOTE_TOP = CAP + 8
PAREN_LOW, PAREN_HIGH = -158, CAP + 98


def dot_size(s: Style) -> float:
    return s.stem * 1.1


def punct_stem(s: Style, regular: float = 80.6) -> float:
    """Grubość nawiasów i kresek pomocniczych: w Bold rośnie wolniej niż trzon liter,
    inaczej nawias zamienia się w sztabę."""
    return regular + (s.stem - 84.0) * 0.55


def square_dot(s: Style, x0: float = 0.0, y0: float = 0.0, scale: float = 1.0) -> Shape:
    d = dot_size(s) * scale
    r = corner(s, d * 0.24)
    return box(x0, y0, x0 + d, y0 + d, r, r, r, r)


def comma_shape(s: Style, x0: float = 0.0, y0: float = 0.0) -> Shape:
    """Kwadratowa kropka z ogonkiem pochylonym jak trzony Ave Display."""
    d = dot_size(s)
    tail = d * 0.95
    r = corner(s, d * 0.24)
    head = box(x0, y0, x0 + d, y0 + d, None, None, r, r)
    lean = DISPLAY_SLANT * tail * 0.9
    drop = polygon([(x0, y0 + 1), (x0 + d, y0 + 1), (x0 + d - lean, y0 - tail), (x0 + d * 0.38 - lean, y0 - tail)])
    return head | drop


def quote_shape(s: Style) -> Shape:
    """Apostrof / prawy cudzysłów: przecinek uniesiony do wysokości wersalików."""
    return comma_shape(s, 0, QUOTE_TOP - dot_size(s))


def quote_left(s: Style) -> Shape:
    q = comma_shape(s)
    x0, y0, x1, y1 = q.bounds
    return q.rotated_180((x0 + x1) / 2, (y0 + y1) / 2).moved(0, QUOTE_TOP - y1)


def pair(shape: Shape, gap: float) -> Shape:
    x0, _, x1, _ = shape.bounds
    return shape | shape.moved(x1 - x0 + gap)


def chevron(s: Style, depth: float, height: float, td: float) -> Shape:
    """Szewron skierowany w lewo (‹), czubek w x = 0, środek wysokości w y = 0."""
    v = vertex((-height / 2, depth), (height / 2, depth), 0, s.stem * 0.5, td)
    return v.affine(0, -1, 1, 0, 0, 0)


GUIL_Y = XH / 2 + 6


# --- techniczne ------------------------------------------------------------------------------

@glyph(".notdef", "", 50, 50)
def notdef(s: Style) -> Shape:
    return rect(0, 0, 500, CAP) - rect(70, 70, 430, CAP - 70)


@glyph("space", [0x20, 0xA0], advance=lambda s: s.space)
def space(s: Style) -> Shape:
    return Shape()


# --- kropki, przecinki ---------------------------------------------------------------------------

@glyph("period", ".", ("stem", 0.85), ("stem", 0.85))
def period(s: Style) -> Shape:
    return square_dot(s)


@glyph("comma", ",", ("stem", 0.85), ("stem", 0.85))
def comma(s: Style) -> Shape:
    return comma_shape(s)


@glyph("colon", ":", ("stem", 0.85), ("stem", 0.85))
def colon(s: Style) -> Shape:
    return square_dot(s) | square_dot(s, 0, XH - dot_size(s))


@glyph("semicolon", ";", ("stem", 0.85), ("stem", 0.85))
def semicolon(s: Style) -> Shape:
    return comma_shape(s) | square_dot(s, 0, XH - dot_size(s))


@glyph("ellipsis", "…", ("stem", 0.85), ("stem", 0.85))
def ellipsis(s: Style) -> Shape:
    d = dot_size(s)
    step = d + s.w(d * 0.95)
    return square_dot(s) | square_dot(s, step) | square_dot(s, 2 * step)


@glyph("periodcentered", "·", ("stem", 0.85), ("stem", 0.85))
def periodcentered(s: Style) -> Shape:
    return square_dot(s, 0, XH / 2 + 30 - dot_size(s) / 2)


@glyph("bullet", "•", 50, 50)
def bullet(s: Style) -> Shape:
    d = dot_size(s) * 1.55
    return square_dot(s, 0, XH / 2 + 30 - d / 2, scale=1.55)


@glyph("exclam", "!", ("cap_stem", 0.9), ("cap_stem", 0.9))
def exclam(s: Style) -> Shape:
    d = dot_size(s)
    x = (d - s.stem_cap) / 2
    return square_dot(s) | rect(x, d * 1.9, x + s.stem_cap, CAP)


@glyph("exclamdown", "¡", ("cap_stem", 0.9), ("cap_stem", 0.9))
def exclamdown(s: Style) -> Shape:
    x0, _, x1, _ = exclam(s).bounds
    return exclam(s).rotated_180((x0 + x1) / 2, CAP / 2).moved(0, XH - CAP)


@glyph("question", "?", 40, ("cap_stem", 0.8))
def question(s: Style) -> Shape:
    st, hh = s.stem_cap, s.hair_cap
    w = s.w(388)
    top = CAP + OVS
    d = dot_size(s)
    xs = w * 0.36
    neck = CAP * 0.40
    cs = corners_of(s, s.radius_cap * 0.85)
    shape = outline([
        (-200, top), (w, top, cs["tr"]), (w, neck, cs["br"]),
        (xs + st, neck), (xs + st, d * 1.9), (xs, d * 1.9),
        (xs, neck + hh, corner(s, 10)),
        (w - st, neck + hh, inner_corner(s, cs["br"], st, hh)),
        (w - st, top - hh, inner_corner(s, cs["tr"], st, hh)),
        (-200, top - hh),
    ])
    shape = cut_left(s, shape, s.w(8), top - hh - 1, top + 1)
    return shape | square_dot(s, xs + st / 2 - d / 2)


@glyph("questiondown", "¿", ("cap_stem", 0.8), 40)
def questiondown(s: Style) -> Shape:
    x0, _, x1, _ = question(s).bounds
    return question(s).rotated_180((x0 + x1) / 2, CAP / 2).moved(0, XH - CAP)


# --- kreski ----------------------------------------------------------------------------------------

def dash_y(s: Style) -> tuple[float, float]:
    mid = XH / 2 + 14
    return mid - s.bar / 2, mid + s.bar / 2


@glyph("hyphen", [0x2D, 0xAD], 44, 44)
def hyphen(s: Style) -> Shape:
    y0, y1 = dash_y(s)
    return rect(0, y0, s.w(206), y1)


@glyph("endash", "–", 30, 30)
def endash(s: Style) -> Shape:
    y0, y1 = dash_y(s)
    return rect(0, y0, s.w(440), y1)


@glyph("emdash", "—", 30, 30)
def emdash(s: Style) -> Shape:
    y0, y1 = dash_y(s)
    return rect(0, y0, s.w(880), y1)


@glyph("underscore", "_", 0, 0)
def underscore(s: Style) -> Shape:
    return rect(0, -150, s.w(520), -150 + s.hair)


@glyph("slash", "/", 16, 16)
def slash(s: Style) -> Shape:
    return diagonal((0, -120), (s.w(300), CAP + 30), s.stem * 0.86, -120, CAP + 30)


@glyph("backslash", "\\", 16, 16)
def backslash(s: Style) -> Shape:
    return slash(s).mirrored_x(s.w(300) / 2)


@glyph("bar", "|", 70, 70)
def bar(s: Style) -> Shape:
    return rect(0, PAREN_LOW - 30, s.stem * 0.9, PAREN_HIGH + 30)


@glyph("brokenbar", "¦", 70, 70)
def brokenbar(s: Style) -> Shape:
    t = s.stem * 0.9
    return rect(0, PAREN_LOW - 30, t, 220) | rect(0, 360, t, PAREN_HIGH + 30)


# --- nawiasy -----------------------------------------------------------------------------------------

def arc_left(s: Style, low: float, high: float, width: float) -> Shape:
    """Łuk otwarty w prawo: pionowy środek, końce wygięte w prawo i zwężone (nawiasy, klamry).
    Duży promień narożnika sprawia, że kształt czyta się jako łuk, a nie jako nawias kwadratowy."""
    st, hh = punct_stem(s), s.hair * 0.82
    width = width + (s.stem - 84.0) * 0.6
    ry = (high - low) * 0.26
    outer_c = corner(s, width, ry, 0.6)
    inner_c = corner(s, width - st * 0.4, ry - hh, 0.6)
    outer = box(0, low, width, high, bl=outer_c, tl=outer_c)
    inner = box(st, low + hh, width + st, high - hh, bl=inner_c, tl=inner_c)
    return outer - inner


def paren_left_shape(s: Style) -> Shape:
    return arc_left(s, PAREN_LOW, PAREN_HIGH, s.w(168))


@glyph("parenleft", "(", ("stem", 0.9), 24)
def parenleft(s: Style) -> Shape:
    return paren_left_shape(s)


@glyph("parenright", ")", 24, ("stem", 0.9))
def parenright(s: Style) -> Shape:
    shape = paren_left_shape(s)
    x0, _, x1, _ = shape.bounds
    return shape.mirrored_x((x0 + x1) / 2)


def bracket_left_shape(s: Style) -> Shape:
    st, hh, w = punct_stem(s), s.hair * 0.9, s.w(186)
    return rect(0, PAREN_LOW, st, PAREN_HIGH) | rect(0, PAREN_LOW, w, PAREN_LOW + hh) | rect(0, PAREN_HIGH - hh, w, PAREN_HIGH)


@glyph("bracketleft", "[", ("stem", 0.95), 24)
def bracketleft(s: Style) -> Shape:
    return bracket_left_shape(s)


@glyph("bracketright", "]", 24, ("stem", 0.95))
def bracketright(s: Style) -> Shape:
    return bracket_left_shape(s).mirrored_x(s.w(186) / 2)


def brace_left_shape(s: Style) -> Shape:
    st, hh = punct_stem(s, 77.0), s.hair * 0.9
    xv = s.w(64)
    mid = (PAREN_LOW + PAREN_HIGH) / 2
    w = s.w(150)
    upper = arc_left(s, mid - hh / 2, PAREN_HIGH, w) - rect(-FAR, -FAR, FAR, mid)
    lower = arc_left(s, PAREN_LOW, mid + hh / 2, w) - rect(-FAR, mid, FAR, FAR)
    body = (upper | lower | rect(0, mid - 40, st, mid + 40)).moved(xv)
    nub = rect(0, mid - hh / 2, xv + st, mid + hh / 2)
    return body | nub


@glyph("braceleft", "{", 30, 24)
def braceleft(s: Style) -> Shape:
    return brace_left_shape(s)


@glyph("braceright", "}", 24, 30)
def braceright(s: Style) -> Shape:
    shape = brace_left_shape(s)
    x0, _, x1, _ = shape.bounds
    return shape.mirrored_x((x0 + x1) / 2)


# --- cudzysłowy ---------------------------------------------------------------------------------------

QUOTE_GAP = 0.55


@glyph("quotesingle", "'", ("stem", 0.9), ("stem", 0.9))
def quotesingle(s: Style) -> Shape:
    return rect(0, QUOTE_TOP - 236, s.stem * 0.96, QUOTE_TOP)


@glyph("quotedbl", '"', ("stem", 0.9), ("stem", 0.9))
def quotedbl(s: Style) -> Shape:
    return pair(quotesingle(s), s.stem * 0.85)


@glyph("quoteright", "’", ("stem", 0.8), ("stem", 0.8))
def quoteright(s: Style) -> Shape:
    return quote_shape(s)


@glyph("quoteleft", "‘", ("stem", 0.8), ("stem", 0.8))
def quoteleft(s: Style) -> Shape:
    return quote_left(s)


@glyph("quotesinglbase", "‚", ("stem", 0.8), ("stem", 0.8))
def quotesinglbase(s: Style) -> Shape:
    return comma_shape(s)


@glyph("quotedblright", "”", ("stem", 0.8), ("stem", 0.8))
def quotedblright(s: Style) -> Shape:
    return pair(quote_shape(s), dot_size(s) * QUOTE_GAP)


@glyph("quotedblleft", "“", ("stem", 0.8), ("stem", 0.8))
def quotedblleft(s: Style) -> Shape:
    return pair(quote_left(s), dot_size(s) * QUOTE_GAP)


@glyph("quotedblbase", "„", ("stem", 0.8), ("stem", 0.8))
def quotedblbase(s: Style) -> Shape:
    return pair(comma_shape(s), dot_size(s) * QUOTE_GAP)


@glyph("guilsinglleft", "‹", 34, 34)
def guilsinglleft(s: Style) -> Shape:
    return chevron(s, s.w(196), 286, s.stem * 0.86).moved(0, GUIL_Y)


@glyph("guilsinglright", "›", 34, 34)
def guilsinglright(s: Style) -> Shape:
    return guilsinglleft(s).mirrored_x(s.w(196) / 2)


@glyph("guillemotleft", "«", 34, 34)
def guillemotleft(s: Style) -> Shape:
    one = guilsinglleft(s)
    return one | one.moved(s.w(196) * 0.78)


@glyph("guillemotright", "»", 34, 34)
def guillemotright(s: Style) -> Shape:
    one = guilsinglright(s)
    return one | one.moved(s.w(196) * 0.78)


# --- znaki z tekstu: * # † ‡ @ & § ¶ ------------------------------------------------------------------

@glyph("asterisk", "*", 34, 34)
def asterisk(s: Style) -> Shape:
    t, half = s.stem * 0.84, 150.0
    arm = rect(-t / 2, -half, t / 2, half)
    out = arm
    for angle in (60, 120):
        a = math.radians(angle)
        out = out | arm.affine(math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
    return out.moved(half, CAP - half * 1.02)


@glyph("numbersign", "#", 30, 30)
def numbersign(s: Style) -> Shape:
    w, t, hh = s.w(540), s.stem * 0.86, s.hair
    lean = math.tan(math.radians(10)) * CAP
    v = polygon([(0, 0), (t, 0), (t + lean, CAP - 30), (lean, CAP - 30)])
    gap = w * 0.38
    x_shift = (w - gap - t - lean) / 2
    verticals = v.moved(x_shift) | v.moved(x_shift + gap)
    bars = rect(0, 196, w, 196 + hh) | rect(0, 452, w, 452 + hh)
    return verticals | bars


@glyph("dagger", "†", 40, 40)
def dagger(s: Style) -> Shape:
    w, st = s.w(360), s.stem * 0.9
    return rect(w / 2 - st / 2, -110, w / 2 + st / 2, CAP + 20) | rect(0, CAP - 210, w, CAP - 210 + s.hair)


@glyph("daggerdbl", "‡", 40, 40)
def daggerdbl(s: Style) -> Shape:
    return dagger(s) | rect(0, 80, s.w(360), 80 + s.hair)


@glyph("at", "@", 44, 44)
def at(s: Style) -> Shape:
    st, hh = s.stem * 0.92, s.hair * 0.94
    w = s.w(800)
    low, high = -120.0, CAP + 10
    c = corners_of(s, s.radius * 1.2)
    outer = box(0, low, w, high, c["bl"], c["br"], c["tr"], c["tl"]) - box(
        st, low + hh, w - st, high - hh, *(inner_corner(s, c[k], st, hh) for k in ("bl", "br", "tr", "tl")))
    foot_y = 112.0
    outer = outer - rect(w * 0.70, -FAR, FAR, foot_y)
    outer = cut_right(s, outer, w * 0.70, -FAR, foot_y, y_ref=low + hh / 2)
    x0, x1 = w * 0.27, w * 0.68
    ci = corners_of(s, s.radius * 0.8)
    bowl = box(x0, foot_y, x1, 512, bl=ci["bl"], tl=ci["tl"], tr=ci["tr"]) - box(
        x0 + st, foot_y + hh, x1 - st, 512 - hh,
        bl=inner_corner(s, ci["bl"], st, hh), tl=inner_corner(s, ci["tl"], st, hh), tr=inner_corner(s, ci["tr"], st, hh))
    foot = rect(x1 - st, foot_y, w, foot_y + hh)
    return outer | bowl | foot


@glyph("ampersand", "&", 36, 20)
def ampersand(s: Style) -> Shape:
    st, hh = s.stem_cap * 0.96, s.hair_cap
    w = s.w(600)
    ym = CAP * 0.54
    c = corners_of(s, s.radius_cap * 0.8)
    loop_x0, loop_x1 = w * 0.06, w * 0.62
    loop = box(loop_x0, ym, loop_x1, CAP + OVS, c["bl"], c["br"], c["tr"], c["tl"]) - box(
        loop_x0 + st, ym + hh, loop_x1 - st, CAP + OVS - hh,
        *(inner_corner(s, c[k], st, hh) for k in ("bl", "br", "tr", "tl")))
    lower = box(0, -OVS, w * 0.86, ym + hh, bl=c["bl"], tl=c["tl"], br=c["br"]) - box(
        st, -OVS + hh, FAR, ym, bl=inner_corner(s, c["bl"], st, hh), tl=inner_corner(s, c["tl"], st, hh))
    lower = lower - rect(loop_x1 - 1, -OVS + hh, FAR, ym + hh + 1)
    lower = cut_right(s, lower, w * 0.66, -FAR, ym / 2, y_ref=-OVS + hh / 2)
    leg = diagonal((loop_x0 + st * 0.6, ym + hh * 0.4), (w + s.w(8), 0), s.stem_cap * 0.92, 0, ym + hh * 0.4)
    arm = rect(w * 0.64, CAP * 0.36 - hh / 2, w * 0.98, CAP * 0.36 + hh / 2)
    return loop | lower | leg | arm


@glyph("section", "§", 40, 40)
def section(s: Style) -> Shape:
    from .common import s_shape

    w = s.w(372)
    h = CAP * 0.64
    one = s_shape(s, w, h, 0, s.stem * 0.96, s.hair, s.radius * 0.8)
    return one.moved(0, CAP - h + OVS) | one.moved(0, -OVS - 60)


@glyph("paragraph", "¶", 36, 36)
def paragraph(s: Style) -> Shape:
    st, hh, w = s.stem * 0.92, s.hair, s.w(470)
    x1 = w * 0.62
    c = corners_of(s, s.radius * 0.9)
    fill = box(0, CAP * 0.36, x1, CAP, bl=c["bl"], tl=c["tl"])
    return fill | rect(x1 - st, -120, x1, CAP) | rect(w - st, -120, w, CAP) | rect(x1 - st, CAP - hh, w, CAP)
