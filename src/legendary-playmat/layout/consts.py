"""Layout constants for a Marvel Legendary playmat: card, City and HQ sizes, margins, gaps, cell grids, and labels."""

from collections.abc import Mapping
from typing import Final

from printing_spec.consts import GIMP2_DPI, Mat

# The GIMP 2 plugin's canvas had a 37.5 px bleed, which the trim rule splits as 37 px at the left and top and 38 px
# at the right and bottom. So its 115 px outside gap is 78 px from the left and top trim, and 77 px from the right
# and bottom.
GIMP2_TRIM_LEFT_TOP: Final = 37
GIMP2_TRIM_RIGHT_BOTTOM: Final = 38
GIMP2_OUTSIDE_GAP: Final = 115
MARGIN_LEFT_TOP: Final = (GIMP2_OUTSIDE_GAP - GIMP2_TRIM_LEFT_TOP) / GIMP2_DPI
MARGIN_RIGHT_BOTTOM: Final = (GIMP2_OUTSIDE_GAP - GIMP2_TRIM_RIGHT_BOTTOM) / GIMP2_DPI
CARD_WIDTH: Final = 2.5
CARD_HEIGHT: Final = 3.5
LABEL_HEIGHT: Final = 65 / GIMP2_DPI
ROW_GAP: Final = 85 / GIMP2_DPI
COLUMN_GAP: Final = 70 / GIMP2_DPI
CITY_AND_HQ_WIDTH: Final = 2070 / GIMP2_DPI
CITY_AND_HQ_HEIGHT: Final = 600 / GIMP2_DPI
TITLE_HEIGHT: Final = 200 / GIMP2_DPI
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

CELL_GRIDS: Final[Mapping[Mat, tuple[tuple[str | None, ...], ...]]] = {
    Mat.STANDARD: (
        ("scheme", "twists", "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", CITY_AND_HQ_SPACE, CITY_AND_HQ_SPACE, "villain-deck"),
        ("shield", "sidekicks", CITY_AND_HQ_SPACE, CITY_AND_HQ_SPACE, "hero-deck"),
    ),
    Mat.OVERSIZE: (
        (EXTRA_CELL, "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", "villain-deck", "shield"),
        ("scheme", "twists", "hero-deck", "sidekicks"),
    ),
}

GAP_BEFORE_CITY_AND_HQ: Final[Mapping[Mat, float]] = {
    Mat.STANDARD: (70 + 15) / GIMP2_DPI,
    Mat.OVERSIZE: 162.5 / GIMP2_DPI,
}
