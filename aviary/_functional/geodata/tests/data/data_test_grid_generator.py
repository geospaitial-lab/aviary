import numpy as np
from shapely.geometry import box

from ....._utils.types import BoundingBox

data_test_compute_coordinates = [
    # test case 1: bounding_box is not quantized
    (
        BoundingBox(-127, -127, 127, 127),
        128,
        False,
        np.array([[-127, -127], [1, -127], [-127, 1], [1, 1]], dtype=np.int32),
    ),
    # test case 2: bounding_box is quantized
    (
        BoundingBox(-127, -127, 127, 127),
        128,
        True,
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
    ),
]

data_test__generate_tiles = [
    (
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
        128,
        [
            box(-128, -128, 0, 0),
            box(0, -128, 128, 0),
            box(-128, 0, 0, 128),
            box(0, 0, 128, 128),
        ],
    ),
]
