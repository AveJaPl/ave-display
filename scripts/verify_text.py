#!/usr/bin/env python3
"""Testy zbudowanej rodziny Ave Text (Regular, Italic, Bold, Bold Italic).

Użycie:  .venv/bin/python scripts/verify_text.py [katalog z plikami, domyślnie dist/]
"""

from __future__ import annotations

import sys
from pathlib import Path

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from verify import Report, glyph_path, profile, signed_area  # noqa: E402

FAMILY = "Ave Text"
STYLES = {
    "AveText-Regular": dict(name="Regular", weight=400, italic=False, bold=False, stem=84, stem_cap=88),
    "AveText-Italic": dict(name="Italic", weight=400, italic=True, bold=False, stem=84, stem_cap=88),
    "AveText-Bold": dict(name="Bold", weight=700, italic=False, bold=True, stem=152, stem_cap=162),
    "AveText-BoldItalic": dict(name="Bold Italic", weight=700, italic=True, bold=True, stem=152, stem_cap=162),
}
ASCENT, DESCENT, CAP, XH, UPM = 950, -250, 700, 510, 1000
MIN_KERN_GAP = 12
EMPTY_OK = {0x20, 0xA0}


def required_codepoints() -> set[int]:
    """Drukowalne znaki stron kodowych Windows-1250 i Windows-1252, twarda spacja i minus."""
    need = {0xA0, 0x2212}
    for enc in ("cp1252", "cp1250"):
        for b in range(0x20, 0x100):
            if b == 0x7F:
                continue
            try:
                need.add(ord(bytes([b]).decode(enc)))
            except UnicodeDecodeError:
                pass
    return need


def gpos_pairs(font: TTFont) -> dict[tuple[str, str], int]:
    """Spłaszczony kerning (formaty 1 i 2), z pierwszeństwem par glifów jak w HarfBuzz."""
    pairs: dict[tuple[str, str], int] = {}
    if "GPOS" not in font:
        return pairs
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if getattr(sub, "Format", None) == 1:
                for first, pairset in zip(sub.Coverage.glyphs, sub.PairSet):
                    for rec in pairset.PairValueRecord:
                        pairs.setdefault((first, rec.SecondGlyph), rec.Value1.XAdvance)
            elif getattr(sub, "Format", None) == 2:
                c1 = sub.ClassDef1.classDefs
                c2 = sub.ClassDef2.classDefs
                by2: dict[int, list[str]] = {}
                for g, k in c2.items():
                    by2.setdefault(k, []).append(g)
                for first in sub.Coverage.glyphs:
                    row = sub.Class1Record[c1.get(first, 0)]
                    for k2, rec in enumerate(row.Class2Record):
                        value = rec.Value1.XAdvance if rec.Value1 else 0
                        if not value or k2 == 0:
                            continue
                        for second in by2.get(k2, []):
                            pairs.setdefault((first, second), value)
    return pairs


class _Flat(BasePen):
    """Spłaszcza kontury do odcinków (krzywe próbkowane), żeby liczyć przecięcia z prostą."""

    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        self.current = self.start = None

    def _moveTo(self, pt):
        self.current = self.start = pt

    def _lineTo(self, pt):
        self.segments.append((self.current, pt))
        self.current = pt

    def _qCurveToOne(self, a, b):
        p0 = self.current
        for i in range(1, 17):
            t = i / 16
            mt = 1 - t
            self._lineTo((mt * mt * p0[0] + 2 * mt * t * a[0] + t * t * b[0],
                          mt * mt * p0[1] + 2 * mt * t * a[1] + t * t * b[1]))

    def _curveToOne(self, a, b, c):
        p0 = self.current
        for i in range(1, 17):
            t = i / 16
            mt = 1 - t
            self._lineTo((mt ** 3 * p0[0] + 3 * mt * mt * t * a[0] + 3 * mt * t * t * b[0] + t ** 3 * c[0],
                          mt ** 3 * p0[1] + 3 * mt * mt * t * a[1] + 3 * mt * t * t * b[1] + t ** 3 * c[1]))

    def _closePath(self):
        if self.current != self.start:
            self.segments.append((self.current, self.start))


