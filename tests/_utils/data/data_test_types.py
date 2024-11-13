import re

import numpy as np

# noinspection PyProtectedMember
from aviary._utils.types import (
    BoundingBox,
    ProcessArea,
)

data_test_bounding_box_buffer = [
    # test case 1: buffer_size is 0
    (0, BoundingBox(-128, -128, 128, 128)),
    # test case 2: buffer_size is positive
    (64, BoundingBox(-192, -192, 192, 192)),
    # test case 3: buffer_size is negative
    (-64, BoundingBox(-64, -64, 64, 64)),
]

data_test_bounding_box_buffer_exceptions = [
    # test case 1: buffer_size is equal to half the width or height of the bounding box
    (-128, 'Invalid buffer size! buffer_size must be less than half the width or height of the bounding box.'),
    # test case 2: buffer_size is greater than half the width or height of the bounding box
    (-192, 'Invalid buffer size! buffer_size must be less than half the width or height of the bounding box.'),
]

data_test_bounding_box_init_exceptions = [
    # test case 1: x_min == x_max
    (0, 0, 0, 128, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 2: x_min > x_max
    (128, 0, 0, 128, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 3: y_min == y_max
    (0, 0, 128, 0, 'Invalid bounding box! y_min must be less than y_max.'),
    # test case 4: y_min > y_max
    (0, 128, 128, 0, 'Invalid bounding box! y_min must be less than y_max.'),
    # test case 5: x_min == x_max, y_min == y_max
    (0, 0, 0, 0, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 6: x_min > x_max, y_min > y_max
    (128, 128, 0, 0, 'Invalid bounding box! x_min must be less than x_max.'),
]

data_test_bounding_box_properties_exceptions = [
    # test case 1: x_min == x_max
    ('x_min', 128, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 2: x_min > x_max
    ('x_min', 129, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 3: y_min == y_max
    ('y_min', 128, 'Invalid bounding box! y_min must be less than y_max.'),
    # test case 4: y_min > y_max
    ('y_min', 129, 'Invalid bounding box! y_min must be less than y_max.'),
    # test case 5: x_max == x_min
    ('x_max', -128, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 6: x_max < x_min
    ('x_max', -129, 'Invalid bounding box! x_min must be less than x_max.'),
    # test case 7: y_max == y_min
    ('y_max', -128, 'Invalid bounding box! y_min must be less than y_max.'),
    # test case 8: y_max < y_min
    ('y_max', -129, 'Invalid bounding box! y_min must be less than y_max.'),
]

data_test_bounding_box_area = [
    # test case 1: bounding box is in all quadrants
    (BoundingBox(-128, -128, 128, 128), 65536),
    # test case 2: bounding box is in the first quadrant
    (BoundingBox(128, 128, 256, 256), 16384),
    # test case 3: bounding box is in the second quadrant
    (BoundingBox(-256, 128, -128, 256), 16384),
    # test case 4: bounding box is in the third quadrant
    (BoundingBox(-256, -256, -128, -128), 16384),
    # test case 5: bounding box is in the fourth quadrant
    (BoundingBox(128, -256, 256, -128), 16384),
]

data_test_bounding_box_quantize = [
    # test case 1: bounding box is in all quadrants, bounding box is divisible by value
    (BoundingBox(-128, -128, 128, 128), 128, BoundingBox(-128, -128, 128, 128)),
    # test case 2: bounding box is in all quadrants, bounding box is not divisible by value
    (BoundingBox(-127, -127, 127, 127), 128, BoundingBox(-128, -128, 128, 128)),
    # test case 3: bounding box is in all quadrants, bounding box is not divisible by value
    (BoundingBox(-129, -129, 129, 129), 128, BoundingBox(-256, -256, 256, 256)),
    # test case 4: bounding box is in the first quadrant, bounding box is divisible by value
    (BoundingBox(128, 128, 256, 256), 128, BoundingBox(128, 128, 256, 256)),
    # test case 5: bounding box is in the first quadrant, bounding box is not divisible by value
    (BoundingBox(129, 129, 255, 255), 128, BoundingBox(128, 128, 256, 256)),
    # test case 6: bounding box is in the first quadrant, bounding box is not divisible by value
    (BoundingBox(127, 127, 257, 257), 128, BoundingBox(0, 0, 384, 384)),
    # test case 7: bounding box is in the second quadrant, bounding box is divisible by value
    (BoundingBox(-256, 128, -128, 256), 128, BoundingBox(-256, 128, -128, 256)),
    # test case 8: bounding box is in the second quadrant, bounding box is not divisible by value
    (BoundingBox(-255, 129, -129, 255), 128, BoundingBox(-256, 128, -128, 256)),
    # test case 9: bounding box is in the second quadrant, bounding box is not divisible by value
    (BoundingBox(-257, 127, -127, 257), 128, BoundingBox(-384, 0, 0, 384)),
    # test case 10: bounding box is in the third quadrant, bounding box is divisible by value
    (BoundingBox(-256, -256, -128, -128), 128, BoundingBox(-256, -256, -128, -128)),
    # test case 11: bounding box is in the third quadrant, bounding box is not divisible by value
    (BoundingBox(-255, -255, -129, -129), 128, BoundingBox(-256, -256, -128, -128)),
    # test case 12: bounding box is in the third quadrant, bounding box is not divisible by value
    (BoundingBox(-257, -257, -127, -127), 128, BoundingBox(-384, -384, 0, 0)),
    # test case 13: bounding box is in the fourth quadrant, bounding box is divisible by value
    (BoundingBox(128, -256, 256, -128), 128, BoundingBox(128, -256, 256, -128)),
    # test case 14: bounding box is in the fourth quadrant, bounding box is not divisible by value
    (BoundingBox(129, -255, 255, -129), 128, BoundingBox(128, -256, 256, -128)),
    # test case 15: bounding box is in the fourth quadrant, bounding box is not divisible by value
    (BoundingBox(127, -257, 257, -127), 128, BoundingBox(0, -384, 384, 0)),
]

data_test_bounding_box_quantize_exceptions = [
    # test case 1: value is 0
    (0, 'Invalid value! value must be positive.'),
    # test case 2: value is negative
    (-128, 'Invalid value! value must be positive.'),
]

data_test_process_area_init_exceptions = [
    # test case 1: coordinates has not 2 dimensions
    (
        np.ones(shape=(4, 2, 1), dtype=np.int32),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has not 2 values in the second dimension
    (
        np.ones(shape=(4, 4), dtype=np.int32),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates is not of data type int32
    (
        np.ones(shape=(4, 2), dtype=np.float32),
        1,
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 4: tile_size is 0
    (
        np.ones(shape=(4, 2), dtype=np.int32),
        0,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
    # test case 5: tile_size is negative
    (
        np.ones(shape=(4, 2), dtype=np.int32),
        -1,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
]

data_test_process_area_properties_exceptions = [
    # test case 1: coordinates has not 2 dimensions
    (
        'coordinates',
        np.ones(shape=(4, 2, 1), dtype=np.int32),
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has not 2 values in the second dimension
    (
        'coordinates',
        np.ones(shape=(4, 4), dtype=np.int32),
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates is not of data type int32
    (
        'coordinates',
        np.ones(shape=(4, 2), dtype=np.float32),
        re.escape('Invalid coordinates! coordinates must be an array of shape (n, 2) and data type int32.'),
    ),
    # test case 4: tile_size is 0
    (
        'tile_size',
        0,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
    # test case 5: tile_size is negative
    (
        'tile_size',
        -1,
        re.escape('Invalid tile size! tile_size must be positive.'),
    ),
]

data_test_process_area_area = [
    # test case 1: process area has no tiles
    (
        ProcessArea(tile_size=128),
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
