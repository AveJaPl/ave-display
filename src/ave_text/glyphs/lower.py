"""Małe litery a-z w układzie pionowym (kursywa = pochylenie + formy alternatywne).

Konstrukcja jak w kanciastych groteskach: łuk n, h, m, r wyrasta z trzonu poniżej jego
szczytu (małe wcięcie przy łączeniu), brzuszki b, d, p, q, g, a łączą się z trzonem
przewężeniem, końcówki c, e, s, a, r, f, t, l, j, g są cięte prosto albo pod kątem
pochylenia Ave Display (parametr stylu `cut`).
"""

from __future__ import annotations

from ..shapes import (
    Corner, Shape, band, box, corner, corners_of, cut_left, cut_right, diagonal,
    horizontal_width,
    inner_corner, outline, rect, ring,
)
from ..style import ASC, DESC, FAR, OVS, XH, Style
from .common import diag_thickness, k_shape, s_shape, vertex
from .registry import glyph

ARCH_OVS = 4
T_TOP = XH + 140

# Szerokości obrysu w Regular (j.), skalowane przez Style.width.
W_N = 432
W_M = 716
W_O = 452
W_BOWL = 464
W_A = 420
W_E = 440
W_C = 404
W_S = 392
W_V = 448
W_W = 690
W_X = 440
W_Y = 452
W_Z = 396
W_K = 428
R_ARM = 172
L_FOOT = 98
T_FOOT = 92
T_BAR = 100
F_ARM = 124
F_BAR = 100
F_LEFT = 56
T_LEFT = 50
J_HOOK = 112
G_HOOK = 22

# Ile zaokrąglenia narożnika zostaje na końcówce c/e (0 = cięcie przed łukiem, 1 = pełny łuk).
TERMINAL_ROUND = 0.4


def shoulder(s: Style, h: float) -> Corner:
    """Narożnik, którym łuk wyrasta z trzonu; ry < h, więc łuk zawsze łączy się z trzonem."""
    return corner(s, s.stem * 1.25, h * s.join, 0.6)


def arch(s: Style, x0: float, x1: float, radius: float, top: float = XH + ARCH_OVS) -> Shape:
    """Łuk n bez lewego trzonu: wyrasta z prawej krawędzi trzonu x0, prawa noga kończy się w x1."""
    st, h = s.stem, s.hair
    tr = corners_of(s, radius)["tr"]
    outer = outline([(x0 - 1, 0), (x1, 0), (x1, top, tr), (x0 - 1, top, shoulder(s, h))])
    counter = box(x0, -FAR, x1 - st, top - h, tr=inner_corner(s, tr, st, h))
    return outer - counter


def bowl(s: Style, x0: float, x1: float, stem_side: str, radius: float | None = None) -> Shape:
    """Brzuszek b/d/p/q bez trzonu. Po stronie trzonu narożniki są przewężonymi połączeniami."""
    st, h = s.stem, s.hair
    c = corners_of(s, s.radius if radius is None else radius)
    j = shoulder(s, h)
    y0, y1 = -OVS, XH + OVS
    if stem_side == "right":
        xs = x1 - st + 1
        outer = box(x0, y0, xs, y1, bl=c["bl"], br=j, tr=j, tl=c["tl"])
        inner = box(x0 + st, y0 + h, x1 - st, y1 - h,
                    bl=inner_corner(s, c["bl"], st, h), tl=inner_corner(s, c["tl"], st, h))
    else:
        xs = x0 + st - 1
        outer = box(xs, y0, x1, y1, bl=j, br=c["br"], tr=c["tr"], tl=j)
        inner = box(x0 + st, y0 + h, x1 - st, y1 - h,
                    br=inner_corner(s, c["br"], st, h), tr=inner_corner(s, c["tr"], st, h))
    return outer - inner


def dot(s: Style, cx: float, top: float | None = None) -> Shape:
    d = s.stem * 1.1
    if top is None:
        top = ASC + (d - 92.4) * 0.3
    r = corner(s, d * 0.24)
    return box(cx - d / 2, top - d, cx + d / 2, top, r, r, r, r)


def open_round(s: Style, width: float) -> tuple[Shape, dict[str, Corner]]:
    """Obrys c/e: lewy bok i oba narożniki prawe z zapasem na cięcie końcówek w x = width."""
    c = corners_of(s, s.radius)
    reach = width + c["tr"][0] * (1 - TERMINAL_ROUND)
    outer = box(0, -OVS, reach, XH + OVS, c["bl"], c["br"], c["tr"], c["tl"])
    return outer, c


