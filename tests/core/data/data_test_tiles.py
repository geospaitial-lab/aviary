import re

import numpy as np

from aviary.core.enums import ChannelName
from aviary.core.tiles import Tiles
from tests.core.conftest import (
    get_metadata,
    get_tiles,
    get_tiles_channel_1,
    get_tiles_channel_2,
    get_tiles_channel_3,
    get_tiles_channel_4,
    get_tiles_channels,
    get_tiles_coordinates,
)

data_test_tiles_bool = [
    # test case 1: channels contains no channels
    (
        Tiles(
            channels=[],
            coordinates=get_tiles_coordinates(),
            tile_size=128,
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 2: channels contains channels
    (
        get_tiles(),
        True,
    ),
]

data_test_tiles_contains = [
    (ChannelName.R, True),
    ('r', True),
    ('custom', True),
    ('invalid', False),
]

data_test_tiles_eq = [
    # test case 1: other is equal
    (
        get_tiles(),
        True,
    ),
    # test case 2: channels is not equal
    (
        Tiles(
            channels=[
                get_tiles_channel_1(),
            ],
            coordinates=get_tiles_coordinates(),
            tile_size=128,
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: coordinates is not equal
    (
        Tiles(
            channels=get_tiles_channels(),
            coordinates=np.array(
                [[-128, 0], [0, 0]],
                dtype=np.int32,
            ),
            tile_size=128,
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: tile_size is not equal
    (
        Tiles(
            channels=get_tiles_channels(),
            coordinates=get_tiles_coordinates(),
            tile_size=64,
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 5: copy is not equal
    (
        Tiles(
            channels=get_tiles_channels(),
            coordinates=get_tiles_coordinates(),
            tile_size=128,
            metadata=None,
            copy=True,
        ),
        True,
    ),
    # test case 6: other is not of type Tiles
    (
        'invalid',
        False,
    ),
]

data_test_tiles_getattr = [
    ('r', get_tiles_channel_1()),
    ('g', get_tiles_channel_2()),
    ('b', get_tiles_channel_3()),
    ('custom', get_tiles_channel_4()),
]

data_test_tiles_getitem = [
    (ChannelName.R, get_tiles_channel_1()),
    ('r', get_tiles_channel_1()),
    (ChannelName.G, get_tiles_channel_2()),
    ('g', get_tiles_channel_2()),
    (ChannelName.B, get_tiles_channel_3()),
    ('b', get_tiles_channel_3()),
    ('custom', get_tiles_channel_4()),
]

data_test_tiles_init = [
    # test case 1: Default
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        128,
        None,
        False,
        get_tiles_channels(),
        get_tiles_coordinates(),
        128,
        {},
        False,
    ),
    # test case 2: channels contains no channels
    (
        [],
        get_tiles_coordinates(),
        128,
        None,
        False,
        [],
        get_tiles_coordinates(),
        128,
        {},
        False,
    ),
    # test case 3: batch_size is 1
    # test case 4: metadata is not None
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        128,
        get_metadata(),
        False,
        get_tiles_channels(),
        get_tiles_coordinates(),
        128,
        get_metadata(),
        False,
    ),
]

data_test_tiles_init_exceptions = [
    # test case 1: channels contains duplicate channel names
    (
        [
            *get_tiles_channels(),
            get_tiles_channel_1(),
        ],
        get_tiles_coordinates(),
        128,
        re.escape('Invalid channels! The channels must contain unique channel names.'),
    ),
    # test case 2: batch_size is not equal
    # test case 3: coordinates has one dimension
    (
        get_tiles_channels(),
        np.arange(
            8,
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 4: coordinates has three dimensions
    (
        get_tiles_channels(),
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 2, 2),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 5: coordinates has not two values in the second dimension
    (
        get_tiles_channels(),
        np.arange(
            8,
            dtype=np.int32,
        ).reshape(2, 4),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 6: coordinates is not of data type int32
    (
        get_tiles_channels(),
        np.arange(
            8,
            dtype=np.float32,
        ).reshape(4, 2),
        128,
        re.escape('Invalid coordinates! The coordinates must be in shape (n, 2) and data type int32.'),
    ),
    # test case 7: coordinates contains duplicate coordinates
    (
        get_tiles_channels(),
        np.array(
            [[128, -128], [128, -128]],
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The coordinates must contain unique coordinates.'),
    ),
    # test case 8: len(coordinates) is not equal to batch_size
    (
        get_tiles_channels(),
        np.array(
            [[128, -128]],
            dtype=np.int32,
        ),
        128,
        re.escape('Invalid coordinates! The number of coordinates must be equal to the batch size of the channels.'),
    ),
    # test case 9: tile_size is negative
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 10: tile_size is 0
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]
