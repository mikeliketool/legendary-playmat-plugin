"""Printing spec constants for a Marvel Legendary playmat: mat sizes, limits, safe margin, rounding, scaled sizes."""

from enum import Enum
from typing import Final

MIN_DPI: Final = 150
MAX_DPI: Final = 600
MAX_BLEED: Final = 0.5
# Inked Gaming's cut isn't exact, so text and important art stay this far inside the trim.
# https://www.inkedgaming.com/pages/art-instructions
SAFE_MARGIN: Final = 0.5

# Inches typed as decimals aren't exact in binary floating point, so 0.29 x 200 comes out as 57.99999999999999.
# Rounding a product to this many decimal places first lets a whole or half pixel on paper round as one.
PIXEL_PRECISION: Final = 9

GIMP2_DPI: Final = 150
LABEL_FONT_INCHES: Final = 54 / GIMP2_DPI
TITLE_FONT_INCHES: Final = 150 / GIMP2_DPI
OUTLINE_THICKNESS_INCHES: Final = 3 / GIMP2_DPI
LINE_WIDTH_INCHES: Final = 3 / GIMP2_DPI
CORNER_RADIUS_INCHES: Final = 30 / GIMP2_DPI


class Mat(Enum):
    """The two mat sizes Inked Gaming prints, as (width, height) of the trim in inches."""

    STANDARD = (24.0, 14.0)
    OVERSIZE = (28.0, 14.0)

    @property
    def width(self) -> float:
        """Trim width in inches."""
        return self.value[0]

    @property
    def height(self) -> float:
        """Trim height in inches."""
        return self.value[1]
