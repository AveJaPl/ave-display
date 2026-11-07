"""Symbole: matematyczne, waluty, znaki prawne, procenty, indeksy górne, ułamki, cyfry tabelaryczne.

Znaki matematyczne mają wspólną szerokość i oś (MATH_Y), więc w kolumnach liczb + − = × ÷
stoją równo. Cyfry tabelaryczne (zero.tf … nine.tf) mają stałą szerokość i są włączane cechą tnum.
"""

from __future__ import annotations

import math

from ..shapes import Shape, box, corners_of, cut_right, diagonal, inner_corner, rect, ring
from ..style import CAP, FAR, OVS, XH, Style
from . import digits, lower, upper
from .common import apex
from .latin import superior
from .marks import tilde
from .punct import chevron, dot_size, square_dot
from .registry import glyph

MATH_Y = 330.0
MATH_W = 440.0
MATH_SIDE = 60
TABULAR_W = 578.0


def math_t(s: Style) -> float:
    return (s.stem + s.hair) / 2


def hbar(s: Style, y: float, x0: float = 0.0, x1: float | None = None) -> Shape:
    t = math_t(s)
    x1 = s.w(MATH_W) if x1 is None else x1
    return rect(x0, y - t / 2, x1, y + t / 2)


def rotated(shape: Shape, degrees: float, cx: float, cy: float) -> Shape:
    a = math.radians(degrees)
    c, s_ = math.cos(a), math.sin(a)
    return shape.affine(c, s_, -s_, c, cx - c * cx + s_ * cy, cy - s_ * cx - c * cy)


# --- matematyczne -----------------------------------------------------------------------------

@glyph("plus", "+", MATH_SIDE, MATH_SIDE)
def plus(s: Style) -> Shape:
    w, t = s.w(MATH_W), math_t(s)
    return hbar(s, MATH_Y) | rect(w / 2 - t / 2, MATH_Y - w / 2, w / 2 + t / 2, MATH_Y + w / 2)


@glyph("minus", [0x2212], MATH_SIDE, MATH_SIDE)
def minus(s: Style) -> Shape:
    return hbar(s, MATH_Y)


@glyph("equal", "=", MATH_SIDE, MATH_SIDE)
def equal(s: Style) -> Shape:
    gap = 104 + math_t(s)
    return hbar(s, MATH_Y - gap / 2) | hbar(s, MATH_Y + gap / 2)


@glyph("less", "<", MATH_SIDE, MATH_SIDE)
def less(s: Style) -> Shape:
    return chevron(s, s.w(MATH_W) * 0.86, 440, s.stem * 0.86).moved(0, MATH_Y)


@glyph("greater", ">", MATH_SIDE, MATH_SIDE)
def greater(s: Style) -> Shape:
    return less(s).mirrored_x(s.w(MATH_W) * 0.43)


@glyph("plusminus", "±", MATH_SIDE, MATH_SIDE)
def plusminus(s: Style) -> Shape:
    w, t = s.w(MATH_W), math_t(s)
    y = MATH_Y + 64
    arm = w * 0.42
    cross = hbar(s, y) | rect(w / 2 - t / 2, y - arm, w / 2 + t / 2, y + arm)
    return cross | hbar(s, y - arm - 66 - t / 2)


@glyph("multiply", "×", MATH_SIDE, MATH_SIDE)
def multiply(s: Style) -> Shape:
    w, t = s.w(MATH_W), math_t(s)
    arm = w * 0.5
    bar = rect(w / 2 - arm, MATH_Y - t / 2, w / 2 + arm, MATH_Y + t / 2)
    return (rotated(bar, 45, w / 2, MATH_Y) | rotated(bar, -45, w / 2, MATH_Y)) & rect(
        w * 0.12, MATH_Y - w * 0.38, w * 0.88, MATH_Y + w * 0.38)


@glyph("divide", "÷", MATH_SIDE, MATH_SIDE)
def divide(s: Style) -> Shape:
    w = s.w(MATH_W)
    d = dot_size(s)
    gap = 70 + math_t(s) / 2
    return hbar(s, MATH_Y) | square_dot(s, w / 2 - d / 2, MATH_Y + gap) | square_dot(s, w / 2 - d / 2, MATH_Y - gap - d)


