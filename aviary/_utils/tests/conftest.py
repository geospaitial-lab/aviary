import pytest

from ..types import (
    BoundingBox,
)


@pytest.fixture(scope='function')
def bounding_box() -> BoundingBox:
    x_min = -128
    y_min = -128
    x_max = 128
    y_max = 128
    return BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )
