"""Interpunkcja i znaki: . , : ; - – / ! ? % + & ' " ( ) # @ * · × °"""

import math

from ..geometry import Shape, polygon, rect, rounded, stroke, union, width_for
from ..params import BAR, BOWL, CAP, MID_HI, MID_LO, RA, RB, SHEAR_ORIGIN_Y, SLANT, STEM, rA, rB
from ..spacing import SB
from .registry import glyph

DOT = 210
PUNCT_SLASH = 0.62


def scaled(corner, factor):
    rx, ry, k = corner
    return (rx * factor, ry * factor, k)


def italic_native(shape: Shape) -> Shape:
    """Znak projektowany wprost w układzie pochylonym (po pochyleniu wraca do zamierzonego kształtu)."""
    return shape.sheared(-SLANT, SHEAR_ORIGIN_Y)


def rotated(shape: Shape, angle_deg: float, cx: float, cy: float) -> Shape:
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    return shape.affine(c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy)


def small_ring(x0: float, y0: float, w: float, h: float, side: float, bar: float) -> Shape:
    f = h / CAP * 1.4
    outer = rounded([(x0, y0, scaled(RA, f)), (x0 + w, y0, scaled(RB, f)),
                     (x0 + w, y0 + h, scaled(RA, f)), (x0, y0 + h, scaled(RB, f))])
    return outer - rect(x0 + side, y0 + bar, x0 + w - side, y0 + h - bar)


def period_shape(y0: float = 0) -> Shape:
    return rect(0, y0, DOT, y0 + BAR)


def comma_shape() -> Shape:
    return polygon([(0, -150), (78, -150), (DOT, 28), (DOT, BAR), (0, BAR)])


@glyph("period", ".", SB.PUNCT, SB.PUNCT)
def period() -> Shape:
    return period_shape()


@glyph("comma", ",", SB.PUNCT, SB.PUNCT)
def comma() -> Shape:
    return comma_shape()


COLON_HIGH = CAP - BAR - BAR


@glyph("colon", ":", SB.PUNCT, SB.PUNCT)
def colon() -> Shape:
    return period_shape() | period_shape(COLON_HIGH)


@glyph("semicolon", ";", SB.PUNCT, SB.PUNCT)
def semicolon() -> Shape:
    return comma_shape() | period_shape(COLON_HIGH)


@glyph("hyphen", "-", SB.BAR, SB.BAR)
def hyphen() -> Shape:
    return rect(0, MID_LO, 420, MID_HI)


@glyph("endash", "–", SB.BAR, SB.BAR)
def endash() -> Shape:
    return rect(0, MID_LO, 640, MID_HI)


@glyph("slash", "/", SB.DIAG, SB.DIAG)
def slash() -> Shape:
    return stroke((0, 0), PUNCT_SLASH, 180, -40, CAP + 40)


@glyph("exclam", "!", SB.PUNCT, SB.PUNCT)
def exclam() -> Shape:
    return rect(0, BAR + 96, DOT, CAP) | period_shape()


QUESTION_WIDTH, QUESTION_STEM_X = 720, 240


@glyph("question", "?", SB.BAR, SB.ROUND)
def question() -> Shape:
    w, x = QUESTION_WIDTH, QUESTION_STEM_X
    hook = rounded([
        (0, CAP), (w, CAP, RA), (w, MID_LO, RB), (x + DOT, MID_LO), (x + DOT, BAR + 96),
        (x, BAR + 96), (x, MID_HI), (w - BOWL, MID_HI, rB), (w - BOWL, CAP - BAR, rA), (0, CAP - BAR),
    ])
    return hook | rect(x, 0, x + DOT, BAR)


PERCENT_WIDTH = 900


@glyph("percent", "%", SB.ROUND, SB.ROUND)
def percent() -> Shape:
    w = PERCENT_WIDTH
    size, side, bar = 290, 100, 92
    slash_shape = stroke((175, 0), PUNCT_SLASH, 170, 0, CAP)
    return small_ring(0, CAP - size, size, size, side, bar) | small_ring(w - size, 0, size, size, side, bar) | slash_shape


PLUS_WIDTH, PLUS_ARM = 540, 170


@glyph("plus", "+", SB.PUNCT, SB.PUNCT)
def plus() -> Shape:
    cx, cy = PLUS_WIDTH / 2, (MID_LO + MID_HI) / 2
    half = PLUS_WIDTH / 2
    return rect(0, MID_LO, PLUS_WIDTH, MID_HI) | rect(cx - PLUS_ARM / 2, cy - half, cx + PLUS_ARM / 2, cy + half)


AMP_LOOP_X0, AMP_LOOP_X1, AMP_COUNTER_W, AMP_LEG_SLOPE, AMP_ARM_X0, AMP_ARM_X1 = 60, 560, 130, -1.3, 700, 930


