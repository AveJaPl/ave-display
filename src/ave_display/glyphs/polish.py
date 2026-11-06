"""Polskie litery: kreska, kropka, ogonek i przekreślenie w kanciastym, pochylonym stylu."""

from ..geometry import Shape, band, polygon, rect
from ..params import BACKCUT, CAP, STEM
from . import letters
from .registry import REGISTRY, glyph

ACCENT_LO = CAP + 66
ACCENT_HEIGHT = 165
ACUTE_SLOPE = 0.32
ACUTE_WIDTH = 192
ACUTE_SHIFT = 30
DOT_WIDTH = 200
DOT_HEIGHT = 160

OGONEK_STEM = 130
OGONEK_FOOT = 300
OGONEK_FOOT_HEIGHT = 100
OGONEK_DEPTH = 185

LSLASH_LEFT, LSLASH_RIGHT = -70, STEM + 146
LSLASH_Y, LSLASH_RISE, LSLASH_THICK = 250, 150, 130


def _center(base: str) -> float:
    x0, _, x1, _ = REGISTRY[base].build().bounds
    return (x0 + x1) / 2


def acute(cx: float) -> Shape:
    """Kreska: równoległobok wznoszący się w prawo, z poziomymi cięciami jak belki."""
    cx += ACUTE_SHIFT
    rise = ACUTE_SLOPE * ACCENT_HEIGHT
    x0 = cx - ACUTE_WIDTH / 2 - rise / 2
    return band(x0, ACCENT_LO, x0 + rise, ACCENT_LO + ACCENT_HEIGHT, ACUTE_WIDTH)


def dot(cx: float) -> Shape:
    return rect(cx - DOT_WIDTH / 2, ACCENT_LO, cx + DOT_WIDTH / 2, ACCENT_LO + DOT_HEIGHT)


def ogonek(x: float) -> Shape:
    """Ogonek: kanciasty hak spod litery; stopka w prawo, ścięta skosem jak belka R."""
    foot_top = OGONEK_FOOT_HEIGHT - OGONEK_DEPTH
    return polygon([
        (x, 1), (x + OGONEK_STEM, 1), (x + OGONEK_STEM, foot_top),
        (x + OGONEK_FOOT - BACKCUT * OGONEK_FOOT_HEIGHT, foot_top), (x + OGONEK_FOOT, -OGONEK_DEPTH),
        (x, -OGONEK_DEPTH),
    ])


def stroke_through_stem() -> Shape:
    """Przekreślenie Ł: belka przecinająca trzon, wznosząca się w prawo, cięta pionowo."""
    y0, y1 = LSLASH_Y, LSLASH_Y + LSLASH_RISE
    return polygon([
        (LSLASH_LEFT, y0), (LSLASH_RIGHT, y1), (LSLASH_RIGHT, y1 + LSLASH_THICK),
        (LSLASH_LEFT, y0 + LSLASH_THICK),
    ])


@glyph("Aogonek", "Ą", also="ą", spacing_from="A")
def Aogonek() -> Shape:
    return letters.A() | ogonek(letters.A_WIDTH - STEM + 14)


@glyph("Cacute", "Ć", also="ć", spacing_from="C")
def Cacute() -> Shape:
    return letters.C() | acute(_center("C"))


@glyph("Eogonek", "Ę", also="ę", spacing_from="E")
def Eogonek() -> Shape:
    return letters.E() | ogonek(letters.E_WIDTH - OGONEK_FOOT - 20)


@glyph("Lslash", "Ł", also="ł", spacing_from="L")
def Lslash() -> Shape:
    return letters.L() | stroke_through_stem()


@glyph("Nacute", "Ń", also="ń", spacing_from="N")
def Nacute() -> Shape:
    return letters.N() | acute(_center("N"))


@glyph("Oacute", "Ó", also="ó", spacing_from="O")
def Oacute() -> Shape:
    return letters.O() | acute(_center("O"))


@glyph("Sacute", "Ś", also="ś", spacing_from="S")
def Sacute() -> Shape:
    return letters.S() | acute(_center("S"))


@glyph("Zacute", "Ź", also="ź", spacing_from="Z")
def Zacute() -> Shape:
    return letters.Z() | acute(_center("Z"))


@glyph("Zdotaccent", "Ż", also="ż", spacing_from="Z")
def Zdotaccent() -> Shape:
    return letters.Z() | dot(_center("Z"))