def ink_runs(glyphset, name: str, y: float) -> list[tuple[float, float]]:
    """Odcinki tuszu na wysokości y (reguła niezerowego nawinięcia)."""
    pen = _Flat(glyphset)
    glyphset[name].draw(pen)
    hits = []
    for (x0, y0), (x1, y1) in pen.segments:
        if (y0 <= y < y1) or (y1 <= y < y0):
            hits.append((x0 + (y - y0) / (y1 - y0) * (x1 - x0), 1 if y1 > y0 else -1))
    hits.sort()
    runs, winding, start = [], 0, None
    for x, d in hits:
        new = winding + d
        if winding == 0 and new != 0:
            start = x
        elif winding != 0 and new == 0:
            runs.append((start, x))
        winding = new
    return runs


def check_style(path: Path, spec: dict, report: Report) -> TTFont:
    font = TTFont(str(path))
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    hmtx = font["hmtx"]
    glyf = font["glyf"]
    print(f"\n{path.name}: {len(order)} glifów, {len(cmap)} znaków w cmap")

    need = required_codepoints()
    missing = sorted(need - set(cmap))
    report.check(not missing, "pełne strony kodowe Windows-1250 i 1252",
                 "brak: " + " ".join(f"U+{c:04X}" for c in missing[:20]) if missing else f"{len(need)} znaków")
    report.check(order[0] == ".notdef" and glyf[".notdef"].numberOfContours > 0, ".notdef pierwszy i z konturem")

    empty = [f"U+{c:04X}" for c, n in cmap.items()
             if c not in EMPTY_OK and (glyf[n].numberOfContours == 0 or abs(signed_area(gs, n)) < 500)]
    report.check(not empty, "brak pustych glifów (poza spacjami)", " ".join(empty[:20]))
    report.check(all(hmtx[n][0] > 0 for n in order), "każdy glif ma dodatnią szerokość")

    wrong_dir, overlaps = [], []
    for name in order:
        g = glyf[name]
        if g.isComposite() or g.numberOfContours <= 0:
            continue
        area = signed_area(gs, name)
        if area >= 0:
            wrong_dir.append(name)
        merged = glyph_path(gs, name)
        merged.simplify(fix_winding=True)
        if abs(abs(area) - abs(merged.area)) > 2.0:
            overlaps.append(name)
    report.check(not wrong_dir, "kierunek konturów zgodny z TrueType", " ".join(wrong_dir[:12]))
    report.check(not overlaps, "brak nakładających się konturów", " ".join(overlaps[:12]))

    os2, head, hhea, post, name = font["OS/2"], font["head"], font["hhea"], font["post"], font["name"]
    report.check(head.unitsPerEm == UPM and os2.sCapHeight == CAP and os2.sxHeight == XH,
                 "UPM 1000, wersaliki 700, wysokość x 510 (jak Ave Display)")
    report.check(hhea.ascent == os2.sTypoAscender == ASCENT and hhea.descent == os2.sTypoDescender == DESCENT
                 and hhea.lineGap == os2.sTypoLineGap == 0 and bool(os2.fsSelection & (1 << 7)),
                 "metryki linii 950/-250 w hhea i OS/2, USE_TYPO_METRICS")
    report.check(head.yMax <= ASCENT and head.yMin >= DESCENT,
                 "wszystkie glify mieszczą się w linii 950/-250", f"yMin={head.yMin}, yMax={head.yMax}")
    report.check(os2.usWinAscent >= head.yMax and os2.usWinDescent >= -head.yMin,
                 "usWinAscent/usWinDescent obejmują glify", f"{os2.usWinAscent}/{os2.usWinDescent}")

    fam = name.getDebugName(1)
    sub = name.getDebugName(2)
    report.check(fam == FAMILY and sub == spec["name"], "nazwy rodziny i stylu (nameID 1/2)", f"{fam} / {sub}")
    bold_bit, italic_bit, regular_bit = bool(os2.fsSelection & 32), bool(os2.fsSelection & 1), bool(os2.fsSelection & 64)
    linked = (bold_bit == spec["bold"] and italic_bit == spec["italic"]
              and regular_bit == (not spec["bold"] and not spec["italic"])
              and bool(head.macStyle & 1) == spec["bold"] and bool(head.macStyle & 2) == spec["italic"]
              and os2.usWeightClass == spec["weight"])
    report.check(linked, "łączenie stylów: fsSelection, macStyle, usWeightClass",
                 f"fsSelection={os2.fsSelection:#06x}, macStyle={head.macStyle}, waga={os2.usWeightClass}")
    angle_ok = (post.italicAngle == -10.0 and hhea.caretSlopeRun > 0) if spec["italic"] else (post.italicAngle == 0)
    report.check(angle_ok, "kąt kursywy i nachylenie kursora", f"italicAngle={post.italicAngle}")

    # mierzymy poziomo: pochylenie kursywy nie zmienia poziomej szerokości trzonu
    n_runs = ink_runs(gs, cmap[ord("n")], XH * 0.45)
    h_runs = ink_runs(gs, cmap[ord("H")], CAP * 0.25)
    n_stem = n_runs[0][1] - n_runs[0][0] if n_runs else None
    h_stem = h_runs[0][1] - h_runs[0][0] if h_runs else None
    report.check(n_stem is not None and abs(n_stem - spec["stem"]) <= 3 and h_stem is not None
                 and abs(h_stem - spec["stem_cap"]) <= 3,
                 "grubość trzonów n i H zgodna z parametrami stylu",
                 f"n={n_stem and round(n_stem)} (cel {spec['stem']}), H={h_stem and round(h_stem)} (cel {spec['stem_cap']})")

    digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    tab = {hmtx[f"{d}.tf"][0] for d in digits if f"{d}.tf" in hmtx.metrics}
    gsub_ok = False
    if "GSUB" in font:
        for rec in font["GSUB"].table.FeatureList.FeatureRecord:
            if rec.FeatureTag == "tnum":
                gsub_ok = True
    report.check(len(tab) == 1 and gsub_ok, "cyfry tabelaryczne: równa szerokość i cecha tnum", f"szerokości {sorted(tab)}")

    pairs = gpos_pairs(font)
    report.check(len(pairs) > 200, "kerning (GPOS) obecny", f"{len(pairs)} par glifów po rozwinięciu klas")
    paths: dict[str, pathops.Path] = {}
    collisions = []
    for (a, b), value in pairs.items():
        if value >= 0:
            continue
        pa = paths.setdefault(a, glyph_path(gs, a))
        pb = paths.setdefault(b, glyph_path(gs, b))
        shift = hmtx[a][0] + value
        closest = float("inf")
        for y in range(-250, 950, 20):
            ea, eb = profile(pa, y), profile(pb, y)
            if ea and eb:
                closest = min(closest, shift + eb[0] - ea[1])
        if closest < MIN_KERN_GAP:
            collisions.append(f"{a}/{b} ({closest:.0f})")
    report.check(not collisions, f"pary z kerningiem nie stykają się (≥ {MIN_KERN_GAP} j.)", ", ".join(collisions[:10]))

    report.check("fpgm" in font and "prep" in font, "hinting (ttfautohint) obecny")
    woff2 = path.with_suffix(".woff2")
    if woff2.exists():
        web = TTFont(str(woff2))
        report.check(web.flavor == "woff2" and web.getGlyphOrder() == order and web.getBestCmap() == cmap,
                     "WOFF2 zgodny z TTF", f"{woff2.stat().st_size} B")
    else:
        report.check(False, "WOFF2 istnieje", str(woff2))
    return font


