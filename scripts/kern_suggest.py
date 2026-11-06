#!/usr/bin/env python3
"""Podpowiada wartości kerningu z profili glifów.

Dla pary liczy w każdym wierszu (co 10 j.) poziomy odstęp między obrysami, ogranicza go
do DEPTH i dobiera kerning tak, by suma odstępów była taka jak dla pary HH. Kerning nie
zbliży glifów bardziej niż na MIN_GAP (sprawdzane też na wysokości akcentów i ogonków).
Wynik to propozycja: wartości w src/ave_display/spacing.py ustawia się po obejrzeniu podglądu.

Użycie:  .venv/bin/python scripts/kern_suggest.py V/A T/A L/T
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ave_display.builder import build_glyphs  # noqa: E402
from ave_display.geometry import rect  # noqa: E402
from ave_display.spacing import SB  # noqa: E402

DEPTH, MIN_GAP, MAX_KERN = 220, 70, 260
VISIBLE = range(5, 700, 10)
ALL_ROWS = range(-245, 950, 10)


def main(pairs: list[str]) -> None:
    built = {g.name: g for g in build_glyphs()}
    cache: dict[tuple[str, int], tuple[float, float] | None] = {}

    def extent(name: str, y: int):
        if (name, y) not in cache:
            hit = built[name].shape & rect(-5000, y - 1, 5000, y + 1)
            x0, _, x1, _ = hit.bounds
            cache[(name, y)] = (x0, x1) if hit.area > 0 else None
        return cache[(name, y)]

    def gaps(a: str, b: str, rows) -> list[float]:
        out = []
        for y in rows:
            ea, eb = extent(a, y), extent(b, y)
            out.append(built[a].advance + eb[0] - ea[1] if ea and eb else float("inf"))
        return out

    target = 2 * SB.STEM * len(VISIBLE)
    for pair in pairs:
        a, b = pair.split("/")
        visible = gaps(a, b, VISIBLE)
        closest = min(gaps(a, b, ALL_ROWS))
        kern = 0
        for k in range(0, -MAX_KERN - 1, -5):
            if closest + k < MIN_GAP:
                break
            kern = k
            if sum(min(max(g + k, 0), DEPTH) for g in visible) <= target:
                break
        print(f"{a}/{b}: {kern}   (najmniejszy odstęp {min(visible):.0f} j.)")


if __name__ == "__main__":
    main(sys.argv[1:])
