import re

import numpy as np

from aviary.core.process_area import ProcessArea

data_test_process_area_init = [
    # test case 1: process area has no tiles
    (
        None,
        128,
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
    # test case 2: process area has one tile
    (
        np.array([[-128, -128]], dtype=np.int32),
        128,
        np.array([[-128, -128]], dtype=np.int32),
    ),
    # test case 3: process area has four tiles
    (
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
        128,
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
    ),
]

data_test_process_area_validation = [
    # test case 1: coordinates has not 2 dimensions
    (
        np.arange(8, dtype=np.int32).reshape(4, 2, 1),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has not 2 values in the second dimension
    (
        np.arange(8, dtype=np.int32).reshape(2, 4),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates is not of data type int32
    (
        np.arange(8, dtype=np.float32).reshape(4, 2),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 4: tile_size is 0
    (
        np.arange(8, dtype=np.int32).reshape(4, 2),
        0,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
    # test case 5: tile_size is negative
    (
        np.arange(8, dtype=np.int32).reshape(4, 2),
        -1,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
]

data_test_process_area_area = [
    # test case 1: process area has no tiles
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        0,
    ),
    # test case 2: process area has one tile
    (
        ProcessArea(
            coordinates=np.array([[-128, -128]], dtype=np.int32),
            tile_size=128,
        ),
        16384,
    ),
    # test case 3: process area has four tiles
    (
        ProcessArea(
            coordinates=np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32),
            tile_size=128,
        ),
        65536,
    ),
]
