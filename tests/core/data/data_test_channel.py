import re

import geopandas as gpd
import numpy as np
from shapely.geometry import box

from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName

_raster_channel_data = np.ones(shape=(640, 640), dtype=np.uint8)
_raster_channel_buffered_data = np.zeros(shape=(960, 960), dtype=np.uint8)
_raster_channel_buffered_data[160:800, 160:800] = 1

_vector_channel_data_geometries = [
    box(0., 0., .1, .1),
    box(.9, 0., 1., .1),
    box(.9, .9, 1., 1.),
    box(0., .9, .1, 1.),
    box(.45, .45, .55, .55),
]
_vector_channel_data = gpd.GeoDataFrame(geometry=_vector_channel_data_geometries)
_vector_channel_unbuffered_data_geometries = [
    box(.425, .425, .575, .575),
]
_vector_channel_unbuffered_data = gpd.GeoDataFrame(geometry=_vector_channel_unbuffered_data_geometries)
_vector_channel_empty_data = gpd.GeoDataFrame(geometry=[])

data_test_raster_channel_eq = [
    # test case 1: other is equal
    (
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        True,
    ),
    # test case 2: data is not equal
    (
        RasterChannel(
            data=_raster_channel_buffered_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: name is not equal
    (
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.G,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: buffer_size is not equal
    (
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=.125,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 5: time_step is not equal
    (
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=0,
            copy=False,
        ),
        False,
    ),
    # test case 6: copy is not equal
    (
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=True,
        ),
        True,
    ),
    # test case 7: other is not of type RasterChannel
    (
        'invalid',
        False,
    ),
]

data_test_raster_channel_init = [
    # test case 1: default
    (
        _raster_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
        _raster_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 2: name is str, but can be parsed to ChannelName
    (
        _raster_channel_data,
        'r',
        0.,
        None,
        False,
        _raster_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 3: name is str
    (
        _raster_channel_data,
        'custom',
        0.,
        None,
        False,
        _raster_channel_data,
        'custom',
        0.,
        None,
        False,
    ),
]

data_test_raster_channel_init_exceptions = [
    # test case 1: data has not two dimensions
    (
        np.ones(shape=(640, 640, 3), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 2: data is not square
    (
        np.ones(shape=(640, 320), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 3: buffer_size is negative
    (
        _raster_channel_buffered_data,
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 4: buffer_size is .5
    (
        _raster_channel_buffered_data,
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 5: buffer_size is greater than .5
    (
        _raster_channel_buffered_data,
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 6: buffer_size results in a fractional number of pixels
    (
        _raster_channel_buffered_data,
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
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
    # test case 2: buffer_size is not 0.
    (
        RasterChannel(
            data=_raster_channel_buffered_data,
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        RasterChannel(
            data=_raster_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
]

data_test_vector_channel_eq = [
    # test case 1: other is equal
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        True,
    ),
    # test case 2: data is not equal
    (
        VectorChannel(
            data=_vector_channel_empty_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: name is not equal
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.G,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: buffer_size is not equal
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=.125,
            time_step=None,
            copy=False,
        ),
        False,
    ),
    # test case 5: time_step is not equal
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=0,
            copy=False,
        ),
        False,
    ),
    # test case 6: copy is not equal
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=True,
        ),
        True,
    ),
    # test case 7: other is not of type VectorChannel
    (
        'invalid',
        False,
    ),
]

data_test_vector_channel_from_unscaled_data_exceptions = [
    # test case 1: tile_size is negative
    (
        -1,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 2: tile_size is 0
    (
        0,
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 3: buffer_size is negative
    (
        128,
        -1,
        re.escape('Invalid buffer_size! The buffer size must be positive or zero.'),
    ),
]

data_test_vector_channel_init = [
    # test case 1: default
    (
        _vector_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
        _vector_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 2: data is empty (needed for coverage)
    (
        _vector_channel_empty_data,
        ChannelName.R,
        0.,
        None,
        False,
        _vector_channel_empty_data,
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 3: name is str, but can be parsed to ChannelName
    (
        _vector_channel_data,
        'r',
        0.,
        None,
        False,
        _vector_channel_data,
        ChannelName.R,
        0.,
        None,
        False,
    ),
    # test case 4: name is str
    (
        _vector_channel_data,
        'custom',
        0.,
        None,
        False,
        _vector_channel_data,
        'custom',
        0.,
        None,
        False,
    ),
]

data_test_vector_channel_init_exceptions = [
    # test case 1: data has a coordinate reference system
    (
        gpd.GeoDataFrame(geometry=_vector_channel_data_geometries, crs='EPSG:25832'),
        0.,
        re.escape('Invalid data! The data must not have a coordinate reference system.'),
    ),
    # test case 2: data is not scaled to the spatial extent [0, 1] in x and y direction
    (
        gpd.GeoDataFrame(geometry=[box(-.1, -.1, 1.1, 1.1)]),
        0.,
        re.escape('Invalid data! The data must be scaled to the spatial extent [0, 1] in x and y direction.'),
    ),
    # test case 3: buffer_size is negative
    (
        _vector_channel_data,
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 4: buffer_size is .5
    (
        _vector_channel_data,
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 5: buffer_size is greater than .5
    (
        _vector_channel_data,
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
]

data_test_vector_channel_remove_buffer = [
    # test case 1: buffer_size is 0.
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
    # test case 2: buffer_size is not 0.
    (
        VectorChannel(
            data=_vector_channel_data,
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        VectorChannel(
            data=_vector_channel_unbuffered_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
    # test case 3: data is empty
    (
        VectorChannel(
            data=_vector_channel_empty_data,
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        VectorChannel(
            data=_vector_channel_empty_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
]
