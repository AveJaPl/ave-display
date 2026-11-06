"""Składanie fontu: kształty → pochylenie → kontury TrueType → TTF i WOFF2."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.roundTools import otRound
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.roundingPen import RoundingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

from . import glyphs
from .geometry import Shape
from .glyphs.registry import REGISTRY, GlyphSpec
from .params import ASCENT, CAP, DESCENT, SHEAR_ORIGIN_Y, SLANT, SLANT_DEG, UPM
from .spacing import kerning_pairs

FAMILY = "Ave Display"
STYLE = "Regular"
PS_NAME = "AveDisplay-Regular"
VERSION = "1.000"
RELEASE_EPOCH = 1793923200
OWNER = "Filip Piątek"
COPYRIGHT = f"Copyright (c) 2026 {OWNER} (AveJa). Wszelkie prawa zastrzeżone."
LICENSE = (
    "Font jest własnością Filipa Piątka. Wszelkie prawa zastrzeżone. "
    "Kopiowanie, rozpowszechnianie i modyfikowanie bez pisemnej zgody właściciela jest zabronione."
)

EXTRA_CMAP = {0x00A0: "space"}


@dataclass
class BuiltGlyph:
    name: str
    shape: Shape
    advance: int


def _final_shape(spec: GlyphSpec, cache: dict[str, Shape]) -> tuple[Shape, int]:
    shape = cache.setdefault(spec.name, spec.build())
    if spec.advance is not None:
        return shape, int(spec.advance)

    base = REGISTRY[spec.spacing_from] if spec.spacing_from else spec
    reference = cache.setdefault(base.name, base.build())
    xmin, _, xmax, _ = reference.bounds
    if base.left_edge is not None:
        xmin = base.left_edge
    advance = otRound(base.lsb + (xmax - xmin) + base.rsb)
    placed = shape.moved(base.lsb - xmin).sheared(SLANT, SHEAR_ORIGIN_Y)
    return placed, advance


def build_glyphs() -> list[BuiltGlyph]:
    cache: dict[str, Shape] = {}
    return [BuiltGlyph(name, *_final_shape(spec, cache)) for name, spec in REGISTRY.items()]


def _to_tt_glyph(shape: Shape):
    pen = TTGlyphPen(None)
    shape.draw(Cu2QuPen(RoundingPen(pen), max_err=0.4, reverse_direction=True))
    return pen.glyph()


def _cmap() -> dict[int, str]:
    cmap: dict[int, str] = {}
    for name, spec in REGISTRY.items():
        for code in spec.unicodes + spec.extra_unicodes:
            if code in cmap:
                raise ValueError(f"U+{code:04X} przypisany do {cmap[code]} i {name}")
            cmap[code] = name
    cmap.update(EXTRA_CMAP)
    return cmap


def _kerning_feature() -> str:
    lines = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "", "feature kern {"]
    for (left, right), value in sorted(kerning_pairs().items()):
        if left in REGISTRY and right in REGISTRY:
            lines.append(f"    pos {left} {right} {value};")
    lines.append("} kern;")
    return "\n".join(lines) + "\n"


def build_font(out_dir: Path) -> tuple[Path, Path]:
    os.environ.setdefault("SOURCE_DATE_EPOCH", str(RELEASE_EPOCH))
    out_dir.mkdir(parents=True, exist_ok=True)
    built = build_glyphs()
    order = [g.name for g in built]

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(_cmap())
    fb.setupGlyf({g.name: _to_tt_glyph(g.shape) for g in built})

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
        caretSlopeRise=UPM, caretSlopeRun=otRound(UPM * SLANT),
    )
    fb.setupNameTable(
        {
            "copyright": COPYRIGHT,
            "familyName": FAMILY,
            "styleName": STYLE,
            "uniqueFontIdentifier": f"{VERSION};AVEJ;{PS_NAME}",
            "fullName": f"{FAMILY} {STYLE}",
            "version": f"Version {VERSION}",
            "psName": PS_NAME,
            "manufacturer": f"{OWNER} (AveJa)",
            "designer": OWNER,
            "description": "Wersalikowy krój wystawowy zbudowany na literze R z monogramu RR.",
            "licenseDescription": LICENSE,
        },
        mac=False,
    )
    fb.setupOS2(
        version=4,
        usWeightClass=400,
        usWidthClass=5,
        fsType=0,
        fsSelection=(1 << 6) | (1 << 7),
        achVendID="AVEJ",
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=max(ASCENT, y_max),
        usWinDescent=max(-DESCENT, -y_min),
        sxHeight=CAP,
        sCapHeight=CAP,
        usDefaultChar=0,
        usBreakChar=32,
        usMaxContext=2,
        ulCodePageRange1=(1 << 0) | (1 << 1),
    )
    fb.setupPost(italicAngle=-SLANT_DEG, underlinePosition=-130, underlineThickness=70)
    fb.addOpenTypeFeatures(_kerning_feature())

    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    fb.font["gasp"] = gasp

    fb.font["OS/2"].recalcUnicodeRanges(fb.font)
    fb.font["head"].fontRevision = float(VERSION)

    ttf_path = out_dir / f"{PS_NAME}.ttf"
    woff2_path = out_dir / f"{PS_NAME}.woff2"
    fb.save(str(ttf_path))

    web = TTFont(str(ttf_path))
    web.flavor = "woff2"
    web.save(str(woff2_path))
    return ttf_path, woff2_path


__all__ = ["build_font", "build_glyphs", "glyphs"]
