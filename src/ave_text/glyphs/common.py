"""Pomocnicze konstrukcje wspólne dla małych i wielkich liter."""

from __future__ import annotations

from ..shapes import Shape, band, below_line, corners_of, diagonal, inner_corner, outline, perp_width, polygon, rect
from ..style import FAR, Style


def diag_thickness(s: Style, factor: float = 0.94, stem: float | None = None) -> float:
    """Kreski ukośne są odrobinę cieńsze od trzonu, bo optycznie wydają się grubsze."""
    return (s.stem if stem is None else stem) * factor


def line_x(p0: tuple[float, float], p1: tuple[float, float], y: float) -> float:
    (x0, y0), (x1, y1) = p0, p1
    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)


def vertex(left_top: tuple[float, float], right_top: tuple[float, float], bottom: float, flat: float,
           td: float, bottom_y: float = 0.0) -> Shape:
    """Dolny wierzchołek jak w v: dwie kreski przycięte do zewnętrznego obrysu, więc ich narożniki
    nie wystają spod wierzchołka. bottom to środek płaskiego dna na wysokości bottom_y."""
    left_bottom, right_bottom = (bottom - flat / 2, bottom_y), (bottom + flat / 2, bottom_y)
    left = band(left_top, left_bottom, td, anchor="left")
    right = band(right_top, right_bottom, td, anchor="right")
    top = max(left_top[1], right_top[1])
    hull = polygon([
        (line_x(left_top, left_bottom, top + 1), top + 1), left_bottom, right_bottom,
        (line_x(right_top, right_bottom, top + 1), top + 1),
    ])
    return (left | right) & hull & rect(-FAR, bottom_y, FAR, top)


def apex(left_bottom: tuple[float, float], right_bottom: tuple[float, float], top: float, flat: float,
         td: float, top_y: float) -> Shape:
    """Górny wierzchołek jak w A: lustrzane odbicie `vertex` względem poziomu."""
    flip = lambda pt: (pt[0], -pt[1])  # noqa: E731
    shape = vertex(flip(left_bottom), flip(right_bottom), top, flat, td, bottom_y=-top_y)
    return shape.affine(1, 0, 0, -1, 0, 0)


def s_shape(s: Style, w: float, top: float, bot: float, st: float, hh: float, radius: float) -> Shape:
    """Kanciaste S jednym konturem: górna kreska, lewy bok, grzbiet, prawy bok, dolna kreska.
    Górna połowa jest odrobinę mniejsza (grzbiet nad środkiem), końcówki cięte jak w c."""
    h_spine = hh * 1.04
    v_left, v_right = st * 0.94, st * 0.98
    mid = (top + bot) / 2 + (top - bot) * 0.012
    y0, y1 = mid - h_spine / 2, mid + h_spine / 2
    cs = corners_of(s, radius)
    t_end, b_end = w - s.w(8), s.w(4)
    cut = s.cut
    return outline([
        (t_end + cut * hh / 2, top),
        (0, top, cs["tl"]),
        (0, y0, cs["bl"]),
        (w - v_right, y0, inner_corner(s, cs["tr"], v_right, h_spine)),
        (w - v_right, bot + hh, inner_corner(s, cs["br"], v_right, hh)),
        (b_end + cut * hh / 2, bot + hh),
        (b_end - cut * hh / 2, bot),
        (w, bot, cs["br"]),
        (w, y1, cs["tr"]),
        (v_left, y1, inner_corner(s, cs["bl"], v_left, h_spine)),
        (v_left, top - hh, inner_corner(s, cs["tl"], v_left, hh)),
        (t_end - cut * hh / 2, top - hh),
    ])


def k_shape(s: Style, st: float, w: float, height: float, top: float, td: float, joint: float = 0.22,
            leg_start: float = 0.34) -> Shape:
    """K/k: trzon, ramię i noga. Ramię wyznacza punkt, w którym jego DOLNA krawędź styka się
    z trzonem (joint × height), więc nic nie wystaje pod złączem niezależnie od grubości.
    Noga wyrasta z osi ramienia i jest ucięta wzdłuż tej osi (chowa się w ramieniu)."""
    y_joint = height * joint
    m = (w - st) / (height - y_joint)
    width = perp_width(td, m)

    def right_edge(y: float) -> float:
        return st + m * (y - y_joint)

    arm = polygon([
        (right_edge(y_joint) - width - 1, y_joint), (right_edge(y_joint), y_joint),
        (right_edge(height), height), (right_edge(height) - width, height),
    ]) & rect(st - 1, y_joint, FAR, height)
    axis0 = (right_edge(y_joint) - width / 2, y_joint)
    axis1 = (right_edge(height) - width / 2, height)
    start_y = y_joint + (height - y_joint) * leg_start
    start_x = line_x(axis0, axis1, start_y)
    leg = diagonal((start_x - width * 0.18, start_y), (w + s.w(6), 0), td * 1.03, 0, height)
    leg = leg & below_line(axis0, axis1) & rect(st - 1, 0, FAR, height)
    return rect(0, 0, st, top) | arm | leg
