"""Parametry stylów Ave Text.

Metryki pionowe są wspólne dla całej rodziny (i zgodne z Ave Display: wersaliki 700 j.,
linia 950/-250). Grubości, szerokości, zaokrąglenia i odstępy zależą od stylu, dlatego
żyją w obiekcie `Style`, a glify są funkcjami `(Style) -> Shape`.

Wartości startowe pochodzą z pomiarów Sairy i Exo 2 przeskalowanych do wersalików 700 j.
(docs/superpowers/specs/2026-11-07-ave-text-design.md).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

UPM = 1000
CAP = 700
XH = 510
ASC = 740
DESC = -210
OVS = 10
ASCENT = 950
DESCENT = -250

FAR = 4000

# Kąt pochylenia Ave Display; ścięcia końcówek w wariancie „ostrze” biegną równolegle do jego trzonów.
DISPLAY_SLANT = math.tan(math.radians(28.0))


@dataclass(frozen=True)
class Style:
    name: str
    weight: int
    italic: bool = False
    slant_deg: float = 0.0

    stem: float = 84.0
    stem_cap: float = 88.0
    hair: float = 72.0
    hair_cap: float = 76.0
    bar: float = 68.0

    width: float = 1.0
    radius: float = 128.0
    radius_cap: float = 160.0
    tension: float = 0.62
    inner: float = 1.0
    join: float = 0.5

    # Wariant „C” wybrany 2026-11-07: końcówki cięte pod kątem pochylenia Ave Display (28°)
    # i większe narożniki prawy górny / lewy dolny (asym). A = cut 0, asym 1; B = tylko cut.
    cut: float = DISPLAY_SLANT
    asym: float = 1.3

    sb_stem: float = 80.0
    sb_round: float = 62.0
    sb_cap_stem: float = 92.0
    sb_cap_round: float = 70.0
    space: float = 230.0

    alternates: frozenset[str] = field(default_factory=frozenset)

    @property
    def slant(self) -> float:
        return math.tan(math.radians(self.slant_deg))

    @property
    def ps_style(self) -> str:
        return self.name.replace(" ", "")

    def w(self, value: float) -> float:
        """Szerokość zależna od stylu (Bold jest odrobinę szerszy)."""
        return value * self.width

    def variant(self, **changes) -> Style:
        return replace(self, **changes)


REGULAR = Style(name="Regular", weight=400)

# Bold: trzony jak w Exo 2/Sairze 700 (150-164 j.), poziome kreski 0,78 trzonu, litery szersze o 4%,
# żeby światła nie zarosły, i ciaśniejsze odstępy (grubsze kreski same zabierają światło).
BOLD = Style(
    name="Bold", weight=700,
    stem=152.0, stem_cap=162.0, hair=118.0, hair_cap=124.0, bar=100.0,
    width=1.045, radius=150.0, radius_cap=178.0,
    sb_stem=62.0, sb_round=44.0, sb_cap_stem=72.0, sb_cap_round=52.0, space=236.0,
)

# Kursywy: pochylenie 10° (między Exo 2 a Sairą) i własne formy liter jak w Exo 2:
# jednopiętrowe a oraz f z ogonkiem pod linią pisma.
ITALIC_ALTERNATES = frozenset({"a.single", "f.descender"})
ITALIC = REGULAR.variant(name="Italic", italic=True, slant_deg=10.0, alternates=ITALIC_ALTERNATES)
BOLD_ITALIC = BOLD.variant(name="Bold Italic", italic=True, slant_deg=10.0, alternates=ITALIC_ALTERNATES)

STYLES: dict[str, Style] = {"regular": REGULAR, "italic": ITALIC, "bold": BOLD, "bold-italic": BOLD_ITALIC}