@glyph("logicalnot", "¬", MATH_SIDE, MATH_SIDE)
def logicalnot(s: Style) -> Shape:
    w, t = s.w(MATH_W), math_t(s)
    return hbar(s, MATH_Y + 40) | rect(w - t, MATH_Y - 130, w, MATH_Y + 40)


@glyph("asciitilde", "~", MATH_SIDE, MATH_SIDE)
def asciitilde(s: Style) -> Shape:
    t = tilde(s, False).affine(1.7, 0, 0, 1.25, 0, 0)
    x0, y0, x1, y1 = t.bounds
    return t.moved(-x0, MATH_Y - (y0 + y1) / 2)


@glyph("asciicircum", "^", 40, 40)
def asciicircum(s: Style) -> Shape:
    w = s.w(MATH_W) * 0.92
    return apex((0, CAP * 0.46), (w, CAP * 0.46), w / 2, s.stem * 0.7, s.stem * 0.86, CAP)


# --- procenty --------------------------------------------------------------------------------

def small_ring(s: Style, x0: float, y0: float, w: float = 208.0, h: float = 296.0) -> Shape:
    st, hh = s.stem * 0.92, s.hair * 0.94
    return ring(s, x0, y0, x0 + w, y0 + h, st, hh, corners_of(s, 66))


@glyph("percent", "%", 34, 34)
def percent(s: Style) -> Shape:
    w = s.w(690)
    rw = s.w(208)
    slash = diagonal((w * 0.2, -10), (w * 0.8, CAP + 10), s.stem * 0.84, -10, CAP + 10)
    return small_ring(s, 0, CAP - 296 + OVS, rw) | small_ring(s, w - rw, -OVS, rw) | slash


@glyph("perthousand", "‰", 34, 34)
def perthousand(s: Style) -> Shape:
    rw = s.w(208)
    return percent(s) | small_ring(s, s.w(690) + s.w(52), -OVS, rw)


# --- waluty ----------------------------------------------------------------------------------

def outside_bar(s: Style, cx: float, low: float, high: float, top: float, extend: float = 96) -> Shape:
    t = s.stem * 0.62
    return rect(cx - t / 2, low - extend, cx + t / 2, low + 2) | rect(cx - t / 2, high - 2, cx + t / 2, high + extend)


@glyph("dollar", "$", ("cap_round", 0.8), ("cap_round", 0.8))
def dollar(s: Style) -> Shape:
    from .common import s_shape

    w = s.w(452)
    body = s_shape(s, w, CAP + OVS, -OVS, s.stem_cap * 0.96, s.hair_cap, s.radius_cap * 0.9)
    return body | outside_bar(s, w / 2, -OVS, CAP + OVS, CAP)


@glyph("cent", "¢", "round", ("round", 0.72))
def cent(s: Style) -> Shape:
    body = lower.c(s)
    x0, _, x1, _ = body.bounds
    return body | outside_bar(s, x0 + (x1 - x0) * 0.46, -OVS, XH + OVS, XH, 100)


@glyph("sterling", "£", 30, 30)
def sterling(s: Style) -> Shape:
    st, hh, w = s.stem_cap, s.hair_cap, s.w(500)
    xs = s.w(86)
    c = upper.cap_corners(s, 0.85)
    top = CAP + OVS
    hook = box(xs, hh, xs + st + 400, top, tl=c["tl"]) - box(xs + st, -FAR, FAR, top - hh, tl=inner_corner(s, c["tl"], st, hh))
    hook = cut_right(s, hook, w - s.w(10), top - hh - 1, top + 1)
    return hook | rect(0, 0, w, hh) | upper.bar(s, CAP * 0.44, 0, xs + st + s.w(170))


@glyph("currency", "¤", 40, 40)
def currency(s: Style) -> Shape:
    size, tick = s.w(330), 58.0
    t = s.stem * 0.84
    body = ring(s, 0, 0, size, size, t, s.hair, corners_of(s, 90))
    stub = rect(-t / 2, -tick, t / 2, tick)
    inset = 26.0
    for cx, cy, angle in ((inset, inset, 45), (size - inset, inset, -45), (size - inset, size - inset, 45),
                          (inset, size - inset, -45)):
        body = body | rotated(stub.moved(cx, cy), angle, cx, cy)
    x0, y0, x1, y1 = body.bounds
    return body.moved(0, MATH_Y - (y0 + y1) / 2)


