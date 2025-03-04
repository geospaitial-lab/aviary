import re

import numpy as np

from aviary.core.enums import ChannelName
from aviary.core.tiles import Tiles
from tests.core.conftest import (
    get_tiles,
    get_tiles_channel_1,
    get_tiles_channel_2,
    get_tiles_channel_3,
    get_tiles_channel_4,
    get_tiles_channels,
    get_tiles_coordinates,
)

data_test_tiles_contains = [
    (ChannelName.R, True),
    ('r', True),
    ('custom', True),
    ((ChannelName.R, None), True),
    (('r', None), True),
    (('custom', None), True),
    ('invalid', False),
    (('invalid', None), False),
    ((ChannelName.R, 0), False),
    (('r', 0), False),
    (('custom', 0), False),
    (('invalid', 0), False),
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
    ((ChannelName.R, None), get_tiles_channel_1()),
    (('r', None), get_tiles_channel_1()),
    ((ChannelName.G, None), get_tiles_channel_2()),
    (('g', None), get_tiles_channel_2()),
    ((ChannelName.B, None), get_tiles_channel_3()),
    (('b', None), get_tiles_channel_3()),
    (('custom', None), get_tiles_channel_4()),
]

data_test_tiles_init = [

]

data_test_tiles_init_exceptions = [
    # test case 1: channels contains no channel
    (
        [],
        get_tiles_coordinates(),
        128,
        re.escape('Invalid channels! The channels must contain at least one channel.'),
    ),
    # test case 2: channels contains duplicate channel name and time step combinations
    (
        [*get_tiles_channels(), get_tiles_channel_1()],
        get_tiles_coordinates(),
        128,
        re.escape(
            'Invalid channels! '
            'The channels must contain unique channel name and time step combinations.',
        ),
    ),
    # test case 3: batch_size is not equal
    # test case 4: tile_size is negative
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        -128,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
    # test case 5: tile_size is 0
    (
        get_tiles_channels(),
        get_tiles_coordinates(),
        0,
        re.escape('Invalid tile_size! The tile size must be positive.'),
    ),
]
