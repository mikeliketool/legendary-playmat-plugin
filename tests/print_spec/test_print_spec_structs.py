"""Tests for print_spec.structs beyond the acceptance tests: settings errors say what's allowed."""

import math

import pytest
from print_spec.structs import PrintSettings


@pytest.mark.parametrize("dpi", [149, 601])
def test_dpi_error_gives_the_allowed_range(dpi: int) -> None:
    with pytest.raises(ValueError, match=r"DPI must be between 150 and 600"):
        PrintSettings(dpi=dpi)


@pytest.mark.parametrize("bleed", [-0.01, 0.51, math.nan])
def test_bleed_error_gives_the_allowed_range(bleed: float) -> None:
    with pytest.raises(ValueError, match=r"Bleed must be between 0 and 0\.5 inches"):
        PrintSettings(bleed=bleed)
