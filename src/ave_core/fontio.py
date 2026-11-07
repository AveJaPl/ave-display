"""Wspólne kroki zapisu fontu: kontury TrueType, tabela gasp, pliki TTF i WOFF2."""

from __future__ import annotations

from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

from .geometry import Shape


def to_tt_glyph(shape: Shape):
    """Kontur z krzywymi trzeciego stopnia → glif TrueType (krzywe kwadratowe, współrzędne całkowite)."""
    pen = TTGlyphPen(None)
    shape.draw(Cu2QuPen(RoundingPen(pen), max_err=0.4, reverse_direction=True))
    return pen.glyph()


def gasp_smooth_all() -> object:
    """gasp: wygładzanie i hinting siatki we wszystkich rozmiarach."""
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    return gasp


def save_ttf_and_woff2(fb: FontBuilder, out_dir: Path, ps_name: str) -> tuple[Path, Path]:
    ttf_path = out_dir / f"{ps_name}.ttf"
    woff2_path = out_dir / f"{ps_name}.woff2"
    fb.save(str(ttf_path))
    write_woff2(ttf_path, woff2_path)
    return ttf_path, woff2_path


def write_woff2(ttf_path: Path, woff2_path: Path) -> None:
    web = TTFont(str(ttf_path))
    web.flavor = "woff2"
    web.save(str(woff2_path))


def hint_ttf(ttf_path: Path) -> None:
    """Hinting ttfautohint (w miejscu). Instrukcje wyostrzają kreski na siatce pikseli w małych
    rozmiarach (14-18 px), co widać zwłaszcza na Windowsie. Opcja windows_compatibility
    dopasowuje strefy do usWinAscent/usWinDescent, no_info nie dopisuje wersji do nazw."""
    import ttfautohint

    data = ttfautohint.ttfautohint(
        in_buffer=ttf_path.read_bytes(),
        hinting_range_min=8, hinting_range_max=48, hinting_limit=200,
        windows_compatibility=True, no_info=True, default_script="latn",
    )
    ttf_path.write_bytes(data)
