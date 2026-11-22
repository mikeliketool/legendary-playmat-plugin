"""Layout of a Marvel Legendary playmat: where everything goes on the mat, in inches from the trim.

Pure Python with no GIMP code, so the layout can be tested on its own.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from print_spec.model import Mat, Rect

# The measurements below come from the old GIMP 2 plugin, which worked in pixels at 150 DPI, so each one is written
# as old pixels / 150. The old canvas had a 1/4" bleed, which put the trim 37 px in from its left and top edges and
# 38 px in from its right and bottom edges. The old 115 px gap from the canvas edge is therefore 78 px from the
# left and top of the trim, and 77 px from the right and bottom.
_MARGIN_LEFT_TOP: Final = 78 / 150
_MARGIN_RIGHT_BOTTOM: Final = 77 / 150
_CARD_WIDTH: Final = 2.5  # 375 px
_CARD_HEIGHT: Final = 3.5  # 525 px
_LABEL_HEIGHT: Final = 65 / 150
_ROW_GAP: Final = 85 / 150
_COLUMN_GAP: Final = 70 / 150
_ROW_TOPS: Final = tuple(_MARGIN_LEFT_TOP + row * (_LABEL_HEIGHT + _CARD_HEIGHT + _ROW_GAP) for row in range(3))

_EXTRA_CELL: Final = "extra"
_LABELS: Final[Mapping[str, str]] = {
    _EXTRA_CELL: "",
    "mastermind": "Mastermind",
    "scheme": "Scheme",
    "escaped": "Escaped",
    "strikes": "Strikes",
    "twists": "Twists",
    "bystanders": "Bystanders",
    "shield": "S.H.I.E.L.D.",
    "sidekicks": "Sidekicks",
    "wounds": "Wounds",
    "villain-deck": "Villain Deck",
    "hero-deck": "Hero Deck",
}

# Each mat's cells by row and column, as they appear on the mat. The City and HQ fill the empty middle.
_CELL_GRIDS: Final[Mapping[Mat, tuple[tuple[str | None, ...], ...]]] = {
    Mat.STANDARD: (
        ("scheme", "twists", "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", None, None, "villain-deck"),
        ("shield", "sidekicks", None, None, "hero-deck"),
    ),
    Mat.OVERSIZE: (
        (_EXTRA_CELL, "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", "villain-deck", "shield"),
        ("scheme", "twists", "hero-deck", "sidekicks"),
    ),
}


@dataclass(frozen=True)
class Cell:
    """A card cell: a label box with the card area below it.

    The key never changes and is what a cell's layer group records. The label is the text drawn on the mat.
    """

    key: str
    label: str
    label_box: Rect
    card: Rect


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

    def cell(self, key: str) -> Cell:
        """Find a cell by its key.

        Args:
            key: The key saved on the cell's layer group, such as "mastermind".

        Returns:
            The cell with that key.

        Raises:
            UnknownCellError: If this layout has no cell with that key. It's a KeyError, and its message names the
                key.
        """
        for cell in self.cells:
            if cell.key == key:
                return cell
        raise UnknownCellError(f"No cell with key {key!r} in this {_size_name(self.mat)} layout.")


def layout_for(mat: Mat, include_extra_cell: bool = False) -> Layout:
    """Build the layout for a mat.

    Args:
        mat: Which mat size to lay out.
        include_extra_cell: Whether to add the blank cell in the 28x14 mat's top-left corner.

    Returns:
        Every cell, in inches from the trim.

    Raises:
        ValueError: If include_extra_cell is True for a mat that has no extra cell (the 24x14).
    """
    if include_extra_cell and mat is not Mat.OVERSIZE:
        raise ValueError(f"Only the 28x14 mat has an extra cell, so the {_size_name(mat)} mat can't include one.")
    columns = _column_lefts(mat)
    cells = tuple(
        _cell(key, columns[column], _ROW_TOPS[row])
        for row, keys in enumerate(_CELL_GRIDS[mat])
        for column, key in enumerate(keys)
        if key is not None and (key != _EXTRA_CELL or include_extra_cell)
    )
    return Layout(mat, cells)


def _size_name(mat: Mat) -> str:
    return f"{mat.width:g}x{mat.height:g}"


def _column_lefts(mat: Mat) -> tuple[float, ...]:
    """Left edge of each column of cells: the last two are measured from the right trim, the others from the left."""
    step = _CARD_WIDTH + _COLUMN_GAP
    first = _MARGIN_LEFT_TOP
    last = mat.width - _MARGIN_RIGHT_BOTTOM - _CARD_WIDTH
    match mat:
        case Mat.STANDARD:
            return (first, first + step, first + 2 * step, last - step, last)
        case Mat.OVERSIZE:
            return (first, first + step, last - step, last)


def _cell(key: str, left: float, top: float) -> Cell:
    label_box = Rect(left, top, _CARD_WIDTH, _LABEL_HEIGHT)
    card = Rect(left, label_box.bottom, _CARD_WIDTH, _CARD_HEIGHT)
    return Cell(key, _LABELS[key], label_box, card)