def terminal_top(s: Style, shape: Shape, x: float, h: float, top: float = XH + OVS) -> Shape:
    return cut_right(s, shape, x, XH / 2, FAR, y_ref=top - h / 2)


def terminal_bottom(s: Style, shape: Shape, x: float, h: float, bottom: float = -OVS) -> Shape:
    return cut_right(s, shape, x, -FAR, XH / 2, y_ref=bottom + h / 2)


# --- n h m u r ----------------------------------------------------------------------------

@glyph("n", "n", "stem", "stem")
def n(s: Style) -> Shape:
    return rect(0, 0, s.stem, XH) | arch(s, s.stem, s.w(W_N), s.radius)


@glyph("h", "h", "stem", "stem")
def h(s: Style) -> Shape:
    return rect(0, 0, s.stem, ASC) | arch(s, s.stem, s.w(W_N), s.radius)


@glyph("m", "m", "stem", "stem")
def m(s: Style) -> Shape:
    st, w = s.stem, s.w(W_M)
    mid = (w - st) / 2
    r = s.radius * 0.82
    return rect(0, 0, st, XH) | arch(s, st, mid + st, r) | arch(s, mid + st, w, r)


@glyph("u", "u", "stem", "stem")
def u(s: Style) -> Shape:
    w = s.w(W_N)
    return n(s).rotated_180(w / 2, XH / 2)


@glyph("r", "r", "stem", 6)
def r(s: Style) -> Shape:
    st, hh = s.stem, s.hair
    top = XH + ARCH_OVS
    end = st + s.w(R_ARM)
    arm = arch(s, st, end + 200, s.radius) & rect(-FAR, top - hh, FAR, FAR)
    return rect(0, 0, st, XH) | cut_right(s, arm, end, top - hh - 1, top + 1)


# --- o c e s --------------------------------------------------------------------------------

@glyph("o", "o", "round", "round")
def o(s: Style) -> Shape:
    return ring(s, 0, -OVS, s.w(W_O), XH + OVS, s.stem, s.hair, corners_of(s, s.radius))


@glyph("c", "c", "round", ("round", 0.72))
def c(s: Style) -> Shape:
    w = s.w(W_C)
    outer, cs = open_round(s, w)
    counter = box(s.stem, -OVS + s.hair, FAR, XH + OVS - s.hair,
                  bl=inner_corner(s, cs["bl"], s.stem, s.hair), tl=inner_corner(s, cs["tl"], s.stem, s.hair))
    shape = outer - counter
    shape = terminal_top(s, shape, w, s.hair)
    return terminal_bottom(s, shape, w, s.hair)


@glyph("e", "e", "round", ("round", 0.86))
def e(s: Style) -> Shape:
    st, hh, w = s.stem, s.hair, s.w(W_E)
    cs = corners_of(s, s.radius)
    outer = box(0, -OVS, w, XH + OVS, cs["bl"], cs["br"], cs["tr"], cs["tl"])
    mid = XH / 2 + 12
    bar_lo, bar_hi = mid - s.bar / 2, mid + s.bar / 2
    upper = box(st, bar_hi, w - st, XH + OVS - hh,
                tl=inner_corner(s, cs["tl"], st, hh), tr=inner_corner(s, cs["tr"], st, hh))
    lower = box(st, -OVS + hh, FAR, bar_lo, bl=inner_corner(s, cs["bl"], st, hh))
    shape = outer - upper - lower
    return terminal_bottom(s, shape, w - cs["br"][0] * (1 - TERMINAL_ROUND) * 0.8, hh)


@glyph("s", "s", ("round", 0.84), ("round", 0.84))
def s_(s: Style) -> Shape:
    return s_shape(s, s.w(W_S), XH + OVS, -OVS, s.stem, s.hair, s.radius * 0.95)


# --- b d p q g a ----------------------------------------------------------------------------

@glyph("b", "b", "stem", "round")
def b(s: Style) -> Shape:
    w = s.w(W_BOWL)
    return rect(0, 0, s.stem, ASC) | bowl(s, 0, w, "left")


@glyph("d", "d", "round", "stem")
def d(s: Style) -> Shape:
    w = s.w(W_BOWL)
    return rect(w - s.stem, 0, w, ASC) | bowl(s, 0, w, "right")


