#!/usr/bin/env python3
"""Testy zbudowanego fontu Ave Display.

Użycie:  .venv/bin/python scripts/verify.py [dist/AveDisplay-Regular.ttf]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pathops
from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SVG_R = ROOT / "reference" / "R-z-monogramu.svg"

UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "ĄĆĘŁŃÓŚŹŻ"
DIGITS = "0123456789"
PUNCT = " .,:;-–/!?%+&'\"()#@*·×°"
REQUIRED = UPPER + UPPER.lower() + DIGITS + PUNCT
EMPTY_OK = {" ", " "}

MIN_KERN_GAP = 20
R_IOU_MIN = 0.98


class Report:
    def __init__(self):
        self.failures: list[str] = []

    def check(self, ok: bool, label: str, detail: str = "") -> None:
        mark = "OK  " if ok else "BŁĄD"
        print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
        if not ok:
            self.failures.append(label)


def glyph_path(glyphset, name: str) -> pathops.Path:
    path = pathops.Path()
    glyphset[name].draw(path.getPen())
    return path


def signed_area(glyphset, name: str) -> float:
    pen = AreaPen(glyphset)
    glyphset[name].draw(pen)
    return pen.value


def profile(path: pathops.Path, y: float) -> tuple[float, float] | None:
    band = pathops.Path()
    pen = band.getPen()
    pen.moveTo((-10000, y - 1))
    pen.lineTo((10000, y - 1))
    pen.lineTo((10000, y + 1))
    pen.lineTo((-10000, y + 1))
    pen.closePath()
    hit = pathops.op(path, band, pathops.PathOp.INTERSECTION)
    if hit.area <= 0:
        return None
    x0, _, x1, _ = hit.bounds
    return x0, x1


def kerning_pairs(font: TTFont) -> dict[tuple[str, str], int]:
    pairs: dict[tuple[str, str], int] = {}
    if "GPOS" not in font:
        return pairs
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if sub.Format != 1:
                continue
            for first, pairset in zip(sub.Coverage.glyphs, sub.PairSet):
                for rec in pairset.PairValueRecord:
                    pairs[(first, rec.SecondGlyph)] = rec.Value1.XAdvance
    return pairs


def svg_r_path(scale_to: float) -> pathops.Path:
    svg = SVG_R.read_text()
    view = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    height = view[3]
    s = scale_to / height
    points = [(float(x), float(y)) for x, y in re.findall(r"([\d.]+) ([\d.]+)", re.search(r' d="([^"]+)"', svg).group(1))]
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo((points[0][0] * s, (height - points[0][1]) * s))
    for x, y in points[1:]:
        pen.lineTo((x * s, (height - y) * s))
    pen.closePath()
    path.simplify(fix_winding=True)
    return path


def run(ttf_path: Path, woff2_path: Path | None = None) -> bool:
    report = Report()
    font = TTFont(str(ttf_path))
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    order = font.getGlyphOrder()
    hmtx = font["hmtx"]

    print(f"Weryfikacja {ttf_path.name}: {len(order)} glifów, {len(cmap)} znaków w cmap")

    missing = [c for c in REQUIRED if ord(c) not in cmap]
    report.check(not missing, "każdy wymagany znak ma glif w cmap",
                 "brak: " + " ".join(f"U+{ord(c):04X}" for c in missing) if missing else f"{len(REQUIRED)} znaków")

    mismatched = [c for c in UPPER if cmap.get(ord(c.lower())) != cmap.get(ord(c))]
    report.check(not mismatched, "małe litery wskazują na glify wersalików",
                 " ".join(mismatched) if mismatched else "")

    report.check(order[0] == ".notdef" and font["glyf"][".notdef"].numberOfContours > 0,
                 ".notdef jest pierwszym glifem i ma kontur")

    empty = []
    for ch in REQUIRED:
        name = cmap.get(ord(ch))
        if name is None or ch in EMPTY_OK:
            continue
        glyph = font["glyf"][name]
        if glyph.numberOfContours <= 0 or abs(signed_area(glyphset, name)) < 1000:
            empty.append(ch)
    report.check(not empty, "brak pustych konturów (poza spacją)", " ".join(empty))

    space = cmap.get(ord(" "))
    report.check(space is not None and font["glyf"][space].numberOfContours == 0 and hmtx[space][0] > 0,
                 "spacja jest pusta i ma szerokość", f"{hmtx[space][0] if space else '-'} j.")

    wrong_dir, overlaps = [], []
    for name in order:
        if font["glyf"][name].numberOfContours <= 0:
            continue
        area = signed_area(glyphset, name)
        if area >= 0:
            wrong_dir.append(name)
        merged = glyph_path(glyphset, name)
        merged.simplify(fix_winding=True)
        if abs(abs(area) - abs(merged.area)) > 2.0:
            overlaps.append(name)
    report.check(not wrong_dir, "kierunek konturów zgodny z TrueType (zewnętrzne zgodnie ze wskazówkami)",
                 " ".join(wrong_dir))
    report.check(not overlaps, "brak nakładających się konturów", " ".join(overlaps))

    os2, head = font["OS/2"], font["head"]
    report.check(os2.usWinAscent >= head.yMax and os2.usWinDescent >= -head.yMin,
                 "usWinAscent/usWinDescent obejmują wszystkie glify",
                 f"yMin={head.yMin}, yMax={head.yMax}, win={os2.usWinAscent}/{os2.usWinDescent}")
    report.check(all(hmtx[n][0] > 0 for n in order), "każdy glif ma dodatnią szerokość")
    report.check(os2.sCapHeight == 700 and font["head"].unitsPerEm == 1000, "UPM 1000, wersaliki 700")

    pairs = kerning_pairs(font)
    report.check(len(pairs) > 0, "kerning (GPOS kern) obecny", f"{len(pairs)} par glifów")
    paths = {n: glyph_path(glyphset, n) for n in {a for a, _ in pairs} | {b for _, b in pairs}}
    collisions = []
    for (a, b), value in sorted(pairs.items()):
        shift = hmtx[a][0] + value
        closest = float("inf")
        for y in range(-240, 960, 10):
            pa, pb = profile(paths[a], y), profile(paths[b], y)
            if pa and pb:
                closest = min(closest, shift + pb[0] - pa[1])
        if closest < MIN_KERN_GAP:
            collisions.append(f"{a}/{b} ({closest:.0f})")
    report.check(not collisions, f"pary z kerningiem nie stykają się (odstęp ≥ {MIN_KERN_GAP} j.)",
                 ", ".join(collisions[:12]))

    r_name = cmap[ord("R")]
    glyph_r = glyph_path(glyphset, r_name)
    reference = svg_r_path(700)
    gx0, gy0, _, _ = glyph_r.bounds
    rx0, ry0, _, _ = reference.bounds

    def overlap(dx: float, dy: float) -> float:
        aligned = reference.transform(1, 0, 0, 1, gx0 - rx0 + dx, gy0 - ry0 + dy)
        inter = pathops.op(glyph_r, aligned, pathops.PathOp.INTERSECTION).area
        return inter / pathops.op(glyph_r, aligned, pathops.PathOp.UNION).area

    iou, dx, dy = max((overlap(dx, dy), dx, dy) for dx in range(-12, 13, 2) for dy in range(-4, 5, 2))
    report.check(iou >= R_IOU_MIN, "litera R pokrywa się z R-z-monogramu.svg",
                 f"IoU = {iou:.3f} przy przesunięciu ({dx}, {dy}) j. (próg {R_IOU_MIN})")

    if woff2_path is not None:
        web = TTFont(str(woff2_path))
        report.check(web.flavor == "woff2" and web.getGlyphOrder() == order and web.getBestCmap() == cmap,
                     "WOFF2 ma te same glify i cmap co TTF", f"{woff2_path.stat().st_size} B")

    if report.failures:
        print(f"Wynik: {len(report.failures)} błędów.")
        return False
    print("Wynik: wszystkie testy przeszły.")
    return True


if __name__ == "__main__":
    ttf = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "AveDisplay-Regular.ttf"
    woff2 = ttf.with_suffix(".woff2")
    sys.exit(0 if run(ttf, woff2 if woff2.exists() else None) else 1)
