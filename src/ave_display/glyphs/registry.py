"""Rejestr glifów: kształt w układzie pionowym, znaki Unicode i światła boczne."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..geometry import Shape


@dataclass
class GlyphSpec:
    name: str
    build: Callable[[], Shape]
    unicodes: list[int]
    lsb: float
    rsb: float
    spacing_from: str | None = None
    advance: float | None = None
    extra_unicodes: list[int] = field(default_factory=list)
    left_edge: float | None = None


REGISTRY: dict[str, GlyphSpec] = {}


def glyph(name: str, chars: str | list[int] = "", lsb: float = 0, rsb: float = 0, *,
          spacing_from: str | None = None, advance: float | None = None, also: str | list[int] = "",
          left_edge: float | None = None):
    """Rejestruje funkcję budującą glif.

    chars: znaki mapowane na glif; also: dodatkowe znaki (np. małe litery);
    spacing_from: glif, którego obrys wyznacza światła (dla liter z diakrytykami);
    left_edge: x, od którego liczy się lewe światło zamiast skrajnego punktu (np. trzon,
    gdy ostrze belki ma wchodzić w pole poprzedniej litery).
    """

    def to_codes(value):
        if isinstance(value, str):
            return [ord(c) for c in value]
        return list(value)

    def decorator(fn: Callable[[], Shape]):
        REGISTRY[name] = GlyphSpec(
            name=name,
            build=fn,
            unicodes=to_codes(chars),
            lsb=lsb,
            rsb=rsb,
            spacing_from=spacing_from,
            advance=advance,
            extra_unicodes=to_codes(also),
            left_edge=left_edge,
        )
        return fn

    return decorator
