import copy
import re

import geopandas as gpd
import numpy as np
from shapely.geometry import box

from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName
from tests.core.conftest import (
    get_raster_channel,
    get_raster_channel_buffered_data_item,
    get_raster_channel_data,
    get_raster_channel_data_item,
    get_vector_channel,
    get_vector_channel_buffered_data_item,
    get_vector_channel_data,
    get_vector_channel_data_item,
    get_vector_channel_empty_data_item,
)

data_test_raster_channel_eq = [
    # test case 1: other is equal
    (
        get_raster_channel(),
        True,
    ),
    # test case 2: data is not equal
    (
        RasterChannel(
            data=[
                get_raster_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: data is not equal
    (
        RasterChannel(
            data=[
                get_raster_channel_buffered_data_item(),
                get_raster_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: data is not equal
    (
        RasterChannel(
            data=[
                get_raster_channel_buffered_data_item(),
                get_raster_channel_buffered_data_item(),
                get_raster_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 5: name is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.G,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 6: buffer_size is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=.125,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 7: time_step is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            time_step=0,
            copy=False,
        ),
        False,
    ),
    # test case 8: copy is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=True,
        ),
        True,
    ),
    # test case 9: other is not of type RasterChannel
    (
        'invalid',
        False,
    ),
]

data_test_raster_channel_init = [
    # test case 1: Default
    (
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 2: data is a single data item
    (
        get_raster_channel_data_item(),
        ChannelName.R,
        0.,
        None,
        False,
        [
            get_raster_channel_data_item(),
        ],
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 3: name is str, but can be parsed to ChannelName
    (
        get_raster_channel_data(),
        'r',
        0.,
        None,
        False,
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 4: name is str
    (
        get_raster_channel_data(),
        'custom',
        0.,
        None,
        False,
        get_raster_channel_data(),
        'custom',
        0.,
        None,
        False,
    ),
]

data_test_raster_channel_init_exceptions = [
    # test case 1: data contains no data items
    (
        [],
        0.,
        re.escape('Invalid data! The data must contain at least one data item.'),
    ),
    # test case 2: data contains data items that have one dimension
    (
        [
            np.ones(
                shape=(640, ),
                dtype=np.uint8,
            ),
            np.ones(
                shape=(640, ),
                dtype=np.uint8,
            ),
        ],
        0.,
        re.escape('Invalid data! The data item must be in shape (n, n).'),
    ),
    # test case 3: data contains data items that have three dimensions
    (
        [
            np.ones(
                shape=(640, 640, 1),
                dtype=np.uint8,
            ),
            np.ones(
                shape=(640, 640, 1),
                dtype=np.uint8,
            ),
        ],
        0.,
        re.escape('Invalid data! The data item must be in shape (n, n).'),
    ),
    # test case 4: data contains data items that are not square
    (
        [
            np.ones(
                shape=(640, 320),
                dtype=np.uint8,
            ),
            np.ones(
                shape=(640, 320),
                dtype=np.uint8,
            ),
        ],
        0.,
        re.escape('Invalid data! The data item must be in shape (n, n).'),
    ),
    # test case 5: data contains data items whose shapes are not equal
    (
        [
            get_raster_channel_data_item(),
            get_raster_channel_buffered_data_item(),
        ],
        0.,
        re.escape('Invalid data! The shapes of the data items must be equal.'),
    ),
    # test case 6: buffer_size is negative
    (
        [
            get_raster_channel_buffered_data_item(),
            get_raster_channel_buffered_data_item(),
        ],
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 7: buffer_size is .5
    (
        [
            get_raster_channel_buffered_data_item(),
            get_raster_channel_buffered_data_item(),
        ],
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 8: buffer_size is greater than .5
    (
        [
            get_raster_channel_buffered_data_item(),
            get_raster_channel_buffered_data_item(),
        ],
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 9: buffer_size results in a fractional number of pixels
    (
        [
            get_raster_channel_buffered_data_item(),
            get_raster_channel_buffered_data_item(),
        ],
        .2,
        re.escape(
            'Invalid buffer_size! '
            'The buffer size must must match the spatial extent of the data, '
            'resulting in a whole number of pixels.',
        ),
    ),
]

data_test_raster_channel_remove_buffer = [
    # test case 1: buffer_size is 0.
    (
        get_raster_channel(),
        get_raster_channel(),
    ),
    # test case 2: buffer_size is not 0.
    (
        RasterChannel(
            data=[
                get_raster_channel_buffered_data_item(),
                get_raster_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
]

data_test_raster_channel_remove_buffer_inplace = copy.deepcopy(data_test_raster_channel_remove_buffer)
data_test_raster_channel_remove_buffer_inplace_return = copy.deepcopy(data_test_raster_channel_remove_buffer)

data_test_vector_channel_eq = [
    # test case 1: other is equal
    (
        get_vector_channel(),
        True,
    ),
    # test case 2: data is not equal
    (
        VectorChannel(
            data=[
                get_vector_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: data is not equal
    (
        VectorChannel(
            data=[
                get_vector_channel_buffered_data_item(),
                get_vector_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: data is not equal
    (
        VectorChannel(
            data=[
                get_vector_channel_buffered_data_item(),
                get_vector_channel_buffered_data_item(),
                get_vector_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 5: name is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.G,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 6 buffer_size is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=.125,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 7: time_step is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            time_step=0,
            copy=False,
        ),
        False,
    ),
    # test case 8: copy is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=True,
        ),
        True,
    ),
    # test case 9: other is not of type VectorChannel
    (
        'invalid',
        False,
    ),
]

data_test_vector_channel_from_unscaled_data_exceptions = [
    # test case 1: data contains no data items
    (
        [],
        128,
        0,
        re.escape('Invalid data! The data must contain at least one data item.'),
    ),
    # test case 2: tile_size is negative
    (
        get_vector_channel_data(),
        -128,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 3: tile_size is 0
    (
        get_vector_channel_data(),
        0,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 4: buffer_size is negative
    (
        get_vector_channel_data(),
        128,
        -32,
        re.escape('Invalid buffer_size! The buffer size must be positive or zero.'),
    ),
]

data_test_vector_channel_init = [
    # test case 1: Default
    (
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 2: data is a single data item
    (
        get_vector_channel_data_item(),
        ChannelName.R,
        0.,
        None,
        False,
        [
            get_vector_channel_data_item(),
        ],
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 3: data contains data items that contain no geometries (needed for coverage)
    (
        [
            get_vector_channel_empty_data_item(),
            get_vector_channel_empty_data_item(),
        ],
        ChannelName.R,
        0.,
        None,
        False,
        [
            get_vector_channel_empty_data_item(),
            get_vector_channel_empty_data_item(),
        ],
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 4: name is str, but can be parsed to ChannelName
    (
        get_vector_channel_data(),
        'r',
        0.,
        None,
        False,
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 5: name is str
    (
        get_vector_channel_data(),
        'custom',
        0.,
        None,
        False,
        get_vector_channel_data(),
        'custom',
        0.,
        None,
        False,
    ),
]

data_test_vector_channel_init_exceptions = [
    # test case 1: data contains no data items
    (
        [],
        0.,
        re.escape('Invalid data! The data must contain at least one data item.'),
    ),
    # test case 2: data contains data items that have a coordinate reference system
    (
        [
            get_vector_channel_data_item().set_crs('EPSG:25832'),
            get_vector_channel_data_item().set_crs('EPSG:25832'),
        ],
        0.,
        re.escape('Invalid data! The data item must not have a coordinate reference system.'),
    ),
    # test case 3: data contains data items that are not scaled to the spatial extent [0, 1] in x and y direction
    (
        [
            gpd.GeoDataFrame(geometry=[box(-.1, -.1, 1.1, 1.1)]),
            gpd.GeoDataFrame(geometry=[box(-.1, -.1, 1.1, 1.1)]),
        ],
        0.,
        re.escape('Invalid data! The data item must be scaled to the spatial extent [0, 1] in x and y direction.'),
    ),
    # test case 4: buffer_size is negative
    (
        [
            get_vector_channel_buffered_data_item(),
            get_vector_channel_buffered_data_item(),
        ],
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 5: buffer_size is .5
    (
        [
            get_vector_channel_buffered_data_item(),
            get_vector_channel_buffered_data_item(),
        ],
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 6: buffer_size is greater than .5
    (
        [
            get_vector_channel_buffered_data_item(),
            get_vector_channel_buffered_data_item(),
        ],
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
]

data_test_vector_channel_remove_buffer = [
    # test case 1: buffer_size is 0.
    (
        get_vector_channel(),
        get_vector_channel(),
    ),
    # test case 2: buffer_size is not 0.
    (
        VectorChannel(
            data=[
                get_vector_channel_buffered_data_item(),
                get_vector_channel_buffered_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        get_vector_channel(),
    ),
    # test case 3: data contains no geometries
    (
        VectorChannel(
            data=[
                get_vector_channel_empty_data_item(),
                get_vector_channel_empty_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        VectorChannel(
            data=[
                get_vector_channel_empty_data_item(),
                get_vector_channel_empty_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
]

data_test_vector_channel_remove_buffer_inplace = copy.deepcopy(data_test_vector_channel_remove_buffer)
data_test_vector_channel_remove_buffer_inplace_return = copy.deepcopy(data_test_vector_channel_remove_buffer)
