"""Layout constants for a Marvel Legendary playmat: card, City and HQ sizes, margins, gaps, cell grids, and labels."""

from collections.abc import Mapping
from enum import Enum
from typing import Final

from printing_spec.consts import TEMPLATE_DPI, Mat

# The existing mats have their cells 115 px from the template's edge, and the 1/4" bleed (37.5 px) splits as 37 px
# at the left and top and 38 px at the right and bottom, so the margins from the trim are 78 px and 77 px.
MARGIN_LEFT_TOP: Final = 78 / TEMPLATE_DPI
MARGIN_RIGHT_BOTTOM: Final = 77 / TEMPLATE_DPI
CARD_WIDTH: Final = 2.5
CARD_HEIGHT: Final = 3.5
LABEL_HEIGHT: Final = 65 / TEMPLATE_DPI
ROW_GAP: Final = 85 / TEMPLATE_DPI
COLUMN_GAP: Final = 70 / TEMPLATE_DPI
CITY_AND_HQ_WIDTH: Final = 2070 / TEMPLATE_DPI
CITY_AND_HQ_HEIGHT: Final = 600 / TEMPLATE_DPI
TITLE_HEIGHT: Final = 200 / TEMPLATE_DPI
LABEL_STRIP_HEIGHT: Final = CITY_AND_HQ_HEIGHT / 4
ROW_TOPS: Final = tuple(MARGIN_LEFT_TOP + row * (LABEL_HEIGHT + CARD_HEIGHT + ROW_GAP) for row in range(3))

EXTRA_CELL: Final = "extra"
CITY_AND_HQ_SPACE: Final = None
LABELS: Final[Mapping[str, str]] = {
    EXTRA_CELL: "",
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
DISTRICT_NAMES: Final = ("Bridge", "Streets", "Rooftops", "Bank", "Sewers")


class MatLayout(Enum):
    """Each mat's layout facts, as (cell grid, columns measured from the left, gap before the City and HQ)."""

    _value_: tuple[tuple[tuple[str | None, ...], ...], int, float]

    STANDARD = (
        (
            ("scheme", "twists", "escaped", "wounds", "bystanders"),
            ("mastermind", "strikes", CITY_AND_HQ_SPACE, CITY_AND_HQ_SPACE, "villain-deck"),
            ("shield", "sidekicks", CITY_AND_HQ_SPACE, CITY_AND_HQ_SPACE, "hero-deck"),
        ),
        3,
        (70 + 15) / TEMPLATE_DPI,
    )
    OVERSIZE = (
        (
            (EXTRA_CELL, "escaped", "wounds", "bystanders"),
            ("mastermind", "strikes", "villain-deck", "shield"),
            ("scheme", "twists", "hero-deck", "sidekicks"),
        ),
        2,
        162.5 / TEMPLATE_DPI,
    )

    @property
    def cell_grid(self) -> tuple[tuple[str | None, ...], ...]:
        """Cell keys row by row, top to bottom, with CITY_AND_HQ_SPACE where the City and HQ go."""
        return self._value_[0]

    @property
    def columns_from_left(self) -> int:
        """How many columns, counting from the left, are measured from the left margin."""
        return self._value_[1]

    @property
    def gap_before_city_and_hq(self) -> float:
        """Gap in inches between the second column's cards and the City and HQ."""
        return self._value_[2]


MAT_LAYOUTS: Final[Mapping[Mat, MatLayout]] = {
    Mat.STANDARD: MatLayout.STANDARD,
    Mat.OVERSIZE: MatLayout.OVERSIZE,
}
