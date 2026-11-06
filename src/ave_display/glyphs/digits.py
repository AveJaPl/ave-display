"""Cyfry 0-9 zbudowane z tych samych elementów co litery."""

from ..geometry import Shape, clip_box, diagonal, polygon, rect, rounded
from ..params import (
    BACKCUT, BAR, BOWL, CAP, DIAG, FAR, MID_HI, MID_LO, R_MID_HI, R_MID_LO, RA, RB, STEM, rA, rB,
)
from ..spacing import SB
from .letters import ring
from .registry import glyph

ZERO_WIDTH = 780


@glyph("zero", "0", SB.ROUND, SB.ROUND)
def zero() -> Shape:
    return ring(ZERO_WIDTH)


ONE_FLAG = 130


@glyph("one", "1", 0, SB.STEM)
def one() -> Shape:
    x = ONE_FLAG + BACKCUT * BAR
    flag = polygon([(x - ONE_FLAG, CAP - BAR), (x + STEM, CAP - BAR), (x + STEM, CAP), (0, CAP)])
    return rect(x, 0, x + STEM, CAP) | flag


TWO_WIDTH = 800


@glyph("two", "2", SB.BAR, SB.BAR)
def two() -> Shape:
    w = TWO_WIDTH
    return rounded([
        (0, CAP), (w, CAP, RA), (w, MID_LO, RB), (STEM, MID_LO, rB), (STEM, BAR, rA),
        (w, BAR), (w, 0), (0, 0), (0, MID_HI, RB), (w - BOWL, MID_HI, rB),
        (w - BOWL, CAP - BAR, rA), (0, CAP - BAR),
    ])


THREE_WIDTH, THREE_TOP, THREE_MID_X = 800, 770, 190


@glyph("three", "3", SB.BAR, SB.ROUND)
def three() -> Shape:
    w, wt = THREE_WIDTH, THREE_TOP
    upper = rounded([(0, MID_LO), (wt, MID_LO, RB), (wt, CAP, RA), (0, CAP)])
    lower = rounded([(0, 0), (w, 0, RB), (w, MID_HI, RB), (0, MID_HI)])
    upper_counter = rounded([(-FAR, MID_HI), (wt - BOWL, MID_HI, rB), (wt - BOWL, CAP - BAR, rA), (-FAR, CAP - BAR)])
    lower_counter = rounded([(-FAR, BAR), (w - BOWL, BAR, rB), (w - BOWL, MID_LO, rA), (-FAR, MID_LO)])
    notch = rect(-FAR, MID_LO, THREE_MID_X, MID_HI)
    return (upper | lower) - upper_counter - lower_counter - notch


FOUR_WIDTH = 820


@glyph("four", "4", SB.STEM, SB.STEM)
def four() -> Shape:
    w = FOUR_WIDTH
    return rect(0, R_MID_LO, STEM, CAP) | rect(0, R_MID_LO, w, R_MID_HI) | rect(w - STEM, 0, w, CAP)


FIVE_WIDTH = 800


@glyph("five", "5", SB.STEM, SB.ROUND)
def five() -> Shape:
    w = FIVE_WIDTH
    lower = rounded([(0, 0), (w, 0, RB), (w, MID_HI, RA), (0, MID_HI)])
    lower_counter = rounded([(-FAR, BAR), (w - BOWL, BAR, rB), (w - BOWL, MID_LO, rA), (-FAR, MID_LO)])
    return (lower - lower_counter) | rect(0, CAP - BAR, w, CAP) | rect(0, MID_LO, STEM, CAP)


SIX_WIDTH = 800


@glyph("six", "6", SB.ROUND, SB.ROUND)
def six() -> Shape:
    w = SIX_WIDTH
    outer = rounded([
        (w, CAP), (0, CAP, RB), (0, 0, RA), (w, 0, RB), (w, MID_HI, RA),
        (STEM, MID_HI, rA), (STEM, CAP - BAR, rB), (w, CAP - BAR),
    ])
    counter = rounded([(STEM, BAR, rA), (w - BOWL, BAR, rB), (w - BOWL, MID_LO, rA), (STEM, MID_LO, rB)])
    return outer - counter


SEVEN_WIDTH, SEVEN_FOOT = 760, 190


@glyph("seven", "7", SB.BAR, SB.BAR)
def seven() -> Shape:
    w = SEVEN_WIDTH
    diag = diagonal((SEVEN_FOOT, 0), (w, CAP - BAR), DIAG)
    return clip_box(rect(0, CAP - BAR, w, CAP) | diag, 0, 0, w, CAP)


EIGHT_WIDTH, EIGHT_INSET = 820, 34


@glyph("eight", "8", SB.ROUND, SB.ROUND)
def eight() -> Shape:
    w, i = EIGHT_WIDTH, EIGHT_INSET
    upper = rounded([(i, MID_LO), (w - i, MID_LO), (w - i, CAP, RA), (i, CAP, RB)])
    lower = rounded([(0, 0, RA), (w, 0, RB), (w, MID_HI, RB), (0, MID_HI, RB)])
    upper_counter = rounded([
        (i + STEM, MID_HI, rA), (w - i - BOWL, MID_HI, rB),
        (w - i - BOWL, CAP - BAR, rA), (i + STEM, CAP - BAR, rB),
    ])
    lower_counter = rounded([(STEM, BAR, rA), (w - BOWL, BAR, rB), (w - BOWL, MID_LO, rA), (STEM, MID_LO, rB)])
    return (upper | lower) - upper_counter - lower_counter


@glyph("nine", "9", SB.ROUND, SB.ROUND)
def nine() -> Shape:
    return six().rotated_180(SIX_WIDTH / 2, CAP / 2)
