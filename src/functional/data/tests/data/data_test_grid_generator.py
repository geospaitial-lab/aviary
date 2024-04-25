import numpy as np
from shapely.geometry import box

data_test_compute_coordinates = [
    # test case 1: bounding_box is not quantized
    (
        (-127, -127, 128, 128),
        128,
        False,
        np.array([[-127, -127], [1, -127], [-127, 1], [1, 1]], dtype=np.int32),
    ),
    # test case 2: bounding_box is quantized
    (
        (-127, -127, 128, 128),
        128,
        True,
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
    ),
]

data_test__quantize_coordinates = [
    (-129, -129, 128, (-256, -256)),
    (-128, -128, 128, (-128, -128)),
    (-127, -127, 128, (-128, -128)),
    (-1, -1, 128, (-128, -128)),
    (0, 0, 128, (0, 0)),
    (1, 1, 128, (0, 0)),
    (127, 127, 128, (0, 0)),
    (128, 128, 128, (128, 128)),
    (129, 129, 128, (128, 128)),
]

data_test__generate_polygons = [
    (
        np.array([[-256, -256], [0, 0], [256, 256]], dtype=np.int32),
        256,
        [
            box(-256, -256, 0, 0),
            box(0, 0, 256, 256),
            box(256, 256, 512, 512),
        ],
    ),
]