@glyph("p", "p", "stem", "round")
def p(s: Style) -> Shape:
    w = s.w(W_BOWL)
    return rect(0, DESC, s.stem, XH) | bowl(s, 0, w, "left")


@glyph("q", "q", "round", "stem")
def q(s: Style) -> Shape:
    w = s.w(W_BOWL)
    return rect(w - s.stem, DESC, w, XH) | bowl(s, 0, w, "right")


@glyph("g", "g", "round", "stem")
def g(s: Style) -> Shape:
    st, hh, w = s.stem, s.hair, s.w(W_BOWL)
    bottom = DESC - OVS / 2
    cs = corners_of(s, s.radius)
    start = s.w(G_HOOK)
    hook = box(start - 200, bottom, w, XH / 2, br=cs["br"]) - box(-FAR, bottom + hh, w - st, FAR,
                                                                    br=inner_corner(s, cs["br"], st, hh))
    hook = cut_left(s, hook, start, bottom - 1, bottom + hh + 1)
    return bowl(s, 0, w, "right") | rect(w - st, 0, w, XH) | hook


def a_double(s: Style) -> Shape:
    st, hh, w = s.stem, s.hair, s.w(W_A)
    top = XH + OVS
    cs = corners_of(s, s.radius)
    start = s.w(30)
    hook = box(start - 200, 0, w, top, tr=cs["tr"]) - box(-FAR, -FAR, w - st, top - hh,
                                                            tr=inner_corner(s, cs["tr"], st, hh))
    hook = cut_left(s, hook, start, top - hh - 1, top + 1)
    bowl_top = XH * 0.57
    tl = corner(s, s.radius * 0.62)
    outer = box(0, -OVS, w - st + 1, bowl_top, bl=cs["bl"], br=shoulder(s, hh), tl=tl)
    inner = box(st, -OVS + hh, w - st, bowl_top - s.bar,
                bl=inner_corner(s, cs["bl"], st, hh), tl=inner_corner(s, tl, st, s.bar))
    return hook | (outer - inner)


def a_single(s: Style) -> Shape:
    w = s.w(W_BOWL) * 0.98
    return rect(w - s.stem, 0, w, XH) | bowl(s, 0, w, "right")


@glyph("a", "a", ("round", 0.9), "stem")
def a(s: Style) -> Shape:
    return a_single(s) if "a.single" in s.alternates else a_double(s)


# --- i j l t f ------------------------------------------------------------------------------

@glyph("i", "i", "stem", "stem")
def i(s: Style) -> Shape:
    return rect(0, 0, s.stem, XH) | dot(s, s.stem / 2)


@glyph("dotlessi", [0x0131], "stem", "stem")
def dotlessi(s: Style) -> Shape:
    return rect(0, 0, s.stem, XH)


@glyph("j", "j", 14, "stem")
def j(s: Style) -> Shape:
    st, hh = s.stem, s.hair
    x = s.w(J_HOOK)
    bottom = DESC - OVS / 2
    cs = corners_of(s, s.radius * 0.9)
    hook = box(-200, bottom, x + st, XH, br=cs["br"]) - box(-FAR, bottom + hh, x, FAR,
                                                            br=inner_corner(s, cs["br"], st, hh))
    hook = cut_left(s, hook, 0, bottom - 1, bottom + hh + 1)
    return hook | dot(s, x + st / 2)


@glyph("l", "l", "stem", 14)
def l(s: Style) -> Shape:  # noqa: E743
    st, hh = s.stem, s.hair
    end = st + s.w(L_FOOT)
    bl = corner(s, s.radius * 0.8)
    shape = outline([
        (0, ASC), (0, 0, bl), (end + 200, 0), (end + 200, hh),
        (st, hh, inner_corner(s, bl, st, hh)), (st, ASC),
    ])
    return cut_right(s, shape, end, -1, hh + 1)


@glyph("t", "t", 18, 16)
def t(s: Style) -> Shape:
    st, hh = s.stem, s.hair
    x = s.w(T_LEFT)
    end = x + st + s.w(T_FOOT)
    bl = corner(s, s.radius * 0.8)
    stem = outline([
        (x, T_TOP - st * 0.6), (x + st, T_TOP),
        (x + st, hh, inner_corner(s, bl, st, hh)), (end + 200, hh), (end + 200, 0), (x, 0, bl),
    ])
    stem = cut_right(s, stem, end, -1, hh + 1)
    return stem | rect(0, XH - s.bar, x + st + s.w(T_BAR), XH)


