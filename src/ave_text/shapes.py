"""Prymitywy kroju tekstowego: zaokrąglone prostokąty, pierścienie, końcówki, kreski ukośne.

Wszystko rysujemy w układzie pionowym (bez pochylenia). Narożnik to krotka (rx, ry, k):
rx/ry to długości stycznych wzdłuż krawędzi poziomej/pionowej, k to napięcie krzywej
(0,55 ≈ okrąg, więcej = bardziej kanciasto).
"""

from __future__ import annotations

import math
from contextlib import contextmanager
from contextvars import ContextVar

from ave_core.geometry import Shape, polygon, rect, rounded, union

from .style import FAR, Style

Corner = tuple[float, float, float] | None

# Nachylenie kursywy (dx/dy) aktywne podczas budowania glifów stylu. Ukośne kreski liczą
# grubość po pochyleniu, więc w kursywie lewa i prawa kreska v/A/V mają tę samą grubość.
_SLANT: ContextVar[float] = ContextVar("ave_text_slant", default=0.0)


@contextmanager
def slanted(slope: float):
    token = _SLANT.set(slope)
    try:
        yield
    finally:
        _SLANT.reset(token)


def perp_width(thickness: float, m: float) -> float:
    """Szerokość pozioma pasa o nachyleniu m (dx/dy, przed pochyleniem), który PO pochyleniu
    kursywy ma prostopadłą grubość `thickness`."""
    return thickness * math.hypot(1.0, m + _SLANT.get())

__all__ = [
    "Shape", "Corner", "polygon", "rect", "rounded", "union", "corner", "box", "outline", "corners_of",
    "inner_corner", "ring", "cut_right", "cut_left", "band", "slab", "diagonal", "diagonal_geometry", "below_line", "slanted", "perp_width",
    "horizontal_width",
]


def corner(s: Style, rx: float, ry: float | None = None, k: float | None = None) -> Corner:
    return (rx, rx if ry is None else ry, s.tension if k is None else k)


def corners_of(s: Style, r: float, ry: float | None = None) -> dict[str, Corner]:
    """Cztery narożniki o promieniu r. Przy asym > 1 narożniki prawy górny i lewy dolny są większe,
    jak w Ave Display, gdzie po pochyleniu te narożniki stają się ostre."""
    ry = r if ry is None else ry
    big, small = s.asym, 1.0 / s.asym
    return {
        "bl": corner(s, r * big, ry * big), "tr": corner(s, r * big, ry * big),
        "tl": corner(s, r * small, ry * small), "br": corner(s, r * small, ry * small),
    }


def inner_corner(s: Style, outer: Corner, tv: float, th: float, minimum: float = 8.0) -> Corner:
    """Narożnik światła współśrodkowy z narożnikiem zewnętrznym kreski o grubościach tv (pion) i th (poziom)."""
    if outer is None:
        return None
    rx, ry, k = outer
    return ((max(rx - tv, minimum)) * s.inner, (max(ry - th, minimum)) * s.inner, k)


def _vertex(x: float, y: float, c: Corner):
    return (x, y) if c is None else (x, y, c)


def box(x0: float, y0: float, x1: float, y1: float, bl: Corner = None, br: Corner = None,
        tr: Corner = None, tl: Corner = None) -> Shape:
    return rounded([_vertex(x0, y0, bl), _vertex(x1, y0, br), _vertex(x1, y1, tr), _vertex(x0, y1, tl)], fit=True)


def outline(points) -> Shape:
    """Wielokąt z opcjonalnymi zaokrągleniami: punkty (x, y) albo (x, y, narożnik-lub-None)."""
    return rounded([p if len(p) == 2 or p[2] is not None else (p[0], p[1]) for p in points], fit=True)


def ring(s: Style, x0: float, y0: float, x1: float, y1: float, tv: float, th: float,
         corners: dict[str, Corner]) -> Shape:
    outer = box(x0, y0, x1, y1, corners["bl"], corners["br"], corners["tr"], corners["tl"])
    inner = box(x0 + tv, y0 + th, x1 - tv, y1 - th,
                *(inner_corner(s, corners[key], tv, th) for key in ("bl", "br", "tr", "tl")))
    return outer - inner


