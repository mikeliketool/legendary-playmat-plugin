"""Acceptance tests for the layout follow-ups: the 28x14's extra cell, and asking which mats have one."""

import pytest
from layout.transforms import find_cell, has_extra_cell, layout_for
from printing_spec.consts import Mat


def test_leaving_out_the_extra_cell_moves_no_other_cell() -> None:
    with_extra = layout_for(Mat.OVERSIZE, include_extra_cell=True)
    for cell in layout_for(Mat.OVERSIZE).cells:
        assert cell == find_cell(with_extra, cell.key)


def test_only_the_28x14_mat_has_an_extra_cell() -> None:
    assert has_extra_cell(Mat.OVERSIZE) is True
    assert has_extra_cell(Mat.STANDARD) is False


@pytest.mark.parametrize("mat", [Mat.STANDARD, Mat.OVERSIZE])
def test_the_extra_cell_can_be_included_exactly_when_the_mat_has_one(mat: Mat) -> None:
    if has_extra_cell(mat):
        layout = layout_for(mat, include_extra_cell=True)
        assert find_cell(layout, "extra").label == ""
    else:
        with pytest.raises(ValueError, match="Only the 28x14 mat has an extra cell"):
            layout_for(mat, include_extra_cell=True)
