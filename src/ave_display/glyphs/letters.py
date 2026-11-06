"""Wersaliki A-Z w układzie pionowym. Małe litery wskazują na te same glify."""

from ..geometry import (
    Shape, clip_box, crossing_y, diagonal, diagonal_slope, polygon, rect, rounded, stroke, width_for,
)
from ..params import (
    BACKCUT, BAR, BEAM_TIP_X, BOWL, CAP, DIAG, FAR, LEG, MID_HI, MID_LO, R_MID_HI, R_MID_LO,
    RA, RB, SLANT, STEM, STENCIL, TIP_X, rA, rB,
)
from ..spacing import SB
from .registry import glyph

LEG_SLOPE = -(1 + SLANT)
ARM_SLOPE = 1 - SLANT


def tip_of(tip_x: float) -> float:
    return tip_x - BACKCUT * BAR


def tip_beam(x_right: float, tip_x: float | None = None) -> Shape:
    """Górna belka, której lewy koniec jest ścięty jak w R."""
    tip_x = BEAM_TIP_X if tip_x is None else tip_x
    return polygon([(tip_x, CAP - BAR), (x_right, CAP - BAR), (x_right, CAP), (tip_of(tip_x), CAP)])


def open_bowl(width: float, bottom: float, counter_bottom: float, tip_x: float = TIP_X) -> Shape:
    """Belka ze ściętym końcem i brzuszkiem po prawej; światło otwarte w lewo."""
    outer = rounded([
        (0, bottom), (width, bottom, RB), (width, CAP, RA),
        (tip_of(tip_x), CAP), (tip_x, CAP - BAR), (0, CAP - BAR),
    ])
    counter = rounded([
        (-FAR, counter_bottom), (width - BOWL, counter_bottom, rB),
        (width - BOWL, CAP - BAR, rA), (-FAR, CAP - BAR),
    ])
    return outer - counter


def ring(width: float, height: float = CAP, side: float = STEM, bar: float = BAR) -> Shape:
    outer = rounded([(0, 0, RA), (width, 0, RB), (width, height, RA), (0, height, RB)])
    inner = rounded([
        (side, bar, rA), (width - side, bar, rB),
        (width - side, height - bar, rA), (side, height - bar, rB),
    ])
    return outer - inner


def v_shape(x0: float, x1: float, flat: float, height: float = CAP, perp: float = DIAG) -> Shape:
    """V o płaskim dnie; każde ramię ma grubość perp po pochyleniu."""
    cx = (x0 + x1) / 2
    left_slope = -(cx - flat / 2 - x0) / height
    right_slope = (x1 - cx - flat / 2) / height
    left = stroke((x0, height), left_slope, perp)
    right = stroke((x1, height), right_slope, perp, edge="right")
    silhouette = polygon([(x0, height), (cx - flat / 2, 0), (cx + flat / 2, 0), (x1, height)])
    return (left | right) & silhouette


A_WIDTH = 940


@glyph("A", "A", SB.DIAG, SB.STEM, also="a")
def A() -> Shape:
    w = A_WIDTH
    diag = stroke((0, 0), ARM_SLOPE, LEG, 0, CAP)
    body = diag | rect(0, CAP - BAR, w, CAP) | rect(0, R_MID_LO, w, R_MID_HI) | rect(w - STEM, 0, w, CAP)
    return body & polygon([(0, 0), (w, 0), (w, CAP), (ARM_SLOPE * CAP, CAP)])


B_WIDTH, B_TOP = 880, 850


@glyph("B", "B", SB.TIP, SB.ROUND, also="b", left_edge=0)
def B() -> Shape:
    upper = rounded([
        (0, MID_LO), (B_TOP, MID_LO, RB), (B_TOP, CAP, RA),
        (tip_of(BEAM_TIP_X), CAP), (BEAM_TIP_X, CAP - BAR), (0, CAP - BAR),
    ])
    lower = rounded([(0, 0), (B_WIDTH, 0, RB), (B_WIDTH, MID_HI, RB), (0, MID_HI)])
    upper_counter = rounded([
        (-FAR, MID_HI), (B_TOP - BOWL, MID_HI, rB), (B_TOP - BOWL, CAP - BAR, rA), (-FAR, CAP - BAR),
    ])
    lower_counter = rounded([
        (STEM, BAR), (B_WIDTH - BOWL, BAR, rB), (B_WIDTH - BOWL, MID_LO, rA), (STEM, MID_LO),
    ])
    return (upper | lower) - upper_counter - lower_counter


C_WIDTH = 840


@glyph("C", "C", SB.ROUND, SB.BAR, also="c")
def C() -> Shape:
    w = C_WIDTH
    outer = rounded([(0, 0, RA), (w, 0), (w, CAP), (0, CAP, RB)])
    counter = rounded([(STEM, BAR, rA), (FAR, BAR), (FAR, CAP - BAR), (STEM, CAP - BAR, rB)])
    return outer - counter


D_WIDTH = 860