def f_upright(s: Style) -> Shape:
    st, hh = s.stem, s.hair
    x = s.w(F_LEFT)
    top = ASC + OVS / 2
    tl = corner(s, s.radius * 0.9)
    hook = box(x, 0, x + st + 400, top, tl=tl) - box(x + st, -FAR, FAR, top - hh,
                                                     tl=inner_corner(s, tl, st, hh))
    hook = cut_right(s, hook, x + st + s.w(F_ARM), top - hh - 1, top + 1)
    return hook | rect(0, XH - s.bar, x + st + s.w(F_BAR), XH)


def f_descender(s: Style) -> Shape:
    """f kursywy: trzon schodzi pod linię pisma i kończy się haczykiem w lewo (jak w Exo 2)."""
    st, hh = s.stem, s.hair
    x = s.w(F_LEFT + 40)
    top, bottom = ASC + OVS / 2, DESC - OVS / 2
    tl = corner(s, s.radius * 0.9)
    br = corner(s, s.radius * 0.85)
    body = box(x, 0, x + st + 400, top, tl=tl) - box(x + st, -FAR, FAR, top - hh, tl=inner_corner(s, tl, st, hh))
    body = cut_right(s, body, x + st + s.w(F_ARM), top - hh - 1, top + 1)
    hook = box(x - 300, bottom, x + st, XH, br=br) - box(-FAR, bottom + hh, x, FAR, br=inner_corner(s, br, st, hh))
    hook = cut_left(s, hook, x - s.w(96), bottom - 1, bottom + hh + 1)
    return body | hook | rect(x - s.w(F_LEFT), XH - s.bar, x + st + s.w(F_BAR), XH)


def f_left(s: Style) -> float:
    return -24.0 if "f.descender" in s.alternates else 16.0


def f_right(s: Style) -> float:
    return -14.0 if "f.descender" in s.alternates else -6.0


@glyph("f", "f", f_left, f_right)
def f(s: Style) -> Shape:
    return f_descender(s) if "f.descender" in s.alternates else f_upright(s)


# --- ukośne: k v w x y z ------------------------------------------------------------------------

@glyph("k", "k", "stem", 10)
def k(s: Style) -> Shape:
    return k_shape(s, s.stem, s.w(W_K), XH, ASC, diag_thickness(s))


@glyph("v", "v", 14, 14)
def v(s: Style) -> Shape:
    w, td = s.w(W_V), diag_thickness(s)
    return vertex((0, XH), (w, XH), w / 2, s.stem * 0.7, td)


@glyph("w", "w", 12, 12)
def w_(s: Style) -> Shape:
    w, td = s.w(W_W), diag_thickness(s, 0.88)
    flat = s.stem * 0.55
    b1, b2, mid = w * 0.265, w * 0.735, w / 2
    return vertex((0, XH), (mid + flat / 2, XH), b1, flat, td) | vertex((mid - flat / 2, XH), (w, XH), b2, flat, td)


@glyph("x", "x", 12, 12)
def x(s: Style) -> Shape:
    w, td = s.w(W_X), diag_thickness(s, 0.92)
    one = diagonal((0, XH), (w, 0), td)
    two = diagonal((0, 0), (w, XH), td)
    return (one | two) & rect(0, 0, w, XH)


@glyph("y", "y", 14, 14)
def y(s: Style) -> Shape:
    w, td = s.w(W_Y), diag_thickness(s)
    base = w * 0.6
    width_r = horizontal_width(td, (w, XH), (base, 0))
    right = band((w, XH), (base, 0), td, DESC, XH, anchor="right")
    left = band((0, XH), (base - width_r, 0), td, 0, XH, anchor="left")
    return (left | right) & rect(-FAR, DESC, w, XH)


@glyph("z", "z", 34, 34)
def z(s: Style) -> Shape:
    w, hh = s.w(W_Z), s.hair
    td = diag_thickness(s, 0.92)
    bars = rect(s.w(10), XH - hh, w, XH) | rect(0, 0, w, hh)
    diag = diagonal((0, hh), (w, XH - hh), td, 0, XH)
    return bars | (diag & rect(0, 0, w, XH))
