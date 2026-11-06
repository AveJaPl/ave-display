"""Glify techniczne: .notdef i spacja."""

from ..geometry import Shape, rect
from ..params import CAP
from ..spacing import SB, SPACE_WIDTH
from .registry import glyph


@glyph(".notdef", "", SB.PUNCT, SB.PUNCT)
def notdef() -> Shape:
    return rect(0, 0, 560, CAP) - rect(80, 80, 480, CAP - 80)


@glyph("space", " ", advance=SPACE_WIDTH)
def space() -> Shape:
    return Shape()