@glyph("D", "D", SB.TIP, SB.ROUND, also="d", left_edge=0)
def D() -> Shape:
    w = D_WIDTH
    outer = rounded([
        (0, 0), (w, 0, RB), (w, CAP, RA), (tip_of(BEAM_TIP_X), CAP), (BEAM_TIP_X, CAP - BAR), (0, CAP - BAR),
    ])
    counter = rounded([
        (-FAR, R_MID_HI), (STEM, R_MID_HI), (STEM, BAR), (w - BOWL, BAR, rB),
        (w - BOWL, CAP - BAR, rA), (-FAR, CAP - BAR),
    ])
    return outer - counter


E_WIDTH, E_MID = 720, 630


@glyph("E", "E", SB.TIP, SB.BAR, also="e", left_edge=0)
def E() -> Shape:
    return tip_beam(E_WIDTH) | rect(0, MID_LO, E_MID, MID_HI) | rect(0, 0, E_WIDTH, BAR) | rect(0, 0, STEM, MID_HI)


@glyph("F", "F", SB.TIP, SB.BAR, also="f", left_edge=0)
def F() -> Shape:
    return tip_beam(E_WIDTH) | rect(0, MID_LO, E_MID, MID_HI) | rect(0, 0, STEM, MID_HI)


G_WIDTH, G_BAR_X = 880, 470


@glyph("G", "G", SB.ROUND, SB.STEM, also="g")
def G() -> Shape:
    w = G_WIDTH
    outer = rounded([(0, 0, RA), (w, 0, RB), (w, CAP), (0, CAP, RB)])
    counter = rounded([
        (STEM, BAR, rA), (w - STEM, BAR, rB), (w - STEM, MID_LO), (G_BAR_X, MID_LO),
        (G_BAR_X, MID_HI), (FAR, MID_HI), (FAR, CAP - BAR), (STEM, CAP - BAR, rB),
    ])
    return outer - counter


H_WIDTH = 880


@glyph("H", "H", SB.STEM, SB.STEM, also="h")
def H() -> Shape:
    return rect(0, 0, STEM, CAP) | rect(H_WIDTH - STEM, 0, H_WIDTH, CAP) | rect(0, MID_LO, H_WIDTH, MID_HI)


@glyph("I", "I", SB.STEM, SB.STEM, also="i")
def I() -> Shape:  # noqa: E743
    return rect(0, 0, STEM, CAP)


J_WIDTH, J_STUB = 780, 330


@glyph("J", "J", SB.BAR, SB.STEM, also="j")
def J() -> Shape:
    w = J_WIDTH
    return rounded([
        (0, J_STUB), (0, 0, RA), (w, 0, RB), (w, CAP), (w - STEM, CAP),
        (w - STEM, BAR, rB), (STEM, BAR, rA), (STEM, J_STUB),
    ])


K_NODE, K_ARM_SLOPE = 320, 0.8


@glyph("K", "K", SB.STEM, SB.LEG, also="k")
def K() -> Shape:
    node = (STEM, K_NODE)
    crotch = crossing_y(
        (STEM + width_for(LEG, K_ARM_SLOPE), K_NODE), K_ARM_SLOPE,
        (STEM + width_for(LEG, LEG_SLOPE), K_NODE), LEG_SLOPE,
    )
    arm = stroke(node, K_ARM_SLOPE, LEG, crotch, CAP)
    leg = stroke(node, LEG_SLOPE, LEG, 0, crotch)
    return clip_box(rect(0, 0, STEM, CAP) | arm | leg, 0, 0, FAR, CAP)


L_WIDTH = 700


@glyph("L", "L", SB.STEM, SB.BAR, also="l")
def L() -> Shape:
    return rect(0, 0, STEM, CAP) | rect(0, 0, L_WIDTH, BAR)


M_WIDTH, M_VERTEX, M_FLAT = 1180, 220, 0


@glyph("M", "M", SB.STEM, SB.STEM, also="m")
def M() -> Shape:
    w = M_WIDTH
    cx = w / 2
    low_left, low_right = (cx - M_FLAT / 2, M_VERTEX), (cx + M_FLAT / 2, M_VERTEX)
    m_left = diagonal_slope(low_left, (STEM, CAP), DIAG)
    m_right = diagonal_slope((w - STEM, CAP), low_right, DIAG)
    left = stroke(low_left, m_left, DIAG)
    right = stroke((w - STEM, CAP), m_right, DIAG)
    y_left = M_VERTEX + (STEM - low_left[0]) / m_left
    y_right = M_VERTEX + (w - STEM - low_right[0]) / m_right
    silhouette = polygon([
        (0, 0), (0, CAP), (w, CAP), (w, 0), (w - STEM, 0), (w - STEM, y_right),
        low_right, low_left, (STEM, y_left), (STEM, 0),
    ])
    return (rect(0, 0, STEM, CAP) | rect(w - STEM, 0, w, CAP) | left | right) & silhouette


N_WIDTH = 960