def run(directory: Path) -> bool:
    report = Report()
    fonts = {}
    for stem, spec in STYLES.items():
        path = directory / f"{stem}.ttf"
        if not path.exists():
            report.check(False, f"plik {path.name} istnieje")
            continue
        fonts[stem] = check_style(path, spec, report)

    if len(fonts) == len(STYLES):
        print("\nRodzina:")
        orders = {tuple(f.getGlyphOrder()) for f in fonts.values()}
        cmaps = {tuple(sorted(f.getBestCmap().items())) for f in fonts.values()}
        report.check(len(orders) == 1 and len(cmaps) == 1, "wszystkie style mają ten sam zestaw glifów i znaków")
        metrics = {(f["hhea"].ascent, f["hhea"].descent, f["OS/2"].usWinAscent, f["OS/2"].usWinDescent)
                   for f in fonts.values()}
        report.check(len(metrics) == 1, "jednakowe metryki pionowe (ta sama wysokość linii)", str(sorted(metrics)))
        reg, ita = fonts["AveText-Regular"], fonts["AveText-Italic"]
        a_reg = signed_area(reg.getGlyphSet(), "a")
        a_ita = signed_area(ita.getGlyphSet(), "a")
        report.check(abs(a_reg - a_ita) > 1000, "kursywa ma własne formy (jednopiętrowe a)")

    if report.failures:
        print(f"\nWynik: {len(report.failures)} błędów.")
        return False
    print("\nWynik: wszystkie testy przeszły.")
    return True


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
    sys.exit(0 if run(target) else 1)