def cut_right(s: Style, shape: Shape, x: float, y_lo: float, y_hi: float, y_ref: float | None = None) -> Shape:
    """Odcina końcówkę: usuwa wszystko na prawo od linii przez (x, y_ref) między y_lo i y_hi.
    Linia jest pionowa albo pochylona jak trzony Ave Display (s.cut)."""
    y_ref = (y_lo + y_hi) / 2 if y_ref is None else y_ref
    xa = x + s.cut * (y_lo - y_ref)
    xb = x + s.cut * (y_hi - y_ref)
    return shape - polygon([(xa, y_lo), (FAR, y_lo), (FAR, y_hi), (xb, y_hi)])


def cut_left(s: Style, shape: Shape, x: float, y_lo: float, y_hi: float, y_ref: float | None = None) -> Shape:
    y_ref = (y_lo + y_hi) / 2 if y_ref is None else y_ref
    xa = x + s.cut * (y_lo - y_ref)
    xb = x + s.cut * (y_hi - y_ref)
    return shape - polygon([(-FAR, y_lo), (xa, y_lo), (xb, y_hi), (-FAR, y_hi)])


def band(p0: tuple[float, float], p1: tuple[float, float], thickness: float,
         y_lo: float = -FAR, y_hi: float = FAR, anchor: str = "center") -> Shape:
    """Pas o prostopadłej grubości `thickness` wzdłuż prostej p0→p1, przycięty do y_lo..y_hi.
    anchor mówi, która krawędź pasa przechodzi przez p0/p1: left, right albo center."""
    (x0, y0), (x1, y1) = p0, p1
    dy = y1 - y0
    if abs(dy) < 1e-9:
        raise ValueError("band: prosta pozioma, użyj rect")
    slope = (x1 - x0) / dy
    width = perp_width(thickness, slope)
    offset = {"left": 0.0, "right": -width, "center": -width / 2}[anchor]

    def x_at(y: float) -> float:
        return x0 + (y - y0) * slope + offset

    return polygon([(x_at(y_lo), y_lo), (x_at(y_lo) + width, y_lo), (x_at(y_hi) + width, y_hi), (x_at(y_hi), y_hi)])


def slab(x0: float, y0: float, x1: float, y1: float) -> Shape:
    """Prostokąt dopuszczający odwrócone współrzędne."""
    return rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def diagonal_geometry(left_pt: tuple[float, float], right_pt: tuple[float, float],
                      thickness: float) -> tuple[float, float]:
    """Nachylenie m (dx/dy) i szerokość pozioma pasa, którego lewa krawędź przechodzi przez left_pt,
    a prawa przez right_pt."""
    (xl, yl), (xr, yr) = left_pt, right_pt
    if abs(yr - yl) < 1e-9:
        raise ValueError("diagonal: punkty na tej samej wysokości")

    def miss(m: float) -> float:
        return xl + m * (yr - yl) + perp_width(thickness, m) - xr

    lo, hi = -50.0, 50.0
    f_lo = miss(lo)
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = miss(mid)
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    m = (lo + hi) / 2
    return m, perp_width(thickness, m)


def diagonal(left_pt: tuple[float, float], right_pt: tuple[float, float], thickness: float,
             y_lo: float = -FAR, y_hi: float = FAR) -> Shape:
    """Pas o prostopadłej grubości `thickness`, którego lewa krawędź przechodzi przez left_pt,
    a prawa przez right_pt (punkty na różnych wysokościach)."""
    m, width = diagonal_geometry(left_pt, right_pt, thickness)
    xl, yl = left_pt

    def x_at(y: float) -> float:
        return xl + (y - yl) * m

    return polygon([(x_at(y_lo), y_lo), (x_at(y_lo) + width, y_lo), (x_at(y_hi) + width, y_hi), (x_at(y_hi), y_hi)])


def below_line(p0: tuple[float, float], p1: tuple[float, float]) -> Shape:
    """Półpłaszczyzna pod prostą przez p0 i p1 (prosta nie może być pionowa)."""
    (x0, y0), (x1, y1) = p0, p1
    k = (y1 - y0) / (x1 - x0)
    return polygon([(-FAR, -FAR * 8), (FAR, -FAR * 8), (FAR, y0 + (FAR - x0) * k), (-FAR, y0 + (-FAR - x0) * k)])


def horizontal_width(thickness: float, p0: tuple[float, float], p1: tuple[float, float]) -> float:
    """Szerokość pozioma pasa o prostopadłej grubości `thickness` biegnącego mniej więcej p0→p1."""
    (x0, y0), (x1, y1) = p0, p1
    return perp_width(thickness, (x1 - x0) / (y1 - y0))
