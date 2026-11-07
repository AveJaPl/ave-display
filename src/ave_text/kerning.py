"""Kerning Ave Text: klasy kształtów, wartości z profili glifów i ochrona przed kolizjami.

Metoda (pole białej przestrzeni z ograniczeniem głębokości, jak w HT Letterspacer):
dla pary liczymy w każdym wierszu (co ROW j.) poziomy odstęp między obrysami, obcinamy go do
DEPTH i sumujemy w strefie pary (wysokość x, wersaliki albo zakres znaku interpunkcyjnego).
Kerning dobieramy tak, żeby ta suma była równa sumie dla pary wzorcowej, w której litery zastąpiono
literami o prostych bokach (H dla wersalików i cyfr, n dla małych). Kerujemy tylko kuratorowaną
listę par klas (standardowa praktyka łacińska), bo litery z otwartym bokiem (r, f, t, c) mają
odstępy ustawione celowo i metoda pola zawęziłaby je za bardzo.

Każda para członków klas przechodzi kontrolę kolizji (akcenty, ogonki): jeśli wartość klasowa
zbliżyłaby glify bardziej niż MIN_GAP, para dostaje własny, łagodniejszy wyjątek. Osobny skan
wszystkich par liter i interpunkcji dodaje dodatni kerning tam, gdzie glify by się stykały (np. f’).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pathops

from .builder import BuiltGlyph
from .glyphs.registry import REGISTRY
from .style import CAP, XH, Style

ROW = 10
DEPTH = 250
CONE = 1.3
REACH = 400
MAX_KERN = 160
MIN_GAP = 36
MIN_GAP_PUNCT = 26
SCALE = 0.85
THRESHOLD = 10
ALL_ROWS = range(-250, 960, ROW)


@dataclass
class Profile:
    advance: float
    rows: dict[int, tuple[float, float]]
    zone: tuple[float, float]
    cache: dict = field(default_factory=dict)


def _extent(path: pathops.Path, y: float) -> tuple[float, float] | None:
    band = pathops.Path()
    pen = band.getPen()
    pen.moveTo((-5000, y - ROW / 2))
    pen.lineTo((5000, y - ROW / 2))
    pen.lineTo((5000, y + ROW / 2))
    pen.lineTo((-5000, y + ROW / 2))
    pen.closePath()
    hit = pathops.op(path, band, pathops.PathOp.INTERSECTION)
    if hit.area <= 0.5:
        return None
    x0, _, x1, _ = hit.bounds
    return x0, x1


LOWER_ZONE = (0.0, float(XH))
CAP_ZONE = (0.0, float(CAP))


def zone_of(name: str, path: pathops.Path) -> tuple[float, float]:
    base = REGISTRY[name].spacing_from or name
    if len(base) == 1 and base.isalpha():
        return LOWER_ZONE if base.islower() else CAP_ZONE
    if base in LOWER_NAMES:
        return LOWER_ZONE
    if base in CAP_NAMES or base.endswith(".tf") or base in DIGITS:
        return CAP_ZONE
    _, y0, _, y1 = path.bounds
    return (max(y0, -250.0), min(y1, 950.0))


DIGITS = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
LOWER_NAMES = {"ae", "oe", "oslash", "eth", "thorn", "germandbls", "dotlessi", "mu", "florin"}
CAP_NAMES = {"AE", "OE", "Oslash", "Thorn"}


def profiles(built: list[BuiltGlyph], names: set[str]) -> dict[str, Profile]:
    out = {}
    for g in built:
        if g.name not in names:
            continue
        path = g.shape.path
        rows = {}
        for y in ALL_ROWS:
            e = _extent(path, y)
            if e:
                rows[y] = e
        out[g.name] = Profile(g.advance, rows, zone_of(g.name, path))
    return out


def cone_right(p: Profile, y: int) -> float | None:
    """Optyczna prawa krawędź w wierszu y: tusz z innych wierszy też się liczy, ale słabnie
    o CONE j. na każdą jednostkę odległości w pionie (przewieszenia jak brzuszek P nad kropką)."""
    key = ("R", y)
    if key not in p.cache:
        best = None
        for yy, (_, x1) in p.rows.items():
            dy = abs(yy - y)
            if dy <= REACH:
                v = x1 - CONE * dy
                best = v if best is None or v > best else best
        p.cache[key] = best
    return p.cache[key]


def cone_left(p: Profile, y: int) -> float | None:
    key = ("L", y)
    if key not in p.cache:
        best = None
        for yy, (x0, _) in p.rows.items():
            dy = abs(yy - y)
            if dy <= REACH:
                v = x0 + CONE * dy
                best = v if best is None or v < best else best
        p.cache[key] = best
    return p.cache[key]


def gap_rows(left: Profile, right: Profile, rows) -> list[float | None]:
    out = []
    for y in rows:
        a, b = cone_right(left, y), cone_left(right, y)
        out.append(left.advance - a + b if a is not None and b is not None else None)
    return out


def raw_gaps(left: Profile, right: Profile, rows) -> list[float]:
    out = []
    for y in rows:
        a, b = left.rows.get(y), right.rows.get(y)
        if a and b:
            out.append(left.advance - a[1] + b[0])
    return out


def area(left: Profile, right: Profile, rows, kern: float = 0.0) -> float:
    return sum(DEPTH if g is None else min(max(g + kern, 0.0), DEPTH) for g in gap_rows(left, right, rows))


def closest(left: Profile, right: Profile, kern: float = 0.0) -> float:
    gaps = raw_gaps(left, right, ALL_ROWS)
    return min(gaps) + kern if gaps else float("inf")


def pair_rows(left: Profile, right: Profile) -> list[int]:
    lo = max(left.zone[0], right.zone[0])
    hi = min(left.zone[1], right.zone[1])
    if hi - lo < ROW * 3:
        lo, hi = min(left.zone[0], right.zone[0]), max(left.zone[1], right.zone[1])
    return [y for y in ALL_ROWS if lo + ROW / 2 <= y <= hi - ROW / 2]


def stand_in(name: str, prof: dict[str, Profile]) -> str:
    zone = prof[name].zone
    if zone == LOWER_ZONE:
        return "n"
    if zone == CAP_ZONE:
        return "H"
    return name


def suggest(left: str, right: str, prof: dict[str, Profile]) -> int:
    rows = pair_rows(prof[left], prof[right])
    target = area(prof[stand_in(left, prof)], prof[stand_in(right, prof)], rows)
    best = 0
    for k in range(0, -400, -2):
        if area(prof[left], prof[right], rows, k) <= target:
            best = k
            break
    else:
        best = -400
    return int(round(max(best * SCALE, -MAX_KERN) / 5.0) * 5)


def min_gap(left: str, right: str) -> float:
    punct = not (left[:1].isalpha() and right[:1].isalpha()) or left in PUNCT or right in PUNCT
    return MIN_GAP_PUNCT if punct else MIN_GAP


PUNCT = {"period", "comma", "ellipsis", "quoteright", "quotedblright", "quotesingle", "quotedbl", "quoteleft",
         "quotedblleft", "quotesinglbase", "quotedblbase", "hyphen", "endash", "emdash", "colon", "semicolon",
         "guilsinglleft", "guilsinglright", "guillemotleft", "guillemotright", "parenright", "bracketright",
         "braceright", "question", "exclam"}


def safe(value: int, left: str, right: str, prof: dict[str, Profile]) -> int:
    """Najbardziej ujemna wartość ≤ value (bliżej zera), przy której glify się nie zbliżą poniżej progu."""
    limit = min_gap(left, right)
    near = closest(prof[left], prof[right])
    if near + value >= limit:
        return value
    return min(0, int((limit - near) // 5 * 5 + 5)) if near < float("inf") else value


# --- klasy --------------------------------------------------------------------------------------

def members(*bases: str) -> list[str]:
    """Glify bazowe i wszystkie litery z akcentami zbudowane na nich."""
    out = []
    for base in bases:
        if base in REGISTRY and base not in out:
            out.append(base)
        for name, spec in REGISTRY.items():
            if spec.spacing_from == base and name not in out:
                out.append(name)
    return out


def _unique(classes: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: list(dict.fromkeys(n for n in names if n in REGISTRY)) for key, names in classes.items()}


def left_classes() -> dict[str, list[str]]:
    """Klasy po prawym boku glifu (glif stoi po lewej stronie pary)."""
    return _unique({
        "A": members("A"), "F": ["F"], "K": ["K", "X"], "L": members("L"), "P": ["P", "Thorn"],
        "R": members("R"), "T": members("T"), "V": ["V"], "W": ["W"], "Y": members("Y"),
        "O": members("O", "D", "Q") + ["Oslash"],
        "r": members("r"), "f": ["f"], "v": ["v"], "w": ["w"], "y": members("y"), "k": ["k", "x"],
        "o": members("o", "b", "p") + ["oslash", "thorn"],
        "period": ["period", "comma", "ellipsis"],
        "quote": ["quoteright", "quotedblright", "quotesingle", "quotedbl"],
        "base": ["quotesinglbase", "quotedblbase"],
        "hyphen": ["hyphen", "endash", "emdash"],
        "guil": ["guilsinglright", "guillemotright"],
        "quoteleft": ["quoteleft", "quotedblleft"],
    })


def right_classes() -> dict[str, list[str]]:
    """Klasy po lewym boku glifu (glif stoi po prawej stronie pary)."""
    return _unique({
        "A": members("A") + ["AE"], "O": members("O", "C", "G", "Q") + ["Oslash", "OE"], "J": ["J"],
        "T": members("T"), "V": ["V"], "W": ["W"], "Y": members("Y"), "X": ["X"],
        "a": members("a") + ["ae"],
        "o": members("o", "c", "d", "e", "g", "q") + ["oslash", "oe", "eth"],
        "n": members("n", "m", "p", "r", "u") + ["mu"],
        "v": members("v", "w", "y"), "x": ["x"], "z": members("z"), "s": members("s"),
        "period": ["period", "comma", "ellipsis"],
        "quote": ["quoteright", "quotedblright", "quotesingle", "quotedbl"],
        "hyphen": ["hyphen", "endash", "emdash"],
        "colon": ["colon", "semicolon"],
        "guil": ["guilsinglleft", "guillemotleft"],
    })


PAIRS: list[tuple[str, str]] = [
    # wersaliki z wersalikami
    ("A", "T"), ("A", "V"), ("A", "W"), ("A", "Y"), ("A", "O"), ("A", "quote"),
    ("L", "T"), ("L", "V"), ("L", "W"), ("L", "Y"), ("L", "O"), ("L", "quote"),
    ("F", "A"), ("P", "A"), ("T", "A"), ("V", "A"), ("W", "A"), ("Y", "A"),
    ("F", "J"), ("P", "J"), ("T", "J"), ("V", "J"), ("W", "J"), ("Y", "J"),
    ("T", "O"), ("V", "O"), ("W", "O"), ("Y", "O"), ("O", "T"), ("O", "V"), ("O", "W"), ("O", "Y"),
    ("O", "A"), ("O", "X"), ("K", "O"), ("R", "O"), ("R", "T"), ("R", "V"), ("R", "W"), ("R", "Y"),
    # wersalik + mała
    ("T", "a"), ("T", "o"), ("T", "n"), ("T", "v"), ("T", "x"), ("T", "z"), ("T", "s"),
    ("V", "a"), ("V", "o"), ("V", "n"), ("V", "s"), ("W", "a"), ("W", "o"), ("W", "n"), ("W", "s"),
    ("Y", "a"), ("Y", "o"), ("Y", "n"), ("Y", "s"), ("Y", "v"), ("F", "a"), ("F", "o"), ("P", "a"), ("P", "o"),
    ("K", "o"), ("K", "v"), ("A", "v"), ("L", "v"),
    # małe z małymi
    ("r", "period"), ("v", "period"), ("w", "period"), ("y", "period"), ("f", "period"),
    ("v", "o"), ("w", "o"), ("y", "o"), ("o", "v"), ("o", "x"), ("k", "o"), ("r", "a"), ("r", "o"),
    # interpunkcja
    ("period", "quote"), ("quote", "A"), ("quoteleft", "A"), ("base", "T"), ("base", "V"), ("base", "W"), ("base", "Y"),
    ("T", "period"), ("V", "period"), ("W", "period"), ("Y", "period"), ("F", "period"), ("P", "period"),
    ("T", "hyphen"), ("V", "hyphen"), ("W", "hyphen"), ("Y", "hyphen"),
    ("hyphen", "T"), ("hyphen", "V"), ("hyphen", "W"), ("hyphen", "Y"),
    ("T", "guil"), ("V", "guil"), ("Y", "guil"),
    ("guil", "T"), ("guil", "V"), ("guil", "Y"),
]

# Zestaw do skanu kolizji: litery, cyfry i interpunkcja, które stoją obok liter.
COLLISION_LEFT = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["quoteright", "parenleft", "bracketleft"]
COLLISION_RIGHT = [chr(c) for c in range(ord("a"), ord("z") + 1)] + [
    "quoteright", "quotedblright", "quotesingle", "quotedbl", "parenright", "bracketright", "braceright",
    "question", "exclam", "asterisk"]


def kerning(built: list[BuiltGlyph]) -> tuple[dict[str, list[str]], dict[str, list[str]], dict, dict]:
    """Zwraca (klasy lewe, klasy prawe, pary klas {(L, R): v}, wyjątki {(lewy glif, prawy glif): v})."""
    lefts, rights = left_classes(), right_classes()
    names = {n for cls in lefts.values() for n in cls} | {n for cls in rights.values() for n in cls}
    names |= {"H", "n"} | set(COLLISION_LEFT) | set(COLLISION_RIGHT)
    names &= {g.name for g in built}
    prof = profiles(built, names)

    class_pairs: dict[tuple[str, str], int] = {}
    exceptions: dict[tuple[str, str], int] = {}
    for lc, rc in PAIRS:
        lm = [n for n in lefts[lc] if n in prof]
        rm = [n for n in rights[rc] if n in prof]
        if not lm or not rm:
            continue
        value = suggest(lm[0], rm[0], prof)
        value = safe(value, lm[0], rm[0], prof)
        if abs(value) < THRESHOLD:
            continue
        class_pairs[(lc, rc)] = value
        for a in lm:
            for b in rm:
                ok = safe(value, a, b, prof)
                if ok != value:
                    exceptions[(a, b)] = ok

    in_class = {}
    for (lc, rc), value in class_pairs.items():
        for a in lefts[lc]:
            for b in rights[rc]:
                in_class[(a, b)] = exceptions.get((a, b), value)

    for a in COLLISION_LEFT:
        for b in COLLISION_RIGHT:
            if a not in prof or b not in prof:
                continue
            current = in_class.get((a, b), 0)
            near = closest(prof[a], prof[b], current)
            limit = min_gap(a, b) * 0.6
            if near < limit:
                exceptions[(a, b)] = current + int((limit - near) // 5 * 5 + 5)
    return lefts, rights, class_pairs, exceptions


def kern_feature(built: list[BuiltGlyph]) -> str:
    lefts, rights, class_pairs, exceptions = kerning(built)
    used_l = sorted({lc for lc, _ in class_pairs})
    used_r = sorted({rc for _, rc in class_pairs})
    lines = []
    for lc in used_l:
        lines.append(f"@kL_{lc} = [{' '.join(lefts[lc])}];")
    for rc in used_r:
        lines.append(f"@kR_{rc} = [{' '.join(rights[rc])}];")
    lines.append("feature kern {")
    for (a, b), value in sorted(exceptions.items()):
        lines.append(f"    pos {a} {b} {value};")
    for (lc, rc), value in sorted(class_pairs.items()):
        lines.append(f"    pos @kL_{lc} @kR_{rc} {value};")
    lines.append("} kern;")
    return "\n".join(lines)


def report(built: list[BuiltGlyph]) -> str:
    _, _, class_pairs, exceptions = kerning(built)
    out = [f"pary klas: {len(class_pairs)}, wyjątki: {len(exceptions)}"]
    out += [f"  {lc}/{rc}: {v}" for (lc, rc), v in sorted(class_pairs.items(), key=lambda kv: kv[1])]
    out += [f"  wyjątek {a}/{b}: {v}" for (a, b), v in sorted(exceptions.items())]
    return "\n".join(out)


__all__ = ["kern_feature", "kerning", "report", "Style"]
