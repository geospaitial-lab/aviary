#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import copy
import re

import geopandas as gpd
from shapely.geometry import (
    MultiPolygon,
    Point,
    Polygon,
    box,
)

from aviary.core.bounding_box import BoundingBox
from tests.core.conftest import get_bounding_box

data_test_bounding_box_area = [
    # test case 1: bounding_box is in all quadrants
    (
        get_bounding_box(),
        65536,
    ),
    # test case 2: bounding_box is in the first quadrant
    (
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
        16384,
    ),
    # test case 3: bounding_box is in the second quadrant
    (
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
        16384,
    ),
    # test case 4: bounding_box is in the third quadrant
    (
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
        16384,
    ),
    # test case 5: bounding_box is in the fourth quadrant
    (
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
        16384,
    ),
]

data_test_bounding_box_buffer = [
    # test case 1: bounding_box is in all quadrants and buffer_size is 0
    (
        get_bounding_box(),
        0,
        get_bounding_box(),
    ),
    # test case 2: bounding_box is in all quadrants and buffer_size is positive
    (
        get_bounding_box(),
        32,
        BoundingBox(
            x_min=-160,
            y_min=-96,
            x_max=160,
            y_max=224,
        ),
     ),
    # test case 3: bounding_box is in all quadrants and buffer_size is negative
    (
        get_bounding_box(),
        -32,
        BoundingBox(
            x_min=-96,
            y_min=-32,
            x_max=96,
            y_max=160,
        ),
    ),
    # test case 4: bounding_box is in the first quadrant and buffer_size is 0
    (
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
        0,
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
    ),
    # test case 5: bounding_box is in the first quadrant and buffer_size is positive
    (
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
        32,
        BoundingBox(
            x_min=96,
            y_min=160,
            x_max=288,
            y_max=352,
        ),
    ),
    # test case 6: bounding_box is in the first quadrant and buffer_size is negative
    (
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
        -32,
        BoundingBox(
            x_min=160,
            y_min=224,
            x_max=224,
            y_max=288,
        ),
    ),
    # test case 7: bounding_box is in the second quadrant and buffer_size is 0
    (
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
        0,
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
    ),
    # test case 8: bounding_box is in the second quadrant and buffer_size is positive
    (
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
        32,
        BoundingBox(
            x_min=-288,
            y_min=160,
            x_max=-96,
            y_max=352,
        ),
    ),
    # test case 9: bounding_box is in the second quadrant and buffer_size is negative
    (
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
        -32,
        BoundingBox(
            x_min=-224,
            y_min=224,
            x_max=-160,
            y_max=288,
        ),
    ),
    # test case 10: bounding_box is in the third quadrant and buffer_size is 0
    (
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
        0,
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
    ),
    # test case 11: bounding_box is in the third quadrant and buffer_size is positive
    (
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
        32,
        BoundingBox(
            x_min=-288,
            y_min=-224,
            x_max=-96,
            y_max=-32,
        ),
    ),
    # test case 12: bounding_box is in the third quadrant and buffer_size is negative
    (
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
        -32,
        BoundingBox(
            x_min=-224,
            y_min=-160,
            x_max=-160,
            y_max=-96,
        ),
    ),
    # test case 13: bounding_box is in the fourth quadrant and buffer_size is 0
    (
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
        0,
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
    ),
    # test case 14: bounding_box is in the fourth quadrant and buffer_size is positive
    (
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
        32,
        BoundingBox(
            x_min=96,
            y_min=-224,
            x_max=288,
            y_max=-32,
        ),
    ),
    # test case 15: bounding_box is in the fourth quadrant and buffer_size is negative
    (
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
        -32,
        BoundingBox(
            x_min=160,
            y_min=-160,
            x_max=224,
            y_max=-96,
        ),
    ),
]

data_test_bounding_box_buffer_exceptions = [
    # test case 1: buffer_size is negative and abs(buffer_size) is equal to half the width and height
    # of the bounding box
    (
        -128,
        re.escape(
            'Invalid buffer_size! '
            'The absolute value of a negative buffer size must be less than half the width and height '
            'of the bounding box.',
        ),
    ),
    # test case 2: buffer_size is negative and abs(buffer_size) is greater than half the width and height
    # of the bounding box
    (
        -256,
        re.escape(
            'Invalid buffer_size! '
            'The absolute value of a negative buffer size must be less than half the width and height '
            'of the bounding box.',
        ),
    ),
]

data_test_bounding_box_buffer_inplace = copy.deepcopy(data_test_bounding_box_buffer)
data_test_bounding_box_buffer_inplace_return = copy.deepcopy(data_test_bounding_box_buffer)

