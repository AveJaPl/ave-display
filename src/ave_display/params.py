"""Wspólne parametry kroju Ave Display.

Wszystkie glify projektowane są w układzie pionowym (bez pochylenia), a na końcu
pochylane o SLANT_DEG wokół połowy wysokości wersalików. Wartości wzorcowe
pochodzą z obrysu `reference/R-z-monogramu.svg` przeskalowanego do CAP = 700.
"""

import math

UPM = 1000
CAP = 700
ASCENT = 950
DESCENT = -250

SLANT_DEG = 28.0
SLANT = math.tan(math.radians(SLANT_DEG))
SHEAR_ORIGIN_Y = CAP / 2

STEM = 240
BAR = 178
BOWL = 230

MID_LO, MID_HI = 280, 420
R_MID_LO, R_MID_HI = 226, 391

TIP_X = 22
BEAM_TIP_X = 90
BACKCUT = 1.108

LEG = 204
DIAG = 212

STENCIL = 96

RA = (242, 178, 0.34)
RB = (146, 110, 0.58)
rA = (70, 54, 0.48)
rB = (50, 36, 0.60)

FAR = 2000
