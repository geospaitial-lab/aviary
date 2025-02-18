import copy
import re

import numpy as np

from aviary.core.process_area import ProcessArea
from tests.core.conftest import (
    get_bounding_box,
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
    # test case 1: Default
    (
        get_process_area(),
        (128, -128),
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_append_inplace = copy.deepcopy(data_test_process_area_append)
data_test_process_area_append_inplace_return = copy.deepcopy(data_test_process_area_append)

data_test_process_area_append_warnings = [
    # test case 1: coordinates is already in process_area
    (
        get_process_area(),
        (-128, -128),
        get_process_area(),
        re.escape('Invalid coordinates! The coordinates are already in the process area.'),
    ),
]

data_test_process_area_append_inplace_warnings = copy.deepcopy(data_test_process_area_append_warnings)
data_test_process_area_append_inplace_return_warnings = copy.deepcopy(data_test_process_area_append_warnings)

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
    # test case 1: len(coordinates) is divisible by num_chunks
    (
        get_process_area(),
        2,
        [
            ProcessArea(
                coordinates=np.array(
                    [[-128, -128], [0, -128]],
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
        ],
    ),
    # test case 2: len(coordinates) is not divisible by num_chunks
    (
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        2,
        [
            ProcessArea(
                coordinates=np.array(
                    [[-128, -128], [0, -128], [128, -128]],
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
        ],
    ),
    # test case 3: num_chunks is equal to len(coordinates)
    (
        get_process_area(),
        4,
        [
            ProcessArea(
                coordinates=np.array(
                    [[-128, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            ProcessArea(
                coordinates=np.array(
                    [[0, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            ProcessArea(
                coordinates=np.array(
                    [[-128, 0]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            ProcessArea(
                coordinates=np.array(
                    [[0, 0]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
        ],
    ),
    # test case 4: num_chunks is 1
    (
        get_process_area(),
        1,
        [
            get_process_area(),
        ],
    ),
]

data_test_process_area_chunk_exceptions = [
    # test case 1: num_chunks is negative
    (
        -2,
        re.escape('Invalid num_chunks! The number of chunks must be in the range [1, n].'),
    ),
    # test case 2: num_chunks is 0
    (
        0,
        re.escape('Invalid num_chunks! The number of chunks must be in the range [1, n].'),
    ),
    # test case 3: num_chunks is greater than len(coordinates)
    (
        5,
        re.escape('Invalid num_chunks! The number of chunks must be in the range [1, n].'),
    ),
]

data_test_process_area_contains = [
    ((-128, -128), True),
    ((0, -128), True),
    ((-128, 0), True),
    ((0, 0), True),
    ((128, -128), False),
    ((128, 0), False),
]

data_test_process_area_eq = [
    # test case 1: other is equal
    (
        get_process_area(),
        True,
    ),
    # test case 2: coordinates is not equal
    (
        ProcessArea(
            coordinates=None,
            tile_size=128,
        ),
        False,
    ),
    # test case 3: tile_size is not equal
    (
        ProcessArea(
            coordinates=get_process_area_coordinates(),
            tile_size=64,
        ),
        False,
    ),
    # test case 4: other is not of type ProcessArea
    (
        'invalid',
        False,
    ),
]

data_test_process_area_from_bounding_box = [
    # test case 1: quantize is False
    (
        get_bounding_box(),
        128,
        False,
        ProcessArea(
            coordinates=np.array(
                [[-128, -64], [0, -64], [-128, 64], [0, 64]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 2: quantize is True
    (
        get_bounding_box(),
        128,
        True,
        ProcessArea(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_from_bounding_box_exceptions = [
    # test case 1: tile_size is negative
    (
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 2: tile_size is 0
    (
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
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
    # test case 1: json_string does not contain the keys coordinates and tile_size
    (
        '{}',
        re.escape('Invalid json_string! The JSON string must contain the keys coordinates and tile_size.'),
    ),
    # test case 2: json_string does not contain the key tile_size
    (
        '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]]}',
        re.escape('Invalid json_string! The JSON string must contain the keys coordinates and tile_size.'),
    ),
    # test case 3: json_string does not contain the key coordinates
    (
        '{"tile_size": 128}',
        re.escape('Invalid json_string! The JSON string must contain the keys coordinates and tile_size.'),
    ),
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
    # test case 3: coordinates is not sorted
    (
        np.array(
            [[0, 0], [-128, 0], [0, -128], [-128, -128]],
            dtype=np.int32,
        ),
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
    # test case 5: tile_size is negative
    (
        get_process_area_coordinates(),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 6: tile_size is 0
    (
        get_process_area_coordinates(),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]

data_test_process_area_init_warnings = [
    # test case 1: coordinates contains duplicates
    (
        np.array(
            [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, -128], [0, 0]],
            dtype=np.int32,
        ),
        128,
        get_process_area_coordinates(),
        128,
        re.escape('Invalid coordinates! The coordinates must contain unique coordinates. Duplicates are removed.'),
    ),
]

data_test_process_area_remove = [
    # test case 1: Default
    (
        get_process_area(),
        (-128, -128),
        ProcessArea(
            coordinates=np.array(
                [[0, -128], [-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_process_area_remove_inplace = copy.deepcopy(data_test_process_area_remove)
data_test_process_area_remove_inplace_return = copy.deepcopy(data_test_process_area_remove)


data_test_process_area_remove_warnings = [
    # test case 1: coordinates is not in process_area
    (
        get_process_area(),
        (128, -128),
        get_process_area(),
        re.escape('Invalid coordinates! The coordinates are not in the process area.'),
    ),
]

data_test_process_area_remove_inplace_warnings = copy.deepcopy(data_test_process_area_remove_warnings)
data_test_process_area_remove_inplace_return_warnings = copy.deepcopy(data_test_process_area_remove_warnings)

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