@glyph("N", "N", SB.STEM, SB.STEM, also="n")
def N() -> Shape:
    w = N_WIDTH
    diag = diagonal((w - STEM, 0), (STEM, CAP), DIAG)
    return clip_box(rect(0, 0, STEM, CAP) | rect(w - STEM, 0, w, CAP) | diag, 0, 0, w, CAP)


O_WIDTH = 900


@glyph("O", "O", SB.ROUND, SB.ROUND, also="o")
def O() -> Shape:
    return ring(O_WIDTH)


R_WIDTH = 902


@glyph("P", "P", SB.TIP, SB.ROUND, also="p", left_edge=0)
def P() -> Shape:
    return open_bowl(R_WIDTH, R_MID_LO, R_MID_HI) | rect(0, 0, STEM, R_MID_HI)


Q_TAIL_X, Q_TAIL_DROP = 640, 100


@glyph("Q", "Q", SB.ROUND, SB.LEG, also="q")
def Q() -> Shape:
    tail = stroke((Q_TAIL_X, 0), LEG_SLOPE, LEG, -Q_TAIL_DROP, BAR)
    return ring(O_WIDTH) | tail


@glyph("R", "R", SB.TIP, SB.LEG, also="r", left_edge=0)
def R() -> Shape:
    leg = stroke((735, 0), LEG_SLOPE, LEG, 0, R_MID_LO + 60)
    return open_bowl(R_WIDTH, R_MID_LO, R_MID_HI) | rect(0, 0, STEM, R_MID_HI) | leg


S_WIDTH = 860


@glyph("S", "S", SB.ROUND, SB.ROUND, also="s")
def S() -> Shape:
    w = S_WIDTH
    return rounded([
        (w, CAP), (0, CAP, RB), (0, MID_LO, RA), (w - STEM, MID_LO, rA), (w - STEM, BAR, rB),
        (0, BAR), (0, 0), (w, 0, RB), (w, MID_HI, RA), (STEM, MID_HI, rA),
        (STEM, CAP - BAR, rB), (w, CAP - BAR),
    ])


T_WIDTH = 740


@glyph("T", "T", SB.BAR, SB.BAR, also="t")
def T() -> Shape:
    cx = T_WIDTH / 2
    return rect(0, CAP - BAR, T_WIDTH, CAP) | rect(cx - STEM / 2, 0, cx + STEM / 2, CAP - BAR - STENCIL)


U_WIDTH = 880


@glyph("U", "U", SB.STEM, SB.STEM, also="u")
def U() -> Shape:
    w = U_WIDTH
    outer = rounded([(0, CAP), (0, 0, RA), (w, 0, RB), (w, CAP)])
    counter = rounded([(STEM, FAR), (STEM, BAR, rA), (w - STEM, BAR, rB), (w - STEM, FAR)])
    return outer - counter


V_WIDTH, V_FLAT = 920, 250


@glyph("V", "V", SB.DIAG, SB.DIAG, also="v")
def V() -> Shape:
    return v_shape(0, V_WIDTH, V_FLAT)


W_WIDTH, W_SPAN, W_FLAT = 1320, 760, 200


@glyph("W", "W", SB.DIAG, SB.DIAG, also="w")
def W() -> Shape:
    return v_shape(0, W_SPAN, W_FLAT) | v_shape(W_WIDTH - W_SPAN, W_WIDTH, W_FLAT)


X_WIDTH = 900


@glyph("X", "X", SB.DIAG, SB.DIAG, also="x")
def X() -> Shape:
    w = X_WIDTH
    back = diagonal((0, CAP), (w, 0), DIAG)
    fore = diagonal((0, 0), (w, CAP), DIAG)
    return clip_box(back | fore, 0, 0, w, CAP)


Y_WIDTH, Y_JOIN = 900, 300


@glyph("Y", "Y", SB.DIAG, SB.DIAG, also="y")
def Y() -> Shape:
    w = Y_WIDTH
    cx = w / 2
    left = stroke((0, CAP), -(cx - STEM / 2) / (CAP - Y_JOIN), DIAG)
    right = stroke((w, CAP), (w - cx - STEM / 2) / (CAP - Y_JOIN), DIAG, edge="right")
    stem = rect(cx - STEM / 2, 0, cx + STEM / 2, Y_JOIN)
    silhouette = polygon([
        (0, CAP), (w, CAP), (cx + STEM / 2, Y_JOIN), (cx + STEM / 2, 0),
        (cx - STEM / 2, 0), (cx - STEM / 2, Y_JOIN),
    ])
    return (left | right | stem) & silhouette


Z_WIDTH = 840


@glyph("Z", "Z", SB.BAR, SB.BAR, also="z")
def Z() -> Shape:
    w = Z_WIDTH
    diag = diagonal((0, BAR), (w, CAP - BAR), DIAG)
    return clip_box(rect(0, CAP - BAR, w, CAP) | rect(0, 0, w, BAR) | diag, 0, 0, w, CAP)
