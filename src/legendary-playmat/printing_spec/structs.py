"""Printing spec data types for a Marvel Legendary playmat: print settings, boxes, and scaled sizes.

Pure Python with no GIMP code, so it can be tested on its own. Positions are in inches from the top-left corner of
the trim (the finished mat's edge), and only become pixels at drawing time (see printing_spec.transforms).
"""

from dataclasses import dataclass

from printing_spec.consts import MAX_BLEED, MAX_DPI, MIN_DPI


@dataclass(frozen=True)
class PrintSettings:
    """Resolution and bleed for one print file.

    Attributes:
        dpi: Print resolution in dots per inch.
        bleed: Extra artwork past the trim on each side, in inches.

    Raises:
        ValueError: If dpi is outside 150-600 or bleed is outside 0-0.5 inches.
    """

    dpi: int = 150
    bleed: float = 0.25

    def __post_init__(self) -> None:
        if not MIN_DPI <= self.dpi <= MAX_DPI:
            raise ValueError(f"DPI must be between {MIN_DPI} and {MAX_DPI}, not {self.dpi}.")
        if not 0 <= self.bleed <= MAX_BLEED:
            raise ValueError(f"Bleed must be between 0 and {MAX_BLEED} inches, not {self.bleed}.")


@dataclass(frozen=True)
class MatBox:
    """A box on the mat in inches, measured from the top-left corner of the trim."""

    left: float
    top: float
    width: float
    height: float

    @property
    def right(self) -> float:
        """Right edge in inches from the trim's left edge."""
        return self.left + self.width

    @property
    def bottom(self) -> float:
        """Bottom edge in inches from the trim's top edge."""
        return self.top + self.height


@dataclass(frozen=True)
class CanvasBox:
    """A box in pixels on the GIMP canvas, bleed included."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Style:
    """Sizes in pixels that scale with DPI."""

    label_font_size: int
    title_font_size: int
    outline_thickness: int
    line_width: int
    corner_radius: int
