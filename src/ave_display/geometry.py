"""Prymitywy geometryczne w układzie pionowym oraz operacje logiczne na konturach."""

from __future__ import annotations

import math
from functools import reduce

import pathops

from .params import FAR, SLANT


class Shape:
    """Zbiór konturów z operacjami | (suma), - (różnica), & (część wspólna)."""

    __slots__ = ("path",)

    def __init__(self, path: pathops.Path | None = None):
        self.path = path if path is not None else pathops.Path()

    def __or__(self, other: Shape) -> Shape:
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.UNION))

    def __sub__(self, other: Shape) -> Shape:
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.DIFFERENCE))

    def __and__(self, other: Shape) -> Shape:
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.INTERSECTION))

    def affine(self, a, b, c, d, e, f) -> Shape:
        path = self.path.transform(a, b, c, d, e, f)
        path.simplify(fix_winding=True)
        return Shape(path)

    def moved(self, dx: float, dy: float = 0) -> Shape:
        return self.affine(1, 0, 0, 1, dx, dy)

    def mirrored_x(self, axis: float) -> Shape:
        return self.affine(-1, 0, 0, 1, 2 * axis, 0)

    def rotated_180(self, cx: float, cy: float) -> Shape:
        return self.affine(-1, 0, 0, -1, 2 * cx, 2 * cy)

    def sheared(self, slope: float, origin_y: float) -> Shape:
        return self.affine(1, 0, slope, 1, -slope * origin_y, 0)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self.path.bounds

    @property
    def area(self) -> float:
        return self.path.area

    def draw(self, pen) -> None:
        self.path.draw(pen)


def union(*shapes: Shape) -> Shape:
    return reduce(lambda a, b: a | b, shapes, Shape())


def polygon(points) -> Shape:
    path = pathops.Path()
    path.moveTo(*points[0])
    for pt in points[1:]:
        path.lineTo(*pt)
    path.close()
    path.simplify(fix_winding=True)
    return Shape(path)


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def _toward(a, b, dist):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    return (a[0] + dx / length * dist, a[1] + dy / length * dist)


def _lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def _tangent_length(vertex, neighbour, corner):
    rx, ry, _ = corner
    horizontal = abs(neighbour[0] - vertex[0]) >= abs(neighbour[1] - vertex[1])
    return rx if horizontal else ry


def rounded(vertices) -> Shape:
    """Wielokąt z zaokrąglonymi narożnikami.

    Wierzchołek to (x, y) albo (x, y, (rx, ry, k)): rx/ry to długości stycznych
    wzdłuż krawędzi bardziej poziomej/pionowej, k to napięcie krzywej (0 = ścięcie,
    1 = ostry narożnik).
    """
    pts = [(v[0], v[1]) for v in vertices]
    corners = [v[2] if len(v) > 2 else None for v in vertices]
    n = len(pts)

    cuts = []
    for i in range(n):
        corner = corners[i]
        if corner is None:
            cuts.append((0.0, 0.0))
            continue
        prev_pt, next_pt = pts[i - 1], pts[(i + 1) % n]
        cuts.append((_tangent_length(pts[i], prev_pt, corner), _tangent_length(pts[i], next_pt, corner)))

    for i in range(n):
        j = (i + 1) % n
        edge = math.dist(pts[i], pts[j])
        if cuts[i][1] + cuts[j][0] > edge + 1e-6:
            raise ValueError(f"zaokrąglenia nie mieszczą się na krawędzi {pts[i]} -> {pts[j]}")

    path = pathops.Path()
    first = True
    for i in range(n):
        vertex = pts[i]
        corner = corners[i]
        if corner is None:
            if first:
                path.moveTo(*vertex)
                first = False
            else:
                path.lineTo(*vertex)
            continue
        k = corner[2]
        t1 = _toward(vertex, pts[i - 1], cuts[i][0])
        t2 = _toward(vertex, pts[(i + 1) % n], cuts[i][1])
        if first:
            path.moveTo(*t1)
            first = False
        else:
            path.lineTo(*t1)
        c1 = _lerp(t1, vertex, k)
        c2 = _lerp(t2, vertex, k)
        path.cubicTo(*c1, *c2, *t2)
    path.close()
    path.simplify(fix_winding=True)
    return Shape(path)


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


def clip_box(shape: Shape, x0: float, y0: float, x1: float, y1: float) -> Shape:
    return shape & rect(x0, y0, x1, y1)
