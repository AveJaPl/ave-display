"""Rejestr glifów Ave Text: funkcja budująca kształt dla stylu, znaki Unicode i światła boczne."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Union

from ..shapes import Shape
from ..style import Style

# Światło boczne: liczba (j.), nazwa klasy ("stem", "round", "cap_stem", "cap_round"),
# krotka (klasa, mnożnik) albo funkcja stylu.
Side = Union[float, str, tuple, Callable[[Style], float]]

CLASSES = {
    "stem": lambda s: s.sb_stem,
    "round": lambda s: s.sb_round,
    "cap_stem": lambda s: s.sb_cap_stem,
    "cap_round": lambda s: s.sb_cap_round,
}


def side_value(s: Style, side: Side) -> float:
    if callable(side):
        return float(side(s))
    if isinstance(side, (int, float)):
        return float(side)
    if isinstance(side, str):
        return CLASSES[side](s)
    cls, factor = side
    return CLASSES[cls](s) * factor


@dataclass
class TextGlyph:
    name: str
    build: Callable[[Style], Shape]
    unicodes: list[int]
    left: Side
    right: Side
    advance: Callable[[Style], float] | None = None
    spacing_from: str | None = None
    extra: dict = field(default_factory=dict)


REGISTRY: dict[str, TextGlyph] = {}


def glyph(name: str, chars: str | list[int] = "", left: Side = 0, right: Side = 0, *,
          advance: Callable[[Style], float] | None = None, spacing_from: str | None = None):
    """Rejestruje funkcję budującą glif. spacing_from: glif bazowy, którego obrys i światła
    wyznaczają położenie (litery z akcentami mają odstępy litery bazowej)."""
    def to_codes(value):
        return [ord(c) for c in value] if isinstance(value, str) else list(value)

    def decorator(fn: Callable[[Style], Shape]):
        if name in REGISTRY:
            raise ValueError(f"glif {name} zarejestrowany dwa razy")
        REGISTRY[name] = TextGlyph(name, fn, to_codes(chars), left, right, advance, spacing_from)
        return fn

    return decorator
