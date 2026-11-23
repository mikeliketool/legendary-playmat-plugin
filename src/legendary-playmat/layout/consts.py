"""Layout constants for a Marvel Legendary playmat: card sizes, margins, gaps, row tops, cell grids, and labels."""

from collections.abc import Mapping
from typing import Final

from printing_spec.consts import Mat

# The measurements below come from the old GIMP 2 plugin, which worked in pixels at 150 DPI, so each one is written
# as old pixels / 150. The old canvas had a 1/4" bleed, which put the trim 37 px in from its left and top edges and
# 38 px in from its right and bottom edges. The old 115 px gap from the canvas edge is therefore 78 px from the
# left and top of the trim, and 77 px from the right and bottom.
MARGIN_LEFT_TOP: Final = 78 / 150
MARGIN_RIGHT_BOTTOM: Final = 77 / 150
CARD_WIDTH: Final = 2.5  # 375 px
CARD_HEIGHT: Final = 3.5  # 525 px
LABEL_HEIGHT: Final = 65 / 150
ROW_GAP: Final = 85 / 150
COLUMN_GAP: Final = 70 / 150
ROW_TOPS: Final = tuple(MARGIN_LEFT_TOP + row * (LABEL_HEIGHT + CARD_HEIGHT + ROW_GAP) for row in range(3))

EXTRA_CELL: Final = "extra"
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

# Each mat's cells by row and column, as they appear on the mat. The City and HQ fill the empty middle.
CELL_GRIDS: Final[Mapping[Mat, tuple[tuple[str | None, ...], ...]]] = {
    Mat.STANDARD: (
        ("scheme", "twists", "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", None, None, "villain-deck"),
        ("shield", "sidekicks", None, None, "hero-deck"),
    ),
    Mat.OVERSIZE: (
        (EXTRA_CELL, "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", "villain-deck", "shield"),
        ("scheme", "twists", "hero-deck", "sidekicks"),
    ),
}
