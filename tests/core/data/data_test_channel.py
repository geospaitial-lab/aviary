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
import numpy as np
from shapely.geometry import box

from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName
from tests.core.conftest import (
    get_metadata,
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

data_test_raster_channel_add = [
    # test case 1: Default
    (
        get_raster_channel(),
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                *get_raster_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=True,
        ),
    ),
    # test case 2: metadata is not None
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=True,
        ),
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                *get_raster_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=True,
        ),
    ),
]

data_test_raster_channel_add_exceptions = [
    # test case 1: name is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.B,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
        re.escape('Invalid other! The names of the channels must be equal.'),
    ),
    # test case 2: buffer_size is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=.125,
            metadata=None,
            copy=False,
        ),
        re.escape('Invalid other! The buffer sizes of the channels must be equal.'),
    ),
]

data_test_raster_channel_append = [
    # test case 1: Default
    (
        get_raster_channel_data(),
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                *get_raster_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 2: data is a single data item
    (
        get_raster_channel_data_item(),
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                get_raster_channel_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 3: data contains no data items
    (
        [],
        get_raster_channel(),
    ),
]

data_test_raster_channel_append_inplace = copy.deepcopy(data_test_raster_channel_append)
data_test_raster_channel_append_inplace_return = copy.deepcopy(data_test_raster_channel_append)

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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 7: metadata is not equal
    (
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
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
            metadata=None,
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

data_test_raster_channel_from_channels = [
    # test case 1: Default
    (
        [
            get_raster_channel(),
            get_raster_channel(),
        ],
        False,
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                *get_raster_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 2: metadata is not None
    (
        [
            get_raster_channel(),
            RasterChannel(
                data=get_raster_channel_data(),
                name=ChannelName.R,
                buffer_size=0.,
                metadata=get_metadata(),
                copy=False,
            ),
        ],
        False,
        RasterChannel(
            data=[
                *get_raster_channel_data(),
                *get_raster_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=False,
        ),
    ),
]

data_test_raster_channel_from_channels_exceptions = [
    # test case 1: channels contains no channels
    (
        [],
        re.escape('Invalid channels! The channels must contain at least one channel.'),
    ),
    # test case 2: name is not equal
    (
        [
            get_raster_channel(),
            RasterChannel(
                data=get_raster_channel_data(),
                name=ChannelName.B,
                buffer_size=0.,
                metadata=None,
                copy=False,
            ),
        ],
        re.escape('Invalid channels! The names of the channels must be equal.'),
    ),
    # test case 3: buffer_size is not equal
    (
        [
            get_raster_channel(),
            RasterChannel(
                data=get_raster_channel_data(),
                name=ChannelName.R,
                buffer_size=.125,
                metadata=None,
                copy=False,
            ),
        ],
        re.escape('Invalid channels! The buffer sizes of the channels must be equal.'),
    ),
]

data_test_raster_channel_getitem = [
    (0, get_raster_channel_data_item()),
    (1, get_raster_channel_data_item()),
    (-1, get_raster_channel_data_item()),
    (-2, get_raster_channel_data_item()),
]

data_test_raster_channel_getitem_slice = [
    (
        slice(None, 1),
        [
            get_raster_channel_data_item(),
        ],
    ),
    (
        slice(1, None),
        [
            get_raster_channel_data_item(),
        ],
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
        {},
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
        {},
        False,
    ),
    # test case 3: name is str, but can be coerced to ChannelName
    (
        get_raster_channel_data(),
        'r',
        0.,
        None,
        False,
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        {},
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
        {},
        False,
    ),
    # test case 5: metadata is not None
    (
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        get_metadata(),
        False,
        get_raster_channel_data(),
        ChannelName.R,
        0.,
        get_metadata(),
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
            metadata=None,
            copy=False,
        ),
        RasterChannel(
            data=get_raster_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
]

data_test_raster_channel_remove_buffer_inplace = copy.deepcopy(data_test_raster_channel_remove_buffer)
data_test_raster_channel_remove_buffer_inplace_return = copy.deepcopy(data_test_raster_channel_remove_buffer)

data_test_vector_channel_add = [
    # test case 1: Default
    (
        get_vector_channel(),
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                *get_vector_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=True,
        ),
    ),
    # test case 2: metadata is not None
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=True,
        ),
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                *get_vector_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=True,
        ),
    ),
]

data_test_vector_channel_add_exceptions = [
    # test case 1: name is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.B,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
        re.escape('Invalid other! The names of the channels must be equal.'),
    ),
    # test case 2: buffer_size is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=.125,
            metadata=None,
            copy=False,
        ),
        re.escape('Invalid other! The buffer sizes of the channels must be equal.'),
    ),
]

