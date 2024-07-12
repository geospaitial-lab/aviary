import numpy as np
import pytest

# noinspection PyProtectedMember
from aviary._utils.types import (
    BoundingBox,
    ProcessArea,
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


@pytest.fixture(scope='function')
def process_area() -> ProcessArea:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    return ProcessArea(
        coordinates=coordinates,
    )
