"""Składanie Ave Text: glify stylu → odstępy → pochylenie kursywy → TTF i WOFF2.

Cztery style tworzą rodzinę RIBBI (Regular, Italic, Bold, Bold Italic): nameID 1 to zawsze
„Ave Text”, nameID 2 to nazwa stylu, a fsSelection/macStyle mówią systemom, który plik
jest pogrubieniem, a który kursywą tej samej rodziny.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.roundTools import otRound

from ave_core.fontio import gasp_smooth_all, hint_ttf, to_tt_glyph, write_woff2
from ave_core.meta import COPYRIGHT, LICENSE, MANUFACTURER, OWNER, RELEASE_EPOCH, VENDOR

from . import glyphs  # noqa: F401  (rejestruje glify)
from .glyphs.registry import REGISTRY, TextGlyph, side_value
from .shapes import Shape, slanted
from .style import ASCENT, CAP, DESCENT, UPM, XH, Style

FAMILY = "Ave Text"
VERSION = "0.100"


@dataclass
class BuiltGlyph:
    name: str
    shape: Shape
    advance: int
    lsb: float
    rsb: float


def place(spec: TextGlyph, s: Style) -> BuiltGlyph:
    with slanted(s.slant if s.italic else 0.0):
        return _place(spec, s)


def _place(spec: TextGlyph, s: Style) -> BuiltGlyph:
    shape = spec.build(s)
    if spec.advance is not None:
        if s.italic and shape.area:
            shape = shape.sheared(s.slant, XH / 2)
        return BuiltGlyph(spec.name, shape, otRound(spec.advance(s)), 0, 0)
    base = REGISTRY[spec.spacing_from] if spec.spacing_from else spec
    reference = base.build(s) if spec.spacing_from else shape
    xmin, _, xmax, _ = reference.bounds
    lsb, rsb = side_value(s, base.left), side_value(s, base.right)
    placed = shape.moved(lsb - xmin)
    if s.italic:
        placed = placed.sheared(s.slant, XH / 2)
    return BuiltGlyph(spec.name, placed, otRound(lsb + (xmax - xmin) + rsb), lsb, rsb)


def build_glyphs(s: Style) -> list[BuiltGlyph]:
    return [place(spec, s) for spec in REGISTRY.values()]


def cmap() -> dict[int, str]:
    out: dict[int, str] = {}
    for name, spec in REGISTRY.items():
        for code in spec.unicodes:
            if code in out:
                raise ValueError(f"U+{code:04X} przypisany do {out[code]} i {name}")
            out[code] = name
    return out


def ps_name(family: str, s: Style) -> str:
    return f"{family.replace(' ', '')}-{s.ps_style}"


def build_font(s: Style, out_dir: Path, family: str = FAMILY, features: str | None = None,
               hint: bool = False) -> tuple[Path, Path]:
    os.environ.setdefault("SOURCE_DATE_EPOCH", str(RELEASE_EPOCH))
    out_dir.mkdir(parents=True, exist_ok=True)
    built = build_glyphs(s)
    if features is None:
        from .features import feature_file

        features = feature_file(s, built)
    order = [g.name for g in built]
    bold = s.weight >= 600

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap())
    fb.setupGlyf({g.name: to_tt_glyph(g.shape) for g in built})

    glyf = fb.font["glyf"]
    metrics = {}
    y_min, y_max = 0, 0
    for g in built:
        tt = glyf[g.name]
        tt.recalcBounds(glyf)
        if tt.numberOfContours:
            metrics[g.name] = (g.advance, tt.xMin)
            y_min, y_max = min(y_min, tt.yMin), max(y_max, tt.yMax)
        else:
            metrics[g.name] = (g.advance, 0)
    fb.setupHorizontalMetrics(metrics)

    fb.setupHorizontalHeader(
        ascent=ASCENT, descent=DESCENT, lineGap=0,
        caretSlopeRise=UPM if s.italic else 1, caretSlopeRun=otRound(UPM * s.slant) if s.italic else 0,
    )
    ps = ps_name(family, s)
    fb.setupNameTable(
        {
            "copyright": COPYRIGHT,
            "familyName": family,
            "styleName": s.name,
            "uniqueFontIdentifier": f"{VERSION};{VENDOR};{ps}",
            "fullName": f"{family} {s.name}" if s.name != "Regular" else f"{family} Regular",
            "version": f"Version {VERSION}",
            "psName": ps,
            "manufacturer": MANUFACTURER,
            "designer": OWNER,
            "description": "Krój do akapitów w parze z Ave Display.",
            "licenseDescription": LICENSE,
        },
        mac=False,
    )
    fs_selection = (1 << 7)  # USE_TYPO_METRICS
    if s.italic:
        fs_selection |= 1 << 0
    if bold:
        fs_selection |= 1 << 5
    if not s.italic and not bold:
        fs_selection |= 1 << 6
    fb.setupOS2(
        version=4,
        usWeightClass=s.weight,
        usWidthClass=5,
        fsType=0,
        fsSelection=fs_selection,
        achVendID=VENDOR,
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=max(ASCENT, y_max),
        usWinDescent=max(-DESCENT, -y_min),
        sxHeight=XH,
        sCapHeight=CAP,
        usDefaultChar=0,
        usBreakChar=32,
        usMaxContext=2,
        ulCodePageRange1=(1 << 0) | (1 << 1),
    )
    fb.setupPost(italicAngle=-s.slant_deg, underlinePosition=-120, underlineThickness=otRound(s.hair * 0.8))
    if features:
        fb.addOpenTypeFeatures(features)
    fb.font["gasp"] = gasp_smooth_all()
    fb.font["OS/2"].recalcUnicodeRanges(fb.font)
    fb.font["head"].fontRevision = float(VERSION)
    fb.font["head"].macStyle = (1 if bold else 0) | (2 if s.italic else 0)
    ttf_path = out_dir / f"{ps}.ttf"
    woff2_path = out_dir / f"{ps}.woff2"
    fb.save(str(ttf_path))
    if hint:
        hint_ttf(ttf_path)
    write_woff2(ttf_path, woff2_path)
    return ttf_path, woff2_path


def build_family(out_dir: Path, hint: bool = True) -> list[tuple[Path, Path]]:
    """Cztery style Ave Text (Regular, Italic, Bold, Bold Italic) do out_dir."""
    from .style import STYLES

    return [build_font(s, out_dir, hint=hint) for s in STYLES.values()]


__all__ = ["build_font", "build_family", "build_glyphs", "BuiltGlyph", "FAMILY"]
