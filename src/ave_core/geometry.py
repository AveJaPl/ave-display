"""Wspólne prymitywy geometryczne krojów Ave: kontury i operacje logiczne na nich (skia-pathops)."""

from __future__ import annotations

import math
from functools import reduce

import pathops


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


def rounded(vertices, fit: bool = False) -> Shape:
    """Wielokąt z zaokrąglonymi narożnikami.

    Wierzchołek to (x, y) albo (x, y, (rx, ry, k)): rx/ry to długości stycznych
    wzdłuż krawędzi bardziej poziomej/pionowej, k to napięcie krzywej (0 = ścięcie,
    1 = ostry narożnik). fit=True: zaokrąglenia za długie dla krawędzi maleją
    proporcjonalnie zamiast zgłaszać błąd (potrzebne w grubszych odmianach).
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
            if not fit:
                raise ValueError(f"zaokrąglenia nie mieszczą się na krawędzi {pts[i]} -> {pts[j]}")
            # dopasowanie: oba zaokrąglenia na tej krawędzi maleją proporcjonalnie
            k = edge * 0.98 / (cuts[i][1] + cuts[j][0])
            cuts[i] = (cuts[i][0], cuts[i][1] * k)
            cuts[j] = (cuts[j][0] * k, cuts[j][1])

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


def clip_box(shape: Shape, x0: float, y0: float, x1: float, y1: float) -> Shape:
    return shape & rect(x0, y0, x1, y1)
