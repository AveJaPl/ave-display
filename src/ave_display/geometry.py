"""Prymitywy Ave Display zależne od pochylenia 28°; ogólne kształty pochodzą z ave_core."""

from __future__ import annotations

import math

from ave_core.geometry import Shape, clip_box, polygon, rect, rounded, union

from .params import FAR, SLANT

__all__ = [
    "Shape", "union", "polygon", "rect", "rounded", "clip_box", "italic_slope", "upright_slope",
    "width_for", "band", "stroke", "diagonal_slope", "diagonal", "edge_x", "crossing_y",
]


def italic_slope(upright_slope: float) -> float:
    return upright_slope + SLANT


def upright_slope(italic: float) -> float:
    return italic - SLANT


def width_for(perp: float, slope: float) -> float:
    """Szerokość pozioma pasa o nachyleniu dx/dy=slope, który po pochyleniu ma grubość perp."""
    return perp * math.hypot(1.0, italic_slope(slope))


def band(x0: float, y0: float, x1: float, y1: float, width: float) -> Shape:
    """Równoległobok: lewa krawędź od (x0, y0) do (x1, y1), stała szerokość pozioma."""
    return polygon([(x0, y0), (x0 + width, y0), (x1 + width, y1), (x1, y1)])


def stroke(through, slope: float, perp: float, y_lo: float = -FAR, y_hi: float = FAR, edge: str = "left") -> Shape:
    """Pas o nachyleniu slope (dx/dy w układzie pionowym), którego wskazana krawędź przechodzi przez punkt."""
    w = width_for(perp, slope)
    x, y = through
    if edge == "right":
        x -= w
    elif edge == "center":
        x -= w / 2
    return band(x + (y_lo - y) * slope, y_lo, x + (y_hi - y) * slope, y_hi, w)


def diagonal_slope(left_pt, right_pt, perp: float) -> float:
    """Nachylenie pasa, którego lewa krawędź przechodzi przez left_pt, a prawa przez right_pt."""
    (xl, yl), (xr, yr) = left_pt, right_pt

    def miss(m):
        return xl + m * (yr - yl) + width_for(perp, m) - xr

    lo, hi = -20.0, 20.0
    f_lo = miss(lo)
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = miss(mid)
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return (lo + hi) / 2


def diagonal(left_pt, right_pt, perp: float, y_lo: float = -FAR, y_hi: float = FAR) -> Shape:
    """Pas, którego lewa krawędź przechodzi przez left_pt, a prawa przez right_pt."""
    return stroke(left_pt, diagonal_slope(left_pt, right_pt, perp), perp, y_lo, y_hi)


def edge_x(through, slope: float, y: float) -> float:
    """Współrzędna x prostej o nachyleniu dx/dy=slope przechodzącej przez punkt, na wysokości y."""
    return through[0] + (y - through[1]) * slope


def crossing_y(a, slope_a: float, b, slope_b: float) -> float:
    """Wysokość, na której przecinają się dwie proste zadane punktem i nachyleniem dx/dy."""
    return (b[0] - a[0] + a[1] * slope_a - b[1] * slope_b) / (slope_a - slope_b)
