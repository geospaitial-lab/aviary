import copy
import re

import geopandas as gpd
import numpy as np
from shapely.geometry import (
    MultiPolygon,
    Point,
    Polygon,
    box,
)

from aviary.core.grid import Grid
from tests.core.conftest import (
    get_bounding_box,
    get_grid,
    get_grid_coordinates,
)

data_test_grid_add = [
    # test case 1: other contains no coordinates
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        get_grid(),
    ),
    # test case 2: other contains coordinates
    (
        Grid(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_add_exceptions = [
    # test case 1: tile_size is not equal
    (
        Grid(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the grids must be equal.'),
    ),
]

data_test_grid_and = [
    # test case 1: other contains no coordinates
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        Grid(
            coordinates=None,
            tile_size=128,
        ),
    ),
    # test case 2: other contains coordinates
    (
        Grid(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        Grid(
            coordinates=np.array(
                [[-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_and_exceptions = [
    # test case 1: tile_size is not equal
    (
        Grid(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the grids must be equal.'),
    ),
]

data_test_grid_append = [
    # test case 1: Default
    (
        get_grid(),
        (128, -128),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 2: coordinates contains no coordinates
    (
        get_grid(),
        np.empty(
            shape=(0, 2),
            dtype=np.int32,
        ),
        get_grid(),
    ),
    # test case 3: coordinates contains coordinates
    (
        get_grid(),
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_append_exceptions = [
    # test case 1: coordinates has one dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has three dimensions
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 2, 2),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates has not two values in the second dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 4),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 4: coordinates is not of data type int32
    (
        np.arange(
            8,
            dtype=np.float32,
        ).reshape(4, 2),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
]

data_test_grid_append_inplace = copy.deepcopy(data_test_grid_append)
data_test_grid_append_inplace_return = copy.deepcopy(data_test_grid_append)

data_test_grid_area = [
    # test case 1: coordinates contains no coordinates
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        0,
    ),
    # test case 2: coordinates contains one coordinates
    (
        Grid(
            coordinates=np.array(
                [[-128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        16384,
    ),
    # test case 3: coordinates contains four coordinates
    (
        get_grid(),
        65536,
    ),
]

data_test_grid_bool = [
    # test case 1: coordinates contains no coordinates
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        False,
    ),
    # test case 2: coordinates contains coordinates
    (
        get_grid(),
        True,
    ),
]

data_test_grid_chunk = [
    # test case 1: len(coordinates) is divisible by num_chunks
    (
        get_grid(),
        2,
        [
            Grid(
                coordinates=np.array(
                    [[-128, -128], [0, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            Grid(
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
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        2,
        [
            Grid(
                coordinates=np.array(
                    [[-128, -128], [0, -128], [128, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            Grid(
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
        get_grid(),
        4,
        [
            Grid(
                coordinates=np.array(
                    [[-128, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            Grid(
                coordinates=np.array(
                    [[0, -128]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            Grid(
                coordinates=np.array(
                    [[-128, 0]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
            Grid(
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
        get_grid(),
        1,
        [
            get_grid(),
        ],
    ),
]

data_test_grid_chunk_exceptions = [
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

data_test_grid_contains = [
    ((-128, -128), True),
    ((0, -128), True),
    ((-128, 0), True),
    ((0, 0), True),
    ((128, -128), False),
    ((128, 0), False),
    (
        np.array(
            [[-128, -128], [0, -128]],
            dtype=np.int32,
        ),
        True,
    ),
    (
        get_grid_coordinates(),
        True,
    ),
    (
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        False,
    ),
    (
        np.array(
            [[-128, -128], [0, -128], [128, -128], [128, 0]],
            dtype=np.int32,
        ),
        False,
    ),
]

data_test_grid_eq = [
    # test case 1: other is equal
    (
        get_grid(),
        True,
    ),
    # test case 2: coordinates is not equal
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        False,
    ),
    # test case 3: tile_size is not equal
    (
        Grid(
            coordinates=get_grid_coordinates(),
            tile_size=64,
        ),
        False,
    ),
    # test case 4: other is not of type Grid
    (
        'invalid',
        False,
    ),
]

data_test_grid_from_bounding_box = [
    # test case 1: quantize is False
    (
        get_bounding_box(),
        128,
        False,
        Grid(
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
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_from_bounding_box_exceptions = [
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

data_test_grid_from_gdf = [
    # test case 1: gdf contains a box and quantize is False
    (
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
        128,
        False,
        Grid(
            coordinates=np.array(
                [[-128, -64], [0, -64], [-128, 64], [0, 64]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 2: gdf contains a box and quantize is True
    (
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
        128,
        True,
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 3: gdf contains boxes and quantize is False
    (
        gpd.GeoDataFrame(
            geometry=[
                box(-128, -64, -96, -32),
                box(96, 160, 128, 192),
            ],
        ),
        128,
        False,
        Grid(
            coordinates=np.array(
                [[-128, -64], [0, 64]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 4: gdf contains boxes and quantize is True
    (
        gpd.GeoDataFrame(
            geometry=[
                box(-128, -64, -96, -32),
                box(96, 160, 128, 192),
            ],
        ),
        128,
        True,
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 5: gdf contains a polygon and quantize is False
    (
        gpd.GeoDataFrame(
            geometry=[Polygon([[-128, 64], [0, -64], [128, 64], [0, 192]])],
        ),
        128,
        False,
        Grid(
            coordinates=np.array(
                [[-128, -64], [0, -64], [-128, 64], [0, 64]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 6: gdf contains a polygon and quantize is True
    (
        gpd.GeoDataFrame(
            geometry=[Polygon([[-128, 64], [0, -64], [128, 64], [0, 192]])],
        ),
        128,
        True,
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 7: gdf contains a multi polygon and quantize is False
    (
        gpd.GeoDataFrame(
            geometry=[
                MultiPolygon([
                    Polygon([[-128, -64], [-96, -64], [-96, -32], [-128, -32]]),
                    Polygon([[96, 160], [128, 160], [128, 192], [96, 192]]),
                ]),
            ],
        ),
        128,
        False,
        Grid(
            coordinates=np.array(
                [[-128, -64], [0, 64]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 8: gdf contains a multi polygon and quantize is True
    (
        gpd.GeoDataFrame(
            geometry=[
                MultiPolygon([
                    Polygon([[-128, -64], [-96, -64], [-96, -32], [-128, -32]]),
                    Polygon([[96, 160], [128, 160], [128, 192], [96, 192]]),
                ]),
            ],
        ),
        128,
        True,
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, 128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_from_gdf_exceptions = [
    # test case 1: gdf contains no geometries
    (
        gpd.GeoDataFrame(),
        128,
        re.escape('Invalid gdf! The geodataframe must contain at least one geometry.'),
    ),
    # test case 2: gdf contains geometries other than polygons
    (
        gpd.GeoDataFrame(
            geometry=[Point(0, 0)],
        ),
        128,
        re.escape('Invalid gdf! The geodataframe must contain only polygons.'),
    ),
    # test case 3: tile_size is negative
    (
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 4: tile_size is 0
    (
        gpd.GeoDataFrame(
            geometry=[box(-128, -64, 128, 192)],
        ),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]

data_test_grid_from_json = [
    # test case 1: coordinates contains no coordinates
    (
        '{"coordinates": [], "tile_size": 128}',
        Grid(
            coordinates=None,
            tile_size=128,
        ),
    ),
    # test case 2: coordinates contains coordinates
    (
        '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]], "tile_size": 128}',
        get_grid(),
    ),
]

data_test_grid_from_json_exceptions = [
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

data_test_grid_from_grids = [
    # test case 1: Default
    (
        [
            get_grid(),
            Grid(
                coordinates=np.array(
                    [[128, -128], [128, 0]],
                    dtype=np.int32,
                ),
                tile_size=128,
            ),
        ],
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_from_grids_exceptions = [
    # test case 1: grids contains no grid
    (
        [],
        re.escape('Invalid grids! The grids must contain at least one grid.'),
    ),
    # test case 2: tile_size is not equal
    (
        [
            get_grid(),
            Grid(
                coordinates=np.array(
                    [[128, -128], [128, 0]],
                    dtype=np.int32,
                ),
                tile_size=64,
            ),
        ],
        re.escape('Invalid grids! The tile sizes of the grids must be equal.'),
    ),
]

data_test_grid_getitem = [
    (0, (-128, -128)),
    (1, (0, -128)),
    (2, (-128, 0)),
    (3, (0, 0)),
    (-1, (0, 0)),
    (-2, (-128, 0)),
    (-3, (0, -128)),
    (-4, (-128, -128)),
]

data_test_grid_getitem_slice = [
    (
        slice(None, 2),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(2, None),
        Grid(
            coordinates=np.array(
                [[-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(1, -1),
        Grid(
            coordinates=np.array(
                [[0, -128], [-128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None),
        get_grid(),
    ),
    (
        slice(None, None, 2),
        Grid(
            coordinates=np.array(
                [[-128, -128], [-128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None, -2),
        Grid(
            coordinates=np.array(
                [[0, 0], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    (
        slice(None, None, -1),
        Grid(
            coordinates=np.array(
                [[0, 0], [-128, 0], [0, -128], [-128, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_init = [
    # test case 1: coordinates contains no coordinates
    (
        None,
        128,
        np.empty(
            shape=(0, 2),
            dtype=np.int32,
        ),
        128,
    ),
    # test case 2: coordinates contains coordinates
    (
        get_grid_coordinates(),
        128,
        get_grid_coordinates(),
        128,
    ),
    # test case 3: coordinates contains duplicate coordinates
    (
        np.array(
            [[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 0], [0, 0]],
            dtype=np.int32,
        ),
        128,
        get_grid_coordinates(),
        128,
    ),
    # test case 4: coordinates is not sorted
    (
        np.array(
            [[0, 0], [-128, 0], [0, -128], [-128, -128]],
            dtype=np.int32,
        ),
        128,
        get_grid_coordinates(),
        128,
    ),
]

data_test_grid_init_exceptions = [
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
    # test case 5: coordinates is not quantized regularly
    (
        np.array(
            [[-128, -128], [0, -128], [-128, 0], [0, 0], [64, -128]],
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must be quantized regularly.'),
    ),
    # test case 6: coordinates is not quantized regularly
    (
        np.array(
            [[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -64]],
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must be quantized regularly.'),
    ),
    # test case 7: coordinates is not quantized regularly
    (
        np.array(
            [[-128, -128], [0, -128], [-128, 0], [0, 0], [64, -64]],
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must be quantized regularly.'),
    ),
    # test case 8: tile_size is negative
    (
        get_grid_coordinates(),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 9: tile_size is 0
    (
        get_grid_coordinates(),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]

data_test_grid_remove = [
    # test case 1: Default
    (
        get_grid(),
        (-128, -128),
        Grid(
            coordinates=np.array(
                [[0, -128], [-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
    # test case 2: coordinates contains no coordinates
    (
        get_grid(),
        np.empty(
            shape=(0, 2),
            dtype=np.int32,
        ),
        get_grid(),
    ),
    # test case 3: coordinates contains coordinates
    (
        get_grid(),
        np.array(
            [[-128, 0], [0, 0]],
            dtype=np.int32,
        ),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_remove_exceptions = [
    # test case 1: coordinates has one dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 2: coordinates has three dimensions
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 2, 2),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates has not two values in the second dimension
    (
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 4),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 4: coordinates is not of data type int32
    (
        np.arange(
            8,
            dtype=np.float32,
        ).reshape(4, 2),
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
]

data_test_grid_remove_inplace = copy.deepcopy(data_test_grid_remove)
data_test_grid_remove_inplace_return = copy.deepcopy(data_test_grid_remove)

data_test_grid_sub = [
    # test case 1: other contains no coordinates
    (
        Grid(
            coordinates=None,
            tile_size=128,
        ),
        get_grid(),
    ),
    # test case 2: other contains coordinates
    (
        Grid(
            coordinates=np.array(
                [[-128, 0], [0, 0], [128, -128], [128, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
        Grid(
            coordinates=np.array(
                [[-128, -128], [0, -128]],
                dtype=np.int32,
            ),
            tile_size=128,
        ),
    ),
]

data_test_grid_sub_exceptions = [
    # test case 1: tile_size is not equal
    (
        Grid(
            coordinates=None,
            tile_size=64,
        ),
        re.escape('Invalid other! The tile sizes of the grids must be equal.'),
    ),
]