data_test_vector_channel_append = [
    # test case 1: Default
    (
        get_vector_channel_data(),
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                *get_vector_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 2: data is a single data item
    (
        get_vector_channel_data_item(),
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                get_vector_channel_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 3: data contains no data items
    (
        [],
        get_vector_channel(),
    ),
]

data_test_vector_channel_append_inplace = copy.deepcopy(data_test_vector_channel_append)
data_test_vector_channel_append_inplace_return = copy.deepcopy(data_test_vector_channel_append)

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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
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
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 7: metadata is not equal
    (
        VectorChannel(
            data=get_vector_channel_data(),
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
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
            metadata=None,
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

data_test_vector_channel_from_channels = [
    # test case 1: Default
    (
        [
            get_vector_channel(),
            get_vector_channel(),
        ],
        False,
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                *get_vector_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
    # test case 2: metadata is not None
    (
        [
            get_vector_channel(),
            VectorChannel(
                data=get_vector_channel_data(),
                name=ChannelName.R,
                buffer_size=0.,
                metadata=get_metadata(),
                copy=False,
            ),
        ],
        False,
        VectorChannel(
            data=[
                *get_vector_channel_data(),
                *get_vector_channel_data(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=get_metadata(),
            copy=False,
        ),
    ),
]

data_test_vector_channel_from_channels_exceptions = [
    # test case 1: channels contains no channels
    (
        [],
        re.escape('Invalid channels! The channels must contain at least one channel.'),
    ),
    # test case 2: name is not equal
    (
        [
            get_vector_channel(),
            VectorChannel(
                data=get_vector_channel_data(),
                name=ChannelName.B,
                buffer_size=0.,
                metadata=None,
                copy=False,
            ),
        ],
        re.escape('Invalid channels! The names of the channels must be equal.'),
    ),
    # test case 3: buffer_size is not equal
    (
        [
            get_vector_channel(),
            VectorChannel(
                data=get_vector_channel_data(),
                name=ChannelName.R,
                buffer_size=.125,
                metadata=None,
                copy=False,
            ),
        ],
        re.escape('Invalid channels! The buffer sizes of the channels must be equal.'),
    ),
]

data_test_vector_channel_from_unnormalized_data_exceptions = [
    # test case 1: data contains no data items
    (
        [],
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        128,
        0,
        re.escape('Invalid data! The data must contain at least one data item.'),
    ),
    # test case 2: coordinates has one dimension
    (
        get_vector_channel_data(),
        np.arange(
            8,
            dtype=np.int32,
        ),
        128,
        0,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 3: coordinates has three dimensions
    (
        get_vector_channel_data(),
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 2, 2),
        128,
        0,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 4: coordinates has not two values in the second dimension
    (
        get_vector_channel_data(),
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 4),
        128,
        0,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 5: coordinates is not of data type int32
    (
        get_vector_channel_data(),
        np.arange(
            8,
            dtype=np.float32,
        ).reshape(4, 2),
        128,
        0,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 6: coordinates contains duplicate coordinates
    (
        get_vector_channel_data(),
        np.array(
            [[128, -128], [128, -128]],
            dtype=np.int32,
        ),
        128,
        0,
        re.escape('Invalid coordinates! The coordinates must contain unique coordinates.'),
    ),
    # test case 7: len(coordinates) is not equal to len(data)
    (
        get_vector_channel_data(),
        np.array(
            [[128, -128]],
            dtype=np.int32,
        ),
        128,
        0,
        re.escape('Invalid coordinates! The number of coordinates must be equal to the number of data items.'),
    ),
    # test case 8: tile_size is negative
    (
        get_vector_channel_data(),
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        -128,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 9: tile_size is 0
    (
        get_vector_channel_data(),
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        0,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 10: buffer_size is negative
    (
        get_vector_channel_data(),
        np.array(
            [[128, -128], [128, 0]],
            dtype=np.int32,
        ),
        128,
        -32,
        re.escape('Invalid buffer_size! The buffer size must be positive or zero.'),
    ),
]

data_test_vector_channel_getitem = [
    (0, get_vector_channel_data_item()),
    (1, get_vector_channel_data_item()),
    (-1, get_vector_channel_data_item()),
    (-2, get_vector_channel_data_item()),
]

data_test_vector_channel_getitem_slice = [
    (
        slice(None, 1),
        [
            get_vector_channel_data_item(),
        ],
    ),
    (
        slice(1, None),
        [
            get_vector_channel_data_item(),
        ],
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
        {},
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
        {},
        False,
    ),
    # test case 3: data contains data items that contain no geometries (necessary for coverage)
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
        {},
        False,
    ),
    # test case 4: name is str, but can be coerced to ChannelName
    (
        get_vector_channel_data(),
        'r',
        0.,
        None,
        False,
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        {},
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
        {},
        False,
    ),
    # test case 6: metadata is not None
    (
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        get_metadata(),
        False,
        get_vector_channel_data(),
        ChannelName.R,
        0.,
        get_metadata(),
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
            get_vector_channel_data_item().set_crs(crs='EPSG:25832'),
            get_vector_channel_data_item().set_crs(crs='EPSG:25832'),
        ],
        0.,
        re.escape('Invalid data! The data item must not have a coordinate reference system.'),
    ),
    # test case 3: data contains data items that are not normalized to the spatial extent [0, 1] in x and y direction
    (
        [
            gpd.GeoDataFrame(geometry=[box(-.1, -.1, 1.1, 1.1)]),
            gpd.GeoDataFrame(geometry=[box(-.1, -.1, 1.1, 1.1)]),
        ],
        0.,
        re.escape('Invalid data! The data item must be normalized to the spatial extent [0, 1] in x and y direction.'),
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
            metadata=None,
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
            metadata=None,
            copy=False,
        ),
        VectorChannel(
            data=[
                get_vector_channel_empty_data_item(),
                get_vector_channel_empty_data_item(),
            ],
            name=ChannelName.R,
            buffer_size=0.,
            metadata=None,
            copy=False,
        ),
    ),
]

data_test_vector_channel_remove_buffer_inplace = copy.deepcopy(data_test_vector_channel_remove_buffer)
data_test_vector_channel_remove_buffer_inplace_return = copy.deepcopy(data_test_vector_channel_remove_buffer)
