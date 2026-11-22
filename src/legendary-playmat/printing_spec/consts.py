"""Printing spec constants for a Marvel Legendary playmat: mat sizes, settings limits, rounding, and scaled sizes."""

from enum import Enum
from typing import Final

MIN_DPI: Final = 150
MAX_DPI: Final = 600
MAX_BLEED: Final = 0.5  # inches. The smallest bleed is 0.

# Inches typed as decimals aren't exact in binary floating point, so 0.29 x 200 comes out as 57.99999999999999.
# Rounding a product to this many decimal places first lets a whole or half pixel on paper round as one.
PIXEL_PRECISION: Final = 9

# Sizes in inches that become pixels at the print DPI.
LABEL_FONT_SIZE: Final = 54 / 150
TITLE_FONT_SIZE: Final = 150 / 150
OUTLINE_THICKNESS: Final = 3 / 150
LINE_WIDTH: Final = 3 / 150
CORNER_RADIUS: Final = 30 / 150


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
