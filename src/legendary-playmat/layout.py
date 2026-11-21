"""Layout of a Marvel Legendary playmat: mat sizes, element positions, and the inches-to-pixels rule.

Pure Python with no GIMP code, so the layout can be tested on its own. Positions are in inches from the
top-left corner of the trim (the finished mat's edge), and only become pixels at drawing time.

This is a stub with the real signatures. The dev agent implements it.
"""

from dataclasses import dataclass
from enum import Enum


class Mat(Enum):
    """The two mat sizes Inked Gaming prints, as (width, height) of the trim in inches."""

    STANDARD = (24.0, 14.0)
    OVERSIZE = (28.0, 14.0)

    @property
    def width(self) -> float:
        """Trim width in inches."""
        raise NotImplementedError

    @property
    def height(self) -> float:
        """Trim height in inches."""
        raise NotImplementedError


@dataclass(frozen=True)
class PrintSettings:
    """Resolution and bleed for one print file.

    Raises:
        ValueError: If dpi is outside 150-600 or bleed is outside 0-0.5 inches.
    """

    dpi: int = 150
    bleed: float = 0.25

    def __post_init__(self) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class PixelRect:
    """A box in pixels on the canvas, bleed included."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Rect:
    """A box in inches, measured from the top-left corner of the trim."""

    left: float
    top: float
    width: float
    height: float

    @property
    def right(self) -> float:
        """Right edge in inches from the trim's left edge."""
        raise NotImplementedError

    @property
    def bottom(self) -> float:
        """Bottom edge in inches from the trim's top edge."""
        raise NotImplementedError

    def to_pixels(self, settings: PrintSettings) -> PixelRect:
        """Convert to pixels: each edge goes through position_to_pixels, and the size comes from those edges."""
        raise NotImplementedError


@dataclass(frozen=True)
class Cell:
    """A card cell: a label box with the card area below it.

    The key never changes and is what a cell's layer group records. The label is the text drawn on the mat.
    """

    key: str
    label: str
    label_box: Rect
    card: Rect


@dataclass(frozen=True)
class District:
    """One of the City's five spaces, with its name label."""

    name: str
    label_box: Rect


@dataclass(frozen=True)
class City:
    """The City: an outline with a title, four vertical dividers, and a strip of district labels."""

    outline: Rect
    title_box: Rect
    divider_xs: tuple[float, ...]
    label_strip: Rect
    districts: tuple[District, ...]


@dataclass(frozen=True)
class Headquarters:
    """The HQ row: an outline with a title."""

    outline: Rect
    title_box: Rect


@dataclass(frozen=True)
class Layout:
    """Everything drawn on one mat, in inches from the trim."""

    mat: Mat
    cells: tuple[Cell, ...]
    city: City
    hq: Headquarters

    def cell(self, key: str) -> Cell:
        """Find a cell by its key.

        Raises:
            KeyError: If this layout has no cell with that key. The message names the key.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class Style:
    """Sizes in pixels that scale with DPI."""

    label_font_size: int
    title_font_size: int
    outline_thickness: int
    line_width: int
    corner_radius: int


def layout_for(mat: Mat, include_extra_cell: bool = False) -> Layout:
    """Build the layout for a mat.

    Raises:
        ValueError: If include_extra_cell is True for a mat that has no extra cell (the 24x14).
    """
    raise NotImplementedError


def canvas_size(mat: Mat, settings: PrintSettings) -> tuple[int, int]:
    """Canvas (width, height) in pixels, bleed included: round((trim + 2 x bleed) x DPI), halves rounded up."""
    raise NotImplementedError


def trim_offset(settings: PrintSettings) -> int:
    """Pixels from the canvas's left or top edge to the trim: floor(bleed x DPI)."""
    raise NotImplementedError


def position_to_pixels(inches: float, settings: PrintSettings) -> int:
    """Canvas pixel for a position in inches from the trim: trim_offset + round(inches x DPI), halves rounded up."""
    raise NotImplementedError


def style_for(settings: PrintSettings) -> Style:
    """Font sizes, outline thickness, line width, and corner radius for these settings."""
    raise NotImplementedError
