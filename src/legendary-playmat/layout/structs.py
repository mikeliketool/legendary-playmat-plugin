"""Layout data types for a Marvel Legendary playmat: the cells, the whole layout, and the unknown-cell error.

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