data_test_bounding_box_eq = [
    # test case 1: other is equal
    (
        get_bounding_box(),
        True,
    ),
    # test case 2: x_min is not equal
    (
        BoundingBox(
            x_min=0,
            y_min=-64,
            x_max=128,
            y_max=192,
        ),
        False,
    ),
    # test case 3: y_min is not equal
    (
        BoundingBox(
            x_min=-128,
            y_min=0,
            x_max=128,
            y_max=192,
        ),
        False,
    ),
    # test case 4: x_max is not equal
    (
        BoundingBox(
            x_min=-128,
            y_min=-64,
            x_max=0,
            y_max=192,
        ),
        False,
    ),
    # test case 5: y_max is not equal
    (
        BoundingBox(
            x_min=-128,
            y_min=-64,
            x_max=128,
            y_max=0,
        ),
        False,
    ),
    # test case 6: other is not of type BoundingBox
    (
        'invalid',
        False,
    ),
]

data_test_bounding_box_from_gdf = [
    # test case 1: gdf contains a box
    (
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
        get_bounding_box(),
    ),
    # test case 2: gdf contains a box that needs to be rounded
    (
        gpd.GeoDataFrame(
            geometry=[box(-127.9, -63.9, 127.9, 191.9)],
        ),
        get_bounding_box(),
    ),
    # test case 3: gdf contains a box that needs to be rounded
    (
        gpd.GeoDataFrame(
            geometry=[box(-127.1, -63.1, 127.1, 191.1)],
        ),
        get_bounding_box(),
    ),
    # test case 4: gdf contains boxes
    (
        gpd.GeoDataFrame(
            geometry=[
                box(-128, -64, -96, -32),
                box(96, 160, 128, 192),
            ],
        ),
        get_bounding_box(),
    ),
    # test case 5: gdf contains a polygon
    (
        gpd.GeoDataFrame(
            geometry=[Polygon([[-128, 64], [0, -64], [128, 64], [0, 192]])],
        ),
        get_bounding_box(),
    ),
    # test case 6: gdf contains a multi polygon
    (
        gpd.GeoDataFrame(
            geometry=[
                MultiPolygon([
                    Polygon([[-128, -64], [-96, -64], [-96, -32], [-128, -32]]),
                    Polygon([[96, 160], [128, 160], [128, 192], [96, 192]]),
                ]),
            ],
        ),
        get_bounding_box(),
    ),
]

data_test_bounding_box_from_gdf_exceptions = [
    # test case 1: gdf contains no geometries
    (
        gpd.GeoDataFrame(),
        re.escape('Invalid gdf! The geodataframe must contain at least one geometry.'),
    ),
    # test case 2: gdf contains geometries other than polygons
    (
        gpd.GeoDataFrame(
            geometry=[Point(0, 0)],
        ),
        re.escape('Invalid gdf! The geodataframe must contain only polygons.'),
    ),
]

data_test_bounding_box_getitem = [
    (0, -128),
    (1, -64),
    (2, 128),
    (3, 192),
    (-1, 192),
    (-2, 128),
    (-3, -64),
    (-4, -128),
]

