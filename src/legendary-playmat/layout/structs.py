"""Layout data types for a Marvel Legendary playmat: the cells, City, HQ, whole layout, and unknown-cell error.

Pure Python with no GIMP code, so it can be tested on its own. Everything is in inches from the trim (see
printing_spec.structs.MatBox), and layout.transforms builds it.
"""

from dataclasses import dataclass

from printing_spec.consts import Mat
from printing_spec.structs import MatBox


@dataclass(frozen=True)
class Cell:
    """A card cell: a label box with the card area below it.

    The key never changes and is what a cell's layer group records. The label is the text drawn on the mat.
    """

    key: str
    label: str
    label_box: MatBox
    card: MatBox


@dataclass(frozen=True)
class District:
    """One of the City's five spaces, with its name label."""

    name: str
    label_box: MatBox


@dataclass(frozen=True)
class City:
    """The City: an outline with a title, four vertical dividers, and a strip of district labels.

    Attributes:
        outline: The City's border.
        title_box: The box for the City's title, across the top of the outline.
        divider_xs: The x of each divider line, in inches from the trim's left edge. Each line runs the full height
            of the outline.
        label_strip: The strip across the bottom of the outline that holds the district labels.
        districts: The five districts, left to right. Each one's label box is its fifth of the label strip.
    """

    outline: MatBox
    title_box: MatBox
    divider_xs: tuple[float, ...]
    label_strip: MatBox
    districts: tuple[District, ...]


@dataclass(frozen=True)
class Headquarters:
    """The HQ row: an outline with a title."""

    outline: MatBox
    title_box: MatBox


class UnknownCellError(KeyError):
    """A layout has no cell with the requested key.

    It's a KeyError, so code that expects one still works. Unlike a plain KeyError, its message reads as plain text
    instead of being wrapped in quotes, so it can be shown to the user as it is.
    """

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


@dataclass(frozen=True)
class Layout:
    """Everything drawn on one mat, in inches from the trim."""

    mat: Mat
    cells: tuple[Cell, ...]
    city: City
    hq: Headquarters