@glyph("yen", "¥", 10, 10)
def yen(s: Style) -> Shape:
    w = s.w(upper.W_Y)
    ystem = upper.Y(s)
    return ystem | upper.bar(s, CAP * 0.30, w * 0.16, w * 0.84) | upper.bar(s, CAP * 0.14, w * 0.16, w * 0.84)


@glyph("Euro", "€", 20, ("cap_round", 0.72))
def Euro(s: Style) -> Shape:
    shift = s.w(70)
    body = upper.C(s).moved(shift)
    w = s.w(upper.W_C) + shift
    return body | upper.bar(s, CAP * 0.58, 0, w * 0.74) | upper.bar(s, CAP * 0.40, 0, w * 0.70)


# --- prawne, stopnie ------------------------------------------------------------------------------

def badge(s: Style, inner_build) -> Shape:
    w = s.w(760)
    t, hh = s.stem * 0.78, s.hair * 0.8
    outer = ring(s, 0, -OVS, w, CAP + OVS, t, hh, corners_of(s, s.radius_cap * 1.3))
    mark = superior(s, inner_build, scale=0.52, top=CAP * 0.5 + 0.26 * CAP, boost=1.45)
    mx0, _, mx1, _ = mark.bounds
    return outer | mark.moved(w / 2 - (mx0 + mx1) / 2)


@glyph("copyright", "©", 40, 40)
def copyright(s: Style) -> Shape:
    return badge(s, upper.C)


@glyph("registered", "®", 40, 40)
def registered(s: Style) -> Shape:
    return badge(s, upper.R)


@glyph("trademark", "™", 40, 40)
def trademark(s: Style) -> Shape:
    t = superior(s, upper.T, scale=0.5, boost=1.4)
    m = superior(s, upper.M, scale=0.5, boost=1.4)
    _, _, tx1, _ = t.bounds
    mx0, _, _, _ = m.bounds
    return t | m.moved(tx1 + s.w(40) - mx0)


@glyph("degree", "°", 40, 40)
def degree(s: Style) -> Shape:
    size = s.w(206)
    t, th = min(s.stem * 0.72, size * 0.27), min(s.hair * 0.78, size * 0.25)
    return ring(s, 0, CAP - size + OVS, size, CAP + OVS, t, th, corners_of(s, 70))


# --- indeksy górne i ułamki -------------------------------------------------------------------------

@glyph("onesuperior", "¹", 40, 40)
def onesuperior(s: Style) -> Shape:
    return superior(s, digits.one)


@glyph("twosuperior", "²", 40, 40)
def twosuperior(s: Style) -> Shape:
    return superior(s, digits.two)


@glyph("threesuperior", "³", 40, 40)
def threesuperior(s: Style) -> Shape:
    return superior(s, digits.three)


def fraction(s: Style, num, den) -> Shape:
    w = s.w(800)
    top = superior(s, num)
    bottom = superior(s, den, top=CAP * 0.62 + OVS)
    bx0, _, bx1, _ = bottom.bounds
    slash = diagonal((w * 0.30, -10), (w * 0.72, CAP + 10), s.hair * 0.96, -10, CAP + 10)
    return top | slash | bottom.moved(w - bx1)


@glyph("onequarter", "¼", 30, 30)
def onequarter(s: Style) -> Shape:
    return fraction(s, digits.one, digits.four)


@glyph("onehalf", "½", 30, 30)
def onehalf(s: Style) -> Shape:
    return fraction(s, digits.one, digits.two)


@glyph("threequarters", "¾", 30, 30)
def threequarters(s: Style) -> Shape:
    return fraction(s, digits.three, digits.four)


# --- cyfry tabelaryczne ------------------------------------------------------------------------------

DIGIT_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def tabular_width(s: Style) -> float:
    return s.w(TABULAR_W)


def _tabular(name: str):
    def build(s: Style) -> Shape:
        from .registry import REGISTRY

        shape = REGISTRY[name].build(s)
        x0, _, x1, _ = shape.bounds
        return shape.moved((tabular_width(s) - (x1 - x0)) / 2 - x0)
    return build


for _name in DIGIT_NAMES:
    glyph(f"{_name}.tf", [], advance=tabular_width)(_tabular(_name))