data_test_bounding_box_init_exceptions = [
    # test case 1: x_min is greater than x_max
    (
        192,
        -64,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 2: x_min is equal to x_max
    (
        128,
        -64,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 3: y_min is greater than y_max
    (
        -128,
        256,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 4: y_min is equal to y_max
    (
        -128,
        192,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 5: x_min is greater than x_max and y_min is greater than y_max
    (
        192,
        256,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 6: x_min is equal to x_max and y_min is equal to y_max
    (
        128,
        192,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 7: x_min is greater than x_max and y_min is equal to y_max
    (
        192,
        192,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
    # test case 8: x_min is equal to x_max and y_min is greater than y_max
    (
        128,
        256,
        128,
        192,
        re.escape('Invalid bounding_box! x_min must be less than x_max and y_min must be less than y_max.'),
    ),
]

data_test_bounding_box_snap = [
    # test case 1: bounding_box is in all quadrants and divisible by value
    (
        BoundingBox(
            x_min=-128,
            y_min=-128,
            x_max=128,
            y_max=128,
        ),
        128,
        BoundingBox(
            x_min=-128,
            y_min=-128,
            x_max=128,
            y_max=128,
        ),
    ),
    # test case 2: bounding_box is in all quadrants and not divisible by value
    (
        BoundingBox(
            x_min=-127,
            y_min=-127,
            x_max=127,
            y_max=127,
        ),
        128,
        BoundingBox(
            x_min=-128,
            y_min=-128,
            x_max=128,
            y_max=128,
        ),
    ),
    # test case 3: bounding_box is in all quadrants and not divisible by value
    (
        BoundingBox(
            x_min=-129,
            y_min=-129,
            x_max=129,
            y_max=129,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=-256,
            x_max=256,
            y_max=256,
        ),
    ),
    # test case 4: bounding_box is in all quadrants and not divisible by value
    (
        get_bounding_box(),
        128,
        BoundingBox(
            x_min=-128,
            y_min=-128,
            x_max=128,
            y_max=256,
        ),
    ),
    # test case 5: bounding_box is in the first quadrant and divisible by value
    (
        BoundingBox(
            x_min=128,
            y_min=128,
            x_max=256,
            y_max=256,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=128,
            x_max=256,
            y_max=256,
        ),
    ),
    # test case 6: bounding_box is in the first quadrant and not divisible by value
    (
        BoundingBox(
            x_min=129,
            y_min=129,
            x_max=255,
            y_max=255,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=128,
            x_max=256,
            y_max=256,
        ),
    ),
    # test case 7: bounding_box is in the first quadrant and not divisible by value
    (
        BoundingBox(
            x_min=127,
            y_min=127,
            x_max=257,
            y_max=257,
        ),
        128,
        BoundingBox(
            x_min=0,
            y_min=0,
            x_max=384,
            y_max=384,
        ),
    ),
    # test case 8: bounding_box is in the first quadrant and not divisible by value
    (
        BoundingBox(
            x_min=128,
            y_min=192,
            x_max=256,
            y_max=320,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=128,
            x_max=256,
            y_max=384,
        ),
    ),
    # test case 9: bounding_box is in the second quadrant and divisible by value
    (
        BoundingBox(
            x_min=-256,
            y_min=128,
            x_max=-128,
            y_max=256,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=128,
            x_max=-128,
            y_max=256,
        ),
    ),
    # test case 10: bounding_box is in the second quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-255,
            y_min=129,
            x_max=-129,
            y_max=255,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=128,
            x_max=-128,
            y_max=256,
        ),
    ),
    # test case 11: bounding_box is in the second quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-257,
            y_min=127,
            x_max=-127,
            y_max=257,
        ),
        128,
        BoundingBox(
            x_min=-384,
            y_min=0,
            x_max=0,
            y_max=384,
        ),
    ),
    # test case 12: bounding_box is in the second quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-256,
            y_min=192,
            x_max=-128,
            y_max=320,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=128,
            x_max=-128,
            y_max=384,
        ),
    ),
    # test case 13: bounding_box is in the third quadrant and divisible by value
    (
        BoundingBox(
            x_min=-256,
            y_min=-256,
            x_max=-128,
            y_max=-128,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=-256,
            x_max=-128,
            y_max=-128,
        ),
    ),
    # test case 14: bounding_box is in the third quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-255,
            y_min=-255,
            x_max=-129,
            y_max=-129,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=-256,
            x_max=-128,
            y_max=-128,
        ),
    ),
    # test case 15: bounding_box is in the third quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-257,
            y_min=-257,
            x_max=-127,
            y_max=-127,
        ),
        128,
        BoundingBox(
            x_min=-384,
            y_min=-384,
            x_max=0,
            y_max=0,
        ),
    ),
    # test case 16: bounding_box is in the third quadrant and not divisible by value
    (
        BoundingBox(
            x_min=-256,
            y_min=-192,
            x_max=-128,
            y_max=-64,
        ),
        128,
        BoundingBox(
            x_min=-256,
            y_min=-256,
            x_max=-128,
            y_max=0,
        ),
    ),
    # test case 17: bounding_box is in the fourth quadrant and divisible by value
    (
        BoundingBox(
            x_min=128,
            y_min=-256,
            x_max=256,
            y_max=-128,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=-256,
            x_max=256,
            y_max=-128,
        ),
    ),
    # test case 18: bounding_box is in the fourth quadrant and not divisible by value
    (
        BoundingBox(
            x_min=129,
            y_min=-255,
            x_max=255,
            y_max=-129,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=-256,
            x_max=256,
            y_max=-128,
        ),
    ),
    # test case 19: bounding_box is in the fourth quadrant and not divisible by value
    (
        BoundingBox(
            x_min=127,
            y_min=-257,
            x_max=257,
            y_max=-127,
        ),
        128,
        BoundingBox(
            x_min=0,
            y_min=-384,
            x_max=384,
            y_max=0,
        ),
    ),
    # test case 20: bounding_box is in the fourth quadrant and not divisible by value
    (
        BoundingBox(
            x_min=128,
            y_min=-192,
            x_max=256,
            y_max=-64,
        ),
        128,
        BoundingBox(
            x_min=128,
            y_min=-256,
            x_max=256,
            y_max=0,
        ),
    ),
]

data_test_bounding_box_snap_exceptions = [
    # test case 1: value is negative
    (
        -128,
        re.escape('Invalid value! The value must be positive.'),
    ),
    # test case 2: value is 0
    (
        0,
        re.escape('Invalid value! The value must be positive.'),
    ),
]

data_test_bounding_box_snap_inplace = copy.deepcopy(data_test_bounding_box_snap)
data_test_bounding_box_snap_inplace_return = copy.deepcopy(data_test_bounding_box_snap)

data_test_bounding_box_to_gdf = [
    # test case 1: EPSG code is None
    (
        None,
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
    ),
    # test case 2: EPSG code is not None
    (
        25832,
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
            crs='EPSG:25832',
        ),
    ),
]
