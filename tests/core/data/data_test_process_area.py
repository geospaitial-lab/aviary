import re

import numpy as np

from aviary.core.process_area import ProcessArea
from tests.core.conftest import (
    get_process_area,
    get_process_area_coordinates,
)

data_test_process_area_add = [
    # test case 1: other contains no coordinates
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        get_process_area(),
    ),
    # test case 2: other contains coordinates
    (
        ProcessArea(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_add_exceptions = [
    # test case 1: tile_size is not equal
    (
        ProcessArea(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the process areas must be equal.'),
    ),
]

data_test_process_area_and = [
    # test case 1: other contains no coordinates
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
    ),
    # test case 2: other contains coordinates
    (
        ProcessArea(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        ProcessArea(
            coordinates=np.array(
                [[-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_and_exceptions = [
    # test case 1: tile_size is not equal
    (
        ProcessArea(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the process areas must be equal.'),
    ),
]

data_test_process_area_append = [

]

data_test_process_area_append_inplace = [

]

data_test_process_area_append_inplace_return = [

]

data_test_process_area_append_inplace_return_warnings = [

]

data_test_process_area_append_inplace_warnings = [

]

data_test_process_area_append_warnings = [

]

data_test_process_area_area = [
    # test case 1: process_area contains no coordinates
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        0,
    ),
    # test case 2: process_area contains one coordinates
    (
        ProcessArea(
            coordinates=np.array(
                [[-128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        16384,
    ),
    # test case 3: process_area contains four coordinates
    (
        get_process_area(),
        65536,
    ),
]

data_test_process_area_chunk = [

]

data_test_process_area_chunk_exceptions = [

]

data_test_process_area_eq = [

]

data_test_process_area_from_bounding_box = [

]

data_test_process_area_from_bounding_box_exceptions = [

]

data_test_process_area_from_gdf = [

]

data_test_process_area_from_gdf_exceptions = [

]

data_test_process_area_from_json = [
    # test case 1: process_area contains no coordinates
    (
        '{"coordinates": [], "tile_size": 128}',
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
    ),
    # test case 2: process_area contains coordinates
    (
        '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]], "tile_size": 128}',
        get_process_area(),
    ),
]

data_test_process_area_from_json_exceptions = [

]

data_test_process_area_getitem = [
    (0, (-128, -128)),
    (1, (0, -128)),
    (2, (-128, 0)),
    (3, (0, 0)),
    (-1, (0, 0)),
    (-2, (-128, 0)),
    (-3, (0, -128)),
    (-4, (-128, -128)),
]

data_test_process_area_getitem_slice = [
    (
        slice(None, 2),
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(2, None),
        ProcessArea(
            coordinates=np.array(
                [[-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(1, -1),
        ProcessArea(
            coordinates=np.array(
                [[0, -128], [-128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None),
        get_process_area(),
    ),
    (
        slice(None, None, 2),
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [-128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None, -2),
        ProcessArea(
            coordinates=np.array(
                [[0, 0], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None, -1),
        ProcessArea(
            coordinates=np.array(
                [[0, 0], [-128, 0], [0, -128], [-128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_init = [
    # test case 1: process_area contains no coordinates
    (
        None,
        128,
        np.empty(
            shape=(0, 2),
            dtype=np.int32,
        ),
        128,
    ),
    # test case 2: process_area contains coordinates
    (
        get_process_area_coordinates(),
        128,
        get_process_area_coordinates(),
        128,
    ),
]

data_test_process_area_init_exceptions = [
    # test case 1: coordinates has one dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has three dimensions
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 2, 2),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates has not two values in the second dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 4),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 4: coordinates is not of data type int32
    (
        np.arange(
            8,
            dtype=np.float32,
        ).reshape(4, 2),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 5: tile_size is 0
    (
        get_process_area_coordinates(),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 6: tile_size is negative
    (
        get_process_area_coordinates(),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]

data_test_process_area_init_warnings = [

]

data_test_process_area_remove = [

]

data_test_process_area_remove_inplace = [

]

data_test_process_area_remove_inplace_return = [

]

data_test_process_area_remove_inplace_return_warnings = [

]

data_test_process_area_remove_inplace_warnings = [

]

data_test_process_area_remove_warnings = [

]

data_test_process_area_sub = [
    # test case 1: other contains no coordinates
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        get_process_area(),
    ),
    # test case 2: other contains coordinates
    (
        ProcessArea(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_sub_exceptions = [
    # test case 1: tile_size is not equal
    (
        ProcessArea(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the process areas must be equal.'),
    ),
]
