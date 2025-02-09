import re

import numpy as np

from aviary.core.channel import RasterChannel
from aviary.core.enums import ChannelName

_data = np.ones(shape=(640, 640), dtype=np.uint8)
_buffered_data = np.zeros(shape=(960, 960), dtype=np.uint8)
_buffered_data[160:800, 160:800] = 1

data_test_raster_channel_init_exceptions = [
    # test case 1: data has not two dimensions
    (
        np.ones(shape=(640, 640, 3), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 2: data is not a square
    (
        np.ones(shape=(640, 320), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 3: buffer_size is negative
    (
        _buffered_data,
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 4: buffer_size is .5
    (
        _buffered_data,
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 5: buffer_size is greater than .5
    (
        _buffered_data,
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 6: buffer_size results in a fractional number of pixels
    (
        _buffered_data,
        .16,
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
            data=_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
        RasterChannel(
            data=_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
    # test case 2: buffer_size is not 0.
    (
        RasterChannel(
            data=_buffered_data,
            name=ChannelName.R,
            buffer_size=.25,
            time_step=None,
            copy=False,
        ),
        RasterChannel(
            data=_data,
            name=ChannelName.R,
            buffer_size=0.,
            time_step=None,
            copy=False,
        ),
    ),
]