@glyph("ampersand", "&", SB.ROUND, SB.LEG)
def ampersand() -> Shape:
    x0, x1 = AMP_LOOP_X0, AMP_LOOP_X1
    loop = rounded([(x0, MID_LO), (x1, MID_LO), (x1, CAP, RA), (x0, CAP, RB)])
    cx = (x0 + STEM + x1 - BOWL) / 2
    a, b = scaled(rA, 0.6), scaled(rB, 0.6)
    loop -= rounded([
        (cx - AMP_COUNTER_W / 2, MID_HI, a), (cx + AMP_COUNTER_W / 2, MID_HI, b),
        (cx + AMP_COUNTER_W / 2, CAP - BAR, a), (cx - AMP_COUNTER_W / 2, CAP - BAR, b),
    ])
    leg = stroke((x1, MID_HI), AMP_LEG_SLOPE, 197, 0, MID_HI, edge="right")
    foot = leg.bounds[2] - width_for(197, AMP_LEG_SLOPE)
    lower = rounded([(0, 0, RA), (foot, 0), (foot, BAR), (STEM, BAR, rA), (STEM, MID_HI), (0, MID_HI, RB)])
    arm = rect(AMP_ARM_X0, MID_LO, AMP_ARM_X1, MID_HI)
    return loop | lower | leg | arm


QUOTE_WIDTH, QUOTE_LOW = 150, CAP - 250


@glyph("quotesingle", "'", SB.PUNCT, SB.PUNCT)
def quotesingle() -> Shape:
    return rect(0, QUOTE_LOW, QUOTE_WIDTH, CAP)


@glyph("quotedbl", '"', SB.PUNCT, SB.PUNCT)
def quotedbl() -> Shape:
    return rect(0, QUOTE_LOW, QUOTE_WIDTH, CAP) | rect(QUOTE_WIDTH + 100, QUOTE_LOW, 2 * QUOTE_WIDTH + 100, CAP)


PAREN_WIDTH, PAREN_SIDE, PAREN_BAR, PAREN_LO, PAREN_HI = 310, 170, 120, -130, CAP + 130
PAREN_ROUND, PAREN_INNER = 1.15, 1.8


def paren_left_shape() -> Shape:
    w, s, b = PAREN_WIDTH, PAREN_SIDE, PAREN_BAR
    lo, hi = PAREN_LO, PAREN_HI
    return rounded([
        (0, lo, scaled(RA, PAREN_ROUND)), (w, lo), (w, lo + b), (s, lo + b, scaled(rA, PAREN_INNER)),
        (s, hi - b, scaled(rB, PAREN_INNER)), (w, hi - b), (w, hi), (0, hi, scaled(RB, PAREN_ROUND)),
    ])


@glyph("parenleft", "(", SB.ROUND, SB.BAR)
def parenleft() -> Shape:
    return paren_left_shape()


@glyph("parenright", ")", SB.BAR, SB.ROUND)
def parenright() -> Shape:
    return paren_left_shape().rotated_180(PAREN_WIDTH / 2, (PAREN_LO + PAREN_HI) / 2)


@glyph("numbersign", "#", SB.DIAG, SB.DIAG)
def numbersign() -> Shape:
    w, v, h = 760, 150, 130
    return union(
        rect(150, 0, 150 + v, CAP), rect(w - 150 - v, 0, w - 150, CAP),
        rect(0, 170, w, 170 + h), rect(0, CAP - 170 - h, w, CAP - 170),
    )


AT_WIDTH = 960


@glyph("at", "@", SB.ROUND, SB.ROUND)
def at() -> Shape:
    w, lo, hi = AT_WIDTH, -150, CAP + 20
    side, bar = 170, 140
    frame = rounded([(0, lo, RA), (w, lo, RB), (w, hi, RA), (0, hi, RB)])
    frame -= rounded([(side, lo + bar, rA), (w - side, lo + bar, rB), (w - side, hi - bar, rA), (side, hi - bar, rB)])
    frame -= rect(w - side - 10, lo - 10, w + 10, 130)
    inner = rounded([(300, 110, rA), (w - side, 110), (w - side, 520, rA), (300, 520, rB)])
    inner -= rect(300 + 150, 110 + 125, w - side - 150, 520 - 125)
    return frame | inner | rect(w - side - 150, lo + bar - 1, w - side, 130)


@glyph("asterisk", "*", SB.PUNCT, SB.PUNCT)
def asterisk() -> Shape:
    cx, cy, length, thick = 230, CAP - 220, 440, 120
    arm = rect(cx - thick / 2, cy - length / 2, cx + thick / 2, cy + length / 2)
    return union(*(rotated(arm, a, cx, cy) for a in (0, 60, 120)))


@glyph("periodcentered", "·", SB.PUNCT, SB.PUNCT)
def periodcentered() -> Shape:
    return period_shape((MID_LO + MID_HI) / 2 - BAR / 2)


@glyph("multiply", "×", SB.PUNCT, SB.PUNCT)
def multiply() -> Shape:
    cx, cy, length, thick = 240, (MID_LO + MID_HI) / 2, 560, 140
    arm = rect(cx - thick / 2, cy - length / 2, cx + thick / 2, cy + length / 2)
    cross = rotated(arm, 45, cx, cy) | rotated(arm, -45, cx, cy)
    return italic_native(cross)


@glyph("degree", "°", SB.PUNCT, SB.PUNCT)
def degree() -> Shape:
    return small_ring(0, CAP - 300, 300, 300, 104, 96)
